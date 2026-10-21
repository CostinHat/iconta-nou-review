# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d205_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d205_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_inregistrari_linii(cur, inc, sf):
    cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l "
                "JOIN inregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status='validata' AND l.cont_debit LIKE '457%%' "
                "AND i.data >= %s AND i.data < %s", (inc, sf))
    return cur.fetchone()


def select_asociati(cur):
    cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0 ORDER BY nume")
    return cur.fetchall()


def select_asociati_istoric(cur):
    """[lot 19 pct.4e] SQL PROPRIU al căii 2: structurile anterioare ale asociaților (nu importă repo-ul generatorului)."""
    cur.execute("SELECT cnp, nume, cota, valabil_pana_la FROM asociati_istoric ORDER BY valabil_pana_la, cnp")
    return cur.fetchall()


def select_457_miscari(cur, sf):
    """[A6] Mișcările de dividende pe NOTĂ cu DATA, din tot registrul până la `sf` (exclusiv), ordonate cronologic — recalcul
    INDEPENDENT pentru atribuirea FIFO plată->distribuire (cota după data distribuirii). SQL PROPRIU al căii 2 (nu importă
    repo-ul generatorului). [lotul 10, deficiența 431] Pe lângă 457 (credit = distribuire, 457 = 446 impozitul înregistrat, alt
    debit = plata netului, 457 = 463 = compensarea cu interimarele), interimarele pe 456: 463 = 456 distribuirea, 456 = 446
    impozitul, 456 = 512x / 531x plata. Coloanele, în
    ordine: data, distribuit, impozit, platit, compensat, distribuit_interimar, impozit_interimar, platit_interimar
    (impozitul înregistrat = debitul spre 446, plata = netul)."""
    cur.execute("SELECT n.data, "
                "SUM(CASE WHEN r.cont_credit LIKE '457%%' THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '457%%' AND substr(r.cont_credit, 1, 3) = '446' THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '457%%' AND substr(r.cont_credit, 1, 3) NOT IN ('446', '463') THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '457%%' AND substr(r.cont_credit, 1, 3) = '463' THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '463%%' AND r.cont_credit LIKE '456%%' THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '456%%' AND substr(r.cont_credit, 1, 3) = '446' THEN r.suma ELSE 0 END), "
                "SUM(CASE WHEN r.cont_debit LIKE '456%%' AND substr(r.cont_credit, 1, 3) IN ('512', '531') THEN r.suma ELSE 0 END) "
                "FROM inregistrari n JOIN inregistrari_linii r ON r.inregistrare_id = n.id "
                "WHERE n.status = 'validata' AND n.data < %s "
                "AND (r.cont_credit LIKE '45_%%' OR r.cont_debit LIKE '45_%%') "
                "GROUP BY n.id, n.data ORDER BY n.data, n.id", (sf,))
    return cur.fetchall()


def select_457_deschidere(cur, sf):
    """[lotul 10, decizia Costin A] SQL PROPRIU al căii 2: soldul creditor net al conturilor 457 din balanța de deschidere, pe data
    de referință, înainte de `sf` — dividende distribuite înainte de evidență, deschise la preluare. [(data, sold)] cu sold > 0."""
    cur.execute("SELECT s.data_referinta, SUM(s.sold_creditor) - SUM(s.sold_debitor) FROM solduri_initiale s "
                "WHERE substr(s.cont, 1, 3) = '457' AND s.data_referinta IS NOT NULL AND s.data_referinta < %s "
                "GROUP BY s.data_referinta ORDER BY s.data_referinta", (sf,))
    return [(d, v) for d, v in cur.fetchall() if v and v > 0]
