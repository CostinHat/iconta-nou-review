# -*- coding: utf-8 -*-
"""GARD D112 (16.08.2026, Task 2 exhaustiv) — DEDUCEREA PERSONALA SUPLIMENTARA cablata.

CF art.77 alin.(10): (a) 15% x salariu minim pentru tineri SUB 26 de ani (venit <= sm+2000); (b) 100 lei/luna
pentru fiecare copil <=18 ani inscris in invatamant, pe baza DECLARATIEI parintelui (alin.12-13). Formula exista
in salarizare.deducere_personala DAR era NECABLATA: niciun apelant de productie trecea sub_26/copii_scoala ->
impozit SUPRA-declarat pt tineri si parinti. FIX: coloane noi salariati (data_nastere/copii_scolarizati/
declaratie_copii) + d112.pull + stat_plata_api paseaza deducerea (sub_26 derivat din data_nastere).

Aserturi ASCII.
"""
import pytest
from core import d112, db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d112_ded_supl"


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
                "declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'PROBA SRL','14399840','Str 1',"
                "'Buc','B','6202',true,'L','Pop','Ion','administrator')")
    for s in salariati:
        cur.execute("INSERT INTO salariati (cnp,nume,prenume,data_angajare,salariu_brut,ore_zi,judet_casa,cor,"
                    "data_nastere,copii_scolarizati,declaratie_copii,tip_asigurat) VALUES "
                    "(%(cnp)s,%(nume)s,'X','2024-01-01',5000,8,'B','251401',%(dn)s,%(copii)s,%(decl)s,'1')", s)


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_deducere_suplimentara_cablata_pull(conn):
    """Pull: TANAR (<26) are deducere MAI MARE + impozit MAI MIC decat MATUR; PARINTE cu copii+declaratie
    are deducere +200 (2x100); PARINTE cu copii FARA declaratie NU primeste (gate) si NU ridica eroare.
    RED pre-fix: sub_26/copii necablate -> toti aveau aceeasi deducere de baza."""
    with conn.cursor() as cur:
        _setup(cur, [
            {"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False},
            {"cnp": "1800101410011", "nume": "MATUR", "dn": "1980-06-01", "copii": 0, "decl": False},
            {"cnp": "1800202410011", "nume": "PARINTE_DA", "dn": "1980-06-01", "copii": 2, "decl": True},
            {"cnp": "1800303410011", "nume": "PARINTE_NU", "dn": "1980-06-01", "copii": 2, "decl": False},
        ])
    conn.commit()
    _prof, sal = d112.pull(conn, _SCHEMA, 2026, 6)
    d = {s["nume"]: s for s in sal}
    # tineri <26: deducere mai mare, impozit mai mic
    assert d["TANAR"]["deducere"] > d["MATUR"]["deducere"], "tanar <26 trebuie sa aiba deducere suplimentara"
    assert d["TANAR"]["impozit"] < d["MATUR"]["impozit"], "tanar <26 -> impozit mai mic (deducere mai mare)"
    # copii scolarizati + declaratie: +200 (2 copii x 100)
    assert d["PARINTE_DA"]["deducere"] == d["MATUR"]["deducere"] + 200, (
        "2 copii scolarizati cu declaratie -> +200 deducere; got %s vs %s" % (
            d["PARINTE_DA"]["deducere"], d["MATUR"]["deducere"]))
    # copii FARA declaratie: nu se acorda (gate), aceeasi deducere ca MATUR, fara eroare
    assert d["PARINTE_NU"]["deducere"] == d["MATUR"]["deducere"], (
        "copii fara declaratie -> deducerea de 100 lei NU se acorda (art.77 alin.12-13)")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_tanar_sub26_diferenta_e_15pct_salariu_minim(conn):
    """Diferenta de deducere TANAR-MATUR = 15%% x salariu minim al lunii (rotunjit)."""
    from core.common import cota
    from datetime import date
    with conn.cursor() as cur:
        _setup(cur, [
            {"cnp": "5000101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False},
            {"cnp": "1800101410011", "nume": "MATUR", "dn": "1980-06-01", "copii": 0, "decl": False},
        ])
    conn.commit()
    _prof, sal = d112.pull(conn, _SCHEMA, 2026, 6)
    d = {s["nume"]: s for s in sal}
    sm = float(cota("salariu_minim", date(2026, 6, 1))[0])
    dif = d["TANAR"]["deducere"] - d["MATUR"]["deducere"]
    assert abs(dif - round(0.15 * sm)) <= 1, "diferenta %s ~ 15%% x sm %s = %s" % (dif, sm, round(0.15 * sm))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d112_cu_deducere_suplimentara_duk_valid(conn):
    """Proba DUK: D112 cu un tanar <26 (deducere suplimentara aplicata) e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    with conn.cursor() as cur:
        _setup(cur, [{"cnp": "1900101410011", "nume": "TANAR", "dn": "2002-06-01", "copii": 0, "decl": False}])
    conn.commit()
    xml = d112.genereaza(conn, _SCHEMA, 2026, 6)[0]
    rez = duk.valideaza(xml, "d112", an=2026, luna=6)
    assert rez["stare"] == "valid", "D112 cu deducere suplimentara trebuie DUK-valid; rez=%r" % rez
