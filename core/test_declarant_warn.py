# -*- coding: utf-8 -*-
"""core/test_declarant_warn.py — GARD: cand declarantul lipseste din profil, generatoarele nu fabrica TACIT "ADMINISTRATOR".
17.08.2026 (audit tenant_001, thread 3): implicitul ramanea, dar AVERTIZAT. [lotul 10, C69 — supersedeaza] implicitul s-a scos:
lipsa declarantului OPRESTE generarea (`firma_profil_api.erori_declarant`, R101), iar garda verifica, pe AST, poarta si absenta
formei `prof.get("declarant_…") or "<constanta>"`. Regula 4."""
import ast
import io

# (fisier de cod ce emite declarantul) -> avertizeaza cand lipseste. bilant sta in bilant_api.
# [lotul 10, C69] bilanțul a ieșit de aici: nu mai avertizează, se OPREȘTE (decizia Costin „Câmpuri noi + blocaj” — administratorul
# din declarant, „19. nume_admin … DA”); garda lui e mai jos și în core/test_lot10_c69_bilant.py
_DECL = {"d100":"core/d100.py","d101":"core/d101.py","d205":"core/d205.py","d112":"core/d112.py",
         "d300":"core/d300.py","d301":"core/d301.py","d390":"core/d390.py"}


def test_toate_declaratiile_opresc_declarantul_lipsa_fara_implicit():
    """[C69, lotul 10 — supersedează „avertizează”] Toate opresc lipsa declarantului prin `erori_declarant` (R101) ÎNAINTE de build_xml,
    deci avertismentul „se trece implicit ADMINISTRATOR” era cod mort și s-a scos, odată cu implicitul. Garda: fiecare generator cheamă
    `erori_declarant`, și niciunul nu mai are implicitul (garda pe formă: core/test_lot10_c69_declarant_fara_implicit.py)."""
    cu_poarta = {d for d, path in _DECL.items() if _cheama_erori_declarant(_arbore(path))}
    assert cu_poarta == set(_DECL), "declaratii fara poarta declarantului: %s" % sorted(set(_DECL) - cu_poarta)
    implicite = {d: _implicite_declarant(_arbore(path)) for d, path in _DECL.items()}
    assert {d: l for d, l in implicite.items() if l} == {}, "implicit pe declarant (linia): %s" % implicite


def _arbore(path):
    return ast.parse(io.open(path, encoding="utf-8").read())


def _cheama_erori_declarant(arb):
    """Generatorul cheamă `firma_profil_api.erori_declarant` (direct sau prin aliasul importului, ex. `as _ed`) — nod de apel, nu text."""
    nume = {a.asname or a.name for n in ast.walk(arb) if isinstance(n, ast.ImportFrom) and n.module == "core.firma_profil_api"
            for a in n.names if a.name == "erori_declarant"}
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in nume for n in ast.walk(arb))


def _implicite_declarant(arb):
    """Liniile cu forma implicitului: `prof.get("declarant_…") or "<constantă>"` (un `or` între citirea câmpului și un șir fix)."""
    out = []
    for n in ast.walk(arb):
        if not (isinstance(n, ast.BoolOp) and isinstance(n.op, ast.Or)):
            continue
        citiri = [v for v in n.values if isinstance(v, ast.Call) and getattr(v.func, "attr", None) == "get" and v.args
                  and isinstance(v.args[0], ast.Constant) and str(v.args[0].value).startswith("declarant_")]
        if citiri and any(isinstance(v, ast.Constant) and isinstance(v.value, str) for v in n.values):
            out.append(n.lineno)
    return out


def test_gardul_implicitului_vede_forma_veche():
    """Anti-vacuu: forma scoasă la C69 (`prof.get("declarant_nume") or "ADMINISTRATOR"`) e prinsă, cea nouă nu."""
    assert _implicite_declarant(ast.parse('x = _t(prof.get("declarant_nume") or den or "ADMINISTRATOR", 75)')) == [1]
    assert _implicite_declarant(ast.parse('x = _t(prof.get("declarant_nume"), 75)')) == []
    assert _cheama_erori_declarant(ast.parse("from core.firma_profil_api import erori_declarant as _ed\ne = _ed(prof)"))
    assert not _cheama_erori_declarant(ast.parse("e = []"))


def test_bilantul_nu_fabrica_administratorul_il_cere():
    """[lotul 10, C69] Bilanțul nu mai scrie „ADMINISTRATOR”: fără numele și prenumele declarantului se oprește (`bilant.erori_antet`)."""
    from core import bilant
    for path in ("core/bilant.py", "core/bilant_api.py"):
        assert '"ADMINISTRATOR"' not in io.open(path, encoding="utf-8").read(), path
    erori = bilant.erori_antet({"cod_judet": 40, "mare_contribuabil": False, "forma_proprietate": "35", "interes_public": False, "calit_intocmit": 12, "intocmit_nume": "IONESCU MARIA"})
    assert len(erori) == 1, erori                                    # numai administratorul lipsește („19. nume_admin … DA”)
    assert "administratorului lipsesc" in erori[0], erori
