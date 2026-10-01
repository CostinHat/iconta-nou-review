# -*- coding: utf-8 -*-
"""GARD: niciun <input> din ecrane nu-și spune sensul DOAR prin `title` (01.10.2026).

DE CE. `title` nu se vede pe touch și nu e o etichetă (DS v2.42: title-only pierdut pe touch se repară prin
`aria-label`). Scanul de interacțiune îl prinde numai pe ce RANDEAZĂ — iar câmpurile dintr-o zonă care apare
după un click (ex. „nr. copii" de la tichetele de creșă, găsit 01.10.2026 de proba zonei) îi scapă. Gardul
ăsta e STRUCTURAL: citește șabloanele din `static/js`, deci vede și zonele nedeschise.

CE NU VEDE: input-uri construite cu `createElement` + `.title = ...` (nu există azi) și etichete legate prin
`<label for=...>` — acelea au etichetă vizibilă, deci nu sunt title-only și nu se cer aici.
"""
import glob
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_INPUT = re.compile(r"<input\b[^>]*>", re.I | re.S)


def title_only(text):
    """[(linie, tag)] — <input> cu `title` dar fără `aria-label`/`aria-labelledby`."""
    out = []
    for m in _INPUT.finditer(text):
        tag = m.group(0)
        if re.search(r"\btitle\s*=", tag) and not re.search(r"\baria-label(ledby)?\s*=", tag):
            out.append((text.count("\n", 0, m.start()) + 1, tag[:120]))
    return out


def test_niciun_input_title_only():
    rele = []
    for p in sorted(glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True)):
        for ln, tag in title_only(open(p, encoding="utf-8").read()):
            rele.append("%s:%d %s" % (os.path.relpath(p, RAD), ln, tag))
    assert not rele, "input cu sens DOAR prin title (adaugă aria-label):\n" + "\n".join(rele)


def test_CALIBRARE_ambele_directii():
    assert title_only('<input id="a" placeholder="1" title="nr. copii">')
    assert not title_only('<input id="a" aria-label="Nr. copii" title="nr. copii">')
    assert not title_only('<input id="a" placeholder="Preț">')
