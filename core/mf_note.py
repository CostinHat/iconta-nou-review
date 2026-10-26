# -*- coding: utf-8 -*-
"""core/mf_note.py — mijlocul fix ținut PE ACTIV în notele contabile (lotul 13, deficiențele 519 / 522 / 518 / 517).

Structura (DDL-ul: `core/migrare_mf_note.py`, oglindit în `tenant_template.sql`):
  - `mf_linii (linie_id, mijloc_fix_id)` — activul rândului (tabel alăturat: rândul notei validate nu se schimbă); amortizarea
    ÎNREGISTRATĂ a unui activ e suma rândurilor LUI pe contul de amortizare (credit − debit), din notele validate, plus partea lui din
    soldul preluat — nu soldul contului împărțit între active;
  - `mf_note` — nota care aduce activul în registru (`intrare`) sau îl scoate (`iesire`); triggerul bazei îl face activ / inactiv la
    VALIDAREA notei și îl scoate la ștergerea ciornei de intrare (comanda Costin 13.1, 519: „un activ adăugat sau schimbat de o notă
    există în registru numai după validarea ei și dispare la ștergere”).
"""
from decimal import Decimal

B = Decimal("0.01")


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def _rows(cur):
    return [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]


def leaga(cur, schema, mijloc_fix_id, nota_id, fel):
    """Nota `nota_id` aduce (`intrare`) sau scoate (`iesire`) activul; efectul pe registru îl face triggerul la validarea ei."""
    if fel not in ("intrare", "iesire"):
        raise ValueError("fel necunoscut: %r" % fel)
    cur.execute("INSERT INTO %smf_note (inregistrare_id, mijloc_fix_id, fel) VALUES (%%s, %%s, %%s)" % _p(schema),
                (nota_id, mijloc_fix_id, fel))


def adauga_linie(cur, schema, nota_id, debit, credit, suma, mijloc_fix_id, partener_cui=None, partener_nume=None):
    """Un rând de notă cu activul lui (și, unde e cazul, partenerul — locatorul la primirea în leasing).

    [lotul 13, deficiența 536 — „amortizarea moștenește centrul activului”] Rândul de cheltuială / venit al activului (6811 = 28…, casarea,
    reevaluarea) poartă centrul de cost al activului (`mijloace_fixe.centru_cost_id`); rândurile fără clasa 6 / 7 nu poartă centru."""
    from core import centre_cost_api as _cc
    p = _p(schema)
    centru = None
    if _cc.e_rand_de_centru(debit, credit):
        cur.execute("SELECT centru_cost_id FROM %smijloace_fixe WHERE id = %%s" % p, (mijloc_fix_id,))
        r = cur.fetchone()
        centru = (r["centru_cost_id"] if isinstance(r, dict) else r[0]) if r else None
    cur.execute("INSERT INTO %sinregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma, partener_cui, partener_nume, centru_cost_id) "
                "VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s) RETURNING id" % p,
                (nota_id, debit, credit, suma, partener_cui, partener_nume, centru))
    r = cur.fetchone()
    lid = r["id"] if isinstance(r, dict) else r[0]
    cur.execute("INSERT INTO %smf_linii (linie_id, mijloc_fix_id) VALUES (%%s, %%s)" % p, (lid, mijloc_fix_id))
    return lid


def in_asteptare(cur, schema):
    """{mijloc_fix_id: {"intrare"|"iesire": (nota_id, data)}} — notele NEVALIDATE care aduc sau scot un activ."""
    p = _p(schema)
    cur.execute("SELECT n.mijloc_fix_id, n.fel, n.inregistrare_id, i.data FROM %smf_note n JOIN %sinregistrari i ON i.id = n.inregistrare_id "
                "WHERE i.status <> 'validata' ORDER BY i.data, i.id" % (p, p))
    out = {}
    for mid, fel, nid, data in _rows(cur):
        out.setdefault(mid, {})[fel] = (nid, data)
    return out


def iesire_in_asteptare(cur, schema, mijloc_fix_id):
    """(nota_id, data) a casării nevalidate a activului, sau None."""
    return in_asteptare(cur, schema).get(int(mijloc_fix_id), {}).get("iesire")


def pe_activ(cur, schema, pana_la):
    """{mijloc_fix_id: {"inregistrat": Decimal, "luni": {(an, luna)}, "luni_ciorna": {(an, luna)}}} — din rândurile cu activ pe conturile
    de amortizare (28…): credit − debit în notele validate până la `pana_la`; lunile = lunile notelor care trec amortizarea lunii pe
    activ (6811 = 28…), validate / nevalidate."""
    p = _p(schema)
    cur.execute("SELECT ml.mijloc_fix_id, i.status, i.data, l.cont_debit, l.cont_credit, l.suma FROM %sinregistrari_linii l "
                "JOIN %smf_linii ml ON ml.linie_id = l.id JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE (l.cont_debit LIKE '28%%' OR l.cont_credit LIKE '28%%')" % (p, p, p))
    out = {}
    for mid, status, data, cd, cc, suma in _rows(cur):
        e = out.setdefault(mid, {"inregistrat": Decimal("0"), "luni": set(), "luni_ciorna": set()})
        s = Decimal(str(suma))
        if status == "validata" and data <= pana_la:
            e["inregistrat"] += s if str(cc).startswith("28") else -s
        if str(cd).startswith("68") and str(cc).startswith("28"):
            (e["luni"] if status == "validata" else e["luni_ciorna"]).add((data.year, data.month))
    return out


def nealocat_pe_cont(cur, schema, cont, pana_la):
    """Rândurile validate pe contul de amortizare FĂRĂ activ (o notă manuală, una dinaintea lotului 13 nepotrivită): credit − debit."""
    p = _p(schema)
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_credit = %%s OR l.cont_credit LIKE %%s THEN l.suma ELSE 0 END), 0) - "
                "COALESCE(SUM(CASE WHEN l.cont_debit = %%s OR l.cont_debit LIKE %%s THEN l.suma ELSE 0 END), 0) "
                "FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data <= %%s AND NOT EXISTS (SELECT 1 FROM %smf_linii ml WHERE ml.linie_id = l.id)" % (p, p, p),
                (cont, cont + ".%", cont, cont + ".%", pana_la))
    r = cur.fetchone()
    return Decimal(str((list(r.values())[0] if isinstance(r, dict) else r[0]) or 0))
