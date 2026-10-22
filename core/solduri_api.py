"""
core/solduri_api.py — import solduri inițiale (balanță de deschidere) per firmă.

Citește o balanță (.xlsx/.csv) cu coloanele: Cont, Denumire, Sold debitor, Sold creditor.
Soldurile se salvează în schema tenantului (tabel solduri_initiale, auto-creat).
Conturile analitice (4111.ALPHA, 401.GAMMA) se păstrează ca atare — așa intră planul
analitic, derivat direct din balanță.

"""
# [E2b, 15.09.2026] Tranzactia e a APELANTULUI: `db.get_conn` comite la iesirea din bloc, iar un
# `commit` aici ar taia tranzactia lui in doua (P4). Depozitul primeste conexiunea si scrie; nu
# deschide, nu comite.
from __future__ import annotations


def _numar(v, strict=False):
    """Transformă o valoare în număr (acceptă '1.234,56', '1,234.56', '(500)', '', None).

    PARANTEZELE = sumă negativă — convenția contabilă din exporturile SAGA/Ciel/Excel
    (format „contabil"). Fără asta, `(500)` cădea pe `float()` și devenea 0.0 TĂCUT:
    soldul dispărea din balanță, iar totalurile păreau corecte. Dovedit de test, nu de
    utilizator (15.07.2026).

    strict=True → ridică ValueError pe text neinterpretabil, în loc să întoarcă 0.
    Un sold care devine 0 în tăcere e mai periculos decât un import refuzat.
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).strip()
    if not t:
        return 0.0
    t = t.replace(" ", "").replace("\xa0", "")
    # format contabil: (500) = -500
    neg = t.startswith("(") and t.endswith(")")
    if neg:
        t = t[1:-1].strip()
    # sufixe de moneda din exporturi: "1.234,56 RON" / "500 lei"
    for suf in ("RON", "ron", "LEI", "Lei", "lei", "EUR", "eur"):
        if t.endswith(suf):
            t = t[:-len(suf)].strip()
    # dacă are și punct și virgulă, ultimul separator e zecimala
    if "," in t and "." in t:
        if t.rfind(",") > t.rfind("."):
            t = t.replace(".", "").replace(",", ".")   # 1.234,56
        else:
            t = t.replace(",", "")                      # 1,234.56
    elif "," in t:
        # virgulă singură: zecimală dacă are 1-2 cifre după, altfel separator de mii
        parte = t.split(",")[-1]
        t = t.replace(",", ".") if len(parte) <= 2 else t.replace(",", "")
    try:
        x = float(t)
    except ValueError:
        if strict:
            raise ValueError("valoare numerică neinterpretabilă: %r" % (v,))
        return 0.0
    return -x if neg else x


# ── citirea balanței (C21, comanda Costin 14.10.2026, verbatim în DECIZII „Importul din SAGA”) ──────────────────────────
# Fișierul trece prin `core.import_tabel` (sursa unică: format, codare, antet, coloane). Aici rămâne numai ce e propriu
# balanței: CARE pereche debit/credit e soldul final, ce rânduri nu sunt conturi, și sinteticele dublate de analiticele lor.
from core import import_tabel as _it
from core import migrare_api as _mig   # [426, clasa] înlocuirea confirmată, comună importurilor
from core import chei_unice as _chei   # [lotul 10, C73] cheia naturală dublată -> refuz numit, nu 500
from core.pdf_util import bani as _bani, data_ro as _data_ro   # DS cap.4: sumele și datele din text, canonic
from core.common import cate as _cate   # numeralul acordat („1 cont”, „20 de conturi”), gardul `test_plural_dupa_numar`
import re as _re

CAMPURI = {
    "cont": ("simbol cont", "cont contabil", "nr cont", "=cont", "=simbol", "simbol*"),
    "denumire": ("denumire cont", "denumirea contului", "titlu cont", "denumire*", "explicatie", "nume"),
    "debit": ("debit*", "d"),
    "credit": ("credit*", "c"),
}

# un cont: 3–6 cifre, opțional un analitic după punct / cratimă / bară („401.00001” SAGA, „4111.ALPHA”, „5121-1”)
_CONT = _re.compile(r"^\d{3,6}(?:[.\-/][0-9A-Za-z][0-9A-Za-z.\-/_]*)?$")


def _e_stramos(a, b):
    """`a` e sinteticul lui `b` (b ≠ a): „411” -> „4111”, „4111” -> „4111.0001”, „401” -> „401.00001”."""
    if a == b:
        return False
    if b.startswith(a + "."):
        return True
    ra, rb = a.split(".")[0], b.split(".")[0]
    return "." not in a and ra.isdigit() and rb != ra and rb.startswith(ra)


def extrage_balanta_detaliat(continut, nume_fisier=""):
    """`{randuri, coloane, ignorate, sintetice_inlocuite, fara_sold}` din balanța din fișier.

    - `randuri` = [{cont, denumire, debit, credit}] — soldurile FINALE, numai frunzele (analiticele, nu și sinteticul lor);
    - `coloane` = antetul coloanelor citite (ecranul le arată: „s-au citit «Sold final debitor» / «Sold final creditor»”);
    - `ignorate` = rândurile care nu sunt conturi (totaluri, titluri de clasă) — numărate și arătate, nu importate;
    - `sintetice_inlocuite` = sinteticele scoase fiindcă fișierul are analiticele lor (cu același sold net);
    - `fara_sold` = conturi fără nimic de preluat (sold final 0 / 0 și, când fișierul are rulajele, nici sold inițial, nici rulaj);
    - `rulaje` = fișierul are soldurile inițiale ale anului și rulajele (deficiența 425): fiecare rând poartă `si_debit`, `si_credit`,
      `rulaj_debit`, `rulaj_credit`, iar conturile cu sold final 0 dar cu rulaj intră; `perechi` = antetele perechilor citite."""
    brut = _it.citeste(continut, nume_fisier)
    if not brut or all(_it.rand_gol(r) for r in brut):
        return {"randuri": [], "coloane": {}, "ignorate": [], "sintetice_inlocuite": [], "fara_sold": 0, "rulaje": False,
                "perechi": {}}
    antet, start = _it.gaseste_antet(brut, CAMPURI, obligatorii=("cont",), nume_fisier=nume_fisier)
    i_cont = _it.coloana(antet, CAMPURI["cont"], camp="cont")
    i_den = _it.coloana(antet, CAMPURI["denumire"], exclus=(i_cont,), camp="denumire")
    i_deb, i_cre = _it.pereche_sold_final(antet, nume_fisier)
    # [deficiența 425] celelalte perechi ale balanței de verificare (solduri inițiale an, sume precedente, rulaje, total sume)
    per = _it.perechi_balanta(antet, nume_fisier)
    # [439] o sursă a rulajelor anului: un total cumulat (total sume / total rulaje) sau precedentele + rulajele lunii
    cu_rulaje = "si" in per and (any(g in per for g in TOTALURI) or ("rl" in per and any(g in per for g in PRECEDENTE)))

    citite, ignorate, fara_sold = [], [], 0
    for nr, r in enumerate(brut[start:], start=start + 1):
        if _it.rand_gol(r):
            continue
        cont = _it.celula(r, i_cont)
        if not _CONT.match(cont):
            eticheta = cont or _it.celula(r, i_den) or "(rând fără cont)"
            ignorate.append(eticheta)
            continue
        try:
            deb = _numar(_it.valoare(r, i_deb), strict=True) if i_deb >= 0 else 0.0
            cre = _numar(_it.valoare(r, i_cre), strict=True) if i_cre >= 0 else 0.0
        except ValueError:
            raise _it.FisierNecitit("Rândul %d (contul %s): soldul final „%s” / „%s” nu e un număr. Corectează celula și "
                                    "încarcă fișierul din nou." % (nr, cont, _it.celula(r, i_deb), _it.celula(r, i_cre)))
        # [comanda Costin 8.2 pct.4] numărul rândului din fișier: previzualizarea arată fiecare rând cu starea lui, pe numărul lui
        x = {"cont": cont, "denumire": _it.celula(r, i_den), "debit": deb, "credit": cre, "rand_fisier": nr}
        if cu_rulaje:
            x["_perechi"] = _perechi_rand(r, per, nr, cont)    # [439] valorile brute; forma lor se stabilește pe tot fișierul
        citite.append(x)

    # același cont de două ori: baza are UNIQUE(cont) (GARZI cat.1) — refuz numit, nu o eroare de bază la scriere
    dubluri = conturi_dublate(citite)
    if dubluri:
        raise _it.FisierNecitit(MESAJ_CONT_DUBLAT % ", ".join(dubluri[:8]))
    # sinteticele dublate de analiticele lor: păstrez frunzele, dacă netul sinteticului = suma netului frunzelor lui
    conturi = [x["cont"] for x in citite]
    net = {}
    for x in citite:
        net[x["cont"]] = net.get(x["cont"], 0.0) + x["debit"] - x["credit"]
    frunze = [c for c in conturi if not any(_e_stramos(c, d) for d in conturi)]
    inlocuite = []
    for c in sorted(set(conturi) - set(frunze)):
        fiice = [f for f in set(frunze) if _e_stramos(c, f)]
        suma = round(sum(net[f] for f in fiice), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
        if abs(round(net[c], 2) - suma) >= 0.01:  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            raise _it.FisierNecitit(
                "Contul %s are în fișier sold final net %s, iar analiticele lui (%s) însumează %s. Balanța amestecă "
                "sintetice și analitice care nu se potrivesc — exportă balanța numai cu analitice (sau numai sintetică) și "
                "încarcă-o din nou." % (c, _bani(net[c], "lei"), ", ".join(sorted(fiice)[:5]), _bani(suma, "lei")))
        inlocuite.append(c)
    out = []
    for x in citite:
        if x["cont"] in inlocuite:
            continue
        # [deficiența 425] „cu toate conturile care au rulaj”: un cont cu sold final 0 (707, 607, 641 … închise pe 121) intră când are
        # sold inițial sau rulaj în an; numai contul fără nimic (sold final, sold inițial și rulaj zero) rămâne pe dinafară, numărat
        _miscare = cu_rulaje and any(v for p in x["_perechi"].values() for v in p)
        if round(x["debit"], 2) == 0 and round(x["credit"], 2) == 0 and not _miscare:  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            fara_sold += 1
            continue
        out.append(x)
    forma = None
    if cu_rulaje:
        # [439] numai frunzele: un sintetic bifuncțional poartă soldul NET, iar sumele lui brute (cumulul analiticelor) nu se închid pe el
        forma = forma_rulajelor(out)
        verifica_coloane(out, {g: [_it.eticheta(antet, d), _it.eticheta(antet, c)] for g, (d, c) in per.items()})
        verifica_rulaje(out)
    for x in citite:
        x.pop("_perechi", None)
    return {"randuri": out,
            "coloane": {"cont": _it.eticheta(antet, i_cont), "debit": _it.eticheta(antet, i_deb),
                        "credit": _it.eticheta(antet, i_cre)},
            "ignorate": ignorate, "sintetice_inlocuite": inlocuite, "fara_sold": fara_sold, "rulaje": cu_rulaje,
            # [425] ce perechi s-au citit, cu antetul lor din fișier (ecranul le numește)
            "perechi": {g: [_it.eticheta(antet, d), _it.eticheta(antet, c)] for g, (d, c) in per.items()},
            # [439] pentru fiecare pereche cumulată: cuprinde (True) sau nu (False) soldul inițial al anului — stabilit din date
            "forma_rulaje": forma}


# ── rulajele anului (deficiența 425, comanda Costin 10.1; deficiența 439, comanda Costin 11.1 — verbatim în DECIZII) ─────────────────
# `si_*` = soldul la 1 ianuarie al anului; `rulaj_*` = rulajele 01.01..data balanței FĂRĂ soldul inițial.
# [439] Perechile cumulate ale unei balanțe de verificare au DOUĂ forme, după seria de egalități aleasă la generare (manualul SAGA,
# „Balante”, anaf_surse/saga_manual_topic52_…: „Înainte de generarea balanței se vor seta seriile de egalități”):
# - CU soldul inițial al anului: „sume precedente” (manualul SAGA, „Preluare date contabile”, anaf_surse/saga_manual_topic12_…: „Debit
#   precedent” / „Credit precedent” = „rulajele cumulate (inclusiv soldurile iniţiale)”) și „total sume”;
# - FĂRĂ el: „rulaje precedente” și „total rulaje”.
# Verificarea lotului 10 presupunea că orice „… precedente” cuprinde soldul inițial și cerea `precedente + rulajele lunii = total sume`;
# pe „rulaje precedente” omitea soldul inițial al anului și refuza fiecare cont cu sold la 1 ianuarie (439). Acum antetul dă numai ORDINEA
# încercărilor: se păstrează forma pentru care TOATE conturile verifică ecuațiile balanței (OMFP 2634/2015 anexa 1 pct.52: „Soldul
# debitor sau creditor al fiecărui cont se stabilește în funcție de rulajele debitoare și creditoare ale contului respectiv, ținându-se
# seama de soldul de la începutul anului”):
#   rulajele anului = total − sold inițial (când totalul îl cuprinde) = precedente − sold inițial (când îl cuprind) + rulajele lunii;
#   sold inițial + rulajele anului = sold final (net, pe fiecare cont); fiecare pereche de coloane are debit = credit (`verifica_coloane`).
CHEI_RULAJE = ("si_debit", "si_credit", "rulaj_debit", "rulaj_credit")
TOTALURI = ("ts", "tr")
PRECEDENTE = ("sp", "rp")
#: forma după antet (prima încercată): True = coloana cuprinde soldul inițial al anului
CUPRINDE_SI = {"sp": True, "rp": False, "ts": True, "tr": False}
NUME_GRUP = {"si": "soldurile inițiale ale anului", "sp": "sumele precedente", "rp": "rulajele precedente", "rl": "rulajele lunii",
             "ts": "totalul sumelor", "tr": "totalul rulajelor"}


def _bani_d(v):
    from decimal import Decimal, ROUND_HALF_UP
    return Decimal(str(v or 0)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _perechi_rand(r, per, nr, cont):
    """`{grup: (debit, credit)}` (Decimal) dintr-un rând al balanței cu perechile `per`. Refuz numit pe o celulă care nu e număr."""
    v = {}
    for g, (i_d, i_c) in per.items():
        try:
            v[g] = (_bani_d(_numar(_it.valoare(r, i_d), strict=True)), _bani_d(_numar(_it.valoare(r, i_c), strict=True)))
        except ValueError:
            raise _it.FisierNecitit("Rândul %d (contul %s): o sumă din coloanele balanței nu e un număr („%s” / „%s”). Corectează celula și "
                                    "încarcă fișierul din nou." % (nr, cont, _it.celula(r, i_d), _it.celula(r, i_c)))
    return v


def _forme_incercate(grupuri):
    """Formele posibile ale perechilor cumulate din fișier ({grup: cuprinde soldul inițial}), cea din antet întâi, apoi după câte
    perechi se abat de la antet."""
    import itertools
    cum = [g for g in TOTALURI + PRECEDENTE if g in grupuri]
    forme = [dict(zip(cum, f)) for f in itertools.product((True, False), repeat=len(cum))]
    return sorted(forme, key=lambda f: sum(f[g] != CUPRINDE_SI[g] for g in cum))


def _surse(v, forma):
    """`[(grup, (rulaj debit, rulaj credit))]` — rulajele anului FĂRĂ soldul inițial, după fiecare sursă a rândului (totalurile întâi)."""
    si, out = v["si"], []
    for g in TOTALURI:
        if g in v:
            k = 1 if forma[g] else 0
            out.append((g, (v[g][0] - k * si[0], v[g][1] - k * si[1])))
    if "rl" in v:
        for g in PRECEDENTE:
            if g in v:
                k = 1 if forma[g] else 0
                out.append((g, (v[g][0] - k * si[0] + v["rl"][0], v[g][1] - k * si[1] + v["rl"][1])))
    return out


def _descrie(g, forma, ref_cuprinde):
    """Partea stângă a refuzului, spusă în termenii coloanei de referință (cu sau fără soldul inițial al anului)."""
    luna = g in PRECEDENTE
    if ref_cuprinde and not forma[g]:
        return "soldul inițial al anului plus " + NUME_GRUP[g] + (" plus rulajele lunii" if luna else "")
    if forma[g] and not ref_cuprinde:
        return NUME_GRUP[g] + " fără soldul inițial al anului" + (", plus rulajele lunii," if luna else "")
    return NUME_GRUP[g] + (" plus rulajele lunii" if luna else "")


def _abatere(x, forma, i):
    """Motivul pentru care rândul NU verifică forma (textul refuzului), sau None."""
    v, nr, cont = x["_perechi"], _it.nr_rand(x, i), x.get("cont")
    surse = _surse(v, forma)
    ref_g, ref = surse[0]
    si, k = v["si"], (1 if forma[ref_g] else 0)
    for g, r in surse[1:]:
        if abs(r[0] - ref[0]) >= _bani_d("0.01") or abs(r[1] - ref[1]) >= _bani_d("0.01"):
            return ("Rândul %d (contul %s): %s (debit %s, credit %s) nu dau %s (debit %s, credit %s). Balanța se contrazice — exportă-o din "
                    "nou din programul vechi." % (nr, cont, _descrie(g, forma, bool(k)), _bani(r[0] + k * si[0], "lei"),
                                                   _bani(r[1] + k * si[1], "lei"), NUME_GRUP[ref_g], _bani(v[ref_g][0], "lei"),
                                                   _bani(v[ref_g][1], "lei")))
    stanga = si[0] - si[1] + ref[0] - ref[1]
    dreapta = _bani_d(x.get("debit")) - _bani_d(x.get("credit"))
    if abs(stanga - dreapta) >= _bani_d("0.01"):
        return ("Rândul %d (contul %s): soldul inițial al anului și rulajele dau %s, iar soldul final din fișier e %s (net, debitor cu +). "
                "Balanța se contrazice — exportă-o din nou din programul vechi." % (nr, cont, _bani(stanga, "lei"), _bani(dreapta, "lei")))
    return None


def forma_rulajelor(randuri):
    """[439] Stabilește din DATE forma perechilor cumulate ({grup: cuprinde soldul inițial al anului}) și scrie pe fiecare rând
    `si_debit`, `si_credit`, `rulaj_debit`, `rulaj_credit`. Rândurile poartă `_perechi` (valorile brute). Se încearcă întâi forma din
    antet, apoi celelalte; rămâne prima pentru care TOATE conturile verifică ecuațiile. Nicio formă -> refuz numit, cu primul rând care nu
    verifică forma din antet. Două forme care verifică totul, dar dau rulaje diferite (un cont cu sold inițial și debitor, și creditor)
    -> refuz numit: nu se alege una."""
    if not randuri:
        return None
    forme = _forme_incercate(set(randuri[0]["_perechi"]))
    bune, motiv = [], None
    for f in forme:
        ab = next((m for m in (_abatere(x, f, i) for i, x in enumerate(randuri, start=2)) if m), None)
        if ab is None:
            bune.append(f)
        elif motiv is None:
            motiv = ab
    if not bune:
        raise _it.FisierNecitit(motiv)
    forma = bune[0]
    rez = [_surse(x["_perechi"], forma)[0][1] for x in randuri]
    for alta in bune[1:]:
        for i, (x, r) in enumerate(zip(randuri, rez), start=2):
            if _surse(x["_perechi"], alta)[0][1] != r:
                g = next(g for g in forma if forma[g] != alta[g])
                raise _it.FisierNecitit(
                    "Rândul %d (contul %s): din fișier nu se poate stabili dacă %s cuprind soldul inițial al anului — contul are sold "
                    "inițial și pe debit, și pe credit, iar ambele citiri închid balanța. Exportă balanța cu soldul inițial net (pe o "
                    "singură parte) și încarcă-o din nou." % (_it.nr_rand(x, i), x.get("cont"), NUME_GRUP[g]))
    for x, r in zip(randuri, rez):
        si = x["_perechi"]["si"]
        x.update({"si_debit": float(si[0]), "si_credit": float(si[1]), "rulaj_debit": float(r[0]), "rulaj_credit": float(r[1])})
    return forma


def verifica_coloane(randuri, etichete):
    """[439] PURĂ pe rândurile cu `_perechi`: fiecare pereche citită are totalul debitor egal cu cel creditor — OMFP 2634/2015 anexa 1
    pct.52: „Balanța de verificare este documentul contabil utilizat pentru verificarea înregistrării corecte în contabilitate a
    operațiunilor efectuate”; fiecare înregistrare are debit = credit, deci fiecare coloană. Refuz numit cu antetul perechii din fișier."""
    for g in ("si", "sp", "rp", "rl", "tr", "ts"):
        if g not in etichete or not randuri:
            continue
        d = sum((x["_perechi"][g][0] for x in randuri), _bani_d(0))
        c = sum((x["_perechi"][g][1] for x in randuri), _bani_d(0))
        if abs(d - c) >= _bani_d("0.01"):
            raise _it.FisierNecitit(
                "Coloanele „%s” / „%s” nu se echilibrează: debit %s, credit %s (diferență %s). Fiecare înregistrare are debit = credit, "
                "deci în balanța de verificare fiecare pereche de coloane are totalurile egale — exportă-o din nou din programul vechi."
                % (etichete[g][0], etichete[g][1], _bani(d, "lei"), _bani(c, "lei"), _bani(d - c, "lei")))


def verifica_rulaje(randuri):
    """PURĂ, ridică `ValueError` numit. Când balanța poartă soldurile inițiale ale anului și rulajele (deficiența 425):
    - le poartă TOATE rândurile (o balanță jumătate cu rulaje, jumătate fără, nu e o balanță);
    - pe fiecare cont, sold inițial + rulaj debitor − rulaj creditor = sold final (net, debitor cu +). OMFP 2634/2015 anexa 1 pct.52:
      „Soldul debitor sau creditor al fiecărui cont se stabilește în funcție de rulajele debitoare și creditoare ale contului respectiv,
      ținându-se seama de soldul de la începutul anului”;
    - soldurile inițiale se echilibrează (debit = credit), iar rulajele la fel — același pct.52: „Balanța de verificare este documentul
      contabil utilizat pentru verificarea înregistrării corecte în contabilitate a operațiunilor efectuate”; fiecare înregistrare are
      o sumă egală în debit și în credit, deci totalurile coloanelor sunt egale.
    Întoarce True dacă balanța are rulaje, False dacă are numai solduri finale."""
    randuri = randuri or []
    cu = [r for r in randuri if any(r.get(k) is not None for k in CHEI_RULAJE)]
    if not cu:
        return False
    if len(cu) != len(randuri) or any(r.get(k) is None for r in cu for k in CHEI_RULAJE):
        raise ValueError("Balanța are soldurile inițiale ale anului și rulajele numai pe o parte din conturi. Încarcă balanța de "
                         "verificare întreagă (aceleași coloane pe fiecare cont) sau numai soldurile finale.")
    tot = {k: _bani_d(0) for k in CHEI_RULAJE}
    for i, r in enumerate(randuri, start=2):
        b = {k: _bani_d(r.get(k)) for k in CHEI_RULAJE}
        for k in CHEI_RULAJE:
            tot[k] += b[k]
        dreapta = _bani_d(r.get("debit")) - _bani_d(r.get("credit"))
        stanga = b["si_debit"] - b["si_credit"] + b["rulaj_debit"] - b["rulaj_credit"]
        if abs(stanga - dreapta) >= _bani_d("0.01"):
            raise ValueError(
                "Rândul %d (contul %s): soldul inițial al anului și rulajele dau %s, iar soldul final din fișier e %s (net, debitor cu +). "
                "Balanța se contrazice — exportă-o din nou din programul vechi." % (
                    _it.nr_rand(r, i), r.get("cont"), _bani(stanga, "lei"), _bani(dreapta, "lei")))
    for d, c, ce in (("si_debit", "si_credit", "Soldurile inițiale ale anului"), ("rulaj_debit", "rulaj_credit", "Rulajele anului")):
        if abs(tot[d] - tot[c]) >= _bani_d("0.01"):
            raise ValueError("%s nu se echilibrează: debit %s, credit %s (diferență %s). Fiecare înregistrare are debit = credit, deci "
                             "o balanță completă le are egale." % (ce, _bani(tot[d], "lei"), _bani(tot[c], "lei"),
                                                                  _bani(tot[d] - tot[c], "lei")))
    return True


def avertisment_fara_rulaje(data_referinta):
    """[deficiența 425] „Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului lipsesc
    și ce afectează.” Textul, sau None când nu lipsește nimic: o balanță la 31 decembrie deschide exercițiul următor (rulajele anului
    de preluare încep de la zero)."""
    import datetime as _dt
    d = None
    if data_referinta:
        try:
            d = data_referinta if isinstance(data_referinta, _dt.date) else _dt.date.fromisoformat(str(data_referinta)[:10])
        except ValueError:
            d = None
    if d is not None and (d.month, d.day) == (12, 31):
        return None
    pana = (" până la %s" % _data_ro(d)) if d else ""
    return ("Fișierul are numai soldurile finale: soldurile de la 1 ianuarie și rulajele anului%s lipsesc, iar conturile cu sold final 0 "
            "(veniturile și cheltuielile închise pe 121, TVA-ul lunii) nu intră deloc. Fără ele ies greșite pentru anul preluării: "
            "declarația de impozit pe profit (D101) și situațiile financiare anuale (cifra de afaceri și cheltuielile anului), plafonul "
            "de microîntreprindere, controalele cumulate de TVA și coloanele „sold inițial” / „sume precedente” din balanța de "
            "verificare. Ca să le ai, încarcă balanța de verificare completă (solduri inițiale an, rulaje, total sume, solduri finale)."
            % pana)


#: [deficiența 425] „când balanța are sold pe 371, metoda de stoc se cere la migrare, nu rămâne «nedeclarată»” — 371 Mărfuri și 378
#: Diferențe de preț la mărfuri (OMFP 1802/2014 pct.594: „371. Mărfuri (A)”, „378. Diferenţe de preţ la mărfuri (A/P)”), cu analiticele
CONTURI_MARFA = ("371", "378")


def are_sold_marfa(randuri):
    """PURĂ: balanța are sold final pe un cont de mărfuri — atunci metoda de stoc a firmei se cere la migrare."""
    return any(str(r.get("cont") or "").split(".")[0].startswith(CONTURI_MARFA)
               and (_bani_d(r.get("debit")) != 0 or _bani_d(r.get("credit")) != 0) for r in (randuri or []))


def extrage_balanta(continut, nume_fisier=""):
    """Întoarce [{cont, denumire, debit, credit}] — soldurile finale din balanță (vezi `extrage_balanta_detaliat`)."""
    return extrage_balanta_detaliat(continut, nume_fisier)["randuri"]


def asigura_tabel(conn):
    """Creează tabelul solduri_initiale în schema curentă (search_path = tenantul)."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS solduri_initiale (
                id SERIAL PRIMARY KEY,
                cont TEXT NOT NULL,
                denumire TEXT NOT NULL DEFAULT '',
                sold_debitor NUMERIC(15,2) NOT NULL DEFAULT 0,
                sold_creditor NUMERIC(15,2) NOT NULL DEFAULT 0,
                data_referinta DATE
            )
        """)


def verifica_echilibru(randuri):
    """PURA: (ok, debit, credit, diferenta). O balanta de deschidere trebuie sa aiba
    totalul debitor egal cu cel creditor - altfel toata contabilitatea firmei porneste
    gresit."""
    td = round(sum(_numar(r.get("debit")) for r in (randuri or [])), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tc = round(sum(_numar(r.get("credit")) for r in (randuri or [])), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    dif = round(td - tc, 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    return abs(dif) < 0.01, td, tc, dif


#: [lotul 10, C73] același cont de două ori — la citirea fișierului ȘI la scriere (rândurile pot veni și direct, prin API)
MESAJ_CONT_DUBLAT = ("Contul %s apare de mai multe ori în balanță. Fiecare cont are un singur rând de sold; corectează "
                     "fișierul și încarcă-l din nou.")


def conturi_dublate(randuri):
    """PURĂ: conturile care apar pe mai multe rânduri, în ordinea primei dubluri. Baza are UNIQUE(cont) (`solduri_initiale_cont_uniq`)."""
    vazute, dubluri = set(), []
    for x in randuri or []:
        c = str(x.get("cont") or "").strip()
        if c in vazute and c not in dubluri:
            dubluri.append(c)
        vazute.add(c)
    return dubluri


def _refuz_cont_scris_intre_timp(cur, e):
    """[lotul 10, C73] Rândurile trimise n-au cont dublat (verificat înainte), deci violarea lui `solduri_initiale_cont_uniq` vine de la
    o altă salvare a balanței, terminată în timpul acesteia."""
    return _chei.CheieDublata("În timp ce salvai, altă salvare a scris deja soldul contului %s. Din balanța ta nu s-a scris nimic: "
                              "reîncarcă pagina, verifică balanța firmei și salveaz-o din nou dacă e cazul." % _chei.valoarea(e),
                              valoare=_chei.valoarea(e))


def balanta_valida(randuri):
    """PURA: (ok, motiv). O balanta reala are solduri (totaluri != 0) si conturi contabile.
    Un fisier strain (ex. istoric_declaratii.csv incarcat din greseala) e citit cu coloanele
    debit/credit NEGASITE -> toate 0 -> verifica_echilibru zice "echilibrat" (0==0). Fara
    aceasta poarta, o balanta GOALA se salva cu bulina verde si contabilul credea ca e in
    regula (constatare de ecran 09.08.2026). Paralela cu importul de parteneri, care compara
    cu balanta si arata diferenta; solduri n-avea nicio verificare de continut."""
    randuri = randuri or []
    if not randuri:
        return False, "Fișier gol: niciun rând de citit."
    td = round(sum(_numar(r.get("debit")) for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    tc = round(sum(_numar(r.get("credit")) for r in randuri), 2)  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
    conturi_cont = sum(1 for r in randuri if str(r.get("cont") or "").strip()[:1].isdigit())
    if conturi_cont == 0:
        return False, ("Fișier nerecunoscut ca balanță: nicio valoare din coloana Cont nu arată "
                       "a cont contabil (un cont începe cu cifră; „D394” nu e cont). "
                       "Verifică dacă ai încărcat balanța de deschidere.")
    if td == 0 and tc == 0:
        return False, ("Balanță fără solduri: total debitor și total creditor sunt amândouă 0 "
                       "(coloanele Sold debitor/creditor lipsesc sau toate valorile sunt 0). "
                       "„Echilibrat” pe 0 = 0 nu înseamnă o balanță validă.")
    return True, ""


def _adauga_conturi_lipsa(conn, randuri):
    """Conturile din balanta care nu sunt in planul firmei intra in el.

    Ecranul promite: "conturile analitice (clienti, furnizori) intra automat in plan",
    iar docstringul modulului la fel - dar importa() nu atingea deloc plan_conturi
    (dovedit 15.07.2026: grep plan_conturi in solduri_api = 0). Planul avea doar cele
    185 de conturi standard OMFP; o balanta cu analitice reale (4111.01 DEDEMAN,
    401.05 ORANGE - cum au toate cabinetele) lasa soldurile pe conturi inexistente
    in nomenclator.
    Tipul ramane 'Bifunctional' (implicitul tabelei): natura contului se deduce din
    simbol, nu o inventam aici. ON CONFLICT DO NOTHING - nu suprascriem denumirile
    din planul oficial cu cele din balanta.
    """
    conturi = []
    for r in (randuri or []):
        c = str(r.get("cont") or "").strip()
        if c:
            conturi.append((c, (str(r.get("denumire") or "").strip() or c)))
    if not conturi:
        return 0
    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO plan_conturi (simbol, denumire) VALUES (%s, %s) "
            "ON CONFLICT (simbol) DO NOTHING", conturi)
        return cur.rowcount


def data_balantei(v, azi=None):
    """[C22, comanda Costin 14.10.2026] Data la care sunt soldurile din balanță — CERUTĂ, nu dedusă. Din ea se propun data
    soldurilor inițiale și luna preluării (`luna_preluare`, `bilant_api.data_soldurilor`); fără ea, aplicația le deducea din
    data adăugării firmei sau din prima notă. `'YYYY-MM-DD'`; lipsă, neinterpretabilă sau în viitor -> `ValueError`."""
    import datetime as _dt
    t = str(v or "").strip()
    if not t:
        raise ValueError("Data balanței lipsește: scrie data la care sunt soldurile din fișier (de obicei ultima zi a lunii "
                         "dinaintea preluării). Din ea se stabilește luna de la care lucrezi în iConta.")
    try:
        d = _dt.date.fromisoformat(t[:10])
    except ValueError:
        raise ValueError("Data balanței „%s” nu se înțelege; se așteaptă o dată calendaristică." % t)
    if d > (azi or _dt.date.today()):
        raise ValueError("Data balanței (%s) e în viitor: soldurile se preiau la o dată încheiată." % _data_ro(d))
    return d.isoformat()


class BalantaExistenta(_mig.InlocuireNeconfirmata):
    """[deficiența 426] Firma are deja o balanță de deschidere, iar cererea n-a confirmat înlocuirea. `vechi` / `nou` = totalurile,
    `dependente` = notele de după data balanței. Forma balanței a refuzului comun al clasei (`migrare_api.InlocuireNeconfirmata`)."""


def note_dupa(cur, data_referinta):
    """[deficiența 426] Notele contabile de DUPĂ data balanței: `{numar, prima}` (prima = data celei mai vechi, 'YYYY-MM-DD'), sau
    `{numar: 0, prima: None}`. Soldurile lor se citesc peste balanța de deschidere (`bilant_api.sold_la`: soldurile de preluare + mișcările
    de după data lor), deci o balanță înlocuită le schimbă soldurile."""
    if not data_referinta:
        return {"numar": 0, "prima": None}
    cur.execute("SELECT count(*), min(data) FROM inregistrari WHERE data > %s", (str(data_referinta)[:10],))
    n, prima = cur.fetchone()
    return {"numar": int(n or 0), "prima": prima.isoformat() if prima else None}


def text_inlocuire(vechi, nou, note, data_noua=None):
    """[deficiența 426] „spune că există deja o balanță, arată totalurile vechi și noi […]; dacă există note pe lunile de după preluare,
    spune că soldurile lor se recalculează.” Textul comun avertismentului din previzualizare și refuzului de la salvare."""
    t = ("Firma are deja o balanță de deschidere%s: %s, debit %s, credit %s. Balanța nouă%s: %s, debit %s, credit %s. "
         "Salvarea o înlocuiește pe cea veche." % (
             (" la %s" % _data_ro(vechi["data_referinta"])) if vechi.get("data_referinta") else "",
             _cate(vechi["randuri"], "cont", "conturi"), _bani(vechi["total_debit"], "lei"), _bani(vechi["total_credit"], "lei"),
             (" la %s" % _data_ro(data_noua)) if data_noua else "", _cate(nou["randuri"], "cont", "conturi"),
             _bani(nou["total_debit"], "lei"), _bani(nou["total_credit"], "lei")))
    if note and note.get("numar"):
        t += (" Firma are %s după data balanței (prima la %s): soldurile lor se recalculează pe balanța nouă." % (
            "o notă contabilă" if note["numar"] == 1 else _cate(note["numar"], "notă contabilă", "note contabile"),
            _data_ro(note.get("prima")) or "—"))
    return t


def importa(conn, randuri, data_referinta=None, inlocuieste=False):
    """Scrie soldurile de preluare (DELETE + INSERT). Întoarce {randuri, total_debit, total_credit, rulaje, avertisment_rulaje,
    inlocuita, note_dupa}. Ridica ValueError daca balanta nu se echilibreaza.

    REFUZ dovedit necesar 15.07.2026, prin migrare reala: ecranul afisa "neechilibrat"
    rosu, dar importa() scria oricum, iar migrarea marca stratul "gata" verde. Firma
    ramanea cu o balanta de deschidere imposibila si contabilul credea ca e in regula.
    Semnalarea fara oprire e mai rea decat tacerea: da impresia ca produsul a verificat.

    [deficiența 426] „al doilea import de balanță pentru aceeași firmă o înlocuiește pe prima fără avertisment” — o balanță existentă se
    înlocuiește NUMAI cu `inlocuieste=True` (confirmarea de pe ecran); fără ea -> `BalantaExistenta`, cu totalurile vechi și noi.
    [deficiența 425] soldurile inițiale ale anului și rulajele (`si_*`, `rulaj_*`) se scriu când balanța le are (`verifica_rulaje`).
    """
    # REFUZUL E PRIMA POARTA: nimic nu se scrie dintr-o balanta respinsa. Pusesem
    # _adauga_conturi_lipsa inaintea verificarii - conturile intrau in plan chiar si
    # cand importul era refuzat. Prins de test (15.07.2026), nu de mine.
    vok, vmotiv = balanta_valida(randuri)
    if not vok:
        raise ValueError(vmotiv)
    dubluri = conturi_dublate(randuri)   # [lotul 10, C73] înaintea scrierii: refuzul numit, nu `UniqueViolation` -> 500
    if dubluri:
        raise ValueError(MESAJ_CONT_DUBLAT % ", ".join(dubluri[:8]))
    ok, td_v, tc_v, dif = verifica_echilibru(randuri)
    if not ok:
        raise ValueError(
            "Balanța nu se echilibrează: debit %s, credit %s "
            "(diferență %s). O balanță de deschidere trebuie să aibă totalul "
            "debitor egal cu cel creditor — altfel toată contabilitatea firmei "
            "pornește greșit." % (_bani(td_v, "lei"), _bani(tc_v, "lei"), _bani(dif, "lei")))
    cu_rulaje = verifica_rulaje(randuri)                 # [425] ecuația pe fiecare cont + echilibrul coloanelor
    data_referinta = data_balantei(data_referinta)       # [C22] cerută, după validitate și echilibru
    asigura_tabel(conn)
    vechi = rezumat(conn)
    nou = {"randuri": len(randuri), "total_debit": td_v, "total_credit": tc_v}
    with conn.cursor() as cur:
        note = note_dupa(cur, data_referinta)
    _mig.cere_confirmarea_inlocuirii(vechi["are_solduri"], inlocuieste, text_inlocuire(vechi, nou, note, data_referinta),
                                     vechi, nou, note, exceptie=BalantaExistenta)   # [426] poarta comună a clasei
    _adauga_conturi_lipsa(conn, randuri)
    td = tc = 0.0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM solduri_initiale")
        with _chei.refuza_dublura(cur, ("solduri_initiale_cont_uniq",), _refuz_cont_scris_intre_timp):
            for r in randuri:
                cur.execute(
                    "INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta, "
                    "si_an_debit, si_an_credit, rulaj_an_debit, rulaj_an_credit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (r["cont"], r.get("denumire", ""), r.get("debit", 0), r.get("credit", 0), data_referinta,
                     *((r.get(k) for k in CHEI_RULAJE) if cu_rulaje else (None,) * 4)))
                td += float(r.get("debit", 0) or 0)
                tc += float(r.get("credit", 0) or 0)
    return {"randuri": len(randuri), "total_debit": round(td, 2), "total_credit": round(tc, 2),  # round-ok: sumă / diferență de valori care au deja bani: curăță zgomotul float, nu întâlnește ,xx5
            "rulaje": cu_rulaje, "avertisment_rulaje": None if cu_rulaje else avertisment_fara_rulaje(data_referinta),
            "inlocuita": vechi if vechi["are_solduri"] else None, "note_dupa": note}


def rezumat(conn):
    """{are_solduri, randuri, total_debit, total_credit, data_referinta, rulaje} pentru firma curentă. [426] data balanței și dacă are
    rulajele anului: avertismentul de înlocuire le arată."""
    asigura_tabel(conn)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), COALESCE(sum(sold_debitor),0), COALESCE(sum(sold_creditor),0), max(data_referinta), "
                    "count(rulaj_an_debit) FROM solduri_initiale")
        n, td, tc, dr, nr = cur.fetchone()
    return {"are_solduri": n > 0, "randuri": n, "total_debit": float(td), "total_credit": float(tc),
            "data_referinta": dr.isoformat() if dr else None, "rulaje": bool(nr)}


def solduri_deschidere(cur):
    """[359 / 374, comanda Costin 8.2] Balanța de deschidere a firmei: {cont: (sold debitor, sold creditor)} — reconcilierea registrelor
    preluate (mijloace fixe, stoc) cu ea. Conexiunea e pe schema firmei."""
    cur.execute("SELECT cont, sold_debitor, sold_creditor FROM solduri_initiale")
    return {(r["cont"] if isinstance(r, dict) else r[0]): ((r["sold_debitor"], r["sold_creditor"]) if isinstance(r, dict) else (r[1], r[2]))
            for r in cur.fetchall()}
