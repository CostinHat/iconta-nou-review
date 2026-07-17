# -*- coding: utf-8 -*-
"""Stocuri global-valorică — strat API. Motorul: core/stocuri.py.
AI propune (note ciorne), contabilul validează în jurnal."""
import json
from decimal import Decimal
from psycopg2.extras import RealDictCursor
from core import stocuri as _m


def _noteaza(cur, schema, data, descriere, note):
    """Creează câte o înregistrare ciornă per notă propusă. Întoarce id-urile."""
    ids = []
    for n in note:
        if Decimal(str(n["suma"])) <= 0:
            continue
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status)
                        VALUES (%s,%s,'stocuri','ciorna') RETURNING id""",
                    (data, descriere[:200]))
        iid = cur.fetchone()["id"]
        cur.execute(f"""INSERT INTO {schema}.inregistrari_linii
                        (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)""",
                    (iid, n["debit"], n["credit"], Decimal(str(n["suma"]))))
        ids.append(iid)
    return ids


def adauga_nir(conn, schema, nir):
    """nir: {numar, data, furnizor?, cui?, factura_ref?, linii: [...]}.
    Calculează prin motor, persistă NIR + linii, creează notele ciorne."""
    try:
        rez = _m.nir_gv(nir["linii"], transport=nir.get("transport", 0),
                        taxe=nir.get("taxe", 0),
                        cont_transport=nir.get("cont_transport") or "401",
                        cont_taxe=nir.get("cont_taxe") or "446")
    except (ValueError, KeyError) as e:
        return {"eroare": str(e)}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        desc = f"NIR {nir['numar']} {nir.get('furnizor') or ''}".strip()
        ids = _noteaza(cur, schema, nir["data"], desc, rez["note"])
        cur.execute(f"""INSERT INTO {schema}.nir
                        (numar, data, furnizor, cui, factura_ref, cost_total,
                         valoare_vanzare, adaos_total, tva_neexigibila, transport, taxe,
                         inregistrari_ids)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                    (nir["numar"], nir["data"], nir.get("furnizor"), nir.get("cui"),
                     nir.get("factura_ref"), rez["cost_total"], rez["valoare_vanzare"],
                     rez["adaos_total"], rez["tva_neexigibila"], rez["transport"], rez["taxe"],
                     json.dumps(ids)))
        nid = cur.fetchone()["id"]
        for l in rez["linii"]:
            cur.execute(f"""INSERT INTO {schema}.nir_linii
                            (nir_id, denumire, cantitate, pret_achizitie, pret_vanzare, cota_tva)
                            VALUES (%s,%s,%s,%s,%s,%s)""",
                        (nid, l["denumire"], Decimal(str(l["cantitate"])),
                         Decimal(str(l["pret_achizitie"])), Decimal(str(l["pret_vanzare"])),
                         Decimal(str(l.get("cota_tva", 21)))))
    conn.commit()
    return {"id": nid, "inregistrari": ids,
            "cost_total": str(rez["cost_total"]), "cost_baza_total": str(rez["cost_baza_total"]),
            "transport": str(rez["transport"]), "taxe": str(rez["taxe"]),
            "adaos_total": str(rez["adaos_total"]),
            "tva_neexigibila": str(rez["tva_neexigibila"]),
            "valoare_vanzare": str(rez["valoare_vanzare"])}


def lista_nir(conn, schema, an, luna):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT * FROM {schema}.nir
                        WHERE date_trunc('month', data) = %s ORDER BY data, id""",
                    (f"{an}-{luna:02d}-01",))
        out = []
        for r in cur.fetchall():
            out.append({k: (str(v) if isinstance(v, Decimal) or hasattr(v, "isoformat") else v)
                        for k, v in r.items()})
        return out


def _rulaj(cur, schema, cont, parte, pana_exclusiv, de_la=None, surse=None):
    """Rulajul unui cont (debit sau credit) pe note validate, in [de_la, pana)."""
    col = "cont_debit" if parte == "debit" else "cont_credit"
    q = f"""SELECT COALESCE(SUM(l.suma),0) FROM {schema}.inregistrari_linii l
            JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
            WHERE l.{col} = %s AND i.status='validata' AND i.data < %s"""
    p = [cont, pana_exclusiv]
    if surse:
        q += " AND i.sursa = ANY(%s)"; p.append(list(surse))
    if de_la:
        q += " AND i.data >= %s"; p.append(de_la)
    cur.execute(q, p)
    return Decimal(cur.fetchone()[0] or 0)


def descarca_luna(conn, schema, an, luna):
    """Descărcarea gestiunii pe luna dată, din rulajele reale (note validate).
    Cumulat de la 1 ianuarie (OMFP 1802); soldurile inițiale de exercițiu
    se preiau din solduri_initiale dacă există."""
    from datetime import date
    inceput_an = date(an, 1, 1)
    inceput_luna = date(an, luna, 1)
    sfarsit = date(an + (luna == 12), (luna % 12) + 1, 1)
    with conn.cursor() as cur:
        si = {}
        for cont in ("371", "378", "4428"):
            cur.execute(f"""SELECT COALESCE(SUM(sold_debitor),0), COALESCE(SUM(sold_creditor),0)
                            FROM {schema}.solduri_initiale WHERE cont LIKE %s""", (cont + "%",))
            d, c = cur.fetchone()
            si[cont] = Decimal(d or 0) - Decimal(c or 0)   # debitor pozitiv
        # rulaje cumulate de la inceputul anului pana la sfarsitul lunii
        rd_371 = _rulaj(cur, schema, "371", "debit", sfarsit, inceput_an)
        rc_378 = _rulaj(cur, schema, "378", "credit", sfarsit, inceput_an)
        rc_4428 = _rulaj(cur, schema, "4428", "credit", sfarsit, inceput_an)
        # vanzari de marfuri DOAR pe luna
        rc_707 = _rulaj(cur, schema, "707", "credit", sfarsit, inceput_luna, surse=("horeca_z", "stocuri", "facturi_marfa"))
        # TVA aferenta vanzarilor de marfuri: proportional din 4427 e riscant;
        # folosim TVA neexigibila medie: tva = rc707 * (Si4428+Rc4428)/numitor-ul fara TVA
        # -> mai sigur: tva = rc707 * cota medie din stoc
    try:
        k = _m.coeficient_k(-si["378"], rc_378, si["371"], rd_371, -si["4428"], rc_4428)
    except ValueError as e:
        return {"eroare": str(e)}
    baza_stoc = (si["371"] + rd_371) - (-si["4428"] + rc_4428)
    tva_stoc = -si["4428"] + rc_4428
    tva_vanzari = (rc_707 * tva_stoc / baza_stoc).quantize(Decimal("0.01")) if baza_stoc else Decimal("0")
    rez = _m.descarcare_gv(rc_707, tva_vanzari, -si["378"], rc_378,
                           si["371"], rd_371, -si["4428"], rc_4428)
    if not rez["note"]:
        return {"k": None, "mesaj": "fara vanzari de marfuri in luna", "note": []}
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        import calendar
        ultima_zi = date(an, luna, calendar.monthrange(an, luna)[1])
        ids = _noteaza(cur, schema, ultima_zi,
                       f"Descarcare gestiune {luna:02d}/{an}", rez["note"])
    conn.commit()
    return {"k": str(rez["k"].quantize(Decimal('0.000001'))), "cmv": str(rez["cmv"]),
            "adaos": str(rez["adaos"]), "tva": str(rez["tva"]),
            "total_371": str(rez["total_371"]), "inregistrari": ids}
