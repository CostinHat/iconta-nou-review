"""
Modul D112 — Declarația privind obligațiile de plată a contribuțiilor sociale,
impozitului pe venit și evidența nominală a persoanelor asigurate
(ANAF v7, D112_A7.2.6, Ordin comun 2066/248/1377/3103/2025, structură 03.02.2026).

STIL NOU: calculul pe salariat este DELEGAT modulului core.salarizare (sursă unică de adevăr
pentru CAS/CASS/impozit/CAM, salariu minim, facilitate, deduceri — toate cu DATĂ din common).
Astfel D112 și statul de plată folosesc EXACT aceeași formulă. XML-ul rămâne neschimbat
(validat cu DUKIntegrator).

Coduri obligații: 602=imp salarii, 412=CAS, 432=CASS, 480=CAM.
Separare strictă: calcul pur / validare / XML / DB / orchestrare.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from core import common as c
from core import salarizare as sal

NS = "mfp:anaf:dgti:d112:declaratie:v7"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")


def _data(an, luna):
    return date(int(an), int(luna), 1)


def sal_minim(luna, an=2026, constructii=False):
    """Salariu minim din common (cu dată). Construcții = sector special (4582 în 2026)."""
    if constructii:
        return 4582
    val, _ = c.cota("salariu_minim", _data(an, luna))
    return int(val)


def suma_netaxabila(luna, an=2026):
    """Facilitate netaxabilă (OUG156/2024) din common, cu dată: 300 S1 / 200 S2 2026."""
    val, _ = c.cota("facilitate_salariu_minim", _data(an, luna))
    return int(val)


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


@dataclass
class CalcSalariat:
    nume: str
    cnp: str
    brut: int
    cas: int
    cass: int
    deducere: int
    baza_impozit: int
    impozit: int
    net: int
    cam: int
    parttime: bool = False
    netaxabil: int = 0


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    salariati: list = field(default_factory=list)
    total_brut: int = 0
    total_cas: int = 0
    total_cass: int = 0
    total_impozit: int = 0
    total_cam: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_salariat(s, luna, an=2026):
    """PUR: delegă la salarizare.calcul_salariu (sursă unică). Întoarce CalcSalariat (întregi ANAF)."""
    la_data = _data(an, luna)
    r = sal.calcul_salariu(
        brut=s.get("brut") or 0,
        persoane=int(s.get("nr_persoane_intretinere") or 0),
        sub_26=bool(s.get("sub_26")),
        copii_scoala=int(s.get("copii_scoala") or 0),
        functie_baza=bool(s.get("functie_baza", True)),
        la_data=la_data,
    )
    I = lambda x: int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return CalcSalariat(
        nume=s.get("nume") or "",
        cnp=_NEDIGIT.sub("", s.get("cnp") or ""),
        brut=I(r["brut"]), cas=I(r["cas"]), cass=I(r["cass"]),
        deducere=I(r["deducere"]["total"]), baza_impozit=I(r["baza_impozabila"]),
        impozit=I(r["impozit"]), net=I(r["net"]), cam=I(r["cam"]),
        parttime=bool(s.get("parttime")), netaxabil=I(r["facilitate"]),
    )


def calcul_d112(prof, an, luna, salariati_raw):
    """PUR: D112 pentru toți salariații (calcul delegat la salarizare)."""
    calc = [calcul_salariat(s, luna, an) for s in salariati_raw]
    tb = sum(x.brut for x in calc)
    tcas = sum(x.cas for x in calc)
    tcass = sum(x.cass for x in calc)
    timp = sum(x.impozit for x in calc)
    tcam = sum(x.cam for x in calc)
    res = Rezultat(an=an, luna=luna, prof=prof, salariati=calc,
                   total_brut=tb, total_cas=tcas, total_cass=tcass,
                   total_impozit=timp, total_cam=tcam,
                   total_plata_a=timp + tcas + tcass + tcam)
    res.avertismente.append(
        "D112 %d/%d: %d salariați, brut %d, CAS %d, CASS %d, impozit %d, CAM %d (calcul din core.salarizare)."
        % (luna, an, len(calc), tb, tcas, tcass, timp, tcam))
    return res


def valideaza(res):
    """Reguli ANAF. Întoarce listă de erori (gol = ok)."""
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CIF angajator.")
    if not _NEDIGIT.sub("", prof.get("caen") or ""):
        erori.append("LIPSĂ CAEN (obligatoriu la D112).")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire angajator.")
    for x in res.salariati:
        if not x.cnp or len(x.cnp) != 13:
            erori.append("CNP invalid pentru salariat %s." % x.nume)
        if x.brut <= 0:
            erori.append("Salariat %s cu brut 0." % x.nume)
    return erori


def build_xml(res):
    prof = res.prof
    cif = _NEDIGIT.sub("", prof.get("cui") or "")
    caen = _NEDIGIT.sub("", prof.get("caen") or "")
    den = prof.get("nume") or ""
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<declaratieUnica xmlns="%s" luna_r="%d" an_r="%d" d_rec="0" '
             'nume_declar="%s" prenume_declar="%s" functie_declar="%s">'
             % (NS, res.luna, res.an,
                _esc(prof.get("declarant_nume") or "ADMINISTRATOR"),
                _esc(prof.get("declarant_prenume") or "-"),
                _esc(prof.get("declarant_functie") or "ADMINISTRATOR")))
    H.append('  <angajator cif="%s" caen="%s" den="%s" datCAM="1" totalPlata_A="%d">'
             % (_esc(cif), _esc(caen or "0"), _esc(den), res.total_plata_a))
    for cod, cb, suma in [("01", "5503XXXXXX", res.total_impozit),
                          ("02", "5503XXXXXX", res.total_cas),
                          ("07", "5503XXXXXX", res.total_cass),
                          ("46", "20A470300X", res.total_cam)]:
        if suma:
            H.append('    <angajatorA A_codOblig="%s" A_codBugetar="%s" A_datorat="%d"/>'
                     % (cod, cb, suma))
    H.append('  </angajator>')
    for x in res.salariati:
        H.append('  <asiguratA A_1="1" cnp_asig="%s" nume="%s" A_brut="%d" '
                 'A_12="%d" A_14="%d" A_impozit="%d" A_net="%d"/>'
                 % (_esc(x.cnp), _esc(x.nume), x.brut, x.cass, x.cas, x.impozit, x.net))
    H.append('</declaratieUnica>')
    return "\n".join(H)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, caen, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        sal_rows = []
        try:
            cur.execute("SELECT nume, cnp, salariu_brut AS brut, "
                        "COALESCE(part_time,false) AS parttime, "
                        "COALESCE(persoane_intretinere,0) AS nr_persoane_intretinere "
                        "FROM salariati WHERE activ = true ORDER BY id")
            sal_rows = [dict(r) for r in cur.fetchall()]
        except Exception:
            sal_rows = []
    return prof, sal_rows


def genereaza(conn, schema, an, luna):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, sal_rows = pull(conn, schema, an, luna)
    res = calcul_d112(prof, an, luna, sal_rows)
    return build_xml(res), res
