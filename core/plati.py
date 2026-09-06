# -*- coding: utf-8 -*-
"""Calea de plata online — INCHISA. Nu se implementeaza.

**DECIZIA, a lui Costin, 06.09.2026**, verbatim: *„Nu se integreaza niciun procesator — fluxul real
e transfer bancar, confirmat din extras."* Iar despre restanta: *„R43, partea externa: se inchide ca
«nu se implementeaza», nu ramane deschisa la nesfarsit. Motivul: functionalitatea nu corespunde
fluxului de lucru real."*

**CE INSEMNA INAINTE.** `GET /public/plata/{ref}` randa o pagina cu un buton care spunea, literal,
*„Integrarea cu procesatorul de plati urmeaza. Apasati pentru a simula plata."* Apasarea marca
factura incasata. Iar `platita_la` devenea o afirmatie despre bani pe care nimic n-o sprijinea.

**CE S-A INCHIS, si unde.** Aici, intr-un singur loc: `CALEA_ONLINE_ACTIVA = False`. Amandoua
functiile refuza pe el, iar rutele si ecranul nu mai ofera nimic care sa duca aici. Comutatorul
exista ca REACTIVAREA sa fie un act deliberat si vizibil, nu o consecinta a stergerii unui `if`.

**CE NU S-A ATINS, si de ce.** `facturi.platita_la` ramane — nu era al caii asteia. Masurat inainte
de a inchide, pe toate cele 20 de firme: **o singura** factura poarta `platita_la`, pusa de calea
CHITANTEI (incasare in numerar), cu `plata_confirmata_de` gol si fara nicio referinta de plata.
**Zero** facturi cu marca de simulare, **zero** linkuri generate vreodata, **zero** randuri in
`public.plata_referinte`. Inchiderea nu desface nicio evidenta, fiindca n-a produs niciuna.

CE RAMANE, DECLARAT: tabela `public.plata_referinte` si coloana `facturi.plata_confirmata_de` raman
in schema, goale. Stergerea lor e o operatiune distructiva si o decizie separata; pana atunci sunt
consemnate ca dormante, nu ca uitate.
"""
import os

#: Comutatorul. `False` = calea e inchisa; vezi decizia din antet. Nu se ridica fara o decizie
#: scrisa: functionalitatea a fost inchisa fiindca NU corespunde fluxului real (transfer bancar,
#: confirmat din extras), nu fiindca ar fi fost incompleta.
CALEA_ONLINE_ACTIVA = False

#: Ce se spune omului, in loc de un buton. Numeste fluxul REAL, ca refuzul sa fie o indrumare.
MOTIV_INCHIS = ("Plata online nu e disponibilă în aplicație. Încasarea se face prin transfer "
                "bancar, iar factura se marchează încasată din extrasul de cont, la reconciliere.")


def provider_activ():
    """Providerul configurat. Ramane, dar nu mai deschide nimic: calea e inchisa mai sus."""
    if os.environ.get("STRIPE_SECRET_KEY"):
        return "stripe"
    if os.environ.get("NETOPIA_API_KEY"):
        return "netopia"
    return "mock"


def firma_pentru_ref(conn, ref):
    """`(tenant_id, schema_name, factura_id)` pentru o referinta, sau `None`.

    Ramane fiindca perechile vechi (daca ar exista vreodata) trebuie sa poata fi CITITE fara a
    plimba toate schemele — reparatia de izolare a lui R43. Azi tabela e goala."""
    with conn.cursor() as cur:
        cur.execute("""SELECT tenant_id, schema_name, factura_id
                       FROM public.plata_referinte WHERE ref = %s""", (ref,))
        return cur.fetchone()


def genereaza_link(conn, schema, factura_id, baza_url, tenant_id=None):
    """INCHISA. Nu se mai genereaza niciun link de plata.

    Refuzul e aici, nu in ruta: exista doua cai catre functia asta (ruta din ecran si orice apel
    viitor), iar o poarta pusa doar in ruta ar lasa-o pe cealalta deschisa."""
    if not CALEA_ONLINE_ACTIVA:
        return {"eroare": MOTIV_INCHIS, "inchis": True}
    raise NotImplementedError(
        "calea de plata online e inchisa prin decizie (06.09.2026); reactivarea cere o decizie noua")


def confirma_plata(conn, schema, ref, provider=None):
    """INCHISA. Nicio confirmare nu mai marcheaza o factura incasata.

    *Marcarea unei facturi ca incasata ramane la caile care corespund fluxului real*: chitanta
    (incasare in numerar) si aprobarea bonului (plata catre furnizor). Amandoua sunt neatinse.
    """
    if not CALEA_ONLINE_ACTIVA:
        return {"eroare": MOTIV_INCHIS, "inchis": True}
    raise NotImplementedError(
        "calea de plata online e inchisa prin decizie (06.09.2026); reactivarea cere o decizie noua")
