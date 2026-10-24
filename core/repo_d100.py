# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d100.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d100.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, regim_fiscal, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_inregistrari_linii(cur, _inc, _sf):
    # [A8, 17.09.2026] Veniturile micro/profit sunt din ORICE SURSĂ, nu doar din exploatare (70x).
    # Art. 53(1) / art. 19 CF: intră și 75x (alte venituri din exploatare) și 76x (venituri
    # financiare), iar 709 (reduceri comerciale acordate) SE SCADE (cont de venit cu sold debitor).
    # Până azi baza micro (cod 121) lua doar `cont_credit LIKE '70%'`, deci un venit financiar 766 sau
    # o dobândă 766 nu intrau, iar reducerile 709 nu se scădeau. `71x` (variația stocurilor) rămâne în
    # afară, deliberat: e o corecție de producție, nu venit din sursă (art. 53 nu o include în micro).
    # [C119, lotul 12] veniturile = RULAJUL NET al conturilor 70x / 75x / 76x (credit − debit, fără închiderea în 121): nota Raportului Z
    # trece brutul pe 707 și scoate TVA-ul cu 707 = 4427 — un debit pe 707 care până azi nu se scădea (baza micro cu TVA-ul în ea).
    # 709 (reducerile acordate, cont 70x cu sold debitor) se scade tot pe aici; cheltuielile, la fel, pe rulajul net al clasei 6.
    cur.execute("SELECT COALESCE(SUM(CASE WHEN (l.cont_credit LIKE '70%%' OR l.cont_credit LIKE '75%%' "
                "        OR l.cont_credit LIKE '76%%') THEN l.suma ELSE 0 END),0) "
                "     - COALESCE(SUM(CASE WHEN (l.cont_debit LIKE '70%%' OR l.cont_debit LIKE '75%%' "
                "        OR l.cont_debit LIKE '76%%') THEN l.suma ELSE 0 END),0) AS venituri, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' THEN l.suma ELSE 0 END),0) "
                "     - COALESCE(SUM(CASE WHEN l.cont_credit LIKE '6%%' THEN l.suma ELSE 0 END),0) AS cheltuieli "
                "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND i.data >= %s AND i.data < %s "
                "AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%'", (_inc.isoformat(), _sf.isoformat()))   # [C15] fără închiderea în 121
    return cur.fetchone()


def select_facturi(cur, _inc, _sf):
    from core import nomenclator_status_factura as _nsf   # [lotul 12, 252] numai documentele fiscale (nu proforme, avize, facturi preluate)
    cur.execute("SELECT count(*) FROM facturi WHERE directie='emisa' "
                "AND data_emitere >= %s AND data_emitere < %s AND " + _nsf.clauza_tip_document(None), (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()


def venituri_pe_conturi(cur, _inc, _sf):
    """[deficiența 295] Baza micro pe conturi: aceleași note și aceleași conturi ca `select_inregistrari_linii` — rulajul NET al fiecărui
    cont 70x / 75x / 76x (credit − debit; [C119] debitul 707 = 4427 al notei Z se scade), note validate, fără închiderea în 121.
    [(cont, suma)] — 709 cu semnul minus."""
    cur.execute("SELECT cont, SUM(s) FROM ("
                "SELECT l.cont_credit AS cont, l.suma AS s FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND i.data >= %s AND i.data < %s "
                "AND (l.cont_credit LIKE '70%%' OR l.cont_credit LIKE '75%%' OR l.cont_credit LIKE '76%%') "
                "AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%' "
                "UNION ALL "
                "SELECT l.cont_debit, -l.suma FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND i.data >= %s AND i.data < %s "
                "AND (l.cont_debit LIKE '70%%' OR l.cont_debit LIKE '75%%' OR l.cont_debit LIKE '76%%') "
                "AND l.cont_debit NOT LIKE '121%%' AND l.cont_credit NOT LIKE '121%%') x GROUP BY cont HAVING SUM(s) <> 0 ORDER BY 1",
                (_inc.isoformat(), _sf.isoformat(), _inc.isoformat(), _sf.isoformat()))
    return cur.fetchall()



def d100_depuse_an(cur, schema, an):
    """[deficiența 377, 18.10.2026] D100-urile depuse ale anului (prin iConta sau preluate din istoric la migrare), cea curentă pe perioadă:
    [(luna, randuri, sursa, data_depunere)]."""
    cur.execute("SELECT d.luna, d.randuri, d.sursa, d.data_depunere FROM public.declaratii_depuse_curente d "
                "JOIN public.tenants t ON t.id = d.tenant_id WHERE t.schema_name = %s AND d.tip = 'd100' AND d.an = %s ORDER BY d.luna",
                (str(schema).strip('"'), int(an)))
    return [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]
