# -*- coding: utf-8 -*-
"""PROBA UI — D394 Î2: firma exceptată de la casa de marcat (Date firmă) și chitanța fără factură (Casă). Rulează cu app
viu pe PROBA_BAZA (8011, baza de test), pe firma implicită a contului (`w_auth`, tenant_003).

Pregătire (baza de test, anulată la final): o chitanță fără factură și fără cotă, emisă „înainte de marcare” (încasare
de creanță, 5311=4111), apoi firma marcată exceptată (lit. i). Starea profilului se restaurează, rândurile create se șterg.
A. Date firmă: blocul „Casa de marcat” — „Activitate exceptată” = Da, activitatea vizibilă -> axe.
B. Casă: „+ Chitanță fără factură” -> fără cotă = eroare pe câmp; cu 21% -> chitanța emisă, nota 5311=707 + 5311=4427 ->
   axe pe formular deschis.
C. Rândul chitanței vechi: «Stabilește cota» fără cotă = eroare pe câmp; cu 21% -> nota refăcută -> axe.
D. Telefon (Pixel 5): Casă cu formularul deschis — revărsare orizontală, ținte sub 24px; axe.
"""
import datetime
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
from core import db, casa_api, repo_casa  # noqa: E402

IESIRE = os.path.join(HERE, "proba_d394_i2_ui.json")
SCHEMA = "tenant_003"
AZI = datetime.date.today().isoformat()
MOBIL_JS = """(sel) => {
    const z = document.querySelector(sel) || document.body;
    const sub = r => r.width > 0 && (r.width < 24 || r.height < 24);
    const el = [...z.querySelectorAll('button,input,select')].filter(e => e.offsetParent !== null);
    return {revarsare_x: document.documentElement.scrollWidth > document.documentElement.clientWidth,
            tinte_sub_24: el.filter(e => sub(e.getBoundingClientRect())).map(e => e.id || e.textContent.trim().slice(0, 20))};
}"""


def _pregateste():
    db.init_pool()
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT activitate_exceptata_amef, activitate_amef FROM %s.firma_profil WHERE id = 1" % SCHEMA)
            stare = cur.fetchone()
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM %s.chitante" % SCHEMA)
            prag = cur.fetchone()[0]
            cur.execute("SELECT COALESCE(MAX(id), 0) FROM %s.casa_operatiuni" % SCHEMA)
            prag_op = cur.fetchone()[0]
        rez = casa_api.adauga(c, SCHEMA, {"data": AZI, "categorie": "incasare_client", "suma": 242,
                                          "document": "CH-PROBA", "partener": "Maria Ionescu (proba)"})
        with c.cursor() as cur:
            cid = repo_casa.adauga_chitanta(cur, SCHEMA, "PRB", 1, AZI, None, "Maria Ionescu (proba)", None, 242,
                                            "reparatie (proba)", rez["id"], rez["inregistrare_id"])[0]
            cur.execute("UPDATE %s.firma_profil SET activitate_exceptata_amef = true, activitate_amef = 'i' "
                        "WHERE id = 1" % SCHEMA)
        c.commit()
    return stare, prag, prag_op, cid


def _curata(stare, prag, prag_op):
    with db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT inregistrare_id FROM %s.casa_operatiuni WHERE id > %%s" % SCHEMA, (prag_op,))
            note = [r[0] for r in cur.fetchall() if r[0]]
            cur.execute("DELETE FROM %s.chitante WHERE id > %%s" % SCHEMA, (prag,))
            cur.execute("DELETE FROM %s.casa_operatiuni WHERE id > %%s" % SCHEMA, (prag_op,))
            if note:
                cur.execute("DELETE FROM %s.inregistrari WHERE id = ANY(%%s)" % SCHEMA, (note,))
            cur.execute("UPDATE %s.firma_profil SET activitate_exceptata_amef = %%s, activitate_amef = %%s WHERE id = 1"
                        % SCHEMA, (stare[0], stare[1]))
        c.commit()


def _casa(pg):
    w_auth.deschide_firma(pg)
    pg.click("#fa-casa", timeout=8000)
    pg.wait_for_selector("#c-toggle", timeout=15000)


def main():
    r = {}
    stare, prag, prag_op, cid = _pregateste()
    try:
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            ctx = b.new_context(viewport={"width": 1280, "height": 1400})
            ctx.add_init_script(w_auth.INIT)
            pg = ctx.new_page()
            # A. Date firmă
            w_auth.deschide_firma(pg)
            pg.click("#fa-datefirma")
            pg.wait_for_selector("#df-activitate_exceptata_amef", timeout=15000)
            r["df_exceptata"] = pg.input_value("#df-activitate_exceptata_amef")
            r["df_activitate"] = pg.input_value("#df-activitate_amef")
            r["df_activitate_vizibila"] = pg.is_visible("#df-activitate_amef")
            r["axe_date_firma"] = axe_scan.scaneaza(pg)
            # B. Casă — chitanța fără factură
            _casa(pg)
            r["buton_chitanta"] = pg.locator("#c-chit-toggle").count()
            pg.click("#c-chit-toggle")
            pg.fill("#ch-data", AZI)
            pg.fill("#ch-suma", "121")
            pg.click("#ch-emite")
            pg.wait_for_timeout(800)
            r["fara_cota_invalid"] = pg.get_attribute("#ch-cota", "aria-invalid")
            pg.select_option("#ch-cota", "21")
            pg.fill("#ch-client", "Ion Popescu (proba)")
            pg.fill("#ch-repr", "reparatie centrala (proba)")
            pg.click("#ch-emite")
            pg.wait_for_timeout(3000)
            r["mesaj_emitere"] = (pg.text_content(".pf-intro") or "").strip()
            r["axe_casa"] = axe_scan.scaneaza(pg)
            # C. Stabilește cota pe chitanța veche
            sel = "button[data-cota='%s']" % cid
            r["buton_cota"] = pg.locator(sel).count()
            if r["buton_cota"]:
                pg.click(sel)
                pg.wait_for_timeout(600)
                r["cota_goala_invalid"] = pg.get_attribute("#c-cota-%s" % cid, "aria-invalid")
                pg.select_option("#c-cota-%s" % cid, "21")
                pg.click(sel)
                pg.wait_for_timeout(3000)
                r["mesaj_cota"] = (pg.text_content(".pf-intro") or "").strip()
                r["buton_cota_dupa"] = pg.locator(sel).count()
                r["axe_casa_dupa_cota"] = axe_scan.scaneaza(pg)
            ctx.close()
            # D. telefon
            m = b.new_context(**pw.devices["Pixel 5"])
            m.add_init_script(w_auth.INIT)
            pm = m.new_page()
            _casa(pm)
            pm.click("#c-chit-toggle")
            pm.wait_for_timeout(500)
            r["mobil_casa"] = pm.evaluate(MOBIL_JS, ".fereastra-corp")
            r["axe_mobil_casa"] = axe_scan.scaneaza(pm)
            b.close()
    finally:
        _curata(stare, prag, prag_op)
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT activitate_exceptata_amef, activitate_amef FROM %s.firma_profil WHERE id = 1" % SCHEMA)
        r["profil_restaurat"] = list(cur.fetchone()) == list(stare)
    json.dump(r, open(IESIRE, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print("Date firmă: exceptată=%r activitate=%r vizibilă=%r" % (r.get("df_exceptata"), r.get("df_activitate"),
                                                               r.get("df_activitate_vizibila")))
    print("Casă: buton «+ Chitanță fără factură» %s · fără cotă aria-invalid=%r" % (r.get("buton_chitanta"),
                                                                                  r.get("fara_cota_invalid")))
    print("Casă: după emitere: %r" % r.get("mesaj_emitere", "")[:200])
    print("Casă: «Stabilește cota» %s · goală aria-invalid=%r · după: %r · butonul mai e: %s" % (
        r.get("buton_cota"), r.get("cota_goala_invalid"), r.get("mesaj_cota", "")[:200], r.get("buton_cota_dupa")))
    for k in ("axe_date_firma", "axe_casa", "axe_casa_dupa_cota", "axe_mobil_casa"):
        print("%s: %s" % (k, json.dumps(r.get(k), ensure_ascii=False)[:200]))
    print("mobil Casă:", r.get("mobil_casa"), "· profil restaurat:", r.get("profil_restaurat"))


if __name__ == "__main__":
    main()
