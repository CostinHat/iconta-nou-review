"""
Modul D100 — Declarația privind obligațiile de plată la bugetul de stat
(ANAF v2, OPANAF 587/2016 cu modificările ulterioare).

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D100-D710).

Caz tratat: impozit pe venitul microîntreprinderii (cod obligație 121).

COTĂ MICRO (oficial, corectat față de versiunea veche):
  cota=1 -> 1%  : micro cu PESTE 2 salariați (inclusiv)
  cota=2 -> 2%  : micro cu UN salariat
  cota=3 -> 3%  : micro FĂRĂ salariați
(parametrul `nr_salariati` determină cota automat dacă nu e dată explicit)

Cod bugetar oficial: 5503 (a înlocuit 20470101 din 26.07.2018).
Scadență 121: 25 a lunii următoare; EXCEPȚIE trim.IV -> 25.06.an+1.

Separare strictă: calcul pur / validare / XML / DB / orchestrare.
"""
import re
from core import common as c
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d100:declaratie:v2"
REGULI = "2026.1"
COD_OBLIG_MICRO = "121"
COD_BUGETAR_MICRO = "5503XXXXXX"   # cont unic, completat cu X până la 10
_NEDIGIT = re.compile(r"\D")


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def cota_micro(nr_salariati):
    """Cotă oficială micro după numărul de salariați."""
    n = int(nr_salariati or 0)
    if n == 0:
        return 3   # 3% fără salariați
    if n == 1:
        return 2   # 2% un salariat
    return 1       # 1% peste 2 (inclusiv 2+)


def procent_din_cota(cota):
    return {1: 1, 2: 2, 3: 3}.get(int(cota), 1)


def scadenta_micro(an, trim):
    """Scadența pentru cod 121: 25 a lunii următoare trimestrului.
    EXCEPȚIE trim.IV -> 25.06.an+1 (până la anul de raportare 2025 inclusiv)."""
    lm = trim * 3
    if trim == 4:
        return "25.06.%04d" % (an + 1)
    dm, dy = lm + 1, an
    if dm > 12:
        dm, dy = 1, dy + 1
    return "25.%02d.%04d" % (dm, dy)


def nr_evidenta(an, luna_sfarsit, scadenta_str, cod_oblig=COD_OBLIG_MICRO):
    """Format oficial N(23): poz1-2=10, 3-5=cod, 6-7=01, 8-11=LLAA,
    12-17=ZZLLAA scadență, 18=0, 19=0, 20-21=00, 22-23=sumă control."""
    ll = "%02d" % luna_sfarsit
    aa = "%02d" % (an % 100)
    # scadența ZZ.LL.AAAA -> ZZLLAA
    p = scadenta_str.split(".")
    zz, sl, sa = p[0], p[1], p[2][2:]
    scad = zz + sl + sa
    s = "10" + ("%03d" % int(cod_oblig)) + "01" + ll + aa + scad + "0" + "0" + "00"
    return s + "%02d" % (sum(int(c) for c in s) % 100)


@dataclass
class Rezultat:
    an: int
    trim: int
    luna: int          # luna de sfârșit = trim*3
    prof: dict
    cota: int          # 1/2/3
    procent: int       # 1/2/3 %
    baza: int
    impozit: int
    total_plata_a: int
    scadenta: str
    avertismente: list = field(default_factory=list)


def calcul_d100(prof, an, trim, venit, nr_salariati=None, cota=None):
    """Calcul PUR. venit = bază (fără TVA) pe trimestru.
    cota: dacă None, se determină din nr_salariati."""
    if cota is None:
        cota = cota_micro(nr_salariati)
    cota = int(cota)
    proc = procent_din_cota(cota)
    baza = Decimal(str(venit or 0))
    imp = int((baza * Decimal(proc) / Decimal(100)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    lm = trim * 3
    scad = scadenta_micro(an, trim)

    res = Rezultat(an=an, trim=trim, luna=lm, prof=prof, cota=cota, procent=proc,
                   baza=int(baza), impozit=imp, total_plata_a=imp, scadenta=scad)
    if imp <= 0:
        res.avertismente.append("Impozit micro 0 (fără venituri în trimestru) — D100 nu se depune gol.")
    res.avertismente.append("D100 micro: venit %d lei × %d%% (cota %d) = impozit %d lei (trim %d/%d)."
                            % (int(baza), proc, cota, imp, trim, an))
    return res


def valideaza(res):
    erori = []
    prof = res.prof
    if res.trim < 1 or res.trim > 4:
        erori.append("Trimestru invalid.")
    if res.cota not in (1, 2, 3):
        erori.append("Cotă micro invalidă (trebuie 1/2/3).")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI firmă.")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire firmă.")
    if not prof.get("adresa"):
        erori.append("LIPSĂ adresă firmă.")
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip() or den
    tel = prof.get("telefon") or ""
    mail = prof.get("email") or ""
    scad = res.scadenta
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie100 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D100.xsd" '
           'luna="%d" an="%d" d_anulare="0" d_succ="0" '
           'nume_declar="%s" prenume_declar="%s" functie_declar="%s" '
           'cui="%s" den="%s" adresa="%s"'
           % (NS, NS, res.luna, res.an,
              _esc(prof.get("declarant_nume") or den or "ADMINISTRATOR"),
              _esc(prof.get("declarant_prenume") or "-"),
              _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
              _esc(cui), _esc(den), _esc(adr)))
    if tel:
        hdr += ' telefon="%s"' % _esc(tel)
    if mail:
        hdr += ' mail="%s"' % _esc(mail)
    hdr += ' totalPlata_A="%d">' % res.total_plata_a
    H.append(hdr)
    H.append('  <obligatie tip_oblig="1" cod_oblig="%s" cod_bugetar="%s" scadenta="%s" '
             'nr_evid="%s" cota="%d" suma_dat="%d" suma_ded="0" suma_plata="%d" suma_rest="0"/>'
             % (COD_OBLIG_MICRO, COD_BUGETAR_MICRO, scad,
                nr_evidenta(res.an, res.luna, scad), res.cota, res.impozit, res.impozit))
    H.append("</declaratie100>")
    return "\n".join(H)


def pull(conn, schema, an, trim):
    import psycopg2.extras as _E
    lm = trim * 3
    fm = lm - 2
    inceput = "%04d-%02d-01" % (an, fm)
    sfarsit = ("%04d-01-01" % (an + 1,)) if lm == 12 else ("%04d-%02d-01" % (an, lm + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT COALESCE(SUM(COALESCE(total,0)-COALESCE(tva,0)),0) AS venit "
                    "FROM facturi WHERE directie='emisa' AND data_emitere >= %s AND data_emitere < %s",
                    (inceput, sfarsit))
        venit = (cur.fetchone() or {}).get("venit") or 0
        # nr salariați activi (pentru cotă)
        nr_sal = 0
        try:
            cur.execute("SELECT COUNT(*) AS n FROM salariati")
            nr_sal = (cur.fetchone() or {}).get("n") or 0
        except Exception:
            nr_sal = 0
    return prof, venit, nr_sal


def genereaza(conn, schema, an, trim, cota=None):
    if trim < 1 or trim > 4:
        raise ValueError("Trimestru invalid: %r" % trim)
    prof, venit, nr_sal = pull(conn, schema, an, trim)
    res = calcul_d100(prof, an, trim, venit, nr_salariati=nr_sal, cota=cota)
    return build_xml(res), res
