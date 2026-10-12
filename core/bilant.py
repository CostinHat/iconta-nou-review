# -*- coding: utf-8 -*-
"""S1005 - situatii financiare anuale microentitati (OMF 107/2025, XSD v14).
Motor PUR: mapare balanta -> F10 (bilant prescurtat) + rulaje -> F20 (cont prescurtat micro).
Sursa formule rânduri: ANAF structura bilant VERSIUNE NECUNOSCUTA structura_SC (F10_BS, F20_micro).
Conventii:
  solduri: dict cont(text) -> (sold_debitor, sold_creditor)  [solduri FINALE la 31.12]
  rulaje:  dict cont(text) -> (rulaj_debitor, rulaj_creditor) [cumulate an, clasele 6/7]
Valorile F* sunt intregi (lei), rotunjite aritmetic."""
from decimal import Decimal, ROUND_HALF_UP

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


def f10_din_balanta(s):
    """F10 bilant prescurtat micro (S1005). Intoarce dict rd->valoare (lei intregi).
    Randuri per formular oficial; sume algebrice cu ajustari (28x/29x/39x/49x/59x) scazute."""
    r = {}
    r[1] = sd(s, "201","203","205","206","2071","208","4094") - sc(s, "280","290","2933","2934")
    r[2] = (sd(s, "211","212","213","214","215","216","217","223","224","227","231","235","4093")
            - sc(s, "281","291","2931","2935"))
    r[3] = sd(s, "261","262","263","265","266","267") - sc(s, "296")
    r[4] = r[1] + r[2] + r[3]
    # stocuri: 30x/32x/33x/34x/35x/36x/37x/38x + 4091, minus 39x; 378/4428 (adaos+TVA neex) scad; 308/348/368/388 dupa sold
    r[5] = (sd(s, "301","302","303","321","322","323","326","327","328","331","332",
                  "341","345","346","347","351","354","356","357","358","361","371","381","4091")
            + sd(s, "308","348","368","388") - sc(s, "308","348","368","388")
            - sc(s, "378") - sc(s, "391","392","393","394","395","396","397","398")
            # [08.10.2026, decizia Costin pct.1 la §6 S6] „din ct. 4428” = numai TVA-ul din prețul de raft, pe analiticul lui
            - sc(s, CONT_TVA_STOC))
    s = _fara_tva_stoc(s)   # de aici încolo (creanțe, datorii) analiticul stocului nu mai contează — o singură dată, la rd.05
    # creante (numai solduri debitoare pe conturile bifunctionale)
    # [08.10.2026, §6 pct.3] 4428 cu sold DEBITOR (TVA-ul NIR-urilor fără factură, 4428.01; achizițiile la TVA la încasare) e creanță —
    # OMFP 1802/2014, bilanțul prescurtat, rd.06 CREANȚE: „… + 4424 + din ct. 4428** + 444** …” (** = solduri debitoare)
    r[301] = (sd(s, "4092","411","413","418","425","4282","431","437","4382","441","4424","4428",
                   "444","445","446","447","4482","451","453","456","4582","461","4662","473","5187")
              - sc(s, "491","495","496"))
    r[302] = Decimal("0")  # creante din dividende interimare - rar la micro
    r[6] = r[301] + r[302]
    r[7] = sd(s, "501","505","506","507","508","5113","5114") - sc(s, "591","595","596","598")
    r[8] = sd(s, "5112","512","531","532","541","542")
    r[9] = r[5] + r[6] + r[7] + r[8]
    r[11] = sd(s, "471"); r[12] = Decimal("0"); r[10] = r[11] + r[12]
    # datorii sub 1 an (numai solduri creditoare) - v1: toate pe termen scurt (micro tipic)
    r[13] = (sc(s, "161","162","166","167","168","269","401","403","404","405","408","419",
                  "421","423","424","426","427","4281","431","437","4381","441","4423","4428",
                  "444","446","447","4481","451","453","455","456","457","4581","462","4661",
                  "473","509","5186","519") - sd(s, "169"))
    r[16] = Decimal("0")  # datorii peste 1 an - v1 (de introdus manual daca exista)
    r[17] = sc(s, "151")
    r[20] = Decimal("0"); r[21] = sc(s, "475"); r[19] = r[20] + r[21]
    r[23] = sc(s, "472"); r[24] = Decimal("0"); r[22] = r[23] + r[24]
    r[26] = Decimal("0"); r[27] = sc(s, "478"); r[25] = r[26] + r[27]
    r[28] = sc(s, "2075")
    r[18] = r[19] + r[22] + r[25] + r[28]
    r[14] = r[9] + r[11] - r[13] - r[20] - r[23] - r[26]
    r[15] = r[4] + r[12] + r[14]
    r[30] = sc(s, "1012"); r[31] = sc(s, "1011"); r[32] = sc(s, "1015")
    r[33] = sc(s, "1018"); r[34] = sc(s, "1031")
    r[29] = r[30] + r[31] + r[32] + r[33] + r[34]
    r[35] = sc(s, "104"); r[36] = sc(s, "105"); r[37] = sc(s, "106")
    r[38] = sd(s, "109"); r[39] = sc(s, "141"); r[40] = sd(s, "149")
    r[41] = sc(s, "117"); r[42] = sd(s, "117")
    r[43] = sc(s, "121"); r[44] = sd(s, "121")
    r[45] = sd(s, "129")
    r[46] = (r[29] + r[35] + r[36] + r[37] - r[38] + r[39] - r[40]
             + r[41] - r[42] + r[43] - r[44] - r[45])
    r[47] = sc(s, "1016"); r[48] = sc(s, "1017")
    r[49] = r[46] + r[47] + r[48]
    return {k: _i(v) for k, v in r.items()}

def f20_din_rulaje(rl):
    """F20 cont prescurtat micro. rd1 CA neta, 2 alte venituri, 3 materii/materiale,
    4 personal (inclusiv 646 CAM), 5 ajustari de valoare, 6 alte cheltuieli, 7 impozite,
    8 profit / 9 pierdere."""
    r = {}
    r[1] = rc(rl, "701","702","703","704","705","706","707","708") - rd(rl, "709") + rc(rl, "7411")
    ven_total = rc(rl, "70") - rd(rl, "709") + rc(rl, "71","72","74","75","76","78")
    r[2] = ven_total - r[1]
    if r[2] < 0: r[2] = Decimal("0")
    r[3] = rd(rl, "601","602","603","604","606","607","608") - rc(rl, "609")
    r[4] = rd(rl, "641","642","643","644","645","646")
    r[5] = rd(rl, "654","681","686") - rc(rl, "754","7812","7813","7814","786")
    che_total = rd(rl, "6") - rc(rl, "609","754","7812","7813","7814","786")
    r[7] = rd(rl, "691","694","697","698")
    r[6] = che_total - r[3] - r[4] - (rd(rl, "654","681","686")) - r[7]
    if r[6] < 0: r[6] = Decimal("0")
    rez = ven_total - che_total
    r[8] = rez if rez > 0 else Decimal("0")
    r[9] = -rez if rez < 0 else Decimal("0")
    return {k: _i(v) for k, v in r.items()}

def _a(nume, val):
    from xml.sax.saxutils import quoteattr
    # ANAF respinge "atribut prezent dar vid" (dovedit 15.07.2026 pe regCom/banca/cont).
    # Un atribut fara valoare se OMITE, nu se scrie gol: altfel contabilul primeste o
    # eroare criptica de la validator in loc sa afle ce camp sa completeze in profil.
    if val is None or str(val).strip() == "":
        return ""
    return ' %s=%s' % (nume, quoteattr(str(val)))

def xml_s1005(prof, an, f10p, f10c, f20p, f20c):
    """XML S1005 v15. f10p/f20p = an precedent (dict rd->val), f10c/f20c = an curent.

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
    # F30 date informative minime: rd1/2 = unitati cu profit/pierdere (col1=nr, col2=suma), rd3 idem 0
    pr, pi = f20c.get(8, 0), f20c.get(9, 0)
    f30 = []
    f30.append(_a("F30_0011", 1 if pr > 0 else 0)); f30.append(_a("F30_0012", pr))
    f30.append(_a("F30_0021", 1 if pi > 0 else 0)); f30.append(_a("F30_0022", pi))
    f30.append(_a("F30_0031", 1 if (pr == 0 and pi == 0) else 0)); f30.append(_a("F30_0032", 0))
    H.append('  <F30%s/>' % "".join(f30))
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


def motiv_sintetic(sintetic):
    """Motivul refuzului pentru un rulaj pe `sintetic`, cu analiticele cerute grupate pe rândul formularului."""
    pe_rand = {}
    for analitic, rand in F20_S1003_NOMENCLATOR_SINTETICE[sintetic]:
        pe_rand.setdefault(rand, []).append(analitic)
    rd = lambda r: "rd.%s" % (("%02d" % r) if r < 100 else r)   # noqa: E731
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
    r = v
    r[1] = r[2] + r[3] - r[4] + r[6]                                                    # R01: R02+R03-R04+R06
    r[16] = r[1] + r[7] - r[8] + r[9] + r[10] + r[11] + r[12] + r[13]                   # R16
    r[22] = r[23] + r[24]                                                               # R22
    r[25] = r[306] + r[26] - r[27]                                                      # R25: R306+R26-R27
    r[28] = r[29] - r[30]                                                               # R28
    r[31] = r[32] + r[33] + r[34] + r[35] + r[36] + r[37] + r[310] + r[312] + r[314] + r[316]   # R31
    r[39] = r[40] - r[41]                                                               # R39
    r[42] = r[17] + r[18] + r[19] + r[20] - r[21] + r[22] + r[25] + r[28] + r[31] + r[39]      # R42
    r[43], r[44] = max(r[16] - r[42], D("0")), max(r[42] - r[16], D("0"))              # R43 / R44
    r[46] = r[48] = r[57] = D("0")                                                      # „din care … afiliate”: nu se știu
    r[52] = r[45] + r[47] + r[49] + r[50]                                               # R52
    r[53] = r[54] - r[55]                                                               # R53
    r[59] = r[53] + r[56] + r[58]                                                       # R59
    r[60], r[61] = max(r[52] - r[59], D("0")), max(r[59] - r[52], D("0"))              # R60 / R61
    r[62] = r[16] + r[52]                                                               # R62
    r[63] = r[42] + r[59]                                                               # R63
    r[64], r[65] = max(r[62] - r[63], D("0")), max(r[63] - r[62], D("0"))              # R64 / R65
    net = (r[64] + r[305]) - (r[65] + r[66] + r[68] + r[304] + r[317])                 # R69 / R70 (R67 = null, scos din calcul)
    r[69], r[70] = max(net, D("0")), max(-net, D("0"))
    for k in (46, 48, 57):
        r.pop(k)
    return {k: _i(x) for k, x in r.items()}


def xml_s1003(prof, an, f10p, f10c, f20p, f20c):
    """XML S1003 (mici) v15 - aceeasi structura antet ca S1005, tipBIL=BS."""
    x = xml_s1005(prof, an, f10p, f10c, f20p, f20c)
    x = x.replace("mfp:anaf:dgti:s1005:declaratie:v15", "mfp:anaf:dgti:s1003:declaratie:v15")
    x = x.replace("<Bilant1005", "<Bilant1003").replace("</Bilant1005>", "</Bilant1003>")
    x = x.replace('tipBIL="UU"', 'tipBIL="BS"')
    return x


def randuri_din_xml(xml):
    """[deficiența 188, retestul Costin 09.10.2026: „rândurile bilanțului (F10_0052, F10_0132 și restul) apar pe ecranul Bilanț, cu cifrele
    care se depun, nu doar verdictul”] Rândurile CITITE din XML-ul care se depune (nu recalculate): [{formular, rand, cod_precedent,
    an_precedent, cod_curent, an_curent}], în ordinea formularului. Codul atributului e `F<formular>_<rând pe 3 cifre><coloana>`
    (1 = an precedent, 2 = an curent — `xml_s1005`). [deficiența 227, comanda Costin 12.10.2026] fiecare rând poartă și denumirea de pe
    formular (`core/bilant_denumiri.py`, extrasă din structura ANAF), după formularul din rădăcina XML-ului (Bilant1003 / Bilant1005)."""
    import re as _re
    from core.bilant_denumiri import NOMENCLATOR_DENUMIRI
    den = NOMENCLATOR_DENUMIRI["s1003" if "<Bilant1003" in (xml or "") else "s1005"]
    out = {}
    for f, r, col, v in _re.findall(r'\b(F\d\d)_(\d{3})([12])="(-?\d+)"', xml or ""):
        d = out.setdefault((f, int(r)), {"formular": f, "rand": int(r), "denumire": den.get(f, {}).get(int(r), ""),
                                          "cod_precedent": "%s_%s1" % (f, r), "an_precedent": 0,
                                          "cod_curent": "%s_%s2" % (f, r), "an_curent": 0})
        d["an_precedent" if col == "1" else "an_curent"] = int(v)
    return [out[k] for k in sorted(out)]

