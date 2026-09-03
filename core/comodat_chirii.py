# -*- coding: utf-8 -*-
"""Comodat, chirii, refacturari utilitati - motor PUR.
Surse: OMFP 1802/2014 + Cod fiscal art. 271 (refacturare = structura de
comisionar, prestare in nume propriu) + practica ANAF.
- COMODAT (folosinta gratuita, contract civil art. 2146 CC): bunul NU intra
  in patrimoniul comodatarului; evidenta extracontabila D8031/8038 la primire,
  C la restituire; cheltuielile de functionare (utilitati, reparatii curente)
  suportate de comodatar sunt deductibile daca contractul le prevede;
- CHIRIE platita: 612 = 401 + 4426 (PJ cu factura); de la PERSOANA FIZICA:
  612 = 462, fara TVA, fara retinere la sursa (PF isi declara singura prin DU);
- CHIRIE incasata (activitate): 4111 = 706 + 4427;
- REFACTURARE utilitati (chirias): structura de comisionar art. 271:
  la primire factura furnizor (partea chiriasului): 461 = 401 cu TVA-ul
  refacturat identic; la refacturare: se emite factura cu aceeasi cota;
  practica simpla: primire % (605 + 4426) = 401 pentru partea proprie,
  461 = 401 partea de refacturat; emitere 4111 = 708 + 4427."""
from decimal import Decimal, ROUND_HALF_UP
from core.common import nomenclator_cerut

B = Decimal("0.01")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def _tva(baza, cota):
    return (_d(baza) * Decimal(str(cota)) / 100).quantize(B, rounding=ROUND_HALF_UP)

def nota_comodat(valoare, moment="primire"):
    """Extracontabil 8038 (bunuri primite in folosinta): D la primire, C la restituire."""
    v = _d(valoare)
    if v <= 0:
        raise ValueError("Valoarea introdusă e invalidă (trebuie un număr pozitiv).")
    if moment == "primire":
        return {"linii": [("8038", "891", v)]}
    if moment == "restituire":
        return {"linii": [("891", "8038", v)]}
    raise ValueError(nomenclator_cerut("moment", "primire|restituire"))

def nota_chirie_platita(chirie, cota_tva=None, proprietar="pj"):
    """PJ: 612=401+4426; PF: 612=462 fara TVA (PF declara prin Declaratia Unica)."""
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    c = _d(chirie)
    if c <= 0:
        raise ValueError("chirie invalida")
    if proprietar == "pf":
        return {"linii": [("612", "462", c)],
                "nota": "chirie PF: fara TVA, fara retinere - proprietarul "
                        "declara prin Declaratia Unica"}
    tva = _tva(c, cota_tva)
    linii = [("612", "401", c)]
    if tva > 0:
        linii.append(("4426", "401", tva))
    return {"linii": linii}

def nota_chirie_incasata(chirie, cota_tva=None):
    """4111 = 706 + 4427."""
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    c = _d(chirie)
    if c <= 0:
        raise ValueError("chirie invalida")
    tva = _tva(c, cota_tva)
    linii = [("4111", "706", c)]
    if tva > 0:
        linii.append(("4111", "4427", tva))
    return {"linii": linii}

def nota_refacturare(total_factura_furnizor, parte_refacturata, cota_tva=None):
    """Factura furnizor: partea proprie 605+4426=401, partea chiriasului 461=401
    (cu TVA inclus in creanta); refacturare: 4111 = 708 + 4427 cu ACEEASI cota
    (art. 271 - structura de comisionar)."""
    if cota_tva is None:
        raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
    tf, pr = _d(total_factura_furnizor), _d(parte_refacturata)
    if tf <= 0 or pr < 0 or pr > tf:
        raise ValueError("valori invalide (partea refacturata <= total)")
    proprie = tf - pr
    tva_proprie = _tva(proprie, cota_tva)
    tva_refact = _tva(pr, cota_tva)
    primire = []
    if proprie > 0:
        primire.append(("605", "401", proprie))
        if tva_proprie > 0:
            primire.append(("4426", "401", tva_proprie))
    if pr > 0:
        primire.append(("461", "401", pr + tva_refact))
    emitere = []
    if pr > 0:
        emitere = [("4111", "708", pr)]
        if tva_refact > 0:
            emitere.append(("4111", "4427", tva_refact))
    return {"primire": primire, "emitere": emitere, "tva_refacturat": tva_refact}
