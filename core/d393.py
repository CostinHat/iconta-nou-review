"""core/d393.py -- D393: Declaratie informativa privind biletele de calatorie pentru
transportul rutier international de persoane.

Declaratie ANUALA depusa de operatorii de transport rutier international de persoane care
detin licenta de traseu / autorizatie, informand ANAF asupra veniturilor din biletele de
calatorie emise. Aplicatia nu are registrul biletelor emise; cifrele vin din `manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator). Namespace declaratie:v1,
pachet d393validator/v0. Campurile au fost CITITE din bytecode-ul D393Validator.jar (clasele
Identificare / DataObjectRoot / DbAccessImpl / ValidatorImpl) si PROBATE camp cu camp pe validator.
Radacina `d393`, structura PLATA (toate campurile sunt atribute pe radacina, fara sectiuni copil).

Atribute radacina confirmate pe validator:
  an, luna, d_rec                          -- perioada de raportare + rectificativa (numerice, obligatorii)
  cif                                       -- CUI operator (declarant); validatorul verifica cifra de control CUI
  nume1, adresa1                            -- identificare operator (obligatorii)
  telefon1, fax1, email1                    -- contact operator (optionale)
  nume_declarant, prenume_declarant, functia_declarant  -- semnatarul (OBLIGATORII, probat pe validator)
  serie_licenta, numar_licenta              -- licenta de traseu / autorizatie (optionale)
  totalPlata_A                              -- suma de control
  Venituri_bilete                           -- venituri din bilete (suma de control totalPlata_A = Venituri_bilete)
  cif2, nume2, adresa2, telefon2, fax2, email2  -- reprezentant fiscal (grup OPTIONAL, all-or-nothing pe cif2/nume2/adresa2)

Reguli citite din validator (probate):
  R_reprezentant: daca unul din cif2/nume2/adresa2 este <> null, toate cif2/nume2/adresa2 devin obligatorii.
  R_suma_control: totalPlata_A = Venituri_bilete (suma de control).

Contract dXXX: pull/erori_generare/calcul_d393/build_xml/genereaza(conn, schema, perioada, manual).
NEPOPULAT deliberat (optionale, semantica nedeterminata fara actul OPANAF in corpus): telefon1/fax1/email1,
serie_licenta/numar_licenta si intreg grupul reprezentantului fiscal (cif2/nume2/adresa2/telefon2/fax2/email2)
-- se completeaza din `manual` la nevoie, pe aceeasi metoda.
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație informativă privind biletele de călătorie pentru transportul rutier de persoane'
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d393:declaratie:v1"
_NEDIGIT = re.compile(r"\D")

# campuri declarant obligatorii (probate pe validator: "atributul trebuie sa existe")
_DECLARANT = (("nume_declarant", "nume declarant"),
              ("prenume_declarant", "prenume declarant"),
              ("functia_declarant", "funcția declarant"))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat393:
    an: int
    luna: int
    total_plata_a: int = 0
    venituri_bilete: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d393(manual):
    """Suma de control (R_suma_control): totalPlata_A = Venituri_bilete = suma veniturilor din input.

    `venituri_bilete` poate fi o valoare unica sau o lista de valori (se insumeaza)."""
    v = manual.get("venituri_bilete")
    if isinstance(v, (list, tuple)):
        total = sum(int(_cif(x) or 0) for x in v)
    else:
        total = int(_cif(v) or 0)
    return {"totalPlata_A": total, "Venituri_bilete": total}


def pull(conn, schema, perioada):
    """D393 e informativa manuala; aplicatia nu are registrul biletelor emise. Contractul cere `pull`."""
    return {}


def _are_reprezentant(manual):
    return any(str(manual.get(k) or "").strip() for k in ("cif2", "nume2", "adresa2"))


def erori_generare(prof, manual):
    er = []
    if not (2 <= len(_cif(manual.get("cif"))) <= 10):
        er.append("CUI operator (cif) invalid.")
    if not str(manual.get("nume1") or "").strip():
        er.append("Lipsă denumire operator (nume1).")
    if not str(manual.get("adresa1") or "").strip():
        er.append("Lipsă adresa operator (adresa1).")
    for k, et in _DECLARANT:
        if not str(manual.get(k) or "").strip():
            er.append("Lipsă %s (%s)." % (et, k))
    if calcul_d393(manual)["Venituri_bilete"] <= 0:
        er.append("Lipsă venituri din bilete (venituri_bilete) > 0.")
    # R_reprezentant: grup all-or-nothing pe cif2/nume2/adresa2
    if _are_reprezentant(manual):
        if not (2 <= len(_cif(manual.get("cif2"))) <= 10):
            er.append("Reprezentant fiscal declarat: cif2 obligatoriu și valid.")
        if not str(manual.get("nume2") or "").strip():
            er.append("Reprezentant fiscal declarat: nume2 obligatoriu.")
        if not str(manual.get("adresa2") or "").strip():
            er.append("Reprezentant fiscal declarat: adresa2 obligatoriu.")
    return er


def build_xml(prof, an, luna, manual):
    c = calcul_d393(manual)
    d_rec = _cif(manual.get("d_rec")) or "0"
    a = []
    a.append('an="%d"' % int(an))
    a.append('luna="%d"' % int(luna))
    a.append('d_rec="%s"' % d_rec)
    a.append('cif="%s"' % _cif(manual.get("cif")))
    a.append('nume1="%s"' % _esc(manual.get("nume1"), 200))
    a.append('adresa1="%s"' % _esc(manual.get("adresa1"), 200))
    if manual.get("telefon1"):
        a.append('telefon1="%s"' % _esc(manual.get("telefon1"), 15))
    if manual.get("fax1"):
        a.append('fax1="%s"' % _esc(manual.get("fax1"), 15))
    if manual.get("email1"):
        a.append('email1="%s"' % _esc(manual.get("email1"), 250))
    a.append('nume_declarant="%s"' % _esc(manual.get("nume_declarant"), 75))
    a.append('prenume_declarant="%s"' % _esc(manual.get("prenume_declarant"), 75))
    a.append('functia_declarant="%s"' % _esc(manual.get("functia_declarant"), 75))
    if manual.get("serie_licenta"):
        a.append('serie_licenta="%s"' % _esc(manual.get("serie_licenta"), 50))
    if manual.get("numar_licenta"):
        a.append('numar_licenta="%s"' % _esc(manual.get("numar_licenta"), 50))
    a.append('totalPlata_A="%d"' % c["totalPlata_A"])
    a.append('Venituri_bilete="%d"' % c["Venituri_bilete"])
    # reprezentant fiscal (grup optional)
    if _are_reprezentant(manual):
        a.append('cif2="%s"' % _cif(manual.get("cif2")))
        a.append('nume2="%s"' % _esc(manual.get("nume2"), 200))
        a.append('adresa2="%s"' % _esc(manual.get("adresa2"), 200))
        if manual.get("telefon2"):
            a.append('telefon2="%s"' % _esc(manual.get("telefon2"), 15))
        if manual.get("fax2"):
            a.append('fax2="%s"' % _esc(manual.get("fax2"), 15))
        if manual.get("email2"):
            a.append('email2="%s"' % _esc(manual.get("email2"), 250))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<d393 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D393 nu se poate genera: " + " ".join(er))
    c = calcul_d393(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat393(an=an, luna=luna, total_plata_a=c["totalPlata_A"],
                      venituri_bilete=c["Venituri_bilete"])
    return xml, res
