"""17.5-F6 · proba REAL a arhitectului (Claude, 27.11.2026, fișa 17.5-F6), pe copia oficială 8019. Varianta nominală F6 a probei calificate la
17.5-F5 (e2e_fundatie_17_5_F5.py, 8748c291…, reper înghețat): aceleași opt criterii e.1–e.8, neschimbate, și e.9 pentru pagina cabinetului.
Baza: publicarea 17.5-C9 (6ad08381ec8f5ec3930f01cbb99be3d418b775eb). Candidatul: 17.5-F6 (continuarea lui 17.5-F5). Contul de probă al cabinetului, ceasul fixat la MOMENT_REF.

Date de probă (D2), puse de test numai după citirea premiselor și scoase la final, inclusiv la o întrerupere în pregătire; rulatorul nativ
restaurează și iconta_test:
  - pe F2, în soldurile de preluare, 1171 creditor 100.000 lei (rând nou) și 5121 debitor de la 5.000 la 105.000 lei;
  - cursul BNR EUR din 31.12.2025, 5,0985, pus numai dacă lipsește; un curs preexistent diferit oprește proba înaintea oricărei scrieri.
  e.1 F2 · Decontări asociați · dividend T1: firma, formularul și propunerea (2 asociați 60/40; brut 30.000/20.000; impozit 4.800/3.200;
      net 25.200/16.800; total 50.000/8.000/42.000), din contul 1171, cu hotărârea nr. 1 din 15.03.2026.
  e.2 în același formular, butoanele „Descarcă Word” și „Descarcă PDF”; ambele documente, recitite ca OOXML și ca PDF, au firma, hotărârea,
      rândul fiecărui asociat pe coloane și totalurile T1; descărcarea nu creează note.
  e.3 F1 · fereastra firmei: firma, rolul admin_firma al contului de probă, accesul la F1, grupul „Contabilitate” deschis.
  e.4 ultimul card al grupului este „Consultanță fiscală”; fereastra F1 arată M1–M5 cu stările prezise de date și de comandă;
      M4: 509.850,00 lei = 100.000 € × 5,0985, pentru 2026.
  e.5 F1 · Bancă: firma, titlul „Bancă”, martorul „Importă extras” și nivelul ferestrei în stiva navigatorului.
  e.6 AC202: un singur semn, title = aria-label = „Ajutor: Bancă”; un clic deschide o singură fereastră nouă (nivelul crește cu unu) cu
      secțiunile F012, F011, F073; ✕ revine în aceeași Bancă, redeschiderea arată același ajutor, Esc revine în Bancă.
  e.7 F1 · Control fiscal la 603×590: octombrie, septembrie, revenirea în octombrie, apoi Declarații D394 octombrie; patru etape, o dată, în ordine.
  e.8 „▾ detalii”: cele opt perechi ale pct. 18, fiecare legată de ținta observată și de modulul ds_piese.js încărcat în documentul ei.
  e.9 pagina cabinetului, contul de probă cu firme: după cele șase carduri de sus și secțiunea șefului (dacă se desenează) stă, ultima, o
      singură secțiune pliabilă „Consultanță”, pliată la deschidere; desfăcută arată exact două carduri, „Hotărâri AGA” (501) și
      „Consultanță fiscală” (502), în această ordine, fiecare cu rândul lui de rezumat; se pliază la loc. Nicio cheie de consultanță în
      grila de sus sau în secțiunea șefului (comanda F5, Cabinet 1–4 și 7; comanda F6, pct. 4). Pagina nedesenată sau sesiunea greșită
      opresc proba (NEEXECUTAT), nu dau un roșu.
Contractele ecranelor noi (e.2, e.4, e.6) sunt în decizii_17_5_F5.txt, D4–D6, preluate în decizii_17_5_F6.txt; contractul e.9 e în D11.
Analiza e aici; cititorul recitește fișierele și o reia.
"""

import csv
import hashlib
import io
import json
import posixpath
import re
import time
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit

LOT = "17_5_F6"
IDS = ("e.1", "e.2", "e.3", "e.4", "e.5", "e.6", "e.7", "e.8", "e.9")
DIM = ((1366, 768), (603, 590))
DIM_DETALII = ((603, 590),)
DIM_ID = {i: (DIM_DETALII if i in ("e.7", "e.8") else DIM) for i in IDS}
CONT_PROBA = "dovada.71507@sesiuneab.test"
ROL_PROBA = "admin_firma"
F1 = "F1 Comert Stoc SRL"
F2 = "F2 Profit Amortizare SRL"
TOP = ".fereastra-overlay:not(.fundal) "
MODUL = re.compile(r"/static/js/ds_piese\.js(?:\?|$)")

T1_FORMULAR = (("data", "2026-03-15"), ("brut", "50000"), ("numar_hotarare", "1"), ("data_hotarare", "2026-03-15"))
T1_ASOCIATI = (("Ion Test", "60", "30000.00", "4800.00", "25200.00"), ("Maria Test", "40", "20000.00", "3200.00", "16800.00"))
T1_TOTAL = ("50000.00", "8000.00", "42000.00")
HOTARARE = re.compile(r"\bnr\.?\s*1\s+din\s+15\.03\.2026\b")
SOLD_T1 = (("1171", "Rezultatul reportat (probă REAL 17.5-F6, T1)", Decimal("0.00"), Decimal("100000.00")),
           ("5121", None, Decimal("100000.00"), Decimal("0.00")))
PREMISE_SOLD = {"1171": None, "5121": (Decimal("5000.00"), Decimal("0.00"))}
CURS_EUR = ("2025-12-31", "EUR", Decimal("5.0985"))
PLAFON_LEI, AN_PLAFON = Decimal("509850.00"), "2026"

# D4 · contractul 501 (e.2)
DOC_CAMPURI = (("op-aprobare_anuala", "da"), ("op-an_situatii", "2025"), ("op-termen_plata", "2026-04-15"),
               ("op-modalitate_plata", "virament"), ("op-loc_adunare", "sediul societății"),
               ("op-convocare", "convocarea administratorului din 01.03.2026"), ("op-prezenta", "toti"), ("op-vot", "unanimitate"))
ADMIN_IMPLICIT = "Popescu Petru"   # reprezentantul legal din profilul F2 pe copie; folosit numai dacă formularul nu propune nimic
EXEMPLARE_F2 = "3"
BUTOANE = (("docx", "#op-descarca-docx", "Descarcă Word"), ("pdf", "#op-descarca-pdf", "Descarcă PDF"))
COLOANE = (("nume", "asociat"), ("cota", "cota"), ("brut", "brut"), ("impozit", "impozit"), ("net", "net"))
# D5 · contractul 502 (e.4)
CARD_502, TITLU_502 = "fa-consultanta", "Consultanță fiscală"
MASURI = (("M1", "Salariu sau dividende"), ("M2", "Beneficii pentru salariați"), ("M3", "Sponsorizări"), ("M4", "Plafonul micro"),
          ("M5", "Profit reinvestit"))
STARI = ("Se aplică", "Nu se aplică", "Lipsesc date", "Lipsesc date — temei neverificat")
# F1: micro, 3 salariați, niciun asociat înregistrat (anexa cifre_snapshot). M1 fără asociat: «Lipsesc date» (pct. 8 și 10); M3 pe micro: «Nu se
# aplică» (pct. 12); M5 pe micro: «Nu se aplică» (pct. 14); M4 pe micro nu poate fi «Nu se aplică» (pct. 13); M2 rămâne nejudecat de date.
PREDICTIE_F1 = {"M1": ("Lipsesc date",), "M2": STARI, "M3": ("Nu se aplică",), "M4": ("Se aplică", "Lipsesc date", "Lipsesc date — temei neverificat"),
                "M5": ("Nu se aplică",)}
# D6 · contractul AC202 (e.6)
AJUTOR_BANCA, ORDINE_BANCA, SEMNE_BAZA = "Ajutor: Bancă", ("F012", "F011", "F073"), ("F011", "F012", "F073")
GENERIC = ("Ce face și cum se folosește", "Ajutor")
# D11 · contractul secțiunii „Consultanță” a cabinetului (e.9)
DIRECTE = ("validat", "control", "termene", "firme", "brief", "setari")   # cele șase carduri de sus (ORDINE_CABINET, e2e_bloc_a.py)
SEF = "fgc-sef"
CHEI_CONS = ("hotarari_aga", "consultanta")   # 501, 502 — cheile din comanda F6, pct. 4
TITLURI_CONS = ("Hotărâri AGA", "Consultanță fiscală")
TITLU_SECTIUNE = re.compile(r"consultanță(?: · ([1-9][0-9]*) (?:de )?firm(?:ă|e))?")   # „CONSULTANȚĂ · N firme”; la zero, numai „CONSULTANȚĂ”
ID_DOM = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
# e.7/e.8 · pct. 18
ETAPE = (("10", None), ("10→09", "2026-9"), ("10→09→10", "2026-10"))
ORDINE_ETAPE = ("10", "10→09", "10→09→10", "Declarații")
SELECTOR = {"la deschidere": "2026-10", "2026-9": "2026-9", "2026-10": "2026-10"}
TINTE = {"10": ("semnal", "Statul de plată", "SPV"), "10→09": ("SPV",), "10→09→10": ("semnal", "Statul de plată", "SPV"),
         "Declarații": ("avertisment",)}
ABSENTE = {"10→09": ("semnal", "Statul de plată")}
PERECHI = tuple((e, t) for e in ORDINE_ETAPE for t in TINTE[e])
DESCHIS, INCHIS = ["true", False, True, "▴ detalii"], ["false", True, False, "▾ detalii"]
PROFIL_BAZA = {("10", "semnal"): ((1, "deschis"), (1, "închis")), ("10", "Statul de plată"): ((1, "deschis"), (1, "închis")),
               ("10", "SPV"): ((2, "închis"), (2, "închis")), ("10→09", "SPV"): ((3, "deschis"), (3, "închis")),
               ("10→09→10", "semnal"): ((2, "închis"), (2, "închis")),
               ("10→09→10", "Statul de plată"): ((2, "închis"), (2, "închis")),
               ("10→09→10", "SPV"): ((3, "deschis"), (3, "închis")), ("Declarații", "avertisment"): ((1, "deschis"), (1, "închis"))}

STABIL = """() => new Promise((ok, rau) => { const t = setTimeout(() => rau(Error('pagina nedesenata')), 3000);
  requestAnimationFrame(() => requestAnimationFrame(() => { clearTimeout(t); ok(); })); })"""
TXT = "const txt = e => (e ? e.textContent.replace(/\\s+/g, ' ').trim() : null);"
VIZ = "const viz = e => !!e && e.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) && e.getClientRects().length > 0;"
# Textul redat pe care utilizatorul îl poate vedea, citit literă cu literă. O literă contează numai dacă e redată vizibil (vizibilitate CSS,
# opacitate, culoare netransparentă, dreptunghi nenul) și dacă rămâne în porțiunea afișabilă a fiecărui strămoș care taie conținutul: la
# overflow hidden/clip trebuie să stea, cel puțin pe jumătate, în cutia strămoșului (iar unde textul e prescurtat cu puncte de suspensie,
# întreagă înaintea lor); la overflow auto/scroll se calculează unde poate ajunge efectiv litera prin derulare (cursa reală a zonei: fără
# cursă, zona taie ca overflow hidden), iar pozițiile astfel atinse se verifică mai departe la fiecare strămoș; la capăt, fereastra
# navigatorului (sau documentul, dacă se derulează). Literele redate, dar care nu se văd, lasă în text semnul MARCA_TAIAT, deci textul citit nu mai e cel
# complet; conținutul neredat deloc (display:none) nu lasă nimic, ca pe ecran. Spațiile sunt cele redate: fragmentele alăturate dintr-un rând
# (de exemplu «20» și «26» cu altă formatare) se lipesc, iar blocurile și întreruperile de rând despart cuvintele.
MARCA_TAIAT = "⟦tăiat⟧"
VTXT = r"""const vtxt = e => { if (!e) return null;
  const de = document.documentElement, MARCA = '⟦tăiat⟧', out = [];
  const seg = (typeof Intl !== 'undefined' && Intl.Segmenter) ? new Intl.Segmenter(undefined, {granularity: 'grapheme'}) : null;
  const litere = s => { if (seg) return [...seg.segment(s)].map(x => [x.index, x.segment]); const v = []; let i = 0;
    for (const ch of s) { v.push([i, ch]); i += ch.length; } return v; };
  const pune = s => { if (s !== MARCA || out[out.length - 1] !== MARCA) out.push(s); };
  let panza = null;
  const puncte = c => { try { panza = panza || document.createElement('canvas').getContext('2d'); panza.font = c.font || (c.fontSize + ' ' + c.fontFamily);
    const w = panza.measureText('…').width; return w > 0 ? w : parseFloat(c.fontSize) || 0; } catch (x) { return parseFloat(c.fontSize) || 0; } };
  const lant = p => { const v = []; let fix = false, taiat = false;   // strămoșii care taie conținutul, de la text în sus
    for (let x = p; x && x.nodeType === 1 && x !== de && x !== document.body; x = x.parentElement) { const c = getComputedStyle(x);
      if (c.position === 'fixed') fix = true;
      const ox = c.overflowX, oy = c.overflowY; if (ox === 'visible' && oy === 'visible') continue;
      if (x.clientWidth < 1 || x.clientHeight < 1) { taiat = true; break; }
      const ascuns = o => o === 'hidden' || o === 'clip';
      if (ascuns(oy) && c.webkitLineClamp && c.webkitLineClamp !== 'none' && x.scrollHeight > x.clientHeight + 1) { taiat = true; break; }   // rânduri prescurtate
      const q = x.getBoundingClientRect(), L = q.left + x.clientLeft, T = q.top + x.clientTop;
      v.push({ox, oy, L, T, R: L + x.clientWidth, B: T + x.clientHeight, sl: x.scrollLeft, sw: x.scrollWidth, st: x.scrollTop, sh: x.scrollHeight, cw: x.clientWidth, ch: x.clientHeight,
              elipsa: ascuns(ox) && c.textOverflow !== 'clip' && x.scrollWidth > x.clientWidth + 1 ? puncte(c) : 0, rtl: c.direction === 'rtl'}); }
    return {v, fix, taiat}; };
  // O axă a unui strămoș care taie. Litera are lățimea w, iar marginea ei de început poate ajunge, prin derulările de până aici, oriunde în
  // [lo, hi]; [A, Z] e cutia strămoșului. Întoarce pozițiile în care litera se vede în cutie sau null.
  const axa = (o, lo, hi, w, A, Z, derulat, total, cutie, elipsa, rtl) => {
    if (o === 'visible') return [lo, hi];
    const cursa = (o === 'auto' || o === 'scroll') ? Math.max(0, total - cutie) : 0;
    if (cursa > 0.5) { const u = Math.max(lo + derulat - cursa, A - 0.5), v = Math.min(hi + derulat, Z - w + 0.5); return u <= v ? [u, v] : null; }   // cât ajunge efectiv prin derulare
    if (elipsa) { const u = Math.max(lo, (rtl ? A + elipsa : A) - 0.5), v = Math.min(hi, (rtl ? Z : Z - elipsa) - w + 0.5); return u <= v ? [u, v] : null; }   // întreagă, înaintea punctelor de suspensie
    const u = Math.max(lo, A - w / 2), v = Math.min(hi, Z - w / 2); return (u <= v && Z > A) ? [u, v] : null; };   // tăiere (și zonă derulabilă fără cursă): cel puțin jumătate în cutie
  const derulabil = a => ![getComputedStyle(de)['overflow' + a], getComputedStyle(document.body)['overflow' + a]].some(o => o === 'hidden' || o === 'clip');
  const vede = (g, ln) => { let reg = [...g.getClientRects()].filter(r => r.width > 0 && r.height > 0).map(r => ({xl: r.left, xh: r.left, w: r.width, yl: r.top, yh: r.top, h: r.height}));
    for (const s of ln.v) { if (!reg.length) return false;
      reg = reg.map(r => { const x = axa(s.ox, r.xl, r.xh, r.w, s.L, s.R, s.sl, s.sw, s.cw, s.elipsa, s.rtl), y = axa(s.oy, r.yl, r.yh, r.h, s.T, s.B, s.st, s.sh, s.ch, 0, false);
        return x && y ? {xl: x[0], xh: x[1], w: r.w, yl: y[0], yh: y[1], h: r.h} : null; }).filter(Boolean); }
    const fer = (lo, hi, m, lat, poz, tot, a) => { const c = (!ln.fix && derulabil(a)) ? Math.max(0, tot - lat) : 0; return hi + poz > -m && lo + poz - c < lat; };   // fereastra, cu derularea documentului
    return reg.some(r => fer(r.xl, r.xh, r.w, innerWidth, scrollX, de.scrollWidth, 'X') && fer(r.yl, r.yh, r.h, innerHeight, scrollY, de.scrollHeight, 'Y')); };
  const text = n => { const p = n.parentElement, s = n.nodeValue || ''; if (!p || !s) return;
    if (!/\S/.test(s)) { pune(' '); return; }
    const col = getComputedStyle(p).color.match(/rgba\(([^)]+)\)/);
    if (!p.checkVisibility({checkOpacity: true, checkVisibilityCSS: true}) || (col && parseFloat(col[1].split(',')[3]) === 0)) { pune(MARCA); return; }
    const ln = lant(p); if (ln.taiat) { pune(MARCA); return; }
    const g = document.createRange();
    for (const [i, ch] of litere(s)) { if (!/\S/.test(ch)) { pune(' '); continue; }
      g.setStart(n, i); g.setEnd(n, i + ch.length); pune(vede(g, ln) ? ch : MARCA); } };
  const umbla = (n, radacina) => { if (n.nodeType === 3) { text(n); return; } if (n.nodeType !== 1) return;
    if (n.tagName === 'BR') { pune(' '); return; }
    const d = getComputedStyle(n).display; if (d === 'none' && !radacina) return;
    const bloc = !(d.startsWith('inline') || d === 'contents' || d === 'ruby' || d === 'ruby-text');
    if (bloc) pune(' '); for (const c of n.childNodes) umbla(c, false); if (bloc) pune(' '); };
  umbla(e, true);
  return out.join('').replace(/\s+/g, ' ').trim(); };"""
SUS = "const top = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop();"
JS_STIVA = "() => {" + TXT + """
  const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')], t = o.length ? o[o.length - 1] : null;
  const f = t ? t.querySelector('.fereastra') : null;
  return {active: o.length, nivel: t ? (t.dataset.nivel === undefined ? null : t.dataset.nivel) : null,
          antet: f ? txt(f.querySelector('.fereastra-antet, header')) : null, h2: f ? txt(f.querySelector('h2.pf-titlu')) : null}; }"""
JS_DIVIDEND = "() => {" + SUS + TXT + VIZ + """
  if (!top) return null;
  const t = top.querySelector('#op-div-tabel'), op = top.querySelector('#op-operatie');
  const btn = s => { const b = top.querySelector(s);
    return b ? {exista: true, vizibil: viz(b), text: txt(b), acelasi_formular: !!op && b.closest('.pf-frand') === op.closest('.pf-frand')} : {exista: false}; };
  const generice = [...top.querySelectorAll('button, a')].filter(b => /Descarc/i.test(b.textContent || '') && /(Word|PDF)/.test(b.textContent || ''))
    .map(b => ({id: b.id || null, text: txt(b)}));
  return {antet: txt(top.querySelector('.fereastra-antet, header')), titlu: txt(top.querySelector('h2.pf-titlu')),
          operatie: op ? op.value : null, tabel_vizibil: viz(t),
          randuri: t ? [...t.querySelectorAll('tbody tr')].map(r => [...r.querySelectorAll('td')].map(txt)) : null,
          total: t ? [...t.querySelectorAll('tfoot td')].map(txt) : null, zona: txt(top.querySelector('#op-propunere')),
          butoane: {docx: btn('#op-descarca-docx'), pdf: btn('#op-descarca-pdf')}, butoane_descarcare: generice};
}"""
JS_VALORI = "(ids) => {" + SUS + """
  const out = {}; for (const i of ids) { const e = top ? top.querySelector('#' + i) : null; out[i] = e ? e.value : null; } return out; }"""
JS_MENIU = "() => {" + SUS + TXT + VIZ + """
  if (!top) return null;
  const g = top.querySelector('#fg-contabilitate'), c = top.querySelector('#fgc-contabilitate');
  const b = g ? g.querySelector('button.firme-grup-btn') : null;
  return {antet: txt(top.querySelector('.fereastra-antet, header')), titlu: txt(top.querySelector('h2.pf-titlu')), grup: txt(g),
          deschis: b ? b.getAttribute('aria-expanded') : null, grup_vizibil: viz(c),
          carduri: c ? [...c.querySelectorAll('button.firme-optiune')].map(x => ({id: x.id || null, titlu: txt(x.querySelector('.firme-optiune-titlu')),
                                                                                 vizibil: viz(x), activ: !x.disabled})) : null,
          id_502_in_fereastra: !!top.querySelector('#fa-consultanta'),
          titlu_502_in_fereastra: [...top.querySelectorAll('.firme-optiune-titlu')].filter(x => txt(x) === 'Consultanță fiscală').length};
}"""
JS_CONSULTANTA = "() => {" + SUS + TXT + VIZ + VTXT + """
  if (!top) return null;
  return {antet: txt(top.querySelector('.fereastra-antet, header')), titlu: txt(top.querySelector('h2.pf-titlu')),
          randuri: [...top.querySelectorAll('[data-masura]')].map(r => { const vv = [...r.querySelectorAll('[data-valoare="plafon_lei"]')],
            pp = [...r.querySelectorAll('[data-perioada="plafon_lei"]')],
            mo = r.querySelector('[data-masura-motiv]'), n = r.querySelector('[data-masura-nume]'), s = r.querySelector('[data-masura-stare]');
            return {cod: r.dataset.masura, vizibil: viz(r), nume: vtxt(n), stare: vtxt(s), motiv: vtxt(mo),
                    plafoane: vv.map(v => ({text: vtxt(v), vizibil: viz(v)})), perioade: pp.map(x => ({text: vtxt(x), vizibil: viz(x)}))}; })};
}"""
JS_CABINET = "() => {" + TXT + VIZ + """
  const ov = document.querySelectorAll('.fereastra-overlay:not(.fundal)').length;
  const g = [...document.querySelectorAll('.cab-grila')].find(x => !x.closest('.firme-grup'));
  if (!g) return {grila: false, overlay: ov};
  const card = c => { const s = c.querySelector('[data-cheie]');
    return {cheie: s ? s.dataset.cheie : null, titlu: txt(c.querySelector('.cab-card-titlu')), sinteza: txt(s), vizibil: viz(c), activ: !c.disabled}; };
  const copii = [...g.children].map(c => c.matches('button.cab-card') ? Object.assign({tip: 'card'}, card(c))
    : c.matches('section') ? {tip: 'sectiune', controls: (c.querySelector('button.firme-grup-btn[aria-controls]') || {getAttribute: () => null}).getAttribute('aria-controls')}
    : {tip: 'alt', tag: c.tagName});
  const sectiuni = [...g.querySelectorAll('button.firme-grup-btn[aria-controls]')].map(b => { const id = b.getAttribute('aria-controls'),
    c = document.getElementById(id), sec = b.closest('section');
    return {controls: id, titlu: txt(b), expandat: b.getAttribute('aria-expanded'), buton_vizibil: viz(b), continut: !!c,
            continut_in_sectiune: !!c && !!sec && sec.contains(c), continut_vizibil: viz(c), index_in_grila: sec ? [...g.children].indexOf(sec) : -1,
            carduri: c ? [...c.querySelectorAll('button.cab-card')].map(card) : [],
            chei: c ? [...c.querySelectorAll('[data-cheie]')].map(x => x.dataset.cheie) : []}; });
  return {grila: true, overlay: ov, copii, sectiuni, chei_pagina: [...document.querySelectorAll('[data-cheie]')].map(x => x.dataset.cheie),
          titluri_consultanta: [...document.querySelectorAll('button.firme-grup-btn')].filter(b => /^consultan/i.test(txt(b) || '')).length};
}"""
JS_BANCA = "() => {" + SUS + TXT + VIZ + """
  if (!top) return null;
  const h = top.querySelector('#bk-rezumat h2.pf-titlu'), a = top.querySelector('#bk-alege');
  const semne = h ? [...h.querySelectorAll('[data-ajutor]')].map(b => { const r = b.getBoundingClientRect();
    return {id: b.dataset.ajutor, title: b.getAttribute('title'), aria: b.getAttribute('aria-label'), vizibil: viz(b),
            latime: Math.round(r.width), inaltime: Math.round(r.height)}; }) : null;
  return {antet: txt(top.querySelector('.fereastra-antet, header')),
          titlu: h ? [...h.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\\s+/g, ' ').trim() : null,
          semne, martor: a ? {text: txt(a), vizibil: viz(a)} : null};
}"""
JS_SECTIUNI = "() => {" + SUS + VIZ + VTXT + """
  if (!top) return null;
  return [...top.querySelectorAll('[data-ajutor-sectiune]')].map(s => ({id: s.dataset.ajutorSectiune, vizibil: viz(s),
    titlu: vtxt(s.querySelector('[data-ajutor-sectiune-titlu]')), linii: [...s.querySelectorAll('.aj-sec, .aj-p')].map(vtxt)}));
}"""
JS_NIVEL = """(n) => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')], t = o.length ? o[o.length - 1] : null;
  return !!t && t.dataset.nivel === String(n); }"""
CENTRU = """(sel) => { const b = document.querySelector(sel); if (!b) return null; b.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});
  const r = b.getBoundingClientRect(); const x = r.x + r.width / 2, y = r.y + r.height / 2; const el = document.elementFromPoint(x, y);
  return {x, y, hit: !!el && (el === b || b.contains(el))}; }"""
CARD = "const textCard = x => { const c = x.closest('.ds-semnal-cutie, .ds-rezumat-cutie'); return c ? (c.querySelector('.ds-semnal-text, .ds-rezumat-text') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim() : ''; };"
LISTE = """const grupTva = [...top.querySelectorAll('section.cf-grup')].find(x => (x.querySelector('h3') || {textContent: ''}).textContent.includes('Coerență TVA'));
  const semnale = grupTva ? [...grupTva.querySelectorAll('.ds-semnal-cutie .ds-semnal-plie')] : [];
  const carduri = [...top.querySelectorAll('.ds-rezumat-cutie .ds-rezumat-plie')].filter(x => !x.classList.contains('ds-rezumat-plie-auto'));
  const avertismente = [...top.querySelectorAll('.dec-avert-semnal .ds-semnal-cutie .ds-semnal-plie')];"""
TINTA = """([tip, prefix]) => {
  const top = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop();
  window.__btn = null;
  if (!top) return null;
  """ + CARD + LISTE + """
  const lista = tip === 'semnal' ? semnale : tip === 'rezumat' ? carduri : avertismente;
  const ordinal = tip === 'rezumat' ? lista.findIndex(x => textCard(x).startsWith(prefix)) : (lista.length ? 0 : -1);
  if (ordinal < 0) return null;
  const b = lista[ordinal];
  window.__btn = b;
  return {tip, ordinal, text: textCard(b), grup: grupTva && tip === 'semnal' ? (grupTva.querySelector('h3') || {textContent: ''}).textContent.replace(/\\s+/g, ' ').trim() : null,
          in_corp: !!b.closest('.cf-corp'), in_avertisment: !!b.closest('.dec-avert-semnal')};
}"""
STARE = """() => { const b = window.__btn; const cut = b.closest('.ds-semnal-cutie, .ds-rezumat-cutie');
  const d = cut && cut.querySelector('.ds-semnal-detalii, .ds-rezumat-detalii');
  return [b.getAttribute('aria-expanded'), d ? d.hidden : null, d ? d.getClientRects().length > 0 : null, b.textContent.trim()]; }"""
CONECTAT = "() => !!window.__btn && window.__btn.isConnected"
CENTRU_BTN = """() => { const b = window.__btn; b.scrollIntoView({block: 'center', inline: 'nearest', behavior: 'instant'});
  const r = b.getBoundingClientRect(); const x = r.x + r.width / 2, y = r.y + r.height / 2; const el = document.elementFromPoint(x, y);
  return {x, y, hit: !!el && (el === b || b.contains(el))}; }"""
URMARESTE = """() => { const b = window.__btn; window.__mut = []; window.__ajuns = [];
  if (window.__obs) window.__obs.disconnect();
  window.__obs = new MutationObserver(ms => { for (const m of ms) window.__mut.push(m.oldValue); });
  window.__obs.observe(b, {attributes: true, attributeOldValue: true, attributeFilter: ['aria-expanded']});
  if (window.__clic) document.removeEventListener('click', window.__clic);
  window.__clic = e => { if (e.target === b || b.contains(e.target)) window.__ajuns.push(e.isTrusted); };
  document.addEventListener('click', window.__clic); return true; }"""
COLECTEAZA = """() => { for (const m of window.__obs.takeRecords()) window.__mut.push(m.oldValue);
  const out = {mutatii: window.__mut.slice(), ajuns_la_document: window.__ajuns.slice()}; window.__mut.length = 0; window.__ajuns.length = 0; return out; }"""
INCHEIE = """() => { if (window.__obs) window.__obs.disconnect(); if (window.__clic) document.removeEventListener('click', window.__clic); return true; }"""
INVENTAR = """() => { const top = [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra')].pop();
  if (!top) return null;
  """ + CARD + LISTE + """
  return {semnale: semnale.map(textCard), carduri: carduri.map(textCard), avertismente: avertismente.map(textCard),
          butoane: top.querySelectorAll('.ds-semnal-plie, .ds-rezumat-plie').length}; }"""


RE_SUMA = re.compile(r"(?<![\d.,])(\()?\s?([-−–]\s?)?(\d{1,3}(?:\.\d{3})+|\d+),(\d{2})(\))?(?![\d,])")
RE_PCT = re.compile(r"(?<![\d.,])(\d+(?:,\d+)?)\s?%")
RE_INT = re.compile(r"(?<![\d.,])\d+(?![\d.,])")
RE_LEI = re.compile(r"(\d{1,3}(?:[.\s  ]\d{3})+|\d+),(\d{2})\s?lei")


def norm(t):
    return re.sub(r"\s+", " ", t or "").strip()


def _val(m):
    v = Decimal(m.group(3).replace(".", "") + "." + m.group(4))
    return -v if m.group(2) or (m.group(1) and m.group(5)) else v


def bani_exact(text):
    """Celula este o singură sumă întreagă, cu semnul ei («30.000,00», «−25.200,00», «(25.200,00)», opțional « lei»); altfel None."""
    m = RE_SUMA.fullmatch(re.sub(r"\s?lei$", "", norm(text)))
    return _val(m) if m else None


def cota_exacta(text):
    m = re.fullmatch(r"(\d+(?:,\d+)?)\s?%?", norm(text))
    return Decimal(m.group(1).replace(",", ".")).normalize() if m else None


def lei_exact(text):
    """Textul întreg este o sumă în lei («509.850,00 lei»; miile despărțite prin punct, spațiu sau nedespărțite); altfel None."""
    m = RE_LEI.fullmatch(norm(text))
    return Decimal(re.sub(r"[.\s  ]", "", m.group(1)) + "." + m.group(2)) if m else None


def celule_linie(text):
    """Un rând vizual despărțit în celule tipizate, în ordinea din rând: N text, P procent, S sumă cu semn, I număr întreg."""
    text, out, poz = norm(text), [], 0
    while poz < len(text):
        c = [(m.start(), k, m) for k, m in enumerate((RE_PCT.search(text, poz), RE_SUMA.search(text, poz), RE_INT.search(text, poz))) if m]
        if not c:
            break
        s, k, m = min(c, key=lambda x: (x[0], x[1]))
        if text[poz:s].strip():
            out.append(("N", text[poz:s].strip()))
        out.append(("P", Decimal(m.group(1).replace(",", ".")).normalize()) if k == 0 else ("S", _val(m)) if k == 1 else ("I", Decimal(m.group(0))))
        poz = m.end()
    if text[poz:].strip():
        out.append(("N", text[poz:].strip()))
    return out


def sha(b):
    return hashlib.sha256(b).hexdigest()


def fis(*parti):
    """Numele unei capturi, numai din litere ASCII și cifre, părțile unite cu «_»."""
    return "_".join(re.sub(r"[^A-Za-z0-9]", "", unicodedata.normalize("NFKD", str(p)).encode("ascii", "ignore").decode()) for p in parti)


def ruta_copie(u):
    """Ruta măsurată e a copiei de test: http, 127.0.0.1 sau localhost, portul 8019."""
    try:
        a = urlsplit(u or "")
        return a.scheme == "http" and a.hostname in ("127.0.0.1", "localhost") and a.port == 8019 and a.path.startswith("/")
    except ValueError:
        return False


# ---------- e.2: cititorul de documente Word (pachet OPC) și cititorul PDF (aceleași funcții la test și la cititor) ----------
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PR = "{http://schemas.openxmlformats.org/package/2006/relationships}"
TIP_DOC = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
COLOANE = ("nume", "cota", "brut", "impozit", "net")
SUME_CAP = ("brut", "impozit", "net")
# titlurile vizibile ale modelului 501, cu cota T1 (4.800,00 din 30.000,00 = 16 %) și moneda
TITLURI_501 = ("Asociatul", "Cota din capitalul social", "Dividend brut (lei)", "Impozit pe dividende 16% (lei)", "Dividend net (lei)")
MANDAT = re.compile(r"Se împuternicește\s+(.+?),\s*administrator al societății")
EXEMPLARE = re.compile(r"în\s+(\d+)\s+(?:de\s+)?exemplare originale")
TOL_X = 1.0   # puncte PDF
GOL_LIPIT, GOL_SPATIU = 0.08, 0.6   # fracțiuni din înălțimea cuvântului: sub primul, cuvintele sunt lipite; sub al doilea, e un spațiu obișnuit


def _da(e):
    """Valoarea unei proprietăți Word de tip comutator (w:vanish): prezentă și nu «0/false/off»."""
    return e is not None and (e.get(W + "val") or "true").lower() not in ("0", "false", "off")


def citeste_docx(continut):
    """Deschide documentul Word ca pachet OPC, cum îl deschide un cititor de documente: arhiva întreagă, tipurile de conținut, apoi fiecare
    relație internă, de la rădăcină, urmată până la partea ei (o parte referită și absentă, fără tip sau cu XML stricat = nu se deschide).
    Verifică partea principală, lipsa protecției la editare și a conținutului înglobat. Întoarce textul afișat: paragrafele din afara
    tabelelor și tabelele, fără textul ascuns (w:vanish pe fragment sau moștenit din stilul lui ori al paragrafului), cu întreruperile de rând
    și tabulatoarele redate ca spații."""
    gol = {"paragrafe": [], "randuri_text": [], "tabele": []}
    try:
        z = zipfile.ZipFile(io.BytesIO(continut))
        if z.testzip() is not None:
            return dict(gol, probleme=["arhivă coruptă"])
        nume = set(z.namelist())
        tipuri = ET.fromstring(z.read("[Content_Types].xml"))
    except (zipfile.BadZipFile, KeyError, ET.ParseError):
        return dict(gol, probleme=["nu e pachet OPC ([Content_Types].xml)"])
    ov = {o.get("PartName"): o.get("ContentType") for o in tipuri if o.tag.endswith("}Override")}
    df = {(d.get("Extension") or "").lower(): d.get("ContentType") for d in tipuri if d.tag.endswith("}Default")}
    tip = lambda p: ov.get("/" + p) or df.get(p.rsplit(".", 1)[-1].lower() if "." in p else "")  # noqa: E731
    probleme, parti, principala, protectie = [], {}, [], False

    def relatii(sursa):
        r = posixpath.join(posixpath.dirname(sursa), "_rels", posixpath.basename(sursa) + ".rels") if sursa else "_rels/.rels"
        if r not in nume:
            return [] if sursa else None
        try:
            return [(x.get("Type") or "", x.get("Target") or "", x.get("TargetMode")) for x in ET.fromstring(z.read(r)).iter(PR + "Relationship")]
        except ET.ParseError:
            probleme.append("relații necitite: " + r)
            return []

    def urmeaza(sursa):
        rel = relatii(sursa)
        if rel is None:
            probleme.append("fără _rels/.rels")
            return
        for t, tinta, mod in rel:
            if mod == "External":
                continue
            p = posixpath.normpath(tinta[1:] if tinta.startswith("/") else posixpath.join(posixpath.dirname(sursa), tinta))
            if not sursa and t == REL_DOC:
                principala.append(p)
            if p in parti:
                continue
            if p not in nume:
                probleme.append("relație spre o parte absentă: " + p)
                continue
            parti[p] = tip(p)
            if not parti[p]:
                probleme.append("parte fără tip de conținut: " + p)
            elif parti[p].endswith("xml"):
                try:
                    ET.fromstring(z.read(p))
                except ET.ParseError:
                    probleme.append("parte XML stricată: " + p)
                    continue
            urmeaza(p)

    urmeaza("")
    if principala != ["word/document.xml"] or parti.get("word/document.xml") != TIP_DOC:
        probleme.append("partea principală nu e word/document.xml de tip WordprocessingML")
    if any(n.lower().endswith(".pdf") for n in nume) or any(b"altChunk" in z.read(p) for p in parti if p.endswith(".xml")):
        probleme.append("PDF sau bloc străin înglobat")
    for p in parti:
        if p.endswith("settings.xml") and re.search(r"<w:(documentProtection|writeProtection)\b", z.read(p).decode("utf-8", "replace")):
            protectie = True
    if protectie:
        probleme.append("documentul e protejat la editare")
    try:
        doc = ET.fromstring(z.read("word/document.xml"))
    except (KeyError, ET.ParseError):
        return dict(gol, probleme=probleme + ["word/document.xml lipsește sau nu e XML"])
    corp = doc.find(W + "body")
    if doc.tag != W + "document" or corp is None:
        return dict(gol, probleme=probleme + ["fără w:document/w:body"])
    # stilurile care ascund textul (w:vanish), cu moștenirea prin w:basedOn și cu valorile implicite ale documentului
    ascunse, baza, implicit = {}, {}, False
    st = next((p for p in parti if p.endswith("styles.xml")), None)
    if st:
        try:
            rs = ET.fromstring(z.read(st))
            implicit = _da(rs.find("%sdocDefaults/%srPrDefault/%srPr/%svanish" % (W, W, W, W)))
            for s in rs.iter(W + "style"):
                sid, v, b = s.get(W + "styleId"), s.find("%srPr/%svanish" % (W, W)), s.find(W + "basedOn")
                ascunse[sid] = None if v is None else _da(v)
                baza[sid] = b.get(W + "val") if b is not None else None
        except ET.ParseError:
            pass

    def stil_ascuns(sid, adanc=0):
        if sid is None or sid not in ascunse or adanc > 20:
            return None
        return ascunse[sid] if ascunse[sid] is not None else stil_ascuns(baza.get(sid), adanc + 1)

    def text(e):
        out = []
        for p in ([e] if e.tag == W + "p" else e.iter(W + "p")):
            ps = p.find("%spPr/%spStyle" % (W, W))
            ps = stil_ascuns(ps.get(W + "val")) if ps is not None else None
            for r in p.iter(W + "r"):
                v, rs = r.find("%srPr/%svanish" % (W, W)), r.find("%srPr/%srStyle" % (W, W))
                rs = stil_ascuns(rs.get(W + "val")) if rs is not None else None
                ascuns = _da(v) if v is not None else rs if rs is not None else ps if ps is not None else implicit
                if not ascuns:   # textul fragmentului, cu separatoarele redate: întreruperea de rând și tabulatorul despart cuvintele
                    out.append("".join((x.text or "") if x.tag == W + "t" else "\t" if x.tag == W + "tab" else " " for x in r.iter()
                                       if x.tag in (W + "t", W + "br", W + "cr", W + "tab")))
            out.append(" ")
        return "".join(out)   # tabulatoarele rămân «\t»: despart părțile unui paragraf așezate ca într-un rând
    in_tabel = {id(p) for t in corp.iter(W + "tbl") for p in t.iter(W + "p")}
    brute = [text(p) for p in corp.iter(W + "p") if id(p) not in in_tabel]
    paragrafe = [norm(x) for x in brute if norm(x)]
    randuri_text = [[norm(s) for s in x.split("\t") if norm(s)] for x in brute if norm(x)]
    tabele = [[[norm(text(c)) for c in r.findall(W + "tc")] for r in t.findall(W + "tr")] for t in corp.iter(W + "tbl")]
    return {"probleme": probleme, "paragrafe": paragrafe, "randuri_text": randuri_text, "tabele": tabele}


def citeste_pdf(continut):
    """Paginile și rândurile vizuale ale PDF-ului, cum le vede destinatarul. Structura (se deschide, necriptat, are pagini) și textul în modul
    de redare invizibil se citesc cu pypdf. Cuvintele și dreptunghiurile lor vin de la cititorul Poppler (pdftotext -bbox-layout -cropbox),
    în coordonatele zonei afișate a paginii (CropBox): un cuvânt care nu stă integral în zona afișată nu contează. Cuvintele se grupează pe
    linia de bază; pe fiecare rând, cele lipite se unesc (literele puse separat de generator), cele despărțite de un spațiu obișnuit formează
    aceeași bucată, iar un gol mai mare începe altă bucată. Întoarce, pe rânduri, bucățile (x stânga, x dreapta, text)."""
    import html
    import logging
    import subprocess
    import tempfile
    from pypdf import PdfReader
    logging.getLogger("pypdf").setLevel(logging.CRITICAL)   # avertismentele bibliotecii nu sunt măsuri; structura se judecă mai jos
    gol = {"pagini": 0, "linii": []}
    try:
        r = PdfReader(io.BytesIO(continut))
        if r.is_encrypted:
            return dict(gol, probleme=["PDF criptat"])
        pagini = list(r.pages)
    except Exception as e:   # noqa: BLE001 — orice eroare de structură înseamnă PDF neutilizabil
        return dict(gol, probleme=["PDF ilizibil: %s" % type(e).__name__])
    if not pagini:
        return dict(gol, probleme=["PDF fără pagini"])
    invizibile = []   # pe pagini: (x, y, cuvintele) ale bucăților scrise în modul de redare 3, în coordonatele zonei afișate
    for p in pagini:
        buc, redare, stiva = [], [0], []
        try:
            st, sus = float(p.cropbox.left), float(p.cropbox.top)
        except Exception as e:   # noqa: BLE001
            return dict(gol, probleme=["PDF ilizibil: %s" % type(e).__name__])

        def inainte(op, args, cm, tm, redare=redare, stiva=stiva):   # modul de redare ține de starea grafică: q îl salvează, Q îl reface
            if op == b"Tr" and args:
                redare[0] = int(args[0])
            elif op == b"q":
                stiva.append(redare[0])
            elif op == b"Q" and stiva:
                redare[0] = stiva.pop()

        def viz(tx, cm, tm, *_, buc=buc, redare=redare, st=st, sus=sus):
            if tx and tx.strip() and redare[0] == 3:   # modul 3: text nici umplut, nici conturat (invizibil)
                buc.append((tm[4] * cm[0] + tm[5] * cm[2] + cm[4] - st, sus - (tm[4] * cm[1] + tm[5] * cm[3] + cm[5]), norm(tx).split(" ")))
        try:
            p.extract_text(visitor_text=viz, visitor_operand_before=inainte)
        except Exception as e:   # noqa: BLE001
            return dict(gol, probleme=["PDF ilizibil: %s" % type(e).__name__])
        invizibile.append(buc)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "document.pdf"
            f.write_bytes(continut)
            x = subprocess.run(["pdftotext", "-bbox-layout", "-cropbox", "-enc", "UTF-8", str(f), "-"], capture_output=True, timeout=60, check=False)
    except (OSError, subprocess.SubprocessError) as e:
        return dict(gol, probleme=["cititorul Poppler (pdftotext) nu a putut fi rulat: %s" % type(e).__name__])
    if x.returncode != 0:
        return dict(gol, probleme=["cititorul Poppler (pdftotext) nu deschide documentul: rc %d" % x.returncode])
    pg = re.split(r"<page\b", x.stdout.decode("utf-8", "replace"))[1:]
    if len(pg) != len(pagini):
        return dict(gol, probleme=["cititorul Poppler vede %d pagini, pypdf %d" % (len(pg), len(pagini))])
    linii = []
    for k, s in enumerate(pg):
        m = re.match(r'\s+width="([\d.]+)" height="([\d.]+)"', s)
        if not m:
            return dict(gol, probleme=["ieșirea cititorului Poppler nu are dimensiunea paginii"])
        lat, inalt = float(m.group(1)), float(m.group(2))
        cuv = [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in
               re.findall(r'<word xMin="([-\d.]+)" yMin="([-\d.]+)" xMax="([-\d.]+)" yMax="([-\d.]+)">(.*?)</word>', s, re.S)]
        cuv = [c for c in cuv if c[4].strip() and c[0] >= -1 and c[1] >= -1 and c[2] <= lat + 1 and c[3] <= inalt + 1]   # numai ce stă în zona afișată
        pe_linie = {}
        for c in cuv:
            y = next((y for y in pe_linie if abs(y - c[3]) <= 2), c[3])
            pe_linie.setdefault(y, []).append(c)
        for y, v in sorted(pe_linie.items()):
            v.sort()
            sterse = set()   # cuvintele scrise invizibil: bucata începe în dreptunghiul cuvântului, apoi urmează cuvintele ei
            for ix, iy, cuvinte in invizibile[k]:
                for n, c in enumerate(v):
                    if c[0] - 1 <= ix <= c[2] and c[1] <= iy <= c[3] + 2:
                        rest = "".join(cuvinte)
                        for q in range(n, len(v)):
                            if q in sterse or not rest.startswith(v[q][4]):
                                break
                            sterse.add(q)
                            rest = rest[len(v[q][4]):]
                        break
            buc = []
            for n, (a, b, c, d, w) in enumerate(v):
                if n in sterse:
                    continue
                h = d - b
                if buc and a - buc[-1][1] <= GOL_LIPIT * h:
                    buc[-1] = [buc[-1][0], c, buc[-1][2] + w]
                elif buc and a - buc[-1][1] <= GOL_SPATIU * h:
                    buc[-1] = [buc[-1][0], c, buc[-1][2] + " " + w]
                else:
                    buc.append([a, c, w])
            if buc:
                linii.append([(a, c, norm(w)) for a, c, w in buc])
    return {"probleme": [], "pagini": len(pagini), "linii": linii}


def rand_de_repartizare(text):
    """Un text care arată ca un rând de repartizare: un nume, opțional o cotă, apoi cel puțin două sume și nimic altceva."""
    c = [k for k, _ in celule_linie(text)]
    return len(c) >= 3 and c[0] == "N" and c[1:] in (["P"] + ["S"] * (len(c) - 2), ["I"] + ["S"] * (len(c) - 2), ["S"] * (len(c) - 1)) and c.count("S") >= 2


# Regula rândurilor cu sume din afara tabelului de repartizare (D4). Funcția rand_in_plus este scrisă de GPT-6 (fișierul rand_in_plus_F5.py,
# SHA-256 456f025db55b53e22ea67ca188aa946ab364e2fdd87d229d708f936daa39e3b4, 27.11.2026) și integrată neschimbată; probele ei (422) stau în
# același fișier, păstrat în calificarea fișei (calificare/rand_in_plus_F5.py). Citește T1_TOTAL în ordinea brut, impozit, net și judecă un singur rând, fără stare între apeluri.
def rand_in_plus(segmente):
    """Judecă un singur rând vizibil din afara tabelului de repartizare."""
    from decimal import Decimal
    import re
    import unicodedata

    def normalizare(s):
        s = unicodedata.normalize("NFKD", " ".join((s or "").split()))
        return "".join(c for c in s if not unicodedata.combining(c))

    bucati = [normalizare(s) for s in segmente if s and s.strip()]
    # Un întreg într-o celulă proprie este monetar după o etichetă de rubrică.
    # Nu inventăm moneda unei date, cote sau numerotări dintr-un paragraf.
    grupat = r"(?:\d{1,3}(?:[. ]\d{3})+|\d+)"
    if len(bucati) == 2 and re.fullmatch(rf"[−–-]?{grupat}", bucati[1]):
        bucati[1] += ",00"
    text = " ".join(bucati)
    if not any(c.isdecimal() for c in text):
        return None

    # Numărul articolului și procentele nu sunt sume de bani.
    text = re.sub(r"^\s*art(?:icolul)?\.?\s+(?:\d+|[ivxlcdm]+)\s*[.:)]?\s*", "", text, flags=re.I)
    text = re.sub(r"(?<![\d.,])\d+(?:,\d+)?\s*%", " ", text)
    valute = r"(?:lei|leu|ron|eur|euro|usd|gbp|chf|huf|mdl|bgn|jpy|cad|aud|pln|czk|sek|nok|dkk|try|cny|€|\$|£|¥)"
    # Întregii din date, identificatori și numere de articole nu au monedă.
    bani = re.compile(
        rf"(?<![\w.,])(?P<par>\()?\s*(?P<semn>[−–-]?)\s*"
        rf"(?P<numar>{grupat},\d{{2}}(?![\d,])|{grupat}(?=\s*{valute}(?!\w)))"
        rf"\s*(?P<moneda>{valute}(?!\w))?(?(par)\)|)", re.I)

    rubrici = {"brut": Decimal(T1_TOTAL[0]), "impozit": Decimal(T1_TOTAL[1]),
               "net": Decimal(T1_TOTAL[2])}

    def afisare(suma):
        return f"{suma:,.2f}".translate(str.maketrans(",.", ".,"))

    def este_destinatar(eticheta):
        # Un destinatar explicit poate avea chiar un nume alcătuit din cuvinte comune.
        marcaj = re.search(r"\b(?:catre|pentru|beneficiar(?:ul|a)?\s*[:=])\s*[:=]?\s*(.+)", eticheta)
        if marcaj:
            tinta = marcaj.group(1).strip(" :.;,-")
            # În art. 3, „către asociați a dividendelor ...” descrie colectiv distribuirea.
            generic = re.match(
                r"^(?:(?:toti )?asociat(?:i|ii)|asociat(?:ul|ului)? unic|societate|bugetul de stat)"
                r"(?:$|\s+(?:a|ai|in|din|pentru|privind|potrivit|la)\b)", tinta)
            if not generic and not re.match(r"^(?:plata|calculul|distribuirea|aprobarea|dividende(?:le|lor)?|exercitiul|anul|perioada|trimestrul)\b", tinta):
                return True
        if re.match(r"^plata\s+(?:efectuata\s+)?(?:lui|doamnei|domnului)\s+\w", eticheta):
            return True
        return bool(re.match(r"^(?:beneficiar(?:ul|a)?|destinatar(?:ul)?|asociat(?:ul)?)\s*[:=]\s*\w", eticheta))

    def rol(eticheta):
        # Ordinea cuvintelor contează: în „dividend net după impozit” rubrica este netul.
        # Excludem indicatorii financiari diferiți înainte de a căuta rubrica dividendului.
        eticheta = re.sub(r"\b(?:profit\w*|activ\w*|salari\w*)\s+(?:brut|net)\w*\b", " ", eticheta)
        eticheta = re.sub(r"\bimpozit(?:ul|ului)? pe (?:profit|salarii|cladiri)\b", " ", eticheta)
        m = re.search(r"\b(brut(?:a|e|i|ul|ului)?|impozit(?:ul|ului|e|ele|elor)?|net(?:a|e|i|ul|ului)?)\b", eticheta)
        if m:
            return next(k for k in rubrici if m.group().startswith(k))
        return None

    def explica_alta_marime(eticheta):
        return bool(re.search(
            r"\b(?:profit\w*|activ\w*|salari\w*)\s+(?:brut|net)\w*\b|"
            r"\b(?:rezerv\w*|profit\w* nerepartizat|capital\w* social|capital\w* subscris|"
            r"pierder\w*|datori\w*|rezultat\w* reportat|dividende\w* interimare|impozit(?:ul)? pe (?:profit|salarii|cladiri))\b", eticheta))

    def denumire_firma(eticheta):
        # Un CUI care urmează denumirii nu schimbă forma juridică.
        eticheta = re.sub(r"[, (]*\bcui\s*[:=]?\s*(?:ro)?\s*\d+\)?\s*$", "", eticheta)
        # Se examinează sigla ca termen întreg. „Art. II” a fost eliminat mai sus.
        sigle = {"srl", "srld", "sa", "sca", "scs", "snc", "pfa", "ii", "if", "ra", "sc"}
        compact = re.sub(r"(?<!\w)(?:[a-z]\.\s*)+[a-z]?(?!\w)",
                         lambda m: " " + re.sub(r"[.\s]", "", m.group()) + " ", eticheta)
        parti = re.findall(r"[a-z0-9]+", compact)
        return len(parti) >= 2 and (parti[-1] in sigle or parti[0] in sigle
                                    or compact.rstrip(" .,:;").endswith("societate cu raspundere limitata"))

    aparitii = list(bani.finditer(text))
    if not aparitii:
        if len(bucati) == 2 and rol(bucati[0].casefold()) and re.fullmatch(
                r"[-−–(+]?\d[\d,. ]*\)?(?:\s*[a-zA-Z]{3}|\s*[€£$¥])?", bucati[1]):
            return "sumă sau monedă nerecunoscută în rubrica " + rol(bucati[0].casefold())
        return None

    inceput = 0
    urmatoare = []
    ultima = None
    antete_celule = []
    if len(aparitii) > 1 and len(bucati) == 2 * len(aparitii):
        prefix = bucati[:len(aparitii)]
        if all(rol(c.casefold()) and not bani.search(c) for c in prefix):
            antete_celule = [c.casefold() for c in prefix]
    for index, m in enumerate(aparitii):
        brut = text[inceput:m.start()].strip(" \t:;,=()")
        inceput = m.end()
        eticheta = brut.casefold()
        if este_destinatar(eticheta) or denumire_firma(eticheta):
            return "plată către un beneficiar"
        if eticheta:
            # „brut / impozit / net” oferă trei etichete; „net după impozit” oferă una.
            # Păstrăm și frontierele celulelor când Poppler sau Word le transmite separat.
            antete = re.split(r"\s*(?:[/;|]|\bsi\b)\s*", eticheta)
            if index == 0 and antete_celule:
                antete = antete_celule
            roluri = [rol(c) for c in antete if c.strip()]
            urmatoare = roluri if len(roluri) > 1 and all(roluri) else []
            cheie = urmatoare.pop(0) if urmatoare else rol(eticheta)
        else:
            cheie = urmatoare.pop(0) if urmatoare else ultima
        ultima = cheie
        if cheie is not None:
            moneda = m.group("moneda")
            moneda_eticheta = re.search(rf"(?<!\w)({valute})(?!\w)\s*\)?\s*$", eticheta, re.I)
            dupa_paranteza = (re.match(rf"\s*({valute})(?!\w)", text[m.end():], re.I)
                             if m.group("par") else None)
            # Într-o declarație monetară care se termină cu un cod de trei litere,
            # și codurile absente din lista uzuală trebuie confruntate cu RON.
            cod_final = re.fullmatch(r"\s*([a-z]{3}|[^\w\s])\s*[.;]?\s*", text[m.end():], re.I)
            cod_ramas = cod_final.group(1) if cod_final else ""
            if len(cod_ramas) == 1 and unicodedata.category(cod_ramas) != "Sc":
                cod_ramas = ""
            cod_antet = re.search(r"(?:\(|\bin\s+)([a-z]{3})\)?$", eticheta)
            for cod in (moneda, moneda_eticheta.group(1) if moneda_eticheta else None,
                        dupa_paranteza.group(1) if dupa_paranteza else None, cod_ramas,
                        cod_antet.group(1) if cod_antet else None):
                if cod and cod.casefold() not in {"ron", "lei", "leu"}:
                    return f"rubrica {cheie} este în lei, iar rândul indică {cod.upper()}"
            valoare = Decimal(m.group("numar").replace(".", "").replace(" ", "").replace(",", "."))
            if m.group("semn") or m.group("par"):
                valoare = -valoare
            if valoare != rubrici[cheie]:
                return (f"rubrica {cheie} din etichetă are în tabel totalul {afisare(rubrici[cheie])}, "
                        f"iar rândul scrie {afisare(valoare)}")
        elif not explica_alta_marime(eticheta):
            cuvinte = re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", brut)
            if 2 <= len(cuvinte) <= 6 and all(c[0].isupper() for c in cuvinte):
                return "plată către un beneficiar"
    return None


def rand_de_total(segmente):
    """Un rând cu formă de rând de total al repartizării: începe cu cuvântul «Total» (cuvânt întreg, în orice grafie) și are forma unui
    rând de tabel (etichetă, opțional cotă, cel puțin două sume și nimic altceva). «Total brut aprobat | 50.000,00 lei» nu are această formă."""
    text = norm(" ".join(segmente))
    return bool(re.match(r"total\b", text, re.I)) and rand_de_repartizare(text)


def _randuri_tabel(celule, prob):
    """Din celulele pe coloane ale rândurilor de sub cap: beneficiarii {nume: (cotă, brut, impozit, net)} și totalul; fiecare valoare
    trebuie să fie singură și întreagă în coloana ei."""
    ben, tot = {}, []
    for n, r in enumerate(celule):
        if r["nume"].casefold() == "total":   # rândul de total al tabelului: eticheta «Total», singură în coloana ei
            if r["cota"] not in ("", "100%"):
                prob.append("rândul Total are alt text în coloana cotei: %s" % r["cota"][:10])
            tot.append((n, tuple(bani_exact(r[k]) for k in SUME_CAP)))
            continue
        v = (cota_exacta(r["cota"]),) + tuple(bani_exact(r[k]) for k in SUME_CAP)
        if not r["nume"] or None in v:
            prob.append("rând cu o valoare lipsă, dublă sau în altă coloană: %s" % " | ".join(r[k] for k in COLOANE)[:80])
        if r["nume"] in ben:
            prob.append("beneficiar repetat: " + r["nume"][:40])
        ben[r["nume"]] = v
    if len(tot) != 1 or tot[0][0] != len(celule) - 1:
        prob.append("rândul Total nu e unic și ultimul")
    return ben, (tot[0][1] if len(tot) == 1 else None)


def repartizare_docx(d):
    """Tabelul de repartizare din Word, unic: primul rând are exact titlurile afișate ale modelului 501 (cu 16% și lei), fiecare valoare stă
    în celula de sub titlul ei, rândul Total e unic și ultimul. În restul documentului nu există altă repartizare: niciun rând al altui
    tabel și niciun paragraf nu arată o plată către un beneficiar și nu contrazice o rubrică (rand_in_plus, aceeași regulă ca în PDF). O sumă explicativă, în text
    sau lângă eticheta ei, rămâne."""
    cap = [i for i, t in enumerate(d["tabele"]) if t and tuple(t[0]) == TITLURI_501]
    if len(cap) != 1:
        return {}, None, ["tabelul cu titlurile afișate ale modelului 501 (cota 16%%, lei): %d" % len(cap)]
    prob = []
    randuri = d["tabele"][cap[0]][1:]
    prob += ["rând cu %d celule" % len(r) for r in randuri if len(r) != 5]
    ben, total = _randuri_tabel([dict(zip(COLOANE, r)) for r in randuri if len(r) == 5], prob)
    for i, t in enumerate(d["tabele"]):
        if i != cap[0]:
            prob += ["%s, în alt tabel al documentului: %s" % (rand_in_plus(r), " | ".join(r)[:60]) for r in t if rand_in_plus(r)]
            prob += ["al doilea rând de total, în alt tabel al documentului: " + " | ".join(r)[:60] for r in t if rand_de_total(r)]
    prob += ["al doilea rând de total, în afara tabelului: " + " | ".join(s)[:60] for s in d["randuri_text"] if rand_de_total(s)]
    prob += ["%s, în afara tabelului: %s" % (rand_in_plus(s), " | ".join(s)[:60]) for s in d["randuri_text"] if rand_in_plus(s)]
    return ben, total, prob


def _coloane_vizuale(randuri):
    """Coloanele vizuale ale unui grup de rânduri: bucățile se leagă dacă se suprapun pe orizontală ori au același început, același sfârșit
    sau același mijloc (aliniere la stânga, la dreapta, centrată). Întoarce coloanele de la stânga la dreapta, fiecare cu bucățile ei
    (rând, x, text) și cu întinderea ei, sau None dacă întinderile a două coloane se suprapun."""
    b = [(n, a, z, tx) for n, ln in enumerate(randuri) for a, z, tx in ln]
    tata = list(range(len(b)))

    def rad(i):
        while tata[i] != i:
            tata[i] = tata[tata[i]]
            i = tata[i]
        return i
    for i in range(len(b)):
        for j in range(i):
            (_, a, z, _), (_, c, e, _) = b[i], b[j]
            if min(z, e) - max(a, c) > TOL_X or abs(a - c) <= TOL_X or abs(z - e) <= TOL_X or abs(a + z - c - e) <= 2 * TOL_X:
                tata[rad(i)] = rad(j)
    grup = {}
    for i, x in enumerate(b):
        grup.setdefault(rad(i), []).append(x)
    col = sorted(((min(x[1] for x in g), max(x[2] for x in g), sorted((x[0], x[1], x[3]) for x in g)) for g in grup.values()), key=lambda c: c[0])
    return None if any(y[0] < x[1] for x, y in zip(col, col[1:])) else col


def _rand_pdf_in_plus(linii, txt, i):
    """Un rând vizual din PDF, judecat cu rand_in_plus. Într-un PDF, un paragraf e rupt în rânduri oriunde, iar regula judecă un singur
    rând: «…care evidențiază un profit» / «net de 80.000,00 lei» ar da, pe al doilea rând, o abatere a rubricii «net». De aceea o abatere
    de rubrică se rejudecă o dată împreună cu rândul vizual de deasupra (textul lor, unul după altul) și rămâne abatere numai dacă se
    păstrează și așa. Plata către un beneficiar nu se rejudecă."""
    r = rand_in_plus([x[2] for x in linii[i]])
    if r and r.startswith("rubrica") and i > 0 and not rand_in_plus([txt[i - 1] + " " + txt[i]]):
        return None
    return r


def repartizare_pdf(linii):
    """Tabelul de repartizare din PDF, reconstruit pe coloanele vizuale. Rândul «Total» e unic; deasupra lui stau, unul sub altul, rândurile
    beneficiarilor (nume, cotă, trei sume, fiecare pe un rând vizual), iar deasupra lor capul, ale cărui titluri pot ocupa oricâte linii:
    liniile se adaugă una câte una, până rezultă titlurile complete sau până când o linie nu mai ține de cele cinci coloane. Bucățile capului și ale rândurilor se așază pe coloane după poziția lor pe orizontală; trebuie să rezulte exact cinci coloane,
    fiecare cu titlul modelului 501 (cu 16% și lei), citit de sus în jos, și cu o singură valoare, întreagă, pe fiecare rând. Niciun alt
    rând al documentului nu arată o plată către un beneficiar (rand_in_plus, aceeași regulă ca în Word)."""
    txt = [norm(" ".join(x[2] for x in ln)) for ln in linii]
    # rândurile cu formă de rând de total (rand_de_total): trebuie să fie unul singur, cel al tabelului; eticheta lui din coloana numelui
    # («Total», singură), poziția (ultimul rând) și valorile din coloanele tabelului se verifică în _randuri_tabel. Un rând explicativ care
    # doar începe cu acest cuvânt («Total brut aprobat 50.000,00 lei») nu are formă de rând de total
    tot = [i for i, ln in enumerate(linii) if rand_de_total([x[2] for x in ln])]
    if len(tot) != 1:
        return {}, None, ["rânduri Total ale tabelului: %d" % len(tot)]
    t = tot[0]
    b = t
    while b > 0 and rand_de_repartizare(txt[b - 1]):
        b -= 1
    if b == t:
        return {}, None, ["niciun rând de beneficiar deasupra rândului Total"]
    for n in range(1, b + 1):   # capul: liniile de deasupra beneficiarilor, luate una câte una, până dau cele cinci titluri sau ies din tabel
        col = _coloane_vizuale(linii[b - n:t + 1])
        if col is None or len(col) != 5:
            break   # linia adăugată nu mai ține de cele cinci coloane: am ieșit din zona tabelului
        if tuple(norm(" ".join(tx for r, _, tx in c[2] if r < n)) for c in col) != TITLURI_501:
            continue
        prob = ["%s, în afara tabelului: %s" % (_rand_pdf_in_plus(linii, txt, i), txt[i][:60]) for i in range(len(linii))
                if not b - n <= i <= t and _rand_pdf_in_plus(linii, txt, i)]
        celule = [{COLOANE[k]: norm(" ".join(tx for r, _, tx in c[2] if r == rr)) for k, c in enumerate(col)} for rr in range(n, n + t - b + 1)]
        ben, total = _randuri_tabel(celule, prob)
        return ben, total, prob
    return {}, None, ["capul cu titlurile modelului 501 (cota 16%, lei), pe cinci coloane vizuale deasupra beneficiarilor: nu se regăsește"]


def judeca_document(tip, continut):
    """Concluziile despre un document descărcat, recalculate din conținut: se deschide; tabelul cu titlurile modelului, pe coloane; mulțimea
    exactă a beneficiarilor (în orice ordine, fiecare o dată); totalurile reconciliate cu rândurile și egale cu T1; firma, hotărârea,
    administratorul împuternicit și numărul de exemplare."""
    if tip == "docx":   # domeniu-unic: tipurile sunt două, Word și PDF, și se judecă amândouă, fiecare pe ramura lui (ramura PDF urmează)
        d = citeste_docx(continut)
        text = norm(" ".join(d["paragrafe"]))
        ben, total, prob = repartizare_docx(d)
    else:
        d = citeste_pdf(continut)
        text = norm(" ".join(x[2] for ln in d["linii"] for x in ln))
        ben, total, prob = repartizare_pdf(d["linii"]) if d["linii"] else ({}, None, [])
    probleme = list(d["probleme"]) + prob
    if F2 not in text:
        probleme.append("firma")
    if not HOTARARE.search(text):
        probleme.append("hotărârea nr. 1 din 15.03.2026")
    if ben != {n: (Decimal(c).normalize(), Decimal(b), Decimal(i), Decimal(t)) for n, c, b, i, t in T1_ASOCIATI}:
        probleme.append("beneficiarii nu sunt exact cei doi din T1, cu valorile pe coloanele lor")
    if total != tuple(Decimal(x) for x in T1_TOTAL):
        probleme.append("totalul nu e cel din T1")
    if total is None or None in total or any(None in v for v in ben.values()) or tuple(sum(v[j] for v in ben.values()) for j in (1, 2, 3)) != total:
        probleme.append("totalurile nu se reconciliază cu rândurile")
    adm, ex = MANDAT.findall(text), EXEMPLARE.findall(text)
    if len(adm) != 1:
        probleme.append("mandatul administratorului: %d" % len(adm))
    if len(ex) != 1:
        probleme.append("numărul de exemplare: %d" % len(ex))
    f = lambda x: None if x is None else format(x, "f") if isinstance(x, Decimal) else x  # noqa: E731
    return {"probleme": probleme, "date": {"beneficiari": sorted([n] + [f(x) for x in v] for n, v in ben.items()), "total": [f(x) for x in total] if total else None,
                                           "administrator": norm(adm[0]) if len(adm) == 1 else None, "exemplare": ex[0] if len(ex) == 1 else None}}


# ---------- D2: premisele, pregătirea și restaurarea datelor de probă ----------
def premise_date(sql, s2):
    """Citiri înaintea oricărei scrieri: rândurile 1171 și 5121 ale F2 și cursul EUR din 31.12.2025. -> (stare, abateri)."""
    if not re.fullmatch(r"tenant_[0-9]+", s2):
        raise ValueError("schemă F2 nevalidă")
    stare, abateri = {}, []
    for cont, *_ in SOLD_T1:
        r = sql('SELECT sold_debitor, sold_creditor FROM "%s".solduri_initiale WHERE cont = %%s' % s2, (cont,))
        if len(r) > 1:
            abateri.append("%s are %d rânduri" % (cont, len(r)))
        stare[cont] = (Decimal(r[0][0]).quantize(Decimal("0.01")), Decimal(r[0][1]).quantize(Decimal("0.01"))) if r else None
        if stare[cont] != PREMISE_SOLD[cont]:
            abateri.append("%s: %r, premisa %r" % (cont, stare[cont], PREMISE_SOLD[cont]))
    c = sql("SELECT curs FROM public.curs_bnr_zilnic WHERE data = %s AND moneda = %s", CURS_EUR[:2])
    stare["curs"] = Decimal(c[0][0]) if c else None
    if len(c) > 1 or (stare["curs"] is not None and stare["curs"] != CURS_EUR[2]):
        abateri.append("cursul EUR din %s preexistent diferit: %r (BNR: %s)" % (CURS_EUR[0], [x[0] for x in c], CURS_EUR[2]))
    return stare, abateri


def pregateste_date(sql, s2, stare, facute):
    """Scrierile D2, fiecare consemnată în `facute` imediat după ce s-a comis (conftest.sql comite fiecare apel)."""
    for cont, den, deb, cred in SOLD_T1:
        if stare[cont] is None:
            sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor) VALUES (%%s, %%s, %%s, %%s)' % s2, (cont, den, deb, cred))
            facute.append(("sterge_sold", cont))
        else:
            sql('UPDATE "%s".solduri_initiale SET sold_debitor = sold_debitor + %%s, sold_creditor = sold_creditor + %%s WHERE cont = %%s' % s2,
                (deb, cred, cont))
            facute.append(("pune_sold", cont, stare[cont]))
    if stare["curs"] is None:
        sql("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s, %s, %s)", CURS_EUR)
        facute.append(("sterge_curs",))


def restaureaza_date(sql, s2, stare, facute):
    """Anulează numai operațiile comise, în ordine inversă, apoi recitește. -> lista abaterilor față de starea inițială (goală = refăcut)."""
    erori = []
    for op in reversed(list(facute)):
        try:
            if op[0] == "sterge_sold":
                sql('DELETE FROM "%s".solduri_initiale WHERE cont = %%s' % s2, (op[1],))
            elif op[0] == "pune_sold":
                sql('UPDATE "%s".solduri_initiale SET sold_debitor = %%s, sold_creditor = %%s WHERE cont = %%s' % s2, (op[2][0], op[2][1], op[1]))
            else:
                sql("DELETE FROM public.curs_bnr_zilnic WHERE data = %s AND moneda = %s", CURS_EUR[:2])
            facute.remove(op)
        except Exception as e:   # noqa: BLE001 — se încearcă toate anulările; abaterea rămâne consemnată
            erori.append("%s: %s" % (op[0], type(e).__name__))
    dupa, _ = premise_date(sql, s2)
    erori += ["%s: %r după, %r înainte" % (k, dupa[k], stare[k]) for k in stare if dupa[k] != stare[k]]
    return erori


# ---------- analiza ----------
def asteptat_ajutor(text_csv):
    """Secțiunile așteptate ale ferestrei AC202 la Bancă, din registru: numele și rândurile nevide ale coloanei ajutor, fără «## »."""
    r = {x["ID"]: x for x in csv.DictReader(io.StringIO(text_csv))}
    return [{"id": fid, "titlu": norm(r[fid]["Functionalitate"]),
             "linii": [x for x in (norm(l[3:] if l.startswith("## ") else l) for l in r[fid]["ajutor"].split("\n")) if x]} for fid in ORDINE_BANCA]


def stare_nume(st):
    return "deschis" if st == DESCHIS else "închis" if st == INCHIS else "alta"


def analiza_dividend(m):
    for k in ("antet", "formular", "note_inainte", "note_dupa", "captura", "ruta"):
        if k not in m:
            raise ValueError("Măsura dividendului e incompletă: " + k)
    f = m["formular"]
    if not isinstance(f, dict) or f.get("operatie") != "dividend" or not isinstance(f.get("butoane"), dict):
        raise ValueError("Formularul dividend nu a fost măsurat")
    e1, e2 = [], []
    if F2 not in (m["antet"] or ""):
        e1.append("firma")
    if not ruta_copie(m["ruta"]):
        e1.append("ruta")
    rand = f.get("randuri")
    if not f.get("tabel_vizibil") or not isinstance(rand, list):
        e1.append("propunere_absenta")
    else:
        obs = [(r[0], cota_exacta(r[1]), bani_exact(r[2]), bani_exact(r[3]), bani_exact(r[4])) if len(r) == 5 else None for r in rand]
        ast = [(n, Decimal(c).normalize(), Decimal(b), Decimal(i), Decimal(t)) for n, c, b, i, t in T1_ASOCIATI]
        if obs != ast:
            e1.append("asociati_T1")
        tot = f.get("total") or []
        if len(tot) != 5 or tuple(bani_exact(x) for x in tot[2:]) != tuple(Decimal(x) for x in T1_TOTAL):
            e1.append("total_T1")
        if not re.search(r"\bnr\.? 1 din 15\.03\.2026, din contul 1171\b", f.get("zona") or ""):
            e1.append("sursa_si_hotararea")
    b = f["butoane"]
    if not any(b[k].get("exista") for k, *_ in BUTOANE):
        e2.append("descarcari_lipsa")
        return {"e.1": e1, "e.2": e2}
    for k, _, text in BUTOANE:
        x = b.get(k) or {}
        if not x.get("exista"):
            e2.append("buton_%s_lipsa" % k)
        elif not x.get("vizibil") or x.get("text") != text or not x.get("acelasi_formular"):
            e2.append("buton_%s" % k)
    v = m.get("valori")
    if not isinstance(v, dict) or not isinstance(v.get("initial"), dict) or not isinstance(v.get("final"), dict):
        e2.append("valori_formular")
    else:
        e2 += ["camp_lipsa:" + c for c, _ in DOC_CAMPURI if v["final"].get(c) is None]
        e2 += ["camp:" + c for c, val in DOC_CAMPURI if v["final"].get(c) is not None and v["final"][c] != val]
        if v["initial"].get("op-exemplare") != EXEMPLARE_F2 or v["final"].get("op-exemplare") != EXEMPLARE_F2:
            e2.append("exemplare_sugerate")
        if not (v["final"].get("op-administrator") or "").strip():
            e2.append("administrator")
        if ("op-administrator" in m.get("completat_de_test", [])) == bool((v["initial"].get("op-administrator") or "").strip()):
            e2.append("administrator_consemnare")
    d = m.get("documente")
    if not isinstance(d, dict) or set(d) != {"docx", "pdf"}:
        e2.append("documente_nemasurate")
        return {"e.1": e1, "e.2": e2}
    for k, ext in (("docx", ".docx"), ("pdf", ".pdf")):
        if not (d[k].get("nume") or "").lower().endswith(ext):
            e2.append("nume_%s" % k)
        e2 += ["%s:%s" % (k, p) for p in d[k].get("judecata", {}).get("probleme", ["nejudecat"])]
    dd, dp = (d[k].get("judecata", {}).get("date") or {} for k in ("docx", "pdf"))
    if dd != dp:
        e2.append("documente_diferite")
    final = v["final"] if isinstance(v, dict) and isinstance(v.get("final"), dict) else {}
    for k in ("docx", "pdf"):   # valorile confirmate în formular, regăsite în fiecare document
        x = d[k].get("judecata", {}).get("date") or {}
        if not x.get("administrator") or x["administrator"] != norm(final.get("op-administrator")):
            e2.append("administrator_%s" % k)
        if x.get("exemplare") != final.get("op-exemplare"):
            e2.append("exemplare_%s" % k)
    if m["note_dupa"] != m["note_inainte"]:
        e2.append("note_create_la_descarcare")
    return {"e.1": e1, "e.2": e2}


def analiza_meniu(m):
    for k in ("antet", "meniu", "drepturi", "firme_cont", "acces", "captura", "ruta"):
        if k not in m:
            raise ValueError("Măsura meniului e incompletă: " + k)
    me = m["meniu"]
    if not isinstance(me, dict) or not isinstance(me.get("carduri"), list):
        raise ValueError("Meniul firmei nu a fost măsurat")
    e3, e4 = [], []
    titlu = me.get("titlu") or ""
    if not titlu.startswith(F1 + " · CUI ") or not re.search(r"CUI \d+", titlu) or F1 not in (m["antet"] or ""):
        e3.append("firma")
    dr, fc = m["drepturi"], m["firme_cont"]
    if not ruta_copie(m["ruta"]):
        e3.append("ruta")
    if m["acces"] != 1 or not isinstance(dr, dict) or dr.get("stare_http") != 200 or dr.get("rol") != ROL_PROBA \
            or not isinstance(fc, dict) or fc.get("stare_http") != 200 or fc.get("f1") is not True:
        e3.append("rol")
    if not (me.get("grup") or "").startswith("Contabilitate") or me.get("deschis") != "true" or not me.get("grup_vizibil") or not me["carduri"] \
            or not all(c.get("vizibil") for c in me["carduri"]):
        e3.append("grup_contabilitate")
    carduri = [c for c in me["carduri"] if c.get("titlu") == TITLU_502 or c.get("id") == CARD_502]
    if not carduri and not me.get("id_502_in_fereastra") and not me.get("titlu_502_in_fereastra"):
        e4.append("card_502_lipsa")
        return {"e.3": e3, "e.4": e4}
    if len(carduri) != 1 or me["carduri"][-1].get("titlu") != TITLU_502 or me["carduri"][-1].get("id") != CARD_502 \
            or me.get("titlu_502_in_fereastra") != 1 or not me["carduri"][-1].get("activ"):
        e4.append("card_502_loc")
    c = m.get("consultanta")
    if not isinstance(c, dict) or not isinstance(c.get("randuri"), list):
        e4.append("fereastra_502")
        return {"e.3": e3, "e.4": e4}
    if F1 not in (c.get("antet") or ""):
        e4.append("firma_502")
    if TITLU_502 not in (c.get("titlu") or ""):
        e4.append("titlu_502")
    r = c["randuri"]
    if [x.get("cod") for x in r] != [cod for cod, _ in MASURI]:
        e4.append("randuri_M1_M5")
        return {"e.3": e3, "e.4": e4}
    for x, (cod, nume) in zip(r, MASURI):
        if not x.get("vizibil") or nume not in (x.get("nume") or ""):   # nume, stare, motiv: textul redat vizibil
            e4.append("nume_" + cod)
        if (x.get("stare") or "") not in PREDICTIE_F1[cod]:
            e4.append("stare_" + cod)
        if x.get("stare") != "Se aplică" and not (x.get("motiv") or "").strip():
            e4.append("motiv_" + cod)
    pl, pe = r[3].get("plafoane"), r[3].get("perioade")
    if not isinstance(pl, list) or len(pl) != 1 or not pl[0].get("vizibil") or lei_exact(pl[0].get("text")) != PLAFON_LEI:
        e4.append("plafon_micro_lei")
    # perioada aceleiași valori: un singur element [data-perioada="plafon_lei"] în rândul M4, vizibil, cu un singur an, 2026
    if not isinstance(pe, list) or len(pe) != 1 or not pe[0].get("vizibil") or re.findall(r"(?<!\d)(?:19|20)\d{2}(?!\d)", pe[0].get("text") or "") != [AN_PLAFON]:
        e4.append("plafon_micro_perioada")
    return {"e.3": e3, "e.4": e4}


def analiza_banca(m):
    for k in ("banca", "ecran", "captura"):
        if k not in m:
            raise ValueError("Măsura Băncii e incompletă: " + k)
    b, ec = m["banca"], m["ecran"]
    if not isinstance(b, dict) or not isinstance(b.get("semne"), list) or not isinstance(ec, dict):
        raise ValueError("Fereastra Bancă nu a fost măsurată")
    e5, e6 = [], []
    if F1 not in (b.get("antet") or "") or F1 not in (ec.get("antet") or ""):
        e5.append("firma")
    if not ruta_copie(ec.get("url")):
        e5.append("ruta")
    if b.get("titlu") != "Bancă" or "Bancă" not in (ec.get("antet") or "") or ec.get("active") != 1 or not re.fullmatch(r"[0-9]+", str(ec.get("nivel"))):
        e5.append("titlu")
    if not isinstance(b.get("martor"), dict) or b["martor"].get("text") != "Importă extras" or not b["martor"].get("vizibil"):
        e5.append("martor")
    s = b["semne"]
    if len(s) != 1:
        e6.append("semne_%d" % len(s))
        return {"e.5": e5, "e.6": e6}
    if s[0].get("title") != AJUTOR_BANCA or s[0].get("aria") != AJUTOR_BANCA or not s[0].get("vizibil") \
            or s[0].get("latime", 0) < 24 or s[0].get("inaltime", 0) < 24:
        e6.append("eticheta")
    a = m.get("ajutor")
    if not isinstance(a, dict) or not isinstance(a.get("pasi"), list) or [p.get("pas") for p in a["pasi"]] != ["inainte", "clic", "x", "redeschidere", "esc"]:
        e6.append("fereastra_ajutor")
        return {"e.5": e5, "e.6": e6}
    p = {x["pas"]: x for x in a["pasi"]}
    n0 = int(ec["nivel"]) if re.fullmatch(r"[0-9]+", str(ec.get("nivel"))) else None
    banca = lambda x: (x.get("stiva") or {}).get("nivel") == str(n0) and (x.get("stiva") or {}).get("active") == 1 \
        and (x.get("stiva") or {}).get("antet") == ec.get("antet") and x.get("asteptat") is True  # noqa: E731
    ajutor = lambda x: (x.get("stiva") or {}).get("nivel") == str(n0 + 1) and (x.get("stiva") or {}).get("active") == 1 \
        and "Ajutor" in ((x.get("stiva") or {}).get("antet") or "") and x.get("asteptat") is True  # noqa: E731
    if n0 is None or not banca(p["inainte"]):
        e6.append("stare_initiala")
    if not p["clic"].get("centru_atins") or not p["redeschidere"].get("centru_atins"):
        e6.append("gest")
    if not ajutor(p["clic"]):
        e6.append("fereastra_la_clic")
    if not banca(p["x"]):
        e6.append("inchidere_x")
    if not ajutor(p["redeschidere"]) or p["redeschidere"].get("sectiuni") != p["clic"].get("sectiuni") \
            or (p["redeschidere"].get("stiva") or {}).get("antet") != (p["clic"].get("stiva") or {}).get("antet"):
        e6.append("redeschidere")
    if not banca(p["esc"]):
        e6.append("inchidere_esc")
    sec = p["clic"].get("sectiuni")
    if not isinstance(sec, list) or [x.get("id") for x in sec] != list(ORDINE_BANCA) or not all(x.get("vizibil") for x in sec):
        e6.append("sectiuni")
    elif isinstance(a.get("registru"), list):
        for x, y in zip(sec, a["registru"]):
            if norm(x.get("titlu")) != y["titlu"] or [norm(t) for t in x.get("linii") or []] != y["linii"]:
                e6.append("sectiune_%s" % x.get("id"))
    else:
        e6.append("registru")
    return {"e.5": e5, "e.6": e6}


def perechi(m):
    """{(etapa, țintă): [clic1, clic2]} din clicurile consemnate; o dublură sau o țintă străină face măsura invalidă."""
    out = {}
    for c in m["clicuri"]:
        k = (c.get("etapa"), c.get("tinta"))
        if k not in PROFIL_BAZA or c.get("clic") not in (1, 2):
            raise ValueError("Clic străin: %r" % (k,))
        out.setdefault(k, {})
        if c["clic"] in out[k]:
            raise ValueError("Clic dublat: %r" % (k,))
        out[k][c["clic"]] = c
    return {k: [v.get(1), v.get(2)] for k, v in out.items()}


def clic_valid(c):
    """Gestul și succesiunea completă aria-expanded a unui clic: centrul atins, exact un eveniment de sistem la document, stări coerente
    (aria-expanded, hidden, vizibilitate, etichetă), valoarea veche a primei mutații = starea inițială, fiecare mutație schimbă valoarea,
    ultima duce în starea finală."""
    if not (isinstance(c, dict) and isinstance(c.get("centru"), dict) and c["centru"].get("hit") is True and c.get("ajuns_la_document") == [True]
            and isinstance(c.get("captura"), str) and isinstance(c.get("mutatii"), list) and c.get("stare_inainte") in (DESCHIS, INCHIS)
            and c.get("stare_dupa") in (DESCHIS, INCHIS) and isinstance(c.get("document"), int) and c.get("conectat") is True and ruta_copie(c.get("ruta"))):
        return False
    sec = list(c["mutatii"]) + [c["stare_dupa"][0]]
    if not c["mutatii"]:
        return c["stare_dupa"] == c["stare_inainte"]
    return sec[0] == c["stare_inainte"][0] and all(a != b for a, b in zip(sec, sec[1:])) and all(x in ("true", "false") for x in sec)


def tinta_asteptata(tinta, inv):
    """Identitatea țintei în inventarul stabil al etapei: (ordinalul, textul integral); None dacă lipsește sau nu e unică."""
    if not isinstance(inv, dict):
        return None
    if tinta == "semnal":
        lista, g = inv.get("semnale"), [0]
    elif tinta == "avertisment":
        lista, g = inv.get("avertismente"), [0]
    else:
        lista = inv.get("carduri")
        g = [i for i, c in enumerate(lista or []) if isinstance(c, str) and c.startswith(tinta)]
    if not isinstance(lista, list) or len(g) != 1 or g[0] >= len(lista) or not lista[g[0]]:
        return None
    return g[0], lista[g[0]]


def tinta_ok(tinta, t, inv):
    """Ținta clicului este chiar ținta din inventarul etapei: același ordinal și același text integral, în zona ei."""
    a = tinta_asteptata(tinta, inv)
    if not isinstance(t, dict) or a is None or (t.get("ordinal"), t.get("text")) != a:
        return False
    if tinta == "semnal":
        return t.get("tip") == "semnal" and "Coerență TVA" in (t.get("grup") or "") and t.get("in_corp") is True
    if tinta == "avertisment":
        return t.get("tip") == "avertisment" and t.get("in_avertisment") is True
    return t.get("tip") == "rezumat" and t.get("in_corp") is True


def analiza_detalii(m):
    for k in ("identitate", "luni", "etape", "clicuri", "module", "captura"):
        if k not in m:
            raise ValueError("Măsura «▾ detalii» e incompletă: " + k)
    mod = m["module"]
    if not isinstance(mod, list) or not mod or len({x.get("sha256") for x in mod}) != 1 or any(
            x.get("stare_http") != 200 or not re.fullmatch(r"[0-9a-f]{64}", str(x.get("sha256"))) or not re.search(r"/static/js/ds_piese\.js\?v=[0-9a-f]{10}$", str(x.get("url")))
            or x.get("tip") != "script" for x in mod) or sorted(x.get("document") for x in mod) != [1, 2]:
        raise ValueError("Varianta servită a ds_piese.js nu e identificată în documentele probei")
    e7, e8 = [], []
    ident = m["identitate"]
    if F1 not in (ident.get("antet") or "") or not isinstance(ident.get("tenant"), int):
        e7.append("firma")
    if not ruta_copie(ident.get("ruta")):
        e7.append("ruta")
    luni = m["luni"]
    if [x.get("luna_ceruta") for x in luni] != ["la deschidere", "2026-9", "2026-10"]:
        e7.append("luni")
    for x in luni:
        if x.get("stare_http") != 200 or x.get("luna_in_selector") != SELECTOR.get(x.get("luna_ceruta")) \
                or (x.get("luna_ceruta") != "la deschidere" and x.get("corp_inlocuit") is not True):
            e7.append("luna_%s" % x.get("luna_ceruta"))
    if [e.get("etapa") for e in m["etape"]] != list(ORDINE_ETAPE):
        raise ValueError("Etapele «▾ detalii» nu sunt cele patru, o dată, în ordine")
    for e in m["etape"]:
        etapa, inv = e["etapa"], e.get("inventar")
        if not isinstance(inv, dict) or not all(isinstance(inv.get(k), list) and all(isinstance(x, str) and x for x in inv[k]) for k in ("semnale", "carduri", "avertismente")):
            e7.append("inventar_" + etapa)
            continue
        if inv.get("stabil") is not True:
            e7.append("inventar_nestabil_" + etapa)
        if etapa == "Declarații":
            calc = ["avertisment"] if inv["avertismente"] else []
            dc = e.get("declaratie") or {}
            if F1 not in (dc.get("antet") or "") or dc.get("tip") != "d394" or (dc.get("an"), dc.get("luna")) != ("2026", "10") \
                    or not inv["avertismente"] or dc.get("primul_avertisment") != inv["avertismente"][0]:
                e7.append("declaratie_D394")
        else:
            calc = (["semnal"] if inv["semnale"] else []) + [p for p in ("Statul de plată", "SPV") if any(c.startswith(p) for c in inv["carduri"])]
        if e.get("prezente") != calc or e.get("absente") != [t for t in ABSENTE.get(etapa, ()) if t not in calc] \
                or not isinstance(inv.get("butoane"), int) or inv["butoane"] < len(calc):
            e7.append("inventar_discordant_" + etapa)
        e7 += ["tinta_%s_%s" % (etapa, t) for t in TINTE[etapa] if t not in calc or tinta_asteptata(t, inv) is None]
        e7 += ["absenta_%s_%s" % (etapa, t) for t in ABSENTE.get(etapa, ()) if t in calc]
    p = perechi(m)
    documente = {x["document"] for x in mod}
    inventare = {e["etapa"]: e.get("inventar") for e in m["etape"]}
    for k in PERECHI:
        c1, c2 = p.get(k, [None, None])
        if not clic_valid(c1) or not clic_valid(c2) or c2["stare_inainte"] != c1["stare_dupa"] or c1["stare_inainte"] != INCHIS \
                or not tinta_ok(k[1], c1.get("tinta_observata"), inventare.get(k[0])) or c1.get("tinta_observata") != c2.get("tinta_observata") \
                or c1["document"] != c2["document"] or c1["document"] not in documente or c1["document"] != (2 if k[0] == "Declarații" else 1):
            e8.append("pereche_%s_%s" % k)
            continue
        if c1["mutatii"] != ["false"] or c1["stare_dupa"] != DESCHIS or c2["mutatii"] != ["true"] or c2["stare_dupa"] != INCHIS:
            e8.append("comutari_%s_%s" % k)
    return {"e.7": e7, "e.8": e8}


def profil_detalii(m):
    """Profilul celor 16 clicuri: {(etapa, țintă): ((mutații, stare), (mutații, stare))}; None dacă o pereche lipsește sau e invalidă."""
    p = perechi(m)
    out = {}
    for k in PERECHI:
        c1, c2 = p.get(k, [None, None])
        if not clic_valid(c1) or not clic_valid(c2) or c1["stare_inainte"] != INCHIS or c2["stare_inainte"] != c1["stare_dupa"]:
            return None
        out[k] = ((len(c1["mutatii"]), stare_nume(c1["stare_dupa"])), (len(c2["mutatii"]), stare_nume(c2["stare_dupa"])))
    return out


def sectiuni_consultanta(c):
    """Secțiunile paginii care țin de consultanță: după conținut (una din cheile 501/502) sau după titlu; secțiunea șefului nu intră."""
    return [s for s in c["sectiuni"] if s.get("controls") != SEF
            and (set(s.get("chei") or ()) & set(CHEI_CONS) or TITLU_SECTIUNE.match(norm(s.get("titlu") or "").casefold()))]


def analiza_cabinet(m):
    """e.9. Pagina nedesenată, o fereastră deschisă peste ea sau sesiunea greșită sunt ValueError (proba nu s-a executat), nu un roșu."""
    for k in ("cabinet", "drepturi", "firme_cont", "captura", "ruta"):
        if k not in m:
            raise ValueError("Măsura cabinetului e incompletă: " + k)
    c, dr, fc = m["cabinet"], m["drepturi"], m["firme_cont"]
    if not isinstance(c, dict) or c.get("grila") is not True or c.get("overlay") != 0 or not ruta_copie(m["ruta"]):
        raise ValueError("Pagina cabinetului nu a fost desenată")
    directe = [x for x in c["copii"] if x.get("tip") == "card"]
    if tuple(x.get("cheie") for x in directe if x.get("cheie") not in CHEI_CONS) != DIRECTE or not all(x.get("vizibil") for x in directe):
        raise ValueError("Pagina cabinetului nu are cele șase carduri de sus")
    if not isinstance(dr, dict) or dr.get("stare_http") != 200 or dr.get("rol") != ROL_PROBA \
            or not isinstance(fc, dict) or fc.get("stare_http") != 200 or not isinstance(fc.get("numar"), int) or fc["numar"] < 1:
        raise ValueError("Sesiunea cabinetului nu e a contului de probă cu firme")
    cons = sectiuni_consultanta(c)
    if not cons and not set(c["chei_pagina"]) & set(CHEI_CONS) and not c.get("titluri_consultanta"):
        if "deschis" in m or "inchis" in m:
            raise ValueError("Măsuri de secțiune fără secțiune")
        return {"e.9": ["sectiune_consultanta_lipsa"]}
    e = []
    if len(cons) != 1 or c.get("titluri_consultanta") != 1:
        return {"e.9": ["sectiune_unica"]}
    s, n = cons[0], len(c["copii"])
    if not ID_DOM.fullmatch(s.get("controls") or "") or not s.get("continut") or not s.get("continut_in_sectiune") or not s.get("buton_vizibil"):
        e.append("piesa_de_pliere")
    if s.get("expandat") != "false" or s.get("continut_vizibil"):
        e.append("pliata_implicit")
    if not TITLU_SECTIUNE.fullmatch(norm(s.get("titlu") or "").casefold()):
        e.append("titlu_sectiune")
    if s.get("index_in_grila") != n - 1 or [x.get("tip") for x in c["copii"]].count("alt"):
        e.append("sectiune_ultima")
    sef = [x for x in c["sectiuni"] if x.get("controls") == SEF]
    if len(sef) > 1 or (sef and sef[0].get("index_in_grila") != s.get("index_in_grila", 0) - 1) \
            or [x.get("tip") for x in c["copii"]].count("sectiune") != 1 + len(sef):
        e.append("dupa_sectiunea_sefului")
    afara = [x.get("cheie") for x in directe] + [k for x in sef for k in (x.get("chei") or ())]
    if set(afara) & set(CHEI_CONS) or any(c["chei_pagina"].count(k) != 1 for k in CHEI_CONS):
        e.append("carduri_in_afara_sectiunii")
    d, i = m.get("deschis"), m.get("inchis")
    if not isinstance(d, dict) or not isinstance(i, dict):
        e.append("deschidere_nemasurata")
        return {"e.9": e}
    sd, si = sectiuni_consultanta(d) if d.get("grila") is True else [], sectiuni_consultanta(i) if i.get("grila") is True else []
    if len(sd) != 1 or sd[0].get("controls") != s.get("controls") or sd[0].get("expandat") != "true" or not sd[0].get("continut_vizibil") \
            or d.get("overlay") != 0:
        e.append("deschidere")
        return {"e.9": e}
    carduri = sd[0].get("carduri") or []
    if tuple(x.get("cheie") for x in carduri) != CHEI_CONS or tuple(sd[0].get("chei") or ()) != CHEI_CONS:
        e.append("carduri_501_502")
    elif tuple(x.get("titlu") for x in carduri) != TITLURI_CONS:
        e.append("titluri_carduri")
    if not carduri or not all(x.get("vizibil") and x.get("activ") and (x.get("sinteza") or "").strip() for x in carduri):
        e.append("rezumat_card")
    if not TITLU_SECTIUNE.fullmatch(norm(sd[0].get("titlu") or "").casefold()):
        e.append("titlu_sectiune_deschisa")
    if len(si) != 1 or si[0].get("expandat") != "false" or si[0].get("continut_vizibil") or i.get("overlay") != 0:
        e.append("pliere_la_loc")
    return {"e.9": e}


ANALIZE = {"dividend": (("e.1", "e.2"), analiza_dividend), "meniu": (("e.3", "e.4"), analiza_meniu),
           "banca": (("e.5", "e.6"), analiza_banca), "detalii": (("e.7", "e.8"), analiza_detalii), "cabinet": (("e.9",), analiza_cabinet)}


def analiza(masuri):
    """{id: {dimensiune: [motive]}} pe toate măsurile; o măsură lipsă, străină sau incompletă e ValueError (nu e un roșu prezis)."""
    if set(masuri) != set(IDS):
        raise ValueError("Lipsesc identificatori")
    out = {i: {} for i in IDS}
    for zona, (ids, fn) in ANALIZE.items():
        dims = ["%dx%d" % d for d in DIM_ID[ids[0]]]
        for i in ids:
            if set(masuri[i]) != set(dims):
                raise ValueError("Rezoluții incomplete pentru " + i)
        for z in dims:
            m = masuri[ids[0]][z]
            if any(masuri[i][z] != m for i in ids) or m.get("zona") != zona or m.get("viewport") != z:
                raise ValueError("Măsuri incompatibile la %s %s" % (zona, z))
            for i, motive in fn(m).items():
                out[i][z] = motive
    return out


def test_fundatie_17_5_F6(browser, capsys):
    from conftest import BAZA, CAPTURI, alege_perioada, sesiune, sql
    from core.ceas_proba import MOMENT_REF
    from declaratie_tip import alege_tipul
    from e2e_ferestre_17_5_Q5 import acasa, firma, origine_proba

    origine_proba(BAZA)
    d = Path(CAPTURI) / LOT
    d.mkdir(parents=True, exist_ok=True)
    radacina = Path(__file__).resolve().parents[2]
    firme = {n: sql("SELECT id, schema_name, cui FROM public.tenants WHERE nume = %s", (n,)) for n in (F1, F2)}
    assert all(len(v) == 1 for v in firme.values()), "firmele de probă F1/F2 lipsesc sau sunt duble"
    (id1, s1, cui1), (id2, s2, cui2) = firme[F1][0], firme[F2][0]
    assert re.fullmatch(r"tenant_[0-9]+", s1) and re.fullmatch(r"tenant_[0-9]+", s2), "schemele F1/F2"
    cont = sql("SELECT id FROM public.users WHERE email = %s", (CONT_PROBA,))
    assert len(cont) == 1, "contul de probă lipsește"
    uid = cont[0][0]
    stare, abateri = premise_date(sql, s2)
    assert not abateri, "PREMISE_F6: " + "; ".join(abateri)   # înaintea oricărei scrieri
    reg = (radacina / "FUNCTIONALITATI.csv").read_bytes()
    (d / "FUNCTIONALITATI.csv").write_bytes(reg)   # registrul servit, recitit de cititor (amprenta C9 în cititor)
    for f, nume in (("static/js/ds_piese.js", "exportat_ds_piese.js"), ("static/js/api.js", "exportat_api.js")):
        (d / nume).write_bytes((radacina / f).read_bytes())   # fișierele arborelui servit, confruntate de cititor cu modulul încărcat
    arbore = {"ds_piese_sha256": sha((d / "exportat_ds_piese.js").read_bytes()), "api_sha256": sha((d / "exportat_api.js").read_bytes()),
              "functionalitati_sha256": sha(reg)}   # arborele servit (commitul și arborele Git sunt în rulare.meta a rulatorului nativ)
    registru = asteptat_ajutor(reg.decode("utf-8"))
    note = lambda: sql('SELECT count(*) FROM "%s".inregistrari' % s2)[0][0]  # noqa: E731
    acces = sql("SELECT count(*) FROM public.user_tenants WHERE user_id = %s AND tenant_id = %s", (uid, id1))[0][0]
    capturi = {}

    def stabil(pg):
        pg.evaluate(STABIL)

    def poza(pg, nume, z, **scena):
        f = d / ("%s.png" % nume)
        if f.exists():
            raise ValueError("captură repetată: " + f.name)
        pg.screenshot(path=str(f))
        capturi[f.name] = dict(scena, rezolutie=z, sha256=sha(f.read_bytes()), stiva=pg.evaluate(JS_STIVA))
        return f.name

    def api(pg, cale):
        return pg.evaluate("""async (cale) => { const t = sessionStorage.getItem('iconta_token');
          const r = await fetch(cale, {headers: {Authorization: 'Bearer ' + t}, cache: 'no-store'}); let d = null; try { d = await r.json(); } catch (e) {}
          return {status: r.status, date: d}; }""", cale)

    def dividend(pg, z):
        firma(pg, F2, "#fa-operatiuni")
        pg.locator(TOP + 'button[data-op="asociati"]').click()
        pg.locator(TOP + "#op-operatie").wait_for(state="attached")
        pg.locator(TOP + "#op-operatie").select_option("dividend")
        for camp, val in T1_FORMULAR:
            loc = pg.locator(TOP + "#op-" + camp)
            loc.fill(val)
            loc.dispatch_event("change")
        pg.locator(TOP + "#op-interimar").select_option("0")
        pg.locator(TOP + "#op-div-tabel").wait_for(state="visible", timeout=30000)
        stabil(pg)
        pg.wait_for_timeout(400)
        f = pg.evaluate(JS_DIVIDEND)
        m = {"zona": "dividend", "viewport": z, "antet": f.get("antet"), "formular": f, "note_inainte": note(), "ruta": pg.url}
        if all(f["butoane"][k].get("exista") for k, *_ in BUTOANE):
            ids = [c for c, _ in DOC_CAMPURI] + ["op-administrator", "op-exemplare"]
            initial = pg.evaluate(JS_VALORI, ids)
            facut = []
            for cid, val in DOC_CAMPURI:
                loc = pg.locator(TOP + "#" + cid)
                if not loc.count():
                    continue
                if loc.evaluate("e => e.tagName") == "SELECT":
                    loc.select_option(val)
                else:
                    loc.fill(val)
                    loc.dispatch_event("change")
                facut.append(cid)
            if pg.locator(TOP + "#op-administrator").count() and not (initial.get("op-administrator") or "").strip():
                pg.locator(TOP + "#op-administrator").fill(ADMIN_IMPLICIT)
                pg.locator(TOP + "#op-administrator").dispatch_event("change")
                facut.append("op-administrator")
            stabil(pg)
            m.update({"valori": {"initial": initial, "final": pg.evaluate(JS_VALORI, ids)}, "completat_de_test": facut})
            docs = {}
            for cheie, sel, _ in BUTOANE:
                with pg.expect_download(timeout=60000) as dl:
                    pg.locator(TOP + sel).click()
                nume = "hotarare_%s.%s" % (z, cheie)
                dl.value.save_as(str(d / nume))
                continut = (d / nume).read_bytes()
                docs[cheie] = {"fisier": nume, "nume": dl.value.suggested_filename, "sha256": sha(continut), "octeti": len(continut),
                               "judecata": judeca_document(cheie, continut)}
            m["documente"] = docs
        m["note_dupa"] = note()
        m["captura"] = poza(pg, "dividend_%s" % z, z, zona="dividend", scena="formular")
        return m

    def meniu(pg, z):
        acasa(pg)
        pg.locator("button.cab-card:has([data-cheie='firme'])").click()
        pg.locator(TOP + "#opt-existente").click()
        pg.locator(TOP + "#firme-lista button.firme-rand").filter(has=pg.get_by_text(F1, exact=True)).click()
        pg.locator(TOP + "#fg-contabilitate").wait_for(state="attached")
        b = pg.locator(TOP + "#fg-contabilitate button.firme-grup-btn")
        if b.get_attribute("aria-expanded") != "true":
            b.click()
        pg.locator(TOP + "#fgc-contabilitate").wait_for(state="visible")
        stabil(pg)
        me = pg.evaluate(JS_MENIU)
        dr, tn = api(pg, "/eu/drepturi"), api(pg, "/tenants")
        lista = ((tn.get("date") or {}).get("tenants") or []) if isinstance(tn.get("date"), dict) else []
        m = {"zona": "meniu", "viewport": z, "antet": me.get("antet"), "meniu": me, "acces": acces, "ruta": pg.url,
             "drepturi": {"stare_http": dr.get("status"), "rol": (dr.get("date") or {}).get("rol") if isinstance(dr.get("date"), dict) else None},
             "firme_cont": {"stare_http": tn.get("status"), "f1": any(t.get("id") == id1 and t.get("nume") == F1 for t in lista)},
             "captura": poza(pg, "meniu_%s" % z, z, zona="meniu", scena="meniu")}
        if pg.locator(TOP + "#" + CARD_502).count():
            pg.locator(TOP + "#" + CARD_502).click()
            try:
                pg.locator(TOP + "[data-masura]").first.wait_for(state="visible", timeout=30000)
            except Exception:   # noqa: BLE001 — fereastra fără rânduri e o măsură (fereastra_502), nu o eroare de probă
                pass
            stabil(pg)
            pg.wait_for_timeout(400)
            m["consultanta"] = pg.evaluate(JS_CONSULTANTA)
            m["captura_502"] = poza(pg, "consultanta_%s" % z, z, zona="meniu", scena="consultanta")
        return m

    def cabinet(pg, z):
        acasa(pg)
        pg.wait_for_function("() => !!document.querySelector('.cab-grila') && !document.querySelector('.cab-grila').innerText.includes('se încarcă')",
                             timeout=60000)
        stabil(pg)
        pg.wait_for_timeout(800)
        stabil(pg)
        c = pg.evaluate(JS_CABINET)
        dr, tn = api(pg, "/eu/drepturi"), api(pg, "/tenants")
        lista = ((tn.get("date") or {}).get("tenants") or []) if isinstance(tn.get("date"), dict) else []
        m = {"zona": "cabinet", "viewport": z, "cabinet": c, "ruta": pg.url,
             "drepturi": {"stare_http": dr.get("status"), "rol": (dr.get("date") or {}).get("rol") if isinstance(dr.get("date"), dict) else None},
             "firme_cont": {"stare_http": tn.get("status"), "numar": len(lista)}}
        cons = sectiuni_consultanta(c) if c.get("grila") is True else []
        if len(cons) == 1 and ID_DOM.fullmatch(cons[0].get("controls") or ""):
            b = pg.locator('button.firme-grup-btn[aria-controls="%s"]' % cons[0]["controls"])
            b.scroll_into_view_if_needed()
            stabil(pg)
            m["captura"] = poza(pg, "cabinet_%s" % z, z, zona="cabinet", scena="cabinet")
            b.click()
            stabil(pg)
            pg.wait_for_timeout(400)
            b.scroll_into_view_if_needed()
            stabil(pg)
            m["deschis"] = pg.evaluate(JS_CABINET)
            m["captura_deschis"] = poza(pg, "cabinet_deschis_%s" % z, z, zona="cabinet", scena="cabinet_deschis")
            b.click()
            stabil(pg)
            pg.wait_for_timeout(400)
            m["inchis"] = pg.evaluate(JS_CABINET)
        else:
            m["captura"] = poza(pg, "cabinet_%s" % z, z, zona="cabinet", scena="cabinet")
        return m

    def asteapta_nivel(pg, n):
        try:
            pg.wait_for_function(JS_NIVEL, arg=n, timeout=10000)
            stabil(pg)
            return True
        except Exception:   # noqa: BLE001 — nivelul neatins e o măsură (refuzul e.6), nu o eroare de probă
            return False

    def banca(pg, z):
        firma(pg, F1, "#fa-banca")
        pg.locator(TOP + "#bk-rezumat h2.pf-titlu").wait_for(state="visible")
        stabil(pg)
        b = pg.evaluate(JS_BANCA)
        ec = dict(pg.evaluate(JS_STIVA), url=pg.url)
        m = {"zona": "banca", "viewport": z, "banca": b, "ecran": ec, "captura": poza(pg, "banca_%s" % z, z, zona="banca", scena="banca")}
        s = b.get("semne") or []
        if len(s) == 1 and s[0].get("title") == AJUTOR_BANCA and re.fullmatch(r"[0-9]+", str(ec.get("nivel"))):
            n0 = int(ec["nivel"])
            sel = (TOP + "#bk-rezumat h2.pf-titlu [data-ajutor]").strip()
            pasi = [{"pas": "inainte", "stiva": pg.evaluate(JS_STIVA), "asteptat": True}]
            c = pg.evaluate(CENTRU, sel)
            pg.mouse.click(c["x"], c["y"])
            ok = asteapta_nivel(pg, n0 + 1)
            pasi.append({"pas": "clic", "centru_atins": bool(c["hit"]), "asteptat": ok, "stiva": pg.evaluate(JS_STIVA), "sectiuni": pg.evaluate(JS_SECTIUNI),
                         "captura": poza(pg, "ajutor_%s" % z, z, zona="banca", scena="ajutor")})
            x = pg.locator(TOP + "button.nav-x").last
            if x.count():
                x.click()
            ok = asteapta_nivel(pg, n0)
            pasi.append({"pas": "x", "asteptat": ok, "stiva": pg.evaluate(JS_STIVA)})
            c = pg.evaluate(CENTRU, sel)
            if c:
                pg.mouse.click(c["x"], c["y"])
            ok = asteapta_nivel(pg, n0 + 1)
            pasi.append({"pas": "redeschidere", "centru_atins": bool(c and c["hit"]), "asteptat": ok, "stiva": pg.evaluate(JS_STIVA),
                         "sectiuni": pg.evaluate(JS_SECTIUNI)})
            pg.keyboard.press("Escape")
            ok = asteapta_nivel(pg, n0)
            pasi.append({"pas": "esc", "asteptat": ok, "stiva": pg.evaluate(JS_STIVA)})
            m["ajutor"] = {"pasi": pasi, "registru": registru}
        return m

    def doua_clicuri(pg, m, z, etapa, tinta, tip, prefix, document):
        t = pg.evaluate(TINTA, [tip, prefix])
        if not t:
            m["clicuri"].append({"etapa": etapa, "tinta": tinta, "absent": True})
            return
        pg.evaluate(URMARESTE)
        for nr in (1, 2):
            pg.evaluate(CENTRU_BTN)
            stabil(pg)
            c = pg.evaluate(CENTRU_BTN)
            pg.evaluate(COLECTEAZA)
            st0 = pg.evaluate(STARE)
            pg.mouse.click(c["x"], c["y"])
            stabil(pg)
            pg.wait_for_timeout(300)
            stabil(pg)
            col = pg.evaluate(COLECTEAZA)
            st1 = pg.evaluate(STARE)
            conectat = pg.evaluate(CONECTAT)
            cap = poza(pg, fis("detalii", etapa, tinta, "clic%d" % nr, z), z, zona="detalii", scena="clic", etapa=etapa, tinta=tinta, clic=nr)
            m["clicuri"].append(dict({"etapa": etapa, "tinta": tinta, "clic": nr, "centru": c, "stare_inainte": st0, "stare_dupa": st1,
                                      "captura": cap, "tinta_observata": t, "document": document, "ruta": pg.url, "conectat": conectat}, **col))
        pg.evaluate(INCHEIE)

    def inventar_stabil(pg, max_s=20.0, liniste_s=1.5):
        """Inventarul brut al butoanelor «detalii» după 1,5 s fără schimbări (secțiunile asincrone, ca SPV, desenate); ceasul procesului de test."""
        t0 = din = time.monotonic()
        ultim = None
        while True:
            inv = pg.evaluate(INVENTAR)
            cheie = json.dumps(inv, sort_keys=True, ensure_ascii=False)
            if cheie != ultim:
                ultim, din = cheie, time.monotonic()
            elif time.monotonic() - din >= liniste_s:
                return dict(inv, stabil=True)
            if time.monotonic() - t0 > max_s:
                return dict(inv, stabil=False)
            pg.wait_for_timeout(250)

    def luna(pg, valoare, tid):
        an, l = valoare.split("-")
        vechi = pg.evaluate_handle("() => document.querySelector('.fereastra-overlay:not(.fundal) .cf-corp')")
        tipar = re.compile(r"/control-fiscal/%s\?an=%s&luna=%s(?:&|$)" % (tid, an, l))
        with pg.expect_response(lambda r: r.request.method == "GET" and bool(tipar.search(r.url)), timeout=60000) as ri:
            pg.locator(TOP + "#cf-luna-comparata").select_option(valoare)
        pg.wait_for_function("""([v, luna]) => !v.isConnected && !!document.querySelector('.fereastra-overlay:not(.fundal) .cf-corp')
            && document.querySelector('.fereastra-overlay:not(.fundal) #cf-luna-comparata').value === luna""", arg=[vechi, valoare], timeout=60000)
        stabil(pg)
        return {"luna_ceruta": valoare, "stare_http": ri.value.status, "corp_inlocuit": True,
                "luna_in_selector": pg.locator(TOP + "#cf-luna-comparata").input_value()}

    def modul(r, document):
        corp = r.body()   # octeții primiți de documentul curent, citiți cât documentul e încă activ
        nume = "servit_ds_piese_%d.js" % document
        (d / nume).write_bytes(corp)
        return {"document": document, "url": r.url.replace(origine_proba(BAZA), ""), "stare_http": r.status, "tip": r.request.resource_type,
                "sha256": sha(corp), "fisier": nume}

    def detalii(pg, z):
        m = {"zona": "detalii", "viewport": z, "luni": [], "etape": [], "clicuri": [], "module": [], "arbore": arbore}
        cdp = pg.context.new_cdp_session(pg)
        cdp.send("Network.enable")
        cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})   # fiecare document își încarcă modulul din rețea
        with pg.expect_response(lambda r: bool(MODUL.search(r.url)), timeout=60000) as rm, \
                pg.expect_response(lambda r: r.request.method == "GET" and bool(re.search(r"/control-fiscal/[0-9]+(?:\?|$)", r.url)), timeout=60000) as ri0:
            firma(pg, F1, "#fa-control")
        m["module"].append(modul(rm.value, 1))
        pg.wait_for_selector(TOP + "#cf-luna-comparata", state="attached", timeout=60000)
        stabil(pg)
        pg.wait_for_timeout(800)
        tid = next(t["id"] for t in api(pg, "/tenants")["date"]["tenants"] if t["nume"] == F1)
        m["identitate"] = {"antet": pg.evaluate("() => {" + SUS + TXT + "return top ? txt(top.querySelector('.fereastra-antet, header')) : null; }"),
                           "tenant": tid, "ruta": pg.url}
        m["luni"].append({"luna_ceruta": "la deschidere", "stare_http": ri0.value.status,
                          "luna_in_selector": pg.locator(TOP + "#cf-luna-comparata").input_value()})
        for etapa, val in ETAPE:
            if val:
                m["luni"].append(luna(pg, val, tid))
            inv = inventar_stabil(pg)
            prezente = (["semnal"] if inv["semnale"] else []) + [p for p in ("Statul de plată", "SPV") if any(c.startswith(p) for c in inv["carduri"])]
            cap = poza(pg, fis("detalii", etapa, "inainte", z), z, zona="detalii", scena="etapa", etapa=etapa)
            if etapa == "10":
                m["captura"] = cap
            m["etape"].append({"etapa": etapa, "inventar": inv, "prezente": prezente,
                               "absente": [t for t in ABSENTE.get(etapa, ()) if t not in prezente], "captura": cap})
            for tinta in TINTE[etapa]:
                doua_clicuri(pg, m, z, etapa, tinta, "semnal" if tinta == "semnal" else "rezumat", None if tinta == "semnal" else tinta, 1)
        with pg.expect_response(lambda r: bool(MODUL.search(r.url)), timeout=60000) as rm2:
            firma(pg, F1, "#fa-declaratii")
        m["module"].append(modul(rm2.value, 2))
        pg.wait_for_selector(TOP + "#dec-tip", state="attached", timeout=60000)
        alege_tipul(pg, "d394", zona=TOP)
        pg.wait_for_selector(TOP + "#dec-an", timeout=10000)
        alege_perioada(pg, 2026, 10, zona=TOP)
        dc = pg.evaluate("() => {" + SUS + TXT + """ const v = s => { const e = top ? top.querySelector(s) : null; return e ? e.value : null; };
            return {tip: v('#dec-tip'), an: v('#dec-an'), luna: v('#dec-luna')}; }""")   # alegerea, citită înainte de «Continuă»
        pg.locator(TOP + "#dec-continua").click()
        pg.wait_for_selector(TOP + "#dec-rezultat, " + TOP + ".dec-eroare", timeout=120000)
        pg.wait_for_timeout(1500)
        stabil(pg)
        inv = inventar_stabil(pg)
        dc["antet"] = pg.evaluate("() => {" + SUS + TXT + "return top ? txt(top.querySelector('.fereastra-antet, header')) : null; }")
        dc["primul_avertisment"] = inv["avertismente"][0] if inv["avertismente"] else None
        prezente = ["avertisment"] if inv["avertismente"] else []
        m["etape"].append({"etapa": "Declarații", "inventar": inv, "declaratie": dc, "prezente": prezente, "absente": [],
                           "captura": poza(pg, fis("detalii", "Declarații", "inainte", z), z, zona="detalii", scena="etapa", etapa="Declarații")})
        doua_clicuri(pg, m, z, "Declarații", "avertisment", "avertisment", None, 2)
        return m

    facute = []
    try:
        pregateste_date(sql, s2, stare, facute)
        masuri = {i: {} for i in IDS}
        erori = []
        for w, h in DIM:
            z = "%dx%d" % (w, h)
            ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
            try:
                ctx.clock.set_fixed_time(MOMENT_REF)
                ctx.add_init_script(sesiune(CONT_PROBA))
                pg = ctx.new_page()
                pg.on("pageerror", lambda e: erori.append(str(e)[:300]))
                pg.goto(BAZA + "/", wait_until="domcontentloaded")
                for nume, fn in (("cabinet", cabinet), ("dividend", dividend), ("meniu", meniu), ("banca", banca)) + ((("detalii", detalii),) if (w, h) in DIM_DETALII else ()):
                    m = fn(pg, z)
                    for i in ANALIZE[nume][0]:
                        masuri[i][z] = m
            finally:
                ctx.close()
        for i, (zona, f) in zip(IDS, (("dividend", "captura"), ("dividend", "captura"), ("meniu", "captura"), ("meniu", "captura"),
                                       ("banca", "captura"), ("banca", "captura"), ("detalii", "captura"), ("detalii", None), ("cabinet", "captura"))):
            z = "%dx%d" % DIM_ID[i][0]
            sursa = masuri[i][z]["clicuri"][-1]["captura"] if f is None else masuri[i][z][f]
            (d / ("%s.png" % i)).write_bytes((d / sursa).read_bytes())
        (d / "masuri.json").write_text(json.dumps(masuri, ensure_ascii=False, default=str), encoding="utf-8")
        (d / "capturi.json").write_text(json.dumps(capturi, ensure_ascii=False), encoding="utf-8")
        (d / "erori.json").write_text("{}", encoding="utf-8")
        (d / "erori_pagina.json").write_text(json.dumps(erori, ensure_ascii=False), encoding="utf-8")   # informativ, nejudecat
        (d / "partiale.json").write_text("{}", encoding="utf-8")
        rez = analiza(json.loads((d / "masuri.json").read_text(encoding="utf-8")))
        verdicte = {i: all(not motive for motive in rez[i].values()) for i in IDS}
        with capsys.disabled():
            for i in IDS:
                print("VERDICT", i, "trece" if verdicte[i] else "pica", flush=True)
        assert all(verdicte.values()), "F6_FUNDATIE"
    finally:
        probleme = restaureaza_date(sql, s2, stare, facute)
        (d / "restaurare.json").write_text(json.dumps({"abateri": probleme, "ramase": [list(map(str, x)) for x in facute]}, ensure_ascii=False), encoding="utf-8")
        if probleme or facute:
            raise AssertionError("RESTAURARE_F6: " + "; ".join(probleme))
