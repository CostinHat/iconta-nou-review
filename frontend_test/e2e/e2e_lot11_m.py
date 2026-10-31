# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin, verbatim în DECIZII „Comanda 11.1”) — importurile de migrare, subagentul M:
439 (pct.5, PRIORITAR: „balanța completă SAGA e respinsă, pentru că verificarea omite soldul inițial al anului. După reparare, 425 și 426
trebuie să poată fi retestate.”), 420 (pct.12), 424 (pct.13), 446 (pct.14), 447 (pct.15).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`). Balanța e cea SINTETICĂ din
`core/test_lot11_m_balanta_saga.py` (forma exportului SAGA: titluri, antet pe două rânduri, sintetice + analitice, totaluri pe clasă,
Windows-1250; sold la 1 ianuarie pe 13 conturi; coloanele din descrierea lui Costin la 425: „solduri inițiale an, rulaje precedente,
rulaje lună, total sume, solduri finale”). CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md).

DE CE E2E-URILE LOTULUI 10 AU TRECUT ȘI PRODUCȚIA NU:
- 439: fișierul de probă al lui 425 era scris de aceeași presupunere ca și codul (sumele precedente = total sume − rulajele lunii, adică
  CU soldul inițial), deci verificarea `precedente + rulajele lunii = total sume` trecea pe el și pica pe „rulaje precedente” reale;
- 420: testul lucra pe o firmă nouă; pe F6 salariații existau (importați la 19.10 cu norma pusă tăcut), iar reimportul ținea marcajul
  numai pe intersecția cu cel vechi;
- 424 / 446: testul ferestrelor măsura numai importul salariaților, fără balanță existentă și fără confirmare, și numai butonul și
  derularea laterală — nu cât loc rămâne tabelului între rezumat și bară.
"""
import os
import sys

import pytest

from conftest import firma_noua, sql
from e2e_lot12_migr import confirma_firma_fisierului, alege_analitic_117

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_lot11_m_balanta_saga import fisier, randuri, _ro   # noqa: E402

#: [lotul 12, 599] antetul balanțelor SAGA de probă (`core/test_lot11_m_balanta_saga.fisier`, a doua linie): altă firmă decât firma de test,
#: deci salvarea cere întâi „Da, sunt ale acestei firme”
ANTET_MIGRARE = "SC Firmă Probă Migrare SRL"

LAPTOP = {"width": 1280, "height": 720}
CNP1 = "1900101410011"      # cifra de control verificată (core/test_412_cim_salariat.py)
CNP2 = "1960101078916"      # cifra de control verificată (core/test_import_saga.py, CNP_OK)
FARA_NORMA = ("nume;prenume;cnp;data angajare;brut;judet;cor;persoane in intretinere;scutit contributie minima\n"
              "POPESCU;ANA;%s;2024-01-15;5000;B;251401;0;nu\nIONESCU;RADU;%s;2024-02-01;6000;CJ;251401;1;nu\n" % (CNP1, CNP2)).encode()


def fisier_fara_norma():
    """Fișierul testului 420, pentru dovada pe firmele de test (`frontend_test/dovada/dovezi_lot11.json`, pasul `incarca`): aceeași sursă."""
    return FARA_NORMA

#: locul tabelului între rezumatul lipit sus și bara lipită jos, la 1280×720 (rândul de tabel ≈ 37 px)
MASOARA = """() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); const f = c.closest('.fereastra');
  const rez = c.querySelector('.rezumat-fix'), bara = c.querySelector('.bara-fixa'); c.scrollTop = 1e7;
  const r = (e) => e.getBoundingClientRect();
  return {loc: Math.round(r(f).bottom - r(c).top - rez.offsetHeight - bara.offsetHeight), rez_sus: Math.round(r(rez).top - r(c).top),
          bara_jos: Math.round(r(c).bottom - r(bara).bottom),
          derulante: [...f.querySelectorAll('*')].filter((e) => ['auto', 'scroll'].includes(getComputedStyle(e).overflowY)
                                                             && e.scrollHeight > e.clientHeight + 1).map((e) => e.className)}; }"""


@pytest.fixture()
def firma_m():
    for f in firma_noua():
        # metoda de stoc nedeclarată (o cere balanța, pe 371): firma nouă nu o are — coloana n-are implicit (`tenant_template.sql`,
        # `metoda_stoc`); se citește, nu se scrie
        assert sql('SELECT metoda_stoc FROM "%s".firma_profil' % f["schema"]) == [(None,)]
        yield f


def _pas(patron, firma, titlu):
    """Fereastra firmei -> „Import date” -> pasul cu titlul dat."""
    pg = patron.pg
    patron.firma(firma["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text=titlu).first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)


def _incarca(patron, nume, continut, astept):
    patron.pg.set_input_files("#mig-file", files=[{"name": nume, "mimeType": "text/csv", "buffer": continut}])
    patron.pg.wait_for_selector(astept, timeout=30000)


def _sold(s, cont):
    return [tuple(float(x) for x in r) for r in sql('SELECT si_an_debit, si_an_credit, rulaj_an_debit, rulaj_an_credit, sold_debitor, '
                                                     'sold_creditor FROM "%s".solduri_initiale WHERE cont = %%s' % s, (cont,))]


# ── 439 (+ 425 și 426 retestate pe balanța SAGA) ────────────────────────────────────────────────────────────────────────────────
def test_def_439_balanta_saga_cu_sold_initial_intra_si_a_doua_cere_confirmare(patron, firma_m):
    """439. Pașii: firma -> Import date -> Solduri inițiale -> balanța SAGA (rulaje precedente, total sume, sold la 1 ianuarie pe 13
    conturi) -> previzualizarea: 21 de conturi (sinteticele 401 / 4111 / 5121 înlocuite de analitice), „rulajele precedente (fără soldul
    inițial al anului)” -> data 30.09.2026, metoda cantitativ-valorică -> „Salvează soldurile” -> 21 de conturi salvate cu rulajele anului
    (5121.1: sold inițial 5.000, rulaje 45.000 / 41.200, sold final 8.800; 707: cifra de afaceri 50.000) -> 426: aceeași balanță în forma
    „total rulaje” -> avertismentul o dată, galben -> „Înlocuiește balanța” -> „Înlocuiesc balanța” -> „Renunță”: nimic schimbat -> din
    nou -> „Înlocuiesc balanța” -> „a fost înlocuită”. ROȘU înainte: „Rândul 6 (contul 1012): sumele precedente plus rulajele lunii
    (debit 0,00 lei, credit 0,00 lei) nu dau totalul sumelor (debit 0,00 lei, credit 16.800,00 lei)”."""
    pg, s = patron.pg, firma_m["schema"]
    _pas(patron, firma_m, "Solduri ini")
    _incarca(patron, "balanta_saga.csv", fisier("rulaje_precedente"), "#mig-salveaza-sold")
    t = " ".join(patron.fereastra().split())
    patron.captura("previzualizare")
    assert "21 de conturi · debit 38.200,00 · credit 38.200,00" in t and "echilibrat" in t, t[:1500]
    pg.click("#mig-citit summary")
    t = " ".join(patron.fereastra().split())
    assert "rulajele precedente (fără soldul inițial al anului) din „Rulaje precedente Debit” / „Rulaje precedente Credit”" in t, t[:2500]
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
    alege_analitic_117(pg)
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_MIGRARE)   # [lotul 12, 599] antetul balanței SAGA numește altă firmă: confirmarea, apoi salvarea
    pg.wait_for_function("() => document.body.innerText.includes('21 de conturi salvate, cu soldurile la 30.09.2026. Soldurile de la 1 "
                         "ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.')", timeout=30000)
    patron.captura("salvat")
    # OMFP 2634/2015 anexa 1 pct.52: soldul final din rulaje „ținându-se seama de soldul de la începutul anului”: 5.000 + 45.000 − 41.200
    assert _sold(s, "5121.1") == [(5000.0, 0.0, 45000.0, 41200.0, 8800.0, 0.0)]
    assert _sold(s, "707") == [(0.0, 0.0, 50000.0, 50000.0, 0.0, 0.0)]
    # 426 pe balanța SAGA: a doua balanță cere confirmarea
    _pas(patron, firma_m, "Solduri ini")
    _incarca(patron, "balanta_saga_2.csv", fisier("total_rulaje"), "#mig-salveaza-sold")
    from conftest import text_din_card
    av_text, av_cls = text_din_card(pg, "#mig-inlocuire")   # [lotul 14, 687] avertismentul stă în cardul lui
    assert av_cls == "msg-avert" and av_text.startswith(
        "Firma are deja o balanță de deschidere la 30.09.2026: 21 de conturi"), av_text
    alege_analitic_117(pg)
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_MIGRARE)   # [599] întâi firma din antet, apoi întrebarea înlocuirii (426)
    pg.wait_for_selector("#ca-ok", timeout=10000)
    assert pg.inner_text("#ca-ok").strip() == "Înlocuiesc balanța" and not pg.is_visible("#mig-salveaza-sold")
    patron.captura("confirmare")
    pg.click("#ca-nu")
    assert pg.is_visible("#mig-salveaza-sold") and sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 21
    alege_analitic_117(pg)
    pg.click("#mig-salveaza-sold")
    confirma_firma_fisierului(pg, ANTET_MIGRARE)
    pg.wait_for_function("() => (document.querySelector('#ca-ok') || {}).textContent === 'Înlocuiesc balanța'", timeout=10000)
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('a fost înlocuită.')", timeout=30000)
    assert _sold(s, "5121.1") == [(5000.0, 0.0, 45000.0, 41200.0, 8800.0, 0.0)]


def test_def_439_balanta_dezechilibrata_se_refuza_cu_motivul(patron, firma_m):
    """Balanța SAGA cu 100 lei în plus pe „Rulaje lună Credit” la 707 (fiecare cont se închide, numai coloanele nu se mai echilibrează)
    -> refuzul la încărcare numește perechea și totalurile: „Coloanele „Rulaje precedente Debit” / „Rulaje precedente Credit” nu se
    echilibrează: debit 276.340,00 lei, credit 276.240,00 lei (diferență 100,00 lei)”; nimic scris."""
    pg, s = patron.pg, firma_m["schema"]
    rr = randuri("rulaje_precedente")
    for r in rr:
        if r[0] == "707":
            for j in (7, 9, 11):
                r[j] = _ro(float(r[j].replace(".", "").replace(",", ".")) + 100)
        if r[0] == "1012":
            for j, d in ((4, 100), (8, 100), (11, -100)):
                r[j] = _ro(float(r[j].replace(".", "").replace(",", ".")) + d)
    _pas(patron, firma_m, "Solduri ini")
    pg.set_input_files("#mig-file", files=[{"name": "dezechilibrata.csv", "mimeType": "text/csv", "buffer": fisier(rr=rr)}])
    # starea FINALĂ a încărcării: `#mig-eroare` arată întâi „Se citește balanța…” (migrare.js, cât așteaptă serverul) — de așteptat refuzul
    # sau previzualizarea, nu primul text
    pg.wait_for_function("() => { const e = document.querySelector('#mig-eroare'); const p = document.querySelector('#mig-preview');"
                         " const t = ((e && e.innerText) || '').trim();"
                         " return (t && t !== 'Se citește balanța…') || !!(p && p.innerHTML.trim()); }", timeout=30000)
    m = " ".join(pg.inner_text("#mig-eroare").split())
    patron.captura()
    assert m.startswith("Coloanele „Rulaje precedente Debit” / „Rulaje precedente Credit” nu se echilibrează: debit 276.340,00 lei, "
                        "credit 276.240,00 lei (diferență 100,00 lei)"), m
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 0


# ── 424 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_424_importul_are_rezumatul_sus_actiunea_jos_si_deruleaza_numai_tabelul(patron, firma_m):
    """424. Pașii, la 1280×720: Import date -> Solduri inițiale -> balanța SAGA (21 de conturi) -> derulez tabelul la capăt: rezumatul
    (21 de conturi, debit / credit) rămâne sus, „Salvează soldurile” cu data și metoda rămân jos, între ele tabelul are cel puțin 240 px;
    un singur element derulează. Apoi Articole și stoc inițial (zona de încărcare nu mai stă deasupra rezumatului). ROȘU înainte:
    rezumatul lipit avea 611 px din 661 (nota „ce s-a citit”), deci nu mai stătea lipit și derula toată fereastra."""
    pg = patron.pg
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    try:
        _pas(patron, firma_m, "Solduri ini")
        _incarca(patron, "balanta_saga.csv", fisier("rulaje_precedente"), "#mig-salveaza-sold")
        o = pg.evaluate(MASOARA)
        patron.captura("balanta_derulata")
        assert o["derulante"] == ["zona-derulare"] and 0 <= o["rez_sus"] <= 100 and o["bara_jos"] == 0 and o["loc"] >= 240, o   # [lotul 14, 687] derulează numai zona tabelului; rezumatul rămâne sub titlu
        _pas(patron, firma_m, "Articole")
        _incarca(patron, "articole.csv", ("denumire;um;cantitate;pret;cont stoc;cont cheltuiala\n" + "".join(
            "Marfa %02d;buc;10;2,50;371;607\n" % i for i in range(30))).encode(), "#mig-importa")
        sus = pg.evaluate("() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); c.scrollTop = 0; "
                          "return Math.round(c.querySelector('.rezumat-fix').getBoundingClientRect().top - c.getBoundingClientRect().top); }")
        o = pg.evaluate(MASOARA)
        patron.captura("articole_derulate")
        assert sus <= 80 and not pg.is_visible("#mig-drop"), sus           # deasupra rezumatului numai titlul, nu zona de încărcare
        assert 0 <= o["rez_sus"] <= 100 and o["bara_jos"] == 0 and o["loc"] >= 240, o   # [lotul 14, 687] rezumatul rămâne sub titlu, nu mai e lipit de marginea corpului
    finally:
        pg.set_viewport_size(vp)


# ── 420 / 446 / 447 — salariații reimportați peste fișe existente (cazul F6) ────────────────────────────────────────────────────
def _fise_ca_pe_f6(s):
    """DATE DE PORNIRE: fișele lui POPESCU și IONESCU cum le-a lăsat importul din 19.10.2026 (dinainte de 420) — norma întreagă și funcția
    de bază puse fără marcaj, marcate numai persoanele și scutirea. Aplicația de azi nu mai produce starea asta (codul vechi o producea),
    deci se scrie direct; tot restul e drumul ecranului."""
    for cnp, nume in ((CNP1, "POPESCU"), (CNP2, "IONESCU")):
        # date-de-pornire: fișele lăsate de importul de dinainte de 420 (codul de azi nu mai produce starea asta) — documentul vechi
        sql('INSERT INTO "%s".salariati (cnp, nume, prenume, data_angajare, judet_casa, part_time, ore_zi, functie_baza, de_verificat) '
            "VALUES (%%s, %%s, 'X', '2024-01-15', 'B', false, 8, true, ARRAY['scutit_contrib_minim', 'persoane_intretinere'])" % s,
            (cnp, nume))


def _reimport(patron, firma):
    _fise_ca_pe_f6(firma["schema"])
    _pas(patron, firma, "Salaria")
    _incarca(patron, "salariati.csv", FARA_NORMA, "#mig-salveaza-sal")


def test_def_420_norma_si_functia_lipsa_arata_fisa_editabile_si_marcate(patron, firma_m):
    """420. Pașii: firma cu POPESCU / IONESCU (ca pe F6) -> Salariați -> fișierul fără normă și funcție de bază -> pe fiecare rând: Normă
    „întreagă (8 h)” și Funcție de bază „Da” — cele din fișă, editabile, „din fișa existentă — de verificat” -> la IONESCU aleg normă
    parțială, 4 ore -> „Salvează salariații” -> „Actualizez fișele” -> în fișe: POPESCU păstrează norma întreagă / „Da”, marcate de
    verificat; IONESCU parțial 4 ore (ales), marcată numai funcția de bază. ROȘU înainte: după salvare POPESCU avea marcajul [] (norma și
    funcția de bază „puse tăcut”)."""
    pg, s = patron.pg, firma_m["schema"]
    _reimport(patron, firma_m)
    assert [pg.input_value(x) for x in ("#mig-norma-2", "#mig-fbaza-2")] == ["intreaga", "true"]
    rand = " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="2"]').all_inner_texts()).split())
    patron.captura("propuneri")
    assert rand.count("din fișa existentă — de verificat") == 2, rand
    pg.select_option("#mig-norma-3", "partiala")
    pg.fill("#mig-ore-3", "4")
    pg.click("#mig-salveaza-sal")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('Salariați: 0 noi, 2 fișe actualizate.')", timeout=30000)
    fise = sql('SELECT nume, part_time, ore_zi, functie_baza, de_verificat FROM "%s".salariati ORDER BY nume' % s)
    assert [(n, p, float(o), f, sorted(d)) for n, p, o, f, d in fise] == [
        ("IONESCU", True, 4.0, True, ["functie_baza"]), ("POPESCU", False, 8.0, True, ["functie_baza", "tip_norma"])], fise


def test_def_446_avertismentul_o_data_confirmarea_ia_locul_butonului(patron, firma_m):
    """446. Pașii, la 1280×720: firma cu doi salariați -> Salariați -> fișierul cu aceiași CNP -> avertismentul „Firma are deja 2
    salariați …” o singură dată, galben (`msg-avert`), nu caseta roșie -> „Salvează salariații” -> întrebarea „Actualizezi fișele
    salariaților existenți cu datele din fișier?” (nu avertismentul din nou), „Salvează salariații” ascuns (numai „Actualizez fișele” și
    „Renunță”), tabelul are încă cel puțin 150 px -> „Renunță”: butonul revine, nimic scris."""
    pg, s = patron.pg, firma_m["schema"]
    vp = pg.viewport_size
    pg.set_viewport_size(LAPTOP)
    try:
        _reimport(patron, firma_m)
        from conftest import text_din_card
        text, av_cls = text_din_card(pg, "#mig-inlocuire")   # [lotul 14, 687] avertismentul stă în cardul lui
        text = text.strip()
        assert av_cls == "msg-avert" and text.startswith("Firma are deja 2 salariați"), text
        pg.click("#mig-salveaza-sal")
        pg.wait_for_selector("#ca-ok", timeout=10000)
        o = pg.evaluate(MASOARA)
        patron.captura("confirmare")
        f = patron.fereastra()
        assert f.count(text[:60]) == 0, f[:2000]   # [lotul 14, 687] avertismentul stă numai în cardul lui; confirmarea e întrebarea scurtă, nu a doua oară textul
        f += " " + pg.inner_text("#caseta-atentie-activa")   # [15.1, 446.1] întrebarea e fereastra de confirmare (în `body`), nu text al ferestrei de lucru
        assert "Actualizezi fișele salariaților existenți cu datele din fișier?" in f
        assert not pg.is_visible("#mig-salveaza-sal") and pg.inner_text("#ca-ok").strip() == "Actualizez fișele"
        assert o["loc"] >= 150, o
        pg.click("#ca-nu")
        assert pg.is_visible("#mig-salveaza-sal")
        assert sql('SELECT count(*) FROM "%s".salariati WHERE cardinality(de_verificat) = 2' % s)[0][0] == 2   # nimic actualizat
    finally:
        pg.set_viewport_size(vp)


def test_def_447_mesajul_spune_noi_si_fise_actualizate_o_singura_data(patron, firma_m):
    """447. Pașii: firma cu POPESCU / IONESCU -> Salariați -> fișierul cu aceiași CNP -> „Salvează salariații” -> „Actualizez fișele” ->
    mesajul „Salariați: 0 noi, 2 fișe actualizate.”, fără „2 salariați importați” și fără a doua numărătoare. ROȘU înainte: „2 salariați
    importați. Fișele a 2 salariați existenți au fost actualizate.”"""
    pg = patron.pg
    _reimport(patron, firma_m)
    pg.click("#mig-salveaza-sal")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('Salariați: 0 noi, 2 fișe actualizate.')", timeout=30000)
    t = patron.fereastra()
    patron.captura()
    assert "importați" not in t.split("Salariați: 0 noi, 2 fișe actualizate.")[0][-200:] and "au fost actualizate" not in t, t[:1500]
