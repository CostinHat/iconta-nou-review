# -*- coding: utf-8 -*-
"""core/repo_ajustari_fiscale.py — SQL-ul lui `core/ajustari_fiscale.py` (deficiența 378, 18.10.2026): tabelul `ajustari_fiscale` al
firmei. Rândurile se întorc ca tupluri și pe cursorul dict (`core/test_coloane_numite.py`)."""


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _t(r):
    return tuple(r.values()) if isinstance(r, dict) else tuple(r)


def lista(cur, schema, an):
    cur.execute("SELECT id, an, trim, rand, suma, descriere, document FROM %sajustari_fiscale WHERE an = %%s "
                "ORDER BY COALESCE(trim, 0), rand, id" % _q(schema), (an,))
    return [_t(r) for r in cur.fetchall()]


def adauga(cur, schema, an, trim, rand, suma, descriere, document, user_id):
    cur.execute("INSERT INTO %sajustari_fiscale (an, trim, rand, suma, descriere, document, creat_de) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s) "
                "RETURNING id" % _q(schema), (an, trim, rand, suma, descriere, document, user_id))
    return _t(cur.fetchone())[0]


def sterge(cur, schema, ajustare_id):
    cur.execute("DELETE FROM %sajustari_fiscale WHERE id = %%s" % _q(schema), (ajustare_id,))
    return cur.rowcount == 1


def cumulat(cur, schema, an, pana_la_trim):
    cur.execute("SELECT rand, COALESCE(SUM(suma), 0) AS suma FROM %sajustari_fiscale WHERE an = %%s AND (trim IS NULL OR trim <= %%s) "
                "GROUP BY rand" % _q(schema), (an, pana_la_trim))
    return [_t(r) for r in cur.fetchall()]
