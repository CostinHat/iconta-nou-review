# -*- coding: utf-8 -*-
"""core/extrabilant.py — evidența în afara bilanțului (clasa 8), într-o singură parte (lotul 13, deficiența 507).

Comanda Costin 13.1, verbatim: „Clasa 8 se înregistrează într-o singură parte (doar debit 8035 la dare, doar credit la scoatere) și nu
intră în totalurile de rulaje (azi totalul ciornelor le include).” Înainte: `8035 = 891` / `891 = 8035` în rândurile notei — cu 891
„Bilanț de deschidere” drept contrapartidă și cu suma în totalurile notei și ale rulajelor. Structura: `core/migrare_extrabilant.py`.

O înregistrare e legată de nota operației care o produce (există și e validată odată cu ea) sau stă singură, cu documentul ei (scoaterea
din folosință, comodatul, garanția): atunci contează de la scriere.
"""
from decimal import Decimal


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def scrie(cur, schema, data, cont, sens, suma, explicatie, inregistrare_id=None, document=None, obiect_id=None, mijloc_fix_id=None):
    if not str(cont).startswith("8") or sens not in ("D", "C"):
        raise ValueError("înregistrarea în afara bilanțului cere un cont din clasa 8 și o singură parte (D sau C)")
    cur.execute("INSERT INTO %sevidenta_extrabilant (inregistrare_id, data, document, cont, sens, suma, explicatie, obiect_id, mijloc_fix_id) "
                "VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s) RETURNING id" % _p(schema),
                (inregistrare_id, data, document, cont, sens, suma, explicatie, obiect_id, mijloc_fix_id))
    r = cur.fetchone()
    return list(r.values())[0] if isinstance(r, dict) else r[0]


def sold(cur, schema, cont, data):
    """D − C pe `cont` la `data`: înregistrările de sine stătătoare și cele ale notelor VALIDATE."""
    p = _p(schema)
    cur.execute("SELECT COALESCE(SUM(CASE WHEN e.sens = 'D' THEN e.suma ELSE -e.suma END), 0) FROM %sevidenta_extrabilant e "
                "LEFT JOIN %sinregistrari i ON i.id = e.inregistrare_id WHERE e.cont = %%s AND e.data <= %%s "
                "AND (e.inregistrare_id IS NULL OR i.status = 'validata')" % (p, p), (cont, data))
    r = cur.fetchone()
    return Decimal(str((list(r.values())[0] if isinstance(r, dict) else r[0]) or 0))


def text(cont, sens, suma):
    """„8035 debit 350,00 lei (în afara bilanțului)” — pentru confirmarea operației."""
    from core.pdf_util import bani
    return "%s %s %s (în afara bilanțului)" % (cont, "debit" if sens == "D" else "credit", bani(suma, "lei"))
