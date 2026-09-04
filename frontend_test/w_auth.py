# -*- coding: utf-8 -*-
"""Helper comun: auth mintuit + navigare la firma tenant_003. Import: from w_auth import *

[LOTUL 10, 04.09.2026] RECONSTRUIT din `__pycache__/w_auth.cpython-312.pyc`. Sursa fusese stearsa
de pe disc pe 26.08 odata cu `b87dad49` („Scoate din urmarire cele 234 de artefacte maturate din
greseala"), iar de atunci **24 de fisiere** — printre ele `interactiune_scan`, `axe_scan`,
`mobil_scan` si `nav_ecrane`, adica toata infrastructura vizuala gardata — se importau dintr-un
bytecode de 4,6 KB. Nimic nu era rosu: Python incarca `.pyc`-ul fara sa-i ceara sursa. *Un
`find -name __pycache__ -delete` — curatenia obisnuita — ar fi oprit tacut tot ce se sprijina
aici.* Vezi `core/test_infra_vizuala.py`, care de acum cere SURSA, nu doar importul.
"""
import json
import os

from playwright.sync_api import sync_playwright  # noqa: F401  (reexportat: probele il importa de aici)

from core import db, auth_api

BAZA = "http://127.0.0.1:8010"
OUT = os.path.dirname(os.path.abspath(__file__))


def _utilizator():
    """Tokenul se MINTUIESTE local (nu prin `/auth/login`): probele vizuale nu masoara
    autentificarea, iar o parola in fisier ar fi al doilea loc in care traieste un secret."""
    import psycopg2.extras as E
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001
        pass
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u "
                        "LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id "
                        "WHERE u.email=%s", ("patron@prisma-cont.test",))
            u = cur.fetchone()
        conn.rollback()
    tok = auth_api.emite_token(dict(u))
    user = {
        "id": u.get("id"), "rol": u.get("rol"), "nume": u.get("nume"),
        "prenume": u.get("prenume"), "firm": u.get("accounting_firm_id"),
        "nume_firma": u.get("nume_firma"), "nume_tenant": None,
        "tenant_are_cabinet": False,
        "poate_pregati": bool(u.get("poate_pregati")),
        "poate_valida": bool(u.get("poate_valida")),
        "poate_depune": bool(u.get("poate_depune")),
        "bun_venit_vazut": True,
    }
    return tok, user


_tok, _USER = _utilizator()

INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_tok) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_USER)) + ");")


def new_page(pw):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1200, "height": 1800})
    ctx.add_init_script(INIT)
    return b, ctx.new_page()


def deschide_firma(pg):
    """Cabinet -> Firme -> Firme existente -> „Comert Micro TVA" (tenant_003)."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(300)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000)
    pg.wait_for_timeout(300)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000)
    pg.wait_for_timeout(300)
    pg.get_by_text("Comert Micro TVA", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-import, #fa-datefirma", timeout=12000)
    pg.wait_for_timeout(400)


def shot(pg, nume):
    pg.screenshot(path=os.path.join(OUT, "t003_" + nume + ".png"), full_page=True)


def txt(pg, sel):
    """Textul primului element care se potriveste, sau „" daca nu exista."""
    e = pg.query_selector(sel)
    return (e.inner_text() or "").strip() if e else ""
