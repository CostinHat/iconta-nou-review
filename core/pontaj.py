"""
core/pontaj.py — F135: pontaj lunar informativ per salariat. Calcul PUR + strat DB.

Evidenta de prezenta pura - NU alimenteaza calculul salarial (DECIZII.md 17.07 F135).
Zilele lucratoare EXCLUD sarbatorile legale (scadente.e_zi_lucratoare - acelasi calendar
ca proratarea CM, OUG 158/2005 art.10). Se stocheaza doar EXCEPTIILE (zilele care nu-s
"prezent"); prezenta = absenta unui rand pe o zi lucratoare din perioada de activitate.
"""
import calendar
from datetime import date
from core.scadente import e_zi_lucratoare
from core.migrare_pontaj import STARI


def grila_pura(an, luna, data_angajare, exceptii):
    """PURA. exceptii = {date: stare}. Intoarce {zile, rezumat, data_angajare}.
    Stari per zi: nelucratoare (weekend/sarbatoare), inainte_angajare, prezent, sau
    o exceptie (absent_*/concediu_*/invoire/delegatie)."""
    zile, rezumat = [], {"prezent": 0}
    for s in STARI:
        rezumat[s] = 0
    for z in range(1, calendar.monthrange(an, luna)[1] + 1):
        d = date(an, luna, z)
        lucr = e_zi_lucratoare(d)
        in_activ = (data_angajare is None or d >= data_angajare)
        if not lucr:
            stare = "nelucratoare"
        elif not in_activ:
            stare = "inainte_angajare"
        else:
            stare = exceptii.get(d) or "prezent"
        zile.append({"zi": d.isoformat(), "zi_nr": z, "lucratoare": lucr,
                     "in_activitate": in_activ, "stare": stare})
        if stare in rezumat:
            rezumat[stare] += 1
    return {"an": an, "luna": luna, "zile": zile, "rezumat": rezumat,
            "data_angajare": data_angajare.isoformat() if data_angajare else None}


def grila(conn, schema, salariat_id, an, luna):
    """Citeste data_angajare + exceptiile lunii si construieste grila. Conexiune pe schema."""
    prima = date(an, luna, 1)
    urm = date(an + 1, 1, 1) if luna == 12 else date(an, luna + 1, 1)
    with conn.cursor() as cur:
        cur.execute("SELECT data_angajare FROM salariati WHERE id = %s", (salariat_id,))
        r = cur.fetchone()
        if r is None:
            return None
        data_ang = r[0]
        cur.execute("SELECT zi, stare FROM pontaj WHERE salariat_id = %s AND zi >= %s AND zi < %s",
                    (salariat_id, prima, urm))
        exceptii = {row[0]: row[1] for row in cur.fetchall()}
    return grila_pura(an, luna, data_ang, exceptii)


def seteaza(conn, schema, salariat_id, zi, stare):
    """Set/clear o zi. stare='prezent' (sau gol) -> sterge randul (prezenta = implicit).
    Altfel trebuie sa fie in STARI. Intoarce {ok, mesaj?}."""
    if not stare or stare == "prezent":
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pontaj WHERE salariat_id = %s AND zi = %s", (salariat_id, zi))
        return {"ok": True}
    if stare not in STARI:
        return {"ok": False, "mesaj": "stare invalida: %s" % stare}
    with conn.cursor() as cur:
        cur.execute("INSERT INTO pontaj (salariat_id, zi, stare) VALUES (%s, %s, %s) "
                    "ON CONFLICT (salariat_id, zi) DO UPDATE SET stare = EXCLUDED.stare",
                    (salariat_id, zi, stare))
    return {"ok": True}
