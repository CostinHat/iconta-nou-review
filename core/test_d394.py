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
def test_cota_zero_permisa_doar_pentru_LS_AS_ASI_N_V():
    assert set(TIP_COTA_ZERO) == {"LS", "AS", "ASI", "N", "V"}


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
