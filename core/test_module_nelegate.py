# -*- coding: utf-8 -*-
"""CLICHET — module de producție din `core/` pe care nu le cheamă nimeni în afara testelor.

  core/test_module_nelegate.py   (instrument: core/scan_module_nelegate.py — sursă unică)

R33, 24.08.2026. Clasa: *„nu s-a stricat, n-a fost niciodată legat"*. Un modul cu funcții publice,
cu teste care trec, și cu zero apelanți în producție arată identic cu unul viu — testele îl țin
verde, deci **nimic nu semnalează**.

Clichetul e ancorat pe **NUME**, nu pe un număr: un modul care intră ȘI unul care iese sunt amândoi
vizibili. Un contor de „5" ar fi trecut peste o înlocuire.

CE NU ACOPERĂ, declarat (vezi și modurile de eșec din antetul instrumentului): nivelul **funcție**.
Un modul importat pentru o funcție, cu alte trei moarte, nu apare aici. Aia e o măsurătoare separată.
"""
import ast
import io
import os

import pytest

from core import scan_module_nelegate as scan

# Fiecare intrare poartă DE CE e aici. O intrare fără motiv ar face clichetul o listă de tolerat.
PIN = {
    "core/compensare.py":
        "PRODUCTIE, nelegat — 5 functii publice, inclusiv pull(conn, schema) si propune_compensari()",
    "core/echilibru_perioada.py":
        "PRODUCTIE, nelegat — SI are o a doua implementare LEGATA: main.py:4389 cheama "
        "verificatoare.verifica_balanta pentru «echilibru». Logica paralela, nu doar cod nelegat",
    "core/fisa_cont.py":
        "PRODUCATOR FARA LIVRARE, declarat (METODA §20) — Fisa de cont 14-6-22, care inlocuieste "
        "Cartea mare 14-1-3; zero rute si zero ecrane, spus in ISTORIC 23.08.2026 (3): «artefactul "
        "are producator, nu livrare». NU e omisiune - conditia lui de deblocare e LIVRAREA, nu un apel",
    "core/salarii_contare.py":
        "PRODUCTIE, nelegat — control_coerenta() e verificare incrucisata nota-vs-declaratie; "
        "salarizare.py:296 o NUMESTE, dar intr-un COMENTARIU",
    "core/scan_valori_afisate.py":
        "FALS POZITIV DECLARAT (modul de esec E2): unealta rulata din linia de comanda, fara garda "
        "`if __name__ == \"__main__\"`, deci sonda n-o poate deosebi de un modul nelegat",
}


@pytest.fixture(scope="module")
def rez():
    r = scan.masoara()
    assert r["fisiere"] > 500, "sonda a parcurs doar %d fisiere — anti-vacuu" % r["fisiere"]
    return r


def test_setul_nu_creste(rez):
    """Clichet bidirecțional: nimic nou fără decizie, și nimic vechi rămas în pin după ce s-a legat."""
    gasit = {r[0] for r in scan.doar_core(rez)}
    nou = gasit - set(PIN)
    assert not nou, (
        "MODUL DE PRODUCTIE NOU, nelegat: %s. Ori primeste un apelant, ori intra in PIN cu motivul "
        "scris." % sorted(nou))
    disparut = set(PIN) - gasit
    assert not disparut, (
        "%s nu mai e nelegat (bine!) — scoate-l din PIN, altfel clichetul ramane peste realitate "
        "si nu mai masoara nimic." % sorted(disparut))


def test_fiecare_intrare_poarta_un_motiv():
    for nume, motiv in PIN.items():
        assert len(motiv) > 40, "%s e in clichet fara motiv scris" % nume


def test_intrarile_din_pin_exista_pe_disc(rez):
    """Anti-vacuu pe pin: un clichet care numeste fisiere inexistente trece verde despre nimic."""
    for nume in PIN:
        cale = os.path.join(scan.RAD, nume)
        assert os.path.exists(cale), "clichetul numeste un fisier inexistent: %s" % nume


# ── calibrare NEGATIVĂ: ce sonda NU trebuie să găsească ───────────────────────
def test_modulele_viu_legate_nu_apar(rez):
    """Membri pe care sonda nu trebuie sa-i gaseasca. `control_incrucisat` e aici deliberat: a fost
    presupus nelegat pe 24.08, iar masuratoarea a aratat 6 importatori de productie."""
    gasit = {r[0] for r in scan.doar_core(rez)}
    for nume in ("control_incrucisat", "common", "d300", "control_fiscal_api", "verificatoare"):
        alti = rez["importatori"].get(nume, set())
        assert alti, "SONDA E RUPTA: %s n-are niciun importator de productie" % nume
        assert "core/%s.py" % nume not in gasit, "%s raportat gresit ca nelegat" % nume


def test_proza_nu_conteaza_ca_apel():
    """Modul de eșec propriu al sondei: un scan pe TEXT ar declara „legat" un modul care e doar
    MENȚIONAT. Cazul e CONSTRUIT, nu citit dintr-un fișier real — o calibrare care se sprijină pe
    proza din cod ar fi ea însăși o gardă ancorată în proză (interdicția 18, și chiar așa a picat
    prima formă). Construit, cazul nu se poate învechi și nu depinde de ce scrie cineva într-un
    comentariu."""
    sursa = (
        "# incrucisat nota-vs-declaratie (modul_doar_pomenit.control_coerenta)\n"
        '"""Docstring care mai pomeneste o data modul_doar_pomenit."""\n'
        "from core import common\n"
        "def f():\n"
        "    from core import d300 as _d\n"
        "    return _d\n"
    )
    gasite = scan._importate(ast.parse(sursa))
    assert "common" in gasite, "sonda nu mai vede importurile de la nivel de modul"
    assert "d300" in gasite, "sonda nu mai vede importurile LAZY, din corpul functiei"
    assert "modul_doar_pomenit" not in gasite, (
        "sonda numara PROZA ca import — un comentariu sau un docstring nu leaga nimic")


def test_o_suprafata_doar_privata_NU_e_suprafata_publica():
    """Calibrare NEGATIVA pe E5, ceruta de Costin 24.08.2026: sonda numara „functii publice", deci
    trebuie dovedit ca un modul care are DOAR functii private e sarit — nu raportat ca nelegat.

    Cazul e CONSTRUIT, nu citit dintr-un fisier real: asa nu depinde de ce contine azi depozitul."""
    sursa = (
        '"""Modul cu cod, dar fara nicio suprafata publica."""\n'
        "_CONST = 3\n"
        "def _ajutor(x):\n"
        "    def imbricata(y):\n"
        "        return y\n"
        "    return imbricata(x)\n"
        "class _Intern:\n"
        "    def metoda_publica_dar_pe_clasa_privata(self):\n"
        "        return 1\n"
    )
    assert scan._publice(ast.parse(sursa)) == [], (
        "sonda numara ca PUBLIC ceva ce e privat sau imbricat — atunci lista de module nelegate "
        "contine module care n-au ce lega")


def test_o_functie_publica_la_nivel_de_modul_CHIAR_se_vede():
    """Cealalta directie a calibrarii: daca prima ar trece fiindca `_publice` intoarce mereu [],
    aserțiunea de mai sus n-ar dovedi nimic."""
    sursa = "def face(x):\n    return x\n\ndef _ascuns(y):\n    return y\n"
    assert scan._publice(ast.parse(sursa)) == ["face"]


def test_cat_din_domeniu_vede_sonda(rez):
    """CIFRA CARE FACE UTILIZABILE celelalte cifre. Fara ea, „44 nelegate" nu se poate folosi la
    triaj: nu se stie din CE numitor.

    Masurat 24.08.2026 pe `b5e1e5b`: 402 module ne-test, din care 361 au suprafata publica (89,8%)
    si 41 nu au (invizibile prin E5). Din cele 41, doar 5 au cod propriu — restul n-au nicio
    definitie la nivel de modul (scripturi, constante, configurari).

    Se garda RAPORTUL, nu cifra exacta: un depozit viu adauga module. Ce nu are voie sa creasca tacit
    e PUNCTUL ORB."""
    total = vizibile = 0
    for cale in scan._fisiere(scan.RAD):
        if scan.e_test(cale):
            continue
        b = os.path.basename(cale)[:-3]
        if b == "__init__":
            continue
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        total += 1
        if scan._publice(arb):
            vizibile += 1
    assert total > 300, "domeniu suspect de mic (%d module) — anti-vacuu" % total
    acoperire = vizibile / float(total)
    assert acoperire >= 0.85, (
        "sonda vede doar %.1f%% din module (%d din %d) — punctul orb E5 a crescut; cifrele de "
        "module nelegate nu se mai pot folosi la triaj fara re-declararea numitorului"
        % (acoperire * 100, vizibile, total))
    del rez


def test_perimetrul_dinamic_e_raportat_nu_inghitit(rez):
    """E1: importurile dinamice sunt invizibile pentru AST. Sonda trebuie sa le NUMEASCA, nu sa taca."""
    assert isinstance(rez["dinamice"], list)
    assert "main.py" in rez["dinamice"], (
        "main.py nu mai apare ca avand import dinamic — perimetrul necunoscut nu se mai raporteaza")
