# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/scadentar.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/scadentar.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:829`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT COALESCE(notificari_scadenta_activ, false) AS activ FROM firma_profil WHERE id=1")
    return cur.fetchone()


def select_facturi(cur):
    cur.execute("SELECT f.id, f.numar, f.serie, f.data_emitere, f.data_scadenta, "
                "       COALESCE(f.total,0) AS suma, f.moneda, f.tert_nume, f.tert_cui, "
                "       f.client_id, c.email, "
                "       COALESCE(f.notificare_stop, false) AS notificare_stop, f.notificare_amanata_pana "
                "  FROM facturi f "
                "  LEFT JOIN clienti c ON c.id = f.client_id "
                " WHERE f.directie = 'emisa' AND f.platita_la IS NULL "
                "   AND COALESCE(f.tip, 'factura') = 'factura' "
                "   AND f.storno_din_id IS NULL")
    return cur.fetchall()


def select_firma_profil_2(cur):
    cur.execute("SELECT email FROM firma_profil WHERE id=1")
    return cur.fetchone()


def update_firma_profil(cur, activ):
    cur.execute("UPDATE firma_profil SET notificari_scadenta_activ=%s WHERE id=1", (bool(activ),))


def update_facturi(cur, factura_id, stop, amanata_pana):
    cur.execute("UPDATE facturi SET notificare_stop=%s, notificare_amanata_pana=%s "
                "WHERE id=%s AND directie='emisa'", (bool(stop), amanata_pana or None, factura_id))
