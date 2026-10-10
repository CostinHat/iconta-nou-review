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
TEMEI_COST = "OMFP 1802/2014 pct.286 alin.(1), pct.287 alin.(1)-(2) - evaluare la cost, aplicata cu consecventa"


def _d(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))


def _q(v):
    return _d(v).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _urma(temei=TEMEI_GV):
    return {"modul": MODUL, "reguli": REGULI, "temei": temei}


class RefuzLinie(ValueError):
    """[lotul 07.10 B, C11a] Refuzul unui ARTICOL din NIR: mesajul + linia și câmpul, ca ecranul să-l pună lângă câmp."""
    def __init__(self, mesaj, linie, camp):
        super().__init__(mesaj)
        self.linie, self.camp = linie, camp


def _repartizeaza(linii, transport, taxe):
    """Costul de bază pe linie și accesoriul (transport + taxe) repartizat proporțional, cu restul pe ultima linie (OMFP 1802/2014:
    costul de achiziție cuprinde prețul, taxele nerecuperabile și transportul direct atribuibil). -> (baze, reparti, accesoriu)."""
    transport = _q(transport); taxe = _q(taxe)
    if transport < 0 or taxe < 0:
        raise ValueError("Transportul și taxele nu pot fi negative.")
    accesoriu = transport + taxe
    baze = []
    for i, l in enumerate(linii):
        cant = _d(l["cantitate"])
        if cant <= 0:
            raise RefuzLinie("Cantitatea trebuie să fie mai mare decât zero la «%s»." % (l.get("denumire") or ""), i, "cantitate")
        baze.append(_q(cant * _d(l["pret_achizitie"])))
    baza_totala = sum(baze, Decimal("0"))
    if accesoriu > 0 and baza_totala <= 0:
        raise ValueError("Costul accesoriu nu se poate repartiza: costul de bază al articolelor e zero.")
    reparti, ramas = [], accesoriu
    for i, b in enumerate(baze):
        if accesoriu <= 0:
            reparti.append(Decimal("0.00"))
        elif i == len(baze) - 1:
            reparti.append(ramas)
        else:
            cota_r = _q(accesoriu * b / baza_totala)
            reparti.append(cota_r); ramas -= cota_r
    return baze, reparti, transport, taxe


def nir_cost(linii, transport=0, taxe=0, cont_transport="401", cont_taxe="446", cont_furnizor="401", cont_tva="4426"):
    """[lotul 07.10 B, C10] NIR la firma cu stocul la COST (cantitativ-valoric, CMP — `core.metoda_stoc`): marfa intră la costul
    de achiziție (cu accesoriul repartizat), fără adaos și fără TVA neexigibilă — prețul de raft nu se cere și nu se verifică.
    Temei: OMFP 1802/2014 pct.286 alin.(1) — ieșirile se evaluează la cost (CMP / FIFO), iar pct.287 alin.(1)-(2): „Metoda aleasă
    trebuie aplicată cu consecvență”, deci intrarea se evaluează pe aceeași bază ca ieșirea (607=371 la CMP). Note:
      371 = 401  (cost de bază) · 4426 = 401 (TVA deductibilă) · 371 = cont_transport / cont_taxe (accesoriu capitalizat)."""
    baze, reparti, transport, taxe = _repartizeaza(linii, transport, taxe)
    linii_out, tva_ded = [], Decimal("0")
    for i, (l, cost_baza, land) in enumerate(zip(linii, baze, reparti)):
        if l.get("cota_tva") is None:
            raise RefuzLinie("Alege cota de TVA la «%s»." % (l.get("denumire") or ""), i, "cota_tva")
        tva_ded += _q(cost_baza * _d(l["cota_tva"]) / 100)
        linii_out.append({**l, "cost_baza": cost_baza, "landed": land, "cost": _q(cost_baza + land)})
    cost_baza_total = _q(sum(baze, Decimal("0")))
    # [08.10.2026, decizia Costin §6 pct.1 + pct.3] NIR-ul FĂRĂ factură: 371 = 408 și TVA pe 4428 (analiticul de achiziție) = 408 —
    # apelantul (`stocuri_api.adauga_nir`) dă conturile; implicit, NIR-ul cu factură: 371 = 401, 4426 = 401.
    note = [{"debit": "371", "credit": cont_furnizor, "suma": cost_baza_total, **_urma(TEMEI_COST)},
            {"debit": cont_tva, "credit": cont_furnizor, "suma": _q(tva_ded), **_urma(TEMEI_COST)}]
    if transport > 0:
        note.append({"debit": "371", "credit": cont_transport, "suma": transport, **_urma(TEMEI_COST)})
    if taxe > 0:
        note.append({"debit": "371", "credit": cont_taxe, "suma": taxe, **_urma(TEMEI_COST)})
    return {"linii": linii_out, "cost_total": _q(cost_baza_total + transport + taxe), "cost_baza_total": cost_baza_total,
            "transport": transport, "taxe": taxe, "tva_deductibila": _q(tva_ded), "adaos_total": Decimal("0.00"),
            "tva_neexigibila": Decimal("0.00"), "valoare_vanzare": Decimal("0.00"), "note": note}


def nir_gv(linii, cota_tva_implicita=None, transport=0, taxe=0,
          cont_transport="401", cont_taxe="446", cont_furnizor="401", cont_tva="4426"):
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
    # [R29 per-linie, reparat] Garda cotei se aplica PE LINIE (vezi bucla de mai jos), NU pe param-ul
    # global. Pana la reparatie garda de aici ridica NECONDITIONAT cand globalul lipsea - dar apelantul
    # unic (`stocuri_api.adauga_nir`) trimite cota PER LINIE si NU paseaza niciodata param-ul global,
    # deci garda veche rupea ORICE NIR (422 "Cota de TVA nu s-a dat" desi fiecare linie avea cota 21).
    # R29 cere cota explicita, nu o cota GLOBALA: cota poate diferi de la o linie la alta. Deci se
    # pastreaza interdictia de default tacit, dar la nivel de linie (gardata de test_stocuri.py, nu de
    # test_cota_fara_default.py care testeaza param-ul de nivel-functie). Param-ul global ramane
    # fallback OPTIONAL (o singura cota pentru tot NIR-ul), nu obligatoriu.
    baze, reparti, transport, taxe = _repartizeaza(linii, transport, taxe)   # o singură repartizare (și pentru `nir_cost`)
    accesoriu = transport + taxe

    cost_baza_total = tva_ded = vanzare_total = Decimal("0")
    linii_out = []
    for _i, (l, cost_baza, land) in enumerate(zip(linii, baze, reparti)):
        cant = _d(l["cantitate"])
        _cota_raw = l.get("cota_tva")
        if _cota_raw is None:
            _cota_raw = cota_tva_implicita                # fallback optional (o cota pentru tot NIR-ul)
        if _cota_raw is None:                             # [R29] nicio cota declarata pe aceasta linie -> STOP, fara default tacit
            raise ValueError("Cota de TVA nu s-a dat. Nu se folosește o valoare implicită: o cotă scrisă în cod se rupe tăcut de lege la prima schimbare, iar o operațiune veche are altă cotă decât una de azi. Declară cota operațiunii.")
        cota = _d(_cota_raw)
        cost = _q(cost_baza + land)                     # cost de achizitie cu accesoriu
        vanz = _q(cant * _d(l["pret_vanzare"]))
        if vanz < cost:
            raise RefuzLinie("Prețul de raft e sub costul de achiziție (cu transportul și taxele repartizate) la «%s»: %s lei la "
                             "raft, %s lei cost." % (l.get("denumire") or "", vanz, cost), _i, "pret_vanzare")
        tva_v = _q(vanz * cota / (100 + cota))          # TVA din pretul de raft (suta marita)
        adaos = _q(vanz - tva_v - cost)
        if adaos < 0:
            raise RefuzLinie("Adaosul iese negativ la «%s»: prețul de raft fără TVA e sub cost." % (l.get("denumire") or ""),
                             _i, "pret_vanzare")
        cost_baza_total += cost_baza
        tva_ded += _q(cost_baza * cota / 100)           # TVA deductibila pe marfa (accesoriul are TVA-ul lui, separat)
        vanzare_total += vanz
        linii_out.append({**l, "cost_baza": cost_baza, "landed": land, "cost": cost,
                          "vanzare": vanz, "tva_neexigibila": tva_v, "adaos": adaos})
    tva_neex = _q(sum(x["tva_neexigibila"] for x in linii_out))
    cost_total = _q(cost_baza_total + accesoriu)
    adaos_total = _q(vanzare_total - tva_neex - cost_total)
    note = [   # [08.10, §6 pct.1 + pct.3] fără factură: 371 = 408, 4428.01 = 408 (vezi `nir_cost`)
        {"debit": "371", "credit": cont_furnizor, "suma": _q(cost_baza_total), **_urma()},
        {"debit": cont_tva, "credit": cont_furnizor, "suma": _q(tva_ded), **_urma()},
    ]
    if transport > 0:
        note.append({"debit": "371", "credit": cont_transport, "suma": transport, **_urma()})
    if taxe > 0:
        note.append({"debit": "371", "credit": cont_taxe, "suma": taxe, **_urma()})
    note += [
        {"debit": "371", "credit": "378", "suma": adaos_total, **_urma()},
        {"debit": "371", "credit": CONT_TVA_STOC, "suma": tva_neex, **_urma()},
    ]
    return {"linii": linii_out, "cost_total": cost_total, "cost_baza_total": _q(cost_baza_total),
            "transport": transport, "taxe": taxe, "tva_deductibila": _q(tva_ded),
            "adaos_total": adaos_total, "tva_neexigibila": tva_neex,
            "valoare_vanzare": _q(vanzare_total), "note": note}


#: [08.10.2026, decizia Costin la §6 al lotului „Deciziile 08.10 §6”, pct.1, verbatim în DECIZII] „analitic propriu pentru TVA-ul din
#: prețul de raft, cu migrarea soldurilor existente. În bilanț acesta se scade doar din stocuri (rd.05) și nu mai apare la datorii.”
#: TVA-ul neexigibil din prețul cu amănuntul (global-valoric: `371 = 4428.02` la NIR, `4428.02 = 371` la descărcare) stă pe analiticul
#: lui, separat de TVA-ul la încasare (sinteticul 4428) și de TVA-ul NIR-ului fără factură (4428.01). OMFP 1802/2014, bilanțul
#: prescurtat, rd.05 STOCURI: „… 371 +/- 378 … - din ct. 4428”.
CONT_TVA_STOC = "4428.02"


def coeficient_k(si_378, rc_378, si_371, rd_371, si_4428, rc_4428):
    """Coeficientul K, cumulat de la inceputul exercitiului."""
    numitor = (_d(si_371) + _d(rd_371)) - (_d(si_4428) + _d(rc_4428))
    if numitor <= 0:
        raise ValueError(
            "Nu se poate calcula coeficientul de adaos: valoarea mărfurilor la preț de vânzare "
            "(contul 371) minus TVA neexigibilă (contul 4428) dă zero sau negativ. Verifică "
            "soldurile și rulajele conturilor 371 și 4428 pe perioada aleasă — până atunci "
            "descărcarea de gestiune nu se poate face.")
    return (_d(si_378) + _d(rc_378)) / numitor


def descarcare_gv(rc_707, tva_vanzari, si_378, rc_378, si_371, rd_371, si_4428, rc_4428):
    """Descarcarea lunara a gestiunii. rc_707 = venituri din vanzarea marfurilor (fara TVA),
    tva_vanzari = TVA colectata aferenta (devine 4428 descarcat).
    Intoarce nota % = 371 si detaliile."""
    rc_707 = _d(rc_707)
    if rc_707 < 0:
        raise ValueError("rc_707 negativ")  # invariant-intern-ok: invariant de calcul
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
        {"debit": CONT_TVA_STOC, "credit": "371", "suma": tva, **_urma()},
    ]
    return {"k": k, "adaos": adaos, "cmv": cmv, "tva": tva,
            "total_371": _q(cmv + adaos + tva), "note": note}
