# -*- coding: utf-8 -*-
"""Lotul 13 (534, regula straturilor): citirile notificării e-Transport completate din factură / NIR — SQL-ul din
`etransport.din_document` / `etransport.documente_recente`, mutat fără schimbare de comportament. Zero `get_conn`, zero commit: primesc
cursorul apelantului (dicționare, `RealDictCursor`) și schema firmei."""
from core import cui_forma as _cf


def _s(schema):
    return '"%s".' % str(schema).strip('"')


def firma(cur, schema):
    """Numele și adresa firmei (locul de pornire / de sosire), sau {}."""
    cur.execute("SELECT nume, adresa, oras, judet FROM %sfirma_profil WHERE id = 1" % _s(schema))
    return cur.fetchone() or {}


def factura(cur, schema, factura_id):
    cur.execute("SELECT id, directie, tert_nume, tert_cui, tert_tara, tert_adresa, tert_oras, tert_judet, curs_bnr, moneda "
                "FROM %sfacturi WHERE id = %%s" % _s(schema), (factura_id,))
    return cur.fetchone()


def factura_linii(cur, schema, factura_id):
    cur.execute("SELECT descriere, cantitate, um, pret_unitar, valoare_neta FROM %sfactura_linii WHERE factura_id = %%s ORDER BY id"
                % _s(schema), (factura_id,))
    return cur.fetchall()


def nir(cur, schema, nir_id):
    cur.execute("SELECT id, numar, data, furnizor, cui FROM %snir WHERE id = %%s" % _s(schema), (nir_id,))
    return cur.fetchone()


def nir_linii(cur, schema, nir_id):
    s = _s(schema)
    cur.execute("SELECT l.denumire, l.cantitate, l.pret_achizitie, a.um FROM %snir_linii l LEFT JOIN %sarticole a ON a.id = l.articol_id "
                "WHERE l.nir_id = %%s ORDER BY l.id" % (s, s), (nir_id,))
    return cur.fetchall()


def adresa_furnizor(cur, schema, cui):
    """Adresa din fișa furnizorului cu acest cod fiscal (forma lui stocată, `cui_forma`), sau {}."""
    cur.execute("SELECT adresa, oras, judet FROM %sfurnizori WHERE %s = %%s ORDER BY id LIMIT 1" % (_s(schema), _cf.SQL.format(c="cui")),
                (_cf.stocare(cui) or "",))
    return cur.fetchone() or {}


def facturi_recente(cur, schema, zile):
    """Facturile (emise și primite, nu proforme, nu stornări, nu anulate / ciorne) din ultimele `zile` zile, cele mai noi întâi."""
    cur.execute("SELECT id, directie, tip, serie, numar, data_emitere, tert_nume FROM %sfacturi WHERE COALESCE(tip, 'factura') = 'factura' "
                "AND storno_din_id IS NULL AND COALESCE(status, '') NOT IN ('anulata', 'ciorna') "
                "AND data_emitere >= CURRENT_DATE - %%s ORDER BY data_emitere DESC, id DESC LIMIT 200" % _s(schema), (zile,))
    return cur.fetchall()


def nir_recente(cur, schema, zile):
    cur.execute("SELECT id, numar, data, furnizor FROM %snir WHERE data >= CURRENT_DATE - %%s ORDER BY data DESC, id DESC LIMIT 200"
                % _s(schema), (zile,))
    return cur.fetchall()
