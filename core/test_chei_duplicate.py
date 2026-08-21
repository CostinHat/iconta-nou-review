# -*- coding: utf-8 -*-
"""GARDĂ: o cheie care apare de două ori în același dicționar e o intrare MOARTĂ. (21.08.2026)

CUM A IEȘIT. Un patch s-a aplicat de două ori și a scris `"creare_esuata": {...}` de două ori în
`migrare_api.REGULI`. Python păstrează ultima și o aruncă tăcut pe prima — `len(REGULI)` era corect,
testele treceau, iar sursa avea un bloc duplicat despre care nimeni n-ar fi aflat. Ruff nu prinde
clasa asta.

DE CE E PERICULOASĂ AICI. Într-un nomenclator fiscal, două intrări cu aceeași cheie și valori DIFERITE
înseamnă că una dintre reguli e ignorată — și e ultima scrisă care câștigă, adică ordinea din fișier
decide ce cotă sau ce temei se aplică. Nimeni nu citește un dicționar de 25 de intrări căutând
duplicate.

Se verifică și dicționarele imbricate, și `dict(...)` cu argumente-cheie repetate n-are cum să apară
(Python ridică singur acolo) — deci domeniul e literalul `{...}`.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SARI = ("venv", ".git", "_arhiva", "node_modules", "__pycache__")


def _fisiere():
    for rad, dirs, fis in os.walk(RAD):
        dirs[:] = [d for d in dirs if d not in SARI]
        for f in fis:
            if f.endswith(".py"):
                yield os.path.join(rad, f)


def duplicate():
    """[(fisier, linie, cheie)] — chei care apar de mai multe ori în același literal de dicționar."""
    out = []
    for p in sorted(_fisiere()):
        try:
            arb = ast.parse(io.open(p, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = os.path.relpath(p, RAD).replace(os.sep, "/")
        for n in ast.walk(arb):
            if not isinstance(n, ast.Dict):
                continue
            vazute = set()
            for k in n.keys:
                if not (isinstance(k, ast.Constant) and isinstance(k.value, (str, int))):
                    continue
                if k.value in vazute:
                    out.append((rel, k.lineno, k.value))
                vazute.add(k.value)
    return out


def test_nicio_cheie_duplicata():
    rele = ["  %s:%d  cheia %r apare a doua oară" % x for x in duplicate()]
    assert not rele, (
        "chei duplicate în literale de dicționar — Python o păstrează pe ULTIMA și o aruncă tăcut pe "
        "prima:\n" + "\n".join(rele))


def test_gardul_chiar_vede_un_duplicat(tmp_path):
    """ANTI-VACUU pe mecanism: dacă detectorul n-ar deosebi, testul de sus ar trece pe gol pentru
    totdeauna. Se probează pe un fișier construit, nu pe repo."""
    f = tmp_path / "cu_duplicat.py"
    f.write_text('X = {"a": 1, "b": 2, "a": 3}\n', encoding="utf-8")
    arb = ast.parse(f.read_text(encoding="utf-8"))
    d = [n for n in ast.walk(arb) if isinstance(n, ast.Dict)][0]
    chei = [k.value for k in d.keys if isinstance(k, ast.Constant)]
    assert len(chei) != len(set(chei)), "AST-ul nu mai păstrează cheile duplicate — schimbă detectorul"


def test_domeniul_nu_s_a_ingustat():
    """Un scan care nu mai vede fișiere raportează verde despre o lume goală."""
    n = sum(1 for _ in _fisiere())
    assert n >= 200, "doar %d fișiere .py văzute — domeniul s-a îngustat" % n
