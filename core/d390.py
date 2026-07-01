"""
Modul D390 — Declarație recapitulativă VIES privind livrările/achizițiile/
prestările intracomunitare (ANAF v3, OPANAF 705/11.03.2020).

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D390_2020_180320).

Separare strictă:
  - CALCUL PUR : calcul_d390(prof, an, luna, facturi, manual=None) -> Rezultat
  - VALIDARE   : valideaza(rezultat) -> listă erori
  - XML        : build_xml(rezultat) -> str
  - CITIRE DB  : pull(conn, schema, an, luna) -> (prof, facturi)
  - ORCHESTRARE: genereaza(conn, schema, an, luna) -> (xml, rezultat)

Tipuri operațiune (oficial):
  L = livrări intracomunitare de bunuri
  T = livrări în cadrul unei operațiuni triunghiulare
  A = achiziții intracomunitare de bunuri
  P = prestări intracomunitare de servicii
  S = achiziții intracomunitare de servicii
  R = livrări intracomunitare de bunuri în regim special pentru agricultori

Mapare automată din facturi: emisă->L (bunuri), primită->A (bunuri).
Serviciile (P/S) și triangulația (T/R) = clasificare manuală de contabil (prin `manual`).

totalPlata_A = nrOPI + bazaL + bazaT + bazaA + bazaP + bazaS + bazaR (formula oficială).
"""
import re
from core import common as c
from dataclasses import dataclass, field
from decimal import Decimal

NS = "mfp:anaf:dgti:d390:declaratie:v3"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
# CUI UE: prefix 2 litere + cod
_CUI_UE = re.compile(r"^([A-Z]{2})([0-9A-Z]+)$")

# Nomenclator oficial țări (cod TVA -> cod ANAF în XML). Atenție: Croația HR -> CR în XML.
TARI_UE = {
    "AT", "BE", "BG", "CZ", "CY", "HR", "DK", "EE", "DE", "EL", "FI", "FR",
    "IE", "IT", "LV", "LU", "LT", "MT", "GB", "NL", "PL", "PT", "SI", "SK",
    "ES", "SE", "HU", "XI",  # XI = Irlanda de Nord (post-Brexit, VIES)
}
# prefixul de TVA HR (Croația) se scrie CR în nomenclatorul ANAF
_TARA_XML = {"HR": "CR"}

TIPURI = ("L", "T", "A", "P", "S", "R")


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    try:
        return int(round(float(x)))
    except Exception:
        return 0


def _tara_xml(t):
    return _TARA_XML.get(t, t)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    ops: dict = field(default_factory=dict)        # (tip,tara,cod,den) -> baza int
    rezumat: dict = field(default_factory=dict)    # {L,T,A,P,S,R: int}
    nr_opi: int = 0
    total_baza: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d390(prof, an, luna, facturi, manual=None):
    """Calcul PUR. facturi: dict cu cui, nume, directie, total, tva.
    manual: listă opțională de dict-uri {tip, tara, cod, den, baza} introduse de contabil
            (pentru P/S/T/R care nu se pot deriva automat din facturi)."""
    ops = {}
    skip_nocui = skip_dom = 0

    for f in facturi:
        raw = (f.get("cui") or "").strip().upper().replace(" ", "").replace("-", "")
        m = _CUI_UE.match(raw)
        if not m:
            skip_nocui += 1
            continue
        tara, cod = m.group(1), m.group(2)[:12]
        if tara == "RO" or tara not in TARI_UE:
            skip_dom += 1
            continue
        tip = "L" if f.get("directie") == "emisa" else "A"   # bunuri
        den = (f.get("nume") or "")[:200]
        baza = Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0))
        k = (tip, tara, cod, den)
        ops[k] = ops.get(k, Decimal("0")) + baza

    # operațiuni manuale (P/S/T/R)
    for op in (manual or []):
        tip = op.get("tip")
        if tip not in TIPURI:
            continue
        tara = (op.get("tara") or "").upper()
        cod = (op.get("cod") or "")[:12]
        den = (op.get("den") or "")[:200]
        k = (tip, tara, cod, den)
        ops[k] = ops.get(k, Decimal("0")) + Decimal(str(op.get("baza") or 0))

    rez = {t: Decimal("0") for t in TIPURI}
    for (tip, _, _, _), b in ops.items():
        rez[tip] += b
    bz = {t: _int(rez[t]) for t in TIPURI}
    nr_opi = len(ops)
    tot = _int(sum(rez.values()))
    # formula oficială totalPlata_A
    total_plata = nr_opi + bz["L"] + bz["T"] + bz["A"] + bz["P"] + bz["S"] + bz["R"]

    ops_int = {k: _int(v) for k, v in ops.items()}
    res = Rezultat(an=an, luna=luna, prof=prof, ops=ops_int, rezumat=bz,
                   nr_opi=nr_opi, total_baza=tot, total_plata_a=total_plata)
    if skip_dom:
        res.avertismente.append("%d facturi cu parteneri RO/non-UE — excluse (D390 e doar intracomunitar)." % skip_dom)
    if skip_nocui:
        res.avertismente.append("%d facturi fără CUI UE valid (prefix țară) — excluse." % skip_nocui)
    if not ops:
        res.avertismente.append("Nicio operațiune intracomunitară în lună — D390 se depune doar dacă există operațiuni.")
    res.avertismente.append("Mapare automată: emisă->L, primită->A (bunuri). Servicii (P/S) și triangulație (T/R) = clasificare manuală.")
    return res


def valideaza(res):
    """Verifică regulile ANAF. Întoarce listă de erori."""
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    if res.an >= 2020 and res.luna < 2 and res.an == 2020:
        erori.append("Pentru an=2020, luna >= 2.")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI firmă (obligatoriu).")
    if not (prof.get("nume")):
        erori.append("LIPSĂ denumire firmă.")
    # codO obligatoriu pentru L,T,P,R
    for (tip, tara, cod, den) in res.ops:
        if tip in ("L", "T", "P", "R") and not cod:
            erori.append("Operatorul %s/%s (tip %s) nu are cod — obligatoriu pentru L,T,P,R." % (tara, den, tip))
        if tara and tara not in TARI_UE:
            erori.append("Țara %s nu e în nomenclatorul UE." % tara)
    # totalPlata_A coerent
    calc = (res.nr_opi + res.rezumat["L"] + res.rezumat["T"] + res.rezumat["A"]
            + res.rezumat["P"] + res.rezumat["S"] + res.rezumat["R"])
    if calc != res.total_plata_a:
        erori.append("totalPlata_A incoerent (calcul=%d, stocat=%d)." % (calc, res.total_plata_a))
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip()
    tel = prof.get("telefon") or ""
    mail = prof.get("email") or ""
    bz = res.rezumat
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie390 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D390.xsd" '
           'luna="%d" an="%d" d_rec="0" nume_declar="%s" prenume_declar="%s" '
           'functie_declar="%s" cui="%s" den="%s" adresa="%s"'
           % (NS, NS, res.luna, res.an,
              _esc(prof.get("declarant_nume") or "ADMINISTRATOR"),
              _esc(prof.get("declarant_prenume") or "-"),
              _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
              _esc(cui), _esc(den), _esc(adr)))
    if tel:
        hdr += ' telefon="%s"' % _esc(tel)
    if mail:
        hdr += ' mail="%s"' % _esc(mail)
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    H.append('  <rezumat nr_pag="1" nrOPI="%d" bazaL="%d" bazaT="%d" bazaA="%d" '
             'bazaP="%d" bazaS="%d" bazaR="%d" total_baza="%d"/>'
             % (res.nr_opi, bz["L"], bz["T"], bz["A"], bz["P"], bz["S"], bz["R"], res.total_baza))
    # operațiuni ordonate (tip, tara, cod)
    for (tip, tara, cod, den) in sorted(res.ops.keys(), key=lambda k: (k[0], k[1], k[2])):
        H.append('  <operatie tip="%s" tara="%s" codO="%s" denO="%s" baza="%d"/>'
                 % (tip, _tara_xml(tara), _esc(cod), _esc(den), res.ops[(tip, tara, cod, den)]))
    H.append("</declaratie390>")
    return "\n".join(H)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT f.id, f.tert_nume, c.nume AS c_nume, c.cui AS c_cui, "
                    "f.directie, f.total, f.tva "
                    "FROM facturi f LEFT JOIN clienti c ON c.id = f.client_id "
                    "WHERE f.data_emitere >= %s AND f.data_emitere < %s ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    facturi = [{"cui": (r["c_cui"] or "").strip(),
                "nume": (r["c_nume"] or r["tert_nume"] or "").strip(),
                "directie": r["directie"],
                "total": r["total"] if r["total"] is not None else 0,
                "tva": r["tva"] if r["tva"] is not None else 0} for r in rows]
    return prof, facturi


def genereaza(conn, schema, an, luna, manual=None):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, facturi = pull(conn, schema, an, luna)
    res = calcul_d390(prof, an, luna, facturi, manual)
    return build_xml(res), res
