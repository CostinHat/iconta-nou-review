# -*- coding: utf-8 -*-
"""Lotul 10, deficiența 426 — CLASA (comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”): „al doilea import de balanță pentru aceeași
firmă o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi, cere
confirmare; dacă există note pe lunile de după preluare, spune că soldurile lor se recalculează.”

Balanța e probată în `e2e_lot10_migrare.py::test_def_426_a_doua_balanta_arata_totalurile_si_cere_confirmare`. Aici celelalte patru
importuri care înlocuiau pe tăcute: soldurile pe parteneri, mijloacele fixe, istoricul declarațiilor, salariații (același CNP). Pentru
fiecare: firma are deja datele (scrise direct în baza de test, ca după un prim import) -> fereastra firmei -> Import date -> pasul ->
fișierul nou -> caseta de sus (`#mig-inlocuire`) spune ce există și ce aduce fișierul -> butonul -> confirmarea (`#ca-ok` / `#ca-nu`) ->
„Renunță”: nimic schimbat -> din nou -> confirmă -> mesajul spune ce s-a înlocuit; în evidență, datele noi.

Pașii pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). CUI-urile (14399840, 4221306, 18189442) și CNP-ul
(1900101410011) au cifra de control verificată (algoritmul din CLAUDE.md)."""
import pytest

from conftest import firma_noua, sql

CNP1 = "1900101410011"      # cifra de control verificată (core/test_412_cim_salariat.py)


@pytest.fixture
def firma_inl():
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
    patron.pg.set_input_files("#mig-file", files=[{"name": nume, "mimeType": "text/csv", "buffer": continut.encode("utf-8")}])
    patron.pg.wait_for_selector(astept, timeout=30000)


def _caseta(pg):
    return " ".join(pg.inner_text("#mig-inlocuire").split())


def _renunta_apoi_confirma(patron, buton, text_ok, numara, inainte, mesaj):
    """Butonul -> confirmarea cu `text_ok` -> „Renunță”: `numara()` rămâne `inainte` -> din nou -> confirmă -> `mesaj` pe ecran."""
    pg = patron.pg
    pg.click(buton)
    pg.wait_for_selector("#ca-ok", timeout=10000)
    assert pg.inner_text("#ca-ok").strip() == text_ok
    pg.click("#ca-nu")
    assert numara() == inainte, "Renunță a scris totuși"
    pg.click(buton)
    pg.click("#ca-ok")
    pg.wait_for_function("(m) => document.body.innerText.includes(m)", arg=mesaj, timeout=30000)
    patron.captura("inlocuit")


def test_def_426_parteneri_al_doilea_import_arata_totalurile_si_cere_confirmare(patron, firma_inl):
    """Firma are soldurile pe parteneri la 31.12.2025 (DEDEMAN 1.000 lei debit, FURNIZOR 400 lei credit) și balanța cu 4111 = 2.500 lei
    -> Solduri parteneri -> fișierul cu ALT CLIENT 2.500 lei -> caseta: „Firma are deja solduri pe parteneri la 31.12.2025: 2 parteneri,
    debit 1.000,00 lei, credit 400,00 lei. Fișierul nou: 1 partener, debit 2.500,00 lei, credit 0,00 lei. Salvarea le înlocuiește pe cele
    vechi.” -> „Înlocuiește partenerii” -> „Înlocuiesc soldurile pe parteneri” -> „Un partener salvat. Soldurile vechi (2 parteneri) au
    fost înlocuite.”"""
    pg, s = patron.pg, firma_inl["schema"]
    sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES '
        "('4111', 'Clienți', 2500, 0, '2025-12-31'), ('401', 'Furnizori', 0, 400, '2025-12-31'), ('1012', 'Capital', 0, 2100, '2025-12-31')" % s)
    sql('INSERT INTO "%s".solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) VALUES '
        "('4111', 'RO14399840', 'DEDEMAN', 1000, 0, '2025-12-31'), ('401', 'RO4221306', 'FURNIZOR', 0, 400, '2025-12-31')" % s)
    _pas(patron, firma_inl, "Solduri parteneri")
    _incarca(patron, "parteneri.csv", "cont;cui;denumire;sold debitor;sold creditor\n4111;RO18189442;ALT CLIENT;2500;0\n",
             "#mig-salveaza-part")
    patron.captura("avertisment")
    assert _caseta(pg) == ("Firma are deja solduri pe parteneri la 31.12.2025: 2 parteneri, debit 1.000,00 lei, credit 400,00 lei. "
                           "Fișierul nou: 1 partener, debit 2.500,00 lei, credit 0,00 lei. Salvarea le înlocuiește pe cele vechi."), _caseta(pg)
    assert pg.inner_text("#mig-salveaza-part").strip() == "Înlocuiește partenerii"
    _renunta_apoi_confirma(patron, "#mig-salveaza-part", "Înlocuiesc soldurile pe parteneri",
                           lambda: sql('SELECT count(*) FROM "%s".solduri_parteneri' % s)[0][0], 2,
                           "Un partener salvat. Soldurile vechi (2 parteneri) au fost înlocuite.")
    # CUI-ul se salvează fără „RO” (`cui_forma.stocare`, decizia 10.3: „RO14837428 -> 14837428”)
    assert sql('SELECT cui, sold_debitor FROM "%s".solduri_parteneri' % s) == [("18189442", 2500)]


def test_def_426_mijloace_fixe_al_doilea_import_arata_valorile_si_amortizarile(patron, firma_inl):
    """Firma are registrul (Laptop, 6.000 lei, amortizare preluată 1.500 lei) și două note de amortizare (01 și 03/2026) -> Mijloace fixe
    -> fișierul cu Server 12.000 lei -> caseta: „Firma are deja un registru de mijloace fixe: 1 mijloc fix, valoare de intrare 6.000,00
    lei, amortizare preluată 1.500,00 lei. Fișierul nou: 1 mijloc fix, valoare de intrare 12.000,00 lei, amortizare preluată 2.000,00 lei.
    Salvarea înlocuiește registrul vechi. În contabilitate sunt 2 note de amortizare (din 01/2026 până în 03/2026) …” -> „Înlocuiește
    registrul” -> „Înlocuiesc registrul” -> „Registrul vechi (1 mijloc fix) a fost înlocuit.”"""
    pg, s = patron.pg, firma_inl["schema"]
    sql('INSERT INTO "%s".mijloace_fixe (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, '
        "activ, amortizare_preluata) VALUES ('100', 'Laptop', '2141', '2814', 6000, 0, 36, '2025-01-10', 'liniara', true, 1500)" % s)
    sql('INSERT INTO "%s".inregistrari (data, numar, descriere, status, sursa) VALUES (\'2026-01-31\', \'A1\', \'Amortizare\', \'validata\', '
        "'amortizare'), ('2026-03-31', 'A3', 'Amortizare', 'validata', 'amortizare')" % s)
    _pas(patron, firma_inl, "Mijloace fixe")
    _incarca(patron, "mf.csv", "cod;denumire;valoare;durata;data pif;metoda;cont imobilizare;cont amortizare;amortizare cumulata\n"
                               "200;Server;12000;36;10.01.2025;liniara;2141;2814;2000\n", "#mig-salveaza-mf")
    patron.captura("avertisment")
    c = _caseta(pg)
    assert c.startswith("Firma are deja un registru de mijloace fixe: 1 mijloc fix, valoare de intrare 6.000,00 lei, amortizare preluată "
                        "1.500,00 lei. Fișierul nou: 1 mijloc fix, valoare de intrare 12.000,00 lei, amortizare preluată 2.000,00 lei. "
                        "Salvarea înlocuiește registrul vechi."), c
    assert "În contabilitate sunt 2 note de amortizare (din 01/2026 până în 03/2026), calculate pe registrul vechi" in c, c
    assert pg.inner_text("#mig-salveaza-mf").strip() == "Înlocuiește registrul"
    _renunta_apoi_confirma(patron, "#mig-salveaza-mf", "Înlocuiesc registrul",
                           lambda: sql('SELECT count(*) FROM "%s".mijloace_fixe' % s)[0][0], 1,
                           "Registrul vechi (1 mijloc fix) a fost înlocuit.")
    assert sql('SELECT cod, valoare FROM "%s".mijloace_fixe' % s) == [("200", 12000)]


def test_def_426_istoricul_al_doilea_import_arata_perioadele_si_cere_confirmare(patron, firma_inl):
    """Firma are istoricul preluat (D300 pe 03/2025, D100 pe 06/2025) -> Istoric declarații -> fișierul cu D300 pe 06/2025 -> caseta:
    „Firma are deja un istoric de declarații preluat: 2 declarații (D100, D300), din 03/2025 până în 06/2025. Fișierul nou: 1 declarație
    (D300), pe 06/2025. Salvarea înlocuiește istoricul preluat; declarațiile depuse prin iConta rămân.” -> „Înlocuiește istoricul” ->
    „Înlocuiesc istoricul” -> „Istoricul preluat vechi (2 declarații) a fost înlocuit.”"""
    pg, t = patron.pg, firma_inl["tenant_id"]
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa) VALUES "
        "(%s, 2025, 3, 'd300', '2025-04-20', 'migrare'), (%s, 2025, 6, 'd100', '2025-07-20', 'migrare')", (t, t))
    _pas(patron, firma_inl, "Istoric declarații")
    _incarca(patron, "istoric.csv", "Tip declarație;An;Lună;Data depunerii\nD300;2025;6;21.07.2025\n", "#mig-salveaza-ist")
    patron.captura("avertisment")
    assert _caseta(pg) == ("Firma are deja un istoric de declarații preluat: 2 declarații (D100, D300), din 03/2025 până în 06/2025. "
                           "Fișierul nou: 1 declarație (D300), pe 06/2025. Salvarea înlocuiește istoricul preluat; declarațiile depuse "
                           "prin iConta rămân."), _caseta(pg)
    assert pg.inner_text("#mig-salveaza-ist").strip() == "Înlocuiește istoricul"
    _renunta_apoi_confirma(patron, "#mig-salveaza-ist", "Înlocuiesc istoricul",
                           lambda: sql("SELECT count(*) FROM public.declaratii_depuse WHERE tenant_id = %s", (t,))[0][0], 2,
                           "Istoricul preluat vechi (2 declarații) a fost înlocuit.")
    assert sql("SELECT tip, an, luna FROM public.declaratii_depuse WHERE tenant_id = %s", (t,)) == [("d300", 2025, 6)]


def test_def_426_salariatii_existenti_se_actualizeaza_numai_confirmat(patron, firma_inl):
    """Firma are salariata POPESCU ANA (CNP 1900101410011) -> Salariați -> fișierul cu același CNP, nume POPA, 7.000 lei -> caseta: „Firma
    are deja 1 salariat; salariatul din fișier există deja după CNP: POPESCU ANA. Salvarea îi actualizează fișa cu datele din fișier …”
    -> „Salvează salariații” -> „Actualizez fișele” -> „Salariați: 0 noi, 1 fișă actualizată.” (lotul 11, 447: o singură numărătoare)"""
    pg, s = patron.pg, firma_inl["schema"]
    sql('INSERT INTO "%s".salariati (cnp, nume, prenume, data_angajare, judet_casa, part_time, ore_zi) '
        "VALUES (%%s, 'POPESCU', 'ANA', '2024-01-15', 'B', false, 8)" % s, (CNP1,))
    _pas(patron, firma_inl, "Salariați")
    _incarca(patron, "salariati.csv", "nume;prenume;cnp;data angajare;norma;ore pe zi;brut;judet;functie de baza;persoane in intretinere;"
                                      "scutit contributie minima\nPOPA;ANA;%s;2024-01-15;intreaga;8;7000;B;da;0;nu\n" % CNP1,
             "#mig-salveaza-sal")
    patron.captura("avertisment")
    assert _caseta(pg).startswith("Firma are deja 1 salariat; salariatul din fișier există deja după CNP: POPESCU ANA. Salvarea îi "
                                  "actualizează fișa cu datele din fișier"), _caseta(pg)
    _renunta_apoi_confirma(patron, "#mig-salveaza-sal", "Actualizez fișele",
                           lambda: sql('SELECT nume FROM "%s".salariati WHERE cnp = %%s' % s, (CNP1,))[0][0], "POPESCU",
                           "Salariați: 0 noi, 1 fișă actualizată.")
    assert sql('SELECT nume FROM "%s".salariati WHERE cnp = %%s' % s, (CNP1,)) == [("POPA",)]


def test_def_426_asociatii_al_doilea_import_cere_confirmare(patron, firma_inl):
    """[426, ultimul membru al clasei: asociații] Firma are asociații POPESCU ION 60% / IONESCU MARIA 40% și nota de dividende din
    20.05.2026 (10.000 lei, validată) -> Asociați -> fișierul cu POPESCU ION 50% / VASILE DAN 50%, fără dată de cesiune -> caseta: „Firma
    are deja 2 asociați: POPESCU ION 60%, IONESCU MARIA 40%. Fișierul nou: POPESCU ION 50%, VASILE DAN 50%. Fără dată de cesiune, salvarea e
    o corectură […] Nota de dividende se împarte după structura de acum: nota nr. crt. 1 din 20.05.2026 (10.000,00 lei) […]” -> „Salvează
    asociații” -> „Înlocuiesc asociații” -> „Renunță”: structura neschimbată -> din nou -> confirmă -> „Structura veche (2 asociați) a fost
    înlocuită.” CNP-urile 1800101400016, 2850202400023, 1900101410011 au cifra de control verificată (algoritmul din CLAUDE.md)."""
    pg, s = patron.pg, firma_inl["schema"]
    sql('INSERT INTO "%s".asociati (nume, cnp, cota) VALUES (%%s, %%s, 60), (%%s, %%s, 40)' % s,
        ("POPESCU ION", "1800101400016", "IONESCU MARIA", "2850202400023"))
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, document_ref) VALUES (\'2026-05-20\', \'Dividende\', '
              "'operatiuni', 'ciorna', 'Hotărârea AGA nr 3') RETURNING id" % s)[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'117\', \'457\', 10000)' % s,
        (nid,))
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))
    _pas(patron, firma_inl, "Asociați")
    _incarca(patron, "asociati.csv", "nume;cnp/cui;cota %%\nPOPESCU ION;1800101400016;50\nVASILE DAN;%s;50\n" % CNP1, "#mig-salveaza-asoc")
    patron.captura("avertisment")
    c = _caseta(pg)
    assert c.startswith("Firma are deja 2 asociați: POPESCU ION 60%, IONESCU MARIA 40%. Fișierul nou: POPESCU ION 50%, VASILE DAN 50%. "
                        "Fără dată de cesiune, salvarea e o corectură"), c
    assert "Nota de dividende se împarte după structura de acum: nota nr. crt. 1 din 20.05.2026 (10.000,00 lei)" in c, c
    _renunta_apoi_confirma(patron, "#mig-salveaza-asoc", "Înlocuiesc asociații",
                           lambda: sql('SELECT nume, cota FROM "%s".asociati ORDER BY cota DESC, nume' % s),
                           [("POPESCU ION", 60), ("IONESCU MARIA", 40)],
                           "Structura veche (2 asociați) a fost înlocuită.")
    assert sql('SELECT nume, cota FROM "%s".asociati ORDER BY nume' % s) == [("POPESCU ION", 50), ("VASILE DAN", 50)]
