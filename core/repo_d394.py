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
from core import facturi as _fc   # [decizia A 02.10] definiția „factură din bon fiscal”


def select_rapoarte_z(cur, surse, inceput, sfarsit):
    """[D394 op2 Î1, decizia B 02.10.2026] Rapoartele Z VALIDATE din fereastră: casa + bonurile (`rapoarte_z_amef`) și
    defalcarea pe cote (`rapoarte_z_cote`) — aceleași tabele pe ambele rute (import AMEF / tastat). LEFT JOIN: un raport
    fără rândul AMEF sau fără cote iese cu NULL, ca apelantul să-l NUMEASCĂ, nu să-l sară."""
    cur.execute("SELECT i.id AS id, i.numar AS numar, i.data AS data, a.nui AS nui, a.nr_bonuri AS nr_bonuri, "
                "z.cota AS cota, z.baza AS baza, z.tva AS tva "
                "FROM inregistrari i LEFT JOIN rapoarte_z_amef a ON a.inregistrare_id = i.id "
                "LEFT JOIN rapoarte_z_cote z ON z.inregistrare_id = i.id "
                "WHERE i.status = 'validata' AND i.sursa = ANY(%s) AND i.data >= %s AND i.data < %s "
                "ORDER BY i.data, i.id, z.cota", (list(surse), inceput, sfarsit))
    return cur.fetchall()


def select_chitante_fara_factura(cur, inceput, sfarsit):
    """[D394 Î2, decizia Costin 03.10.2026] Chitanțele fără factură, neanulate, din fereastră — cu cota (vânzare din
    activitatea exceptată) sau fără (neclasificată, o numește apelantul)."""
    cur.execute("SELECT id, serie, numar, data, suma, cota_tva FROM chitante "
                "WHERE factura_id IS NULL AND NOT anulata AND data >= %s AND data < %s ORDER BY data, id",
                (inceput, sfarsit))
    return cur.fetchall()


def select_casa_incasari_nelegate(cur, fara_vanzare, inceput, sfarsit):
    """[D394 Î2, decizia Costin 03.10.2026] Încasările din registrul de casă fără chitanță (deci fără factură) și
    fără o categorie cunoscută fără caracter de vânzare — semnal, nu blocaj."""
    cur.execute("SELECT o.id, o.data, o.document, o.partener, o.suma, o.categorie FROM casa_operatiuni o "
                "WHERE o.tip = 'incasare' AND NOT (o.categorie = ANY(%s)) AND o.data >= %s AND o.data < %s "
                "AND NOT EXISTS (SELECT 1 FROM chitante c WHERE c.casa_operatiune_id = o.id AND NOT c.anulata) "
                "ORDER BY o.data, o.id", (list(fara_vanzare), inceput, sfarsit))
    return cur.fetchall()


def select_facturi_din_bon(cur, inceput, sfarsit):
    """[decizia A 02.10.2026] Facturile EMISE pe baza unui bon fiscal din fereastră (pe DATA BONULUI — luna raportului Z din
    care se scad), cu liniile pe cotă. Aceleași filtre de status/document ca `select_facturi`; storno-ul (care moștenește
    marca) vine cu linii negative și adaugă suma înapoi în Î1."""
    cur.execute("SELECT f.id AS id, f.numar AS numar, f.bon_fiscal_nr AS bon_fiscal_nr, f.bon_fiscal_data AS bon_fiscal_data, "
                "f.moneda AS moneda, f.curs_bnr AS curs_bnr, f.total_lei AS total_lei, f.tva_lei AS tva_lei, "
                "f.total AS total, f.tva AS tva, l.cota_tva AS cota, ROUND(l.cantitate * l.pret_unitar, 2) AS baza "
                "FROM facturi f JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE " + _fc.clauza_din_bon("f") + " "
                "AND f.bon_fiscal_data >= %s AND f.bon_fiscal_data < %s "
                "AND " + _status_declarabil("f") + " AND " + _doc_fiscal("f") + " ORDER BY f.id, l.id",
                (inceput, sfarsit))
    return cur.fetchall()


def select_facturi(cur, inceput, sfarsit):
    # [A3, 17.09.2026] D394 filtra doar TIPUL (proforma/aviz), NU statusul: o factura `anulata` sau
    # `stornata` intra in D394 cu baza/TVA — desi D300 le exclude. Consecinta masurata de audit: op1
    # si rezumat2 supra-declarate fata de D300 rd.9. Se adauga acelasi filtru de status ca D300 (sursa
    # unica `nomenclator_status_factura`: ciorna/de_preluat/descarcata/anulata/stornata excluse).
    cur.execute("""
                    SELECT f.id, f.directie, f.total, f.tva, f.taxare_inversa AS ti,
                           f.moneda, f.curs_bnr, f.total_lei, f.tva_lei,
                           COALESCE(f.furnizor_tva_incasare, false) AS furnizor_tva_incasare,
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
