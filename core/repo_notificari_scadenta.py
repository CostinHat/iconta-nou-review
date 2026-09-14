# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/notificari_scadenta.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/notificari_scadenta.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def insert_notificari_scadenta(cur, factura_id, prag):
    cur.execute("INSERT INTO notificari_scadenta (factura_id, prag, stare) "
                "VALUES (%s, %s, 'in_curs') ON CONFLICT (factura_id, prag) "
                "DO NOTHING RETURNING factura_id", (factura_id, prag))
    return cur.fetchone()


def insert_notificari_scadenta_2(cur, factura_id, prag, stare):
    cur.execute("INSERT INTO notificari_scadenta (factura_id, prag, stare) "
                "VALUES (%s, %s, %s) ON CONFLICT (factura_id, prag) DO NOTHING", (factura_id, prag, stare))


def update_notificari_scadenta(cur, stare, factura_id, prag):
    cur.execute("UPDATE notificari_scadenta SET stare = %s "
                " WHERE factura_id = %s AND prag = %s", (stare, factura_id, prag))


def select_firma_profil(cur):
    cur.execute("SELECT nume, email, COALESCE(notificari_scadenta_activ, false) "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_facturi(cur, azi):
    cur.execute("SELECT f.id, f.numar, f.data_scadenta, COALESCE(f.total,0) AS suma, f.moneda, "
                "       c.email AS client_email "
                "  FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                " WHERE f.directie='emisa' AND f.platita_la IS NULL "
                "   AND COALESCE(f.tip,'factura')='factura' AND f.storno_din_id IS NULL "
                "   AND COALESCE(f.notificare_stop, false) = false "
                "   AND (f.notificare_amanata_pana IS NULL OR f.notificare_amanata_pana < %s) "
                "   AND f.data_scadenta IS NOT NULL", (azi,))
    return cur.fetchall()


def select_notificari_scadenta(cur, f):
    cur.execute("SELECT prag FROM notificari_scadenta WHERE factura_id=%s", (f["id"],))
    return cur.fetchall()


def select_information_schema(cur):
    cur.execute("SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
    return cur.fetchall()
