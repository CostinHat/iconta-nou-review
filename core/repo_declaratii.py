# -*- coding: utf-8 -*-
"""REPOSITORY — coada declarațiilor și artefactele lor.

[P7 · V1, 13.09.2026] Citirile de aici stăteau în corpul rutelor din `main.py`. Textul canonic
(`PLAN_HARDENING.md:842`) spune că repository-ul e *„singurul care știe SQL și scheme"*, iar ruta nu
conține SQL — deci SQL-ul s-a mutat, nu s-a rescris: aceleași instrucțiuni, aceiași parametri,
aceeași ordine, același `fetchone`/`fetchall`.

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI. Nu deschide conexiuni, nu comite, nu face rollback,
nu construiește `HTTPException` și nu decide niciun cod HTTP. *Așa rămâne întreagă tranzacția pe
care o deține apelantul — contractul P4, care nu se redeschide aici.*
"""


def continutul_din_coada(cur, coada_id, tenant_id):
    cur.execute("SELECT tip, payload, (payload->>'_an')::int, (payload->>'_luna')::int "
                        "FROM public.declaratii_coada WHERE id=%s AND cabinet_id=%s",
                (coada_id, tenant_id))
    return cur.fetchone()


def element_coada(cur, coada_id):
    """[validare_note] (fel, tenant_id, schema firmei, cabinet_id, payload) al unui element, sau None."""
    cur.execute("SELECT c.fel, c.tenant_id, t.schema_name, c.cabinet_id, c.payload FROM public.declaratii_coada c "
                "LEFT JOIN public.tenants t ON t.id = c.tenant_id WHERE c.id=%s", (coada_id,))
    return cur.fetchone()


def autorul_elementului(cur, coada_id):
    """[deficiența 293] Cine a pus elementul în coadă (`creat_de_id`), sau None."""
    cur.execute("SELECT creat_de_id FROM public.declaratii_coada WHERE id=%s", (coada_id,))
    r = cur.fetchone()
    return r[0] if r else None


def schema_firmei_cabinetului(cur, tenant_id, cabinet_id):
    """[validare_note] Schema firmei, numai dacă firma e a cabinetului (altfel None)."""
    cur.execute("SELECT schema_name FROM public.tenants WHERE id=%s AND accounting_firm_id=%s", (tenant_id, cabinet_id))
    r = cur.fetchone()
    return r[0] if r else None


def nota_cu_linii(cur, schema, nota_id):
    """[validare_note] Nota și liniile ei, pentru ecranul de validare (citire)."""
    cur.execute(f"SELECT id, data, descriere, document_ref, status, sursa FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    n = cur.fetchone()
    if not n:
        return None, []
    cur.execute(f"SELECT cont_debit, cont_credit, suma FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s ORDER BY id",
                (nota_id,))
    return n, cur.fetchall()


def cabinet_din_coada(cur, coada_id):
    """[B1, 17.09.2026] Cabinetul care DEȚINE elementul de coadă (sau None). Poarta de apartenență
    a lui `coada_depune` interoghează prin AICI — SQL-ul stă în repository, nu în use-case (P7)."""
    cur.execute("SELECT cabinet_id FROM public.declaratii_coada WHERE id=%s", (coada_id,))
    r = cur.fetchone()
    return r[0] if r else None


def perioada_d300_manual(cur, schema, manual_id):
    cur.execute(f"SELECT an, luna FROM {schema}.d300_manual WHERE id=%s",
                (manual_id,))
    return cur.fetchone()


def trimiteri_etransport(cur, schema):
    cur.execute(f"""SELECT id, stare, uit, data_transport, uit_valabil_pana, intracom, error_message
                              FROM {schema}.etransport_trimiteri WHERE mediu='prod'
                              ORDER BY id DESC LIMIT 50""")
    return cur.fetchall()


# ── [deficiența 284] declarația de TVA care așteaptă validarea notelor (`public.declaratii_in_asteptare`, uc_coada) ──────────────────────
def inchide_asteptarea_deschisa(cur, tenant_id, tip, an, luna, trim, rezultat):
    cur.execute("UPDATE public.declaratii_in_asteptare SET rezolvata_la = now(), rezultat = %s WHERE tenant_id = %s AND tip = %s "
                "AND an = %s AND COALESCE(luna, 0) = %s AND COALESCE(trim, 0) = %s AND rezolvata_la IS NULL",
                (rezultat, tenant_id, tip, an, luna or 0, trim or 0))


def insereaza_asteptare(cur, cabinet_id, tenant_id, tip, an, luna, trim, cerere, user_id, rol, note_ids):
    cur.execute("INSERT INTO public.declaratii_in_asteptare (cabinet_id, tenant_id, tip, an, luna, trim, cerere, user_id, rol, note_ids) "
                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (cabinet_id, tenant_id, tip, an, luna, trim, cerere, user_id, rol, note_ids))
    return cur.fetchone()[0]


def asteptari_deschise(cur, cabinet_id):
    """[(id, tenant_id, note_ids, schema)] — așteptările deschise ale cabinetului."""
    cur.execute("SELECT a.id, a.tenant_id, a.note_ids, t.schema_name FROM public.declaratii_in_asteptare a "
                "JOIN public.tenants t ON t.id = a.tenant_id WHERE a.cabinet_id = %s AND a.rezolvata_la IS NULL ORDER BY a.id",
                (cabinet_id,))
    return cur.fetchall()


def revendica_asteptarea(cur, aid):
    """Închide așteptarea și întoarce (cerere, user_id, rol, tip, an, luna, trim) — None dacă a închis-o deja altă cerere."""
    cur.execute("UPDATE public.declaratii_in_asteptare SET rezolvata_la = now() WHERE id = %s AND rezolvata_la IS NULL "
                "RETURNING cerere, user_id, rol, tip, an, luna, trim", (aid,))
    return cur.fetchone()


def scrie_rezultatul_asteptarii(cur, aid, rezultat):
    cur.execute("UPDATE public.declaratii_in_asteptare SET rezultat = %s WHERE id = %s", (rezultat, aid))

