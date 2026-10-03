# -*- coding: utf-8 -*-
"""PROBA UI — lot 19: bifa „C&D” din registrul Mijloace fixe (defectul 11) și refuzul de emitere pentru capitalul social
lipsă (defectul 12). Rulează cu app viu pe PROBA_BAZA (8011, baza de test), pe firma implicită a contului (`w_auth`,
tenant_003).

A. Registrul: un activ TEMPORAR (inserat în tenant_003 pe baza de test, șters la final) -> butonul „C&D: nu” -> clic ->
   „C&D: da” (citit din registru, după reîncărcare) -> axe desktop + telefon (revărsare, ținte sub 24px).
B. Emiterea pe firma fără formă juridică/capital: denumire + CUI + o linie -> «Emite» -> caseta de refuz cu ce lipsește,
   temeiul și butonul «Deschide Date firmă»; formularul rămâne cum a fost scris (valorile citite din casete) -> butonul
   deschide Date firmă cu blocul „Capital social” -> axe pe ambele stări + telefon pe Date firmă.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "vizual"))
sys.path.insert(0, os.path.dirname(HERE))

from playwright.sync_api import sync_playwright  # noqa: E402
import w_auth  # noqa: E402
from vizual import axe_scan  # noqa: E402
from core import db  # noqa: E402

IESIRE = os.path.join(HERE, "proba_lot19_ui.json")
SCHEMA = "tenant_003"
MOBIL_JS = """(sel) => {
    const z = document.querySelector(sel) || document.body;
    const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
    const el = [...z.querySelectorAll('button,input,select')].filter(e => e.offsetParent !== null);
    return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            tinte_sub_24: el.filter(e => sub(e.getBoundingClientRect())).map(e => e.id || e.textContent.trim().slice(0, 20))};
}"""


def _activ_temporar():
    db.init_pool()
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("INSERT INTO %s.mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, "
                        "dnf_luni, data_pif, metoda, activ) VALUES ('PRB-CD','Spectrometru PROBA UI','2132','2813',60000,0,"
                        "60,'2026-01-15','liniara',true) RETURNING id" % SCHEMA)
            mid = cur.fetchone()[0]
        c.commit()
    return mid


def _sterge(mid):
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DELETE FROM %s.mijloace_fixe WHERE id = %%s" % SCHEMA, (mid,))
        c.commit()


def _registru(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-mijloace")
    pg.wait_for_selector("table.fd-tabel", timeout=15000)


def _emitere(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-facturi", timeout=8000)
    pg.wait_for_timeout(1400)
    pg.get_by_text("Emite", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#em-emite", timeout=15000)


def main():
    r = {}
    mid = _activ_temporar()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            ctx = b.new_context(viewport={"width": 1280, "height": 1400})
            ctx.add_init_script(w_auth.INIT)
            pg = ctx.new_page()
            # A. registrul
            _registru(pg)
            sel = "button[data-cd='%s']" % mid
            r["buton_inainte"] = pg.text_content(sel).strip()
            pg.click(sel)
            pg.wait_for_timeout(1500)
            pg.wait_for_selector(sel, timeout=8000)
            r["buton_dupa"] = pg.text_content(sel).strip()
            r["axe_registru"] = axe_scan.scaneaza(pg)
            # B. emiterea
            _emitere(pg)
            pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
            pg.fill("#em-cui", "14399840")      # cifra de control verificată
            pg.fill("#em-l0-descriere", "Consultanta contabila")
            pg.fill("#em-l0-cantitate", "1")
            pg.fill("#em-l0-pret_unitar", "100")
            pg.click("#em-emite")
            pg.wait_for_timeout(6000)
            r["rezultat"] = (pg.text_content("#em-rezultat") or "").strip()
            r["buton_date_firma"] = pg.locator("#em-deschide-date-firma").count()
            r["pastrat"] = {"denumire": pg.input_value("#em-l0-descriere"), "nume": pg.input_value("#em-nume"),
                            "cui": pg.input_value("#em-cui"), "pret": pg.input_value("#em-l0-pret_unitar")}
            r["axe_refuz"] = axe_scan.scaneaza(pg)
            if r["buton_date_firma"]:
                pg.click("#em-deschide-date-firma")
                pg.wait_for_selector("#df-forma_juridica", timeout=15000)
                r["date_firma_capital"] = pg.locator("#df-forma_juridica, #df-capital_subscris, #df-capital_varsat").count()
                r["axe_date_firma"] = axe_scan.scaneaza(pg)
            ctx.close()
            m = b.new_context(**pw.devices["Pixel 5"])
            m.add_init_script(w_auth.INIT)
            pm = m.new_page()
            _registru(pm)
            r["mobil_registru"] = pm.evaluate(MOBIL_JS, ".fereastra-corp")
            r["axe_mobil_registru"] = axe_scan.scaneaza(pm)
            w_auth.deschide_firma(pm)
            pm.click("#fa-datefirma")
            pm.wait_for_selector("#df-forma_juridica", timeout=15000)
            r["mobil_date_firma"] = pm.evaluate(MOBIL_JS, ".fereastra-corp")
            r["axe_mobil_date_firma"] = axe_scan.scaneaza(pm)
            b.close()
    finally:
        _sterge(mid)
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("registru: buton %r -> %r" % (r.get("buton_inainte"), r.get("buton_dupa")))
    print("emitere: rezultat %r" % r.get("rezultat", "")[:260])
    print("emitere: buton «Deschide Date firmă» %s · formular păstrat %s" % (r.get("buton_date_firma"), r.get("pastrat")))
    print("Date firmă: câmpuri capital %s" % r.get("date_firma_capital"))
    for k in ("axe_registru", "axe_refuz", "axe_date_firma", "axe_mobil_registru", "axe_mobil_date_firma"):
        print("%s: %s" % (k, json.dumps(r.get(k), ensure_ascii=False)[:200]))
    print("mobil registru:", r.get("mobil_registru"), "· mobil Date firmă:", r.get("mobil_date_firma"))


if __name__ == "__main__":
    main()
