"""
core/common.py — STRAT COMUN MIC ȘI STABIL.

Singurul cod partajat între module. Conține:
  - normalizare bani (Decimal): _dec, _q
  - contractul de rezultat al verificărilor (ok/cod/mesaj/așteptat/găsit/temei/nivel)
  - dicționarul unic coduri -> (mesaj, temei) — nicio greșeală fără justificare
  - tabela de cote/plafoane cu DATĂ de valabilitate (din când e validă o valoare)

Reguli de dependență (graf aciclic, fără interferențe între module):
  - modulele importă DOAR din common
  - common NU importă din module
  - main.py importă din module; modulele NU știu de main.py
"""
from __future__ import annotations
import os
from collections import defaultdict
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

VERSIUNE_COMMON = "2026.1"


def cfg(cheie, default="", cast=str):
    """Config din env citită LA APEL, nu la import (item 5 DE_FACUT). Ordinea de
    import devine irelevantă (nu mai îngheață o valoare goală sub pytest), iar o
    valoare schimbată în env nu mai cere restart de proces ca să fie citită.
    `default` e string (ca env), `cast` îl convertește la tipul real (int/float)."""
    return cast(os.environ.get(cheie, default))


def cfg_secret(cheie):
    """Secret din env, citit LA APEL, cu EXCEPȚIE DURĂ la absență/gol — NICIODATĂ default,
    NICIODATĂ None tăcut. Un secret gol pe o cheie HMAC = bypass complet de autentificare
    (tokenuri forjabile cu cheie goală, publică). De aceea nu are default (vezi DECIZII 22.07).
    Se folosește pentru JWT_SECRET etc. — nu pentru config obișnuit (ăla e cfg())."""
    v = os.environ.get(cheie, "")
    if not v:
        raise RuntimeError(
            "secret obligatoriu absent din env: %s — refuz să semnez/verific cu cheie goală "
            "(ar face tokenurile forjabile). Setează %s în env." % (cheie, cheie))
    return v


def azi_ro(acum=None):
    """Data calendaristică în Europe/Bucharest, pentru VERDICTE de zi (la termen vs întârziat,
    fereastra UIT e-Transport, cron alerte) — robustă la fusul procesului, spre deosebire de
    date.today() care urmează OS TZ și ar sări ziua pe un server UTC. Se folosește DOAR unde ziua
    decide un verdict; restul (afișare/context) rămâne date.today(). `acum` (datetime aware) =
    hook de test determinist. Vezi DECIZII 22.07."""
    import datetime, zoneinfo
    buc = zoneinfo.ZoneInfo("Europe/Bucharest")
    acum = acum if acum is not None else datetime.datetime.now(buc)
    return acum.astimezone(buc).date()

_CENT = Decimal("0.01")

# nivelurile unei probleme semnalate
BLOCANT = "blocant"        # nu se poate depune/contabiliza
AVERTISMENT = "avertisment"  # legal, dar riscant (ex. sold peste plafon)


# ============================================================
#  BANI — Decimal, niciodată float
# ============================================================
def _dec(x) -> Decimal:
    """Normalizează la Decimal. Acceptă int/float/Decimal sau string RO ('1.234,56')."""
    if isinstance(x, Decimal):
        return x
    if isinstance(x, (int, float)):
        return Decimal(str(x))
    s = str(x).strip().replace(" ", "")
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return Decimal(s)


def _q(x) -> Decimal:
    """Rotunjește la 2 zecimale (ban)."""
    return _dec(x).quantize(_CENT, rounding=ROUND_HALF_UP)


def este_decimal(x) -> bool:
    """Gardă: un ban trebuie să fie Decimal, nu float. Folosit de teste."""
    return isinstance(x, Decimal)


# ============================================================
#  DICȚIONAR UNIC DE GREȘELI — cod -> (mesaj_șablon, temei legal)
#  Nicio eroare nu poate fi semnalată fără intrare aici.
# ============================================================
CODURI = {
    # — partidă dublă / note —
    "NOTA_NEECHILIBRATA": (
        "Notă neechilibrată: debit {debit} ≠ credit {credit}.",
        "OMFP 1802/2014 — principiul partidei duble"),
    "TREZORERIE_NEGATIVA": (
        "Cont de trezorerie {cont} cu sold creditor {sold} — nu poți avea bani negativi în casă/cont.",
        "OMFP 1802/2014 — conturi de trezorerie (clasa 5)"),
    # — TVA —
    "TVA_COTA_GRESITA": (
        "TVA declarat {gasit} lei, dar baza {baza} × {cota_pct}% = {asteptat} lei. Diferență {diferenta} lei.",
        "Legea 141/2025 — cota standard TVA 21% din 01.08.2025"),
    "BALANTA_INEGALA": (
        "Balanță dezechilibrată: sume debitoare {debit} ≠ sume creditoare {credit}.",
        "OMFP 1802/2014 — egalitatea balanței de verificare"),
    "BALANTA_SI_DEZECHILIBRATA": (
        "Solduri inițiale dezechilibrate: diferența {diferenta_solduri} lei "
        "(SI debitoare ≠ SI creditoare) — verifică introducerea soldurilor.",
        "OMFP 1802/2014 — egalitatea balanței de verificare"),
    # — plafoane numerar (Legea 70/2015) —
    "PLAFON_SOLD_CASA": (
        "Sold casierie {gasit} lei la sfârșitul zilei {zi} > plafon {asteptat} lei.",
        "Legea 70/2015 art. 4^2 — plafon sold casierie"),
    "PLAFON_INCASARE_PJ": (
        "Încasare {gasit} lei de la persoana juridică {partener} > {asteptat} lei/zi.",
        "Legea 70/2015 art. 3 alin. (1) lit. a)"),
    "PLAFON_PLATA_PJ": (
        "Plată {gasit} lei către persoana juridică {partener} > {asteptat} lei/zi.",
        "Legea 70/2015 art. 3 alin. (1) lit. c)"),
    "PLAFON_PLATA_PJ_TOTAL": (
        "Total plăți către persoane juridice {gasit} lei în ziua {zi} > {asteptat} lei.",
        "Legea 70/2015 art. 3 alin. (1) lit. c)"),
    "PLAFON_PF": (
        "Operațiune {gasit} lei cu persoana fizică {partener} > {asteptat} lei.",
        "Legea 70/2015 art. 3 — operațiuni cu persoane fizice"),
    "PLAFON_AVANS": (
        "Avans spre decontare {gasit} lei pentru {partener} > {asteptat} lei/zi.",
        "Legea 70/2015 art. 3 alin. (1) lit. e) (OUG 115/2023)"),
    # — declarații / scadențe —
    "DECLARATIE_INTARZIATA": (
        "Declarația {tip} pentru {perioada} avea termen {scadenta} — depășit.",
        "Calendar ANAF — termen depunere"),
}


def problema(cod, nivel=BLOCANT, **campuri):
    """
    Construiește o problemă semnalată cu justificare completă.
    Niciodată doar 'False' sau []: întotdeauna ce e greșit, ce se aștepta, temeiul.
    """
    if cod not in CODURI:
        raise ValueError(f"cod de eroare neînregistrat în common.CODURI: {cod!r}")
    sablon, temei = CODURI[cod]
    # Câmpurile MONETARE se formatează canonic (1.234,56) DOAR pentru mesaj — șabloanele CODURI au deja
    # sufixul „lei", deci bani() fără monedă. Valorile brute rămân în return (folosite programatic de
    # apelanți). Sursă unică de formatare: pdf_util.bani (DS cap.7). Orice câmp monetar NOU dintr-un
    # șablon TREBUIE adăugat aici, altfel se randează brut (garda .py nu vede șabloanele .format).
    from core.pdf_util import bani
    MONEDA_CAMP = {"gasit", "asteptat", "baza", "diferenta", "diferenta_solduri", "debit", "credit", "sold"}
    afis = {k: (bani(v) if k in MONEDA_CAMP and v is not None else v) for k, v in campuri.items()}
    try:
        mesaj = sablon.format(**afis)
    except KeyError as e:
        raise ValueError(f"lipsește câmpul {e} pentru mesajul codului {cod!r}")
    return {"ok": False, "cod": cod, "nivel": nivel,
            "mesaj": mesaj, "temei": temei, **campuri}


def ok():
    """Rezultat pozitiv (fără problemă)."""
    return {"ok": True}


# ============================================================
#  COTE / PLAFOANE CU VALABILITATE — codul știe nu doar CÂT, ci DIN CÂND
# ============================================================
# fiecare valoare: (valabil_din, valoare, temei)
COTE = {
    "tva_standard": [
        (date(2025, 8, 1), Decimal("0.21"), "Legea 141/2025"),
        (date(2017, 1, 1), Decimal("0.19"), "Legea 227/2015"),
    ],
    "plafon_mijloc_fix": [
        (date(2026, 1, 1), Decimal("5000"), "OUG 8/2026"),
        (date(2015, 1, 1), Decimal("2500"), "Legea 227/2015"),
    ],
    "plafon_sold_casa": [
        (date(2015, 5, 9), Decimal("50000"), "Legea 70/2015"),
    ],
    "plafon_avans_decontare": [
        (date(2023, 12, 15), Decimal("5000"), "OUG 115/2023"),
    ],
    # — salarizare 2026 —
    "cas": [
        (date(2018, 1, 1), Decimal("0.25"), "Cod fiscal art. 138"),
    ],
    "cass": [
        (date(2018, 1, 1), Decimal("0.10"), "Cod fiscal art. 156"),
    ],
    "impozit_venit": [
        (date(2018, 1, 1), Decimal("0.10"), "Cod fiscal art. 78"),
    ],
    "cam": [
        (date(2018, 1, 1), Decimal("0.0225"), "Cod fiscal art. 220^1"),
    ],
    "salariu_minim": [
        (date(2026, 7, 1), Decimal("4325"), "HG 146/2026"),
        (date(2026, 1, 1), Decimal("4050"), "HG 1510/2024"),
        (date(2025, 1, 1), Decimal("3700"), "HG 1006/2024"),
    ],
    "facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("200"), "OUG 89/2025 art.III + Ordin 605/2026"),
        (date(2025, 1, 1), Decimal("300"), "OUG 115/2023"),
    ],
    "plafon_facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("4600"), "OUG 89/2025 art.III lit.b (venit brut total, S2 2026)"),
        (date(2026, 1, 1), Decimal("4300"), "OUG 89/2025 art.III lit.b (venit brut total, S1 2026)"),
    ],
    # [F133] valoarea maxima legala a unui tichet de masa / zi lucrata. Legea 201/2025
    # (MO 1106/28.11.2025): 45 lei pt S1 2026 + iul-sep 2026 (reindexare dupa octombrie).
    # Tichetele de masa: CASS 10% + impozit 10% (Legea 296/2023), fara CAS/CAM.
    "tichet_masa_plafon": [
        (date(2026, 1, 1), Decimal("45"), "Legea 201/2025 (MO 1106/2025)"),
    ],
}


def cota(nume, la_data=None):
    """
    Întoarce (valoare, temei) valabilă la data dată (implicit azi).
    Permite semnalarea greșelilor de PERIOADĂ, nu doar de moment.
    """
    if nume not in COTE:
        raise ValueError(f"cotă necunoscută: {nume!r}")
    la_data = la_data or date.today()
    for din, valoare, temei in sorted(COTE[nume], key=lambda r: r[0], reverse=True):
        if la_data >= din:
            return valoare, temei
    raise ValueError(f"nicio valoare pentru {nume!r} la data {la_data}")


# ============================================================
#  PRIMITIVĂ DE POSTARE — agregare note pe conturi (rulaje + sold)
#  Fundație partajată: o folosesc și balanța (verificare) și închiderea (motor).
# ============================================================
def agrega_conturi(note, solduri_initiale=None):
    """
    Din lista de note {debit, credit, suma} construiește {cont: {debit, credit, sold}}.
    sold = sold_inițial + rulaj_debitor - rulaj_creditor.
    """
    rd = defaultdict(Decimal)
    rc = defaultdict(Decimal)
    for n in note:
        s = _dec(n["suma"])
        rd[n["debit"]] += s
        rc[n["credit"]] += s
    si = {k: _dec(v) for k, v in (solduri_initiale or {}).items()}
    conturi = set(rd) | set(rc) | set(si)
    out = {}
    for ct in sorted(conturi):
        sold = si.get(ct, Decimal(0)) + rd[ct] - rc[ct]
        out[ct] = {"debit": _q(rd[ct]), "credit": _q(rc[ct]), "sold": _q(sold)}
    return out
