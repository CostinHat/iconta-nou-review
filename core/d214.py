"""core/d214.py — D214: Cerere pentru stabilirea impozitului pe venitul din instrainarea de terenuri agricole.

Titlu oficial (OPANAF 216/2023): "Cerere pentru stabilirea impozitului privind venitul realizat de
persoana fizica si/sau juridica din instrainarea, prin hotarare judecatoreasca, a terenurilor agricole
situate in extravilan/pachetului de control al persoanelor juridice care au in proprietate unul sau mai
multe terenuri agricole situate in extravilan". Sursa: static.anaf.ro (schema XSD actualizata 22.06.2026).

Declaratie MANUALA depusa de contribuabil (persoana fizica si/sau juridica) in legatura cu un act de
instrainare a unui teren agricol extravilan (respectiv a pachetului de control): contribuabilul SOLICITA
organului fiscal STABILIREA impozitului pe venitul realizat. Aplicatia nu are registru de contribuabili
persoane fizice, nici datele actului (hotararea judecatoreasca) - toate vin din `manual`. Contribuabilul
NU calculeaza cuantumul; organul fiscal il determina, de aceea suma de control (totalPlata_A) este 0
(DUK regula R7).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul peste anexe, DUKIntegrator). Namespace si
structura au fost CITITE din bytecode-ul D214Validator.jar (constant pool + fluxul checkTag pe
clasa d214validator/v0/D214), radacina PROBATA pe validator:
  - Namespace: mfp:anaf:dgti:d214:declaratie:v1
  - Radacina (element unic, structura plata, fara copii): <D214> (bytecode: TAG_COUNT=1, clasa D214)
  - Atribute in ORDINEA de citire a validatorului (nextAttribute* secvential): d_rec, cifContribuabil,
    an, luna, numeContribuabil, adresaContribuabil, totalPlata_A, taraRezidenta, actInstrainare,
    dataAct, optiuneInstrainare, telC, faxC, emailC, denR, cifR, adresaR, telR, faxR, emailR,
    numeD, functieD.
Reguli citite din validator (probate):
  - DUK regula R7: "Suma de control (totalPlata_A) trebuie sa fie 0" => totalPlata_A = 0 mereu.
  - DUK regula R8/checkNIF: daca cifContribuabil este un NIF (nerezident) atunci taraRezidenta
    (cod ISO numeric din nomenclatorul _nomenTari, ex. Romania=642) este OBLIGATORIU.
  - optiuneInstrainare ∈ {1, 2} (lista _optiuneInstrainare din Parameters_v0).

Campuri OBLIGATORII (probate pe validator): cifContribuabil, an, luna, numeContribuabil,
adresaContribuabil, totalPlata_A (=0), taraRezidenta, actInstrainare, dataAct, optiuneInstrainare,
numeD, functieD. (d_rec se emite mereu cu 0 = declaratie initiala.)

Modulul implementeaza CAZUL PRINCIPAL: persoana fizica REZIDENTA (cifContribuabil = CNP, taraRezidenta
implicit 642), fara reprezentant fiscal. NEPOPULAT deliberat (optional, nu se ghiceste): blocul
reprezentant/imputernicit (denR/cifR/adresaR/telR/faxR/emailR) si datele de contact
(telC/faxC/emailC) - se adauga la nevoie, pe aceeasi metoda `manual`.

Contract dXXX: pull/erori_generare/calcul_d214/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Cerere pentru stabilirea impozitului pe venitul din înstrăinarea de terenuri agricole'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d214:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
_OPTIUNI = ("1", "2")
_DATA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_DATA_RO = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")


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


def _bani(x):
    """Rotunjire monetara half-up cu Decimal (nu bancara; fara zecimale = lei intregi)."""
    try:
        d = Decimal(str(x).replace(",", ".")) if x not in (None, "") else Decimal(0)
    except Exception:
        d = Decimal(0)
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Rezultat214:
    an: int
    luna: int
    total_plata_a: int = 0
    contribuabil: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d214(manual):
    """Suma de control (DUK regula R7): totalPlata_A trebuie sa fie 0 - organul fiscal stabileste impozitul."""
    return {"totalPlata_A": 0}


def pull(conn, schema, perioada):
    """D214 e MANUALA pe persoana fizica; aplicatia nu are registru de persoane. Contractul cere `pull`."""
    return {}


def _data_act(manual):
    """Data actului de instrainare in format calendaristic ANAF ZZ.LL.AAAA (validatorul respinge ISO).

    Accepta la intrare string ZZ.LL.AAAA, string ISO AAAA-LL-ZZ, sau parti zi_act/luna_act/an_act.
    """
    d = str(manual.get("dataAct") or "").strip()
    m = _DATA_RO.match(d)
    if m:
        z, l, a = m.group(1), m.group(2), m.group(3)
        return "%s.%s.%s" % (z, l, a)
    m = _DATA_ISO.match(d)
    if m:
        a, l, z = m.group(1), m.group(2), m.group(3)
        return "%s.%s.%s" % (z, l, a)
    z, l, a = manual.get("zi_act"), manual.get("luna_act"), manual.get("an_act")
    if z and l and a:
        return "%02d.%02d.%04d" % (int(z), int(l), int(a))
    return ""


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsă nume/denumire contribuabil (nume_c).")
    if not str(manual.get("adresa_c") or "").strip():
        er.append("Lipsă adresa contribuabil (adresa_c).")
    cif = _cif(manual.get("cif_c"))
    nif = bool(manual.get("nif"))
    if not cif:
        er.append("Lipsă CIF/CNP contribuabil (cif_c).")
    elif not nif and not _cnp_valid(cif):
        er.append("CNP contribuabil (cif_c) invalid (13 cifre + cifra de control); pentru NIF nerezident setează nif=1.")
    if nif and not _cif(manual.get("taraRezidenta")):
        er.append("cif_c e NIF nerezident: setează taraRezidenta cu codul ISO numeric al tarii de rezidență (DUK regula R8).")
    if not _data_act(manual):
        er.append("Lipsă/format greșit data act instrainare (dataAct ZZ.LL.AAAA sau zi_act/luna_act/an_act).")
    if not str(manual.get("actInstrainare") or "").strip():
        er.append("Lipsă identificator act de instrainare (actInstrainare).")
    if str(manual.get("optiuneInstrainare") or "1") not in _OPTIUNI:
        er.append("optiuneInstrainare trebuie să fie 1 sau 2.")
    if not str(manual.get("numeD") or "").strip():
        er.append("Lipsă nume semnatar declarație (numeD) - obligatoriu.")
    if not str(manual.get("functieD") or "").strip():
        er.append("Lipsă funcție/calitate semnatar (functieD) - obligatoriu.")
    return er


def _attr(lst, nume, val):
    if val is not None and str(val) != "":
        lst.append('%s="%s"' % (nume, val))


def build_xml(prof, an, luna, manual):
    total = calcul_d214(manual)["totalPlata_A"]
    cif = _cif(manual.get("cif_c"))
    a = []
    _attr(a, "d_rec", int(manual.get("d_rec") or 0))
    _attr(a, "cifContribuabil", cif)
    _attr(a, "an", int(an))
    _attr(a, "luna", int(luna))
    _attr(a, "numeContribuabil", _esc(manual.get("nume_c"), 75))
    _attr(a, "adresaContribuabil", _esc(manual.get("adresa_c"), 200))
    _attr(a, "totalPlata_A", total)
    # DUK regula R8: taraRezidenta e ceruta neconditionat (checkNIF clasifica si CNP-ul ca NIF in
    # aceasta versiune de validator). Rezident => Romania (642); nerezident cu NIF => tara din manual.
    _attr(a, "taraRezidenta", _cif(manual.get("taraRezidenta")) or "642")
    _attr(a, "actInstrainare", _esc(manual.get("actInstrainare"), 100))
    _attr(a, "dataAct", _data_act(manual))
    _attr(a, "optiuneInstrainare", str(manual.get("optiuneInstrainare") or "1"))
    # contact contribuabil (optional)
    _attr(a, "telC", _esc(manual.get("telC"), 15))
    _attr(a, "faxC", _esc(manual.get("faxC"), 15))
    _attr(a, "emailC", _esc(manual.get("emailC"), 250))
    # reprezentant fiscal / imputernicit (optional)
    _attr(a, "denR", _esc(manual.get("denR"), 75))
    if manual.get("cifR"):
        _attr(a, "cifR", _cif(manual.get("cifR")))
    _attr(a, "adresaR", _esc(manual.get("adresaR"), 200))
    _attr(a, "telR", _esc(manual.get("telR"), 15))
    _attr(a, "faxR", _esc(manual.get("faxR"), 15))
    _attr(a, "emailR", _esc(manual.get("emailR"), 250))
    # semnatar declaratie (optional)
    _attr(a, "numeD", _esc(manual.get("numeD"), 75))
    _attr(a, "functieD", _esc(manual.get("functieD"), 75))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D214 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D214 nu se poate genera: " + " ".join(er))
    total = calcul_d214(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat214(an=an, luna=luna, total_plata_a=total,
                      contribuabil=str(manual.get("nume_c") or ""))
    return xml, res
