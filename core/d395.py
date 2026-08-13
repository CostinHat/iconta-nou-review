"""core/d395.py - D395: Declaratie informativa privind trimiterile postale contra ramburs.

Depusa LUNAR de furnizorii de servicii postale. Raporteaza, pentru fiecare trimitere postala
livrata contra ramburs, expeditorul, destinatarul, documentul, valoarea rambursului si modul
in care suma rambursata a fost pusa la dispozitia expeditorului (virament in IBAN sau ridicata
in numerar de o persoana receptionata).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D395Validator.jar, arbitrat prin DUKIntegrator).
Namespace declaratie:v1, pachet d395validator/v1. Numele si obligativitatea campurilor au fost
CITITE din bytecode-ul claselor D395 / Lista / Lista2 si PROBATE camp cu camp pe DUK pana la
"Validare fara erori":
  - Antet (D395): an, luna, d_rec, totalPlata_A, cif, den, adresa, telefon, mail, cifR, denR,
    adresaR, telefonR, mailR, declarant, functie. TOATE obligatorii (probat: DUK cere fiecare;
    exista bloc reprezentant cifR..mailR mandatoriu, nu doar declarantul).
  - lista (repetabil, >=1): nr_doc (unic - R.Nrdoc), data_doc (dd.mm.yyyy, <= perioada raportare
    R21), val_ramb, den_expeditor, den_destinatar, jud_preluare (cod judet 1..52), exact UNA din
    adresa_preluare / adresa_oficiu (R27/R27.1) impreuna cu jud_preluare (R27.2). Identitatea
    expeditorului: cif_expeditor (CUI RO) SAU perechea cif_expeditor_str + cod_tara_str (extern,
    cod tara NUMERIC din nomenclator) - cele doua cai se exclud (R35/R36). Modul de plata:
    mod=1 <=> iban completat (R29, IBAN valid), mod=2 <=> den_receptionat completat (R30).
  - lista2 (OPTIONAL, sumar): daca e prezenta, nr_colete + nr_colete_info + nr_colete_taxa sunt
    obligatorii (rec_s1/rectif_s1 - interne, neexpuse).

Reguli PROBATE pe DUK: totalPlata_A NU e verificat ca suma de control (DUK lenient) - il calculam
totusi ca suma val_ramb (semantica naturala "total plata ramburs"). data_doc dd.mm.yyyy acceptat.
jud_preluare validat contra listei de judete (40/403 respinse; 1..52 acceptate). cod_tara_str e
INTREG (nu cod alfabetic). Sectiunile in XML sunt lowercase: <lista>, <lista2>.

Valorile vin din `manual` (furnizorul de servicii postale isi tine propriile evidente - aplicatia
nu are registru de trimiteri postale). NU se fabrica nimic din acte. d_rec="0" implicit.
NEPOPULAT deliberat: rec_s/rec_s1/rectif_s1 (numerotare interna a validatorului, neceruta in XML).

Contract dXXX: NS, _cif/_esc, calcul_d395(manual), pull (return {}), erori_generare, build_xml,
genereaza(conn, schema, perioada, manual=None).
"""
from dataclasses import dataclass, field
import re
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d395:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
_DATA_OK = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
_MAIL_OK = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _num(x):
    """Valoare monetara: virgula->punct, fara zecimale inutile (1000 / 1000.5)."""
    s = str(x if x is not None else "").replace(",", ".").strip()
    try:
        v = float(s)
    except ValueError:
        return "0"
    return ("%.2f" % v).rstrip("0").rstrip(".")


def _mod_si_cheie(t):
    """Deduce modul de punere la dispozitie a rambursului dintr-o trimitere.
    iban -> (mod=1, 'iban'); den_receptionat -> (mod=2, 'den_receptionat')."""
    iban = str(t.get("iban") or "").replace(" ", "").upper()
    rec = str(t.get("den_receptionat") or "").strip()
    if iban:
        return 1, iban, ""
    if rec:
        return 2, "", rec
    return 0, "", ""


def calcul_d395(manual):
    """Suma de control din antet: totalPlata_A = suma val_ramb din trimiteri (int, ANAF nu
    o cross-verifica dar e valoarea informativa naturala). Intoarce si sumarul lista2 daca e dat."""
    total = 0.0
    for t in (manual.get("trimiteri") or []):
        try:
            total += float(str(t.get("val_ramb") or "0").replace(",", "."))
        except ValueError:
            pass
    out = {"totalPlata_A": int(Decimal(str(total)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))}
    l2 = manual.get("lista2")
    if l2:
        out["lista2"] = {
            "nr_colete": _cif(l2.get("nr_colete")),
            "nr_colete_info": _cif(l2.get("nr_colete_info")),
            "nr_colete_taxa": _cif(l2.get("nr_colete_taxa")),
        }
    return out


def pull(conn, schema, perioada):
    """D395 e MANUALA: furnizorul postal isi tine propriile evidente de trimiteri contra ramburs;
    aplicatia nu are un registru al trimiterilor postale. Contractul cere `pull`."""
    return {}


def _err_trimitere(i, t):
    er = []
    p = "trimitere #%d" % i
    if not _cif(t.get("nr_doc")) and not str(t.get("nr_doc") or "").strip():
        er.append("%s: lipsa nr_doc." % p)
    d = str(t.get("data_doc") or "").strip()
    if not _DATA_OK.match(d):
        er.append("%s: data_doc invalid ('%s') - astept zz.ll.aaaa." % (p, d))
    if _num(t.get("val_ramb")) in ("", "0"):
        er.append("%s: val_ramb lipsa sau 0." % p)
    if not str(t.get("den_expeditor") or "").strip():
        er.append("%s: lipsa den_expeditor." % p)
    if not str(t.get("den_destinatar") or "").strip():
        er.append("%s: lipsa den_destinatar." % p)
    # expeditor: cif_expeditor (RO) XOR cif_expeditor_str + cod_tara_str (extern)
    cif_e = _cif(t.get("cif_expeditor"))
    cif_str = str(t.get("cif_expeditor_str") or "").strip()
    tara = _cif(t.get("cod_tara_str"))
    if cif_e and cif_str:
        er.append("%s: cif_expeditor si cif_expeditor_str nu pot fi simultan completate (R35)." % p)
    if not cif_e and not cif_str:
        er.append("%s: lipsa identificare expeditor (cif_expeditor sau cif_expeditor_str)." % p)
    if bool(cif_str) != bool(tara):
        er.append("%s: cif_expeditor_str si cod_tara_str (numeric) trebuie ambele date sau ambele goale (R36)." % p)
    # adresa preluare/oficiu: exact una + judet
    ap = str(t.get("adresa_preluare") or "").strip()
    ao = str(t.get("adresa_oficiu") or "").strip()
    if ap and ao:
        er.append("%s: adresa_preluare si adresa_oficiu nu pot fi simultan completate (R27)." % p)
    if not ap and not ao:
        er.append("%s: lipsa adresa preluare/oficiu (exact una obligatorie) (R27.1)." % p)
    if not _cif(t.get("jud_preluare")):
        er.append("%s: lipsa jud_preluare (cod judet, obligatoriu cu adresa) (R27.2)." % p)
    # mod: iban XOR den_receptionat
    iban = str(t.get("iban") or "").replace(" ", "").upper()
    rec = str(t.get("den_receptionat") or "").strip()
    if iban and rec:
        er.append("%s: iban si den_receptionat se exclud (mod=1 vs mod=2)." % p)
    if not iban and not rec:
        er.append("%s: lipsa mod plata ramburs - da 'iban' (mod 1) sau 'den_receptionat' (mod 2)." % p)
    if iban and not _IBAN_OK.match(iban):
        er.append("%s: IBAN invalid ('%s')." % (p, iban))
    return er


def erori_generare(prof, manual):
    er = []
    # antet - declarant (furnizor postal)
    for k, et in (("cif", "CIF declarant"), ("den", "denumire declarant"),
                  ("adresa", "adresa declarant"), ("telefon", "telefon declarant"),
                  ("mail", "email declarant")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsa %s (%s)." % (et, k))
    # antet - reprezentant (obligatoriu in validator)
    for k, et in (("cifR", "CIF reprezentant"), ("denR", "denumire reprezentant"),
                  ("adresaR", "adresa reprezentant"), ("telefonR", "telefon reprezentant"),
                  ("mailR", "email reprezentant")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsa %s (%s)." % (et, k))
    for k, et in (("declarant", "nume semnatar"), ("functie", "functie semnatar")):
        if not str(manual.get(k) or "").strip():
            er.append("Lipsa %s (%s)." % (et, k))
    if manual.get("mail") and not _MAIL_OK.match(str(manual.get("mail")).strip()):
        er.append("Email declarant (mail) invalid.")
    if manual.get("mailR") and not _MAIL_OK.match(str(manual.get("mailR")).strip()):
        er.append("Email reprezentant (mailR) invalid.")
    if not (2 <= len(_cif(manual.get("cif"))) <= 10):
        er.append("CIF declarant (cif) invalid.")
    if not (2 <= len(_cif(manual.get("cifR"))) <= 10):
        er.append("CIF reprezentant (cifR) invalid.")
    # trimiteri
    trim = manual.get("trimiteri") or []
    if not trim:
        er.append("Lipsa trimiteri (cel putin o trimitere postala contra ramburs).")
    vazute = set()
    for i, t in enumerate(trim, 1):
        er.extend(_err_trimitere(i, t))
        nd = str(t.get("nr_doc") or "").strip()
        if nd and nd in vazute:
            er.append("trimitere #%d: nr_doc '%s' duplicat (trebuie unic - R.Nrdoc)." % (i, nd))
        vazute.add(nd)
    # lista2 optional: daca e prezent, cele trei numere sunt obligatorii
    l2 = manual.get("lista2")
    if l2:
        for k in ("nr_colete", "nr_colete_info", "nr_colete_taxa"):
            if not _cif(l2.get(k)):
                er.append("lista2: lipsa %s (obligatoriu cand sectiunea sumar e prezenta)." % k)
    return er


def _attr(name, val):
    return ' %s="%s"' % (name, val)


def build_xml(prof, an, luna, manual):
    calc = calcul_d395(manual)
    h = []
    h.append(_attr("an", int(an)))
    h.append(_attr("luna", int(luna)))
    h.append(_attr("d_rec", _esc(manual.get("d_rec")) or "0"))
    h.append(_attr("totalPlata_A", calc["totalPlata_A"]))
    h.append(_attr("cif", _cif(manual.get("cif"))))
    h.append(_attr("den", _esc(manual.get("den"), 200)))
    h.append(_attr("adresa", _esc(manual.get("adresa"), 500)))
    h.append(_attr("telefon", _esc(manual.get("telefon"), 30)))
    h.append(_attr("mail", _esc(manual.get("mail"), 250)))
    h.append(_attr("cifR", _cif(manual.get("cifR"))))
    h.append(_attr("denR", _esc(manual.get("denR"), 200)))
    h.append(_attr("adresaR", _esc(manual.get("adresaR"), 500)))
    h.append(_attr("telefonR", _esc(manual.get("telefonR"), 30)))
    h.append(_attr("mailR", _esc(manual.get("mailR"), 250)))
    h.append(_attr("declarant", _esc(manual.get("declarant"), 200)))
    h.append(_attr("functie", _esc(manual.get("functie"), 200)))

    linii = []
    for t in (manual.get("trimiteri") or []):
        mod, iban, rec = _mod_si_cheie(t)
        a = []
        a.append(_attr("nr_doc", _esc(t.get("nr_doc"), 50)))
        a.append(_attr("data_doc", _esc(t.get("data_doc"), 10)))
        a.append(_attr("val_ramb", _num(t.get("val_ramb"))))
        a.append(_attr("den_expeditor", _esc(t.get("den_expeditor"), 200)))
        cif_e = _cif(t.get("cif_expeditor"))
        if cif_e:
            a.append(_attr("cif_expeditor", cif_e))
        else:
            a.append(_attr("cif_expeditor_str", _esc(t.get("cif_expeditor_str"), 50)))
            a.append(_attr("cod_tara_str", _cif(t.get("cod_tara_str"))))
        a.append(_attr("jud_preluare", _cif(t.get("jud_preluare"))))
        if str(t.get("adresa_preluare") or "").strip():
            a.append(_attr("adresa_preluare", _esc(t.get("adresa_preluare"), 500)))
        else:
            a.append(_attr("adresa_oficiu", _esc(t.get("adresa_oficiu"), 500)))
        a.append(_attr("mod", mod))
        if mod == 1:
            a.append(_attr("iban", iban))
        elif mod == 2:
            a.append(_attr("den_receptionat", _esc(rec, 200)))
        a.append(_attr("den_destinatar", _esc(t.get("den_destinatar"), 200)))
        linii.append("  <lista%s/>" % "".join(a))

    l2 = calc.get("lista2")
    if l2:
        linii.append('  <lista2 nr_colete="%s" nr_colete_info="%s" nr_colete_taxa="%s"/>'
                     % (l2["nr_colete"], l2["nr_colete_info"], l2["nr_colete_taxa"]))

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<D395 xmlns="%s"%s>\n%s\n</D395>\n'
            % (NS, "".join(h), "\n".join(linii)))


@dataclass
class Rezultat395:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_trimiteri: int = 0
    avertismente: list = field(default_factory=list)


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D395 nu se poate genera: " + " ".join(er))
    calc = calcul_d395(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat395(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_trimiteri=len(manual.get("trimiteri") or []))
    return xml, res
