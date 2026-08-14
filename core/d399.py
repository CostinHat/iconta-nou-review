"""core/d399.py — D399: Declaratie speciala de TVA pentru regimul special de import (IOSS).

Declaratia se depune de persoana impozabila (sau intermediarul) inregistrata in Romania pentru
regimul special prevazut la art. 315^2 din Codul fiscal (Legea 227/2015, articol introdus prin
Legea 33/2024, MO 179/05.03.2024) - regimul de import "Import One Stop Shop" (IOSS) pentru vanzari
la distanta de bunuri importate din teritorii/tari terte in loturi de maximum 150 euro. Sumele se
declara in EURO. Romania este statul membru de identificare (MSID).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D399Validator.jar, DUKIntegrator - arbitrul peste anexe).
Schema (namespace declaratie:v1, pachet d399validator/v0) a fost CITITA din bytecode-ul validatorului
(clasele Declaratie399 / MSEST / MSCON) si PROBATA camp cu camp:
  - radacina `declaratie399` (atribute): year (2015..2100), quarter (1..4), correction (0/1),
    nil_vat_return (0/1), period_start_date/period_end_date (optionale, ambele nule sau ambele
    completate), vat_return_reference (obligatoriu doar la rectificativa), moss_voes (RO/EU),
    currency (EUR), vat_id_num, name, address, phone (opt), email (opt), family_name, first_name,
    title, grand_total, grand_total_msid, grand_total_msest.
    ATENTIE: perioada de raportare este TRIMESTRUL (`quarter`); validatorul deriva intern luna =
    quarter*3, deci NU exista atribut XML `month`.
  - MSEST (stat membru de stabilire), atribute: fix_est, vat_id_num_fe. Contine elemente MSCON.
    Pentru moss_voes='EU' atributul fix_est trebuie sa fie '99'.
  - MSCON (stat membru de consum), atribute: mscon_state, vat_rate_type (0=standard, 1=redusa),
    vat_rate, taxable_amount, vat_amount.

Reguli citite din validator (probate), prefix "DUK regula <cod>":
  - DUK regula R31.2: vat_amount = round_half_up(vat_rate * taxable_amount / 100, 2) (setScale(2, HALF_UP)).
  - DUK regula R30 / R31.1: taxable_amount <> 0 si vat_amount <> 0.
  - DUK regula R29.1: vat_rate in intervalul (0, 100].
  - DUK regula R29.2: vat_rate trebuie sa apartina listei de cote a statului de consum (verificare
    server-side, ANAF; cota NU se hardcodeaza aici - vine din `manual`).
  - DUK regula R27.1: fix_est <> mscon_state. R27.2: mscon_state <> 'RO' cand moss_voes = 'RO'.
  - grand_total = grand_total_msid + grand_total_msest; grand_total_msid = suma vat_amount pentru
    fix_est = 'RO'; grand_total_msest = suma vat_amount pentru fix_est <> 'RO'.
  - nil_vat_return = 1 <=> nu exista niciun MSEST (declaratie pe zero); = 0 <=> exista prestari.
  - correction = 0 => vat_return_reference gol; correction = 1 => vat_return_reference completat.
  - pentru moss_voes/fix_est = 'RO' (sau moss_voes = 'EU'): vat_id_num = vat_id_num_fe.
  - tripletul (mscon_state, vat_rate_type, vat_rate) unic in cadrul unui MSEST; fix_est unic in declaratie.

Cotele de TVA NU se hardcodeaza (vin din `manual` per linie). Rotunjire half-up prin Decimal.quantize.

NEPOPULAT deliberat (optional in schema, semantica nedeterminata din act, nu se ghiceste):
  period_start_date / period_end_date (ambele nule => verificarea de incadrare in perioada nu se
  aplica). Se completeaza la nevoie prin manual['period_start_date']/['period_end_date'].

Contract dXXX: pull/erori_generare/calcul_d399/build_xml/genereaza(conn, schema, perioada, manual).
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d399:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_TWO = Decimal("0.01")


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _dec(x):
    """Decimal tolerant la virgula/spatii; ridica ValueError daca nu e numeric."""
    s = str("" if x is None else x).replace(",", ".").replace(" ", "").strip()
    if s == "":
        raise ValueError("valoare numerica lipsa")
    return Decimal(s)


def _q2(d):
    """Rotunjire half-up la 2 zecimale (setScale(2, HALF_UP) al validatorului)."""
    return d.quantize(_TWO, rounding=ROUND_HALF_UP)


def _fmt(d):
    """Format zecimal fix cu 2 zecimale (ex: 19.00), scala potrivita cu suma din validator."""
    return "{:.2f}".format(_q2(Decimal(d)))


def _quarter_din_luna(luna):
    """Perioada de raportare = trimestrul care contine luna data (validatorul deriva luna=quarter*3)."""
    return (int(luna) - 1) // 3 + 1


@dataclass
class Linie399:
    fix_est: str
    vat_id_num_fe: str
    mscon_state: str
    vat_rate_type: int
    vat_rate: Decimal
    taxable_amount: Decimal
    vat_amount: Decimal


@dataclass
class Rezultat399:
    an: int
    trimestru: int
    nil_vat_return: int
    grand_total: str = "0.00"
    grand_total_msid: str = "0.00"
    grand_total_msest: str = "0.00"
    nr_linii: int = 0
    avertismente: list = field(default_factory=list)


def _linii(manual):
    """Normalizeaza prestarile din manual['prestari'] (sau 'linii') in Linie399, cu vat_amount calculat."""
    brute = manual.get("prestari") or manual.get("linii") or []
    out = []
    for r in brute:
        rate = _dec(r.get("vat_rate"))
        baza = _dec(r.get("taxable_amount"))
        vat = _q2(rate * baza / Decimal(100))  # DUK regula R31.2
        out.append(Linie399(
            fix_est=str(r.get("fix_est") or "RO").strip().upper(),
            vat_id_num_fe=str(r.get("vat_id_num_fe") or "").strip(),
            mscon_state=str(r.get("mscon_state") or "").strip().upper(),
            vat_rate_type=int(r.get("vat_rate_type", 0)),
            vat_rate=rate,
            taxable_amount=baza,
            vat_amount=vat,
        ))
    return out


def calcul_d399(manual):
    """Agregate grand_total (= msid + msest), grand_total_msid (fix_est='RO'), grand_total_msest (rest)."""
    linii = _linii(manual)
    msid = sum((l.vat_amount for l in linii if l.fix_est == "RO"), Decimal(0))
    msest = sum((l.vat_amount for l in linii if l.fix_est != "RO"), Decimal(0))
    return {
        "grand_total": _fmt(msid + msest),
        "grand_total_msid": _fmt(msid),
        "grand_total_msest": _fmt(msest),
        "nil_vat_return": 0 if linii else 1,
        "nr_linii": len(linii),
    }


def pull(conn, schema, perioada):
    """D399 (IOSS) declara vanzari la distanta pe stat de consum, care aplicatia nu le tine pe schema
    contabila standard; datele vin din `manual`. Contractul cere `pull`. Sigur la conn=None."""
    return {}


def erori_generare(prof, manual):
    er = []
    moss = str(manual.get("moss_voes") or "RO").strip().upper()
    if moss not in ("RO", "EU"):
        er.append("moss_voes trebuie sa fie 'RO' sau 'EU'.")
    if not str(manual.get("vat_id_num") or manual.get("cui") or "").strip():
        er.append("Lipsa vat_id_num (codul de inregistrare pentru regimul special).")
    if not str(manual.get("name") or manual.get("denumire") or "").strip():
        er.append("Lipsa name (denumire persoana impozabila).")
    if not str(manual.get("address") or manual.get("adresa") or "").strip():
        er.append("Lipsa address (adresa).")
    if not str(manual.get("family_name") or "").strip():
        er.append("Lipsa family_name (nume semnatar).")
    if not str(manual.get("first_name") or "").strip():
        er.append("Lipsa first_name (prenume semnatar).")
    if not str(manual.get("title") or "").strip():
        er.append("Lipsa title (functie semnatar).")
    try:
        corr = int(manual.get("correction", 0))
    except (TypeError, ValueError):
        corr = -1
    if corr not in (0, 1):
        er.append("correction trebuie sa fie 0 (initiala) sau 1 (rectificativa).")
    if corr == 1 and not str(manual.get("vat_return_reference") or "").strip():
        er.append("vat_return_reference obligatoriu la rectificativa (DUK regula: correction=1).")
    vat_id = str(manual.get("vat_id_num") or manual.get("cui") or "").strip()
    try:
        linii = _linii(manual)
    except (ValueError, ArithmeticError) as e:
        er.append("Prestare cu valoare numerica invalida (vat_rate/taxable_amount): %s" % e)
        linii = []
    seen_fix = set()
    for i, l in enumerate(linii, 1):
        et = "prestarea %d" % i
        if not l.mscon_state:
            er.append("%s: lipsa mscon_state." % et)
        if l.fix_est == l.mscon_state:
            er.append("%s: fix_est = mscon_state (DUK regula R27.1)." % et)
        if moss == "RO" and l.mscon_state == "RO":
            er.append("%s: mscon_state nu poate fi 'RO' cand moss_voes='RO' (DUK regula R27.2)." % et)
        if moss == "EU" and l.fix_est != "99":
            er.append("%s: pentru moss_voes='EU' fix_est trebuie sa fie '99'." % et)
        if l.vat_rate_type not in (0, 1):
            er.append("%s: vat_rate_type trebuie 0 (standard) sau 1 (redusa)." % et)
        if not (Decimal(0) < l.vat_rate <= Decimal(100)):
            er.append("%s: vat_rate in afara intervalului (0,100] (DUK regula R29.1)." % et)
        if l.taxable_amount == 0:
            er.append("%s: taxable_amount nu poate fi 0 (DUK regula R30)." % et)
        if l.vat_amount == 0:
            er.append("%s: vat_amount nu poate fi 0 (DUK regula R31.1)." % et)
        if (moss == "EU" or l.fix_est == "RO") and l.vat_id_num_fe and l.vat_id_num_fe != vat_id:
            er.append("%s: pentru fix_est='RO'/moss_voes='EU' vat_id_num_fe trebuie = vat_id_num." % et)
        key = (l.fix_est, l.mscon_state, l.vat_rate_type, str(l.vat_rate))
        if key in seen_fix:
            er.append("%s: triplet (mscon_state, vat_rate_type, vat_rate) duplicat in MSEST." % et)
        seen_fix.add(key)
    return er


def _grup_msest(linii, vat_id):
    """Grupeaza liniile pe fix_est (un MSEST per stat de stabilire), pastrand ordinea."""
    grupuri = {}
    for l in linii:
        fe = l.vat_id_num_fe or (vat_id if l.fix_est == "RO" else "")
        grupuri.setdefault((l.fix_est, fe), []).append(l)
    return grupuri


def build_xml(prof, an, trimestru, manual):
    moss = str(manual.get("moss_voes") or "RO").strip().upper()
    currency = str(manual.get("currency") or "EUR").strip().upper()
    corr = int(manual.get("correction", 0))
    vat_id = str(manual.get("vat_id_num") or manual.get("cui") or "").strip()
    ag = calcul_d399(manual)
    linii = _linii(manual)

    a = []
    a.append('year="%d"' % int(an))
    a.append('quarter="%d"' % int(trimestru))
    a.append('correction="%d"' % corr)
    a.append('nil_vat_return="%d"' % ag["nil_vat_return"])
    ps = str(manual.get("period_start_date") or "").strip()
    pe = str(manual.get("period_end_date") or "").strip()
    if ps and pe:
        a.append('period_start_date="%s"' % _esc(ps))
        a.append('period_end_date="%s"' % _esc(pe))
    if corr == 1:
        a.append('vat_return_reference="%s"' % _esc(manual.get("vat_return_reference"), 22))
    a.append('moss_voes="%s"' % _esc(moss, 4))
    a.append('currency="%s"' % _esc(currency, 4))
    a.append('vat_id_num="%s"' % _esc(vat_id, 20))
    a.append('name="%s"' % _esc(manual.get("name") or manual.get("denumire"), 200))
    a.append('address="%s"' % _esc(manual.get("address") or manual.get("adresa"), 1000))
    if manual.get("phone") or manual.get("telefon"):
        a.append('phone="%s"' % _esc(manual.get("phone") or manual.get("telefon"), 15))
    if manual.get("email"):
        a.append('email="%s"' % _esc(manual.get("email"), 200))
    a.append('family_name="%s"' % _esc(manual.get("family_name"), 75))
    a.append('first_name="%s"' % _esc(manual.get("first_name"), 75))
    a.append('title="%s"' % _esc(manual.get("title"), 50))
    a.append('grand_total="%s"' % ag["grand_total"])
    a.append('grand_total_msid="%s"' % ag["grand_total_msid"])
    a.append('grand_total_msest="%s"' % ag["grand_total_msest"])

    corp = []
    for (fix_est, fe), grup in _grup_msest(linii, vat_id).items():
        m = ['fix_est="%s"' % _esc(fix_est, 4)]
        if fe:
            m.append('vat_id_num_fe="%s"' % _esc(fe, 12))
        corp.append('  <MSEST %s>' % " ".join(m))
        for l in grup:
            corp.append('    <MSCON mscon_state="%s" vat_rate_type="%d" vat_rate="%s" '
                        'taxable_amount="%s" vat_amount="%s"/>'
                        % (_esc(l.mscon_state, 4), l.vat_rate_type, _fmt(l.vat_rate),
                           _fmt(l.taxable_amount), _fmt(l.vat_amount)))
        corp.append('  </MSEST>')
    corp_xml = ("\n" + "\n".join(corp) + "\n") if corp else ""

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie399 xmlns="%s" %s>%s</declaratie399>\n'
            % (NS, " ".join(a), corp_xml))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an = int(perioada.an)
    trimestru = int(manual.get("quarter") or _quarter_din_luna(perioada.luna))
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D399 nu se poate genera: " + " ".join(er))
    ag = calcul_d399(manual)
    xml = build_xml(prof, an, trimestru, manual)
    res = Rezultat399(an=an, trimestru=trimestru, nil_vat_return=ag["nil_vat_return"],
                      grand_total=ag["grand_total"], grand_total_msid=ag["grand_total_msid"],
                      grand_total_msest=ag["grand_total_msest"], nr_linii=ag["nr_linii"])
    return xml, res
