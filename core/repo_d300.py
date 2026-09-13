# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d300.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d300.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:808`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""

def select_inregistrari(cur, _STATUS_FINAL, inceput, sfarsit):
    cur.execute("SELECT i.factura_id AS fid, f.directie AS directie, SUM(l.suma) AS settled "
                "FROM inregistrari i "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "JOIN facturi f ON f.id = i.factura_id "
                "WHERE i.status = 'validata' AND i.factura_id IS NOT NULL "
                "AND COALESCE(f.taxare_inversa, false) = false "  # art.282(6)/297(3): taxare inversa = regim general, nu la incasare
                "AND " + _STATUS_FINAL + " "  # [B1] doar facturi contabilizabile
                "AND i.data >= %s AND i.data < %s "
                "AND ((f.directie = 'emisa' AND l.cont_credit = '4111') "
                "  OR (f.directie = 'primita' AND l.cont_debit = '401')) "
                "GROUP BY i.factura_id, f.directie", (inceput, sfarsit))
    return cur.fetchall()


def select_facturi(cur, fids):
    cur.execute("SELECT f.id AS fid, f.total, f.tva, l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE f.id = ANY(%s)", (fids,))


def select_facturi_2(cur, _STATUS_FINAL, _EXIG_NORMAL, inceput, sfarsit):
    cur.execute("SELECT f.id, f.directie, f.total, f.tva, "
                "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
                "COALESCE(f.tert_tara, 'RO') AS tert_tara, "
                "l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE " + _EXIG_NORMAL + " >= %s AND " + _EXIG_NORMAL + " < %s "
                "AND " + _STATUS_FINAL + " "
                "AND COALESCE(f.taxare_inversa, false) = true ORDER BY f.id", (inceput, sfarsit))


def select_inregistrari_2(cur, _STATUS_FINAL, inceput, sfarsit):
    cur.execute("SELECT i.factura_id AS fid, SUM(l.suma) AS settled "
                "FROM inregistrari i "
                "JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "JOIN facturi f ON f.id = i.factura_id "
                "WHERE i.status = 'validata' AND i.factura_id IS NOT NULL "
                "AND f.directie = 'primita' AND COALESCE(f.furnizor_tva_incasare, false) = true "
                "AND COALESCE(f.taxare_inversa, false) = false "
                "AND " + _STATUS_FINAL + " "
                "AND i.data >= %s AND i.data < %s AND l.cont_debit = '401' "
                "GROUP BY i.factura_id", (inceput, sfarsit))
    return cur.fetchall()


def select_facturi_3(cur, fids):
    cur.execute("SELECT f.id AS fid, f.total, f.tva, l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                "WHERE f.id = ANY(%s)", (fids,))


def select_firma_profil(cur):
    cur.execute("SELECT nume, cui, adresa, oras, judet, caen, banca, iban, tip_decont, pro_rata, "
                "COALESCE(tva_la_incasare, false) AS tva_la_incasare, "
                "declarant_nume, declarant_prenume, declarant_functie "
                "FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_facturi_4(cur, _STATUS_FINAL, _EXIG_NORMAL, inceput, sfarsit):
    cur.execute("SELECT f.id, f.directie, f.total, f.tva, "
                "COALESCE(f.taxare_inversa, false) AS taxare_inversa, f.categorie_331, "
                "COALESCE(f.tert_tara, 'RO') AS tert_tara, f.tert_cui, "
                # [F125] LUNA de exigibilitate (aceeasi expresie pe care se face fereastra): cheia
                # reclasificarii D390 e per-luna (acelasi partener poate fi reclasificat diferit in luni
                # diferite - trimestru). Fara ea D300 nu poate potrivi factura pe luna corecta.
                + _EXIG_NORMAL + " AS exig, "
                "l.cantitate, l.pret_unitar, l.cota_tva "
                "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                # [B1] fereastra pe EXIGIBILITATE (COALESCE(data_faptului_generator, data_emitere); avans->emitere)
                "WHERE " + _EXIG_NORMAL + " >= %s AND " + _EXIG_NORMAL + " < %s "
                # [B1] doar facturi contabilizabile (exclude ciorna/de_preluat/descarcata/anulata/stornata)
                "AND " + _STATUS_FINAL + " "
                # [B1] deducere amanata (art.297 alin.2): primita de la furnizor la incasare -> exclusa din
                # calea de EMITERE, adusa separat pe calea de PLATA (_pull_furnizor_incasare)
                "AND NOT (f.directie = 'primita' AND COALESCE(f.furnizor_tva_incasare, false) = true) "
                "ORDER BY f.id", (inceput, sfarsit))
    return cur.fetchall()


def select_facturi_5(cur, _nsf, _inc, _sf):
    cur.execute("SELECT count(*) FROM facturi WHERE data_emitere >= %s AND data_emitere < %s "
                "AND " + _nsf.clauza_sql(None), (_inc.isoformat(), _sf.isoformat()))
    return cur.fetchone()
