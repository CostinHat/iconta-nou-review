# -*- coding: utf-8 -*-
"""core/d119.py - D119: Declaratie speciala privind obligatiile de plata la bugetul
general consolidat ale BNR din veniturile nete realizate.

SCOP REAL (confirmat, NU presupus): declaratie SPECIALA depusa de BANCA NATIONALA A
ROMANIEI (BNR) pentru obligatiile de plata la bugetul general consolidat rezultate din
veniturile nete realizate. Confirmat din pagina oficiala ANAF (static.anaf.ro/.../119.html,
07.02.2019) SI din structura validatorului (un singur cont bancar `banca`+`Cont`, o singura
obligatie cu Suma_dat/ded/plata/rest). NU exista D119Pdf.jar in pachetul DUK - scopul a fost
adus din pagina ANAF + arbitrat de validator.

DECLARATIE MANUALA: aplicatia nu tine contabilitatea BNR; toate valorile (identificare BNR,
cont trezorerie, sume) vin din `manual`. `pull` intoarce {} (contractul cere pull; conn poate
fi None). Modelata dupa sablonul manual d230, cu aritmetica obligatiei ca la d100.

STRUCTURA + REGULI = CITITE DIN VALIDATORUL OFICIAL (D119Validator.jar, pachet d119validator/v0)
si PROBATE camp cu camp pe DUKIntegrator (-v D119 -> "ok"). Structura in vigoare:
  Radacina (element UNIC, PLAT - NU are element-copil, dovedit pe validator): <D119>
  Namespace: mfp:anaf:dgti:d119:declaratie:v1 (confirmat din constant pool + probat).
  Atribute (case EXACT din bytecode `_<nume>_ok`): an, luna, d_rec, cif, den, adresaS,
  banca, Cont, nume, prenume, functie, nr_evid, scadenta, Suma_dat, Suma_ded, Suma_plata,
  Suma_rest, totalPlata_A. OBLIGATORII (dovedit "atributul trebuie sa existe"): d_rec, banca,
  Cont (+ identificarea si sumele). Optionale (in constant pool, neconfirmate obligatorii,
  nepopulate deliberat): telefon, fax, email, numeDeclar, prenumeDeclar, functieDeclar,
  tipPerioada.
Reguli extrase (mesaje validator, coduri REALE la rulare) - prefix "DUK regula <cod>":
  DUK regula R15: cand Suma_dat >= Suma_ded -> Suma_plata = Suma_dat - Suma_ded si Suma_rest = 0.
    ANOMALIE PROBATA (nu presupusa): mesajul R15 spune "daca Suma_dat <= Suma_ded atunci Suma_rest
    = Suma_ded - Suma_dat", DAR validatorul NU accepta NICIO combinatie cand Suma_dat < Suma_ded
    (R15 se declanseaza pt. orice rest/plata; iar Suma_rest negativ e "in afara intervalului").
    Practic Suma_dat >= Suma_ded e OBLIGATORIU. Generatorul RESPINGE Suma_ded > Suma_dat cu eroare
    clara (nu emite XML mereu respins de validator) - vezi calcul_d119.
  DUK regula R20: totalPlata_A = Suma_dat + Suma_ded + Suma_plata + Suma_rest.
  DUK regula R17: nr_evid - lungime 23; cifra de control (poz.22-23) = suma primelor 21 cifre % 100;
    pozitii fixe 1-7 = "1010101" si 18-21 = "0000"; poz.8-11 = LLAA (perioada raportare = luna+an);
    poz.12-17 = ZZLLAA (scadenta). Toate probate camp cu camp pe DUKIntegrator.
  DUK regula scadenta: "Scadenta trebuie sa fie 25 a lunii urmatoare" perioadei de raportare.
"""
from __future__ import annotations

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație specială privind obligațiile de plată la bugetul de stat'

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from xml.sax.saxutils import quoteattr
import re

from core.identitate import valideaza_cui  # sursa CANONICA checksum CUI (import READ-ONLY, LEAF)

NS = "mfp:anaf:dgti:d119:declaratie:v1"

_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
_NEDIGIT = re.compile(r"\D")

# nr_evid: pozitii fixe probate pe validator (mesaj "pozitii fixe (1-7, 18-21) eronate";
# constanta "10101010000" = "1010101" + "0000"). BNR = o singura obligatie -> prefix fix.
_NRE_PREFIX = "1010101"   # poz.1-7
_NRE_MIJLOC_FIX = "0000"  # poz.18-21


def _i(x):
    """Intreg lei, rotunjire HALF-UP prin Decimal.quantize (nu bancara)."""
    return int(Decimal(str(x if x not in (None, "") else 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(v, lim=None):
    s = "" if v is None else " ".join(str(v).split())
    if lim:
        s = s[:lim]
    return quoteattr(s)


def _scadenta_std(an, luna):
    """(zi, luna, an) scadentei: 25 a lunii urmatoare perioadei de raportare (DUK regula scadenta)."""
    lu = luna + 1
    a = an
    if lu > 12:
        lu = 1
        a += 1
    return 25, lu, a


def _nr_evid(luna, an, zi_s, luna_s, an_s):
    """23 caractere. Layout probat pe validator (DUK regula nr_evid):
      poz.1-7  : "1010101" (fix)
      poz.8-11 : LLAA - luna+an (2 cifre) ale perioadei de raportare
      poz.12-17: ZZLLAA - data scadentei
      poz.18-21: "0000" (fix)
      poz.22-23: cifra de control = suma primelor 21 cifre % 100 (DUK regula R17.4)
    """
    p1_21 = (_NRE_PREFIX +
             "%02d%02d" % (luna, an % 100) +
             "%02d%02d%02d" % (zi_s, luna_s, an_s % 100) +
             _NRE_MIJLOC_FIX)
    assert len(p1_21) == 21, "nr_evid: %d pozitii, asteptam 21" % len(p1_21)
    control = "%02d" % (sum(int(c) for c in p1_21) % 100)
    return p1_21 + control


@dataclass
class RezultatD119:
    an: int
    luna: int
    suma_dat: int = 0
    suma_ded: int = 0
    suma_plata: int = 0
    suma_rest: int = 0
    total_plata_a: int = 0
    scadenta: str = ""
    nr_evid: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d119(an, luna, manual):
    """Aritmetica obligatiei (DUK regula R15/R20). Suma_dat/Suma_ded din `manual` (lei intregi).
    Suma_dat >= Suma_ded OBLIGATORIU (anomalia R15 probata: dat < ded e mereu respins, Suma_rest
    negativ e in afara intervalului) -> respingem inainte de a emite XML respins de validator.
    Scadenta implicita = 25 a lunii urmatoare; override manual in format ZZ.LL.AAAA (nr_evid
    e derivat din ACEEASI data - poz.12-17, altfel R17 nr_evid respinge)."""
    suma_dat = _i(manual.get("suma_dat"))
    suma_ded = _i(manual.get("suma_ded"))
    if suma_ded > suma_dat:
        raise ValueError(
            "D119: Suma_ded (%d) > Suma_dat (%d). Validatorul oficial (DUK regula R15) NU accepta "
            "Suma_dat < Suma_ded (Suma_rest trebuie >= 0, nicio combinatie nu trece). Declarația "
            "se depune doar cand suma datorată >= suma dedusa." % (suma_ded, suma_dat))
    suma_plata = suma_dat - suma_ded
    suma_rest = 0
    total = suma_dat + suma_ded + suma_plata + suma_rest

    zi_s, luna_s, an_s = _scadenta_std(an, luna)
    scad_manual = str(manual.get("scadenta") or "").strip()
    if scad_manual:
        p = scad_manual.split(".")
        if (len(p) != 3 or not all(x.isdigit() for x in p)
                or len(p[0]) != 2 or len(p[1]) != 2 or len(p[2]) != 4):
            raise ValueError("D119: scadență manuală %r nu e în formatul ZZ.LL.AAAA." % scad_manual)
        zi_s, luna_s, an_s = int(p[0]), int(p[1]), int(p[2])
    scad_str = "%02d.%02d.%04d" % (zi_s, luna_s, an_s)

    return RezultatD119(
        an=an, luna=luna, suma_dat=suma_dat, suma_ded=suma_ded,
        suma_plata=suma_plata, suma_rest=suma_rest, total_plata_a=total,
        scadenta=scad_str, nr_evid=_nr_evid(luna, an, zi_s, luna_s, an_s))


def pull(conn, schema, perioada):
    """D119 e MANUALA (aplicatia nu tine contabilitatea BNR). Contractul cere `pull`;
    conn poate fi None. Nu se citeste nimic din baza."""
    return {}


def erori_generare(prof, manual):
    er = []
    cui = _cif(manual.get("cif"))
    if not cui:
        er.append("Lipsă cod de identificare fiscala (cif) al BNR.")
    else:
        ok, motiv = valideaza_cui(cui)
        if not ok:
            er.append("D119: cif invalid (%s: %s)." % (cui, motiv))
    if not str(manual.get("den") or "").strip():
        er.append("Lipsă denumire (den).")
    if not str(manual.get("adresaS") or "").strip():
        er.append("Lipsă adresa sediu (adresaS).")
    if not str(manual.get("banca") or "").strip():
        er.append("Lipsă banca (banca) - atribut obligatoriu.")
    iban = str(manual.get("Cont") or "").replace(" ", "").upper()
    if not _IBAN_OK.match(iban):
        er.append("Cont (IBAN) invalid - aștept RO + 22 caractere.")
    for k, et in (("nume", "nume reprezentant"), ("prenume", "prenume reprezentant"),
                  ("functie", "funcție reprezentant")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsă %s (%s)." % (et, k))
    if _i(manual.get("suma_dat")) < 0 or _i(manual.get("suma_ded")) < 0:
        er.append("Sumele (suma_dat/suma_ded) nu pot fi negative.")
    try:
        drec = int(manual.get("d_rec", 0))
    except (TypeError, ValueError):
        drec = -1
    if drec not in (0, 1):
        er.append("d_rec obligatoriu 0 (initiala) sau 1 (rectificativa).")
    return er


def build_xml(prof, res, manual):
    iban = str(manual.get("Cont") or "").replace(" ", "").upper()
    try:
        drec = int(manual.get("d_rec", 0))
    except (TypeError, ValueError):
        drec = 0
    a = []
    a.append('an="%d"' % int(res.an))
    a.append('luna="%d"' % int(res.luna))
    a.append('d_rec="%d"' % drec)
    a.append('cif="%s"' % _cif(manual.get("cif")))
    a.append('den=%s' % _esc(manual.get("den"), 200))
    a.append('adresaS=%s' % _esc(manual.get("adresaS"), 200))
    a.append('banca=%s' % _esc(manual.get("banca"), 100))
    a.append('Cont=%s' % _esc(iban, 24))
    a.append('nume=%s' % _esc(manual.get("nume"), 75))
    a.append('prenume=%s' % _esc(manual.get("prenume"), 75))
    a.append('functie=%s' % _esc(manual.get("functie"), 75))
    if str(manual.get("telefon") or "").strip():
        a.append('telefon=%s' % _esc(manual.get("telefon"), 15))
    if str(manual.get("email") or "").strip():
        a.append('email=%s' % _esc(manual.get("email"), 60))
    a.append('nr_evid="%s"' % res.nr_evid)
    a.append('scadenta="%s"' % res.scadenta)
    a.append('Suma_dat="%d"' % res.suma_dat)
    a.append('Suma_ded="%d"' % res.suma_ded)
    a.append('Suma_plata="%d"' % res.suma_plata)
    a.append('Suma_rest="%d"' % res.suma_rest)
    a.append('totalPlata_A="%d"' % res.total_plata_a)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D119 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    """D119 MANUALA lunara (contract uniform: pull/erori_generare/calcul/build/genereaza).
    perioada.luna obligatoriu. `manual`: cif, den, adresaS, banca, Cont, nume, prenume, functie,
    suma_dat, suma_ded(optional), d_rec(optional 0/1), scadenta(optional override ZZ.LL.AAAA)."""
    manual = dict(manual or {})
    an = int(perioada.an)
    if perioada.luna is None:
        raise ValueError("D119 lunara: perioada.luna obligatoriu.")
    luna = int(perioada.luna)
    if not (1 <= luna <= 12):
        raise ValueError("D119: lună invalidă: %r." % luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D119 nu se poate genera: " + " ".join(er))
    res = calcul_d119(an, luna, manual)
    xml = build_xml(prof, res, manual)
    return xml, res
