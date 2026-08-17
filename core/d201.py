"""core/d201.py — D201: Declaratie privind veniturile realizate din strainatate (persoane fizice).

Declaratie ANUALA, MANUALA (persoana fizica): contribuabilul declara veniturile obtinute in
strainatate, pe pereche (tara, categorie de venit). Aplicatia nu are registrul veniturilor externe
ale persoanei fizice - toate valorile numerice vin din `manual`.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (DUKIntegrator, D201Validator.jar, pachet d201validator/v1,
namespace declaratie:v2). Structura si regulile au fost CITITE din bytecode si PROBATE camp cu camp pe
validator (proba finala: DUKIntegrator -v D201 -> 'Validare fara erori'):
  Radacina <declaratie201> (namespace v2). Sectiune repetabila <sect_2> (tag MIC, nu 'Sect_2';
  atributul 'nrcrt' NU exista in XML - respins ca necunoscut).
  Antet OBLIGATORIU (probat 'atributul trebuie sa existe'): luna, an, d_rec, nume_c, initiala_c,
    prenume_c, cif_c (CNP), totalPlata_A. OPTIONAL: adresa_c, banca_c, cont_c, telefon_c si blocul
    imputernicitului cif_i/den_i/adresa_i/telefon_i (den_i <=> cif_i ambele sau niciunul).
  sect_2 OBLIGATORIU: categ_venit, statul (cod tara ISO-3166 numeric din nomenclator), venit_B (brut),
    chlt_D (cheltuieli deductibile), venit_N (net), imp1 (impozit platit in strainatate), imp2 (impozit
    pe salarii), pierdere. OPTIONAL: data_I, data_P (format dd.mm.yyyy, in anul raportarii, data_I<=data_P).
Reguli probate pe validator: R30 (categ<>23 & venit_B>chlt_D => venit_N=venit_B-chlt_D); pierdere=chlt_D-venit_B
  cand venit_B<chlt_D (si venit_N=0); categ=23 => venit_B=0 & chlt_D=0; R33 (imp2<>0 admis DOAR la
  categ_venit=14); perechea (statul,categ_venit) unica; 'pierdere si venit nu in acelasi timp'.

CRITIC: actul (metodologia creditului fiscal extern) NU e in corpus. Modulul NU fabrica rate de impozit,
credit fiscal, curs valutar sau plafoane - toate valorile numerice vin din `manual`. SINGURUL calcul
intern: venit_N = venit_B - chlt_D (respectiv pierdere = chlt_D - venit_B) cand ambele sunt date; altfel
se preia (carry) valoarea din `manual`. d_rec='0' implicit (rectificativa: 1). totalPlata_A implicit '0'
(suma de control; PDF-ul inteligent ANAF o recalculeaza; nu fabricam credit fiscal).

Contract dXXX: pull/erori_generare/calcul_d201/build_xml/genereaza(conn, schema, perioada, manual=None).
NEPOPULAT deliberat (optionale, se adauga din `manual` la nevoie; nimic nu se ghiceste): blocul
imputernicitului (cif_i/den_i/adresa_i/telefon_i), banca_c/cont_c/telefon_c, data_I/data_P.
"""
from dataclasses import dataclass, field
import re

NS = "mfp:anaf:dgti:d201:declaratie:v2"
_NEDIGIT = re.compile(r"\D")
_DATA_RO = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
_CATEG_NET_ONLY = 23   # categ_venit=23 => venit_B=0, chlt_D=0 (doar venit net)
_CATEG_SALARII = 14    # imp2 (impozit pe salarii) admis DOAR la categ_venit=14 (R33)


def _cif(x):
    # NB: "" if x is None (NU str(x or "")): valoarea intreaga 0 e reala (chlt_D=0), nu absenta.
    return _NEDIGIT.sub("", "" if x is None else str(x))


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


def _int(x):
    """Suma intreaga in lei (D201 nu are zecimale in atributele numerice). Gol/None -> None."""
    d = _cif(x)
    return int(d) if d else None


@dataclass
class Rezultat201:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_sectiuni: int = 0
    venit_net_total: int = 0
    avertismente: list = field(default_factory=list)


def _norm_sectiune(s):
    """Aplica R30 / pierdere / categ=23: completeaza venit_N sau pierdere cand venit_B si chlt_D sunt
    ambele date; altfel preia (carry) valorile din `manual`. Nu inventeaza nimic peste bruta-cheltuieli."""
    categ = _int(s.get("categ_venit"))
    vb = _int(s.get("venit_B"))
    cd = _int(s.get("chlt_D"))
    vn = _int(s.get("venit_N"))
    pierdere = _int(s.get("pierdere"))
    imp1 = _int(s.get("imp1"))
    imp2 = _int(s.get("imp2"))
    if categ == _CATEG_NET_ONLY:
        vb, cd = 0, 0                      # categ=23: fara brut / cheltuieli
        pierdere = 0 if pierdere is None else pierdere
    elif vb is not None and cd is not None:
        if vb > cd:
            vn, pierdere = vb - cd, 0
        elif vb < cd:
            vn, pierdere = 0, cd - vb
        else:
            vn, pierdere = 0, 0
    imp1 = 0 if imp1 is None else imp1
    imp2 = (0 if imp2 is None else imp2) if categ == _CATEG_SALARII else 0   # R33
    return {"categ_venit": categ, "statul": _int(s.get("statul")),
            "venit_B": vb or 0, "chlt_D": cd or 0, "venit_N": vn or 0,
            "imp1": imp1, "imp2": imp2, "pierdere": pierdere or 0,
            "data_I": _esc(s.get("data_I")) or None, "data_P": _esc(s.get("data_P")) or None}


def calcul_d201(manual):
    """Normalizeaza sectiunile (venit_N/pierdere) si suma de control totalPlata_A.
    totalPlata_A: preluat din `manual` daca e dat; altfel 0 (PDF-ul inteligent ANAF o recalculeaza)."""
    sect = [_norm_sectiune(s) for s in (manual.get("sectiuni") or [])]
    tot = _int(manual.get("totalPlata_A"))
    return {"sectiuni": sect, "totalPlata_A": tot if tot is not None else 0,
            "venit_net_total": sum(s["venit_N"] for s in sect)}


def pull(conn, schema, perioada):
    """D201 e MANUALA pe persoana fizica; firma nu are registrul veniturilor externe ale PF.
    Contractul dXXX cere `pull`; nu exista sursa de tras."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("nume_c") or "").strip():
        er.append("Lipsă nume contribuabil (nume_c).")
    if not str(manual.get("initiala_c") or "").strip():
        er.append("Lipsă initiala tata (initiala_c).")
    if not str(manual.get("prenume_c") or "").strip():
        er.append("Lipsă prenume contribuabil (prenume_c).")
    if not _cnp_valid(manual.get("cif_c")):
        er.append("CNP contribuabil (cif_c) invalid (13 cifre + cifra de control).")
    sect = manual.get("sectiuni") or []
    if not sect:
        er.append("Lipsă sectiuni de venit (sectiuni) - minim o pereche (țară, categorie).")
    vazute = set()
    for i, s in enumerate(sect, 1):
        categ = _int(s.get("categ_venit"))
        tara = _int(s.get("statul"))
        if categ is None:
            er.append("Secțiunea %d: lipsă categ_venit (categoria de venit)." % i)
        if tara is None:
            er.append("Secțiunea %d: lipsă statul (cod țară ISO-3166 numeric)." % i)
        if categ is not None and tara is not None:
            if (tara, categ) in vazute:
                er.append("Secțiunea %d: perechea (statul=%s, categ_venit=%s) duplicata - trebuie unica."
                          % (i, tara, categ))
            vazute.add((tara, categ))
        if _int(s.get("imp2")) and categ != _CATEG_SALARII:
            er.append("Secțiunea %d: imp2 (impozit pe salarii) admis doar la categ_venit=14 (R33)." % i)
        for et in ("data_I", "data_P"):
            dv = s.get(et)
            if dv and not _DATA_RO.match(str(dv).strip()):
                er.append("Secțiunea %d: %s trebuie în format dd.mm.yyyy." % (i, et))
    return er


def build_xml(prof, an, luna, manual):
    calc = calcul_d201(manual)
    d_rec = _int(manual.get("d_rec"))
    h = ['luna="%d"' % int(luna), 'an="%d"' % int(an),
         'd_rec="%d"' % (0 if d_rec is None else d_rec),
         'nume_c="%s"' % _esc(manual.get("nume_c"), 75),
         'initiala_c="%s"' % _esc(manual.get("initiala_c"), 1),
         'prenume_c="%s"' % _esc(manual.get("prenume_c"), 75),
         'cif_c="%s"' % _cif(manual.get("cif_c"))]
    if manual.get("adresa_c"):
        h.append('adresa_c="%s"' % _esc(manual.get("adresa_c"), 200))
    if manual.get("banca_c"):
        h.append('banca_c="%s"' % _esc(manual.get("banca_c"), 100))
    if manual.get("cont_c"):
        h.append('cont_c="%s"' % _esc(str(manual.get("cont_c")).replace(" ", "").upper(), 24))
    if manual.get("telefon_c"):
        h.append('telefon_c="%s"' % _esc(manual.get("telefon_c"), 15))
    h.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = []
    for s in calc["sectiuni"]:
        a = ['categ_venit="%d"' % s["categ_venit"], 'statul="%d"' % s["statul"],
             'venit_B="%d"' % s["venit_B"], 'chlt_D="%d"' % s["chlt_D"],
             'venit_N="%d"' % s["venit_N"], 'imp1="%d"' % s["imp1"],
             'imp2="%d"' % s["imp2"], 'pierdere="%d"' % s["pierdere"]]
        if s["data_I"]:
            a.append('data_I="%s"' % s["data_I"])
        if s["data_P"]:
            a.append('data_P="%s"' % s["data_P"])
        linii.append('  <sect_2 %s/>' % " ".join(a))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie201 xmlns="%s" %s>\n%s\n</declaratie201>\n'
            % (NS, " ".join(h), "\n".join(linii)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = int(perioada.luna) if getattr(perioada, "luna", None) else 12
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D201 nu se poate genera: " + " ".join(er))
    calc = calcul_d201(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat201(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_sectiuni=len(calc["sectiuni"]), venit_net_total=calc["venit_net_total"])
    return xml, res
