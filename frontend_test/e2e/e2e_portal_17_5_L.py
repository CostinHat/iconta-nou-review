# -*- coding: utf-8 -*-
"""PORTALUL CLIENTULUI — lotul 17.5-L (AC145–AC149, AC151, AC155, AC157, AC159, AC161, AC162, AC164, AC166, AC167, AC169–AC173, AC175–AC178; comanda_17_5_L.txt, «Aserțiunile oracolului» și «Numai e2e_portal_17_5_L.py»).
Scris pentru arhitect; Code nu îl modifică (dacă pică pe C, repară aplicația, nu testul). Un singur test, la 1366×768, ceas înghețat (core/ceas_proba.py: MOMENT_REF 03.11.2026 10:00; luna curentă 11/2026,
luna anterioară 10/2026) în contextul care deschide și tabul de previzualizare.

Două grupe de date:
  G1 = firma F1 Comert Stoc (tenant 105779, schema tenant_9049, snapshot), numai citire: cabinetul (dovada.71507@sesiuneab.test) › Firme › F1 › Acces client › «Previzualizează portalul» (tab NOU, `context.expect_page`);
  G2 = o firmă NOUĂ de test (`firma_noua`), cu cont de client real (`_client` din e2e_lot13_portal_p1.py), date seed prin `sql` pe anul 2099, șterse la final (`_scoate_contul`).

Cele 18 id-uri ale comenzii: cele 6 ale oracolului (f.1, a.3, a.4, f.2, a.5, a.6: aceleași texte, citite din textContent al tabului de previzualizare, ca dom:body|text) și e.1–e.12. Fiecare măsură tipărește (pe consolă, vizibil și fără -s, și în E2E_CAPTURI/masuri_17_5_L.txt) un rând `MASURA <id> <valoare observată> <valoare așteptată> <trece|pica>` (spațiile din valori sunt «_»); pentru e.1 în plus
`MASURA zona_cifre 1366x768 zona=<px> corp=<px> derulante=<număr> loc=<px>`. Textele noi (AC155, AC157, AC159, AC172, AC173, AC175, AC176, AC177, AC178) se tipăresc ca `TEXT <AC> <observat> <așteptat> <trece|pica>`. Testul pică la final cu lista tuturor rândurilor «pica»
(fiecare cu ID-ul și martorul ei); o secțiune care nu poate rula e înregistrată ca «pica» cu motivul, nu opresce celelalte secțiuni.
Nu salvează nimic în G1 (previzualizarea refuză orice mutație, main.py:720–733); în G2 scrie numai ce numesc AC172/AC173/AC176 (mesaje, o declarație depusă), curățate la final.
Rezultatele pe bază se măsoară pe commitul post-K2."""
import importlib.util
import os
import re
import sys
from decimal import Decimal

import pytest

from conftest import BAZA, CAPTURI, firma_noua, sesiune, sql
from e2e_bloc_a import pregateste_firma
from e2e_lot12_start import _scoate_contul
from e2e_lot13_portal_p1 import _client

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
F1 = "F1 Comert Stoc"
TOP = ".fereastra-overlay:not(.fundal) "
FER = TOP + ".fereastra"
# 1×1 PNG valid (octeții contează numai pentru FileReader/FormData: răspunsul /portal/bon e simulat)
PNG = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6300010000000500010d0a2db40000000049454e44ae426082")

# portal.js::incarcaForecast etichetează fiecare săptămână cu data de început.
# Cadrul poate muta alte rânduri în aceeași zonă de derulare.
ETICHETA_SAPTAMANA = r"^din\s+\d{1,2}\.\d{1,2}(?=\s|·|$)"
JS_DERULARI = r"""() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return {fereastra: false};
  const corp = F.querySelector('.fereastra-corp'); if (!corp) return {fereastra: false};
  const vazut = (e) => e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden' && e.getBoundingClientRect().width > 0 && e.getBoundingClientRect().height > 0;
  const nume = (e) => e.tagName.toLowerCase() + '.' + (String(e.className).trim().split(/\s+/)[0] || '');
  const deruleaza = (e) => vazut(e) && /(auto|scroll)/.test(getComputedStyle(e).overflowY) && e.scrollHeight > e.clientHeight + 2;
  const derulante = [corp, ...corp.querySelectorAll('*')].filter(deruleaza);
  const zona = corp.querySelector('#cf-zona');
  const esteSaptamana = (r) => /__ETICHETA_SAPTAMANA__/i.test((r.querySelector('.pf-frand-nume')?.textContent || '').trim());
  const randuri = zona ? [...zona.querySelectorAll('.pf-frand')].filter(esteSaptamana) : [];
  const scroller = randuri[0] && derulante.find((e) => e.contains(randuri[0]));
  const dreptunghiVizibil = (r) => {
    const rect = r.getBoundingClientRect();
    let sus = Math.max(0, rect.top), jos = Math.min(innerHeight, rect.bottom);
    let stanga = Math.max(0, rect.left), dreapta = Math.min(innerWidth, rect.right);
    for (let e = r.parentElement; e && e !== document.body; e = e.parentElement) {
      const stil = getComputedStyle(e);
      const limita = e.getBoundingClientRect();
      if (/(auto|scroll|hidden|clip)/.test(stil.overflowY)) {
        sus = Math.max(sus, limita.top + e.clientTop);
        jos = Math.min(jos, limita.top + e.clientTop + e.clientHeight);
      }
      if (/(auto|scroll|hidden|clip)/.test(stil.overflowX)) {
        stanga = Math.max(stanga, limita.left + e.clientLeft);
        dreapta = Math.min(dreapta, limita.left + e.clientLeft + e.clientWidth);
      }
    }
    return vazut(r) && jos > sus && dreapta > stanga
      ? {x: (stanga + dreapta) / 2, y: (sus + jos) / 2}
      : null;
  };
  return {corp: corp.clientHeight, derulante: derulante.map(nume),
          wrapper: !!scroller && scroller !== corp,
          inaltime: scroller ? scroller.clientHeight : 0,
          scrollTop: scroller ? scroller.scrollTop : 0,
          punct: scroller ? dreptunghiVizibil(scroller) : null,
          total: randuri.length, vizibile: randuri.flatMap((r, i) => dreptunghiVizibil(r) ? [i + 1] : [])};
}""".replace("__ETICHETA_SAPTAMANA__", ETICHETA_SAPTAMANA)
# descendent, nu copil direct: listeDSAplica (ds_piese.js:599-690) mută .pf-frand în celulele unui table.ds-tabel din listă
JS_CIFRE = r"""() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return null;
  const t = (e) => (e ? (e.textContent || '').replace(/\s+/g, ' ').trim() : '');
  const rand = (e) => ({nume: t(e.querySelector('.pf-frand-nume')), suma: t(e.querySelector('.pf-frand-suma')), sub: [...e.querySelectorAll('.pf-frand-sub')].map(t)});
  const randuri = [...F.querySelectorAll('.pf-lista .pf-frand')].map(rand);
  const esteSaptamana = (r) => /__ETICHETA_SAPTAMANA__/i.test(r.nume);
  return {sus: randuri.filter((r) => !esteSaptamana(r)), zona: randuri.filter(esteSaptamana),
          intro: t(F.querySelector('#cf-intro')), de_platit: t(F.querySelector('#cf-de-platit'))};
}""".replace("__ETICHETA_SAPTAMANA__", ETICHETA_SAPTAMANA)
JS_BODY = r"""() => (document.body.textContent || '').trim().replace(/\s+/g, ' ')"""   # ca măsura dom:body|text a oracolului (textContent, nu text vizibil)
JS_ETICHETA_LUNA = r"""() => { const e = document.querySelector('.fereastra-overlay:not(.fundal) .pf-intro'); return e ? e.textContent.replace(/\s+/g, ' ').trim() : ''; }"""
JS_NEXT_ACTIV = r"""() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #fac-next'); return b ? !(b.disabled || b.getAttribute('aria-disabled') === 'true') : null; }"""
JS_TEXT_FEREASTRA = r"""() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); return f ? (f.textContent || '').replace(/\s+/g, ' ').trim() : ''; }"""
JS_STARI_BON = r"""() => {
  const q = (s) => document.querySelector(s);
  const st = (e) => e ? {disabled: !!e.disabled, aria: e.getAttribute('aria-disabled'), motiv: e.getAttribute('data-motiv-inactiv') || e.title || ''} : null;
  const f = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra');
  return {foto: st(q('#bon-fotografiaza')), galerie: st(q('#bon-incarca')), input_foto: st(q('#bon-fisier')), input_galerie: st(q('#bon-fisier-galerie')),
          fereastra: f ? (f.textContent || '').replace(/\s+/g, ' ').trim() : ''};
}"""
JS_BUTOANE_BON = r"""() => {
  const q = (s) => document.querySelector(s);
  const b = q('#bon-butoane');
  const info = (e) => e ? {in: !!(b && b.contains(e)), jos: !!e.closest('.fereastra-jos'), clase: String(e.className), top: Math.round(e.getBoundingClientRect().top), text: (e.textContent || '').trim()} : null;
  return {foto: info(q('#bon-fotografiaza')), galerie: info(q('#bon-incarca')), ordine: b ? [...b.querySelectorAll('button')].map((x) => x.id) : []};
}"""
JS_FISIER_NOU = r"""([sel, nume]) => {
  const i = document.querySelector(sel); if (!i) return false;
  const dt = new DataTransfer(); dt.items.add(new File([new Uint8Array([137, 80, 78, 71])], nume, {type: 'image/png'}));
  i.files = dt.files; i.dispatchEvent(new Event('change', {bubbles: true})); return true;
}"""
JS_POST_SOLICITARE = r"""async ([mesaj, pv]) => {
  const t = sessionStorage.getItem(pv ? 'iconta_pv_token' : 'iconta_token');
  const r = await fetch('/portal/solicitari', {method: 'POST', headers: {Authorization: 'Bearer ' + t, 'Content-Type': 'application/json'}, body: JSON.stringify({mesaj})});
  let j = null; try { j = await r.json(); } catch (e) {}
  return {status: r.status, detail: j && j.detail};
}"""
JS_DESCHIDE_CARD = """(sel) => {
  const c = document.querySelector('.fereastra-overlay:not(.fundal) ' + sel); if (!c) return 'lipsa';
  const cont = c.closest('.firme-optiuni');
  if (cont && cont.hasAttribute('hidden')) { const b = document.querySelector('.firme-grup-btn[aria-controls="' + cont.id + '"]'); if (b) b.click(); }
  return 'ok';
}"""

RE_2Z = re.compile(r"^-?\d{1,3}(?:\.\d{3})*,\d{2}$")
RE_SUMA_VALUTA = re.compile(r"(?<![\w.,])(-?\d[\d.]*(?:,\d+)?) (lei|[A-Z]{3})\b")
MINUS = "[−–-]"


# ── rezultate ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _t(x, lung=170):
    return re.sub(r"\s+", "_", str(x).strip())[:lung] or "-"


class Rez:
    """Rândurile MASURA / TEXT, tipărite pe loc (capsys.disabled: vizibile și fără -s) și în E2E_CAPTURI/masuri_17_5_L.txt; lista celor «pica» pică testul la final."""

    def __init__(self, capsys):
        self.capsys, self.picate, self.toate = capsys, [], []
        self.id_uri_masurate = set()
        os.makedirs(CAPTURI, exist_ok=True)
        self.fisier = os.path.join(CAPTURI, "masuri_17_5_L.txt")
        open(self.fisier, "w", encoding="utf-8").close()

    def _scrie(self, linie):
        with self.capsys.disabled():
            print(linie, flush=True)
        with open(self.fisier, "a", encoding="utf-8") as f:
            f.write(linie + "\n")

    def linie(self, text):
        self._scrie(text)

    def masura(self, id_, observat, asteptat, ok, martor):
        self._emite("MASURA", id_, observat, asteptat, ok, martor)

    def text(self, ac, observat, asteptat, ok, martor=""):
        self._emite("TEXT", ac, observat, asteptat, ok, martor)

    def _emite(self, fel, id_, observat, asteptat, ok, martor):
        self._scrie("%s %s %s %s %s" % (fel, id_, _t(observat), _t(asteptat), "trece" if ok else "pica"))
        if fel == "MASURA":
            if id_ in self.id_uri_masurate:
                self.picate.append("ID măsurat de mai multe ori: " + id_)
                return
            self.id_uri_masurate.add(id_)
            self._scrie("VERDICT %s %s" % (id_, "trece" if ok else "pica"))
        self.toate.append((fel, id_, ok))
        if not ok:
            self.picate.append("%s %s (martor: %s): observat «%s», așteptat «%s»" % (fel, id_, martor or "-", str(observat)[:300], str(asteptat)[:300]))

    def sectiune(self, nume, f, *a):
        try:
            f(self, *a)
        except Exception as e:   # noqa: BLE001 — secțiunea n-a putut rula: se înregistrează, celelalte continuă
            self._scrie("SECTIUNE %s neexecutata: %s: %s" % (nume, type(e).__name__, _t(str(e)[:200])))
            self.toate.append(("SECTIUNE", nume, False))
            self.picate.append("SECȚIUNEA %s n-a putut rula: %s: %s" % (nume, type(e).__name__, str(e)[:300]))


def _incarca_parcurs_17_1():
    spec = importlib.util.spec_from_file_location("parcurs_17_1", os.path.join(RAD, "docs", "dovezi", "17_1", "parcurs_17_1.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def dec(s):
    return Decimal(str(s).replace("−", "-").replace("–", "-").strip().replace(".", "").replace(",", "."))


def _card_cabinet(pg, parcurs, firma, sel, asteapta=None):
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
    pg.wait_for_timeout(2000)
    return True


def acasa_pagina(p, asteapta=".cab-grila button.cab-card"):
    """Pagina principală a portalului (goto, memoria ferestrei deschise ștearsă); starea previzualizării (sessionStorage per tab) rămâne."""
    p.evaluate("() => sessionStorage.removeItem('iconta_fereastra_deschisa')")
    p.goto(BAZA + "/", wait_until="domcontentloaded")
    p.wait_for_selector(asteapta, timeout=30000)
    try:
        p.wait_for_function("() => { const s = document.querySelector('#pa-status'); return !!s && !s.textContent.includes('Se verifică'); }", timeout=20000)
    except Exception:   # noqa: BLE001
        pass
    p.wait_for_timeout(600)


def deschide_card(p, titluri):
    """Clic pe primul card al ecranului de start al cărui titlu e unul din `titluri` (pe bază și după schimbarea numelui). -> titlul găsit."""
    for t in titluri:
        loc = p.locator(".cab-card-titlu", has_text=re.compile("^%s$" % re.escape(t)))
        if loc.count():
            loc.first.click(timeout=10000)
            return t
    raise AssertionError("niciun card cu titlul %s pe ecranul de start" % (titluri,))


def previzualizare(pg, parcurs):
    """Cabinet › F1 › Acces client › #ac-btn-preview: tabul NOU al portalului (context.expect_page). -> pagina tabului."""
    if not _card_cabinet(pg, parcurs, F1, "#fa-acces", "#ac-btn-preview"):
        raise AssertionError("cardul «Acces client» al firmei F1 lipsește")
    pg.wait_for_function("() => { const b = document.querySelector('.fereastra-overlay:not(.fundal) #ac-btn-preview'); const l = document.querySelector('.fereastra-overlay:not(.fundal) #ac-lista');"
                         " return !!b && !b.disabled && !!l && !l.textContent.includes('Se încarcă'); }", timeout=20000)
    with pg.context.expect_page(timeout=30000) as fila:
        pg.click(TOP + "#ac-btn-preview", timeout=10000)
    tab = fila.value
    tab.wait_for_load_state("domcontentloaded", timeout=30000)
    tab.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    tab.wait_for_timeout(1500)
    return tab


# ── G1: F1, previzualizarea portalului ────────────────────────────────────────────────────────────────────────────────────────────
def luna_eticheta(tab):
    m = re.search(r"Luna (\d{2}/\d{4})", tab.evaluate(JS_ETICHETA_LUNA))
    return m.group(1) if m else None


def la_luna(tab, tinta, max_pasi=5):
    """Din antetul lunii din Istoric facturi la luna `tinta` (LL/AAAA) prin #fac-prev / #fac-next. -> eticheta ajunsă."""
    def cheie(e):
        return (int(e[3:]), int(e[:2]))
    cur = luna_eticheta(tab)
    for _ in range(max_pasi):
        if cur is None or cur == tinta:
            break
        tab.click(TOP + ("#fac-prev" if cheie(cur) > cheie(tinta) else "#fac-next"), timeout=10000)
        tab.wait_for_timeout(1800)
        cur = luna_eticheta(tab)
    return cur


def istoric_nou(tab):
    """Deschidere NOUĂ a lui Istoric facturi din meniu (ecranul de start proaspăt, «Facturi» › «Istoric facturi»)."""
    acasa_pagina(tab)
    deschide_card(tab, ["Facturi"])
    tab.wait_for_selector(TOP + "#fac-istoric", timeout=20000)
    tab.click(TOP + "#fac-istoric", timeout=10000)
    tab.wait_for_selector(TOP + "#fac-prev", state="attached", timeout=30000)
    tab.wait_for_timeout(2500)


def g1_cifre(R, tab):
    acasa_pagina(tab)
    deschide_card(tab, ["Cifrele firmei"])
    saptamani = tab.locator(TOP + "#cf-zona .pf-frand").filter(
        has=tab.locator(".pf-frand-nume", has_text=re.compile(ETICHETA_SAPTAMANA, re.I))
    )
    saptamani.first.wait_for(timeout=30000)
    tab.wait_for_timeout(2000)
    # e.1 (AC167): geometrie pe post-K2 și atingerea rândurilor prin scroll de browser.
    criteriu = "derulante<=1,raport>=40%_daca_zona_deruleaza,saptamani=1..8"
    try:
        masura = tab.evaluate(JS_DERULARI)
        assert masura["corp"] > 0 and masura["total"] == 8, masura
        assert len(masura["derulante"]) <= 1, masura
        assert not masura["wrapper"] or masura["inaltime"] >= 0.4 * masura["corp"], masura
        vizibile = set(masura["vizibile"])
        inceput = masura["scrollTop"]
        if vizibile != set(range(1, 9)):
            assert masura["derulante"], masura
            # Derulează containerul chiar dacă nicio săptămână nu este vizibilă inițial.
            punct = masura["punct"]
            assert punct, masura
            tab.mouse.move(punct["x"], punct["y"])
            for _ in range(24):
                if vizibile == set(range(1, 9)):
                    break
                vechi = masura["scrollTop"]
                tab.mouse.wheel(0, max(1, masura["inaltime"] // 2))
                try:
                    tab.wait_for_function(
                        "() => (" + JS_DERULARI + ")().scrollTop !== " + str(vechi),
                        timeout=750,
                    )
                except Exception:
                    break
                masura = tab.evaluate(JS_DERULARI)
                vizibile.update(masura["vizibile"])
        observat = "corp=%s,zona=%s,derulante=%s,scroll=%s->%s,saptamani=%s" % (
            masura["corp"], masura["inaltime"], len(masura["derulante"]),
            inceput, masura["scrollTop"], sorted(vizibile),
        )
        R.masura("e.1", observat, criteriu, vizibile == set(range(1, 9)), "AC167, F1")
    except Exception as e:
        R.masura("e.1", "neexecutat:%s" % str(e)[:180], criteriu, False, "AC167, F1")
    c = tab.evaluate(JS_CIFRE)
    # e.9 (AC169): linia «Neînregistrate încă de contabil și neincluse în sumă», cel puțin 3 facturi (67, 68, 70)
    try:
        m = re.search(r"Neînregistrate încă de contabil și neincluse în sumă: (\d+) (?:de )?factur", c["de_platit"])
        n = int(m.group(1)) if m else 0
        R.masura("e.9", "linia=%s,facturi=%d" % ("da" if m else "lipseste", n), "linia_prezenta,facturi>=3", bool(m) and n >= 3, "AC169, F1: facturile primite 67, 68, 70 cu notele în ciornă")
    except Exception as e:   # noqa: BLE001
        R.masura("e.9", "neexecutat:%s" % str(e)[:80], "linia_prezenta,facturi>=3", False, "AC169")
    # e.10 (AC170, AC171): fiecare sumă cu exact 2 zecimale; soldul fiecărei săptămâni = soldul precedent + încasările − plățile rândului, la cent
    try:
        rele = []
        sume = [r["suma"] for r in c["sus"] + c["zona"]]
        for s in sume:
            v = re.sub(r"\s*lei$", "", s)
            if not RE_2Z.match(v.replace("−", "-")):
                rele.append("suma:" + s)
        for r in c["sus"] + c["zona"]:
            for tinta in [r["nume"]] + r["sub"]:
                for v, _m in RE_SUMA_VALUTA.findall(tinta):
                    if not RE_2Z.match(v.replace("−", "-")):
                        rele.append("in_text:" + v)
        for v in re.findall(r"~\s*(\S+) lei", c["intro"]):
            if not RE_2Z.match(v):
                rele.append("intro:" + v)
        for r in c["zona"]:
            for parte in [p for p in re.split(r" · ", " · ".join(r["sub"])) if ":" in p]:
                for comp in parte.split(":", 1)[1].split(", "):
                    cuv = comp.strip().rsplit(" ", 1)
                    if len(cuv) == 2 and re.match(r"^-?[\d.]+(?:,\d+)?$", cuv[1]) and not RE_2Z.match(cuv[1]):
                        rele.append("componenta:" + cuv[1])
        cash = next((dec(re.sub(r"\s*lei$", "", r["suma"])) for r in c["sus"] if r["nume"].startswith("Bani disponibili")), None)
        ident = []
        if cash is None or not c["zona"]:
            ident.append("lipsesc_Bani_disponibili_sau_randurile_previziunii")
        else:
            prec = cash
            for i, r in enumerate(c["zona"], 1):
                mi, mp = re.search(r"\+\s*(\d[\d.]*(?:,\d+)?) lei", r["nume"]), re.search(MINUS + r"\s*(\d[\d.]*(?:,\d+)?) lei", r["nume"])
                inc, pla = dec(mi.group(1)) if mi else Decimal(0), dec(mp.group(1)) if mp else Decimal(0)
                sold = dec(re.sub(r"\s*lei$", "", r["suma"]))
                if sold != prec + inc - pla:
                    ident.append("sapt%d:%s!=%s+%s-%s" % (i, sold, prec, inc, pla))
                prec = sold
        R.masura("e.10", "formate_gresite=%d,identitate_sold=%s,randuri_sus=%d,randuri_zona=%d" % (len(rele), "ok" if not ident else "pica(%s)" % ";".join(ident)[:120], len(c["sus"]), len(c["zona"])), "formate_gresite=0,identitate_sold=ok,randuri_sus=6,randuri_zona=8",
                 not rele and not ident, "AC170 + AC171, F1: 10.557 + 324 − 5.866 = 5.015, pe ecran «5.014 lei» pe bază")
    except Exception as e:   # noqa: BLE001
        R.masura("e.10", "neexecutat:%s" % str(e)[:80], "formate_gresite=0,identitate_sold=ok", False, "AC170, AC171")


def asteapta_detaliu_factura(pagina):
    pagina.wait_for_selector(TOP + "#fac-prev", state="detached", timeout=20000)
    # Antetul este prezent atât în detaliul obișnuit, cât și la factura preluată.
    # Este randat după răspunsul GET și lipsește din ecranul de încărcare.
    pagina.locator(TOP + ".fd-antet h2.pf-titlu").wait_for(state="attached", timeout=20000)


def g1_istoric(R, tab, martor=None):
    # e.4 (AC166): deschidere nouă din meniu → luna ultimei facturi (10/2026) și fraza
    istoric_nou(tab)
    eticheta, text = luna_eticheta(tab), tab.evaluate(JS_TEXT_FEREASTRA)
    fraza = "Luna curentă nu are facturi; se arată ultima lună cu facturi." in text
    corp_oracol = tab.evaluate(JS_BODY)
    for id_, val in (("a.5", "Export SAGA lună"), ("a.6", "Export WinMentor lună")):
        R.masura(id_, "lipseste:" + ("da" if val not in corp_oracol else "nu,apare"), "lipseste:da", val not in corp_oracol, "oracol, AC164: pe bază butonul «%s» e în Istoric facturi al previzualizării" % val)
    R.masura("e.4", "luna=%s,fraza=%s" % (eticheta, "da" if fraza else "nu"), "luna=10/2026,fraza=da", eticheta == "10/2026" and fraza, "AC166, F1: ultima factură 10/2026, luna curentă a ceasului fix 11/2026 e goală")
    # e.3 (AC162): #fac-next activ în 10/2026, inactiv în luna curentă (11/2026, ceasul fix)
    try:
        la_luna(tab, "10/2026")
        a10 = tab.evaluate(JS_NEXT_ACTIV)
        tab.click(TOP + "#fac-next", timeout=10000)
        tab.wait_for_timeout(1800)
        e11, a11 = luna_eticheta(tab), tab.evaluate(JS_NEXT_ACTIV)
        R.masura("e.3", "10/2026:activ=%s;%s:activ=%s" % (a10, e11, a11), "10/2026:activ=True;11/2026:activ=False", a10 is True and e11 == "11/2026" and a11 is False, "AC162, F1: 11/2026 = luna curentă a ceasului fix")
    except Exception as e:   # noqa: BLE001
        R.masura("e.3", "neexecutat:%s" % str(e)[:80], "10/2026:activ=True;11/2026:activ=False", False, "AC162")
    # e.2 (AC161): prima factură din 10/2026 deschisă, «←» → aceeași lună ca înainte
    try:
        la_luna(tab, "10/2026")
        inainte = luna_eticheta(tab)
        tab.locator(TOP + ".fac-frand-btn").first.click(timeout=10000)
        tab.wait_for_selector(TOP + "#fac-prev", state="detached", timeout=20000)
        tab.wait_for_timeout(1200)
        tab.click(TOP + ".fereastra-antet .nav-inapoi", timeout=10000)
        tab.wait_for_selector(TOP + "#fac-prev", state="attached", timeout=20000)
        tab.wait_for_timeout(2500)
        dupa = luna_eticheta(tab)
        R.masura("e.2", "inainte=%s,dupa_inapoi=%s" % (inainte, dupa), "10/2026,aceeasi", inainte == "10/2026" and dupa == inainte, "AC161, F1: pe bază «←» revine la 11/2026 (luna curentă)")
    except Exception as e:   # noqa: BLE001
        R.masura("e.2", "neexecutat:%s" % str(e)[:80], "10/2026,aceeasi", False, "AC161")
    # e.5 (AC164), partea de previzualizare: butoanele de export și #fac-saga-zona lipsesc din listă; în detaliul fiecărei facturi vizitate lipsesc #fd-saga și «notă propusă», iar starea n-are «notă» / «de validat» / «contabiliz» (decizia 1: orice stare a notei contabile)
    prev = {}
    try:
        la_luna(tab, "10/2026")
        text = tab.evaluate(JS_TEXT_FEREASTRA)
        prev["saga_luna"] = int(bool(tab.locator(TOP + "#fac-saga-luna").count()) or "Export SAGA lună" in text)
        prev["wm_luna"] = int(bool(tab.locator(TOP + "#fac-winmentor-luna").count()) or "Export WinMentor lună" in text)
        prev["saga_zona"] = tab.locator(TOP + "#fac-saga-zona").count()
        prev["fd_saga"], prev["nota_propusa"], prev["stare_cu_nota"], vizitate = 0, 0, 0, 0
        for luna in ("10/2026", "09/2026"):
            if la_luna(tab, luna) != luna:
                continue
            n = tab.locator(TOP + ".fac-frand-btn").count()
            for i in range(min(n, 10 if luna == "10/2026" else 3)):
                tab.locator(TOP + ".fac-frand-btn").nth(i).click(timeout=10000)
                asteapta_detaliu_factura(tab)
                prev["fd_saga"] += tab.locator(TOP + "#fd-saga").count()
                prev["nota_propusa"] += int("notă propusă" in tab.evaluate(JS_TEXT_FEREASTRA))
                stari = tab.locator(TOP + ".fd-stare").all_inner_texts()
                prev["stare_cu_nota"] += int(any(re.search(r"notă|de validat|contabiliz", s, re.I) for s in stari))
                vizitate += 1
                tab.click(TOP + ".fereastra-antet .nav-inapoi", timeout=10000)
                tab.wait_for_selector(TOP + "#fac-prev", state="attached", timeout=20000)
                tab.wait_for_timeout(1500)
                la_luna(tab, luna)
        prev["vizitate"] = vizitate
        if martor:
            luna, factura = martor
            assert la_luna(tab, luna) == luna
            buton = tab.locator(TOP + f'.fac-frand-btn[data-id="{factura}"]')
            assert buton.count() == 1, f"Factura martor {factura} lipsește în portal"
            buton.click(timeout=10000)
            asteapta_detaliu_factura(tab)
            text_martor = tab.locator(FER).inner_text()
            prev["martor_fara_stare"] = not re.search(r"notă propusă|contabilizată", text_martor, re.I)
    except Exception as e:   # noqa: BLE001
        prev["eroare"] = "%s:%s" % (type(e).__name__, str(e)[:80])
    R.prev_e5 = prev


def g1_bon_preview(R, tab):
    acasa_pagina(tab)
    cereri = []
    tab.on("request", lambda r: cereri.append(r.url) if r.method == "POST" and r.url.split("?")[0].endswith("/portal/bon") else None)
    tab.locator("#pa-bon-slot button.cab-card").first.click(timeout=10000)
    tab.wait_for_selector(TOP + "#bon-butoane", timeout=20000)
    tab.wait_for_timeout(1000)
    s = tab.evaluate(JS_STARI_BON)
    tab.evaluate("() => { for (const sel of ['#bon-fotografiaza', '#bon-incarca']) { const b = document.querySelector(sel); if (b) b.click(); } }")   # clic fără gest: pe un buton inactiv nu face nimic
    tab.wait_for_timeout(1200)
    motiv = "Previzualizare: doar vizualizare."

    def inactiv(e):   # comanda (AC149): inactiv prin aria-disabled="true" (api.js:atributeInactiv), nu prin atributul disabled
        return bool(e) and e["aria"] == "true"
    stari = {k: ("inactiv" if inactiv(s[k]) else "activ") for k in ("foto", "galerie", "input_foto", "input_galerie")}
    motive = all(s[k] and (motiv in (s[k]["motiv"] or "") or motiv in s["fereastra"]) for k in ("foto", "galerie"))
    R.masura("e.11", "foto=%s,galerie=%s,input_foto=%s,input_galerie=%s,motiv=%s,cereri=%d" % (stari["foto"], stari["galerie"], stari["input_foto"], stari["input_galerie"], "da" if motive else "nu", len(cereri)),
             "toate=inactiv,motiv=da,cereri=0", all(v == "inactiv" for v in stari.values()) and motive and not cereri, "AC149, F1, previzualizare: «%s»" % motiv)


def g1(R, ctx, pg, parcurs):
    # e.5, partea de cabinet: «Istoric facturi F1» are butoanele de export (cabinetul păstrează comportamentul de azi)
    cab = {}
    martor = None
    try:
        if not _card_cabinet(pg, parcurs, F1, "#fa-facturi", "#fac-istoric"):
            raise AssertionError("cardul «Facturi» lipsește")
        pg.click(TOP + "#fac-istoric", timeout=10000)
        pg.wait_for_selector(TOP + "#fac-prev", state="attached", timeout=30000)
        pg.wait_for_timeout(1500)
        cab = {"saga_luna": pg.locator(TOP + "#fac-saga-luna").count(), "wm_luna": pg.locator(TOP + "#fac-winmentor-luna").count()}
        for luna in ("10/2026", "09/2026"):
            if la_luna(pg, luna) != luna:
                continue
            facturi = pg.locator(TOP + ".fac-frand-btn")
            for i in range(min(facturi.count(), 10)):
                buton = facturi.nth(i)
                factura = buton.get_attribute("data-id")
                assert factura and factura.isdecimal(), factura
                buton.click(timeout=10000)
                asteapta_detaliu_factura(pg)
                text_martor = pg.locator(FER).inner_text()
                if "notă propusă, de validat" in text_martor:
                    martor = (luna, factura)
                    break
                pg.click(TOP + ".fereastra-antet .nav-inapoi", timeout=10000)
                pg.wait_for_selector(TOP + "#fac-prev", timeout=20000)
                assert la_luna(pg, luna) == luna
            if martor:
                break
        cab["martor"] = martor
    except Exception as e:   # noqa: BLE001
        cab = {"eroare": "%s:%s" % (type(e).__name__, str(e)[:80])}
    tab = previzualizare(pg, parcurs)
    R.prev_e5 = {}
    try:
        # texte pe ecranul de start (AC157, AC155, AC175) și mesajul serverului în previzualizare (AC157)
        acasa_pagina(tab)
        t = tab.evaluate("() => (document.body.textContent || '').replace(/\\s+/g, ' ')")
        corp_oracol = tab.evaluate(JS_BODY)
        for id_, val, descriere_oracol in (("f.1", "Acces cont", "invariantă: cardul «Acces cont», neschimbat de lot"), ("a.3", "Fotografiază bon sau chitanță", "AC155: pe bază cardul se numește «Pozează bon sau chitanță»"),
                                 ("a.4", "Mesaje către contabil", "AC175: pe bază cardul se numește «Solicitări»"), ("f.2", "Declarații depuse", "invariantă: cardul «Declarații depuse», neschimbat de lot")):
            R.masura(id_, "text_contine:" + ("prezent" if val in corp_oracol else "absent"), "text_contine:prezent", val in corp_oracol, "oracol, %s, F1 previzualizare" % descriere_oracol)
        R.text("AC157-caseta", "noua=%s,veche=%s" % ("da" if "Previzualizare: doar vizualizare." in t else "nu", "da" if "Previzualizare — doar vizualizare" in t else "nu"), "noua=da,veche=nu",
               "Previzualizare: doar vizualizare." in t and "Previzualizare — doar vizualizare" not in t, "F1 previzualizare, caseta de pe ecranul de start (portal.js, desktopPortal)")
        r = tab.evaluate(JS_POST_SOLICITARE, ["probă preview", True])
        asteptat = "Previzualizare: doar vizualizare. Acțiunile sunt dezactivate în modul de previzualizare."
        R.text("AC157-server", "%s:%s" % (r["status"], r["detail"]), "403:" + asteptat, r["status"] == 403 and r["detail"] == asteptat, "main.py, _preview_readonly_guard: POST în previzualizare")
        R.sectiune("G1/cifre", g1_cifre, tab)
        R.sectiune("G1/istoric", g1_istoric, tab, martor)
        R.sectiune("G1/bon_preview", g1_bon_preview, tab)
    finally:
        try:
            tab.close()
        except Exception:   # noqa: BLE001
            pass
    p = R.prev_e5
    obs = "previzualizare:saga_luna=%s,wm_luna=%s,saga_zona=%s,fd_saga=%s,notă_propusă=%s,stare_cu_notă=%s,facturi_vizitate=%s;cabinet:saga_luna=%s,wm_luna=%s" % (
        p.get("saga_luna"), p.get("wm_luna"), p.get("saga_zona"), p.get("fd_saga"), p.get("nota_propusa"), p.get("stare_cu_nota"), p.get("vizitate"), cab.get("saga_luna"), cab.get("wm_luna"))
    if p.get("eroare") or cab.get("eroare"):
        obs += ";eroare=%s|%s" % (p.get("eroare"), cab.get("eroare"))
    ok_prev = not p.get("eroare") and p.get("saga_luna") == 0 and p.get("wm_luna") == 0 and p.get("saga_zona") == 0 and p.get("fd_saga") == 0 and p.get("nota_propusa") == 0 and p.get("stare_cu_nota") == 0 and (p.get("vizitate") or 0) >= 1
    ok_cab = not cab.get("eroare") and cab.get("saga_luna") == 1 and cab.get("wm_luna") == 1
    obs += ";martor=%s;martor_fara_stare=%s" % (martor, p.get("martor_fara_stare"))
    ok_cab = ok_cab and bool(martor) and p.get("martor_fara_stare") is True
    R.masura("e.5", obs, "acelasi_martor:stare_doar_in_cabinet;previzualizare:toate=0,facturi_vizitate>=1;cabinet:saga_luna=1,wm_luna=1", ok_prev and ok_cab, "AC164, F1: pe bază butoanele sunt în previzualizare, iar 67, 68, 70 spun «notă propusă, de validat»")


# ── G2: firmă nouă, cont de client real ───────────────────────────────────────────────────────────────────────────────────────────
def bon_nou(cp):
    acasa_pagina(cp)
    cp.locator("#pa-bon-slot button.cab-card").first.click(timeout=10000)
    cp.wait_for_selector(TOP + "#bon-butoane", timeout=20000)
    cp.wait_for_timeout(600)


def _poarta_bon(url):
    return url.split("?")[0].endswith("/portal/bon")


def _poarta_confirma(url):
    return re.search(r"/portal/bon/\d+/confirma$", url.split("?")[0]) is not None


def _poarta_povesti(url):
    return url.split("?")[0].endswith("/portal/povesti")


def g2_bon(R, cp):
    # AC155 / AC146: cardul de pe ecranul de start, titlul ferestrei și intro-ul
    acasa_pagina(cp)
    card = cp.locator("#pa-bon-slot button.cab-card").first
    titlu_card = " ".join(card.locator(".cab-card-titlu").inner_text().split())
    R.text("AC155-card", titlu_card, "Fotografiază bon sau chitanță", titlu_card == "Fotografiază bon sau chitanță", "G2, ecranul de start al clientului")
    card.click(timeout=10000)
    cp.wait_for_selector(TOP + "#bon-butoane", timeout=20000)
    cp.wait_for_timeout(600)
    h2 = " ".join(cp.locator(FER + " .pf-titlu").first.inner_text().split())
    R.text("AC155-fereastra", h2, "Fotografiază bon sau chitanță", h2 == "Fotografiază bon sau chitanță", "G2, h2 al ferestrei")
    intro = " ".join(cp.locator(FER + " .pf-intro").first.inner_text().split())
    R.text("AC146-intro", intro, "contine:Poți trimite până la 4 fotografii pentru același document.", "Poți trimite până la 4 fotografii pentru același document." in intro, "G2, intro-ul ferestrei")
    # e.12 (AC151): cele două butoane ale pasului 1, în #bon-butoane, ambele secundare, același loc, în bara de jos niciunul
    b = cp.evaluate(JS_BUTOANE_BON)
    f, g = b["foto"], b["galerie"]
    ok12 = bool(f and g and f["in"] and g["in"] and not f["jos"] and not g["jos"] and "buton-secundar" in f["clase"] and "buton-secundar" in g["clase"]
                and "buton-primar" not in f["clase"] and "buton-primar" not in g["clase"] and abs(f["top"] - g["top"]) <= 2 and b["ordine"] == ["bon-fotografiaza", "bon-incarca"])
    R.masura("e.12", "foto=%s;galerie=%s;ordine=%s" % (f and (("in" if f["in"] else "afara") + ",jos=%s,top=%s" % (f["jos"], f["top"])), g and (("in" if g["in"] else "afara") + ",jos=%s,top=%s" % (g["jos"], g["top"])), ",".join(b["ordine"])),
             "ambele_in_#bon-butoane,secundare,top±2,niciunul_jos", ok12, "AC151, G2: pe bază «Fotografiază documentul» e în bara de jos, primar")

    # e.7 (AC146): 5 fișiere → 0 cereri și mesajul
    cereri = []

    def tine(route):
        cereri.append(route.request.url)
        route.fulfill(status=400, content_type="application/json", body='{"detail": "probă"}')
    cp.route(_poarta_bon, tine)
    try:
        bon_nou(cp)
        cp.set_input_files("#bon-fisier-galerie", [{"name": "b%d.png" % i, "mimeType": "image/png", "buffer": PNG} for i in range(5)])
        cp.wait_for_timeout(2000)
        rez = cp.evaluate("() => { const e = document.querySelector('#bon-rezultat'); return e ? {text: e.textContent.replace(/\\s+/g, ' ').trim(), eroare: e.matches('.msg-eroare') || !!e.querySelector('.msg-eroare')} : null; }")
        mesaj = "Poți trimite cel mult 4 fotografii odată. Alege din nou."
        respinse = len(cereri)
        recuperat = False
        if respinse == 0 and rez and rez["text"] == mesaj and rez["eroare"]:
            with cp.expect_response(
                lambda raspuns: _poarta_bon(raspuns.url) and raspuns.request.method == "POST",
                timeout=10000,
            ):
                cp.set_input_files("#bon-fisier-galerie",
                                   {"name": "b-valid.png", "mimeType": "image/png", "buffer": PNG})
            recuperat = len(cereri) == 1
        R.masura("e.7", "respinse=%d;dupa_selectie_valida=%d;mesaj=%s" %
                 (respinse, len(cereri), rez and rez["text"]),
                 "respinse=0;dupa_selectie_valida=1;mesaj=" + mesaj,
                 recuperat, "AC146, G2, același formular, răspuns interceptat")
    finally:
        cp.unroute(_poarta_bon)

    # e.6 (AC145): două selecții la rând, înainte de răspuns → 1 cerere, input-urile și butoanele disabled cât durează
    tinute = []
    cp.route(_poarta_bon, lambda route: tinute.append(route))
    try:
        bon_nou(cp)
        cp.set_input_files("#bon-fisier-galerie", {"name": "b1.png", "mimeType": "image/png", "buffer": PNG})
        cp.wait_for_function("() => (document.querySelector('#bon-rezultat') || {textContent: ''}).textContent.includes('Se citește')", timeout=10000)
        cp.evaluate(JS_FISIER_NOU, ["#bon-fisier", "b2.png"])   # al doilea gest, pe celălalt input, înainte de răspuns
        cp.wait_for_timeout(1500)
        s = cp.evaluate(JS_STARI_BON)
        dezactivate = all(s[k] and s[k]["disabled"] for k in ("foto", "galerie", "input_foto", "input_galerie"))
        R.masura("e.6", "cereri=%d;dezactivate=%s" % (len(tinute), {k: bool(s[k] and s[k]["disabled"]) for k in ("foto", "galerie", "input_foto", "input_galerie")}), "cereri=1;toate_disabled=True", len(tinute) == 1 and dezactivate,
                 "AC145, G2: pe bază a doua selecție trimite a doua cerere, input-urile rămân active")
    finally:
        for r in tinute:
            try:
                r.fulfill(status=400, content_type="application/json", body='{"detail": "probă"}')
            except Exception:   # noqa: BLE001
                pass
        cp.unroute(_poarta_bon)

    # e.8 (AC147) + AC159: răspuns simulat cu etichete HTML în textele citite de AI → apar ca text, nu se execută; apoi «Se trimite…»
    import json
    bon = {"bon_id": 987654, "bon": {"tip": "bon", "comerciant": "<img src=x onerror=window.__xss=1>", "numar_document": "12", "data": "2026-10-01", "cui": "RO123", "total": 10.5,
                                      "tva": [{"cota": 21, "valoare": 1.82}], "mentiuni": "<img src=y onerror=window.__xss2=1>"},
           "avertismente": ["<img src=z onerror=window.__xss3=1>"]}
    confirma = []
    cp.route(_poarta_bon, lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(bon)))
    cp.route(_poarta_confirma, lambda route: confirma.append(route))
    try:
        bon_nou(cp)
        cp.set_input_files("#bon-fisier-galerie", {"name": "b1.png", "mimeType": "image/png", "buffer": PNG})
        cp.wait_for_selector(TOP + "#bon-trimite", timeout=20000)
        cp.wait_for_timeout(1500)
        text = cp.evaluate(JS_TEXT_FEREASTRA)
        xss = cp.evaluate("() => [typeof window.__xss, typeof window.__xss2, typeof window.__xss3].join(',')")
        R.masura("e.8", "xss=%s;text_literal=%s" % (xss, "da" if "<img src=x onerror=window.__xss=1>" in text else "nu"), "xss=undefined,undefined,undefined;text_literal=da",
                 xss == "undefined,undefined,undefined" and "<img src=x onerror=window.__xss=1>" in text, "AC147, G2: pe bază comerciantul, mențiunile și avertismentul sunt inserate ca HTML")
        cp.click(TOP + "#bon-trimite", timeout=10000)
        cp.wait_for_timeout(1200)
        txt_btn = cp.evaluate("() => (document.querySelector('#bon-trimite') || {textContent: ''}).textContent.trim()")
        R.text("AC159-trimite", txt_btn, "Se trimite…", txt_btn == "Se trimite…", "G2, pasul 2, butonul «Trimite la contabil» cât durează cererea")
    finally:
        for r in confirma:
            try:
                r.fulfill(status=200, content_type="application/json", body='{"ok": true}')
            except Exception:   # noqa: BLE001
                pass
        cp.unroute(_poarta_bon)
        cp.unroute(_poarta_confirma)


def g2_declaratii_documente(R, cp, f):
    # AC176: rândul declarației depuse spune o singură dată «depusă»
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa, recipisa) VALUES (%s, 2099, 1, 'd406', '2099-03-02 10:00+02', 'extern', 'E2E-L176')", (f["tenant_id"],))
    acasa_pagina(cp)
    deschide_card(cp, ["Declarații depuse"])
    cp.wait_for_selector(FER + " .pf-frand", timeout=30000)
    rand = cp.locator(FER + " .pf-frand", has_text="D406").first
    text = " ".join(rand.inner_text().split())
    ok_el = cp.locator(FER + " .pf-frand-ok").first
    eticheta = " ".join(ok_el.inner_text().split())
    aria, title = ok_el.get_attribute("aria-label"), ok_el.get_attribute("title")
    R.text("AC176", "rand=%s;eticheta=%s;aria=%s;title=%s" % (text, eticheta, aria, title), "contine:depusă_pe_02.03.2099;eticheta=✓;aria-label=depusă;title=Depusă;fara:✓_depusă",
           "depusă pe 02.03.2099" in text and "✓ depusă" not in text and eticheta == "✓" and aria == "depusă" and title == "Depusă", "G2, D406 01/2099, recipisa E2E-L176")
    # AC177: fereastra «Documente» se numește «Documente»
    acasa_pagina(cp)
    deschide_card(cp, ["Documente"])
    cp.wait_for_selector(FER + " .pf-titlu", timeout=30000)
    cp.wait_for_timeout(1000)
    h2 = " ".join(cp.locator(FER + " .pf-titlu").first.inner_text().split())
    intro = " ".join(cp.locator(FER + " .pf-intro").first.inner_text().split())
    asteptat = "Balanțele lunare, generate din contabilitate. O lună provizorie se poate schimba până o închide contabilul."
    R.text("AC177", "h2=%s;intro=%s" % (h2, intro), "h2=Documente;intro=" + asteptat, h2 == "Documente" and intro == asteptat, "G2, cardul «Documente» și fereastra lui (pe bază fereastra se numește «Balanțe lunare»)")


def g2_mesaje(R, cp, f):
    # AC175: cardul, titlul, intro-ul, butonul, placeholder-ul, starea goală (firma nouă n-are mesaje)
    acasa_pagina(cp)
    carduri = cp.locator("button.cab-card").filter(has=cp.locator(".cab-card-titlu", has_text=re.compile("^(Mesaje către contabil|Solicitări)$")))
    titlu_card = " ".join(carduri.first.locator(".cab-card-titlu").inner_text().split())
    sinteza = " ".join(carduri.first.locator(".cab-card-sinteza").inner_text().split())
    R.text("AC175-card", "titlu=%s;sinteza=%s" % (titlu_card, sinteza), "titlu=Mesaje către contabil;sinteza=Scrie un mesaj contabilului.", titlu_card == "Mesaje către contabil" and sinteza == "Scrie un mesaj contabilului.", "G2, ecranul de start")
    carduri.first.click(timeout=10000)
    cp.wait_for_selector(FER + " #sol-input", timeout=30000)
    cp.wait_for_timeout(800)
    h2 = " ".join(cp.locator(FER + " .pf-titlu").first.inner_text().split())
    intro = " ".join(cp.locator(FER + " .pf-intro").first.inner_text().split())
    btn = " ".join(cp.locator(FER + " #sol-trimite-btn").inner_text().split())
    ph = cp.locator(FER + " #sol-input").get_attribute("placeholder")
    gol = " ".join(cp.locator(FER + " #sol-fir").inner_text().split())
    obs = "h2=%s;intro=%s;buton=%s;placeholder=%s;gol=%s" % (h2, intro, btn, ph, gol)
    R.text("AC175-fereastra", obs, "h2=Mesaje către contabil;intro=Scrie contabilului tău ce ai nevoie.;buton=Trimite mesajul;placeholder=Scrie un mesaj…;gol=Niciun mesaj încă.",
           h2 == "Mesaje către contabil" and intro == "Scrie contabilului tău ce ai nevoie." and btn == "Trimite mesajul" and ph == "Scrie un mesaj…" and gol == "Niciun mesaj încă.", "G2, fereastra de mesaje")
    # AC172: serverul refuză gol / spații / peste 4.000 de caractere; scrie mesajul tăiat
    gol_txt, lung_txt = "Scrie solicitarea înainte de a o trimite.", "Mesajul are peste 4.000 de caractere. Scurtează-l."
    for nume, mesaj, asteptat in (("gol", "", gol_txt), ("spatii", "   ", gol_txt), ("4001", "a" * 4001, lung_txt)):
        r = cp.evaluate(JS_POST_SOLICITARE, [mesaj, False])
        R.text("AC172-" + nume, "%s:%s" % (r["status"], r["detail"]), "400/422:" + asteptat, r["status"] in (400, 422) and r["detail"] == asteptat, "G2, POST /portal/solicitari cu tokenul clientului")
    r = cp.evaluate(JS_POST_SOLICITARE, ["  Mesaj tăiat L172  ", False])
    scris = sql("SELECT mesaj FROM public.solicitari_client WHERE tenant_id = %s ORDER BY id DESC LIMIT 1", (f["tenant_id"],))
    R.text("AC172-taiat", "status=%s;scris=%r" % (r["status"], scris[0][0] if scris else None), "status=200;scris='Mesaj tăiat L172'", r["status"] == 200 and bool(scris) and scris[0][0] == "Mesaj tăiat L172", "G2, mesajul scris în bază e cel tăiat")
    # AC173 + AC159: din ecran, cu cererea ținută (butonul «Se trimite…»), apoi linia verde și «Tu · <data cu oră> · Trimis»
    tinute = []

    def este_sol(u):
        return u.split("?")[0].endswith("/portal/solicitari")
    cp.route(este_sol, lambda route: tinute.append(route) if route.request.method == "POST" else route.continue_())
    try:
        acasa_pagina(cp)
        deschide_card(cp, ["Mesaje către contabil", "Solicitări"])
        cp.wait_for_selector(FER + " #sol-input", timeout=30000)
        cp.fill(FER + " #sol-input", "Salut L173")
        cp.click(FER + " #sol-trimite-btn", timeout=10000)
        cp.wait_for_timeout(1200)
        txt_btn = cp.evaluate("() => (document.querySelector('#sol-trimite-btn') || {textContent: ''}).textContent.trim()")
        R.text("AC159-mesaje", txt_btn, "Se trimite…", txt_btn == "Se trimite…", "G2, butonul de trimitere cât durează cererea")
        if tinute:
            tinute[0].continue_()
        cp.wait_for_timeout(2500)
        text = cp.evaluate(JS_TEXT_FEREASTRA)
        linie = "Mesajul a fost trimis contabilului." in text
        meta = re.search(r"Tu · \d{2}\.\d{2}\.\d{4} \d{2}:\d{2} · Trimis", text)
        R.text("AC173-trimis", "linia=%s;meta=%s" % ("da" if linie else "nu", meta.group(0) if meta else "lipseste"), "linia=da;meta=Tu_·_zz.ll.aaaa_hh:mm_·_Trimis", linie and bool(meta), "G2, după trimitere")
    finally:
        cp.unroute(este_sol)
    # cabinetul răspunde (rând autor_rol = cabinet, creat_la mai nou) → «Răspuns primit», iar rândul cabinetului «Contabil · <data cu oră>»
    ((uid,),) = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")
    sql("INSERT INTO public.solicitari_client (tenant_id, mesaj, autor_rol, autor_id, creat_la) VALUES (%s, 'Răspuns L173', 'cabinet', %s, now() + interval '1 minute')", (f["tenant_id"], uid))
    acasa_pagina(cp)
    deschide_card(cp, ["Mesaje către contabil", "Solicitări"])
    cp.wait_for_selector(FER + " .sol-rand", timeout=30000)
    cp.wait_for_timeout(800)
    text = cp.evaluate(JS_TEXT_FEREASTRA)
    meta_cl = re.search(r"Tu · \d{2}\.\d{2}\.\d{4} \d{2}:\d{2} · Răspuns primit", text)
    meta_cab = re.search(r"Contabil · \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}(?! ·)", text)
    R.text("AC173-raspuns", "client=%s;cabinet=%s" % (meta_cl.group(0) if meta_cl else "lipseste", meta_cab.group(0) if meta_cab else "lipseste"),
           "client=Tu_·_data_ora_·_Răspuns_primit;cabinet=Contabil_·_data_ora", bool(meta_cl) and bool(meta_cab), "G2, după un rând autor_rol=cabinet mai nou")


def g2_povestea(R, cp):
    # AC178: răspunsul /portal/povesti simulat cu diferența −13713, 500 și 0
    def rand(luna, dif):
        return {"an": 2026, "luna": luna, "text": "Text de probă luna %d." % luna, "retrasa": False, "diferenta": dif}
    corp = {"povesti": [rand(10, -13713), rand(9, 500), rand(8, 0)]}
    import json
    cp.route(_poarta_povesti, lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(corp)))
    try:
        acasa_pagina(cp)
        deschide_card(cp, ["Povestea lunii"])
        cp.wait_for_selector(FER + " #pov-lista .pf-frand", timeout=30000)
        cp.wait_for_timeout(800)
        randuri = [" ".join(x.split()) for x in cp.locator(FER + " #pov-lista .pf-frand").all_inner_texts()]
        asteptate = ["cu 13.713,00 lei mai puțin decât luna anterioară (rezultat înainte de impozit)", "cu 500,00 lei mai mult decât luna anterioară (rezultat înainte de impozit)",
                     "la fel ca luna anterioară (rezultat înainte de impozit)"]
        ok = len(randuri) == 3 and all(a in r for a, r in zip(asteptate, randuri)) and not any(re.search(MINUS + r"\s*13\.713|\+\s*500,00 lei la rezultatul|față de luna anterioară", r) for r in randuri)
        R.text("AC178", " || ".join(r[-110:] for r in randuri), " || ".join(asteptate), ok, "G2, rânduri simulate cu diferența −13713, 500, 0 (pe bază «-13.713,00 lei la rezultatul înainte de impozit, față de luna anterioară»)")
    finally:
        cp.unroute(_poarta_povesti)


def g2_text_astepare(R):
    """AC159: orice text de așteptare din portal.js care începe cu «Se » și se termină cu trei puncte ASCII (citit din fișierul servit de 8019, ca regula din comandă, dar nu numai cu literele din regex-ul ei)."""
    with open(os.path.join(RAD, "static", "js", "ecrane", "portal.js"), encoding="utf-8") as fis:
        sursa = fis.read()
    ramase = re.findall("[\"'>`]Se [^\"'`<>\\n]*\\.\\.\\.", sursa)
    R.text("AC159-sursa", "ramase=%d:%s" % (len(ramase), ";".join(ramase[:4])), "ramase=0", not ramase, "portal.js (pe bază: «Se încarcă...», «Se trimite...», «Se salvează...», «Se verifică situația la ANAF...»)")


def g2(R, ctx, cp, f):
    R.sectiune("G2/bon", g2_bon, cp)
    R.sectiune("G2/declaratii_documente", g2_declaratii_documente, cp, f)
    R.sectiune("G2/mesaje", g2_mesaje, cp, f)
    R.sectiune("G2/povestea", g2_povestea, cp)
    R.sectiune("G2/text_astepare", g2_text_astepare)


@pytest.fixture(scope="module")
def firma_g2():
    for f in firma_noua():
        yield f


def test_portal_17_5_L(browser, patron, firma_g2, capsys):
    from core import ceas_proba
    parcurs = _incarca_parcurs_17_1()
    R = Rez(capsys)
    # G1: cabinetul (dovada.71507) și previzualizarea portalului F1, în același context cu ceas fix
    c1 = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        c1.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        c1.add_init_script(sesiune(ADMIN))
        pg = c1.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        R.sectiune("G1", g1, c1, pg, parcurs)
    finally:
        c1.close()
    # G2: firmă nouă, cont de client real
    f = firma_g2
    email = None
    c2 = None
    try:
        pregateste_firma(patron, f)
        email = _client(patron, f, "l17")
        c2 = browser.new_context(viewport={"width": 1366, "height": 768})
        c2.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        c2.add_init_script(sesiune(email))
        cp = c2.new_page()
        cp.goto(BAZA + "/", wait_until="domcontentloaded")
        cp.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
        R.sectiune("G2", g2, c2, cp, f)
    except Exception as e:   # noqa: BLE001
        R.picate.append("G2 n-a putut porni: %s: %s" % (type(e).__name__, str(e)[:300]))
    finally:
        if c2 is not None:
            c2.close()
        if email:
            _scoate_contul(email)
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND an = 2099", (f["tenant_id"],))
        # notificările create de POST /portal/solicitari (uc_portal.py:274-281: tip «solicitare_client», link «solicitari:<tenant_id>», către conturile cabinetului);
        # cheia e tenant_id-ul firmei noi (creată de test), deci nu atinge notificări preexistente
        sql("DELETE FROM public.notificari WHERE tip = 'solicitare_client' AND link = %s", ("solicitari:%s" % f["tenant_id"],))
        sql("DELETE FROM public.solicitari_client WHERE tenant_id = %s", (f["tenant_id"],))
    R.linie("SUMAR %d rânduri, %d pică" % (len(R.toate), len(R.picate)))
    assert not R.picate, "e2e_portal_17_5_L: %d rânduri pică:\n  " % len(R.picate) + "\n  ".join(R.picate)
