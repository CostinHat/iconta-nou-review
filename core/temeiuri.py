# -*- coding: utf-8 -*-
"""core/temeiuri.py - gaseste locurile din cod care CITEAZA un temei (act normativ sau regula de
validator). Pe forme PARTIALE: cauti ACTUL, nu potrivirea exacta - "OUG 89/2025" gaseste si
"OUG 89/2025 art.III alin.(4) lit.b". La o schimbare legislativa, primul pas e o comanda, nu o
cautare manuala prin cod.

  python -m core.temeiuri "OUG 89/2025"            # act, cu tot ce-l citeaza (articolele incluse)
  python -m core.temeiuri "A91b"                   # regula de validator (gaseste "DUK regula A91b")
  python -m core.temeiuri "ANAF structura D300"    # structura ANAF

Output: fisier:linie [functia care contine linia] context. Functia (prin ast) spune CE face codul
acolo - o cota, un prag, o conditie - nu doar ca exista o linie."""
import ast
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent


def _functie_la_linie(tree, lineno):
    """Numele functiei/metodei care CONTINE linia (cea mai interioara), sau '<modul>' / '?'."""
    if tree is None:
        return "?"
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", None) or node.lineno
            if node.lineno <= lineno <= end and (best is None or node.lineno > best.lineno):
                best = node
    return best.name if best is not None else "<modul>"


def gaseste(query, radacina=None):
    """[{fisier, linie, functie, context}] pentru locurile din core/*.py care CONTIN `query`
    (substring -> formele partiale/cu articol se gasesc). O simpla cautare de text, deci acopera
    ambele categorii (normativ + validator) fara reguli separate."""
    rad = pathlib.Path(radacina) if radacina else _RAD
    q = query.strip()
    rez = []
    for f in sorted(rad.glob("core/*.py")):
        src = f.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            tree = None
        for i, line in enumerate(src.splitlines(), 1):
            if q and q in line:
                rez.append({"fisier": f.name, "linie": i,
                            "functie": _functie_la_linie(tree, i), "context": line.strip()})
    return rez


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print('uz: python -m core.temeiuri "<act|regula>"   (ex: "OUG 89/2025", "A91b", "ANAF structura D300")')
        sys.exit(2)
    q = sys.argv[1]
    hits = gaseste(q)
    if not hits:
        print("Niciun loc din core/ nu citeaza %r." % q)
        sys.exit(0)
    print("%d locuri citeaza %r:" % (len(hits), q))
    for h in hits:
        print("  %s:%d  [%s]  %s" % (h["fisier"], h["linie"], h["functie"], h["context"][:100]))
