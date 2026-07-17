# -*- coding: utf-8 -*-
"""core/rapoarte_comerciale_api.py — F144 v1: rapoarte comerciale READ-ONLY.

Perimetru v1 (agreat 17.07.2026): doar ce se poate construi corect pe schema
actuala, citind exclusiv din `facturi`. Trei rapoarte:
  - vanzari pe PARTENER (net, pe perioada);
  - durata medie de incasare (din data reala a decontarii, nu platita_la);
  - fisa client/furnizor (facturi + decontat + sold, pe un partener).

NU livreaza profit-pe-produs / vanzari-pe-articol / vanzari-pe-agent: vanzarea
si descarcarea gestiunii sunt acte deconectate prin design (miscari_stoc fara
factura_id; factura_linii fara articol_id). Vezi DECIZII.md 17.07 "F144 profit-
pe-produs RAMAS DESCHIS" + DE_FACUT.md CARENTE pct.4.

Conventia de sold/storno e IDENTICA cu core/reconciliere_api.py (sursa unica):
  sold = COALESCE(total_lei,total) - decontat + storno.
  storno = facturi cu storno_din_id setat, cu totaluri NEGATIVE (linii negate);
  se exclud din randul principal si se aduna inapoi (negative -> reduc valoarea).
  decontat emise = SUM linii cu cont_credit=4111; primite = cont_debit=401.
"""
from decimal import Decimal
from psycopg2.extras import RealDictCursor

CONT_CLIENTI, CONT_FURNIZORI = "4111", "401"


def _f(v):
    """Decimal/None -> float rotunjit la 2 zecimale (afisare prin bani() in UI)."""
    return round(float(v or 0), 2)


def vanzari_pe_partener(conn, schema, de, pana):
    """Vanzari NETE (fara TVA) grupate pe partener, pe perioada [de, pana].
    Doar facturi EMISE tip='factura', fara anulate/storno; storno-ul aferent
    se scade (net negativ). Sortare descrescatoare dupa net."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.tert_cui AS cui,
                   MAX(f.tert_nume) AS nume,
                   COUNT(*) AS nr,
                   SUM(
                     (COALESCE(f.total_lei, f.total) - COALESCE(f.tva_lei, f.tva))
                     + COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total)
                                          - COALESCE(st.tva_lei, st.tva))
                                 FROM {schema}.facturi st
                                 WHERE st.storno_din_id = f.id), 0)
                   ) AS net
            FROM {schema}.facturi f
            WHERE f.directie = 'emisa' AND f.tip = 'factura'
              AND f.status NOT IN ('anulata', 'storno')
              AND f.storno_din_id IS NULL
              AND f.data_emitere BETWEEN %s AND %s
            GROUP BY f.tert_cui
            ORDER BY net DESC NULLS LAST
        """, (de, pana))
        randuri = [{"cui": r["cui"], "nume": r["nume"] or "(fara nume)",
                    "nr": r["nr"], "net": _f(r["net"])} for r in cur.fetchall()]
    total = _f(sum(Decimal(str(r["net"])) for r in randuri))
    return {"parteneri": randuri, "total_net": total}


def durata_medie_incasare(conn, schema, de, pana):
    """Durata medie (zile) de la emitere la incasarea EFECTIVA, pe facturi emise
    din perioada care sunt integral incasate. Data incasarii = ultima decontare
    (nota cu cont_credit=4111), NU `platita_la` (care prinde doar platile online
    prin provider si ar da un numar partinitor)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            WITH e AS (
              SELECT f.id, f.data_emitere,
                     COALESCE(f.total_lei, f.total)
                       - COALESCE((SELECT SUM(l.suma)
                                   FROM {schema}.inregistrari i
                                   JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                                   WHERE i.factura_id = f.id AND l.cont_credit = %s), 0)
                       + COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total))
                                   FROM {schema}.facturi st
                                   WHERE st.storno_din_id = f.id), 0) AS sold,
                     (SELECT MAX(i.data)
                        FROM {schema}.inregistrari i
                        JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                        WHERE i.factura_id = f.id AND l.cont_credit = %s) AS data_incasare
              FROM {schema}.facturi f
              WHERE f.directie = 'emisa' AND f.tip = 'factura'
                AND f.status NOT IN ('anulata', 'storno')
                AND f.storno_din_id IS NULL
                AND f.data_emitere BETWEEN %s AND %s
            )
            SELECT AVG(data_incasare - data_emitere) AS zile, COUNT(*) AS nr
            FROM e
            WHERE data_incasare IS NOT NULL AND sold <= 0.01
        """, (CONT_CLIENTI, CONT_CLIENTI, de, pana))
        r = cur.fetchone() or {}
    zile = r.get("zile")
    return {"zile_medii": round(float(zile), 1) if zile is not None else None,
            "nr_facturi": r.get("nr") or 0}


def lista_parteneri(conn, schema):
    """Partenerii distincti din facturi (ambele directii), pentru selectorul de fisa."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT tert_cui AS cui, MAX(tert_nume) AS nume
            FROM {schema}.facturi
            WHERE tert_cui IS NOT NULL AND tert_cui <> ''
            GROUP BY tert_cui
            ORDER BY MAX(tert_nume)
        """)
        return [{"cui": r["cui"], "nume": r["nume"] or r["cui"]} for r in cur.fetchall()]


def fisa_partener(conn, schema, cui, de, pana):
    """Fisa unui partener (dupa CUI): facturile lui (ambele directii) din perioada,
    fiecare cu decontat si sold (conventia reconciliere), + sumar. Read-only."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.numar, f.data_emitere, f.directie, f.tert_nume,
                   COALESCE(f.total_lei, f.total) AS total,
                   COALESCE((SELECT SUM(l.suma)
                             FROM {schema}.inregistrari i
                             JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                             WHERE i.factura_id = f.id
                               AND ((f.directie = 'emisa'   AND l.cont_credit = %s)
                                 OR (f.directie = 'primita' AND l.cont_debit  = %s))), 0) AS decontat,
                   COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total))
                             FROM {schema}.facturi st
                             WHERE st.storno_din_id = f.id), 0) AS storno
            FROM {schema}.facturi f
            WHERE f.tert_cui = %s AND f.tip = 'factura'
              AND f.status NOT IN ('anulata', 'storno')
              AND f.storno_din_id IS NULL
              AND f.data_emitere BETWEEN %s AND %s
            ORDER BY f.data_emitere, f.id
        """, (CONT_CLIENTI, CONT_FURNIZORI, cui, de, pana))
        facturi = []
        s_fact = s_dec = s_sold = Decimal("0")
        nume = None
        for r in cur.fetchall():
            nume = nume or r["tert_nume"]
            total = Decimal(r["total"] or 0)
            dec = Decimal(r["decontat"] or 0)
            sold = total - dec + Decimal(r["storno"] or 0)
            s_fact += total; s_dec += dec; s_sold += sold
            facturi.append({
                "id": r["id"], "numar": r["numar"],
                "data": r["data_emitere"].isoformat() if r["data_emitere"] else None,
                "directie": r["directie"], "total": _f(total),
                "decontat": _f(dec), "sold": _f(sold),
                "stare": "achitata" if sold <= Decimal("0.01") else "deschisa",
            })
    return {"partener": {"cui": cui, "nume": nume or cui},
            "facturi": facturi,
            "sumar": {"nr": len(facturi), "facturat": _f(s_fact),
                      "decontat": _f(s_dec), "sold": _f(s_sold)}}
