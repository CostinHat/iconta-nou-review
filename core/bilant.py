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
    return [t for par in re.findall(r"\(((?:din\s*)?ct\.[^()]*)\)", text) for t in termeni(par.replace("din ct.", "din").replace("din ct", "din"))]


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
              "F20": {8: ("+1+2-3-4-5-6-7+304", True), 9: ("-1-2+3+4+5+6+7-304", True)}},
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
    F10_64). Clasele 6 / 7 nu se citesc aici (rezultatul exercițiului e soldul lui 121 — închiderea lor e decizia cerută la §6, 12.10.2026)."""
    fara = conturi_fara_rand(F10_NOMENCLATOR, s, "12345")
    if fara:
        raise ValueError(motiv_f10(fara))
    v = _randuri_din_nomenclator(F10_NOMENCLATOR, s, tva_stoc_la=5)
    for r in (12, 16, 20, 24, 26):                     # NOMENCLATOR_ABATERI_FORMULAR: conturile lor stau pe rândul pereche
        v[r] = Decimal("0")
    return {k: _i(x) for k, x in cu_totaluri("s1005", "F10", v).items()}


def motiv_f10(fara):
    det = "; ".join("%s sold %s %s" % (c, "debitor" if l == "d" else "creditor", format(v, ".2f")) for c, l, v in fara)
    return ("Bilanțul: soldurile la 31.12 de mai jos nu au rând în bilanțul formularului ANAF 2025 (F10), pe latura lor — bilanțul n-ar mai "
            "fi egal (DUK regula F10_64): %s. Regularizează sau reclasează conturile la 31.12, apoi generează din nou." % det)


#: [C13] sinteticele planului OMFP 1802/2014 ale căror analitice stau pe rânduri DIFERITE ale F20 S1005 (aceeași regulă ca la S1003 —
#: decizia Costin 12.10.2026: „nu ghicim rândul”); păzit de `core/test_bilant_formular.py` (= lista calculată din plan)
F20_S1005_NOMENCLATOR_SINTETICE = {
    "741": (("7411", 1), ("7412", 2), ("7413", 2), ("7414", 2), ("7415", 2), ("7416", 2), ("7417", 2), ("7418", 2), ("7419", 2)),
    "781": (("7812", 5), ("7813", 5), ("7814", 5), ("7815", 2), ("7818", 5)),
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
    sintetice = sorted({str(c).split(".")[0] for c in rl if str(c).split(".")[0] in F20_S1005_NOMENCLATOR_SINTETICE})
    if sintetice:
        raise ValueError("Bilanțul S1005: " + " ".join(motiv_sintetic(c, F20_S1005_NOMENCLATOR_SINTETICE) for c in sintetice))
    fara = sorted(str(c) for c in rl if rand_f20_s1005(c) is None)
    if fara:
        raise ValueError("Bilanțul S1005: contul %s nu are rând în contul prescurtat de profit și pierdere al formularului ANAF 2025 — "
                         "rulajul lui nu se poate depune; reclasează-l pe un cont al planului OMFP 1802/2014." % ", ".join(fara))
    v = _randuri_din_nomenclator(F20_S1005_NOMENCLATOR, rl)
    v.update(_randuri_din_nomenclator(F20_S1005_NOMENCLATOR_DIN_CARE, rl))
    return {k: _i(x) for k, x in cu_totaluri("s1005", "F20", v).items()}


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


def motiv_sintetic(sintetic, tabel=None):
    """Motivul refuzului pentru un rulaj pe `sintetic`, cu analiticele cerute grupate pe rândul formularului (`tabel`: S1003 implicit)."""
    pe_rand = {}
    for analitic, rand in (tabel or F20_S1003_NOMENCLATOR_SINTETICE)[sintetic]:
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
    # totalurile = calculele formularului (`NOMENCLATOR_TOTALURI`, păzit de core/test_bilant_formular.py); rândurile „din care … afiliate”
    # (46, 48, 57) nu se pot ști din rulaje și nu se scriu; R67 („=null”) nu intră în R69 / R70
    return {k: _i(x) for k, x in cu_totaluri("s1003", "F20", v).items()}


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
    formular (`core/bilant_denumiri.py`, extrasă din formularul ANAF), după formularul din rădăcina XML-ului (Bilant1003 / Bilant1005).
    [deficiența 234] în ORDINEA formularului (06a, 06b înaintea totalului 06) și cu codul tipărit pe el („06a (301)”)."""
    from core.bilant_denumiri import NOMENCLATOR_COD, NOMENCLATOR_DENUMIRI, NOMENCLATOR_ORDINE
    tip = "s1003" if "<Bilant1003" in (xml or "") else "s1005"
    den, cod, ordine = NOMENCLATOR_DENUMIRI[tip], NOMENCLATOR_COD[tip], NOMENCLATOR_ORDINE[tip]
    out = {}
    for f, r, col, v in re.findall(r'\b(F\d\d)_(\d{3})([12])="(-?\d+)"', xml or ""):
        d = out.setdefault((f, int(r)), {"formular": f, "rand": int(r), "denumire": den.get(f, {}).get(int(r), ""),
                                          "cod": cod.get(f, {}).get(int(r), r[1:] if r.startswith("0") else r),
                                          "cod_precedent": "%s_%s1" % (f, r), "an_precedent": 0,
                                          "cod_curent": "%s_%s2" % (f, r), "an_curent": 0})
        d["an_precedent" if col == "1" else "an_curent"] = int(v)
    loc = lambda k: (k[0], ordine.get(k[0], []).index(k[1]) if k[1] in ordine.get(k[0], []) else 1000 + k[1])   # noqa: E731
    return [out[k] for k in sorted(out, key=loc)]

