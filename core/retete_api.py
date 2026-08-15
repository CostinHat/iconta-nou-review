# -*- coding: utf-8 -*-
"""Retetar - strat DB. Consum pe reteta -> iesiri miscari_stoc la CMP + nota ciorna
(cont_cheltuiala per articol = cont_stoc, ex. 371=371 la marfa; tipic 601/607=3xx)."""
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import retete as _r
from core import stocuri_cv as _m


def _fara_decimal(x):
    if isinstance(x, Decimal):
        return str(x)
    if isinstance(x, dict):
        return {k: _fara_decimal(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_fara_decimal(v) for v in x]
    return x


def _miscari(cur, schema, articol_id):
    cur.execute(f"""SELECT data, tip, cantitate, pret_unitar FROM {schema}.miscari_stoc
                    WHERE articol_id=%s ORDER BY data, id""", (articol_id,))
    return [dict(r) for r in cur.fetchall()]


def _cmp_si_stoc(cur, schema, articol_id):
    fisa = _m.fisa_magazie(_miscari(cur, schema, articol_id))
    if not fisa:
        return Decimal("0"), Decimal("0")
    u = fisa[-1]
    return Decimal(str(u["cmp"] or 0)), Decimal(str(u["sold_cantitate"] or 0))
def _cmp_la_data(cur, schema, articol_id, data_iso):
    """CMP la o data: fisa pe miscarile pana la data inclusiv. [gv_crono]"""
    pana = [m for m in _miscari(cur, schema, articol_id) if str(m["data"]) <= data_iso]
    fisa = _m.fisa_magazie(pana)
    if not fisa or not fisa[-1]["sold_cantitate"]:
        return Decimal("0")
    return Decimal(str(fisa[-1]["cmp"] or 0))
def _valideaza_iesire_la_data(cur, schema, articol_id, data_iso, cantitate):
    """Replay complet cu iesirea noua inserata cronologic - prinde si spargerea
    miscarilor ULTERIOARE de o iesire antedatata. [gv_crono]"""
    miscari = _miscari(cur, schema, articol_id)
    pana = [m for m in miscari if str(m["data"]) <= data_iso]
    dupa = [m for m in miscari if str(m["data"]) > data_iso]
    noua = {"data": data_iso, "tip": "iesire", "cantitate": cantitate, "pret_unitar": None}
    _m.fisa_magazie(pana + [noua] + dupa)


def lista(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT r.*, COALESCE(json_agg(json_build_object(
                            'id', l.id, 'articol_id', l.articol_id, 'cantitate', l.cantitate,
                            'denumire', a.denumire, 'um', a.um)
                          ORDER BY l.id) FILTER (WHERE l.id IS NOT NULL), '[]') AS linii
                        FROM {schema}.retete r
                        LEFT JOIN {schema}.retete_linii l ON l.reteta_id = r.id
                        LEFT JOIN {schema}.articole a ON a.id = l.articol_id
                        GROUP BY r.id ORDER BY r.id""")
        ret = [dict(r) for r in cur.fetchall()]
        for r in ret:
            linii = []
            for l in (r["linii"] or []):
                cmp, _ = _cmp_si_stoc(cur, schema, l["articol_id"])
                l["cmp"] = str(cmp)
                linii.append(l)
            fc = _r.food_cost([{"articol_id": l["articol_id"], "cantitate": l["cantitate"],
                                "cmp": l["cmp"]} for l in linii], r.get("pret_fara_tva"))
            r["food_cost"] = fc
    return _fara_decimal({"retete": ret})


def _ingrediente_campuri_lipsa(linii):
    """Ingrediente goale -> [{camp, eticheta}]. Obligatorii: articol ales + cantitate>0 (aceleasi criterii pe
    care frontendul le filtra tacit inainte). id camp = rt-l{i}-{camp}, i = pozitia in lista (cap.24)."""
    lipsa = []
    for i, l in enumerate(linii):
        n = i + 1
        if not l.get("articol_id"):
            lipsa.append({"camp": "rt-l%d-articol" % i, "eticheta": "Ingredient %d: articol" % n})
        try:
            ok = float(l.get("cantitate") or 0) > 0
        except (TypeError, ValueError):
            ok = False
        if not ok:
            lipsa.append({"camp": "rt-l%d-cantitate" % i, "eticheta": "Ingredient %d: cantitate" % n})
    return lipsa


def salveaza(conn, schema, corp):
    """corp: {id?, denumire, pret_fara_tva, linii:[{articol_id, cantitate}]}. Upsert.
    [cap.24 regula 2] validare per-linie AUTORITARA inainte de scriere: un ingredient inceput incomplet se
    raporteaza langa campul lui (rt-l{i}-..), nu il filtreaza tacit frontendul."""
    linii = corp.get("linii") or []
    if not (corp.get("denumire") or "").strip():
        return {"eroare": "Denumirea retetei e obligatorie."}
    if not linii:
        return {"eroare": "Adaugă cel puțin un ingredient."}
    lipsa = _ingrediente_campuri_lipsa(linii)
    if lipsa:
        return {"eroare": "Completează ingredientele: " + "; ".join(x["eticheta"] for x in lipsa),
                "erori_campuri": [{"camp": x["camp"], "mesaj": x["eticheta"]} for x in lipsa]}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        if corp.get("id"):
            cur.execute(f"""UPDATE {schema}.retete SET denumire=%s, pret_fara_tva=%s
                            WHERE id=%s RETURNING id""",
                        (corp["denumire"], corp.get("pret_fara_tva") or 0, corp["id"]))
            rid = cur.fetchone()["id"]
            cur.execute(f"DELETE FROM {schema}.retete_linii WHERE reteta_id=%s", (rid,))
        else:
            cur.execute(f"""INSERT INTO {schema}.retete (denumire, pret_fara_tva)
                            VALUES (%s,%s) RETURNING id""",
                        (corp["denumire"], corp.get("pret_fara_tva") or 0))
            rid = cur.fetchone()["id"]
        for l in corp.get("linii", []):
            cur.execute(f"""INSERT INTO {schema}.retete_linii (reteta_id, articol_id, cantitate)
                            VALUES (%s,%s,%s)""", (rid, l["articol_id"], l["cantitate"]))
    conn.commit()
    return {"id": rid}


def sterge(conn, schema, reteta_id):
    with conn.cursor() as cur:
        cur.execute(f"DELETE FROM {schema}.retete WHERE id=%s", (reteta_id,))
    conn.commit()
    return {"ok": True}


def descarca(conn, schema, corp):
    """corp: {reteta_id, portii, data}. Iesiri la CMP per ingredient + nota ciorna cumulata
    (per cont: cont_cheltuiala = cont_stoc al articolului)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.retete WHERE id=%s", (corp["reteta_id"],))
        ret = cur.fetchone()
        if not ret:
            raise ValueError("reteta inexistenta")
        cur.execute(f"""SELECT l.*, a.denumire, a.cont_stoc, a.cont_cheltuiala
                        FROM {schema}.retete_linii l
                        JOIN {schema}.articole a ON a.id = l.articol_id
                        WHERE l.reteta_id=%s ORDER BY l.id""", (corp["reteta_id"],))
        linii_r = [dict(r) for r in cur.fetchall()]
        if not linii_r:
            raise ValueError("reteta fara ingrediente")
        import datetime as _dt
        d = corp.get("data") or _dt.date.today().isoformat()  # [gv_fix] fara data -> azi
        pentru_motor = []
        for l in linii_r:
            l["cmp"] = _cmp_la_data(cur, schema, l["articol_id"], d)
            pentru_motor.append({"articol_id": l["articol_id"],
                                 "cantitate": l["cantitate"], "cmp": l["cmp"]})
        cons = _r.consum_pe_portii(pentru_motor, corp["portii"])
        pe_art = {c["articol_id"]: c for c in cons["linii"]}
        for l in linii_r:
            c = pe_art[l["articol_id"]]
            try:  # [gv_crono] iesirea la data ei nu are voie sa sparga fisa
                _valideaza_iesire_la_data(cur, schema, l["articol_id"], d, c["cantitate"])
            except ValueError as e:
                raise ValueError(f"stoc insuficient la {l['denumire']}: {e}")
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                        VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                    (d, f"Consum reteta {ret['denumire']} x{corp['portii']}"[:200]))
        iid = cur.fetchone()["id"]
        pe_cont = {}
        for l in linii_r:
            c = pe_art[l["articol_id"]]
            cheie = (l["cont_cheltuiala"], l["cont_stoc"])
            pe_cont[cheie] = pe_cont.get(cheie, Decimal("0")) + c["valoare"]
            cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                            (articol_id, data, tip, cantitate, valoare, document, inregistrare_id)
                            VALUES (%s,%s,'iesire',%s,%s,'reteta',%s)""",
                        (l["articol_id"], d, c["cantitate"], c["valoare"], iid))
        for (deb, cred), suma in pe_cont.items():
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma)
                            VALUES (%s,%s,%s,%s)""", (iid, deb, cred, suma))
    conn.commit()
    return _fara_decimal({"inregistrare_id": iid, "cost_total": cons["cost_total"],
                          "linii": cons["linii"]})
