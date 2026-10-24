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


def rezerva_si_pierderea(cur, schema, mijloc_fix_id):
    """[lotul 12, C116] (sold 105, pierdere 655 necompensată) ale ACTIVULUI, din notele reevaluărilor lui APLICATE: rezerva = creditele
    lui 105 minus debitele lui 105; pierderea = debitele lui 655 minus creditele lui 755 (compensarea din pct.111 alin.(1)). Fiecare,
    cel puțin 0. Numai reevaluările aplicate (nota validată): o ciornă n-a schimbat nici rezerva, nici cheltuiala."""
    cur.execute(f"""SELECT COALESCE(sum(CASE WHEN split_part(l.cont_credit, '.', 1) = '105' THEN l.suma ELSE 0 END), 0)
                         - COALESCE(sum(CASE WHEN split_part(l.cont_debit, '.', 1) = '105' THEN l.suma ELSE 0 END), 0),
                           COALESCE(sum(CASE WHEN split_part(l.cont_debit, '.', 1) = '655' THEN l.suma ELSE 0 END), 0)
                         - COALESCE(sum(CASE WHEN split_part(l.cont_credit, '.', 1) = '755' THEN l.suma ELSE 0 END), 0)
                    FROM {schema}.reevaluari r JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = r.inregistrare_id
                    WHERE r.mijloc_fix_id = %s AND r.aplicata_la IS NOT NULL""",
                (mijloc_fix_id,))
    s105, p655 = cur.fetchone()
    return max(s105 or 0, 0), max(p655 or 0, 0)
