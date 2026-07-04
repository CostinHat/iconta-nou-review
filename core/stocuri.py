# -*- coding: utf-8 -*-
"""Stocuri — metoda global-valorică (preț cu amănuntul). OMFP 1802/2014.
Motor pur: NIR (adaos + TVA neexigibilă), coeficient K, descărcare lunară.

Formule (OMFP 1802, pct. aferente metodei prețului cu amănuntul):
  K = (Si378 + Rc378) / [(Si371 + Rd371) - (Si4428 + Rc4428)]   (cumulat exercițiu)
  Adaos descărcat (378) = K * Rc707
  4428 descărcat = TVA aferentă vânzărilor
  607 = Rc707 - 378 descărcat
  Nota: % = 371  (607 + 378 + 4428), total = vânzări cu TVA
"""
from decimal import Decimal, ROUND_HALF_UP

MODUL = "stocuri"
REGULI = "2026.1"
TEMEI_GV = "OMFP 1802/2014 - metoda pretului cu amanuntul"


def _d(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))


def _q(v):
    return _d(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _urma(temei=TEMEI_GV):
    return {"modul": MODUL, "reguli": REGULI, "temei": temei}


def nir_gv(linii, cota_tva_implicita=21):
    """NIR global-valoric. linii: [{denumire, cantitate, pret_achizitie (unitar, fara TVA),
    pret_vanzare (unitar, cu TVA), cota_tva?}].
    Întoarce totaluri + notele propuse:
      % = 401  (371 cost, 4426)
      371 = %  (378 adaos, 4428 TVA neexigibila)
    371 final = valoarea la pret de vanzare cu TVA."""
    cost_total = tva_ded = vanzare_total = Decimal("0")
    linii_out = []
    for l in linii:
        cant = _d(l["cantitate"])
        if cant <= 0:
            raise ValueError(f"cantitate invalida la {l.get('denumire')!r}")
        cota = _d(l.get("cota_tva", cota_tva_implicita))
        cost = _q(cant * _d(l["pret_achizitie"]))
        vanz = _q(cant * _d(l["pret_vanzare"]))
        if vanz < cost:
            raise ValueError(f"pret de vanzare sub cost la {l.get('denumire')!r}")
        tva_v = _q(vanz * cota / (100 + cota))          # TVA din pretul de raft (suta marita)
        adaos = _q(vanz - tva_v - cost)
        if adaos < 0:
            raise ValueError(f"adaos negativ la {l.get('denumire')!r}")
        cost_total += cost
        tva_ded += _q(cost * cota / 100)
        vanzare_total += vanz
        linii_out.append({**l, "cost": cost, "vanzare": vanz,
                          "tva_neexigibila": tva_v, "adaos": adaos})
    tva_neex = _q(sum(x["tva_neexigibila"] for x in linii_out))
    adaos_total = _q(vanzare_total - tva_neex - cost_total)
    note = [
        {"debit": "371", "credit": "401", "suma": _q(cost_total), **_urma()},
        {"debit": "4426", "credit": "401", "suma": _q(tva_ded), **_urma()},
        {"debit": "371", "credit": "378", "suma": adaos_total, **_urma()},
        {"debit": "371", "credit": "4428", "suma": tva_neex, **_urma()},
    ]
    return {"linii": linii_out, "cost_total": _q(cost_total), "tva_deductibila": _q(tva_ded),
            "adaos_total": adaos_total, "tva_neexigibila": tva_neex,
            "valoare_vanzare": _q(vanzare_total), "note": note}


def coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428):
    """Coeficientul K, cumulat de la inceputul exercitiului."""
    numitor = (_d(si_371) + _d(rd_371)) - (_d(si_4428) + _d(rc_4428))
    if numitor <= 0:
        raise ValueError("numitor <= 0: solduri/rulaje 371/4428 inconsistente")
    return (_d(si_378) + _d(rc_378)) / numitor


def descarcare_gv(rc_707, tva_vanzari, si_378, rc_378, si_371, rd_371, si_4428, rc_4428):
    """Descarcarea lunara a gestiunii. rc_707 = venituri din vanzarea marfurilor (fara TVA),
    tva_vanzari = TVA colectata aferenta (devine 4428 descarcat).
    Intoarce nota % = 371 si detaliile."""
    rc_707 = _d(rc_707)
    if rc_707 < 0:
        raise ValueError("rc_707 negativ")
    if rc_707 == 0:
        return {"k": None, "adaos": _q(0), "cmv": _q(0), "tva": _q(0), "note": []}
    k = coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428)
    adaos = _q(rc_707 * k)
    cmv = _q(rc_707 - adaos)
    tva = _q(tva_vanzari)
    if cmv < 0:
        raise ValueError("CMV negativ: K > 1, verifica soldurile")
    note = [
        {"debit": "607", "credit": "371", "suma": cmv, **_urma()},
        {"debit": "378", "credit": "371", "suma": adaos, **_urma()},
        {"debit": "4428", "credit": "371", "suma": tva, **_urma()},
    ]
    return {"k": k, "adaos": adaos, "cmv": cmv, "tva": tva,
            "total_371": _q(cmv + adaos + tva), "note": note}
