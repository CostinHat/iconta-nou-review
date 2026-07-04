# -*- coding: utf-8 -*-
"""Jurnal — editare/ștergere/validare note. Doar ciornele se pot modifica:
AI propune (ciorna), contabilul validează."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor


def _nota(cur, schema, nota_id):
    cur.execute(f"SELECT * FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    return cur.fetchone()


def editeaza(conn, schema, nota_id, descriere=None, data=None, linii=None):
    """Editează o notă ciornă. linii = [{debit, credit, suma}] înlocuiește complet liniile."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot edita"}
        if linii is not None:
            if not linii:
                return {"eroare": "nota trebuie sa aiba cel putin o linie"}
            for l in linii:
                if not str(l.get("debit", "")).strip() or not str(l.get("credit", "")).strip():
                    return {"eroare": "fiecare linie are nevoie de cont debit si credit"}
                if Decimal(str(l.get("suma", 0))) <= 0:
                    return {"eroare": "suma fiecarei linii trebuie sa fie > 0"}
            cur.execute(f"DELETE FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s", (nota_id,))
            for l in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                    (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                    (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                     Decimal(str(l["suma"]))))
        seturi, valori = [], []
        if descriere is not None:
            seturi.append("descriere=%s"); valori.append(descriere)
        if data is not None:
            seturi.append("data=%s"); valori.append(data)
        if seturi:
            cur.execute(f"UPDATE {schema}.inregistrari SET {', '.join(seturi)} WHERE id=%s",
                        (*valori, nota_id))
    conn.commit()
    return {"ok": True}


def sterge(conn, schema, nota_id):
    """Șterge o notă ciornă (liniile cad prin ON DELETE CASCADE)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "doar ciornele se pot sterge"}
        cur.execute(f"DELETE FROM {schema}.casa_operatiuni WHERE inregistrare_id=%s", (nota_id,))
        cur.execute(f"""UPDATE {schema}.extras_linii SET status='potrivit'
                        WHERE status='contat'
                          AND alocari->'inregistrari_ids' @> %s::jsonb""", (str(nota_id),))
        cur.execute(f"DELETE FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    conn.commit()
    return {"ok": True}


def valideaza(conn, schema, nota_id):
    """Ciorna -> validata (aprobarea contabilului)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        n = _nota(cur, schema, nota_id)
        if not n:
            return None
        if n["status"] != "ciorna":
            return {"eroare": "nota nu e ciorna"}
        cur.execute(f"SELECT COUNT(*) AS c FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s",
                    (nota_id,))
        if cur.fetchone()["c"] == 0:
            return {"eroare": "nota nu are linii"}
        cur.execute(f"UPDATE {schema}.inregistrari SET status='validata' WHERE id=%s", (nota_id,))
    conn.commit()
    return {"ok": True}
