#!/usr/bin/env python3
"""AUDIT restante NESUSTINUTE pe toata baza de test.
Ruleaza motorul (control_fiscal_api.evalueaza_firma) pe FIECARE tenant, colecteaza toate
verdictele de RESTANTA (lipsa) si stabileste per verdict daca are PREMISA DEMONSTRABILA din date.
NU modifica motorul, NU comite. cu_reconciliere=False (pur read, focus pe lipsa).
"""
import os, sys, datetime, calendar, collections
sys.path.insert(0, ".")

def _load():
    cale = os.path.expanduser("~/.iconta/db.env")
    for l in open(cale, encoding="utf-8"):
        l = l.strip()
        if l and not l.startswith("#") and "=" in l:
            k, v = l.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load()

from core import db, control_fiscal_api as cf, control_incrucisat as ci, d390, scadente
db.init_pool()

AZI = datetime.date(2026, 8, 15)

def _ultima_zi(an, luna):
    return datetime.date(an, luna, calendar.monthrange(an, luna)[1])

def existenta_an(conn, schema, Y):
    with conn.cursor() as c:
        c.execute("SELECT to_regclass(%s)", (schema + ".facturi",))
        if c.fetchone()[0]:
            c.execute('SELECT 1 FROM "%s".facturi WHERE EXTRACT(year FROM data_emitere)=%%s LIMIT 1' % schema, (Y,))
            if c.fetchone(): return True
        c.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
        if c.fetchone()[0]:
            c.execute('SELECT 1 FROM "%s".salariati WHERE (data_angajare IS NULL OR data_angajare<=%%s) '
                      'AND (data_incetare IS NULL OR data_incetare>=%%s) LIMIT 1' % schema,
                      ("%d-12-31" % Y, "%d-01-01" % Y))
            if c.fetchone(): return True
        c.execute("SELECT to_regclass(%s)", (schema + ".inregistrari",))
        if c.fetchone()[0]:
            c.execute('SELECT 1 FROM "%s".inregistrari WHERE EXTRACT(year FROM data)=%%s LIMIT 1' % schema, (Y,))
            if c.fetchone(): return True
    return False

def clasifica(conn, schema, vector, item):
    """-> (verdict SUSTINUT/NESUSTINUT/NECLASIFICAT, cauza)"""
    tip = item["tip"]; an = item["an"]; luna = item["luna"]
    plat = vector.get("platitor_tva"); tvi = vector.get("tva_inceput")
    if tip == "d112":
        activ = ci.are_salariat_activ_luna(conn, schema, an, luna)
        return ("SUSTINUT", "salariat activ in luna") if activ else ("NESUSTINUT", "luna fara salariat activ")
    if tip in ("d300", "d394") or (tip == "d406" and plat is True):
        if plat is True and tvi is None:
            return ("NESUSTINUT", "platitor TVA fara data inregistrare (tva_data_inceput NULL)")
        if tvi is not None and tvi <= _ultima_zi(an, luna):
            return ("SUSTINUT", "inregistrat TVA acoperind luna")
        return ("NESUSTINUT", "luna inainte de inregistrarea TVA")
    if tip == "d390":
        f = d390.d390_are_operatiuni(conn, schema, an, luna, AZI)
        return ("SUSTINUT", "operatiuni IC in luna") if f else ("NESUSTINUT", "nicio operatiune IC in luna")
    if tip == "d301":
        luni = ci.d301_luni_operatiuni(conn, schema, an) | ci.d301_luni_facturi_ic(conn, schema, an)
        return ("SUSTINUT", "operatiuni IC in luna") if luna in luni else ("NESUSTINUT", "nicio operatiune IC in luna")
    if tip in ("d100", "d101") or (tip == "d406" and plat is not True):
        ok = existenta_an(conn, schema, an)
        return ("SUSTINUT", "existenta demonstrabila in %d" % an) if ok else ("NESUSTINUT", "fara existenta demonstrabila in %d" % an)
    if tip == "d205":
        suma, _ = ci.dividende_distribuite(conn, schema, an)
        return ("SUSTINUT", "dividende (rulaj 457)") if suma > 0 else ("NESUSTINUT", "fara rulaj 457")
    return ("NECLASIFICAT", tip)

# shadow: cate ar fi emis un motor naiv (snapshot) dar motorul curent SUPRIMA corect
def luni_candidat(tip):
    per = [(2025, 12)] + [(2026, m) for m in range(1, 13)]
    return [(a, m) for (a, m) in per if scadente.scadenta_data(tip, a, m) < AZI]

def main():
    with db.get_conn() as cp:
        cur = cp.cursor()
        cur.execute("SELECT id, schema_name, nume FROM public.tenants ORDER BY id")
        tenants = cur.fetchall()

    tot_lipsa = 0
    tot_nesust = 0
    per_tip = collections.Counter()          # nesustinute per tip
    per_cauza = collections.Counter()         # nesustinute per cauza
    per_tip_total = collections.Counter()     # toate lipsa per tip
    exemple = []
    d112_supr = 0                             # D112 suprimate corect (luna fara salariat)
    tva_supr = 0                              # D300+D394 suprimate corect (inainte de inreg TVA)
    per_firma = []

    for tid, schema, nume in tenants:
        with db.get_conn(schema) as cs, db.get_conn() as cpub:
            # vector
            with cs.cursor() as c:
                c.execute("SELECT platitor_tva, platitor_tva_anaf_inceput FROM firma_profil LIMIT 1")
                r = c.fetchone()
                vector = {"platitor_tva": r[0] if r else None,
                          "tva_inceput": r[1] if r else None}
            ev = cf.evalueaza_firma(cs, cpub, tid, schema, azi=AZI, cu_reconciliere=False)
            lipsa = ev.get("lipsa", [])
            f_nesust = 0
            for it in lipsa:
                verdict, cauza = clasifica(cs, schema, vector, it)
                per_tip_total[it["tip"]] += 1
                tot_lipsa += 1
                if verdict == "NESUSTINUT":
                    tot_nesust += 1; f_nesust += 1
                    per_tip[it["tip"]] += 1
                    per_cauza[cauza] += 1
                    exemple.append((schema, nume, it["tip"], it["an"], it["luna"], it.get("perioada"), cauza))
            # shadow suppressions (dovada fix-uri)
            with cs.cursor() as c:
                c.execute("SELECT to_regclass(%s)", (schema + ".salariati",))
                has_sal = bool(c.fetchone()[0])
                nsal = 0
                if has_sal:
                    c.execute('SELECT count(*) FROM "%s".salariati' % schema); nsal = c.fetchone()[0]
            if has_sal and nsal > 0:
                for (a, m) in luni_candidat("d112"):
                    if not ci.are_salariat_activ_luna(cs, schema, a, m):
                        d112_supr += 1
            if vector["platitor_tva"] is True and vector["tva_inceput"] is not None:
                for (a, m) in luni_candidat("d300"):
                    if vector["tva_inceput"] > _ultima_zi(a, m):
                        tva_supr += 2   # D300 + D394
            per_firma.append((schema, nume, len(lipsa), f_nesust))

    print("=" * 70)
    print("REZULTAT AUDIT — restante NESUSTINUTE pe baza de test")
    print("azi=%s ; %d tenant-uri" % (AZI, len(tenants)))
    print("=" * 70)
    print("TOTAL verdicte de restanta (lipsa)        : %d" % tot_lipsa)
    print("TOTAL restante NESUSTINUTE                 : %d" % tot_nesust)
    print("TOTAL restante sustinute (cu premisa)     : %d" % (tot_lipsa - tot_nesust))
    print()
    print("--- NESUSTINUTE per declaratie ---")
    for tip, n in per_tip.most_common():
        print("   %-6s %3d   (din %d lipsa totale pe %s)" % (tip.upper(), n, per_tip_total[tip], tip.upper()))
    print()
    print("--- NESUSTINUTE per cauza ---")
    for cauza, n in per_cauza.most_common():
        print("   %3d  %s" % (n, cauza))
    print()
    print("--- Toate lipsa per declaratie (context) ---")
    for tip, n in per_tip_total.most_common():
        print("   %-6s %3d" % (tip.upper(), n))
    print()
    print("--- DEJA gestionate corect de motor (suprimate, NU apar ca restanta) ---")
    print("   D112 luni fara salariat suprimate (fix d112_fapt)      : %d" % d112_supr)
    print("   D300+D394 luni inainte de inreg TVA suprimate (marginit): %d" % tva_supr)
    print()
    print("--- Exemple concrete (max 12) ---")
    for e in exemple[:12]:
        print("   %-11s %-28s %-5s %d-%02d %-8s :: %s" % (e[0], (e[1] or "")[:28], e[2].upper(), e[3], e[4], str(e[5]), e[6]))
    print()
    print("--- Per firma (schema | lipsa_total | nesustinute) ---")
    for s, n, tl, fn in per_firma:
        print("   %-11s %-30s lipsa=%-3d nesust=%-3d" % (s, (n or "")[:30], tl, fn))

if __name__ == "__main__":
    main()
