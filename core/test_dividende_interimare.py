# -*- coding: utf-8 -*-
"""GARD — regularizarea dividendelor interimare (lot 19, defectul 9, 03.10.2026).

Înainte: nota de regularizare purta 5121=463 la BRUT, datată la aprobarea situațiilor anuale — o încasare care nu
avusese loc și mai mare decât cea posibilă (asociatul încasase netul). Impozitul aferent excesului nu apărea nicăieri.
Iar `nota_dividend` refuza cu „Salariul brut…”.
"""
import io
import os
import re
from decimal import Decimal

import pytest

from core import decontari_asociati as da

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_regularizarea_nu_inregistreaza_incasari():
    r = da.nota_regularizare_interimar(50000, 30000, impozit_interimar=5000)
    # OMFP 1802/2014 pct.423^2: regularizarea = „articol contabil 457 «Dividende de plată» = 463”
    assert r["linii"] == [("1171", "457", Decimal("30000.00")), ("457", "463", Decimal("30000.00"))]
    assert not [l for l in r["linii"] if l[0] == "5121"], "încasare fabricată la regularizare"


def test_excesul_se_imparte_in_net_de_la_asociat_si_impozit_de_la_buget():
    r = da.nota_regularizare_interimar(50000, 30000, impozit_interimar=5000)
    # exces 20.000; impozitul reținut efectiv 5.000 pe 50.000 -> 2.000 pe exces; asociatul restituie netul 18.000
    assert (r["exces_de_restituit"], r["impozit_de_recuperat"], r["net_de_restituit"]) == \
        (Decimal("20000.00"), Decimal("2000.00"), Decimal("18000.00"))


def test_impozitul_vine_din_retinerea_efectiva_nu_din_cota_zilei():
    # interimare 2025 la 10%: 5.000 pe 50.000; o regularizare în 2026 (cota 16%) ar fi dat 3.200 pe exces
    r = da.nota_regularizare_interimar(50000, 30000, impozit_interimar=5000)
    assert r["impozit_de_recuperat"] == Decimal("2000.00")


def test_exces_fara_impozit_retinut_refuza():
    with pytest.raises(ValueError, match="impozitul reținut"):
        da.nota_regularizare_interimar(50000, 30000)
    assert da.nota_regularizare_interimar(30000, 50000)["exces_de_restituit"] == 0   # fără exces nu se cere


def test_restituirea_incasata_e_5121_463_cu_suma_incasata():
    # OMFP 1802/2014, funcțiunea contului 463: creditul 463 = „sumele încasate reprezentând restituiri de dividende
    # datorate, conform legii (512, 531)”
    assert da.nota_restituire_dividend(18000)["linii"] == [("5121", "463", Decimal("18000.00"))]
    with pytest.raises(ValueError):
        da.nota_restituire_dividend(0)


def test_mesajul_dividendului_nu_mai_spune_salariu():
    with pytest.raises(ValueError, match="Dividendul brut"):
        da.nota_dividend(0)


def test_ecranul_poate_inregistra_interimare_si_restituirea():
    # formularul citit cu parserul gărzii formularelor (structura câmpurilor, nu sub-șiruri)
    from core.test_formulare_operatiuni_campuri import formulare
    js = io.open(os.path.join(RAD, "static/js/ecrane/operatiuni_ecran.js"), encoding="utf-8").read()
    campuri = {c["nume"]: c for ch, ruta, cs in formulare(js) if ruta == "nota-asociati" for c in cs}
    assert campuri["interimar"]["optiuni"] == ["0", "1"] and campuri["interimar"]["cond"] == ("operatie", ["dividend"])
    assert "restituire_dividend" in campuri["operatie"]["optiuni"]
    assert campuri["suma_restituita"]["cond"] == ("operatie", ["restituire_dividend"])
    assert campuri["impozit_interimar"]["cond"] == ("operatie", ["regularizare"])
    uc = io.open(os.path.join(RAD, "core/uc_tenants.py"), encoding="utf-8").read()
    import ast
    fn = [n for n in ast.parse(uc).body if isinstance(n, ast.FunctionDef) and n.name == "nota_asociati"][0]
    bife = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "bifa"
            and len(n.args) > 1 and isinstance(n.args[1], ast.Constant) and n.args[1].value == "interimar"]
    assert bife, "„0” din select ar fi citit ca interimar (bifa nu mai e folosită în nota_asociati)"
    assert re.search(r'op == "restituire_dividend"', uc)
