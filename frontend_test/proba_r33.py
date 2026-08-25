# -*- coding: utf-8 -*-
"""PROBA R33 pe procesul VIU: semnalul de coerenta nota-vs-D112 apare la propunere, arata AMBELE
cifre, si NU blocheaza.

De ce pe procesul viu si nu doar pe AST (METODA §24): pe 25.08 o proba a dat "16/16" fiindca JS-ul
de pe disc era nou si serviciul vechi. Aici se citeste ce vede omul, dupa restart.

Ce se asteapta INAINTE de rulare (METODA §1 - asteptarea scrisa INAINTE):
  1. butonul "Contabilizeaza statul" exista pe ecranul de stat de plata;
  2. apasarea lui produce o propunere cu linii de nota si un semnal;
  3. daca sunt divergente, tabelul lor are coloane pentru NOTA si pentru D112, cu cifre in
     amandoua - nu doar "exista o divergenta";
  4. butonul "Scrie nota ciorna" ramane APASABIL cand exista divergente (semnaleaza, nu blocheaza).
"""
import json
import os
import urllib.request

from playwright.sync_api import sync_playwright

BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1)
        CFG[k] = v
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")
AICI = os.path.dirname(__file__)

rez = {}
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for eticheta, vp in (("desktop", {"width": 1100, "height": 1600}),
                         ("mobil", {"width": 393, "height": 851})):
        ctx = b.new_context(viewport=vp)
        ctx.add_init_script(INIT)
        pg = ctx.new_page()
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-card", timeout=15000)
        pg.wait_for_timeout(500)
        pg.get_by_text("Firme", exact=True).first.click(timeout=8000)
        pg.wait_for_timeout(700)
        pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("button.firme-rand", timeout=10000)
        pg.wait_for_timeout(400)
        pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
        pg.wait_for_selector("#fa-salariati", timeout=10000)
        pg.click("#fa-salariati")
        pg.wait_for_selector("#sp-contare", timeout=12000)
        rez["%s_buton" % eticheta] = True
        pg.screenshot(path=os.path.join(AICI, "r33_%s_1_inainte.png" % eticheta), full_page=True)
        pg.click("#sp-contare")
        pg.wait_for_timeout(2500)
        zona = pg.query_selector("#sp-contare-zona")
        text = zona.inner_text() if zona else ""
        rez["%s_a_raspuns" % eticheta] = bool(text.strip())
        # STRUCTURA, nu text: cate randuri de divergenta, si cate celule are fiecare
        randuri = pg.query_selector_all("#sp-contare-zona table tbody tr")
        rez["%s_randuri_tabel" % eticheta] = len(randuri)
        cap = [th.inner_text().strip() for th in pg.query_selector_all("#sp-contare-zona table thead th")]
        rez["%s_capete" % eticheta] = cap
        div_tabel = pg.query_selector(".caseta-atentie table")
        if div_tabel:
            celule = [td.inner_text().strip()
                      for td in div_tabel.query_selector_all("tbody tr:first-child td")]
            rez["%s_divergenta_celule" % eticheta] = celule
            rez["%s_are_ambele_cifre" % eticheta] = len(celule) >= 5 and bool(celule[2]) and bool(celule[3])
        else:
            rez["%s_divergente" % eticheta] = 0
        btn = pg.query_selector("#sp-contare-scrie")
        rez["%s_buton_scrie_exista" % eticheta] = bool(btn)
        rez["%s_buton_scrie_activ" % eticheta] = (btn.is_enabled() if btn else None)
        pg.screenshot(path=os.path.join(AICI, "r33_%s_2_propunere.png" % eticheta), full_page=True)
        ctx.close()
    b.close()

print(json.dumps(rez, ensure_ascii=False, indent=1))
