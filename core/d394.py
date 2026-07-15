"""
Modul D394 — Declarația informativă privind livrările/prestările și achizițiile
efectuate pe teritoriul național de persoanele înregistrate în scopuri de TVA
(ANAF, OPANAF 3769/2015 cu modificările ulterioare).

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D394).

Tipuri operațiune (oficial):
  L = livrări de bunuri/prestări servicii efectuate
  A = achiziții de bunuri și servicii efectuate
  V = livrări cu taxare inversă
  C = achiziții cu taxare inversă

Doar parteneri ÎNREGISTRAȚI în scopuri de TVA în România (CUI fără prefix de țară).
Agregare pe (cuiP, tip) — pereche unică. Secțiunea op11 (cereale) doar pt V/C.
totalPlata_A = nrCui + bazaL+tvaL + bazaA+tvaA + bazaV+tvaV + bazaC+tvaC + bazaVc+tvaVc + bazaCc+tvaCc.

Separare strictă: calcul pur / validare / XML / DB / orchestrare.
"""
import re
from core import common as c
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d394:declaratie:v2"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
_CUI_RO = re.compile(r"^(RO)?(\d{2,10})$", re.I)
TIPURI = ("L", "A", "V", "C")

# nomenclator NC cereale (pentru taxare inversă agricolă)
NC_CEREALE = {"10011000", "10019010", "10019091", "10019099", "10020000",
              "100300", "1005", "120100", "1205", "120600", "121291"}


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    try:
        return int(round(float(x or 0)))
    except Exception:
        return 0


def _cui_ro(raw):
    """Extrage CUI românesc (fără RO). Întoarce None dacă nu e RO valid."""
    s = (raw or "").strip().upper().replace(" ", "").replace("-", "")
    m = _CUI_RO.match(s)
    if not m:
        return None
    return m.group(2)


@dataclass
class Rezultat:
    an: int
    luna: int
    prof: dict
    op1: dict = field(default_factory=dict)        # (tip,cui,den) -> [baza, tva]
    rezumat: dict = field(default_factory=dict)    # {bazaL,tvaL,bazaA,...}
    nr_cui: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d394(prof, an, luna, facturi, manual=None):
    """PUR. facturi: dict cu cui, nume, directie, baza, tva, taxare_inversa(bool).
    manual: listă opțională {tip, cui, den, baza, tva} pentru clasificări speciale."""
    op1 = {}
    skip_strain = skip_nocui = 0

    for f in facturi:
        cui = _cui_ro(f.get("cui"))
        if cui is None:
            # poate fi partener UE/extern -> nu intră în D394 (e doar național)
            raw = (f.get("cui") or "").strip().upper()
            if raw and raw[:2].isalpha() and raw[:2] != "RO":
                skip_strain += 1
            else:
                skip_nocui += 1
            continue
        emisa = (f.get("directie") == "emisa")
        ti = bool(f.get("taxare_inversa"))
        if emisa:
            tip = "V" if ti else "L"
        else:
            tip = "C" if ti else "A"
        den = (f.get("nume") or "")[:200]
        baza = Decimal(str(f.get("baza") if f.get("baza") is not None
                           else (Decimal(str(f.get("total") or 0)) - Decimal(str(f.get("tva") or 0)))))
        tva = Decimal(str(f.get("tva") or 0))
        k = (tip, cui, den)
        cur = op1.setdefault(k, [Decimal(0), Decimal(0)])
        cur[0] += baza; cur[1] += tva

    for op in (manual or []):
        tip = op.get("tip")
        if tip not in TIPURI:
            continue
        cui = _cui_ro(op.get("cui")) or (op.get("cui") or "")
        den = (op.get("den") or "")[:200]
        k = (tip, cui, den)
        cur = op1.setdefault(k, [Decimal(0), Decimal(0)])
        cur[0] += Decimal(str(op.get("baza") or 0))
        cur[1] += Decimal(str(op.get("tva") or 0))

    # rezumat pe tip
    rez = {t: [Decimal(0), Decimal(0)] for t in TIPURI}
    cuis = set()
    for (tip, cui, den), (b, t) in op1.items():
        rez[tip][0] += b; rez[tip][1] += t
        cuis.add(cui)

    R = {
        "bazaL": _int(rez["L"][0]), "tvaL": _int(rez["L"][1]),
        "bazaA": _int(rez["A"][0]), "tvaA": _int(rez["A"][1]),
        "bazaV": _int(rez["V"][0]), "tvaV": _int(rez["V"][1]),
        "bazaC": _int(rez["C"][0]), "tvaC": _int(rez["C"][1]),
        "bazaVc": 0, "tvaVc": 0, "bazaCc": 0, "tvaCc": 0,   # cereale (op11) — manual
    }
    nr_cui = len(cuis)
    total_plata = (nr_cui + R["bazaL"] + R["tvaL"] + R["bazaA"] + R["tvaA"]
                   + R["bazaV"] + R["tvaV"] + R["bazaC"] + R["tvaC"]
                   + R["bazaVc"] + R["tvaVc"] + R["bazaCc"] + R["tvaCc"])

    op1_int = {k: [_int(v[0]), _int(v[1])] for k, v in op1.items()}
    res = Rezultat(an=an, luna=luna, prof=prof, op1=op1_int, rezumat=R,
                   nr_cui=nr_cui, total_plata_a=total_plata)
    if skip_strain:
        res.avertismente.append("%d facturi cu parteneri străini (UE/non-UE) — excluse (D394 e doar național)." % skip_strain)
    if skip_nocui:
        res.avertismente.append("%d facturi fără CUI valid (ex. persoane fizice) — excluse din secțiunea pe parteneri." % skip_nocui)
    res.avertismente.append("D394 %d/%d: %d parteneri TVA, livrări %d, achiziții %d."
                            % (luna, an, nr_cui, R["bazaL"], R["bazaA"]))
    return res


def valideaza(res):
    erori = []
    prof = res.prof
    if res.luna < 1 or res.luna > 12:
        erori.append("Lună invalidă.")
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI declarant.")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire.")
    for (tip, cui, den) in res.op1:
        if tip not in TIPURI:
            erori.append("Tip operațiune %s invalid (trebuie A/L/C/V)." % tip)
        if not _NEDIGIT.sub("", cui):
            erori.append("Partener fără CUI valid: %s." % den)
    # coerență totalPlata_A
    R = res.rezumat
    calc = (res.nr_cui + sum(R.values()))
    if calc != res.total_plata_a:
        erori.append("totalPlata_A incoerent.")
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip()
    R = res.rezumat
    # tip declarație după lună (L/T/S/A) — implicit lunar
    tip_d = "L"
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    H.append('<declaratie394 xmlns="%s" luna="%d" an="%d" tip_D394="%s" '
             'nume_declar="%s" prenume_declar="%s" functie_declar="%s" '
             'totalPlata_A="%d">'
             % (NS, res.luna, res.an, tip_d,
                _esc(prof.get("declarant_nume") or "ADMINISTRATOR"),
                _esc(prof.get("declarant_prenume") or "-"),
                _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
                res.total_plata_a))
    H.append('  <identificare cui="%s" den="%s" adresa="%s"/>' % (_esc(cui), _esc(den), _esc(adr)))
    H.append('  <rezumat nrCui="%d" bazaL="%d" tvaL="%d" bazaA="%d" tvaA="%d" '
             'bazaV="%d" tvaV="%d" bazaC="%d" tvaC="%d" '
             'bazaVc="%d" tvaVc="%d" bazaCc="%d" tvaCc="%d"/>'
             % (res.nr_cui, R["bazaL"], R["tvaL"], R["bazaA"], R["tvaA"],
                R["bazaV"], R["tvaV"], R["bazaC"], R["tvaC"],
                R["bazaVc"], R["tvaVc"], R["bazaCc"], R["tvaCc"]))
    for (tip, cui_p, den_p) in sorted(res.op1.keys(), key=lambda k: (k[0], k[1])):
        b, t = res.op1[(tip, cui_p, den_p)]
        H.append('  <op1 tip="%s" cuiP="%s" denP="%s" baza="%d" tva="%d"/>'
                 % (tip, _esc(cui_p), _esc(den_p), b, t))
    H.append('</declaratie394>')
    return "\n".join(H)


def _b(x):
    return Decimal(str(x or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def pull(conn, schema, an, luna):
    import psycopg2.extras as _E
    inceput = "%04d-%02d-01" % (an, luna)
    sfarsit = ("%04d-01-01" % (an + 1,)) if luna == 12 else ("%04d-%02d-01" % (an, luna + 1))
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        # PARTENER: la emise vine din clienti (client_id); la primite furnizorul e in
        # tert_cui/tert_nume (nu exista client_id) - inainte se citea doar din clienti,
        # deci ACHIZITIILE ieseau fara CUI si cadeau din D394 ca "fara cui". 15.07.2026.
        # PROFORME: nu se raporteaza in D394 (nu sunt facturi fiscale).
        # NU defalcam pe cote: cartusul op1 raporteaza per partener/tip, cu baza si TVA
        # TOTALE; cotele apar in cartuse pe care nu le generam inca (vezi LIMITE, la fel
        # ca op11 cereale = manual). O defalcare aici s-ar re-aduna in aceeasi cheie.
        cur.execute("SELECT f.id, f.tert_nume, f.tert_cui, c.nume AS c_nume, c.cui AS c_cui, "
                    "f.directie, f.total, f.tva, f.taxare_inversa AS ti, f.categorie_331 "
                    "FROM facturi f "
                    "LEFT JOIN clienti c ON c.id = f.client_id "
                    "WHERE f.data_emitere >= %s AND f.data_emitere < %s "
                    "  AND COALESCE(f.tip, 'factura') = 'factura' "
                    "ORDER BY f.id",
                    (inceput, sfarsit))
        rows = cur.fetchall()
    facturi = []
    for r in rows:
        emisa = (r["directie"] == "emisa")
        cui = ((r["c_cui"] if emisa else None) or r["tert_cui"] or r["c_cui"] or "").strip()
        nume = ((r["c_nume"] if emisa else None) or r["tert_nume"] or r["c_nume"] or "").strip()
        total = Decimal(str(r["total"] or 0))
        tva = Decimal(str(r["tva"] or 0))
        facturi.append({"cui": cui, "nume": nume, "directie": r["directie"],
                        "taxare_inversa": bool(r["ti"]),
                        "categorie_331": r["categorie_331"],
                        "baza": _b(total - tva), "tva": _b(tva)})
    return prof, facturi


def genereaza(conn, schema, an, luna, manual=None):
    if luna < 1 or luna > 12:
        raise ValueError("Luna invalidă: %r" % luna)
    prof, facturi = pull(conn, schema, an, luna)
    res = calcul_d394(prof, an, luna, facturi, manual)
    return build_xml(res), res
