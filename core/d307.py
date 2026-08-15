"""core/d307.py — D307: Declaratie privind sumele rezultate din ajustarea/corectia ajustarilor/regularizarea TVA.

Persoana impozabila declara sumele de TVA rezultate din ajustare, defalcate pe operatiuni (tip A/L/C).
Declaratie informativa (NU are cont bugetar / cod_bug). MANUALA - lista de operatiuni vine din input.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D307Validator.jar). _dateVersionTable o singura linie
("2016-01 J1.1.0 0") -> sub-pachet v0, DAR namespace XML :v1 (nepotrivire istorica). Radacina <declaratie307>.
  <declaratie307>: luna, an, d_rec, d_anulare, temei, nume_declar, prenume_declar, functie_declar, cif, den,
    adresa, telefon, fax, mail, tvaA, tvaL, tvaC, totalPlata_A.
  <operatie> (1-n): tip (A/L/C), codO, denO, tva.

SEMANTICA/REGULI din ACT (anaf_surse/structura_D307_2017_071117 + d307_20171205.xsd; OPANAF 793/2016;
CF art.270(7) transfer active, art.324(8),(9), art.316(11) anulare cod TVA):
  - tvaA=Σtva(tip=A); tvaL=Σtva(tip=L); tvaC=Σtva(tip=C); totalPlata_A=Σtva (suma de control).
  - tip A = transfer de active (codO=cedent); L = leasing, transfer active la finalul contractului (codO=finantator);
    C = anularea codului de TVA (codO=beneficiar).
  - temei ∈ {1,2} obligatoriu daca d_anulare=1 (1=art.105(6)a L.207/2015; 2=art.105(6)b).
  - tva poate fi <=0 (permis din J1.0.1). Atribut e `mail` (nu `email`). D307 NU are cod_bug.

Contract dXXX: pull/erori_generare/calcul_d307/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d307:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_TIP_VALIDE = {"A", "L", "C"}


def _i(x, camp="D307"):
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat307:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_operatiuni: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d307(manual):
    ops = manual.get("operatiuni") or []
    tva = {"A": 0, "L": 0, "C": 0}
    for o in ops:
        t = str(o.get("tip") or "").upper()
        if t in tva:
            tva[t] += _i(o.get("tva"))
    total = tva["A"] + tva["L"] + tva["C"]
    return {"tvaA": tva["A"], "tvaL": tva["L"], "tvaC": tva["C"], "totalPlata_A": total}


def pull(conn, schema, perioada):
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    adresa = " ".join(x for x in (r[2], r[3], r[4]) if x)
    return {"den": r[0], "cui": r[1], "adresa": adresa, "declarant_nume": r[5], "declarant_prenume": r[6],
            "declarant_functie": r[7], "telefon": r[8], "email": r[9]}


def erori_generare(prof, manual):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CUI persoana impozabila lipsa/invalid.")
    if not str(prof.get("den") or "").strip():
        er.append("LIPSA denumire.")
    if not str(prof.get("adresa") or "").strip():
        er.append("LIPSA adresa.")
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("LIPSA %s (declarant obligatoriu)." % c)
    if str(manual.get("d_anulare") or "0") == "1" and str(manual.get("temei") or "") not in ("1", "2"):
        er.append("d_anulare=1 cere temei (1=art.105(6)a / 2=art.105(6)b din L.207/2015).")
    ops = manual.get("operatiuni") or []
    if not ops:
        er.append("D307 cere cel putin o operatiune (operatiuni[]).")
    for i, o in enumerate(ops, 1):
        if str(o.get("tip") or "").upper() not in _TIP_VALIDE:
            er.append("Operatiune %d: tip %r invalid (A=transfer active / L=leasing / C=anulare cod TVA)." %
                      (i, o.get("tip")))
        if not str(o.get("den") or o.get("denO") or "").strip():
            er.append("Operatiune %d: lipsa denumire operator (denO)." % i)
        if not _cif(o.get("cod") or o.get("codO")):
            er.append("Operatiune %d: lipsa cod operator (codO)." % i)
    return er


def build_xml(prof, an, luna, manual, calc):
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('d_anulare="%d"' % int(manual.get("d_anulare") or 0))
    if str(manual.get("d_anulare") or "0") == "1":
        a.append('temei="%s"' % _esc(manual.get("temei")))
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie"), 50))
    a.append('cif="%s"' % _cif(prof.get("cui")))
    a.append('den="%s"' % _esc(prof.get("den"), 200))
    a.append('adresa="%s"' % _esc(prof.get("adresa"), 1000))
    if prof.get("telefon"):
        a.append('telefon="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('mail="%s"' % _esc(prof.get("email"), 200))
    a.append('tvaA="%d"' % calc["tvaA"])
    a.append('tvaL="%d"' % calc["tvaL"])
    a.append('tvaC="%d"' % calc["tvaC"])
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<declaratie307 xmlns="%s" %s>' % (NS, " ".join(a))]
    for o in manual.get("operatiuni") or []:
        oa = ['tip="%s"' % _esc(str(o.get("tip") or "").upper(), 1),
              'codO="%s"' % _cif(o.get("cod") or o.get("codO")),
              'denO="%s"' % _esc(o.get("den") or o.get("denO"), 200), 'tva="%d"' % _i(o.get("tva"))]
        linii.append('  <operatie %s/>' % " ".join(oa))
    linii.append('</declaratie307>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D307 nu se poate genera: " + " ".join(er))
    calc = calcul_d307(manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat307(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_operatiuni=len(manual.get("operatiuni") or []))
    return xml, res
