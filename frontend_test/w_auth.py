# -*- coding: utf-8 -*-
"""Helper comun: auth mintuit + navigare la firma tenant_003. Import: from w_auth import *"""
import os, json, traceback
from core import db, auth_api
import psycopg2.extras as E
from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
OUT = os.path.dirname(os.path.abspath(__file__))

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
        cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id WHERE u.email=%s", ("patron@prisma-cont.test",))
        u = cur.fetchone()
    _tok = auth_api.emite_token(u)
_USER = {"id": u["id"], "rol": u["rol"], "nume": u.get("nume"), "prenume": u.get("prenume"),
         "firm": u["accounting_firm_id"], "nume_firma": u.get("nume_firma"), "nume_tenant": None,
         "tenant_are_cabinet": False, "poate_pregati": bool(u.get("poate_pregati")),
         "poate_valida": bool(u.get("poate_valida")), "poate_depune": bool(u.get("poate_depune")),
         "bun_venit_vazut": True}
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_tok) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_USER)) + ");")


def new_page(pw):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1800}); ctx.add_init_script(INIT)
    return b, ctx.new_page()


def deschide_firma(pg):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("Comert Micro TVA", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000); pg.wait_for_timeout(400)


def shot(pg, nume):
    pg.screenshot(path=os.path.join(OUT, "t003_" + nume + ".png"), full_page=True)


def txt(pg, sel):
    e = pg.query_selector(sel)
    return e.inner_text().strip() if e else None
