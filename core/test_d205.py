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


def test_total_plata_a_res_egal_checksum_emis():
    """Gard clasa-d100 (capcana latenta): res.total_plata_a (sursa unica) trebuie sa fie
    checksum-ul EMIS in XML == nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp (formula ANAF
    D205, OPANAF 102/2025). Inainte de aliniere res tinea DOAR Timp - un cross-check pe
    res.total_plata_a al d205 ar fi primit Timp, nu checksum-ul (exact bug-ul d100 R11b)."""
    res = calcul_d205(_prof(), 2025, [
        {"categ": "1.a", "nume": "X", "cif": "1850101450013",
         "baza": 50000, "imp": 8000, "castig": 50000}])
    xml = build_xml(res)
    # nrben(1)+Tcastig(0)+Tpierd(0)+T_VB(0)+T_GAR(0)+Tbaza(50000)+Timp(8000) = 58001
    assert res.total_plata_a == 58001
    # header totalPlata_A emis == res.total_plata_a (sursa unica)
    assert ('totalPlata_A="%d"' % res.total_plata_a) in xml
    # si == suma componentelor sect_II parsate din XML (leaga header de continut, nu doar de res)
    import re as _re
    sec = dict(_re.findall(r'(nrben|Tcastig|Tpierd|T_VB|T_GAR|Tbaza|Timp)="(-?\d+)"', xml))
    assert sum(int(sec[k]) for k in ('nrben','Tcastig','Tpierd','T_VB','T_GAR','Tbaza','Timp')) == res.total_plata_a


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
    Dividende 50000 platite in 2026, asociat 100%% -> parte 50000, impozit pe dividende 16%% = 8000
    (Legea 141/2025, CF art.97: "cota de impozit de 16%% asupra dividendului brut" de la 01.01.2026;
    era 10%% pana in 2025). impozit b.imp1 = 8000; res.total_plata_a = checksum = 58001. Rata rutata
    prin cota("impozit_dividend"), period-aware."""
    xml, res = _d205.genereaza(conn_schema_div, _SCHEMA_D205, Perioada(2026))
    assert res.an == 2026
    assert len(res.beneficiari) == 1, "un beneficiar (asociatul cu cota>0)"
    b = res.beneficiari[0]
    assert b.baza1 == 50000 and b.imp1 == 8000, (
        "50000 dividende platite 2026, impozit 16%% (Legea 141/2025) = 8000; got baza=%s imp=%s" % (b.baza1, b.imp1))
    # res.total_plata_a e CHECKSUM-ul (nrben+Tbaza+Timp = 1+50000+8000), nu Timp singur -
    # aliniat la totalPlata_A emis (sursa unica, clasa d100). Taxa (8000) e verificata via b.imp1.
    assert res.total_plata_a == 58001


@pytest.mark.skipif(not _db_ok() or not _D205_DUK, reason="DB sau DUK d205 indisponibil")
def test_d205_contract_proba_duk_valid(conn_schema_div):
    """Proba pana la declaratie: D205 generat prin contractul uniform trece validatorul OFICIAL DUK."""
    xml, res = _d205.genereaza(conn_schema_div, _SCHEMA_D205, Perioada(2026))
    rez = _duk.valideaza(xml, "d205", an=2026)
    assert rez["stare"] == "valid", "DUK a respins D205: %s" % rez


# ============================================================
#  Impozit pe dividende PERIOD-AWARE in D205 (cluster sect_II tip_venit / impozit retinut).
#  Rata NU mai e hardcodata 10% - vine din cota("impozit_dividend"): 10% pana in 2025,
#  16% de la 01.01.2026 (Legea 141/2025, CF art.97: "cota de impozit de 16% asupra
#  dividendului brut platit unei persoane fizice/juridice romane").
# ============================================================
def test_impozit_dividend_period_aware_cf_art97():
    from decimal import Decimal
    from datetime import date
    from core.common import cota
    # 2026: 16% (Legea 141/2025). 2025: 8% (OG 16/2022). Proba de valoare pe 50000 dividende:
    assert cota("impozit_dividend", date(2026, 12, 31))[0] == Decimal("0.16")   # CF art.97 / Legea 141/2025
    assert cota("impozit_dividend", date(2025, 12, 31))[0] == Decimal("0.08")   # OG 16/2022 (2023-2025)
    assert Decimal(50000) * cota("impozit_dividend", date(2026, 12, 31))[0] == Decimal("8000")
    assert Decimal(50000) * cota("impozit_dividend", date(2025, 12, 31))[0] == Decimal("4000")


def test_d205_rata_dividend_din_cota_nu_hardcodat():
    # GARD anti-regresie: genereaza NU mai calculeaza impozitul cu 10% literal - foloseste
    # cota("impozit_dividend"). Daca cineva rescrie Decimal("10")/Decimal(100), pica aici.
    import inspect
    from core import d205
    src = inspect.getsource(d205.genereaza)
    assert 'Decimal("10") / Decimal(100)' not in src, "rata dividend hardcodata reintrodusa"
    assert 'cota("impozit_dividend"' in src or '_cota205("impozit_dividend"' in src


# ============================================================
#  Rotunjire D205 (cluster rotunjire | d205): sumele fiscale (baza, impozit, dividende) se
#  rotunjesc ARITMETIC (half-up), nu bancar - aceeasi regula ANAF ca la D112 (validator A91b:
#  "Contributiile se rotunjesc aritmetic"). _i = Decimal.quantize(ROUND_HALF_UP).
# ============================================================
def test_d205_rotunjeste_aritmetic_nu_bancar():
    from core.d205 import _i
    assert _i(112.5) == 113   # aritmetic; bancar (half-to-even) ar da 112
    assert _i(2.5) == 3       # bancar ar da 2 (par)
    assert _i(0.5) == 1       # bancar ar da 0
    assert _i(112.4) == 112
    assert _i(112.6) == 113
