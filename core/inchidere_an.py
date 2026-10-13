# -*- coding: utf-8 -*-
"""core/inchidere_an.py — propunerea notei de închidere a exercițiului (varianta (a), decizia Costin 13.10.2026, verbatim în DECIZII):

  „Aplicația propune, la cererea contabilului, nota de închidere la 31.12: clasele 6/7 → 121 și regularizarea TVA 4426/4427 →
  4423/4424. Nota apare ca propunere și intră în evidență numai după ce contabilul o validează (R36).”

Din soldurile la 31.12 ale notelor VALIDATE (`bilant_api.sold_la`) se scriu două note CIORNĂ, datate 31.12, `sursa='inchidere_an'`, cu
documentul intern „Notă de calcul” (Legea 82/1991 art.6 alin.(1)):
  1. regularizarea TVA (`motor.regularizare_tva`): 4427 = 4426, diferența 4427 = 4423 sau 4424 = 4426;
  2. închiderea claselor 6 / 7 (`motor.inchidere_din_solduri`): 7xx = 121, 121 = 6xx.
TEMEI: OMFP 1802/2014, funcțiunea contului 121 și a conturilor 4423 / 4424 / 4426 / 4427 (`motor.TEMEI_INCHIDERE`,
`motor.TEMEI_REGULARIZARE_TVA`).

O propunere nevalidată (ciornă, respinsă) a aceluiași 31.12 se înlocuiește la o nouă cerere — documentul ei intern se păstrează, fără
număr nou; o propunere VALIDATĂ nu se atinge: o cerere ulterioară închide numai ce a rămas cu sold (o notă de după validare). O ciornă
aflată la validare în coadă nu se înlocuiește sub ochii cabinetului: refuz."""
import datetime
from decimal import Decimal

from core import bilant_api as _ba
from core import motor as _m
from core import note_derivate as _nd
from core import repo_contabilitate as _rc

SURSA = "inchidere_an"
DESCRIERE_TVA = "Regularizarea TVA la 31.12.%d"
DESCRIERE_INCHIDERE = "Închiderea conturilor de venituri și cheltuieli în 121 la 31.12.%d"


def propunere(solduri):
    """{"tva": [note], "inchidere": [note], "rezultat": Decimal} — calcul PUR, din soldurile la 31.12."""
    inchidere = _m.inchidere_din_solduri(solduri)
    rez = sum(((n["suma"] if n["credit"] == "121" else -n["suma"]) for n in inchidere), Decimal("0"))
    return {"tva": _m.regularizare_tva(solduri), "inchidere": inchidere, "rezultat": rez}


def _ciorne_existente(cur, schema, zi):
    cur.execute(f"SELECT id, descriere FROM {schema}.inregistrari WHERE sursa = %s AND data = %s AND status = 'ciorna' ORDER BY id",
                (SURSA, zi))
    return [(r["id"], r["descriere"]) if isinstance(r, dict) else (r[0], r[1]) for r in cur.fetchall()]


def propune(cur, schema, an):
    """Scrie propunerea pe 31.12.`an` (cursor RealDictCursor, în tranzacția apelantului). Întoarce {"note": [{id, descriere, linii,
    document}], "rezultat", "inlocuite", "nimic"}; ValueError cu motivul când nu se poate (an dinaintea soldurilor de preluare, o ciornă
    la validare)."""
    from core import coada_api as _coada
    zi = datetime.date(an, 12, 31)
    s = _ba.sold_la(cur, schema, zi)
    if s is None:
        raise ValueError("Nota de închidere pe %d nu se poate propune: soldurile de la 31.12.%d nu sunt în aplicație (evidența firmei "
                         "începe după soldurile de preluare)." % (an, an))
    vechi = _ciorne_existente(cur, schema, zi)
    for nid, _d in vechi:
        if _coada.nota_la_validare(cur, schema, nid):
            raise ValueError("Propunerea de închidere #%d e la validare în coadă — nu se înlocuiește cât o verifică cabinetul." % nid)
    doc_vechi = {d: _rc.documentul_notei(cur, schema, nid) for nid, d in vechi}
    for nid, _d in vechi:
        if _nd.respinsa(cur, schema, nid):
            _nd.sterge_respinsa(cur, schema, nid)
        else:
            _nd.sterge_ciorna_inlocuita(cur, schema, nid)
    p = propunere(s)
    note = []
    for descriere, linii in ((DESCRIERE_TVA % an, p["tva"]), (DESCRIERE_INCHIDERE % an, p["inchidere"])):
        if not linii:
            continue
        doc = doc_vechi.get(descriere)
        cur.execute(f"""INSERT INTO {schema}.inregistrari (data, descriere, sursa, status, document_ref)
                        VALUES (%s, %s, %s, 'ciorna', %s) RETURNING id""", (zi, descriere, SURSA, doc))
        r = cur.fetchone()
        nid = r["id"] if isinstance(r, dict) else r[0]
        if not doc:
            _rc._cu_document_intern(cur, schema, "nota_calcul", zi, r)
        for n in linii:
            _rc.adauga_linie(cur, schema, nid, n["debit"], n["credit"], n["suma"])
        note.append({"id": nid, "descriere": descriere, "linii": [(n["debit"], n["credit"], str(n["suma"])) for n in linii],
                     "document": _rc.documentul_notei(cur, schema, nid)})
    return {"note": note, "rezultat": p["rezultat"], "inlocuite": [nid for nid, _d in vechi], "nimic": not note}
