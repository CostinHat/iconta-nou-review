"""core/d311.py — D311: TVA datorata de persoane impozabile al caror cod de TVA a fost anulat.

Declaratie MANUALA: contabilul introduce bazele/TVA pe situatii (operatiuni de exceptie dupa
anularea codului de TVA - aplicatia nu are sursa automata). Structura din SURSA OFICIALA:
  anaf_surse/d311_20210129.xsd (namespace v1.02) + structura_D311_2021_290121.pdf.

Doua scheme mutual-exclusive (structura, sectiunea "Completari posibile"):
  IV (dupa ANULARE, art.316(11)): Data_A + (d_anul1 XOR d_anul2) + OB_11..OB_52; OB_51+OB_52>0.
  V  (dupa REINREGISTRARE, art.316(12)): Data_I + OB_61/OB_62; OB_61+OB_62>0.
Modulul implementeaza SCHEMA IV (cazul principal). Schema V (reinregistrare) e o limitare
documentata: XSD v1.02 marcheaza Data_A/d_anul1/d_anul2 use="required", in conflict cu regula de
excludere Data_I<->Data_A din structura; se activeaza cand se rezolva pe validatorul oficial.

Calcule (structura, rd.03/05/19): OB_31=OB_11+OB_21, OB_32=OB_12+OB_22, OB_51=OB_31+OB_41,
  OB_52=OB_32+OB_42; totalPlata_A = OB_51+OB_52+OB_61+OB_62 (suma de control).

Contract dXXX (verificator): pull / erori_generare / calcul_d311 / build_xml / genereaza(conn, schema, perioada).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'TVA datorată de persoane impozabile al căror cod de TVA a fost anulat'
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d311:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
# campurile de intrare MANUALA (bazele/TVA); restul (OB_31/32/51/52) se CALCULEAZA.
_INTRARE = ("OB_11", "OB_12", "OB_21", "OB_22", "OB_41", "OB_42", "OB_61", "OB_62")


def _i(x):
    """Suma in bani -> intreg (rotunjire canonica, ca d300). Gol/None -> 0."""
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, "D311").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    """CUI conform CifSType ([1-9]\\d{...}): cifre, fara RO/spatii/zerouri initiale."""
    return _NEDIGIT.sub("", str(x or "")).lstrip("0")


def _esc(s, lim=None):
    """Valoare de atribut XML: escape + truncare la maxLength XSD."""
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _data(x):
    """DateSType ZZ.LL.AAAA (DD.MM.YYYY) - format XML ANAF, NU display uman (nu trece prin data_ro).
    Accepta date/datetime sau 'YYYY-MM-DD'/'DD.MM.YYYY'."""
    if isinstance(x, (date, datetime)):
        return "%02d.%02d.%04d" % (x.day, x.month, x.year)
    s = str(x or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        y, m, d = s.split("-")
        return "%s.%s.%s" % (d, m, y)
    return s


@dataclass
class Rezultat311:
    an: int
    luna: int
    schema: int            # 1 = sectiunea IV (anulare); 2 = sectiunea V (reinregistrare)
    ob: dict = field(default_factory=dict)
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d311(manual):
    """OB calculate + suma de control, din intrarile manuale. Sursa: structura rd.03/05/19."""
    ob = {k: _i(manual.get(k)) for k in _INTRARE}
    ob["OB_31"] = ob["OB_11"] + ob["OB_21"]
    ob["OB_32"] = ob["OB_12"] + ob["OB_22"]
    ob["OB_51"] = ob["OB_31"] + ob["OB_41"]
    ob["OB_52"] = ob["OB_32"] + ob["OB_42"]
    total = ob["OB_51"] + ob["OB_52"] + ob["OB_61"] + ob["OB_62"]
    return ob, total


def pull(conn, schema, perioada):
    """Header firmei (D311 e MANUALA - nu se trag tranzactii; sumele vin din `manual`)."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT nume, nume, cui, adresa, declarant_nume, declarant_prenume, "
            "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"den": r[0], "nume": r[1], "cui": r[2], "adresa": r[3],
            "declarant_nume": r[4], "declarant_prenume": r[5], "declarant_functie": r[6],
            "telefon": r[7], "email": r[8]}


def erori_generare(prof, manual):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CUI firma lipsă/invalid (D311 cere cod fiscal valid).")
    if not (prof.get("den") or prof.get("nume")):
        er.append("LIPSĂ denumire firma.")
    # [mesaj_contabil] Regula 14.4 + GARDA campaniei: erorile urca la UTILIZATOR (ValueError -> 422 ->
    # e.mesaj in formular). Textul e in limba contabilului - ce lipseste si unde se completeaza -, NU
    # numele intern al campului (Data_A/d_anul1/OB_51). Numele XSD raman doar in cod/comentariu/test.
    _ET_DECL = {"declarant_nume": "numele declarantului", "declarant_prenume": "prenumele declarantului",
                "declarant_functie": "funcția declarantului"}
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("Lipsește %s (obligatoriu la D311) — completează la datele firmei." % _ET_DECL[c])
    sch = int(manual.get("schema") or 1)
    if sch != 1:
        er.append("D311 acoperă deocamdată doar situația de după anularea codului de TVA. "
                  "Cazul reînregistrării în scopuri de TVA nu e încă disponibil (vezi ajutorul declarației).")
        return er
    if not manual.get("Data_A"):
        er.append("Completează data anulării înregistrării în scopuri de TVA (obligatorie).")
    a1, a2 = int(manual.get("d_anul1") or 0), int(manual.get("d_anul2") or 0)
    if a1 + a2 != 1:
        er.append("Bifează motivul anulării codului de TVA: din oficiu, ori la cerere "
                  "(firmă care aplica TVA la încasare). Exact unul dintre cele două.")
    ob, _ = calcul_d311(manual)
    if ob["OB_51"] + ob["OB_52"] <= 0:
        er.append("Nu ai introdus nicio sumă de plată (bază sau TVA pe operațiunile din perioada "
                  "în care firma nu a avut cod valabil de TVA). D311 nu se depune pe zero.")
    return er


def build_xml(prof, an, luna, manual, ob, total):
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('d_anulare="%d"' % int(manual.get("d_anulare") or 0))
    if manual.get("temei"):
        a.append('temei="%d"' % int(manual["temei"]))
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie"), 50))
    a.append('cui="%s"' % _cif(prof.get("cui")))
    a.append('den="%s"' % _esc(prof.get("den") or prof.get("nume"), 200))
    a.append('adresa="%s"' % _esc(prof.get("adresa"), 1000))
    if prof.get("telefon"):
        a.append('telefon="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('mail="%s"' % _esc(prof.get("email"), 200))
    a.append('Data_A="%s"' % _data(manual["Data_A"]))
    a.append('d_anul1="%d"' % int(manual.get("d_anul1") or 0))
    a.append('d_anul2="%d"' % int(manual.get("d_anul2") or 0))
    a.append('totalPlata_A="%d"' % int(total))
    # Sectiunea IV: OB_11..OB_52 (OB_61/OB_62 = sectiunea V, omise in schema IV)
    for k in ("OB_11", "OB_12", "OB_21", "OB_22", "OB_31", "OB_32", "OB_41", "OB_42", "OB_51", "OB_52"):
        a.append('%s="%d"' % (k, ob[k]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie311 xmlns="%s" %s/>\n' % (NS, " ".join(a)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    manual.setdefault("schema", 1)
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D311 nu se poate genera: " + " ".join(er))
    ob, total = calcul_d311(manual)
    xml = build_xml(prof, an, luna, manual, ob, total)
    res = Rezultat311(an=an, luna=luna, schema=1, ob=ob, total_plata_a=total)
    return xml, res
