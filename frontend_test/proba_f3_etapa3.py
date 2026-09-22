# -*- coding: utf-8 -*-
"""SESIUNEA B — F3 ETAPA 3 (operatiuni intracomunitare) prin FLUXUL UNIFICAT achizitie-ic + DUK.
F3 = SRL neplatitor TVA + art.317, micro 1%. tenant_051 (id 105781, admin uid 71507).

Intra 2 achizitii IC prin `achizitie_ic` (calea unica, DECIZII 66: factura + nota payer-aware +
D390 + operatiunea D301 legata). Verifica DB (nota = cont+446 in COST, NU 4426=4427; op D301 legata),
apoi genereaza D301/D390/D100/D406 + valideaza DUK, si confirma ca D390 numara fiecare achizitie O DATA.

Idempotent: sare achizitia daca numarul ei exista deja (re-rulare sigura). Vezi asteptari_f3_etapa3.md.
Env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; ./venv/bin/python frontend_test/proba_f3_etapa3.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)

import core.db as _db  # noqa: E402
from core import uc_tenants as _uc  # noqa: E402
from core import d301, d390, d100, d406, duk  # noqa: E402
from core.common import Perioada  # noqa: E402

SCH = "tenant_051"
TID = 105781
CTX = {"uid": 71507}
AN, LUNA = 2026, 6
ACHIZITII = [
    {"data": "2026-06-15", "valoare": 5000, "cod_tva_furnizor": "DE811569869",
     "numar": "DE-A-001", "furnizor_nume": "Lieferant DE GmbH", "cont_destinatie": "371",
     "tip": "bunuri", "cota": 21},
    {"data": "2026-06-15", "valoare": 2500, "cod_tva_furnizor": "DE811569869",
     "numar": "DE-B-001", "furnizor_nume": "Lieferant DE GmbH", "cont_destinatie": "628",
     "tip": "servicii", "cota": 21},
]


def _exista(cur, numar):
    cur.execute('SELECT count(*) FROM "%s".facturi WHERE numar=%%s' % SCH, (numar,))
    return cur.fetchone()[0] > 0


def _val(x, tip, an=AN, luna=LUNA):
    try:
        r = duk.valideaza(x, tip, an=an, luna=luna)
        return (r.get("stare"), (r.get("erori") or "")[:180]) if isinstance(r, dict) else (r, "")
    except Exception as e:
        return ("EROARE", str(e)[:180])


def main():
    _db.init_pool()
    print("=== INTRODUCERE 2 ACHIZITII IC prin achizitie-ic (flux unificat) ===")
    for a in ACHIZITII:
        with _db.get_conn() as c:
            with c.cursor() as cur:
                cur.execute('SET search_path TO "%s", public' % SCH)
                deja = _exista(cur, a["numar"])
        if deja:
            print("  %s (%s): exista deja -> sar (idempotent)" % (a["numar"], a["tip"]))
            continue
        r = _uc.achizitie_ic(TID, a, CTX)
        print("  %s (%s): factura_id=%s valoare=%s tva=%s"
              % (a["numar"], a["tip"], r.get("factura_id"), r.get("valoare"), r.get("tva")))

    print("\n=== VERIFICARE DB (nota payer-aware + op D301 legata) ===")
    with _db.get_conn() as c:
        cur = c.cursor()
        cur.execute('SET search_path TO "%s", public' % SCH)
        cur.execute("SELECT f.numar, l.cont_debit, l.cont_credit, l.suma "
                    "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id=i.id "
                    "JOIN facturi f ON f.id=i.factura_id "
                    "WHERE f.numar IN ('DE-A-001','DE-B-001') ORDER BY f.numar, l.id")
        for row in cur.fetchall():
            print("  nota %s: %s = %s  · %s" % (row[0], row[1], row[2], row[3]))
        cur.execute("SELECT nr_doc, tip, val_valuta, tva, partener_tara, factura_id "
                    'FROM "%s".d301_operatiuni WHERE an=%%s AND luna=%%s ORDER BY id' % SCH, (AN, LUNA))
        print("  --- operatiuni D301 (factura_id NENUL = legat de intrarea unica) ---")
        for row in cur.fetchall():
            print("  op %s tip=%s baza=%s tva=%s tara=%s factura_id=%s"
                  % (row[0], row[1], row[2], row[3], row[4], row[5]))

    print("\n=== DECLARATII + DUK ===")
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO "%s", public' % SCH)
        try:
            x = d301.genereaza(conn, SCH, Perioada(AN, luna=LUNA))
            x = x[0] if isinstance(x, tuple) else x
            print("  D301:", _val(x, "d301"))
        except Exception as e:
            print("  D301: EROARE", str(e)[:180])
        try:
            r = d390.genereaza(conn, SCH, AN, LUNA)
            xr = r[0] if isinstance(r, tuple) else r
            print("  D390:", _val(xr, "d390"))
        except Exception as e:
            print("  D390: EROARE", str(e)[:180])
        try:
            r = d100.genereaza(conn, SCH, Perioada(AN, trim=2))
            xr = r[0] if isinstance(r, tuple) else r
            print("  D100(T2 micro):", _val(xr, "d100", luna=None))
        except Exception as e:
            print("  D100: EROARE", str(e)[:180])
        try:
            r = d406.genereaza(conn, SCH, AN, LUNA)
            xr = r[0] if isinstance(r, tuple) else r
            print("  D406:", _val(xr, "d406"))
        except Exception as e:
            print("  D406: EROARE", str(e)[:180])

    print("\n=== NO-DOUBLE-COUNT: liniile D390 (asteptat cod A 5000 + cod S 2500, o data fiecare) ===")
    with _db.get_conn() as conn:
        prof, facturi = d390.pull(conn, SCH, AN, LUNA)
        rez = d390.calcul_d390(prof, AN, LUNA, facturi)
        ops = getattr(rez, "ops", None) or getattr(rez, "operatiuni", None) or []
        print("  linii D390:", len(ops))
        for o in ops:
            print("   ", o)


if __name__ == "__main__":
    main()
