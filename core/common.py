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


# Valori care se ACTUALIZEAZA PERIODIC prin act normativ nou (HG, OUG, lege).
# Pentru ele, lipsa unei valori pentru anul urmator NU inseamna ca cea veche ramane -
# inseamna ca nimeni n-a actualizat registrul. Diferenta conteaza: prima interpretare
# produce declaratii gresite IN TACERE.
#
# 29.07.2026: cota() intorcea tacit ultima valoare cunoscuta pentru orice data viitoare.
# In ianuarie 2027, D112 ar fi folosit salariul minim din iulie 2026 fara niciun semnal.
# {nume: luni_de_valabilitate_de_la_ultima_intrare}
EXPIRA_DUPA_LUNI = {
    "salariu_minim": 12,                      # HG anuala, uneori si la mijloc de an
    "facilitate_salariu_minim": 12,           # OUG anuala
    "plafon_facilitate_salariu_minim": 12,    # OUG anuala
    "plafon_mijloc_fix": 24,                  # se schimba rar, dar se schimba
}


def cota(nume, la_data=None, strict=True):
    """Intoarce (valoare, temei) valabila la data data (implicit azi).

    Permite semnalarea greselilor de PERIOADA, nu doar de moment.

    EXPIRARE (29.07.2026): pentru valorile din EXPIRA_DUPA_LUNI, daca data ceruta depaseste
    termenul de valabilitate al ultimei intrari, se RIDICA. Motivul: o cifra plauzibila si
    gresita intr-o declaratie depusa la ANAF e mai rea decat o eroare la generare. Cine chiar
    vrea valoarea veche (rapoarte istorice, comparatii) cheama cu strict=False.
    """
    if nume not in COTE:
        raise ValueError(f"cotă necunoscută: {nume!r}")
    la_data = la_data or date.today()
    intrari = sorted(COTE[nume], key=lambda r: r[0], reverse=True)
    for din, valoare, temei in intrari:
        if la_data >= din:
            luni = EXPIRA_DUPA_LUNI.get(nume)
            if strict and luni and din == intrari[0][0]:
                limita = _adauga_luni(din, luni)
                if la_data > limita:
                    raise ValueError(
                        f"{nume}: ultima valoare cunoscută este din {din.isoformat()} "
                        f"({temei}), valabilă până la {limita.isoformat()}. "
                        f"S-a cerut pentru {la_data.isoformat()}. "
                        f"Verifică dacă a apărut un act normativ nou și actualizează COTE "
                        f"în core/common.py. Nu se folosește valoarea veche: ar produce o "
                        f"cifră plauzibilă și greșită într-o declarație depusă la ANAF."
                    )
            return valoare, temei
    raise ValueError(f"nicio valoare pentru {nume!r} la data {la_data}")


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


def cote_care_expira(in_zile=60, la_data=None):
    """Valorile a caror valabilitate se termina in urmatoarele `in_zile`.

    Folosit de jobul lunar de avertizare: schimbarile fiscale nu sunt aleatorii (salariul
    minim se schimba in decembrie sau iulie), deci un termen anuntat inainte e mai util
    decat o stire de presa dupa.
    """
    la_data = la_data or date.today()
    rez = []
    for nume, luni in EXPIRA_DUPA_LUNI.items():
        if nume not in COTE:
            continue
        din, valoare, temei = sorted(COTE[nume], key=lambda r: r[0], reverse=True)[0]
        limita = _adauga_luni(din, luni)
        zile = (limita - la_data).days
        if zile <= in_zile:
            rez.append({"nume": nume, "valoare": valoare, "temei": temei,
                        "din": din, "expira": limita, "zile": zile})
    return sorted(rez, key=lambda r: r["zile"])


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
