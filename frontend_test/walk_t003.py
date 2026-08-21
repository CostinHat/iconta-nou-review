# -*- coding: utf-8 -*-
"""Audit vizual tenant_003 (Comert Micro TVA SRL, cabinet 1968) — parcurge migrarea.
Auth: token mintuit direct pentru patron@prisma-cont.test (fara parola)."""
import os, json, traceback
from core import db, auth_api
import psycopg2.extras as E
from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
OUT = os.path.dirname(os.path.abspath(__file__))
FIRMA = "Comert Micro TVA"

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
        cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u "
                    "LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id "
                    "WHERE u.email=%s", ("patron@prisma-cont.test",))
        u = cur.fetchone()
    tok = auth_api.emite_token(u)
USER = {"id": u["id"], "rol": u["rol"], "nume": u.get("nume"), "prenume": u.get("prenume"),
        "firm": u["accounting_firm_id"], "nume_firma": u.get("nume_firma"),
        "nume_tenant": None, "tenant_are_cabinet": False,
        "poate_pregati": bool(u.get("poate_pregati")), "poate_valida": bool(u.get("poate_valida")),
        "poate_depune": bool(u.get("poate_depune")), "bun_venit_vazut": bool(u.get("bun_venit_vazut_la"))}
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(tok) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(USER)) + ");")


def shot(pg, nume):
    pg.screenshot(path=os.path.join(OUT, "t003_" + nume + ".png"), full_page=True)


def txt(pg, sel):
    e = pg.query_selector(sel)
    return e.inner_text().strip() if e else None


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    rez = {}
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(400)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
        pg.get_by_text(FIRMA, exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000); pg.wait_for_timeout(400)
        shot(pg, "00_meniu_firma")
        # cardurile firmei (ce module are firma)
        rez["carduri_firma"] = pg.eval_on_selector_all("[id^=fa-]",
            "els => els.map(e => ({id:e.id, txt:e.innerText.trim().split(String.fromCharCode(10))[0]}))")
        # --- IMPORT DATE (meniul de migrare per firma) ---
        pg.click("#fa-import"); pg.wait_for_timeout(800)
        pg.wait_for_selector("body", timeout=8000); pg.wait_for_timeout(600)
        shot(pg, "01_import_meniu")
        # straturile de migrare afisate + starile lor
        rez["import_meniu_text"] = (txt(pg, ".pf-container") or txt(pg, "main") or txt(pg, "body"))[:2500]
    except Exception as e:
        rez["error"] = str(e); traceback.print_exc(); shot(pg, "ERR")
    print(json.dumps(rez, ensure_ascii=False, indent=2)[:4000])
    b.close()
