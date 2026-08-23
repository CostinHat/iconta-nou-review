# -*- coding: utf-8 -*-
"""GARD (R26): nicio funcție fiscală nu are cotă implicită, iar REFUZUL chiar se produce.

CE FACE IMPOSIBIL — două lucruri, iar al doilea e cel care lipsea:
  1. ca un literal de cotă să reapară ca default de parametru (regresie de formă);
  2. ca funcția să **treacă tăcut** fără cotă — adică refuzul să fie scris și nefuncțional.

DE CE EXISTĂ A DOUA PARTE. Întrebarea lui Costin, 23.08.2026: *„reparația a fost verificată cum?
Testele acoperă acum căile, sau doar confirmă că defaultul a dispărut din semnătură?"* Răspunsul
onest era **a doua**: cele 15 fișiere de test actualizate atunci **dau** cota, deci verifică doar că
funcțiile calculează corect **cu** ea. Niciunul nu exercita calea fără cotă. Verificasem în direcția
ușoară — exact `METODA_VERIFICARE.md` §16.

CE NU FACE, declarat: nu verifică dacă mesajul de refuz e cel potrivit pentru fiecare funcție în
parte (e același text, verificat o dată), și nu acoperă funcțiile care primesc cota prin dicționar
(`corp["cota"]`) — acelea sunt apărate de `common.cota_ceruta`, altă poartă.
"""
import ast
import glob
import inspect
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_NUME_COTA = ("cota", "cota_tva", "cota_tva_implicita")


_SRC = {}


def _tinte():
    """[(modul, functie, param)] pentru parametrii de cotă cu default `None` ȘI cu refuz în corp."""
    out = []
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        f = os.path.basename(p)
        if f.startswith("test_"):
            continue
        src = io.open(p, encoding="utf-8").read()
        _SRC[f] = src
        try:
            arb = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            a = n.args
            poz = list(a.args)
            defs = [None] * (len(poz) - len(a.defaults)) + list(a.defaults)
            for arg, d in list(zip(poz, defs)) + list(zip(a.kwonlyargs, a.kw_defaults)):
                if arg.arg not in _NUME_COTA or not isinstance(d, ast.Constant) or d.value is not None:
                    continue
                # DOAR functiile care poarta refuzul. Restul trateaza `None` ca „nu se aplica"
                # (d101 fara cota pe o firma neplatitoare, `facturi.calcul_tva` pe o linie scutita) -
                # aia e alta clasa si ar fi un fals pozitiv. Distinctia se citeste din COD, nu din nume.
                corp_fn = ast.get_source_segment(_SRC[f], n) or ""
                if "%s is None" % arg.arg in corp_fn and "raise" in corp_fn:
                    out.append((f[:-3], n.name, arg.arg))
    return out


def test_ANTIVACUU_exista_tinte():
    """Dacă lista se golește, tot fișierul ar trece degeaba."""
    t = _tinte()
    assert len(t) >= 20, "prea puține funcții cu cotă fără default (%d) — s-au redenumit?" % len(t)


def test_nicio_cota_nu_mai_are_DEFAULT_CU_VALOARE():
    """Regresia de formă: un literal de cotă reapărut ca default."""
    rele = []
    for p in sorted(glob.glob(os.path.join(_RAD, "core", "*.py"))):
        f = os.path.basename(p)
        if f.startswith("test_"):
            continue
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except SyntaxError:
            continue
        for n in ast.walk(arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            a = n.args
            poz = list(a.args)
            defs = [None] * (len(poz) - len(a.defaults)) + list(a.defaults)
            for arg, d in list(zip(poz, defs)) + list(zip(a.kwonlyargs, a.kw_defaults)):
                if arg.arg in _NUME_COTA and isinstance(d, ast.Constant) \
                   and isinstance(d.value, (int, float)) and not isinstance(d.value, bool):
                    rele.append("  %s::%s(%s=%s)" % (f, n.name, arg.arg, d.value))
    assert not rele, ("cotă cu valoare implicită, din nou:\n" + "\n".join(rele)
                      + "\n\nCota se declară la apel. Vezi R26 și `common.cota_ceruta`.")


def _umple(par):
    """Argument inofensiv după numele parametrului — testul e despre REFUZ, nu despre calcul."""
    if par in ("linii", "randuri", "operatiuni"):
        return []
    if par in ("tva_pe",):
        return ()
    return 0


@pytest.mark.parametrize("modul,functie,param", _tinte())
def test_fara_cota_REFUZA(modul, functie, param):
    """Miezul, și partea care lipsea: chemată fără cotă, funcția ridică — nu calculează tăcut."""
    mod = __import__("core.%s" % modul, fromlist=[functie])
    fn = getattr(mod, functie)
    sig = inspect.signature(fn)
    kw = {}
    for nume, p in sig.parameters.items():
        if nume == param:
            continue
        if p.default is inspect.Parameter.empty and p.kind in (
                p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY):
            kw[nume] = _umple(nume)
    with pytest.raises(ValueError) as e:
        fn(**kw)
    assert "ot" in str(e.value), (
        "%s::%s a ridicat altceva decât refuzul de cotă: %s" % (modul, functie, e.value))
