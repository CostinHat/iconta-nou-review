# -*- coding: utf-8 -*-
"""PROBA în browser — lotul 07.10, partea 2 (retestul Costin din 06.10.2026, F5 salarii + F1 factură), pe baza de TEST (8011).

Aceeași probă rulează pe codul VECHI (worktree la `main`, înainte) și pe cel NOU (ramura lotului, după); ce lipsește în forma
veche iese ca `None` / `False`, nu ca excepție. SCRIE în baza de test (note, elemente în coadă, notificări, jurnalul Date firmă,
numerotarea) — `--curata` le șterge după reperele luate la pornire și pune la loc profilul firmei și bifele asistentului.

    PYTHONPATH=.:frontend_test ./venv/bin/python frontend_test/proba_lot0710.py --asistent asistent@prisma-cont.test \
        --validator patron@prisma-cont.test --iesire /tmp/.../l0710_dupa.json
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
from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402

CLIENT = {"#em-cui": "14399840", "#em-nume": "ZT Client Lot 0710", "#em-adresa": "Str. Proba 7, București"}


def _texte(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).map(e => e.innerText.trim()).filter(Boolean)")


def _in_vedere(pg, sel):
    """Elementul e în zona vizibilă a ferestrei (nu sub ea)?"""
    return pg.evaluate("""(s) => { const e = document.querySelector(s); if (!e) return null;
        const r = e.getBoundingClientRect(); const c = e.closest('.fereastra-corp');
        const sus = Math.max(0, c ? c.getBoundingClientRect().top : 0), jos = Math.min(innerHeight, c ? c.getBoundingClientRect().bottom : innerHeight);
        return r.top >= sus - 1 && r.bottom <= jos + 1; }""", sel)


def _desktop(pg, baza, sel=".asi-arbore, .cab-grila"):
    pg.goto(baza + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(sel, timeout=20000)
    pg.wait_for_timeout(700)


def _firma(pg, baza, firma):
    _desktop(pg, baza)
    if pg.query_selector(".asi-nod[data-nod='firme']"):
        pg.click(".asi-nod[data-nod='firme']")
    pg.wait_for_selector("#firme-lista button.firme-rand", timeout=15000)
    pg.locator("#firme-lista button.firme-rand", has_text=re.compile(firma)).first.click()
    pg.wait_for_selector("#fa-facturi", timeout=15000)
    pg.wait_for_timeout(400)


def _emitere(pg, baza, firma):
    _firma(pg, baza, firma)
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-emite", timeout=15000)
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui, #em-nu", timeout=20000)
    if pg.query_selector("#em-nu"):        # numerotare neconfigurată: „încep acum”, cu seria (cerută din 06.10) și regimul TVA
        if pg.query_selector("#em-tva-da"):
            pg.click("#em-tva-da")
        pg.click("#em-nu")
        pg.wait_for_selector("#em-salveaza-config2", timeout=10000)
        pg.fill("#em-serie2", "ZT")
        pg.click("#em-salveaza-config2")
        pg.wait_for_selector("#em-cui", timeout=20000)
    pg.wait_for_timeout(800)


def _stare_formular(pg):
    sel = list(CLIENT) + ["#em-l0-descriere", "#em-l0-cantitate", "#em-l0-pret_unitar", "#em-scadenta"]
    return {s: (pg.eval_on_selector(s, "e => e.value") if pg.query_selector(s) else None) for s in sel}


def _jurnal(pg, baza, firma):
    _firma(pg, baza, firma)
    pg.click("#fa-jurnal")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    pg.wait_for_timeout(600)


def _validat(pg, baza):
    _desktop(pg, baza, ".cab-grila")
    pg.evaluate("""() => { const s = document.querySelector(".cab-card-sinteza[data-cheie='validat']");
                            (s && s.closest('.cab-card') || {click(){}}).click(); }""")
    pg.wait_for_selector("#val-note, #val-deValidat", timeout=20000)
    pg.wait_for_timeout(900)


def _stat(pg, baza, firma, pasi):
    _firma(pg, baza, firma)
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-contare", timeout=20000)
    for _ in range(pasi):
        pg.click("#sp-prev")
        pg.wait_for_selector("#sp-contare", timeout=20000)
        pg.wait_for_timeout(400)
    pg.wait_for_timeout(600)


def proba(pw, baza, asistent, validator, firma, pasi, iesire):
    r = {}
    azi = datetime.date.today()
    # ── A) factura: scadența propusă, refuzul cu buton, mesajul în vedere, ciorna păstrată, renunțarea ─────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent), inalt=520)   # ecran mic: mesajul de sub buton cade sub zona vizibilă
    _emitere(pg, baza, firma)
    r["A_scadenta_la_deschidere"] = pg.eval_on_selector("#em-scadenta", "e => e.value")
    r["A_scadenta_asteptata"] = (azi + datetime.timedelta(days=30)).isoformat()
    for s, v in CLIENT.items():
        pg.fill(s, v)
    pg.fill("#em-l0-descriere", "Vânzare marfă: făină")   # marfă -> cont 707 (facturi.tip_din_denumire) -> metoda de stoc
    pg.fill("#em-l0-cantitate", "2")
    pg.fill("#em-l0-pret_unitar", "150")
    try:
        pg.wait_for_function("() => { const c = document.querySelector('#em-l0-cota'); return c && (c.value || /%/.test(c.textContent)); }", timeout=20000)
    except Exception:  # noqa: BLE001
        pass
    # ca omul: butonul „Emite” la marginea de JOS a ferestrei, clic de mouse pe el (fără derularea automată a Playwright)
    pg.evaluate("() => document.querySelector('#em-emite').scrollIntoView({block: 'end'})")
    pg.wait_for_timeout(500)
    bb = pg.locator("#em-emite").bounding_box()
    pg.mouse.click(bb["x"] + bb["width"] / 2, bb["y"] + bb["height"] / 2)
    pg.wait_for_timeout(3500)
    if pg.query_selector("#em-poarta-nu"):
        pg.click("#em-poarta-nu"); pg.wait_for_timeout(3000)
    pg.wait_for_timeout(900)    # derularea lină se termină
    r["A_refuz"] = (pg.eval_on_selector("#em-rezultat", "e => e.innerText") or "")[:240]
    r["A_buton_spre_ecran"] = [t for t in _texte(pg, "#em-rezultat button")]
    r["A_refuz_in_vedere"] = _in_vedere(pg, "#em-rezultat .em-curs-box, #em-rezultat")
    pg.screenshot(path=iesire + "_A_refuz.png", full_page=False)
    r["A_formular_inainte"] = _stare_formular(pg)
    pg.click(".nav-x")                       # X: acasă (drumul care, înainte, pierdea formularul)
    pg.wait_for_timeout(800)
    _emitere(pg, baza, firma)
    r["A_formular_dupa_X"] = _stare_formular(pg)
    r["A_anunt_ciorna"] = _texte(pg, "#em-ciorna")
    pg.screenshot(path=iesire + "_A_reluat.png", full_page=True)
    r["A_axe"] = _axe(pg)
    if pg.query_selector("#em-renunta"):
        pg.click("#em-renunta")
        pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=5000)
        pg.wait_for_timeout(900)
        r["A_confirmare_in_vedere"] = _in_vedere(pg, "#caseta-atentie-activa")
        pg.click("#caseta-atentie-activa #ca-ok")
        pg.wait_for_selector("#em-cui", timeout=15000)
        pg.wait_for_timeout(800)
        r["A_dupa_renuntare"] = _stare_formular(pg)
    r["A_erori_consola"] = erori
    b.close()
    # ── B) Stocuri și Casa: formularele nu stau deschise ───────────────────────────────────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _firma(pg, baza, firma)
    pg.click("#fa-stocuri")
    pg.wait_for_selector("#sn-zona", state="attached", timeout=20000)
    pg.wait_for_timeout(500)
    r["B_nir_vizibil_la_deschidere"] = pg.is_visible("#sn-zona")
    pg.screenshot(path=iesire + "_B_stocuri.png", full_page=True)
    _firma(pg, baza, firma)
    pg.click("#fa-casa")
    pg.wait_for_selector("#c-zona", state="attached", timeout=20000)
    pg.wait_for_timeout(500)
    r["B_dispozitie_vizibila_la_deschidere"] = pg.is_visible("#c-zona")
    b.close()
    # ── C) asistentul scrie o notă din jurnal: data în editor, nota la validare nu se mai editează ─────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _jurnal(pg, baza, firma)
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-desc", timeout=10000)
    r["C_camp_data_in_editor"] = bool(pg.query_selector("#je-data"))
    pg.fill("#je-desc", "ZT Lot0710 chirie")
    pg.fill("#je-doc", "Factura ZT-CH1 din 05.10.2026")
    pg.fill("#je-linii .je-deb", "612")
    pg.fill("#je-linii .je-cre", "401")
    pg.fill("#je-linii .je-sum", "100")
    with pg.expect_response(lambda x: re.search(r"/jurnal$", x.url.split("?")[0]) is not None and x.request.method == "POST", timeout=30000) as rr:
        pg.click("#je-salveaza")
    r["C_creare_status"] = rr.value.status
    pg.wait_for_timeout(1500)
    rand = pg.locator(".pf-frand", has_text="ZT Lot0710 chirie").first
    r["C_rand"] = rand.inner_text()[:300] if rand.count() else None
    r["C_butoane_pe_rand"] = rand.locator("button").all_inner_texts() if rand.count() else None
    r["C_antet"] = _texte(pg, "p.pf-intro")[:1]
    pg.screenshot(path=iesire + "_C_jurnal_asistent.png", full_page=True)
    b.close()
    # ── D) validatorul: cardul, fereastra, notificarea care duce la notă, respingerea ──────────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(validator))
    _desktop(pg, baza, ".cab-grila")
    pg.wait_for_timeout(1500)
    r["D_card_titlu"] = pg.evaluate("""() => { const s = document.querySelector(".cab-card-sinteza[data-cheie='validat']");
                                                 const c = s && s.closest('.cab-card'); return c ? c.querySelector('.cab-card-titlu').innerText : null; }""")
    r["D_card_sinteza"] = _texte(pg, ".cab-card-sinteza[data-cheie='validat']")
    if pg.query_selector("#nav-clopot"):
        pg.click("#nav-clopot")
        pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=10000)
        pg.wait_for_timeout(600)
        r["D_notificari"] = _texte(pg, ".clopot-item .clopot-text")[:4]
        it = pg.locator(".clopot-item", has_text="ZT Lot0710 chirie").first
        if it.count():
            it.click()
            pg.wait_for_timeout(2500)
            r["D_dupa_clic_notificare"] = {"fereastra": _texte(pg, ".fereastra-titlu, .nav-titlu")[:2],
                                           "evidentiat": _texte(pg, ".val-evidentiat .val-titlu")}
    _validat(pg, baza)
    r["D_fereastra_note"] = _texte(pg, "#val-note .cf-grup-titlu")
    r["D_intro"] = _texte(pg, "#val-note .mig-intro, .mig-intro")[:3]
    r["D_carduri_note"] = _texte(pg, "#val-note .val-card .val-titlu")
    pg.screenshot(path=iesire + "_D_de_validat.png", full_page=True)
    r["D_axe"] = _axe(pg)
    card = pg.locator("#val-note .val-card", has_text="ZT Lot0710 chirie").first
    if card.count():
        card.locator(".val-respinge").click()
        pg.wait_for_selector("textarea, input.camp-input", timeout=10000)
        camp = pg.locator(".fereastra-corp textarea, .fereastra-corp input.camp-input").last
        camp.fill("Data e greșită: contractul e din 1 octombrie")
        pg.locator(".fereastra-corp button.val-respinge").last.click()
        pg.wait_for_timeout(1500)
        r["D_respinsa"] = True
    b.close()
    # ── E) asistentul: antetul jurnalului, editarea datei, retrimiterea, bara „din prima” ─────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _jurnal(pg, baza, firma)
    r["E_antet_dupa_respingere"] = _texte(pg, "p.pf-intro")[:1]
    rand = pg.locator(".pf-frand", has_text="ZT Lot0710 chirie").first
    if rand.count() and rand.locator("button", has_text="Editează").count():
        rand.locator("button", has_text="Editează").click()
        pg.wait_for_selector("#je-desc", timeout=10000)
        if pg.query_selector("#je-data"):
            pg.fill("#je-data", "2026-10-01")
        with pg.expect_response(lambda x: "/jurnal/" in x.url and x.request.method == "PUT", timeout=30000) as rp:
            pg.click("#je-salveaza")
        r["E_editare_status"] = rp.value.status
        pg.wait_for_timeout(1200)
    rand = pg.locator(".pf-frand", has_text="ZT Lot0710 chirie").first
    r["E_rand_dupa_editare"] = rand.inner_text()[:200] if rand.count() else None
    if rand.count() and rand.locator("[data-retrimite]").count():
        rand.locator("[data-retrimite]").click()
        pg.wait_for_timeout(1500)
    r["E_antet_dupa_retrimitere"] = _texte(pg, "p.pf-intro")[:1]
    b.close()
    # ── F) nota de salarii: titlul, data, fraza despre semnal; validatorul o respinge; statul o arată la deschidere ──
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _stat(pg, baza, firma, pasi)
    r["F_la_deschidere_inainte_de_scriere"] = _texte(pg, "#sp-contare-zona .caseta-atentie, #sp-contare-zona p")
    with pg.expect_response(lambda x: "/salarii-contare/propunere" in x.url, timeout=90000) as rpp:
        pg.click("#sp-contare")
    r["F_propunere_status"] = rpp.value.status
    pg.wait_for_timeout(1500)
    r["F_zona_propunere"] = (pg.eval_on_selector("#sp-contare-zona", "e => e.innerText") or "")[-500:]
    r["F_buton_scrie"] = bool(pg.query_selector("#sp-contare-scrie"))
    r["F_fraza_semnal"] = [t for t in _texte(pg, "#sp-contare-zona .tip-micut") if "mai sus" in t]
    if pg.query_selector("#sp-contare-scrie"):
        with pg.expect_response(lambda x: re.search(r"/salarii-contare\?", x.url) is not None, timeout=60000) as rsc:
            pg.click("#sp-contare-scrie")
        r["F_scriere_status"] = rsc.value.status
        try:
            r["F_scriere_raspuns"] = str(rsc.value.json())[:300]
        except Exception:  # noqa: BLE001
            r["F_scriere_raspuns"] = None
        pg.wait_for_timeout(2000)
    r["F_dupa_scriere"] = _texte(pg, "#sp-contare-zona .tip-micut, #sp-contare-zona .caseta-atentie")
    b.close()
    b, pg, cereri, erori = _pagina(pw, _sesiune(validator))
    _validat(pg, baza)
    card = pg.locator("#val-note .val-card").filter(has=pg.locator(".val-titlu", has_text=re.compile("Stat de plat|Salariile lunii", re.I))).first
    r["F_titlu_nota_salarii"] = card.locator(".val-titlu").inner_text() if card.count() else None
    r["F_rand_nota_salarii"] = card.locator(".val-termen").inner_text() if card.count() else None
    if card.count():
        card.locator(".val-respinge").click()
        pg.wait_for_selector("textarea, input.camp-input", timeout=10000)
        pg.locator(".fereastra-corp textarea, .fereastra-corp input.camp-input").last.fill("Lipsește un salariat")
        pg.locator(".fereastra-corp button.val-respinge").last.click()
        pg.wait_for_timeout(1500)
    b.close()
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _stat(pg, baza, firma, pasi)
    r["F_stat_la_deschidere"] = _texte(pg, "#sp-contare-zona .caseta-atentie, #sp-contare-zona p")
    pg.screenshot(path=iesire + "_F_stat_respinsa.png", full_page=True)
    r["F_axe"] = _axe(pg)
    b.close()
    # ── G) Date firmă: eroarea de câmp adusă în vedere (pct.3); metoda declarată -> istoricul lizibil (pct.19) ──────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent), lat=420, inalt=520)
    _firma(pg, baza, firma)
    pg.click("#fa-datefirma")
    pg.wait_for_selector("#df-metoda_stoc, #df-salveaza", timeout=20000)
    pg.wait_for_timeout(800)
    r["G_are_select_metoda"] = bool(pg.query_selector("#df-metoda_stoc"))
    pg.select_option("#df-metoda_stoc", "cantitativ_valoric")
    if pg.query_selector("#df-forma_juridica"):
        pg.select_option("#df-forma_juridica", "SRL")
    if pg.query_selector("#df-capital_subscris") and not pg.eval_on_selector("#df-capital_subscris", "e => e.value"):
        pg.fill("#df-capital_subscris", "200")
    pg.click("#df-salveaza")                 # „Salvează” e jos; câmpul lipsă (Telefon) e sus
    pg.wait_for_timeout(1200)
    r["G_erori_camp"] = _texte(pg, ".msg-eroare")[:4]
    r["G_eroare_camp_in_vedere"] = _in_vedere(pg, ".msg-eroare[data-camp]")
    pg.screenshot(path=iesire + "_G_eroare_camp.png", full_page=False)
    if pg.query_selector("#df-telefon"):
        pg.fill("#df-telefon", "0700000000")
        pg.click("#df-salveaza")
        pg.wait_for_timeout(3500)
    r["G_cereri_salvare"] = [c for c in cereri if "firma-profil" in c[1] or "vector" in c[1]]
    r["G_mesaj"] = _texte(pg, "#df-msg, .msg-eroare")[:3]
    r["G_jurnal"] = _texte(pg, "#df-jurnal tbody tr")[:3]
    r["G_derulare_orizontala"] = pg.evaluate("""() => { const t = document.querySelector('#df-jurnal'); const c = t && t.closest('.fereastra-corp');
        return t ? {tabel: t.scrollWidth, fereastra: c ? c.clientWidth : null, pagina_scroll: document.documentElement.scrollWidth > innerWidth} : null; }""")
    pg.screenshot(path=iesire + "_G_date_firma.png", full_page=True)
    r["G_axe"] = _axe(pg)
    b.close()
    # ── H) bara asistentului: pregătite / din prima ───────────────────────────────────────────────────────────────
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _desktop(pg, baza)
    pg.wait_for_timeout(1500)
    r["H_bara3"] = _texte(pg, ".bara3")
    b.close()
    return r


def repere():
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE nume ILIKE 'Panificatie%' ORDER BY id LIMIT 1")
        tid, sch = cur.fetchone()
        r = {"tid": tid, "sch": sch}
        for k, q in (("coada", "SELECT COALESCE(MAX(id),0) FROM public.declaratii_coada"), ("notif", "SELECT COALESCE(MAX(id),0) FROM public.notificari"),
                     ("note", 'SELECT COALESCE(MAX(id),0) FROM "%s".inregistrari' % sch), ("fpj", 'SELECT COALESCE(MAX(id),0) FROM "%s".firma_profil_jurnal' % sch),
                     ("facturi", 'SELECT COALESCE(MAX(id),0) FROM "%s".facturi' % sch)):
            cur.execute(q); r[k] = cur.fetchone()[0]
        cur.execute('SELECT * FROM "%s".firma_profil LIMIT 1' % sch)
        r["profil_col"] = [d[0] for d in cur.description]
        r["profil"] = list(cur.fetchone())
        cur.execute('UPDATE "%s".firma_profil SET reg_com=COALESCE(NULLIF(reg_com,\'\'),\'J40/1/2020\'), adresa=COALESCE(NULLIF(adresa,\'\'),\'Str. Proba 1\'), '
                    'banca=COALESCE(NULLIF(banca,\'\'),\'Banca Proba\'), iban=COALESCE(NULLIF(iban,\'\'),\'RO49AAAA1B31007593840000\')' % sch)
        # cazul din retest (F1, 06.10): profilul complet, venitul pe 707 (marfă), metoda de stoc NEDECLARATĂ -> refuzul la „Emite”
        cur.execute('UPDATE "%s".firma_profil SET forma_juridica=\'SRL\', capital_subscris=200, capital_varsat=200, '
                    'cont_venit_implicit=\'707\', metoda_stoc=NULL' % sch)
        cur.execute("SELECT poate_pregati, poate_valida, poate_depune FROM public.users WHERE email='asistent@prisma-cont.test'")
        r["bife"] = list(cur.fetchone())
        cur.execute("UPDATE public.users SET poate_pregati=true, poate_valida=false WHERE email='asistent@prisma-cont.test'")
        c.commit()
    return r


def curata(rp):
    db.init_pool()
    sch = rp["sch"]
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("DELETE FROM public.notificari WHERE id > %s", (rp["notif"],))
        cur.execute("DELETE FROM public.declaratii_coada WHERE id > %s AND tenant_id = %s", (rp["coada"], rp["tid"]))
        cur.execute('DELETE FROM "%s".inregistrari WHERE id > %%s' % sch, (rp["note"],))
        cur.execute('DELETE FROM "%s".facturi WHERE id > %%s' % sch, (rp["facturi"],))
        cur.execute('DELETE FROM "%s".firma_profil_jurnal WHERE id > %%s' % sch, (rp["fpj"],))
        cols = [c for c in rp["profil_col"] if c != "id"]
        vals = [v for c, v in zip(rp["profil_col"], rp["profil"]) if c != "id"]
        cur.execute('UPDATE "%s".firma_profil SET %s' % (sch, ", ".join('"%s"=%%s' % c for c in cols)), vals)
        cur.execute("UPDATE public.users SET poate_pregati=%s, poate_valida=%s, poate_depune=%s WHERE email='asistent@prisma-cont.test'",
                    tuple(rp["bife"]))
        c.commit()
    return "curatat"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--validator", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--pasi-inapoi", type=int, default=1)   # 09/2026: deschisă (08/2026 e închisă pe firma de test)
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    rp = repere()
    try:
        with sync_playwright() as pw:
            r = proba(pw, a.baza, a.asistent, a.validator, a.firma, a.pasi_inapoi, a.iesire.replace(".json", ""))
    finally:
        print(curata(rp))
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    for k, v in r.items():
        if not k.endswith("_axe") and k != "A_erori_consola":
            print(k, json.dumps(v, ensure_ascii=False)[:400])
    for k in sorted(x for x in r if x.endswith("_axe")):
        print(k, (r[k] or {}).get("violari"), (r[k] or {}).get("reguli"))


if __name__ == "__main__":
    main()
