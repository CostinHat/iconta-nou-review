# -*- coding: utf-8 -*-
"""REPOSITORY — facturile din schema unui tenant.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def tip_si_transformare(cur, factura_id):
    cur.execute("SELECT tip, transformat_in_id FROM facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


def candidate_pentru_bon(cur, schema, cui, total):
    cur.execute(f"""
                SELECT id, numar, serie, data_emitere, total, tert_nume, tert_cui
                FROM {schema}.facturi
                WHERE directie='primita' AND COALESCE(status,'') <> 'anulata' AND platita_la IS NULL
                ORDER BY (upper(replace(COALESCE(tert_cui,''),'RO','')) = %s) DESC,
                         abs(total - %s) ASC, data_emitere DESC
                LIMIT 10
            """,
                (cui, total))
    return cur.fetchall()


def factura_pentru_chitanta(cur, schema, factura_id):
    cur.execute(f"SELECT serie, numar, tert_nume, tert_cui, total, directie, data_emitere FROM {schema}.facturi WHERE id=%s",
                (factura_id,))
    return cur.fetchone()


def pentru_cashflow(cur):
    cur.execute("""SELECT directie, data_emitere, data_scadenta, total
                           FROM facturi WHERE tip='factura' AND storno_din_id IS NULL""")
    return cur.fetchall()


def stare_pentru_recunoastere(cur, schema, factura_id):
    cur.execute(f"SELECT status, directie, (xml IS NOT NULL) FROM {schema}.facturi "
                        f"WHERE id=%s FOR UPDATE",
                (factura_id,))
    return cur.fetchone()


def emise_pe_luni_pentru_intrastat(cur, schema, an):
    cur.execute(f"""SELECT directie, tert_cui,
                                   EXTRACT(MONTH FROM data_emitere)::int AS luna,
                                   COALESCE(total,0) - COALESCE(tva,0) AS baza
                            FROM {schema}.facturi
                            WHERE EXTRACT(YEAR FROM data_emitere) = %s""",
                (an,))
    return cur.fetchall()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def leaga_proforma_de_factura(cur, transformat_in_id, id_):
    cur.execute("UPDATE facturi SET transformat_in_id=%s WHERE id=%s",
                (transformat_in_id, id_))


def marcheaza_primita_platita(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s AND directie='primita'",
                (id_,))


def marcheaza_platita(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET platita_la=now() WHERE id=%s",
                (id_,))


def marcheaza_emisa(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.facturi SET status='emisa' WHERE id=%s",
                (id_,))


def actualizeaza_clasificarea(cur, schema, bucati_set, valori):
    """Scrie clasificarea aleasă la validare, pe coloanele pe care apelantul le-a ales.

    `bucati_set` sunt bucățile `coloana=%s` compuse de apelant, iar `valori` le urmează în ordine,
    cu `id`-ul la coadă. Repository-ul nu alege coloanele și nu decide dacă operația are loc — asta
    rămâne la apelant; el doar persistă.
    """
    cur.execute(f"UPDATE {schema}.facturi SET " + ", ".join(bucati_set) + " WHERE id=%s",
                valori)


def actualizeaza_destinatii_linii(cur, schema, fid, destinatii):
    """[A12b] Aplica destinatia TVA (taxabil/scutit/mixt) per linie de factura, in ORDINEA
    liniilor (ORDER BY id) — aceeasi ordine in care `_factura_din_parsat` insereaza `f["linii"]`
    din XML. UPDATE, nu INSERT: functioneaza si cand factura era deja creata prin dedup (liniile
    exista deja), nu doar la prima validare. destinatii[i] <-> linia i.

    De ce coloana ramane taxabil implicit: art.300 alin.5 (pro-rata) se aplica DOAR achizitiilor cu
    destinatie mixta; achizitia pur taxabila se deduce integral. Contabilul CLASIFICA un fapt
    importat, nu-l editeaza — vezi DESIGN_SYSTEM cap.28 (clasificare per-linie pe ecran de validare).
    """
    from core.migrare_destinatie_tva import DESTINATII
    if not destinatii:
        return
    cur.execute(f"SELECT id FROM {schema}.factura_linii WHERE factura_id=%s ORDER BY id",
                (fid,))
    ids = [r[0] for r in cur.fetchall()]
    for lid, dest in zip(ids, destinatii):
        d = (dest or "taxabil").strip()
        if d not in DESTINATII:
            raise ValueError("destinatie TVA invalida: %r (permise: %s)"
                             % (d, ", ".join(DESTINATII)))
        cur.execute(f"UPDATE {schema}.factura_linii SET destinatie_tva=%s WHERE id=%s",
                    (d, lid))
