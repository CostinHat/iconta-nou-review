# -*- coding: utf-8 -*-
"""Teste motor S1005 (mapare F10/F20)."""
from decimal import Decimal
from core import bilant

def s(**kw):
    return {k: (Decimal(str(v[0])), Decimal(str(v[1]))) for k, v in kw.items()}

def test_f10_activ_simplu():
    sold = {"212": (100000, 0), "2812": (0, 20000), "371": (5000, 0), "378": (0, 1000),
            "4428.02": (0, 800), "4111": (3000, 0), "5121": (7000, 0), "5311": (500, 0)}
    # [retest 08.10 pct.1] TVA-ul din prețul de raft stă pe analiticul 4428.02 (stocuri.CONT_TVA_STOC) și se scade NUMAI la rd.05
    r = bilant.f10_din_balanta(sold)
    assert r[2] == 80000
    assert r[4] == 80000
    assert r[5] == 5000 - 1000 - 800
    assert r[6] == 3000
    assert r[8] == 7500
    assert r[9] == r[5] + r[6] + r[8]

def test_f10_pasiv_si_capitaluri():
    sold = {"401": (0, 4000), "421": (0, 2000), "1012": (0, 200), "121": (0, 15000),
            "117": (0, 5000), "5121": (26200, 0)}
    r = bilant.f10_din_balanta(sold)
    assert r[13] == 6000
    assert r[29] == 200
    assert r[41] == 5000
    assert r[43] == 15000
    assert r[46] == 200 + 5000 + 15000
    assert r[49] == r[46]
    # ecuatia bilantiera: F(rd15) = capitaluri+provizioane+ven avans>1an... aici simplu:
    assert r[14] == r[9] - r[13]
    assert r[15] == r[14]

def test_f10_bifunctionale():
    # 431 cu sold creditor -> datorie, nu creanta; 473 debitor -> creanta
    sold = {"431": (0, 900), "473": (150, 0)}
    r = bilant.f10_din_balanta(sold)
    assert r[6] == 150
    assert r[13] == 900

def test_f20_micro():
    """[C13, 12.10.2026] rândurile = listele formularului ANAF 2025 (F20 S1005): 607 (mărfurile) e la rd.06 „Alte cheltuieli”
    („6. Alte cheltuieli (ct. 603 + 604 + 605 + 606 + 607 + …)”), nu la rd.03 („3. Costul materiilor prime și al consumabilelor (ct. 601 +
    602 - 609*)”) — testul vechi cerea rd.03 = 30.000; 646 la rd.04 („ct. 641 + … + 645 + 646”)."""
    rl = {"707": (0, 50000), "709": (500, 0), "607": (30000, 0), "641": (8000, 0),
          "646": (180, 0), "6811": (1200, 0), "691": (1600, 0), "765": (0, 300)}   # [C14] 681 sintetic oprește generarea: 6811
    r = bilant.f20_din_rulaje(rl)
    assert r[1] == 49500                                 # 707 - 709
    assert r[2] == 300                                   # 765
    assert r[3] == 0 and r[6] == 30000                   # 607 -> rd.06
    assert r[4] == 8180                                  # 641 + 646
    assert r[5] == 1200
    assert r[7] == 1600
    assert r[8] == 49500 + 300 - 0 - 8180 - 1200 - 30000 - 1600 and r[9] == 0

def test_f20_pierdere():
    rl = {"707": (0, 1000), "607": (5000, 0)}
    r = bilant.f20_din_rulaje(rl)
    assert r[8] == 0 and r[9] == 4000

# [lotul 10, C69] câmpurile antetului pe care generatorul nu le mai inventează (`bilant.erori_antet` refuză lipsa lor), din structura ANAF
# anaf_surse/structura_SC_1225_270126.txt: „10. bifaMC … DA”, „16. codTT Cod judet sediu (fara cod 41) N(2) DA”, „18. codPP Cod forma de
# proprietate N(2) DA Nomenclator forme de proprietate”, „19. nume_admin Nume si prenume Administrator C(75) DA”. CUI-ul 14399840 are
# cifra de control corectă (cel vechi, 12345678, n-o avea).
_ANTET = {"cui_numeric": "14399840", "cod_judet": 40, "mare_contribuabil": False, "forma_proprietate": "35",
          "declarant_nume": "POPESCU", "declarant_prenume": "ION"}


def test_xml_are_antet_si_valori():
    prof = dict(_ANTET, nume="TEST SRL", reg_com="J40/1/2020", caen="6920")
    x = bilant.xml_s1005(prof, 2025, {}, {2: 80000, 4: 80000}, {}, {1: 49500, 8: 9000})
    # v15 e versiunea acceptata de validatorul oficial; v14 e RESPINSA (namespace).
    assert 'xmlns="mfp:anaf:dgti:s1005:declaratie:v15"' in x
    assert 'F10_0022="80000"' in x
    assert 'F20_0012="49500"' in x
    assert 'totalPlata_A=' in x

def test_f10_atribut_creante_3011():
    # Randurile >=100 (301/302 creante) -> F10_3011/F10_3021, NU F10_03011 (atribut
    # necunoscut in XSD). Regula validator F10_68: F10_0061 = F10_3011 + F10_3021.
    # f10p = an precedent (coloana 1: F10_xxx1)
    x = bilant.xml_s1005(dict(_ANTET, nume="T"), 2025,
                         {301: 19040, 6: 19040}, {}, {}, {})
    assert 'F10_3011="19040"' in x
    assert 'F10_03011' not in x
    assert 'F10_0061="19040"' in x
