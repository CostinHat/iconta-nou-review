# -*- coding: utf-8 -*-
"""API public: chei per cabinet. Cheia se arata O SINGURA DATA la creare; stocam doar SHA256."""
import hashlib
import secrets
from psycopg2.extras import RealDictCursor


def genereaza(conn, firm_id, nume=None):
    cheie = "ick_" + secrets.token_urlsafe(32)
    h = hashlib.sha256(cheie.encode()).hexdigest()
    with conn.cursor() as cur:
        cur.execute("""INSERT INTO public.api_chei (accounting_firm_id, cheie_hash, prefix, nume)
                       VALUES (%s,%s,%s,%s) RETURNING id""",
                    (firm_id, h, cheie[:12], nume))
        kid = cur.fetchone()[0]
    conn.commit()
    return {"id": kid, "cheie": cheie, "prefix": cheie[:12]}


def lista(conn, firm_id):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""SELECT id, prefix, nume, activ, ultima_folosire, creat_la
                       FROM public.api_chei WHERE accounting_firm_id=%s ORDER BY id""", (firm_id,))
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        for c in ("ultima_folosire", "creat_la"):
            if r[c]:
                r[c] = str(r[c])
    return rows


def revoca(conn, firm_id, kid):
    with conn.cursor() as cur:
        cur.execute("""UPDATE public.api_chei SET activ=false
                       WHERE id=%s AND accounting_firm_id=%s RETURNING id""", (kid, firm_id))
        if not cur.fetchone():
            return {"eroare": "cheie inexistentă"}
    conn.commit()
    return {"revocat": kid}


def verifica(conn, cheie):
    """Intoarce firm_id daca cheia e valida si activa SI cabinetul ei e activ, altfel None.

    [DECIZIA lui Costin, 14.09.2026] Suspendarea unui cabinet e o poarta de AUTENTIFICARE si
    inchide tot accesul, nu doar loginul oamenilor: pana azi `suspenda` oprea `auth_api.login`
    (care se uita la `af.activ`), dar cheile de API mergeau mai departe, fiindca aici se intreba
    doar de `api_chei.activ`. Datele unui cabinet suspendat se livreaza prin export explicit, nu
    prin chei live. Vezi DECIZII.md (44).

    Poarta sta AICI fiindca `verifica` e singurul loc prin care trece o cheie - o verificare pusa
    pe rute ar trebui tinuta minte la fiecare ruta noua.

    Suspendarea NU atinge `api_chei.activ`: revocarea ramane un act separat, deci reactivarea
    cabinetului reda exact cheile de dinainte, fara regenerare. Iar `ultima_folosire` se scrie doar
    cand cheia chiar deschide - o incercare respinsa nu e o folosire, si nu are voie sa lase urma
    care spune ca un cabinet suspendat "a folosit" cheia."""
    if not cheie or not cheie.startswith("ick_"):
        return None
    h = hashlib.sha256(cheie.encode()).hexdigest()
    with conn.cursor() as cur:
        cur.execute("""UPDATE public.api_chei k SET ultima_folosire=now()
                       WHERE k.cheie_hash=%s AND k.activ=true
                         AND EXISTS (SELECT 1 FROM public.accounting_firms f
                                     WHERE f.id = k.accounting_firm_id AND f.activ)
                       RETURNING k.accounting_firm_id""", (h,))
        r = cur.fetchone()
    conn.commit()
    return r[0] if r else None
