# -*- coding: utf-8 -*-
"""Teste gardian pentru d394 (functiile PURE).

Fiecare test apara o regula DOVEDITA pe D394Validator v5 (15.07.2026), cu numarul
ei. Daca un test pica dupa o modificare, ANAF ar respinge declaratia.
Modulul n-a avut NICIODATA teste - de asta a putut sta rupt fara sa se observe.
"""
from decimal import Decimal

from core.d394 import (
    COTE, TIP_COTA_ZERO, TIPURI, OP1_CU_TVA, REZ1_FARA_TVA,
    P_TVA_RO, P_NEINREG, P_UE, P_NONUE,
    calcul_d394, build_xml, clasifica_partener, tip_operatiune, rez1_tipuri,
    jud_siruta, codpr_din_categorie, cui_ro, cota_standard,
)
from core.common import Perioada as _Per394
_calcul_d394_real = calcul_d394


def calcul_d394(prof, an, luna, facturi, manual=None, serii_emise=None):
    """Shim de test: mapeaza apelurile vechi (an,luna,facturi[,manual,serii]) pe contractul nou
    calcul_d394(prof, perioada, date, manual). Adaptor VIZIBIL de test - modulul are contractul curat."""
    return _calcul_d394_real(prof, _Per394(an, luna=luna),
                             {"facturi": facturi, "serii": serii_emise or {}},
                             {"operatiuni": manual} if manual is not None else None)


PROF = {"cui": "26766053", "caen": "6920", "nume": "TEST SRL", "adresa": "Str. 1",
        "telefon": "0722000000", "judet": "B", "declarant_functie": "ADMIN"}


def _f(cui, directie, cota, baza, tva, ti=False, cat=None, nume="P"):
    return {"cui": cui, "nume": nume, "directie": directie, "cota": cota,
            "baza": Decimal(str(baza)), "tva": Decimal(str(tva)),
            "taxare_inversa": ti, "categorie_331": cat}


# ---------- clasificarea partenerului (pct. 216) ----------
def test_partener_ro_valid_e_tip_1():
    assert clasifica_partener("RO14399840") == (P_TVA_RO, "14399840")


def test_partener_fara_cui_e_tip_2():
    assert clasifica_partener("") == (P_NEINREG, None)
    assert clasifica_partener(None) == (P_NEINREG, None)


def test_partener_ue_e_tip_3_nu_se_exclude():
    """Partenerii straini INTRA in D394 ca tip 3/4 - vechea versiune ii excludea."""
    tp, cui = clasifica_partener("IE6388047V")
    assert tp == P_UE and cui == "IE6388047V"


def test_partener_non_ue_e_tip_4():
    assert clasifica_partener("CH123456")[0] == P_NONUE


def test_tip_partener_clasificare_pct216():
    """VERIFICARE pct.216 (sursa curenta OPANAF 77/2022): clasificarea acopera cele 4 categorii oficiale.
    1 = persoana impozabila inregistrata in RO (prefix RO / numeric); 2 = neinregistrata (fara CUI sau CUI
    ne-numeric); 3 = stabilita in alt stat membru UE (prefix stat membru din _TARI_UE); 4 = nestabilita in UE.
    NOTA de design (conform): validitatea checksum-ului CUI-ului RO NU se verifica la clasificare (cui_ro e
    doar NORMALIZARE) - un CUI RO invalid da tip 1, iar D394Validator il respinge (R218.2: cuiP invalid),
    FAIL-FAST, nu tacit; a-l reclasifica la tip 2 ar declara GRESIT un partener inregistrat ca neinregistrat.
    Ramura UE/non-UE se sprijina pe _TARI_UE (verificat DUK in clusterul nomenclator tari HR->CR)."""
    assert clasifica_partener("RO14399840")[0] == P_TVA_RO          # 1 - inregistrat RO
    assert clasifica_partener("14399840")[0] == P_TVA_RO            # 1 - numeric fara prefix = RO
    assert clasifica_partener("")[0] == P_NEINREG                   # 2 - fara CUI
    assert clasifica_partener(None)[0] == P_NEINREG                 # 2 - None
    assert clasifica_partener("ROABC")[0] == P_NEINREG             # 2 - RO ne-numeric -> neinregistrat
    assert clasifica_partener("DE811569869")[0] == P_UE            # 3 - UE (Germania)
    assert clasifica_partener("HR12345678901")[0] == P_UE          # 3 - UE (Croatia, prefix HR)
    assert clasifica_partener("CH123456")[0] == P_NONUE            # 4 - non-UE (Elvetia)
    # cele 4 valori sunt distincte (nomenclatorul oficial de tip_partener)
    assert len({P_TVA_RO, P_NEINREG, P_UE, P_NONUE}) == 4


# ---------- tipul operatiunii (pct. 215) ----------
def test_tip_respecta_compatibilitatea_cu_partenerul():
    """tip_partener=1 -> tip<>N ; =2 -> tip in (L,LS,N) ; in (3,4) -> tip in (L,LS,C)"""
    assert tip_operatiune("emisa", False, P_TVA_RO) == "L"
    assert tip_operatiune("primita", False, P_TVA_RO) == "A"
    assert tip_operatiune("emisa", True, P_TVA_RO) == "V"
    assert tip_operatiune("primita", True, P_TVA_RO) == "C"
    assert tip_operatiune("primita", False, P_NEINREG) == "N"
    assert tip_operatiune("emisa", False, P_NEINREG) == "L"
    assert tip_operatiune("emisa", False, P_UE) == "L"


def test_toate_tipurile_generate_sunt_in_lista_oficiala():
    for tp in (P_TVA_RO, P_NEINREG, P_UE, P_NONUE):
        for d in ("emisa", "primita"):
            for ti in (True, False):
                assert tip_operatiune(d, ti, tp) in TIPURI


def _oib_d394(base10="1234567890"):
    x = 10
    for ch in base10:
        x = (x + int(ch)) % 10
        if x == 0:
            x = 10
        x = (x * 2) % 11
    return base10 + str((11 - x) % 10)


def test_TIPURI_e_setul_validatorului_curent():
    """Pin pct.215: TIPURI = cele 8 tipuri op1 acceptate de D394Validator INSTALAT (J8, versiunea CURENTA
    ANAF), aliniate la OPANAF 77/2022 (anaf_surse/opanaf_77_2022). Sursa NU mai e pdf-ul structD394_02092020
    (2020/J4, invechit, care avea 9 tipuri incl. ASI). ASI a fost ELIMINAT post-2020 (03.08.2026, greenlight
    Costin - tool-ul urmeaza validatorul). Un tip adaugat/scos tacit din cod pica aici."""
    assert set(TIPURI) == {"A", "L", "C", "V", "AI", "LS", "AS", "N"}, "TIPURI = %s" % sorted(TIPURI)
    assert "ASI" not in TIPURI and "ASI" not in TIP_COTA_ZERO and "ASI" not in REZ1_FARA_TVA


def test_asi_ramane_scos_gard_invers():
    """GARD INVERS (fost datorie, REZOLVAT 03.08.2026 cu greenlight Costin). ASI a fost SCOS din TIPURI ca
    aliniere la D394Validator INSTALAT (care il respinge - 'tip: valoarea ASI nu se afla in lista') si la
    OPANAF 77/2022 (AS = achizitii regim special, fara sub-varianta dupa sistemul de TVA al partenerului;
    fost-ASI -> AS). Verifica INVERS: daca o versiune noua de validator ajunge sa ACCEPTE din nou ASI, testul
    PICA si te anunta sa reevaluezi (poate ASI a fost reintrodus in structura). Fara date ASI de migrat:
    op1.tip NU e persistat in DB (derivat din facturi - niciodata ASI - sau dat manual la generare)."""
    from core import duk
    if not duk.poate_valida("d394"):
        import pytest
        pytest.skip("DUK d394 indisponibil")
    import re
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210)]
    xml = build_xml(calcul_d394(PROF, 2026, 6, facturi))
    xml_asi = re.sub(r'(<op1 tip=")[^"]*(")', lambda m: m.group(1) + "ASI" + m.group(2), xml, count=1)
    rez = duk.valideaza(xml_asi, "d394", an=2026, luna=6)
    er = str(rez.get("erori"))
    assert "ASI" in er and "nu se afla in lista" in er, (
        "Validatorul instalat ACCEPTA acum ASI (nu mai da eroare de enum) - ASI pare REINTRODUS intr-o "
        "versiune noua de D394; reevalueaza scoaterea lui din TIPURI. erori=%s" % er[:200])



# ---------- rezumat1: setul de campuri (R38/R41/R49/R53/R56/R591) ----------
def test_rez1_cota_zero_nu_are_L():
    """R38.2: daca cota = 0 atunci facturiL nu trebuie sa existe."""
    assert "L" not in rez1_tipuri(P_TVA_RO, 0)


def test_rez1_cota_nenula_are_L():
    assert "L" in rez1_tipuri(P_TVA_RO, 21)


def test_rez1_A_doar_la_partener_1():
    """R43.2/R46.2: A si AI doar la tip_partener = 1."""
    assert "A" in rez1_tipuri(P_TVA_RO, 21)
    assert "A" not in rez1_tipuri(P_NEINREG, 11)
    assert "A" not in rez1_tipuri(P_UE, 21)


def test_rez1_N_doar_la_partener_2_si_cota_0():
    """R591.2/R62.2: N doar la tip_partener = 2."""
    assert "N" in rez1_tipuri(P_NEINREG, 0)
    assert "N" not in rez1_tipuri(P_TVA_RO, 0)
    assert "N" not in rez1_tipuri(P_NEINREG, 11)


def test_rez1_AS_si_V_doar_la_partener_1_cota_0():
    """R49.1/R53.1."""
    assert "AS" in rez1_tipuri(P_TVA_RO, 0) and "V" in rez1_tipuri(P_TVA_RO, 0)
    assert "AS" not in rez1_tipuri(P_NEINREG, 0)


def test_rezumat1_campuri_complete_tp1_tp3_valide_pe_validator():
    """VERIFICARE (cluster rezumat1 campuri complete): pentru partenerii INREGISTRATI (RO tip 1) si STRAINI
    (UE tip 3 / non-UE tip 4), setul de campuri rezumat1 emis (facturi/baza pe fiecare tip cerut, tva doar
    pt A/L/C/AI, 0-umplut) e COMPLET si ACCEPTAT de validatorul CURENT (J8). Probat pe DUK."""
    from core import duk
    if not duk.poate_valida("d394"):
        import pytest
        pytest.skip("DUK d394 indisponibil")
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210),      # L tp1 cota21
               _f("RO14399840", "primita", 21, 2000, 420),    # A tp1 cota21
               _f("DE811569869", "emisa", 0, 4000, 0)]        # L tp3
    res = calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 3)})
    rez = duk.valideaza(build_xml(res), "d394", an=2026, luna=6)
    assert rez["stare"] == "valid", "rezumat1 tp1/tp3 respins de J8: %s" % rez.get("erori")


def test_operatiuni_N_excluse_cu_avertisment_vizibil():
    """DECIZIE Costin 04.08 (approach b): operatiunile N (achizitii de la parteneri NEINREGISTRATI, produse auto
    din facturi fara CUI) se EXCLUD din D394 - NU tacit: cu AVERTISMENT VIZIBIL care NUMESTE furnizorul si suma
    (in res.avertismente -> UI + fluxul de generare). Restul declaratiei RAMANE valid (submitabil). Motiv: tip_N
    (bunuri/servicii) e continut declarat, un default gresit ar produce o declaratie ACCEPTATA dar FALSA."""
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210),
               _f("", "primita", 0, 500, 0, nume="FURNIZOR NEINREG SRL")]  # -> N, exclus
    res = calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 1)})
    # N nu apare in declaratie
    assert not any(k[0] == "N" for k in res.op1), "N trebuie EXCLUS din op1"
    assert 'tip="N"' not in build_xml(res), "N nu trebuie sa apara in XML"
    # avertisment VIZIBIL care numeste furnizorul si suma
    av = " ".join(res.avertismente)
    assert "EXCLUSE" in av and "FURNIZOR NEINREG SRL" in av and "500" in av, (
        "avertismentul trebuie sa numeasca furnizorul si suma excluse; got: %s" % res.avertismente)
    # restul declaratiei e valid pe validatorul curent
    from core import duk
    if duk.poate_valida("d394"):
        rez = duk.valideaza(build_xml(res), "d394", an=2026, luna=6)
        assert rez["stare"] == "valid", "restul D394 (fara N) trebuie sa fie valid: %s" % rez.get("erori")


def test_N_ar_fi_respins_de_validator_daca_emis_GARD_INVERS():
    """GARD ANTI-REGRESIE (ramane pana la implementarea completa a suportului N - decizie Costin 04.08).
    Motivul pentru care N se EXCLUDE (nu se emite) e ca validatorul CURENT (J8) il RESPINGE: op1.tip_document
    (pct.228) / rezumat1.document_N (pct.60) lipsesc. Injectam manual un op1 N intr-o declaratie valida si
    confirmam ca J8 il respinge. Cand se implementeaza suportul N complet (tip_document/tip_N/document_N) SAU
    validatorul ajunge sa accepte N fara ele, acest test PICA si te anunta sa reevaluezi excluderea."""
    from core import duk
    if not duk.poate_valida("d394"):
        import pytest
        pytest.skip("DUK d394 indisponibil")
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210)]
    xml = build_xml(calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 1)}))
    # injecteaza un op1 N (achizitie de la neinregistrat) fara atributele tehnice cerute
    op_n = '  <op1 tip="N" tip_partener="2" cota="0" cuiP="" denP="X" nrFact="1" baza="500" tva="0"/>\n'
    xml_n = xml.replace("</declaratie394>", op_n + "</declaratie394>")
    rez = duk.valideaza(xml_n, "d394", an=2026, luna=6)
    er = str(rez.get("erori"))
    assert rez["stare"] != "valid" and ("tip_document" in er or "document_N" in er or "N" in er), (
        "Validatorul ACCEPTA acum un op1 N fara tip_document/document_N - suportul N pare (partial) valid; "
        "reevalueaza EXCLUDEREA N (poate poate fi emis). stare=%s erori=%s" % (rez.get("stare"), er[:200]))


def test_rez1_LS_la_orice_partener_cu_cota_0():
    """R41.1: daca cota = 0 atunci facturiLS trebuie sa existe."""
    assert "LS" in rez1_tipuri(P_TVA_RO, 0)
    assert "LS" in rez1_tipuri(P_NEINREG, 0)


def test_rez1_C_la_parteneri_1_3_4_cu_cota_nenula():
    """R56.1."""
    for tp in (P_TVA_RO, P_UE, P_NONUE):
        assert "C" in rez1_tipuri(tp, 21)
    assert "C" not in rez1_tipuri(P_NEINREG, 11)


def test_tipurile_fara_tva_nu_primesc_tva_in_rezumat1():
    """tvaV/tvaLS/tvaAS/tvaN sunt atribute NECUNOSCUTE in v5."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True,
                                       cat="deseuri")])
    for (tp, cota), camp in r.rezumat1.items():
        for tip in REZ1_FARA_TVA:
            assert ("tva" + tip) not in camp, "tva%s nu exista in v5" % tip


# ---------- cota (pct. 217) ----------
def test_cota_zero_permisa_doar_pentru_LS_AS_N_V():
    # ASI eliminat 03.08.2026 (aliniere validator J8 / OPANAF 77/2022) - vezi TIPURI.
    assert set(TIP_COTA_ZERO) == {"LS", "AS", "N", "V"}


def test_achizitie_taxare_inversa_cu_cota_zero_e_semnalata_nu_declarata():
    """C nu e in lista pentru cota 0: beneficiarul aplica 4426=4427 la cota bunului."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "primita", 0, 5000, 0, ti=True)])
    assert not r.op1
    assert any("cot" in a.lower() for a in r.avertismente)


def test_achizitie_taxare_inversa_cu_cota_reala_intra():
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "primita", 21, 5000, 1050,
                                       ti=True, cat="deseuri")])
    assert any(k[0] == "C" for k in r.op1)


def test_cota_standard_vine_din_sursa_unica():
    """Legea 141/2025: 21% de la 01.08.2025. common tine FRACTII, D394 cere PROCENTE."""
    assert cota_standard(2025, 7) == 19
    assert cota_standard(2025, 8) == 21
    assert cota_standard(2026, 6) == 21


# ---------- informatii (pct. 122-125, R132) ----------
def test_nrCui2_e_numar_de_inregistrari_nu_distinct():
    """pct.123: nrCui2 = Nr inregistrari op1 pt tip_partener=2 (nu count distinct)."""
    r = calcul_d394(PROF, 2026, 6, [
        _f("", "emisa", 11, 100, 11, nume="POPESCU"),
        _f("", "emisa", 21, 200, 42, nume="IONESCU"),
    ])
    assert r.informatii["nrCui2"] == 2


def test_nrCui1_e_distinct_pe_cui():
    r = calcul_d394(PROF, 2026, 6, [
        _f("RO14399840", "emisa", 21, 100, 21),
        _f("RO14399840", "primita", 21, 200, 42),
    ])
    assert r.informatii["nrCui1"] == 1


def test_nrFacturiL_PF_e_mereu_zero():
    """R132: incepand cu perioada 1.2017 trebuie sa fie 0."""
    r = calcul_d394(PROF, 2026, 6, [_f("", "emisa", 11, 100, 11)])
    assert r.informatii["nrFacturiL_PF"] == 0


def test_tvaDedAI_obligatoriu_dar_tvaDed_doar_la_tva_la_incasare():
    """R135.1: sistemTVA=0 -> tvaDed* nu se completeaza; tvaDedAI* mereu."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 100, 21)])
    assert "tvaDedAI21" in r.informatii
    assert "tvaDed21" not in r.informatii
    r2 = calcul_d394(dict(PROF, tva_la_incasare=True), 2026, 6,
                     [_f("RO14399840", "emisa", 21, 100, 21)])
    assert "tvaDed21" in r2.informatii


# ---------- totalPlata_A (pct. 17 / R17) ----------
def test_totalPlata_A_R17_sursa_unica_si_probat_pe_validator():
    """VERIFICARE R17 (cluster totalPlata_A): res.total_plata_a (calculat in calcul_d394) == valoarea EMISA
    in XML (SURSA UNICA - build_xml emite res, clasa d100). Probat pe validatorul CURENT J8: valoarea corecta
    e VALIDA, o valoare gresita e RESPINSA cu DUK regula R17 (totalPlata_A trebuie sa fie egal cu Suma...). Formula
    codului = R17-ul validatorului, nu una inventata (comentariul d394.py:18 despre formula veche inventata)."""
    import re
    from core import duk
    if not duk.poate_valida("d394"):
        import pytest
        pytest.skip("DUK d394 indisponibil")
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210), _f("RO4221306", "primita", 21, 2000, 420)]
    res = calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 1)})
    xml = build_xml(res)
    emis = int(re.search(r'totalPlata_A="(\d+)"', xml).group(1))
    assert emis == res.total_plata_a, "totalPlata_A emis (%d) != res (%d) - sursa unica rupta" % (emis, res.total_plata_a)
    assert duk.valideaza(xml, "d394", an=2026, luna=6)["stare"] == "valid", "valoarea corecta trebuie sa fie R17-valida"
    xml_bad = re.sub(r'totalPlata_A="\d+"', 'totalPlata_A="%d"' % (emis + 999), xml, count=1)
    rez = duk.valideaza(xml_bad, "d394", an=2026, luna=6)
    er = str(rez.get("erori"))
    assert rez["stare"] != "valid" and "R17" in er, "R17 nu mai impune totalPlata_A (checksum ne-pazit): %s" % er[:150]


def test_total_plata_a_dupa_formula_oficiala():
    """R17: totalPlata_A = Suma(nrCui<i>) + Suma(rezumat2.baza[L+A+AI])."""
    r = calcul_d394(PROF, 2026, 6, [
        _f("RO14399840", "emisa", 21, 1000, 210),
        _f("RO4221306", "primita", 21, 2000, 420),
    ])
    nrcui = sum(r.informatii["nrCui%d" % i] for i in (1, 2, 3, 4))
    baze = sum(v["bazaL"] + v["bazaA"] + v["bazaAI"] for v in r.rezumat2.values())
    assert r.total_plata_a == nrcui + baze


# ---------- rezumat2 (R84, R99) ----------
def test_rezumat2_exista_pentru_fiecare_cota_din_op1():
    """R84: Nu exista sectiune Rezumat2 pentru cota X pentru agregarea din Op1."""
    r = calcul_d394(PROF, 2026, 6, [
        _f("RO14399840", "emisa", 21, 1000, 210),
        _f("RO4221306", "emisa", 11, 100, 11),
    ])
    assert set(r.rezumat2) == {21, 11}


def test_achizitia_cu_taxare_inversa_intra_la_nrFacturiA_in_rezumat2():
    """R99: C e tot o achizitie - rezumat2 centralizeaza pe firma."""
    r = calcul_d394(PROF, 2026, 6, [
        _f("RO4221306", "primita", 21, 2000, 420),
        _f("RO14399840", "primita", 21, 5000, 1050, ti=True, cat="deseuri"),
    ])
    assert r.rezumat2[21]["nrFacturiA"] == 2


# ---------- op11 + detaliu (R233.5, R35) ----------
def test_op11_generat_pentru_taxare_inversa_la_partener_1():
    """R233.5: tip_partener=1 si tip in (C,V) -> cel putin o sectiune op11."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True,
                                       cat="deseuri")])
    assert r.op11 and list(r.op11.values())[0]["codPR"] == "22"


def test_op11_fara_tvaPR_la_livrare_cu_taxare_inversa():
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True,
                                       cat="deseuri")])
    assert list(r.op11.values())[0]["tvaPR"] is None


def test_cereale_codPR_e_subcodul_NC_iar_detaliu_bun_e_categoria():
    """ANAF: codul 21 e centralizator, NU la nivel de Detaliu."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True,
                                       cat="1005")])
    o = list(r.op11.values())[0]
    assert o["codPR"] == "1005" and o["bun"] == "21"
    assert any(k[2] == "21" for k in r.detaliu)


def test_taxare_inversa_fara_categorie_e_semnalata():
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True)])
    assert any("331" in a for a in r.avertismente)


def test_codpr_din_nomenclatorul_oficial():
    assert codpr_din_categorie("deseuri") == "22"
    assert codpr_din_categorie("telefoane") == "29"
    assert codpr_din_categorie("1005") == "1005"
    assert codpr_din_categorie("inexistent") is None


# ---------- judP (SIRUTA) ----------
def test_judp_e_cod_siruta_nu_abreviere():
    """Dovedit pe validator: 'B'/'PH'/'IF' respinse, 40 acceptat."""
    assert jud_siruta("B") == "40"
    assert jud_siruta("PH") == "29"
    assert jud_siruta("București") == "40"
    assert jud_siruta("40") == "40"
    assert jud_siruta(None) is None


def test_toate_judetele_au_cod_de_doua_cifre():
    from core.d394 import JUDETE_SIRUTA
    assert len(JUDETE_SIRUTA) == 42
    for ab, cod in JUDETE_SIRUTA.items():
        assert len(cod) == 2 and cod.isdigit(), ab


# ---------- intracomunitar ----------
def test_achizitia_intracomunitara_nu_intra_in_d394():
    """Ghid ANAF: se declara in D390 (VIES), nu in D394."""
    r = calcul_d394(PROF, 2026, 6, [_f("IE6388047V", "primita", 0, 1000, 0)])
    assert not r.op1
    assert any("390" in a for a in r.avertismente)


def test_livrarea_catre_ue_intra_ca_partener_3():
    r = calcul_d394(PROF, 2026, 6, [_f("IE6388047V", "emisa", 21, 1000, 210)])
    assert any(k[1] == P_UE for k in r.op1)


# ---------- XML ----------
def test_xml_are_ordinea_ceruta_de_validator():
    """declaratie394 -> informatii -> rezumat1 -> rezumat2 -> serieFacturi -> op1"""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 1000, 210)],
                    serii_emise={"A": (1, 5)})
    x = build_xml(r)
    poz = [x.index(t) for t in ("<informatii", "<rezumat1", "<rezumat2",
                                "<serieFacturi", "<op1")]
    assert poz == sorted(poz), "ordinea sectiunilor e normativa"


def test_xml_nu_are_elemente_inexistente_in_v5():
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 1000, 210)])
    x = build_xml(r)
    for t in ("<identificare", "<idReprezentant", "nume_declar", "prenume_declar"):
        assert t not in x, "%s nu exista in namespace v5" % t


def test_xml_are_atributele_obligatorii_pe_radacina():
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 1000, 210)])
    x = build_xml(r)
    for a in ("sistemTVA=", "op_efectuate=", "prsAfiliat=", "cui=", "caen=", "den=",
              "adresa=", "telefon=", "totalPlata_A=", "cif_intocmit=",
              "calitate_intocmit=", "denR=", "adresaR="):
        assert a in x, a


def test_xml_fara_functie_intocmit_la_persoana_juridica():
    """Validator: daca tip_intocmit = 0 atunci functie_intocmit nu trebuie completata."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 1000, 210)])
    x = build_xml(r)
    assert 'tip_intocmit="0"' in x and "functie_intocmit=" not in x


def test_op1_fara_tva_pentru_tipuri_in_afara_listei():
    """R232.2: tva doar pentru tip in (A, L, C, AI)."""
    assert set(OP1_CU_TVA) == {"A", "L", "C", "AI"}
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 0, 3000, 0, ti=True,
                                       cat="deseuri")])
    x = build_xml(r)
    linia = [l for l in x.split("\n") if "<op1 " in l][0]
    assert 'tip="V"' in linia and " tva=" not in linia


def test_op1_partener_2_are_tara_si_judet():
    """R220 + R222.3."""
    r = calcul_d394(PROF, 2026, 6, [_f("", "emisa", 11, 100, 11, nume="POPESCU")])
    x = build_xml(r)
    linia = [l for l in x.split("\n") if "<op1 " in l][0]
    assert 'taraP="RO"' in linia and 'judP="40"' in linia


def test_op_efectuate_zero_fara_operatiuni():
    r = calcul_d394(PROF, 2026, 6, [])
    assert r.op_efectuate == 0
    assert 'op_efectuate="0"' in build_xml(r)


def test_efectuat_nu_se_completeaza_la_solicit_zero():
    """R191.1."""
    r = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "emisa", 21, 1000, 210)])
    assert "efectuat=" not in build_xml(r)


def test_cotele_includ_21_si_11_din_legea_141_2025():
    assert 21 in COTE and 11 in COTE


def test_cui_ro_normalizeaza():
    assert cui_ro("RO 14399840") == "14399840"
    assert cui_ro("14399840") == "14399840"
    assert cui_ro("") is None


def test_d394_manual_tip_necunoscut_ridica_nu_dispare():
    # [GARD CLASA] operatiune manuala a contabilului cu tip gresit -> eroare vizibila, nu skip tacit.
    import pytest as _pt
    with _pt.raises(ValueError) as e:
        calcul_d394(PROF, 2026, 6, [], [{"tip": "ZZZ", "tip_partener": 1, "cota": 21,
                                       "cuiP": "RO123", "denP": "X", "nrFact": 1, "baza": 100, "tva": 21}])
    assert "tip necunoscut" in str(e.value)



def test_d394_cote_acceptate_sunt_setul_validatorului_v5():
    """Pin anti-drift: setul de cote acceptate de D394 = superset fix ce oglindeste validatorul
    ANAF v5 (OPANAF 2194/2025: TVA 21%% si 11%% de la 01.08.2025) peste structura 2020
    (0,5,9,19,20,24). O schimbare a setului cade aici si cere reverificare la validator."""
    assert COTE == (0, 5, 9, 11, 19, 20, 21, 24), COTE


def test_d394_cote_acopera_toate_cotele_tva_din_common():
    """Gard CROSS-MODUL anti-drop: orice cota de TVA din registrul central common.COTE (chei
    tva_*), la orice moment din valabilitate, TREBUIE sa fie in d394.COTE. Altfel o operatiune la
    o cota valida (ex. o cota redusa noua adaugata candva in common) ar fi IGNORATA tacit de D394
    ('Cota TVA nedeclarabila'). Leaga sursa unica de cote (common) de setul acceptat de D394."""
    from core import common
    ceruta = set()
    for cheie, serie in common.COTE.items():
        if not cheie.startswith("tva_"):
            continue
        for _din, val, _t in serie:
            ceruta.add(int(Decimal(str(val)) * 100))
    lipsa = ceruta - set(COTE)
    assert not lipsa, "cote TVA din common.COTE neacceptate de d394.COTE: %s" % sorted(lipsa)



def test_codpr_valide_pe_validatorul_curent():
    """VERIFICARE nomenclator codPR (art.331): codurile din d394.CODPR sunt ACCEPTATE de validatorul CURENT
    (J8), NU doar de Ghid_D394_2016 (sursa citata in cod, INVECHITA). Probat DUK pe reprezentative: deseuri(22),
    gaze_naturale(36) - fostul blocaj al datoriei lit.l, acum CONFIRMAT pe validator; cereale subcod NC 1001.
    Sursa autoritara pentru nomenclator = validatorul RULAT, nu ghidul 2016 (lectia ASI/limita-text)."""
    from core import duk
    if not duk.poate_valida("d394"):
        import pytest
        pytest.skip("DUK d394 indisponibil")
    for cat in ("deseuri", "gaze_naturale", "1001"):
        res = calcul_d394(PROF, 2026, 6, [_f("RO14399840", "primita", 21, 5000, 1050, ti=True, cat=cat)],
                          serii_emise={"A": (1, 1)})
        rez = duk.valideaza(build_xml(res), "d394", an=2026, luna=6)
        assert rez["stare"] == "valid", "codPR pentru %s respins de J8: %s" % (cat, rez.get("erori"))


def test_toate_categoriile_taxare_inversa_au_codpr_d394():
    """Gard CROSS-MODUL anti-regresie: orice categorie de taxare inversa recunoscuta de MOTOR
    (taxare_inversa.CATEGORII) TREBUIE sa aiba un codPR in maparea D394 (d394.CODPR). Altfel o
    factura in acea categorie e recunoscuta de motor dar CADE din sectiunea op11 obligatorie a D394
    (declaratie structural incompleta, validator R233.5). Cine adauga o categorie in motor fara
    codul D394 pica aici - forteaza fixul complet (motor + codPR impreuna), nu pe jumatate."""
    from core.taxare_inversa import CATEGORII
    from core.d394 import CODPR
    fara_cod = sorted(set(CATEGORII) - set(CODPR))
    assert not fara_cod, "categorii taxare inversa fara codPR D394: %s" % fara_cod


# ── Suport N approach (a) — 04.08.2026: N declarabil cu categoria art.331 (op11) ──
def test_N_cu_categorie_art331_e_declarat_si_valid_pe_duk():
    """approach (a): o operatiune N (achizitie de la persoana fizica neinregistrata) cu CATEGORIE art.331 se
    DECLARA in D394 - op1 tip_document=1 + rezumat1 document_N=1 + op11 codPR + detaliu nrN/valN. Probat pe
    validatorul INSTALAT (J8/v5). DESCOPERIRE (proba jar v5): op1.tip_N (bunuri/servicii) din pdf-ul de structura
    NU exista in v5 ('tip_N atribut necunoscut') - premisa approach b era pe un camp inexistent (tiparul ASI).
    Continutul declarat real e op11.codPR (categoria bunurilor), care reutilizeaza categorie_331 EXISTENTA."""
    from decimal import Decimal
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210),
               _f("", "primita", 0, 500, 0, nume="ION POPESCU", cat="deseuri")]  # N cu categorie
    res = calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 1)})
    xml = build_xml(res)
    assert any(k[0] == "N" for k in res.op1), "N cu categorie trebuie INCLUS in op1"
    assert 'tip="N"' in xml and 'tip_document="1"' in xml
    assert 'document_N="1"' in xml
    assert 'codPR="22"' in xml           # deseuri -> 22
    assert 'nrN=' in xml and 'valN=' in xml  # detaliu N
    from core import duk
    if duk.poate_valida("d394"):
        r = duk.valideaza(xml, "d394", an=2026, luna=6)
        assert r["stare"] == "valid", "N cu categorie respins de J8: %s" % r.get("erori")


def test_N_fara_categorie_ramane_exclus_cu_avertisment():
    """approach (a): N FARA categorie art.331 nu poate fi declarat valid (R233.6 cere op11.codPR pt persoana
    fizica) -> ramane EXCLUS cu avertisment care numeste furnizorul+suma si cere adaugarea categoriei. Restul
    declaratiei ramane valid (submitabil)."""
    facturi = [_f("RO14399840", "emisa", 21, 1000, 210),
               _f("", "primita", 0, 500, 0, nume="FURNIZOR PF")]  # N fara categorie
    res = calcul_d394(PROF, 2026, 6, facturi, serii_emise={"A": (1, 1)})
    assert not any(k[0] == "N" for k in res.op1), "N fara categorie trebuie EXCLUS"
    av = " ".join(res.avertismente)
    assert "EXCLUSE" in av and "FURNIZOR PF" in av and "500" in av and "categoria art.331" in av
    from core import duk
    if duk.poate_valida("d394"):
        assert duk.valideaza(build_xml(res), "d394", an=2026, luna=6)["stare"] == "valid"
