"""core/d397.py - D397: Declaratie informativa privind activitatile de transport alternativ
cu autoturism si conducator auto.

Se depune LUNAR de operatorii/platformele de transport alternativ (declarantul din antet, `cif`/`den`).
Platforma raporteaza, pentru fiecare operator de transport alternativ cu care lucreaza:
  - Informatii_op  : totalurile pe operator (val_curse, val_incasari) - sinteza financiara.
  - Informatii_auto: acelasi operator, defalcat pe autoturisme; sectiunea `Auto` (repetabila) descrie
    fiecare autoturism si conducatorul asociat (nr_auto, nr_km, durata, venituri, sume_n, nume, cnp...).

SURSA STRUCTURII = VALIDATORUL OFICIAL ANAF (D397Validator.jar, pachet d397validator/v0), citita din
bytecode-ul claselor D397 / Informatii_op / Informatii_auto / Auto si PROBATA camp cu camp pe DUKIntegrator.
Radacina `D397`, namespace `mfp:anaf:dgti:d397:declaratie:v1`.

Reguli probate pe validator:
  - R4       : totalPlata_A = suma cifrelor (digitilor) din `cif`-ul declarantului (suma de control). Calculata.
  - Rlista1/2: multimea cif_O din Informatii_auto trebuie sa coincida cu multimea cifO din Informatii_op.
  - Rvenituri: val_curse (Informatii_op) >= suma `venituri` a autoturismelor operatorului.
  - Rincasari: val_incasari (Informatii_op) >= suma `sume_n` a autoturismelor operatorului.
  - datele calendaristice: format dd.mm.yyyy; data_accept/data_acceptA/data_accept_CA nu pot fi ulterioare
    lunii de raportare, iar data_accept* trebuie sa fie anterioara perechii data_elim*.

Toate valorile vin din `manual` (aplicatia nu are registru de transport alternativ). NU se fabrica nimic din
acte. d_rec="0" implicit. Un Informatii_op + un Informatii_auto se emit pentru fiecare operator; daca val_curse/
val_incasari lipsesc, se deriva din sumele autoturismelor (egalitate, satisface regulile >=).

NEPOPULAT deliberat (optionale in validator, fara semantica determinabila fara input explicit): telefon, fax,
email_L, denR/cifR/adresaR/telefonR/faxR/emailR (reprezentant fiscal), data_elim / data_elimA / data_elim_CA
(operator/auto/conducator inca activ).

Contract dXXX: pull/erori_generare/calcul_d397/build_xml/genereaza(conn, schema, perioada, manual=None).
"""
from dataclasses import dataclass, field
import re
from datetime import date, datetime

NS = "mfp:anaf:dgti:d397:declaratie:v1"
_NEDIGIT = re.compile(r"\D")
_CUI_KEY = [2, 3, 5, 7, 1, 2, 3, 5, 7]  # cheia 753217532, aliniata la dreapta
_CNP_W = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]


def _cif(x):
    return _NEDIGIT.sub("", str(x or ""))


def _cui_valid(x):
    c = _cif(x)
    if not (2 <= len(c) <= 10):
        return False
    ds = [int(d) for d in c[:-1]][::-1]
    s = sum(ds[i] * _CUI_KEY[i] for i in range(len(ds)))
    ctrl = (s * 10) % 11
    ctrl = 0 if ctrl == 10 else ctrl
    return ctrl == int(c[-1])


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


def _data(x):
    """Normalizeaza data la dd.mm.yyyy (formatul cerut de validator). Formatare aritmetica cu regex,
    FARA strftime pe %d (gardul BACKEND_UI_BRUT: strftime("%d...") = data pentru ochi uman); acelasi
    procedeu ca in core/d204.py. str(date) da isoformat 'yyyy-mm-dd', prins de prima ramura."""
    s = str(x or "").strip()
    if not s:
        return ""
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", s)
    if m:
        return "%02d.%02d.%s" % (int(m.group(3)), int(m.group(2)), m.group(1))
    m = re.match(r"^(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})$", s)
    if m:
        return "%02d.%02d.%s" % (int(m.group(1)), int(m.group(2)), m.group(3))
    return s


def _int(x):
    v = _cif(x)
    return int(v) if v else 0


@dataclass
class Rezultat397:
    an: int
    luna: int
    total_plata_a: int = 0
    nr_operatori: int = 0
    nr_auto: int = 0
    avertismente: list = field(default_factory=list)


def _operatori(manual):
    return list(manual.get("operatori") or [])


def calcul_d397(manual):
    """R4: suma de control totalPlata_A = suma digitilor din cif-ul declarantului.
    Deriva si totalurile pe operator (val_curse/val_incasari) cand lipsesc din input."""
    total_plata = sum(int(d) for d in _cif(manual.get("cif")))
    ops = []
    n_auto = 0
    for op in _operatori(manual):
        autos = list(op.get("auto") or [])
        n_auto += len(autos)
        s_ven = sum(_int(a.get("venituri")) for a in autos)
        s_cash = sum(_int(a.get("sume_n")) for a in autos)
        val_curse = _int(op["val_curse"]) if op.get("val_curse") not in (None, "") else s_ven
        val_incasari = _int(op["val_incasari"]) if op.get("val_incasari") not in (None, "") else s_cash
        ops.append({"cif_O": _cif(op.get("cif_O")), "sum_ven": s_ven, "sum_cash": s_cash,
                    "val_curse": val_curse, "val_incasari": val_incasari})
    return {"totalPlata_A": total_plata, "operatori": ops, "nr_auto": n_auto}


def pull(conn, schema, perioada):
    """D397 e MANUALA: aplicatia nu are evidenta activitatii de transport alternativ. Contractul cere `pull`."""
    return {}


def erori_generare(prof, manual):
    er = []
    if not str(manual.get("den") or "").strip():
        er.append("Lipsă denumire declarant (den).")
    if not _cui_valid(manual.get("cif")):
        er.append("CIF declarant (cif) invalid - CUI cu cifra de control greșită.")
    if not str(manual.get("adresa") or "").strip():
        er.append("Lipsă adresa declarant (adresa).")
    if not str(manual.get("numeIntocmit") or "").strip():
        er.append("Lipsă nume intocmitor (numeIntocmit).")
    if not str(manual.get("functiaIntocmit") or "").strip():
        er.append("Lipsă funcție intocmitor (functiaIntocmit).")
    ops = _operatori(manual)
    if not ops:
        er.append("Lipsă operatori (cel puțin un operator cu cel puțin un autoturism).")
    calc = {o["cif_O"]: o for o in calcul_d397(manual)["operatori"]}
    for i, op in enumerate(ops, 1):
        p = "Operator %d" % i
        if not _cui_valid(op.get("cif_O")):
            er.append("%s: CIF operator (cif_O) invalid." % p)
        if not str(op.get("den_O") or "").strip():
            er.append("%s: lipsă denumire operator (den_O)." % p)
        if not _data(op.get("data_accept")):
            er.append("%s: lipsă data acceptare operator (data_accept)." % p)
        autos = list(op.get("auto") or [])
        if not autos:
            er.append("%s: niciun autoturism (Auto)." % p)
        c = calc.get(_cif(op.get("cif_O")))
        if c:
            if c["val_curse"] < c["sum_ven"]:
                er.append("%s: val_curse (%d) < suma venituri auto (%d) - regula Rvenituri."
                          % (p, c["val_curse"], c["sum_ven"]))
            if c["val_incasari"] < c["sum_cash"]:
                er.append("%s: val_incasari (%d) < suma sume_n auto (%d) - regula Rincasari."
                          % (p, c["val_incasari"], c["sum_cash"]))
        for j, a in enumerate(autos, 1):
            q = "%s auto %d" % (p, j)
            if not str(a.get("nr_auto") or "").strip():
                er.append("%s: lipsă nr. înmatriculare (nr_auto)." % q)
            if not _data(a.get("data_acceptA")):
                er.append("%s: lipsă data acceptare autoturism (data_acceptA)." % q)
            if not _data(a.get("data_accept_CA")):
                er.append("%s: lipsă data acceptare conducator (data_accept_CA)." % q)
            if not str(a.get("nume") or "").strip():
                er.append("%s: lipsă nume conducator (nume)." % q)
            if not _cnp_valid(a.get("cnp")):
                er.append("%s: CNP conducator (cnp) invalid." % q)
            if not str(a.get("statut") or "").strip():
                er.append("%s: lipsă statut (statut)." % q)
    return er


def _attr(name, val):
    return ' %s="%s"' % (name, val)


def build_xml(prof, an, luna, manual):
    calc = calcul_d397(manual)
    total = calc["totalPlata_A"]
    val_by_cif = {o["cif_O"]: o for o in calc["operatori"]}
    d_rec = _cif(manual.get("d_rec")) or "0"

    h = []
    h.append(_attr("luna", int(luna)))
    h.append(_attr("an", int(an)))
    h.append(_attr("d_rec", d_rec))
    h.append(_attr("totalPlata_A", total))
    h.append(_attr("den", _esc(manual.get("den"), 200)))
    h.append(_attr("cif", _cif(manual.get("cif"))))
    h.append(_attr("adresa", _esc(manual.get("adresa"), 200)))
    for opt, lim in (("telefon", 15), ("fax", 15), ("email_L", 250)):
        if manual.get(opt):
            h.append(_attr(opt, _esc(manual.get(opt), lim)))
    for opt, lim in (("denR", 200), ("cifR", None), ("adresaR", 200),
                     ("telefonR", 15), ("faxR", 15), ("emailR", 250)):
        if manual.get(opt):
            v = _cif(manual.get(opt)) if opt == "cifR" else _esc(manual.get(opt), lim)
            h.append(_attr(opt, v))
    h.append(_attr("numeIntocmit", _esc(manual.get("numeIntocmit"), 75)))
    h.append(_attr("functiaIntocmit", _esc(manual.get("functiaIntocmit"), 75)))

    body = []
    # Informatii_op - o sinteza pe operator
    for op in _operatori(manual):
        c = val_by_cif.get(_cif(op.get("cif_O")), {})
        a = []
        a.append(_attr("denO", _esc(op.get("den_O"), 200)))
        a.append(_attr("cifO", _cif(op.get("cif_O"))))
        a.append(_attr("data_accept", _data(op.get("data_accept"))))
        if op.get("data_elim"):
            a.append(_attr("data_elim", _data(op.get("data_elim"))))
        a.append(_attr("val_curse", c.get("val_curse", 0)))
        a.append(_attr("val_incasari", c.get("val_incasari", 0)))
        body.append("  <Informatii_op%s/>" % "".join(a))
    # Informatii_auto - defalcare pe autoturisme
    for op in _operatori(manual):
        a = []
        a.append(_attr("den_O", _esc(op.get("den_O"), 200)))
        a.append(_attr("cif_O", _cif(op.get("cif_O"))))
        a.append(_attr("data_accept", _data(op.get("data_accept"))))
        if op.get("data_elim"):
            a.append(_attr("data_elim", _data(op.get("data_elim"))))
        body.append("  <Informatii_auto%s>" % "".join(a))
        for au in (op.get("auto") or []):
            at = []
            at.append(_attr("nr_auto", _esc(au.get("nr_auto"), 20)))
            at.append(_attr("data_acceptA", _data(au.get("data_acceptA"))))
            if au.get("data_elimA"):
                at.append(_attr("data_elimA", _data(au.get("data_elimA"))))
            at.append(_attr("nr_km", _int(au.get("nr_km"))))
            at.append(_attr("durata", _int(au.get("durata"))))
            at.append(_attr("venituri", _int(au.get("venituri"))))
            at.append(_attr("sume_n", _int(au.get("sume_n"))))
            at.append(_attr("nume", _esc(au.get("nume"), 75)))
            at.append(_attr("cnp", _cif(au.get("cnp"))))
            at.append(_attr("data_accept_CA", _data(au.get("data_accept_CA"))))
            if au.get("data_elim_CA"):
                at.append(_attr("data_elim_CA", _data(au.get("data_elim_CA"))))
            at.append(_attr("statut", _esc(au.get("statut"), 20)))
            body.append("    <Auto%s/>" % "".join(at))
        body.append("  </Informatii_auto>")

    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            "<D397 xmlns=\"%s\"%s>\n%s\n</D397>\n"
            % (NS, "".join(h), "\n".join(body)))


def genereaza(conn, schema, perioada, manual=None):
    manual = dict(manual or {})
    an, luna = int(perioada.an), int(perioada.luna)
    prof = pull(conn, schema, perioada)
    er = erori_generare(prof, manual)
    if er:
        raise ValueError("D397 nu se poate genera: " + " ".join(er))
    calc = calcul_d397(manual)
    xml = build_xml(prof, an, luna, manual)
    res = Rezultat397(an=an, luna=luna, total_plata_a=calc["totalPlata_A"],
                      nr_operatori=len(_operatori(manual)), nr_auto=calc["nr_auto"])
    return xml, res
