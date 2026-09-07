"""core/d230.py — D230: Cerere privind destinatia sumei de pana la 3,5% din impozitul anual (redirectionare ONG).

Declaratie MANUALA (persoana fizica): contribuabilul redirectioneaza pana la 3,5% din impozitul pe venit
catre o entitate nonprofit/unitate de cult. Aplicatia nu are registru de persoane fizice si nici beneficiarul
ales - toate vin din `manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul peste anexe, DUKIntegrator). Structura schemei in
vigoare (namespace declaratie:v5, pachet d230validator/v1) a fost CITITA din bytecode-ul D230Validator.jar
(numele campurilor pe clasele Declaratie230 / Bursa_entit) si PROBATA camp cu camp pe validator:
  - Bursa_entit v5: bifa_bursa, bifa_entitate, den_entitate, cif_entitate, cont_entitate, contract_bursa,
    doc_plata_bursa, suma_bursa, suma_entitate, cota, procent, valabilitate_distribuire, acord.
    NU are bifa_sal/bifa_pens/sectiune (acelea sunt in v4/pachet v104, versiune anterioara).
  - e_sectiune1/e_sectiune2 sunt campuri INTERNE ale validatorului, NU atribute XML (respinse ca necunoscute).
Reguli citite din validator (probate): R_optiune (bifa_entitate=1 => valabilitate_distribuire<>null,
OBLIGATORIU); R_procent (procent <= 3.5); R31 (totalPlata_A = suma de control = suma sumelor declarate; 0 cand
suma nu e specificata, ANAF determina cuantumul).

Modulul implementeaza CAZUL PRINCIPAL: redirectionare catre O entitate (bifa_entitate=1), ANAF determina
cuantumul (suma_entitate omisa) sau suma exacta specificata. LIMITARI documentate: bursa privata (bifa_bursa),
mai multi beneficiari intr-un fisier, imputernicit (den_i/cif_i) - se adauga la nevoie, pe aceeasi metoda.
NEPOPULAT deliberat (nu se ghiceste, camp optional cu semantica nedeterminata din act): `acord`, `cota`.

Contract dXXX: pull/erori_generare/calcul_d230/build_xml/genereaza(conn, schema, perioada).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Cerere privind destinația sumei de până la 3,5% din impozitul anual (redirecționare ONG)'
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d230:declaratie:v5"
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
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


def _procent(x):
    """procent <= 3,5 (regula R_procent). Implicit 3.5 (redirectionarea maxima)."""
    try:
        p = float(str(x).replace(",", ".")) if x not in (None, "") else 3.5
    except ValueError:
        p = 3.5
    if p > 3.5:
        p = 3.5
    # format zecimal cu maxim o zecimala, fara zerouri inutile (3.5 / 2)
    return ("%.1f" % p).rstrip("0").rstrip(".")


@dataclass
class Rezultat230:
    an: int
    luna: int
    total_plata_a: int = 0
    beneficiar: str = ""
    avertismente: list = field(default_factory=list)


def calcul_d230(manual):
    """Suma de control (R31): suma sumelor declarate. 0 cand suma nu e specificata (ANAF determina)."""
    suma = _cif(manual.get("suma_entitate"))
    return {"totalPlata_A": int(suma) if suma else 0}


def pull(conn, schema, perioada):
    """D230 e MANUALA pe persoana fizica; firma nu are registru de persoane. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsă nume contribuabil (nume_c).")
    if not str(manual.get("prenume_c") or "").strip():
        er.append("Lipsă prenume contribuabil (prenume_c).")
    if not str(manual.get("initiala_c") or "").strip():
        er.append("Lipsă initiala tata (initiala_c).")
    if not _cnp_valid(manual.get("cif_c")):
        er.append("CNP contribuabil (cif_c) invalid (13 cifre + cifra de control).")
    if not str(manual.get("den_entitate") or "").strip():
        er.append("Lipsă denumire entitate beneficiara (den_entitate).")
    if not (2 <= len(_cif(manual.get("cif_entitate"))) <= 10):
        er.append("CIF entitate (cif_entitate) invalid.")
    iban = str(manual.get("cont_entitate") or "").replace(" ", "").upper()
    if not _IBAN_OK.match(iban):
        er.append("IBAN entitate (cont_entitate) invalid - aștept RO + 22 caractere.")
    try:
        valab = int(manual.get("valabilitate_distribuire"))
    except (TypeError, ValueError):
        valab = 0
    if valab not in (1, 2):
        er.append("valabilitate_distribuire obligatoriu 1 (un an) sau 2 (doi ani) - regula R_optiune.")
    return er


def build_xml(prof, an, luna, manual):
    iban = str(manual.get("cont_entitate") or "").replace(" ", "").upper()
    total = calcul_d230(manual)["totalPlata_A"]
    valab = int(manual.get("valabilitate_distribuire"))
    h = []
    h.append('luna="12"')  # structura: perioada de raportare luna=12 (fix)
    h.append('an="%d"' % int(an))
    h.append('nume_c="%s"' % _esc(manual.get("nume_c"), 75))
    h.append('initiala_c="%s"' % _esc(manual.get("initiala_c"), 1))
    h.append('prenume_c="%s"' % _esc(manual.get("prenume_c"), 75))
    if manual.get("adresa_c"):
        h.append('adresa_c="%s"' % _esc(manual.get("adresa_c"), 200))
    if manual.get("telefon_c"):
        h.append('telefon_c="%s"' % _esc(manual.get("telefon_c"), 15))
    if manual.get("email_c"):
        h.append('email_c="%s"' % _esc(manual.get("email_c"), 250))
    h.append('cif_c="%s"' % _cif(manual.get("cif_c")))
    h.append('totalPlata_A="%d"' % total)
    b = []
    b.append('bifa_bursa="0"')
    b.append('bifa_entitate="1"')
    b.append('den_entitate="%s"' % _esc(manual.get("den_entitate"), 60))
    b.append('cif_entitate="%s"' % _cif(manual.get("cif_entitate")))
    b.append('cont_entitate="%s"' % _esc(iban, 24))
    if _cif(manual.get("suma_entitate")):
        b.append('suma_entitate="%s"' % _cif(manual.get("suma_entitate")))
    b.append('procent="%s"' % _procent(manual.get("procent")))
    b.append('valabilitate_distribuire="%d"' % valab)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie230 xmlns="%s" %s>\n'
            '  <bursa_entit %s/>\n'
            '</declaratie230>\n' % (NS, " ".join(h), " ".join(b)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D230 nu se poate genera: " + " ".join(er))
    total = calcul_d230(manual)["totalPlata_A"]
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat230(an=an, luna=luna, total_plata_a=total,
                      beneficiar=str(manual.get("den_entitate") or ""))
    return xml, res
