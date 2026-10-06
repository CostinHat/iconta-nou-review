# -*- coding: utf-8 -*-
"""PROBA în browser — ciorna facturii (comanda Costin 06.10.2026, pct.1: „factura începută se pierde a PATRA oară”), pe baza
de TEST (8011).

Reface drumul EXACT din retest (F1 ca Ana): Facturi → completat (Dante 14399840; Marfa A 3×120 21%; „Carte – Ghid contabil
2026” 2×45 11%; scadența 05.11.2026) → ← → ← (fereastra firmei) → Date firmă → ← → Facturi → Emite. Apoi fiecare altă ieșire
din formular (X, reîncărcarea paginii, firul de sus, un tab nou, „Schimbă seria”, altă firmă, alt utilizator, „Renunță”,
emiterea refuzată). Plus pct.1b (prețul pe rândul nou), 1c (articolul de stoc al rândului scris de mână, din cererea de
emitere interceptată — nu pleacă la server) și 1d (scadența la deschiderea formularului).

Aceeași probă rulează pe codul VECHI (înainte) și pe cel NOU (după); ce lipsește în forma veche iese `None` / `False`.
SCRIE în baza de test un articol de stoc și un produs „Marfa A” (preț 100, 21%, ca F1 pe producție) pe firma Panificatie;
`curata()` le șterge.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_ciorna_factura.py --iesire /tmp/.../ciorna_dupa.json
"""
import argparse
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import db  # noqa: E402
from proba_asistent_drepturi import _axe, _sesiune  # noqa: E402

ASISTENT = "asistent@prisma-cont.test"
ALT_USER = "patron@prisma-cont.test"
FIRMA, ALTA_FIRMA = "Panificatie", "Coafor"
CUI_DANTE = "14399840"              # DANTE INTERNATIONAL SA; cifra de control verificată în `cui_valid` (repere)
SCADENTA = "2026-11-05"
L2 = "Carte – Ghid contabil 2026"
CAMPURI = ["#em-cui", "#em-nume", "#em-scadenta", "#em-l0-descriere", "#em-l0-cantitate", "#em-l0-pret_unitar", "#em-l0-cota",
           "#em-l0-articol", "#em-l1-descriere", "#em-l1-cantitate", "#em-l1-pret_unitar", "#em-l1-cota", "#em-l1-articol"]


def cui_valid(cui):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    c = str(cui).strip()
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = (sum(int(corp[i]) * ch[i] for i in range(9)) * 10) % 11
    return (0 if r == 10 else r) == ctrl


def _context(b, lat=1280, inalt=900):
    ctx = b.new_context(viewport={"width": lat, "height": inalt})
    pg = ctx.new_page()
    erori = []
    pg.on("pageerror", lambda e: erori.append(str(e)))
    return ctx, pg, erori


def _intra(pg, baza, email):
    """Sesiunea utilizatorului în tabul ăsta (sessionStorage), FĂRĂ să atingă localStorage — acolo stă ciorna."""
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.evaluate("() => sessionStorage.clear()")
    pg.evaluate(_sesiune(email).replace("sessionStorage", "window.sessionStorage"))
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
    pg.wait_for_timeout(600)


def _acasa(pg, baza):
    if not pg.query_selector(".asi-arbore, .cab-grila"):
        pg.goto(baza + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
        pg.wait_for_timeout(500)


def _firma(pg, baza, firma):
    _acasa(pg, baza)
    if pg.query_selector(".asi-nod[data-nod='firme']"):
        pg.click(".asi-nod[data-nod='firme']")
        pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
        pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    else:                                    # cabinetul: lista firmelor din grilă
        pg.click("button.cab-card:has([data-cheie='firme'])")     # Firme → „Firme existente” → lista
        pg.wait_for_selector("#opt-existente", timeout=10000)
        pg.click("#opt-existente")
        pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
        pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=15000)
    pg.wait_for_timeout(400)


def _deschide_emitere(pg):
    """Din fereastra firmei: Facturi → Emite factură (cardul, apoi butonul), ca omul."""
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-emite", timeout=15000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui, #em-nu", timeout=20000)
    if pg.query_selector("#em-nu"):          # numerotare neconfigurată pe firma de test: „încep acum”, seria ZT
        if pg.query_selector("#em-tva-da"):
            pg.click("#em-tva-da")
        pg.click("#em-nu")
        pg.wait_for_selector("#em-salveaza-config2", timeout=10000)
        pg.fill("#em-serie2", "ZT")
        pg.click("#em-salveaza-config2")
        pg.wait_for_selector("#em-cui", timeout=20000)
    pg.wait_for_timeout(1200)


def _stare(pg):
    out = {}
    for s in CAMPURI:
        out[s] = pg.eval_on_selector(s, "e => e.value") if pg.query_selector(s) else None
    out["anunt"] = (pg.eval_on_selector("#em-ciorna", "e => e.innerText.trim()") if pg.query_selector("#em-ciorna") else None) or ""
    out["linii"] = pg.eval_on_selector_all(".em-l-den", "els => els.length")
    return out


def _ciorne(pg):
    return pg.evaluate("""() => Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura'))
                                 .map(k => [k, (JSON.parse(localStorage.getItem(k)).linii || []).map(l => l.descriere)])""")


def _asteapta_cota(pg, i):
    try:
        pg.wait_for_function("(i) => { const c = document.querySelector('#em-l' + i + '-cota'); return c && c.value; }", arg=i, timeout=15000)
    except Exception:  # noqa: BLE001
        pass
    pg.wait_for_timeout(300)


def _completeaza(pg, r, cheie=None):
    """Drumul lui Costin: client, rândul 1 din stoc (Marfa A 3×120, 21%), rândul 2 scris de mână (Carte 2×45, 11%), scadența."""
    pg.fill("#em-cui", CUI_DANTE)
    pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
    art = pg.eval_on_selector_all("#em-l0-articol option", "os => os.filter(o => /Marfa A/.test(o.textContent)).map(o => o.value)")
    if art:
        pg.select_option("#em-l0-articol", art[0])
    _asteapta_cota(pg, 0)
    if cheie:
        r[cheie + "_l0_pret_propus"] = pg.eval_on_selector("#em-l0-pret_unitar", "e => e.value")
    pg.fill("#em-l0-cantitate", "3")
    pg.fill("#em-l0-pret_unitar", "120")
    pg.select_option("#em-l0-cota", "21")
    pg.click("#em-add-linie")
    pg.wait_for_selector("#em-l1-descriere", timeout=5000)
    pg.wait_for_timeout(300)
    if cheie:   # pct.1b: rândul NOU, înainte de orice tastă
        r[cheie + "_l1_pret_la_rand_nou"] = pg.eval_on_selector("#em-l1-pret_unitar", "e => e.value")
        r[cheie + "_l1_articol_la_rand_nou"] = pg.eval_on_selector("#em-l1-articol", "e => e.selectedOptions[0] && e.selectedOptions[0].textContent.trim()") if pg.query_selector("#em-l1-articol") else None
    pg.fill("#em-l1-descriere", L2)
    _asteapta_cota(pg, 1)
    pg.wait_for_timeout(900)          # potrivirea din nomenclator (550 ms) a avut timp să scrie
    if cheie:   # pct.1b/1c: după denumirea scrisă de mână
        r[cheie + "_l1_pret_dupa_denumire"] = pg.eval_on_selector("#em-l1-pret_unitar", "e => e.value")
        r[cheie + "_l1_articol_dupa_denumire"] = pg.eval_on_selector("#em-l1-articol", "e => e.selectedOptions[0] && e.selectedOptions[0].textContent.trim()") if pg.query_selector("#em-l1-articol") else None
    pg.fill("#em-l1-cantitate", "2")
    pg.fill("#em-l1-pret_unitar", "45")
    if pg.query_selector("select#em-l1-cota"):
        pg.select_option("#em-l1-cota", "11")
    pg.fill("#em-scadenta", SCADENTA)
    pg.wait_for_timeout(500)


def _complet(st):
    """Formularul are ce a scris omul (drumul lui Costin)?"""
    return (st.get("#em-cui") == CUI_DANTE and st.get("#em-l0-cantitate") == "3" and st.get("#em-l0-pret_unitar") == "120"
            and st.get("#em-l1-descriere") == L2 and st.get("#em-l1-pret_unitar") == "45" and st.get("#em-scadenta") == SCADENTA)


def _gol(st):
    return not (st.get("#em-cui") or st.get("#em-l0-descriere") or st.get("#em-l0-cantitate"))


def _cerere_emitere(pg):
    """Apasă „Emite” cu cererea INTERCEPTATĂ (nu pleacă la server; răspuns 400 fabricat): ce linii, ce articol de stoc."""
    prinse = []

    def _h(route):
        try:
            prinse.append(json.loads(route.request.post_data or "{}"))
        except Exception:  # noqa: BLE001
            prinse.append({"brut": route.request.post_data})
        route.fulfill(status=400, content_type="application/json", body=json.dumps({"detail": "proba: emiterea interceptată"}))
    if pg.eval_on_selector("#em-emite", "e => e.disabled"):
        return {"cerere": None, "emite_dezactivat": pg.eval_on_selector("#em-emite", "e => e.title")}
    pg.route(re.compile(r".*/facturi/emite.*"), _h)
    pg.evaluate("() => document.querySelector('#em-emite').scrollIntoView({block: 'center'})")
    pg.click("#em-emite")
    pg.wait_for_timeout(1500)
    if pg.query_selector("#em-poarta-da") and not prinse:      # „Pleacă marfa acum?” — da, ca la o vânzare din stoc
        pg.click("#em-poarta-da")
        pg.wait_for_timeout(1500)
    pg.unroute(re.compile(r".*/facturi/emite.*"))
    if not prinse:
        return {"cerere": None, "rezultat": (pg.eval_on_selector("#em-rezultat", "e => e.innerText") or "")[:300]}
    c = prinse[-1]
    return {"linii": [{k: l.get(k) for k in ("descriere", "cantitate", "pret_unitar", "cota_tva", "articol_id")} for l in c.get("linii", [])],
            "pleaca_marfa": c.get("pleaca_marfa", c.get("descarca_stoc"))}


_DIR_CAPTURI = ["."]


def _rand_ales_apoi_scris(pg):
    """Rând nou: articolul „Marfa A” ales din listă (denumirea și prețul de vânzare vin din nomenclator), apoi denumirea
    rescrisă de mână „Carte – Ghid contabil 2026”, prețul NEatins. Ce rămâne pe rând și ce ar pleca la emitere."""
    out = {}
    pg.click("#em-add-linie")
    pg.wait_for_selector("#em-l2-descriere", timeout=5000)
    art = pg.eval_on_selector_all("#em-l2-articol option", "os => os.filter(o => /Marfa A/.test(o.textContent)).map(o => o.value)")
    if not art:
        return {"fara_lista_de_articole": True}
    pg.select_option("#em-l2-articol", art[0])
    _asteapta_cota(pg, 2)
    pg.wait_for_timeout(900)
    out["dupa_alegere"] = {"denumire": pg.eval_on_selector("#em-l2-descriere", "e => e.value"),
                           "pret": pg.eval_on_selector("#em-l2-pret_unitar", "e => e.value")}
    pg.fill("#em-l2-descriere", L2)
    _asteapta_cota(pg, 2)
    pg.wait_for_timeout(900)
    pg.fill("#em-l2-cantitate", "2")
    out["dupa_rescriere"] = {"denumire": pg.eval_on_selector("#em-l2-descriere", "e => e.value"),
                             "pret": pg.eval_on_selector("#em-l2-pret_unitar", "e => e.value"),
                             "articol": pg.eval_on_selector("#em-l2-articol", "e => e.selectedOptions[0] && e.selectedOptions[0].textContent.trim()")}
    out["cerere_emitere"] = _cerere_emitere(pg)
    # emiterea REALĂ (neinterceptată) cu rândul fără preț: refuzul serverului, lângă câmpul prețului (nicio scriere: validarea
    # liniilor vine înaintea oricărei scrieri, `facturi_api.emite_factura`)
    if not pg.eval_on_selector("#em-l2-pret_unitar", "e => e.value"):
        pg.evaluate("() => document.querySelector('#em-emite').scrollIntoView({block: 'center'})")
        pg.click("#em-emite")
        pg.wait_for_timeout(2500)
        if pg.query_selector("#em-poarta-nu"):
            pg.click("#em-poarta-nu"); pg.wait_for_timeout(2500)
        out["refuz_server_pret"] = {
            "langa_camp": pg.eval_on_selector_all('.msg-eroare[data-camp="em-l2-pret_unitar"]', "els => els.map(e => e.innerText.trim())"),
            "camp_invalid": pg.eval_on_selector("#em-l2-pret_unitar", "e => e.getAttribute('aria-invalid')"),
            "rezultat": (pg.eval_on_selector("#em-rezultat", "e => e.innerText") or "")[:200]}
        pg.screenshot(path=os.path.join(_DIR_CAPTURI[0], "bc2_refuz_pret.png"), full_page=True)
    pg.click("#em-l2-descriere")
    sterge = pg.query_selector('.em-l-sterge[data-idx="2"]')
    if sterge:
        sterge.click()
        pg.wait_for_timeout(400)
    return out


def _iesire(pg, baza, nume, iesi, r, dir_capturi, reintra=None):
    """Formularul completat → ieșirea dată → redeschiderea formularului pe aceeași firmă → ce a rămas. O ieșire care nu se
    poate face (element absent) se consemnează cu eroarea și captura, iar proba trece la următoarea de pe acasă."""
    try:
        iesi()
        (reintra or (lambda: (_firma(pg, baza, FIRMA), _deschide_emitere(pg))))()
    except Exception as e:  # noqa: BLE001
        r[nume] = {"eroare": str(e).splitlines()[0][:200], "titlu": _titlu(pg)}
        pg.screenshot(path=os.path.join(dir_capturi, nume + "_eroare.png"), full_page=True)
        pg.goto(baza + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)
        _firma(pg, baza, FIRMA)
        _deschide_emitere(pg)
        return _stare(pg)
    st = _stare(pg)
    r[nume] = {"pastrat": _complet(st), "anunt": bool(st["anunt"]), "stare": st}
    pg.screenshot(path=os.path.join(dir_capturi, nume + ".png"), full_page=True)
    return st


def proba(pw, baza, dir_capturi, rp, r):
    _DIR_CAPTURI[0] = dir_capturi
    r["azi"] = datetime.date.today().isoformat()
    b = pw.chromium.launch(headless=True)
    ctx, pg, erori = _context(b)
    _intra(pg, baza, ASISTENT)
    pg.evaluate("() => Object.keys(localStorage).filter(k => k.startsWith('iconta_ciorna_factura')).forEach(k => localStorage.removeItem(k))")

    # ── 1d: scadența la deschiderea unui formular NOU (gol), înainte de client ───────────────────────────────────────────
    _firma(pg, baza, FIRMA)
    _deschide_emitere(pg)
    r["d_scadenta_la_deschidere"] = pg.eval_on_selector("#em-scadenta", "e => e.value")
    r["d_data_emiterii"] = pg.eval_on_selector("#em-data", "e => e.value")
    r["d_ajutor_scadenta"] = pg.eval_on_selector("#em-scadenta-ajutor", "e => e.innerText") if pg.query_selector("#em-scadenta-ajutor") else None
    r["d_pret_rand_nou_gol"] = pg.eval_on_selector("#em-l0-pret_unitar", "e => e.value")
    pg.screenshot(path=os.path.join(dir_capturi, "d_formular_nou.png"), full_page=True)

    # ── 1a: DRUMUL EXACT ──────────────────────────────────────────────────────────────────────────────────────────────
    _completeaza(pg, r, "bc")
    r["a_inainte_de_iesire"] = _stare(pg)
    r["a_ciorne_inainte"] = _ciorne(pg)
    pg.screenshot(path=os.path.join(dir_capturi, "a0_completat.png"), full_page=True)
    pasi = []

    def drum():
        pg.click(".nav-inapoi"); pg.wait_for_timeout(700); pasi.append(("← 1", _titlu(pg), _ciorne(pg)))
        pg.click(".nav-inapoi"); pg.wait_for_timeout(700); pasi.append(("← 2", _titlu(pg), _ciorne(pg)))
        pg.click("#fa-datefirma"); pg.wait_for_timeout(1500); pasi.append(("Date firmă", _titlu(pg), _ciorne(pg)))
        pg.click(".nav-inapoi"); pg.wait_for_timeout(700); pasi.append(("← 3", _titlu(pg), _ciorne(pg)))

    def reintra_drum():
        _deschide_emitere(pg)
        pasi.append(("Facturi → Emite", _titlu(pg), _ciorne(pg)))
    _iesire(pg, baza, "a1_drumul_costin", drum, r, dir_capturi, reintra=reintra_drum)
    r["a1_pasi"] = pasi

    # 1c: ce ar pleca la emitere de pe formularul restaurat (cererea interceptată)
    r["c_cerere_emitere"] = _cerere_emitere(pg)
    r["c_dupa_emitere_refuzata"] = {"pastrat": _complet(_stare(pg)), "ciorne": _ciorne(pg)}

    # ── 1b/1c, varianta din retest: pe rândul 2 se alege ÎNTÂI „Marfa A” din listă, apoi se scrie peste denumire ───────
    r["bc2"] = _rand_ales_apoi_scris(pg)

    # ── celelalte ieșiri ─────────────────────────────────────────────────────────────────────────────────────────────
    def asigura_completat():
        if not _complet(_stare(pg)):
            for s in ("#em-renunta",):
                pass
            _completeaza(pg, {}, None)

    asigura_completat()
    _iesire(pg, baza, "a2_x_acasa", lambda: (pg.click(".nav-x"), pg.wait_for_timeout(700)), r, dir_capturi)
    asigura_completat()
    _iesire(pg, baza, "a3_reincarcare", lambda: (pg.reload(wait_until="domcontentloaded"), pg.wait_for_selector(".asi-arbore, .cab-grila", timeout=20000)), r, dir_capturi)
    asigura_completat()

    def fir():   # firul de sus: veriga „Facturi” (pasul de dinainte), apoi „Emite”
        r["a4_verigi"] = pg.eval_on_selector_all(".fir-veriga", "els => els.map(e => e.textContent.trim())")
        pg.locator(".fir-veriga").last.click(); pg.wait_for_timeout(800)

    def reintra_fir():
        pg.click("#fac-emite")
        pg.wait_for_selector("#em-cui", timeout=15000)
        pg.wait_for_timeout(1200)
    _iesire(pg, baza, "a4_fir_sus", fir, r, dir_capturi, reintra=reintra_fir)
    asigura_completat()

    # tab nou (tabul vechi închis): aceeași sesiune de browser, sesiunea refăcută în tab
    pg.close()
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: erori.append(str(e)))
    _intra(pg, baza, ASISTENT)
    _iesire(pg, baza, "a5_tab_nou", lambda: None, r, dir_capturi)
    asigura_completat()

    def serie():
        if pg.query_selector("#em-schimba-serie"):
            pg.click("#em-schimba-serie"); pg.wait_for_timeout(1200)
            pg.click(".nav-inapoi"); pg.wait_for_timeout(1000)
    _iesire(pg, baza, "a6_schimba_seria", serie, r, dir_capturi, reintra=lambda: pg.wait_for_timeout(300))
    asigura_completat()

    # altă firmă: ciorna Panificatie NU apare la Coafor; înapoi la Panificatie, e acolo
    pg.click(".nav-x"); pg.wait_for_timeout(600)
    _firma(pg, baza, ALTA_FIRMA)
    _deschide_emitere(pg)
    st = _stare(pg)
    r["a7_alta_firma"] = {"gol": _gol(st), "anunt": bool(st["anunt"]), "stare": st}
    pg.screenshot(path=os.path.join(dir_capturi, "a7_alta_firma.png"), full_page=True)
    pg.click(".nav-x"); pg.wait_for_timeout(600)
    _firma(pg, baza, FIRMA)
    _deschide_emitere(pg)
    r["a7_inapoi_la_firma"] = {"pastrat": _complet(_stare(pg))}

    # alt utilizator, ACELAȘI browser (localStorage comun): ciorna asistentului NU apare la el; înapoi la asistent, e acolo
    _intra(pg, baza, ALT_USER)
    _firma(pg, baza, FIRMA)
    _deschide_emitere(pg)
    st = _stare(pg)
    r["a8_alt_utilizator"] = {"gol": _gol(st), "anunt": bool(st["anunt"]), "stare": st}
    pg.screenshot(path=os.path.join(dir_capturi, "a8_alt_utilizator.png"), full_page=True)
    _intra(pg, baza, ASISTENT)
    _firma(pg, baza, FIRMA)
    _deschide_emitere(pg)
    r["a8_inapoi_la_asistent"] = {"pastrat": _complet(_stare(pg))}
    r["axe_formular_restaurat"] = _axe(pg)

    # „Renunță”: ciorna se șterge, formularul gol rămâne gol la redeschidere
    if pg.query_selector("#em-renunta"):
        pg.click("#em-renunta")
        pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=5000)
        pg.click("#caseta-atentie-activa #ca-ok")
        pg.wait_for_selector("#em-cui", timeout=15000)
        pg.wait_for_timeout(900)
        r["a9_dupa_renunta"] = {"gol": _gol(_stare(pg)), "ciorne": _ciorne(pg)}
        pg.fill("#em-l0-cantitate", "1")      # o tastă după renunțare: ciorna veche nu are voie să învie
        pg.wait_for_timeout(400)
        r["a9_ciorne_dupa_o_tasta"] = _ciorne(pg)
        pg.click(".nav-x"); pg.wait_for_timeout(600)
        _firma(pg, baza, FIRMA)
        _deschide_emitere(pg)
        st = _stare(pg)
        r["a9_redeschis"] = {"descriere_l0": st["#em-l0-descriere"], "l1": st["#em-l1-descriere"], "cui": st["#em-cui"]}
    r["erori_consola"] = erori
    b.close()
    return r


def _titlu(pg):
    t = pg.query_selector(".fereastra .pf-titlu, .fereastra h2")
    return t.inner_text().strip()[:60] if t else ("acasă" if pg.query_selector(".asi-arbore, .cab-grila") else "?")


def repere():
    assert cui_valid(CUI_DANTE), "CUI de probă cu cifra de control greșită"
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE nume ILIKE %s ORDER BY id LIMIT 1", (FIRMA + "%",))
        tid, sch = cur.fetchone()
        r = {"tid": tid, "sch": sch}
        cur.execute('SELECT COALESCE(MAX(id),0) FROM "%s".articole' % sch); r["art"] = cur.fetchone()[0]
        cur.execute('SELECT COALESCE(MAX(id),0) FROM "%s".produse' % sch); r["prod"] = cur.fetchone()[0]
        cur.execute('SELECT COALESCE(MAX(id),0) FROM "%s".facturi' % sch); r["facturi"] = cur.fetchone()[0]
        cur.execute('SELECT * FROM "%s".firma_profil LIMIT 1' % sch)
        r["profil_col"] = [d[0] for d in cur.description]
        r["profil"] = list(cur.fetchone())
        # profilul complet (altfel „Emite” e dezactivat: „Completează întâi în Date firmă…”); se pune la loc în `curata`
        cur.execute('UPDATE "%s".firma_profil SET reg_com=COALESCE(NULLIF(reg_com,\'\'),\'J40/1/2020\'), adresa=COALESCE(NULLIF(adresa,\'\'),'
                    '\'Str. Proba 1\'), banca=COALESCE(NULLIF(banca,\'\'),\'Banca Proba\'), iban=COALESCE(NULLIF(iban,\'\'),\'RO49AAAA1B31007593840000\'), '
                    'forma_juridica=\'SRL\', capital_subscris=200, capital_varsat=200' % sch)
        # ca F1 pe producție (tenant_049): articolul de stoc „Marfa A” și produsul din nomenclator cu preț de vânzare 100, 21%
        cur.execute('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES (\'Marfa A\', \'buc\', \'371\', \'607\') RETURNING id' % sch)
        r["art_nou"] = cur.fetchone()[0]
        cur.execute('INSERT INTO "%s".produse (denumire, um, pret_unitar, cota_tva, sursa, confirmat) VALUES (\'Marfa A\', \'buc\', 100, 21, \'manual\', true) RETURNING id' % sch)
        r["prod_nou"] = cur.fetchone()[0]
        c.commit()
    return r


def curata(rp):
    db.init_pool()
    sch = rp["sch"]
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute('DELETE FROM "%s".facturi WHERE id > %%s' % sch, (rp["facturi"],))
        cur.execute('DELETE FROM "%s".produse WHERE id > %%s' % sch, (rp["prod"],))
        cur.execute('DELETE FROM "%s".articole WHERE id > %%s' % sch, (rp["art"],))
        cols = [x for x in rp["profil_col"] if x != "id"]
        vals = [v for x, v in zip(rp["profil_col"], rp["profil"]) if x != "id"]
        cur.execute('UPDATE "%s".firma_profil SET %s' % (sch, ", ".join('"%s"=%%s' % x for x in cols)), vals)
        c.commit()
    return "curatat"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    dir_capturi = a.iesire.replace(".json", "_capturi")
    os.makedirs(dir_capturi, exist_ok=True)
    rp = repere()
    r = {}
    try:
        with sync_playwright() as pw:
            proba(pw, a.baza, dir_capturi, rp, r)
    except Exception as e:  # noqa: BLE001 — rezultatele de până la eroare rămân în fișier, eroarea cu ele
        r["EROARE_PROBA"] = "%s: %s" % (type(e).__name__, str(e).splitlines()[0][:300])
    finally:
        print(curata(rp))
        json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k, v in r.items():
        print(k, json.dumps(v, ensure_ascii=False)[:600])


if __name__ == "__main__":
    main()
