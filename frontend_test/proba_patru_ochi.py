# -*- coding: utf-8 -*-
"""PROBA LIVE I1 — cabinet Prisma 1968: indicatorul patru-ochi in AMBELE stari, before/after.

Trei capturi pe acelasi cabinet, acelasi ecran:
  0_INAINTE   — codul VECHI simulat (indicatorul decide pe `activ` brut) -> "Validarea in doi ✓"
                pe un cabinet cu UN singur validator = MINCIUNA (defectul principal al lui I1)
  1_SUSPENDAT — codul NOU, aceeasi baza de date -> "suspendata — esti singurul validator"
  2_EFECTIV   — codul NOU, al doilea validator activat -> "Validarea in doi asistenti ✓" (adevarat)

Plus, pe fiecare stare: ecranul cozii + axe (desktop) + mobil Pixel 5.
Datele: al doilea validator e activat TEMPORAR si restaurat exact la final (igiena de date).
"""
import io
import json
import os
import sys

sys.path.insert(0, "/home/costin/iconta_nou")
sys.path.insert(0, "/home/costin/probe_t006")

from core import db, auth_api  # noqa: E402
import psycopg2.extras as E  # noqa: E402
from playwright.sync_api import sync_playwright  # noqa: E402

BAZA = "http://127.0.0.1:8010"
OUT = "/home/costin/iconta_nou/frontend_test"
CAB = 1968
ASISTENT = 6248
CABINET_JS = "/home/costin/iconta_nou/static/js/ecrane/cabinet.js"
AXE = open("/home/costin/iconta_nou/frontend_test/vizual/axe.min.js", encoding="utf-8").read()

db.init_pool()
with db.get_conn() as conn:
    with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
        cur.execute("SELECT u.*, af.nume AS nume_firma FROM public.users u "
                    "LEFT JOIN public.accounting_firms af ON af.id=u.accounting_firm_id "
                    "WHERE u.email=%s", ("patron@prisma-cont.test",))
        u = cur.fetchone()
    _tok = auth_api.emite_token(u)
_USER = {"id": u["id"], "rol": u["rol"], "nume": u.get("nume"), "prenume": u.get("prenume"),
         "firm": u["accounting_firm_id"], "nume_firma": u.get("nume_firma"), "nume_tenant": None,
         "tenant_are_cabinet": False, "poate_pregati": bool(u.get("poate_pregati")),
         "poate_valida": bool(u.get("poate_valida")), "poate_depune": bool(u.get("poate_depune")),
         "bun_venit_vazut": True}
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_tok) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_USER)) + ");")


def sql(q, args=()):
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, args)
        conn.commit()


def stare_backend():
    from core import coada_api
    with db.get_conn() as conn:
        return coada_api.patru_ochi_stare(conn, CAB)


def mut_cabinet_js(vechi, nou):
    t = io.open(CABINET_JS, encoding="utf-8").read()
    assert t.count(vechi) == 1, "ancora cabinet.js: %d aparitii" % t.count(vechi)
    io.open(CABINET_JS, "w", encoding="utf-8", newline="\n").write(t.replace(vechi, nou))


NOU_LINIE = "  const efectiv = !!st.efectiv;            // politica AND aplicabilitate = ce se aplica DE FAPT"
VECHI_LINIE = "  const efectiv = !!st.activ;  /* SIMULARE COD VECHI - proba before */"


def captura(pg, eticheta):
    """Deschide dashboardul cabinetului, citeste indicatorul, apoi coada."""
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(900)
    ind = pg.query_selector("#po-indicator")
    txt = ind.inner_text().strip() if ind else "(indicator absent)"
    culoare = ind.evaluate("e => getComputedStyle(e).color") if ind else "-"
    titlu_card = pg.eval_on_selector_all(
        '.cab-card', "els => els.map(e => e.querySelector('.cab-card-titlu')?.textContent).filter(Boolean)")
    p = os.path.join(OUT, "po_%s_dashboard.png" % eticheta)
    pg.screenshot(path=p, full_page=True)
    print("  INDICATOR: %-70r  culoare=%s" % (txt, culoare))
    print("  CARDURI  : %s" % ([t for t in titlu_card if "valid" in t.lower() or "depus" in t.lower()],))
    print("  SHOT", p)
    # ecranul cozii
    z = pg.query_selector('[data-cheie="validat"]')
    if z:
        z.click()
        pg.wait_for_timeout(1200)
        p2 = os.path.join(OUT, "po_%s_coada.png" % eticheta)
        pg.screenshot(path=p2, full_page=True)
        corp = pg.inner_text("body")
        butoane = pg.eval_on_selector_all(
            ".fereastra button, .ecran-continut button",
            "els => els.map(e => e.textContent.trim()).filter(t => /Aprob|Respinge|Depune|Confirm/i.test(t))")
        print("  COADA butoane:", butoane)
        print("  COADA intro  :", [l for l in corp.splitlines() if "valid" in l.lower()][:2])
        print("  SHOT", p2)
    return txt


def axe_pe_dashboard(pg, eticheta):
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(800)
    pg.add_script_tag(content=AXE)
    r = pg.evaluate("async () => { const r = await axe.run(document, "
                    "{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}); "
                    "return r.violations.map(v => ({id:v.id, impact:v.impact, n:v.nodes.length})); }")
    print("  AXE %-12s: %s" % (eticheta, r if r else "0 violari"))
    return r


def rezultat_mobil(pw, eticheta):
    d = pw.devices["Pixel 5"]
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(**d)
    ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000)
    pg.wait_for_timeout(900)
    lat = pg.evaluate("() => [document.body.scrollWidth, window.innerWidth]")
    ind = pg.query_selector("#po-indicator")
    h = ind.bounding_box()["height"] if ind else 0
    p = os.path.join(OUT, "po_%s_mobil.png" % eticheta)
    pg.screenshot(path=p, full_page=True)
    pg.add_script_tag(content=AXE)
    r = pg.evaluate("async () => { const r = await axe.run(document, "
                    "{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}); "
                    "return r.violations.map(v => ({id:v.id, impact:v.impact, n:v.nodes.length})); }")
    print("  MOBIL %-10s: body=%s viewport=%s  tinta indicator=%.0fpx  axe=%s"
          % (eticheta, lat[0], lat[1], h, r if r else "0 violari"))
    print("  SHOT", p)
    b.close()


with sync_playwright() as pw:
    def pagina():
        b = pw.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": 1280, "height": 1400})
        ctx.add_init_script(INIT)
        return b, ctx.new_page()

    print("\n=== STARE BACKEND (1 validator activ) ===")
    print(" ", stare_backend())

    # ---------- 0. INAINTE (cod vechi simulat) ----------
    print("\n=== 0_INAINTE — indicatorul decide pe `activ` brut (codul de pe HEAD) ===")
    mut_cabinet_js(NOU_LINIE, VECHI_LINIE)
    try:
        b, pg = pagina()
        t0 = captura(pg, "0_inainte")
        b.close()
    finally:
        mut_cabinet_js(VECHI_LINIE, NOU_LINIE)   # restaurare EXACTA
    assert "✓" in t0, "simularea codului vechi n-a reprodus bifa: %r" % t0

    # ---------- 1. DUPA, suspendat ----------
    print("\n=== 1_SUSPENDAT — cod nou, acelasi cabinet (1 validator) ===")
    b, pg = pagina()
    t1 = captura(pg, "1_suspendat")
    axe_pe_dashboard(pg, "suspendat")
    b.close()
    rezultat_mobil(pw, "1_suspendat")
    assert "✓" not in t1 and "suspendat" in t1.lower(), t1

    # ---------- 2. DUPA, efectiv (al doilea validator) ----------
    print("\n=== 2_EFECTIV — al doilea validator activat TEMPORAR ===")
    sql("UPDATE public.users SET activ=true, poate_pregati=true, poate_valida=true WHERE id=%s",
        (ASISTENT,))
    try:
        print(" ", stare_backend())
        b, pg = pagina()
        t2 = captura(pg, "2_efectiv")
        axe_pe_dashboard(pg, "efectiv")
        b.close()
        rezultat_mobil(pw, "2_efectiv")
        assert "✓" in t2, t2
    finally:
        sql("UPDATE public.users SET activ=false, poate_pregati=false, poate_valida=false, "
            "poate_depune=false WHERE id=%s", (ASISTENT,))
        print("\n=== IGIENA: asistentul 6248 restaurat ===")
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, activ, poate_pregati, poate_valida, poate_depune "
                            "FROM public.users WHERE accounting_firm_id=%s ORDER BY id", (CAB,))
                for r in cur.fetchall():
                    print("   ", r)
        print("  stare backend finala:", stare_backend())

print("\nPROBA OK — before/after pe 1968, ambele stari ale indicatorului.")
