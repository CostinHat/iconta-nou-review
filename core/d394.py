# -*- coding: utf-8 -*-
"""
core/d394.py — D394 "Declaratie informativa privind livrarile/prestarile si
achizitiile efectuate pe teritoriul national" (OPANAF 3769/2015, actualizat prin
OPANAF 2194/2025 pentru cotele de TVA de la 01.08.2025).

REFACUT DE LA ZERO 15.07.2026 din sursele oficiale (regula: structura declaratiei
se ia de la ANAF, nu din memorie):
  - d394_struct_anaf.txt  — structD394 (ANAF, 41 pagini): elemente, tip+lungime,
    obligativitate, formule, erori.
  - d394_structura_v5.txt — schema extrasa din D394Validator.jar INSTALAT
    (namespace mfp:anaf:dgti:d394:declaratie:v5).
Cele doua se citesc incrucisat: documentul zice CE inseamna, validatorul zice CE
accepta. Unde difera, validatorul castiga (e mai nou: are cotele 21/11).

Versiunea anterioara nu fusese validata NICIODATA: scria <rezumat> in loc de
<rezumat1>, fara <informatii> (obligatoriu), fara sistemTVA/op_efectuate/caen,
cu totalPlata_A dupa o formula inventata, si excludea partenerii straini (care
intra, ca tip_partener 3/4). Testele treceau pentru ca verificau functia pura cu
date scrise de noi, nu ce cere ANAF.

STRUCTURA (ordinea conteaza):
  <declaratie394 luna an tip_D394 sistemTVA op_efectuate prsAfiliat ...>
    <identificare cui caen den adresa telefon ... totalPlata_A/>
    <informatii nrCui1..4 .../>        <-- INAINTE de rezumat1 (atentionare ANAF)
    <rezumat1 tip_partener cota facturiL bazaL tvaL .../>   <-- calculat din op1
    <op1 tip tip_partener cota cuiP denP nrFact baza tva/>
  </declaratie394>
"""
from __future__ import annotations

from core.common import text_anaf as _t  # limita 75 car. ANAF (27.07.2026)
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
from core.common import cheie_manual
_COLOANE_PROFIL = ("nume", "cui", "adresa", "caen")   # minimul citit de aici

import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

MODUL = "d394"
REGULI = "2026.1"
NS = "mfp:anaf:dgti:d394:declaratie:v5"

# op1.tip — lista din ANAF structura D394 VERSIUNE NECUNOSCUTA (pct. 215). NOUA tipuri.
TIPURI = ("A", "L", "C", "V", "AI", "LS", "AS", "ASI", "N")

# tip_partener (pct. 216/36)
P_TVA_RO = 1      # persoana impozabila inregistrata in scopuri de TVA in Romania
P_NEINREG = 2     # persoana neinregistrata in scopuri de TVA
P_UE = 3          # nestabilita in RO, stabilita in alt stat membru
P_NONUE = 4       # nestabilita in RO, in afara UE

# cote acceptate: doc. 2020 zice (0,5,9,19,20,24); validatorul v5 are si 21 si 11
# (OPANAF 2194/2025, TVA 21% si 11% de la 01.08.2025). Validatorul castiga.
COTE = (0, 5, 9, 11, 19, 20, 21, 24)
# cota=0 permisa DOAR pentru aceste tipuri (pct. 217)
TIP_COTA_ZERO = ("LS", "AS", "ASI", "N", "V")

# Campurile pe care le accepta <rezumat1> in v5 - lista EXACTA din validator
# (strings pe Rezumat1.class). Nu se deduc din numele tipului: setul e asimetric.
# rezumat1 cere campurile COMPLETE pe (tip_partener, cota), nu doar cele cu valori:
# validatorul da R38.1/R41.1/R42.1/R49.1/R50.1/R53.1 "trebuie sa existe" pe campuri
# lipsa. Deci se scriu toate, cu 0 unde nu exista operatiuni.
#   cota <> 0 -> facturi/baza/tva pentru L, A (+ AI, AS la tip_partener=1)
#   cota  = 0 -> LS, AS, V, N
# LECTIE 15.07.2026: lista dedusa din `strings` pe Rezumat1.class era INCOMPLETA -
# numele scurte (facturiL) se construiesc dinamic in validator ("facturi" + tip), nu
# apar ca siruri in constant pool. Absenta dintr-un extras NU e absenta.
# Sursa fiabila pentru reguli = validatorul RULAT, care le spune numerotat.
# Cele doua surse se COMPLETEAZA (nu se contrazic):
#  - strings pe Rezumat1.class -> atributele declarate STATIC: tva* exista doar
#    pentru L/A/C/AI. tvaV/tvaLS/tvaAS/tvaN = "atribut necunoscut" (dovedit prin
#    rulare): la taxare inversa TVA e la beneficiar, iar LS/AS sunt regim special.
#  - validatorul RULAT -> campurile construite dinamic ("facturi"+tip), care nu apar
#    ca siruri in constant pool: facturi* exista pentru toate tipurile.
REZ1_FARA_TVA = frozenset(("V", "LS", "AS", "ASI", "N"))
# R232.2 (validator): "daca tip nu este in lista (A, L, C, AI) atunci tva nu trebuie
# sa fie completat" - la taxare inversa TVA-ul e la beneficiar, la neinregistrati nu exista.
OP1_CU_TVA = frozenset(("A", "L", "C", "AI"))

# op11.codPR — nomenclatorul OFICIAL ANAF (Ghid_D394_2016.pdf pag. 26; copie in
# d394_nomenclator_codpr.txt). Mapare din categoriile art. 331 folosite de
# core/taxare_inversa.py (CATEGORII) in codurile D394.
# ATENTIE: codul 21 (cereale) e CENTRALIZATOR - la nivel de op11 se pune SUBCODUL NC
# (1001 grau, 1005 porumb, 120600 floarea-soarelui...), nu 21. De aceea cerealele cer
# codul bunului pe factura, nu doar categoria. Validatorul: "codPR eronat in dictionar".
CODPR = {
    "cereale": "21",              # centralizator; necesita subcod NC pe factura
    "deseuri": "22",
    "masa_lemnoasa": "23",
    "certificate_emisii": "24",
    "energie_electrica": "25",
    "certificate_verzi": "26",
    "cladiri_terenuri": "27",
    "aur_investitii": "28",
    "telefoane": "29",
    "circuite_integrate": "30",   # microprocesoare
    "console_tablete": "31",
}
# Subcodurile NC valide pentru cereale/plante tehnice (Ghid pag. 26).
CODPR_CEREALE = frozenset(("1001", "1002", "1003", "1004", "1005", "1201", "1205",
                           "120600", "121291", "10086000", "120400"))


# judP — cod SIRUTA de judet, 2 cifre cu zero in fata. DOVEDIT pe validator
# (15.07.2026): "B"/"BU"/"BUC"/"IF"/"PH" respinse ("nu se afla in lista"), 40 acceptat.
# Nomenclatorul e compilat in validator, nu exista ca fisier in pachet; codurile 42/43/46
# sunt respinse (goluri reale in nomenclatorul SIRUTA).
JUDETE_SIRUTA = {
    "AB": "01", "AR": "02", "AG": "03", "BC": "04", "BH": "05", "BN": "06", "BT": "07",
    "BV": "08", "BR": "09", "BZ": "10", "CS": "11", "CL": "51", "CJ": "12", "CT": "13",
    "CV": "14", "DB": "15", "DJ": "16", "GL": "17", "GR": "52", "GJ": "18", "HR": "19",
    "HD": "20", "IL": "21", "IS": "22", "IF": "23", "MM": "24", "MH": "25", "MS": "26",
    "NT": "27", "OT": "28", "PH": "29", "SM": "30", "SJ": "31", "SB": "32", "SV": "33",
    "TR": "34", "TM": "35", "TL": "36", "VS": "37", "VL": "38", "VN": "39", "B": "40",
}


def jud_siruta(judet):
    """Codul SIRUTA pentru judP. Accepta abrevierea (PH), numele (Prahova) sau codul."""
    if not judet:
        return None
    j = str(judet).strip().upper()
    if j.isdigit():
        return j.zfill(2)
    if j in JUDETE_SIRUTA:
        return JUDETE_SIRUTA[j]
    nume = {"ALBA": "AB", "ARAD": "AR", "ARGES": "AG", "ARGEȘ": "AG", "BACAU": "BC",
            "BACĂU": "BC", "BIHOR": "BH", "BISTRITA-NASAUD": "BN", "BOTOSANI": "BT",
            "BRASOV": "BV", "BRAȘOV": "BV", "BRAILA": "BR", "BRĂILA": "BR",
            "BUZAU": "BZ", "BUZĂU": "BZ", "CARAS-SEVERIN": "CS", "CALARASI": "CL",
            "CĂLĂRAȘI": "CL", "CLUJ": "CJ", "CONSTANTA": "CT", "CONSTANȚA": "CT",
            "COVASNA": "CV", "DAMBOVITA": "DB", "DÂMBOVIȚA": "DB", "DOLJ": "DJ",
            "GALATI": "GL", "GALAȚI": "GL", "GIURGIU": "GR", "GORJ": "GJ",
            "HARGHITA": "HR", "HUNEDOARA": "HD", "IALOMITA": "IL", "IASI": "IS",
            "IAȘI": "IS", "ILFOV": "IF", "MARAMURES": "MM", "MEHEDINTI": "MH",
            "MURES": "MS", "MUREȘ": "MS", "NEAMT": "NT", "NEAMȚ": "NT", "OLT": "OT",
            "PRAHOVA": "PH", "SATU MARE": "SM", "SALAJ": "SJ", "SĂLAJ": "SJ",
            "SIBIU": "SB", "SUCEAVA": "SV", "TELEORMAN": "TR", "TIMIS": "TM",
            "TIMIȘ": "TM", "TULCEA": "TL", "VASLUI": "VS", "VALCEA": "VL",
            "VÂLCEA": "VL", "VRANCEA": "VN", "BUCURESTI": "B", "BUCUREȘTI": "B"}
    return JUDETE_SIRUTA.get(nume.get(j, ""))


def codpr_din_categorie(categorie):
    """Codul D394 pentru categoria art.331 de pe factura. Pentru cereale se accepta
    direct subcodul NC (10 05, 1201...); codul 21 nu e valid la nivel de op11."""
    if not categorie:
        return None
    c = str(categorie).strip()
    if c in CODPR_CEREALE:
        return c
    return CODPR.get(c)

# <rezumat2>: TOATE campurile sunt obligatorii, si cele de facturi simplificate/bonuri,
# chiar daca sunt 0 (dovedit prin rulare: "atributul trebuie sa existe").
# FSLcod = facturi simplificate cu CUI-ul beneficiarului; FSL = fara CUI; FSA/FSAI =
# achizitii pe factura simplificata (sistem normal / TVA la incasare); BFAI = bonuri.
# iConta nu are inca facturi simplificate si AMEF -> raman 0 pana se construiesc.
REZ2_GOL = {
    "nrFacturiL": 0, "bazaL": Decimal(0), "tvaL": Decimal(0),
    "nrFacturiA": 0, "bazaA": Decimal(0), "tvaA": Decimal(0),
    "nrFacturiAI": 0, "bazaAI": Decimal(0), "tvaAI": Decimal(0),
    "bazaFSLcod": Decimal(0), "TVAFSLcod": Decimal(0),
    "bazaFSL": Decimal(0), "TVAFSL": Decimal(0),
    "bazaFSA": Decimal(0), "TVAFSA": Decimal(0),
    "bazaFSAI": Decimal(0), "TVAFSAI": Decimal(0),
    "bazaBFAI": Decimal(0), "TVABFAI": Decimal(0),
    "baza_incasari_i1": Decimal(0), "tva_incasari_i1": Decimal(0),
    "baza_incasari_i2": Decimal(0), "tva_incasari_i2": Decimal(0),
    "bazaL_PF": Decimal(0), "tvaL_PF": Decimal(0),
}


def rez1_tipuri(tip_partener, cota):
    """Tipurile care TREBUIE sa apara in <rezumat1> pentru (tip_partener, cota).
    Conditiile sunt cele din validatorul v5, citate exact (rulat 15.07.2026):
      R38/R39/R40 : cota <> 0 -> facturiL/bazaL/tvaL
      R49.1/R50.1 : tip_partener = 1 si cota = 0 -> facturiAS/bazaAS
      R49.2/R50.2 : tip_partener <> 1 sau cota <> 0 -> AS nu trebuie sa existe
      R53.1       : tip_partener = 1 si cota = 0 -> facturiV
      R56.1       : tip_partener in (1,3,4) si cota <> 0 -> facturiC
      R591.2/R62.2: tip_partener <> 2 sau cota <> 0 -> N nu trebuie sa existe
      R41.x/R42.x : tip_partener = 2, cota = 0, document_N = 1 -> facturiLS/bazaLS
    Un camp in plus e la fel de respins ca unul lipsa."""
    t = []
    if cota != 0:
        t.append("L")               # R38.1/R38.2: L doar la cota <> 0
        if tip_partener == P_TVA_RO:
            t += ["A", "AI"]        # R43.2/R46.2: A si AI doar la tip_partener = 1
        if tip_partener in (P_TVA_RO, P_UE, P_NONUE):
            t.append("C")           # R56.1
    else:
        t.append("LS")              # R41.1: cota = 0 -> facturiLS, indiferent de partener
        if tip_partener == P_TVA_RO:
            t += ["AS", "V"]        # R49.1/R53.1
        if tip_partener == P_NEINREG:
            t.append("N")           # R591.2: N doar la tip_partener = 2
    return tuple(t)

_NEDIGIT = re.compile(r"\D")
_TARI_UE = {"AT","BE","BG","CY","CZ","DE","DK","EE","EL","ES","FI","FR","HR","HU",
            "IE","IT","LT","LU","LV","MT","NL","PL","PT","SE","SI","SK"}


def _esc(v):
    return (str(v or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _int(x):
    """D394 raporteaza in LEI intregi (N(15))."""
    return int(Decimal(str(x or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _d(x):
    return Decimal(str(x or 0))


def cui_ro(v):
    """CUI romanesc normalizat (fara RO, fara separatori) sau None."""
    raw = (v or "").strip().upper().replace(" ", "")
    if not raw:
        return None
    if raw.startswith("RO"):
        raw = raw[2:]
    cif = _NEDIGIT.sub("", raw)
    return cif or None


def clasifica_partener(cui_brut):
    """(tip_partener, cui_normalizat) — pct. 216.
    Fara CUI -> 2 (neinregistrat). Prefix de stat membru -> 3. Alt prefix -> 4."""
    raw = (cui_brut or "").strip().upper().replace(" ", "")
    if not raw:
        return P_NEINREG, None
    prefix = raw[:2]
    if prefix.isalpha() and prefix != "RO":
        return (P_UE if prefix in _TARI_UE else P_NONUE), raw
    cif = cui_ro(raw)
    return (P_TVA_RO, cif) if cif else (P_NEINREG, None)


def tip_operatiune(directie, taxare_inversa, tip_partener):
    """op1.tip din datele facturii, cu regulile de compatibilitate (pct. 215).
    tip_partener=1 -> tip<>N ; =2 -> tip in (L,LS,N) ; in (3,4) -> tip in (L,LS,C)"""
    emisa = (directie == "emisa")
    if tip_partener == P_NEINREG:
        return "L" if emisa else "N"
    if tip_partener in (P_UE, P_NONUE):
        return "L" if emisa else "C"
    if emisa:
        return "V" if taxare_inversa else "L"
    return "C" if taxare_inversa else "A"


def cota_standard(an, luna):
    """Cota standard de TVA a perioadei, din SURSA UNICA core/common (tva_standard).
    NU se redefineste aici: o a doua sursa pentru aceeasi valoare fiscala e exact
    tiparul care produce doua cifre diferite pentru acelasi lucru."""
    from core import common as _c
    from datetime import date as _dt
    v, _temei = _c.cota("tva_standard", _dt(an, luna, 1))
    # common tine cotele ca FRACTII (0.21), D394 le cere ca PROCENTE intregi (21).
    # int(0.21) = 0 -> cota 0 in declaratie, adica exact bugul pe care il reparam.
    return int((_d(v) * Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def tip_d394(luna):
    """Perioada fiscala din decontul de TVA (pct. 4). Implicit lunar: iConta
    genereaza pe luna. T/S/A raman de completat cand exista vector fiscal."""
    return "L"


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    op1: dict = field(default_factory=dict)       # (tip,tip_partener,cota,cuiP,denP) -> [nrFact,baza,tva]
    rezumat1: dict = field(default_factory=dict)  # (tip_partener,cota) -> {facturiL,bazaL,...}
    rezumat2: dict = field(default_factory=dict)  # cota -> {nrFacturiL,bazaL,tvaL,...}
    op11: dict = field(default_factory=dict)      # cheie op1 -> {codPR,nrFactPR,bazaPR,tvaPR}
    detaliu: dict = field(default_factory=dict)   # (tip_partener,cota,bun) -> {nrLivV,...}
    serii: list = field(default_factory=list)     # [{tip,serieI,nrI,nrF}]
    informatii: dict = field(default_factory=dict)
    total_plata_a: int = 0
    op_efectuate: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d394(prof, perioada, date, manual=None):
    """PUR. facturi: [{cui, nume, directie, taxare_inversa, cota, baza, tva, tip_N?}].
    manual: [{tip, tip_partener, cota, cuiP, denP, nrFact, baza, tva}] pentru
    operatiuni pe care evidenta nu le poate deduce (bonuri, borderouri, art.331 pe cod).
    """
    an, luna = perioada.an, perioada.luna
    facturi = date.get("facturi") or []
    serii_emise = date.get("serii") or {}
    ops = (manual or {}).get("operatiuni") or []
    intracom = 0
    op1 = {}
    categorii = {}     # cheie op1 -> {categorii art.331} pentru op11
    avert = []
    nefacturabile = 0

    def _adauga(tip, tp, cota, cuiP, denP, nrFact, baza, tva, cat=None):
        k = (tip, tp, int(cota), cuiP or "", (denP or "")[:200])
        if cat:
            categorii.setdefault(k, set()).add(cat)
        c = op1.setdefault(k, [0, Decimal(0), Decimal(0)])
        c[0] += int(nrFact)
        c[1] += _d(baza)
        c[2] += _d(tva)

    for f in facturi:
        tp, cui = clasifica_partener(f.get("cui"))
        # ACHIZITIILE INTRACOMUNITARE NU INTRA IN D394 - se declara in D390 (VIES).
        # Ghid ANAF: "Nu se inscriu achizitiile intracomunitare de bunuri si servicii
        # pentru care exista obligativitatea inscrierii in declaratia 390."
        # D394 e declaratie NATIONALA: partenerii 3/4 apar doar la LIVRARI (si la
        # achizitii cu taxare inversa efectuate pe teritoriul national de nestabiliti).
        if tp in (P_UE, P_NONUE) and f.get("directie") == "primita":
            intracom += 1
            continue
        tip = tip_operatiune(f.get("directie"), f.get("taxare_inversa"), tp)
        cota = int(f.get("cota") or 0)
        if cota not in COTE:
            avert.append("Cotă TVA %s nedeclarabilă (acceptate: %s) — factură ignorată."
                         % (cota, ", ".join(str(c) for c in COTE)))
            nefacturabile += 1
            continue
        # pct. 217: cota=0 permisa doar pentru LS/AS/ASI/N/V
        if cota == 0 and tip not in TIP_COTA_ZERO:
            avert.append("Operațiune tip %s cu cotă 0 (partener %s) — ANAF acceptă cota 0 "
                         "doar pentru %s. Verifică factura." % (tip, cui or "fără CUI",
                                                                "/".join(TIP_COTA_ZERO)))
            nefacturabile += 1
            continue
        _adauga(tip, tp, cota, cui, f.get("nume"), 1, f.get("baza"), f.get("tva"),
                f.get("categorie_331"))

    for op in ops:
        if op.get("tip") not in TIPURI:
            continue
        _adauga(op["tip"], int(op.get("tip_partener") or P_TVA_RO), op.get("cota") or 0,
                op.get("cuiP"), op.get("denP"), op.get("nrFact") or 1,
                op.get("baza"), op.get("tva"))

    # rezumat1: unic pe (tip_partener, cota), CALCULAT din op1 (pct. 38-40).
    # ATENTIE: setul de atribute e ASIMETRIC si e cel din validatorul v5, nu unul
    # dedus din numele tipului (dovedit pe Rezumat1.class 15.07.2026):
    #   are baza+tva pt L/A/C/AI ; bazaV FARA tvaV (la taxare inversa TVA e la
    #   beneficiar) ; facturi* DOAR pt AI/AS/LS ; bazaN+document_N pt tip N.
    # facturiL/A/C/V nu exista: numarul de facturi se citeste din op1.nrFact.
    rez1 = {}
    for (tip, tp, cota, cuiP, denP), (nr, baza, tva) in op1.items():
        r = rez1.setdefault((tp, cota), {})
        r["baza" + tip] = r.get("baza" + tip, Decimal(0)) + baza
        r["facturi" + tip] = r.get("facturi" + tip, 0) + nr
        if tip not in REZ1_FARA_TVA:
            r["tva" + tip] = r.get("tva" + tip, Decimal(0)) + tva

    # Setul de campuri e EXACT: ce lipseste da eroare, ce e in plus la fel.
    for (tp, cota), r in rez1.items():
        ceruta = rez1_tipuri(tp, cota)
        for tip in ceruta:
            r.setdefault("facturi" + tip, 0)
            r.setdefault("baza" + tip, Decimal(0))
            if tip not in REZ1_FARA_TVA:
                r.setdefault("tva" + tip, Decimal(0))
        for k in list(r):
            tip = k.replace("facturi", "").replace("baza", "").replace("tva", "")
            if tip and tip not in ceruta:
                del r[k]

    # rezumat2: 0-4 aparitii, pe COTA, agregat din op1 pentru L/A/AI (dovedit prin
    # rulare: R84 "Nu exista sectiune Rezumat2 pentru cota = X pentru agregarea
    # valorilor din Op1" -> e obligatoriu pentru fiecare cota nenula din op1).
    # Restul campurilor (facturi simplificate FSL*/FSA*, bonuri BFAI, incasari) = 0:
    # iConta nu are inca facturi simplificate/AMEF. Se completeaza doar la op_efectuate=1.
    rez2 = {}
    # R99 (validator, dovedit 15.07.2026): "in sectiunea Rezumat2 corespunzatoare
    # cota=21 atributul nrFacturiA trebuie sa fie egal cu valoarea calculata (2)" -
    # rezumat2 centralizeaza pe FIRMA, iar achizitia cu taxare inversa (C) e tot o
    # ACHIZITIE: intra in nrFacturiA/bazaA/tvaA, nu are camp propriu. La fel, livrarea
    # cu taxare inversa (V) e tot o livrare, dar are cota 0 -> nu ajunge aici.
    REZ2_MAPARE = {"L": "L", "A": "A", "C": "A", "AI": "AI"}
    for (tip, tp, cota, cuiP, denP), (nr, baza, tva) in op1.items():
        camp = REZ2_MAPARE.get(tip)
        if cota == 0 or not camp:
            continue
        r = rez2.setdefault(cota, dict(REZ2_GOL))
        r["nrFacturi" + camp] += nr
        r["baza" + camp] += baza
        r["tva" + camp] += tva

    # informatii (pct. 122-125): nrCui2 = NR INREGISTRARI op1, restul = distinct cuiP
    cuis = {P_TVA_RO: set(), P_UE: set(), P_NONUE: set()}
    nr_op1_p2 = 0
    for (tip, tp, cota, cuiP, denP) in op1:
        if tp == P_NEINREG:
            nr_op1_p2 += 1
        else:
            cuis[tp].add(cuiP)
    inf = {
        "nrCui1": len(cuis[P_TVA_RO]), "nrCui2": nr_op1_p2,
        "nrCui3": len(cuis[P_UE]), "nrCui4": len(cuis[P_NONUE]),
        "nr_BF_i1": 0, "incasari_i1": 0, "incasari_i2": 0,
        "nrFacturi_terti": 0, "nrFacturi_benef": 0,
        # R131: nrFacturi > 0 <=> exista serieFacturi tip 2. Le legam la aceeasi sursa.
        "nrFacturi": sum(1 + (b - a) for a, b in serii_emise.values()) if serii_emise else 0,
        # R132 (validator): "Incepand cu perioada 1.2017 atributul nrFacturiL_PF
        # trebuie sa fie egal cu 0". Camp mort - livrarile catre persoane fizice
        # se declara ca op1 tip N/LS, nu aici.
        "nrFacturiL_PF": 0,
        "nrFacturiLS_PF": 0, "val_LS_PF": 0,
        "solicit": 0, "efectuat": 0,
    }
    # R135.1 (validator): "daca atributul sistemTVA = 0 atunci atributul tvaDed24 nu
    # trebuie sa fie completat". Campurile tvaDed*/tvaDedAI*/tvaCol* apartin sistemului
    # de TVA LA INCASARE - la sistem normal se OMIT, nu se pun pe 0.
    # Distinctia (dovedita prin rulare 15.07.2026):
    #  - tvaDed* / tvaCol* : TVA exigibila prin PROPRIUL sistem de TVA la incasare
    #    -> R135.1: la sistemTVA = 0 NU se completeaza.
    #  - tvaDedAI*         : TVA dedusa din facturi primite de la FURNIZORI cu TVA la
    #    incasare -> obligatorii MEREU (orice firma poate cumpara de la un astfel de
    #    furnizor, indiferent de sistemul propriu).
    for c in COTE:
        if not c:
            continue
        inf["tvaDedAI%d" % c] = 0
        if prof.get("tva_la_incasare"):
            inf["tvaDed%d" % c] = 0
            inf["tvaCol%d" % c] = 0

    # pct. 17 / validator: totalPlata_A = Suma(informatii.nrCui<i>) + Suma(rezumat2.baza[L+A+AI])
    total_plata = (inf["nrCui1"] + inf["nrCui2"] + inf["nrCui3"] + inf["nrCui4"]
                   + sum(_int(r["bazaL"]) + _int(r["bazaA"]) + _int(r["bazaAI"])
                         for r in rez2.values()))

    op_efectuate = 1 if op1 else 0
    inf["efectuat"] = 0 if op1 else 1   # pct. 191: "nu a efectuat livrari..."

    op1_int = {k: [v[0], _int(v[1]), _int(v[2])] for k, v in op1.items()}
    rez1_int = {k: {kk: (_int(vv) if not kk.startswith("facturi") else int(vv))
                    for kk, vv in v.items()} for k, v in rez1.items()}
    # op11 — R233.5: "daca tip_partener = 1 si tip este in lista (C, V) atunci trebuie
    # completata cel putin o sectiune op11". codPR din nomenclatorul ANAF.
    # tvaPR nu se pune la (tip_partener=1 si tip=V) — regula din validator.
    op11 = {}
    for k, (nr, baza, tva) in op1.items():
        tip, tp, cota, cuiP, denP = k
        if not (tp == P_TVA_RO and tip in ("V", "C")):
            continue
        cats = categorii.get(k) or set()
        cod = None
        for c in cats:
            cod = codpr_din_categorie(c)
            if cod:
                break
        if not cod:
            avert.append("Operațiune cu taxare inversă (%s, %s) fără categorie art. 331 "
                         "declarabilă — D394 cere codul produsului (op11)."
                         % (tip, cuiP or denP))
            continue
        # bun = categoria pentru <detaliu>; codPR = subcodul NC pentru <op11>.
        # La cereale codul de categorie e 21, iar codPR trebuie sa fie subcodul NC.
        bun = "21" if cod in CODPR_CEREALE else cod
        op11[k] = {"codPR": cod, "bun": bun, "nrFactPR": nr, "bazaPR": _int(baza),
                   "tvaPR": (None if tip == "V" else _int(tva))}

    # <detaliu> — R35: "Nu exista sectiune Detaliu pentru (tip_partener, cota,
    # document_N, codPR)". Centralizeaza op11 pe (tip_partener, cota, bun):
    #   tip V -> nrLivV / bazaLivV ; tip C -> nrAchizC / bazaAchizC / tvaAchizC
    # Formulele din validator (v1): bazaVc = Suma(op11.bazaPR pt op1.tip='V').
    detaliu = {}
    for k, o in op11.items():
        tip, tp, cota, cuiP, denP = k
        # detaliu.bun = CATEGORIA art.331 (21 = cereale), nu subcodul NC.
        # ANAF: "Codul 21 (cereale) e utilizat numai in cadrul centralizatorului si NU
        # la nivel de Detaliu" -> invers: op11.codPR = subcod NC (1005 porumb),
        # detaliu.bun = categoria (21). Dovedit: bun='1005' -> "nu se afla in lista".
        bun = o.get("bun") or o["codPR"]
        d = detaliu.setdefault((tp, cota, bun),
                               {"nrLivV": 0, "bazaLivV": 0, "nrAchizC": 0,
                                "bazaAchizC": 0, "tvaAchizC": 0})
        if tip == "V":
            d["nrLivV"] += o["nrFactPR"]
            d["bazaLivV"] += o["bazaPR"]
        else:
            d["nrAchizC"] += o["nrFactPR"]
            d["bazaAchizC"] += o["bazaPR"]
            d["tvaAchizC"] += (o["tvaPR"] or 0)

    # <serieFacturi> — R131: "nrFacturi > 0 daca si numai daca exista serieFacturi cu
    # tip 2"; R130: "daca exista serieFacturi cu tip 2 atunci trebuie sa existe cel
    # putin una cu tip 1". tip 1 = plaja ALOCATA (decizie interna), 2 = emise,
    # 3 = emise de beneficiari, 4 = emise de terti (acestea cer cui/den).
    # Seriile se deduc din facturile emise ale lunii; plaja alocata = cea folosita
    # (iConta nu tine inca decizii interne de alocare - vezi LIMITE).
    serii = []
    if serii_emise:
        for serie, (nmin, nmax) in sorted(serii_emise.items()):
            serii.append({"tip": 1, "serieI": serie, "nrI": nmin, "nrF": nmax})
            serii.append({"tip": 2, "serieI": serie, "nrI": nmin, "nrF": nmax})

    rez2_int = {c: {k: (int(v) if k.startswith("nrFacturi") else _int(v))
                    for k, v in r.items()} for c, r in rez2.items()}
    res = Rezultat(an=an, luna=luna, prof=prof, op1=op1_int, rezumat1=rez1_int,
                   rezumat2=rez2_int, op11=op11, detaliu=detaliu, serii=serii,
                   informatii=inf, total_plata_a=total_plata, op_efectuate=op_efectuate)
    res.avertismente = avert
    if intracom:
        res.avertismente.append(
            "%d achiziții de la parteneri din UE/non-UE — nu intră în D394 "
            "(se declară în D390 - VIES)." % intracom)
    if nefacturabile:
        res.avertismente.append("%d facturi excluse din declarație (vezi mai sus)." % nefacturabile)
    res.avertismente.append(
        "D394 %02d/%d: %d parteneri TVA RO, %d neînregistrați, %d UE, %d non-UE; %d operațiuni."
        % (luna, an, inf["nrCui1"], inf["nrCui2"], inf["nrCui3"], inf["nrCui4"], len(op1)))
    return res


def build_xml(res):
    """Ordinea elementelor e normativa: identificare -> informatii -> rezumat1 -> op1.
    Atentionare explicita in structD394: <informatii> se pozitioneaza in
    <declaratie394> INAINTE de <rezumat1>."""
    prof = res.prof or {}
    inf = res.informatii
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")]
                   if x).strip()
    sistem_tva = 1 if prof.get("tva_la_incasare") else 0
    # DOVEDIT 15.07.2026 pe validatorul instalat: <identificare> si <idReprezentant>
    # NU sunt taguri cunoscute de D394Validator v5 (tagurile reale: declaratie394,
    # informatii, rezumat1/2, op1/11/2, facturi, serieFacturi, detaliu, lista).
    # Atributele cui/caen/den/adresa/telefon/totalPlata_A/denR/functie_reprez sunt
    # INLINE pe radacina. structD394 (2020) le arata in <identificare> - documentul
    # e mai vechi decat validatorul, iar validatorul decide ce se depune.
    # ATRIBUTELE RADACINII = exact cele acceptate de D394Validator v5 (dovedit prin
    # strings pe Declaratie394.class, 15.07.2026). nume_declar/prenume_declar/
    # functie_declar NU exista in v5 (erau in structD394 2020) -> "atribut necunoscut".
    # Declarantul e blocul *_intocmit. Reguli incrucisate, citate din validator:
    #   "daca tip_intocmit = 0 atunci cif_intocmit trebuie sa fie CUI"
    #   "daca tip_intocmit = 0 sau (tip_intocmit = 1 si functie_intocmit necompletata)
    #    atunci calitate_intocmit trebuie sa fie completata"
    # Cabinetul/firma depune in nume propriu -> tip_intocmit=0 (persoana juridica),
    # cif_intocmit = CUI-ul firmei, calitate_intocmit completata, functie_intocmit=null.
    rep_den = prof.get("reprezentant_nume") or prof.get("declarant_nume") or "ADMINISTRATOR"
    rep_fct = prof.get("reprezentant_functie") or prof.get("declarant_functie") or "ADMINISTRATOR"
    A = ['<?xml version="1.0" encoding="UTF-8"?>']
    A.append('<declaratie394 xmlns="%s" luna="%d" an="%d" tip_D394="%s" sistemTVA="%d" '
             'op_efectuate="%d" prsAfiliat="0" '
             'cui="%s" caen="%s" den="%s" adresa="%s" telefon="%s" '
             'cifR="%s" denR="%s" functie_reprez="%s" adresaR="%s" '
             'tip_intocmit="0" den_intocmit="%s" cif_intocmit="%s" calitate_intocmit="%s" '
             'optiune="0" totalPlata_A="%d">'
             % (NS, res.luna, res.an, tip_d394(res.luna), sistem_tva, res.op_efectuate,
                _esc(cui), _esc(prof.get("caen") or ""), _esc(_t(prof.get("nume") or "")),
                _esc(_t(adr)), _esc(prof.get("telefon") or ""),
                _esc(cui), _esc(_t(rep_den)), _esc(_t(rep_fct)), _esc(_t(adr)),
                _esc(_t(prof.get("nume") or "")), _esc(cui),
                _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
                res.total_plata_a))
    # <informatii> INAINTE de <rezumat1> (atentionare ANAF in structD394)
    ordine_inf = ["nrCui1", "nrCui2", "nrCui3", "nrCui4", "nr_BF_i1", "incasari_i1",
                  "incasari_i2", "nrFacturi_terti", "nrFacturi_benef", "nrFacturi",
                  "nrFacturiL_PF", "nrFacturiLS_PF", "val_LS_PF"]
    at = " ".join('%s="%d"' % (k, inf[k]) for k in ordine_inf if k in inf)
    at += " " + " ".join('%s="%d"' % (k, inf[k]) for k in sorted(inf)
                         if k.startswith(("tvaDed", "tvaCol")))
    # R191.1: "daca atributul solicit = 0 atunci atributul efectuat nu trebuie sa fie
    # completat" — efectuat apartine blocului de rambursare (solicit=1).
    at += ' solicit="%d"' % inf["solicit"]
    if inf["solicit"]:
        at += ' efectuat="%d"' % inf["efectuat"]
    A.append('  <informatii %s/>' % at)
    for (tp, cota) in sorted(res.rezumat1):
        r = res.rezumat1[(tp, cota)]
        camp = " ".join('%s="%d"' % (k, v) for k, v in sorted(r.items()))
        det = [(k, v) for k, v in sorted(res.detaliu.items()) if k[0] == tp and k[1] == cota]
        if not det:
            A.append('  <rezumat1 tip_partener="%d" cota="%d" %s/>' % (tp, cota, camp))
            continue
        A.append('  <rezumat1 tip_partener="%d" cota="%d" %s>' % (tp, cota, camp))
        for (_tp, _c, bun), d in det:
            at_d = ' bun="%s"' % _esc(bun)
            at_d += "".join(' %s="%d"' % (k, v) for k, v in sorted(d.items()) if v)
            A.append('    <detaliu%s/>' % at_d)
        A.append('  </rezumat1>')
    # ORDINEA sectiunilor, dovedita in D394Validator v5 (ValidatorImpl, 15.07.2026):
    #   declaratie394 -> informatii -> rezumat1 (-> detaliu) -> rezumat2 ->
    #   serieFacturi -> lista -> facturi -> op1 (-> op11)
    # Nu e cea din structD394 (2020), unde rezumat1 e primul si informatii la pct.121.
    for cota in sorted(res.rezumat2):
        r = res.rezumat2[cota]
        camp = " ".join('%s="%d"' % (k, v) for k, v in sorted(r.items()))
        A.append('  <rezumat2 cota="%d" %s/>' % (cota, camp))
    for s_ in res.serii:
        A.append('  <serieFacturi tip="%d" serieI="%s" nrI="%d" nrF="%d"/>'
                 % (s_["tip"], _esc(s_["serieI"]), s_["nrI"], s_["nrF"]))
    for k in sorted(res.op1, key=lambda x: (x[0], x[1], x[2], x[3])):
        tip, tp, cota, cuiP, denP = k
        nr, baza, tva = res.op1[k]
        # R220: tip_partener = 2 si cuiP necompletat -> taraP obligatoriu.
        # R232.2: tva se completeaza DOAR pentru tip in (A, L, C, AI); la taxare
        # inversa (V) si la neinregistrati (N/LS) TVA nu se declara aici.
        # R222.3: tip_partener = 2, cuiP necompletat, taraP = 'RO' -> judP obligatoriu.
        at = (' cuiP="%s"' % _esc(cuiP) if cuiP
              else ' taraP="RO" judP="%s"' % (jud_siruta(prof.get("judet")) or "40"))
        at += ' denP="%s" nrFact="%d" baza="%d"' % (_esc(denP), nr, baza)
        if tip in OP1_CU_TVA:
            at += ' tva="%d"' % tva
        o11 = res.op11.get(k)
        if not o11:
            A.append('  <op1 tip="%s" tip_partener="%d" cota="%d"%s/>' % (tip, tp, cota, at))
            continue
        A.append('  <op1 tip="%s" tip_partener="%d" cota="%d"%s>' % (tip, tp, cota, at))
        a11 = ' codPR="%s" nrFactPR="%d" bazaPR="%d"' % (o11["codPR"], o11["nrFactPR"],
                                                             o11["bazaPR"])
        if o11["tvaPR"] is not None:
            a11 += ' tvaPR="%d"' % o11["tvaPR"]
        A.append('    <op11%s/>' % a11)
        A.append('  </op1>')
    A.append('</declaratie394>')
    return "\n".join(A)


def valideaza(res):
    """Erori care ar fi respinse oricum de ANAF — le spunem inainte."""
    erori = []
    prof = res.prof or {}
    if not (1 <= res.luna <= 12):
        erori.append("Lună invalidă.")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI declarant (obligatoriu).")
    if not prof.get("caen"):
        erori.append("LIPSĂ cod CAEN în profilul firmei (obligatoriu în D394).")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire firmă.")
    if not prof.get("adresa"):
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    if not prof.get("telefon"):
        erori.append("LIPSĂ telefon (obligatoriu în D394).")
    return erori


def pull(conn, schema, perioada):
    """Facturile lunii, cu cota din linii. O factura cu doua cote da doua intrari:
    op1 e unic pe (cuiP, tip, cota) — pct. 218. Intoarce (prof, {facturi, serii})."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    inceput = _inc.isoformat()
    sfarsit = _sf.isoformat()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT * FROM firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        prof = dict(cur.fetchone() or {})
        # partener: emise -> clienti (client_id); primite -> tert_* (furnizorul).
        # proformele nu se raporteaza (nu sunt facturi fiscale).
        cur.execute("""
            SELECT f.id, f.directie, f.total, f.tva, f.taxare_inversa AS ti,
                   f.categorie_331, f.tert_nume, f.tert_cui,
                   c.nume AS c_nume, c.cui AS c_cui,
                   COALESCE(json_agg(json_build_object(
                       'cota', l.cota_tva,
                       'baza', ROUND(l.cantitate * l.pret_unitar, 2))
                     ORDER BY l.id) FILTER (WHERE l.id IS NOT NULL), '[]') AS linii
              FROM facturi f
              LEFT JOIN clienti c ON c.id = f.client_id
              LEFT JOIN factura_linii l ON l.factura_id = f.id
             WHERE f.data_emitere >= %s AND f.data_emitere < %s
               AND COALESCE(f.tip, 'factura') = 'factura'
             GROUP BY f.id, c.nume, c.cui
             ORDER BY f.id
        """, (inceput, sfarsit))
        rows = cur.fetchall()
    facturi = []
    for r in rows:
        emisa = (r["directie"] == "emisa")
        cui = ((r["c_cui"] if emisa else None) or r["tert_cui"] or r["c_cui"] or "")
        nume = ((r["c_nume"] if emisa else None) or r["tert_nume"] or r["c_nume"] or "")
        comun = {"cui": cui, "nume": nume, "directie": r["directie"],
                 "taxare_inversa": bool(r["ti"]), "categorie_331": r["categorie_331"]}
        pe_cota = {}
        for l in (r["linii"] or []):
            if l.get("cota") is None or l.get("baza") is None:
                continue
            c = int(Decimal(str(l["cota"])))
            pe_cota[c] = pe_cota.get(c, Decimal(0)) + _d(l["baza"])
        if pe_cota:
            for cota, baza in sorted(pe_cota.items()):
                facturi.append(dict(comun, cota=cota, baza=baza,
                                    tva=(baza * Decimal(cota) / Decimal(100))))
        else:
            # Factura fara linii (import / e-Factura fara detaliu): cota se deduce din
            # raportul tva/baza. ATENTIE la TAXARE INVERSA PRIMITA (tip C): documentul
            # are TVA = 0 (beneficiarul aplica 4426=4427, art. 331 + norme pct.109), dar
            # ANAF cere COTA BUNULUI: structD394 pct.217 - "valoarea 0 este permisa daca
            # si numai daca tip in (LS, AS, ASI, N, V)". C nu e in lista.
            # Fara asta, orice achizitie cu taxare inversa cadea din declaratie.
            total, tva = _d(r["total"]), _d(r["tva"])
            baza = total - tva
            if tva and baza:
                cota = int((tva / baza * Decimal(100)).quantize(
                    Decimal("1"), rounding=ROUND_HALF_UP))
            elif bool(r["ti"]) and r["directie"] == "primita":
                # cota bunului: nu e pe document. Fara linii nu o putem sti -> cota
                # standard a perioadei, semnalata ca presupunere in avertismente.
                cota = cota_standard(an, luna)
            else:
                cota = 0
            facturi.append(dict(comun, cota=cota, baza=baza,
                                tva=(baza * Decimal(cota) / Decimal(100)
                                     if bool(r["ti"]) and r["directie"] == "primita" else tva)))
    return prof, {"facturi": facturi, "serii": serii_emise(conn, schema, perioada)}


def serii_emise(conn, schema, perioada):
    """Plajele de facturi EMISE in luna: {serie: (nr_min, nr_max)}.
    R130/R131: nrFacturi > 0 <=> exista serieFacturi tip 2; tip 2 cere tip 1.
    Numarul se extrage din partea numerica a lui facturi.numar."""
    import re as _re
    _inc, _sf = perioada.interval()
    inceput = _inc.isoformat()
    sfarsit = _sf.isoformat()
    out = {}
    with conn.cursor() as cur:
        cur.execute("""SELECT COALESCE(NULLIF(serie, ''), '-') AS s, numar
                         FROM facturi
                        WHERE data_emitere >= %s AND data_emitere < %s
                          AND directie = 'emisa' AND COALESCE(tip, 'factura') = 'factura'
                    """, (inceput, sfarsit))
        for serie, numar in cur.fetchall():
            cifre = _re.sub(r"\D", "", str(numar or ""))
            if not cifre:
                continue
            n = int(cifre)
            if serie in out:
                out[serie] = (min(out[serie][0], n), max(out[serie][1], n))
            else:
                out[serie] = (n, n)
    return out


def erori_generare(prof):
    """Poarta bazei nule: profil incomplet -> STOP cu mesaj clar, nu XML respins de ANAF."""
    erori = []
    if not str(prof.get("cui") or "").strip():
        erori.append("LIPSA CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSA denumire firma.")
    return erori


def genereaza(conn, schema, perioada, manual=None):
    manual = cheie_manual(manual, "operatiuni")
    if perioada.luna is None or not (1 <= perioada.luna <= 12):
        raise ValueError("D394 lunar: luna invalidă: %r" % perioada.luna)
    prof, date = pull(conn, schema, perioada)
    _er = erori_generare(prof)
    if _er:
        raise ValueError("D394 nu se poate genera: " + " ".join(_er))
    res = calcul_d394(prof, perioada, date, manual)
    for e in valideaza(res):
        res.avertismente.insert(0, e)
    res.modul, res.reguli = MODUL, REGULI
    return build_xml(res), res
