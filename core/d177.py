"""core/d177.py — D177: Cerere privind redirectionarea impozitului pe profit catre entitati nonprofit.

Platitorul de impozit pe profit redirectioneaza o suma din impozit catre entitati nonprofit / unitati de
cult (sponsorizare/mecenat, art.25 alin.(4) lit.i)/t) CF). Declaratie MANUALA - beneficiarii + sumele vin din
input. (Redirectionarea micro e ABROGATA din 2024, art.56(2^5) - modulul acopera cazul PROFIT, tipPlatitor=1.)

SURSA: validatorul oficial (D177Validator.jar, in vigoare v1/namespace v1) pentru STRUCTURA; actul in corpus
(OPANAF_3562_2024_D177 + structura_D177_2026, anaf_surse) pentru SEMANTICA/reguli. Nimic ghicit.

Nomenclator (structura_D177_2026):
  tipPlatitor = (1,2): 1=platitor impozit pe profit; 2=platitor impozit micro (abrogat 2024).
  tipB = (1,2,3,5) [4 nepermis]: 1=sponsorizare unitati de cult; 2=sponsorizare alte entitati nonprofit;
    3=UNICEF/organizatii internationale cu acord special; 5=... . cuiB=CUI pt tipB in (1,2,5), CNP pt (3,4).
  acord = (0,1) pe beneficiar. contractB obligatoriu daca tipB<5.
Reguli: sumaMax >= sumaAnt+sumaRest; sumaRest>0; Σ sumaB <= sumaRest; IBAN cu cifra de control;
  totalPlata_A (C15, suma de control) = 0 (D177 informativa; validator J2.0.3, pachet v1, an 2025).
  NOTA: formula veche round(sumaRest/100) era FALS-confirmata - validatorul vechi crapa tacit (fals-verde,
  vezi DECIZII 14.08); validatorul curent respinge orice totalPlata_A != 0 ('nu se incadreaza in interval').

Contract dXXX: pull/erori_generare/calcul_d177/build_xml/genereaza(conn, schema, perioada).
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d177:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
_TIPB_VALIDE = {"1", "2", "3", "5"}         # 4 nepermis (validator)
_TIPB_CUI = {"1", "2", "5"}                 # cuiB = CUI; restul (3) = CNP


def _i(x):
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, "D177").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _data(x):
    if isinstance(x, (date, datetime)):
        return "%02d.%02d.%04d" % (x.day, x.month, x.year)
    s = str(x or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        y, m, d = s.split("-")
        return "%s.%s.%s" % (d, m, y)
    return s


@dataclass
class Rezultat177:
    an: int
    luna: int
    suma_rest: int = 0
    total_plata_a: str = "0"
    nr_beneficiari: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d177(manual):
    """suma de control totalPlata_A = 0 (D177 e informativa; validator J2.0.3/v1). Formula veche
    round(sumaRest/100) era fals-confirmata pe validatorul vechi care crapa tacit (fals-verde)."""
    rest = _i(manual.get("suma_rest"))
    return {"suma_rest": rest, "totalPlata_A": "0"}


def pull(conn, schema, perioada):
    with conn.cursor() as cur:
        cur.execute("SELECT cui, nume, adresa, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"cui": r[0], "den": r[1], "adresa": r[2], "telefon": r[3], "email": r[4]}


def erori_generare(prof, manual):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CUI firma platitoare lipsa/invalid.")
    if not prof.get("den"):
        er.append("LIPSA denumire firma.")
    if int(manual.get("tip_platitor") or 1) not in (1, 2):
        er.append("tipPlatitor invalid (1=profit, 2=micro).")
    smax, sant, srest = _i(manual.get("suma_max")), _i(manual.get("suma_ant")), _i(manual.get("suma_rest"))
    if srest <= 0:
        er.append("sumaRest (suma de redirectionat) trebuie > 0.")
    if smax < sant + srest:
        er.append("sumaMax (%d) trebuie >= sumaAnt (%d) + sumaRest (%d)." % (smax, sant, srest))
    benef = manual.get("beneficiari") or []
    if not benef:
        er.append("D177 cere cel putin un beneficiar.")
    tot_b = 0
    for i, b in enumerate(benef, 1):
        tb = str(b.get("tip") or "")
        if tb not in _TIPB_VALIDE:
            er.append("Beneficiar %d: tipB %r invalid (1/2/3/5; 4 nepermis)." % (i, tb))
        if int(manual.get("tip_platitor") or 1) == 2 and tb == "3":
            er.append("Beneficiar %d: la tipPlatitor=2 (micro) tipB nu poate fi 3." % i)
        if not str(b.get("den") or "").strip():
            er.append("Beneficiar %d: lipsa denumire (denB)." % i)
        if not _cif(b.get("cui")):
            er.append("Beneficiar %d: lipsa cod fiscal beneficiar (cuiB)." % i)
        iban = str(b.get("iban") or "").replace(" ", "").upper()
        if not _IBAN_OK.match(iban):
            er.append("Beneficiar %d: IBAN invalid (RO + 22 caractere)." % i)
        if tb in ("1", "2", "3") and not str(b.get("contract") or "").strip():
            er.append("Beneficiar %d: contractB obligatoriu pentru tipB<5 (nr. si data sponsorizarii)." % i)
        if str(b.get("acord") or "") not in ("0", "1"):
            er.append("Beneficiar %d: acord obligatoriu (0/1)." % i)
        tot_b += _i(b.get("suma"))
    if tot_b > srest:
        er.append("Suma beneficiarilor (%d) depaseste sumaRest (%d)." % (tot_b, srest))
    return er


def build_xml(prof, an, luna, manual, calc):
    tp = int(manual.get("tip_platitor") or 1)
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('d_rec_notif="%d"' % int(manual.get("d_rec_notif") or 0))
    if manual.get("d_rec") and manual.get("index"):
        a.append('index="%s"' % _esc(manual.get("index"), 20))
    a.append('totalPlata_A="%s"' % calc["totalPlata_A"])
    a.append('cif="%s"' % _cif(prof.get("cui")))
    a.append('denC="%s"' % _esc(prof.get("den"), 250))
    if prof.get("adresa"):
        a.append('adresaC="%s"' % _esc(prof.get("adresa"), 500))
    if prof.get("telefon"):
        a.append('telC="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('emailC="%s"' % _esc(prof.get("email"), 250))
    a.append('sumaMax="%d"' % _i(manual.get("suma_max")))
    a.append('sumaAnt="%d"' % _i(manual.get("suma_ant")))
    a.append('sumaRest="%d"' % calc["suma_rest"])
    a.append('tipPlatitor="%d"' % tp)
    if tp == 1:
        a.append('dataInceput="%s"' % _data(manual.get("data_inceput")))
        a.append('dataSfarsit="%s"' % _data(manual.get("data_sfarsit")))
    linii = ['<D177 xmlns="%s" %s>' % (NS, " ".join(a))]
    for b in manual.get("beneficiari") or []:
        tb = str(b.get("tip") or "")
        iban = str(b.get("iban") or "").replace(" ", "").upper()
        ba = ['tipB="%s"' % tb, 'cuiB="%s"' % _cif(b.get("cui")),
              'denB="%s"' % _esc(b.get("den"), 250), 'ibanB="%s"' % _esc(iban, 24),
              'sumaB="%d"' % _i(b.get("suma")), 'acord="%s"' % str(b.get("acord") or "0")]
        if b.get("adresa"):
            ba.append('adresaB="%s"' % _esc(b.get("adresa"), 500))
        if b.get("contract"):
            ba.append('contractB="%s"' % _esc(b.get("contract"), 500))
        linii.append('  <beneficiar %s/>' % " ".join(ba))
    linii.append('</D177>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    manual.setdefault("tip_platitor", 1)
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D177 nu se poate genera: " + " ".join(er))
    calc = calcul_d177(manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat177(an=an, luna=luna, suma_rest=calc["suma_rest"], total_plata_a=calc["totalPlata_A"],
                      nr_beneficiari=len(manual.get("beneficiari") or []))
    return xml, res
