"""
Modul D390 — Declarație recapitulativă VIES privind livrările/achizițiile/
prestările intracomunitare (ANAF v3, OPANAF 705/11.03.2020, MO 217/17.03.2020).
Statut temei verificat la MO 04.08.2026: OPANAF 705/2020 IN VIGOARE - nu s-a gasit abrogare sau ordin
de inlocuire (2021-2026); nomenclatoarele TARI_UE/TIPURI confirmate separat pe validatorul instalat D390_11.

REFĂCUT DE LA ZERO după ANAF structura D390 2020_180320 (structura_D390_2020_180320).

Separare strictă:
  - CALCUL PUR : calcul_d390(prof, an, luna, facturi, manual=None) -> Rezultat
  - VALIDARE   : valideaza(rezultat) -> listă erori
  - XML        : build_xml(rezultat) -> str
  - CITIRE DB  : pull(conn, schema, an, luna) -> (prof, facturi)
  - ORCHESTRARE: genereaza(conn, schema, an, luna) -> (xml, rezultat)

Tipuri operațiune (oficial):
  L = livrări intracomunitare de bunuri
  T = livrări în cadrul unei operațiuni triunghiulare
  A = achiziții intracomunitare de bunuri
  P = prestări intracomunitare de servicii
  S = achiziții intracomunitare de servicii
  R = livrări intracomunitare de bunuri în regim special pentru agricultori

Mapare automată din facturi: emisă->L (bunuri), primită->A (bunuri).
Serviciile (P/S) și triangulația (T/R) = clasificare manuală de contabil (prin `manual`).

totalPlata_A = nrOPI + bazaL + bazaT + bazaA + bazaP + bazaS + bazaR (formula oficială).
"""

from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
import re
import datetime
from core import common as c
from core import d390_reconciliere as _recon  # POARTA a-doua-cale (recalcul independent sursa->declaratie)
from core.identitate import valideaza_cui as _valideaza_cui  # T1: checksum CUI RO (partener/firma), sursa canonica (read-only)
from dataclasses import dataclass, field
from decimal import Decimal

NS = "mfp:anaf:dgti:d390:declaratie:v3"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
# CUI UE: prefix 2 litere + cod
_CUI_UE = re.compile(r"^([A-Z]{2})([0-9A-Z]+)$")

# Nomenclator oficial țări (cod TVA = cod ISO în XML). Croația = HR (NU CR - vezi mai jos).
TARI_UE = {
    "AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
    "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK",
    "ES", "SE", "HU", "XI",  # XI = Irlanda de Nord (post-Brexit, VIES)
}
# Codurile de țară în XML = prefixul de TVA (identic cu ISO). NU există remapare: maparea HR->CR
# (crezută corectă până la 03.08.2026) era GREȘITĂ - probă DUK: tara="CR" e respinsă ("nu se află în
# lista"), tara="HR" e acceptată. Nomenclatorul ANAF D390 folosește HR pentru Croația. Gard:
# test_croatia_emite_HR_nu_CR + test_croatia_HR_trece_duk.
_TARA_XML = {}

# TIPURI + TARI_UE: nomenclatoare confirmate pe VALIDATORUL instalat D390_11 (proba DUK boundary
# 04.08.2026), nu doar pe pdf-ul de structura 2020 (INVECHIT). Fiecare tip valid / fiecare tara aplica
# algoritmul R24.1; niciun cod mort, niciun gap. Pazit de test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020.
TIPURI = ("L", "T", "A", "P", "S", "R")

# Tipurile legale per DIRECTIE (OPANAF 705/2020: L/T/P/R = latura de livrare/prestare; A/S = latura de
# achizitie). Sursa UNICA a regulii de tranzitie - importata si de d390_clasificare_api (write-side).
TIPURI_DIRECTIE = {"emisa": ("L", "T", "P", "R"), "primita": ("A", "S")}


def _reclasificare_tip(directie, tara, cod, recl, tip_def):
    """Tipul reclasificat al unei operatiuni auto, VALIDAT contra directiei - la fel ca la scriere
    (salveaza_reclasificare). Un override care nu e legal pentru directie (achizitia nu poate deveni
    livrare si invers, DECIZII 21.07) RIDICA eroare vizibila, NU revine tacit la default: o revenire
    tacuta ar fi misclasificare (intentia contabilului - ex. P - inlocuita tacut cu L). Acelasi
    principiu ca gardul liniilor manuale (tip introdus de contabil, invalid -> eroare, nu disparitie
    /schimbare tacuta). Pe date valide (scrierea valideaza deja) nu se schimba nimic."""
    tip = recl.get((directie, tara, cod), tip_def)
    if tip != tip_def and tip not in TIPURI_DIRECTIE.get(directie, ()):
        raise ValueError(
            "D390: reclasificare cu tip %r nepermis pentru direcția %s (permise: %s). Un tip din "
            "d390_reclasificare nelegal pentru direcție trebuie să producă eroare vizibilă, nu să "
            "revina tacit la %r (misclasificare)."
            % (tip, directie, "/".join(TIPURI_DIRECTIE.get(directie, ())), tip_def))
    return tip


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    """Baza D390 in lei intregi, rotunjire ARITMETICA (half-up).

    27.07.2026 - trecut de la `round()` (BANCARA) la ROUND_HALF_UP. Rationament:
      (a) VERIFICAT LA SURSA: OPANAF 705/2020 si instructiunile de completare NU prevad o
          regula de rotunjire pentru D390 - deci nu se interzice cea aritmetica;
      (b) CONSECVENTA: d390 era SINGURUL din cele 10 generatoare cu rotunjire bancara;
          d112/d300/d406/d710/d100/d101/d205 folosesc toate ROUND_HALF_UP;
      (c) RISC ASIMETRIC: la D112 ANAF cere EXPLICIT rotunjire aritmetica si a RESPINS-o pe
          cea bancara prin validator (DUK regula A91b, CAM 112 cerut 113). Daca aceeasi asteptare
          exista si la D390, bancara produce declaratii gresite; invers, aritmetica nu strica
          nimic - nicio sursa n-o interzice.
    Diferenta apare doar la .5 exact (112.5: bancar 112, aritmetic 113). Pe datele actuale
    nu se manifesta (toate bazele sunt rotunde), dar asta e noroc, nu garantie.

    MASCA SCOASA 27.07.2026: numar_fiscal ridica pe valoare invalida (vezi core/numere.py).
    """
    from decimal import Decimal, ROUND_HALF_UP
    from core.numere import numar_fiscal
    return int(numar_fiscal(x, "D390").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _tara_xml(t):
    return _TARA_XML.get(t, t)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    ops: dict = field(default_factory=dict)        # (tip,tara,cod,den) -> baza int
    rezumat: dict = field(default_factory=dict)    # {L,T,A,P,S,R: int}
    nr_opi: int = 0
    total_baza: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)
    diag: list = field(default_factory=list)        # probleme per-partener (T1/T3): checksum/prefix/tara/codO_lung


# ── VIES checksum OFFLINE (T1/T3) — subset ANCORAT pe DUK boundary 10.08.2026 ─────────────────────
# DECIZIE (Costin): reimplementarea COMPLETA a celor 27 de algoritmi VIES e DEFERATA. Biblioteca
# oficiala (vatalgo) e IN jar-ul DUK; nu e expusa ca API offline apelabil din Python (DUK valideaza
# doar declaratia intreaga, lent, deci NU pre-emit per-partener). Reimplementarea integrala ar risca
# DIVERGENTA fata de autoritatea care valideaza la depunere (aceeasi lectie ca D101 R17: codul urmeaza
# validatorul, nu invers). Se implementeaza DOAR algoritmii VERIFICATI contra valorilor pe care DUK-ul
# INSTALAT le accepta (DE 136695976, FR 40303265045, HR OIB) - proba boundary 10.08.2026:
#   DE/HR = ISO/IEC 7064 MOD 11,10 ; FR = cheia SIREN (12 + 3*SIREN) mod 97.
# Pentru restul tarilor checksum-ul ramane "neverificat offline" (structura DA, cifra de control o lasa
# pe DUK) - fara fals-pozitiv pe tari neimplementate. Scop: partenerul cu VAT checksum-invalid sa fie
# NUMIT pre-emit (nu descoperit abia din DUK regula R24.1 brut). Gard: test_d390_vies_checksum.
def _vies_mod1110(corp):
    """ISO/IEC 7064 MOD 11,10 -> cifra de control (DE 9 cifre / HR OIB 11 cifre)."""
    p = 10
    for ch in corp:
        x = (int(ch) + p) % 10
        if x == 0:
            x = 10
        p = (x * 2) % 11
    return (11 - p) % 10


def checksum_vies(tara, cod):
    """(stare, motiv): stare in {ok, invalid, neverificat}. Doar algoritmii verificati pe DUK instalat."""
    cod = (cod or "").upper()
    if tara in ("DE", "HR"):
        n = 9 if tara == "DE" else 11
        if not (cod.isdigit() and len(cod) == n):
            return "invalid", "format %s cere %d cifre (are %r)" % (tara, n, cod)
        return ("ok", "ok") if _vies_mod1110(cod[:-1]) == int(cod[-1]) else ("invalid", "cifra de control (MOD 11,10)")
    if tara == "FR":
        if len(cod) == 11 and cod[:2].isdigit() and cod[2:].isdigit():
            key = (12 + 3 * (int(cod[2:]) % 97)) % 97
            return ("ok", "ok") if key == int(cod[:2]) else ("invalid", "cheia FR (SIREN) greșită")
        return "neverificat", "format FR neabordat offline - verificat de DUK"
    return "neverificat", "algoritm %s neimplementat offline - verificat de DUK" % tara


def _clasifica_partener(raw):
    """CUI-ul brut al unui partener -> (categorie, tara, cod, motiv). NU ridica (calcul PUR).
    categorie: ic (intracomunitar valid) | domestic (RO/fara CUI, exclus corect) |
               prefix (fara prefix de tara UE valid, SUSPECT) | tara (prefix ne-UE, mistypat)."""
    raw = (raw or "").strip().upper().replace(" ", "").replace("-", "")
    if not raw:
        return "domestic", None, "", "fără CUI (partener intern/persoana fizica)"
    m = _CUI_UE.match(raw)
    if not m:
        # fara prefix de 2 litere: CUI RO valid -> intern (exclus corect); altfel SUSPECT (prefix lipsa)
        if _valideaza_cui(raw)[0]:
            return "domestic", "RO", raw, "CUI RO valid (operațiune interna)"
        return "prefix", None, raw, "CUI fără prefix de țară UE valid (prefix țară lipsă/invalid)"
    tara, cod = m.group(1), m.group(2)
    if tara == "RO":
        return "domestic", "RO", cod, "partener RO (operațiune interna)"
    if tara not in TARI_UE:
        sug = {"CR": "HR (Croatia)", "GR": "EL (Grecia)"}.get(tara)
        motiv = "țară %r nu e în nomenclatorul UE" % tara + ((" (ai vrut %s?)" % sug) if sug else "")
        return "tara", tara, cod, motiv
    return "ic", tara, cod, "ok"


def _facturi_ic(facturi):
    """Facturile INTRACOMUNITARE valide -> (out, diag). out = [{directie, tara, cod, den, baza}]
    (latura auto, FARA tip inca). diag = probleme per-partener (domestic/prefix/tara/checksum/codO_lung).
    NU ridica - calcul PUR (control_incrucisat cheama calculeaza); blocarea o face genereaza via valideaza.
    Sursa unica a filtrului IC - folosit si de calcul_d390 si de operatiuni_auto (fara dublura)."""
    out, diag = [], []
    for f in facturi:
        cat, tara, cod, motiv = _clasifica_partener(f.get("cui"))
        den = (f.get("nume") or "")
        baza = Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0))
        info = {"categorie": cat, "den": den, "cui": (f.get("cui") or ""),
                "directie": f.get("directie"), "tara": tara, "cod": cod, "baza": baza, "motiv": motiv}
        if cat != "ic":
            diag.append(info)                        # domestic/prefix/tara -> NU intra in declaratie
            continue
        if len(cod) > 12:                            # T6: NU trunchia codO (trunchierea CORUPE VAT-ul)
            diag.append(dict(info, categorie="codO_lung",
                             motiv="codO are %d caractere (max 12) - trunchierea ar CORUPE numărul de TVA" % len(cod)))
        else:
            st, mo = checksum_vies(tara, cod)
            if st == "invalid":
                diag.append(dict(info, categorie="checksum",
                                 motiv="cod TVA %s%s invalid: %s (va fi respins de DUK regula R24.1)" % (tara, cod, mo)))
        out.append({"directie": f.get("directie"), "tara": tara, "cod": cod,
                    "den": den[:200], "baza": baza})
    return out, diag


def operatiuni_auto(facturi, reclasificari=None):
    """[F125] Pentru UI: operațiunile auto-derivate din facturi, agregate pe (directie, tara, cod,
    den), cu tipul curent (default L/A sau reclasificat). Contabilul le vede și le reclasifică."""
    recl = reclasificari or {}
    ic, _diag = _facturi_ic(facturi)
    agg = {}
    for o in ic:
        k = (o["directie"], o["tara"], o["cod"], o["den"])
        agg[k] = agg.get(k, Decimal("0")) + o["baza"]
    out = []
    for (directie, tara, cod, den), b in agg.items():
        tip_def = "L" if directie == "emisa" else "A"
        out.append({"directie": directie, "tara": tara, "cod": cod, "den": den,
                    "baza": _int(b), "tip_default": tip_def,
                    "tip_curent": _reclasificare_tip(directie, tara, cod, recl, tip_def)})
    return sorted(out, key=lambda x: (x["directie"], x["tara"], x["cod"]))


def calcul_d390(prof, an, luna, facturi, manual=None, reclasificari=None):
    """Calcul PUR. facturi: dict cu cui, nume, directie, total, tva.
    manual: listă opțională de dict-uri {tip, tara, cod, den, baza} introduse de contabil
            (linii pur manuale, fără factură în sistem).
    reclasificari: dict {(directie, tara, cod): tip} — override-ul tipului unei operațiuni
            auto-derivate (emisă implicit L, primită implicit A). RECLASIFICĂ, nu adaugă →
            fără dublă numărare a facturilor de servicii (F125). Vezi DECIZII 21.07."""
    ops = {}
    recl = reclasificari or {}
    ic, diag = _facturi_ic(facturi)
    for o in ic:
        tip_def = "L" if o["directie"] == "emisa" else "A"       # implicit: bunuri
        # override contabil, VALIDAT contra directiei (ca la scriere); invalid -> eroare, nu fallback tacit
        tip = _reclasificare_tip(o["directie"], o["tara"], o["cod"], recl, tip_def)
        k = (tip, o["tara"], o["cod"], o["den"])
        ops[k] = ops.get(k, Decimal("0")) + o["baza"]

    # operațiuni manuale (P/S/T/R)
    for op in (manual or []):
        tip = op.get("tip")
        if tip not in TIPURI:
            # [GARD CLASA] operatiune manuala a contabilului cu tip gresit -> eroare vizibila, nu drop tacit.
            raise ValueError("D390: operațiune manuală cu tip necunoscut %r (acceptate: %s). Un tip introdus "
                             "de contabil care nu e în lista trebuie să producă eroare vizibilă, nu să dispară "
                             "tacut din declarație." % (tip, ", ".join(map(str, TIPURI))))
        tara = (op.get("tara") or "").upper()
        cod = (op.get("cod") or "")            # T6: NU mai trunchia la 12 - ar CORUPE numarul de TVA
        den = (op.get("den") or "")[:200]
        baza_op = Decimal(str(op.get("baza") or 0))
        if len(cod) > 12:
            diag.append({"categorie": "codO_lung", "den": den, "cui": (tara + cod),
                         "directie": "manual", "tara": tara, "cod": cod, "baza": baza_op,
                         "motiv": "codO manual are %d caractere (max 12) - trunchierea ar CORUPE numărul de TVA" % len(cod)})
        k = (tip, tara, cod, den)
        ops[k] = ops.get(k, Decimal("0")) + baza_op

    # ROTUNJIRE COERENTA (10.08.2026, probat DUK R16): rezumatul (bazaL..bazaR, total_baza) =
    # suma bazelor ROTUNJITE PE OPERATIE (exact valorile emise in <operatie baza=...>), NU
    # rotunjirea sumei brute Decimal. Validatorul recalculeaza R16: bazaL = Suma(baza pt tip=L)
    # peste operatiile (deja intregi) din XML; daca rezumatul rotunjeste suma bruta iar operatiile
    # se rotunjesc individual, cele doua diverg la baze fractionare (2x 1000.50 -> operatii
    # 1001+1001=2002, dar _int(2001.00)=2001 -> R16 respins). Gard: test_d390_rotunjire_coerenta.
    ops_int = {k: _int(v) for k, v in ops.items()}
    bz = {t: 0 for t in TIPURI}
    for (tip, _, _, _), b in ops_int.items():
        bz[tip] += b
    nr_opi = len(ops_int)
    tot = sum(bz.values())
    # formula oficială totalPlata_A
    total_plata = nr_opi + bz["L"] + bz["T"] + bz["A"] + bz["P"] + bz["S"] + bz["R"]
    res = Rezultat(an=an, luna=luna, prof=prof, ops=ops_int, rezumat=bz,
                   nr_opi=nr_opi, total_baza=tot, total_plata_a=total_plata)
    res.diag = diag
    # T1/T3: NU mai agregam intr-un count anonim. Domesticele (RO/fara CUI) = exclusie legitima, sumar
    # scurt; ORICE partener problematic (prefix mistypat, tara ne-UE, checksum invalid, codO>12) e NUMIT
    # per-partener (denumire + CUI + factura + motiv). Principiu Costin: utilizatorul afla CARE si DE CE,
    # nu declaratia se subtiaza tacit.
    _domestic = [d for d in diag if d["categorie"] == "domestic"]
    if _domestic:
        res.avertismente.append("%d facturi cu parteneri interni (RO)/fără CUI - excluse (D390 e doar intracomunitar)." % len(_domestic))
    for d in diag:
        _id = "%s (CUI %r, factura %s)" % (d["den"] or "(fără denumire)", d["cui"], d["directie"] or "-")
        if d["categorie"] == "prefix":
            res.avertismente.append("Partener EXCLUS - %s: %s. Verifică prefixul de țară (ex. DE/FR/IT)." % (_id, d["motiv"]))
        elif d["categorie"] == "tara":
            res.avertismente.append("Partener EXCLUS (țară mistypata) - %s: %s." % (_id, d["motiv"]))
        elif d["categorie"] == "checksum":
            res.avertismente.append("ATENTIE cod TVA invalid - %s: %s." % (_id, d["motiv"]))
        elif d["categorie"] == "codO_lung":
            res.avertismente.append("codO prea lung - %s: %s." % (_id, d["motiv"]))
    _tel = str(prof.get("telefon") or "")
    if len(_tel) > 15:
        res.avertismente.append("Telefon firma are %d caractere (max 15, C(15)) - va fi trunchiat la 15 la emitere; verifică." % len(_tel))
    if not ops:
        res.avertismente.append("Nicio operațiune intracomunitară în lună — D390 se depune doar dacă există operațiuni.")
    res.avertismente.append("Mapare automată: emisă->L, primită->A (bunuri). Servicii (P/S) și triangulație (T/R) = clasificare manuală.")
    return res


def valideaza(res):
    """Verifica regulile ANAF care se pot prinde PRE-DUK -> lista de erori BLOCANTE. Cablat in
    genereaza (T2 - inainte era cod mort). NB: checksum-ul VIES invalid NU e aici (e AVERTISMENT, nu
    blocant): o operatiune obligatorie raportata cu CUI invalid e mai buna decat una disparuta tacit
    (Costin) - se emite si se NUMESTE partenerul, DUK o prinde daca e cazul."""
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Luna invalidă.")
    if res.an == 2020 and res.luna < 2:
        erori.append("Pentru an=2020, luna >= 2.")
    _cui = _NEDIGIT.sub("", prof.get("cui") or "")
    if not _cui:
        erori.append("LIPSĂ CUI firma (obligatoriu).")
    elif len(_cui) > 10:
        erori.append("CUI firma are %d cifre (max 10, N(10)) - clamparea ar corupe identitatea; corectează." % len(_cui))
    if not (prof.get("nume")):
        erori.append("LIPSĂ denumire firma.")
    # codO obligatoriu pentru L,T,P,R. NOTA: catalogul/tura ziceau "DUK cere codO doar pt L,T,P (nu R)";
    # proba DUK boundary 10.08.2026 CONTRAZICE: R fara codO e respins de validatorul instalat prin
    # DUK regula R24.2 ("o tranzactie de tip R trebuie sa aibe codO completat"), pe langa cerinta pt L,T,P. Deci codO
    # obligatoriu = L,T,P,R (ancorat pe validatorul instalat, ca test_nomenclatoare...). A,S il pot omite.
    for (tip, tara, cod, den) in res.ops:
        if tip in ("L", "T", "P", "R") and not cod:
            erori.append("Operatorul %s/%s (tip %s) nu are cod - obligatoriu pentru L,T,P,R (DUK regula R24.2 pentru R; codO cerut și pentru L,T,P)." % (tara, den, tip))
        if tara and tara not in TARI_UE:
            erori.append("Țară %s (operator %s) nu e în nomenclatorul UE." % (tara, den))
        if cod and len(cod) > 12:
            erori.append("codO %r (operator %s/%s) depășește 12 caractere C(12) - trunchierea ar corupe VAT-ul." % (cod, tara, den))
    # per-partener din diag: tara mistypata + codO_lung = BLOCANTE (nu lasa operatiunea obligatorie sa
    # dispara tacit intr-un count anonim; numeste partenerul si motivul, pre-DUK).
    for d in getattr(res, "diag", []):
        _id = "%s (CUI %r, factura %s)" % (d["den"] or "(fără denumire)", d["cui"], d["directie"] or "-")
        if d["categorie"] == "tara":
            erori.append("Partener %s: %s. Operatiunea NU se poate declara până nu corectezi țară - nu dispare tacit." % (_id, d["motiv"]))
        elif d["categorie"] == "codO_lung":
            erori.append("Partener %s: %s." % (_id, d["motiv"]))
    # totalPlata_A coerent
    calc = (res.nr_opi + res.rezumat["L"] + res.rezumat["T"] + res.rezumat["A"]
            + res.rezumat["P"] + res.rezumat["S"] + res.rezumat["R"])
    if calc != res.total_plata_a:
        erori.append("totalPlata_A incoerent (calcul=%d, stocat=%d)." % (calc, res.total_plata_a))
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip()
    tel = (prof.get("telefon") or "")[:15]   # C(15): clamp la emitere (avertisment dat in calcul_d390)
    mail = prof.get("email") or ""
    bz = res.rezumat
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    # [regula 4 - fara default tacut] nume/prenume/functie declarant sunt DA (obligatorii); cand lipsesc
    # din profil emitem un implicit (altfel DUK respinge campul gol) DAR ANUNTAT prin avertisment.
    _dnume = prof.get("declarant_nume")
    _dfct = prof.get("declarant_functie")
    if not (_dnume and _dfct):
        res.avertismente.append("D390: declarantul (nume/funcție) lipsește din profil -> emis implicit "
                                "\"ADMINISTRATOR\". Completează declarantul în profilul firmei, nu lasa implicitul.")
    _dnume = _dnume or "ADMINISTRATOR"
    _dpren = prof.get("declarant_prenume") or "-"
    _dfct = _dfct or "ADMINISTRATOR"
    hdr = ('<declaratie390 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D390.xsd" '
           'luna="%d" an="%d" d_rec="0" nume_declar="%s" prenume_declar="%s" '
           'functie_declar="%s" cui="%s" den="%s" adresa="%s"'
           % (NS, NS, res.luna, res.an,
              _esc(_t(_dnume, _LIM["d390"]["nume_declar"])),
              _esc(_t(_dpren, _LIM["d390"]["prenume_declar"])),
              _esc(_t(_dfct, _LIM["d390"]["functie_declar"])),
              _esc(cui), _esc(_t(den, _LIM["d390"]["den"])), _esc(_t(adr, _LIM["d390"]["adresa"]))))
    if tel:
        hdr += ' telefon="%s"' % _esc(tel)
    if mail:
        hdr += ' mail="%s"' % _esc(_t(mail, _LIM["d390"]["mail"]))
    # CORECTAT 16.07.2026, dupa verificare la sursa oficiala (static.anaf.ro,
    # structura_D390_2020_180320.pdf, OPANAF 705/2020): <rezumat> EXISTA, e element
    # separat, 1 aparitie obligatorie. Fix-ul de 15.07.2026 il scosese ("REZUMATUL E
    # INLINE PE RADACINA") pe baza unui `strings` pe binarul validatorului care n-a
    # gasit clasa/tag "rezumat" acolo - concluzie gresita: absenta dintr-un extras nu
    # inseamna absenta. Sursa oficiala arata clar "<rezumat> 1 aparitie", cu campurile
    # nr_pag/nrOPI/bazaL/bazaT/bazaA/bazaP/bazaS/bazaR/total_baza in interiorul lui,
    # nu pe radacina.
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    H.append('  <rezumat nr_pag="1" nrOPI="%d" bazaL="%d" bazaT="%d" bazaA="%d" '
             'bazaP="%d" bazaS="%d" bazaR="%d" total_baza="%d"/>'
             % (res.nr_opi, bz["L"], bz["T"], bz["A"], bz["P"], bz["S"], bz["R"],
                res.total_baza))
    # operațiuni ordonate (tip, tara, cod)
    for (tip, tara, cod, den) in sorted(res.ops.keys(), key=lambda k: (k[0], k[1], k[2])):
        # codO="" (atribut vid) e respins structural de DUK ("prezent dar vid nepermis"); pentru A/S codO
        # POATE lipsi -> se OMITE atributul cand e gol (L,T,P,R gol e deja blocat de valideaza in genereaza).
        _codO = (' codO="%s"' % _esc(cod)) if cod else ''
        H.append('  <operatie tip="%s" tara="%s"%s denO="%s" baza="%d"/>'
                 % (tip, _tara_xml(tara), _codO, _esc(_t(den, _LIM["d390"]["denO"])), res.ops[(tip, tara, cod, den)]))
    H.append("</declaratie390>")
    return "\n".join(H)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        # [A2 art.284 "ziua 15"] Incadrarea in perioada se face pe EXIGIBILITATE, nu pe data_emitere bruta.
        # CF art.284: exigibilitatea operatiunilor IC intervine la data emiterii facturii, DAR nu mai tarziu de
        # a 15-a zi a lunii urmatoare celei in care a avut loc faptul generator. Deci exigibilitate =
        # MIN(data_emitere, ziua 15 a lunii urmatoare faptului). Camp data_faptului_generator OPTIONAL: cand e
        # NULL -> exigibilitate = data_emitere = comportamentul ANTERIOR (backward-compat). O factura emisa TARZIU
        # (dupa ziua 15) cu fapt intr-o luna anterioara se muta pe luna exigibilitatii (mai devreme).
        _exig = ("CASE WHEN f.data_faptului_generator IS NULL THEN f.data_emitere "
                 "ELSE LEAST(f.data_emitere, (date_trunc('month', f.data_faptului_generator) "
                 "+ interval '1 month' + interval '14 days')::date) END")
        cur.execute("SELECT f.id, f.tert_nume, f.tert_cui, c.nume AS c_nume, c.cui AS c_cui, "
                    "f.directie, f.total, f.tva "
                    "FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                    "WHERE " + _exig + " >= %s AND " + _exig + " < %s ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    # CUI-ul: intai clientul din nomenclator (c.cui), altfel tert_cui de pe factura.
    # Bug dovedit 16.07.2026 prin audit pe date reale: se citea DOAR c.cui, legat de
    # client_id. Facturile create direct (fara fisa de client) si TOATE facturile
    # PRIMITE (care n-au niciodata client_id - ala e pentru clienti, nu furnizori)
    # aveau cui="" -> respinse tacit de calcul_d390 la primul filtru CUI. D390
    # genera mereu "0 operatiuni" chiar si cu facturi UE reale in luna.
    facturi = [{"cui": (r["c_cui"] or r["tert_cui"] or "").strip(),
                "nume": (r["c_nume"] or r["tert_nume"] or "").strip(),
                "directie": r["directie"],
                "total": r["total"] if r["total"] is not None else 0,
                "tva": r["tva"] if r["tva"] is not None else 0} for r in rows]
    return prof, facturi


def pull_manual(conn, schema, an, luna):
    """[F125] Liniile pur manuale D390 pentru luna (introduse de contabil, fără factură).
    Include id-ul: UI-ul il foloseste ca sa STEARGA linia (butonul dec-man-del -> DELETE
    .../manual/{id}). Fara id, GET-ul returna linii nestergibile (data-id=undefined -> 422).
    Consumatorii de calcul (calcul_d390) ignora cheia id."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT id, tip, tara, cod, den, baza FROM {schema}.d390_manual "
                    f"WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        return [{"id": i, "tip": t, "tara": ta, "cod": c, "den": d, "baza": b}
                for (i, t, ta, c, d, b) in cur.fetchall()]


def pull_reclasificari(conn, schema, an, luna):
    """[F125] Override-urile de tip pe operațiuni auto-derivate: {(directie, tara, cod): tip}."""
    with conn.cursor() as cur:
        cur.execute(f"SELECT directie, tara, cod, tip FROM {schema}.d390_reclasificare "
                    f"WHERE an=%s AND luna=%s", (an, luna))
        return {(dir_, ta, c): t for (dir_, ta, c, t) in cur.fetchall()}


def achizitii_d301(conn, schema, an, luna):
    """[front D390<->d301, audit tenant_006 18.08.2026] Cate operatiuni IC sunt inregistrate in
    d301_operatiuni pentru perioada (achizitii IC ale neplatitorilor art.317, din ecranul D301).
    D390 NU le citeste automat: d301_operatiuni NU are codul TVA + tara FURNIZORULUI, pe care D390 cod A
    le cere (codT/codO) - vezi decizia de flux (extindere d301 vs facturi). Pe refuzul-pe-zero le
    SEMNALAM (Regula 4: nu 'nu exista operatiuni' cand D301 are achizitii). Tabela poate lipsi (partida simpla)."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
        if not cur.fetchone()[0]:
            return 0
        cur.execute(f"SELECT count(*) FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s", (an, luna))
        return cur.fetchone()[0]


def d390_are_operatiuni(conn, schema, an, luna, azi=None):
    """Fapt per-luna: exista operatiuni intracomunitare in (an, luna)? -> True | False | None.
      True/False = perioada INCHISA (luna incheiata inainte de azi): fapt STABILIT din facturi IC
                   (_facturi_ic) + d390_manual (liniile manuale F125) - sursele D390 ale unui PLATITOR.
      None       = perioada DESCHISA (curenta/viitoare): exigibilitatea nu se poate stabili inca.
    Se apeleaza DOAR pentru platitori (art. 316) - poarta din obligatii_datorate. NU citeste d301_operatiuni
    (acela e artefact D301 / NEplatitori, irelevant pentru D390 al unui platitor, si lipseste la unele scheme
    vechi de partida simpla -> ar crapa). Temei: D390 se depune NUMAI pentru lunile in care ia nastere
    exigibilitatea operatiunilor IC (instr. completare D390, anexa OPANAF 705/2020; principiu identic OPANAF 705/2020 anexa 2 pct.1.2 (anterior OPANAF 394/2017, abrogat) la D390). NU e obligatie lunara fixa. Vezi DECIZII 23.07."""
    azi = azi or c.azi_ro()
    prima_urm = datetime.date(an + 1, 1, 1) if luna == 12 else datetime.date(an, luna + 1, 1)
    if prima_urm > azi:
        return None                         # luna nu s-a incheiat -> perioada deschisa
    _prof, facturi = pull(conn, schema, an, luna)
    ic, _diag = _facturi_ic(facturi)
    if ic:
        return True
    if pull_manual(conn, schema, an, luna):
        return True
    return False


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firma.")
    return erori


def calculeaza(conn, schema, an, luna, manual=None, reclasificari=None):
    """Calculul D390, FARA poarta fiscala. Intoarce doar `res`.

    Separat de `genereaza` pe 27.07.2026: EMITEREA are o poarta (D390 nu se depune pe zero,
    OPANAF 705/2020 pct. 1.2), dar CALCULUL nu trebuie s-o aiba. Verificatorii incrucisati
    (control_incrucisat.verifica_d390) au nevoie de bazele IC ca sa compare cu evidenta si cu
    D300 depus - iar acolo "zero operatiuni" e un raspuns legitim (baza 0), nu o eroare.

    Fara separarea asta, poarta de la emitere transforma orice luna fara operatiuni intr-un
    verdict GRI pe intreg verificatorul, ascunzand sub-verificarea D-vs-D. Regresie reala,
    prinsa de suita imediat dupa adaugarea portii.
    """
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, facturi = pull(conn, schema, an, luna)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D390 nu se poate genera: " + " ".join(_er))
    # [F125] dacă nu s-au dat explicit (ex. în teste), se iau din evidența persistată — ca toate
    # căile (wizard, pachet, control încrucișat) să vadă ACELEAȘI clasificări.
    if manual is None:
        manual = pull_manual(conn, schema, an, luna)
    if reclasificari is None:
        reclasificari = pull_reclasificari(conn, schema, an, luna)
    res = calcul_d390(prof, an, luna, facturi, manual, reclasificari)
    return res


def genereaza(conn, schema, an, luna, manual=None, reclasificari=None):
    """Genereaza XML-ul D390. Refuza luna fara operatiuni (vezi poarta de mai jos)."""
    res = calculeaza(conn, schema, an, luna, manual, reclasificari)
    # T2: valideaza(res) era COD MORT (calculat, aruncat). Acum e CABLAT: verificarile blocante ->
    # ValueError cu motivul EXACT, per-partener, PRE-DUK (nu mesajul brut DUK dupa generare). Ruleaza
    # INAINTE de poarta zero: daca singurul partener e o tara mistypata, mesajul "corecteaza tara X"
    # e mai util decat "nu ai operatiuni" (altfel operatiunea obligatorie ar disparea tacit).
    _er = valideaza(res)
    if _er:
        raise ValueError("D390 nu se poate genera (corectează și regenereaza):\n  - " + "\n  - ".join(_er))
    # POARTA A DOUA CALE (10.08.2026): recalcul INDEPENDENT sursa->declaratie (core/d390_reconciliere,
    # ca d300_reconciliere). Ruleaza DUPA valideaza (codO/tara/manual curate) si INAINTE de poarta-zero.
    # Blocheaza emiterea daca generatorul a pierdut/mutat o operatiune intre facturi si <rezumat>
    # (aggregation-loss) - DUK n-ar prinde-o (structura valida). Pe zero operatiuni: recalcul 0 == res 0,
    # nu alarmeaza; poarta-zero de mai jos da mesajul corect.
    _recon.verifica_reconciliere(conn, schema, an, luna, res, manual, reclasificari)
    # POARTA FISCALA (27.07.2026, verificat la sursa): D390 NU se depune pe zero.
    # OPANAF 705/2020, Instructiuni pct. 1.2: "Persoanele impozabile inregistrate in scopuri
    # de TVA depun declaratia recapitulativa NUMAI pentru lunile calendaristice in care ia
    # nastere exigibilitatea taxei" (art. 325 Cod fiscal, Legea 227/2015). O luna fara
    # operatiuni intracomunitare NU produce obligatie de depunere.
    #
    # Validatorul ANAF confirma regula structural: cu zero <operatie> respinge cu "lipsa
    # sectiune obligatorie"; cu o singura operatiune, acelasi XML e valid (dovedit pe
    # tenant_001/iunie 2026). Deci sectiunea <operatie> e minOccurs=1 - structura oglindeste
    # regula fiscala.
    #
    # Inainte de asta generatorul emitea un XML gol pe care ANAF il respingea, iar contabilul
    # primea un mesaj de structura in loc de "nu ai ce depune". Acelasi tipar ca la d205
    # ("D205 fara niciun beneficiar de venit").
    if res.nr_opi == 0:
        # [front D390<->d301] Daca D301 are achizitii IC in perioada dar D390 e pe zero, contabilul le-a
        # introdus in ecranul D301 (d301_operatiuni) fara sa le reflecte in D390 -> nu spunem "nu ai
        # operatiuni" (ar fi fals si ar duce la omiterea D390 pentru un art.317). Il indrumam explicit spre
        # adaugarea manuala (Tip A). Acelasi tipar ca refuzul D301 care semnaleaza facturile IC neintroduse.
        _d301 = achizitii_d301(conn, schema, an, luna)
        if _d301:
            raise ValueError(
                "D390 pe zero, DAR există %d operațiune(i) intracomunitară(e) în D301 (d301_operatiuni) în "
                "%02d/%d, nereflectate în D390. Dacă firma e înregistrată conform art.317, adaugă-le manual "
                "în Clasificarea intracomunitară a D390 (Tip A — achiziție bunuri IC de la furnizor UE, cu "
                "țara și codul de TVA al furnizorului). D390 se construiește din facturi + liniile manuale, "
                "nu automat din tabelul D301." % (_d301, luna, an))
        raise ValueError(
            "D390 nu se depune pe zero: luna %02d/%d nu are nicio operațiune intracomunitară. "
            "Declarația recapitulativă se depune NUMAI pentru lunile în care ia naștere "
            "exigibilitatea taxei (OPANAF 705/2020 pct. 1.2; art. 325 Cod fiscal). "
            "Dacă ar fi trebuit să existe operațiuni, verifică dacă facturile UE sunt "
            "introduse și dacă partenerii au cod de TVA valid." % (luna, an))
    return build_xml(res), res
