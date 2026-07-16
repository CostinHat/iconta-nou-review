"""
core/scadentar.py — scadentar facturi emise neincasate + fisa client. Calcul PUR, fara DB.

F131 (Notificari de plata si alerte neplatnici), componentele 1-4 (fara notificare email,
care cere schema si e amanata). Se aplica facturilor EMISE ale firmei catre clientii ei.

Stare per factura neincasata (facturi.platita_la IS NULL):
  restanta     : data_scadenta < azi (intarziere)
  scade_curand : azi <= data_scadenta <= azi + prag_zile
  in_termen    : data_scadenta > azi + prag_zile
  fara_scadenta: data_scadenta lipseste (nu se poate clasifica; se raporteaza separat)
Facturile achitate (platita_la != NULL) NU intra in scadentar - nu mai sunt de urmarit.

Ordinea de urgenta (ca la semafoare, cap.8 DS): restanta -> scade_curand -> in_termen.
"""
from decimal import Decimal

PRAG_ZILE = 7

# ordinea de urgenta pentru sortare (rosu intai)
_ORD = {"restanta": 0, "scade_curand": 1, "fara_scadenta": 2, "in_termen": 3}


def clasifica(data_scadenta, azi, prag_zile=PRAG_ZILE):
    """(stare, zile) pentru o factura neincasata. zile = data_scadenta - azi
    (negativ = intarziere). data_scadenta poate lipsi -> ('fara_scadenta', None)."""
    if not data_scadenta:
        return ("fara_scadenta", None)
    zile = (data_scadenta - azi).days
    if zile < 0:
        return ("restanta", zile)
    if zile <= prag_zile:
        return ("scade_curand", zile)
    return ("in_termen", zile)


def scadentar(facturi, azi, prag_zile=PRAG_ZILE):
    """facturi: NEINCASATE (apelantul filtreaza platita_la IS NULL). Fiecare:
    {id, numar, data_emitere, data_scadenta, suma, tert_nume, tert_cui, client_id, email}.
    Intoarce {linii (sortate pe urgenta), rezumat (nr pe stare), clienti (fisa agregata)}."""
    linii = []
    rezumat = {"restanta": 0, "scade_curand": 0, "in_termen": 0, "fara_scadenta": 0}
    per_client = {}
    for f in facturi:
        stare, zile = clasifica(f.get("data_scadenta"), azi, prag_zile)
        suma = Decimal(str(f.get("suma") or 0))
        linii.append({**f, "stare": stare, "zile": zile})
        rezumat[stare] += 1
        k = (f.get("tert_cui") or "").strip() or (f.get("tert_nume") or "").strip() or "?"
        c = per_client.setdefault(k, {
            "nume": f.get("tert_nume"), "cui": f.get("tert_cui"), "email": f.get("email"),
            "client_id": f.get("client_id"), "nr": 0, "sold": Decimal(0), "restant": Decimal(0)})
        c["nr"] += 1
        c["sold"] += suma
        if stare == "restanta":
            c["restant"] += suma
    # sortare pe urgenta, apoi cele mai intarziate intai (zile crescator: -30 inaintea -1)
    linii.sort(key=lambda l: (_ORD[l["stare"]], l["zile"] if l["zile"] is not None else 0))
    clienti = sorted(per_client.values(), key=lambda c: (-c["restant"], -c["sold"]))
    return {"linii": linii, "rezumat": rezumat, "clienti": clienti}


def total_restant(rez):
    """Numarul de facturi restante - pentru alerta (contor) pe cardul Facturi."""
    return rez["rezumat"]["restanta"]


def pull(conn, schema, azi=None, prag_zile=PRAG_ZILE):
    """Citeste facturile EMISE neincasate si intoarce scadentarul. Conexiunea trebuie
    pozitionata pe schema (get_conn(schema)). Exclude storno-urile si proformele/avizele
    (v1: storno-ul care neteste o factura nu e modelat inca - de reluat cand apare cazul).
    Email-ul clientului via LEFT JOIN clienti (facturile create direct, client_id NULL,
    apar in scadentar dar fara email -> nu pot fi notificate automat)."""
    import psycopg2.extras as _E
    from datetime import date as _d
    azi = azi or _d.today()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT f.id, f.numar, f.serie, f.data_emitere, f.data_scadenta, "
            "       COALESCE(f.total,0) AS suma, f.moneda, f.tert_nume, f.tert_cui, "
            "       f.client_id, c.email "
            "  FROM facturi f "
            "  LEFT JOIN clienti c ON c.id = f.client_id "
            " WHERE f.directie = 'emisa' AND f.platita_la IS NULL "
            "   AND COALESCE(f.tip, 'factura') = 'factura' "
            "   AND f.storno_din_id IS NULL")
        facturi = [dict(r) for r in cur.fetchall()]
    return scadentar(facturi, azi, prag_zile)
