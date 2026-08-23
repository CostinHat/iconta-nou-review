# -*- coding: utf-8 -*-
"""core/scan_norma_implementare.py — INTERDICȚIA 60: elementul care implementează o normă îi poartă
articolul?

Planul: *„Azi doar valorile poartă temei; formulele, condițiile de eligibilitate, structurile de
declarație, nomenclatoarele, termenele și regulile de validare nu poartă nimic. Măsurătoarea nu e
«câte au temei», ci câte elemente care implementează o normă EXISTĂ, și câte dintre ele îl poartă."*

NUMITORUL E PARTEA GREA, și e o alegere — deci se declară, ca să poată fi contrazisă. Categoriile de
mai jos sunt cele pe care le numește planul, fiecare cu proxy mecanic:

  formulă            funcție care cere DIRECT o valoare din registru (`cota(...)`)
  structură          funcție `build_xml` / `calcul_dNNN` — forma declarației
  nomenclator        constantă de modul, NUME_MARE, dict/tuple/set/frozenset, în modul fiscal
  termen             funcție cu `scadenta` / `termen` în nume
  validare           funcție `valideaza*` / `erori_generare` / `blocante*`

CE POARTĂ, în trei trepte — și distincția asta e chiar rezultatul măsurătorii:
  STRUCTURAT   obiect `Temei(...)` în corp — verificabil mecanic, se poate întreba «ce depinde de el»
  PROZĂ        un marcaj `TEMEI:` sau o citare `art.NN` în docstring/comentariu — verificabil de OM
  NIMIC        nicio urmă

CALIBRAREA, pe cele trei legături pe care planul le numește cunoscute (dacă scanul nu le clasifică
așa, e rupt): deducerea personală → STRUCTURAT · podeaua part-time → PROZĂ · nomenclatorul codurilor
de indemnizație → PROZĂ.

CE NU POATE SPUNE: că articolul citat e cel POTRIVIT. Măsoară prezența legăturii, nu corectitudinea ei
— aia e interdicția 53, măsurată separat. Și nu vede o legătură scrisă în alt fișier decât cel care
implementează.
"""
import ast
import pathlib
import re

RAD = pathlib.Path(__file__).resolve().parents[1]

# Module care implementeaza norme fiscale. Lista e DECLARATA: un modul de infrastructura (db, auth,
# observare) nu implementeaza o norma, deci n-are ce purta.
_NEFISCALE = re.compile(r"^(db|auth|observare|main|conftest|scan_|test_|agenda|graf_|audit_|"
                        r"migrare_|gen_|verificator)")

_MARCAJ_PROZA = re.compile(r"TEMEI\s*:|\bart\.\s*\d|\bArticolul\s+\d|\bpct\.\s*\d|Nomenclator", re.I)


def _fiscal(p):
    return not _NEFISCALE.match(p.stem)


def _are_temei_structurat(nod):
    for n in ast.walk(nod):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if nume == "Temei":
                return True
    return False


def _proza_din(nod, src_linii):
    """Docstringul + comentariile de deasupra si din corp."""
    buc = [ast.get_docstring(nod) or ""] if isinstance(
        nod, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module, ast.ClassDef)) else []
    st = getattr(nod, "lineno", 1)
    sf = getattr(nod, "end_lineno", st)
    buc.append("\n".join(src_linii[max(0, st - 6):sf]))
    return "\n".join(buc)


def _cere_cota(nod):
    for n in ast.walk(nod):
        if isinstance(n, ast.Call):
            nume = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
            if nume in ("cota", "salariu_minim_luna"):
                return True
    return False


def _temei_prin_registru(arb):
    """{nume_functie} pentru functiile carora li se ataseaza un Temei printr-un REGISTRU DE VARIANTE.

    Tiparul proiectului: `_VARIANTE_X = [("2018-01-01", _calcul_2018, Temei(...)), ...]`. Temeiul nu e
    in corpul functiei, ci langa ea in registru — iar prima forma a scanului asta o clasa drept PROZA,
    ratand chiar cazul de calibrare pe care planul il numeste cunoscut (deducerea personala <-> art.77
    alin.(4)). `graf_temei` a avut de tratat special acelasi tipar; nu e o exceptie, e conventia."""
    out = set()
    for n in ast.walk(arb):
        if not isinstance(n, ast.Assign):
            continue
        are_temei = any(
            isinstance(x, ast.Call)
            and (getattr(x.func, "id", None) or getattr(x.func, "attr", None)) == "Temei"
            for x in ast.walk(n.value))
        if not are_temei:
            continue
        for x in ast.walk(n.value):
            if isinstance(x, ast.Name):
                out.add(x.id)
    return out


def inventar():
    """[(fisier, categorie, nume, treapta)] pentru fiecare element care implementeaza o norma."""
    out = []
    for p in sorted(RAD.glob("core/*.py")):
        if not _fiscal(p):
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            arb = ast.parse(src)
        except (OSError, SyntaxError):
            continue
        linii = src.split("\n")
        prin_registru = _temei_prin_registru(arb)

        def treapta(nod, nume=None):
            if _are_temei_structurat(nod) or (nume and nume in prin_registru):
                return "STRUCTURAT"
            if _MARCAJ_PROZA.search(_proza_din(nod, linii)):
                return "PROZA"
            return "NIMIC"

        for n in arb.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nume = n.name
                cat = None
                if nume.startswith("build_xml") or re.match(r"^calcul_d\d", nume):
                    cat = "structura"
                elif "scadenta" in nume or "termen" in nume:
                    cat = "termen"
                elif nume.startswith(("valideaza", "erori_generare", "blocante")):
                    cat = "validare"
                elif _cere_cota(n):
                    cat = "formula"
                if cat:
                    out.append((p.name, cat, nume, treapta(n, nume)))
            elif isinstance(n, ast.Assign):
                for tg in n.targets:
                    if (isinstance(tg, ast.Name) and tg.id.isupper() and len(tg.id) > 3
                            and isinstance(n.value, (ast.Dict, ast.Tuple, ast.List, ast.Set))):
                        out.append((p.name, "nomenclator", tg.id, treapta(n, tg.id)))
    return out


def rezumat():
    import collections
    inv = inventar()
    per_cat = collections.defaultdict(collections.Counter)
    for _f, cat, _n, tr in inv:
        per_cat[cat][tr] += 1
    return inv, per_cat


if __name__ == "__main__":
    inv, per = rezumat()
    print("INTERDICTIA 60 — elemente care implementeaza o norma, si ce poarta")
    print("%-14s %8s %8s %8s %8s" % ("categorie", "total", "STRUCT", "PROZA", "NIMIC"))
    t = s = pr = ni = 0
    for cat in sorted(per):
        c = per[cat]
        tot = sum(c.values())
        print("%-14s %8d %8d %8d %8d" % (cat, tot, c["STRUCTURAT"], c["PROZA"], c["NIMIC"]))
        t += tot
        s += c["STRUCTURAT"]
        pr += c["PROZA"]
        ni += c["NIMIC"]
    print("%-14s %8d %8d %8d %8d" % ("TOTAL", t, s, pr, ni))
    print()
    print("   poarta legatura (structurat sau proza): %d din %d = %.0f%%" % (s + pr, t, 100.0 * (s + pr) / max(t, 1)))
    print("   verificabil MECANIC (structurat)      : %d din %d = %.0f%%" % (s, t, 100.0 * s / max(t, 1)))
