# -*- coding: utf-8 -*-
"""core/test_front_e_editare_identitate.py — GARD Front E: identitatea/contractul salariatului
se poate CORECTA din UI.

BUG (audit tenant_005): din ecranul de salariati se editau doar salariu/IBAN/COR/incetare.
nume/prenume/CNP/data_angajare/norma NU se puteau corecta din UI, desi backendul (SalariatEdit +
salariati_api._CAMPURI_API) le accepta - o eroare de tastare in nume/CNP ramanea necorectabila
(MEMORY §13). Fix: buton "Corecteaza datele" in ecranSalariati (firme.js) -> PUT /salariati/{id}.

Gard: (1) backendul PASTREAZA campurile in contract; (2) UI-ul PASTREAZA cablarea. RED-probate.
"""
import glob
import pytest

_CAMPURI_FRONT_E = ("nume", "prenume", "cnp", "data_angajare", "tip_norma", "ore_zi")


def test_backend_accepta_editarea_identitatii():
    from main import SalariatEdit
    from core.salariati_api import _CAMPURI_API
    camp = set(getattr(SalariatEdit, "model_fields", None) or SalariatEdit.__fields__)
    for f in _CAMPURI_FRONT_E:
        assert f in camp, "SalariatEdit nu mai accepta %r - Front E (corectare identitate) s-ar strica" % f
        assert f in _CAMPURI_API, "_CAMPURI_API nu mai scrie %r in DB" % f


def test_ui_cableaza_editarea_identitatii():
    import os
    p = "static/js/ecrane/firme.js"
    if not os.path.exists(p):
        pytest.skip("firme.js absent")
    src = open(p, encoding="utf-8").read()
    i = src.index("async function ecranSalariati")
    rest = src[i + 1:]
    j = i + 1 + rest.index("\nasync function ") if "\nasync function " in rest else len(src)
    reg = src[i:j]
    assert "data-date=" in reg and "ed-cnp" in reg and "cnpValid" in reg, \
        "editarea identitatii (nume/prenume/CNP/data angajare/norma) nu mai e cablata in ecranSalariati"
    assert 'api.put(`/tenants/${t.id}/salariati/${sid}`, { nume, prenume, cnp, data_angajare, tip_norma, ore_zi }' in reg, \
        "PUT-ul de corectare identitate nu mai trimite campurile asteptate"
