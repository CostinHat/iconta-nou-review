# -*- coding: utf-8 -*-
"""Script de unică folosință (17.3): încercare locală, cele 105 intrări × 3 rezoluții, același detector ca matricea (matrice_text_taiat.deschide), rezumat pe selector.
Nu înlocuiește matricea «dupa» din pct.4.2 (aceea e cea din raport). Uz: ./venv/bin/python docs/dovezi/17_3/proba_cifre.py <fișier_ieșire>"""
import collections
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import matrice_text_taiat as M  # noqa: E402
import verificator_design as VD  # noqa: E402

iesire = sys.argv[1]
tot = collections.Counter()
cu = []
for e in VD.registru():
    for rez in M.REZOLUTII:
        js = M.deschide(e["nume"], rez, "/tmp/proba_cifre_json")
        if not isinstance(js, dict):
            print("NEDESCHIS", e["nume"], rez, js, flush=True)
            continue
        r = M.rand_ecran(e["nume"], rez, js)
        tot[rez] += r["numar"]
        if r["numar"]:
            cu.append((e["nume"], rez, r["numar"], collections.Counter((t["tip"], t["selector"]) for t in r["taiate"]).most_common(4)))
            print(e["nume"], rez, r["numar"], cu[-1][3], flush=True)
print("TOTAL", dict(tot), flush=True)
json.dump(cu, open(iesire, "w"), ensure_ascii=False)
