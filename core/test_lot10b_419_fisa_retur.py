# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 419 (partea fișei) — comanda Costin 10.2 pct.7f, verbatim] „în fișa de magazie, rândul de retur din stornare
apare «−-1 · -27,50 lei»”. Stornarea în roșu a ieșirii (retur) are cantitatea și valoarea cu minus (OMFP 1802/2014 pct.69: „corectarea
cu semnul minus a operațiunii inițiale (stornare în roșu)”), iar ecranul punea și semnul rândului în față. Ruta fișei spune acum care
rând e o stornare (`storno`), ca ecranul să pună UN singur semn și să numească rândul (`firme.js::miscareFisa`, probat în browser de
`e2e_lot10b_stoc.py::test_def_419_…`). Schemă efemeră din template, în tranzacție anulată."""
import io

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_419_fisa"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
            yield c
        finally:
            c.rollback()


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_def_419_fisa_spune_care_rand_e_stornarea_in_rosu(conn):
    from core import stocuri_cv_api as scv
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa B', 'buc') RETURNING id")
        aid = cur.fetchone()[0]
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document) VALUES "
                    "(%s, '2026-10-01', 'intrare', 2, 27.5, 55, 'NIR nr 3 din 01.10.2026')", (aid,))
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document) VALUES "
                    "(%s, '2026-10-05', 'iesire', 1, 27.5, 'Factură F1A9 din 05.10.2026') RETURNING id", (aid,))
        iesire = cur.fetchone()[0]
        # returul la stornare (`retur_la_stornare`): aceeași ieșire, cu minus, legată de ea
        cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, valoare, document, anuleaza_id) VALUES "
                    "(%s, '2026-10-20', 'iesire', -1, -27.5, 'Factură F1A10 din 20.10.2026', %s)", (aid, iesire))
    linii = scv.fisa(conn, SCH, aid)["linii"]
    # OMFP 1802/2014 pct.69: stornarea în roșu = operațiunea inițială cu semnul minus — rândul ei se numește, celelalte nu
    assert [(l["tip"], l["storno"]) for l in linii] == [("intrare", False), ("iesire", False), ("iesire", True)], linii
    assert (linii[-1]["cantitate"], linii[-1]["valoare"]) == ("-1.000", "-27.50") and linii[-1]["sold_cantitate"] == "2.000", linii[-1]
