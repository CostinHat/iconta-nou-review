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


# ============================================================================
#  CALEA DE SUCCES — pe scheme REALE, nu inexistente
# ============================================================================
#: **DE CE EXISTĂ, și ce corectează.** Curba sintetică folosește firme cu scheme INEXISTENTE.
#: Prima formă a diagnosticului a spus că asta redă „forma creșterii" și subestimează doar munca.
#: **Afirmația era prea largă:** pe o schemă inexistentă, `rezumat()` iese devreme
#: (`SELECT to_regclass(...)` întoarce `NULL`), deci **coeficientul de interogări per firmă e el
#: însuși mai mic** — nu doar timpul. Numărul de conexiuni rămâne același, dar cel de interogări nu.
#:
#: Aici se construiesc firme cu schemă ADEVĂRATĂ din `tenant_template.sql`, la N = 5/10/14, și se
#: separă mecanic **overhead-ul fix** de **costul marginal per firmă**. Nimic nu se mai deduce din
#: forma sintetică.
CABINET_REAL = "PROBA P3 SUCCESS PATH"
UTILIZATOR_REAL = "proba-p3-succes@iconta.local"
PREFIX_SCHEMA_REAL = "proba_p3s_"

#: Rutele cu N+1 care deschid schema fiecărei firme — singurele la care calea de succes diferă.
RUTE_SUCCES = ("/migrare/asociati", "/migrare/mijloace-fixe", "/migrare/salariati",
               "/migrare/parteneri")


def curata_reale(conn):
    """Șterge cabinetul de probă, utilizatorul, firmele ȘI schemele lor. Idempotentă."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.accounting_firms WHERE nume = %s", (CABINET_REAL,))
        r = cur.fetchone()
        if r:
            fid = r[0]
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id = %s",
                        (fid,))
            firme = cur.fetchall()
            ids = [x[0] for x in firme]
            if ids:
                # `audit_log` E în listă, și nu e un detaliu: middleware-ul de audit scrie acolo la
                # FIECARE cerere, deci o sondă care folosește firmele astea lasă în urmă rânduri
                # care trimit la firme inexistente. S-a întâmplat — 60 de orfani în producție, de
                # la o sondă ad-hoc care nu știa. *Curățenia comună e locul unde disciplina nu se
                # poate uita; în fiecare sondă în parte, se uită.*
                for t in ("firma_rezumat", "firma_sursa_versiune", "firma_tip", "supervizor_sursa",
                          "supervizor_rezultat", "user_tenants", "declaratii_depuse", "audit_log"):
                    cur.execute("DELETE FROM public.%s WHERE tenant_id = ANY(%%s)" % t, (ids,))
                cur.execute("DELETE FROM public.tenants WHERE id = ANY(%s)", (ids,))
            for _tid, sch in firme:
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % sch)
            # și rândurile de audit ale utilizatorului sintetic, nu doar ale firmelor lui:
            # `audit_log` poartă și `user_id`, iar un rând cu utilizator inexistent e tot orfan
            cur.execute(
                "DELETE FROM public.audit_log WHERE user_id IN "
                " (SELECT id FROM public.users WHERE accounting_firm_id = %s OR email = %s)",
                (fid, UTILIZATOR_REAL))
            cur.execute("DELETE FROM public.users WHERE accounting_firm_id = %s OR email = %s",
                        (fid, UTILIZATOR_REAL))
            cur.execute("DELETE FROM public.accounting_firms WHERE id = %s", (fid,))
        else:
            cur.execute("DELETE FROM public.users WHERE email = %s", (UTILIZATOR_REAL,))
        # scheme ramase din rulari intrerupte
        cur.execute("SELECT nspname FROM pg_namespace WHERE nspname LIKE %s",
                    (PREFIX_SCHEMA_REAL + "%",))
        for (sch,) in cur.fetchall():
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % sch)


def construieste_reale(conn, n):
    """`n` firme cu SCHEMĂ ADEVĂRATĂ din `tenant_template.sql`. Întoarce `(uid, ids)`.

    Fiecare firmă primește și un `firma_profil` completat: fără el, rutele ar putea ieși pe altă
    ramură decât cea măsurată, iar „calea de succes" ar fi din nou altceva decât spune numele."""
    from core import tenant_provisioning as TP
    cale_tpl = os.path.join(RAD, "tenant_template.sql")
    with open(cale_tpl, encoding="utf-8") as f:
        tpl = f.read()

    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.accounting_firms (nume, activ) VALUES (%s, true) "
                    "RETURNING id", (CABINET_REAL,))
        fid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO public.users (email, password_hash, rol, accounting_firm_id, activ) "
            "VALUES (%s, %s, 'admin_firma', %s, true) RETURNING id",
            (UTILIZATOR_REAL, "scrypt$fara-parola", fid))
        uid = cur.fetchone()[0]

    ids = []
    for i in range(n):
        sch = "%s%03d" % (PREFIX_SCHEMA_REAL, i)
        TP.creeaza_schema(conn, sch, tpl)
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, activ) "
                "VALUES (%s, %s, NULL, %s, true) RETURNING id",
                (sch, "PROBA P3 SUCCES %03d" % i, fid))
            tid = cur.fetchone()[0]
            cur.execute('INSERT INTO "%s".firma_profil (id, nume, cui, serie_factura, '
                        '  urmator_numar_factura, tip_firma, regim_fiscal, platitor_tva, '
                        "  tip_decont, operatiuni_ic) "
                        "VALUES (1,'PROBA P3 SUCCES','12345678','PS',1,'srl','micro',true,'L',"
                        "        false) ON CONFLICT (id) DO NOTHING" % sch)
        ids.append(tid)
    conn.commit()
    return uid, ids


def _panta(puncte):
    """`(baza, panta, liniar)` dintr-un set de `(n, y)`. Cu trei puncte se poate VERIFICA
    liniaritatea, nu doar presupune — de-aia se măsoară la trei valori ale lui N, nu la două."""
    puncte = sorted(puncte)
    (n0, y0), (nk, yk) = puncte[0], puncte[-1]
    panta = (yk - y0) / float(nk - n0) if nk != n0 else 0.0
    baza = y0 - panta * n0
    liniar = all(abs((baza + panta * n) - y) < 1e-6 for n, y in puncte)
    return baza, panta, liniar


def curba_succes(nn=(5, 10, 14), rute=None):
    """Calea de SUCCES, pe scheme reale. `{ruta: {puncte, BASE_*, *_PER_FIRM, liniar}}`."""
    from core import db as _db
    _db.init_pool()
    rute = list(rute or RUTE_SUCCES)
    brut = {}
    for n in nn:
        with _db.get_conn() as conn:
            curata_reale(conn)
            conn.commit()
        with _db.get_conn() as conn:
            uid, _ids = construieste_reale(conn, n)
            tok = MR._token(conn, uid)
        with MR.client_test() as cl:
            cl.get(rute[0], headers={"Authorization": "Bearer " + tok})     # încălzire
            brut[n] = {r: masoara_ruta(cl, tok, r) for r in rute}
        print("   REAL N=%-3d %s" % (n, {r: "%dq/%dc %.3fs" % (v["interogari"], v["conexiuni"],
                                                               v["total_sec"])
                                         for r, v in brut[n].items()}), flush=True)
    with _db.get_conn() as conn:
        curata_reale(conn)
        conn.commit()

    out = {}
    for r in rute:
        pq = [(n, brut[n][r]["interogari"]) for n in nn]
        pc = [(n, brut[n][r]["conexiuni"]) for n in nn]
        bq, sq, lq = _panta(pq)
        bc, sc, lc = _panta(pc)
        out[r] = {"puncte": {str(n): brut[n][r] for n in nn},
                  "BASE_QUERIES": round(bq, 3), "QUERIES_PER_FIRM": round(sq, 3),
                  "BASE_CONNECTIONS": round(bc, 3), "CONNECTIONS_PER_FIRM": round(sc, 3),
                  "liniar_interogari": lq, "liniar_conexiuni": lc,
                  "statusuri": sorted({brut[n][r]["status"] for n in nn})}
    return out, brut


# ============================================================================
#  DE CE DIFERĂ — instrucțiunile, capturate pe amândouă căile
# ============================================================================
class _CursorSpion:
    def __init__(self, real, jurnal):
        self._real, self._j = real, jurnal

    def execute(self, sql, params=None):
        try:
            m = self._real.mogrify(sql, params)
            m = m.decode("utf-8", "replace") if isinstance(m, bytes) else m
        except Exception:
            m = sql if isinstance(sql, str) else str(sql)
        self._j.append(" ".join(m.split())[:200])
        return self._real.execute(sql, params) if params is not None else self._real.execute(sql)

    def __getattr__(self, n):
        return getattr(self._real, n)

    def __enter__(self):
        self._real.__enter__()
        return self

    def __exit__(self, *a):
        return self._real.__exit__(*a)

    def __iter__(self):
        return iter(self._real)


class _ConnSpion:
    def __init__(self, real, jurnal):
        self._real, self._j = real, jurnal

    def cursor(self, *a, **k):
        return _CursorSpion(self._real.cursor(*a, **k), self._j)

    def __getattr__(self, n):
        return getattr(self._real, n)


@contextlib.contextmanager
def spioneaza():
    from core import db as _db
    jurnal = []
    original = _db.get_conn

    @contextlib.contextmanager
    def get_conn_spionat(schema=None):
        jurnal.append("-- get_conn(schema=%r)" % schema)
        with original(schema) as c:
            yield _ConnSpion(c, jurnal)

    _db.get_conn = get_conn_spionat
    try:
        yield jurnal
    finally:
        _db.get_conn = original


def de_ce_difera(ruta="/migrare/asociati"):
    """Instrucțiunile executate pentru O firmă, pe schemă REALĂ vs pe schemă INEXISTENTĂ.

    Nu se explică din citirea codului: se **captează** amândouă și se arată diferența."""
    from core import db as _db
    _db.init_pool()
    out = {}

    with _db.get_conn() as conn:
        curata_reale(conn)
        conn.commit()
    with _db.get_conn() as conn:
        uid, _ids = construieste_reale(conn, 1)
        tok = MR._token(conn, uid)
    with MR.client_test() as cl:
        with spioneaza() as j:
            cl.get(ruta, headers={"Authorization": "Bearer " + tok})
    out["real"] = list(j)
    with _db.get_conn() as conn:
        curata_reale(conn)
        conn.commit()

    with _db.get_conn() as conn:
        MR.curata(conn)
        conn.commit()
    with _db.get_conn() as conn:
        uid, _ids = MR.construieste(conn, 1, 10, rece=False)
        tok = MR._token(conn, uid)
    with MR.client_test() as cl:
        with spioneaza() as j:
            cl.get(ruta, headers={"Authorization": "Bearer " + tok})
    out["sintetic"] = list(j)
    with _db.get_conn() as conn:
        MR.curata(conn)
        conn.commit()
    return out


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
