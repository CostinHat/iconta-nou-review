# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 13 și clasa lui: formularele din ecranul Operațiuni.

    python frontend_test/proba_lot19_d13_formulare.py <radacina_cod>
F1 (tenant_049) din baza de producție, calea aplicației: use-case-urile rutelor (`uc_tenants.nota_credit`,
`nota_inventariere`, `achizitie_taxare_inversa`, `achizitie_agricultor`, `nota_subventie`, `nota_ong`), cu cererea
EXACT cum o trimite ecranul (selecturile ca text „true”/„false”; câmpurile pe care formularul vechi nu le avea lipsesc
pe codul vechi). `commit` neutralizat, ANAF simulat indisponibil (verdictul cade pe bifa), ROLLBACK la final.
"""
import contextlib
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, uc_tenants, uc_comun, anaf_api  # noqa: E402

observare.alerteaza = lambda *a, **k: None
anaf_api.platitor_tva_freeze = lambda cui, fallback=None, **k: fallback      # ANAF indisponibil -> fallback = bifa
NOU = hasattr(uc_comun, "bifa")
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
db.init_pool()
real = db.get_conn


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


D = "2026-09-30"
CERERI = [
    ("Credite › Garanție", "nota_credit",
     {"data": D, "operatie": "garantie", "tip": "lung"},
     {"data": D, "operatie": "garantie", "tip": "lung", "suma": 50000, "fel": "primita", "actiune": "inregistrare"}),
    ("Credite › Restanță", "nota_credit",
     {"data": D, "operatie": "restanta", "tip": "lung"},
     {"data": D, "operatie": "restanta", "tip": "lung", "suma": 2000}),
    ("Inventar › Minus, Imputabil: Nu", "nota_inventariere",
     {"data": D, "operatie": "minus", "valoare": 1000, "cont_stoc": "371", "imputabil": "false"},
     {"data": D, "operatie": "minus", "valoare": 1000, "cont_stoc": "371", "imputabil": "false", "cota": 21}),
    ("Leasing › Rată", "nota_leasing",
     {"data": D, "tip": "rata", "capital": 1000, "dobanda": 100},
     {"data": D, "tip": "rata", "capital": 1000, "dobanda": 100, "cota": 21}),
    ("Taxare inversă, furnizor plătitor: Nu", "achizitie_taxare_inversa",
     {"data": D, "furnizor_nume": "Furnizor Test", "furnizor_cui": "14399840", "numar": "F1", "categorie": "deseuri",
      "valoare": 10000, "cont_destinatie": "371", "cota": 21, "furnizor_platitor_tva": "false"}, None),
    ("Agricultor în registru: Nu", "achizitie_agricultor",
     {"data": D, "valoare": 5000, "cont_cheltuiala": "301", "agricultor_in_registru": "false"}, None),
    ("Taxare inversă, furnizor plătitor: Da", "achizitie_taxare_inversa",
     {"data": D, "furnizor_nume": "Furnizor Test", "furnizor_cui": "14399840", "numar": "F2", "categorie": "deseuri",
      "valoare": 10000, "cont_destinatie": "371", "cota": 21, "furnizor_platitor_tva": "true"}, None),
    ("Agricultor în registru: Da", "achizitie_agricultor",
     {"data": D, "valoare": 5000, "cont_cheltuiala": "301", "agricultor_in_registru": "true"}, None),
    ("Subvenții › Reluare", "nota_subventie",
     {"data": D, "fel": "reluare"},
     {"data": D, "fel": "reluare", "valoare_activ": 100000, "subventie": 60000, "amortizare_lunara": 1000}),
    ("ONG › Calcul scutire", "nota_ong",
     {"data": D, "operatie": "scutire"},
     {"data": D, "operatie": "scutire", "venituri_economice": 50000, "venituri_neimpozabile": 300000, "curs_eur": 5.0}),
]
with real() as conn:
    px = _Fara(conn)
    db.get_conn = contextlib.contextmanager(lambda *a, **k: (yield px))
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name='tenant_049'")
        tid, cab = cur.fetchone()
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}
        for eticheta, fn, vechi, nou in CERERI:
            corp = (nou or vechi) if NOU else vechi
            try:
                r = getattr(uc_tenants, fn)(tid, corp, ctx)
                if r.get("inregistrare_id"):
                    cur.execute("SELECT descriere FROM tenant_049.inregistrari WHERE id=%s", (r["inregistrare_id"],))
                    descr = cur.fetchone()[0]
                    cur.execute("SELECT cont_debit, cont_credit, suma::text FROM tenant_049.inregistrari_linii "
                                "WHERE inregistrare_id=%s ORDER BY id", (r["inregistrare_id"],))
                    print("  %-38s NOTĂ %s · «%s»" % (eticheta, [list(x) for x in cur.fetchall()], descr[:70]))
                else:
                    print("  %-38s CALCUL %s" % (eticheta, r))
            except Exception as e:
                print("  %-38s REFUZ: %s" % (eticheta, str(getattr(e, "mesaj", e))[:150]))
    finally:
        db.get_conn = real
        conn.rollback()
        print("  ROLLBACK — nimic scris")
