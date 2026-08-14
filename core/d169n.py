"""core/d169n.py - D169n: Declaratie privind neconcordantele dintre informatiile privind beneficiarii
reali disponibile in Registrul central al fiduciilor si al constructiilor juridice similare fiduciilor
si informatiile detinute de autoritati/entitati raportoare.

ATENTIE (neconcordanta cu premisa sarcinii): D169n NU este raspunsul la notificarea e-TVA (decont
precompletat). Bytecode-ul validatorului D169nValidator.jar si actul oficial (OPANAF 2175/2025, Anexa nr.6)
o definesc drept declaratia de NECONCORDANTE privind BENEFICIARUL REAL AL FIDUCIEI, temei art.19 alin.(11) si
art.4 alin.(2) lit.b) din Legea nr.129/2019 (prevenirea spalarii banilor). Nu exista niciun camp de decont,
rand, suma sau neconcordanta e-TVA in schema. Sursa (validator + act) bate memoria/premisa.

Declaratie MANUALA depusa de o autoritate/entitate raportoare. Aplicatia nu are Registrul central al
fiduciilor si nici lista beneficiarilor reali - toate datele vin din `manual`. Fara persoana juridica proprie
in joc: `pull` nu atinge baza, deci `genereaza` merge si cu conn=None.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator). Radacina, campurile si sectiunea
repetabila au fost CITITE din bytecode (d169nvalidator/v0/D169n.class + BenefR.class) si PROBATE camp cu camp
pe validator (java -jar DUKIntegrator.jar -v D169n). Confirmat:
  - RADACINA: <D169n> (nu `declaratie`/`declaratie169n`); namespace mfp:anaf:dgti:d169n:declaratie:v1.
  - Sectiune repetabila: <benefR> (cate un beneficiar real), MAX_OCC_BENEFR.
  - Atribute radacina: an, luna, nume, functie (semnatar); den_E, cif, judet_E, sector_E, localit_E, adresa_E,
    codp_E, tel_E, fax_E, email_E (A. entitate raportoare); den_R, calit_R (B. reprezentant legal);
    den_F, cif_F, judet_F, sector_F, localit_F, adresa_F, codp_F, tel_F, fax_F, email_F (C. fiduciar);
    nr_contract, data_contract (contractul de fiducie).
  - Atribute benefR: den_B, cif_B, data_nasterii_B, actId_B, stat_cetatenie_B, stat_resedinta_B, adresa_B,
    mod_control_B, cal1_B..cal4_B (calitatea beneficiarului real), natura, mentiuni (D + E neconcordante).

Reguli citite din validator (probate camp cu camp):
  - DUK regula luna: luna trebuie sa fie 12 (valoare fixa; orice alta valoare "nu se incadreaza in interval").
  - DUK regula sector judet 40: 'sectorul este obligatoriu pt judetul 40' (Bucuresti). Pt alte judete e optional.
  - DUK regula R40: '9.Calitatea necompletata' - cel putin o calitate (cal1_B..cal4_B) trebuie bifata.
    Fiecare calX_B accepta DOAR valoarea "1" (bifat); nebifat = atribut OMIS (nu "0", care e respins "nu se afla in lista").
  - DUK regula R33.1: daca stat_resedinta_B=null si cif_B#null atunci verificare cif_B(13) (rezident RO -> CNP 13 cifre).
  - DUK regula RUnicitate: 'Unicitate beneficiari reali' - perechile (den_B, cif_B) trebuie sa fie unice.
  - DUK regula stat_resedinta_B: 'stat_resedinta_B trebuie sa fie diferit de RO' (pt rezidenti RO se omite, se da CNP).

Campuri OBLIGATORII (probate minimal pe validator): an, luna(=12), nume, functie, den_E, cif, judet_E,
localit_E, adresa_E (+sector_E daca judet_E=40), den_R, calit_R, den_F, cif_F, judet_F, localit_F, adresa_F
(+sector_F daca judet_F=40), nr_contract, data_contract; pe benefR: den_B, cif_B, data_nasterii_B, actId_B,
adresa_B, mod_control_B, natura, mentiuni si cel putin o calitate.
OPTIONALE (emise doar daca sunt date): codp_E, tel_E, fax_E, email_E, codp_F, tel_F, fax_F, email_F,
stat_cetatenie_B, stat_resedinta_B.

NEPOPULAT deliberat: nu exista niciun camp monetar in schema (deci nici rotunjire) - declaratia nu contine
sume. Registrul central al fiduciilor nu e in aplicatie, deci datele nu se pot pre-completa automat.

Contract dXXX: pull/erori_generare/calcul_d169n/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d169n:declaratie:v1"
LUNA_FIXA = 12  # DUK regula luna: perioada declaratiei = luna 12 (valoare fixa acceptata de validator)

_NEDIGIT = re.compile(r"\D")
_DATA_RE = re.compile(r"^(\d{2})\.(\d{2})\.(\d{4})$")
_DATA_ISO = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_JUDET_BUCURESTI = "40"  # DUK regula sector judet 40
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


def _data(x):
    """Normalizeaza la zz.ll.aaaa (formatul acceptat de validator). Accepta si aaaa-ll-zz. Fara strftime."""
    s = str(x or "").strip()
    m = _DATA_RE.match(s)
    if m:
        return s
    m = _DATA_ISO.match(s)
    if m:
        return "%s.%s.%s" % (m.group(3), m.group(2), m.group(1))
    return ""


def _judet(x):
    return _cif(x)


def _calitati(b):
    """Intoarce lista ordonata de calitati bifate din {1,2,3,4}.
    Accepta `calitati=[...]` sau flag-uri individuale cal1..cal4 (orice valoare truthy)."""
    vals = b.get("calitati")
    out = set()
    if vals:
        for v in vals:
            iv = _cif(v)
            if iv in ("1", "2", "3", "4"):
                out.add(iv)
    for i in ("1", "2", "3", "4"):
        v = b.get("cal%s_B" % i, b.get("cal%s" % i))
        if v not in (None, "", 0, "0", False):
            out.add(i)
    return sorted(out)


@dataclass
class Rezultat169n:
    an: int
    luna: int
    nr_beneficiari: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d169n(manual):
    """Fara sume in schema: singurul agregat este numarul de beneficiari reali declarati."""
    benef = manual.get("beneficiari") or []
    return {"nr_beneficiari": len(benef)}


def pull(conn, schema, perioada):
    """D169n e MANUALA (Registrul central al fiduciilor nu e in aplicatie). Contractul cere `pull`.
    Nu atinge baza -> merge si cu conn=None."""
    return {}


def _erori_beneficiar(b, idx):
    er = []
    p = "beneficiar %d:" % idx
    if not str(b.get("den_B") or "").strip():
        er.append("%s lipsa nume si prenume (den_B)." % p)
    rez = _cif(b.get("stat_resedinta_B"))
    stat_res = str(b.get("stat_resedinta_B") or "").strip().upper()
    # DUK regula R33.1: rezident RO (fara stat_resedinta_B) -> cif_B = CNP 13 cifre
    if not stat_res:
        if not _cnp_valid(b.get("cif_B")):
            er.append("%s CNP (cif_B) invalid pentru rezident RO - astept 13 cifre cu cifra de control (R33.1)." % p)
    else:
        # DUK regula stat_resedinta_B: trebuie diferit de RO
        if stat_res == "RO":
            er.append("%s stat_resedinta_B trebuie sa fie diferit de RO (pt rezidenti RO se omite si se da CNP)." % p)
        if not str(b.get("cif_B") or "").strip():
            er.append("%s lipsa cod de identificare fiscala (cif_B)." % p)
    if not _data(b.get("data_nasterii_B")):
        er.append("%s data nasterii (data_nasterii_B) invalida - astept zz.ll.aaaa." % p)
    if not str(b.get("actId_B") or "").strip():
        er.append("%s lipsa serie si numar act de identitate (actId_B)." % p)
    if not str(b.get("adresa_B") or "").strip():
        er.append("%s lipsa domiciliu/resedinta (adresa_B)." % p)
    if not str(b.get("mod_control_B") or "").strip():
        er.append("%s lipsa modalitatea de exercitare a controlului (mod_control_B)." % p)
    if not str(b.get("natura") or "").strip():
        er.append("%s lipsa natura si amploarea interesului (natura)." % p)
    if not str(b.get("mentiuni") or "").strip():
        er.append("%s lipsa mentiuni privind neconcordantele (mentiuni)." % p)
    if not _calitati(b):
        er.append("%s cel putin o calitate a beneficiarului real (1-4) trebuie bifata (R40)." % p)
    return er


def erori_generare(prof, manual):
    er = []
    # A. entitate raportoare
    if not str(manual.get("den_E") or "").strip():
        er.append("Lipsa denumire entitate raportoare (den_E).")
    if not (2 <= len(_cif(manual.get("cif"))) <= 10):
        er.append("CIF entitate raportoare (cif) invalid - astept 2-10 cifre.")
    if not _judet(manual.get("judet_E")):
        er.append("Lipsa judet entitate (judet_E) - cod numeric de judet.")
    if _judet(manual.get("judet_E")) == _JUDET_BUCURESTI and not str(manual.get("sector_E") or "").strip():
        er.append("Sectorul (sector_E) este obligatoriu pentru judetul 40 (Bucuresti).")
    if not str(manual.get("localit_E") or "").strip():
        er.append("Lipsa localitate entitate (localit_E).")
    if not str(manual.get("adresa_E") or "").strip():
        er.append("Lipsa adresa entitate (adresa_E).")
    # semnatar
    if not str(manual.get("nume") or "").strip():
        er.append("Lipsa nume semnatar (nume).")
    if not str(manual.get("functie") or "").strip():
        er.append("Lipsa functie semnatar (functie).")
    # B. reprezentant legal
    if not str(manual.get("den_R") or "").strip():
        er.append("Lipsa nume si prenume reprezentant legal (den_R).")
    if not str(manual.get("calit_R") or "").strip():
        er.append("Lipsa calitatea reprezentantului legal (calit_R).")
    # C. fiduciar
    if not str(manual.get("den_F") or "").strip():
        er.append("Lipsa denumire fiduciar (den_F).")
    if not (2 <= len(_cif(manual.get("cif_F"))) <= 10):
        er.append("CIF fiduciar (cif_F) invalid - astept 2-10 cifre.")
    if not _judet(manual.get("judet_F")):
        er.append("Lipsa judet fiduciar (judet_F) - cod numeric de judet.")
    if _judet(manual.get("judet_F")) == _JUDET_BUCURESTI and not str(manual.get("sector_F") or "").strip():
        er.append("Sectorul (sector_F) este obligatoriu pentru judetul 40 (Bucuresti).")
    if not str(manual.get("localit_F") or "").strip():
        er.append("Lipsa localitate fiduciar (localit_F).")
    if not str(manual.get("adresa_F") or "").strip():
        er.append("Lipsa adresa fiduciar (adresa_F).")
    # contract de fiducie
    if not str(manual.get("nr_contract") or "").strip():
        er.append("Lipsa numarul contractului de fiducie (nr_contract).")
    if not _data(manual.get("data_contract")):
        er.append("Data contractului de fiducie (data_contract) invalida - astept zz.ll.aaaa.")
    # D. beneficiari reali
    benef = manual.get("beneficiari") or []
    if not benef:
        er.append("Lipsa beneficiari reali - cel putin unul este obligatoriu (sectiunea benefR).")
    perechi = set()
    for i, b in enumerate(benef, 1):
        er.extend(_erori_beneficiar(b, i))
        cheie = (str(b.get("den_B") or "").strip().upper(), _cif(b.get("cif_B")))
        if cheie in perechi:
            er.append("beneficiar %d: duplicat (den_B, cif_B) - unicitate beneficiari reali (RUnicitate)." % i)
        perechi.add(cheie)
    return er


def _attr(name, val, lim=None):
    v = _esc(val, lim)
    return '%s="%s"' % (name, v) if v != "" else ""


def _benefR_xml(b):
    a = []
    a.append(_attr("den_B", b.get("den_B"), 200))
    a.append(_attr("cif_B", _cif(b.get("cif_B"))))
    a.append(_attr("data_nasterii_B", _data(b.get("data_nasterii_B"))))
    a.append(_attr("actId_B", b.get("actId_B"), 50))
    stat_cet = str(b.get("stat_cetatenie_B") or "").strip().upper()
    if stat_cet:
        a.append(_attr("stat_cetatenie_B", stat_cet, 2))
    stat_res = str(b.get("stat_resedinta_B") or "").strip().upper()
    if stat_res:
        a.append(_attr("stat_resedinta_B", stat_res, 2))
    a.append(_attr("adresa_B", b.get("adresa_B"), 400))
    a.append(_attr("mod_control_B", b.get("mod_control_B"), 500))
    for i in _calitati(b):
        a.append('cal%s_B="1"' % i)  # DUK regula R40: bifat = "1"
    a.append(_attr("natura", b.get("natura"), 500))
    a.append(_attr("mentiuni", b.get("mentiuni"), 500))
    return "  <benefR %s/>" % " ".join(x for x in a if x)


def build_xml(prof, an, luna, manual):
    h = []
    h.append('luna="%d"' % LUNA_FIXA)  # DUK regula luna: fix 12
    h.append('an="%d"' % int(an))
    h.append(_attr("nume", manual.get("nume"), 75))
    h.append(_attr("functie", manual.get("functie"), 75))
    # A. entitate raportoare
    h.append(_attr("den_E", manual.get("den_E"), 200))
    h.append(_attr("cif", _cif(manual.get("cif"))))
    h.append(_attr("judet_E", _judet(manual.get("judet_E"))))
    if str(manual.get("sector_E") or "").strip():
        h.append(_attr("sector_E", _cif(manual.get("sector_E"))))
    h.append(_attr("localit_E", manual.get("localit_E"), 100))
    h.append(_attr("adresa_E", manual.get("adresa_E"), 400))
    for k, lim in (("codp_E", 6), ("tel_E", 15), ("fax_E", 15), ("email_E", 250)):
        if str(manual.get(k) or "").strip():
            h.append(_attr(k, manual.get(k), lim))
    # B. reprezentant legal
    h.append(_attr("den_R", manual.get("den_R"), 200))
    h.append(_attr("calit_R", manual.get("calit_R"), 100))
    # C. fiduciar
    h.append(_attr("den_F", manual.get("den_F"), 200))
    h.append(_attr("cif_F", _cif(manual.get("cif_F"))))
    h.append(_attr("judet_F", _judet(manual.get("judet_F"))))
    if str(manual.get("sector_F") or "").strip():
        h.append(_attr("sector_F", _cif(manual.get("sector_F"))))
    h.append(_attr("localit_F", manual.get("localit_F"), 100))
    h.append(_attr("adresa_F", manual.get("adresa_F"), 400))
    for k, lim in (("codp_F", 6), ("tel_F", 15), ("fax_F", 15), ("email_F", 250)):
        if str(manual.get(k) or "").strip():
            h.append(_attr(k, manual.get(k), lim))
    # contract de fiducie
    h.append(_attr("nr_contract", manual.get("nr_contract"), 50))
    h.append(_attr("data_contract", _data(manual.get("data_contract"))))
    benef = manual.get("beneficiari") or []
    corp = "\n".join(_benefR_xml(b) for b in benef)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D169n xmlns="%s" %s>\n%s\n</D169n>\n'
            % (NS, " ".join(x for x in h if x), corp))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = LUNA_FIXA
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D169n nu se poate genera: " + " ".join(er))
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat169n(an=an, luna=luna, nr_beneficiari=len(manual.get("beneficiari") or []))
    return xml, res
