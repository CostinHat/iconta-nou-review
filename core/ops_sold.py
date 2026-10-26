# -*- coding: utf-8 -*-
"""core/ops_sold.py — soldul contului pe care îl stinge o operațiune specială, verificat ÎNAINTE de a scrie nota.

[lotul 13, deficiența 524, comanda Costin 13.1, verbatim] „Plata ratei nu verifică soldul: cu creditul și dobânda doar ciorne (1621 și 1682
zero) a generat 1621 = 5121 5.000 și 1682 = 5121 500 — la validare conturile ajung cu sold invers. […] La fel la Decontări asociați:
restituirea împrumutului (4551 = 5121 20.000) se generează fără datorie către asociați. La fel la Avansuri: regularizarea 409 (401 = 4091
5.000, 401 = 4426 1.050) se generează cu 4091 zero. La fel la Decontare în valută […] Regula, pentru toate operațiile speciale: orice
plată, restituire sau regularizare verifică soldul contului pe care îl stinge, ca la dividende.”

CE E SOLDUL (aceeași regulă ca dividendele, `uc_tenants._sursa_profitului` / `bilant_api.sold_la`): soldurile preluate
(`solduri_initiale`) plus notele VALIDATE până la data operațiunii — evidența e ce a validat un om (decizia Costin 08.10.2026 §6 pct.7).
O ciornă care ar crea soldul (primirea creditului, dobânda, avansul) nu-l creează încă: refuzul o numește, ca omul s-o valideze întâi.
Din sold se scade ce consumă deja ALTE ciorne care îl sting (două restituiri nevalidate ale aceluiași împrumut nu trec amândouă).

TEMEI: OMFP 1802/2014 — funcțiunea fiecărui cont stins (1621/1682: „În debitul contului … se înregistrează: – sumele rambursate”;
4551: sumele restituite asociaților; 4091: avansurile regularizate la primirea facturii; 542: avansurile decontate). Un cont de datorie
(creditor) nu se debitează peste soldul lui, unul de creanță (debitor) nu se creditează peste el — altfel soldul devine invers, adică o
datorie care s-ar fi plătit de două ori sau o creanță care n-a existat (OMFP 1802/2014 pct.62: „Soldul … reprezintă …”).
Refuzul e de FORMĂ (sold invers), nu o regulă fiscală.
"""
from decimal import Decimal

from core import erori as _erori
from core.pdf_util import bani, data_ro

#: sensul soldului pe care îl stinge operațiunea: „creditor” = o datorie (credit, dobândă, împrumut de la asociat, TVA neexigibilă colectată);
#: „debitor” = o creanță (avans dat, avans de trezorerie, creanță în valută)
SENSURI = ("creditor", "debitor")


def _p(schema):
    return ('"%s".' % schema) if schema else ""


def _unu(r):
    return (list(r.values())[0] if isinstance(r, dict) else r[0]) if r else None


def _potriveste(cont):
    """(cont exact, tiparul analiticelor lui) — 4091 îi cuprinde pe 4091.x, nu pe 409."""
    return str(cont), str(cont) + ".%"


def sold_net(cur, schema, cont, data, partener_cui=None):
    """Debit − credit pe `cont` (și analiticele lui) la `data`, inclusiv: soldurile preluate + notele validate. Cu `partener_cui`, numai
    rândurile notelor care poartă acel partener (soldul preluat nu are partener: atunci nu se adună). Decimal."""
    c, an = _potriveste(cont)
    p = _p(schema)
    initial = Decimal("0")
    if not partener_cui:
        cur.execute("SELECT COALESCE(SUM(sold_debitor), 0) - COALESCE(SUM(sold_creditor), 0) FROM %ssolduri_initiale "
                    "WHERE cont = %%s OR cont LIKE %%s" % p, (c, an))
        initial = Decimal(str(_unu(cur.fetchone()) or 0))
    filtru = " AND l.partener_cui = %s" if partener_cui else ""
    args = (c, an, c, an, data) + ((partener_cui,) if partener_cui else ())
    cur.execute("SELECT COALESCE(SUM(CASE WHEN l.cont_debit = %%s OR l.cont_debit LIKE %%s THEN l.suma ELSE 0 END), 0) "
                "- COALESCE(SUM(CASE WHEN l.cont_credit = %%s OR l.cont_credit LIKE %%s THEN l.suma ELSE 0 END), 0) "
                "FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id "
                "WHERE i.status = 'validata' AND i.data <= %%s%s" % (p, p, filtru), args)
    return initial + Decimal(str(_unu(cur.fetchone()) or 0))


def ciorne_care_misca(cur, schema, cont, sens_stingere):
    """Notele NEVALIDATE care mișcă `cont`: {"creeaza": [(id, suma)], "sting": [(id, suma)]}. `sens_stingere` = partea pe care o scrie
    operațiunea care stinge („debit” pentru un cont creditor, „credit” pentru unul debitor). O ciornă care creează soldul îl va crea
    abia la validare; una care îl stinge îl consumă deja."""
    c, an = _potriveste(cont)
    p = _p(schema)
    cur.execute("SELECT i.id, "
                "COALESCE(SUM(CASE WHEN l.cont_debit = %%s OR l.cont_debit LIKE %%s THEN l.suma ELSE 0 END), 0) AS deb, "
                "COALESCE(SUM(CASE WHEN l.cont_credit = %%s OR l.cont_credit LIKE %%s THEN l.suma ELSE 0 END), 0) AS cre "
                "FROM %sinregistrari i JOIN %sinregistrari_linii l ON l.inregistrare_id = i.id "
                "WHERE i.status <> 'validata' AND (l.cont_debit = %%s OR l.cont_debit LIKE %%s OR l.cont_credit = %%s OR "
                "l.cont_credit LIKE %%s) GROUP BY i.id ORDER BY i.id" % (p, p), (c, an, c, an, c, an, c, an))
    out = {"creeaza": [], "sting": []}
    for r in cur.fetchall():
        nid, deb, cre = (r["id"], r["deb"], r["cre"]) if isinstance(r, dict) else r
        net = Decimal(str(deb)) - Decimal(str(cre))   # + = debitează, - = creditează
        if net == 0:
            continue
        stinge = (net > 0) if sens_stingere == "debit" else (net < 0)
        out["sting" if stinge else "creeaza"].append((nid, abs(net)))
    return out


def disponibil(cur, schema, cont, data, sens, partener_cui=None):
    """Soldul care se mai poate stinge: (disponibil, sold_validat, ciorne) — `sens` = „creditor” (datorie) / „debitor” (creanță)."""
    if sens not in SENSURI:
        raise ValueError("Sensul soldului %r nu e „debitor” sau „creditor” — o greșeală a programului, nu a datelor." % sens)
    net = sold_net(cur, schema, cont, data, partener_cui)
    sold = -net if sens == "creditor" else net
    ciorne = ciorne_care_misca(cur, schema, cont, "debit" if sens == "creditor" else "credit")
    consumat = sum((s for _i, s in ciorne["sting"]), Decimal("0"))
    return sold - consumat, sold, ciorne


def cere_sold(cur, schema, cont, data, suma, sens, ce, camp=None, partener_cui=None, partener=None):
    """Refuză (DateInvalide, lângă `camp`) dacă `suma` depășește soldul `sens` al contului `cont` la `data`. `ce` = operațiunea, cum o
    citește contabilul („Plata ratei”, „Restituirea împrumutului”). Mesajul spune soldul, ce ciorne îl vor crea (de validat întâi) și ce
    ciorne îl consumă deja."""
    from core import eticheta_nota as _et
    suma = Decimal(str(suma or 0))
    if suma <= 0:
        return
    disp, sold, ciorne = disponibil(cur, schema, cont, data, sens, partener_cui)
    if suma <= disp + Decimal("0.005"):
        return
    cui = " (partenerul %s)" % partener if partener else ""
    m = ("%s de %s stinge contul %s%s, dar la %s contul are sold %s %s (din soldurile preluate și notele validate)"
         % (ce, bani(suma, "lei"), cont, cui, data_ro(data), sens, bani(max(sold, Decimal("0")), "lei")))
    stinse = sum((s for _i, s in ciorne["sting"]), Decimal("0"))
    if stinse > 0:
        m += ", din care %s sunt deja stinși de %s" % (bani(stinse, "lei"), _et.lista(cur, schema, [i for i, _s in ciorne["sting"]]))
    m += ". Nota ar lăsa contul cu sold invers."
    if ciorne["creeaza"]:
        m += (" %s pe contul %s e încă în ciorna %s: valideaz-o întâi din Registrul jurnal, apoi generează din nou."
              % ("Datoria" if sens == "creditor" else "Creanța", cont, _et.lista(cur, schema, [i for i, _s in ciorne["creeaza"]])))
    raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp, "mesaj": m}]} if camp else m)


def cere_sold_4428(cur, schema, data, suma, sens, camp=None):
    """[lotul 13, deficiențele 541 / 524] „Nota manuală «TVA la încasare» generează 4428 = 4427 fără verificarea soldului.” Contul 4428 e
    bifuncțional la TVA la încasare: pe credit stă TVA-ul colectat neexigibil al facturilor emise (4111 = 4428), pe debit cel deductibil
    neexigibil al facturilor primite (4428 = 401). Soldul net le-ar amesteca, deci se citește partea pe care o stinge nota:
      sens „incasare” (4428 = 4427): TVA colectat neexigibil = soldul creditor preluat + creditele 4428 (în afară de 4426 = 4428) −
        exigibilizările 4428 = 4427 deja validate, minus ce exigibilizează ciornele;
      sens „plata” (4426 = 4428): TVA deductibil neexigibil = soldul debitor preluat + debitele 4428 (în afară de 4428 = 4427) −
        exigibilizările 4426 = 4428 deja validate, minus ce exigibilizează ciornele.
    TEMEI: CF art.282 alin.(3)-(4) (exigibilitatea la încasare / dreptul de deducere la plată, art.297 alin.(2)) — nota exigibilizează
    numai TVA-ul care e neexigibil; refuz de FORMĂ (sold invers pe 4428)."""
    from core import eticheta_nota as _et
    suma = Decimal(str(suma or 0))
    if suma <= 0:
        return
    p = _p(schema)
    initial_col = "sold_creditor" if sens == "incasare" else "sold_debitor"
    cur.execute("SELECT COALESCE(SUM(%s), 0) FROM %ssolduri_initiale WHERE cont = '4428' OR cont LIKE '4428.%%'" % (initial_col, p))
    initial = Decimal(str(_unu(cur.fetchone()) or 0))
    if sens == "incasare":   # intră pe credit (fără 4426 = 4428), iese pe debit spre 4427
        intra, iese = ("l.cont_credit LIKE '4428%%' AND l.cont_debit NOT LIKE '4426%%'", "l.cont_debit LIKE '4428%%' AND l.cont_credit LIKE '4427%%'")
    else:                    # intră pe debit (fără 4428 = 4427), iese pe credit spre 4426
        intra, iese = ("l.cont_debit LIKE '4428%%' AND l.cont_credit NOT LIKE '4427%%'", "l.cont_credit LIKE '4428%%' AND l.cont_debit LIKE '4426%%'")
    cur.execute("SELECT COALESCE(SUM(CASE WHEN i.status = 'validata' AND %s THEN l.suma ELSE 0 END), 0) AS intrat, "
                "COALESCE(SUM(CASE WHEN i.status = 'validata' AND %s THEN l.suma ELSE 0 END), 0) AS iesit, "
                "COALESCE(SUM(CASE WHEN i.status <> 'validata' AND %s THEN l.suma ELSE 0 END), 0) AS in_ciorne "
                "FROM %sinregistrari_linii l JOIN %sinregistrari i ON i.id = l.inregistrare_id WHERE i.data <= %%s"
                % (intra, iese, iese, p, p), (data,))
    r = cur.fetchone()
    intrat, iesit, in_ciorne = (Decimal(str(x)) for x in (list(r.values()) if isinstance(r, dict) else r))
    neexigibil = initial + intrat - iesit
    if suma <= neexigibil - in_ciorne + Decimal("0.005"):
        return
    fel = "colectat" if sens == "incasare" else "deductibil"
    m = ("Exigibilizarea de %s ar muta pe %s mai mult TVA %s neexigibil decât are contul 4428 la %s: %s (din soldurile preluate și notele "
         "validate)" % (bani(suma, "lei"), "4427" if sens == "incasare" else "4426", fel, data_ro(data), bani(max(neexigibil, Decimal("0")), "lei")))
    if in_ciorne > 0:
        m += ", din care %s sunt deja exigibilizați de note nevalidate" % bani(in_ciorne, "lei")
    m += (". Nota ar lăsa contul 4428 cu sold invers. Încasarea sau plata legată de factură (Bancă, Casă) mută singură TVA-ul; nota manuală e "
          "numai pentru cazurile speciale (art. 291 alin. (5)).")
    raise _erori.DateInvalide({"mesaj": m, "erori_campuri": [{"camp": camp, "mesaj": m}]} if camp else m)
