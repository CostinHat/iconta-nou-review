# -*- coding: utf-8 -*-
"""GARD C7 — generarea TVA-decont (d300/d394/d406) urmeaza periodicitatea EFECTIVA a firmei (tip_decont),
nu cea statica. Pe firma trimestriala, wizardul trimite `trim`; codul vechi valideaza cu periodicitatea
statica (lunar) si ridica "luna invalida: None (astept 1-12)" -> generarea D300/D394/D406 era BLOCATA
pentru toate firmele trimestriale (audit vizual tenant_003, 16.08.2026).

Fix (dispecerul genereaza + valideaza_cerere): periodicitate efectiva la validare + conversie trim->luna
ancora (T1->3, T2->6, T3->9, T4->12; generatoarele sunt ancorate pe luna, agrega trimestrul; DUK R18)."""
import pytest
from core import declaratii_api as da
from core import db as _db, tenant_provisioning as _tp

SCH = "ztest_c7_trim"


# ---------- PUR: valideaza_cerere pe periodicitate efectiva ----------
def test_valideaza_trimestrial_accepta_trim():
    # firma trimestriala -> per_efectiv='trimestrial' -> trim valid, fara "luna invalida"
    er = da.valideaza_cerere("d300", {"an": 2026, "trim": 3}, per_efectiv="trimestrial")
    assert er == [], er

def test_valideaza_trimestrial_cere_trim_nu_luna():
    er = da.valideaza_cerere("d300", {"an": 2026, "luna": 9}, per_efectiv="trimestrial")
    assert any("trimestru" in e for e in er), er   # cere trim, nu accepta bare luna

def test_valideaza_lunar_accepta_luna():
    er = da.valideaza_cerere("d300", {"an": 2026, "luna": 6}, per_efectiv="lunar")
    assert er == [], er

def test_valideaza_static_backward_compat():
    # fara per_efectiv -> periodicitatea statica (d300=lunar) -> cere luna
    er = da.valideaza_cerere("d300", {"an": 2026, "trim": 3})
    assert any("luna" in e for e in er), er


# ---------- DB: genereaza pe firma trimestriala/lunara ----------
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False

def _seed(tip_decont):
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("""INSERT INTO firma_profil
                (id,nume,cui,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,tip_firma,
                 declarant_nume,declarant_prenume,declarant_functie)
                VALUES (1,'ZTEST C7','14399840','Str 1','Buc','B','4711','Banca',
                 'RO49AAAA1B31007593840000',%s,true,'srl','A','B','ADMINISTRATOR')""", (tip_decont,))
        conn.commit()

def _drop():
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_trimestrial_genereaza_pe_luna_ancora():
    _seed("T")
    try:
        with _db.get_conn(SCH) as conn:
            xml, res = da.genereaza(conn, SCH, "d300", {"an": 2026, "trim": 3})   # RED pe vechi: "luna invalida: None"
        assert 'luna="9"' in xml or 'luna="09"' in xml, "T3 -> luna ancora 9 (ultima luna a trimestrului)"
    finally:
        _drop()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_lunar_genereaza_pe_luna():
    _seed("L")
    try:
        with _db.get_conn(SCH) as conn:
            xml, res = da.genereaza(conn, SCH, "d300", {"an": 2026, "luna": 5})
        assert 'luna="5"' in xml or 'luna="05"' in xml
    finally:
        _drop()
