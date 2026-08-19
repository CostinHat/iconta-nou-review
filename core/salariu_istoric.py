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


def _t(schema, tabela):
    return ("%s.%s" % (schema, tabela)) if schema else tabela


def salariu_la(cur, schema, salariat_id, data):
    """Salariul de baza valabil la `data` (ultima intrare din istoric cu valabil_din <= data).
    schema=None -> tabela necalificata (context search_path, ex. salariati_api). Bridge tranzitie:
    daca istoricul e gol, valoarea curenta din salariati.salariu_brut (se retrage in 2b-coloana)."""
    cur.execute("SELECT salariu_brut FROM %s "
                "WHERE salariat_id=%%s AND valabil_din <= %%s ORDER BY valabil_din DESC LIMIT 1"
                % _t(schema, "salariu_istoric"), (salariat_id, data))
    r = cur.fetchone()
    if r is not None:
        return r["salariu_brut"] if isinstance(r, dict) else r[0]   # accepta tuplu SAU RealDictRow
    cur.execute("SELECT salariu_brut FROM %s WHERE id=%%s" % _t(schema, "salariati"), (salariat_id,))  # [tranzitie] bridge
    r = cur.fetchone()
    if r is None:
        return None
    return r["salariu_brut"] if isinstance(r, dict) else r[0]


def seteaza(cur, salariat_id, salariu_brut, valabil_din):
    """Scrie o intrare de salariu in ISTORIC (UPSERT pe salariat+data). SURSA UNICA a salariului
    contractual (PASUL 2b) - toate scrierile (creare/editare/import) trec pe aici, nu pe
    salariati.salariu_brut. Context search_path pe schema tenant (necalificat)."""
    # upsert-ok: set salariu la o data (salariat,valabil_din) - editarea aceleiasi date rescrie intentionat
    cur.execute("INSERT INTO salariu_istoric (salariat_id, valabil_din, salariu_brut) VALUES (%s, %s, %s) "
                "ON CONFLICT (salariat_id, valabil_din) DO UPDATE SET salariu_brut = EXCLUDED.salariu_brut",
                (salariat_id, valabil_din, salariu_brut))


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
