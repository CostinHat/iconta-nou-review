# -*- coding: utf-8 -*-
"""DECONTUL CARE SPUNE CE ÎI LIPSEȘTE — lotul 17.5-W (AC184, AC185, AC186 din auditul complet; decizii_17_5_W.txt și «De ce» din comanda_17_5_W.txt).
Scris de arhitect; Code nu îl modifică. Probă pe bază: pică; pe C: trece.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe F1 Comert Stoc (tenant_9049), baza de test restaurată din snapshot. Fiecare mesaj de eșec începe cu numărul AC
(și cu un id e.1–e.20 propriu testului, distinct de ids din oracolul pasi_17_5_W), urmat de martorul de pe snapshot:
  1. AC184: Declarații › D300 pe 10/2026 › pasul 2: caseta «Avertismente» numește rapoartele Z în ciornă omise (număr, dată, TVA pe cotă) și totalul TVA lipsă; «Pune în „De depus” →» e inactiv, cu motivul lângă el
     și cu un buton «Deschide nota …» pentru fiecare raport; cererea directă POST /coada e refuzată cu același motiv și nu lasă nimic în coadă; regula de calcul rămâne (numai Z validat: R9_2 = 1873, R10_2 = 99 în XML);
  2. AC184: la fel pe D394 pe 10/2026;
  3. AC185: Control fiscal › «Declarație vs contabilitate»: pe rândul fiecărui cont comparat în diferență (4427, 4426, 4423) se spune câte note în ciornă îl ating în perioada comparată și suma lor; numerele vin din
     baza de test pe luna pe care o arată ecranul (luna comparată vine din data serverului, nu din ceasul înghețat al browserului);
  4. AC186: martorii lămuririi (F1A13 id 64 nu are notă; R10_2 = 99 în XML; Z-0050 validat intră în decont) — pasesc și pe bază, și pe C: lămurirea o face Code cu un test propriu (comanda, pct.2); lotul nu repară nimic aici.
Scrie în baza de date numai dacă defectul AC184 există (cererea POST /coada primită): rândul rămas în coadă se șterge la sfârșit; baza se restaurează înainte de grupul următor (comanda, pct.8). Un singur test."""
import importlib.util
from decimal import Decimal, ROUND_HALF_UP
import base64
import os
import re
import sys

from conftest import BAZA, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
SCHEMA = "tenant_9049"
TOP = ".fereastra-overlay:not(.fundal) "

Z42, Z43 = "Z-8000000001-0042", "Z-8000000001-0043"
T_AVERT_1 = ("Din decont lipsește TVA din rapoarte Z în ciornă: 2 rapoarte Z nevalidate nu intră în calcul până la validare — "
             "%s din 20.10.2026 (TVA 11%%: 10,90 lei; TVA 21%%: 21,00 lei); %s din 21.10.2026 (TVA 21%%: 21,00 lei)." % (Z42, Z43))
T_AVERT_2 = "TVA colectată lipsă din decont: 52,90 lei (11%: 10,90 lei; 21%: 42,00 lei)."
T_BLOCAJ = ("Declarația nu se depune până la validarea rapoartelor Z: din decont lipsește TVA din 2 rapoarte Z în ciornă, în total 52,90 lei. "
            "Validează-le în Registrul jurnal, apoi generează din nou.")
T_BUTOANE_NOTE = ["Deschide nota din 20.10.2026 — %s, TVA 31,90 lei" % Z42, "Deschide nota din 21.10.2026 — %s, TVA 21,00 lei" % Z43]
T_ETICHETA = "Pune în „De depus” →"


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def ro_bani(v):
    """Formatul sumelor aplicației: punct la mii, virgulă la zecimale, două zecimale (ca bani() din static/js/api.js)."""
    n = Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return "{:,.2f}".format(n).replace(",", "§").replace(".", ",").replace("§", ".")


def _norm(t):
    return " ".join(str(t or "").split())


def _api(pg, cale, metoda="GET", corp=None):
    """Cerere către server cu sesiunea paginii; -> (status, json)."""
    return pg.evaluate("""async ([c, m, b]) => { const t = sessionStorage.getItem('iconta_token');
      const r = await fetch(c, { method: m, headers: Object.assign({ 'Authorization': 'Bearer ' + t }, b ? { 'Content-Type': 'application/json' } : {}), body: b ? JSON.stringify(b) : undefined });
      let j = null; try { j = await r.json(); } catch (e) {} return [r.status, j]; }""", [cale, metoda, corp])


def _sectiune(rele, nume, fn, *argumente):
    """O secțiune care aruncă excepție nu oprește celelalte: eșecul ei intră în listă."""
    try:
        fn(rele, *argumente)
    except Exception as e:   # noqa: BLE001
        rele.append("%s: secțiunea a căzut (%s: %s)" % (nume, type(e).__name__, str(e)[:200]))


def _card(pg, parcurs, firma, sel, asteapta=None):
    parcurs.firma(pg, firma)
    pg.evaluate("""(sel) => { const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return;
      const cont = c.closest('.firme-optiuni'); if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); } }""", sel)
    pg.click(TOP + sel, timeout=10000)
    if asteapta:
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    pg.wait_for_timeout(1500)


def _pasul_2(pg, parcurs, tip):
    """Declarații F1 › `tip` pe 10/2026 › «Continuă» › pasul 2; -> (arata_eroare, text_eroare)."""
    _card(pg, parcurs, F1, "#fa-declaratii", "#dec-tip")
    optiune = TOP + "#dec-tip option[value='%s']" % tip
    if not pg.locator(optiune).count() and pg.locator(TOP + "#dec-alte").count():
        if pg.get_attribute(TOP + "#dec-alte", "aria-expanded") != "true":
            pg.click(TOP + "#dec-alte", timeout=10000)
        pg.wait_for_selector(optiune, state="attached", timeout=10000)
    pg.select_option(TOP + "#dec-tip", tip)
    pg.fill(TOP + "#dec-an", "2026")
    pg.dispatch_event(TOP + "#dec-an", "change")
    if pg.locator(TOP + "#dec-luna").count():
        pg.select_option(TOP + "#dec-luna", "10")
    pg.click(TOP + "#dec-continua", timeout=10000)
    pg.wait_for_selector(TOP + "#dec-trimite, " + TOP + ".dec-eroare", state="attached", timeout=120000)
    pg.wait_for_timeout(2500)   # eticheta butonului vine după două cereri, apoi butoanele notelor
    if pg.locator(TOP + ".dec-eroare").count() and not pg.locator(TOP + "#dec-trimite").count():
        return True, _norm(pg.inner_text(TOP + ".dec-eroare"))[:300]
    return False, ""


def _verifica_pasul_2(rele, pg, tip, prima, cu_note):
    """Aserțiunile AC184 pe pasul 2 deschis al lui `tip` (D300: prima = id-ul de început e.1, cu butoanele notelor; D394: e.7); avertismentul lipsă din decont trebuie să fie PRIMUL din casetă, la ambele."""
    nume = tip.upper()
    avert = [_norm(t) for t in pg.eval_on_selector_all(TOP + "#dec-rezultat .dec-avert li", "els => els.map(e => e.textContent)")]
    toate = " || ".join(avert)
    if not avert or not avert[0].startswith(T_AVERT_1):
        rele.append("AC184 / e.%d: caseta «Avertismente» a lui %s pe 10/2026 nu are ca PRIM avertisment pe cel care numește rapoartele Z în ciornă omise (așteptat: «%s»); avertismentele de azi (%d): %s"
                    % (prima, nume, T_AVERT_1, len(avert), toate[:400]))
    if T_AVERT_2 not in toate:
        rele.append("AC184 / e.%d: %s pe 10/2026 nu spune totalul TVA lipsă din decont (așteptat: «%s»); avertismentele de azi (%d): %s"
                    % (prima + 1, nume, T_AVERT_2, len(avert), toate[:400]))
    if not pg.locator(TOP + "#dec-trimite").count():
        rele.append("AC184 / e.%d: pasul 2 al lui %s nu are butonul #dec-trimite" % (prima + 2, nume))
        return
    if not pg.is_disabled(TOP + "#dec-trimite"):
        rele.append("AC184 / e.%d: «%s» e activ pe %s 10/2026, deși din decont lipsește TVA din 2 rapoarte Z în ciornă (52,90 lei)" % (prima + 2, T_ETICHETA, nume))
    eticheta = _norm(pg.inner_text(TOP + "#dec-trimite"))
    if T_ETICHETA not in eticheta:
        rele.append("AC184 / e.%d: butonul de pe %s are eticheta %r (așteptat «%s», și inactiv)" % (prima + 3, nume, eticheta, T_ETICHETA))
    blocaj = _norm(pg.inner_text(TOP + "#dec-blocaj")) if pg.locator(TOP + "#dec-blocaj").count() else ""
    if T_BLOCAJ not in blocaj:
        rele.append("AC184 / e.%d: lângă buton, pe %s, nu e motivul inactivității (așteptat «%s»); găsit: %r" % (prima + 4, nume, T_BLOCAJ, blocaj[:300]))
    elif not pg.evaluate("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #dec-trimite'), m = document.querySelector('.fereastra-overlay:not(.fundal) #dec-blocaj');"
                         " return !!(b && m && b.closest('.bara-fixa') && b.closest('.bara-fixa').contains(m)); }"):
        rele.append("AC184 / e.%d: motivul inactivității de pe %s nu stă în aceeași bară fixă cu butonul" % (prima + 4, nume))
    if cu_note:
        butoane = [_norm(t) for t in pg.eval_on_selector_all(TOP + "#dec-blocaj button", "els => els.map(e => e.innerText)")]
        if butoane != T_BUTOANE_NOTE:
            rele.append("AC184 / e.%d: butoanele spre notele rapoartelor Z din %s sunt %s (așteptat %s)" % (prima + 5, nume, butoane, T_BUTOANE_NOTE))


def _d300(rele, pg, parcurs):
    eroare, text = _pasul_2(pg, parcurs, "d300")
    if eroare:
        rele.append("AC184 / e.1: pasul 2 al lui D300 pe 10/2026 s-a oprit la o eroare (testul nu poate judeca): %s" % text)
        return
    _verifica_pasul_2(rele, pg, "d300", 1, True)


def _d394(rele, pg, parcurs):
    eroare, text = _pasul_2(pg, parcurs, "d394")
    if eroare:
        rele.append("AC184 / e.7: pasul 2 al lui D394 pe 10/2026 s-a oprit la o eroare (testul nu poate judeca): %s" % text)
        return
    _verifica_pasul_2(rele, pg, "d394", 7, False)


def _coada_si_calcul(rele, pg):
    tid = sql("SELECT id FROM public.tenants WHERE schema_name = %s", (SCHEMA,))[0][0]
    # regula de calcul rămâne: numai Z validat intră în decont (R9_2 = 1873 și R10_2 = 99 pe snapshot: Z-0050 validat, Z-0042 și Z-0043 în ciornă)
    st, js = _api(pg, "/declaratii/d300/valideaza", "POST", {"tenant_id": tid, "an": 2026, "luna": 10})
    xml = base64.b64decode(js["xml_b64"]).decode("utf-8") if st == 200 and js and js.get("xml_b64") else ""
    if 'R9_2="1873"' not in xml or 'R10_2="99"' not in xml:
        rele.append("AC184 / e.12: calculul D300 pe 10/2026 s-a schimbat (așteptat R9_2=1873 și R10_2=99: numai Z validat intră în decont); status %s, XML: %s" % (st, xml[-300:] if xml else js))
    if st == 200 and not (js or {}).get("blocaj_depunere"):
        rele.append("AC184 / e.13: răspunsul rutei /declaratii/d300/valideaza pe 10/2026 nu are blocaj_depunere (așteptat refuzul cu motivul rapoartelor Z în ciornă)")
    # cererea directă de intrare în coadă e refuzată cu același motiv și nu lasă nimic în coadă
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    st2, js2 = _api(pg, "/coada", "POST", {"tenant_id": tid, "an": 2026, "luna": 10, "tip": "d300"})
    if st2 != 422 or "Declarația nu se depune până la validarea rapoartelor Z" not in str(js2):
        rele.append("AC184 / e.14: POST /coada pentru D300 pe 10/2026 a primit status %s (așteptat 422 cu «Declarația nu se depune până la validarea rapoartelor Z»): %s" % (st2, str(js2)[:300]))
    ramase = sql("SELECT count(*) FROM public.declaratii_coada WHERE id > %s AND tenant_id = %s", (peste, tid))[0][0]
    if ramase:
        rele.append("AC184 / e.14: cererea POST /coada a lăsat %d rând(uri) în coadă pentru F1 (decontul cu TVA lipsă a intrat în «De depus»)" % ramase)
        try:
            sql("DELETE FROM public.declaratii_coada WHERE id > %s AND tenant_id = %s", (peste, tid))
        except Exception:   # noqa: BLE001 — curățenia e un bonus: baza se restaurează oricum înainte de grupul următor
            pass


def _control(rele, pg, parcurs):
    _card(pg, parcurs, F1, "#fa-control", "#cf-incrucisat")
    pg.wait_for_timeout(2500)
    perioada = _norm(pg.inner_text(TOP + "#cf-perioade")) if pg.locator(TOP + "#cf-perioade").count() else ""
    m = re.search(r"D300 (\d{2})/(\d{4})", perioada)
    if not m:
        rele.append("AC185 / e.15: Control fiscal F1 nu arată «Perioada comparată: D300 LL/AAAA» (testul nu poate judeca): %r" % perioada)
        return
    luna, an = int(m.group(1)), int(m.group(2))
    de = "%04d-%02d-01" % (an, luna)
    pana = "%04d-%02d-01" % (an + 1, 1) if luna == 12 else "%04d-%02d-01" % (an, luna + 1)
    randuri = [_norm(t) for t in pg.eval_on_selector_all(TOP + "#cf-incrucisat .ds-semnal:not(.ds-semnal-info) .ds-semnal-text", "els => els.map(e => e.textContent)")]
    vizibile = " || ".join(_norm(t) for t in pg.eval_on_selector_all(TOP + "#cf-incrucisat .ds-semnal-text", "els => els.map(e => e.textContent)"))   # numai textul vizibil al rândurilor (prima propoziție), nu detaliile pliate
    for i, (cont, coloana) in enumerate((("4427", "cont_credit"), ("4426", "cont_debit"), ("4423", "cont_credit")), start=16):
        rand = [r for r in randuri if "contul %s" % cont in r]
        if not rand or "diferență" not in rand[0]:
            continue   # contul nu are comparație în diferență pe luna aceasta (coincide sau nu se compară): nimic de explicat
        n, suma = sql("SELECT count(DISTINCT i.id), COALESCE(sum(l.suma), 0) FROM %s.inregistrari_linii l JOIN %s.inregistrari i ON i.id = l.inregistrare_id "
                      "WHERE i.status <> 'validata' AND i.data >= %%s AND i.data < %%s AND l.%s = %%s" % (SCHEMA, SCHEMA, coloana), (de, pana, cont))[0]
        asteptat = ("Note în ciornă pe contul %s în perioadă: %d, cu suma de %s lei." % (cont, n, ro_bani(suma))) if n else (
            "Note în ciornă pe contul %s în perioadă: niciuna." % cont)
        if asteptat not in vizibile:
            rele.append("AC185 / e.%d: sub rândul comparației cu contul %s (luna %02d/%d) nu e rândul vizibil care explică diferența prin notele în ciornă (așteptat «%s»); rândul comparației: %r"
                        % (i, cont, luna, an, asteptat, rand[0][:300]))


def _martori_ac186(rele, pg):
    # AC186: martorii lămuririi, adevărați și pe bază, și pe C (lotul nu repară nimic aici; lămurirea e a lui Code, în raport)
    note_f1a13 = sql("SELECT count(*) FROM %s.inregistrari WHERE factura_id = 64" % SCHEMA)[0][0]
    if note_f1a13 != 0:
        rele.append("AC186 / e.19: factura F1A13 (id 64, emisă pe baza bonului fiscal 0002) are acum %d note (martorul a fost: nicio notă)" % note_f1a13)
    z50 = sql("SELECT status FROM %s.inregistrari WHERE numar = 'Z-8000000001-0050'" % SCHEMA)
    if not z50 or z50[0][0] != "validata":
        rele.append("AC186 / e.20: Z-8000000001-0050 nu mai e validat pe snapshot (martorul: validat, 11%% TVA 10,90 și 21%% TVA 42,00): %s" % z50)


def test_decont_ciorne_17_5_W(browser):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _sectiune(rele, "D300 pasul 2 (AC184)", _d300, pg, parcurs)
        _sectiune(rele, "D394 pasul 2 (AC184)", _d394, pg, parcurs)
        _sectiune(rele, "Calculul și coada (AC184)", _coada_si_calcul, pg)
        _sectiune(rele, "Control fiscal (AC185)", _control, pg, parcurs)
        _sectiune(rele, "Martorii lămuririi (AC186)", _martori_ac186, pg)
    finally:
        b.close()
    assert not rele, "decontul 17.5-W: " + "; ".join(rele)
