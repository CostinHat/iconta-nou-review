# -*- coding: utf-8 -*-
"""Lotul 10, deficiențele 421 și 424 (aceeași clasă, toată aplicația) — rezumatul lipit sus al ferestrei cu tabel.

Comanda Costin 10.1 pct.5, verbatim în DECIZII: „Regula: ferestrele cu tabele se deschid aproape pe tot ecranul (cum e deja Balanța de
verificare); rezumatul stă fix sus și acțiunea principală fix jos; se derulează doar tabelul din mijloc, niciodată lateral.”

Temei: N/A — regulă de UI (DS cap.9 v2.97 pct.5: „Rezumatul e obligatoriu pe orice ecran care desenează un tabel de date în fereastră”).

Ce păzește (regula REALĂ `verificator_conformitate.analiza_fereastra_tabel`, scoasă cu `ast` — fixturile `regula` / `reale` din
`core/test_lot10_fereastra_tabel.py`):
  1. REZUMAT_TABEL_LIPSA pe fișierele de acum: niciun ecran cu tabel fără `.rezumat-fix` (în afara excepțiilor scrise, cu motiv).
  2. Mutațiile pe fișierele reale: rezumatul scos din Balanță / din cadrul comun al previzualizărilor / de peste tot (anti-vacuu: cel
     puțin cele 29 de ecrane cu rezumat pică), o excepție rămasă fără obiect pică și ea.
  3. Fragmente sintetice: tabelul direct, prin funcție-șablon, lista-tabel, zona desenată sub rezumatul ecranului, fereastra nouă deschisă
     de pe un rând, macheta, comentariile.
  4. Lista-tabel `.mig-sold-tabel` (Activitate cabinet) nu mai derulează ea însăși: regula pe stil.css + navigatorul și stil.css reale,
     în Chromium (corpul derulează, rezumatul și antetul listei rămân sus).
"""
import ast
import io
import os
import re

import pytest

from core.test_lot10_fereastra_tabel import _cod_lateste, pagina, regula, reale  # noqa: F401  (fixturi)

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_COD = "REZUMAT_TABEL_LIPSA"

# Ecranele care au acum rezumatul lipit sus (inventarul din lotul 10: 12 puse acum + 17 care îl aveau). Anti-vacuu: fără niciun
# `rezumat-fix`, regula trebuie să le prindă pe toate.
_CU_REZUMAT = {
    ("activitate_cabinet.js", "randeazaActivitateCabinet"), ("admin.js", "randeazaAdminInvitatii"), ("capacitate.js", "randeazaCapacitate"),
    ("clienti_ecran.js", "ecranClienti"), ("compensari_ecran.js", "ecranCompensari"), ("declaratii.js", "pas2"),
    ("facturi_ecran.js", "detaliiFactura"), ("firme.js", "ecranSalariati"), ("firme.js", "ecranFisaCont"), ("firme.js", "ecranJurnalMarja"),
    ("firme.js", "ecranRegistruFiscal"), ("firme.js", "ecranRegistruInventar"), ("firme.js", "ecranRegistre321"), ("firme.js", "ecranBilant"),
    ("firme.js", "ecranNir"), ("firme.js", "ecranBalanta"), ("firme.js", "ecranRapoarte"), ("migrare.js", "previzualizeazaSolduri"),
    ("migrare.js", "previzualizeazaParteneri"), ("migrare.js", "previzualizeazaSalariati"), ("migrare.js", "previzualizeazaAsociati"),
    ("migrare.js", "previzualizeazaMijloace"), ("migrare.js", "previzualizeazaIstoric"), ("migrare.js", "previzualizeazaRetete"),
    ("migrare.js", "previzualizeazaArticole"), ("migrare.js", "previzualizeazaRip"), ("mijloace_ecran.js", "ecranMijloace"),
    ("reevaluare_ecran.js", "ecranReevaluareValuta"), ("validat.js", "deschideNota"),
}


def _rez(rez):
    return [r for r in rez if r[2] == _COD]


def _prinse(rez):
    return {(r[0], re.search(r"„([^”]+)”", r[3]).group(1)) for r in _rez(rez)}


# ── 1. fișierele de acum ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_ecranele_reale_cu_tabel_au_rezumatul_lipit_sus(regula, reale):
    css, nav, fis = reale
    # comanda 10.1 pct.5: „rezumatul stă fix sus” — pe orice ecran care desenează un tabel în fereastră (DS cap.9 v2.97 pct.5)
    assert _rez(regula(css, nav, fis)) == []


def test_exceptiile_sunt_scrise_cu_motiv():
    """Lista excepțiilor e citită din verificator (literalul `rezumat_exceptii`): cine o lungește trebuie să scrie motivul, iar o excepție
    nouă schimbă testul acesta — nu trece tăcut."""
    src = io.open(os.path.join(_RAD, "verificator_conformitate.py"), encoding="utf-8").read()
    fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "analiza_fereastra_tabel"][0]
    lit = [n.value for n in ast.walk(fn) if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "rezumat_exceptii"]
    assert len(lit) == 1, "ANTI-VACUU: `rezumat_exceptii` nu mai e în regulă"
    exc = ast.literal_eval(lit[0])
    assert set(exc) == {("date_firma.js", "randeazaDateFirma"), ("operatiuni_ecran.js", "ecranOperatiuni"), ("tipare.js", "randeazaTipare"),
                        ("admin.js", "cereriNeconfirmate"), ("firme.js", "randeazaSituatiaStocului")}
    # DS cap.9 v2.97 pct.5: excepțiile sunt formularele (tabel mic în formular) și ecranele „de decis de Costin” (rezumatul ar cere o mutare)
    assert all(re.match(r"(formular|de decis de Costin): \S", m) and len(m) > 80 for m in exc.values()), exc


# ── 2. mutațiile pe fișierele reale ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_balanta_fara_rezumat_e_prinsa(regula, reale):
    css, nav, fis = reale
    ancora = '<div class="rezumat-fix">\n      <h2 class="pf-titlu">Balan\\u021b\\u0103 de verificare</h2>'
    assert fis["firme.js"].count(ancora) == 1, "ANTI-VACUU: ancora rezumatului Balanței lipsește din firme.js"
    rau = dict(fis, **{"firme.js": fis["firme.js"].replace(ancora, ancora.replace("rezumat-fix", "balanta-sus"))})
    assert _prinse(regula(css, nav, rau)) == {("firme.js", "ecranBalanta")}   # „rezumatul stă fix sus”, ca la Balanța de verificare


def test_cadrul_previzualizarilor_fara_rezumat_e_prins(regula, reale):
    css, nav, fis = reale
    ancora = 'return `<div class="rezumat-fix">${sus}</div>'
    assert fis["migrare.js"].count(ancora) == 1, "ANTI-VACUU: `_cadruPrev` nu mai e în migrare.js"
    rau = dict(fis, **{"migrare.js": fis["migrare.js"].replace(ancora, 'return `<div>${sus}</div>')})
    # rezumatul venea dintr-o funcție-șablon: toate cele nouă previzualizări îl pierd odată cu ea
    assert _prinse(regula(css, nav, rau)) == {k for k in _CU_REZUMAT if k[0] == "migrare.js"}


def test_fara_niciun_rezumat_toate_ecranele_cu_tabel_sunt_prinse(regula, reale):
    """Anti-vacuu: regula vede cel puțin cele 29 de ecrane cu tabel care au acum rezumat (unitatea, funcțiile-șablon, zonele)."""
    css, nav, fis = reale
    rau = {k: v.replace("rezumat-fix", "rezumat-scos") for k, v in fis.items()}
    assert rau != fis
    assert _prinse(regula(css, nav, rau)) >= _CU_REZUMAT


_FARA_REZUMAT = "„%s” desenează un tabel în fereastră fără rezumatul lipit sus (`.rezumat-fix`) — DS cap.9 v2.97 pct.5"


@pytest.mark.parametrize("fisier, ancora, inlocuire, asteptat", [
    ("tipare.js", '<h3 class="tip-titlu">Motive de respingere recurente</h3>',
     '<div class="rezumat-fix"><h3 class="tip-titlu">Motive de respingere recurente</h3></div>',
     ["excepția „randeazaTipare” nu mai are obiect: are acum rezumatul lipit sus"]),
    # redenumită, funcția iese din excepție: e prinsă ea (și zona ei, `_legaTvaIncasare`), iar excepția rămasă fără obiect e numită
    ("date_firma.js", "export async function randeazaDateFirma(", "export async function randeazaDateleFirmei(",
     [_FARA_REZUMAT % "_legaTvaIncasare", _FARA_REZUMAT % "randeazaDateleFirmei",
      "excepția „randeazaDateFirma” nu mai are obiect: funcția nu mai desenează un tabel în fereastră"]),
])
def test_exceptia_fara_obiect_e_prinsa(regula, reale, fisier, ancora, inlocuire, asteptat):
    css, nav, fis = reale
    assert fis[fisier].count(ancora) == 1, "ANTI-VACUU: ancora %r lipsește din %s" % (ancora, fisier)
    rez = _rez(regula(css, nav, dict(fis, **{fisier: fis[fisier].replace(ancora, inlocuire)})))
    # lista excepțiilor nu putrezește: abaterile, exact, toate pe fișierul atins
    assert ({r[0] for r in rez}, sorted(r[3] for r in rez)) == ({fisier}, sorted(asteptat)), rez


# ── 3. fragmente sintetice ──────────────────────────────────────────────────────────────────────────────────────────────────────────
_RAU = '''
async function ecranProba(corp, nav, t) {
  corp.innerHTML = `
    <h2 class="pf-titlu">Proba</h2>
    <p class="pf-intro" id="pr-luna">Luna 09.2026</p>
    <table class="fd-tabel"><tbody>${randuri}</tbody></table>`;
}
'''
_BUN = _RAU.replace('<p class="pf-intro" id="pr-luna">Luna 09.2026</p>', '<div class="rezumat-fix"><p class="pf-intro">Luna 09.2026</p></div>')


@pytest.mark.parametrize("nume, sursa, asteptat", [
    ("tabel fără rezumat", _RAU, ["ecranProba"]),
    ("tabel cu rezumat", _BUN, []),
    ("rezumatul ca a doua clasă", _RAU.replace('class="pf-intro" id="pr-luna"', 'class="pf-intro rezumat-fix"'), []),
    ("rezumatul numai într-un comentariu", "// <div class=\"rezumat-fix\">\n" + _RAU, ["ecranProba"]),
    ("tabelul numai într-un comentariu", _RAU.replace('<table class="fd-tabel"><tbody>${randuri}</tbody></table>', "")
     + "// odinioară: `<table class=\"fd-tabel\">`\n", []),
    ("tabel de machetă", _RAU.replace('class="fd-tabel"', 'class="mfp-tabel"'), []),
    ("lista-tabel", _RAU.replace('<table class="fd-tabel"><tbody>${randuri}</tbody></table>',
                                 '<div class="mig-sold-tabel">${randuri}</div>'), ["ecranProba"]),
    ("tabelul dintr-o funcție-șablon", '''
function _tabel(r) { return `<table class="fd-tabel"><tbody>${r}</tbody></table>`; }
async function ecranProba(corp) { corp.innerHTML = `<h2>Proba</h2>${_tabel(x)}`; }
''', ["ecranProba"]),
    ("rezumatul dintr-o funcție-șablon", '''
function _cadru(sus, tabel) { return `<div class="rezumat-fix">${sus}</div>${tabel}`; }
async function ecranProba(corp) { corp.innerHTML = _cadru(`<p>Luna</p>`, `<table class="fd-tabel"></table>`); }
''', []),
    ("zona desenată sub rezumatul ecranului", '''
async function ecranProba(corp) {
  corp.innerHTML = `<div class="rezumat-fix"><p>Anul</p></div><div id="z"></div>`;
  deseneazaZona(corp.querySelector("#z"));
}
function deseneazaZona(z) { z.innerHTML = `<table class="fd-tabel"></table>`; }
''', []),
    ("fereastra nouă deschisă de pe un rând nu e acoperită de rezumatul ecranului", '''
async function ecranProba(corp, nav) {
  corp.innerHTML = `<div class="rezumat-fix"><p>Anul</p></div><button id="d">Deschide</button>`;
  corp.querySelector("#d").addEventListener("click", () => nav.mergi("Detaliu", (c2) => ecranDetaliu(c2)));
}
async function ecranDetaliu(corp) { corp.innerHTML = `<table class="fd-tabel"></table>`; }
''', ["ecranDetaliu"]),
    ("o funcție-șablon singură nu e ecran", "function _tabel() { return `<table class=\"fd-tabel\"></table>`; }\n", []),
])
def test_regula_pe_fragmente(regula, reale, nume, sursa, asteptat):
    css, nav, _fis = reale
    # comanda 10.1 pct.5: „rezumatul stă fix sus” — prins acolo unde lipsește, tăcut unde e (sau unde tabelul nu e de date)
    assert sorted(n for _f, n in _prinse(regula(css, nav, {"proba.js": sursa}))) == asteptat, nume


# ── 4. lista-tabel fără derulare proprie ─────────────────────────────────────────────────────────────────────────────────────────────
def test_lista_tabel_care_deruleaza_iar_singura_e_prinsa(regula, reale):
    css, nav, _fis = reale
    ancora = ".fereastra.fer-tabel .fereastra-corp .mig-sold-tabel { max-height: none; overflow: clip; flex: 0 0 auto; }"
    assert css.count(ancora) == 1, "ANTI-VACUU: regula listei-tabel lipsește din stil.css"
    assert regula(css, nav, {}) == []                      # stil.css + navigatorul de acum: nicio abatere
    rez = regula(css.replace(ancora, ""), nav, {})
    # DS cap.9 v2.97 pct.3: „un singur element derulează: corpul ferestrei” — cutia de 280 px a listei ar fi al doilea
    assert [(r[0], r[2], r[3]) for r in rez] == [
        ("stil.css", "FEREASTRA_TABEL", "lista-tabel `.mig-sold-tabel` derulează iar ea însăși în fereastra cu tabel (DS cap.9 v2.97)")]


_LISTA_JS = """([cod, randuri]) => {
  document.head.innerHTML = '<link rel="stylesheet" href="/static/stil.css">';
  return new Promise((gata) => { document.head.querySelector('link').onload = () => {
    const rand = (i) => `<div class="mig-sold-rand ac-rand"><span class="ac-cand">21.10.2026 10:${String(i % 60).padStart(2, '0')}</span>
      <span class="ac-cine">Ana Pop</span><span class="ac-act">aprobată</span><span class="ac-decl">D300 · 09.2026</span><span class="ac-firma">Firma ${i}</span></div>`;
    document.body.innerHTML = `<div class="fereastra-overlay"><div class="fereastra"><div class="fereastra-antet"><span>Activitate cabinet</span></div>
      <div class="fereastra-corp" tabindex="0">
      <div class="rezumat-fix" id="rez"><div class="ac-perbar"><button class="ac-per ac-per-on">Luna</button></div>
        <div class="mig-intro">Jurnal cronologic — ${randuri} evenimente</div></div>
      <div class="mig-sold-tabel ac-tabel" id="lista"><div class="mig-sold-rand ac-cap" id="cap"><span class="ac-cand">Când</span>
        <span class="ac-cine">Cine</span><span class="ac-act">Acțiune</span><span class="ac-decl">Declarație</span><span class="ac-firma">Firmă</span></div>
        ${Array.from({length: randuri}, (_, i) => rand(i)).join('')}</div>
      </div></div></div>`;
    const fer = document.querySelector('.fereastra'), _corp = fer.querySelector('.fereastra-corp');
    void fer.offsetWidth;
    new Function('_corp', 'fer', cod + '\\n_lateste();')(_corp, fer);
    const lista = document.querySelector('#lista');
    const r = (e) => Math.round(e.getBoundingClientRect().top), j = (e) => Math.round(e.getBoundingClientRect().bottom);
    const o = {clase: [...fer.classList].sort(), listaOverflow: getComputedStyle(lista).overflowY, listaSh: lista.scrollHeight, listaCh: lista.clientHeight,
               corpSh: _corp.scrollHeight, corpCh: _corp.clientHeight};
    _corp.scrollTop = 1e7;
    o.dupa = {corp: r(_corp), rez: r(document.querySelector('#rez')), rezJos: j(document.querySelector('#rez')), cap: r(document.querySelector('#cap'))};
    gata(o);
  }; });
}"""


def test_jurnalul_activitatii_se_deruleaza_in_corp_cu_rezumatul_si_antetul_sus(pagina):
    o = pagina.evaluate(_LISTA_JS, [_cod_lateste(), 120])
    # comanda 10.1 pct.5: „se derulează doar tabelul din mijloc” — prin corp: lista nu mai e cutie cu derulare proprie (avea 280 px)
    assert o["clase"] == ["fer-tabel", "fereastra"] and o["listaOverflow"] not in ("auto", "scroll") and o["listaSh"] <= o["listaCh"] + 1, o
    assert o["corpSh"] > o["corpCh"] + 1000, o
    # „rezumatul stă fix sus”: după derularea la capăt, perioada și numărul evenimentelor sunt lipite sus, iar antetul listei sub ele
    assert o["dupa"]["rez"] == o["dupa"]["corp"] and abs(o["dupa"]["cap"] - o["dupa"]["rezJos"]) <= 1, o


# ── 5. ACTIUNE_TABEL_NEFIXATA lărgită la ZONELE ferestrei cu tabel (DS cap.9 v2.97 pct.6) ──────────────────────────────────────────────
_ACT = "ACTIUNE_TABEL_NEFIXATA"


def _actiuni(rez):
    return sorted(re.search(r"„([^”]+)”", r[3]).group(1) for r in rez if r[2] == _ACT)


_ZONA_RAU = '''
async function ecranProba(corp, nav, t) {
  corp.innerHTML = `<div class="rezumat-fix"><p>Anul</p></div><div id="z"></div>`;
  const zona = corp.querySelector("#z");
  const lista = !d.x.length ? `<div class="stare-goala">Nimic.</div>` : `<div><table class="fd-tabel"><tbody></tbody></table></div>`;
  zona.innerHTML = `<h3>Ajustări</h3>${lista}
      <div id="pr-mesaj"></div>
      <div style="margin-top:12px"><button class="buton-primar" id="pr-adauga" data-actiune="POST /tenants/{tenant_id}/proba">Adaugă</button></div>`;
}
'''


@pytest.mark.parametrize("nume, sursa, asteptat", [
    ("zona: acțiunea sub tabel", _ZONA_RAU, ["pr-adauga"]),
    ("zona: acțiunea în bara fixă", _ZONA_RAU.replace('<div style="margin-top:12px"><button', '<div class="bara-fixa"><button'), []),
    ("zona: acțiunea DEASUPRA tabelului (o cere rezumatul, nu bara)", _ZONA_RAU.replace("<h3>Ajustări</h3>${lista}", "<h3>Ajustări</h3>")
     .replace("Adaugă</button></div>`;", "Adaugă</button></div>${lista}`;"), []),
    ("zona: șablonul după un text (`info + …`)", _ZONA_RAU.replace("zona.innerHTML = `<h3>", "zona.innerHTML = info + `<h3>"), ["pr-adauga"]),
    ("zona: tabelul dintr-un arrow dat ca referință", '''
async function ecranProba(corp) {
  const sectiune = (s) => {
    const ordine = s.randuri;
    return `<table class="fd-tabel"><tbody>${ordine}</tbody></table>`;
  };
  zonaPrec.innerHTML = `${p.de_completat.map(sectiune).join("")}
    <button class="buton-secundar" id="pr-salveaza" data-actiune="POST /x">Salvează</button><div id="pr-mesaj"></div>`;
}
''', ["pr-salveaza"]),
    ("formularul adăugat după tabel (`corpHtml += formular(d)`)", '''
async function ecranProba(corp) {
  const formular = (d) => `<h3>Înscrie</h3><div><button class="buton-primar" id="pr-inscrie" data-actiune="POST /x">Înscrie</button></div>`;
  let corpHtml = `<div><table class="fd-tabel"></table></div>`;
  corpHtml += formular(d);
  corp.innerHTML = `<div class="rezumat-fix"><p>Anul</p></div>${corpHtml}`;
}
''', ["pr-inscrie"]),
    ("panou fără tabel în fereastra cu tabel (formularul unui rând: salariu, IBAN)", _ZONA_RAU.replace("${lista}", "<p>Salariul de bază</p>"), []),
    ("acțiunea de pe rândul tabelului din zonă", _ZONA_RAU.replace('<tbody></tbody>',
     '<tbody><tr><td><button class="buton-sters" data-actiune="DELETE /x/{id}">Șterge</button></td></tr></tbody>'), ["pr-adauga"]),
])
def test_actiunea_din_zona_ferestrei_cu_tabel(regula, reale, nume, sursa, asteptat):
    css, nav, _fis = reale
    # DS cap.9 v2.97 pct.6 / comanda 10.1 pct.5: „acțiunea principală fix jos” — și când tabelul și butonul stau într-o zonă a ferestrei
    assert _actiuni(regula(css, nav, {"proba.js": sursa})) == asteptat, nume


@pytest.mark.parametrize("ancora, butonul", [
    ('<div class="bara-fixa" style="margin-top:12px"><button class="buton-primar" id="aj-adauga"', "aj-adauga"),
    ('<div class="bara-fixa" style="margin-top:12px"><button class="buton-primar" id="rf-adauga"', "rf-adauga"),
    ('<div class="bara-fixa"><button class="buton-secundar" id="bl-prec-salveaza"', "bl-prec-salveaza"),
])
def test_bara_scoasa_de_pe_actiunile_din_zone_e_prinsa(regula, reale, ancora, butonul):
    css, nav, fis = reale
    assert fis["firme.js"].count(ancora) == 1, "ANTI-VACUU: ancora %r lipsește din firme.js" % ancora
    rau = dict(fis, **{"firme.js": fis["firme.js"].replace(ancora, ancora.replace(' class="bara-fixa"', ""))})
    assert _actiuni(regula(css, nav, rau)) == [butonul]   # „acțiunea principală fix jos”, nu la capătul conținutului


def test_fara_nicio_bara_actiunile_de_sub_tabele_sunt_prinse(regula, reale):
    """Anti-vacuu: fără nicio `.bara-fixa` în firme.js, regula vede acțiunile de sub tabele — din corp și din zone."""
    css, nav, fis = reale
    rau = dict(fis, **{"firme.js": fis["firme.js"].replace("bara-fixa", "bara-scoasa")})
    assert set(_actiuni(regula(css, nav, rau))) >= {"ri-adauga", "r3-adauga", "sp-contare-scrie", "aj-adauga", "rf-adauga", "bl-prec-salveaza"}


def test_exceptia_actiunii_fara_obiect_e_prinsa(regula, reale):
    css, nav, fis = reale
    ancora = '<button class="buton-primar" id="el-adauga"'
    assert fis["firme.js"].count(ancora) == 1, "ANTI-VACUU: „Adaugă” din panoul elementelor de salariu lipsește"
    rau = dict(fis, **{"firme.js": fis["firme.js"].replace(ancora, '<button class="buton-primar" id="el-adauga-nou"')})
    rez = [r for r in regula(css, nav, rau) if r[2] == _ACT]
    # lista excepțiilor nu putrezește: „el-adauga” nu mai e văzut, iar butonul redenumit e prins
    assert [r[3] for r in rez] == ["„el-adauga-nou” la capătul conținutului: în .bara-fixa (jos) sau .rezumat-fix (sus) — DS cap.9 v2.96",
                                   "excepția „el-adauga” nu mai are obiect: butonul nu mai e la capătul unui tabel"], rez
