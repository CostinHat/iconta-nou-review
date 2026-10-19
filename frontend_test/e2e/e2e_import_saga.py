# -*- coding: utf-8 -*-
"""Importul din SAGA (comanda Costin 14.10.2026, verbatim în DECIZII „Importul din SAGA”): C21–C25, C27–C32 — pașii contabilului pe
ecranele de import ale unei firme NOI de test, pe aplicația din index, pe baza de TEST. Fișierele sunt INVENTATE, cu antetele din
manualul SAGA C (`anaf_surse/saga_manual_topic*`), aceleași ca în `core/test_import_saga.py`."""
import os
import sys

import pytest

from conftest import firma_noua, sql

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.test_import_saga import BALANTA_SAGA, CNP_GRESIT, ISTORIC, MF_SAGA, SALARIATI_SAGA, _cp1250   # noqa: E402


@pytest.fixture(scope="module")
def firma_import():
    for f in firma_noua():
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
    patron.pg.wait_for_selector(astept, timeout=20000)


def _balanta(patron, firma):
    _pas(patron, firma, "Solduri ini")
    _incarca(patron, "balanta_saga.csv", _cp1250(BALANTA_SAGA), "#mig-salveaza-sold")
    return patron.fereastra()


# ── balanța ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c21_balanta_completa_se_citeste_cu_soldurile_finale(patron, firma_import):
    """C21: „Migrare -> Solduri inițiale: o balanță completă (sold inițial, rulaje, sold final) se importă cu PRIMELE coloane …
    soldurile inițiale, nu cele finale — fără niciun avertisment.”
    Pașii: firma -> Import date -> Solduri inițiale -> balanța SAGA (titluri, antet pe două rânduri: solduri inițiale an / total sume /
    solduri finale) -> previzualizarea spune din ce coloane s-a citit și 5311 are 300,00 (soldul FINAL; inițialul era 250).
    MUTAȚIA din plasă: perechea de sold final -> prima pereche -> ROȘU."""
    t = _balanta(patron, firma_import)
    patron.captura()
    assert "Soldurile s-au citit din coloanele „Solduri finale Debit” și „Solduri finale Credit”." in t, t[:1500]
    assert "5311 Casa în lei 300,00 0,00" in " ".join(t.split()), t[:1500]


def test_def_c29_totalurile_si_sinteticele_dublate_nu_intra(patron, firma_import):
    """C29 (găsită de Code la C21): rândurile „Total clasa 4” / „TOTAL GENERAL” intrau ca solduri de „cont”, iar sinteticul 401
    alături de analiticele lui se dubla — balanța rămânea echilibrată (totalul se dubla pe ambele părți), deci trecea.
    Pașii: aceeași balanță -> „2 rânduri nu sunt conturi și nu intră (totaluri, titluri)”, „Contul sintetic 401 e înlocuit de
    analiticele din fișier”, 4 conturi, debit = credit = 300,00."""
    t = _balanta(patron, firma_import)
    patron.captura()
    assert "2 rânduri nu sunt conturi și nu intră (totaluri, titluri): „Total clasa 4”, „TOTAL GENERAL”." in t, t[:1500]
    assert "Contul sintetic 401 e înlocuit de analiticele din fișier (același sold)." in t, t[:1500]
    assert "4 conturi · debit 300,00 · credit 300,00" in " ".join(t.split()), t[:800]


def test_def_c22_data_balantei_e_ceruta_si_salvata(patron, firma_import):
    """C22: „Migrare -> Solduri inițiale: data balanței nu se cere și nu se trimite.”
    Pașii: balanța -> „Salvează soldurile” fără dată: refuz lângă câmp („Scrie data la care sunt soldurile din balanță.”), nimic
    scris -> data 30.09.2026 -> „4 conturi salvate, cu soldurile la 30.09.2026.”; în evidență data soldurilor = 30.09.2026."""
    pg = patron.pg
    _balanta(patron, firma_import)
    pg.fill("#mig-data-bal", "")   # [344] data se propune (ziua dinaintea lunii preluării); proba cere câmpul golit de contabil
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector('.msg-eroare[data-camp="mig-data-bal"]', timeout=10000)
    assert "Scrie data la care sunt soldurile din balanță." in pg.inner_text('.msg-eroare[data-camp="mig-data-bal"]')
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % firma_import["schema"])[0][0] == 0
    patron.captura("fara_data")
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => document.body.innerText.includes('4 conturi salvate, cu soldurile la 30.09.2026.')", timeout=20000)
    patron.captura("salvat")
    assert sql('SELECT cont, sold_debitor, sold_creditor, data_referinta::text FROM "%s".solduri_initiale ORDER BY cont'
               % firma_import["schema"]) == [("1012", 0, 200, "2026-09-30"), ("401.00001", 0, 70, "2026-09-30"),
                                             ("401.00002", 0, 30, "2026-09-30"), ("5311", 300, 0, "2026-09-30")]


def test_def_c27_csv_windows_1250_cu_diacriticele_intacte(patron, firma_import):
    """C27: un CSV salvat în Windows-1250 se citea ca UTF-8 cu înlocuire: „Furnizor Şerban” devenea „Furnizor �erban”, tăcut.
    Pașii: balanța SAGA în Windows-1250 -> previzualizarea arată „Furnizor Şerban”, „Furnizor Ţăndărei”, „Capital subscris vărsat”;
    salvată, denumirile rămân cu diacritice."""
    pg = patron.pg
    t = _balanta(patron, firma_import)
    assert "Furnizor Şerban" in t and "Furnizor Ţăndărei" in t and "Capital subscris vărsat" in t and "�" not in t, t[:1500]
    patron.captura()
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_function("() => document.body.innerText.includes('4 conturi salvate')", timeout=20000)
    assert sql('SELECT denumire FROM "%s".solduri_initiale ORDER BY cont' % firma_import["schema"]) == [
        ("Capital subscris vărsat",), ("Furnizor Şerban",), ("Furnizor Ţăndărei",), ("Casa în lei",)]


# ── salariați ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _salariati(patron, firma):
    pg = patron.pg
    _pas(patron, firma, "Salaria")
    _incarca(patron, "salariati_saga.csv", _cp1250(SALARIATI_SAGA), "#mig-salveaza-sal")
    assert not pg.is_disabled("#mig-salveaza-sal"), patron.fereastra()[:1500]
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-sal")
    pg.wait_for_function("() => document.body.innerText.includes('2 salariați importați.')", timeout=20000)
    patron.captura("salvat")


def test_def_c23_iban_ul_salariatului_ajunge_in_evidenta(patron, firma_import):
    """C23: „Migrare -> Salariați: IBAN-ul citit din fișier se pierde la salvare.”
    Pașii: Import date -> Salariați -> fișierul SAGA (coloana „Cont card”) -> „Salvează” -> Popescu are IBAN-ul din fișier."""
    _salariati(patron, firma_import)
    assert sql('SELECT iban FROM "%s".salariati WHERE nume = %%s' % firma_import["schema"], ("Popescu",)) == \
        [("RO49AAAA1B31007593840000",)]


def test_def_c28_antetele_saga_se_recunosc_pe_cuvinte_intregi(patron, firma_import):
    """C28 (găsită de Code): coloanele se potriveau pe SUBȘIR — pe exportul SAGA „Funcție baza” nu se recunoștea (fiecare salariat
    refuzat), „Data angajării” se pierdea, „Norma pe zi” = 4 devenea normă întreagă, „Ore pe lună” intra ca ore pe zi, iar la
    imobilizări valoarea de intrare se lua din „Data intrare”.
    Pașii: salariații SAGA -> în evidență: Popescu angajat 15.01.2024, normă întreagă 8 h, casa CJ (din „CAS Cluj”); Ionescu
    normă parțială de 4 h -> imobilizările SAGA -> laptopul are valoarea 6.000 și contul 2131."""
    _salariati(patron, firma_import)
    assert sql('SELECT nume, data_angajare::text, judet_casa, part_time, ore_zi, functie_baza FROM "%s".salariati ORDER BY nume'
               % firma_import["schema"]) == [("Ionescu", "2025-03-01", "CJ", True, 4, False),
                                             ("Popescu", "2024-01-15", "CJ", False, 8, True)]
    _mijloace(patron, firma_import)
    assert sql('SELECT cod, valoare, dnf_luni, cont_imobilizare FROM "%s".mijloace_fixe' % firma_import["schema"]) == \
        [("100", 6000, 36, "2131")]


def test_def_c30_salvarea_nu_crede_indicatorii_trimisi_de_ecran(patron, firma_import):
    """C30 (găsită de Code): salvarea credea `cnp_valid` (salariați) și `valid` (articole) din cererea ecranului — o cerere cu
    `cnp_valid: true` pe un CNP cu cifra de control greșită intra. Pașii: din sesiunea contabilului, cererea de salvare a unui
    salariat cu CNP greșit și `cnp_valid: true` -> refuz „CNP invalid (cifra de control greșită)”, nimic scris."""
    pg = patron.pg
    patron.firma(firma_import["nume"])
    rasp = pg.evaluate("""async ([tid, cnp]) => {
        const tok = sessionStorage.getItem('iconta_token');          // static/js/sesiune.js: CHEIE_TOKEN, per tab
        const r = await fetch(`/tenants/${tid}/salariati-import`, {method: 'POST',
          headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + tok},
          body: JSON.stringify({randuri: [{nume: 'Fals', prenume: 'Cnp', cnp: cnp, cnp_valid: true, tip_norma: 'intreaga', ore_zi: 8,
                                          functie_baza: true, scutit_contrib_minim: false, salariu_brut: 5000, judet_casa: 'CJ'}]})});
        return [r.status, await r.text()]; }""", [firma_import["tenant_id"], CNP_GRESIT])
    assert rasp[0] == 422 and "CNP invalid (cifra de control greșită)" in rasp[1], rasp
    assert sql('SELECT count(*) FROM "%s".salariati WHERE nume = %%s' % firma_import["schema"], ("Fals",))[0][0] == 0


# ── mijloace fixe ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _mijloace(patron, firma, nume="mijloace_fixe_saga.csv", continut=None):
    pg = patron.pg
    _pas(patron, firma, "Mijloace fixe")
    _incarca(patron, nume, continut or _cp1250(MF_SAGA), "#mig-salveaza-mf")
    t = patron.fereastra()
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-mf")
    pg.wait_for_function("() => document.body.innerText.includes('Un mijloc fix importat.')", timeout=20000)
    return t, patron.fereastra()


def test_def_c24_mijloace_fixe_randul_problema_se_arata_restul_se_salveaza(patron, firma_import):
    """C24: „Migrare -> Mijloace fixe: un rând pentru care motorul nu poate calcula amortizarea face salvarea să cadă cu 422.”
    Decizia Costin 14.10.2026: „fără blocare la salvare; rândul problemă se arată, restul se salvează”.
    Pașii: Import date -> Mijloace fixe -> registrul SAGA (laptop liniar pe 2131; autoturism accelerat fără cont) -> „Un rând nu
    intră — celelalte se salvează”, butonul „Salvează rândul bun (mijloace fixe)” -> salvat: „Un mijloc fix importat.”, „Un rând
    nu a intrat: rândul 3 …”; în registru numai laptopul."""
    inainte, dupa = _mijloace(patron, firma_import)
    assert "Un rând nu intră — celelalte se salvează" in inainte and "rândul 3: Autoturism: amortizarea nu se poate calcula" in inainte
    assert "Salvează rândul bun (mijloace fixe)" in inainte, inainte[:2000]
    assert "Un rând nu a intrat:" in dupa and "rândul 3: Autoturism" in dupa, dupa[:1500]
    patron.captura("salvat")
    assert sql('SELECT cod FROM "%s".mijloace_fixe' % firma_import["schema"]) == [("100",)]


def test_def_c31_randul_numit_e_cel_din_fisier_sub_titluri(patron, firma_import):
    """C31 (găsită de Code): cu titluri deasupra antetului (registrul exportat are „Registrul imobilizărilor”, firma, data),
    refuzul număra rândurile de la antet = rândul 1, deci numea alt rând decât cel greșit.
    Pașii: registrul SAGA cu 3 rânduri de titlu deasupra antetului -> autoturismul e numit „rândul 6” (rândul lui din fișier)."""
    titluri = "Registrul imobilizărilor;;;\nSC Firmă Probă SRL;;;\nla 30.09.2026;;;\n"
    inainte, _ = _mijloace(patron, firma_import, "registru_cu_titluri.csv", _cp1250(titluri + MF_SAGA))
    assert "rândul 6: Autoturism: amortizarea nu se poate calcula" in inainte, inainte[:2000]


def test_def_c32_motivul_amortizarii_e_in_cuvinte(patron, firma_import):
    """C32 (găsită de Code la C24): motivul motorului de amortizare ajungea pe ecran cu codurile interne: „(contul , categoria
    „alt_mijloc_fix”): metoda 'accelerata' nu e permisă de lege; permise: degresiva, liniara”.
    Pașii: registrul SAGA -> rândul autoturismului: „fără cont de imobilizare, deci alt mijloc fix, CF art.28 alin.(5) lit.c):
    metoda accelerată nu e permisă de lege; permise: degresivă, liniară”, fără „alt_mijloc_fix”."""
    inainte, _ = _mijloace(patron, firma_import)
    assert ("fără cont de imobilizare, deci alt mijloc fix, CF art.28 alin.(5) lit.c): metoda accelerată nu e permisă de lege; "
            "permise: degresivă, liniară") in " ".join(inainte.split()), inainte[:2000]
    assert "alt_mijloc_fix" not in inainte and "'accelerata'" not in inainte


# ── istoric ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c25_istoricul_randul_problema_se_arata_restul_se_salveaza(patron, firma_import):
    """C25: „Migrare -> Istoric declarații: un rând cu avertisment face salvarea să cadă cu 422.” Decizia Costin 14.10.2026: „fără
    blocare la salvare; rândul problemă se arată, restul se salvează”.
    Pașii: Import date -> Istoric declarații -> D300 08/2026, D212 2025 (anuală, fără lună), D112 fără lună, D999 -> „2 rânduri nu
    intră”, cu motivele -> „Salvează cele 2 rânduri bune (declarații)” -> în evidență: d300 08/2026 și d212 pe 12/2025."""
    pg = patron.pg
    _pas(patron, firma_import, "Istoric declara")
    _incarca(patron, "istoric.csv", ISTORIC.encode("utf-8"), "#mig-salveaza-ist")
    t = patron.fereastra()
    assert "2 rânduri nu intră — celelalte se salvează" in t, t[:2000]
    assert "rândul 4: D112/2026: luna lipsește" in t and "rândul 5: declarația D999 nu există" in t, t[:2000]
    assert pg.inner_text("#mig-salveaza-ist").strip() == "Salvează cele 2 rânduri bune (declarații)"
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-ist")
    pg.wait_for_function("() => document.body.innerText.includes('2 declarații din istoric salvate.')", timeout=20000)
    patron.captura("salvat")
    assert sql("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id = %s AND sursa = 'migrare' ORDER BY tip",
               (firma_import["tenant_id"],)) == [("d212", 2025, 12), ("d300", 2026, 8)]


def test_def_c33_contul_de_doua_ori_se_refuza_numit(patron, firma_import):
    """C33 (găsită de Code în GARZI cat.1): `solduri_initiale(cont)` e UNIQUE în bază; o balanță cu același cont de două ori trecea de
    previzualizare și cădea la salvare cu o eroare de bază (500), fără să spună ce cont.
    Pașii: Import date -> Solduri inițiale -> balanța cu 5311 pe două rânduri -> refuz la încărcare: „Contul 5311 apare de mai multe
    ori în balanță.”, fără previzualizare și fără buton de salvare."""
    pg = patron.pg
    _pas(patron, firma_import, "Solduri ini")
    csv = "cont,denumire,sold debitor,sold creditor\n5311,Casa,100,0\n5311,Casa,50,0\n1012,Capital,0,150\n".encode("utf-8")
    pg.set_input_files("#mig-file", files=[{"name": "balanta_dubla.csv", "mimeType": "text/csv", "buffer": csv}])
    pg.wait_for_function("() => (document.querySelector('#mig-eroare') || {innerText: ''}).innerText.includes('apare de mai multe ori')",
                         timeout=20000)
    patron.captura()
    assert "Contul 5311 apare de mai multe ori în balanță." in pg.inner_text("#mig-eroare")
    assert pg.locator("#mig-salveaza-sold").count() == 0


# ── decizia Costin 14.10.2026 (răspunsul la §6 al lotului 1): salvarea parțială la salariați și parteneri; „de verificat” ─────
SALARIATI_FARA_SCUTIRE = (
    "Cod;Nume;Prenume;Funcție;Data angajării;Funcție baza;Norma pe zi;Ore pe lună;Salariu brut;CNP;Casa de sănătate;Cont card\n"
    "000001;Marin;Elena;Economist;15.01.2024;Da;8;168;6000;2950312123455;CAS Cluj;RO49 AAAA 1B31 0075 9384 0000\n"
    "000002;Dobre;Vasile;Vânzător;01.03.2025;Nu;4;84;3000;1850715410012;CJ;\n"
    "000003;Greșit;Ion;Paznic;01.03.2025;Da;8;168;4500;1960101078911;CJ;\n")


def test_salariatii_partial_si_de_verificat_pana_la_confirmare(patron, firma_import):
    """Decizia Costin 14.10.2026 pct.2–4 (verbatim în DECIZII): salvarea parțială la salariați; persoanele în întreținere și scutirea
    lipsă din fișier -> rândul se importă (0 / „nescutit”), salariatul e marcat, statul de plată afișează avertismentul până la
    confirmare; un reimport nu strică ce s-a confirmat.
    Pașii: exportul SAGA fără coloana scutirii, cu un CNP greșit -> „Un rând nu intră”, „Salvează cele 2 rânduri bune (salariați)”,
    „scutit minim: Nu — de verificat”, „persoane în întreținere: 0 — de completat” -> salvat: 2 salariați, marcați -> Stat de plată:
    avertismentul pe rând și „De verificat (2)” -> Marin: 1 persoană, scutit „Nu” -> „Confirmă” -> avertismentul dispare, marcajul
    e gol -> același fișier importat din nou: Marin rămâne cu 1 persoană, fără marcaj."""
    pg = patron.pg
    sch = firma_import["schema"]
    _pas(patron, firma_import, "Salaria")
    _incarca(patron, "salariati_fara_scutire.csv", _cp1250(SALARIATI_FARA_SCUTIRE), "#mig-salveaza-sal")
    t = patron.fereastra()
    assert "Un rând nu intră — celelalte se salvează" in t and "rândul 4: Greşit Ion: CNP invalid (cifra de control greșită)" in t, t[:2000]   # Windows-1250: ş cu sedilă
    # [349, comanda Costin 8.2] fiecare câmp are coloana lui în tabelul comun al previzualizării
    antet = [" ".join(x.split()) for x in pg.locator(".mig-prev thead th").all_inner_texts()]
    celule = dict(zip(antet, [x.strip() for x in pg.locator('.mig-prev tbody tr[data-rand="2"]:not(.mig-prev-motive) td').all_inner_texts()]))
    assert (celule["Scutit minim"], celule["Persoane în întreținere"]) == ("Nu (de verificat)", "0 (de verificat)"), celule
    assert pg.inner_text("#mig-salveaza-sal").strip() == "Salvează cele 2 rânduri bune (salariați)"
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-sal")
    pg.wait_for_function("() => document.body.innerText.includes('2 salariați importați.')", timeout=20000)
    assert "2 salariați au date de verificat în Stat de plată" in patron.fereastra()
    assert sql('SELECT nume, persoane_intretinere, scutit_contrib_minim, de_verificat FROM "%s".salariati '
               "WHERE nume IN ('Dobre', 'Marin') ORDER BY nume" % sch) == [
        ("Dobre", 0, False, ["persoane_intretinere", "scutit_contrib_minim"]),
        ("Marin", 0, False, ["persoane_intretinere", "scutit_contrib_minim"])]
    patron.firma(firma_import["nume"])
    pg.click("#fa-salariati")
    pg.wait_for_selector("[data-verif]", timeout=20000)
    t = patron.fereastra()
    assert "persoane în întreținere de completat (s-au importat 0 — deducerea personală poate fi greșită)" in t, t[:2000]
    patron.captura("stat_avertisment")
    pid = sql('SELECT id FROM "%s".salariati WHERE nume = %%s' % sch, ("Marin",))[0][0]
    pg.click("[data-verif='%s']" % pid)
    pg.fill("#dv-persoane", "1")
    pg.select_option("#dv-scutit", "false")
    pg.click("#dv-save")
    pg.wait_for_function("() => document.body.innerText.includes('datele de verificat sunt confirmate')", timeout=20000)
    patron.captura("confirmat")
    assert sql('SELECT persoane_intretinere, scutit_contrib_minim, de_verificat FROM "%s".salariati WHERE id = %%s' % sch, (pid,)) == \
        [(1, False, [])]
    assert pg.locator("[data-verif='%s']" % pid).count() == 0
    _pas(patron, firma_import, "Salaria")
    _incarca(patron, "salariati_fara_scutire.csv", _cp1250(SALARIATI_FARA_SCUTIRE), "#mig-salveaza-sal")
    pg.click("#mig-salveaza-sal")
    pg.wait_for_function("() => document.body.innerText.includes('2 salariați importați.')", timeout=20000)
    assert sql('SELECT persoane_intretinere, de_verificat FROM "%s".salariati WHERE id = %%s' % sch, (pid,)) == [(1, [])]


def test_partenerii_partial_randul_refuzat_se_arata(patron, firma_import):
    """Decizia Costin 14.10.2026 pct.2: salvarea parțială la parteneri. Pașii: situația clienților SAGA cu un CUI greșit, contul 4111
    ales -> „Un rând nu intră”, „Salvează cele 2 rânduri bune (parteneri)” -> „2 parteneri salvați.”, „Un rând nu a intrat”."""
    pg = patron.pg
    # [346, comanda Costin 8.2] partenerii intră numai dacă dau soldul contului din balanța de deschidere: 4111 = 300 + 50 (rândurile bune)
    sch = firma_import["schema"]
    sql('DELETE FROM "%s".solduri_initiale' % sch)
    sql('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (\'4111\', 350, 0, \'2026-09-30\'), '
        '(\'1012\', 0, 350, \'2026-09-30\')' % sch)
    _pas(patron, firma_import, "Solduri parteneri")
    pg.select_option("#mig-cont-part", "4111")
    csv = ("Denumire;Cod fiscal/ CNP;Neachitat final\nClient Unu SRL;RO14837428;300\nPopescu Ana;1960101078916;50\n"
           "Client Greșit SRL;14837429;70\n")
    _incarca(patron, "clienti.csv", csv.encode("utf-8"), "#mig-salveaza-part")
    t = patron.fereastra()
    assert "Un rând nu intră — celelalte se salvează" in t and "rândul 4: CUI 14837429 invalid (cifra de control)" in t, t[:2000]
    patron.captura("previzualizare")
    pg.click("#mig-salveaza-part")
    pg.wait_for_function("() => document.body.innerText.includes('2 parteneri salvați.')", timeout=20000)
    assert "Un rând nu a intrat:" in patron.fereastra()
    assert sql('SELECT cont, cui, sold_debitor FROM "%s".solduri_parteneri ORDER BY cui' % firma_import["schema"]) == [
        ("4111", "14837428", 300), ("4111", "1960101078916", 50)]
