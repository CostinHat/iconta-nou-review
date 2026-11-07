# -*- coding: utf-8 -*-
"""Script de unică folosință (17.3, pct.2 c): măsoară bara de sus la 603×590 pe câteva ferestre și scrie docs/dovezi/17_3/antet_603.txt.
Uz: ./venv/bin/python docs/dovezi/17_3/masoara_antet.py   (8019 din acest arbore, baza restaurată)"""
import contextlib
import io
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verificator_design as VD  # noqa: E402

JS = os.path.join(RAD, "docs", "dovezi", "17_3", "masoara_antet.js")
ECRANE = ["Control fiscal", "Firme existente", "Plan de conturi F1", "Mișcări și fișe de magazie F1", "Ore suplimentare F5", "Panou Admin — Raportări", "Detaliu firmă F2"]
linii = ["# antet_603.txt (17.3, pct.2 c): bara de sus la 603×590; criteriu: placeholder == «Caută» și scrollWidth <= clientWidth pe .fereastra-fir; ce nu iese se declară ca limită, pe nume.",
         "# ecran | placeholder | fir scrollWidth/clientWidth | încape | segmente vizibile | înălțime antet | înălțime fir | cale întreagă (title)"]
for n in ECRANE:
    with contextlib.redirect_stdout(io.StringIO()):
        VD.ecran(n, "603x590", "/tmp/antet_603_json", masuri_alt=JS)
    m = json.load(open("/tmp/antet_603_json/%s_603x590.json" % VD.slug(n), encoding="utf-8"))["masuri_alt"]
    linii.append(" | ".join([n, str(m["placeholder"]), "%d/%d" % (m["fir_scrollWidth"], m["fir_clientWidth"]), "da" if m["fir_incape"] else "NU", "; ".join(m["segmente_vizibile"]),
                             "%d px" % m["antet_px"], "%d px" % m["fir_inaltime_px"], m["cale_intreaga_in_title"]]))
open(os.path.join(RAD, "docs", "dovezi", "17_3", "antet_603.txt"), "w", encoding="utf-8").write("\n".join(linii) + "\n")
print("\n".join(linii))
