"""
core/salariati_api.py — salariați în schema unui tenant: listă, creare, detalii,
editare, ștergere. Alimentează D112 (payroll). Rulează pe conexiunea poziționată
pe schema tenantului.

Validare minimală pe server (PURĂ, testabilă): CNP 13 cifre, brut ≥ 0,
tip_norma ∈ {intreaga, partiala}. Prinde greșeli evidente devreme.

Traducere API<->DB: API foloseste tip_norma (text: intreaga/partiala), coloana
reala din DB e part_time (boolean). Traducerea se face la granita, contractul
API ramane neschimbat (compat cu main.py si frontend).

Ștergere PROTEJATĂ: dacă salariatul are concedii medicale, refuz curat.
"""
from __future__ import annotations
import re

REGULI = "2026.1"
MODUL = "salariati_api"

_CNP = re.compile(r"^\d{13}$")
_NORME = ("intreaga", "partiala")
_CAMPURI_API = ("cnp", "nume", "prenume", "data_angajare", "tip_norma", "ore_zi",
                "salariu_brut", "persoane_intretinere", "judet_casa", "activ",
                "scutit_contrib_minim", "motiv_exceptare", "cor")


def _api_spre_db(date):
    """Traduce cheile API (tip_norma) in coloane reale DB (part_time)."""
    d = dict(date)
    if "tip_norma" in d:
        tn = d.pop("tip_norma")
        if tn is not None:
            d["part_time"] = (tn == "partiala")
    return d


def _db_spre_api(row):
    """Traduce un rand din DB (part_time bool) inapoi in forma API (tip_norma)."""
    if row is None:
        return None
    r = dict(row)
    if "part_time" in r:
        r["tip_norma"] = "partiala" if r.pop("part_time") else "intreaga"
    return r


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
            "SELECT id, cnp, nume, prenume, data_angajare, part_time, ore_zi, "
            "salariu_brut, persoane_intretinere, activ, cor "
            "FROM salariati" + cond + " ORDER BY nume, prenume", val)
        return [_db_spre_api(dict(r)) for r in cur.fetchall()]


# ============================================================
#  CREARE
# ============================================================
def creeaza_salariat(conn, **date):
    """Inserează un salariat (după validare). Întoarce {ok, salariat_id} sau ridică
    ValueError cu erorile."""
    erori = valideaza_salariat(date)
    if erori:
        raise ValueError("; ".join(erori))
    campuri_api = {k: date[k] for k in _CAMPURI_API if k in date and date[k] is not None}
    campuri_db = _api_spre_db(campuri_api)
    cols = list(campuri_db.keys())
    vals = list(campuri_db.values())
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
            "SELECT id, cnp, nume, prenume, data_angajare, part_time, ore_zi, "
            "salariu_brut, persoane_intretinere, judet_casa, activ, "
            "scutit_contrib_minim, motiv_exceptare, cor "
            "FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
    return _db_spre_api(dict(r)) if r else None


# ============================================================
#  EDITARE (doar câmpurile trimise, validate)
# ============================================================
def actualizeaza_salariat(conn, salariat_id, **date):
    """Editează câmpurile date (validate). Întoarce {ok} sau ridică ValueError."""
    campuri_api = {k: v for k, v in date.items() if k in _CAMPURI_API and v is not None}
    if not campuri_api:
        return {"ok": True, "neschimbat": True}
    erori = valideaza_salariat({**campuri_api, "nume": campuri_api.get("nume", "x")})
    # la editare parțială, 'nume' poate lipsi — punem placeholder ca să nu dea fals-pozitiv
    erori = [e for e in erori if e != "nume obligatoriu"]
    if erori:
        raise ValueError("; ".join(erori))
    campuri = _api_spre_db(campuri_api)
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


# ============================================================
#  CONCEDII MEDICALE — calcul (calcul_cm + taxe_cm) + salvare
# ============================================================
def lista_concedii(conn, salariat_id, an=None):
    """Concediile medicale ale unui salariat, optional filtrate pe an. Desc dupa data inceput."""
    with conn.cursor() as cur:
        if an:
            cur.execute("SELECT * FROM concedii_medicale WHERE salariat_id=%s AND an=%s "
                        "ORDER BY data_inceput DESC NULLS LAST, id DESC", (salariat_id, an))
        else:
            cur.execute("SELECT * FROM concedii_medicale WHERE salariat_id=%s "
                        "ORDER BY data_inceput DESC NULLS LAST, id DESC", (salariat_id,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


def _dec_pos(v):
    try: return float(v)
    except (TypeError, ValueError): return 0.0


def salveaza_concediu(conn, salariat_id, date):
    """Calculeaza indemnizatia CM (calcul_cm + taxe_cm) si o salveaza in concedii_medicale.
    date: serie, numar, cod, data_acordare, data_inceput, data_sfarsit, loc_prescriere,
          diagnostic, spitalizare, zile_cm (lucratoare), venituri_6_luni, zile_6_luni,
          an, luna, procent_accident (optional). Intoarce randul salvat + breakdown calcul."""
    from core import salarizare as _s
    from decimal import Decimal
    cod = str(date.get("cod") or "01").zfill(2)
    zile_cm = int(date.get("zile_cm") or 0)
    ven6 = date.get("venituri_6_luni") or 0
    zile6 = int(date.get("zile_6_luni") or 1)
    spitalizare = bool(date.get("spitalizare"))
    pacc = int(date.get("procent_accident") or 100)
    import datetime as _dtmod
    _di = date.get("data_inceput") or None
    if isinstance(_di, str) and _di:
        try: la_data = _dtmod.date.fromisoformat(_di[:10])
        except ValueError: la_data = None
    else:
        la_data = _di

    # Validare: baza de calcul trebuie sa fie reala (altfel brut 0 dar net pozitiv = imposibil)
    if _dec_pos(ven6) <= 0:
        raise ValueError("Veniturile brute pe 6 luni lipsesc sau sunt 0 - completeaza baza de calcul din statele de plata.")
    if zile6 <= 0:
        raise ValueError("Zilele lucratoare din cele 6 luni lipsesc sau sunt 0.")
    if zile_cm <= 0:
        raise ValueError("Zilele lucratoare CM trebuie sa fie cel putin 1.")
    if cod == "10":  # [cod10] art. 19 OUG 158/2005: baza - venit realizat, plafon 25% din baza; integral FNUASS (art. 12)
        from decimal import Decimal as _D
        vr = date.get("venit_realizat")
        if vr in (None, ""):
            raise ValueError("La codul 10 completeaza venitul brut realizat in noua situatie.")
        mz = (_D(str(ven6)) / _D(zile6)).quantize(_D("0.01"))
        baza_per = (mz * _D(zile_cm)).quantize(_D("0.01"))
        brut10 = _s.calcul_cm_cod10(baza_per, vr)
        calc = {"brut": brut10, "media_zilnica": mz, "procent": _D("0.25"), "diminuare": False,
                "zile_platite": zile_cm, "zile_ang": 0, "zile_fnuass": zile_cm,
                "brut_ang": _D("0"), "brut_fnuass": brut10}
    else:
        calc = _s.calcul_cm(ven6, zile6, zile_cm, cod=cod, spitalizare=spitalizare,
                            la_data=la_data, procent_accident=pacc)
    taxe = _s.taxe_cm(calc["brut"], cod=cod, la_data=la_data)

    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, "
            "baza, media_zilnica, procent, diminuare, zile_platite, zile_ang, zile_fnuass, "
            "brut_ang, brut_fnuass, cass, impozit, cas, net, serie, numar, data_acordare, "
            "data_inceput, data_sfarsit, loc_prescriere, diagnostic) "
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            "RETURNING id",
            (salariat_id, date.get("an"), date.get("luna"), cod, zile_cm, calc["brut"],
             ven6, calc["media_zilnica"], calc["procent"], bool(calc["diminuare"]),
             calc["zile_platite"], calc["zile_ang"], calc["zile_fnuass"],
             calc["brut_ang"], calc["brut_fnuass"], taxe["cass"], taxe["impozit"],
             taxe["cas"], taxe["net"], date.get("serie"), date.get("numar"),
             date.get("data_acordare"), date.get("data_inceput"), date.get("data_sfarsit"),
             int(date.get("loc_prescriere") or 1), date.get("diagnostic")))
        cm_id = cur.fetchone()[0]
    return {"ok": True, "id": cm_id, "calcul": {**calc, **taxe}}


def sterge_concediu(conn, salariat_id, cm_id):
    """Sterge un concediu medical (verifica apartenenta la salariat)."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM concedii_medicale WHERE id=%s AND salariat_id=%s RETURNING id",
                    (cm_id, salariat_id))
        r = cur.fetchone()
    return {"ok": r is not None}
