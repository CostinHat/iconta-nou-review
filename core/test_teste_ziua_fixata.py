# -*- coding: utf-8 -*-
"""GARD — bomba de calendar din suită (găsită de Code la 243, 14.10.2026; neconformitate a porții, nu a aplicației — GARZI): un test
care întreabă regula „perioada s-a încheiat” (`inchidere_luna.luna_in_curs`, `inchidere_an.an_incheiat`) pe un an scris în cifre, fără
ziua fixată, e verde numai până trece luna: `core/test_retest2.py` afirma `luna_in_curs(2026, 10)` pe ziua de azi și ar fi oprit poarta
de la 01.11.2026 fără nicio schimbare de cod (CLAUDE.md, „Testele nu presupun gol un interval unde pot ajunge date reale” — aceeași
familie: testul depinde de calendar).

CE FACE IMPOSIBIL: în `core/test_*.py` și `frontend_test/e2e/*.py`, un apel al regulii cu anul literal și fără `azi=`. Un test care vrea
„anul curent” îl calculează (`datetime.date.today().year`), ca e2e-ul 243. CE NU VEDE: alte funcții care citesc ziua de azi."""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_APEL = re.compile(r"\b(luna_in_curs|an_incheiat)\(\s*\d{4}\b[^()]*(?:\([^()]*\)[^()]*)*\)")


def apeluri_fara_zi(fisiere):
    out = []
    for f in fisiere:
        for i, ln in enumerate(open(f, encoding="utf-8"), 1):
            out += ["%s:%d %s" % (os.path.relpath(f, RAD), i, m.group(0)) for m in _APEL.finditer(ln) if "azi" not in m.group(0)]
    return out


def test_CALIBRARE_apelul_fara_zi_e_prins(tmp_path):
    f = tmp_path / "test_proba.py"
    f.write_text("assert luna_in_curs(2026, 10)\nassert luna_in_curs(2026, 10, azi=zi)\nassert ia.an_incheiat(2025)\n"
                 "assert ia.an_incheiat(an)\n", encoding="utf-8")
    assert [x.split(" ", 1)[1] for x in apeluri_fara_zi([str(f)])] == ["luna_in_curs(2026, 10)", "an_incheiat(2025)"]


def test_niciun_test_nu_intreaba_regula_pe_ziua_de_azi():
    """MUTAȚIE: `azi=zi` scos din `core/test_retest2.py::test_pct5_amortizarea_pana_la_ultima_luna_incheiata` -> pică."""
    fis = sorted(glob.glob(os.path.join(RAD, "core", "test_*.py")) + glob.glob(os.path.join(RAD, "frontend_test", "e2e", "*.py")))
    assert apeluri_fara_zi([f for f in fis if not f.endswith("test_teste_ziua_fixata.py")]) == []
