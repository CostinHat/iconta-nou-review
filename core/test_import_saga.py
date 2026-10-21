# -*- coding: utf-8 -*-
"""core/test_import_saga.py — importul din SAGA (comanda Costin 14.10.2026, verbatim în DECIZII „Importul din SAGA”): C21–C25,
codarea Windows-1250 (C27), clasa pe toate parserele și pe modelele de salvare, plus garda care face citirea paralelă imposibilă.

Fișierele sunt INVENTATE (date de probă, niciun dat al vreunui client), cu antetele luate din manualul SAGA C, salvat în
`anaf_surse/` (capitolul e numit pe linie). Unde manualul nu dă antetul exact al exportului (balanța de verificare), antetul e
compus din termenii manualului („Solduri finale”, „Total sume”, „Debit inițial an”, „Debit precedent”) — limita e în raport.
TEMEI: N/A — citirea fișierelor de import (tooling); regulile fiscale atinse (CNP, CUI) au algoritmul oficial deja în cod.
"""
import ast
import datetime
import glob
import json
import os

import pytest

from core import import_tabel as it
from core import solduri_api, solduri_parteneri_api as sp, salariati_import_api as si
from core import mijloace_fixe_import_api as mf, istoric_declaratii_import_api as ist, articole_import_api as art
from core.salariati_import_api import valideaza_cnp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNP_OK = "1960101078916"          # cifra de control verificată (algoritmul din CLAUDE.md: (12 cifre · 279146358279) mod 11)
CNP_GRESIT = "1960101078911"      # aceeași bază, cifra de control greșită


def _cp1250(s):
    """Textul cum îl scrie un program în Windows-1250: codarea are numai ş / ţ cu SEDILĂ (nu ș / ț cu virgulă)."""
    return s.translate(str.maketrans("șțȘȚ", "şţŞŢ")).encode("cp1250")


def test_cnp_urile_de_proba_sunt_cele_declarate():
    assert valideaza_cnp(CNP_OK) == (True, "ok")
    assert valideaza_cnp(CNP_GRESIT) == (False, "cifra de control greșită")


# ── C21 / C27: balanța de verificare completă, Windows-1250, antet pe două rânduri, titluri, totaluri, sintetic + analitice ──────
# Termenii coloanelor: manualul SAGA, „Balante” (anaf_surse/saga_manual_topic52_balante.txt: balanța sintetică / analitică,
# „Soldurile iniţiale şi finale”) și „Preluare date contabile” (…topic12…: „Total Sume debitoare/creditoare”).
BALANTA_SAGA = (
    "Balanţă de verificare analitică;;;;;;;;\n"
    "SC Firmă Probă SRL;;;;;;;;\n"
    "Perioada: 01.01.2026 - 30.09.2026;;;;;;;;\n"
    "Simbol cont;Denumirea contului;Solduri iniţiale an;;Total sume;;Solduri finale;;\n"
    ";;Debit;Credit;Debit;Credit;Debit;Credit\n"
    "1012;Capital subscris vărsat;0;200;0;200;0;200\n"
    "401;Furnizori;0;50;30;130;0;100\n"
    "401.00001;Furnizor Şerban;0;30;10;80;0;70\n"
    "401.00002;Furnizor Ţăndărei;0;20;20;50;0;30\n"
    "5311;Casa în lei;250;0;900;600;300;0\n"
    "Total clasa 4;;;;;;;;\n"
    "TOTAL GENERAL;;250;250;930;930;300;300\n"
)


def test_def_c21_balanta_completa_se_importa_cu_soldurile_finale():
    """C21: o balanță cu mai multe perechi debit/credit se citea cu PRIMA pereche (soldurile inițiale), echilibrată, deci tăcut.
    Acum: perechea „Solduri finale”, rândurile de total ignorate și numărate, sinteticul 401 înlocuit de analiticele lui."""
    d = solduri_api.extrage_balanta_detaliat(_cp1250(BALANTA_SAGA), "balanta_saga.csv")
    assert [(r["cont"], r["debit"], r["credit"]) for r in d["randuri"]] == [
        ("1012", 0.0, 200.0), ("401.00001", 0.0, 70.0), ("401.00002", 0.0, 30.0), ("5311", 300.0, 0.0)]   # sold FINAL, nu inițial
    assert d["coloane"] == {"cont": "Simbol cont", "debit": "Solduri finale Debit", "credit": "Solduri finale Credit"}
    assert d["ignorate"] == ["Total clasa 4", "TOTAL GENERAL"]
    assert d["sintetice_inlocuite"] == ["401"]
    assert d["randuri"][1]["denumire"] == "Furnizor Şerban"                      # C27: diacriticele intacte, nu „�”
    ok, td, tc, _ = solduri_api.verifica_echilibru(d["randuri"])
    assert ok and td == tc == 300.0


def test_c21_mai_multe_perechi_fara_sold_final_se_refuza_numit():
    csv = "Cont;Denumire;Rulaj debit;Rulaj credit;Total sume debit;Total sume credit\n5311;Casa;10;5;100;50\n".encode()
    with pytest.raises(it.FisierNecitit) as e:
        solduri_api.extrage_balanta(csv, "b.csv")
    assert str(e.value) == 'Balanța din fișierul «b.csv» are mai multe coloane de debit («Rulaj debit», «Total sume debit») și de credit («Rulaj credit», «Total sume credit»), iar soldul final nu se poate deosebi neechivoc de celelalte. Numește perechea soldurilor finale „Sold final debitor” / „Sold final creditor” (sau „Solduri finale” deasupra lui „Debit / Credit”) și încarcă fișierul din nou.'   # [lotul 10, 425] celelalte perechi se citesc acum (sold inițial, rulaje); textul nu mai spune „numai soldurile finale”


def test_c21_sinteticul_care_nu_se_potriveste_cu_analiticele_se_refuza():
    csv = ("Cont;Denumire;Sold final debitor;Sold final creditor\n401;Furnizori;0;100\n401.1;F1;0;60\n401.2;F2;0;30\n"
           "5311;Casa;100;0\n").encode()
    with pytest.raises(it.FisierNecitit) as e:
        solduri_api.extrage_balanta(csv, "b.csv")
    assert str(e.value) == 'Contul 401 are în fișier sold final net -100,00 lei, iar analiticele lui (401.1, 401.2) însumează -90,00 lei. Balanța amestecă sintetice și analitice care nu se potrivesc — exportă balanța numai cu analitice (sau numai sintetică) și încarcă-o din nou.'


def test_contul_de_doua_ori_se_refuza_numit_nu_la_scriere():
    """`solduri_initiale(cont)` și `solduri_parteneri(cont, cui)` sunt UNIQUE în bază (GARZI cat.1): un fișier cu același cont / partener
    de două ori se refuză la citire, numit — nu cu o eroare de bază la salvare. MUTAȚIA: verificarea scoasă -> ROȘU."""
    csv = "cont,denumire,sold debitor,sold creditor\n5311,Casa,100,0\n5311,Casa,50,0\n1012,Capital,0,150\n".encode()
    with pytest.raises(it.FisierNecitit) as e:
        solduri_api.extrage_balanta(csv, "b.csv")
    assert str(e.value).startswith("Contul 5311 apare de mai multe ori în balanță.")
    csv = "Cont;Cod fiscal;Denumire;Sold debitor;Sold creditor\n4111;14837428;A;10;0\n4111;RO14837428;A;5;0\n".encode()
    with pytest.raises(it.FisierNecitit) as e:
        sp.extrage(csv, "p.csv")
    assert str(e.value) == 'Același partener apare de două ori pe același cont: 4111 / 14837428 (rândurile 2 și 3). Un partener are un singur sold pe un cont; adună rândurile în fișier și încarcă-l din nou.'


def test_balanta_simpla_de_deschidere_ramane_cum_era():
    csv = "cont,denumire,sold debitor,sold creditor\n1012,Capital,0,100\n5311,Casa,100,0\n".encode()
    assert [(r["cont"], r["debit"], r["credit"]) for r in solduri_api.extrage_balanta(csv, "m.csv")] == [
        ("1012", 0.0, 100.0), ("5311", 100.0, 0.0)]


# ── C22: data balanței ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c22_data_balantei_e_ceruta():
    randuri = [{"cont": "1012", "debit": 0, "credit": 100}, {"cont": "5311", "debit": 100, "credit": 0}]
    with pytest.raises(ValueError) as e:
        solduri_api.importa(None, randuri, None)               # refuzul vine înainte de orice scriere (conn neatins)
    assert str(e.value).startswith("Data balanței lipsește")
    with pytest.raises(ValueError) as e:
        solduri_api.data_balantei("2026-12-31", azi=datetime.date(2026, 10, 14))
    assert str(e.value) == 'Data balanței (31.12.2026) e în viitor: soldurile se preiau la o dată încheiată.'
    assert solduri_api.data_balantei("2026-09-30", azi=datetime.date(2026, 10, 14)) == "2026-09-30"


def test_c22_clasa_stocul_initial_nu_primeste_data_de_azi():
    with pytest.raises(ValueError) as e:
        art.importa(None, "s", [{"denumire": "Faina", "um": "kg", "cantitate": 1, "pret": 2}], data_sold=None)
    assert str(e.value).startswith("Data stocului inițial nu se cunoaște")


# ── C27: codarea ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_c27_windows_1250_recunoscut_si_utf16():
    assert it.decodeaza(_cp1250("Casă şi ţară")) == ("Casă şi ţară", "windows-1250")
    assert it.decodeaza("Casă și țară".encode("utf-8")) == ("Casă și țară", "utf-8")
    assert it.decodeaza("﻿Casă".encode("utf-8")) == ("Casă", "utf-8")
    assert it.decodeaza("Casă".encode("utf-16")) == ("Casă", "utf-16")


def test_c27_codarea_care_nu_se_poate_citi_sigur_se_refuza_cu_mesaj():
    with pytest.raises(it.FisierNecitit) as e:
        it.decodeaza(b"cont;denumire\n5311;Cas\xa4\xb6\xbe\n", "x.csv")      # nu e UTF-8, iar ca 1250 dă „¤¶ľ” — nu sunt litere RO
    assert str(e.value) == 'Fișierul «x.csv» nu se poate citi fără să se strice diacriticele: nu e UTF-8, iar ca Windows-1250 rândul 2 ar conține „¤¶”, care nu sunt litere românești. Salvează exportul ca „CSV UTF-8” (sau XLSX) și încarcă-l din nou.'


# ── coloanele: cuvinte întregi, ambiguitate refuzată ───────────────────────────────────────────────────────────────────────────
def test_coloana_pe_cuvinte_intregi_nu_pe_subsir():
    antet = [it.norm(h) for h in ("Data angajării", "Tip", "An", "Nume")]
    assert it.coloana(antet, ("=an", "anul")) == 2                                  # „an” nu mai prinde „angajării”
    assert it.coloana(antet, ("angaj*",)) == 0                                      # prefixul cerut explicit, cu `*`


def test_doua_coloane_la_fel_de_potrivite_se_refuza_numit():
    antet = it._antet(["Cont bancar", "Cont card"])
    with pytest.raises(it.ColoaneAmbigue) as e:
        it.coloana(antet, ("cont",), camp="contul de salariu")
    assert str(e.value) == 'Coloanele «Cont bancar», «Cont card» se potrivesc toate la „contul de salariu” — nu aleg una la întâmplare. Lasă în fișier una singură sau redenumește-le.'


def test_xls_se_citeste():
    """XLS (Excel 97–2003) — formatul de export al SAGA („exportă datele din ecranul curent, în format XLS(Excel), CSV, TXT sau XML”,
    anaf_surse/saga_manual_topic5_consideratii_generale.txt). Fișierele de probă (inventate) sunt în `date_test/import_saga/`,
    scrise cu xlwt într-un mediu separat; aplicația le citește cu xlrd (ca extrasele bancare). Data din celulă rămâne dată."""
    cale = os.path.join(RAD, "date_test", "import_saga")
    d = solduri_api.extrage_balanta_detaliat(open(os.path.join(cale, "balanta_saga.xls"), "rb").read(), "balanta.xls")
    assert [(r["cont"], r["debit"], r["credit"]) for r in d["randuri"]] == [
        ("1012", 0.0, 200.0), ("401.00001", 0.0, 70.0), ("401.00002", 0.0, 30.0), ("5311", 300.0, 0.0)]
    assert d["coloane"]["debit"] == "Solduri finale Debit" and d["randuri"][1]["denumire"] == "Furnizor Şerban"
    r = mf.extrage(open(os.path.join(cale, "mijloace_fixe_saga.xls"), "rb").read(), "mf.xls")
    assert [(x["cod"], x["valoare"], x["data_pif"], x["cont_imobilizare"]) for x in r] == [("100", 6000.0, "2024-03-15", "2131")]


# ── parteneri: „Situație clienți / furnizori” SAGA ────────────────────────────────────────────────────────────────────────────
# Coloanele: anaf_surse/saga_manual_topic60_situatii_clienti_furnizori.txt („Neachitat inițial”, „Total intrări”, „Total
# plăți/ încasări”, „Neachitat final”, „Neachitat la zi”) + anaf_surse/saga_manual_topic17_terti.txt („Denumire”, „Cod fiscal/ CNP”).
SITUATIE_CLIENTI = ("Denumire;Cod fiscal/ CNP;Neachitat inițial;Total intrări;Total plăți/ încasări;Neachitat final;Neachitat la zi\n"
                    "Client Unu SRL;RO14837428;100;500;300;300;300\n"
                    "Popescu Ana;%s;0;50;0;50;50\n"
                    "Client Achitat SRL;14837428;100;0;100;0;0\n"
                    "Total;;200;550;400;350;350\n" % CNP_OK)


def test_parteneri_situatia_clientilor_saga_cu_contul_ales():
    r = sp.extrage(SITUATIE_CLIENTI.encode("utf-8"), "clienti.csv", cont_implicit="4111")
    assert [(x["cont"], x["cui"], x["denumire"], x["debit"], x["credit"]) for x in r] == [
        ("4111", "14837428", "Client Unu SRL", 300.0, 0.0), ("4111", CNP_OK, "Popescu Ana", 50.0, 0.0)]   # neachitatul FINAL
    erori, _ = sp.verifica_randuri(r)
    assert erori == [], erori                                                     # CNP valid = identificator de persoană fizică


def test_parteneri_fara_coloana_cont_si_fara_cont_ales_se_refuza():
    with pytest.raises(it.FisierNecitit) as e:
        sp.extrage(SITUATIE_CLIENTI.encode("utf-8"), "clienti.csv")
    assert str(e.value) == 'Fișierul «clienti.csv» n-are coloana „Cont”. Alege din listă contul partenerilor din fișier (4111 — situația clienților, 401 — situația furnizorilor) și încarcă-l din nou.'


def test_parteneri_furnizori_soldul_pe_credit():
    csv = "Denumire;Cod fiscal/ CNP;Neachitat final\nFurnizor SRL;RO14837428;120,50\n".encode("utf-8")
    assert [(x["debit"], x["credit"]) for x in sp.extrage(csv, "f.csv", cont_implicit="401")] == [(0.0, 120.5)]


def test_parteneri_cnp_gresit_e_refuzat_cu_cheia_cnp():
    erori, _ = sp.verifica_randuri([{"cont": "4111", "cui": CNP_GRESIT, "denumire": "X", "debit": 1, "credit": 0}])
    # pe structură: regula și identificatorul respins; mesajul îl numește CNP (nu „CUI”) — începutul lui, nu textul întreg
    assert erori and (erori[0]["regula"], erori[0]["cui"]) == ("cui_invalid", CNP_GRESIT) and erori[0]["mesaj"].startswith("CNP ")


# ── salariați: ecranul Salariați SAGA (anaf_surse/saga_manual_topic25_salariati.txt) ─────────────────────────────────────────
SALARIATI_SAGA = ("Cod;Nume;Prenume;Punct de lucru;Funcție;Data angajării;Tip;Funcție baza;Norma pe zi;Ore pe lună;Salariu brut;"
                  "Salariu orar;CNP;Județ;Casa de sănătate;Cont card;Scutit contribuție minimă\n"
                  "000001;Popescu;Ana;Sediu;Economist;15.01.2024;Permanent;Da;8;168;6000;0;%s;Bihor;CAS Cluj;"
                  "RO49 AAAA 1B31 0075 9384 0000;Nu\n"
                  "000002;Ionescu;Radu;Sediu;Vânzător;01.03.2025;Permanent;Nu;4;84;3000;0;2900215410011;Cluj;CJ;;Nu\n" % CNP_OK)


def test_salariati_antetele_saga():
    r = si.extrage(_cp1250(SALARIATI_SAGA), "salariati.csv")
    a, b = r
    assert (a["data_angajare"], a["tip_norma"], a["ore_zi"], a["functie_baza"]) == ("2024-01-15", "intreaga", 8.0, True)
    assert (b["tip_norma"], b["ore_zi"], b["functie_baza"]) == ("partiala", 4.0, False)   # „Norma pe zi” = 4 -> parțială, 4 ore
    assert a["judet_casa"] == "CJ" and b["judet_casa"] == "CJ"          # casa de sănătate, nu județul adresei; „CAS Cluj” -> CJ
    assert a["iban"] == "RO49AAAA1B31007593840000"                       # „Cont card”
    assert si.verifica_randuri(r) == []


def test_def_c23_iban_trece_prin_modelul_de_salvare():
    """C23: `SalariatRand` n-avea `iban` — FastAPI arunca câmpul, IBAN-ul importat se pierdea la salvare."""
    import main
    rand = si.extrage(_cp1250(SALARIATI_SAGA), "s.csv")[0]
    assert main.SalariatRand(**rand).model_dump()["iban"] == "RO49AAAA1B31007593840000"


def test_salariati_norma_zero_ore_pe_luna_se_refuza_numit():
    csv = ("Nume;Prenume;CNP;Norma pe zi;Ore pe lună;Salariu brut;Funcție baza;Scutit contribuție minimă;Casa de sănătate\n"
           "Pop;Ion;%s;0;80;3000;Da;Nu;CJ\n" % CNP_OK).encode("utf-8")
    r = si.extrage(csv, "s.csv")
    assert r[0]["ore_zi"] == 0                                             # „Ore pe lună” nu devine ore pe zi
    assert [e["regula"] for e in si.verifica_randuri(r)] == ["norma_ore_luna"]


def test_salariati_cnp_valid_din_cerere_nu_mai_e_crezut():
    er = si.verifica_randuri([{"nume": "X", "cnp": CNP_GRESIT, "cnp_valid": True, "tip_norma": "intreaga", "ore_zi": 8,
                               "functie_baza": True, "scutit_contrib_minim": False, "salariu_brut": 5000}])
    assert [e["regula"] for e in er] == ["cnp_invalid"]


# ── mijloace fixe: ecranul Imobilizări SAGA (anaf_surse/saga_manual_topic34_imobilizari.txt) ─────────────────────────────────
MF_SAGA = ("Nr.inv.;Denumire;Nr.document;Gestiune;Cod clasă;Data intrare;Valoare intrare;Valoare inventar;Dur.luni;Tip amortizare;"
           "Val. ramasa;Dur. ramasă;Amort. lunara;Amort. inreg.;Necorp.;Cont;Cont amortizare;Cont cheltuiala\n"
           "100;Laptop;F12;Sediu;2.2.9;15.03.2024;6000;6000;36;liniara;2000;12;166,67;4000;;2131;2813;6811\n"
           "101;Autoturism;F13;Sediu;2.3.2.1.1;01.06.2023;80000;80000;60;accelerata;0;0;0;0;;;2813;6811\n")


def test_mijloace_fixe_antetele_saga():
    r = mf.extrage(_cp1250(MF_SAGA), "mf.csv")
    a = r[0]
    assert (a["cod"], a["valoare"], a["dnf_luni"], a["data_pif"], a["cont_imobilizare"], a["cont_amortizare"]) == \
        ("100", 6000.0, 36, "2024-03-15", "2131", "2813")                 # valoarea din „Valoare intrare”, nu din „Data intrare”


def test_def_c24_randul_necalculabil_se_arata_restul_se_salveaza():
    """C24: un rând pe care motorul nu-l poate calcula (`amortizat: None`) răsturna salvarea întreagă cu 422 de model. Acum
    rândul e refuzat numit (`amortizare_necalculabila`), iar celelalte se scriu."""
    import main
    r = mf.extrage(_cp1250(MF_SAGA), "mf.csv")
    randuri = [main.MijlocFixRand(**x).model_dump() for x in r]       # modelul primește rândul „necalculabil” fără 422
    conn = _ConnFals()
    rez = mf.importa(conn, randuri)
    assert rez["importati"] == 1
    assert [(e["rand"], e["regula"]) for e in rez["respinse"]] == [(3, "amortizare_necalculabila")]
    assert [p[0] for p in conn.inserate("mijloace_fixe")] == ["100"]


# ── istoric declarații ─────────────────────────────────────────────────────────────────────────────────────────────────────────
ISTORIC = ("Tip declarație;An;Lună;Data depunerii\nD300;2026;8;25.09.2026\nD212;2025;;20.05.2026\nD112;2026;;25.08.2026\n"
           "D999;2026;8;25.09.2026\n")


def test_def_c25_istoric_randul_problema_se_arata_restul_se_salveaza():
    import main
    r = ist.extrage(ISTORIC.encode("utf-8"), "ist.csv")
    assert [(x["tip"], x["stare"]) for x in r] == [("D300", "ok"), ("D212", "ok"), ("D112", "respins"), ("D999", "respins")]
    randuri = [main.IstoricDeclRand(**x).model_dump() for x in r]     # avertismentele nu mai răstoarnă modelul (C25)
    conn = _ConnFals()
    rez = ist.importa(conn, 77, randuri)
    assert rez["importati"] == 2
    assert sorted((e["rand"], e["regula"]) for e in rez["respinse"]) == [(4, "luna_invalida"), (5, "tip_necunoscut")]
    assert [(p[1], p[2], p[3]) for p in conn.inserate("declaratii_depuse")] == [(2026, 8, "d300"), (2025, 12, "d212")]


def test_articolele_revalideaza_pe_server():
    conn = _ConnFals()
    rez = art.importa(conn, "s", [{"denumire": "Faina", "um": "kg", "cantitate": -1, "pret": 2, "cont_stoc": "371",
                                   "cont_cheltuiala": "607", "valid": True, "motiv": "ok"}], data_sold="2026-09-30")
    assert rez["create"] == 0 and rez["sarite"][0]["regula"] == "cantitate_pret_negativ"


# ── GARDA DE CLASĂ: modelul de salvare primește tot ce produce previzualizarea ─────────────────────────────────────────────────
# Câmpurile CALCULATE de previzualizare (pe care serverul le recalculează la scriere) — singurele care au voie să lipsească din model.
CALCULATE = {
    # [348] `functie`: textul funcției din fișier e numai de afișat — evidența ține codul COR (D112), iar lipsa codului se semnalează
    # cu funcția din fișier (`salariati_import_api.semnale_randuri`, regula `cor_lipsa`)
    "SalariatRand": {"cnp_valid", "cnp_motiv", "functie"},
    "AsociatRand": {"cnp_valid", "cnp_motiv"},
    # [comanda Costin 8.2 pct.4] `stare` / `motive` (eticheta rândului) și semnalele / calculul de la data preluării: salvarea le
    # recalculează din aceeași verificare (`verifica_randuri`)
    "MijlocFixRand": {"amortizat_calculat", "semnale_extra", "stare", "motive"},
    "IstoricDeclRand": {"tip_cunoscut", "anuala", "stare", "motive"},
    "PartenerRand": set(),
    "SoldRand": set(),
    "ArticolImportIn": set(),     # [373] salvarea revalidează fiecare rând (`articole_import_api.importa`)
    "RipRand": set(),             # [372] previzualizare, apoi salvare (`rip_migrare_api.importa` reverifică)
}


def _iesire(model):
    """Ieșirea previzualizării pentru modelul dat — calculată în TEST, nu la colectare (plasa e2e importă fișierele de aici; o
    mutație a parserului trebuie să pice testul ei, nu importul modulului)."""
    asoc = "Nume;CNP;Cotă %%\nPop Ion;%s;100\n" % CNP_OK
    return {"SalariatRand": lambda: si.extrage(_cp1250(SALARIATI_SAGA), "s.csv"),
            "MijlocFixRand": lambda: mf.extrage(_cp1250(MF_SAGA), "m.csv"),
            "IstoricDeclRand": lambda: ist.extrage(ISTORIC.encode("utf-8"), "i.csv"),
            "PartenerRand": lambda: sp.extrage(SITUATIE_CLIENTI.encode("utf-8"), "p.csv", cont_implicit="4111"),
            "SoldRand": lambda: solduri_api.extrage_balanta(_cp1250(BALANTA_SAGA), "b.csv"),
            "AsociatRand": lambda: __import__("core.asociati_import_api", fromlist=["x"]).extrage(asoc.encode("utf-8"), "a.csv"),
            "ArticolImportIn": lambda: __import__("core.articole_import_api", fromlist=["x"]).extrage(
                "Denumire;UM;Cantitate;Pret;Cont stoc;Cont cheltuiala\nFaina;kg;10;2;371;607\nZahar;kg;zece;3;371;\n".encode("utf-8"), "a.csv"),
            "RipRand": lambda: __import__("core.rip_migrare_api", fromlist=["x"]).extrage(
                "Data;Tip;Explicatie;Suma;Metoda;Categorie;Document\n01.03.2026;incasare;Vanzare;100,50;numerar;marfa;F1\n"
                "2026-13-01;plata;Chirie;x;;;\n".encode("utf-8"), "r.csv"),
            }[model]()


@pytest.mark.parametrize("model", sorted(CALCULATE))
def test_modelul_de_salvare_nu_pierde_si_nu_rastoarna_iesirea_previzualizarii(model):
    """C23 / C24 / C25 ca CLASĂ: orice câmp de DATE produs de `extrage` există în modelul rutei de salvare, iar modelul primește
    fiecare rând fără eroare. MUTAȚIA: `iban` scos din `SalariatRand` -> ROȘU (pierdut); `amortizat: float` repus -> ROȘU (422)."""
    import main
    M = getattr(main, model)
    randuri = _iesire(model)
    assert randuri
    for r in randuri:
        pierdute = set(r) - set(M.model_fields) - CALCULATE[model]
        assert not pierdute, "%s pierde câmpurile %s la salvare" % (model, sorted(pierdute))
        M(**r)                                                            # fără ValidationError
        # drumul real trece prin JSON (răspunsul previzualizării, apoi corpul salvării): Decimal / date ajung șiruri sau numere
        from fastapi.encoders import jsonable_encoder
        M(**json.loads(json.dumps(jsonable_encoder(r))))


# ── GARDA STRUCTURALĂ: citirea unui fișier de import are o singură sursă ──────────────────────────────────────────────────────
PARSERE = sorted(set(glob.glob(os.path.join(RAD, "core", "*_import_api.py"))) |
                 {os.path.join(RAD, "core", f) for f in ("solduri_api.py", "solduri_parteneri_api.py", "rip_migrare_api.py",
                                                         "anaf_api.py")})


def test_nicio_citire_de_fisier_de_import_in_afara_lui_import_tabel():
    """O copie a citirii (decodare cu `errors="replace"`, `load_workbook` / `xlrd` direct, o funcție `_gaseste_col`) e exact forma
    din care au ieșit C21 și C27: opt copii, fiecare cu „prima coloană care CONȚINE cheia” și UTF-8 cu înlocuire tăcută. Orice
    parser de import citește prin `core.import_tabel`. MUTAȚIA: un `_gaseste_col` repus într-un parser -> ROȘU."""
    rele = []
    for fn in PARSERE:
        src = open(fn, encoding="utf-8").read()
        arb = ast.parse(src)
        for n in ast.walk(arb):
            if isinstance(n, ast.FunctionDef) and n.name in ("_gaseste_col", "_citeste_tabel"):
                rele.append("%s: def %s" % (os.path.basename(fn), n.name))
            if isinstance(n, ast.Call):
                f = n.func
                nume = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
                if nume in ("load_workbook", "open_workbook"):
                    rele.append("%s:%d: %s" % (os.path.basename(fn), n.lineno, nume))
                if nume == "decode" and any(isinstance(k.value, ast.Constant) and k.value.value == "replace"
                                            for k in n.keywords if k.arg == "errors"):
                    rele.append("%s:%d: decode(errors='replace')" % (os.path.basename(fn), n.lineno))
    assert len(PARSERE) >= 10, PARSERE                  # 6 `*_import_api` + solduri, parteneri, RIP, lista de CUI-uri
    assert not rele, "citire de fișier de import în afara lui core.import_tabel:\n" + "\n".join(rele)


def test_formatele_ecranului_sunt_cele_ale_serverului():
    """Câmpurile de fișier ale importurilor acceptă exact formatele pe care le citește `import_tabel.citeste`."""
    import re
    js = open(os.path.join(RAD, "static", "js", "ecrane", "migrare.js"), encoding="utf-8").read()
    accept = set(re.findall(r'data-actiune="POST /tenants/\{tenant_id\}/[a-z-]+(?:/incarca)?"\s+accept="([^"]+)"', js))
    assert accept == {",".join((".csv", ".txt", ".tsv", ".xlsx", ".xls"))}, accept
    assert set(it.FORMATE) == {".csv", ".tsv", ".txt", ".xlsx", ".xlsm", ".xls"}


# ── conexiune falsă: captează scrierile, fără bază ────────────────────────────────────────────────────────────────────────────
class _ConnFals:
    def __init__(self):
        self.executate = []

    def cursor(self, *a, **k):
        return _CurFals(self)

    def inserate(self, tabel):
        return [p for s, p in self.executate if s.lstrip().upper().startswith("INSERT") and tabel in s]


class _CurFals:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, s, p=None):
        self.conn.executate.append((s, p))
        self._ultim = s

    def fetchone(self):
        s = self._ultim.lstrip()
        if not s.upper().startswith("SELECT"):
            return (1,)
        if s.upper().startswith("SELECT TO_REGCLASS("):   # instrucțiunea însăși, nu un sub-șir al alteia
            return ("tabel",)                         # [426] tabelele firmei există (citirea `existent` nu face DDL)
        if "count(" not in s.lower():
            return None
        # [lotul 10, 426 — clasa] agregatele pe o firmă FĂRĂ date (count / sum -> 0, min / max -> NULL): `existent` al fiecărui import
        # citește ce există înainte de înlocuire, iar falsul ăsta e o firmă goală (prima preluare)
        import re as _re
        lista, adanc, parti, bucata = s[6:s.upper().index(" FROM ")], 0, [], ""
        for ch in lista:
            adanc += (ch == "(") - (ch == ")")
            if ch == "," and not adanc:
                parti.append(bucata)
                bucata = ""
            else:
                bucata += ch
        parti.append(bucata)
        return tuple(None if _re.match(r"\s*(min|max)\(", x, _re.I) else 0 for x in parti)

    def fetchall(self):
        return []                                     # [426] o firmă fără date: nimic de înlocuit


def test_mesajele_importului_nu_au_sume_si_date_brute():
    """[14.10.2026, găsit pe captura C24] Avertismentele previzualizării arătau „(2000.00)” și „la 2026-10-14” — DS cap.4: sumele
    prin `pdf_util.bani`, datele prin `pdf_util.data_ro`. Clasa, în toate parserele de import: niciun șir cu `%.2f` și niciun
    `.isoformat()` / `strftime` într-un mesaj formatat cu `%`. MUTAȚIA: un mesaj readus la `%.2f` -> ROȘU."""
    rele = []
    for fn in PARSERE + [os.path.join(RAD, "core", "import_tabel.py")]:
        arb = ast.parse(open(fn, encoding="utf-8").read())
        for n in ast.walk(arb):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.find("%.2f") >= 0:
                rele.append("%s:%d: %r" % (os.path.basename(fn), n.lineno, n.value[:70]))
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and isinstance(n.left, ast.Constant) \
                    and isinstance(n.left.value, str) and not n.left.value.lstrip().upper().startswith(("SELECT", "INSERT", "UPDATE", "DELETE")):
                for c in ast.walk(n.right):
                    if isinstance(c, ast.Attribute) and c.attr in ("isoformat", "strftime"):
                        rele.append("%s:%d: dată brută în mesaj" % (os.path.basename(fn), n.lineno))
    assert not rele, "sume / date brute în mesajele importului (DS cap.4: bani / data_ro):\n" + "\n".join(rele)
