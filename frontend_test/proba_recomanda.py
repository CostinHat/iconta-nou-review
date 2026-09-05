# -*- coding: utf-8 -*-
"""LOTUL 15 — proba pe ruta care trimite invitatia, cu o adresa care NU e o adresa.

DE CE PE RUTA, si nu pe ecran: butonul «Trimite invitația» cade sub `OPRITE` — iese din
aplicatie. Intrebarea campaniei se pune totusi: ce raspunde cand primeste `«»@#$%`?
Santinela e aleasa astfel incat sa nu poata fi adresa nimanui: daca refuzul lipseste si
cererea pleaca spre furnizorul de email, ea nu ajunge la niciun om.
"""
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/costin/iconta_nou")
sys.path.insert(0, "/home/costin/iconta_nou/frontend_test")

from core import auth_api, db  # noqa: E402

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8010")
EMAIL = "patron@prisma-cont.test"


def _token(email):
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (email,))
            u = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, u[0])
        conn.rollback()
    return s["token"]


def cere(metoda, cale, corp, tok):
    req = urllib.request.Request(
        BAZA + cale, method=metoda,
        data=json.dumps(corp).encode() if corp is not None else None,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()[:600]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:600]


if __name__ == "__main__":
    tok = _token(EMAIL)
    for corp in ([{"emails": ["«»@#$%"]},
                  {"emails": ["fara-arond.ro"]},
                  {"emails": []}]):
        st, txt = cere("POST", "/recomanda", corp, tok)
        print("POST /recomanda %s" % json.dumps(corp, ensure_ascii=False))
        print("   -> %s %s" % (st, txt))
