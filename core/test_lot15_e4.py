# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E4 — scenariile de server / registre: criteriul verificatorului (R5), registrul fără „Primii pași”, intrarea „Audit de preluare” în Import date."""
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verificator_design as V  # noqa: E402


def test_criteriul_verificatorului_poarta_corectiile_pct_2():
    c = V.RANDURI
    assert "gri" in c["d"] and "cel mult 2" in c["d"] and "deschide X" in c["d"]       # card gri valid, regula „cel mult 2”, semnal cu ecran = buton
    assert "numele proprii" in c["f"] and "cod de cont analitic" in c["g"] and "bara-fixa" in c["c"]


def test_promptul_fix_contine_criteriul_nou():
    p = V.prompt(["Control fiscal"], "/tmp/x")
    assert "deschide X" in p and "numele proprii" in p and "cod de cont analitic" in p


def test_registrul_nu_are_primii_pasi_dar_are_auditul_prin_import_date():
    reg = json.load(open(os.path.join(RAD, "core", "catalog_ecrane.json"), encoding="utf-8"))
    nume = [e["nume"] for e in reg]
    assert "Primii pași" not in nume                                                  # nu e fereastră de lucru
    audit = next(e for e in reg if e["nume"].startswith("Import date — Audit de preluare"))
    assert audit["pasi"][0]["click"] == "#fa-import" and audit["pasi"][1]["text"] == "Audit de preluare"


def test_import_date_are_intrarea_audit_de_preluare_cu_butonul_ei():
    mig = open(os.path.join(RAD, "static", "js", "ecrane", "migrare.js"), encoding="utf-8").read()
    assert re.search(r'titlu: "Audit de preluare".*deschideControlFirma', mig)
    firme = open(os.path.join(RAD, "static", "js", "ecrane", "firme.js"), encoding="utf-8").read()
    assert "export async function deschideControlFirma" in firme
