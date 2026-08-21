# -*- coding: utf-8 -*-
"""Probe UI #11 (eroare nu rupe randul), #12 (latime em-adresa), #13 (cant/pret goale + antet)."""
import os, json, urllib.request
from playwright.sync_api import sync_playwright
BAZA = "http://127.0.0.1:8010"
CFG = {}
for ln in open(os.path.expanduser("~/.iconta/fe_test.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); CFG[k] = v
_body = json.dumps({"email": CFG["FE_TEST_EMAIL"], "parola": CFG["FE_TEST_PAROLA"]}).encode()
_d = json.load(urllib.request.urlopen(urllib.request.Request(
    BAZA + "/auth/login", _body, {"Content-Type": "application/json"}), timeout=15))
INIT = ("sessionStorage.setItem('iconta_token'," + json.dumps(_d["token"]) + ");"
        "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(_d["user"])) + ");")
OUT = os.path.dirname(os.path.abspath(__file__))
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 1100, "height": 1500}); ctx.add_init_script(INIT)
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-card", timeout=15000); pg.wait_for_timeout(400)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000); pg.wait_for_timeout(500)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("button.firme-rand", timeout=10000); pg.wait_for_timeout(300)
    pg.get_by_text("ALFA MICRO", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#fa-facturi", timeout=10000)
    pg.click("#fa-facturi"); pg.wait_for_timeout(500)
    pg.wait_for_selector("#fac-emite", timeout=10000)
    pg.click("#fac-emite")
    # poate aparea poarta de configurare numerotare (firma neconfigurata) SAU direct formularul
    pg.wait_for_selector("#em-da, #em-add-linie", timeout=12000); pg.wait_for_timeout(300)
    if pg.query_selector("#em-da"):
        if pg.query_selector("#em-tva-nu"):
            pg.click("#em-tva-nu"); pg.wait_for_timeout(150)
        pg.click("#em-nu"); pg.wait_for_timeout(300)
        pg.wait_for_selector("#em-salveaza-config2", timeout=8000)
        pg.click("#em-salveaza-config2")
    pg.wait_for_selector("#em-add-linie", timeout=12000); pg.wait_for_timeout(500)

    # ---- #13: cant/pret goale + placeholder + antet ----
    cant = pg.eval_on_selector("#em-l0-cantitate", "e=>({val:e.value, ph:e.placeholder})")
    pret = pg.eval_on_selector("#em-l0-pret_unitar", "e=>({val:e.value, ph:e.placeholder})")
    antet = pg.query_selector(".em-linie-antet")
    antet_txt = antet.inner_text().replace("\n", " | ") if antet else None
    print("#13 cantitate:", cant, "| pret:", pret, "| antet:", antet_txt)

    # ---- #12: latime em-adresa ~ em-nume ----
    w_nume = pg.eval_on_selector("#em-nume", "e=>e.getBoundingClientRect().width")
    w_adr = pg.eval_on_selector("#em-adresa", "e=>e.getBoundingClientRect().width")
    w_cui = pg.eval_on_selector("#em-cui", "e=>e.getBoundingClientRect().width")
    print("#12 latimi -> em-nume=%.0f  em-adresa=%.0f  em-cui=%.0f" % (w_nume, w_adr, w_cui))

    # ---- #11: declanseaza eroare pe linie ----
    pg.fill("#em-nume", "BETA TEST SRL")
    pg.fill("#em-l0-descriere", "Consultanță")
    # cantitate/pret lasate goale -> backend valideaza linia
    pg.click("#em-emite"); pg.wait_for_timeout(1500)
    # asteapta orice .msg-eroare[data-camp] care incepe cu em-l0
    err = pg.query_selector('.em-linie .msg-eroare[data-camp]')
    real_line_err = bool(err)
    if not real_line_err:
        # daca backendul n-a intors eroare pe linie, injectam una identica structural (test CSS layout)
        pg.eval_on_selector("#em-linii",
            "root=>{const api=null; const inp=root.querySelector('#em-l0-cantitate');"
            "const sp=document.createElement('span'); sp.className='msg-eroare'; sp.setAttribute('data-camp','em-l0-cantitate');"
            "sp.textContent='Completează cantitatea.'; inp.insertAdjacentElement('afterend', sp);}")
        pg.wait_for_timeout(200)
        err = pg.query_selector('.em-linie .msg-eroare[data-camp]')
    # masuratori aliniere: butonul de sters NU sare pe rand nou
    m = pg.eval_on_selector(".em-linie",
        "row=>{const den=row.querySelector('.em-l-den'); const del=row.querySelector('.em-l-sterge');"
        "const er=row.querySelector('.msg-eroare');"
        "const rd=den.getBoundingClientRect(), rx=del.getBoundingClientRect();"
        "return {den_top:rd.top, del_top:rx.top, diff:Math.abs(rd.top-rx.top),"
        "err_present:!!er, err_gridcol: er?getComputedStyle(er).gridColumnStart+'/'+getComputedStyle(er).gridColumnEnd:null,"
        "err_w: er?er.getBoundingClientRect().width:0, row_w: row.getBoundingClientRect().width};}")
    print("#11 eroare_reala_backend:", real_line_err)
    print("#11 aliniere -> den_top=%.1f del_top=%.1f diff=%.1fpx (aliniat daca <8)" % (m["den_top"], m["del_top"], m["diff"]))
    print("#11 err_present=%s gridColumn=%s err_w=%.0f row_w=%.0f (span pe tot randul daca err_w~row_w)" %
          (m["err_present"], m["err_gridcol"], m["err_w"], m["row_w"]))
    pg.screenshot(path=os.path.join(OUT, "proba_ui_emitere.png"), full_page=True)
    print("screenshot:", os.path.join(OUT, "proba_ui_emitere.png"))
    ok13 = cant["val"] == "" and pret["val"] == "" and antet is not None
    ok12 = abs(w_nume - w_adr) < 8
    ok11 = m["diff"] < 8 and m["err_present"]
    print("REZULTAT #11:", "PASS" if ok11 else "FAIL", "| #12:", "PASS" if ok12 else "FAIL", "| #13:", "PASS" if ok13 else "FAIL")
    b.close()
