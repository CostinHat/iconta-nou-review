# -*- coding: utf-8 -*-
"""[deficiența 392, retestul Costin 19.10.2026] „Solduri inițiale: 5121 cu sold creditor intră fără avertisment la import (auditul de
preluare îl prinde).” O singură regulă (`audit_preluare.parte_gresita`) pentru audit și pentru previzualizare. Temei: OMFP 1802/2014
pct.593 alin.(2): „Conturile pot avea funcțiune contabilă de activ (A), pasiv (P) sau sunt bifuncționale (A/P). În general, conturile cu
funcțiune contabilă de activ corespund elementelor de natura activelor [...]”; 5121 „Conturi la bănci în lei” e (A) în pct.594."""
import ast
import inspect
import textwrap

from core import audit_preluare as ap, uc_tenants


def test_5121_creditor_e_semnalat():
    assert ap.parte_gresita("5121", 0, 20000) == "5121 (activ) are sold creditor 20.000,00 lei"


def test_pasivul_debitor_si_analiticul():
    assert ap.parte_gresita("401.00012", 50, 0) == "401.00012 (pasiv) are sold debitor 50,00 lei"
    assert ap.parte_gresita("5121", 20000, 0) is None and ap.parte_gresita("4428", 0, 10) is None   # pct.594: „4428. TVA neexigibilă (A/P)”


def _cheama(f):
    """Funcțiile `audit_preluare` chemate în corpul funcției, din arborele sintactic (nu un sub-șir din sursă: un comentariu n-ar conta);
    un import local `from core.audit_preluare import x as _x` se rezolvă la `x`."""
    arb = ast.parse(textwrap.dedent(inspect.getsource(inspect.unwrap(f))))
    alias = {a.asname or a.name: a.name for n in ast.walk(arb) if isinstance(n, ast.ImportFrom) and n.module == "core.audit_preluare"
             for a in n.names}
    chemate = {getattr(n.func, "attr", None) or getattr(n.func, "id", None) for n in ast.walk(arb) if isinstance(n, ast.Call)}
    return {alias.get(c, c) for c in chemate}


def test_auditul_si_previzualizarea_folosesc_aceeasi_regula():
    assert {"parte_gresita"} <= _cheama(ap.verifica_parte_sold) & _cheama(uc_tenants.solduri_incarca)
