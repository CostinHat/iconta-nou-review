"""core/d130.py — D130: Decont privind impozitul la titeiul din productia interna.

Plateste impozit la titeiul (si, istoric, gazele naturale) din productia interna. Impozitul se
datoreaza pentru cantitatile LIVRATE; in decont se inscriu sumele CUMULATE pentru anul de raportare
(OPANAF 1950/2012, Anexa 10 — instructiuni; Cod fiscal L227/2015, Titlul VIII). Depunere ANUALA, pana
la 30 aprilie a anului urmator. Formularul curent (validat de DUK) e pe TITEI (o singura linie:
cantitate_titei / impozit_datorat), nu pe doua produse ca modelul vechi titei+gaze.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D130Validator.jar, pachet d130validator/v0, clasa
Declaratie130). Radacina XML `declaratie130`, namespace `mfp:anaf:dgti:d130:declaratie:v1` — CITITE din
bytecode si PROBATE camp cu camp pe DUKIntegrator. Atribute (ordinea din clasa): luna, an, d_rec,
nume_declar, prenume_declar, functie_declar, cui, denumire, adresa, telefon, fax, email, totalPlata_A,
cantitate_titei, impozit_datorat. Regula sumei de control (citita din validator): totalPlata_A = suma
de control calculata = impozit_datorat.

ATENTIE periodicitate: actul (OPANAF 1950/2012 + formular) prevede depunere ANUALA (sume cumulate pe an,
scadenta 30 aprilie). Perioada de raportare (an, luna) vine din `perioada`; luna e pastrata ca in
program (validatorul o cere in interval 1..12). Nu se hardcodeaza nivelul impozitului pe titei —
cantitatea si impozitul vin din `manual` (contribuabilul le calculeaza dupa cota legala aplicabila).

Contract dXXX: pull/erori_generare/calcul_d130/build_xml/genereaza(conn, schema, perioada).
NEPOPULAT deliberat: identitatea platitorului (cui/denumire/adresa/contact) NU se trage din registru
(pull()=={}) — vine integral din `manual`; nivelul cotei de impozit (se calculeaza in afara modulului).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import re

NS = "mfp:anaf:dgti:d130:declaratie:v1"
_NEDIGIT = re.compile(r"\D")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _suma(x):
    """Rotunjire half-up pe SUME (Decimal.quantize ROUND_HALF_UP), rezultat intreg (lei / tona)."""
    if x in (None, ""):
        return 0
    try:
        d = Decimal(str(x).replace(",", "."))
    except (InvalidOperation, ValueError):
        return 0
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Rezultat130:
    an: int
    luna: int
    cantitate_titei: int = 0
    impozit_datorat: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d130(manual):
    """cantitate_titei si impozit_datorat vin din input (contribuabilul aplica cota legala).
    Suma de control totalPlata_A = cantitate_titei + impozit_datorat (DUK regula R13 a validatorului:
    suma cumulata a tuturor campurilor numerice din sectiunea B — PROBAT pe DUK)."""
    q = _suma(manual.get("cantitate_titei"))
    imp = _suma(manual.get("impozit_datorat"))
    return {
        "cantitate_titei": q,
        "impozit_datorat": imp,
        "totalPlata_A": q + imp,
    }


def pull(conn, schema, perioada):
    """Identitatea platitorului nu se trage din registru pentru D130; vine din `manual`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not (2 <= len(_cif(manual.get("cui"))) <= 10):
        er.append("Cod de identificare fiscala (cui) invalid — astept 2..10 cifre.")
    if not str(manual.get("denumire") or "").strip():
        er.append("Lipsa denumire platitor (denumire).")
    for k, et in (("nume_declar", "nume"), ("prenume_declar", "prenume"),
                  ("functie_declar", "functia/calitatea")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsa %s declarant (%s) — obligatoriu." % (et, k))
    if manual.get("cantitate_titei") in (None, ""):
        er.append("Lipsa cantitate titei livrata (cantitate_titei).")
    if manual.get("impozit_datorat") in (None, ""):
        er.append("Lipsa impozit datorat (impozit_datorat).")
    if _suma(manual.get("impozit_datorat")) < 0 or _suma(manual.get("cantitate_titei")) < 0:
        er.append("cantitate_titei si impozit_datorat trebuie sa fie >= 0.")
    return er


def build_xml(prof, an, luna, manual):
    c = calcul_d130(manual)
    d_rec = _cif(manual.get("d_rec")) or "0"
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%s"' % d_rec)
    a.append('nume_declar="%s"' % _esc(manual.get("nume_declar"), 75))
    a.append('prenume_declar="%s"' % _esc(manual.get("prenume_declar"), 75))
    a.append('functie_declar="%s"' % _esc(manual.get("functie_declar"), 75))
    a.append('cui="%s"' % _cif(manual.get("cui")))
    a.append('denumire="%s"' % _esc(manual.get("denumire"), 200))
    if manual.get("adresa"):
        a.append('adresa="%s"' % _esc(manual.get("adresa"), 200))
    if manual.get("telefon"):
        a.append('telefon="%s"' % _esc(manual.get("telefon"), 15))
    if manual.get("fax"):
        a.append('fax="%s"' % _esc(manual.get("fax"), 15))
    if manual.get("email"):
        a.append('email="%s"' % _esc(manual.get("email"), 250))
    a.append('totalPlata_A="%d"' % c["totalPlata_A"])
    a.append('cantitate_titei="%d"' % c["cantitate_titei"])
    a.append('impozit_datorat="%d"' % c["impozit_datorat"])
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie130 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D130 nu se poate genera: " + " ".join(er))
    c = calcul_d130(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat130(an=an, luna=luna, cantitate_titei=c["cantitate_titei"],
                      impozit_datorat=c["impozit_datorat"], total_plata_a=c["totalPlata_A"])
    return xml, res
