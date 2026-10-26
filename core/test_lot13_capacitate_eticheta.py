# -*- coding: utf-8 -*-
"""[lotul 13, 694 — „Tipare și Capacitate arată tipul intern `nota` ca «NOTA»”, clasa 569 / 163]

Capacitate › Timp pe tip scria `tip.toUpperCase()` din coada de pregătiri: o notă contabilă pregătită de asistent apărea „NOTA". Eticheta se
calculează acum în backend cu aceeași regulă ca Tipare (`tipare_api.eticheta_tip`: „Note contabile”), iar ecranul o afișează ca atare.

Date: cabinet sintetic în tranzacție ANULATĂ (fixture-ul `tx` din `test_lot11_t2_inlocuiri`), an 2099.
Temei: N/A — indicatori interni ai cabinetului (nu regulă fiscală).
MUTAȚIA: `"eticheta": eticheta_tip(...)` -> `t["tip"].upper()` în `capacitate_api` -> „NOTA” -> pică.
"""
from core.test_lot11_t2_inlocuiri import tx, _declaratie  # noqa: F401  (tx = fixture)


def test_694_timpul_pe_tip_numeste_notele_contabile(tx):
    from core import capacitate_api
    conn, cab, asist, _valid, tids, _azi = tx
    for tip, tid, luna in (("nota", tids[0], 1), ("d300", tids[1], 2)):
        cid = _declaratie(conn, cab, tids[0] if tip == "nota" else tid, asist, luna, tip=tip)
        with conn.cursor() as cur:
            cur.execute("UPDATE public.declaratii_coada SET inceput_la = creat_la - interval '5 minutes' WHERE id = %s", (cid,))
    pe_tip = {x["tip"]: x["eticheta"] for x in capacitate_api.capacitate(conn, cab)["timp"]["pe_tip"]}
    assert pe_tip == {"nota": "Note contabile", "d300": "D300"}, pe_tip
