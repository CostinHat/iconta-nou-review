"""
core/facturi.py — contare facturi + TVA + storno. Calcul PUR, fără DB.
Construit de la zero din OMFP 1802/2014 + Cod fiscal (TVA, taxare inversă art. 331).

Conturi:
  emisă:   4111 Clienți ; 4427 TVA colectată ; venituri 701/703/704/707
  primită: 401 Furnizori ; 4426 TVA deductibilă ; 301/302/371/6xx
  taxare inversă: 4426 = 4427 (autocolectare la beneficiar)
"""
from __future__ import annotations
from decimal import Decimal

from core import common as c
from core.common import _dec, _q

REGULI = "2026.1"
MODUL = "facturi"

VENIT = {            # tip -> cont de venit (factură emisă)
    "marfa": "707",
    "produse": "701",
    "servicii": "704",
    "prestari": "704",
    "reziduale": "703",
}
ACHIZITIE = {        # tip -> cont (factură primită)
    "marfa": "371",
    "materii_prime": "301",
    "materiale": "302",
    "obiecte_inventar": "303",
    "imobilizare": "213",
}


# ── FACTURA EMISĂ PE BAZA BONULUI FISCAL (decizia Costin A, 02.10.2026) ──────────────────────────────────────────
# HG 1/2016 pct.97 alin.(1): „Pe facturile emise și achitate pe bază de bonuri fiscale … fiind suficientă mențiunea
# «conform bon fiscal nr./data»”. Vânzarea e deja în raportul Z al zilei bonului, deci factura NU e o vânzare nouă: nu
# intră în D300, nu se mai scrie notă de vânzare, nu descarcă stocul, iar în D394 rămâne în op1 (are partener) dar suma ei
# se scade din op2 Î1 („cu excepția celor pentru care s-au emis facturi”, OPANAF 2194/2025 lit.G). DEFINIȚIA E AICI, o dată.
def e_din_bon_fiscal(f):
    """Factura (dict cu `directie`, `bon_fiscal_nr`) e emisă pe baza unui bon fiscal."""
    return (f.get("directie") or "emisa") == "emisa" and bool(str(f.get("bon_fiscal_nr") or "").strip())


# ── FACTURA PRIMITĂ CU TAXARE INVERSĂ: TOTALUL DE PLATĂ (lotul 13, deficiența 546) ───────────────────────────────────
# CF art.331 alin.(3): „Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2) furnizorii/prestatorii
# nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în decontul prevăzut la art. 323,
# atât ca taxă colectată, cât și ca taxă deductibilă.” Pe factura primită cu taxare inversă, antetul păstrează TVA-ul determinat de
# beneficiar (`tva`, scris odată cu nota 4426 = 4427 și citit de D300 / D394 / D406), dar datoria către furnizor e numai baza: nota e
# `<cont> = 401 baza`. O SINGURĂ definiție a „totalului de plată”: starea de plată, scadențarul, potrivirea plății, ecranul.
def fara_tva_de_plata(f):
    """Factura (dict cu `directie`, `taxare_inversa`) e primită cu taxare inversă: TVA-ul de pe antet nu se plătește furnizorului."""
    return (f.get("directie") or "") == "primita" and bool(f.get("taxare_inversa"))


def total_de_plata(f, total, tva):
    """Totalul de plată al facturii (în moneda lui `total`): `total - tva` la factura primită cu taxare inversă, altfel `total`."""
    t = _dec(total or 0)
    return t - _dec(tva or 0) if fara_tva_de_plata(f) else t


#: aceeași definiție, în SQL, în LEI, pe factura cu aliasul `{a}` (cititorii care adună datorii / creanțe în lei)
SQL_TOTAL_DE_PLATA_LEI = ("(COALESCE({a}.total_lei, {a}.total) - CASE WHEN {a}.directie = 'primita' AND COALESCE({a}.taxare_inversa, false) "
                          "THEN COALESCE({a}.tva_lei, {a}.tva, 0) ELSE 0 END)")


#: [lotul 13, decizia sesiunii principale 26.10.2026 pe întrebarea UM — CLAUDE.md §8 + DS cap.6 v2.104, 504: „nimic precompletat care induce
#: în eroare”] UM-ul gol NU devine „buc” pe ascuns: se refuză lângă câmp, cu această propoziție, în toate locurile care scriu o linie nouă
#: (emiterea, factura primită introdusă de mână, articolul nou din borderou) — o singură regulă, server + ecran.
MESAJ_UM_LIPSA = "Alege unitatea de măsură a liniei."


def um_linie(linie, um_articol=None):
    """UM-ul liniei, după regula unică: cel scris pe linie; gol, pe o linie cu articol din nomenclator (`articol_id`) -> UM-ul articolului
    (vizibil pe linie, ecranul îl pune la alegerea articolului); altfel None = de refuzat. Niciodată „buc” din oficiu."""
    um = str((linie or {}).get("um") or "").strip()
    if um:
        return um
    if (linie or {}).get("articol_id") and str(um_articol or "").strip():
        return str(um_articol).strip()
    return None


def um_lipsa(linii, um_articole=None, prefix="em-l", de_la=0):
    """[(camp, mesaj)] pentru fiecare linie fără UM (`um_linie`); pe celelalte pune UM-ul ales (al articolului, când linia îl ia de acolo).
    `um_articole` = {articol_id: um}; câmpul = `{prefix}{i}-um`, cu i numărat de la `de_la` (emiterea: 0, factura de mână: 1)."""
    out = []
    for i, l in enumerate(linii, de_la):
        um = um_linie(l, (um_articole or {}).get(l.get("articol_id")))
        if um:
            l["um"] = um
        else:
            out.append(("%s%d-um" % (prefix, i), MESAJ_UM_LIPSA))
    return out


def clauza_nu_din_bon(alias="f"):
    """Predicatul SQL al aceleiași definiții, pentru repository-urile care numără vânzările (D300 și calea a doua)."""
    return ("%s.bon_fiscal_nr IS NULL" % alias) if alias else "bon_fiscal_nr IS NULL"


def clauza_din_bon(alias="f"):
    """Predicatul SQL complementar: factura EMISĂ și marcată (D394 op2 Î1 o scade din luna bonului)."""
    a = (alias + ".") if alias else ""
    return "%sdirectie = 'emisa' AND %sbon_fiscal_nr IS NOT NULL" % (a, a)


def mentiune_bon(f):
    """Mențiunea de pe factură (HG 1/2016 pct.97 alin.(1)): „conform bon fiscal nr./data”."""
    from core.pdf_util import data_ro
    return "conform bon fiscal nr. %s/%s" % (str(f.get("bon_fiscal_nr")).strip(), data_ro(f.get("bon_fiscal_data")))



def mentiune_storno(f):
    """[deficiența 417, retestul Costin 19.10.2026, PRIORITAR] Trimiterea facturii de stornare la factura stornată: „Stornare factura F1A
    nr. 8 din 19.10.2026”; None pe o factură care nu stornează. Temei: CF art.330 alin.(1) lit.b): „[...] se emite o factură cu valorile
    cu semnul minus [...] în care se înscriu numărul și data facturii corectate”; CF art.319 alin.(20) lit.r): „o referire la alte
    facturi sau documente emise anterior, atunci când se emit mai multe facturi ori documente pentru aceeași operațiune”."""
    o = f.get("storno_din")
    if not o:
        return None
    from core.pdf_util import data_ro
    from core.pdf_util import serie_nr   # [lotul 11, 443] o singură regulă pentru seria și numărul („F1A nr. 8”)
    return "Stornare factura %s din %s" % (serie_nr(o.get("serie"), o.get("numar")), data_ro(str(o.get("data_emitere"))[:10]))


_RADACINI_VENIT = (            # radacina in denumire -> tip (OMFP 1802/2014)
    ("marf", "marfa"),         # marfa (bunuri spre revanzare) -> 707
    ("produs", "produse"),     # produse finite -> 701
    ("servici", "servicii"),   # servicii/prestari -> 704
    ("prestar", "servicii"),
    ("rezidual", "reziduale"), # produse reziduale -> 703
)


def tip_din_denumire(denumire):
    """Clasifica DETERMINIST contul de venit din denumirea liniei, fara AI.
    Intoarce o cheie din VENIT (marfa/produse/servicii/reziduale) sau None cand
    denumirea nu se incadreaza CLAR: zero potriviri, SAU mai multe tipuri deodata
    (ex. "Produs marfa" = produse+marfa) = ambiguu. None inseamna "nu pot decide",
    nu un default (apelantul incearca AI, apoi blocheaza)."""
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFKD", (denumire or "").lower())
                if not unicodedata.combining(c))
    gasite = {tip for rad, tip in _RADACINI_VENIT if rad in t}
    return gasite.pop() if len(gasite) == 1 else None


def _nota(debit, credit, suma, temei=None):
    n = {"debit": debit, "credit": credit, "suma": _q(suma),
         "modul": MODUL, "reguli": REGULI}
    if temei:
        n["temei"] = temei
    return n


# ============================================================
#  TVA pe cotă (cu dată de valabilitate)
# ============================================================
def calcul_tva(baza, cota=None, la_data=None):
    """
    Întoarce {tva, cota, temei}. Dacă `cota` lipsește, ia cota standard din common
    valabilă la `la_data` (prinde 19 vs 21 după perioadă).
    """
    if cota is None:
        cota, temei = c.cota("tva_standard", la_data)
    else:
        cota, temei = _dec(cota), "cotă specificată (redusă/scutită)"
    return {"tva": _q(_dec(baza) * cota), "cota": cota, "temei": temei}


# ============================================================
#  FACTURĂ EMISĂ (vânzare)
# ============================================================
def factura_emisa(baza, tip="marfa", cota=None, la_data=None, cont_venit=None, tva_incasare=False):
    """4111 = venit (bază) ; 4111 = 4427 (TVA)."""
    cont = cont_venit or VENIT[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota("4111", cont, baza)]
    if t["tva"]:
        note.append(_nota("4111", "4428" if tva_incasare else "4427", t["tva"], temei=t["temei"]))
    return note


# ============================================================
#  FACTURĂ PRIMITĂ (achiziție)
# ============================================================
def factura_primita(baza, tip="marfa", cota=None, la_data=None, cont=None, tva_incasare=False):
    """cont = 401 (bază) ; 4426 = 401 (TVA)."""
    c_ach = cont or ACHIZITIE[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota(c_ach, "401", baza)]
    if t["tva"]:
        note.append(_nota("4428" if tva_incasare else "4426", "401", t["tva"], temei=t["temei"]))
    return note


# ============================================================
#  TAXARE INVERSĂ (art. 331 Cod fiscal)
# ============================================================
def taxare_inversa(baza, tip="marfa", cota=None, la_data=None, cont=None):
    """
    La beneficiar: cont = 401 (bază, fără TVA pe 401) ; 4426 = 4427 (autocolectare).
    Nu se plătește TVA efectiv către furnizor.
    """
    c_ach = cont or ACHIZITIE[tip]
    t = calcul_tva(baza, cota, la_data)
    note = [_nota(c_ach, "401", baza)]
    if t["tva"]:
        note.append(_nota("4426", "4427", t["tva"],
                          temei="Cod fiscal art. 331 — taxare inversă"))
    return note


# ============================================================
#  STORNO (corecție în roșu — sume negative)
# ============================================================
def storno(note):
    """Întoarce aceleași note cu sume negative (corecție în același exercițiu, pct. 330)."""
    return [{**n, "suma": _q(-_dec(n["suma"])), "storno": True} for n in note]
