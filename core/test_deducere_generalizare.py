# -*- coding: utf-8 -*-
"""GARD Fix 3 (Task 2 D112): GENERALIZAREA clasei fix 1 (deducere necablata) la CEILALTI apelanti de productie
ai calcul_salariu gasiti prin §8:
  - adeverinta.date_auto: net-ul de pe adeverinta trebuie sa reflecte deducerea suplimentara (tanar<26 -> net mai
    mare decat un matur cu acelasi brut);
  - salarii_contare.note_lunare: impozitul din notele contabile trebuie sa COINCIDA cu D112 (control_coerenta gol),
    altfel contabilitatea declara alt impozit decat declaratia. RED pre-fix: contarea omitea sub_26/copii.
Aserturi ASCII.
"""
import pytest
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_ded_generalizare"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _setup(cur, salariati):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,"
                "declarant_nume,declarant_prenume,declarant_functie,patron_nume) VALUES (1,'PROBA SRL','14399840',"
                "'Str 1','Buc','B','6202',true,'L','Pop','Ion','administrator','Pop Ion')")
    ids = {}
    for s in salariati:
        cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa,cor,"
                    "data_nastere,copii_scolarizati,declaratie_copii,tip_asigurat) VALUES "
                    "(%(cnp)s,%(nume)s,'X','2024-01-01',5000,8,'B','251401',%(dn)s,%(copii)s,%(decl)s,'1') "
                    "RETURNING id", s)
        ids[s["nume"]] = cur.fetchone()[0]
    return ids


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_adeverinta_net_reflecta_deducerea_suplimentara(conn):
    """Adeverinta: tanar<26 are net MAI MARE decat matur (acelasi brut) - deducerea reduce impozitul -> net mai
    mare. RED pre-fix: date_auto chema calcul_salariu fara sub_26 -> acelasi net."""
    from core import adeverinta
    with conn.cursor() as cur:
        ids = _setup(cur, [
            {"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False},
            {"cnp": "1800101410013", "nume": "MATUR", "dn": "1980-06-01", "copii": 0, "decl": False},
        ])
    conn.commit()
    a_tanar = adeverinta.date_auto(conn, _SCHEMA, ids["TANAR"], 2026, 6)
    a_matur = adeverinta.date_auto(conn, _SCHEMA, ids["MATUR"], 2026, 6)
    assert a_tanar and a_matur, "date_auto a intors None"
    assert a_tanar["net"] > a_matur["net"], (
        "tanar<26 trebuie net mai mare pe adeverinta (deducere suplimentara); got %s vs %s" % (
            a_tanar["net"], a_matur["net"]))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_note_contabile_coerente_cu_d112_pe_deducere(conn):
    """salarii_contare: notele contabile pe un tanar<26 trebuie coerente cu D112 (control_coerenta gol). RED
    pre-fix: contarea omitea sub_26 -> impozit contabil > D112 -> divergenta pe contul de impozit (444)."""
    from core import salarii_contare
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False}])
    conn.commit()
    note, _n = salarii_contare.note_lunare(conn, _SCHEMA, 2026, 6)
    div = salarii_contare.control_coerenta(note, conn, _SCHEMA, 2026, 6)
    assert div == [], "note contabile divergente de D112 (deducere necablata in contare): %s" % div
