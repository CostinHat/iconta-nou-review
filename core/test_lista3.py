# -*- coding: utf-8 -*-
"""GARDĂ: titlul listei 3 e GENERAT, nu scris — a doua aplicare a regulii, pe propria listă.

*Costin, 31.08.2026: «Cifra "opt artefacte" vine din premisa care a căzut: e un număr derivat
reafirmat în proză, care nu se mai regenerează din nimic — aceeași clasă ca antetul T02. Se aplică
regula ei propriei liste: ori se generează, ori se șterge.»*

**Instanța, măsurată:** titlul scria **5 artefacte deschise** (măsurat 30.08 dimineață). Derivat din
chiar tabelele de dedesubt: **1 deschis din 7**. Rămăsese în urmă cu patru reparații — și, ca antetul
T02, **n-a țipat**: nimic nu-l compara cu nimic.

**De ce se GENEREAZĂ și nu se ȘTERGE.** Titlul e util — spune dintr-o privire cât a mai rămas. Cifra
lui are o sursă unică (coloana `stare`), deci se poate produce. Un titlu fără cifră ar fi mutat
întrebarea în capul cititorului, care ar fi numărat rândurile de mână — adică exact ce face
instrumentul, dar fără urmă.

**CE NU PĂZEȘTE, declarat:** dacă starea scrisă în tabel e ADEVĂRATĂ. Un rând care zice REPARAT fără
să fie trece pe aici; pentru asta sunt gărzile fiecărui artefact (`test_registre_art321`,
`test_registru_inventar`, `test_registru_evidenta_fiscala`, `test_note_explicative_asteapta`).
"""
import io
import os

import pytest

from scripts import scan_lista3 as sl


@pytest.fixture(scope="module")
def doc():
    return io.open(sl.CONF, encoding="utf-8").read()


def test_titlul_listei_3_e_IDENTIC_cu_ce_genereaza_instrumentul(doc):
    """doc↔cod, caracter cu caracter. Nu se repară cu mâna: se regenerează."""
    gen = sl.titlu(doc)
    linii = [l for l in doc.split("\n") if l.startswith("#### Lista 3 —")]
    assert len(linii) == 1, (
        "titlul listei 3 apare de %d ori — dacă s-a duplicat, cele două se pot despărți tăcut"
        % len(linii))
    assert linii[0] == gen, (
        "titlul listei 3 diferă de ce generează instrumentul:\n  scris:   %s\n  generat: %s\n\n"
        "Regenerează-l din `scan_lista3.titlu()`. Nu-l corecta cu mâna — a doua oară va rămâne în "
        "urmă la fel de tăcut." % (linii[0], gen))


def test_verdictele_sunt_un_nomenclator_INCHIS(doc):
    """Un al patrulea cuvânt în coloana `stare` e o decizie, nu o scăpare de tipar. Dacă apare,
    instrumentul refuză să numere în loc să-l pună tăcut la «altceva»."""
    d = sl.numara(doc)
    assert not d["necunoscute"], (
        "verdicte în afara nomenclatorului (%s): %r — adaugă-l în `scan_lista3.VERDICTE` cu ce "
        "înseamnă, sau scrie starea cu unul din cele existente"
        % (", ".join(sl.VERDICTE), d["necunoscute"]))


def test_anti_vacuu_instrumentul_chiar_gaseste_randuri(doc):
    """Un titlu generat dintr-un tabel gol ar scrie «niciun artefact deschis» și ar fi verde."""
    rs = sl.randuri(doc)
    assert len(rs) >= 5, (
        "doar %d rânduri de listă 3 găsite — capul de tabel s-a schimbat, iar cifra generată nu mai "
        "descrie nimic" % len(rs))
    assert sum(1 for r in rs if r["verdict"] == "REPARAT") > 0, (
        "niciun rând REPARAT — clasificarea n-a discriminat nimic")


def test_calibrare_titlul_se_SCHIMBA_cand_se_schimba_o_stare(doc):
    """CALIBRARE pe modul propriu de eșec: dacă titlul n-ar depinde de coloana `stare`, ar fi o
    constantă frumos ambalată. Se probează pe o COPIE a documentului, nu pe fișierul real."""
    inainte = sl.titlu(doc)
    mutat = doc.replace("| **DESCHIS** |", "| **REPARAT** |", 1)
    assert mutat != doc, "nu există niciun rând DESCHIS de mutat — calibrarea n-are pe ce lucra"
    assert sl.titlu(mutat) != inainte, (
        "titlul nu se schimbă când un rând trece din DESCHIS în REPARAT — nu se derivă din stare")

    # și direcția inversă, ca să nu treacă un instrument care doar numără rânduri
    invers = doc.replace("| **REPARAT.**", "| **DESCHIS.**", 1)
    if invers != doc:
        assert sl.titlu(invers) != inainte, "titlul nu se schimbă nici când un REPARAT se redeschide"


def test_tabelul_de_proba_e_GENERAT_nu_scris(doc):
    """[31.08.2026] Extinderea regulii, cerută de Costin după **a treia instanță în două zile**:

    *«Regula de ieri acoperă de acum și CALIFICATIVUL derivat, nu doar numărul. O afirmație al cărei
    adevăr depinde de un calificativ măsurat ori se regenerează din instrument, ori nu se scrie.»*

    **Instanța care a cerut-o e a mea.** Tabelul ăsta, scris de mână, a purtat o zi propoziția
    *„niciuna n-are două exerciții consecutive"* — adevărată doar cu **«cu rulaje»**, calificativ
    care lipsea. Numărul era corect; **ce anume număra**, nu. Un clichet pe cifre n-ar fi prins-o:
    cifra n-avea nimic.

    De-aia tabelul se generează din măsurătoare, nu din memoria a ce s-a măsurat.
    """
    gen = sl.proba_md()
    cap = gen.split(chr(10))[0]
    assert cap in doc, (
        "capul tabelului de probă nu se mai găsește în registru — ori s-a rescris de mână, ori "
        "instrumentul produce altă formă. Regenerează cu `scan_lista3.proba_md()`.")
    i = doc.index(cap)
    scris = doc[i:i + len(gen)]
    assert scris == gen, (
        "tabelul de probă diferă de ce generează instrumentul.\n  scris:   %r\n  generat: %r\n\n"
        "Nu-l corecta cu mâna — regenerează-l. Adevărul lui depinde de calificative măsurate "
        "(«cu rulaje», «cu note»), iar acelea se schimbă fără să anunțe."
        % (scris[:220], gen[:220]))


def test_fiecare_rand_DESCHIS_apare_in_proba(doc):
    """Un rând deschis fără dimensiune măsurată e o cifră moștenită — chiar defectul recalculării."""
    deschise = [r["artefact"] for r in sl.randuri(doc) if r["verdict"] == "DESCHIS"]
    if not deschise:
        pytest.skip("niciun rând deschis — proba n-are obiect")
    gen = sl.proba_md()
    lipsa = [a for a in deschise if a.split("(")[0].strip()[:18] not in gen]
    assert not lipsa, (
        "artefacte DESCHISE fără rând în tabelul de probă: %s. Măsoară-le înainte de a construi "
        "din ele — sau adaugă-le în `scan_lista3.proba_md()`, ca dimensiunea lor să se genereze."
        % lipsa)

def test_instrumentul_NU_numara_tabelul_vechi_de_cauze(doc):
    """Modul de eșec 1, ținut vizibil: tabelul de cauze are DOUĂ coloane și păstrează cauza măsurată
    la descoperire, nu starea de azi. Dacă ar intra în numărătoare, artefacte reparate ar fi numărate
    a doua oară ca deschise."""
    # Pe STRUCTURA: capetele de tabel se PARSEAZA (linia de coloane + separatorul de sub ea) și se
    # compară ca mulțime. Un `"| artefact | cauza |" in doc` ar fi trecut la fel de bine dacă șirul
    # apărea într-un paragraf care citează tabelul (clichet 50).
    capete = sl.capete_de_tabel(doc)
    assert capete >= {("artefact", "cauza")}, (
        "tabelul vechi de cauze a dispărut — modul de eșec 1 al instrumentului nu mai are obiect, "
        "dar nici istoricul măsurătorilor nu mai există")
    cap5 = {c for c in capete if len(c) == 5 and c[0] == "artefact"}
    assert cap5, "niciun tabel cu cele cinci coloane — instrumentul n-are ce număra"
    assert len(sl.randuri(doc)) < sum(1 for c in capete if len(c) == 2) * 40, (
        "numărătoarea pare să fi înghițit și alte tabele")


def test_fisierul_instrumentului_exista_unde_il_cauta_documentul():
    """Titlul trimite cititorul la instrument. O trimitere la ceva inexistent e mai rea decât niciuna."""
    assert os.path.exists(os.path.join(sl.RAD, "scripts", "scan_lista3.py"))
