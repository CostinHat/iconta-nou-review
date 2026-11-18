# -*- coding: utf-8 -*-
"""FERESTRE: ETICHETE ȘI ZONE DE DERULARE LA REZOLUȚII MICI — lotul 17.5-K (constatările AC019, AC020, AC043, AC057, AC065, AC074, AC082, AC092, AC102, AC111 din auditul complet;
decizii_17_5_K.txt și «De ce» din comanda_17_5_K.txt). Testul corectat a.9/a.11 este redactat de GPT-6; Code îl aplică și îl execută.

Cu contul administratorului (dovada.71507), ceas înghețat 03.11.2026 (ceas_proba.MOMENT_REF), fiecare măsurare pe o fereastră deschisă proaspăt (goto) la rezoluția ei, cu o singură fereastră deschisă:
  a.1   Sinteza zilei, «Ultimele evenimente», 603×590: eticheta «Vezi tot» pe un singur rând (getClientRects);
  a.2   e-Transport F1, 603×590: cele patru file `.rap-tab` între 24 și 40 px înălțime și pe un singur rând (1,1,1,1);
  a.3   Control fiscal (firmă) F1, rândul D406 01/2026, 603×590: butoanele «Modifică marcarea» și «Anulează marcarea» între 20 și 30 px, pe un rând (1,1), nimic ieșit din fereastră;
  a.4   Rapoarte comerciale F1, 603×590: locul de derulare utilizabil `loc` ≥ 201 px;
  a.5   Plan de conturi F1, 603×590: `loc` ≥ 201 px;
  a.6   Analitică stoc F1 (analitica deschisă), 1366×768: `loc` ≥ 272 px;
  a.7   Import date — Solduri inițiale F1 (fișierul solduri_17_5_K.csv încărcat), 1366×603: `loc` ≥ 206 px;
  a.8   Mijloace fixe — Leasing F1, tip «Primire bun», 1366×603: `position` calculat al `.bara-fixa:has(#op-renunta)` = static;
  a.9   același loc: niciun câmp vizibil al formularului «acoperit» (elementFromPoint, după scrollIntoView center);
  a.10  Certificat CM F5, Certificat nou pentru Ionescu Vasile, 1366×768: `position` al `.bara-fixa:has(#cm-renunta)` = static;
  a.11  același loc: niciun câmp acoperit;
  a.12  Chirii / comodat / refacturări F2, 1366×603: `position` al `.bara-fixa:has(#op-renunta)` = static;
  a.13  Declarații F1 pasul 1, deschisă la 1366×768 și apoi fereastra browserului redusă la 603×590 FĂRĂ reîncărcare: placeholderul lui `#cautare-fereastra` = «Caută»;
  f.1   pagina cabinetului la 1366×768 conține «Control fiscal» (invariantă);  f.2  Plan de conturi F1 la 1366×768 conține «Adaugă analitic» (invariantă);
  f.3   același pas ca a.13, fereastra browserului readusă la 1366×768 fără reîncărcare: placeholderul = «Caută o funcție: D300, stat de plată, NIR…» (garda întoarcerii).
În plus, fără id: butonul «Renunță» vizibil în corp, cu dimensiunea de azi, la Leasing, Certificat nou și Chirii F2; criteriul de zonă întreg (cel mult un loc de derulare; zona ≥ 40% din corp sau fără derulare;
fără zonă, singurul loc de derulare e corpul) la cele patru ferestre ale lui (5), la cele trei rezoluții (603×590, 1366×603, 1366×768).
Tipărește (și când trece) rândurile MASURA <fereastra> <lățime>x<înălțime> zona=<px> corp=<px> derulante=<n> loc=<px>, MASURA acoperit <fereastra> <lățime>x<înălțime> campuri=<n> acoperite=<k> bara_sus=<px>,
MASURA renunta … și un rând VERDICT <id> trece|pica pentru fiecare dintre cele 16 id-uri. Nu salvează nimic. Un singur test."""
import importlib.util
import os
import sys

from conftest import BAZA, sesiune
from e2e_pilot_x06 import JS_DERULARI
from e2e_pilot_x09 import JS_IESITE

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
F2 = "F2 Profit Amortizare"
F5 = "F5 SRL Salariati"
TOP = ".fereastra-overlay:not(.fundal) "
R1, R2, R3 = (603, 590), (1366, 603), (1366, 768)   # rezoluțiile măsurilor (corp 502, 515 și 680 px)
REZOLUTII = (R1, R2, R3)
PRAG_LOC = {("Rapoarte comerciale F1", R1): 201, ("Plan de conturi F1", R1): 201, ("Analitică stoc F1", R3): 272, ("Import date — Solduri inițiale F1", R2): 206}
ID_AN = {"Rapoarte comerciale F1": "a.4", "Plan de conturi F1": "a.5", "Analitică stoc F1": "a.6", "Import date — Solduri inițiale F1": "a.7"}
SOLDURI_CSV = os.path.expanduser("~/ghid_incoming/solduri_17_5_K.csv")
PLACEHOLDER_SCURT = "Caută"
PLACEHOLDER_LUNG = "Caută o funcție: D300, stat de plată, NIR…"
ID_URI = ("f.1", "a.1", "a.2", "a.3", "a.4", "a.5", "a.6", "a.7", "a.8", "a.9", "a.10", "a.11", "a.12", "a.13", "f.2", "f.3")

JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""
# rândurile de text ale fiecărui element potrivit: valori distincte ale lui `top` (±2 px) ale dreptunghiurilor textului (getClientRects pe un Range peste conținutul elementului); dreptunghiurile fără lățime (span-uri goale) nu se numără
JS_RANDURI = """(sel) => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) ' + sel)].map((e) => {
  const r = document.createRange(); r.selectNodeContents(e);
  const tops = [];
  for (const q of r.getClientRects()) { if (q.width === 0) continue; if (!tops.some((t) => Math.abs(t - q.top) <= 2)) tops.push(q.top); }
  return tops.length;
})"""
JS_INALTIMI = """(sel) => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) ' + sel)].map((e) => Math.round(e.getBoundingClientRect().height * 10) / 10)"""
JS_POZITIE = """(sel) => { const e = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); return e ? getComputedStyle(e).position : null; }"""
# butonul «Renunță»: vizibil (getClientRects, visibility, lățime și înălțime > 0), în corpul ferestrei, cu dimensiunea lui calculată
JS_RENUNTA = """(sel) => {
  const b = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!b) return null;
  const r = b.getBoundingClientRect(), cs = getComputedStyle(b);
  return {vizibil: b.getClientRects().length > 0 && cs.visibility !== 'hidden' && r.width > 0 && r.height > 0, in_corp: !!b.closest('.fereastra-corp'),
          h: Math.round(r.height * 10) / 10, w: Math.round(r.width * 10) / 10, pad: cs.paddingLeft, text: (b.textContent || '').trim()};
}"""
# «acoperit»: control realmente vizibil (inclusiv piesa DS care înlocuiește un select-sursă invizibil), după scrollIntoView center și randare;
# elementFromPoint trebuie să atingă controlul sau un descendent. O sursă fără piesa vizibilă așteptată este defect, nu PASS.
# bara_sus = `top` al barei față de marginea de sus a corpului, cu corpul derulat la început
JS_ACOPERITE = """async (selBara) => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return null;
  const corp = F.querySelector('.fereastra-corp'); if (!corp) return null;
  const vizibil = (e) => {
    if (!e || !e.isConnected) return false;
    for (let n = e; n && n.nodeType === 1; n = n.parentElement) {
      const s = getComputedStyle(n);
      if (n.hidden || n.getAttribute('aria-hidden') === 'true' || s.display === 'none' ||
          s.visibility === 'hidden' || s.visibility === 'collapse' || Number(s.opacity) === 0) return false;
    }
    const r = e.getBoundingClientRect();
    return e.getClientRects().length > 0 && r.width > 0 && r.height > 0;
  };
  const cadru = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));
  corp.scrollTop = 0; await cadru();
  const bara = corp.querySelector(selBara);
  const bara_sus = bara ? Math.round((bara.getBoundingClientRect().top - corp.getBoundingClientRect().top) * 10) / 10 : null;
  // Măsurăm controalele UTILIZATE de om, nu select-urile invizibile care le păstrează valoarea.
  // DS: .ds-lista este DUPĂ sursă; .alegere-butoane/.alegere-comutator/.alegere-text sunt ÎNAINTE.
  const campuri = [], piese_lipsa = [], vazute = new Set();
  const adauga = (e, nume) => {
    if (vizibil(e) && !e.closest('.bara-fixa, .fereastra-jos') && !vazute.has(e)) {
      vazute.add(e); campuri.push({e, nume});
    }
  };
  for (const s of corp.querySelectorAll('input, select, textarea')) {
    if ((s.tagName === 'INPUT' && s.type === 'hidden') || s.closest('.bara-fixa, .fereastra-jos')) continue;
    if (s.matches('select.ds-lista-sursa, select.alegere-sursa')) {
      if (s.hidden || s.closest('[hidden]')) continue; // câmp condițional care nu este afișat
      if (s.matches('select.alegere-sursa[data-gol]')) continue; // cadru.js:74: listă fără variante, ascunsă intenționat, fără piesă
      const id = s.id || s.name || 'select';
      const lista = s.classList.contains('ds-lista-sursa');
      const piesa = lista ? s.nextElementSibling : s.previousElementSibling;
      const potrivita = piesa && (lista ? piesa.matches('.ds-lista') :
        piesa.matches('.alegere-butoane, .alegere-comutator, .alegere-text'));
      if (!potrivita) { piese_lipsa.push(id); continue; }  // nu mascăm un control lipsă
      if (!vizibil(piesa)) continue; // piesa este ascunsă legitim de starea formularului
      if (lista) {
        const tinta = piesa.querySelector('.ds-lista-titlu, .ds-lista-cauta, .ds-lista-rand');
        if (!tinta || !vizibil(tinta)) piese_lipsa.push(id);
        else adauga(tinta, id);
      } else if (piesa.matches('.alegere-butoane')) {
        const butoane = [...piesa.querySelectorAll('button')].filter(vizibil);
        if (!butoane.length) piese_lipsa.push(id);
        butoane.forEach((b, i) => adauga(b, id + '/buton' + (i + 1)));
      } else adauga(piesa, id);
      continue;
    }
    adauga(s, s.id || s.name || s.tagName.toLowerCase());
  }
  const acoperite = [];
  for (const {e, nume} of campuri) {
    e.scrollIntoView({block: 'center'}); await cadru();
    const r = e.getBoundingClientRect();
    const el = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    if (!(el && (el === e || e.contains(el)))) {
      acoperite.push(nume + ' sub ' + (el ? (el.tagName.toLowerCase() + '.' + String(el.className).trim().split(/\\s+/)[0]) : 'nimic'));
    }
  }
  corp.scrollTop = 0;
  return {campuri: campuri.length, acoperite, piese_lipsa, bara_sus};
}"""


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _norm(t):
    return " ".join((t or "").split())


def _acasa(pg):
    """Pagina principală proaspătă (goto), cu cardurile desenate."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(BAZA + "/", wait_until="load", timeout=30000)
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    pg.wait_for_timeout(1000)


def _card(pg, parcurs, firma, sel, asteapta=None):
    """Fereastra firmei `firma` proaspătă, cardul `sel` din ea (grupul pliat se deschide), așteptarea lui `asteapta` în fereastra nouă."""
    parcurs.firma(pg, firma)
    if pg.evaluate(JS_DESCHIDE_CARD, sel) != "ok":
        return False
    pg.click(TOP + sel, timeout=10000)
    try:
        pg.wait_for_selector(TOP + "#fa-facturi", state="detached", timeout=20000)
        if asteapta:
            pg.wait_for_selector(TOP + asteapta, state="attached", timeout=30000)
    except Exception:   # noqa: BLE001 — fereastra nu s-a schimbat: se măsoară ce e desenat, rezultatul pică
        return False
    pg.wait_for_timeout(2000)
    return True


def _w_rapoarte(pg, parcurs):
    """Rapoarte comerciale F1, anul 2026 (ceasul înghețat), vederea «Vânzări» cu tabelul celor 4 parteneri."""
    if not _card(pg, parcurs, F1, "#fa-rapoarte", "#r-vederi"):
        return False
    try:
        pg.wait_for_selector(TOP + ".rc-vedere[data-vedere='vanzari'] tbody tr", state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)
    return True


def _w_plan(pg, parcurs):
    """Plan de conturi F1 (579 de conturi): lista `#pcf-lista` umplută."""
    if not _card(pg, parcurs, F1, "#fa-planconturi", "#pcf-lista"):
        return False
    try:
        pg.wait_for_function("() => document.querySelectorAll('.fereastra-overlay:not(.fundal) #pcf-lista > *').length > 5", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    pg.wait_for_timeout(1500)
    return True


def _w_analitica(pg, parcurs):
    """Analitică stoc F1: Stocuri › «Mișcări, fișe de magazie, coduri, nivel minim» › «Analitică stoc» (cardul `.pf-card[data-zona-derulare]` în `#cv-loc-zona`)."""
    if not _card(pg, parcurs, F1, "#fa-stocuri", "#cv-toggle"):
        return False
    try:
        pg.click(TOP + "#cv-toggle", timeout=10000)
        pg.wait_for_selector(TOP + "#cv-ana", state="attached", timeout=30000)
        pg.click(TOP + "#cv-ana", timeout=10000)
        pg.wait_for_selector(TOP + "#cv-loc-zona .pf-card[data-zona-derulare]", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(2000)
    return True


def _w_solduri(pg, parcurs):
    """Import date — Solduri inițiale F1: fișierul solduri_17_5_K.csv (antet și două conturi) încărcat; așteptarea previzualizării `.mig-prev-cutie`."""
    if not _card(pg, parcurs, F1, "#fa-import"):
        return False
    try:
        pg.locator(TOP + "button", has_text="Solduri inițiale").first.click(timeout=15000)
        pg.wait_for_selector(TOP + "#mig-file", state="attached", timeout=20000)
        pg.set_input_files(TOP + "#mig-file", SOLDURI_CSV)
        pg.wait_for_selector(TOP + ".mig-prev-cutie", state="attached", timeout=30000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(2000)
    return True


def _w_operatie(pg, parcurs, firma, cheie, tip=None):
    """Operațiuni speciale `firma` › formularul operațiunii `cheie` (`button[data-op]`), cu tipul ales dacă e dat."""
    if not _card(pg, parcurs, firma, "#fa-operatiuni"):
        return False
    try:
        pg.wait_for_selector(TOP + "button[data-op='%s']" % cheie, state="attached", timeout=25000)
        pg.click(TOP + "button[data-op='%s']" % cheie, timeout=10000)
        pg.wait_for_selector(TOP + "#op-trimite", state="attached", timeout=20000)
        if tip:
            pg.wait_for_function("(v) => [...(document.querySelector('.fereastra-overlay:not(.fundal) #op-tip') || {options: []}).options].some((o) => o.value === v)", arg=tip, timeout=20000)
            pg.select_option(TOP + "#op-tip", tip)
            pg.dispatch_event(TOP + "#op-tip", "change")
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(2000)
    return True


def _w_certificat(pg, parcurs):
    """Certificat CM F5: Salariați › fișa lui Ionescu Vasile › Concediu medical › «+ Certificat nou»."""
    if not _card(pg, parcurs, F5, "#fa-salariati", "#sp-contare"):
        return False
    for incercare in range(4):
        try:
            pg.wait_for_selector(TOP + "#sp-tabel tbody tr.sp-rand", timeout=12000)
            break
        except Exception:   # noqa: BLE001
            if incercare == 3:
                return False
            try:
                pg.click(TOP + "#sp-prev", timeout=5000)
            except Exception:   # noqa: BLE001
                return False
            pg.wait_for_timeout(1500)
    try:
        rand = pg.locator(TOP + "#sp-tabel tbody tr.sp-rand").filter(has_text="Ionescu")
        if not rand.count():
            return False
        rand.first.locator(".sp-deschide").click(timeout=10000)
        pg.wait_for_selector(TOP + "#ss-butoane", timeout=30000)
        pg.locator(TOP + "#ss-butoane button", has_text="Concediu medical").first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#cm-nou", timeout=20000)
        pg.click(TOP + "#cm-nou", timeout=10000)
        pg.wait_for_selector(TOP + "#cm-calc", state="attached", timeout=20000)
    except Exception:   # noqa: BLE001
        return False
    pg.wait_for_timeout(2000)
    return True


def _zona(pg):
    """Măsurile zonei ferestrei de sus (JS_DERULARI din e2e_pilot_x06.py): zona, corpul, locurile de derulare și `loc` (locul de derulare utilizabil: zona vizibilă dacă derulează, altfel corpul); None dacă nu e fereastră."""
    pg.wait_for_timeout(900)
    d = pg.evaluate(JS_DERULARI)
    if not d or not d.get("fereastra"):
        return None
    z = d["zone"][0] if d["zone"] else None
    loc = z["inaltime"] if z and z["continut"] > z["inaltime"] + 2 else d["corpInaltime"]
    return {"zona": z["inaltime"] if z else None, "continut_zona": z["continut"] if z else None, "corp": d["corpInaltime"], "derulante": d["derulante"], "n_derulante": len(d["derulante"]),
            "zone": d["zone"], "loc": loc}


def _criteriu_zona(m):
    """Criteriul de zonă (Definiții): cel mult un loc de derulare verticală ȘI, cu zonă vizibilă, zona ≥ 0,4 × corpul sau fără derulare; fără zonă vizibilă, singurul loc de derulare e corpul. -> lista motivelor de pică."""
    rele = []
    if m["n_derulante"] > 1:
        rele.append("%d locuri de derulare (%s)" % (m["n_derulante"], ", ".join(m["derulante"])))
    if m["zone"]:
        for z in m["zone"]:
            if not (z["inaltime"] >= 0.4 * m["corp"] or z["inaltime"] >= z["continut"]):
                rele.append("zona %s are %s px din %s px ai corpului (sub 40%%, derulează %s px)" % (z["loc"], z["inaltime"], m["corp"], z["continut"]))
    elif any(not d.startswith("div.fereastra-corp") for d in m["derulante"]):
        rele.append("fără zonă vizibilă, dar locul de derulare nu e corpul (%s)" % ", ".join(m["derulante"]))
    return rele


def test_ferestre_17_5_K(browser, capsys):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    rele, verdicte = [], {}

    def out(linie):
        with capsys.disabled():
            print(linie)

    def verdict(id_, ok, text):
        verdicte[id_] = (ok, text)
        if not ok:
            rele.append("%s: %s" % (id_, text))

    b = browser.new_context(viewport={"width": R3[0], "height": R3[1]})
    try:
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)

        # f.1 — cabinetul la 1366×768: cardul «Control fiscal» (invariantă față de lot)
        pg.set_viewport_size({"width": R3[0], "height": R3[1]})
        _acasa(pg)
        t = _norm(pg.evaluate("() => { const m = document.querySelector('main'); return m ? m.textContent : ''; }"))
        verdict("f.1", "Control fiscal" in t, "pagina cabinetului 1366×768 %s «Control fiscal» (text de %d caractere)" % ("conține" if "Control fiscal" in t else "NU conține", len(t)))

        # a.1 — AC019: Sinteza zilei, «Ultimele evenimente», 603×590: «Vezi tot» pe un singur rând
        pg.set_viewport_size({"width": R1[0], "height": R1[1]})
        _acasa(pg)
        randuri = None
        try:
            pg.click("button.cab-card:has([data-cheie='brief'])", timeout=15000)
            pg.wait_for_selector(TOP + ".sa-cap-rand button[data-ecran='activitate']", state="attached", timeout=30000)
            pg.wait_for_timeout(2000)
            randuri = pg.evaluate(JS_RANDURI, ".sa-cap-rand button[data-ecran='activitate']")
        except Exception:   # noqa: BLE001
            pass
        verdict("a.1", randuri == [1], "Sinteza zilei 603×590, «Vezi tot»: rânduri de text = %s (așteptat [1])" % (randuri if randuri is not None else "fereastra sau butonul nu s-au deschis"))

        # a.2 — AC043: e-Transport F1, 603×590: filele pe un singur rând, înălțime 24–40 px
        pg.set_viewport_size({"width": R1[0], "height": R1[1]})
        deschis = _card(pg, parcurs, F1, "#fa-etransport", ".rap-tabs .rap-tab")
        randuri = pg.evaluate(JS_RANDURI, ".rap-tabs .rap-tab") if deschis else None
        inalt = pg.evaluate(JS_INALTIMI, ".rap-tabs .rap-tab") if deschis else None
        ok = deschis and randuri == [1, 1, 1, 1] and bool(inalt) and len(inalt) == 4 and all(24 <= h <= 40 for h in inalt)
        verdict("a.2", ok, "e-Transport F1 603×590, filele: rânduri de text = %s (așteptat [1, 1, 1, 1]), înălțimi = %s px (așteptat 24–40)" % (randuri, inalt) if deschis else "e-Transport F1 nu s-a deschis")

        # a.3 — AC057: Control fiscal (firmă) F1, 603×590, rândul D406 01/2026: «Modifică marcarea» / «Anulează marcarea» pe un rând, 20–30 px, nimic ieșit din fereastră
        deschis = _card(pg, parcurs, F1, "#fa-control", ".cf-grup-titlu")
        sel_btn = "tr:has(.cf-extern-anuleaza) :is(.cf-extern-btn, .cf-extern-anuleaza)"
        grup_inainte = False
        if deschis and not pg.locator(TOP + ".cf-extern-anuleaza").count():   # rândul stă în grupul «Înainte de preluare»: fereastra lui se deschide din «Vezi declarațiile»
            try:
                pg.click(TOP + ".cf-inainte-btn", timeout=10000)
                pg.wait_for_selector(TOP + ".cf-extern-anuleaza", state="attached", timeout=20000)
                grup_inainte = True
            except Exception:   # noqa: BLE001
                pass
        pg.wait_for_timeout(1000)
        randuri = pg.evaluate(JS_RANDURI, sel_btn) if deschis else None
        inalt = pg.evaluate(JS_INALTIMI, sel_btn) if deschis else None
        iesite = pg.evaluate(JS_IESITE) if deschis else None
        out("MASURA control_fiscal_D406_01_2026 603x590 grup=%s randuri=%s inaltimi=%s iesite=%s" % ("inainte_de_preluare (fereastra «Vezi declarațiile»)" if grup_inainte else "in fereastra Control fiscal", randuri, inalt, iesite))
        ok = deschis and randuri == [1, 1] and bool(inalt) and len(inalt) == 2 and all(20 <= h <= 30 for h in inalt) and iesite == []
        verdict("a.3", ok, "Control fiscal F1 603×590, rândul D406 01/2026: rânduri de text = %s (așteptat [1, 1]), înălțimi = %s px (așteptat 20–30), iesite = %s (așteptat [])" % (randuri, inalt, iesite) if deschis else "Control fiscal F1 nu s-a deschis")

        # a.4–a.7 + criteriul de zonă — cele patru ferestre ale lui (5), la cele trei rezoluții, fiecare măsurare pe o fereastră deschisă proaspăt
        ferestre = (("Rapoarte comerciale F1", _w_rapoarte), ("Plan de conturi F1", _w_plan), ("Analitică stoc F1", _w_analitica), ("Import date — Solduri inițiale F1", _w_solduri))
        zone_ok = {}
        for nume, deschide in ferestre:
            for (w, h) in REZOLUTII:
                pg.set_viewport_size({"width": w, "height": h})
                m = _zona(pg) if deschide(pg, parcurs) else None
                if m is None:
                    out("MASURA %s %dx%d fereastra nu s-a deschis" % (nume, w, h))
                    rele.append("criteriu de zonă %s %dx%d: fereastra nu s-a deschis" % (nume, w, h))
                    zone_ok[(nume, (w, h))] = None
                    continue
                out("MASURA %s %dx%d zona=%s corp=%s derulante=%d loc=%s" % (nume, w, h, m["zona"] if m["zona"] is not None else "-", m["corp"], m["n_derulante"], m["loc"]))
                zone_ok[(nume, (w, h))] = m
                motive = _criteriu_zona(m)
                if motive:
                    rele.append("criteriu de zonă %s %dx%d (zona=%s corp=%s loc=%s): %s" % (nume, w, h, m["zona"], m["corp"], m["loc"], "; ".join(motive)))
        for nume, rez in PRAG_LOC:
            m = zone_ok.get((nume, rez))
            prag = PRAG_LOC[(nume, rez)]
            verdict(ID_AN[nume], m is not None and m["loc"] >= prag, "%s %dx%d: loc = %s px (așteptat ≥ %d; zona=%s, corp=%s, derulante=%s)" % (
                nume, rez[0], rez[1], m["loc"] if m else "fereastra nu s-a deschis", prag, m["zona"] if m else "-", m["corp"] if m else "-", m["derulante"] if m else "-"))

        # a.8 + a.9 — AC102: Mijloace fixe — Leasing F1, «Primire bun», 1366×603
        # a.10 + a.11 — AC111: Certificat CM F5, Certificat nou pentru Ionescu Vasile, 1366×768
        # a.12 — AC102: Chirii / comodat / refacturări F2, 1366×603
        formulare = (("Mijloace fixe — Leasing F1", R2, "#op-renunta", lambda: _w_operatie(pg, parcurs, F1, "leasing", "primire"), "a.8", "a.9"),
                     ("Certificat CM F5 — Certificat nou", R3, "#cm-renunta", lambda: _w_certificat(pg, parcurs), "a.10", "a.11"),
                     ("Chirii / comodat / refacturări F2", R2, "#op-renunta", lambda: _w_operatie(pg, parcurs, F2, "chirie"), "a.12", None))
        for nume, (w, h), buton, deschide, id_pozitie, id_acoperit in formulare:
            pg.set_viewport_size({"width": w, "height": h})
            deschis = deschide()
            bara = ".bara-fixa:has(%s)" % buton
            poz = pg.evaluate(JS_POZITIE, bara) if deschis else None
            verdict(id_pozitie, poz == "static", "%s %dx%d: `position` calculat al `%s` = %s (așteptat static)" % (nume, w, h, bara, poz if deschis else "formularul nu s-a deschis"))
            r = pg.evaluate(JS_RENUNTA, buton) if deschis else None
            if r:
                out("MASURA renunta %s %dx%d vizibil=%s in_corp=%s inaltime=%s latime=%s padding_stanga=%s" % (nume, w, h, r["vizibil"], r["in_corp"], r["h"], r["w"], r["pad"]))
            if not r or not r["vizibil"] or not r["in_corp"] or r["text"] != "Renunță":
                rele.append("Renunță (fără id) %s %dx%d: butonul «Renunță» nu e vizibil în corp (%s)" % (nume, w, h, r))
            elif buton == "#op-renunta" and (r["h"] != 44 or r["pad"] != "20px"):
                rele.append("Renunță (fără id) %s %dx%d: dimensiunea butonului e %s px înălțime și %s padding stânga (așteptat 44 px și 20px, stil.css #op-renunta)" % (nume, w, h, r["h"], r["pad"]))
            a = pg.evaluate(JS_ACOPERITE, bara) if deschis else None
            if a:
                out("MASURA acoperit %s %dx%d campuri=%d acoperite=%d bara_sus=%s" % (nume, w, h, a["campuri"], len(a["acoperite"]), a["bara_sus"]))
                if a["acoperite"]:
                    out("ACOPERITE %s %dx%d: %s" % (nume, w, h, "; ".join(a["acoperite"][:6])))
                if a["piese_lipsa"]:
                    out("PIESE_LIPSA %s %dx%d: %s" % (nume, w, h, "; ".join(a["piese_lipsa"])))
            if id_acoperit:
                verdict(id_acoperit, bool(a) and a["campuri"] > 0 and not a["acoperite"] and not a["piese_lipsa"], "%s %dx%d: câmpuri acoperite = %s din %s; surse fără piesa vizibilă = %s (așteptat 0 acoperite, 0 surse fără piesă, cel puțin un câmp vizibil)" % (
                    nume, w, h, len(a["acoperite"]) if a else "formularul nu s-a deschis", a["campuri"] if a else "-", ", ".join(a["piese_lipsa"]) if a else "-"))

        # a.13 + f.3 — AC020: Declarații F1 pasul 1 deschisă la 1366×768, fereastra browserului redusă la 603×590 FĂRĂ reîncărcare, apoi readusă la 1366×768 (tot fără reîncărcare)
        pg.set_viewport_size({"width": R3[0], "height": R3[1]})
        deschis = _card(pg, parcurs, F1, "#fa-declaratii", "#dec-continua")
        ph = {}
        if deschis:
            for eticheta, (w, h) in (("initial", R3), ("ingust", R1), ("readus", R3)):
                pg.set_viewport_size({"width": w, "height": h})
                pg.wait_for_timeout(1000)
                try:
                    ph[eticheta] = pg.get_attribute(TOP + "#cautare-fereastra", "placeholder", timeout=5000)
                except Exception:   # noqa: BLE001
                    ph[eticheta] = None
            out("MASURA placeholder #cautare-fereastra initial(1366x768)=%r ingust(603x590)=%r readus(1366x768)=%r" % (ph["initial"], ph["ingust"], ph["readus"]))
        verdict("a.13", deschis and ph.get("ingust") == PLACEHOLDER_SCURT, "Declarații F1 pasul 1, după redimensionarea 1366×768 → 603×590 fără reîncărcare: placeholder = %r (așteptat %r)" % (ph.get("ingust") if deschis else "fereastra nu s-a deschis", PLACEHOLDER_SCURT))
        verdict("f.3", deschis and ph.get("readus") == PLACEHOLDER_LUNG, "Declarații F1 pasul 1, după readucerea la 1366×768 fără reîncărcare: placeholder = %r (așteptat %r)" % (ph.get("readus") if deschis else "fereastra nu s-a deschis", PLACEHOLDER_LUNG))

        # f.2 — Plan de conturi F1 la 1366×768 conține «Adaugă analitic» (invariantă față de lot)
        pg.set_viewport_size({"width": R3[0], "height": R3[1]})
        deschis = _w_plan(pg, parcurs)
        t = _norm(pg.evaluate("() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); return e ? e.textContent : ''; }")) if deschis else ""
        verdict("f.2", "Adaugă analitic" in t, "Plan de conturi F1 1366×768: corpul ferestrei %s «Adaugă analitic» (text de %d caractere)" % ("conține" if "Adaugă analitic" in t else "NU conține", len(t)))
    finally:
        b.close()
        for id_ in ID_URI:
            ok, text = verdicte.get(id_, (False, "neexecutat"))
            out("VERDICT %s %s — %s" % (id_, "trece" if ok else "pica", text))
    assert not rele, "ferestre 17.5-K: %s" % "; ".join(rele)
