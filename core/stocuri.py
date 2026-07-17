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


def nir_gv(linii, cota_tva_implicita=21, transport=0, taxe=0,
          cont_transport="401", cont_taxe="446"):
    """NIR global-valoric. linii: [{denumire, cantitate, pret_achizitie (unitar, fara TVA),
    pret_vanzare (unitar, cu TVA), cota_tva?}].
    transport/taxe: cost accesoriu (landed cost) care se CAPITALIZEAZA in costul de
    achizitie (OMFP 1802/2014: cost achizitie = pret + taxe nerecuperabile de import +
    cheltuieli de transport direct atribuibile). Se repartizeaza pe linii PROPORTIONAL cu
    costul de baza (cheia standard cand nu e direct atribuibil), cu restul de rotunjire pe
    ultima linie ca suma sa fie exacta. cont_transport/cont_taxe = contul de credit al
    accesoriului (confirmat de contabil: 401 furnizor transport / 446 taxe vamale - default).
    Întoarce totaluri + notele propuse:
      371 = 401   (cost marfa de baza)
      4426 = 401  (TVA deductibila pe marfa)
      371 = cont_transport / cont_taxe  (accesoriu capitalizat, daca > 0)
      371 = 378   (adaos, recalculat dupa capitalizare)
      371 = 4428  (TVA neexigibila)
    371 final = valoarea la pret de vanzare cu TVA."""
    transport = _q(transport); taxe = _q(taxe)
    if transport < 0 or taxe < 0:
        raise ValueError("transport/taxe negative")
    accesoriu = transport + taxe
    baze = []
    for l in linii:
        cant = _d(l["cantitate"])
        if cant <= 0:
            raise ValueError(f"cantitate invalida la {l.get('denumire')!r}")
        baze.append(_q(cant * _d(l["pret_achizitie"])))
    baza_totala = sum(baze, Decimal("0"))
    if accesoriu > 0 and baza_totala <= 0:
        raise ValueError("accesoriu > 0 dar cost de baza 0 - nu se poate repartiza")
    # repartizare proportionala cu restul pe ultima linie (suma repartizata == accesoriu)
    reparti = []
    ramas = accesoriu
    for i, b in enumerate(baze):
        if accesoriu <= 0:
            reparti.append(Decimal("0.00"))
        elif i == len(baze) - 1:
            reparti.append(ramas)
        else:
            cota_r = _q(accesoriu * b / baza_totala)
            reparti.append(cota_r); ramas -= cota_r

    cost_baza_total = tva_ded = vanzare_total = Decimal("0")
    linii_out = []
    for l, cost_baza, land in zip(linii, baze, reparti):
        cant = _d(l["cantitate"])
        cota = _d(l.get("cota_tva", cota_tva_implicita))
        cost = _q(cost_baza + land)                     # cost de achizitie cu accesoriu
        vanz = _q(cant * _d(l["pret_vanzare"]))
        if vanz < cost:
            raise ValueError(f"pret de vanzare sub costul de achizitie (cu accesoriu) la {l.get('denumire')!r}")
        tva_v = _q(vanz * cota / (100 + cota))          # TVA din pretul de raft (suta marita)
        adaos = _q(vanz - tva_v - cost)
        if adaos < 0:
            raise ValueError(f"adaos negativ la {l.get('denumire')!r}")
        cost_baza_total += cost_baza
        tva_ded += _q(cost_baza * cota / 100)           # TVA deductibila pe marfa (accesoriul are TVA-ul lui, separat)
        vanzare_total += vanz
        linii_out.append({**l, "cost_baza": cost_baza, "landed": land, "cost": cost,
                          "vanzare": vanz, "tva_neexigibila": tva_v, "adaos": adaos})
    tva_neex = _q(sum(x["tva_neexigibila"] for x in linii_out))
    cost_total = _q(cost_baza_total + accesoriu)
    adaos_total = _q(vanzare_total - tva_neex - cost_total)
    note = [
        {"debit": "371", "credit": "401", "suma": _q(cost_baza_total), **_urma()},
        {"debit": "4426", "credit": "401", "suma": _q(tva_ded), **_urma()},
    ]
    if transport > 0:
        note.append({"debit": "371", "credit": cont_transport, "suma": transport, **_urma()})
    if taxe > 0:
        note.append({"debit": "371", "credit": cont_taxe, "suma": taxe, **_urma()})
    note += [
        {"debit": "371", "credit": "378", "suma": adaos_total, **_urma()},
        {"debit": "371", "credit": "4428", "suma": tva_neex, **_urma()},
    ]
    return {"linii": linii_out, "cost_total": cost_total, "cost_baza_total": _q(cost_baza_total),
            "transport": transport, "taxe": taxe, "tva_deductibila": _q(tva_ded),
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
