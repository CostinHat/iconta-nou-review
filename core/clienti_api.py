"""
core/clienti_api.py — clienți/parteneri în schema unui tenant: listă, creare,
detalii, editare, ștergere. Rulează pe conexiunea poziționată pe schema tenantului.

Fără logică de business (doar date) — nu există parte „pură" de calcul.
Ștergerea e PROTEJATĂ: dacă clientul are facturi, refuz curat (nu las FK-ul să
arunce un 500 urât și să strice tranzacția).
"""
from __future__ import annotations

from core import chei_unice as _chei
from core.common import cate as _cate

REGULI = "2026.1"
MODUL = "clienti_api"

_CAMPURI = ("nume", "cui", "adresa", "email", "telefon",
            "oras", "judet", "cod_postal", "status", "afiliat")

#: [lotul 10, deficiența 428, decizia Costin 20.10.2026 „Bifă pe client”] CUI-ul comparat fără spații și fără prefixul RO (clientul scris
#: „RO 18547290” e același cu factura către „18547290”)
_CUI_SQL = "regexp_replace(regexp_replace(upper(COALESCE({c}, '')), '\\s', '', 'g'), '^RO', '')"


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
            "SELECT id, nume, cui, email, telefon, oras, judet, status, afiliat "
            "FROM clienti" + cond + " ORDER BY nume", val)
        return [dict(r) for r in cur.fetchall()]


# ============================================================
#  CREARE
# ============================================================
def creeaza_client(conn, nume, cui=None, adresa=None, email=None, telefon=None,
                   oras=None, judet=None, cod_postal=None, status="activ", afiliat=False):
    """Inserează un client. Întoarce {ok, client_id}. `afiliat` = persoană afiliată (Cod fiscal art.7 pct.26) — CF art.282 alin.(6) lit.d."""
    if not nume or not str(nume).strip():
        raise ValueError("nume client obligatoriu")
    with conn.cursor() as cur:
        # [lotul 10, C73] un CUI deja în nomenclator -> refuzul numit, cu clientul existent (nu `500` din `clienti_cui_uniq`)
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI,), _refuz_cui(None)):
            cur.execute(
                "INSERT INTO clienti (nume, cui, adresa, email, telefon, oras, judet, "
                "cod_postal, status, afiliat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                (nume, cui, adresa, email, telefon, oras, judet, cod_postal, status, bool(afiliat)))
            client_id = cur.fetchone()[0]
    return {"ok": True, "client_id": client_id}


#: cheia naturală a clientului (`core/migrare_intrare_date_garduri.UNIQUE`): un CUI = o singură fișă de client
CONSTRANGERE_CUI = "clienti_cui_uniq"


def _refuz_cui(client_id):
    """[lotul 10, C73] Refuzul CUI-ului dublat, cu clientul care îl are deja: numele lui și id-ul fișei (`existent`), ca ecranul să
    poată duce la el. `client_id` = fișa editată (None la creare)."""
    def refuz(cur, e):
        cur.execute("SELECT id, nume, cui FROM clienti WHERE cui = %s AND id IS DISTINCT FROM %s ORDER BY id LIMIT 1",
                    (_chei.valoarea(e), client_id))
        r = cur.fetchone()
        if not r:   # cheia citită din detaliul bazei nu mai găsește rândul (șters între timp): spunem valoarea, fără nume
            return _chei.CheieDublata("Există deja un client cu CUI-ul %s. Un CUI are o singură fișă de client."
                                      % (_chei.valoarea(e) or ""), valoare=_chei.valoarea(e), camp="cui")
        ce = "Nu se creează a doua fișă pentru același CUI" if client_id is None else "Un CUI aparține unei singure fișe de client"
        return _chei.CheieDublata(
            "Există deja clientul %s cu CUI-ul %s (în lista Clienți). %s: deschide fișa existentă și schimbă acolo ce ai de schimbat."
            % (r[1], r[2], ce), valoare=r[2], existent={"client_id": r[0], "nume": r[1]}, camp="cui")
    return refuz


# ============================================================
#  DETALII
# ============================================================
def detalii_client(conn, client_id):
    """Un client complet, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, nume, cui, adresa, email, telefon, oras, judet, "
            "cod_postal, status, afiliat FROM clienti WHERE id = %s", (client_id,))
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
        # [lotul 10, C73] CUI-ul schimbat pe unul care e deja al altui client -> același refuz numit ca la creare
        with _chei.refuza_dublura(cur, (CONSTRANGERE_CUI,), _refuz_cui(client_id)):
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
                    "mesaj": "clientul are %s — nu poate fi șters" % _cate(nr, "factură", "facturi")}
        cur.execute("DELETE FROM clienti WHERE id = %s", (client_id,))
        sters = cur.rowcount > 0
    return {"ok": sters}


# ============================================================
#  PERSOANA AFILIATĂ (lotul 10, deficiența 428)
# ============================================================
def client_afiliat(cur, client_id=None, cui=None):
    """Beneficiarul e persoană afiliată (bifa clientului)? Clientul ales (`client_id`) sau, fără el, clientul cu același CUI (emiterea scrie
    numai CUI-ul). CF art.282 alin.(6) lit.d): sistemul TVA la încasare nu se aplică pentru „livrările de bunuri/prestările de servicii
    pentru care beneficiarul este o persoană afiliată furnizorului/prestatorului potrivit art. 7 pct. 26”. Fără client găsit: False."""
    if client_id is None and not str(cui or "").strip():
        return False
    cur.execute("SELECT COALESCE(bool_or(afiliat), false) FROM clienti WHERE id = %s OR (%s::int IS NULL AND %s <> '' AND "
                + _CUI_SQL.format(c="cui") + " = " + _CUI_SQL.format(c="%s") + ")",
                (client_id, client_id, str(cui or "").strip(), str(cui or "")))
    r = cur.fetchone()
    return bool(r["coalesce"] if isinstance(r, dict) else r[0])


def parteneri_fara_fisa(conn):
    """Beneficiarii facturilor emise care n-au încă fișă de client (CUI-ul lor nu e în `clienti`) — pe ecranul clienților, ca bifa
    „persoană afiliată” să se poată pune și pe ei. [{cui, nume, facturi}]; cel mai recent nume al partenerului."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT " + _CUI_SQL.format(c="f.tert_cui") + " AS cui, "
                    "(array_agg(f.tert_nume ORDER BY f.data_emitere DESC, f.id DESC))[1] AS nume, count(*) AS facturi "
                    "FROM facturi f WHERE f.directie = 'emisa' AND COALESCE(f.tip, 'factura') = 'factura' "
                    "AND " + _CUI_SQL.format(c="f.tert_cui") + " <> '' AND NOT EXISTS (SELECT 1 FROM clienti c WHERE "
                    + _CUI_SQL.format(c="c.cui") + " = " + _CUI_SQL.format(c="f.tert_cui") + ") "
                    "GROUP BY 1 ORDER BY 2, 1")
        return [dict(r) for r in cur.fetchall()]
