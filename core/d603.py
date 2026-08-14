"""core/d603.py — D603: Declaratie pe propria raspundere pentru exceptarea de la plata
contributiei de asigurari sociale de sanatate (CASS).

Declaratie MANUALA (persoana fizica). Contribuabilul declara ca, pentru o perioada, este exceptat de
la plata CASS in Romania deoarece este asigurat intr-un alt stat (regula validatorului: statAsigurare
trebuie sa fie DIFERIT de RO). Aplicatia nu are registru de persoane fizice — toate valorile vin din
`manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D603Validator.jar, arbitrul peste anexe). Structura
(namespace declaratie:v1, pachet d603validator/v0) a fost CITITA din bytecode-ul jar-ului si PROBATA
camp cu camp pe DUKIntegrator (rezultat: "Validare fara erori"). Constatari cheie confirmate pe
validator, care contrazic sabloanele uzuale:
  - RADACINA XML = `d603` (DECLARATION_name='d603'); NU `declaratie` (respins: "sectiune necunoscuta").
  - STRUCTURA E PLATA: toate campurile sunt ATRIBUTE pe <d603>; NU exista element copil `exceptare`
    (respins ca sectiune). `exceptare` este un ATRIBUT = codul categoriei de exceptare, in {2,3,4}
    (lista interna _listaExceptare a validatorului).
  - `luna` obligatoriu = "12" (declaratie anuala; alte valori respinse "in afara intervalului").
  - `d_rec` NU e permis (respins: "atribut necunoscut"); NU se emite.
  - Datele calendaristice in format `dd.MM.yyyy` (yyyy-MM-dd respins: "data calendaristica eronata").
Reguli probate:
  - R20: totalPlata_A = suma cifrelor din cif (suma de control, NU un cuantum de plata CASS).
  - R21: daca taraContrib = RO atunci judetContrib obligatoriu.
  - R22/R23/R24/R33: daca imputernicit = 1 atunci cifImputernicit/nrImputernicit/numeImputernicit/
    dataImputernicit/judetImputernicit obligatorii.
  - R36: statAsigurare diferit de RO; dataInceput < dataSfarsit.
  - ibanContrib (daca prezent): exact 24 caractere, majuscule, incepe cu 'RO'.

NU se fabrica valori/plafoane CASS — declaratia nu contine cuantumuri de contributie, doar perioada de
exceptare, statul de asigurare si categoria. Obligatorii (probate pe validator): an, luna=12,
totalPlata_A, cif, numeContrib, taraContrib, imputernicit, exceptare, statAsigurare, dataInceput,
dataSfarsit, dataExceptare, documente; judetContrib obligatoriu doar cand taraContrib=RO (R21).
NEPOPULAT deliberat (optional, nu se ghiceste): adresa contribuabilului (localitate/strada/mentiuni),
contactul (telefon/fax/email/iban/banca/act), blocul imputernicit.
NEDETERMINAT din validator (numeric {2,3,4}, fara text): semantica exacta a fiecarui cod `exceptare` —
se ia din act / de la apelant, nu se presupune.

Contract dXXX: NS, _cif/_cnp_valid/_esc, calcul_d603, pull, erori_generare, build_xml,
genereaza(conn, schema, perioada, manual=None).
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d603:declaratie:v1"
COD_EXCEPTARE = (2, 3, 4)  # _listaExceptare din validator (coduri categorie exceptare CASS)
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO[A-Z0-9]{22}$")
_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_RO = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


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


def _suma_cifre(cif):
    return sum(int(c) for c in _cif(cif))


def _data(v):
    """Normalizeaza o data la formatul cerut de validator: dd.MM.yyyy. Accepta si yyyy-MM-dd.
    Intoarce ("dd.MM.yyyy", (yyyy,mm,dd)) sau (None, None) daca invalida."""
    s = str(v or "").strip()
    m = _RO.match(s)
    if m:
        d, mo, y = m.group(1), m.group(2), m.group(3)
    else:
        m = _ISO.match(s)
        if not m:
            return None, None
        y, mo, d = m.group(1), m.group(2), m.group(3)
    try:
        yi, mi, di = int(y), int(mo), int(d)
        import datetime
        datetime.date(yi, mi, di)
    except ValueError:
        return None, None
    return "%02d.%02d.%04d" % (di, mi, yi), (yi, mi, di)


@dataclass
class Rezultat603:
    an: int
    luna: int
    total_plata_a: int = 0
    stat_asigurare: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d603(manual):
    """Suma de control (R20): totalPlata_A = suma cifrelor din CIF/CNP. Nu e cuantum de plata."""
    return {"totalPlata_A": _suma_cifre(manual.get("cif"))}


def pull(conn, schema, perioada):
    """D603 e MANUALA pe persoana fizica; firma nu are registru de persoane. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("numeContrib") or "").strip():
        er.append("Lipsa nume contribuabil (numeContrib).")
    if not _cnp_valid(manual.get("cif")):
        er.append("CNP contribuabil (cif) invalid (13 cifre + cifra de control).")
    tara = str(manual.get("taraContrib") or "RO").strip().upper()
    if tara == "RO" and not str(manual.get("judetContrib") or "").strip():
        er.append("Daca taraContrib=RO atunci judetContrib obligatoriu (DUK regula R21).")
    iban = str(manual.get("ibanContrib") or "").replace(" ", "").upper()
    if iban and not _IBAN_OK.match(iban):
        er.append("ibanContrib invalid - astept RO + 22 caractere majuscule (24 total).")
    try:
        cod = int(manual.get("exceptare"))
    except (TypeError, ValueError):
        cod = None
    if cod not in COD_EXCEPTARE:
        er.append("Cod exceptare (exceptare) obligatoriu, unul din %s." % (COD_EXCEPTARE,))
    st = str(manual.get("statAsigurare") or "").strip().upper()
    if not st:
        er.append("statAsigurare obligatoriu (stat de asigurare, cod tara).")
    elif st == "RO":
        er.append("statAsigurare trebuie sa fie diferit de RO (DUK regula R36).")
    di, tdi = _data(manual.get("dataInceput"))
    ds, tds = _data(manual.get("dataSfarsit"))
    if not di:
        er.append("dataInceput lipsa/invalida (astept YYYY-MM-DD sau dd.MM.yyyy).")
    if not ds:
        er.append("dataSfarsit lipsa/invalida (astept YYYY-MM-DD sau dd.MM.yyyy).")
    if tdi and tds and tdi >= tds:
        er.append("dataInceput trebuie sa fie mai mica decat dataSfarsit (DUK regula R36).")
    if not _data(manual.get("dataExceptare"))[0]:
        er.append("dataExceptare obligatorie/invalida (astept YYYY-MM-DD sau dd.MM.yyyy).")
    if not str(manual.get("documente") or "").strip():
        er.append("documente obligatoriu (documentele justificative ale exceptarii).")
    if int(manual.get("imputernicit") or 0) == 1:
        if not _data(manual.get("dataImputernicit"))[0]:
            er.append("imputernicit=1 => dataImputernicit obligatoriu/valid.")
        for k, et in (("cifImputernicit", "cif"), ("numeImputernicit", "nume"),
                      ("nrImputernicit", "nr"), ("judetImputernicit", "judet")):
            if not str(manual.get(k) or "").strip():
                er.append("imputernicit=1 => %sImputernicit obligatoriu." % et)
    return er


def _attr(name, val, lim=None):
    return ' %s="%s"' % (name, _esc(val, lim))


def build_xml(prof, an, luna, manual):
    total = calcul_d603(manual)["totalPlata_A"]
    imp = int(manual.get("imputernicit") or 0)
    tara = str(manual.get("taraContrib") or "RO").strip().upper()
    a = []
    a.append(_attr("an", int(an)))
    a.append(_attr("luna", 12))  # declaratie anuala; validatorul cere luna=12
    a.append(_attr("totalPlata_A", total))
    a.append(_attr("cif", _cif(manual.get("cif"))))
    a.append(_attr("numeContrib", manual.get("numeContrib"), 75))
    a.append(_attr("taraContrib", tara, 2))
    if manual.get("judetContrib"):
        a.append(_attr("judetContrib", manual.get("judetContrib"), 2))
    for name, lim in (("localitateContrib", 200), ("stradaContrib", 200),
                      ("mentiuniAdresaContrib", 200), ("telefonContrib", 15),
                      ("faxContrib", 15), ("emailContrib", 250), ("bancaContrib", 200),
                      ("actContrib", 200)):
        if manual.get(name):
            a.append(_attr(name, manual.get(name), lim))
    iban = str(manual.get("ibanContrib") or "").replace(" ", "").upper()
    if iban:
        a.append(_attr("ibanContrib", iban, 24))
    a.append(_attr("imputernicit", imp))
    if imp == 1:
        a.append(_attr("numeImputernicit", manual.get("numeImputernicit"), 75))
        a.append(_attr("cifImputernicit", _cif(manual.get("cifImputernicit"))))
        a.append(_attr("nrImputernicit", manual.get("nrImputernicit"), 50))
        a.append(_attr("dataImputernicit", _data(manual.get("dataImputernicit"))[0], 10))
        a.append(_attr("judetImputernicit", manual.get("judetImputernicit"), 2))
        for name, lim in (("localitateImputernicit", 200), ("stradaImputernicit", 200),
                          ("mentiuniAdresaImputernicit", 200), ("telefonImputernicit", 15),
                          ("faxImputernicit", 15), ("emailImputernicit", 250)):
            if manual.get(name):
                a.append(_attr(name, manual.get(name), lim))
    a.append(_attr("exceptare", int(manual.get("exceptare"))))
    a.append(_attr("statAsigurare", str(manual.get("statAsigurare") or "").upper(), 2))
    a.append(_attr("dataInceput", _data(manual.get("dataInceput"))[0], 10))
    a.append(_attr("dataSfarsit", _data(manual.get("dataSfarsit"))[0], 10))
    if manual.get("dataExceptare"):
        a.append(_attr("dataExceptare", _data(manual.get("dataExceptare"))[0], 10))
    if manual.get("documente"):
        a.append(_attr("documente", manual.get("documente"), 500))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<d603 xmlns="%s"%s/>\n' % (NS, "".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D603 nu se poate genera: " + " ".join(er))
    total = calcul_d603(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat603(an=an, luna=luna, total_plata_a=total,
                      stat_asigurare=str(manual.get("statAsigurare") or "").upper())
    return xml, res
