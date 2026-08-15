"""core/d110.py — D110: Declaratie de regularizare / cerere de restituire privind impozitul pe venit retinut la sursa.

Platitorul de venit regularizeaza impozitul retinut la sursa (compara datorat vs retinut) si, optional, cere
restituirea diferentei retinute in plus. Per obligatie: suma_dat vs suma_rest -> dif_plata (de plata) sau
dif_rest (de restituit). Declaratie MANUALA - obligatiile vin din input.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D110Validator.jar). _dateVersionTable o singura linie
("2014-01 J1.0.3 0", publicata 2026-03-27) -> sub-pachet v0, DAR namespace XML :v1. Radacina <D110> (MAJUSCULE).
  <D110>: luna, an, d_rec, d_temei, IBAN, banca, nume_declar, prenume_declar, functie_declar, cif, den, adresa,
    telefon, fax, mail, totalPlata_A.
  <obligatie> (1-n): cod_oblig, cod_bugetar, scadenta, nr_evid, suma_dat, suma_rest, dif_plata, dif_rest.

SEMANTICA/REGULI din ACT (anaf_surse/structura_D110_2026_240326 + d110_20260330.xsd; CPF L207/2015 art.168,170;
CF titlurile II/III; coduri obligatie nomenclator):
  - d_temei=0 -> Sigma(dif_rest)=0, IBAN si banca null; d_temei=1 -> Sigma(dif_rest)!=0, IBAN+banca completate.
  - totalPlata_A = Sigma(dif_plata + dif_rest).
  - Per obligatie: suma_dat>=0; suma_rest>0 STRICT; daca suma_dat>=suma_rest -> dif_plata=suma_dat-suma_rest,
    dif_rest=0; altfel dif_rest=suma_rest-suma_dat, dif_plata=0. cod_oblig unic per declaratie.
  - cod_bugetar = "5503XXXXXX" (X-uri LITERALE), exceptand cod_oblig=629 -> "20A031800X".
  - scadenta = 25 a lunii urmatoare perioadei (D(10) ZZ.LL.AAAA).
  - nr_evid (23 caractere): "10" + cod_oblig(3) + "01" + LLAA(perioada) + "25"+LLAA(scadenta) + "0000" +
    control(2), unde control = suma primelor 21 cifre % 100 (CONFIRMAT empiric pe DUKIntegrator).
  - cod_oblig ∈ nomenclator (604,605,606,608,621,690,631..642,628,629,602,611,622,623,619,626,607,625,627).

Contract dXXX: pull/erori_generare/calcul_d110/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

from core.numere import numar_fiscal

NS = "mfp:anaf:dgti:d110:declaratie:v1"
_NEDIGIT = re.compile(r"\D")

_COD_OBLIG_VALIDE = {"604", "605", "606", "608", "621", "690", "631", "632", "633", "634", "635", "636",
                     "637", "638", "639", "640", "641", "642", "628", "629", "602", "611", "622", "623",
                     "619", "626", "607", "625", "627"}


def _i(x, camp="D110"):
    if x in (None, ""):
        return 0
    return int(numar_fiscal(x, camp).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _cod_bugetar(cod_oblig):
    return "20A031800X" if str(cod_oblig) == "629" else "5503XXXXXX"


def _scadenta_luna_an(luna, an):
    m, y = int(luna) + 1, int(an)
    if m > 12:
        m -= 12
        y += 1
    return m, y


def _nr_evid(cod_oblig, luna, an, scad_luna, scad_an):
    """nr_evid 23 caractere; control = suma primelor 21 cifre % 100 (confirmat pe DUKIntegrator)."""
    p = ("10" + str(cod_oblig).zfill(3) + "01" + "%02d%02d" % (int(luna), int(an) % 100)
         + "25" + "%02d%02d" % (int(scad_luna), int(scad_an) % 100) + "0000")
    ctrl = sum(int(c) for c in p) % 100
    return p + "%02d" % ctrl


@dataclass
class Rezultat110:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_obligatii: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d110(luna, an, manual):
    obl = []
    for o in manual.get("obligatii") or []:
        cod = str(o.get("cod_oblig") or "").strip()
        suma_dat = _i(o.get("suma_dat"))
        suma_rest = _i(o.get("suma_rest"))
        if suma_dat >= suma_rest:
            dif_plata, dif_rest = suma_dat - suma_rest, 0
        else:
            dif_plata, dif_rest = 0, suma_rest - suma_dat
        sl, sy = _scadenta_luna_an(luna, an)
        obl.append({"cod_oblig": cod, "cod_bugetar": _cod_bugetar(cod),
                    "scadenta": "25.%02d.%04d" % (sl, sy), "nr_evid": _nr_evid(cod, luna, an, sl, sy),
                    "suma_dat": suma_dat, "suma_rest": suma_rest, "dif_plata": dif_plata, "dif_rest": dif_rest})
    total = sum(o["dif_plata"] + o["dif_rest"] for o in obl)
    return {"obligatii": obl, "totalPlata_A": total, "sigma_dif_rest": sum(o["dif_rest"] for o in obl)}


def pull(conn, schema, perioada):
    with conn.cursor() as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, declarant_nume, declarant_prenume, "
                    "declarant_functie, telefon, email, iban, banca FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
    if not r:
        return {}
    adresa = " ".join(x for x in (r[2], r[3], r[4]) if x)
    return {"den": r[0], "cui": r[1], "adresa": adresa, "declarant_nume": r[5], "declarant_prenume": r[6],
            "declarant_functie": r[7], "telefon": r[8], "email": r[9], "iban": r[10], "banca": r[11]}


def erori_generare(prof, manual, calc):
    er = []
    if not _cif(prof.get("cui")):
        er.append("CUI platitor lipsa/invalid.")
    if not str(prof.get("den") or "").strip():
        er.append("LIPSA denumire.")
    if not str(prof.get("adresa") or "").strip():
        er.append("LIPSA adresa.")
    for c in ("declarant_nume", "declarant_prenume", "declarant_functie"):
        if not str(prof.get(c) or "").strip():
            er.append("LIPSA %s (declarant obligatoriu)." % c)
    obl = manual.get("obligatii") or []
    if not obl:
        er.append("D110 cere cel putin o obligatie (obligatii[]).")
    coduri = []
    for i, o in enumerate(obl, 1):
        cod = str(o.get("cod_oblig") or "").strip()
        if cod not in _COD_OBLIG_VALIDE:
            er.append("Obligatie %d: cod_oblig %r negasit in nomenclator." % (i, cod))
        else:
            coduri.append(cod)
        if _i(o.get("suma_dat")) < 0:
            er.append("Obligatie %d: suma_dat trebuie >= 0." % i)
        if _i(o.get("suma_rest")) <= 0:
            er.append("Obligatie %d: suma_rest trebuie > 0 (strict)." % i)
    if len(coduri) != len(set(coduri)):
        er.append("cod_oblig duplicat (unic per declaratie).")
    d_temei = int(manual.get("d_temei") or 0)
    if d_temei == 1:
        if calc["sigma_dif_rest"] == 0:
            er.append("d_temei=1 (cerere restituire) dar nicio diferenta de restituit (suma dif_rest=0).")
        if not str(manual.get("iban") or prof.get("iban") or "").strip():
            er.append("d_temei=1 cere IBAN (pentru restituire).")
        if not str(manual.get("banca") or prof.get("banca") or "").strip():
            er.append("d_temei=1 cere banca (pentru restituire).")
    else:
        if calc["sigma_dif_rest"] != 0:
            er.append("d_temei=0 dar exista diferente de restituit (suma dif_rest!=0); seteaza d_temei=1 + IBAN/banca.")
    return er


def build_xml(prof, an, luna, manual, calc):
    d_temei = int(manual.get("d_temei") or 0)
    a = []
    a.append('luna="%d"' % int(luna))
    a.append('an="%d"' % int(an))
    a.append('d_rec="%d"' % int(manual.get("d_rec") or 0))
    a.append('d_temei="%d"' % d_temei)
    if d_temei == 1:
        a.append('IBAN="%s"' % _esc(manual.get("iban") or prof.get("iban"), 24))
        a.append('banca="%s"' % _esc(manual.get("banca") or prof.get("banca"), 1000))
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
    a.append('totalPlata_A="%d"' % calc["totalPlata_A"])
    linii = ['<D110 xmlns="%s" %s>' % (NS, " ".join(a))]
    for o in calc["obligatii"]:
        oa = ['cod_oblig="%s"' % o["cod_oblig"], 'cod_bugetar="%s"' % o["cod_bugetar"],
              'scadenta="%s"' % o["scadenta"], 'nr_evid="%s"' % o["nr_evid"],
              'suma_dat="%d"' % o["suma_dat"], 'suma_rest="%d"' % o["suma_rest"],
              'dif_plata="%d"' % o["dif_plata"], 'dif_rest="%d"' % o["dif_rest"]]
        linii.append('  <obligatie %s/>' % " ".join(oa))
    linii.append('</D110>')
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    calc = calcul_d110(luna, an, manual)
    er = erori_generare(prof, manual, calc)
    if er:
        raise ValueError("D110 nu se poate genera: " + " ".join(er))
    xml = build_xml(prof, an, luna, manual, calc)
    res = Rezultat110(an=an, luna=luna, total_plata_a=calc["totalPlata_A"], nr_obligatii=len(calc["obligatii"]))
    return xml, res
