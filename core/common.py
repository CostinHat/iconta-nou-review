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


def perioada_tva_tip(prof):
    """Tipul perioadei fiscale TVA (L/T/S/A) din VECTORUL FISCAL al firmei
    (firma_profil.tip_decont). [06.08.2026, conditia Costin] FARA default tacit:
    lipsa/necunoscut -> eroare (NU 'L'). Decontul TVA (D300/D394) urmeaza aceasta perioada."""
    raw = str((prof or {}).get("tip_decont") or "").strip().lower()
    if not raw:
        raise ValueError(
            "LIPSA tip_decont (perioada fiscala TVA) in vectorul firmei - obligatoriu pentru "
            "decontul de TVA (D300/D394). Completeaza lunar/trimestrial in vectorul fiscal.")
    if raw in ("l", "t", "s", "a"):
        return raw.upper()
    if "trim" in raw:
        return "T"
    if "sem" in raw:
        return "S"
    if raw.startswith("an"):
        return "A"
    if raw.startswith("lun") or raw == "l":
        return "L"
    raise ValueError("tip_decont necunoscut in vectorul fiscal: %r" % raw)


def fereastra_tva(perioada, tip):
    """(inceput, sfarsit) semi-deschis [inceput, sfarsit) pentru decontul TVA, functie de
    PERIOADA FISCALA (tip=L/T/S/A). Decupleaza ETICHETA (perioada.luna, pusa in XML: 3/6/9/12
    pentru trimestrial) de FEREASTRA DE DATE (trimestrul intreg). perioada.luna = ancora."""
    an, luna = perioada.an, perioada.luna
    if luna is None:
        raise ValueError("fereastra_tva cere perioada.luna (ancora)")
    if tip == "L":
        sf = date(an + 1, 1, 1) if luna == 12 else date(an, luna + 1, 1)
        return date(an, luna, 1), sf
    if tip == "T":
        q = (luna - 1) // 3 + 1
        m0 = (q - 1) * 3 + 1
        sf = date(an + 1, 1, 1) if q == 4 else date(an, m0 + 3, 1)
        return date(an, m0, 1), sf
    if tip == "S":
        if luna <= 6:
            return date(an, 1, 1), date(an, 7, 1)
        return date(an, 7, 1), date(an + 1, 1, 1)
    if tip == "A":
        return date(an, 1, 1), date(an + 1, 1, 1)
    raise ValueError("tip perioada TVA necunoscut: %r" % tip)


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
        (date(2025, 8, 1), Decimal("0.21"), Temei("Legea", 141, 2025, art="291", alin="1", data_in="2025-08-01", verificat_la="2026-08-07", de_cine="Code/Costin", url="anaf_surse/legea_141_2025_consolidat.html", text_citat="Art.II pct.42 (modifica art.291 alin.1 CF): cota standard TVA 21%", lant_acte="Legea 141/2025 modifica art.291 CF; cota 19% (Legea 227/2015) abrogata la 31.07.2025", nivel_sursa="MO")),
        (date(2017, 1, 1), Decimal("0.19"), Temei("Legea", 227, 2015, data_in="2017-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "tva_redusa": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="2", data_in="2025-08-01", verificat_la="2026-08-07", de_cine="Code/Costin", url="anaf_surse/legea_141_2025_consolidat.html", text_citat="Art.II pct.42 (art.291 alin.2 CF): Cota redusa de 11% se aplica asupra bazei de impozitare", nivel_sursa="MO")),
    ],
    # Cotele reduse ISTORICE 9% si 5%, coexistente pana la 31.07.2025, comasate in 11% de Legea 141/2025
    # (decizia lui Costin 03.08: doua chei separate, fiecare cu temeiul ei). Intrarea de la 01.08.2025 (0.11)
    # e COMASAREA: fara ea, cota() ar intoarce 9/5 ca "in vigoare azi" (data_out None pe ultima intrare) - fals.
    # TEMEI operatiuni: verificat (art.291 alin.2 = 9%, alin.3 = 5%). SFARSIT: verificat (Legea 141/2025 pct.42/43,
    # efect 01.08.2025). DATA DE INCEPUT: NEDOCUMENTATA in codul fiscal consolidat (nota istorica de introducere nu
    # e pastrata); ancorata la 2017-01-01 = inceputul erei standard 19% (in toata acea era reducerile erau 9%/5%).
    # INTERPRETARE CU TEMEI (§3): de reconfirmat la MO pentru perioade < 2017; pana atunci cota() refuza (fail-loud).
    "tva_redusa_9": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="2", data_in="2025-08-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/legea_141_2025_consolidat.html", text_citat="Art.II pct.42 (art.291 alin.2 CF): cota redusa unica de 11% (comaseaza fostele operatiuni de 9%)", lant_acte="Legea 141/2025 pct.42 comaseaza cota redusa de 9% (CF art.291 alin.2) in 11% de la 01.08.2025")),
        (date(2016, 1, 1), Decimal("0.09"), Temei("Legea", 227, 2015, art="291", alin="2", data_in="2016-01-01", verificat_la="2026-08-07", de_cine="Code+cercetare", nivel_sursa="MO", url="anaf_surse/cf_art291_2016_forma_initiala.txt", text_citat="cota redusa de 9% pt operatiunile CF art.291 alin.(2) lit.a-n (medicamente, alimente, apa/canalizare, irigatii, ingrasaminte/pesticide, carti/manuale/ziare, acces cultural, lemn de foc, energie termica, locuinte sociale, cazare, restaurant/catering)", lant_acte="cota 9% in vigoare de la 01.01.2016 (Legea 227/2015, MO 688/2015; verificat 03.08.2026 - anaf_surse/cf_art291_2016_forma_initiala.txt). Comasata in 11% de Legea 141/2025 de la 01.08.2025. Nota: apa/ingrasaminte (g/h) adaugate de Legea 175/2018 din 01.01.2019")),
    ],
    "tva_redusa_5": [
        (date(2025, 8, 1), Decimal("0.11"), Temei("Legea", 141, 2025, art="291", alin="3", data_in="2025-08-01", verificat_la="2026-08-03", de_cine="Code/Costin", nivel_sursa="REDARE", lant_acte="Legea 141/2025 pct.43 abroga cota redusa de 5% (CF art.291 alin.3); operatiunile trec la 11% de la 01.08.2025")),
        (date(2016, 1, 1), Decimal("0.05"), Temei("Legea", 227, 2015, art="291", alin="3", data_in="2016-01-01", verificat_la="2026-08-07", de_cine="Code+cercetare", nivel_sursa="MO", url="anaf_surse/cf_art291_2016_forma_initiala.txt", text_citat="cota redusa de 5% CF art.291 alin.(3) (locuinte sociale sub 600.000 lei lit.c pct.3, carti, acces evenimente culturale/sportive)", lant_acte="cota 5% ca alin.(3) art.291 in vigoare de la 01.01.2016 (Legea 227/2015; verificat 03.08.2026 - anaf_surse/cf_art291_2016_forma_initiala.txt): carti/manuale (a), acces cultural (b), locuinte sociale (c). Locuinte la 5% au continuitate din vechiul cod (OUG 200/2008). Abrogata de Legea 141/2025 de la 01.08.2025")),
    ],
    # impozit pe dividende / castig din lichidare (regim dividende), CF art.97 alin.(7). Cote istorice VERIFICATE
    # la sursa 03.08.2026 (anaf_surse/impozit_dividende_istoric_cote.txt): 5% (2016-2022), 8% (2023-2025, OG 16/2022),
    # 16% (de la 01.01.2026, Legea 141/2025). Se aplica dupa data DISTRIBUIRII. (Fostul petic "10%" era GRESIT -
    # 10% e cota impozitului pe VENIT art.78, nu pe dividende.)
    "impozit_dividend": [
        (date(2026, 1, 1), Decimal("0.16"), Temei("Legea", 141, 2025, art="97", alin="7", data_in="2026-01-01", verificat_la="2026-08-07", de_cine="Code+cercetare", nivel_sursa="MO", url="anaf_surse/legea_141_2025_consolidat.html", text_citat="Art.II pct.1 (art.43 alin.2 CF): impozit pe dividende cota 16% asupra dividendului brut", lant_acte="Legea 141/2025 majoreaza impozitul pe dividende de la 8% la 16%, dividende distribuite de la 01.01.2026")),
        (date(2023, 1, 1), Decimal("0.08"), Temei("OG", 16, 2022, art="97", alin="7", data_in="2023-01-01", verificat_la="2026-08-03", de_cine="Code+cercetare", nivel_sursa="REDARE", lant_acte="OG 16/2022 (MO 716/15.07.2022) majoreaza cota de la 5% la 8%, dividende distribuite de la 01.01.2023; aprobata prin Legea 370/2022")),
        (date(2016, 1, 1), Decimal("0.05"), Temei("Legea", 227, 2015, art="97", alin="7", data_in="2016-01-01", verificat_la="2026-08-03", de_cine="Code+cercetare", nivel_sursa="REDARE", lant_acte="cota 5% pt dividende distribuite de la 01.01.2016 (OUG 50/2015 MO 817/2015 accelereaza data din Legea 227/2015; aprobata prin Legea 358/2015)")),
    ],
    # plafon TVA la incasare (fost petic 3-tier plafon_la). OUG 8/2026: 5M de la 03.2026, 5.5M de la 2027.
    # 4.5M = Legea 296/2020 (majorare 2,25M->4,5M de la 01.01.2021), ramas pana la OUG 8/2026.
    "plafon_tva_incasare": [
        (date(2027, 1, 1), Decimal("5500000"), Temei("OUG", 8, 2026, art="282", alin="3", lit="b", data_in="2027-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_8_2026.html", text_citat="art.282 alin.(3) lit.b) CF: Plafonul pentru aplicarea sistemului TVA la incasare este de 5.500.000 lei, incepand cu data de 1 ianuarie 2027")),
        (date(2026, 3, 1), Decimal("5000000"), Temei("OUG", 8, 2026, art="282", alin="3", lit="a", data_in="2026-03-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_8_2026.html", text_citat="art.282 alin.(3) lit.a) CF: Plafonul pentru aplicarea sistemului TVA la incasare este de 5.000.000 lei, in perioada 1 martie-31 decembrie 2026")),
        (date(2021, 1, 1), Decimal("4500000"), Temei("Legea", 296, 2020, data_in="2021-01-01", verificat_la="2026-08-05", de_cine="Code/Costin", nivel_sursa="REDARE", lant_acte="Legea 296/2020 (MO 1269/21.12.2020) majoreaza plafonul TVA la incasare 2.250.000->4.500.000 de la 01.01.2021; ramas 4,5M pana la OUG 8/2026 (5M de la 01.03.2026). Confirmat secundar - CF consolidat a inlocuit tier-ul la OUG 8/2026")),
    ],
    "plafon_mijloc_fix": [
        (date(2026, 1, 1), Decimal("5000"), Temei("OUG", 8, 2026, art="28", alin="2", lit="b", data_in="2026-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_8_2026.html", text_citat="art.28 alin.(2) lit.b) CF: la data intrarii in patrimoniul contribuabilului are o valoare fiscala egala sau mai mare decat suma de 5.000 lei; aceasta limita se actualizeaza anual cu indicele de inflatie, prin HG")),
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
        (date(2023, 1, 1), Decimal("0.01"), Temei("CF", art="51", alin="1", data_in="2023-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.51 alin.(1): Cota de impozit pe veniturile microintreprinderilor este de 1%", lant_acte="cota micro 1% (CF art.51 alin.1). OUG 89/2025 (MO 1203/24.12.2025) art.I pct.4 pastreaza 1% ca forma UNICA de la 01.01.2026 + pct.5 abroga alin.(1^1)=cota 3%; pe 2026 nu mai exista split 1%/3% si nici pragul 60.000 EUR. Confirmat la sursa 05.08.2026 (validat Costin)")),
    ],
    "impozit_profit": [
        (date(2018, 1, 1), Decimal("0.16"), Temei("CF", art="17", data_in="2018-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.17: Cota de impozit pe profit care se aplica asupra profitului impozabil este de 16%")),
    ],
    "cas": [
        (date(2018, 1, 1), Decimal("0.25"), Temei("CF", art="138", data_in="2018-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.138 lit.a): 25% datorata de persoanele fizice care au calitatea de angajati")),
    ],
    "cass": [
        (date(2018, 1, 1), Decimal("0.10"), Temei("CF", art="156", data_in="2018-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.156: Cota de contributie de asigurari sociale de sanatate este de 10%")),
    ],
    "impozit_venit": [
        (date(2018, 1, 1), Decimal("0.10"), Temei("CF", art="78", data_in="2018-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.64 alin.(1): Cota de impozit este de 10% (aplicata la venituri din salarii, art.78)")),
    ],
    "cam": [
        (date(2018, 1, 1), Decimal("0.0225"), Temei("CF", art="220^1", data_in="2018-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/cod_fiscal_227_2015_consolidat.html", text_citat="art.220^3 alin.(1): Cota contributiei asiguratorii pentru munca este de 2,25%")),
    ],
    "salariu_minim": [
        (date(2026, 7, 1), Decimal("4325"), Temei("HG", 146, 2026, data_in="2026-07-01", url="anaf_surse/hg_146_2026_salariu_minim.html", verificat_la="2026-08-07", de_cine="Code/Costin", text_citat="Articolul 1: Incepand cu data de 1 iulie 2026 ... la suma de 4.325 lei lunar", lant_acte="HG 146/2026 art.2 abroga HG 1506/2024 de la 01.07.2026", nivel_sursa="MO")),
        (date(2025, 1, 1), Decimal("4050"), Temei("HG", 1506, 2024, data_in="2025-01-01", url="anaf_surse/hg_1506_2024_salariu_minim.html", verificat_la="2026-08-07", de_cine="Code/Costin", text_citat="Articolul 1: Incepand cu data de 1 ianuarie 2025 ... la suma de 4.050 lei lunar", lant_acte="HG 1506/2024 abroga HG 598/2024 (=3700)", nivel_sursa="MO")),
    ],
    "facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("200"), Temei("OUG", 89, 2025, art="III", data_in="2026-07-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_89_2025.html", text_citat="art.III alin.(1): pentru suma de 200 lei/luna din veniturile din salarii aferente perioadei 1 iulie-31 decembrie 2026 nu se datoreaza impozit pe venit si contributii sociale obligatorii")),
        (date(2025, 1, 1), Decimal("300"), Temei("OUG", 115, 2023, data_in="2025-01-01", verificat_la="2026-07-31", de_cine="Code/Costin", nivel_sursa="REDARE")),
    ],
    "plafon_facilitate_salariu_minim": [
        (date(2026, 7, 1), Decimal("4600"), Temei("OUG", 89, 2025, art="III", alin="1", lit="b", data_in="2026-07-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_89_2025.html", text_citat="art.III alin.(1) lit.b): venitul brut din salarii (fara tichete masa/vouchere vacanta/indemnizatie hrana) nu depaseste nivelul de 4.600 lei inclusiv in perioada 1 iulie-31 decembrie 2026")),
        (date(2026, 1, 1), Decimal("4300"), Temei("OUG", 89, 2025, art="III", alin="1", lit="b", data_in="2026-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_89_2025.html", text_citat="art.III alin.(1) lit.b): venitul brut din salarii (fara tichete masa/vouchere vacanta/indemnizatie hrana) nu depaseste nivelul de 4.300 lei inclusiv in perioada 1 ianuarie-30 iunie 2026")),
        (date(2025, 1, 1), Decimal("4300"), Temei("OUG", 156, 2024, art="LXVI", data_in="2025-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/oug_156_2024.pdf", text_citat="art.LXVI alin.(1) lit.b: venitul brut (fara tichete masa/vouchere vacanta/indemnizatie hrana) nu depaseste 4.300 lei inclusiv; veniturile aferente lunilor ianuarie-decembrie 2025")),
    ],
    "tichet_masa_plafon": [
        (date(2025, 11, 1), Decimal("45"), Temei("Legea", 201, 2025, art="I", data_in="2025-11-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/legea_201_2025.html", text_citat="art.I pct.1: valoarea nominala a unui tichet de masa nu poate depasi suma de 45 lei; art.II alin.(1): se aplica incepand cu drepturile aferente lunii noiembrie 2025")),
        (date(2025, 4, 1), Decimal("40.18"), Temei("Ordin", "484", 2025, data_in="2025-04-01", data_out="2025-09-30", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/anaf_limite_2025.pdf", text_citat="Ordinul MF 484/2025: tichet masa 40,18 lei, semestrul I 2025 din aprilie + august si septembrie 2025; octombrie 2025 neacoperit -> gol motivat (data_out explicit 30 sep)")),
        (date(2025, 1, 1), Decimal("40.04"), Temei("Ordin", "4679", 2024, data_in="2025-01-01", verificat_la="2026-08-07", de_cine="Code/Costin", nivel_sursa="MO", url="anaf_surse/anaf_limite_2025.pdf", text_citat="Ordinul MF 4.679/2024: tichet masa 40,04 lei, semestrul II 2024 din octombrie + februarie si martie 2025")),
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
            if _sortate[_idx][2].data_out is None:   # RESPECTA data_out EXPLICIT (sfarsit de
                _sortate[_idx][2].data_out = _succ_din - _timedelta(days=1)  # acoperire fara succesor
                # confirmat -> gol motivat); DERIVA doar cand lipseste. Verificat: nicio valoare
                # existenta n-are data_out explicit -> comportament identic pt cele existente.
        if _sortate[-1][2].data_out is None:
            _sortate[-1][2].data_out = None   # valoarea curenta ramane in vigoare


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
    # CONFIRMATA la PRIMAR 04.08.2026 (fosta GRI verdict 16): textul operativ al Ordinului MF/MC 1.574/3.246/2025
    # (anaf_surse/ordin_1574_3246_2025_cultural.pdf, sha256): "Pentru semestrul II al anului 2025 ... maximum 240
    # lei/luna, respectiv maximum 470 lei/eveniment ... se aplica si pentru primele 2 luni ale semestrului I 2026"
    # (feb-mar 2026). Publicat MO nr. 900 din 01.10.2025. Acopera oct.2025 - mar.2026.
    (date(2025, 10, 1), date(2026, 3, 31), Decimal("240"), Decimal("470"),
     "Ordin MF/MC 1.574/3.246/2025, MO 900/01.10.2025 (anaf_surse/ordin_1574_3246_2025_cultural.pdf)"),
    (date(2026, 4, 1), date(2026, 9, 30), Decimal("250"), Decimal("490"),
     "Ordin MF/MC 369/2.624/2026, MO 258/01.04.2026 (anaf_surse/ordin_369_2624_2026.html)"),
]
# Fereastra oct.2025-mar.2026 a fost CONFIRMATA la primar 04.08.2026 (mai sus) - nu mai e GRI. Nicio fereastra GRI
# ramasa; perioadele neacoperite de un ordin descarcat raman blocate prin fallback-ul generic din plafon_cultural.
_CULTURAL_GRI = None


def plafon_cultural(la_data, ocazional=False):
    """Plafonul maxim al unui tichet cultural pentru luna la_data: (Decimal, sursa).
    ocazional=False -> plafon LUNAR ; True -> plafon pe EVENIMENT. Ridica PlafonCulturalIndisponibil
    (blocaj motivat) pentru ferestre neconfirmate la sursa (GRI sau semestru fara ordin descarcat)."""
    d = _ca_data(la_data)
    for start, end, lunar, eveniment, sursa in _FERESTRE_CULTURAL:
        if start <= d <= end:
            return (eveniment if ocazional else lunar), sursa
    if _CULTURAL_GRI is not None and _CULTURAL_GRI[0] <= d <= _CULTURAL_GRI[1]:
        raise PlafonCulturalIndisponibil(d, "fereastra GRI (semestru fara ordin confirmat).")
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
    """Plafonul maxim lunar al tichetelor de cresa: (Decimal, sursa). = 450 * nr_copii (L165 art.19(1), baza
    confirmata). Indexarea (740 lei S1 2026, Ordin MF/MMSS 368/179/2026, MO 249/31.03.2026) e CONFIRMATA la EMITENT
    (mmuncii.gov.ro) si prin MO-referinta din surse multiple (04.08.2026), DAR: textul operativ al ordinului NU s-a
    obtinut (primar strict), functia nu are inca mecanism de ferestre datate (ca plafon_cultural), iar valorile
    intermediare (ex. 710) nu-s cercetate -> indexarea RAMANE NEaplicata (cap conservator la baza 450). Se
    deblocheaza cand: (a) se obtine textul ordinului 368/179/2026 la MO + (b) se adauga un mecanism de ferestre
    _FERESTRE_CRESA cu istoricul complet. Vezi DECIZII 04.08."""
    n = int(nr_copii) if nr_copii else 1
    if n < 1:
        n = 1
    return Decimal("450") * n, "Legea 165/2018 art.19(1) - baza 450/luna/copil (indexare GRI verdict 17, neaplicata)"


PRAG_VOLATIL_LUNI = 18  # Corpus (2) garda 3: fereastra +/- fata de azi in care o valoare curenta e "recenta"


def _luni_distanta(d1, d2):
    """Numar de luni intre doua date (valoare absoluta), aproximat pe an*12+luna. Robust la viitor/trecut."""
    return abs((d2.year - d1.year) * 12 + (d2.month - d1.month))


def cote_volatile_fara_mo(la_data=None):
    """Corpus (2) garda 3 (semnal la generare, NU zgomot): cotele a caror VALOARE CURENTA (ultima intrare)
    nu are nivel_sursa='MO' SI e volatila (cota are >=2 intrari datate) SAU recenta (data_in in +/-18 luni
    fata de la_data). Valorile REDARE stabile-vechi cu o singura intrare NU apar -> semnalul e util doar
    unde conteaza (act de sursat sau de decis). Intoarce lista sortata de nume de cota."""
    if la_data is None:
        la_data = date.today()
    out = []
    for nume, intrari in COTE.items():
        if not intrari:
            continue
        d, _v, t = max(intrari, key=lambda iv: iv[0])  # valoarea CURENTA = data_in cea mai mare (COTE e ordonat descrescator, dar nu ne bazam pe ordine)
        if getattr(t, "nivel_sursa", None) == "MO":
            continue
        volatila = len(intrari) >= 2
        recenta = _luni_distanta(d, la_data) <= PRAG_VOLATIL_LUNI
        if volatila or recenta:
            out.append(nume)
    return sorted(out)


def avertizeaza_cote_volatile_fara_mo(la_data=None, logger=None):
    """Hook apelabil la generarea unei declaratii: emite UN warning agregat cu cotele volatile fara sursa MO
    (folosind cota curenta). Nu blocheaza generarea - doar semnaleaza ce e de sursat. Intoarce lista."""
    import logging
    lst = cote_volatile_fara_mo(la_data)
    if lst:
        (logger or logging.getLogger("iconta.corpus")).warning(
            "Corpus: %d cote au valoarea curenta fara sursa MO (de sursat/decis): %s",
            len(lst), ", ".join(lst))
    return lst


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


def salariu_minim_luna(la_data=None, strict=True):
    """CF art.77 alin.(3) teza finala: cand in cursul ACELEIASI luni se utilizeaza mai multe valori ale
    salariului minim brut pe tara, se ia in calcul valoarea CEA MAI MICA (acelasi principiu la plafonul de
    20% facilitate). Intoarce (valoare, temei) = cea mai mica valoare a salariului minim ACTIVA in luna lui
    la_data (implicit azi). O luna cu o singura valoare = identic cu cota(). Period-aware.
    TEMEI verificat verbatim in anaf_surse/cod_fiscal_227_2015_consolidat.html (art.77 alin.3)."""
    la_data = la_data or date.today()
    prima = date(la_data.year, la_data.month, 1)
    urm = _adauga_luni(prima, 1)
    active = []
    for din, val, temei in COTE["salariu_minim"]:
        out = getattr(temei, "data_out", None)
        if din < urm and (out is None or out >= prima):
            active.append((val, temei))
    if not active:
        return cota("salariu_minim", prima, strict=strict)
    return min(active, key=lambda vt: vt[0])


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


# LIMITE_TEXT_ANAF = sursa UNICA a limitelor de text pentru XML-ul declaratiilor: lungimea
# oficiala C(n) a fiecarui camp din structura ANAF (anaf_surse/dNNN_struct*), CONFIRMATA
# boundary-cu-boundary pe validatorul DUK (len==C(n) -> valid, len==C(n)+1 -> respins).
#
# ISTORIC (corectat 03.08.2026): pana aici se folosea o limita GLOBALA 74, pe premisa "ANAF
# respinge orice text >75". Premisa a fost INFIRMATA de proba DUK: fiecare camp are C(n) propriu
# (den 200, adresa 1000, functie_declar 50, nume/prenume 75, functie_reprez 100, den1 100, ...).
# Limita 74 OVER-trunchia den/adresa/nume/prenume (pierdere de date pe denumiri/adrese reale) SI
# sub-trunchia functie_declar (74 > C(50) => ANAF respingea functii de 51-74 car.). Vezi
# DECIZII.md 03.08 (audit limita text) + GARZI.md. Orice limita noua se adauga AICI, dupa ce e
# probata pe DUK; codul NU are voie sa treaca o limita literala (garda de clasa test_limita_text).
LIMITE_TEXT_ANAF = {
    "d100": {"den": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75, "telefon": 15},
    "d101": {"denumire": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75, "telefon": 15},
    "d112": {"den": 200, "numeAsig": 75, "prenAsig": 75, "nume_declar": 75, "prenume_declar": 75, "functie_declar": 50},
    "d205": {"den": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75, "den1": 100},
    "d300": {"den": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75, "banca": 50, "cont": 50},
    "d301": {"denumire": 200, "adresa": 1000, "functia_declarant": 50, "nume_declarant": 75, "prenume_declarant": 75, "banca": 50, "cont": 50},
    "d390": {"den": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75, "mail": 200, "denO": 200},
    "d394": {"den": 200, "adresa": 1000, "denR": 200, "functie_reprez": 100, "adresaR": 1000, "den_intocmit": 75, "calitate_intocmit": 75, "denP": 200},
    "d710": {"den": 200, "adresa": 1000, "functie_declar": 50, "nume_declar": 75, "prenume_declar": 75},
    # d406 = SAF-T: limitele sunt tipurile din XSD (d406_schema_anaf.xlsx, foaia SimpleTypes):
    # SAFshorttextType=18, SAFmiddle1textType=35, SAFmiddle2textType=70, SAFlongtextType=256.
    "d406": {"CompanyName": 256, "StreetName": 70, "City": 35, "PostalCode": 18, "ContactLastName": 70,
             "PartnerName": 70, "AccountDescription": 256, "Description": 256, "PaymentMethod": 18},
}


def text_anaf(v, limita):
    """Text pentru un atribut/element XML de declaratie: normalizeaza spatiile si TRUNCHIAZA la
    `limita`. `limita` este OBLIGATORIE = lungimea oficiala C(n) a campului, din LIMITE_TEXT_ANAF
    (nu exista limita globala - fiecare camp are C(n) propriu, confirmat pe DUK). Un apel fara
    limita e o eroare (TypeError), tocmai ca sa fie imposibil sa emiti text cu o limita ne-oficiala."""
    t = " ".join(str(v or "").split())      # normalizeaza spatiile multiple
    return t[:limita]
