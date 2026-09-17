# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d394.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d394.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_firma_profil(cur):
    cur.execute("SELECT * FROM firma_profil WHERE id = 1")


from core.nomenclator_status_factura import clauza_tip_document as _doc_fiscal
from core.nomenclator_status_factura import clauza_sql as _status_declarabil  # [A3] filtru de STATUS


def select_facturi(cur, inceput, sfarsit):
    # [A3, 17.09.2026] D394 filtra doar TIPUL (proforma/aviz), NU statusul: o factura `anulata` sau
    # `stornata` intra in D394 cu baza/TVA — desi D300 le exclude. Consecinta masurata de audit: op1
    # si rezumat2 supra-declarate fata de D300 rd.9. Se adauga acelasi filtru de status ca D300 (sursa
    # unica `nomenclator_status_factura`: ciorna/de_preluat/descarcata/anulata/stornata excluse).
    cur.execute("""
                    SELECT f.id, f.directie, f.total, f.tva, f.taxare_inversa AS ti,
                           f.moneda, f.curs_bnr, f.total_lei, f.tva_lei,
                           f.categorie_331, f.tert_nume, f.tert_cui, f.tert_platitor_tva,
                           c.nume AS c_nume, c.cui AS c_cui,
                           COALESCE(json_agg(json_build_object(
                               'cota', l.cota_tva,
                               'baza', ROUND(l.cantitate * l.pret_unitar, 2))
                             ORDER BY l.id) FILTER (WHERE l.id IS NOT NULL), '[]') AS linii
                      FROM facturi f
                      LEFT JOIN clienti c ON c.id = f.client_id
                      LEFT JOIN factura_linii l ON l.factura_id = f.id
                     WHERE f.data_emitere >= %s AND f.data_emitere < %s
                       AND """ + _doc_fiscal("f") + """
                       AND """ + _status_declarabil("f") + """
                     GROUP BY f.id, c.nume, c.cui
                     ORDER BY f.id
                """, (inceput, sfarsit))
    return cur.fetchall()


def select_facturi_2(cur, inceput, sfarsit):
    cur.execute("""SELECT numar FROM facturi
                     WHERE data_emitere >= %s AND data_emitere < %s
                       AND directie = 'emisa' AND """ + _doc_fiscal(None) + """
                """, (inceput, sfarsit))
    return cur.fetchall()


def select_facturi_3(cur, inceput, sfarsit):
    cur.execute("""SELECT COALESCE(NULLIF(serie, ''), '-') AS s, numar
                     FROM facturi
                    WHERE data_emitere >= %s AND data_emitere < %s
                      AND directie = 'emisa' AND """ + _doc_fiscal(None) + """
                """, (inceput, sfarsit))
    return cur.fetchall()
