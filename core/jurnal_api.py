# -*- coding: utf-8 -*-
"""Jurnal — editare/ștergere/validare note. Doar ciornele se pot modifica:
AI propune (ciorna), contabilul validează."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor


def _nota(cur, schema, nota_id):
    cur.execute(f"SELECT * FROM {schema}.inregistrari WHERE id=%s", (nota_id,))
    return cur.fetchone()


def _centru(l):
    """[F143] centru_cost_id de pe o linie -> int sau None (nealocat). Gol/0 = nealocat."""
    v = l.get("centru_cost_id")
    if v in (None, "", 0, "0"):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def creeaza(conn, schema, descriere, data, linii):
    """Creeaza o nota manuala noua, ca ciorna. linii = [{debit, credit, suma}], min 1 linie."""
    if not linii:
        return {"eroare": "nota trebuie să aibă cel puțin o linie"}
    for l in linii:
        if not str(l.get("debit", "")).strip() or not str(l.get("credit", "")).strip():
            return {"eroare": "fiecare linie are nevoie de cont debit și credit"}
        if Decimal(str(l.get("suma", 0))) <= 0:
            return {"eroare": "suma fiecărei linii trebuie să fie > 0"}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                        VALUES (%s,%s,'manual','ciorna') RETURNING id""",
                    (data, (descriere or "")[:200]))
        nota_id = cur.fetchone()["id"]
        for l in linii:
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id)
                VALUES (%s,%s,%s,%s,%s)""",
                (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                 Decimal(str(l["suma"])), _centru(l)))
    conn.commit()
    return {"ok": True, "id": nota_id}
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
                return {"eroare": "nota trebuie să aibă cel puțin o linie"}
            # ai_corectie_v1: memoreaza contul debit dinainte de edit (propunerea AI)
            cur.execute(f"""SELECT cont_debit FROM {schema}.inregistrari_linii
                            WHERE inregistrare_id=%s ORDER BY id LIMIT 1""", (nota_id,))
            _vechi = cur.fetchone()
            _cont_vechi = (_vechi["cont_debit"] if isinstance(_vechi, dict) else _vechi[0]) if _vechi else None
            for l in linii:
                if not str(l.get("debit", "")).strip() or not str(l.get("credit", "")).strip():
                    return {"eroare": "fiecare linie are nevoie de cont debit și credit"}
                if Decimal(str(l.get("suma", 0))) <= 0:
                    return {"eroare": "suma fiecărei linii trebuie să fie > 0"}
            cur.execute(f"DELETE FROM {schema}.inregistrari_linii WHERE inregistrare_id=%s", (nota_id,))
            for l in linii:
                cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                    (inregistrare_id, cont_debit, cont_credit, suma, centru_cost_id)
                    VALUES (%s,%s,%s,%s,%s)""",
                    (nota_id, str(l["debit"]).strip(), str(l["credit"]).strip(),
                     Decimal(str(l["suma"])), _centru(l)))
            # ai_corectie_v2: cont schimbat de contabil => corectie invatata
            try:
                _cont_nou = str(linii[0]["debit"]).strip()
                if _cont_vechi and _cont_nou and _cont_vechi != _cont_nou and n.get("descriere"):
                    from core import ai_incredere as _ai
                    _ctx = _ai.normalizeaza(n["descriere"])
                    if _ctx:
                        cur.execute(f"""INSERT INTO {schema}.ai_corectii
                                        (context, cont_propus, cont_final, corectat)
                                        VALUES (%s,%s,%s,true)""", (_ctx, _cont_vechi, _cont_nou))
            except Exception as _e:
                from core import observare as _obs
                _obs.esec_secundar("invatare AI la editare nota", _e)  # inghitit, dar nu tacut (27.07.2026)
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
            return {"eroare": "doar ciornele se pot șterge"}
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
        # ai_invatare_v1: invatare din validare (context = descriere, cont = debitul primei linii)
        try:
            cur.execute(f"""SELECT cont_debit FROM {schema}.inregistrari_linii
                            WHERE inregistrare_id=%s ORDER BY id LIMIT 1""", (nota_id,))
            ld = cur.fetchone()
            if ld and n.get("descriere"):
                from core import ai_incredere as _ai
                ctx_t = _ai.normalizeaza(n["descriere"])
                cont_f = ld["cont_debit"] if isinstance(ld, dict) else ld[0]
                if ctx_t and cont_f:
                    cur.execute(f"""INSERT INTO {schema}.ai_corectii
                                    (context, cont_propus, cont_final, corectat)
                                    VALUES (%s,%s,%s,false)""", (ctx_t, cont_f, cont_f))
        except Exception as _e:
            from core import observare as _obs
            _obs.esec_secundar("invatare AI la validare nota", _e)  # inghitit, dar nu tacut (27.07.2026)
    conn.commit()
    return {"ok": True}


def document_justificativ(document_ref, fel, serie, numar, data):
    """Coloana 3 din Registrul-jurnal (OMFP 2634/2015, cod 14-1-1): *„felul, numărul și data
    documentului justificativ care stă la baza operațiunilor (factura, chitanța etc.)"*.

    Se DERIVĂ, nu se fabrică. Trei căi, în ordine:
      1. `document_ref` scris explicit pe notă — se ia ca atare;
      2. factura legată prin `factura_id` — se compune „Factură <serie><număr> din <data>";
      3. nimic din care s-o derivi -> **None**, adică lipsă vizibilă.

    A treia e importantă: un registru care ar completa un document inexistent ar face exact ce am
    scos din ecranul de NIR — ar răspunde în locul omului. O coloană goală e onestă.
    """
    if document_ref:
        return str(document_ref).strip() or None
    if numar is None:
        return None
    nr = "%s%s" % (serie or "", numar)
    et = "Factură" if (fel or "factura") == "factura" else str(fel).capitalize()
    return "%s %s din %s" % (et, nr, data.isoformat() if hasattr(data, "isoformat") else data)
