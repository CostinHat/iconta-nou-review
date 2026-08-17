"""core/d221.py — D221: Declaratie privind veniturile din activitati agricole impuse pe baza de norme de venit.

Persoana fizica (individual) sau asociere fara personalitate juridica declara activitatile agricole (pe judet/
localitate, cu produse: cod produs + suprafata/nr. capete). NU contine sume de impozit (totalPlata_A=0 mereu);
ANAF aplica normele de venit intern. Declaratie MANUALA.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D221Validator.jar). _dateVersionTable o singura linie
("2016-12 J1.0.1 0") -> sub-pachet v0, DAR namespace XML :v1 (confirmata de XSD). Radacina <declaratie221>.
  <declaratie221>: luna, an, d_rec, nume_declar, prenume_declar, functie_declar, totalPlata_A, aj_soc, nume_a,
    cif, adresa_a, telefon_a, fax_a, email_a, forma_org, nr_asoc, nr_contr, data_contr, nr_zile_scut,
    den_r, cif_r, adresa_r, telefon_r, fax_r, email_r.
  <activitati> (1-n; ORDINEA in XSD: activitati INAINTE de asociati): judet, localitate, optiune.
    -> <produse> (1-20): codp, prod1.
  <asociati> (0 daca forma_org=1; 2-n daca forma_org=2): nume_d, cif_d, dom_d, cota_d, nr_zile_d.

SEMANTICA/REGULI din ACT (anaf_surse/structura_D221_2017_050118 + d221_20170303.xsd; OPANAF 3622/2015;
CF art.103-106 venituri agricole pe norme de venit):
  - luna = 12 (fix); an>=2016. totalPlata_A = 0 (mereu). aj_soc = 0 (obligatoriu pt an>=2017).
  - forma_org 1=Individual (fara asociati; nr_asoc=0; nr_contr/data_contr null), 2=Asociere f.PJ (asociati 2-n;
    nr_asoc=nr asociati; nr_contr/data_contr obligatorii).
  - suma(cota_d)=100; per asociat 0<cota_d<100; cif_d unic (CNP). localitate unica intre activitati; codp unic
    in cadrul unei activitati. prod1>=0.
  - bloc imputernicit (den_r/cif_r/adresa_r) all-or-nothing. D221 NU are cod_bug.

Contract dXXX: pull/erori_generare/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d221:declaratie:v1"
_NEDIGIT = re.compile(r"\D")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cota(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _num2(x):
    d = Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return ("%d" % d) if d == d.to_integral_value() else ("%s" % d)


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat221:
    an: int
    nr_activitati: int = 0
    nr_asociati: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d221(manual):
    """D221 nu are sume de impozit (totalPlata_A=0 mereu; ANAF aplica normele intern). Calculul se rezuma la
    numararea activitatilor/asociatilor si suma de control fixa 0 (contract uniform dXXX)."""
    return {"nr_activitati": len(manual.get("activitati") or []),
            "nr_asociati": len(manual.get("asociati") or []),
            "totalPlata_A": 0}


def pull(conn, schema, perioada):
    with conn.cursor() as cur:
        cur.execute("SELECT declarant_nume, declarant_prenume, declarant_functie FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    return {"declarant_nume": r[0], "declarant_prenume": r[1], "declarant_functie": r[2]}


def _declarant(prof, manual):
    return {"nume_declar": manual.get("nume_declar") or prof.get("declarant_nume"),
            "prenume_declar": manual.get("prenume_declar") or prof.get("declarant_prenume"),
            "functie_declar": manual.get("functie_declar") or prof.get("declarant_functie") or "TITULAR"}


def erori_generare(prof, an, manual):
    er = []
    d = _declarant(prof, manual)
    for c in ("nume_declar", "prenume_declar"):
        if not str(d.get(c) or "").strip():
            er.append("LIPSĂ %s (declarant/titular obligatoriu)." % c)
    if not _cif(manual.get("cif")):
        er.append("D221 cere cif (CNP/NIF contribuabil).")
    if not str(manual.get("nume_a") or "").strip():
        er.append("LIPSĂ nume_a (nume+prenume / denumire contribuabil sau asociere).")
    if not str(manual.get("adresa_a") or "").strip():
        er.append("LIPSĂ adresa_a.")
    forma = str(manual.get("forma_org") or "")
    if forma not in {"1", "2"}:
        er.append("forma_org invalid (1=individual / 2=asociere fără PJ).")
    activitati = manual.get("activitati") or []
    if not activitati:
        er.append("D221 cere cel puțin o activitate (activități[]).")
    locuri = []
    for i, a in enumerate(activitati, 1):
        if not str(a.get("judet") or "").strip():
            er.append("Activitate %d: lipsă județ." % i)
        loc = str(a.get("localitate") or "").strip()
        if not loc:
            er.append("Activitate %d: lipsă localitate." % i)
        else:
            locuri.append(loc)
        if str(a.get("optiune") or "0") not in {"0", "1"}:
            er.append("Activitate %d: optiune invalidă (0/1)." % i)
        produse = a.get("produse") or []
        if not produse:
            er.append("Activitate %d: cere cel puțin un produs (produse[])." % i)
        coduri = []
        for j, p in enumerate(produse, 1):
            cp = str(p.get("codp") or "").strip()
            if not cp:
                er.append("Activitate %d produs %d: lipsă codp." % (i, j))
            else:
                coduri.append(cp)
            try:
                if Decimal(str(p.get("prod1") or 0)) < 0:
                    er.append("Activitate %d produs %d: prod1 trebuie >= 0." % (i, j))
            except Exception:
                er.append("Activitate %d produs %d: prod1 invalid." % (i, j))
        if len(coduri) != len(set(coduri)):
            er.append("Activitate %d: codp duplicat (unic în cadrul unei activități)." % i)
    if len(locuri) != len(set(locuri)):
        er.append("localitate duplicata intre activități (trebuie unica).")
    asociati = manual.get("asociati") or []
    if forma == "1" and asociati:
        er.append("forma_org=1 (individual): nu se completează asociati.")
    if forma == "2":
        if len(asociati) < 2:
            er.append("forma_org=2 (asociere): cere cel puțin 2 asociati.")
        if not str(manual.get("nr_contr") or "").strip() or not str(manual.get("data_contr") or "").strip():
            er.append("forma_org=2: nr_contr și data_contr obligatorii.")
    cifuri, suma = [], Decimal(0)
    for i, a in enumerate(asociati, 1):
        if not str(a.get("nume_d") or "").strip():
            er.append("Asociat %d: lipsă nume_d." % i)
        cf = _cif(a.get("cif_d"))
        if len(cf) != 13:
            er.append("Asociat %d: cif_d trebuie CNP 13 cifre." % i)
        else:
            cifuri.append(cf)
        if not str(a.get("dom_d") or "").strip():
            er.append("Asociat %d: lipsă dom_d." % i)
        try:
            cota = _cota(a.get("cota_d") or 0)
        except Exception:
            cota = Decimal(0)
        suma += cota
        if not (Decimal(0) < cota < Decimal(100)):
            er.append("Asociat %d: cota_d %s invalida (0<cota_d<100)." % (i, a.get("cota_d")))
    if asociati and suma != Decimal(100):
        er.append("Suma cotelor de distribuire (%s) trebuie să fie 100." % suma)
    if len(cifuri) != len(set(cifuri)):
        er.append("Asociații au cif_d duplicat.")
    # bloc imputernicit all-or-nothing
    imp = [str((manual.get("imputernicit") or {}).get(k) or "").strip() for k in ("den_r", "cif_r", "adresa_r")]
    if any(imp) and not all(imp):
        er.append("Imputernicit: den_r, cif_r și adresa_r trebuie completate impreuna (all-or-nothing).")
    return er


def build_xml(prof, an, manual):
    d = _declarant(prof, manual)
    forma = str(manual.get("forma_org") or "")
    asociati = manual.get("asociati") or []
    a = []
    a.append('luna="12"')
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('nume_declar="%s"' % _esc(d.get("nume_declar"), 75))
    a.append('prenume_declar="%s"' % _esc(d.get("prenume_declar"), 75))
    a.append('functie_declar="%s"' % _esc(d.get("functie_declar"), 50))
    a.append('totalPlata_A="0"')
    a.append('aj_soc="0"')
    a.append('nume_a="%s"' % _esc(manual.get("nume_a"), 75))
    a.append('cif="%s"' % _cif(manual.get("cif")))
    a.append('adresa_a="%s"' % _esc(manual.get("adresa_a"), 200))
    for k, xa in (("telefon_a", "telefon_a"), ("fax_a", "fax_a"), ("email_a", "email_a")):
        if str(manual.get(k) or "").strip():
            a.append('%s="%s"' % (xa, _esc(manual.get(k), 200 if k == "email_a" else 15)))
    a.append('forma_org="%s"' % forma)
    if forma == "2":
        a.append('nr_asoc="%d"' % len(asociati))
        a.append('nr_contr="%s"' % _esc(manual.get("nr_contr"), 15))
        a.append('data_contr="%s"' % _esc(manual.get("data_contr"), 10))
    if str(manual.get("nr_zile_scut") or "").strip():
        a.append('nr_zile_scut="%s"' % _esc(manual.get("nr_zile_scut")))
    imp = manual.get("imputernicit") or {}
    if imp.get("cif_r") or imp.get("den_r"):
        a.append('den_r="%s"' % _esc(imp.get("den_r"), 75))
        a.append('cif_r="%s"' % _cif(imp.get("cif_r")))
        a.append('adresa_r="%s"' % _esc(imp.get("adresa_r"), 200))
        for k, xa in (("telefon_r", "telefon_r"), ("fax_r", "fax_r"), ("email_r", "email_r")):
            if str(imp.get(k) or "").strip():
                a.append('%s="%s"' % (xa, _esc(imp.get(k), 200)))
    linii = ['<declaratie221 xmlns="%s" %s>' % (NS, " ".join(a))]
    # ORDINE XSD: activitati INAINTE de asociati
    for act in manual.get("activitati") or []:
        aa = ['judet="%s"' % _esc(act.get("judet"), 2), 'localitate="%s"' % _esc(act.get("localitate"), 30),
              'optiune="%s"' % _esc(act.get("optiune") or "0")]
        linii.append('  <activitati %s>' % " ".join(aa))
        for p in act.get("produse") or []:
            linii.append('    <produse codp="%s" prod1="%s"/>' % (_esc(p.get("codp"), 3), _num2(p.get("prod1") or 0)))
        linii.append('  </activitati>')
    for s in asociati:
        cota = _cota(s.get("cota_d") or 0)
        cota_s = ("%d" % cota) if cota == cota.to_integral_value() else ("%s" % cota)
        sa = ['nume_d="%s"' % _esc(s.get("nume_d"), 75), 'cif_d="%s"' % _cif(s.get("cif_d")),
              'dom_d="%s"' % _esc(s.get("dom_d"), 200), 'cota_d="%s"' % cota_s]
        if str(s.get("nr_zile_d") or "").strip():
            sa.append('nr_zile_d="%s"' % _esc(s.get("nr_zile_d")))
        linii.append('  <asociati %s/>' % " ".join(sa))
    linii.append('</declaratie221>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, an, manual)
    if er:
        raise ValueError("D221 nu se poate genera: " + " ".join(er))
    calc = calcul_d221(manual)
    xml = build_xml(prof, an, manual)
    res = Rezultat221(an=an, nr_activitati=calc["nr_activitati"], nr_asociati=calc["nr_asociati"])
    return xml, res
