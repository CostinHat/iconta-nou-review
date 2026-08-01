# -*- coding: utf-8 -*-
"""TVA la incasare (art. 282 CF, OUG 8/2026) - motor PUR.
Exigibilitatea intervine la incasarea totala/partiala; fiecare incasare include TVA
(art. 282 alin. 8, suta marita). Plafon: 5.000.000 lei (01.03.2026-31.12.2026),
5.500.000 din 2027. Exclus (regim general): taxare inversa, scutite, regimuri
speciale 311-313, beneficiar afiliat."""
from decimal import Decimal, ROUND_HALF_UP

def tva_din_incasare(suma_incasata, cota):
    """TVA exigibil dintr-o incasare (suta marita): suma x cota/(100+cota)."""
    s = Decimal(str(suma_incasata))
    c = Decimal(str(cota))
    if s <= 0:
        raise ValueError("suma incasata trebuie sa fie pozitiva")
    return (s * c / (100 + c)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def tva_exigibil_alocari(alocari):
    """alocari: [{suma, cota_tva}] (sumele incasate alocate pe facturi/cote).
    Intoarce lista [{cota, tva}] agregata pe cota + total."""
    pe_cota = {}
    for a in alocari:
        c = Decimal(str(a["cota_tva"]))
        pe_cota[c] = pe_cota.get(c, Decimal("0")) + tva_din_incasare(a["suma"], c)
    linii = [{"cota": str(c), "tva": str(v)} for c, v in sorted(pe_cota.items())]
    total = sum(pe_cota.values(), Decimal("0"))
    return {"linii": linii, "total": total.quantize(Decimal("0.01"))}

def plafon_la(data_iso):
    """Plafonul TVA la incasare valabil la o data, period-aware din common.COTE (fost petic 3-tier).
    OUG 8/2026: 5M de la 03.2026, 5.5M de la 2027; 4.5M anterior (PAS 2, valoare -> registru)."""
    from core import common as _c
    from datetime import date as _d
    return _c.cota("plafon_tva_incasare", _d.fromisoformat(str(data_iso)[:10]))[0]
