"""
core/salariati_api.py — salariați în schema unui tenant: listă, creare, detalii,
editare, ștergere. Alimentează D112 (payroll). Rulează pe conexiunea poziționată
pe schema tenantului.

Validare minimală pe server (PURĂ, testabilă): CNP 13 cifre, brut ≥ 0,
tip_norma ∈ {intreaga, partiala}. Prinde greșeli evidente devreme.

Ștergere PROTEJATĂ: dacă salariatul are concedii medicale, refuz curat.
"""
from __future__ import annotations
import re

REGULI = "2026.1"
MODUL = "salariati_api"

_CNP = re.compile(r"^\d{13}$")
_NORME = ("intreaga", "partiala")
_CAMPURI = ("cnp", "nume", "prenume", "data_angajare", "tip_norma", "ore_zi",
            "salariu_brut", "persoane_intretinere", "judet_casa", "activ",
            "scutit_contrib_minim", "motiv_exceptare", "cor")


# ============================================================
#  VALIDARE — PURĂ
# ============================================================
def valideaza_salariat(date):
    """Verifică datele unui salariat. Întoarce listă erori (gol = ok)."""
    erori = []
    if not (date.get("nume") and str(date["nume"]).strip()):
        erori.append("nume obligatoriu")
    cnp = date.get("cnp")
    if cnp and not _CNP.match(str(cnp)):
        erori.append("CNP invalid: aștept 13 cifre")
    brut = date.get("salariu_brut")
    if brut is not None:
        try:
            if float(brut) < 0:
                erori.append("salariu_brut nu poate fi negativ")
        except (TypeError, ValueError):
            erori.append("salariu_brut invalid")
    tn = date.get("tip_norma")
    if tn is not None and tn not in _NORME:
        erori.append("tip_norma trebuie 'intreaga' sau 'partiala'")
    return erori


# ============================================================
#  LISTĂ
# ============================================================
def lista_salariati(conn, activ=None):
    """Salariații, opțional filtrați pe activ (True/False)."""
    import psycopg2.extras as _E
    cond, val = "", []
    if activ is not None:
        cond = " WHERE activ = %s"; val.append(activ)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, cnp, nume, prenume, data_angajare, tip_norma, ore_zi, "
            "salariu_brut, persoane_intretinere, activ, cor "
            "FROM salariati" + cond + " ORDER BY nume, prenume", val)
        return [dict(r) for r in cur.fetchall()]


# ============================================================
#  CREARE
# ============================================================
def creeaza_salariat(conn, **date):
    """Inserează un salariat (după validare). Întoarce {ok, salariat_id} sau ridică
    ValueError cu erorile."""
    erori = valideaza_salariat(date)
    if erori:
        raise ValueError("; ".join(erori))
    cols = [k for k in _CAMPURI if k in date and date[k] is not None]
    vals = [date[k] for k in cols]
    ph = ", ".join(["%s"] * len(cols))
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO salariati (%s) VALUES (%s) RETURNING id"
            % (", ".join(cols), ph), vals)
        sid = cur.fetchone()[0]
    return {"ok": True, "salariat_id": sid}


# ============================================================
#  DETALII
# ============================================================
def detalii_salariat(conn, salariat_id):
    """Un salariat complet, sau None."""
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute(
            "SELECT id, cnp, nume, prenume, data_angajare, tip_norma, ore_zi, "
            "salariu_brut, persoane_intretinere, judet_casa, activ, "
            "scutit_contrib_minim, motiv_exceptare, cor "
            "FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
    return dict(r) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise, validate)
# ============================================================
def actualizeaza_salariat(conn, salariat_id, **date):
    """Editează câmpurile date (validate). Întoarce {ok} sau ridică ValueError."""
    campuri = {k: v for k, v in date.items() if k in _CAMPURI and v is not None}
    if not campuri:
        return {"ok": True, "neschimbat": True}
    erori = valideaza_salariat({**campuri, "nume": campuri.get("nume", "x")})
    # la editare parțială, 'nume' poate lipsi — punem placeholder ca să nu dea fals-pozitiv
    erori = [e for e in erori if e != "nume obligatoriu"]
    if erori:
        raise ValueError("; ".join(erori))
    seturi = ", ".join("%s = %%s" % k for k in campuri)
    vals = list(campuri.values()) + [salariat_id]
    with conn.cursor() as cur:
        cur.execute("UPDATE salariati SET %s WHERE id = %%s" % seturi, vals)
        ok = cur.rowcount > 0
    return {"ok": ok}


# ============================================================
#  ȘTERGERE — protejată (concedii medicale legate)
# ============================================================
def sterge_salariat(conn, salariat_id):
    """Șterge salariatul DOAR dacă nu are concedii medicale legate."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM concedii_medicale WHERE salariat_id = %s",
                    (salariat_id,))
        nr = cur.fetchone()[0]
        if nr:
            return {"ok": False, "cod": "ARE_CONCEDII",
                    "mesaj": "salariatul are %d concedii medicale — nu poate fi șters" % nr}
        cur.execute("DELETE FROM salariati WHERE id = %s", (salariat_id,))
        sters = cur.rowcount > 0
    return {"ok": sters}
