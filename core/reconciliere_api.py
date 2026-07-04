# -*- coding: utf-8 -*-
"""Reconciliere bancară — strat API (tipar stat_plata_api: funcții conn+schema).
Motorul de matching e în core/reconciliere.py (pur, testat)."""
import json
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import reconciliere as _m

CONT_CLIENTI, CONT_FURNIZORI = "4111", "401"


def _data_iso(v):
    """dd.mm.yyyy -> yyyy-mm-dd; lasa neschimbat ce e deja ISO/date."""
    if isinstance(v, str) and len(v) == 10 and v[2] == "." and v[5] == ".":
        return f"{v[6:]}-{v[3:5]}-{v[:2]}"
    return v


def _cont_banca(valuta):
    return "5124" if valuta else "5121"


def facturi_deschise(conn, schema):
    """Facturi cu sold > 0. Sold = total_lei(±total) - sume decontate prin
    inregistrari legate cu factura_id (credit 4111 la emise / debit 401 la primite)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""
            SELECT f.id, f.tert_cui, f.directie, f.data_emitere,
                   COALESCE(f.total_lei, f.total) AS total,
                   COALESCE((SELECT SUM(l.suma)
                             FROM {schema}.inregistrari i
                             JOIN {schema}.inregistrari_linii l ON l.inregistrare_id = i.id
                             WHERE i.factura_id = f.id
                               AND ((f.directie='emisa'   AND l.cont_credit=%s)
                                 OR (f.directie='primita' AND l.cont_debit=%s))), 0) AS decontat,
                   COALESCE((SELECT SUM(COALESCE(st.total_lei, st.total))
                             FROM {schema}.facturi st
                             WHERE st.storno_din_id = f.id), 0) AS storno
            FROM {schema}.facturi f
            WHERE f.status NOT IN ('anulata','storno')
              AND f.storno_din_id IS NULL
        """, (CONT_CLIENTI, CONT_FURNIZORI))
        rez = []
        for r in cur.fetchall():
            sold = Decimal(r["total"] or 0) - Decimal(r["decontat"] or 0) + Decimal(r["storno"] or 0)
            if sold > Decimal("0.01"):
                rez.append({"id": r["id"], "tert_cui": r["tert_cui"],
                            "directie": r["directie"],
                            "data_emitere": r["data_emitere"], "sold": sold})
        return rez


def importa_extras(conn, schema, tranzactii, fisier=""):
    """Persistă liniile de extras + rulează matching-ul. Întoarce liniile cu rezultat."""
    facturi = facturi_deschise(conn, schema)
    linii = [{"suma": Decimal(str(abs(t.get("suma", 0)))),
              "tip": "incasare" if t.get("suma", 0) > 0 else "plata",
              "cui": t.get("cui"), "descriere": t.get("detalii", ""),
              "data": _data_iso(t.get("data"))} for t in tranzactii]
    rezultate = _m.potriveste_extras(linii, facturi)
    out = []
    with conn.cursor() as cur:
        for t, ln, rez in zip(tranzactii, linii, rezultate):
            aloc = {"status_match": rez["status"], "motiv": rez["motiv"],
                    "alocari": [{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                for a in rez["alocari"]]}
            status = "potrivit" if rez["status"] in ("verde", "galben") else "nou"
            cur.execute(f"""
                INSERT INTO {schema}.extras_linii
                  (data, descriere, suma, valuta, tip, cui_detectat, status,
                   alocari, nota_propusa, fisier_sursa)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (ln["data"], ln["descriere"], ln["suma"], bool(t.get("valuta")),
                  ln["tip"], ln["cui"], status, json.dumps(aloc),
                  json.dumps(t.get("nota"), default=str) if t.get("nota") else None, fisier))
            out.append({"id": cur.fetchone()[0], "data": str(ln["data"]),
                        "descriere": ln["descriere"], "suma": str(ln["suma"]),
                        "tip": ln["tip"], "cui": ln["cui"], "status": status, **aloc})
    conn.commit()
    return out


def lista(conn, schema, status=None):
    """Liniile de extras cu detaliile facturilor alocate (pentru UI)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"SELECT * FROM {schema}.extras_linii"
        if status:
            cur.execute(q + " WHERE status=%s ORDER BY data, id", (status,))
        else:
            cur.execute(q + " ORDER BY data, id")
        linii = cur.fetchall()
        ids = set()
        for l in linii:
            for a in (l.get("alocari") or {}).get("alocari", []):
                ids.add(a["factura_id"])
        facturi = {}
        if ids:
            cur.execute(f"""SELECT id, numar, serie, data_emitere, tert_nume, tert_cui,
                            COALESCE(total_lei, total) AS total
                            FROM {schema}.facturi WHERE id = ANY(%s)""", (list(ids),))
            facturi = {f["id"]: f for f in cur.fetchall()}
        for l in linii:
            l["suma"] = str(l["suma"])
            l["data"] = str(l["data"])
            l["creat_la"] = str(l["creat_la"])
            for a in (l.get("alocari") or {}).get("alocari", []):
                f = facturi.get(a["factura_id"])
                if f:
                    a["factura"] = {"numar": f["numar"], "serie": f["serie"],
                                    "data": str(f["data_emitere"]),
                                    "tert": f["tert_nume"], "total": str(f["total"])}
        return linii


def conteaza(conn, schema, linie_id, alocari=None):
    """Contează o linie: câte o înregistrare per factură alocată.
    incasare: 5121/5124 = 4111; plata: 401 = 5121/5124.
    alocari=None → folosește alocările din matching."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.extras_linii WHERE id=%s", (linie_id,))
        l = cur.fetchone()
        if not l:
            return None
        if l["status"] == "contat":
            return {"eroare": "linia e deja contata"}
        aloc = alocari or (l.get("alocari") or {}).get("alocari", [])
        if not aloc:
            np = l.get("nota_propusa") or {}
            if not (np.get("debit") and np.get("credit")):
                return {"eroare": "fara alocari si fara nota propusa; alege facturile"}
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                VALUES (%s,%s,'banca','ciorna') RETURNING id
            """, (l["data"], (l["descriere"] or "")[:200] or "operatiune bancara"))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, np["debit"], np["credit"], Decimal(str(np.get("suma") or l["suma"]))))
            cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                        (json.dumps({**(l.get("alocari") or {}), "inregistrari_ids": [iid]}), linie_id))
            conn.commit()
        banca = _cont_banca(l["valuta"])
        debit, credit = (banca, CONT_CLIENTI) if l["tip"] == "incasare" else (CONT_FURNIZORI, banca)
        create = []
        for a in aloc:
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari (data, factura_id, descriere, sursa, status)
                VALUES (%s,%s,%s,'banca','ciorna') RETURNING id
            """, (l["data"], a["factura_id"],
                  (l["descriere"] or "")[:200] or "operatiune bancara"))
            iid = cur.fetchone()["id"]
            cur.execute(f"""
                INSERT INTO {schema}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma)
                VALUES (%s,%s,%s,%s)
            """, (iid, debit, credit, Decimal(str(a["suma"]))))
            # [tvai_v1] TVA la incasare: exigibilitate la incasare/plata (art.282(3),(8))
            cur.execute(f"SELECT COALESCE(tva_la_incasare, false) AS b FROM {schema}.firma_profil WHERE id = 1")
            if (cur.fetchone() or {}).get("b"):
                from core import tva_incasare as _tv
                cur.execute(f"""SELECT f.directie, COALESCE((SELECT cota_tva FROM {schema}.factura_linii
                                        WHERE factura_id = f.id LIMIT 1), 21) AS cota
                                FROM {schema}.facturi f WHERE f.id = %s""", (a["factura_id"],))
                _f = cur.fetchone()
                if _f:
                    _tva = _tv.tva_din_incasare(a["suma"], _f["cota"])
                    if _tva > 0:
                        _deb, _cred = ("4428", "4427") if _f["directie"] == "emisa" else ("4426", "4428")
                        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                                        (inregistrare_id, cont_debit, cont_credit, suma)
                                        VALUES (%s,%s,%s,%s)""", (iid, _deb, _cred, _tva))
            create.append(iid)
        cur.execute(f"UPDATE {schema}.extras_linii SET status='contat', alocari=%s WHERE id=%s",
                    (json.dumps({**(l.get("alocari") or {}),
                                 "alocari": [{"factura_id": a["factura_id"], "suma": str(a["suma"])}
                                             for a in aloc],
                                 "inregistrari_ids": create}), linie_id))
    conn.commit()
    return {"inregistrari": create, "nota": f"{debit}={credit}"}


def facturi_deschise_detalii(conn, schema):
    """Facturile deschise cu detalii pentru picker-ul din UI."""
    fd = facturi_deschise(conn, schema)
    if not fd:
        return []
    ids = [f["id"] for f in fd]
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT id, numar, serie, tert_nume FROM {schema}.facturi WHERE id=ANY(%s)", (ids,))
        det = {r["id"]: r for r in cur.fetchall()}
    return [{"id": f["id"], "tert_cui": f["tert_cui"], "directie": f["directie"],
             "data_emitere": str(f["data_emitere"]), "sold": str(f["sold"]),
             "numar": det[f["id"]]["numar"], "serie": det[f["id"]]["serie"],
             "tert_nume": det[f["id"]]["tert_nume"]} for f in fd]
