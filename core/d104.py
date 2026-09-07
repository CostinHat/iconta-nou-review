"""core/d104.py — D104: Declaratie privind distribuirea intre asociati a veniturilor si cheltuielilor.

Se depune de asociatul desemnat al unei ASOCIERI FARA PERSONALITATE JURIDICA, in numele asocierii:
distribuie pe fiecare asociat venitul/cheltuiala/impozitul si diferenta de plata/recuperat. Trimestrial
(cumulat) + definitivare anuala. Declaratie MANUALA - lista de asociati + sumele vin din input (aplicatia
nu are inca registru dedicat de asocieri).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D104Validator.jar). _dateVersionTable are o singura linie
("2012-01 J1.2.0 0") -> sub-pachet in vigoare d104validator/v0/, DAR namespace-ul XML e :v1 (nepotrivire
istorica, confirmata de ValidatorImpl + d104.xsd). declaratie stabila (fara versiune noua din 2013).
  <declaratie104> (identificare + totaluri): luna, an, d_rec, nume_declar, prenume_declar, functie_declar,
    cui, den, adresa, telefon, fax, mail, Tven, Tchelt, profit_pierd, TimpD, TimpR, TdifP, TdifR, totalPlata_A.
  <SB> (1-n, per asociat): den1, cif1, adresa1, cota, venit, chelt, impD, impR, difPR.

SEMANTICA/REGULI din ACT (anaf_surse/structura_D104_2012_v100_030613 + OPANAF 1950/2012; asocieri fara
personalitate juridica, CF L227/2015 - regimul asocierilor):
  - luna (marcator perioada) ∈ {3=Trim.I, 6=Trim.II, 9=Trim.III, 12=Definitivare An}; an>=2012.
  - Totaluri: Tven=Σ(venit); Tchelt=Σ(chelt); TimpD=Σ(impD); TimpR=Σ(impR); TdifP=Σ(difPR>0);
    TdifR=Σ(difPR<0). totalPlata_A = profit_pierd + TimpD + TimpR + TdifP + TdifR (suma de control).
  - Per SB: cota (0<cota<=100); venit/chelt/impD>=0; impR=0 daca luna∈{3,6,9}; difPR = impD-impR daca
    luna=12, altfel 0. cif1 = cheie unica (nu se repeta).
  - profit_pierd = profit impozabil(+)/pierdere(-) al asocierii - INPUT contabil (NU se calcula ca
    Tven-Tchelt: pot exista ajustari fiscale; actul nu da formula).
  - D104 NU are cod_bug (nu e obligatie de plata pe cont bugetar).

Contract dXXX: pull/erori_generare/calcul_d104/build_xml/genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație privind distribuirea între asociați a veniturilor și cheltuielilor'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d104:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_LUNI_VALIDE = {3, 6, 9, 12}


def _i(x, camp="D104"):
    """Suma in bani -> intreg cu rotunjire ARITMETICA (half-up), nu bancara (ANAF cere half-up)."""
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cota(x):
    """Cota de participare N(3.2): 0<cota<=100, cu maxim 2 zecimale."""
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


@dataclass
class Rezultat104:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_asociati: int = 0
    avertismente: list = field(default_factory=list)


def _luna(perioada):
    """Marcatorul de perioada D104: trim (1-4) -> {3,6,9,12}; sau luna deja ∈ {3,6,9,12}."""
    if getattr(perioada, "trim", None):
        return int(perioada.trim) * 3
    return int(getattr(perioada, "luna", 0) or 0)


def calcul_d104(luna, manual):
    """Distribuie pe SB si agrega totalurile (struct rd.13-22)."""
    asociati = manual.get("asociati") or []
    sb = []
    for a in asociati:
        impD = _i(a.get("imp_datorat"))
        impR = 0 if luna in (3, 6, 9) else _i(a.get("imp_declarat"))
        difPR = (impD - impR) if luna == 12 else 0
        sb.append({
            "den1": a.get("den"), "cif1": _cif(a.get("cif")), "adresa1": a.get("adresa"),
            "cota": _cota(a.get("cota") or 0), "venit": _i(a.get("venit")), "chelt": _i(a.get("chelt")),
            "impD": impD, "impR": impR, "difPR": difPR,
        })
    profit_pierd = _i(manual.get("profit_pierd"))
    tven = sum(s["venit"] for s in sb)
    tchelt = sum(s["chelt"] for s in sb)
    timpd = sum(s["impD"] for s in sb)
    timpr = sum(s["impR"] for s in sb)
    tdifp = sum(s["difPR"] for s in sb if s["difPR"] > 0)
    tdifr = sum(s["difPR"] for s in sb if s["difPR"] < 0)
    total = profit_pierd + timpd + timpr + tdifp + tdifr
    return {"SB": sb, "profit_pierd": profit_pierd, "Tven": tven, "Tchelt": tchelt, "TimpD": timpd,
            "TimpR": timpr, "TdifP": tdifp, "TdifR": tdifr, "totalPlata_A": total}


def pull(conn, schema, perioada):
    """Declarantul (reprezentantul) + identitatea asocierii (fallback din firma_profil daca profilul E
    asocierea; altfel se dau prin manual['asociere'])."""
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    adresa = " ".join(x for x in (r[2], r[3], r[4]) if x)
    return {"den": r[0], "cui": r[1], "adresa": adresa, "declarant_nume": r[5],
            "declarant_prenume": r[6], "declarant_functie": r[7], "telefon": r[8], "email": r[9]}


def _asociere(prof, manual):
    """Datele asocierii: manual['asociere'] daca e dat, altfel fallback pe firma_profil."""
    a = dict(manual.get("asociere") or {})
    return {"cui": a.get("cui") or prof.get("cui"), "den": a.get("den") or prof.get("den"),
            "adresa": a.get("adresa") or prof.get("adresa")}


def erori_generare(prof, luna, manual):
    er = []
    if luna not in _LUNI_VALIDE:
        er.append("D104: luna de raportare %r invalidă (trim -> 3/6/9/12)." % luna)
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("LIPSĂ %s (declarant obligatoriu)." % c)
    aso = _asociere(prof, manual)
    if not _cif(aso.get("cui")):
        er.append("CUI asociere lipsă/invalid (manual.asociere.cui sau firma_profil).")
    if not str(aso.get("den") or "").strip():
        er.append("LIPSĂ denumire asociere.")
    if not str(aso.get("adresa") or "").strip():
        er.append("LIPSĂ adresa asociere.")
    if manual.get("profit_pierd") is None:
        er.append("D104 cere profit_pierd (profit impozabil(+)/pierdere(-) al asocierii; input contabil).")
    asociati = manual.get("asociati") or []
    if not asociati:
        er.append("D104 cere cel puțin un asociat (asociati[]).")
    cifuri = []
    for i, a in enumerate(asociati, 1):
        if not str(a.get("den") or "").strip():
            er.append("Asociat %d: lipsă denumire/nume (den1)." % i)
        cf = _cif(a.get("cif"))
        if not cf:
            er.append("Asociat %d: lipsă cod de identificare fiscala (cif1)." % i)
        else:
            cifuri.append(cf)
        try:
            cota = _cota(a.get("cota") or 0)
        except Exception:
            cota = Decimal(0)
        if not (Decimal(0) < cota <= Decimal(100)):
            er.append("Asociat %d: cota %s invalida (0<cota<=100)." % (i, a.get("cota")))
        for camp in ("venit", "chelt", "imp_datorat"):
            if _i(a.get(camp)) < 0:
                er.append("Asociat %d: %s trebuie >= 0." % (i, camp))
    if len(cifuri) != len(set(cifuri)):
        er.append("Asociații au cif1 duplicat (cif1 = cheie unica per SB).")
    return er


def build_xml(prof, an, luna, manual, calc):
    aso = _asociere(prof, manual)
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('nume_declar="%s"' % _esc(prof.get("declarant_nume"), 75))
    a.append('prenume_declar="%s"' % _esc(prof.get("declarant_prenume"), 75))
    a.append('functie_declar="%s"' % _esc(prof.get("declarant_functie"), 50))
    a.append('cui="%s"' % _cif(aso.get("cui")))
    a.append('den="%s"' % _esc(aso.get("den"), 200))
    a.append('adresa="%s"' % _esc(aso.get("adresa"), 1000))
    if prof.get("telefon"):
        a.append('telefon="%s"' % _esc(prof.get("telefon"), 15))
    if prof.get("email"):
        a.append('mail="%s"' % _esc(prof.get("email"), 200))
    a.append('Tven="%d"' % calc["Tven"])
    a.append('Tchelt="%d"' % calc["Tchelt"])
    a.append('profit_pierd="%d"' % calc["profit_pierd"])
    a.append('TimpD="%d"' % calc["TimpD"])
    a.append('TimpR="%d"' % calc["TimpR"])
    a.append('TdifP="%d"' % calc["TdifP"])
    a.append('TdifR="%d"' % calc["TdifR"])
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<declaratie104 xmlns="%s" %s>' % (NS, " ".join(a))]
    for s in calc["SB"]:
        cota = s["cota"]
        cota_s = ("%d" % cota) if cota == cota.to_integral_value() else ("%s" % cota)
        ba = ['den1="%s"' % _esc(s["den1"], 100), 'cif1="%s"' % s["cif1"]]
        if str(s.get("adresa1") or "").strip():
            ba.append('adresa1="%s"' % _esc(s["adresa1"], 1000))
        ba += ['cota="%s"' % cota_s, 'venit="%d"' % s["venit"], 'chelt="%d"' % s["chelt"],
               'impD="%d"' % s["impD"], 'impR="%d"' % s["impR"], 'difPR="%d"' % s["difPR"]]
        linii.append('  <SB %s/>' % " ".join(ba))
    linii.append('</declaratie104>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    luna = _luna(perioada)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, luna, manual)
    if er:
        raise ValueError("D104 nu se poate genera: " + " ".join(er))
    calc = calcul_d104(luna, manual)
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat104(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_asociati=len(calc["SB"]))
    return xml, res
