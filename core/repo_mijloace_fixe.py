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
from core import chei_unice as _chei   # [lotul 10, C73] codul de inventar dublat -> refuz numit, nu 500


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


# [359, decizia Costin 9.1 A.1] fiecare cititor al registrului pentru amortizare poartă și `amortizare_preluata` / `data_preluare`
# (`d406_active._preluare`): o singură regulă pentru nota lunii, registru, închiderea lunii și D406
def de_amortizat(cur, schema):
    cur.execute(f"""
                SELECT id, denumire, cont_amortizare, valoare, COALESCE(rezidual,0), dnf_luni,
                       data_pif, cont_imobilizare, metoda, {_REEV.format(p=schema + ".")} AS reevaluari,
                       destinatie_cd, amortizare_preluata, data_preluare
                FROM {schema}.mijloace_fixe WHERE activ = true ORDER BY id
            """)
    return cur.fetchall()


def active_pentru_d406(cur, schema, an):
    cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                   valoare, rezidual, dnf_luni, data_pif, metoda, activ,
                                   {_REEV.format(p=schema + ".")} AS reevaluari, destinatie_cd, amortizare_preluata, data_preluare
                            FROM {schema}.mijloace_fixe
                            WHERE data_pif IS NOT NULL
                              AND EXTRACT(YEAR FROM data_pif) <= %s
                              -- [lotul 13, 519] activul adus de o notă încă nevalidată nu e în evidență
                              AND NOT EXISTS (SELECT 1 FROM {schema}.mf_note n JOIN {schema}.inregistrari i ON i.id = n.inregistrare_id
                                              WHERE n.mijloc_fix_id = mijloace_fixe.id AND n.fel = 'intrare' AND i.status <> 'validata')
                            ORDER BY id""",
                (an,))
    return cur.fetchall()


def pentru_reevaluare(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                           valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda,
                                           {_REEV.format(p=schema + ".")} AS reevaluari, destinatie_cd, amortizare_preluata,
                                           data_preluare
                                    FROM {schema}.mijloace_fixe WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()


def toate(cur):
    cur.execute(f"""SELECT id, cod, denumire, cont_imobilizare, cont_amortizare,
                                  valoare, rezidual, dnf_luni, data_pif, metoda, activ,
                                  {_REEV.format(p="")} AS reevaluari, destinatie_cd, cod_catalog, amortizare_preluata, data_preluare
                           FROM mijloace_fixe ORDER BY activ DESC, id""")
    return cur.fetchall()


def seteaza_cod_catalog(cur, mijloc_id, cod):
    """[08.10.2026, W2] codul de clasificare din Catalogul HG 2139/2004."""
    cur.execute("UPDATE mijloace_fixe SET cod_catalog = %s WHERE id = %s RETURNING id, dnf_luni", (cod, mijloc_id))
    return cur.fetchone()


def pentru_inventariere(cur, schema, mijloc_id):
    cur.execute(f"""SELECT denumire, cont_imobilizare, cont_amortizare,
                                               valoare, COALESCE(rezidual,0), dnf_luni, data_pif, metoda,
                                               {_REEV.format(p=schema + ".")} AS reevaluari, destinatie_cd, amortizare_preluata,
                                               data_preluare
                                        FROM {schema}.mijloace_fixe
                                        WHERE id=%s AND activ=true""",
                (mijloc_id,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

#: cheia naturală a registrului (`core/migrare_intrare_date_garduri.UNIQUE`): un cod de inventar = un singur mijloc fix, activ sau scos
CONSTRANGERE_COD = "mijloace_fixe_cod_uniq"


def cod_liber(cur, schema, cod):
    """[lotul 10, C73] Codul de inventar pe care îl dă aplicația când omul n-a scris unul (ecranele de operațiuni n-au câmp de cod):
    `cod` dacă e liber, altfel primul `cod-2`, `cod-3`, … liber. Înainte, a doua licență primea același „NEC-LIC” ca prima și
    scrierea cădea cu 500 pe `mijloace_fixe_cod_uniq` — o dublură produsă de aplicație, nu de om."""
    cur.execute(f"SELECT cod FROM {schema}.mijloace_fixe WHERE cod = %s OR left(cod, length(%s) + 1) = %s || '-'", (cod, cod, cod))
    folosite = {r[0] for r in cur.fetchall()}
    if cod not in folosite:
        return cod
    n = 2
    while "%s-%d" % (cod, n) in folosite:
        n += 1
    return "%s-%d" % (cod, n)


def _refuz_cod(cur, e, schema, cod):
    """Refuzul codului de inventar dublat, cu mijlocul fix care îl are deja (citit după ROLLBACK TO SAVEPOINT, pe cursorul apelantului)."""
    cur.execute(f"SELECT id, denumire, activ FROM {schema}.mijloace_fixe WHERE cod = %s", (cod,))
    r = cur.fetchone()
    unde = (" la %s%s" % (r[1], "" if r[2] else " (scos din evidență)")) if r else ""
    return _chei.CheieDublata("Codul de inventar %s e deja în registrul mijloacelor fixe%s. Un cod de inventar aparține unui "
                              "singur mijloc fix: dă-i acestuia alt cod." % (cod, unde), valoare=cod,
                              existent={"mijloc_fix_id": r[0], "denumire": r[1]} if r else None, camp="cod")


def adauga(cur, schema, cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni):
    with _chei.refuza_dublura(cur, (CONSTRANGERE_COD,), lambda c, e: _refuz_cod(c, e, schema, cod)):   # [lotul 10, C73]
        cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                                (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                                 rezidual, dnf_luni, data_pif, metoda, activ)
                                VALUES (%s,%s,%s,%s,%s,0,%s,%s,'liniara',true) RETURNING id""",
                    (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni))
        return cur.fetchone()


def urca_valoarea(cur, schema, id_, valoare):
    """[R59] Valoarea bruta a activului, dupa o reevaluare APLICATA (la validarea notei).

    Cifra 1 din criteriul de inchidere al lui R59; cifra 2 (`AcquisitionAndProductionCostsEnd`) o
    declara `core/d406_active.calc_asset`, care citeste tot de aici. *Un singur loc unde se scrie,
    un singur loc de unde se citeste.*
    """
    cur.execute(f"UPDATE {schema}.mijloace_fixe SET valoare=%s WHERE id=%s", (valoare, id_))


def adauga_cu_reevaluare(cur, schema, cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda, destinatie_cd=False):
    with _chei.refuza_dublura(cur, (CONSTRANGERE_COD,), lambda c, e: _refuz_cod(c, e, schema, cod)):   # [lotul 10, C73]
        cur.execute(f"""INSERT INTO {schema}.mijloace_fixe
                                    (cod, denumire, cont_imobilizare, cont_amortizare, valoare,
                                     rezidual, dnf_luni, data_pif, metoda, activ, destinatie_cd)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,true,%s) RETURNING id""",
                    (cod, denumire, cont_imobilizare, cont_amortizare, valoare, rezidual, dnf_luni, data_pif, metoda,
                     bool(destinatie_cd)))
        return cur.fetchone()


def seteaza_destinatie_cd(cur, schema, id_, destinatie_cd, user_id):
    """[lot 19 d11] Bifa «Destinat C&D» (CF art.20 alin.(1) lit.b)). Intoarce (id, valoarea veche) sau None daca activul
    nu exista. [decizia Costin 04.10.2026] Fiecare SCHIMBARE se jurnalizeaza (utilizator, data, veche -> noua) in ACEEASI
    tranzactie — randul vechi se blocheaza (FOR UPDATE), ca doua apasari simultane sa nu scrie acelasi „veche”."""
    cur.execute(f"SELECT destinatie_cd FROM {schema}.mijloace_fixe WHERE id=%s AND activ=true FOR UPDATE", (id_,))
    r = cur.fetchone()
    if r is None:
        return None
    veche, noua = bool(r[0]), bool(destinatie_cd)
    if veche != noua:
        cur.execute(f"UPDATE {schema}.mijloace_fixe SET destinatie_cd=%s WHERE id=%s", (noua, id_))
        cur.execute(f"""INSERT INTO {schema}.mijloace_fixe_jurnal (mijloc_id, camp, valoare_veche, valoare_noua, user_id)
                        VALUES (%s, 'destinatie_cd', %s, %s, %s)""", (id_, str(veche).lower(), str(noua).lower(), user_id))
    return id_, veche


def seteaza_cod_catalog_schema(cur, schema, mijloc_id, cod):
    """[lotul 13, 521] Codul din catalog al activului nou (plus de inventar, leasing), pe schema dată."""
    cur.execute(f"UPDATE {schema}.mijloace_fixe SET cod_catalog = %s WHERE id = %s", (cod, mijloc_id))
