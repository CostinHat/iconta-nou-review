# -*- coding: utf-8 -*-
"""scripts/masoara_rute_portofoliu.py — CURBA celor cinci rute de portofoliu, pe cererea ÎNTREAGĂ.

**DE CE EXISTĂ, și de ce nu e același lucru cu `masoara_interogari`.** Acela numără ce face un bloc
de cod. Ăsta cere ruta prin `TestClient`, deci prin dependențele ei — `cere_context`, `cere_cabinet`,
`tenantii_userului`, serializarea răspunsului. *Cifra care contează e cea pe care o plătește
cererea, nu cea pe care o plătește funcția pe care am ales s-o măsor.*

Diferența nu e teoretică: curba lui P2 din 08.09 dimineața a fost măsurată cu `tenantii_userului`
**înlocuit de ham**, deci interogările lui n-au intrat în cifră — nici înainte, nici după. Exact
acolo stătea O(N)-ul care a supraviețuit remedierii sub formă de cale de rezervă. Aici nu se
înlocuiește nimic din calea de cerere.

**AL DOILEA MOTIV, la fel de important: cifra trebuie să se poată RECALCULA.** Curba de dimineață a
fost produsă de un ham care n-a rămas nicăieri; ea nu mai e o măsurătoare, e o amintire. Ăsta e un
fișier din repo, cu scenariul lui scris, și se rulează din nou oricând.

**SCENARIUL, declarat.** Domeniu sintetic: `N` firme în `public.tenants`, legate de un cabinet de
probă, fiecare cu **schema ei — reală, dar GOALĂ**.

Prima formă a hamului voia să cicleze schemele REALE peste firmele sintetice, ca munca per firmă să
fie reală. Nu se poate: `tenants.schema_name` are constrângere de unicitate. Calea de citire a lui
P2 oricum **nu deschide nicio schemă** — citește modelul din `public`, o interogare pentru tot
portofoliul —, deci pentru ea numele schemei nici nu contează.

**A doua formă lăsa schemele INEXISTENTE, și era greșită.** `SET search_path TO "inexistenta",
public` e acceptat de PostgreSQL, care ignoră tăcut schemele care lipsesc; o rută care execută apoi
un `CREATE TABLE IF NOT EXISTS` necalificat nimerește prima schemă existentă din cale — `public`.
Măsurând `/migrare/parteneri` la diagnosticul P3, sonda a creat `public.solduri_parteneri` în
producție. *„N-are ce scrie" era o presupunere, nu o garanție* — și e chiar clasa „sonda de audit nu
e read-only".

Acum schema există și e goală. `to_regclass('tabela')` întoarce tot `NULL`, deci **ramura măsurată
nu se schimbă**, dar orice scriere necalificată aterizează în schema de probă, care se șterge la
curățenie.

**Ce rămâne adevărat despre domeniul sintetic:** dacă vreo ramură ar cădea pe muncă per firmă, ea ar
da peste o schemă goală — și ar ieși ori ca interogări care cresc cu N (contorul le vede), ori ca un
răspuns care nu mai e 200. Ce **nu** mai afirmăm e că numărul de interogări per firmă ar fi identic
cu cel de pe o schemă reală: nu e, iar `curba_succes()` din `masoara_p3.py` îl măsoară separat.

**CE NU ACOPERĂ, scris ca să nu se citească mai mult decât spune:**
  * nu măsoară costul RECALCULĂRII (cel mutat din cerere), ci al cererii. Recalcularea se măsoară
    unde se plătește: în lucrător.
  * firmele sintetice n-au triggere proprii; rândurile de model se seamănă direct. Se măsoară calea
    de CITIRE, iar ea nu știe cum au apărut rândurile. Invalidarea are propriile gărzi, pe o firmă
    cu schemă și triggere adevărate (`core/test_firma_rezumat.py`).
  * paritatea verdictelor se probează separat, pe firme REALE (`core/test_paritate_p2.py`) — aici
    se numără interogări, nu se verifică adevărul răspunsului.
  * latența depinde de mașină și de cât e încărcată; **numărul de interogări** e cifra robustă, și
    e chiar cerința. Secundele sunt orientative.
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

import masoara_interogari as MI  # noqa: E402

RUTE = ("/migrare/solduri", "/migrare/plan-conturi", "/migrare/vector",
        "/termene", "/control-fiscal")

#: Domeniul firmelor sintetice. Deasupra oricărui `tenant_id` real; curățenia pleacă de la cabinet.
CABINET_PROBA = "PROBA CURBA P2"
UTILIZATOR_PROBA = "proba-curba-p2@iconta.local"


# ============================================================================
#  DOMENIUL SINTETIC
# ============================================================================
def curata(conn):
    """Șterge tot domeniul sintetic. Idempotentă; se cheamă și înainte, și după."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM public.accounting_firms WHERE nume = %s", (CABINET_PROBA,))
        r = cur.fetchone()
        if not r:
            cur.execute("DELETE FROM public.users WHERE email = %s", (UTILIZATOR_PROBA,))
            return 0
        fid = r[0]
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id = %s",
                    (fid,))
        randuri = cur.fetchall()
        ids = [x[0] for x in randuri]
        # ȘTERGEREA SCHEMELOR SE FACE ÎN LOTURI, cu `commit` după fiecare.
        # `DROP SCHEMA ... CASCADE` ține blocaje până la capătul tranzacției; la 1000 de scheme
        # într-una singură, PostgreSQL cade cu `out of shared memory / max_locks_per_transaction`
        # — iar curățenia PICĂ tocmai când e cel mai mult de curățat, lăsând în urmă exact
        # mizeria pe care venise s-o strângă. *S-a întâmplat la N=1000, pe 09.09.2026.*
        LOT_DROP = 50
        for i in range(0, len(randuri), LOT_DROP):
            for _t, sch in randuri[i:i + LOT_DROP]:
                cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % sch)
            conn.commit()
        if ids:
            for t in ("firma_rezumat", "firma_sursa_versiune", "firma_tip", "supervizor_sursa",
                      "supervizor_rezultat", "user_tenants"):
                cur.execute("DELETE FROM public.%s WHERE tenant_id = ANY(%%s)" % t, (ids,))
            cur.execute("DELETE FROM public.tenants WHERE id = ANY(%s)", (ids,))
        cur.execute("DELETE FROM public.users WHERE accounting_firm_id = %s OR email = %s",
                    (fid, UTILIZATOR_PROBA))
        cur.execute("DELETE FROM public.accounting_firms WHERE id = %s", (fid,))
        return len(ids)


def construieste(conn, n, procent_invalidat=0, rece=False, azi=None):
    """Creează `n` firme sintetice + cabinet + utilizator. Întoarce `(uid, ids)`.

    `rece=True` = **niciun rând de model**, adică exact starea de după o repornire cu baza refăcută
    sau după adăugarea unui lot de firme. E scenariul în care prima formă a lui P2 cădea înapoi pe
    bucla per firmă, deci e cel care trebuie măsurat, nu ocolit."""
    from core import firma_rezumat as FR
    from core.common import azi_ro as _azi_ro
    azi = azi or _azi_ro()

    with conn.cursor() as cur:
        cur.execute("INSERT INTO public.accounting_firms (nume, activ) VALUES (%s, true) "
                    "RETURNING id", (CABINET_PROBA,))
        fid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO public.users (email, password_hash, rol, accounting_firm_id, activ) "
            "VALUES (%s, %s, 'admin_firma', %s, true) RETURNING id",
            (UTILIZATOR_PROBA, "scrypt$fara-parola", fid))
        uid = cur.fetchone()[0]

        ids = []
        for i in range(n):
            # ── SCHEMĂ REALĂ, DAR GOALĂ ─────────────────────────────────────────────
            # Prima formă lăsa schemele INEXISTENTE. Părea inofensiv — calea de citire nu
            # deschide nicio schemă —, dar nu era: `SET search_path TO "inexistenta", public`
            # e ACCEPTAT de PostgreSQL, care ignoră tăcut schemele care lipsesc. O rută care
            # apoi execută un `CREATE TABLE IF NOT EXISTS` NECALIFICAT nimerește prima schemă
            # existentă din cale — adică `public`. *Măsurând `/migrare/parteneri`, sonda a
            # creat `public.solduri_parteneri` în producție.*
            #
            # Cu schema creată (și goală), `to_regclass('tabela')` întoarce tot `NULL` — deci
            # ramura măsurată rămâne aceeași —, dar orice scriere necalificată aterizează în
            # schema de probă, care se șterge la curățenie. *O sondă de măsurare n-are voie să
            # lase nimic în urmă, iar „n-are ce scrie" e o presupunere, nu o garanție.*
            sch = "proba_curba_%06d" % i
            cur.execute('CREATE SCHEMA IF NOT EXISTS "%s"' % sch)
            cur.execute(
                "INSERT INTO public.tenants (schema_name, nume, cui, accounting_firm_id, activ) "
                "VALUES (%s, %s, %s, %s, true) RETURNING id",
                (sch, "PROBA CURBA %05d" % i, None, fid))
            ids.append(cur.fetchone()[0])

        # proiecția `tip_firma` — pe calea reală o pune triggerul de pe `firma_profil`. Firmele
        # sintetice n-au schemă, deci se seamănă direct: ce se măsoară e că valoarea E acolo și
        # intră în interogarea listei, nu de unde a venit.
        cur.executemany(
            "INSERT INTO public.firma_tip (tenant_id, tip_firma) VALUES (%s, 'srl') "
            "ON CONFLICT (tenant_id) DO UPDATE SET tip_firma = EXCLUDED.tip_firma",
            [(t,) for t in ids])

        if not rece:
            cur.executemany(
                "INSERT INTO public.firma_sursa_versiune (tenant_id, tabela, versiune) "
                "VALUES (%s, %s, 5) "
                "ON CONFLICT (tenant_id, tabela) DO UPDATE SET versiune = 5",
                [(t, tab) for t in ids for tab in FR.tabele_urmarite()])
    conn.commit()

    if not rece:
        prag = int(round(n * procent_invalidat / 100.0))
        v = FR.versiuni_aspecte(conn, ids[0], list(FR.TOATE))
        for i, tid in enumerate(ids):
            invalid = i < prag
            for aspect in FR.TOATE:
                FR.scrie(conn, tid, aspect,
                         {"stare": "verde", "lipsa": 0, "urmarit": 0, "neclar": 0,
                          "contabil": [], "conturi": 3, "are_solduri": True, "randuri": 2,
                          "completat": True, "eval": None, "neevaluat": None},
                         v[aspect] - 1 if invalid else v[aspect],
                         epoca=FR.epoca_pentru(aspect, azi))
        conn.commit()
    return uid, ids


def _token(conn, uid):
    import psycopg2.extras as _E
    from core import auth_api
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, rol, accounting_firm_id FROM public.users WHERE id = %s", (uid,))
        u = dict(cur.fetchone())
    return auth_api.emite_token(u)


# ============================================================================
#  MĂSURAREA UNEI RUTE, prin cererea ÎNTREAGĂ
# ============================================================================
@contextlib.contextmanager
def client_test():
    """`TestClient(app)` FĂRĂ lifespan: pornirea aplicației ar aplica DDL și ar migra triggerele la
    fiecare măsurătoare, iar cifrele ar cuprinde munca de pornire, nu munca cererii."""
    from fastapi.testclient import TestClient
    import main as _main
    from core import db as _db
    _db.init_pool()
    c = TestClient(_main.app)
    try:
        yield c
    finally:
        c.close()


def masoara_ruta(client, token, ruta):
    with MI.numara() as n:
        r = client.get(ruta, headers={"Authorization": "Bearer " + token})
    d = n.dict()
    d["status"] = r.status_code
    d["octeti"] = len(r.content)
    if r.status_code != 200:
        d["corp"] = r.text[:200]
    return d


# ============================================================================
#  CALIBRAREA HAMULUI — ambele direcții, PRIN STRATUL HTTP
# ============================================================================
def calibreaza(verbose=True):
    """`(ok, detalii)`.

    `masoara_interogari` e deja calibrat pe blocuri de cod; ce NU s-a dovedit încă e că învelișul
    lui **supraviețuiește stratului HTTP** — că `TestClient` nu rulează ruta pe alt fir sau pe alt
    modul `db`, caz în care contorul ar raporta liniștit ZERO pentru orice rută, iar toate curbele
    de mai jos ar arăta minunat și n-ar însemna nimic.

    Deci: o rută înregistrată anume pentru probă, care face **o interogare per element**, măsurată la
    5 și la 50. Trebuie (a) să se vadă, (b) să CREASCĂ cu N. Și una set-based, care nu trebuie să
    crească. *Un contor care numără zero prin HTTP arată exact ca o rută perfect optimizată.*"""
    from core import db as _db
    import main as _main
    _db.init_pool()

    cale_rea, cale_buna = "/_proba_curba_n_plus_1", "/_proba_curba_set_based"
    if not any(getattr(r, "path", None) == cale_rea for r in _main.app.routes):
        @_main.app.get(cale_rea)
        def _proba_rea(n: int = 5):
            for i in range(n):
                with _db.get_conn() as c:
                    with c.cursor() as cur:
                        cur.execute("SELECT %s", (i,))
                        cur.fetchone()
            return {"n": n}

        @_main.app.get(cale_buna)
        def _proba_buna(n: int = 5):
            with _db.get_conn() as c:
                with c.cursor() as cur:
                    cur.execute("SELECT x FROM unnest(%s::int[]) AS t(x)", (list(range(n)),))
                    cur.fetchall()
            return {"n": n}

    det = {}
    with client_test() as cl:
        for eticheta, cale in (("n_plus_1", cale_rea), ("set_based", cale_buna)):
            for n in (5, 50):
                with MI.numara() as m:
                    r = cl.get("%s?n=%d" % (cale, n))
                det["%s_%d" % (eticheta, n)] = dict(m.dict(), status=r.status_code)

    vede_ceva = det["n_plus_1_5"]["interogari"] > 0
    creste = det["n_plus_1_50"]["interogari"] >= det["n_plus_1_5"]["interogari"] * 5
    nu_creste = det["set_based_50"]["interogari"] == det["set_based_5"]["interogari"] == 1
    ok = vede_ceva and creste and nu_creste
    if verbose:
        print("CALIBRARE ham HTTP (ambele direcții, prin TestClient):")
        for k in sorted(det):
            print("   %-16s -> %s" % (k, det[k]))
        print("   vede interogările prin HTTP      :", vede_ceva)
        print("   vede CREȘTEREA cu N              :", creste)
        print("   vede și cazul CORECT (constant)  :", nu_creste)
        print("   VERDICT:", "OK" if ok else "PICAT — nicio curbă de mai jos n-ar valora nimic")
    return ok, det


# ============================================================================
#  CURBA
# ============================================================================
def curba(nn=(5, 50, 100, 250, 500, 1000), scenarii=((0, False), (10, False), (100, False),
                                                     (0, True)), azi=None):
    """`{scenariu: {n: {ruta: masuratoare}}}`. `scenarii` = `(procent_invalidat, rece)`."""
    from core import db as _db
    _db.init_pool()
    out = {}
    for procent, rece in scenarii:
        eticheta = "model_rece" if rece else "invalidat_%d%%" % procent
        out[eticheta] = {}
        for n in nn:
            with _db.get_conn() as conn:
                curata(conn)
                conn.commit()
            with _db.get_conn() as conn:
                uid, ids = construieste(conn, n, procent, rece, azi=azi)
                tok = _token(conn, uid)
            with client_test() as cl:
                # o cerere de încălzire, nemăsurată: prima cerere plătește importurile leneșe ale
                # rutei, iar aia e o cifră despre Python, nu despre portofoliu
                cl.get(RUTE[0], headers={"Authorization": "Bearer " + tok})
                out[eticheta][n] = {r: masoara_ruta(cl, tok, r) for r in RUTE}
            print("   %s N=%-5d %s" % (eticheta, n, {
                r: "%dq/%dc/%.3fs" % (v["interogari"], v["conexiuni"], v["secunde"])
                for r, v in out[eticheta][n].items()}), flush=True)
    with _db.get_conn() as conn:
        curata(conn)
        conn.commit()
    return out


def _tipar(rez):
    for eticheta, pe_n in rez.items():
        print("\n═══ scenariu: %s ═══" % eticheta)
        print("%-22s %s" % ("ruta", "  ".join("N=%d" % n for n in sorted(pe_n))))
        for r in RUTE:
            celule = []
            for n in sorted(pe_n):
                v = pe_n[n][r]
                celule.append("%d q / %d c" % (v["interogari"], v["conexiuni"]))
            print("%-22s %s" % (r, "  |  ".join(celule)))
        stat = {n: pe_n[n][RUTE[0]]["status"] for n in sorted(pe_n)}
        if set(stat.values()) != {200}:
            print("   ! statusuri neuniforme: %s" % stat)


if __name__ == "__main__":
    t0 = time.time()
    ok, _ = calibreaza()
    if not ok:
        sys.exit(2)
    print()
    rez = curba()
    _tipar(rez)
    cale = os.path.join(RAD, "curba_rute_p2.json")
    with open(cale, "w", encoding="utf-8", newline="") as f:
        json.dump(rez, f, ensure_ascii=False, indent=2, default=str)
    print("\nscris: %s   (total %.1fs)" % (cale, time.time() - t0))
