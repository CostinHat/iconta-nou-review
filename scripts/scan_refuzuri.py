# -*- coding: utf-8 -*-
"""scripts/scan_refuzuri.py — CE POARTA un refuz al aplicatiei, si ce nu poarta.

Cerut de Costin ca inventar al locurilor unde aplicatia refuza, inaintea normei de blocaj-cu-temei.

CE MASOARA, exact: fiecare `raise` din `main.py` si `core/` care OPRESTE un act, si **ce poarta
refuzul cu el** — temeiul, ca date sau ca proza, sau nimic.

DE CE NU E ACELASI LUCRU CU `core/scan_refuz_tacut.py`: acela intreaba daca refuzul **ajunge** la om
(are un `catch` care afiseaza ceva). Asta intreaba daca refuzul **spune pe ce se sprijina**. Un refuz
poate ajunge perfect la om si sa fie, tot asa, o afirmatie fara temei — «nu se poate», fara sa spuna
cine zice asta. Cele doua populatii se suprapun, dar niciuna n-o cuprinde pe cealalta.

CELE PATRU MODURI DE ESEC ALE ACESTUI INSTRUMENT, scrise INAINTE de prima masuratoare
(interdictia 76, si de data asta chiar inainte):

  1. **NU EXECUTA.** Un refuz construit de un ajutor (`_refuz(camp, temei)`) si ridicat in alta parte
     e numarat la locul lui `raise`, unde temeiul nu se vede. Deci clasa `FARA` e un **PLAFON
     SUPERIOR**: pot exista refuzuri care poarta temei printr-un drum pe care scanul nu-l urmeaza.
  2. **NU DEOSEBESTE NORMATIV DE FORMA.** Un 400 «lipseste campul` si un 400 «norma nu permite» sunt
     amandoua refuzuri, iar temeiul e cerut doar de al doilea. Scanul le numara la un loc si **spune
     asta**; nu incearca sa ghiceasca normativitatea din text, fiindca ar fi exact ancorarea pe
     cuvinte pe care clichetul 50 o interzice. Cifra `FARA` amesteca deci doua populatii.
  3. **VEDE DOAR PYTHON.** Refuzurile din ecran (validare in JS inainte de cerere) nu sunt aici.
     Alta populatie, alt instrument.
  4. **VEDE DOAR `raise`.** O ruta care INTOARCE un corp de eroare fara sa ridice — `return
     {"eroare": ...}` — e invizibila. Numarate separat, ca sa se vada cat de mare e umbra.

CE NU MASOARA, declarat: daca temeiul e CORECT. Doar daca exista si sub ce forma.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Clasele de refuz, dupa CE OPRESTE refuzul. Nomenclator INCHIS.
CLASE = ("acces", "negasit", "refuz")

#: Cum poarta refuzul temeiul. Ordinea e de la tare la slab; un refuz primeste prima care se potriveste.
PURTATOR = ("structurat", "proza", "fara")

#: 401/403 = cine esti, nu ce ai cerut. Un temei legal n-ar avea ce cauta acolo — refuzul nu se
#: sprijina pe o norma fiscala, ci pe faptul ca nu ai acces. Declarate in afara clasei masurate.
_ACCES = (401, 403)
#: 404 e AMESTECAT prin constructie: si «tenant inexistent», si «fel necunoscut» (nomenclator inchis).
#: Se numara separat tocmai ca sa nu se topeasca in niciuna dintre celelalte doua.
_NEGASIT = (404,)

#: Semne ca proza refuzului trimite la un act. Lista supraevalueaza deliberat (prinde si `art.` dintr-un
#: `articol` de stoc), deci `proza` e plafon SUPERIOR si `fara` plafon INFERIOR. Directia se scrie.
_SEMNE_ACT = ("art.", "art ", "alin", "pct.", "OMFP", "OPANAF", "HG ", "Legea", "Cod fiscal",
              "Codul fiscal", "norma", "normele", "L227", "227/2015", "82/1991")


def _fisiere():
    out = [os.path.join(RAD, "main.py")]
    for f in sorted(os.listdir(os.path.join(RAD, "core"))):
        if f.endswith(".py") and not f.startswith(("test_", "scan_")):
            out.append(os.path.join(RAD, "core", f))
    return out


def _siruri(nod):
    """Toate sirurile literale din subarborele unui nod."""
    return [n.value for n in ast.walk(nod)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _poarta_temei_structurat(nod):
    """Temeiul ca DATE: un `temei=` cu nume, o cheie `"temei"` intr-un dict, un `Temei(...)`, sau un
    nume care incepe cu TEMEI. Se decide pe STRUCTURA, nu pe text."""
    for n in ast.walk(nod):
        if isinstance(n, ast.keyword) and n.arg == "temei":
            return True
        if isinstance(n, ast.Constant) and n.value == "temei":
            return True
        if isinstance(n, ast.Name) and (n.id == "Temei" or n.id.startswith("TEMEI")):
            return True
        if isinstance(n, ast.Attribute) and (n.attr == "temei" or n.attr.startswith("TEMEI")):
            return True
    return False


def _clasa_si_stare(nod):
    """(clasa, stare_http|None) pentru un `raise`. `None` daca nu e un refuz."""
    exc = nod.exc
    if exc is None:
        return None, None
    tinta = exc.func if isinstance(exc, ast.Call) else exc
    nume = tinta.id if isinstance(tinta, ast.Name) else getattr(tinta, "attr", None)
    if nume == "HTTPException":
        stare = None
        if isinstance(exc, ast.Call) and exc.args and isinstance(exc.args[0], ast.Constant):
            stare = exc.args[0].value
        if stare in _ACCES:
            return "acces", stare
        if stare in _NEGASIT:
            return "negasit", stare
        return "refuz", stare
    # exceptiile aplicatiei: orice nume care se termina in una din formele de refuz, plus ValueError
    if nume and (nume.endswith(("Incompleta", "IncompletaPF", "Neconstruibil", "Neconfirmata",
                                "Invalid", "Invalida", "Ratata", "Refuzat"))
                 or nume == "ValueError"):
        return "refuz", None
    return None, None


def inventar():
    """[{fisier, linia, functie, clasa, stare, purtator}] — un rand per `raise` care opreste un act."""
    out = []
    for cale in _fisiere():
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        parinte = {}
        for fn in ast.walk(arb):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for n in ast.walk(fn):
                    parinte.setdefault(id(n), fn.name)
        for n in ast.walk(arb):
            if not isinstance(n, ast.Raise):
                continue
            clasa, stare = _clasa_si_stare(n)
            if clasa is None:
                continue
            if _poarta_temei_structurat(n):
                purtator = "structurat"
            else:
                txt = " ".join(_siruri(n))
                purtator = "proza" if any(s in txt for s in _SEMNE_ACT) else "fara"
            out.append({"fisier": rel, "linia": n.lineno,
                        "functie": parinte.get(id(n), "(modul)"),
                        "clasa": clasa, "stare": stare, "purtator": purtator,
                        "citeaza": modul_citeaza_legea(cale)})
    return out


def refuzuri_care_INTORC():
    """Modul de esec 4, numarat: `return {"eroare": ...}` — refuz care nu trece prin `raise`."""
    out = []
    for cale in _fisiere():
        try:
            arb = ast.parse(io.open(cale, encoding="utf-8").read())
        except SyntaxError:
            continue
        rel = os.path.relpath(cale, RAD).replace(os.sep, "/")
        for n in ast.walk(arb):
            if isinstance(n, ast.Return) and isinstance(n.value, ast.Dict):
                chei = {k.value for k in n.value.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                if chei & {"eroare", "erori", "erori_campuri"}:
                    out.append({"fisier": rel, "linia": n.lineno})
    return out


_CITARE = None


def modul_citeaza_legea(cale):
    """Fisierul contine un `Temei(...)` sau un nume `TEMEI*`? Pe AST, nu pe text."""
    global _CITARE
    if _CITARE is None:
        _CITARE = {}
    if cale in _CITARE:
        return _CITARE[cale]
    try:
        arb = ast.parse(io.open(cale, encoding="utf-8").read())
    except SyntaxError:
        _CITARE[cale] = False
        return False
    gasit = False
    for n in ast.walk(arb):
        if isinstance(n, ast.Name) and (n.id == "Temei" or n.id.startswith("TEMEI")):
            gasit = True
            break
        if isinstance(n, ast.Attribute) and (n.attr == "Temei" or n.attr.startswith("TEMEI")):
            gasit = True
            break
    _CITARE[cale] = gasit
    return gasit


def datorie(inv=None):
    """{fisier: n} — refuzuri intr-un modul care CITEAZA legea, dar care nu poarta temeiul.

    Unitatea clichetului. Vezi docstringul de modul pentru de ce nu e `fara` brut.
    """
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and r["purtator"] == "fara" and r["citeaza"]:
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def umbra(inv=None):
    """{fisier: n} — module care REFUZA si nu citeaza legea nicaieri. Nu e datorie; e nemasurat."""
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and not r["citeaza"]:
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def pe_clasa(inv=None):
    inv = inventar() if inv is None else inv
    d = {c: {p: 0 for p in PURTATOR} for c in CLASE}
    for r in inv:
        d[r["clasa"]][r["purtator"]] += 1
    return d


def pe_fisier_fara_temei(inv=None):
    """{fisier: cate refuzuri din clasa `refuz` n-au niciun temei} — unitatea clichetului."""
    inv = inventar() if inv is None else inv
    d = {}
    for r in inv:
        if r["clasa"] == "refuz" and r["purtator"] == "fara":
            d[r["fisier"]] = d.get(r["fisier"], 0) + 1
    return d


def _main():
    import json
    import sys
    inv = inventar()
    if "--json" in sys.argv:
        print(json.dumps({"inventar": inv, "pe_fisier_fara_temei": pe_fisier_fara_temei(inv)},
                         ensure_ascii=False, indent=1, sort_keys=True))
        return 0
    d = pe_clasa(inv)
    print("REFUZURI: %d (`raise` care opresc un act)\n" % len(inv))
    print("%-10s %12s %8s %8s   %s" % ("clasa", "structurat", "proza", "fara", "ce opreste"))
    ce = {"acces": "cine esti (401/403) — temeiul legal n-ar avea ce cauta",
          "negasit": "404 — AMESTECAT: resursa inexistenta + nomenclator inchis",
          "refuz": "ce ai cerut (400/409/422 + exceptiile producatorilor)"}
    for c in CLASE:
        print("%-10s %12d %8d %8d   %s" % (c, d[c]["structurat"], d[c]["proza"], d[c]["fara"], ce[c]))
    fara = pe_fisier_fara_temei(inv)
    dat, umb = datorie(inv), umbra(inv)
    print("\nFARA TEMEI in clasa `refuz`: %d, in %d fisiere." % (sum(fara.values()), len(fara)))
    print("  din care DATORIE (modulul CITEAZA legea, refuzul nu poarta temeiul): %d, in %d fisiere"
          % (sum(dat.values()), len(dat)))
    print("  restul e in module care nu citeaza legea nicaieri — vezi UMBRA")
    for f, n in sorted(dat.items(), key=lambda x: -x[1])[:12]:
        print("   %-46s %d" % (f, n))
    print("\n[umbra] refuzuri in module care NU citeaza legea nicaieri: %d, in %d fisiere"
          % (sum(umb.values()), len(umb)))
    print("   ori sunt generice (si atunci e in regula), ori aplica o regula pe care n-o pot numi")
    ir = refuzuri_care_INTORC()
    print("\n[umbra] refuzuri care INTORC in loc sa ridice (modul de esec 4): %d" % len(ir))
    print("[anti-vacuu] fisiere citite: %d" % len(_fisiere()))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
