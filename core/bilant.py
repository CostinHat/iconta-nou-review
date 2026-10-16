# -*- coding: utf-8 -*-
"""S1005 - situatii financiare anuale microentitati (OMF 107/2025, XSD v14).
Motor PUR: mapare balanta -> F10 (bilant prescurtat) + rulaje -> F20 (cont prescurtat micro).
Sursa rândurilor: FORMULARUL ANAF de bilanț 2025 („soft A”, `anaf_surse/bilant_SC_1225_XML_270326.pdf`) — listele de conturi tipărite
pe fiecare rând (F10, F20 S1005, F20 S1003) și calculele totalurilor; păzite de `core/test_bilant_formular.py` (C12, C13, 233).
Conventii:
  solduri: dict cont(text) -> (sold_debitor, sold_creditor)  [solduri FINALE la 31.12]
  rulaje:  dict cont(text) -> (rulaj_debitor, rulaj_creditor) [cumulate an, clasele 6/7]
Valorile F* sunt intregi (lei), rotunjite aritmetic."""
import re
from decimal import Decimal, ROUND_HALF_UP

from core.common import cate as _cate
from core.stocuri import CONT_TVA_STOC   # TVA-ul din prețul de raft: numai la rd.05 (decizia Costin 08.10, pct.1 la §6 S6)

def _i(x):
    return int(Decimal(str(x or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

def _pe_prefix(m, prefixe, idx):
    """Suma componentelor idx (0=debit,1=credit) pe conturile care incep cu unul din prefixe."""
    t = Decimal("0")
    for cont, v in m.items():
        c = str(cont)
        if any(c.startswith(p) for p in prefixe):
            t += Decimal(str(v[idx] or 0))
    return t

def sd(solduri, *prefixe):  # sold debitor
    return _pe_prefix(solduri, prefixe, 0)

def sc(solduri, *prefixe):  # sold creditor
    return _pe_prefix(solduri, prefixe, 1)

def rd(rulaje, *prefixe):
    return _pe_prefix(rulaje, prefixe, 0)

def rc(rulaje, *prefixe):
    return _pe_prefix(rulaje, prefixe, 1)

def _fara_tva_stoc(s):
    """Soldurile fără analiticul TVA-ului din prețul de raft (`stocuri.CONT_TVA_STOC`, 4428.02): el intră NUMAI la stocuri (rd.05)."""
    return {k: v for k, v in s.items() if str(k) != CONT_TVA_STOC}


# ── Listele de conturi și calculele FORMULARULUI ANAF 2025 ─────────────────────────────────────────────────────────────────────────────
# [C12 + C13, 12.10.2026] SURSA: formularul oficial 2025 („soft A”, `anaf_surse/bilant_SC_1225_XML_270326.pdf`), tabelele `form1.F10S`
# (bilanțul prescurtat, comun S1003 / S1005) și `form1.F20S` (contul prescurtat de profit și pierdere al microentităților): fiecare rând
# își tipărește lista de conturi („(ct. 201 + 203 … − 4904)”) — temeiul ei: OMFP 1802/2014 pct.451 / pct.601, actualizate prin
# OMF 2036/2025 (citat pe formular) — iar totalurile au calculul în `<calculate>`. Nomenclatoarele de mai jos sunt scrise în SINTAXA
# FORMULARULUI și `core/test_bilant_formular.py` le compară cu textul lui, rând cu rând (abaterile — `NOMENCLATOR_ABATERI_FORMULAR` — numite, cu
# motivul). Înainte, F10 nu avea 436 (CAM-ul de plată: bilanțul oricărei firme cu salariați era respins: DUK regula F10_64), 467,
# 4901–4904, 463, iar F20 S1005 punea 603–608 la rd.03, număra de două ori reluările de ajustări (754, 7812–7814, 786) și pierdea 794.
_TERMEN = re.compile(r"(\+/-|[+-])(din)?(\d{3,5})(\*{1,3})?")


def termeni(lista):
    """„201+203-280”, „din508*+5112”, „+/-308”, „431**” -> [(semn, cont, calificativ)]: semnul „+”/„-”; calificativul „” / „*” (de
    repartizat după natură) / „**” (sold debitor) / „***” (sold creditor) / „+/-” (soldul net) / „din” (+ stelele: o parte din cont)."""
    s = re.sub(r"\s+|ct\.", "", lista)
    s = s if s[:1] in "+-" else "+" + s
    out = []
    for semn, din, cont, stele in _TERMEN.findall(s):
        out.append(("+" if semn == "+/-" else semn, cont, "+/-" if semn == "+/-" else (din or "") + (stele or "")))
    return out


def termeni_din_denumire(text):
    """Lista de conturi tipărită în denumirea unui rând de pe formular: parantezele „(ct. …)” / „(din ct. …)”."""
    # „(ct. 6053” — paranteza neînchisă pe formular (F30 rd.185b) se citește și ea
    return [t for par in re.findall(r"\(((?:din\s*)?ct\.[^()]*)(?:\)|$)", text.strip())
            for t in termeni(par.replace("din ct.", "din").replace("din ct", "din"))]


#: F10 — (rând, latura, conturile din formular). Latura „d”: +cont = soldul debitor, −cont = soldul creditor (activele; și acțiunile
#: proprii, pierderile, repartizarea profitului, soldurile D ale lui 117 / 121); „c”: invers (datoriile, capitalurile, provizioanele).
#: „**” = numai soldul debitor, „***” = numai cel creditor, „+/-” = soldul net. „din 4428” la rd.05 = TVA-ul din prețul de raft
#: (`CONT_TVA_STOC`, decizia Costin 08.10.2026); în rest 4428 fără el. Rândurile de total nu sunt aici (`NOMENCLATOR_TOTALURI`).
F10_NOMENCLATOR = (
    (1, "d", "201+203+205+206+2071+4094+208-280-290-4904"),
    (2, "d", "211+212+213+214+215+216+217+223+224+227+231+235+4093-281-291-2931-2935-4903"),
    (3, "d", "261+262+263+265+267*-296*"),
    (5, "d", "301+302+303+321+322+/-308+323+326+327+328+331+332+341+345+346+347+/-348+351+354+356+357+358+361+/-368+371+/-378+381"
             "+/-388+4091-391-392-393-394-395-396-397-398-din4428-4901"),
    (301, "d", "4092+411+413+418+425+4282+431**+436**+437**+4382+441**+4424+din4428**+444**+445+446**+447**+4482+451**+453**+456**+4582"
               "+461+4662+473**-491-495-496-4902+5187"),
    (302, "d", "463"),
    (7, "d", "501+505+506+507+din508*+5113+5114-591-595-596-598"),
    (8, "d", "5112+512+531+532+541+542"),
    (11, "d", "471*"),
    (13, "c", "161+162+166+167+168-169+269+401+403+404+405+408+419+421+423+424+426+427+4281+431***+436***+437***+4381+441***+4423"
              "+4428***+444***+446***+447***+4481+451***+453***+455+456***+457+4581+462+4661+467+473***+509+5186+519"),
    (17, "c", "151"),
    (21, "c", "din475*"),
    (23, "c", "din472*"),
    (27, "c", "din478*"),
    (28, "c", "2075"),
    (30, "c", "1012"), (31, "c", "1011"), (32, "c", "1015"), (33, "c", "1018"), (34, "c", "1031"),
    (35, "c", "104"), (36, "c", "105"), (37, "c", "106"), (38, "d", "109"), (39, "c", "141"), (40, "d", "149"),
    (41, "c", "117"), (42, "d", "117"), (43, "c", "121"), (44, "d", "121"), (45, "d", "129"),
    (47, "c", "1016"), (48, "c", "1017"),
)
#: F20 S1005 — (rând, latura, conturile din formular). Latura „c”: +cont = rulajul creditor, −cont = rulajul debitor (veniturile);
#: „d”: invers (cheltuielile). „+/-” = rulajul net (711, 712: soldul, ca la S1003 rd.07 / rd.08).
F20_S1005_NOMENCLATOR = (
    (1, "c", "701+702+703+704+705+706+708+707-709+7411"),
    (2, "c", "+/-711+/-712+721+722+725+7412+7413+7414+7415+7416+7417+7418+7419+751+755+758+761+762+764+765+766+767+768+7815"),
    (3, "d", "601+602-609*"),
    (4, "d", "641+642+643+644+645+646"),
    (5, "d", "654+681+686-754-7812-7813-7814-7818-786"),
    (6, "d", "603+604+605+606+607+608+611+612+613+614+615+616+617+618+621+622+623+624+625+626+627+628+635+651+652+655+658+663+664+665"
             "+666+667+668"),
    (7, "d", "691+694+697+698"),
    (304, "c", "794"),
)
#: „din care” — părți ale unui rând de mai sus, nu componente ale totalurilor
F20_S1005_NOMENCLATOR_DIN_CARE = ((302, "d", "6051"), (303, "d", "6053"))
#: [C14, comanda Costin 12.10.2026: „construiește F30 cap.XIX pentru S1005, după formularul ANAF 2025, cu listele de conturi tipărite pe
#: fiecare rând”] F30 cap.XIX „Situația veniturilor și cheltuielilor” (numai la microentități, anual: `form1.F30.Table8_an_micro`) — (rând,
#: latura, conturile din formular), ca F20. DUK o confruntă cu F20 (`NOMENCLATOR_CONCORDANTA_F20_F30`). Rândurile 173 / 174 (sold C / D al
#: lui 711 + 712) le calculează `f30_din_rulaje`; rândurile pe care rulajele nu le pot ști nu se scriu: 171 / 204 / 233 / 342 („=null” pe
#: formular), 325 (activitatea preponderentă), 212 / 214 / 223 / 336 / 338 / 340 (entitățile afiliate), 322–324 (felul calamității).
F30_S1005_NOMENCLATOR = (
    (168, "c", "701+702+703+704+705+706+708"), (169, "c", "707"), (170, "d", "709"), (172, "c", "7411"),
    (175, "c", "721+722"), (176, "c", "755"), (177, "c", "725"), (178, "c", "7412+7413+7414+7415+7416+7417+7419"),
    (179, "c", "751+758+7815"),
    (183, "d", "601+602"), (184, "d", "603+604+606+608"), (185, "d", "605"), (186, "d", "607"), (187, "c", "609"),
    (189, "d", "641+642+643+644"), (190, "d", "645+646"),
    (330, "d", "6811"), (192, "d", "6813+6817"), (193, "c", "7813"), (195, "d", "654+6814+din6818"), (196, "c", "754+7814+din7818"),
    (198, "d", "611+613+614+615+621+622+623+624+625+626+627+628"), (331, "d", "612"), (335, "d", "616"), (337, "d", "617"),
    (339, "d", "618"), (199, "d", "635+6586"), (200, "d", "652"), (201, "d", "655"), (202, "d", "6587"),
    (203, "d", "651+6581+6582+6583+6584+6588"), (206, "d", "6812"), (207, "c", "7812"),
    (211, "c", "7611+7612+7613"), (213, "c", "766"), (215, "c", "7418"), (216, "c", "7615+762+764+765+767+768"),
    (220, "d", "686"), (221, "c", "786"), (222, "d", "666"), (224, "d", "663+664+665+667+668"),
    (232, "d", "691"), (328, "d", "694"), (329, "c", "794"), (341, "d", "697"), (234, "d", "698"),
)
#: „din care” — părți ale unui rând de mai sus, nu componente ale totalurilor
F30_S1005_NOMENCLATOR_DIN_CARE = ((180, "c", "7584"), (181, "c", "7815"), (326, "d", "6051"), (327, "d", "6053"), (332, "d", "6121"),
                                  (333, "d", "6122"), (334, "d", "6123"), (217, "c", "7615"))
#: rândurile 173 / 174: „2. Venituri aferente costului producției în curs de execuție (ct.711+712)”, soldul C / soldul D
F30_S1005_VARIATIA_STOCURILOR = ("711", "712")
#: [C14] DUK S1005 (validatorul instalat, `S1005Validator.jar` v13, regulile F20_F30_1–10): F20 = F30 cap.XIX pe ambele coloane —
#: {rândul F20: termenii F30}. Generatorul le respectă prin construcție (păzit de `core/test_bilant_f30.py`); coloana „An precedent”
#: completată manual se verifică la salvare (`neconcordante_f20_f30`).
NOMENCLATOR_CONCORDANTA_F20_F30 = {1: "+167", 4: "+188", 7: "+232+234+328+341", 8: "+235", 9: "+236"}
#: ABATERI de la listele formularului, fiecare cu motivul: {(secțiune, tip, rând): {termen din formular: ce face generatorul}}. Un termen
#: al formularului care lipsește din nomenclator fără să fie aici, sau unul în plus, oprește `core/test_bilant_formular.py`.
NOMENCLATOR_ABATERI_FORMULAR = {
    # „*) Conturi de repartizat după natura elementelor respective” — aplicația nu ține natura (scadența, destinația) pe analitic; fiecare
    # cont „de repartizat” stă pe UN rând, cel de mai jos (INTERPRETARE CU TEMEI, aceeași ca înainte de C12; de reconfirmat dacă apare o
    # normă care transează sau dacă aplicația începe să țină scadența):
    ("F10", "*", 301): {"+267*": "rd.03", "-296*": "rd.03"},          # creanțele imobilizate și ajustările lor: imobilizări financiare
    ("F10", "*", 8): {"+din508*": "rd.07"},                           # 508: investiții pe termen scurt
    ("F10", "*", 12): {"+471*": "rd.11"},                             # cheltuielile în avans: sub un an
    ("F10", "*", 16): "rd.13",                                        # datoriile: toate sub un an (aplicația nu ține scadența)
    ("F10", "*", 20): {"+din475*": "rd.21"},                          # subvențiile pentru investiții: peste un an
    ("F10", "*", 24): {"+din472*": "rd.23"},                          # veniturile în avans: sub un an
    ("F10", "*", 26): {"+din478*": "rd.27"},                          # activele primite de la clienți: peste un an
    ("F20", "s1005", 6): {"-609*": "rd.03"},                          # reducerile primite: toate la materii prime și consumabile
    # „741 **) Rd.01 - veniturile din subvenții de exploatare aferente cifrei de afaceri”, „741 ***) … altele decât cele aferente cifrei de
    # afaceri”: planul OMFP 1802/2014 le are pe analitice — 7411 („aferente cifrei de afaceri nete”) / 7412–7419 (S1003 rd.06 / rd.12, rd.49)
    ("F20", "s1005", 1): {"+741**": "+7411"},
    ("F20", "s1005", 2): {"+741***": "+7412+7413+7414+7415+7416+7417+7418+7419", "+711": "+/-711", "+712": "+/-712"},
    # S1003 (C10, deciziile Costin 12.10.2026): 6811 numai la 25a (rd.306) — altfel ar intra de două ori în rd.25; „din ct.6818 / 7818”
    # la b) — activele circulante (rd.29 / rd.30); rândurile „=null” ale formularului (rd.05 — 766*, rd.38 — 666*, rd.67 — 695) nu se scriu
    ("F20", "s1003", 26): {"+6811": "rd.306", "+6818": "rd.29"},
    ("F20", "s1003", 27): {"+7818": "rd.30"},
    ("F20", "s1003", 5): "=null", ("F20", "s1003", 38): "=null", ("F20", "s1003", 67): "=null",
    # F30 cap.XIX (C14), aceleași interpretări ca la S1003 (C10, deciziile Costin 12.10.2026): rd.191 = 191a (330) + 192 − 193, iar 191a =
    # 6811 — formularul tipărește 6811 și la a.2) (rd.192), deci 6811 numai la 191a; „din ct.6818 / 7818” la b) (rd.195 / 196). rd.197 =
    # 198 + … + 198a (331), iar 198a = 612 — formularul tipărește 612 și la 11.1 (rd.198), deci 612 numai la 198a (altfel de două ori în
    # rd.197, iar profitul n-ar mai fi cel din F20: DUK regula F20_F30_8).
    ("F30", "s1005", 192): {"+6811": "rd.330", "+din6818": "rd.195"},
    ("F30", "s1005", 193): {"+din7818": "rd.196"},
    ("F30", "s1005", 198): {"+612": "rd.331"},
    # rândurile „=null” ale cap.XIX (entitățile radiate cu leasing în derulare — 171 / 204 —, impozitul specific 695 — 233): nu se scriu
    ("F30", "s1005", 171): "=null", ("F30", "s1005", 204): "=null", ("F30", "s1005", 233): "=null",
}


def _valoare_termen(solduri, latura, semn, cont, cal, tva_stoc=False):
    """Contribuția unui termen al formularului (sold sau rulaj). `tva_stoc`: „din 4428” la stocuri = numai `CONT_TVA_STOC`."""
    pref = (CONT_TVA_STOC,) if tva_stoc else (cont,)
    d, c = _pe_prefix(solduri, pref, 0), _pe_prefix(solduri, pref, 1)
    if cal == "+/-":
        return (d - c) if latura == "d" else (c - d)
    if cal.endswith("***"):
        v = c
    elif cal.endswith("**"):
        v = d
    else:
        v = (d if semn == "+" else c) if latura == "d" else (c if semn == "+" else d)
    return v if semn == "+" else -v


def _acopera(latura, semn, cal):
    """Ce latură a soldului / rulajului unui cont o preia termenul: {"d", "c"}."""
    if cal == "+/-":
        return {"d", "c"}
    if cal.endswith("***"):
        return {"c"}
    if cal.endswith("**"):
        return {"d"}
    return {"d" if (latura == "d") == (semn == "+") else "c"}


def _randuri_din_nomenclator(nomenclator, solduri, tva_stoc_la=None):
    v = {}
    for rand, latura, lista in nomenclator:
        sold = solduri if rand == tva_stoc_la else _fara_tva_stoc(solduri)
        v[rand] = sum((_valoare_termen(sold, latura, s, c, q, tva_stoc=(rand == tva_stoc_la and c == "4428" and "din" in q))
                       for s, c, q in termeni(lista)), Decimal("0"))
    return v


def conturi_fara_rand(nomenclator, solduri, clase):
    """[(cont, latura "d"/"c", suma)] — soldurile (rulajele) din `clase` pe care nu le preia niciun rând: un sold pierdut strică egalitatea
    bilanțului (DUK regula F10_64), un rulaj pierdut — rezultatul."""
    acop = [(c, _acopera(lat, s, q)) for _r, lat, lista in nomenclator for s, c, q in termeni(lista)]
    out = []
    for cont, (d, c) in sorted((solduri or {}).items()):
        k = str(cont)
        if k[:1] not in clase:
            continue
        for latura, suma in (("d", Decimal(str(d or 0))), ("c", Decimal(str(c or 0)))):
            if suma and not any(k.startswith(p) and latura in l for p, l in acop):
                out.append((k, latura, suma))
    return out


#: [deficiența 233, comanda Costin 12.10.2026] TOTALURILE formularelor: {tip: {secțiune: {rând: (termeni, pozitiv)}}}. `termeni` în
#: sintaxa calculului din formular (`<calculate>` al rândului: „this=R01.C1+R02.C1+R03.C1” -> „+1+2+3”); `pozitiv` = rândul primește
#: valoarea numai dacă e pozitivă, altfel 0 („if (v1 > 0) this.rawValue = v1; else 0” — profitul / pierderea). Generatorul, completarea
#: manuală a coloanei „An precedent” și ecranul calculează totalurile de aici; `core/test_bilant_formular.py` le compară cu formularul.
_NOMENCLATOR_TOTALURI_F10 = {
    4: ("+1+2+3", False), 6: ("+301+302", False), 9: ("+5+6+7+8", False), 10: ("+11+12", False),
    14: ("+9+11-13-20-23-26", False), 15: ("+4+12+14", False), 18: ("+19+22+25+28", False), 19: ("+20+21", False),
    22: ("+23+24", False), 25: ("+26+27", False), 29: ("+30+31+32+33+34", False),
    46: ("+29+35+36+37-38+39-40+41-42+43-44-45", False), 49: ("+46+47+48", False),
}
NOMENCLATOR_TOTALURI = {
    "s1005": {"F10": _NOMENCLATOR_TOTALURI_F10,
              "F20": {8: ("+1+2-3-4-5-6-7+304", True), 9: ("-1-2+3+4+5+6+7-304", True)},
              # [C14] F30 cap.XIX: calculele formularului (`<calculate>` din `Table8_an_micro`; rândurile „=null” — 171, 204, 233 — nu intră)
              "F30": {167: ("+168+169-170+172", False), 182: ("+167+173-174+175+176+177+178+179", False), 188: ("+189+190", False),
                      191: ("+330+192-193", False), 194: ("+195-196", False),
                      197: ("+198+199+200+201+202+203+331+335+337+339", False), 205: ("+206-207", False),
                      208: ("+183+184+185+186-187+188+191+194+197+205", False), 209: ("+182-208", True), 210: ("-182+208", True),
                      218: ("+211+213+215+216", False), 219: ("+220-221", False), 225: ("+219+222+224", False),
                      226: ("+218-225", True), 227: ("-218+225", True), 228: ("+182+218", False), 229: ("+208+225", False),
                      230: ("+228-229", True), 231: ("-228+229", True),
                      235: ("+230+329-231-232-234-328-341", True), 236: ("-230-329+231+232+234+328+341", True)}},
    "s1003": {"F10": _NOMENCLATOR_TOTALURI_F10,
              "F20": {1: ("+2+3-4+6", False), 16: ("+1+7-8+9+10+11+12+13", False), 22: ("+23+24", False),
                      25: ("+306+26-27", False), 28: ("+29-30", False), 31: ("+32+33+34+35+36+37+310+312+314+316", False),
                      39: ("+40-41", False), 42: ("+17+18+19+20-21+22+25+28+31+39", False),
                      43: ("+16-42", True), 44: ("-16+42", True), 52: ("+45+47+49+50", False), 53: ("+54-55", False),
                      59: ("+53+56+58", False), 60: ("+52-59", True), 61: ("-52+59", True), 62: ("+16+52", False),
                      63: ("+42+59", False), 64: ("+62-63", True), 65: ("-62+63", True),
                      69: ("+64+305-65-66-68-304-317", True), 70: ("-64-305+65+66+68+304+317", True)}},
}


def termeni_total(expr):
    """„+9+11-13” -> [(1, 9), (1, 11), (-1, 13)]."""
    return [(1 if s == "+" else -1, int(r)) for s, r in re.findall(r"([+-])(\d+)", expr)]


def cu_totaluri(tip, sectiune, valori):
    """`valori` (rândurile componente, lei) + totalurile secțiunii calculate ca în formular; un total depinde și de alte totaluri (rd.15 =
    rd.04 + 12 + 14), deci se calculează la cerere, o singură dată. O componentă lipsă = 0 (rândul nescris în XML)."""
    tot = NOMENCLATOR_TOTALURI[tip].get(sectiune, {})
    out = {k: v for k, v in valori.items() if k not in tot}

    def val(r):
        if r not in out:
            if r in tot:
                expr, poz = tot[r]
                x = sum((s * val(k) for s, k in termeni_total(expr)), 0)
                out[r] = max(x, 0) if poz else x
            else:
                return 0
        return out[r]

    for r in tot:
        val(r)
    return out


def f10_din_balanta(s):
    """F10 — bilanțul prescurtat (S1005 și S1003), pe rândurile și listele de conturi ale formularului ANAF 2025 (`F10_NOMENCLATOR`) și
    totalurile lui (`NOMENCLATOR_TOTALURI`). `s` = soldurile finale la 31.12. Un sold pe care nu-l preia niciun rând (cont fără rând în
    formular, sau sold pe latura pe care formularul nu o cere — ex. 401 debitor) oprește generarea: bilanțul n-ar mai fi egal (DUK regula
    F10_64). Clasele 6 / 7 nu se citesc aici: rezultatul exercițiului e soldul lui 121, iar închiderea lor o cere `inchiderea_6_7` (C15)."""
    fara = conturi_fara_rand(F10_NOMENCLATOR, s, "12345")
    if fara:
        raise ValueError(motiv_f10(fara))
    v = _randuri_din_nomenclator(F10_NOMENCLATOR, s, tva_stoc_la=5)
    for r in (12, 16, 20, 24, 26):                     # NOMENCLATOR_ABATERI_FORMULAR: conturile lor stau pe rândul pereche
        v[r] = Decimal("0")
    return {k: _i(x) for k, x in cu_totaluri("s1005", "F10", v).items()}


#: [deficiența 238, retestul Costin 12.10.2026: „Rescrie-l pentru contabil, câte un rând pe cont, cu suma și acțiunea concretă, fără coduri
#: DUK”] ce face contabilul cu un sold pe care bilanțul nu-l preia: {(prefix de cont, latura „d” / „c” / „*”): (acțiunea, temeiul)}. Se
#: alege prefixul cel mai lung; temeiul e funcțiunea contului din OMFP 1802/2014 (`anaf_surse/omfp_1802_2014.txt`), citată, unde există.
#: Gardat de `core/test_bilant_formular.py`: fiecare cont al planului fără rând (pe latura lui) are aici o acțiune concretă.
_CONSOLIDARE = "„Acest cont apare numai în situațiile financiare anuale consolidate.”"
NOMENCLATOR_ACTIUNI_SOLD = {
    # conturile fără niciun rând în bilanțul prescurtat
    ("1033", "*"): ("contul apare numai în situațiile financiare consolidate, nu în bilanțul firmei; trece soldul pe contul potrivit "
                    "naturii lui", "OMFP 1802/2014, planul de conturi, contul 1033: " + _CONSOLIDARE),
    ("1038", "*"): ("contul apare numai în situațiile financiare consolidate, nu în bilanțul firmei; trece soldul pe contul potrivit "
                    "naturii lui", "OMFP 1802/2014, planul de conturi, contul 1038: " + _CONSOLIDARE),
    ("107", "*"): ("contul se folosește numai la consolidarea societăților nerezidente; trece soldul pe contul potrivit naturii lui",
                   "OMFP 1802/2014, contul 107: „se utilizează numai în situațiile financiare anuale consolidate”"),
    ("108", "*"): ("contul se folosește numai la consolidarea filialelor; trece soldul pe contul potrivit naturii lui",
                   "OMFP 1802/2014, contul 108: „se utilizează numai în situațiile financiare anuale consolidate”"),
    ("264", "*"): ("titlurile puse în echivalență apar numai în situațiile financiare consolidate; în bilanțul firmei participațiile stau "
                   "în 261, 262 sau 263", "OMFP 1802/2014, contul 264: participațiile „prezentate în situațiile financiare anuale "
                   "consolidate la valoarea determinată prin metoda punerii în echivalență”"),
    ("266", "*"): ("contul nu mai există în planul de conturi; trece soldul pe contul potrivit naturii lui (ex. 267 creanțe imobilizate)",
                   "OMFP 1802/2014: „Contul 266 - funcțiune eliminată.”"),
    ("4426", "*"): ("închide TVA-ul lunii: compensează-l cu 4427, iar diferența trece în 4423 (de plată) sau 4424 (de recuperat)",
                    "OMFP 1802/2014, contul 4426: „sumele compensate la sfârșitul perioadei din taxa pe valoarea adăugată colectată "
                    "(4427)”"),
    ("4427", "*"): ("închide TVA-ul lunii: compensează-l cu 4426, iar diferența trece în 4423 (de plată) sau 4424 (de recuperat)",
                    "OMFP 1802/2014, contul 4427: „taxa pe valoarea adăugată deductibilă, compensată la sfârșitul perioadei, potrivit "
                    "legii (4426)”"),
    ("481", "*"): ("decontările dintre firmă și subunitățile ei se compensează în bilanțul firmei: la 31.12 soldul trebuie să fie zero; "
                   "verifică transferurile neînregistrate la una din părți", "OMFP 1802/2014, contul 481: decontări „din cadrul unei "
                   "entități cu subunități fără personalitate juridică”"),
    ("482", "*"): ("decontările dintre subunitățile aceleiași firme se compensează în bilanțul firmei: la 31.12 soldul trebuie să fie "
                   "zero; verifică transferurile neînregistrate la una din părți", "OMFP 1802/2014, contul 482: decontări „între "
                   "subunitățile fără personalitate juridică din cadrul aceleiași unități”"),
    ("581", "*"): ("viramentele interne trebuie să aibă sold zero; înregistrează și intrarea banilor în contul de destinație (512, 531, "
                   "541)", "OMFP 1802/2014, contul 581: „De regulă, contul nu prezintă sold.”"),
    # soldurile pe latura nefirească a unui cont care are pereche în plan
    ("401", "d"): ("reclasifică în 409 (furnizori-debitori)", "OMFP 1802/2014, contul 409: „evidența avansurilor acordate furnizorilor”"),
    ("403", "d"): ("reclasifică în 409 (furnizori-debitori)", "OMFP 1802/2014, contul 409: „evidența avansurilor acordate furnizorilor”"),
    ("404", "d"): ("reclasifică în 409 (furnizori-debitori)", "OMFP 1802/2014, contul 409: „evidența avansurilor acordate furnizorilor”"),
    ("405", "d"): ("reclasifică în 409 (furnizori-debitori)", "OMFP 1802/2014, contul 409: „evidența avansurilor acordate furnizorilor”"),
    ("408", "d"): ("reclasifică în 409 (furnizori-debitori)", "OMFP 1802/2014, contul 409: „evidența avansurilor acordate furnizorilor”"),
    ("409", "c"): ("avansul decontat e mai mare decât cel plătit: reclasifică diferența în 401 (furnizori)", ""),
    ("411", "c"): ("reclasifică în 419 (clienți-creditori)", "OMFP 1802/2014, contul 419: „avansurile încasate de la clienți”"),
    ("413", "c"): ("reclasifică în 419 (clienți-creditori)", "OMFP 1802/2014, contul 419: „avansurile încasate de la clienți”"),
    ("418", "c"): ("reclasifică în 419 (clienți-creditori)", "OMFP 1802/2014, contul 419: „avansurile încasate de la clienți”"),
    ("419", "d"): ("avansul decontat e mai mare decât cel încasat: reclasifică diferența în 4111 (clienți)", ""),
    ("421", "d"): ("salariile plătite în plus sunt o creanță: reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                   "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("423", "d"): ("sumele plătite în plus sunt o creanță: reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                   "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("424", "d"): ("sumele plătite în plus sunt o creanță: reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                   "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("426", "d"): ("sumele plătite în plus sunt o creanță: reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                   "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("427", "d"): ("sumele plătite în plus sunt o creanță: reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                   "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("4281", "d"): ("reclasifică în 4282 (alte creanțe în legătură cu personalul)",
                    "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("4282", "c"): ("reclasifică în 4281 (alte datorii în legătură cu personalul)",
                    "OMFP 1802/2014, contul 428: „evidența altor datorii și creanțe în legătură cu personalul”"),
    ("4381", "d"): ("reclasifică în 4382 (alte creanțe sociale)", "OMFP 1802/2014, contul 438: „Alte datorii și creanțe sociale”"),
    ("4382", "c"): ("reclasifică în 4381 (alte datorii sociale)", "OMFP 1802/2014, contul 438: „Alte datorii și creanțe sociale”"),
    ("4423", "d"): ("TVA-ul plătit în plus e de recuperat: reclasifică în 4424 (TVA de recuperat)",
                    "OMFP 1802/2014, contul 4424: „evidența taxei pe valoarea adăugată de recuperat de la bugetul statului”"),
    ("4424", "c"): ("TVA-ul încasat în plus e de plată: reclasifică în 4423 (TVA de plată)",
                    "OMFP 1802/2014, contul 4423: „evidența taxei pe valoarea adăugată de plătit la bugetul statului”"),
    ("4481", "d"): ("reclasifică în 4482 (alte creanțe privind bugetul statului)",
                    "OMFP 1802/2014, contul 448: „evidența altor datorii și creanțe cu bugetul statului”"),
    ("4482", "c"): ("reclasifică în 4481 (alte datorii față de bugetul statului)",
                    "OMFP 1802/2014, contul 448: „evidența altor datorii și creanțe cu bugetul statului”"),
    ("4581", "d"): ("reclasifică în 4582 (decontări din operațiuni în participație — activ)",
                    "OMFP 1802/2014, contul 458: „evidența decontărilor din operațiuni în participație”"),
    ("4582", "c"): ("reclasifică în 4581 (decontări din operațiuni în participație — pasiv)",
                    "OMFP 1802/2014, contul 458: „evidența decontărilor din operațiuni în participație”"),
    ("461", "c"): ("reclasifică în 462 (creditori diverși)", "OMFP 1802/2014, contul 462: „evidența sumelor datorate terților”"),
    ("462", "d"): ("reclasifică în 461 (debitori diverși)", "OMFP 1802/2014, contul 461: „evidența debitorilor”"),
    ("4661", "d"): ("reclasifică în 4662 (creanțe din operațiuni de fiducie)", ""),
    ("4662", "c"): ("reclasifică în 4661 (datorii din operațiuni de fiducie)", ""),
    ("512", "c"): ("descoperitul de cont e un credit pe termen scurt: reclasifică în 519 (credite bancare pe termen scurt)",
                   "OMFP 1802/2014, contul 519: „evidența creditelor acordate de bănci pe termen scurt”"),
    ("531", "c"): ("casa nu poate avea sold creditor; verifică plățile și încasările în numerar înregistrate", ""),
    ("532", "c"): ("valorile de încasat nu pot avea sold creditor; verifică intrările și ieșirile lor", ""),
    ("541", "c"): ("acreditivele nu pot avea sold creditor; verifică intrările și ieșirile lor", ""),
    ("542", "c"): ("avansul de trezorerie decontat e mai mare decât cel dat: verifică decontul avansului", ""),
}
#: când nu e o pereche anume: după natura contului (prima cifră a grupei), pe latura nefirească
NOMENCLATOR_ACTIUNI_SOLD_GRUPE = {
    ("1", "d"): "un cont de capitaluri, provizioane sau împrumuturi nu are sold debitor; verifică înregistrările care l-au trecut pe debit",
    ("1", "c"): "contul nu are sold creditor; verifică înregistrările care l-au trecut pe credit",
    ("2", "c"): "o imobilizare nu are sold creditor; verifică intrările și ieșirile ei",
    ("2", "d"): "amortizarea sau ajustarea nu are sold debitor; verifică scoaterile din evidență și reluările",
    ("3", "c"): "stocul nu poate fi negativ; verifică recepțiile și descărcarea din gestiune",
    ("3", "d"): "ajustarea pentru depreciere nu are sold debitor; verifică reluările",
    ("4", "d"): "o datorie nu are sold debitor; verifică plățile și stornările contului",
    ("4", "c"): "o creanță nu are sold creditor; verifică încasările și stornările contului",
    ("5", "c"): "contul de trezorerie nu are sold creditor; verifică intrările și ieșirile lui",
    ("5", "d"): "o datorie sau o ajustare de trezorerie nu are sold debitor; verifică plățile și reluările contului",
}


def actiune_sold(cont, latura):
    """(acțiunea, temeiul) pentru un sold pe care bilanțul nu-l preia — perechea anume din `NOMENCLATOR_ACTIUNI_SOLD` (prefixul cel mai
    lung, pe latura lui sau „*”), altfel natura contului (`NOMENCLATOR_ACTIUNI_SOLD_GRUPE`)."""
    c = str(cont).split(".")[0]
    best = None
    for (p, l), v in NOMENCLATOR_ACTIUNI_SOLD.items():
        if c.startswith(p) and l in (latura, "*") and (best is None or len(p) > best[0]):
            best = (len(p), v)
    if best:
        return best[1]
    return NOMENCLATOR_ACTIUNI_SOLD_GRUPE[(c[0], latura)], ""


def _randuri_fara_loc(fara):
    from core.pdf_util import bani
    out = []
    for c, l, v in fara:
        act, temei = actiune_sold(c, l)
        out.append("• %s sold %s %s — %s.%s" % (c, "debitor" if l == "d" else "creditor", bani(v), act,
                                                (" " + temei + ("" if temei.endswith(".”") else ".")) if temei else ""))
    return out


def motiv_f10(fara):
    """[deficiența 238] Mesajul de oprire pentru contabil: câte un rând pe cont — contul, latura, suma, ce face, temeiul unde există."""
    return ("Bilanțul nu se poate genera: soldurile de la 31.12 de mai jos nu au loc în bilanț. Corectează-le, apoi generează din nou.\n"
            + "\n".join(_randuri_fara_loc(fara)))


#: [C15, decizia Costin 12.10.2026, varianta (c)] „Generarea bilanțului se oprește cu motivul «închide clasele 6/7 în 121 la 31.12», cu
#: suma rezultatului.” TEMEI: OMFP 1802/2014, funcțiunea contului 121 (`anaf_surse/omfp_1802_2014.txt`).
_TEMEI_121 = ("OMFP 1802/2014, contul 121: „În creditul contului 121 «Profit sau pierdere» se înregistrează: la sfârșitul perioadei, "
              "soldul creditor al conturilor din clasa 7 (701 la 786)”; „În debitul contului 121 «Profit sau pierdere» se înregistrează: la "
              "sfârșitul perioadei, soldul debitor al conturilor de cheltuieli (601 la 698)”")


def conturi_6_7_cu_sold(s):
    """[(cont, latura, suma)] — conturile din clasele 6 și 7 cu sold la data lui `s` (după închidere, niciunul)."""
    out = []
    for cont, (d, c) in sorted((s or {}).items()):
        net = Decimal(str(d or 0)) - Decimal(str(c or 0))
        if str(cont)[:1] in "67" and net:
            out.append((str(cont), "d" if net > 0 else "c", abs(net)))
    return out


class BilantOprit(ValueError):
    """[C15, 242] Refuzul bilanțului la 31.12, cu TOATE motivele deodată. `an` = anul la 31.12 căruia se închid clasele 6 / 7 (pentru
    propunerea notei de închidere — varianta (a)); `inchidere` = unul din motive e închiderea 6 / 7."""

    def __init__(self, mesaj, an=None, inchidere=False, ani_inchidere=None, propuse=None):
        super().__init__(mesaj)
        self.an, self.inchidere = an, inchidere
        self.ani_inchidere = list(ani_inchidere) if ani_inchidere is not None else ([an] if inchidere else [])
        #: [244] propunerile care așteaptă validarea (`inchidere_an.ciorne`): ecranul pune legătura spre Registrul jurnal pe luna lor
        self.propuse = list(propuse or [])


def refuz_impreuna(oprite):
    """[deficiența 242] Refuzurile ambilor ani (coloana „An precedent” din evidență și „An curent”) într-unul singur."""
    if len(oprite) == 1:
        raise oprite[0]
    if oprite:
        raise BilantOprit("\n\n".join(str(e) for e in oprite), an=oprite[-1].an, inchidere=any(e.inchidere for e in oprite),
                          ani_inchidere=sorted({a for e in oprite for a in e.ani_inchidere}),
                          propuse=[p for e in oprite for p in e.propuse])


def _text_6_7(cu_sold, an, incheiat=True):
    """`incheiat` = False [243]: anul nu s-a încheiat — nu se cere închiderea acum, se spune când se face."""
    from core.pdf_util import bani
    rez = sum(((v if l == "c" else -v) for _c, l, v in cu_sold), Decimal("0"))
    ce = "profit %s lei" % bani(rez) if rez > 0 else ("pierdere %s lei" % bani(-rez) if rez < 0 else "rezultat zero (0,00 lei)")
    conturi = "\n".join("• %s sold %s %s" % (c, "debitor" if l == "d" else "creditor", bani(v)) for c, l, v in cu_sold)
    if not incheiat:
        return ("anul %d nu s-a încheiat — clasele 6/7 se închid în 121 la 31.12.%d, iar nota de închidere se propune după această dată "
                "(până atunci urmează operațiuni care schimbă soldurile). Rezultatul de până acum: %s. %s.\nConturile cu sold:\n%s"
                % (an, an, ce, _TEMEI_121, conturi))
    return ("închide clasele 6/7 în 121 la 31.12.%d. Rezultatul de închis: %s (veniturile minus cheltuielile cu sold la 31.12.%d). Până la "
            "închidere, rezultatul exercițiului nu e în contul 121, deci lipsește din bilanț. %s.\nConturile cu sold:\n%s"
            % (an, ce, an, _TEMEI_121, conturi))


def inchiderea_6_7(s, an, bilant_pe=None):
    """[C15] Bilanțul pe `an` cere clasele 6 / 7 închise în 121 la 31.12: altfel rezultatul exercițiului nu e în 121, deci lipsește din
    bilanț (rd.43 / 44) — și bilanțul n-ar fi egal. `s` = soldurile la 31.12.`an`; `bilant_pe` = anul bilanțului (an + 1 pentru coloana
    „An precedent” din evidență). Refuzul spune rezultatul de închis și conturile."""
    cu_sold = conturi_6_7_cu_sold(s)
    if cu_sold:
        raise BilantOprit("Bilanțul pe %d nu se poate genera: %s" % (bilant_pe or an, _text_6_7(cu_sold, an)), an=an, inchidere=True)


def _text_propuse(p):
    """[244] Clasele 6 / 7 au încă sold, iar notele de închidere sunt propuse: motivul e validarea lor, nu o nouă închidere."""
    an, note = p["an"], "; ".join("%s (nota %s)" % (n["descriere"], n["eticheta"]) for n in p["note"])   # [258] nu id-ul intern
    t = "Notele de închidere propuse așteaptă validarea: %s. Se validează în Registrul jurnal, luna decembrie %d" % (note, an)
    if not p["incheiat"]:
        return t + (". Anul %d nu s-a încheiat: se validează numai după 31.12.%d, dacă mai corespund atunci soldurilor; până atunci "
                    "operațiunile anului le pot schimba." % (an, an))
    if not p["la_zi"]:
        return t + (", dar nu mai corespund soldurilor de la 31.12.%d din notele validate (după propunere s-au validat operațiuni ale "
                    "anului sau notele au fost modificate): propune-le din nou — butonul de mai jos le recalculează." % an)
    return t + "; apoi generează bilanțul."


def motive_31_12(s, an, propuse=None, incheiat=True, s_dupa=None):
    """[deficiența 242] Motivele de oprire din soldurile la 31.12.`an`, TOATE: [{"fel", "titlu", "text"}] — clasele 6 / 7 neînchise (C15),
    soldurile fără loc în bilanț (238). Lista goală = soldurile permit bilanțul.
    [243, 244] `propuse` = propunerea care așteaptă validarea (`inchidere_an.ciorne`): atunci motivul e validarea ei („inchidere_propusa”),
    cu propunerea din nou numai când nu mai corespunde soldurilor; `incheiat` = False: anul nu s-a încheiat, propunerea nu se oferă;
    `s_dupa` = soldurile după notele propuse (`inchidere_an.solduri_dupa`): soldurile fără loc se spun pe ele."""
    out = []
    cu_sold = conturi_6_7_cu_sold(s)
    if cu_sold and propuse:
        out.append({"fel": "inchidere_propusa", "titlu": "Clasele 6 / 7", "text": _text_propuse(propuse), "simplu": _text_propuse(propuse),
                    "propuse": propuse, "din_nou": propuse["incheiat"] and not propuse["la_zi"]})
    elif cu_sold:
        out.append({"fel": "inchidere_6_7" if incheiat else "an_neincheiat", "titlu": "Clasele 6 / 7",
                    "text": _text_6_7(cu_sold, an, incheiat=incheiat)})
    fara = conturi_fara_rand(F10_NOMENCLATOR, s if s_dupa is None else s_dupa, "12345")
    if fara:
        out.append({"fel": "fara_loc", "titlu": "Soldurile de la 31.12 de mai jos nu au loc în bilanț",
                    "text": "\n".join(_randuri_fara_loc(fara)), "simplu": motiv_f10(fara)})
    return out


def refuz(motive, an, bilant_pe=None):
    """[deficiența 242] Un singur refuz cu toate motivele: unul -> textul lui (ca până acum); mai multe -> numerotate, fiecare cu acțiunea
    lui, ca să se rezolve dintr-o singură trecere."""
    if not motive:
        return
    inchidere = any(m["fel"] == "inchidere_6_7" or m.get("din_nou") for m in motive)
    propuse = [m["propuse"] for m in motive if m["fel"] == "inchidere_propusa"]
    if len(motive) == 1:
        m = motive[0]
        mesaj = m.get("simplu") or "Bilanțul pe %d nu se poate genera: %s" % (bilant_pe or an, m["text"])
    else:
        mesaj = ("Bilanțul pe %d nu se poate genera — %s; rezolvă-le pe toate, apoi generează din nou.\n" % (bilant_pe or an, _cate(len(motive), "motiv", "motive"))
                 + "\n".join("%d. %s:%s%s" % (i, m["titlu"], "\n" if m["fel"] == "fara_loc" else " ", m["text"])
                             for i, m in enumerate(motive, start=1)))
    raise BilantOprit(mesaj, an=an, inchidere=inchidere, propuse=propuse)


def verifica_31_12(s, an, bilant_pe=None):
    """Soldurile la 31.12.`an` permit bilanțul? Altfel refuzul cu toate motivele lor (`motive_31_12` + `refuz`)."""
    refuz(motive_31_12(s, an), an, bilant_pe)


#: [C13, C14] sinteticele planului OMFP 1802/2014 ale căror analitice stau pe rânduri DIFERITE ale S1005 — F20 sau F30 cap.XIX (rândurile
#: de mai jos sunt ale cap.XIX, mai detaliat: el desparte și 658, 681, 761, pe care F20 le ține pe un rând). Aceeași regulă ca la S1003
#: (decizia Costin 12.10.2026, reconfirmată seara: „741 fără analitic: … Generarea se oprește și cere contul analitic.”); păzit de
#: `core/test_bilant_f30.py` (= lista calculată din plan cu `rand_f20_s1005` și `rand_f30_s1005`).
S1005_NOMENCLATOR_SINTETICE = {
    "658": (("6581", 203), ("6582", 203), ("6583", 203), ("6584", 203), ("6586", 199), ("6587", 202), ("6588", 203)),
    "681": (("6811", 330), ("6812", 206), ("6813", 192), ("6814", 195), ("6817", 192), ("6818", 195)),
    "741": (("7411", 172), ("7412", 178), ("7413", 178), ("7414", 178), ("7415", 178), ("7416", 178), ("7417", 178), ("7418", 215),
            ("7419", 178)),
    "761": (("7611", 211), ("7612", 211), ("7613", 211), ("7615", 216)),
    "781": (("7812", 207), ("7813", 193), ("7814", 196), ("7815", 179), ("7818", 196)),
}


def rand_f20_s1005(cont):
    """Rândul F20 S1005 pe care intră `cont` (prefixul listat cel mai lung care îl cuprinde) sau None."""
    c = str(cont).split(".")[0]
    best = None
    for rand, _lat, lista in F20_S1005_NOMENCLATOR:
        for _s, p, _q in termeni(lista):
            if c.startswith(p) and (best is None or len(p) > best[0]):
                best = (len(p), rand)
    return best[1] if best else None


def f20_din_rulaje(rl):
    """F20 S1005 — contul prescurtat de profit și pierdere al microentităților, pe rândurile și listele de conturi ale formularului ANAF
    2025 (`F20_S1005_NOMENCLATOR`, rd.01–07, 07a = 304, „din care” 302 / 303) și rd.08 / 09 din calculul lui (`NOMENCLATOR_TOTALURI`).
    `rl` = {cont: (rulaj debitor, rulaj creditor)} pe anul bilanțului. Un cont fără rând sau un sintetic cu analitice pe rânduri diferite
    oprește generarea (`ValueError`, cu motivul) — ca la S1003."""
    rl = rl or {}
    sintetice = sorted({str(c).split(".")[0] for c in rl if str(c).split(".")[0] in S1005_NOMENCLATOR_SINTETICE})
    if sintetice:
        raise ValueError("Bilanțul S1005: " + " ".join(motiv_sintetic(c, S1005_NOMENCLATOR_SINTETICE, "F30 ") for c in sintetice))
    fara = sorted(str(c) for c in rl if rand_f20_s1005(c) is None)
    if fara:
        raise ValueError("Bilanțul S1005: contul %s nu are rând în contul prescurtat de profit și pierdere al formularului ANAF 2025 — "
                         "rulajul lui nu se poate depune; reclasează-l pe un cont al planului OMFP 1802/2014." % ", ".join(fara))
    v = _randuri_din_nomenclator(F20_S1005_NOMENCLATOR, rl)
    v.update(_randuri_din_nomenclator(F20_S1005_NOMENCLATOR_DIN_CARE, rl))
    return {k: _i(x) for k, x in cu_totaluri("s1005", "F20", v).items()}


#: F30 cap.I, rândurile 01–03 („Unități care au înregistrat profit / pierdere / nici profit nici pierdere”): coloana 1 = numărul, coloana 2
#: = suma — nu „an precedent / an curent”
F30_RANDURI_CAP_I = (1, 2, 3)


def rand_f30_s1005(cont):
    """Rândul F30 cap.XIX pe care intră `cont` (prefixul listat cel mai lung care îl cuprinde) sau None; 711 / 712 -> 173 (sold C / D)."""
    c = str(cont).split(".")[0]
    if c.startswith(F30_S1005_VARIATIA_STOCURILOR):
        return 173
    best = None
    for rand, _lat, lista in F30_S1005_NOMENCLATOR:
        for _s, p, _q in termeni(lista):
            if c.startswith(p) and (best is None or len(p) > best[0]):
                best = (len(p), rand)
    return best[1] if best else None


def f30_din_rulaje(rl):
    """[C14] F30 cap.XIX S1005 — situația veniturilor și cheltuielilor, pe rândurile și listele de conturi ale formularului ANAF 2025
    (`F30_S1005_NOMENCLATOR`, „din care” `F30_S1005_NOMENCLATOR_DIN_CARE`) și totalurile lui (`NOMENCLATOR_TOTALURI["s1005"]["F30"]`).
    `rl` = {cont: (rulaj debitor, rulaj creditor)} pe anul bilanțului. Refuzurile sunt ale lui `f20_din_rulaje` (cont fără rând, sintetic
    cu analitice pe rânduri diferite) — aceleași conturi, aceeași generare."""
    rl = rl or {}
    v = _randuri_din_nomenclator(F30_S1005_NOMENCLATOR, rl)
    net = sum(((Decimal(str(c or 0)) - Decimal(str(d or 0))) for k, (d, c) in rl.items()
               if str(k).split(".")[0].startswith(F30_S1005_VARIATIA_STOCURILOR)), Decimal("0"))
    v[173], v[174] = (net, Decimal("0")) if net > 0 else (Decimal("0"), -net)
    v.update(_randuri_din_nomenclator(F30_S1005_NOMENCLATOR_DIN_CARE, rl))
    return {k: _i(x) for k, x in cu_totaluri("s1005", "F30", v).items()}


def neconcordante_f20_f30(f20, f30):
    """[(rândul F20, valoarea F20, termenii F30, valoarea F30)] — rândurile pe care F20 S1005 și F30 cap.XIX nu se potrivesc (DUK S1005,
    regulile F20_F30_1–10: `NOMENCLATOR_CONCORDANTA_F20_F30`)."""
    out = []
    for r, expr in NOMENCLATOR_CONCORDANTA_F20_F30.items():
        x = sum(s * int((f30 or {}).get(k, 0) or 0) for s, k in termeni_total(expr))
        if int((f20 or {}).get(r, 0) or 0) != x:
            out.append((r, int((f20 or {}).get(r, 0) or 0), expr, x))
    return out


def _a(nume, val):
    from xml.sax.saxutils import quoteattr
    # ANAF respinge "atribut prezent dar vid" (dovedit 15.07.2026 pe regCom/banca/cont).
    # Un atribut fara valoare se OMITE, nu se scrie gol: altfel contabilul primeste o
    # eroare criptica de la validator in loc sa afle ce camp sa completeze in profil.
    if val is None or str(val).strip() == "":
        return ""
    return ' %s=%s' % (nume, quoteattr(str(val)))

def xml_s1005(prof, an, f10p, f10c, f20p, f20c, f30p=None, f30c=None, rezultat=None):
    """XML S1005 v15. f10p/f20p/f30p = an precedent (dict rd->val), f10c/f20c/f30c = an curent; f30 = F30 cap.XIX (C14, numai S1005).
    `rezultat` = (profitul, pierderea) exercițiului pentru F30 rd.01–03 — implicit F20 S1005 rd.08 / 09; S1003 dă rd.69 / 70 (C16).

    VERIFICAT 15.07.2026 pe validatorul instalat (S1005_41): v15 e acceptata, v14 e
    RESPINSA (eroare de namespace). Docstringul zicea v14 desi codul genera v15.
    Nota: `strings` pe S1005Validator.jar arata doar v14 - versiunea acceptata se
    construieste dinamic in validator. Absenta dintr-un extras NU inseamna absenta;
    singura dovada e rularea validatorului pe XML real."""
    NS = "mfp:anaf:dgti:s1005:declaratie:v15"
    at = []
    at.append(_a("luna", 12)); at.append(_a("an", an))
    at.append(_a("cui", prof.get("cui_numeric")))
    at.append(_a("den", prof.get("nume") or ""))
    if prof.get("adresa"): at.append(_a("adresa", prof["adresa"]))
    at.append(_a("regCom", prof.get("reg_com") or ""))
    at.append(_a("caen", prof.get("caen"))); at.append(_a("caenE", prof.get("caen")))
    at.append(_a("bifa_aprob", 1)); at.append(_a("AN_CAEN", an))
    at.append(_a("bifaMC", 1)); at.append(_a("bifaDD", 0))
    at.append(_a("bifaGG", 0)); at.append(_a("bifaAA", 0))
    at.append(_a("bifa_art27", 0)); at.append(_a("tipBIL", "UU"))
    at.append(_a("interes_public", 0))
    at.append(_a("codTT", prof.get("cod_judet") or 40))
    at.append(_a("codJJ", 10)); at.append(_a("codPP", 35))
    at.append(_a("nume_admin", prof.get("declarant_nume") or "ADMINISTRATOR"))
    at.append(_a("nume_intocmit", prof.get("intocmit_nume") or prof.get("declarant_nume") or "ADMINISTRATOR"))
    at.append(_a("calit_intocmit", prof.get("calit_intocmit") or 12))
    if prof.get("cif_intocmit"): at.append(_a("cif_intocmit", prof["cif_intocmit"]))
    at.append(_a("totalPlata_A", f10c.get(49, 0)))
    # Atribute F<tag>_<rand><col>: randul pe 3 CIFRE, apoi coloana (1=an precedent,
    # 2=an curent). Ex: rand 6 -> F10_0061; rand 301 -> F10_3011; rand 302 -> F10_3021
    # (creante, componentele lui F10_0061 - DUK regula F10_68 / DUK regula F10_69: F10_0061 =
    # F10_3011 + F10_3021). Vechea formatare ("F10_0" + str(k) pentru k>=100) producea
    # F10_03011 in loc de F10_3011 - "atribut necunoscut" in XSD + DUK regula F10_68 pica
    # (F10_3011/F10_3021 lipseau, deci suma iesea 0 != 19040). Dovedit pe validatorul
    # oficial S1005/S1003 (16.07.2026, XSD ~/duk/xsd/s1005_20260312.xsd).
    def bloc(tag, dp, dc):
        a = []
        for k in sorted(set(dp) | set(dc)):
            v1, v2 = dp.get(k, 0), dc.get(k, 0)
            if v1: a.append(_a("F%s_%03d1" % (tag, k), v1))
            if v2: a.append(_a("F%s_%03d2" % (tag, k), v2))
        return "".join(a)
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<Bilant1005 xmlns="%s"%s>' % (NS, "".join(at)))
    H.append('  <F10%s/>' % bloc("10", f10p, f10c))
    H.append('  <F20%s/>' % bloc("20", f20p, f20c))
    # F30 date informative minime: rd1/2 = unitati cu profit/pierdere (col1=nr, col2=suma), rd3 idem 0 — DUK S1005: „Daca F20_0082 > 0
    # atunci F30_0011 = 1, F30_0012 = F20_0082”. [C16] rezultatul e al formularului: la S1003, rd.08 / 09 sunt variația stocurilor (sold D)
    # și producția de imobilizări, nu profitul / pierderea — acolo vin rd.69 / 70 (`xml_s1003`).
    pr, pi = rezultat if rezultat is not None else (f20c.get(8, 0), f20c.get(9, 0))
    f30 = []
    f30.append(_a("F30_0011", 1 if pr > 0 else 0)); f30.append(_a("F30_0012", pr))
    f30.append(_a("F30_0021", 1 if pi > 0 else 0)); f30.append(_a("F30_0022", pi))
    f30.append(_a("F30_0031", 1 if (pr == 0 and pi == 0) else 0)); f30.append(_a("F30_0032", 0))
    # [C14] F30 cap.XIX (situația veniturilor și cheltuielilor), pe ambele coloane, ca F10 / F20
    H.append('  <F30%s%s/>' % ("".join(f30), bloc("30", f30p or {}, f30c or {})))
    H.append('</Bilant1005>')
    return "\n".join(H)


# ── F20 S1003 (contul de profit și pierdere al entităților mici) — [C10, comanda Costin 12.10.2026, verbatim în DECIZII] „rescrie F20
# din S1003 pe numerotarea formularului ANAF (70 de rânduri), cu denumirile oficiale.” SURSA: FORMULARUL oficial 2025 („soft A”,
# `anaf_surse/bilant_SC_1225_XML_270326.pdf`, tabelul `form1.F20` pe care scriptul formularului îl folosește la S1002 și S1003):
# conturile tipărite pe fiecare rând și calculele lui (`<calculate>`), citite în șablonul XFA. Unde textul structurii
# (`structura_SC_1225_270126.pdf`) diferă, formularul câștigă: rd.32 (11.1) fără 612; rd.33 (11.2) = 612 — în structură o copie a lui
# 11.6; rd.24 (9.b) = 645 + 646; rd.01 = rd.02 + 03 − 04 + 06 (fără rd.05).
# Fiecare cont din rulaje merge pe UN rând: cel al prefixului listat CEL MAI LUNG care îl cuprinde (6586 -> 11.6, 6587 -> 11.9, 7411 ->
# rd.06, 7418 -> rd.49). Un cont fără rând, sau un sintetic cu analitice pe rânduri diferite, oprește generarea (`ValueError`, cu motivul).
# INTERPRETĂRI CU TEMEI (formularul s-ar contrazice altfel):
#   · rd.26 (a.2) tipărește „6811 + 6813 + 6817 + din ct.6818”, iar rd.25 = 25a + 26 − 27 cu 25a = 6811: 6811 ar intra de două ori, deci
#     6811 numai la 25a (rândul 306);
#   · „din ct.6818” / „din ct.7818” se repartizează „după natura elementelor” (nota formularului): la noi, la b) — activele circulante
#     (rd.29 / rd.30); rd.26 / rd.27 primesc numai 6813 + 6817 / 7813;
#   (ambele confirmate de Costin, 12.10.2026)
# [decizia Costin 12.10.2026, verbatim în DECIZII] „Pentru 741 și 658 folosite sintetic, fără analitic: nu ghicim rândul. Generarea S1003
# se oprește, cu motivul și contul analitic cerut, la fel ca la contul fără rând.” Clasa: orice SINTETIC al cărui analitice stau pe rânduri
# diferite (F20_S1003_NOMENCLATOR_SINTETICE, derivat din planul OMFP 1802/2014) — 658, 681, 741, 761, 781.
# Rândurile „=null” ale formularului (rd.05, rd.38, rd.67, rd.318) nu se scriu; „din care … afiliate” și rd.301 (activitatea
# preponderentă) nu se pot ști din rulaje — nu se scriu (ANAF le acceptă absente).
#: (rând, latura, prefixe) — latura: "c" rulajul creditor, "d" rulajul debitor, "n" soldul net creditor (711, 712 -> rd.07 / rd.08)
F20_S1003_NOMENCLATOR = (
    (2, "c", ("701", "702", "703", "704", "705", "706", "708")),
    (3, "c", ("707",)),
    (4, "d", ("709",)),
    (6, "c", ("7411",)),
    (7, "n", ("711", "712")),
    (9, "c", ("721", "722")),
    (10, "c", ("755",)),
    (11, "c", ("725",)),
    (12, "c", ("7412", "7413", "7414", "7415", "7416", "7417", "7419")),
    (13, "c", ("751", "758", "7815")),
    (17, "d", ("601", "602")),
    (18, "d", ("603", "604", "606", "608")),
    (19, "d", ("605",)),
    (20, "d", ("607",)),
    (21, "c", ("609",)),
    (23, "d", ("641", "642", "643", "644")),
    (24, "d", ("645", "646")),
    (306, "d", ("6811",)),
    (26, "d", ("6813", "6817")),
    (27, "c", ("7813",)),
    (29, "d", ("654", "6814", "6818")),
    (30, "c", ("754", "7814", "7818")),
    (32, "d", ("611", "613", "614", "615", "621", "622", "623", "624", "625", "626", "627", "628")),
    (33, "d", ("612",)),
    (310, "d", ("616",)),
    (312, "d", ("617",)),
    (314, "d", ("618",)),
    (316, "d", ("635", "6586")),
    (34, "d", ("652",)),
    (35, "d", ("655",)),
    (36, "d", ("6587",)),
    (37, "d", ("651", "6581", "6582", "6583", "6584", "6588")),
    (40, "d", ("6812",)),
    (41, "c", ("7812",)),
    (45, "c", ("7611", "7612", "7613")),
    (47, "c", ("766",)),
    (49, "c", ("7418",)),
    (50, "c", ("762", "764", "765", "767", "768", "7615")),
    (54, "d", ("686",)),
    (55, "c", ("786",)),
    (56, "d", ("666",)),
    (58, "d", ("663", "664", "665", "667", "668")),
    (66, "d", ("691",)),
    (304, "d", ("694",)),
    (305, "c", ("794",)),
    (317, "d", ("697",)),
    (68, "d", ("698",)),
)
#: „din care” — părți ale unui rând de mai sus, nu componente ale totalurilor
F20_S1003_NOMENCLATOR_DIN_CARE = (
    (14, "c", ("7584",)), (15, "c", ("7815",)), (51, "c", ("7615",)),
    (302, "d", ("6051",)), (303, "d", ("6053",)),
    (307, "d", ("6121",)), (308, "d", ("6122",)), (309, "d", ("6123",)),
)
#: sinteticele planului OMFP 1802/2014 ale căror analitice stau pe rânduri DIFERITE: un rulaj pe sintetic (sau pe un analitic al aplicației,
#: „741.01”) nu spune rândul — generarea se oprește și cere analiticul. {sintetic: ((analitic, rând), …)}; păzit de
#: `core/test_bilant_s1003_f20.py` (= lista calculată din plan cu `rand_f20_s1003`).
F20_S1003_NOMENCLATOR_SINTETICE = {
    "658": (("6581", 37), ("6582", 37), ("6583", 37), ("6584", 37), ("6586", 316), ("6587", 36), ("6588", 37)),
    "681": (("6811", 306), ("6812", 40), ("6813", 26), ("6814", 29), ("6817", 26), ("6818", 29)),
    "741": (("7411", 6), ("7412", 12), ("7413", 12), ("7414", 12), ("7415", 12), ("7416", 12), ("7417", 12), ("7418", 49), ("7419", 12)),
    "761": (("7611", 45), ("7612", 45), ("7613", 45), ("7615", 50)),
    "781": (("7812", 41), ("7813", 27), ("7814", 30), ("7815", 13), ("7818", 30)),
}


def motiv_sintetic(sintetic, tabel=None, sectiune=""):
    """Motivul refuzului pentru un rulaj pe `sintetic`, cu analiticele cerute grupate pe rândul formularului (`tabel`: S1003 implicit;
    `sectiune` = prefixul rândului, „F30 ” la S1005, unde rândurile sunt ale cap.XIX)."""
    pe_rand = {}
    for analitic, rand in (tabel or F20_S1003_NOMENCLATOR_SINTETICE)[sintetic]:
        pe_rand.setdefault(rand, []).append(analitic)
    rd = lambda r: "%srd.%s" % (sectiune, ("%02d" % r) if r < 100 else r)   # noqa: E731
    return ("contul %s e folosit sintetic, fără analitic, iar formularul ANAF îi pune analiticele pe rânduri diferite: %s. Trece rulajul "
            "pe analiticul potrivit — iConta.eu nu alege rândul în locul tău."
            % (sintetic, "; ".join("%s (%s)" % (", ".join(a), rd(r)) for r, a in pe_rand.items())))


#: rânduri „=null” în formular (nu se scriu); 695 (impozitul specific, rd.67 „=null”) nu are rând — un rulaj pe el oprește generarea
F20_S1003_NOMENCLATOR_NULL = (5, 38, 67, 318)


def rand_f20_s1003(cont):
    """(rând, latura) pe care intră `cont` — prefixul listat cel mai lung care îl cuprinde — sau None."""
    c = str(cont).split(".")[0]
    best = None
    for rand, lat, prefixe in F20_S1003_NOMENCLATOR:
        for p in prefixe:
            if c.startswith(p) and (best is None or len(p) > best[0]):
                best = (len(p), rand, lat)
    return (best[1], best[2]) if best else None


def f20_complet_din_rulaje(rl):
    """F20 S1003 pe rândurile formularului ANAF 2025: {rând: lei întregi}. `rl` = {cont: (rulaj debitor, rulaj creditor)} pe anul
    bilanțului (`bilant_api._rulaje_67`). Totalurile urmează calculele formularului (`<calculate>` din șablonul XFA, citate pe fiecare)."""
    D = Decimal
    v = {r: D("0") for r, _l, _p in F20_S1003_NOMENCLATOR}
    v[8] = D("0")
    sintetice = sorted({str(c).split(".")[0] for c in (rl or {}) if str(c).split(".")[0] in F20_S1003_NOMENCLATOR_SINTETICE})
    if sintetice:
        raise ValueError("Bilanțul S1003: " + " ".join(motiv_sintetic(c) for c in sintetice))
    fara_rand = []
    for cont, (deb, cred) in (rl or {}).items():
        rr = rand_f20_s1003(cont)
        if rr is None:
            fara_rand.append(str(cont))
            continue
        rand, lat = rr
        if lat == "c":
            v[rand] += D(str(cred))
        elif lat == "d":
            v[rand] += D(str(deb))
        else:
            v[rand] += D(str(cred)) - D(str(deb))
    if fara_rand:
        raise ValueError("Bilanțul S1003: contul %s nu are rând în contul de profit și pierdere al formularului ANAF 2025 — rulajul lui "
                         "nu se poate depune; reclasează-l pe un cont al planului OMFP 1802/2014." % ", ".join(sorted(fara_rand)))
    sold = v.pop(7)
    v[7], v[8] = (sold, D("0")) if sold > 0 else (D("0"), -sold)
    for rand, lat, prefixe in F20_S1003_NOMENCLATOR_DIN_CARE:
        v[rand] = sum((D(str(cred if lat == "c" else deb)) for cont, (deb, cred) in (rl or {}).items()
                       if str(cont).split(".")[0].startswith(prefixe)), D("0"))
    # totalurile = calculele formularului (`NOMENCLATOR_TOTALURI`, păzit de core/test_bilant_formular.py); rândurile „din care … afiliate”
    # (46, 48, 57) nu se pot ști din rulaje și nu se scriu; R67 („=null”) nu intră în R69 / R70
    return {k: _i(x) for k, x in cu_totaluri("s1003", "F20", v).items()}


def xml_s1003(prof, an, f10p, f10c, f20p, f20c):
    """XML S1003 (mici) v15 - aceeasi structura antet ca S1005, tipBIL=BS."""
    x = xml_s1005(prof, an, f10p, f10c, f20p, f20c, rezultat=(f20c.get(69, 0), f20c.get(70, 0)))   # [C16] profitul / pierderea netă
    x = x.replace("mfp:anaf:dgti:s1005:declaratie:v15", "mfp:anaf:dgti:s1003:declaratie:v15")
    x = x.replace("<Bilant1005", "<Bilant1003").replace("</Bilant1005>", "</Bilant1003>")
    x = x.replace('tipBIL="UU"', 'tipBIL="BS"')
    return x


def randuri_din_xml(xml):
    """[deficiența 188, retestul Costin 09.10.2026: „rândurile bilanțului (F10_0052, F10_0132 și restul) apar pe ecranul Bilanț, cu cifrele
    care se depun, nu doar verdictul”] Rândurile CITITE din XML-ul care se depune (nu recalculate): [{formular, rand, cod_precedent,
    an_precedent, cod_curent, an_curent}], în ordinea formularului. Codul atributului e `F<formular>_<rând pe 3 cifre><coloana>`
    (1 = an precedent, 2 = an curent — `xml_s1005`). [deficiența 227, comanda Costin 12.10.2026] fiecare rând poartă și denumirea de pe
    formular (`core/bilant_denumiri.py`, extrasă din formularul ANAF), după formularul din rădăcina XML-ului (Bilant1003 / Bilant1005).
    [deficiența 234] în ORDINEA formularului (06a, 06b înaintea totalului 06) și cu codul tipărit pe el („06a (301)”)."""
    from core.bilant_denumiri import NOMENCLATOR_COD, NOMENCLATOR_DENUMIRI, NOMENCLATOR_ORDINE
    tip = "s1003" if "<Bilant1003" in (xml or "") else "s1005"
    den, cod, ordine = NOMENCLATOR_DENUMIRI[tip], NOMENCLATOR_COD[tip], NOMENCLATOR_ORDINE[tip]
    out = {}
    for f, r, col, v in re.findall(r'\b(F\d\d)_(\d{3})([12])="(-?\d+)"', xml or ""):
        d = out.setdefault((f, int(r)), {"formular": f, "rand": int(r), "denumire": den.get(f, {}).get(int(r), ""),
                                          # [C14] pe doi ani (an precedent / an curent): F10, F20 și F30 cap.XIX; F30 rd.01–03 (unități cu
                                          # profit / pierdere) au alte coloane (numărul și suma)
                                          "doi_ani": not (f == "F30" and int(r) in F30_RANDURI_CAP_I),
                                          "cod": cod.get(f, {}).get(int(r), r[1:] if r.startswith("0") else r),
                                          "cod_precedent": "%s_%s1" % (f, r), "an_precedent": 0,
                                          "cod_curent": "%s_%s2" % (f, r), "an_curent": 0})
        d["an_precedent" if col == "1" else "an_curent"] = int(v)
    loc = lambda k: (k[0], ordine.get(k[0], []).index(k[1]) if k[1] in ordine.get(k[0], []) else 1000 + k[1])   # noqa: E731
    return [out[k] for k in sorted(out, key=loc)]

