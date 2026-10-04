# -*- coding: utf-8 -*-
"""core/salariu_istoric.py — istoricul salariului de baza pe contract (PASUL 2, forma 1).

salariu_istoric(salariat_id, valabil_din, salariu_brut) e SURSA UNICA a salariului contractual.
Citirile fiscale devin CONSTIENTE DE DATA prin salariu_la(): salariul de pe o zi = ultima intrare
cu valabil_din <= acea zi. De ce istoric si nu o valoare curenta: alin.(4) lit.a) OUG 156/2024 cere
facilitatea proratata pe "perioada din luna in care salariul e MENTINUT la nivelul minim" - deci
trebuie stiut, pentru fiecare zi, daca salariul era la minim.

[punctul 4, 04.10.2026] Tranzitia s-a incheiat: scrierile au trecut pe istoric in 2b-scrieri, iar coloana
salariati.salariu_brut a fost retrasa (core/migrare_2b_coloana.py, cu backfill pentru salariatii fara istoric).
Puntea (cadere pe coloana cand istoricul e gol) a disparut odata cu ea: istoric gol = salariu necunoscut (None).
"""
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import calendar

from core import scadente as _scad
from core.common import cota, _dec


def _t(schema, tabela):
    return ("%s.%s" % (schema, tabela)) if schema else tabela


def salariu_la(cur, schema, salariat_id, data):
    """Salariul de baza valabil la `data` (ultima intrare din istoric cu valabil_din <= data), sau None.
    schema=None -> tabela necalificata (context search_path, ex. salariati_api)."""
    cur.execute("SELECT salariu_brut FROM %s "
                "WHERE salariat_id=%%s AND valabil_din <= %%s ORDER BY valabil_din DESC LIMIT 1"
                % _t(schema, "salariu_istoric"), (salariat_id, data))
    r = cur.fetchone()
    if r is None:
        return None
    return r["salariu_brut"] if isinstance(r, dict) else r[0]   # accepta tuplu SAU RealDictRow


def intrari(cur, schema, salariat_id):
    """[salariul în timp, 04.10.2026] Istoricul salariului, cronologic: [(valabil_din, salariu_brut)]."""
    cur.execute("SELECT valabil_din, salariu_brut FROM %s WHERE salariat_id=%%s ORDER BY valabil_din"
                % _t(schema, "salariu_istoric"), (salariat_id,))
    return [(r["valabil_din"], r["salariu_brut"]) if isinstance(r, dict) else (r[0], r[1]) for r in cur.fetchall()]


def seteaza(cur, salariat_id, salariu_brut, valabil_din):
    """Scrie o intrare de salariu in ISTORIC (UPSERT pe salariat+data). SURSA UNICA a salariului
    contractual (PASUL 2b) - toate scrierile (creare/editare/import) trec pe aici. Context search_path pe schema
    tenant (necalificat)."""
    # upsert-ok: set salariu la o data (salariat,valabil_din) - editarea aceleiasi date rescrie intentionat
    cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (%s, %s, %s) "
                "ON CONFLICT (salariat_id, valabil_din) DO UPDATE SET salariu_brut = EXCLUDED.salariu_brut",
                (salariat_id, valabil_din, salariu_brut))


def salariu_curent(cur, schema, salariat_id, azi=None):
    return salariu_la(cur, schema, salariat_id, azi or date.today())


def _pd(v):
    if v is None:
        return None
    if isinstance(v, date):
        return v
    try:
        return date.fromisoformat(str(v)[:10])
    except (ValueError, TypeError):
        return None


def suspendari_luna(cur, schema, salariat_id, an, luna):
    """[lot 19 pct.4c] Perioadele de suspendare FĂRĂ drepturi salariale (CFP / suspendare) care ating luna, ca
    `[(inceput, sfarsit, tip)]` tăiate la lună. Codul muncii art.49 alin.(2): suspendarea suspendă „plata drepturilor
    de natură salarială”; art.54: CFP = suspendare prin acordul părților."""
    prima = date(an, luna, 1)
    ultima = date(an, luna, calendar.monthrange(an, luna)[1])
    cur.execute("SELECT data_inceput, data_sfarsit, tip FROM %s WHERE salariat_id=%%s AND data_inceput <= %%s "
                "AND data_sfarsit >= %%s ORDER BY data_inceput" % _t(schema, "suspendari_contract"),
                (salariat_id, ultima, prima))
    out = []
    for r in cur.fetchall():
        a, b, tip = (r["data_inceput"], r["data_sfarsit"], r["tip"]) if isinstance(r, dict) else r
        out.append((max(a, prima), min(b, ultima), tip))
    return out


def _fereastra(an, luna, data_angajare, data_incetare):
    prima = date(an, luna, 1)
    ultima = date(an, luna, calendar.monthrange(an, luna)[1])
    da, di = _pd(data_angajare), _pd(data_incetare)
    return (da if (da is not None and da > prima) else prima), (di if (di is not None and di < ultima) else ultima)


def _suspendata(d, suspendari):
    return any(a <= d <= b for a, b, *_ in (suspendari or ()))


def zile_active(an, luna, data_angajare=None, data_incetare=None, suspendari=()):
    """[lot 19 pct.4c] Zilele LUCRĂTOARE (fără sărbători, OUG 158/2005 art.10 — același calendar ca proratarea CM) din
    luna în care contractul e în vigoare (după angajare, până la încetare) și NEsuspendat. Codul muncii art.159
    alin.(1): salariul e contraprestația muncii depuse în baza contractului; art.49 alin.(2): pe suspendare nu se plătește."""
    start, end = _fereastra(an, luna, data_angajare, data_incetare)
    out, d = [], start
    while d <= end:
        if _scad.e_zi_lucratoare(d) and not _suspendata(d, suspendari):
            out.append(d)
        d += timedelta(days=1)
    return out


def zile_suspendate(an, luna, data_angajare=None, data_incetare=None, suspendari=()):
    """Zilele lucrătoare din contract căzute pe o suspendare (D112 `B1_7` = ore suspendate)."""
    start, end = _fereastra(an, luna, data_angajare, data_incetare)
    n, d = 0, start
    while d <= end:
        if _scad.e_zi_lucratoare(d) and _suspendata(d, suspendari):
            n += 1
        d += timedelta(days=1)
    return n


def brut_cuvenit(cur, schema, salariat_id, an, luna, data_angajare=None, data_incetare=None, suspendari=()):
    """[lot 19 pct.4c] Brutul cuvenit pentru prezența în contract din lună: Σ (salariul de bază al ZILEI) / zile
    lucrătoare ale lunii, peste zilele active. INTERPRETARE CU TEMEI: Codul muncii art.160 alin.(2) — salariul de bază
    remunerează munca „pe parcursul unei luni calendaristice”, deci o zi lucrătoare valorează salariul lunii / zilele
    lucrătoare ale lunii (același numitor ca proratarea CM și facilitatea); art.159 alin.(1) — zilele fără contract
    sau suspendate (art.49 alin.(2)) nu se plătesc; la o schimbare de salariu în lună fiecare zi poartă salariul ei
    (salariu_istoric). Alternativă respinsă: zile calendaristice (alt numitor decât CM și facilitatea — două proratări
    diferite pe același fluturaș). De reconfirmat dacă apare o normă care tranșează metoda. Lună întreagă, fără
    schimbare și fără suspendare -> exact salariul lunii (zl × S / zl). Rotunjire aritmetică la bani."""
    zl = _scad.zile_lucratoare_luna(an, luna)
    zile = zile_active(an, luna, data_angajare, data_incetare, suspendari)
    if not zl or not zile:
        return Decimal("0.00")
    total = sum((_dec(salariu_la(cur, schema, salariat_id, d) or 0) for d in zile), Decimal(0))
    return (total / Decimal(zl)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def zile_la_minim(cur, schema, salariat_id, an, luna, data_angajare=None, data_incetare=None, suspendari=()):
    """(zile_la_minim, zile_lucratoare_luna) — zilele lucratoare din luna in care contractul e ACTIV (nesuspendat)
    SI salariul e EXACT la nivelul minim al zilei (alin.4 lit.a). Baza proratarii facilitatii. [lot 19] Zilele de
    suspendare ies: OUG 156/2024 art.LXVI alin.(4) lit.c) — suma „se diminuează în funcție de … fracția din lună
    pentru care se determină veniturile din salarii”."""
    zl = _scad.zile_lucratoare_luna(an, luna)
    n = 0
    for d in zile_active(an, luna, data_angajare, data_incetare, suspendari):
        sal = salariu_la(cur, schema, salariat_id, d)
        sm, _ = cota("salariu_minim", d)
        if sal is not None and _dec(sal) == _dec(sm):
            n += 1
    return n, zl
