"""
core/notificari_api.py — notificari in-app (clopotel).
O notificare = un eveniment adresat unui user (user_id), cu tip, text, link optional.
Faza 1: doar in-app. Email zilnic = faza 2.
"""
import psycopg2.extras as _E


def adauga(conn, user_id, tip, text, link=None):
    """Scrie o notificare pentru un user. user_id None -> ignora (defensiv)."""
    if not user_id:
        return {"ok": False, "cod": "FARA_DESTINATAR"}
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO public.notificari (user_id, tip, text, link) "
            "VALUES (%s,%s,%s,%s) RETURNING id",
            (int(user_id), tip, text, link))
        nid = cur.fetchone()[0]
    return {"ok": True, "id": nid}


def adauga_multi(conn, user_ids, tip, text, link=None):
    """Aceeasi notificare pentru mai multi useri (ex: toti validatorii)."""
    n = 0
    for uid in (user_ids or []):
        if uid:
            adauga(conn, uid, tip, text, link)
            n += 1
    return {"ok": True, "trimise": n}


def validatorii_cabinetului(conn, cabinet_id, exclude_id=None):
    """Id-urile validatorilor activi (poate_valida), optional fara unul (pregatitorul).

    [po_efectiv_v1] Delegat la core.coada_api.validatori_activi: destinatarii notificarii de
    validare sunt EXACT multimea pe care se calculeaza aplicabilitatea patru-ochi. Doua interogari
    separate puteau diverge - s-ar fi notificat cine nu poate aproba, sau invers."""
    from core.coada_api import validatori_activi as _va
    return _va(conn, cabinet_id, exclude_id=exclude_id)


def lista(conn, user_id, doar_necitite=False, limita=50):
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cond = "user_id = %s"
        val = [int(user_id)]
        if doar_necitite:
            cond += " AND citit = false"
        cur.execute(
            "SELECT id, tip, text, link, citit, creat_la "
            "  FROM public.notificari WHERE " + cond +
            " ORDER BY creat_la DESC LIMIT %s", val + [int(limita)])
        out = []
        for r in cur.fetchall():
            out.append({
                "id": r["id"], "tip": r["tip"], "text": r["text"],
                "link": r["link"], "citit": r["citit"],
                "cand": r["creat_la"].isoformat(),
            })
    return {"ok": True, "notificari": out}


def contor(conn, user_id):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM public.notificari WHERE user_id = %s AND citit = false",
            (int(user_id),))
        n = cur.fetchone()[0]
    return {"ok": True, "necitite": int(n)}


def marcheaza_citit(conn, user_id, notif_id=None):
    """Marcheaza una (notif_id) sau toate notificarile userului ca citite."""
    with conn.cursor() as cur:
        if notif_id is not None:
            cur.execute(
                "UPDATE public.notificari SET citit = true "
                " WHERE id = %s AND user_id = %s", (int(notif_id), int(user_id)))
        else:
            cur.execute(
                "UPDATE public.notificari SET citit = true "
                " WHERE user_id = %s AND citit = false", (int(user_id),))
    return {"ok": True}

def sumar(conn, user_id):  # [p63_notif_sumar]
    """Necitite grupate pe tip, pentru sumarul de la login."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT tip, COUNT(*) FROM public.notificari "
            " WHERE user_id = %s AND citit = false GROUP BY tip",
            (int(user_id),))
        pe_tip = [{"tip": r[0], "n": int(r[1])} for r in cur.fetchall()]
    total = sum(x["n"] for x in pe_tip)
    return {"ok": True, "necitite": total, "pe_tip": pe_tip}
