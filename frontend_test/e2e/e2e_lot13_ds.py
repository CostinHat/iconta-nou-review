# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), zona DS — mecanismele globale și regulile Design System probate în browser, pe firme NOI (`firma_e2e`,
`firma_noua`), pe aplicația din index și pe baza de TEST.

  * 655 (grupa 1) — sumele scrise în format românesc („1.000”, „1.500”, „1.000,50”) se citesc corect: Casă (instanța F7: „1.500” citit
    1,50 lei) și D207 (instanța: „1.000” înregistrat „bază 1,00 lei”); un text care nu e număr nu pleacă la server.

Temei: N/A — reguli de interfață (DS cap.6 „Numerele scrise de om”)."""
import datetime as _dt

import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, sql
from e2e_bloc_a import _card

_F = ".fereastra:last-of-type "
MESAJ_NUMAR_RO = "Scrie numărul ca în contabilitate: 1.234,56 (punct la mii, virgulă la zecimale)."


def _casa_dispozitie_noua(patron, firma):
    pg = patron.pg
    patron.firma(firma["nume"])
    pg.click("#fa-casa")
    pg.wait_for_selector(_F + "#c-toggle", timeout=20000)
    pg.click(_F + "#c-toggle")
    pg.wait_for_selector(_F + "#c-suma", timeout=10000)
    return pg


def test_def_655_suma_cu_punct_de_mii_in_casa(patron, firma_e2e):
    """655. Pașii contabilului (instanța F7, dispoziție nouă): Casă -> „+ Dispoziție nouă” -> Tip „Ridicare de la bancă” -> Suma „1.500”
    (cum scrie un contabil o mie cinci sute) -> „Adaugă”: în registru apare 1.500,00 lei, iar în bază operațiunea are 1500.00.
    Înainte: câmpul `type="number"` citea „1.500” ca 1,5 -> „1,50 lei”."""
    pg = _casa_dispozitie_noua(patron, firma_e2e)
    pg.select_option(_F + "#c-cat", "ridicare_banca")
    pg.fill(_F + "#c-suma", "1.500")
    pg.fill(_F + "#c-doc", "RB 655")
    # ce citește ECRANUL (lumea paginii, unde stă mecanismul din api.js): o mie cinci sute; `input_value` al Playwright citește din lumea
    # lui izolată textul scris de om („1.500”), care rămâne cum l-a scris
    assert pg.eval_on_selector(_F + "#c-suma", "e => e.value") == "1500"
    assert pg.input_value(_F + "#c-suma") == "1.500"
    assert pg.evaluate("() => document.querySelector('.fereastra:last-of-type #c-suma').getAttribute('inputmode')") == "decimal"
    patron.captura("casa_inainte_de_adauga")
    pg.click(_F + "#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('RB 655')", timeout=20000)
    patron.captura("casa_registru")
    txt = patron.fereastra()
    assert "1.500,00" in txt and "1,50 lei" not in txt, txt[:600]
    st = sql('SELECT suma::text FROM "%s".casa_operatiuni WHERE document = %%s' % firma_e2e["schema"], ("RB 655",))
    assert st == [("1500.00",)], st


def test_def_655_textul_care_nu_e_numar_nu_se_salveaza(patron, firma_e2e):
    """655. Pașii: Casă -> „+ Dispoziție nouă” -> Ridicare de la bancă -> Suma „1.5o0” (o literă în loc de cifră) -> „Adaugă”: lângă câmp
    „Scrie numărul ca în contabilitate: 1.234,56 …”, caseta „NU s-a salvat.” lângă buton, nicio operațiune scrisă. Înainte: textul
    greșit devenea o sumă ghicită sau goală."""
    pg = _casa_dispozitie_noua(patron, firma_e2e)
    pg.select_option(_F + "#c-cat", "ridicare_banca")
    pg.fill(_F + "#c-suma", "1.5o0")
    pg.fill(_F + "#c-doc", "RB 655 rau")
    pg.click(_F + "#c-adauga")
    pg.wait_for_selector(_F + '.msg-eroare[data-camp="c-suma"]', timeout=10000)
    patron.captura("casa_refuz_format")
    assert pg.inner_text(_F + '.msg-eroare[data-camp="c-suma"]').strip() == MESAJ_NUMAR_RO, pg.inner_text(_F + '.msg-eroare[data-camp="c-suma"]')
    assert MESAJ_NUMAR_RO in patron.fereastra()
    assert pg.locator(_F + ".refuz-salvare").count() == 1
    assert sql('SELECT count(*) FROM "%s".casa_operatiuni WHERE document = %%s' % firma_e2e["schema"], ("RB 655 rau",)) == [(0,)]


@pytest.fixture()
def firma_d207():
    for f in firma_noua():
        yield f


def test_def_655_baza_d207_cu_punct_de_mii(patron, firma_d207):
    """655. Pașii contabilului (instanța D207): firma -> Declarații -> D207 -> anul -> „Continuă →” -> „Adaugă beneficiar nerezident”: tip
    07 (servicii prestate de nerezidenți), denumire, stat DE, cod fiscal străinătate, act „Codul fiscal”, Bază „1.000” -> „+ adaugă”:
    rândul beneficiarului spune „bază 1.000,00 lei”. Înainte: „bază 1,00 lei”."""
    pg = patron.pg
    patron.firma(firma_d207["nume"])
    _card(patron, "declaratii", "#dec-tip")
    alege_tipul(pg, "d207", zona=_F)
    alege_perioada(pg, _dt.date.today().year - 1, zona=_F)
    pg.click(_F + "#dec-continua")
    pg.wait_for_selector(_F + "#d207-add", timeout=120000)
    pg.select_option(_F + "#d207-tip", "07")
    pg.fill(_F + "#d207-den", "Beneficiar Proba 655 GmbH")
    if pg.locator(_F + "input#d207-stat").count():
        pg.fill(_F + "#d207-stat", "DE")
    else:   # lista de țări (653): aceeași alegere
        pg.select_option(_F + "#d207-stat", "DE")
    pg.fill(_F + "#d207-cifs", "DE655000001")
    pg.select_option(_F + "#d207-act", "1")
    pg.fill(_F + "#d207-baza", "1.000")
    pg.fill(_F + "#d207-imp", "160")
    pg.click(_F + "#d207-add")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Beneficiar Proba 655 GmbH')",
                         timeout=20000)
    patron.captura("d207_beneficiar")
    txt = patron.fereastra()
    assert "bază 1.000,00 lei" in txt and "bază 1,00 lei" not in txt, txt[:800]


# ── 676 — listele scurte sunt butoane alăturate (Da/Nu din „Salariat nou”, `selectDaNu`) ─────────────────────────────────────────────
def test_def_676_da_nu_din_salariat_nou_sunt_butoane_alaturate(patron, firma_e2e):
    """676. Pașii: firma -> Salariați -> „+ Salariat nou”: „Funcția de bază la acest angajator” arată două butoane alăturate, „Da” și
    „Nu”, niciunul ales; apăsat „Da”, butonul e marcat (`aria-checked`), iar valoarea formularului e „true”. Înainte: o listă derulantă
    cu „— alege —”. MUTAȚIE (`mut_lot13_ds.json`): `data-butoane` scos din `selectDaNu` -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "salariati", _F + "#sp-salariat-nou")
    pg.click(_F + "#sp-salariat-nou")
    pg.wait_for_selector(_F + "#sn-functie_baza", state="attached", timeout=20000)
    grup = _F + ".alegere-butoane:has(+ #sn-functie_baza)"
    pg.wait_for_selector(grup, timeout=10000)
    butoane = pg.eval_on_selector_all(grup + " button", "bs => bs.map((b) => [b.innerText.trim(), b.getAttribute('aria-checked')])")
    assert butoane == [["Da", "false"], ["Nu", "false"]], butoane
    patron.captura("salariat_nou_da_nu")
    pg.click(grup + " button >> text=Da")
    assert pg.eval_on_selector(_F + "#sn-functie_baza", "s => s.value") == "true"
    assert pg.get_attribute(grup + " button >> text=Da", "aria-checked") == "true"


# ── 673 / 509 — fereastra deschisă din fereastra firmei e fereastra de lucru cât ecranul (Marjă agenții de turism) ─────────────────────
def test_def_673_509_operatiunea_se_deschide_in_fereastra_de_lucru_cat_ecranul(patron, firma_e2e):
    """673 / 509. Pașii (instanța lui Costin): firma -> „Operațiuni speciale” -> „Marjă agenții de turism”: fereastra e cât ecranul (minus
    marginea de 24 px), centrată, fără derulare laterală. Înainte: fereastră de 680 px care derula pe interior deși ecranul avea loc.
    MUTAȚIE: `fer-lucru` scos din navigator -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "operatiuni", _F + '[data-op="marja_turism"]')
    pg.click(_F + '[data-op="marja_turism"]')
    pg.wait_for_selector(_F + "#op-trimite", timeout=20000)
    pg.wait_for_timeout(300)
    r = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop(), b = f.getBoundingClientRect();
      const c = f.querySelector('.fereastra-corp');
      return { clase: f.className, lat: b.width, inalt: b.height, vw: innerWidth, vh: innerHeight, lateral: c.scrollWidth - c.clientWidth }; }""")
    patron.captura("marja_turism_fereastra_de_lucru")
    assert "fer-lucru" in r["clase"], r
    assert abs(r["lat"] - (r["vw"] - 48)) <= 2 and abs(r["inalt"] - (r["vh"] - 48)) <= 2, r
    assert r["lateral"] <= 1, r


# ── 575 — drumul din antet se încheie cu fereastra de acum ───────────────────────────────────────────────────────────────────────────
def test_def_575_antetul_adauga_firma_se_incheie_cu_adauga_firma(patron):
    """575 (afișare). Pașii: Firme -> „Firme existente” -> „+ Adaugă firmă”: antetul ferestrei arată „Firme › Firme existente › Adaugă
    firmă” — ultimul nod e fereastra de acum. Înainte: „Firme › Firme existente”, citit ca titlul ferestrei. MUTAȚIE: `fir-acum` scos
    din navigator -> ROȘU."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.wait_for_selector("#opt-existente", timeout=20000)
    pg.click("#opt-existente")
    pg.wait_for_selector("#firme-adauga", timeout=20000)
    pg.click("#firme-adauga")
    pg.wait_for_selector(_F + "#fn-cui", timeout=20000)
    patron.captura("adauga_firma_antet")
    assert pg.inner_text(_F + ".fereastra-fir .fir-acum").strip() == "Adaugă firmă"
    assert pg.inner_text(_F + ".fereastra-fir").replace("\n", " ").split("›")[-1].strip() == "Adaugă firmă"


# ── 625 / 654 — refuzul lângă câmp și în rezumat, o dată; refuzul vechi pleacă la acțiunea următoare (Casă) ────────────────────────────
def test_def_625_654_refuzul_casei_o_data_si_pleaca_dupa_reusita(patron, firma_e2e):
    """625. Pașii: Casă -> „+ Dispoziție nouă” -> „Adaugă” fără sumă și fără tip: „Suma trebuie să fie un număr mai mare ca 0.” stă de
    DOUĂ ori pe ecran — lângă câmp și în caseta „NU s-a salvat.” —, nu de trei ori. 654. Apoi tipul „Ridicare de la bancă”, suma „250”,
    „Adaugă”: caseta „NU s-a salvat.” și refuzurile de dinainte nu mai sunt pe ecran. MUTAȚIE: `refuzuriVechi(_butonScriere)` scos din
    api.js -> caseta veche rămâne -> ROȘU."""
    pg = _casa_dispozitie_noua(patron, firma_e2e)
    pg.click(_F + "#c-adauga")
    pg.wait_for_selector(_F + ".refuz-salvare", timeout=10000)
    t = "Suma trebuie să fie un număr mai mare ca 0."
    n = pg.evaluate("(t) => [...document.querySelectorAll('.fereastra')].pop().innerText.split(t).length - 1", t)
    patron.captura("casa_refuz_o_data")
    assert n == 2, n
    pg.select_option(_F + "#c-cat", "ridicare_banca")
    pg.fill(_F + "#c-suma", "250")
    pg.fill(_F + "#c-doc", "RB 654")
    pg.click(_F + "#c-adauga")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('RB 654')", timeout=20000)
    patron.captura("casa_dupa_reusita")
    assert pg.locator(_F + ".refuz-salvare").count() == 0
    assert t not in patron.fereastra()


# ── 681 — căutarea globală din antet ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_681_cautarea_gaseste_decontul_de_deplasare(patron, firma_e2e):
    """681 (proba lui Costin): firma în lucru -> în căsuța din antet „diurnă” -> primul rezultat „Decont deplasare / diurnă”, „Operațiuni
    speciale › Personal și deconturi” -> clic: se deschide formularul decontului (fereastra Operațiuni speciale, pasul „Decont deplasare
    / diurnă”). Fără căutare, decontul se găsea numai știind că e în Operațiuni → Personal și deconturi. MUTAȚIE: `puneCautarea` scos din
    navigator -> căsuța lipsește -> ROȘU."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.wait_for_selector("#cautare-globala", timeout=10000)
    pg.fill("#cautare-globala", "diurnă")
    pg.wait_for_selector("#cautare-rez .cautare-item", timeout=15000)
    primul = pg.inner_text("#cautare-rez .cautare-item >> nth=0")
    patron.captura("cautare_diurna")
    assert "Decont deplasare / diurnă" in primul and "Personal și deconturi" in primul, primul
    pg.click("#cautare-rez .cautare-item >> nth=0")
    pg.wait_for_selector(_F + "#op-trimite", timeout=30000)
    patron.captura("decont_deschis")
    assert "Decont deplasare / diurnă" in patron.fereastra()


def test_def_681_cautarea_d112_deschide_declaratiile_cu_d112_ales(patron, firma_e2e):
    """681. Pașii: firma în lucru -> „D112” în căsuța din antet -> rezultatul declarației -> clic: fereastra Declarații, cu D112 ales.
    Căsuța e deasupra ferestrelor: se poate scrie în ea și cu o fereastră deschisă."""
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    pg.fill("#cautare-globala", "D112")
    pg.wait_for_selector("#cautare-rez .cautare-item", timeout=15000)
    loc = pg.locator("#cautare-rez .cautare-item", has_text="D112 —")
    assert loc.count() >= 1, pg.inner_text("#cautare-rez")
    loc.first.click()
    pg.wait_for_selector(_F + "#dec-tip", timeout=30000)
    pg.wait_for_timeout(800)
    patron.captura("cautare_d112")
    assert pg.eval_on_selector(_F + "#dec-tip", "s => s.value") == "d112"
