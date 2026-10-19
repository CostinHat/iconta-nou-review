# -*- coding: utf-8 -*-
"""core/repo_ajustari_fiscale.py — SQL-ul lui `core/ajustari_fiscale.py` (deficiența 378, 18.10.2026): tabelul `ajustari_fiscale` al
firmei. Rândurile se întorc ca tupluri și pe cursorul dict (`core/test_coloane_numite.py`).

[deficiența 404, lotul 9, decizia Costin „Da, automat”] Ajustarea scrisă automat dintr-o notă (lipsa neimputabilă de la inventar) poartă
`inregistrare_id`: intră în cumul numai cu nota VALIDATĂ — la fel ca rd.1–7, care se iau din notele validate —, deci nota în ciornă sau
respinsă la validare nu mută impozitul; ștergerea notei o șterge (ON DELETE CASCADE, `core/migrare_avans_nir_ajustare_nota.py`). Cea
scrisă de om (`inregistrare_id` NULL) intră ca până acum."""


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _t(r):
    return tuple(r.values()) if isinstance(r, dict) else tuple(r)


def lista(cur, schema, an):
    """(id, an, trim, rand, suma, descriere, document, inregistrare_id, nota_validata)."""
    cur.execute("SELECT a.id, a.an, a.trim, a.rand, a.suma, a.descriere, a.document, a.inregistrare_id, "
                "(SELECT i.status = 'validata' FROM %sinregistrari i WHERE i.id = a.inregistrare_id) AS nota_validata "
                "FROM %sajustari_fiscale a WHERE a.an = %%s ORDER BY COALESCE(a.trim, 0), a.rand, a.id" % (_q(schema), _q(schema)), (an,))
    return [_t(r) for r in cur.fetchall()]


def adauga(cur, schema, an, trim, rand, suma, descriere, document, user_id, inregistrare_id=None):
    cur.execute("INSERT INTO %sajustari_fiscale (an, trim, rand, suma, descriere, document, creat_de, inregistrare_id) "
                "VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s) RETURNING id" % _q(schema),
                (an, trim, rand, suma, descriere, document, user_id, inregistrare_id))
    return _t(cur.fetchone())[0]


def sterge(cur, schema, ajustare_id):
    cur.execute("DELETE FROM %sajustari_fiscale WHERE id = %%s" % _q(schema), (ajustare_id,))
    return cur.rowcount == 1


def cumulat(cur, schema, an, pana_la_trim):
    cur.execute("SELECT a.rand, COALESCE(SUM(a.suma), 0) AS suma FROM %sajustari_fiscale a WHERE a.an = %%s "
                "AND (a.trim IS NULL OR a.trim <= %%s) AND (a.inregistrare_id IS NULL OR EXISTS (SELECT 1 FROM %sinregistrari i "
                "WHERE i.id = a.inregistrare_id AND i.status = 'validata')) GROUP BY a.rand" % (_q(schema), _q(schema)), (an, pana_la_trim))
    return [_t(r) for r in cur.fetchall()]
