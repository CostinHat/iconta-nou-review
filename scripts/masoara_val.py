# -*- coding: utf-8 -*-
"""scripts/masoara_val.py — BEFORE / AFTER pentru un val de remediere P3.

**CE FACE, și de ce e un instrument și nu un script de o dată.** Un val de remediere are trei
întrebări, iar toate trei se pun de două ori — înainte și după:

  1. **crește costul cu N?** — curba de interogări și conexiuni, la N = 5…1000;
  2. **răspunde la fel?** — paritate pe portofoliul REAL, comparând corpurile JSON **întregi**;
  3. **cât costă?** — latență, octeți, procentul petrecut în bază.

Modul `--inainte` scrie un instantaneu; `--dupa` îl citește și îl confruntă. *Paritatea nu se poate
măsura după fapt: dacă răspunsul dinainte nu e păstrat, „identic" devine o amintire.*

**PARITATEA SE FACE PE CORPUL ÎNTREG, cu `==`.** Fără normalizare, fără sortare, fără rotunjire.
Singurul lucru scos e ordinea firmelor — nu, nici ea: rutele întorc firmele în ordinea dată de
`tenantii_userului` (`ORDER BY nume`), deci ordinea E parte din contract și se compară.

**DOMENIUL curbei**, declarat: firme sintetice cu schemă proprie **reală, dar goală**. Pentru rutele
care nu deschid schema firmei (cele din valul A) e fidel; pentru cele care o deschid, coeficientul
căii de succes se măsoară separat, pe scheme construite din `tenant_template.sql`
(`masoara_p3.curba_succes`). *Se scrie aici ca cifra să nu fie citită mai larg decât e.*
"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import masoara_p3 as MP          # noqa: E402
import masoara_rute_portofoliu as MR  # noqa: E402

VALURI = {
    "a": ("/migrare/istoric-declaratii", "/supervizor"),
    "b": ("/migrare/parteneri", "/migrare/asociati", "/migrare/mijloace-fixe",
          "/migrare/salariati"),
}

NN = (5, 50, 100, 250, 500, 1000)


def _commit():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                          cwd=RAD).stdout.strip()


def _token_real():
    """Utilizatorul de cabinet cu cele mai multe firme REALE, și tokenul lui."""
    import psycopg2.extras as _E
    from core import auth_api, db as _db
    _db.init_pool()
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
    return uid, cate, auth_api.emite_token(u)


def corpuri_reale(rute):
    """Corpurile JSON ÎNTREGI, pe portofoliul real — materia primă a parității."""
    uid, cate, tok = _token_real()
    out = {}
    with MR.client_test() as cl:
        cl.get(rute[0], headers={"Authorization": "Bearer " + tok})
        for r in rute:
            resp = cl.get(r, headers={"Authorization": "Bearer " + tok})
            out[r] = {"status": resp.status_code, "corp": resp.json() if resp.status_code == 200
                      else resp.text}
    return {"uid": uid, "firme": cate, "rute": out}


def curba(rute, nn=NN):
    from core import db as _db
    _db.init_pool()
    out = {}
    for n in nn:
        with _db.get_conn() as conn:
            MR.curata(conn)
            conn.commit()
        with _db.get_conn() as conn:
            uid, _ids = MR.construieste(conn, n, procent_invalidat=10, rece=False)
            tok = MR._token(conn, uid)
        with MR.client_test() as cl:
            cl.get(rute[0], headers={"Authorization": "Bearer " + tok})
            out[n] = {r: MP.masoara_ruta(cl, tok, r) for r in rute}
        print("   N=%-5d %s" % (n, {r: "%dq/%dc %.3fs" % (v["interogari"], v["conexiuni"],
                                                          v["total_sec"])
                                    for r, v in out[n].items()}), flush=True)
    with _db.get_conn() as conn:
        MR.curata(conn)
        conn.commit()
    return out


def pante(curba_rez, rute, nn=NN):
    out = {}
    for r in rute:
        pq = [(n, curba_rez[n][r]["interogari"]) for n in nn]
        pc = [(n, curba_rez[n][r]["conexiuni"]) for n in nn]
        bq, sq, lq = MP._panta(pq)
        bc, sc, lc = MP._panta(pc)
        out[r] = {"BASE_QUERIES": bq, "QUERY_SLOPE": sq, "liniar_q": lq,
                  "BASE_CONNECTIONS": bc, "CONNECTION_SLOPE": sc, "liniar_c": lc}
    return out


def masoara(val, eticheta):
    rute = list(VALURI[val])
    print("── %s · val %s · rute: %s ──" % (eticheta.upper(), val.upper(), ", ".join(rute)),
          flush=True)
    reale = corpuri_reale(rute)
    print("   portofoliu real: %d firme (uid %s)" % (reale["firme"], reale["uid"]), flush=True)
    c = curba(rute)
    return {"commit": _commit(), "eticheta": eticheta, "val": val, "rute": rute,
            "curba": {str(k): v for k, v in c.items()}, "pante": pante(c, rute),
            "real": reale}


def _cale(val, eticheta):
    d = os.path.join(RAD, "masuratori", "p3")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "wave_%s_%s.json" % (val, eticheta))


def compara(val):
    """Confruntă instantaneul de dinainte cu cel de acum. Întoarce raportul, nu-l tipărește."""
    inainte = json.load(io.open(_cale(val, "inainte"), encoding="utf-8"))
    dupa = json.load(io.open(_cale(val, "dupa"), encoding="utf-8"))
    rap = {"val": val, "commit_inainte": inainte["commit"], "commit_dupa": dupa["commit"],
           "rute": {}}
    for r in inainte["rute"]:
        a = inainte["real"]["rute"][r]
        b = dupa["real"]["rute"][r]
        pa, pb = inainte["pante"][r], dupa["pante"][r]
        ca, cb = inainte["curba"], dupa["curba"]
        rap["rute"][r] = {
            "BEFORE_QUERIES_N1000": ca["1000"][r]["interogari"],
            "AFTER_QUERIES_N1000": cb["1000"][r]["interogari"],
            "BEFORE_CONNECTIONS_N1000": ca["1000"][r]["conexiuni"],
            "AFTER_CONNECTIONS_N1000": cb["1000"][r]["conexiuni"],
            "BEFORE_LATENCY_MS_N1000": round(ca["1000"][r]["total_sec"] * 1000, 1),
            "AFTER_LATENCY_MS_N1000": round(cb["1000"][r]["total_sec"] * 1000, 1),
            "PAYLOAD_BYTES_N1000": cb["1000"][r]["octeti"],
            "BEFORE_QUERY_SLOPE": pa["QUERY_SLOPE"], "AFTER_QUERY_SLOPE": pb["QUERY_SLOPE"],
            "BEFORE_CONNECTION_SLOPE": pa["CONNECTION_SLOPE"],
            "AFTER_CONNECTION_SLOPE": pb["CONNECTION_SLOPE"],
            "status_inainte": a["status"], "status_dupa": b["status"],
            "PARITY": "PASS" if (a["status"] == b["status"] and a["corp"] == b["corp"])
                      else "FAIL",
        }
    return rap


if __name__ == "__main__":
    val = sys.argv[1] if len(sys.argv) > 1 else "a"
    mod = sys.argv[2] if len(sys.argv) > 2 else "inainte"
    if mod == "compara":
        r = compara(val)
        print(json.dumps(r, ensure_ascii=False, indent=2, default=str))
        sys.exit(0)
    rez = masoara(val, mod)
    cale = _cale(val, mod)
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        json.dump(rez, f, ensure_ascii=False, indent=2, default=str)
    print("\nscris: %s" % cale)
    print("pante:")
    for r, p in rez["pante"].items():
        print("   %-30s q: %s + %s*N (liniar %s) | c: %s + %s*N (liniar %s)"
              % (r, p["BASE_QUERIES"], p["QUERY_SLOPE"], p["liniar_q"],
                 p["BASE_CONNECTIONS"], p["CONNECTION_SLOPE"], p["liniar_c"]))
