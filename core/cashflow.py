# -*- coding: utf-8 -*-
"""Forecast cash-flow 8 saptamani: cash curent + incasari/plati asteptate pe scadente.

[lotul 13, deficiențele 553 + 559, comanda Costin 13.1] Până azi soldul 4111 / 401 din balanță se împărțea pe facturi „de la cele mai noi
spre vechi” (`aloca_sold`), iar săptămâna întâi aduna totul fără să spună din ce: pe F1 „15.423 lei” la plăți, când furnizorii erau 3.000.
Acum:
  * încasările / plățile așteptate vin din FACTURILE DESCHISE cu nota validată (`repo_portal.facturi_deschise_validate`) — aceeași bază ca
    „De încasat” din „Cifrele firmei” și ca Scadențarul portalului —, fiecare cu restul ei în lei și scadența ei; ce arată balanța în plus
    față de facturi (sold preluat nedefalcat, avans) intră o dată, în săptămâna întâi, numit ca atare (`din_facturi`);
  * fiecare săptămână își spune componentele (`forecast` -> `componente`): facturi de la furnizori, salarii nete, impozite și contribuții,
    cheltuieli lunare estimate;
  * media cheltuielilor lunare cuprinde și salariile (641 / 645) — până azi le scotea („acoperite de 421 / 431”), dar 421 / 431 acoperă
    numai luna trecută, deci lunile următoare plecau fără salarii — și se împarte la lunile cu evidență în iConta.eu (`luni_cu_evidenta`),
    nu la luna calendaristică: pe F1 (evidență din septembrie) media ieșea „~117 lei” din 15.074 lei cheltuiți în două luni.
"""
import datetime
from decimal import Decimal, ROUND_HALF_UP

from core.motor import GRUPE_IMPOZIT   # 69x / 79x: impozitul pe profit / venit (OMFP 1802/2014, grupa 69) — se plătește din 441, nu din medie

#: Ce înseamnă fiecare sumă din previziune, în cuvintele clientului (rândul săptămânii le spune).
CE_FACTURI_CLIENTI = "facturi către clienți"
CE_FACTURI_FURNIZORI = "facturi de la furnizori"
CE_SOLD_INCASAT_FARA_FACTURA = "sold de încasat fără factură în evidență (preluat sau avans)"
CE_SOLD_PLATIT_FARA_FACTURA = "sold de plătit fără factură în evidență (preluat sau avans)"
CE_SALARII = "salarii nete"
CE_FISCALE = "impozite, taxe și contribuții"
CE_MEDIE = "cheltuieli lunare estimate (media lunilor)"


def _bani(x):
    return Decimal(str(x or 0))


def din_facturi(facturi, sold_balanta, ce, ce_fara_factura, azi):
    """Încasările (sau plățile) așteptate dintr-o listă de facturi deschise (`repo_facturi.de_incasat`: `rest_lei`, `data_scadenta`,
    `data_emitere`), fiecare la scadența ei (fără scadență: la emitere, deci în săptămâna întâi). Ce arată balanța (`sold_balanta`, în lei)
    peste suma facturilor intră o dată, azi, cu numele `ce_fara_factura` — previziunea pornește tot din balanță, dar spune ce nu e factură."""
    out = [{"data_scadenta": str(f.get("data_scadenta") or f.get("data_emitere") or azi), "suma": _bani(f.get("rest_lei")), "ce": ce}
           for f in facturi if _bani(f.get("rest_lei")) > 0]
    rest = _bani(sold_balanta) - sum((x["suma"] for x in out), Decimal(0))
    if rest > 0:
        out.append({"data_scadenta": azi.isoformat(), "suma": rest, "ce": ce_fara_factura})
    return out


def forecast(cash, emise_deschise, primite_deschise, azi=None, saptamani=8):
    """Proiectie saptamanala. Scadentele trecute intra in saptamana 1. Fiecare săptămână: încasări, plăți, soldul de la sfârșitul ei și
    `componente` = [{ce, sens: "+"/"-", suma}] — din ce e formată (553)."""
    azi = azi or datetime.date.today()
    sold = _bani(cash)
    rez = []
    for w in range(saptamani):
        inceput = azi + datetime.timedelta(days=7 * w)
        sfarsit = inceput + datetime.timedelta(days=7)

        def _in(f):
            d = f.get("data_scadenta")
            d = datetime.date.fromisoformat(str(d)[:10]) if d else azi
            if w == 0:
                return d < sfarsit
            return inceput <= d < sfarsit
        componente = {}
        for sens, lista in (("+", emise_deschise), ("-", primite_deschise)):
            for f in lista:
                if _in(f):
                    k = (sens, f.get("ce") or "")
                    componente[k] = componente.get(k, Decimal(0)) + _bani(f.get("suma"))
        inc = sum((v for (s, _c), v in componente.items() if s == "+"), Decimal(0))
        pla = sum((v for (s, _c), v in componente.items() if s == "-"), Decimal(0))
        sold = sold + inc - pla
        rez.append({"saptamana": w + 1, "de_la": inceput.isoformat(),
                    "incasari": float(inc), "plati": float(pla), "sold": float(sold),
                    "componente": [{"ce": c, "sens": s, "suma": float(v)} for (s, c), v in componente.items()]})
    return rez


def obligatii_din_balanta(randuri):
    """Solduri creditoare de platit: fiscale (25 ale lunii) + salarii nete (imediat). [553] + 4418, impozitul pe veniturile
    microîntreprinderii (CF art.56 alin.(1): „Calculul și plata impozitului pe veniturile microîntreprinderilor se efectuează trimestrial,
    până la data de 25 inclusiv a lunii următoare trimestrului”), care lipsea: la o firmă micro previziunea nu plătea impozitul."""
    def _sc(prefixe):
        return float(sum((_bani(r["sf_c"]) for r in randuri if any(str(r["cont"]).startswith(p) for p in prefixe)), Decimal(0)))
    return {"fiscale": _sc(("4423", "431", "436", "444", "4411", "4418")),
            "salarii_nete": _sc(("421",))}


def luni_cu_evidenta(azi, preluare, rulaje_preluate):
    """[553] Lunile anului `azi.year` din cumulatul balanței: de la 1 ianuarie dacă evidența e mai veche decât anul sau dacă balanța de
    deschidere a adus rulajele anului (`rulaje_preluate.are_rulaje`); altfel de la luna preluării (`luna_preluare.efectiva`, (an, luna)).
    Întoarce (luna_de_la, numărul de luni), cel puțin o lună."""
    de_la = 1
    if preluare and tuple(preluare) >= (azi.year, 1) and not rulaje_preluate:
        de_la = min(int(preluare[1]), azi.month) if int(preluare[0]) == azi.year else azi.month
    return de_la, azi.month - de_la + 1


def cheltuieli_lunare_cash(randuri, luni_scurse):
    """Media lunara a cheltuielilor cash: cl.6 fara 68x (amortizari, provizioane: fără ieșire de bani) și fără grupa 69 (impozitul, plătit
    din 441 la obligații). [553] Salariile (641 / 645) intră: 421 / 431 din balanță acoperă numai luna trecută."""
    from core.documente_api import rulaje_cumulate   # cumulatul anului; `rul_*` e acum luna (W1, 08.10)
    ch = sum((_bani(rulaje_cumulate(r, "d")) - _bani(rulaje_cumulate(r, "c")) for r in randuri
              if str(r["cont"]).startswith("6") and not str(r["cont"]).startswith(("68",) + GRUPE_IMPOZIT)), Decimal(0))
    return float((ch / max(int(luni_scurse), 1)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))   # bani, cu rotunjire aritmetică


def plati_estimate(obligatii, medie_lunara, azi=None, saptamani=8):
    """Genereaza lista de plati estimate: [{data_scadenta, suma, ce}]."""
    azi = azi or datetime.date.today()
    plati = []
    if obligatii.get("salarii_nete"):
        plati.append({"data_scadenta": azi.isoformat(), "suma": obligatii["salarii_nete"], "ce": CE_SALARII})
    # termenul obligațiilor lunare din sursa unică (scadente): mutat la zi lucrătoare, iar în decembrie pe 21 (CPF
    # art.155 alin.(2)) — înainte, ziua era scrisă aici și cădea pe 25 decembrie (lot 19 defect 7)
    from core import scadente
    termen = scadente.urmatorul_termen_lunar(azi)
    if obligatii.get("fiscale"):
        plati.append({"data_scadenta": termen.isoformat(), "suma": obligatii["fiscale"], "ce": CE_FISCALE})
    if medie_lunara > 0:
        d = azi
        for _ in range(max(1, saptamani // 4)):
            d = (d.replace(day=1) + datetime.timedelta(days=32)).replace(day=min(azi.day, 28))
            plati.append({"data_scadenta": d.isoformat(), "suma": medie_lunara, "ce": CE_MEDIE})
    return plati
