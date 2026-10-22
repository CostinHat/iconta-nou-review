# -*- coding: utf-8 -*-
"""Diferente de curs valutar (665/765) - motor PUR.
Sursa: OMFP 1802/2014 pct.322 (diferentele la DECONTAREA creantelor/datoriilor in valuta) si pct.325
(REEVALUAREA LUNARA). [lotul 10, deficienta 429] Citarea veche „pct. 316” era gresita: pct.316 e dispozitia
tranzitorie despre avansuri (409 / 419 nu se mai evalueaza la curs) — textul de la pct.325, verbatim
(`anaf_surse/omfp_1802_2014_reglementari_consolidat.txt`):
  OMFP 1802/2014 pct.325 alin.(1): „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al
  pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză. Diferențele de curs înregistrate
  se recunosc în contabilitate la venituri sau cheltuieli din diferențe de curs valutar, după caz.”
  OMFP 1802/2014 pct.325 alin.(2) lit.b: „[...] din ultima zi bancară a lunii în cauză, pentru evaluarea creanțelor și datoriilor
  în valută, a disponibilităților în valută și a altor valori de trezorerie [...] existente în sold la sfârșitul lunii.”
  OMFP 1802/2014 pct.325 alin.(3): creantele/datoriile in lei cu decontare in functie de cursul unei valute -> „alte venituri
  financiare sau alte cheltuieli financiare” (768 / 668; la data bilantului, pct.94 lit.b).
Reguli de semn:
- CREANTA (4111, 461...) sau DISPONIBIL (5124): curs creste -> castig 765;
- DATORIE (401, 462...): curs creste -> pierdere 665."""
from decimal import Decimal, ROUND_HALF_UP
from core.common import nomenclator_cerut

B = Decimal("0.01")
TIPURI = ("creanta", "disponibil", "datorie")


def _d(x):
    return Decimal(str(x or 0))


def _cont_si_sens(dif, tip, in_lei_cu_clauza=False):
    """dif = cu cat creste valoarea in lei a elementului (semnat). -> (cont, sens) sau (None, None) la 0. O SINGURA regula de semn,
    pentru decontare si pentru reevaluare: la creanta / disponibil cresterea e castig, la datorie e pierdere."""
    if tip not in TIPURI:
        raise ValueError(nomenclator_cerut("tip", "|".join(TIPURI)))
    if dif == 0:
        return None, None
    castig = dif > 0 if tip in ("creanta", "disponibil") else dif < 0
    cont_venit, cont_chelt = ("768", "668") if in_lei_cu_clauza else ("765", "665")
    return (cont_venit if castig else cont_chelt), ("favorabila" if castig else "nefavorabila")


def diferenta(valoare_valuta, curs_initial, curs_final, tip, in_lei_cu_clauza=False):
    """tip: creanta|disponibil|datorie. Returneaza {diferenta (abs), cont, sens} sau diferenta=0.
    [1b] in_lei_cu_clauza: creanta/datorie IN LEI decontata in functie de cursul unei valute ->
    diferentele merg la 768/668 (alte venituri/cheltuieli financiare), nu 765/665 (OMFP 1802/2014
    pct. 94 lit. b)."""
    v, c1, c2 = _d(valoare_valuta), _d(curs_initial), _d(curs_final)
    if v <= 0 or c1 <= 0 or c2 <= 0:
        raise ValueError("Una sau mai multe valori sunt invalide. Verifică sumele și cantitățile introduse.")
    if tip not in TIPURI:
        raise ValueError(nomenclator_cerut("tip", "|".join(TIPURI)))
    dif = (v * (c2 - c1)).quantize(B, rounding=ROUND_HALF_UP)
    cont, sens = _cont_si_sens(dif, tip, in_lei_cu_clauza)
    if not cont:
        return {"diferenta": Decimal("0.00"), "cont": None, "sens": None}
    return {"diferenta": abs(dif), "cont": cont, "sens": sens}

def nota_decontare(valoare_valuta, curs_factura, curs_decontare, tip,
                   cont_tert, cont_banca="5124", in_lei_cu_clauza=False):
    """Nota la incasare creanta / plata datorie. Diferenta pe 665/765 (valuta) sau 668/768
    (in lei cu clauza valutara, OMFP 1802/2014 pct. 94 lit. b)."""
    v = _d(valoare_valuta)
    lei_factura = (v * _d(curs_factura)).quantize(B, rounding=ROUND_HALF_UP)
    lei_decont = (v * _d(curs_decontare)).quantize(B, rounding=ROUND_HALF_UP)
    d = diferenta(v, curs_factura, curs_decontare, tip, in_lei_cu_clauza=in_lei_cu_clauza)
    linii = []
    if tip == "creanta":
        linii.append((cont_banca, cont_tert, lei_factura))
        if d["sens"] == "favorabila":
            linii.append((cont_banca, d["cont"], d["diferenta"]))
        elif d["sens"] == "nefavorabila":
            linii.append((d["cont"], cont_banca, d["diferenta"]))
    else:  # datorie
        linii.append((cont_tert, cont_banca, lei_factura))
        if d["sens"] == "nefavorabila":
            linii.append((d["cont"], cont_banca, d["diferenta"]))
        elif d["sens"] == "favorabila":
            linii.append((cont_banca, d["cont"], d["diferenta"]))
    return {"lei_evidenta": lei_factura, "lei_decontare": lei_decont,
            "diferenta": d, "linii": linii}


def _linie_reevaluare(d, cont_sold):
    """Linia notei de reevaluare: castigul se crediteaza (cont = 765), pierderea se debiteaza (665 = cont)."""
    if d["sens"] == "favorabila":
        return (cont_sold, d["cont"], d["diferenta"])
    return (d["cont"], cont_sold, d["diferenta"])


def reevaluare_element(sold_valuta, lei_evidenta, curs_bnr, tip, cont_sold, in_lei_cu_clauza=False):
    """[lotul 10, deficienta 429] Reevaluarea unui element propus de aplicatie, pe VALOAREA IN LEI din evidenta (nu pe cursul ei):
    elementul ajunge la `sold_valuta x curs BNR` (rotunjit la ban, ROUND_HALF_UP), iar diferenta e exact cat lipseste soldului in lei
    din evidenta pana acolo — OMFP 1802/2014 pct.325 alin.(1): „se evaluează la cursul de schimb [...] din ultima zi bancară a
    lunii”. Pe curs (`diferenta`) diferenta ar fi `v x (c2 - c1)` rotunjita o data, care poate lasa soldul in lei la un ban
    de `v x c2` cand soldul vechi era el insusi rotunjit; pe disponibilitati cursul din evidenta e chiar un raport (lei / valuta).
    -> {lei_nou, diferenta (semnata: cu cat creste soldul in lei), cont, sens, linie (None la 0)}."""
    v, lei, c2 = _d(sold_valuta), _d(lei_evidenta), _d(curs_bnr)
    if v <= 0 or c2 <= 0:
        raise ValueError("Soldul în valută și cursul BNR trebuie să fie pozitive.")
    lei_nou = (v * c2).quantize(B, rounding=ROUND_HALF_UP)
    dif = lei_nou - lei.quantize(B, rounding=ROUND_HALF_UP)
    cont, sens = _cont_si_sens(dif, tip, in_lei_cu_clauza)
    d = {"diferenta": abs(dif), "cont": cont, "sens": sens}
    return {"lei_nou": lei_nou, "diferenta": dif, "cont": cont, "sens": sens,
            "linie": _linie_reevaluare(d, cont_sold) if cont else None}
