# -*- coding: utf-8 -*-
"""GARD Q16 — preview salariati imbogateste COR cu denumirea ocupatiei (nu doar codul).
migrare.js:885 arata r.cor (codul) etichetat 'Functie'. Fix: endpointul de preview ataseaza
`cor_denumire` (cor_api.denumire); frontendul arata denumirea, fallback la cod. RED pe cod vechi:
raspunsul de preview nu avea cheia `cor_denumire`."""
import io, contextlib
import pytest
from starlette.datastructures import UploadFile

import main
from core import salariati_import_api as _sal
from core import cor_api as _cor


@contextlib.contextmanager
def _fake_conn(*a, **k):
    yield None


def _uf():
    return UploadFile(io.BytesIO(b"x"), filename="x.csv")


def test_preview_salariati_ataseaza_denumirea_cor(monkeypatch):
    rand = {"nume": "POP", "prenume": "ION", "cnp": "1960101078916", "cnp_valid": True,
            "tip_norma": "intreaga", "ore_zi": 8, "cor": "251401", "salariu_brut": 5000, "judet_casa": "B"}
    monkeypatch.setattr(main, "_schema_sau_404", lambda ctx, tid: "public")
    monkeypatch.setattr(_sal, "extrage", lambda *a, **k: [dict(rand)])
    monkeypatch.setattr(main.db, "get_conn", _fake_conn)
    monkeypatch.setattr(_cor, "denumire", lambda conn, cod: "Programator" if cod == "251401" else None)

    res = main.salariati_import_incarca(1, fisier=_uf(), ctx={"uid": 1})
    r0 = res["randuri"][0]
    assert "cor_denumire" in r0, "preview NU ataseaza denumirea COR (Q16)"
    assert r0["cor_denumire"] == "Programator"
    assert r0["cor"] == "251401"   # codul ramane (fallback + title in UI)


def test_preview_salariati_cor_necunoscut_ramane_none(monkeypatch):
    rand = {"nume": "X", "prenume": "Y", "cnp": "1960101078916", "cnp_valid": True,
            "tip_norma": "intreaga", "ore_zi": 8, "cor": "999999", "salariu_brut": 5000, "judet_casa": "B"}
    monkeypatch.setattr(main, "_schema_sau_404", lambda ctx, tid: "public")
    monkeypatch.setattr(_sal, "extrage", lambda *a, **k: [dict(rand)])
    monkeypatch.setattr(main.db, "get_conn", _fake_conn)
    monkeypatch.setattr(_cor, "denumire", lambda conn, cod: None)
    res = main.salariati_import_incarca(1, fisier=_uf(), ctx={"uid": 1})
    assert res["randuri"][0]["cor_denumire"] is None   # necunoscut ramane necunoscut (fallback la cod in UI)
