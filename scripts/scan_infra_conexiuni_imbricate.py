# -*- coding: utf-8 -*-
"""scripts/scan_infra_conexiuni_imbricate.py — CINE ȚINE DOUĂ CONEXIUNI DEODATĂ, derivat din cod (C201, lotul 13).

**DE CE EXISTĂ.** Pe 25.10.2026 o cerere a Control fiscal ținea două conexiuni (`with db.get_conn(schema) as cs, db.get_conn() as
cp`). Una a rămas „idle in transaction” cu blocări pe tabelele firmei; `DROP SCHEMA` al curățeniei e2e a așteptat-o, iar a doua
conexiune a aceleiași cereri a așteptat după `DROP` — 38 de minute. PostgreSQL nu vede ciclul: una din muchii e firul aplicației,
care așteaptă între două conexiuni proprii. Pe O SINGURĂ conexiune, același conflict e un `deadlock` pe care PostgreSQL îl vede și
îl oprește într-o secundă. Deci întrebarea se pune peste tot codul, nu numai în Control fiscal: **unde ține o funcție o conexiune
și, cât o ține, mai deschide una?**

**MODELUL** e cel din `scripts/scan_tranzactii.py` (refolosit, nu rescris): `graf()` dă, pentru fiecare definiție, arborele de
domenii (`with … get_conn(…)`) și apelurile; `rezolva()` leagă un apel de definiția lui în trei trepte. Peste el:

  1. funcțiile care DESCHID: au un domeniu (sau o deschidere fără `with`) în corp, ori cheamă — rezolvat fără omonimie — una care
     deschide (punct fix);
  2. în fiecare domeniu al fiecărei funcții: un domeniu imbricat direct, ori un apel rezolvat la o funcție care deschide = o a doua
     conexiune ținută deodată cu prima;
  3. separat, pe `ast`: un `with` cu DOUĂ deschideri în același enunț (`with get_conn(a) as x, get_conn(b) as y`) — `graf()` îl vede
     ca un singur domeniu.

Cheia unei găsiri e stabilă la mutarea liniilor: `fișier::funcția_care_ține -> fișier::funcția_care_deschide` (sau
`-> (with cu două conexiuni)`).

**CE NU VEDE, declarat.** Apelurile indirecte (funcție dată ca argument, `getattr`, dicționar de funcții) și omonimiile nerezolvabile
(același nume definit în mai multe module, fără alias de import) — numărate separat (`nerezolvate`). Pentru drumurile reparate,
garda dinamică `db.o_singura_conexiune()` le acoperă la rulare (`core/test_lot13_infra_o_conexiune.py`).
"""
import ast
import io
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (RAD, os.path.join(RAD, "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import scan_tranzactii as T  # noqa: E402

WITH_DUBLU = "(with cu două conexiuni)"
DESCHIDERE_DIRECTA = "(conexiune deschisă fără with)"


def _noduri(arbore):
    """Toate nodurile unui arbore de domenii, în adâncime (inclusiv cele din domeniile imbricate)."""
    for n in arbore:
        yield n
        if n[0] == "domeniu":
            yield from _noduri(n[1])


def _domenii(arbore):
    for n in _noduri(arbore):
        if n[0] == "domeniu":
            yield n


def _deschide_direct(arbore):
    return any(n[0] == "domeniu" or (n[0] == "ev" and n[2] == "deschide_fara_with") for n in _noduri(arbore))


def _rezolvat(n, gazda, arbori, definitii):
    """Cheile unui apel, numai când rezolvarea e fără omonimie; altfel None."""
    _f, nume, _fis, _lin, _ram, modul = n
    chei, omonim = T.rezolva(nume, gazda[0], modul, arbori, definitii)
    return None if omonim else chei


def functii_care_deschid(arbori, definitii):
    deschid = {k for k, a in arbori.items() if _deschide_direct(a)}
    apeluri = {k: [n for n in _noduri(a) if n[0] == "apel"] for k, a in arbori.items()}
    schimbat = True
    while schimbat:
        schimbat = False
        for k, lst in apeluri.items():
            if k in deschid:
                continue
            for n in lst:
                chei = _rezolvat(n, k, arbori, definitii) or []
                if any(c in deschid and c != k for c in chei):
                    deschid.add(k)
                    schimbat = True
                    break
    return deschid


def _with_duble(fisiere, rad):
    """{cheie} pentru fiecare `with` cu două deschideri în același enunț."""
    out = set()
    for cale in fisiere:
        rel = os.path.relpath(cale, rad).replace(os.sep, "/")
        try:
            radacina = ast.parse(io.open(cale, encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue

        def viz(nod, fn):
            if isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef)):
                fn = nod.name
            if isinstance(nod, (ast.With, ast.AsyncWith)):
                if sum(1 for it in nod.items if T._e_deschidere(it.context_expr)) >= 2:
                    out.add("%s::%s -> %s" % (rel, fn, WITH_DUBLU))
            for c in ast.iter_child_nodes(nod):
                viz(c, fn)
        viz(radacina, "<modul>")
    return out


def inventar(fisiere=None, rad=None):
    """`(gasite, nedecise)`: mulțimea cheilor „ține o conexiune și mai deschide una” și lista apelurilor din domenii care nu s-au putut
    rezolva fără omonimie ȘI au printre definițiile posibile una care deschide — singurele pe care scanarea nu le poate decide."""
    rad = rad or T.RAD
    fisiere = fisiere or T._fisiere()
    arbori, _rute, definitii, _mm = T.graf(fisiere, rad)
    deschid = functii_care_deschid(arbori, definitii)
    gasite, nedecise = set(), []
    for k, arb in arbori.items():
        for dom in _domenii(arb):
            for n in _noduri(dom[1]):
                if n[0] == "domeniu":
                    gasite.add("%s::%s -> %s::%s" % (k[0], k[1], k[0], k[1]))
                elif n[0] == "ev" and n[2] == "deschide_fara_with":
                    gasite.add("%s::%s -> %s" % (k[0], k[1], DESCHIDERE_DIRECTA))
                elif n[0] == "apel":
                    chei = _rezolvat(n, k, arbori, definitii)
                    if chei is None:
                        posibile, _om = T.rezolva(n[1], k[0], n[5], arbori, definitii)
                        if any(c in deschid and c != k for c in posibile):
                            nedecise.append("%s::%s -> %s (omonim, linia %d)" % (k[0], k[1], n[1], n[3]))
                        continue
                    for c in chei:
                        if c in deschid and c != k:
                            gasite.add("%s::%s -> %s::%s" % (k[0], k[1], c[0], c[1]))
    return gasite | _with_duble(fisiere, rad), nedecise


if __name__ == "__main__":
    g, nd = inventar(rad=sys.argv[1] if len(sys.argv) > 1 else None,
                     fisiere=None if len(sys.argv) < 2 else [os.path.join(sys.argv[1], "main.py")] + sorted(
                         os.path.join(sys.argv[1], "core", n) for n in os.listdir(os.path.join(sys.argv[1], "core"))
                         if n.endswith(".py") and not n.startswith(("test_", "scan_"))))
    for x in sorted(g):
        print(x)
    for x in nd:
        print("NEDECIS:", x)
    print("total: %d locuri unde o funcție ține o conexiune și mai deschide una; nedecise (omonime cu o definiție care deschide): %d"
          % (len(g), len(nd)))
