# -*- coding: utf-8 -*-
"""Mesaje de REUSITA tiparite dupa un `await` catre un ajutor care se poate opri fara sa spuna.

Clasa R159: `await _salveaza(...)` -> ajutorul refuza si scrie de ce -> apelantul scrie oricum
„Ciorna salvata.". Un mesaj de reusita care nu se uita la rezultat e o afirmatie falsa.
"""
import os
import re

TIPAR = re.compile(r'await\s+(_?\w+)\([^;]*\);\s*[^;]*;?\s*arataMesaj\([^,]+,\s*["\'][^"\']*'
                   r'(salvat|Salvat|trimis|Trimis|Aprobat|aprobat|✓)', re.S)
n = 0
for dr, _, fs in os.walk('static/js'):
    for f in sorted(fs):
        if not f.endswith('.js'):
            continue
        p = os.path.join(dr, f)
        t = open(p, encoding='utf-8').read()
        for m in TIPAR.finditer(t):
            n += 1
            print('%s:%d  await %s(...) -> mesaj de reusita neconditionat'
                  % (p, t[:m.start()].count('\n') + 1, m.group(1)))
print('TOTAL:', n)
