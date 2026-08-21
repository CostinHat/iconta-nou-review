# -*- coding: utf-8 -*-
"""Provoacă un blocaj (regula 14 pct.4): fișier salariați cu CNP valid fără normă + CNP invalid.
Citește ce scrie pe ecran la preview (gateazaPreview Q5 + avertismentul CNP)."""
import os, json, traceback
from core import db, auth_api
import psycopg2.extras as E
from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
OUT = os.path.dirname(os.path.abspath(__file__))
BAD = os.path.join(OUT, "bad_salariati.csv")
open(BAD, "w", encoding="utf-8").write("nume,cnp,brut\nPOP ION,1960101078911,3000\nBAD GUY,1234567890123,4000\n")

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
        cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id WHERE u.email=%s", ("patron@prisma-cont.test",))
        u = cur.fetchone()
    tok = auth_api.emite_token(u)
USER = {"id": u["id"], "rol": u["rol"], "nume": u.get("nume"), "prenume": u.get("prenume"),
        "firm": u["accounting_firm_id"], "nume_firma": u.get("nume_firma"), "nume_tenant": None,
        "tenant_are_cabinet": False, "poate_pregati": bool(u.get("poate_pregati")),
        "poate_valida": bool(u.get("poate_valida")), "poate_depune": bool(u.get("poate_depune")),
        "bun_venit_vazut": True}
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(tok) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(USER)) + ");")

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1700}); ctx.add_init_script(INIT)
    pg = ctx.new_page(); rez = {}
    try:
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
        pg.get_by_text("Comert Micro TVA", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-import", timeout=12000); pg.wait_for_timeout(300)
        pg.click("#fa-import"); pg.wait_for_timeout(700)
        pg.get_by_text("Salariați", exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
        pg.screenshot(path=os.path.join(OUT, "t003_sal_01_import.png"), full_page=True)
        # upload fisier stricat
        pg.set_input_files("#mig-file", BAD); pg.wait_for_timeout(1500)
        pg.screenshot(path=os.path.join(OUT, "t003_sal_02_preview_erori.png"), full_page=True)
        rez["caseta_atentie"] = [e.inner_text().strip() for e in pg.query_selector_all(".caseta-atentie")]
        rez["salveaza_disabled"] = pg.eval_on_selector("#mig-salveaza-sal", "e=>e.disabled") if pg.query_selector("#mig-salveaza-sal") else "(fara buton)"
        rez["banda"] = pg.eval_on_selector(".mig-coer", "e=>e.innerText") if pg.query_selector(".mig-coer") else None
        # avertismentul CNP pe rand: title= (inaccesibil, Q12) sau vizibil?
        rez["cnp_warn_title"] = pg.eval_on_selector_all(".mig-cnp-no", "els=>els.map(e=>({vizibil:e.innerText.trim(), title:e.getAttribute('title')}))")
    except Exception as e:
        rez["error"] = str(e); traceback.print_exc(); pg.screenshot(path=os.path.join(OUT, "t003_sal_ERR.png"))
    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
