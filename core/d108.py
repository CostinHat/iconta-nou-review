# -*- coding: utf-8 -*-
"""core/d108.py — D108: Declaratie privind impozitul pe reprezentanta.

Reprezentanta unei/unor persoane juridice straine infiintata in Romania datoreaza un impozit
ANUAL FIX pe reprezentanta. Sursa semanticii SI a valorii (VERIFICAT la sursa, 14.08.2026):
  Cod fiscal (Legea 227/2015), Titlul VI "Impozitul pe reprezentante" -
  anaf_surse/cod_fiscal_227_2015_consolidat.txt:
    L15801: "Impozitul pe reprezentanta pentru un an fiscal este de 18.000 lei."
    L15811: se declara si se plateste pana in ultima zi a lunii februarie a anului de impunere.
    L15815: reprezentanta desfiintata in cursul anului recalculeaza impozitul pentru perioada de
            activitate de la inceputul anului pana la data de 1 a lunii urmatoare celei in care se
            desfiinteaza si depune declaratia in termen de 30 de zile.
  (forma initiala art.235-237, anaf_surse/cf_2015_forma_initiala.txt:8068-8088, aceeasi semantica;
   cuantumul de acolo, 4.000 euro, a fost modificat ulterior la 18.000 lei fix - vezi consolidatul.)

STRUCTURA = VALIDATORUL OFICIAL D108Validator.jar (pachet d108validator/v0, namespace
mfp:anaf:dgti:d108:declaratie:v1), CITITA din bytecode (clasele D108 / ValidatorImpl / Pdf_v0)
si PROBATA camp cu camp pe DUKIntegrator (cazurile anual / infiintare / desfiintare => toate "ok"):
  - Radacina XML = <D108> (numele sectiunii DEC). NU "declaratie"/"declaratie108" (respinse:
    "sectiune necunoscuta"). Atributele perioadei sunt `an` si `luna` (formularul PDF le eticheteaza
    an_r/luna_r, dar atributele XML se numesc an/luna). luna = 12 (declaratie anuala).
  - Atribute plate pe radacina: an, luna, d_rec, bifainfr, bifadesfr, cif, den, adresaS, telefon,
    fax, email, datai, dataincetarii, scadenta, sumaimp, nr_evid, nume, prenume, functie, totalPlata_A.
  - bifainfr si bifadesfr sunt OBLIGATORII ca prezenta (implicit "0"); cel mult una poate fi "1".
    nr_evid OBLIGATORIU (23 caractere, format NEP - vezi _nr_evid).

Reguli probate pe validator (D108.class):
  - datai <-> bifainfr, dataincetarii <-> bifadesfr (completate impreuna); cel mult o bifa.
  - R5/R6: an = anul din datai (infiintare) / anul din scadenta (rest).
  - R15.1: anual (fara bife) => scadenta = ultima zi a lunii februarie a anului (ex. 28.02.2025).
  - R15.2: infiintare => scadenta = datai + 30 de zile. R15.3: desfiintare => scadenta = dataincetarii.
  - R18.1: anual => impozit = 18.000 lei. R18.2/R18.3: proportional pe lunile de activitate.
  - TotalPlata_A trebuie sa fie egal cu sumaimp.

Contract dXXX: NS, _cif/_esc, calcul_d108, pull, erori_generare, build_xml, genereaza.
Valoarea impozitului NU se fabrica: e suma legala fixa (18.000 lei), impusa si de validator (R18);
`impozit_anual` permite override doar daca legea/validatorul se schimba. `sumaimp` explicit in manual
e respectat ca atare (raspunderea platitorului), altfel se calculeaza din suma legala.
"""
from core.identitate import valideaza_cui as _valideaza_cui  # checksum CUI (sursa canonica, read-only)
from datetime import date as _date, timedelta as _timedelta
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import calendar
import re

def _dmy(d):
    """Data la dd.mm.yyyy fara strftime pe %d (gard BACKEND_UI_BRUT): formatare aritmetica."""
    return "%02d.%02d.%04d" % (d.day, d.month, d.year)

NS = "mfp:anaf:dgti:d108:declaratie:v1"

IMPOZIT_ANUAL = 18000     # CF (L227/2015) Titlul VI: 18.000 lei / an fiscal (consolidat L15801)
COD_OBLIG = "160"         # (160) Impozit pe reprezentanta (eticheta din formular + cod in nr_evid)
_NEDIGIT = re.compile(r"\D")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _parse_data(s):
    """ZZ.LL.AAAA -> date (None daca lipseste/invalid)."""
    s = str(s or "").strip()
    if not s:
        return None
    try:
        z, l, a = [int(x) for x in s.split(".")]
        return _date(a, l, z)
    except (ValueError, TypeError):
        return None


def _tip(manual):
    """anual | infiintare | desfiintare. Prioritate: `tip` explicit, apoi datai / dataincetarii."""
    t = str(manual.get("tip") or "").strip().lower()
    if t in ("anual", "infiintare", "desfiintare"):
        return t
    if manual.get("datai"):
        return "infiintare"
    if manual.get("dataincetarii"):
        return "desfiintare"
    return "anual"


def _nr_evid(an, scad):
    """Numar de evidenta a platii, 23 caractere (format oficial NEP, probat pe DUK D108):
    poz.1-2 '10', poz.3-5 cod obligatie '160', poz.6-7 '01', poz.8-9 '12' (perioada anuala),
    poz.10-11 AA (anul de impunere), poz.12-17 ZZLLAA (scadenta), poz.18-21 '0000',
    poz.22-23 = ultimele doua cifre din suma primelor 21. Confirmat pe exemplarul din validator
    (10160011218280218000042) si pe cele 3 probe DUK."""
    p1_21 = ("10" + COD_OBLIG + "01" + "%02d%02d" % (12, an % 100) +
             "%02d%02d%02d" % (scad.day, scad.month, scad.year % 100) + "0000")
    assert len(p1_21) == 21, p1_21
    return p1_21 + "%02d" % (sum(int(c) for c in p1_21) % 100)


def calcul_d108(manual):
    """Impozit (18.000 lei/an, proportional pe lunile active) + scadenta + nr_evid.
    Valoarea NU se fabrica: e suma fixa legala (CF Titlul VI), impusa si de validator (R18).
    Daca `manual` da explicit `sumaimp`, se foloseste ca atare (raspunderea platitorului)."""
    tip = _tip(manual)
    imp_an = int(manual.get("impozit_anual") or IMPOZIT_ANUAL)
    if tip == "infiintare":
        di = _parse_data(manual.get("datai"))
        an, scad, luni = di.year, di + _timedelta(days=30), 12 - di.month + 1
    elif tip == "desfiintare":
        dc = _parse_data(manual.get("dataincetarii"))
        an, scad, luni = dc.year, dc, dc.month
    else:
        an = int(manual.get("an"))
        scad, luni = _date(an, 2, calendar.monthrange(an, 2)[1]), 12
    if manual.get("sumaimp") not in (None, ""):
        sumaimp = int(_cif(manual.get("sumaimp")))
    else:
        sumaimp = _i(Decimal(imp_an) * Decimal(luni) / Decimal(12))
    return {
        "tip": tip, "an": an, "luna": 12,
        "scadenta": scad, "scadenta_str": _dmy(scad),
        "luni_active": luni, "sumaimp": sumaimp, "totalPlata_A": sumaimp,
        "nr_evid": _nr_evid(an, scad),
    }


def pull(conn, schema, perioada):
    """D108 este declaratia reprezentantei unei persoane juridice straine; datele (denumire, CF/NIF,
    domiciliu fiscal, reprezentant legal) vin din `manual`. Contractul dXXX cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not _valideaza_cui(_cif(manual.get("cif")))[0]:
        er.append("CF/CUI reprezentanta (cif) invalid - cifra de control eronata.")
    if not _esc(manual.get("den")):
        er.append("Lipsă denumire reprezentanta / persoana juridica străină (den).")
    if not _esc(manual.get("adresaS")):
        er.append("Lipsă domiciliu fiscal (adresaS).")
    for c in ("nume", "prenume", "functie"):
        if not _esc(manual.get(c)):
            er.append("Lipsă %s reprezentant legal (%s)." % (c, c))
    tip = _tip(manual)
    if tip == "infiintare" and _parse_data(manual.get("datai")) is None:
        er.append("Infiintare: data infiintarii (datai) lipsă/invalidă - aștept ZZ.LL.AAAA.")
    if tip == "desfiintare" and _parse_data(manual.get("dataincetarii")) is None:
        er.append("Desfiintare: data desfiintarii (dataincetarii) lipsă/invalidă - aștept ZZ.LL.AAAA.")
    if tip == "anual":
        try:
            int(manual.get("an"))
        except (TypeError, ValueError):
            er.append("An de impunere (an) lipsă/invalid.")
    return er


def build_xml(prof, an, luna, manual):
    c = calcul_d108(manual)
    tip = c["tip"]
    a = []
    a.append('an="%d"' % c["an"])
    a.append('luna="%d"' % c["luna"])
    a.append('d_rec="%s"' % (_cif(manual.get("d_rec")) or "0"))
    a.append('bifainfr="%d"' % (1 if tip == "infiintare" else 0))
    a.append('bifadesfr="%d"' % (1 if tip == "desfiintare" else 0))
    a.append('cif="%s"' % _cif(manual.get("cif")))
    a.append('den="%s"' % _esc(manual.get("den"), 200))
    a.append('adresaS="%s"' % _esc(manual.get("adresaS"), 200))
    if _esc(manual.get("telefon")):
        a.append('telefon="%s"' % _esc(manual.get("telefon"), 15))
    if _esc(manual.get("fax")):
        a.append('fax="%s"' % _esc(manual.get("fax"), 15))
    if _esc(manual.get("email")):
        a.append('email="%s"' % _esc(manual.get("email"), 250))
    if tip == "infiintare":
        a.append('datai="%s"' % _dmy(_parse_data(manual.get("datai"))))
    if tip == "desfiintare":
        a.append('dataincetarii="%s"' % _dmy(_parse_data(manual.get("dataincetarii"))))
    a.append('scadenta="%s"' % c["scadenta_str"])
    a.append('sumaimp="%d"' % c["sumaimp"])
    a.append('nr_evid="%s"' % c["nr_evid"])
    a.append('nume="%s"' % _esc(manual.get("nume"), 75))
    a.append('prenume="%s"' % _esc(manual.get("prenume"), 75))
    a.append('functie="%s"' % _esc(manual.get("functie"), 75))
    a.append('totalPlata_A="%d"' % c["totalPlata_A"])
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D108 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


@dataclass
class RezultatD108:
    an: int
    luna: int
    tip: str = "anual"
    sumaimp: int = 0
    total_plata_a: int = 0
    scadenta: str = ""
    nr_evid: str = ""
    avertismente: list = field(default_factory=list)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    manual.setdefault("an", int(perioada.an))
    er = erori_generare(pull(conn, schema, perioada), manual)
    if er:
        raise ValueError("D108 nu se poate genera: " + " ".join(er))
    c = calcul_d108(manual)
    xml = build_xml({}, c["an"], c["luna"], manual)
    res = RezultatD108(an=c["an"], luna=c["luna"], tip=c["tip"], sumaimp=c["sumaimp"],
                       total_plata_a=c["totalPlata_A"], scadenta=c["scadenta_str"],
                       nr_evid=c["nr_evid"])
    return xml, res
