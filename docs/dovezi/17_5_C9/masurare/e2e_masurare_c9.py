# -*- coding: utf-8 -*-
"""17.5-C9 pct.5 — exemplul reproductibil al uneltei de măsurare Pilot pe un cod existent (F018, Parteneri F1), la 1366×768 și 603×590.
Rulat numai prin lansatorul nativ al probelor pe 8019 (docs/dovezi/17_5_Q12/rulare_8019.sh … scripts/e2e_poarta.py --doar=…), care
restaurează baza înainte și după. Gestul: Firme › F1 › Parteneri; măsura fiecărei celule: `scripts/masurare_pilot.py::masoara_celula`
(cheia `dom:` citită prin `verifica_pas.observa_pagina`), cu captura și manifestul martorilor. Judecata o face apoi unealta:
  MASURARE_COMMIT=$(git rev-parse HEAD) sh docs/dovezi/17_5_Q12/rulare_8019.sh --restaureaza <iesire> --doar=../../docs/dovezi/17_5_C9/masurare/e2e_masurare_c9.py
  ./venv/bin/python scripts/masurare_pilot.py judeca docs/dovezi/17_5_C9/masurare/inventar_F018_exemplu.tsv <capturi>/17_5_C9_masurare <commit> <iesire.tsv>"""
import os
import subprocess
import sys
from pathlib import Path

RAD = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAD / "scripts"))
RAD_E2E = RAD / "frontend_test" / "e2e"
sys.path.insert(0, str(RAD_E2E))
sys.path.insert(0, str(RAD_E2E.parent))
import importlib.util as _iu  # noqa: E402
_spec = _iu.spec_from_file_location("conftest_e2e_c9", RAD_E2E / "conftest.py")   # același bootstrap ca proba Q12 (docs/dovezi/17_5_Q12/e2e_probe_q12.py)
conftest_e2e = _iu.module_from_spec(_spec)
_spec.loader.exec_module(conftest_e2e)
if getattr(sys.modules.get("conftest"), "sesiune", None) is None:
    sys.modules["conftest"] = conftest_e2e


def test_masurare_c9_F018():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            _masoara(browser)
        finally:
            browser.close()


def _masoara(browser):
    from conftest import BAZA, CAPTURI, Ecran, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import TOP, F1, firma, origine_proba
    import masurare_pilot as mp

    origine_proba(BAZA)
    # commitul măsurat: lansatorul servește un export al indexului (fără .git), deci apelantul îl dă (`MASURARE_COMMIT=$(git rev-parse HEAD)`)
    commit = os.environ.get("MASURARE_COMMIT") or subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    assert len(commit) == 40, "commitul măsurat lipsește (MASURARE_COMMIT)"
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
