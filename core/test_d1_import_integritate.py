# -*- coding: utf-8 -*-
"""core/test_d1_import_integritate.py — GARD: importul de salariati BLOCHEAZA CNP invalid, NU sare tacut.

SUPERSEDEAZA (16.08.2026, tura audit vizual tenant_003) gardul vechi `test_salariati_skip_surfatat_in_ui`,
care cerea ca `sarite_cnp` (cate randuri sarite) sa fie SURFATAT in UI. Premisa aceea era FALSA: `importa()`
ridica ValueError la PRIMUL CNP invalid (`verifica_randuri` e prima poarta) -> nu se ajunge NICIODATA la
bucla de skip; `sarite_cnp` era mereu 0 (cod mort), iar textele "vor fi sarite" / "X sariti" promiteau un
comportament inexistent. Dovada vizuala (regula 14, tenant_003 Comert Micro TVA): pe acelasi ecran banda
"2 cu CNP gresit (vor fi sarite)" contrazicea caseta "2 randuri nu pot fi salvate" + butonul Salveaza
dezactivat. Adevarul garantat aici: BLOCHEAZA, nu sare.
"""
import io
import re
import pytest
from core import salariati_import_api as s


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_importa_blocheaza_cnp_invalid_nu_sare():
    """Un rand cu CNP invalid -> importa RIDICA (nimic nu se scrie), nu il sare tacut.
    Ridica INAINTE de orice cursor, deci conn=None nu se atinge (proba ca poarta e prima)."""
    rows = [{"nume": "X", "prenume": "Y", "cnp": "1234567890123", "cnp_valid": False,
             "cnp_motiv": "luna", "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 3000}]
    with pytest.raises(ValueError):
        s.importa(None, rows)


def test_fara_cod_mort_skip_in_backend():
    """Codul mort de skip (sarite_cnp + bucla 'sare CNP invalid') e ELIMINAT din backend.
    RED pe codul vechi: sarite_cnp prezent + `sarite += 1`."""
    src = _read("core/salariati_import_api.py")
    assert "sarite_cnp" not in src, "sarite_cnp reintrodus (cod mort: importa blocheaza, nu sare)"
    assert not re.search(r"sarite\s*\+=\s*1", src), "bucla de skip reintrodusa in importa"


def test_fara_promisiune_falsa_de_skip_in_ui():
    """Frontendul NU promite un skip inexistent la salariati. RED pe codul vechi:
    'vor fi sarite' + 'semnalate si sarite' + citirea sarite_cnp erau prezente.
    (Retete/articole folosesc legitim 'X sarite (existente/invalide)' - skip REAL, neatins.)"""
    src = _read("static/js/ecrane/migrare.js")
    assert "vor fi sărite" not in src, "banda salariati promite skip inexistent (cod mort)"
    assert "semnalate și sărite" not in src, "intro salariati promite skip inexistent"
    assert "sarite_cnp" not in src, "UI citeste sarite_cnp (skip inexistent)"
    # blocajul REAL: preview dezactiveaza Salvarea pe randuri respinse (gateazaPreview, Q5)
    assert "gateazaPreview" in src, "poarta de blocare a preview-ului lipseste"
