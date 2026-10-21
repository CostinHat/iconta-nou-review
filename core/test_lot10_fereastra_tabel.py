# -*- coding: utf-8 -*-
"""Lotul 10, deficiențele 421 și 424 (aceeași clasă, toată aplicația) — fereastra cu tabel.

Comanda Costin 10.1 pct.5, verbatim în DECIZII: „Deficiența 421 și 424 (clasă, toată aplicația) — ferestrele cu tabele cer multe derulări:
ocupă cam jumătate din lățimea ecranului, tabelul de import salariați are derulare laterală, butonul de salvare și mesajele de blocare sunt
la capătul conținutului (regula 285 nerespectată aici). Regula: ferestrele cu tabele se deschid aproape pe tot ecranul (cum e deja Balanța
de verificare); rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar tabelul din mijloc, niciodată lateral.”

Temei: N/A — regulă de UI (DS cap.9 v2.96, „Fereastra cu tabel”).

Ce păzește:
  1. Regula verificatorului (`verificator_conformitate.analiza_fereastra_tabel`) — logica REALĂ, scoasă din fișier cu `ast` și chemată pe
     fragmente known-good / known-bad (ca `test_verificator_izolare.py`, dar fără să ruleze tot auditul): FEREASTRA_TABEL (navigator +
     stil.css), DERULARE_INLINE, ACTIUNE_TABEL_NEFIXATA. Fiecare cod are fragmentul rău care trebuie prins și fragmentul bun care nu.
  2. Navigatorul și stil.css REALE, în Chromium (1366×768): codul `_prealata` / `_cuTabel` / `_lateste` luat din navigator.js, pe o fereastră
     cu tabel ca Balanța (14 coloane, sume de 7 cifre): fereastra ia aproape tot ecranul, nimic nu derulează lateral, butonul din
     `.bara-fixa` se vede fără derulare, rezumatul și antetul tabelului rămân sus după derularea tabelului la capăt; un tabel mic nu e
     strâns degeaba (331); o fereastră fără tabel nu se lățește.
"""
import ast
import functools
import http.server
import io
import os
import re
import socketserver
import threading

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _citeste(rel):
    return io.open(os.path.join(_RAD, rel), encoding="utf-8").read()


@pytest.fixture(scope="module")
def regula():
    """`analiza_fereastra_tabel` din verificator, fără restul auditului (funcția e pură: primește textele, întoarce tuplurile)."""
    src = _citeste("verificator_conformitate.py")
    fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "analiza_fereastra_tabel"]
    assert len(fn) == 1, "ANTI-VACUU: verificatorul nu mai are funcția `analiza_fereastra_tabel` (gardul 421/424 ar fi dispărut tăcut)"
    ns = {}
    exec(compile(ast.Module(body=fn, type_ignores=[]), "verificator_conformitate.py", "exec"), ns)
    # chemarea ei din audit: altfel funcția ar exista, dar TOTAL nu i-ar număra rezultatele — atribuirea `rap["fereastra_tabel"] =
    # analiza_fereastra_tabel(...)` la nivelul modulului, ca nod (un comentariu sau un șir cu aceleași cuvinte nu o înlocuiește)
    chemari = [n for n in ast.parse(src).body if isinstance(n, ast.Assign) and len(n.targets) == 1
               and isinstance(n.targets[0], ast.Subscript) and getattr(n.targets[0].value, "id", None) == "rap"
               and getattr(n.targets[0].slice, "value", None) == "fereastra_tabel"
               and isinstance(n.value, ast.Call) and getattr(n.value.func, "id", None) == "analiza_fereastra_tabel"]
    assert len(chemari) == 1, "verificatorul nu mai cheamă regula ferestrei cu tabel"
    return ns["analiza_fereastra_tabel"]


@pytest.fixture(scope="module")
def reale():
    fis = {}
    for d in ("static/js/ecrane", "static/js"):
        for f in sorted(os.listdir(os.path.join(_RAD, d))):
            if f.endswith(".js") and ".bak" not in f and f not in fis:
                fis[f] = _citeste(os.path.join(d, f))
    assert len(fis) >= 40 and set(fis) >= {"firme.js", "navigator.js"}, "ANTI-VACUU: %d fișiere JS citite" % len(fis)
    return _citeste("static/stil.css"), _citeste("static/js/navigator.js"), fis


def _coduri(rez, cod):
    return [r for r in rez if r[2] == cod]


# ── 1. regula verificatorului pe fișierele reale ──────────────────────────────────────────────────────────────────────────────────
def test_navigatorul_si_stilul_real_respecta_regula(regula, reale):
    """Pe fișierele de acum: navigatorul pune singur `fer-tabel`, stil.css are fereastra de tot ecranul, corpul fără derulare laterală,
    rezumatul lipit sus, cutia previzualizării fără derulare proprie."""
    css, nav, fis = reale
    assert _coduri(regula(css, nav, fis), "FEREASTRA_TABEL") == []   # comanda 10.1 pct.5: „aproape pe tot ecranul … niciodată lateral”


def test_sabloanele_reale_fara_derulare_inline_si_fara_actiune_la_capat(regula, reale):
    """Starea FINALĂ a lotului: niciun stil inline cu derulare și nicio acțiune care scrie lăsată la capătul unei ferestre cu tabel.
    (Pică până când firme.js și migrare.js sunt aduse la regulă — lucrul sesiunii principale și al subagentului M, în același lot.)"""
    css, nav, fis = reale
    rez = regula(css, nav, fis)
    rele = _coduri(rez, "DERULARE_INLINE") + _coduri(rez, "ACTIUNE_TABEL_NEFIXATA")
    assert rele == [], "\n".join(map(str, rele))   # „butonul de salvare și mesajele de blocare sunt la capătul conținutului”


# ── 2. regula pe fragmente sintetice: fiecare cod, prins (rău) și tăcut (bun) ───────────────────────────────────────────────────────
def test_navigatorul_fara_recunoasterea_tabelului_e_prins(regula, reale):
    css, nav, fis = reale
    rau = nav.replace("(_cuTabel() || _prealata())", "(_prealata())")
    assert rau != nav, "ANTI-VACUU: ancora mutației lipsește din navigator.js"
    assert [r[3] for r in _coduri(regula(css, rau, {}), "FEREASTRA_TABEL")] == ["`_lateste` nu pune `fer-tabel` pe fereastra cu tabel"]
    rau2 = re.sub(r'for \(const treapta of \["fer-strans", "fer-rupt"\]\)[^\n]*', "", nav)
    assert rau2 != nav and len(_coduri(regula(css, rau2, {}), "FEREASTRA_TABEL")) == 1


@pytest.mark.parametrize("ancora, inlocuire, fragment", [
    ("height: calc(100vh - 48px); transition: none;", "transition: none;", "înălțimea ecranului"),
    ("{ width: calc(100vw - 48px); max-width", "{ max-width", "lățimea ecranului"),
    ("{ overflow-x: hidden; overflow-y: auto; }", "{ overflow-x: auto; overflow-y: auto; }", "numai vertical"),
    ("position: sticky; top: -24px; z-index: 3;", "z-index: 3;", "`.rezumat-fix` nu mai e lipit sus"),
    (".mig-prev-cutie { margin-top: 8px; }", ".mig-prev-cutie { max-height: 55vh; overflow: auto; margin-top: 8px; }", "`.mig-prev-cutie` derulează"),
])
def test_stilul_stricat_e_prins(regula, reale, ancora, inlocuire, fragment):
    css, nav, _fis = reale
    assert css.count(ancora) == 1, "ANTI-VACUU: ancora %r nu e (o singură dată) în stil.css" % ancora
    rez = _coduri(regula(css.replace(ancora, inlocuire), nav, {}), "FEREASTRA_TABEL")
    assert any(fragment in r[3] for r in rez), rez   # DS cap.9 v2.96: fiecare jumătate a regulii are gardul ei


def test_o_regula_fer_tabel_care_permite_derularea_laterala_e_prinsa(regula, reale):
    css, nav, _fis = reale
    rez = _coduri(regula(css + "\n.fereastra.fer-tabel .mig-prev { overflow-x: auto; }\n", nav, {}), "FEREASTRA_TABEL")
    # „niciodată lateral”: exact o abatere, a regulii adăugate (selectorul ei), nu „undeva în listă”
    assert [r[3] for r in rez] == ["derulare laterală permisă: .fereastra.fer-tabel .mig-prev"], rez


_SABLON_RAU = '''
async function ecranProba(corp, nav, t) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Proba</h2>
    <table class="fd-tabel"><tbody>${randuri}</tbody></table>
    <button class="buton-primar" id="pr-salveaza" data-actiune="POST /tenants/{tenant_id}/proba">Salvează</button>`;
}
'''


@pytest.mark.parametrize("nume, sursa, asteptat", [
    ("acțiunea la capătul tabelului", _SABLON_RAU, ["pr-salveaza"]),
    ("acțiunea în bara fixă", _SABLON_RAU.replace('<button class="buton-primar"', '<div class="bara-fixa"><button class="buton-primar"')
     .replace("Salvează</button>`", "Salvează</button></div>`"), []),
    ("acțiunea în rezumatul lipit sus", _SABLON_RAU.replace('<button class="buton-primar"', '<div class="rezumat-fix"><button class="buton-primar"')
     .replace("Salvează</button>`", "Salvează</button></div>`"), []),
    ("bara fixă închisă înaintea butonului", _SABLON_RAU.replace('<button class="buton-primar"', '<div class="bara-fixa"><p>x</p></div><button class="buton-primar"'),
     ["pr-salveaza"]),
    ("acțiunea de pe rând (în celulă)", _SABLON_RAU.replace("<tbody>${randuri}</tbody></table>\n    <button", "<tbody><tr><td><button")
     .replace("Salvează</button>`", "Salvează</button></td></tr></tbody></table>`"), []),
    ("acțiunea de pe rând (identificatorul rândului)", _SABLON_RAU.replace('id="pr-salveaza"', 'data-id="${r.id}"'), []),
    ("tabelul adus printr-o variabilă", '''
async function ecranProba(corp, nav, t) {
  const tabel = !randuri.length ? `<div class="stare-goala">Nimic; nimic.</div>` : `<table class="fd-tabel"><tbody></tbody></table>`;
  corp.innerHTML = `<h2>Proba</h2>${tabel}
    <div><button class="buton-primar" id="pr-adauga" data-actiune="PUT /x">Înscrie</button></div>`;
}
''', ["pr-adauga"]),
    ("tabel de machetă (modelul facturii)", _SABLON_RAU.replace('class="fd-tabel"', 'class="mfp-tabel"'), []),
    ("buton care citește", _SABLON_RAU.replace(' data-actiune="POST /tenants/{tenant_id}/proba"', ""), []),
    ("fără tabel în fereastră", _SABLON_RAU.replace("<table class=\"fd-tabel\"><tbody>${randuri}</tbody></table>", "<p>x</p>"), []),
    ("un comentariu cu backtick nu deschide un șablon", "// `fer-tabel` și `x`\n" + _SABLON_RAU, ["pr-salveaza"]),
])
def test_actiunea_ferestrei_cu_tabel(regula, reale, nume, sursa, asteptat):
    css, nav, _fis = reale
    rez = _coduri(regula(css, nav, {"proba.js": sursa}), "ACTIUNE_TABEL_NEFIXATA")
    # comanda 10.1 pct.5: „acțiunea principală fix jos” — butonul care scrie nu rămâne la capătul conținutului
    assert [re.search(r"„([^”]+)”", r[3]).group(1) for r in rez] == asteptat, (nume, rez)


@pytest.mark.parametrize("sursa, n", [
    ('const h = `<div style="overflow-x:auto"><table></table></div>`;', 1),
    ("const h = '<div style=\"max-height:180px;overflow: auto\"></div>';", 1),
    ('el.style.overflowX = "auto";', 1),
    ('const h = `<div style="overflow-y:auto"></div>`;', 0),          # derularea verticală a unei cutii nu e laterală (o prinde altă regulă)
    ("// odinioară: <div style=\"overflow-x:auto\">\nconst h = `<p></p>`;", 0),   # un comentariu nu e șablon
])
def test_derularea_inline(regula, reale, sursa, n):
    css, nav, _fis = reale
    # comanda 10.1 pct.5: „se derulează doar tabelul din mijloc, niciodată lateral” — nicio cutie cu derulare proprie scrisă inline
    assert len(_coduri(regula(css, nav, {"proba.js": sursa}), "DERULARE_INLINE")) == n


# ── 3. navigatorul și stil.css reale, în Chromium ─────────────────────────────────────────────────────────────────────────────────
def _cod_lateste():
    """`_prealata`, `_cuTabel` și `_lateste`, exact cum stau în navigator.js (între prima definiție și primul apel)."""
    nav = _citeste("static/js/navigator.js")
    m = re.search(r"\n(\s*const _prealata = .*?\n\s*\};)\n\s*_lateste\(\);", nav, re.S)
    # ANTI-VACUU pe structura blocului: cele trei definiții, în ordine, și treptele de strângere, exact
    assert m and re.findall(r"\bconst (_\w+) = ", m.group(1)) == ["_prealata", "_cuTabel", "_lateste"] \
        and re.findall(r'"(fer-[a-z]+)"', m.group(1)) == ["fer-tabel", "fer-tabel", "fer-tabel", "fer-strans", "fer-rupt"], \
        "ANTI-VACUU: blocul `_lateste` nu mai e în navigator.js"
    return m.group(1)


@pytest.fixture(scope="module")
def pagina():
    from playwright.sync_api import sync_playwright
    from core.test_emitere_randuri_dinamice import _lanseaza_chromium
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=_RAD))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    pw = sync_playwright().start()
    b = _lanseaza_chromium(pw)
    if b is None:
        pw.stop()
        srv.shutdown()
        pytest.fail("GARD headless nu poate rula: chromium indisponibil. NU e skip verde-fals.")
    p = b.new_page(viewport={"width": 1366, "height": 768})
    p.goto("http://127.0.0.1:%d/static/" % srv.server_address[1])
    try:
        yield p
    finally:
        b.close()
        pw.stop()
        srv.shutdown()


_FEREASTRA_JS = """([cod, randuri, coloane, suma, cuTabel]) => {
  document.head.innerHTML = '<link rel="stylesheet" href="/static/stil.css">';
  return new Promise((gata) => { document.head.querySelector('link').onload = () => {
    const th = Array.from({length: coloane}, (_, i) => `<th class="fd-td-num">Sold inițial debitor ${i}</th>`).join('');
    const tr = Array.from({length: randuri}, () => '<tr><td>5311</td><td>Casa în lei</td>' +
      Array.from({length: coloane}, () => `<td class="fd-td-num">${suma}</td>`).join('') + '</tr>').join('');
    const tabel = cuTabel ? `<table class="fd-tabel"><thead><tr><th>Cont</th><th>Denumire</th>${th}</tr></thead><tbody>${tr}</tbody></table>`
                          : '<p>Un formular fără tabel.</p>';
    document.body.innerHTML = `<div class="fereastra-overlay"><div class="fereastra"><div class="fereastra-antet"><span>Balanță</span></div>
      <div class="fereastra-corp" tabindex="0"><h2 class="pf-titlu">Balanță de verificare</h2>
      <div class="rezumat-fix" id="rez"><p class="pf-intro">Luna 09.2026 · ${randuri} conturi</p></div>${tabel}
      <div class="bara-fixa"><p><button class="buton-primar" id="b-pdf">Descarcă PDF</button></p><div id="b-mesaj">Refuzul se vede.</div></div>
      </div></div></div>`;
    const fer = document.querySelector('.fereastra'), _corp = fer.querySelector('.fereastra-corp');
    void fer.offsetWidth;   // ca în aplicație: fereastra e deja așezată (îngustă) când îi sosește tabelul
    new Function('_corp', 'fer', cod + '\\n_lateste();')(_corp, fer);
    const r = (e) => { const b = e.getBoundingClientRect(); return {sus: Math.round(b.top), jos: Math.round(b.bottom)}; };
    const o = {clase: [...fer.classList].sort(), lat: fer.offsetWidth, inalt: fer.offsetHeight, sw: _corp.scrollWidth, cw: _corp.clientWidth,
      laterale: [...fer.querySelectorAll('*')].filter((e) => ['auto', 'scroll'].includes(getComputedStyle(e).overflowX)
                                                         && e.scrollWidth > e.clientWidth + 1).map((e) => e.className),
      buton: r(document.querySelector('#b-pdf')), mesaj: r(document.querySelector('#b-mesaj')), corp: r(_corp)};
    _corp.scrollTop = 1e7;
    o.dupa = {corp: r(_corp), rez: r(document.querySelector('#rez')), th: cuTabel ? r(document.querySelector('thead th')) : null};
    gata(o);
  }; });
}"""


def test_fereastra_cu_tabelul_balantei_ia_ecranul_si_nu_deruleaza_lateral(pagina):
    o = pagina.evaluate(_FEREASTRA_JS, [_cod_lateste(), 80, 12, "1.234.567,89", True])
    # „ferestrele cu tabele se deschid aproape pe tot ecranul”: 1366 - 2×24 = 1318, 768 - 2×24 = 720
    assert (o["lat"], o["inalt"]) == (1318, 720), o
    # „niciodată lateral”: tabelul de 14 coloane cu sume de 7 cifre încape, strâns în trepte (măsurat: 1.654 px fără ele)
    # (clasele ferestrei, exact: lățită + ambele trepte de strângere — măsurat în Chromium, 1366×768)
    assert o["clase"] == ["fer-rupt", "fer-strans", "fer-tabel", "fereastra"] and o["sw"] <= o["cw"] + 1 and o["laterale"] == [], o
    # „acțiunea principală fix jos”: butonul și mesajul lui, în fereastră, fără derulare
    assert o["corp"]["sus"] < o["buton"]["sus"] and o["mesaj"]["jos"] <= o["corp"]["jos"] + 1, o
    # „rezumatul stă fix sus”: după derularea tabelului la capăt, rezumatul e lipit de marginea de sus a corpului, iar antetul tabelului
    # stă imediat sub el
    assert o["dupa"]["rez"]["sus"] == o["dupa"]["corp"]["sus"] and abs(o["dupa"]["th"]["sus"] - o["dupa"]["rez"]["jos"]) <= 1, o


def test_un_tabel_care_incape_nu_e_strans(pagina):
    o = pagina.evaluate(_FEREASTRA_JS, [_cod_lateste(), 3, 3, "100,00", True])
    # fereastra tot ia ecranul (are tabel), dar tabelul nu e strâns degeaba: cuvintele scurte rămân întregi (331)
    assert o["clase"] == ["fer-tabel", "fereastra"] and o["lat"] == 1318, o


def test_un_tabel_mediu_e_masurat_in_fereastra_lata_nu_in_timpul_latirii(pagina):
    o = pagina.evaluate(_FEREASTRA_JS, [_cod_lateste(), 20, 6, "1.234.567,89", True])
    # tabelul (~1.000 px) nu încape în fereastra îngustă (680), dar încape în cea lată (1.318): se lățește fără să fie strâns. O lățire
    # animată ar fi fost măsurată la jumătate și ar fi strâns tabelul degeaba (DS cap.9 v2.96, pct.4)
    assert o["clase"] == ["fer-tabel", "fereastra"] and o["sw"] <= o["cw"] + 1, o


def test_o_fereastra_fara_tabel_nu_se_lateste(pagina):
    o = pagina.evaluate(_FEREASTRA_JS, [_cod_lateste(), 0, 0, "", False])
    assert o["clase"] == ["fereastra"] and o["lat"] == 680, o   # numai ferestrele CU tabel (comanda 10.1 pct.5)
