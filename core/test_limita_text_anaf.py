# -*- coding: utf-8 -*-
"""Gard: niciun atribut de text din declaratii nu depaseste limita ANAF (75 caractere).

DE CE (27.07.2026): ANAF respinge cu "sir mai lung de 75 caractere". Pe o firma reala cu
denumire completa (115 car.: nume + titulaturi profesionale), D300/D301/D390/D394/D112 erau
TOATE respinse. Contabilul primea eroarea criptica a validatorului, fara legatura vizibila
cu campul din ecran.

CE ERA INAINTE: trunchierea `[:74]` exista deja in 6 din 11 locuri unde se emite
`declarant_nume` - regula era cunoscuta si aplicata pe jumatate, din 15.07 (vezi comentariul
din d112). Si acoperea DOAR numele declarantului; campurile care chiar crapau erau `den`
(numele firmei), `adresa`, `den_intocmit`, `adresaR` - netrunchiate nicaieri.

ACUM: sursa unica `common.text_anaf` (normalizeaza spatiile + trunchiaza), folosita in toate
generatoarele. Trunchierea e legitima: forma scurta a denumirii e acceptata de ANAF, iar CUI-ul
identifica firma - nu se pierde informatie fiscala.

Acest test era in registrul de datorie (`test_datorie.py`) ca xfail; s-a reparat, deci a fost
mutat aici ca gard permanent. Asa se inchide un item: nu se sterge, se transforma in gard.
"""
import re

import pytest

from core import db, declaratii_api

CERERI = [
    ("d100", {"an": 2026, "trim": 2}), ("d101", {"an": 2025}),
    ("d112", {"an": 2026, "luna": 6}), ("d205", {"an": 2026}),
    ("d300", {"an": 2026, "luna": 6}), ("d301", {"an": 2026, "luna": 6}),
    ("d390", {"an": 2026, "luna": 6}), ("d394", {"an": 2026, "luna": 6}),
    ("d406", {"an": 2026, "luna": 6}),
]
LIMITA = 75
MARCAJ_COTA = "# ROTUNJIRE PE COTA"


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


def test_functia_trunchiaza_si_normalizeaza():
    from core.common import text_anaf, LIMITA_TEXT_ANAF
    assert LIMITA_TEXT_ANAF < LIMITA, "limita interna trebuie sa fie SUB pragul ANAF"
    lung = "A" * 200
    assert len(text_anaf(lung)) == LIMITA_TEXT_ANAF
    assert text_anaf("  doua   spatii  ") == "doua spatii", "spatiile multiple se normalizeaza"
    assert text_anaf(None) == "" and text_anaf("") == ""


def test_niciun_generator_nu_mai_trunchiaza_local():
    """Regula traieste intr-un singur loc. Un `[:74]` local ar diverge tacut."""
    import pathlib
    rad = pathlib.Path(__file__).resolve().parent
    vinovati = []
    for f in sorted(rad.glob("d[0-9]*.py")):
        for nr, linie in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            if "[:74]" in linie and not linie.strip().startswith("#"):
                vinovati.append("%s:%d" % (f.name, nr))
    assert not vinovati, "trunchiere locala in loc de common.text_anaf: %s" % vinovati


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
@pytest.mark.parametrize("tip,body", CERERI)
def test_atributele_respecta_limita_anaf(tip, body):
    """Pe firma reala cu denumire de 115 caractere - cazul care a produs defectul."""
    with db.get_conn("tenant_001") as c:
        try:
            xml, _ = declaratii_api.genereaza(c, "tenant_001", tip, dict(body))
        except ValueError:
            pytest.skip("%s nu se datoreaza / profil incomplet pe tenant_001" % tip)
        finally:
            c.rollback()
    xml = xml.decode("utf-8") if isinstance(xml, bytes) else xml
    lungi = [(a, len(v)) for a, v in re.findall(r'(\w+)="([^"]*)"', xml) if len(v) > LIMITA]
    assert not lungi, "atribute peste %d caractere (ANAF le respinge): %s" % (LIMITA, lungi)


# ============================================================
#  D390 nu se depune pe zero (regula fiscala, nu structura)
# ============================================================
def test_d390_refuza_luna_fara_operatiuni():
    """OPANAF 705/2020 pct. 1.2 + art. 325 Cod fiscal: declaratia recapitulativa se depune
    NUMAI pentru lunile in care ia nastere exigibilitatea taxei. O luna fara operatiuni
    intracomunitare nu produce obligatie.

    Verificat la sursa 27.07.2026. Validatorul ANAF confirma structural: zero <operatie> ->
    "lipsa sectiune obligatorie"; cu o operatiune, acelasi XML e valid.
    """
    import core.d390 as d390
    src = __import__("pathlib").Path(d390.__file__).read_text(encoding="utf-8")
    i = src.index("def genereaza(")
    corp = src[i:src.index("\n", src.index("return build_xml(res), res", i))]
    assert "res.nr_opi == 0" in corp and "raise ValueError" in corp, \
        "d390.genereaza nu mai refuza luna fara operatiuni"
    assert "705/2020" in corp, "poarta fara temei legal citat"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d390_pe_firma_fara_operatiuni_da_mesaj_citibil():
    with db.get_conn("tenant_001") as c:
        with pytest.raises(ValueError) as e:
            declaratii_api.genereaza(c, "tenant_001", "d390", {"an": 2026, "luna": 6})
        c.rollback()
    m = str(e.value)
    assert "nu se depune pe zero" in m and "325" in m, m[:120]


def test_toate_generatoarele_rotunjesc_aritmetic():
    """ANAF cere rotunjire ARITMETICA (half-up), nu bancara - documentat explicit la D112
    (regula A91b: CAM calculat 112, cerut 113). `round()` din Python e BANCARA (half-to-even).

    27.07.2026: d390 era singurul din 10 generatoare cu round() bancar. Aliniat.
    Un generator nou care foloseste round() pe o valoare fiscala pica aici.
    """
    import pathlib, re
    rad = pathlib.Path(__file__).resolve().parent
    vinovati = []
    for f in sorted(rad.glob("d[0-9]*.py")):
        for nr, linie in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
            if linie.strip().startswith("#"):
                continue
            if not re.search(r"\bint\(round\(", linie):
                continue
            # Escape hatch adnotat, ca la masti: rotunjirea pe COTA (procent) e legitima -
            # cotele fiscale RO sunt intregi (21/11/9/5/0), deci bancar == aritmetic.
            # Doar rotunjirea pe SUME (lei) trebuie half-up.
            if MARCAJ_COTA in linie:
                continue
            vinovati.append("%s:%d" % (f.name, nr))
    assert not vinovati, (
        "rotunjire BANCARA pe valoare fiscala: %s\n"
        "-> foloseste Decimal.quantize(ROUND_HALF_UP), sau marcheaza linia cu "
        "'%s' daca e rotunjire pe procent, nu pe lei." % (vinovati, MARCAJ_COTA))


def test_rotunjirea_e_identica_intre_generatoare():
    from core.d390 import _int as a
    from core.d300 import _int as b
    from core.d112 import _d112int as c
    for v in (112.5, 0.5, 2.5, 1000.5, 112.4, 112.6):
        assert a(v) == b(v) == c(v), "rotunjiri divergente pe %s: %s/%s/%s" % (v, a(v), b(v), c(v))
