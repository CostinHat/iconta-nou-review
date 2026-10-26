# -*- coding: utf-8 -*-
"""Retestul Costin 12.10.2026 (verbatim în DECIZII): 224 și 225 redeschise, 226–232 — probate în browser, pe firme noi ale rulării și pe
firmele de test ale cabinetului. Pașii contabilului sunt în docstringul fiecărui test; captura fiecăruia rămâne în directorul plasei."""
import datetime as _dt
import re

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import T_COMERT, cont_asistent, ecran_cont
from e2e_bloc_d import PATRON, _api, _cnp, _control_firma, _date_firma, _deschide, _grupuri_control, _nota_validata
from e2e_comanda_1010 import _alege_bilant, _lista_control, _rezumate_la_zi, _solduri, _valideaza_bilant

STARI = {"rosu": "restanță", "galben": "de urmărit", "verde": "la zi", "gri": "nu se poate verifica"}

#: pagina principală, măsurată pe arborele de randare: structura, benzile, grila, cardul Control fiscal
_PAGINA = """() => {
  const salut = document.querySelector('.cab-salut'), grila = document.querySelector('.cab-grila');
  const r = (e) => e.getBoundingClientRect();
  const control = grila.querySelector('[data-cheie="control"]');
  const carduri = [...grila.querySelectorAll(':scope > .cab-card')].map((c) => Math.round(r(c).height));
  return {structura: [...salut.parentElement.children].map((e) => e.className),
          meniu_lateral: document.querySelectorAll('.asi-arbore, .asi-nod, .cab-salut ~ nav').length,
          benzi: [...salut.querySelectorAll('.cab-banda')].map((b) => ({titlu: b.innerText.trim(), top: Math.round(r(b).top),
                                                                         bottom: Math.round(r(b).bottom), h: Math.round(r(b).height)})),
          grila_top: Math.round(r(grila).top), carduri,
          titluri: [...grila.querySelectorAll('.cab-card-titlu')].map((t) => t.innerText.trim()),
          control: {h: Math.round(r(control.closest('.cab-card')).height), text: control.innerText.replace(/\\s+/g, ' ').trim(),
                    lumini: [...control.querySelectorAll('.cab-stare')].map((s) => s.dataset.stare),
                    numere: [...control.querySelectorAll('.cab-stare .tip-figura')].map((b) => parseInt(b.innerText, 10)),
                    randuri: new Set([...control.querySelectorAll('.cab-stare')].map((s) => Math.round(r(s).top))).size}};
}"""


def _pagina(ecran):
    ecran.acasa()
    ecran.pg.wait_for_function("() => document.querySelector('[data-cheie=\"control\"] .cab-semafor4')", timeout=120000)
    return ecran.pg.evaluate(_PAGINA)


# ── 224 · 225 · 231 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_224_cardul_control_fiscal_semafor_cu_patru_lumini(browser, request, patron):
    """224 (REDESCHISĂ 12.10.2026). „cardul Control fiscal are încă listă cu text. Cardul arată doar un rând cu 4 buline colorate și
    numărul fiecăreia, fără text, iar înălțimea lui e la fel cu a celorlalte carduri. Textul rămâne numai în fereastră.”
    Pașii contabilului: contabilul-șef -> pagina principală: cardul Control fiscal = un rând, roșu · galben · verde · gri, fiecare cu un
    număr (și 0), fără nume de stare; cardul are înălțimea celorlalte; numerele = rândurile listei Control fiscal pe culori; fereastra
    are luminile cu numele stării -> asistentul: același rând, cu firma lui.
    MUTAȚIA din plasă: cardul întors pe semaforul ferestrei (listă cu text) -> ROȘU."""
    _rezumate_la_zi()
    m = _pagina(patron)
    patron.captura("card_cabinet")
    c = m["control"]
    assert c["lumini"] == ["rosu", "galben", "verde", "gri"] and c["randuri"] == 1, c
    assert re.fullmatch(r"\d+( \d+){3}", c["text"]), c["text"]                     # numai numerele
    # înălțimea NATURALĂ (fără întinderea pe rândul grilei): un vecin pe două rânduri de text (ex. „De depus” cu declarații depășite)
    # face rândul mai înalt, dar nu e cardul Control fiscal; o listă cu text în cardul Control fiscal îl face pe el mai înalt
    nat = patron.pg.evaluate("""() => { const g = document.querySelector('.cab-grila');
      const cs = [...g.querySelectorAll(':scope > .cab-card')]; cs.forEach((x) => { x.style.alignSelf = 'start'; });
      const hs = cs.map((x) => Math.round(x.getBoundingClientRect().height));
      const ctl = Math.round(g.querySelector('[data-cheie="control"]').closest('.cab-card').getBoundingClientRect().height);
      cs.forEach((x) => { x.style.alignSelf = ''; }); return {ctl, hs}; }""")
    # rândul de lumini e cu ~2 px mai înalt decât un rând de text; o listă adaugă cel puțin un rând (~27 px): pragul e sub o jumătate de rând
    assert abs(nat["ctl"] - sorted(nat["hs"])[len(nat["hs"]) // 2]) <= 12, nat
    randuri = _lista_control(patron)
    culoare = lambda r: ("rosu" if "#ff8a80" in r["dot"] else "galben" if "#f0cd7a" in r["dot"] else "verde" if "#6fc494" in r["dot"]   # noqa: E731
                         else "gri")
    assert dict(zip(c["lumini"], c["numere"])) == {s: sum(1 for r in randuri if culoare(r) == s) for s in STARI}, (c, randuri)
    fereastra = patron.pg.inner_text(".fereastra:last-of-type .cf-sumar")
    patron.captura("fereastra_cu_text")
    assert "de urmărit" in fereastra and "la zi" in fereastra, fereastra                # textul stărilor stă în fereastră
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        ma = _pagina(e)
        e.captura("card_asistent")
        ca = ma["control"]
        assert ca["lumini"] == ["rosu", "galben", "verde", "gri"] and ca["randuri"] == 1 and sum(ca["numere"]) == 1, ca
        assert re.fullmatch(r"\d+( \d+){3}", ca["text"]) and abs(ca["h"] - sorted(ma["carduri"])[len(ma["carduri"]) // 2]) <= 1, ca


def test_def_225_recomanda_si_suport_benzi_la_ambele_roluri(browser, request, patron):
    """225 (REDESCHISĂ 12.10.2026). „la B, cardul «Suport» lipsește. La Ana stă jos. «Recomandă» și «Suport» sunt două benzi înguste,
    una lângă alta, deasupra cardurilor, la ambele roluri, ca la Cabinet.”
    Pașii: contabilul-șef -> pagina principală: sus, lângă salut, două benzi pe același rând — „Recomandă”, „Suport” —, mai scunde decât
    un card, deasupra grilei; niciuna nu mai e card în grilă; „Suport” deschide fereastra „Suport” -> asistentul: la fel.
    MUTAȚIA din plasă: banda „Suport” scoasă din salut.js -> ROȘU."""
    for rol, e in (("cabinet", patron), ("asistent", None)):
        if e is None:
            with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as ea:
                _benzi(ea, rol)
        else:
            _benzi(e, rol)


def _benzi(e, rol):
    m = _pagina(e)
    b = m["benzi"]
    assert [x["titlu"] for x in b] == ["Recomandă", "Suport"], (rol, b)
    assert abs(b[0]["top"] - b[1]["top"]) <= 1 and max(x["bottom"] for x in b) <= m["grila_top"], (rol, b, m["grila_top"])
    assert max(x["h"] for x in b) < min(m["carduri"]), (rol, b, m["carduri"])
    assert "Suport" not in m["titluri"] and "Recomandă" not in m["titluri"], (rol, m["titluri"])
    e.captura("benzi_" + rol)
    e.pg.click("[data-banda='raport']")
    e.pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Suport')", timeout=30000)


def test_def_231_pagina_principala_aceeasi_structura_fara_meniu_lateral(browser, request, patron):
    """231. „la Ana, scoate meniul din stânga care repetă cardurile. Pagina principală are aceeași structură la ambele roluri.”
    Pașii: asistentul (Ana) -> pagina principală: banda de salut și grila de carduri, fără meniul din stânga; contabilul-șef: aceeași
    structură; Ana ajunge la firme din cardul „Firme”.
    MUTAȚIA din plasă: arborele readus în pagina asistentului -> ROȘU."""
    mp = _pagina(patron)
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        ma = _pagina(e)
        e.captura("asistent")
        # [319 + 320] zona cardurilor de început (`inceput`) stă între banda de salut și grilă, la ambele roluri (DS cap.12b)
        assert ma["structura"] == mp["structura"] and [x for x in mp["structura"] if x != "inceput"] == ["cab-salut", "cab-grila"], (
            ma["structura"], mp["structura"])
        assert ma["meniu_lateral"] == mp["meniu_lateral"] == 0, (ma["meniu_lateral"], mp["meniu_lateral"])
        e.pg.click("button.cab-card:has([data-cheie='firme'])")
        e.pg.wait_for_selector("#firme-lista button.firme-rand", timeout=20000)


# ── 226 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_226_eticheta_firmei_e_una_din_cele_patru_stari(patron, firma_e2e):
    """226. „în fereastra Control fiscal, eticheta din dreapta fiecărei firme e una din cele 4 stări (restanță, de urmărit, la zi, nu se
    poate verifica). Acum apar «neconcordanță» și «2 nu se pot verifica». Detaliul rămâne pe rândul de dedesubt.”
    Pașii: Control fiscal -> fiecare rând: eticheta = numele culorii lui, una din patru; pe rândul de dedesubt rămâne detaliul (numărul
    declarațiilor care nu se pot verifica, constatările) -> detaliul unei firme: antetul are tot numele stării.
    MUTAȚIA din plasă: eticheta gri cu numărul („2 nu se pot verifica”) -> ROȘU."""
    randuri = _lista_control(patron)
    patron.captura()
    culoare = lambda r: ("rosu" if "#ff8a80" in r["dot"] else "galben" if "#f0cd7a" in r["dot"] else "verde" if "#6fc494" in r["dot"]   # noqa: E731
                         else "gri")
    rele = [(r["nume"], r["eticheta"]) for r in randuri if r["eticheta"] != STARI[culoare(r)]]
    assert not rele, rele
    gri_cu_numar = [r for r in randuri if culoare(r) == "gri" and re.search(r"\d+ declarați", r["sub"])]
    assert gri_cu_numar, [(r["nume"], r["eticheta"], r["sub"]) for r in randuri]   # anti-vacuu: cazul „2 nu se pot verifica” e pe ecran
    patron.pg.locator(".fereastra:last-of-type #cf-lista .mig-frand", has_text=gri_cu_numar[0]["nume"]).first.click()
    patron.pg.wait_for_selector(".fereastra:last-of-type .mig-intro", timeout=60000)
    antet = patron.pg.inner_text(".fereastra:last-of-type .mig-intro")
    patron.captura("detaliu")
    assert antet.split("·")[-1].strip() == "nu se poate verifica", antet


# ── 232 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_preluata_08():
    """Firmă nouă cu un salariat din 01/2026 (D112 lunar) și luna preluării aleasă în Date firmă: 08/2026."""
    for f in firma_noua():
        st, r = _api(PATRON, "POST", "/tenants/%d/salariati" % f["tenant_id"],
                     {"nume": "Popescu", "prenume": "Ion", "cnp": _cnp("185010140123"), "data_angajare": "2026-01-05",
                      "tip_norma": "intreaga", "ore_zi": 8, "salariu_brut": 5000, "persoane_intretinere": 0,
                      "scutit_contrib_minim": False, "functie_baza": True, "cor": "331302"})
        assert st == 200, (st, r)
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"luna_preluare": "2026-08"})
        assert st == 200 and r.get("ok") is not False, (st, r)
        yield f


def test_def_232_inainte_de_preluare_si_restantele_spun_aceeasi_luna(patron, firma_preluata_08):
    """232. „F3, Control fiscal: «Înainte de preluare — 06/2026 (nu se numără la restanțe)», dar D390 și D301 pe 06/2026 apar ca restanțe.
    Stabilește din datele firmei care e luna preluării și fă cele două locuri consecvente.” Antetul arăta LUNA PRELUĂRII, iar dedesubt
    erau perioadele dinaintea ei; luna preluării se numără.
    Pașii: firma cu luna preluării 08/2026 (Date firmă) -> Control fiscal -> firma: grupul „Înainte de preluare în iConta.eu — până la
    07/2026”, cu D112 07/2026, iar explicația spune luna preluării (08/2026), de unde vine („aleasă în Date firmă”) și că 08/2026 se
    numără; D112 08/2026 (termen 25.09) e la „Restanțe”, nu înainte de preluare.
    MUTAȚIA din plasă: antetul înapoi pe luna preluării -> ROȘU."""
    _control_firma(patron, firma_preluata_08)
    g = _grupuri_control(patron)
    patron.pg.click(".fereastra:last-of-type .cf-inainte-btn")   # [lotul 13, 674] grupul se deschide în fereastra lui
    expl = patron.pg.inner_text(".fereastra:last-of-type .cf-inainte .cf-incr-temei")
    patron.captura()
    inainte = next((v for k, v in g.items() if k.startswith("Înainte de preluare în iConta.eu — până la 07/2026")), None)
    restante = [r for k, v in g.items() if k.startswith("Restanțe") for r in v]
    assert inainte and any(r.startswith("D112 07/2026") for r in inainte), g
    assert not [r for r in inainte if r.startswith("D112 08/2026")] and any(r.startswith("D112 08/2026") for r in restante), g
    assert "Luna preluării în iConta.eu e 08/2026 (aleasă în Date firmă)" in expl and "pe 08/2026 și după se numără" in expl, expl


# ── 227 · 228 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_f20_manual():
    """Firmă nouă cu soldurile de preluare la 31.12.2024 și un aport validat în 03/2025: bilanțul 2025 cere F20 „An precedent” manual."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _nota_validata(f, "2025-03-10", "5121", "1012", 2000, "Aport capital")
        yield f


def _bilant_2025(patron, f):
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)


def test_def_227_coloana_manuala_cu_denumirile_de_pe_formular(patron, firma_f20_manual):
    """227. „la completarea manuală a coloanei «An precedent» din bilanț, fiecare rând arată denumirea de pe formular, nu doar «rândul 41».”
    Pașii: firma cu soldurile de preluare la 31.12.2024 și un aport în 03/2025 -> Bilanț 2025, S1005: F20 se cere manual; fiecare rând
    are denumirea de pe formular („1.Cifra de afaceri netă” …, din structura ANAF) -> salvează -> „Validează”: rândurile depuse au și ele
    denumirea („IV. CASA ȘI CONTURI LA BĂNCI”).
    MUTAȚIA din plasă: denumirea scoasă din formular -> ROȘU."""
    pg = patron.pg
    _bilant_2025(patron, firma_f20_manual)
    den = pg.eval_on_selector_all(".fereastra:last-of-type .bl-prec-tabel[data-sectiune='F20'] tbody tr",
                                  "trs => trs.map(t => [...t.querySelectorAll('td')].slice(0, 2).map(td => td.innerText.trim()))")
    patron.captura("formular")
    # [234] denumirile curate, cu codul formularului; F20 micro: rd.01–07, 06a/06b („din care” energie / gaze), 07a, 08, 09
    assert den[0] == ["rândul 01", "1. Cifra de afaceri netă"] and den[3] == ["rândul 04", "4. Cheltuieli cu personalul"], den
    assert all(d for _r, d in den) and len(den) == 12, den
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, _rand = _valideaza_bilant(patron, 2025, alege=False)
    rand8 = pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri tbody tr",
                                    "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim())).filter(c => c[0] === 'F10' && c[1] === 'rândul 08')")
    patron.captura("randuri_depuse_cu_denumire")
    assert "Validare fără erori" in text and rand8 and rand8[0][2] == "IV. Casa și conturi la bănci", (text[:300], rand8)


def test_def_228_actiunile_inactive_pana_se_completeaza_coloana(patron, firma_f20_manual):
    """228. „în bilanț, «Validează» și «Trimite în coadă» sunt inactive până se completează coloana «An precedent», cu motivul afișat lângă
    ele.” (și „Descarcă XML”: serverul refuză și XML-ul cu coloana goală)
    Pașii: Bilanț 2025, S1005, F20 „An precedent” necompletată: „Validează”, „Descarcă XML”, „Trimite în coadă” inactive, iar lângă ele
    scrie de ce (F20) -> salvează coloana -> acțiunile se activează, motivul dispare.
    MUTAȚIA din plasă: legarea acțiunilor de coloană scoasă -> ROȘU."""
    pg = patron.pg
    _bilant_2025(patron, firma_f20_manual)
    actiuni = pg.eval_on_selector_all(".fereastra:last-of-type #bl-val, .fereastra:last-of-type #bl-xml, .fereastra:last-of-type #bl-coada",
                                      "bs => bs.map(b => b.disabled)")
    motiv = pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")
    patron.captura("actiuni_inactive")
    assert actiuni == [True, True, True] and "An precedent" in motiv and "(F20, F30)" in motiv, (actiuni, motiv)   # [C14] și F30 cap.XIX
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    actiuni = pg.eval_on_selector_all(".fereastra:last-of-type #bl-val, .fereastra:last-of-type #bl-xml, .fereastra:last-of-type #bl-coada",
                                      "bs => bs.map(b => b.disabled)")
    patron.captura("actiuni_active")
    assert actiuni == [False, False, False] and pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv").strip() == "", actiuni


# ── 229 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_infiintata_2025():
    for f in firma_noua():
        yield f


def test_def_229_primul_exercitiu_fara_an_precedent(patron, firma_infiintata_2025):
    """229. „dacă firma s-a înființat în anul bilanțului, coloana «An precedent» rămâne legal goală (primul exercițiu) și nu se cere
    completarea manuală. Ține cont de data înființării.” TEMEI: Legea 82/1991 art.27 alin.(8); OMFP 1802/2014 pct.130.
    Pașii: Date firmă: „Data înființării” 15.03.2025 (pe ruta ecranului; câmpul o arată) -> o notă în 03/2025 -> Bilanț 2025, S1005: „Primul exercițiu financiar:
    firma s-a înființat pe 15.03.2025 …”, fără formular de completat, acțiunile active -> „Validează”: fără erori, coloana „An precedent”
    zero pe toate rândurile -> Bilanț 2024: acțiunile inactive, „nu există: firma s-a înființat pe 15.03.2025”.
    MUTAȚIA din plasă: regula primului exercițiu scoasă -> se cere completarea -> ROȘU."""
    f = firma_infiintata_2025
    pg = patron.pg
    _date_firma(f)
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2025-03-15"})   # ruta ecranului
    assert st == 200 and r.get("ok") is not False, (st, r)
    patron.firma(f["nume"])
    pg.click("#fa-datefirma")
    pg.wait_for_selector(".fereastra:last-of-type #df-data_infiintare", timeout=20000)
    patron.captura("date_firma")
    assert pg.input_value(".fereastra:last-of-type #df-data_infiintare") == "2025-03-15"
    _nota_validata(f, "2025-03-20", "5121", "1012", 1000, "Aport capital D229")
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    zona = _alege_bilant(patron, 2025)
    patron.captura("primul_exercitiu")
    assert "Primul exercițiu financiar: firma s-a înființat pe 15.03.2025" in zona, zona
    assert pg.locator(".fereastra:last-of-type .bl-prec-tabel").count() == 0 and not pg.locator(".fereastra:last-of-type #bl-val").is_disabled()
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("validat")
    assert "Validare fără erori" in text and rand and all(p == "0,00" for p, _c in rand.values()), (text[:400], rand)
    pg.fill(".fereastra:last-of-type #bl-an", "2024")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    # [237] refuzul stă o dată; [lotul 11, 440] imediat sub rândul butoanelor, cu textul lui — nota de lângă ele nu trimite „mai jos”
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #bl-precedent') || {}).innerText.includes('nu există')",
                         timeout=60000)
    patron.captura("inainte_de_infiintare")
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled()
    assert "firma s-a înființat pe 15.03.2025" in pg.inner_text(".fereastra:last-of-type #bl-precedent")
    assert pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv") == "Inactive până se rezolvă refuzul:"
    assert pg.eval_on_selector(".fereastra:last-of-type #bl-precedent", "z => !!z.previousElementSibling && z.previousElementSibling.classList.contains('rezumat-fix')"), "refuzul nu stă imediat sub rândul butoanelor (440)"


# ── 230 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_230_firul_de_intrare_al_lui_ana_incepe_de_la_1(browser, request, patron):
    """230. „la Ana, în catalog, «Firul de intrare» începe de la pasul 2. Numerotează de la 1.”
    Pașii: Ana (asistent, „Poate pregăti”) -> „?” -> „Firul de intrare”: pașii numerotați 1, 2, 3 … (fără pasul „Firme”, al
    administratorului) -> contabilul-șef: tot de la 1, începând cu „Firme”.
    MUTAȚIA din plasă: numărul luat înapoi din STRATURI (`st.nr`) -> la Ana începe de la 2 -> ROȘU."""
    # [lotul 13, 562 — anexa comenzii 13.1, decizia 320] asistentul nu mai primește firul de intrare (pașii de preluare sunt ai
    # administratorului): în „?” are intro-ul pe rol și cardurile lui de început, deci niciun pas numerotat — nici „2” fără „1”
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        e.acasa()
        e.pg.click("#nav-ghid")
        e.pg.wait_for_selector(".fereastra #ans-inceput", timeout=20000)
        e.pg.wait_for_timeout(600)
        nr = e.pg.eval_on_selector_all(".fereastra .ans-pas-nr", "els => els.map(x => x.innerText.trim())")
        e.captura("ana")
        assert nr == [], nr
    patron.acasa()
    patron.pg.click("#nav-ghid")
    patron.pg.wait_for_selector(".fereastra .ans-pas-nr", timeout=20000)
    nr = patron.pg.eval_on_selector_all(".fereastra .ans-pas-nr", "els => els.map(x => x.innerText.trim())")
    titluri = patron.pg.eval_on_selector_all(".fereastra .ans-pas-titlu", "els => els.map(x => x.innerText.trim())")
    assert nr == [str(i) for i in range(1, len(nr) + 1)] and titluri[:1] == ["Firme"], (nr, titluri)


# ── C11 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c11_datele_informative_f30_in_tabelul_lor(patron, firma_infiintata_2025):
    """C11. Bilanț, „Ce se depune”: rândurile F30 (datele informative: unități cu profit / cu pierdere / fără) apăreau sub „An precedent” /
    „An curent”, fără denumire — coloanele F30 nu sunt anii, iar 1 („o unitate”) se citea „1,00 lei, anul precedent”. Găsită de plasa
    deficienței 229 (12.10.2026).
    Pașii: firma în primul exercițiu (2025), o notă -> Bilanț 2025, S1005 -> „Validează”: F10/F20 în „Ce se depune”, cu „An precedent” /
    „An curent”; F30 în „Date informative (F30)”, cu denumirea de pe formular și valorile așa cum se depun.
    MUTAȚIA din plasă: rândurile F30 înapoi în tabelul pe ani -> ROȘU."""
    f = firma_infiintata_2025
    pg = patron.pg
    _date_firma(f)
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2025-03-15"})
    assert st == 200 and r.get("ok") is not False, (st, r)
    _nota_validata(f, "2025-03-20", "5121", "1012", 1000, "Aport capital C11")
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    f30 = pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri-f30 tbody tr",
                                  "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim()))")
    patron.captura()
    assert "Validare fără erori" in text and {fm for fm, _r in rand} <= {"F10", "F20"}, (text[:300], sorted(rand))
    assert [x[:2] for x in f30] == [["rândul 01", "Unități care au înregistrat profit"], ["rândul 02", "Unități care au înregistrat pierdere"],
                                    ["rândul 03", "Unități care nu au înregistrat nici profit nici pierdere"]], f30
    assert f30[2][2:] == ["1", "0"], f30                                       # o unitate fără profit și fără pierdere: „1”, nu „1,00”


# ── C10 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_s1003():
    """Firmă nouă: soldurile de preluare la 31.12.2024, iar în 2025 vânzări 5.000 (704), o subvenție aferentă cifrei de afaceri 800 (7411)
    și reduceri comerciale acordate 300 (709)."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        # 7411 (analiticul OMFP 1802 al lui 741, „aferente cifrei de afaceri”) și 709 sunt în planul firmei de la lotul 9 (planul OMFP
        # 1802/2014 întreg în șablon, `core/plan_conturi_omfp.py`) — nu se mai adaugă de mână
        assert {r[0] for r in sql('SELECT simbol FROM "%s".plan_conturi WHERE simbol IN (%%s, %%s)' % f["schema"], ("7411", "709"))} \
            == {"7411", "709"}
        _nota_validata(f, "2025-03-10", "5121", "704", 5000, "Vanzare C10")
        _nota_validata(f, "2025-04-10", "5121", "7411", 800, "Subventie C10")
        _nota_validata(f, "2025-05-10", "709", "5121", 300, "Reducere C10")
        _inchide_6_7(f, "2025-12-31", {"704": 5000, "7411": 800, "709": -300})      # [C15] închiderea în 121 la 31.12
        yield f


def test_def_c10_s1003_contul_de_profit_si_pierdere_pe_randurile_formularului(patron, firma_s1003):
    """C10. Bilanțul S1003: F20 era scris pe o numerotare proprie de 38 de rânduri (subvențiile pe rd.04, unde formularul ANAF are
    „Reduceri comerciale acordate”), iar rândurile 39–70 lipseau; DUK îl declara totuși „valid”. Găsită la extragerea denumirilor
    pentru 227 (12.10.2026); rescriere comandată de Costin (12.10.2026).
    Pașii: firma cu vânzări 5.000, subvenție aferentă cifrei de afaceri 800 și reduceri acordate 300 în 2025 -> Bilanț 2025, S1003 ->
    completează F20 „An precedent” (2024 nu e în aplicație) -> „Validează”: fără erori; „Ce se depune” — rd.04 „Reduceri comerciale
    acordate” 300, rd.06 subvenția 800, rd.01 cifra de afaceri 5.500 (rd.02 + 03 − 04 + 06), fiecare cu denumirea de pe formular.
    Apoi un rulaj pe 741 sintetic -> „Validează” refuză cu analiticele cerute (decizia Costin 12.10.2026: „nu ghicim rândul”).
    MUTAȚIILE din plasă: 7411 înapoi pe rd.04 -> ROȘU; refuzul sinteticului scos -> ROȘU."""
    f = firma_s1003
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    pg.fill(".fereastra:last-of-type #bl-an", "2025")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-categorie'); return z && "
                         "!z.hasAttribute('aria-busy') && !z.innerText.includes('Se calculează'); }", timeout=90000)
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1003")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-precedent'); "
                         "return z && z.dataset.pentru === '2025|s1003' && z.innerText.trim(); }", timeout=60000)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    den = {(x[0], int(x[1].split("(")[-1].rstrip(")")) if "(" in x[1] else int(x[1].split()[-1])): x[2] for x in pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri tbody tr",
           "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim()))")}
    patron.captura()
    assert "Validare fără erori" in text, text[:400]
    assert (rand[("F20", 4)][1], rand[("F20", 6)][1], rand[("F20", 1)][1], rand[("F20", 2)][1]) == \
        ("300,00", "800,00", "5.500,00", "5.000,00"), sorted((k, v) for k, v in rand.items() if k[0] == "F20")
    assert den[("F20", 4)] == "Reduceri comerciale acordate" and den[("F20", 1)].startswith("1. Cifra de afaceri netă"), den
    # [decizia Costin 12.10.2026] „Pentru 741 și 658 folosite sintetic, fără analitic: nu ghicim rândul. Generarea S1003 se oprește, cu
    # motivul și contul analitic cerut.” Un rulaj pe 741 sintetic -> „Validează” refuză și numește analiticele cu rândul lor
    _nota_validata(f, "2025-06-10", "5121", "741", 100, "Subventie pe sintetic C10")
    _inchide_6_7(f, "2025-12-31", {"741": 100})
    text, _rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("sintetic_741_refuzat")
    assert "contul 741 e folosit sintetic" in text and "7411 (rd.06); 7412, 7413, 7414, 7415, 7416, 7417, 7419 (rd.12); 7418 (rd.49)" in text, \
        text[:600]


def _inchide_6_7(f, zi, solduri):
    """[C15] Nota de închidere a claselor 6 / 7 în 121 (OMFP 1802/2014, contul 121): {cont: soldul} — creditor (venit) > 0, debitor < 0."""
    for cont, s in solduri.items():
        if s > 0:
            _nota_validata(f, zi, cont, "121", s, "Inchidere %s" % cont)
        else:
            _nota_validata(f, zi, "121", cont, -s, "Inchidere %s" % cont)


def test_def_c16_s1003_unitatile_cu_profit_din_profitul_net(patron, firma_s1003):
    """C16 (găsită de Code, 12.10.2026). S1003 scria în datele informative F30 rd.01 / 02 („Unități care au înregistrat profit / pierdere”)
    rândurile 08 / 09 ale contului de profit și pierdere S1003 — care sunt variația stocurilor (sold D) și producția de imobilizări —, nu
    profitul / pierderea netă (rd.69 / 70). Pașii: firma cu vânzări 5.000, subvenție 800, reduceri 300 în 2025, închise în 121 -> Bilanț
    2025, S1003 -> „Validează” -> „Date informative (F30)”: rândul 01 = 1 unitate, 5.500 (profitul net, rd.69); rândul 02 = 0.
    MUTAȚIA din plasă: rezultatul S1003 înapoi din rd.08 / 09 -> rândul 01 = 0 / 0 -> ROȘU."""
    f = firma_s1003
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    pg.fill(".fereastra:last-of-type #bl-an", "2025")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-categorie'); return z && "
                         "!z.hasAttribute('aria-busy') && !z.innerText.includes('Se calculează'); }", timeout=90000)
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1003")
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-precedent'); "
                         "return z && z.dataset.pentru === '2025|s1003' && z.innerText.trim(); }", timeout=60000)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    f30 = pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri-f30 tbody tr",
                                  "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim()))")
    patron.captura()
    assert "Validare fără erori" in text and rand[("F20", 69)][1] == "5.500,00", (text[:300], sorted(rand))
    assert [x[0] for x in f30[:2]] == ["rândul 01", "rândul 02"] and f30[0][2:] == ["1", "5500"] and f30[1][2:] == ["0", "0"], f30


# ── 233 · 234 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_f10_manual():
    """Firmă nouă cu soldurile de preluare la 30.06.2025: bilanțul 2025 cere manual AMBELE secțiuni ale coloanei „An precedent” (31.12.2024
    e dinaintea preluării, iar evidența nu acoperă 2024)."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2025-06-30")
        yield f


def _tabel_manual(pg, sectiune):
    """[(cod, denumire, câmp | None, valoarea afișată)] pe rândurile tabelului manual al secțiunii, în ordinea de pe ecran."""
    return pg.eval_on_selector_all(
        ".fereastra:last-of-type .bl-prec-tabel[data-sectiune='%s'] tbody tr" % sectiune,
        "trs => trs.map(t => { const td = [...t.querySelectorAll('td')]; const i = t.querySelector('input'); "
        "return [td[0].innerText.trim(), td[1].innerText.trim(), i ? i.dataset.rand : null, td[2].innerText.trim()]; })")


def test_def_233_totalurile_se_calculeaza_si_nu_au_camp(patron, firma_f10_manual):
    """233. „în bilanț, la completarea manuală a coloanei «An precedent», rândurile de total (de ex. F10 rd.4 = 01+02+03, rd.6 = 301+302,
    rd.9; F20 profit/pierdere) au câmp de completat. Totalurile se calculează automat din componente și se afișează fără câmp.”
    Pașii: firma cu soldurile de preluare la 30.06.2025 -> Bilanț 2025, S1005: F10 și F20 se cer manual; rândurile de total (F10: 04, 06,
    09, 10, 14, 15, 18, 19, 22, 25, 29, 46, 49; F20: 08, 09) n-au câmp -> scrie rd.08 casa și conturi la bănci 5.000 și rd.30 capitalul
    5.000, F20 rd.01 1.000 și rd.03 300: pe loc, rd.09 = rd.15 = rd.46 = rd.49 = 5.000,00 și profitul rd.08 = 700,00, pierderea 0,00 ->
    salvează -> „Validează”: „An precedent” pe rândurile de total = cele calculate (serverul le calculează la fel).
    MUTAȚIILE din plasă: totalurile înapoi cu câmp -> ROȘU; serverul nu mai calculează totalurile -> ROȘU."""
    pg = patron.pg
    f = firma_f10_manual
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    f10, f20 = _tabel_manual(pg, "F10"), _tabel_manual(pg, "F20")
    fara_camp = {s: [c for c, _d, i, _v in t if i is None] for s, t in (("F10", f10), ("F20", f20))}
    assert fara_camp == {"F10": ["rândul 04", "rândul 06", "rândul 09", "rândul 10", "rândul 14", "rândul 15", "rândul 18", "rândul 19",
                                 "rândul 22", "rândul 25", "rândul 29", "rândul 46", "rândul 49"],
                         "F20": ["rândul 08", "rândul 09"]}, fara_camp
    for sel, v in (("F10'] input[data-rand='8'", "5000"), ("F10'] input[data-rand='30'", "5000"),
                   ("F20'] input[data-rand='1'", "1000"), ("F20'] input[data-rand='3'", "300"),
                   # [C14] F30 cap.XIX, copiat din același bilanț depus: producția vândută 1.000, materiile prime 300 (= F20)
                   ("F30'] input[data-rand='168'", "1000"), ("F30'] input[data-rand='183'", "300")):
        pg.fill(".fereastra:last-of-type .bl-prec-tabel[data-sectiune='%s]" % sel, v)
    tot = {(s, c): v for s, t in (("F10", _tabel_manual(pg, "F10")), ("F20", _tabel_manual(pg, "F20"))) for c, _d, i, v in t if i is None}
    patron.captura("totaluri_calculate")
    assert [tot[("F10", "rândul %s" % r)] for r in ("09", "15", "46", "49", "04")] == ["5.000,00"] * 4 + ["0,00"], tot
    assert (tot[("F20", "rândul 08")], tot[("F20", "rândul 09")]) == ("700,00", "0,00"), tot
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("validat")
    assert (rand[("F10", 9)][0], rand[("F10", 49)][0], rand[("F20", 8)][0]) == ("5.000,00", "5.000,00", "700,00"), \
        (text[:400], sorted(rand.items()))


def test_def_234_denumirile_complete_curate_in_ordinea_formularului(patron, firma_f10_manual):
    """234. „denumirile rândurilor sunt copiate brut: «II. CREANȚE 1.» e tăiat, «2.Creante repr.dividende…» are puncte de suspensie,
    «6.Alte cheltuieli*****» are steluțe, «si» e fără diacritice. Rândurile 301 și 302 apar la final, nu sub rd.6. Denumirile se scriu
    complete, curate, cu diacritice, în ordinea de pe formular.”
    Pașii: Bilanț 2025, S1005, completarea manuală: F10 — rândurile în ordinea formularului (05, 06a (301), 06b (302), 06, 07 …), „II.
    Creanțe — 1. Creanțe”, „II. Creanțe — 2. Creanțe reprezentând dividende repartizate în cursul exercițiului financiar”, „IV. Casa și
    conturi la bănci”; F20 — „6. Alte cheltuieli” (fără steluțe); nicio denumire cu majuscule de formular, „…”, „*” sau cuvinte fără
    diacritice (verificatorul de limbă al aplicației).
    MUTAȚIA din plasă: ordinea după numărul rândului (301 / 302 la final) -> ROȘU."""
    pg = patron.pg
    f = firma_f10_manual
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    f10, f20 = _tabel_manual(pg, "F10"), _tabel_manual(pg, "F20")
    patron.captura("denumiri")
    coduri = [c for c, _d, _i, _v in f10]
    assert coduri[4:9] == ["rândul 05", "rândul 06a (301)", "rândul 06b (302)", "rândul 06", "rândul 07"], coduri
    den, den20 = {c: d for c, d, _i, _v in f10}, {c: d for c, d, _i, _v in f20}
    assert den["rândul 06a (301)"] == "II. Creanțe — 1. Creanțe", den
    assert den["rândul 06b (302)"] == "II. Creanțe — 2. Creanțe reprezentând dividende repartizate în cursul exercițiului financiar", den
    assert (den["rândul 08"], den20["rândul 06"]) == ("IV. Casa și conturi la bănci", "6. Alte cheltuieli"), (den, den20)
    from core import limba_ecran
    rele = [(c, d) for c, d, _i, _v in f10 + f20 if limba_ecran.defecte(d) or re.search(r"\*|\.\.\.|…", d)]
    assert not rele, rele


# ── 235 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_infiintata_2026():
    for f in firma_noua():
        _date_firma(f)
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2026-03-15"})
        assert st == 200 and r.get("ok") is not False, (st, r)
        yield f


def test_def_235_primul_exercitiu_incadrarea_dupa_regula_entitatilor_nou_infiintate(patron, firma_infiintata_2026):
    """235. „la o firmă în primul exercițiu (F2, înființată pe 15.03.2026), căsuța roșie spune încă «Categoria de mărime nu se poate
    determina… norma cere două exerciții consecutive». Asta contrazice nota de primul exercițiu de dedesubt. Încadrarea în primul exercițiu
    se face după regula din OMFP 1802/2014 pentru entitățile nou-înființate, fără mesaj roșu. Citează temeiul.”
    TEMEI: OMFP 1802/2014 pct.22 alin.(1): „În cazul entităților nou-înființate, acestea pot întocmi pentru primul exercițiu financiar de
    raportare situațiile financiare anuale prevăzute fie la pct. 20, fie la pct. 21 sau în formatul aplicabil microentităților.”
    Pașii: firma înființată pe 15.03.2026 -> Bilanț 2026: caseta categoriei e de informare (nu de atenție), spune „Primul exercițiu
    financiar” și citează pct.22 alin.(1); „nu se poate determina” nu apare -> nota „An precedent” a primului exercițiu, dedesubt.
    MUTAȚIA din plasă: regula primului exercițiu scoasă din încadrare -> caseta roșie -> ROȘU."""
    pg = patron.pg
    f = firma_infiintata_2026
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    zona = _alege_bilant(patron, 2026)
    cat = pg.inner_text(".fereastra:last-of-type #bl-categorie")
    patron.captura()
    assert pg.locator(".fereastra:last-of-type #bl-categorie .caseta-atentie").count() == 0, cat
    assert pg.locator(".fereastra:last-of-type #bl-categorie .caseta-info").count() == 1, cat
    assert "Primul exercițiu financiar" in cat and "OMFP 1802/2014 pct.22 alin.(1)" in cat and "nu se poate determina" not in cat, cat
    assert "Primul exercițiu financiar: firma s-a înființat pe 15.03.2026" in zona, zona


# ── 236 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_236_tipul_bilantului_ramane_cel_ales_pe_firma(patron, firma_f20_manual, firma_infiintata_2026):
    """236. „tipul bilanțului revine la «— alege —» la schimbarea anului și la redeschiderea ecranului. Reține ultimul tip ales pentru fiecare
    firmă.”
    Pașii: firma A -> Bilanț: alege S1003 -> schimbă anul: rămâne S1003 -> închide și redeschide Bilanț: S1003 -> firma B: „— alege —”
    (tipul e al firmei A) -> alege S1005 -> înapoi la firma A: S1003.
    MUTAȚIA din plasă: tipul nu se mai reține -> ROȘU."""
    pg = patron.pg
    a, b = firma_f20_manual, firma_infiintata_2026
    tip = lambda: pg.eval_on_selector(".fereastra:last-of-type #bl-tip", "s => s.value")   # noqa: E731
    patron.firma(a["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1003")
    pg.fill(".fereastra:last-of-type #bl-an", "2024")
    pg.dispatch_event(".fereastra:last-of-type #bl-an", "change")
    assert tip() == "s1003"
    patron.firma(a["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    patron.captura("redeschis")
    assert tip() == "s1003"
    patron.firma(b["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    assert tip() == ""
    pg.select_option(".fereastra:last-of-type #bl-tip", "s1005")
    patron.firma(a["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    patron.captura("firma_a")
    assert tip() == "s1003"


# ── C12 · C13 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_cam_de_plata():
    """Firmă nouă cu soldurile de preluare la 31.12.2024 (bancă 10.000 = capital 9.500 + CAM-ul lui decembrie de plată, 436: 500) și un
    aport în 03/2025."""
    for f in firma_noua():
        _date_firma(f)
        st, r = _api(PATRON, "POST", "/tenants/%d/solduri" % f["tenant_id"],
                     {"data_referinta": "2024-12-31", "randuri": [
                         {"cont": "5121", "denumire": "Conturi la bănci în lei", "debit": 10000},
                         {"cont": "1012", "denumire": "Capital subscris vărsat", "credit": 9500},
                         {"cont": "436", "denumire": "Contribuția asiguratorie pentru muncă", "credit": 500}]})
        assert st == 200 and r.get("ok") is not False, (st, r)
        _nota_validata(f, "2025-03-10", "5121", "1012", 2000, "Aport capital C12")
        yield f


def test_def_c12_cam_de_plata_e_datorie_si_bilantul_e_valid(patron, firma_cam_de_plata):
    """C12. Bilanț F10: lista de conturi era scrisă din memorie, nu de pe formularul ANAF 2025 — lipsea 436 (CAM-ul de plată), deci bilanțul
    oricărei firme cu salariați ieșea inegal și DUK îl respingea („F10_64: F10_0492 (500) = … (1000)”). Găsită de Code la 233, 12.10.2026.
    Pașii: firma cu CAM de plată 500 la 31.12.2024 -> Bilanț 2025, S1005, F20 „An precedent” completat (2024 nu e în aplicație) ->
    „Validează”: fără erori; rd.13 (datorii sub un an) „An precedent” și „An curent” 500.
    MUTAȚIA din plasă: 436 scos din rd.13 -> ROȘU."""
    pg = patron.pg
    _bilant_2025(patron, firma_cam_de_plata)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura()
    assert "Validare fără erori" in text, text[:500]
    assert rand[("F10", 13)] == ("500,00", "500,00") and rand[("F10", 49)] == ("9.500,00", "11.500,00"), sorted(rand.items())


@pytest.fixture()
def firma_s1005_cheltuieli():
    """Firmă nouă: soldurile de preluare la 31.12.2024; în 2025 vânzări de mărfuri 1.000 (707), mărfuri descărcate 300 (607), servicii 200
    (628)."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _nota_validata(f, "2025-03-10", "5121", "707", 1000, "Vanzare marfa C13")
        _nota_validata(f, "2025-03-11", "607", "5121", 300, "Marfa descarcata C13")
        _nota_validata(f, "2025-03-12", "628", "5121", 200, "Servicii C13")
        _inchide_6_7(f, "2025-12-31", {"707": 1000, "607": -300, "628": -200})     # [C15]
        yield f


def test_def_c13_contul_prescurtat_pe_listele_formularului(patron, firma_s1005_cheltuieli):
    """C13. Bilanț S1005, contul prescurtat de profit și pierdere: mărfurile (607) ieșeau la rd.03 „Costul materiilor prime și al
    consumabilelor” (formularul 2025: „601 + 602 − 609”), reluările de ajustări se numărau de două ori, iar profitul nu era calculul
    formularului. Găsită de Code la 233, 12.10.2026.
    Pașii: firma cu vânzări de mărfuri 1.000, mărfuri 300, servicii 200 în 2025 -> Bilanț 2025, S1005, F20 „An precedent” completat ->
    „Validează” -> „Ce se depune”: rd.03 nu apare (zero), rd.06 „6. Alte cheltuieli” = 500 (607 + 628), rd.08 profit = 500 = rd.01 −
    rd.06 — iar de la C14 (F30 cap.XIX scris) validarea e fără erori.
    MUTAȚIA din plasă: 603–608 înapoi la rd.03 -> ROȘU."""
    pg = patron.pg
    _bilant_2025(patron, firma_s1005_cheltuieli)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura()
    f20 = {k[1]: v[1] for k, v in rand.items() if k[0] == "F20"}
    assert 3 not in f20 and (f20[1], f20[6], f20[8]) == ("1.000,00", "500,00", "500,00"), f20
    assert "Validare fără erori" in text, text[:600]


# ── C15 · C14 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_c15():
    """Firmă nouă: soldurile de preluare la 31.12.2024; în 2025 vânzări de mărfuri 1.000 (707), mărfuri 300 (607), servicii 200 (628) —
    neînchise în 121."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _nota_validata(f, "2025-03-10", "5121", "707", 1000, "Vanzare marfa C15")
        _nota_validata(f, "2025-03-11", "607", "5121", 300, "Marfa descarcata C15")
        _nota_validata(f, "2025-03-12", "628", "5121", 200, "Servicii C15")
        yield f


def test_def_c15_clasele_6_7_neinchise_opresc_bilantul_cu_suma_rezultatului(patron, firma_c15):
    """C15 (decizia Costin 12.10.2026, varianta (c)): „Generarea bilanțului se oprește cu motivul «închide clasele 6/7 în 121 la 31.12», cu
    suma rezultatului.” TEMEI: OMFP 1802/2014, contul 121 — „la sfârșitul perioadei, soldul creditor al conturilor din clasa 7 … soldul
    debitor al conturilor de cheltuieli”.
    Pașii: firma cu vânzări 1.000, mărfuri 300, servicii 200 în 2025, neînchise -> Bilanț 2025, S1005: „închide clasele 6/7 în 121 la
    31.12.2025. Rezultatul de închis: profit 500,00 lei”, cu conturile, iar acțiunile sunt inactive -> nota de închidere la 31.12 (707 =
    121, 121 = 607, 121 = 628) -> Bilanț 2025: coloana „An precedent” (F20 și F30 cap.XIX, 2024 nu e în aplicație) completată și salvată
    -> „Validează”: fără erori, profitul în bilanț (F10 rd.43 = 500), F20 rd.08 = 500.
    MUTAȚIA din plasă: verificarea închiderii scoasă -> bilanțul se generează fără rezultat -> ROȘU."""
    f = firma_c15
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    zona = _alege_bilant(patron, 2025)
    patron.captura("neinchise")
    assert "închide clasele 6/7 în 121 la 31.12.2025. Rezultatul de închis: profit 500,00 lei" in zona, zona
    assert re.findall(r"• (\d+) sold (debitor|creditor) ([\d.,]+)", zona) == [("607", "debitor", "300,00"), ("628", "debitor", "200,00"),
                                                                              ("707", "creditor", "1.000,00")], zona
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled()
    _inchide_6_7(f, "2025-12-31", {"707": 1000, "607": -300, "628": -200})
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    patron.captura("inchise_valid")
    assert "Validare fără erori" in text, text[:600]
    assert rand[("F10", 43)][1] == "500,00" and rand[("F20", 8)][1] == "500,00", sorted(rand.items())


@pytest.fixture()
def firma_c14():
    """Firmă înființată pe 10.01.2025 (primul exercițiu: coloana „An precedent” e legal goală): capital 1.000, vânzări de mărfuri 1.000,
    mărfuri 300, chirie 200 (6123), închise în 121 la 31.12.2025."""
    for f in firma_noua():
        _date_firma(f)
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2025-01-10"})
        assert st == 200 and r.get("ok") is not False, (st, r)
        # 6123 e în planul firmei de la lotul 9 (planul OMFP 1802/2014 întreg în șablon)
        assert sql('SELECT 1 FROM "%s".plan_conturi WHERE simbol = %%s' % f["schema"], ("6123",)) == [(1,)]
        _nota_validata(f, "2025-01-15", "5121", "1012", 1000, "Aport C14")
        _nota_validata(f, "2025-03-10", "5121", "707", 1000, "Vanzare marfa C14")
        _nota_validata(f, "2025-03-11", "607", "5121", 300, "Marfa descarcata C14")
        _nota_validata(f, "2025-03-12", "6123", "5121", 200, "Chirie C14")
        _inchide_6_7(f, "2025-12-31", {"707": 1000, "607": -300, "6123": -200})
        yield f


def test_def_c14_situatia_veniturilor_si_cheltuielilor_se_depune_si_bilantul_e_valid(patron, firma_c14):
    """C14 (comanda Costin 12.10.2026): „construiește F30 cap.XIX pentru S1005, după formularul ANAF 2025, cu listele de conturi tipărite pe
    fiecare rând.” Înainte: S1005 nu scria situația veniturilor și cheltuielilor, iar DUK îl respingea („F20_F30_2: F20_0012 (1000) =
    F30_1672 (0)”, „F20_F30_8: F20_0082 (500) = F30_2352 (0)”) la orice firmă cu activitate.
    Pașii: firma în primul exercițiu, cu vânzări 1.000, mărfuri 300, chirie 200, închise -> Bilanț 2025, S1005 -> „Validează”: fără erori;
    „Ce se depune” are F30 cap.XIX pe rândurile formularului, cu denumirile lui: rândul 167 cifra de afaceri 1.000, 169 vânzarea mărfurilor
    1.000, 186 mărfurile 300, 198a (331) chiriile 200 și „din care” 198d (334) 200, 235 profitul net 500 = F20 rd.08.
    MUTAȚIA din plasă: cap.XIX nescris în XML -> DUK respinge -> ROȘU."""
    pg = patron.pg
    f = firma_c14
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, 2025)
    text, rand = _valideaza_bilant(patron, 2025, alege=False)
    den = {(x[0], x[1]): x[2] for x in pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri tbody tr",
                                                              "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim()))")}
    patron.captura()
    pg.locator(".fereastra:last-of-type #bl-randuri tbody tr", has_text="rândul 167").scroll_into_view_if_needed()
    patron.captura("cap_xix")                                                  # rândurile cap.XIX, cu denumirile lor
    assert "Validare fără erori" in text, text[:600]
    f30 = {k[1]: v[1] for k, v in rand.items() if k[0] == "F30"}
    assert {k: f30.get(k) for k in (167, 169, 186, 331, 334, 235)} == {167: "1.000,00", 169: "1.000,00", 186: "300,00", 331: "200,00",
                                                                      334: "200,00", 235: "500,00"}, f30
    assert rand[("F20", 8)][1] == "500,00", sorted(rand.items())
    assert den[("F30", "rândul 198a (331)")] == "11.2. Cheltuieli cu redevențele, locațiile de gestiune și chiriile", den
    assert den[("F30", "rândul 167")].startswith("1. Cifra de afaceri netă"), den


# ── 237 · 238 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_solduri_fara_loc():
    """Firmă nouă: soldurile de preluare la 31.12.2024; în 2025 un avans plătit furnizorului pe 401 (401 debitor 500), TVA colectată
    neînchisă (4427 creditor 1.050) și o depunere de numerar înregistrată numai în bancă (581 creditor 1.000) — cazul F2 din producție."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _nota_validata(f, "2025-03-10", "401", "5121", 500, "Avans furnizor 238")
        _nota_validata(f, "2025-03-11", "4111", "4427", 1050, "TVA colectata 238")
        _nota_validata(f, "2025-03-12", "5121", "581", 1000, "Depunere numerar 238")
        yield f


def _bilant_oprit(patron, f):
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    return _alege_bilant(patron, 2025)


def test_def_237_mesajul_de_oprire_apare_o_singura_data(patron, firma_solduri_fara_loc):
    """237 (retestul Costin 12.10.2026): „în Bilanț, mesajul de oprire (solduri fără rând) apare de două ori: o dată gri, sub butoane, și o
    dată roșu, jos. Trebuie să apară o singură dată.”
    Pașii: firma cu solduri pe care bilanțul nu le preia -> Bilanț 2025, S1005: refuzul apare O DATĂ în fereastră (roșu), imediat sub
    rândul butoanelor (lotul 11, 440); lângă butoanele inactive scrie numai că așteaptă rezolvarea lui, fără „motivul e mai jos”.
    MUTAȚIA din plasă: nota de lângă butoane înapoi cu tot refuzul -> de două ori -> ROȘU."""
    pg = patron.pg
    _bilant_oprit(patron, firma_solduri_fara_loc)
    fereastra = pg.inner_text(".fereastra:last-of-type")
    nota = pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")
    patron.captura()
    assert fereastra.count("nu au loc în bilanț") == 1 and fereastra.count("401 sold debitor 500,00") == 1, fereastra[:1500]
    assert nota == "Inactive până se rezolvă refuzul:" and pg.locator(".fereastra:last-of-type #bl-val").is_disabled(), nota
    assert pg.eval_on_selector(".fereastra:last-of-type #bl-precedent", "z => !!z.previousElementSibling && z.previousElementSibling.classList.contains('rezumat-fix')"), "refuzul nu stă imediat sub rândul butoanelor (440)"
    assert pg.locator(".fereastra:last-of-type #bl-precedent .msg-eroare").count() == 1


def test_def_238_mesajul_de_oprire_pentru_contabil_un_rand_pe_cont(patron, firma_solduri_fara_loc):
    """238 (retestul Costin 12.10.2026): „mesajul de oprire e scris tehnic («nu au rând în bilanțul formularului… pe latura lor… DUK
    regula F10_64»). Rescrie-l pentru contabil, câte un rând pe cont, cu suma și acțiunea concretă, fără coduri DUK.”
    Pașii: firma cu 401 debitor 500, 4427 creditor 1.050, 581 creditor 1.000 la 31.12.2025 -> Bilanț 2025, S1005: refuzul are câte un rând
    pe cont, afișat pe rânduri separate: „401 sold debitor 500,00 — reclasifică în 409 (furnizori-debitori)”, „4427 sold creditor 1.050,00
    — închide TVA-ul lunii …”, „581 sold creditor 1.000,00 — viramentele interne trebuie să aibă sold zero …”, fiecare cu temeiul OMFP
    1802/2014; fără „DUK”, fără „F10_64”, fără „pe latura lor”.
    MUTAȚIA din plasă: mesajul vechi (o frază, cod DUK) -> ROȘU."""
    pg = patron.pg
    zona = _bilant_oprit(patron, firma_solduri_fara_loc)
    inaltime_rand = pg.eval_on_selector(".fereastra:last-of-type #bl-precedent .msg-eroare",
                                        "e => [e.getBoundingClientRect().height, parseFloat(getComputedStyle(e).lineHeight)]")
    patron.captura()
    linii = [ln for ln in zona.split("\n") if ln.startswith("• ")]
    assert [ln.split(" — ")[0] for ln in linii] == ["• 401 sold debitor 500,00", "• 4427 sold creditor 1.050,00",
                                                    "• 581 sold creditor 1.000,00"], zona
    assert linii[0].startswith("• 401 sold debitor 500,00 — reclasifică în 409 (furnizori-debitori). OMFP 1802/2014, contul 409"), linii
    assert "închide TVA-ul lunii" in linii[1] and "4423" in linii[1] and "viramentele interne trebuie să aibă sold zero" in linii[2], linii
    assert "DUK" not in zona and "F10_64" not in zona and "pe latura lor" not in zona, zona
    assert inaltime_rand[0] >= 4 * inaltime_rand[1] - 1, inaltime_rand               # antetul + trei rânduri, pe rânduri separate
