"""
core/clienti_api.py — clienți/parteneri în schema unui tenant: listă, creare,
detalii, editare, ștergere. Rulează pe conexiunea poziționată pe schema tenantului.

Fără logică de business (doar date) — nu există parte „pură" de calcul.
Ștergerea e PROTEJATĂ: dacă clientul are facturi, refuz curat (nu las FK-ul să
arunce un 500 urât și să strice tranzacția).
"""
from __future__ import annotations

REGULI = "2026.1"
MODUL = "clienti_api"

_CAMPURI = ("nume", "cui", "adresa", "email", "telefon",
            "oras", "judet", "cod_postal", "status")


# ============================================================
#  LISTĂ
# ============================================================
def lista_clienti(conn, status=None):
    """Toți clienții, opțional filtrați pe status (activ/inactiv)."""
    import psycopg2.extras as _E
    cond, val = "", []
    if status is not None:
        cond = " WHERE status = %s"; val.append(status)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, nume, cui, email, telefon, oras, judet, status "
            "FROM clienti" + cond + " ORDER BY nume", val)
        return [dict(r) for r in cur.fetchall()]


# ============================================================
#  CREARE
# ============================================================
def creeaza_client(conn, nume, cui=None, adresa=None, email=None, telefon=None,
                   oras=None, judet=None, cod_postal=None, status="activ"):
    """Inserează un client. Întoarce {ok, client_id}."""
    if not nume or not str(nume).strip():
        raise ValueError("nume client obligatoriu")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO clienti (nume, cui, adresa, email, telefon, oras, judet, "
            "cod_postal, status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
            (nume, cui, adresa, email, telefon, oras, judet, cod_postal, status))
        client_id = cur.fetchone()[0]
    return {"ok": True, "client_id": client_id}


# ============================================================
#  DETALII
# ============================================================
def detalii_client(conn, client_id):
    """Un client complet, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, nume, cui, adresa, email, telefon, oras, judet, "
            "cod_postal, status FROM clienti WHERE id = %s", (client_id,))
        r = cur.fetchone()
    return dict(r) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise)
# ============================================================
def actualizeaza_client(conn, client_id, **campuri):
    """Editează doar câmpurile date (din _CAMPURI). Întoarce {ok}."""
    seturi, valori = [], []
    for k in _CAMPURI:
        if k in campuri and campuri[k] is not None:
            seturi.append("%s = %%s" % k); valori.append(campuri[k])
    if not seturi:
        return {"ok": True, "neschimbat": True}
    valori.append(client_id)
    with conn.cursor() as cur:
        cur.execute("UPDATE clienti SET %s WHERE id = %%s" % ", ".join(seturi), valori)
        ok = cur.rowcount > 0
    return {"ok": ok}


# ============================================================
#  ȘTERGERE — protejată (refuz dacă are facturi)
# ============================================================
def sterge_client(conn, client_id):
    """
    Șterge clientul DOAR dacă nu are facturi legate (FK ar bloca oricum).
    Verific întâi, ca să întorc mesaj clar fără să stric tranzacția.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE client_id = %s", (client_id,))
        nr = cur.fetchone()[0]
        if nr:
            return {"ok": False, "cod": "ARE_FACTURI",
                    "mesaj": "clientul are %d facturi — nu poate fi șters" % nr}
        cur.execute("DELETE FROM clienti WHERE id = %s", (client_id,))
        sters = cur.rowcount > 0
    return {"ok": sters}
