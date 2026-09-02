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

from core.common import text_anaf as _t, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
from core.common import cere_coloane_cursor  # [garda coloane 27.07.2026]
from core.common import cheie_manual
from core.common import perioada_tva_tip as _ptv, fereastra_tva as _fer  # [fix trim 06.08.2026]
# [LANT legislatie TURA 3, 10.08.2026] SURSA CANONICA de validare a identitatii fiscale (T1/T3 din
# CATALOG_INVALIDITATE.md). Import READ-ONLY, modul LEAF (fara db) - fara risc de import circular.
from core.identitate import valideaza_cui as _vcui, valideaza_cif as _vcif
_COLOANE_PROFIL = ("nume", "cui", "adresa", "caen")   # minimul citit de aici

import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

MODUL = "d394"
REGULI = "2026.1"
NS = "mfp:anaf:dgti:d394:declaratie:v5"

# op1.tip — cele 8 tipuri acceptate de D394Validator INSTALAT (J8, versiunea CURENTA ANAF), aliniate la
# OPANAF 77/2022 (anaf_surse/opanaf_77_2022). ASI ("achizitii regim special catre pers care aplica sistemul
# de TVA la incasare" in pdf-ul 2020/J4) a fost ELIMINAT in versiune post-2020: validatorul il respinge
# ("tip: valoarea ASI nu se afla in lista"). OPANAF 77/2022 defineste AS = "achizitii regim special de la
# persoane care aplica regimul special (agentii turism, second-hand, arta, colectie, antichitati)" - fara
# sub-distinctia dupa sistemul de TVA al partenerului, deci fost-ASI se consolideaza in AS. (03.08.2026,
# greenlight Costin - tool-ul urmeaza validatorul, ca la D101.)
# SURSA (reancorare 25.08.2026): norma, nu validatorul. Norma IN VIGOARE nu e insa OPANAF 77/2022 din
# comentariul de mai sus, ci OPANAF 3769/2015 modificat ultima data de OPANAF 2194/2025 (MO 852/
# 17.09.2025, art.III: se aplica operatiunilor de la 1.08.2025) - act aflat in corpus si necitat nicaieri
# in cod pana azi. Vocabularul e identic in ambele forme ("Tip L/A/LS/AS/AI/V/C/N/I1/I2"), deci
# eliminarea lui ASI - decisa in 08.2026 pe autoritatea validatorului - e sustinuta de NORMA. Nimeni nu
# verificase; validatorul inchisese discutia.
# Doua dezacorduri consemnate in core/nomenclatoare.py: norma scrie AI cu diacritica, iar I1/I2
# (incasari prin aparate de marcat) sunt in norma dar neconstruite in iConta.
TIPURI = ("A", "L", "C", "V", "AI", "LS", "AS", "N")

# tip_partener (pct. 216/36)
P_TVA_RO = 1      # persoana impozabila inregistrata in scopuri de TVA in Romania
P_NEINREG = 2     # persoana neinregistrata in scopuri de TVA
P_UE = 3          # nestabilita in RO, stabilita in alt stat membru
P_NONUE = 4       # nestabilita in RO, in afara UE
# [T3/G-d1 10.08.2026] SENTINEL intern (NU tip ANAF): CUI cu prefix alfabetic care nu e cod de tara
# recunoscut -> CUI RO gresit tastat, NU partener strain. Vezi clasifica_partener + calcul_d394 (blocaj).
P_INVALID = -1

# cote acceptate: doc. 2020 zice (0,5,9,19,20,24); validatorul v5 are si 21 si 11
# (OPANAF 2194/2025, TVA 21% si 11% de la 01.08.2025). Validatorul castiga.
COTE = (0, 5, 9, 11, 19, 20, 21, 24)
# cota=0 permisa DOAR pentru aceste tipuri (pct. 217)
TIP_COTA_ZERO = ("LS", "AS", "N", "V")

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
REZ1_FARA_TVA = frozenset(("V", "LS", "AS", "N"))
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
    "gaze_naturale": "36",
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


# Nomenclatorul pentru operatiuni N (lit. D, OPANAF 77/2022 pct.10): "natura bunurilor/serviciilor
# achizitionate de la persoane fizice - tip N - cereale si plante tehnice, deseuri, masa lemnoasa, terenuri,
# constructii, ALTE bunuri si servicii". Codurile de categorie 22/23/32-35 sunt valide direct la op11
# (2 cifre). EXCEPTIE cereale (21): centralizator - la op11 codul 21 NU e valid (DUKIntegrator D394_31,
# reguli 2026.1: "valoarea '21' nu se afla in lista" + R63; spec anaf_surse/d394_struct_anaf.txt poz.68-70:
# "op11(codPR)=bun pt bun<>21 SAU lung(op11(codPR))>2 pt bun=21"), se cere subcodul NC (lung>2), ca la art.331.
# NOTA 10.08.2026: comentariul anterior sustinea ca validatorul accepta 21 pt tip_partener=2 - CREDINTA
# NECORFRUNTATA, infirmata la confruntarea cu DUK (verificare circulara: cod+test scrise pe aceeasi presupunere).
CODPR_N = {
    "cereale": "21",         # centralizator - cere subcod NC pe factura (ca la art.331)
    "deseuri": "22",
    "masa_lemnoasa": "23",
    "terenuri": "32",
    "constructii": "33",
    "alte_bunuri": "34",
    "alte_servicii": "35",
}


def codpr_N_din_categorie(categorie):
    """codPR pentru o operatiune N (lit.D). None daca necunoscuta.
    Pentru cereale accepta direct subcodul NC (1001, 1005...) - la op11 codul 21 (centralizator) NU e
    valid (spec poz.68-70: pt bun=21 lung(op11(codPR))>2); subcodul e obligatoriu, ca pe calea art.331."""
    if not categorie:
        return None
    c = str(categorie).strip()
    if c in CODPR_CEREALE:
        return c
    return CODPR_N.get(c.lower())


def codpr_din_categorie(categorie):
    """Codul D394 pentru categoria art.331 de pe factura. Pentru cereale se accepta
    direct subcodul NC (10 05, 1201...); codul 21 nu e valid la nivel de op11."""
    if not categorie:
        return None
    c = str(categorie).strip()
    if c in CODPR_CEREALE:
        return c
    return CODPR.get(c)


def _op11_necesita(tip, tp):
    """op11 e OBLIGATORIU pt: R233.5 (tip_partener=1 si tip in C/V) sau R233.6 (tip_partener=2 si tip N).
    Un op1 din aceste cazuri emis FARA op11 e respins de DUK -> nu-l expediem (blocaj/excludere)."""
    return (tp == P_TVA_RO and tip in ("V", "C")) or (tp == P_NEINREG and tip == "N")


def _op11_cod(k, categorii):
    """(codPR, bun, motiv_lipsa) pentru un op1 care necesita op11. PUR (foloseste nomenclatorul
    modulului). codPR=None + motiv cand nu se poate obtine un cod valid (fara categorie art.331, sau
    cereale fara subcodul NC pe factura - centralizatorul '21' nu e valid la op11, poz.68-70)."""
    tip = k[0]
    cats = categorii.get(k) or set()
    cod = None
    for c in cats:
        cod = codpr_N_din_categorie(c) if tip == "N" else codpr_din_categorie(c)
        if cod:
            break
    if not cod:
        return None, None, "fără categoria art.331 a bunului"
    bun = "21" if cod in CODPR_CEREALE else cod
    if bun == "21" and len(cod) <= 2:
        return None, None, "cereale fără subcodul NC pe factura (ex. 1001 grau / 1005 porumb)"
    return cod, bun, None

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
# [T3/G-d1] coduri de tara NON-UE recunoscute (ISO 3166-1 alpha-2, set generos de parteneri comerciali
# reali). Rol: a distinge un partener STRAIN GENUIN (prefix = cod de tara real) de un CUI RO gresit
# tastat cu litere (prefix care NU e cod de tara -> nu-l facem tacit partener strain, vezi P_INVALID).
# Erand spre BLOCAJ: un cod NON-UE lipsa aici e o eroare vizibila (contabilul o vede), pe cand un CUI RO
# garbage clasificat tacit strain e cea mai grava neconformitate D394 (date gresite acceptate de DUK).
_TARI_NONUE = {
    "GB","CH","NO","IS","LI","MC","SM","VA","AD","GI",
    "AL","BA","ME","MK","RS","XK","MD","UA","BY","RU","TR","GE","AM","AZ",
    "US","CA","MX","BR","AR","CL","CO","PE","UY","VE","EC","BO","PY","CR","PA","DO","GT",
    "CN","JP","KR","HK","TW","SG","MY","TH","VN","ID","PH","IN","PK","BD","LK","KZ","UZ",
    "IL","AE","SA","QA","KW","BH","OM","JO","LB","IQ","IR","EG","MA","TN","DZ","LY",
    "ZA","NG","KE","GH","ET","TZ","AU","NZ",
}


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


def clasifica_partener(cui_brut, platitor_tva=None):
    """(tip_partener, cui_normalizat) — pct. 216. `platitor_tva` = statutul TVA INGHETAT pe factura (fapt
    contabil), consultat pentru RO cu CUI valid: True -> tip 1 (inregistrat); False -> tip 2 (NEinregistrat in
    scop TVA, chiar cu CUI valid: PJ neplatitor / PF) -> pe achizitie devine N. NULL = necunoscut (factura
    legacy, inainte de camp) -> EURISTICA de forma (un CUI valid e PRESUPUS platitor). Limita legacy + trigger
    de backfill via perioade_TVA: GARZI. Corectitudine ISTORICA: flag-ul inghetat da statutul de ATUNCI (acelasi
    CUI, 2 facturi -> 2 raspunsuri).
    Fara CUI -> 2. Prefix de stat membru UE -> 3; prefix de tara NON-UE recunoscut -> 4.
    [T3/G-d1 10.08.2026] Prefix ALFABETIC care NU e cod de tara (UE sau non-UE) recunoscut -> P_INVALID:
    e un CUI RO gresit tastat (ex. 'ABC...'), NU un partener strain. ANTERIOR: orice prefix alfa != RO
    devenea TACIT tip 4 (strain, LS cota 0) si DUK trecea cu date GRESITE - cea mai grava neconformitate
    D394. Acum sentinelul urca la calcul_d394 care BLOCHEAZA cu motivul exact (nu-l facem tacit strain)."""
    raw = (cui_brut or "").strip().upper().replace(" ", "")
    if not raw:
        return P_NEINREG, None
    prefix = raw[:2]
    if prefix.isalpha() and prefix != "RO":
        if prefix in _TARI_UE:
            return P_UE, raw
        if prefix in _TARI_NONUE:
            return P_NONUE, raw
        return P_INVALID, raw   # prefix alfa necunoscut: CUI RO invalid, nu partener strain
    cif = cui_ro(raw)
    if not cif:
        return P_NEINREG, None
    if platitor_tva is False:          # RO cu CUI valid DAR neinregistrat in scop TVA -> tip 2 (achizitie N)
        return P_NEINREG, None
    return P_TVA_RO, cif                # True sau NULL (fallback euristica: CUI valid presupus platitor)


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


def tip_d394(prof):
    """Perioada fiscala din decontul de TVA (pct. 4) = VECTORUL FISCAL al firmei
    (firma_profil.tip_decont): L/T/S/A. [06.08.2026] Citit din vector, NU presupus lunar;
    lipsa -> eroare (perioada_tva_tip), fara default tacit 'L'."""
    return _ptv(prof)


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
    # [R119, 02.09.2026] Ce facturi a inclus declaratia, pe cheia operatiunii. Exista ca sa se poata
    # confrunta cu ce s-a transmis prin e-Factura FARA a reimplementa eligibilitatea: cine decide ce
    # intra ramane generatorul, iar cine confrunta doar citeste.
    facturi_incluse: dict = field(default_factory=dict)
    # Cate operatiuni din declaratie NU au factura in spate (manuale: bonuri, borderouri). Se expune
    # fiindca fara ea confruntarea n-ar sti ca nu vede tot — v. regula "unde nu poti stabili ca vezi
    # tot, spui gri".
    manuale_fara_factura: int = 0
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
    # [R119, 02.09.2026] cheie op1 -> {id-uri de facturi}. Se curata la aceleasi `del op1[k]` ca
    # `categorii`: o operatiune scoasa din declaratie isi ia si facturile cu ea, deci nimeni nu poate
    # crede ca o factura a intrat cand de fapt a fost exclusa.
    incluse = {}
    avert = []
    nefacturabile = 0
    excluse_N = []   # (nume, cui, baza) operatiuni N excluse - decizie Costin 04.08 (approach b)

    def _adauga(tip, tp, cota, cuiP, denP, nrFact, baza, tva, cat=None, fid=None):
        # [V_cota0 10.08.2026] R217.2 (validator, PROBAT pe date populate + DUK): tip in
        # (LS,AS,N,V) => cota TREBUIE sa fie 0. V (livrare cu taxare inversa) nu declara TVA
        # (reverse charge la beneficiar); cota bunului sta in op11/detaliu (bazaLivV la
        # tip_partener=1, cota=0), NU pe op1. Fara asta, o livrare taxare inversa cu linii pe
        # cota bunului (ex.21) e respinsa: R217.2 + R68.2/R69.2 (nrLivV/bazaLivV nu au voie la
        # cota<>0) + R35. LS/AS/N sunt deja emise cu cota 0; V era singurul care purta cota
        # bunului. Centralizat aici ca sa acopere ambele cai (facturi + manual).
        k = (tip, tp, (0 if tip == "V" else int(cota)), cuiP or "", (denP or "")[:200])
        if cat:
            categorii.setdefault(k, set()).add(cat)
        # [R119] Ce factura a produs randul. Pe aceeasi cheie ca `categorii`, deci se curata prin
        # aceleasi `del op1[k]` — o operatiune scoasa din declaratie isi ia si facturile cu ea.
        # O factura multi-cota apare pe mai multe chei: `set` dedupe.
        if fid is not None:
            incluse.setdefault(k, set()).add(fid)
        c = op1.setdefault(k, [0, Decimal(0), Decimal(0)])
        c[0] += int(nrFact)
        c[1] += _d(baza)
        c[2] += _d(tva)

    for f in facturi:
        tp, cui = clasifica_partener(f.get("cui"), f.get("platitor_tva"))
        if tp == P_INVALID:
            # [T3/G-d1 10.08.2026] BLOCAJ pre-DUK: un CUI cu prefix alfabetic care NU e cod de tara
            # recunoscut e un CUI RO gresit tastat, NU un partener strain. ANTERIOR devenea TACIT tip
            # 3/4 -> livrare scutita cota 0 (LS) -> DUK trecea cu DATE GRESITE (cea mai grava
            # neconformitate D394). Nu-l emitem tacit: numim partenerul si motivul exact.
            raise ValueError(
                "D394: partenerul \"%s\" are CUI \"%s\" cu prefix alfabetic care nu e cod de țară valid "
                "-> CUI RO invalid, nu partener străin. Un CUI RO tastat greșit (cu litere) NU trebuie "
                "raportat tacit ca partener străin (tip 3/4, cota 0). Corectează CUI-ul pe factura."
                % (f.get("nume") or "?", f.get("cui") or ""))
        # ACHIZITIILE INTRACOMUNITARE NU INTRA IN D394 - se declara in D390 (VIES).
        # Ghid ANAF: "Nu se inscriu achizitiile intracomunitare de bunuri si servicii
        # pentru care exista obligativitatea inscrierii in declaratia 390."
        # D394 e declaratie NATIONALA: partenerii 3/4 apar doar la LIVRARI (si la
        # achizitii cu taxare inversa efectuate pe teritoriul national de nestabiliti).
        if tp in (P_UE, P_NONUE) and f.get("directie") == "primita":
            intracom += 1
            continue
        tip = tip_operatiune(f.get("directie"), f.get("taxare_inversa"), tp)
        if tip == "N":
            # [approach a, 04.08.2026] N (achizitii de la parteneri NEINREGISTRATI, tip_partener=2). DESCOPERIRE
            # (proba jar v5 + DUK): validatorul INSTALAT v5 NU are atributul op1.tip_N (bunuri/servicii) - "tip_N
            # atribut necunoscut". Premisa approach b (tip_N = continut declarat) se baza pe un camp din pdf-ul de
            # structura INEXISTENT in v5 (tiparul ASI). N SE EMITE (tip_document=1, document_N=1), DAR pentru
            # persoana fizica (achizitie fara CUI) R233.6 CERE op11 cu codPR (categoria art.331 a bunurilor) +
            # detaliu(nrN/valN). codPR = CONTINUT DECLARAT, dar reutilizeaza categoria art.331 EXISTENTA pe factura.
            # Fara categorie -> N nu poate fi declarat valid -> ramane EXCLUS cu avertisment (contabilul o adauga).
            if codpr_N_din_categorie(f.get("categorie_331")):
                _adauga("N", P_NEINREG, 0, cui, f.get("nume"), f.get("nrFact", 1), f.get("baza"), 0,
                        f.get("categorie_331"), fid=f.get("factura_id"))
            else:
                excluse_N.append((f.get("nume"), f.get("cui"), f.get("baza")))
            continue
        cota = int(f.get("cota") or 0)
        if cota not in COTE:
            avert.append("Cotă TVA %s nedeclarabilă (acceptate: %s) — factură ignorată."
                         % (cota, ", ".join(str(c) for c in COTE)))
            nefacturabile += 1
            continue
        # pct. 217: cota=0 permisa doar pentru LS/AS/N/V (ASI eliminat - vezi TIPURI)
        if cota == 0 and tip not in TIP_COTA_ZERO:
            # [A6 06.08.2026] o LIVRARE (L) cu cota 0 catre partener RO cu CUI e o livrare SCUTITA (LS),
            # nu o operatiune de aruncat: pct.215 interzice N la tip_partener=1, V=taxare inversa (deja
            # rutata), iar rezumat1 R41.1 cere "cota 0 -> facturiLS indiferent de partener". Reclasificam
            # L->LS in loc s-o pierdem tacut. Reconcilierea (d394_reconciliere) acopera doar cota>0 ->
            # neafectata. Alte tipuri (A/C) cu cota 0 raman semnalate vizibil.
            if tip == "L":
                tip = "LS"
            else:
                avert.append("Operațiune tip %s cu cotă 0 (partener %s) — ANAF acceptă cota 0 "
                             "doar pentru %s. Verifică factura." % (tip, cui or "fără CUI",
                                                                    "/".join(TIP_COTA_ZERO)))
                nefacturabile += 1
                continue
        _adauga(tip, tp, cota, cui, f.get("nume"), f.get("nrFact", 1), f.get("baza"), f.get("tva"),
                f.get("categorie_331"), fid=f.get("factura_id"))

    for op in ops:
        if op.get("tip") not in TIPURI:
            # [GARD CLASA] operatiune manuala a contabilului cu tip gresit -> eroare vizibila, nu drop tacit.
            raise ValueError("D394: operațiune manuală cu tip necunoscut %r (acceptate: %s). Un tip introdus "
                             "de contabil care nu e în lista trebuie să producă eroare vizibilă, nu să dispară "
                             "tacut din declarație." % (op.get("tip"), ", ".join(map(str, TIPURI))))
        if op.get("tip") == "N":
            # [approach a] N inclus cu tip_document=1 + document_N + op11(codPR) DOAR daca are categorie art.331
            # (R233.6 persoana fizica). Fara categorie -> exclus cu avertisment (vezi calea auto).
            if codpr_N_din_categorie(op.get("categorie_331")):
                _adauga("N", P_NEINREG, 0, op.get("cuiP"), op.get("denP"), op.get("nrFact") or 1,
                        op.get("baza"), 0, op.get("categorie_331"))
            else:
                excluse_N.append((op.get("denP"), op.get("cuiP"), op.get("baza")))
            continue
        # [manual_codPR 10.08.2026] SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.233:
        # "Pt ((tip in (V,C) si tip_partener=1) sau (tip=N si ...)) sectiunea <op11> este
        # OBLIGATORIE". O operatiune manuala C (achizitie art.331) / V (livrare cu taxare
        # inversa) catre partener TVA RO (tip_partener=1) trebuie sa poarte codPR in <op11>,
        # altfel op1 se emite FARA op11 -> DUKIntegrator R233.5 respinge. Contractul manual
        # duce categoria art.331 in campul categorie_331 (numele categoriei "deseuri"/"cereale"
        # ... SAU subcodul NC direct, exact ca pe calea facturilor); build op11 (mai jos) o
        # transforma in codPR prin acelasi nomenclator. Fara acest argument C/V manual emitea
        # op1 fara op11 (neconformitate confirmata).
        _adauga(op["tip"], int(op.get("tip_partener") or P_TVA_RO), op.get("cota") or 0,
                op.get("cuiP"), op.get("denP"), op.get("nrFact") or 1,
                op.get("baza"), op.get("tva"), op.get("categorie_331"))

    if excluse_N:
        lista = "; ".join("%s (baza %s lei)" % (n or (c or "fără CUI"), _int(b)) for n, c, b in excluse_N)
        avert.append(
            "ATENTIE: %d operațiune(i) N (achiziții de la parteneri NEÎNREGISTRAȚI, persoane fizice) EXCLUSE "
            "din D394 fiindcă le LIPSEȘTE categoria art.331 a bunurilor (op11.codPR e OBLIGATORIU la persoana "
            "fizica, conform R233.6). Adaugă categoria produsului pe factura ca să fie declarate. Furnizori/sume: "
            "%s. Restul declarației RAMANE valid." % (len(excluse_N), lista))

    # [T1/G-c1 10.08.2026] CHECKSUM cuiP partener, PRE-DUK (altfel DUK il prinde brut: R218.2/R218.3).
    # Sursa canonica core.identitate (import read-only). Un CUI/CIF cu cifra de control gresita / lungime /
    # non-numeric era emis TACIT -> DUK il respingea la depunere. Acum: avertisment care NUMESTE partenerul
    # + motivul exact, PE FIECARE partener distinct (dedup pe (tip, cuiP)). NU exclude (clasificarea e
    # aceeasi ca in a doua cale -> reconciliere neafectata); DUK tot il respinge, dar userul stie motivul.
    # tip 1 = CUI RO (valideaza_cui); tip 2 = poate fi CUI/CNP/NIF (valideaza_cif); 3/4 = strain (RO N/A).
    _cuip_vazute = set()
    for (tip, tp, cota, cuiP, denP) in op1:
        if not cuiP or (tp, cuiP) in _cuip_vazute:
            continue
        _cuip_vazute.add((tp, cuiP))
        if tp == P_TVA_RO:
            ok, motiv = _vcui(cuiP)
            if not ok:
                avert.append("Partener \"%s\": CUI \"%s\" invalid (%s) - DUK regula R218.2 îl respinge. "
                             "Corectează CUI-ul pe factura." % (denP or "?", cuiP, motiv))
        elif tp == P_NEINREG:
            ok, _tid, motiv = _vcif(cuiP)
            if not ok:
                avert.append("Partener \"%s\": cod fiscal \"%s\" invalid (%s) - DUK regula R218.3 îl "
                             "respinge. Corectează codul pe factura." % (denP or "?", cuiP, motiv))

    # [T4/G-bc1 + G-bc2 10.08.2026] op1 care NECESITA op11 dar NU-l poate obtine -> EXCLUS aici, INAINTE de
    # rezumat1/rezumat2 (totalurile raman coerente) si de reconciliere. ANTERIOR (T4): op1 C/V (tip_partener=1)
    # fara categorie art.331 se emitea FARA op11 -> DUK R233.5 respingea, iar avertismentul NU bloca (avertiza-
    # dar-emite-invalid). Acum nu expediem XML pe care DUK il respinge - consistent cu excluderea N-fara-subcod.
    # G-bc2: un N (tip_partener=2) cu cuiP = CUI de FIRMA (nu CNP de persoana fizica) contrazice op11-ul de
    # persoana fizica -> DUK R233.4; il detectam (valideaza_cif: tip 'cui') si-l excludem cu motivul exact.
    for k in list(op1):
        tip, tp, cota, cuiP, denP = k
        if not _op11_necesita(tip, tp):
            continue
        if tp == P_NEINREG and tip == "N" and cuiP:
            _ok, _tid, _m = _vcif(cuiP)
            if _ok and _tid == "cui":
                avert.append(
                    "Operațiune N către partener \"%s\" (cod \"%s\") - codul e CUI de FIRMA, nu CNP de "
                    "persoana fizica: op11 (categoria art.331) e cerut la persoane fizice, iar un partener cu "
                    "CUI de firma declarat ca N-persoana fizica e respins de DUK regula R233.4. Operațiune "
                    "EXCLUSA din declarație; declara-l corect (persoana fizica fără CUI, sau alt tip de "
                    "operatiune)." % (denP or "?", cuiP))
                del op1[k]
                categorii.pop(k, None)
                incluse.pop(k, None)
                continue
        cod, _bun, motiv = _op11_cod(k, categorii)
        if cod is None:
            _regula = "R233.6" if tip == "N" else "R233.5"
            _ident = (denP or "?") + ((" (CUI %s)" % cuiP) if cuiP else "")
            avert.append(
                "Operațiune %s către partener %s %s -> op1 s-ar emite FĂRĂ op11 (codul produsului "
                "art.331), pe care DUK regula %s îl respinge. Operațiune EXCLUSA din declarație; adaugă "
                "categoria art.331 / subcodul NC pe factura ca să fie declarata. Restul declarației RAMANE "
                "valid." % (tip, _ident, motiv, _regula))
            del op1[k]
            categorii.pop(k, None)
            incluse.pop(k, None)

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
        if tip == "N":
            r["document_N"] = 1   # pct.60 = tip_document (facturi=1); conditioneaza facturiLS (R41.2)

    # Setul de campuri e EXACT: ce lipseste da eroare, ce e in plus la fel.
    for (tp, cota), r in rez1.items():
        ceruta = rez1_tipuri(tp, cota)
        for tip in ceruta:
            r.setdefault("facturi" + tip, 0)
            r.setdefault("baza" + tip, Decimal(0))
            if tip not in REZ1_FARA_TVA:
                r.setdefault("tva" + tip, Decimal(0))
        for k in list(r):
            if k == "document_N":
                continue   # document_N nu e un camp per-tip (nu se sterge la curatarea seturilor)
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
        # R131: nrFacturi > 0 <=> exista serieFacturi tip 2. Numarul REAL (din DB, pull) cand
        # e disponibil; apelantii puri (fara nr_facturi) cad pe spanul seriei (aproximatie).
        "nrFacturi": (date.get("nr_facturi") if date.get("nr_facturi") is not None
                      else (sum(1 + (b - a) for a, b in serii_emise.values()) if serii_emise else 0)),
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
    # op11 — R233.5 (tp=1, tip C/V) si R233.6 (tp=2, tip N): codPR din nomenclatorul ANAF, obtinut prin
    # _op11_cod (sursa unica; cereale cer subcodul NC, nu centralizatorul '21' - poz.68-70). op1-urile care
    # NU pot obtine un cod valid au fost DEJA excluse mai sus (T4/G-bc1), inainte de rezumat1/rezumat2 si de
    # reconciliere, deci aici gasim mereu un cod pentru cele care necesita op11 (safety-continue pastrat).
    # tvaPR nu se pune la (tip_partener=1 si tip=V) si nici la N — regula din validator.
    op11 = {}
    for k, (nr, baza, tva) in op1.items():
        tip, tp, cota, cuiP, denP = k
        if not _op11_necesita(tip, tp):
            continue
        cod, bun, _motiv = _op11_cod(k, categorii)
        if cod is None:
            continue   # exclus deja mai sus; nu emitem niciodata op1 fara op11 cerut
        op11[k] = {"codPR": cod, "bun": bun, "nrFactPR": nr, "bazaPR": _int(baza),
                   "tvaPR": (None if tip in ("V", "N") else _int(tva))}

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
                                "bazaAchizC": 0, "tvaAchizC": 0, "nrN": 0, "valN": 0})
        if tip == "V":
            d["nrLivV"] += o["nrFactPR"]
            d["bazaLivV"] += o["bazaPR"]
        elif tip == "N":
            # Detaliu pt N (achizitii de la persoane fizice, tip_partener=2): nrN + valN (v5 Detaliu.class).
            d["nrN"] += o["nrFactPR"]
            d["valN"] += o["bazaPR"]
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
    # [R119] Ce facturi au intrat efectiv in declaratie, pe cheia operatiunii. Sortate, ca
    # rezultatul sa fie determinist (aceleasi intrari -> acelasi obiect, deci si aceeasi amprenta).
    incluse_int = {k: sorted(v) for k, v in incluse.items()}
    # Operatiunile MANUALE n-au factura in spate (bonuri, borderouri, art.331 pe cod). Cine
    # confrunta cu e-Factura trebuie sa STIE cate sunt: fara cifra asta, o factura acoperita de o
    # operatiune manuala ar aparea ca "transmisa si nedeclarata", adica un rosu fals.
    manuale_fara_factura = sum(1 for k, v in op1.items() if k not in incluse)
    res = Rezultat(an=an, luna=luna, prof=prof, op1=op1_int, rezumat1=rez1_int,
                   rezumat2=rez2_int, op11=op11, detaliu=detaliu, serii=serii,
                   informatii=inf, total_plata_a=total_plata, op_efectuate=op_efectuate,
                   facturi_incluse=incluse_int, manuale_fara_factura=manuale_fara_factura)
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
    # [regula 4 - fara default tacut] denR/functie_reprez/calitate_intocmit sunt OBLIGATORII la ANAF;
    # cand lipsesc din profil emitem tot un implicit (altfel DUK respinge campul gol), DAR ANUNTAT prin
    # avertisment - implicit DECLARAT, nu tacit. Contabilul completeaza profilul firmei.
    rep_den = prof.get("reprezentant_nume") or prof.get("declarant_nume")
    rep_fct = prof.get("reprezentant_functie") or prof.get("declarant_functie")
    calitate = prof.get("declarant_functie") or prof.get("reprezentant_functie")
    if not rep_den:
        res.avertismente.append("D394: numele reprezentantului (denR) lipsește din profil -> emis implicit "
                                "\"ADMINISTRATOR\". Completează reprezentantul în profilul firmei, nu lasa implicitul.")
        rep_den = "ADMINISTRATOR"
    if not rep_fct:
        res.avertismente.append("D394: funcția reprezentantului (functie_reprez) lipsește din profil -> emisă "
                                "implicit \"ADMINISTRATOR\". Completează în profil.")
        rep_fct = "ADMINISTRATOR"
    if not calitate:
        res.avertismente.append("D394: calitatea întocmitorului (calitate_intocmit) lipsește din profil -> emisă "
                                "implicit \"ADMINISTRATOR\". Completează în profil.")
        calitate = "ADMINISTRATOR"
    # [prsAfiliat 10.08.2026] SPEC OFICIAL anaf_surse/d394_struct_anaf.txt poz.6.a:
    # "prsAfiliat - Au fost efectuate operatiuni cu persoane afiliate in perioada de
    # raportare", N(1), camp OBLIGATORIU: =0 NU, =1 Da. NU e derivabil din datele iConta -
    # confruntat cu schema (tenant_016 DELTA): firma_profil / clienti / furnizori NU au nicio
    # coloana de persoana afiliata / related-party; 'afiliat' apare in provizioane.py si
    # tva_incasare.py doar ca PARAMETRU de calcul, nu ca date stocate despre parteneri. Sursa
    # onesta = un flag EXPLICIT pe profilul firmei. Pana cand coloana exista prof.get(...) e
    # None -> "0" = DECLARAT: fara operatiuni cu persoane afiliate (valoare declarata, NU
    # presupusa verificata). DDL recomandat (a se aplica de owner, nu aici):
    #   ALTER TABLE firma_profil ADD COLUMN are_operatiuni_afiliate boolean NOT NULL DEFAULT false;
    # firma_profil se citeste cu SELECT * -> coloana, odata adaugata, ajunge automat in prof.
    prs_afiliat = 1 if prof.get("are_operatiuni_afiliate") else 0
    A = ['<?xml version="1.0" encoding="UTF-8"?>']
    A.append('<declaratie394 xmlns="%s" luna="%d" an="%d" tip_D394="%s" sistemTVA="%d" '
             'op_efectuate="%d" prsAfiliat="%d" '
             'cui="%s" caen="%s" den="%s" adresa="%s" telefon="%s" '
             'cifR="%s" denR="%s" functie_reprez="%s" adresaR="%s" '
             'tip_intocmit="0" den_intocmit="%s" cif_intocmit="%s" calitate_intocmit="%s" '
             'optiune="0" totalPlata_A="%d">'
             % (NS, res.luna, res.an, tip_d394(res.prof), sistem_tva, res.op_efectuate, prs_afiliat,
                _esc(cui), _esc(prof.get("caen") or ""), _esc(_t(prof.get("nume") or "", _LIM["d394"]["den"])),
                _esc(_t(adr, _LIM["d394"]["adresa"])), _esc(prof.get("telefon") or ""),
                _esc(cui), _esc(_t(rep_den, _LIM["d394"]["denR"])), _esc(_t(rep_fct, _LIM["d394"]["functie_reprez"])), _esc(_t(adr, _LIM["d394"]["adresaR"])),
                _esc(_t(prof.get("nume") or "", _LIM["d394"]["den_intocmit"])), _esc(cui),
                _esc(_t(calitate, _LIM["d394"]["calitate_intocmit"])),
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
        if cuiP:
            at = ' cuiP="%s"' % _esc(cuiP)
        else:
            # R222.3: tip_partener=2, cuiP necompletat, taraP='RO' -> judP obligatoriu. Proxy = judetul
            # FIRMEI (partenerul neinregistrat n-are adresa stocata). [regula 4] lipsa judetului NU se
            # acopera tacit cu "40" (Bucuresti) - se anunta o singura data.
            _jud = jud_siruta(prof.get("judet"))
            if not _jud:
                if not any("judP emis implicit" in a for a in res.avertismente):
                    res.avertismente.append("D394: județul firmei lipsește din profil -> judP emis implicit "
                                            "\"40\" (București) pentru partenerii neînregistrați fără cod. "
                                            "Completează județul în profil.")
                _jud = "40"
            at = ' taraP="RO" judP="%s"' % _jud
        at += ' denP="%s" nrFact="%d" baza="%d"' % (_esc(_t(denP, _LIM["d394"]["denP"])), nr, baza)
        if tip in OP1_CU_TVA:
            at += ' tva="%d"' % tva
        if tip == "N":
            at += ' tip_document="1"'   # pct.228 (v5): OBLIGATORIU pt tip_partener=2 + N; calea auto = facturi=1
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
    else:
        # [T1/G-c1] CUI-ul PROPRIEI firme prezent-dar-invalid (checksum/lungime) -> DUK regula R6 il
        # respinge la depunere. Il verificam pre-DUK cu sursa canonica (core.identitate), nu doar non-gol.
        _ok, _motiv = _vcui(prof.get("cui"))
        if not _ok:
            erori.append("CUI declarant \"%s\" invalid (%s) - DUK regula R6 îl respinge; corectează CUI-ul "
                         "în profilul firmei." % (prof.get("cui"), _motiv))
    if not prof.get("caen"):
        erori.append("LIPSĂ cod CAEN în profilul firmei (obligatoriu în D394).")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire firmă.")
    if not prof.get("adresa"):
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    if not prof.get("telefon"):
        erori.append("LIPSĂ telefon (obligatoriu în D394).")
    # [R102, 30.08.2026] R112.1 a validatorului, prinsa INAINTE de el: daca declaratia are
    # operatiuni de LIVRARE (L / LS / V), atunci cel putin unul din contoarele de facturi emise
    # trebuie sa fie strict pozitiv. Altfel XML-ul spune, in acelasi document, „am livrat" si
    # „n-am emis nicio factura" — iar DUKIntegrator il respinge cu textul lui brut.
    # DE CE SE INTAMPLA, masurat pe `tenant_017` (08/2026): singura factura emisa in perioada e
    # numerotata `FG-ICL`, FARA NICIO CIFRA, iar `nr_facturi_emise` numara doar facturile al caror
    # numar contine cifre (si pe drept: un numar fara cifre nu e o numerotare). Deci contorul iese
    # 0 peste o livrare reala. Aplicatia STIE asta si poate s-o spuna in cuvintele contabilului.
    _TIP_LIVRARE = ("L", "LS", "V")
    _inf = getattr(res, "informatii", None) or {}
    _are_livrari = any(str(k[0]) in _TIP_LIVRARE for k in (getattr(res, "op1", None) or {}) if k)
    if _are_livrari and not (_inf.get("nrFacturi") or _inf.get("nrFacturi_benef")
                             or _inf.get("nrFacturi_terti")):
        erori.append("D394 declară livrări, dar numărul facturilor emise în perioadă e 0 — "
                     "validatorul ANAF respinge (DUK regula R112.1). Se numără doar facturile al căror "
                     "NUMĂR conține cifre: verifică numerotarea facturilor emise din perioadă.")
    return erori


def pull(conn, schema, perioada):
    """Facturile lunii, cu cota din linii. O factura cu doua cote da doua intrari:
    op1 e unic pe (cuiP, tip, cota) — pct. 218. Intoarce (prof, {facturi, serii})."""
    an, luna = perioada.an, perioada.luna  # [fix NameError 10.08.2026] folosite la cota_standard (taxare inversa primita fara linii)
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT * FROM firma_profil WHERE id = 1")
        cere_coloane_cursor(cur, _COLOANE_PROFIL, "firma_profil")   # [garda 27.07.2026]
        prof = dict(cur.fetchone() or {})
        # [06.08.2026] fereastra pe PERIOADA FISCALA TVA (ca d300.pull); trimestrial -> tot trimestrul.
        _inc, _sf = _fer(perioada, _ptv(prof))
        inceput = _inc.isoformat()
        sfarsit = _sf.isoformat()
        # partener: emise -> clienti (client_id); primite -> tert_* (furnizorul).
        # proformele nu se raporteaza (nu sunt facturi fiscale).
        cur.execute("""
            SELECT f.id, f.directie, f.total, f.tva, f.taxare_inversa AS ti,
                   f.categorie_331, f.tert_nume, f.tert_cui, f.tert_platitor_tva,
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
                 "taxare_inversa": bool(r["ti"]), "categorie_331": r["categorie_331"],
                 "platitor_tva": r["tert_platitor_tva"],
                 # [R119, 02.09.2026] id-ul facturii traverseaza pana la rezultat, ca declaratia
                 # sa poata SPUNE ce a inclus. Era selectat in SQL si se pierdea chiar aici.
                 "factura_id": r["id"]}
        pe_cota = {}
        for l in (r["linii"] or []):
            if l.get("cota") is None or l.get("baza") is None:
                continue
            c = int(Decimal(str(l["cota"])))
            pe_cota[c] = pe_cota.get(c, Decimal(0)) + _d(l["baza"])
        if pe_cota:
            # [nrFact multi-cota, OPANAF 2194/2025 pct.C.5:1221-1227] Pentru o factura cu operatiuni
            # pe cote DIFERITE, la "numar de facturi" se inscrie valoarea 1 in dreptul operatiunii cu
            # TVA cea mai mare si 0 pentru rest (la TVA egal -> cota cea mai mare). ANTERIOR fiecare
            # split primea nrFact=1 -> o factura 2-cote raporta nrFact=2 (supra-numarare tacuta).
            _tva_cota = {c: b * Decimal(c) / Decimal(100) for c, b in pe_cota.items()}
            _cota_nrfact = max(_tva_cota, key=lambda c: (_tva_cota[c], c))
            for cota, baza in sorted(pe_cota.items()):
                facturi.append(dict(comun, cota=cota, baza=baza, tva=_tva_cota[cota],
                                    nrFact=(1 if cota == _cota_nrfact else 0)))
        else:
            # Factura fara linii (import / e-Factura fara detaliu): cota se deduce din
            # raportul tva/baza. ATENTIE la TAXARE INVERSA PRIMITA (tip C): documentul
            # are TVA = 0 (beneficiarul aplica 4426=4427, art. 331 + norme pct.109), dar
            # ANAF cere COTA BUNULUI: structD394 pct.217 - "valoarea 0 este permisa daca
            # si numai daca tip in (LS, AS, N, V)". C nu e in lista. (ASI eliminat - vezi TIPURI)
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
    return prof, {"facturi": facturi, "serii": serii_emise(conn, schema, inceput, sfarsit),
                  "nr_facturi": nr_facturi_emise(conn, inceput, sfarsit)}


def nr_facturi_emise(conn, inceput, sfarsit):
    """Numarul REAL de facturi EMISE cu numar numeric in perioada. Struct D394 (poz.
    nrFacturi, d394_struct_anaf.txt:1797): 'Nr total facturi emise in perioada'. NU spanul
    seriei (min..max): la numerotare necontigua (45,46,50) spanul supra-numara (6 in loc de 3).
    Aceeasi populatie ca serii_emise (facturi emise cu cifre in numar) -> R131 pastrat
    (nrFacturi>0 <=> exista serieFacturi tip 2)."""
    import re as _re
    n = 0
    with conn.cursor() as cur:
        cur.execute("""SELECT numar FROM facturi
                         WHERE data_emitere >= %s AND data_emitere < %s
                           AND directie = 'emisa' AND COALESCE(tip, 'factura') = 'factura'
                    """, (inceput, sfarsit))
        for (numar,) in cur.fetchall():
            if _re.sub(r"\D", "", str(numar or "")):
                n += 1
    return n


def serii_emise(conn, schema, inceput, sfarsit):
    """Plajele de facturi EMISE in PERIOADA [inceput, sfarsit): {serie: (nr_min, nr_max)}.
    R130/R131: nrFacturi > 0 <=> exista serieFacturi tip 2; tip 2 cere tip 1.
    Numarul se extrage din partea numerica a lui facturi.numar.
    [06.08.2026] Fereastra primita din pull (aliniata la perioada fiscala TVA), nu recalculata pe luna."""
    import re as _re
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
        erori.append("LIPSĂ CUI firma.")
    if not str(prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firma.")
    from core.firma_profil_api import erori_declarant as _ed   # [R101] sursa unica
    erori += _ed(prof)
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
    # POARTA A DOUA CALE (gard de continut, 05.08.2026, pas 2/6): reconciliere pe totalurile
    # rezumat2 dintr-un recalcul INDEPENDENT al liniilor brute. Divergenta = HARD-BLOCK care
    # numeste ambele valori; NU repara tacit (tipar DECIZII 05.08). Vezi core/d394_reconciliere.py.
    from core.d394_reconciliere import verifica_reconciliere
    verifica_reconciliere(conn, perioada, res, manual)
    # [R93, 30.08.2026] BLOCANT, nu avertisment — si asta e chiar reparatia.
    # `valideaza(res)` contine exact aceleasi cerinte pe care D100/D101/D205 le opresc CURAT, cu
    # mesaj in clar (adresa domiciliului fiscal, telefon, CAEN, CUI valid). Aici erau impinse in
    # `avertismente`, deci generarea continua si XML-ul pleca incomplet. Masurat pe `tenant_001`,
    # 29.08.2026, prin arbitrul oficial: DUKIntegrator il respinge cu „eroare atribut: adresa:
    # atribut prezent dar vid nepermis" (plus `telefon` si `adresaR`). Contabilul primea eroarea
    # BRUTA a validatorului ANAF in locul propozitiei pe care aplicatia o avea deja scrisa.
    # O obligatie declarata intr-un singur loc (`firma_profil_api.OBLIGATORII`) nu are voie sa fie
    # poarta in trei module si avertisment in al patrulea.
    _er_camp = valideaza(res)
    if _er_camp:
        raise ValueError("D394 nu se poate genera: " + " ".join(_er_camp))
    res.modul, res.reguli = MODUL, REGULI
    _xml = build_xml(res)
    from core.reconciliere_emis import verifica_total_plata_a as _vte
    _vte("d394", _xml, res.total_plata_a)   # poarta pe ARTEFACT: totalPlata_A parsat din emis == res
    return _xml, res
