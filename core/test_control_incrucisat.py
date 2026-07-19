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
    r = compara_tva({"R17_2": 21, "R27_2": 0}, _rulaje(colectata=21))
    assert r[0]["stare"] == "verde"
    assert r[0]["remediu"] is None


def test_toleranta_1_leu_rotunjire_d300():
    # D300 rotunjeste la leu: 95 vs 94.50 contabil = coerent
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=Decimal("94.50")))
    assert r[0]["stare"] == "verde"


def test_divergenta_explicata_de_facturi_necontate_da_remediu_executabil():
    necontate = [
        {"id": 2, "directie": "emisa", "tva": Decimal("21.00")},
        {"id": 3, "directie": "emisa", "tva": Decimal("52.50")},
    ]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["diferenta"] == Decimal("74")
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [2, 3]


def test_divergenta_neexplicata_da_investigatie_nu_ajustare():
    # diferenta NU se explica prin necontate -> investigatie, fara buton
    necontate = [{"id": 2, "directie": "emisa", "tva": Decimal("5.00")}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "investigatie"
    assert c["remediu"]["facturi"] == []
    # PRINCIPIU: nu propunem ajustarea contului ca sa dea verde
    txt = (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()
    assert "ajusteaz" not in txt and "modifica contul" not in txt


def test_fiecare_constatare_isi_declara_temeiul():
    r = compara_tva({"R17_2": 21, "R27_2": 0}, _rulaje(colectata=21))
    for c in r:
        assert c["temei"]
        assert "D300" in c["temei"]


def test_temei_corect_pe_directie():
    r = compara_tva({"R17_2": 0, "R27_2": 0}, _rulaje())
    assert "emise" in r[0]["temei"]      # colectata <- facturi emise
    assert "primite" in r[1]["temei"]    # deductibila <- facturi primite


def test_deductibila_necontata_primite():
    necontate = [{"id": 9, "directie": "primita", "tva": Decimal("10.00")}]
    r = compara_tva({"R17_2": 0, "R27_2": 10}, _rulaje(dedusa=0), necontate)
    c = r[1]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [9]


def test_ciorna_nu_da_verde_asteapta_validare():
    """O nota ciorna e propunere, nu evidenta: constatarea ramane rosie pana la patru-ochi."""
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["stare"] == "rosu"
    assert r[0]["remediu"]["fel"] == "sugerat"
    assert "ciorn" in r[0]["remediu"]["cauza"]
    assert r[0]["remediu"]["facturi"] == []


def test_mixt_executabil_doar_pe_facturile_fara_nota():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("40"), "are_ciorna": True},
                 {"id": 2, "directie": "emisa", "tva": Decimal("34"), "are_ciorna": False}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), necontate)
    assert r[0]["remediu"]["fel"] == "executabil"
    assert r[0]["remediu"]["facturi"] == [2]
    assert "ciorn" in r[0]["remediu"]["cauza"]


def test_o_factura_cu_ciorna_nu_intra_niciodata_intr_un_remediu_executabil():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True},
                 {"id": 2, "directie": "primita", "tva": Decimal("10"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R27_2": 10}, _rulaje(colectata=21, dedusa=0), necontate)
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


# ---- F163: D390 (bunuri IC) vs EVIDENȚA contabilă validată ----
# NU e D-vs-D (rândurile R1_1/R5_1 ale D300 sunt manual-only, nepersistate — vezi DECIZII 19.07).
# Regula direcțională: declarat la VIES DAR absent din evidența validată = ROȘU; invers = GRI;
# cifre diferite = GRI (niciodată roșu pe cifre); ambele 0 = tăcut.
from core.control_incrucisat import compara_d390, _fereastra_tva


def _fic(id, directie, total, tva, contab=False, ciorna=False):
    return {"id": id, "numar": "F%d" % id, "directie": directie,
            "total": Decimal(str(total)), "tva": Decimal(str(tva)),
            "contabilizata": contab, "are_ciorna": ciorna}


def test_d390_ambele_zero_nimic_de_raportat():
    r = compara_d390({"L": 0, "A": 0}, {"emisa": [], "primita": []})
    assert r == []


def test_d390_coerent_da_verde():
    # o livrare IC de 1000 (total 1000, tva 0 — scutit), contabilizată -> D390 L=1000 vs evidență 1000
    ic = {"emisa": [_fic(1, "emisa", 1000, 0, contab=True)], "primita": []}
    r = compara_d390({"L": 1000, "A": 0}, ic)
    assert len(r) == 1 and r[0]["stare"] == "verde" and r[0]["remediu"] is None


def test_d390_declarat_la_vies_absent_din_evidenta_da_rosu_sugerat():
    # ROȘU direcțional: D390 declară achiziții IC, dar factura nu are notă validată
    ic = {"emisa": [], "primita": [_fic(7, "primita", 500, 105)]}  # 500 bază, necontabilizată
    r = compara_d390({"L": 0, "A": 500}, ic)
    c = [x for x in r if x["eticheta"].startswith("Achiziții")][0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "sugerat"          # corecția e în contabilitate SAU recapitulativă
    assert c["remediu"]["facturi"] == [7]
    assert "VIES" in c["remediu"]["cauza"]


def test_d390_evidenta_fara_vies_da_gri_nu_rosu():
    # INVERS: în evidența validată apar achiziții IC, dar D390=0 -> GRI (decalaj posibil), NU roșu
    ic = {"emisa": [], "primita": [_fic(3, "primita", 800, 168, contab=True)]}
    r = compara_d390({"L": 0, "A": 0}, ic)
    c = [x for x in r if x["eticheta"].startswith("Achiziții")][0]
    assert c["stare"] == "gri"
    assert c["remediu"]["fel"] == "investigatie"


def test_d390_cifre_diferite_ambele_pozitive_da_gri_nu_rosu():
    # ambele > 0 dar diferite -> GRI (decalaj exigibilitate/regularizări/rotunjire = legitim)
    ic = {"emisa": [], "primita": [_fic(4, "primita", 600, 126, contab=True)]}  # evidență 600
    r = compara_d390({"L": 0, "A": 900}, ic)                                     # D390 declară 900
    c = [x for x in r if x["eticheta"].startswith("Achiziții")][0]
    assert c["stare"] == "gri"
    assert c["remediu"]["fel"] == "investigatie"
    # PRINCIPIU: nu se propune ajustarea contului
    assert "ajust" not in (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()


def test_d390_ciorna_nu_conteaza_ca_evidenta():
    # factura cu notă CIORNĂ (nevalidată) -> tot ROȘU (ciorna nu e dovadă)
    ic = {"emisa": [], "primita": [_fic(9, "primita", 500, 105, contab=False, ciorna=True)]}
    r = compara_d390({"L": 0, "A": 500}, ic)
    c = [x for x in r if x["eticheta"].startswith("Achiziții")][0]
    assert c["stare"] == "rosu"
    assert "ciorn" in c["remediu"]["cauza"]
    assert c["remediu"]["facturi"] == [9]


def test_d390_toleranta_rotunjire_leu():
    # D390 rotunjește la leu; 1000 vs 999.50 în evidență = coerent
    ic = {"emisa": [_fic(1, "emisa", Decimal("999.50"), 0, contab=True)], "primita": []}
    r = compara_d390({"L": 1000, "A": 0}, ic)
    assert r[0]["stare"] == "verde"


def test_d390_temei_si_limita_pe_fiecare_constatare():
    ic = {"emisa": [], "primita": [_fic(7, "primita", 500, 105)]}
    r = compara_d390({"L": 0, "A": 500}, ic)
    for c in r:
        assert "art. 325" in c["temei"]                 # temei legal recapitulativă
        assert "doar BUNURI" in c["temei"]              # limită explicită servicii
        assert "D300 depus" in c["temei"]               # limită explicită D-vs-D


def test_fereastra_lunar_o_luna():
    luni, de, pana, et = _fereastra_tva("lunar", 2026, 3)
    assert luni == [3] and de == "2026-03-01" and pana == "2026-04-01"


def test_fereastra_trimestrial_trei_luni():
    # firmă trimestrială: luna 8 -> trimestrul 3 (iul-sep), fereastră [07-01, 10-01)
    luni, de, pana, et = _fereastra_tva("trimestrial", 2026, 8)
    assert luni == [7, 8, 9] and de == "2026-07-01" and pana == "2026-10-01"
    assert "trimestrul 3" in et


def test_fereastra_trimestrial_decembrie_trece_anul():
    luni, de, pana, et = _fereastra_tva("T", 2026, 12)
    assert luni == [10, 11, 12] and de == "2026-10-01" and pana == "2027-01-01"


# ---- F184: conformitate cota TVA facturi emise (value-aware, wrapper peste verifica_tva_pe_cota) ----
from core.control_incrucisat import constatare_cota_tva
from datetime import date as _date

def _linie(id, data, cota, cant=1, pret=1000):
    return {"id": id, "numar": "F%d" % id, "data_emitere": data,
            "cantitate": cant, "pret_unitar": pret, "cota_tva": cota}

def test_cota_veche_dupa_schimbare_da_rosu():
    # 19% pe o factura din 09/2025 (standard = 21% de la 01.08.2025) -> ROSU
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 19)], 2025, 9)
    assert r["stare"] == "rosu"
    c = r["constatari"][0]
    assert c["remediu"]["fel"] == "sugerat" and c["remediu"]["facturi"] == [1]
    assert "19% în loc de 21%" in c["mesaj"]

def test_cota_corecta_pe_perioada_da_verde():
    # 21% pe o factura din 09/2025 -> VERDE
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 21)], 2025, 9)
    assert r["stare"] == "verde"

def test_cota_veche_dar_inainte_de_schimbare_da_verde():
    # 19% pe o factura din 06/2025 (standard era inca 19%) -> VERDE (period-corect)
    r = constatare_cota_tva([_linie(1, _date(2025, 6, 10), 19)], 2025, 6)
    assert r["stare"] == "verde"

def test_cota_redusa_9_nu_e_fals_pozitiv():
    # 9% (cota redusa) dupa 01.08.2025 -> IGNORAT, nu rosu (nu e in familia standard)
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 9)], 2025, 9)
    assert r["stare"] == "verde"          # nicio linie standard verificata cu problema
    assert r["constatari"] == []          # 0 linii standard -> tacit

def test_scutit_0_ignorat():
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 0)], 2025, 9)
    assert r["stare"] == "verde" and r["constatari"] == []

def test_mix_prinde_doar_linia_gresita():
    # factura 1: 19% gresit; factura 2: 21% corect; factura 3: 9% redus (ignorat)
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 1), 19),
                             _linie(2, _date(2025, 9, 2), 21),
                             _linie(3, _date(2025, 9, 3), 9)], 2025, 9)
    assert r["stare"] == "rosu"
    assert r["constatari"][0]["remediu"]["facturi"] == [1]   # doar 1

def test_temei_si_limita_declarate():
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 19)], 2025, 9)
    c = r["constatari"][0]
    assert "Legea 141/2025" in c["temei"] and "reduse" in c["temei"].lower()
    assert "NEVERIFICAT" in r["limita"]
