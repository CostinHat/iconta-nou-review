# -*- coding: utf-8 -*-
"""Compensari cu tertii - stingerea reciproca a creantelor si datoriilor fata de acelasi partener. Motor PUR.

Cand un partener e simultan CLIENT (creanta, sold debitor 4111) si FURNIZOR (datorie, sold creditor 401),
creantele si datoriile reciproce se sting prin compensare pana la concurenta celei mai mici (Cod civil art.1616).
Inregistrarea contabila: 401 = 4111 pentru suma compensata (se sting simultan datoria si creanta).

TEMEI (verificat verbatim in corpus, anaf_surse/):
- Cod civil (Legea 287/2009) art.1616-1623 (cod_civil_287_2009_art_1616_1623_compensare.txt):
  * art.1616: "Datoriile reciproce se sting prin compensatie pana la concurenta celei mai mici dintre ele"
    -> suma compensabila = min(creanta, datorie).
  * art.1617: compensatia opereaza de plin drept intre doua datorii CERTE, LICHIDE si EXIGIBILE -> preconditii
    de FOND, confirmate de contabil (nu se pot deduce din solduri); vezi PRECONDITII_ART1617.
  * art.1618: EXCLUDERI (creanta dintr-un act facut cu intentia de a pagubi; restituire depozit/comodat; bun
    insesizabil) -> vezi EXCLUDERI_ART1618.
- OMFP 1802/2014 pct.56 (omfp_1802_2014.txt):
  * alin.(1) principiul necompensarii: in SITUATIILE FINANCIARE nu se compenseaza active cu datorii;
  * alin.(3): "Eventualele compensari intre creante si datorii fata de aceeasi entitate efectuate cu
    respectarea prevederilor legale pot fi inregistrate numai DUPA contabilizarea creantelor si veniturilor,
    respectiv a datoriilor si cheltuielilor corespunzatoare" + "in notele explicative se prezinta VALOAREA
    BRUTA a creantelor si datoriilor care au facut obiectul compensarii" -> nota pastreaza valorile BRUTE +
    resturile, nu doar netul; compensarea se face DUPA ce ambele au fost contabilizate.
- Compensarea prin SISTEMUL INFORMATIC DE COMPENSARE (SIC), gestionat de CPPI Busteni, se aplica facturilor
  restante MAI VECHI DE 30 DE ZILE (de la emitere sau scadenta) ale persoanelor juridice cu capital de stat -
  HG 773/2019, Norme metodologice Art.1-2 (hg_773_2019_norme_monitorizare_datorii_nerambursate.txt; baza OUG
  77/1999). HG 773/2019 confirma regula min: Art.3(a) "compensare = stingerea obligatiilor... pana la concurenta
  obligatiei celei mai mici, prin ordine de compensare". NU EXISTA prag VALORIC in lei in actul in vigoare -
  pragul de ~10.000 lei (100 mil ROL) apartinea HG 685/1999, ABROGAT de HG 773/2019. Vezi necesita_sistem_electronic().
"""
from decimal import Decimal, ROUND_HALF_UP

B = Decimal("0.01")
CONT_CLIENT = "4111"      # creanta fata de tert (sold debitor)
CONT_FURNIZOR = "401"     # datorie fata de tert (sold creditor)

# Preconditii de fond ale compensarii legale (Cod civil art.1617) - le confirma contabilul, nu se deduc din solduri.
PRECONDITII_ART1617 = ("certe", "lichide", "exigibile")
# Cazuri in care compensatia este EXCLUSA (Cod civil art.1618).
EXCLUDERI_ART1618 = ("creanta dintr-un act facut cu intentia de a pagubi",
                     "datorie de restituire a bunului dat in depozit sau comodat",
                     "obiect: un bun insesizabil")


def _d(x):
    return Decimal(str(x or 0)).quantize(B, rounding=ROUND_HALF_UP)


def suma_compensabila(creanta, datorie):
    """Suma care se stinge prin compensare = min(creanta, datorie) (Cod civil art.1616). Ambele nenegative."""
    c, d = _d(creanta), _d(datorie)
    if c < 0 or d < 0:
        raise ValueError("Creanta si datoria trebuie sa fie sume pozitive.")
    return min(c, d)


def nota_compensare(creanta, datorie):
    """Nota contabila de compensare cu un tert: 401 = 4111 pentru suma compensabila (Cod civil art.1616;
    OMFP 1802 pct.56 alin.3). Pastreaza valorile BRUTE si resturile - valoarea bruta se prezinta in notele
    explicative (OMFP 1802 pct.56 alin.3). Compensarea presupune ca ambele au fost DEJA contabilizate."""
    c, d = _d(creanta), _d(datorie)
    comp = suma_compensabila(c, d)
    if comp <= 0:
        raise ValueError("Nu exista compensare: e nevoie de creanta SI de datorie fata de acelasi partener.")
    return {
        "linii": [(CONT_FURNIZOR, CONT_CLIENT, comp)],   # 401 = 4111
        "compensat": comp,
        "brut_creanta": c, "brut_datorie": d,
        "rest_creanta": (c - comp).quantize(B),
        "rest_datorie": (d - comp).quantize(B),
    }


PRAG_VECHIME_ZILE = 30   # HG 773/2019 Norme metodologice Art.2 alin.(1): facturi restante mai vechi de 30 de zile

def necesita_sistem_electronic(varsta_factura_zile=None, cu_capital_de_stat=True):
    """True daca compensarea intra in Sistemul Informatic de Compensare (SIC, gestionat de CPPI Busteni):
    factura restanta MAI VECHE DE 30 DE ZILE (PRAG_VECHIME_ZILE) de la emitere/scadenta, pentru persoane juridice
    cu capital de stat - HG 773/2019 Norme metodologice Art.1-2 (baza OUG 77/1999). Actul in vigoare NU prevede
    prag VALORIC in lei (cel de ~10.000 lei / 100 mil ROL era in HG 685/1999, ABROGAT de HG 773/2019). Fara
    varsta furnizata -> None (necunoscut)."""
    if varsta_factura_zile is None:
        return None
    return bool(cu_capital_de_stat) and int(varsta_factura_zile) > PRAG_VECHIME_ZILE


def propune_compensari(parteneri):
    """parteneri: iterabil de dict {cui, denumire, creanta, datorie, [varsta_factura_zile], [cu_capital_de_stat]}.
    Intoarce doar partenerii cu AMBELE solduri > 0 (compensare posibila), fiecare cu suma compensabila, nota si
    semnalul SIC (HG 773/2019: >30 zile + capital de stat). Fara varsta_factura_zile -> semnalul e None."""
    out = []
    for p in parteneri:
        c, d = _d(p.get("creanta")), _d(p.get("datorie"))
        if c > 0 and d > 0:
            n = nota_compensare(c, d)
            n["necesita_sistem_electronic"] = necesita_sistem_electronic(
                p.get("varsta_factura_zile"), p.get("cu_capital_de_stat", True))
            out.append({"cui": p.get("cui"), "denumire": p.get("denumire"), **n})
    return out


def pull(conn, schema):
    """Candidatii de compensare din solduri_parteneri: per partener (cui), creanta = suma sold_debitor pe
    conturile de client (411*), datorie = suma sold_creditor pe conturile de furnizor (401*)."""
    cand = {}
    with conn.cursor() as cur:
        cur.execute(f"SELECT cont, cui, denumire, sold_debitor, sold_creditor FROM {schema}.solduri_parteneri")
        for cont, cui, den, sd, sc in cur.fetchall():
            key = cui or ""
            r = cand.setdefault(key, {"cui": cui, "denumire": den or "",
                                      "creanta": Decimal("0"), "datorie": Decimal("0")})
            radacina = str(cont or "").split(".")[0]
            if radacina.startswith("411"):
                r["creanta"] += _d(sd)
            elif radacina.startswith("401"):
                r["datorie"] += _d(sc)
            if den and not r["denumire"]:
                r["denumire"] = den
    return propune_compensari(cand.values())
