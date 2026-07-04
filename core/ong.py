# -*- coding: utf-8 -*-
"""ONG contabilitate specifica - motor PUR (OMFP 3103/2017 anexa 1, partida
dubla + art. 15 alin. 2-3 CF).
- venituri fara scop patrimonial (grupa 73): 731 cotizatii/contributii
  membri si simpatizanti/cote-parti statutare; 733 donatii si sume primite
  prin sponsorizare/ajutoare; 734 venituri financiare AFSP (dobanzi,
  dividende, dif. curs); 736 resurse fonduri publice/finantari nerambursabile;
  738 actiuni ocazionale (evenimente, tombole, conferinte); 739 alte;
- evidenta DISTINCTA pe activitati: fara scop patrimonial (73x/6xx analitic
  AFSP, rezultat 121.AFSP) vs economice (70x-76x conform OMFP 1802,
  rezultat 121.EC);
- fiscal art. 15(2)-(3): veniturile AFSP = neimpozabile; veniturile
  ECONOMICE scutite pana la min(15.000 EUR/an fiscal la cursul de la
  finele anului; 10% din veniturile neimpozabile); excedentul = impozit
  pe profit 16% (D101)."""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
CONT_VENIT = {"cotizatie": "731", "contributie": "731", "donatie": "733",
              "sponsorizare": "733", "financiar": "734", "fonduri": "736",
              "ocazional": "738", "alte": "739"}
PLAFON_EUR = Decimal("15000")

def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)

def nota_venit(suma, fel="cotizatie", sursa="casa"):
    """Incasare venit AFSP: 5311/5121 = 73x."""
    s = _d(suma)
    if s <= 0:
        raise ValueError("suma invalida")
    cont = CONT_VENIT.get(fel)
    if not cont:
        raise ValueError("fel: " + "|".join(CONT_VENIT))
    bani = "5311" if sursa == "casa" else "5121"
    return {"linii": [(bani, cont, s)], "cont_venit": cont}

def scutire_economica(venituri_economice_an, venituri_neimpozabile_an, curs_eur):
    """Art. 15(3): scutit = min(15.000 EUR x curs; 10% x venituri neimpozabile).
    Excedentul intra la impozit pe profit 16%."""
    ve, vn = _d(venituri_economice_an), _d(venituri_neimpozabile_an)
    c = Decimal(str(curs_eur))
    if ve < 0 or vn < 0 or c <= 0:
        raise ValueError("valori invalide")
    p1 = (PLAFON_EUR * c).quantize(B, rounding=ROUND_HALF_UP)
    p2 = (vn * Decimal("0.10")).quantize(B, rounding=ROUND_HALF_UP)
    plafon = min(p1, p2)
    scutit = min(ve, plafon)
    impozabil = ve - scutit
    return {"plafon_15000_eur": p1, "plafon_10pct": p2, "plafon": plafon,
            "scutit": scutit, "impozabil": impozabil,
            "impozit_estimat": (impozabil * Decimal("0.16"))
                .quantize(B, rounding=ROUND_HALF_UP)}
