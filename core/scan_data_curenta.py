# -*- coding: utf-8 -*-
"""INTERDICȚIA 3 — «Un calcul fiscal care citește data curentă», măsurată.

**De ce e o cifră validă și falsă.** O funcție fiscală care cade pe `date.today()` când apelantul nu-i
dă data răspunde despre **azi**, nu despre perioada calculată. Numărul iese perfect valid — trece
orice schemă, intră în orice declarație — și e fals pentru perioada lui. Registrul de cote e cheiat
pe dată tocmai ca asta să nu se întâmple; implicitul îl **desface la locul apelului**.

DOUĂ POPULAȚII, nu una:

  A. **funcțiile care CAD pe data curentă** — `la_data or date.today()`. Fiecare e un generator
     latent: orice apelant viitor care uită data primește tăcut „azi".
  B. **apelurile care OMIT data** — clasa care produce cifra falsă *azi*.

CUM AM GREȘIT MĂSURÂND, de trei ori în aceeași alegere, toate în aceeași direcție — **numărând
FORMA, nu EFECTUL** (fix limita declarată la interdicția 14):

  1. am căutat numai `cota(...)` ca **nume**, deci n-am văzut `_common.cota(...)` ca **atribut** → „1 apel";
  2. am socotit „omis" orice apel fără **cuvânt-cheie**, deci am numărat drept omisiuni cele **310**
     care dau data **pozițional** → „68 de apeluri de producție";
  3. tiparul de nume de parametru a prins `data_transport` la o funcție de **email**, care nu e
     un calcul fiscal → un fals pozitiv rămas până la citirea la sursă.

Adevărul, măsurat cu semnătura reală: **310 dau data · 4 n-o dau**, din care **2 sunt fiscale**.
Fiecare dintre cele trei greșeli are calibrare proprie în `core/test_data_curenta.py`.

CE NU VEDE, declarat:
  - **numai `core/`**. `main.py` nu e parcurs; un apel de acolo care omite data nu se vede aici.
  - **nu urmărește valoarea**: dacă apelantul dă `la_data=None` explicit, apelul apare ca „dă data",
    deși efectul e identic cu omiterea. Direcția e cea permisivă, și se scrie.
  - **nu spune dacă „azi" e greșit** pentru un apel anume. Spune că nimeni n-a ales data. Alegerea
    dintre „defect" și „azi e corect aici" e a omului, iar răspunsul lui stă în `EXCEPTII`.
"""
import ast
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(RAD, "core")

#: Un parametru care poartă o dată. Îngust intenționat: `data_emitere`, `la_data`, `data`.
NUME_DE_DATA = re.compile(r"^(la_data|data|data_.+)$")

#: Corpul cade pe data curentă: `la_data or date.today()` / `x = datetime.now()`.
_CADE_PE_AZI = (re.compile(r"(la_data|data)\s+or\s+[\w.]*(today|now)\(\)"),
                re.compile(r"=\s*[\w.]*(today|now)\(\)\s*$", re.M))

#: Apeluri care omit data DELIBERAT, fiecare cu motivul. Un apel care nu e aici și omite data e o
#: omisiune. *Excepția se numește; un clichet fără nume e o excepție știută de un singur raport.*
EXCEPTII = {
    ("alerta_acces.py", "trimite"):
        "NU e un calcul fiscal: trimite un email de alertă de acces. `data_transport` e parametrul "
        "unei rute de e-Transport refolosite, nu o dată de calcul. Fals pozitiv al primei sonde, "
        "prins la citirea sursei — se declară ca să nu fie „prins” a doua oară.",
    ("salariati_api.py", "cota"):
        "Validează plafonul unui tichet de masă TASTAT ACUM, într-un formular. „Azi” e data corectă "
        "pentru ce se introduce azi. *Rămâne declarat, nu tăcut: dacă ecranul va edita vreodată "
        "perioade trecute, excepția devine defect și trebuie scoasă de aici.*",
}


def _sursa(f):
    return io.open(os.path.join(DIR, f), encoding="utf-8").read()


def _fisiere():
    return [f for f in sorted(os.listdir(DIR)) if f.endswith(".py")]


def cade_pe_azi():
    """{nume_functie: (fisier, {param: index_pozitional}, [parametri_de_data])} — populația A."""
    out = {}
    for f in _fisiere():
        if f.startswith("test_"):
            continue
        src = _sursa(f)
        try:
            arb = ast.parse(src)
        except SyntaxError:
            continue
        linii = src.split("\n")
        for n in ast.walk(arb):
            if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            corp = "\n".join(linii[n.lineno - 1:(n.end_lineno or n.lineno)])
            if not any(t.search(corp) for t in _CADE_PE_AZI):
                continue
            poz = [a.arg for a in n.args.posonlyargs] + [a.arg for a in n.args.args]
            de_data = [p for p in poz + [a.arg for a in n.args.kwonlyargs]
                       if NUME_DE_DATA.match(p)]
            if de_data:
                out[n.name] = (f, {p: i for i, p in enumerate(poz)}, de_data)
    return out


def _da_data(apel, indici, de_data):
    """Apelul furnizează data — pe NUME sau POZIȚIONAL. A doua jumătate lipsea din prima sondă și a
    umflat clasa de la 4 la 68."""
    kw = {k.arg for k in apel.keywords if k.arg}
    if any(p in kw for p in de_data):
        return True
    return any(p in indici and indici[p] < len(apel.args) for p in de_data)


def apeluri(fn=None):
    """[(fisier, linie, functie, da_data, e_test)] — populația B, pe toate apelurile."""
    fn = cade_pe_azi() if fn is None else fn
    out = []
    for f in _fisiere():
        try:
            arb = ast.parse(_sursa(f))
        except SyntaxError:
            continue
        for n in ast.walk(arb):
            if not isinstance(n, ast.Call):
                continue
            # NUME sau ATRIBUT: `cota(...)` și `_common.cota(...)` sunt același apel.
            nume = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, "attr", None)
            if nume not in fn:
                continue
            _fdef, indici, de_data = fn[nume]
            out.append((f, n.lineno, nume, _da_data(n, indici, de_data), f.startswith("test_")))
    return out


def omisiuni():
    """Apelurile de PRODUCȚIE care omit data, FĂRĂ cele declarate în `EXCEPTII`."""
    fn = cade_pe_azi()
    return [(f, l, nume) for f, l, nume, da, e_test in apeluri(fn)
            if not da and not e_test and (f, nume) not in EXCEPTII]


def scutite():
    """Apelurile care omit data și SUNT declarate — ca să se vadă că excepțiile încă au obiect."""
    fn = cade_pe_azi()
    return [(f, l, nume) for f, l, nume, da, e_test in apeluri(fn)
            if not da and not e_test and (f, nume) in EXCEPTII]


def cifre():
    fn = cade_pe_azi()
    ap = apeluri(fn)
    return {"functii_care_cad_pe_azi": len(fn),
            "apeluri_care_dau_data": sum(1 for *_r, da, t in ap if da and not t),
            "apeluri_de_test": sum(1 for *_r, _da, t in ap if t),
            "omisiuni": len(omisiuni()),
            "scutite_declarat": len(scutite())}


if __name__ == "__main__":
    c = cifre()
    print("INTERDICȚIA 3 — un calcul fiscal care citește data curentă")
    for k, v in c.items():
        print("  %-26s %d" % (k, v))
    print("\nA. funcții care cad pe data curentă:")
    for nume, (f, _i, de_data) in sorted(cade_pe_azi().items()):
        print("   %-30s %-26s %s" % (nume[:30], f[:26], de_data))
    print("\nB. apeluri de PRODUCȚIE care omit data (defecte):")
    for f, l, nume in omisiuni():
        print("   %s:%d  → %s()" % (f, l, nume))
    print("\nB'. omisiuni DECLARATE, cu motivul:")
    for f, l, nume in scutite():
        print("   %s:%d  → %s()\n      %s" % (f, l, nume, EXCEPTII[(f, nume)]))
