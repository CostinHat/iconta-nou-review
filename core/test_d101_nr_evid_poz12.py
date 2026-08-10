# -*- coding: utf-8 -*-
"""core/test_d101_nr_evid_poz12.py — gard: nr_evid poz.1-2 = '11' (OPANAF 206/2025).

CONFRUNTARE cu sursa OFICIALA (anaf_surse/d101_struct_anaf.txt, rand nr_evid, poz.19):
  "Poz.1-2 :11" — confirmat de exemplul ANAF din CHIAR structura oficiala:
  "11103011212250413000028" (poz.1-2='11', poz.3-5='103'=cod_obligatie, poz.6-7='01', ...).

BUG (HEAD pre-fix, commit c9869a1): _nr_evid emitea poz.1-2 = '10' — fara temei in sursa,
sustinut doar de un comentariu auto-referential. DUKIntegrator R18 verifica DOAR cifra de
control (poz.22-23), NU litera poz.1-2, deci accepta si '10' si '11'; leninenta care MASCA
neconformitatea fata de structura oficiala. Confruntarea e cu sursa ANAF, nu cu validatorul.

RED pe HEAD: assert n[:2]=='11' pica ('10'). GREEN dupa fix. Mutatie: reintroducerea '10' -> RED.
"""
from core.d101 import _nr_evid


def test_nr_evid_poz_1_2_este_11():
    n = _nr_evid("14399840", 2026, 12, "103")
    assert n[:2] == "11", "poz.1-2 trebuie '11' (OPANAF 206/2025), emis: %r" % n[:2]


def test_nr_evid_structura_si_checksum_conforme_sursei():
    n = _nr_evid("14399840", 2026, 12, "103")
    assert len(n) == 23 and n.isdigit()
    assert n[0:2] == "11"                 # poz.1-2 (sursa)
    assert n[2:5] == "103"                # poz.3-5 cod_obligatie
    assert n[5:7] == "01"                 # poz.6-7
    # poz.22-23 = ultimele 2 cifre din suma primelor 21 (sursa), consistent cu poz.1-2 corectat
    assert n[21:23] == "%02d" % (sum(int(c) for c in n[:21]) % 100)


def test_nr_evid_ancorat_pe_exemplul_oficial_anaf():
    # Exemplul verbatim din structura oficiala ANAF: 11103011212250413000028.
    ex = "11103011212250413000028"
    assert ex[0:2] == "11" and ex[5:7] == "01"
    assert ex[21:23] == "%02d" % (sum(int(c) for c in ex[:21]) % 100)
