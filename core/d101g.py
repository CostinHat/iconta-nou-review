# -*- coding: utf-8 -*-
"""core/d101g.py — D101G: Declaratie CONSOLIDATA privind impozitul pe profit determinat de GRUPUL FISCAL.

Depusa de PERSOANA JURIDICA RESPONSABILA a grupului fiscal in domeniul impozitului pe profit
(Cod fiscal, Cap. IV^1, art. 42^1-42^11). Fiecare membru depune propriul D101 (cu rubrica "Declaratie
depusa de membrul unui grup fiscal" bifata); persoana responsabila insumeaza rezultatele fiscale ale
membrilor si depune ACEASTA declaratie consolidata. Aplicatia NU are registru de membri de grup, deci
valorile fiscale consolidate (P01-P16) vin din `manual`; identitatea = firma_profil (responsabilul).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, ~/duk/dist/lib/D101GValidator.jar J2.0.0, valabil pentru an
sfarsit de perioada >= 2024: `Validator._dateVersionTable` „2024-01 J2.0.0”), coroborat cu structura ANAF
`anaf_surse/d101g_structura_2025_050526.pdf` (.txt = extrasul ei; static.anaf.ro/…/AplicatiiDec/structura_D101G_2025_050526.pdf,
adusa 21.10.2026). [lotul 11, C70 — refacut pe validatorul v2] Ce scria generatorul inainte si DUK respingea:
  - radacina `<declaratie>` -> „sectiune necunoscuta ('declaratie')”. Validatorul: `DECTag("D101G")`; structura nr.1 `<D101G>`.
  - `d_recN="0"` -> „nu se incadreaza in intervalul cerut”: DUK `d_recN` interval [1,1], optional; structura „d_recN =1,null”.
  - `cod_obligatie="103"` -> „nu se afla in lista”: DUK `Parameters_v1.nomenclat_cod_obl` = {"100"} (structura listeaza si
    102-105, dar validatorul, arbitrul, primeste numai 100).
  - `caen` -> „atribut necunoscut”: atributul e `CAEN` (DUK `nextAttributeInList(nomenclat_caen, "CAEN")`, structura nr.26),
    pe nomenclatorul CAEN al validatorului (probat 21.10.2026: 6920 / 6201 trec, 9999 / 0000 „nu se afla in lista”).
  - `totalPlata_A` = P15 -> „nu se incadreaza in intervalul cerut”: DUK interval [0,0]; structura nr.20 „totalPlata_A =0”.
  - `temei` text liber: DUK interval [1,2]; structura 4b „1-art.105 alin(6) lit.a) din Legea nr.207/2015, 2-… lit.b)”.
  - `functie_declar` taiat la 75: DUK lungime 50 (structura C(50)); lungimile se verifica, nu se taie (datele raman nealterate).
  Atributele v2 (clasa d101gvalidator/v1/Identificare, toate cele 66): Data_S, d_rec, d_recN, d_anulare, temei, cod_obligatie,
  luna_i, an_i, luna, an, d_alte, d_reglem, primul_an_modif, ultimul_an_modif, Data_M, Data_I, scadenta, cod_bug, nr_evid,
  totalPlata_A, nume_declar, prenume_declar, functie_declar, cif, CAEN, denumire, adresa, telefon, fax, email, cifR, denR,
  adrR, telR, faxR, emailR, P01 … P16. Nu exista sectiune de membri in XML-ul consolidat (fiecare membru = propriul D101).

Randuri (formular 101 Grup fiscal, OPANAF 206/2025, anaf_surse/opanaf_206_2025_d101.txt liniile ~928-1073)
mapate pe atribute:
  rd.1  profit impozabil grup           -> P01      rd.11  pierdere fiscala grup            -> P01a
  rd.2  pierdere recuperat ani prec.    -> P02      rd.21  pierdere recuperat an curent     -> P02a
  rd.3  profit impozabil an (1-21)      -> P03      rd.31  pierdere fiscala a anului        -> P03a
  rd.4  impozit pe profit (cota)        -> P04
  rd.5  total credit fiscal (5.1+5.2+5.3)-> P05     rd.5.1 credit fiscal extern            -> P051
  rd.5.2 impozit scutit                 -> P052     rd.5.2.1 art.22 CF -> P0521   rd.5.2.2 art.22^1 -> P0522
  rd.5.3 scutiri/reduceri               -> P053     rd.5.3.1 Legea 566/2004                -> P0531
  rd.6  sponsorizare/mecenat            -> P06      rd.6.1 an curent -> P061   rd.6.2 reportate -> P062
  rd.61 cercetare-dezvoltare 16% (OUG 115/2024) -> P06a
  rd.7  alte sume care se scad          -> P07      rd.8  reducere OUG 153/2020             -> P08
  rd.9  impozit pt comparatie cu IMCA   -> P09      rd.10 impozit la nivelul IMCA (art.18^1)-> P10
  rd.11 impozit anual datorat/IMCA      -> P11
  rd.11.1 (rd4-rd5-rd6-rd7-rd8)>=0      -> P111     rd.11.2 (rd10-rd5.1-rd6.1-rd61)>=0     -> P112
  rd.12 impozit stabilit inspectie      -> P12      rd.13 impozit declarat prin D100        -> P13
  rd.14 diferenta restituire sponsoriz. -> P14
  rd.15 diferenta de plata (rd11+rd14)-(rd12+rd13)>=0     -> P15
  rd.16 diferenta de recuperat (rd12+rd13)-(rd11+rd14)>=0 -> P16

Reguli citite din validator (DUK regula <cod/expresie>), implementate/verificate:
  - DUK regula P02a<=P02 daca P01>0 (altfel P02a=0).
  - DUK regula P111: =(P04-P05-P06-P07-P08) daca P09>P10 si expresia>=0, altfel 0.
  - DUK regula P112: =(P10-P051-P061-P06a) daca P10>P09 si expresia>=0, altfel 0.
  - DUK regula P16: =(P12+P13)-(P11+P14) daca >0, altfel 0 (si P15 = complementul >=0).
  - DUK regula R17 scadenta: d_reglem=1 -> LL+3 (25 martie); d_reglem<>1 -> LL+6 (25 iunie) din Data_S.
  - DUK regula Data_S=31.12.an; Data_S>=Data_I; d_rec=2 daca d_recN=1; temei<>null daca d_anulare=1.

totalPlata_A = suma de control: DUK o cere 0 (interval [0,0]; structura nr.20 „totalPlata_A =0”). Diferenta de plata
ramane la rd.15 (P15); `RezultatD101G.total_plata_a` e ce se scrie in XML, adica 0.

Contract dXXX (uniform): NS, _cif/_esc, calcul_d101g, pull, erori_generare, build_xml,
genereaza(conn, schema, perioada, manual=None). Valorile din `manual`; cota NU e hardcodata (override).
"""
from __future__ import annotations

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație CONSOLIDATĂ privind impozitul pe profit determinat de GRUPUL FISCAL'

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re
from core import repo_d101g as _repo
from datetime import date as _date
from core import common as _c

NS = "mfp:anaf:dgti:d101g:declaratie:v2"

# DUK regula cod_obligatie: `Parameters_v1.nomenclat_cod_obl` = {"100"} (orice alta valoare: „nu se afla in lista”); tot el e
# poz.3-5 din nr_evid (structura nr.19 „Poz.3-5 : cod_obligatie”).
_COD_OBLIGATIE_D101G = ("100",)
_COD_OBLIGATIE_DEFAULT = "100"
_COD_BUG_DEFAULT = "5503XXXXXX"          # structura nr.18: cod_bug C(10) „5503XXXXXX” (X-uri literale, ca la D101)
# structura 4b: temei N(1) — „1-art.105 alin(6) lit.a) din Legea nr.207/2015”, „2-art.105 alin(6) lit.b) din Legea nr.207/2015”
# (DUK `temei` interval [1,2], obligatoriu cand d_anulare=1 — DUK regula R4b).
TEMEIURI_ANULARE = {1: "CPF art.105 alin.(6) lit.a", 2: "CPF art.105 alin.(6) lit.b"}
#: primul an acoperit de validatorul v2 (J2.0.0, „2024-01”); 2022-2023 au structura veche (namespace v1, J1.0.1).
AN_SCHEMA_V2 = 2024
# Lungimile maxime din DUK (`nextAttribute(nume, lungime, …)`) = structura (C(n)); peste ele DUK respinge. Se verifica, nu se taie.
LIMITE_XSD_D101G = (("nume", "denumirea", 200), ("adresa", "adresa", 1000), ("telefon", "telefonul", 15), ("email", "e-mailul", 200),
            ("declarant_nume", "numele declarantului", 75), ("declarant_prenume", "prenumele declarantului", 75),
            ("declarant_functie", "funcția declarantului", 50))
_NEDIGIT = re.compile(r"\D")

# Campuri de INTRARE (valori fiscale consolidate furnizate de persoana responsabila). Restul (P03, P04,
# P05, P052, P053, P06, P09, P111, P112, P11, P15, P16) se CALCULEAZA din formulele oficiale.
_P_INTRARI = {
    "P01", "P01a", "P02", "P02a",
    "P051", "P0521", "P0522", "P0531",
    "P061", "P062", "P06a",
    "P07", "P08", "P10",
    "P12", "P13", "P14",
}
# Randuri de intrare cu regula "Pn>=0" (sume, N(15) fara semn). Se verifica PRE-DUK.
_NENEG = tuple(sorted(_P_INTRARI))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _i(x):
    """Intreg cu rotunjire half-up (Decimal.quantize), fara pierderi binare."""
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


@dataclass
class RezultatD101G:
    an: int
    prof: dict = field(default_factory=dict)
    P: dict = field(default_factory=dict)
    total_plata_a: int = 0
    cod_obligatie: str = _COD_OBLIGATIE_DEFAULT
    cod_bug: str = _COD_BUG_DEFAULT
    d_reglem: int = 0
    d_rec: int = 0
    d_recN: int = 0
    d_anulare: int = 0
    d_alte: int = 0
    temei: int = 0
    rectificativa: object = None   # [lotul 11, C77] mențiunea de pe ecran („Rectificativă la declarația depusă …”), None la inițială


def calcul_d101g(prof, an, intrari=None, cota=None, cod_obligatie=_COD_OBLIGATIE_DEFAULT,
                 cod_bug=_COD_BUG_DEFAULT, d_reglem=0, d_recN=0, d_anulare=0, d_alte=0, temei=0, rect=0):
    """Calculeaza randurile consolidate P01-P16 din `intrari` (chei din _P_INTRARI). Formulele urmeaza
    formularul oficial (OPANAF 206/2025) SI conditiile validatorului (D101GValidator.jar, pachet v1)."""
    I = dict(intrari or {})
    if str(cod_obligatie) not in _COD_OBLIGATIE_D101G:
        raise ValueError("D101G: codul de obligație %s nu e acceptat de validatorul ANAF (lista: %s)." % (
            cod_obligatie, ", ".join(_COD_OBLIGATIE_D101G)))
    if int(an) < AN_SCHEMA_V2:
        raise ValueError("D101G pe %d: anii dinainte de %d au altă structură ANAF (validatorul J1.0.1); aplicația generează "
                         "numai structura în vigoare de la %d." % (int(an), AN_SCHEMA_V2, AN_SCHEMA_V2))
    necunoscute = [k for k in I if k not in _P_INTRARI]
    if necunoscute:
        raise ValueError("D101G intrări necunoscute: %s (permise: %s)" % (sorted(necunoscute), sorted(_P_INTRARI)))
    for k in _NENEG:
        if _i(I.get(k, 0)) < 0:
            raise ValueError("D101G: %s = %d < 0 (DUK regula %s>=0). Corectează valoarea consolidată." % (
                k, _i(I.get(k, 0)), k))
    # cota impozitului pe profit (override prin manual["cota"]) din registru, ca la D101 (`d101._cota_profit`): CF art.17 la 1 ianuarie
    # a anului declarației. [R3a, 11.10.2026] Până atunci, `COTA_STANDARD = 16` ancorat aici dubla `COTE["impozit_profit"]`.
    cota = Decimal(str(cota if cota is not None else _c.cota("impozit_profit", _date(an, 1, 1))[0] * 100))
    g = lambda k: _i(I.get(k, 0))

    P = {}
    P["P01"] = g("P01")                                  # profit impozabil al grupului
    P["P01a"] = g("P01a")                                # pierdere fiscala a grupului
    P["P02"] = g("P02")                                  # pierdere de recuperat din anii precedenti
    # DUK regula P02a<=P02 daca P01>0; altfel P02a=0
    if P["P01"] > 0:
        P["P02a"] = g("P02a")
        if P["P02a"] > P["P02"]:
            raise ValueError("D101G: P02a = %d > P02 = %d (DUK regula P02a<=P02 când P01>0)." % (P["P02a"], P["P02"]))
    else:
        P["P02a"] = 0
    # rd.3 = rd.1 - rd.21 (profit impozabil aferent anului); rd.31 = pierderea anului (preia rd.11)
    if P["P01"] > 0:
        P["P03"] = max(P["P01"] - P["P02a"], 0)
        P["P03a"] = 0
    else:
        P["P03"] = 0
        P["P03a"] = P["P01a"]
    P["P04"] = _i(Decimal(P["P03"]) * cota / 100)        # impozit pe profit = cota% x profit impozabil an
    # rd.5 credit fiscal total (5.1 + 5.2 + 5.3); subtotalele "din care" insumate din detaliu
    P["P051"] = g("P051")
    P["P0521"] = g("P0521"); P["P0522"] = g("P0522")
    P["P052"] = P["P0521"] + P["P0522"]
    P["P0531"] = g("P0531")
    P["P053"] = P["P0531"]
    P["P05"] = P["P051"] + P["P052"] + P["P053"]
    # rd.6 sponsorizare (6.1 an curent + 6.2 reportat); rd.61 cercetare-dezvoltare
    P["P061"] = g("P061"); P["P062"] = g("P062")
    P["P06"] = P["P061"] + P["P062"]
    P["P06a"] = g("P06a")
    P["P07"] = g("P07")                                  # alte sume care se scad
    P["P08"] = g("P08")                                  # reducere OUG 153/2020
    # rd.9 impozit pt comparatie cu IMCA = rd4-rd5-rd6-rd7-rd8; rd.10 IMCA (art.18^1) = intrare
    P["P09"] = P["P04"] - P["P05"] - P["P06"] - P["P07"] - P["P08"]
    P["P10"] = g("P10")
    # rd.11.1 / rd.11.2: ramura activa dupa comparatia impozit pe profit vs IMCA
    expr111 = P["P04"] - P["P05"] - P["P06"] - P["P07"] - P["P08"]
    expr112 = P["P10"] - P["P051"] - P["P061"] - P["P06a"]
    P["P111"] = expr111 if (P["P09"] > P["P10"] and expr111 >= 0) else 0
    P["P112"] = expr112 if (P["P10"] > P["P09"] and expr112 >= 0) else 0
    P["P11"] = P["P111"] + P["P112"]                     # impozit pe profit anual datorat/IMCA anual
    P["P12"] = g("P12")                                  # impozit stabilit in urma inspectiei fiscale
    P["P13"] = g("P13")                                  # impozit declarat prin D100
    P["P14"] = g("P14")                                  # diferenta la restituire sponsorizare/bursa/mecenat
    dif = (P["P11"] + P["P14"]) - (P["P12"] + P["P13"])
    P["P15"] = dif if dif > 0 else 0                     # rd.15 diferenta de impozit de plata (>=0)
    P["P16"] = -dif if dif < 0 else 0                    # rd.16 diferenta de impozit de recuperat (>=0)

    total = 0                                            # totalPlata_A: DUK interval [0,0], structura nr.20 „totalPlata_A =0”
    Pnz = {k: v for k, v in P.items() if v}              # se emit doar randurile nenule
    return RezultatD101G(an=an, prof=prof, P=Pnz, total_plata_a=total,
                         cod_obligatie=str(cod_obligatie), cod_bug=str(cod_bug),
                         d_reglem=int(d_reglem or 0), d_rec=(2 if int(d_recN or 0) == 1 else int(rect or 0)),   # [lotul 11, C77] structura D101G: „d_rec =(0,1,2) … 1-rectificativa”
                         d_recN=int(d_recN or 0), d_anulare=int(d_anulare or 0),
                         d_alte=int(d_alte or 0), temei=int(temei or 0))


def _scadenta(an, d_reglem):
    """Scadenta platii (zi, luna, an) din Data_S=31.12.an. DUK regula R17: d_reglem=1 -> LL+3 (25 martie);
    d_reglem<>1 -> LL+6 (25 iunie). Confirmat in validator (mesaje 'daca d_reglem=1 atunci LL=LL+3')."""
    ll = 12 + (3 if int(d_reglem or 0) == 1 else 6)
    scad_an = an + 1
    if ll > 12:
        ll -= 12
    return 25, ll, scad_an


def _nr_evid(cod_oblig, an, d_reglem):
    """Numar de evidenta a platii, 23 caractere (DUK regula nr_evid, poz1_2..poz22_23):
    poz1-2='11', poz3-5=cod_obligatie, poz6-7='01', poz8-11=LLAA (sfarsit perioada=12.AA),
    poz12-17=ZZLLAA (scadenta), poz18='0' (fara data lichidare), poz19-21='000',
    poz22-23 = ultimele 2 cifre din suma primelor 21 (cifra de control)."""
    _zz, scad_luna, scad_an = _scadenta(an, d_reglem)
    p1_21 = ("11" + str(cod_oblig).rjust(3, "0")[-3:] + "01" +
             "%02d%02d" % (12, an % 100) +
             "%02d%02d%02d" % (25, scad_luna, scad_an % 100) + "0" + "000")
    assert len(p1_21) == 21
    suma = sum(int(c) for c in p1_21)
    return p1_21 + "%02d" % (suma % 100)


def _erori_lungime(prof):
    """Lungimile maxime ale validatorului (`LIMITE_XSD_D101G`): peste ele DUK respinge, iar a taia ar altera datele firmei."""
    erori = []
    for cheie, eticheta, maxim in LIMITE_XSD_D101G:
        v = str(prof.get(cheie) or "").strip()
        if len(v) > maxim:
            erori.append("D101G: %s are %s; formularul ANAF primește cel mult %s. Scurtează-l în Date firmă." % (
                eticheta, _c.cate(len(v), "caracter", "caractere"), _c.cate(maxim, "caracter", "caractere")))
    return erori


def erori_generare(prof):
    erori = []
    _cui = _cif(prof.get("cui"))
    if not _cui:
        erori.append("Lipsă CUI persoana juridică responsabilă (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("Lipsă denumire persoana juridică responsabilă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("Lipsă adresa domiciliu fiscal (obligatorie).")
    _caen = (prof.get("caen") or "").strip()
    if not _caen:
        erori.append("Lipsă cod CAEN (obligatoriu în D101G).")
    elif not re.fullmatch(r"\d{4}", _caen):
        erori.append("D101G: cod CAEN invalid (%s): trebuie exact 4 cifre — N(4). Corectează în Profil firma." % _caen)
    erori.extend(_erori_lungime(prof))
    # [lotul 10, deficiența C69 — „valoare inventată pe documentul ANAF în loc de blocaj”] Declarantul: aceeași poartă ca la D101
    # (`firma_profil_api.erori_declarant`). Sursa, în lipsa unei structuri D101G în anaf_surse/: validatorul ANAF D101G v2 instalat
    # (~/duk/dist/lib/D101GValidator.jar, J2.0.0 — sha256 identic cu cel publicat de ANAF la update5/D101G_3), probat 20.10.2026 pe XML
    # sintetic fără câmp: „eroare atribut: nume_declar: atributul trebuie sa existe” (la fel `prenume_declar`, `functie_declar`). Până azi
    # generatorul scria „ADMINISTRATOR” / „-” în locul lor.
    from core.firma_profil_api import erori_declarant
    erori.extend(erori_declarant(prof))
    return erori


def build_xml(res):
    """Emite <D101G> cu toate campurile ca ATRIBUTE (ca la D101; validatorul respinge randurile P ca elemente-copil).
    Radacina: DUK `DECTag("D101G")` + structura nr.1 `<D101G>` (C70: era `<declaratie>`)."""
    prof = res.prof
    an = res.an
    cif_num = _cif(prof.get("cui"))
    zz, scad_luna, scad_an = _scadenta(an, res.d_reglem)
    a = []
    a.append('an="%d" luna="12" an_i="%d" luna_i="1"' % (an, an))
    a.append('Data_I="01.01.%d" Data_S="31.12.%d"' % (an, an))
    a.append('d_rec="%d" d_reglem="%d" d_anulare="%d" d_alte="%d"' % (res.d_rec, res.d_reglem, res.d_anulare, res.d_alte))
    if res.d_recN == 1:                                   # DUK `d_recN` interval [1,1], optional; structura „d_recN =1,null”
        a.append('d_recN="1"')
    a.append('cod_obligatie="%s" cod_bug="%s"' % (res.cod_obligatie, res.cod_bug))
    a.append('nr_evid="%s" scadenta="%02d%02d%02d"' % (
        _nr_evid(res.cod_obligatie, an, res.d_reglem), zz, scad_luna, scad_an % 100))
    a.append('totalPlata_A="%d"' % res.total_plata_a)
    if res.d_anulare == 1:
        if res.temei not in TEMEIURI_ANULARE:              # DUK R4b + `temei` interval [1,2]
            raise ValueError("D101G: la anulare temeiul e 1 (%s) sau 2 (%s)." % (TEMEIURI_ANULARE[1], TEMEIURI_ANULARE[2]))
        a.append('temei="%d"' % res.temei)
    # [lotul 10, C69] declarantul din Date firmă / din `manual`, fără „ADMINISTRATOR” / „-” (lipsa îl oprește în `erori_generare`)
    from core.firma_profil_api import erori_declarant
    _er_decl = erori_declarant(prof)
    if _er_decl:
        raise ValueError("D101G nu se poate genera: " + " ".join(_er_decl))
    _er_lung = _erori_lungime(prof)
    if _er_lung:                                          # lungimile DUK: se opresc, nu se taie
        raise ValueError(" ".join(_er_lung))
    a.append('nume_declar=%s prenume_declar=%s functie_declar=%s' % (
        _esc(str(prof["declarant_nume"]).strip()),
        _esc(str(prof["declarant_prenume"]).strip()),
        _esc(str(prof["declarant_functie"]).strip())))
    a.append('cif="%s" denumire=%s adresa=%s' % (
        cif_num, _esc((prof.get("nume") or "").strip()), _esc((prof.get("adresa") or "").strip())))
    caen = (prof.get("caen") or "").strip()
    if caen:                                              # DUK `CAEN` (majuscule), obligatoriu; structura nr.26
        a.append('CAEN=%s' % _esc(caen))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        a.append('telefon=%s' % _esc(tel))
    email = (prof.get("email") or "").strip()
    if email:
        a.append('email=%s' % _esc(email))

    def _ordine(k):
        m = re.match(r"P(\d+)([a-z]?)(\d*)", k)
        return (int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (999, "", 0)
    for k in sorted(res.P.keys(), key=_ordine):
        a.append('%s="%d"' % (k, res.P[k]))

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D101G xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="%s" xsi:schemaLocation="%s D101G.xsd" %s/>\n' % (NS, NS, " ".join(a)))


def pull(conn, schema, perioada):
    """Identitatea persoanei juridice responsabile a grupului (firma_profil). Valorile consolidate P01-P16
    NU se afla in balanta contabila a responsabilului (sunt insumarea rezultatelor membrilor) - vin din
    `manual`. Cand conn=None, se lucreaza integral din `manual` (identitatea vine tot din manual)."""
    if conn is None:
        return {}
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        prof = _repo.select_firma_profil(cur) or {}
    if prof.get("oras"):
        prof["adresa"] = " ".join(x for x in (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
    return prof


def genereaza(conn, schema, perioada, manual=None):
    """D101G consolidat anual. `manual` = valorile fiscale consolidate (chei P01..P14 din _P_INTRARI) +
    optional cota/cod_obligatie/cod_bug/d_reglem/d_recN/d_anulare/d_alte/temei + suprascrieri de identitate
    (cui/nume/adresa/caen/telefon/email/declarant_*). O cheie P necunoscuta e respinsa (typo != tacut)."""
    manual = dict(manual or {})
    cota = manual.pop("cota", None)
    cod_obligatie = str(manual.pop("cod_obligatie", _COD_OBLIGATIE_DEFAULT))
    cod_bug = str(manual.pop("cod_bug", _COD_BUG_DEFAULT))
    d_reglem = int(manual.pop("d_reglem", 0) or 0)
    d_recN = int(manual.pop("d_recN", 0) or 0)
    # [lotul 11, C77] rectificativa: depunerile înregistrate pe an (orice sursă) sau bifa din formular (`core.rectificativa`)
    from core import rectificativa as _rect
    _st_rect = _rect.stabileste(conn, schema, "d101g", perioada.an, bifata=_rect.bifata({"d_rec": manual.pop("d_rec", 0)}))
    d_anulare = int(manual.pop("d_anulare", 0) or 0)
    d_alte = int(manual.pop("d_alte", 0) or 0)
    temei = manual.pop("temei", 0) or 0
    try:
        temei = int(temei)
    except (TypeError, ValueError):
        raise ValueError("D101G: temeiul anulării e 1 (%s) sau 2 (%s), nu „%s”." % (
            TEMEIURI_ANULARE[1], TEMEIURI_ANULARE[2], temei))
    # suprascrieri / sursa de identitate din manual (cand nu exista DB sau se corecteaza profilul)
    ident = {}
    for k in ("cui", "nume", "adresa", "caen", "telefon", "email",
              "declarant_nume", "declarant_prenume", "declarant_functie"):
        if k in manual:
            ident[k] = manual.pop(k)

    prof = pull(conn, schema, perioada)
    prof = dict(prof or {})
    prof.update(ident)
    if d_anulare == 1 and temei not in TEMEIURI_ANULARE:
        raise ValueError("D101G: la o declarație depusă după anularea rezervei verificării ulterioare se alege temeiul: 1 (%s) "
                         "sau 2 (%s); validatorul ANAF o respinge fără el." % (TEMEIURI_ANULARE[1], TEMEIURI_ANULARE[2]))
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))
    res = calcul_d101g(prof, perioada.an, intrari=manual, cota=cota, cod_obligatie=cod_obligatie,
                       cod_bug=cod_bug, d_reglem=d_reglem, d_recN=d_recN, d_anulare=d_anulare,
                       d_alte=d_alte, temei=temei, rect=_st_rect.d_rec)
    res.rectificativa = _st_rect.mentiune
    xml = build_xml(res)
    return xml, res
