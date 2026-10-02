# -*- coding: utf-8 -*-
"""GARD — o cheie pe care ecranul Declarații o trimite în `manual` trebuie să fie citită de generator (02.10.2026).

Clasa: o dată introdusă de contabil, trimisă de ecran, pe care generatorul n-o citește, DISPARE tăcut din declarație —
XML-ul iese valid DUK (capitolele sunt opționale), deci nici validatorul n-o observă. Instanța care a deschis clasa
(D212 Etapa 3): `manual.norma` (activitățile pe normă de venit) era ignorat de `d212.genereaza` — proba pe F4 a dat
impozit pe normă 0 lei în loc de 4078, cu DUK „valid”. `common.cheie_manual` închide clasa pe generatoarele care îl
folosesc (cheie necunoscută -> refuz), dar nu pe toate; gardul ăsta închide calea REALĂ de producție pentru toate:
fiecare `_dXXXManual()` din `static/js/ecrane/declaratii.js` e citit, iar fiecare cheie de obiect pe care o produce
(inclusiv cele din rândurile listelor) trebuie să apară ca șir în modulul generatorului `core/dXXX.py`.

Cheile numerotate construite în buclă (`m["baza" + i] = …`, D600 baza1..baza12) se verifică pe familie: generatorul
trebuie să conțină măcar un `"baza<n>"`.

LIMITĂ declarată: verifică PREZENȚA numelui cheii în modul, nu că e citită din `manual` (un nume omonim folosit în
alt scop ar trece); o cheie calculată altfel decât prefix + număr (`m[k] = …` cu `k` arbitrar) nu e extrasă.
"""
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(_RAD, "static", "js", "ecrane", "declaratii.js")
_RE_TRIMITE = re.compile(r'if \(S\.tip === "(\w+)"\) body\.manual = (_\w+)\(\)')
# a doua cale: lista din memorie trimisă direct (D710: `body.obligatii = S.d710_obligatii`); rândurile ei se construiesc
# într-un handler `S.<lista>.push(<var>)` — cheile lui `<var>` (literal + `<var>.k = …`) trebuie citite de generator
_RE_LISTA = re.compile(r'if \(S\.tip === "(\w+)"\) body\.(\w+) = S\.(\w+)')


def _corp(js, fn):
    m = re.search(r"function %s\([^)]*\)\s*\{" % re.escape(fn), js)
    assert m, "funcția %s lipsește din declaratii.js" % fn
    i, adanc = m.end(), 1
    while adanc:
        adanc += {"{": 1, "}": -1}.get(js[i], 0)
        i += 1
    return js[m.end():i]


def chei_trimise(corp):
    """Cheile de obiect produse de funcție: literal (`{ k: …, k2: … }`), atribuire (`m.k = …`) și familii numerotate
    (`m["baza" + i] = …` -> `baza<n>`)."""
    familii = {f + "<n>" for f in re.findall(r"""\b[a-z]\w*\[\s*["']([A-Za-z_]\w*)["']\s*\+""", corp)}
    corp = re.sub(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'', '""', corp)       # fără conținutul șirurilor
    literal = re.findall(r"[{,]\s*([A-Za-z_]\w*)\s*:(?!:)", corp)
    atribuit = re.findall(r"\b[a-z]\w*\.([A-Za-z_]\w*)\s*=(?!=)", corp)
    return set(literal) | set(atribuit) | familii


def chei_rand_lista(js, lista):
    """Cheile rândurilor adăugate cu `S.<lista>.push(<var>)`: literalul `const <var> = {…}` + `<var>.k = …`."""
    chei = set()
    for p in re.finditer(r"S\.%s\.push\((\w+)\)" % re.escape(lista), js):
        var, inainte = p.group(1), js[:p.start()]
        dec = list(re.finditer(r"const %s = \{" % re.escape(var), inainte))
        assert dec, "rândul %s al listei %s nu e construit ca literal" % (var, lista)
        bloc = js[dec[-1].start():p.start()]
        chei |= {k for k in chei_trimise(bloc) if re.search(r"(?:\{|,)\s*%s\s*:|%s\.%s\s*=" % (k, var, k), bloc)}
    return chei


def _necitite(tip, chei):
    src = open(os.path.join(_RAD, "core", tip + ".py"), encoding="utf-8").read()
    return sorted(k for k in chei if not re.search(r"""['"]%s['"]""" % re.escape(k).replace("<n>", r"\d+"), src))


def nesolicitate():
    js = open(_JS, encoding="utf-8").read()
    out = {}
    for tip, fn in _RE_TRIMITE.findall(js):
        out[tip] = _necitite(tip, chei_trimise(_corp(js, fn)))
    for tip, camp, lista in _RE_LISTA.findall(js):
        out[tip + "." + camp] = _necitite(tip, chei_rand_lista(js, lista) | {camp})
    return {k: v for k, v in out.items() if v}


def test_ecranul_trimite_manual_pentru_declaratiile_cunoscute():
    # gardul nu are voie să treacă pentru că n-a găsit nimic de verificat (regex rupt de o refactorizare)
    tipuri = dict(_RE_TRIMITE.findall(open(_JS, encoding="utf-8").read()))
    assert len(tipuri) >= 21 and tipuri.get("d212") == "_d212Manual"
    js = open(_JS, encoding="utf-8").read()
    assert chei_rand_lista(js, "d710_obligatii") >= {"cod_oblig", "suma_dat_i", "suma_dat_c", "cota"}


def test_extractorul_vede_cheile_din_liste_si_din_atribuiri():
    corp = ('const m = { cif: x, d_rec: d.d_rec ? 1 : 0 }; if (a) m.norma = l.map((a) => ({ caen: a.caen, "x": 1 }));'
            ' for (let i = 1; i <= 12; i++) m["baza" + i] = b;')
    assert chei_trimise(corp) == {"cif", "d_rec", "norma", "caen", "baza<n>"}


def test_fiecare_cheie_trimisa_de_ecran_e_citita_de_generator():
    assert nesolicitate() == {}
