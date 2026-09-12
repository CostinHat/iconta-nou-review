# -*- coding: utf-8 -*-
"""P6 valul 1 — probele de acceptare: starea business e comuna intre procese, si nu mai pierde.

Cele sase probe cerute de arhitect, in ordinea lui. Fiecare are scris langa ea CE ar trece daca
reparatia ar fi facuta pe jumatate — fiindca o proba care nu poate distinge reparatia de aparenta
ei nu e o proba.

  A  LOGIN MULTI-PROCESS   cinci esecuri pe instanta A -> urmatoarea cerere pe B e blocata.
                           DOUA PROCESE DE SISTEM, prin ruta HTTP reala. Cu starea in memorie,
                           B raspundea 401 (necunoscator); acum raspunde 429.
  B  LOGIN CONCURRENCY     k=2,5,10 plus presiunea sustinuta din diagnostic -> LOST_UPDATES=0.
                           Cu forma dinainte se pierdeau 87% din esecuri la k=10.
  C  LOGIN EXPIRY          dupa fereastra, incercarile vechi nu mai contribuie — si nici nu mai
                           stau in tabela dupa prima scriere.
  D  ALERT COOLDOWN        A rezerva -> B, alt proces, NU retrimite in fereastra.
  E  FAILURE               baza cazuta -> esec curat: fara stare partiala, fara falsa confirmare,
                           si mai ales fara «nu e blocat» spus dintr-o eroare.
  F  TWO LIVE INSTANCES    cele doua procese din A si D sunt reale si IZOLATE: se dovedeste
                           mecanic ca n-au pornit bucle de fundal cu efecte in afara.

IZOLAREA PROBEI, ceruta explicit. Procesele-copil NU intra in `lifespan`: isi deschid singure
pool-ul si cheama `TestClient` fara context manager. Deci ruta, modelul, validarea si baza sunt
cele reale, dar bucla de alerte — singura care are efect in AFARA (e-mail catre superadmin) — nu
porneste. `test_F_*` nu crede asta pe cuvant: citeste contorul de taskuri din fiecare copil.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time

import pytest

RADACINA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RADACINA)

from core import db as _db  # noqa: E402
from core import stare_partajata as _sp  # noqa: E402

#: Presiunea sustinuta din diagnosticul de pe 12.09, aceeasi forma si acelasi ordin de marime:
#: acolo k=10 x 500 runde au pierdut 4326 din 5000 de esecuri.
RUNDE_PRESIUNE = 500
EMAIL_BAZA = "ztest_wave1_%s@invalid"
CATEGORIE_BAZA = "ztest_wave1_%s"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn() as c:
            _sp.aplica_ddl(c)
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _curata(email=None, categorie=None):
    with _db.get_conn() as c, c.cursor() as cur:
        if email:
            cur.execute("DELETE FROM public.login_esecuri WHERE email = %s", (email,))
        if categorie:
            cur.execute("DELETE FROM public.alerte_cooldown WHERE categorie = %s", (categorie,))


# ============================================================
#  Copilul: un PROCES separat, cu propria memorie si propriul pool
# ============================================================
COPIL = r'''
import json, os, sys
sys.path.insert(0, %(rad)r)
from core import db
db.init_pool()                       # pool propriu, FARA `lifespan` -> fara bucle de fundal
import main
from fastapi.testclient import TestClient
cl = TestClient(main.app)            # fara `with`: lifespan NU ruleaza

rol, arg = sys.argv[1], sys.argv[2]
out = {"rol": rol, "taskuri_fundal": main._TASKURI_FUNDAL_PORNITE, "pid": os.getpid()}

if rol == "login":
    coduri = []
    for _ in range(int(sys.argv[3])):
        r = cl.post("/auth/login", json={"email": arg, "parola": "gresita-oricum"})
        coduri.append(r.status_code)
    out["coduri"] = coduri
elif rol == "alerta":
    out["rezervat"] = main._poate_alerta(arg)

print("__REZULTAT__" + json.dumps(out))
''' % {"rad": RADACINA}


def _copil(rol, arg, n=1):
    cale = os.path.join(RADACINA, ".lant_tmp_wave1_copil.py")
    with open(cale, "w") as f:
        f.write(COPIL)
    try:
        r = subprocess.run([sys.executable, cale, rol, str(arg), str(n)],
                           capture_output=True, text=True, cwd=RADACINA,
                           env=dict(os.environ), timeout=180)
        linii = [x for x in r.stdout.splitlines() if x.startswith("__REZULTAT__")]
        if not linii:
            raise AssertionError("procesul-copil n-a raportat nimic.\nstdout: %s\nstderr: %s"
                                 % (r.stdout[-800:], r.stderr[-1500:]))
        return json.loads(linii[-1][len("__REZULTAT__"):])
    finally:
        if os.path.exists(cale):
            os.remove(cale)


# ============================================================
#  A. LOGIN MULTI-PROCESS
# ============================================================
def test_A_blocarea_produsa_de_un_proces_e_vazuta_de_celalalt():
    """Criteriul canonic `PLAN_HARDENING.md:715`: «blocarea la autentificare ține pe ambele»."""
    email = EMAIL_BAZA % "multiproc"
    _curata(email=email)
    try:
        a = _copil("login", email, _sp.PRAG_ESECURI)
        assert a["coduri"] == [401] * _sp.PRAG_ESECURI, (
            "instanta A trebuia sa refuze de %d ori cu 401, a dat %s"
            % (_sp.PRAG_ESECURI, a["coduri"]))

        b = _copil("login", email, 1)
        assert b["pid"] != a["pid"], "probele A si B au rulat in acelasi proces"
        assert b["coduri"] == [429], (
            "instanta B a raspuns %s in loc de 429 — nu vede esecurile lui A, deci starea e "
            "inca in memoria unui proces" % b["coduri"])
    finally:
        _curata(email=email)


# ============================================================
#  B. LOGIN CONCURRENCY
# ============================================================
def _presiune(k, runde, email):
    """Aceeasi forma ca in diagnostic: fiecare fir intreaba DACA e blocat, apoi consemneaza un
    esec. Acolo, intrebarea rescria lista si inghitea ce adaugase alt fir."""
    import main
    erori = []
    latente = []
    lat_lock = threading.Lock()
    bariera = threading.Barrier(k)

    def fir():
        bariera.wait()
        for _ in range(runde):
            t0 = time.perf_counter()
            try:
                main._login_blocat(email)
                main._login_esec(email)
            except Exception as e:                      # noqa: BLE001 — se RAPORTEAZA, nu se inghite
                erori.append(repr(e))
                return
            with lat_lock:
                latente.append(time.perf_counter() - t0)

    fire = [threading.Thread(target=fir) for _ in range(k)]
    t0 = time.perf_counter()
    for f in fire:
        f.start()
    for f in fire:
        f.join()
    total = time.perf_counter() - t0
    with _db.get_conn() as c:
        vazute = _sp.esecuri_in_fereastra(c, email)
    latente.sort()

    def pct(p):
        if not latente:
            return None
        return latente[min(len(latente) - 1, int(round(p / 100.0 * (len(latente) - 1))))]

    return {"trimise": k * runde, "vazute": vazute, "pierdute": k * runde - vazute,
            "erori": erori, "p50": pct(50), "p95": pct(95), "p99": pct(99), "total": total}


@pytest.mark.parametrize("k", [2, 5, 10])
def test_B_nicio_inserare_pierduta(k):
    email = EMAIL_BAZA % ("conc%d" % k)
    _curata(email=email)
    try:
        r = _presiune(k, 1, email)
        assert not r["erori"], "erori in fire: %s" % r["erori"][:3]
        assert r["pierdute"] == 0, (
            "k=%d: %d esecuri trimise, %d vazute in baza -> LOST_UPDATES=%d"
            % (k, r["trimise"], r["vazute"], r["pierdute"]))
    finally:
        _curata(email=email)


def test_B_presiune_sustinuta_echivalenta_diagnosticului():
    """k=10 x 500 runde — exact forma care pierdea 4326 din 5000 in memoria procesului."""
    email = EMAIL_BAZA % "presiune"
    _curata(email=email)
    try:
        r = _presiune(10, RUNDE_PRESIUNE, email)
        assert not r["erori"], "erori in fire: %s" % r["erori"][:3]
        assert r["pierdute"] == 0, (
            "presiune sustinuta: %d trimise, %d vazute -> LOST_UPDATES=%d. Forma dinainte pierdea "
            "87%% aici." % (r["trimise"], r["vazute"], r["pierdute"]))
    finally:
        _curata(email=email)


# ============================================================
#  C. LOGIN EXPIRY
# ============================================================
def test_C_esecurile_iesite_din_fereastra_nu_mai_contribuie():
    email = EMAIL_BAZA % "expirare"
    _curata(email=email)
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO public.login_esecuri (email, esuat_la) "
                "SELECT %s, now() - make_interval(secs => %s) FROM generate_series(1, %s)",
                (email, _sp.FEREASTRA_ESECURI_SEC + 60, _sp.PRAG_ESECURI + 3))
        with _db.get_conn() as c:
            assert _sp.esecuri_in_fereastra(c, email) == 0, "randuri expirate inca numarate"
            assert _sp.login_blocat(c, email) is False, (
                "cont blocat de esecuri iesite din fereastra — pragul ar deveni permanent")
    finally:
        _curata(email=email)


def test_C_expirarea_e_si_MARGINITA_nu_doar_filtrata_la_citire():
    """Contractul cere expirare «explicita si marginita». Filtrarea la citire e explicita; ca
    tabela sa nu creasca la nesfarsit, orice SCRIERE sterge si ce a iesit din fereastra."""
    vechi = EMAIL_BAZA % "marginit_vechi"
    nou = EMAIL_BAZA % "marginit_nou"
    _curata(email=vechi)
    _curata(email=nou)
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO public.login_esecuri (email, esuat_la) "
                "SELECT %s, now() - make_interval(secs => %s) FROM generate_series(1, 20)",
                (vechi, _sp.FEREASTRA_ESECURI_SEC + 60))
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s", (vechi,))
            assert cur.fetchone()[0] == 20

        with _db.get_conn() as c:          # o scriere pentru ALT cont
            _sp.login_esec(c, nou)

        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s", (vechi,))
            ramase = cur.fetchone()[0]
        assert ramase == 0, (
            "%d randuri expirate au supravietuit unei scrieri — tabela ar creste nemarginit"
            % ramase)
    finally:
        _curata(email=vechi)
        _curata(email=nou)


# ============================================================
#  D. ALERT COOLDOWN
# ============================================================
def test_D_cooldownul_e_global_intre_procese():
    categorie = CATEGORIE_BAZA % "cooldown"
    _curata(categorie=categorie)
    try:
        a = _copil("alerta", categorie)
        b = _copil("alerta", categorie)
        assert b["pid"] != a["pid"], "cele doua rezervari au rulat in acelasi proces"
        assert a["rezervat"] is True, "primul proces n-a putut rezerva"
        assert b["rezervat"] is False, (
            "al doilea proces a rezervat si el in aceeasi fereastra -> alerta ar pleca de doua "
            "ori. Exact defectul pe care valul 1 il inchide.")
    finally:
        _curata(categorie=categorie)


def test_D_din_zece_fire_simultane_rezerva_exact_unul():
    """Rezervarea e atomica, nu «aproape atomica»: nu «cel mult unul», ci EXACT unul."""
    import main
    categorie = CATEGORIE_BAZA % "cursa"
    _curata(categorie=categorie)
    try:
        castiguri = []
        lock = threading.Lock()
        bariera = threading.Barrier(10)

        def fir():
            bariera.wait()
            r = main._poate_alerta(categorie)
            with lock:
                castiguri.append(r)

        fire = [threading.Thread(target=fir) for _ in range(10)]
        for f in fire:
            f.start()
        for f in fire:
            f.join()
        assert sum(1 for x in castiguri if x) == 1, (
            "au castigat %d fire din 10 — rezervarea nu e atomica" % sum(1 for x in castiguri if x))
    finally:
        _curata(categorie=categorie)


# ============================================================
#  E. FAILURE
# ============================================================
class _BazaCazuta(Exception):
    """Tipul propriu al caderii simulate.

    Prima forma a probei de mai jos cauta sirul «cazut» in textul exceptiei. Un gard pe text
    pazeste FORMULAREA, nu comportamentul: ar fi trecut la fel daca `login_blocat` ar fi ridicat
    din cu totul alt motiv, atata timp cat mesajul continea bucata aia. Tipul e structura."""


class _ConnCrapata:
    def cursor(self, *a, **k):
        raise _BazaCazuta()


def test_E_login_blocat_RIDICA_nu_raspunde_ca_nu_e_blocat():
    """Cea mai importanta dintre probele de esec. Un `except` care ar intoarce `False` aici ar
    transforma o baza cazuta intr-o poarta de autentificare deschisa."""
    with pytest.raises(_BazaCazuta):
        _sp.login_blocat(_ConnCrapata(), "oricine@invalid")


def test_E_login_esec_nu_lasa_stare_partiala():
    """`login_esec` sterge expirate SI insereaza. Daca tranzactia cade intre ele, nici stergerea
    nu are voie sa ramana — altfel un esec pierdut ar fi insotit de o curatenie facuta pe jumatate."""
    vechi = EMAIL_BAZA % "atomic_vechi"
    nou = EMAIL_BAZA % "atomic_nou"
    _curata(email=vechi)
    _curata(email=nou)
    try:
        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute(
                "INSERT INTO public.login_esecuri (email, esuat_la) "
                "SELECT %s, now() - make_interval(secs => %s) FROM generate_series(1, 5)",
                (vechi, _sp.FEREASTRA_ESECURI_SEC + 60))

        pool = _db.pool()
        conn = pool.getconn()
        try:
            _sp.login_esec(conn, nou)      # sterge expiratele + insereaza
            conn.rollback()                # ...si tranzactia cade
        finally:
            pool.putconn(conn)

        with _db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s", (vechi,))
            expirate_ramase = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM public.login_esecuri WHERE email = %s", (nou,))
            inserate = cur.fetchone()[0]
        assert expirate_ramase == 5, (
            "stergerea a supravietuit unui rollback (%d din 5 randuri) — stare partiala"
            % expirate_ramase)
        assert inserate == 0, "inserarea a supravietuit unui rollback"
    finally:
        _curata(email=vechi)
        _curata(email=nou)


def test_E_alerta_la_baza_cazuta_NU_se_trimite_si_nu_tace(monkeypatch):
    """Fara rezervare nu se poate sti ca alt proces nu trimite chiar acum. Deci `False` — dar
    consemnat, fiindca un `except` tacut e chiar clasa pe care casa o interzice."""
    import main
    from core import observare as _obs

    consemnate = []
    monkeypatch.setattr(_obs, "esec_secundar",
                        lambda ce, e, *a, **k: consemnate.append(ce))

    def _crapa(*a, **k):
        raise RuntimeError("pool indisponibil")
    monkeypatch.setattr(main.db, "get_conn", _crapa)

    assert main._poate_alerta("ztest_wave1_baza_cazuta") is False, (
        "s-a raspuns `True` dintr-o eroare — alerta ar pleca din fiecare proces deodata")
    assert consemnate, "esecul a fost inghitit TACUT"


# ============================================================
#  F. TWO LIVE INSTANCES
# ============================================================
def test_F_cele_doua_instante_sunt_procese_reale_si_izolate():
    """Proba de acceptare foloseste doua procese de sistem, si o DOVEDESTE — PID-uri diferite.

    Si dovedeste izolarea ceruta: contorul de taskuri de fundal e 0 in fiecare, deci bucla de
    alerte (singura cu efect in afara: e-mail catre superadmin) n-a pornit. Fara verificarea asta,
    «am izolat proba» ar fi o afirmatie despre intentia mea, nu despre ce s-a intamplat.
    """
    categorie = CATEGORIE_BAZA % "izolare"
    _curata(categorie=categorie)
    try:
        a = _copil("alerta", categorie)
        b = _copil("alerta", categorie)
        assert a["pid"] != b["pid"] != os.getpid()
        for x in (a, b):
            assert x["taskuri_fundal"] == 0, (
                "procesul %s a pornit %d taskuri de fundal — proba nu e izolata"
                % (x["pid"], x["taskuri_fundal"]))
    finally:
        _curata(categorie=categorie)
