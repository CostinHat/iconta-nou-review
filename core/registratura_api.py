# -*- coding: utf-8 -*-
"""core/registratura_api.py — F146: registratura documente (registru unic intrare-iesire).

Un singur numar secvential per an (coloana `directie` marcheaza sensul). Numarul se aloca
la inregistrare din MAX(an)+1 (resetare anuala naturala). v1 = registru manual. Izolat de
contabilitate. Vezi DECIZII.md 17.07 "Lot 6 F146".
"""
import datetime
from psycopg2.extras import RealDictCursor

DIRECTII = {"intrare", "iesire"}


def lista(conn, schema, an):
    """Inregistrarile dintr-un an, in ordinea numarului."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, directie, numar, an, data, descriere, partener, document_ref
                        FROM {schema}.registratura WHERE an=%s ORDER BY numar""", (an,))
        randuri = [{"id": r["id"], "directie": r["directie"], "numar": r["numar"], "an": r["an"],
                    "data": r["data"].isoformat() if r["data"] else None,
                    "descriere": r["descriere"], "partener": r["partener"],
                    "document_ref": r["document_ref"]} for r in cur.fetchall()]
    return {"an": an, "inregistrari": randuri}


def inregistreaza(conn, schema, corp, creat_de):
    """Aloca urmatorul numar (per anul din `data`) si insereaza. corp: {directie, data?,
    descriere, partener?, document_ref?}. Coduri eroare: DIRECTIE_INVALIDA / DESCRIERE_GOALA."""
    directie = (corp.get("directie") or "").strip().lower()
    if directie not in DIRECTII:
        return {"ok": False, "cod": "DIRECTIE_INVALIDA"}
    descriere = (corp.get("descriere") or "").strip()
    if not descriere:
        return {"ok": False, "cod": "DESCRIERE_GOALA"}
    data = (corp.get("data") or "").strip() or datetime.date.today().isoformat()
    an = int(data[:4])
    partener = (corp.get("partener") or "").strip() or None
    document_ref = (corp.get("document_ref") or "").strip() or None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT COALESCE(MAX(numar),0)+1 AS urm FROM {schema}.registratura WHERE an=%s", (an,))
        numar = cur.fetchone()["urm"]
        cur.execute(f"""INSERT INTO {schema}.registratura
                        (directie, numar, an, data, descriere, partener, document_ref, creat_de)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (directie, numar, an, data, descriere, partener, document_ref, creat_de))
        rid = cur.fetchone()["id"]
    return {"ok": True, "id": rid, "numar": numar, "an": an, "directie": directie}
