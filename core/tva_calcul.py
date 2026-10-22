# -*- coding: utf-8 -*-
"""core/tva_calcul.py — REGULA UNICĂ de calcul și rotunjire a TVA-ului unui document (lotul 11, decizia Costin 10.3: „Rotunjirea TVA: o
singură regulă pe toată aplicația, cea cerută de validatorul e-Factura.”).

REGULA, din regulile EN 16931 pe care le aplică validatorul RO e-Factura (CIUS-RO se sprijină pe EN 16931; textul — artefactele oficiale de
validare CEN, `ConnectingEurope/eInvoicing-EN16931`, `ubl/schematron/abstract/EN16931-model.sch`, citat verbatim):
  * BR-DEC-23: „The allowed maximum number of decimals for the Invoice line net amount (BT-131) is 2.”
    -> valoarea netă a liniei = cantitate × preț, rotunjită la 2 zecimale (`net_linie`).
  * BR-S-08: „For each different value of VAT category rate (BT-119) where the VAT category code (BT-118) is "Standard rated", the VAT
    category taxable amount (BT-116) in a VAT breakdown (BG-23) shall equal the sum of Invoice line net amounts (BT-131) [...] where [...]
    the VAT rate (BT-152 [...]) equals the VAT category rate (BT-119).”
    -> baza pe cotă = suma valorilor nete ale liniilor cu acea cotă (`pe_cote`).
  * BR-CO-17: „VAT category tax amount (BT-117) = VAT category taxable amount (BT-116) x (VAT category rate (BT-119) / 100), rounded to two
    decimals.” -> TVA-ul pe cotă = baza pe cotă × cotă / 100, rotunjit O SINGURĂ DATĂ, la 2 zecimale (`tva_din_baza`). NU suma TVA-urilor
    rotunjite pe linii și NU TVA-ul nerotunjit al tuturor liniilor, rotunjit la total.
  * BR-CO-14: „Invoice total VAT amount (BT-110) = Σ VAT category tax amount (BT-117).” -> TVA-ul documentului = suma TVA-urilor pe cote.
  * BR-CO-10 / BR-CO-13 / BR-CO-15: totalul fără TVA = Σ valorilor nete ale liniilor; totalul cu TVA = totalul fără TVA + TVA-ul total.
Modul de rotunjire: EN 16931 spune „rounded to two decimals”; schematronul UBL (`EN16931-UBL-model.sch`, BR-CO-17 / BR-S-09) testează cu
`round(... * 10 * 10) div 100` (jumătatea în sus) — aceeași cu regula fiscală iConta (CLAUDE.md „Rotunjire fiscală”: `Decimal` +
`ROUND_HALF_UP`, niciodată `round()`).

TVA-ul DIN TOTAL (suta mărită: încasarea la TVA la încasare, bonul, chitanța) e aceeași regulă aplicată unei sume care include taxa:
TVA = total × cotă / (100 + cotă), rotunjit la 2 zecimale (`tva_din_total`).

Funcții pure: fără bază, fără rețea. Garda `core/test_lot11_t_tva_unica.py` pică dacă un calcul paralel de TVA apare în afara lor.
"""
from decimal import Decimal, ROUND_HALF_UP

_BAN = Decimal("0.01")


def _d(x):
    return Decimal(str(x if x not in (None, "") else 0))


def q2(x):
    """Rotunjirea la ban a unei sume fiscale: 2 zecimale, ROUND_HALF_UP (BR-CO-17 „rounded to two decimals”; CLAUDE.md)."""
    return _d(x).quantize(_BAN, rounding=ROUND_HALF_UP)


def net_linie(cantitate, pret_unitar, valoare_neta=None):
    """BR-DEC-23: valoarea netă a liniei (BT-131) = cantitate × preț unitar, cu cel mult 2 zecimale.

    [lotul 11, C82] `valoare_neta` = valoarea netă scrisă PE FACTURĂ (BT-131 din XML-ul e-Factura, `factura_linii.valoare_neta`): când
    există, ea e valoarea liniei — prețul unitar ținut la 2 zecimale (`factura_linii.pret_unitar`) înmulțit cu o cantitate neîntreagă nu o
    mai reface la ban (3,333 × 30,00 = 99,99, pe factură 100,00)."""
    if valoare_neta not in (None, ""):
        return q2(valoare_neta)
    return q2(_d(cantitate) * _d(pret_unitar))


def tva_din_baza(baza, cota):
    """BR-CO-17: TVA = bază × (cotă / 100), rotunjit la 2 zecimale. `cota` în procente, ca BT-119 / BT-152 din factură (nu ca fracție)."""
    return q2(_d(baza) * _d(cota) / Decimal(100))


def tva_din_total(total, cota):
    """Suta mărită: TVA-ul cuprins într-o sumă care include taxa = total × cotă / (100 + cotă), rotunjit la 2 zecimale (aceeași rotunjire ca
    BR-CO-17). `cota` în procente."""
    c = _d(cota)
    return q2(_d(total) * c / (Decimal(100) + c))


def pe_cote(linii):
    """BR-S-08 + BR-CO-17: {cota (Decimal, procente): (baza, tva)} dintr-un șir de linii {cantitate, pret_unitar, cota_tva}. Baza pe cotă =
    Σ `net_linie`; TVA-ul pe cotă = `tva_din_baza(baza)`, rotunjit o singură dată pe cotă. O linie fără cotă (None) se refuză: absența nu se
    ghicește."""
    baze = {}
    for l in linii:
        ct = l.get("cota_tva") if isinstance(l, dict) else l[2]
        if ct is None:
            raise ValueError("O linie fără cotă de TVA: TVA-ul documentului nu se poate calcula — completează cota (0 e o valoare validă).")
        cant, pret = (l.get("cantitate"), l.get("pret_unitar")) if isinstance(l, dict) else (l[0], l[1])
        c = _d(ct)
        # [lotul 11, C82] valoarea netă a liniei de pe factură (BT-131), când linia o poartă
        baze[c] = baze.get(c, Decimal(0)) + net_linie(cant, pret, l.get("valoare_neta") if isinstance(l, dict) else None)
    return {c: (b, tva_din_baza(b, c)) for c, b in baze.items()}


def tva_lei_pe_cote(pe_cote_doc, curs, tva_lei_document=None):
    """TVA-ul pe cote al unui document în valută, în lei: {cota: tva_lei}. TVA-ul în lei al DOCUMENTULUI e TVA-ul total × curs, rotunjit o
    dată (CF art.319 alin.(20) lit.j: „suma taxei colectate, exprimate în lei”; aceeași definiție ca `facturi_api.sume_lei`); pe cote,
    fiecare = TVA-ul cotei × curs la ban, iar diferența de rotunjire dintre suma lor și TVA-ul documentului merge pe cota cu cel mai mare TVA
    — suma pe cote e mereu TVA-ul documentului. La RON (curs 1) e chiar TVA-ul pe cote.

    [lotul 11, C81] `tva_lei_document` = TVA-ul în lei SCRIS PE FACTURĂ (BT-111 din XML-ul e-Factura, `facturi.tva_lei_xml`): când există,
    el e TVA-ul documentului în lei (CF art.319 alin.(20) lit.j — „suma taxei colectate, exprimate în lei” e cea de pe factură, nu TVA-ul
    în valută × cursul beneficiarului). Pe cote se împarte PROPORȚIONAL cu TVA-ul cotei în valută (fiecare la ban), cu diferența de
    rotunjire pe cota cu cel mai mare TVA: suma pe cote e exact BT-111."""
    c = _d(curs)
    if tva_lei_document not in (None, "") and pe_cote_doc:
        tot_v = sum((t for _b, t in pe_cote_doc.values()), Decimal(0))
        if tot_v:
            out = {k: q2(_d(tva_lei_document) * t / tot_v) for k, (_b, t) in pe_cote_doc.items()}
            dif = q2(tva_lei_document) - sum(out.values(), Decimal(0))
            if dif:
                k = max(pe_cote_doc, key=lambda x: (abs(pe_cote_doc[x][1]), x))
                out[k] += dif
            return out
    out = {k: q2(t * c) for k, (_b, t) in pe_cote_doc.items()}
    if out:
        total = q2(sum((t for _b, t in pe_cote_doc.values()), Decimal(0)) * c)
        dif = total - sum(out.values(), Decimal(0))
        if dif:
            k = max(pe_cote_doc, key=lambda x: (abs(pe_cote_doc[x][1]), x))
            out[k] += dif
    return out


def totaluri(linii):
    """BR-CO-10 / 13 / 14 / 15: {"baza": Σ net_linie, "tva": Σ TVA pe cote, "total": baza + tva, "pe_cote": `pe_cote`} — totalurile
    documentului, aceleași pe factură, PDF, XML-ul e-Factura și nota contabilă."""
    pc = pe_cote(linii)
    baza = sum((b for b, _t in pc.values()), Decimal(0))
    tva = sum((t for _b, t in pc.values()), Decimal(0))
    return {"baza": baza, "tva": tva, "total": baza + tva, "pe_cote": pc}
