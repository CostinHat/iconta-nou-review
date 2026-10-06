# -*- coding: utf-8 -*-
"""PROBA în browser — anunțul „Versiune nouă” pe o filă încărcată ÎNAINTE de publicare și autentificată DUPĂ ea (comanda
Costin 06.10.2026, pct.1a: retestul s-a făcut pe codul vechi, fără ca aplicația să spună).

Scenariul măsurat pe producție: pagina de intrare deschisă la 19:12:40 (cod vechi), publicarea la 19:15:26, autentificarea la
19:46:51 fără reîncărcare. Aici, pe 8011 (baza de TEST): pagina se încarcă, amprenta servită (`.publicat.json` din directorul
publicat al serverului de probă) se schimbă, apoi utilizatorul se autentifică în aceeași filă (`sesiune.intra`, modulul deja
încărcat — exact ce face formularul de intrare). Se așteaptă: anunțul APARE. Martor: o filă încărcată DUPĂ publicare nu-l arată.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_versiune_la_incarcare.py \
        --publicat /home/costin/proba_l2/dupa/iconta_publicat/static/.publicat.json --iesire /tmp/.../versiune_dupa.json
"""
import argparse
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import auth_api, db  # noqa: E402

ASISTENT = "asistent@prisma-cont.test"


def _token(email):
    import psycopg2.extras as E
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u["id"])
        conn.rollback()
    return s["token"], s["user"]


def _intra_in_fila(pg, token, user):
    """Autentificarea din formularul de intrare, fără reîncărcare: `sesiune.intra` pe modulul DEJA încărcat al filei."""
    return pg.evaluate("""async ([t, u]) => {
        const e = performance.getEntriesByType('resource').map(x => x.name).find(n => /\\/static\\/js\\/sesiune\\.js/.test(n));
        const m = await import(e);
        m.sesiune.intra(t, u);
        return e; }""", [token, user])


def _stare_versiune(pg):
    return pg.evaluate("""async () => {
        const e = performance.getEntriesByType('resource').map(x => x.name).find(n => /\\/static\\/js\\/versiune\\.js/.test(n));
        if (!e) return null;
        const m = await import(e);
        return m.stare(); }""")


def _o_fila(pw, baza, cale, schimba_inainte_de_intrare, token, user):
    b = pw.chromium.launch(headless=True)
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_function("() => performance.getEntriesByType('resource').some(x => /\\/static\\/js\\/versiune\\.js/.test(x.name))",
                         timeout=20000)
    pg.wait_for_timeout(2500)                                # modulele încărcate și evaluate, fila stă pe ecranul public / de intrare
    r0 = {"ecran_inainte_de_intrare": pg.evaluate("() => document.body.innerText.slice(0, 80)")}
    r = dict(r0, stare_inainte_de_publicare=_stare_versiune(pg))
    if schimba_inainte_de_intrare:
        a = json.load(io.open(cale, encoding="utf-8"))
        a["commit"] = "proba-publicare-dupa-incarcarea-filei"
        io.open(cale, "w", encoding="utf-8").write(json.dumps(a, ensure_ascii=False, indent=2) + "\n")
    r["modul_sesiune"] = _intra_in_fila(pg, token, user).split("/static/")[-1]
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(3000)                                # prima verificare (`porneste`) a avut loc
    r["anunt_vizibil"] = pg.eval_on_selector_all(".versiune-noua", "els => els.filter(e => e.offsetParent !== null).length") > 0
    r["anunt_text"] = pg.eval_on_selector_all(".versiune-noua", "els => els.map(e => e.innerText.trim())")
    r["stare_versiune"] = _stare_versiune(pg)
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--publicat", required=True, help="amprenta servită de serverul de probă (.publicat.json)")
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    original = io.open(a.publicat, encoding="utf-8").read()
    token, user = _token(ASISTENT)
    r = {}
    try:
        with sync_playwright() as pw:
            r["fila_veche"] = _o_fila(pw, a.baza, a.publicat, True, token, user)       # publicare între încărcare și intrare
            r["martor_fila_noua"] = _o_fila(pw, a.baza, a.publicat, False, token, user)  # încărcată după publicare
    finally:
        io.open(a.publicat, "w", encoding="utf-8").write(original)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k, v in r.items():
        print(k, json.dumps(v, ensure_ascii=False)[:500])


if __name__ == "__main__":
    main()
