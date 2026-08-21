# -*- coding: utf-8 -*-
"""Sweep operare: deschide fiecare card operational, captura + text scurt."""
import os, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, shot, txt

CARDURI = [
    ("salariati", "#fa-salariati"),
    ("facturi", "#fa-facturi"),
    ("banca", "#fa-banca"),
    ("casa", "#fa-casa"),
    ("produse", "#fa-produse"),
    ("declaratii", "#fa-declaratii"),
    ("control", "#fa-control"),
]

with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {}
    for nume, sel in CARDURI:
        try:
            deschide_firma(pg)
            pg.click(sel); pg.wait_for_timeout(1500)
            shot(pg, "op_" + nume)
            t = (txt(pg, ".pf-container") or txt(pg, "main") or txt(pg, "body") or "")
            # taie antetul de dashboard daca modalul e peste el
            rez[nume] = t[:700]
        except Exception as e:
            rez[nume] = "ERROR: " + str(e); shot(pg, "op_" + nume + "_ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:4500])
    b.close()
