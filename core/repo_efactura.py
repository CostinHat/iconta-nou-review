# -*- coding: utf-8 -*-
"""REPOSITORY — e-Factura primită și trimiterile către SPV.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def primite_in_asteptare(cur, schema):
    cur.execute(f"""SELECT id, cif_emitent, cif_beneficiar, status, xml_brut, factura_id
                              FROM {schema}.efactura_primite WHERE status IN ('descarcata','ciorna')
                              ORDER BY importat_la DESC LIMIT 100""")
    return cur.fetchall()


def contul_invatat_al_emitentului(cur, schema, cif_emitent):
    cur.execute(f"""SELECT cont_cheltuiala FROM {schema}.efactura_primite
                                WHERE cif_emitent=%s AND cont_cheltuiala IS NOT NULL
                                ORDER BY validat_la DESC NULLS LAST LIMIT 1""",
                (cif_emitent,))
    return cur.fetchone()


def xml_brut(cur, schema, primita_id):
    cur.execute(f"SELECT xml_brut FROM {schema}.efactura_primite WHERE id=%s",
                (primita_id,))
    return cur.fetchone()


def primita_pentru_validare(cur, schema, primita_id):
    cur.execute(f"""SELECT status, xml_brut, cif_beneficiar, factura_id
                              FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE""",
                (primita_id,))
    return cur.fetchone()


def starea_primitei_blocata(cur, schema, primita_id):
    cur.execute(f"SELECT status FROM {schema}.efactura_primite WHERE id=%s FOR UPDATE",
                (primita_id,))
    return cur.fetchone()


def ultima_trimitere_per_factura(cur, schema):
    cur.execute(f"""SELECT DISTINCT ON (factura_id) factura_id, stare, index_incarcare, error_message
                              FROM {schema}.efactura_trimiteri ORDER BY factura_id, id DESC""")
    return cur.fetchall()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def marcheaza_primita_validata(cur, schema, factura_id, cont_cheltuiala, id_):
    cur.execute(f"""UPDATE {schema}.efactura_primite
                            SET status='validata', factura_id=COALESCE(%s, factura_id),
                                cont_cheltuiala=%s, validat_la=now() WHERE id=%s
                            RETURNING factura_id""",
                (factura_id, cont_cheltuiala, id_))
    return cur.fetchone()


def marcheaza_primita_respinsa(cur, schema, motiv_respins, id_):
    cur.execute(f"""UPDATE {schema}.efactura_primite SET status='respinsa', motiv_respins=%s
                            WHERE id=%s""",
                (motiv_respins, id_))


# ── P7 · valul D2: SQL-ul care statea in motorul fiscal `core/efactura_send.py` ──
#
# Cele sapte de mai jos erau, pana la 13.09.2026, in corpul lui `incarca_factura` si al lui
# `trimite`, intr-un modul declarat `FISCAL_ENGINE`. Textul canonic cere ca un motor fiscal sa nu
# atinga baza; instructiunile s-au MUTAT, nu s-au rescris — acelasi text, aceiasi parametri,
# aceeasi ordine. Proiectiile sunt cele cerute de UBL 2.1 / CIUS-RO, de-aia stau aici si nu in
# `repo_facturi`: nu sunt „factura", sunt „factura asa cum o cere e-Factura".

def factura_pentru_ubl(cur, schema, factura_id):
    cur.execute(f"""SELECT id, numar, serie, data_emitere, data_scadenta, moneda,
                               tert_nume, tert_cui, tert_adresa, tert_oras, tert_judet,
                               taxare_inversa, tip, storno_din_id, total, tva
                          FROM {schema}.facturi WHERE id = %s""", (int(factura_id),))
    return cur.fetchone()


def linii_pentru_ubl(cur, schema, factura_id):
    cur.execute(f"""SELECT descriere, um, cantitate, pret_unitar, cota_tva
                          FROM {schema}.factura_linii WHERE factura_id = %s ORDER BY id""",
                (int(factura_id),))
    return cur.fetchall()


def emitent_pentru_ubl(cur, schema):
    cur.execute(f"""SELECT nume, cui, reg_com, adresa, oras, judet, cod_postal, iban,
                               platitor_tva
                          FROM {schema}.firma_profil WHERE id = 1""")
    return cur.fetchone()


def cui_emitent(cur, schema):
    cur.execute(f"SELECT cui FROM {schema}.firma_profil WHERE id=1")
    return cur.fetchone()


def trimitere_vie(cur, schema, factura_id, mediu):
    cur.execute(f"""SELECT id, stare FROM {schema}.efactura_trimiteri
                WHERE factura_id=%s AND mediu=%s AND stare IN ('incarcat','in_prelucrare','ok')
                LIMIT 1""", (factura_id, mediu))
    return cur.fetchone()


def insereaza_trimitere_pregatita(cur, schema, factura_id, mediu, xml, sha):
    cur.execute(f"""INSERT INTO {schema}.efactura_trimiteri
                (factura_id, mediu, stare, xml_trimis, xml_sha256, trimis_la)
                VALUES (%s,%s,'pregatit',%s,%s, now()) RETURNING id""",
                (factura_id, mediu, xml, sha))
    return cur.fetchone()


def rezultatul_trimiterii(cur, schema, stare, index_incarcare, execution_status, errmsg, trimitere_id):
    cur.execute(f"""UPDATE {schema}.efactura_trimiteri
                SET stare=%s, index_incarcare=%s, execution_status=%s, error_message=%s,
                    actualizat_la=now(),
                    finalizat_la=CASE WHEN %s IN ('nok','eroare_upload') THEN now() ELSE finalizat_la END
                WHERE id=%s""",
                (stare, index_incarcare, execution_status, errmsg, stare, trimitere_id))
