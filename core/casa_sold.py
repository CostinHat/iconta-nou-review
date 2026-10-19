# -*- coding: utf-8 -*-
"""core/casa_sold.py — [deficiența 406, retestul Costin 19.10.2026, PRIORITAR] „Casă: plată 200 cu sold 142 acceptată, registru −58;
validarea a trecut; refuz la salvare și blocare la validare.”

O singură regulă, cu două momente:
  - la SALVARE (dispoziția de plată, stornarea unei încasări): soldul casei din tot ce e înregistrat — solduri de preluare + notele
    validate ȘI ciornele (plata în ciornă a scos deja banii din casă);
  - la VALIDARE (`jurnal_api.valideaza`, unicul drum de validare — jurnalul și coada): soldul din evidența VALIDATĂ, plus nota care se
    validează. Prinde orice drum de scriere (notă manuală, import, stornare), nu numai dispoziția.
Refuzul apare dacă, după ieșire, casa ar ajunge sub zero în ziua operațiunii SAU în oricare zi de după (o plată pusă în trecut scade
toate soldurile de după ea).

Temei: OMFP 1802/2014, funcțiunea contului 531: „Contul 531 "Casa" este un cont de activ. [...] Soldul contului reprezintă numerarul
existent în casierie.” — numerarul existent nu poate fi sub zero. Conturile: 5311 (casa în lei) și 5314 (casa în valută), fiecare cu
analiticele lui. LIMITA, deliberată: conturile de bancă (5121/5124) NU sunt aici — extrasul băncii e documentul, iar un descoperit pe
extras (neconform sau nu) trebuie înregistrat cum e; casa n-are un document extern care s-o arate negativă.
"""
from decimal import Decimal

from core.pdf_util import bani as _lei, data_ro as _data_ro

CONTURI_CASA = ("5311", "5314")
COD = "CASA_NEGATIVA"
TEMEI = ("OMFP 1802/2014, funcțiunea contului 531: „Contul 531 \"Casa\" este un cont de activ. [...] Soldul contului reprezintă "
         "numerarul existent în casierie.”")


def sintetic_casa(cont):
    """'5311' pentru '5311' / '5311.01'; None pentru un cont care nu e de casă."""
    s = str(cont or "").split(".")[0]
    return s if s in CONTURI_CASA else None


def _miscari(cur, schema, cont, doar_validate):
    """(sold de preluare, {data: variație}) pe contul de casă `cont` (sintetic, cu analiticele lui)."""
    from psycopg2.extras import RealDictCursor
    from core.bilant_api import data_soldurilor
    with cur.connection.cursor(cursor_factory=RealDictCursor) as c:   # `data_soldurilor` citește rânduri-dicționar
        ref = data_soldurilor(c, schema)
    cur.execute(f"SELECT COALESCE(sum(sold_debitor - sold_creditor), 0) AS s FROM {schema}.solduri_initiale "
                f"WHERE split_part(cont, '.', 1) = %s", (cont,))
    r = cur.fetchone()
    initial = Decimal(str(r["s"] if isinstance(r, dict) else r[0]))
    cur.execute(f"""SELECT i.data, sum(CASE WHEN split_part(l.cont_debit, '.', 1) = %s THEN l.suma ELSE 0 END)
                                 - sum(CASE WHEN split_part(l.cont_credit, '.', 1) = %s THEN l.suma ELSE 0 END) AS v
                      FROM {schema}.inregistrari_linii l JOIN {schema}.inregistrari i ON i.id = l.inregistrare_id
                     WHERE (split_part(l.cont_debit, '.', 1) = %s OR split_part(l.cont_credit, '.', 1) = %s)
                       AND (i.status = 'validata' OR NOT %s) AND (%s::date IS NULL OR i.data > %s::date)
                     GROUP BY i.data""", (cont, cont, cont, cont, doar_validate, ref, ref))
    out = {}
    for x in cur.fetchall():
        d, v = (x["data"], x["v"]) if isinstance(x, dict) else (x[0], x[1])
        out[d] = Decimal(str(v))
    return ref, initial, out


def refuz_iesire(cur, schema, cont, data, iesire, doar_validate, ce="Plata"):
    """Mesajul refuzului dacă ieșirea `iesire` (lei, > 0) din casa `cont`, la `data`, duce soldul sub zero în acea zi sau în oricare zi de
    după; None dacă încape. `doar_validate`: soldul evidenței validate (la validare) sau al tuturor notelor (la salvare)."""
    import datetime as _dt
    cont = sintetic_casa(cont)
    iesire = Decimal(str(iesire))
    if cont is None or iesire <= 0:
        return None
    if not hasattr(data, "year"):
        data = _dt.date.fromisoformat(str(data)[:10])
    ref, sold, mis = _miscari(cur, schema, cont, doar_validate)
    if ref is not None and data <= ref:
        return None   # înainte de soldurile de preluare aplicația nu știe ce era în casă
    for d in sorted(mis):
        if d < data:
            sold += mis[d]
    sold_inainte = sold + mis.get(data, Decimal(0))
    zile = sorted(set([data] + [d for d in mis if d >= data]))
    curent = sold
    for d in zile:
        curent += mis.get(d, Decimal(0))
        if curent - iesire < 0:
            evidenta = "evidența validată" if doar_validate else "registru"
            cand = ("pe %s" % _data_ro(d)) if d == data else ("pe %s, după operațiunile înregistrate până atunci" % _data_ro(d))
            return ("%s de %s lei nu încape în casă (contul %s): soldul casei pe %s, în %s, e %s lei, iar după ea casa ar ajunge la %s lei %s. "
                    "Numerarul din casă nu poate fi negativ. Înregistrează întâi încasarea sau ridicarea de numerar din care s-a plătit%s."
                    % (ce, _lei(iesire), cont, _data_ro(data), evidenta, _lei(sold_inainte), _lei(curent - iesire), cand,
                       " (și valideaz-o)" if doar_validate else ""))
    return None


def sold_inainte(cur, schema, cont, zi, doar_validate=False):
    """Soldul casei `cont` la începutul zilei `zi` (preluare + notele de dinainte); 0 înainte de soldurile de preluare. Soldul de la care
    pornește registrul de casă al lunii — nu zero în fiecare lună."""
    ref, sold, mis = _miscari(cur, schema, sintetic_casa(cont), doar_validate)
    if ref is not None and zi <= ref:
        return Decimal(0)
    return sold + sum((v for d, v in mis.items() if d < zi), Decimal(0))
