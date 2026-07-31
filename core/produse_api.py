"""
core/produse_api.py — nomenclatorul de produse per firma (schema tenant).
Cota TVA se potriveste automat cu AI (cote_tva.potriveste_cota) la prima
introducere a unei denumiri; apoi produsul e salvat si cota vine din nomenclator
(nu se mai intreaba AI). Un om poate confirma/corecta cota (control fiscal).

Conexiunea vine deja pe schema tenant (search_path setat de apelant).
"""
from core import cote_tva


def lista(conn, doar_confirmate=False):
    """Toate produsele firmei, ordonate alfabetic."""
    import psycopg2.extras as _E
    cond = " WHERE confirmat = true" if doar_confirmate else ""
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, denumire, um, pret_unitar, cota_tva, categorie, "
            "justificare, sursa, confirmat "
            "FROM produse" + cond + " ORDER BY lower(denumire)")
        out = []
        for r in cur.fetchall():
            d = dict(r)
            d["pret_unitar"] = float(d["pret_unitar"]) if d["pret_unitar"] is not None else 0.0
            d["cota_tva"] = float(d["cota_tva"]) if d["cota_tva"] is not None else 21.0
            out.append(d)
    return out


def cauta_dupa_denumire(conn, denumire):
    """Cauta un produs existent dupa denumire (case-insensitive). Intoarce dict sau None."""
    import psycopg2.extras as _E
    d = (denumire or "").strip()
    if not d:
        return None
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, denumire, um, pret_unitar, cota_tva, categorie, "
            "justificare, sursa, confirmat "
            "FROM produse WHERE lower(denumire) = lower(%s) LIMIT 1", (d,))
        r = cur.fetchone()
    if not r:
        return None
    out = dict(r)
    out["pret_unitar"] = float(out["pret_unitar"] or 0)
    out["cota_tva"] = float(out["cota_tva"] or 21)
    return out


def potriveste(denumire, platitor_tva=True):
    """
    Propune cota pentru o denumire noua, FARA sa salveze (preview pentru UI).
    Intoarce rezultatul din cote_tva.potriveste_cota (cota, categorie,
    justificare, incredere, sursa).
    """
    return cote_tva.potriveste_cota(denumire, platitor_tva=platitor_tva)


def creeaza(conn, denumire, um="buc", pret_unitar=0, cota_tva=None,
            categorie=None, justificare=None, sursa="manual",
            confirmat=False, platitor_tva=True):
    """
    Creeaza un produs in nomenclator. Daca cota_tva nu e data, o potriveste cu AI.
    Daca produsul exista deja (aceeasi denumire), intoarce cel existent (nu dubleaza).
    Intoarce {ok, id, denumire, cota_tva, categorie, justificare, sursa, confirmat, existent}.
    """
    d = (denumire or "").strip()
    if not d:
        return {"ok": False, "cod": "GOL", "mesaj": "denumire lipsă"}

    existent = cauta_dupa_denumire(conn, d)
    if existent:
        existent["existent"] = True
        existent["ok"] = True
        return existent

    # daca nu s-a dat cota, o potrivim cu AI
    sursa_finala = sursa
    if cota_tva is None:
        rez = cote_tva.potriveste_cota(d, platitor_tva=platitor_tva)
        if rez.get("cota") is None:
            # auto-match esuat: NU salvam un produs cu cota ghicita -> NEDETERMINAT (baza nula).
            # (0 = scutit/neplatitor NU e None -> se salveaza normal)
            return {"ok": False, "cod": "NEDETERMINAT", "denumire": d,
                    "mesaj": rez.get("justificare") or "cota TVA nedeterminata"}
        cota_tva = rez["cota"]
        categorie = categorie or rez.get("categorie")
        justificare = justificare or rez.get("justificare")
        sursa_finala = rez.get("sursa", "ai")

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO produse (denumire, um, pret_unitar, cota_tva, categorie, "
            "justificare, sursa, confirmat) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (d, um or "buc", pret_unitar or 0, cota_tva, categorie,
             justificare, sursa_finala, bool(confirmat)))
        pid = cur.fetchone()[0]

    return {"ok": True, "id": pid, "denumire": d, "um": um or "buc",
            "pret_unitar": float(pret_unitar or 0), "cota_tva": float(cota_tva),
            "categorie": categorie, "justificare": justificare,
            "sursa": sursa_finala, "confirmat": bool(confirmat), "existent": False}


def actualizeaza(conn, produs_id, denumire=None, um=None, pret_unitar=None,
                 cota_tva=None, categorie=None, confirmat=None):
    """Actualizeaza campurile date ale unui produs. Daca se schimba cota manual,
    sursa devine 'manual'. Intoarce {ok} sau {ok:False}."""
    seturi, val = [], []
    if denumire is not None:
        seturi.append("denumire = %s"); val.append(denumire.strip())
    if um is not None:
        seturi.append("um = %s"); val.append(um)
    if pret_unitar is not None:
        seturi.append("pret_unitar = %s"); val.append(pret_unitar)
    if cota_tva is not None:
        seturi.append("cota_tva = %s"); val.append(cota_tva)
        seturi.append("sursa = 'manual'")  # corectat de om
    if categorie is not None:
        seturi.append("categorie = %s"); val.append(categorie)
    if confirmat is not None:
        seturi.append("confirmat = %s"); val.append(bool(confirmat))
    if not seturi:
        return {"ok": False, "cod": "NIMIC", "mesaj": "nimic de actualizat"}
    val.append(produs_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE produse SET " + ", ".join(seturi) + " WHERE id = %s", val)
        afectate = cur.rowcount
    return {"ok": afectate > 0, "id": produs_id}


def sterge(conn, produs_id):
    """Sterge un produs din nomenclator."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM produse WHERE id = %s", (produs_id,))
        afectate = cur.rowcount
    return {"ok": afectate > 0}
