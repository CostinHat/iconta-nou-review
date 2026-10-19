# -*- coding: utf-8 -*-
"""[deficiența 388, retestul Costin 19.10.2026] Modelele CSV din Migrare treceau sau picau la propria validare: CNP-ul devenea 2,9E+12 în
Excel, salariații intrau „cu observație” (fără coloana persoanelor în întreținere), CUI-urile din modelul de parteneri picau la cifra de
control, 5121 avea sold creditor, făina și uleiul stăteau pe 371 / 607.
GARDA DE CLASĂ: fiecare model, generat exact cum îl descarcă ecranul (`MODELE` + `_celulaCSV` din static/js/ecrane/migrare.js, rulate cu
node), trece prin parserul și verificarea importului lui FĂRĂ nicio respingere și fără nicio observație; balanța e echilibrată și niciun
sold nu stă pe partea opusă funcțiunii contului."""
import json
import os
import re
import subprocess

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = os.path.join(RAD, "static", "js", "ecrane", "migrare.js")


def _modele():
    src = open(MIG, encoding="utf-8").read()
    bloc = src[src.index("const MODELE = {"):src.index("function _descarcaModelCSV")]
    js = bloc + "\nconst out = {}; for (const k of Object.keys(MODELE)) { const m = MODELE[k];" \
                " out[k] = [m.coloane, ...m.randuri].map((r) => r.map(_celulaCSV).join(SEPARATOR_MODEL)).join('\\r\\n') + '\\r\\n'; }" \
                " console.log(JSON.stringify(out));"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


MODELE = _modele()


class _ConnArticole:
    """Conexiunea de care are nevoie `retete_import_api.potriveste`: articolele din modelul de articole (în ordinea lui)."""
    def __init__(self, articole):
        self.a = articole

    def cursor(self):
        a = self.a

        class _C:
            def __enter__(self):
                return self

            def __exit__(self, *x):
                return False

            def execute(self, *x):
                pass

            def fetchall(self):
                return [(i + 1, r["denumire"], r["um"]) for i, r in enumerate(a)]
        return _C()


def _fara_probleme(modul, cheie, **kw):
    m = __import__(modul, fromlist=["x"])
    randuri = m.extrage(("\ufeff" + MODELE[cheie]).encode("utf-8"), "model.csv")
    if cheie == "retete":   # rețeta se verifică după potrivirea ingredientelor pe articolele din stoc — cele din modelul de articole
        from core import articole_import_api
        m.potriveste(_ConnArticole(articole_import_api.extrage(MODELE["articole"].encode("utf-8"), "a.csv")), "s", randuri)
    er = m.verifica_randuri(randuri, **kw) if kw else m.verifica_randuri(randuri)
    er = er[0] if isinstance(er, tuple) else er
    assert randuri and not er, (cheie, er)
    sem = getattr(m, "semnale_randuri", None)
    if sem:
        assert not sem(randuri), (cheie, sem(randuri))
    return randuri


def test_salariatii_din_model_intra_fara_observatie():
    r = _fara_probleme("core.salariati_import_api", "salariati")
    assert [x["cnp"] for x in r] == ["2900215410011", "1850715410012"]          # CNP-ul întreg, nu 2,9E+12
    assert all(not x.get("de_verificat") for x in r), [x.get("de_verificat") for x in r]


def test_asociatii_din_model():
    _fara_probleme("core.asociati_import_api", "asociati")


def test_partenerii_din_model_au_cui_valid():
    from core import identitate
    for linie in MODELE["parteneri"].splitlines()[1:]:
        cui = linie.split(";")[1].replace("RO", "")
        assert identitate.valideaza_cui(cui) == (True, "ok"), linie


def test_balanta_din_model_e_echilibrata_si_pe_partea_functiunii():
    from core import solduri_api
    from core.audit_preluare import parte_gresita
    det = solduri_api.extrage_balanta_detaliat(("﻿" + MODELE["solduri"]).encode("utf-8"), "model.csv")
    assert solduri_api.balanta_valida(det["randuri"])[0] and solduri_api.verifica_echilibru(det["randuri"])[0], det
    assert not [g for g in (parte_gresita(r["cont"], r["debit"], r["credit"]) for r in det["randuri"]) if g]


@pytest.mark.parametrize("cheie,modul", [("articole", "core.articole_import_api"), ("mijloace", "core.mijloace_fixe_import_api"),
                                         ("istoric", "core.istoric_declaratii_import_api"), ("retete", "core.retete_import_api")])
def test_celelalte_modele_trec_de_verificare(cheie, modul):
    _fara_probleme(modul, cheie)


def test_materiile_prime_din_model_sunt_pe_301_601():
    """OMFP 1802/2014 pct.594: „301. Materii prime (A)”, „601. Cheltuieli cu materiile prime” — făina și uleiul nu sunt marfă (371)."""
    for linie in MODELE["articole"].splitlines()[1:]:
        c = linie.split(";")
        if re.match(r"(Făină|Ulei)", c[0]):
            assert (c[4], c[5]) == ("301", "601"), linie
