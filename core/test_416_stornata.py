# -*- coding: utf-8 -*-
"""[deficiența 416, retestul Costin 19.10.2026] „După stornarea integrală F1A8 (F1A9, −121 EUR), F1A8 «neîncasată»; trebuie «stornată»,
fără scadențar/notificări.”

O singură definiție (`repo_facturi.SQL_STORNARI`, `facturi.TOLERANTA_STORNATA`): rămasul facturii = totalul + stornările ei (negative). Temei: CF
art.330 alin.(1) lit.b): factura cu valorile cu semnul minus, „în care se înscriu numărul și data facturii corectate”, anulează valorile
facturii corectate — nu mai e nimic de încasat. Schemă efemeră din template, în tranzacție anulată (fixtura lui 417)."""
import datetime

import pytest

from core import facturi_api, repo_notificari_scadenta, repo_portal, repo_scadentar
from core.test_417_storno_trimitere import _LINIE, _db_ok, _storno, conn  # noqa: F401 — fixtura și ajutoarele ei


def _ids(rows):
    return [r["id"] if isinstance(r, dict) else r[0] for r in rows]


def _nota_validata(conn, fid):
    """Nota facturii, VALIDATĂ de contabil (date de pornire): `repo_portal.facturi_deschise_validate` — cititorul previziunii clientului
    (cashflow, 559) — numără numai facturile cu nota validată."""
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE factura_id = %s AND sursa = 'facturi'", (fid,))
        assert cur.rowcount >= 1, "factura n-are nota ei de facturi"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_stornata_integral_nu_mai_e_de_incasat(conn):
    r, s, _d = _storno(conn)
    _nota_validata(conn, r["factura_id"])
    d = facturi_api.detalii_factura(conn, r["factura_id"])
    assert d["stare_incasare"] == {"stare": "stornata", "incasat": "0.00", "total": "121.00", "stornat": "121.00"}, d["stare_incasare"]
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        assert r["factura_id"] not in _ids(repo_scadentar.select_facturi(cur))
        assert r["factura_id"] not in _ids(repo_notificari_scadenta.select_facturi(cur, datetime.date(2026, 12, 31)))
        # previziunea clientului (cashflow): factura stornată integral nu mai intră, una nestornată cu nota validată (martorul) intră
        martor = facturi_api.creeaza_factura(conn, "F1A12", "2026-10-19", "emisa", [dict(_LINIE)], data_scadenta="2026-11-18",
                                             tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840", status="emisa")["factura_id"]
        _nota_validata(conn, martor)
        deschise = _ids(repo_portal.facturi_deschise_validate(cur, "emisa"))
        assert martor in deschise and r["factura_id"] not in deschise, (martor, r["factura_id"], deschise)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_stornata_partial_ramane_cu_restul(conn):
    """O stornare parțială (o reducere de preț de 21 lei): factura rămâne de încasat cu 100 lei, în toate cele patru locuri."""
    r = facturi_api.creeaza_factura(conn, "F1A10", "2026-10-19", "emisa", [dict(_LINIE)], data_scadenta="2026-11-18",
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840", status="emisa")
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, tert_nume, tert_cui, status, storno_din_id, tip) "
                    "VALUES ('F1A11','F1A','2026-10-20','emisa',-21,-3.64,'DANTE INTERNATIONAL SA','RO14399840','emisa',%s,'factura')",
                    (r["factura_id"],))
    _nota_validata(conn, r["factura_id"])
    d = facturi_api.detalii_factura(conn, r["factura_id"])
    assert d["stare_incasare"] == {"stare": "neincasata", "incasat": "0.00", "total": "100.00", "stornat": "21.00"}, d["stare_incasare"]
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        assert [float(x["suma"]) for x in repo_scadentar.select_facturi(cur) if x["id"] == r["factura_id"]] == [100.0]
        assert [float(x["suma"]) for x in repo_notificari_scadenta.select_facturi(cur, datetime.date(2026, 12, 31))
                if x["id"] == r["factura_id"]] == [100.0]
        assert [float(x["rest_lei"]) for x in repo_portal.facturi_deschise_validate(cur, "emisa") if x["id"] == r["factura_id"]] == [100.0]
