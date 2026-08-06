#!/usr/bin/env python3
"""Seed REPRODUCTIBIL (R2) — C-4 Tranșa 2: coerență + TVA.

Provizionează cabinet Prisma + cele 11 tenant-uri din C-2 (M1,M2,P1,P2,N1,S1,S2,S3,
NR1,T1,T2 — S4=tenant_001 e provizionat de tranșa 1) și populează tranzacțiile de
COERENȚĂ R3 (T-1…T-7): fiecare factură apare la EMITENT (directie='emisa') și la
PRIMITOR (directie='primita') cu numar/serie/dată/total/tva IDENTICE → D394
vânzări↔cumpărări + control încrucișat se verifică din DATE.

Rulare:  venv/bin/python3 date_test/seed/transa2_coerenta_tva.py [--only-provision]
Idempotent: re-rulabil (nu dublează firme, nu dublează facturi).

Parametri 2026 (C-1): cotă TVA standard 21% (Legea 141/2025 art.291, valabil 01.08.2025).
CUI-uri fictive verificate ANAF v9 05.08 (lot 95–96M, gasit=False) — C-2 secțiunea A.
"""
import sys
sys.path.insert(0, ".")
from core import db, auth_api, tenant_provisioning as tp

CAB_NUME = "Cabinet Contabil Prisma SRL"
CAB_EMAIL = "patron@prisma-cont.test"
CAB_PAROLA = "Prisma!patron2026"

# ---- FIRME (C-2 sect. B) : (cheie, nume, cui, caen, regim_fiscal, platitor_tva, tip_decont, operatiuni_ic) ----
# cui = 8 cifre fără prefix RO (DB stochează fără RO; RO e doar afișare pt plătitori). tip_decont: L=lunar T=trim.
FIRME = [
    ("M1",  "Coafor Micro Neplatitor SRL",     "95138914", "9602", "micro",  False, "T", False),
    ("M2",  "Comert Micro TVA SRL",            "95141537", "4711", "micro",  True,  "T", False),
    ("P1",  "Distributie Profit IC SRL",       "95275466", "4669", "profit", True,  "L", True),
    ("P2",  "Constructii Profit Trim SRL",     "95363126", "4321", "profit", True,  "T", False),
    ("N1",  "Achizitii IC Neplatitor SRL",     "95451848", "4791", "micro",  False, "T", True),
    ("S1",  "Agentie Turism Marja SRL",        "95687300", "7911", "profit", True,  "L", False),
    ("S2",  "Second Hand Marja SRL",           "95775518", "4779", "profit", True,  "L", False),
    ("S3",  "Ferma Agricultor Forfetar SRL",   "95873249", "0111", "micro",  False, "T", False),
    ("NR1", "IT Servicii Nerezidenti SRL",     "95904434", "6201", "profit", True,  "L", False),
    ("T1",  "Startup Partial 2026 SRL",        "96385785", "6201", "micro",  False, "T", False),
    ("T2",  "Trecere Micro Profit SRL",        "96516171", "4652", "micro",  True,  "T", False),
]
# S4 (tranșa 1) — deja provizionat ca tenant_001; îl folosim pt T-7.
S4_CUI = "96653616"

# ---- COERENȚA R3 (C-4 sect. C) : T-1…T-7 ----
# (cheie, emitent, primitor, data, net, tva, cota_tva_linie, taxare_inversa, categ_331, emitent_platitor, nota)
# net/tva/total IDENTICE pe ambele laturi. cota 21% pt standard; T-3 neplătitor (tva 0, cota 0);
# T-5 forfetar agricol (tva=forfait 8%, cota linie 0 — exceptia numită D394); T-6 taxare inversă (tva 0 pe factură).
TRANZACTII = [
    ("T1", "P1",  "M2", "2026-03-15", 50000, 10500, 21, False, None,          True,  "marfa; TVA lunar(P1) <-> trim(M2)"),
    ("T2", "P1",  "P2", "2026-04-10", 80000, 16800, 21, False, None,          True,  "marfa profit<->profit"),
    ("T3", "M1",  "P1", "2026-02-20",  8000,     0,  0, False, None,          False, "furnizor NEPLATITOR -> P1 fara drept deducere"),
    ("T4", "NR1", "P1", "2026-05-05", 30000,  6300, 21, False, None,          True,  "servicii IT intern"),
    ("T5", "S3",  "P1", "2026-06-12", 25000,  2000,  0, False, None,          False, "agricultor forfetar 8% (art.315^1); D394 achizitie de la agricultor"),
    ("T6", "P2",  "S1", "2026-07-08", 40000,     0, 21, True,  "constructii", True,  "taxare inversa (art.331); S1 autolichideaza"),
    ("T7", "P1",  "S4", "2026-03-20", 60000, 12600, 21, False, None,          True,  "materii prime/utilaje; S4 cumparator TVA deductibila"),
]
SERIE = "COER"


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


def ensure_tenant(conn, fid, uid, tpl, nume, cui, caen, regim, platitor, tip_decont, ic):
    """Idempotent: întoarce (schema, nou?). Setează firma_profil complet."""
    with conn.cursor() as c:
        c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s", (cui, fid))
        r = c.fetchone()
        if r:
            schema, nou = r[0], False
        else:
            res = tp.provision_tenant(conn, nume, cui, fid, uid, tpl)
            schema, nou = res["schema_name"], True
    with conn.cursor() as c:
        # profil complet: declarațiile TVA (D300/D394/D390) cer identificare + bancă/IBAN
        # (poarta D300 27.07 cere banca+IBAN) + declarant. Valori de test valide structural.
        c.execute(
            'UPDATE "%s".firma_profil SET nume=%%s, cui=%%s, caen=%%s, regim_fiscal=%%s, '
            'platitor_tva=%%s, tip_decont=%%s, operatiuni_ic=%%s, '
            'adresa=%%s, oras=%%s, judet=%%s, cod_postal=%%s, banca=%%s, iban=%%s, '
            'telefon=%%s, email=%%s, declarant_nume=%%s, declarant_prenume=%%s, declarant_functie=%%s '
            'WHERE id=1' % schema,
            (nume, cui, caen, regim, platitor, tip_decont, ic,
             "Str. Testului nr. 1", "Bucuresti", "București", "010101",
             "Banca Test", "RO49AAAA1B31007593840000", "0210000001", "firma@test.ro",
             "Dobrescu", "Elena", "ADMINISTRATOR"))
    return schema, nou


def _schema_for(conn, fid, cui):
    with conn.cursor() as c:
        c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s", (cui, fid))
        r = c.fetchone()
        return r[0] if r else None


def _factura_exista(conn, schema, numar, directie, data):
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".facturi WHERE numar=%%s AND directie=%%s AND data_emitere=%%s'
                  % schema, (numar, directie, data))
        return c.fetchone() is not None


def _insert_factura(conn, schema, *, numar, serie, data, directie, tert_cui, tert_nume,
                    net, tva, cota_linie, taxare_inversa, categ_331, tert_platitor):
    total = net + tva
    with conn.cursor() as c:
        c.execute(
            'INSERT INTO "%s".facturi (numar, serie, data_emitere, directie, tert_cui, tert_nume, '
            'total, tva, moneda, tip, taxare_inversa, categorie_331, tert_platitor_tva) '
            'VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
            (numar, serie, data, directie, tert_cui, tert_nume, total, tva, "RON", "factura",
             taxare_inversa, categ_331, tert_platitor))
        fid = c.fetchone()[0]
        c.execute(
            'INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) '
            'VALUES (%%s,%%s,%%s,%%s,%%s,%%s)' % schema,
            (fid, "coerenta R3", "buc", 1, net, cota_linie))
    return fid


def seed_coerenta(conn, fid, cuimap, numemap):
    """Inserează T-1…T-7 la ambele capete. Idempotent. Întoarce raport per tranzacție."""
    rap = []
    for (k, em, pr, data, net, tva, cota, ti, categ, em_plat, nota) in TRANZACTII:
        numar = "%s-%s" % (SERIE, k)
        em_cui, pr_cui = cuimap[em], cuimap[pr]
        em_nume, pr_nume = numemap[em], numemap[pr]
        em_schema, pr_schema = _schema_for(conn, fid, em_cui), _schema_for(conn, fid, pr_cui)
        assert em_schema and pr_schema, "schema lipsa pt %s (%s->%s)" % (k, em, pr)
        actiuni = []
        # latura EMITENT (vanzare / emisa)
        if not _factura_exista(conn, em_schema, numar, "emisa", data):
            _insert_factura(conn, em_schema, numar=numar, serie=SERIE, data=data, directie="emisa",
                            tert_cui=pr_cui, tert_nume=pr_nume, net=net, tva=tva, cota_linie=cota,
                            taxare_inversa=ti, categ_331=categ, tert_platitor=True)
            actiuni.append("emisa@%s" % em)
        # latura PRIMITOR (cumparare / primita)
        if not _factura_exista(conn, pr_schema, numar, "primita", data):
            _insert_factura(conn, pr_schema, numar=numar, serie=SERIE, data=data, directie="primita",
                            tert_cui=em_cui, tert_nume=em_nume, net=net, tva=tva, cota_linie=cota,
                            taxare_inversa=ti, categ_331=categ, tert_platitor=em_plat)
            actiuni.append("primita@%s" % pr)
        rap.append((k, "%s->%s" % (em, pr), net + tva, ", ".join(actiuni) or "deja prezent"))
    return rap


def main():
    _incarca_db_env()
    db.init_pool()
    tpl = open("tenant_template.sql", encoding="utf-8").read()
    with db.get_conn() as conn:
        fid, uid = ensure_cabinet(conn)
        print("cabinet firm_id=%d user_id=%d" % (fid, uid))
        cuimap = {"S4": S4_CUI}
        numemap = {"S4": "Panificatie Salarii Speciale SRL"}
        for (k, nume, cui, caen, regim, platitor, tipd, ic) in FIRME:
            schema, nou = ensure_tenant(conn, fid, uid, tpl, nume, cui, caen, regim, platitor, tipd, ic)
            cuimap[k], numemap[k] = cui, nume
            print("  %-3s cui=%s schema=%s (nou=%s) regim=%s tva=%s per=%s ic=%s"
                  % (k, cui, schema, nou, regim, platitor, tipd, ic))
        if "--only-provision" not in sys.argv:
            print("coerenta R3:")
            for (k, sens, total, act) in seed_coerenta(conn, fid, cuimap, numemap):
                print("  %-3s %-9s total=%-8d %s" % (k, sens, total, act))
        print("OK.")


if __name__ == "__main__":
    main()
