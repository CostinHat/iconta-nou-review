# -*- coding: utf-8 -*-
"""core/salariu_istoric.py — istoricul salariului de baza pe contract (PASUL 2, forma 1).

salariu_istoric(salariat_id, valabil_din, salariu_brut) e SURSA UNICA a salariului contractual.
Citirile fiscale devin CONSTIENTE DE DATA prin salariu_la(): salariul de pe o zi = ultima intrare
cu valabil_din <= acea zi. De ce istoric si nu o valoare curenta: alin.(4) lit.a) OUG 156/2024 cere
facilitatea proratata pe "perioada din luna in care salariul e MENTINUT la nivelul minim" - deci
trebuie stiut, pentru fiecare zi, daca salariul era la minim.

[tranzitie 29.07.2026] In pasul 2a scrierile inca merg in salariati.salariu_brut; salariu_la() cade
pe acea valoare cand istoricul e gol (bridge). In 2b scrierile trec pe istoric si salariu_brut se
retrage din tabel. NU adauga citiri fiscale noi pe salariati.salariu_brut.
"""
from datetime import date, timedelta
import calendar

from core import scadente as _scad
from core.common import cota, _dec


def salariu_la(cur, schema, salariat_id, data):
    """Salariul de baza valabil la `data` (ultima intrare din istoric cu valabil_din <= data).
    Bridge tranzitie: daca istoricul e gol, valoarea curenta din salariati.salariu_brut."""
    cur.execute(f"SELECT salariu_brut FROM {schema}.salariu_istoric "
                f"WHERE salariat_id=%s AND valabil_din <= %s ORDER BY valabil_din DESC LIMIT 1",
                (salariat_id, data))
    r = cur.fetchone()
    if r is not None:
        return r[0]
    cur.execute(f"SELECT salariu_brut FROM {schema}.salariati WHERE id=%s", (salariat_id,))  # [tranzitie] bridge
    r = cur.fetchone()
    return r[0] if r else None


def salariu_curent(cur, schema, salariat_id, azi=None):
    return salariu_la(cur, schema, salariat_id, azi or date.today())


def zile_la_minim(cur, schema, salariat_id, an, luna, data_angajare=None, data_incetare=None):
    """(zile_la_minim, zile_lucratoare_luna) — zilele lucratoare din luna in care contractul e ACTIV
    SI salariul e EXACT la nivelul minim al zilei (alin.4 lit.a). Baza proratarii facilitatii."""
    def _pd(v):
        if v is None:
            return None
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v)[:10])
        except (ValueError, TypeError):
            return None
    zl = _scad.zile_lucratoare_luna(an, luna)
    prima = date(an, luna, 1)
    ultima = date(an, luna, calendar.monthrange(an, luna)[1])
    da, di = _pd(data_angajare), _pd(data_incetare)
    start = da if (da is not None and da > prima) else prima
    end = di if (di is not None and di < ultima) else ultima
    n, d = 0, start
    while d <= end:
        if _scad.e_zi_lucratoare(d):
            sal = salariu_la(cur, schema, salariat_id, d)
            sm, _ = cota("salariu_minim", d)
            if sal is not None and _dec(sal) == _dec(sm):
                n += 1
        d += timedelta(days=1)
    return n, zl
