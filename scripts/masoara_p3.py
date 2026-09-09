# -*- coding: utf-8 -*-
"""scripts/masoara_p3.py — DIAGNOSTIC P3: ce anume din cererea de portofoliu crește cu N.

**CE ADAUGĂ FAȚĂ DE `masoara_rute_portofoliu`.** Acela numără interogări și conexiuni — destul ca
să spui *dacă* ceva crește. P3 întreabă *CE* crește, iar pentru asta cifra trebuie DESPICATĂ:

  * `db_sec`      — timpul petrecut ÎN bază: suma duratelor `execute` + `fetch*`. Măsurat în jurul
                    apelurilor reale, nu estimat.
  * `cpu_sec`     — restul: `total_sec - db_sec`. Adică Python — construirea răspunsului,
                    serializarea JSON, validarea, dependențele FastAPI.
  * `octeti`      — mărimea răspunsului. Proxy pentru costul de serializare și de rețea; crește cu
                    N chiar și când interogările nu cresc.
  * `interogari`, `conexiuni`, `dus_intors` — ca înainte.

*O rută poate avea număr constant de interogări și tot să crească liniar: dacă lista de răspuns are
N elemente, cineva tot trebuie s-o construiască și s-o serializeze. Fără despicare, cele două cauze
arată la fel.*

**CALIBRAREA SEPARĂRII, în ambele direcții** — și e chiar proba că despicarea înseamnă ceva:
  (a) o rută care doar AȘTEAPTĂ baza (`pg_sleep`) -> `db_sec` ≈ total, `cpu_sec` ≈ 0;
  (b) o rută care doar ARDE CPU, fără nicio interogare -> `cpu_sec` ≈ total, `db_sec` ≈ 0.
*Un instrument care ar pune tot timpul într-o singură coloană ar trece nedetectat pe orice rută
reală; numai o rută care e sigur de celălalt fel îl demască.*

**DOMENIUL, declarat, cu limita lui.** Firmele sintetice au scheme cu nume propriu, INEXISTENTE pe
disc (`tenants.schema_name` e unic, deci schemele reale nu se pot cicla). Pentru rutele care CITESC
DOAR MODELUL asta e fidel: ele nu deschid nicio schemă. Pentru rutele care deschid schema fiecărei
firme, măsurătoarea redă corect **FORMA creșterii** (câte conexiuni și interogări per firmă), dar
**subestimează munca** per firmă — o schemă reală ar avea de citit date. De aceea costul real per
firmă se măsoară separat, pe portofoliul REAL, cu `masoara_pe_real()`, iar raportul le pune cap la
cap. *Se scrie aici ca cifra de latență să nu fie citită ca predicție.*
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import masoara_rute_portofoliu as MR  # noqa: E402


class Ceas:
    def __init__(self):
        self.interogari = 0
        self.conexiuni = 0
        self.dus_intors = 0
        self.db_sec = 0.0
        self.total_sec = 0.0

    def dict(self):
        cpu = max(0.0, self.total_sec - self.db_sec)
        return {"interogari": self.interogari, "conexiuni": self.conexiuni,
                "dus_intors": self.dus_intors,
                "db_sec": round(self.db_sec, 4), "cpu_sec": round(cpu, 4),
                "total_sec": round(self.total_sec, 4),
                "db_procent": (round(100.0 * self.db_sec / self.total_sec, 1)
                               if self.total_sec > 0 else None)}


class _Cursor:
    """Înveliș care CRONOMETREAZĂ, nu doar numără. Timpul se ia în jurul apelului real."""

    def __init__(self, real, c):
        self._real, self._c = real, c

    def _cu_ceas(self, fn, *a, **k):
        t = time.perf_counter()
        try:
            return fn(*a, **k)
        finally:
            self._c.db_sec += time.perf_counter() - t

    def execute(self, *a, **k):
        self._c.interogari += 1
        self._c.dus_intors += 1
        return self._cu_ceas(self._real.execute, *a, **k)

    def executemany(self, *a, **k):
        self._c.interogari += 1
        self._c.dus_intors += 1
        return self._cu_ceas(self._real.executemany, *a, **k)

    def fetchone(self, *a, **k):
        self._c.dus_intors += 1
        return self._cu_ceas(self._real.fetchone, *a, **k)

    def fetchall(self, *a, **k):
        self._c.dus_intors += 1
        return self._cu_ceas(self._real.fetchall, *a, **k)

    def fetchmany(self, *a, **k):
        self._c.dus_intors += 1
        return self._cu_ceas(self._real.fetchmany, *a, **k)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *a):
        return self._real.__exit__(*a)

    def __iter__(self):
        return iter(self._real)


class _Conn:
    def __init__(self, real, c):
        self._real, self._c = real, c

    def cursor(self, *a, **k):
        return _Cursor(self._real.cursor(*a, **k), self._c)

    def __getattr__(self, n):
        return getattr(self._real, n)


@contextlib.contextmanager
def cronometreaza():
    from core import db as _db
    c = Ceas()
    original = _db.get_conn

    @contextlib.contextmanager
    def get_conn_cronometrat(schema=None):
        c.conexiuni += 1
        t = time.perf_counter()
        with original(schema) as real:
            c.db_sec += time.perf_counter() - t      # și deschiderea conexiunii e timp de bază
            yield _Conn(real, c)

    _db.get_conn = get_conn_cronometrat
    t0 = time.perf_counter()
    try:
        yield c
    finally:
        c.total_sec = time.perf_counter() - t0
        _db.get_conn = original


def masoara_ruta(client, token, ruta):
    with cronometreaza() as c:
        r = client.get(ruta, headers={"Authorization": "Bearer " + token})
    d = c.dict()
    d["status"] = r.status_code
    d["octeti"] = len(r.content)
    if r.status_code != 200:
        d["corp"] = r.text[:160]
    return d


# ============================================================================
#  CALIBRARE — separarea DB / CPU, în ambele direcții
# ============================================================================
def calibreaza(verbose=True):
    from core import db as _db
    import main as _main
    _db.init_pool()

    cale_db, cale_cpu = "/_p3_doar_baza", "/_p3_doar_cpu"
    if not any(getattr(r, "path", None) == cale_db for r in _main.app.routes):
        @_main.app.get(cale_db)
        def _doar_baza():
            with _db.get_conn() as c:
                with c.cursor() as cur:
                    cur.execute("SELECT pg_sleep(0.20)")
                    cur.fetchone()
            return {"ok": True}

        @_main.app.get(cale_cpu)
        def _doar_cpu():
            t = time.perf_counter()
            x = 0
            while time.perf_counter() - t < 0.20:
                x += 1
            return {"ok": True, "x": x}

    det = {}
    with MR.client_test() as cl:
        for eticheta, cale in (("doar_baza", cale_db), ("doar_cpu", cale_cpu)):
            with cronometreaza() as c:
                r = cl.get(cale)
            det[eticheta] = dict(c.dict(), status=r.status_code)

    b, u = det["doar_baza"], det["doar_cpu"]
    vede_db = b["db_procent"] is not None and b["db_procent"] >= 80
    vede_cpu = u["db_procent"] is not None and u["db_procent"] <= 20
    deosebeste = b["db_procent"] > u["db_procent"] + 50
    ok = vede_db and vede_cpu and deosebeste
    if verbose:
        print("CALIBRARE masoara_p3 — separarea DB / CPU, ambele direcții:")
        print("  (a) rută care doar AȘTEAPTĂ baza -> %s" % b)
        print("  (b) rută care doar ARDE CPU      -> %s" % u)
        print("  pune timpul de bază în `db_sec`   :", vede_db)
        print("  pune timpul de Python în `cpu_sec`:", vede_cpu)
        print("  le DEOSEBEȘTE                     :", deosebeste)
        print("  VERDICT:", "OK" if ok else "PICAT — nicio despicare de mai jos n-ar valora nimic")
    return ok, det


# ============================================================================
#  CURBA — pe rutele derivate din cod
# ============================================================================
def rute_de_masurat():
    """Rutele DE CABINET care ating portofoliul, derivate cu `scan_cale_cerere` — nu scrise aici.

    Se măsoară doar `GET`-urile: un `POST` de portofoliu ar schimba date, iar o măsurătoare care
    scrie nu se poate repeta identic."""
    import scan_cale_cerere as SC
    return [x["cale"] for x in SC.rute_care_cresc()
            if x["creste_cu_N"] and x["metoda"] == "GET" and "{" not in x["cale"]]


def curba(nn=(5, 50, 100, 250, 500, 1000), rute=None, procent_invalidat=10):
    from core import db as _db
    _db.init_pool()
    rute = rute or rute_de_masurat()
    out = {}
    for n in nn:
        with _db.get_conn() as conn:
            MR.curata(conn)
            conn.commit()
        with _db.get_conn() as conn:
            uid, _ids = MR.construieste(conn, n, procent_invalidat, rece=False)
            tok = MR._token(conn, uid)
        with MR.client_test() as cl:
            cl.get(rute[0], headers={"Authorization": "Bearer " + tok})     # încălzire
            out[n] = {r: masoara_ruta(cl, tok, r) for r in rute}
        print("   N=%-5d %s" % (n, {r: "%dq/%dc %.3fs (db %s%%)"
                                    % (v["interogari"], v["conexiuni"], v["total_sec"],
                                       v["db_procent"])
                                    for r, v in out[n].items()}), flush=True)
    with _db.get_conn() as conn:
        MR.curata(conn)
        conn.commit()
    return out


def masoara_pe_real(rute=None):
    """Aceleași rute, pe portofoliul REAL — unde schemele există și munca per firmă e adevărată.

    Curba sintetică redă FORMA creșterii; asta dă costul REAL per firmă. Raportul le pune cap la
    cap: forma × costul real = predicția, iar amândouă componentele sunt măsurate, nu presupuse."""
    import psycopg2.extras as _E
    from core import auth_api, db as _db
    _db.init_pool()
    rute = rute or rute_de_masurat()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("SELECT u.id, count(t.id) FROM public.users u "
                        "  JOIN public.tenants t ON t.accounting_firm_id = u.accounting_firm_id "
                        " WHERE u.rol = 'admin_firma' AND u.activ AND t.activ "
                        "   AND t.schema_name LIKE 'tenant_%' "
                        " GROUP BY u.id ORDER BY 2 DESC LIMIT 1")
            uid, cate = cur.fetchone()
        with c.cursor(cursor_factory=_E.RealDictCursor) as cur:
            cur.execute("SELECT id, rol, accounting_firm_id FROM public.users WHERE id = %s", (uid,))
            u = dict(cur.fetchone())
    tok = auth_api.emite_token(u)
    with MR.client_test() as cl:
        cl.get(rute[0], headers={"Authorization": "Bearer " + tok})
        rez = {r: masoara_ruta(cl, tok, r) for r in rute}
    return {"uid": uid, "firme": cate, "rute": rez}


def _tipar(rez, real):
    nn = sorted(rez)
    rute = sorted(rez[nn[0]])
    print("\n═══ CURBA SINTETICĂ — interogări / conexiuni ═══")
    print("%-30s %s" % ("ruta", "  ".join("N=%-4d" % n for n in nn)))
    for r in rute:
        print("%-30s %s" % (r, "  ".join("%4dq/%-3dc" % (rez[n][r]["interogari"],
                                                         rez[n][r]["conexiuni"]) for n in nn)))
    print("\n═══ CURBA SINTETICĂ — total_sec (db% din el) ═══")
    print("%-30s %s" % ("ruta", "  ".join("N=%-4d" % n for n in nn)))
    for r in rute:
        print("%-30s %s" % (r, "  ".join("%.3f(%s%%)" % (rez[n][r]["total_sec"],
                                                        rez[n][r]["db_procent"]) for n in nn)))
    print("\n═══ CURBA SINTETICĂ — octeți răspuns ═══")
    for r in rute:
        print("%-30s %s" % (r, "  ".join("%7d" % rez[n][r]["octeti"] for n in nn)))
    print("\n═══ PE PORTOFOLIUL REAL (%d firme, scheme adevărate) ═══" % real["firme"])
    print("%-30s %8s %6s %10s %10s %10s %9s" % ("ruta", "interog", "conex", "total_s",
                                                "db_s", "cpu_s", "octeti"))
    for r in rute:
        v = real["rute"].get(r, {})
        print("%-30s %8s %6s %10s %10s %10s %9s"
              % (r, v.get("interogari"), v.get("conexiuni"), v.get("total_sec"),
                 v.get("db_sec"), v.get("cpu_sec"), v.get("octeti")))


if __name__ == "__main__":
    ok, _ = calibreaza()
    if not ok:
        sys.exit(2)
    print()
    rute = rute_de_masurat()
    print("RUTE derivate din cod (GET, de cabinet, ating portofoliul): %d" % len(rute))
    for r in rute:
        print("   %s" % r)
    print()
    real = masoara_pe_real(rute)
    rez = curba(rute=rute)
    _tipar(rez, real)
    cale = os.path.join(RAD, "masuratori", "post_p2", "curba_p3.json")
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    with open(cale, "w", encoding="utf-8", newline="") as f:
        json.dump({"sintetic": rez, "real": real, "rute": rute}, f,
                  ensure_ascii=False, indent=2, default=str)
    print("\nscris: %s" % cale)
