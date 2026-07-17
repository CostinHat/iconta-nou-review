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
                        (articol_id, data, tip, cantitate, pret_unitar, valoare, document, locatie)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s) RETURNING id""",
                    (aid, corp["data"], cant, pret, val, corp.get("document"),
                     corp.get("locatie") or None))
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
                        (articol_id, data, tip, cantitate, valoare, document, inregistrare_id, locatie)
                        VALUES (%s,%s,'iesire',%s,%s,%s,%s,%s) RETURNING id""",
                    (a["id"], corp["data"], Decimal(str(corp["cantitate"])), r["valoare"],
                     corp.get("document"), iid, corp.get("locatie") or None))
        mid = cur.fetchone()["id"]
    conn.commit()
    return {"id": mid, "cmp": str(r["cmp"]), "valoare": str(r["valoare"]),
            "nota": f"{a['cont_cheltuiala']}={a['cont_stoc']}", "inregistrare_id": iid}


def inventar(conn, schema, corp):
    """corp: {data, linii: [{articol_id, faptic}]}. Diferente la CMP:
    plus -> intrare + nota 371=607 (ciorna); minus -> iesire + nota 607=371 (ciorna).
    Temei: OMFP 1802/2014, functiunea conturilor 371/607."""
    rez = []
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for l in corp.get("linii", []):
            cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (l["articol_id"],))
            a = cur.fetchone()
            if not a:
                rez.append({"articol_id": l["articol_id"], "eroare": "articol inexistent"})
                continue
            fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
            scriptic = fisa[-1]["sold_cantitate"] if fisa else Decimal("0")
            cmp = Decimal(str(fisa[-1]["cmp"])) if fisa and fisa[-1]["cmp"] else Decimal("0")
            faptic = Decimal(str(l["faptic"]))
            dif = faptic - scriptic
            if dif == 0:
                rez.append({"articol_id": a["id"], "denumire": a["denumire"], "diferenta": "0"})
                continue
            val = (abs(dif) * cmp).quantize(Decimal("0.01"))
            if dif > 0:
                debit, credit, tip = a["cont_stoc"], a["cont_cheltuiala"], "intrare"
            else:
                if abs(dif) > scriptic:
                    rez.append({"articol_id": a["id"], "eroare": "minus peste stocul scriptic"})
                    continue
                debit, credit, tip = a["cont_cheltuiala"], a["cont_stoc"], "iesire"
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                        (corp["data"], f"Inventar {a['denumire']}: {'plus' if dif > 0 else 'minus'} {abs(dif)}"[:200]))
            iid = cur.fetchone()["id"]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                        (iid, debit, credit, val))
            cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                            (articol_id, data, tip, cantitate, pret_unitar, valoare, document, inregistrare_id)
                            VALUES (%s,%s,%s,%s,%s,%s,'inventar',%s)""",
                        (a["id"], corp["data"], tip, abs(dif),
                         cmp if tip == "intrare" else None, val, iid))
            rez.append({"articol_id": a["id"], "denumire": a["denumire"],
                        "diferenta": str(dif), "valoare": str(val),
                        "nota": f"{debit}={credit}", "inregistrare_id": iid})
    conn.commit()
    return {"rezultate": rez}


def _stoc_locatie(cur, schema, articol_id, locatie):
    """Cantitatea neta a unui articol la o locatie (intrari - iesiri). Pur cantitativ."""
    cur.execute(f"""SELECT COALESCE(SUM(CASE WHEN tip='intrare' THEN cantitate
                    WHEN tip='iesire' THEN -cantitate ELSE 0 END),0) AS q
                    FROM {schema}.miscari_stoc
                    WHERE articol_id=%s AND locatie IS NOT DISTINCT FROM %s""",
                (articol_id, locatie or None))
    return Decimal(str(cur.fetchone()["q"]))


def stoc_pe_locatii(conn, schema, articol_id=None):
    """Stocul CANTITATIV pe fiecare locatie (F138 Tier 1, eticheta descriptiva).
    CMP ramane GLOBAL — aici doar cantitati, nu valorizare per locatie (Tier 3 AMANAT)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        q = f"""SELECT m.articol_id, a.denumire, a.um, m.locatie,
                   SUM(CASE WHEN m.tip='intrare' THEN m.cantitate
                            WHEN m.tip='iesire' THEN -m.cantitate ELSE 0 END) AS cantitate
                FROM {schema}.miscari_stoc m JOIN {schema}.articole a ON a.id=m.articol_id"""
        params = []
        if articol_id:
            q += " WHERE m.articol_id=%s"
            params.append(articol_id)
        q += """ GROUP BY m.articol_id, a.denumire, a.um, m.locatie
                 HAVING SUM(CASE WHEN m.tip='intrare' THEN m.cantitate
                                 WHEN m.tip='iesire' THEN -m.cantitate ELSE 0 END) <> 0
                 ORDER BY a.denumire, m.locatie NULLS FIRST"""
        cur.execute(q, params)
        return [{"articol_id": r["articol_id"], "denumire": r["denumire"], "um": r["um"],
                 "locatie": r["locatie"] or "(nespecificat)", "cantitate": str(r["cantitate"])}
                for r in cur.fetchall()]


def transfer(conn, schema, corp):
    """corp: {articol_id, din_locatie, in_locatie, cantitate, data, document?}.
    Transfer FIZIC intre locatii: iesire din sursa + intrare in destinatie, ambele la
    CMP-ul GLOBAL curent. NU genereaza nota contabila (nu e consum/achizitie) si e NEUTRU
    pe CMP si pe D406 (net zero cantitate+valoare). F138 Tier 1."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        din = (corp.get("din_locatie") or "").strip() or None
        catre = (corp.get("in_locatie") or "").strip() or None
        if din == catre:
            return {"eroare": "locatia sursa si destinatie sunt identice"}
        cant = Decimal(str(corp["cantitate"]))
        if cant <= 0:
            return {"eroare": "cantitate invalida"}
        disp = _stoc_locatie(cur, schema, a["id"], din)
        if cant > disp:
            return {"eroare": f"transfer {cant} peste stocul {disp} la locatia sursa"}
        try:
            r = _m.valoare_iesire(_miscari(cur, schema, a["id"]), None, cant)
        except ValueError as e:
            return {"eroare": str(e)}
        doc = (corp.get("document") or f"transfer {din or '-'}->{catre or '-'}")[:100]
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, valoare, document, locatie)
                        VALUES (%s,%s,'iesire',%s,%s,%s,%s)""",
                    (a["id"], corp["data"], cant, r["valoare"], doc, din))
        cur.execute(f"""INSERT INTO {schema}.miscari_stoc
                        (articol_id, data, tip, cantitate, pret_unitar, valoare, document, locatie)
                        VALUES (%s,%s,'intrare',%s,%s,%s,%s,%s)""",
                    (a["id"], corp["data"], cant, r["cmp"], r["valoare"], doc, catre))
    conn.commit()
    return {"articol_id": a["id"], "denumire": a["denumire"], "cantitate": str(cant),
            "cmp": str(r["cmp"]), "valoare": str(r["valoare"]),
            "din_locatie": din or "(nespecificat)", "in_locatie": catre or "(nespecificat)"}


def reclasificare(conn, schema, corp):
    """corp: {articol_id, cont_stoc_nou, cont_cheltuiala_nou?, data, document?}.
    Schimba tipul de produs (ex. materie prima 301 -> marfa 371): actualizeaza conturile
    articolului si emite nota de reclasificare a soldului la CMP curent
    (debit cont_stoc_nou = credit cont_stoc_vechi). Cantitatea NU se atinge.
    Temei: OMFP 1802/2014, functiunea conturilor de stoc. F138 (jumatatea usoara)."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT * FROM {schema}.articole WHERE id=%s", (corp["articol_id"],))
        a = cur.fetchone()
        if not a:
            return None
        cont_nou = (corp.get("cont_stoc_nou") or "").strip()
        if not cont_nou:
            return {"eroare": "cont_stoc_nou lipsa"}
        if cont_nou == a["cont_stoc"]:
            return {"eroare": "contul de stoc e neschimbat"}
        chelt_nou = (corp.get("cont_cheltuiala_nou") or "").strip() or a["cont_cheltuiala"]
        fisa = _m.fisa_magazie(_miscari(cur, schema, a["id"]))
        val = Decimal(str(fisa[-1]["sold_valoare"])) if fisa else Decimal("0")
        iid = None
        if val > 0:
            cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                            VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                        (corp["data"],
                         f"Reclasificare {a['denumire']}: {a['cont_stoc']}->{cont_nou}"[:200]))
            iid = cur.fetchone()["id"]
            cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                            (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                        (iid, cont_nou, a["cont_stoc"], val))
        cur.execute(f"UPDATE {schema}.articole SET cont_stoc=%s, cont_cheltuiala=%s WHERE id=%s",
                    (cont_nou, chelt_nou, a["id"]))
    conn.commit()
    return {"articol_id": a["id"], "denumire": a["denumire"],
            "cont_stoc_vechi": a["cont_stoc"], "cont_stoc": cont_nou,
            "cont_cheltuiala": chelt_nou, "valoare_reclasificata": str(val),
            "nota": (f"{cont_nou}={a['cont_stoc']}" if val > 0 else None),
            "inregistrare_id": iid}
