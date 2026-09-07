"""core/d216.py - D216: Declaratie privind impozitul special pe bunurile imobile si mobile de valoare mare.

Declaratie ANUALA (Legea 296/2023, impozit special pe bunuri de valoare mare). Contribuabilul declara
bunurile imobile rezidentiale cu valoare peste plafon si autovehiculele/bunurile mobile de valoare mare,
platind un impozit special. Aplicatia NU are registru de bunuri de valoare mare al contribuabilului -
toate datele bunurilor (valoare impozabila, cota, plafon, coduri SIRUTA) vin din `manual` (input contabil).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (arbitrul, DUKIntegrator). Namespace declaratie:v1,
pachet d216validator/v0 - structura CITITA din bytecode-ul D216Validator.jar (numele campurilor pe
clasele D216 / Bun_imobil / Bun_mobil) si PROBATA camp cu camp pe validator:
  - Antet D216: luna, an, d_rec, nume, cif, domiciliuFiscal, impozit_imobile, impozit_mobile,
    totalPlata_A, nume_intocmit, functia_intocmit (toate obligatorii; imputernicit optional:
    nume_imputernicit + cif_imputernicit conditionati reciproc).
  - bun_imobil (repetabil, tag XML minuscul): judet_imobil, cod_judet_imobil, localitate_imobil,
    cod_localitate_imobil, strada_imobil, cod_strada_imobil, nr_cadastral, valoare_impozabila_imobil,
    cota, plafon_imobil, baza_imobil, impozit_imobil (optional: nr_strada).
  - bun_mobil (repetabil, tag XML minuscul): an_detinere, niv, valoare_impozabila_mobil, plafon_mobil,
    baza_mobil, impozit_mobil.

Reguli citite din validator si PROBATE pe DUK (D216Validator.jar):
  - R4: totalPlata_A = suma cifrelor din cif (regula de control a validatorului - literala, nu economica).
  - impozit_imobile = suma tuturor impozit_imobil; impozit_mobile = suma tuturor impozit_mobil.
  - d_rec=0 => valoare_impozabila_imobil > plafon_imobil; valoare_impozabila_mobil > plafon_mobil.
  - R28.1: baza_imobil = (valoare_impozabila_imobil - plafon_imobil) * cota / 100.
  - impozit_imobil = ROUND(baza_imobil * COTA_IMPOZIT / 100).
  - R36.1: baza_mobil = valoare_impozabila_mobil - plafon_mobil; impozit_mobil = ROUND(baza_mobil * COTA_IMPOZIT / 100).
  - cod_judet_imobil in lista codurilor de judet (1..52); 0 < cota <= 100; niv in interval intreg.

CRITIC: actul (Legea 296/2023) NU este in corpus. NU se hardcodeaza cota si nici plafoanele -
valorile impozabile, cota si plafoanele sunt introduse de contabil in `manual`. COTA_IMPOZIT (rata
ROUND din formula de impozit) este o CONSTANTA de calcul a VALIDATORULUI (nu a actului), impusa de
aritmetica lui - documentata, nu ghicita. Totalurile de antet = sumele/regulile aritmetice ale listelor.
d_rec="0" implicit (declaratie initiala).

Contract dXXX: pull/erori_generare/calcul_d216/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind impozitul special pe bunurile imobile și mobile de valoare mare'
from dataclasses import dataclass, field
import re
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d216:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_Q = chr(34)

# Rata din formula de impozit a VALIDATORULUI (ROUND(baza * COTA_IMPOZIT / 100)). Constanta de calcul
# a lui D216Validator.jar (probata pe DUK), NU o valoare din act - actul nu e in corpus.
COTA_IMPOZIT = 0.3


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _suma_cifre(cif):
    """R4: totalPlata_A = suma cifrelor din cif (regula de control literala a validatorului)."""
    return sum(int(d) for d in _cif(cif))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace(_Q, "&quot;").strip()
    return t[:lim] if lim else t


def _int(x):
    try:
        return (int(Decimal(str(str(x).replace(",", "."))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))) if x not in (None, "") else 0
    except (TypeError, ValueError):
        return 0


def _cota(x):
    """cota procentuala pe bunul imobil (0 < cota <= 100). Vine din manual (NU se hardcodeaza)."""
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return 0.0


def _cota_str(c):
    return ("%.4f" % c).rstrip("0").rstrip(".")


def _round(x):
    """ROUND half-up ca in validator (Math.round pe pozitiv)."""
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def _calc_imobil(b):
    """baza_imobil = (val - plafon)*cota/100 (R28.1); impozit_imobil = ROUND(baza * COTA_IMPOZIT/100)."""
    val = _int(b.get("valoare_impozabila_imobil"))
    plafon = _int(b.get("plafon_imobil"))
    cota = _cota(b.get("cota"))
    baza = _round((val - plafon) * cota / 100.0)
    imp = _round(baza * COTA_IMPOZIT / 100.0)
    return baza, imp


def _calc_mobil(b):
    """baza_mobil = val - plafon (R36.1); impozit_mobil = ROUND(baza * COTA_IMPOZIT/100)."""
    val = _int(b.get("valoare_impozabila_mobil"))
    plafon = _int(b.get("plafon_mobil"))
    baza = val - plafon
    imp = _round(baza * COTA_IMPOZIT / 100.0)
    return baza, imp


@dataclass
class Rezultat216:
    an: int
    luna: int
    impozit_imobile: int = 0
    impozit_mobile: int = 0
    total_plata_a: int = 0
    nr_imobile: int = 0
    nr_mobile: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d216(manual):
    """Totaluri antet = regulile aritmetice ale listelor.
    impozit_imobile = suma impozitelor pe bunuri imobile; impozit_mobile = suma impozit_mobil;
    totalPlata_A = suma cifrelor din cif (R4, regula de control a validatorului)."""
    imob = manual.get("imobile") or []
    mob = manual.get("mobile") or []
    ti = sum(_calc_imobil(b)[1] for b in imob)
    tm = sum(_calc_mobil(b)[1] for b in mob)
    return {"impozit_imobile": ti, "impozit_mobile": tm, "totalPlata_A": _suma_cifre(manual.get("cif"))}


def pull(conn, schema, perioada):
    """D216 e MANUALA (bunuri de valoare mare ale contribuabilului); firma nu are registru. Contractul cere pull."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume") or "").strip():
        er.append("Lipsă nume contribuabil (nume).")
    if not (2 <= len(_cif(manual.get("cif"))) <= 13):
        er.append("CIF/CNP contribuabil (cif) invalid.")
    if not str(manual.get("domiciliuFiscal") or "").strip():
        er.append("Lipsă domiciliu fiscal (domiciliuFiscal).")
    if not str(manual.get("nume_intocmit") or "").strip():
        er.append("Lipsă nume intocmit (nume_intocmit) - obligatoriu.")
    if not str(manual.get("functia_intocmit") or "").strip():
        er.append("Lipsă funcția intocmit (functia_intocmit) - obligatoriu.")
    imob = manual.get("imobile") or []
    mob = manual.get("mobile") or []
    if not imob and not mob:
        er.append("Cel puțin un bun (imobil sau mobil) trebuie declarat.")
    for i, b in enumerate(imob, 1):
        for camp in ("judet_imobil", "cod_judet_imobil", "localitate_imobil", "cod_localitate_imobil",
                     "strada_imobil", "cod_strada_imobil", "nr_cadastral"):
            if not str(b.get(camp) or "").strip():
                er.append("Bun imobil %d: lipsă %s." % (i, camp))
        if _int(b.get("valoare_impozabila_imobil")) <= 0:
            er.append("Bun imobil %d: valoare_impozabila_imobil invalidă." % i)
        if not (0 < _cota(b.get("cota")) <= 100):
            er.append("Bun imobil %d: cota trebuie 0 < cota <= 100." % i)
        if _int(b.get("plafon_imobil")) <= 0:
            er.append("Bun imobil %d: plafon_imobil invalid." % i)
        if _int(b.get("valoare_impozabila_imobil")) <= _int(b.get("plafon_imobil")):
            er.append("Bun imobil %d: valoare_impozabila_imobil trebuie > plafon_imobil (d_rec=0)." % i)
    for i, b in enumerate(mob, 1):
        if _int(b.get("an_detinere")) <= 0:
            er.append("Bun mobil %d: an_detinere invalid." % i)
        if str(b.get("niv") or "").strip() == "":
            er.append("Bun mobil %d: lipsă niv." % i)
        if _int(b.get("valoare_impozabila_mobil")) <= 0:
            er.append("Bun mobil %d: valoare_impozabila_mobil invalidă." % i)
        if _int(b.get("plafon_mobil")) <= 0:
            er.append("Bun mobil %d: plafon_mobil invalid." % i)
        if _int(b.get("valoare_impozabila_mobil")) <= _int(b.get("plafon_mobil")):
            er.append("Bun mobil %d: valoare_impozabila_mobil trebuie > plafon_mobil (d_rec=0)." % i)
    return er


def build_xml(prof, an, luna, manual):
    imob = manual.get("imobile") or []
    mob = manual.get("mobile") or []
    tot = calcul_d216(manual)
    d_rec = _int(manual.get("d_rec"))

    def at(name, value):
        return name + "=" + _Q + value + _Q

    h = [
        at("luna", str(int(luna))),
        at("an", str(int(an))),
        at("d_rec", str(d_rec)),
        at("nume", _esc(manual.get("nume"), 75)),
        at("cif", _cif(manual.get("cif"))),
        at("domiciliuFiscal", _esc(manual.get("domiciliuFiscal"), 200)),
        at("impozit_imobile", str(tot["impozit_imobile"])),
        at("impozit_mobile", str(tot["impozit_mobile"])),
        at("totalPlata_A", str(tot["totalPlata_A"])),
        at("nume_intocmit", _esc(manual.get("nume_intocmit"), 75)),
        at("functia_intocmit", _esc(manual.get("functia_intocmit"), 75)),
    ]
    if str(manual.get("nume_imputernicit") or "").strip() and _cif(manual.get("cif_imputernicit")):
        h.append(at("nume_imputernicit", _esc(manual.get("nume_imputernicit"), 75)))
        h.append(at("cif_imputernicit", _cif(manual.get("cif_imputernicit"))))
    rows = []
    for b in imob:
        baza, imp = _calc_imobil(b)
        a = [
            at("judet_imobil", _esc(b.get("judet_imobil"), 60)),
            at("cod_judet_imobil", _cif(b.get("cod_judet_imobil"))),
            at("localitate_imobil", _esc(b.get("localitate_imobil"), 60)),
            at("cod_localitate_imobil", _cif(b.get("cod_localitate_imobil"))),
            at("strada_imobil", _esc(b.get("strada_imobil"), 100)),
            at("cod_strada_imobil", _cif(b.get("cod_strada_imobil"))),
            at("nr_cadastral", _esc(b.get("nr_cadastral"), 40)),
            at("valoare_impozabila_imobil", str(_int(b.get("valoare_impozabila_imobil")))),
            at("cota", _cota_str(_cota(b.get("cota")))),
            at("plafon_imobil", str(_int(b.get("plafon_imobil")))),
            at("baza_imobil", str(baza)),
            at("impozit_imobil", str(imp)),
        ]
        if str(b.get("nr_strada") or "").strip():
            a.insert(6, at("nr_strada", _esc(b.get("nr_strada"), 40)))
        rows.append("  <bun_imobil " + " ".join(a) + "/>")
    for b in mob:
        baza, imp = _calc_mobil(b)
        a = [
            at("an_detinere", str(_int(b.get("an_detinere")))),
            at("niv", str(_int(b.get("niv")))),
            at("valoare_impozabila_mobil", str(_int(b.get("valoare_impozabila_mobil")))),
            at("plafon_mobil", str(_int(b.get("plafon_mobil")))),
            at("baza_mobil", str(baza)),
            at("impozit_mobil", str(imp)),
        ]
        rows.append("  <bun_mobil " + " ".join(a) + "/>")
    body = ("\n" + "\n".join(rows)) if rows else ""
    return ('<?xml version=' + _Q + '1.0' + _Q + ' encoding=' + _Q + 'UTF-8' + _Q + '?>\n'
            '<D216 xmlns=' + _Q + NS + _Q + ' ' + " ".join(h) + '>' + body + '\n</D216>\n')


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(getattr(perioada, "an", 0) or manual.get("an") or 0)
    luna = int(getattr(perioada, "luna", 0) or manual.get("luna") or 12)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D216 nu se poate genera: " + " ".join(er))
    tot = calcul_d216(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat216(an=an, luna=luna, impozit_imobile=tot["impozit_imobile"],
                      impozit_mobile=tot["impozit_mobile"], total_plata_a=tot["totalPlata_A"],
                      nr_imobile=len(manual.get("imobile") or []),
                      nr_mobile=len(manual.get("mobile") or []))
    return xml, res
