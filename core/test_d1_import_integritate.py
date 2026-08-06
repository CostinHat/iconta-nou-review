# -*- coding: utf-8 -*-
"""core/test_d1_import_integritate.py — GARD Bloc 0 (D1a): skip la import NU e tăcut.

`salariati-import` calculează `sarite_cnp` (câte rânduri au fost sărite pt CNP invalid) dar UI-ul îl
arunca (`migrare.js` naviga tăcut peste pierderea de date). Gardul cere ca răspunsul să fie SURFAȚAT
într-un canal vizibil înainte de navigare.

NOTĂ (finding 06.08, tura 5): NOT NULL pe coloanele monetare a fost RETRAS. În acest codebase principiul
„bază nulă = eroare" e enforce-uit SEMANTIC (detectează-și-semnalează), nu la nivel de schemă: ex.
`test_d112_reconciliere.test_skip_suspect_brut_lipsa_e_semnalat_nu_tacut` se bazează pe `salariati.salariu_brut`
NULL ca stare-semnal („brut lipsă → suspect"). Un NOT NULL de schemă ar ȘTERGE stări-semnal designate și
intră în conflict cu garda semantică existentă. Deci integritatea monetară rămâne la stratul de reconciliere,
nu în DDL.
"""
import io
import re


def _read(p):
    return io.open(p, encoding="utf-8").read()


def test_salariati_skip_surfatat_in_ui():
    """Răspunsul import-ului de salariați (sarite_cnp) NU e aruncat: UI-ul îl citește și-l afișează vizibil."""
    src = _read("static/js/ecrane/migrare.js")
    # backend-ul întoarce contractul
    assert '"sarite_cnp"' in _read("core/salariati_import_api.py"), "backend nu mai întoarce sarite_cnp"
    # UI-ul referă sarite_cnp (nu-l lasă tăcut) în handlerul de salvare salariați
    assert "sarite_cnp" in src, "migrare.js nu mai citește sarite_cnp — skip tăcut re-introdus"
    # și îl duce într-un canal vizibil (confirmă/mesaj), nu doar îl citește
    assert re.search(r"sarite_cnp[\s\S]{0,400}(confirmaCaseta|arataMesaj)", src), \
        "sarite_cnp citit dar nu afișat vizibil (confirmaCaseta/arataMesaj)"
