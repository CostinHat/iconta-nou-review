# -*- coding: utf-8 -*-
"""LOTUL 15 — starea care lipsea, construita PRIN LANTUL APLICATIEI (PLAN_LUCRU, regula 3).

DOUA ECRANE erau declarate „neprobate" nu fiindca n-ar avea formular, ci fiindca **datele
firmei nu-l produceau**:

  · `#fa-mijloace` (#446 / #484) — registrul mijloacelor fixe randeaza campul «valoare justă» si
    butoanele «Casează» / «Reevaluează» PE FIECARE RAND. Firma campaniei n-avea niciun activ, deci
    ecranul arata starea goala: zero campuri. *Punctul orb e FIRMA, nu ecranul.*
  · `admin_raportari` (#467) — formularul de raspuns se randeaza pe o sesizare EXISTENTA, iar lista
    era goala.

SCENARIUL, DECLARAT (ca sa se poata reface sau desface):
  · firma: «Comert Micro TVA» (`tenant_003`), cabinetul 1968;
  · mijlocul fix: cod `MF-PROBA-L15`, 1.200,00 lei, DNF 60 de luni, PIF in luna curenta, liniar,
    intrat prin «Plus la inventar mijloace fixe» — `POST /tenants/{}/nota-inventariere`, adica
    exact calea pe care o foloseste ecranul «Operatiuni speciale». Lasa in urma o NOTA CIORNA.
  · sesizarea: subiect `PROBA LOT 15`, deschisa de contul patronului de cabinet prin
    `POST /raportari` — calea ecranului «Raportează» (#490).

Nimic nu se scrie prin `INSERT`: daca o stare nu se poate produce prin lantul aplicatiei, ea nu e
o stare a aplicatiei. Desfacerea: `--sterge`.
"""
import datetime
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, "/home/costin/iconta_nou")

from core import auth_api, db  # noqa: E402

BAZA = os.environ.get("PROBA_BAZA", "http://127.0.0.1:8011")
EMAIL = "patron@prisma-cont.test"
FIRMA = "Comert Micro TVA SRL"   # numele DIN BAZA, nu cel din navigarea pe potrivire partiala
COD_MF = "MF-PROBA-L15"
SUBIECT = "PROBA LOT 15"


def _tok_si_tenant():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM public.users WHERE email=%s", (EMAIL,))
            uid = cur.fetchone()[0]
            cur.execute("SELECT id, schema_name FROM public.tenants WHERE nume=%s", (FIRMA,))
            tid, schema = cur.fetchone()
        s = auth_api.sesiune_pentru_user(conn, uid)
        conn.rollback()
    return s["token"], tid, schema


def cere(metoda, cale, corp, tok):
    req = urllib.request.Request(
        BAZA + cale, method=metoda,
        data=json.dumps(corp).encode() if corp is not None else None,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]


def construieste(tok, tid):
    azi = datetime.date.today()
    st, r = cere("POST", "/tenants/%d/nota-inventariere" % tid, {
        "operatie": "plus_mf",
        "data": azi.replace(day=1).isoformat(),
        "valoare": "1200.00",
        "dnf_luni": 60,
        "cod": COD_MF,
        "denumire": "Mijloc fix — fixtură lot 15",
        "cont_imobilizare": "2131",
        "metoda": "liniara",
    }, tok)
    print("mijloc fix -> %s %s" % (st, r))
    st, r = cere("POST", "/raportari", {"subiect": SUBIECT,
                                        "text": "Sesizare de probă pentru lotul 15 al campaniei. "
                                                "Se șterge la sfârșitul lotului."}, tok)
    print("sesizare   -> %s %s" % (st, r))


def sterge(schema):
    """Desfacerea, pe aceleasi obiecte, numite. Ce nu se poate desface se SPUNE, nu se trece."""
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM %s.mijloace_fixe WHERE cod=%%s" % schema, (COD_MF,))
        ids = [r[0] for r in cur.fetchall()]
        cur.execute("DELETE FROM %s.mijloace_fixe WHERE cod=%%s" % schema, (COD_MF,))
        n_mf = cur.rowcount
        cur.execute("SELECT id FROM %s.inregistrari WHERE descriere ILIKE %%s" % schema,
                    ("%Plus la inventar mijloace fixe%",))
        note = [r[0] for r in cur.fetchall()]
        cur.execute("DELETE FROM %s.linii WHERE inregistrare_id = ANY(%%s)" % schema, (note,))
        n_l = cur.rowcount
        cur.execute("DELETE FROM %s.inregistrari WHERE id = ANY(%%s)" % schema, (note,))
        n_n = cur.rowcount
        cur.execute("DELETE FROM public.raportari WHERE subiect=%s", (SUBIECT,))
        n_r = cur.rowcount
        conn.commit()
    print("sters: mijloace_fixe=%d %s · note=%d · linii=%d · raportari=%d"
          % (n_mf, ids, n_n, n_l, n_r))


if __name__ == "__main__":
    tok, tid, schema = _tok_si_tenant()
    print("firma %s -> tenant_id=%s schema=%s" % (FIRMA, tid, schema))
    if "--sterge" in sys.argv:
        sterge(schema)
    else:
        construieste(tok, tid)
