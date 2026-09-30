# -*- coding: utf-8 -*-
"""Diferente de curs valutar (665/765) - motor PUR.
Sursa: OMFP 1802/2014 pct. 316-322: diferentele de curs la decontarea
creantelor/datoriilor in valuta si la reevaluarea LUNARA a soldurilor
(creante, datorii, disponibilitati) la cursul BNR din ultima zi bancara a
lunii se recunosc in 665 (cheltuieli) / 765 (venituri).
Reguli de semn:
- CREANTA (4111, 461...) sau DISPONIBIL (5124): curs creste -> castig 765;
- DATORIE (401, 462...): curs creste -> pierdere 665."""
from decimal import Decimal, ROUND_HALF_UP
from core.common import nomenclator_cerut

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0))

def diferenta(valoare_valuta, curs_initial, curs_final, tip, in_lei_cu_clauza=False):
    """tip: creanta|disponibil|datorie. Returneaza {diferenta (abs), cont, sens} sau diferenta=0.
    [1b] in_lei_cu_clauza: creanta/datorie IN LEI decontata in functie de cursul unei valute ->
    diferentele merg la 768/668 (alte venituri/cheltuieli financiare), nu 765/665 (OMFP 1802/2014
    pct. 94 lit. b)."""
    v, c1, c2 = _d(valoare_valuta), _d(curs_initial), _d(curs_final)
    if v <= 0 or c1 <= 0 or c2 <= 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    if tip not in ("creanta", "disponibil", "datorie"):
        raise ValueError(nomenclator_cerut("tip", "creanta|disponibil|datorie"))
    dif = (v * (c2 - c1)).quantize(B, rounding=ROUND_HALF_UP)
    if dif == 0:
        return {"diferenta": Decimal("0.00"), "cont": None, "sens": None}
    castig = dif > 0 if tip in ("creanta", "disponibil") else dif < 0
    cont_venit, cont_chelt = ("768", "668") if in_lei_cu_clauza else ("765", "665")
    return {"diferenta": abs(dif), "cont": cont_venit if castig else cont_chelt,
            "sens": "favorabila" if castig else "nefavorabila"}

def nota_decontare(valoare_valuta, curs_factura, curs_decontare, tip,
                   cont_tert, cont_banca="5124", in_lei_cu_clauza=False):
    """Nota la incasare creanta / plata datorie. Diferenta pe 665/765 (valuta) sau 668/768
    (in lei cu clauza valutara, OMFP 1802/2014 pct. 94 lit. b)."""
    v = _d(valoare_valuta)
    lei_factura = (v * _d(curs_factura)).quantize(B, rounding=ROUND_HALF_UP)
    lei_decont = (v * _d(curs_decontare)).quantize(B, rounding=ROUND_HALF_UP)
    d = diferenta(v, curs_factura, curs_decontare, tip, in_lei_cu_clauza=in_lei_cu_clauza)
    linii = []
    if tip == "creanta":
        linii.append((cont_banca, cont_tert, lei_factura))
        if d["sens"] == "favorabila":
            linii.append((cont_banca, d["cont"], d["diferenta"]))
        elif d["sens"] == "nefavorabila":
            linii.append((d["cont"], cont_banca, d["diferenta"]))
    else:  # datorie
        linii.append((cont_tert, cont_banca, lei_factura))
        if d["sens"] == "nefavorabila":
            linii.append((d["cont"], cont_banca, d["diferenta"]))
        elif d["sens"] == "favorabila":
            linii.append((cont_banca, d["cont"], d["diferenta"]))
    return {"lei_evidenta": lei_factura, "lei_decontare": lei_decont,
            "diferenta": d, "linii": linii}

def reevaluare_sold(sold_valuta, curs_evidenta, curs_bnr_sfarsit_luna, tip,
                    cont_sold, in_lei_cu_clauza=False):
    """Reevaluare lunara sold valuta (OMFP 1802 pct. 316). Returneaza linia
    notei sau None daca diferenta e 0."""
    d = diferenta(sold_valuta, curs_evidenta, curs_bnr_sfarsit_luna, tip, in_lei_cu_clauza=in_lei_cu_clauza)
    if not d["cont"]:
        return None
    if d["sens"] == "favorabila":
        linie = (cont_sold, d["cont"], d["diferenta"])
    else:
        linie = (d["cont"], cont_sold, d["diferenta"])
    return {"diferenta": d, "linie": linie}
