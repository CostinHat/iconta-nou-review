# -*- coding: utf-8 -*-
"""SGR sistem garantie-returnare - motor PUR (HG 1074/2021, garantie 0,50
lei/ambalaj, administrator RetuRO). Tratament MFP/CECCAR:
- garantia NU intra in sfera TVA; tariful de gestionare primit de la RetuRO
  este purtator de TVA (autofactura emisa de RetuRO in numele comerciantului);
- COMERCIANT: achizitie marfa 371+4426=401 + garantia platita furnizorului
  461.SGR=401 (fara TVA); vanzare: garantia incasata de la client distinct pe
  bon 5311/5121=462.SGR; restituire garantie consumatorului care returneaza
  ambalajul: 461.SGR=5311 (devine creanta asupra RetuRO); autofactura lunara
  RetuRO: incasare garantii returnate 5121=461.SGR + tarif gestionare
  4111=708+4427; virarea garantiilor incasate si neretinute catre amonte:
  462.SGR=401/5121."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
GARANTIE_UNITARA = Decimal("0.50")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _suma(nr_ambalaje=None, suma=None):
    if suma is not None:
        s = _d(suma)
    elif nr_ambalaje:
        s = (GARANTIE_UNITARA * int(nr_ambalaje)).quantize(B)
    else:
        raise ValueError("nr_ambalaje sau suma obligatoriu")
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    return s

def nota_garantie_achizitie(nr_ambalaje=None, suma=None):
    """Garantia platita furnizorului la achizitia marfii: 461.SGR=401, fara TVA."""
    return {"linii": [("461", "401", _suma(nr_ambalaje, suma))]}

def nota_garantie_vanzare(nr_ambalaje=None, suma=None, sursa="casa"):
    """Garantia incasata de la client (distinct pe bon): 5311/5121=462.SGR."""
    cont = "5311" if sursa == "casa" else "5121"
    return {"linii": [(cont, "462", _suma(nr_ambalaje, suma))]}

def nota_restituire_consumator(nr_ambalaje=None, suma=None, sursa="casa"):
    """Restituire garantie la returnarea ambalajului: 461.SGR = 5311/5121
    (creanta asupra RetuRO pentru ambalajele colectate)."""
    cont = "5311" if sursa == "casa" else "5121"
    return {"linii": [("461", cont, _suma(nr_ambalaje, suma))]}

def nota_autofactura_returo(garantii_returnate, tarif_gestionare=0, cota_tva=None):
    """Autofactura lunara RetuRO: incasare garantii 5121=461.SGR (fara TVA) +
    tarif gestionare 4111=708+4427 (cu TVA)."""
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    g = _d(garantii_returnate)
    t = _d(tarif_gestionare)
    if g < 0 or t < 0 or (g + t) <= 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    linii = []
    if g > 0:
        linii.append(("5121", "461", g))
    if t > 0:
        tva = (t * Decimal(str(cota_tva)) / 100).quantize(B, rounding=ROUND_HALF_UP)
        linii.append(("4111", "708", t))
        if tva > 0:
            linii.append(("4111", "4427", tva))
    return {"linii": linii}

def nota_virare_garantii(suma, catre="furnizor"):
    """Virarea garantiilor incasate: 462.SGR = 401 (furnizor) / 5121 (plata directa)."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("Suma trebuie să fie un număr pozitiv.")
    cont = "401" if catre == "furnizor" else "5121"
    return {"linii": [("462", cont, s)]}
