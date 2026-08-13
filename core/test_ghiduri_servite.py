# -*- coding: utf-8 -*-
"""Gard: ghid/ e SURSA UNICA a paginilor publice de ghid.

set(fisiere .md din ghid/) == set(slug-uri returnate de _ghid_lista()). Pica pe diferenta in ORICE sens, cu
numele fisierelor afisate. Clasa de defect prinsa: pagina scrisa + comisa pe disc dar INVIZIBILA (neservita,
neinclusa in index/sitemap), fara niciun semnal - sau invers, un slug servit fara fisier pe disc.
"""
import os
import main

_GHID_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ghid")


def test_ghid_md_egal_cu_servite():
    pe_disc = {f[:-3] for f in os.listdir(_GHID_DIR) if f.endswith(".md")}
    servite = {g["slug"] for g in main._ghid_lista()}
    invizibile = pe_disc - servite          # scrise pe disc dar neservite (defectul de azi)
    fara_fisier = servite - pe_disc         # servite dar fara .md pe disc
    assert pe_disc == servite, (
        "ghid/ nu e sursa unica a paginilor publice:\n"
        + ("  INVIZIBILE (pe disc, neservite): %s\n" % sorted(invizibile) if invizibile else "")
        + ("  SERVITE FARA FISIER: %s\n" % sorted(fara_fisier) if fara_fisier else ""))
