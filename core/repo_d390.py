# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d390.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d390.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


from core.nomenclator_status_factura import (clauza_sql as _status_declarabil,      # [A3] status
                                             clauza_tip_document as _doc_fiscal)     # [A3] tip


def select_facturi(cur, _exig, inceput, sfarsit):
    # [A3, 17.09.2026] D390 NU filtra nimic — nici statusul, nici tipul: proforme/avize și facturi
    # `anulata`/`stornata`/`ciorna` intrau în operațiunile IC (o proformă IC + factura rezultată =
    # dublă numărare). Se adaugă filtrele de status ȘI de tip, aceeași sursă unică ca D300/D394.
    cur.execute("SELECT f.id, f.tert_nume, f.tert_cui, c.nume AS c_nume, c.cui AS c_cui, "
                "f.directie, f.total, f.tva, f.axa_ic, "
                "f.moneda, f.curs_bnr, f.total_lei, f.tva_lei "  # [A1] conversia in lei (core.sume_lei)
                "FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                "WHERE " + _exig + " >= %s AND " + _exig + " < %s "
                "AND " + _doc_fiscal("f") + " AND " + _status_declarabil("f") + " "  # [A3] tip + status
                "ORDER BY f.id", (inceput, sfarsit))
    return cur.fetchall()


def select_d390_manual(cur, schema, an, luna):
    cur.execute(f"SELECT id, tip, tara, cod, den, baza FROM {schema}.d390_manual "
                f"WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
    return cur.fetchall()


def select_d390_reclasificare(cur, schema, an, luna):
    cur.execute(f"SELECT directie, tara, cod, tip FROM {schema}.d390_reclasificare "
                f"WHERE an=%s AND luna=%s", (an, luna))
    return cur.fetchall()


def select(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
    return cur.fetchone()


def select_d301_operatiuni(cur, schema, an, luna):
    cur.execute(f"SELECT count(*) FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s "
                f"AND tip IN (1, 3, 5) AND coalesce(partener_tara, '') = ''", (an, luna))
    return cur.fetchone()


def select_2(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
    return cur.fetchone()


def select_d301_operatiuni_2(cur, schema, an, luna):
    cur.execute(f"SELECT tip, val_valuta, curs, partener_tara, partener_cod, partener_den "
                f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s AND factura_id IS NULL "
                f"ORDER BY id", (an, luna))  # [DECIZII 66] op legata de factura -> D390 din factura


def select_3(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
    return cur.fetchone()


def select_d301_operatiuni_3(cur, schema, an, luna):
    cur.execute(f"SELECT tip, nr_doc, partener_tara, partener_cod, partener_den, temei_307 "
                f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s AND factura_id IS NULL "
                f"ORDER BY id", (an, luna))  # [DECIZII 66] op legata -> nu e exclusa, e in D390 din factura


def select_4(cur, schema):
    cur.execute("SELECT to_regclass(%s)", (schema + ".efactura_primite",))
    return cur.fetchone()


def select_schema(cur, schema, an, luna, datetime):
    cur.execute("SELECT count(*) FROM " + schema + ".efactura_primite "
                "WHERE status = 'descarcata' AND data_creare >= %s AND data_creare < %s", (datetime.date(an, luna, 1),
                         (datetime.date(an + 1, 1, 1) if luna == 12 else datetime.date(an, luna + 1, 1))))
    return cur.fetchone()
