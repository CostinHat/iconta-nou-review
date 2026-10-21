# -*- coding: utf-8 -*-
"""REPOSITORY — instructiunile SQL ale lui `core/d406.py`.

[P7 · valul D4, 13.09.2026] Statele in `core/d406.py`, modul care facea DOUA straturi deodata. Textul
canonic (`PLAN_HARDENING.md:842`): *repository-ul e singurul care stie SQL si scheme*. Instructiunile
s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri, aceeasi ordine, acelasi
`fetchone`/`fetchall`. Mutarea a fost facuta de `scripts/p7_d4_separa.py`, iar
`core/test_p7_d4.py` confrunta multimea de instructiuni a repo-ului cu cea de dinainte.

FIECARE FUNCTIE PRIMESTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construieste `HTTPException`. *Hotarele tranzactiei raman ale apelantului — contractul P4 nu se
redeschide aici.*
"""
from core.nomenclator_status_factura import (clauza_sql as _status_declarabil,      # [A3] status
                                             clauza_tip_document as _doc_fiscal)     # [A3] tip


def select_firma_profil(cur):
    # [lotul 10, deficiența C69] + telefon, iban, declarant_nume, declarant_prenume: antetul D406 le cere (S.CTH.2, S.BA.1,
    # S.PN.2, S.PN.5), iar până azi nu se citeau deloc — de-aia generatorul le „completa” cu „-” și cu un IBAN fix.
    # + baza_contabila: generatorul o citea (`TaxAccountingBasis`, planul oficial al normei) din `prof`, dar SELECT-ul nu o aducea,
    # deci fișierul spunea mereu „A” (valoarea implicită), oricare ar fi fost norma firmei (aceeași clasă: valoare pusă în locul
    # celei a firmei).
    # [lotul 10, C69, decizia Costin „Varianta 1”] + fara_cont_bancar: bifa „nu are cont bancar” din Date firmă (S.BA.2 „Fara cont bancar”)
    cur.execute("SELECT nume, cui, adresa, oras, cod_postal, platitor_tva, tip_decont, telefon, iban, declarant_nume, "
                "declarant_prenume, baza_contabila, fara_cont_bancar FROM firma_profil WHERE id = 1")
    return cur.fetchone()


def select_plan_conturi(cur):
    cur.execute("SELECT simbol, denumire, COALESCE(tip,'Bifunctional') AS tip, "
                "COALESCE(sold_debitor,0) AS sd, COALESCE(sold_creditor,0) AS sc "
                "FROM plan_conturi ORDER BY simbol")


def select_clienti(cur):
    cur.execute("SELECT id, nume, cui, oras FROM clienti ORDER BY id")


def select_furnizori(cur):
    cur.execute("SELECT id, nume, cui, oras FROM furnizori ORDER BY id")


def select_facturi(cur):
    cur.execute("SELECT tert_cui, tert_nume FROM facturi "
                "WHERE directie='emisa' ORDER BY id")


def select_facturi_2(cur):
    cur.execute("SELECT tert_cui, tert_nume FROM facturi "
                "WHERE directie='primita' ORDER BY id")


def parteneri_si_localitati(cur):
    """[lotul 10, deficiența C69, decizia Costin „Completez din ANAF”] Toți partenerii cunoscuți firmei, cu localitatea scrisă de
    contabil unde există: nomenclatorul de clienți / furnizori, facturile (`tert_oras`, cea mai nouă întâi), liniile notelor și
    operațiunile de casă (fără localitate). [{cui, nume, oras}] — `d406.localitati_locale` le face hartă pe identitatea SAF-T, iar
    partenerii cu CUI românesc rămași fără localitate se cer ANAF-ului înaintea generării."""
    cur.execute("SELECT cui, nume, oras FROM ("
                " SELECT cui, nume, oras, 1 AS o, id FROM clienti"
                " UNION ALL SELECT cui, nume, oras, 2, id FROM furnizori"
                " UNION ALL SELECT tert_cui, tert_nume, tert_oras, 3, -id FROM facturi"
                " UNION ALL SELECT partener_cui, partener_nume, NULL, 4, id FROM inregistrari_linii"
                "  WHERE COALESCE(partener_cui, '') <> '' OR COALESCE(partener_nume, '') <> ''"
                " UNION ALL SELECT cui, partener, NULL, 5, id FROM casa_operatiuni WHERE COALESCE(cui, '') <> ''"
                ") p ORDER BY o, id")
    return cur.fetchall()


def select_inregistrari(cur, di, ds):
    # [deficiența 381, 18.10.2026] partenerul liniei: cel scris pe linie (nota manuală pe 401 / 4111), altfel al facturii legate, altfel al
    # operațiunii de casă din care vine nota — până azi numai factura, deci o plată fără factură n-avea furnizor
    cur.execute("SELECT i.id, i.data, i.descriere, i.sursa, i.factura_id, l.cont_debit, l.cont_credit, "
                "l.suma, COALESCE(NULLIF(l.partener_cui, ''), f.tert_cui, co.cui) AS tert_cui, "
                "COALESCE(NULLIF(l.partener_nume, ''), f.tert_nume, co.partener) AS tert_nume "
                "FROM inregistrari i JOIN inregistrari_linii l ON l.inregistrare_id = i.id "
                "LEFT JOIN facturi f ON f.id = i.factura_id "
                "LEFT JOIN LATERAL (SELECT c.cui, c.partener FROM casa_operatiuni c WHERE c.inregistrare_id = i.id ORDER BY c.id LIMIT 1) co "
                "ON true "
                "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s "
                "ORDER BY i.id, l.id", (di, ds))


def select_factura_linii(cur, di, ds):
    # [A3, 17.09.2026] subquery-ul de facturi filtreaza status + tip (aceeasi sursa unica), altfel
    # liniile unei facturi anulate/proforme intrau in SAF-T SalesInvoices/PurchaseInvoices.
    cur.execute("SELECT factura_id, id, descriere, um, "
                "COALESCE(cantitate,0) AS cantitate, "
                "COALESCE(pret_unitar,0) AS pret_unitar, "
                "COALESCE(cota_tva,0) AS cota_tva, cont_venit "   # [380] contul de venit al liniei
                "FROM factura_linii WHERE factura_id IN "
                "(SELECT id FROM facturi WHERE data_emitere >= %s AND data_emitere < %s "
                " AND " + _doc_fiscal(None) + " AND " + _status_declarabil(None) + ") "
                "ORDER BY factura_id, id", (di, ds))


def select_facturi_3(cur, di, ds):
    # [A3] D406 nu filtra status/tip — facturile anulate/proforme intrau in SAF-T. Se adauga filtrele.
    # [lotul 10, C69] + tert_oras, tert_tara: adresa de facturare a facturii (S.I.25 / S.I.28 BillingAddress „Mandatory”), în locul „-”
    cur.execute("SELECT id, numar, data_emitere, tert_cui, tert_nume, tert_oras, tert_tara, "
                "COALESCE(total,0) AS total, COALESCE(tva,0) AS tva, "
                "moneda, curs_bnr, total_lei, tva_lei, "  # [A1] conversia in lei (SAF-T CurrencyCode=RON)
                "COALESCE(taxare_inversa,false) AS ti, storno_din_id, directie, "
                "bon_fiscal_nr, tip_operatiune "   # [punctul 3] bonul fiscal -> TaxCode 310327; [380] avansul -> 419
                "FROM facturi WHERE data_emitere >= %s AND data_emitere < %s "
                "AND " + _doc_fiscal(None) + " AND " + _status_declarabil(None) + " "
                "ORDER BY id", (di, ds))
    return cur.fetchall()



def cont_venit_implicit(cur):
    """[380] contul de venit implicit al firmei (`firma_profil.cont_venit_implicit`), ca la contarea facturii."""
    cur.execute("SELECT cont_venit_implicit FROM firma_profil WHERE id = 1")
    r = cur.fetchone()
    if not r:
        return None
    return r["cont_venit_implicit"] if isinstance(r, dict) else r[0]
