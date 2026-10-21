# -*- coding: utf-8 -*-
"""GARD — numeralul acordat cu substantivul: „1 notă”, „3 note”, „20 de note”, nu „1 note” / „20 note” / „5 absent”.

Comanda Costin 15.10.2026 (lotul 5), verbatim: „261, 263 și «1 angajați» din Panou Admin → Cabinete: plural fix după număr
(«1 note», «1 facturi»). Corectezi clasa peste tot.”

Clasa: un număr calculat, urmat în textul afișat de un substantiv scris o singură dată (la plural, sau la singular), fără să țină
cont de număr. Româna cere: 1 -> singular; 2–19 (și orice număr care se termină în 01–19) -> plural; 0, 20–99 și orice număr care
se termină în 00 sau 20–99 -> „de” + plural. Un singur loc în fiecare limbaj face asta: `core/common.py::cate` (Python) și
`static/js/plural.js::cate` (JS, reexportat din `api.js`), verificate pe ACEEAȘI tabelă de valori (`TABELA`).

Ce prinde gardul pe sursă (calibrat pe codul din 15.10.2026; ieșirea `python -m core.test_plural_dupa_numar`):
  JS (`static/js/**/*.js`, cu escape-urile `\\uXXXX` decodate):
    R1 `${expr} [de ]cuvânt` — o interpolare urmată (eventual după etichete HTML) de un cuvânt care se termină ca un plural
       românesc (-i / -e, deci și -uri, -ări, -ii) sau de un „de” scris de mână;
    R2 `expr + " [de ]cuvânt"` — același lucru, prin concatenare;
    R3 `x === 1 ? "…" : "…"` / `x === 1 ? a : b` — alegerea scrisă de mână între forme (nu pune „de” de la 20); înlocuită de `cate`.
  Python (`core/**/*.py` fără teste, și `main.py`), pe arborele sintactic, numai în textele care pot ajunge la om (nu în print,
  jurnal, assert, docstring):
    P1 f-string `{expr} [de ]cuvânt`; P2 `%d`/`%s`/`%(x)d` + ` [de ]cuvânt`; P3 `str(n) + " cuvânt"`.
Cuvântul NU e o listă scrisă de mână de substantive: e orice cuvânt cu terminație de plural, minus o listă ÎNCHISĂ de cuvinte care
nu sunt substantive numărabile (`NU_SUBSTANTIV`: verbe, prepoziții, conjuncții, unitatea monetară). Ce rămâne după aceste reguli
e numit structural în `EXCEPTII` (fișier, fragment, motiv) — clichet la zero pentru tot restul.

LIMITE declarate: un număr pus într-un element și substantivul în ALT element construit separat (alt șir, altă funcție) nu se
vede; un singular fix urmat de un număr („firmă: 3”) nu e clasa. Pe ecran, `core/limba_ecran.py::_ACORD` prinde „1 <plural>” și
„20 <plural>” fără „de” pe textul afișat, cu lista de plurale `PLURALE` (verificată aici că acoperă toate formele date lui `cate`).
"""
import ast
import io
import json
import os
import re
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: una și aceeași tabelă pentru Python și JS: (n, așteptat cu „partener”/„parteneri”)
TABELA = [(0, "0 parteneri"), (1, "1 partener"), (2, "2 parteneri"), (19, "19 parteneri"), (20, "20 de parteneri"),
          (21, "21 de parteneri"), (99, "99 de parteneri"), (100, "100 de parteneri"), (101, "101 parteneri"),
          (119, "119 parteneri"), (120, "120 de parteneri"), (1000, "1000 de parteneri"), (1001, "1001 parteneri"),
          (2.5, "2,5 parteneri"), (20.5, "20,5 parteneri"), (1.5, "1,5 parteneri")]

#: cuvinte cu terminație de plural care NU sunt substantive numărate după un număr (listă închisă; un substantiv nou NU intră aici)
NU_SUBSTANTIV = {
    "e", "este", "sunt", "fi", "si", "și", "pe", "de", "se", "ce", "care", "mai", "nici", "decât", "dacă", "ori", "sau", "fie",
    "rămâne", "rămân", "trebuie", "poate", "pare", "apare", "apar", "intră", "deci", "aici", "acolo", "acestei", "către", "le", "îi",
    "lei", "peste", "ale", "are", "cere", "cuprinde", "începe", "vine", "duce", "trece", "aparține", "depune", "face", "spune", "arată", "oricare",
}


def _decodeaza(text):
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), text)


_CUV = r"(?P<de>de\s+)?(?P<w>[a-zăâîșțşţ]+)"
_R1 = re.compile(r"\$\{(?P<e>(?:[^{}]|\{[^{}]*\})*)\}(?:\s*</?[a-zA-Z][^<>]*>)*(?:\s|&nbsp;)+" + _CUV + r"(?![\w=-])")
_R2 = re.compile(r"(?P<e>[\w.\])]+)\s*\+\s*[\"'`](?:\s|&nbsp;)+" + _CUV + r"(?![\w-])")
#: R3a `${x} ${x === 1 ? …}` — forma substantivului aleasă de mână imediat după același număr
_R3A = re.compile(r"\$\{\s*(?P<x>[^{}]+?)\s*\}(?:\s*</?[a-zA-Z][^<>]*>)*(?:\s|&nbsp;)*\$\{\s*\(?\s*(?P=x)\s*\)?\s*===?\s*1\s*\?")
#: R3b `factur${n === 1 ? "ă" : "i"}` — terminația aleasă de mână, lipită de cuvânt
_R3B = re.compile(r"(?<!\\)[a-zăâîșț]\$\{[^{}]*?===?\s*1\s*\?\s*[\"'`]")
#: R3c `n === 1 ? unu : multe` — un selector generic de formă (ce face `cate`, fără „de”)
_R3C = re.compile(r"===?\s*1\s*\?\s*[A-Za-z_]\w*\s*:\s*[A-Za-z_]\w*\s*[)};,]")
#: R4 o expresie sigur numerică (`|| 0`, `?? 0`, `.length`, `Number(`) urmată de orice cuvânt care nu e de legătură — prinde și
#: singularul fix („5 absent”, „3 concediu”, „2 salariat”), pe care terminația de plural nu-l vede
_R4 = re.compile(r"\$\{(?P<e>[^{}?]*(?:\|\| 0|\?\? 0|\.length|Number\()[^{}?]*)\}(?:\s*</?[a-zA-Z][^<>]*>)*(?:\s|&nbsp;)+"
                 r"(?P<w>[a-zăâîșțşţ]+)(?![\w=-])")
#: cuvinte de legătură care pot urma unui număr fără să fie substantivul numărat (listă închisă)
DE_LEGATURA = {"fără", "cu", "în", "din", "deja", "un", "o", "prin", "la", "pe", "și", "sau", "de", "până", "după", "peste", "sub",
               "pentru", "față", "ori", "x"}


def _plural(w, de):
    """Cuvântul are terminație de plural românesc (-i, -e: deci și -uri, -ări, -ii, -ele) și nu e de legătură. Un „de” scris de mână
    contează numai înaintea unui astfel de cuvânt („20 de zile”); „3 de urmărit” / „2 de validat” nu sunt numeralul cu „de”."""
    return w not in NU_SUBSTANTIV and w.endswith(("i", "e")) and not w.endswith(("ește", "ește", "ăște", "ează"))


def _e_text(expr):
    """Interpolarea se încheie cu un șir literal („${x ? "a" : "b"}”) — produce text, nu un număr."""
    return expr.rstrip().endswith(('"', "'", "`"))


def _linii_cod(text):
    """Liniile de cod, cu comentariile întregi golite (păstrează numerotarea)."""
    out, bloc = [], False
    for linie in text.split("\n"):
        s = linie.strip()
        if bloc:
            out.append("")
            bloc = "*/" not in s
            continue
        if s.startswith("/*"):
            out.append("")
            bloc = "*/" not in s
            continue
        out.append("" if s.startswith("//") or s.startswith("*") else linie)
    return out


def gaseste_js():
    """[(fisier, linie, regula, fragment)] — locurile din JS unde un număr e urmat de o formă scrisă fix."""
    out = []
    baza = os.path.join(RAD, "static", "js")
    for d, _, fs in os.walk(baza):
        for f in sorted(fs):
            if not f.endswith(".js") or f.endswith(".min.js"):
                continue
            p = os.path.join(d, f)
            rel = os.path.relpath(p, RAD)
            for i, linie in enumerate(_linii_cod(_decodeaza(io.open(p, encoding="utf-8").read())), 1):
                for rx, reg in ((_R1, "R1"), (_R2, "R2")):
                    for m in rx.finditer(linie):
                        if _plural(m.group("w"), m.group("de")) and not _e_text(m.group("e")):
                            out.append((rel, i, reg, m.group(0)[-90:]))
                for rx, reg in ((_R3A, "R3"), (_R3B, "R3"), (_R3C, "R3")):
                    out += [(rel, i, reg, m.group(0)[-90:]) for m in rx.finditer(linie)]
                for m in _R4.finditer(linie):
                    w = m.group("w")
                    if w not in DE_LEGATURA and w not in NU_SUBSTANTIV and not w.endswith(("i", "e")) \
                            and not re.match(r"\s*(?:cate|dupaNumar)\(", m.group("e")):   # numărul trecut deja prin helper
                        out.append((rel, i, "R4", m.group(0)[-90:]))
    return out


# ── Python ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_LOG = {"print", "debug", "info", "warning", "warn", "error", "exception", "critical", "log"}
_P2 = re.compile(r"%(?:\([a-z_]+\))?[ds](?:\s|&nbsp;)+" + _CUV + r"(?![\w=-])")   # „cui=” e atribut XML, nu cuvânt
_P_FMT = re.compile(r"\{[a-z_0-9]*\}(?:\s)+" + _CUV + r"(?![\w=-])")
_P_LIPIT = re.compile(r"^(?:\s|&nbsp;)+" + _CUV + r"(?![\w-])")


def _fisiere_py():
    for d, _, fs in os.walk(os.path.join(RAD, "core")):
        if os.path.basename(d) == "__pycache__":
            continue
        for f in sorted(fs):
            if f.endswith(".py") and not f.startswith("test_"):
                yield os.path.join(d, f)
    yield os.path.join(RAD, "main.py")


def _numeric(nod):
    """Expresia pare un număr (nu un nume, nu un text): len(...), un nume, un atribut, un apel la int/len/sum, o operație."""
    if isinstance(nod, ast.Call):
        f = nod.func
        nume = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
        return nume in ("len", "int", "sum", "str", "max", "min", "abs", "count", "get")
    return isinstance(nod, (ast.Name, ast.Attribute, ast.Subscript, ast.BinOp, ast.Constant))


#: acordul VERBULUI cu numărul („apare”/„apar”) e legitim după `cate`; listă închisă de forme verbale
VERBE_ACORD = {"e", "este", "sunt", "apare", "apar", "poate", "pot", "rămâne", "rămân", "a", "au", "are", "intră", "intra", "nu intră",
               "nu intra", "trebuie", "lipsește", "lipsesc", "s-a", "s-au", "va", "vor", "o", "le", "îl", "îi", "a fost", "au fost"}


def _e_unu(test):
    return (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], (ast.Eq, ast.NotEq))
            and isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value == 1)


def _intreg(nod):
    return isinstance(nod, ast.Call) and getattr(nod.func, "id", "") in ("len", "int")


def gaseste_py():
    out = []
    for p in _fisiere_py():
        rel = os.path.relpath(p, RAD)
        src = io.open(p, encoding="utf-8").read()
        try:
            arb = ast.parse(src)
        except SyntaxError:
            continue
        ignorate = set()
        for nod in ast.walk(arb):
            if isinstance(nod, ast.Call):
                f = nod.func
                nume = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
                if nume in _LOG:
                    ignorate |= {id(x) for a in nod.args for x in ast.walk(a)}
            elif isinstance(nod, ast.Raise) and isinstance(nod.exc, ast.Call) \
                    and getattr(nod.exc.func, "id", "") in ("AssertionError", "RuntimeError", "SystemExit"):
                # invariant încălcat / aplicația nu pornește: textul îl citește dezvoltatorul în jurnal, nu contabilul
                ignorate |= {id(x) for x in ast.walk(nod)}
            elif isinstance(nod, ast.Assert):
                ignorate |= {id(x) for x in ast.walk(nod)}
            elif isinstance(nod, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)) and nod.body:
                b = nod.body[0]
                if isinstance(b, ast.Expr) and isinstance(b.value, ast.Constant):
                    ignorate.add(id(b.value))
        for nod in ast.walk(arb):
            if id(nod) in ignorate:
                continue
            if isinstance(nod, ast.JoinedStr):
                v = nod.values
                for a, b in zip(v, v[1:]):
                    if isinstance(a, ast.FormattedValue) and _numeric(a.value) and isinstance(b, ast.Constant) and isinstance(b.value, str):
                        m = _P_LIPIT.match(b.value)
                        if m and _plural(m.group("w"), m.group("de")) and not (m.group("de") and not _intreg(a.value)):
                            out.append((rel, b.lineno, "P1", "{%s}%s" % (ast.unparse(a.value)[:50], b.value[:40])))
            elif isinstance(nod, ast.Constant) and isinstance(nod.value, str):
                for rx, reg in ((_P2, "P2"), (_P_FMT, "P2")):
                    for m in rx.finditer(nod.value):
                        # „%s de livrare” e complement, nu numeralul cu „de”; „%d de zile” e numeralul
                        if _plural(m.group("w"), m.group("de")) and not (m.group("de") and not m.group(0).startswith(("%d", "%("))):
                            out.append((rel, nod.lineno, reg, m.group(0)[-90:]))
            elif isinstance(nod, ast.IfExp) and _e_unu(nod.test) and all(isinstance(x, ast.Constant) and isinstance(x.value, str)
                                                                          for x in (nod.body, nod.orelse)) \
                    and not ({nod.body.value.strip(), nod.orelse.value.strip()} <= VERBE_ACORD):
                out.append((rel, nod.lineno, "P4", "%r if … == 1 else %r" % (nod.body.value[:30], nod.orelse.value[:30])))
            elif isinstance(nod, ast.BinOp) and isinstance(nod.op, ast.Add) and isinstance(nod.right, ast.Constant) \
                    and isinstance(nod.right.value, str) and isinstance(nod.left, ast.Call) and getattr(nod.left.func, "id", "") == "str":
                m = _P_LIPIT.match(nod.right.value)
                if m and _plural(m.group("w"), m.group("de")):
                    out.append((rel, nod.lineno, "P3", nod.right.value[:90]))
    return out


# ── excepțiile reale, numite (fișier, fragmentul găsit, motivul) ────────────────────────────────────────────────────────────────
#: module Python al căror text NU ajunge la contabil (unelte de dezvoltator, jurnal operațional) — tot modulul, cu motivul
EXCEPTII_PY_MODULE = {
    "core/agenda.py": "starea campaniei de dezvoltare (TESTE.md, GARZI.md, git) — o citește executorul în terminal",
    "core/alerta_acces.py": "alertă de securitate (GDPR art.33) pe emailul operatorului platformei, nu la cabinet",
    "core/alerta_load.py": "motivul alertei de încărcare a serverului, în jurnal și în emailul operatorului",
    "core/expirare_cote.py": "raport intern de vechime a confirmării valorilor fiscale — către dezvoltator",
    "core/observare.py": "stratul de observare (timpi, pool) — alertă operațională către operator",
    "core/p4_clasificare.py": "clasificarea operațiilor compuse din cod — unealtă de dezvoltator, verdicte în teste",
    "core/p5_clasificare.py": "verdictele I/O blocant din cod — unealtă de dezvoltator",
}
#: (fișier, fragment din ce raportează scanerul, motiv)
EXCEPTII = [
    ("static/js/ecrane/semafor.js", "unu : multe}",
     "formele din LUMINI_CONTROL sunt eliptice, fără substantiv („cu restanțe”, „de urmărit”, „la zi”, „nu se pot verifica”): ternarul "
     "acordă verbul („1 nu se poate verifica” / „2 nu se pot verifica”); cu „de” ar ieși „20 de cu restanțe”"),
    ("static/js/ecrane/semafor.js", "${n}</b>&nbsp;${n === 1 ?", "aceeași listă eliptică (LUMINI_CONTROL), afișată cu cifra îngroșată"),
    ("static/js/ecrane/semafor.js", "${s[k] || 0} ${(s[k] || 0) === 1 ?", "aceeași listă eliptică (LUMINI_CONTROL), în eticheta cardului"),
    ("static/js/ecrane/firme.js", "${r.nota} create",
     "`r.nota` e formula contabilă a notei („5121=4111”), nu un număr; numărul e trecut prin `cate` cu formele complete "
     "(„notă 5121=4111 creată” / „note 5121=4111 create”)"),
    ("static/js/ecrane/asistenti.js", ") + ` dezactivați",
     "operandul din stânga e un ternar de text („Arată” / „Ascunde”), nu un număr: „Arată dezactivați (N)”"),
    ("core/chitante.py", "' ban' if",
     "suma în litere de pe chitanță: „un ban” / „doi bani” sub 20, iar ramura de la 20 pune „de bani” explicit (ca la lei, rândul de mai sus)"),
    ("core/d401.py", "%s coproprietate",
     "`%s` e prefixul rândului (imobilul), nu un număr: „Imobilul 2: coproprietate -> cel puțin un coproprietar”"),
    ("core/tipare_api.py", "%d respingeri", "prompt pentru asistentul AI (date de intrare, nu text afișat)"),
    ("core/tipare_api.py", "%d respinse", "prompt pentru asistentul AI (date de intrare, nu text afișat)"),
    ("core/uc_coada.py", "'notei' if",
     "[284] genitivul articulat fără numeral („declarația așteaptă validarea notei” / „notelor”): niciun număr afișat, deci nici „de”"),
    ("core/interpretare.py", "%d variante", "invariant al registrului de interpretări, verificat la încărcarea modulului (`InterpretareIncompleta`)"),
    ("core/d205.py", "'valideaz-o' if",
     "[lotul 10, 431] pronumele clitic acordat cu notele ENUMERATE înaintea lui („nota … e ciornă. … valideaz-o” / „validează-le”): niciun "
     "numeral afișat, deci nici „de” — aceeași clasă cu „notei” din `uc_coada`"),
    ("core/istoric_declaratii_import_api.py", "'anul' if",
     "[lotul 10, 426] „În anul 2025” / „În anii 2024, 2025”: anii se ENUMERĂ, nu se numără — niciun numeral afișat, deci nici „de”; "
     "numărul declarațiilor din aceeași frază trece prin `cate`"),
]


def _exceptat(g):
    rel, _, _, frag = g
    return rel in EXCEPTII_PY_MODULE or any(rel == f and x in frag for f, x, _ in EXCEPTII)


def test_cate_python_si_js_pe_aceeasi_tabela(tmp_path):
    """`common.cate` și `plural.js::cate` dau exact aceleași texte pe aceeași tabelă (0, 1, 2, 19, 20, 21, 99, 100, 101, 119, 120,
    1000, 1001); `dupaNumar` e același text fără număr. MUTAȚIE: în plural.js `r >= 20` -> `r > 20` -> „20 parteneri” -> pică."""
    from core.common import cate
    assert [cate(n, "partener", "parteneri") for n, _ in TABELA] == [t for _, t in TABELA]
    (tmp_path / "plural.mjs").write_text(io.open(os.path.join(RAD, "static/js/plural.js"), encoding="utf-8").read(), encoding="utf-8")
    cod = ("import('%s').then((m) => console.log(JSON.stringify(%s.map((n) => [m.cate(n, 'partener', 'parteneri'), "
           "m.dupaNumar(n, 'partener', 'parteneri')]))))" % ((tmp_path / "plural.mjs").as_posix(), json.dumps([n for n, _ in TABELA])))
    r = subprocess.run(["node", "-e", cod], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stderr[-800:]
    assert json.loads(r.stdout) == [[t, t.split(" ", 1)[1]] for _, t in TABELA]


def test_api_reexporta_helperul_si_nu_mai_exista_selectoare_locale():
    """`api.js` reexportă `cate` și `dupaNumar` din `plural.js` (un singur loc); `asistenti.js` nu mai are `_n` al lui."""
    api = io.open(os.path.join(RAD, "static/js/api.js"), encoding="utf-8").read()
    assert re.search(r'export \{ cate, dupaNumar \} from "\./plural\.js(\?v=\w+)?";', api)
    assert not re.search(r"\bconst _n\s*=", io.open(os.path.join(RAD, "static/js/ecrane/asistenti.js"), encoding="utf-8").read())


def test_js_niciun_numar_cu_forma_scrisa_fix():
    """Clichet la ZERO în `static/js` (R1–R4), în afara excepțiilor numite. MUTAȚIE: în `firme.js` antetul Registrului jurnal înapoi la
    `${note.length} note` -> pică cu „firme.js:… [R1] ${note.length} note”."""
    rele = [g for g in gaseste_js() if not _exceptat(g)]
    assert not rele, "număr urmat de o formă scrisă fix (folosește `cate` din api.js):\n  " + "\n  ".join("%s:%d [%s] %s" % g for g in rele)


def test_py_niciun_numar_cu_forma_scrisa_fix():
    """Clichet la ZERO în `core/*.py` și `main.py` (P1–P4), în afara excepțiilor numite. MUTAȚIE: în `clienti_api.py` mesajul înapoi
    la „clientul are %d facturi” -> pică."""
    rele = [g for g in gaseste_py() if not _exceptat(g)]
    assert not rele, "număr urmat de o formă scrisă fix (folosește `common.cate`):\n  " + "\n  ".join("%s:%d [%s] %s" % g for g in rele)


def test_exceptiile_inca_exista():
    """O excepție care nu mai prinde nimic se scoate (altfel ar acoperi tăcut un loc nou cu același fragment)."""
    toate = gaseste_js() + gaseste_py()
    for f, x, motiv in EXCEPTII:
        assert motiv and any(g[0] == f and x in g[3] for g in toate), (f, x)
    for f, motiv in EXCEPTII_PY_MODULE.items():
        assert motiv and any(g[0] == f for g in toate), f


def _forme_date_lui_cate():
    """Pluralele date lui `cate` / `dupaNumar` în cod (JS și Python), ca șiruri literale."""
    rx = re.compile(r"\b(?:cate|dupaNumar)\(\s*[^\"'`]+?,\s*([\"'])((?:(?!\1).)+)\1\s*,\s*([\"'])((?:(?!\3).)+)\3\s*\)")
    out = set()
    surse = [os.path.join(d, f) for d, _, fs in os.walk(os.path.join(RAD, "static", "js")) for f in fs if f.endswith(".js")]
    surse += list(_fisiere_py())
    for p in surse:
        for m in rx.finditer(_decodeaza(io.open(p, encoding="utf-8").read())):
            out.add(m.group(4))
    return out


def test_scanul_ecranului_cunoaste_toate_pluralele_din_cod():
    """`core/limba_ecran.py::PLURALE` (din care se face `_ACORD`, judecata textului AFIȘAT) cuprinde substantivul fiecărui plural dat
    lui `cate` în cod — lista ecranului e derivată din cod, nu una mică scrisă o dată. MUTAȚIE: „angajați” scos din PLURALE -> pică."""
    from core.limba_ecran import PLURALE
    lipsa = sorted({p.split()[0] for p in _forme_date_lui_cate()} - set(PLURALE))
    assert not lipsa, "plurale date lui cate, necunoscute scanului de ecran (adaugă-le în limba_ecran.PLURALE): %s" % lipsa


def test_scanul_ecranului_prinde_acordul_gresit():
    """Judecata textului afișat: „1 note”, „1 angajați”, „20 facturi” sunt defecte de acord; „1 notă”, „20 de note”, „101 note”,
    „1.200 de facturi” nu."""
    from core.limba_ecran import defecte
    rele = ("Luna 10/2026 · 1 note", "1 angajați · 3 firme", "din 20 facturi încasate", "120 cabinete active")
    bune = ("Luna 10/2026 · 1 notă", "20 de note", "101 note", "1.200 de facturi", "2 angajați", "19 zile", "1 iulie 2026")
    assert all([d for d in defecte(t) if d[0] == "acord"] for t in rele), [(t, defecte(t)) for t in rele]
    assert not [(t, d) for t in bune for d in defecte(t) if d[0] == "acord"]


if __name__ == "__main__":
    import sys
    tot = gaseste_js() + (gaseste_py() if "--py" in sys.argv or "--tot" in sys.argv else [])
    if "--py" in sys.argv:
        tot = gaseste_py()
    for r in tot:
        print("%s:%d [%s] %s" % r)
    print("TOTAL", len(tot))
