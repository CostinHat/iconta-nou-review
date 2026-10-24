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
    """Facturile emise de notificat: cu scadență, cu ceva de încasat, fără notificările oprite / amânate după `azi`.
    [deficiența 416] factura stornată integral nu primește notificare; cea stornată parțial, cu rămasul ei.
    [lotul 12, 466] starea de încasare e cea UNICĂ (`repo_facturi.de_incasat`), nu `platita_la IS NULL`: o factură încasată prin bancă
    primea notificare de plată (emailul pleacă la CLIENT). Rândurile au forma cursorului: dict (id, numar, data_scadenta, suma, moneda,
    client_email) pe un cursor de dict-uri, tuplu în aceeași ordine altfel (`notificari_scadenta._plan_notificari`)."""
    from core import repo_facturi as _rf
    rand = ("id", "numar", "data_scadenta", "suma", "moneda", "client_email")
    out = []
    for f in _rf.de_incasat(cur, "emisa", " AND COALESCE(f.notificare_stop, false) = false"
                                         " AND (f.notificare_amanata_pana IS NULL OR f.notificare_amanata_pana < %s)"
                                         " AND f.data_scadenta IS NOT NULL", (azi,)):
        v = dict(f, suma=f["rest"], client_email=f["email"])
        out.append({k: v[k] for k in rand})
    import psycopg2.extras as _E
    return out if isinstance(cur, _E.RealDictCursor) else [tuple(r[k] for k in rand) for r in out]


def select_notificari_scadenta(cur, f):
    cur.execute("SELECT prag FROM notificari_scadenta WHERE factura_id=%s", (f["id"],))
    return cur.fetchall()


def select_information_schema(cur):
    cur.execute("SELECT schema_name FROM information_schema.schemata "
                "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
    return cur.fetchall()
