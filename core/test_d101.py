# -*- coding: utf-8 -*-
"""Teste gardian D101 - RECONSTRUIT 01.08.2026 pe formularul OFICIAL (OPANAF 206/2025, D101_A600 v10,
anaf_surse/d101_struct_anaf.txt).

Reconstructia a inlaturat numerotarea P INVENTATA (versiunea anterioara: p11=impozit, p9=baza -
nu corespundea formularului) si a mutat P-urile din ELEMENTE-copil in ATRIBUTE pe <declaratie101>
(validatorul respingea 'sectiune necunoscuta P1'). Fiecare P corespunde acum randului oficial; lantul
de formule (P3=P1-P2, P7=P3+P6, P10=P7+P8-P9, P22=P10-P16-P21, P40, P41=P411+P412, totalPlata_A=
suma(P1..P53)) e cel din doc. Proba nu mai e doar 'trece DUK' (trecea si cu numerotare inventata) -
golden calculat de mana + corespondenta camp/formula in DECIZII 01.08.
"""
import pytest
from core.d101 import calcul_d101, build_xml, erori_generare, _nr_evid, _scadenta, NS


def _prof():
    return {"cui": "14399840", "nume": "DANTE INTERNATIONAL SA",
            "adresa": "Bd. Timisoara 26Z", "caen": "4711"}


def test_namespace_e_v10():
    assert NS == "mfp:anaf:dgti:d101:declaratie:v10"


# ── GOLDEN: caz numeric calculat de MANA din formulele oficiale (Conditia 1 Costin) ──
def test_golden_lant_formule_oficiale():
    """Venituri exploatare 100000, cheltuieli exploatare 60000, fara ajustari fiscale.
    Lant OFICIAL (OPANAF 206/2025), calculat de mana:
      P3 = P1-P2 = 40000 ; P6 = P4-P5 = 0 ; P7 = P3+P6 = 40000 (rd.40, R38)
      P10 = P7+P8-P9 = 40000 ; P22 = P10-P16-P21 = 40000 (rd.69)
      P35 = P22+P34 = 40000 ; P38a = P35+P36+P37-P38 = 40000 (rd.86a)
      P40 = P38a-P39a = 40000 (rd.88) ; P411 = 16% x P40 = 6400 (rd.90)
      P41 = P411+P412 = 6400 (rd.89, R41) ; P48 = P481 = P41-P42-P43-P44-P45 = 6400 (rd.105/106)
      P52 = (P48+P51)-(P49+P50) = 6400 (rd.110)
      totalPlata_A = suma(P1..P53) = 100000+60000+40000+40000+40000+40000+40000+40000+6400+6400+6400 = 419200 (rd.20)"""
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000})
    asteptat = {"P1": 100000, "P2": 60000, "P3": 40000, "P7": 40000, "P10": 40000,
                "P22": 40000, "P35": 40000, "P38a": 40000, "P40": 40000,
                "P411": 6400, "P41": 6400, "P481": 6400, "P48": 6400, "P52": 6400}
    for k, v in asteptat.items():
        assert res.P.get(k) == v, "%s: astept %d, obtinut %s" % (k, v, res.P.get(k))
    assert res.total_plata_a == 419200, "checksum P1..P53"
    # impozitul e in P41 (oficial), NU in P11 (numerotarea inventata a disparut)
    assert res.P.get("P11", 0) == 0


def test_pierdere_nu_genereaza_impozit():
    """Cheltuieli > venituri -> P38a<0 -> P40=0 -> fara impozit (P41 absent)."""
    res = calcul_d101(_prof(), 2026, {"P1": 5000, "P2": 9000})
    assert res.P["P3"] == -4000 and res.P["P22"] == -4000
    assert res.P.get("P40", 0) == 0
    assert "P41" not in res.P and "P411" not in res.P


def test_venituri_financiare_separate_de_exploatare():
    """P1/P2 = exploatare, P4/P5 = financiar; P7 = (P1-P2)+(P4-P5)."""
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000, "P4": 5000, "P5": 2000})
    assert res.P["P3"] == 40000 and res.P["P6"] == 3000 and res.P["P7"] == 43000


def test_cheie_intrare_necunoscuta_ridica():
    """Un typo intr-o cheie P (ex. Pxx) e RESPINS, nu se scurge in implicit tacut."""
    with pytest.raises(ValueError):
        calcul_d101(_prof(), 2026, {"P1": 1000, "Pxx": 5})


def test_impozit_e_in_P41_ca_atribut_nu_element():
    """Regresie clasa d101: P-urile sunt ATRIBUTE pe <declaratie101>, nu elemente <P41>."""
    xml = build_xml(calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000}))
    assert 'P41="6400"' in xml
    assert "<P41>" not in xml and "<P1>" not in xml


def test_flagurile_valide_apar_pe_radacina():
    res = calcul_d101(_prof(), 2026, {"P1": 1000, "P2": 500})
    xml = build_xml(res)
    for flag in ("d_rec", "d_reg", "d_reglem", "d_anulare", "d_succ", "d_prof", "d_alte"):
        assert '%s="0"' % flag in xml, "lipseste %s" % flag
    assert "d_recN=" not in xml and "d_grup=" not in xml


def test_cod_obligatie_si_denumire():
    xml = build_xml(calcul_d101(_prof(), 2026, {"P1": 1000, "P2": 500}))
    assert 'cod_obligatie="103"' in xml
    assert 'denumire=' in xml and ' den=' not in xml


def test_scadenta_LL_plus_3_pentru_an_peste_2025():
    """Scadenta D101 (regula datata, temeiuri confirmate 03.08.2026): an Data_S 2022-2025 -> 25 iunie/LL+6
    (OUG 153/2020 art.I alin.(13) lit.a), derogare art.41-42 CF, aplicabil 2021-2025 - LEGAL CORECT si DUK-valid);
    an Data_S 2026+ -> 25 martie/LL+3 (art.42(1) CF baza dupa incheierea schemei = ce cere jar-ul DUK). OUG
    8/2026 muta 2026 la iunie cand validatorul se actualizeaza (proba DUK pe an=2026 va semnala). Vezi DECIZII."""
    assert _scadenta(2026) == (3, 2027) and _scadenta(2025) == (6, 2026)
    assert 'scadenta="250327"' in build_xml(calcul_d101(_prof(), 2026, {"P1": 1000, "P2": 500}))
    assert 'scadenta="250626"' in build_xml(calcul_d101(_prof(), 2025, {"P1": 1000, "P2": 500}))


def test_cod_bug_data_i_data_s():
    xml = build_xml(calcul_d101(_prof(), 2026, {"P1": 1000, "P2": 500}))
    assert 'cod_bug="5503XXXXXX"' in xml
    assert 'Data_I="01.01.2026"' in xml and 'Data_S="31.12.2026"' in xml


def test_nr_evid_are_23_caractere_si_cifra_control():
    n = _nr_evid("14399840", 2026, 12)
    assert len(n) == 23 and n.isdigit()
    suma = sum(int(c) for c in n[:21])
    assert n[21:23] == "%02d" % (suma % 100)


def test_lipsa_caen_e_prinsa_la_generare():
    prof = dict(_prof()); del prof["caen"]
    assert any("CAEN" in e for e in erori_generare(prof))


# ── PROBA PANA LA DECLARATIE: contract uniform + reconstructie -> DUK VALID (pe date reale) ──
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk, d101 as _d101

_SCHEMA_D101 = "ztest_d101_recon"
_D101_DUK = _duk.poate_valida("d101")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_schema_profit():
    """Schema temporara, firma completa (caen) + note validate: venit exploatare 100000 (cont 707)
    si cheltuiala exploatare 60000 (cont 607) in 2026. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_D101)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_D101))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_D101)
                cur.execute(
                    "INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, "
                    "regim_fiscal, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','6202','real',true,'L','Pop','Ion','administrator') "
                    "ON CONFLICT (id) DO UPDATE SET caen=EXCLUDED.caen")
                cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere) "
                            "VALUES ('2026-06-15','validata','test','Vanzare') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'4111','707',100000)", (iid,))
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s,'607','401',60000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d101_reconstructie_pull_genereaza(conn_schema_profit):
    """pull split exploatare/financiar -> calcul_d101 oficial -> P41=impozit (nu P11)."""
    xml, res = _d101.genereaza(conn_schema_profit, _SCHEMA_D101, Perioada(2026))
    assert res.an == 2026
    assert res.P["P1"] == 100000 and res.P["P2"] == 60000 and res.P["P3"] == 40000
    assert res.P["P40"] == 40000 and res.P["P41"] == 6400 and res.P["P52"] == 6400
    assert res.total_plata_a == 419200


@pytest.mark.skipif(not _db_ok() or not _D101_DUK, reason="DB sau DUK d101 indisponibil")
def test_d101_reconstructie_proba_duk_valid(conn_schema_profit):
    """Proba pana la declaratie: D101 reconstruit trece validatorul OFICIAL DUK (era: respins pe P1)."""
    xml, res = _d101.genereaza(conn_schema_profit, _SCHEMA_D101, Perioada(2026))
    rez = _duk.valideaza(xml, "d101", an=2026)
    assert rez["stare"] == "valid", "DUK a respins D101 reconstruit: %s" % rez


# ---- Cota impozit pe profit = 16% (verificare la sursa, aliniere la lege) ----
def test_cota_profit_16pct_din_cota_cu_temei():
    # CF art.17 (verbatim anaf_surse/cod_fiscal_227_2015_consolidat.html): "Cota de impozit pe profit
    # care se aplica asupra profitului impozabil este de 16%". Valoarea traieste in common.COTE
    # (impozit_profit, CF art.17); d101 o foloseste ca P411 = 16% x P40.
    from decimal import Decimal as _D
    from core import common as _c
    assert _c.cota("impozit_profit")[0] == _D("0.16")   # CF art.17 (16%, stabil din 2005)
    # golden d101: P411 = 16% x P40 (vezi test_calcul_d101_complet, P40=40000 -> P411=6400)


# ============================================================
#  IMCA - impozit minim pe cifra de afaceri (CF art.18^1). Verificat verbatim anaf_surse/.
# ============================================================
def test_imca_formula_1pct_din_vt_vs_i_a():
    from core.d101 import impozit_minim_cifra_afaceri as imca
    # art.18^1 alin.(3): IMCA = 1% x (VT - Vs - I - A)
    assert imca(100_000_000, 20_000_000, 5_000_000, 3_000_000) == 720_000   # 1% x 72.000.000
    assert imca(300_000_000, 20_000_000, 5_000_000, 3_000_000) == 2_720_000  # 1% x 272.000.000
    # art.18^1 alin.(4): valoare negativa -> impozit minim zero
    assert imca(10_000_000, 8_000_000, 3_000_000, 1_000_000) == 0            # 1% x (-2.000.000) -> 0


def test_datoreaza_imca_prag_50mil_euro():
    from core.d101 import datoreaza_imca
    # art.18^1 alin.(1): cifra de afaceri (= VT - Vs) > 50.000.000 euro, la curs
    assert datoreaza_imca(300_000_000, 20_000_000, 5) is True    # (280M)/5 = 56M euro > 50M
    assert datoreaza_imca(200_000_000, 20_000_000, 5) is False   # (180M)/5 = 36M euro < 50M


def test_imca_wiring_p47_si_comparatie_p48():
    from core.d101 import calcul_d101
    # firma cu impozit pe profit (comparatie) MIC si IMCA MARE -> P48 = P482 (nivelul IMCA).
    # imca: VT=300M, Vs=20M, I=5M, A=3M, curs=5 -> eligibil (56M euro); IMCA = 1% x 272M = 2.720.000.
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000, "P46": 1_000_000},
                      imca={"vt": 300_000_000, "vs": 20_000_000, "i": 5_000_000, "a": 3_000_000, "curs": 5})
    assert res.P["P47"] == 2_720_000                 # P47 computat din formula
    # P46 (1.000.000) < P47 (2.720.000) -> se plateste la nivelul IMCA (P482)
    assert res.P["P482"] == 2_720_000
    assert res.P["P48"] == 2_720_000


def test_imca_sub_prag_p47_zero():
    from core.d101 import calcul_d101
    # firma sub pragul de 50M euro -> nu datoreaza IMCA -> P47=0, se plateste impozitul pe profit normal.
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000, "P46": 1_000_000},
                      imca={"vt": 200_000_000, "vs": 20_000_000, "i": 0, "a": 0, "curs": 5})
    assert res.P.get("P47", 0) == 0


@pytest.mark.skipif(not _duk.poate_valida("d101"), reason="DUK d101 indisponibil")
def test_imca_d101_duk_valid():
    # D101 cu IMCA (P47 computat = 2.720.000; P48 = P482 = nivelul IMCA) trece DUKIntegrator.
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000, "P46": 1_000_000},
                      imca={"vt": 300_000_000, "vs": 20_000_000, "i": 5_000_000, "a": 3_000_000, "curs": 5})
    assert res.P["P47"] == 2_720_000 and res.P["P48"] == 2_720_000
    xml = build_xml(res)
    r = _duk.valideaza(xml, "d101", an=2026)
    assert r["stare"] == "valid", "d101+IMCA respins de DUK: %s" % (str(r.get("erori") or ""))[:200]


# ---- Amortizare fiscala (CF art.28): ajustarea fiscal-contabil in d101 ----
def test_amortizare_ajustare_fiscala_art28():
    # CF art.28 (amortizarea fiscala): amortizarea CONTABILA (P28) se ADAUGA inapoi (P34), amortizarea
    # FISCALA (P11) se DEDUCE (P16). Golden: venituri 100000, cheltuieli 60000 (include 10000 amort
    # contabila), amort fiscala 12000 -> impozabil = 40000 - 12000 + 10000 = 38000; impozit = 16% = 6080.
    res = calcul_d101(_prof(), 2026, {"P1": 100000, "P2": 60000, "P28": 10000, "P11": 12000})
    assert res.P["P16"] == 12000   # amortizarea fiscala dedusa (art.28 alin.1)
    assert res.P["P34"] == 10000   # amortizarea contabila adaugata inapoi
    assert res.P["P22"] == 28000
    assert res.P["P35"] == 38000
    assert res.P["P411"] == 6080   # 16% x 38000


def test_mf_prag_amortizabil_5000_art28():
    # CF art.28 alin.(2) lit.b: mijloc fix amortizabil are valoare fiscala >= 5.000 lei (plafon OUG 8/2026).
    from core.mijloace_fixe_import_api import PLAFON_MF_2026
    assert PLAFON_MF_2026 == 5000.0



def test_rezerva_legala_deductibila_auto_art26_1_a():
    """CF art.26 alin.(1) lit.a: rezerva legala deductibila (P13) se COMPUTA AUTOMAT din contabilitate
    cand nu e data manual - omiterea ei (firma ar supra-declara impozitul pe profit) devine IMPOSIBILA.
    Baza = profitul contabil brut = P7 + cheltuiala cu impozitul (691, se adauga inapoi - fara bucla cu
    impozitul D101). Deductibil = min(5%% x baza; 20%% x capital subscris/varsat 1012 - rezerva 1061), >=0."""
    from core.d101 import calcul_d101
    prof = {"cui": "14399840", "nume": "T SRL"}
    ir = {"P1": 1000000, "P2": 700000}   # P7 = 300000 (P2 include 691)
    # baza = 300000 + 50000 = 350000; 5%% = 17500; capital 200000 -> plafon 20%% = 40000 -> P13 = 17500
    res = calcul_d101(prof, 2026, dict(ir), rezerva={"capital": 200000, "rezerva_existenta": 0, "chelt_impozit": 50000})
    assert res.P["P13"] == 17500, res.P.get("P13")
    # OMITEREA IMPOSIBILA: conditii indeplinite, P13 NU dat manual -> se computa (> 0), nu ramane 0
    assert res.P["P13"] > 0
    # plafonul de 20%% musca: rezerva existenta 35000 -> plafon 40000-35000 = 5000 < 17500 -> P13 = 5000
    res2 = calcul_d101(prof, 2026, dict(ir), rezerva={"capital": 200000, "rezerva_existenta": 35000, "chelt_impozit": 50000})
    assert res2.P["P13"] == 5000, res2.P.get("P13")
    # pierdere contabila (baza <= 0) -> nicio rezerva
    resl = calcul_d101(prof, 2026, {"P1": 700000, "P2": 1000000}, rezerva={"capital": 200000, "rezerva_existenta": 0, "chelt_impozit": 0})
    assert resl.P.get("P13", 0) == 0
    # override MANUAL respectat (contabilul poate forta P13)
    resm = calcul_d101(prof, 2026, dict(ir, P13=9000), rezerva={"capital": 200000, "rezerva_existenta": 0, "chelt_impozit": 50000})
    assert resm.P["P13"] == 9000, resm.P.get("P13")
