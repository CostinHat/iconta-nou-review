# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d112_reconciliere.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d112_reconciliere.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select(cur, schema, sid, data):
    cur.execute("SELECT salariu_brut FROM %s.salariu_istoric WHERE salariat_id=%%s AND valabil_din<=%%s "
                "ORDER BY valabil_din DESC LIMIT 1" % schema, (sid, data))
    return cur.fetchone()


def select_3(cur, schema, sid, luna_inc, luna_sf):
    cur.execute("SELECT COUNT(*) AS n FROM %s.salariu_istoric WHERE salariat_id=%%s "
                "AND valabil_din > %%s AND valabil_din <= %%s" % schema, (sid, luna_inc, luna_sf))
    return cur.fetchone()


def select_4(cur, schema, luna_inc):
    cur.execute("SELECT id, part_time, scutit_contrib_minim, tichet_masa_valoare, "
                "data_angajare, data_incetare FROM %s.salariati "
                "WHERE (data_incetare IS NULL OR data_incetare >= %%s) ORDER BY id" % schema, (luna_inc,))
    return cur.fetchall()


def select_luna_partiala(cur, schema, luna_inc, luna_sf):
    """[lot 19 pct.4c] Salariații cu luna NEÎNTREAGĂ pe alte axe decât angajarea/încetarea: o schimbare de salariu în
    cursul lunii (salariu_istoric.valabil_din după prima zi) sau o suspendare (CFP / suspendare) care atinge luna."""
    cur.execute("SELECT salariat_id FROM %s.salariu_istoric WHERE valabil_din > %%s AND valabil_din <= %%s "
                "UNION SELECT salariat_id FROM %s.suspendari_contract WHERE data_inceput <= %%s AND data_sfarsit >= %%s"
                % (schema, schema), (luna_inc, luna_sf, luna_sf, luna_inc))
    return cur.fetchall()


def select_5(cur, schema, an, luna):
    cur.execute("SELECT DISTINCT salariat_id FROM %s.concedii_medicale WHERE an=%%s AND luna=%%s"
                % schema, (an, luna))
    return cur.fetchall()


def elemente_variabile(cur, schema, an, luna):
    """[S1] Elementele variabile ale lunii (prime, sporuri, ore suplimentare), pe salariat — SQL PROPRIU al căii a doua (nu
    `elemente_salariale`, care e citirea generatorului)."""
    cur.execute("SELECT salariat_id, SUM(suma) AS total FROM %s.elemente_salariale WHERE an=%%s AND luna=%%s GROUP BY salariat_id"
                % schema, (an, luna))
    return cur.fetchall()


def select_6(cur, schema, an, luna):
    cur.execute("SELECT DISTINCT salariat_id FROM %s.beneficii_lunare WHERE an=%%s AND luna=%%s"
                % schema, (an, luna))
    return cur.fetchall()
