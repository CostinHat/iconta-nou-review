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

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație recapitulativă VIES privind livrările/achizițiile/prestările intracomunitare'

from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
import re
import datetime
from core import common as c
from core import afirmatii as _af  # [P8] diagnosticele sunt afirmatii
from core.unde import Unde as _Unde  # [P8] domeniul e FACTURA, nu o luna
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

# TIPURI: SURSA e NORMA - OPANAF 705/2020 enumera exact cele sase tipuri la instructiunile de
# completare ("L - pentru livrari intracomunitare de bunuri catre alte state membre" s.u.). Proba pe
# validatorul instalat D390_11 (04.08.2026) ramane, dar ca ce e: CONSTRANGERE, nu sursa. Cele doua sunt
# de acord aici - ce s-a schimbat pe 25.08 e de UNDE se ia nomenclatorul, nu ce contine.
#
# TARI_UE: norma NU enumera tarile - trimite la "codul tarii care a emis codul de inregistrare in
# scopuri de TVA". Lista de mai jos e o INCHIDERE construita de noi peste o norma deschisa; dezacordul
# (inclusiv GB post-Brexit si XI) e consemnat, nu tacut.
#
# Ancorele, structurate si pazite: core/nomenclatoare.py (ANCORE_NORMA) + core/test_nomenclator_pe_norma.py.
# Proba pe validator: test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020.
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
        # [P8, 22.08] FAPT despre FACTURA, nu despre o luna: `_facturi_ic` e pura si clasifica
        # fiecare factura in parte. Domeniul e factura; `unde` il poarta.
        info = dict(_af.afirmatie(
            "fapt", "d390", motiv,
            unde=_Unde("factura", (f.get("cui") or "?"), den or "(fără denumire)"),
            temei_completitudine="codul de TVA al partenerului, verificat contra prefixelor UE"),
            categorie=cat, den=den, cui=(f.get("cui") or ""),
            directie=f.get("directie"), tara=tara, cod=cod, baza=baza)
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
    _sursa = {}   # k -> {"factura","manual/D301"} pt detectia sursei-duble (Q1a)
    recl = reclasificari or {}
    ic, diag = _facturi_ic(facturi)
    for o in ic:
        tip_def = "L" if o["directie"] == "emisa" else "A"       # implicit: bunuri
        # override contabil, VALIDAT contra directiei (ca la scriere); invalid -> eroare, nu fallback tacit
        tip = _reclasificare_tip(o["directie"], o["tara"], o["cod"], recl, tip_def)
        k = (tip, o["tara"], o["cod"], o["den"])
        ops[k] = ops.get(k, Decimal("0")) + o["baza"]
        _sursa.setdefault(k, set()).add("factura")

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
            diag.append(dict(_af.afirmatie(
                "neconformitate", "d390",
                "codO manual are %d caractere (max 12) - trunchierea ar CORUPE numărul de TVA" % len(cod),
                unde="partenerul %s (%s%s)" % (den or "(fără denumire)", tara, cod),
                regula="cod_tva_peste_12_caractere"),
                categorie="codO_lung", den=den, cui=(tara + cod), directie="manual", tara=tara,
                cod=cod, baza=baza_op))
        elif tara and cod:
            # [checksum manual 20.08.2026] Bucla manuala sarea peste checksum_vies - il chema DOAR
            # `_facturi_ic` (latura auto). Deci o linie introdusa de contabil in ecranul D390 sau
            # derivata din D301 ajungea in declaratie cu un cod TVA nevalidat, iar contabilul afla
            # abia din respingerea de la DUK regula R24.1. Acelasi diagnostic, aceeasi categorie,
            # acelasi caracter NEBLOCANT ca pe facturi (vezi `valideaza`: cod invalid raportat >
            # operatiune obligatorie disparuta tacit).
            # `tara and cod`: A/S pot omite legal codO (vezi `valideaza`) - un codO gol NU e un cod
            # gresit, deci nu se raporteaza ca invalid.
            _st, _mo = checksum_vies(tara, cod)
            if _st == "invalid":
                diag.append(dict(_af.afirmatie(
                    "neconformitate", "d390",
                    "cod TVA %s%s invalid: %s (va fi respins de DUK regula R24.1)" % (tara, cod, _mo),
                    unde="partenerul %s (%s%s)" % (den or "(fără denumire)", tara, cod),
                    regula="DUK regula R24.1"),
                    categorie="checksum", den=den, cui=(tara + cod), directie="manual", tara=tara,
                    cod=cod, baza=baza_op))
        k = (tip, tara, cod, den)
        ops[k] = ops.get(k, Decimal("0")) + baza_op
        _sursa.setdefault(k, set()).add("manual/D301")

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
    # [Q2] factura PRIMITĂ fără CUI furnizor: nu doar in numaratoarea anonima - pentru
    # directia primita un CUI gol e SUSPECT (posibila achizitie IC careia ii lipseste codul de TVA).
    for _dp in _domestic:
        if _dp.get("directie") == "primita" and not str(_dp.get("cui") or "").strip():
            res.avertismente.append(
                "Factură PRIMITĂ fără CUI furnizor - %s: exclusă din D390. Dacă e achiziție "
                "intracomunitară, adaugă codul de TVA al furnizorului (fără el nu poate fi "
                "raportată la VIES)." % (_dp["den"] or "(fără denumire)"))
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
    # [Q1a] aceeasi operatiune a primit baza din AMBELE surse (factura + manual/D301) -> bazele
    # s-au ADUNAT in D390 (dubla raportare). Nimic nu impiedica introducerea pe ambele cai; semnalam.
    for _ks, _ss in _sursa.items():
        if "factura" in _ss and "manual/D301" in _ss:
            _tp, _tr, _cd, _dn = _ks
            res.avertismente.append(
                "Posibilă DUBLĂ raportare - operațiunea (tip %s, %s%s, %s) apare ȘI ca factură ȘI "
                "ca linie manuală/din ecranul D301; bazele se adună in D390. Verifică să nu fie "
                "introdusă de două ori." % (_tp, _tr, _cd, _dn or "(fără denumire)"))
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
    """[front D390<->d301, audit tenant_006 18.08.2026] Cate operatiuni D301 AR TREBUI sa apara in D390 dar NU
    au aparut fiindca le lipseste tara furnizorului. Numara DOAR tipurile auto-derivabile (1/3->A, 5->S) FARA
    tara - exact cazul care justifica refuzul-pe-zero cu indrumare spre completarea furnizorului (Regula 4).
    Tipurile 2 (transport nou) / 4 (art.307 mixt) NU se numara: ele nu intra in D390 nici cu tara, deci nu sunt
    'lipsa' din D390 - a le semnala 'lipseste tara' ar fi fals. Tabela/coloana poate lipsi -> 0."""
    if conn is None:
        return 0
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
        if not cur.fetchone()[0]:
            return 0
        cur.execute(f"SELECT count(*) FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s "
                    f"AND tip IN (1, 3, 5) AND coalesce(partener_tara, '') = ''", (an, luna))
        return cur.fetchone()[0]


# [auto-derivare d301->D390, decizia Costin 18.08.2026] Maparea tipului D301 (OPANAF 592/2016) -> codul
# D390 (OPANAF 394/2017 anexa 2 / OPANAF 705/2020), VERIFICATA element-cu-element la sursa:
#  tip 1 (achizitii IC bunuri taxabile) + tip 3 (produse accizabile = bunuri) -> A (cod A = "achizitii
#    intracomunitare de bunuri", fara excludere accizabile - instr. D390);
#  tip 5 (achizitii servicii IC, art.307 alin.(2) CF = servicii art.278(2) de la prestator UE = S4.1) -> S.
# EXCLUSE (nu intra in declaratia recapitulativa):
#  tip 2 (mijloace de transport noi) - raportare speciala, nu in recapitulativa;
#  tip 4 (Sectiunea 4 = art.307 alin.(3)(5)(6) CF, verificat cod_fiscal_227_2015): alin.(3)=gaz/energie
#    electrica/termica (art.275(1)e/f) de la nestabilit -> LIVRARE cu loc in RO, nu achizitie IC; alin.(5)=
#    bunuri iesite din regim suspensiv (art.295(1)a/d) -> operatiune INTERNA; alin.(6)=taxare inversa
#    generala pt livrari/prestari cu loc in RO de la nestabilit neinregistrat -> nu IC. Serviciile IC
#    (alin.2) NU se pun ca tip 4, ci ca tip 5 (S4.1 e subset al S4) -> deja mapate la S.
_D301_TIP_COD = {1: "A", 3: "A", 5: "S"}


def operatiuni_din_d301(conn, schema, an, luna):
    """[auto-derivare d301->D390] Achizitiile IC din ecranul D301 (d301_operatiuni) devin linii D390
    pre-tipizate (ca liniile manuale d390_manual): tip D301 -> cod D390 prin _D301_TIP_COD. Se deriveaza
    DOAR operatiunile cu TARA furnizorului completata (fara tara nu se poate forma o linie D390 valida -
    codT obligatoriu; codO poate fi gol = NOTA 1). baza = round(val_valuta x curs) (aceeasi ca D301).
    Directie 'primita' (achizitii). Tabela poate lipsi (partida simpla) -> []. conn None (teste cu pull
    monkeypatchuit, fara DB) -> [] (nicio operatiune d301 din DB)."""
    from decimal import ROUND_HALF_UP as _RH
    if conn is None:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
        if not cur.fetchone()[0]:
            return []
        cur.execute(f"SELECT tip, val_valuta, curs, partener_tara, partener_cod, partener_den "
                    f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        out = []
        for tip, val, curs, tara, cod, den in cur.fetchall():
            codD = _D301_TIP_COD.get(int(tip or 1))
            tara = (tara or "").strip().upper()
            if not codD or not tara:
                continue   # tip neauto-derivabil (2/4) sau fara tara furnizor -> nu formam linie
            baza = int((Decimal(str(val or 0)) * Decimal(str(curs or 0))).quantize(Decimal("1"), rounding=_RH))
            out.append({"tip": codD, "tara": tara, "cod": (cod or "").strip(),
                        "den": (den or "")[:200], "baza": baza, "directie": "primita"})
    return out


def excluse_d301(conn, schema, an, luna):
    """[audit tenant_006] Operatiunile D301 cu partener UE care NU ajung in D390 - cu MOTIV numit + TEMEI
    citat, SIMETRIC cu diag-ul per-partener al facturilor. Face excluderea AUDITABILA:
      - tip 4 -> art. 307 alin. (3)/(5)/(6) dupa temei_307 (NULL = NECONFIRMAT -> SEMNAL, nu verde);
      - tip 2 -> mijloace de transport noi (raportare speciala);
      - tip 1/3/5 FARA tara furnizor -> nu se poate forma linia D390 (codT obligatoriu) -> SEMNAL.
    Read-only. Tabela poate lipsi -> []. conn None -> []."""
    from core.d301_operatiuni_api import TEMEI_307 as _T307
    if conn is None:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".d301_operatiuni",))
        if not cur.fetchone()[0]:
            return []
        cur.execute(f"SELECT tip, nr_doc, partener_tara, partener_cod, partener_den, temei_307 "
                    f"FROM {schema}.d301_operatiuni WHERE an=%s AND luna=%s ORDER BY id", (an, luna))
        out = []
        for tip, nr_doc, tara, cod, den, temei in cur.fetchall():
            tip = int(tip or 1)
            tara = (tara or "").strip().upper()
            _id = "%s (%s%s, %s)" % (den or "(fără denumire)", tara, (cod or "").strip(), nr_doc or "-")
            codD = _D301_TIP_COD.get(tip)
            if codD and tara:
                continue                      # se deriveaza in D390 (cod A/S) - nu e exclusa
            if codD and not tara:
                out.append(dict(_af.afirmatie(
                    "neconformitate", "d390",
                    "lipsă țara furnizorului — nu se poate forma linia D390 (codT obligatoriu)",
                    unde=_id, regula="tara_furnizor_lipsa"),
                    semnal=True, id=_id, temei="instr. completare D390 (OPANAF 705/2020)"))
            elif tip == 2:
                out.append(dict(_af.afirmatie(
                    "fapt", "d390",
                    "mijloace de transport noi — raportare specială, nu în recapitulativă",
                    an=an, luna=luna,
                    temei_completitudine="instr. completare D390 (OPANAF 705/2020) — tipul operațiunii "
                                         "din D301 determină excluderea"),
                    semnal=False, id=_id, temei="instr. completare D390 (OPANAF 705/2020)"))
            elif tip == 4:
                if temei in _T307:
                    out.append(dict(_af.afirmatie(
                        "fapt", "d390", "exclusa din D390: %s" % _T307[temei]["eticheta"],
                        an=an, luna=luna, temei_completitudine=_T307[temei]["temei"]),
                        semnal=False, id=_id, temei=_T307[temei]["temei"]))
                else:
                    out.append(dict(_af.necunoastere_pe_luna(
                        "d390",
                        "tip 4 (art. 307 alin. 3/5/6) cu TEMEI NECONFIRMAT — confirmă alineatul "
                        "în ecranul D301 ca excluderea din D390 să fie auditabilă", an, luna),
                        semnal=True, id=_id, temei="Cod fiscal art. 307 alin. (3)/(5)/(6)"))
    return out


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


def evidenta_incompleta(conn, schema, an, luna):
    """[21.08.2026] Ce ne impiedica sa AFIRMAM ca luna n-a avut operatiuni intracomunitare?
    Intoarce motivul (text pentru contabil) sau None daca nu stim de nimic in asteptare.

    DE CE EXISTA. `d390_are_operatiuni` intoarce False pe „luna inchisa" - dar inchis inseamna acolo
    doar ca luna CALENDARISTICA s-a terminat (`prima_urm > azi`), NU ca evidenta lunii e completa. O
    firma care n-a inregistrat inca facturile de iulie primea in august „D390 nu se datoreaza pe iulie".
    Poarta se INTARESTE (decis de Costin 21.08), nu se converteste in necunoastere: gri-ul isi pierde
    intelesul daca acopera si „nu stim nimic" si „stim, dar poarta e slaba". Deci: raspundem gri DOAR
    pe lunile despre care avem un semnal CONCRET ca evidenta nu e inchisa.

    CE ACOPERA AZI: e-Facturi descarcate de la SPV si ramase `descarcata` (nici ciorna, nici validata,
    nici respinsa) cu data in luna. E un document pe care ANAF ni l-a dat si care nu e inca inregistrat.

    CE LIPSESTE ca „luna inchisa" sa insemne COMPLETITUDINE (scris, ca tacerea sa nu se citeasca drept
    acoperire):
      1. PERIOADA CONFIRMATA pe domeniul facturi/TVA. Mecanismul general exista (`core/perioada.py`,
         DESIGN_SYSTEM cap.23: cat timp e neconfirmat, datele sunt informative si calculele din aval
         blocheaza), dar singurul domeniu folosit azi e `pontaj`. Fara un domeniu de facturi si fara
         actiunea de confirmare la inchidere, nimeni nu declara vreodata luna incheiata. Asta e
         jumatatea care lipseste, si e munca de produs, nu de cod.
      2. Documentele care exista DOAR pe hartie sau la client. Necunoscute prin constructie - nicio
         poarta nu le poate acoperi, deci limita ramane declarata oricat s-ar intari restul.
    """
    if not conn or not schema:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT to_regclass(%s)", (schema + ".efactura_primite",))
            if not cur.fetchone()[0]:
                return None
            cur.execute("SELECT count(*) FROM " + schema + ".efactura_primite "
                        "WHERE status = 'descarcata' AND data_creare >= %s AND data_creare < %s",
                        (datetime.date(an, luna, 1),
                         (datetime.date(an + 1, 1, 1) if luna == 12 else datetime.date(an, luna + 1, 1))))
            n = cur.fetchone()[0]
    except Exception:
        # MASCA MOTIVATA: None = „nu stiu de nimic in asteptare", deci poarta ramane cum era inainte
        # de intarire (comportament vechi). Un esec de citire NU are voie sa produca gri pe toate
        # lunile - ar converti clasa in necunoastere, exact ce s-a decis sa NU se faca.
        return None
    if not n:
        return None
    return ("%d e-Factur%s primit%s de la ANAF pe %02d.%04d %s încă neînregistrat%s — până atunci nu pot "
            "confirma că luna n-a avut operațiuni intracomunitare." %
            (n, "ă" if n == 1 else "i", "ă" if n == 1 else "e", luna, an,
             "e" if n == 1 else "sunt", "ă" if n == 1 else "e"))


def evidenta_incompleta_sau_neinchisa(conn, schema, an, luna):
    """Poarta COMPLETA a lunii, in ordinea in care conteaza:
      1. documente pe care ANAF ni le-a dat si nu le-am inregistrat (fapt observabil, orice firma);
      2. luna nedeclarata inchisa - DOAR daca firma foloseste inchiderea (`core/inchidere_luna.py`).
    Punctul 2 e adoptarea per firma: o firma care n-a inchis niciodata o luna ramane cu comportamentul
    de dinainte, deci intarirea nu converteste clasa in necunoastere peste noapte."""
    m = evidenta_incompleta(conn, schema, an, luna)
    if m:
        return m
    try:
        from core import inchidere_luna as _il
        return _il.luna_neinchisa_desi_firma_inchide(conn, schema, an, luna)
    except Exception:
        # MASCA MOTIVATA: None = „nu stiu de nimic", deci poarta ramane cum era. Un esec de citire NU
        # are voie sa produca gri pe toate lunile - ar fi exact conversia refuzata.
        return None


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firma.")
    from core.firma_profil_api import erori_declarant as _ed   # [R101] sursa unica
    erori += _ed(prof)
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
    # [auto-derivare d301->D390] achizitiile IC din ecranul D301 (cu furnizor completat) intra ca linii
    # pre-tipizate A/S, INTOTDEAUNA (ca facturile) - persistate, deci vazute de toate caile (wizard/control).
    manual = list(manual) + operatiuni_din_d301(conn, schema, an, luna)
    res = calcul_d390(prof, an, luna, facturi, manual, reclasificari)
    # [audit] excluderi D301->D390 auditabile (motiv + temei citat, semnal pe temei neconfirmat / lipsa tara)
    for _ex in excluse_d301(conn, schema, an, luna):
        _pre = "\u26a0 " if _ex["semnal"] else ""
        res.avertismente.append("%sOperatiune D301 EXCLUSA din D390 - %s: %s (%s)."
                                % (_pre, _ex["id"], _ex["motiv"], _ex["temei"]))
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
            # D390 e pe zero desi D301 are operatiuni -> auto-derivarea nu le-a putut aduce (le lipseste
            # TARA furnizorului). Indrumam spre completarea furnizorului in ecranul D301 (nu 'nu ai operatiuni').
            raise ValueError(
                "D390 pe zero, DAR există %d operațiune(i) intracomunitară(e) în D301 (d301_operatiuni) în "
                "%02d/%d care nu au apărut în D390 — le lipsește ȚARA furnizorului. Completează țara (și, "
                "dacă există, codul de TVA) furnizorului pe fiecare operațiune din ecranul D301: achizițiile "
                "de bunuri (tip 1/3) apar automat ca linii cod A, serviciile IC (tip 5) ca linii cod S. "
                "(Operațiunile tip 2 — transport nou — și tip 4 se clasifică manual în D390 dacă e cazul.)"
                % (_d301, luna, an))
        raise ValueError(
            "D390 nu se depune pe zero: luna %02d/%d nu are nicio operațiune intracomunitară. "
            "Declarația recapitulativă se depune NUMAI pentru lunile în care ia naștere "
            "exigibilitatea taxei (OPANAF 705/2020 pct. 1.2; art. 325 Cod fiscal). "
            "Dacă ar fi trebuit să existe operațiuni, verifică dacă facturile UE sunt "
            "introduse și dacă partenerii au cod de TVA valid." % (luna, an))
    return build_xml(res), res
