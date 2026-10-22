# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 (Costin, verbatim în DECIZII „Comanda 10.1”) — importurile de migrare: 425 (PRIORITAR: balanța de deschidere
cu soldurile inițiale ale anului și rulajele; metoda de stoc la migrare), 426 (a doua balanță cere confirmare), 420 (salariații fără
normă și funcție de bază intră cu propunere editabilă), 423 a/b/c (confirmarea după salvare, „gata · N de verificat”, textul ecranului
Salariați), SalariatEdit („Corectează datele” corectează și datele deducerilor).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). Balanța e cea SINTETICĂ din
`core/test_lot10_import_balanta.py` (fișierul `date_test/import_saga/balanta_saga_completa.xlsx`, 19 conturi la 30.09.2026, cele cinci
perechi SAGA, antet pe două rânduri). CNP-urile de probă au cifra de control verificată (algoritmul din CLAUDE.md)."""
import os
import sys

import pytest

from conftest import firma_noua, sql
from e2e_lot92 import _stat, firma_cv, firma_cv_noua  # noqa: F401 — fixturile modulului (Stat de plată)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_lot10_import_balanta import FISIER, _csv, randuri_saga   # noqa: E402

CNP1 = "1900101410011"      # cifra de control verificată (core/test_412_cim_salariat.py)
CNP2 = "1960101078916"      # cifra de control verificată (core/test_import_saga.py, CNP_OK)
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@pytest.fixture(scope="module")
def firma_mig():
    for f in firma_noua():
        sql('UPDATE "%s".firma_profil SET metoda_stoc = NULL WHERE id = 1' % f["schema"])   # metoda nedeclarată: o cere balanța
        yield f


def _pas(patron, firma, titlu):
    """Fereastra firmei -> „Import date” -> pasul cu titlul dat."""
    pg = patron.pg
    patron.firma(firma["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".mig-frand", timeout=20000)
    pg.locator(".mig-frand", has_text=titlu).first.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)


def _incarca(patron, nume, continut, astept, tip="text/csv"):
    patron.pg.set_input_files("#mig-file", files=[{"name": nume, "mimeType": tip, "buffer": continut}])
    patron.pg.wait_for_selector(astept, timeout=30000)


def _randul(pg, nr):
    return " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="%s"]' % nr).all_inner_texts()).split())


def _numai_solduri_finale():
    return _csv([r[:2] + r[10:] for r in randuri_saga()])


# ── 425 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_425_numai_soldurile_finale_spune_ce_lipseste_si_ce_afecteaza(patron, firma_mig):
    """425 (a doua jumătate): „Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului
    lipsesc și ce afectează.” Pașii: firma -> Import date -> Solduri inițiale -> balanța numai cu soldurile finale -> caseta galbenă:
    „Fișierul are numai soldurile finale: soldurile de la 1 ianuarie și rulajele anului până la 30.09.2026 lipsesc …” cu D101,
    situațiile financiare anuale, plafonul de microîntreprindere, controalele cumulate de TVA; 9 conturi (cele cu sold final)."""
    pg = patron.pg
    _pas(patron, firma_mig, "Solduri ini")
    _incarca(patron, "balanta_solduri_finale.csv", _numai_solduri_finale(), "#mig-salveaza-sold")
    patron.captura()
    av = " ".join(pg.inner_text("#mig-rulaje").split())
    assert pg.locator("#mig-rulaje.msg-avert, #mig-rulaje .msg-avert").count() >= 1, av
    for ce in ("Fișierul are numai soldurile finale", "până la 30.09.2026 lipsesc", "(D101)", "situațiile financiare anuale",
               "plafonul de microîntreprindere", "controalele cumulate de TVA"):
        assert ce in av, (ce, av)
    # [lotul 11, 424 — comanda Costin 11.1 pct.13, DS cap.9 v2.98] „ce s-a citit” (și conturile cu sold 0 care nu intră) e o notă pliată,
    # `details#mig-citit`, cu coloanele soldului în titlu; avertismentul rulajelor (#mig-rulaje) rămâne la vedere. Contabilul o deschide.
    pg.click("#mig-citit > summary")
    pg.wait_for_function("() => document.querySelector('#mig-citit').open", timeout=5000)
    t = " ".join(patron.fereastra().split())
    assert "9 conturi · debit 79.525,00 · credit 79.525,00" in t and "10 conturi cu sold final 0 nu intră" in t, t[:1500]


def test_def_425_balanta_completa_intra_cu_rulajele_si_cere_metoda_de_stoc(patron, firma_mig):
    """425: „O balanță completă la 30.09.2026 (format SAGA …) e citită doar din «Solduri finale» […] conturile cu sold final 0 (707, 607,
    641, 646, 6811, 4426, 4427) nu intră deloc.” Pașii: Solduri inițiale -> balanța SAGA completă (XLSX) -> 19 conturi, cu 707: rulaj
    180.000,00 / 180.000,00, sold final 0; nota spune ce perechi s-au citit -> „Metoda de stoc a firmei” e cerută (sold pe 371):
    „Salvează” fără ea -> refuz lângă câmp, nimic scris -> cantitativ-valoric -> „19 conturi salvate, cu soldurile la 30.09.2026.
    Soldurile de la 1 ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.” (pe ecranul în care se revine);
    în evidență: 707 cu rulajul anului 180.000, metoda de stoc cantitativ-valorică, în jurnalul Date firmă."""
    pg = patron.pg
    s = firma_mig["schema"]
    _pas(patron, firma_mig, "Solduri ini")
    _incarca(patron, "balanta_saga_completa.xlsx", open(FISIER, "rb").read(), "#mig-salveaza-sold", tip=XLSX)
    pg.click("#mig-citit summary")     # [lotul 11, 424] ce s-a citit din fișier stă pliat sub primul rând (rezumatul lipit sus e scurt)
    t = " ".join(patron.fereastra().split())
    patron.captura("previzualizare")
    assert "19 conturi · debit 79.525,00 · credit 79.525,00" in t, t[:1500]
    assert ("Din aceeași balanță s-au citit soldurile la 1 ianuarie din „Solduri inițiale an Debit” / „Solduri inițiale an Credit”"
            in t), t[:2500]
    assert _randul(pg, 24) == "24 intră 707 Venituri din vânzarea mărfurilor — 180.000,00 180.000,00 0,00 0,00", _randul(pg, 24)
    assert _randul(pg, 19) == "19 intră 5121 Conturi la bănci în lei 12.000,00 D 200.000,00 183.275,00 28.725,00 0,00"
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector('.msg-eroare[data-camp="mig-metoda-stoc"]', timeout=10000)
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 0
    patron.captura("fara_metoda")
    pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => document.body.innerText.includes('19 conturi salvate, cu soldurile la 30.09.2026. Soldurile de la 1 "
                         "ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT si_an_debit, rulaj_an_debit, rulaj_an_credit, sold_debitor, sold_creditor FROM "%s".solduri_initiale '
               "WHERE cont = '707'" % s) == [(0, 180000, 180000, 0, 0)]
    assert sql('SELECT metoda_stoc FROM "%s".firma_profil' % s) == [("cantitativ_valoric",)]
    assert sql('SELECT valoare_noua FROM "%s".firma_profil_jurnal WHERE camp = %%s' % s, ("metoda_stoc",)) == [("cantitativ_valoric",)]


# ── 426 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_426_a_doua_balanta_arata_totalurile_si_cere_confirmare(patron, firma_mig):
    """426: „al doilea import de balanță pentru aceeași firmă o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că
    există deja o balanță, arată totalurile vechi și noi, cere confirmare; dacă există note pe lunile de după preluare, spune că soldurile
    lor se recalculează.” Pașii: firma cu balanța completă (testul de mai sus) și o notă pe 05.10.2026 -> Solduri inițiale -> altă
    balanță -> caseta: „Firma are deja o balanță de deschidere la 30.09.2026: 19 conturi …”, „Balanța nouă …: 9 conturi …”, „Firma are o
    notă contabilă după data balanței (prima la 05.10.2026): soldurile lor se recalculează pe balanța nouă.” -> „Înlocuiește balanța” ->
    confirmarea -> „Renunță”: nimic schimbat -> din nou -> „Înlocuiesc balanța” -> „Balanța veche (19 conturi, la 30.09.2026) a fost
    înlocuită.”; în evidență 9 conturi."""
    pg = patron.pg
    s = firma_mig["schema"]
    if not sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0]:
        pytest.skip("rulat singur: balanța de înlocuit o scrie testul 425 de mai sus")
    sql('INSERT INTO "%s".inregistrari (data, numar, descriere) VALUES (%%s, %%s, %%s)' % s, ("2026-10-05", "E2E-426", "probă 426"))
    _pas(patron, firma_mig, "Solduri ini")
    _incarca(patron, "balanta_solduri_finale.csv", _numai_solduri_finale(), "#mig-salveaza-sold")
    caseta = " ".join(pg.inner_text("#mig-inlocuire").split())
    patron.captura("avertisment")
    assert caseta.startswith("Firma are deja o balanță de deschidere la 30.09.2026: 19 conturi, debit 79.525,00 lei, credit 79.525,00 lei. "
                             "Balanța nouă la 30.09.2026: 9 conturi, debit 79.525,00 lei, credit 79.525,00 lei."), caseta
    assert "Firma are o notă contabilă după data balanței (prima la 05.10.2026): soldurile lor se recalculează pe balanța nouă." in caseta
    assert pg.inner_text("#mig-salveaza-sold").strip() == "Înlocuiește balanța"
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector("#ca-ok", timeout=10000)
    assert pg.inner_text("#ca-ok").strip() == "Înlocuiesc balanța"
    pg.click("#ca-nu")
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 19
    pg.click("#mig-salveaza-sold")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('a fost înlocuită.')", timeout=30000)
    t = " ".join(patron.fereastra().split())
    patron.captura("inlocuita")
    assert "9 conturi salvate, cu soldurile la 30.09.2026. Balanța veche (19 conturi, la 30.09.2026) a fost înlocuită." in t, t[:1500]
    assert "Soldurile notei de după 30.09.2026 se recalculează pe balanța nouă." in t, t[:1500]
    assert sql('SELECT count(*), count(rulaj_an_debit) FROM "%s".solduri_initiale' % s) == [(9, 0)]


# ── 420 / 423 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _migrare(patron):
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='firme'])")
    pg.click("#opt-migrare")
    pg.wait_for_selector("#mig-meniu .mig-op", timeout=20000)


def _lista_salariati(patron, firma):
    pg = patron.pg
    pg.locator("#mig-meniu .mig-op", has_text="Salariați").first.click()
    pg.wait_for_selector(".mig-frand", timeout=20000)
    return pg.locator(".mig-frand", has_text=firma["nume"]).first


@pytest.fixture()
def firma_sal():
    """O firmă NOUĂ pe test: importul salariaților o singură dată (al doilea import pe aceeași firmă cere confirmarea, 426)."""
    yield from firma_noua()


def _importa_fara_norma(patron, firma):
    """Firme -> Migrare cabinet -> Salariați -> firma -> fișierul fără normă și funcție de bază -> IONESCU: normă parțială, 4 ore ->
    „Salvează”. Întoarce textul introducerii ecranului Salariați (423 c), citit înainte de alegerea firmei."""
    pg = patron.pg
    csv = ("nume;prenume;cnp;data angajare;brut;judet;cor;persoane in intretinere;scutit contributie minima\n"
           "POPESCU;ANA;%s;2024-01-15;5000;B;251401;0;nu\nIONESCU;RADU;%s;2024-02-01;6000;CJ;251401;1;nu\n" % (CNP1, CNP2)).encode()
    _migrare(patron)
    rand = _lista_salariati(patron, firma)
    intro = " ".join(pg.inner_text(".mig-intro").split())
    rand.click()
    pg.wait_for_selector("#mig-file", state="attached", timeout=10000)
    _incarca(patron, "salariati_fara_norma.csv", csv, "#mig-salveaza-sal")
    propuse = [pg.input_value(x) for x in ("#mig-norma-2", "#mig-fbaza-2", "#mig-norma-3", "#mig-fbaza-3")]
    rand2 = _randul(pg, 2)
    patron.captura("propuneri")
    pg.select_option("#mig-norma-3", "partiala")
    pg.fill("#mig-ore-3", "4")
    pg.click("#mig-salveaza-sal")
    return intro, propuse, rand2


def test_def_420_salariatii_fara_norma_intra_cu_propunerea_editabila(patron, firma_sal):
    """420: „rândurile fără normă de lucru și funcție de bază sunt respinse întregi […] Câmpurile lipsă se completează pe ecran, înainte de
    import, cu propunere editabilă (normă întreagă, funcție de bază Da) […] (intră marcate «de verificat»).”
    Pașii: Firme -> Migrare cabinet -> Salariați -> firma -> fișierul fără norma și funcția de bază -> pe fiecare rând: Normă „întreagă
    (8 h)” și Funcție de bază „Da”, propuse, de verificat -> la IONESCU: normă parțială, 4 ore -> „Salvează” -> în evidență: IONESCU
    parțial 4 ore (ales), POPESCU întreagă 8 ore (propus), amândoi cu ce e de verificat."""
    s = firma_sal["schema"]
    _intro, propuse, rand2 = _importa_fara_norma(patron, firma_sal)
    assert propuse == ["intreaga", "true", "intreaga", "true"]          # propunerea comenzii: normă întreagă, funcție de bază Da
    assert "propusă — de verificat" in rand2 and "intră, cu observație" in rand2, rand2
    patron.pg.wait_for_function("() => document.body.innerText.includes('Salariați: 2 noi, 0 fișe actualizate.')", timeout=30000)
    assert sql('SELECT nume, part_time, ore_zi, functie_baza, de_verificat FROM "%s".salariati ORDER BY nume' % s) == [
        ("IONESCU", True, 4, True, ["functie_baza"]), ("POPESCU", False, 8, True, ["tip_norma", "functie_baza"])]


def test_def_423_importul_salariatilor_confirma_si_numara_cei_de_verificat(patron, firma_sal):
    """423 a: „după salvare nu apare niciun mesaj de confirmare (aceeași clasă cu 410)”; b: „starea «gata» nu spune câți salariați rămân
    «de verificat»”; c: „textul ecranului Salariați spune că importul se face doar după ce toate sunt corectate, dar salariații intră cu
    observații — textul urmează comportamentul.”
    Pașii: Firme -> Migrare cabinet -> Salariați (textul: „rândurile bune intră, cele respinse … se arată”) -> firma -> fișierul fără
    normă și funcție de bază -> „Salvează” -> în lista Salariați, confirmarea „Salariați: 2 noi, 0 fișe actualizate. 2 salariați au date de verificat în
    Stat de plată” -> rândul firmei: „✓ gata · 2 de verificat”."""
    pg = patron.pg
    intro, _propuse, _rand2 = _importa_fara_norma(patron, firma_sal)
    assert "doar după ce toate sunt corectate" not in intro and "rândurile bune intră, cele respinse" in intro, intro      # 423 c
    pg.wait_for_function("() => document.body.innerText.includes('Salariați: 2 noi, 0 fișe actualizate. 2 salariați au date de verificat în Stat de "
                         "plată')", timeout=30000)
    patron.captura("confirmare")                                                                                    # 423 a
    assert pg.locator(".mig-frand").count() >= 1                       # e lista stratului (drumul de cabinet), nu meniul firmei
    # 423 b: rezumatul se recalculează în fundal după scriere; lista se redeschide până îl arată
    for _ in range(20):
        _migrare(patron)
        txt = " ".join(_lista_salariati(patron, firma_sal).inner_text().split())
        if "de verificat" in txt:
            break
        pg.wait_for_timeout(1000)
    patron.captura("gata_de_verificat")
    assert "✓ gata · 2 de verificat" in txt and "2 salariați importați · 2 au date de verificat în Stat de plată" in txt, txt


# ── SalariatEdit ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_salariat_edit_corecteaza_datele_deducerilor(patron, firma_cv):
    """Decizia sesiunii principale (observația „SalariatEdit” din lotul 9): „Corectează datele” primește data nașterii, copiii
    școlarizați, declarația copiilor și funcția de bază (deducerile CF art.77 depind de ele). Pașii: Salariați -> „Corectează datele” la
    IONESCU VASILE -> funcția de bază „Nu”, data nașterii 10.05.2002, 2 copii, declarația „Da” -> „Salvează” -> confirmarea „IONESCU
    VASILE: datele corectate s-au salvat; statul se calculează cu ele.”; fișa le păstrează, iar formularul redeschis le arată."""
    s = firma_cv["schema"]
    pg = _stat(patron, firma_cv)
    rand = pg.locator(".pf-frand", has_text="IONESCU VASILE").first
    rand.locator("[data-date]").click()
    pg.wait_for_function("() => (document.querySelector('#ed-fbaza') || {}).value", timeout=20000)   # fișa citită (Da/Nu salvat)
    pg.select_option("#ed-fbaza", "false")
    pg.fill("#ed-nastere", "2002-05-10")
    pg.fill("#ed-copii", "2")
    pg.select_option("#ed-declcopii", "true")
    pg.click("#ed-save")
    pg.wait_for_function("() => document.body.innerText.includes('datele corectate s-au salvat; statul se calculează cu ele.')",
                         timeout=30000)
    patron.captura()
    assert sql('SELECT functie_baza, data_nastere::text, copii_scolarizati, declaratie_copii FROM "%s".salariati WHERE nume = %%s'
               % s, ("IONESCU",)) == [(False, "2002-05-10", 2, True)]
    rand = pg.locator(".pf-frand", has_text="IONESCU VASILE").first
    rand.locator("[data-date]").click()
    pg.wait_for_function("() => (document.querySelector('#ed-nastere') || {}).value === '2002-05-10'", timeout=20000)
    assert (pg.input_value("#ed-fbaza"), pg.input_value("#ed-copii"), pg.input_value("#ed-declcopii")) == ("false", "2", "true")
    # starea de la început, pentru rularea repetată
    sql('UPDATE "%s".salariati SET functie_baza = true, data_nastere = NULL, copii_scolarizati = 0, declaratie_copii = false '
        "WHERE nume = %%s" % s, ("IONESCU",))
