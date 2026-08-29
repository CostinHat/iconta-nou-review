# -*- coding: utf-8 -*-
"""CE OPREȘTE EFECTIV FIECARE GENERATOR DE DECLARAȚIE — instrumentul lui R93, 30.08.2026.

DE CE EXISTĂ. `firma_profil_api.OBLIGATORII` e o **afirmație**: „câmpul `adresa` e obligatoriu la
D100, D205 și D394". R93 a arătat că afirmația poate fi adevărată în trei module și falsă în al
patrulea: aceeași verificare — *„LIPSĂ adresă domiciliu fiscal (obligatorie)"* — era `raise` la
D100/D101/D205 și **avertisment** la D394, iar prețul l-a plătit contabilul, sub forma unei erori
brute a validatorului ANAF în loc de propoziția pe care aplicația o avea deja scrisă.

Deci: harta trebuie confruntată cu **ce oprește efectiv codul**, în amândouă direcțiile.

CUM MĂSOARĂ, pe AST și nu pe text (METODA §23):
  1. în `genereaza` se caută ce funcții au rezultatul **ridicat** — tiparul `x = f(...)` urmat de
     `if x: raise`, sau `if f(...): raise`. Alea sunt **funcțiile blocante**;
  2. se caută ce funcții au rezultatul împins în **`avertismente`** — alea sunt **funcțiile de
     avertisment**;
  3. în corpul fiecăreia se citesc câmpurile de profil atinse: `prof.get("X")`, `prof["X"]`,
     `res.prof.get("X")`. Astea sunt câmpurile pe care funcția le **verifică**.

Rezultatul: pentru fiecare modul, {blocante} și {doar_avertisment}. Un câmp care e în `OBLIGATORII`
pentru modulul ăla și apare **doar** în a doua mulțime e chiar forma lui R93.

CE NU VEDE, declarat:
  - o verificare făcută **fără să citească `prof`** (de exemplu pe `res.luna`) — nu are câmp de
    atribuit, deci nu intră în hartă; se numără separat;
  - o poartă care oprește **mai devreme**, în `pull` sau într-un ajutor chemat indirect — sonda se
    uită doar la funcțiile numite direct în `genereaza`;
  - dacă mesajul e **bun**. Că un refuz e citibil de un contabil e o judecată de om.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Modulele de declarație care au `genereaza(conn, schema, perioada, ...)`. Se declară aici, ca
# domeniul să fie vizibil: o listă derivată din numele fișierelor ar tăcea la un modul nou.
MODULE = ("d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406")


def _fisier(mod):
    return os.path.join(RAD, "core", "%s.py" % mod)


def _campuri_profil(nod):
    """Câmpurile de profil citite în subarborele `nod`: prof.get("X") / prof["X"] / res.prof.get("X")."""
    out = set()
    for n in ast.walk(nod):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "get" and n.args:
            baza = getattr(n.func, "value", None)
            nume_baza = getattr(baza, "id", None) or getattr(baza, "attr", None)
            if nume_baza == "prof" and isinstance(n.args[0], ast.Constant):
                out.add(n.args[0].value)
        if isinstance(n, ast.Subscript):
            baza = n.value
            nume_baza = getattr(baza, "id", None) or getattr(baza, "attr", None)
            if nume_baza == "prof" and isinstance(n.slice, ast.Constant):
                out.add(n.slice.value)
    return out


def _apeluri(nod):
    """Numele funcțiilor apelate direct în subarborele `nod`."""
    out = set()
    for n in ast.walk(nod):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "id", None)
            if nume:
                out.add(nume)
    return out


def _functii(arb):
    return {n.name: n for n in arb.body if isinstance(n, ast.FunctionDef)}


def analizeaza(mod):
    """{blocante, avertisment, campuri_blocante, campuri_avertisment, ridica_direct}."""
    cale = _fisier(mod)
    if not os.path.exists(cale):
        return None
    arb = ast.parse(io.open(cale, encoding="utf-8").read(), filename=cale)
    fn = _functii(arb)
    gen = fn.get("genereaza")
    if gen is None:
        return None

    blocante, avert = set(), set()
    # (a) `x = f(...)` apoi `if x: raise`  ·  (b) `if f(...): raise`
    atribuiri = {}
    for n in ast.walk(gen):
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
            nume = getattr(n.value.func, "id", None)
            for t in n.targets:
                if isinstance(t, ast.Name) and nume:
                    atribuiri[t.id] = nume
    for n in ast.walk(gen):
        if not isinstance(n, ast.If):
            continue
        are_raise = any(isinstance(x, ast.Raise) for x in ast.walk(n))
        if not are_raise:
            continue
        # ce e in test
        if isinstance(n.test, ast.Name) and n.test.id in atribuiri:
            blocante.add(atribuiri[n.test.id])
        blocante |= {c for c in _apeluri(n.test) if c in fn}
    # `for e in f(...): ... avertismente...`
    for n in ast.walk(gen):
        if isinstance(n, ast.For) and isinstance(n.iter, ast.Call):
            nume = getattr(n.iter.func, "id", None)
            if nume in fn and any("avertismente" in ast.dump(x) for x in n.body):
                avert.add(nume)

    camp_bloc, camp_avert = set(), set()
    for nume in blocante:
        camp_bloc |= _campuri_profil(fn[nume])
    for nume in avert:
        camp_avert |= _campuri_profil(fn[nume])
    return {"blocante": sorted(blocante), "avertisment": sorted(avert),
            "campuri_blocante": sorted(camp_bloc),
            "campuri_doar_avertisment": sorted(camp_avert - camp_bloc)}


def masoara():
    return {m: analizeaza(m) for m in MODULE if analizeaza(m) is not None}


if __name__ == "__main__":
    r = masoara()
    print("module analizate: %d din %d" % (len(r), len(MODULE)))
    for m, d in sorted(r.items()):
        print("\n%s" % m.upper())
        print("  functii BLOCANTE   : %s" % (d["blocante"] or "—"))
        print("  functii AVERTISMENT: %s" % (d["avertisment"] or "—"))
        print("  campuri oprite     : %s" % (d["campuri_blocante"] or "—"))
        print("  campuri DOAR avert.: %s" % (d["campuri_doar_avertisment"] or "—"))
