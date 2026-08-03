# -*- coding: utf-8 -*-
"""core/d101.py — D101 (Declaratie privind impozitul pe profit).

REFACUT A DOUA OARA, COMPLET, 16.07.2026, direct din D101Validator.jar (v8,
namespace mfp:anaf:dgti:d101:declaratie:v10), atribute + mesaje de eroare
extrase din constant pool-ul clasei Identificare.

PRIMA REFACERE (aceeasi zi) fusese gresita in executie, nu in decizie: structura
veche (P1-P53) ERA cea corecta (confirmata acum in validator), dar fusese
inlocuita cu P1-P16 inventat din cap, crezand gresit ca era formularul de grup
fiscal (D101G). Namespace-ul v10 si Data_I/Data_S erau deja corecte in prima
refacere - pastrate aici.

Structura reala <declaratie101>:
  Flag-uri pe radacina (toate "0" implicit, fara conditii suplimentare):
    d_rec, d_recN, d_reg, d_reglem, d_anulare, d_succ, d_grup, d_prof, d_alte
  Date obligatorii: Data_I (inceput exercitiu), Data_S (sfarsit exercitiu),
    an_i, luna_i (derivate din Data_I), an, luna (derivate din Data_S)
  Identificare: cif, den, adresa, telefon, email, caen
  Declarant: nume_declar, prenume_declar, functie_declar
  temei (daca d_anulare=1), Stat_rezid, nr_evid, totalPlata_A

  Corpul declaratiei (P1-P16 - cele relevante pentru o firma fara grup fiscal,
  fara operatiuni offshore/redirectionare, cazuri acoperite de P17-P53):
    P1  = Total venituri
    P2  = Total cheltuieli
    P3  = Rezultat contabil (P1-P2)
    P4  = Elemente similare veniturilor
    P5  = Elemente similare cheltuielilor
    P6  = Deduceri fiscale
    P7  = Venituri neimpozabile
    P8  = Cheltuieli nedeductibile (=P081+P082+P083+P084 daca detaliat)
    P9  = Rezultat fiscal (P3+P4-P5+P8-P6-P7, minim 0)
    P10 = Pierdere fiscala recuperata
    P11 = Impozit pe profit calculat
    P12 = Reduceri de impozit
    P13 = Impozit declarat trimestrial prin D100
    P15 = Diferenta de impozit datorata: max((P11-P12)-P13, 0)
    P16 = Diferenta de impozit de recuperat: max(P13-(P11-P12), 0)

  NEIMPLEMENTATE (cazuri speciale, nu se aplica unei firme obisnuite):
    P17 (redirectionare 20%), P38-P53 (offshore, facilitati specifice,
    grup fiscal). Se adauga cand apare un caz real care le cere.
"""
from __future__ import annotations

from core.common import text_anaf as _t, alege_varianta as _av, Temei as _Tm, LIMITE_TEXT_ANAF as _LIM  # +versionare +limite text
from datetime import date as _date_v
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d101:declaratie:v10"

COTA_STANDARD = Decimal("16")

# ============================================================
#  IMCA - impozit minim pe cifra de afaceri (CF art.18^1). Verificat VERBATIM la sursa:
#  anaf_surse/cod_fiscal_227_2015_consolidat.html, art.18^1. VT/Vs/I/A sunt determinate de contabil
#  si primite ca intrari (I=investitii, A=amortizarea acestora). d101 avea deja comparatia P46/P47/P48
#  (alin.5); aici se ADAUGA CALCULUL IMCA (P47) + eligibilitatea, care lipseau (graf_temei: obligatie noua).
# ============================================================
PRAG_IMCA_EUR = Decimal("50000000")   # art.18^1 alin.(1): cifra de afaceri > 50.000.000 euro


def datoreaza_imca(vt, vs, curs_eur):
    """True daca firma datoreaza IMCA: cifra de afaceri a anului precedent (= VT - Vs, art.18^1 alin.(1))
    depaseste 50.000.000 euro, la cursul de la inchiderea exercitiului financiar. TEMEI: CF art.18^1 alin.(1)."""
    c = Decimal(str(curs_eur))
    if c <= 0:
        raise ValueError("curs_eur invalid (trebuie > 0)")
    cifra_afaceri_lei = Decimal(str(vt)) - Decimal(str(vs))
    return (cifra_afaceri_lei / c) > PRAG_IMCA_EUR


def impozit_minim_cifra_afaceri(vt, vs, i, a):
    """IMCA = 1% x (VT - Vs - I - A); daca formula da valoare negativa -> 0 (art.18^1 alin.(3)-(4)).
    VT=venituri totale; Vs=venituri care se scad (alin.3); I=investitii; A=amortizarea acestora.
    TEMEI: CF art.18^1 alin.(3)-(4). VERDE (verbatim anaf_surse/)."""
    baza = Decimal(str(vt)) - Decimal(str(vs)) - Decimal(str(i)) - Decimal(str(a))
    imca = Decimal("0.01") * baza
    return _i(imca) if imca > 0 else 0


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class RezultatD101:
    an: int
    prof: dict = field(default_factory=dict)
    P: dict = field(default_factory=dict)
    total_plata_a: int = 0
    cod_obligatie: str = "103"
    d_grup: int = 0


# Campurile P de INTRARE: baza contabila (P1,P2,P4,P5 - din pull) + ajustari fiscale (restul,
# introduse de contabil prin `manual`, default 0). Campurile derivate NU sunt intrari - se
# CALCULEAZA din formulele oficiale (OPANAF 206/2025). Un typo intr-o cheie manual e respins.
_P_INTRARI = {
    "P1", "P2", "P4", "P5",
    "P8", "P081", "P082", "P083", "P084", "P9", "P91",
    "P11", "P111", "P112", "P113", "P12", "P121", "P122", "P13", "P14", "P141", "P15", "P151",
    "P17", "P171", "P172", "P173", "P18", "P19", "P20",
    "P23", "P24", "P25", "P26", "P27", "P28", "P29", "P30", "P31", "P32", "P33",
    "P36", "P37", "P38", "P39", "P39a",
    "P412", "P421", "P4221", "P4222", "P423", "P4231", "P431", "P432", "P43a",
    "P44", "P45", "P46", "P47", "P49", "P50", "P51",
}
# Randurile PRINCIPALE P1..P53 (numar intreg) - checksum totalPlata_A le insumeaza pe TOATE,
# NU si sub-randurile 'din care' (P081, P411, P421...) sau cele cu litera (P38a, P39a, P40a, P43a).
# OPANAF 206/2025 poz.20: "totalPlata_A = suma(P1 la P53) (nu se insumeaza rd. de sub rd. 'din care')".
_P_MAIN = ["P%d" % n for n in range(1, 54)]


# Scadenta platii D101 = regula de STRUCTURA versionata pe an (tiparul cota() pe cod, PAS 2). Valorile urmeaza
# validatorul OFICIAL DUKIntegrator (R17) SI sunt legal corecte pe 2022-2025 - temeiul real (verificat 03.08.2026):
#   2022-2025 -> 25 iunie (LL+6): OUG 153/2020 art.I alin.(13) lit.a) "prin derogare de la art.41 si 42 din Codul
#     fiscal, termenul pentru depunerea declaratiei anuale privind impozitul pe profit... este pana la data de 25
#     iunie inclusiv a anului urmator", aplicabil pentru anii fiscali 2021-2025 (art.VI). MO 817/04.09.2020.
#   2026+ -> 25 martie (LL+3): art.42(1) CF baza (Legea 227/2015), dupa incheierea schemei OUG 153/2020. E si ce
#     cere jar-ul DUK instalat azi. NOTA (decizie Costin 03.08.2026): OUG 8/2026 art.6 pct.12 (MO 147/25 feb 2026)
#     muta termenul de baza la 25 iunie PERMANENT de la anul fiscal 2026; jar-ul instalat inca cere martie, iar
#     D101 pt fiscal 2026 se depune in 2027 - ANAF actualizeaza validatorul pana atunci (nu e conflict de fond).
#     Cand jar-ul trece la iunie, probele DUK pe an=2026 (test_imca_d101_duk_valid) vor pica -> semnal sa treci
#     _scadenta_2026 la LL+6. Vezi DECIZII.md 03.08.2026.
def _scadenta_2022(an):
    """an Data_S 2021-2025 -> 25 IUNIE (LL+6): OUG 153/2020 art.I alin.(13) lit.a), derogare de la art.41-42 CF,
    aplicabil 2021-2025 (art.VI). Legal corect SI DUK-valid. Confirmat 03.08.2026 la sursa (MO 817/04.09.2020)."""
    ll, scad_an = 12 + 6, an + 1
    if ll > 12:
        ll -= 12
    return ll, scad_an


def _scadenta_2026(an):
    """an Data_S >= 2026 -> 25 MARTIE (LL+3): art.42(1) CF baza (Legea 227/2015), schema OUG 153/2020 incheiata =
    ce cere validatorul DUK instalat. OUG 8/2026 art.6 pct.12 muta baza la 25 iunie de la fiscal 2026 cand jar-ul
    se actualizeaza (D101 fiscal 2026 depusa in 2027) - vezi nota de deasupra + DECIZII.md 03.08.2026."""
    ll, scad_an = 12 + 3, an + 1
    if ll > 12:
        ll -= 12
    return ll, scad_an


_VARIANTE_SCADENTA = [
    ("2022-01-01", _scadenta_2022, _Tm("OUG", 153, 2020, art="I", alin="13", lit="a", nivel_sursa="MO", de_cine="Costin", verificat_la="2026-08-03")),
    ("2026-01-01", _scadenta_2026, _Tm("Legea", 227, 2015, art="42", alin="1", nivel_sursa="MO", de_cine="Costin", verificat_la="2026-08-03")),
]


def _scadenta(an):
    """Scadenta platii (luna, an), DISPECER pe an - varianta de regula valabila pentru anul declaratiei."""
    fn, _ = _av(_VARIANTE_SCADENTA, _date_v(an, 1, 1))
    return fn(an)


def calcul_d101(prof, an, intrari=None, cota=None, d_grup=0, cod_obligatie="103", imca=None, rezerva=None):
    """Reconstruit 01.08.2026 pe FORMULARUL OFICIAL (OPANAF 206/2025, D101_A600 v10,
    anaf_surse/d101_struct_anaf.txt). `intrari` = dict cu campurile P de intrare (P1,P2,P4,P5 din
    contabilitate + ajustari fiscale din manual). Numerotarea inventata anterioara (p11=impozit) a
    DISPARUT: fiecare P corespunde randului oficial. Campurile derivate se calculeaza din formule."""
    I = dict(intrari or {})
    necunoscute = [k for k in I if k not in _P_INTRARI]
    if necunoscute:
        raise ValueError("D101 intrari necunoscute: %s (permise: %s)" % (sorted(necunoscute), sorted(_P_INTRARI)))
    cota = Decimal(str(cota if cota is not None else COTA_STANDARD))
    g = lambda k: _i(I.get(k, 0))

    P = {}
    # --- Venituri/cheltuieli, rezultat brut (rd.1-10) ---
    P["P1"] = g("P1")                                   # Venituri din exploatare
    P["P2"] = g("P2")                                   # Cheltuieli de exploatare
    P["P3"] = P["P1"] - P["P2"]                         # P3=P1-P2 (rezultat exploatare)
    P["P4"] = g("P4")                                   # Venituri financiare
    P["P5"] = g("P5")                                   # Cheltuieli financiare
    P["P6"] = P["P4"] - P["P5"]                         # P6=P4-P5 (rezultat financiar)
    P["P7"] = P["P3"] + P["P6"]                         # P7=P3+P6 (rezultat brut)  [R38]
    P["P8"] = g("P8")                                   # Elemente similare veniturilor
    P["P9"] = g("P9")                                   # Elemente similare cheltuielilor
    P["P10"] = P["P7"] + P["P8"] - P["P9"]              # P10=P7+P8-P9
    # P13 Rezerva legala deductibila (CF art.26 alin.(1) lit.a), AUTO din contabilitate cand nu e dat
    # manual. Baza = profitul contabil BRUT = P7 + cheltuiala CONTABILA cu impozitul (cont 691, se
    # adauga inapoi - cifra contabila, NU impozitul calculat de D101 -> fara circularitate). Deductibil =
    # min(5%% x baza; 20%% x capital subscris/varsat (1012) - rezerva existenta (1061)), >= 0. Fara ea,
    # firma supra-declara impozitul pe profit (deducerea nu se aplica desi conditiile sunt indeplinite).
    if "P13" not in I and rezerva:
        _baza_rez = P["P7"] + _i(rezerva.get("chelt_impozit", 0))
        if _baza_rez > 0:
            _cota_rez = _i(Decimal(str(_baza_rez)) * Decimal("0.05"))
            _plafon_rez = (_i(Decimal(str(rezerva.get("capital", 0) or 0)) * Decimal("0.20"))
                           - _i(rezerva.get("rezerva_existenta", 0)))
            I["P13"] = max(0, min(_cota_rez, _plafon_rez))
    # --- Deduceri (rd.11-16) ---
    for k in ("P11", "P12", "P13", "P14", "P15"):
        P[k] = g(k)
    P["P16"] = P["P11"] + P["P12"] + P["P13"] + P["P14"] + P["P15"]     # P16 total deduceri
    # --- Venituri neimpozabile (rd.17-21) ---
    for k in ("P17", "P18", "P19", "P20"):
        P[k] = g(k)
    P["P21"] = P["P17"] + P["P18"] + P["P19"] + P["P20"]                # P21
    P["P22"] = P["P10"] - P["P16"] - P["P21"]          # P22 profit/pierdere
    # --- Cheltuieli nedeductibile (rd.23-34) ---
    P["P34"] = 0
    for n in range(23, 34):
        P["P%d" % n] = g("P%d" % n)
        P["P34"] += P["P%d" % n]                        # P34 = P23+..+P33
    P["P35"] = P["P22"] + P["P34"]                     # P35
    for k in ("P36", "P37", "P38"):
        P[k] = g(k)
    P["P38a"] = P["P35"] + P["P36"] + P["P37"] - P["P38"]               # P38a
    P["P39"] = g("P39")
    P["P39a"] = g("P39a")
    # --- Profit impozabil (rd.40) ---
    if P["P38a"] >= 0 and P["P39a"] >= 0 and (P["P38a"] - P["P39a"]) > 0:
        P["P40"] = P["P38a"] - P["P39a"]
    else:
        P["P40"] = 0
    P["P40a"] = -P["P38a"] if P["P38a"] < 0 else 0
    # --- Impozit pe profit (rd.41) ---
    P["P411"] = _i(Decimal(P["P40"]) * cota / 100)     # 16% pe profitul impozabil
    P["P412"] = g("P412")                               # 5% baruri de noapte etc.
    if d_grup:
        P["P412"] = 0
    P["P41"] = P["P411"] + P["P412"]                   # P41=P411+P412  [R41]
    # --- Credit fiscal, sponsorizare, reduceri (rd.42-45) ---
    P["P421"] = g("P421")
    P["P4221"] = g("P4221"); P["P4222"] = g("P4222")
    P["P422"] = g("P422") if False else (P["P4221"] + P["P4222"])
    P["P4231"] = g("P4231")
    P["P423"] = g("P423") if g("P423") else P["P4231"]
    P["P42"] = P["P421"] + P["P422"] + P["P423"]       # P42=P421+P422+P423
    P["P431"] = g("P431"); P["P432"] = g("P432"); P["P43a"] = g("P43a")
    P["P43"] = P["P431"] + P["P432"]                   # P43=P431+P432
    P["P44"] = g("P44"); P["P45"] = g("P45")
    P["P46"] = g("P46"); P["P47"] = g("P47")
    # [IMCA art.18^1] daca se dau componentele (imca={vt,vs,i,a,curs}), P47 se COMPUTA din formula
    # 1% x (VT-Vs-I-A) cand firma e sub prag (>50 mil euro); altfel P47=0. Fara componente -> P47 ramane input.
    if imca is not None:
        if datoreaza_imca(imca.get("vt", 0), imca.get("vs", 0), imca.get("curs", 0)):
            P["P47"] = impozit_minim_cifra_afaceri(imca.get("vt", 0), imca.get("vs", 0),
                                                   imca.get("i", 0), imca.get("a", 0))
        else:
            P["P47"] = 0
    # --- Impozit datorat (rd.48) ---
    v481 = P["P41"] - P["P42"] - P["P43"] - P["P44"] - P["P45"]         # P481 var
    v482 = P["P47"] - P["P421"] - P["P431"] - P["P43a"]                 # P482 var
    if P["P46"] == 0 and P["P47"] == 0:
        P["P481"] = max(v481, 0); P["P482"] = 0
    elif P["P46"] >= P["P47"]:
        P["P481"] = max(v481, 0); P["P482"] = 0
    else:
        P["P481"] = 0; P["P482"] = max(v482, 0)
    P["P48"] = P["P481"] + P["P482"]                   # P48=P481+P482
    if d_grup:
        P["P48"] = P["P481"] = P["P482"] = 0
    # --- Diferente (rd.49-53) ---
    P["P49"] = g("P49"); P["P50"] = g("P50"); P["P51"] = g("P51")
    if d_grup:
        P["P50"] = P["P51"] = 0
    dif = (P["P48"] + P["P51"]) - (P["P49"] + P["P50"])
    P["P52"] = dif if dif >= 0 else 0                  # diferenta de plata
    P["P53"] = -dif if dif < 0 else 0                  # diferenta de recuperat
    if d_grup:
        P["P52"] = P["P53"] = 0
    # sub-randuri optionale informative (emise doar daca furnizate)
    for k in ("P081", "P082", "P083", "P084", "P91", "P111", "P112", "P113",
              "P121", "P122", "P141", "P151", "P171", "P172", "P173", "P4221", "P4222", "P4231"):
        if g(k):
            P[k] = g(k)

    # totalPlata_A = suma randurilor PRINCIPALE P1..P53 (checksum de structura, nu impozit datorat)
    total = sum(P.get(k, 0) for k in _P_MAIN)
    # emitem doar campurile NENULE (validatorul nu cere randuri = 0 explicit)
    Pnz = {k: v for k, v in P.items() if v}
    return RezultatD101(an=an, prof=prof, P=Pnz, total_plata_a=total,
                        cod_obligatie=str(cod_obligatie), d_grup=int(d_grup))


def erori_generare(prof):
    erori = []
    if not (prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    if not (prof.get("caen") or "").strip():
        erori.append("LIPSĂ cod CAEN (obligatoriu în D101).")
    return erori


def _nr_evid(cui, an, luna, cod_oblig="103"):
    """23 caractere, format oficial ANAF: poz.1-2 '10', poz.3-5 cod_oblig, poz.6-7 '01',
    poz.8-11 LLAA (sfarsit perioada = 12.AA), poz.12-17 ZZLLAA (scadenta din _scadenta),
    poz.18 '0', poz.19 '0', poz.20-21 '00', poz.22-23 = ultimele 2 cifre din suma primelor 21."""
    scad_luna, scad_an = _scadenta(an)
    p1_21 = ("10" + str(cod_oblig).rjust(3, "0")[-3:] + "01" +
             "%02d%02d" % (12, an % 100) +
             "%02d%02d%02d" % (25, scad_luna, scad_an % 100) + "0" + "0" + "00")
    assert len(p1_21) == 21
    suma = sum(int(c) for c in p1_21)
    return p1_21 + "%02d" % (suma % 100)


def build_xml(res):
    """P-urile se emit ca ATRIBUTE pe <declaratie101> (nu elemente-copil: validatorul respinge
    'sectiune necunoscuta P1'). OPANAF 206/2025: toate campurile (d_rec..P53) sunt atribute ale
    elementului unic <declaratie101>, care se inchide self-fara-copii."""
    prof = res.prof
    an = res.an
    cif_num = "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit())
    scad_luna, scad_an = _scadenta(an)
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    a = []
    a.append('an="%d" luna="12" an_i="%d" luna_i="1" cod_obligatie="%s"' % (an, an, res.cod_obligatie))
    a.append('d_rec="0" d_reg="0" d_reglem="0" d_anulare="0" d_succ="0" d_prof="0" d_alte="0"')
    if res.d_grup:
        a.append('d_grup="1"')
    a.append('Data_I="01.01.%d" Data_S="31.12.%d"' % (an, an))
    a.append('cod_bug="5503XXXXXX" nr_evid="%s" scadenta="25%02d%02d"' % (
        _nr_evid(cif_num, an, 12, res.cod_obligatie), scad_luna, scad_an % 100))
    a.append('totalPlata_A="%d"' % res.total_plata_a)
    a.append('nume_declar=%s prenume_declar=%s functie_declar=%s' % (
        _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR", _LIM["d101"]["nume_declar"])),
        _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d101"]["prenume_declar"])),
        _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d101"]["functie_declar"]))))
    a.append('cif="%s" denumire=%s adresa=%s' % (
        cif_num, _esc(_t(prof.get("nume"), _LIM["d101"]["denumire"])), _esc(_t(prof.get("adresa"), _LIM["d101"]["adresa"]))))
    caen = (prof.get("caen") or "").strip()
    if caen:
        a.append('caen=%s' % _esc(caen))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        a.append('telefon=%s' % _esc(_t(tel, _LIM["d101"]["telefon"])))
    # campurile P (nenule) ca atribute, in ordinea oficiala a randurilor
    def _ordine(k):
        m = re.match(r"P(\d+)([a-z]?)(\d*)", k)
        return (int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (999, "", 0)
    for k in sorted(res.P.keys(), key=_ordine):
        a.append('%s="%d"' % (k, res.P[k]))
    H.append('<declaratie101 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
             'xmlns="%s" xsi:schemaLocation="%s D101.xsd" %s/>' % (NS, NS, " ".join(a)))
    return "\n".join(H)


def pull(conn, schema, perioada):
    """Profil + venituri/cheltuieli SPLIT pe exploatare (P1/P2) si financiar (P4/P5), din note
    VALIDATE, pe fereastra anului. Clasa 76 = venituri financiare, 66 = cheltuieli financiare;
    restul 7x/6x = exploatare (planul de conturi RO). Fara split, D101 ar pune tot in exploatare."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, caen, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        cur.execute(
            "SELECT "
            "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_fin, "
            "COALESCE(SUM(CASE WHEN l.cont_credit LIKE '7%%' AND l.cont_credit NOT LIKE '76%%' THEN l.suma ELSE 0 END),0) AS ven_expl, "
            "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_fin, "
            "COALESCE(SUM(CASE WHEN l.cont_debit LIKE '6%%' AND l.cont_debit NOT LIKE '66%%' THEN l.suma ELSE 0 END),0) AS chelt_expl "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s",
            (_inc.isoformat(), _sf.isoformat()))
        r = cur.fetchone() or {}
        # Balante pentru rezerva legala deductibila (CF art.26 alin.(1) lit.a):
        #  capital 1012 (subscris/varsat) = sold cumulat pana la SFARSITUL perioadei (credit-debit);
        #  rezerva 1061 EXISTENTA = sold cumulat pana la INCEPUTUL anului (din anii anteriori);
        #  691 = cheltuiala cu impozitul pe profit pe anul curent (baza rezervei = profit contabil + 691).
        cur.execute(
            "SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '1012%%' THEN l.suma ELSE 0 END),0) "
            "     - COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '1012%%' THEN l.suma ELSE 0 END),0) AS capital "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status = 'validata' AND i.data < %s", (_sf.isoformat(),))
        r["capital"] = (cur.fetchone() or {}).get("capital", 0)
        cur.execute(
            "SELECT COALESCE(SUM(CASE WHEN l.cont_credit LIKE '1061%%' THEN l.suma ELSE 0 END),0) "
            "     - COALESCE(SUM(CASE WHEN l.cont_debit  LIKE '1061%%' THEN l.suma ELSE 0 END),0) AS rez "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status = 'validata' AND i.data < %s", (_inc.isoformat(),))
        r["rezerva_existenta"] = (cur.fetchone() or {}).get("rez", 0)
        cur.execute(
            "SELECT COALESCE(SUM(CASE WHEN l.cont_debit LIKE '691%%' THEN l.suma ELSE 0 END),0) AS imp "
            "FROM inregistrari_linii l JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status = 'validata' AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
        r["chelt_impozit"] = (cur.fetchone() or {}).get("imp", 0)
    return prof, r


def genereaza(conn, schema, perioada, manual=None):
    """D101 anual (contract uniform A1 + reconstructie oficiala 01.08.2026 pe OPANAF 206/2025).
    Foloseste perioada.an. `manual` = ajustari fiscale (chei P8..P51 din formular) + cota/d_grup/
    cod_obligatie; o cheie P necunoscuta e respinsa de calcul_d101 (typo != implicit tacut)."""
    manual = dict(manual or {})
    cota = manual.pop("cota", None)
    d_grup = int(manual.pop("d_grup", 0) or 0)
    cod_obligatie = str(manual.pop("cod_obligatie", "103"))
    prof, r = pull(conn, schema, perioada)
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))
    intrari = {"P1": r.get("ven_expl", 0), "P2": r.get("chelt_expl", 0),
               "P4": r.get("ven_fin", 0), "P5": r.get("chelt_fin", 0)}
    intrari.update(manual)   # ajustarile fiscale ale contabilului completeaza/suprascriu baza
    res = calcul_d101(prof, perioada.an, intrari, cota=cota, d_grup=d_grup, cod_obligatie=cod_obligatie,
                      rezerva={"capital": r.get("capital", 0),
                               "rezerva_existenta": r.get("rezerva_existenta", 0),
                               "chelt_impozit": r.get("chelt_impozit", 0)})
    xml = build_xml(res)
    return xml, res
