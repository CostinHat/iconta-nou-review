# -*- coding: utf-8 -*-
"""Conector WooCommerce: import comenzi -> facturi iConta.
Config per tenant in firma_profil (wc_url, wc_ck, wc_cs). Idempotent pe numar comanda."""
import json
import requests
from decimal import Decimal
from psycopg2.extras import RealDictCursor


def comenzi(url, ck, cs, dupa=None, status="completed,processing"):
    """Citeste comenzile din WC REST API."""
    p = {"per_page": 100, "status": status}
    if dupa:
        p["after"] = dupa + "T00:00:00"
    r = requests.get(url.rstrip("/") + "/wp-json/wc/v3/orders",
                     auth=(ck, cs), params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def comanda_in_factura(c):
    """PURA: comanda WC -> dict factura iConta (linii cu preturi fara TVA din WC)."""
    linii = []
    for l in c.get("line_items", []):
        cant = Decimal(str(l.get("quantity") or 1))
        total = Decimal(str(l.get("total") or 0))
        pret = (total / cant).quantize(Decimal("0.01")) if cant else Decimal("0")
        linii.append({"descriere": l.get("name") or "produs",
                      "cantitate": float(cant), "pret_unitar": float(pret),
                      "cota_tva": None})
    b = c.get("billing") or {}
    nume = (b.get("company") or "").strip() or f'{b.get("first_name","")} {b.get("last_name","")}'.strip() or "client web"
    return {"sursa_numar": str(c.get("number") or c.get("id")),
            "data": str(c.get("date_created") or "")[:10],
            "tert_nume": nume, "tert_cui": None,
            "moneda": c.get("currency") or "RON",
            "total_wc": float(c.get("total") or 0),
            "linii": linii}


def deja_importata(conn, schema, sursa_numar):
    with conn.cursor() as cur:
        cur.execute(f"""SELECT id FROM {schema}.facturi
                        WHERE sursa_externa=%s LIMIT 1""",
                    ("WC-" + sursa_numar,))
        return cur.fetchone() is not None


def config(conn, schema):
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"SELECT wc_url, wc_ck, wc_cs, wc_ultima_sinc FROM {schema}.firma_profil LIMIT 1")
        return cur.fetchone()


def sincronizeaza(conn, schema):
    """Import comenzi noi -> facturi emise (status de_preluat). Idempotent pe numar WC-<nr>."""
    from core import facturi_api
    cfg = config(conn, schema)
    if not (cfg and cfg["wc_url"] and cfg["wc_ck"] and cfg["wc_cs"]):
        return {"eroare": "WooCommerce neconfigurat"}
    dupa = str(cfg["wc_ultima_sinc"]) if cfg["wc_ultima_sinc"] else None
    lista_c = comenzi(cfg["wc_url"], cfg["wc_ck"], cfg["wc_cs"], dupa=dupa)
    importate, sarite = [], 0
    for c in lista_c:
        f = comanda_in_factura(c)
        if not f["linii"]:
            sarite += 1
            continue
        if deja_importata(conn, schema, f["sursa_numar"]):
            sarite += 1
            continue
        rez = facturi_api.emite_factura(conn, f["linii"],
                                        tert_nume=f["tert_nume"],
                                        data_emitere=f["data"],
                                        moneda=f["moneda"])
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {schema}.facturi SET sursa_externa=%s WHERE id=%s",
                        ("WC-" + f["sursa_numar"], rez["factura_id"]))
        conn.commit()
        importate.append({"comanda": f["sursa_numar"], "factura_id": rez["factura_id"],
                          "total": rez.get("total")})
    import datetime
    with conn.cursor() as cur:
        cur.execute(f"UPDATE {schema}.firma_profil SET wc_ultima_sinc=%s",
                    (datetime.date.today().isoformat(),))
    conn.commit()
    return {"importate": importate, "sarite": sarite}
