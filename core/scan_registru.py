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


def _fractie(v):
    """Valoarea ca fracție, ca un procent întreg al unei constante ancorate (16) să se întâlnească cu fracția registrului (0.16); `None`
    pentru ce nu e un număr (o mulțime de cote, un text)."""
    from decimal import Decimal, InvalidOperation
    try:
        d = Decimal(str(v))
    except (InvalidOperation, ValueError):
        return None
    return d / 100 if 1 < d <= 100 else d


def dubluri(cote=None):
    """[(constanta ancorată, cealaltă intrare)] — o constantă ancorată care repetă PREVEDEREA (articol, alineat; litera egală sau una
    dintre ele lipsă — o citare fără literă acoperă tot alineatul) ȘI VALOAREA altei intrări din registru: aceeași regulă scrisă de două
    ori, care poate diverge (R3, 11.10.2026: d101/d101g/cote_tva/bacsis/d212). Actul NU intră în comparație: registrul citează uneori
    articolul din Codul fiscal prin legea care l-a modificat („Legea 141/2025 art.291”), iar constanta „CF art.291” — aceeași prevedere.
    Cheile istorice între ele nu se compară: `tva_redusa_9`/`tva_redusa_5` = `tva_redusa` de la 01.08.2025 e decizia lui Costin
    (03.08.2026, DECIZII), nu o dublură uitată."""
    from core import common as c
    cote = c.registru_complet() if cote is None else cote
    intrari = [(k, v, t) for k, lst in cote.items() for _d, v, t in lst]
    out = set()
    for k, v, t in intrari:
        if "." not in k or getattr(t, "art", None) is None or _fractie(v) is None:
            continue
        for k2, v2, t2 in intrari:
            if k2 == k or (str(t.art), str(t.alin)) != (str(t2.art), str(t2.alin)):
                continue
            if (t.lit is None or t2.lit is None or t.lit == t2.lit) and _fractie(v) == _fractie(v2):
                out.add(tuple(sorted((k, k2))) if "." in k2 else (k, k2))
    return sorted(out)


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
    d = dubluri()
    print("dubluri          %4d%s" % (len(d), "".join("\n  %s = %s" % p for p in d)))


if __name__ == "__main__":
    _main()
