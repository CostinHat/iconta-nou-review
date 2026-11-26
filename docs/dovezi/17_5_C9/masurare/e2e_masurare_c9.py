# -*- coding: utf-8 -*-
"""17.5-C9 pct.5 — exemplul reproductibil al uneltei de măsurare Pilot pe un cod existent (F018, Parteneri F1), la 1366×768 și 603×590.
Rulat numai prin lansatorul nativ al probelor pe 8019 (docs/dovezi/17_5_Q12/rulare_8019.sh … scripts/e2e_poarta.py --doar=…), care
restaurează baza înainte și după. Gestul: Firme › F1 › Parteneri; măsura fiecărei celule: `scripts/masurare_pilot.py::masoara_celula`
(cheia `dom:` citită prin `verifica_pas.observa_pagina`), cu captura și manifestul martorilor. Judecata o face apoi unealta:
  ./venv/bin/python scripts/masurare_pilot.py judeca docs/dovezi/17_5_C9/masurare/inventar_F018_exemplu.tsv <capturi>/17_5_C9_masurare <commit> <iesire.tsv>"""
import os
import subprocess
import sys
from pathlib import Path

RAD = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAD / "scripts"))


def test_masurare_c9_F018(browser):
    from conftest import BAZA, CAPTURI, Ecran, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import TOP, F1, firma, origine_proba
    import masurare_pilot as mp

    origine_proba(BAZA)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    director = Path(CAPTURI) / "17_5_C9_masurare"
    director.mkdir(parents=True, exist_ok=True)
    randuri = mp.citeste_tsv(str(Path(__file__).with_name("inventar_F018_exemplu.tsv")))
    for w, h in ((1366, 768), (603, 590)):
        ctx = browser.new_context(viewport={"width": w, "height": h})
        erori = []
        try:
            ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(sesiune("dovada.71507@sesiuneab.test"))
            pg = ctx.new_page()
            pg.on("console", lambda m: erori.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: erori.append(str(e)))
            Ecran(pg, "c9").acasa()
            firma(pg, F1, "#fa-parteneri")
            desenat = True
            try:
                pg.locator(TOP + "#pt-tabel").wait_for(state="visible", timeout=20000)
                pg.evaluate("() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))")
            except Exception:
                desenat = False
            titlu = pg.locator(TOP + "h2").first.inner_text() if desenat else ""
            for r in randuri:
                if r["rezolutie"] != "%dx%d" % (w, h):
                    continue
                mp.masoara_celula(pg, r, str(director), commit, {
                    "firma": F1, "rol": r["rol"], "ruta": "Parteneri" if titlu.strip().startswith("Parteneri") else titlu.strip(),
                    "stare": r["stare"], "gest": r["gest"], "dimensiune": r["dimensiune"], "ecran_desenat": desenat,
                    "consola_erori": list(erori)})
        finally:
            ctx.close()
    assert (director / "martori.sha256").is_file()
