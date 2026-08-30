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
    r = compara_tva({"R17_2": 21, "R27_2": 0}, _rulaje(colectata=21), 2026, 7)
    assert r[0]["stare"] == "verde"
    assert r[0]["remediu"] is None


def test_toleranta_1_leu_rotunjire_d300():
    # D300 rotunjeste la leu: 95 vs 94.50 contabil = coerent
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=Decimal("94.50")), 2026, 7)
    assert r[0]["stare"] == "verde"


def test_divergenta_explicata_de_facturi_necontate_da_remediu_executabil():
    necontate = [
        {"id": 2, "directie": "emisa", "tva": Decimal("21.00")},
        {"id": 3, "directie": "emisa", "tva": Decimal("52.50")},
    ]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["diferenta"] == Decimal("74")
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [2, 3]


def test_divergenta_neexplicata_da_investigatie_nu_ajustare():
    # diferenta NU se explica prin necontate -> investigatie, fara buton
    necontate = [{"id": 2, "directie": "emisa", "tva": Decimal("5.00")}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "investigatie"
    assert c["remediu"]["facturi"] == []
    # PRINCIPIU: nu propunem ajustarea contului ca sa dea verde
    txt = (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()
    assert "ajusteaz" not in txt and "modifica contul" not in txt


def test_fiecare_constatare_isi_declara_temeiul():
    r = compara_tva({"R17_2": 21, "R27_2": 0}, _rulaje(colectata=21), 2026, 7)
    for c in r:
        assert c["temei"]
        assert "D300" in c["temei"]


def test_temei_corect_pe_directie():
    r = compara_tva({"R17_2": 0, "R27_2": 0}, _rulaje(), 2026, 7)
    assert "emise" in r[0]["temei"]      # colectata <- facturi emise
    assert "primite" in r[1]["temei"]    # deductibila <- facturi primite


def test_deductibila_necontata_primite():
    necontate = [{"id": 9, "directie": "primita", "tva": Decimal("10.00")}]
    r = compara_tva({"R17_2": 0, "R27_2": 10}, _rulaje(dedusa=0), 2026, 7, necontate)
    c = r[1]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "executabil"
    assert c["remediu"]["facturi"] == [9]


def test_ciorna_nu_da_verde_asteapta_validare():
    """O nota ciorna e propunere, nu evidenta: constatarea ramane rosie pana la patru-ochi."""
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    assert r[0]["stare"] == "rosu"
    assert r[0]["remediu"]["fel"] == "sugerat"
    assert "ciorn" in r[0]["remediu"]["cauza"]
    assert r[0]["remediu"]["facturi"] == []


def test_mixt_executabil_doar_pe_facturile_fara_nota():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("40"), "are_ciorna": True},
                 {"id": 2, "directie": "emisa", "tva": Decimal("34"), "are_ciorna": False}]
    r = compara_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    assert r[0]["remediu"]["fel"] == "executabil"
    assert r[0]["remediu"]["facturi"] == [2]
    assert "ciorn" in r[0]["remediu"]["cauza"]


def test_o_factura_cu_ciorna_nu_intra_niciodata_intr_un_remediu_executabil():
    necontate = [{"id": 1, "directie": "emisa", "tva": Decimal("74"), "are_ciorna": True},
                 {"id": 2, "directie": "primita", "tva": Decimal("10"), "are_ciorna": True}]
    r = compara_tva({"R17_2": 95, "R27_2": 10}, _rulaje(colectata=21, dedusa=0), 2026, 7, necontate)
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

def test_linie_cota_neparsabila_declarata_in_limita_nu_gri_global():
    # o linie cu cota neparsabila NU face verdictul gri global (ar ascunde verdele real pe restul); e
    # contorizata si declarata in limita. Verdictul ramane pe ce s-a putut verifica.
    r = constatare_cota_tva([_linie(1, _date(2025, 9, 10), 21),     # corecta -> verde
                             _linie(2, _date(2025, 9, 10), "N/A")], 2025, 9)  # neparsabila -> sarita
    assert r["stare"] == "verde"                                    # NU gri global
    assert "neparsabil" in r["limita"] and "1 linie" in r["limita"]

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
    assert "Legea 141/2025" in c["temei"] and "redus" in c["temei"].lower()  # cota redusă (11%) unică, nu 9/5
    assert "NEVERIFICAT" in r["limita"]


# ============================================================
#  F163 D-vs-D REAL (deblocat F198): D390 vs D300 DEPUS (compara_d390_vs_d300)
# ============================================================
from core.control_incrucisat import (compara_d390_vs_d300, _d300_depus_randuri,
                                     _d300_depus_recent, verifica_d390)


def _randuri(**R):
    """randuri persistat al unui D300 depus, cu dict-ul R (chei R1_1/R5_1 -> int)."""
    return {"R": {k: v for k, v in R.items()}}


def test_dvsd_rosu_d390_livrare_d300_fara_R1_1():
    # D390 livrări 5000, D300 depus FĂRĂ R1_1 (manual-only neintrodus) -> ROȘU sugerat
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=True, randuri=_randuri())
    liv = [c for c in r if c["eticheta"].startswith("Livrări")][0]
    assert liv["stare"] == "rosu"
    assert liv["remediu"]["fel"] == "sugerat"
    assert "R1_1 absent" in liv["temei"] and "manual-only" in liv["temei"]   # contabilul vede CAUZA


def test_dvsd_verde_ambele_5000():
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=True, randuri=_randuri(R1_1=5000))
    liv = [c for c in r if c["eticheta"].startswith("Livrări")][0]
    assert liv["stare"] == "verde" and liv["remediu"] is None


def test_dvsd_gri_pe_cifre_diferite():
    # ambele > 0 dar diferite -> GRI (decalaj exigibilitate), NICIODATĂ roșu pe cifre
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=True, randuri=_randuri(R1_1=4000))
    liv = [c for c in r if c["eticheta"].startswith("Livrări")][0]
    assert liv["stare"] == "gri"
    assert "exigibilitate" in liv["temei"] and liv["remediu"] is None


def test_dvsd_gri_pe_randuri_null():
    # D300 depus dar fără rânduri persistate (pre-F198 / import) -> GRI, nu roșu
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=True, randuri=None)
    assert len(r) == 1 and r[0]["stare"] == "gri"
    assert "fără rânduri persistate" in r[0]["mesaj"]


def test_dvsd_gri_pe_zero_depuneri():
    # niciun D300 depus în fereastră -> GRI, nu roșu
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=False, randuri=None)
    assert len(r) == 1 and r[0]["stare"] == "gri"
    assert "Nu există D300 depus" in r[0]["mesaj"]


def test_dvsd_ambele_zero_tacut():
    r = compara_d390_vs_d300({"L": 0, "A": 0}, gasit=True, randuri=_randuri())
    assert r == []                                             # tăcut


def test_dvsd_achizitii_R5_1():
    # achiziții: D390 A=3000 vs D300 R5_1 absent -> ROȘU pe achiziții
    r = compara_d390_vs_d300({"L": 0, "A": 3000}, gasit=True, randuri=_randuri())
    ach = [c for c in r if c["eticheta"].startswith("Achiziții")][0]
    assert ach["stare"] == "rosu" and "R5_1 absent" in ach["temei"]


# --- DB: _d300_depus_randuri prin depunere d300 FABRICATA in ROLLBACK. DECUPLAT de tenant_002
# persistent (29.07): _d300_depus_* mapeaza schema->id prin public.tenants (SELECT id ... WHERE
# schema_name=%s), deci fabricam SI un rand tenants sintetic in aceeasi tranzactie cu ROLLBACK.
# Nu depinde de nicio firma din baza. Vezi DECIZII 29.07.
import psycopg2.extras as _E
from core import db as _db
from core import tenant_provisioning as _tp


def _conn():
    _db.init_pool(); return _db.pool().getconn()


def _tenant_fabricat(cur, schema_name):
    """Rand public.tenants SINTETIC -> id, ca _d300_depus_* sa mapeze schema->id fara tenant real."""
    cur.execute("INSERT INTO public.tenants (schema_name, nume) VALUES (%s, 'PROBA CI') RETURNING id",
                (schema_name,))
    return cur.fetchone()[0]


def test_d300_depus_randuri_citeste_depunere_fabricata():
    # perioada SINTETICA (2099) ca sa nu coincida cu depuneri reale (PK tenant/an/luna/tip/nr)
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _tenant_fabricat(cur, "ztest_ci")
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
                        "VALUES (%s, 2099, 6, 'd300', '<x/>', %s, 1)",
                        (tid, _E.Json({"R": {"R1_1": 5000, "R5_1": 3000}})))
            gasit, randuri = _d300_depus_randuri(conn, "ztest_ci", 2099, 6)
        assert gasit is True
        assert randuri["R"]["R1_1"] == 5000 and randuri["R"]["R5_1"] == 3000
    finally:
        conn.rollback(); _db.pool().putconn(conn)


def test_d300_depus_randuri_null_si_zero_depuneri():
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _tenant_fabricat(cur, "ztest_ci")
        # zero depuneri d300 in 2099/7 (sintetic) -> gasit False
        with conn.cursor() as cur:
            g0, r0 = _d300_depus_randuri(conn, "ztest_ci", 2099, 7)
        assert g0 is False and r0 is None
        # depunere cu randuri NULL -> gasit True, randuri None
        with conn.cursor() as cur:
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
                        "VALUES (%s, 2099, 7, 'd300', '<x/>', NULL, 1)", (tid,))
            g1, r1 = _d300_depus_randuri(conn, "ztest_ci", 2099, 7)
        assert g1 is True and r1 is None
    finally:
        conn.rollback(); _db.pool().putconn(conn)


# ============================================================
#  F163 D-vs-D: fereastra PROPRIE = cea mai recenta perioada depusa (reparat gri permanent, 23.07).
#  Latura D390-vs-evidenta ramane pe luna curenta; D-vs-D isi alege perioada cu D300 depus.
# ============================================================
import pytest


def test_dvsd_perioada_afisata_in_eticheta():
    # perioada evaluata (alta decat restul ecranului) TREBUIE sa apara explicit in verdict.
    r = compara_d390_vs_d300({"L": 5000, "A": 0}, gasit=True, randuri=_randuri(R1_1=5000), perioada="06/2026")
    liv = [c for c in r if c["eticheta"].startswith("Livrări")][0]
    assert "perioada 06/2026" in liv["eticheta"]
    assert "perioada 06/2026" in liv["mesaj"]      # mesajul e derivat din eticheta


def test_fereastra_tva_reconstruieste_trimestrul_din_luna_depusa():
    # D300 trimestrial se depune cu luna = ultima luna a trimestrului (coada_api: trim*3). Fereastra
    # D-vs-D reconstruieste cele 3 luni din acea luna -> baza D390 recalculata pe TOT trimestrul.
    luni, de, pana, et = _fereastra_tva("trimestrial", 2026, 6)
    assert luni == [4, 5, 6] and et == "trimestrul 2/2026"
    assert de == "2026-04-01" and pana == "2026-07-01"


def test_d300_depus_recent_alege_cea_mai_recenta():
    # mai multe depuneri d300 sintetice -> _d300_depus_recent ia (an DESC, luna DESC). 2099 domina realul.
    conn = _conn()
    try:
        with conn.cursor() as cur:
            tid = _tenant_fabricat(cur, "ztest_ci")
            for an, luna in ((2098, 12), (2099, 3), (2099, 6)):
                cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
                            "VALUES (%s, %s, %s, 'd300', '<x/>', %s, 1)",
                            (tid, an, luna, _E.Json({"R": {"R1_1": an}})))
            rec = _d300_depus_recent(conn, "ztest_ci")
        assert rec is not None
        an_d, luna_d, randuri_d = rec
        assert (an_d, luna_d) == (2099, 6) and randuri_d["R"]["R1_1"] == 2099
    finally:
        conn.rollback(); _db.pool().putconn(conn)


def test_d300_depus_recent_none_pe_schema_inexistenta():
    conn = _conn()
    try:
        assert _d300_depus_recent(conn, "tenant_inexistent_9999") is None
    finally:
        conn.rollback(); _db.pool().putconn(conn)


def test_verifica_d390_dvsd_foloseste_perioada_depusa_nu_luna_curenta():
    # DECUPLAT (29.07): schema efemera + tenants sintetic + D300 depus (2026/6) fabricat, tot in ROLLBACK.
    # Verificat pe luna CURENTA (iulie, fara D300 depus) -> D-vs-D NU mai e gri „nicio depunere", ci
    # compara pe perioada efectiv depusa (06/2026), afisata in eticheta.
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS ztest_ci_d390 CASCADE")
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), "ztest_ci_d390"))
            cur.execute("INSERT INTO ztest_ci_d390.firma_profil (id, nume, cui, platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie) "
                        "VALUES (1, 'PROBA CI', '14399840', true, 'L', 'Popescu', 'Ion', 'ADMINISTRATOR')")
            tid = _tenant_fabricat(cur, "ztest_ci_d390")
            # fixtura-sintetica-ok: tenant_id sintetic (nu coliziune PK cu depunere reala)
            cur.execute("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, xml, randuri, nr_depunere) "
                        "VALUES (%s, 2026, 6, 'd300', '<x/>', %s, 1)", (tid, _E.Json({"R": {"R1_1": 5000}})))
            # d390.calculeaza (chemat de verifica_d390) interogheaza firma_profil NECALIFICAT ->
            # search_path pe schema efemera. SET LOCAL = anulat de rollback, nu polueaza pool-ul.
            cur.execute("SET LOCAL search_path TO ztest_ci_d390, public")
            rec = _d300_depus_recent(conn, "ztest_ci_d390")
            assert rec is not None, "depunerea fabricata trebuie vazuta (decuplare corecta)"
            r = verifica_d390(conn, "ztest_ci_d390", 2026, 7)   # iulie = luna curenta, fara D300 depus
    finally:
        conn.rollback(); _db.pool().putconn(conn)
    dvsd = [c for c in r["constatari"] if "D300 depus" in c["eticheta"]]
    assert dvsd, "sub-verificarea D-vs-D lipseste"
    assert all("Nicio depunere" not in c["mesaj"] for c in dvsd)   # a iesit din gri-ul permanent
    an_d, luna_d, _ = rec
    et = "%02d/%d" % (luna_d, an_d)
    assert any(("perioada %s" % et) in c["eticheta"] for c in dvsd)


# ---- garda salariati pe verifica_d112 (fara salariati -> absent, nu verde pe 0-vs-0) ----
from core.control_incrucisat import verifica_d112 as _verifica_d112, verifica_tva as _verifica_tva

# REGULA (nu cazul): un verificator declarat-vs-contabil al carui SUBIECT nu exista (fara salariati,
# neplatitor TVA, ...) NU produce verdict -> absent, nu verde pe 0-vs-0. Verdele = "am verificat, e ok";
# fara subiect n-a verificat nimic. Cate un test pe fiecare verificator atins.
def test_verifica_d112_fara_salariati_e_absent_nu_verde():
    # DECUPLAT (29.07): schema efemera cu firma_profil (PFA), tabela salariati GOALA -> nr_sal=0.
    # d112.genereaza ruleaza pe schema (calificat + SET LOCAL pt orice acces necalificat), tot in ROLLBACK.
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS ztest_ci_d112 CASCADE")
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), "ztest_ci_d112"))
            cur.execute("INSERT INTO ztest_ci_d112.firma_profil (id, nume, cui, platitor_tva, declarant_nume, declarant_prenume, declarant_functie) "
                        "VALUES (1, 'PROBA CI PFA', '14399840', false, 'Popescu', 'Ion', 'ADMINISTRATOR')")
            cur.execute("SET LOCAL search_path TO ztest_ci_d112, public")
            v = _verifica_d112(conn, "ztest_ci_d112", 2026, 7)   # fara salariati -> subiect inexistent
        assert v["constatari"] == []                      # absent, nu verde
        assert "nu se datorează" in v["limita"]
    finally:
        conn.rollback(); _db.pool().putconn(conn)

def test_verifica_tva_neplatitor_e_absent_nu_verde():
    # DECUPLAT (29.07): schema efemera cu firma_profil platitor_tva=false -> garda "neplatitor"
    # intoarce INAINTE de orice generare D300. Tot in ROLLBACK, fara firma persistenta.
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS ztest_ci_tva CASCADE")
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), "ztest_ci_tva"))
            cur.execute("INSERT INTO ztest_ci_tva.firma_profil (id, nume, cui, platitor_tva, declarant_nume, declarant_prenume, declarant_functie) "
                        "VALUES (1, 'PROBA CI', '14399840', false, 'Popescu', 'Ion', 'ADMINISTRATOR')")
            v = _verifica_tva(conn, "ztest_ci_tva", 2026, 7)    # neplatitor TVA -> D300 fara subiect
        assert v["constatari"] == []                      # absent, NU verde "coincid" pe 0-vs-0
        assert "neplătitoare de TVA" in v["limita"]
    finally:
        conn.rollback(); _db.pool().putconn(conn)


# ============================================================
#  C2 (intre documente): fluturas <-> D112, prin ARTEFACTUL contabil.
#  Fluturasul (stat_plata_api) si D112 IMPART salarizare.calcul_salariu -> un compare DIRECT pe formula e TAUTOLOGIE
#  (ambele documente citesc aceeasi functie). A DOUA CALE REALA e artefactul contabil: ce s-a BOOKAT in ledger
#  (rulaje credit 4315/4316/436/444) vs ce DECLARA D112 in XML-ul emis (angajatorA A_datorat). control_incrucisat.
#  compara_d112 confrunta cele doua ARTEFACTE. Era NETESTAT -> divergenta CM de azi (D112 pe brut intreg vs ledger pe
#  brut_lucrat) trecea semaforul. Gardat aici cu mutatie.
# ============================================================
from core.control_incrucisat import compara_d112


def test_compara_d112_verde_cand_declaratia_coincide_cu_ledgerul():
    tot = {"602": 800, "412": 1500, "432": 600, "480": 135}   # D112 declarat (din XML)
    rul = {"444": {"credit": 800}, "4315": {"credit": 1500}, "4316": {"credit": 600}, "436": {"credit": 135}}
    rez = compara_d112(tot, rul, nr_salariati=1)
    assert all(c["stare"] == "verde" for c in rez), rez


def test_compara_d112_prinde_divergenta_declaratie_vs_ledger_MUTATIE():
    """MUTATIE: D112 declara CAS 2000 (supra-declarat pe brut intreg - exact tiparul bug-ului CM de azi) dar ledger-ul
    are 1500 (bookat pe brut_lucrat) -> compara_d112 da ROSU pe CAS, restul raman verzi. Dovada ca a doua cale
    (artefact D112 vs artefact contabil) prinde divergenta pe care fluturas-vs-D112 direct (tautologic) n-ar prinde-o."""
    tot = {"602": 800, "412": 1500, "432": 600, "480": 135}
    rul = {"444": {"credit": 800}, "4315": {"credit": 1500}, "4316": {"credit": 600}, "436": {"credit": 135}}
    tot_bug = dict(tot); tot_bug["412"] = 2000
    rez = compara_d112(tot_bug, rul, nr_salariati=1)
    cas = [c for c in rez if c["eticheta"] == "CAS"][0]
    assert cas["stare"] == "rosu", cas
    assert cas["diferenta"] == 500, cas["diferenta"]
    assert all(c["stare"] == "verde" for c in rez if c["eticheta"] != "CAS"), rez


def test_c2_d112_confrunta_artefacte_nu_recalculeaza_NON_TAUTOLOGIE():
    """[non-tautologie C2] Perechea nu e proba daca ambele parti recalculeaza cu aceeasi functie. compara_d112 +
    totaluri_d112_din_xml confrunta ARTEFACTUL D112 (parse din XML-ul EMIS) cu rulajele din ledger - NU apeleaza
    calcul_salariu/taxe_cm/calcul_cm/pull. Verificat pe AST. Asa, chiar daca upstream fluturas+D112 impart
    calcul_salariu, confruntarea se face pe doua ARTEFACTE independente (declaratia emisa vs registrul contabil)."""
    import ast, inspect
    from core import control_incrucisat as _ci
    interzis = {"calcul_salariu", "taxe_cm", "calcul_cm", "pull"}
    for fn in (_ci.compara_d112, _ci.totaluri_d112_din_xml):
        src = inspect.getsource(fn)
        t = ast.parse(src)
        nume = {n.id for n in ast.walk(t) if isinstance(n, ast.Name)}
        attrs = {n.attr for n in ast.walk(t) if isinstance(n, ast.Attribute)}
        gasit = (nume | attrs) & interzis
        assert not gasit, ("%s recalculeaza contributii %s - ar fi tautologie, nu confruntare de artefacte"
                           % (fn.__name__, gasit))
    # cele doua surse SUNT diferite: D112 din regex pe XML (artefact emis), ledger din dict (rulaje din registru)
    assert "finditer" in inspect.getsource(_ci.totaluri_d112_din_xml), "totalurile D112 trebuie parsate din XML-ul EMIS"


# ============================================================
#  #18 — remediu PRECIS pe PerioadaNeconfirmata (nu mesajul generic "Date lipsă")
#  #19 — formularea remediului reflectă four-eyes REAL (nu presupune mereu activat)
# ============================================================
from core.control_incrucisat import compara_tva as _c_tva, compara_d112 as _c_d112, compara_d390 as _c_d390


class _FakeCur:
    def __init__(self, row): self._row = row
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def execute(self, *a, **k): pass
    def fetchone(self): return self._row


class _FakeConn:
    """Conn minimal: fetchone întoarce mereu `row` (destul cât să treacă de garda platitor_tva)."""
    def __init__(self, row): self._row = row
    def cursor(self, *a, **k): return _FakeCur(self._row)


def test_d112_perioada_neconfirmata_da_cauza_precisa(monkeypatch):
    from core import d112 as _d112
    from core.perioada import PerioadaNeconfirmata
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise PerioadaNeconfirmata("Tichetele de masă (D112)", 2026, 8, "pontaj", "HG 1045/2018 art.10(3)")
    monkeypatch.setattr(_d112, "genereaza", _boom)
    r = _ci.verifica_d112(None, "tenant_x", 2026, 8)
    rem = r["constatari"][0]["remediu"]
    assert "CONFIRMAT" in rem["cauza"] and "pontaj" in rem["cauza"].lower()
    assert "Date lips" not in rem["cauza"]           # NU mai contrazice explicația precisă
    assert rem["actiune"] == "Confirmă pontajul lunii (rol admin_firma)."


def test_d112_exceptie_necunoscuta_pastreaza_remediu_generic(monkeypatch):
    from core import d112 as _d112
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise RuntimeError("cu totul altceva")
    monkeypatch.setattr(_d112, "genereaza", _boom)
    r = _ci.verifica_d112(None, "tenant_x", 2026, 8)
    rem = r["constatari"][0]["remediu"]
    assert rem["cauza"] == "Date lipsă sau profil incomplet."
    assert rem["actiune"].startswith("Completează profilul")


def test_tva_perioada_neconfirmata_da_cauza_precisa(monkeypatch):
    from core import d300 as _d300
    from core.perioada import PerioadaNeconfirmata
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise PerioadaNeconfirmata("Decontul (D300)", 2026, 8, "TVA", "")
    monkeypatch.setattr(_d300, "genereaza", _boom)
    r = _ci.verifica_tva(_FakeConn((True,)), "tenant_x", 2026, 8)   # platitor_tva=True -> nu iese pe gardă
    rem = r["constatari"][0]["remediu"]
    assert "CONFIRMAT" in rem["cauza"]
    assert "Date lips" not in rem["cauza"]
    assert rem["actiune"] == "Confirmă perioada lunii (rol admin_firma)."


def test_tva_exceptie_necunoscuta_pastreaza_remediu_generic(monkeypatch):
    from core import d300 as _d300
    from core import control_incrucisat as _ci
    def _boom(*a, **k):
        raise RuntimeError("cu totul altceva")
    monkeypatch.setattr(_d300, "genereaza", _boom)
    r = _ci.verifica_tva(_FakeConn((True,)), "tenant_x", 2026, 8)
    rem = r["constatari"][0]["remediu"]
    assert rem["cauza"] == "Date lipsă sau profil fiscal incomplet."


def test_tva_four_eyes_activ_vs_neactivat_text_diferit():
    necontate = [{"directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    args = ({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    activ = _c_tva(*args, patru_ochi=True)[0]["remediu"]["actiune"]
    neact = _c_tva(*args, patru_ochi=False)[0]["remediu"]["actiune"]
    assert "patru ochi" in activ and "al doilea utilizator" in activ
    assert "patru ochi" not in neact and "al doilea utilizator" not in neact
    assert neact == "Validează nota (din ciornă în evidență)."


def test_d112_four_eyes_neactivat_nu_promite_al_doilea_utilizator():
    args = ({"602": 100, "412": 250, "432": 100, "480": 22}, _rd())
    activ = _c_d112(*args, note_ciorna=1, patru_ochi=True)[0]["remediu"]["actiune"]
    neact = _c_d112(*args, note_ciorna=1, patru_ochi=False)[0]["remediu"]["actiune"]
    assert "al doilea utilizator" in activ
    assert neact == "Validează nota (din ciornă în evidență)."


def test_d390_four_eyes_neactivat_scoate_mentiunea_patru_ochi():
    ic = {"emisa": [], "primita": [_fic(7, "primita", 500, 105)]}
    ca = [x for x in _c_d390({"L": 0, "A": 500}, ic, patru_ochi=True)
          if x["eticheta"].startswith("Achiziții")][0]["remediu"]["actiune"]
    cn = [x for x in _c_d390({"L": 0, "A": 500}, ic, patru_ochi=False)
          if x["eticheta"].startswith("Achiziții")][0]["remediu"]["actiune"]
    assert "patru ochi" in ca and "patru ochi" not in cn
    assert "notă validată" in cn


def test_four_eyes_default_true_nu_sparge_apelantii_existenti():
    # semnătura veche (fără patru_ochi) rămâne validă și dă formularea prudentă
    necontate = [{"directie": "emisa", "tva": Decimal("74"), "are_ciorna": True}]
    a = _c_tva({"R17_2": 95, "R27_2": 0}, _rulaje(colectata=21), 2026, 7, necontate)
    assert "al doilea utilizator" in a[0]["remediu"]["actiune"]


def test_contul_4428_cu_sold_e_un_fapt_cu_perioada():
    """CALEA CARE CĂDEA ÎN TĂCERE (21.08.2026). Ramura contului 4428 n-avea NICIUN test — `_rulaje()`
    nu produce 4428 — deci când `an`/`luna` au fost puse opționale „ca să nu ating testele pure",
    ramura a început să ridice `AfirmatieIncompleta` și suita a rămas verde peste o cădere.

    Un fapt despre datele firmei ARE o perioadă; semnătura o cere acum, nu o speră."""
    from core.afirmatii import FELURI
    r = compara_tva({"R17_2": 0, "R27_2": 0}, {"4428": {"credit": 500, "debit": 0}}, 2026, 7)
    c = next(x for x in r if "4428" in x["eticheta"])
    assert c["stare"] == "gri" and c["fel"] == "fapt"
    assert c["an"] == 2026 and c["luna"] == 7, "faptul nu poartă perioada pe care o afirmă"
    for camp in FELURI["fapt"]:
        assert camp in c, "constatarea 4428 nu e o afirmație validă: lipsește %s" % camp
    assert c["mesaj"] == c["motiv"], "textul s-a despărțit în două surse"
