# -*- coding: utf-8 -*-
"""SESIUNEA B — F5 ETAPA 4 (salarizare) + ETAPA 8 (D112) pe SRL cu salariati. tenant_053.
2 salariati (CNP checksum-valid + COR nomenclator + salariu) -> stat de plata -> D112 + DUK.
REGES-ONLINE = API EXTERN (api.inspectiamuncii.ro, credentiale per CUI) -> confirmare STRUCTURALA.
Idempotent: sare salariatul cu CNP existent. Env: db.env + api_keys.env.
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import salariati_api, stat_plata_api, d112, duk  # noqa: E402

SCH = "tenant_053"
AN, LUNA = 2026, 6


def _cnp(base12):
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    s = sum(int(base12[i]) * ch[i] for i in range(12))
    c = s % 11
    return base12 + str(1 if c == 10 else c)


SALARIATI = [
    {"cnp": _cnp("185061512345"), "nume": "Ionescu", "prenume": "Vasile", "cor": "817207",
     "salariu_brut": 5000, "data_angajare": "2026-01-05", "tip_norma": "intreaga"},
    {"cnp": _cnp("290032012678"), "nume": "Popescu", "prenume": "Elena", "cor": "831204",
     "salariu_brut": 6000, "data_angajare": "2026-01-05", "tip_norma": "intreaga"},
]


def main():
    _db.init_pool()
    print("=== ETAPA 4: creare salariati + stat de plata ===")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        for s in SALARIATI:
            with conn.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % SCH)
                cur.execute("SELECT id FROM salariati WHERE cnp=%s", (s["cnp"],))
                ex = cur.fetchone()
            if ex:
                print("  %s %s (CNP %s): exista (id=%s) -> sar" % (s["nume"], s["prenume"], s["cnp"], ex[0]))
                continue
            try:
                r = salariati_api.creeaza_salariat(conn, **s)
                conn.commit()
                print("  %s %s: creat id=%s (COR %s, brut %s)" % (s["nume"], s["prenume"], r.get("salariat_id"), s["cor"], s["salariu_brut"]))
            except Exception as e:
                print("  %s %s: EROARE %s" % (s["nume"], s["prenume"], str(e)[:160]))

    print("\n=== stat de plata (%s/%s) ===" % (LUNA, AN))
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        try:
            st = stat_plata_api.stat_plata(conn, SCH, AN, LUNA)
            linii = st.get("linii") if isinstance(st, dict) else st
            n = len(linii) if isinstance(linii, list) else "?"
            print("  linii stat:", n)
            if isinstance(linii, list):
                for l in linii[:4]:
                    if isinstance(l, dict):
                        print("   ", {k: l.get(k) for k in ("nume", "salariu_brut", "cas", "cass", "impozit", "net") if k in l})
        except Exception as e:
            print("  stat_plata EROARE:", str(e)[:160])

    print("\n=== ETAPA 8: D112 + DUK ===")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        try:
            r = d112.genereaza(conn, SCH, AN, LUNA)
            xml = r[0] if isinstance(r, tuple) else r
            v = duk.valideaza(xml, "d112", an=AN, luna=LUNA, timeout=120)
            print("  D112:", (v.get("stare"), (v.get("erori") or "")[:160]) if isinstance(v, dict) else v)
        except Exception as e:
            print("  D112 EROARE:", str(e)[:200])

    print("\n=== REGES-ONLINE (structural, EXTERN) ===")
    try:
        from core import reges_client
        fns = [f for f in dir(reges_client) if not f.startswith("_")]
        print("  reges_client incarcat; simboluri:", [f for f in fns if callable(getattr(reges_client, f))][:8])
        print("  [EXTERN] submit live cere credentiale Inspectia Muncii per CUI (OpenID) - netestabil aici")
    except Exception as e:
        print("  reges_client EROARE:", str(e)[:120])


if __name__ == "__main__":
    main()
