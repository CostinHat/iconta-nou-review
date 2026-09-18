# -*- coding: utf-8 -*-
"""[E1, 18.09.2026] Contarea unei facturi PRIMITE mixte (21/11) se face PE COTE, nu cu `MAX(cota_tva)`
pe toată factura.

Constatarea E (contare_facturi): calea primită agrega `SUM(baza)` cu `MAX(cota_tva)` -> o factură mixtă
21/11 aplica 21% pe TOATĂ baza, deci 4426 (TVA deductibilă) supraevaluat. D300 calculează corect pe
rânduri, deci controlul încrucișat ieșea roșu — risc de „corectare" a declarației după carte. Calea
emisă gruppa deja corect pe cotă; asta o aliniază pe primită.

Caz: factură primită cu 1.000 @21% și 1.000 @11%. 4426 corect = 210 + 110 = 320.
BUG (MAX 21 pe 2.000): 4426 = 420. PICĂ pe codul de dinainte (420), TRECE după (320).
"""
from __future__ import annotations

import pytest

from core import contare_facturi
from core import db as _db

SCH = "ztest_e1_contare"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def schema_cu_factura():
    from core import tenant_provisioning as _tp
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("INSERT INTO facturi (directie, serie, numar, data_emitere, moneda) "
                        "VALUES ('primita','F','100','2026-05-10','RON') RETURNING id")
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) "
                        "VALUES (%s,'la 21',1,1000,21), (%s,'la 11',1,1000,11)", (fid, fid))
        yield {"conn": conn, "fid": fid}
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_primita_mixta_tva_pe_cote_nu_max(schema_cu_factura):
    import psycopg2.extras as _E
    conn = schema_cu_factura["conn"]
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute('SET search_path TO "%s", public' % SCH)
        f = {"id": schema_cu_factura["fid"], "directie": "primita", "data_emitere": "2026-05-10",
             "moneda": "RON", "taxare_inversa": False, "furnizor_tva_incasare": False,
             "serie": "F", "numar": "100"}
        note = contare_facturi.genereaza_note(cur, SCH, f, tva_incasare_firma=False,
                                              cont_venit_implicit=None, cont_cheltuiala="628")

    def _s(n, k):
        return n[k] if isinstance(n, dict) else getattr(n, k)
    tva_4426 = sum(int(_s(n, "suma")) for n in note if str(_s(n, "debit")) == "4426")
    assert tva_4426 == 320, (
        "4426 = %r (așteptat 320 = 1.000×21%% + 1.000×11%%; 420 = bug MAX(cota)=21%% pe toată baza)"
        % tva_4426)
