# -*- coding: utf-8 -*-
"""Link de plata pe factura emisa. Provider abstract: mock (fara cont) / netopia / stripe.
Cheia providerului va veni din env la activare; pana atunci mock genereaza link intern."""
import os
import secrets

def provider_activ():
    if os.environ.get("STRIPE_SECRET_KEY"):
        return "stripe"
    if os.environ.get("NETOPIA_API_KEY"):
        return "netopia"
    return "mock"

def genereaza_link(conn, schema, factura_id, baza_url):
    """Factura emisa + neplatita -> {link, provider, ref}. Idempotent: link existent se refoloseste."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT directie, status, total, moneda, link_plata, plata_ref, platita_la
                        FROM {schema}.facturi WHERE id=%s""", (factura_id,))
        r = cur.fetchone()
    if not r:
        return {"eroare": "factură inexistentă"}
    directie, status, total, moneda, link, ref, platita = r
    if directie != "emisa":
        return {"eroare": "doar facturi emise"}
    if platita:
        return {"eroare": "factura deja platita"}
    if link:
        return {"link": link, "provider": provider_activ(), "ref": ref, "existent": True}
    prov = provider_activ()
    ref = "pl_" + secrets.token_urlsafe(16)
    if prov == "mock":
        link = f"{baza_url}/public/plata/{ref}"
    else:
        raise NotImplementedError(f"provider {prov}: de implementat la primirea cheilor")
    with conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.facturi SET link_plata=%s, plata_provider=%s, plata_ref=%s
                        WHERE id=%s""", (link, prov, ref, factura_id))
    conn.commit()
    return {"link": link, "provider": prov, "ref": ref, "existent": False}

def confirma_plata(conn, schema, ref):
    """Callback provider: marcheaza platita. Idempotent."""
    with conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.facturi SET platita_la=now()
                        WHERE plata_ref=%s AND platita_la IS NULL RETURNING id""", (ref,))
        r = cur.fetchone()
    conn.commit()
    if r:
        return {"ok": True, "factura_id": r[0]}
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {schema}.facturi WHERE plata_ref=%s", (ref,))
        r = cur.fetchone()
    return {"ok": bool(r), "factura_id": r[0] if r else None, "deja": True} if r else {"eroare": "ref necunoscut"}
