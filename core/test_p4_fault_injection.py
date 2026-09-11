# -*- coding: utf-8 -*-
"""GARD P4 — INJECȚIE DE DEFECT pe fiecare operație compusă critică.

**CE PROBEAZĂ.** Nu că funcțiile merg — asta o spun testele lor. Aici se probează **ce rămâne în
bază când ceva cade la mijloc**: se provoacă un eșec la fiecare frontieră dintre efectele unei
operații compuse și se compară **starea persistentă** dinainte cu cea de după.

**AMPRENTĂ, NU NUMĂRĂTOARE.** Starea se compară pe amprenta rândurilor, nu pe `count(*)`. Sonda
care număra rânduri a fost oarbă la modificări o dată (**R137**, 04.09.2026): a redenumit o firmă în
două tabele și a raportat „nicio schimbare de stare". Aici, `amprenta()` citește rândurile
ordonate și le rezumă în sha256 — un `UPDATE` mișcă amprenta.

**FIECARE PROBĂ ARE DOUĂ DIRECȚII.** Fără calea fără defect, o probă care asertează „nu s-a scris
nimic" ar trece și pe un cod care nu scrie niciodată nimic. De-asta fiecare probă verifică întâi
că **fără** defect actul CHIAR se scrie, apoi că **cu** defect nu rămâne jumătate. Un instrument
calibrat într-o singură direcție n-are niciun plafon (METODA §22).

**CE NU ACOPERĂ, declarat:**
  * defectele se injectează în PYTHON (o funcție ridică), nu la nivelul rețelei sau al procesului.
    O cădere a serverului PostgreSQL între `INSERT` și `COMMIT` are același efect ca aici —
    tranzacția nu se comite — dar nu e probată de mâna asta;
  * probele care ating ANAF, Brevo sau BNR lucrează pe substitute; ce se probează e **ordinea
    efectelor și proprietatea tranzacției**, nu comportamentul serviciului extern;
  * ce nu e clasificat `CRITICAL_COMPOSITE` în `core/p4_clasificare.py` nu are probă aici, iar
    motivul fiecărei excluderi e scris acolo. `core/test_tranzactii_clasificate.py` păzește
    corespondența: o cale critică fără probă cu numele ei **cade poarta**.
"""
import contextlib
import hashlib
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db          # noqa: E402
from core import auth_api           # noqa: E402
from core import tenant_provisioning as _tp   # noqa: E402

SCHEMA = "ztest_p4"
EMAIL_CAB = "ztest_p4_cabinet@exemplu.ro"
NUME_CAB = "ZTEST P4 CABINET"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ============================================================================
#  AMPRENTA — starea persistentă, rezumată; nu numărată
# ============================================================================

def amprenta(tabele, schema=None, unde=None):
    """`{tabel: sha256}` peste rândurile ordonate ale tabelelor date.

    `unde` — `{tabel: (fragment_sql, params)}`, ca amprenta să privească doar rândurile probei.
    Un tabel inexistent primește `"(lipsa)"`, ca să se vadă diferența dintre „gol" și „nu există".
    """
    out = {}
    with _db.get_conn(schema) as conn:
        for t in tabele:
            filtru, params = (unde or {}).get(t, ("", ()))
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT md5(t::text) FROM %s t %s ORDER BY 1"
                                % (t, ("WHERE " + filtru) if filtru else ""), params)
                    randuri = [r[0] for r in cur.fetchall()]
                out[t] = hashlib.sha256("|".join(randuri).encode()).hexdigest()[:16]
            except Exception:
                conn.rollback()
                out[t] = "(lipsa)"
    return out


# ============================================================================
#  MEDIUL — cabinet, user și firmă REALE, cu commituri reale; curățate la final
# ============================================================================

def _curata():
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.tenants WHERE schema_name = %s", (SCHEMA,))
            r = cur.fetchone()
            if r:
                # LISTA CANONICA, nu una scrisa de mana: aceeasi pe care o foloseste stergerea
                # unei firme (`tenant_stergere.TABELE_TENANT`), plus legaturile de utilizator.
                # Prima forma a probei avea o lista proprie, ii lipseau doua tabele, si a lasat in
                # urma **doi orfani** — prinsi de `test_tenant_stergere` si de blocul de cifre din
                # predare. *O probă care lasă baza mai murdară decât a găsit-o nu e o probă.*
                from core import tenant_stergere as _ts
                for t in tuple(_ts.TABELE_TENANT) + ("user_tenants", "urme_portal"):
                    try:
                        cur.execute("SAVEPOINT s")
                        cur.execute("DELETE FROM public.%s WHERE tenant_id = %%s" % t, (r[0],))
                        cur.execute("RELEASE SAVEPOINT s")
                    except Exception:
                        cur.execute("ROLLBACK TO SAVEPOINT s")
                cur.execute("DELETE FROM public.tenants WHERE id = %s", (r[0],))
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA)
            cur.execute("SELECT id FROM public.accounting_firms WHERE nume = %s", (NUME_CAB,))
            f = cur.fetchone()
            if f:
                cur.execute("SELECT id FROM public.users WHERE accounting_firm_id = %s", (f[0],))
                uids = [x[0] for x in cur.fetchall()] or [-1]
                for t in ("acord_termeni", "audit_log", "tokene_activare", "user_tenants",
                          "alerte_acces_dedup"):
                    try:
                        cur.execute("SAVEPOINT s")
                        cur.execute("DELETE FROM public.%s WHERE user_id = ANY(%%s)" % t, (uids,))
                        cur.execute("RELEASE SAVEPOINT s")
                    except Exception:
                        cur.execute("ROLLBACK TO SAVEPOINT s")
                cur.execute("DELETE FROM public.spv_token WHERE accounting_firm_id = %s", (f[0],))
                cur.execute("DELETE FROM public.users WHERE accounting_firm_id = %s", (f[0],))
                cur.execute("DELETE FROM public.accounting_firms WHERE id = %s", (f[0],))
            # Curatarea se face si pe ADRESA, nu doar pe cabinet: un rand ramas de la o rulare
            # de dinainte a facut proba de inregistrare sa numere doua dovezi in loc de una.
            cur.execute("DELETE FROM public.acord_termeni WHERE email LIKE 'ztest_p4%%'")
            cur.execute("DELETE FROM public.users WHERE email LIKE 'ztest_p4%%'")
            cur.execute("DELETE FROM public.accounting_firms WHERE nume LIKE 'ZTEST P4%%'")


@pytest.fixture
def mediu():
    """Cabinet + admin + firmă cu schemă reală. **Commituri reale** — altfel nu s-ar putea
    observa ce rămâne comis după un defect, adică exact întrebarea probei."""
    _curata()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id",
                        (NUME_CAB,))
            firm = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO public.users (email,password_hash,nume,prenume,rol,"
                "accounting_firm_id,activ,poate_pregati,poate_valida,poate_depune) "
                "VALUES (%s,'x','P4','Proba','admin_firma',%s,true,true,true,true) RETURNING id",
                (EMAIL_CAB, firm))
            uid = cur.fetchone()[0]
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % SCHEMA)
            cur.execute(_tp.parametrizeaza_template(
                open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
            cur.execute('SET search_path TO "%s", public' % SCHEMA)
            cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,"
                        "platitor_tva,tip_decont,serie_factura,urmator_numar_factura) "
                        "VALUES (1,'ZTEST P4 SRL','14399840','Str 1','Buc','B','6202',true,'L',"
                        "'P4',100)")
            cur.execute("SET search_path TO public")
            cur.execute("INSERT INTO public.tenants (schema_name,nume,cui,accounting_firm_id,activ)"
                        " VALUES (%s,'ZTEST P4 SRL','14399840',%s,true) RETURNING id",
                        (SCHEMA, firm))
            tid = cur.fetchone()[0]
            cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s,%s)",
                        (uid, tid))
    token = auth_api.emite_token({"id": uid, "rol": "admin_firma", "accounting_firm_id": firm})
    try:
        yield {"firm": firm, "uid": uid, "tid": tid, "schema": SCHEMA, "token": token}
    finally:
        _curata()


def _client():
    import main
    from fastapi.testclient import TestClient
    return TestClient(main.app)


@contextlib.contextmanager
def defect_in(obiect, nume, mesaj="defect injectat P4"):
    """Înlocuiește `obiect.nume` cu o funcție care ridică. Frontiera aleasă se numește în mesaj."""
    vechi = getattr(obiect, nume)

    def _crapa(*a, **k):
        raise RuntimeError(mesaj)

    setattr(obiect, nume, _crapa)
    try:
        yield
    finally:
        setattr(obiect, nume, vechi)


# ============================================================================
#  1. POST /coada/{id}/depune — confirmarea nu rămâne fără depunerea ei
# ============================================================================

def test_depunere_confirmarea_nu_ramane_fara_depunere(mediu, monkeypatch):
    """Frontiera probată: **între confirmarea supervizorului și marcarea depunerii**.

    Poarta supervizorului e înlocuită cu un substitut care scrie o confirmare pe conexiunea
    primită — adică exact ce face `scrie_confirmare` — și întoarce „nimic neconfirmat". Ce se
    probează nu e logica supervizorului, ci **a cui e tranzacția în care scrie el**.

    Calibrare în ambele direcții: fără defect, confirmarea RĂMÂNE (altfel proba ar trece și pe un
    cod care nu scrie nimic); cu defect după ea, nu rămâne nimic.
    """
    from core import coada_api, supervizor

    cl = _client()
    H = {"Authorization": "Bearer " + mediu["token"]}

    def _pune_in_coada(luna):
        with _db.get_conn() as conn:
            r = coada_api.adauga_in_coada(
                conn, mediu["firm"], mediu["tid"], "d300", 2026,
                {"randuri": [], "avertismente": []},
                creat_de=str(mediu["uid"]), creat_de_id=int(mediu["uid"]), luna=luna)
            # verdictul intra odata cu elementul, ca in ruta reala: fara el, aprobarea refuza
            # cu `FARA_VERDICT`, iar proba s-ar opri inainte de frontiera pe care o testeaza.
            coada_api.scrie_verdict(conn, r["coada_id"], {"stare": "valid", "erori": None},
                                    "proba-p4", "<x/>")
        return r.get("coada_id")

    def _stub_poarta(conn, schema, tenant_id, an, luna, confirmari=None,
                     confirmat_de=None, confirmat_de_id=None):
        supervizor.scrie_confirmare(
            conn, tenant_id, an, luna,
            {"tip_constatare": "PROBA_P4", "amprenta": "amprenta_p4"},
            confirmat_de, confirmat_de_id, "motiv de probă P4")
        return []

    monkeypatch.setattr(supervizor, "poarta_confirmarii", _stub_poarta)

    def _confirmari():
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.supervizor_confirmari "
                            " WHERE tenant_id = %s AND tip_constatare = 'PROBA_P4'",
                            (mediu["tid"],))
                return cur.fetchone()[0]

    # --- DIRECȚIA 1: fără defect, confirmarea CHIAR se scrie (proba nu e vacuă)
    cid = _pune_in_coada(6)
    assert cid, "elementul de coadă nu s-a creat — proba ar fi despre altceva"
    r = cl.post("/coada/%d/depune" % cid, headers=H,
                json={"spv_index": "P4-1", "motiv_trecere": "probă P4"})
    assert r.status_code == 200, r.text
    assert _confirmari() == 1, "fără defect, confirmarea trebuie să rămână scrisă"

    # --- DIRECȚIA 2: defect ÎNTRE confirmare și marcarea depunerii
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.supervizor_confirmari WHERE tenant_id = %s",
                        (mediu["tid"],))
    cid2 = _pune_in_coada(7)
    inainte = amprenta(["public.supervizor_confirmari", "public.declaratii_coada",
                        "public.declaratii_depuse"],
                       unde={"public.supervizor_confirmari": ("t.tenant_id = %s", (mediu["tid"],)),
                             "public.declaratii_coada": ("t.tenant_id = %s", (mediu["tid"],)),
                             "public.declaratii_depuse": ("t.tenant_id = %s", (mediu["tid"],))})
    with defect_in(coada_api, "marcheaza_depusa", "P4: defect intre confirmare si depunere"):
        with pytest.raises(RuntimeError):
            cl.post("/coada/%d/depune" % cid2, headers=H,
                    json={"spv_index": "P4-2", "motiv_trecere": "probă P4"})
    dupa = amprenta(["public.supervizor_confirmari", "public.declaratii_coada",
                     "public.declaratii_depuse"],
                    unde={"public.supervizor_confirmari": ("t.tenant_id = %s", (mediu["tid"],)),
                          "public.declaratii_coada": ("t.tenant_id = %s", (mediu["tid"],)),
                          "public.declaratii_depuse": ("t.tenant_id = %s", (mediu["tid"],))})

    assert _confirmari() == 0, (
        "PARTIAL_STATE_AFTER_FAULT: a rămas o confirmare peste o depunere care nu s-a făcut")
    assert dupa == inainte, "starea persistentă s-a mișcat după un defect: %s -> %s" % (
        inainte, dupa)

    # --- DIRECȚIA 3: nu un defect, ci un REFUZ. Aprobarea nu are voie să rămână comisă.
    #
    # Frontiera e alta și merită numită: `auto_aproba_daca_e_cazul` scrie, apoi `marcheaza_depusa`
    # poate REFUZA (`FARA_VERDICT`, `STARE_GRESITA`). Dacă refuzul iese din tranzacție, aprobarea
    # rămâne — iar din `aprobata` elementul nu se mai poate RESPINGE. Exact forma pe care R128 o
    # reparase venind din client.
    cid3 = _pune_in_coada(8)

    def _stare_coada(cid):
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT stare FROM public.declaratii_coada WHERE id = %s", (cid,))
                r = cur.fetchone()
                return r[0] if r else None

    stare_inainte = _stare_coada(cid3)
    monkeypatch.setattr(coada_api, "marcheaza_depusa",
                        lambda *a, **k: {"ok": False, "cod": "FARA_VERDICT",
                                         "mesaj": "refuz injectat P4"})
    r3 = cl.post("/coada/%d/depune" % cid3, headers=H,
                 json={"spv_index": "P4-3", "motiv_trecere": "probă P4"})
    assert r3.status_code == 403, r3.text
    assert _stare_coada(cid3) == stare_inainte, (
        "PARTIAL_STATE_AFTER_FAULT: refuzul marcării a lăsat aprobarea comisă (%s -> %s)"
        % (stare_inainte, _stare_coada(cid3)))


# ============================================================================
#  2. POST /auth/register — contul nu rămâne fără dovada acordului
# ============================================================================

def test_register_contul_nu_ramane_fara_dovada_acordului(monkeypatch):
    """Frontiera probată: **între crearea contului și scrierea dovezii acordului**.

    Defectul se injectează dându-i lui `acord_termeni` un `cabinet_id` inexistent: cheia străină
    refuză, deci scrierea a doua cade — exact scenariul pe care vechea formă îl înghițea într-un
    `print`, lăsând contul în urmă.
    """
    import main

    _curata()
    cl = _client()
    email = "ztest_p4_reg@exemplu.ro"

    def _useri():
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.users WHERE email = %s", (email,))
                return cur.fetchone()[0]

    corp = {"email": email, "parola": "Parola.P4.2026", "nume_cabinet": "ZTEST P4 CABINET REG",
            "nume": "P4", "prenume": "Proba", "accept_termeni": True}

    # Defectul se injectează pe `acord_termeni.versiune`, care e `NOT NULL` — verificat în
    # `acord_termeni_ddl.sql`. Prima formă a probei dădea un `cabinet_id` inexistent și NU
    # producea niciun defect: tabelul n-are cheie străină, deci înregistrarea trecea. *O injecție
    # care nu injectează nimic e o probă care raportează verde despre o lume pe care n-o atinge.*

    inainte = amprenta(["public.users", "public.accounting_firms", "public.acord_termeni"],
                       unde={"public.users": ("t.email = %s", (email,)),
                             "public.accounting_firms": ("t.nume LIKE 'ZTEST P4%%'", ()),
                             "public.acord_termeni": ("t.email = %s", (email,))})

    monkeypatch.setattr(main, "_termeni_versiune", lambda _txt: None)
    try:
        r = cl.post("/auth/register", json=corp)
        assert r.status_code >= 400, "defectul injectat trebuia să oprească înregistrarea"
    except Exception:
        pass                     # o excepție necaptată e tot un eșec al cererii
    monkeypatch.undo()

    dupa = amprenta(["public.users", "public.accounting_firms", "public.acord_termeni"],
                    unde={"public.users": ("t.email = %s", (email,)),
                          "public.accounting_firms": ("t.nume LIKE 'ZTEST P4%%'", ()),
                          "public.acord_termeni": ("t.email = %s", (email,))})
    assert _useri() == 0, (
        "PARTIAL_STATE_AFTER_FAULT: contul a rămas, fără dovada acordului")
    assert dupa == inainte, "starea persistentă s-a mișcat: %s -> %s" % (inainte, dupa)

    # --- DIRECȚIA 2: fără defect, contul ȘI dovada intră amândouă
    r = cl.post("/auth/register", json=corp)
    assert r.status_code == 200, r.text
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.acord_termeni WHERE email = %s", (email,))
            acorduri = cur.fetchone()[0]
    assert _useri() == 1 and acorduri == 1, (
        "fără defect trebuie să existe și contul, și dovada: %s conturi, %s acorduri"
        % (_useri(), acorduri))
    _curata()


# ============================================================================
#  3. POST /tenants/{id}/client-acces — contul nu rămâne fără cheia lui
# ============================================================================

def test_client_acces_contul_nu_ramane_fara_token(mediu, monkeypatch):
    """Frontiera probată: **între crearea contului de client și tokenul de activare**.

    Defectul se injectează în `_pune_token`. Vechea formă scria tokenul într-o a doua tranzacție,
    deci contul rămânea — un utilizator fără nicio cale de intrare, cu urma din portal spunând
    „cabinetul a dat acces".
    """
    import main

    cl = _client()
    H = {"Authorization": "Bearer " + mediu["token"]}
    email = "ztest_p4_client@exemplu.ro"
    monkeypatch.setattr(main._obs, "trimite_email_html", lambda *a, **k: True)

    def _stare():
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.users WHERE email = %s", (email,))
                u = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM public.tokene_activare ta "
                            " JOIN public.users u ON u.id = ta.user_id WHERE u.email = %s",
                            (email,))
                t = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM public.urme_portal WHERE tenant_id = %s",
                            (mediu["tid"],))
                p = cur.fetchone()[0]
        return u, t, p

    inainte = _stare()
    with defect_in(main, "_pune_token", "P4: defect intre cont si tokenul lui"):
        try:
            r = cl.post("/tenants/%d/client-acces" % mediu["tid"], headers=H,
                        json={"email": email, "nume": "Client P4"})
            assert r.status_code >= 400
        except RuntimeError:
            pass
    dupa = _stare()
    assert dupa == inainte == (0, 0, 0) or dupa == inainte, (
        "PARTIAL_STATE_AFTER_FAULT: %s -> %s (cont/token/urmă)" % (inainte, dupa))
    assert dupa[0] == 0, "contul de client a rămas fără tokenul lui — fundătură"

    # --- DIRECȚIA 2: fără defect, contul ȘI tokenul intră amândouă
    r = cl.post("/tenants/%d/client-acces" % mediu["tid"], headers=H,
                json={"email": email, "nume": "Client P4"})
    assert r.status_code == 200, r.text
    u, t, _p = _stare()
    assert (u, t) == (1, 1), "fără defect trebuie să existe și contul, și tokenul: %s/%s" % (u, t)


# ============================================================================
#  4. spv_conector.reimprospateaza_token — tokenul rotit supraviețuiește
# ============================================================================

def test_token_rotit_supravietuieste_esecului_de_dupa(mediu, monkeypatch):
    """Frontiera probată: **după rotația la ANAF, înainte ca apelul care a cerut-o să reușească**.

    ANAF rotește perechea: în secunda răspunsului, vechiul `refresh_token` e mort acolo. Dacă
    perechea nouă trăiește în tranzacția lui `apel_anaf`, o eroare de după o șterge din bază —
    principalul rămâne deconectat, și nimic nu pică, fiindcă apelul eșuează din alt motiv.

    Proba merge pe calea REALĂ (`apel_anaf`), nu pe funcția de rotație luată singură: acolo trăiește
    tranzacția, deci acolo se vede dacă scrierea supraviețuiește. Defectul se injectează în
    `requests.request` — apelul propriu-zis către ANAF, de după refresh.
    """
    from core import spv_conector as SC
    from datetime import datetime, timedelta, timezone

    principal = SC.principal_din_rand(mediu["firm"], None)
    acum = datetime.now(timezone.utc)
    with _db.get_conn() as conn:
        SC.salveaza_token(conn, principal, {
            "serial_certificat": "P4SERIAL",
            "access_token": "acces_vechi_p4", "refresh_token": "refresh_vechi_p4",
            "access_expira": acum - timedelta(minutes=1),      # EXPIRAT: cere refresh
            "refresh_expira": acum + timedelta(days=30)})

    def _valori_noi(_tok, acum=None):
        a = datetime.now(timezone.utc)
        return {"serial_certificat": "P4SERIAL",
                "access_token": "acces_NOU_p4", "refresh_token": "refresh_NOU_p4",
                "access_expira": a + timedelta(hours=1),
                "refresh_expira": a + timedelta(days=30)}

    monkeypatch.setattr(SC, "reimprospateaza_pereche", lambda _rt: {"NOU": True})
    monkeypatch.setattr(SC, "valori_din_raspuns_token", _valori_noi)

    def _cade(*a, **k):
        raise RuntimeError("P4: apelul catre ANAF a cazut DUPA rotatie")

    monkeypatch.setattr(SC.requests, "request", _cade)

    with pytest.raises(RuntimeError):
        SC.apel_anaf(principal, "GET", "https://exemplu.invalid/x", timeout=1)

    with _db.get_conn() as conn:
        dupa = SC.ia_token_activ(conn, principal)
    assert dupa is not None, "tokenul a dispărut cu totul"
    assert dupa["access_token"] == "acces_NOU_p4", (
        "PARTIAL_STATE_AFTER_FAULT: rotația s-a făcut la ANAF, dar baza a rămas cu perechea "
        "veche (%r) — principalul e deconectat și nimic n-o spune" % dupa["access_token"])
    assert dupa["refresh_token"] == "refresh_NOU_p4"

    # --- DIRECȚIA 2: fără defect, apelul merge, iar tokenul e tot cel nou (proba nu e vacuă)
    class _Raspuns:
        status_code = 200
        text = "ok"

    monkeypatch.setattr(SC.requests, "request", lambda *a, **k: _Raspuns())
    r = SC.apel_anaf(principal, "GET", "https://exemplu.invalid/x", timeout=1)
    assert r.status_code == 200
    with _db.get_conn() as conn:
        assert SC.ia_token_activ(conn, principal)["access_token"] == "acces_NOU_p4"


# ============================================================================
#  5. notificari_scadenta — e-mailul nu pleacă de două ori
# ============================================================================

def test_notificare_scadenta_nu_pleaca_de_doua_ori(mediu, monkeypatch):
    """Frontiera probată: **după e-mail, înainte de scrierea rezultatului**.

    Proprietatea cerută e **cel mult o dată**: dacă rezultatul nu se mai poate scrie, pragul tot
    rămâne consumat, iar a doua rulare NU mai trimite. Vechea formă ținea și e-mailul, și rândul
    în aceeași tranzacție deschisă pentru toată firma — deci un eșec de după le despărțea exact
    invers: e-mailul rămânea, rândul nu.
    """
    from core import notificari_scadenta as NS
    from core import observare
    import datetime

    azi = datetime.date(2026, 6, 10)
    scadenta = azi + datetime.timedelta(days=3)
    with _db.get_conn(mediu["schema"]) as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE firma_profil SET notificari_scadenta_activ = true, "
                        " email = 'ztest_p4_firma@exemplu.ro' WHERE id = 1")
            cur.execute("INSERT INTO clienti (nume, email) VALUES ('CLIENT P4','cli@exemplu.ro') "
                        "RETURNING id")
            cid = cur.fetchone()[0]
            cur.execute("INSERT INTO facturi (numar,data_emitere,data_scadenta,directie,client_id,"
                        "tert_cui,tert_nume,total,tva) VALUES ('P4-1',%s,%s,'emisa',%s,"
                        "'RO14399840','CLIENT P4',1210,210) RETURNING id",
                        (azi, scadenta, cid))
            fid = cur.fetchone()[0]

    trimise = []
    monkeypatch.setattr(observare, "trimite_email_html",
                        lambda *a, **k: trimise.append(a[0]) or True)

    # rulare 1: defect DUPĂ e-mail, la scrierea rezultatului
    with defect_in(NS, "_scrie_rezultatul", "P4: defect dupa e-mail"):
        with _db.get_conn(mediu["schema"]) as conn:
            with pytest.raises(RuntimeError):
                NS.emite_pentru_firma(mediu["schema"], azi=azi)
    assert len(trimise) == 1, "e-mailul trebuia să plece o dată: %d" % len(trimise)

    with _db.get_conn(mediu["schema"]) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT prag, stare FROM notificari_scadenta WHERE factura_id = %s", (fid,))
            randuri = cur.fetchall()
    assert len(randuri) == 1, (
        "PARTIAL_STATE_AFTER_FAULT: e-mailul a plecat, iar rândul care îl oprește nu s-a scris — "
        "a doua rulare l-ar trimite din nou")

    # rulare 2: același prag NU se mai trimite
    with _db.get_conn(mediu["schema"]) as conn:
        NS.emite_pentru_firma(mediu["schema"], azi=azi)
    assert len(trimise) == 1, (
        "e-mailul a plecat de două ori pentru același prag: %d trimiteri" % len(trimise))


# ============================================================================
#  6. alerta_acces — rezervarea de dedup se comite înaintea alertei
# ============================================================================

def test_alerta_acces_dedup_se_comite_inainte_de_alerta(mediu):
    """Frontiera probată: **între rezervarea ferestrei de dedup și alerta trimisă**.

    Rezervarea se cheamă din interiorul unei tranzacții a apelantului care apoi CADE. Dacă
    rezervarea ar trăi în ea, s-ar întoarce odată cu ea — iar alerta, deja plecată, ar pleca din
    nou la următoarea rulare a cronului, din 15 în 15 minute.
    """
    from core import alerta_acces as AA

    cheie = "ztest_p4_dedup"
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.alerte_acces_dedup WHERE cheie = %s", (cheie,))

    with pytest.raises(RuntimeError):
        with _db.get_conn() as conn:
            assert AA._poate_trimite(cheie, 15) is True
            raise RuntimeError("P4: defect dupa rezervare, ca la o alerta plecata")

    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM public.alerte_acces_dedup WHERE cheie = %s", (cheie,))
            n = cur.fetchone()[0]
    assert n == 1, (
        "PARTIAL_STATE_AFTER_FAULT: rezervarea de dedup s-a întors odată cu tranzacția "
        "apelantului — alerta ar pleca din nou")

    # a doua cerere, în fereastră, e refuzată: dedup-ul chiar apără
    assert AA._poate_trimite(cheie, 15) is False, "dedup-ul nu apără nimic în fereastră"

    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM public.alerte_acces_dedup WHERE cheie = %s", (cheie,))


# ============================================================================
#  7. facturi/emite — numărul nu se consumă fără factura lui
# ============================================================================

def test_emiterea_facturii_nu_lasa_numar_fara_factura(mediu):
    """Frontiera probată: **înainte de commitul final al emiterii**.

    Actul are patru efecte — factura, liniile ei, numărul din serie, și (când poarta o cere)
    descărcarea de gestiune. Proprietatea cerută: toate patru sau niciunul. Instanța din 04.09
    arată că nu e teoretică: un commit străin în mijlocul actului a lăsat o factură numerotată și
    contată, fără curs.
    """
    from core import facturi_api

    linii = [{"descriere": "Serviciu P4", "cantitate": 1, "pret_unitar": 100,
              "cota_tva": 21}]

    def _stare():
        with _db.get_conn(mediu["schema"]) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM facturi")
                f = cur.fetchone()[0]
                cur.execute("SELECT count(*) FROM factura_linii")
                l = cur.fetchone()[0]
                cur.execute("SELECT urmator_numar_factura FROM firma_profil WHERE id = 1")
                n = cur.fetchone()[0]
        return f, l, n

    inainte = _stare()

    # --- DIRECȚIA 1: defect ÎNAINTE de commitul final
    with pytest.raises(RuntimeError):
        with _db.get_conn(mediu["schema"]) as conn:
            facturi_api.emite_factura(
                conn, linii, tert_nume="CLIENT P4", tert_cui="RO14399840",
                data_emitere="2026-06-10", moneda="RON", platitor_tva=True, tip="factura")
            raise RuntimeError("P4: defect inainte de commitul final al emiterii")

    dupa = _stare()
    assert dupa == inainte, (
        "PARTIAL_STATE_AFTER_FAULT: emiterea a lăsat stare după un defect. "
        "(facturi, linii, urmator_numar): %s -> %s" % (inainte, dupa))

    # --- DIRECȚIA 2: fără defect, actul CHIAR se scrie — altfel proba de mai sus n-ar dovedi nimic
    with _db.get_conn(mediu["schema"]) as conn:
        r = facturi_api.emite_factura(
            conn, linii, tert_nume="CLIENT P4", tert_cui="RO14399840",
            data_emitere="2026-06-10", moneda="RON", platitor_tva=True, tip="factura")
    assert r.get("factura_id"), "emiterea n-a produs factură: proba de mai sus ar fi vacuă (%r)" % r
    final = _stare()
    assert final[0] == inainte[0] + 1 and final[1] > inainte[1] and final[2] > inainte[2], (
        "fără defect trebuie să crească și facturile, și liniile, și numărul: %s -> %s"
        % (inainte, final))
