# -*- coding: utf-8 -*-
"""Teste scadentar F131 (facturi emise neincasate) — clasificare + fisa client.

Logica e obiectiva (stare din data_scadenta vs azi), fara valori fiscale.
"""
from datetime import date
from decimal import Decimal
from core.scadentar import clasifica, scadentar, total_restant

AZI = date(2026, 6, 15)


def test_clasifica_restanta():
    assert clasifica(date(2026, 6, 10), AZI) == ("restanta", -5)

def test_clasifica_scade_curand_in_prag():
    assert clasifica(date(2026, 6, 20), AZI)[0] == "scade_curand"   # +5 zile <= 7
    assert clasifica(date(2026, 6, 22), AZI)[0] == "scade_curand"   # +7 exact

def test_clasifica_in_termen_peste_prag():
    assert clasifica(date(2026, 6, 23), AZI)[0] == "in_termen"      # +8 > 7

def test_clasifica_fara_scadenta():
    assert clasifica(None, AZI) == ("fara_scadenta", None)

def test_clasifica_prag_configurabil():
    assert clasifica(date(2026, 6, 25), AZI, prag_zile=15)[0] == "scade_curand"


def _f(id, scad, suma, cui="4221306", nume="ALTEX"):
    return {"id": id, "numar": "KAI%d" % id, "data_emitere": date(2026, 5, 1),
            "data_scadenta": scad, "suma": Decimal(str(suma)), "tert_cui": cui,
            "tert_nume": nume, "client_id": 1, "email": "x@y.ro"}


def test_scadentar_rezumat_si_ordine():
    fs = [_f(1, date(2026, 6, 23), 100),      # in_termen
          _f(2, date(2026, 6, 10), 200),      # restanta -5
          _f(3, date(2026, 6, 5), 300),       # restanta -10
          _f(4, date(2026, 6, 18), 400)]      # scade_curand +3
    r = scadentar(fs, AZI)
    assert r["rezumat"] == {"restanta": 2, "scade_curand": 1, "in_termen": 1, "fara_scadenta": 0}
    # ordine urgenta: restantele intai, cea mai intarziata (id3, -10) prima
    assert [l["id"] for l in r["linii"]] == [3, 2, 4, 1]

def test_fisa_client_agrega_sold_si_restant():
    fs = [_f(1, date(2026, 6, 10), 200, cui="4221306", nume="ALTEX"),   # restant
          _f(2, date(2026, 6, 23), 100, cui="4221306", nume="ALTEX"),   # in termen
          _f(3, date(2026, 6, 5), 500, cui="14837428", nume="ORANGE")]  # restant
    r = scadentar(fs, AZI)
    cl = {c["cui"]: c for c in r["clienti"]}
    assert cl["4221306"]["nr"] == 2 and cl["4221306"]["sold"] == Decimal(300)
    assert cl["4221306"]["restant"] == Decimal(200)
    assert cl["14837428"]["restant"] == Decimal(500)
    # clientii sortati dupa restant descrescator: ORANGE (500) inaintea ALTEX (200)
    assert r["clienti"][0]["cui"] == "14837428"

def test_total_restant_pentru_alerta():
    fs = [_f(1, date(2026, 6, 10), 200), _f(2, date(2026, 6, 5), 300), _f(3, date(2026, 6, 23), 100)]
    assert total_restant(scadentar(fs, AZI)) == 2
