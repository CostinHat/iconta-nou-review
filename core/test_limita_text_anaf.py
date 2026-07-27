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
