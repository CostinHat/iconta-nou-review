# -*- coding: utf-8 -*-
"""scripts/scan_etichete_campuri.py — câmpuri de formular fără etichetă accesibilă (gardul `core/test_etichete_campuri.py`).

Clasa (găsită 04.10.2026, la proba UI a schimbării salariului — axe: „Form elements must have labels” pe #salariu-input și
#salariu-data): câmpuri `<input>/<select>/<textarea>` din șabloanele ecranelor, cu eticheta vizibilă într-un `<span>` sau într-un
`<label>` vecin NELEGAT (fără `for`, fără să învelească câmpul). Vizual arată etichetat; un cititor de ecran citește
„câmp de editare” fără nume. axe le prinde doar pe ecranele pe care le deschide (zonele inline nu), deci gardul e STATIC.

Un câmp e etichetat dacă: are `aria-label`/`aria-labelledby`; e în interiorul unui `<label …>` deschis în același fișier;
sau un `<label for="<id>">` există în fișier. Sărite: hidden/button/submit/checkbox/radio, `input type=file` ascuns
(`hidden` sau `display:none` — se deschide din buton, care are textul).

    python scripts/scan_etichete_campuri.py
"""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CAMP = re.compile(r"<(input|select|textarea)\b[^>]*>")


def neetichetate(rad=None):
    """[(fișier relativ, linie, id-ul sau începutul tag-ului)] — gol = toate câmpurile au nume accesibil."""
    rad = rad or RAD
    out = []
    for f in sorted(glob.glob(os.path.join(rad, "static", "js", "**", "*.js"), recursive=True)):
        s = open(f, encoding="utf-8").read()
        for m in _CAMP.finditer(s):
            tag = m.group(0)
            if re.search(r'type="(hidden|button|submit|checkbox|radio)"', tag):
                continue
            if re.search(r'\bhidden\b(?!-)', tag.replace("hidden;", "")) or "display:none" in tag.replace(" ", ""):
                continue
            if "aria-label" in tag:
                continue
            inainte = s[:m.start()]
            if inainte.rfind("<label") > inainte.rfind("</label>"):
                continue
            idm = re.search(r'id="([^"]+)"', tag)
            if idm and re.search(r'<label[^>]*\bfor="%s"' % re.escape(idm.group(1)), s):
                continue
            out.append((os.path.relpath(f, rad), inainte.count("\n") + 1, idm.group(1) if idm else tag[:60]))
    return out


if __name__ == "__main__":
    r = neetichetate()
    print("câmpuri fără etichetă: %d" % len(r))
    for x in r:
        print("  %s:%d %s" % x)
