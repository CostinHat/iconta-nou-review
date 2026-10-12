# -*- coding: utf-8 -*-
"""Retestul Costin 12.10.2026 (verbatim în DECIZII): 224 și 225 redeschise, 226–232 — probate în browser, pe firme noi ale rulării și pe
firmele de test ale cabinetului. Pașii contabilului sunt în docstringul fiecărui test; captura fiecăruia rămâne în directorul plasei."""
import datetime as _dt
import re

import pytest

from conftest import firma_noua
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
    assert abs(c["h"] - sorted(m["carduri"])[len(m["carduri"]) // 2]) <= 1, (c["h"], m["carduri"])
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
        assert ma["structura"] == mp["structura"] == ["cab-salut", "cab-grila"], (ma["structura"], mp["structura"])
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
    patron.pg.click(".fereastra:last-of-type details.cf-inainte summary")
    expl = patron.pg.inner_text(".fereastra:last-of-type details.cf-inainte .cf-incr-temei")
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
    assert den[0] == ["rândul 1", "1.Cifra de afaceri netă"] and den[3] == ["rândul 4", "4.Cheltuieli cu personalul"], den
    assert all(d for _r, d in den) and len(den) == 9, den                                     # F20 micro: 9 rânduri, toate cu denumire
    pg.click(".fereastra:last-of-type #bl-prec-salveaza")
    pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #bl-val').disabled", timeout=60000)
    text, _rand = _valideaza_bilant(patron, 2025, alege=False)
    rand8 = pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri tbody tr",
                                    "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim())).filter(c => c[0] === 'F10' && c[1] === 'rândul 8')")
    patron.captura("randuri_depuse_cu_denumire")
    assert "Validare fără erori" in text and rand8 and rand8[0][2] == "IV. CASA ȘI CONTURI LA BĂNCI", (text[:300], rand8)


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
    assert actiuni == [True, True, True] and "An precedent" in motiv and "(F20)" in motiv, (actiuni, motiv)
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
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #bl-actiuni-motiv') || {}).innerText.includes('nu există')",
                         timeout=60000)
    patron.captura("inainte_de_infiintare")
    assert pg.locator(".fereastra:last-of-type #bl-val").is_disabled()
    assert "firma s-a înființat pe 15.03.2025" in pg.inner_text(".fereastra:last-of-type #bl-actiuni-motiv")


# ── 230 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_230_firul_de_intrare_al_lui_ana_incepe_de_la_1(browser, request, patron):
    """230. „la Ana, în catalog, «Firul de intrare» începe de la pasul 2. Numerotează de la 1.”
    Pașii: Ana (asistent, „Poate pregăti”) -> „?” -> „Firul de intrare”: pașii numerotați 1, 2, 3 … (fără pasul „Firme”, al
    administratorului) -> contabilul-șef: tot de la 1, începând cu „Firme”.
    MUTAȚIA din plasă: numărul luat înapoi din STRATURI (`st.nr`) -> la Ana începe de la 2 -> ROȘU."""
    with cont_asistent(firme=(T_COMERT,)) as a, ecran_cont(browser, request, a["email"]) as e:
        e.acasa()
        e.pg.click("#nav-ghid")
        e.pg.wait_for_selector(".fereastra .ans-pas-nr", timeout=20000)
        nr = e.pg.eval_on_selector_all(".fereastra .ans-pas-nr", "els => els.map(x => x.innerText.trim())")
        titluri = e.pg.eval_on_selector_all(".fereastra .ans-pas-titlu", "els => els.map(x => x.innerText.trim())")
        e.captura("ana")
        assert nr == [str(i) for i in range(1, len(nr) + 1)] and "Firme" not in titluri, (nr, titluri)
    patron.acasa()
    patron.pg.click("#nav-ghid")
    patron.pg.wait_for_selector(".fereastra .ans-pas-nr", timeout=20000)
    nr = patron.pg.eval_on_selector_all(".fereastra .ans-pas-nr", "els => els.map(x => x.innerText.trim())")
    assert nr == [str(i) for i in range(1, len(nr) + 1)], nr


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
    assert [x[:2] for x in f30] == [["rândul 1", "Unităti care au inregistrat profit"], ["rândul 2", "Unităti care au inregistrat pierdere"],
                                    ["rândul 3", "Unități care nu au înregistrat nici profit nici pierdere"]], f30
    assert f30[2][2:] == ["1", "0"], f30                                       # o unitate fără profit și fără pierdere: „1”, nu „1,00”


# ── C10 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_s1003():
    """Firmă nouă: soldurile de preluare la 31.12.2024, iar în 2025 vânzări 5.000 (704), o subvenție aferentă cifrei de afaceri 800 (7411)
    și reduceri comerciale acordate 300 (709)."""
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        # 7411 (analiticul OMFP 1802 al lui 741, „aferente cifrei de afaceri”) și 709 nu sunt în șablonul planului firmei — contabilul le adaugă
        for simbol, den in (("7411", "Venituri din subvenții de exploatare aferente cifrei de afaceri"),
                            ("709", "Reduceri comerciale acordate")):
            st, r = _api(PATRON, "POST", "/tenants/%d/plan-conturi" % f["tenant_id"], {"simbol": simbol, "denumire": den})
            assert st == 200, (st, r)
        _nota_validata(f, "2025-03-10", "5121", "704", 5000, "Vanzare C10")
        _nota_validata(f, "2025-04-10", "5121", "7411", 800, "Subventie C10")
        _nota_validata(f, "2025-05-10", "709", "5121", 300, "Reducere C10")
        yield f


def test_def_c10_s1003_contul_de_profit_si_pierdere_pe_randurile_formularului(patron, firma_s1003):
    """C10. Bilanțul S1003: F20 era scris pe o numerotare proprie de 38 de rânduri (subvențiile pe rd.04, unde formularul ANAF are
    „Reduceri comerciale acordate”), iar rândurile 39–70 lipseau; DUK îl declara totuși „valid”. Găsită la extragerea denumirilor
    pentru 227 (12.10.2026); rescriere comandată de Costin (12.10.2026).
    Pașii: firma cu vânzări 5.000, subvenție aferentă cifrei de afaceri 800 și reduceri acordate 300 în 2025 -> Bilanț 2025, S1003 ->
    completează F20 „An precedent” (2024 nu e în aplicație) -> „Validează”: fără erori; „Ce se depune” — rd.04 „Reduceri comerciale
    acordate” 300, rd.06 subvenția 800, rd.01 cifra de afaceri 5.500 (rd.02 + 03 − 04 + 06), fiecare cu denumirea de pe formular.
    MUTAȚIA din plasă: 7411 înapoi pe rd.04 -> ROȘU."""
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
    den = {(x[0], int(x[1].split()[-1])): x[2] for x in pg.eval_on_selector_all(".fereastra:last-of-type #bl-randuri tbody tr",
           "trs => trs.map(t => [...t.querySelectorAll('td')].map(td => td.innerText.trim()))")}
    patron.captura()
    assert "Validare fără erori" in text, text[:400]
    assert (rand[("F20", 4)][1], rand[("F20", 6)][1], rand[("F20", 1)][1], rand[("F20", 2)][1]) == \
        ("300,00", "800,00", "5.500,00", "5.000,00"), sorted((k, v) for k, v in rand.items() if k[0] == "F20")
    assert den[("F20", 4)] == "Reduceri comerciale acordate" and den[("F20", 1)].startswith("1. Cifra de afaceri netă"), den
