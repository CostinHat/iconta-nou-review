# -*- coding: utf-8 -*-
"""Teste gardian pentru D205 - REFACUT A DOUA OARA 16.07.2026.

Prima incercare avea trei greseli, gasite toate prin validatorul oficial:
1. Atributele reale ale <benef> nu erau cele extrase dintr-un grep ingust pe
   binar: den1 (nu nume1), cifR (nu cif), Rezid cu majuscula, tip_venit1 pe
   FIECARE beneficiar (nu doar pe sect_II), id_inreg (secvential).
2. tip_venit pentru dividende e "08" (confirmat: "08 1.a) venituri din
   dividende"), NU "25" - la 08 se completeaza divid_D/divid_P, la 25
   baza1/imp1 sunt INTERZISE (regulile R44/R45).
3. Tcastig/Tpierd/T_VB/T_GAR se calculeaza STRICT pe tip_venit1 corespunzator
   (25 si 29) - la tip_venit=08 raman 0, nu se calculeaza din divid_D/divid_P.
4. totalPlata_A = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+
   suma(T_GAR)+suma(Tbaza)+suma(Timp) - suma pe TOATE campurile din sect_II,
   nu doar Timp.
"""
import pytest
from core.d205 import calcul_d205, build_xml


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA", "adresa": "X"}


def test_dividende_valid():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "POPESCU Ion", "cif": "1850101450013",
         "baza": 10000, "imp": 1000, "castig": 10000}])
    xml = build_xml(res)
    assert 'tip_venit="08"' in xml
    assert 'divid_D="10000"' in xml


def test_tcastig_ramane_zero_la_dividende():
    """Regresie: Tcastig=10000 (calculat din divid_D) era gresit - regula
    oficiala il calculeaza doar din beneficiari cu tip_venit1=25."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013",
         "baza": 5000, "imp": 500, "castig": 5000}])
    xml = build_xml(res)
    assert 'Tcastig="0"' in xml
    assert 'Tpierd="0"' in xml


def test_totalPlata_A_e_suma_tuturor_campurilor_sect_II():
    """Regresie: totalPlata_A=Timp era gresit. Formula reala include si nrben,
    Tbaza (T_VB/T_GAR/Tcastig/Tpierd raman 0 la dividende)."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013",
         "baza": 10000, "imp": 1000, "castig": 10000}])
    xml = build_xml(res)
    # nrben(1) + Tcastig(0) + Tpierd(0) + T_VB(0) + T_GAR(0) + Tbaza(10000) + Timp(1000)
    assert 'totalPlata_A="11001"' in xml


def test_id_inreg_e_secvential():
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "A", "cif": "1850101450013", "baza": 100, "imp": 10, "castig": 100},
        {"categ": "1.a", "nume": "B", "cif": "1850101450013", "baza": 200, "imp": 20, "castig": 200},
    ])
    xml = build_xml(res)
    assert 'id_inreg="1"' in xml
    assert 'id_inreg="2"' in xml


def test_atributele_reale_pe_benef():
    """Regresie: den1 (nu nume1), cifR (nu cif), Rezid majuscula (nu rezid),
    tip_venit1 pe fiecare beneficiar. 'categ' nu e atribut valid - omis."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013", "baza": 100, "imp": 10, "castig": 100}])
    xml = build_xml(res)
    linie = [l for l in xml.split("\n") if "<benef" in l][0]
    assert "den1=" in linie and "nume1=" not in linie
    assert "cifR=" in linie and 'cif="' not in linie
    assert "Rezid=" in linie
    assert "tip_venit1=" in linie
    assert "categ=" not in linie


# ── CONTRACT UNIFORM A1 (modul 7/10, C3, 31.07.2026) — proba pana la declaratie ──
# genereaza(conn, schema, perioada, manual) prin pull() -> calcul_d205 -> build_xml -> DUK valid.
# N/A temei fiscal (schimbare de tooling: uniformizare contract, comportament identic).
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk, d205 as _d205

_SCHEMA_D205 = "ztest_d205_contract"
_D205_DUK = _duk.poate_valida("d205")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_schema_div():
    """Schema temporara, firma_profil completa + 1 asociat (cota 100%, CNP valid) + o nota
    validata cu 50000 dividende distribuite (cont debit 457) in 2026. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_D205)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_D205))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_D205)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','real',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET nume=EXCLUDED.nume")
                cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('ASOCIAT UNU','1900101410011',100)")
                cur.execute("INSERT INTO inregistrari (data, status, sursa) "
                            "VALUES ('2026-04-10','validata','test') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'457','5121',50000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d205_contract_pull_genereaza_perioada(conn_schema_div):
    """C3 contract uniform: genereaza(conn, schema, Perioada(an), manual) prin pull().
    Dividende 50000, asociat 100%% -> parte 50000, impozit 10%% = 5000 (total_plata_a)."""
    xml, res = _d205.genereaza(conn_schema_div, _SCHEMA_D205, Perioada(2026))
    assert res.an == 2026
    assert len(res.beneficiari) == 1, "un beneficiar (asociatul cu cota>0)"
    b = res.beneficiari[0]
    assert b.baza1 == 50000 and b.imp1 == 5000, (
        "50000 dividende, impozit 10%% = 5000; got baza=%s imp=%s" % (b.baza1, b.imp1))
    assert res.total_plata_a == 5000


@pytest.mark.skipif(not _db_ok() or not _D205_DUK, reason="DB sau DUK d205 indisponibil")
def test_d205_contract_proba_duk_valid(conn_schema_div):
    """Proba pana la declaratie: D205 generat prin contractul uniform trece validatorul OFICIAL DUK."""
    xml, res = _d205.genereaza(conn_schema_div, _SCHEMA_D205, Perioada(2026))
    rez = _duk.valideaza(xml, "d205", an=2026)
    assert rez["stare"] == "valid", "DUK a respins D205: %s" % rez
