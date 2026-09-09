# -*- coding: utf-8 -*-
"""GARD P3 · VALUL A — cele două rute set-based nu mai cresc cu numărul de firme.

**CE PAZEȘTE, și de ce fiecare rând e aici:**

  COSTUL NU CREȘTE CU N     `/migrare/istoric-declaratii` și `/supervizor` fac același număr de
      interogări **și** de conexiuni la 5 firme și la 50. Măsurat prin cererea HTTP întreagă, nu
      prin funcția izolată — O(N)-ul reparat aici stătea tocmai în dependențele rutei.
  ACELEAȘI VALORI           `rezumat_lot` întoarce, firmă cu firmă, exact ce întorcea `rezumat`
      chemată în buclă. *Un lot mai rapid care răspunde altceva nu e o optimizare, e un defect.*
  ECHIVALENȚA E PROBATĂ, NU CREZUTĂ   `/supervizor` nu mai cheamă `schema_tenant` per firmă,
      fiindcă `tenantii_userului` filtrează pe aceleași reguli și întoarce deja `schema_name`.
      Afirmația aia e scrisă în cod ca justificare — deci trebuie să aibă o probă care o verifică
      pe portofoliul real, firmă cu firmă.
  NIMIC NU S-A MUTAT ÎN CACHE   ambele rute citesc aceleași surse, la fel de proaspăt. Nu există
      model de citire, deci nu există stare de prospețime de gardat aici.

**Aserțiuni anti-vacuu peste tot:** o listă goală de firme ar face toate probele să treacă verde
despre o lume pe care n-o văd.
"""
import os
import sys

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
sys.path.insert(0, os.path.join(_RAD, "scripts"))

from core import auth_api  # noqa: E402
from core import db as _db  # noqa: E402
from core import istoric_declaratii_import_api as IST  # noqa: E402

RUTE = ("/migrare/istoric-declaratii", "/supervizor")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture(scope="module")
def cabinet_real():
    """Cabinetul real cu cele mai multe firme, și tokenul lui."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import psycopg2.extras as _E
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT u.id, count(t.id) FROM public.users u "
                        "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                        " WHERE u.rol = 'admin_firma' AND u.activ AND t.activ "
                        "   AND t.schema_name LIKE 'tenant_%' "
                        " GROUP BY u.id ORDER BY 2 DESC LIMIT 1")
            r = cur.fetchone()
        if not r or r[1] < 2:
            pytest.skip("niciun cabinet real cu cel puțin două firme")
        uid, cate = r
        with c.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute("SELECT id, rol, accounting_firm_id FROM public.users WHERE id = %s", (uid,))
            u = dict(cur.fetchone())
    return uid, cate, auth_api.emite_token(u)


# ============================================================================
#  COSTUL NU CREȘTE CU N
# ============================================================================
@pytest.mark.parametrize("ruta", RUTE)
def test_costul_nu_creste_cu_numarul_de_firme(ruta):
    """5 firme vs 50, prin cererea HTTP întreagă: același număr de interogări ȘI de conexiuni.

    Criteriul e **panta**, nu un prag absolut: un total mai mare decât plafonul pool-ului n-ar fi
    în sine un defect, fiindcă pool-ul servește secvențial. Ce nu are voie e să crească cu N."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    import masoara_p3 as MP
    import masoara_rute_portofoliu as MR

    ok, _ = MR.calibreaza(verbose=False)
    assert ok, "hamul HTTP nu e calibrat — nicio cifră de mai jos n-ar valora nimic"

    masurat = {}
    try:
        for n in (5, 50):
            with _db.get_conn() as conn:
                MR.curata(conn)
                conn.commit()
            with _db.get_conn() as conn:
                uid, _ids = MR.construieste(conn, n, procent_invalidat=10, rece=False)
                tok = MR._token(conn, uid)
            with MR.client_test() as cl:
                cl.get(ruta, headers={"Authorization": "Bearer " + tok})   # încălzire
                masurat[n] = MP.masoara_ruta(cl, tok, ruta)
    finally:
        with _db.get_conn() as conn:
            MR.curata(conn)
            conn.commit()

    a, b = masurat[5], masurat[50]
    assert a["status"] == b["status"] == 200, (a.get("corp"), b.get("corp"))
    assert a["interogari"] > 0, "contorul n-a văzut nimic — proba n-ar putea eșua"
    assert a["interogari"] == b["interogari"], (
        "%s: %d interogări la 5 firme, %d la 50 — costul crește cu N"
        % (ruta, a["interogari"], b["interogari"]))
    assert a["conexiuni"] == b["conexiuni"], (
        "%s: %d conexiuni la 5 firme, %d la 50 — costul crește cu N"
        % (ruta, a["conexiuni"], b["conexiuni"]))


# ============================================================================
#  ACELEAȘI VALORI CA ÎNAINTE
# ============================================================================
def test_rezumat_lot_da_aceleasi_valori_ca_rezumat_per_firma(cabinet_real):
    """Lotul întoarce, firmă cu firmă, exact ce întorcea funcția chemată în buclă.

    `rezumat()` NU s-a atins — o cheamă ecranele unei singure firme —, deci se poate folosi drept
    martor: e chiar codul de dinaintea reparației."""
    uid, _cate, _tok = cabinet_real
    with _db.get_conn() as c:
        firme = auth_api.tenantii_userului(c, uid)
        ids = [f["id"] for f in firme]
        lot = IST.rezumat_lot(c, ids)
        unul_cate_unul = {t: IST.rezumat(c, t) for t in ids}
    assert ids, "portofoliu gol — proba n-ar putea eșua"
    assert set(lot) == set(unul_cate_unul)
    assert lot == unul_cate_unul, (
        "lotul diferă de bucla martor: %s"
        % {t: (lot[t], unul_cate_unul[t]) for t in ids if lot[t] != unul_cate_unul[t]})


def test_rezumat_lot_declara_si_firmele_fara_istoric(cabinet_real):
    """O firmă fără niciun rând primește `0`, nu lipsește din rezultat. *Absența se declară.*"""
    uid, _cate, _tok = cabinet_real
    with _db.get_conn() as c:
        ids = [f["id"] for f in auth_api.tenantii_userului(c, uid)]
        lot = IST.rezumat_lot(c, ids)
    assert set(lot) == set(ids), "firme lipsă din rezultatul lotului: %s" % (set(ids) - set(lot))
    for t in ids:
        assert lot[t]["randuri"] >= 0 and isinstance(lot[t]["are_istoric"], bool)


def test_rezumat_lot_pe_lista_goala():
    """Fără firme, fără interogare — și fără excepție."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        assert IST.rezumat_lot(c, []) == {}
        assert IST.rezumat_lot(c, None) == {}


# ============================================================================
#  ECHIVALENȚA PE CARE SE SPRIJINĂ /supervizor — PROBATĂ
# ============================================================================
def test_schema_din_lista_e_aceeasi_cu_cea_verificata_per_firma(cabinet_real):
    """`/supervizor` nu mai cheamă `schema_tenant` per firmă. Proba că avea voie.

    Pentru FIECARE firmă întoarsă de `tenantii_userului`, `schema_tenant` (calea veche, neatinsă)
    trebuie să dea exact același `schema_name`. Dacă vreodată regulile de acces ale celor două
    diverg, garda asta cade — și cade ÎNAINTE ca o firmă să apară pe un ecran unde n-avea acces."""
    uid, _cate, _tok = cabinet_real
    with _db.get_conn() as c:
        firme = auth_api.tenantii_userului(c, uid)
        assert firme, "portofoliu gol — proba n-ar putea eșua"
        nepotriviri = []
        for f in firme:
            pe_calea_veche = auth_api.schema_tenant(c, uid, f["id"])
            if pe_calea_veche != f.get("schema_name"):
                nepotriviri.append((f["id"], f.get("schema_name"), pe_calea_veche))
    assert not nepotriviri, (
        "lista portofoliului și verificarea per firmă nu mai sunt de acord: %s\n"
        "`/supervizor` se sprijină pe faptul că sunt." % nepotriviri)


def test_toate_cele_trei_roluri_primesc_schema_name():
    """**Orbirea primei forme a acestui gard, închisă.**

    Proba de mai sus compară cele două căi pe portofoliul REAL — dar portofoliul real pe care l-am
    ales e al unui `admin_firma`. `tenantii_userului` are TREI ramuri de SQL, una per rol, iar o
    ramură care ar uita `t.schema_name` ar face `/supervizor` să sară tăcut peste toate firmele
    rolului aceluia. *Am ales un rol și am numit rezultatul „portofoliul real"; punctul orb nu era
    firma, era rolul.*

    Aici se execută **toate trei**, pe date construite anume, într-o tranzacție care se dă înapoi:
      * `superadmin`   -> firme FĂRĂ cabinet;
      * `admin_firma`  -> firmele cabinetului lui;
      * alt rol        -> doar cele legate prin `user_tenants`.

    Nu se citește SQL-ul și nu se caută niciun șir în el (METODA §23): se cheamă funcția și se
    cere rândului cheia. **`ROLLBACK` la final** — un gard care măsoară pe baza de producție n-are
    voie să lase nimic în urmă, iar clichetul de orfani chiar asta păzește."""
    if not _db_ok():
        pytest.skip("fara baza de date")
    vazute = {}
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("INSERT INTO public.accounting_firms (nume) VALUES (%s) RETURNING id",
                            ("ZTEST cabinet roluri P3",))
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) "
                            "VALUES (%s, %s, %s) RETURNING id",
                            ("ztest_rol_cabinet", "ZTEST firma de cabinet", fid))
                t_cab = cur.fetchone()[0]
                cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id) "
                            "VALUES (%s, %s, NULL) RETURNING id",
                            ("ztest_rol_liber", "ZTEST firma fara cabinet"))
                t_lib = cur.fetchone()[0]
                useri = {}
                for rol, firma in (("superadmin", None), ("admin_firma", fid), ("angajat", fid)):
                    cur.execute("INSERT INTO public.users (email, password_hash, rol, "
                                "accounting_firm_id) VALUES (%s, %s, %s, %s) RETURNING id",
                                ("ztest_%s@p3.local" % rol, "x", rol, firma))
                    useri[rol] = cur.fetchone()[0]
                cur.execute("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s)",
                            (useri["angajat"], t_cab))

            asteptat = {"superadmin": t_lib, "admin_firma": t_cab, "angajat": t_cab}
            for rol, uid in useri.items():
                firme = auth_api.tenantii_userului(c, uid)
                vazute[rol] = [f.get("id") for f in firme]
                assert asteptat[rol] in vazute[rol], (
                    "[anti-vacuu] ramura %r n-a întors firma construită pentru ea — proba n-ar "
                    "măsura nimic despre ramura asta" % rol)
                # Nu într-o buclă: o buclă peste o listă goală n-asertează nimic, iar premisa
                # care ar salva-o e cu trei rânduri mai sus. Se calculează MULȚIMILE și se cere
                # să fie goale — premisa stă lângă aserțiune, unde se poate citi.
                fara_cheie = [f.get("id") for f in firme if "schema_name" not in f]
                cu_valoare_goala = [f.get("id") for f in firme if not f.get("schema_name")]
                assert firme, "[anti-vacuu] ramura %r n-a întors nicio firmă" % rol
                assert not fara_cheie, (
                    "ramura de rol %r nu întoarce deloc cheia `schema_name` pentru firmele %s — "
                    "`/supervizor` ar sări tăcut peste toate firmele rolului ăstuia"
                    % (rol, fara_cheie))
                assert not cu_valoare_goala, (
                    "ramura de rol %r a întors `schema_name` gol pentru firmele %s"
                    % (rol, cu_valoare_goala))
        finally:
            c.rollback()

    assert set(vazute) == {"superadmin", "admin_firma", "angajat"}, (
        "n-au fost exercitate toate trei ramurile: %s" % sorted(vazute))
    assert t_lib not in vazute["admin_firma"], (
        "ramura `admin_firma` a întors o firmă fără cabinet — filtrul ei nu mai e cel pe care se "
        "sprijină `/supervizor`")


def test_o_firma_a_ALTUI_cabinet_nu_intra_in_lista(cabinet_real):
    """Direcția a doua: echivalența de mai sus n-ar valora nimic dacă lista ar fi permisivă.

    O firmă a altui cabinet nu apare în `tenantii_userului` **și** `schema_tenant` o refuză."""
    uid, _cate, _tok = cabinet_real
    with _db.get_conn() as c:
        ale_mele = {f["id"] for f in auth_api.tenantii_userului(c, uid)}
        with c.cursor() as cur:
            cur.execute("SELECT id FROM public.tenants WHERE activ AND id <> ALL(%s) LIMIT 1",
                        (list(ale_mele) or [0],))
            r = cur.fetchone()
        if not r:
            pytest.skip("nicio firmă din afara portofoliului — proba n-ar discrimina nimic")
        strain = r[0]
        assert strain not in ale_mele
        assert auth_api.schema_tenant(c, uid, strain) is None, (
            "firma %s nu e în portofoliu, dar `schema_tenant` i-ar da schema" % strain)
