# -*- coding: utf-8 -*-
"""GARD — C10 (comanda Costin 12.10.2026, verbatim în DECIZII): „rescrie F20 din S1003 pe numerotarea formularului ANAF (70 de rânduri),
cu denumirile oficiale.” Înainte: o numerotare proprie de 38 de rânduri (la noi rd.04 = subvenții 7411; pe formular rd.04 = „Reduceri
comerciale acordate” 709), iar DUK S1003 o declara „valid” — validatorul nu verifică formulele F20 (probat: rd.01 = 999 fără componente
trece). Deci judecătorul e FORMULARUL oficial: `anaf_surse/bilant_SC_1225_XML_270326.pdf` (tabelul `form1.F20`, conturile tipărite și
calculele `<calculate>` ale fiecărui rând), citat pe fiecare aserțiune. Universul conturilor: planul OMFP 1802/2014 din corpus
(`anaf_surse/omfp_1802_2014.txt`, clasele 6 și 7)."""
import io
import os
import re
from decimal import Decimal

import pytest

from core import bilant as b

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _plan_oficial_67():
    t = io.open(os.path.join(_RAD, "anaf_surse", "omfp_1802_2014.txt"), encoding="utf-8").read()
    seg = t[t.index("Clasa 6"):t.index("Clasa 8", t.index("Clasa 6"))]
    return sorted(set(re.findall(r"(?<![\d.])([67]\d{2,4})\. [A-ZȘȚĂÎÂ]", seg)))


def _frunze(conturi):
    return [c for c in conturi if not any(o != c and o.startswith(c) for o in conturi)]


def test_fiecare_cont_al_planului_oficial_are_un_singur_rand():
    """Fiecare cont analitic (frunză) de clasa 6/7 al planului OMFP 1802/2014 intră pe exact un rând al F20 S1003 (prefixul cel mai lung);
    sinteticele cu analitice pe rânduri diferite nu au rând (vezi testul de mai jos). Singura frunză fără rând: 695 (impozitul specific,
    rd.67 „=null” în formular). MUTAȚIE: un cont scos din tabel (ex. 646 din rd.24) -> pică."""
    plan = _plan_oficial_67()
    assert len(plan) > 150, len(plan)                                    # anti-vacuu: planul întreg, nu un fragment
    fara = [c for c in _frunze(plan) if b.rand_f20_s1003(c) is None and c != "695"]
    assert not fara, "conturi fără rând în F20 S1003: %s" % fara
    assert b.rand_f20_s1003("695") is None


def test_randurile_cazului_c10_sunt_ale_formularului():
    """Cazul din C10: 704 = 5.000, 7411 = 800, 709 = 300 -> rd.02 = 5.000 (Producția vândută), rd.04 = 300 (Reduceri comerciale
    acordate, ct.709), rd.06 = 800 (subvenții aferente CA, ct.7411), rd.01 = rd.02 + 03 − 04 + 06 = 5.500 (calculul R01 al formularului).
    Înainte: rd.04 = 800 (subvențiile). MUTAȚIE: 7411 pe rd.04 -> pică."""
    r = b.f20_complet_din_rulaje({"704": (0, 5000), "7411": (0, 800), "709": (300, 0)})
    assert (r[2], r[4], r[6], r[1]) == (5000, 300, 800, 5500), r


def test_cheltuielile_pe_randurile_formularului():
    """Formularul (șablonul XFA): rd.24 „b) Cheltuieli cu asigurările și protecția socială (ct.645+646)”; rd.32 „11.1. … prestațiile
    externe (ct.611+613+…+628)” FĂRĂ 612; rd.33 „11.2. … redevențele, locațiile de gestiune și chiriile (ct. 612)” cu „din care” 6121 /
    6122 / 6123 (rd.307–309); 11.6 (rd.316) = 635 + 6586; 11.9 (rd.36) = 6587; 6588 -> 11.10 (rd.37); 25a (rd.306) = 6811.
    MUTAȚIE: 612 înapoi în 11.1 -> pică; 646 scos din 9.b -> pică."""
    r = b.f20_complet_din_rulaje({"646": (40, 0), "645": (60, 0), "641": (1000, 0), "6123": (200, 0), "611": (50, 0),
                                  "6586": (7, 0), "6587": (3, 0), "6588": (11, 0), "6811": (90, 0), "6813": (10, 0)})
    assert (r[23], r[24], r[22]) == (1000, 100, 1100), r                                     # R22 = R23 + R24
    assert (r[32], r[33], r[309], r[316], r[36], r[37]) == (50, 200, 200, 7, 3, 11), r
    assert (r[306], r[26], r[25]) == (90, 10, 100), r                                         # R25 = R306 + R26 − R27
    assert r[31] == 50 + 200 + 7 + 3 + 11, r                                                  # R31 = R32+…+R37+R310+R312+R314+R316


def _rulaje_tot_planul():
    """Câte o sumă distinctă pe fiecare frunză a planului (debit pe 6xx, credit pe 7xx; 609 credit, 709 debit, 711 / 712 pe sold)."""
    rl = {}
    for i, c in enumerate(_frunze(_plan_oficial_67()), start=1):
        if c == "695":
            continue
        s = Decimal(100 + i)
        rl[c] = (s, Decimal(0)) if (c[0] == "6" and c != "609") or c == "709" else (Decimal(0), s)
    rl["711"] = (Decimal(30), Decimal(130))                                                   # sold creditor 100
    rl["712"] = (Decimal(50), Decimal(50))                                                    # sold 0: rd.07 / rd.08 = soldul 711 + 712
    return rl


def test_totalurile_urmeaza_calculele_formularului():
    """Pe un rulaj pe TOT planul: fiecare total = calculul lui din formular (`<calculate>` al rândului)."""
    r = b.f20_complet_din_rulaje(_rulaje_tot_planul())
    assert r[1] == r[2] + r[3] - r[4] + r[6]                                                  # R01
    assert r[16] == r[1] + r[7] - r[8] + r[9] + r[10] + r[11] + r[12] + r[13]                # R16
    assert r[42] == r[17] + r[18] + r[19] + r[20] - r[21] + r[22] + r[25] + r[28] + r[31] + r[39]   # R42
    assert r[52] == r[45] + r[47] + r[49] + r[50] and r[59] == r[53] + r[56] + r[58]          # R52, R59
    assert (r[62], r[63]) == (r[16] + r[52], r[42] + r[59])                                   # R62, R63
    assert r[64] - r[65] == r[62] - r[63] and min(r[64], r[65]) == 0                          # R64/R65 se exclud reciproc
    assert r[69] - r[70] == (r[64] + r[305]) - (r[65] + r[66] + r[68] + r[304] + r[317]) and min(r[69], r[70]) == 0   # R69/R70
    assert (r[7], r[8]) == (100, 0)


def test_rezultatul_net_e_cel_din_rulaje():
    """Reconcilierea: rezultatul net din F20 (rd.69 − rd.70) = veniturile din rulaje − cheltuielile din rulaje (709 scade veniturile,
    609 scade cheltuielile, 711 pe sold), pe TOT planul — un cont pierdut sau numărat de două ori (ex. 6811 și la 25a, și la a.2) strică
    egalitatea. MUTAȚIE: 6811 adăugat și la rd.26 -> pică."""
    rl = _rulaje_tot_planul()
    ven = (sum(c for k, (d, c) in rl.items() if k[0] == "7" and k not in ("709", "711", "712")) - rl["709"][0]
           + sum(rl[k][1] - rl[k][0] for k in ("711", "712")))
    che = sum(d for k, (d, c) in rl.items() if k[0] == "6" and k != "609") - rl["609"][1]
    r = b.f20_complet_din_rulaje(rl)
    assert r[69] - r[70] == int(ven - che), (r[69], r[70], ven, che)


def test_randurile_null_si_contul_fara_rand():
    """Rândurile „=null” ale formularului (rd.05, rd.38, rd.67, rd.318) nu se scriu; un rulaj pe un cont fără rând (695, sau un cont
    inventat) oprește generarea cu motivul, nu dispare din contul de profit și pierdere."""
    r = b.f20_complet_din_rulaje({"704": (0, 10)})
    assert not set(b.F20_S1003_NOMENCLATOR_NULL) & set(r), sorted(r)
    with pytest.raises(ValueError, match=r"contul 695 nu are rând"):
        b.f20_complet_din_rulaje({"695": (5, 0)})


def test_xml_s1003_valid_pe_duk():
    """XML-ul S1003 cu F20 pe rândurile formularului trece validatorul oficial (structura; formulele le păzesc testele de mai sus)."""
    from core import duk
    prof = {"cui_numeric": 14399840, "nume": "ZTEST BILANT SRL", "reg_com": "J40/1/2020", "adresa": "Str 1", "caen": "6202",
            "declarant_nume": "Pop", "declarant_prenume": "Ion", "declarant_functie": "ADMINISTRATOR",
            "cod_judet": 40, "mare_contribuabil": False, "forma_proprietate": "35"}  # [lotul 10, C69] antetul bilanțului: codTT, bifaMC/codJJ, codPP, nume_admin — din Date firmă
    f20 = b.f20_complet_din_rulaje({"704": (0, 5000), "7411": (0, 800), "709": (300, 0), "612": (200, 0), "6123": (200, 0), "641": (1000, 0)})
    x = b.xml_s1003(prof, 2025, {}, {8: 1000, 9: 1000, 15: 1000, 29: 1000, 30: 1000, 46: 1000, 49: 1000}, {}, f20)
    assert re.findall(r'\bF20_0042="(\d+)"', x) == ["300"] and re.findall(r'\bF20_0062="(\d+)"', x) == ["800"], x[:400]
    assert not re.search(r'\bF20_0(05|38|67)\d="', x) and not re.search(r'\bF20_318\d="', x)
    v = duk.valideaza(x, "s1003", an=2025, luna=12)
    assert v["stare"] == "valid", v


def test_sinteticele_cu_analitice_pe_randuri_diferite_opresc_generarea():
    """[decizia Costin 12.10.2026] „Pentru 741 și 658 folosite sintetic, fără analitic: nu ghicim rândul. Generarea S1003 se oprește, cu
    motivul și contul analitic cerut.” Clasa, calculată din planul OMFP: orice sintetic ale cărui analitice cad pe rânduri DIFERITE
    (658, 681, 741, 761, 781) — tabelul `F20_S1003_NOMENCLATOR_SINTETICE` e exact lista calculată, iar un rulaj pe sintetic (și pe un
    analitic al aplicației, „741.01”) oprește generarea cu analiticele cerute pe rândurile lor. MUTAȚIE: 741 readus pe rd.12 (rândul
    ghicit) -> pică; un sintetic scos din tabel -> pică; refuzul scos -> pică."""
    plan = _plan_oficial_67()
    calculat = {}
    for p in plan:
        frunze = [c for c in _frunze(plan) if c != p and c.startswith(p)]
        randuri = {c: (b.rand_f20_s1003(c) or (None,))[0] for c in frunze}
        if len(set(randuri.values())) > 1:
            calculat[p] = tuple(sorted(randuri.items()))
    assert {k: tuple(sorted(v)) for k, v in b.F20_S1003_NOMENCLATOR_SINTETICE.items()} == calculat, calculat
    assert sorted(calculat) == ["658", "681", "741", "761", "781"]
    for s in calculat:
        assert b.rand_f20_s1003(s) is None, s                                   # niciun rând ghicit pentru sintetic
    with pytest.raises(ValueError) as e:
        b.f20_complet_din_rulaje({"704": (0, 10), "741": (0, 800), "658.01": (5, 0)})
    m = str(e.value)
    assert re.findall(r"contul (\d+) e folosit sintetic", m) == ["658", "741"], m
    assert re.findall(r"contul 741 e folosit sintetic, fără analitic, iar formularul ANAF îi pune analiticele pe rânduri diferite: (.*?)\. Trece", m) \
        == ["7411 (rd.06); 7412, 7413, 7414, 7415, 7416, 7417, 7419 (rd.12); 7418 (rd.49)"], m
