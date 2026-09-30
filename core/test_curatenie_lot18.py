# -*- coding: utf-8 -*-
"""GARZI [curatenie lot18]: reparatiile 1a (vanzare marja la pret vanzare), 1b (diferente curs 768/668
la creante/datorii in lei cu clauza valutara), 1c (baza impozitului pe salarii rotunjita la leu),
1e (creditul de sponsorizare - conditia Registru nu se aplica institutiilor publice).

Aserteaza pe COMPORTAMENT (apeluri de functii) si pe STRUCTURA (AST/regex pe sursa, NU `"sir" in X`).
Fiecare are proba de MUTATIE scrisa in comentariu.
"""
import io
import os
import re
from datetime import date
from decimal import Decimal

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _sursa(rel):
    return io.open(os.path.join(RAD, rel), encoding="utf-8").read()


# ===== 1a: vanzare marja =====
def test_1a_marja_negativa_tva_zero_fara_report():
    # [CF art.312, norme pct.86] marja negativa -> TVA 0; nota engine NU mai vorbeste de "report".
    # MUTATIE: revert mesajul tva_marja la "se reporteaza in jurnalul special" -> regex prinde -> rosu.
    from core import tva_marja as m
    r = m.vanzare_marja(1000, 1200, cota=21)          # pret_vanzare < pret_cumparare -> marja negativa
    assert r["tva"] == Decimal("0.00"), "marja negativa -> TVA 0"
    assert r["marja_bruta"] <= 0
    assert re.search(r"reporteaz", r["nota"] or "") is None, "nota nu mai AFIRMA reportarea (se distinge de «fara report»; pct.86, metoda pe livrare)"


def test_1a_nota_use_case_la_pret_vanzare():
    # [1a] STRUCTURA: uc_tenants.vanzare_marja construieste 4111=707 din pret_VANZARE (_pv - tva),
    # nu din pret_cumparare. MUTATIE: revert la ("4111","707", pret_cumparare) -> regex nu mai prinde -> rosu.
    s = _sursa("core/uc_tenants.py")
    assert re.search(r'_pv\s*=\s*Decimal\(str\(corp\["pret_vanzare"\]\)\)', s), \
        "nota marja nu mai porneste de la pret_vanzare"
    assert re.search(r'linii\.append\(\("4111",\s*"707",\s*_pv\s*-\s*r\["tva"\]\)\)', s), \
        "linia 4111=707 nu mai e la pret_vanzare - TVA"


# ===== 1b: diferente de curs 768/668 pt lei cu clauza valutara =====
def test_1b_lei_cu_clauza_768_668():
    # [OMFP 1802/2014 pct.94 lit.b] creante/datorii IN LEI decontate pe cursul unei valute -> 768/668.
    # MUTATIE: revert ("768","668") la ("765","665") -> asertiile pe 768/668 pica.
    from core import diferente_curs as dc
    fav = dc.diferenta(1000, 4.9, 5.0, "creanta", in_lei_cu_clauza=True)    # curs creste -> castig
    assert fav["cont"] == "768", "creanta in lei cu clauza, favorabila -> 768"
    nef = dc.diferenta(1000, 5.0, 4.9, "creanta", in_lei_cu_clauza=True)    # curs scade -> pierdere
    assert nef["cont"] == "668", "creanta in lei cu clauza, nefavorabila -> 668"
    # valuta pura ramane 765/665
    assert dc.diferenta(1000, 4.9, 5.0, "creanta")["cont"] == "765"
    assert dc.diferenta(1000, 5.0, 4.9, "creanta")["cont"] == "665"


def test_1b_nota_decontare_paseaza_flag():
    from core import diferente_curs as dc
    r = dc.nota_decontare(1000, 4.9, 5.0, "creanta", "4111", "5121", in_lei_cu_clauza=True)
    conturi = {c for linie in r["linii"] for c in linie[:2]}
    assert "768" in conturi, "nota_decontare in lei cu clauza -> diferenta pe 768"


# ===== 1c: baza impozitului pe salarii rotunjita la leu =====
def test_1c_baza_impozit_rotunjita_la_leu():
    # [CF art.64, HG 1/2016 tit.IV pct.4] baza de calcul se rotunjeste la leu (<=50 bani jos, >50 sus).
    # Deci impozitul = (baza intreaga) x 10% -> impozit x 10 e multiplu de 1 leu.
    # MUTATIE: scoate `.quantize(Decimal("1"), rounding=ROUND_HALF_DOWN)` -> baza fractionara -> rosu.
    from core import salarizare as sz
    r = sz.calcul_salariu(6000, persoane=0, la_data=date(2026, 9, 1))
    baza = (r["impozit"] - r.get("impozit_tichete", Decimal(0))) / Decimal("0.10")
    assert baza == baza.to_integral_value(), "baza impozitului pe salariu trebuie sa fie leu intreg"
    assert r["impozit"] == Decimal("377.00"), "impozit pe baza rotunjita (6000, sem2)"


# ===== 1e: creditul de sponsorizare - institutie publica scutita de conditia Registru =====
def test_1e_institutie_publica_fara_conditia_registru():
    # [CF art.25(4)i] conditia inscrierii in Registru se aplica DOAR entitatilor persoane juridice fara
    # scop lucrativ (inclusiv unitati de cult), NU institutiilor publice.
    # MUTATIE: revert `not beneficiar_institutie_publica and` -> institutia publica ar primi 0 -> rosu.
    from core import sponsorizari as sp
    la = date(2026, 3, 1)
    pub = sp.credit_sponsorizare(10_000_000, 500_000, 20_000, beneficiar_in_registru=False,
                                 beneficiar_institutie_publica=True, la_data=la)
    assert pub["credit"] > 0, "institutia publica primeste credit fara inscriere in Registru"
    ong = sp.credit_sponsorizare(10_000_000, 500_000, 20_000, beneficiar_in_registru=False,
                                 beneficiar_institutie_publica=False, la_data=la)
    assert ong["credit"] == Decimal("0.00"), "ONG neinscris in Registru -> fara credit (art.25(4)i)"
