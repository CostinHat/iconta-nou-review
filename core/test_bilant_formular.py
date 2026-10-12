# -*- coding: utf-8 -*-
"""GARD — generatoarele bilanțului urmează FORMULARUL ANAF 2025 rând cu rând (C12, C13, deficiența 233; 12.10.2026).

SURSA: formularul oficial 2025 („soft A”, `anaf_surse/bilant_SC_1225_XML_270326.pdf`), citit în șablonul XFA de
`scripts/extrage_denumiri_bilant.sablon_formular`: fiecare rând își tipărește lista de conturi („(ct. 201 + 203 … − 4904)”), iar fiecare total
își are calculul în `<calculate>`.

CE ERA (C12, C13): F10 nu avea 436 — CAM-ul de plată la 31.12 —, deci bilanțul ORICĂREI firme cu salariați era respins de DUK (regula
F10_64: „F10_0492 (500) = … (1000)”); nici 467, 4901–4904, 463. F20 S1005 punea 603–608 la rd.03 (formularul: rd.06), număra de două ori
reluările de ajustări (754, 7812–7814, 786 — în „alte venituri” și scăzute din rd.05), pierdea 794 (rd.07a) și calcula profitul din
venituri − cheltuieli, nu din rândurile pe care le depune. Lista era scrisă din memorie; acum e transcrisă din formular și comparată cu el.

CE FACE IMPOSIBIL: un cont al formularului lipsă din generator (sau unul în plus), fără o abatere numită cu motivul ei; un total calculat
altfel decât în formular; un sold / rulaj care nu ajunge pe niciun rând fără ca generarea să se oprească.
"""
import io
import os
import re
import sys
from decimal import Decimal

import pytest

from core import bilant as b

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_RAD, "scripts"))
import extrage_denumiri_bilant as ex  # noqa: E402


@pytest.fixture(scope="module")
def sablon():
    return ex.sablon_formular()


def _fmt(t):
    semn, cont, cal = t
    if cal == "+/-":
        return "+/-" + cont
    return semn + ("din" if "din" in cal else "") + cont + cal.replace("din", "")


def _din_formular(sablon, tabel):
    """{rând: [termenii tipăriți]} pentru rândurile formularului care își tipăresc lista de conturi."""
    return {r: [_fmt(t) for t in b.termeni_din_denumire(text)] for r, _cod, text, _a in ex.randuri_tabel(sablon, tabel)
            if b.termeni_din_denumire(text)}


def _asteptat(sectiune, tip, rand, termeni_formular):
    """Termenii pe care generatorul trebuie să-i aibă pe rând: cei din formular, cu abaterile numite (`NOMENCLATOR_ABATERI_FORMULAR`)."""
    ab = b.NOMENCLATOR_ABATERI_FORMULAR.get((sectiune, tip, rand))
    if isinstance(ab, str):                       # rândul întreg stă pe alt rând (motivul e în tabel)
        return None
    out = []
    for t in termeni_formular:
        if ab and t in ab:
            inlocuire = ab[t]
            if inlocuire and inlocuire[:1] in "+-":
                out += [_fmt(x) for x in b.termeni(inlocuire)]
        else:
            out.append(t)
    return sorted(out) or None


def _nomenclator(nomenclator):
    return {r: sorted(_fmt(t) for t in b.termeni(lista)) for r, _lat, lista in nomenclator}


@pytest.mark.parametrize("sectiune,tip,tabel,nomenclator", [
    ("F10", "*", "F10S", lambda: b.F10_NOMENCLATOR),
    ("F20", "s1005", "F20S", lambda: b.F20_S1005_NOMENCLATOR + b.F20_S1005_NOMENCLATOR_DIN_CARE),
    ("F30", "s1005", ex.TABEL_F30_CAP_XIX, lambda: b.F30_S1005_NOMENCLATOR + b.F30_S1005_NOMENCLATOR_DIN_CARE),   # C14
])
def test_listele_de_conturi_sunt_ale_formularului(sablon, sectiune, tip, tabel, nomenclator):
    """Fiecare rând al generatorului = conturile tipărite pe rândul formularului, cu abaterile numite. Totalurile își tipăresc și ele
    conturile (rd.10 „(ct. 471)”), dar se calculează din rânduri. MUTAȚII: 436 scos din rd.13 -> pică; 266 adăugat la rd.03 -> pică;
    603 mutat înapoi la rd.03 (S1005) -> pică; F30 cap.XIX: 612 readus la rd.198 -> pică (C14)."""
    form = _din_formular(sablon, tabel)
    gen = _nomenclator(nomenclator())
    totaluri = b.NOMENCLATOR_TOTALURI["s1005"][sectiune]
    for r, termeni in form.items():
        if r in totaluri:
            continue
        asteptat = _asteptat(sectiune, tip, r, termeni)
        assert gen.get(r) == asteptat, (sectiune, tip, r, "formular:", termeni, "generator:", gen.get(r))
    assert set(gen) <= set(form), ("rânduri ale generatorului fără listă pe formular", sorted(set(gen) - set(form)))


def test_listele_f20_s1003_sunt_ale_formularului(sablon):
    """F20 S1003 (C10): conturile fiecărui rând = cele tipărite pe formular. Abaterile sunt deciziile Costin 12.10.2026 (6811 numai la
    25a; „din ct. 6818 / 7818” la b)) și rândurile „=null” (5, 38, 67), numite în `NOMENCLATOR_ABATERI_FORMULAR`."""
    form = _din_formular(sablon, "F20")
    gen = {r: sorted("+" + p for p in pref) for r, _lat, pref in b.F20_S1003_NOMENCLATOR + b.F20_S1003_NOMENCLATOR_DIN_CARE}
    for r, termeni in form.items():
        if r in b.NOMENCLATOR_TOTALURI["s1003"]["F20"]:
            continue
        asteptat = _asteptat("F20", "s1003", r, [t.replace("din", "").replace("*", "") for t in termeni])
        if asteptat is None:
            assert r not in gen, r
            continue
        assert gen.get(r) == asteptat, (r, "formular:", termeni, "generator:", gen.get(r))


# ── totalurile ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _calcul(script):
    """`<calculate>` al unui total -> (termeni „+1+2-3”, pozitiv) sau None. Formele din formular: „this=R01.C1+R02.C1;”,
    „this.rawValue = R30.C1.rawValue + …;”, „var v1 = <expr>; if (v1 > 0) this.rawValue = v1; else 0” (pozitiv)."""
    s = "\n".join(re.sub(r"//.*$", "", ln) for ln in script.replace("&gt;", ">").splitlines())
    s = re.sub(r"\.rawValue|\.C1|\s", "", s)
    m = re.search(r"varv1=(.+?);if\(v1>0\)", s)
    poz = bool(m)
    expr = m.group(1) if m else (re.search(r"this=([^;]+);", s) or [None, None])[1]
    if not expr or expr == "null" or not re.search(r"R\d+", expr):
        return None
    termeni, stiva, semn = [], [1], 1
    for tok in re.findall(r"R\d+|[-+()]", expr):
        if tok == "-":
            semn = -1
        elif tok == "+":
            semn = 1
        elif tok == "(":
            stiva.append(stiva[-1] * semn)
            semn = 1
        elif tok == ")":
            stiva.pop()
        else:
            termeni.append((stiva[-1] * semn, int(tok[1:])))
            semn = 1
    return "".join("%s%d" % ("+" if s > 0 else "-", r) for s, r in termeni), poz


def _calcule(sablon, tabel):
    bloc = ex.bloc_tabel(sablon, tabel)
    randuri = [(m.start(), int(m.group(1))) for m in re.finditer(r'<subform\b[^>]*\bname="R(\d+)"', bloc)]
    out = {}
    for k, (p, r) in enumerate(randuri):
        seg = bloc[p:randuri[k + 1][0] if k + 1 < len(randuri) else len(bloc)]
        c1 = re.search(r'<field\b[^>]*name="C1".*?</field\s*>', seg, re.S)
        sc = re.search(r"<calculate\b[^>]*>\s*<script[^>]*>(.*?)</script", c1.group(0), re.S) if c1 else None
        f = _calcul(sc.group(1)) if sc else None
        if f:
            out[r] = f
    return out


@pytest.mark.parametrize("tip,sectiune,tabel", [("s1005", "F10", "F10S"), ("s1005", "F20", "F20S"), ("s1003", "F20", "F20"),
                                                 ("s1003", "F10", "F10S"), ("s1005", "F30", ex.TABEL_F30_CAP_XIX)])
def test_totalurile_sunt_calculele_formularului(sablon, tip, sectiune, tabel):
    """`NOMENCLATOR_TOTALURI` = calculele formularului, rând cu rând (termeni și „numai dacă e pozitiv”). Singura excepție: S1003 rd.01
    — formularul calculează „v1 = R02 + R03 − R04 + R06” dar nu-l atribuie (linie comentată); formula e cea din denumire, „(rd. 02 + 03 −
    04 + 06)”. MUTAȚII: rd.14 fără „− 26” -> pică; rd.44 fără „pozitiv” -> pică."""
    calc = _calcule(sablon, tabel)
    nule = {r for (s, ti, r), v in b.NOMENCLATOR_ABATERI_FORMULAR.items() if (s, ti) == (sectiune, tip) and v == "=null"}
    # [C14] un rând „=null” (nescris) nu intră în totaluri: F30 rd.167 = 168 + 169 − 170 (+ 171 =null) + 172; rd.197 (+ 204 =null)
    calc = {r: ("".join(x for x in re.findall(r"[+-]\d+", e) if int(x[1:]) not in nule), p) for r, (e, p) in calc.items()}
    canon = lambda e: "".join(sorted(re.findall(r"[+-]\d+", e)))   # noqa: E731  (ordinea termenilor nu contează)
    calc = {r: (canon(e), p) for r, (e, p) in calc.items()}
    tot = {r: (canon(e), p) for r, (e, p) in b.NOMENCLATOR_TOTALURI[tip][sectiune].items()}
    if (tip, sectiune) == ("s1003", "F20"):
        assert 1 not in calc and tot.pop(1) == (canon("+2+3-4+6"), False)
        den = dict((r, t) for r, _c, t, _a in ex.randuri_tabel(sablon, tabel))[1]
        assert re.sub(r"\s", "", den).endswith("(rd.02+03-04+06)"), den
    assert tot == calc, {r: (tot.get(r), calc.get(r)) for r in set(tot) | set(calc) if tot.get(r) != calc.get(r)}


def test_cu_totaluri_calculeaza_si_totalurile_din_totaluri():
    """rd.15 = rd.04 + 12 + 14, iar rd.04 și rd.14 sunt și ele totaluri: se calculează în ordinea dependențelor; profitul / pierderea se
    exclud reciproc. MUTAȚIE: „pozitiv” ignorat -> rd.09 negativ -> pică."""
    v = b.cu_totaluri("s1005", "F10", {1: 10, 2: 20, 3: 5, 5: 7, 301: 3, 302: 0, 7: 1, 8: 9, 11: 2, 12: 0, 13: 4, 20: 0, 23: 1, 26: 0})
    assert (v[4], v[6], v[9], v[14], v[15]) == (35, 3, 20, 17, 52), v
    f20 = b.cu_totaluri("s1005", "F20", {1: 100, 2: 0, 3: 30, 4: 10, 5: 0, 6: 5, 7: 1, 304: 0})
    assert (f20[8], f20[9]) == (54, 0), f20
    f20 = b.cu_totaluri("s1005", "F20", {1: 10, 2: 0, 3: 30, 4: 0, 5: 0, 6: 0, 7: 0, 304: 0})
    assert (f20[8], f20[9]) == (0, 20), f20


# ── F20 S1005 pe tot planul ──────────────────────────────────────────────────────────────────────────────────────────────────────────
def _plan(clase):
    t = io.open(os.path.join(_RAD, "anaf_surse", "omfp_1802_2014.txt"), encoding="utf-8").read()
    seg = t[t.index("Clasa %s" % clase[0]):t.index("Clasa 8", t.index("Clasa 6"))] if clase == "67" else \
        t[t.index("Clasa 1"):t.index("Clasa 6", t.index("Clasa 1"))]
    pl = sorted(set(re.findall(r"(?<![\d.])([%s]\d{2,4})\. [A-ZȘȚĂÎÂ]" % clase, seg)))
    return pl, [c for c in pl if not any(o != c and o.startswith(c) for o in pl)]


def test_f20_s1005_fiecare_cont_are_un_rand_si_rezultatul_e_cel_din_rulaje():
    """Pe un rulaj pe TOT planul (o sumă distinctă pe fiecare frunză de clasa 6/7, fără 695 — „=null” și pe formular): profitul −
    pierderea (rd.08 − rd.09) = veniturile − cheltuielile din rulaje (709 scade veniturile, 609 cheltuielile, 711/712 pe sold) — un cont
    pierdut sau numărat de două ori strică egalitatea. MUTAȚII: 7812 scos din rd.05 -> pică; 754 adăugat și la rd.02 -> pică."""
    plan, frunze = _plan("67")
    assert len(plan) > 150, len(plan)
    fara = [c for c in frunze if b.rand_f20_s1005(c) is None]
    assert fara == ["695"], fara
    rl = {}
    for i, c in enumerate(frunze, start=1):
        if c == "695":
            continue
        s = Decimal(100 + i)
        rl[c] = (s, Decimal(0)) if (c[0] == "6" and c != "609") or c == "709" else (Decimal(0), s)
    rl["711"], rl["712"] = (Decimal(30), Decimal(130)), (Decimal(50), Decimal(50))
    ven = (sum(c for k, (d, c) in rl.items() if k[0] == "7" and k not in ("709", "711", "712")) - rl["709"][0]
           + sum(rl[k][1] - rl[k][0] for k in ("711", "712")))
    che = sum(d for k, (d, c) in rl.items() if k[0] == "6" and k != "609") - rl["609"][1]
    r = b.f20_din_rulaje(rl)
    assert r[8] - r[9] == int(ven - che), (r[8], r[9], ven, che)
    assert r[8] - r[9] == r[1] + r[2] - r[3] - r[4] - r[5] - r[6] - r[7] + r[304] and min(r[8], r[9]) == 0   # din rândurile depuse
    # [C14] F30 cap.XIX: fiecare frunză are un rând, iar rândurile pe care DUK le compară cu F20 dau aceleași cifre (regulile F20_F30_1–10)
    assert [c for c in frunze if b.rand_f30_s1005(c) is None] == ["695"]
    f30 = b.f30_din_rulaje(rl)
    assert b.neconcordante_f20_f30(r, f30) == [], b.neconcordante_f20_f30(r, f30)
    assert min(f30[235], f30[236]) == 0 and f30[235] - f30[236] == r[8] - r[9]


def test_f20_s1005_sinteticele_cu_analitice_pe_randuri_diferite_opresc_generarea():
    """Ca la S1003 (decizia Costin 12.10.2026, „nu ghicim rândul”, reconfirmată seara pentru 741): tabelul = sinteticele planului ale căror
    analitice cad pe rânduri diferite ale S1005 — F20 sau F30 cap.XIX (C14: cap.XIX desparte și 658, 681, 761); un rulaj pe ele oprește
    generarea cu analiticele cerute, pe rândurile cap.XIX. MUTAȚIE: 781 scos din tabel -> pică; 658 scos -> pică."""
    plan, frunze = _plan("67")
    calc = {}
    for s in plan:
        an = [c for c in frunze if c != s and c.startswith(s)]
        rand = {(b.rand_f20_s1005(c), b.rand_f30_s1005(c)) for c in an}
        if len(rand) > 1:
            calc[s] = tuple((c, b.rand_f30_s1005(c)) for c in an)
    assert b.S1005_NOMENCLATOR_SINTETICE == calc, calc
    with pytest.raises(ValueError, match=r"contul 741 e folosit sintetic.*7411 \(F30 rd\.172\)"):
        b.f20_din_rulaje({"704": (0, 10), "741": (0, 800)})
    with pytest.raises(ValueError, match=r"contul 695 nu are rând"):
        b.f20_din_rulaje({"695": (5, 0)})


# ── F10 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_f10_cam_de_plata_436_e_datorie_si_bilantul_e_egal():
    """C12: 436 cu sold creditor (CAM-ul lui decembrie, de plată) -> rd.13; bilanțul e egal (rd.49 = rd.04 + 09 + 10 − 13 − 16 − 17 − 18,
    corelația dublă a formularului, DUK regula F10_64). Înainte: rd.13 = 0, rd.49 = 500 ≠ 1000. MUTAȚIE: 436*** scos din rd.13 -> pică."""
    s = {"5121": (Decimal(1000), Decimal(0)), "1012": (Decimal(0), Decimal(500)), "436": (Decimal(0), Decimal(500))}
    r = b.f10_din_balanta(s)
    assert (r[13], r[46], r[49]) == (500, 500, 500), r
    assert r[49] == r[4] + r[9] + r[10] - r[13] - r[16] - r[17] - r[18]


def test_def_238_soldul_fara_rand_opreste_generarea_cu_un_rand_pe_cont_pentru_contabil():
    """238 (retestul Costin 12.10.2026): „Rescrie-l pentru contabil, câte un rând pe cont, cu suma și acțiunea concretă, fără coduri DUK.
    Exemple: «401 sold debitor 500,00 — reclasifică în 409 (furnizori-debitori)»; «4427 sold creditor 1.050,00 — închide TVA-ul lunii în
    4423»; «581 sold creditor 1.000,00 — viramentele interne trebuie să aibă sold zero».” Cazul firmei F2 din producție (read-only,
    12.10.2026). Un sold pe care bilanțul nu-l preia oprește generarea (bilanțul n-ar fi egal); mesajul are un rând pe cont, cu suma în
    formatul românesc, acțiunea și temeiul OMFP 1802/2014. MUTAȚII: acțiunea lui 401 scoasă (cade pe natura contului) -> pică; mesajul
    vechi (DUK regula F10_64, sume „500.00”) -> pică."""
    with pytest.raises(ValueError) as e:
        b.f10_din_balanta({"5121": (Decimal(1550), 0), "401": (Decimal(500), 0), "4427": (0, Decimal(1050)), "581": (0, Decimal(1000))})
    linii = str(e.value).split("\n")
    assert linii[0] == "Bilanțul nu se poate genera: soldurile de la 31.12 de mai jos nu au loc în bilanț. Corectează-le, apoi generează din nou."
    assert linii[1].startswith("• 401 sold debitor 500,00 — reclasifică în 409 (furnizori-debitori). OMFP 1802/2014, contul 409:"), linii
    assert linii[2].startswith("• 4427 sold creditor 1.050,00 — închide TVA-ul lunii: compensează-l cu 4426, iar diferența trece în 4423"), linii
    assert linii[3].startswith("• 581 sold creditor 1.000,00 — viramentele interne trebuie să aibă sold zero"), linii
    assert len(linii) == 4 and "DUK" not in str(e.value) and "F10" not in str(e.value), linii


def test_def_238_fiecare_sold_fara_loc_din_plan_are_o_actiune_concreta():
    """Pe TOT planul OMFP (clasele 1–5, fiecare frunză pe fiecare latură): orice sold pe care bilanțul nu-l preia primește o acțiune, fără
    coduri DUK, în română corectă (verificatorul de limbă al aplicației); cele 12 conturi fără niciun rând (1033, 1038, 107, 1081, 1082,
    264, 266, 4426, 4427, 481, 482, 581) au acțiunea lor anume, cu temeiul OMFP 1802/2014 — nu una după natura contului. MUTAȚIE: 266
    scos din `NOMENCLATOR_ACTIUNI_SOLD` -> pică."""
    from core import limba_ecran
    _p, frunze = _plan("12345")
    fara = []
    for lat in ("d", "c"):
        s = {c: ((Decimal(1), Decimal(0)) if lat == "d" else (Decimal(0), Decimal(1))) for c in frunze}
        fara += b.conturi_fara_rand(b.F10_NOMENCLATOR, s, "12345")
    rele = [ln for ln in b.motiv_f10(fara).split("\n") if limba_ecran.defecte(ln) or re.search(r"DUK| — \.", ln)]
    assert len(fara) > 250 and not rele, rele[:5]
    fara_rand = ["1033", "1038", "107", "1081", "1082", "264", "266", "4426", "4427", "481", "482", "581"]
    for c in fara_rand:
        act, temei = b.actiune_sold(c, "d")
        assert act not in b.NOMENCLATOR_ACTIUNI_SOLD_GRUPE.values() and temei.startswith("OMFP 1802/2014"), (c, act, temei)


def test_f10_pe_tot_planul_fiecare_sold_pe_latura_lui_are_rand():
    """Pe TOT planul OMFP (clasele 1–5, fiecare frunză cu soldul pe latura ei firească — activ debitor, pasiv creditor, bifuncționalele pe
    amândouă): singurele frunze fără rând sunt cele pe care formularul 2025 nu le cere în bilanțul prescurtat sau care la 31.12 trebuie să
    fie zero. Lista e fixată: un cont nou fără rând apare aici."""
    _plan_, frunze = _plan("12345")
    fara = set()
    for lat in ("d", "c"):
        s = {c: ((Decimal(1), Decimal(0)) if lat == "d" else (Decimal(0), Decimal(1))) for c in frunze}
        fara_lat = {c for c, _l, _v in b.conturi_fara_rand(b.F10_NOMENCLATOR, s, "12345")}
        fara |= {c for c in fara_lat if c in {x for x, _ll, _vv in b.conturi_fara_rand(b.F10_NOMENCLATOR,
                 {c2: ((Decimal(0), Decimal(1)) if lat == "d" else (Decimal(1), Decimal(0))) for c2 in frunze}, "12345")}}
    assert sorted(fara) == ["1033", "1038", "107", "1081", "1082", "264", "266", "4426", "4427", "481", "482", "581"], sorted(fara)
