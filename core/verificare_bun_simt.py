# -*- coding: utf-8 -*-
"""core/verificare_bun_simt.py — [lotul 13, deficiența 656 + comanda 13.1 pct.5] VERIFICAREA PROPRIE A CIFRELOR unei declarații, înaintea
validatorului ANAF.

CE ERA GREȘIT. O D207 cu impozit reținut 160 lei pe o bază de 1 leu s-a generat și a trecut DUKIntegrator „fără erori”: validatorul
verifică FORMA (atribute, sume de control, liste), nu dacă impozitul e plauzibil față de bază. Comanda 13.1, verbatim: „Lipsește
verificarea proprie: impozit ≤ bază și cota conformă tipului de venit și actului normativ. Probă automată pe toate declarațiile rare.”

CE FACE. `verifica(tip, body, conn=None)` -> (erori, avertismente): erorile opresc generarea (o cifră imposibilă nu pleacă la ANAF),
avertismentele se arată lângă rezultat. Chemată pe drumul fiecărei cereri a omului (`uc_declaratii.poarta_cererii`: pasul 2 al
Declarațiilor, generarea, intrarea în coadă), după generator și înaintea validatorului. Scripturile de citire (cifrele de referință,
amprentele) cheamă dispecerul fără ea. Verificările stau pe declarație, în `VERIFICARI`; o declarație fără cifre de bază și impozit (ex.
D107, D230, D603) nu are ce verifica aici — `FARA_CIFRE` le numește, ca proba automată (`core/test_lot13_decl_rare.py`) să nu poată uita
una: fiecare declarație rară e ori în `VERIFICARI`, ori în `FARA_CIFRE`, cu motivul.

TEMEIURILE (textul, din `anaf_surse/`):
  - CF art.224 alin.(4) (cotele impozitului reținut nerezidenților, forma în vigoare): „b) 16% pentru veniturile din dividende prevăzute la
    art. 223 alin. (1) lit. a)” (Legea 141/2025 art.II pct.41, „se aplică veniturilor din dividende distribuite începând cu data de 1
    ianuarie 2026”); „c) 50% pentru veniturile prevăzute la art. 223 alin. (1) lit. b)-g), i), k), l) și o), dacă veniturile sunt plătite
    într-un cont dintr-un stat cu care România nu are încheiat un instrument juridic în baza căruia să se realizeze schimbul de
    informații”; „c^1) 10% în cazul veniturilor impozabile enumerate la art. 223 alin. (1) lit. b)- i) și k)-p) obținute din România de
    persoane fizice rezidente într-un stat membru al Uniunii Europene sau într-un stat cu care România are încheiată o convenție de evitare
    a dublei impuneri”; „d) 16% în cazul oricăror altor venituri impozabile obținute din România, așa cum sunt enumerate la art. 223 alin.
    (1)”. Pentru 2025, OUG 156/2024 art.LXIV pct.15: „b) 10% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a);”, în
    vigoare la 1 ianuarie 2025 (art.LXV alin.(1)). Cota dividendelor dinainte de 2025 NU e verificată aici în corpus pentru art.224 —
    pentru anii aceia se verifică numai că impozitul nu depășește baza.
  - CF art.230 alin.(1): „În situația în care sunt cote diferite de impozitare în legislația internă sau în convențiile de evitare a dublei
    impuneri, se aplică cotele de impozitare mai favorabile.” — de aici, la actul „convenție” sau „acord internațional”, impozitul nu poate
    depăși cota din Codul fiscal.
  - CF art.500^2 lit.a (D216): cota impozitului special — registrul `common.cota("impozit_special_valoare_mare")`.
  - CF art.291 (cotele TVA, D311): registrul `common.cota("tva_standard" / "tva_redusa…")`, prin `d301_operatiuni_api.cote_perioada`.
  - HG 1/2016 pct.73 alin.(13)-(14) (D318, deficiența 638): „(13) În cazul în care cererea de rambursare vizează o perioadă de rambursare
    mai mică de un an calendaristic, dar mai mare de 3 luni, cuantumul TVA pentru care se solicită o rambursare nu poate fi mai mic de 400
    euro sau echivalentul acestei sume în moneda națională a statului de rambursare. (14) În cazul în care cererea de rambursare se referă la
    o perioadă de rambursare de un an calendaristic sau la perioada rămasă dintr-un an calendaristic, cuantumul TVA nu poate fi mai mic de 50
    euro sau echivalentul acestei sume în moneda națională a statului de rambursare.”
"""
from __future__ import annotations

import datetime as _dt
from decimal import Decimal, ROUND_HALF_UP

from core import common as _c
from core.erori import RefuzGenerare

_CF = "anaf_surse/cod_fiscal_227_2015_consolidat.html"
# Cotele CF art.224 alin.(4), în procente (cum le scrie legea), fiecare cu textul ei din corpus; fracția o face `_fr` la folosire.
_ART224 = dict(art="224", alin="4", verificat_la="2026-10-25", de_cine="Code (lotul 13, 656)", nivel_sursa="MO", url=_CF)
#: dividendele plătite nerezidenților distribuite în 2025 — OUG 156/2024 art.LXIV pct.15 (în vigoare la 1 ianuarie 2025, art.LXV alin.(1))
COTA_DIVIDENDE_NEREZIDENTI_2025 = _c.ancoreaza("verificare_bun_simt.COTA_DIVIDENDE_NEREZIDENTI_2025", Decimal("10"),
    _c.Temei("OUG", 156, 2024, art="LXIV", data_in="2025-01-01", verificat_la="2026-10-25", de_cine="Code (lotul 13, 656)",
             nivel_sursa="MO", url="anaf_surse/oug_156_2024.txt",
             text_citat="b) 10% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a);",
             lant_acte="OUG 156/2024 art.LXIV pct.15: „La articolul 224 alineatul (4), litera b) se modifică”; înlocuită din 2026 de "
                       "Legea 141/2025 (COTA_DIVIDENDE_NEREZIDENTI_2026)"))
#: dividendele plătite nerezidenților distribuite din 2026 — CF art.224 alin.(4) lit.b, forma dată de Legea 141/2025 art.II pct.41
COTA_DIVIDENDE_NEREZIDENTI_2026 = _c.ancoreaza("verificare_bun_simt.COTA_DIVIDENDE_NEREZIDENTI_2026", Decimal("16"),
    _c.Temei("CF", lit="b", data_in="2026-01-01", text_citat="b) 16% pentru veniturile din dividende prevăzute la art. 223 alin. (1) lit. a)",
             lant_acte="Legea 141/2025 art.II pct.41: „se aplică veniturilor din dividende distribuite începând cu data de 1 ianuarie 2026”",
             **_ART224))
#: celelalte venituri impozabile ale nerezidenților — CF art.224 alin.(4) lit.d
COTA_ALTE_VENITURI_NEREZIDENTI = _c.ancoreaza("verificare_bun_simt.COTA_ALTE_VENITURI_NEREZIDENTI", Decimal("16"),
    _c.Temei("CF", lit="d", data_in="2021-01-01",
             text_citat="d) 16% în cazul oricăror altor venituri impozabile obținute din România, așa cum sunt enumerate la art. 223 alin. (1)",
             **_ART224))
#: aceleași venituri, la persoanele fizice rezidente în UE / într-un stat cu convenție — CF art.224 alin.(4) lit.c^1 (Legea 296/2020)
COTA_VENITURI_NEREZIDENTI_PF_UE = _c.ancoreaza("verificare_bun_simt.COTA_VENITURI_NEREZIDENTI_PF_UE", Decimal("10"),
    _c.Temei("CF", lit="lit.c^1", data_in="2021-01-01",   # `lit.` scris: formatul canonic nu are litera cu exponent
             text_citat="10% în cazul veniturilor impozabile enumerate la art. 223 alin. (1) lit. b)- i) și k)-p) obținute din România de "
                        "persoane fizice rezidente într-un stat membru al Uniunii Europene",
             **_ART224))
#: venituri plătite într-un stat fără instrument juridic de schimb de informații — CF art.224 alin.(4) lit.c
COTA_VENITURI_FARA_SCHIMB_INFORMATII = _c.ancoreaza("verificare_bun_simt.COTA_VENITURI_FARA_SCHIMB_INFORMATII", Decimal("50"),
    _c.Temei("CF", lit="c", data_in="2016-01-01",
             text_citat="c) 50% pentru veniturile prevăzute la art. 223 alin. (1) lit. b)-g)",
             lant_acte="… dacă veniturile sunt plătite într-un cont dintr-un stat cu care România nu are încheiat un instrument juridic în "
                       "baza căruia să se realizeze schimbul de informații",
             **_ART224))


def _fr(cota_impozit):
    """Cota impozitului (în procente, cum o scrie Codul fiscal) ca fracție a bazei — impozit pe venit, nu TVA."""
    return cota_impozit / 100


# [lotul 13, reparațiile finale] Fracțiile se fac LA FOLOSIRE, în funcții, nu în structuri de modul calculate la import: o constantă
# ancorată citită numai de cod de modul n-are cititor în graful consumatorilor (`core/consumatori_temei.py`), deci reverificarea ei ar fi
# ieșit „consecință necunoscută” (core/test_consumatori_temei.py). Aceleași valori, același temei.
def cota_dividende_nerezidenti(an):
    """Cota pe anul distribuirii dividendelor, ca fracție — numai anii verificați la sursă; altfel None (se verifică doar impozit ≤ bază)."""
    return {2025: _fr(COTA_DIVIDENDE_NEREZIDENTI_2025), 2026: _fr(COTA_DIVIDENDE_NEREZIDENTI_2026)}.get(an)


def cote_alte_venituri():
    """Cotele Codului fiscal pentru celelalte venituri (lit.c^1, lit.d, lit.c), ca fracții."""
    return (_fr(COTA_VENITURI_NEREZIDENTI_PF_UE), _fr(COTA_ALTE_VENITURI_NEREZIDENTI), _fr(COTA_VENITURI_FARA_SCHIMB_INFORMATII))


def cota_maxima_conventie_alte():
    """art.230 alin.(1): convenția se aplică numai dacă e mai favorabilă — cota din Codul fiscal (lit.d) e plafonul."""
    return _fr(COTA_ALTE_VENITURI_NEREZIDENTI)

#: D207: tipurile de venit care sunt chiar „cf. convenției” (nomenclatorul structurii D207): actul normativ nu poate fi Codul fiscal
TIP_D207_CONVENTIE = {"22", "23", "24", "25"}
TIP_D207_DIVIDENDE = {"01", "22"}
TIP_D207_SCUTIT = {"%02d" % n for n in range(12, 22)}

#: D318: pragul minim al cererii de rambursare, în euro — HG 1/2016 pct.73 alin.(13) (perioadă sub un an) și alin.(14) (an / rest de an)
_PCT73 = dict(art="pct.73", verificat_la="2026-10-25", de_cine="Code (lotul 13, 638)", nivel_sursa="MO",
              url="anaf_surse/hg_1_2016_norme_cod_fiscal.html")
PRAG_D318_EUR_PERIOADA = _c.ancoreaza("verificare_bun_simt.PRAG_D318_EUR_PERIOADA", Decimal("400"),
    _c.Temei("HG", 1, 2016, alin="13", data_in="2016-01-13",
             text_citat="cuantumul TVA pentru care se solicită o rambursare nu poate fi mai mic de 400 euro sau echivalentul acestei sume în "
                        "moneda națională a statului de rambursare", **_PCT73))
PRAG_D318_EUR_AN = _c.ancoreaza("verificare_bun_simt.PRAG_D318_EUR_AN", Decimal("50"),
    _c.Temei("HG", 1, 2016, alin="14", data_in="2016-01-13",
             text_citat="perioada rămasă dintr-un an calendaristic, cuantumul TVA nu poate fi mai mic de 50 euro sau echivalentul acestei sume",
             **_PCT73))

#: Declarațiile rare FĂRĂ cifre de bază și impozit pe care să le compare aplicația — cu motivul (proba automată le cere pe toate).
FARA_CIFRE = {
    "d107": "sumele sponsorizărilor / mecenatului sunt cele plătite, fără impozit calculat pe ele",
    "d110": "regularizarea compară impozitul datorat cu cel reținut, ambele din documentele plătitorului, fără bază",
    "d114": "contribuția se calculează de ecran din venit (nu e scrisă de om)",
    "d177": "plafoanele redirecționării le verifică generatorul (suma redirecționată ≤ suma maximă)",
    "d204": "venitul net se distribuie pe cote; generatorul verifică Σcote = 100 și Σvenit = venitul net",
    "d212": "impozitul și contribuțiile le calculează aplicația (motorul D212), nu le scrie omul",
    "d230": "procentul redirecționat (≤ 3,5%) îl verifică generatorul; nu e impozit pe o bază",
    "d307": "D307 declară numai sumele de TVA ale ajustărilor, fără bază",
    "d398": "TVA-ul fiecărei livrări îl calculează ecranul (bază × cotă); cotele sunt ale statelor de consum",
    "d603": "declarația de exceptare nu conține sume",
    "d710": "D710 corectează sume declarate în D100 (datorat inițial / corect), fără bază",
    "d106": "doar prin API: dividendele acționarilor de stat, cifrele din hotărârea de repartizare",
    "d108": "doar prin API: impozitul pe reprezentanță e o sumă fixă în euro (CF art.236)",
    "d119": "doar prin API: declarație specială a BNR",
    "d120": "doar prin API: decontul anual de accize (totalPlata_A = 0, structura)",
    "d130": "doar prin API: decontul impozitului la țiței, sumele din formular",
    "d169": "doar prin API: fiducie, fără sume de impozit",
    "d169n": "doar prin API: neconcordanțe beneficiar real, fără sume",
    "d213": "doar prin API: impozitul îl stabilește ANAF",
    "d214": "doar prin API: impozitul îl stabilește ANAF",
    "d393": "doar prin API: venituri din bilete, fără impozit",
    "d395": "doar prin API: trimiteri contra ramburs, fără impozit",
    "d397": "doar prin API: transport alternativ, fără impozit",
    "d399": "doar prin API: regimul special de import (IOSS), TVA-ul pe statele de consum",
    "d401": "doar prin API: informații DAC, fără impozit",
    "d402": "doar prin API: informații DAC1, fără impozit",
    "d403": "doar prin API: informații DAC2, fără impozit",
    "d407": "doar prin API: informații CRS, fără impozit",
    "d101g": "doar prin API: grupul fiscal, cifrele din D101 ale membrilor",
}


def _int(x):
    """Suma scrisă de om -> întreg (lei), rotunjire aritmetică (CLAUDE.md: Decimal + ROUND_HALF_UP). Gol -> 0. Ilizibil -> None."""
    if x in (None, ""):
        return 0
    try:
        return int(Decimal(str(x).strip()).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except Exception:  # noqa: BLE001 — o sumă ilizibilă o refuză generatorul, cu mesajul lui (numar_fiscal)
        return None


def _dec(x):
    try:
        return Decimal(str(x).strip()) if x not in (None, "") else Decimal("0")
    except Exception:  # noqa: BLE001
        return None


def _lei(n):
    """1234 -> „1.234 lei” (forma românească a sumei, DS cap.4)."""
    return "{:,}".format(int(n)).replace(",", ".") + " lei"


def _proc(c):
    p = (Decimal(c) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return ("%d%%" % p) if p == p.to_integral() else ("%s%%" % p.normalize()).replace(".", ",")


def _aproape(suma, asteptat):
    """Abaterea admisă față de bază × cotă: 1 leu, plus 0,5% din impozit (impozitul se reține pe fiecare plată, rotunjit pe plată)."""
    return abs(Decimal(suma) - asteptat) <= max(Decimal(1), asteptat / 100 / 2)


# ── D207 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _d207(body, conn=None):
    er = []
    an = body.get("an")
    for i, b in enumerate((body.get("manual") or {}).get("beneficiari") or [], 1):
        cine = "Beneficiarul %d (%s)" % (i, str(b.get("den") or "").strip() or "fără nume")
        tv = str(b.get("tip_venit") or "").zfill(2)
        baza, imp, imps = _int(b.get("baza")), _int(b.get("imp")), _int(b.get("imp_suportat"))
        if None in (baza, imp, imps):
            continue   # suma ilizibilă: refuzul generatorului o numește
        if baza < 0 or imp < 0 or imps < 0:
            er.append("%s: baza și impozitul nu pot fi negative." % cine)
            continue
        total = imp + imps
        if total > baza:
            er.append("%s: impozitul (%s) e mai mare decât baza (%s). Impozitul reținut nerezidentului e un procent din venitul brut "
                      "(CF art.224 alin.(4)) — verifică baza și impozitul scrise." % (cine, _lei(total), _lei(baza)))
            continue
        if tv in TIP_D207_SCUTIT or not baza:
            continue
        act = str(b.get("act_n") or "")
        if tv in TIP_D207_CONVENTIE and act == "1":
            er.append("%s: tipul de venit e „cf. convenției de evitare a dublei impuneri”, dar actul normativ ales e Codul fiscal — alege "
                      "„Convenție de evitare a dublei impuneri” sau tipul de venit din Codul fiscal." % cine)
            continue
        cota_div = cota_dividende_nerezidenti(int(an)) if isinstance(an, int) else None
        alte = cote_alte_venituri()
        if act == "1":
            if tv in TIP_D207_DIVIDENDE:
                if cota_div is not None and not _aproape(total, Decimal(baza) * cota_div):
                    er.append("%s: la dividende plătite în %d, Codul fiscal cere impozit de %s din bază (CF art.224 alin.(4) lit.b): %s, nu "
                              "%s. Dacă se aplică o convenție de evitare a dublei impuneri, alege actul „Convenție”." % (
                                  cine, an, _proc(cota_div), _lei(int((Decimal(baza) * cota_div).quantize(Decimal("1"), ROUND_HALF_UP))),
                                  _lei(total)))
            elif not any(_aproape(total, Decimal(baza) * c) for c in alte):
                er.append("%s: impozitul (%s) nu corespunde niciunei cote din Codul fiscal pentru acest venit (CF art.224 alin.(4): 16%%; 10%% "
                          "pentru persoanele fizice din UE sau dintr-un stat cu convenție; 50%% în statele fără schimb de informații) — "
                          "pe baza de %s ar fi %s sau %s. Dacă se aplică o convenție, alege actul „Convenție”." % (
                              cine, _lei(total), _lei(baza), _lei(int((Decimal(baza) * alte[1]).quantize(Decimal("1"), ROUND_HALF_UP))),
                              _lei(int((Decimal(baza) * alte[0]).quantize(Decimal("1"), ROUND_HALF_UP)))))
        elif act in ("2", "3"):
            maxim = cota_div if tv in TIP_D207_DIVIDENDE else cota_maxima_conventie_alte()
            if maxim is not None and Decimal(total) > (Decimal(baza) * maxim).quantize(Decimal("1"), ROUND_HALF_UP) + 1:
                er.append("%s: cu o convenție / un acord internațional, impozitul (%s) nu poate depăși cota din Codul fiscal (%s din %s = %s; "
                          "CF art.230 alin.(1): se aplică cota mai favorabilă)." % (
                              cine, _lei(total), _proc(maxim), _lei(baza),
                              _lei(int((Decimal(baza) * maxim).quantize(Decimal("1"), ROUND_HALF_UP)))))
    return er, []


# ── D205 completat de mână (dividendele preluate) ───────────────────────────────────────────────────────────────────────────────────
def _d205(body, conn=None):
    er = []
    for i, b in enumerate((body.get("manual") or {}).get("beneficiari") or [], 1):
        baza, imp = _int(b.get("baza")), _int(b.get("imp"))
        if None in (baza, imp):
            continue
        if imp > baza:
            er.append("Beneficiarul %d (%s): impozitul reținut (%s) e mai mare decât baza (%s)." % (
                i, str(b.get("nume") or "").strip() or "fără nume", _lei(imp), _lei(baza)))
    return er, []


# ── D104 (asocierea fără personalitate juridică) ─────────────────────────────────────────────────────────────────────────────────────
def _d104(body, conn=None):
    er = []
    for i, a in enumerate((body.get("manual") or {}).get("asociati") or [], 1):
        venit = _int(a.get("venit"))
        for camp, et in (("imp_datorat", "impozitul datorat"), ("imp_declarat", "impozitul declarat")):
            imp = _int(a.get(camp))
            if venit is not None and imp is not None and imp > max(venit, 0):
                er.append("Asociatul %d (%s): %s (%s) e mai mare decât venitul distribuit (%s)." % (
                    i, str(a.get("den") or "").strip() or "fără nume", et, _lei(imp), _lei(max(venit, 0))))
    return er, []


# ── D208 (notarii) ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _d208(body, conn=None):
    er = []
    for imob in (body.get("manual") or {}).get("imobile") or []:
        for i, b in enumerate(imob.get("beneficiari") or [], 1):
            baza, imp = _int(b.get("baza_calcul")), _int(b.get("impozit"))
            # cota impozitului pe transferul proprietăților imobiliare (CF art.111), câmpul `cotaImpozit` al D208 — impozit, nu TVA: nu trece
            # prin `tva_calcul` (eFactura regula BR-CO-17 rotunjește la ban, iar impozitul se compară în lei întregi — o rotunjire, nu două)
            cota_impozit = _dec(b.get("cotaImpozit"))
            if None in (baza, imp) or cota_impozit is None:
                continue
            impozit_asteptat = Decimal(baza) * cota_impozit / 100
            cine = "Beneficiarul %d (%s)" % (i, str(b.get("nume") or "").strip() or "fără nume")
            if imp > baza:
                er.append("%s: impozitul (%s) e mai mare decât baza de calcul (%s)." % (cine, _lei(imp), _lei(baza)))
            elif not _aproape(imp, impozit_asteptat):
                er.append("%s: impozitul (%s) nu e %s%% din baza de calcul (%s = %s)." % (
                    cine, _lei(imp), cota_impozit.normalize(), _lei(baza), _lei(int(impozit_asteptat.quantize(Decimal("1"), ROUND_HALF_UP)))))
    return er, []


# ── D216 (impozitul special pe bunurile de valoare mare) ─────────────────────────────────────────────────────────────────────────────
def _d216(body, conn=None):
    from core import common as _c
    er = []
    an = body.get("an")
    if not isinstance(an, int):
        return er, []
    try:
        legal = _c.cota("impozit_special_valoare_mare", _dt.date(an, 1, 1))[0] * 100   # procent
    except Exception:  # noqa: BLE001 — anul fără cotă în registru: generatorul refuză cu motivul lui
        return er, []
    for i, b in enumerate((body.get("manual") or {}).get("imobile") or [], 1):
        c = _dec(b.get("cota"))
        if c is not None and c and c != legal:
            er.append("Clădirea %d: cota scrisă (%s%%) nu e cota legală pe %d (%s%%, CF art.500^2 lit.a)." % (
                i, str(c.normalize()).replace(".", ","), an, str(legal.normalize()).replace(".", ",")))
    return er, []


# ── D311 (TVA după anularea codului) ─────────────────────────────────────────────────────────────────────────────────────────────────
_D311_RANDURI = (("OB_11", "OB_12", "livrările / prestările"), ("OB_21", "OB_22", "achizițiile cu taxare inversă"),
                 ("OB_41", "OB_42", "livrările cu TVA la încasare"))


def _d311(body, conn=None):
    from core import d301_operatiuni_api as _d301
    er = []
    m = body.get("manual") or {}
    an, luna = body.get("an"), body.get("luna")
    try:
        cote = [Decimal(o["val"]) / 100 for o in _d301.cote_perioada(an, luna) if o["val"]]
    except (TypeError, ValueError):   # `common.PerioadaIndisponibila` (ValueError): perioada fără cote în registru / an-lună lipsă: numai comparația TVA ≤ bază
        cote = []
    maxim = max(cote) if cote else Decimal("1")
    for kb, kt, et in _D311_RANDURI:
        baza, tva = _int(m.get(kb)), _int(m.get(kt))
        if None in (baza, tva):
            continue
        if tva and not baza:
            er.append("D311, %s: TVA de %s fără bază — completează baza impozabilă." % (et, _lei(tva)))
        elif tva > (Decimal(baza) * maxim).quantize(Decimal("1"), ROUND_HALF_UP) + 1:
            er.append("D311, %s: TVA (%s) e mai mare decât baza (%s) × cota cea mai mare a perioadei (%s)." % (
                et, _lei(tva), _lei(baza), _proc(maxim)))
    return er, []


# ── D318 (rambursarea TVA din alt stat membru) ───────────────────────────────────────────────────────────────────────────────────────
def _d318(body, conn=None):
    er, av = [], []
    m = body.get("manual") or {}
    total = Decimal("0")
    for fel in ("achizitii", "importuri"):
        for i, f in enumerate(m.get(fel) or [], 1):
            ta, va, dv = (_dec(f.get(k)) for k in ("taxable_amount", "vat_amount", "deductible_vat"))
            if None in (ta, va, dv):
                continue
            if abs(dv) > abs(va):
                er.append("Factura %s (%s): TVA-ul deductibil cerut (%s) e mai mare decât TVA-ul facturii (%s)." % (
                    f.get("reference_number") or i, "import" if fel == "importuri" else "achiziție", dv, va))
            total += dv
    moneda = str(m.get("currency") or "").strip().upper()
    try:
        an, li, ls = int(m.get("an") or body.get("an")), int(m.get("luna_inceput") or 1), int(m.get("luna_sfarsit") or 12)
    except (TypeError, ValueError):
        return er, av
    # alin.(14): perioada de un an sau RESTUL anului (până la decembrie) -> 50 euro; alin.(13): perioada mai scurtă -> 400 euro
    sfarsit_de_an = ls == 12
    prag = PRAG_D318_EUR_AN if sfarsit_de_an else PRAG_D318_EUR_PERIOADA
    temei = "HG 1/2016 pct.73 alin.(%s)" % ("14" if sfarsit_de_an else "13")
    eur = _in_euro(conn, total, moneda, _dt.date(an, ls, 28))
    if eur is None:
        av.append("Pragul minim al cererii de rambursare (%s euro, %s) nu s-a putut verifica: lipsește cursul BNR pentru %s. "
                  "Verifică-l înainte de depunere." % (prag, temei, moneda or "monedă"))
    elif eur < prag:
        er.append("Cererea de rambursare pe %02d–%02d/%d cere %s %s (aproximativ %s euro la cursul BNR), sub pragul minim de %s euro: %s — "
                  "„cuantumul TVA pentru care se solicită o rambursare nu poate fi mai mic de %s euro sau echivalentul acestei sume în moneda "
                  "națională a statului de rambursare”. Adaugă facturile restului perioadei sau depune cererea pe tot anul." % (
                      li, ls, an, str(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)).replace(".", ","), moneda,
                      str(eur.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)).replace(".", ","), prag, temei, prag))
    return er, av


def _in_euro(conn, suma, moneda, zi):
    """Suma în euro, la cursurile BNR ale ultimei zile bancare a perioadei (moneda/RON și EUR/RON, `curs_bnr.curs_sfarsit_luna`). None
    dacă un curs lipsește sau conexiunea lipsește (calcul pur)."""
    if not moneda:
        return None
    if moneda == "EUR":
        return suma
    if conn is None:
        return None
    from core import curs_bnr as _cb
    import calendar as _cal
    ultima = _dt.date(zi.year, zi.month, _cal.monthrange(zi.year, zi.month)[1])
    try:
        c_mon = _cb.curs_sfarsit_luna(conn, moneda, ultima)[0] if moneda != "RON" else Decimal("1")
        c_eur = _cb.curs_sfarsit_luna(conn, "EUR", ultima)[0]
    except (_cb.CursIndisponibil, _cb.CursPreaVechi):   # cursul lipsă / prea vechi nu oprește cererea: devine avertisment („nu s-a putut verifica”)
        return None
    return (suma * Decimal(c_mon) / Decimal(c_eur))


VERIFICARI = {"d207": _d207, "d205": _d205, "d104": _d104, "d208": _d208, "d216": _d216, "d311": _d311, "d318": _d318}


def verifica(tip, body, conn=None):
    """(erori, avertismente) pentru declarația cerută (`body` = cererea, cu `manual`)."""
    f = VERIFICARI.get(str(tip or "").lower())
    if f is None or not isinstance(body, dict):
        return [], []
    return f(body, conn)


def poarta(tip, body, res, conn=None):
    """Pe drumul cererii (`uc_declaratii.poarta_cererii`): erorile opresc generarea (`RefuzGenerare`, ecranul o arată ca refuz),
    avertismentele se adaugă la rezultat (`res.avertismente`)."""
    er, av = verifica(tip, body, conn)
    if er:
        raise RefuzGenerare("%s nu se generează — verificarea cifrelor: %s" % (str(tip).upper(), " ".join(er)))
    if av and res is not None and not isinstance(res, list):
        try:
            res.avertismente = list(getattr(res, "avertismente", None) or []) + av
        except AttributeError:
            pass
