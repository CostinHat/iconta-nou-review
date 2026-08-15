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

# ---------------------------------------------------------------------------------------------
# [D300 remediere] Cazuri REALE pentru FIECARE situatie noua a decontului v12, pe FIRMA GREA.
# Firma e platitoare de la 01.05.2026 -> toate operatiunile TVA sunt >= mai. O luna curata per
# situatie, ca proba pe date reale sa fie neambigua. Coloane noi: data_faptului_generator,
# tert_tara (explicit, nu derivat din prefix), tip_operatiune, furnizor_tva_incasare.
#   (numar, data_emitere, data_fapt, directie, tert_cui, tert_nume, net, tva, cota,
#    tert_tara, tip_operatiune, furnizor_tva_incasare)
CAZURI_D300 = [
    # [sit.1] LIVRARE INTRACOMUNITARA de bunuri (partener UE FR, 0%, art.294 alin.2) -> rd.1 (R1_1).
    ("FG-ICL", "2026-08-12", None, "emisa", "FR40303265045", "Distributeur SARL",
     8000, 0, 0, "FR", "normal", False),
    # [sit.3] EXPORT non-UE (partener US, emisa 0%, scutit cu drept) -> rd.14 (R14_1).
    ("FG-EXP", "2026-09-10", None, "emisa", "US-880033", "Overseas Trading Inc",
     6000, 0, 0, "US", "normal", False),
    # [sit.4] AVANS incasat: emisa in IULIE, faptul generator abia in OCTOMBRIE -> exigibil la
    # EMITERE (art.282 alin.2 lit.b): apare in decontul lunii facturii (iulie, R9), NU reapare in
    # octombrie la faptul generator.
    ("FG-AV", "2026-07-05", "2026-10-15", "emisa", "95141537", "Comert Micro TVA SRL",
     1000, 210, 21, "RO", "avans", False),
    # [sit.5] REGULARIZARE AVANS: la livrarea din octombrie se emite factura finala (5000) cu
    # STORNAREA avansului deja facturat (-1000) -> rd.9 net 4000/840. Peste iulie (210) + octombrie
    # (840) = 1050 = 21% din livrarea totala de 5000 (coerent, fara dubla numarare).
    ("FG-REGAV", "2026-10-20", "2026-10-20", "emisa", "95141537", "Comert Micro TVA SRL",
     None, None, None, "RO", "regularizare_avans", False),
    # [sit.6] FURNIZOR LA INCASARE: primita in NOIEMBRIE de la furnizor care aplica TVA la incasare
    # -> deducerea se AMANA pana la PLATA (art.297 alin.2), chiar daca firma proprie e in regim
    # normal. Nu apare in decontul lunii facturii (noiembrie); apare cand se plateste (decembrie).
    ("FG-FTI", "2026-11-08", None, "primita", "95363126", "Constructii Profit Trim SRL",
     2000, 420, 21, "RO", "normal", True),
]
# Linii MULTIPLE pentru facturile de regularizare (net = livrare - avans stornat). Cheie = numar.
# Fiecare linie: (descriere, um, cantitate, pret_unitar, cota_tva).
LINII_MULTI = {
    "FG-REGAV": [
        ("livrare finala bunuri", "buc", 1, 5000, 21),    # livrarea la faptul generator
        ("storno avans facturat", "buc", 1, -1000, 21),   # regularizare: storneaza avansul din iulie
    ],
}
# [sit.6] plata facturii FG-FTI (401=5121) validata in DECEMBRIE -> deducerea devine exigibila pe
# calea de plata (decembrie): (numar, data_plata, suma).
PLATA_FTI = ("FG-FTI", "2026-12-15", 2420)
# [sit.7] rand MANUAL D300 pe tenant_017: R16 (Regularizari taxa colectata) pe MAI 2026 (luna cu
# livrare interna R9). Rand ne-derivabil din facturi -> componenta manuala reala a decontului.
#   (perioada "AAAA-LL", rand, baza, tva, descriere)
MANUAL_D300 = ("2026-05", "R16", 1000, 210, "[SEED-FG] regularizare taxa colectata")
# [sit.2] achizitie IC (FG-ICB, iunie) si [sit.8] zero-base (FEBRUARIE, fara nicio factura) sunt deja
# acoperite de FACTURI / de lunile goale de mai sus.

# [F125 servicii IC reclasificate] Prestare + achizitie IC de SERVICII pe firma grea (IULIE 2026),
# reclasificate P/S in d390_reclasificare (SURSA UNICA D300<->D390: bun-vs-serviciu = proprietate a
# operatiunii, contabilul reclasifica O DATA din panoul D390, ambele declaratii CITESC). Astfel firma
# grea acopera si calea SERVICII, consistent: D300 rd.3 (P) / rd.7+rd.20 (S, autolichidare 21%, net
# zero), D390 bazaP/bazaS. 0% (taxare la beneficiar, art.294/331). Iulie e curata de alte operatiuni IC
# (are doar avansul RO FG-AV -> rd.9), deci R3/R7/R20 vs P/S se probeaza 1:1. Partenerii au checksum VIES
# verificat pe DUK (FR40303265045, DE136695976). cod = fara prefix de tara (cheia reclasificarii).
#   (numar, data_emitere, directie, tert_cui, tert_nume, net, tara, cod_fara_prefix, tip)
SERVICII_IC = [
    ("FG-SRVP", "2026-07-15", "emisa",   "FR40303265045", "Distributeur SARL",
     5000, "FR", "40303265045", "P"),   # prestare servicii IC (emisa) -> rd.3 (R3_1) + rd.3.1
    ("FG-SRVS", "2026-07-18", "primita", "DE136695976",   "BAUHAUS GMBH",
     7000, "DE", "136695976", "S"),     # achizitie servicii IC (primita) -> rd.7 colectat + rd.20 oglinda
]


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


def seed_cazuri_d300(conn, schema):
    """[D300 remediere] Facturi cu coloanele noi (data_faptului_generator, tert_tara explicit,
    tip_operatiune, furnizor_tva_incasare) + linii multiple pentru regularizari. Idempotent."""
    rap = []
    for (numar, data, fapt, directie, tcui, tnume, net, tva, cota,
         tara, tipop, fti) in CAZURI_D300:
        if _factura_exista(conn, schema, numar, directie):
            rap.append((numar, "deja prezent")); continue
        linii = LINII_MULTI.get(numar)
        if linii is not None:
            # net/tva din suma liniilor (respecta storno negativ)
            net_tot = sum(cant * pret for (_d, _u, cant, pret, _c) in linii)
            tva_tot = sum(round(cant * pret * cta / 100) for (_d, _u, cant, pret, cta) in linii)
        else:
            net_tot, tva_tot = net, tva
            linii = [("seed firma grea D300", "buc", 1, net, cota)]
        total = net_tot + tva_tot
        with conn.cursor() as c:
            c.execute(
                'INSERT INTO "%s".facturi (numar, serie, data_emitere, data_faptului_generator, '
                'directie, tert_cui, tert_nume, total, tva, moneda, tip, tert_tara, tip_operatiune, '
                'furnizor_tva_incasare, tert_platitor_tva) '
                'VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                (numar, "FG", data, fapt, directie, tcui, tnume, total, tva_tot, "RON", "factura",
                 tara, tipop, fti, True))
            fid = c.fetchone()[0]
            for (descr, um, cant, pret, cta) in linii:
                c.execute(
                    'INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) '
                    'VALUES (%%s,%%s,%%s,%%s,%%s,%%s)' % schema,
                    (fid, descr, um, cant, pret, cta))
        rap.append((numar, "inserata id=%d (net=%d tva=%d)" % (fid, net_tot, tva_tot)))
    return rap


def seed_plata_fti(conn, schema):
    """[sit.6] plata FG-FTI (401=5121) validata in decembrie -> exigibilitate deducere pe plata."""
    numar, data_p, suma = PLATA_FTI
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".facturi WHERE numar=%%s AND directie=%%s' % schema,
                  (numar, "primita"))
        r = c.fetchone()
        fid = r[0] if r else None
    if not fid:
        return (numar, "factura primita lipsa - plata nu se poate atasa")
    with conn.cursor() as c:
        c.execute('SELECT id FROM "%s".inregistrari WHERE factura_id=%%s AND data=%%s AND status=%%s'
                  % schema, (fid, data_p, "validata"))
        if c.fetchone():
            return ("plata %s" % numar, "deja prezent")
        c.execute('INSERT INTO "%s".inregistrari (data, descriere, factura_id, sursa, status) '
                  'VALUES (%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                  (data_p, "[SEED-FG] plata furnizor la incasare", fid, "banca", "validata"))
        nid = c.fetchone()[0]
        c.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) '
                  'VALUES (%%s,%%s,%%s,%%s)' % schema, (nid, "401", "5121", suma))
    return ("plata %s" % numar, "inserata nota id=%d (401=5121 %d lei)" % (nid, suma))


def seed_servicii_ic(conn, schema):
    """[F125] Prestare/achizitie IC de SERVICII (0%) + reclasificarea lor P/S in d390_reclasificare
    (SURSA UNICA D300<->D390). Idempotent: factura pe (numar,directie) -> skip daca exista; reclasificarea
    prin salveaza_reclasificare (upsert ON CONFLICT, valideaza tip contra directiei). tert_tara = prefixul
    VIES; luna reclasificarii = luna de exigibilitate (data_emitere)."""
    from core import d390_clasificare_api as _cls
    rap = []
    for (numar, data, directie, tcui, tnume, net, tara, cod, tip) in SERVICII_IC:
        an, luna = (int(x) for x in data.split("-")[:2])
        if _factura_exista(conn, schema, numar, directie):
            rap.append((numar, "deja prezent"))
        else:
            with conn.cursor() as c:
                c.execute(
                    'INSERT INTO "%s".facturi (numar, serie, data_emitere, directie, tert_cui, tert_nume, '
                    'total, tva, moneda, tip, tert_platitor_tva, tert_tara) '
                    'VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id' % schema,
                    (numar, "FG", data, directie, tcui, tnume, net, 0, "RON", "factura", True, tara))
                fid = c.fetchone()[0]
                c.execute(
                    'INSERT INTO "%s".factura_linii (factura_id, descriere, um, cantitate, pret_unitar, cota_tva) '
                    'VALUES (%%s,%%s,%%s,%%s,%%s,%%s)' % schema,
                    (fid, "servicii IC (%s)" % tip, "buc", 1, net, 0))
            rap.append((numar, "inserata id=%d (net=%d, tip=%s)" % (fid, net, tip)))
        # reclasificarea in SURSA UNICA (idempotent prin upsert; salveaza_reclasificare face commit)
        res = _cls.salveaza_reclasificare(conn, schema, an, luna, directie, tara, cod, tip)
        rap.append(("%s recl" % numar, "%s %s %s%s -> %s -> %s"
                    % (data[:7], directie, tara, cod, tip, "OK" if res.get("ok") else res)))
    return rap


def seed_manual_d300(schema):
    """[sit.7] rand MANUAL D300 (d300_manual) via API - validare + upsert idempotent pe UNIQUE.
    API-ul (d300_manual_api / d300.pull) foloseste nume de tabel NEcalificate -> cere search_path pe
    schema tenantului; deschidem o conexiune dedicata schema-scoped (SET LOCAL + RESET la iesire)."""
    from core import d300_manual_api as _dm
    per, rand, baza, tva, descr = MANUAL_D300
    an, luna = (int(x) for x in per.split("-"))
    with db.get_conn(schema) as conn2:
        res = _dm.adauga(conn2, schema, an, luna,
                         {"rand": rand, "baza": baza, "tva": tva, "descriere": descr})
    if res.get("ok"):
        return ("%s %s" % (per, rand), "id=%d baza=%d tva=%d" % (res["id"], res["baza"], res["tva"]))
    return ("%s %s" % (per, rand), "EROARE: %s" % res.get("eroare"))


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
        print("cazuri D300:")
        for (n, act) in seed_cazuri_d300(conn, schema):
            print("   %-10s %s" % (n, act))
        print("   %-10s %s" % seed_plata_fti(conn, schema))
        print("servicii IC (F125 reclasificare P/S, sursa unica D390):")
        for (n, act) in seed_servicii_ic(conn, schema):
            print("   %-14s %s" % (n, act))
        conn.commit()   # persista facturile/plata inainte de pasul manual (conexiune separata)
    print("   %-10s %s" % seed_manual_d300(schema))
    print("OK. schema=%s" % schema)


if __name__ == "__main__":
    main()
