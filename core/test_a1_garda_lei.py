# -*- coding: utf-8 -*-
"""[A1, 17.09.2026] GARDĂ anti-regresie: fiecare cititor care transformă factura în cifră de
declarație sau de notă trece prin `core.sume_lei` (conversia în lei).

DE CE structural, nu pe text (METODA §23): aserțiunea e pe ARBORELE de import (un `ImportFrom`
al `core.sume_lei`), nu pe un `"sume_lei" in sursă`. Un cititor de declarație care pierde conversia
— exact regresia A1 — rupe garda.

ANTI-VACUUM (interdicția 76 / „gardul care nu se verifică pe sine"): garda dovedește că discriminează
— un modul care N-are treabă cu conversia (`core.identitate`) NU importă `sume_lei`, deci un test care
ar trece pe orice ar pica aici.
"""
import ast
import os

import pytest

# Cititorii care produc cifre de declaratie / de nota din facturi. Fiecare TREBUIE sa treaca prin
# core.sume_lei. Lista e explicita: un cititor nou de declaratie se adauga aici, deliberat.
_CITITORI_LEI = [
    "core/d300.py", "core/d394.py", "core/d390.py", "core/d406.py",
    "core/contare_facturi.py",
    "core/d300_reconciliere.py", "core/d394_reconciliere.py", "core/d390_reconciliere.py",
]

# Modul-martor: NU are treaba cu conversia. Daca ar „importa" sume_lei dupa criteriul gardii, garda
# ar fi vacua. E aici ca sa dovedeasca contrariul.
_MARTOR_FARA_LEI = "core/identitate.py"


def _importa_sume_lei(cale):
    with open(cale, encoding="utf-8") as f:
        arbore = ast.parse(f.read(), cale)
    for nod in ast.walk(arbore):
        if isinstance(nod, ast.ImportFrom):
            mod = nod.module or ""
            if mod in ("core", "core.sume_lei") and any(
                    a.name in ("sume_lei",) or a.name == "*" for a in nod.names):
                return True
            if mod == "core.sume_lei":
                return True
        if isinstance(nod, ast.Import):
            if any(a.name in ("core.sume_lei",) for a in nod.names):
                return True
    return False


@pytest.mark.parametrize("cale", _CITITORI_LEI)
def test_cititorul_de_declaratie_trece_prin_sume_lei(cale):
    assert os.path.exists(cale), "cititor A1 dispărut: %s" % cale
    assert _importa_sume_lei(cale), (
        "%s nu mai importă core.sume_lei — conversia în lei (A1) s-a pierdut din acest cititor. "
        "Orice cifră de declarație/notă trebuie să treacă prin curs." % cale)


def test_garda_discrimineaza_anti_vacuum():
    """Martorul NU importă sume_lei: dacă ar trece, criteriul ar fi vacuu."""
    assert os.path.exists(_MARTOR_FARA_LEI)
    assert not _importa_sume_lei(_MARTOR_FARA_LEI), (
        "modul-martor %s importă sume_lei — garda nu mai discriminează, alege alt martor"
        % _MARTOR_FARA_LEI)
