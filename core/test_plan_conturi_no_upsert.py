# -*- coding: utf-8 -*-
"""[Regula 4 + Regula 14.4] GARD: adaugarea MANUALA de cont in plan NU suprascrie tacut un simbol existent.

Provocarea stratului de import 'plan_conturi' (Adauga cont: simbol + denumire) a scos o mutatie tacuta
PERICULOASA: handler-ul facea INSERT ... ON CONFLICT (simbol) DO UPDATE SET denumire=EXCLUDED.denumire.
Un contabil care 'adauga' simbolul '101' cu alta denumire REDENUMEA tacut contul OMFP standard 'Capital'
(seed-uit la crearea firmei), fara avertisment - corupere de date. Calea bulk (solduri_api) foloseste corect
ON CONFLICT DO NOTHING; doar calea manuala era outlierul. Acum refuza explicit, cu denumirea existenta.
Ratchet pe sursa (fara DB) impotriva revenirii la upsert tacut.
"""
import os
import re
import pytest


def _handler_src():
    p = "main.py"
    if not os.path.exists(p):
        pytest.skip("main.py absent")
    s = open(p, encoding="utf-8").read()
    m = re.search(r"def tenant_plan_conturi_adauga\(.*?\n(.*?)\n@app\.", s, re.DOTALL)
    return m.group(1) if m else ""


def test_handler_gasit():
    assert _handler_src(), "handler tenant_plan_conturi_adauga negasit (redenumit?)"


def test_manual_add_nu_face_upsert_tacut():
    body = _handler_src()
    # semnatura defectului = upsert-ul care suprascrie (ON CONFLICT ... DO UPDATE); 'ON CONFLICT' singur
    # poate aparea legitim intr-un comentariu care descrie calea bulk (DO NOTHING).
    assert "DO UPDATE" not in body, "calea manuala inca face upsert (suprascrie tacut un cont existent)"


def test_manual_add_refuza_duplicatul_cu_mesaj():
    body = _handler_src()
    assert "SELECT denumire FROM plan_conturi WHERE simbol" in body, \
        "handler-ul nu mai verifica existenta simbolului inainte de INSERT"
    assert "există deja" in body, "handler-ul nu mai refuza duplicatul cu mesaj de contabil"
    assert "409" in body, "refuzul duplicatului ar trebui sa fie un 409 (conflict)"
