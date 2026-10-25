# -*- coding: utf-8 -*-
"""REPOSITORY — citirile motorului TVA la încasare (`core/tva_incasare.py`).

[lotul 10, deficiența 428] Motorul decide exigibilitatea pe DATA documentului (CF art.282 alin.(3), (7)); citirile de care are nevoie
stau aici: factura, cotele liniilor, cât din TVA-ul ei a devenit deja exigibil / deductibil și cât a anulat o stornare (alin.(10)).

FIECARE FUNCȚIE PRIMEȘTE CURSORUL APELANTULUI ȘI `schema`. `schema` gol = nume necalificate (search_path pus de `db.get_conn(schema)`);
`schema` dat = nume calificate (rutele din `uc_tenants` care lucrează pe `db.get_conn()` fără search_path — aceeași convenție ca
`contare_facturi._p`). Nu deschide conexiuni, nu comite.
"""
from contextlib import contextmanager
from decimal import Decimal

from psycopg2.extras import RealDictCursor

from core import facturi as _fc   # [decizia A 02.10] definiția unică a facturii din bon fiscal

#: liniile prin care TVA-ul trece din neexigibil în exigibil: încasarea unei facturi emise (4428 -> 4427, CF art.282 alin.(3)) și
#: plata unei facturi primite cu deducerea amânată (4428 -> 4426, CF art.297 alin.(2)-(3))
LINIE_EMISA = ("4428", "4427")
LINIE_PRIMITA = ("4426", "4428")


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def _dict(cur):
    return cur.connection.cursor(cursor_factory=RealDictCursor)


@contextmanager
def search_path(cur, schema):
    """Regimul firmei (`core/regim_tva_incasare`) citește tabela pe search_path. Pe o conexiune fără search_path (nume calificate),
    îl pune pe schema firmei cât ține citirea și îl întoarce după — în aceeași tranzacție (`set_config(..., true)`)."""
    if not schema:
        yield
        return
    with _dict(cur) as c:
        c.execute("SELECT current_setting('search_path') AS sp")
        vechi = c.fetchone()["sp"]
        c.execute("SELECT set_config('search_path', %s, true)", ('"%s", public' % schema,))
    try:
        yield
    finally:
        with _dict(cur) as c:
            c.execute("SELECT set_config('search_path', %s, true)", (vechi,))


def factura(cur, schema, factura_id):
    """Antetul facturii, cu ce decide regimul ei (direcție, dată, taxare inversă, țara partenerului, furnizorul la încasare, stornarea)."""
    with _dict(cur) as c:
        c.execute("SELECT id, directie, COALESCE(tip, 'factura') AS tip, data_emitere, serie, numar, total, tva, total_lei, tva_lei, "
                  "moneda, curs_bnr, COALESCE(taxare_inversa, false) AS taxare_inversa, COALESCE(tert_tara, 'RO') AS tert_tara, "
                  "COALESCE(furnizor_tva_incasare, false) AS furnizor_tva_incasare, storno_din_id, bon_fiscal_nr, tip_operatiune, status, "
                  # [lotul 10, 428, decizia Costin „Bifă pe client”] beneficiarul afiliat, înghețat pe factură la emitere — CF art.282
                  # alin.(6) lit.d): factura către el rămâne pe regulile generale (`tva_incasare.motiv_excludere`)
                  "COALESCE(beneficiar_afiliat, false) AS beneficiar_afiliat, "
                  # [lotul 11] statutul TVA al clientului înghețat la emitere — BT-48 din e-Factura (`efactura_trimitere.incarca_factura`)
                  "tert_platitor_tva "
                  "FROM %sfacturi WHERE id = %%s" % _p(schema), (int(factura_id),))
        r = c.fetchone()
    return dict(r) if r else None


def cote_linii(cur, schema, factura_id):
    """Cotele de TVA ale liniilor facturii (procente, cum stau în `factura_linii.cota_tva`)."""
    with _dict(cur) as c:
        c.execute("SELECT cota_tva FROM %sfactura_linii WHERE factura_id = %%s ORDER BY id" % _p(schema), (int(factura_id),))
        return [r["cota_tva"] for r in c.fetchall()]


def exigibil_deja(cur, schema, factura_id, directie, pana_la=None, doar_validate=False):
    """Cât din TVA-ul facturii a trecut deja din neexigibil în exigibil (emisă) / deductibil (primită): suma liniilor 4428 = 4427 /
    4426 = 4428 de pe notele legate de factură (încasări, plăți și stornările lor, în roșu), până la `pana_la` inclusiv. `doar_validate`
    = numai notele validate (D300 declară decontările validate). [lotul 10, 428, decizia „Construiesc acum”] „Legate” = și compensările
    (`compensari_api.legaturi`: nota compensării stinge ambele facturi; linia cu direcția facturii e a ei)."""
    from core import compensari_api as _cz
    d, c_ = LINIE_EMISA if directie == "emisa" else LINIE_PRIMITA
    with _dict(cur) as c:
        c.execute("SELECT COALESCE(SUM(l.suma), 0) AS s FROM %s lg JOIN %sinregistrari i ON i.id = lg.inregistrare_id "
                  "JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                  "WHERE lg.factura_id = %%s AND l.cont_debit = %%s AND l.cont_credit = %%s AND (%%s::date IS NULL OR i.data <= %%s::date) "
                  "AND (NOT %%s OR i.status = 'validata')"
                  % (_cz.legaturi(_p(schema)), _p(schema), _p(schema)), (int(factura_id), d, c_, pana_la, pana_la, bool(doar_validate)))
        return Decimal(str(c.fetchone()["s"]))


def anulat_prin_stornari(cur, schema, factura_id, directie, pana_la=None, fara=None):
    """TVA neexigibil anulat de stornările facturii (CF art.282 alin.(10)): partea de pe 4428 din notele de contare ale facturilor care o
    stornează (emisă: 4111 = 4428 cu minus; primită: 4428 = 401 cu minus), ca sumă pozitivă. `pana_la` = numai stornările emise până
    atunci; `fara` = stornarea care se judecă acum — se numără doar cele DINAINTEA ei (id mai mic), ca împărțirea ei să nu se schimbe
    când apare o stornare ulterioară."""
    if directie == "emisa":
        cond = "l.cont_debit LIKE '4111%%' AND l.cont_credit = '4428'"
    else:
        cond = "l.cont_debit = '4428' AND (l.cont_credit LIKE '401%%' OR l.cont_credit LIKE '404%%')"
    with _dict(cur) as c:
        c.execute("SELECT COALESCE(SUM(l.suma), 0) AS s FROM %sfacturi st JOIN %sinregistrari i ON i.factura_id = st.id "
                  "JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                  "WHERE st.storno_din_id = %%s AND (%%s::int IS NULL OR st.id < %%s::int) "
                  "AND (%%s::date IS NULL OR st.data_emitere <= %%s::date) AND %s"
                  % (_p(schema), _p(schema), _p(schema), cond), (int(factura_id), fara, fara, pana_la, pana_la))
        return -Decimal(str(c.fetchone()["s"]))


def facturi_candidate(cur, schema, pana_la, clauza_status):
    """Facturile (emise și primite) cu TVA, emise până la `pana_la` inclusiv, declarabile (`clauza_status` = nomenclatorul de status),
    documente fiscale, fără taxare inversă: candidatele la TVA rămas neexigibil (D300 secțiunea A/B, lista de la ieșirea din sistem).
    [lotul 12, 252, decizia Costin 12.3 pct.5] + facturile deschise PRELUATE cu TVA încă neexigibil / nededus la preluare
    (`clauza_tip_cu_incasare`): TVA-ul lor stă pe 4428 până la încasare / plată, deci e „existent în sold la sfârșitul perioadei”."""
    from core import nomenclator_status_factura as _nsf
    with _dict(cur) as c:
        c.execute("SELECT f.id FROM %sfacturi f WHERE f.data_emitere <= %%s AND %s "
                  "AND COALESCE(f.taxare_inversa, false) = false AND f.storno_din_id IS NULL AND COALESCE(f.tva_lei, f.tva, 0) > 0 "
                  "AND %s AND %s ORDER BY f.data_emitere, f.id" % (_p(schema), _nsf.clauza_tip_cu_incasare("f"), _fc.clauza_nu_din_bon("f"), clauza_status),
                  (pana_la,))
        return [r["id"] for r in c.fetchall()]
