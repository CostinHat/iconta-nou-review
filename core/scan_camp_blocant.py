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


# Ajutoare de validare care traiesc in ALT modul si sunt chemate din functiile blocante. Se declara
# aici, pe nume, nu se urmaresc toate apelurile: o sonda care intra oriunde ar deveni un interpretor.
# [R101, 30.08.2026] `erori_declarant` a aparut fiindca cele trei campuri ale declarantului sunt
# cerute de structura ANAF a TUTUROR celor opt declaratii — deci verificarea are un singur loc, iar
# sonda trebuie sa stie sa ajunga la el. Fara asta ar fi raportat „nu opreste", desi opreste.
AJUTOARE = {"erori_declarant": "firma_profil_api"}


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


def _campuri_ajutor(nume_ajutor):
    """Campurile de profil verificate de un ajutor declarat, citite in modulul lui."""
    cale = os.path.join(RAD, "core", "%s.py" % AJUTOARE[nume_ajutor])
    if not os.path.exists(cale):
        return set()
    arb = ast.parse(io.open(cale, encoding="utf-8").read(), filename=cale)
    fn = next((n for n in arb.body if isinstance(n, ast.FunctionDef) and n.name == nume_ajutor), None)
    return _campuri_profil(fn) if fn is not None else set()


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

    def _porti(corp):
        """Functiile al caror rezultat e RIDICAT in `corp`: `x = f(...)` + `if x: raise`, sau
        `if f(...): raise`."""
        gasite, atribuiri = set(), {}
        for n in ast.walk(corp):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                nume_f = getattr(n.value.func, "id", None)
                for tinta in n.targets:
                    if isinstance(tinta, ast.Name) and nume_f:
                        atribuiri[tinta.id] = nume_f
        for n in ast.walk(corp):
            if not isinstance(n, ast.If):
                continue
            if not any(isinstance(x, ast.Raise) for x in ast.walk(n)):
                continue
            if isinstance(n.test, ast.Name) and atribuiri.get(n.test.id) in fn:
                gasite.add(atribuiri[n.test.id])
            gasite |= {c for c in _apeluri(n.test) if c in fn}
        return gasite

    # RAZA: `genereaza`, plus functiile LOCALE pe care le cheama (doua niveluri). Fara asta, o
    # poarta ridicata intr-un ajutor — `calculeaza` la D390 — ar aparea ca inexistenta, iar garda ar
    # raporta „nu opreste" despre un cod care opreste. Masurat: exact cazul D390, 30.08.2026.
    vazute, coada = set(), ["genereaza"]
    for _adancime in range(3):
        urmatoare = []
        for nume_f in coada:
            if nume_f in vazute or nume_f not in fn:
                continue
            vazute.add(nume_f)
            blocante |= _porti(fn[nume_f])
            urmatoare += [c for c in _apeluri(fn[nume_f]) if c in fn and c not in vazute]
        coada = urmatoare

    # `for e in f(...): ... avertismente...` — cautat pe aceeasi raza
    for nume_f in vazute:
        for n in ast.walk(fn[nume_f]):
            if isinstance(n, ast.For) and isinstance(n.iter, ast.Call):
                nume_i = getattr(n.iter.func, "id", None)
                if nume_i in fn and any("avertismente" in ast.dump(x) for x in n.body):
                    avert.add(nume_i)

    # aliasurile sub care sunt importate ajutoarele declarate: `import erori_declarant as _ed`
    alias = {}
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name in AJUTOARE:
                    alias[a.asname or a.name] = a.name

    camp_bloc, camp_avert = set(), set()
    for nume in blocante:
        camp_bloc |= _campuri_profil(fn[nume])
        # ajutorul declarat, chemat din functia blocanta: campurile LUI opresc si ele
        for chemat in _apeluri(fn[nume]):
            if chemat in alias:
                camp_bloc |= _campuri_ajutor(alias[chemat])
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
