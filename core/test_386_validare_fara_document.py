# -*- coding: utf-8 -*-
"""[deficiența 386, retestul Costin 19.10.2026] „Registru jurnal: «Validează fără document» (după confirmare) nu face nimic și nu spune de
ce.” Regula de fond R3 din bază (`core/migrare_reguli_fond.py`, comanda Costin 09.10.2026 pct.11: „fiecare notă are documentul-sursă”)
refuză validarea unei note fără document justificativ; ecranele o promiteau totuși (confirmarea din 05.10.2026, rămasă după regulă).
GARDA: cât timp regula e în bază, niciun ecran nu oferă validarea fără document. Că regula e în bază și refuză o probează, pe comportament,
`core/test_reguli_fond.py` (nota fără document e respinsă cu mesajul regulii); dacă regula se scoate, acel test pică și cere decizia."""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_niciun_ecran_nu_ofera_validarea_fara_document():
    gasit = []
    for f in glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True):
        txt = open(f, encoding="utf-8").read()
        for m in re.finditer(r"Valide(az|ez)[ăa]\w* (totu[șs]i|f[ăa]r[ăa] document)|Validezi totu[șs]i", txt):
            gasit.append("%s:%d %s" % (os.path.relpath(f, RAD), txt[:m.start()].count("\n") + 1, m.group(0)))
    assert not gasit, "ecran care promite validarea unei note fără document (regula de fond R3 din bază o refuză): %s" % gasit
