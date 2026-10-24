# -*- coding: utf-8 -*-
"""GARD — [lotul 12, C140, găsită de Code la 485] săgeata înapoi = UN pas înapoi, întâi în ecran.

Defectul: în `static/js/navigator.js` ordinea la „←” era pas pe traseu -> fereastră (stiva > 1) -> `nav.setInapoi(fn)`, deci pasul intern
declarat de ecran nu se atingea niciodată pe a doua fereastră sau într-un pas: „←” din editorul de șablon (Contracte) închidea fereastra
Contracte, „←” din lista de CUI-uri verificate (Migrare cabinet -> Firme) sărea peste lista lipită, iar din previzualizarea unui import
(Solduri, Parteneri, ...) sărea peste alegerea fișierului. Regula: DESIGN_SYSTEM.md cap.3 — „Săgeata portocalie duce MEREU exact un pas
înapoi în ierarhia ecranului. Mecanismul: `nav.setInapoi(fn)` — obligatoriu apelat la începutul FIECĂRUI sub-ecran: rădăcina cu
undefined/null, sub-ecranele cu funcția părinte.” Temei fiscal: N/A — regulă de produs (DS cap.3).

CE FACE IMPOSIBIL
  1. (navigator) o ordine în care pasul intern al ecranului vine după traseu / fereastră; un pas intern folosit de două ori (nu se consumă
     înainte de chemare); un pas intern vechi rămas peste un ecran redesenat de la început; `inapoiPas` (ieșirea după o acțiune reușită) sau
     X care iau pasul intern; logica de întoarcere la un pas dublată în mai multe locuri;
  2. (clasa, toate ecranele din `static/js`) un `setInapoi` care declară ca pas intern ecranul ALTEI ferestre sau al altui pas — tocmai ce
     făcea ordinea veche să pară necesară („antetul acumula ferestre / pași”, fir_pop_v1): cu pasul intern întâi, `setInapoi(() =>
     meniuMigrare(...))` din fereastra „Solduri inițiale” ar desena meniul Migrare cabinet ÎN ea. Ecranul unei ferestre / al unui pas e
     funcția dată lui `nav.deschide` / `nav.mergi` (sau unui `fn:` / `peFirma:` care ajunge acolo), plus ce desenează ea pe loc
     (apeluri `f(corp, …)`); un `setInapoi(F)` din funcția S e permis numai dacă S și F sunt ecrane ale ACELEIAȘI ferestre / aceluiași pas.

CE NU VEDE (declarat): citește sursa, nu rulează browserul (comportamentul îl probează e2e `frontend_test/e2e/e2e_lot12_inapoi.py`);
leagă numai funcțiile declarate la coloana 0 ale aceluiași fișier, iar „pe loc” înseamnă un apel cu `corp` ca prim argument, pe un rând
fără `nav.deschide(` / `nav.mergi(` / `setInapoi(` înaintea lui; o funcție locală (închidere) e permisă ca țintă — e ecranul aceleiași
ferestre, cum sunt editorul și lista din Contracte."""
import os
import re

from core import arbore_js as _aj

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(RAD, "static", "js")
NAV = os.path.join(JS, "navigator.js")


def _citeste(cale):
    with open(cale, encoding="utf-8") as f:
        return f.read()


def _surse(rad=JS):
    out = {}
    for d, _, fs in os.walk(rad):
        for f in fs:
            if f.endswith(".js"):
                out[os.path.relpath(os.path.join(d, f), RAD)] = _citeste(os.path.join(d, f))
    return out


def _functii(s):
    """(nume, început, sfârșit) — funcțiile declarate la nivelul modulului (coloana 0)."""
    poz = [(m.group(1), m.start()) for m in re.finditer(r"^(?:export )?(?:async )?function ([\w$]+)\(", s, re.M)]
    return [(n, a, poz[i + 1][1] if i + 1 < len(poz) else len(s)) for i, (n, a) in enumerate(poz)]


_TAIE = re.compile(r"nav\.deschide\(|\.mergi\(|setInapoi\(")


def tinte_ferestre(surse):
    """Numele funcțiilor care desenează o fereastră sau un pas: cele chemate din callback-ul lui `nav.deschide` / `nav.mergi`, plus cele din
    callback-urile de obiect (`fn: (c, n) => importSolduriFirma(…)`, `peFirma: …`) pe care ecranele le dau mai departe acelorași două."""
    tinte = set()
    for s in surse.values():
        for rand in s.splitlines():
            m = re.search(r"nav\.deschide\(|nav\.mergi\(", rand)
            if m:
                tinte.update(re.findall(r"=>\s*\{?\s*(?:[\w$]+\.)?([\w$]+)\(", rand[m.start():]))
        tinte.update(re.findall(r"\b[\w$]+\s*:\s*\([^)]*\)\s*=>\s*([\w$]+)\(", s))
    return tinte


def _pe_loc(corp):
    """Funcțiile chemate PE LOC dintr-un corp de funcție: `f(corp, …)`, înaintea unui `nav.deschide(` / `nav.mergi(` / `setInapoi(`."""
    out = set()
    for rand in corp.splitlines():
        m = _TAIE.search(rand)
        out.update(re.findall(r"(?<![\w$.])([\w$]+)\(\s*corp\s*[,)]", rand[:m.start()] if m else rand))
    return out


def incalcari(surse):
    """Lista `fișier:rând S -> F` a `setInapoi`-urilor care declară ca pas intern ecranul altei ferestre / altui pas; plus (al doilea
    element) câte `setInapoi` cu țintă funcție de modul au fost verificate (anti-vacuu)."""
    tinte = tinte_ferestre(surse)
    viol, verificate = [], 0
    for fisier, s in sorted(surse.items()):
        fm = _functii(s)
        nume = {n for n, _, _ in fm}
        corpuri = {n: s[a:b] for n, a, b in fm}
        apeluri = {n: _pe_loc(c) & nume for n, c in corpuri.items()}

        def fereastra(t):
            w, coada = {t}, [t]
            while coada:
                for g in apeluri.get(coada.pop(), ()):
                    if g not in w:
                        w.add(g)
                        coada.append(g)
            return w

        ferestre = [fereastra(t) for t in tinte & nume]
        for m in re.finditer(r"setInapoi\(\s*(?:\(\)\s*=>\s*\{?\s*)?([\w$.]+)", s):
            f = m.group(1)
            if f not in nume:
                continue     # undefined / null / nav.reiaPasul / opt.inapoi / funcție locală (aceeași fereastră)
            sus = next((n for n, a, b in fm if a <= m.start() < b), None)
            if sus and re.search(r"^\s+(?:async\s+)?function\s+%s\(|\b(?:const|let)\s+%s\s*=" % (re.escape(f), re.escape(f)),
                                 corpuri[sus], re.M):
                continue     # numele e al unei funcții locale din același ecran
            verificate += 1
            if not sus or not any(sus in w and f in w for w in ferestre):
                viol.append("%s:%d %s -> %s" % (fisier, s.count("\n", 0, m.start()) + 1, sus, f))
    return viol, verificate


# ── 1. navigatorul ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _bucata(s, inceput, sfarsit):
    i = s.index(inceput)
    return s[i:s.index(sfarsit, i)]


def test_sageata_ia_intai_pasul_intern_o_singura_data():
    """DS cap.3: „←” = un pas înapoi în ierarhia ECRANULUI — întâi pasul declarat de ecran, consumat înainte de chemare (o singură dată),
    apoi traseul, apoi fereastra."""
    s = _citeste(NAV)
    h = _bucata(s, 'bInapoi.addEventListener("click"', "\n    }\n")
    i_intern = h.index('typeof sus.inapoi === "function"')
    assert i_intern < h.index("sus.pasi && sus.pasi.length") < h.index("nav.inapoi()"), h
    assert re.search(r"const (\w+) = sus\.inapoi;\s*sus\.inapoi = null;\s*\1\(\)", h), "pasul intern nu se consumă înainte de chemare:\n" + h


def test_ecranul_desenat_de_la_inceput_porneste_fara_pas_intern():
    """Un `setInapoi` vechi nu rămâne peste un ecran redesenat (pas scos, fereastră de dedesubt, firma în lucru schimbată): se șterge
    înaintea desenării, numai când elementul nu e păstrat (pct.1b); pasul păstrat își primește înapoi pasul intern (`_laPas`, `mergi`)."""
    s = _citeste(NAV)
    # pe NOD (`core/arbore_js.py`): condiția cu ramura ei, atribuirea cu valoarea ei — nu șirul căutat în sursă (`core/test_garzi_pe_text.py`)
    arb, cod = _aj.arbore_js(NAV)
    r = _aj.functia(arb, "randeazaFerestre")
    sterge = [i for i in _aj.noduri(r, "IfStatement") if (cod(i["test"]), cod(i["consequent"])) == ("!pastrat", "sus.inapoi = null;")]
    assert len(sterge) == 1, "un pas intern vechi rămâne peste ecranul redesenat de la început"
    deseneaza = [c for c in _aj.noduri(r, "CallExpression") if cod(c["callee"]) == "sus.curent || sus.randator"]
    assert [[cod(a) for a in c["arguments"]] for c in deseneaza] == [['fer.querySelector(".fereastra-corp")', "nav"]], deseneaza
    assert sterge[0]["end"] < deseneaza[0]["start"], "pasul intern vechi se șterge abia după desenare"
    assert [cod(a["right"]) for a in _aj.noduri(_aj.functia(arb, "_laPas"), "AssignmentExpression")
            if cod(a["left"]) == "sus.inapoi"] == ["p.inapoi || null"]
    assert re.search(r"sus\.pasi\.push\(\{[\s\S]*?\binapoi: p \? sus\.inapoi : null \}\)", _bucata(s, "mergi(titlu, fn) {", "setInapoi(fn) {"))


def test_inapoipas_si_x_nu_iau_pasul_intern_iar_intoarcerea_la_pas_e_intr_un_singur_loc():
    """`inapoiPas` = ieșirea din pas după o acțiune reușită; X = închide fereastra (deficiența 4). Niciunul nu cheamă pasul intern. Întoarcerea
    la un pas de pe traseu are un singur loc (`_laPas`), folosit de săgeată, fir și `inapoiPas`."""
    s = _citeste(NAV)
    assert "sus.inapoi" not in _bucata(s, "inapoiPas() {", "reiaPasul() {")
    arb, cod = _aj.arbore_js(NAV)
    x = [c for c in _aj.noduri(arb, "CallExpression") if cod(c["callee"]) == 'fer.querySelector(".nav-x").addEventListener']
    assert [cod(c["arguments"][0]) for c in x] == ['"click"'], [cod(c) for c in x]
    pe_x = x[0]["arguments"][1]
    assert not [m for m in _aj.noduri(pe_x, "MemberExpression") if cod(m) == "sus.inapoi"], cod(pe_x)
    assert _aj.apeluri(pe_x, cod, "nav.acasa") == [()], cod(pe_x)
    apeluri = re.findall(r"(?<!function )_laPas\(sus, ", s)
    assert "sus.pasi.pop()" not in s and len(apeluri) == 3, len(apeluri)


# ── 2. clasa: niciun ecran nu-și declară ca pas intern ecranul altei ferestre ────────────────────────────────────────────────────
def test_niciun_setinapoi_nu_trimite_in_ecranul_altei_ferestre():
    viol, verificate = incalcari(_surse())
    assert verificate >= 1, "garda n-a verificat niciun setInapoi cu țintă funcție de modul — s-a stricat citirea?"
    assert not viol, "setInapoi spre ecranul altei ferestre / altui pas (ar fi desenat în fereastra de acum):\n" + "\n".join(viol)


def test_ANTI_VACUU_garda_vede_clasa_si_lasa_pasul_intern():
    """Sintetic: fereastra A (`ecranA`) și fereastra B (`ecranB`, deschisă din A); B își declară ca pas intern ecranul lui A -> prins;
    pasul intern al lui B (`pasB2`, desenat pe loc din B) -> permis; o funcție locală -> permisă."""
    sursa = (
        'function ecranA(corp, nav) {\n  nav.setInapoi(undefined);\n'
        '  b.addEventListener("click", () => nav.deschide("B", (cc, nn) => ecranB(cc, nn)));\n}\n'
        'function ecranB(corp, nav) {\n  nav.setInapoi(() => ecranA(corp, nav));\n  pasB1(corp, nav);\n}\n'
        'function pasB1(corp, nav) {\n  x.onclick = () => pasB2(corp, nav, 1);\n}\n'
        'function pasB2(corp, nav, r) {\n  nav.setInapoi(() => pasB1(corp, nav));\n}\n'
        'async function ecranC(corp, nav) {\n  function lista() { nav.setInapoi(undefined); }\n'
        '  function editor() { nav.setInapoi(lista); }\n}\n'
        'm.onclick = () => nav.mergi("C", (c) => ecranC(c, nav));\n')
    viol, verificate = incalcari({"sintetic.js": sursa})
    assert viol == ["sintetic.js:6 ecranB -> ecranA"], viol
    assert verificate == 2
    # ecranele reale: perechile cunoscute, legitime, se văd (pasul intern din Migrare cabinet -> Firme)
    surse = _surse()
    m = surse[os.path.join("static", "js", "ecrane", "migrare.js")]
    assert {"pasInput"} <= _pe_loc(dict((n, m[a:b]) for n, a, b in _functii(m))["wizardFirme"])
    assert {"wizardSolduri", "importSolduriFirma", "meniuMigrarePerFirma", "randeazaMigrare", "ecranContracte"} <= tinte_ferestre(surse)
