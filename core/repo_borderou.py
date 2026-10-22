# -*- coding: utf-8 -*-
"""REPOSITORY — borderoul de achiziție (`facturi.tip = 'borderou'`, OMFP 2634/2015 cod 14-4-13) și stornarea lui.

[lotul 11, subagentul x — regula straturilor, `core/straturi.py`] SQL-ul scris în lotul 11 în use-case-urile borderoului
(`uc_tenants.achizitie_neinregistrat`, `_borderou_identic`, `borderouri_lista`, `borderou_storneaza`) stă aici, mutat fără schimbare de
comportament: aceleași instrucțiuni, în aceeași ordine, pe cursorul apelantului.

Fiecare funcție primește CURSORUL apelantului: aceeași tranzacție, aceeași conexiune. Nu deschide conexiuni, nu comite, nu face rollback
complet, nu construiește `HTTPException` — contractul P7/P4. Savepoint-urile au nume literal, câte o funcție fiecare (ca în
`core/tranzactie.py`: niciun nume interpolat în SQL). Cele două scrieri pe o cheie unică (`facturi_borderou_storno_uniq`,
`miscari_stoc_anuleaza_uq`) tratează dublura AICI (`chei_unice.refuza_dublura`), cu refuzul dat de apelant.
"""
from core import chei_unice as _chei   # [lotul 10, C73] stornarea dublată în cursă -> refuz numit, nu 500


def blocheaza_borderourile(cur, schema):
    """Borderourile firmei se scriu unul după altul: lacăt pe tranzacție (450 — a doua trimitere a formularului nu dublează nota)."""
    cur.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (schema + ":borderou",))


def vii_cu_data_si_valoarea(cur, schema, data, valoare):
    """[450] Borderourile VII (nici stornare, nici stornate) din `data`, a căror notă are pe 401 exact `valoare`: (id, numar, data, tert_nume)."""
    cur.execute(f"""SELECT f.id, f.numar, f.data_emitere, f.tert_nume FROM {schema}.facturi f
                    WHERE f.tip = 'borderou' AND f.storno_din_id IS NULL AND f.data_emitere = %s
                      AND (SELECT sum(l.suma) FROM {schema}.inregistrari i JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                            WHERE i.factura_id = f.id AND l.cont_credit = '401') = %s
                      AND NOT EXISTS (SELECT 1 FROM {schema}.facturi s WHERE s.storno_din_id = f.id) ORDER BY f.id""", (data, valoare))
    return cur.fetchall()


def descriere_si_cantitate(cur, schema, factura_id):
    """Liniile borderoului: (descriere, cantitate)."""
    cur.execute(f"SELECT descriere, cantitate FROM {schema}.factura_linii WHERE factura_id = %s", (factura_id,))
    return cur.fetchall()


def ale_lunii(cur, schema, an, luna):
    """Borderourile lunii, cu legătura de stornare: id, numar, data_emitere, tert_nume, storno_din_id, stornat_de_id."""
    cur.execute(f"""SELECT f.id, f.numar, f.data_emitere, f.tert_nume, f.storno_din_id,
                           (SELECT s.id FROM {schema}.facturi s WHERE s.storno_din_id = f.id AND s.tip = 'borderou'
                             ORDER BY s.id LIMIT 1) AS stornat_de_id
                      FROM {schema}.facturi f
                     WHERE f.tip = 'borderou' AND EXTRACT(YEAR FROM f.data_emitere) = %s AND EXTRACT(MONTH FROM f.data_emitere) = %s
                     ORDER BY f.data_emitere, f.id""", (int(an), int(luna)))
    return cur.fetchall()


def prima_linie(cur, schema, factura_id):
    """Prima linie a borderoului: descriere, cantitate, um (sau None)."""
    cur.execute(f"SELECT descriere, cantitate, um FROM {schema}.factura_linii WHERE factura_id = %s ORDER BY id LIMIT 1", (factura_id,))
    return cur.fetchone()


def nota_si_valoarea(cur, schema, factura_id):
    """Nota borderoului (prima, după id): id, status și valoarea pe 401 (sau None)."""
    cur.execute(f"""SELECT i.id, i.status, COALESCE((SELECT sum(x.suma) FROM {schema}.inregistrari_linii x
                              WHERE x.inregistrare_id = i.id AND x.cont_credit = '401'), 0) AS valoare
                      FROM {schema}.inregistrari i WHERE i.factura_id = %s ORDER BY i.id LIMIT 1""", (factura_id,))
    return cur.fetchone()


def de_stornat(cur, schema, factura_id):
    """Borderoul de stornat, blocat pentru tranzacția curentă (`FOR UPDATE`), sau None."""
    cur.execute(f"SELECT * FROM {schema}.facturi WHERE id = %s AND tip = 'borderou' FOR UPDATE", (int(factura_id),))
    return cur.fetchone()


def stornarea_lui(cur, schema, factura_id):
    """Borderoul care îl stornează pe `factura_id` (rândul cu `id`), sau None."""
    cur.execute(f"SELECT id FROM {schema}.facturi WHERE storno_din_id = %s AND tip = 'borderou' ORDER BY id LIMIT 1", (factura_id,))
    return cur.fetchone()


def linii_de_stornat(cur, schema, factura_id):
    """Liniile borderoului, în ordine: descriere, um, cantitate, pret_unitar."""
    cur.execute(f"SELECT descriere, um, cantitate, pret_unitar FROM {schema}.factura_linii WHERE factura_id = %s ORDER BY id", (factura_id,))
    return cur.fetchall()


def liniile_notei(cur, schema, factura_id):
    """Rândurile notelor borderoului, în ordine: cont_debit, cont_credit, suma, descriere."""
    cur.execute(f"""SELECT l.cont_debit, l.cont_credit, l.suma, i.descriere FROM {schema}.inregistrari i
                      JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                     WHERE i.factura_id = %s ORDER BY i.id, l.id""", (factura_id,))
    return cur.fetchall()


def intrari_vii(cur, schema, factura_id):
    """Intrările în stoc ale borderoului care n-au fost stornate (`stocuri_anulare._VII`)."""
    from core import stocuri_anulare as _sa
    cur.execute(f"""SELECT m.* FROM {schema}.miscari_stoc m WHERE m.factura_id = %s AND m.tip = 'intrare' AND
                    {_sa._VII.format(s=schema)} ORDER BY m.id""", (factura_id,))
    return cur.fetchall()


def savepoint_stornare(cur):
    """Un refuz al stornării nu lasă nimic scris (nici numărul), oricine ar fi apelantul."""
    cur.execute("SAVEPOINT borderou_storno")


def inapoi_la_stornare(cur):
    cur.execute("ROLLBACK TO SAVEPOINT borderou_storno")


def leaga_stornarea(cur, schema, stornat_id, storno_id, refuz):
    """`storno_din_id` pe borderoul de stornare; a doua stornare simultană a aceluiași borderou (`facturi_borderou_storno_uniq`) -> `refuz`."""
    with _chei.refuza_dublura(cur, ("facturi_borderou_storno_uniq",), refuz):
        cur.execute(f"UPDATE {schema}.facturi SET storno_din_id = %s WHERE id = %s", (stornat_id, storno_id))


def storneaza_intrarea(cur, schema, m, data, document, storno_id, refuz):
    """Intrarea în stoc `m`, stornată în roșu (cantitate și valoare cu minus, `anuleaza_id`), legată de borderoul de stornare. Intrarea deja
    stornată de altă cerere (`miscari_stoc_anuleaza_uq`) -> `refuz`. Id-ul rândului scris."""
    from decimal import Decimal
    with _chei.refuza_dublura(cur, ("miscari_stoc_anuleaza_uq",), refuz):
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document,
                            locatie, factura_id, anuleaza_id)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (m["articol_id"], data, -Decimal(str(m["cantitate"])), m.get("pret_unitar"), -Decimal(str(m["valoare"])), document,
                     m.get("locatie"), storno_id, m["id"]))
        r = cur.fetchone()
    return r["id"] if isinstance(r, dict) else r[0]
