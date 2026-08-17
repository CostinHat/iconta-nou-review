# -*- coding: utf-8 -*-
import os
from w_auth import new_page
from walk_t005 import deschide_t005
from playwright.sync_api import sync_playwright

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "t005_shots")
os.makedirs(OUT, exist_ok=True)

# CSV FARA coloana de salariu/brut
CSV = "nume,prenume,cnp,angajare,norma,ore,judet\nTestescu,Test,1960101227810,2024-01-08,intreaga,8,B\n"
CSVP = os.path.join(OUT, "fara_salariu.csv")
open(CSVP, "w", encoding="utf-8").write(CSV)

def shot(pg, n):
    p = os.path.join(OUT, n + ".png"); pg.screenshot(path=p, full_page=True); print("SHOT", p)

def dtext(pg, tag):
    print("=== TEXT", tag, "===")
    for sel in [".caseta-atentie", ".ca-mesaj", ".mig-eroare", "li", "h2", ".mig-intro", "button"]:
        for e in pg.query_selector_all(sel):
            t = (e.inner_text() or "").strip().replace(chr(10), " | ")
            if t and 2 < len(t) < 200:
                print("  ", sel, "::", t[:190])

with sync_playwright() as pw:
    b, pg = new_page(pw)
    deschide_t005(pg)
    pg.query_selector("#fa-import").click(); pg.wait_for_timeout(1500)
    shot(pg, "60_import_meniu")
    # click stratul Salariati
    pg.get_by_text("Salariați", exact=False).first.click(); pg.wait_for_timeout(1500)
    shot(pg, "61_dupa_salariati")
    # daca apare lista de firme, click firma
    if pg.query_selector("#mig-file") is None:
        fr = pg.query_selector(".mig-frand")
        if fr:
            # cauta randul firmei tenant_005
            rand = None
            for r in pg.query_selector_all(".mig-frand"):
                if "Constructii Profit Trim" in (r.inner_text() or ""):
                    rand = r; break
            (rand or fr).click(); pg.wait_for_timeout(1500)
    shot(pg, "62_upload_ecran")
    fi = pg.query_selector("#mig-file")
    print("HAS #mig-file:", fi is not None)
    if fi:
        fi.set_input_files(CSVP)
        pg.wait_for_timeout(2500)
        shot(pg, "63_preview_respins")
        dtext(pg, "63_preview_respins")
        # butonul Salveaza dezactivat?
        bs = pg.query_selector("#mig-salveaza-sal")
        print("Salveaza disabled:", bs.is_disabled() if bs else "ABSENT")
    b.close()
