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
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

VERSIUNE_COMMON = "2026.1"


@dataclass(frozen=True)
class Perioada:
    """Obiect valoare pentru perioada unei declaratii (contract uniform A1, 31.07.2026).

    Inlocuieste params divergenti (an/trim/luna). Fiecare declaratie citeste ce-i trebuie:
    lunare -> luna; trimestriale (d100) -> trim; anuale (d101/d205) -> nici luna nici trim.
    pull() foloseste interval() pentru fereastra de date [inceput, sfarsit)."""
    an: int
    luna: int | None = None
    trim: int | None = None

    def interval(self):
        """(inceput, sfarsit) - fereastra semi-deschisa [inceput, sfarsit) pentru pull."""
        if self.luna is not None:
            inc = date(self.an, self.luna, 1)
            sf = date(self.an + 1, 1, 1) if self.luna == 12 else date(self.an, self.luna + 1, 1)
        elif self.trim is not None:
            m0 = (self.trim - 1) * 3 + 1
            inc = date(self.an, m0, 1)
            sf = date(self.an + 1, 1, 1) if self.trim == 4 else date(self.an, m0 + 3, 1)
        else:
            inc, sf = date(self.an, 1, 1), date(self.an + 1, 1, 1)
        return inc, sf


def cheie_manual(manual, *permise):
    """Valideaza cheile unui dict `manual` contra listei PERMISE si intoarce dict-ul (sau {}).

    O cheie NECUNOSCUTA ridica eroare - nu se ignora tacut. Un typo ({"kota":"1"} in loc de
    {"cota":"1"}) altfel s-ar scurge in implicit si ar produce o cifra plauzibila si gresita -
    aceeasi clasa cu "or 21" / "NULL = absenta". Un dict deschis e groapa pentru greseli de tastare."""
    m = manual or {}
    necunoscute = [k for k in m if k not in permise]
    if necunoscute:
        raise ValueError("chei 'manual' necunoscute: %s (permise: %s)" % (
            sorted(necunoscute), sorted(permise)))
    return m


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


def stare_din_nivel(nivel):
    """Mapare UNICA nivel-motor -> stare de verdict. Randarea NU-si mai alege culoarea: deriva din
    nivelul DECLARAT de motor. BLOCANT -> rosu, AVERTISMENT -> galben, absent/necunoscut -> gri
    (nu inventa severitate la randare; lipsa nivelului la un motor = decizie de fond, nu default de
    culoare). NB: galbenul din pastila-firma (semafor de lista) e ALTA axa - nu se imprumuta cu asta.
    Vezi DECIZII 23.07 (doua axe: severitate constatare vs escaladare pastila)."""
    return {BLOCANT: "rosu", AVERTISMENT: "galben"}.get(nivel, "gri")


_RANG_STARE = {"verde": 1, "galben": 2, "rosu": 3}  # gri (necunoscut) = 0: NU escaladeaza pastila


def pastila_firma(base, constatari):
    """Pastila-firma (semafor de lista) = ESCALADARE: severitatea MAXIMA intre starea de baza (declaratii)
    si constatarile firmei. NU poate DEPASI max(constatari) - supra-escaladarea erodeaza increderea in
    semafor: un rosu pe lista care 'minte' (blocant afara, doar avertisment inauntru) invata contabilul ca
    rosul minte, si va ignora si rosurile reale. Un SINGUR loc, nu escaladari imprastiate cu literal per
    verificator. gri (necunoscut, 'nu pot verifica') NU escaladeaza - nu face firma necompletata; base 'gri'
    se pastreaza daca nimic confirmat nu escaladeaza. constatari = [{'stare': ...}, ...]. Vezi DECIZII 23.07."""
    rang = max([_RANG_STARE.get(base, 0)] + [_RANG_STARE.get((c or {}).get("stare"), 0) for c in constatari])
    return base if rang == 0 else {1: "verde", 2: "galben", 3: "rosu"}[rang]


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


def cota_ceruta(corp):
    """Cota TVA dintr-un corp de cerere API, OBLIGATORIE — regula bazei nule.

    Absenta (cheie lipsa / None) = intrare INCOMPLETA -> ValueError; NU se ghiceste o cota
    implicita, nici macar cota standard (un default cu common.cota() ar fi tot o valoare
    inventata, doar actualizata). Apelantul (endpoint) prinde ValueError -> HTTP 422.

    0 (scutit / neplatitor TVA) e VALOARE VALIDA, nu absenta: se distinge None de 0 si se
    intoarce 0 ca atare.
    """
    c = corp.get("cota")
    if c is None:
        raise ValueError("cotă TVA obligatorie: operațiunea trebuie să declare explicit cota "
                         "(o operațiune fără cotă e intrare incompletă, nu cotă standard)")
    return c


class Temei(str):
    """Temei fiscal STRUCTURAT si citabil mecanic (CLAUDE.md 3.1).

    Subclasa de str: se comporta ca string-ul de citare canonic (afisare, JSON, `in`, concatenare),
    dar poarta campurile structurate - tip/nr/an/art/alin/lit/data_in/data_out/url + verificat_la/de_cine.
    Roluri:
      - GREP la o schimbare de lege: gasesti TOATE locurile care citeaza un act.
      - data_out NU se scrie de mana - se DERIVA din succesor (_deriva_data_out): predecesorul primeste
        data_out = ziua dinaintea lui data_in a succesorului; valoarea CURENTA are data_out None (in
        vigoare). O lege spune de CAND intra, nu pana cand (Modelul de temei 01.08, pct.1).
      - verificat_la/de_cine: cand si de cine a fost confirmata valoarea la sursa. Semnalul de deriva e
        VECHIMEA CONFIRMARII (raport intern cote_neconfirmate), NU o expirare inventata (pct.2).
    """
    NIVELE_SURSA = ("MO", "REDARE", "INTERPRETARE_OFICIALA", "PRACTICA")

    def __new__(cls, tip=None, nr=None, an=None, art=None, alin=None, lit=None,
                data_in=None, data_out=None, url=None, verificat_la=None, de_cine=None,
                nivel_sursa=None, text_citat=None, lant_acte=None, text=None):
        s = text if text is not None else _citare_temei(tip, nr, an, art, alin, lit)
        o = super().__new__(cls, s)
        o.tip, o.nr, o.an = tip, nr, an
        o.art, o.alin, o.lit = art, alin, lit
        o.data_in = _ca_data(data_in)
        o.data_out = _ca_data(data_out)   # de regula None; DERIVAT din succesor (_deriva_data_out)
        o.url = url
        o.verificat_la = _ca_data(verificat_la)
        o.de_cine = de_cine
        # nivel_sursa: MO (autoritativ) / REDARE (secundar) / INTERPRETARE_OFICIALA (pliant/ghid) /
        # PRACTICA. text_citat = fraza verbatim (proba verificarii; obligatorie doar la MO).
        # lant_acte = actul modificator/abrogat (ex: HG 146/2026 abroga HG 1506/2024).
        o.nivel_sursa = nivel_sursa
        o.text_citat = text_citat
        o.lant_acte = lant_acte
        return o


def _citare_temei(tip, nr, an, art, alin, lit):
    """Formatul canonic §3.1: <TIP> <nr>/<an> [art.<art>] [alin.(<alin>)] [lit.<lit>].
    CF/CPF sunt coduri (fara nr/an) -> se trece direct la art."""
    p = []
    if tip:
        p.append(str(tip))
    if nr and an:
        p.append("%s/%s" % (nr, an))
    if art:
        p.append("art.%s" % art)
    if alin:
        p.append("alin.(%s)" % alin)
    if lit:
        p.append("lit.%s" % lit)
    return " ".join(p)


def _ca_data(x):
    if x is None or isinstance(x, date):
        return x
    return date.fromisoformat(str(x))


# ============================================================
#  COTE / PLAFOANE CU VALABILITATE — codul știe nu doar CÂT, ci DIN CÂND
# ============================================================
# fiecare valoare: (valabil_din, valoare, temei)
COTE = {
    # data_out NU se scrie aici - se DERIVA din succesor (_deriva_data_out): valoarea CURENTA (cea mai
    # recenta) ramane in vigoare (data_out None), predecesorul primeste ziua dinaintea succesorului.
    # verificat_la/de_cine = cand/de cine confirmata la sursa (semnal de deriva = vechimea confirmarii).
    "tva_standard": [
        (date(2025, 8, 1), Decimal("0.21"), Temei("Legea", 141, 2025, art="291", alin="1", data_in="2025-08-01", verificat_la="2026-07-31", de_cine="Code/Costin", lant_acte="Legea 141/2025 modifica art.291 CF; cota 19% (Legea 227/2015) abrogata la 31.07.2025", nivel_sursa="REDARE")),
        (date(2017, 1, 1), Decimal("0.19"), Temei("Legea", 227, 2015, data_in="2017-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "tva_redusa": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="2", data_in="2025-08-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    # Cotele reduse ISTORICE 9% si 5%, coexistente pana la 31.07.2025, comasate in 11% de Legea 141/2025
    # (decizia lui Costin 03.08: doua chei separate, fiecare cu temeiul ei). Intrarea de la 01.08.2025 (0.11)
    # e COMASAREA: fara ea, cota() ar intoarce 9/5 ca "in vigoare azi" (data_out None pe ultima intrare) - fals.
    # TEMEI operatiuni: verificat (art.291 alin.2 = 9%, alin.3 = 5%). SFARSIT: verificat (Legea 141/2025 pct.42/43,
    # efect 01.08.2025). DATA DE INCEPUT: NEDOCUMENTATA in codul fiscal consolidat (nota istorica de introducere nu
    # e pastrata); ancorata la 2017-01-01 = inceputul erei standard 19% (in toata acea era reducerile erau 9%/5%).
    # INTERPRETARE CU TEMEI (§3): de reconfirmat la MO pentru perioade < 2017; pana atunci cota() refuza (fail-loud).
    "tva_redusa_9": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="2", data_in="2025-08-01", verificat_la="2026-08-03", de_cine="Code/Costin", nivel_sursa="REDARE", lant_acte="Legea 141/2025 pct.42 comaseaza cota redusa de 9% (CF art.291 alin.2) in 11% de la 01.08.2025")),
        (date(2017, 1, 1), Decimal("0.09"), Temei("Legea", 227, 2015, art="291", alin="2", data_in="2017-01-01", verificat_la="2026-08-03", de_cine="Code/Costin", nivel_sursa="REDARE", text_citat="cota redusa de 9% pt operatiunile CF art.291 alin.(2) lit.a-n (medicamente, alimente, apa/canalizare, irigatii, ingrasaminte/pesticide, carti/manuale/ziare, acces cultural, lemn de foc, energie termica, locuinte sociale, cazare, restaurant/catering)", lant_acte="data de INCEPUT a cotei de 9% NU e in codul fiscal consolidat; ancora=era standard 19% (2017-01-01); de reconfirmat la MO pt perioade anterioare")),
    ],
    "tva_redusa_5": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="3", data_in="2025-08-01", verificat_la="2026-08-03", de_cine="Code/Costin", nivel_sursa="REDARE", lant_acte="Legea 141/2025 pct.43 abroga cota redusa de 5% (CF art.291 alin.3); operatiunile trec la 11% de la 01.08.2025")),
        (date(2017, 1, 1), Decimal("0.05"), Temei("Legea", 227, 2015, art="291", alin="3", data_in="2017-01-01", verificat_la="2026-08-03", de_cine="Code/Costin", nivel_sursa="REDARE", text_citat="cota redusa de 5% CF art.291 alin.(3) (locuinte sociale sub 600.000 lei lit.c pct.3, carti, acces evenimente culturale/sportive)", lant_acte="textul verbatim al fostului alin.(3) si data de INCEPUT NU sunt in codul consolidat (apare doar 'Abrogat'); ancora=2017-01-01; de reconfirmat la MO")),
    ],
    # impozit pe dividende / castig din lichidare (regim dividende). 16% de la 01.01.2026 (Legea 141/2025).
    # NEVERIFICAT LA SURSA pentru pre-2026: codul folosea 10 pentru orice data pre-2026 (petic "else 10");
    # istoricul real poate diferi (posibil 8% 2023-2025). data_in 10% = 2024-01-01, REDARE, de reconfirmat la MO.
    "impozit_dividend": [
        (date(2026, 1, 1), Decimal("0.16"), Temei("Legea", 141, 2025, data_in="2026-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE", lant_acte="Legea 141/2025 majoreaza impozitul pe dividende de la 10% la 16% de la 01.01.2026")),
        (date(2024, 1, 1), Decimal("0.10"), Temei("CF", art="97", data_in="2024-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    # plafon TVA la incasare (fost petic 3-tier plafon_la). OUG 8/2026: 5M de la 03.2026, 5.5M de la 2027.
    # 4.5M anterior - act de reconfirmat (REDARE), data_in aproximata (pre-2026 raporteaza gol daca ceri <2023).
    "plafon_tva_incasare": [
        (date(2027, 1, 1), Decimal("5500000"), Temei("OUG", 8, 2026, data_in="2027-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
        (date(2026, 3, 1), Decimal("5000000"), Temei("OUG", 8, 2026, data_in="2026-03-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
        (date(2023, 1, 1), Decimal("4500000"), Temei(text="plafon TVA la incasare pre-OUG 8/2026 (act de reconfirmat)", data_in="2023-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "plafon_mijloc_fix": [
        (date(2026, 1, 1), Decimal("5000"), Temei("OUG", 8, 2026, data_in="2026-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
        (date(2015, 1, 1), Decimal("2500"), Temei("Legea", 227, 2015, data_in="2015-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "plafon_sold_casa": [
        (date(2015, 5, 9), Decimal("50000"), Temei("Legea", 70, 2015, data_in="2015-05-09", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "plafon_avans_decontare": [
        (date(2023, 12, 15), Decimal("5000"), Temei("OUG", 115, 2023, data_in="2023-12-15", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    # impozit micro (1% standard) / profit (16%) - rata DEFAULT (contabilul o poate da explicit prin manual).
    # Mutate din literalele hardcodate din d100 (dependenta ascunsa V2) -> vizibile in graf.
    "impozit_micro": [
        (date(2023, 1, 1), Decimal("0.01"), Temei("CF", art="51", alin="1", data_in="2023-01-01", verificat_la="2026-08-02", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "impozit_profit": [
        (date(2018, 1, 1), Decimal("0.16"), Temei("CF", art="17", data_in="2018-01-01", verificat_la="2026-08-02", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "cas": [
        (date(2018, 1, 1), Decimal("0.25"), Temei("CF", art="138", data_in="2018-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "cass": [
        (date(2018, 1, 1), Decimal("0.10"), Temei("CF", art="156", data_in="2018-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "impozit_venit": [
        (date(2018, 1, 1), Decimal("0.10"), Temei("CF", art="78", data_in="2018-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "cam": [
        (date(2018, 1, 1), Decimal("0.0225"), Temei("CF", art="220^1", data_in="2018-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "salariu_minim": [
        (date(2026, 7, 1), Decimal("4325"), Temei("HG", 146, 2026, data_in="2026-07-01", url="https://legislatie.just.ro/Public/DetaliiDocumentAfis/308231", verificat_la="2026-07-31", de_cine="Code/Costin", lant_acte="HG 146/2026 art.2 abroga HG 1506/2024 de la 01.07.2026", nivel_sursa="REDARE")),
        (date(2025, 1, 1), Decimal("4050"), Temei("HG", 1506, 2024, data_in="2025-01-01", url="https://legislatie.just.ro/Public/DetaliiDocument/291450", verificat_la="2026-07-31", de_cine="Code/Costin", lant_acte="HG 1506/2024 abroga HG 598/2024 (=3700)", nivel_sursa="REDARE")),
    ],
    "facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("200"), Temei("OUG", 89, 2025, art="III", data_in="2026-07-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
        (date(2025, 1, 1), Decimal("300"), Temei("OUG", 115, 2023, data_in="2025-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "plafon_facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("4600"), Temei("OUG", 89, 2025, art="III", lit="b", data_in="2026-07-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
        (date(2026, 1, 1), Decimal("4300"), Temei("OUG", 89, 2025, art="III", lit="b", data_in="2026-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "tichet_masa_plafon": [
        (date(2026, 1, 1), Decimal("45"), Temei("Legea", 201, 2025, data_in="2026-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
}


# Valori care se ACTUALIZEAZA PERIODIC prin act normativ nou (HG, OUG, lege).
# Pentru ele, lipsa unei valori pentru anul urmator NU inseamna ca cea veche ramane -
# inseamna ca nimeni n-a actualizat registrul. Diferenta conteaza: prima interpretare
# produce declaratii gresite IN TACERE.
#
# 29.07.2026: cota() intorcea tacit ultima valoare cunoscuta pentru orice data viitoare.
# In ianuarie 2027, D112 ar fi folosit salariul minim din iulie 2026 fara niciun semnal.
# {nume: luni_de_valabilitate_de_la_ultima_intrare}
from datetime import timedelta as _timedelta


def _deriva_data_out(cote=None):
    """data_out se DERIVA din succesor (Modelul de temei 01.08, pct.1): predecesorul (dupa data_in)
    primeste data_out = ziua dinaintea lui data_in a succesorului; valoarea CURENTA ramane None (in
    vigoare). Rulat o data la incarcarea modulului - data_out nu se scrie de mana, e fapt derivat."""
    _c = cote if cote is not None else COTE
    for _nume, _intrari in _c.items():
        _sortate = sorted(_intrari, key=lambda r: r[0])   # crescator dupa data_in
        for _idx in range(len(_sortate) - 1):
            _succ_din = _sortate[_idx + 1][0]
            _sortate[_idx][2].data_out = _succ_din - _timedelta(days=1)
        _sortate[-1][2].data_out = None   # valoarea curenta e in vigoare


_deriva_data_out()


# Cea mai devreme perioada pentru care sistemul are date de calcul salarial: salariu_minim si
# facilitate_salariu_minim au fost populate incepand cu 2025-01-01 (pentru adeverinte/rectificative 2025).
# O cota de REGULA cu data_in DUPA aceasta podea (ex. plafon_facilitate/tichet incep 2026-01-01) rupe un
# calcul pentru o perioada [podea, data_in) in care functia are ALTFEL date -> blocaj MOTIVAT, nu exceptie bruta.
DATA_START_SISTEM = date(2025, 1, 1)


class PerioadaIndisponibila(ValueError):
    """Blocaj MOTIVAT (nu exceptie bruta): o cota ceruta de un calcul nu e definita pentru perioada ceruta
    (data ceruta e inainte de prima valoare cunoscuta a cotei). NU e defect de sistem - e LIMITA DECLARATA:
    valoarea nu a fost verificata la sursa pentru perioade anterioare (o lege spune de CAND intra, nu se
    inventeaza retroactiv - Modelul de temei 01.08). Mesajul poarta cele 4 elemente (ce s-a oprit / de ce /
    ce se poate face / cine decide) + tag-ul PERIOADA_BLOCATA, ca handler-ul global (main.py) sa-l arate
    utilizatorului ca mesaj (423), nu ca traceback (500). Subclasa de ValueError -> `except ValueError`
    existent ramane valabil."""
    def __init__(self, nume, la_data, prima_data):
        self.nume = nume
        self.la_data = _ca_data(la_data)
        self.prima_data = _ca_data(prima_data)
        det = ("%s nu poate fi calculata: valoarea '%s' nu e definita inainte de %s (nu a fost verificata "
               "la sursa pentru perioade anterioare - nu se inventeaza retroactiv). Calculul e disponibil de "
               "la %s; pentru perioade anterioare valoarea se completeaza in COTE la sursa (decizie de "
               "dezvoltator)." % (self.la_data.isoformat(), nume, self.prima_data.isoformat(),
                                  self.prima_data.isoformat()))
        super().__init__("PERIOADA_BLOCATA: " + det)


# ============================================================
#  TICHETE CULTURALE — plafoane semestriale indexate (Legea 165/2018 art.22, indexat prin ordine MF/MC).
#  Temeiuri VERDE: anaf_surse/RAPORT_verificare_temeiuri.md (verdict 15 valoare nominala; verdict 16 ferestre).
#  Ferestrele CONFIRMATE la sursa primara; fereastra oct.2025-mar.2026 (S2 2025) = GRI (ordinul de mijloc
#  1.574/3.246/2025 e stub pe just.ro) -> BLOCAJ MOTIVAT, NU 240/470 tacit (GARD OBLIGATORIU).
# ============================================================
class PlafonCulturalIndisponibil(ValueError):
    """Blocaj MOTIVAT: plafonul tichetelor culturale nu e confirmat la sursa primara pentru luna ceruta
    (fereastra GRI sau semestru fara ordin de indexare descarcat). Mesaj cu 4 elemente + tag
    PERIOADA_BLOCATA (handler global main.py -> 423, nu traceback 500). Subclasa de ValueError."""
    def __init__(self, la_data, motiv):
        self.la_data = _ca_data(la_data)
        super().__init__("PERIOADA_BLOCATA: Tichete culturale - plafon indisponibil pentru %s: %s"
                         % (self.la_data.isoformat(), motiv))


# (start, end_inclusiv, lunar, eveniment, sursa) - valori CONFIRMATE la sursa primara (anaf_surse/).
_FERESTRE_CULTURAL = [
    (date(2025, 4, 1), date(2025, 9, 30), Decimal("220"), Decimal("450"),
     "Ordin MF/MC 361/2.680/2025, MO 244/20.03.2025 (anaf_surse/ordin_361_2680_2025.html)"),
    (date(2026, 4, 1), date(2026, 9, 30), Decimal("250"), Decimal("490"),
     "Ordin MF/MC 369/2.624/2026, MO 258/01.04.2026 (anaf_surse/ordin_369_2624_2026.html)"),
]
# Fereastra GRI (verdict 16): 2025-10-01 .. 2026-03-31 (semestrul II 2025). Ordinul 1.574/3.246/2025 e stub
# pe just.ro; valoarea 240/470 doar din surse secundare, NEconfirmata la MO -> se BLOCHEAZA, nu se aplica tacit.
_CULTURAL_GRI = (date(2025, 10, 1), date(2026, 3, 31))


def plafon_cultural(la_data, ocazional=False):
    """Plafonul maxim al unui tichet cultural pentru luna la_data: (Decimal, sursa).
    ocazional=False -> plafon LUNAR ; True -> plafon pe EVENIMENT. Ridica PlafonCulturalIndisponibil
    (blocaj motivat) pentru ferestre neconfirmate la sursa (GRI sau semestru fara ordin descarcat)."""
    d = _ca_data(la_data)
    for start, end, lunar, eveniment, sursa in _FERESTRE_CULTURAL:
        if start <= d <= end:
            return (eveniment if ocazional else lunar), sursa
    if _CULTURAL_GRI[0] <= d <= _CULTURAL_GRI[1]:
        raise PlafonCulturalIndisponibil(d,
            "fereastra oct.2025-mar.2026 (semestrul II 2025) e GRI - ordinul MF/MC 1.574/3.246/2025 e stub pe "
            "just.ro, valoarea (240/470) doar din surse secundare, NEconfirmata la MO. Ce se poate face: obtine "
            "textul operativ al ordinului la MO si adauga fereastra in _FERESTRE_CULTURAL. Cine decide: Costin.")
    raise PlafonCulturalIndisponibil(d,
        "niciun ordin de indexare confirmat la sursa pentru semestrul acestei luni. Ce se poate face: descarca "
        "ordinul MF/MC de indexare a tichetelor culturale pentru semestrul respectiv la MO si adauga fereastra. "
        "Cine decide: Costin.")


# ============================================================
#  TICHETE DE CRESA — Legea 165/2018 art.19. Baza legala: 450 lei/luna/COPIL (art.19(1)); valoare nominala
#  10/multiplu/max 100 (art.19(2)). Tratament fiscal = ca tichetul cultural (impozit 10%, FARA CAS/CASS/CAM:
#  cresa e in CF art.142 lit.r + exceptata din CASS art.157(2) care lasa doar masa+vacanta). Valoarea se
#  INDEXEAZA semestrial prin ordine MF/MMSS - NEconfirmate la sursa primara (verdict 17 GRI: ordinul 368/179/
#  2026 = 740 lei doar din surse secundare, mmuncii HTTP 503) -> se aplica BAZA confirmata 450/copil,
#  grant-urile care depind de indexarea neconfirmata (>450/copil) sunt blocate (GARD).
# ============================================================
def plafon_cresa(la_data, nr_copii=1):
    """Plafonul maxim lunar al tichetelor de cresa: (Decimal, sursa). = 450 * nr_copii (L165 art.19(1),
    baza confirmata). Indexarea (ex. 740 din 2026) e GRI (verdict 17) -> NEaplicata; cap conservator la baza."""
    n = int(nr_copii) if nr_copii else 1
    if n < 1:
        n = 1
    return Decimal("450") * n, "Legea 165/2018 art.19(1) - baza 450/luna/copil (indexare GRI verdict 17, neaplicata)"


def cota(nume, la_data=None, strict=True):
    """Intoarce (valoare, temei) valabila la data ceruta (implicit azi).

    RIDICA (strict) DOAR cand valoarea selectata are un data_out REAL (derivat din succesor) si data
    ceruta e dupa el - adica un GOL intre valori sau o valoare istorica ceruta in afara valabilitatii.
    Valoarea CURENTA are data_out None -> NU expira niciodata prin cota() (o lege spune de cand, nu pana
    cand - Modelul de temei 01.08). Semnalul ca o valoare curenta n-a mai fost confirmata de mult e
    VECHIMEA CONFIRMARII (cote_neconfirmate), raport INTERN, nu blocaj la calcul. strict=False intoarce
    valoarea oricum (rapoarte istorice)."""
    if nume not in COTE:
        raise ValueError(f"cotă necunoscută: {nume!r}")
    la_data = la_data or date.today()
    intrari = sorted(COTE[nume], key=lambda r: r[0], reverse=True)
    for din, valoare, temei in intrari:
        if la_data >= din:
            _out = getattr(temei, "data_out", None)
            if strict and _out is not None and la_data > _out:
                raise ValueError(
                    f"{nume}: valoarea din {din.isoformat()} ({temei}) a fost valabila pana la "
                    f"{_out.isoformat()} (succesorul a intrat in vigoare dupa). S-a cerut pentru "
                    f"{la_data.isoformat()} - gol in registru. Adauga valoarea valabila in COTE."
                )
            return valoare, temei
    # la_data e inainte de PRIMA valoare cunoscuta (intrari sortate descrescator -> ultima = cea mai veche).
    # NU exceptie bruta: blocaj MOTIVAT (valoarea nu e verificata la sursa pentru perioade anterioare).
    raise PerioadaIndisponibila(nume, la_data, intrari[-1][0])


def alege_varianta(variante, la_data=None):
    """Alege varianta de FORMULA valabila la la_data - tiparul cota() dar pe COD. variante = [(data_in,
    functie, temei), ...]; intoarce (functie, temei) pentru cea mai recenta cu data_in <= la_data.
    Cotele sunt period-aware prin cota(); formulele (scara, prorata, plafonare, split) devin period-aware
    prin acest dispecer - o schimbare de regula se adauga ca varianta datata, NU ca 'if data' (trecutul
    ramane calculabil: adeverinte/rectificative pe o luna trecuta folosesc regula de ATUNCI). Ridica pe gol."""
    la_data = la_data or date.today()
    for din, fn, temei in sorted(variante, key=lambda r: _ca_data(r[0]), reverse=True):
        if la_data >= _ca_data(din):
            return fn, temei
    raise ValueError("nicio varianta de formula valabila la %s" % la_data)


def _adauga_luni(d, luni):
    """Data + N luni, cu ultima zi a lunii daca ziua nu exista (31 ian + 1 luna = 28/29 feb)."""
    an = d.year + (d.month - 1 + luni) // 12
    luna = (d.month - 1 + luni) % 12 + 1
    zi = d.day
    while zi > 1:
        try:
            return date(an, luna, zi)
        except ValueError:
            zi -= 1
    return date(an, luna, 1)


def cote_neconfirmate(luni=6, la_data=None):
    """RAPORT INTERN (Modelul de temei 01.08, pct.2): valorile CURENTE care n-au mai fost confirmate la
    sursa de peste `luni` luni (verificat_la vechi sau lipsa). NU e in interfata contabilului - e alerta
    catre dezvoltator. Inlocuieste expirarea inventata (EXPIRA_DUPA_LUNI, scoasa): legea n-a spus ca
    valoarea expira, dar confirmarea imbatraneste - dezvoltatorul verifica periodic MO. Fereastra intre
    publicarea in MO si actualizarea in aplicatie NU se poate inchide automat (nu exista API legislativ RO)."""
    la_data = la_data or date.today()
    prag = _adauga_luni(la_data, -luni)
    rez = []
    for nume in COTE:
        din, valoare, temei = sorted(COTE[nume], key=lambda r: r[0], reverse=True)[0]
        vl = getattr(temei, "verificat_la", None)
        if vl is None or vl <= prag:
            rez.append({"nume": nume, "valoare": valoare, "temei": temei,
                        "din": din, "verificat_la": vl,
                        "luni_de_la_confirmare": None if vl is None else
                        (la_data.year - vl.year) * 12 + (la_data.month - vl.month)})
    return sorted(rez, key=lambda r: (r["verificat_la"] or date.min))


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


def cere_coloane(rand, chei, unde=""):
    """Verifica CA EXISTA cheile intr-un rand citit din DB. Cheie lipsa -> ValueError.

    DE CE (27.07.2026): `SELECT *` NU crapa cand o coloana dispare din schema - query-ul
    reuseste si randul iese pur si simplu fara cheia aceea. Apoi `s.get("x")` da None, iar
    None e o absenta LEGITIMA pentru un camp optional. Rezultatul: valoarea devine tacit 0.

    Dovedit pe D112: cu `salariu_brut` redenumita, generarea a scos o declaratie de 1333
    caractere cu suma 0, in loc de 1890 cu 5000. Depunere la ANAF cu salarii zero, fara
    niciun semnal. Gaura apare exact intre doua comportamente CORECTE: SELECT * tolerant
    si absenta tratata ca zero.

    CE VERIFICA: PREZENTA cheii, nu valoarea. `salariu_brut = 0` e legitim (salariat in
    concediu medical toata luna); `salariu_brut` INEXISTENT nu e.
    """
    lipsa = [c for c in chei if c not in rand]
    if lipsa:
        raise ValueError(
            "coloane lipsa%s: %s. Randul citit din baza nu are aceste campuri - schema "
            "nu se potriveste cu ce asteapta codul (SELECT * nu semnaleaza asta singur)."
            % ((" in %s" % unde) if unde else "", ", ".join(lipsa)))
    return rand


def cere_coloane_cursor(cur, chei, unde=""):
    """Ca `cere_coloane`, dar verifica pe CURSOR - deci prinde si tabela GOALA.

    DE CE (27.07.2026): `cere_coloane` verifica randurile CITITE. Pe zero randuri n-are ce
    verifica si trece - o coloana disparuta pe o firma fara salariati nu se semnala. Limita
    reala, consemnata cand a fost gasita.

    `cur.description` descrie ce a intors query-ul indiferent cate randuri sunt: pe tabela
    goala da tot lista completa de coloane (dovedit pe tenant_003.salariati: 0 randuri, 20 de
    coloane). Zero cost - nu e query in plus, e metadata pe care driverul o are deja.

    Se cheama IMEDIAT dupa `cur.execute`, inainte de fetch.
    """
    col = {d[0] for d in (cur.description or ())}
    if not col:
        raise ValueError("cursorul nu a intors coloane%s - query-ul n-a rulat?"
                         % ((" la %s" % unde) if unde else ""))
    lipsa = [c for c in chei if c not in col]
    if lipsa:
        raise ValueError(
            "coloane lipsa%s: %s. Query-ul a reusit dar schema nu are aceste campuri - "
            "SELECT * nu semnaleaza asta singur, iar valorile ar deveni tacit zero."
            % ((" in %s" % unde) if unde else "", ", ".join(lipsa)))
    return True


# ANAF respinge orice atribut de text peste 75 de caractere ("sir mai lung de 75
# caractere"). 74 = marja fata de limita, tiparul deja folosit in d100/d101/d112/d205/d710.
LIMITA_TEXT_ANAF = 74


def text_anaf(v, limita=LIMITA_TEXT_ANAF):
    """Text pentru un atribut XML de declaratie: curatat si TRUNCHIAT la limita ANAF.

    DE CE (27.07.2026): trunchierea `[:74]` exista deja in 6 din 11 locuri unde se emite
    `declarant_nume` - deci regula era cunoscuta si aplicata pe jumatate. In plus acoperea
    DOAR numele declarantului; campurile care chiar au crapat la validator sunt altele:
    `den` (numele firmei, 115 caractere la o firma reala), `adresa` (97), `den_intocmit`.

    Dovedit pe tenant_001: D300, D301, D390, D394 si D112 emiteau toate atribute peste 75
    de caractere, iar ANAF le respingea cu un mesaj pe care contabilul nu-l poate lega de
    campul din ecran.

    Trunchierea e legitima aici: numele lung e o denumire completa cu titulaturi, iar ANAF
    accepta forma scurta. Nu se pierde nicio informatie fiscala - CUI-ul identifica firma.
    """
    t = " ".join(str(v or "").split())      # normalizeaza spatiile multiple
    return t[:limita]
