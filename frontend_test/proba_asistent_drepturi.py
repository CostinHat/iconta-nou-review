# -*- coding: utf-8 -*-
"""PROBA în browser — testarea ca asistent (comanda Costin 04.10.2026, punctele 1–7).

Rulează pe ORICE bază, fiindcă nu importă `w_auth` (care la import construiește sesiunea contului
`patron@prisma-cont.test`, inexistent în producție). Sesiunea vine pe aceeași cale ca la `w_auth`:
`auth_api.sesiune_pentru_user` — fără parolă, fără dicționar scris de mână.

NU SCRIE NIMIC în bază. Singurele cereri de scriere sunt cele pe care serverul le REFUZĂ (asta e chiar
ce se probează: refuzul se vede, acțiunea interzisă nu se afișează). Bun-venitul se deschide forțând
`bun_venit_vazut=false` în sesiunea din browser; închiderea lui ar scrie `bun_venit_vazut_la`, deci
proba NU apasă butonul de la capăt pe contul real — doar X / Esc, care pe codul vechi nu există.

Ieșire: JSON cu cifrele (argumentul --iesire) + capturi PNG lângă el.

    set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a
    PYTHONPATH=. ./venv/bin/python frontend_test/proba_asistent_drepturi.py \
        --baza http://127.0.0.1:8010 --asistent costin.hateganu+asistent@gmail.com \
        --admin contabil.b@sesiuneab.test --iesire /tmp/.../inainte.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import auth_api, db  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizual"))


def _axe(pg):
    # Import LENEȘ: `axe_scan` importă `w_auth`, care la încărcare construiește sesiunea lui `patron@prisma-cont.test`
    # — inexistent în producție. Importat sus, proba n-ar mai porni pe producție (faza „înainte”, contul Anei), adică
    # exact ce promite antetul. Faza care rulează axe merge pe baza de test, unde contul există.
    import axe_scan  # noqa: E402  (axe-core vandorizat; aceeași unealtă ca infrastructura vizuală)
    viol, _t = axe_scan.scaneaza(pg)
    return {"violari": len(viol), "reguli": sorted({v.get("id") for v in viol})}

CUI_PROBA = "55229657"          # CUI-ul tastat de Costin la testare; cifra de control verificată
EMAIL_ALT_ROL = "costin.hateganu@gmail.com"   # contul superadmin (punctul 3)


def _sesiune(email, **suprascrie):
    import psycopg2.extras as E
    try:
        db.init_pool()
    except Exception:  # noqa: BLE001
        pass
    with db.get_conn() as conn:
        with conn.cursor(cursor_factory=E.RealDictCursor) as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u["id"]) if u else None
        conn.rollback()
    if not s or not s.get("ok"):
        raise SystemExit("cont indisponibil pentru proba: %s (%s)" % (email, s))
    user = dict(s["user"], **suprascrie)
    return ("sessionStorage.setItem('iconta_token'," + json.dumps(s["token"]) + ");"
            "sessionStorage.setItem('iconta_user'," + json.dumps(json.dumps(user)) + ");")


def _pagina(pw, init, lat=1280, inalt=900):
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": lat, "height": inalt})
    ctx.add_init_script(init)
    pg = ctx.new_page()
    cereri = []
    pg.on("response", lambda r: cereri.append((r.request.method, r.url.split("//", 1)[-1].split("/", 1)[-1], r.status))
          if r.request.method != "GET" else None)
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    return b, pg, cereri, erori


def _vizibile(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def _deschide_firme_asistent(pg, baza):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(500)
    pg.click(".asi-nod[data-nod='firme']", timeout=8000)
    pg.wait_for_selector("#firme-lista .firme-rand, #firme-lista .firme-gol", timeout=15000)
    pg.wait_for_timeout(600)


def punct12(pw, baza, asistent, iesire):
    """1 + 2 + 3: lista de firme ca asistent; Adaugă firmă cu CUI valid și emailul superadmin."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_firme_asistent(pg, baza)
    r["lista_firme"] = pg.eval_on_selector_all("#firme-lista .firme-rand-nume", "els => els.map(e => e.textContent.trim())")
    r["vizibil_adauga"] = _vizibile(pg, "#firme-adauga")
    r["vizibil_import_masa"] = _vizibile(pg, "#firme-import-masa")
    r["vizibil_scoate"] = _vizibile(pg, ".firme-rand-scoate")
    r["vizibil_nota_scoate"] = pg.evaluate("() => document.body.innerText.includes('Butonul Scoate')")
    pg.screenshot(path=iesire + "_1_lista_firme.png", full_page=True)
    if r["vizibil_adauga"]:
        pg.click("#firme-adauga")
        pg.wait_for_selector("#fn-cui", timeout=8000)
        pg.fill("#fn-cui", CUI_PROBA)
        pg.wait_for_function("() => !document.querySelector('#fn-salveaza').disabled", timeout=20000)
        pg.fill("#fn-email", EMAIL_ALT_ROL)
        r["info_inainte_de_clic"] = pg.inner_text("#fn-cui-info")
        pg.click("#fn-salveaza")
        pg.wait_for_timeout(1800)
        r["cereri_dupa_clic"] = [c for c in cereri if "tenants" in c[1]]
        # Unde a ajuns mesajul de refuz: textul, clasa, distanța față de buton, stilul de eroare
        r["refuz"] = pg.evaluate("""() => {
          const btn = document.querySelector('#fn-salveaza');
          const bb = btn.getBoundingClientRect();
          const cand = [...document.querySelectorAll('.fereastra-corp *')].filter(e =>
              e.children.length === 0 && /rol|administrator|drept/i.test(e.textContent) && e.offsetParent !== null);
          return {
            info_text: (document.querySelector('#fn-cui-info') || {}).textContent || null,
            info_clasa: (document.querySelector('#fn-cui-info') || {}).className || null,
            elemente_cu_refuz: cand.map(e => ({tag: e.tagName, clasa: e.className, text: e.textContent.trim().slice(0, 160),
                 culoare: getComputedStyle(e).color, distanta_px_fata_de_buton: Math.round(bb.top - e.getBoundingClientRect().bottom),
                 stil_eroare: !!e.closest('.msg-eroare, .msg-avert, [role=alert]')})),
            banner_global: !!document.getElementById('refuz-nevazut'),
            camp_email_marcat: (document.querySelector('#fn-email') || {}).getAttribute ? document.querySelector('#fn-email').getAttribute('aria-invalid') : null,
          };
        }""")
        pg.screenshot(path=iesire + "_2_dupa_adauga.png", full_page=True)
    r["erori_consola"] = erori
    b.close()
    return r


def punct45(pw, baza, asistent, iesire):
    """4 + 5 + 7: bun-venitul ca asistent (forțat în sesiunea din browser)."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent, bun_venit_vazut=False))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".bun-venit-overlay .ans-continut", timeout=20000)
    pg.wait_for_timeout(800)
    r["butoane_in_antet"] = pg.eval_on_selector_all(".bun-venit-antet button", "els => els.map(e => e.getAttribute('aria-label') || e.textContent)")
    r["pasi_fir"] = pg.eval_on_selector_all(".bun-venit-overlay .ans-pas-titlu", "els => els.map(e => e.textContent.trim())")
    txt = pg.inner_text(".bun-venit-overlay")
    r["contine_48_ore"] = "48 de ore" in txt
    r["contine_nu_ai_firme"] = "nu ai firme" in txt.lower()
    r["text_inceput"] = txt[:400]
    pg.screenshot(path=iesire + "_3_bun_venit.png")
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(500)
    r["deschis_dupa_esc"] = pg.query_selector(".bun-venit-overlay") is not None
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def punct6(pw, baza, admin, iesire):
    """6: contorul din ecranul Asistenți, ca administrator."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(admin))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=20000)
    pg.wait_for_timeout(500)
    pg.click("button.cab-card:has([data-cheie='asistenti'])", timeout=8000)
    pg.wait_for_selector(".asi-sumar", timeout=15000)
    pg.wait_for_timeout(600)
    r["sumar"] = pg.inner_text(".asi-sumar")
    r["actori"] = pg.eval_on_selector_all("#asi-lista .asi-nume", "els => els.map(e => e.textContent.trim())")
    r["roluri"] = pg.eval_on_selector_all("#asi-lista .asi-rol", "els => els.map(e => e.textContent.trim())")
    pg.screenshot(path=iesire + "_4_asistenti.png", full_page=True)
    r["erori_consola"] = erori
    b.close()
    return r


# ── FAZA „DUPĂ” (codul nou): aceleași puncte, plus nivelurile în fereastra firmei ──────────────────────────
def _vizibil(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def dupa_asistent(pw, baza, asistent, iesire, eticheta="pregatire"):
    """Asistent DOAR cu «Poate pregăti» (ca Ana): ce vede în listă, ce primește la POST /tenants, ce vede în firmă."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_firme_asistent(pg, baza)
    r["lista_firme"] = pg.eval_on_selector_all("#firme-lista .firme-rand-nume", "els => els.map(e => e.textContent.trim())")
    r["vizibil_adauga"] = _vizibil(pg, "#firme-adauga")
    r["vizibil_import_masa"] = _vizibil(pg, "#firme-import-masa")
    r["vizibil_scoate"] = _vizibil(pg, ".firme-rand-scoate")
    r["in_dom_scoate"] = pg.eval_on_selector_all(".firme-rand-scoate", "els => els.length")
    r["vizibil_firme_scoase"] = _vizibil(pg, "#firme-vezi-scoase")   # istoricul scoaterilor = al cabinetului întreg
    r["vizibil_nota_scoate"] = pg.evaluate("() => document.body.innerText.includes('Butonul Scoate')")
    pg.screenshot(path=iesire + "_1_lista_firme_%s.png" % eticheta, full_page=True)
    r["axe_lista_firme"] = _axe(pg)
    # refuzul serverului, citit din pagină (butonul nu mai există, deci se cere direct, cum ar face un clic vechi)
    r["post_tenants"] = pg.evaluate("""async () => {
      const t = sessionStorage.getItem('iconta_token');
      const x = await fetch('/tenants', {method:'POST', headers:{'Content-Type':'application/json', Authorization:'Bearer '+t},
                                         body: JSON.stringify({nume:'ZT proba', cui:'55229657'})});
      return {status: x.status, detail: (await x.json()).detail};
    }""")
    # fereastra primei firme: Registru jurnal, Date firmă, Import date
    pg.click("#firme-lista button.firme-rand")
    pg.wait_for_selector("#fa-jurnal", timeout=15000)
    pg.wait_for_timeout(500)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-prev", timeout=15000)   # „+ Notă nouă” poate fi ascuns (asistent fără drepturi)
    pg.wait_for_timeout(1200)
    r["jurnal"] = {"nota_noua_vizibil": _vizibil(pg, "#j-nota-noua"),
                   "valideaza_vizibile": _vizibil(pg, "[data-val]"), "valideaza_in_dom": pg.eval_on_selector_all("[data-val]", "e => e.length"),
                   "bloc_luna_in_dom": pg.eval_on_selector_all("#j-lock", "e => e.length"),
                   "amortizare_vizibil": _vizibil(pg, "#j-amort"),
                   "sterge_vizibile": _vizibil(pg, "[data-del]")}
    pg.screenshot(path=iesire + "_5_jurnal_%s.png" % eticheta, full_page=True)
    pg.click(".nav-sageata.nav-inapoi")
    pg.wait_for_selector("#fa-datefirma", timeout=15000)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-nume-portofoliu", timeout=15000)
    pg.wait_for_timeout(600)
    r["date_firma"] = {"salveaza_vizibil": _vizibil(pg, "#df-salveaza"),
                       "nume_portofoliu_dezactivat": pg.eval_on_selector("#df-nume-portofoliu", "e => e.disabled")}
    pg.click(".nav-sageata.nav-inapoi")
    pg.wait_for_selector("#fa-import", timeout=15000)
    pg.click("#fa-import")
    pg.wait_for_selector("#mig-pasi, .stare-goala", timeout=15000)
    pg.wait_for_timeout(600)
    r["import_mesaj_fara_drept"] = pg.eval_on_selector_all("#mig-fara-drept", "e => e.map(x => x.textContent.trim())")
    r["import_pasi_vizibili"] = pg.eval_on_selector_all(".mig-frand", "els => els.filter(e => e.offsetParent !== null).map(e => e.querySelector('.mig-frand-nume').textContent)")
    pg.click(".nav-sageata.nav-inapoi")
    pg.wait_for_selector("#fa-operatiuni", timeout=15000)
    pg.click("#fa-operatiuni")
    pg.wait_for_selector(".fereastra-corp h2", timeout=15000)
    pg.wait_for_timeout(600)
    r["operatiuni_vizibile"] = pg.eval_on_selector_all("[data-op]", "e => e.filter(x => x.offsetParent !== null).length")
    r["operatiuni_mesaj"] = pg.eval_on_selector_all(".fereastra-corp .ecran-nota", "e => e.map(x => x.textContent.trim()).filter(t => t.includes('Poate pregăti'))")
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def dupa_bun_venit(pw, baza, cont, iesire, eticheta):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(cont, bun_venit_vazut=False))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".bun-venit-overlay .ans-continut", timeout=20000)
    pg.wait_for_timeout(800)
    r["butoane_in_antet"] = pg.eval_on_selector_all(".bun-venit-antet button", "els => els.map(e => e.getAttribute('aria-label') || e.textContent)")
    r["pasi_fir"] = pg.eval_on_selector_all(".bun-venit-overlay .ans-pas-titlu", "els => els.map(e => e.textContent.trim())")
    txt = pg.inner_text(".bun-venit-overlay")
    r["contine_48_ore"] = "48 de ore" in txt
    r["mesaj_fara_firme"] = pg.eval_on_selector_all(".ans-fara-firme", "els => els.map(e => e.textContent.trim())")
    r["text_inceput"] = txt[:420]
    pg.screenshot(path=iesire + "_3_bun_venit_%s.png" % eticheta)
    r["axe"] = _axe(pg)
    pg.keyboard.press("Escape")
    pg.wait_for_timeout(700)
    r["deschis_dupa_esc"] = pg.query_selector(".bun-venit-overlay") is not None
    r["marcat_vazut_la_esc"] = [c for c in cereri if "bun-venit-vazut" in c[1]]
    r["erori_consola"] = erori
    b.close()
    # X-ul, separat (o pagină nouă)
    b, pg, cereri, erori = _pagina(pw, _sesiune(cont, bun_venit_vazut=False))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".bun-venit-antet .nav-x", timeout=20000)
    pg.click(".bun-venit-antet .nav-x")
    pg.wait_for_timeout(700)
    r["deschis_dupa_x"] = pg.query_selector(".bun-venit-overlay") is not None
    b.close()
    # telefon (Pixel 5): X-ul se vede și se poate apăsa, nimic nu se revarsă orizontal
    b = pw.chromium.launch(headless=True)
    ctx = b.new_context(**pw.devices["Pixel 5"])
    ctx.add_init_script(_sesiune(cont, bun_venit_vazut=False))
    m = ctx.new_page()
    m.goto(baza + "/", wait_until="domcontentloaded")
    m.wait_for_selector(".bun-venit-antet .nav-x", timeout=20000)
    m.wait_for_timeout(600)
    r["mobil"] = {"x_vizibil": m.is_visible(".bun-venit-antet .nav-x"),
                  "x_dimensiune": m.eval_on_selector(".bun-venit-antet .nav-x", "e => { const b = e.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; }"),
                  "revarsare_x": m.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"),
                  "axe": _axe(m)}
    m.screenshot(path=iesire + "_6_bun_venit_mobil_%s.png" % eticheta)
    b.close()
    return r


def dupa_admin(pw, baza, admin, email_alt_rol, iesire):
    """Administratorul: contorul Asistenți; Adaugă firmă cu emailul unui cont cu alt rol -> refuz lângă buton,
    câmpul marcat, nicio firmă creată."""
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(admin))
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=20000)
    pg.wait_for_timeout(500)
    pg.click("button.cab-card:has([data-cheie='asistenti'])", timeout=8000)
    pg.wait_for_selector(".asi-sumar", timeout=15000)
    pg.wait_for_timeout(600)
    r["sumar"] = pg.inner_text(".asi-sumar")
    r["roluri"] = pg.eval_on_selector_all("#asi-lista .asi-rol", "els => els.map(e => e.textContent.trim())")
    pg.screenshot(path=iesire + "_4_asistenti.png", full_page=True)
    numar = """async () => { const t = sessionStorage.getItem('iconta_token');
      const x = await fetch('/tenants?inactive=true', {headers:{Authorization:'Bearer '+t}}); return ((await x.json()).tenants || []).length; }"""
    r["firme_inainte"] = pg.evaluate(numar)
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=20000)
    pg.get_by_text("Firme", exact=True).first.click(timeout=8000)
    pg.wait_for_timeout(400)
    pg.get_by_text("Firme existente", exact=False).first.click(timeout=8000)
    pg.wait_for_selector("#firme-adauga", timeout=15000)
    pg.click("#firme-adauga")
    pg.wait_for_selector("#fn-cui", timeout=8000)
    pg.fill("#fn-cui", CUI_PROBA)
    pg.wait_for_function("() => !document.querySelector('#fn-salveaza').disabled", timeout=25000)
    pg.fill("#fn-email", email_alt_rol)
    pg.click("#fn-salveaza")
    pg.wait_for_timeout(2000)
    r["refuz"] = pg.evaluate("""() => {
      const btn = document.querySelector('#fn-salveaza'), m = document.querySelector('#fn-msg');
      const em = document.querySelector('#fn-email');
      const sub = em && em.parentElement.querySelector('.msg-eroare[data-camp="fn-email"]');
      return {mesaj: m && m.textContent, clasa: m && m.className, rol: m && m.getAttribute('role'),
              distanta_px_sub_buton: m ? Math.round(m.getBoundingClientRect().top - btn.getBoundingClientRect().bottom) : null,
              camp_email_invalid: em && em.getAttribute('aria-invalid'), mesaj_pe_camp: sub && sub.textContent,
              info_cui: (document.querySelector('#fn-cui-info') || {}).textContent};
    }""")
    pg.screenshot(path=iesire + "_2_adauga_admin_email_alt_rol.png", full_page=True)
    r["axe_formular_cu_refuz"] = _axe(pg)
    r["firme_dupa"] = pg.evaluate(numar)
    r["cereri"] = [c for c in cereri if "tenants" in c[1]]
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--admin", required=True)
    ap.add_argument("--iesire", required=True)
    ap.add_argument("--faza", choices=("inainte", "dupa", "fara-drepturi"), default="inainte")
    ap.add_argument("--asistent-fara-firme", default=None)
    ap.add_argument("--email-alt-rol", default=None)
    a = ap.parse_args()
    baza_iesire = os.path.splitext(a.iesire)[0]
    if a.faza == "fara-drepturi":
        # asistent CU firme alocate, FĂRĂ nicio bifă (cazul Anei din producție): vede firmele, nu vede nicio acțiune
        with sync_playwright() as pw:
            rez = {"baza": a.baza, "faza": "fara-drepturi",
                   "asistent_fara_drepturi": dupa_asistent(pw, a.baza, a.asistent, baza_iesire, "fara_drepturi")}
        with open(a.iesire, "w", encoding="utf-8") as f:
            json.dump(rez, f, ensure_ascii=False, indent=1)
        print(json.dumps(rez, ensure_ascii=False, indent=1))
        return
    if a.faza == "dupa":
        with sync_playwright() as pw:
            rez = {"baza": a.baza, "faza": "dupa",
                   "asistent_doar_pregatire": dupa_asistent(pw, a.baza, a.asistent, baza_iesire),
                   "bun_venit_asistent": dupa_bun_venit(pw, a.baza, a.asistent, baza_iesire, "asistent"),
                   "bun_venit_admin": dupa_bun_venit(pw, a.baza, a.admin, baza_iesire, "admin"),
                   "admin": dupa_admin(pw, a.baza, a.admin, a.email_alt_rol, baza_iesire)}
            if a.asistent_fara_firme:
                rez["bun_venit_fara_firme"] = dupa_bun_venit(pw, a.baza, a.asistent_fara_firme, baza_iesire, "fara_firme")
        with open(a.iesire, "w", encoding="utf-8") as f:
            json.dump(rez, f, ensure_ascii=False, indent=1)
        print(json.dumps(rez, ensure_ascii=False, indent=1))
        return
    with sync_playwright() as pw:
        rez = {"baza": a.baza, "asistent": a.asistent, "admin": a.admin,
               "p1_2_3": punct12(pw, a.baza, a.asistent, baza_iesire),
               "p4_5_7": punct45(pw, a.baza, a.asistent, baza_iesire),
               "p6": punct6(pw, a.baza, a.admin, baza_iesire)}
    with open(a.iesire, "w", encoding="utf-8") as f:
        json.dump(rez, f, ensure_ascii=False, indent=1)
    print(json.dumps(rez, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
