# -*- coding: utf-8 -*-
"""UNEALTA — scan de INTERACTIUNE + a11y consolidat, per ecran (nav_ecrane.ECRANE).

Verifica ce NU e aparent (cerut de Costin 19.08.2026): pe langa axe/contrast/diacritice (aparent),
APASA butoanele si COMPLETEAZA casetele si vede daca se strica ceva:
  - COMPLETARE: umple fiecare input/textarea vizibil cu text lung+diacritice la limita -> prinde
    overflow-x (layout rupt) si elemente impinse dincolo de viewport (aliniere rupta / text impins afara).
  - APASARE: apasa butoanele din CONTINUTUL ecranului (.fereastra), ne-destructive -> prinde erori JS de
    consola/pagina + rupturi de layout. Cand un buton inchide/navigheaza ecranul, RE-navigheaza si continua
    (acoperire reala, nu doar primul buton). Sare butoanele destructive (salveaza/sterge/importa/depune/...).
  - a11y: axe pe DESKTOP + pe MOBIL (Pixel 5) — combinatia prinde scrollable-region-focusable (apare doar cand
    continutul depaseste viewportul); tinte de atingere <24 (AA); title-only pierdut pe touch.

Scrie `acoperire_vizuala.json` (per ecran + ui_hash-ul surselor UI) — citit de gardul
core/test_acoperire_vizuala.py, care PICA daca UI-ul s-a schimbat de la ultimul scan sau daca scanul a gasit
vreo violare. Ruleaza cu serverul pe 127.0.0.1:8010 + PYTHONPATH pe frontend_test[/vizual].
"""
import os
import sys
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_RAD = os.path.abspath(os.path.join(_HERE, "..", ".."))
sys.path.insert(0, os.path.join(_RAD, "frontend_test"))
sys.path.insert(0, _HERE)

from playwright.sync_api import sync_playwright  # noqa: E402
from w_auth import INIT  # noqa: E402
from nav_ecrane import ECRANE  # noqa: E402
from acoperire_hash import ui_hash, ARTEFACT  # noqa: E402

AXE = open(os.path.join(_HERE, "axe.min.js"), encoding="utf-8").read()
EDGE = "Denumire foarte lunga cu diacritice ăâîșț ĂÂÎȘȚ 01234567890 pentru testul de limita si aliniere"
DESTRUCTIV = ("salv", "sterg", "șterg", "import", "depun", "trimit", "confirm", "adaug", "genereaz", "finaliz")
MARKERI = {
    "vector_fiscal": "#vf-salveaza", "plan_conturi": "#pc-adauga", "solduri_parteneri": "#mig-drop",
    "import_mijloace_fixe": ".fereastra", "stat_plata": ".fereastra", "declaratii": ".fereastra",
}


def _axe(pg):
    pg.evaluate(AXE)
    return pg.evaluate(
        "async () => { const r = await axe.run(document, {resultTypes:['violations']});"
        " return r.violations.map(v=>({id:v.id, impact:v.impact, n:v.nodes.length,"
        " target:(v.nodes[0]||{}).target})); }")


def _completare(pg):
    for h in pg.query_selector_all("input[type=text], input:not([type]), textarea, input[type=search]"):
        try:
            if h.is_visible() and not h.get_attribute("readonly"):
                h.fill(EDGE)
        except Exception:  # noqa: BLE001
            continue
    pg.wait_for_timeout(250)
    return pg.evaluate("""() => {
        const vw = window.innerWidth;
        const peste = [];
        document.querySelectorAll('.fereastra *').forEach(e => {
            const r = e.getBoundingClientRect();
            if (r.width > 0 && r.height > 0 && r.right > vw + 2 && getComputedStyle(e).position !== 'fixed')
                peste.push((e.className || e.tagName) + ' right=' + Math.round(r.right));
        });
        return {overflow_x: document.body.scrollWidth > vw + 2, peste_viewport: peste.slice(0, 8)};
    }""")


def _apasare(pg, nav, marker):
    """Apasa butoanele din .fereastra (continutul ecranului), ne-destructive. Re-navigheaza cand un buton
    inchide ecranul (marker disparut), ca sa le acopere pe toate. Prinde erori JS + layout rupt."""
    erori = []
    pg.on("console", lambda m: erori.append("CONSOLE:" + m.text[:120]) if m.type == "error" else None)
    pg.on("pageerror", lambda e: erori.append("PAGEERROR:" + str(e)[:120]))
    sel = ".fereastra button:not([disabled]), .fereastra [role=button]"
    total = len(pg.query_selector_all(sel))
    apasate = 0
    for i in range(min(total, 24)):
        btns = pg.query_selector_all(sel)
        if i >= len(btns):
            break
        b = btns[i]
        try:
            if not b.is_visible():
                continue
            t = (b.inner_text() or "").strip().lower()
            if any(d in t for d in DESTRUCTIV):
                continue
            b.click(timeout=1200)
            apasate += 1
            pg.wait_for_timeout(120)
            if marker and not pg.query_selector(marker):
                nav(pg)  # a navigat/inchis -> restaureaza ecranul, continua cu urmatorul buton
        except Exception:  # noqa: BLE001
            if marker and not pg.query_selector(marker):
                try:
                    nav(pg)
                except Exception:  # noqa: BLE001
                    break
            continue
    layout_rupt = pg.evaluate("document.body.scrollWidth > window.innerWidth + 2")
    return {"vazute": total, "apasate": apasate, "console_errors": erori, "layout_rupt_dupa_click": layout_rupt}


def _mobil(pg):
    return pg.evaluate("""() => {
        const vw = window.innerWidth;
        const small = [];
        document.querySelectorAll('button, a, input, [role=button]').forEach(e=>{
            const r = e.getBoundingClientRect();
            if (r.width>0 && r.height>0 && (r.width<24 || r.height<24))
                small.push((e.className||e.tagName)+' '+Math.round(r.width)+'x'+Math.round(r.height));
        });
        let titleUnic = 0;
        document.querySelectorAll('[title]').forEach(e=>{
            const t=(e.getAttribute('title')||'').trim();
            if (t && !(e.innerText||'').trim() && !e.getAttribute('aria-label')) titleUnic++;
        });
        return {tap_sub24: small.slice(0,10), overflow_x: document.body.scrollWidth>vw+2, title_unic: titleUnic};
    }""")


def _pagina(pw, mobil):
    b = pw.chromium.launch(headless=True)
    if mobil:
        ctx = b.new_context(viewport={"width": 393, "height": 851}, is_mobile=True, has_touch=True)
    else:
        ctx = b.new_context(viewport={"width": 1200, "height": 1800})
    ctx.add_init_script(INIT)
    return b, ctx.new_page()


def scan():
    rez = {"ui_hash": ui_hash(), "ecrane": {}}
    with sync_playwright() as pw:
        for nume, nav in ECRANE:
            r = {}
            b, pg = _pagina(pw, False)
            try:
                nav(pg)
                r["axe_desktop"] = _axe(pg)
                r["apasare"] = _apasare(pg, nav, MARKERI.get(nume))
                r["completare"] = _completare(pg)
            except Exception as e:  # noqa: BLE001
                r["error"] = str(e)[:200]
            b.close()
            b2, pg2 = _pagina(pw, True)
            try:
                nav(pg2)
                r["axe_mobil"] = _axe(pg2)
                r["mobil"] = _mobil(pg2)
            except Exception as e:  # noqa: BLE001
                r["error_mobil"] = str(e)[:200]
            b2.close()
            rez["ecrane"][nume] = r
            print("scanat:", nume, "| apasate", r.get("apasare", {}).get("apasate"), "/", r.get("apasare", {}).get("vazute"))
    with open(ARTEFACT, "w", encoding="utf-8") as f:
        json.dump(rez, f, ensure_ascii=False, indent=1)
    print("ARTEFACT scris ui_hash", rez["ui_hash"])


if __name__ == "__main__":
    scan()
