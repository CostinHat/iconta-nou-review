# -*- coding: utf-8 -*-
"""[d112 asiguratD zero-base] Un certificat de concediu medical caruia ii lipseste un camp
OBLIGATORIU din AsiguratDType (D_1 serie / D_2 numar / D_5 data acordarii / D_6 data inceput /
D_7 data incetare, toate use="required" in anaf_surse/d112_06082026.xsd l.665-671) NU trebuie
sa produca un XML ANAF-invalid (DUK: "D_1: atributul trebuie sa exista"). d112.genereaza refuza
pe gol la radacina cu ValueError care numeste salariatul si campul gol - aceeasi clasa ca
hard-block-ul D_8 si ca D205 cifR.

MUTATIE (probata pe HEAD 6cd0054): inainte de fix campurile goale se OMITEAU (vid nepermis) -
genereaza intorcea XML fara ValueError -> pytest.raises pica. Dupa fix -> ValueError ridicat.
"""
import pytest

from core import db, tenant_provisioning as tp

SCHEMA_T = "ztest_d112_zb"


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture
def schema():
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "platitor_tva, tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                    "(1, 'PROBA SRL', '14399840', 'Str. Test 1', 'Bucuresti', 'B', '6202', true, 'L','Popescu','Ion','ADMINISTRATOR') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume, cui=EXCLUDED.cui")
            yield conn
        finally:
            conn.rollback()


def _seed_salariat(cur):
    cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,"
                "part_time) OVERRIDING SYSTEM VALUE VALUES "
                "(1,'CM','Z','1900101410011','2026-01-01',6000,8,false)")


def _cm(cur, **col):
    """Insereaza un CM cod 01 cu campurile obligatorii date, restul goale (NULL)."""
    baza = {"serie": None, "numar": None, "data_acordare": None,
            "data_inceput": None, "data_sfarsit": None}
    baza.update(col)
    cur.execute(
        "INSERT INTO concedii_medicale (id,salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,"
        "brut_ang,brut_fnuass,baza,media_zilnica,loc_prescriere,serie,numar,data_acordare,"
        "data_inceput,data_sfarsit) OVERRIDING SYSTEM VALUE VALUES "
        "(1,1,2026,6,'01',5,5,0,2000,0,6000,600,1,%(serie)s,%(numar)s,%(data_acordare)s,"
        "%(data_inceput)s,%(data_sfarsit)s)", baza)


@pytest.mark.parametrize("lipsa,eticheta", [
    ("serie", "D_1"),
    ("numar", "D_2"),
    ("data_acordare", "D_5"),
    ("data_inceput", "D_6"),
    ("data_sfarsit", "D_7"),
])
def test_d112_asiguratd_camp_obligatoriu_gol_refuzat(schema, lipsa, eticheta):
    from core import d112
    # certificat complet, cu EXCEPTIA campului testat (ramane NULL)
    plin = {"serie": "AB", "numar": "1", "data_acordare": "2026-06-01",
            "data_inceput": "2026-06-01", "data_sfarsit": "2026-06-05"}
    plin[lipsa] = None
    with schema.cursor() as cur:
        _seed_salariat(cur)
        _cm(cur, **plin)
    with pytest.raises(ValueError) as ei:
        d112.genereaza(schema, SCHEMA_T, 2026, 6)
    msg = str(ei.value)
    assert eticheta in msg, "ValueError trebuie sa numeasca campul obligatoriu %s: %s" % (eticheta, msg)
    assert "1900101410011" in msg, "ValueError trebuie sa numeasca salariatul (CNP): %s" % msg


def test_d112_asiguratd_complet_emite_toate_atributele(schema):
    """Control pozitiv: un certificat cu toate campurile obligatorii completate se emite,
    iar asiguratD poarta EFECTIV D_1..D_7 (garda nu supra-blocheaza)."""
    import re
    from core import d112
    with schema.cursor() as cur:
        _seed_salariat(cur)
        _cm(cur, serie="AB", numar="1", data_acordare="2026-06-01",
            data_inceput="2026-06-01", data_sfarsit="2026-06-05")
    xml, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    m = re.search(r"<asiguratD[^>]*/>", xml)
    assert m, "asiguratD trebuie emis pe un certificat complet"
    d = m.group(0)
    for a in ("D_1", "D_2", "D_5", "D_6", "D_7"):
        assert a + '="' in d, "atributul obligatoriu %s lipseste din asiguratD: %s" % (a, d)
