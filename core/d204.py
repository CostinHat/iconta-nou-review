"""core/d204.py — D204: Declaratie anuala de venit pentru asocieri fara personalitate
juridica si entitati supuse regimului transparentei fiscale.

Se depune anual de asociatul desemnat, in numele asocierii: pentru fiecare activitate se
distribuie pe asociati venitul net / pierderea fiscala, proportional cu cota de participare
(Σ cote = 100). Declaratie MANUALA - identitatea asocierii, reprezentantul, activitatea si
lista asociatilor vin din `manual` (aplicatia nu are registru de asocieri fara personalitate
juridica).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D204Validator.jar), versiunea in vigoare
J3.0.14 (anaf_surse/versiuni.xml) = pachet d204validator/v2, namespace declaratie:v3.
Structura a fost CITITA din bytecode si PROBATA atribut cu atribut pe DUKIntegrator pana la
"Validare fara erori":
  <d204> (RADACINA, namespace :v3 - atentie, NU <declaratie204>; acela e root-ul versiunilor
    vechi v0/v1 namespace :v1/:v2, respinse de DUK curent cu 'sectiune necunoscuta'):
      luna, an, d_rec;
      ASOCIEREA (entitatea declarata): nume (denumirea asocierii), cif (CUI asociere, max 10),
        adresa;
      REPREZENTANTUL (asociatul desemnat care depune): den_r (numele lui), cif_r (CNP sau CUI,
        deci accepta 13 cifre), adresa_r;
      totalPlata_A.
    (Maparea nume/cif/adresa = asociere vs den_r/cif_r/adresa_r = reprezentant a fost stabilita
    empiric: root 'cif' respinge un CNP de 13 cifre - 'sir mai lung de 10 caractere' - deci e
    CUI de entitate, pe cand 'cif_r' accepta CNP.)
  <activitate> (1..n, copil al <d204>): categ_venit, det_ven_net, CAEN, forma_org, nr_asoc,
    judet, sediu, nr_contr, data_contr, venit3, chelt3, net3, pierd3.
  <asociat> (1..n, copil al <activitate>, DUPA atributele activitatii): cif_d (NIF: CNP/CUI),
    nume_d, cota_d, venit_d, pierd_d.

Reguli citite din validator si PROBATE pe DUK:
  - Σ cota_d = 100 per activitate; fiecare cota_d <= 100.
  - nr_asoc (pe activitate) = numarul de sectiuni <asociat> ale activitatii.
  - net3 = venit3 - chelt3 daca venit3 >= chelt3, altfel 0; pierd3 = chelt3 - venit3 daca
    chelt3 > venit3, altfel 0.
  - Σ venit_d = net3 (venitul net distribuit); Σ pierd_d = pierd3 (pierderea distribuita).
  - categ_venit != 3 => det_ven_net = 1; categ_venit = 3 => forma_org = 1.
  - det_ven_net = 1 => CAEN obligatoriu si FARA sectiuni <anexa>; det_ven_net = 2 (norma de
    venit) => cel putin o <anexa> cu <produse>.
  - judet Bucuresti => atributul 'sector' obligatoriu; alt judet => 'sector' interzis.
  - data_contr in format zi.luna.an (dd.mm.yyyy); nr_contr si data_contr ambele sau niciunul.

NEPOPULAT deliberat (documentat, nu se ghiceste - v. si punctul 6 din raport):
  - Cazul det_ven_net = 2 (norma de venit, tipic categ_venit = 3 activitati agricole):
    sectiunile <anexa>/<produse> (norma, supr, suprImp, suprNimp, normaRed) - se adauga pe
    aceeasi metoda cand apar date. Modulul acopera cazul sistemului real (det_ven_net = 1).
  - Atribute optionale de identificare/contract: telefon/email/fax (reprezentant), data_doc/
    nr_doc, data_I/data_F, modif_exerc - se pun din manual daca sunt date.
  - totalPlata_A = 0 (D204 e informativa - distribuire; nu genereaza obligatie de plata pe cont).

Contract dXXX: pull/erori_generare/calcul_d204/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d204:declaratie:v3"
_NEDIGIT = re.compile(r"\D")
_CATEG_VENIT = {1, 2, 3, 4, 5, 6}          # coduri categorie venit acceptate
_CUI_KEY = (7, 5, 3, 2, 1, 7, 5, 3, 2)     # cheia de control CUI
_CNP_W = (2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9)
_JUDET_BUC = {"40", "B", "BUCURESTI", "MUNICIPIUL BUCURESTI"}


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _i(x):
    """Suma in bani -> intreg, rotunjire aritmetica half-up (ANAF cere half-up)."""
    if x in (None, ""):
        return 0
    return int(Decimal(str(x).replace(",", ".")).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cota(x):
    """Cota de participare N(3.2): maxim 2 zecimale."""
    return Decimal(str(x).replace(",", ".")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _cui_valid(x):
    """CUI valid (cifra de control, cheia 753217532), max 10 cifre."""
    c = _cif(x)
    if not (2 <= len(c) <= 10):
        return False
    body = c[:-1].rjust(9, "0")
    s = sum(int(body[i]) * _CUI_KEY[i] for i in range(9))
    ctrl = (s * 10) % 11
    ctrl = 0 if ctrl == 10 else ctrl
    return ctrl == int(c[-1])


def _cnp_valid(x):
    c = _cif(x)
    if len(c) != 13:
        return False
    s = sum(int(c[i]) * _CNP_W[i] for i in range(12))
    ctrl = s % 11
    ctrl = 1 if ctrl == 10 else ctrl
    return ctrl == int(c[12])


def _nif_valid(x):
    """NIF (cif_d, cif_r): CNP (persoana fizica) sau CUI (persoana juridica)."""
    return _cnp_valid(x) or _cui_valid(x)


def _data(x):
    """Normalizeaza data la dd.mm.yyyy (formatul cerut de validator pentru data_contr)."""
    s = str(x or "").strip()
    if not s:
        return ""
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", s)
    if m:
        return "%02d.%02d.%s" % (int(m.group(3)), int(m.group(2)), m.group(1))
    m = re.match(r"^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})$", s)
    if m:
        return "%02d.%02d.%s" % (int(m.group(1)), int(m.group(2)), m.group(3))
    return s


@dataclass
class Rezultat204:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_activitati: int = 0
    nr_asociati: int = 0
    avertismente: list = field(default_factory=list)


def _activitati(manual):
    """Normalizeaza intrarea la o lista de activitati, fiecare cu lista ei de asociati.
    Accepta fie manual['activitati'] = [{...,'asociati':[...]}], fie forma plata (o singura
    activitate) manual['activitate'] = {...} + manual['asociati'] = [...]."""
    acts = manual.get("activitati")
    if acts:
        return [dict(a) for a in acts]
    act = dict(manual.get("activitate") or {})
    act["asociati"] = manual.get("asociati") or []
    return [act]


def calcul_d204(manual):
    """Per activitate: net3/pierd3 din venit3/chelt3, totalurile distribuite si regula
    cotelor Σ=100. Nu fabrica sume - le preia din `manual`; suma de control = suma din input."""
    out = []
    for act in _activitati(manual):
        venit3 = _i(act.get("venit3"))
        chelt3 = _i(act.get("chelt3"))
        net3 = venit3 - chelt3 if venit3 >= chelt3 else 0
        pierd3 = chelt3 - venit3 if chelt3 > venit3 else 0
        asociati = []
        for a in act.get("asociati") or []:
            asociati.append({
                "cif_d": _cif(a.get("cif")),
                "nume_d": a.get("nume"),
                "cota_d": _cota(a.get("cota") or 0),
                "venit_d": _i(a.get("venit")),
                "pierd_d": _i(a.get("pierd")),
            })
        out.append({
            "categ_venit": int(act.get("categ_venit") or 1),
            "det_ven_net": int(act.get("det_ven_net") or 1),
            "caen": _cif(act.get("caen") or act.get("CAEN")),
            "forma_org": int(act.get("forma_org") or 1),
            "judet": str(act.get("judet") or "").strip(),
            "sector": str(act.get("sector") or "").strip(),
            "sediu": act.get("sediu"),
            "nr_contr": str(act.get("nr_contr") or "").strip(),
            "data_contr": _data(act.get("data_contr")),
            "venit3": venit3, "chelt3": chelt3, "net3": net3, "pierd3": pierd3,
            "nr_asoc": len(asociati),
            "sum_cota": sum((a["cota_d"] for a in asociati), Decimal(0)),
            "sum_venit_d": sum(a["venit_d"] for a in asociati),
            "sum_pierd_d": sum(a["pierd_d"] for a in asociati),
            "asociati": asociati,
        })
    return {"activitati": out, "totalPlata_A": 0}


def pull(conn, schema, perioada):
    """D204 e MANUALA: aplicatia nu are registru de asocieri fara personalitate juridica.
    Identitatea asocierii, reprezentantul, activitatea si asociatii vin din `manual`."""
    return {}


def erori_generare(prof, manual):
    er = []
    aso = manual.get("asociere") or {}
    rep = manual.get("reprezentant") or manual.get("declarant") or {}
    # ASOCIEREA: nume (denumire), cif (CUI, max 10), adresa
    if not str(aso.get("den") or aso.get("nume") or "").strip():
        er.append("Lipsa denumire asociere (asociere.den).")
    if not _cui_valid(aso.get("cif") or aso.get("cui")):
        er.append("CUI asociere (asociere.cif) invalid (max 10 cifre + cifra de control).")
    if not str(aso.get("adresa") or "").strip():
        er.append("Lipsa adresa asociere (asociere.adresa).")
    # REPREZENTANTUL: den_r (nume), cif_r (CNP sau CUI), adresa_r
    if not str(rep.get("nume") or rep.get("den") or "").strip():
        er.append("Lipsa nume reprezentant (reprezentant.nume).")
    if not _nif_valid(rep.get("cif")):
        er.append("CIF/CNP reprezentant (reprezentant.cif) invalid.")
    if not str(rep.get("adresa") or "").strip():
        er.append("Lipsa adresa reprezentant (reprezentant.adresa).")

    calc = calcul_d204(manual)
    if not calc["activitati"] or all(not a["asociati"] for a in calc["activitati"]):
        er.append("D204 cere cel putin o activitate cu cel putin un asociat.")
    for idx, act in enumerate(calc["activitati"], 1):
        et = "Activitate %d" % idx
        if act["categ_venit"] not in _CATEG_VENIT:
            er.append("%s: categ_venit %s invalid." % (et, act["categ_venit"]))
        if act["det_ven_net"] not in (1, 2):
            er.append("%s: det_ven_net trebuie 1 sau 2." % et)
        if act["det_ven_net"] == 2:
            er.append("%s: det_ven_net=2 (norma de venit) cere sectiuni <anexa>/<produse> - "
                      "caz nepopulat in acest modul; foloseste det_ven_net=1 (sistem real)." % et)
        if act["categ_venit"] != 3 and act["det_ven_net"] != 1:
            er.append("%s: categ_venit != 3 impune det_ven_net = 1." % et)
        if act["categ_venit"] == 3 and act["forma_org"] != 1:
            er.append("%s: categ_venit = 3 impune forma_org = 1." % et)
        if act["det_ven_net"] == 1 and not act["caen"]:
            er.append("%s: det_ven_net=1 cere cod CAEN." % et)
        if not act["judet"]:
            er.append("%s: lipsa judet." % et)
        if act["judet"].upper() in _JUDET_BUC and not act["sector"]:
            er.append("%s: pentru Municipiul Bucuresti este obligatoriu sectorul." % et)
        if act["judet"].upper() not in _JUDET_BUC and act["sector"]:
            er.append("%s: sectorul se completeaza doar pentru Municipiul Bucuresti." % et)
        if not str(act["sediu"] or "").strip():
            er.append("%s: lipsa sediu." % et)
        if bool(act["nr_contr"]) != bool(act["data_contr"]):
            er.append("%s: nr_contr si data_contr trebuie completate impreuna." % et)
        if not act["asociati"]:
            er.append("%s: cel putin un asociat." % et)
        cifuri = []
        for j, a in enumerate(act["asociati"], 1):
            if not str(a["nume_d"] or "").strip():
                er.append("%s asociat %d: lipsa nume (nume_d)." % (et, j))
            if not _nif_valid(a["cif_d"]):
                er.append("%s asociat %d: cif_d (CNP/CUI) invalid." % (et, j))
            else:
                cifuri.append(a["cif_d"])
            if not (Decimal(0) < a["cota_d"] <= Decimal(100)):
                er.append("%s asociat %d: cota %s invalida (0<cota<=100)." % (et, j, a["cota_d"]))
        if len(cifuri) != len(set(cifuri)):
            er.append("%s: cif_d duplicat intre asociati." % et)
        if act["asociati"] and act["sum_cota"] != Decimal(100):
            er.append("%s: suma cotelor (%s) trebuie sa fie 100." % (et, act["sum_cota"]))
        if act["sum_venit_d"] != act["net3"]:
            er.append("%s: suma venit_d (%d) trebuie sa fie egala cu venitul net net3 (%d)."
                      % (et, act["sum_venit_d"], act["net3"]))
        if act["sum_pierd_d"] != act["pierd3"]:
            er.append("%s: suma pierd_d (%d) trebuie sa fie egala cu pierderea pierd3 (%d)."
                      % (et, act["sum_pierd_d"], act["pierd3"]))
    return er


def build_xml(prof, an, luna, manual):
    calc = calcul_d204(manual)
    aso = manual.get("asociere") or {}
    rep = manual.get("reprezentant") or manual.get("declarant") or {}
    h = []
    h.append('luna="%d"' % int(luna))
    h.append('an="%d"' % int(an))
    h.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    # ASOCIEREA
    h.append('nume="%s"' % _esc(aso.get("den") or aso.get("nume"), 200))
    h.append('cif="%s"' % _cif(aso.get("cif") or aso.get("cui")))
    h.append('adresa="%s"' % _esc(aso.get("adresa"), 200))
    # REPREZENTANTUL
    h.append('den_r="%s"' % _esc(rep.get("nume") or rep.get("den"), 200))
    h.append('cif_r="%s"' % _cif(rep.get("cif")))
    h.append('adresa_r="%s"' % _esc(rep.get("adresa"), 200))
    if rep.get("telefon"):
        h.append('telefon="%s"' % _esc(rep.get("telefon"), 15))
    if rep.get("email"):
        h.append('email="%s"' % _esc(rep.get("email"), 100))
    if rep.get("fax"):
        h.append('fax="%s"' % _esc(rep.get("fax"), 15))
    h.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<d204 xmlns="%s" %s>' % (NS, " ".join(h))]
    for act in calc["activitati"]:
        aa = []
        aa.append('categ_venit="%d"' % act["categ_venit"])
        aa.append('det_ven_net="%d"' % act["det_ven_net"])
        if act["caen"]:
            aa.append('CAEN="%s"' % act["caen"])
        aa.append('forma_org="%d"' % act["forma_org"])
        aa.append('nr_asoc="%d"' % act["nr_asoc"])
        aa.append('judet="%s"' % _esc(act["judet"]))
        if act["sector"]:
            aa.append('sector="%s"' % _esc(act["sector"]))
        aa.append('sediu="%s"' % _esc(act["sediu"], 200))
        aa.append('nr_contr="%s"' % _esc(act["nr_contr"], 20))
        aa.append('data_contr="%s"' % act["data_contr"])
        aa.append('venit3="%d"' % act["venit3"])
        aa.append('chelt3="%d"' % act["chelt3"])
        aa.append('net3="%d"' % act["net3"])
        aa.append('pierd3="%d"' % act["pierd3"])
        linii.append('  <activitate %s>' % " ".join(aa))
        for a in act["asociati"]:
            cota = a["cota_d"]
            cota_s = ("%d" % cota) if cota == cota.to_integral_value() else ("%s" % cota)
            ba = ['cif_d="%s"' % a["cif_d"], 'nume_d="%s"' % _esc(a["nume_d"], 75),
                  'cota_d="%s"' % cota_s, 'venit_d="%d"' % a["venit_d"],
                  'pierd_d="%d"' % a["pierd_d"]]
            linii.append('    <asociat %s/>' % " ".join(ba))
        linii.append('  </activitate>')
    linii.append('</d204>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = int(getattr(perioada, "luna", 0) or 12)   # D204 = anuala (luna marcaj = 12)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D204 nu se poate genera: " + " ".join(er))
    calc = calcul_d204(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat204(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_activitati=len(calc["activitati"]),
                      nr_asociati=sum(len(a["asociati"]) for a in calc["activitati"]))
    return xml, res
