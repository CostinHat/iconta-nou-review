"""
Modul D205 — Declarația informativă privind impozitul reținut la sursă, veniturile
din jocuri de noroc și câștigurile/pierderile din investiții, pe beneficiari de venit
(ANAF v3, OPANAF 102/2025, structură modif. 12.02.2026).

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D205_2025_120226).

Separare strictă: calcul pur / validare / XML / DB / orchestrare.

D205 e ANUALĂ (luna=12 obligatoriu).
Tipuri venit valide: 04,08,09,11,12,16,18,25,26,27,28,29,30.
Dividende = tip 08 (cota 8%/2024, 10%/2025, 16%/2026), emite divid_D + divid_P.
totalPlata_A = Σnrben + ΣTcastig + ΣTpierd + ΣT_VB + ΣT_GAR + ΣTbaza + ΣTimp.
"""
import re
from core import common as c
from dataclasses import dataclass, field

NS = "mfp:anaf:dgti:d205:declaratie:v3"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")

# tipuri venit oficiale (2026)
TIPURI_VENIT = {"04", "08", "09", "11", "12", "16", "18", "25", "26", "27", "28", "29", "30"}
# cote impozit pe tip venit (oficial)
COTE = {"04": 0.10, "09": 0.10, "11": 0.10, "12": 0.10, "16": 0.10,
        "26": 0.01, "27": 0.03, "28": 0.10, "29": 0.10}
# tip_plata implicit (regim fiscal): 2 = impozit final
TIP_PLATA = {t: 2 for t in TIPURI_VENIT}
TIP_PLATA["25"] = 0   # câștiguri aur investiții -> nu se completează


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _int(x):
    try:
        return int(round(float(x or 0)))
    except Exception:
        return 0


def rata_dividende(an):
    """Cota impozit dividende (tip 08), oficial."""
    if an <= 2024:
        return 0.08
    if an == 2025:
        return 0.10
    return 0.16   # 2026+


def distribuie_dividende(asociati, total_brut, an):
    """PUR: distribuie dividendul pe asociați după cote. -> (beneficiari, avertismente)."""
    rate = rata_dividende(an)
    benefs = []
    for a in asociati:
        cota = float(a.get("cota") or 0)
        suma = round(total_brut * cota / 100.0)
        imp = round(suma * rate)
        benefs.append({"tip_venit": "08", "nume": a.get("nume"), "cnp": a.get("cnp"),
                       "rezid": 1, "suma_bruta": suma, "impozit": imp,
                       "divid_d": suma, "divid_p": suma})
    av = []
    suma_cote = sum(float(a.get("cota") or 0) for a in asociati)
    if abs(suma_cote - 100) > 0.01:
        av.append("Suma cotelor e %g%%, nu 100%% — verifică." % suma_cote)
    return benefs, av


@dataclass
class Rezultat:
    an: int
    prof: dict
    benef_xml: list = field(default_factory=list)
    sect_ii: dict = field(default_factory=dict)    # tip -> {nrben, Tbaza, Timp, Tcastig, Tpierd, T_VB, T_GAR}
    nr_beneficiari: int = 0
    total_impozit: int = 0
    total_baza: int = 0
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d205(prof, benefs, an):
    """PUR: construiește datele D205 din lista de beneficiari."""
    by_tip = {}
    rows = []
    tot_imp = sum_baza = 0
    for idx, b in enumerate(benefs, 1):
        tip = b.get("tip_venit") or "08"
        suma = _int(b.get("suma_bruta"))
        imp = _int(b.get("impozit"))
        cnp = _NEDIGIT.sub("", b.get("cnp") or "")
        nume = b.get("nume") or ""
        rezid = int(b.get("rezid") or 1)
        tip_plata = TIP_PLATA.get(tip, 2)
        d = by_tip.setdefault(tip, {"nrben": 0, "Tbaza": 0, "Timp": 0,
                                    "Tcastig": 0, "Tpierd": 0, "T_VB": 0, "T_GAR": 0})
        if tip == "08":
            divid_d = _int(b.get("divid_d") or suma)
            divid_p = _int(b.get("divid_p") or suma)
            rows.append('  <benef id_inreg="%d" tip_venit1="08" den1="%s" Rezid="%d" cifR="%s" '
                        'tip_plata="%d" divid_D="%d" divid_P="%d" baza1="%d" imp1="%d"/>'
                        % (idx, _esc(nume), rezid, cnp, tip_plata, divid_d, divid_p, suma, imp))
            d["Tbaza"] += suma; d["Timp"] += imp
        elif tip == "25":
            castig = _int(b.get("castig"))
            pierdere = _int(b.get("pierdere"))
            rows.append('  <benef id_inreg="%d" tip_venit1="25" den1="%s" Rezid="%d" cifR="%s" '
                        'tip_plata="0" castig1="%d" pierdere1="%d"/>'
                        % (idx, _esc(nume), rezid, cnp, castig, pierdere))
            d["Tcastig"] += castig; d["Tpierd"] += pierdere
        else:
            rows.append('  <benef id_inreg="%d" tip_venit1="%s" den1="%s" Rezid="%d" cifR="%s" '
                        'tip_plata="%d" baza1="%d" imp1="%d"/>'
                        % (idx, tip, _esc(nume), rezid, cnp, tip_plata, suma, imp))
            d["Tbaza"] += suma; d["Timp"] += imp
        d["nrben"] += 1
        tot_imp += imp; sum_baza += suma

    # totalPlata_A oficial
    total_plata = 0
    for d in by_tip.values():
        total_plata += (d["nrben"] + d["Tcastig"] + d["Tpierd"]
                        + d["T_VB"] + d["T_GAR"] + d["Tbaza"] + d["Timp"])

    res = Rezultat(an=an, prof=prof, benef_xml=rows, sect_ii=by_tip,
                   nr_beneficiari=len(benefs), total_impozit=tot_imp, total_baza=sum_baza,
                   total_plata_a=total_plata)
    res.avertismente.append("D205 an %d: %d beneficiari, impozit total %d lei." % (an, len(benefs), tot_imp))
    return res


def valideaza(res):
    erori = []
    prof = res.prof
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CUI plătitor de venit.")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire plătitor.")
    if not prof.get("adresa"):
        erori.append("LIPSĂ adresă plătitor.")
    for tip in res.sect_ii:
        if tip not in TIPURI_VENIT:
            erori.append("Tip venit %s invalid (nu e în nomenclatorul oficial)." % tip)
    # coerență totalPlata_A
    calc = 0
    for d in res.sect_ii.values():
        calc += d["nrben"] + d["Tcastig"] + d["Tpierd"] + d["T_VB"] + d["T_GAR"] + d["Tbaza"] + d["Timp"]
    if calc != res.total_plata_a:
        erori.append("totalPlata_A incoerent.")
    return erori


def build_xml(res):
    prof = res.prof
    cui = _NEDIGIT.sub("", prof.get("cui") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip() or den
    tel = prof.get("telefon") or ""
    mail = prof.get("email") or ""
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie205 xmlns="%s" luna="12" an="%d" d_rec="0" d_succ="0" '
           'nume_declar="%s" prenume_declar="%s" functie_declar="%s" '
           'cui="%s" den="%s" adresa="%s"'
           % (NS, res.an,
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
    for tip in sorted(res.sect_ii):
        d = res.sect_ii[tip]
        H.append('  <sect_II tip_venit="%s" nrben="%d" Tcastig="%d" Tpierd="%d" '
                 'T_VB="%d" T_GAR="%d" Tbaza="%d" Timp="%d"/>'
                 % (tip, d["nrben"], d["Tcastig"], d["Tpierd"], d["T_VB"], d["T_GAR"], d["Tbaza"], d["Timp"]))
    H.extend(res.benef_xml)
    H.append('</declaratie205>')
    return "\n".join(H)


def ensure_tabel_benef(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS d205_beneficiari (
        id SERIAL PRIMARY KEY, an integer, tip_venit text DEFAULT '08',
        nume text, cnp text, rezid integer DEFAULT 1,
        suma_bruta numeric DEFAULT 0, impozit numeric DEFAULT 0,
        creat timestamp DEFAULT now())""")


def ensure_tabel_asoc(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS asociati (
        id SERIAL PRIMARY KEY, nume text, cnp text, cota numeric DEFAULT 0,
        creat timestamp DEFAULT now())""")


def pull(conn, schema, an):
    import psycopg2.extras as _E
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, email, telefon, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        ensure_tabel_benef(cur)
        cur.execute("SELECT tip_venit, nume, cnp, rezid, suma_bruta, impozit "
                    "FROM d205_beneficiari WHERE an = %s ORDER BY id", (an,))
        benefs = [dict(r) for r in cur.fetchall()]
    conn.commit()
    return prof, benefs


def genereaza(conn, schema, an):
    prof, benefs = pull(conn, schema, an)
    res = calcul_d205(prof, benefs, an)
    return build_xml(res), res
