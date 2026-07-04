# -*- coding: utf-8 -*-
"""S1005 - situatii financiare anuale microentitati (OMF 107/2025, XSD v14).
Motor PUR: mapare balanta -> F10 (bilant prescurtat) + rulaje -> F20 (cont prescurtat micro).
Sursa formule rânduri: structura oficiala ANAF structura_SC (F10_BS, F20_micro).
Conventii:
  solduri: dict cont(text) -> (sold_debitor, sold_creditor)  [solduri FINALE la 31.12]
  rulaje:  dict cont(text) -> (rulaj_debitor, rulaj_creditor) [cumulate an, clasele 6/7]
Valorile F* sunt intregi (lei), rotunjite aritmetic."""
from decimal import Decimal, ROUND_HALF_UP

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
            - sc(s, "4428"))
    # creante (numai solduri debitoare pe conturile bifunctionale)
    r[301] = (sd(s, "4092","411","413","418","425","4282","431","437","4382","441","4424",
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
    return ' %s=%s' % (nume, quoteattr(str(val)))

def xml_s1005(prof, an, f10p, f10c, f20p, f20c):
    """XML S1005 v14. f10p/f20p = an precedent (dict rd->val), f10c/f20c = an curent."""
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
    # emit F10/F20 cu atribute F10_0NN1/F10_0NN2 (NN=rand, 2 cifre) si F10_3011/F10_3021
    def bloc(tag, dp, dc):
        a = []
        for k in sorted(set(dp) | set(dc)):
            v1, v2 = dp.get(k, 0), dc.get(k, 0)
            nn = ("%02d" % k) if k < 100 else str(k)
            if v1: a.append(_a("F%s_0%s1" % (tag, nn), v1))
            if v2: a.append(_a("F%s_0%s2" % (tag, nn), v2))
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
