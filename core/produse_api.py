"""
core/produse_api.py — nomenclatorul de produse per firma (schema tenant).
Cota TVA se potriveste automat cu AI (cote_tva.potriveste_cota) la prima
introducere a unei denumiri; apoi produsul e salvat si cota vine din nomenclator
(nu se mai intreaba AI). Un om poate confirma/corecta cota (control fiscal).
[R193, 10.10.2026] Modelul NU se intreaba de aici: functiile care primesc o conexiune primesc si
raspunsurile, cerute inainte de ea (`de_intrebat` -> `cote_tva.intreaba` -> `raspunsuri=`).

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
            # [R29 24.08.2026] NULL ramane NULL. Inainte: `else 21.0` - un produs fara cota
            # era prezentat ca 21%, pe o cale VIE (main.py:2513). Aceeasi clasa cu defaultul
            # din ecranul de NIR, dar in Python - clasa pe care R26 o declarase golita.
            d["cota_tva"] = float(d["cota_tva"]) if d["cota_tva"] is not None else None
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
    if out["cota_tva"] is None:
        # produs incomplet in nomenclator: NU se ghiceste 21 (baza nula). 0 (scutit) NU e None.
        raise ValueError("produs fără cota TVA în nomenclator: %r" % out.get("denumire"))
    out["cota_tva"] = float(out["cota_tva"])
    return out


def propunere_pentru_linie(conn, denumire, platitor_tva=True, raspunsuri=None):
    """[comanda Costin 05.10.2026 pct.9] Ce se propune pe o linie de factură când se scrie denumirea: produsul din NOMENCLATORUL
    firmei, dacă există (cota, UM, prețul), altfel cota din potrivirea automată. Înainte, linia întreba doar cota (AI), iar
    prețul și UM din nomenclator nu se precompletau. Neplătitorul primește cota 0 (CF art.310 alin.(10) lit.b), iar prețul și
    UM tot din nomenclator."""
    p = cauta_dupa_denumire(conn, denumire)
    if not p:
        return cote_tva.raspuns(raspunsuri, denumire, platitor_tva)
    cota = p["cota_tva"] if platitor_tva else 0
    return {"ok": True, "cota": int(cota) if float(cota).is_integer() else cota, "categorie": p.get("categorie"),
            "justificare": p.get("justificare"), "sursa": "nomenclator", "produs_id": p["id"],
            "um": p.get("um"), "pret_unitar": p["pret_unitar"]}


def de_intrebat(conn, denumire, cota_tva=None):
    """[R193] Faza de citire: denumirea pentru care `creeaza` / `propunere_pentru_linie` vor avea nevoie de răspunsul modelului —
    produsul fără cotă dată și absent din nomenclator. Întrebarea se pune apoi cu pool-ul liber (`cote_tva.intreaba`)."""
    d = (denumire or "").strip()
    return [d] if d and cota_tva is None and not cauta_dupa_denumire(conn, d) else []


def creeaza(conn, denumire, um="buc", pret_unitar=0, cota_tva=None,
            categorie=None, justificare=None, sursa="manual",
            confirmat=False, platitor_tva=True, raspunsuri=None):
    """
    Creeaza un produs in nomenclator. Daca cota_tva nu e data, o ia din `raspunsuri` (modelul, intrebat inaintea conexiunii).
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

    # daca nu s-a dat cota, o luam din raspunsul modelului, cerut INAINTEA conexiunii (`de_intrebat` + `cote_tva.intreaba`, R193)
    sursa_finala = sursa
    if cota_tva is None:
        rez = cote_tva.raspuns(raspunsuri, d, platitor_tva)
        if rez.get("cota") is None:
            # auto-match esuat: NU salvam un produs cu cota ghicita -> NEDETERMINAT (baza nula).
            # (0 = scutit/neplatitor NU e None -> se salveaza normal)
            return {"ok": False, "cod": "NEDETERMINAT", "denumire": d,
                    "mesaj": rez.get("justificare") or "cota TVA nedeterminată"}
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
