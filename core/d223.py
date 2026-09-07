"""core/d223.py — D223: Declaratie privind veniturile estimate pentru asocierile fara personalitate juridica
si entitati supuse regimului transparentei fiscale.

Asocierea (prin responsabilul desemnat) declara venitul estimat (brut, cheltuieli deductibile, net) pentru anul
curent, DISTRIBUIT pe fiecare asociat dupa cota de participare. Declaratie MANUALA - asocierea + activitatea +
asociatii vin din input. Ruda cu D220 (venit estimat) + D104 (distributie pe asociati).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D223Validator.jar). _dateVersionTable o singura linie
("2014-01 J1.1.0 0") -> sub-pachet v0, DAR namespace XML :v1 (nepotrivire istorica, confirmata de XSD).
  <declaratie223> (identificare asociere + responsabil): luna, an, d_rec1, d_rec, nume_declar, prenume_declar,
    functie_declar, totalPlata_A, nume, cif, adresa, telefon, fax, email, den_r, cif_r, adresa_r, ...
  <activitate> (1): categ_venit, forma_org, det_venit, nr_asoc, CAEN, judet, localitate, sector, sediu, nr_contr,
    data_contr, nr_doc, data_doc, data_I, data_F, data_S, venit3, chelt3, net3.
  <asociat> (1-n): id_asociat, nume_d, cif_d, dom_d, cota_d, venit_d.

SEMANTICA/REGULI din ACT (anaf_surse/structura_D223_2016_050116_13012016 + d223_20160113.xsd; OPANAF 184/2013):
  - luna = 12 (fix); an>=2016. net3 = venit3-chelt3 daca >0, altfel 0. totalPlata_A = venit3+chelt3+net3.
  - nr_asoc = numarul de <asociat>. suma(cota_d) = 100; per asociat 0<cota_d<100; cif_d unic (CNP 13 cifre).
  - venit_d = distributie a net3 dupa cota_d (ultimul asociat preia restul -> suma(venit_d)=net3);
    daca det_venit=3 (norma) atunci venit_d=0.
  - categ_venit ∈ {1,2,4,5,6,7}; forma_org ∈ {2,3,4}; det_venit ∈ {1=real, 3=norma}. sector oblig daca judet=40.
  - D223 NU are cod_bug. d_rec2 NU se emite (XSD-ul in vigoare nu-l declara; validat empiric la DUK).

Contract dXXX: pull/erori_generare/calcul_d223/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind veniturile estimate pentru asocierile fără personalitate juridică'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d223:declaratie:v1"
_NEDIGIT = re.compile(r"\D")


def _i(x, camp="D223"):
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cota(x):
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat223:
    an: int
    total_plata_a: int = 0
    nr_asociati: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d223(manual):
    act = manual.get("activitate") or {}
    norma = str(act.get("det_venit") or "") == "3"
    venit3 = _i(act.get("venit_brut"))
    chelt3 = _i(act.get("cheltuieli"))
    net3 = (venit3 - chelt3) if venit3 > chelt3 else 0
    asociati = manual.get("asociati") or []
    dist = []
    rest = net3
    for idx, a in enumerate(asociati):
        cota = _cota(a.get("cota_d") or 0)
        if norma:
            vd = 0
        elif idx == len(asociati) - 1:
            vd = rest                      # ultimul preia restul -> suma(venit_d)=net3
        else:
            vd = _i(Decimal(net3) * cota / Decimal(100))
            rest -= vd
        dist.append({"nume_d": a.get("nume_d"), "cif_d": _cif(a.get("cif_d")), "dom_d": a.get("dom_d"),
                     "cota_d": cota, "venit_d": vd})
    d_rec1 = int(manual.get("d_rec1") or 0)
    d_rec = 1 if d_rec1 == 1 else int(manual.get("d_rec") or 0)
    return {"venit3": venit3, "chelt3": chelt3, "net3": net3, "totalPlata_A": venit3 + chelt3 + net3,
            "asociati": dist, "nr_asoc": len(asociati), "d_rec1": d_rec1, "d_rec": d_rec}


def pull(conn, schema, perioada):
    """Declarant + fallback asociere din firma_profil (daca tenant=asocierea)."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    adresa = " ".join(x for x in (r[2], r[3], r[4]) if x)
    return {"den": r[0], "cui": r[1], "adresa": adresa, "declarant_nume": r[5], "declarant_prenume": r[6],
            "declarant_functie": r[7], "telefon": r[8], "email": r[9]}


def _asociere(prof, manual):
    a = dict(manual.get("asociere") or {})
    return {"nume": a.get("nume") or prof.get("den"), "cif": a.get("cif") or prof.get("cui"),
            "adresa": a.get("adresa") or prof.get("adresa"), "telefon": a.get("telefon") or prof.get("telefon"),
            "fax": a.get("fax"), "email": a.get("email") or prof.get("email")}


def erori_generare(prof, manual):
    er = []
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or (manual.get(c))or "").strip():
            er.append("LIPSĂ %s (declarant obligatoriu)." % c)
    aso = _asociere(prof, manual)
    if not _cif(aso.get("cif")):
        er.append("CUI asociere lipsă/invalid (manual.asociere.cif sau firma_profil).")
    if not str(aso.get("nume") or "").strip():
        er.append("LIPSĂ denumire asociere.")
    if not str(aso.get("adresa") or "").strip():
        er.append("LIPSĂ adresa asociere.")
    resp = manual.get("responsabil") or {}
    for c, et in (("den_r", "den_r"), ("cif_r", "cif_r"), ("adresa_r", "adresa_r")):
        if not str(resp.get(c) or "").strip():
            er.append("LIPSĂ %s (responsabilul asocierii, obligatoriu)." % et)
    act = manual.get("activitate")
    if not isinstance(act, dict) or not act:
        er.append("D223 cere `manual.activitate` (categ_venit, forma_org, det_venit, CAEN, județ, localitate...).")
        return er
    if str(act.get("categ_venit") or "") not in {"1", "2", "4", "5", "6", "7"}:
        er.append("activitate: categ_venit invalid (1,2,4,5,6,7).")
    if str(act.get("forma_org") or "") not in {"2", "3", "4"}:
        er.append("activitate: forma_org invalid (2=asociere f.PJ / 3=transparenta / 4=modificare).")
    if str(act.get("det_venit") or "") not in {"1", "3"}:
        er.append("activitate: det_venit invalid (1=real / 3=norma).")
    for c, et in (("caen", "CAEN"), ("judet", "judet"), ("localitate", "localitate"), ("sediu", "sediu"),
                  ("nr_contr", "nr_contr"), ("data_contr", "data_contr")):
        if not str(act.get(c) or "").strip():
            er.append("activitate: lipsă %s (obligatoriu)." % et)
    if str(act.get("judet") or "") == "40" and not str(act.get("sector") or "").strip():
        er.append("activitate: sector obligatoriu pentru județ=40 (București).")
    asociati = manual.get("asociati") or []
    if not asociati:
        er.append("D223 cere cel puțin un asociat (asociati[]).")
    cifuri, suma_cota = [], Decimal(0)
    for i, a in enumerate(asociati, 1):
        if not str(a.get("nume_d") or "").strip():
            er.append("Asociat %d: lipsă nume_d." % i)
        cf = _cif(a.get("cif_d"))
        if len(cf) != 13:
            er.append("Asociat %d: cif_d trebuie CNP de 13 cifre (a fost %r)." % (i, a.get("cif_d")))
        else:
            cifuri.append(cf)
        try:
            cota = _cota(a.get("cota_d") or 0)
        except Exception:
            cota = Decimal(0)
        suma_cota += cota
        if not (Decimal(0) < cota < Decimal(100)) and not (len(asociati) == 1 and cota == Decimal(100)):
            er.append("Asociat %d: cota_d %s invalida (0<cota_d<100; =100 doar cu un singur asociat)." %
                      (i, a.get("cota_d")))
    if asociati and suma_cota != Decimal(100):
        er.append("Suma cotelor de distribuire (%s) trebuie să fie 100." % suma_cota)
    if len(cifuri) != len(set(cifuri)):
        er.append("Asociații au cif_d duplicat (cif_d = cheie unica).")
    return er


_ACT_OPT = [("nr_doc", "nr_doc"), ("data_doc", "data_doc"), ("data_i", "data_I"), ("data_f", "data_F"),
            ("data_s", "data_S")]


def build_xml(prof, an, manual, calc):
    aso = _asociere(prof, manual)
    resp = manual.get("responsabil") or {}
    act = manual.get("activitate") or {}
    a = []
    a.append('luna="12"')
    a.append('an="%d"' % int(an))
    a.append('d_rec1="%d"' % calc["d_rec1"])
    a.append('d_rec="%d"' % calc["d_rec"])
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume") or manual.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume") or manual.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie") or manual.get("declarant_functie"), 50))
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    a.append('nume="%s"' % _esc(aso.get("nume"), 75))
    a.append('cif="%s"' % _cif(aso.get("cif")))
    a.append('adresa="%s"' % _esc(aso.get("adresa"), 200))
    for k, xa in (("telefon", "telefon"), ("fax", "fax"), ("email", "email")):
        if str(aso.get(k) or "").strip():
            a.append('%s="%s"' % (xa, _esc(aso.get(k), 200 if k == "email" else 15)))
    a.append('den_r="%s"' % _esc(resp.get("den_r"), 75))
    a.append('cif_r="%s"' % _cif(resp.get("cif_r")))
    a.append('adresa_r="%s"' % _esc(resp.get("adresa_r"), 200))
    for k, xa in (("telefon_r", "telefon_r"), ("fax_r", "fax_r"), ("email_r", "email_r")):
        if str(resp.get(k) or "").strip():
            a.append('%s="%s"' % (xa, _esc(resp.get(k), 200)))
    linii = ['<declaratie223 xmlns="%s" %s>' % (NS, " ".join(a))]
    # activitate
    aa = ['categ_venit="%s"' % _esc(act.get("categ_venit")), 'forma_org="%s"' % _esc(act.get("forma_org")),
          'det_venit="%s"' % _esc(act.get("det_venit")), 'nr_asoc="%d"' % calc["nr_asoc"],
          'CAEN="%s"' % _esc(act.get("caen"), 4), 'judet="%s"' % _esc(act.get("judet")),
          'localitate="%s"' % _esc(act.get("localitate"), 50)]
    if str(act.get("sector") or "").strip():
        aa.append('sector="%s"' % _esc(act.get("sector")))
    aa.append('sediu="%s"' % _esc(act.get("sediu"), 200))
    aa.append('nr_contr="%s"' % _esc(act.get("nr_contr"), 15))
    aa.append('data_contr="%s"' % _esc(act.get("data_contr"), 10))
    for k, xa in _ACT_OPT:
        if str(act.get(k) or "").strip():
            aa.append('%s="%s"' % (xa, _esc(act.get(k), 15)))
    aa.append('venit3="%d"' % calc["venit3"])
    aa.append('chelt3="%d"' % calc["chelt3"])
    aa.append('net3="%d"' % calc["net3"])
    linii.append('  <activitate %s>' % " ".join(aa))
    for idx, s in enumerate(calc["asociati"], 1):
        cota = s["cota_d"]
        cota_s = ("%d" % cota) if cota == cota.to_integral_value() else ("%s" % cota)
        sa = ['id_asociat="%d"' % idx, 'nume_d="%s"' % _esc(s["nume_d"], 75), 'cif_d="%s"' % s["cif_d"]]
        if str(s.get("dom_d") or "").strip():
            sa.append('dom_d="%s"' % _esc(s["dom_d"], 200))
        sa += ['cota_d="%s"' % cota_s, 'venit_d="%d"' % s["venit_d"]]
        linii.append('    <asociat %s/>' % " ".join(sa))
    linii.append('  </activitate>')
    linii.append('</declaratie223>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D223 nu se poate genera: " + " ".join(er))
    calc = calcul_d223(manual)
    xml = build_xml(prof, an, manual, calc)
    res = Rezultat223(an=an, total_plata_a=calc["totalPlata_A"], nr_asociati=calc["nr_asoc"])
    return xml, res
