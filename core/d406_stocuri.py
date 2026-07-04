# -*- coding: utf-8 -*-
"""D406 Stocuri (SAF-T la cerere ANAF, sectiunea PhysicalStock) - generator PUR.
Structura verificata pe saft.xsd oficial: PhysicalStockEntry{WarehouseID,
ProductCode, StockAccountNo?, ProductType, StockAccountCommodityCode, OwnerID,
UOMPhysicalStock, UOMToUOMBaseConversionFactor, UnitPrice,
OpeningStockQuantity, OpeningStockValue, ClosingStockQuantity,
ClosingStockValue, StockCharacteristics{...}}.
Sold = cumul miscari (intrare +, iesire -) pana la data; pret unitar mediu."""
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import escape

B2 = Decimal("0.01")
B3 = Decimal("0.001")

def _d(x, q=B2):
    return Decimal(str(x or 0)).quantize(q, rounding=ROUND_HALF_UP)

def solduri(miscari, data_start, data_end):
    """miscari: [{data, tip intrare|iesire, cantitate, valoare}] pt. UN articol.
    Returneaza cantitati/valori la deschidere (< data_start) si inchidere (<= data_end)."""
    oq = ov = cq = cv = Decimal("0")
    for m in miscari:
        semn = 1 if m["tip"] == "intrare" else -1
        q = Decimal(str(m["cantitate"])) * semn
        v = Decimal(str(m["valoare"])) * semn
        if m["data"] < data_start:
            oq += q; ov += v
        if m["data"] <= data_end:
            cq += q; cv += v
    if cq < 0 or cv < 0:
        raise ValueError("stoc negativ la inchidere - verifica miscarile")
    pret = (cv / cq).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP) if cq > 0 else Decimal("0")
    return {"open_q": oq.quantize(B3), "open_v": ov.quantize(B2),
            "close_q": cq.quantize(B3), "close_v": cv.quantize(B2), "pret": pret}

def xml_entry(articol, s, owner_id, warehouse="1"):
    e = escape
    return f"""<nsSAFT:PhysicalStockEntry>
<nsSAFT:WarehouseID>{e(str(warehouse))}</nsSAFT:WarehouseID>
<nsSAFT:ProductCode>{e(str(articol['id']))}</nsSAFT:ProductCode>
<nsSAFT:StockAccountNo>{e(articol.get('cont_stoc') or '371')}</nsSAFT:StockAccountNo>
<nsSAFT:ProductType>{e(articol.get('tip_produs') or 'MARFA')}</nsSAFT:ProductType>
<nsSAFT:StockAccountCommodityCode>{e(articol.get('cont_stoc') or '371')}</nsSAFT:StockAccountCommodityCode>
<nsSAFT:OwnerID>{e(str(owner_id))}</nsSAFT:OwnerID>
<nsSAFT:UOMPhysicalStock>{e(articol.get('um') or 'buc')}</nsSAFT:UOMPhysicalStock>
<nsSAFT:UOMToUOMBaseConversionFactor>1</nsSAFT:UOMToUOMBaseConversionFactor>
<nsSAFT:UnitPrice>{s['pret']}</nsSAFT:UnitPrice>
<nsSAFT:OpeningStockQuantity>{s['open_q']}</nsSAFT:OpeningStockQuantity>
<nsSAFT:OpeningStockValue>{s['open_v']}</nsSAFT:OpeningStockValue>
<nsSAFT:ClosingStockQuantity>{s['close_q']}</nsSAFT:ClosingStockQuantity>
<nsSAFT:ClosingStockValue>{s['close_v']}</nsSAFT:ClosingStockValue>
<nsSAFT:StockCharacteristics><nsSAFT:StockCharacteristic>{e(articol['denumire'])}</nsSAFT:StockCharacteristic>
<nsSAFT:StockCharacteristicValue>{e(articol.get('um') or 'buc')}</nsSAFT:StockCharacteristicValue>
</nsSAFT:StockCharacteristics>
</nsSAFT:PhysicalStockEntry>"""

def xml_physical_stock(articole_cu_miscari, data_start, data_end, owner_id):
    """articole_cu_miscari: [(articol_dict, [miscari])]. Sare articolele fara miscari."""
    parti = []
    for art, mis in articole_cu_miscari:
        if not mis:
            continue
        s = solduri(mis, data_start, data_end)
        parti.append(xml_entry(art, s, owner_id))
    if not parti:
        raise ValueError("niciun articol cu miscari in perioada")
    return "<nsSAFT:PhysicalStock>\n" + "\n".join(parti) + "\n</nsSAFT:PhysicalStock>"
