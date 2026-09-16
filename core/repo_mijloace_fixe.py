# -*- coding: utf-8 -*-
"""REPOSITORY — mijloacele fixe din schema unui tenant.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


#: Coloana `reevaluari` — reevaluarile APLICATE ale activului, ca JSON, in ordine cronologica.
#:
#: [R59] Merge cu activul prin FIECARE interogare care hraneste motorul de amortizare, dinadins:
#: o reevaluare taie durata in etape (`core/d406_active._mf_la`), iar un apelant care ar construi
#: un mijloc fix „fara reevaluari" ar primi inapoi amortizarea calculata pe valoarea noua de la
#: PIF-ul original — o cifra pe care evidenta n-a inregistrat-o niciodata. Aducand-o din
#: interogare, apelantul n-are cum s-o uite: nu exista cale prin care sa n-o ceara.
#:
#: E o CONSTANTA, nu o functie, si nu din stil: in modulul asta orice `def` e o functie de depozit,
#: iar contractul P7 cere ca prima ei parametru sa fie cursorul apelantului (`core/test_p7_v1_citiri.py`).
#: Un fragment de SQL nu primeste cursor — deci nu are ce cauta ca `def`. *Poarta a avut dreptate.*
#: `{p}` = prefixul de schema (`"tenant_00x."`), sau gol cand `search_path` e deja fixat.
_REEV = """COALESCE((SELECT json_agg(json_build_object(
                     'data', r.data, 'valoare_bruta_veche', r.valoare_bruta_veche,
                     'amortizare_eliminata', r.amortizare_eliminata,
                     'valoare_justa', r.valoare_justa) ORDER BY r.data, r.id)
                  FROM {p}reevaluari r
                  WHERE r.mijloc_fix_id = mijloace_fixe.id AND r.aplicata_la IS NOT NULL),
                 '[]'::json)"""


def de_amortizat(cur, schema):
    cur.execute(f"""
                SELECT id, denumire, cont_amortizare, valoare, COALESCE(rezidual,0), dnf_luni,
                       data_pif, cont_imobilizare, metoda, {_REEV.format(p=schema + ".")} AS reevaluari
                FROM {schema}.mijloace_fixe WHERE activ = true
            """)
    return cur.fetchall()


def active_pentru_d406(cur, schema, an):
    cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                   valoare, rezidual, dnf_luni, data_pif, metoda, activ,
                                   {_REEV.format(p=schema + ".")} AS reevaluari
                            FROM {schema}.mijloace_fixe
                            WHERE data_pif IS NOT NULL
                              AND EXTRACT(YEAR FROM data_pif) <= %s
                            ORDER BY id""",
                (an,))
    return cur.fetchall()


def pentru_reevaluare(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                           valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda,
                                           {_REEV.format(p=schema + ".")} AS reevaluari
                                    FROM {schema}.mijloace_fixe WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()


def toate(cur):
    cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                  valoare, rezidual, dnf_luni, data_pif, metoda, activ,
                                  {_REEV.format(p="")} AS reevaluari
                           FROM mijloace_fixe ORDER BY activ DESC, id""")
    return cur.fetchall()


def pentru_inventariere(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                               valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda,
                                               {_REEV.format(p=schema + ".")} AS reevaluari
                                        FROM {schema}.mijloace_fixe
                                        WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def adauga(cur, schema, cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni):
    cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                            (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                             rezidual, dnf_luni, data_pif, metoda, activ)
                            VALUES (%s,%s,%s,%s,%s,0,%s,%s,'liniara',true) RETURNING id""",
                (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni))
    return cur.fetchone()


def scoate_din_evidenta(cur, schema, id_):
    cur.execute(f"UPDATE {schema}.mijloace_fixe SET activ=false WHERE id=%s",
                (id_,))


def urca_valoarea(cur, schema, id_, valoare):
    """[R59] Valoarea bruta a activului, dupa o reevaluare APLICATA (la validarea notei).

    Cifra 1 din criteriul de inchidere al lui R59; cifra 2 (`AcquisitionAndProductionCostsEnd`) o
    declara `core/d406_active.calc_asset`, care citeste tot de aici. *Un singur loc unde se scrie,
    un singur loc de unde se citeste.*
    """
    cur.execute(f"UPDATE {schema}.mijloace_fixe SET valoare=%s WHERE id=%s", (valoare, id_))


def adauga_cu_reevaluare(cur, schema, cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda):
    cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                                (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                                 rezidual, dnf_luni, data_pif, metoda, activ)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true) RETURNING id""",
                (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda))
    return cur.fetchone()
