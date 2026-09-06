# -*- coding: utf-8 -*-
"""Link de plata pe factura emisa. Provider abstract: mock (fara cont) / netopia / stripe.
Cheia providerului va veni din env la activare; pana atunci mock genereaza link intern.

[R43, 06.09.2026] DOUA REPARATII, amandoua INTERNE; a treia parte a restantei ramane EXTERNA.

**(1) REFERINTA ISI STIE FIRMA.** Pana azi `POST /public/plata/{ref}/confirma` citea
`SELECT schema_name FROM public.tenants` si incerca un `UPDATE` in FIECARE schema, pana la prima
potrivire. Nu era o scurgere — raspunsul e doar `{ok}`, iar `ref` are 128 de biti — dar era o ruta
neautentificata care SCRIE prin toate firmele, fara nicio bariera structurala intre ele. Acum
`genereaza_link` inregistreaza perechea in `public.plata_referinte` (`ref` = PRIMARY KEY), iar
confirmarea PLEACA de la firma, nu o cauta. *Coliziunea intre firme devine imposibila prin
constructie, nu improbabila* — iar improbabil nu e o izolare, e un pariu.

**(2) PLATA SIMULATA O SPUNE.** `platita_la` scris pe calea `mock` e un buton apasat, nu bani
intrati. `plata_confirmata_de` retine CINE a confirmat; pe `mock` valoarea e chiar `'mock'`, si
ajunge pe ecran, langa eticheta „platita". Conditia lui R43 cere exact asta pentru inchiderea
partiala.

**CE RAMANE DESCHIS:** confirmarea nu vine de la un procesator real, semnata. Cere chei de la
Costin (`cine deblochează: EXTERN`), iar `provider_activ()` ridica deja `NotImplementedError`
pentru orice altceva decat `mock`, deci calea e pregatita si nu poate fi folosita din greseala.
"""
import os
import secrets

def provider_activ():
    if os.environ.get("STRIPE_SECRET_KEY"):
        return "stripe"
    if os.environ.get("NETOPIA_API_KEY"):
        return "netopia"
    return "mock"


def firma_pentru_ref(conn, ref):
    """`(tenant_id, schema_name, factura_id)` pentru o referinta, sau `None`.

    Singura cale prin care confirmarea afla firma. Fara ea, ruta ar trebui sa caute — adica sa
    atinga toate schemele, ceea ce R43 numeste chiar defectul."""
    with conn.cursor() as cur:
        cur.execute("""SELECT tenant_id, schema_name, factura_id
                       FROM public.plata_referinte WHERE ref = %s""", (ref,))
        return cur.fetchone()


def genereaza_link(conn, schema, factura_id, baza_url, tenant_id=None):
    """Factura emisa + neplatita -> {link, provider, ref}. Idempotent: link existent se refoloseste.

    `tenant_id` e obligatoriu pentru o referinta NOUA: fara el, perechea `ref -> firma` n-ar exista,
    iar confirmarea ar ramane fara drum. Se refuza explicit, in loc sa se scrie un link neconfirmabil.
    """
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
    if tenant_id is None:
        # Mesajul nu numește coloana: cine îl citește e omul, nu cine a scris apelul.
        return {"eroare": "Linkul de plată nu s-a putut crea: nu se știe firma care emite "
                          "factura, iar fără ea confirmarea plății n-ar avea unde ajunge."}
    prov = provider_activ()
    ref = "pl_" + secrets.token_urlsafe(16)
    if prov == "mock":
        link = f"{baza_url}/public/plata/{ref}"
    else:
        raise NotImplementedError(f"provider {prov}: de implementat la primirea cheilor")
    # ACEEASI TRANZACTIE: un `ref` scris pe factura fara perechea lui in `public` ar fi un link care
    # nu se poate confirma niciodata. Se comit impreuna sau deloc.
    with conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.facturi SET link_plata=%s, plata_provider=%s, plata_ref=%s
                        WHERE id=%s""", (link, prov, ref, factura_id))
        cur.execute("""INSERT INTO public.plata_referinte (ref, tenant_id, schema_name, factura_id)
                       VALUES (%s, %s, %s, %s)""", (ref, tenant_id, schema, factura_id))
    conn.commit()
    return {"link": link, "provider": prov, "ref": ref, "existent": False}

def confirma_plata(conn, schema, ref, provider=None):
    """Callback provider: marcheaza platita, si retine CINE a confirmat. Idempotent.

    `provider` gol -> `provider_activ()`. Pe `mock` ramane `'mock'`, adica *simulare*, si asta se
    vede in evidenta (`facturi.plata_confirmata_de`, randat langa eticheta „platita")."""
    prov = provider or provider_activ()
    with conn.cursor() as cur:
        cur.execute(f"""UPDATE {schema}.facturi SET platita_la=now(), plata_confirmata_de=%s
                        WHERE plata_ref=%s AND platita_la IS NULL RETURNING id""", (prov, ref))
        r = cur.fetchone()
    conn.commit()
    if r:
        return {"ok": True, "factura_id": r[0], "provider": prov}
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {schema}.facturi WHERE plata_ref=%s", (ref,))
        r = cur.fetchone()
    return {"ok": bool(r), "factura_id": r[0] if r else None, "deja": True} if r else {"eroare": "ref necunoscut"}
