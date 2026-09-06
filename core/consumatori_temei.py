# -*- coding: utf-8 -*-
"""core/consumatori_temei.py — CINE CONSUMĂ un temei care NU trăiește în registrul de cote.

**Întrebarea, și de ce n-avea răspuns.** Pragul de reverificare al unei valori se compune din două
axe: cât de des se schimbă articolul (frecvența) și **unde ajunge valoarea** (consecința). A doua se
calcula, până azi, numai prin `core/dependenti_act.py`, care merge pe lanțul
`articol → cheie din COTE → funcții care cheamă cota()`. Un temei care **nu e în `COTE`** n-are cheie,
deci lanțul se rupe la primul pas și consecința iese `NECUNOSCUT` **prin construcție**.

Măsurat pe 06.09.2026: din 42 de temeiuri fără prag, **19** erau exact ăsta — `categorie_marime`,
`cota_tva_incasare`, `perioada_fiscala_tva`, `registre_art321`, `registru_inventar`,
`registru_evidenta_fiscala`, `jurnal_api`. *Toate scrise DUPĂ decizia 73, care cere ca temeiul să
stea în modulul REGULII.* Aceeași formă de orbire ca la R169, în alt instrument: **cu cât repo-ul
urmează mai bine regula, cu atât graful vede mai puțin.**

**CE FACE.** Pentru un temei numit prin calea lui din inventar (`registru_inventar.TEMEI_CONTINUT`,
`perioada_fiscala_tva.NORME.lunar[1]`), răspunde la: *ce funcții îl citesc, ce funcții ajung la ele,
și ajunge într-un modul de declarație?*

  1. **cititorii direcți** — funcțiile care numesc atributul, oriunde în `core/*.py` **și** în
     `main.py`. Un `TEMEI["profit"]` se numără la `TEMEI`; un `pft.NORME` la `NORME`.
  2. **închiderea tranzitivă** — cine cheamă un cititor, cine cheamă pe acela, prin graful de apeluri
     din `core/graf_temei.py` (același pe care se sprijină `depinde_de`, deci aceeași rezolvare de
     apeluri reparată la R17).
  3. **verdictul** — `DEPUS` dacă lanțul atinge un modul `d<nnn>*.py`, `CALCULAT` dacă atinge cod dar
     nicio declarație, `NECUNOSCUT` dacă nu-l atinge nimic.

**NU GHICEȘTE PRAGUL.** Modulul ăsta răspunde numai la „cine consumă". Pragul se ia din tabelul lui
Costin (`reverificare.PRAGURI`), pe perechea (frecvență, consecință) — iar când consumatorul nu se
știe, consecința rămâne **NECUNOSCUT declarat**, și valoarea rămâne fără prag. *Nu se ghicește pragul
înainte de a ști consumatorul* (Costin, 06.09.2026).

**CE NU POATE, declarat:**
  - **închiderea tranzitivă e pe `core/*.py`.** `main.py` intră doar ca cititor DIRECT: graful de
    apeluri nu-l conține, deci un lanț `main.py → core` se vede, unul `main.py → main.py` nu. Pentru
    verdict contează puțin — toate modulele de declarație sunt în `core/` —, dar un `CALCULAT` care
    trece numai prin `main.py` poate rămâne nevăzut.
  - **atributul se potrivește pe NUME, nu pe obiect.** Două module cu un atribut `TEMEI` sunt
    deosebite prin modul, dar o funcție care primește temeiul ca *parametru* și îl folosește sub alt
    nume nu se vede. Supra-aproximarea e în direcția zgomotoasă doar la nivel de modul; dincolo, e
    o sub-aproximare declarată.
  - **nu spune că valoarea e FOLOSITĂ corect** — doar că e citită. Ca peste tot: e o potrivire, nu
    o citire.
"""
import ast
import io
import os
import pathlib
import re

from core import graf_temei as gt

_RAD = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#: Modulele care produc o declarație. Aceeași formă ca în `reverificare`, ținută aici lângă
#: verdictul pe care îl decide.
_RE_MODUL_DECLARATIE = re.compile(r"^d\d{3}[a-z0-9_]*\.py::")

#: Fișierele scanate pentru CITITORI DIRECȚI. `main.py` intră, deși graful de apeluri nu-l conține.
_CACHE_CITITORI = {}


def _fisiere(radacina=None):
    rad = pathlib.Path(radacina) if radacina else _RAD
    return sorted(rad.glob("core/*.py")) + [rad / "main.py"]


def _nume_citite(node):
    """Numele la nivel de modul pe care le citește funcția: `X`, `X[...]`, `m.X`, `X.y`."""
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            out.add(n.attr)
    return out


def harta_cititori(radacina=None):
    """{(fisier, atribut): {chei de funcție}} — cine citește ce nume, în core/*.py + main.py."""
    rad = str(radacina or _RAD)
    if rad in _CACHE_CITITORI:
        return _CACHE_CITITORI[rad]
    h = {}
    for f in _fisiere(radacina):
        if not f.exists() or f.name.startswith("test_"):
            continue
        try:
            arb = ast.parse(io.open(f, encoding="utf-8").read())
        except SyntaxError:
            continue
        for node in ast.walk(arb):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            k = gt.cheie(f.name, node.name)
            for nume in _nume_citite(node):
                h.setdefault((f.name, nume), set()).add(k)
    _CACHE_CITITORI[rad] = h
    return h


def _modul_si_atribut(cale):
    """`registru_inventar.TEMEI_CONTINUT` / `perioada_fiscala_tva.NORME.lunar[1]` -> (fișier, atribut).

    `None` dacă forma nu e „modul.atribut…" — de exemplu căile din registrul de cote (`COTE.cas[0][2]`),
    care au deja lanțul lor prin `dependenti_act` și n-au ce căuta aici.
    """
    parti = str(cale or "").split(".")
    if len(parti) < 2:
        return None
    modul, atribut = parti[0], parti[1].split("[")[0]
    if not modul or not atribut or modul == "COTE":
        return None
    return modul + ".py", atribut


def _contine(valoare, tinta, adancime=0):
    """`tinta` e chiar `valoare`, sau stă înăuntrul ei (dict/listă/tuplu)? Prin IDENTITATE."""
    if valoare is tinta:
        return True
    if adancime > 4:
        return False
    if isinstance(valoare, dict):
        return any(_contine(v, tinta, adancime + 1) for v in valoare.values())
    if isinstance(valoare, (list, tuple, set, frozenset)):
        return any(_contine(v, tinta, adancime + 1) for v in valoare)
    return False


def nume_legate(modul, temei):
    """Toate numele de MODUL legate de același obiect `Temei`.

    De ce nu doar numele din cale: `scan_citate` raportează prima cale pe care l-a găsit, iar `dir()`
    e alfabetic — deci un temei ținut și în `TEMEI` (dicționar) și în `TEMEI_PROFIT` (constantă) e
    raportat pe primul, în timp ce codul îl citește pe al doilea. *O sub-aproximare arată exact ca o
    absență*, iar aici absența ar fi devenit `NECUNOSCUT` pe o valoare cu patru cititori.
    """
    import importlib
    try:
        m = importlib.import_module("core." + modul[:-3])
    except Exception:  # noqa: BLE001
        return set()
    return {a for a in dir(m)
            if not a.startswith("_") and _contine(getattr(m, a, None), temei)}


def consumatori(cale, temei=None, radacina=None):
    """{modul, atribut, directi, toti, declaratii, verdict} pentru un temei numit prin calea lui.

    `verdict` e `DEPUS` / `CALCULAT` / `NECUNOSCUT`, cu aceleași înțelesuri ca în `reverificare`.
    """
    gol = {"modul": None, "atribut": None, "nume": [], "directi": [], "toti": [],
           "declaratii": [], "verdict": "NECUNOSCUT"}
    ma = _modul_si_atribut(cale)
    if ma is None:
        return gol
    fisier, atribut = ma
    h = harta_cititori(radacina)
    nume = {atribut} | (nume_legate(fisier, temei) if temei is not None else set())
    directi = set()
    for n in nume:
        directi |= h.get((fisier, n), set())
    if not directi:
        return dict(gol, modul=fisier, atribut=atribut)

    # închiderea tranzitivă, cu același tipar ca `graf_temei.depinde_de`
    graf = gt.construieste_graf(radacina)
    rez = {n: "direct" for n in directi if n in graf}
    for n in directi:                       # cititorii din main.py nu sunt în graf, dar contează
        rez.setdefault(n, "direct")
    schimbat = True
    while schimbat:
        schimbat = False
        for n, d in graf.items():
            if n in rez:
                continue
            for apelat in d["apeleaza"]:
                if apelat in rez:
                    rez[n] = "prin %s" % apelat
                    schimbat = True
                    break
    decl = sorted(n for n in rez if _RE_MODUL_DECLARATIE.match(n))
    return {"modul": fisier, "atribut": atribut, "nume": sorted(nume),
            "directi": sorted(directi), "toti": sorted(rez), "declaratii": decl,
            "verdict": "DEPUS" if decl else "CALCULAT"}


def _main():
    import sys
    from core import scan_citate
    inv = [(c, t) for c, t, _v in scan_citate.inventar()]
    if len(sys.argv) > 1:
        inv = [(c, t) for c, t in inv if c.startswith(sys.argv[1])]
    for cale, temei in inv:
        r = consumatori(cale, temei)
        if r["modul"] is None:
            continue
        print("%-46s %-11s directi=%-3d toti=%-4d declaratii=%s"
              % (cale[:46], r["verdict"], len(r["directi"]), len(r["toti"]),
                 ", ".join(x.split("::")[0] for x in r["declaratii"][:4]) or "—"))


if __name__ == "__main__":
    _main()
