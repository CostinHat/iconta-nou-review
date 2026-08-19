# -*- coding: utf-8 -*-
"""[Date de test — CUI/CNP verificate] GARD: un CUI/CNP folosit ca date de test VALIDE (`cui=`/`cnp="..."`)
trece cifra de control. Un CUI/CNP inventat cu checksum greșit = capcană (16.07: validatorul confunda o dată
de test greșită cu un bug de cod real). Testele NEGATIVE (care testează respingerea) sunt exceptate automat:
linia conține un cuvânt intențional (invalid/control/alterat/greșit/negativ/placeholder) sau marker
`# cui-invalid-ok:`. Extragere PRECISĂ din `cui=/cnp="..."` (nu substring-uri).
"""
import os
import re
import glob
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INTENTIONAT = re.compile(r"invalid|control|alterat|gres|greșit|negativ|placeholder|cui-invalid-ok|format", re.I)
_LIT = re.compile(r"[\"']?\b(cui|cnp)\b[\"']?\s*[:=]\s*[\"']([0-9]{6,13})[\"']", re.I)


def _cui_ok(c):
    if not (2 <= len(c) <= 10):
        return None
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp = c[:-1].rjust(9, "0")
    s = sum(int(corp[i]) * ch[i] for i in range(9))
    r = (s * 10) % 11
    return (0 if r == 10 else r) == int(c[-1])


def _cnp_ok(c):
    if len(c) != 13 or c[0] not in "123456789":
        return None
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    r = sum(int(c[i]) * ch[i] for i in range(12)) % 11
    return (1 if r == 10 else r) == int(c[12])


def test_cui_cnp_de_test_trec_checksum():
    rele = []
    for f in glob.glob(os.path.join(_RAD, "core", "test_*.py")):
        lines = open(f, encoding="utf-8").read().split("\n")
        for i, ln in enumerate(lines):
            for m in _LIT.finditer(ln):
                camp, val = m.group(1).lower(), m.group(2)
                ok = _cnp_ok(val) if len(val) == 13 else _cui_ok(val)
                if ok is False:
                    fer = "\n".join(lines[max(0, i - 1):i + 2])
                    if _INTENTIONAT.search(fer):
                        continue  # test negativ (deliberat invalid)
                    rele.append("%s:%d %s=%s" % (os.path.basename(f), i + 1, camp, val))
    assert not rele, ("CUI/CNP de test cu cifra de control GREȘITĂ, folosit ca dată validă (capcană 16.07); "
                      "corectează-l la o valoare validă sau marchează testul negativ cu `# cui-invalid-ok:`: %s" % rele)
