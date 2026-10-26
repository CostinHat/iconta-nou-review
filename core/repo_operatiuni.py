# -*- coding: utf-8 -*-
"""core/repo_operatiuni.py — DEPOZITUL operațiunilor speciale (lotul 13, pachetul ops).

Regula straturilor (PLAN_HARDENING.md:842): depozitul e singurul care știe SQL. Use-case-urile din `core/uc_tenants.py` (decontul,
creditul, obiectele de inventar, producția, marja / aurul din stoc, subvenția, chiria, provizioanele, sponsorizarea, lichidarea,
listele formularelor) cheamă de aici citirile și scrierile lor; tranzacția rămâne a apelantului — nicio funcție nu deschide conexiuni
și nu comite. Fiecare primește cursorul apelantului (tuplu sau dicționar) și întoarce valori simple."""


def _p(schema):
    return '"%s".' % schema


def _rand(r):
    return (tuple(r.values()) if isinstance(r, dict) else tuple(r)) if r is not None else None


def _randuri(cur):
    return [_rand(r) for r in cur.fetchall()]


# ── vânzarea din stoc (marjă, aur — 548) ─────────────────────────────────────────────────────────────────────────────────────────────
def vanzare_din_stoc_scrie(cur, schema, inregistrare_id, fel, miscare_id, nota_iesire_id, articol_id, cantitate, pret_vanzare,
                           pret_cumparare, tva, client_cui, client_nume, document):
    """Vânzarea și ieșirea ei din stoc, legate (`vanzari_din_stoc`)."""
    cur.execute('INSERT INTO %svanzari_din_stoc (inregistrare_id, fel, miscare_id, nota_iesire_id, articol_id, cantitate, pret_vanzare, '
                'pret_cumparare, tva, client_cui, client_nume, document) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s)'
                % _p(schema), (inregistrare_id, fel, miscare_id, nota_iesire_id, articol_id, cantitate, pret_vanzare, pret_cumparare, tva,
                               client_cui, client_nume, document))


def vanzari_marja_luna(cur, schema, luna):
    """[(id, data, descriere, status, pret_vanzare, pret_cumparare, tva, client_nume, document)] — vânzările în regim de marjă din luna
    „AAAA-LL”, în ordinea datei."""
    p = _p(schema)
    cur.execute('SELECT i.id, i.data, i.descriere, i.status, v.pret_vanzare, v.pret_cumparare, v.tva, v.client_nume, v.document '
                'FROM %svanzari_din_stoc v JOIN %sinregistrari i ON i.id = v.inregistrare_id '
                "WHERE v.fel = 'marja' AND to_char(i.data, 'YYYY-MM') = %%s ORDER BY i.data, i.id" % (p, p), (luna,))
    return _randuri(cur)


# ── facturile ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def scadente_facturi(cur, schema, ids):
    """{factura_id: data_scadenta} pentru facturile cerute."""
    if not ids:
        return {}
    cur.execute("SELECT id, data_scadenta FROM %sfacturi WHERE id = ANY(%%s)" % _p(schema), (list(ids),))
    return {r[0]: r[1] for r in _randuri(cur)}


def factura_primita_dupa_furnizor_si_numar(cur, schema, furnizor_cui, numar):
    """(id, data_emitere, numar) a facturii primite de la furnizor (CUI cu sau fără „RO”) cu acel număr, sau None.

    [lotul 11, decizia Costin 10.3 pct.4] CUI-ul comparat în forma păstrată, pe ambele părți (`cui_forma.SQL` / `cui_forma.stocare`):
    rândurile vechi pot avea „RO” sau spații, iar codul de TVA al altui stat își păstrează prefixul."""
    from core import cui_forma as _cf
    cur.execute("SELECT id, data_emitere, numar FROM %sfacturi WHERE directie = 'primita' AND upper(btrim(numar)) = upper(btrim(%%s)) "
                "AND %s = %%s ORDER BY id LIMIT 1" % (_p(schema), _cf.SQL.format(c="tert_cui")), (str(numar), _cf.stocare(furnizor_cui)))
    return _rand(cur.fetchone())


def leaga_nota_de_factura(cur, schema, inregistrare_id, factura_id):
    """Nota (ciornă) legată de factura din care provine — soldul facturii o socotește."""
    cur.execute("UPDATE %sinregistrari SET factura_id = %%s WHERE id = %%s" % _p(schema), (factura_id, inregistrare_id))


# ── stocul ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def contul_stocului(cur, schema, articol_id):
    """Contul de stoc al articolului (șir; „” fără)."""
    cur.execute("SELECT cont_stoc FROM %sarticole WHERE id = %%s" % _p(schema), (articol_id,))
    r = _rand(cur.fetchone())
    return str((r[0] if r else "") or "")


def leaga_miscarea_de_nota(cur, schema, miscare_id, inregistrare_id):
    """Mișcarea de stoc (intrarea produselor) e a notei care o înregistrează — documentul cu mișcare de stoc."""
    cur.execute("UPDATE %smiscari_stoc SET inregistrare_id = %%s WHERE id = %%s" % _p(schema), (inregistrare_id, miscare_id))


def rulaje_productie_an(cur, schema, document_obtinere, de_la, pana_la):
    """(intrările pe 345 la preț de înregistrare, diferențele de preț ale intrărilor pe 348) din notele VALIDATE între cele două date —
    diferențele numai pe notele de obținere (`document_ref LIKE document_obtinere`)."""
    p = _p(schema)
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_debit LIKE '345%%%%' THEN l.suma ELSE 0 END), 0) AS intrari_345, "
                "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '348%%%%' AND i.document_ref LIKE %%s THEN l.suma ELSE 0 END), 0) "
                "- COALESCE(SUM(CASE WHEN l.cont_credit LIKE '348%%%%' AND i.document_ref LIKE %%s THEN l.suma ELSE 0 END), 0) AS dif_intrari "
                "FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data >= %%s AND i.data <= %%s" % (p, p),
                (document_obtinere, document_obtinere, de_la, pana_la))
    return _rand(cur.fetchone())


# ── obiectele de inventar (505–508) ─────────────────────────────────────────────────────────────────────────────────────────────────
_OBIECT = ("SELECT o.id, o.denumire, o.valoare, o.data_intrare, o.nota_dare_id, o.scoatere_id, ii.status AS stare_intrare, "
           "di.status AS stare_dare, o.factura_id FROM %sobiecte_inventar o LEFT JOIN %sinregistrari ii ON ii.id = o.nota_intrare_id "
           "LEFT JOIN %sinregistrari di ON di.id = o.nota_dare_id")


def obiect_inventar(cur, schema, obiect_id):
    """(id, denumire, valoare, data_intrare, nota_dare_id, scoatere_id, stare_intrare, stare_dare, factura_id) sau None."""
    p = _p(schema)
    cur.execute((_OBIECT + " WHERE o.id = %%s") % (p, p, p), (obiect_id,))
    return _rand(cur.fetchone())


def obiecte_inventar(cur, schema):
    """Toate obiectele de inventar, cu starea notelor lor, în ordinea intrării (aceleași coloane ca `obiect_inventar`)."""
    p = _p(schema)
    cur.execute((_OBIECT + " ORDER BY o.data_intrare, o.id") % (p, p, p))
    return _randuri(cur)


def obiect_inventar_scrie(cur, schema, denumire, valoare, data_intrare, furnizor_cui, furnizor_nume, factura_numar, nota_intrare_id,
                          factura_id):
    """Obiectul intrat în gestiune, cu nota și factura lui; întoarce id-ul."""
    cur.execute("INSERT INTO %sobiecte_inventar (denumire, valoare, data_intrare, furnizor_cui, furnizor_nume, factura_numar, "
                "nota_intrare_id, factura_id) VALUES (%%s, %%s, %%s, %%s, %%s, %%s, %%s, %%s) RETURNING id" % _p(schema),
                (denumire, valoare, data_intrare, furnizor_cui, furnizor_nume, factura_numar, nota_intrare_id, factura_id))
    return _rand(cur.fetchone())[0]


def obiect_dat_in_folosinta(cur, schema, obiect_id, nota_id):
    cur.execute("UPDATE %sobiecte_inventar SET nota_dare_id = %%s WHERE id = %%s" % _p(schema), (nota_id, obiect_id))


def obiect_scos_din_folosinta(cur, schema, obiect_id, extrabilant_id):
    cur.execute("UPDATE %sobiecte_inventar SET scoatere_id = %%s WHERE id = %%s" % _p(schema), (extrabilant_id, obiect_id))


# ── notele ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def dividende_117_nevalidate(cur, schema):
    """[{id, suma}] — notele NEVALIDATE de dividende care reclasifică 117 = 1171 (cu rândul 457 în aceeași notă), cu suma reclasificată."""
    p = _p(schema)
    cur.execute("SELECT i.id, SUM(l.suma) AS suma FROM %sinregistrari i JOIN %sinregistrari_linii l "
                "ON l.inregistrare_id = i.id WHERE i.status <> 'validata' AND l.cont_debit = '117' AND l.cont_credit = '1171' "
                "AND EXISTS (SELECT 1 FROM %sinregistrari_linii x WHERE x.inregistrare_id = i.id AND x.cont_credit LIKE '457%%') "
                "GROUP BY i.id" % (p, p, p))
    return [{"id": r[0], "suma": r[1]} for r in _randuri(cur)]


def venituri_70x(cur, schema, de_la, pana_la):
    """Rulajul creditor al conturilor 70x din notele VALIDATE între cele două date (cifra de afaceri)."""
    p = _p(schema)
    cur.execute("SELECT COALESCE(SUM(l.suma), 0) FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND l.cont_credit LIKE '70%%%%' AND i.data >= %%s AND i.data <= %%s" % (p, p), (de_la, pana_la))
    r = _rand(cur.fetchone())
    return r[0] if r else 0


def nota_dupa_numar(cur, schema, numar):
    """(id, status) a notei cu numărul dat, sau None."""
    cur.execute("SELECT id, status FROM %sinregistrari WHERE numar = %%s" % _p(schema), (numar,))
    return _rand(cur.fetchone())


def sterge_nota(cur, schema, nota_id):
    """Ciorna regenerată (reluarea subvenției) se înlocuiește: rândurile cad prin ON DELETE CASCADE."""
    cur.execute("DELETE FROM %sinregistrari WHERE id = %%s" % _p(schema), (nota_id,))


def subventii_pe_activ(cur, schema):
    """{mijloc_fix_id: (subvenția primită pe 4751, reluată deja pe 758x)} din notele VALIDATE, pe rândurile cu activ (`mf_linii`)."""
    p = _p(schema)
    cur.execute("SELECT ml.mijloc_fix_id, SUM(CASE WHEN l.cont_credit = '4751' THEN l.suma ELSE 0 END) AS primit, "
                "SUM(CASE WHEN l.cont_debit = '4751' AND l.cont_credit LIKE '758%%' THEN l.suma ELSE 0 END) AS reluat "
                "FROM %sinregistrari_linii l JOIN %smf_linii ml ON ml.linie_id = l.id JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND (l.cont_credit = '4751' OR l.cont_debit = '4751') GROUP BY ml.mijloc_fix_id" % (p, p, p))
    return {r[0]: (r[1], r[2]) for r in _randuri(cur) if r[1]}


# ── salariatul (decontul, 670) ───────────────────────────────────────────────────────────────────────────────────────────────────────
def salariat(cur, schema, salariat_id):
    """{id, nume, prenume, cnp, data_angajare, data_incetare} sau None."""
    cur.execute("SELECT id, nume, prenume, cnp, data_angajare, data_incetare FROM %ssalariati WHERE id = %%s" % _p(schema), (salariat_id,))
    r = _rand(cur.fetchone())
    return dict(zip(("id", "nume", "prenume", "cnp", "data_angajare", "data_incetare"), r)) if r else None


# ── mijlocul fix de pe factura primită (601) ─────────────────────────────────────────────────────────────────────────────────────────
def linii_factura(cur, schema, factura_id):
    """[(id, cantitate, pret_unitar, valoare_neta)] — liniile facturii, în ordinea lor (aceeași ordine ca `conturi` / `imobilizari`)."""
    cur.execute("SELECT id, cantitate, pret_unitar, valoare_neta FROM %sfactura_linii WHERE factura_id = %%s ORDER BY id" % _p(schema),
                (factura_id,))
    return _randuri(cur)


def moneda_si_cursul_facturii(cur, schema, factura_id):
    """{id, moneda, curs_bnr} — ce cere `sume_lei.curs_factura`."""
    cur.execute("SELECT id, moneda, curs_bnr FROM %sfacturi WHERE id = %%s" % _p(schema), (factura_id,))
    r = _rand(cur.fetchone())
    return {"id": r[0], "moneda": r[1], "curs_bnr": r[2]} if r else {"id": factura_id, "moneda": "RON", "curs_bnr": None}


# ── contul de trezorerie al decontării în valută (decizia Costin după 524 / 504) ─────────────────────────────────────────────────────
def conturi_cu_prefix(cur, schema, sintetice):
    """[(simbol, denumire)] — conturile din planul firmei care sunt unul din `sintetice` sau un analitic al lor, în ordinea simbolului."""
    cur.execute("SELECT simbol, denumire FROM %splan_conturi WHERE simbol LIKE ANY(%%s) ORDER BY simbol" % _p(schema),
                ([s + "%" for s in sintetice],))
    return _randuri(cur)
