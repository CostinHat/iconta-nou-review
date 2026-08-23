# -*- coding: utf-8 -*-
"""core/scan_conflicte_sursa.py — INTERDICȚIA 58, partea nemăsurată: conflictele NEÎNREGISTRATE.

Prima măsurătoare a lui 58 (23.08) a dat **0 conflicte nedecise**, dar cu limita scrisă pe față: vede
doar ce e deja în `registru_interpretari`. Un conflict pe care nimeni nu l-a observat nu apare nicăieri.
Asta caută scanul de aici.

CE E UN CANDIDAT, mecanic: un loc din cod unde se întâlnesc **două surse de niveluri diferite** —
o citare legală (`art.`, `Legea`, `OUG`, `OMFP`, `OPANAF`) **și** o autoritate de nivel inferior
(`structura`, `validator`, `DUK`, `XSD`, `jar`, `nomenclator ANAF`). Acolo cineva a ales, fie că a
scris-o sau nu. Dacă alegerea e în `registru_interpretari`, e DECISĂ; dacă nu, e CANDIDAT.

CE NU E, și de aceea cifra e o listă de citit, nu o listă de defecte: cele două surse se pot întâlni
și fără să se contrazică — codul poate cita legea pentru regulă și structura pentru FORMATUL în care
se raportează. Contradicția se citește, nu se deduce. Scanul strânge locurile, omul decide.

CALIBRARE: locul unde s-a ales podeaua part-time (structura ANAF pune diminuarea în formula
part_time, textul legii vorbește de normă întreagă) TREBUIE să apară. E singurul conflict cunoscut și
decis; dacă scanul nu-l vede, nu poate pretinde că i-ar vedea pe cei necunoscuți.
"""
import ast
import pathlib
import re

RAD = pathlib.Path(__file__).resolve().parents[1]

_LEGAL = re.compile(r"\bart\.\s*\d|\bLegea\s+\d|\bOUG\s+\d|\bO\.?U\.?G\.?\s*\d|\bOMFP\s+\d"
                    r"|\bOPANAF\s+\d|\bHG\s+\d|\bCod(?:ul)?\s+fiscal", re.I)
_INFERIOR = re.compile(r"\bstructur[aă]\b|\bvalidator|\bDUK\b|\bXSD\b|\bjar\b|\bnomenclator(?:ul)?\s+ANAF"
                       r"|\bstruct\b|\bschema\s+ANAF", re.I)

_NEFISCALE = re.compile(r"^(db|auth|observare|main|conftest|scan_|test_|agenda|graf_|migrare_|gen_)")


def _blocuri(p):
    """[(nume, text)] — docstringul + comentariile fiecărei funcții de nivel de modul."""
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
        arb = ast.parse(src)
    except (OSError, SyntaxError):
        return []
    linii = src.split("\n")
    out = []
    for n in arb.body:
        if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        st = n.lineno - 1
        sf = getattr(n, "end_lineno", n.lineno)
        out.append((n.name, "\n".join(linii[st:sf])))
    # si antetul modulului
    doc = ast.get_docstring(arb)
    if doc:
        out.append(("<antet modul>", doc))
    return out


def candidati():
    """[(fisier, nume, fragment)] — locuri unde se întâlnesc o sursă legală și una inferioară."""
    out = []
    for p in sorted(RAD.glob("core/*.py")):
        if _NEFISCALE.match(p.stem):
            continue
        for nume, text in _blocuri(p):
            # doar în PROZĂ: comentarii și docstring, acolo se scrie autoritatea
            proza = "\n".join(l for l in text.split("\n")
                              if l.strip().startswith("#") or '"""' in l or "'''" in l
                              or not re.match(r"^\s*[a-zA-Z_\[\(]", l))
            if not proza.strip():
                proza = text
            if _LEGAL.search(proza) and _INFERIOR.search(proza):
                m = _INFERIOR.search(proza)
                k = m.start()
                frag = re.sub(r"\s+", " ", proza[max(0, k - 150):k + 150]).strip()
                out.append((p.name, nume, frag))
    return out


def decise():
    """Cheile din registrul de interpretări, plus modulele pe care le ating."""
    from core import registru_interpretari as ri
    return set(ri.INTERPRETARI)


if __name__ == "__main__":
    c = candidati()
    import collections
    per = collections.Counter(f for f, _n, _fr in c)
    print("INTERDICTIA 58 — locuri unde se intalnesc o sursa LEGALA si una INFERIOARA")
    print("   candidati: %d, in %d fisiere" % (len(c), len(per)))
    print("   decise si consemnate in registrul de interpretari: %d" % len(decise()))
    print()
    for f, n in per.most_common(12):
        print("   %-30s %d" % (f, n))
    print()
    print("   primele, cu fragmentul:")
    for f, n, fr in c[:10]:
        print("      %-22s %-28s %s" % (f, n[:28], fr[:110]))
