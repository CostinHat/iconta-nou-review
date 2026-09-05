# -*- coding: utf-8 -*-
"""Toate textele de buton din static/js care contin un cuvant dat.

Se cere INAINTE de a adauga un cuvant in `PROBATE`: lista decide dupa NUME, iar numele nu spune
unde ajunge actiunea. Fara masuratoarea asta, un cuvant nou deblocheaza butoane nevazute.

Textul unui buton apare in sursa in DOUA forme — literal („Înregistrează") si escapat
(`\\u00cenregistreaz\\u0103`). Se cauta in amandoua: o cautare pe una singura ratase chiar
butonul registraturii, adica exact cel pentru care s-a scris instrumentul.
"""
import codecs
import os
import re
import sys

CUVINTE = [x.lower() for x in sys.argv[1:]]
RAD = 'static/js'


def _forme(s):
    """Textul asa cum e, plus varianta cu `\\uXXXX` dezvoltat (numai daca exista asa ceva)."""
    out = [s]
    if '\\u' in s:
        try:
            out.append(codecs.decode(s, 'unicode_escape'))
        except Exception:  # noqa: BLE001
            pass
    return out


gasite = {}
for dr, _, fs in os.walk(RAD):
    for f in sorted(fs):
        if not f.endswith('.js'):
            continue
        p = os.path.join(dr, f)
        txt = open(p, encoding='utf-8').read()
        for m in re.finditer(r'<button([^>]*)>([^<]{0,60})', txt):
            forme = _forme(m.group(2))
            for c in CUVINTE:
                if any(c in x.lower() for x in forme):
                    linia = txt[:m.start()].count('\n') + 1
                    gasite.setdefault(c, []).append(
                        (p, linia, forme[-1].strip()[:50],
                         'DISABLED' if 'disabled' in m.group(1) else ''))
                    break

for c in CUVINTE:
    print('=== %r — %d butoane' % (c, len(gasite.get(c, []))))
    for p, l, t, d in gasite.get(c, []):
        print('   %s:%d  %r %s' % (p, l, t, d))
