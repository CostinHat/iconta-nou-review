# -*- coding: utf-8 -*-
"""[lotul 13, deficiențele 511 / 512, valul 5] Ajustarea creanței pe factura aleasă din lista facturilor emise neîncasate.

Picătura plasei din 26.10.2026: lista (`GET operatiuni-date?ce=facturi_neincasate`) ieșea 500 — `reconciliere_api.facturi_deschise`
n-are numele partenerului (`tert_nume`); detaliile le dă `facturi_deschise_detalii`. Testul reface lista și nota pe o schemă efemeră.

TEMEI: CF art.26 alin.(1) lit.c) („30% din valoarea creanțelor […] neîncasate într-o perioadă ce depășește 270 de zile de la termenul
de scadență”); restul (70%) e nedeductibil și intră în ajustările rezultatului fiscal (D101 rd.29)."""
from decimal import Decimal

from core.test_lot13_ops_schema import CTX, nota, schema_ops


def _factura_scadenta(cur):
    """Factura emisă F1 nr. 9 de 1.210 lei, scadentă pe 01.12.2025, contată prin notă validată (4111 = 707 / 4427)."""
    cur.execute("INSERT INTO facturi (serie, numar, data_emitere, data_scadenta, directie, moneda, total, total_lei, tert_nume, tert_cui) "
                "VALUES ('F1', '9', '2025-11-01', '2025-12-01', 'emisa', 'RON', 1210, 1210, 'Client Restant SRL', '14399840') RETURNING id")
    fid = cur.fetchone()[0]
    nid = nota(cur, "2025-11-01", [("4111", "707", 1000), ("4111", "4427", 210)])
    cur.execute("UPDATE inregistrari SET factura_id = %s, sursa = 'facturi' WHERE id = %s", (fid, nid))
    return fid


def test_def_511_lista_facturilor_neincasate_are_partenerul_soldul_si_zilele(monkeypatch):
    """MUTAȚIE: lista citită din `facturi_deschise` (fără detalii) -> KeyError „tert_nume” (500) -> pică."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        fid = _factura_scadenta(cur)
        r = uc.operatiuni_date(1, "facturi_neincasate", {"data": "2026-10-15"}, CTX)
        f = next(x for x in r["facturi"] if x["id"] == fid)
        # 01.12.2025 -> 15.10.2026 = 318 zile de la scadență
        assert (f["document"], f["partener"], Decimal(str(f["sold"])), f["zile"]) == ("F1 nr. 9", "Client Restant SRL", Decimal("1210.00"), 318), f


def test_def_512_nota_pe_factura_aleasa_spune_partile_fiscale(monkeypatch):
    """318 zile > 270: 30% deductibil (363,00), 70% nedeductibil (847,00) — CF art.26 alin.(1) lit.c)."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        fid = _factura_scadenta(cur)
        r = uc.nota_provizion_ep(1, {"data": "2026-10-15", "fel": "creanta", "factura_id": fid, "garantata": False, "afiliata": False,
                                     "faliment": False}, CTX)
        cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = %s", (r["inregistrare_id"],))
        assert cur.fetchall() == [("6814", "491", "1210.00")]
        assert (r["deductibil"], r["nedeductibil"], r["zile_de_la_scadenta"]) == ("363.00", "847.00", 318), r
