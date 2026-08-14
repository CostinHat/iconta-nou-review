# -*- coding: utf-8 -*-
"""[#6 plimbare 14.08.2026 / regula 9] Garda: o declaratie e LIVE DOAR daca e accesibila in selectorul UI
(in declaratii_api.tipuri(), adica NU in _DOAR_API). "Fara ecran accesibil, functionalitatea nu exista" -
deci un tip doar-API nu are voie sa fie marcat LIVE (ar minti ca e accesibil), si invers."""
import csv, io
from core.declaratii_api import DECLARATII, _DOAR_API


def test_live_declaratie_implica_accesibila_in_selector():
    r = list(csv.reader(io.open("FUNCTIONALITATI.csv", encoding="utf-8-sig")))
    h = r[0]
    isr, ist, inume = h.index("Sursa cod"), h.index("Stare"), h.index("Functionalitate")
    prob = []
    for tip in DECLARATII:
        rr = [x for x in r[1:] if len(x) > max(isr, ist) and ("core/%s.py" % tip) in (x[isr] or "")]
        for x in rr:
            live = x[ist].strip().upper().startswith("LIVE")
            in_api = tip in _DOAR_API
            if in_api and live:
                prob.append("%s (%s): LIVE dar e doar-API (nu in selector) - fa-l accesibil sau schimba starea" % (tip, x[inume]))
            if (not in_api) and (not live):
                prob.append("%s (%s): in selector dar NU e LIVE" % (tip, x[inume]))
    assert not prob, "LIVE != accesibil in selector (regula 9):\n" + "\n".join(prob)
