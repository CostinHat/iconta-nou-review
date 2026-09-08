# -*- coding: utf-8 -*-
"""GARD P2 — infrastructura nu poate eșua tăcut, iar blocajul lucrătorului e al unei SESIUNI.

Cele două clase păzite aici au aceeași formă: **un mecanism de corectitudine care, dacă lipsește,
nu produce nicio eroare** — produce o valoare veche arătată drept curentă.

  STARTUP FAIL-CLOSED   dacă DDL-ul, migrarea triggerelor sau verificarea de după ele eșuează,
      aplicația NU intră în `ready`. Fără registrul aspect→sursă, versiunea oricărui aspect e 0,
      deci ORICE rezumat pare curent, pe veci; fără triggere, nimic nu mai invalidează; fără
      coloana `epoca`, dependența de timp dispare. *Niciuna nu dă eroare la citire.*

  BLOCAJ PE ACEEAȘI SESIUNE   `pg_try_advisory_lock` e ținut de CONEXIUNE, nu de tranzacție. Luat
      pe o conexiune din pool și eliberat pe alta, `pg_advisory_unlock` întoarce `false` pe o
      sesiune care nu ține nimic, iar blocajul rămâne agățat de prima — *iar o firmă blocată nu se
      vede ca eroare, se vede ca o firmă care nu se mai recalculează niciodată.*

**Ce face proba să nu fie tautologică:** `test_..._pool_chiar_da_sesiuni_diferite` verifică întâi
că pool-ul chiar întoarce backenduri PostgreSQL distincte. Fără el, toate probele de blocaj ar
putea trece pentru că pool-ul returnează din întâmplare aceeași conexiune.
"""
import logging
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import firma_rezumat as FR  # noqa: E402

SCHEMA_PROBA = "proba_p2_infra"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(autouse=True)
def _pool_viu():
    """`lifespan` închide pool-ul la ieșire. Fără fixtura asta, prima probă de startup ar lăsa
    restul fișierului fără bază — și ar pica din alt motiv decât cel testat."""
    yield
    try:
        _db.init_pool()
    except Exception:
        pass


@pytest.fixture
def firma_proba():
    """Firmă efemeră cu schemă REALĂ și triggere legate. Ștearsă la final."""
    if not _db_ok():
        pytest.skip("fara baza de date")

    def sterge():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (SCHEMA_PROBA,))
                r = cur.fetchone()
                if r:
                    for t in ("firma_rezumat", "firma_sursa_versiune", "supervizor_sursa",
                              "firma_tip"):
                        cur.execute("DELETE FROM public.%s WHERE tenant_id = %%s" % t, (r[0],))
                    cur.execute("DELETE FROM public.tenants WHERE id = %s", (r[0],))
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA_PROBA)
            c.commit()

    sterge()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('CREATE SCHEMA "%s"' % SCHEMA_PROBA)
            for t in ("facturi", "solduri_initiale", "plan_conturi", "salariati", "articole"):
                cur.execute('CREATE TABLE "%s".%s (id serial PRIMARY KEY, x integer)'
                            % (SCHEMA_PROBA, t))
            cur.execute('CREATE TABLE "%s".firma_profil (id integer PRIMARY KEY, tip_firma text)'
                        % SCHEMA_PROBA)
            cur.execute('INSERT INTO "%s".firma_profil (id, tip_firma) VALUES (1, %%s)'
                        % SCHEMA_PROBA, ("srl",))
            cur.execute("INSERT INTO public.tenants (schema_name, nume, activ) "
                        "VALUES (%s, 'PROBA P2 INFRA', true) RETURNING id", (SCHEMA_PROBA,))
            tid = cur.fetchone()[0]
        FR.leaga_triggerele_firma(c, SCHEMA_PROBA, tid)
        c.commit()
    yield tid, SCHEMA_PROBA
    sterge()


def _porneste_aplicatia():
    """Rulează `lifespan` cap-coadă. Ridică dacă startup-ul refuză să pornească."""
    from fastapi.testclient import TestClient
    import main as _main
    with TestClient(_main.app) as cl:
        return cl.get("/").status_code


# ============================================================================
#  TASK 1 — STARTUP FAIL-CLOSED
# ============================================================================
def test_p2_startup_fails_if_ddl_fails(monkeypatch):
    """1A. DDL-ul central ridică -> aplicația NU intră în `ready`."""
    if not _db_ok():
        pytest.skip("fara baza de date")

    def _explodeaza(conn):
        raise RuntimeError("proba: DDL P2 indisponibil")

    monkeypatch.setattr(FR, "aplica_ddl", _explodeaza)
    with pytest.raises(RuntimeError, match="proba: DDL P2 indisponibil"):
        _porneste_aplicatia()


def test_p2_startup_fails_if_trigger_migration_incomplete(monkeypatch):
    """1B. O singură firmă căreia nu i se pot lega triggerele oprește pornirea.

    Nu „un avertisment și mergem mai departe": firma aceea ar rămâne cu rezumatul necurățat de
    nimic, iar ecranul l-ar arăta drept curent."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    real = FR.leaga_triggerele_firma
    stare = {"n": 0}

    def _prima_pica(conn, schema, tenant_id):
        stare["n"] += 1
        if stare["n"] == 1:
            raise RuntimeError("proba: nu se pot lega triggerele")
        return real(conn, schema, tenant_id)

    monkeypatch.setattr(FR, "leaga_triggerele_firma", _prima_pica)
    with pytest.raises(RuntimeError, match="infrastructura de invalidare INCOMPLET"):
        _porneste_aplicatia()
    assert stare["n"] > 1, ("migrarea s-a oprit la prima firmă — raportul n-ar putea spune CÂTE "
                            "firme sunt rupte, doar care e prima")


def test_p2_startup_detects_missing_trigger(firma_proba, monkeypatch):
    """1C. Un trigger șters DUPĂ migrare e prins de verificare, iar startup-ul pică.

    *Că `CREATE TRIGGER` n-a ridicat excepție nu spune că mecanismul e pe loc.*"""
    tid, schema = firma_proba

    real = FR.migreaza_triggerele

    def _migreaza_apoi_sterge(conn, doar_active=True):
        rap = real(conn, doar_active)
        with conn.cursor() as cur:      # sabotaj DUPĂ migrare, ca verificarea să aibă ce prinde
            cur.execute('DROP TRIGGER trg_sursa_facturi ON "%s".facturi' % schema)
        return rap

    monkeypatch.setattr(FR, "migreaza_triggerele", _migreaza_apoi_sterge)
    with pytest.raises(RuntimeError, match="verificarea infrastructurii a picat"):
        _porneste_aplicatia()


def test_p2_verificarea_prinde_registrul_desincronizat(monkeypatch):
    """Un registru `firma_aspect_sursa` rămas în urmă NU dă eroare la citire: agregarea pur și
    simplu nu numără sursa lipsă, iar aspectul pare curent la infinit. Trebuie prins."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_aspect_sursa WHERE tabela = 'facturi'")
        v = FR.verifica_infrastructura(c)
        c.rollback()            # sabotajul NU se comite
    assert not v["ok"]
    coduri = {p["cod"] for p in v["probleme"]}
    assert FR.COD_REGISTRU_DESINCRONIZAT in coduri, v["probleme"]
    # și DATELE problemei, nu proza ei: se numește chiar perechea care lipsește din bază
    p = next(p for p in v["probleme"] if p["cod"] == FR.COD_REGISTRU_DESINCRONIZAT)
    assert any(t == "facturi" for _a, t in p["ce"]["doar_in_cod"]), p["ce"]


def test_p2_verificarea_prinde_o_functie_lipsa():
    """Un trigger peste o funcție care lipsește există în catalog și nu face nimic."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    assert set(FR.FUNCTII_PG) >= {"marcheaza_sursa"}, "lista de funcții s-a golit"
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM pg_proc p JOIN pg_namespace n "
                        "  ON n.oid = p.pronamespace "
                        " WHERE n.nspname = 'public' AND p.proname = ANY(%s)", (list(FR.FUNCTII_PG),))
            assert cur.fetchone()[0] == len(FR.FUNCTII_PG), "o funcție PostgreSQL a dispărut"


def test_p2_trigger_migration_is_idempotent(firma_proba):
    """1D. A doua migrare nu schimbă nimic și nu lasă triggere duplicate."""
    tid, schema = firma_proba

    def _numara():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    "SELECT c.relname, t.tgname FROM pg_trigger t "
                    "  JOIN pg_class c ON c.oid = t.tgrelid "
                    "  JOIN pg_namespace n ON n.oid = c.relnamespace "
                    " WHERE n.nspname = %s AND NOT t.tgisinternal", (schema,))
                return sorted(cur.fetchall())

    inainte = _numara()
    assert inainte, "proba n-are obiect: firma de probă n-are niciun trigger"
    with _db.get_conn() as c:
        r1 = FR.migreaza_triggerele(c)
        c.commit()
    dupa1 = _numara()
    with _db.get_conn() as c:
        r2 = FR.migreaza_triggerele(c)
        c.commit()
    dupa2 = _numara()

    assert r1["esecuri"] == [] and r2["esecuri"] == []
    assert dupa1 == dupa2 == inainte, "migrarea repetată a schimbat setul de triggere"
    assert len(dupa2) == len(set(dupa2)), "triggere duplicate"
    with _db.get_conn() as c:
        assert FR.verifica_infrastructura(c)["ok"]


def test_p2_startup_happy_path():
    """1D. Pe o bază corectă, pornirea reușește — și reușește și a doua oară."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    assert _porneste_aplicatia() == 200
    assert _porneste_aplicatia() == 200


# ============================================================================
#  TASK 2 — BLOCAJUL LUCRĂTORULUI
# ============================================================================
def _blocaje_active(tenant_id):
    """Câte blocaje consultative cu CHEIA NOASTRĂ sunt ținute acum pentru firma asta.
    Se întreabă `pg_locks` — catalogul lui PostgreSQL, nu o variabilă din proces."""
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' "
                        "   AND classid = %s AND objid = %s AND granted",
                        (FR.CHEIE_BLOCAJ, tenant_id))
            return cur.fetchone()[0]


def test_p2_pool_chiar_da_sesiuni_diferite():
    """ANTI-TAUTOLOGIE, și e proba de care atârnă toate cele de mai jos.

    Dacă pool-ul ar întoarce mereu aceeași conexiune, „lock pe A, unlock pe B" ar trece din
    întâmplare, iar defectul reparat ar rămâne nedemonstrat."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    p = _db.pool()
    a, b = p.getconn(), p.getconn()
    try:
        with a.cursor() as cur:
            cur.execute("SELECT pg_backend_pid()")
            pid_a = cur.fetchone()[0]
        with b.cursor() as cur:
            cur.execute("SELECT pg_backend_pid()")
            pid_b = cur.fetchone()[0]
    finally:
        p.putconn(a)
        p.putconn(b)
    assert pid_a != pid_b, ("pool-ul a dat același backend de două ori (%s) — probele de blocaj "
                            "n-ar dovedi nimic" % pid_a)


def test_p2_worker_same_session_advisory_lock(firma_proba):
    """2 + 2D. Blocajul se ia și se eliberează pe ACELAȘI backend PostgreSQL.

    Se compară PID-ul backendului, citit odată cu luarea și odată cu eliberarea — nu identitatea
    obiectului Python, care nu spune nimic despre sesiunea din bază."""
    tid, _schema = firma_proba
    with _db.get_conn() as lock_conn:
        luat, pid_lock = FR.ia_blocajul(lock_conn, tid)
        assert luat
        assert _blocaje_active(tid) == 1
        with lock_conn.cursor() as cur:
            cur.execute("SELECT pg_backend_pid()")
            assert cur.fetchone()[0] == pid_lock
        eliberat = FR.lasa_blocajul(lock_conn, tid, pid_lock)
    assert eliberat is True
    assert _blocaje_active(tid) == 0


def test_p2_worker_second_worker_skips_locked_tenant(firma_proba):
    """2A. Cu firma blocată de altă sesiune, tura NU o recalculează — și n-o așteaptă."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()

    p = _db.pool()
    alta_sesiune = p.getconn()          # „workerul A" — o sesiune PostgreSQL distinctă
    try:
        luat, _pid = FR.ia_blocajul(alta_sesiune, tid)
        assert luat, "n-am putut lua blocajul; proba n-ar avea obiect"
        r = FR.recalculeaza_lot(limita=5000)     # „workerul B"
        assert r["sarite_blocate"] >= 1, "a doua tură a intrat peste firma blocată"
        with _db.get_conn() as c:
            ramase = {a for t, a in FR.de_recalculat(c, 5000) if t == tid}
        assert ramase, "firma blocată apare ca recalculată, deși n-a fost atinsă"
    finally:
        FR.lasa_blocajul(alta_sesiune, tid)
        p.putconn(alta_sesiune)
    assert _blocaje_active(tid) == 0


def test_p2_worker_unlocks_after_success(firma_proba):
    """2B. După o tură reușită, blocajul nu mai e ținut de nimeni."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    r = FR.recalculeaza_lot(limita=5000)
    assert r["blocaje_neeliberate"] == 0
    assert _blocaje_active(tid) == 0, "blocaj scurs după o tură reușită"

    p = _db.pool()                       # și chiar poate fi luat din nou
    c2 = p.getconn()
    try:
        luat, _ = FR.ia_blocajul(c2, tid)
        assert luat, "blocajul a rămas ținut: nicio altă sesiune nu-l mai poate lua"
        FR.lasa_blocajul(c2, tid)
    finally:
        p.putconn(c2)


def test_p2_worker_unlocks_after_exception(firma_proba, monkeypatch):
    """2C. `finally` — recalcularea crapă, blocajul se eliberează oricum."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()

    def _crapa(*a, **k):
        raise RuntimeError("proba: recalcularea a crăpat")

    monkeypatch.setattr(FR, "recalculeaza_firma", _crapa)
    with pytest.raises(RuntimeError, match="proba: recalcularea a crăpat"):
        FR.recalculeaza_lot(limita=5000)
    assert _blocaje_active(tid) == 0, "blocaj scurs după o excepție — `finally` nu funcționează"


def test_p2_worker_unlock_false_observable(firma_proba, caplog):
    """2E. Un `unlock` care întoarce `false` NU se înghite: se logează ca EROARE.

    E chiar simptomul defectului reparat — o sesiune care crede că eliberează ceva ce nu ține."""
    tid, _schema = firma_proba
    with caplog.at_level(logging.ERROR, logger="iconta.firma_rezumat"):
        with _db.get_conn() as c:
            eliberat = FR.lasa_blocajul(c, tid)     # nimeni n-a luat blocajul
    assert eliberat is False
    # Se cere STRUCTURA înregistrării de log — nivel, logger, argumente —, nu un subșir din
    # mesajul randat: proza se rescrie, iar proba care se sprijină pe ea se rupe tăcut.
    erori = [r for r in caplog.records
             if r.levelno >= logging.ERROR and r.name == "iconta.firma_rezumat"]
    assert erori, "unlock-ul false n-a lăsat nicio urmă în log"
    assert any(tid in (r.args or ()) for r in erori), \
        "eroarea nu numește firma, deci n-ar fi de niciun folos la diagnostic"


def test_p2_worker_semnaleaza_sesiuni_diferite(firma_proba, caplog):
    """Dacă vreodată blocajul s-ar lua pe o sesiune și s-ar elibera pe alta, trebuie SĂ SE VADĂ.
    Se simulează deliberat, ca garda să fie probată pe chiar defectul de dinainte."""
    tid, _schema = firma_proba
    p = _db.pool()
    a, b = p.getconn(), p.getconn()
    try:
        luat, pid_a = FR.ia_blocajul(a, tid)
        assert luat
        with caplog.at_level(logging.ERROR, logger="iconta.firma_rezumat"):
            FR.lasa_blocajul(b, tid, pid_a)         # eliberare pe ALTĂ sesiune
        # structural: o eroare care poartă AMÂNDOUĂ PID-urile, deci chiar despre asta vorbește
        erori = [r for r in caplog.records
                 if r.levelno >= logging.ERROR and r.name == "iconta.firma_rezumat"]
        assert any(pid_a in (r.args or ()) and tid in (r.args or ()) for r in erori), \
            "eliberarea pe altă sesiune a trecut tăcut — exact defectul reparat"
        assert _blocaje_active(tid) == 1, "blocajul chiar a rămas agățat de prima sesiune"
        FR.lasa_blocajul(a, tid, pid_a)
    finally:
        p.putconn(a)
        p.putconn(b)
    assert _blocaje_active(tid) == 0


def test_p2_worker_no_lock_leak_in_pool(firma_proba):
    """2 + 2.5. După tură, NICIUN blocaj cu cheia noastră nu mai e ținut, pentru nicio firmă.

    Se întreabă `pg_locks` global, nu doar pentru firma de probă: un blocaj scurs pe altă firmă ar
    fi la fel de grav și n-ar fi prins de o probă țintită."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    FR.recalculeaza_lot(limita=5000)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT objid FROM pg_locks WHERE locktype = 'advisory' "
                        "   AND classid = %s AND granted", (FR.CHEIE_BLOCAJ,))
            scurse = [r[0] for r in cur.fetchall()]
    assert scurse == [], "blocaje rămase ținute după tură, pentru firmele: %s" % scurse


# ============================================================================
#  POST-P2 HARDENING (09.09.2026) — A: ordinea taskurilor de fundal
# ============================================================================
def test_taskurile_de_fundal_nu_pornesc_daca_infrastructura_pica(monkeypatch):
    """A. La eșec de infrastructură, bucla de sănătate NU se pornește.

    Nu era un defect de corectitudine — startup-ul e fail-closed —, dar era o ordine care nu se
    poate apăra: un task de fundal legat de o bază despre care încă nu se știe dacă poartă
    infrastructura P2. *Ordinea corectă e: deschizi, instalezi, VERIFICI, apoi pornești ce rulează
    singur.*"""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import main as _main
    inainte = _main._TASKURI_FUNDAL_PORNITE

    def _explodeaza(conn):
        raise RuntimeError("proba: DDL P2 indisponibil")

    monkeypatch.setattr(FR, "aplica_ddl", _explodeaza)
    with pytest.raises(RuntimeError, match="proba: DDL P2 indisponibil"):
        _porneste_aplicatia()
    assert _main._TASKURI_FUNDAL_PORNITE == inainte, (
        "un task de fundal a pornit peste o infrastructură care a picat")


def test_taskurile_de_fundal_pornesc_o_data_la_pornire_reusita():
    """A, direcția a doua: pe happy path taskul pornește, și pornește EXACT o dată.

    Fără ea, „nu pornește la eșec" ar trece și dacă n-ar porni niciodată."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import main as _main
    inainte = _main._TASKURI_FUNDAL_PORNITE
    assert _porneste_aplicatia() == 200
    assert _main._TASKURI_FUNDAL_PORNITE == inainte + 1, (
        "taskul de fundal a pornit de %d ori la o singură pornire"
        % (_main._TASKURI_FUNDAL_PORNITE - inainte))


# ============================================================================
#  B — izolarea migrării per tenant (SAVEPOINT)
# ============================================================================
def test_o_firma_rupta_nu_contamineaza_diagnosticul_celorlalte(firma_proba, monkeypatch):
    """B. O EROARE SQL REALĂ pe o firmă nu mai face restul să pice secundar.

    Fără `SAVEPOINT`, prima eroare lasă tranzacția în `current transaction is aborted`, iar toate
    firmele următoare eșuează **din cauza ei**. Raportul ar fi spus „N firme rupte" despre una
    singură, iar diagnosticul ar fi trimis omul să caute în locul greșit.

    Proba folosește o eroare SQL adevărată, nu un `raise` din Python: numai aia abortează
    tranzacția, deci numai aia probează chiar mecanismul reparat."""
    tid, schema = firma_proba
    real = FR.leaga_triggerele_firma

    def _pica_pe_proba(conn, sch, tenant_id):
        if tenant_id == tid:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tabela_care_nu_exista_niciodata_p2")
        return real(conn, sch, tenant_id)

    monkeypatch.setattr(FR, "leaga_triggerele_firma", _pica_pe_proba)
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.tenants WHERE activ")
            total = cur.fetchone()[0]
        rap = FR.migreaza_triggerele(c)
        c.rollback()        # proba nu comite nimic

    assert len(rap["esecuri"]) == 1, (
        "%d firme raportate ca rupte, deși una singură e stricată — tranzacția s-a contaminat: %s"
        % (len(rap["esecuri"]), [e["tenant_id"] for e in rap["esecuri"]]))
    assert rap["esecuri"][0]["tenant_id"] == tid
    assert rap["firme"] == total - 1, (
        "celelalte %d firme n-au fost evaluate independent" % (total - 1 - rap["firme"]))


# ============================================================================
#  C — driftul de după pornire
# ============================================================================
def test_driftul_unui_trigger_sters_e_detectat_si_reparabil(firma_proba):
    """C. Sănătos → PASS · trigger șters → FAIL · repus → PASS.

    Verificarea e **read-only**: nu recreează nimic. O buclă care ar repara singură ar șterge chiar
    semnalul — driftul ar dispărea din log, iar cauza n-ar mai fi căutată de nimeni."""
    tid, schema = firma_proba
    with _db.get_conn() as c:
        assert FR.verifica_drift(c)["ok"] is True, "punct de plecare nesănătos"

        with c.cursor() as cur:
            cur.execute('DROP TRIGGER trg_sursa_facturi ON "%s".facturi' % schema)
        c.commit()
    with _db.get_conn() as c:
        st = FR.verifica_drift(c)
        assert st["ok"] is False, "un trigger șters n-a fost detectat"
        assert FR.COD_TRIGGERE_LIPSA in {p["cod"] for p in st["probleme"]}
        assert st["verificat_la"] is not None
        # READ-ONLY: verificarea NU l-a pus la loc
        with c.cursor() as cur:
            cur.execute("SELECT count(*) FROM pg_trigger tg JOIN pg_class cl "
                        "    ON cl.oid = tg.tgrelid JOIN pg_namespace n ON n.oid = cl.relnamespace "
                        " WHERE n.nspname = %s AND tg.tgname = 'trg_sursa_facturi'", (schema,))
            assert cur.fetchone()[0] == 0, "verificarea a REPARAT singură — nu asta e rolul ei"

    with _db.get_conn() as c:            # repunerea e un act deliberat, prin migrare
        FR.leaga_triggerele_firma(c, schema, tid)
        c.commit()
    with _db.get_conn() as c:
        assert FR.verifica_drift(c)["ok"] is True, "după repunere, starea n-a revenit"


def test_verificarea_de_drift_nu_intra_in_calea_de_cerere(firma_proba):
    """C. Verificarea stă în bucla de sănătate, NU în cereri. Altfel ar întreba catalogul de zeci
    de ori pe secundă — exact munca pe care P2 a scos-o din cererea interactivă."""
    import main as _main
    apeluri = {"n": 0}
    real = FR.verifica_drift

    def _numarat(conn, acum=None):
        apeluri["n"] += 1
        return real(conn, acum)

    FR.verifica_drift = _numarat
    try:
        from fastapi.testclient import TestClient
        cl = TestClient(_main.app)          # fără lifespan: se măsoară CEREREA, nu pornirea
        try:
            for _ in range(3):
                cl.get("/")
                cl.get("/control-fiscal")   # 401 fără token, dar trece prin dependențe
        finally:
            cl.close()
    finally:
        FR.verifica_drift = real
    assert apeluri["n"] == 0, "verificarea de drift a rulat de %d ori în calea de cerere" % apeluri["n"]


# ============================================================================
#  D — observabilitatea backlogului
# ============================================================================
def test_masura_backlogului_numara_ce_asteapta_si_de_cand(firma_proba):
    """D. Backlog construit deliberat: perechi, firme, `fara_calcul`, vechime.

    *„1000 în așteptare" nu spune dacă ecranele mint de zece secunde sau de patru ore.* Cifra care
    contează e vechimea celei mai vechi invalidări — și e un PLAFON SUPERIOR, fiindcă nu ținem
    istoricul schimbărilor de sursă (vezi `masura_backlog`)."""
    import datetime
    tid, schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
        b = FR.masura_backlog(c)
    ale_mele = len(FR.TOATE)
    assert b["perechi_restante"] >= ale_mele
    assert b["firme_restante"] >= 1
    assert b["fara_calcul"] >= ale_mele, "perechile necalculate niciodată nu sunt numărate separat"

    # acum una calculată, dar invalidată: capătă vechime
    ieri = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=3)
    with _db.get_conn() as c:
        v = FR.versiuni_aspecte(c, tid, ["solduri"])
        FR.scrie(c, tid, "solduri", {"x": 1}, v["solduri"] - 1,
                 epoca=FR.epoca_pentru("solduri", datetime.date.today()))
        with c.cursor() as cur:
            cur.execute("UPDATE public.firma_rezumat SET calculat_la = %s "
                        " WHERE tenant_id = %s AND aspect = 'solduri'", (ieri, tid))
        c.commit()
        b2 = FR.masura_backlog(c)
    assert b2["vechime_maxima_sec"] is not None
    assert b2["vechime_maxima_sec"] >= 3 * 3600 - 60, (
        "vechimea măsurată (%s s) nu reflectă cele trei ore" % b2["vechime_maxima_sec"])


def test_tura_raporteaza_metricile_cerute(firma_proba):
    """D. Raportul turei poartă fiecare cifră din care se derivă metricile `p2_worker_*`."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()
    r = FR.recalculeaza_lot(limita=5000)
    for cheie in ("perechi", "recalculate", "ramase", "erori", "sarite_blocate",
                  "blocaje_neeliberate", "secunde", "vechime_maxima_sec", "firme",
                  "fara_calcul", "in_eroare", "oprit", "fara_firma"):
        assert cheie in r, "raportul turei n-are `%s`" % cheie
    assert r["secunde"] >= 0
    # `recalculate` + `erori` = perechile ÎNCERCATE. Pe schema de probă (care n-are toate cele 52
    # de tabele) aspectele grele cad în `erori`, cu starea `eroare` scrisă — nu dispar. Proba cere
    # ca fiecare pereche în așteptare să fi fost ATINSĂ, nu ca toate să reușească.
    assert r["recalculate"] + r["erori"] >= len(FR.TOATE), (
        "firma de probă n-a fost încercată pe toate aspectele: %d reușite + %d erori"
        % (r["recalculate"], r["erori"]))
    assert r["ramase"] >= 0


# ============================================================================
#  E — monotonicitatea versiunilor
# ============================================================================
def test_versiunea_sursei_doar_creste(firma_proba):
    """E. Două scrieri în sursă → două versiuni strict crescătoare.

    Pe invarianta asta stă tot modelul de prospețime: prospețimea se decide comparând suma
    contoarelor de acum cu suma de la calcul. Dacă un contor ar putea SCĂDEA, o sumă veche ar putea
    redeveni egală cu cea curentă — iar un rezumat învechit ar reapărea ca `curent`, tăcut."""
    tid, schema = firma_proba

    def _versiune():
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT versiune FROM public.firma_sursa_versiune "
                            " WHERE tenant_id = %s AND tabela = 'facturi'", (tid,))
                r = cur.fetchone()
        return r[0] if r else 0

    v0 = _versiune()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".facturi (x) VALUES (1)' % schema)
        c.commit()
    v1 = _versiune()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".facturi (x) VALUES (2)' % schema)
        c.commit()
    v2 = _versiune()
    assert v1 > v0 and v2 > v1, "contorul nu crește strict: %s -> %s -> %s" % (v0, v1, v2)


def test_o_scadere_de_versiune_e_REFUZATA_de_baza(firma_proba):
    """E. Invarianta nu depinde de disciplina apelanților: baza o impune.

    Se încearcă deliberat o scădere — pe calea pe care ar face-o o migrare externă sau o mână pe
    `psql`, nu prin API-ul aplicației. Trebuie respinsă."""
    import psycopg2
    tid, schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute('INSERT INTO "%s".facturi (x) VALUES (3)' % schema)
        c.commit()
    with pytest.raises(psycopg2.Error) as ex:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("UPDATE public.firma_sursa_versiune SET versiune = 0 "
                            " WHERE tenant_id = %s AND tabela = 'facturi'", (tid,))
    assert getattr(ex.value, "pgcode", None) == "23514", (
        "scăderea n-a fost respinsă cu `check_violation`, ci cu %r" % getattr(ex.value, "pgcode", None))


def test_p2_worker_nu_epuizeaza_poolul(firma_proba):
    """REGRESIA PE CARE O INTRODUCE REPARAȚIA, măsurată — nu presupusă.

    Ținând conexiunea de blocaj pe toată durata recalculării, tura folosește cu una mai mult decât
    înainte. Dacă vârful de conexiuni simultane atinge plafonul pool-ului, `getconn` ridică
    `PoolError` și tura moare — deci se măsoară vârful, nu se afirmă că „e destul loc"."""
    tid, _schema = firma_proba
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM public.firma_rezumat WHERE tenant_id = %s", (tid,))
        c.commit()

    import contextlib
    original = _db.get_conn
    stare = {"acum": 0, "varf": 0}

    @contextlib.contextmanager
    def _numarat(schema=None):
        stare["acum"] += 1
        stare["varf"] = max(stare["varf"], stare["acum"])
        try:
            with original(schema) as c:
                yield c
        finally:
            stare["acum"] -= 1

    _db.get_conn = _numarat
    try:
        FR.recalculeaza_lot(limita=5000)
    finally:
        _db.get_conn = original

    plafon = int(getattr(_db.pool(), "maxconn", 10) or 10)
    assert stare["varf"] >= 2, "măsurătoarea n-a văzut nimic — proba n-ar putea eșua"
    assert stare["varf"] < plafon, (
        "vârf de %d conexiuni simultane la un plafon de %d — tura poate muri cu PoolError"
        % (stare["varf"], plafon))
