# -*- coding: utf-8 -*-
"""SESIUNEA B — F4 ETAPA 3 (RIP) + ETAPA 8 (Fisa D212) pe PFA sistem real. tenant_052.
Idempotent: sare operatiunile RIP care exista deja (dupa explicatie). Vezi asteptari_f4.md.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; ./venv/bin/python frontend_test/proba_f4_etapa3_8.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import rip_api  # noqa: E402

SCH = "tenant_052"
AN = 2026
UID = 71507
OPS = [
    {"data_operatiune": "2026-03-10", "tip": "incasare", "categorie": "activitate",
     "explicatie": "F4 venituri activitate IT", "suma": 100000, "metoda": "banca"},
    {"data_operatiune": "2026-04-15", "tip": "plata", "categorie": "cheltuiala_deductibila",
     "explicatie": "F4 cheltuieli deductibile", "suma": 30000, "metoda": "banca",
     "deductibilitate": "integrala"},
]


def main():
    _db.init_pool()
    print("=== ETAPA 3: operatiuni RIP (registru incasari/plati, partida simpla) ===")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        for op in OPS:
            with conn.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % SCH)
                cur.execute('SELECT id, status FROM rip_operatiuni WHERE explicatie=%s', (op["explicatie"],))
                ex = cur.fetchone()
            if ex:
                rid, st = ex[0], ex[1]
                print("  %s: exista deja (id=%s status=%s) -> sar" % (op["explicatie"], rid, st))
            else:
                r = rip_api.adauga(conn, SCH, op, user_id=UID)
                if r.get("eroare"):
                    print("  %s: EROARE %s" % (op["explicatie"], r["eroare"])); continue
                rid = r["id"]
                print("  %s: adaugat id=%s (%s %s %s lei)" % (op["explicatie"], rid, op["tip"], op["categorie"], op["suma"]))
            conn.commit()
            # valideaza (ciorna -> validata)
            v = rip_api.valideaza(conn, SCH, rid, user_id=UID)
            print("    valideaza -> %s" % (v.get("status") or v.get("eroare")))
            conn.commit()

    print("\n=== ETAPA 8: Fisa D212 (sistem real, din RIP) ===")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        fisa = rip_api.fisa_d212(conn, SCH, AN)
    # afiseaza componentele-cheie
    def g(d, *ks):
        for k in ks:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return None
        return d
    print("  venit_brut:", g(fisa, "venit_brut") or g(fisa, "fisa", "venit_brut"))
    print("  cheltuieli_deductibile:", g(fisa, "cheltuieli_deductibile") or g(fisa, "fisa", "cheltuieli_deductibile"))
    print("  venit_net:", g(fisa, "venit_net") or g(fisa, "fisa", "venit_net"))
    print("  cas:", g(fisa, "cas") or g(fisa, "fisa", "cas"))
    print("  cass:", g(fisa, "cass") or g(fisa, "fisa", "cass"))
    print("  impozit:", g(fisa, "impozit") or g(fisa, "fisa", "impozit"))
    print("  total_datorat:", g(fisa, "total_datorat") or g(fisa, "fisa", "total_datorat"))
    print("  [fisa brut]:", {k: fisa[k] for k in list(fisa)[:8]} if isinstance(fisa, dict) else fisa)


if __name__ == "__main__":
    main()
