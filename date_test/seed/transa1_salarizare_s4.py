#!/usr/bin/env python3
"""Seed REPRODUCTIBIL (R2) — C-4 Tranșa 1: salarizare S4.

Provizionează cabinet Prisma + tenant S4 (idempotent) și populează salariați cu
situații speciale de salarizare (CM pe coduri, tichete, facilitate, part-time,
luni parțiale, multi-certificat CM). D112 se generează + validează DUK separat.

Rulare:  venv/bin/python3 date_test/seed/transa1_salarizare_s4.py [--only-provision]
Idempotent: re-rulabil pe DB curată SAU deja populată (nu dublează).

Parametri 2026 (C-1): salariu minim 4.050 (ian–iun) / 4.325 (iul–dec);
facilitate min 300 (H1) / 200 (H2); floor part-time = sm − facilitate = 3.750 (H1).
"""
import sys
sys.path.insert(0, ".")
from core import db, auth_api, tenant_provisioning as tp

CAB_NUME = "Cabinet Contabil Prisma SRL"
CAB_EMAIL = "patron@prisma-cont.test"
CAB_PAROLA = "Prisma!patron2026"
S4_NUME = "Panificatie Salarii Speciale SRL"   # S4
S4_CUI = "96653616"      # fictiv, verificat ANAF v9 05.08 (gasit=False)
S4_CAEN = "1071"

# ---- CNP fictiv valid (cheie oficiala 279146358279); jud 51 (Calarasi); fara rezonanta ----
_K = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
def _cnp(sx, yy, mm, dd, nnn, jud=51):
    b = "%d%02d%02d%02d%02d%03d" % (sx, yy, mm, dd, jud, nnn)
    s = sum(int(b[i]) * _K[i] for i in range(12))
    c = s % 11
    return b + str(1 if c == 10 else c)

# salariat: (cheie, nume, prenume, sex, an_n, luna_n, zi_n, seq, brut, ore_zi, part_time, data_ang, data_inc)
# brut = salariul CONTRACTUAL curent (dec 2026). salariu_istoric adauga treptele.
SALARIATI = [
    # E1 minim EXACT (4050 H1 -> 4325 H2), facilitate ambele semestre  [L5 exact, L6]
    ("E1", "MINIM", "EXACT", 2, 88, 3, 12, 101, 4325, 8, False, "2026-01-01", None),
    # E2 minim +1 (4051 H1 -> 4326 H2), NU primeste facilitate  [L5 prag+1]
    ("E2", "MINIM", "PESTEUNU", 1, 90, 5, 7, 102, 4326, 8, False, "2026-01-01", None),
    # E3 peste minim, an intreg, simplu (baseline)  brut 5500
    ("E3", "PESTE", "MINIM", 2, 91, 7, 3, 103, 5500, 8, False, "2026-01-01", None),
    # NOTA: cazul prag-1 (sub minim full-time) = DATE DEFECTE (C-5) - aplicatia il blocheaza corect.
    # E4 part-time sub floor -> suprataxare baza minima CASS (brut 3000 < 3750)  [L9]
    ("E4", "PARTTIME", "SUBFLOOR", 1, 89, 2, 20, 104, 3000, 4, True, "2026-01-01", None),
    # E5 peste minim + CM cod 01 (progresiv 55/65/75)  brut 6000
    ("E5", "CM", "COD01", 2, 85, 9, 9, 105, 6000, 8, False, "2026-01-01", None),
    # E6 CM cod 07 (carantina 100%) + cod 08 (maternitate, CASS-scutit)  brut 5000
    ("E6", "CM", "COD0708", 2, 92, 4, 4, 106, 5000, 8, False, "2026-01-01", None),
    # E7 CM cod 09 (ingrijire copil, cnp_ingrijit) + cod 17 (cardiovascular 75%, cnp_ingrijit)  brut 9000
    ("E7", "CM", "COD0917", 1, 87, 11, 11, 107, 9000, 8, False, "2026-01-01", None),
    # E8 CM cod 91/92 (accident munca, cnp_ingrijit) + cod 15  brut 7000
    ("E8", "CM", "COD9192", 1, 86, 6, 6, 108, 7000, 8, False, "2026-01-01", None),
    # E9 multi-certificat CM aceeasi luna (2x cod 01 in iulie)  brut 6500  [L14]
    ("E9", "CM", "MULTICERT", 2, 84, 1, 15, 109, 6500, 8, False, "2026-01-01", None),
    # E10 tichete (masa permanent + vacanta/cultural/cresa) + angajare la mijloc de luna (15.03)  [L11, tichete, L8]
    ("E10", "TICHETE", "PARTIALA", 2, 93, 8, 8, 110, 4800, 8, False, "2026-03-15", None),
    # E11 plafon 12 SM: brut mare + CM  [L7]
    ("E11", "PLAFON", "12SM", 1, 80, 10, 10, 111, 60000, 8, False, "2026-01-01", None),
    # E12 CM cod 10 (risc maternal, formula speciala)  brut 5500
    ("E12", "CM", "COD10", 2, 90, 12, 1, 112, 5500, 8, False, "2026-01-01", None),
]

# istoric salariu: (cheie, [(valabil_din, brut), ...]) — treapta SM la 01.07 pt cei la minim
ISTORIC = {
    "E1": [("2026-01-01", 4050), ("2026-07-01", 4325)],
    "E2": [("2026-01-01", 4051), ("2026-07-01", 4326)],
    "E4": [("2026-01-01", 3000)],
    "E10": [("2026-03-15", 4800)],
}

# concedii_medicale: (cheie, an, luna, cod, zile, zile_ang, zile_fnuass, brut_ang, brut_fnuass, baza, media, cnp_ingrijit?)
CONCEDII = [
    ("E5", 2026, 6, "01", 10, 5, 5, 1300, 1300, 6000, 286, None),       # progresiv
    ("E6", 2026, 5, "08", 15, 0, 15, 0, 3600, 5000, 238, None),         # maternitate CASS-scutit
    ("E6", 2026, 8, "07", 8, 0, 8, 0, 1600, 5000, 238, None),           # carantina 100%; FNUASS-only (prevenire imbolnavire)
    ("E7", 2026, 6, "09", 5, 0, 5, 0, 3000, 9000, 600, "ING09"),        # ingrijire copil (cnp_ingrijit); FNUASS-only
    ("E7", 2026, 9, "17", 12, 0, 12, 0, 3600, 9000, 429, "ING17"),      # cardiovascular 75% (cnp_ingrijit); FNUASS-only (zile_ang=0)
    ("E8", 2026, 4, "91", 6, 0, 6, 0, 1400, 7000, 333, "ING91"),        # accident munca (cnp_ingrijit); FNUASS-only
    ("E8", 2026, 7, "15", 10, 0, 10, 0, 3300, 7000, 333, None),         # neoplazii 100%; FNUASS-only (zile_ang=0)
    ("E9", 2026, 7, "01", 4, 4, 0, 900, 0, 6500, 310, None),            # multi-cert #1
    ("E9", 2026, 7, "01", 5, 1, 4, 200, 800, 6500, 310, None),          # multi-cert #2 (aceeasi luna)
    ("E11", 2026, 6, "01", 7, 5, 2, 5000, 2000, 60000, 2857, None),     # plafon 12 SM + CM
    ("E12", 2026, 10, "10", 20, 0, 20, 0, 3600, 5500, 262, None),       # risc maternal (formula speciala)
]

# beneficii_lunare: (cheie, an, luna, tip, valoare, eveniment)
BENEFICII = [
    ("E10", 2026, 6, "vacanta", 30000, ""),      # exces peste 6 SM -> intra in baza  [L8]
    ("E10", 2026, 12, "cadou", 300, "craciun"),
    ("E10", 2026, 5, "cultural", 200, ""),
    ("E10", 2026, 9, "cresa", 700, ""),
]

# tichet masa permanent (valoare nominala/zi) — cere pontaj confirmat
TICHET_MASA = {"E10": 40}

# confirmare pontaj pt TOATE lunile (tichetele cer pontaj confirmat oriunde e prezent salariatul)
TICHET_LUNI = [(2026, m) for m in range(1, 13)]


def _cnp_ingrijit(tok):
    return {
        "ING09": _cnp(6, 18, 4, 3, 201),   # copil nascut 2018
        "ING17": _cnp(6, 15, 7, 9, 202),
        "ING91": _cnp(6, 20, 1, 5, 203),
    }.get(tok)


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
        c.execute("SELECT schema_name FROM public.tenants WHERE cui=%s AND accounting_firm_id=%s", (S4_CUI, fid))
        r = c.fetchone()
        if r:
            return r[0], False
    res = tp.provision_tenant(conn, S4_NUME, S4_CUI, fid, uid, tpl)
    schema = res["schema_name"]
    with conn.cursor() as c:
        c.execute('UPDATE "%s".firma_profil SET caen=%%s, nume=%%s, cui=%%s WHERE id=1' % schema,
                  (S4_CAEN, S4_NUME, S4_CUI))
    return schema, True


def seed_payroll(conn, schema):
    q = ('INSERT INTO "%s".' % schema)
    with conn.cursor() as c:
        c.execute('SELECT count(*) FROM "%s".salariati' % schema)
        if c.fetchone()[0] > 0:
            return "deja populat"
        idmap = {}
        for (k, nume, pren, sx, yy, mm, dd, seq, brut, orez, pt, dang, dinc) in SALARIATI:
            cnp = _cnp(sx, yy, mm, dd, seq)
            c.execute(q + "salariati (nume,prenume,cnp,data_angajare,data_incetare,salariu_brut,ore_zi,part_time) "
                      "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                      (nume, pren, cnp, dang, dinc, brut, orez, pt))
            idmap[k] = c.fetchone()[0]
        for k, trepte in ISTORIC.items():
            for (vd, br) in trepte:
                c.execute(q + "salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (%s,%s,%s)",
                          (idmap[k], vd, br))
        for k, val in TICHET_MASA.items():
            c.execute('UPDATE "%s".salariati SET tichet_masa_valoare=%%s WHERE id=%%s' % schema, (val, idmap[k]))
        nr = 0
        for (k, an, lu, cod, zi, za, zf, ba, bf, baza, med, ing) in CONCEDII:
            nr += 1
            cnpi = _cnp_ingrijit(ing) if ing else None
            urg = 55501 if cod == "10" else None   # cod 10: nr aviz medic expert (D_13)
            c.execute(q + "concedii_medicale (salariat_id,an,luna,cod,zile,zile_ang,zile_fnuass,brut_ang,"
                      "brut_fnuass,baza,media_zilnica,serie,numar,data_acordare,data_inceput,data_sfarsit,"
                      "loc_prescriere,cnp_ingrijit,cod_urgenta) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s,%s)",
                      (idmap[k], an, lu, cod, zi, za, zf, ba, bf, baza, med, "AB", str(nr),
                       "%04d-%02d-01" % (an, lu), "%04d-%02d-01" % (an, lu), "%04d-%02d-%02d" % (an, lu, min(zi, 28)), cnpi, urg))
        for (k, an, lu, tip, val, ev) in BENEFICII:
            c.execute(q + "beneficii_lunare (salariat_id,an,luna,tip,valoare,eveniment) VALUES (%s,%s,%s,%s,%s,%s)",
                      (idmap[k], an, lu, tip, val, ev))
        # confirmare pontaj pt lunile cu tichet masa (E10)
        for (an, lu) in TICHET_LUNI:
            c.execute(q + "perioada_confirmata (an,luna,domeniu,confirmat_de,confirmat_la) "
                      "VALUES (%s,%s,'pontaj',1,now()) ON CONFLICT DO NOTHING", (an, lu))
    return "populat %d salariati" % len(SALARIATI)


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


def main():
    _incarca_db_env()
    db.init_pool()
    tpl = open("tenant_template.sql", encoding="utf-8").read()
    with db.get_conn() as conn:
        fid, uid = ensure_cabinet(conn)
        schema, nou = ensure_tenant(conn, fid, uid, tpl)
        print("cabinet firm_id=%d user_id=%d ; tenant=%s (nou=%s)" % (fid, uid, schema, nou))
        if "--only-provision" not in sys.argv:
            print("payroll:", seed_payroll(conn, schema))
        print("OK. schema=%s" % schema)


if __name__ == "__main__":
    main()
