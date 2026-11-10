# -*- coding: utf-8 -*-
"""DE VALIDAT ȘI CONTROL FISCAL — lotul 17.5-G (rândurile AC001, AC002, AC004, AC008, AC009 din auditul complet al ecranelor; decizii_17_5_G.txt).
Scris de arhitect; Code nu îl modifică.

La 1366×768, ceas înghețat 03.11.2026 (core/ceas_proba.MOMENT_REF), contul administratorului (dovada.71507), fără a salva nimic; fiecare
fereastră trebuie întâi să existe, altfel secțiunea pică (nimic nu trece „în gol”):
(1) G1 De validat, cu răspunsurile reale ale serverului: pe fiecare rând din tabelele de note (Note de validat, Notele tale în ciornă) coloana
    „Conturi” are text fără deschiderea rândului (niciun detaliu deschis); cel puțin un rând (snapshot: ciornele proprii pe F1, F2, F5, F6).
(2) G2 De validat, cu GET /coada înlocuit prin page.route de două note de validat fictive (snapshot-ul nu are note în coadă; nimic nu se
    scrie în bază): bara „Validează selectate” există, nimic nu e bifat, iar bara de jos a ferestrei arată
    «Bifează notele pe care le validezi împreună.».
(3) G3 câmpul de căutare (piesa comună htmlCautare) pe Casă, Bancă, Registru jurnal (F1 Comert Stoc) și De validat: textul de îndrumare
    (placeholder, nevid) încape întreg: lățimea lui, măsurată cu un span de probă cu același font, ≤ lățimea de conținut a câmpului
    (clientWidth minus padding stânga și dreapta).
(4) G4 De validat, cu GET /coada și GET /eu/ciorne înlocuite prin page.route de liste goale (nimic nu se scrie în bază): stările goale
    arată exact textele din decizii.
(5) G5 Control fiscal: rândul F1 Comert Stoc conține «Diferențe stocuri — nu se poate verifica» și nu conține «nu se poate verifica:».
Un singur test; lista „rele” numește fiecare secțiune care pică."""
import importlib.util
import json
import os
import re
import sys

from conftest import BAZA, sesiune

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc"
TEXT_G2 = "Bifează notele pe care le validezi împreună."
GOL_NOTE = "Nicio notă nu așteaptă validarea. Aici ajung notele trimise la validare de colegi și de tine; ciornele tale sunt mai jos."
GOL_CIORNE = "Nicio notă de-a ta în ciornă. Notele noi le faci din fereastra firmei, în Registru jurnal."
URL_COADA = re.compile(r"^https?://[^/]+/coada(\?.*)?$")
URL_CIORNE = re.compile(r"^https?://[^/]+/eu/ciorne(\?.*)?$")
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
# coloana „Conturi” a fiecărui tabel de note din fereastra de sus, după antet (nu după poziție): [{tabel, rand, text, detaliu_deschis}]
JS_CONTURI = """() => {
  const out = [];
  document.querySelectorAll('.fereastra-overlay:not(.fundal) table.tn-tabel').forEach((t) => {
    const th = [...t.querySelectorAll('thead th')].map((x) => (x.textContent || '').trim());
    const i = th.indexOf('Conturi');
    t.querySelectorAll('tbody.tn-nota').forEach((tb, k) => {
      if (tb.hidden) return;
      const td = i < 0 ? null : tb.querySelectorAll('tr.tn-rand > td')[i];
      const det = tb.querySelector('tr.tn-detaliu');
      out.push({ tabel: t.id || '?', rand: k, text: td ? (td.textContent || '').trim() : null, detaliu_deschis: !!det && !det.hidden });
    });
  });
  return out;
}"""
# textul de îndrumare al câmpului `sel` față de lățimea de conținut a câmpului; span de probă cu același font
JS_CAUTARE = """async (sel) => {
  await document.fonts.ready;
  const i = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel);
  if (!i) return null;
  const cs = getComputedStyle(i);
  const s = document.createElement('span');
  s.style.cssText = 'position:absolute;left:-10000px;top:0;visibility:hidden;white-space:pre;padding:0;border:0;margin:0';
  for (const p of ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'fontStretch', 'letterSpacing', 'wordSpacing', 'fontKerning', 'textTransform'])
    s.style[p] = cs[p];
  s.textContent = i.placeholder || '';
  document.body.appendChild(s);
  const text = s.scrollWidth;
  s.remove();
  const camp = i.clientWidth - parseFloat(cs.paddingLeft || '0') - parseFloat(cs.paddingRight || '0');
  return { text, camp, placeholder: i.placeholder || '', aria: i.getAttribute('aria-label') || '', vizibil: i.offsetWidth > 0 && i.offsetHeight > 0 };
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _acasa(pg):
    try:   # o pagină nouă (about:blank) n-are sessionStorage: se trece direct la goto
        pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    except Exception:   # noqa: BLE001
        pass
    pg.goto(BAZA + "/", wait_until="load", timeout=30000)
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    pg.wait_for_timeout(800)


def _de_validat(pg):
    """Pagina principală › cardul „De validat”; True dacă fereastra (titlul ei) s-a desenat."""
    _acasa(pg)
    try:
        pg.click("button.cab-card:has([data-cheie='validat'])", timeout=10000)
        pg.wait_for_selector(TOP + "#val-titlu", timeout=30000)
    except Exception:   # noqa: BLE001 — secțiunea pică mai jos, cu motivul
        return False
    pg.wait_for_timeout(2000)
    return True


def _card(pg, parcurs, firma, sel):
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2000)
    return True


def _note_fictive(tenant_id):
    """Două note de validat fictive (pregătite de alt utilizator, deci bifabile de administrator); id-uri și note care nu există în bază."""
    def nota(k):
        return {"id": 990000 + k, "tenant_id": tenant_id, "tip": "nota", "fel": "nota", "perioada": "nota-%d" % (990000 + k),
                "stare": "la_senior", "creat_de": "0", "creat_de_nume": "Coleg probă", "eticheta": "Notă probă %d" % k,
                "nota": {"inregistrare_id": 990000 + k, "data": "2026-11-02", "descriere": "Notă probă %d" % k, "document_ref": "PROBA-%d" % k,
                         "total": "10.00", "rulaj": "10.00", "rulaj_storno": "0", "_an": 2026, "_luna": 11}}
    return {"coada": [nota(1), nota(2)]}


def _json_route(corp):
    def h(route):
        if route.request.method != "GET":
            route.continue_()
            return
        route.fulfill(status=200, content_type="application/json", body=json.dumps(corp))
    return h


def _norm(t):
    return " ".join((t or "").split())


def test_de_validat_17_5_G(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        tenant_id = None
        # (1) G1 — răspunsurile reale
        try:
            with pg.expect_response(lambda r: URL_CIORNE.match(r.url) is not None and r.request.method == "GET", timeout=30000) as rc:
                deschis = _de_validat(pg)
            try:
                fr = (rc.value.json() or {}).get("firme") or []
                tenant_id = fr[0]["tenant_id"] if fr else None
            except Exception:   # noqa: BLE001
                tenant_id = None
        except Exception:   # noqa: BLE001
            deschis = _de_validat(pg)
        if not deschis:
            rele.append("(1) fereastra De validat nu s-a deschis")
        else:
            randuri = pg.evaluate(JS_CONTURI)
            if not randuri:
                rele.append("(1) De validat nu are niciun rând în tabelele de note")
            deschise = [r for r in randuri if r["detaliu_deschis"]]
            if deschise:
                rele.append("(1) %d rânduri au detaliul deschis (proba cere rândurile închise)" % len(deschise))
            goale = [r for r in randuri if not r["text"]]
            if goale:
                rele.append("(1) coloana Conturi e goală pe %d din %d rânduri (prima: tabelul %s, rândul %d)" % (
                    len(goale), len(randuri), goale[0]["tabel"], goale[0]["rand"]))
        # (2) G2 — două note fictive în coadă (page.route), nimic bifat
        p2 = b.new_page()
        p2.route(URL_COADA, _json_route(_note_fictive(tenant_id if tenant_id is not None else 0)))
        try:
            if not _de_validat(p2):
                rele.append("(2) fereastra De validat nu s-a deschis")
            elif not p2.locator(TOP + "#val-aproba-selectate").count():
                rele.append("(2) bara „Validează selectate” lipsește (cu două note de validat)")
            else:
                bifate = p2.locator(TOP + ".val-sel:checked").count()
                if bifate:
                    rele.append("(2) %d note bifate la deschidere" % bifate)
                m = p2.locator(TOP + ".fj-motiv")
                txt = _norm(m.first.inner_text()) if m.count() else ""
                if TEXT_G2 not in txt:
                    rele.append("(2) bara de jos arată «%s», nu «%s»" % (txt, TEXT_G2))
        finally:
            p2.close()
        # (3) G3 — textul de îndrumare al căutării, întreg, la 1366
        masuri = []
        if _card(pg, parcurs, F1, "#fa-casa"):
            try:
                pg.wait_for_selector(TOP + "#c-cauta", timeout=10000)
            except Exception:   # noqa: BLE001 — luna ceasului (noiembrie) n-are operațiuni de casă pe F1: luna dinainte (octombrie)
                try:
                    pg.click(TOP + "#c-prev", timeout=10000)
                    pg.wait_for_selector(TOP + "#c-cauta", timeout=20000)
                except Exception:   # noqa: BLE001
                    pass
            pg.wait_for_timeout(1000)
            masuri.append(("Casă", pg.evaluate(JS_CAUTARE, "#c-cauta")))
        else:
            masuri.append(("Casă", None))
        if _card(pg, parcurs, F1, "#fa-banca"):
            try:
                pg.wait_for_selector(TOP + "#bk-cauta", timeout=30000)
            except Exception:   # noqa: BLE001
                pass
            pg.wait_for_timeout(1000)
            masuri.append(("Bancă", pg.evaluate(JS_CAUTARE, "#bk-cauta")))
        else:
            masuri.append(("Bancă", None))
        if _card(pg, parcurs, F1, "#fa-jurnal"):
            try:
                pg.wait_for_selector(TOP + "#jn-cauta", timeout=20000)
            except Exception:   # noqa: BLE001
                try:
                    pg.click(TOP + "#j-prev", timeout=10000)
                    pg.wait_for_selector(TOP + "#jn-cauta", timeout=20000)
                except Exception:   # noqa: BLE001
                    pass
            pg.wait_for_timeout(1000)
            masuri.append(("Registru jurnal", pg.evaluate(JS_CAUTARE, "#jn-cauta")))
        else:
            masuri.append(("Registru jurnal", None))
        masuri.append(("De validat", pg.evaluate(JS_CAUTARE, "#val-cauta") if _de_validat(pg) else None))
        for nume, m in masuri:
            if not m or not m["vizibil"]:
                rele.append("(3) %s: câmpul de căutare lipsește sau nu se vede" % nume)
            elif not m["placeholder"].strip():
                rele.append("(3) %s: câmpul de căutare n-are text de îndrumare" % nume)
            elif m["text"] > m["camp"]:
                rele.append("(3) %s: textul de îndrumare «%s» are %d px, câmpul %.0f px" % (nume, m["placeholder"], m["text"], m["camp"]))
        # (4) G4 — stările goale (page.route: coadă goală, nicio ciornă)
        p4 = b.new_page()
        p4.route(URL_COADA, _json_route({"coada": []}))
        p4.route(URL_CIORNE, _json_route({"total": 0, "firme": []}))
        try:
            if not _de_validat(p4):
                rele.append("(4) fereastra De validat nu s-a deschis")
            else:
                for zona, asteptat in (("#val-note", GOL_NOTE), ("#val-ciorne", GOL_CIORNE)):
                    g = p4.locator(TOP + zona + " .stare-goala:visible")
                    txt = _norm(g.first.inner_text()) if g.count() else ""
                    if txt != asteptat:
                        rele.append("(4) %s: starea goală e «%s», nu «%s»" % (zona, txt, asteptat))
        finally:
            p4.close()
        # (5) G5 — rândul F1 din Control fiscal
        try:
            _acasa(pg)
            pg.click("button.cab-card:has([data-cheie='control'])", timeout=10000)
            pg.wait_for_selector(TOP + "#cf-lista tbody tr", timeout=60000)
            pg.wait_for_timeout(1500)
            r = pg.locator(TOP + "#cf-lista tbody tr", has_text=F1)
            if not r.count():
                rele.append("(5) rândul %s lipsește din Control fiscal" % F1)
            else:
                t = _norm(r.first.inner_text())
                if "Diferențe stocuri — nu se poate verifica" not in t:
                    rele.append("(5) rândul F1 nu conține «Diferențe stocuri — nu se poate verifica»: «%s»" % t[:200])
                if "nu se poate verifica:" in t:
                    rele.append("(5) rândul F1 conține încă «nu se poate verifica:»: «%s»" % t[:200])
        except Exception as e:   # noqa: BLE001
            rele.append("(5) Control fiscal nu s-a deschis: %s" % str(e)[:100])
    finally:
        b.close()
    assert not rele, "De validat și Control fiscal 17.5-G: %s" % "; ".join(rele)
