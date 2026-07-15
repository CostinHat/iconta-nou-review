# -*- coding: utf-8 -*-
"""Teste gardian pentru control_incrucisat.compara_tva (functia PURA).
Principii aparate: trei stari (verde/rosu/gri), remediu executabil DOAR cu cauza
dovedita, NICIODATA sugestie de ajustare a contului ca sa dea verde.
"""
from decimal import Decimal
from core.control_incrucisat import compara_tva, TOLERANTA


def _rulaje(colectata=0, dedusa=0):
    return {"4427": {"credit": Decimal(str(colectata)), "debit": Decimal("0")},
            "4426": {"debit": Decimal(str(dedusa)), "credit": Decimal("0")}}


def test_coerent_da_verde():
    r = compara_tva({"R17_2": 21, "R31_2": 0}, _rulaje(colectata=21))
    assert r[0]["stare"] == "verde"
    assert r[0]["remediu"] is None


def test_toleranta_1_leu_rotunjire_d300():
    # D300 rotunjeste la leu: 95 vs 94.50 contabil = coerent
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=Decimal("94.50")))
    assert r[0]["stare"] == "verde"


def test_divergenta_explicata_de_facturi_necontate_da_remediu_executabil():
    necontate = [
        {"id": 2, "directie": "emisa", "tva": Decimal("21.00")},
        {"id": 3, "directie": "emisa", "tva": Decimal("52.50")},
    ]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["diferenta"] == Decimal("74")
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [2, 3]


def test_divergenta_neexplicata_da_investigatie_nu_ajustare():
    # diferenta NU se explica prin necontate -> investigatie, fara buton
    necontate = [{"id": 2, "directie": "emisa", "tva": Decimal("5.00")}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "investigatie"
    assert c["remediu"]["facturi"] == []
    # PRINCIPIU: nu propunem ajustarea contului ca sa dea verde
    txt = (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()
    assert "ajusteaz" not in txt and "modifica contul" not in txt


def test_fiecare_constatare_isi_declara_temeiul():
    r = compara_tva({"R17_2": 21, "R31_2": 0}, _rulaje(colectata=21))
    for c in r:
        assert c["temei"]
        assert "D300" in c["temei"]


def test_temei_corect_pe_directie():
    r = compara_tva({"R17_2": 0, "R31_2": 0}, _rulaje())
    assert "emise" in r[0]["temei"]      # colectata <- facturi emise
    assert "primite" in r[1]["temei"]    # deductibila <- facturi primite


def test_deductibila_necontata_primite():
    necontate = [{"id": 9, "directie": "primita", "tva": Decimal("10.00")}]
    r = compara_tva({"R17_2": 0, "R31_2": 10}, _rulaje(dedusa=0), necontate)
    c = r[1]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [9]


def test_ciorna_nu_da_verde_asteapta_validare():
    """O nota ciorna e propunere, nu evidenta: constatarea ramane rosie pana la patru-ochi."""
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["stare"] == "rosu"
    assert r[0]["remediu"]["fel"] == "sugerat"
    assert "ciorn" in r[0]["remediu"]["cauza"]
    assert r[0]["remediu"]["facturi"] == []


def test_mixt_executabil_doar_pe_facturile_fara_nota():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("40"), "are_ciorna": True},
                 {"id": 2, "directie": "emisa", "tva": Decimal("34"), "are_ciorna": False}]
    r = compara_tva({"R17_2": 95, "R31_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["remediu"]["fel"] == "executabil"
    assert r[0]["remediu"]["facturi"] == [2]
    assert "ciorn" in r[0]["remediu"]["cauza"]


def test_o_factura_cu_ciorna_nu_intra_niciodata_intr_un_remediu_executabil():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True},
                 {"id": 2, "directie": "primita", "tva": Decimal("10"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R31_2": 10}, _rulaje(colectata=21, dedusa=0), necontate)
    for c in r:
        rem = c.get("remediu") or {}
        if rem.get("fel") == "executabil":
            assert 1 not in rem["facturi"] and 2 not in rem["facturi"]


# ---- F163: D112 vs contabilitate ----
from core.control_incrucisat import compara_d112, totaluri_d112_din_xml, COD_CONT_D112

def _rd(imp=0, cas=0, cass=0, cam=0):
    return {"444": {"credit": Decimal(str(imp)), "debit": Decimal("0")},
            "4315": {"credit": Decimal(str(cas)), "debit": Decimal("0")},
            "4316": {"credit": Decimal(str(cass)), "debit": Decimal("0")},
            "436": {"credit": Decimal(str(cam)), "debit": Decimal("0")}}


def test_d112_parseaza_totalurile_din_xml():
    xml = ('<angajatorA A_codOblig="602" A_codBugetar="X" A_datorat="100" A_plata="100"/>'
           '<angajatorA A_codOblig="412" A_codBugetar="X" A_datorat="250" A_plata="250"/>')
    t = totaluri_d112_din_xml(xml)
    assert t == {"602": 100, "412": 250}


def test_d112_coerent_da_verde():
    t = {"602": 100, "412": 250, "432": 100, "480": 22}
    r = compara_d112(t, _rd(imp=100, cas=250, cass=100, cam=22))
    assert [c["stare"] for c in r] == ["verde"] * 4


def test_d112_suprataxa_parttime_458_intra_in_4315():
    """458/459 se contabilizeaza tot in 4315/4316 (6451/6453) -> pereche 412+458."""
    t = {"602": 100, "412": 250, "458": 50, "432": 100, "459": 20, "480": 22}
    r = compara_d112(t, _rd(imp=100, cas=300, cass=120, cam=22))
    assert [c["stare"] for c in r] == ["verde"] * 4, [c["mesaj"] for c in r if c["stare"] != "verde"]


def test_d112_nu_verifica_brutul_421():
    """Brutul iese din F163: B_brutSalarii e baza de contributii, nu brut contabil."""
    assert all(cont != "421" for _e, _c, cont in COD_CONT_D112)


def test_d112_cod_lipsa_inseamna_zero_declarat():
    r = compara_d112({"602": 100}, _rd(imp=100))
    assert [c["stare"] for c in r] == ["verde"] * 4


def test_d112_stat_necontabilizat_da_executabil():
    r = compara_d112({"602": 100, "412": 250, "432": 100, "480": 22}, _rd())
    assert all(c["stare"] == "rosu" for c in r)
    assert all(c["remediu"]["fel"] == "executabil" for c in r)


def test_d112_ciorna_da_sugerat_nu_executabil():
    r = compara_d112({"602": 100, "412": 250, "432": 100, "480": 22}, _rd(), note_ciorna=1)
    assert all(c["remediu"]["fel"] == "sugerat" for c in r)
    assert all("ciorn" in c["remediu"]["cauza"] for c in r)


def test_d112_divergenta_partiala_da_investigatie_nu_ajustare():
    r = compara_d112({"602": 100, "412": 250, "432": 100, "480": 22},
                     _rd(imp=80, cas=250, cass=100, cam=22))
    assert r[0]["remediu"]["fel"] == "investigatie"
    assert "ajust" not in r[0]["remediu"]["actiune"].lower()


def test_d112_fiecare_constatare_isi_declara_temeiul():
    r = compara_d112({"602": 100}, _rd(imp=100))
    assert all(c["temei"] and "validate" in c["temei"] for c in r)


from core.control_incrucisat import toleranta_d112

def test_toleranta_creste_cu_efectivul():
    """D112 rotunjeste la leu, evidenta tine bani: fix 1 leu ar da rosu fals pe 40 salariati."""
    assert toleranta_d112(0) == Decimal("1")
    assert toleranta_d112(1) == Decimal("1")
    assert toleranta_d112(40) == Decimal("20")


def test_rotunjire_cam_nu_da_rosu_fals_pe_40_salariati():
    """CAM: 40 x 112.50 = 4500 in evidenta, D112 rotunjeste totalul -> 4499."""
    t = {"480": 4499, "602": 0, "412": 0, "432": 0}
    r = compara_d112(t, _rd(cam=4500), nr_salariati=40)
    cam = [c for c in r if c["eticheta"] == "CAM"][0]
    assert cam["stare"] == "verde", cam["mesaj"]


def test_toleranta_nu_ascunde_eroare_reala():
    """Un salariat lipsa din evidenta (112 lei CAM) depaseste toleranta pe 40 salariati."""
    t = {"480": 4612, "602": 0, "412": 0, "432": 0}
    r = compara_d112(t, _rd(cam=4500), nr_salariati=40)
    cam = [c for c in r if c["eticheta"] == "CAM"][0]
    assert cam["stare"] == "rosu", cam["mesaj"]


def test_temeiul_declara_toleranta():
    r = compara_d112({"602": 100}, _rd(imp=100), nr_salariati=40)
    assert "Toleranță 20" in r[0]["temei"] and "rotunj" in r[0]["temei"]
