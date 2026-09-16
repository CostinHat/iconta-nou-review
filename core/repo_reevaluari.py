# -*- coding: utf-8 -*-
"""REPOSITORY — reevaluarile de imobilizari din schema unui tenant (R59).

Fiecare functie primeste CURSORUL apelantului: aceeasi tranzactie, aceeasi conexiune, acelasi
`search_path`. Nu deschide conexiuni, nu comite, nu face rollback, nu construieste `HTTPException`
si nu decide niciun cod HTTP — contractul P7/P4, care nu se redeschide aici.

Tabelul e descris in `core/migrare_reevaluare.py` (sursa unica a DDL-ului) si oglindit in
`tenant_template.sql`.
"""


def consemneaza(cur, schema, inregistrare_id, mijloc_fix_id, data_,
                valoare_bruta_veche, amortizare_eliminata, valoare_justa):
    """Reevaluarea, asa cum a fost propusa de nota CIORNA. `aplicata_la` ramane NULL."""
    cur.execute(f"""INSERT INTO {schema}.reevaluari
                    (inregistrare_id, mijloc_fix_id, data, valoare_bruta_veche,
                     amortizare_eliminata, valoare_justa)
                    VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
                (inregistrare_id, mijloc_fix_id, data_, valoare_bruta_veche,
                 amortizare_eliminata, valoare_justa))
    return cur.fetchone()


def neaplicata_pentru_nota(cur, schema, inregistrare_id):
    """(id, mijloc_fix_id, valoare_justa) pentru nota data, DOAR daca n-a fost inca aplicata.

    `FOR UPDATE` fiindca apelantul urmeaza sa urce valoarea pe registru: doua validari concurente
    ale aceleiasi note ar citi amandoua `aplicata_la IS NULL` si ar aplica de doua ori.
    """
    cur.execute(f"""SELECT id, mijloc_fix_id, valoare_justa
                    FROM {schema}.reevaluari
                    WHERE inregistrare_id=%s AND aplicata_la IS NULL
                    FOR UPDATE""",
                (inregistrare_id,))
    return cur.fetchone()


def marcheaza_aplicata(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.reevaluari SET aplicata_la=now() WHERE id=%s", (id_,))


def aplicate_pentru_mijloc(cur, schema, mijloc_fix_id):
    """Reevaluarile APLICATE ale unui activ, in ordine cronologica.

    Doar cele aplicate: o ciorna nevalidata n-a schimbat nimic, deci n-are ce cauta in baza de
    amortizare. *Un necunoscut nu se rotunjeste la „stiu ca da".*
    """
    cur.execute(f"""SELECT data, valoare_bruta_veche, amortizare_eliminata, valoare_justa
                    FROM {schema}.reevaluari
                    WHERE mijloc_fix_id=%s AND aplicata_la IS NOT NULL
                    ORDER BY data, id""",
                (mijloc_fix_id,))
    return [{"data": r[0], "valoare_bruta_veche": r[1],
             "amortizare_eliminata": r[2], "valoare_justa": r[3]} for r in cur.fetchall()]
