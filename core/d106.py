"""core/d106.py — D106: Declaratie informativa privind dividendele cuvenite actionarilor.

Se completeaza si se depune de societatile nationale, companiile nationale si societatile la care statul
este actionar unic, majoritar sau detine controlul, in cazul in care pentru anul de raportare au fost
repartizate dividende actionarilor (OG 64/2001, aprobata prin Legea 769/2001). Periodicitate ANUALA -
pana la data de 25 a lunii urmatoare aprobarii repartitiei profitului. Declaratie MANUALA: aplicatia nu
are registru al actionarilor de stat - lista vine din `manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D106Validator.jar, arbitrul peste anexe). Radacina si campurile
au fost CITITE din bytecode (pachet d106validator/v0; namespace declaratie:v1) si PROBATE pe validator:
  - Radacina: <declaratie106> (clasa Declaratie106; DEC_NAMESPACE mfp:anaf:dgti:d106:declaratie:v1).
  - Declaratie106: d_rec, luna, an, cif (nextAttributeAsCui), den, adresa, telefon, fax, email,
    nume_declar, prenume_declar, functie_declar, totalPlata_A.
  - <dividende> (1-n, clasa Dividende): cifAct (nextAttributeAsCif), denAct, cotaAct, divd.
Reguli citite din validator (probate):
  - actionari unici: cifAct nu se poate repeta ("aparitie multipla cif").
  - cotaAct <= 100 ("cotaAct (@0@) > 100").
  - suma de control: totalPlata_A (= _sumaControl) trebuie sa fie egal cu suma dividendelor declarate
    ("Suma dividendelor (@0@) este diferita de suma de control (@1@)"). totalPlata_A = suma(divd).

SEMANTICA/REGULI din ACT (anaf_surse/opanaf_1292_2014_d106_instructiuni.txt, OPANAF 1292/2014, cod formular
14.13.01.01/d.d.):
  - Sectiunea I "Date de identificare a operatorului economic": cif, denumire, adresa domiciliului fiscal.
  - Sectiunea II "Date privind dividendele cuvenite actionarilor", pe fiecare actionar:
      Denumire (denAct) = autoritatea publica centrala, in calitate de actionar;
      Cod de identificare fiscala (cifAct) = CIF-ul actionarului;
      Cota de participare la capitalul social (cotaAct);
      Dividende distribuite (divd) = suma dividendelor distribuite.
D106 NU declara impozit pe linie (nu exista camp de impozit in <dividende>) - modulul NU fabrica nicio cota
de impozit; declara doar dividendul distribuit per actionar. NEPOPULAT deliberat (optional, fara semantica
determinata din act pentru cazul principal): telefon, fax, email.

Contract dXXX: pull/erori_generare/calcul_d106/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație informativă privind dividendele cuvenite acționarilor'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d106:declaratie:v1"
_NEDIGIT = re.compile(r"\D")


def _i(x):
    """Suma in bani -> intreg cu rotunjire aritmetica (half-up), cum cere ANAF."""
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, "D106").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _cota(x):
    """Cota de participare la capitalul social; regula validator cotaAct <= 100. Format zecimal, fara zerouri inutile."""
    try:
        c = float(str(x).replace(",", ".")) if x not in (None, "") else 0.0
    except ValueError:
        c = 0.0
    if c > 100:
        c = 100.0
    return ("%.4f" % c).rstrip("0").rstrip(".") or "0"


@dataclass
class Rezultat106:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_actionari: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d106(manual):
    """Suma de control: totalPlata_A = suma dividendelor distribuite (suma(divd))."""
    total = sum(_i(a.get("dividend")) for a in (manual.get("actionari") or []))
    return {"totalPlata_A": total}


def pull(conn, schema, perioada):
    """Header operatorului economic. Actionarii vin din `manual` (nu exista registru al actionarilor de stat)."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"den": r[0], "cui": r[1], "adresa": r[2], "declarant_nume": r[3],
            "declarant_prenume": r[4], "declarant_functie": r[5], "telefon": r[6], "email": r[7]}


def erori_generare(prof, manual):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CIF operator economic lipsă/invalid.")
    if not prof.get("den"):
        er.append("LIPSĂ denumire operator economic.")
    if not str(prof.get("adresa") or "").strip():
        er.append("LIPSĂ adresa domiciliu fiscal.")
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("LIPSĂ %s (declarant obligatoriu)." % c)
    actionari = manual.get("actionari") or []
    if not actionari:
        er.append("D106 cere cel puțin un actionar (actionari[]).")
    vazute = set()
    for i, a in enumerate(actionari, 1):
        cif = _cif(a.get("cif"))
        if not (2 <= len(cif) <= 13):
            er.append("Actionar %d: CIF (cif) invalid." % i)
        elif cif in vazute:
            er.append("Actionar %d: CIF %s repetat (actionarii trebuie să fie unici)." % (i, cif))
        else:
            vazute.add(cif)
        if not str(a.get("denumire") or "").strip():
            er.append("Actionar %d: lipsă denumire (denAct)." % i)
        try:
            cota = float(str(a.get("cota")).replace(",", ".")) if a.get("cota") not in (None, "") else 0.0
        except ValueError:
            cota = -1
        if not (0 <= cota <= 100):
            er.append("Actionar %d: cota de participare (cota) trebuie în 0..100." % i)
        if _i(a.get("dividend")) <= 0:
            er.append("Actionar %d: dividend distribuit (dividend) trebuie > 0." % i)
    return er


def build_xml(prof, an, luna, manual, calc):
    a = []
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie"), 75))
    a.append('cif="%s"' % _cif(prof.get("cui")))
    a.append('den="%s"' % _esc(prof.get("den"), 200))
    a.append('adresa="%s"' % _esc(prof.get("adresa"), 200))
    if prof.get("telefon"):
        a.append('telefon="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('email="%s"' % _esc(prof.get("email"), 200))
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<declaratie106 xmlns="%s" %s>' % (NS, " ".join(a))]
    for act in manual.get("actionari") or []:
        da = ['cifAct="%s"' % _cif(act.get("cif")),
              'denAct="%s"' % _esc(act.get("denumire"), 200),
              'cotaAct="%s"' % _cota(act.get("cota")),
              'divd="%d"' % _i(act.get("dividend"))]
        linii.append('  <dividende %s/>' % " ".join(da))
    linii.append('</declaratie106>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D106 nu se poate genera: " + " ".join(er))
    calc = calcul_d106(manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat106(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_actionari=len(manual.get("actionari") or []))
    return xml, res
