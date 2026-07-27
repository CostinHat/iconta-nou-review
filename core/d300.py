"""
Modul D300 — Decont de TVA (ANAF v12, conform OPANAF 174/2026 + Legea 141/2025).

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D300_v12.0.0_10022026).

Separare strictă:
  - CALCUL PUR : calcul_d300(prof, an, luna, facturi, manual=None) -> Rezultat
  - VALIDARE   : valideaza(rezultat) -> listă erori (regulile ANAF)
  - XML        : build_xml(rezultat) -> str
  - CITIRE DB  : pull(conn, schema, an, luna) -> (prof, facturi)
  - ORCHESTRARE: genereaza(conn, schema, an, luna) -> (xml, rezultat)

COTE (de la 1 aug 2025, Legea 141/2025):
  - standard 21% -> R9  (livrări col1/col2), R22 (achiziții deductibile)
  - redusă  11% -> R10 (livrări), R24.1 (achiziții)
  - tranzitorie 9% locuințe -> R11 (livrări), R24.4 (achiziții)
  - 5% -> R24.5 deductibilă (livrări 5% R71 doar prin manual)
Cotele vechi (19/9/5) rămân pentru regularizări — suportate prin `manual`.

Maparea automată din facturi: emisă->colectată, primită->deductibilă, pe cotă.
Operațiunile speciale (intracomunitar, taxare inversă, regularizări, scutiri)
se pun prin dict-ul `manual` (rânduri introduse de contabil), nu derivate din facturi.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from core import common as c

NS = "mfp:anaf:dgti:d300:declaratie:v12"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
_TIP_COD = {"L": "301", "T": "302", "S": "303", "A": "304"}

# cotele tratate automat din facturi (col bază, col tva) -> rândul de livrare/achiziție
# livrări: 21->R9, 11->R10, 9->R11 ; achiziții deductibile: 21->R22, 11->R24_1(R74), 9->R24_4
_LIVRARE_RAND = {21: "R9", 11: "R10", 9: "R11"}
_ACHIZ_RAND = {21: "R22", 11: "R74", 9: "R76"}   # R74=24.1(11%), R76=24.4(9%) deductibilă


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    # MASCA SCOASA 27.07.2026 (vezi core.common.numar_fiscal).
    from core.numere import numar_fiscal
    return int(numar_fiscal(x, "D300").quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _digits(x):
    return _NEDIGIT.sub("", x or "")


def _clean_bc(v):
    """Bancă/cont: ANAF interzice virgulă și #."""
    return ("" if v is None else str(v)).replace(",", " ").replace("#", " ").strip()


def tip_decont(prof):
    t = str(prof.get("tip_decont") or "").strip().lower()
    if t in ("l", "t", "s", "a"):
        return t.upper()
    if "trim" in t:
        return "T"
    if "sem" in t:
        return "S"
    if t.startswith("an"):
        return "A"
    return "L"


def nr_evidenta(an, luna, tip):
    """C(23) cu cifră de control. Poz.1-2=10, 3-5=cod tip, 6-7=01,
    8-11=LLAA, 12-17=ZZLLAA scadență, 18-21=0000, 22-23=sumă control."""
    cod = _TIP_COD.get(tip, "301")
    ll = "%02d" % luna
    aa = "%02d" % (an % 100)
    dm, dy = luna + 1, an
    if dm > 12:
        dm, dy = 1, dy + 1
    scad = "25" + "%02d" % dm + "%02d" % (dy % 100)
    s = "10" + cod + "01" + ll + aa + scad + "0000"
    return s + "%02d" % (sum(int(c) for c in s) % 100)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    R: dict = field(default_factory=dict)          # {"R9_1": int, "R9_2": int, ...}
    tva_de_plata: int = 0
    tva_de_recuperat: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def _segmente(f):
    """[(cota_int|None, baza_Decimal), ...] dintr-o factură."""
    linii = f.get("linii") or []
    if linii:
        out = []
        for (cant, pret, cota) in linii:
            baza = Decimal(str(cant)) * Decimal(str(pret))
            ci = None if cota is None else int(round(float(cota)))
            out.append((ci, baza))
        return out
    baza = Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0))
    tva = Decimal(str(f.get("tva") or 0))
    ci = int(round(float(tva) / float(baza) * 100)) if (baza and tva) else None
    return [(ci, baza)]


def calcul_d300(prof, an, luna, facturi, manual=None):
    """
    Calcul PUR al decontului după structura ANAF v12.
    manual: dict opțional {rând: valoare} pentru operațiuni speciale introduse
            de contabil (ex. {"R5_1": 1000, "R5_2": 210} pt achiziții intracom).
    """
    manual = manual or {}
    Z = lambda: [Decimal(0), Decimal(0)]
    # colectată pe cote (livrări taxabile)
    col = {21: Z(), 11: Z(), 9: Z()}
    # deductibilă pe cote (achiziții)
    ded = {21: Z(), 11: Z(), 9: Z()}
    alte_l = alte_a = 0

    for f in facturi:
        emisa = (f.get("directie") == "emisa")
        for (ci, baza) in _segmente(f):
            tva = baza * Decimal(ci) / Decimal(100) if ci else Decimal(0)
            if emisa:
                if ci in col:
                    col[ci][0] += baza; col[ci][1] += tva
                else:
                    alte_l += 1
            else:
                if ci in ded:
                    ded[ci][0] += baza; ded[ci][1] += tva
                else:
                    alte_a += 1

    R = {}
    def setr(name, val):
        v = _int(val)
        if v:
            R[name] = v

    # --- COLECTATĂ: livrări 21/11/9 ---
    setr("R9_1", col[21][0]);  setr("R9_2", col[21][1])     # 21%
    setr("R10_1", col[11][0]); setr("R10_2", col[11][1])    # 11%
    setr("R11_1", col[9][0]);  setr("R11_2", col[9][1])     # 9% tranzitoriu

    # rânduri manuale (intracomunitar, taxare inversă, regularizări, scutiri colectate)
    for k, v in manual.items():
        if k.startswith(("R1_", "R2_", "R3_", "R4_", "R5_", "R6_", "R7_", "R8_",
                         "R13_", "R14_", "R15_", "R16_", "R64_", "R65_")):
            setr(k, v)

    # R17 = TOTAL TAXĂ COLECTATĂ (formula oficială: sumă rd.1-18 cu excepții)
    # col.1 (bază) și col.2 (TVA) — pentru firma simplă: R9_1+R10_1+R11_1, R9_2+R10_2+R11_2
    r17_1 = sum(R.get(k, 0) for k in (
        "R1_1", "R2_1", "R3_1", "R4_1", "R5_1", "R6_1", "R7_1", "R8_1",
        "R9_1", "R10_1", "R11_1", "R12_1", "R13_1", "R14_1", "R15_1", "R16_1",
        "R64_1", "R65_1"))
    r17_2 = sum(R.get(k, 0) for k in (
        "R5_2", "R6_2", "R7_2", "R8_2", "R9_2", "R10_2", "R11_2", "R12_2",
        "R16_2", "R64_2", "R65_2"))
    if r17_1 or r17_2:
        R["R17_1"], R["R17_2"] = r17_1, r17_2

    # --- DEDUCTIBILĂ: achiziții 21/11/9 ---
    setr("R22_1", ded[21][0]); setr("R22_2", ded[21][1])    # 21%
    setr("R74_1", ded[11][0]); setr("R74_2", ded[11][1])    # 11% (rd.24.1)
    setr("R76_1", ded[9][0]);  setr("R76_2", ded[9][1])     # 9% (rd.24.4)

    for k, v in manual.items():
        if k.startswith(("R18_", "R19_", "R20_", "R21_", "R23_", "R25_", "R26_",
                         "R72_", "R73_", "R75_")):
            setr(k, v)

    # R27 = TOTAL TAXA DEDUCTIBILA (col.1 baza, col.2 TVA). Formula oficiala
    # (structura_D300_v12.0.0_10022026.pdf, randul 101-102):
    #   R27_1 = R18_1+R19_1+R20_1+R21_1+R22_1+R23_1+R24_1+R25_1+R74_1+R75_1
    #   R27_2 = R18_2+R19_2+R20_2+R21_2+R22_2+R23_2+R24_2+R25_2+R43_2+R44_2+R74_2+R75_2
    # LIPSEA COMPLET pana la 16.07.2026: modulul calcula R30/R31/R40 direct din R22,
    # sarind peste tot lantul R27->R32->R34->R37->R40 pe care validatorul il cere si
    # verifica formula cu formula. Descoperit prin audit pe date reale, nu pe XML gol.
    r27_1 = sum(R.get(k, 0) for k in (
        "R18_1", "R19_1", "R20_1", "R21_1", "R22_1", "R23_1", "R24_1", "R25_1",
        "R74_1", "R75_1"))
    r27_2 = sum(R.get(k, 0) for k in (
        "R18_2", "R19_2", "R20_2", "R21_2", "R22_2", "R23_2", "R24_2", "R25_2",
        "R43_2", "R44_2", "R74_2", "R75_2"))
    if r27_1 or r27_2:
        R["R27_1"], R["R27_2"] = r27_1, r27_2

    # R28_2 = SUB-TOTAL TAXA DEDUSA conform art.297/298 - la o firma simpla,
    # egal cu R27_2 (nimic de scazut la acest nivel: nu avem TVA restituita
    # cumparatori straini (R29) inca).
    r28_2 = r27_2
    if r28_2:
        R["R28_2"] = r28_2

    # pro-rata pe deductibila -> R31_2 (Ajustari conform pro-rata / ajustari de taxa).
    # NU e "taxa deductibila x pro-rata direct" (asa calcula gresit modulul vechi) -
    # e o AJUSTARE separata, aditionala la R28. La pro_rata=100% (cazul uzual),
    # ajustarea e 0 - nu exista de ajustat.
    # Pro-rata ABSENTA = 100% (cazul uzual, fara activitate mixta). Dar o valoare
    # PREZENTA si invalida nu mai devine tacit 100% - ar declara deducere integrala
    # acolo unde firma are drept partial. Absenta e legitima, invalidul e eroare.
    from core.numere import numar_fiscal
    _pr = prof.get("pro_rata")
    pro_rata = 100.0 if _pr is None or (isinstance(_pr, str) and not _pr.strip()) \
        else float(numar_fiscal(_pr, "pro_rata"))
    r31_2 = 0
    if pro_rata < 100:
        r31_2 = _int(Decimal(str(r28_2)) * Decimal(str(100 - pro_rata)) / Decimal(100) * -1)
    if r31_2:
        R["R31_2"] = r31_2

    # R32 = TOTAL TAXA DEDUSA (rd.31+rd.32+rd.33+rd.34 in numerotarea veche = R28+R29+R30+R31)
    r32_2 = r28_2 + R.get("R29_2", 0) + R.get("R30_2", 0) + r31_2
    if r32_2:
        R["R32_2"] = r32_2

    # --- REZULTAT: lantul complet R33->R42, formule oficiale exacte ---
    r17_2_val = R.get("R17_2", 0)
    r33_2 = max(r32_2 - r17_2_val, 0)          # Suma negativa TVA in perioada
    r34_2 = max(r17_2_val - r32_2, 0)          # Taxa de plata in perioada
    if r33_2:
        R["R33_2"] = r33_2
    if r34_2:
        R["R34_2"] = r34_2

    r35_2 = R.get("R35_2", 0)   # sold de plata reportat din perioada precedenta
    r36_2 = R.get("R36_2", 0)   # diferente stabilite de inspectie fiscala
    r37_2 = r34_2 + r35_2 + r36_2   # TVA de plata cumulat
    if r37_2:
        R["R37_2"] = r37_2

    r38_2 = R.get("R38_2", 0)   # sold suma negativa reportata, fara rambursare ceruta
    r39_2 = R.get("R39_2", 0)   # diferente negative stabilite de inspectie fiscala
    r40_2 = r33_2 + r38_2 + r39_2   # Suma negativa TVA cumulata
    if r40_2:
        R["R40_2"] = r40_2

    r41_2 = max(r37_2 - r40_2, 0)   # Sold TVA de plata la sfarsitul perioadei
    r42_2 = max(r40_2 - r37_2, 0)   # Soldul sumei negative la sfarsitul perioadei
    if r41_2:
        R["R41_2"] = r41_2
    if r42_2:
        R["R42_2"] = r42_2

    de_plata = r41_2
    de_recuperat = r42_2

    res = Rezultat(an=an, luna=luna, prof=prof)
    res.R = R
    res.tva_de_plata = de_plata
    res.tva_de_recuperat = de_recuperat
    # totalPlata_A = suma câmpurilor 27-124 (toate rândurile R emise)
    res.total_plata_a = sum(R.values())

    if alte_l:
        res.avertismente.append("%d linii livrare cu cotă în afara 21/11/9 — neincluse (pune-le manual la rândurile potrivite)." % alte_l)
    if alte_a:
        res.avertismente.append("%d linii achiziție cu cotă în afara 21/11/9 — neincluse." % alte_a)
    _f = lambda x: format(int(x), ",").replace(",", ".")
    rez = ("de plată " + _f(de_plata)) if de_plata else (("de recuperat " + _f(de_recuperat)) if de_recuperat else "0")
    res.avertismente.append("Rezultat TVA %s lei." % rez)
    return res


def valideaza(res):
    """Verifică regulile ANAF. Întoarce listă de erori (gol = ok)."""
    erori = []
    prof = res.prof
    luna = res.luna
    tip = tip_decont(prof)

    # tip_decont corelat cu luna
    if tip == "A" and luna != 12:
        erori.append("tip_decont=A (anual) cere luna=12.")
    if tip == "S" and luna not in (6, 12):
        erori.append("tip_decont=S (semestrial) cere luna 06 sau 12.")
    if tip == "T" and luna not in (2, 3, 5, 6, 8, 9, 11, 12):
        erori.append("tip_decont=T (trimestrial) cere luna în (02,03,05,06,08,09,11,12).")

    # bancă/cont obligatorii
    banca = _clean_bc(prof.get("banca"))
    cont = _clean_bc(prof.get("iban") or prof.get("cont"))
    if not banca:
        erori.append("LIPSĂ bancă — obligatorie la D300.")
    if not cont:
        erori.append("LIPSĂ cont/IBAN — obligatoriu la D300.")
    # CAEN obligatoriu
    if not _digits(prof.get("caen")):
        erori.append("LIPSĂ CAEN — obligatoriu la D300.")
    # CUI
    if not _digits(prof.get("cui")):
        erori.append("LIPSĂ CUI firmă.")

    # marja ±1% pe cotele cu valori. Cota standard vine din common (cu data perioadei
    # declarate), ca să fie corectă și pe perioade cu 19% (înainte de 01.08.2025).
    cota_std_dec, _ = c.cota("tva_standard", date(res.an, res.luna, 1))
    cota_std = int(round(float(cota_std_dec) * 100))   # 21 sau 19

    def marja(baza_k, tva_k, cota):
        b = res.R.get(baza_k, 0)
        t = res.R.get(tva_k, 0)
        if b and t:
            lo = round((cota - 1) / 100 * b)
            hi = round((cota + 1) / 100 * b)
            if not (lo <= t <= hi):
                erori.append("TVA %s (%d) nu se încadrează în %d%%±1%% din baza %d." % (tva_k, t, cota, b))
    marja("R9_1", "R9_2", cota_std)
    marja("R10_1", "R10_2", 11)
    marja("R11_1", "R11_2", 9)
    marja("R22_1", "R22_2", cota_std)
    return erori


def build_xml(res):
    prof = res.prof
    tip = tip_decont(prof)
    cui = _digits(prof.get("cui"))
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip() or den
    A = [
        'luna="%d"' % res.luna, 'an="%d"' % res.an,
        'depusReprezentant="0"', 'bifa_interne="0"', 'temei="0"',
        'nume_declar="%s"' % _esc(prof.get("declarant_nume") or den or "ADMINISTRATOR"),
        'prenume_declar="%s"' % _esc(prof.get("declarant_prenume") or "-"),
        'functie_declar="%s"' % _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
        'cui="%s"' % _esc(cui),
        'den="%s"' % _esc(den),
        'adresa="%s"' % _esc(adr),
        'banca="%s"' % _esc(_clean_bc(prof.get("banca"))),
        'cont="%s"' % _esc(_clean_bc(prof.get("iban") or prof.get("cont"))),
        'caen="%s"' % _esc(_digits(prof.get("caen")) or "0"),
        'tip_decont="%s"' % tip,
        'pro_rata="%s"' % ("%.2f" % (float(prof.get("pro_rata")) if str(prof.get("pro_rata") or "").strip() else 100.0)),
        'bifa_cereale="N"', 'bifa_mob="N"', 'bifa_disp="N"', 'bifa_cons="N"',
        'solicit_ramb="N"',
        'nr_evid="%s"' % nr_evidenta(res.an, res.luna, tip),
        'totalPlata_A="%d"' % res.total_plata_a,
    ]
    for k in sorted(res.R.keys()):
        A.append('%s="%d"' % (k, res.R[k]))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<declaratie300 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns="%s" xsi:schemaLocation="%s D300.xsd" ' % (NS, NS)
            + ' '.join(A) + '/>')


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, caen, banca, iban, tip_decont, pro_rata, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        cur.execute("SELECT f.id, f.directie, f.total, f.tva, l.cantitate, l.pret_unitar, l.cota_tva "
                    "FROM facturi f LEFT JOIN factura_linii l ON l.factura_id = f.id "
                    "WHERE f.data_emitere >= %s AND f.data_emitere < %s ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    fmap = {}
    for r in rows:
        f = fmap.setdefault(r["id"], {"directie": r["directie"],
                                      "total": r["total"] if r["total"] is not None else 0,
                                      "tva": r["tva"] if r["tva"] is not None else 0, "linii": []})
        if r["cantitate"] is not None and r["pret_unitar"] is not None:
            f["linii"].append((r["cantitate"], r["pret_unitar"], r["cota_tva"]))
    return prof, list(fmap.values())


def genereaza(conn, schema, an, luna, manual=None):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, facturi = pull(conn, schema, an, luna)
    res = calcul_d300(prof, an, luna, facturi, manual)
    return build_xml(res), res
