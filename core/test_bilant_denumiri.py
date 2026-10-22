# -*- coding: utf-8 -*-
"""GARD — deficiențele 227 și 234 (comenzile Costin 12.10.2026, verbatim în DECIZII). 227: „la completarea manuală a coloanei «An
precedent» din bilanț, fiecare rând arată denumirea de pe formular, nu doar «rândul 41».” 234: „Denumirile se scriu complete, curate, cu
diacritice, în ordinea de pe formular.”

SURSA denumirilor: FORMULARUL oficial de bilanț 2025 („soft A”, `anaf_surse/bilant_SC_1225_XML_270326.pdf`), tabelele `F10S` / `F20S` /
`F20`, extras de `scripts/extrage_denumiri_bilant.py` în `core/bilant_denumiri.py` (F30 rd.1–3 din structura ANAF). Nimic scris de mână:
modulul generat = extragerea. Înainte (227) sursa era textul structurii: „II. CREANȚE 1.”, „2.Creante repr.dividende ...”, „6.Alte
cheltuieli*****”, rândurile 301 / 302 la sfârșit."""
import os
import re
import sys

from core import bilant as _b, bilant_api as ba, limba_ecran
from core.bilant_denumiri import NOMENCLATOR_COD, NOMENCLATOR_DENUMIRI, NOMENCLATOR_ORDINE

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import extrage_denumiri_bilant as ex  # noqa: E402


def test_modulul_generat_e_extragerea_din_formular():
    """MUTAȚIE: o denumire schimbată de mână în `core/bilant_denumiri.py` -> pică (regenerează cu `--scrie`)."""
    assert (NOMENCLATOR_DENUMIRI, NOMENCLATOR_ORDINE, NOMENCLATOR_COD) == ex.extrage(), \
        "core/bilant_denumiri.py diferă de extragere — ./venv/bin/python scripts/extrage_denumiri_bilant.py --scrie"


def test_fiecare_rand_de_completat_are_denumirea_lui():
    """Toate rândurile pe care le cere completarea manuală (`randuri_formular`) au o denumire; nicio denumire nu poartă formula de conturi,
    codul altui câmp sau un număr de pagină (resturi ale extragerii)."""
    for tip in ("s1005", "s1003"):
        d = ba.denumiri_formular(tip)
        for s, rr in ba.randuri_formular(tip).items():
            assert sorted(d[s]) == rr, (tip, s)
            for r in rr:
                den = d[s][r]
                assert den and "ct." not in den and "F10_" not in den and "F20_" not in den and not den.rstrip().split()[-1].isdigit(), \
                    (tip, s, r, den)


def test_denumirile_sunt_curate_cu_diacritice():
    """234: nicio denumire cu majusculele formularului, cuvinte fără diacritice, steluțe sau puncte de suspensie — verificatorul de limbă
    al aplicației (`limba_ecran.defecte`, același ca pe ecrane). MUTAȚII: diacriticele scoase din extragere -> „si” -> pică; majusculele
    păstrate -> „CASA” -> pică."""
    rele = [(t, s, r, d) for t, x in NOMENCLATOR_DENUMIRI.items() for s, y in x.items() for r, d in y.items()
            if limba_ecran.defecte(d) or re.search(r"\*|\.\.\.|…|\b\d+\.[A-Za-zĂÂÎȘȚ]", d)]
    assert not rele, rele


def test_denumirile_sunt_cele_de_pe_formular():
    """Câteva rânduri, fixate pe textul formularului (tabelul și rândul în comentariu)."""
    f10, f20m, f20 = NOMENCLATOR_DENUMIRI["s1005"]["F10"], NOMENCLATOR_DENUMIRI["s1005"]["F20"], NOMENCLATOR_DENUMIRI["s1003"]["F20"]
    assert f10[8] == "IV. Casa și conturi la bănci"                                         # F10S R08 „IV. CASA ŞI CONTURI LA BĂNCI”
    assert f10[301] == "II. Creanțe — 1. Creanțe"                                           # F10S R301 „II.CREANŢE 1.” (rândul 06a)
    assert f10[302] == "II. Creanțe — 2. Creanțe reprezentând dividende repartizate în cursul exercițiului financiar"   # R302 (06b)
    assert f10[6] == "II. Creanțe — total (rd. 06a + 06b)"                                  # R06 „TOTAL (rd. 06a+06b)”
    assert f10[41] == "V. Profitul sau pierderea reportat(ă) — sold C"                      # R41 „… REPORTAT(Ă) SOLD C”
    assert f10[44] == "VI. Profitul sau pierderea exercițiului financiar — sold D"          # R_PP (situațiile anuale) + R44 „SOLD D”
    assert f20m[1] == "1. Cifra de afaceri netă" and f20m[6] == "6. Alte cheltuieli"        # F20S R01, R06 („6. Alte cheltuieli (ct. …)”)
    assert f20m[8] == "Profitul sau pierderea net(ă) a exercițiului financiar — profit (rd. 01 + 02 - 03 - 04 - 05 - 06 - 07 + 07a)"
    assert f20[4] == "Reduceri comerciale acordate"                                         # F20 R04
    assert f20[33] == "11.2. Cheltuieli cu redevențele, locațiile de gestiune și chiriile"  # F20 R33 (în structură: copie a lui 11.6)
    assert f20[8] == "2. Venituri aferente costului producției în curs de execuție — sold D"   # RGOL2 + R08 „Sold D”
    assert NOMENCLATOR_DENUMIRI["s1003"]["F10"] == f10                                       # F10S e comun S1003 / S1005


def test_ordinea_si_codul_sunt_ale_formularului():
    """234: „Rândurile 301 și 302 apar la final, nu sub rd.6.” Ordinea = cea a formularului (05, 06a, 06b, 06, 07), codul = cel tipărit.
    MUTAȚIE: ordinea după numărul rândului -> 301 / 302 la final -> pică."""
    o = NOMENCLATOR_ORDINE["s1005"]["F10"]
    assert o[4:9] == [5, 301, 302, 6, 7], o
    assert (NOMENCLATOR_COD["s1005"]["F10"][301], NOMENCLATOR_COD["s1005"]["F10"][6]) == ("06a (301)", "06")
    assert NOMENCLATOR_ORDINE["s1005"]["F20"][:3] == [1, 301, 305] and NOMENCLATOR_ORDINE["s1003"]["F20"][-2:] == [69, 70]


def test_randurile_validate_poarta_denumirea_si_ordinea_formularului():
    """Tabelul „Ce se depune” (188) arată denumirea și codul, după formularul din rădăcina XML-ului, în ordinea formularului (234).
    MUTAȚIE: ordinea după numărul rândului în `randuri_din_xml` -> pică."""
    x5 = '<Bilant1005><F10 F10_0061="9" F10_0081="7" F10_3011="9"/><F20 F20_0042="3"/></Bilant1005>'
    r = [(x["formular"], x["rand"], x["cod"], x["denumire"]) for x in _b.randuri_din_xml(x5)]
    assert r == [("F10", 301, "06a (301)", "II. Creanțe — 1. Creanțe"), ("F10", 6, "06", "II. Creanțe — total (rd. 06a + 06b)"),
                 ("F10", 8, "08", "IV. Casa și conturi la bănci"), ("F20", 4, "04", "4. Cheltuieli cu personalul")], r
    x3 = x5.replace("Bilant1005", "Bilant1003")
    assert {(x["formular"], x["rand"]): x["denumire"] for x in _b.randuri_din_xml(x3)}[("F20", 4)] == "Reduceri comerciale acordate"


def test_datele_informative_scrise_au_denumire():
    """[C11, 12.10.2026] Rândurile F30 pe care le scrie generatorul (datele informative, cap.I) au denumirea lor din structura ANAF;
    tabelul „Ce se depune” le arată separat de „An precedent” / „An curent”. MUTAȚIE: F30 scos din extragere -> pică."""
    x = _b.xml_s1005({"cui_numeric": 14399840, "nume": "P", "cod_judet": 40, "mare_contribuabil": False, "forma_proprietate": "35",
                      "declarant_nume": "Pop", "declarant_prenume": "Ion", "interes_public": False, "calit_intocmit": 12, "intocmit_nume": "IONESCU MARIA"}, 2025, {}, {8: 5}, {}, {8: 5})  # [lotul 10, C69] antetul bilanțului: codTT, bifaMC/codJJ, codPP, nume_admin — din Date firmă
    randuri = sorted({int(r) for r in re.findall(r'\bF30_(\d{3})[12]="', x)})
    assert randuri == [1, 2, 3] and all(NOMENCLATOR_DENUMIRI[t]["F30"].get(r) for t in ("s1005", "s1003") for r in randuri), randuri
    assert NOMENCLATOR_DENUMIRI["s1005"]["F30"][1] == "Unități care au înregistrat profit"
