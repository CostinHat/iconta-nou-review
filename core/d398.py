"""core/d398.py — D398: Declaratie speciala de TVA pentru regimurile speciale UE / non-UE / import (OSS - One Stop Shop).

Declaratie MANUALA (nu se deduce din registrele contabile ale firmei): contribuabilul inregistrat in unul din
regimurile speciale OSS raporteaza, prin statul membru de identificare (Romania), TVA-ul datorat in fiecare stat
membru de consum pentru vanzari la distanta / prestari de servicii catre persoane neimpozabile din UE. Aplicatia
nu tine evidenta operatiunilor OSS pe stat de consum si cota straina, asa ca TOATE valorile vin din `manual`.

BAZA LEGALA: Codul fiscal (Legea 227/2015) art. 314 (regimul non-UE pentru servicii), art. 315 (regimul UE) si
art. 315^2 (regimul de import - IOSS), transpunere a Titlului XII cap. 6 din Directiva 2006/112/CE. Normele sunt
in anaf_surse/hg_1_2016_norme_cod_fiscal.html (art. 314-315 prezente). OPANAF specific de aprobare a modelului D398
nu exista in anaf_surse; nu a fost descarcat pentru ca ARBITRUL structurii este validatorul oficial ANAF.

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D398Validator.jar, validator de GENERATIE NOUA - probare cu
DecValidation prin general.Main, nu prin -jar clasic). Radacina si campurile au fost CITITE din bytecode
(clasele d398validator.v0.{D398,MS,SUPPLY,CORRECTION}) si PROBATE camp cu camp pe validator pana la VALID:
  - Radacina XML: <d398> (element lowercase), namespace mfp:anaf:dgti:d398:declaratie:v1.
  - Ierarhie (contexte 0 / 01 / 012 / 03): d398 > MS (0..n) > SUPPLY (1..n); d398 > CORRECTION (0..n).
  - Atribute D398 (numele XML difera de campul intern): an_r (=_year), luna_r (=_vat_return_period), d_rec,
    totalPlata_A, moes_voes_imp, e_int, period_start_date, period_end_date, nil_vat_return, currency,
    vat_id_no, intermediary_id, name, grand_total_vat_due, vat_return_reference.
  - Atribute MS: mscon_state, grand_total, vat_total_services_msid, vat_total_goods_msid,
    vat_total_services_msest, vat_total_goods_msest, due_balance.
  - Atribute SUPPLY: trade_type, vat_id_no_msest, supply_type, vat_rate_type, vat_rate, taxable_amount, vat_amount.
  - Atribute CORRECTION: mscon_state_correction, vat_return_correction_period, year, vat_amount_correction.

moes_voes_imp = regimul special (numeric): 1 = regim UE (art. 315, bunuri + servicii, admite stabiliri fixe
msest), 2 = regim non-UE (art. 314, doar servicii, doar msid), 3 = regim de import IOSS (art. 315^2, doar bunuri).

Reguli citite din validator si PROBATE (prefix "DUK regula <cod>"):
  - DUK regula R5.1: e_int obligatoriu cand moes_voes_imp=1.
  - DUK regula R10: vat_id_no trebuie sa fie un cod de TVA valid (pt regim UE = cod RO valabil).
  - DUK regula R6.1: period_start_date si period_end_date simultan nule sau nenule.
  - DUK regula R13.1: grand_total_vat_due=0 daca nil_vat_return=1.
  - DUK regula R13.2: grand_total_vat_due = suma peste statele de consum a max(due_balance, 0).
  - DUK regula R21: due_balance (per stat) = grand_total(stat) + suma vat_amount_correction pe acelasi stat.
  - DUK regula R16: grand_total = vat_total_services_msid + vat_total_goods_msid + vat_total_services_msest + vat_total_goods_msest.
  - DUK regula R18/R17/R20/R19: vat_total_{goods_msid / services_msid / goods_msest / services_msest} = suma vat_amount pe (supply_type, trade_type) = (1,1)/(2,1)/(1,2)/(2,2).
  - DUK regula R22: daca exista MS trebuie sa existe cel putin un SUPPLY; DUK regula R14: mscon_state unic per MS.
  - DUK regula R23: msest (trade_type=2) doar pentru regim UE (moes_voes_imp=1).
  - DUK regula R24.1 / R24.4: vat_id_no_msest obligatoriu la trade_type=2, interzis la trade_type=1.
  - DUK regula R25.1 / R25.2: bunuri (supply_type=1) interzise in regim non-UE(2); servicii (supply_type=2) interzise in regim import(3).
  - DUK regula R27.1: vat_rate in intervalul (0, 100]; DUK regula R28: taxable_amount strict pozitiv.
  - DUK regula R29: vat_amount = taxable_amount * vat_rate / 100, rotunjit la 2 zecimale (half-up).
  - DUK regula R32: (vat_return_correction_period, year, mscon_state_correction) unic; vat_amount_correction <> 0.

Format probat pe validator: date calendaristice "dd.MM.yyyy"; sume monetare cu 2 zecimale si punct zecimal.

NEPOPULAT deliberat (optionale, semantica nedeterminata fara input de la utilizator): intermediary_id (doar
regim import cu intermediar), vat_return_reference (referinta declaratiei rectificate). NU se ghicesc cotele de
TVA - vin din `manual`, per stat de consum. D398 nu depinde de conn (conn=None merge; pull() intoarce {}).

Contract dXXX: pull / erori_generare / calcul_d398 / build_xml / genereaza(conn, schema, perioada, manual).
"""

#: [07.09.2026] denumirea OFICIALA (cu diacritice) - se afiseaza pe ecranul public,
#: derivata de scripts/genereaza_declaratii_lista.py. Corectura ORTOGRAFICA peste
#: denumirea deja consemnata in modul; NU o re-verificare la ANAF.
DENUMIRE_OFICIALA = 'Declarație specială de TVA pentru regimurile speciale UE / non-UE / import (OSS)'
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
import re

NS = "mfp:anaf:dgti:d398:declaratie:v1"
_D2 = Decimal("0.01")
_DATA_OK = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
_STAT_OK = re.compile(r"^[A-Z]{2}$")
SCHEME_UE, SCHEME_NONUE, SCHEME_IMP = 1, 2, 3


def _esc(s, lim=None):
    t = ("" if s is None else str(s)).replace("&", "&amp;").replace("<", "&lt;") \
        .replace(">", "&gt;").replace('"', "&quot;").strip()
    return t[:lim] if lim else t


def _dec(x):
    """Decimal robust dintr-un input int/float/str (virgula sau punct)."""
    if x is None or x == "":
        return Decimal("0")
    return Decimal(str(x).replace(",", ".").strip())


def _bani(x):
    """Suma monetara: 2 zecimale, rotunjire half-up (DUK regula R29 pentru vat_amount)."""
    return _dec(x).quantize(_D2, rounding=ROUND_HALF_UP)


def _fbani(x):
    """Format monetar cu 2 zecimale si punct (ex. '190.50', '0.00')."""
    return format(_bani(x), "f")


def _frate(x):
    """Cota de TVA: 2 zecimale, fara zerouri inutile. Cotele vin din `manual`, nu hardcodate."""
    q = _dec(x).quantize(_D2, rounding=ROUND_HALF_UP)
    s = format(q, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def _int(x, implicit=None):
    try:
        return int(str(x).strip())
    except (TypeError, ValueError):
        return implicit


@dataclass
class Rezultat398:
    an: int
    luna: int
    moes_voes_imp: int = 0
    nil_vat_return: int = 0
    grand_total_vat_due: str = "0.00"
    nr_state: int = 0
    nr_corectii: int = 0
    avertismente: list = field(default_factory=list)


def _supply_vat(sup):
    """vat_amount = taxable_amount * vat_rate / 100 rotunjit la 2 zecimale half-up (DUK regula R29)."""
    return _bani(_dec(sup.get("taxable_amount")) * _dec(sup.get("vat_rate")) / Decimal("100"))


def calcul_d398(manual):
    """Agregarile impuse de validator (DUK reguli R16/R17/R18/R19/R20/R21/R13.2).

    Intoarce: {ms: [...cu totaluri...], corrections: [...], grand_total_vat_due, nil_vat_return, totalPlata_A}.
    """
    ms_in = manual.get("ms") or []
    cor_in = manual.get("corrections") or []

    # Corectii grupate pe stat (DUK regula R21: due_balance include suma corectiilor pe acel stat)
    cor_pe_stat = {}
    corrections = []
    for c in cor_in:
        stat = _esc(c.get("mscon_state") or c.get("mscon_state_correction")).upper()
        val = _bani(c.get("vat_amount") if c.get("vat_amount") is not None else c.get("vat_amount_correction"))
        cor_pe_stat[stat] = cor_pe_stat.get(stat, Decimal("0")) + val
        corrections.append({
            "mscon_state_correction": stat,
            "vat_return_correction_period": _int(c.get("period") if c.get("period") is not None else c.get("vat_return_correction_period")),
            "year": _int(c.get("year")),
            "vat_amount_correction": _fbani(val),
        })

    ms = []
    due_pe_stat = {}
    for m in ms_in:
        stat = _esc(m.get("mscon_state")).upper()
        supplies = []
        t_goods_msid = t_serv_msid = t_goods_msest = t_serv_msest = Decimal("0")
        for s in (m.get("supplies") or []):
            st = _int(s.get("supply_type"))
            tt = _int(s.get("trade_type"))
            va = _supply_vat(s)
            sup = {
                "trade_type": tt,
                "supply_type": st,
                "vat_rate_type": _int(s.get("vat_rate_type")),
                "vat_rate": _frate(s.get("vat_rate")),
                "taxable_amount": _fbani(s.get("taxable_amount")),
                "vat_amount": _fbani(va),
                "vat_id_no_msest": (_esc(s.get("vat_id_no_msest")).upper() or None) if tt == 2 else None,
            }
            supplies.append(sup)
            if st == 1 and tt == 1:
                t_goods_msid += va
            elif st == 2 and tt == 1:
                t_serv_msid += va
            elif st == 1 and tt == 2:
                t_goods_msest += va
            elif st == 2 and tt == 2:
                t_serv_msest += va
        grand_total = _bani(t_goods_msid + t_serv_msid + t_goods_msest + t_serv_msest)
        due = _bani(grand_total + cor_pe_stat.get(stat, Decimal("0")))
        due_pe_stat[stat] = due
        ms.append({
            "mscon_state": stat,
            "vat_total_goods_msid": _fbani(t_goods_msid),
            "vat_total_services_msid": _fbani(t_serv_msid),
            "vat_total_goods_msest": _fbani(t_goods_msest),
            "vat_total_services_msest": _fbani(t_serv_msest),
            "grand_total": _fbani(grand_total),
            "due_balance": _fbani(due),
            "supplies": supplies,
        })

    # Statele care apar DOAR in corectii (fara MS) contribuie cu propria suma de corectii (DUK regula R21/R13.2)
    for stat, val in cor_pe_stat.items():
        if stat not in due_pe_stat:
            due_pe_stat[stat] = _bani(val)

    # DUK regula R13.2: grand_total_vat_due = suma peste state a max(due_balance, 0)
    gtvd = sum((d for d in due_pe_stat.values() if d > 0), Decimal("0"))
    gtvd = _bani(gtvd)

    # nil_vat_return: fara operatiuni SI fara corectii (o declaratie cu corectii NU e NIL - vezi CORRECTION)
    nil_vat_return = 1 if (not ms and not corrections) else 0
    if nil_vat_return == 1:
        gtvd = Decimal("0.00")

    moes = _int(manual.get("moes_voes_imp"), 0)
    total_plata_a = moes + nil_vat_return  # regula totalPlata_A = moes_voes_imp + nil_vat_return

    return {
        "ms": ms,
        "corrections": corrections,
        "grand_total_vat_due": _fbani(gtvd),
        "nil_vat_return": nil_vat_return,
        "totalPlata_A": total_plata_a,
    }


def pull(conn, schema, perioada):
    """D398 e MANUALA/speciala (OSS): valorile pe stat de consum si cota straina nu exista in registrele firmei.
    Contractul cere `pull`; nu atinge baza de date (conn poate fi None)."""
    return {}


def erori_generare(prof, manual):
    er = []
    moes = _int(manual.get("moes_voes_imp"))
    if moes not in (SCHEME_UE, SCHEME_NONUE, SCHEME_IMP):
        er.append("moes_voes_imp obligatoriu 1 (regim UE) / 2 (regim non-UE) / 3 (regim import).")
    if not _esc(manual.get("name")):
        er.append("Lipsă denumire contribuabil (name).")
    if not _esc(manual.get("vat_id_no")):
        er.append("Lipsă cod de identificare TVA (vat_id_no) - DUK regula R10.")
    if _int(manual.get("an_r")) is None:
        er.append("Lipsă an de raportare (an_r).")
    if _int(manual.get("luna_r")) is None:
        er.append("Lipsă perioada de raportare luna_r - DUK regula R3.")
    if moes == SCHEME_UE and _int(manual.get("e_int")) not in (0, 1):
        er.append("e_int obligatoriu (0/1) cand moes_voes_imp=1 - DUK regula R5.1.")
    ps, pe = _esc(manual.get("period_start_date")), _esc(manual.get("period_end_date"))
    if bool(ps) != bool(pe):
        er.append("period_start_date și period_end_date simultan nule sau nenule - DUK regula R6.1.")
    for d, nume in ((ps, "period_start_date"), (pe, "period_end_date")):
        if d and not _DATA_OK.match(d):
            er.append("%s trebuie în format dd.MM.yyyy." % nume)

    state_vazute = set()
    for i, m in enumerate(manual.get("ms") or [], 1):
        stat = _esc(m.get("mscon_state")).upper()
        if not _STAT_OK.match(stat):
            er.append("MS[%d]: mscon_state invalid (aștept 2 litere)." % i)
        if stat in state_vazute:
            er.append("MS[%d]: mscon_state %s duplicat - DUK regula R14." % (i, stat))
        state_vazute.add(stat)
        supplies = m.get("supplies") or []
        if not supplies:
            er.append("MS[%d] (%s): trebuie cel puțin un SUPPLY - DUK regula R22." % (i, stat))
        for j, s in enumerate(supplies, 1):
            pfx = "MS[%d]/SUPPLY[%d]" % (i, j)
            st = _int(s.get("supply_type"))
            tt = _int(s.get("trade_type"))
            if st not in (1, 2):
                er.append("%s: supply_type obligatoriu 1 (bunuri) / 2 (servicii)." % pfx)
            if tt not in (1, 2):
                er.append("%s: trade_type obligatoriu 1 (msid) / 2 (msest)." % pfx)
            if _int(s.get("vat_rate_type")) is None:
                er.append("%s: vat_rate_type obligatoriu." % pfx)
            rate = _dec(s.get("vat_rate"))
            if not (Decimal("0") < rate <= Decimal("100")):
                er.append("%s: vat_rate în intervalul (0, 100] - DUK regula R27.1." % pfx)
            if _dec(s.get("taxable_amount")) <= 0:
                er.append("%s: taxable_amount strict pozitiv - DUK regula R28." % pfx)
            if st == 1 and moes == SCHEME_NONUE:
                er.append("%s: bunuri interzise în regim non-UE - DUK regula R25.1." % pfx)
            if st == 2 and moes == SCHEME_IMP:
                er.append("%s: servicii interzise în regim import - DUK regula R25.2." % pfx)
            if tt == 2 and moes != SCHEME_UE:
                er.append("%s: msest (trade_type=2) doar în regim UE - DUK regula R23." % pfx)
            if tt == 2 and not _esc(s.get("vat_id_no_msest")):
                er.append("%s: vat_id_no_msest obligatoriu la trade_type=2 - DUK regula R24.1." % pfx)
            if tt == 1 and _esc(s.get("vat_id_no_msest")):
                er.append("%s: vat_id_no_msest interzis la trade_type=1 - DUK regula R24.4." % pfx)

    cor_chei = set()
    for i, c in enumerate(manual.get("corrections") or [], 1):
        stat = _esc(c.get("mscon_state") or c.get("mscon_state_correction")).upper()
        if not _STAT_OK.match(stat):
            er.append("CORRECTION[%d]: mscon_state invalid (2 litere)." % i)
        per = _int(c.get("period") if c.get("period") is not None else c.get("vat_return_correction_period"))
        an_c = _int(c.get("year"))
        if per is None:
            er.append("CORRECTION[%d]: vat_return_correction_period obligatoriu - DUK regula R34." % i)
        if an_c is None:
            er.append("CORRECTION[%d]: year obligatoriu." % i)
        val = c.get("vat_amount") if c.get("vat_amount") is not None else c.get("vat_amount_correction")
        if _dec(val) == 0:
            er.append("CORRECTION[%d]: vat_amount_correction nu poate fi 0 - DUK regula R32." % i)
        cheie = (per, an_c, stat)
        if cheie in cor_chei:
            er.append("CORRECTION[%d]: (period, year, stat) duplicat - DUK regula R32." % i)
        cor_chei.add(cheie)
    return er


def _attr(nume, val):
    return '%s="%s"' % (nume, val)


def build_xml(prof, an, luna, manual):
    calc = calcul_d398(manual)
    moes = _int(manual.get("moes_voes_imp"), 0)
    h = []
    h.append(_attr("an_r", _int(manual.get("an_r"), an)))
    h.append(_attr("luna_r", _int(manual.get("luna_r"), luna)))
    h.append(_attr("d_rec", _int(manual.get("d_rec"), 0)))
    h.append(_attr("moes_voes_imp", moes))
    if _int(manual.get("e_int")) is not None:
        h.append(_attr("e_int", _int(manual.get("e_int"))))
    h.append(_attr("nil_vat_return", calc["nil_vat_return"]))
    if _esc(manual.get("period_start_date")):
        h.append(_attr("period_start_date", _esc(manual.get("period_start_date"))))
        h.append(_attr("period_end_date", _esc(manual.get("period_end_date"))))
    h.append(_attr("currency", _esc(manual.get("currency")) or "EUR"))
    h.append(_attr("vat_id_no", _esc(manual.get("vat_id_no"))))
    if _esc(manual.get("intermediary_id")):
        h.append(_attr("intermediary_id", _esc(manual.get("intermediary_id"))))
    h.append(_attr("name", _esc(manual.get("name"), 200)))
    h.append(_attr("grand_total_vat_due", calc["grand_total_vat_due"]))
    if _esc(manual.get("vat_return_reference")):
        h.append(_attr("vat_return_reference", _esc(manual.get("vat_return_reference"))))
    h.append(_attr("totalPlata_A", calc["totalPlata_A"]))

    linii = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<d398 xmlns="%s" %s>' % (NS, " ".join(h))]
    for m in calc["ms"]:
        ma = [_attr("mscon_state", m["mscon_state"]),
              _attr("grand_total", m["grand_total"]),
              _attr("vat_total_services_msid", m["vat_total_services_msid"]),
              _attr("vat_total_goods_msid", m["vat_total_goods_msid"]),
              _attr("vat_total_services_msest", m["vat_total_services_msest"]),
              _attr("vat_total_goods_msest", m["vat_total_goods_msest"]),
              _attr("due_balance", m["due_balance"])]
        linii.append("  <MS %s>" % " ".join(ma))
        for s in m["supplies"]:
            sa = [_attr("trade_type", s["trade_type"])]
            if s["vat_id_no_msest"]:
                sa.append(_attr("vat_id_no_msest", s["vat_id_no_msest"]))
            sa += [_attr("supply_type", s["supply_type"]),
                   _attr("vat_rate_type", s["vat_rate_type"]),
                   _attr("vat_rate", s["vat_rate"]),
                   _attr("taxable_amount", s["taxable_amount"]),
                   _attr("vat_amount", s["vat_amount"])]
            linii.append("    <SUPPLY %s/>" % " ".join(sa))
        linii.append("  </MS>")
    for c in calc["corrections"]:
        ca = [_attr("mscon_state_correction", c["mscon_state_correction"]),
              _attr("vat_return_correction_period", c["vat_return_correction_period"]),
              _attr("year", c["year"]),
              _attr("vat_amount_correction", c["vat_amount_correction"])]
        linii.append("  <CORRECTION %s/>" % " ".join(ca))
    linii.append("</d398>")
    return "\n".join(linii) + "\n"


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D398 nu se poate genera: " + " ".join(er))
    calc = calcul_d398(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat398(an=an, luna=luna,
                      moes_voes_imp=_int(manual.get("moes_voes_imp"), 0),
                      nil_vat_return=calc["nil_vat_return"],
                      grand_total_vat_due=calc["grand_total_vat_due"],
                      nr_state=len(calc["ms"]),
                      nr_corectii=len(calc["corrections"]))
    return xml, res
