# -*- coding: utf-8 -*-
"""PROBA în browser — emiterea pe F1 (comanda Costin 05.10.2026, pct.2–5), pe contul de asistent, baza de TEST.

1) la DESCHIDEREA „Emite factură”: se spune ce lipsește din Date firmă? „Emite” e activ?
2) Date firmă: forma juridică e propusă? -> se completează capitalul, Salvează, Înapoi -> nota dispare, „Emite” se activează?
3) formularul: data emiterii, scadența, seria; cota propusă se poate schimba
4) emiterea -> rândul din jurnalul cotei (propus -> ales, cine)
5) PDF-ul: codul cu RO (furnizor + beneficiar), „Seria … nr. …”, „Data emiterii”, scadența, titlul documentului
Lanțul care o rulează restaurează profilul firmei și șterge factura emisă.
"""
import argparse
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright  # noqa: E402

from core import db  # noqa: E402
from proba_asistent_drepturi import _axe, _pagina, _sesiune  # noqa: E402
from proba_fara_pierdere import _deschide_emiterea  # noqa: E402


def _viz(pg, sel):
    return pg.eval_on_selector_all(sel, "els => els.filter(e => e.offsetParent !== null).length")


def proba(pw, baza, asistent, firma, tid, schema, iesire):
    r = {}
    b, pg, cereri, erori = _pagina(pw, _sesiune(asistent))
    _deschide_emiterea(pg, baza, firma)
    r["1_la_deschidere"] = {
        "nota_lipsuri": pg.eval_on_selector_all("#em-pregatire .ca-mesaj", "e => e.map(x => x.innerText.trim())"),
        "emite_activ": pg.eval_on_selector("#em-emite", "e => !e.disabled"),
        "camp_data": _viz(pg, "#em-data"), "camp_scadenta": _viz(pg, "#em-scadenta"), "serie_vizibila": _viz(pg, "#em-serie-nr"),
        "antet_numar": pg.eval_on_selector(".em-numar", "e => e.innerText"),
        "cota_e_lista": bool(pg.query_selector("select#em-l0-cota")),
    }
    pg.screenshot(path=iesire + "_1_deschidere.png", full_page=True)
    r["1_axe"] = _axe(pg)
    pg.fill("#em-cui", "14399840"); pg.fill("#em-nume", "DANTE INTERNATIONAL SA"); pg.fill("#em-adresa", "Șos. Virtuții 148, București")
    pg.fill("#em-l0-descriere", "Pâine albă feliată")
    pg.fill("#em-l0-cantitate", "2"); pg.fill("#em-l0-pret_unitar", "100")
    try:
        pg.wait_for_function("() => { const c = document.querySelector('#em-l0-cota'); return c && (c.tagName === 'SELECT' ? c.value !== '' : /%/.test(c.textContent)); }", timeout=25000)
    except Exception:
        pass
    pg.wait_for_timeout(600)
    r["3_cota_propusa"] = pg.eval_on_selector("#em-l0-cota", "e => e.tagName === 'SELECT' ? e.value : e.textContent")
    # 2) Date firmă: propunerea + capitalul + Salvează + Înapoi
    deschide = pg.query_selector("#em-date-firma-sus")
    r["2_buton_sus"] = bool(deschide)
    if deschide:
        deschide.click()
        pg.wait_for_selector("#df-forma_juridica", timeout=15000)
        pg.wait_for_timeout(800)
        r["2_date_firma"] = {"forma_preselectata": pg.eval_on_selector("#df-forma_juridica", "e => e.value"),
                             "nota_propusa": pg.eval_on_selector_all("#df-forma-propusa", "e => e.map(x => x.innerText)")}
        pg.screenshot(path=iesire + "_2_date_firma.png", full_page=True)
        r["2_axe"] = _axe(pg)
        for sel, v in (("#df-capital_subscris", "200"),):
            pg.fill(sel, v)
        # câmpurile obligatorii ale firmei de test (altfel Date firmă refuză salvarea)
        for cid, v in (("df-reg_com", "J40/1234/2015"), ("df-adresa", "Str. Proba 1"), ("df-banca", "Banca Proba"),
                       ("df-iban", "RO49AAAA1B31007593840000"), ("df-telefon", "0712345678")):
            el = pg.query_selector("#" + cid)
            if el and not el.input_value():
                el.fill(v)
        pg.click("#df-salveaza")
        pg.wait_for_timeout(2500)
        r["2_mesaj_salvare"] = pg.eval_on_selector_all("#df-msg, .msg-eroare", "e => e.map(x => x.innerText.trim()).filter(Boolean)")
        pg.click(".nav-sageata.nav-inapoi")
        pg.wait_for_timeout(2500)
        r["2_dupa_inapoi"] = {"nota_lipsuri": pg.eval_on_selector_all("#em-pregatire .ca-mesaj", "e => e.map(x => x.innerText.trim())"),
                              "emite_activ": pg.eval_on_selector("#em-emite", "e => !e.disabled"),
                              "client_pastrat": pg.eval_on_selector("#em-nume", "e => e.value")}
    # 3) cota schimbată + scadența
    if pg.query_selector("select#em-l0-cota"):   # altă cotă decât cea propusă -> rândul de jurnal „propus -> ales”
        pg.select_option("select#em-l0-cota", "21" if r["3_cota_propusa"] == "11" else "11")
        r["3_cota_aleasa"] = pg.eval_on_selector("#em-l0-cota", "e => e.value")
        pg.wait_for_timeout(300)
    if pg.query_selector("#em-scadenta"):
        pg.fill("#em-scadenta", "2026-11-04")
    # 4) emiterea
    if not pg.eval_on_selector("#em-emite", "e => !e.disabled"):
        r["4_emitere"] = {"status": None, "motiv": "„Emite” inactiv: " + (pg.eval_on_selector("#em-emite", "e => e.title") or "")}
        pg.screenshot(path=iesire + "_4_inactiv.png", full_page=True)
        r["erori_consola"] = erori
        b.close()
        return r
    with pg.expect_response(lambda x: x.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    raspuns = rr.value
    corp = {}
    try:
        corp = raspuns.json()
    except Exception:
        pass
    r["4_emitere"] = {"status": raspuns.status, "factura_id": corp.get("factura_id"), "numar": corp.get("numar"),
                      "detaliu": (corp.get("detail") if isinstance(corp.get("detail"), str) else json.dumps(corp.get("detail"), ensure_ascii=False))[:300] if corp.get("detail") else None}
    pg.wait_for_timeout(2000)
    pg.screenshot(path=iesire + "_4_emis.png", full_page=True)
    fid = corp.get("factura_id")
    if fid:
        with db.get_conn() as c, c.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", ("%s.factura_cota_jurnal" % schema,))
            if cur.fetchone()[0]:
                cur.execute("SELECT linie_nr, descriere, cota_propusa::float, cota_aleasa::float, (SELECT email FROM public.users WHERE id=user_id) "
                            "FROM %s.factura_cota_jurnal WHERE factura_id=%%s" % schema, (fid,))
                r["4_jurnal_cota"] = cur.fetchall()
            cur.execute("SELECT data_emitere::text, data_scadenta::text, serie, numar, tert_platitor_tva FROM %s.facturi WHERE id=%%s" % schema, (fid,))
            r["4_factura_in_baza"] = cur.fetchone()
            c.rollback()
        # 5) PDF-ul, cerut din pagină (aceeași sesiune)
        pdf_b64 = pg.evaluate("""async ([tid, fid]) => {
            const t = sessionStorage.getItem('iconta_token');
            const x = await fetch('/tenants/' + tid + '/facturi/' + fid + '/pdf', {headers: {Authorization: 'Bearer ' + t}});
            const b = new Uint8Array(await x.arrayBuffer()); let s = ''; for (const c of b) s += String.fromCharCode(c); return btoa(s);
        }""", [tid, fid])
        import base64
        from pypdf import PdfReader
        rd = PdfReader(io.BytesIO(base64.b64decode(pdf_b64)))
        text = re.sub(r"\s+", " ", "\n".join(p.extract_text() for p in rd.pages))
        r["5_pdf"] = {"titlu": (rd.metadata or {}).get("/Title"),
                      "cod_furnizor": re.findall(r"(?:Cod TVA|CIF|CUI)[: ]+\S+", text)[:3],
                      "serie": re.findall(r"Seria \S+ nr\. \S+|Nr\. \S+", text)[:1] or re.findall(r"FACTURĂ \S+", text)[:1],
                      "data": re.findall(r"Data emiterii: \S+|Emisă - \S+", text)[:1],
                      "scadenta": re.findall(r"Data scadenței: \S+|Scadență: \S+", text)[:1]}
        open(iesire + "_5_factura.pdf", "wb").write(base64.b64decode(pdf_b64))
    r["erori_consola"] = erori
    b.close()
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baza", default=os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011"))
    ap.add_argument("--asistent", required=True)
    ap.add_argument("--firma", default="Panificatie")
    ap.add_argument("--tid", type=int, default=4784)
    ap.add_argument("--schema", default="tenant_001")
    ap.add_argument("--iesire", required=True)
    a = ap.parse_args()
    db.init_pool()
    with sync_playwright() as pw:
        r = proba(pw, a.baza, a.asistent, a.firma, a.tid, a.schema, a.iesire[:-5] if a.iesire.endswith(".json") else a.iesire)
    json.dump(r, open(a.iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    print(json.dumps(r, ensure_ascii=False, indent=1, default=str)[:5000])


if __name__ == "__main__":
    main()
