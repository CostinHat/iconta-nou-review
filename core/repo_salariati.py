# -*- coding: utf-8 -*-
"""REPOSITORY — salariații și cheile REGES ale firmei.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""
from core import chei_unice as _chei   # [lotul 10, C73 / U2] suspendarea dublată în cursă -> refuz numit, nu 500
from core.pdf_util import data_ro as _data_ro


def salariatul_exista(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def salariatul_exista_2(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def salariatul_exista_3(cur, salariat_id):
    cur.execute("SELECT 1 FROM salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def identitate_pentru_reges(cur, schema, salariat_id):
    cur.execute(f"SELECT cnp, nume, prenume FROM {schema}.salariati WHERE id=%s",
                (salariat_id,))
    return cur.fetchone()


def firma_are_chei_reges(cur, tenant_id):
    cur.execute("SELECT 1 FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


def chei_reges(cur, tenant_id):
    cur.execute("SELECT username, parola, mediu, author_id FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


def chei_reges_fara_autor(cur, tenant_id):
    cur.execute("SELECT username, parola, mediu FROM public.reges_chei WHERE tenant_id=%s",
                (tenant_id,))
    return cur.fetchone()


# ── P7 · V2: scrierile, mutate din rute ──────────────────────────────

def salveaza_cheile_reges(cur, tenant_id, username, parola, mediu):
    # upsert-ok: salvare credentiale REGES per tenant - update intentionat al aceleiasi chei (tenant_id)
    cur.execute("""INSERT INTO public.reges_chei (tenant_id, username, parola, mediu)
                           VALUES (%s,%s,%s,%s)
                           ON CONFLICT (tenant_id) DO UPDATE
                           SET username=EXCLUDED.username, parola=EXCLUDED.parola,
                               mediu=EXCLUDED.mediu""",
                (tenant_id, username, parola, mediu))


def scrie_mesaj_reges(cur, tenant_id, salariat_id, operatie, message_id, response_id):
    cur.execute("""INSERT INTO public.reges_mesaje
                           (tenant_id, salariat_id, operatie, message_id, response_id, raspuns)
                           VALUES (%s,%s,'InregistrareSalariat',%s,%s,%s) RETURNING id""",
                (tenant_id, salariat_id, operatie, message_id, response_id))
    return cur.fetchone()


def scrie_raspunsul_reges(cur, raspuns, referinta_salariat, referinta_contract, message_id, tenant_id):
    cur.execute("""UPDATE public.reges_mesaje
                               SET status='raspuns', raspuns=%s,
                                   referinta_salariat=COALESCE(%s::uuid, referinta_salariat),
                                   referinta_contract=COALESCE(%s::uuid, referinta_contract)
                               WHERE message_id=%s::uuid AND tenant_id=%s""",
                (raspuns, referinta_salariat, referinta_contract, message_id, tenant_id))


# [lot 19 pct.4c, 02.10.2026] Suspendările contractului (CFP / suspendare fără drepturi salariale). Context: search_path
# pe schema firmei (ca restul fișierului). Cursorul e al apelantului; nu se comite aici.
def suspendari_salariat(cur, salariat_id):
    cur.execute("SELECT id, data_inceput, data_sfarsit, tip, temei FROM suspendari_contract "
                "WHERE salariat_id=%s ORDER BY data_inceput", (salariat_id,))
    return cur.fetchall()


def suspendari_firma(cur):
    cur.execute("SELECT salariat_id, data_inceput, data_sfarsit, tip, temei FROM suspendari_contract "
                "ORDER BY salariat_id, data_inceput")
    return cur.fetchall()


def inlocuieste_suspendari(cur, salariat_id, lista):
    """Lista suspendărilor salariatului, înlocuită întreagă. [lotul 10, C73 / U2] Două salvări simultane ale aceleiași fișe: a doua
    aștepta la `DELETE`, nu vedea rândurile scrise de prima și cădea cu 500 pe `suspendari_contract_uniq`. Acum refuz numit, iar
    savepoint-ul helperului cuprinde și ștergerea, deci din salvarea a doua nu rămâne nimic."""
    with _chei.refuza_dublura(cur, ("suspendari_contract_uniq",), lambda cur, e: _chei.CheieDublata(
            "În timp ce salvai, altă salvare a scris deja suspendările acestui salariat (începutul %s). Din lista ta nu s-a scris "
            "nimic: reîncarcă fișa și verifică suspendările." % _data_ro((_chei.valoarea(e) or "").split(", ")[-1]))):
        cur.execute("DELETE FROM suspendari_contract WHERE salariat_id=%s", (salariat_id,))
        for a, b, tip, temei in lista:
            cur.execute("INSERT INTO suspendari_contract (salariat_id, data_inceput, data_sfarsit, tip, temei) "
                        "VALUES (%s, %s, %s, %s, %s)", (salariat_id, a, b, tip, temei))


def contract_salariat(cur, salariat_id):
    cur.execute("SELECT data_angajare, data_incetare FROM salariati WHERE id=%s", (salariat_id,))
    return cur.fetchone()


def concedii_medicale_suprapuse(cur, salariat_id, inceput, sfarsit):
    cur.execute("SELECT data_inceput, data_sfarsit FROM concedii_medicale WHERE salariat_id=%s "
                "AND data_inceput IS NOT NULL AND data_sfarsit IS NOT NULL "
                "AND data_inceput <= %s AND data_sfarsit >= %s ORDER BY data_inceput",
                (salariat_id, sfarsit, inceput))
    return cur.fetchall()
