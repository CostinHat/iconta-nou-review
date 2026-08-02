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


def seteaza(conn, schema, salariat_id, zi, stare, tenant_id=None):
    """Set/clear o zi. stare='prezent' (sau gol) -> sterge randul (prezenta = implicit).
    Altfel trebuie sa fie in STARI. Intoarce {ok, mesaj?}.

    Reversibilitate (DESIGN_SYSTEM cap.23): o modificare DE-CONFIRMA automat luna (pontaj) - calculele din
    aval re-blocheaza pana la re-confirmare. DUPA depunerea D112 pe luna (tenant_id dat), editarea se
    BLOCHEAZA (fapt declarat la ANAF) -> corectie prin rectificativa."""
    from datetime import date as _date
    from core import perioada as _per
    if stare not in STARI and stare and stare != "prezent":
        return {"ok": False, "mesaj": "stare invalida: %s" % stare}
    d = zi if isinstance(zi, _date) else _date.fromisoformat(str(zi)[:10])
    an, luna = d.year, d.month
    if tenant_id is not None:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM public.declaratii_depuse WHERE tenant_id = %s AND an = %s AND luna = %s "
                        "AND tip = 'd112' LIMIT 1", (tenant_id, an, luna))
            if cur.fetchone():
                return {"ok": False, "mesaj": "Pontajul lunii %02d.%04d nu se poate modifica: D112 e deja depusa "
                        "la ANAF. Corecteaza prin rectificativa (nu prin editare libera)." % (luna, an)}
    if not stare or stare == "prezent":
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pontaj WHERE salariat_id = %s AND zi = %s", (salariat_id, zi))
    else:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO pontaj (salariat_id, zi, stare) VALUES (%s, %s, %s) "
                        "ON CONFLICT (salariat_id, zi) DO UPDATE SET stare = EXCLUDED.stare",
                        (salariat_id, zi, stare))
    _per.deconfirma(conn, schema, an, luna, "pontaj")   # modificarea invalideaza confirmarea
    return {"ok": True}


# HG 1045/2018 art.10 alin.(3): tichetul de masa se acorda pe zile EFECTIV lucrate. Zilele de concediu de
# odihna, delegatie/detasare, absente (motivate/nemotivate) si invoire NU dau drept la tichet. Concediul
# MEDICAL se scade separat (din evidenta CM, nu se dubleaza aici).
_STARI_FARA_TICHET = ("concediu_odihna", "delegatie", "absent_motivat", "absent_nemotivat", "invoire")


def zile_fara_tichet(conn, schema, salariat_id, an, luna):
    """Zilele LUCRATOARE din pontaj cu o stare care NU da drept la tichet de masa (CO/delegatie/absente/
    invoire), pentru corectia numarului de tichete (D2, HG 1045/2018 art.10(3)). CM exclus (scazut separat).
    Firma FARA pontaj -> 0 (comportament neschimbat, fara blocaj - blocajul-daca-necompletat cere un semnal
    de confirmare a lunii, vezi DECIZII 02.08). None-safe."""
    g = grila(conn, schema, salariat_id, an, luna)
    if g is None:
        return 0
    return sum(g["rezumat"].get(st, 0) for st in _STARI_FARA_TICHET)
