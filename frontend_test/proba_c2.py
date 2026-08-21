# -*- coding: utf-8 -*-
"""Proba C2 (tenant_003, cale per-firma): import salariati -> SALVARE -> revenire la MENIUL FIRMEI
(nu wizardul de cabinet) + mesaj de succes verde. Randare before/after."""
import os, sys, json
from playwright.sync_api import sync_playwright
from w_auth import new_page, deschide_firma, OUT, BAZA

VALID = os.path.join(OUT, "valid_salariati_c2.csv")
open(VALID, "w", encoding="utf-8").write(
    "nume,prenume,cnp,data angajare,norma,brut,judet\n"
    "Popescu,Ana,2900215410011,2020-01-15,intreaga,5000,B\n"
    "Ionescu,Radu,1850715410012,2021-03-01,intreaga,6000,CJ\n")

TAG = sys.argv[1] if len(sys.argv) > 1 else "after"
with sync_playwright() as pw:
    b, pg = new_page(pw); rez = {"tag": TAG}
    errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    try:
        deschide_firma(pg)
        pg.click("#fa-import"); pg.wait_for_timeout(600)
        pg.get_by_text("Salariați", exact=False).first.click(timeout=8000); pg.wait_for_timeout(700)
        pg.set_input_files("#mig-file", VALID); pg.wait_for_timeout(1500)
        pg.screenshot(path=os.path.join(OUT, "proba_c2_%s_1preview.png" % TAG), full_page=True)
        btn = pg.query_selector("#mig-salveaza-sal")
        rez["buton_salvare_prezent"] = bool(btn)
        rez["buton_disabled"] = btn.is_disabled() if btn else None
        if btn and not btn.is_disabled():
            btn.click(); pg.wait_for_timeout(2500)
        pg.screenshot(path=os.path.join(OUT, "proba_c2_%s_2dupa.png" % TAG), full_page=True)
        body = pg.inner_text("body")
        msg_ok = pg.query_selector(".msg-ok")
        rez["mesaj_ok_text"] = msg_ok.inner_text().strip() if msg_ok else "(niciun .msg-ok)"
        # meniul per-firma are intro "Alege ce vrei sa aduci pentru aceasta firma"
        rez["revenit_la_meniul_firmei"] = "Alege ce vrei s" in body
        # wizardul de cabinet ar avea "din vechea aplicație" / "din X firme"
        rez["e_wizard_cabinet"] = ("din vechea aplica" in body) or ("firme au salaria" in body)
        rez["console_errors"] = errs[:3]
    except Exception as e:
        rez["error"] = str(e)
        import traceback; traceback.print_exc()
        pg.screenshot(path=os.path.join(OUT, "proba_c2_%s_ERR.png" % TAG), full_page=True)
    print(json.dumps(rez, ensure_ascii=False, indent=2))
    b.close()
