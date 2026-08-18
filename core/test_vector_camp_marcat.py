# -*- coding: utf-8 -*-
"""[Regula 14.4 pct.4] GARD: eroarea de camp obligatoriu la vectorul fiscal NUMESTE campul vinovat ('camp'),
ca ecranul sa-l poata MARCA (contur rosu + aria-invalid pe grupul de butoane), nu doar mesaj generic jos.

Provocat live pe tenant_001 (firma FARA vector): platitor TVA fara periodicitate decont -> mesajul era corect
in limba contabilului DAR grupul 'Periodicitate decont' nu era marcat vizual (Regula 14.4 pct.4: eroarea care
nu marcheaza campul vinovat). salveaza() intoarce acum 'camp'; ruta /tenants/{id}/vector il expune ca
erori_campuri; migrare.js marcheaza grupul (#vf-regim/#vf-tva/#vf-decont/#vf-ic).
"""
import os
import pytest
from core import vector_fiscal_api


def test_tva_lipsa_numeste_campul():
    # platitor_tva=None -> eroare INAINTE de orice acces la DB (conn poate fi None)
    r = vector_fiscal_api.salveaza(None, "micro", None, None, None)
    assert r["ok"] is False and r.get("camp") == "platitor_tva", r


def test_ic_lipsa_numeste_campul():
    r = vector_fiscal_api.salveaza(None, "micro", True, "lunar", None)
    assert r["ok"] is False and r.get("camp") == "operatiuni_ic", r


def test_decont_lipsa_numeste_campul():
    r = vector_fiscal_api.salveaza(None, "micro", True, None, True)
    assert r["ok"] is False and r.get("camp") == "tip_decont", r


def _f(p):
    if not os.path.exists(p):
        pytest.skip(p + " absent")
    return open(p, encoding="utf-8").read()


def test_ruta_expune_erori_campuri():
    s = _f("main.py")
    assert '"erori_campuri": [{"camp": _camp' in s, "ruta vector nu mai expune campul vinovat ca erori_campuri"


def test_frontend_marcheaza_grupul():
    s = _f("static/js/ecrane/migrare.js")
    assert "erori_campuri" in s, "migrare.js nu mai citeste erori_campuri la vector"
    assert 'tip_decont: "vf-decont"' in s, "maparea camp->grup (tip_decont->vf-decont) lipseste"
    assert 'classList.add("camp-invalid")' in s, "grupul vinovat nu mai e marcat (camp-invalid)"
