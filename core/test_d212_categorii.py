# -*- coding: utf-8 -*-
"""D212 Etapa 5 — veniturile fără date în aplicație (Subsecțiunea I.1.1 pe categorii), CAS cu DPI, CASS 2.2 pe trepte,
Secțiunea 5 și sumarul I.7. Sursa rândurilor: instrucțiunile D212 (OPANAF 2736/2025) Subsecțiunea 1 pct.4-9, Secțiunea 3
pct.46/52, Secțiunile 5 și 7; valorile fiscale: Codul fiscal, citat pe linie. Validatorul instalat (J13.0.1) e judecătorul
structurii: secțiunile cap11 repetate trec DUK."""
import pathlib
import re
import xml.etree.ElementTree as ET

import pytest

from core import d212, d212_engine as e
from core.common import Perioada

ID = {"cif": "1800101221144", "nume_c": "POPESCU ION", "adresa_c": "Bucuresti Sector 1"}
RAD = pathlib.Path(__file__).resolve().parent.parent


def _cat(**a):
    return d212.cap11_categorie(a, 2025)


def test_dpi_cote_forfetare_40_la_suta():
    c = _cat(categ_venit=1003, det_ven_net=2, venit_brut=30000)
    # CF art.72^1 alin.(1): „cheltuielilor determinate prin aplicarea cotei de 40% asupra venitului brut”
    assert (c["chelt_deduc"], c["venit_net_anual"], c["venit_recalculat"]) == (12000, 18000, 18000)
    # CF art.64 alin.(1) lit.a^1): 10%; instrucțiuni pct.4.5.9 rd.9 = 10% x rd.7
    assert c["impozit11"] == 1800 and c["det_ven_net"] == 2 and "pierdere" not in c


def test_dpi_mostenitor_fara_cota():
    # CF art.72^1 alin.(2): moștenitori / drept de suită — „fără aplicarea cotei forfetare de cheltuieli”
    c = _cat(categ_venit=1003, det_ven_net=2, venit_brut=30000, chelt_deduc=3000, fara_cota_forfetara=True)
    assert (c["chelt_deduc"], c["venit_net_anual"], c["impozit11"]) == (3000, 27000, 2700)
    with pytest.raises(ValueError, match="se calculează din venitul brut"):
        _cat(categ_venit=1003, det_ven_net=2, venit_brut=30000, chelt_deduc=3000)


def test_cedarea_folosintei_20_la_suta():
    c = _cat(categ_venit=1015, venit_brut=24000, sediu="Str. Lunga 3")
    # CF art.84 alin.(3): „aplicarea cotei de 20% asupra venitului brut”; instrucțiuni pct.5.6.6 rd.9 = 10% x rd.7
    assert (c["det_ven_net"], c["chelt_deduc"], c["venit_recalculat"], c["impozit11"]) == (2, 4800, 19200, 1920)
    assert c["descriere_sediu_bun"] == "Str. Lunga 3" and "forma_org" not in c


def test_turistic_pierdere_definitiva():
    c = _cat(categ_venit=1006, venit_brut=10000, chelt_deduc=12000)
    # instrucțiuni pct.5.7.3 rd.4: „aceasta reprezintă pierdere definitivă”; rd.9 = 0 la pierdere
    assert (c["det_ven_net"], c["pierdere"], c["impozit11"]) == (1, 2000, 0)
    with pytest.raises(ValueError, match="pierdere definitivă"):
        _cat(categ_venit=1006, venit_brut=10000, chelt_deduc=5000, pierdere_precedenta=1000)
    assert _cat(categ_venit=1006, venit_brut=10000, chelt_deduc=4000)["impozit11"] == 600


def test_agricol_compensare_si_scutire():
    c = _cat(categ_venit=1009, venit_brut=50000, chelt_deduc=30000, pierdere_precedenta=20000)
    # CF art.118 alin.(4): compensare „în limita a 70% din veniturile nete anuale” -> min(20000, 14000)
    assert (c["venit_net_anual"], c["pierdere_compensata"], c["venit_recalculat"], c["impozit11"]) == (20000, 14000, 6000, 600)
    s = _cat(categ_venit=1010, venit_brut=50000, chelt_deduc=30000, nr_zile_scutite=73)
    # CF art.60 pct.1 lit.d) + normele HG 1/2016 la art.69 alin.(11): redus proporțional cu zilele calendaristice
    # (INTERPRETARE CU TEMEI: 365 de zile în 2025) -> 20000 x 292/365 = 16000; rd.9 pe rd.8
    assert (s["venit_redus"], s["impozit11"], s["nr_zile_scutite"]) == (16000, 1600, 73)


def test_redus_handicap_pe_zilele_anului():
    # numitorul = zilele calendaristice ale anului: 366 într-un an bisect (interpretarea declarată în d212.redus_handicap)
    assert d212.redus_handicap(36600, 66, 2024) == 30000
    assert d212.redus_handicap(36500, 65, 2025) == 30000


def test_investitii_castig_si_pierdere():
    c = _cat(categ_venit=1012, castig_net=8000, pierdere_precedenta=10000)
    # CF art.119 alin.(2): pierderea netă „se recuperează în limita a 70% din câștigurile nete anuale” -> 5600
    assert (c["venit_net_anual"], c["pierdere_compensata"], c["venit_recalculat"], c["impozit11"]) == (8000, 5600, 2400, 240)
    p = _cat(categ_venit=1012, castig_net=-3000)
    assert (p["pierdere"], p["impozit11"]) == (3000, 0) and "det_ven_net" not in p
    with pytest.raises(ValueError, match="câștigul net"):
        _cat(categ_venit=1012, venit_brut=1000)


@pytest.mark.parametrize("cod", d212.CATEG_ALTE_SURSE)
def test_alte_surse_doar_rd7_si_rd9(cod):
    c = _cat(categ_venit=cod, venit_impozabil=3000)
    # CF art.116 alin.(2): „prin aplicarea cotei de 10%”; instrucțiuni pct.9.2.2 — doar rd.7 și rd.9
    assert c == {"categ_venit": cod, "venit_recalculat": 3000, "impozit11": 300}


def test_alte_surse_coduri_din_formularul_oficial():
    """Codurile 1021-1024 = literele art.114 alin.(2) k^1/l/m/altele, tipărite în D212Pdf Pdf_v5/v6 (Pdf_v8 le bifează pe
    toate în căsuța 9). Ecranul le arată pe literele astea — dacă ordinea s-ar schimba, eticheta ar minți."""
    js = (RAD / "static/js/ecrane/declaratii.js").read_text(encoding="utf-8")
    for cod, lit in ((1021, "lit.k^1"), (1022, "lit.l"), (1023, "lit.m")):
        assert re.search(r'\["%d", "Alte surse — art\.114 alin\.\(2\) %s' % (cod, re.escape(lit)), js), cod


def test_categoriile_ecranului_sunt_cele_din_server():
    js = (RAD / "static/js/ecrane/declaratii.js").read_text(encoding="utf-8")
    bloc = js[js.index("const _D212_CATEG = ["):js.index("];", js.index("const _D212_CATEG = ["))]
    assert tuple(int(c) for c in re.findall(r'\["(\d{4})"', bloc)) == d212.CATEG_MANUALE
    harta = js[js.index("const _D212_CAMP_CAT = {"):js.index("};", js.index("const _D212_CAMP_CAT = {"))]
    lipsa = set(re.findall(r'"(d212-v-[a-z]+)"', harta)) - set(re.findall(r'id="(d212-v-[a-z]+)"', js))
    assert lipsa == set(), "câmpuri din harta categoriilor care nu există pe ecran: %s" % sorted(lipsa)


def test_anul_2026_refuzat_numit():
    # Legea 239/2025 art.XII schimbă de la veniturile 2026 cedarea folosinței (CF art.83-87) și alte surse (art.114-116)
    with pytest.raises(ValueError, match="Legea 239/2025"):
        d212.cap11_categorie({"categ_venit": 1015, "venit_brut": 1000}, 2026)


def test_scutirea_doar_pe_categoriile_din_art60():
    # CF art.60 pct.1: activități independente, DPI, agricole — nu chirii
    with pytest.raises(ValueError, match="art.60"):
        _cat(categ_venit=1015, venit_brut=1000, nr_zile_scutite=10)


def test_activitate_independenta_din_afara_registrului_se_cumuleaza():
    """A doua activitate independentă (altă firmă / altă formă de exercitare în același an) se adaugă manual și se
    cumulează cu cea din registru — CF art.148 alin.(3) (CAS) și art.170 alin.(1) (CASS) cer cumularea."""
    m = _cat(categ_venit=1016, venit_brut=50000, chelt_deduc=20000, caen="6201")
    # rândurile sistemului real (pct.3.5.11); rd.9 nu se completează la venit net — impozitul e în Secțiunea 4
    assert (m["det_ven_net"], m["venit_net_anual"], m["venit_recalculat"]) == (1, 30000, 30000) and "impozit11" not in m
    rip = d212.cap11_sistem_real(60000, 30000)                               # 30.000 din registru
    o, _ = d212.oblig_realizat([rip], None, 2025)
    assert "cas_datorat" not in o                                            # 30.000 < 12 sm
    o, _ = d212.oblig_realizat([rip, m], None, 2025)
    # cumulat 60.000 >= 12 sm (48.600) -> CAS pe 12 sm; CASS 2.1 pe 60.000; Secțiunea 4 pe ambele venituri
    assert (o["cas_total_ven"], o["cas_datorat"], o["cass_total_ven_ai"], o["real_venit_net_recalculat_ai"]) == \
        (60000, 12150, 60000, 60000)
    # anii activităților independente urmează calea din registru (plafoane verificate 2025/2026), nu ANI_CATEGORII
    assert d212.cap11_categorie({"categ_venit": 1016, "venit_brut": 1000}, 2026)["venit_net_anual"] == 1000


def test_cas_include_venitul_din_dpi():
    sm = e.plafoane_an(2025).salariu_minim
    ai = d212.cap11_sistem_real(140000, 100000)                              # net 40.000 < 12 sm (48.600)
    o, _ = d212.oblig_realizat([ai], None, 2025)
    assert "cas_datorat" not in o
    dpi = _cat(categ_venit=1003, det_ven_net=2, venit_brut=30000)            # net 18.000
    o, b = d212.oblig_realizat([ai, dpi], None, 2025)
    # CF art.148 alin.(3): încadrarea „prin cumularea veniturilor nete ... din activități independente ... precum și a
    # veniturilor nete din drepturi de proprietate intelectuală” -> 58.000 >= 12 sm
    assert (o["cas_total_ven"], o["cas_baza"], o["cas_datorat"], b["bifa131"]) == (58000, 12 * sm, 12150, "1")
    # instrucțiuni Secțiunea 4.1 rd.2: totalul art.148 alin.(1) (cu DPI) e numitorul ponderii
    assert (o["real_cas_total_ven_ai"], o["real_cas_pondere_ai"], o["real_cas_deductibila_ai"]) == (58000, "0.6897", 8379)
    # CASS 2.1 rămâne pe activitățile independente (art.170 alin.(1)); DPI merge la 2.2, unde 18.000 < 6 sm nu datorează
    # (art.170 alin.(2)) — deci nici rândul pe categorii nu se emite
    assert o["cass_total_ven_ai"] == 40000 and "cass_ven_dpi" not in o and "bifa_cass_datorat_dpi" not in o


@pytest.mark.parametrize("venit,treapta", [(24299, 0), (24300, 1), (48599, 1), (48600, 2), (97199, 2), (97200, 3)])
def test_cass_22_pe_trepte(venit, treapta):
    sm = e.plafoane_an(2025).salariu_minim
    r = e.calculeaza_cass_alte_venituri(venit, e.plafoane_an(2025))
    # CF art.170 alin.(2)-(3): sub 6 sm nimic; 6 sm „între 6 ... inclusiv și 12”, 12 sm între 12 și 24, 24 sm de la 24
    assert r["treapta"] == treapta
    assert r["baza"] == ((0, 6, 12, 24)[treapta]) * sm and r["cass"] == r["baza"] * 0.10


def test_cass_22_in_declaratie():
    v = [_cat(categ_venit=1015, venit_brut=40000), _cat(categ_venit=1024, venit_impozabil=5000)]
    o, b = d212.oblig_realizat(v, None, 2025, alte_cass={"dividende_dobanzi": 2000, "asociere_pj": 1000})
    # rd.1 pe categorii (pct.52.1.4; art.170 alin.(4) lit.c, d, f): chirie 32.000, investiții (dividende) 2.000,
    # alte surse 5.000, asocieri 1.000 -> 40.000: treapta 6 sm
    assert (o["cass_ven_cfb"], o["cass_ven_inv"], o["cass_ven_alt"], o["cass_ven_asc"], o["cass_total_ven"]) == \
        (32000, 2000, 5000, 1000, 40000)
    assert (o["bifa_cass_real"], o["cass_baza"], o["cass_datorat"], o["cass_dif_plus"]) == (1, 24300, 2430, 2430)
    assert (o["bifa_cass_datorat_dpi"], b["bifa132"], o["oblcass_real_difPlus_dpi"], o["cass_plus"]) == (1, "1", 2430, 2430)
    # I.7 rd.1 = Σ rd.9 din I.1.1 (3.200 + 500); diferența de plată = impozit + CASS 2.2
    assert (o["oblimpoz_real_total"], o["dif_de_plata"]) == (3700, 6130)


def test_cass_22_retinuta():
    v = [_cat(categ_venit=1015, venit_brut=40000)]
    o, _ = d212.oblig_realizat(v, None, 2025, alte_cass={"cass_retinuta": 430})
    assert (o["cass_retinut"], o["cass_dif_plus"], o["oblcass_real_difPlus_dpi"]) == (430, 2000, 2000)
    with pytest.raises(ValueError, match="diferența stabilită în minus"):
        d212.oblig_realizat(v, None, 2025, alte_cass={"cass_retinuta": 3000})


def test_exceptia_minim_cass_rezulta_din_2_2():
    ai = d212.cap11_sistem_real(30000, 20000)                                 # net 10.000 < 6 sm
    o, _ = d212.oblig_realizat([ai], None, 2025)
    assert o["baza_cass_datorat_ai"] == 24300                                 # CF art.174 alin.(6): baza minimă
    chirie = _cat(categ_venit=1015, venit_brut=40000)                         # net 32.000 >= 6 sm -> CASS 2.2
    o, _ = d212.oblig_realizat([ai, chirie], None, 2025)
    # CF art.174 alin.(7) lit.b): diferența nu se datorează dacă veniturile lit.c)-h) poartă CASS la cel puțin 6 sm
    assert (o["baza_cass_datorat_ai"], o["cass_datorat_ai"], o["cass_baza"]) == (10000, 1000, 24300)


def test_sectiunea_5_dpi_in_sistem_real():
    dpi = _cat(categ_venit=1003, det_ven_net=1, venit_brut=90000, chelt_deduc=20000, nr_zile_scutite=100)
    assert "impozit11" not in dpi and "venit_redus" not in dpi       # pct.4.5.7: rd.8/rd.9 nu se completează la venit net
    o, b = d212.oblig_realizat([dpi], None, 2025)
    # CF art.148 alin.(3) -> CAS pe 12 sm; CF art.118 alin.(2^1): CAS deductibilă = pondere x CAS (aici 1)
    assert (o["cas_datorat"], o["real_cas_pondere_dpi"], o["real_cas_deductibila_dpi"], o["real_cas_dpi"]) == \
        (12150, "1.0000", 12150, 12150)
    # pct.54 rd.3 = 70.000 - 12.150; rd.4 redus pe 265/365 zile (INTERPRETARE, redus_handicap); rd.5 = 10%
    assert (o["real_venit_net_impozabil_dpi"], o["real_venit_net_impozabil_redus_dpi"], o["real_impozit_datorat_dpi"]) == \
        (57850, 42001, 4200)
    assert b["bifa15"] == "1" and o["oblimpoz_real_total"] == 4200


def test_sectiunea_4_redusa_pentru_handicap():
    ai = d212.cap11_sistem_real(160000, 60000, nr_zile_scutite=73)
    o, _ = d212.oblig_realizat([ai], None, 2025)
    imp = o["real_venit_net_impozabil_ai"]
    # instrucțiuni pct.53 rd.5: redus proporțional cu zilele scutite; rd.6 = 10% din rd.5
    assert o["real_venit_net_impozabil_redus_ai"] == d212.redus_handicap(imp, 73, 2025)
    assert o["real_impozit_datorat_ai"] == d212._lei(o["real_venit_net_impozabil_redus_ai"] * 0.10)


def test_dpi_o_singura_sectiune():
    m = dict(ID, venituri=[{"categ_venit": 1003, "venit_brut": 1000}, {"categ_venit": 1003, "venit_brut": 2000}])
    with pytest.raises(ValueError, match="pct.4.4"):
        d212.genereaza(None, None, Perioada(2025), m)


def test_sectiunile_repetate_valide_pe_duk():
    from core import duk
    v = [{"categ_venit": 1003, "det_ven_net": 2, "venit_brut": 30000},
         {"categ_venit": 1015, "venit_brut": 24000, "sediu": "Bucuresti, Str. Lunga 3", "nr_doc": "12", "data_doc": "2024-12-20"},
         {"categ_venit": 1009, "venit_brut": 50000, "chelt_deduc": 30000, "pierdere_precedenta": 5000},
         {"categ_venit": 1012, "castig_net": 8000, "pierdere_precedenta": 10000},
         {"categ_venit": 1024, "venit_impozabil": 3000},
         {"categ_venit": 1006, "venit_brut": 10000, "chelt_deduc": 12000}]
    x, r = d212.genereaza(None, None, Perioada(2025), dict(ID, venituri=v))
    rad = ET.fromstring(x.split("?>", 1)[1])
    assert len(rad.findall("{%s}cap11" % d212.NS)) == 6 and rad.get("bifa111") == "1"
    rez = duk.valideaza(x, "d212", an=2025, luna=12, timeout=180)
    assert rez["stare"] == "valid", rez.get("erori")
