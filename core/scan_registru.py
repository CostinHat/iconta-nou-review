# -*- coding: utf-8 -*-
"""core/scan_registru.py — INVENTARUL registrului unic de parametri fiscali: ce e în registru și ce stă încă în afara lui.

De ce există (comanda Costin 08.10.2026, „registrul unic de parametri fiscali”, pct.2, verbatim în DECIZII): „Inventarul se numără, nu
se estimează.” Registrul e `common.COTE` (pct.1: „Registrul existent COTE devine acest registru”); orice valoare fiscală din alt loc e
de mutat în el. Instrumentul ăsta e măsurătoarea pe care se sprijină migrarea și, după ea, gardul interdicției 1.

Ce numără, pe fișier, din `core/scan_constante.inventar()` (aceeași clasificare, nu una paralelă):
  · `registru` — intrările din `COTE` (chei, intrări istorice);
  · `ancorat` — literal fiscal înregistrat cu `ancoreaza(...)`: din R1 (10.10.2026) e intrare în `COTE` (cheia „<modul>.<NUME>”),
    dar literalul trăiește încă în modul, fără istoric (R4 îl mută);
  · `sursat_in_modul` — clasa A în afara registrului și în afara `ancoreaza` (literal cu `Temei` alături, în modul);
  · `proza` — clasa E: temeiul există doar ca text pentru om;
  · `nesursat` — clasa C: nicio citare.
Literalele din chiar declarația lui `COTE` (`common.py`) se recunosc după intervalul de linii al atribuirii, citit din AST — nu după text.

Limita declarată: vede ce vede `scan_constante` (literalele din `core/` în domeniul fiscal). Clasa C amestecă valori fiscale cu praguri
OPERAȚIONALE (timeout-uri, ferestre anti-abuz, paginări) — numite deja în baseline-ul `core/test_constante_nesursate.py`; separarea lor
e un pas al migrării (R7), nu o presupunere a instrumentului.
"""
import ast
import io
import os

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FELURI = ("ancorat", "sursat_in_modul", "proza", "nesursat")


def _interval_cote():
    """(prima, ultima) linie a atribuirii `COTE = {...}` din `core/common.py`."""
    src = io.open(os.path.join(RAD, "core", "common.py"), encoding="utf-8").read()
    for n in ast.parse(src).body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "COTE" for t in n.targets):
            return n.lineno, n.end_lineno
    raise LookupError("COTE nu mai e o atribuire de modul în core/common.py — registrul s-a mutat, instrumentul trebuie mutat cu el")  # invariant-intern-ok: unealtă de dezvoltare


_APELURI = {}


def _apeluri_ancoreaza(fisier):
    """Intervalele de linii ale apelurilor `ancoreaza(...)` / `c.ancoreaza(...)` dintr-un fișier din `core/` (din AST: un apel întins
    pe mai multe rânduri își are literalul pe alt rând decât numele)."""
    if fisier not in _APELURI:
        arb = ast.parse(io.open(os.path.join(RAD, "core", fisier), encoding="utf-8").read())
        nume = {"ancoreaza"} | {a.asname for n in ast.walk(arb) if isinstance(n, ast.ImportFrom)
                                for a in n.names if a.name == "ancoreaza" and a.asname}   # `ancoreaza as _anc` (d212)
        _APELURI[fisier] = [(n.lineno, n.end_lineno) for n in ast.walk(arb) if isinstance(n, ast.Call)
                            and getattr(n.func, "attr", getattr(n.func, "id", None)) in nume]
    return _APELURI[fisier]


def fel(x, interval):
    """Felul unui rând din `scan_constante.inventar()`: unul din FELURI, `registru`, sau None (nomenclator / precizie)."""
    if x["cls"] == "A":
        if x["f"] == "common.py" and interval[0] <= x["l"] <= interval[1]:
            return "registru"
        if any(a <= x["l"] <= b for a, b in _apeluri_ancoreaza(x["f"])):
            return "ancorat"
        return "sursat_in_modul"
    return {"E": "proza", "C": "nesursat"}.get(x["cls"])


def inventar():
    """{"registru": {chei, intrari}, "in_afara": {fel: {fisier: [ {l, v, txt} ]}}, "total": {fel: n}}."""
    from core import common as c
    from core import scan_constante as sc
    interval = _interval_cote()
    out = {f: {} for f in FELURI}
    for x in sc.inventar():
        k = fel(x, interval)
        if k in FELURI:
            out[k].setdefault(x["f"], []).append({"l": x["l"], "v": x["v"], "txt": (x.get("txt") or "")[:160]})
    cote = c.registru_complet()
    return {"registru": {"chei": len(cote), "intrari": sum(len(v) for v in cote.values()),
                         "ancorate": sum(1 for k in cote if "." in k)},
            "in_afara": out,
            "total": {f: sum(len(v) for v in out[f].values()) for f in FELURI}}


def _main():
    import json
    import sys
    r = inventar()
    if "--json" in sys.argv:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    print("registru: %(chei)d chei (din care %(ancorate)d ancorate), %(intrari)d intrări" % r["registru"])
    for f in FELURI:
        print("%-16s %4d în %d fișiere" % (f, r["total"][f], len(r["in_afara"][f])))


if __name__ == "__main__":
    _main()
