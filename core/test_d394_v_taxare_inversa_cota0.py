# -*- coding: utf-8 -*-
"""GARD D394 - V (livrare cu taxare inversa) trebuie emis cu cota 0 (10.08.2026).

SPEC OFICIAL + VALIDATOR (probat pe date populate + DUK, tenant_016):
  - anaf_surse/d394_struct_anaf.txt poz.217: "valoarea 0 este permisa daca si numai daca
    tip in (LS,AS,ASI,N,V)".
  - poz.68-70 (nrLivV/bazaLivV/tvaLivV): "<>null pt tip_partener=1 si cota=0; =null altfel".
  - DUKIntegrator D394 reguli 2026.1, respins pe cod vechi:
      R217.2: "daca tip (V) este unul din 'LS','AS','N','V' atunci cota (21) trebuie sa fie
               egala cu 0";
      R68.2/R69.2: "daca tip_partener <> 1 sau cota <> 0 atunci nrLivV/bazaLivV nu trebuie sa
               existe" (detaliul livrarii taxare inversa sta doar la cota 0);
      R35: "Nu exista sectiune Detaliu pentru (tip_partener(1), cota(21), ..., codPR)".

DEFECT (cod vechi): o livrare cu taxare inversa (emisa, taxare_inversa) cu linii pe cota
bunului (ex. 21%) devenea op1 tip='V' cu cota=21 -> declaratia era respinsa la DUK.
V nu declara TVA (reverse charge la beneficiar): cota bunului sta in op11/detaliu (bazaLivV
la tip_partener=1, cota=0), NU pe op1. LS/AS/N erau deja emise cu cota 0; V era singurul care
purta cota bunului.

FIX (core.d394._adauga): cheia op1 forteaza cota=0 pentru tip=='V' (centralizat -> acopera si
calea facturilor, si calea manuala).

MUTATIE (un gard care nu pica pe codul vechi nu e gard):
  - o livrare taxare inversa cu cota bunului 21 -> cod vechi: op1 key (V,1,21,...) ; asertia
    "exista (V,...,0) si NU exista niciun (V,...,cota!=0)" PICA pe cod vechi.

Seam PUR: core.d394.calcul_d394(prof, perioada, {"facturi":[...]}) - fara DB.
"""
from decimal import Decimal

from core import d394
from core.common import Perioada

_PROF = {"tva_la_incasare": False}
_PER = Perioada(2026, luna=8)


def _fact_v(cota):
    """Livrare cu taxare inversa (emisa) catre partener RO platitor, categorie art.331."""
    return {"cui": "100018", "platitor_tva": True, "nume": "CLIENT TEL",
            "directie": "emisa", "taxare_inversa": True,
            "cota": cota, "baza": Decimal("1000"), "tva": Decimal("210"),
            "categorie_331": "telefoane"}


def test_v_taxare_inversa_este_emis_cu_cota_0():
    """O livrare taxare inversa cu linii pe cota bunului (21%) trebuie sa apara in op1 cu
    cota=0 (R217.2). Cod vechi o pastra la cota=21 -> respinsa DUK."""
    res = d394.calcul_d394(_PROF, _PER, {"facturi": [_fact_v(21)], "serii": {}})
    chei_v = [k for k in res.op1 if k[0] == "V"]
    assert chei_v, "asteptam o operatiune V (livrare taxare inversa)"
    # niciun V la cota <> 0 (cod vechi: (V,1,21,...) -> pica)
    assert all(k[2] == 0 for k in chei_v), \
        "V trebuie emis cu cota 0 (R217.2); gasit: %r" % (chei_v,)
    # cheia asteptata exista exact la cota 0
    assert any(k[0] == "V" and k[2] == 0 for k in res.op1)


def test_v_taxare_inversa_detaliu_doar_la_cota_0():
    """Detaliul livrarii taxare inversa (nrLivV/bazaLivV) sta la (tip_partener=1, cota=0),
    niciodata la cota<>0 (R68.2/R69.2)."""
    res = d394.calcul_d394(_PROF, _PER, {"facturi": [_fact_v(21)], "serii": {}})
    for (tp, cota, bun), d in res.detaliu.items():
        if d.get("nrLivV") or d.get("bazaLivV"):
            assert cota == 0, \
                "nrLivV/bazaLivV apar la cota %r (trebuie doar la cota 0): %r" % (cota, d)
