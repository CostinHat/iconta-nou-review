# -*- coding: utf-8 -*-
"""Reconciliere bancară — matching linii extras pe facturi deschise.

Motor pur: nu atinge DB. Primește linii de extras (din banca_parser.parse_extras,
îmbogățite cu cui via banca.extrage_cui) și facturi deschise ca liste de dict.

Factură deschisă: {"id", "tert_cui", "directie" ('emisa'/'primita'),
                   "data_emitere" (date/str sortabil), "sold" (Decimal/float)}
Linie extras:     {"suma" (>0), "tip" ('incasare'/'plata'), "cui" (str|None),
                   "descriere", "data"}

Rezultat per linie: {"status": 'verde'|'galben'|'rosu',
                     "alocari": [{"factura_id", "suma"}],
                     "motiv": str}
verde  = match exact (o factură sau combinație cu sumă identică)
galben = alocare parțială / FIFO (necesită confirmare atentă)
rosu   = fără CUI sau fără facturi deschise ale partenerului
"""
from core import afirmatii as _af  # [P8] absenta spune UNDE s-a cautat
from core.unde import Unde as _Unde  # [P8] domeniul e LINIA, nu o luna
from decimal import Decimal
from itertools import combinations
import re

from core.common import cate as _cate
# [lotul 11, decizia Costin 10.3 pct.4, clasa „normalizare locală a CUI”] partenerul liniei de extras / al facturii = codul fiscal în
# forma păstrată (`cui_forma.stocare`). Înainte: `_norm_cui`, cu `.replace("RO", "")` — scotea „RO” de oriunde, iar spațiile din
# mijloc („185 47290”) rămâneau, deci același partener nu se mai potrivea.
from core import cui_forma as _forma_cui

TOLERANTA = Decimal("0.01")
MAX_COMBO = 4  # max facturi într-o combinație exactă


def _d(v):
    return v if isinstance(v, Decimal) else Decimal(str(v))


def facturi_partener(facturi_deschise, cui, tip):
    """Facturile deschise ale partenerului cu CUI dat, pe direcția potrivită tipului.
    incasare -> emise; plata -> primite. Sortate crescător după data_emitere (FIFO)."""
    cui = _forma_cui.stocare(cui)
    if not cui:
        return []
    directie = "emisa" if tip == "incasare" else "primita"
    rez = [f for f in facturi_deschise
           if _forma_cui.stocare(f.get("tert_cui")) == cui
           and f.get("directie") == directie
           and _d(f.get("sold", 0)) > TOLERANTA]
    return sorted(rez, key=lambda f: (str(f.get("data_emitere") or ""), f["id"]))


def _match_exact_una(suma, facturi):
    for f in facturi:
        if abs(_d(f["sold"]) - suma) <= TOLERANTA:
            return f
    return None


def _match_combo(suma, facturi):
    """Combinație de 2..MAX_COMBO facturi cu sumă exactă. Preferă seturile mai mici,
    apoi facturile mai vechi (facturi e deja FIFO)."""
    if len(facturi) > 12:  # limită anti-exploziv; peste, doar FIFO
        facturi = facturi[:12]
    for n in range(2, min(MAX_COMBO, len(facturi)) + 1):
        for combo in combinations(facturi, n):
            if abs(sum(_d(f["sold"]) for f in combo) - suma) <= TOLERANTA:
                return list(combo)
    return None


def _alocare_fifo(suma, facturi):
    """Alocă suma FIFO pe facturi; ultima poate fi parțială. Întoarce (alocari, rest)."""
    alocari, rest = [], suma
    for f in facturi:
        if rest <= TOLERANTA:
            break
        sold = _d(f["sold"])
        parte = min(sold, rest)
        alocari.append({"factura_id": f["id"], "suma": parte})
        rest -= parte
    return alocari, rest


def _directie(tip):
    return "emisa" if tip == "incasare" else "primita"


def numar_in_descriere(serie, numar, descriere):
    """PURĂ. [lotul 12, deficiența 480] Seria și numărul facturii („F1A 7”) scrise în descrierea liniei: seria, apoi numărul de ordine în
    serie (`pdf_util.numar_in_serie`), cu separatorii obișnuiți sau „nr.” între ele și zerourile din față permise — „factura F1A7”,
    „F1A-0007”, „fact. F1A nr. 7”. Numărul întreg, nu o bucată: „F1A77” / „F1A17” nu sunt F1A 7. Fără serie nu se caută (un „7” singur
    ar fi oricare număr din descriere)."""
    from core.pdf_util import numar_in_serie
    sr, n = str(serie or "").strip().upper(), numar_in_serie(serie, numar)
    if not sr or sr == "-" or n is None:
        return False
    tipar = r"(?<![0-9A-Z])" + re.escape(sr) + r"[\s\-/._]*(?:NR\.?\s*)?0*" + str(n) + r"(?![0-9])"
    return re.search(tipar, str(descriere or "").upper()) is not None


def facturi_dupa_numar(facturi_deschise, descriere, tip):
    """[480] Facturile deschise, pe direcția liniei, al căror număr (cu seria) e scris în descriere — FIFO."""
    rez = [f for f in facturi_deschise if f.get("directie") == _directie(tip) and _d(f.get("sold", 0)) > TOLERANTA
           and numar_in_descriere(f.get("serie"), f.get("numar"), descriere)]
    return sorted(rez, key=lambda f: (str(f.get("data_emitere") or ""), f["id"]))


def cod_partener_in_descriere(facturi_deschise, descriere, tip):
    """[480] Codul fiscal al unui partener cu facturi deschise pe direcția liniei, scris în descriere — și codul de TVA al unui partener
    din alt stat („DE136695976”), pe care `banca.extrage_cui` nu-l citește (caută numai „RO…” / „CUI …”). Codurile vin din facturi, nu
    dintr-o listă de formate; în descriere se caută ca un întreg (nu o bucată dintr-un cuvânt sau număr mai lung), cu spațiile din
    interiorul codului permise („DE 136695976”) și, la codul românesc, cu „RO” în față. Un singur partener găsit -> codul lui; niciunul
    sau mai mulți -> None."""
    text = str(descriere or "").upper()
    gasite = set()
    for f in facturi_deschise:
        c = _forma_cui.stocare(f.get("tert_cui"))
        if not c or len(c) < 6 or f.get("directie") != _directie(tip):
            continue
        cod = re.escape(c[0]) + "".join(r"\s?" + re.escape(ch) for ch in c[1:])
        if re.search(r"(?<![0-9A-Z])" + (r"(?:RO\s?)?" if c.isdigit() else "") + cod + r"(?![0-9A-Z])", text):
            gasite.add(c)
    return gasite.pop() if len(gasite) == 1 else None


def potriveste_linie(linie, facturi_deschise):
    """Matching pentru o linie de extras. Vezi docstring modul pentru contract.
    [lotul 12, deficiența 480] Când CUI-ul din descriere nu duce la nicio factură deschisă (sau lipsește), se caută întâi numărul facturii
    scris în descriere („factura F1A7”), apoi codul fiscal al unui partener cu facturi deschise (și codul de TVA al altui stat)."""
    suma = _d(linie.get("suma", 0)).copy_abs()
    cui = _forma_cui.stocare(linie.get("cui"))
    facturi = facturi_partener(facturi_deschise, cui, linie.get("tip")) if cui else []
    if not facturi:
        dupa_nr = facturi_dupa_numar(facturi_deschise, linie.get("descriere"), linie.get("tip"))
        if dupa_nr:
            from core.pdf_util import serie_nr
            et = ", ".join(serie_nr(f.get("serie"), f.get("numar")).replace(" nr. ", " ") for f in dupa_nr)
            return _pe_facturi(suma, dupa_nr, cui or "număr factură", "numărul facturii din descriere (%s)" % et)
        cod = cod_partener_in_descriere(facturi_deschise, linie.get("descriere"), linie.get("tip"))
        if cod:
            cui, facturi = cod, facturi_partener(facturi_deschise, cod, linie.get("tip"))
    if not cui:
        return dict(_af.afirmatie(
            "absenta_observatie", "reconciliere extras",
            "fără CUI în descriere",
            surse_consultate="descrierea liniei de extras (câmpul din care se extrage CUI-ul)"),
            status="rosu", alocari=[])

    if not facturi:
        return dict(_af.afirmatie(
            "absenta_observatie", "reconciliere extras",
            f"niciun document deschis pentru CUI {cui}",
            surse_consultate=f"documentele DESCHISE ale partenerului cu CUI {cui} "
                             f"(cele stinse nu se caută)"),
            status="rosu", alocari=[])

    f = _match_exact_una(suma, facturi)
    if f:
        return dict(_af.afirmatie(
            "fapt", "reconciliere extras", "potrivire exactă pe o factură",
            unde=_Unde("linie_extras", cui, "suma %s" % suma),
            temei_completitudine="documentele deschise ale partenerului, la suma exacta"),
            status="verde", alocari=[{"factura_id": f["id"], "suma": suma}])

    combo = _match_combo(suma, facturi)
    if combo:
        return dict(_af.afirmatie(
            "fapt", "reconciliere extras", f"potrivire exactă pe {_cate(len(combo), 'factură', 'facturi')}",
            unde=_Unde("linie_extras", cui, "suma %s" % suma),
            temei_completitudine="documentele deschise ale partenerului, pe combinație de solduri"),
            status="verde",
            alocari=[{"factura_id": f["id"], "suma": _d(f["sold"])} for f in combo])

    alocari, rest = _alocare_fifo(suma, facturi)
    if rest > TOLERANTA:
        return dict(_af.afirmatie(
            "fapt", "reconciliere extras",
            f"suma depășește soldul total; rest nealocat {rest}",
            unde=_Unde("linie_extras", cui, "suma %s" % suma),
            temei_completitudine="soldurile deschise ale partenerului, însumate"),
            status="galben", alocari=alocari)
    return dict(_af.afirmatie(
        "fapt", "reconciliere extras", "alocare parțială, pe facturile cele mai vechi întâi",
        unde=_Unde("linie_extras", cui, "suma %s" % suma),
        temei_completitudine="documentele deschise, alocate în ordinea vechimii (FIFO)"),
        status="galben", alocari=alocari)


def _pe_facturi(suma, facturi, cheie, dupa):
    """[480] Potrivirea pe facturile găsite după numărul din descriere: suma exactă (una sau o combinație) -> verde; altfel alocare pe
    ele, cele mai vechi întâi -> galben (de confirmat). `dupa` spune pe ce s-a găsit."""
    unde = _Unde("linie_extras", cheie, "suma %s" % suma)
    f = _match_exact_una(suma, facturi)
    combo = None if f else _match_combo(suma, facturi)
    if f or combo:
        return dict(_af.afirmatie("fapt", "reconciliere extras", "potrivire după %s" % dupa, unde=unde,
                                  temei_completitudine="facturile deschise numite în descrierea liniei, la suma exactă"),
                    status="verde", alocari=[{"factura_id": f["id"], "suma": suma}] if f
                    else [{"factura_id": x["id"], "suma": _d(x["sold"])} for x in combo])
    alocari, rest = _alocare_fifo(suma, facturi)
    text = ("%s; suma depășește soldul; rest nealocat %s" % (dupa, rest)) if rest > TOLERANTA else \
        ("%s; suma nu e soldul facturii: alocare parțială, de confirmat" % dupa)
    return dict(_af.afirmatie("fapt", "reconciliere extras", text, unde=unde,
                              temei_completitudine="facturile deschise numite în descrierea liniei, alocate în ordinea vechimii"),
                status="galben", alocari=alocari)


def potriveste_extras(linii, facturi_deschise):
    """Matching pentru toate liniile. Soldurile se consumă secvențial:
    o factură alocată integral la linia N nu mai e disponibilă la linia N+1."""
    solduri = {f["id"]: _d(f["sold"]) for f in facturi_deschise}
    rezultate = []
    for linie in linii:
        disponibile = [dict(f, sold=solduri[f["id"]])
                       for f in facturi_deschise if solduri[f["id"]] > TOLERANTA]
        rez = potriveste_linie(linie, disponibile)
        for a in rez["alocari"]:
            solduri[a["factura_id"]] -= _d(a["suma"])
        rezultate.append(rez)
    return rezultate
