# -*- coding: utf-8 -*-
"""core/ops_valuta.py — decontarea în valută pe FACTURA din care provine creanța sau datoria (Operațiuni → Decontare în valută).

[lotul 13, deficiența 524, comanda Costin 13.1, verbatim] „La fel la Decontare în valută (F3): încasarea a 5.000 EUR (5124 = 4111 24.750,
5124 = 765 1.935) se generează fără creanță în valută — venit din diferențe de curs inventat, profit mai mare; decontarea se face pe factura
din care provine (cursul ei, soldul rămas în valută), iar cursul de evidență nu se mai scrie de mână.”

TEMEI — OMFP 1802/2014 pct.322 alin.(1) (`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`): diferențele de curs „care apar la
decontarea creanțelor și datoriilor în valută la cursuri diferite față de cele la care au fost înregistrate inițial în cursul perioadei
sau față de cele la care au fost raportate în situațiile financiare anterioare se recunosc ca venituri sau cheltuieli din diferențe de
curs valutar”; pct.325: la sfârșitul lunii creanța / datoria se reevaluează, deci cursul „la care e înregistrată” devine cel al ultimei
reevaluări. De aici: cursul de evidență = al ultimei reevaluări VALIDATE a partenerului (pe cont și monedă) dinaintea decontării sau, fără
ea, cursul facturii; soldul în valută = totalul facturii minus ce s-a decontat deja pe ea (notele legate de factură care sting contul de
terț — aceeași regulă ca reevaluarea lunară, `reevaluare_valuta._plati_din_note`), la cursul de evidență.
"""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")


def facturi_deschise(cur, schema, directie, la_data):
    """Facturile în valută ale firmei, pe `directie` („emisa” = creanțe, „primita” = datorii), contate prin notă VALIDATĂ și cu sold în
    valută la `la_data`: [{id, document, partener, cui, moneda, total, rest_valuta, curs_evidenta, curs_din, cont_tert}]."""
    from core import contare_facturi as _cf, eticheta_nota as _et, reevaluare_valuta as _rv
    fact = [f for f in _rv.facturi_in_valuta(cur, schema, la_data) if f["directie"] == directie and f["storno_din_id"] is None]
    note = _cf.note_pe_facturi(cur, schema, [f["id"] for f in fact])
    rev = [r for r in _rv.reevaluari(cur, schema, la_data) if r["status"] == "validata"]
    out = []
    for f in fact:
        if f["curs_bnr"] is None or (f["platita_la"] is not None and f["platita_la"].date() <= la_data):
            continue
        nf = note.get(f["id"], [])
        cont, data_contare, _lei = _rv._cont_tert(nf, directie)
        if not cont or data_contare > la_data:
            continue   # factura necontată (sau contată numai în ciornă) nu are încă creanța / datoria în evidență
        curs_f = Decimal(str(f["curs_bnr"]))
        platit = sum((lei for _d, lei in _rv._plati_din_note(nf, cont, directie, la_data)), Decimal("0"))
        total = Decimal(str(f["total"]))
        rest = (total - platit / curs_f).quantize(B, rounding=ROUND_HALF_UP)
        if rest <= 0:
            continue
        pk = _rv.cheie_partener(f["tert_cui"], f["tert_nume"])
        ult = [r for r in rev if r["cont"] == cont and r["moneda"] == f["moneda"] and (r["partener"] == pk or r["factura_id"] == f["id"])]
        curs_ev, din = (Decimal(str(ult[-1]["curs_nou"])), "reevaluarea din %s" % ult[-1]["data"]) if ult else (curs_f, "cursul facturii")
        out.append({"id": f["id"], "document": _et.factura_din_rand(f), "partener": f["tert_nume"], "cui": f["tert_cui"],
                    "moneda": f["moneda"], "total": total, "rest_valuta": rest, "curs_evidenta": curs_ev, "curs_din": din,
                    "cont_tert": cont, "data": f["data_emitere"]})
    return out


def factura_deschisa(cur, schema, factura_id, directie, la_data):
    """Factura `factura_id` din `facturi_deschise` sau None (nu e în valută, nu e pe direcția cerută, e închisă / necontată)."""
    return next((f for f in facturi_deschise(cur, schema, directie, la_data) if f["id"] == int(factura_id)), None)
