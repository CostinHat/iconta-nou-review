"""
Modul D101 — Declarația privind impozitul pe profit (ANAF v10, OPANAF 206/2025).
universalCode D101_A600. An sfârșit exercițiu >= 2024.

REFĂCUT DE LA ZERO după structura OFICIALĂ ANAF (structura_D101_2024_200225).

Formulele oficiale P1-P53 în cascadă, inclusiv IMCA (impozit minim cifră afaceri):
  P3  = P1 - P2                         (rezultat exploatare)
  P6  = P4 - P5                         (rezultat financiar)
  P7  = P3 + P6                         (rezultat brut)
  P10 = P7 + P8 - P9                    (după elemente similare)
  P16 = P11+P12+P13+P14+P15             (total deduceri)
  P21 = P17+P18+P19+P20                 (total venituri neimpozabile)
  P22 = P10 - P16 - P21                 (profit/pierdere)
  P34 = P23..P33                        (total cheltuieli nedeductibile)
  P35 = P22 + P34                       (profit impozabil brut)
  P38a= P35+P36+P37-P38
  P40 = max(P38a - P39a, 0)             (profit impozabil)
  P411= round(16% × P40)                (impozit la 16%)
  P41 = P411 + P412
  P48 = P481 (dacă P46>=P47) sau P482 (IMCA, dacă P47>P46)
  P481= max(P41-P42-P43-P44-P45, 0)     (impozit normal)
  P482= max(P47-P421-P431-P43a, 0)      (impozit la nivel IMCA)
  P52 = max((P48+P51)-(P49+P50), 0)     (diferență de plată)
  P53 = max((P49+P50)-(P48+P51), 0)     (diferență de recuperat)

Cota standard 16%. IMCA = 1% cifră afaceri (doar firme cu CA > 50 mil EUR an precedent).
cod_obligatie: 102/103/104/105 (103 = PJ române obișnuite).

Separare strictă: calcul pur / validare / XML / DB / orchestrare.
"""
import re
from core import common as c
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d101:declaratie:v10"
REGULI = "2026.1"
_NEDIGIT = re.compile(r"\D")
COTA_PROFIT = Decimal("0.16")
COTA_IMCA = Decimal("0.01")
PRAG_IMCA_EUR = 50_000_000


def _esc(v):
    s = "" if v is None else str(v)
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&apos;"))


def _r0(x):
    return int(Decimal(str(x or 0)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Rezultat:
    an: int
    prof: dict
    P: dict = field(default_factory=dict)
    impozit_datorat: int = 0
    de_plata: int = 0
    de_recuperat: int = 0
    aplica_imca: bool = False
    total_plata_a: int = 0
    avertismente: list = field(default_factory=list)


def calcul_d101(prof, an, date, ca_an_precedent_eur=0):
    """
    Calcul PUR al impozitului pe profit după formulele oficiale.
    date: dict cu intrările contabile (venituri, cheltuieli, deduceri, etc.)
          chei posibile: venituri_exploatare, cheltuieli_exploatare,
          venituri_financiare, cheltuieli_financiare, elem_sim_venit, elem_sim_chelt,
          amortizare_fiscala, rezerva_legala, alte_deduceri, venituri_neimpozabile,
          cheltuieli_nedeductibile, pierdere_precedenta, plati_anticipate_d100,
          sponsorizare, credit_fiscal_extern, impozit_scutit, etc.
    ca_an_precedent_eur: cifra de afaceri an precedent în EUR (pentru IMCA).
    """
    d = lambda k: Decimal(str(date.get(k, 0) or 0))
    P = {}

    # --- rezultat contabil ---
    P["P1"] = _r0(d("venituri_exploatare"))
    P["P2"] = _r0(d("cheltuieli_exploatare"))
    P["P3"] = P["P1"] - P["P2"]
    P["P4"] = _r0(d("venituri_financiare"))
    P["P5"] = _r0(d("cheltuieli_financiare"))
    P["P6"] = P["P4"] - P["P5"]
    P["P7"] = P["P3"] + P["P6"]

    # elemente similare
    P["P8"] = _r0(d("elem_sim_venit"))
    P["P9"] = _r0(d("elem_sim_chelt"))
    P["P10"] = P["P7"] + P["P8"] - P["P9"]

    # deduceri
    P["P11"] = _r0(d("amortizare_fiscala"))
    P["P12"] = _r0(d("cheltuieli_dobanzi_ded"))
    P["P13"] = _r0(d("rezerva_legala"))
    P["P14"] = _r0(d("provizioane_fiscale"))
    P["P15"] = _r0(d("alte_deduceri"))
    P["P16"] = P["P11"] + P["P12"] + P["P13"] + P["P14"] + P["P15"]

    # venituri neimpozabile
    P["P17"] = _r0(d("venituri_dividende_neimp"))
    P["P18"] = _r0(d("venituri_titluri"))
    P["P19"] = _r0(d("venituri_lichidare"))
    P["P20"] = _r0(d("alte_venituri_neimp"))
    P["P21"] = P["P17"] + P["P18"] + P["P19"] + P["P20"]

    # profit/pierdere
    P["P22"] = P["P10"] - P["P16"] - P["P21"]

    # cheltuieli nedeductibile (P23..P33)
    P["P23"] = _r0(d("chelt_impozit_profit"))
    P["P24"] = _r0(d("chelt_impozit_strainatate"))
    P["P25"] = _r0(d("dobanzi_penalitati"))
    P["P26"] = _r0(d("protocol_peste_limita"))
    P["P27"] = _r0(d("sponsorizare_chelt"))
    P["P28"] = _r0(d("amortizare_contabila"))
    P["P29"] = _r0(d("provizioane_nededuct"))
    P["P30"] = _r0(d("chelt_art25_10"))
    P["P31"] = _r0(d("dobanzi_reportate"))
    P["P32"] = _r0(d("chelt_venituri_neimp"))
    P["P33"] = _r0(d("alte_chelt_nededuct"))
    P["P34"] = sum(P["P%d" % i] for i in range(23, 34))

    # profit impozabil
    P["P35"] = P["P22"] + P["P34"]
    P["P36"] = _r0(d("pierdere_de_reportat"))
    P["P37"] = _r0(d("pierdere_transferata"))
    P["P38"] = _r0(d("pierdere_primita"))
    P["P38a"] = P["P35"] + P["P36"] + P["P37"] - P["P38"]
    P["P39"] = _r0(d("pierdere_precedenta"))
    # P39a: pierdere recuperabilă în an, limitată la P39 și la profit
    p39a = min(P["P39"], max(P["P38a"], 0)) if P["P38a"] > 0 else 0
    P["P39a"] = p39a

    # profit impozabil aferent anului
    if P["P38a"] >= 0 and P["P39a"] >= 0 and (P["P38a"] - P["P39a"]) > 0:
        P["P40"] = P["P38a"] - P["P39a"]
    else:
        P["P40"] = 0
    if P["P38a"] < 0:
        P["P40a"] = -P["P38a"]

    # impozit 16%
    P["P411"] = _r0(Decimal(P["P40"]) * COTA_PROFIT)
    P["P412"] = _r0(d("impozit_5la_suta_baruri"))
    P["P41"] = P["P411"] + P["P412"]

    # credite fiscale / scutiri
    P["P421"] = _r0(d("credit_fiscal_extern"))
    P["P422"] = _r0(d("impozit_scutit"))
    P["P423"] = _r0(d("scutiri_reduceri"))
    P["P42"] = P["P421"] + P["P422"] + P["P423"]

    # sponsorizare în limită (max 20% din P41-P42)
    spons_disp = _r0(d("sponsorizare_credit"))
    lim_spons = _r0((Decimal(P["P41"]) - Decimal(P["P42"])) * Decimal("0.20"))
    P["P43"] = max(0, min(spons_disp, lim_spons))
    P["P44"] = _r0(d("alte_sume_scad"))
    P["P45"] = _r0(d("reducere_oug153"))

    # IMCA
    aplica_imca = ca_an_precedent_eur > PRAG_IMCA_EUR
    P["P43a"] = _r0(d("credit_cercetare_imca"))
    if aplica_imca:
        # IMCA = 1% din cifra de afaceri ajustată (simplificat: venituri totale)
        ca_lei = Decimal(str(date.get("cifra_afaceri_lei", 0) or 0))
        P["P46"] = _r0(Decimal(P["P40"]) * COTA_PROFIT)   # impozit profit pt comparație
        P["P47"] = _r0(ca_lei * COTA_IMCA)                # IMCA
    else:
        P["P46"] = 0
        P["P47"] = 0

    # impozit normal (P481) vs IMCA (P482)
    v_normal = max(P["P41"] - P["P42"] - P["P43"] - P["P44"] - P["P45"], 0)
    v_imca = max(P["P47"] - P["P421"] - P["P43"] - P["P43a"], 0)
    if P["P46"] == 0 and P["P47"] == 0:
        P["P481"] = v_normal
        P["P482"] = 0
        P["P48"] = v_normal
    elif P["P46"] >= P["P47"]:
        P["P481"] = v_normal
        P["P482"] = 0
        P["P48"] = v_normal
    else:
        P["P481"] = 0
        P["P482"] = v_imca
        P["P48"] = v_imca

    # diferențe față de plățile anticipate
    P["P49"] = _r0(d("impozit_inspectie"))
    P["P50"] = _r0(d("plati_anticipate_d100"))
    P["P51"] = _r0(d("dif_restituire_spons"))
    dif_plata = (P["P48"] + P["P51"]) - (P["P49"] + P["P50"])
    P["P52"] = max(dif_plata, 0)
    P["P53"] = max(-dif_plata, 0)

    # totalPlata_A = suma P1..P53 (fără rândurile "din care")
    randuri_principale = ["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10",
        "P11","P12","P13","P14","P15","P16","P17","P18","P19","P20","P21","P22",
        "P23","P24","P25","P26","P27","P28","P29","P30","P31","P32","P33","P34",
        "P35","P36","P37","P38","P39","P40","P41","P42","P43","P44","P45","P46",
        "P47","P48","P49","P50","P51","P52","P53"]
    total = sum(P.get(k, 0) for k in randuri_principale)

    res = Rezultat(an=an, prof=prof, P=P, impozit_datorat=P["P48"],
                   de_plata=P["P52"], de_recuperat=P["P53"], aplica_imca=aplica_imca,
                   total_plata_a=total)
    if aplica_imca and P["P48"] == P["P482"] and P["P482"] > 0:
        res.avertismente.append("IMCA aplicat: impozit la nivelul cifrei de afaceri (%d lei) > impozit profit normal." % P["P482"])
    res.avertismente.append("D101 %d: profit impozabil %d lei, impozit datorat %d lei, %s %d lei."
        % (an, P["P40"], P["P48"],
           "de plată" if P["P52"] else ("de recuperat" if P["P53"] else "achitat"),
           P["P52"] or P["P53"]))
    return res


def valideaza(res):
    erori = []
    prof = res.prof
    P = res.P
    if not _NEDIGIT.sub("", prof.get("cui") or ""):
        erori.append("LIPSĂ CIF firmă.")
    if not _NEDIGIT.sub("", prof.get("caen") or ""):
        erori.append("LIPSĂ CAEN (obligatoriu la D101).")
    if not prof.get("nume"):
        erori.append("LIPSĂ denumire.")
    # verificări de coerență formule
    if P.get("P3") != P.get("P1", 0) - P.get("P2", 0):
        erori.append("P3 incoerent (rezultat exploatare).")
    if P.get("P7") != P.get("P3", 0) + P.get("P6", 0):
        erori.append("P7 incoerent (rezultat brut).")
    if P.get("P22") != P.get("P10", 0) - P.get("P16", 0) - P.get("P21", 0):
        erori.append("P22 incoerent (profit/pierdere).")
    if P.get("P52", 0) and P.get("P53", 0):
        erori.append("P52 și P53 se exclud reciproc (nu pot fi ambele > 0).")
    return erori


def build_xml(res):
    prof = res.prof
    cif = _NEDIGIT.sub("", prof.get("cui") or "")
    caen = _NEDIGIT.sub("", prof.get("caen") or "")
    den = prof.get("nume") or ""
    adr = " ".join(x for x in [prof.get("adresa"), prof.get("oras"), prof.get("judet")] if x).strip() or den
    an = res.an
    scad = "2506%02d" % (an % 100)   # 25.06.an+... simplificat pentru cod 103
    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie101 xmlns="%s" d_rec="0" d_reg="0" d_anulare="0" d_succ="0" '
           'd_alte="0" d_reglem="0" cod_obligatie="103" '
           'luna_i="1" an_i="%d" luna="12" an="%d" '
           'scadenta="%s" cod_bug="5503XXXXXX" '
           'nume_declar="%s" prenume_declar="%s" functie_declar="%s" '
           'cif="%s" caen="%s" denumire="%s" adresa="%s" totalPlata_A="%d">'
           % (NS, an, an, scad,
              _esc(prof.get("declarant_nume") or den or "ADMINISTRATOR"),
              _esc(prof.get("declarant_prenume") or "-"),
              _esc(prof.get("declarant_functie") or "ADMINISTRATOR"),
              _esc(cif), _esc(caen or "0"), _esc(den), _esc(adr), res.total_plata_a))
    H.append(hdr)
    for k in sorted(res.P.keys(), key=lambda x: (len(x), x)):
        v = res.P[k]
        if v:
            H.append('  <%s>%d</%s>' % (k, v, k))
    H.append('</declaratie101>')
    return "\n".join(H)


def pull(conn, schema, an):
    import psycopg2.extras as _E
    inceput = "%04d-01-01" % an
    sfarsit = "%04d-01-01" % (an + 1)
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, caen, adresa, oras, judet, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        # agregare din balanță / înregistrări contabile (clase 6 = cheltuieli, 7 = venituri)
        date = {}
        try:
            cur.execute("""SELECT
                COALESCE(SUM(CASE WHEN cont LIKE '7%%' AND cont NOT LIKE '76%%' THEN credit-debit ELSE 0 END),0) AS ven_expl,
                COALESCE(SUM(CASE WHEN cont LIKE '6%%' AND cont NOT LIKE '66%%' THEN debit-credit ELSE 0 END),0) AS chelt_expl,
                COALESCE(SUM(CASE WHEN cont LIKE '76%%' THEN credit-debit ELSE 0 END),0) AS ven_fin,
                COALESCE(SUM(CASE WHEN cont LIKE '66%%' THEN debit-credit ELSE 0 END),0) AS chelt_fin
                FROM inregistrari_linii l JOIN inregistrari i ON i.id=l.inregistrare_id
                WHERE i.data >= %s AND i.data < %s""", (inceput, sfarsit))
            r = cur.fetchone() or {}
            date = {"venituri_exploatare": r.get("ven_expl", 0),
                    "cheltuieli_exploatare": r.get("chelt_expl", 0),
                    "venituri_financiare": r.get("ven_fin", 0),
                    "cheltuieli_financiare": r.get("chelt_fin", 0)}
        except Exception:
            date = {}
    return prof, date


def genereaza(conn, schema, an, date_extra=None, ca_an_precedent_eur=0):
    prof, date = pull(conn, schema, an)
    if date_extra:
        date.update(date_extra)
    res = calcul_d101(prof, an, date, ca_an_precedent_eur)
    return build_xml(res), res
