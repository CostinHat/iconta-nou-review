# -*- coding: utf-8 -*-
"""Facturi recurente: emitere lunara automata din sabloane (cron zilnic).
Regula: sablon activ, zi_emitere <= azi.day, ultima_emitere nu e in luna curenta -> emite."""
import json
import datetime
from psycopg2.extras import RealDictCursor
from core import facturi_api


def lista(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT id, client_id, tert_nume, tert_cui, linii, zi_emitere,
                               moneda, activ, ultima_emitere
                        FROM {schema}.facturi_recurente ORDER BY id""")
        rows = [dict(r) for r in cur.fetchall()]
    for r in rows:
        if isinstance(r["linii"], str):
            r["linii"] = json.loads(r["linii"])
        if r["ultima_emitere"]:
            r["ultima_emitere"] = str(r["ultima_emitere"])
    return rows


def adauga(conn, schema, corp):
    linii = corp.get("linii") or []
    if not linii:
        return {"eroare": "cel puțin o linie"}
    if not (corp.get("tert_nume") or corp.get("client_id")):
        return {"eroare": "beneficiar obligatoriu"}
    zi = int(corp.get("zi_emitere") or 1)
    if not 1 <= zi <= 28:
        return {"eroare": "zi_emitere între 1 și 28"}
    # [cap.24 regula 2] validare per-linie AUTORITARA: un rand incomplet se raporteaza langa campul lui
    # (fr-l{i}-..), nu il filtreaza tacit frontendul. Aceleasi criterii (denumire nevida + cantitate>0),
    # din aceeasi functie ca emitere (fara oglinda care drifteaza, cap.24 regula 4).
    lipsa = facturi_api.linii_campuri_lipsa(linii, prefix="fr-l")
    if lipsa:
        return {"eroare": "Completează liniile: " + "; ".join(x["eticheta"] for x in lipsa),
                "erori_campuri": [{"camp": x["camp"], "mesaj": x["eticheta"]} for x in lipsa]}
    with conn.cursor() as cur:
        cur.execute(f"""INSERT INTO {schema}.facturi_recurente
            (client_id, tert_nume, tert_cui, linii, zi_emitere, moneda)
            VALUES (%s,%s,%s,%s,%s,%s) RETURNING id""",
            (corp.get("client_id"), corp.get("tert_nume"), corp.get("tert_cui"),
             json.dumps(linii), zi, corp.get("moneda", "RON")))
        rid = cur.fetchone()[0]
    conn.commit()
    return {"id": rid}


def comuta(conn, schema, sablon_id, activ):
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.facturi_recurente SET activ=%s WHERE id=%s RETURNING id",
                    (activ, sablon_id))
        if not cur.fetchone():
            return {"eroare": "sablon inexistent"}
    conn.commit()
    return {"id": sablon_id, "activ": activ}


def sterge(conn, schema, sablon_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.facturi_recurente WHERE id=%s RETURNING id", (sablon_id,))
        if not cur.fetchone():
            return {"eroare": "sablon inexistent"}
    conn.commit()
    return {"sters": sablon_id}


def de_emis(sabloane, azi=None):
    """PURA: filtreaza sabloanele scadente azi. sabloane: [{id, activ, zi_emitere, ultima_emitere}]."""
    azi = azi or datetime.date.today()
    rezultat = []
    for s in sabloane:
        if not s.get("activ"):
            continue
        if int(s["zi_emitere"]) > azi.day:
            continue
        ue = s.get("ultima_emitere")
        if ue:
            d = datetime.date.fromisoformat(str(ue)[:10])
            if d.year == azi.year and d.month == azi.month:
                continue
        rezultat.append(s)
    return rezultat


def emite_scadente(conn, schema, azi=None):
    """Emite facturile scadente pentru un tenant. Intoarce lista emisa."""
    from core import facturi_api
    azi = azi or datetime.date.today()
    emise = []
    for s in de_emis(lista(conn, schema), azi):
        try:
            with conn.cursor() as cur:
                cur.execute(f"SET search_path TO {schema}")
            platitor = True
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT platitor_tva FROM firma_profil LIMIT 1")
                    r = cur.fetchone()
                    platitor = bool(r[0]) if r and r[0] is not None else True
            except Exception:
                conn.rollback()
            r = facturi_api.emite_factura(conn, s["linii"], client_id=s.get("client_id"),
                    tert_nume=s.get("tert_nume"), tert_cui=s.get("tert_cui"),
                    data_emitere=azi.isoformat(), moneda=s.get("moneda") or "RON",
                    platitor_tva=platitor)
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {schema}.facturi_recurente SET ultima_emitere=%s WHERE id=%s",
                            (azi, s["id"]))
            conn.commit()
            emise.append({"sablon": s["id"], "factura": r.get("numar")})
        except Exception as e:
            conn.rollback()
            emise.append({"sablon": s["id"], "eroare": str(e)})
    return emise


def _main():
    """Cron zilnic: parcurge toti tenantii activi."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants WHERE activ")
            scheme = [r[0] for r in cur.fetchall()]
    total = []
    for sch in scheme:
        with db.get_conn() as conn:
            rez = emite_scadente(conn, sch)
            if rez:
                total.append({sch: rez})
    print(datetime.datetime.now().isoformat(), "facturi recurente:", total or "nimic de emis")


if __name__ == "__main__":
    from core import cron
    cron.ruleaza("facturi_recurente", _main)
