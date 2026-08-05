# -*- coding: utf-8 -*-
"""core/d205.py — D205 (Declaratie informativa privind impozitul retinut la sursa
si castigurile/pierderile realizate, pe beneficiari de venit).

REFACUT DE LA ZERO 16.07.2026, din ANAF structura D205 (OPANAF 102/2025)
(structura_D205_2025_120226.pdf, modif. 12.02.2026), citita INTEGRAL (461 linii,
dupa o prima incercare care citise doar primele ~180 si a ratat atributele reale
ale sect_II/benef - gasite mai departe in document).

Structura reala:
  <declaratie205 luna="12" an="AAAA" d_rec="0" cui="..." nume_declar="..."
                 prenume_declar="..." functie_declar="..." den="..." adresa="..."
                 totalPlata_A="...">
    <sect_II tip_venit="25" nrben="N" Tcastig="..." Tpierd="..." T_VB="..."
             T_GAR="..." Tbaza="..." Timp="...">   (1 per tip_venit, 1-n aparitii)
      <benef categ="1.a" nume1="..." rezid="1" cif="..." tip_plata="2"
             castig1/divid_D1="..." pierdere1/divid_P1="..." baza1="..."
             imp1="..."/>   (1-n aparitii)
    </sect_II>
  </declaratie205>

Reguli de calcul (din ANAF structura D205 (OPANAF 102/2025)):
  Tcastig = SUMA(castig1) pt. beneficiarii cu tip_venit1=25
  Tpierd  = SUMA(pierdere1) pt. beneficiarii cu tip_venit1=25
  Tbaza   = SUMA(baza1) pt. toti beneficiarii sectiunii
  Timp    = SUMA(imp1) pt. toti beneficiarii sectiunii
  nrben   = COUNT(beneficiari) din sectiune

tip_venit = 25 -> categoria uzuala pentru dividende (1.a). rezid=1 (rezident RO)
e cazul standard; statR/cifS raman goale pentru rezidenti.
"""
from __future__ import annotations

from core.common import text_anaf as _t, cheie_manual, LIMITE_TEXT_ANAF as _LIM  # limite text per-camp (03.08.2026)
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

NS = "mfp:anaf:dgti:d205:declaratie:v3"


def _esc(v):
    from xml.sax.saxutils import quoteattr
    return quoteattr(str(v if v is not None else ""))


def _i(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class Beneficiar:
    categ: str
    nume1: str
    cif: str
    baza1: int = 0
    imp1: int = 0
    castig1: int = 0
    pierdere1: int = 0
    tip_plata: str = "2"
    rezid: str = "1"


@dataclass
class RezultatD205:
    an: int
    prof: dict = field(default_factory=dict)
    beneficiari: list = field(default_factory=list)
    total_plata_a: int = 0


def calcul_d205(prof, an, beneficiari):
    """`beneficiari` = [{categ, nume, cif, baza?, imp?, castig?, pierdere?}]."""
    benef = []
    total_imp = 0
    for b in beneficiari or []:
        baza = _i(b.get("baza", 0))
        imp = _i(b.get("imp", 0))
        castig = _i(b.get("castig", 0))
        pierdere = _i(b.get("pierdere", 0))
        if baza <= 0 and imp <= 0 and castig <= 0 and pierdere <= 0:
            continue
        benef.append(Beneficiar(
            categ=str(b["categ"]), nume1=str(b.get("nume", "")).strip(),
            cif=str(b.get("cif", "")).strip(), baza1=baza, imp1=imp,
            castig1=castig, pierdere1=pierdere,
            tip_plata=str(b.get("tip_plata", "2"))))
        total_imp += imp
    # totalPlata_A = checksum ANAF (OPANAF 102/2025): nrben+Tcastig+Tpierd+T_VB+T_GAR+Tbaza+Timp.
    # La dividende (tip_venit 08) Tcastig/Tpierd/T_VB/T_GAR=0 (niciun tip_venit1=25), deci
    # checksum = nrben+Tbaza+Timp. SURSA UNICA (aliniat la d100 R11b): calcul_d205 il calculeaza,
    # build_xml il EMITE din res.total_plata_a - res.total_plata_a == totalPlata_A emis, mereu.
    _nrben = len(benef)
    _Tbaza = sum(b.baza1 for b in benef)
    _Timp = sum(b.imp1 for b in benef)
    _checksum = _nrben + _Tbaza + _Timp
    return RezultatD205(an=an, prof=prof, beneficiari=benef, total_plata_a=_checksum)


def erori_generare(prof):
    erori = []
    if not (prof.get("cui") or "").strip():
        erori.append("LIPSĂ CUI (obligatoriu).")
    if not (prof.get("nume") or "").strip():
        erori.append("LIPSĂ denumire firmă (obligatorie).")
    if not (prof.get("adresa") or "").strip():
        erori.append("LIPSĂ adresă domiciliu fiscal (obligatorie).")
    return erori


def build_xml(res):
    prof = res.prof
    if not res.beneficiari:
        raise ValueError("D205 fara niciun beneficiar de venit - nu se genereaza "
                         "declaratie fara continut.")

    # Tcastig/Tpierd, conform formulei oficiale, se calculeaza DOAR din
    # beneficiarii cu tip_venit1=25 ("Tcastig = suma(castig1) pt. tip_venit1=25").
    # La tip_venit=08 (dividende), NICIUN beneficiar nu are tip_venit1=25, deci
    # Tcastig/Tpierd raman 0.
    nrben = len(res.beneficiari)
    Tcastig = 0
    Tpierd = 0
    T_VB = 0
    T_GAR = 0
    Tbaza = sum(b.baza1 for b in res.beneficiari)
    Timp = sum(b.imp1 for b in res.beneficiari)
    # totalPlata_A = suma(nrben)+suma(Tcastig)+suma(Tpierd)+suma(T_VB)+
    # suma(T_GAR)+suma(Tbaza)+suma(Timp) - formula EXACTA din ANAF structura D205 (OPANAF 102/2025)
    # (nu doar Timp, cum pusesem prima data - DUK regula R15 respinsese exact asta:
    # cerea 11001, primea 1000).
    # SURSA UNICA: checksum-ul e calculat in calcul_d205 si tinut in res.total_plata_a;
    # aici il EMITEM din res (nu-l recalculam independent - capcana latenta d100). Gardul
    # golden test_total_plata_a_res_egal_checksum_emis leaga res == header == nrben+Tbaza+Timp.
    total_control = res.total_plata_a

    H = ['<?xml version="1.0" encoding="UTF-8"?>']
    hdr = ('<declaratie205 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
           'xmlns="%s" xsi:schemaLocation="%s D205.xsd" '
           'luna="12" an="%d" d_rec="0" '
           'nume_declar=%s prenume_declar=%s functie_declar=%s '
           'cui="%s" den=%s adresa=%s totalPlata_A="%d">'
           % (NS, NS, res.an,
              _esc(_t(prof.get("declarant_nume") or "ADMINISTRATOR", _LIM["d205"]["nume_declar"])),
              _esc(_t(prof.get("declarant_prenume") or "-", _LIM["d205"]["prenume_declar"])),
              _esc(_t(prof.get("declarant_functie") or "ADMINISTRATOR", _LIM["d205"]["functie_declar"])),  # C(50) ANAF (DUK: 51 respins)
              "".join(ch for ch in str(prof.get("cui") or "") if ch.isdigit()),
              _esc(_t(prof.get("nume"), _LIM["d205"]["den"])), _esc(_t(prof.get("adresa"), _LIM["d205"]["adresa"])), total_control))  # den C(200)/adresa C(1000) ANAF (DUK 201/1001 respinse)
    H.append(hdr)
    # sect_II se INCHIDE (linia 26 din ANAF structura D205 (OPANAF 102/2025)) INAINTE de <benef>
    # (linia 27) - sunt elemente FRATI, ambele copii ai radacinii, nu benef in
    # interiorul lui sect_II. Gresit prima data: pusesem benef in interiorul lui
    # sect_II. "sectiunea benef este gresit pozitionata" - eroarea validatorului
    # spunea exact asta.
    # tip_venit "08" = dividende (categ 1.a), NU "25" (alta categorie, unde
    # baza1/imp1 sunt interzise - R44/R45 respinsesera exact asta). Confirmat
    # din ANAF structura D205 (OPANAF 102/2025): "08 1.a) venituri din dividende".
    H.append('  <sect_II tip_venit="08" nrben="%d" Tcastig="%d" Tpierd="%d" '
             'T_VB="%d" T_GAR="%d" Tbaza="%d" Timp="%d"/>'
             % (nrben, Tcastig, Tpierd, T_VB, T_GAR, Tbaza, Timp))
    # den1 (nu nume1), cifR (nu cif), Rezid cu majuscula, tip_venit1 pe FIECARE
    # beneficiar, id_inreg secvential. "categ" NU e atribut valid - respins ca
    # necunoscut de validator; categoria (1.a) e implicita in tip_venit1=08.
    # La tip_venit1=08 se completeaza si divid_D/divid_P (suma bruta a
    # dividendului), pe langa baza1/imp1 - confirmat din formatul oficial de
    # import: "categ(1.a),...,2,divid_D,divid_P,baza,imp".
    for idx, b in enumerate(res.beneficiari, start=1):
        H.append('  <benef id_inreg="%d" den1=%s tip_venit1="08" '
                 'Rezid="1" cifR="%s" tip_plata="%s" '
                 'divid_D="%d" divid_P="%d" baza1="%d" imp1="%d"/>'
                 % (idx, _esc(_t(b.nume1, _LIM["d205"]["den1"])),  # den1 C(100) ANAF (DUK: 101 respins)
                    "".join(ch for ch in b.cif if ch.isdigit()),
                    b.tip_plata, b.castig1, b.pierdere1, b.baza1, b.imp1))
    H.append("</declaratie205>")
    return "\n".join(H)


def pull(conn, schema, perioada):
    """Profil + asociatii cu cota>0 + total dividende distribuite (cont debit 457, note VALIDATE)
    in fereastra anului [inceput, sfarsit) din perioada.interval()."""
    import psycopg2.extras as _E
    _inc, _sf = perioada.interval()
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT nume, cui, adresa, oras, judet, "
                    "declarant_nume, declarant_prenume, declarant_functie "
                    "FROM firma_profil WHERE id = 1")
        prof = cur.fetchone() or {}
        if prof.get("oras"):
            prof["adresa"] = " ".join(x for x in
                (prof.get("adresa"), prof.get("oras"), prof.get("judet")) if x)
        cur.execute("SELECT nume, cnp, cota FROM asociati WHERE cota > 0")
        asoc = cur.fetchall()
        cur.execute(
            "SELECT COALESCE(SUM(l.suma),0) AS total FROM inregistrari_linii l "
            "JOIN inregistrari i ON i.id = l.inregistrare_id "
            "WHERE i.status='validata' AND l.cont_debit LIKE '457%%' "
            "AND i.data >= %s AND i.data < %s", (_inc.isoformat(), _sf.isoformat()))
        total_div = _i((cur.fetchone() or {"total": 0})["total"])
    return prof, asoc, total_div


def genereaza(conn, schema, perioada, manual=None):
    """D205 anual (contract uniform A1). `manual` cu cheia 'beneficiari' suprascrie lista calculata
    automat din dividendele distribuite asociatilor (cota din tabelul `asociati`, suma din notele
    VALIDATE pe contul 457, impozit pe dividende PERIOD-AWARE - cota("impozit_dividend"):
    10% pana in 2025, 16% de la 01.01.2026 (Legea 141/2025, CF art.97). Foloseste perioada.an."""
    from core.common import cota as _cota205
    from datetime import date as _date205
    manual = cheie_manual(manual, "beneficiari")
    prof, asoc, total_div = pull(conn, schema, perioada)

    erori = erori_generare(prof)
    if erori:
        raise ValueError(" ".join(erori))

    beneficiari = manual.get("beneficiari")
    if beneficiari is None:
        beneficiari = []
        if total_div > 0 and asoc:
            for a in asoc:
                parte = _i(Decimal(total_div) * Decimal(str(a["cota"])) / Decimal(100))
                if parte > 0:
                    # impozit pe dividende PERIOD-AWARE: cota 10% pana in 2025, 16% de la
                    # 01.01.2026 (Legea 141/2025, CF art.97 - "cota de impozit de 16% asupra
                    # dividendului brut"). Data = anul declaratiei (dividende platite in an).
                    _cota_div = _cota205("impozit_dividend", _date205(perioada.an, 12, 31))[0]
                    impozit = _i(Decimal(parte) * _cota_div)
                    beneficiari.append({"categ": "1.a", "nume": a["nume"],
                                        "cif": a.get("cnp") or "", "baza": parte,
                                        "imp": impozit, "castig": parte, "pierdere": 0,
                                        "tip_plata": "2"})

    res = calcul_d205(prof, perioada.an, beneficiari)
    # POARTA A DOUA CALE (gard continut, 05.08.2026, pas 6/6): recalcul INDEPENDENT al bazei/
    # impozitului pe dividende din 457 (NU cross-check cu D100 = same-source trap).
    from core.d205_reconciliere import verifica_reconciliere as _vr205
    _vr205(conn, schema, perioada, res, manual)
    xml = build_xml(res)
    return xml, res
