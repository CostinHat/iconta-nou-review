# -*- coding: utf-8 -*-
"""Seed D406 pentru tenant_013 (ALFA) — date de TEST cu structura si validitate REALE,
apte de proba DUK. IDEMPOTENT. Tinteste EXCLUSIV tenant_013 (nu atinge 014/015/016).

Construieste:
  1. CUI-uri valide (corecteaza cifra de control a placeholder-elor RO12345678/RO87654321).
  2. Mijloace fixe (2) + note contabile de achizitie + amortizare cumulata PANA IN LUNA CURENTA
     (nu proiecteaza in viitor). <Assets> anual proiecteaza pana in Dec -> diferenta fata de GL
     e ARATATA, nu fortata.
  3. Plati de trezorerie (casa+banca) legate de facturi, note VALIDATE (intra in GL).
  4. Miscari de stoc (iesiri) legate de facturi -> PhysicalStock cu flux.

Rulare:  PYTHONPATH=$PWD venv/bin/python3 scripts/seed_alfa_d406.py
"""
import os, sys
for ln in open(os.path.expanduser("~/.iconta/db.env")):
    ln = ln.strip()
    if "=" in ln and not ln.startswith("#"):
        k, v = ln.split("=", 1); os.environ.setdefault(k.strip(), v.strip())
from decimal import Decimal
from datetime import date
from core import db
db.init_pool()

SCHEMA = "tenant_013"
MARKER = "[SEED-D406]"

# ---- cifra de control CIF (cheie 753217532) ----
def cif_check(baza):
    key = "753217532"
    b = str(baza)
    kk = key[-len(b):] if len(b) <= len(key) else key.rjust(len(b), "0")
    tot = sum(int(d) * int(k) for d, k in zip(b, kk))
    c = (tot * 10) % 11
    return 0 if c == 10 else c

def cif_valid(cui):
    """True daca CUI (numeric, fara RO) trece cifra de control."""
    cui = str(cui).upper().replace("RO", "").strip()
    if not cui.isdigit() or len(cui) < 2:
        return False
    return cif_check(cui[:-1]) == int(cui[-1])

# CUI-uri de corectat: pastreaza baza, corecteaza ULTIMA cifra
def repara_cui(cui):
    pre = "RO" if cui.upper().startswith("RO") else ""
    num = cui.upper().replace("RO", "")
    baza = num[:-1]
    return "%s%s%d" % (pre, baza, cif_check(baza))

CUI_FIX = {"RO12345678": repara_cui("RO12345678"), "RO87654321": repara_cui("RO87654321")}
print("=== CUI-uri corectate (baza pastrata, cifra de control recalculata) ===")
for vechi, nou in CUI_FIX.items():
    print("  %s -> %s | trece cifra de control: %s" % (vechi, nou, cif_valid(nou)))

with db.get_conn() as conn:
    conn.autocommit = False
    cur = conn.cursor()
    cur.execute(f"SET search_path TO {SCHEMA}, public")

    # ============ 0. CURATA seed-ul anterior (idempotenta) ============
    cur.execute("SELECT id FROM inregistrari WHERE descriere LIKE %s", (MARKER + "%",))
    old_note = [r[0] for r in cur.fetchall()]
    if old_note:
        cur.execute("DELETE FROM inregistrari_linii WHERE inregistrare_id = ANY(%s)", (old_note,))
        cur.execute("DELETE FROM inregistrari WHERE id = ANY(%s)", (old_note,))
    cur.execute("DELETE FROM mijloace_fixe WHERE cod LIKE %s", ("MF-D406-%",))
    cur.execute("DELETE FROM miscari_stoc WHERE document LIKE %s", (MARKER + "%",))

    # ============ 0b. DEBLOCHEAZA 08/2026 (artefact test F118 anterior; blocheaza inserarea notelor) ============
    cur.execute("DELETE FROM perioade_blocate WHERE an=2026 AND luna=8")
    print("perioade 08/2026 deblocate:", cur.rowcount)

    # ============ 1. CUI-uri valide peste tot ============
    loc = [("clienti", "cui"), ("furnizori", "cui"), ("casa_operatiuni", "cui"),
           ("chitante", "client_cui"), ("bonuri", "cui"), ("facturi", "tert_cui")]
    fixe = 0
    for vechi, nou in CUI_FIX.items():
        for tab, col in loc:
            cur.execute("UPDATE %s SET %s=%%s WHERE %s=%%s" % (tab, col, col), (nou, vechi))
            fixe += cur.rowcount
    print("randuri cu CUI corectat:", fixe)

    # ============ helper: nota contabila validata ============
    def nota(data, descriere, linii, factura_id=None, sursa=None):
        cur.execute("INSERT INTO inregistrari (data, descriere, factura_id, sursa, status) "
                    "VALUES (%s,%s,%s,%s,'validata') RETURNING id",
                    (data, MARKER + " " + descriere, factura_id, sursa))
        nid = cur.fetchone()[0]
        for cd, cc, suma in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                        "VALUES (%s,%s,%s,%s)", (nid, cd, cc, Decimal(str(suma))))
        return nid

    # ============ 2. MIJLOACE FIXE + note ============
    # MF-01: laptop, PIF 2026-02-15, val 4800, dnf 24 luni -> rata 200/luna
    #   amortizare incepe martie 2026; pana in aug 2026 = 6 luni -> 1200 (post real, nu proiectat)
    # MF-02: mobilier, PIF 2025-09-01, val 6000, dnf 60 luni -> rata 100/luna
    #   amortizare incepe oct 2025; pana in aug 2026 = 11 luni -> 1100
    active = [
        dict(cod="MF-D406-01", denumire="Laptop Dell Latitude 5540", cont_imobilizare="2131",
             cont_amortizare="2813", valoare=Decimal("4800.00"), rezidual=Decimal("0"),
             dnf_luni=24, data_pif=date(2026, 2, 15), metoda="liniara"),
        dict(cod="MF-D406-02", denumire="Mobilier birou (set complet)", cont_imobilizare="2131",
             cont_amortizare="2813", valoare=Decimal("6000.00"), rezidual=Decimal("0"),
             dnf_luni=60, data_pif=date(2025, 9, 1), metoda="liniara"),
    ]
    def luni_amort(pif, an, luna):
        n = (an - pif.year) * 12 + (luna - pif.month)
        return max(0, n)  # incepe cu luna urmatoare PIF
    AN, LUNA = 2026, 8
    for a in active:
        cur.execute("""INSERT INTO mijloace_fixe (cod,denumire,cont_imobilizare,cont_amortizare,
                       valoare,rezidual,dnf_luni,data_pif,metoda,activ)
                       VALUES (%(cod)s,%(denumire)s,%(cont_imobilizare)s,%(cont_amortizare)s,
                       %(valoare)s,%(rezidual)s,%(dnf_luni)s,%(data_pif)s,%(metoda)s,true)""", a)
        rata = a["valoare"] / a["dnf_luni"]
        # achizitie: 2131 + 4426(21%) / 404 (platitor TVA)
        tva = (a["valoare"] * Decimal("0.21")).quantize(Decimal("0.01"))
        nota(a["data_pif"], "achizitie " + a["cod"],
             [(a["cont_imobilizare"], "404", a["valoare"]), ("4426", "404", tva)])
        # amortizare cumulata pana in luna curenta (REALA, nu proiectata)
        luni = min(a["dnf_luni"], luni_amort(a["data_pif"], AN, LUNA))
        amort = (rata * luni).quantize(Decimal("0.01"))
        if amort > 0:
            nota(date(AN, LUNA, 28), "amortizare cumulata %s (%d luni)" % (a["cod"], luni),
                 [("6811", a["cont_amortizare"], amort)])
        print("  MF %s: val %s, rata %s/luna, %d luni amortizate -> %s (GL)" %
              (a["cod"], a["valoare"], rata, luni, amort))

    # ============ 3. PLATI TREZORERIE legate de facturi (note validate) ============
    # incasare factura 1 (CLIENT ALFA SRL, 1210) prin BANCA
    nota(date(AN, 8, 18), "incasare bancara factura 1 (CLIENT ALFA SRL)",
         [("5121", "4111", Decimal("1210.00"))], factura_id=1, sursa="banca")
    # plata factura 2 (FURNIZOR ALFA SRL, 605) prin BANCA
    nota(date(AN, 8, 19), "plata bancara factura 2 (FURNIZOR ALFA SRL)",
         [("401", "5121", Decimal("605.00"))], factura_id=2, sursa="banca")
    # incasare factura 14 (Beta, 363) prin CASA (chitanta CH-1 exista deja)
    nota(date(AN, 8, 21), "incasare numerar factura 14 (Beta Distributie SRL)",
         [("5311", "4111", Decimal("363.00"))], factura_id=14, sursa="casa")

    # ============ 4. MISCARI STOC (iesiri legate de facturi) ============
    # iesire marfa la vanzare (art 1 Hartie A4: 10 buc * 25 = 250; art 3 Dosar: 20*3=60)
    for art_id, cant, pret, val, fact in [(1, 10, 25, 250, 1), (3, 20, 3, 60, 1)]:
        cur.execute("""INSERT INTO miscari_stoc (articol_id,data,tip,cantitate,pret_unitar,valoare,document,factura_id)
                       VALUES (%s,%s,'iesire',%s,%s,%s,%s,%s)""",
                    (art_id, date(AN, 8, 20), cant, pret, val, MARKER + " iesire vanzare f1", fact))

    # ============ VERIFICARE RECONCILIERI (arata ce se inchide / ce nu) ============
    print("\n=== RECONCILIERI ===")
    # a) note balansate: fiecare nota are debit=credit pe linie (dubla intrare)? (structural OK by design)
    cur.execute("SELECT count(*) FROM inregistrari WHERE status='validata'")
    print("  note validate (total):", cur.fetchone()[0])
    # b) sold 2131 (imobilizari) = suma valoare mijloace_fixe activ
    cur.execute("SELECT coalesce(sum(suma),0) FROM inregistrari_linii WHERE cont_debit='2131'")
    d2131 = cur.fetchone()[0]
    cur.execute("SELECT coalesce(sum(valoare),0) FROM mijloace_fixe WHERE activ")
    mfval = cur.fetchone()[0]
    print("  [inchidere] 2131 debit GL = %s  vs  valoare MF activ = %s  -> %s" %
          (d2131, mfval, "OK" if d2131 == mfval else "DIFERA"))
    # c) sold 2813 (amortizare) GL vs amortizare cumulata la luna curenta
    cur.execute("SELECT coalesce(sum(suma),0) FROM inregistrari_linii WHERE cont_credit='2813'")
    print("  [inchidere] 2813 credit GL (amortizare cumulata la luna) = %s" % cur.fetchone()[0])
    # d) stoc: sold pe articol nenegativ
    cur.execute("""SELECT articol_id,
                     sum(CASE WHEN tip='intrare' THEN cantitate ELSE -cantitate END) qty,
                     sum(CASE WHEN tip='intrare' THEN valoare ELSE -valoare END) val
                   FROM miscari_stoc GROUP BY articol_id ORDER BY articol_id""")
    print("  stoc pe articol (qty, val) - nenegativ?:")
    stoc_ok = True
    for aid, qty, val in cur.fetchall():
        neg = qty < 0 or val < 0
        stoc_ok = stoc_ok and not neg
        print("     art %s: qty=%s val=%s %s" % (aid, qty, val, "!! NEGATIV" if neg else ""))
    # e) CUI-uri: mai exista vreunul invalid?
    print("  CUI-uri invalide ramase:")
    ram = []
    for tab, col in loc + [("solduri_parteneri", "cui")]:
        cur.execute(f"SELECT DISTINCT {col} FROM {tab} WHERE {col} IS NOT NULL AND {col} <> ''")
        for (v,) in cur.fetchall():
            vv = str(v)
            if (vv.upper().startswith("RO") or vv.isdigit()) and not cif_valid(vv) and not vv.startswith(("DE", "FR")):
                ram.append((tab, col, vv))
    print("    ", ram if ram else "niciunul (toate trec cifra de control sau sunt straine/PF)")

    if "--commit" in sys.argv:
        conn.commit(); print("\n[COMMIT] date persistate in tenant_013")
    else:
        conn.rollback(); print("\n[DRY-RUN] rollback (adauga --commit pentru a persista)")
