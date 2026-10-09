# -*- coding: utf-8 -*-
"""core/d300_randuri.py — rândul din formularul D300 pentru un atribut XML „Rn_c” (date, nu calcul).

Modul NEUTRU: îl citesc generatorul (`core/d300.py`), a doua cale (`core/d300_reconciliere.py`, care nu are voie să importe
generatorul — gardul de non-tautologie) și controlul încrucișat. Comanda Costin 09.10.2026, „Retest 2” pct.2.
"""
import re as _re

#: [Retest 2 pct.2] Rândul din FORMULARUL D300 în vigoare pentru fiecare atribut XML „Rn” (OPANAF 174/2026, anexa 1 —
#: anaf_surse/opanaf_174_2026_d300.txt; atributele din anaf_surse/d300_struct_anaf.txt). Până la rd.16 numerele coincid;
#: de la vânzările la distanță (R64, R65 = rd.17, rd.18) formularul a renumerotat, atributele XML au rămas: R17 e
#: „TOTAL TAXĂ COLECTATĂ” = rd.19, R31 „Ajustări conform pro-rata” = rd.34. Contabilul citește formularul, nu XML-ul, deci
#: ecranul spune rândul formularului. Atributele fără rând în formularul de azi (R24, R69–R79: cote din perioade trecute)
#: lipsesc de aici și se numesc prin eticheta oficială. Păzit de core/test_d300_rand_formular.py, care citește formularul.
NOMENCLATOR_RANDURI_FORMULAR = {**{n: n for n in range(1, 17)}, 64: 17, 65: 18, 17: 19, 18: 20, 19: 21, 20: 22, 21: 23, 22: 24, 23: 25,
                 25: 26, 43: 27, 44: 28, 26: 29, 27: 30, 28: 31, 29: 32, 30: 33, 31: 34, 32: 35, 33: 36, 34: 37, 35: 38,
                 36: 39, 37: 40, 38: 41, 39: 42, 40: 43, 41: 44, 42: 45}
RAND_FORMULAR = NOMENCLATOR_RANDURI_FORMULAR   # numele folosit de cititori; valorile sunt nomenclatorul de mai sus
_COLOANA = {"1": "coloana Valoare", "2": "coloana TVA"}


def rand_formular(cheie):
    """„R17_2” -> „rândul 19, coloana TVA”; „R12_1_1” -> „rândul 12.1, coloana Valoare”. Ultima parte a atributului e
    coloana (1 = valoare, 2 = TVA), cele dinainte sunt subrândul. Un atribut fără rând în formularul de azi se numește
    prin eticheta lui oficială; o cheie care nu e atribut D300 rămâne cum e (e o eroare de program, nu un rând)."""
    m = _re.fullmatch(r"R(\d+)((?:_\d+)*)_([12])", str(cheie or ""))
    if not m:
        return str(cheie)
    n, sub, col = int(m.group(1)), m.group(2).replace("_", "."), m.group(3)
    if n in RAND_FORMULAR:
        return "rândul %s%s, %s" % (RAND_FORMULAR[n], sub, _COLOANA[col])
    from core.d300_manual_api import ETICHETE
    return "rândul „%s”, %s" % (ETICHETE["R%d" % n], _COLOANA[col]) if "R%d" % n in ETICHETE else str(cheie)
