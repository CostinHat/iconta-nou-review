# -*- coding: utf-8 -*-
"""Stocuri cantitativ-valorice — strat API. Motorul: core/stocuri_cv.py.
Ieșirile la CMP generează notă ciornă (cont_cheltuiala = cont_stoc)."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import stocuri_cv as _m


def _miscari(cur, schema, articol_id):
    cur.execute(f"""SELECT tip, cantitate, pret_unitar, data, document
                    FROM {schema}.miscari_stoc WHERE articol_id=%s ORDER BY data, id""",
                (articol_id,))
    return [dict(r) for r in cur.fetchall()]


def articole(conn, schema):
    """Articolele cu stocul curent (cantitate, valoare, CMP)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole ORDER BY denumire")
        out = []
        for a in cur.fetchall():
            fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
            if fisa:
                cant, val, cmp = fisa[-1]["sold_cantitate"], fisa[-1]["sold_valoare"], fisa[-1]["cmp"]
            else:
                cant = val = Decimal("0"); cmp = None
            out.append({"id": a["id"], "denumire": a["denumire"], "um": a["um"],
                        "cont_stoc": a["cont_stoc"], "cont_cheltuiala": a["cont_cheltuiala"],
                        "stoc": str(cant), "valoare": str(val),
                        "cmp": str(cmp) if cmp is not None else None})
        return out


def fisa(conn, schema, articol_id):
    """Fișa de magazie a unui articol."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (articol_id,))
        a = cur.fetchone()
        if not a:
            return None
        linii = _m.fisa_magazie(_miscari(cur, schema, articol_id))
    return {"articol": {"id": a["id"], "denumire": a["denumire"], "um": a["um"]},
            "linii": [{"data": str(l["data"]), "tip": l["tip"], "document": l.get("document"),
                       "cantitate": str(l["cantitate"]),
                       "pret_unitar": str(l["pret_unitar"]) if l.get("pret_unitar") else None,
                       "valoare": str(l["valoare"]), "sold_cantitate": str(l["sold_cantitate"]),
                       "sold_valoare": str(l["sold_valoare"]),
                       "cmp": str(l["cmp"]) if l["cmp"] is not None else None}
                      for l in linii]}


def intrare(conn, schema, corp):
    """corp: {articol_id | denumire+um+cont_stoc+cont_cheltuiala, data, cantitate,
    pret_unitar, document?}. Nota de intrare vine din NIR/factură — aici doar mișcarea."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        aid = corp.get("articol_id")
        if not aid:
            cur.execute(f"""INSERT INTO {schema}.articole (denumire, um, cont_stoc, cont_cheltuiala)
                            VALUES (%s,%s,%s,%s) RETURNING id""",
                        (corp["denumire"], corp.get("um", "buc"),
                         corp.get("cont_stoc", "371"), corp.get("cont_cheltuiala", "607")))
            aid = cur.fetchone()["id"]
        cant = Decimal(str(corp["cantitate"]))
        pret = Decimal(str(corp["pret_unitar"]))
        if cant <= 0 or pret < 0:
            return {"eroare": "cantitate/pret invalide"}
        val = (cant * pret).quantize(Decimal("0.01"))
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, pret_unitar, valoare, document)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s) RETURNING id""",
                    (aid, corp["data"], cant, pret, val, corp.get("document")))
        mid = cur.fetchone()["id"]
    conn.commit()
    return {"id": mid, "articol_id": aid, "valoare": str(val)}


def iesire(conn, schema, corp):
    """corp: {articol_id, data, cantitate, document?}. Valoare la CMP + notă ciornă
    cont_cheltuiala = cont_stoc."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        try:
            r = _m.valoare_iesire(_miscari(cur, schema, a["id"]), None, corp["cantitate"])
        except ValueError as e:
            return {"eroare": str(e)}
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                        VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                    (corp["data"], f"Iesire stoc {a['denumire']} x{corp['cantitate']}"[:200]))
        iid = cur.fetchone()["id"]
        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                        (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                    (iid, a["cont_cheltuiala"], a["cont_stoc"], r["valoare"]))
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, valoare, document, inregistrare_id)
                        VALUES (%s,%s,'iesire',%s,%s,%s,%s) RETURNING id""",
                    (a["id"], corp["data"], Decimal(str(corp["cantitate"])), r["valoare"],
                     corp.get("document"), iid))
        mid = cur.fetchone()["id"]
    conn.commit()
    return {"id": mid, "cmp": str(r["cmp"]), "valoare": str(r["valoare"]),
            "nota": f"{a['cont_cheltuiala']}={a['cont_stoc']}", "inregistrare_id": iid}
