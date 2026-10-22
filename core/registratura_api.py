# -*- coding: utf-8 -*-
"""core/registratura_api.py — F146: registratura documente (registru unic intrare-iesire).

Un singur numar secvential per an (coloana `directie` marcheaza sensul). Numarul se aloca
la inregistrare din MAX(an)+1 (resetare anuala naturala). v1 = registru manual. Izolat de
contabilitate. Vezi DECIZII.md 17.07 "Lot 6 F146".
"""
import datetime
from psycopg2.extras import RealDictCursor
from core import chei_unice as _chei   # [lotul 10, C73 / U2] numărul dat de aplicație: cursa se reia, nu dă 500

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
    descriere = (corp.get("descriere") or "").strip()
    # [lotul 11, 440] ambele refuzuri deodată: `coduri` = toate, `cod` = primul (contractul vechi)
    coduri = ([] if directie in DIRECTII else ["DIRECTIE_INVALIDA"]) + ([] if descriere else ["DESCRIERE_GOALA"])
    if coduri:
        return {"ok": False, "cod": coduri[0], "coduri": coduri}
    data = (corp.get("data") or "").strip() or datetime.date.today().isoformat()
    an = int(data[:4])
    partener = (corp.get("partener") or "").strip() or None
    document_ref = (corp.get("document_ref") or "").strip() or None
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        def _scrie():
            cur.execute(f"SELECT COALESCE(MAX(numar),0)+1 AS urm FROM {schema}.registratura WHERE an=%s", (an,))
            numar = cur.fetchone()["urm"]
            cur.execute(f"""INSERT INTO {schema}.registratura
                            (directie, numar, an, data, descriere, partener, document_ref, creat_de)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (directie, numar, an, data, descriere, partener, document_ref, creat_de))
            return cur.fetchone()["id"], numar
        # [lotul 10, C73 / U2] numărul de înregistrare îl dă APLICAȚIA (`MAX + 1`): două înregistrări simultane citeau același număr, iar
        # a doua cădea cu 500 pe `registratura_an_numar_unic`. Cursa nu e a omului — se reia cu numărul următor, sub savepoint.
        rid, numar = _chei.reincearca_la_dublura(cur, ("registratura_an_numar_unic",), _scrie, lambda cur, e: _chei.CheieDublata(
            "Registrul de intrări-ieșiri a primit în același timp prea multe înregistrări și numărul nu s-a putut aloca. Nimic nu s-a "
            "scris: salvează din nou."))
    return {"ok": True, "id": rid, "numar": numar, "an": an, "directie": directie}
