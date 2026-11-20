# -*- coding: utf-8 -*-
"""FERESTRELE FIRMEI F1 ȘI IMPORT SALARIAȚI F5, CU CONTOARE, FORMATE ȘI ACȚIUNI CARE SPUN ADEVĂRUL — lotul 17.5-N (AC041, AC050, AC058, AC060, AC061, AC077, AC117, AC118 din auditul
complet; decizii_17_5_N.txt și «De ce» din comanda_17_5_N.txt). Probă GPT-6. Contractul pe bază cere a.6 și a.7 roșii măsurate. Pe C se cere acceptarea integrală.

La 1366×768, ceas înghețat 03.11.2026, cu contul administratorului (dovada.71507), pe F1 Comert Stoc (tenant_9049) și F5 SRL Salariati. Fiecare mesaj de eșec începe cu id-ul aserțiunii din oracolul
pasi_17_5_N (a.1–a.7) sau cu numărul AC (AC117, AC118, care n-au aserțiune în oracol: oracolul nu poate alege un fișier, limita de la pct.6 al comenzii), urmat de martorul de pe snapshot:
  1. a.2 / a.3 (AC058): Verificări F1, rândul de sus spune «Luna 10/2026 · 32 de note validate în lună» (nu totalul cumulat al liniilor); luna 11/2026: «0 note validate în lună» (ciornele nu se numără); răspunsul
     rutei păstrează cheia veche `note` și are cheia nouă `note_luna` (32, respectiv 0, ca în baza de test); fără `note_luna` în răspuns, după «Luna …» nu se scrie niciun număr;
  2. a.5 (AC060): rândul Stocuri spune «cont <cod>: contabil <x> lei · fișe de magazie <y> lei» pe fiecare cont din răspunsul rutei verificare-stocuri (cifrele lui, nu cifre fixate aici), «(diferență <d> lei)»
     numai pe contul cu ok fals și nota serverului, cuvânt cu cuvânt, numai când ok e fals; fără conturi rămâne «în regulă»;
  3. a.4 (AC061): rândul Intrastat scrie «Introduceri: <x> lei (<p>)» și «Expedieri: <x> lei (<p>)» cu formatul aplicației (martor: «Expedieri: 3.000,00 lei (0,3%)», facturile 51, 52, 53 și 66, IE6388047V);
  4. a.1 (AC077): Scadențar F1, rândul de pastile are a patra pastilă «2 fără scadență în sistem» (facturile 66 și 71), mereu afișată (și «0 …»), iar cele patru contoare însumează toate rândurile listei;
  5. a.6 (AC050): Cartea mare F1, fiecare opțiune a listei de conturi e «<simbol> · <denumire>» din plan_conturi («371 · Mărfuri»), cont fără denumire = simbolul singur, prima opțiune «— alege contul —»;
     răspunsul rutei fisa-cont păstrează `conturi`, `fisa`, `formular` și are `denumiri`; fără `denumiri` în răspuns, opțiunile sunt numai simbolurile;
  6. a.7 (AC041): e-Transport F1 (acoperire SPV «neconectat»): «Trimite UIT în SPV» inactiv prin aria-disabled, cu motivul în title și scris în fereastră (#et-motiv-spv, în bara de jos), «Doar generează XML (manual)»
     singurul buton principal, motivul rămâne după updateFereastra; la «neacoperit» (și la lipsa câmpului cu conectat fals) la fel; la «acoperit», «neverificat», «neconfirmat» și la starea ilizibilă nimic nu se schimbă;
  7. AC117: modelul CSV al salariaților (#mig-model, F5): «Contabil» cu COR 331302, «Ospătar» cu COR 513102 (public.cor_ocupatii: «contabil», «ospătar (chelner)»), nicio altă valoare schimbată;
  8. AC118: previzualizarea salariaților (modelul descărcat, încărcat în F5) are la sfârșit coloanele «Județ» și «IBAN»: rândul Popescu Ana «B» și «RO49 AAAA 1B31 0075 9384 0000», rândul fără IBAN «—»;
     cererea de salvare (oprită în browser, nimic nu se salvează) poartă IBAN-ul din fișier, fără spații.
Nu salvează nimic. Singurul fișier ales e modelul descărcat de aplicație, doar pentru previzualizare. Un singur test."""
import csv
import importlib.util
import io
import json
import os
import re
import sys

from conftest import BAZA, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F5 = "F5 SRL Salariati"
SCHEMA = "tenant_9049"
TOP = ".fereastra-overlay:not(.fundal) "
FER = TOP + ".fereastra"
MOTIV_SPV = "Firma nu are drept SPV, deci UIT-ul nu poate fi trimis de aici. Generează XML-ul și încarcă-l manual în SPV."
NOTA_STOCURI = "Diferențele pot veni din note ciornă nevalidate sau din operațiuni în afara fișelor de magazie."
IBAN_MODEL = "RO49AAAA1B31007593840000"
IBAN_MODEL_GRUPAT = "RO49 AAAA 1B31 0075 9384 0000"
COLOANE_MODEL = ["nume", "prenume", "cnp", "data angajare", "functie", "norma", "ore", "functie de baza", "scutit contributie minima",
                 "persoane in intretinere", "brut", "judet", "cor", "iban"]
# modelul de azi (static/js/ecrane/migrare.js, MODELE.salariati) cu singurele două schimbări ale lotului: COR 331302 la «Contabil» și 513102 la «Ospătar»
RANDURI_MODEL = [["Popescu", "Ana", "2900215410011", "2020-01-15", "Contabil", "intreaga", "8", "da", "nu", "0", "5000", "B", "331302", IBAN_MODEL],
                 ["Ionescu", "Radu", "1850715410012", "2021-03-01", "Ospătar", "partiala", "4", "da", "nu", "1", "6000", "CJ", "513102", ""]]
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
# butoanele e-Transport și motivul, citite din fereastra de sus: starea aria-disabled, title, clasele, butonul (butoanele) principal(e) al ferestrei, motivul și locul lui (bara de jos = .fj-motiv, cadru.js)
JS_ET = r"""() => {
  const windows = document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra');
  const f = windows.length === 1 ? windows[0] : null;
  const all = (selector) => f ? Array.from(f.querySelectorAll(selector)) : [];
  const one = (selector) => {
    const nodes = all(selector);
    return nodes.length === 1 ? nodes[0] : null;
  };
  const text = (e) => e ? e.textContent.replace(/\s+/g, ' ').trim() : '';
  const button = (e) => e && ({aria:e.getAttribute('aria-disabled'), title:e.title || '',
                               clasa:e.className, text:text(e)});
  const t = one('#et-trimite');
  const g = one('#et-genereaza');
  const m = one('#et-motiv-spv');
  const foot = one('.fereastra-jos');
  const primary = one('.fereastra-jos .fj-butoane .fj-principal');
  function rect(e) {
    if (!e) return null;
    const {left, top, right, bottom} = e.getBoundingClientRect();
    return {left, top, right, bottom};
  }
  function visible(e) {
    if (!e || !e.checkVisibility({checkOpacity:true, checkVisibilityCSS:true})) return false;
    const r = rect(e);
    if (r.left < -1 || r.top < -1 || r.right > innerWidth+1 || r.bottom > innerHeight+1 ||
        r.bottom <= r.top || r.right <= r.left) return false;
    for (let node=e.parentElement; node; node=node.parentElement) {
      const style=getComputedStyle(node), a=rect(node);
      if (style.overflowX !== 'visible' && (r.left < a.left-1 || r.right > a.right+1)) return false;
      if (style.overflowY !== 'visible' && (r.top < a.top-1 || r.bottom > a.bottom+1)) return false;
    }
    return true;
  }
  const overlap = (a,b) => a && b && Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 &&
                                       Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1;
  function gap(a,b) {
    const x = Math.max(0, a.left-b.right, b.left-a.right);
    const y = Math.max(0, a.top-b.bottom, b.top-a.bottom);
    return Math.hypot(x,y);
  }
  const neighbors = foot ? [...foot.querySelectorAll('button,[role="button"]')].filter(visible) : [];
  return {
    trimite:button(t), genereaza:button(g),
    principale:all('[data-actiune-principala]').map(e => e.id || text(e)),
    n_motiv:all('#et-motiv-spv').length,
    motiv:m && {text:text(m), clasa:m.className, vizibil:visible(m), in_bara:!!m.closest('.fj-motiv')},
    bara: {
      aceeasi:!!foot && [t,m,primary].every(e => e && e.closest('.fereastra-jos')===foot),
      trimite_vizibil:visible(t), motiv_vizibil:visible(m), xml_vizibil:visible(primary),
      vecin:!!m && !!t && neighbors.includes(t) &&
            neighbors.every(e => gap(rect(t),rect(m)) <= gap(rect(e),rect(m))+1),
      separat:!!t && !!m && !!primary && !overlap(rect(t),rect(m)) &&
               !overlap(rect(t),rect(primary)) && !overlap(rect(m),rect(primary)),
      xml_activ:!!primary && primary===g && !primary.matches(':disabled,[aria-disabled="true"]') &&
                text(primary)==='Doar generează XML (manual)' && !!g &&
                !g.matches(':disabled,[aria-disabled="true"]'),
      pozitii:{trimite:rect(t), motiv:rect(m), xml:rect(primary), bara:rect(foot)}
    }
  };
}"""
JS_PASTILE = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .cf-sumar:not(#sc-fisa-sold) .cf-pastila')].map((e) => {
  const d = e.querySelector('.cf-dot'); return [(e.textContent || '').replace(/\\s+/g, ' ').trim(), d ? (d.getAttribute('style') || '') : ''];
})"""
JS_OPTIUNI = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #fc-cont option')].map((o) => [o.value, (o.textContent || '').replace(/\\s+/g, ' ').trim()])"""
JS_ALES = """() => { const s = document.querySelector('.fereastra-overlay:not(.fundal) #fc-cont'); return s && s.selectedOptions[0] ? [s.value, (s.selectedOptions[0].textContent || '').replace(/\\s+/g, ' ').trim()] : null; }"""
JS_CELULE = """(nr) => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .mig-prev tbody tr[data-rand="' + nr + '"]:not(.mig-prev-motive) td')].map((t) => (t.textContent || '').replace(/\\s+/g, ' ').trim())"""
JS_ANTET_PREV = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .mig-prev thead th')].map((t) => (t.textContent || '').replace(/\\s+/g, ' ').trim())"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join((t or "").split()).replace("−", "-")


def _text_brut(pg):
    """textContent al ferestrei de sus (inclusiv ce stă în elemente ascunse sau pliate), spațiile strânse: așa măsoară oracolul pasi_17_5_N cheia dom:…|text."""
    return pg.evaluate("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return e ? (e.textContent || '').replace(/\\s+/g, ' ').replace(/\\u2212/g, '-').trim() : ''; }")


def ro(v):
    """Formatul bani() al aplicației (static/js/api.js): 1.234,56 (două zecimale, punct la mii, virgulă la zecimale)."""
    return "{:,.2f}".format(float(v)).replace(",", "§").replace(".", ",").replace("§", ".")


def ro_pct(v):
    """Formatul pct() al aplicației: întreg + «%», o zecimală cu virgulă când nu e întreg (0,3%)."""
    n = float(v or 0)
    return (str(int(n)) if n == int(n) else ("%.1f" % n).replace(".", ",")) + "%"


def grupe4(iban):
    s = re.sub(r"\s+", "", iban or "")
    return " ".join(s[i:i + 4] for i in range(0, len(s), 4))


def _raspuns(model):
    """Predicat pentru pg.expect_response: GET pe ruta al cărei URL se potrivește cu `model` (regex)."""
    return lambda r: re.search(model, r.url) is not None and r.request.method == "GET"


def _card(pg, parcurs, firma, sel, asteapta=None):
    """Pagina principală › Firme › firma › cardul `sel` din fereastra firmei (grupul lui se deschide dacă e pliat); fals dacă cardul lipsește."""
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(2500)
    return True


def _json_ruta(model, modifica):
    """Handler pentru pg.route: cererea merge la server, iar corpul JSON al răspunsului trece prin `modifica(corp)` (răspuns vechi sau simulat)."""
    def _h(ruta):
        r = ruta.fetch()
        corp = r.json()
        corp = modifica(corp) or corp
        ruta.fulfill(status=r.status, headers={"content-type": "application/json"}, body=json.dumps(corp))
    return re.compile(model), _h


def _simulat(model, corp, status=200):
    """Handler pentru pg.route: răspunsul rutei e `corp`, fără a atinge serverul."""
    return re.compile(model), (lambda ruta: ruta.fulfill(status=status, headers={"content-type": "application/json"}, body=json.dumps(corp)))


_EVALUATE = []   # cazurile simulate Stocuri evaluate (intra in mesajul final: dovada ca toate trei au rulat)


ID_ORACOL = ("f.1", "a.1", "f.2", "a.2", "a.3", "a.4", "a.5", "a.6", "a.7")


def _masoara_a6(rezultate, ales, denumire):
    if not isinstance(ales, list) or len(ales) != 2 or ales[0] != "371":
        return
    eticheta = ales[1]
    if denumire == "Mărfuri" and isinstance(eticheta, str):
        rezultate["a.6"] = eticheta == "371 · Mărfuri"
        print("MASURA a.6 valoare=371 denumire=Mărfuri eticheta=" +
              json.dumps(eticheta, ensure_ascii=False), flush=True)


def _raporteaza(rele, rezultate):
    for id_pas in ID_ORACOL:
        if id_pas not in rezultate:
            rele.append(id_pas + ": pas nemăsurat sau martor indisponibil")
            continue
        trece = rezultate[id_pas]
        print("VERDICT " + id_pas + (" trece" if trece else " pica"), flush=True)
        if not trece:
            rele.append(id_pas + ": criteriul oracolului a picat")


def _pagina_principala(rele, pg, rezultate):
    pg.wait_for_selector(".cab-grila button.cab-card", state="visible", timeout=30000)
    rezultate["f.1"] = "Control fiscal" in pg.locator("main").inner_text()


def _sectiune(rele, nume, fn, *argumente):
    """O secțiune care aruncă excepție nu oprește celelalte: eșecul ei intră în listă."""
    try:
        fn(rele, *argumente)
    except Exception as e:   # noqa: BLE001
        rele.append("%s: secțiunea a căzut cu %s: %s" % (nume, type(e).__name__, str(e).replace("\n", " ")[:240]))


def _segment(text, de_la, pana_la=None):
    """Textul dintre titlul unui rând al Verificărilor și titlul următorului (sau până la capăt)."""
    i = text.find(de_la)
    if i < 0:
        return None
    i += len(de_la)
    j = text.find(pana_la, i) if pana_la else -1
    return text[i:j] if j >= 0 else text[i:]


# ── 1–3. Verificări F1: AC058 (a.2, a.3), AC060 (a.5), AC061 (a.4) ─────────────────────────────────────────────────────────────────────────────────
def _verificari(rele, pg, parcurs, rezultate):
    with pg.expect_response(_raspuns(r"/firme/\d+/verificari\?"), timeout=60000) as rv, \
            pg.expect_response(_raspuns(r"/tenants/\d+/verificare-stocuri"), timeout=60000) as rs, \
            pg.expect_response(_raspuns(r"/tenants/\d+/intrastat-praguri\?"), timeout=60000) as ri:
        if not _card(pg, parcurs, F1, "#fa-verificari", "#vf-prev"):
            rele.append("Verificări F1: cardul «Verificări» nu s-a deschis")
            return
    ver, vs, ip = rv.value.json(), rs.value.json(), ri.value.json()
    t = _text_brut(pg)

    # a.2 / a.3 — AC058: martor F1 (tenant_9049), 10/2026 = 32 note validate, 11/2026 = 0 (5 ciorne)
    if "Luna 10/2026 · 32 de note validate în lună" not in t:
        rele.append("a.2 AC058 (F1, 10/2026 = 32 note validate): rândul de sus nu spune «Luna 10/2026 · 32 de note validate în lună» (text: «%s…»)" % t[:160])
    if "note contabile" in t:
        rele.append("a.3 AC058: ferestra încă spune «note contabile» (numărul cumulat al liniilor)")
    if ver.get("note_luna") != 32:
        rele.append("a.2 AC058: răspunsul /firme/{id}/verificari are note_luna = %r (așteptat 32, martor 10/2026)" % ver.get("note_luna"))
    if "note" not in ver:
        rele.append("AC058: răspunsul rutei a pierdut cheia veche `note` (nu se scoate din rută)")
    elif ver["note"] == ver.get("note_luna"):
        rele.append("AC058: `note` (linii cumulate) = note_luna = %r: proba nu deosebește notele lunii de liniile cumulate" % ver["note"])
    baza = {"validate": sql('SELECT count(*) FROM "%s".inregistrari WHERE status = %%s AND data >= %%s AND data < %%s' % SCHEMA, ("validata", "2026-10-01", "2026-11-01"))[0][0],
            "validate_nov": sql('SELECT count(*) FROM "%s".inregistrari WHERE status = %%s AND data >= %%s AND data < %%s' % SCHEMA, ("validata", "2026-11-01", "2026-12-01"))[0][0],
            "ciorne_nov": sql('SELECT count(*) FROM "%s".inregistrari WHERE status = %%s AND data >= %%s AND data < %%s' % SCHEMA, ("ciorna", "2026-11-01", "2026-12-01"))[0][0]}
    if (baza["validate"], baza["validate_nov"]) != (32, 0) or baza["ciorne_nov"] < 1:
        rele.append("a.2 AC058: martorul din baza de test nu mai e cel așteptat (validate 10/2026 = %s, 11/2026 = %s, ciorne 11/2026 = %s; așteptat 32, 0, cel puțin 1)" % (baza["validate"], baza["validate_nov"], baza["ciorne_nov"]))

    if "Luna 10/2026" in t and baza["validate"] == 32:
        rezultate["a.2"] = "validate în lună" in t
        rezultate["a.3"] = "Luna 10/2026 · 84 de note" not in t

    # luna 11/2026: 0 note validate (și ciorne, care nu se numără); numărul vechi al liniilor cumulate nu apare
    with pg.expect_response(_raspuns(r"/firme/\d+/verificari\?"), timeout=60000) as rv2:
        pg.click(TOP + "#vf-next", timeout=10000)
    pg.wait_for_timeout(2000)
    t2 = _text_brut(pg)
    ver2 = rv2.value.json()
    if "Luna 11/2026 · 0 note validate în lună" not in t2:
        rele.append("a.2 AC058 (F1, 11/2026 = 0 note validate, %s ciorne): rândul de sus nu spune «Luna 11/2026 · 0 note validate în lună» (text: «%s…»)" % (baza["ciorne_nov"], t2[:160]))
    if ver2.get("note_luna") != 0:
        rele.append("a.2 AC058: răspunsul pe 11/2026 are note_luna = %r (așteptat 0: ciornele nu se numără)" % ver2.get("note_luna"))
    if ver2.get("note") and ("Luna 11/2026 · %s " % ver2["note"]) in t2:
        rele.append("a.2 AC058: pe 11/2026 ecranul încă scrie numărul liniilor cumulate (%s)" % ver2["note"])
    # răspuns vechi sau simulat, fără note_luna: după «Luna …» nu se scrie niciun număr
    model, handler = _json_ruta(r".*/firme/\d+/verificari\?.*", lambda c: (c.pop("note_luna", None), c)[1])
    pg.route(model, handler)
    try:
        _card(pg, parcurs, F1, "#fa-verificari", "#vf-prev")
        m = re.search(r"Luna (\d{2}/\d{4})([^L]{0,40}?)(?:← luna|$)", _text_brut(pg))
        if not m or re.search(r"\d|notă|note", m.group(2)):
            rele.append("AC058: fără note_luna în răspuns, după «Luna …» se scrie ceva (găsit: %r)" % (m.group(0) if m else None))
    finally:
        pg.unroute(model, handler)

    # a.5 — AC060: rândul Stocuri, față de răspunsul rutei verificare-stocuri
    sub = _segment(t, "Stocuri (contabil vs fișe CV)", "Intrastat (prag")
    if sub is None:
        rele.append("a.5 AC060: rândul «Stocuri (contabil vs fișe CV)» lipsește din fereastră")
    else:
        if "Ciorne de stoc: 3.251,90 lei" not in _norm(sub):
            rele.append("AC060: lipsește suma ciornelor de stoc observată pe F1 (3.251,90 lei)")
        _stocuri(rele, sub, vs)
    # a.4 — AC061: rândul Intrastat, față de răspunsul rutei intrastat-praguri
    intra = _segment(t, "Intrastat (prag 1.000.000 lei/flux, an 2026)")
    if intra is None:
        rele.append("a.4 AC061: rândul «Intrastat (prag 1.000.000 lei/flux, an 2026)» lipsește din fereastră")
    else:
        _intrastat(rele, intra, ip)
        s_exp = sql('SELECT sum(coalesce(total, 0) - coalesce(tva, 0)) FROM "%s".facturi WHERE id IN (51, 52, 53, 66) AND tert_cui = %%s' % SCHEMA, ("IE6388047V",))[0][0]
        if float(s_exp or 0) == 3000.0:
            rezultate["a.4"] = "Expedieri: 3.000,00 lei (0,3%)" in intra
        if float(s_exp or 0) != 3000.0:
            rele.append("a.4 AC061: martorul din baza de test nu mai e cel așteptat (facturile 51, 52, 53, 66 = %s, așteptat 3000.00)" % s_exp)
        if "Expedieri: 3.000,00 lei (0,3%)" not in intra:
            rele.append("a.4 AC061 (facturile 51, 52, 53 și 66 = 3.000,00 = 0,3%% din prag): rândul Intrastat nu spune «Expedieri: 3.000,00 lei (0,3%%)» (text: «%s»)" % intra[:200])

    # rândul Stocuri pe răspunsuri simulate: fără conturi = «în regulă»; cont fără diferență fără «(diferență …)» și fără nota serverului; două conturi, diferență numai pe al doilea
    cazuri = [
        ("fără conturi", {"conturi": [], "ok": True, "nota": NOTA_STOCURI}),
        ("un cont fără diferență", {"conturi": [{"cont": "371", "sold_contabil": "100.00", "valoare_fise_cv": "100.00", "diferenta": "0.00", "ok": True}], "ok": True, "nota": NOTA_STOCURI}),
        ("două conturi, diferență pe al doilea", {"conturi": [{"cont": "371", "sold_contabil": "1000.50", "valoare_fise_cv": "1000.50", "diferenta": "0.00", "ok": True},
                                                              {"cont": "301", "sold_contabil": "20.00", "valoare_fise_cv": "1520.25", "diferenta": "-1500.25", "ok": False}], "ok": False, "nota": NOTA_STOCURI}),
    ]
    for nume, corp in cazuri:
        model, handler = _simulat(r".*/tenants/\d+/verificare-stocuri$", corp)
        pg.route(model, handler)
        try:
            with pg.expect_response(_raspuns(r"/tenants/\d+/verificare-stocuri$"), timeout=60000) as primit:
                if not _card(pg, parcurs, F1, "#fa-verificari", "#vf-prev"):
                    rele.append("AC060: Verificări nu s-a deschis pentru " + nume)
                    continue
            if primit.value.status != 200 or primit.value.json() != corp:
                rele.append("AC060: răspunsul simulat nu a ajuns în pagină pentru " + nume)
                continue
            s = _segment(_text_brut(pg), "Stocuri (contabil vs fișe CV)", "Intrastat (prag")
            if s is None:
                rele.append("a.5 AC060 (răspuns simulat: %s): rândul Stocuri lipsește" % nume)
            else:
                _stocuri(rele, s, corp, "răspuns simulat: " + nume)
                if nume == "două conturi, diferență pe al doilea":
                    rezultate["a.5"] = "cont 301: contabil 20,00 lei · fișe de magazie 1.520,25 lei" in _norm(s)
            _EVALUATE.append(nume)
        finally:
            pg.unroute(model, handler)


def _stocuri(rele, sub, vs, unde="F1"):
    """Rândul Stocuri față de răspunsul rutei (cifrele rutei, neschimbate), nu față de cifre fixate."""
    sub = _norm(sub)
    conturi = vs.get("conturi") or []
    if not conturi:
        if "în regulă" not in sub or "fișe de magazie" in sub:
            rele.append("a.5 AC060 (%s): răspuns fără conturi, rândul nu rămâne «în regulă» (text: «%s»)" % (unde, sub[:200]))
        return
    for c in conturi:
        frag = "cont %s: contabil %s lei · fișe de magazie %s lei" % (c["cont"], ro(c["sold_contabil"]), ro(c["valoare_fise_cv"]))
        if frag not in sub:
            rele.append("a.5 AC060 (%s): lipsește «%s» (text: «%s»)" % (unde, frag, sub[:240]))
        dif = "(diferență %s lei)" % ro(c["diferenta"])
        if not c["ok"] and frag + " " + dif not in sub:
            rele.append("a.5 AC060 (%s): contul %s are diferență, dar lipsește «%s» (text: «%s»)" % (unde, c["cont"], dif, sub[:240]))
    nr_fara_ok = sum(1 for c in conturi if not c["ok"])
    if sub.count("(diferență") != nr_fara_ok:
        rele.append("a.5 AC060 (%s): «(diferență …)» apare de %d ori, conturile cu ok fals sunt %d" % (unde, sub.count("(diferență"), nr_fara_ok))
    if not vs.get("ok") and (not vs.get("nota") or vs["nota"] not in sub):
        rele.append("a.5 AC060 (%s): ok e fals, dar nota serverului «%s» nu e în rând (text: «%s»)" % (unde, vs.get("nota"), sub[:240]))
    if vs.get("ok") and NOTA_STOCURI in sub:
        rele.append("a.5 AC060 (%s): ok e adevărat, dar rândul spune nota diferențelor" % unde)
    if " vs fișe " in sub:
        rele.append("a.5 AC060 (%s): rândul mai spune «vs fișe» (formularea veche)" % unde)


def _intrastat(rele, intra, ip):
    intra = _norm(intra)
    for cheie, eticheta in (("introduceri", "Introduceri"), ("expedieri", "Expedieri")):
        o = ip.get(cheie)
        if o:
            asteptat = "%s: %s lei (%s)" % (eticheta, ro(o["cumulat"]), ro_pct(o["procent"]))
            if o.get("status") != "sub_prag":
                asteptat += " · depășit din luna %s" % o.get("luna_depasirii")
        else:
            asteptat = "%s: -" % eticheta
        if asteptat not in intra:
            rele.append("a.4 AC061: rândul Intrastat nu spune «%s» (text: «%s»)" % (asteptat, intra[:240]))
    if re.search(r"\d\.\d+ lei|\d\.\d%", intra):
        rele.append("a.4 AC061: rândul Intrastat are încă punct zecimal sau procent cu punct (text: «%s»)" % intra[:240])


# ── 4. Scadențar F1: AC077 (a.1) ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _scadentar(rele, pg, parcurs, rezultate):
    def _deschide():
        if not _card(pg, parcurs, F1, "#fa-facturi", "#fac-scadentar"):
            return False
        pg.click(TOP + "#fac-scadentar", timeout=10000)
        pg.wait_for_selector(TOP + ".cf-sumar", timeout=30000)
        pg.wait_for_timeout(2000)
        return True
    with pg.expect_response(_raspuns(r"/tenants/\d+/scadentar$"), timeout=60000) as rs:
        if not _deschide():
            rele.append("Scadențar F1: cardul «Facturi» nu s-a deschis")
            return
    linii = rs.value.json().get("linii") or []
    pastile = pg.evaluate(JS_PASTILE)
    randuri = len(linii)   # fiecare factură din răspuns are rând în listă (randFacturi(d.linii))
    fara = sum(1 for l in linii if l.get("stare") == "fara_scadenta")
    fact = sql('SELECT count(*) FROM "%s".facturi WHERE id IN (66, 71) AND directie = %%s AND data_scadenta IS NULL' % SCHEMA, ("emisa",))[0][0]
    if pastile:
        rezultate["f.2"] = any("în termen" in p[0] for p in pastile)
        if fact == 2 and fara == 2:
            rezultate["a.1"] = any("fără scadență în sistem" in p[0] for p in pastile)
    if len(pastile) != 4:
        rele.append("a.1 AC077 (F1, facturile 66 și 71 fără scadență): rândul de pastile are %d pastile (%s), așteptat 4" % (len(pastile), [p[0] for p in pastile]))
        return
    if not pastile[2][0].endswith("în termen"):
        rele.append("f.2: a treia pastilă nu mai e «<n> în termen» (%r)" % pastile[2][0])
    if pastile[3][0] != "2 fără scadență în sistem":
        rele.append("a.1 AC077 (F1, facturile 66 și 71): a patra pastilă e %r (așteptat «2 fără scadență în sistem»)" % pastile[3][0])
    if "gri-semafor" not in pastile[3][1]:
        rele.append("a.1 AC077: pastila nouă n-are punctul cf-dot cu culoarea SEM.fara_scadenta (var(--gri-semafor)); stil: %r" % pastile[3][1])
    nr = [re.match(r"^(\d+)", p[0]) for p in pastile]
    if not all(nr):
        rele.append("a.1 AC077: o pastilă nu începe cu număr (%s)" % [p[0] for p in pastile])
    else:
        suma = sum(int(m.group(1)) for m in nr)
        if suma != randuri:
            rele.append("a.1 AC077: cele patru contoare însumează %d, lista are %d facturi (contoarele trebuie să însumeze toate rândurile listei)" % (suma, randuri))
        if int(nr[3].group(1)) != fara:
            rele.append("a.1 AC077: pastila spune %s fără scadență, lista are %d facturi cu starea fara_scadenta" % (nr[3].group(1), fara))
    if fact != 2:
        rele.append("a.1 AC077: martorul din baza de test nu mai e cel așteptat (facturile 66 și 71 emise fără scadență = %s, așteptat 2)" % fact)
    # Fișă client: rândul de pastile propriu (#sc-fisa-sold) nu primește pastila nouă
    try:
        pg.click(TOP + "#sc-clienti", timeout=10000)
        pg.wait_for_timeout(1200)
        if pg.locator(TOP + "#sc-fisa-sold").count() and "fără scadență în sistem" in pg.locator(TOP + "#sc-fisa-sold").first.inner_text():
            rele.append("AC077: rândul de pastile din Fișă client (#sc-fisa-sold) a primit pastila «fără scadență în sistem» (nu se atinge)")
    except Exception:   # noqa: BLE001 — vederea Fișă client nu se deschide: rândul ei de pastile nu se măsoară
        pass
    # afișată MEREU: și când răspunsul spune 0 sau n-are câmpul
    for nume, mod in (("fara_scadenta = 0", lambda c: c["rezumat"].__setitem__("fara_scadenta", 0)), ("fără câmpul fara_scadenta", lambda c: c["rezumat"].pop("fara_scadenta", None))):
        model, handler = _json_ruta(r".*/tenants/\d+/scadentar$", lambda c, mod=mod: (mod(c), c)[1])
        pg.route(model, handler)
        try:
            _deschide()
            p = pg.evaluate(JS_PASTILE)
            if len(p) != 4 or p[3][0] != "0 fără scadență în sistem":
                rele.append("a.1 AC077 (răspuns cu %s): a patra pastilă e %r (așteptat «0 fără scadență în sistem», afișată mereu)" % (nume, p[3][0] if len(p) > 3 else None))
        finally:
            pg.unroute(model, handler)


# ── 5. Cartea mare F1: AC050 (a.6) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _cartea_mare(rele, pg, parcurs, rezultate):
    with pg.expect_response(_raspuns(r"/tenants/\d+/fisa-cont\?"), timeout=60000) as rf:
        if not _card(pg, parcurs, F1, "#fa-fisacont", "#fc-cont"):
            rele.append("Cartea mare F1: cardul nu s-a deschis")
            return
    d = rf.value.json()
    for cheie in ("conturi", "fisa", "formular"):
        if cheie not in d:
            rele.append("a.6 AC050: răspunsul rutei fisa-cont a pierdut cheia `%s`" % cheie)
    den = d.get("denumiri")
    if not isinstance(den, dict):
        rele.append("a.6 AC050: răspunsul rutei fisa-cont n-are câmpul `denumiri` ({simbol: denumire}); găsit %r" % (den,))
        den = {}
    elif not set(den) <= set(d.get("conturi") or []):
        rele.append("a.6 AC050: `denumiri` are și simboluri care nu sunt în `conturi`: %s" % sorted(set(den) - set(d.get("conturi") or [])))
    plan = {s: " ".join((n or "").split()) for s, n in sql('SELECT simbol, denumire FROM "%s".plan_conturi' % SCHEMA)}
    if plan.get("371") != "Mărfuri":
        rele.append("a.6 AC050: martorul din baza de test nu mai e cel așteptat (plan_conturi 371 = %r, așteptat «Mărfuri»)" % plan.get("371"))
    optiuni = pg.evaluate(JS_OPTIUNI)
    if not optiuni or optiuni[0] != ["", "— alege contul —"]:
        rele.append("a.6 AC050: prima opțiune nu mai e «— alege contul —» cu valoarea goală (găsit %r)" % (optiuni[:1],))
    reale = optiuni[1:]
    if ["371", "371 · Mărfuri"] not in reale:
        rele.append("a.6 AC050 (F1, contul 371 = Mărfuri): lista nu are opțiunea «371 · Mărfuri» cu valoarea 371 (opțiuni: %s)" % reale[:8])
    for v, text in reale:
        den_v = plan.get(v)
        asteptat = ("%s · %s" % (v, den_v)) if den_v else v
        if text != asteptat:
            rele.append("a.6 AC050: opțiunea cu valoarea %s se citește «%s», așteptat «%s» (denumirea din plan_conturi)" % (v, text, asteptat))
    if not reale:
        rele.append("a.6 AC050: lista nu are niciun cont cu mișcare")
        return
    pg.select_option(TOP + "#fc-cont", "371", timeout=10000)
    pg.wait_for_timeout(2500)
    ales = pg.evaluate(JS_ALES)
    _masoara_a6(rezultate, ales, plan.get("371"))
    if ales != ["371", "371 · Mărfuri"]:
        rele.append("a.6 AC050: după alegerea contului 371, opțiunea aleasă se citește %r (așteptat «371 · Mărfuri», valoarea 371)" % (ales,))
    if not pg.locator(TOP + ".fd-tabel tbody tr").count():
        rele.append("AC050: fișa contului 371 nu s-a încărcat după alegerea din listă (value-ul opțiunii a rămas simbolul)")
    # răspuns fără `denumiri` (vechi sau simulat): opțiunile sunt numai simbolurile
    model, handler = _json_ruta(r".*/tenants/\d+/fisa-cont\?.*", lambda c: (c.pop("denumiri", None), c)[1])
    pg.route(model, handler)
    try:
        _card(pg, parcurs, F1, "#fa-fisacont", "#fc-cont")
        opt2 = pg.evaluate(JS_OPTIUNI)[1:]
        rele_fara = [o for o in opt2 if o[0] != o[1]]
        if not opt2 or rele_fara:
            rele.append("a.6 AC050: fără `denumiri` în răspuns, opțiunile nu sunt numai simbolurile (nepotrivite: %s)" % rele_fara[:4])
    finally:
        pg.unroute(model, handler)


# ── 6. e-Transport F1: AC041 (a.7) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _et_deschide(pg, parcurs):
    ok = _card(pg, parcurs, F1, "#fa-etransport", "#et-trimite")
    pg.wait_for_timeout(2500)   # starea SPV se citește la deschidere, după desenarea ferestrei
    return ok


def _et_fara_drept(rele, s, unde):
    t, g = s["trimite"], s["genereaza"]
    if not t or not g:
        rele.append("a.7 AC041 (%s): butoanele #et-trimite / #et-genereaza lipsesc" % unde)
        return
    for key in ("aceeasi", "trimite_vizibil", "motiv_vizibil", "xml_vizibil", "vecin", "separat", "xml_activ"):
        if not s["bara"][key]:
            rele.append(f"a.7 AC041 ({unde}): {key} — {s['bara']['pozitii']}")
    if t["text"] != "Trimite UIT în SPV" or g["text"] != "Doar generează XML (manual)":
        rele.append(f"a.7 AC041 ({unde}): etichetele acțiunilor diferă")
    if t["aria"] != "true":
        rele.append("a.7 AC041 (%s): «Trimite UIT în SPV» nu e inactiv prin aria-disabled (aria-disabled = %r)" % (unde, t["aria"]))
    if t["title"] != MOTIV_SPV:
        rele.append("a.7 AC041 (%s): motivul din title al lui #et-trimite e %r (așteptat «%s»)" % (unde, t["title"], MOTIV_SPV))
    if "buton-primar" in t["clasa"] or "buton-secundar" not in t["clasa"]:
        rele.append("a.7 AC041 (%s): #et-trimite nu e buton secundar (clasa %r)" % (unde, t["clasa"]))
    if s["principale"] != ["et-genereaza"]:
        rele.append("a.7 AC041 (%s): butonul principal al ferestrei e %s (așteptat numai «et-genereaza», adică «Doar generează XML (manual)»)" % (unde, s["principale"]))
    if s["n_motiv"] != 1 or not s["motiv"]:
        rele.append("a.7 AC041 (%s): elementul #et-motiv-spv apare de %d ori (așteptat o dată)" % (unde, s["n_motiv"]))
    else:
        m = s["motiv"]
        if m["text"] != MOTIV_SPV:
            rele.append("a.7 AC041 (%s): #et-motiv-spv spune %r (așteptat «%s»)" % (unde, m["text"], MOTIV_SPV))
        if "ds-motiv-inactiv" not in m["clasa"]:
            rele.append("a.7 AC041 (%s): #et-motiv-spv n-are clasa ds-motiv-inactiv (clasa %r)" % (unde, m["clasa"]))
        if not m["vizibil"] or not m["in_bara"]:
            rele.append("a.7 AC041 (%s): motivul nu e vizibil în bara de jos (vizibil %s, în .fj-motiv %s)" % (unde, m["vizibil"], m["in_bara"]))


def _et_neschimbat(rele, s, unde):
    t = s["trimite"]
    if not t:
        rele.append("a.7 AC041 (%s): #et-trimite lipsește" % unde)
        return
    if t["aria"] == "true" or t["title"] == MOTIV_SPV or s["n_motiv"] or s["motiv"]:
        rele.append("a.7 AC041 (%s): e-Transport s-a schimbat deși nu se știe că firma n-are drept SPV (aria-disabled %r, title %r, #et-motiv-spv %d)" % (unde, t["aria"], t["title"], s["n_motiv"]))
    if s["principale"] != ["et-trimite"]:
        rele.append("a.7 AC041 (%s): butonul principal nu mai e «Trimite UIT în SPV» (principale: %s)" % (unde, s["principale"]))


def _etransport(rele, pg, parcurs, rezultate):
    cereri = []
    pg.on("request", lambda c: cereri.append((c.method, c.url)) if "/etransport" in c.url else None)
    if not _et_deschide(pg, parcurs):
        rele.append("e-Transport F1: cardul nu s-a deschis")
        return
    # martor: F1, public.spv_token fără rând activ → acoperire «neconectat»
    active = sql("SELECT count(*) FROM public.spv_token WHERE activ = true")[0][0]
    if active != 0:
        rele.append("a.7 AC041: martorul din baza de test nu mai e cel așteptat (public.spv_token cu rânduri active = %s, așteptat 0)" % active)
    s = pg.evaluate(JS_ET)
    defecte = []
    _et_fara_drept(defecte, s, "F1, acoperire neconectat")
    if active == 0 and s["trimite"] and s["genereaza"]:
        rezultate["a.7"] = not defecte
    rele.extend(defecte)
    # (d) updateFereastra: o dată în fereastră, motivul rămâne în title și butonul nu se reactivează
    try:
        pg.click(TOP + ".rap-tab[data-fila='partener']", timeout=10000)   # #t-data stă în fila «partener» (et-fila-partener)
        pg.fill(TOP + "#t-data", "2026-11-02", timeout=10000)
        pg.dispatch_event(TOP + "#t-data", "change")
        pg.wait_for_timeout(800)
        s2 = pg.evaluate(JS_ET)
        _et_fara_drept(rele, s2, "F1, după schimbarea datei")
    except Exception as e:   # noqa: BLE001
        rele.append("a.7 AC041 (d): câmpul #t-data nu s-a putut completa (%s)" % type(e).__name__)
    # clicul pe butonul inactiv nu pleacă nicio cerere; «Doar generează XML» o trimite (cu formularul gol marchează câmpurile lipsă, nu descarcă nimic)
    cereri.clear()
    # cererea cliculului pe butonul inactiv se opreste in browser: pe baza (butonul inca activ) nu pleaca nimic spre server, dar cererea se inregistreaza
    model_et = re.compile(r".*/tenants/\d+/etransport.*")

    def _opreste_et(ruta, cerere):
        if cerere.method == "POST":
            cereri.append((cerere.method, cerere.url))
            ruta.abort()
        else:
            ruta.continue_()
    pg.route(model_et, _opreste_et)
    try:
        pg.click(TOP + "#et-trimite", force=True, timeout=10000)
        pg.wait_for_timeout(1500)
    finally:
        pg.unroute(model_et, _opreste_et)
    if [c for c in cereri if c[0] == "POST"]:
        rele.append("a.7 AC041: clicul pe «Trimite UIT în SPV» inactiv a inițiat o cerere POST, interceptată și anulată: %s" % cereri)
    cereri.clear()
    gen = pg.locator(TOP + "#et-genereaza")
    gen.click(timeout=10000)
    pg.wait_for_timeout(2500)
    if not [c for c in cereri if c[0] == "POST" and "etransport-xml" in c[1]]:
        rele.append("a.7 AC041: «Doar generează XML (manual)» nu mai trimite cererea etransport-xml")
    # celelalte acoperiri ale stării SPV, pe răspunsuri simulate
    stari = [
        ("neacoperit", {"acoperire": "neacoperit", "conectat": True, "cui": "RO1", "mesaj": "Certificatul cabinetului nu are drept pe acest CUI."}, True),
        ("fără câmpul acoperire, conectat fals", {"conectat": False}, True),
        ("acoperit", {"acoperire": "acoperit", "conectat": True, "cui": "RO1", "verificat_la": "2026-11-03T09:00:00"}, False),
        ("neverificat", {"acoperire": "neverificat", "conectat": True, "cui": "RO1"}, False),
        ("neconfirmat", {"acoperire": "neconfirmat", "conectat": True, "cui": "RO1", "eroare": "fără răspuns", "eroare_de_la_anaf": False, "verificat_la": "2026-11-03T09:00:00"}, False),
    ]
    for nume, corp, fara_drept in stari + [("starea SPV nu se poate citi (HTTP 500)", {"detail": "eroare"}, False)]:
        model, handler = _simulat(r".*/tenants/\d+/spv/stare$", corp, 500 if "HTTP 500" in nume else 200)
        pg.route(model, handler)
        try:
            _et_deschide(pg, parcurs)
            s = pg.evaluate(JS_ET)
            (_et_fara_drept if fara_drept else _et_neschimbat)(rele, s, "răspuns simulat: " + nume)
        finally:
            pg.unroute(model, handler)


# ── 7–8. Import salariați F5: AC117 (modelul), AC118 (previzualizarea) ──────────────────────────────────────────────────────────────────────────
def _salariati(rele, pg, parcurs):
    if not _card(pg, parcurs, F5, "#fa-import", ".mig-frand"):
        rele.append("Import salariați F5: cardul «Import date» nu s-a deschis")
        return
    pg.locator(TOP + ".mig-frand", has_text="Salaria").first.click(timeout=10000)
    pg.wait_for_selector(TOP + "#mig-file", state="attached", timeout=20000)
    with pg.expect_download(timeout=30000) as d:
        pg.click(TOP + "#mig-model", timeout=10000)
    brut = open(d.value.path(), "rb").read().decode("utf-8-sig")
    randuri = list(csv.reader(io.StringIO(brut), delimiter=";"))
    # AC117: modelul are COR 331302 («contabil») și 513102 («ospătar (chelner)»); nicio altă valoare nu se schimbă
    if not randuri or randuri[0] != COLOANE_MODEL:
        rele.append("AC117: antetul modelului s-a schimbat (găsit %s)" % (randuri[:1],))
    elif len(randuri) != 3:
        rele.append("AC117: modelul are %d rânduri de date (așteptat 2)" % (len(randuri) - 1))
    else:
        for i, asteptat in enumerate(RANDURI_MODEL, 1):
            gasit = [re.sub(r'[="]', "", c) if j == 2 else c for j, c in enumerate(randuri[i])]
            if gasit != asteptat:
                rele.append("AC117: rândul %d al modelului (%s) e %s, așteptat %s (singura diferență de azi: COR 331302 și 513102)" % (i, asteptat[0], gasit, asteptat))
    if "251401" in brut or "522101" in brut:
        rele.append("AC117: modelul mai are codurile COR vechi (251401 sau 522101)")
    cor = sql("SELECT cod, denumire FROM public.cor_ocupatii WHERE cod IN ('331302', '513102') ORDER BY cod")
    if [tuple(r) for r in cor] != [("331302", "contabil"), ("513102", "ospătar (chelner)")]:
        rele.append("AC117: martorul din nomenclator nu mai e cel așteptat (public.cor_ocupatii: %s)" % cor)
    # AC118: modelul descărcat se încarcă în F5; previzualizarea are, la sfârșit, «Județ» și «IBAN»
    with pg.expect_response(lambda r: r.url.split("?")[0].endswith("/salariati-import/incarca") and r.request.method == "POST", timeout=60000) as ri:
        pg.set_input_files(TOP + "#mig-file", files=[{"name": "model_salariati.csv", "mimeType": "text/csv", "buffer": brut.encode("utf-8")}])
    pg.wait_for_selector(TOP + ".mig-prev tbody tr", timeout=30000)
    pg.wait_for_timeout(1000)
    date = ri.value.json()
    antet = pg.evaluate(JS_ANTET_PREV)
    if antet[-2:] != ["Județ", "IBAN"]:
        rele.append("AC118: ultimele două coloane ale previzualizării sunt %s (așteptat «Județ», «IBAN»)" % antet[-2:])
    nr_coloane = len(antet)
    randuri_prev = date.get("randuri") or []
    if len(randuri_prev) != 2:
        rele.append("AC118: previzualizarea are %d rânduri citite (așteptat 2, modelul)" % len(randuri_prev))
    for r in randuri_prev:
        celule = pg.evaluate(JS_CELULE, str(r.get("rand_fisier")))
        asteptat = ((r.get("judet_casa") or "—"), grupe4(r.get("iban")) or "—")
        if len(celule) != nr_coloane or tuple(celule[-2:]) != asteptat:
            rele.append("AC118: rândul %s (%s) are la sfârșit %s, așteptat %s (județ din fișier, IBAN în grupe de patru)" % (r.get("rand_fisier"), r.get("nume"), celule[-2:], list(asteptat)))
        if r.get("nume") == "Popescu" and tuple(celule[-2:]) != ("B", IBAN_MODEL_GRUPAT):
            rele.append("AC118 (rândul Popescu Ana, IBAN %s, județ B): coloanele noi sunt %s, așteptat [B, %s]" % (IBAN_MODEL, celule[-2:], IBAN_MODEL_GRUPAT))
        if r.get("iban") and " " in r["iban"]:
            rele.append("AC118: valoarea IBAN a rândului %s are spații în răspunsul serverului: %r" % (r.get("rand_fisier"), r["iban"]))
    if not any(r.get("nume") == "Popescu" for r in randuri_prev):
        rele.append("AC118: rândul Popescu Ana (martorul) lipsește din previzualizare")
    # valoarea trimisă la salvare rămâne cea din fișier (fără spații): cererea de salvare se oprește în browser, nimic nu se salvează.
    # Dacă fluxul de salvare cere o confirmare înaintea cererii, cererea nu pleacă și verificarea nu se face (limită: aici nu se confirmă nimic).
    capturat = []
    model = re.compile(r".*/tenants/\d+/salariati-import$")

    def _opreste(ruta, cerere):
        if cerere.method == "POST":
            capturat.append(cerere.post_data or "")
            ruta.abort()
        else:
            ruta.continue_()
    pg.route(model, _opreste)
    try:
        pg.click(TOP + "#mig-salveaza-sal", timeout=10000)
        pg.wait_for_timeout(3000)
    except Exception as e:   # noqa: BLE001
        rele.append("AC118: butonul «Salvează salariații» nu s-a putut apăsa (%s)" % type(e).__name__)
    finally:
        pg.unroute(model, _opreste)
    for corp in capturat:
        try:
            ibanuri = [x.get("iban") for x in json.loads(corp).get("randuri", [])]
        except (ValueError, AttributeError):
            continue
        if IBAN_MODEL not in ibanuri or any(i and " " in i for i in ibanuri):
            rele.append("AC118: cererea de salvare poartă IBAN-urile %s (așteptat %s, neschimbat, fără spații)" % (ibanuri, IBAN_MODEL))


def test_ferestre_firma_17_5_N(browser, capsys):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele = []
    rezultate = {}
    b = browser.new_context(viewport={"width": 1366, "height": 768}, accept_downloads=True)
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        _sectiune(rele, "Pagina principală", _pagina_principala, pg, rezultate)
        _sectiune(rele, "Verificări F1 (AC058, AC060, AC061)", _verificari, pg, parcurs, rezultate)
        _sectiune(rele, "Scadențar F1 (AC077)", _scadentar, pg, parcurs, rezultate)
        with capsys.disabled():
            _sectiune(rele, "Cartea mare F1 (AC050)", _cartea_mare, pg, parcurs, rezultate)
        _sectiune(rele, "e-Transport F1 (AC041)", _etransport, pg, parcurs, rezultate)
        _sectiune(rele, "Import salariați F5 (AC117, AC118)", _salariati, pg, parcurs)
    finally:
        with capsys.disabled():
            _raporteaza(rele, rezultate)
        b.close()
    assert not rele, "ferestrele firmei 17.5-N [stocuri simulate evaluate: %d din 3 (%s)]: %s" % (len(_EVALUATE), ", ".join(_EVALUATE), "; ".join(rele))
