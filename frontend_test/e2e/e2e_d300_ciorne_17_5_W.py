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

from conftest import BAZA, alege_perioada, alege_tipul, sesiune, sql

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
    alege_tipul(pg, tip, zona=TOP)
    alege_perioada(pg, 2026, luna=10, zona=TOP)
    pg.click(TOP + "#dec-continua", timeout=10000)
    pg.wait_for_selector(TOP + "#dec-trimite, " + TOP + ".dec-eroare", state="attached", timeout=120000)
    pg.wait_for_timeout(2500)   # eticheta butonului vine după două cereri, apoi butoanele notelor
    if pg.locator(TOP + ".dec-eroare").count() and not pg.locator(TOP + "#dec-trimite").count():
        return True, _norm(pg.inner_text(TOP + ".dec-eroare"))[:300]
    return False, ""


def _verifica_pasul_2(rele, pg, tip, prima, cu_note):
    """Aserțiunile AC184 pe pasul 2 deschis al lui `tip` (D300: prima = id-ul de început e.1, cu butoanele notelor; D394: e.7); avertismentul lipsă din decont trebuie să fie PRIMUL din casetă, la ambele."""
    nume = tip.upper()
    rezultat = pg.locator(TOP + "#dec-rezultat")
    # Închidere de tip DS: în prima vedere rămâne sumarul. Citește și martorii
    # înainte și după deschiderea detaliilor, păstrând toate ID-urile și sumele.
    rezumat = _norm(rezultat.inner_text())
    if not rezumat:
        rele.append("AC184 / e.%d: lipsește sumarul %s" % (prima,nume))
    for buton in rezultat.locator("details:not([open]) > summary:visible").all():
        if re.search(r"detalii|avertis|rapoarte|documente",buton.inner_text(),re.I):
            buton.click()
    for buton in rezultat.get_by_role("button",name=re.compile(r"detalii",re.I)).all():
        if buton.is_visible() and buton.get_attribute("aria-expanded")=="false":
            buton.click()
    toate = _norm(rezultat.inner_text())
    for doc, data, sume in ((Z42,"20.10.2026",("10,90","21,00")), (Z43,"21.10.2026",("21,00",))):
        if not (doc in toate and data in toate and all(x in toate for x in sume)):
            rele.append("AC184 / e.%d: documentul, data sau TVA pe cotă lipsesc pentru %s" %(prima,doc))
    if "52,90" not in toate or "42,00" not in toate or "10,90" not in toate:
        rele.append("AC184 / e.%d: totalul și descompunerea TVA lipsă pentru rapoartele Z" % (prima+1))
    if not pg.locator(TOP + "#dec-trimite").count():
        rele.append("AC184 / e.%d: pasul 2 al lui %s nu are butonul #dec-trimite" % (prima + 2, nume))
        return
    if not pg.is_disabled(TOP + "#dec-trimite"):
        rele.append("AC184 / e.%d: «%s» e activ pe %s 10/2026, deși din decont lipsește TVA din 2 rapoarte Z în ciornă (52,90 lei)" % (prima + 2, T_ETICHETA, nume))
    eticheta = _norm(pg.inner_text(TOP + "#dec-trimite"))
    if T_ETICHETA not in eticheta:
        rele.append("AC184 / e.%d: butonul de pe %s are eticheta %r (așteptat «%s», și inactiv)" % (prima + 3, nume, eticheta, T_ETICHETA))
    blocaj = _norm(pg.inner_text(TOP + "#dec-blocaj")) if pg.locator(TOP + "#dec-blocaj").count() else ""
    if not blocaj or not re.search(r"valid|ciorn|depun|depus",blocaj,re.I):
        rele.append("AC184 / e.%d: lângă buton, pe %s, nu e motivul inactivității (așteptat «%s»); găsit: %r" % (prima + 4, nume, T_BLOCAJ, blocaj[:300]))
    # [corecția 1, 11.11.2026] butonul principal stă în bara de jos a ferestrei (cadru.js îl mută acolo), motivul rămâne în fereastră: legătura e aria-describedby, iar motivul se vede
    elif not pg.evaluate("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #dec-trimite'), m = document.querySelector('.fereastra-overlay:not(.fundal) #dec-blocaj');"
                         " if (!b || !m) return false; const r = m.getBoundingClientRect();"
                         " return (b.getAttribute('aria-describedby') || '').split(/\\s+/).includes('dec-blocaj') && r.width > 0 && r.height > 0 && getComputedStyle(m).visibility !== 'hidden'; }"):
        rele.append("AC184 / e.%d: pe %s butonul inactiv nu e legat de motiv (aria-describedby=\"dec-blocaj\") sau motivul nu se vede în fereastră" % (prima + 4, nume))
    if cu_note:
        butoane = [_norm(t) for t in pg.eval_on_selector_all(TOP + "#dec-blocaj button", "els => els.map(e => e.innerText)")]
        if not all(any(z in b and total in b for b in butoane) for z,total in ((Z42,"31,90"),(Z43,"21,00"))):
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
    from xml.etree import ElementTree
    from hashlib import sha256
    from pathlib import Path
    import csv
    import json
    root = Path(RAD) / "docs/dovezi/17_5_Q9"
    reper = json.loads((root / "repere_D300_Q7.json").read_text())
    assert reper["schema"] == SCHEMA and reper["perioada"] == "2026-10"
    def sursa(nume, amprenta):
        fisier = root / reper[nume]
        assert sha256(fisier.read_bytes()).hexdigest() == reper[amprenta], fisier.name
        with fisier.open(encoding="utf-8-sig", newline="") as flux:
            return list(csv.DictReader(flux, delimiter="\t"))
    documente = sursa("extras_independent", "sha256_documente")
    detalii = sursa("detalii", "sha256_detalii")
    assert len(documente) == len(detalii) == 20
    for doc, det in zip(documente, detalii, strict=True):
        assert doc["document"].startswith(det["document"] + " din ") and doc["localizare"].strip()
        assert all(doc[c] == det[c] for c in ("tip", "cota", "inclus", "tva"))
    assert any(d["document"] == "F1A nr. 13" and d["inclus"] == "0" and d["tip"] == "factura_pe_bon" for d in detalii)
    def total(cota, fara_de=False):
        pozitii = [d for d in detalii if d["inclus"] == "1" and d["cota"] == cota
                   and not (fara_de and d["document"] == "F1A nr. 17")]
        return tuple(str(sum((Decimal(d[c]) for d in pozitii), Decimal(0)).quantize(Decimal(1), rounding=ROUND_HALF_UP))
                     for c in ("baza", "tva"))
    def numeste_de(text):
        return bool(re.search(r"\bF1A\s*(?:nr\.?\s*)?0*17\b", text, re.I))
    def explica_de(text):
        return numeste_de(text) and bool(re.search(r"\b(TVA|(?-i:DE)|Germania|21)\b|cot[ăa]|țar[aă]|partener", text, re.I))
    valori = ElementTree.fromstring(xml).attrib if xml else {}
    pereche9 = (valori.get("R9_1"), valori.get("R9_2"))
    pereche10 = (valori.get("R10_1"), valori.get("R10_2"))
    exclus_de = pereche9 == total("21", True)
    semnalari = (js or {}).get("avertismente") or []
    motiv = str((js or {}).get("blocaj_depunere") or "")
    if (pereche10 != total("11") or not exclus_de
            or not any(explica_de(str(avert)) for avert in semnalari)
            or not explica_de(motiv)):
        rele.append("AC184 / e.12: R9/R10 sau tratamentul nominal al F1A 17 diferă de documentele snapshotului.")
    if st == 200 and not (js or {}).get("blocaj_depunere"):
        rele.append("AC184 / e.13: răspunsul rutei /declaratii/d300/valideaza pe 10/2026 nu are blocaj_depunere (așteptat refuzul cu motivul rapoartelor Z în ciornă)")
    # cererea directă de intrare în coadă e refuzată cu același motiv și nu lasă nimic în coadă
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    st2, js2 = _api(pg, "/coada", "POST", {"tenant_id": tid, "an": 2026, "luna": 10, "tip": "d300"})
    if st2 != 422 or not (js or {}).get("blocaj_depunere") or _norm(str(js["blocaj_depunere"])) not in _norm(str(js2)):
        rele.append("AC184 / e.14: POST /coada pentru D300 pe 10/2026 a primit status %s (așteptat 422 cu «Declarația nu se depune până la validarea rapoartelor Z»): %s" % (st2, str(js2)[:300]))
    if exclus_de and (st2 != 422 or not numeste_de(str(js2))):
        rele.append("AC184 / e.12: refuzul cozii nu identifică factura F1A 17 exclusă.")
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
        # [17.5-T] actualizat la 484 (decizia 17.5-X, P4: fără note în ciornă, prima propoziție e «Diferență neexplicată: X lei.»; frontend_test/e2e/e2e_d300_ciorne_17_5_W.py:196)
        dif = re.search(r"diferență ([\d.]+,\d{2}) lei", rand[0])   # diferența din rândul comparației, în formatul aplicației
        asteptat = ("Note în ciornă pe contul %s în perioadă: %d, cu suma de %s lei." % (cont, n, ro_bani(suma))) if n else (
            "Diferență neexplicată: %s lei." % (dif.group(1) if dif else "?"))
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
