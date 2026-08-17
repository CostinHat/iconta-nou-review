"""core/d200.py — D200: Declaratie privind veniturile realizate din Romania (persoane fizice).

Contribuabilul persoana fizica declara, pe fiecare categorie de venit, venitul brut/net realizat in Romania
(activitati independente, cedarea folosintei bunurilor, activitati agricole, transfer titluri de valoare etc.).
Periodicitate ANUALA. Declaratie MANUALA: aplicatia nu tine registru de venituri ale persoanelor fizice, deci
identitatea contribuabilului si valorile (venit_brut/chelt/net/castig/pierdere) vin din `manual` (input contabil).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D200Validator.jar, arbitrul peste anexe, prin DUKIntegrator).
Namespace XML in vigoare = declaratie:v1; pachetul intern selectat dupa an/luna din _dateVersionTable:
2016-01+ -> pachet v3 (structura curenta). Campurile au fost CITITE din bytecode-ul claselor
d200validator/v3/Identificare (antet) si d200validator/v3/Sect (sectiuni) si PROBATE camp cu camp pe validator:
  - Identificare v3 (antet, pe radacina <declaratie200>): luna, an, d_rec, cif_i(CNP), den_i, adresa_i, telefon_i,
    nume_c/prenume_c/initiala_c/cif_c/adresa_c/telefon_c (imputernicit, optional), cont_c/banca_c (IBAN+banca,
    optional), Rezid/Stat_R/cif_S (rezidenta, optional), totalPlata_A (suma de control).
  - Sect v3 (1-n, pe categorie de venit): categ_venit, caen, venit_brut, chelt, venit_net, venit_net_Rsursa,
    castig, pierdere, cif_orgJN, den_orgJN (+ campuri optionale forma_org/det_venit/data_I/data_P/doc_6 nefolosite).

REGULI (citite din bytecode-ul v3, probate pe validator) — determina zeroizarea/omisiunea pe categorie:
  - categ<>(14): venit_brut>=0, chelt>=0, venit_net_Rsursa>=0, castig=0 (daca <>6,8).
  - categ<>(6,8): venit_net = venit_brut - chelt cand >0, altfel 0; pierdere = chelt - venit_brut sau 0.
  - categ=(6,8): venit_brut=0, chelt=0, venit_net=0, venit_net_Rsursa=0; castig si pierdere NU pot fi amandoua >0.
  - categ=(6,8,11,12): chelt=0, venit_net=0, venit_net_Rsursa=0.
  - categ=(11,12): den_orgJN <> null.  categ=(13): cif_orgJN <> null si den_orgJN <> null.
  - categ=(14): venit_brut/chelt/venit_net/venit_net_Rsursa NU se completeaza; castig sau pierdere > 0.
  - venit_net_Rsursa <= venit_net.
  - totalPlata_A (R29, suma de control) = suma pe sectiuni a (venit_net + castig + pierdere) (probat pe DUK).
  - element sectiune in XML = <sect_2> (tag ID_SECT din validator); radacina = <declaratie200> (ID_DECLARATIE).
  - antet OBLIGATORIU (probat, "atributul trebuie sa existe"): nume_c, prenume_c, cif_c, Rezid, d_reg, d_scut
    (d_rec/d_reg/d_scut = flag-uri 0/1, implicit 0; Rezid=0 = rezident RO).

CRITIC: actul OPANAF (cotele/plafoanele/regimul de impozitare) NU e in corpus. Modulul NU fabrica rate, cote sau
plafoane de impozit. Singurul calcul aritmetic permis (evident, nu rata din act): venit_net = venit_brut - chelt
si pierdere = chelt - venit_brut, DOAR cand ambele valori sunt date; altfel valorile se preiau ca atare (carry)
din `manual`. Impozitul datorat NU se calculeaza in D200 (il stabileste ANAF prin decizie de impunere).

Contract dXXX: pull/erori_generare/calcul_d200/build_xml/genereaza(conn, schema, perioada, manual=None).
"""
from dataclasses import dataclass, field
import re
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d200:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_IBAN_OK = re.compile(r"^RO\d{2}[A-Z0-9]{20}$")
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

# categorii care lucreaza pe castig/pierdere (transfer titluri): venit_brut=0
_CAT_CG = {6, 8}
# categorii cu chelt=0, venit_net=0, venit_net_Rsursa=0
_CAT_NET0 = {6, 8, 11, 12}
# categorii care cer den_orgJN (organizator/platitor)
_CAT_ORGJN_DEN = {11, 12, 13}
# categorii care cer cif_orgJN
_CAT_ORGJN_CIF = {13}
_CAT_14 = 14  # castig/pierdere; fara venit_brut/chelt/venit_net/venit_net_Rsursa


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


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


def _i(x):
    """Suma in lei -> intreg (rotunjire aritmetica). None/'' -> 0."""
    if x in (None, ""):
        return 0
    try:
        return int(Decimal(str(str(x).replace(",", "."))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (TypeError, ValueError):
        return 0


def _present(s, k):
    return s.get(k) not in (None, "")


@dataclass
class Rezultat200:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_sectiuni: int = 0
    avertismente: list = field(default_factory=list)


def _calc_sect(s):
    """Aplica zeroizarea/omisiunea pe categorie si calculeaza venit_net/pierdere (aritmetica evidenta)."""
    c = int(_cif(s.get("categ_venit")) or 0)
    o = {"categ_venit": c}
    if s.get("caen"):
        o["caen"] = _cif(s.get("caen"))
    if c == _CAT_14:
        # castig/pierdere; venit_brut/chelt/venit_net/venit_net_Rsursa NU se completeaza
        o["castig"] = _i(s.get("castig"))
        o["pierdere"] = _i(s.get("pierdere"))
        return o
    vb = 0 if c in _CAT_CG else _i(s.get("venit_brut"))
    ch = 0 if c in _CAT_NET0 else _i(s.get("chelt"))
    if c in _CAT_NET0:
        vnet, vnr = 0, 0
    else:
        # venit_net = venit_brut - chelt cand ambele date; altfel carry din manual
        if _present(s, "venit_brut") and _present(s, "chelt"):
            vnet = max(vb - ch, 0)
        else:
            vnet = _i(s.get("venit_net"))
        vnr = min(_i(s.get("venit_net_Rsursa")), vnet)  # venit_net_Rsursa <= venit_net
    if c in _CAT_CG:
        castig = _i(s.get("castig"))
        pierdere = _i(s.get("pierdere"))
    else:
        castig = 0  # categ<>(6,8) -> castig = 0
        pierdere = max(ch - vb, 0)  # pierdere = chelt - venit_brut sau 0
    o.update(venit_brut=vb, chelt=ch, venit_net=vnet, venit_net_Rsursa=vnr,
             castig=castig, pierdere=pierdere)
    if s.get("cif_orgJN"):
        o["cif_orgJN"] = _cif(s.get("cif_orgJN"))
    if s.get("den_orgJN"):
        o["den_orgJN"] = _esc(s.get("den_orgJN"), 200)
    return o


def calcul_d200(manual):
    """Sectiuni calculate + totalPlata_A (R29, suma de control) = suma pe sectiuni a (venit_net+castig+pierdere).

    Probat pe validator: cu doua sectiuni (venit_net 6000/0 si pierdere 0/2000) suma corecta ceruta = 8000.
    """
    sec = [_calc_sect(s) for s in (manual.get("sectiuni") or [])]
    total = sum(x.get("venit_net", 0) + x.get("castig", 0) + x.get("pierdere", 0) for x in sec)
    return {"sectiuni": sec, "totalPlata_A": total}


def pull(conn, schema, perioada):
    """D200 e MANUALA pe persoana fizica; firma nu are registru de venituri ale persoanelor. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not _cnp_valid(manual.get("cif_i")):
        er.append("CNP contribuabil (cif_i) invalid (13 cifre + cifra de control).")
    if not str(manual.get("den_i") or "").strip():
        er.append("Lipsă nume contribuabil (den_i).")
    if not str(manual.get("adresa_i") or "").strip():
        er.append("Lipsă adresa contribuabil (adresa_i).")
    cont = str(manual.get("cont_c") or "").replace(" ", "").upper()
    if cont and not _IBAN_OK.match(cont):
        er.append("IBAN (cont_c) invalid - aștept RO + 22 caractere.")
    sec = manual.get("sectiuni") or []
    if not sec:
        er.append("D200 cere cel puțin o sectiune de venit (sectiuni[]).")
    for i, s in enumerate(sec, 1):
        c = int(_cif(s.get("categ_venit")) or 0)
        if not (1 <= c <= 14):
            er.append("Secțiunea %d: categ_venit %r invalid (1..14)." % (i, s.get("categ_venit")))
            continue
        if c in _CAT_ORGJN_DEN and not str(s.get("den_orgJN") or "").strip():
            er.append("Secțiunea %d: categ_venit=%d cere den_orgJN (denumire organizator/plătitor)." % (i, c))
        if c in _CAT_ORGJN_CIF and not _cif(s.get("cif_orgJN")):
            er.append("Secțiunea %d: categ_venit=13 cere cif_orgJN." % i)
        if c == _CAT_14:
            if _i(s.get("castig")) <= 0 and _i(s.get("pierdere")) <= 0:
                er.append("Secțiunea %d: categ_venit=14 cere castig>0 sau pierdere>0." % i)
        if c in _CAT_CG and _i(s.get("castig")) > 0 and _i(s.get("pierdere")) > 0:
            er.append("Secțiunea %d: categ_venit=%d - castig și pierdere nu pot fi amandoua >0." % (i, c))
    return er


def build_xml(prof, an, luna, manual, calc):
    a = []
    a.append('luna="12"')  # declaratie anuala: perioada de raportare luna=12 (fix, ca D205/D230)
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    cnp = _cif(manual.get("cif_i"))
    den = _esc(manual.get("den_i"), 200)
    a.append('cif_i="%s"' % cnp)
    a.append('den_i="%s"' % den)
    a.append('adresa_i="%s"' % _esc(manual.get("adresa_i"), 200))
    if manual.get("telefon_i"):
        a.append('telefon_i="%s"' % _esc(manual.get("telefon_i"), 15))
    # contribuabil - nume/prenume/CNP (OBLIGATORII cf. validator). cif_c = acelasi CNP ca cif_i.
    a.append('nume_c="%s"' % _esc(manual.get("nume_c") or den, 75))
    a.append('prenume_c="%s"' % _esc(manual.get("prenume_c"), 75))
    if manual.get("initiala_c"):
        a.append('initiala_c="%s"' % _esc(manual.get("initiala_c"), 1))
    a.append('cif_c="%s"' % (_cif(manual.get("cif_c")) or cnp))
    if manual.get("adresa_c"):
        a.append('adresa_c="%s"' % _esc(manual.get("adresa_c"), 200))
    if manual.get("telefon_c"):
        a.append('telefon_c="%s"' % _esc(manual.get("telefon_c"), 15))
    # rezidenta (OBLIGATORIU Rezid): 0 = rezident RO (implicit). Rezid=1 -> nerezident, cere Stat_R/cif_S.
    rezid = int(manual.get("Rezid") or 0)
    a.append('Rezid="%d"' % rezid)
    if rezid == 1:
        a.append('Stat_R="%s"' % _esc(manual.get("Stat_R"), 2))
        if manual.get("cif_S"):
            a.append('cif_S="%s"' % _esc(manual.get("cif_S"), 20))
    # date antet (OBLIGATORII ca atribut cf. validator): d_reg (data inreg.), d_scut (data scutire)
    a.append('d_reg="%d"' % int(manual.get("d_reg") or 0))
    a.append('d_scut="%d"' % int(manual.get("d_scut") or 0))
    # IBAN (optional)
    cont = str(manual.get("cont_c") or "").replace(" ", "").upper()
    if cont:
        a.append('cont_c="%s"' % _esc(cont, 24))
    if manual.get("banca_c"):
        a.append('banca_c="%s"' % _esc(manual.get("banca_c"), 200))
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<declaratie200 xmlns="%s" %s>' % (NS, " ".join(a))]
    for s in calc["sectiuni"]:
        sa = ['categ_venit="%d"' % s["categ_venit"]]
        if "caen" in s:
            sa.append('caen="%s"' % s["caen"])
        for k in ("venit_brut", "chelt", "venit_net", "venit_net_Rsursa", "castig", "pierdere"):
            if k in s:
                sa.append('%s="%d"' % (k, s[k]))
        if "cif_orgJN" in s:
            sa.append('cif_orgJN="%s"' % s["cif_orgJN"])
        if "den_orgJN" in s:
            sa.append('den_orgJN="%s"' % s["den_orgJN"])
        linii.append('  <sect_2 %s/>' % " ".join(sa))
    linii.append('</declaratie200>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = 12
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D200 nu se poate genera: " + " ".join(er))
    calc = calcul_d200(manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat200(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_sectiuni=len(calc["sectiuni"]))
    return xml, res
