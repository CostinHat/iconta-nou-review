# -*- coding: utf-8 -*-
"""PROBA în browser — răspunsurile lui Costin la confirmările de drepturi (04.10.2026), punctele 1, 2 și 5.

1. R52 răsturnat: asistentul cu „Poate pregăti” vede, pe firmele alocate, fluturașul, fotografia bonului și PDF-ul chitanței.
2. Regimul de TVA la „Poate pregăti”, cu fiecare schimbare jurnalizată (utilizator, dată, vechi → nou).
5. REGES: configurarea cheilor doar la administrator; trimiterea și răspunsurile la „Poate depune”.

Un singur cont de asistent, două faze de drepturi (`--drepturi pregatire` = doar „Poate pregăti”, ca Ana; `depunere` =
„Poate pregăti” + „Poate depune”). Bifele le pune lanțul care o rulează (pe baza de TEST), nu proba.

SCRIE în bază DOAR la punctul 2 (salvează „Date firmă” pe firma `--firma-tva`, ca să se vadă rândul de jurnal); lanțul
care o rulează restaurează profilul și șterge rândurile de jurnal după. Pe producție nu se rulează.

    PYTHONPATH=. ./venv/bin/python frontend_test/proba_drepturi_confirmari.py --baza http://127.0.0.1:8011 \
        --asistent asistent@prisma-cont.test --drepturi pregatire --iesire /tmp/.../dupa_pregatire.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from proba_asistent_drepturi import _axe, _pagina, _sesiune, _deschide_firme_asistent  # noqa: E402


def _vizibil(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def _deschide_firma(pg, baza, nume):
    _deschide_firme_asistent(pg, baza)
    pg.locator("#firme-lista button.firme-rand", has_text=nume).first.click()
    pg.wait_for_selector("#fa-salariati, #fa-datefirma", timeout=15000)
    pg.wait_for_timeout(500)


def _tid_alocat(email, nume):
    from core import db
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT t.id FROM public.tenants t JOIN public.user_tenants ut ON ut.tenant_id = t.id "
                    "JOIN public.users u ON u.id = ut.user_id WHERE u.email = %s AND t.nume ILIKE %s", (email, nume + "%"))
        r = cur.fetchone()
        c.rollback()
    return r[0] if r else None


def _inapoi(pg, sel):
    pg.click(".nav-sageata.nav-inapoi")
    pg.wait_for_selector(sel, timeout=15000)
    pg.wait_for_timeout(300)


def proba(pw, baza, asistent, firma_doc, firma_tva, drepturi, iesire):
    r = {"drepturi": drepturi}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    citiri = []
    pg.on("response", lambda x: citiri.append((x.url.split("//", 1)[-1].split("/", 1)[-1].split("?")[0], x.status))
          if x.request.method == "GET" and any(k in x.url for k in ("/fluturas/", "/imagine/", "/chitante/")) else None)

    # ── 1. documentele de terț ────────────────────────────────────────────────────────────────────────────────────
    _deschide_firma(pg, baza, firma_doc)
    tid = _tid_alocat(asistent, firma_doc)
    pg.click("#fa-salariati")
    pg.wait_for_selector("#sp-reges-zona", state="attached", timeout=20000)
    pg.wait_for_timeout(900)
    s = {"fluturas_vizibile": _vizibil(pg, "[data-flut]"), "reges_rand_vizibile": _vizibil(pg, "[data-reges]"),
         "reges_raspunsuri_vizibil": _vizibil(pg, "#sp-reges-poll"), "chei_reges_vizibil": _vizibil(pg, "#sp-reges-cfg")}
    if s["fluturas_vizibile"]:
        with pg.expect_response(lambda x: "/fluturas/" in x.url, timeout=20000) as rr:
            pg.locator("[data-flut]").first.click()
        s["fluturas_raspuns"] = [rr.value.status, rr.value.headers.get("content-type")]
    pg.screenshot(path=iesire + "_salariati_%s.png" % drepturi, full_page=True)
    s["axe"] = _axe(pg)
    r["salariati"] = s
    _inapoi(pg, "#fa-bonuri")
    pg.click("#fa-bonuri")
    pg.wait_for_selector("[data-doc], .stare-goala", timeout=20000)
    pg.wait_for_timeout(600)
    bon = {"bonuri": pg.eval_on_selector_all("[data-doc]", "e => e.length")}
    if bon["bonuri"]:
        pg.locator("[data-doc]").first.click()
        pg.wait_for_selector("#d-poze", timeout=15000)
        pg.wait_for_timeout(2500)
        bon["poze_afisate"] = pg.eval_on_selector_all("#d-poze img", "e => e.filter(i => i.complete && i.naturalWidth > 0).length")
        bon["mesaj"] = pg.eval_on_selector_all("#d-poze .ecran-nota", "e => e.map(x => x.textContent.trim())")
        pg.screenshot(path=iesire + "_bon_%s.png" % drepturi, full_page=True)
        bon["axe"] = _axe(pg)
    r["bon"] = bon
    # PDF-ul chitanței: firma de test n-are chitanțe -> se cere direct un id inexistent; garda răspunde ÎNAINTE de căutare
    r["chitanta_pdf_id_inexistent"] = pg.evaluate("""async (tid) => {
      const t = sessionStorage.getItem('iconta_token');
      const x = await fetch('/tenants/' + tid + '/chitante/999999/pdf', {headers: {Authorization: 'Bearer ' + t}});
      let d = null; try { d = (await x.json()).detail; } catch (e) {}
      return {status: x.status, detail: d};
    }""", tid)
    r["citiri_documente"] = citiri

    # ── 2. regimul de TVA, cu jurnal (doar în faza de pregătire: aceeași firmă, o singură schimbare) ──────────────────
    if drepturi == "pregatire":
        b.close()
        b, pg, cereri, erori2 = _pagina(pw, _sesiune(asistent))
        erori += erori2
        _deschide_firma(pg, baza, firma_tva)
        pg.click("#fa-datefirma")
        pg.wait_for_selector("#vf-platitor_tva", timeout=15000)
        pg.wait_for_timeout(600)
        t = {"inainte": [pg.eval_on_selector("#vf-platitor_tva", "e => e.value"),
                         pg.eval_on_selector("#vf-tip_decont", "e => e.value")],
             "salveaza_vizibil": _vizibil(pg, "#df-salveaza")}
        pg.select_option("#vf-platitor_tva", "da")
        pg.select_option("#vf-tip_decont", "trimestrial")
        # firma de test poate avea câmpuri de identificare goale, pe care formularul le cere înainte de vector: se
        # completează cu valori de formă validă (profilul se restaurează din instantaneu de lanțul care rulează proba)
        t["completate"] = []
        for _ in range(4):
            n0 = len(cereri)
            pg.click("#df-salveaza")
            pg.wait_for_timeout(5000)
            goale = pg.eval_on_selector_all("[aria-invalid='true']", "e => e.map(x => x.id)")
            if not goale or any(c[1].endswith("/vector") for c in cereri[n0:]):
                break
            for g in goale:
                val = {"df-reg_com": "J40/1234/2015", "df-caen": "9602", "df-cod_postal": "010011"}.get(g, "Proba ZT")
                pg.fill("#" + g, val)
                t["completate"].append([g, val])
        t["cereri_la_salvare"] = cereri[n0:]
        t["erori_campuri"] = pg.eval_on_selector_all(".msg-eroare, .camp-eroare-mesaj", "e => e.map(x => x.textContent.trim()).filter(Boolean)")
        t["mesaj"] = pg.eval_on_selector_all("#df-msg", "e => e.map(x => x.textContent.trim())")
        t["dupa"] = [pg.eval_on_selector("#vf-platitor_tva", "e => e.value"),
                     pg.eval_on_selector("#vf-tip_decont", "e => e.value")]
        pg.screenshot(path=iesire + "_date_firma_tva.png", full_page=True)
        t["axe"] = _axe(pg)
        r["regim_tva"] = t
    r["cereri_scriere"] = cereri
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma-doc", default="Panificatie")
    ap.add_argument("--firma-tva", default="Coafor")
    ap.add_argument("--drepturi", choices=("pregatire", "depunere"), required=True)
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.firma_doc, a.firma_tva, a.drepturi, a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
