# -*- coding: utf-8 -*-
"""core/d101g.py — D101G: Declaratie CONSOLIDATA privind impozitul pe profit determinat de GRUPUL FISCAL.

Depusa de PERSOANA JURIDICA RESPONSABILA a grupului fiscal in domeniul impozitului pe profit
(Cod fiscal, Cap. IV^1, art. 42^1-42^11). Fiecare membru depune propriul D101 (cu rubrica "Declaratie
depusa de membrul unui grup fiscal" bifata); persoana responsabila insumeaza rezultatele fiscale ale
membrilor si depune ACEASTA declaratie consolidata. Aplicatia NU are registru de membri de grup, deci
valorile fiscale consolidate (P01-P16) vin din `manual`; identitatea = firma_profil (responsabilul).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator / D101GValidator.jar), coroborat cu
formularul oficial. Radacina si campurile au fost CITITE din bytecode:
  - namespace v2 = pachet d101gvalidator/v1 (namespace v1 = pachet v0, structura veche P37..P53 - NU se
    foloseste); radacina XML = <declaratie101G>.
  - Atribute (clasa d101gvalidator/v1/Identificare): an, luna, an_i, luna_i, Data_I, Data_S, Data_M (opt),
    d_rec, d_recN, d_reglem, d_anulare, d_alte, cif, denumire, adresa, caen, telefon, email, fax,
    cod_obligatie, cod_bug, nr_evid, scadenta, totalPlata_A, nume_declar, prenume_declar, functie_declar,
    temei (daca d_anulare=1), primul_an_modif/ultimul_an_modif (opt, la rectificativa), P01..P16.
  - Nu exista sectiune de membri in XML-ul consolidat (fiecare membru = propriul D101).

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

totalPlata_A = suma de control: validatorul v2 o preia direct (_sumaControl = totalPlata_A), fara sa o
recalculeze din suma randurilor P (spre deosebire de D101). Se emite = P15 (diferenta de impozit de plata).

Contract dXXX (uniform): NS, _cif/_esc, calcul_d101g, pull, erori_generare, build_xml,
genereaza(conn, schema, perioada, manual=None). Valorile din `manual`; cota NU e hardcodata (override).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d101g:declaratie:v2"

COTA_STANDARD = Decimal("16")            # cota standard impozit pe profit (override prin manual["cota"])
_COD_OBLIGATIE_DEFAULT = "103"           # cod obligatie bugetara impozit pe profit (poz.3-5 din nr_evid)
_COD_BUG_DEFAULT = "5503XXXXXX"          # cod bugetar impozit pe profit (X-uri literale, ca la D101)
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
    temei: str = ""


def calcul_d101g(prof, an, intrari=None, cota=None, cod_obligatie=_COD_OBLIGATIE_DEFAULT,
                 cod_bug=_COD_BUG_DEFAULT, d_reglem=0, d_recN=0, d_anulare=0, d_alte=0, temei=""):
    """Calculeaza randurile consolidate P01-P16 din `intrari` (chei din _P_INTRARI). Formulele urmeaza
    formularul oficial (OPANAF 206/2025) SI conditiile validatorului (D101GValidator.jar, pachet v1)."""
    I = dict(intrari or {})
    necunoscute = [k for k in I if k not in _P_INTRARI]
    if necunoscute:
        raise ValueError("D101G intrari necunoscute: %s (permise: %s)" % (sorted(necunoscute), sorted(_P_INTRARI)))
    for k in _NENEG:
        if _i(I.get(k, 0)) < 0:
            raise ValueError("D101G: %s = %d < 0 (DUK regula %s>=0). Corecteaza valoarea consolidata." % (
                k, _i(I.get(k, 0)), k))
    cota = Decimal(str(cota if cota is not None else COTA_STANDARD))
    g = lambda k: _i(I.get(k, 0))

    P = {}
    P["P01"] = g("P01")                                  # profit impozabil al grupului
    P["P01a"] = g("P01a")                                # pierdere fiscala a grupului
    P["P02"] = g("P02")                                  # pierdere de recuperat din anii precedenti
    # DUK regula P02a<=P02 daca P01>0; altfel P02a=0
    if P["P01"] > 0:
        P["P02a"] = g("P02a")
        if P["P02a"] > P["P02"]:
            raise ValueError("D101G: P02a = %d > P02 = %d (DUK regula P02a<=P02 cand P01>0)." % (P["P02a"], P["P02"]))
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

    total = P["P15"]                                     # totalPlata_A = suma de control (diferenta de plata)
    Pnz = {k: v for k, v in P.items() if v}              # se emit doar randurile nenule
    return RezultatD101G(an=an, prof=prof, P=Pnz, total_plata_a=total,
                         cod_obligatie=str(cod_obligatie), cod_bug=str(cod_bug),
                         d_reglem=int(d_reglem or 0), d_rec=(2 if int(d_recN or 0) == 1 else 0),
                         d_recN=int(d_recN or 0), d_anulare=int(d_anulare or 0),
                         d_alte=int(d_alte or 0), temei=str(temei or ""))


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


def erori_generare(prof):
    erori = []
    _cui = _cif(prof.get("cui"))
    if not _cui:
        erori.append("LIPSA CUI persoana juridica responsabila (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSA denumire persoana juridica responsabila (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSA adresa domiciliu fiscal (obligatorie).")
    _caen = (prof.get("caen") or "").strip()
    if not _caen:
        erori.append("LIPSA cod CAEN (obligatoriu in D101G).")
    elif not re.fullmatch(r"\d{4}", _caen):
        erori.append("D101G: cod CAEN invalid (%s): trebuie exact 4 cifre — N(4). Corecteaza in Profil firma." % _caen)
    return erori


def build_xml(res):
    """Emite <declaratie101G> cu toate campurile ca ATRIBUTE (ca la D101; validatorul respinge randurile
    P ca elemente-copil). Radacina confirmata din bytecode: declaratie101G."""
    prof = res.prof
    an = res.an
    cif_num = _cif(prof.get("cui"))
    zz, scad_luna, scad_an = _scadenta(an, res.d_reglem)
    a = []
    a.append('an="%d" luna="12" an_i="%d" luna_i="1"' % (an, an))
    a.append('Data_I="01.01.%d" Data_S="31.12.%d"' % (an, an))
    a.append('d_rec="%d" d_recN="%d" d_reglem="%d" d_anulare="%d" d_alte="%d"' % (
        res.d_rec, res.d_recN, res.d_reglem, res.d_anulare, res.d_alte))
    a.append('cod_obligatie="%s" cod_bug="%s"' % (res.cod_obligatie, res.cod_bug))
    a.append('nr_evid="%s" scadenta="%02d%02d%02d"' % (
        _nr_evid(res.cod_obligatie, an, res.d_reglem), zz, scad_luna, scad_an % 100))
    a.append('totalPlata_A="%d"' % res.total_plata_a)
    if res.d_anulare == 1 and res.temei:
        a.append('temei=%s' % _esc(res.temei))
    a.append('nume_declar=%s prenume_declar=%s functie_declar=%s' % (
        _esc((prof.get("declarant_nume") or "ADMINISTRATOR")[:75]),
        _esc((prof.get("declarant_prenume") or "-")[:75]),
        _esc((prof.get("declarant_functie") or "ADMINISTRATOR")[:75])))
    a.append('cif="%s" denumire=%s adresa=%s' % (
        cif_num, _esc((prof.get("nume") or "")[:200]), _esc((prof.get("adresa") or "")[:200])))
    caen = (prof.get("caen") or "").strip()
    if caen:
        a.append('caen=%s' % _esc(caen))
    tel = (prof.get("telefon") or "").strip()
    if tel:
        a.append('telefon=%s' % _esc(tel[:15]))
    email = (prof.get("email") or "").strip()
    if email:
        a.append('email=%s' % _esc(email[:60]))

    def _ordine(k):
        m = re.match(r"P(\d+)([a-z]?)(\d*)", k)
        return (int(m.group(1)), m.group(2), int(m.group(3) or 0)) if m else (999, "", 0)
    for k in sorted(res.P.keys(), key=_ordine):
        a.append('%s="%d"' % (k, res.P[k]))

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="%s" xsi:schemaLocation="%s D101G.xsd" %s/>\n' % (NS, NS, " ".join(a)))


def pull(conn, schema, perioada):
    """Identitatea persoanei juridice responsabile a grupului (firma_profil). Valorile consolidate P01-P16
    NU se afla in balanta contabila a responsabilului (sunt insumarea rezultatelor membrilor) - vin din
    `manual`. Cand conn=None, se lucreaza integral din `manual` (identitatea vine tot din manual)."""
    if conn is None:
        return {}
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, caen, telefon, email, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
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
    d_anulare = int(manual.pop("d_anulare", 0) or 0)
    d_alte = int(manual.pop("d_alte", 0) or 0)
    temei = str(manual.pop("temei", "") or "")
    # suprascrieri / sursa de identitate din manual (cand nu exista DB sau se corecteaza profilul)
    ident = {}
    for k in ("cui", "nume", "adresa", "caen", "telefon", "email",
              "declarant_nume", "declarant_prenume", "declarant_functie"):
        if k in manual:
            ident[k] = manual.pop(k)

    prof = pull(conn, schema, perioada)
    prof = dict(prof or {})
    prof.update(ident)
    if d_anulare == 1 and not temei:
        raise ValueError("D101G: d_anulare=1 cere `temei` (DUK regula temei<>null cand d_anulare bifat).")
    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))
    res = calcul_d101g(prof, perioada.an, intrari=manual, cota=cota, cod_obligatie=cod_obligatie,
                       cod_bug=cod_bug, d_reglem=d_reglem, d_recN=d_recN, d_anulare=d_anulare,
                       d_alte=d_alte, temei=temei)
    xml = build_xml(res)
    return xml, res
