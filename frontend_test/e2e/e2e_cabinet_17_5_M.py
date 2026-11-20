# -*- coding: utf-8 -*-
"""ECRANELE CABINETULUI — lotul 17.5-M (AC014, AC015, AC017, AC022, AC024, AC025, AC027, AC028, AC034, AC035, AC036 din auditul complet; decizii_17_5_M.txt și «De ce» din comanda_17_5_M.txt).
Scris de arhitect; Code nu îl modifică. Un singur test, 18 id-uri (f.1, f.2, a.1–a.16): pentru fiecare tipărește `REZULTAT <id> trece|pica <valoarea observată>`, plus rândurile `INFO …`.

La 1366×768 (a.9 și la 603×590), ceas înghețat în browser 03.11.2026, cu contul administratorului (dovada.71507, cabinetul 48765), după seed (recalculare cu funcțiile aplicației, pe firmele active ale cabinetului,
a rezumatelor de termene și a rezultatelor Supervizorului, ca lucrătorul de fundal; seed-ul și serverul folosesc data calendaristică reală, `azi_ro`, ca modelul `_supervizor` din e2e_lot12_texte.py):
  f.1  pagina principală a cabinetului are cardul «Control fiscal» (invariant);
  f.2  Firme existente păstrează butonul «+ Adaugă firmă» (invariant);
  a.1  AC014: Termene › rândul D112 › «Deschide» › Detaliu termen: `.mig-frand-sub` conține «restanță de» (oracol);
  a.2  AC017: Sinteza zilei are textul «Priorități» (oracol);
  a.3  AC022: antetul Supervizorului conține «de lămurit» (oracol);
  a.4  AC022: antetul nu mai conține «0 constatări pe 0 firme» (oracol);
  a.5  AC025: Capacitate: textul ferestrei conține «Ana Asistent» (oracol);
  a.6  AC027: Consolidare: `.pf-lista` conține «,00» (oracol);
  a.7  AC036: Detaliu firmă F2: `#cf-perioade` conține «D390 10/2026» (oracol);
  a.8  AC014: în Detaliu termen, «Deschide declarația» deschide Declarații cu firma rândului și tipul D112;
  a.9  AC015: Firme existente, la 1366×768 și la 603×590: paragraful «Butonul Scoate» e după ultimul rând de firmă; firme.js nu mai are matchMedia în randeazaListaFirme;
  a.10 AC017: în Sinteza zilei rândul de restanțe are cifra egală cu `restante` din /termene și un clic deschide Termene;
  a.11 AC024: în Supervizor prima `.sv-firma` are o diferență, primul ei rând e o constatare cu diferență, iar «Firme cu diferențe de lămurit» precede «Firme fără diferențe»;
  a.12 AC022: D + C din antet = `rezumat.constatari_total` și T = `rezumat.firme_in_domeniu` din /supervizor, T > 0;
  a.13 AC034: Tipare de erori cu /tipare simulat: tabelul pe tipuri (3 rânduri, «Total (toate pregătirile)» = «6 din 23»), tabelul pe firme («Total (firmele cu respingeri)» = 6 și 20), nota, totaluri egale;
  a.14 AC035: cu /asistenti/echipa/semafor simulat: cardul Activitate spune «1 asistent necesită atenție», Tipare de erori are secțiunea cu «Ana Asistent» și «tipar sistematic»;
  a.15 AC027 + AC028: Consolidare: toate celulele numerice au două zecimale (`^-?[0-9.]+,[0-9]{2}$`), Cash-ul lui F5 SRL Salariati SRL e negativ în /cabinet/consolidare și în ecran, cu aceeași valoare;
  a.16 AC025: Capacitate: tabelul din starea cu echipă mică are 3 rânduri în ordinea din /capacitate, iar «Deschide Asistenți» rămâne.
Rândurile INFO: `INFO restante=<n> scadente=<n>`, `INFO sv diferente=<D> fara_diferenta=<C> total=<D+C>`, `INFO sv_rezumat …`, `INFO sv_prima_firma <nume> <textul primului rând>`, `INFO cash_F5 <valoare>`, `INFO termene_d112 <n>`, `INFO seed …`.
Nu salvează nimic în afara seed-ului; nu alege niciun fișier. Răspunsurile simulate (a.13, a.14) sunt singurele rute înlocuite în browser, numai /tipare și /asistenti/echipa/semafor."""
import json
import os
import re
import sys

from conftest import BAZA, sesiune, sql

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)

ADMIN = "dovada.71507@sesiuneab.test"
CABINET = 48765
F5 = "F5 SRL Salariati SRL"
TOP = ".fereastra-overlay:not(.fundal) "
IDURI = ["f.1", "f.2"] + ["a.%d" % i for i in range(1, 17)]
DIFERENTA = ("rosu", "galben")
RX_SUMA = re.compile(r"^-?[0-9.]+,[0-9]{2}$")
NOTA_TOTAL = "Numai firmele cu respingeri, cel mult 15; „Total” numără pregătirile acestor firme, nu pe toate ale cabinetului."

# răspunsurile simulate: exact câmpurile citite de JS (tipare.js, cabinet.js)
TIPARE_SIM = {"ok": True, "are_date": True, "motive": [{"motiv": "Cont greșit", "n": 6}],
              "tipuri": [{"tip": "d112", "total": 2, "respinse": 0, "pct": 0}, {"tip": "d300", "total": 21, "respinse": 6, "pct": 29}],
              "firme": [{"tenant_id": 105779, "nume": "F1 Comert Stoc SRL", "cui": "401002001", "respinse": 6, "total": 20}], "respinse": 6}
SEMAFOR_SIM = {"ok": True, "culoare": "rosu", "counts": {"rosu": 1, "galben": 0, "verde": 0}, "zile": 30,
               "asistenti": [{"id": 1, "nume": "Ana Asistent", "culoare": "rosu", "respinse": 6, "rata": 30}]}

JS_TEXT = """(sel) => Array.from(document.querySelectorAll('.fereastra-overlay:not(.fundal) ' + sel)).map((e) => (e.textContent || '').trim().replace(/\\s+/g, ' ')).join(',')"""
JS_MAIN = """() => Array.from(document.querySelectorAll('main')).map((e) => (e.textContent || '').trim().replace(/\\s+/g, ' ')).join(',')"""
JS_JSON = """async (url) => { const t = sessionStorage.getItem('iconta_token'); const r = await fetch(url, {credentials: 'same-origin', headers: t ? {Authorization: 'Bearer ' + t} : {}});
  if (!r.ok) throw new Error('HTTP ' + r.status + ' pe ' + url); return await r.json(); }"""
JS_SEF = "() => { const b = document.querySelector('.cab-grila > .firme-grup .firme-grup-btn[aria-expanded=\"false\"]'); if (b) b.click(); }"
JS_D112 = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) #term-lista tbody tr')].map((tr) => (tr.cells[1] ? tr.cells[1].textContent.trim() : ''))"""
JS_NOTA_SCOATE = """() => {
  const f = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!f) return null;
  const p = [...f.querySelectorAll('p.ecran-nota')].find((e) => /Butonul\\s+Scoate/.test(e.textContent || ''));
  const linii = [...f.querySelectorAll('.firme-rand-linie')]; const q = f.querySelector('#firme-q');
  if (!p || !linii.length || !q) return {p: !!p, n: linii.length, q: !!q};
  const u = linii[linii.length - 1], rp = p.getBoundingClientRect(), ru = u.getBoundingClientRect(), rq = q.getBoundingClientRect();
  return {p: true, n: linii.length, top: Math.round(rp.top), ub: Math.round(ru.bottom), qb: Math.round(rq.bottom),
          dom_dupa: !!(u.compareDocumentPosition(p) & Node.DOCUMENT_POSITION_FOLLOWING), dom_dupa_q: !!(q.compareDocumentPosition(p) & Node.DOCUMENT_POSITION_FOLLOWING)};
}"""
JS_PRIORITATI = """() => {
  const f = document.querySelector('.fereastra-overlay:not(.fundal)'); if (!f) return null;
  const sec = [...f.querySelectorAll('.sa-sectiune')].find((s) => { const c = s.querySelector('.sa-cap'); return c && c.textContent.replace(/\\s+/g, ' ').trim() === 'Priorități'; });
  if (!sec) return {sectiune: false, randuri: []};
  return {sectiune: true, prima: f.querySelector('.sa-sectiune') === sec, randuri: [...sec.querySelectorAll('button')].map((b) => b.textContent.replace(/\\s+/g, ' ').trim())};
}"""
JS_SV = """() => {
  const z = document.querySelector('.fereastra-overlay:not(.fundal) #sv-zona'); if (!z) return null;
  const norm = (t) => (t || '').replace(/\\s+/g, ' ').trim();
  const prima = z.querySelector('.sv-firma'); if (!prima) return {prima: null};
  const titluri = [...z.querySelectorAll('h3.pf-subtitlu.ds-grup-titlu')].map((h) => ({text: norm(h.textContent), inainte: !!(h.compareDocumentPosition(prima) & Node.DOCUMENT_POSITION_FOLLOWING)}));
  let randuri = [...prima.querySelectorAll('.cf-incr-rand')];
  if (!randuri.length) randuri = [...prima.querySelectorAll('.ds-semnal-cutie')].filter((e) => !e.closest('[data-prospetime]'));
  const r = randuri[0] || null; const t = r ? r.querySelector('.ds-semnal-text') : null; const s = r ? r.querySelector('.ds-semnal') : null;
  return {prima: norm((prima.querySelector('.sv-firma-nume') || {}).textContent), titluri, n_randuri: randuri.length,
          rand_text: r ? norm(r.textContent) : null, rand_titlu: t ? norm(t.getAttribute('title')) : null, rand_ton: s ? ([...s.classList].find((c) => c.startsWith('ds-semnal-') && c !== 'ds-semnal') || null) : null};
}"""
JS_CAP = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .cap-tabel tbody tr')].map((tr) => { const td = tr.cells[0].cloneNode(true);
  td.querySelectorAll('.cap-rol').forEach((x) => x.remove()); return (td.textContent || '').replace(/\\s+/g, ' ').trim(); })"""
JS_CONS = """() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .pf-lista .pf-frand')].map((r) => {
  const sp = [...r.children].filter((e) => e.tagName === 'SPAN').map((e) => (e.textContent || '').trim());
  const nm = r.querySelector('.pf-frand-text');
  return {nume: nm ? (nm.textContent || '').replace(/\\s+/g, ' ').trim() : '', celule: sp, total: !!r.closest('#cons-total')}; })"""
JS_TIPARE = """() => {
  const f = document.querySelector('.fereastra-overlay:not(.fundal)'); const norm = (t) => (t || '').replace(/\\s+/g, ' ').trim();
  return {tabele: [...f.querySelectorAll('.cap-tabel')].map((t) => ({antet: [...t.tHead.rows[0].cells].map((c) => norm(c.textContent)),
            randuri: [...t.tBodies[0].rows].map((r) => [...r.cells].map((c) => norm(c.textContent)))})),
          titluri: [...f.querySelectorAll('h3.tip-titlu')].map((h) => norm(h.textContent)), note: [...f.querySelectorAll('.cap-nota')].map((n) => norm(n.textContent))};
}"""


def _norm(t):
    return " ".join((t or "").split())


def _suma_ro(v):
    """Formatul canonic al lui `bani` (api.js): 1.234,56, cu minus în față pentru negative."""
    s = "{:,.2f}".format(abs(float(v))).replace(",", "§").replace(".", ",").replace("§", ".")
    return ("-" if float(v) < 0 and s != "0,00" else "") + s


class Rezultate:
    def __init__(self):
        self.r, self.info = {}, []

    def pune(self, id_, ok, valoare):
        self.r[id_] = (bool(ok), _norm(str(valoare))[:260])

    def cade(self, ids, e):
        for i in ids:
            if i not in self.r:
                self.r[i] = (False, "EXCEPȚIE %s: %s" % (type(e).__name__, _norm(str(e))[:200]))


def _json(pg, url):
    return pg.evaluate(JS_JSON, url)


def _acasa(pg, sef=False):
    """Pagina principală proaspătă; cu sef=True deschide secțiunea «Pentru șeful de cabinet» (Supervizor, Capacitate, Consolidare, Activitate stau în ea)."""
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
    try:
        pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=20000)
    except Exception:   # noqa: BLE001 — contoarele întârzie: se judecă ce s-a desenat
        pass
    if sef:
        pg.evaluate(JS_SEF)
    pg.wait_for_timeout(800)


def _card(cheie):
    return "button.cab-card:has([data-cheie='%s'])" % cheie


def _deschide(pg, cheie, asteapta, sef=False, timp=1500):
    """Pagina principală › cardul `cheie` › așteptarea unui element al ferestrei; fals dacă elementul n-a apărut."""
    _acasa(pg, sef)
    pg.click(_card(cheie), timeout=10000)
    try:
        pg.wait_for_selector(TOP + asteapta, state="attached", timeout=45000)
        ok = True
    except Exception:   # noqa: BLE001
        ok = False
    pg.wait_for_timeout(timp)
    return ok


def _text(pg, sel=""):
    return pg.evaluate(JS_TEXT, sel)


def _seed(rez):
    """Definiția «seed» din comandă: `firma_rezumat.recalculeaza_greu(tenant_id, schema, azi=azi)` (termene si control_fiscal in aceeasi trecere; recalculeaza_firma(.., ["termene"]) nu face nimic: «termene» nu e aspect usor) și `supervizor_cache.recalculeaza_firma(tenant_id, schema, an, luna)`, cu (an, luna) = luna_confruntata pe azi_ro(),
    pentru fiecare firmă activă a cabinetului 48765."""
    from core import firma_rezumat, supervizor_cache
    from core.common import azi_ro
    from core.control_fiscal_api import luna_confruntata
    azi = azi_ro()
    an, luna = luna_confruntata(azi.year, azi.month)
    firme = sql("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id = %s AND activ = true ORDER BY id", (CABINET,))
    for tid, schema in firme:
        firma_rezumat.recalculeaza_greu(tid, schema, azi=azi)
        supervizor_cache.recalculeaza_firma(tid, schema, an, luna)
    rez.info.append("seed firme=%d ids=%s perioada_supervizor=%02d/%d azi=%s" % (len(firme), ",".join(str(f[0]) for f in firme), luna, an, azi.isoformat()))


def _intra_firme(pg):
    """Pagina principală › Firme › Firme existente (lista desenată)."""
    _acasa(pg)
    pg.click(_card("firme"), timeout=10000)
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector(TOP + "#firme-lista button.firme-rand", state="attached", timeout=30000)
    pg.wait_for_timeout(1000)


def _corp_functie(sursa, nume):
    i = sursa.find("function " + nume)
    if i < 0:
        return None
    j = sursa.find("\n}\n", i)
    return sursa[i:j if j > 0 else len(sursa)]


def s_firme(pg, rez):
    ids = ["f.1", "f.2", "a.9"]
    try:
        _acasa(pg)
        t = pg.evaluate(JS_MAIN)
        rez.pune("f.1", "Control fiscal" in t, "main: %s" % t[:70])
        _intra_firme(pg)
        t = _text(pg)
        rez.pune("f.2", "Adaugă firmă" in t, "fereastră: %s" % t[:90])
        # a.9: la 1366×768 și la 603×590 paragraful «Butonul Scoate» e după ultimul rând al firmelor și după căsuța de căutare; fără matchMedia în randeazaListaFirme
        parti, bune = [], True
        for (w, h) in ((1366, 768), (603, 590)):
            pg.set_viewport_size({"width": w, "height": h})
            _intra_firme(pg)
            m = pg.evaluate(JS_NOTA_SCOATE) or {}
            ok = bool(m.get("p")) and m.get("n", 0) > 0 and m.get("dom_dupa") and m.get("dom_dupa_q") and m.get("top", -1) >= m.get("ub", 10 ** 9) and m.get("top", -1) >= m.get("qb", 10 ** 9)
            bune = bune and ok
            parti.append("%dx%d %s" % (w, h, m))
        sursa = open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
        corp = _corp_functie(sursa, "randeazaListaFirme")
        mm = None if corp is None else corp.count("matchMedia")
        rez.pune("a.9", bune and mm == 0, "%s; matchMedia în randeazaListaFirme: %s" % ("; ".join(parti), "funcția lipsește" if mm is None else mm))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)
    finally:
        pg.set_viewport_size({"width": 1366, "height": 768})


def s_termene(pg, rez):
    ids = ["a.1", "a.8"]
    try:
        t = _json(pg, "/termene")
        rez.info.append("restante=%s scadente=%d" % (t.get("restante"), sum(1 for g in t.get("grupuri", []) if g.get("zile", -1) >= 0)))
    except Exception as e:   # noqa: BLE001
        rez.info.append("restante=? scadente=? (%s)" % type(e).__name__)
    try:
        if not _deschide(pg, "termene", "#term-lista tbody tr"):
            raise RuntimeError("Termene: tabelul scadențelor n-a apărut")
        tipuri = pg.evaluate(JS_D112)
        rez.info.append("termene_d112 %d" % sum(1 for x in tipuri if x == "D112"))
        if "D112" not in tipuri:
            raise RuntimeError("Termene: niciun rând D112 (martor lipsă)")
        pg.locator(TOP + "#term-lista tbody tr").nth(tipuri.index("D112")).locator("button", has_text="Deschide").first.click(timeout=10000)
        pg.wait_for_selector(TOP + ".mig-frand-sub", state="attached", timeout=20000)
        pg.wait_for_timeout(800)
        sub = _text(pg, ".mig-frand-sub")
        rez.pune("a.1", "restanță de" in sub, sub[:200])
        nume = _norm(pg.locator(TOP + ".mig-frand .mig-frand-nume").first.text_content())
        buton = pg.locator(TOP + ".mig-frand button", has_text="Deschide declarația")
        if not buton.count():
            rez.pune("a.8", False, "butonul «Deschide declarația» lipsește din rândurile Detaliu termen (firma %s)" % nume)
            return
        buton.first.click(timeout=10000)
        pg.wait_for_selector(TOP + "#dec-tip", state="attached", timeout=40000)
        pg.wait_for_timeout(800)
        firma = _norm(pg.evaluate("() => { const s = document.querySelector('.fereastra-overlay:not(.fundal) #dec-firma'); return s && s.selectedOptions[0] ? s.selectedOptions[0].textContent : ''; }"))
        tip = pg.evaluate("() => { const s = document.querySelector('.fereastra-overlay:not(.fundal) #dec-tip'); return s ? s.value : null; }")
        rez.pune("a.8", firma == nume and tip == "d112", "rând: %s; Declarații: firma %s, tip %s" % (nume, firma, tip))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_sinteza(pg, rez):
    ids = ["a.2", "a.10"]
    try:
        t = _json(pg, "/termene")
        restante = t.get("restante", 0)
        if not _deschide(pg, "brief", ".sa-cifre", timp=2500):
            raise RuntimeError("Sinteza zilei: fereastra n-a apărut")
        text = _text(pg)
        rez.pune("a.2", "Priorități" in text, text[:120])
        pr = pg.evaluate(JS_PRIORITATI) or {}
        randuri = pr.get("randuri", [])
        rest = [r for r in randuri if re.match(r"^\d+\s+(?:de\s+)?declara\S+\s+restan\S+", r)]
        if restante <= 0:
            rez.pune("a.10", False, "restante=%s în /termene: martorul rândului de restanțe lipsește" % restante)
            return
        if not rest:
            rez.pune("a.10", False, "niciun rând de restanțe în «Priorități» (restante=%s; secțiune=%s; rânduri=%s)" % (restante, pr.get("sectiune"), randuri))
            return
        n = int(re.match(r"^(\d+)", rest[0]).group(1))
        pg.locator(TOP + ".sa-sectiune button", has_text=re.compile(r"restan")).first.click(timeout=10000)
        deschis = True
        try:
            pg.wait_for_selector(TOP + "#term-zona, " + TOP + "#term-lista", state="attached", timeout=30000)
        except Exception:   # noqa: BLE001
            deschis = False
        rez.pune("a.10", n == restante and deschis, "rând «%s», restante în /termene = %s, Termene deschis: %s" % (rest[0], restante, deschis))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_supervizor(pg, rez):
    ids = ["a.3", "a.4", "a.11", "a.12"]
    try:
        sv = _json(pg, "/supervizor")
        D = C = 0
        for f in sv.get("firme", []):
            for c in f.get("constatari") or []:
                if c.get("stare") in DIFERENTA:
                    D += 1
                else:
                    C += 1
        z = sv.get("rezumat") or {}
        rez.info.append("sv diferente=%d fara_diferenta=%d total=%d" % (D, C, D + C))
        rez.info.append("sv_rezumat constatari_total=%s firme_in_domeniu=%s" % (z.get("constatari_total"), z.get("firme_in_domeniu")))
        if not _deschide(pg, "supervizor", ".sv-antet", sef=True, timp=2500):
            raise RuntimeError("Supervizor: antetul n-a apărut")
        antet = _text(pg, ".sv-antet")
        rez.pune("a.3", "de lămurit" in antet, antet[:160])
        rez.pune("a.4", "0 constatări pe 0 firme" not in antet, antet[:160])
        # a.12: D + C din antet = rezumat.constatari_total; T = rezumat.firme_in_domeniu; T > 0
        mD = re.search(r"(\d+)\s*(?:de\s+)?diferen\S*\s+de\s+lămurit", antet)
        mC = re.search(r"(\d+)\s*(?:de\s+)?confrunt\S*\s+fără\s+diferen", antet)
        mT = re.findall(r"din\s*(\d+)\s*(?:de\s+)?firm", antet)
        if not (mD and mC and mT):
            rez.pune("a.12", False, "antet fără cifrele D / C / T (D=%s C=%s T=%s): %s" % (bool(mD), bool(mC), mT, antet[:160]))
        else:
            d, c, t = int(mD.group(1)), int(mC.group(1)), int(mT[-1])
            rez.pune("a.12", d + c == z.get("constatari_total") and t == z.get("firme_in_domeniu") and t > 0,
                     "antet D=%d C=%d T=%d; rezumat constatari_total=%s firme_in_domeniu=%s" % (d, c, t, z.get("constatari_total"), z.get("firme_in_domeniu")))
        # a.11: ordinea din #sv-zona
        o = pg.evaluate(JS_SV) or {}
        nume = o.get("prima")
        firma = next((f for f in sv.get("firme", []) if _norm(f.get("nume")) == nume), None) if nume else None
        cs = (firma or {}).get("constatari") or []
        are_dif = any(c.get("stare") in DIFERENTA for c in cs)
        titluri = [t_["text"] for t_ in o.get("titluri", [])]
        T_DIF, T_FARA = "Firme cu diferențe de lămurit", "Firme fără diferențe"
        # starea primului rând: constatarea al cărei mesaj e titlul rândului (titlul întreg) sau, fără titlu, tonul semnalului («avertisment» = roșu sau galben)
        stare = None
        if o.get("rand_titlu"):
            pot = [c for c in cs if _norm(c.get("mesaj")) == o["rand_titlu"]]
            stare = pot[0].get("stare") if pot else None
        rand_dif = (stare in DIFERENTA) if stare is not None else (o.get("rand_ton") == "ds-semnal-avertisment")
        ordine = T_DIF in titluri and T_FARA in titluri and titluri.index(T_DIF) < titluri.index(T_FARA)
        inainte = bool(titluri) and any(t_["text"] == T_DIF and t_["inainte"] for t_ in o.get("titluri", []))
        rez.info.append("sv_prima_firma %s %s" % (nume, (o.get("rand_text") or "")[:160]))
        rez.pune("a.11", bool(firma) and are_dif and rand_dif and ordine and inainte,
                 "prima firmă %s (diferență în răspuns: %s); primul rând: stare %s ton %s; titluri %s" % (nume, are_dif, stare, o.get("rand_ton"), titluri))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_capacitate(pg, rez):
    ids = ["a.5", "a.16"]
    try:
        cap = _json(pg, "/capacitate")
        nume_api = [_norm(a.get("nume")) for a in cap.get("asistenti", [])]
        if not _deschide(pg, "capacitate", ".cap-ecran", sef=True, timp=1500):
            raise RuntimeError("Capacitate: fereastra n-a apărut")
        text = _text(pg)
        rez.pune("a.5", "Ana Asistent" in text, text[:160])
        randuri = pg.evaluate(JS_CAP)
        buton = pg.locator(TOP + "#cap-adauga-asistenti").count()
        rez.pune("a.16", len(randuri) == 3 and randuri == nume_api and buton == 1,
                 "rânduri în tabel %s; /capacitate asistenti %s; butonul «Deschide Asistenți»: %d" % (randuri, nume_api, buton))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_consolidare(pg, rez):
    ids = ["a.6", "a.15"]
    try:
        cons = _json(pg, "/cabinet/consolidare")
        if not _deschide(pg, "consolidare", "#cons-total", sef=True, timp=1500):
            raise RuntimeError("Consolidare: fereastra n-a apărut")
        rez.pune("a.6", ",00" in _text(pg, ".pf-lista"), _text(pg, ".pf-lista")[:160])
        randuri = [r for r in pg.evaluate(JS_CONS) if not (r["celule"] and r["celule"][0] == "Venituri")]   # fără antetul tabelului
        rele = []
        for r in randuri:
            if len(r["celule"]) != 4:
                rele.append("«%s»: %d celule în loc de 4" % (r["nume"], len(r["celule"])))
            for c in r["celule"]:
                if c != "—" and not RX_SUMA.match(c):
                    rele.append("«%s»: «%s»" % (r["nume"], c))
        if not any(r["total"] for r in randuri) or sum(1 for r in randuri if not r["total"]) < 1:
            rele.append("rândurile firmelor sau rândul Total lipsesc (%d rânduri)" % len(randuri))
        f5 = next((r for r in randuri if r["nume"] == F5), None)
        api5 = next((f for f in cons.get("firme", []) if _norm(f.get("nume")) == F5), None)
        cash_api = ((api5 or {}).get("kpi") or {}).get("cash")
        cash_ecran = f5["celule"][3] if f5 and len(f5["celule"]) == 4 else None
        rez.info.append("cash_F5 %s" % cash_ecran)
        if f5 is None or api5 is None or cash_api is None:
            rele.append("rândul sau KPI-ul lui %s lipsește (ecran: %s, API: %s)" % (F5, f5 is not None, api5 is not None))
        else:
            if not float(cash_api) < 0:
                rele.append("Cash %s în /cabinet/consolidare = %s (nu e negativ)" % (F5, cash_api))
            if cash_ecran != _suma_ro(cash_api):
                rele.append("Cash %s în ecran «%s» ≠ API %s (%s)" % (F5, cash_ecran, cash_api, _suma_ro(cash_api)))
        rez.pune("a.15", not rele, "%d rânduri; cash F5 ecran %s, API %s; %s" % (len(randuri), cash_ecran, cash_api, "; ".join(rele[:4]) or "toate celulele au două zecimale"))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_detaliu_f2(pg, rez):
    ids = ["a.7"]
    try:
        if not _deschide(pg, "control", "#cf-lista tbody tr", timp=1500):
            raise RuntimeError("Control fiscal: lista firmelor n-a apărut")
        pg.locator(TOP + "#cf-lista tbody tr", has_text="F2 Profit").first.locator("button", has_text="Deschide").first.click(timeout=10000)
        try:
            pg.wait_for_selector(TOP + "#cf-perioade", state="attached", timeout=60000)
        except Exception:   # noqa: BLE001 — secțiunea apare numai dacă F2 are constatări
            pass
        pg.wait_for_timeout(1000)
        t = _text(pg, "#cf-perioade")
        rez.pune("a.7", "D390 10/2026" in t, t[:200] or "#cf-perioade lipsește (F2 fără constatări)")
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)


def s_simulat(browser, rez):
    """a.13 și a.14: /tipare și /asistenti/echipa/semafor înlocuite în browser (snapshotul n-are rânduri în declaratii_coada și nici date de calitate pentru semafor)."""
    from core import ceas_proba
    ids = ["a.13", "a.14"]
    ctx = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        ctx.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        ctx.add_init_script(sesiune(ADMIN))
        pg = ctx.new_page()
        pg.route(re.compile(r"/tipare(\?.*)?$"), lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(TIPARE_SIM)))
        pg.route(re.compile(r"/asistenti/echipa/semafor(\?.*)?$"), lambda route: route.fulfill(status=200, content_type="application/json", body=json.dumps(SEMAFOR_SIM)))
        pg.goto(BAZA + "/", wait_until="domcontentloaded")
        pg.wait_for_selector(".cab-grila button.cab-card", timeout=30000)
        pg.evaluate(JS_SEF)
        pg.wait_for_function("() => /necesită atenție/.test((document.querySelector('[data-cheie=\"activitate\"]') || {textContent: ''}).textContent)", timeout=25000)
        card = _norm(pg.evaluate("() => document.querySelector('[data-cheie=\"activitate\"]').textContent"))
        pg.click(_card("activitate"), timeout=10000)
        pg.click(TOP + "#opt-tipare", timeout=20000)
        pg.wait_for_selector(TOP + "#tip-tabel-tipuri", state="attached", timeout=30000)
        pg.wait_for_timeout(800)
        d = pg.evaluate(JS_TIPARE)
        tabele = d["tabele"]
        t_tipuri = next((t for t in tabele if t["antet"] and t["antet"][0].startswith("Declarație sau notă")), None)
        t_firme = next((t for t in tabele if t["antet"] and t["antet"][0] == "Firmă"), None)
        t_asist = next((t for t in tabele if t["antet"] and t["antet"][0] == "Asistent"), None)
        # a.13
        rele = []
        rt = (t_tipuri or {}).get("randuri", [])
        if len(rt) != 3:
            rele.append("tabelul pe tipuri are %d rânduri (așteptat 3: D112, D300, Total)" % len(rt))
        else:
            if not (rt[0][0] == "D112" and rt[0][1] == "0 din 2"):
                rele.append("rândul 1: %s (așteptat D112, «0 din 2»)" % rt[0])
            if not (rt[1][0] == "D300" and rt[1][1] == "6 din 21"):
                rele.append("rândul 2: %s (așteptat D300, «6 din 21»)" % rt[1])
            if not (rt[2][0] == "Total (toate pregătirile)" and rt[2][1] == "6 din 23"):
                rele.append("rândul Total: %s (așteptat «Total (toate pregătirile)», «6 din 23»)" % rt[2])
        rf = (t_firme or {}).get("randuri", [])
        tot_f = next((r for r in rf if r and r[0] == "Total (firmele cu respingeri)"), None)
        if not tot_f or tot_f[1:3] != ["6", "20"]:
            rele.append("tabelul pe firme: rândul «Total (firmele cu respingeri)» = %s (așteptat 6 și 20)" % (tot_f,))
        if NOTA_TOTAL not in d["note"]:
            rele.append("nota de sub tabelul pe firme lipsește (note: %s)" % d["note"])
        resp_tipuri = int(re.match(r"(\d+)", rt[2][1]).group(1)) if len(rt) == 3 and re.match(r"(\d+)", rt[2][1]) else None
        resp_firme = int(tot_f[1]) if tot_f and tot_f[1].isdigit() else None
        if resp_tipuri is None or resp_firme is None or resp_tipuri != resp_firme:
            rele.append("Respinse din cele două totaluri: tipuri %s, firme %s" % (resp_tipuri, resp_firme))
        rez.pune("a.13", not rele, "; ".join(rele) or "tipuri %s; firme %s; Respinse egale (%s)" % (rt, rf, resp_tipuri))
        # a.14
        rand_ana = next((r for r in (t_asist or {}).get("randuri", []) if r and r[0] == "Ana Asistent"), None)
        ok14 = card == "1 asistent necesită atenție" and rand_ana is not None and "tipar sistematic" in " ".join(rand_ana) and "Asistenți care necesită atenție" in d["titluri"]
        rez.pune("a.14", ok14, "card «%s»; titluri %s; rândul asistentului %s" % (card, d["titluri"], rand_ana))
    except Exception as e:   # noqa: BLE001
        rez.cade(ids, e)
    finally:
        ctx.close()


def test_cabinet_17_5_M(browser, capsys):
    from core import ceas_proba
    rez = Rezultate()
    b = browser.new_context(viewport={"width": 1366, "height": 768})
    try:
        _seed(rez)
        b.clock.set_fixed_time(ceas_proba.MOMENT_REF)
        b.add_init_script(sesiune(ADMIN))
        pg = b.new_page()
        pg.goto(BAZA + "/", wait_until="load", timeout=30000)
        s_firme(pg, rez)
        s_termene(pg, rez)
        s_sinteza(pg, rez)
        s_supervizor(pg, rez)
        s_capacitate(pg, rez)
        s_consolidare(pg, rez)
        s_detaliu_f2(pg, rez)
    finally:
        b.close()
    s_simulat(browser, rez)
    with capsys.disabled():
        for i in rez.info:
            print("INFO " + i)
        for i in IDURI:
            ok, val = rez.r.get(i, (False, "neevaluat"))
            print("REZULTAT %s %s %s" % (i, "trece" if ok else "pica", val))
            if i in rez.r:
                print("VERDICT %s %s" % (i, "trece" if ok else "pica"), flush=True)
    rele = ["%s: %s" % (i, rez.r.get(i, (False, "neevaluat"))[1]) for i in IDURI if not rez.r.get(i, (False, ""))[0]]
    assert not rele, "ecranele cabinetului 17.5-M [INFO: %s]: %d din %d id-uri pică: %s" % ("; ".join(rez.info), len(rele), len(IDURI), " | ".join(rele))
