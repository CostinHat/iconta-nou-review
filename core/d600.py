"""core/d600.py - D600: Declaratie privind venitul asupra caruia se datoreaza contributia de
asigurari sociale (CAS) si baza de calcul a contributiei de asigurari sociale de sanatate (CASS)
- estimare, persoane fizice.

Declaratie MANUALA (persoana fizica). Se depune ESTIMAT pentru anul curent (venit estimat pe
categoriile care genereaza CAS/CASS). Aplicatia nu are registru de persoane fizice; identitatea
contribuabilului, categoriile si valorile/bifele vin din `manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator). Actul NU e in corpus, deci
NU se hardcodeaza plafoane CAS/CASS (nr. de salarii minime, cote 25%/10%): sumele si optiunile
vin integral din `manual`. Structura schemei in vigoare (namespace declaratie:v2, pachet
d600validator/v2) a fost CITITA din bytecode-ul D600Validator.jar (Identificare v2) si PROBATA
atribut cu atribut pe validator (DUKIntegrator -v D600), fisier VALID ("ok"):

  Antet:        luna (FIX 12 - R10 "Declaratia este anuala"; luna!=12 => respins), an, d_rec.
  Contribuabil (blocul _c, OBLIGATORIU in XSD): nume_c, initiala_c, prenume_c, cif_c (CNP).
                Optional: adresa_c, fax_c, mail_c, telefon_c, banca_c, cont_c (IBAN).
  Imputernicit (blocul _i): den_i, cif_i, adresa_i ... - NEPOPULAT deliberat (vezi mai jos).
  CAS (sect. II):  cas1..cas4, cas_opt (bifa; selecteaza sectiunea si CERE baze1..12 - DUK regula V2),
                   cas_stop, data_stop_cas, baza1..baza12 (baze lunare - fiecare >= salariul minim).
  CASS (sect. III): cass1..cass6, cass_incepere, cass_opt, cass_stop, data_stop_cass,
                    cass_atas1, cass_atas_alte, atas1, atas2.
  Suma de control: totalPlata_A (DUK regula R41/R42, vezi calcul_d600); trebuie sa fie > 0.

Reguli citite si probate pe validator:
  - R10: luna trebuie sa fie 12 (declaratie anuala); orice alta valoare e respinsa de XSD.
  - blocul _c e obligatoriu: nume_c/initiala_c/prenume_c/cif_c "trebuie sa existe" (XSD required).
  - V12: campurile imputernicitului (blocul _i) sunt simultan nule sau simultan nenule.
  - R41: totalPlata_A = cas1+cas2+cas3+cas4+cas_opt+cas_stop + cass1+cass2+cass3+cass4+cass5+cass6
         + cass_incepere + cass_opt + cass_stop.  R42: totalPlata_A > 0.
  - cass1..cass6 / cass_opt / cass_incepere - cel mult UNA dintre cele trei cai poate fi > 0.
  - "baza nu poate fi mai mica decat salariul minim garantat" - fiecare baza lunara are prag legal.
  - campurile de suma (cas1..cas4, cas_stop) NU accepta 0 (interval > 0); un atribut prezent dar
    vid e respins, iar o data goala arunca parserul => se EMIT DOAR campurile cu valoare pozitiva /
    nevida (0 sau "" => atributul se omite).

NEPOPULAT deliberat:
  - categ, optiune, cod_postal_c, cod_postal_i: prezente in Identificare (mostenire v0/v1) dar
    RESPINSE ca "atribut necunoscut" de XSD v2 => nu se emit (selectarea sectiunii CAS e implicita
    prin cas_opt / prezenta bazelor, nu prin optiune).
  - blocul imputernicit (_i): cod_postal_i e respins ca necunoscut, deci V12 (toate _i nenule) nu
    poate fi satisfacut cu cod postal => imputernicitul nu e suportat (se lasa complet gol, V12 OK).
    Se adauga la nevoie daca ANAF publica o schema cu cod_postal_i valid.
  - plafoane/cote CAS-CASS: actul nu e in corpus; sumele (cas*, cass*, baze) vin din `manual`.

Contract dXXX: pull/erori_generare/calcul_d600/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d600:declaratie:v2"
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

# R41: componentele sumei de control totalPlata_A (in ordinea din validator).
_SUM_KEYS = ["cas1", "cas2", "cas3", "cas4", "cas_opt", "cas_stop",
             "cass1", "cass2", "cass3", "cass4", "cass5", "cass6",
             "cass_incepere", "cass_opt", "cass_stop"]

# Campuri numerice optionale (se emit doar daca int > 0 - intervalele resping 0).
_NUM_OPT = ["cas1", "cas2", "cas3", "cas4", "cas_opt", "cas_stop",
            "baza1", "baza2", "baza3", "baza4", "baza5", "baza6",
            "baza7", "baza8", "baza9", "baza10", "baza11", "baza12",
            "cass1", "cass2", "cass3", "cass4", "cass5", "cass6",
            "cass_incepere", "cass_opt", "cass_stop", "cass_atas1", "atas1", "atas2"]

# Campuri text/data optionale (se emit doar daca nevide - atribut vid e respins de validator).
_STR_OPT = [("adresa_c", 200), ("fax_c", 15), ("mail_c", 250), ("telefon_c", 15),
            ("banca_c", 100), ("cont_c", 24), ("data_stop_cas", 10), ("data_stop_cass", 10),
            ("cass_atas_alte", 250)]


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cnp_valid(cnp):
    cnp = _cif(cnp)
    if len(cnp) != 13:
        return False
    s = sum(int(cnp[i]) * _CNP_W[i] for i in range(12))
    c = s % 11
    c = 1 if c == 10 else c
    return c == int(cnp[12])


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _int(x):
    s = _cif(x)
    return int(s) if s else 0


@dataclass
class Rezultat600:
    an: int
    luna: int
    total_plata_a: int = 0
    contribuabil: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d600(manual):
    """Suma de control R41: totalPlata_A = suma componentelor CAS + CASS. R42 cere > 0."""
    return {"totalPlata_A": sum(_int(manual.get(k)) for k in _SUM_KEYS)}


def pull(conn, schema, perioada):
    """D600 e MANUALA pe persoana fizica; firma nu are registru de persoane. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsa nume contribuabil (nume_c).")
    if not str(manual.get("initiala_c") or "").strip():
        er.append("Lipsa initiala tata (initiala_c).")
    if not str(manual.get("prenume_c") or "").strip():
        er.append("Lipsa prenume contribuabil (prenume_c).")
    if not _cnp_valid(manual.get("cif_c")):
        er.append("CNP contribuabil (cif_c) invalid (13 cifre + cifra de control).")
    if not str(manual.get("adresa_c") or "").strip():
        er.append("Lipsa adresa contribuabil (adresa_c).")
    cont = str(manual.get("cont_c") or "").replace(" ", "").upper()
    if cont and not _IBAN_OK.match(cont):
        er.append("IBAN contribuabil (cont_c) invalid - astept RO + 22 caractere.")
    # R42: suma de control trebuie sa fie > 0 (cel putin o componenta CAS/CASS).
    if calcul_d600(manual)["totalPlata_A"] <= 0:
        er.append("Nicio componenta CAS/CASS > 0 (totalPlata_A trebuie sa fie > 0) - DUK regula R42.")
    # Exclusivitate CASS (probata pe validator): cass1..6 / cass_opt / cass_incepere - cel mult una.
    cass_baze = sum(_int(manual.get("cass%d" % i)) for i in range(1, 7))
    cai = sum(1 for v in (cass_baze, _int(manual.get("cass_opt")),
                          _int(manual.get("cass_incepere"))) if v > 0)
    if cai > 1:
        er.append("CASS: cass1..cass6, cass_opt si cass_incepere nu pot fi simultan > 0.")
    return er


def build_xml(prof, an, luna, manual):
    total = calcul_d600(manual)["totalPlata_A"]
    a = []
    a.append('luna="12"')                       # R10: declaratie anuala, luna FIX 12
    a.append('an="%d"' % int(an))
    a.append('d_rec="%s"' % (_cif(manual.get("d_rec")) or "0"))
    # Contribuabil (blocul _c, obligatoriu)
    a.append('nume_c="%s"' % _esc(manual.get("nume_c"), 75))
    a.append('initiala_c="%s"' % _esc(manual.get("initiala_c"), 1))
    a.append('prenume_c="%s"' % _esc(manual.get("prenume_c"), 75))
    a.append('cif_c="%s"' % _cif(manual.get("cif_c")))
    # Campuri text/data optionale - doar daca nevide (atribut vid e respins)
    for k, lim in _STR_OPT:
        v = manual.get(k)
        if k == "cont_c":
            v = str(v or "").replace(" ", "").upper()
        vv = _esc(v, lim)
        if vv:
            a.append('%s="%s"' % (k, vv))
    # Campuri numerice optionale - doar daca > 0 (intervalele resping 0)
    for k in _NUM_OPT:
        n = _int(manual.get(k))
        if n > 0:
            a.append('%s="%d"' % (k, n))
    a.append('totalPlata_A="%d"' % total)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie600 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D600 nu se poate genera: " + " ".join(er))
    total = calcul_d600(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    nume = ("%s %s %s" % (manual.get("nume_c") or "", manual.get("initiala_c") or "",
                          manual.get("prenume_c") or "")).strip()
    res = Rezultat600(an=an, luna=12, total_plata_a=total, contribuabil=nume)
    return xml, res
