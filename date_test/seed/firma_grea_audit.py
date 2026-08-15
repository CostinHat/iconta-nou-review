#!/usr/bin/env python3
"""Seed FIRMA GREA (audit restante) - un singur an fiscal 2026, TOATE cazurile grele
intr-o firma, ca sa prinda restantele nesustinute (snapshot-vector aplicat la toate lunile).

Cazuri acoperite:
  - salariat INTRAT la mijloc de luna (data_angajare 2026-03-15)      -> G_IN
  - salariat IESIT la mijloc de luna (data_incetare 2026-06-15)       -> G_OUT
  - o luna INTREAGA fara niciun salariat (ianuarie 2026)              -> ambii incep >= feb
  - concediu medical care TRAVERSEAZA granita de luna (28.04->05.05)  -> pe G_IN, 2 randuri (apr+mai)
  - trecere la PLATITOR de TVA in cursul anului (01.05.2026)          -> platitor_tva=True + tva_anaf_inceput
  - o luna fara nicio FACTURA vs luni cu facturi                      -> facturi doar mar/mai/iun

Rulare:  venv/bin/python3 date_test/seed/firma_grea_audit.py
Idempotent: nu dubleaza firma, salariati, CM sau facturi.
"""
import sys, datetime
sys.path.insert(0, ".")
from core import db, auth_api, tenant_provisioning as tp

CAB_NUME = "Cabinet Contabil Prisma SRL"
CAB_EMAIL = "patron@prisma-cont.test"
CAB_PAROLA = "Prisma!patron2026"

FG_NUME = "Firma Grea Audit SRL"
FG_CUI  = "98765438"          # fictiv, lot nefolosit in setul de test
FG_CAEN = "4711"
FG_REGIM = "micro"            # micro -> D100 trimestrial (prinde restanta anuala/existenta)
FG_TVA = True                 # devine platitor pe parcurs
FG_DECONT = "L"              # lunar -> D300/D394/D406 pe luni (granular)
FG_IC = True                 # operatiuni IC (D390 pe fapt)
FG_TVA_INCEPUT = "2026-05-01"  # inregistrare TVA in cursul anului

# CNP fictiv valid
_K = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
def _cnp(sx, yy, mm, dd, nnn, jud=51):
    b = "%d%02d%02d%02d%02d%03d" % (sx, yy, mm, dd, jud, nnn)
    s = sum(int(b[i]) * _K[i] for i in range(12))
    c = s % 11
    return b + str(1 if c == 10 else c)

# (cheie, nume, prenume, sex, an, luna, zi, seq, brut, cor, ore, data_ang, data_inc)
SALARIATI = [
    # G_IN: intrat la mijloc de luna (15.03); ramane pana la final de an
    ("G_IN",  "INTRAT",  "MIJLOC", 1, 90, 3, 15, 301, 5000, "512001", 8, "2026-03-15", None),
    # G_OUT: activ din feb, IESIT la mijloc de luna (15.06)
    ("G_OUT", "IESIT",   "MIJLOC", 2, 88, 6, 15, 302, 4500, "522101", 8, "2026-02-01", "2026-06-15"),
]
# NB: nimeni activ in IANUARIE 2026 (ambii incep >= 01.02) -> luna intreaga fara salariat.

# concediu medical care traverseaza granita apr->mai, pe G_IN. 2 randuri (portiunea din fiecare luna).
CM = [
    # (cheie, an, luna, cod, zile, data_inceput, data_sfarsit, serie, numar)
    ("G_IN", 2026, 4, "01", 3, "2026-04-28", "2026-04-30", "CMG", "1"),   # portiunea din aprilie
    ("G_IN", 2026, 5, "01", 5, "2026-05-01", "2026-05-05", "CMG", "1"),   # continuare in mai (acelasi certificat)
]

# facturi: (numar, data, directie, tert_cui, tert_nume, net, tva, cota) ; unele luni raman FARA factura
FACTURI = [
    # martie: firma inca neplatitoare -> factura emisa fara TVA (cota 0)
    ("FG-MAR-1", "2026-03-10", "emisa",   "95141537", "Comert Micro TVA SRL", 12000,    0,  0),
    # mai: platitoare (de la 01.05) -> emisa cu TVA 21%
    ("FG-MAI-1", "2026-05-12", "emisa",   "95275466", "Distributie Profit IC SRL", 20000, 4200, 21),
    # iunie: achizitie INTRACOMUNITARA (furnizor DE) -> D390 pe fapt = True in iunie
    ("FG-ICB",   "2026-06-08", "primita", "DE136695976", "BAUHAUS GMBH", 15000, 0, 0),
]
# aprilie, februarie, iulie..dec: FARA factura (contrast luni cu/ fara facturi)


def _incarca_db_env():
    import os
    cale = os.path.expanduser("~/.iconta/db.env")
    if not os.path.exists(cale):
        return
    for linie in open(cale, encoding="utf-8"):
        linie = linie.strip()
        if linie and not linie.startswith("#") and "=" in linie:
            k, v = linie.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def ensure_cabinet(conn):
    with conn.cursor() as c:
        c.execute("SELECT id FROM public.accounting_firms WHERE nume=%s", (CAB_NUME,))
        r = c.fetchone()
        if r:
            fid = r[0]
            c.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s AND rol='admin_firma' ORDER BY id LIMIT 1", (fid,))
            return fid, c.fetchone()[0]
    res = auth_api.inregistreaza_cabinet(conn, CAB_EMAIL, CAB_PAROLA, CAB_NUME, "Dobrescu", "Elena")
    assert res.get("ok"), res
    return res["firm_id"], res["user_id"]


def ensure_tenant(conn, fid, uid, tpl):
    with conn.cursor() as c:
        c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s", (FG_CUI, fid))
        r = c.fetchone()
        if r:
            schema, nou = r[0], False
        else:
            res = tp.provision_tenant(conn, FG_NUME, FG_CUI, fid, uid, tpl)
            schema, nou = res["schema_name"], True
    with conn.cursor() as c:
        c.execute(
            'UPDATE "%s".firma_profil SET nume=%%s, cui=%%s, caen=%%s, regim_fiscal=%%s, '
            'platitor_tva=%%s, tip_decont=%%s, operatiuni_ic=%%s, platitor_tva_anaf_inceput=%%s, '
            'adresa=%%s, oras=%%s, judet=%%s, cod_postal=%%s, banca=%%s, iban=%%s, '
            'telefon=%%s, email=%%s, declarant_nume=%%s, declarant_prenume=%%s, declarant_functie=%%s '
            'WHERE id=1' % schema,
            (FG_NUME, FG_CUI, FG_CAEN, FG_REGIM, FG_TVA, FG_DECONT, FG_IC, FG_TVA_INCEPUT,
             "Str. Grea nr. 1", "Bucuresti", "Bucuresti", "010101",
             "Banca Test", "RO49AAAA1B31007593840000", "0210000009", "grea@test.ro",
             "Dobrescu", "Elena", "ADMINISTRATOR"))
    return schema, nou


def seed_payroll(conn, schema):
    q = 'INSERT INTO "%s".' % schema
    with conn.cursor() as c:
        c.execute('SELECT count(*) FROM "%s".salariati' % schema)
        already = c.fetchone()[0] > 0
        idmap = {}
        if not already:
            for (k, nume, pren, sx, yy, mm, dd, seq, brut, cor, orez, dang, dinc) in SALARIATI:
                cnp = _cnp(sx, yy, mm, dd, seq)
                c.execute(q + "salariati (nume,prenume,cnp,data_angajare,data_incetare,salariu_brut,cor,ore_zi) "
                          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                          (nume, pren, cnp, dang, dinc, brut, cor, orez))
                idmap[k] = c.fetchone()[0]
            nr = 0
            for (k, an, lu, cod, zi, di, ds, serie, numar) in CM:
                nr += 1
                c.execute(q + "concedii_medicale (salariat_id,an,luna,cod,zile,data_inceput,data_sfarsit,serie,numar,data_acordare) "
                          "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                          (idmap[k], an, lu, cod, zi, di, ds, serie, numar, di))
            return "populat %d salariati + %d randuri CM" % (len(SALARIATI), len(CM))
        return "deja populat"


def _factura_exista(conn, schema, numar, directie):
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".facturi WHERE numar=%%s AND directie=%%s' % schema, (numar, directie))
        return c.fetchone() is not None


def seed_facturi(conn, schema):
    rap = []
    for (numar, data, directie, tcui, tnume, net, tva, cota) in FACTURI:
        if _factura_exista(conn, schema, numar, directie):
            rap.append((numar, "deja prezent")); continue
        total = net + tva
        import re as _re
        tert_tara = (tcui or "")[:2].upper() if _re.match(r"^[A-Za-z]{2}", tcui or "") else "RO"  # [B1] prefix VIES = tara
        with conn.cursor() as c:
            c.execute(
                'INSERT INTO "%s".facturi (numar, serie, data_emitere, directie, tert_cui, tert_nume, '
                'total, tva, moneda, tip, tert_platitor_tva, tert_tara) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                (numar, "FG", data, directie, tcui, tnume, total, tva, "RON", "factura", True, tert_tara))
            fid = c.fetchone()[0]
            c.execute(
                'INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) '
                'VALUES (%%s,%%s,%%s,%%s,%%s,%%s)' % schema,
                (fid, "seed firma grea", "buc", 1, net, cota))
        rap.append((numar, "inserata"))
    return rap


def main():
    _incarca_db_env()
    db.init_pool()
    tpl = open("tenant_template.sql", encoding="utf-8").read()
    with db.get_conn() as conn:
        fid, uid = ensure_cabinet(conn)
        schema, nou = ensure_tenant(conn, fid, uid, tpl)
        print("cabinet firm_id=%d user_id=%d ; firma_grea schema=%s (nou=%s) cui=%s" % (fid, uid, schema, nou, FG_CUI))
        print("payroll:", seed_payroll(conn, schema))
        print("facturi:")
        for (n, act) in seed_facturi(conn, schema):
            print("   %-10s %s" % (n, act))
        print("OK. schema=%s" % schema)


if __name__ == "__main__":
    main()
