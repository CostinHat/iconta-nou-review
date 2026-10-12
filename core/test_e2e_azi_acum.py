# -*- coding: utf-8 -*-
"""GARD — „azi” fixat la importul unui test e2e, comparat cu ce datează aplicația ACUM (13.10.2026, prins de poarta lotului C14 / C15).

CE ERA: plasa a pornit la 23:5x, iar testul 167 a comparat „Generată la 13.10.2026 00:01” (momentul generării PDF-ului) cu AZI =
12.10.2026, fixat la importul modulului (`AZI = _dt.date.today()`). Testul era roșu fără ca aplicația să greșească — iar poarta respingea
publicarea. Din cele 12 aserțiuni cu AZI (5 fișiere), 8 comparau ce datează aplicația acum (data implicită a facturii pe ecran, scadența,
jurnalul Date firmă, telemetria, momentul generării); 4 compară date pe care testul le-a dat el (marcate).

CE FACE IMPOSIBIL: o aserțiune e2e care folosește AZI fără să spună ce fel de dată compară — fie `zile_de_acum(AZI)` (conftest: ziua de la
import SAU cea de acum, pentru ce datează aplicația acum), fie marcajul `# AZI-dat-de-test` pe una din liniile ei (data pe care testul
însuși a dat-o aplicației; acolo AZI e chiar valoarea așteptată).
MUTAȚIE: `zile_de_acum` scos din aserțiunea testului 167 -> pică."""
import ast
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_E2E = os.path.join(_RAD, "frontend_test", "e2e")


def _aserțiuni_cu_azi():
    out = []
    for f in sorted(os.listdir(_E2E)):
        if not f.endswith(".py"):
            continue
        src = open(os.path.join(_E2E, f), encoding="utf-8").read()
        linii = src.splitlines()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Assert) and any(isinstance(x, ast.Name) and x.id == "AZI" for x in ast.walk(n)):
                text = "\n".join(linii[n.lineno - 1:n.end_lineno])
                out.append((f, n.lineno, text))
    return out


def test_fiecare_asertiune_cu_azi_spune_ce_data_compara():
    toate = _aserțiuni_cu_azi()
    rele = [(f, ln, t.strip()[:120]) for f, ln, t in toate if "zile_de_acum(" not in t and "# AZI-dat-de-test" not in t]
    assert len(toate) >= 12 and not rele, rele
