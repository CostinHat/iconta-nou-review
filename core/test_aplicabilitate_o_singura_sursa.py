# -*- coding: utf-8 -*-
"""GARD R94 (06.09.2026) — aplicabilitatea se decide INTR-UN SINGUR LOC, iar poarta o consulta.

CE PAZESTE. Pana azi doua mecanisme raspundeau DIFERIT la aceeasi intrebare «ce datoreaza firma
asta»: ecranul chema `neaplicabile_selector` (forma + vectorul TVA), poarta generatorului chema
`neaplicabile_forma` (doar forma), iar semaforul stia in plus REGIMUL. Masurat pe cele 19 firme cu
`scripts/scan_1b_regimuri.py`: **8 divergente** - D300 si D394 ieseau `valid` pe cele patru firme
NEPLATITOARE de TVA, desi ecranul le declara neaplicabile cu temei (art. 316). Dupa reparatie: **0**.

DOUA DIRECTII DE ESEC, amandoua pazite (METODA §22) - fiindca un instrument care greseste in ambele
directii n-are NICIUN plafon:
  - poarta prea LARGA (se intoarce la `neaplicabile_forma`) -> `test_poarta_refuza_d300_neplatitor`;
  - poarta prea STRAMTA (blocheaza ce firma DATOREAZA) -> `test_poarta_nu_refuza_ce_se_datoreaza`
    si `test_ic_fapt_ajunge_in_poarta`.

Aserturile compara OBIECTE, nu subsiruri (METODA §23): mesajul refuzului se cere EGAL cu mesajul pe
care il da selectorul, nu „contine". Daca cele doua s-ar despica din nou, egalitatea cade - un
`in` n-ar cadea.
"""
import pytest

from core import control_fiscal_api as cf
from core import db as _db, declaratii_api, tenant_provisioning as _tp

_SCHEMA = "test_aplicabilitate_r94"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, regim="micro", platitor_tva=False, ic=False):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,regim_fiscal,"
                "platitor_tva,operatiuni_ic,tip_decont,declarant_nume,declarant_prenume,declarant_functie)"
                " VALUES (1,'PROBA R94 SRL','14399840','Str 1','Buc','B','6202','BCR',"
                "'RO49RNCB0000000000000001',%s,%s,%s,'L','Pop','Ion','administrator')",
                (regim, platitor_tva, ic))


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("fara baza de date")
    with _db.get_conn() as c:
        yield c
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
        c.commit()


# ── SELECTORUL stie regimul ────────────────────────────────────────────────
def test_micro_nu_datoreaza_d101():
    """D101 e declaratia impozitului pe PROFIT; o firma pe micro nu o datoreaza."""
    neap = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": "micro"})
    assert set(neap) >= {"d101"}
    # remediul se NUMESTE: blocajul sta pe o afirmatie de om, deci spune unde se corecteaza
    assert neap["d101"].endswith("corectează Regimul fiscal la Date firmă.")


def test_profit_datoreaza_si_d100_si_d101():
    """ASIMETRIE DELIBERATA, si e masurata: D100 nu e declaratia micro, e «obligatiile de plata la
    bugetul de stat» si poarta codul 103 = impozit pe PROFIT (avansul trimestrial) - vezi
    nomenclatorul din `core/d100.py` si gardul `core/test_d100_profit_baza.py`. Oglinda
    «profit -> D100 neaplicabil» ar fi refuzat o declaratie REALA. Ca semaforul nu i-o cere azi e
    alta restanta (R95), nu un motiv sa o blocam aici."""
    neap = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": "profit"})
    assert set(neap).isdisjoint({"d100", "d101"})


def test_regim_necompletat_nu_blocheaza_nimic():
    """Un gol nu e un raspuns. Regimul necompletat -> semaforul il arata GRI; selectorul tace."""
    for vector in ({"tip_firma": "srl"}, {"tip_firma": "srl", "regim_fiscal": None},
                   {"tip_firma": "srl", "regim_fiscal": "  "}):
        neap = cf.neaplicabile_selector(vector)
        assert set(neap).isdisjoint({"d100", "d101"}), vector


# ── POARTA consulta ACEEASI sursa ca ecranul ───────────────────────────────
def test_poarta_refuza_d300_neplatitor(conn):
    """Directia 1 de esec: poarta care s-ar intoarce la `neaplicabile_forma` ar lasa D300 sa iasa
    `valid` pe o firma neplatitoare - cele 8 divergente masurate. Mesajul se cere EGAL cu al
    selectorului, nu «contine»: daca cele doua se despica din nou, egalitatea cade."""
    with conn.cursor() as cur:
        _setup(cur, regim="micro", platitor_tva=False)
    conn.commit()
    asteptat = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": "micro",
                                         "platitor_tva": False, "operatiuni_ic": False})
    for tip in ("d300", "d394"):
        with pytest.raises(ValueError) as e:
            declaratii_api.genereaza(conn, _SCHEMA, tip, {"an": 2026, "luna": 8})
        assert str(e.value) == asteptat[tip]


def test_poarta_refuza_d101_pe_micro(conn):
    """Regimul ajunge si in poarta, nu doar pe ecran."""
    with conn.cursor() as cur:
        _setup(cur, regim="micro", platitor_tva=True)
    conn.commit()
    with pytest.raises(ValueError) as e:
        declaratii_api.genereaza(conn, _SCHEMA, "d101", {"an": 2025})
    assert str(e.value) == cf.neaplicabile_selector(
        {"tip_firma": "srl", "regim_fiscal": "micro", "platitor_tva": True})["d101"]


def test_poarta_nu_refuza_ce_se_datoreaza(conn):
    """Directia 2 de esec, si e cea periculoasa: o poarta prea STRAMTA refuza o declaratie pe care
    firma o datoreaza. ANTI-VACUUM: daca poarta ar refuza tot, testele de mai sus ar trece degeaba."""
    with conn.cursor() as cur:
        _setup(cur, regim="micro", platitor_tva=True)
    conn.commit()
    neap = cf.neaplicabile_selector({"tip_firma": "srl", "regim_fiscal": "micro",
                                     "platitor_tva": True, "operatiuni_ic": False})
    assert set(neap).isdisjoint({"d300", "d100"})   # un platitor micro le datoreaza pe amandoua
    for tip in ("d300", "d100"):
        try:
            declaratii_api.genereaza(conn, _SCHEMA, tip, {"an": 2026, "luna": 8, "trim": 3})
        except ValueError as e:
            assert str(e) not in neap.values(), "poarta a refuzat %s ca NEAPLICABIL, desi se datoreaza" % tip


def test_ic_fapt_ajunge_in_poarta(conn):
    """FAPTUL BATE VECTORUL si in poarta - probat cu un fapt REAL in baza, nu citind sursa functiei.

    Prima forma a acestui test citea `inspect.getsource(genereaza)` si cerea sa apara acolo numele
    `ic_fapt`. Clichetul `apare_oricum` a respins-o, si pe drept: un nume de functie e prezent si in
    lumea in care sonda NU se cheama niciodata. Aici se pune in baza o achizitie intracomunitara
    adevarata (partener UE), peste un vector care declara ca firma NU are operatiuni IC - tiparul
    `tenant_006`. Daca poarta n-ar trece `ic_fapt` mai departe, D390 ar fi REFUZAT, si contabilul
    n-ar putea depune o obligatie pe care firma o ARE."""
    with conn.cursor() as cur:
        _setup(cur, regim="micro", platitor_tva=True, ic=False)
        cur.execute("INSERT INTO facturi (numar,directie,data_emitere,total,tva,tert_nume,tert_cui) "
                    "VALUES ('IC-1','primita','2026-05-04',1000,0,'Fornitore UE','DE811907980')")
    conn.commit()

    # perechea de referinta: pe vector singur, D390 se blocheaza; pe fapt, nu
    fara = cf.neaplicabile_selector({"tip_firma": "srl", "platitor_tva": True,
                                     "operatiuni_ic": False}, ic_fapt=lambda: False)
    cu = cf.neaplicabile_selector({"tip_firma": "srl", "platitor_tva": True,
                                   "operatiuni_ic": False}, ic_fapt=lambda: True)
    assert set(fara) - set(cu) == {"d390"}      # exact una se stinge pe fapt, si e cea asteptata

    # sonda vede faptul pus mai sus...
    assert cf.ic_fapt_din_db(conn, _SCHEMA, 2026) is True
    # ...si poarta NU mai refuza D390 ca neaplicabil
    try:
        declaratii_api.genereaza(conn, _SCHEMA, "d390", {"an": 2026, "luna": 5})
    except ValueError as e:
        assert str(e) != fara["d390"], "poarta a blocat D390 pe bifa, desi faptul o contrazice"
