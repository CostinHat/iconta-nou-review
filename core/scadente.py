"""
core/scadente.py — calculează data scadenței unei declarații (format zz/ll/aaaa),
mutată la prima zi lucrătoare dacă pică în weekend/sărbătoare. PUR, fără DB.

Verificat la sursa oficială (calendar ANAF 2026):
  D100, D112, D300, D301, D390 -> 25 ale lunii următoare
  D394                          -> 30 ale lunii următoare
  D406 (SAF-T)                  -> ultima zi a lunii următoare
  trimestrial (D100/D300/...)   -> 25 (sau 30/ultima zi) ale lunii următoare trim.
  D205                          -> ultima zi februarie an următor
  D101                          -> 25 iunie an următor (OUG 153/2020 art.I alin.(13) lit.a pt 2021-2025; OUG 8/2026 art.6 pct.12 -> art.42(1) CF pt 2026+)
Toate se mută la prima zi lucrătoare dacă pică în weekend/sărbătoare legală — CU O EXCEPȚIE: ce cade nominal
pe 25 decembrie (obligațiile lunii noiembrie) e scadent pe 21 decembrie, iar dacă 21 e nelucrătoare, în ultima zi
lucrătoare DINAINTE (CPF art.155 alin.(2), v. TEMEI_21_DECEMBRIE). Termenul se mută ÎNAPOI, nu înainte.

ATENȚIE — termenul legal NU e atributul `scadenta` din XML. Validatorul ANAF cere în declarație scadența
NOMINALĂ (25.12): DUK regula R15.6 (D100) și DUK regula R25 (D300, nr_evid) resping 21.12 — probat 03.10.2026.
Generatorii (d100/d110/d114/d300/d301/d710) își păstrează ziua 25; aici se calculează data până la care
contabilul trebuie să depună și să plătească (calendar, semafor, coadă, control fiscal, cashflow).

Sărbătorile sunt într-un dict EDITABIL per an (Paște/Rusalii variază anual).
"""
from __future__ import annotations
import calendar
from datetime import date, timedelta
from core.cache_declarat import Declaratie as _Dec

REGULI = "2026.1"
MODUL = "scadente"

# Sărbători legale RO. Cele Paște-dependente (Vinerea Mare, Paște, Rusalii) se
# CALCULEAZĂ din data Paștelui ortodox (Legea 220/2016), NU se hardcodează per an -
# altfel calendarul devine incomplet in tacere peste cativa ani (istoric: 2025 lipsea
# COMPLET, iar Vinerea Mare lipsea din 2026 -> proratare CM gresita). Fixe = art. 139
# Codul muncii. Sursa unica: sarbatori_legale(an).
_SARB_FIXE = [(1, 1), (1, 2), (1, 6), (1, 7), (1, 24), (5, 1), (6, 1),
              (8, 15), (11, 30), (12, 1), (12, 25), (12, 26)]
_AN_MIN, _AN_MAX = 2024, 2099   # set fix (cu 6-7 ian) valabil din 2024; offset iulian +13 pana 2099
_cache_sarb = {}
_cache_sarb_DECLARATIE = _Dec(
    rol="memo pentru `sarbatori_legale(an)`, chemata de fiecare calcul de scadenta si de fiecare "
        "proratare de concediu medical",
    sursa="chiar functia `sarbatori_legale`, care e PURA: `_SARB_FIXE` (art. 139 Codul muncii) plus "
          "cele cinci zile derivate din `paste_ortodox(an)` (Legea 220/2016)",
    motiv="calculul Pastelui ortodox se reface altfel la fiecare intrebare despre o zi lucratoare",
    invalidare="NICIODATA, si asta e raspunsul corect, nu o lipsa: valoarea unui an nu se poate "
               "schimba la rulare, iar domeniul e marginit prin `_AN_MIN`/`_AN_MAX` la [2024, 2099], "
               "deci cel mult 76 de chei — un plafon scris, nu unul sperat",
    dovada="core/test_cache_declarat.py::test_sarbatori_se_reconstruiesc_identic",
)

# [R4, 21.08.2026] TEMEIUL PER TIP, ca DATE — nu ca proză. Termenele sunt constante fiscale ca oricare
# altele: notorietatea e o proprietate a CUNOAȘTERII, nu a valorii. S-au schimbat de două ori în viața
# aplicației și NICIUNA n-a fost prinsă de un test (scadența D101 marca fals restanțieri; ziua 30
# inexistentă în februarie).
#
# DE CE REGISTRU ȘI NU COMENTARIU. Prima variantă a pus citările într-un bloc de comentarii, iar gardul
# le căuta prin proximitate (numele tipului la ±8 rânduri de un act). Rezultatul: nota „unde se caută
# pentru cele nesursate" a făcut TOATE tipurile să pară sursate — gardul a trecut pe gol. Proximitatea
# nu e atribuire; aceeași lecție ca la clasa E din scanul de constante, unde antetul modulului părea
# să sursere orice valoare din el.
#
# Fiecare intrare: (act, fișier din corpus, citat VERBATIM). Citatul se verifică mecanic — vezi
# `core/test_temei_termene.py`, care caută fragmentul în fișier, nu se mulțumește cu referința.
TEMEI_TERMEN = {
    "d300": ("CF art. 323 alin.(1)", "anaf_surse/cod_fiscal_227_2015_consolidat.html",
             "până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală"),
    "d301": ("CF art. 324", "anaf_surse/cod_fiscal_227_2015_consolidat.html",
             "până la data de 25 inclusiv a lunii următoare celei în care ia naștere exigibilitatea"),
    "d390": ("OPANAF 705/2020", "anaf_surse/opanaf_705_2020_d390.txt",
             "se depune lunar, până la data de 25 inclusiv a lunii următoare unei luni calendaristice"),
    "d208": ("CF art.113", "anaf_surse/cod_fiscal_227_2015_consolidat.html",
             "au obligația să depună lunar, până la data de 25 inclusiv a lunii următoare celei în care a avut loc "
             "autentificarea actelor privind transferul proprietăților imobiliare"),
}
# NESURSATE ÎNCĂ (clichetul le numără): d100, d101, d112, d205, d394, d406. Unde se caută, ca
# următorul să nu reia de la zero: d112 → CF art. 147; d100 → CF art. 56 (micro) și art. 41 (plăți
# anticipate profit); d101 → CF art. 42; d205 → OPANAF 179/2022 + 102/2025; d394 → OPANAF 3769/2015
# actualizat prin 2194/2025; d406 → OPANAF 1783/2021 Anexa 4. ATENȚIE la consolidat: are întâi un
# CUPRINS cu aceleași marcaje „Articolul N", deci numărul se derivă mergând ÎNAPOI de la fraza găsită,
# nu căutând titlul articolului.

# [Lot 19 defect 7, 03.10.2026] Aplicația arăta 28.12.2026 pentru obligațiile lui noiembrie (25 și 26 decembrie
# sărbători, 27 duminică -> mutare ÎNAINTE). Legea cere 21 decembrie, mutat ÎNAPOI.
TEMEI_21_DECEMBRIE = ("CPF art.155 alin.(2)", "anaf_surse/legea_207_2015_consolidat.txt",
                      "scadența și/sau termenul de declarare se împlinesc la 25 decembrie, sunt scadente și/sau se "
                      "declară până la data de 21 decembrie. În situația în care data de 21 decembrie, este zi "
                      "nelucrătoare, creanțele fiscale sunt scadente și/sau se declară până în ultima zi lucrătoare "
                      "anterioară datei de 21 decembrie")

# ziua nominală a scadenței per tip (în luna următoare perioadei)
_ZIUA = {"d394": 30}          # restul: 25 ; d406: ultima zi (tratat separat)
_ULTIMA_ZI = {"d406"}          # scadența = ultima zi a lunii


def paste_ortodox(an):
    """Data Paștelui ortodox (gregorian) — algoritmul Meeus pe calendarul iulian,
    convertit la gregorian (+13 zile, valabil 1900-2099). Verificat: 2025=20.04,
    2026=12.04, 2027=02.05."""
    a, b, c = an % 19, an % 4, an % 7
    d = (19 * a + 15) % 30
    e = (2 * b + 4 * c + 6 * d + 6) % 7
    zi = 22 + d + e
    iul = date(an, 3, zi) if zi <= 31 else date(an, 4, d + e - 9)
    return iul + timedelta(days=13)


def sarbatori_legale(an):
    """set de (lună, zi) — sărbătorile legale RO pentru an. Fixe (art. 139 Codul muncii)
    + Paște-dependente: Vinerea Mare (Paște−2), Paște (duminică+luni), Rusalii (Paște+49
    duminică, +50 luni). EȘUEAZĂ ZGOMOTOS in afara [2024, 2099] — un an neacoperit trebuie
    sa dea eroare vizibila, nu rezultat gresit TACUT (cazul 2025)."""
    if not (_AN_MIN <= an <= _AN_MAX):
        raise ValueError("sarbatori_legale: an %d neacoperit (valabil %d-%d). Extinde explicit."  # invariant-intern-ok: tabelul de sărbători din cod
                         % (an, _AN_MIN, _AN_MAX))
    if an not in _cache_sarb:
        p = paste_ortodox(an)
        mob = [p - timedelta(days=2), p, p + timedelta(days=1),
               p + timedelta(days=49), p + timedelta(days=50)]
        _cache_sarb[an] = set(_SARB_FIXE) | {(d.month, d.day) for d in mob}
    return _cache_sarb[an]


def _e_sarbatoare(d):
    return (d.month, d.day) in sarbatori_legale(d.year)


def e_zi_lucratoare(d):
    """True dacă d nu e weekend și nu e sărbătoare legală. Pură."""
    return d.weekday() < 5 and not _e_sarbatoare(d)


def zile_lucratoare_luna(an, luna):
    """Nr. de zile lucrătoare (L-V, FĂRĂ sărbători legale) dintr-o lună. SURSA UNICĂ —
    inlocuieste calculele ad-hoc weekday<5 (ignorau sarbatorile -> proratare CM gresita,
    OUG 158/2005 art.10) si tabelele hardcodate _D112_NZL."""
    return sum(1 for z in range(1, calendar.monthrange(an, luna)[1] + 1)
               if e_zi_lucratoare(date(an, luna, z)))


def zile_lucratoare_interval(start, end):
    """Nr. de zile lucrătoare (L-V, FĂRĂ sărbători legale) între start și end inclusiv.
    Folosit la auto-calcul zilelor de CM (numărătorul proratării, OUG 158/2005 art.10)."""
    if end < start:
        return 0
    n, d = 0, start
    while d <= end:
        if e_zi_lucratoare(d):
            n += 1
        d += timedelta(days=1)
    return n


def urmatoarea_zi_lucratoare(d):
    """Prima zi lucrătoare ≥ d. Pură."""
    while not e_zi_lucratoare(d):
        d += timedelta(days=1)
    return d


def _ultima_zi_luna(an, luna):
    return calendar.monthrange(an, luna)[1]


def _luna_urmatoare(an, luna):
    return (an + 1, 1) if luna == 12 else (an, luna + 1)


def _data_nominala(tip, an, luna=None, trim=None):
    """Data scadenței nominală (înainte de mutarea la zi lucrătoare)."""
    tip = tip.lower()
    if tip == "d205":
        # ultima zi februarie an următor
        a = an + 1
        return date(a, 2, _ultima_zi_luna(a, 2))
    if tip == "d101":
        # 25 IUNIE an următor, pentru TOȚI anii afectați. Verificat la sursă:
        #  2021-2025: OUG 153/2020 art. I alin. (13) lit. a), prin derogare de la art. 41-42 CF
        #    (anaf_surse/anaf_oug_153_2020_reduceri_impozit.txt; MO 817/04.09.2020).
        #  2026+:     OUG 8/2026 art. 6 pct. 12 modifică permanent art. 42 alin. (1) CF, aplicabil
        #    din anul fiscal 2026 (anaf_surse/oug_8_2026.txt).
        # (Era 25.03 hardcodat "PROVIZORIU" -> marca fals restanțieri firmele care depuneau apr-iun.)
        return date(an + 1, 6, 25)

    if tip in ("s1005", "s1003"):
        # [C11, 07.10.2026] Bilanțul (situațiile financiare anuale ale societăților). Legea 82/1991 art.36 alin.(1) lit.a), forma
        # OUG 138/2024 (anaf_surse/legea_82_1991_consolidat.txt): „societățile reglementate de Legea nr. 31/1990 … până la data de
        # 31 mai inclusiv a exercițiului financiar următor celui de raportare”; alin.(1^1): zi nelucrătoare -> „prima zi
        # lucrătoare următoare” (= `termen_legal`). Exercițiul diferit de anul calendaristic (alin.(1^2), 150 de zile) nu e
        # modelat: firmele aplicației au exercițiul = anul calendaristic.
        return date(an + 1, 5, 31)

    if trim is not None:
        # luna următoare trimestrului: T1->4, T2->7, T3->10, T4->1(an+1)
        if trim == 4:
            an_s, luna_s = an + 1, 1
        else:
            an_s, luna_s = an, trim * 3 + 1
    elif luna is not None:
        an_s, luna_s = _luna_urmatoare(an, luna)
    else:
        raise ValueError("scadență: lipsește luna sau trim pentru %r" % tip)

    if tip in _ULTIMA_ZI:
        zi = _ultima_zi_luna(an_s, luna_s)
    else:
        # ziua nominala, dar NICIODATA peste ultima zi a lunii: d394 are ziua 30, care nu
        # exista in februarie -> ultima zi (principiul legal: termen pe zi inexistenta = ultima
        # zi a lunii). 25 nu e afectat (orice luna are >=28 zile).
        zi = min(_ZIUA.get(tip, 25), _ultima_zi_luna(an_s, luna_s))
    return date(an_s, luna_s, zi)


def ultima_zi_lucratoare_pana_la(d):
    """Ultima zi lucrătoare ≤ d. Pură."""
    while not e_zi_lucratoare(d):
        d -= timedelta(days=1)
    return d


def termen_legal(nominala):
    """Data până la care se declară/plătește o obligație cu scadența nominală `nominala`: prima zi lucrătoare
    ≥ nominala, cu excepția lui 25 decembrie -> 21 decembrie sau ultima zi lucrătoare dinainte (CPF art.155
    alin.(2), TEMEI_21_DECEMBRIE). Pură."""
    if (nominala.month, nominala.day) == (12, 25):
        return ultima_zi_lucratoare_pana_la(date(nominala.year, 12, 21))
    return urmatoarea_zi_lucratoare(nominala)


def scadenta_data(tip, an, luna=None, trim=None):
    """Scadența legală ca obiect date (v. termen_legal). Pură."""
    return termen_legal(_data_nominala(tip, an, luna=luna, trim=trim))


def urmatorul_termen_lunar(azi):
    """Primul termen legal >= azi al obligațiilor lunare (TVA lunar, contribuții) — pe ziua sursată a D300 (CF art.323
    alin.(1), TEMEI_TERMEN). Pentru prognoze (cashflow), nu pentru o declarație anume. Pură."""
    an, luna = (azi.year, azi.month - 1) if azi.month > 1 else (azi.year - 1, 12)
    t = scadenta_data("d300", an, luna=luna)
    return t if azi <= t else scadenta_data("d300", azi.year, luna=azi.month)


def are_termen(tip, an, luna=None, trim=None):
    """[C2/C11, 07.10.2026] Are tipul un termen de depunere SURSAT în modulul ăsta? Un tip anual fără termen (D212, D230,
    D207 …) nu primește unul ghicit: coada îl etichetează cu perioada de raportare. Datoria: `core/test_datorie.py`."""
    try:
        _data_nominala(tip, an, luna=luna, trim=trim)
        return True
    except ValueError:
        return False


def scadenta(tip, an, luna=None, trim=None):
    """Scadența ca string 'zz.ll.aaaa' (mutată la zi lucrătoare), format RO canonic. Pură."""
    from core.pdf_util import data_ro
    d = scadenta_data(tip, an, luna=luna, trim=trim)
    return data_ro(d)
