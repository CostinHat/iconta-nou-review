# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `migr` — importurile de migrare.

  * 599 — „Importul de migrare primește fără întrebare balanța altei firme (antet «SC Firmă Probă Rulaje SRL» încărcat pe DANTE
    INTERNATIONAL SA); compară firma din fișier cu firma aleasă și cere confirmare când diferă, la toate importurile.” Fișierul e chiar al
    lui Costin (`date_test/import_saga/balanta_saga_completa.xlsx`); clasa (celelalte importuri) pe soldurile pe parteneri, iar pytest-ul
    (`core/test_lot12_migr_firma_fisier.py`) le ia pe toate nouă;
  * 425 / 426 refăcute pe descrierea lui Costin, pe același fișier: balanța completă intră cu soldurile la 1 ianuarie și rulajele (707:
    180.000,00 / 180.000,00, sold final 0; 5121: 12.000,00 D la 1 ianuarie, 28.725,00 D final), iar a doua încărcare spune că există deja
    o balanță și cere confirmarea;
  * 251 — „CSV Windows-1250 strică diacriticele”: un CSV salvat de Excel românesc (Windows-1250) se citește cu diacriticele întregi.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). CUI-urile de probă: 14399840 (DANTE
INTERNATIONAL SA) și 4221306, cu cifra de control verificată (algoritmul din CLAUDE.md). Temei: N/A — reguli de produs (comanda 12.1); cifrele
balanței: OMFP 2634/2015 anexa 1 pct.52 („Soldul debitor sau creditor al fiecărui cont se stabilește în funcție de rulajele debitoare și
creditoare ale contului respectiv, ținându-se seama de soldul de la începutul anului”)."""
import os
import sys

import pytest

from conftest import firma_noua, sql
from e2e_bloc_d import PATRON, _api

RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
FISIER_COSTIN = os.path.join(RAD, "date_test", "import_saga", "balanta_saga_completa.xlsx")
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
ANTET_COSTIN = "SC Firmă Probă Rulaje SRL"
MESAJ_599 = "Fișierul pare al altei firme: în antetul lui scrie „SC Firmă Probă Rulaje SRL”, iar firma aleasă e %s."


def confirma_firma_fisierului(pg, antet):
    """[599] Pasul contabilului după „Salvează …” pe un fișier al cărui antet numește ALTĂ firmă decât cea aleasă (fișierele de probă au
    antetul lor, „SC Firmă Probă SRL” / „SC Firmă Probă Rulaje SRL”, iar firma de test e „E2E Probă …”): întrebarea numește firma din
    fișier și cere „Da, sunt ale acestei firme”; abia după ea pornește salvarea (și, dacă firma are deja datele, întrebarea înlocuirii).
    Sursa unică a pasului pentru testele importurilor care nu probează 599 însuși (599 are pașii lui, cu „Renunță”, mai jos)."""
    pg.wait_for_selector("#caseta-atentie-activa #ca-ok", timeout=10000)
    intrebare = " ".join(pg.inner_text("#caseta-atentie-activa .ca-mesaj").split())
    assert pg.inner_text("#ca-ok").strip() == "Da, sunt ale acestei firme", intrebare
    assert intrebare.startswith("Datele din fișierul cu „%s” intră la " % antet), intrebare
    pg.click("#ca-ok")


# ── fișierele (și pentru dovezile pe firmele de test: `frontend_test/dovada/dovezi_lot12_migr.json`) ─────────────────────────────
def fisier_costin():
    """Balanța lui Costin, exact cum a încărcat-o (antetul „SC Firmă Probă Rulaje SRL”, 19 conturi la 30.09.2026)."""
    return open(FISIER_COSTIN, "rb").read()


def parteneri_altei_firme(randuri=None):
    """Situația partenerilor exportată de ALTĂ firmă: titlul, firma și CUI-ul ei deasupra tabelului. `randuri` = [(cont, debit, credit)]
    pe DANTE INTERNATIONAL SA (implicit 4111 debit 500)."""
    corp = "".join("%s;RO14399840;DANTE INTERNATIONAL SA;%s;%s\n" % r for r in (randuri or [("4111", 500, 0)]))
    return ("Situație solduri parteneri\nFirma:;SC Firmă Probă Rulaje SRL\nCUI:;RO4221306\n"
            "cont;cui;denumire;sold debitor;sold creditor\n" + corp).encode("utf-8")


def _randuri_pe_soldul_firmei(firma):
    """[346] Soldurile pe parteneri intră numai dacă dau soldul fiecărui cont de terți la data preluării
    (`solduri_parteneri_api.coerenta`: balanța de deschidere sau, fără ea, contabilitatea firmei). Rândurile care dau exact acel sold,
    ca fișierul să fie salvabil — altfel „Salvează partenerii” e inactiv și întrebarea firmei nu se mai pune."""
    from core import db, solduri_parteneri_api as sp
    with db.get_conn(firma["schema"]) as c:
        coer = sp.coerenta(c, firma["schema"], [])
    return [(x["cont"], x["sold_balanta"], 0) if x["sold_balanta"] >= 0 else (x["cont"], 0, -x["sold_balanta"]) for x in coer]


def parteneri_cp1250():
    """[251] Partenerii salvați de Excel românesc ca „CSV (separat prin virgulă)”: Windows-1250 (ă, â, î, ş, ţ cu sedilă — literele pe
    care Windows-1250 le are)."""
    return ("cont;cui;denumire;sold debitor;sold creditor\n"
            "4111;RO14399840;Brutăria Ştefan Ţară Pâine Înaltă SRL;500;0\n").encode("cp1250")


@pytest.fixture(scope="module")
def firma_m12():
    for f in firma_noua():
        # premisa, citită (nu scrisă): firma nouă vine fără metodă de stoc declarată — o cere balanța (425)
        assert sql('SELECT metoda_stoc FROM "%s".firma_profil WHERE id = 1' % f["schema"]) == [(None,)]
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


def _txt(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _randul(pg, nr):
    return " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="%s"]' % nr).all_inner_texts()).split())


# ── 599 + 425 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_599_balanta_altei_firme_cere_confirmare_si_intra_cu_cifrele_425(patron, firma_m12):
    """599, pe fișierul lui Costin: Import date -> Solduri inițiale -> balanta_saga_completa.xlsx -> sus, galben: „Fișierul pare al altei
    firme: în antetul lui scrie «SC Firmă Probă Rulaje SRL», iar firma aleasă e <firma>.” -> data 30.09.2026, metoda de stoc ->
    „Salvează soldurile” -> întrebarea „Datele din fișierul cu «SC Firmă Probă Rulaje SRL» intră la <firma>. Confirmi …?”, butonul
    principal ascuns -> „Renunță”: nimic scris -> din nou -> „Da, sunt ale acestei firme” -> „19 conturi salvate, cu soldurile la
    30.09.2026. Soldurile de la 1 ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.” 425 (cifrele, în evidență):
    707 rulaj 180.000 / 180.000, sold final 0; 5121 sold la 1 ianuarie 12.000 D, rulaje 200.000 / 183.275, sold final 28.725 D."""
    pg = patron.pg
    s, nume = firma_m12["schema"], firma_m12["nume"]
    _pas(patron, firma_m12, "Solduri ini")
    _incarca(patron, "balanta_saga_completa.xlsx", fisier_costin(), "#mig-salveaza-sold", tip=XLSX)
    av = _txt(pg, "#mig-firma-fisier")
    patron.captura("avertisment_firma")
    assert pg.locator("#mig-firma-fisier.msg-avert").count() == 1, av
    assert av.startswith(MESAJ_599 % nume), av
    # 425: rândurile previzualizării, cu soldul la 1 ianuarie și rulajele anului din fișier
    assert _randul(pg, 24) == "24 intră 707 Venituri din vânzarea mărfurilor — 180.000,00 180.000,00 0,00 0,00", _randul(pg, 24)
    assert _randul(pg, 19) == "19 intră 5121 Conturi la bănci în lei 12.000,00 D 200.000,00 183.275,00 28.725,00 0,00"
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.select_option("#mig-metoda-stoc", "cantitativ_valoric")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector("#ca-ok", timeout=10000)
    patron.captura("confirmare_firma")
    assert " ".join(pg.inner_text("#caseta-atentie-activa .ca-mesaj").split()) == (
        "Datele din fișierul cu „SC Firmă Probă Rulaje SRL” intră la %s. Confirmi că sunt ale acestei firme?" % nume)
    assert pg.inner_text("#ca-ok").strip() == "Da, sunt ale acestei firme"
    assert pg.locator("#mig-salveaza-sold").is_hidden()          # o singură acțiune activă cât confirmarea e deschisă
    pg.click("#ca-nu")
    pg.wait_for_timeout(500)
    assert sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0] == 0      # fără confirmare nu se scrie nimic
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector("#ca-ok", timeout=10000)
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('19 conturi salvate, cu soldurile la 30.09.2026. Soldurile de la 1 "
                         "ianuarie și rulajele anului au intrat ca sold inițial și sume precedente.')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT si_an_debit, rulaj_an_debit, rulaj_an_credit, sold_debitor, sold_creditor FROM "%s".solduri_initiale '
               "WHERE cont = '707'" % s) == [(0, 180000, 180000, 0, 0)]
    assert sql('SELECT si_an_debit, rulaj_an_debit, rulaj_an_credit, sold_debitor, sold_creditor FROM "%s".solduri_initiale '
               "WHERE cont = '5121'" % s) == [(12000, 200000, 183275, 28725, 0)]
    assert sql('SELECT count(*), sum(sold_debitor), sum(sold_creditor) FROM "%s".solduri_initiale' % s) == [(19, 79525, 79525)]


def test_def_426_a_doua_balanta_a_altei_firme_cere_ambele_confirmari(patron, firma_m12):
    """426 pe descrierea lui Costin („al doilea import înlocuiește balanța fără avertisment”), cu același fișier: sus, ambele avertismente
    (firma din fișier și „Firma are deja o balanță de deschidere la 30.09.2026: 19 conturi …”) -> „Înlocuiește balanța” -> întâi
    confirmarea firmei, apoi a înlocuirii („Înlocuiesc balanța”) -> „Balanța veche (19 conturi, la 30.09.2026) a fost înlocuită.”"""
    pg = patron.pg
    s, nume = firma_m12["schema"], firma_m12["nume"]
    if not sql('SELECT count(*) FROM "%s".solduri_initiale' % s)[0][0]:
        pytest.skip("rulat singur: balanța de înlocuit o scrie testul 599 de mai sus")
    _pas(patron, firma_m12, "Solduri ini")
    _incarca(patron, "balanta_saga_completa.xlsx", fisier_costin(), "#mig-salveaza-sold", tip=XLSX)
    assert _txt(pg, "#mig-firma-fisier").startswith(MESAJ_599 % nume)
    assert _txt(pg, "#mig-inlocuire").startswith("Firma are deja o balanță de deschidere la 30.09.2026: 19 conturi, debit 79.525,00 lei, "
                                                 "credit 79.525,00 lei.")
    patron.captura("doua_avertismente")
    pg.fill("#mig-data-bal", "2026-09-30")
    pg.click("#mig-salveaza-sold")
    pg.wait_for_selector("#ca-ok", timeout=10000)
    assert pg.inner_text("#ca-ok").strip() == "Da, sunt ale acestei firme"
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('#ca-ok') || {}).innerText === 'Înlocuiesc balanța'", timeout=10000)
    patron.captura("confirmare_inlocuire")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.body.innerText.includes('Balanța veche (19 conturi, la 30.09.2026) a fost înlocuită.')",
                         timeout=30000)
    assert sql('SELECT count(*), sum(sold_debitor) FROM "%s".solduri_initiale' % s) == [(19, 79525)]


# ── 599, clasa: celelalte importuri (aici soldurile pe parteneri; toate nouă în pytest) ────────────────────────────────────────────
def test_def_599_partenerii_altei_firme_cer_confirmarea(patron, firma_m12):
    """599, al doilea import: Import date -> Solduri parteneri -> fișierul cu „Firma: SC Firmă Probă Rulaje SRL / CUI: RO4221306”
    deasupra tabelului -> „Fișierul pare al altei firme: în antetul lui scrie CUI 4221306 («SC Firmă Probă Rulaje SRL»), iar firma
    aleasă, <firma>, are CUI <cui>.” -> „Salvează partenerii” -> întrebarea firmei -> „Renunță”: niciun partener scris."""
    pg = patron.pg
    s, nume = firma_m12["schema"], firma_m12["nume"]
    cui = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma_m12["tenant_id"],))[0][0]
    _pas(patron, firma_m12, "Solduri parteneri")
    randuri = _randuri_pe_soldul_firmei(firma_m12)
    if not randuri:
        pytest.skip("rulat singur: soldurile conturilor de terți le scrie balanța din testul 599 de mai sus")
    _incarca(patron, "parteneri_alta_firma.csv", parteneri_altei_firme(randuri), "#mig-salveaza-part")
    av = _txt(pg, "#mig-firma-fisier")
    patron.captura()
    assert av.startswith("Fișierul pare al altei firme: în antetul lui scrie CUI 4221306 („SC Firmă Probă Rulaje SRL”), iar firma "
                         "aleasă, %s, are CUI %s." % (nume, cui)), av
    pg.click("#mig-salveaza-part")
    pg.wait_for_selector("#ca-ok", timeout=10000)
    assert pg.inner_text("#ca-ok").strip() == "Da, sunt ale acestei firme"
    pg.click("#ca-nu")
    pg.wait_for_timeout(500)
    assert sql('SELECT count(*) FROM "%s".solduri_parteneri' % s)[0][0] == 0


def test_def_599_fisierul_firmei_alese_nu_cere_confirmarea(patron, firma_m12):
    """Fișierul cu firma ALEASĂ în antet, scrisă altfel (prefixul „S.C.”, „S.R.L.”, litere mici): niciun avertisment, nicio întrebare."""
    pg = patron.pg
    nume = firma_m12["nume"]
    propriu = nume[:-len(" SRL")] if nume.endswith(" SRL") else nume
    continut = ("Situație solduri parteneri\nS.C. %s S.R.L.\ncont;cui;denumire;sold debitor;sold creditor\n"
                "4111;RO14399840;DANTE INTERNATIONAL SA;500;0\n" % propriu.lower()).encode("utf-8")
    _pas(patron, firma_m12, "Solduri parteneri")
    _incarca(patron, "parteneri_firma_aleasa.csv", continut, "#mig-salveaza-part")
    patron.captura()
    assert pg.locator("#mig-firma-fisier").count() == 0
    assert "pare al altei firme" not in patron.fereastra()


# ── 251 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_251_csv_windows_1250_pastreaza_diacriticele(patron, firma_m12):
    """251 „CSV Windows-1250 strică diacriticele”: Import date -> Solduri parteneri -> CSV salvat în Windows-1250 -> previzualizarea arată
    „Brutăria Ştefan Ţară Pâine Înaltă SRL” întreg, fără „�” și fără „Ä”."""
    pg = patron.pg
    _pas(patron, firma_m12, "Solduri parteneri")
    _incarca(patron, "parteneri_windows1250.csv", parteneri_cp1250(), "#mig-salveaza-part")
    patron.captura()
    rand = " ".join(pg.inner_text(".mig-prev tbody").split())
    assert "Brutăria Ştefan Ţară Pâine Înaltă SRL" in rand, rand
    assert "�" not in rand and "Ä" not in rand


# ── grupa 3: cifrele exacte după import (384 cote, 359 amortizare) și fluxul asociați -> notă -> D205 (431) ────────────────────────
CNP_A, CNP_B = "1800101400016", "2850202400023"      # cifra de control verificată (algoritmul din CLAUDE.md)


def asociati_60_40():
    return ("Nume;CNP;Cota\nPOPESCU ION;%s;60\nIONESCU MARIA;%s;40\n" % (CNP_A, CNP_B)).encode("utf-8")


def mijloace_cu_amortizare():
    return ("Cod;Denumire;Valoare intrare;Data PIF;Durata luni;Metoda;Cont imobilizare;Cont amortizare;Amortizare\n"
            "MF1;Laptop;6000;15.03.2024;36;liniara;2141;2814;3300\n"
            "MF2;Imprimanta;3600;01.06.2024;36;liniara;2141;2814;1800\n").encode("utf-8")


@pytest.fixture(scope="module")
def firma_g3():
    for f in firma_noua():
        s = f["schema"]
        # D205 cere declarantul și adresa domiciliului fiscal înaintea oricărui alt refuz (ca în e2e_lot10_dividende.f6)
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"],   # pe ruta ecranului Date firmă
                     {"declarant_nume": "POPESCU", "declarant_prenume": "ION", "declarant_functie": "ADMINISTRATOR",
                      "adresa": "Str. Probei 431", "oras": "București", "judet": "B"})
        assert st == 200 and r.get("ok") is not False, (st, r)
        # date-de-pornire: soldul inițial al lui 117 (rezultatul reportat la 31.12.2024) din care se împart dividendele — un singur rând
        sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) '
            "VALUES ('117', 'Rezultatul reportat', 0, 34650, '2024-12-31')" % s)
        yield f


def test_def_384_cotele_valide_intra_cu_cifrele_exacte(patron, firma_g3):
    """384 (grav), cifrele după import: Import date -> Asociați -> POPESCU ION 60% + IONESCU MARIA 40% (CNP-uri valide) -> banda „total
    cote: ✓ 100%” -> „Salvează asociații” -> „2 asociați salvați.” În firmă: 60 și 40, totalul 100 (cotele care intră, numai ele)."""
    pg = patron.pg
    s = firma_g3["schema"]
    _pas(patron, firma_g3, "Asocia")
    _incarca(patron, "asociati.csv", asociati_60_40(), "#mig-salveaza-asoc")
    banda = " ".join(pg.inner_text(".mig-coer").split())
    patron.captura("previzualizare")
    assert "total cote: ✓ 100%" in banda, banda
    pg.click("#mig-salveaza-asoc")
    pg.wait_for_function("() => document.body.innerText.includes('2 asociați salvați.')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT nume, cnp, cota FROM "%s".asociati ORDER BY cota DESC' % s) == [("POPESCU ION", CNP_A, 60), ("IONESCU MARIA", CNP_B, 40)]
    assert sql('SELECT sum(cota) FROM "%s".asociati' % s) == [(100,)]


def test_def_359_amortizarea_cumulata_intra_cu_cifrele_exacte(patron, firma_g3):
    """359 (grav), cifrele după import: Import date -> Mijloace fixe -> fișierul cu coloana „Amortizare” (3.300 și 1.800) -> „Amortizare
    preluată”: 3.300,00 lei și 1.800,00 lei -> „Salvează mijloacele fixe” -> în registru: Laptop 6.000 / amortizare preluată 3.300,
    Imprimanta 3.600 / 1.800 (decizia A.1: amortizarea continuă de la cifra din fișier; CF art.28 alin.(6) — rata metodei)."""
    pg = patron.pg
    s = firma_g3["schema"]
    _pas(patron, firma_g3, "Mijloace fixe")
    _incarca(patron, "mf.csv", mijloace_cu_amortizare(), "#mig-salveaza-mf")
    t = " ".join(pg.inner_text(".mig-prev tbody").split())
    patron.captura("previzualizare")
    assert "3.300,00 lei" in t and "1.800,00 lei" in t, t
    pg.click("#mig-salveaza-mf")
    pg.wait_for_function("() => document.body.innerText.includes('2 mijloace fixe importate.')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT cod, valoare, amortizare_preluata FROM "%s".mijloace_fixe ORDER BY cod' % s) == [("MF1", 6000, 3300), ("MF2", 3600, 1800)]


def test_def_431_asociatii_importati_nota_validata_d205_valida_pe_duk(patron, firma_g3):
    """431, cap-coadă: asociații din importul de mai sus (60 / 40) -> Operațiuni speciale -> Asociați -> dividend 10.000 lei distribuit pe
    20.05.2025, neplătit -> nota (117 = 457; 457 = 446) -> validarea notei (`jurnal_api.valideaza`, regula ecranului Registru jurnal) ->
    Declarații -> D205 2025 -> „Validat cu DUKIntegrator (validatorul oficial ANAF rulat local), fără erori.”; XML-ul: POPESCU ION
    divid_D 6000, imp1 600; IONESCU MARIA 4000 / 400 (10% pe 2025: OUG 156/2024 — CF art.97 alin.(7) „se impozitează cu o cotă de 10%”;
    16% numai pentru dividendele distribuite de la 01.01.2026, Legea 141/2025 art.VII alin.(1) lit.c); OPANAF 179/2022 anexa 1 cap.II
    pct.9: distribuitele neplătite se cuprind în declarația perioadei în care s-a aprobat distribuirea)."""
    from conftest import alege_perioada, alege_tipul
    from core import db as _cdb, jurnal_api
    pg = patron.pg
    s = firma_g3["schema"]
    if sql('SELECT count(*) FROM "%s".asociati' % s)[0][0] != 2:
        pytest.skip("rulat singur: asociații îi importă testul 384 de mai sus")
    patron.firma(firma_g3["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    pg.locator("button[data-op='asociati']").click()
    pg.wait_for_selector("#op-trimite", timeout=10000)
    pg.select_option("#op-operatie", "dividend")
    pg.fill("#op-data", "2025-05-20")
    pg.fill("#op-brut", "10000")
    pg.fill("#op-numar_hotarare", "3")
    pg.fill("#op-data_hotarare", "2025-05-15")
    pg.select_option("#op-interimar", "0")
    pg.select_option("#op-cu_plata", "false")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=20000)
    patron.captura("nota")
    ids = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE status <> %%s ORDER BY id' % s, ("validata",))]
    assert ids, "nota de dividende n-a fost scrisă"
    with _cdb.get_conn(s) as c:
        for i in ids:
            v = jurnal_api.valideaza(c, s, i)
            assert v and v.get("ok"), (i, v)
        c.commit()
    patron.firma(firma_g3["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector("#dec-tip", timeout=20000)
    alege_tipul(pg, "d205")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, 2025)
    pg.click("#dec-continua")
    pg.wait_for_selector(".fereastra:last-of-type .dec-eroare, .fereastra:last-of-type details.dec-xml", timeout=90000)
    assert not pg.query_selector(".fereastra:last-of-type .dec-eroare"), patron.fereastra()[:1500]
    assert "Validat cu DUKIntegrator (validatorul oficial ANAF rulat local), fără erori." in patron.fereastra()
    pg.click(".fereastra:last-of-type details.dec-xml > summary:has-text('Vezi XML-ul generat')")
    xml = pg.inner_text(".fereastra:last-of-type details.dec-xml[open] .dec-xml-pre")
    patron.captura("d205")
    assert 'den1="POPESCU ION"' in xml and 'divid_D="6000" divid_P="0" baza1="6000" imp1="600"' in xml, xml
    assert 'den1="IONESCU MARIA"' in xml and 'divid_D="4000" divid_P="0" baza1="4000" imp1="400"' in xml, xml


# ── fișierele dovezilor pe firmele de test (`frontend_test/dovada/dovezi_lot12_migr.json`; numai previzualizare, nimic nu se salvează) ──
CNP_DOVADA = "1800101221144"     # cifra de control verificată (e2e_lot82 / e2e_lot91)


def asociati_cu_respins():
    """[384] Pop Ion 30% (CNP valid) + Ion Pop 70% (CNP cu cifra de control greșită) — conținutul din e2e_lot91."""
    return ("Nume;CNP;Cota\nPop Ion;%s;30\nIon Pop;1800101221145;70\n" % CNP_DOVADA).encode("utf-8")


def asociati_90():
    """[366] opt asociați care dau 90% — conținutul din e2e_lot82 (CNP-uri cu cifra de control calculată)."""
    from e2e_lot82 import cnp_cu_control
    return ("Nume;CNP;Cota\n" + "".join("Asociat %d;%s;%s\n" % (i, cnp_cu_control("1800101221%02d" % (10 + i)), "20" if i < 4 else "2.5")
                                        for i in range(8))).encode("utf-8")


def mijloace_conturi_gresite():
    """[362] conturi inversate, teren cu durată, amenajare de teren pe 10 / 5 ani — conținutul din e2e_lot91."""
    return ("Cod;Denumire;Valoare intrare;Data PIF;Durata luni;Metoda;Cont imobilizare;Cont amortizare\n"
            "MF1;Strung inversat;5000;15.03.2024;36;liniara;2813;2131\n"
            "MF2;Teren;50000;10.01.2020;60;liniara;2111;\n"
            "MF3;Amenajare teren;12000;10.01.2024;120;liniara;2112;2811\n"
            "MF4;Alee;6000;10.01.2024;60;liniara;2112;2811\n").encode("utf-8")


def articole_dublate():
    """[385] același articol pe două rânduri — conținutul din e2e_lot91."""
    return "Denumire;UM;Cantitate;Pret;Cont stoc\nMarfa valida;buc;10;2;371\nMarfa valida;buc;3;2;371\n".encode("utf-8")


def salariat_cnp_excel():
    """[388] CNP-ul transformat de Excel în 2,90022E+12 — conținutul din e2e_lot91."""
    return "Nume;Prenume;CNP;Functie baza;Norma;Salariu brut\nPop;Ion;2,90022E+12;Da;8;5000\n".encode("utf-8")


def salariat_cor_lung():
    """[349] salariatul cu denumirea COR lungă (214441) — conținutul din e2e_lot91."""
    return ("Nume;Prenume;CNP;Functie;Cod COR;Functie baza;Data angajarii;Norma;Salariu brut\n"
            "Pop;Ion;%s;Specialist;214441;Da;01.03.2024;8;5000\n" % CNP_DOVADA).encode("utf-8")


def balanta_5121_creditor():
    """[392] 5121 cu sold creditor — conținutul din e2e_lot91."""
    return "Cont;Denumire;Sold final debitor;Sold final creditor\n5121;Banca;0;20000\n1012;Capital;20000;0\n".encode("utf-8")


# ── C116 (găsită de pachetul `prod`): a doua reevaluare folosește rezerva din reevaluare a activului ─────────────────────────────────
@pytest.fixture()
def firma_c116():
    for f in firma_noua():
        yield f


def test_def_c116_a_doua_reevaluare_scade_intai_rezerva_activului(patron, firma_c116):
    """C116. Pașii: Mijloace fixe -> „Utilaj de probă MFC116” (6.000 lei, PIF în luna curentă: amortizarea cumulată e 0) -> Acțiuni ->
    valoarea justă 7.000 -> „Reevaluează”: „2131 = 105 · 1.000,00 lei” -> nota validată (reevaluarea se aplică pe registru) -> valoarea
    justă 6.500 -> „Reevaluează”: „105 = 2131 · 500,00 lei” — descreșterea scade întâi rezerva activului, „cu minimul dintre valoarea acelei
    rezerve și valoarea descreșterii” (OMFP 1802/2014 pct.111 alin.(2)). Înainte: „655 = 2131 · 500,00 lei” (rezerva luată 0)."""
    from e2e_bloc_e import AZI, _mf, _mijloace
    from e2e_lot11_j2 import _confirmarea, _ultima_nota, fereastra_mf
    from core import db as _cdb, jurnal_api, uc_tenants
    pg = patron.pg
    f = firma_c116
    s = f["schema"]
    _mf(f, "MFC116", "6000", 60, AZI.replace(day=1).isoformat())
    _mijloace(patron, f)
    fereastra_mf(pg, "MFC116", "reevaluare", AZI.isoformat(), 7000)   # [lotul 13, 673] fereastra reevaluării
    assert _confirmarea(pg) == ["2131 = 105 · 1.000,00 lei"], _confirmarea(pg)
    patron.captura("prima")
    nid = _ultima_nota(f)
    with _cdb.get_conn(s) as c:      # validarea notei: drumul lui `jurnal_valideaza` (regula validării + aplicarea pe registru)
        v = jurnal_api.valideaza(c, s, nid)
        assert v and v.get("ok"), v
        assert uc_tenants._aplica_reevaluarea(c, s, nid) is True
        c.commit()
    _mijloace(patron, f)
    fereastra_mf(pg, "MFC116", "reevaluare", AZI.isoformat(), 6500)
    linii = _confirmarea(pg)
    patron.captura("a_doua")
    assert linii == ["105 = 2131 · 500,00 lei"], linii
    assert sql('SELECT cont_debit, cont_credit, suma FROM "%s".inregistrari_linii WHERE inregistrare_id = %%s' % s,
               (_ultima_nota(f),)) == [("105", "2131", 500)]
