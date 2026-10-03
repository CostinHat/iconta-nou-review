# -*- coding: utf-8 -*-
"""GARD — „URMATORUL PAS” din agendă nu poate propune un fir ÎNCHIS sau BLOCAT și vede ambele forme de scriere.

De ce (03.10.2026): `core.agenda.urmatorul_pas` lua primul rând `- urmator:` scris la margine din TOT `TESTE.md`. Firele
noi se scriu indentat (`  - urmator:`), deci erau sărite, iar primul rând la margine era al firului F3 — livrat pe 21.09
(97030ae2, ae876415, 78d2e46e), dar cu „urmator: F3 etapa 3 … NEINCEPUT” rămas în urmă. Agenda propunea un pas făcut de
două săptămâni, iar predarea l-a copiat. Reparat: doar secțiunea „În lucru acum”, ambele forme, ultimul „urmator” al
firului, sărite firele închise (ÎNCHIS / GATA / REZOLVAT / „(fir închis”) și cele blocate (BLOCAT / [EXTERN] / CONSEMNAT).

LIMITA, declarată: garda vede ce scrie în TESTE.md; un fir livrat al cărui „urmator” n-a fost actualizat rămâne invizibil
pentru ea — închiderea firului la livrare rămâne disciplina din CLAUDE.md §2.1 (de aceea închiderile de azi citează commitul).
"""
from core import agenda

TEXT = """# TESTE
## În lucru acum
- fir: **A — livrat** (01.10). ÎNCHIS
  - urmator: — (fir închis). STARE = ÎNCHIS
- fir: **B — blocat pe decizie** (01.10)
- urmator: pasul B1. STARE = NEINCEPUT
- urmator: decizie de produs. STARE = BLOCAT: aștept direcția
- fir: **C — de făcut, scris indentat** (02.10)
  - ultim: ceva
  - urmator: pasul C2. STARE = IN LUCRU
- fir: **D — scris la margine, mai jos**
- urmator: pasul D1. STARE = NEINCEPUT
## Altă secțiune
- urmator: rând din afara secțiunii. STARE = NEINCEPUT
"""


def test_sare_inchis_si_blocat_si_vede_forma_indentata(monkeypatch):
    monkeypatch.setattr(agenda, "_text", lambda f: TEXT)
    # forma veche (primul `- urmator:` la margine din tot fișierul) ar fi întors „pasul B1” — pas al unui fir blocat
    assert agenda.urmatorul_pas() == "pasul C2. STARE = IN LUCRU"


def test_ultimul_urmator_al_firului_e_starea_lui():
    fire = dict(agenda.fire_in_lucru(TEXT))
    assert fire["**B — blocat pe decizie** (01.10)"].startswith("decizie de produs")


def test_nimic_actionabil_e_spus_explicit(monkeypatch):
    monkeypatch.setattr(agenda, "_text", lambda f: TEXT.split("- fir: **C")[0] + "## Altă secțiune\n")
    assert agenda.urmatorul_pas().startswith("nimic acționabil")


def test_pe_TESTE_real_pasul_nu_e_al_unui_fir_inchis_sau_blocat():
    txt = agenda._text(agenda._TESTE)
    pas = agenda.urmatorul_pas()
    perechi = agenda.fire_in_lucru(txt)
    assert perechi, "secțiunea „În lucru acum” n-a fost găsită în TESTE.md"
    for antet, urm in perechi:
        if (urm or antet) == pas:
            assert not (agenda._INCHIS.search(antet) or agenda._INCHIS.search(urm) or agenda._BLOCAT.search(urm)), (antet, urm)
            break
    else:
        assert pas.startswith("nimic acționabil"), pas
