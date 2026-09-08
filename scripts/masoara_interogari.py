# -*- coding: utf-8 -*-
"""scripts/masoara_interogari.py — CÂTE interogări, conexiuni și dus-întorsuri face o cerere.

**DE CE EXISTĂ.** P2 cere ca numărul de interogări pentru o cerere de portofoliu să NU crească
proporțional cu numărul de firme. Asta nu se poate afirma citind codul — o buclă poate ascunde un
apel care deschide o conexiune trei niveluri mai jos. Se măsoară.

**CE NUMĂRĂ, și de ce toate trei:**
  * `interogari`   — apelurile `cursor.execute()`. Costul pe server.
  * `conexiuni`    — de câte ori s-a cerut o conexiune din pool. **Cifra care doare la 1000 de
                     firme**: pool-ul are 10; a 11-a cerere așteaptă. O rută care ia 2 conexiuni per
                     firmă serializează portofoliul, chiar dacă fiecare interogare e ieftină.
  * `dus_intors`   — `execute` + `fetch*`. Latența de rețea o plătește fiecare, separat de costul
                     interogării în sine.

**CUM.** Se împachetează `db.get_conn` și cursoarele lui, la rulare, în jurul blocului măsurat. NU se
citește codul și nu se ghicește: dacă un apel deschide o conexiune, se vede, indiferent cât de adânc
e. *Un contor care numără ce crede că se cheamă e o părere.*

**CALIBRAT ÎN AMBELE DIRECȚII, obligatoriu înainte de folosire** (`calibreaza()`): i se dă un caz în
care TREBUIE să raporteze problemă (buclă N+1) și unul în care TREBUIE să raporteze corect (o
singură interogare agregată). *O calibrare care verifică doar o direcție nu spune nimic despre
cealaltă* — lecția din defectul P0, plătită acum două ore.
"""
from __future__ import annotations

import contextlib
import os
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)


class Numarator:
    def __init__(self):
        self.interogari = 0
        self.conexiuni = 0
        self.dus_intors = 0
        self.secunde = 0.0

    def __repr__(self):
        return ("Numarator(interogari=%d, conexiuni=%d, dus_intors=%d, secunde=%.3f)"
                % (self.interogari, self.conexiuni, self.dus_intors, self.secunde))

    def dict(self):
        return {"interogari": self.interogari, "conexiuni": self.conexiuni,
                "dus_intors": self.dus_intors, "secunde": round(self.secunde, 3)}


class _Cursor:
    """Înveliș peste cursorul real. Numără, apoi deleagă. Nu schimbă nimic din purtare."""

    def __init__(self, real, n):
        self._real = real
        self._n = n

    def execute(self, *a, **k):
        self._n.interogari += 1
        self._n.dus_intors += 1
        return self._real.execute(*a, **k)

    def executemany(self, *a, **k):
        self._n.interogari += 1
        self._n.dus_intors += 1
        return self._real.executemany(*a, **k)

    def fetchone(self, *a, **k):
        self._n.dus_intors += 1
        return self._real.fetchone(*a, **k)

    def fetchall(self, *a, **k):
        self._n.dus_intors += 1
        return self._real.fetchall(*a, **k)

    def fetchmany(self, *a, **k):
        self._n.dus_intors += 1
        return self._real.fetchmany(*a, **k)

    def __getattr__(self, nume):
        return getattr(self._real, nume)

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *a):
        return self._real.__exit__(*a)

    def __iter__(self):
        return iter(self._real)


class _Conn:
    def __init__(self, real, n):
        self._real = real
        self._n = n

    def cursor(self, *a, **k):
        return _Cursor(self._real.cursor(*a, **k), self._n)

    def __getattr__(self, nume):
        return getattr(self._real, nume)


@contextlib.contextmanager
def numara():
    """Măsoară blocul. `with numara() as n: ...` apoi `n.dict()`."""
    from core import db as _db
    n = Numarator()
    original = _db.get_conn

    @contextlib.contextmanager
    def get_conn_numarat(schema=None):
        n.conexiuni += 1
        with original(schema) as c:
            yield _Conn(c, n)

    _db.get_conn = get_conn_numarat
    t0 = time.time()
    try:
        yield n
    finally:
        n.secunde = time.time() - t0
        _db.get_conn = original


# ============================================================================
#  CALIBRARE — în AMBELE direcții, înainte de orice cifră
# ============================================================================
def calibreaza(verbose=True):
    """`(ok, detalii)`. Instrumentul trebuie să vadă ȘI problema, ȘI corectitudinea.

    Fără ramura „corect", un contor care ar raporta mereu „N+1" ar părea că funcționează perfect pe
    orice cod prost — și n-ar spune nimic despre codul bun. Fără ramura „problemă", ar putea număra
    zero la infinit."""
    from core import db as _db
    _db.init_pool()
    N = 12
    det = {}

    # (a) TIPARUL RĂU: o conexiune și o interogare per element
    with numara() as rau:
        for i in range(N):
            with _db.get_conn() as c:
                with c.cursor() as cur:
                    cur.execute("SELECT %s", (i,))
                    cur.fetchone()
    det["n_plus_1"] = rau.dict()

    # (b) TIPARUL BUN: o conexiune, o interogare agregată
    with numara() as bun:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute("SELECT x FROM unnest(%s::int[]) AS t(x)", (list(range(N)),))
                cur.fetchall()
    det["set_based"] = bun.dict()

    vede_problema = (rau.conexiuni >= N and rau.interogari >= N)
    vede_corect = (bun.conexiuni == 1 and bun.interogari == 1)
    creste_cu_N = rau.interogari > bun.interogari * 3

    ok = vede_problema and vede_corect and creste_cu_N
    if verbose:
        print("CALIBRARE instrument de măsurare (ambele direcții):")
        print("  (a) N+1 (%d elemente)   -> %s" % (N, rau))
        print("  (b) set-based           -> %s" % bun)
        print("  vede PROBLEMA (N conexiuni, N interogări) :", vede_problema)
        print("  vede CORECTITUDINEA (1 și 1)              :", vede_corect)
        print("  deosebește cele două                      :", creste_cu_N)
        print("  VERDICT:", "OK" if ok else "PICAT — nicio cifră de mai jos n-ar valora nimic")
    return ok, det


if __name__ == "__main__":
    ok, _ = calibreaza()
    sys.exit(0 if ok else 2)
