"""
core/d205_reconciliere.py — A DOUA CALE D205 (gard de continut, 05.08.2026, pas 6/6).

D205 = impozit pe dividende retinut la sursa, per beneficiar. Generatorul deriva fiecare
beneficiar din: total dividende distribuite (Σ cont 457, note validate) x cota asociatului x cota
impozitului pe dividende (period-aware, common.cota("impozit_dividend")).

DE CE NU CROSS-CHECK D205<->D100 (cerinta Costin - "verifica pe AST ca nu e capcana paritatii"):
D100 declara ACELASI impozit pe dividende, derivat din ACEEASI distributie (cont 457). O
confruntare D205<->D100 ar citi aceeasi sursa de doua ori = same-source trap, exact ca paritatea
D300/D394 (tautologica prin propriul docstring). Deci calea 2 = RECALCUL PROPRIU al bazei si
impozitului per beneficiar din 457 + cota asociat + cota lege, confruntat cu res.beneficiari -
non-tautologic pe AGREGARE/FORMULA (SQL propriu + formula proprie), nu pe sursa.

CE PRINDE: beneficiar scapat din declaratie, baza/impozit gresit (cota asociat aplicata gresit,
cota impozitului gresita, rotunjire), dublare.
CE NU (LIMITA, GARZI cat.4):
  - Beneficiari MANUALI (manual["beneficiari"], introdusi de contabil) -> NEACOPERIT (§8).
  - Input partajat gresit (aceeasi postare 457 gresita citita de ambele cai) - §8.

NON-TAUTOLOGIE (AST): NU importa/foloseste d205.calcul_d205 / d205.pull. Cotele: common.cota
(registrul de lege). Divergenta = HARD-BLOCK care numeste beneficiarul si AMBELE valori.
"""

from core.pdf_util import diferenta as _dif, bani as _bani   # [Retest 2 pct.2] diferența în cuvinte
from core import afirmatii as _af  # [P8] necunoasterea isi poarta domeniul
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from core import repo_d205_reconciliere as _repo


class ReconciliereD205(ValueError):
    """Baza/impozitul pe dividende ale generatorului nu se leaga de recalculul independent."""


def _q(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _dividende_independent(conn, an):
    """[lot 19 pct.4e] Partea fiecărui asociat (bază + impozit) — SQL PROPRIU (457, asociați, istoricul
    cesiunilor, [lotul 10] soldul 457 din balanța de deschidere) + atribuirea din modulul NEUTRU `dividende_curs` (aceeași regulă ca
    generatorul, recitită independent din registru): fiecare tranșă după structura de la data distribuirii ei (Legea 31/1990 art.67
    alin.(2) și (6)), impozitul pe rata de la data distribuirii (A6). [lotul 10, decizia Costin A] Baza = distribuirile anului,
    plătite sau nu la 31.12 (OPANAF 179/2022 anexa 1 cap.II pct.9, antetul `dividende_curs`); plătitul anului se confruntă separat
    (divid_P). {cnp: (nume, baza_int, impozit_int, platit_int)}."""
    from core import common as _c
    from core import dividende_curs as _dc
    sf = date(an + 1, 1, 1).isoformat()
    with conn.cursor() as cur:
        asoc = _repo.select_asociati(cur)
        istoric = _repo.select_asociati_istoric(cur)
        randuri = _repo.select_457_miscari(cur, sf)
        deschidere = _repo.select_457_deschidere(cur, sf)
    chei = ("data", "distribuit", "impozit", "platit", "compensat", "distribuit_interimar", "impozit_interimar",
            "platit_interimar")   # [lotul 10, 431] impozitul înregistrat separat de plată; interimarele
    # [lotul 10, decizia A] soldul de deschidere 457 = distribuire deschisă dinaintea evidenței; la aceeași dată, înaintea notelor
    miscari = [{"data": d, "preluat": v} for d, v in deschidere] + [dict(zip(chei, r)) for r in randuri]
    miscari.sort(key=lambda m: (m["data"], "preluat" not in m))
    struct = _dc.structura_la(list(asoc), list(istoric))
    pe = _dc.atribuie_pe_asociati(miscari, an, lambda d: _c.cota("impozit_dividend", d)[0], struct)
    return {cnp: (r["nume"], _q(r["distribuit"]), _q(r["impozit"]), _q(r["platit"])) for cnp, r in pe.items()}


def _consistenta_interna(perioada, res):
    """d1 (CATALOG): regula fiscala INTERNA per beneficiar - imp1 == round(cota_dividend x baza1).
    DUK-INVIZIBILA: validatorul verifica doar Timp=Σimp1 (totalul), NU cota per beneficiar, deci un
    imp1 individual gresit trece DUK. Se aplica si beneficiarilor MANUALI (fara sursa in 457): NU
    recalculeaza baza dintr-un ledger (nu exista), confrunta doar cele doua campuri DEJA din
    declaratie intre ele. Cota din registrul de lege, period-aware - ACEEASI sursa ca d205
    (common.cota('impozit_dividend')). Toleranta rotunjire: 1 leu (imp1 introdus manual poate diferi
    de round() prin conventia de rotunjire a contabilului; o abatere >1 leu = eroare, nu rotunjire)."""
    an = perioada.an
    from core import common as _c   # registrul de lege (cota impozit dividende period-aware)
    rate_an = Decimal(str(_c.cota("impozit_dividend", date(an, 12, 31))[0]))
    rate_prev = Decimal(str(_c.cota("impozit_dividend", date(an - 1, 12, 31))[0]))
    rate_set = {rate_an, rate_prev}
    divergente = []
    for b in res.beneficiari:
        # [A6, 18.09.2026] Un dividend poate fi DISTRIBUIT în anul anterior (cota acelui an) și plătit
        # acum — imp1 e consistent dacă = round(baza1 × r) pentru rata anului CURENT SAU a celui
        # ANTERIOR (art.VII alin.2 Legea 141/2025: distribuirea 2025 rămâne 10% chiar plătită în 2026).
        # d1 rămâne o plasă contra unui imp1 grosolan greșit (0, dublu, cotă inexistentă), fără să bată
        # rata legitimă de la granița anilor.
        asteptat = _q(Decimal(int(b.baza1)) * rate_an)
        if all(abs(int(b.imp1) - _q(Decimal(int(b.baza1)) * r)) > 1 for r in rate_set):
            divergente.append({"beneficiar": b.cif or b.nume1, "camp": "consistenta_interna",
                               "imp1": int(b.imp1), "rate_baza": asteptat})
    return divergente


def reconciliaza(conn, schema, perioada, res, manual=None):
    """NU ridica. {"acoperit":bool, "neacoperit":afirmatie|None, "divergente":[...]}."""
    manual = manual or {}
    if manual.get("beneficiari"):
        # d1 (CATALOG): beneficiari MANUALI - recalculul din 457 NU se aplica (nicio sursa in
        # registru), DAR imp1 trebuie sa ramana round(cota_dividend x baza1) - regula fiscala
        # INTERNA, invizibila DUK. acoperit ramane False (§8: baza NU e recalculata dintr-o sursa
        # independenta), dar divergentele de consistenta interna se raporteaza (ridica in
        # verifica_reconciliere). Inainte: return divergente=[] TACIT -> imp1 gresit trecea + DUK valid.
        return {"acoperit": False, "divergente": _consistenta_interna(perioada, res),
                "neacoperit": _af.necunoastere_pe_luna(
                    "d205",
                    "Beneficiarii sunt introduși manual de contabil: recalculul din contul 457 nu se "
                    "aplică; se verifică doar că impozitul fiecăruia e cota dividendului "
                    "înmulțită cu baza, rotunjită.", perioada.an)}
    an = perioada.an
    parti = _dividende_independent(conn, an)
    gen = {str(b.cif): b for b in res.beneficiari}
    divergente = []
    for cnp, (nume, parte, imp, platit) in parti.items():
        if parte <= 0 and platit <= 0:
            continue
        b = gen.get(str(cnp or ""))
        if b is None:
            divergente.append({"beneficiar": cnp or nume, "camp": "beneficiar LIPSA din declaratie",
                               "generator": 0, "cale2_baza": parte, "cale2_imp": imp})
            continue
        if int(b.baza1) != parte:
            divergente.append({"beneficiar": cnp or nume, "camp": "baza",
                               "generator": int(b.baza1), "cale2": parte, "diferenta": int(b.baza1) - parte})
        if int(b.imp1) != imp:
            divergente.append({"beneficiar": cnp or nume, "camp": "impozit",
                               "generator": int(b.imp1), "cale2": imp, "diferenta": int(b.imp1) - imp})
        if int(b.divid_p) != platit:   # [lotul 10, decizia A] plătitul anului (divid_P) e acum separat de bază
            divergente.append({"beneficiar": cnp or nume, "camp": "dividende plătite",
                               "generator": int(b.divid_p), "cale2": platit, "diferenta": int(b.divid_p) - platit})
    return {"acoperit": True, "neacoperit": None, "divergente": divergente}


def verifica_reconciliere(conn, schema, perioada, res, manual=None):
    """POARTA (hard-block): ridica ReconciliereD205 daca baza/impozitul pe dividende nu se leaga de
    recalculul independent. Numeste beneficiarul si AMBELE valori. NU repara tacit."""
    rap = reconciliaza(conn, schema, perioada, res, manual)
    if rap["divergente"]:
        det = []
        interne = all(d["camp"] == "consistenta_interna" for d in rap["divergente"])
        for d in rap["divergente"]:
            if d["camp"] == "consistenta_interna":
                det.append(_dif("beneficiarul %s, impozitul reținut" % d["beneficiar"], d["imp1"], d["rate_baza"],
                                sursa="introdus"))
            elif d["camp"].startswith("beneficiar LIPSA"):
                det.append("beneficiarul %s lipsește din declarație (recalculat: baza %s, impozitul %s)"
                           % (d["beneficiar"], _bani(d["cale2_baza"], "lei"), _bani(d["cale2_imp"], "lei")))
            else:
                det.append(_dif("beneficiarul %s, %s" % (d["beneficiar"], d["camp"]), d["generator"], d["cale2"], d["diferenta"]))
        if interne:
            raise ReconciliereD205(
                "D205: impozitul reținut introdus manual nu este cota de impozit pe dividende aplicată "
                "bazei. Validatorul ANAF verifică numai totalul, nu fiecare beneficiar. Diferențe: %s. "
                "Declarația nu se generează: corectează impozitul sau baza." % "; ".join(det))
        raise ReconciliereD205(
            "D205: baza și impozitul pe dividende din declarație nu se potrivesc cu recalculul făcut "
            "separat din contul 457. Diferențe: %s. Declarația nu se generează: aplicația nu alege singură care dintre cele două calcule e corect. Verifică datele perioadei; dacă sunt corecte, anunță echipa iConta." % "; ".join(det))
    return rap
