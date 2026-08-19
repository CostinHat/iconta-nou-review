# -*- coding: utf-8 -*-
"""core/centre_cost_api.py — nomenclator centre de cost (F143 Faza 1).

Management accounting intern: centrul de cost e o DIMENSIUNE pe linia de nota
(inregistrari_linii.centru_cost_id), nu contabilitate bugetara publica. CRUD minimal
per firma. Stergerea nu se face (liniile istorice trimit la centru prin FK) - un centru
scos din uz se DEZACTIVEAZA (activ=false): ramane pe notele vechi, nu se mai ofera la note noi.
"""
from psycopg2.extras import RealDictCursor


def lista(conn, schema, doar_active=False):
    """Centrele firmei: [{id, nume, activ}]. doar_active=True -> doar cele oferibile la note noi."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"SELECT id, nume, activ FROM {schema}.centre_cost"
        if doar_active:
            q += " WHERE activ = true"
        q += " ORDER BY activ DESC, nume"
        cur.execute(q)
        return [dict(r) for r in cur.fetchall()]


def adauga(conn, schema, nume):
    """Adauga un centru nou. Numele e unic (case-insensitive) ca sa nu se dubleze."""
    nume = (nume or "").strip()[:100]
    if not nume:
        return {"eroare": "numele centrului e obligatoriu"}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id FROM {schema}.centre_cost WHERE lower(nume) = lower(%s)", (nume,))
        if cur.fetchone():
            return {"eroare": "există deja un centru cu acest nume"}
        cur.execute(f"INSERT INTO {schema}.centre_cost (nume) VALUES (%s) RETURNING id", (nume,))
        cid = cur.fetchone()["id"]
    conn.commit()
    return {"ok": True, "id": cid}


def seteaza_activ(conn, schema, centru_id, activ):
    """Dezactiveaza/reactiveaza un centru (nu se sterge - FK de pe liniile istorice)."""
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.centre_cost SET activ = %s WHERE id = %s",
                    (bool(activ), centru_id))
        n = cur.rowcount
    conn.commit()
    return {"ok": True} if n else None


def _f(v):
    return round(float(v or 0), 2)


def raport_realizat(conn, schema, de, pana):
    """Realizat pe centru de cost, perioada [de, pana], din note VALIDATE (nu ciorne).
    cheltuieli = SUM linii cu cont_debit clasa 6; venituri = SUM linii cu cont_credit clasa 7.
    Include si centrele fara activitate (0). Liniile fara centru nu intra pe centre, dar se
    raporteaza separat ca 'nealocat' (cat din cheltuieli/venituri nu e atribuit niciunui centru)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT cc.id, cc.nume, cc.activ,
                   COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%' AND i.id IS NOT NULL), 0) AS cheltuieli,
                   COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%' AND i.id IS NOT NULL), 0) AS venituri
            FROM {schema}.centre_cost cc
            LEFT JOIN {schema}.inregistrari_linii l ON l.centru_cost_id = cc.id
            LEFT JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
              AND i.status = 'validata' AND i.data BETWEEN %s AND %s
            GROUP BY cc.id, cc.nume, cc.activ
            ORDER BY cc.nume
        """, (de, pana))
        centre = []
        for r in cur.fetchall():
            ch, ve = _f(r["cheltuieli"]), _f(r["venituri"])
            centre.append({"id": r["id"], "nume": r["nume"], "activ": r["activ"],
                           "cheltuieli": ch, "venituri": ve, "net": round(ve - ch, 2)})
        # nealocat: linii de clasa 6/7 din note validate FARA centru (coverage)
        cur.execute(f"""
            SELECT COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%'), 0) AS cheltuieli,
                   COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%'), 0) AS venituri
            FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE l.centru_cost_id IS NULL AND i.status = 'validata' AND i.data BETWEEN %s AND %s
        """, (de, pana))
        nr = cur.fetchone()
    return {"centre": centre,
            "nealocat": {"cheltuieli": _f(nr["cheltuieli"]), "venituri": _f(nr["venituri"])}}


def seteaza_buget(conn, schema, centru_id, an, buget_cheltuieli, buget_venituri):
    """Upsert bugetul anual al unui centru (per clasa: cheltuieli + venituri). Un rand per
    (centru, an) - re-setarea inlocuieste. Sume >= 0."""
    from decimal import Decimal
    try:
        ch = Decimal(str(buget_cheltuieli or 0))
        ve = Decimal(str(buget_venituri or 0))
    except Exception:
        return {"eroare": "sume invalide"}
    if ch < 0 or ve < 0:
        return {"eroare": "bugetul nu poate fi negativ"}
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {schema}.centre_cost WHERE id = %s", (centru_id,))
        if not cur.fetchone():
            return None
        # upsert-ok: editare buget centru de cost pe (centru,an) - re-scriere intentionata
        cur.execute(f"""INSERT INTO {schema}.bugete
                        (centru_cost_id, an, buget_cheltuieli, buget_venituri)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (centru_cost_id, an) DO UPDATE
                        SET buget_cheltuieli = EXCLUDED.buget_cheltuieli,
                            buget_venituri = EXCLUDED.buget_venituri""",
                    (centru_id, an, ch, ve))
    conn.commit()
    return {"ok": True}


def raport_varianta(conn, schema, an):
    """Buget vs realizat pe an, per centru. Realizat = note VALIDATE pe tot anul (clasele 6/7).
    Include toate centrele (buget 0 daca nesetat). Abaterea o interpreteaza UI (la cheltuieli
    depasirea e rea, la venituri e buna)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT cc.id, cc.nume, cc.activ,
                   COALESCE(b.buget_cheltuieli, 0) AS buget_cheltuieli,
                   COALESCE(b.buget_venituri, 0) AS buget_venituri,
                   COALESCE(SUM(l.suma) FILTER (WHERE l.cont_debit LIKE '6%%' AND i.id IS NOT NULL), 0) AS realizat_cheltuieli,
                   COALESCE(SUM(l.suma) FILTER (WHERE l.cont_credit LIKE '7%%' AND i.id IS NOT NULL), 0) AS realizat_venituri
            FROM {schema}.centre_cost cc
            LEFT JOIN {schema}.bugete b ON b.centru_cost_id = cc.id AND b.an = %s
            LEFT JOIN {schema}.inregistrari_linii l ON l.centru_cost_id = cc.id
            LEFT JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
              AND i.status = 'validata' AND i.data BETWEEN %s AND %s
            GROUP BY cc.id, cc.nume, cc.activ, b.buget_cheltuieli, b.buget_venituri
            ORDER BY cc.nume
        """, (an, f"{an}-01-01", f"{an}-12-31"))
        centre = []
        for r in cur.fetchall():
            bch, bve = _f(r["buget_cheltuieli"]), _f(r["buget_venituri"])
            rch, rve = _f(r["realizat_cheltuieli"]), _f(r["realizat_venituri"])
            centre.append({
                "id": r["id"], "nume": r["nume"], "activ": r["activ"],
                "buget_cheltuieli": bch, "realizat_cheltuieli": rch,
                "buget_venituri": bve, "realizat_venituri": rve,
                "net_buget": round(bve - bch, 2), "net_realizat": round(rve - rch, 2),
            })
    return {"an": an, "centre": centre}
