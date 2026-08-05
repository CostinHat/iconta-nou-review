# -*- coding: utf-8 -*-
"""
core/test_gard_masca_zero.py — GARD C5 (clasa oarba "mascarea erorii / zero tacut", GARZI cat.0).

Cauza radacina transversala: un `except: return 0` (sau `pass` / `return []` / `return None`) pe o cale de BANI
inghite eroarea si emite 0/gol TACIT -> trece toate verificarile downstream (0 e "absenta legitima"). Dovedit trait:
`_d112int` avea `except: return 0` care facea ca o valoare stricata sa devina 0 in D112 fara niciun semnal (MASCA
SCOASA 27.07.2026, vezi comentariul din core/d112.py).

Acest gard interzice, prin analiza AST, ca un handler de exceptie din modulele de BANI (generatoare + calcul fiscal
+ reconcilieri) sa aiba corpul FORMAT DOAR din `pass` sau `return <zero/gol>`. Un except care LOGHEAZA, RIDICA, sau
returneaza o valoare NON-triviala e permis; masca tacuta la zero nu.

NON-TAUTOLOGIE: gardul nu recalculeaza nimic fiscal - e o proba STRUCTURALA (AST), independenta de valori.
LIMITA declarata: prinde DOAR tiparul sintactic `except -> pass/return zero` in modulele listate; un `except` care
mascheaza altfel (ex. `x = 0` in corp) NU e prins de acest gard (alt tipar). Lista de module e explicita (cat.4/
"Iesire catre autoritati" + calcul fiscal); un modul de bani nou trebuie adaugat aici.
"""
import ast
import os

# Modulele de BANI: generatoare de declaratii + calcul fiscal + reconcilieri (calea 2 + artefact).
_MODULE_BANI = (
    "d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406", "d710",
    "salarizare", "verificatoare", "reconciliere_emis",
    "d101_reconciliere", "d112_reconciliere", "d205_reconciliere",
    "d300_reconciliere", "d394_reconciliere", "d406_reconciliere",
)


def _e_zero_sau_gol(n):
    """True daca nodul e un literal 0 / 0.0 / "" / None / [] / {} / () - o valoare de MASCA."""
    # NOTA: None si False EXCLUSE deliberat - / pe un parser/validator (ex.
    # salarizare._pd parseaza o data, None = "nu-i data") e legitim si adesea intentionat (dict.get, bool valid).
    # Masca PERICULOASA cat.0 e ZERO/GOL numeric tacut ( din _d112int) care trece checkurile
    # aritmetice downstream. Un None pe cale de bani ar da TypeError downstream (mai zgomotos), nu masca tacuta.
    if n is None:
        return False
    if isinstance(n, ast.Constant):
        return n.value in (0, 0.0, "")
    if isinstance(n, ast.List) and not n.elts:
        return True
    if isinstance(n, ast.Dict) and not n.keys:
        return True
    if isinstance(n, ast.Tuple) and not n.elts:
        return True
    return False


def scan_masca(src):
    """Intoarce [(lineno, snippet), ...] pt handlerele de exceptie al caror corp e DOAR pass/return-zero-gol."""
    hits = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return hits
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and len(node.body) == 1:
            b = node.body[0]
            masca = isinstance(b, ast.Pass) or (isinstance(b, ast.Return) and _e_zero_sau_gol(b.value))
            if masca:
                kind = "pass" if isinstance(b, ast.Pass) else ("return %r" % (getattr(b.value, "value", None)
                                                                              if isinstance(b.value, ast.Constant) else "gol"))
            if masca:
                hits.append((node.lineno, kind))
    return hits


def test_module_bani_fara_except_masca_zero():
    """Niciun modul de bani nu are `except: pass` sau `except: return <zero/gol>` (masca tacuta a erorii)."""
    rad = os.path.dirname(os.path.dirname(__file__))  # radacina repo (parinte de core/)
    probleme = {}
    for nume in _MODULE_BANI:
        cale = os.path.join(rad, "core", nume + ".py")
        assert os.path.exists(cale), "modul de bani inexistent (actualizeaza lista _MODULE_BANI): %s" % cale
        hits = scan_masca(open(cale, encoding="utf-8").read())
        if hits:
            probleme[nume] = hits
    assert not probleme, (
        "except-masca (inghite eroarea -> 0/gol tacut) in module de bani - inlocuieste cu ridicare/semnalare: %s"
        % probleme)


def test_gardul_prinde_masca_MUTATIE():
    """MUTATIE (dovada ca gardul MUSCA): un snippet cu `except: return 0` / `except: pass` e PRINS de scan;
    un except care RIDICA sau returneaza o valoare reala NU e prins (fara fals-pozitiv)."""
    prins_return0 = scan_masca("def f():\n try:\n  return calc()\n except Exception:\n  return 0\n")
    prins_pass = scan_masca("def f():\n try:\n  x()\n except Exception:\n  pass\n")
    prins_gol = scan_masca("def f():\n try:\n  return q()\n except Exception:\n  return []\n")
    assert prins_return0, "gardul NU prinde `except: return 0` - inutil"
    assert prins_pass, "gardul NU prinde `except: pass` - inutil"
    assert prins_gol, "gardul NU prinde `except: return []` - inutil"
    # fara fals-pozitiv: except care RIDICA sau returneaza valoare reala
    ok_ridica = scan_masca("def f():\n try:\n  return calc()\n except Exception as e:\n  raise ValueError(str(e))\n")
    ok_val = scan_masca("def f():\n try:\n  return calc()\n except Exception:\n  return fallback_real()\n")
    ok_asign = scan_masca("def f():\n try:\n  x()\n except Exception:\n  y = set()\n")
    assert not ok_ridica and not ok_val and not ok_asign, (
        "fals-pozitiv: gardul prinde un except LEGITIM (ridica / valoare reala / asignare): %s %s %s"
        % (ok_ridica, ok_val, ok_asign))
