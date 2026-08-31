# -*- coding: utf-8 -*-
"""SCANNER de constante fiscale NESURSATE din codul de PRODUCTIE (20.08.2026).

DE CE EXISTA. Inventarul de pe 31.07 a masurat TESTE care asertaza o constanta: 114, din care 29 cu
temei si 85 fara. Era orb prin constructie la constantele care traiesc DOAR in productie - `25` din
`_ZIUA.get(tip, 25)` (scadente.py) nu apare in niciun test; testele asertaza date deja calculate.
Deci dimensiunea clasei era necunoscuta, iar sursarea unei bucati insemna munca pe un fragment
dintr-un intreg nemasurat.

CE DISTINGE o constanta fiscala de un numar oarecare. NU felul in care e FOLOSITA - prima incercare a
cautat aritmetica + comparatii: a gasit 127, aproape integral zgomot de format (len(cnp)==13, % 11,
1<=zi<=31, calculul Pastelui) si a RATAT tinta cunoscuta, fiindca un default la .get() nu e nici
aritmetica nici comparatie. Ci felul in care LOCUIESTE:
    H1  constanta la nivel de modul (inclusiv in dict/tuple/set literal)
    H2  default la lookup: x.get(k, N) / getattr(o, a, N)
    H3  default de parametru de functie
    H4  Decimal("N") literal
    H5  atribuit/comparat cu un nume fiscal (prag, plafon, cota, salariu, venit, termen...)

CLASIFICAREA vine de la STRAMOSUL SINTACTIC, nu de la ramura care a gasit literalul - a doua incercare
a picat exact aici: `Decimal("4050")` avea `Temei(...)` pe acelasi rand si a ajuns totusi in "nesursat".
    A  SURSAT      un stramos poarta `Temei(...)`  -> cazul BUN, se exclude
    B  NOMENCLATOR cod/pondere/lungime din XSD sau algoritm (_CNP_W, _JUD, TIPURI_OP, LIMITE_TEXT).
                   Are si el sursa, dar ALTA (XSD/validator) si alta cadenta de revizuire.
    C  NESURSAT    TINTA
    D  precizie    Decimal("0.01") de cuantizare, chr(), stari interne. Numarata, nu aruncata tacut.
    E  TEMEI IN PROZA  citarea EXISTA, dar ca text pentru om, nu ca obiect `Temei` pentru masina.

CLASA E, adaugata 20.08.2026(d) - a patra forma de orbire prin constructie, gasita PRIVIND un fisier,
nu scanandu-l: `cote_tva.py` isi citeaza temeiul in antet (art. 291 CF, Legea 141/2025) si per
categorie, iar verificatorul il are DELIBERAT pe `_TVA_EXCLUSE` fiindca el e modulul care reproduce
legea - si totusi scanul il raporta nesursat, fiindca cerea obiect `Temei`. Masuratoarea trebuia
masurata la randul ei inainte de a arde clichetul dupa ea.

CUM SE RECUNOASTE, si de ce ASA. Ancora e `_TVA_TEMEI` din verificator: acolo un literal are temei
daca VALOAREA LUI e in registrul valoare -> citare. Deci E cere ca aceeasi unitate de proza sa contina
SI o citare legala SI valoarea literalului. Ancorarea pe valoare NU e un rafinament, e miezul:
masurata pe cele 126, regula "exista o citare undeva in antetul modulului" ar fi mutat 100 din 126 in
E - inclusiv cele 11 `assert` din `d212_engine` si `d216.COTA_IMPOZIT = 0.3`, adica exact datoria
reala. Un antet care spune despre CE declaratie e modulul nu e temeiul niciunei valori din el.

    unitatea de proza = blocul contiguu de comentarii de deasupra instructiunii + comentariile de la
    coada randurilor ei; sau un PARAGRAF dintr-un docstring (al modulului / al functiei / al clasei).
    Citarile se sterg din text INAINTE de cautarea valorii, ca `art. 21` sa nu treaca drept cota 21.

E NU e clasa buna. A e sursat pentru MASINA (registrul poate consuma temeiul, gardul poate verifica
citarea); E e sursat doar pentru OM. Se numara separat tocmai ca sa nu se topeasca in A - altfel
distinctia dispare si cu ea si drumul E -> A.

ZGOMOTUL si CITARILE se exclud dupa forma, INAINTE de culegere: operanzii lui len(), divizorii de
modulo, componentele de data, si argumentele lui `Temei(...)`/`date(...)` - care sunt citari, nu valori.

LIMITA, scrisa fiindca tacerea unui scan se citeste ca absenta: granita B/C e euristica pe NUME (NOM).
Un nomenclator botezat neinspirat ajunge in C - fals pozitiv, il vezi. O valoare fiscala botezata
`_TIP_...` ar ajunge in B - fals negativ, NU o vezi. La fel si E: o proza care numeste actul si
valoarea, dar o citeaza GRESIT, trece drept sursata - scanul citeste FORMA citarii, nu adevarul ei.
De-aia gardul care foloseste scannerul poarta o calibrare in PATRU directii, nu una: o singura tinta
lasa scanul sa treaca pe gol in celelalte.
"""

import ast
import io
import json
import os
import re
import tokenize
from collections import Counter

RAD = "/home/costin/iconta_nou/core"
STRUCT = {0, 1, -1, 2, 100}
FIS = re.compile(r"^(d\d{3}[a-z_]*|salarizare|scadente|stat_plata_api|salariati_api|cote\w*|"
                 r"tva_\w+|bilant\w*|impozit\w*|contributii\w*|control_fiscal\w*|common)\.py$")
NF = re.compile(r"prag|plafon|cota|cote|salariu|salar|venit|impozit|contrib|cas\b|cass\b|cam\b|"
                r"deduc|scutir|termen|scadent|zi_dep|micro|profit|dividend|tichet|norma|baza|minim|maxim", re.I)
NOM = re.compile(r"_W$|_WEIGHT|_KEY$|CHEIE|CNP|CUI|JUD|SIRUTA|TIPURI|TIP_|_TIP|FORMA|LIMITE_TEXT|LIMITE|"
                 r"TAXCODE|COD_|CODURI|_REL_|_PER_|CAEN|VALUT|TARA|_MAP$|SCHEMA|XSD|NOMENCL|SARB|"
                 r"HEADER|_STR_|_OPT$|PERIODIC|_CAT_|CATEG", re.I)

# ── clasa E: FORMA unei citari legale in proza. Calibrata pe citarile care EXISTA in modulele
# fiscale (esantionul de 20.08d): "art.18^1 alin.(1)", "CF (L227/2015) Titlul VI", "OPANAF 2194/2025",
# "OUG 156/2024", "HG 1506/2024", "art. 291 alin. 2". Nu contine `\bCF\b` singur: prea multe „CF" din
# alte contexte l-ar face sa firma pe orice.
# GRANITELE DE CUVANT nu sunt cosmetice: fara `\b`, `lit.?\s*[a-z]\)` se aprindea pe „po-LIT-E)" din
# antetul lui `d403` si sursa cinci constante cu o coincidenta ortografica. Iar `lit` cere punctul
# obligatoriu ("lit. a)"), fiindca fara el orice cuvant terminat in „lit" + paranteza trece.
CITARE = re.compile(
    r"\bart\.?\s*\d+|\balin\.?\s*\(?\d|\blit\.\s*[a-z]\)|\bpct\.?\s*\d+"
    r"|Leg(?:ea|ii)\s*\d+\s*/\s*\d{4}|\bL\.?\s*\d{2,3}\s*/\s*\d{4}"
    r"|O\.?U\.?G\.?\s*\d+\s*/\s*\d{4}|\bOG\s*\d+\s*/\s*\d{4}|\bHG\s*\d+\s*/\s*\d{4}"
    r"|OMFP\s*\d+|OMF\s*\d+|OPANAF\s*\d+|Ordin(?:ul)?\s*\d+\s*/\s*\d{4}"
    r"|Cod(?:ul)?\s+fiscal|\bCF\s+art|Titlul\s+[IVX]+|Norm[ae]\s+metodologic", re.I)
# separatorul de mii din proza („50.000.000 euro") nu e in literal („50000000")
_MII = re.compile(r"(?<=\d)[.,  ](?=\d{3}(?!\d))")


# NUMARUL din proza, ca TOKEN - nu ca substring. Masurat pe esantion: `19` din enumerarea
# „(0,5,9,19,20,24)" e o cota si trebuie vazut, `5` din „validatorul v5" e un numar de versiune si
# NU trebuie, iar `9` din „-> R9" e un rand de formular. Deci virgula desparte (nu e separator
# zecimal in proza asta) si o litera lipita in fata descalifica.
_NUM = re.compile(r"(?<![A-Za-z_])\d+(?:\.\d+)?")


def _normal(s):
    """`2430.0` si `2430` sunt acelasi numar; `0.30` si `0.3` la fel."""
    return (s.rstrip("0").rstrip(".") or "0") if "." in s else s


def _valoarea_e_in(txt, val):
    """Valoarea literalului apare in proza asta? Citarile se STERG intai, ca `art. 21` sa nu treaca
    drept cota 21 - altfel numarul actului ar sursa orice literal egal cu el."""
    t = _MII.sub("", CITARE.sub(" ", txt)).replace(",", " , ")
    v = _normal(val)
    return any(_normal(m.group(0)) == v for m in _NUM.finditer(t))


# ── ZGOMOTUL LUI E, NUMARAT SI NUMIT (nu aruncat tacit) ──
# Limita instrumentului, masurata: un numar MIC dintr-o enumerare de coduri, aflata in acelasi
# paragraf cu o citare reala, nu se poate deosebi mecanic de valoarea sursata. Cazurile de mai jos
# au fost PRIVITE in sursa si respinse; raman in C. Cheia e (fisier, valoare), iar gardul cere ca
# fiecare intrare sa fie in continuare un candidat - altfel intrarea a imbatranit si se scoate.
PROZA_RESPINSA = {
    ("d101g.py", "16"): 'cota de impozit pe profit; proza vecina spune „rd.16 diferenta de '
                        'recuperat” si „rd.61 cercetare-dezvoltare 16% (OUG 115/2024)” - alt 16. '
                        'Geamana ei, d101.py:40, e in C: aceeasi constanta nu poate avea doua clase.',
    ("salarizare.py", "12"): 'plafonul de 12 salarii minime la concediu medical; proza vecina spune '
                             '„PNS 12/13/14” - coduri de exceptie, nu plafonul.',
}


def _comentarii(src):
    """{linie: text} pentru fiecare comentariu. Prin `tokenize`, nu prin split pe '#' - altfel un
    '#' dintr-un sir de caractere ar inventa proza care nu exista."""
    d = {}
    try:
        for t in tokenize.generate_tokens(io.StringIO(src).readline):
            if t.type == tokenize.COMMENT:
                d[t.start[0]] = t.string.lstrip("#").strip()
    except (tokenize.TokenError, IndentationError, SyntaxError):
        pass
    return d


def _paragrafe_docstring(n):
    ds = ast.get_docstring(n) if isinstance(
        n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None
    return [p for p in re.split(r"\n\s*\n", ds or "") if p.strip()]


def _proza(L, com, l_instr, l_lit):
    """Unitatile de proza care GUVERNEAZA literalul: blocul contiguu de comentarii de deasupra
    instructiunii + comentariile de la coada randurilor ei. Blocul se ia INTREG (e un singur gand:
    `d394.COTE` isi enumera cotele pe un rand si citeaza OPANAF pe urmatorul)."""
    u = []
    sus, j = [], l_instr - 1
    while j >= 1 and j in com and L[j - 1].strip().startswith("#"):
        sus.insert(0, com[j])
        j -= 1
    coada = [com[k] for k in range(l_instr, l_lit + 1)
             if k in com and not L[k - 1].strip().startswith("#")]
    if sus or coada:
        u.append(" ".join(sus + coada))
    return u


def scan(f, src):
    L = src.splitlines()
    try:
        arb = ast.parse(src)
    except SyntaxError:
        return []
    par = {}
    for n in ast.walk(arb):
        for c in ast.iter_child_nodes(n):
            par[id(c)] = n
    # cache: subarborele lui X contine un Temei?
    tem = {}

    def are_temei(n):
        if id(n) in tem:
            return tem[id(n)]
        r = any(isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id == "Temei"
                or isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute) and x.func.attr == "Temei"
                or isinstance(x, ast.Name) and x.id in ("Temei", "_Tm")
                for x in ast.walk(n))
        tem[id(n)] = r
        return r

    ex, brut = set(), []

    def lit(n):
        return (isinstance(n, ast.Constant) and isinstance(n.value, (int, float))
                and not isinstance(n.value, bool) and n.value not in STRUCT)

    def txt(n):
        ln = getattr(n, "lineno", 0)
        return ln, (L[ln - 1].strip()[:100] if 0 < ln <= len(L) else "")

    # ── pasul 1: exclude zgomotul de format, si CITARILE ──
    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Name) and fn.id == "len":
                ex.update(id(p) for p in ast.walk(n))
            if isinstance(fn, ast.Name) and fn.id in ("Temei", "_Tm", "date", "datetime"):
                ex.update(id(p) for p in ast.walk(n))          # argumentele citarii nu sunt valori
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and lit(n.right):
            ex.add(id(n.right))
        if isinstance(n, ast.Compare):
            nm = ast.unparse(n.left)[:30].strip()
            if re.fullmatch(r"_?(d|zi|mo|luna|y|an|yy|aa|mm|dd)\d?", nm):
                ex.update(id(c) for c in n.comparators if lit(c))

    # ── pasul 2: culege, cu casa si contextul ──
    def cul(n, casa, ctx):
        if lit(n) and id(n) not in ex:
            brut.append((n, casa, ctx))

    niv = {}

    def marc(n, d):
        niv[id(n)] = d
        for c in ast.iter_child_nodes(n):
            marc(c, d + (1 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else 0))
    marc(arb, 0)

    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            fn = n.func
            if isinstance(fn, ast.Attribute) and fn.attr == "get" and len(n.args) == 2:
                cul(n.args[1], "H2", "default la %s.get()" % ast.unparse(fn.value)[:34])
            elif isinstance(fn, ast.Name) and fn.id == "getattr" and len(n.args) == 3:
                cul(n.args[2], "H2", "default la getattr()")
            elif isinstance(fn, ast.Name) and fn.id == "Decimal" and n.args:
                a = n.args[0]
                if isinstance(a, ast.Constant) and re.fullmatch(r"-?\d+(\.\d+)?", str(a.value)) \
                   and float(a.value) not in {0, 1, 2, 100} and id(a) not in ex:
                    brut.append((a, "H4", "Decimal literal"))
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for d in n.args.defaults + [x for x in n.args.kw_defaults if x]:
                cul(d, "H3", "default de parametru in %s()" % n.name)
        elif isinstance(n, ast.Assign):
            tg = ", ".join(ast.unparse(t) for t in n.targets)[:44]
            if niv.get(id(n), 1) == 0:
                for p in ast.walk(n.value):
                    cul(p, "H1", "constanta de modul `%s`" % tg)
            elif NF.search(tg):
                for p in ast.walk(n.value):
                    cul(p, "H5", "atribuit lui `%s`" % tg)
        elif isinstance(n, ast.Compare):
            nm = ast.unparse(n.left)[:30].strip()
            if NF.search(nm) and not re.fullmatch(r"_?(d|zi|mo|luna|y|an|yy|aa|mm|dd)\d?", nm):
                for c in n.comparators:
                    cul(c, "H5", "comparat cu `%s`" % nm)

    # ── clasa E: proza care guverneaza literalul (comentariile lui + docstringurile care-l contin) ──
    com = _comentarii(src)

    def proza_care_sursa(n, val):
        """Unitatea de proza care contine SI citarea SI valoarea. Intoarce citatul, sau None.

        Docstringul care conteaza e DOAR al scope-ului imediat: antetul modulului guverneaza
        constantele MODULULUI, nu orice numar din adancul oricarei functii. Masurat: fara
        restrictia asta, docstringul lui `scadente.py` „sursa" ziua 25 din `_ZIUA.get(tip, 25)` -
        adica exact cazul de calibrare al nesursatului - iar antetul lui `d403` sursa cinci
        numere mici din corpul functiilor, doar fiindca erau lungi si contineau cifre."""
        a, l_instr, vazut, parag = n, getattr(n, "lineno", 0), False, []
        while id(a) in par:
            a = par[id(a)]
            if not vazut and isinstance(a, ast.stmt):
                l_instr, vazut = getattr(a, "lineno", l_instr), True
            if isinstance(a, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                parag = _paragrafe_docstring(a)      # primul scope intalnit, si numai el
                break
        for u in _proza(L, com, l_instr, getattr(n, "lineno", l_instr)) + parag:
            if CITARE.search(u) and _valoarea_e_in(u, val):
                return re.sub(r"\s+", " ", u.strip())[:90]
        return None

    # ── pasul 3: CLASIFICA uniform, urcand pe parinti ──
    out = []
    for n, casa, ctx in brut:
        cls, a = "C", n
        while id(a) in par:
            a = par[id(a)]
            if isinstance(a, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef)):
                break
            if are_temei(a):
                cls = "A"
                break
        if cls == "C" and NOM.search(ctx):
            cls = "B"
        ln, t = txt(n)
        val = str(n.value)
        cit = proza_care_sursa(n, val) if cls == "C" else None
        if cit and (f, val) not in PROZA_RESPINSA:
            cls = "E"
        out.append({"f": f, "l": ln, "v": val, "casa": casa, "cls": cls, "ctx": ctx[:44], "txt": t,
                    "cit": cit or ""})
    return out



# ── clasa D: precizie/format rezidual. Separata DUPA clasificare, ca sa ramana numarabila. ──
def _este_precizie(h):
    t, v = h["txt"], h["v"]
    if v in ("0.01", "0.001", "0.005", "0.5") and (
            "quantize" in t or re.search(r"^_?[A-Z0-9_]{1,6}\s*=\s*Decimal", t)):
        return True
    if "chr(" in t:
        return True
    return bool(re.search(r"_RANG_STARE|_ORDINE|_PRIORIT", h["ctx"]))


def _citeaza_legea(src):
    """True daca modulul CONSTRUIESTE un `Temei` - sub orice alias, rezolvat prin AST.

    DIRECTIA TACUTA, masurata 23.08.2026. Domeniul scanului era o LISTA DE NUME (`FIS`): 79 din 289
    de module `core/`. Restul erau invizibile prin constructie, iar un scan tacut se citeste ca
    absenta. Masurat: 50 de module din afara aveau semnal fiscal, iar PATRU dintre ele construiesc
    `Temei` - adica sunt fiscale prin propria lor marturisire: `contracte_speciale.py`,
    `sponsorizari.py`, `deconturi.py`, `motor.py`. Clasa C din ele: 14, nevazute.

    De ce criteriul asta si nu o lista mai lunga de nume: e MECANIC si se intretine singur. Un modul
    care citeaza legea intra in domeniu in ziua in care o citeaza, fara ca cineva sa-si aminteasca
    sa-l adauge in `FIS`. Un nume nou in `FIS` cere memorie; un `Temei(...)` nu.

    CE NU ACOPERA, scris: un modul fiscal care NU citeaza legea deloc ramane afara (masurat: inca 10
    module cu semnal fiscal, 12 constante de clasa C - vezi R25). Criteriul prinde modulele care
    stiu ca sunt fiscale, nu pe cele care ar trebui sa stie."""
    try:
        arb = ast.parse(src)
    except SyntaxError:
        return False
    alias = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.ImportFrom):
            for a in n.names:
                if a.name == "Temei":
                    alias.add(a.asname or a.name)
        elif isinstance(n, ast.ClassDef) and n.name == "Temei":
            alias.add("Temei")
    for n in ast.walk(arb):
        if isinstance(n, ast.Call):
            f = n.func
            if (isinstance(f, ast.Name) and f.id in alias) or \
               (isinstance(f, ast.Attribute) and f.attr == "Temei"):
                return True
    return False


PRAG_SEMNAL = 20   # potriviri `NF` in sursa; vezi `in_domeniu`


def in_domeniu(f, src):
    """Un modul e in domeniul scanului daca: poarta un NUME fiscal (`FIS`), SAU CITEAZA legea
    (construieste un `Temei`), SAU are DENSITATE de vocabular fiscal peste `PRAG_SEMNAL`.

    A TREIA regula, adaugata 23.08.2026 dupa sondajul COMPLET cerut de Costin. Primele doua prindeau
    modulele care se numesc fiscale sau stiu ca sunt. A treia le prinde pe cele care nici nu se
    numesc, nici nu stiu - si acolo statea datoria: 48 de constante de clasa C in 21 din cele 46 de
    module ramase.

    PRAGUL NU E ALES PE GUST - e ales pe COMPOZITIE, masurata pe toate cele 48 inainte de a decide:
      17 FISCALE reale  - plafoanele de casa (Legea 70/2015, sase valori intr-un modul al carui
                          comentariu spune „cu temei" si nu poarta niciunul), cota 21 ca DEFAULT DE
                          PARAMETRU in sase module, plafonul de 10% si cota de 16% din `ong.py`,
                          pragul de 270 de zile de la art. 26(1)c, impozitul pe dobanda de 10%,
                          norma de 8 ore/zi;
      20 ALGORITM       - vectorul de ponderi al checksum-ului CNP (`_CHEIE`, de doua ori cate noua)
                          si decodarea secolului din CNP. Acestea NU intra: `CHEIE` a fost adaugat in
                          `NOM`, unde ii era locul - e aceeasi clasa cu `_CNP_W`;
      11 OPERATIONALE   - praguri de zile pentru notificari, orizonturi de scadentar, paginare,
                          latimea unui logo in PDF.
    Dupa scoaterea celor 20 de algoritm raman 30, din care 17 fiscale - peste jumatate. Zgomotul
    operational NU se arunca: intra in clichet pe fisierul lui, deci e VIZIBIL si nu poate creste."""
    if not f.endswith(".py") or f.startswith("test_"):
        return False
    return (bool(FIS.match(f)) or _citeaza_legea(src) or len(NF.findall(src)) >= PRAG_SEMNAL
            or _poarta_valoare_de_registru(src))


#: NUME de constanta care ANUNTA o valoare fiscala. E AL DOILEA SEMNAL, si e obligatoriu — vezi
#: `_poarta_valoare_de_registru`. Nu se foloseste singur nicaieri: un nume fiscal fara valoare de
#: registru nu aduce fisierul in domeniu, si nici invers.
NUME_FISCAL = re.compile(r"PLAFON|COTA|COTE|PRAG|TVA|IMPOZIT|ACCIZ|SALARIU|DEDUCER|CASS?|CAM|"
                         r"AMORTIZ|MIJLOC|SCUTIR|FACILITAT|TICHET|DIURN|DIVIDEND|MICRO|PROFIT",
                         re.I)


def _valori_de_registru():
    """Valorile CURENTE din registrul de cote, ca intregi si ca procente. Citite din `common.COTE`,
    nu scrise aici - altfel ar fi chiar constanta nesursata pe care o cautam."""
    try:
        from core.common import COTE
    except Exception:
        return set()
    out = set()
    for intrari in COTE.values():
        for el in intrari:
            try:
                val = el[1]
            except Exception:
                continue
            try:
                f = float(val)
            except Exception:
                continue
            if 0 < f < 1:                       # cotele stau ca fractii: 0.21 -> si 21
                out.add(round(f * 100, 4))
            out.add(f)
    return {v for v in out if v >= 1}           # pragurile mari raman, fractiile de sub 1 ies


def _poarta_valoare_de_registru(src):
    """True daca un DEFAULT DE PARAMETRU e egal cu o valoare din registrul de cote.

    A PATRA directie oarba, masurata 23.08.2026, la intrebarea lui Costin. Dupa doua largiri, 15 din
    cele 25 de functii cu `cota = 21` ca default erau INCA in afara domeniului: `avansuri.py`,
    `comodat_chirii.py`, `intracomunitar.py`, `inventariere.py`, `leasing.py`, `obiecte_inventar.py`,
    `productie.py`, `sgr.py`. Niciunul nu se numeste fiscal, niciunul nu citeaza legea, si toate
    vorbesc prea putin ca sa treaca de pragul de densitate - dar fiecare poarta o COTA DE TVA.

    Criteriul: un modul care poarta o VALOARE din registru e fiscal, oricat de putin ar vorbi. E
    mecanic si se intretine singur - cand se schimba o cota in registru, domeniul se muta cu ea."""
    import ast as _ast
    valori = _valori_de_registru()
    if not valori:
        return False
    try:
        arb = _ast.parse(src)
    except SyntaxError:
        return False
    def _e_valoare(nod):
        """Un literal numeric — direct sau `Decimal("...")` — care e o valoare din registru."""
        if isinstance(nod, _ast.Constant) and isinstance(nod.value, (int, float)) and not isinstance(nod.value, bool):
            return float(nod.value) in valori
        if isinstance(nod, _ast.Call) and getattr(getattr(nod, "func", None), "id", "") == "Decimal" and nod.args and isinstance(nod.args[0], _ast.Constant):
            try:
                return float(nod.args[0].value) in valori
            except (TypeError, ValueError):
                return False
        return False

    for n in _ast.walk(arb):
        if not isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
            continue
        a = n.args
        for d in list(a.defaults) + list(a.kw_defaults):
            if d is not None and _e_valoare(d):
                return True

    # A CINCEA DIRECTIE OARBA, masurata 31.08.2026. Regula de mai sus se uita DOAR la valorile
    # implicite ale parametrilor — forma in care clasa fusese gasita pe 23.08 („cota = 21 ca
    # default"). O CONSTANTA DE MODUL care poarta aceeasi valoare ii scapa. Instanta:
    # `mijloace_fixe_import_api.PLAFON_MF_2026 = 5000.0` — plafonul de incadrare ca mijloc fix, chiar
    # valoarea curenta din registru — statea in afara domeniului, iar fisierul avea ZERO intrari in
    # inventar. A fost gasit din INTAMPLARE, prin axa B a interdictiei 55, nu de instrumentul asta.
    # Masurat atunci: 248 din 412 de fisiere sunt in afara domeniului.
    #
    # DE CE DOUA SEMNALE, si nu doar valoarea. Cu valoarea singura, extinderea aducea `nucleu.py`:
    # `_SCRYPT_N = 16`, `_SALT_BYTES = 16`, `PAROLA_MIN = 8` — parametri de criptografie care se
    # potrivesc din intamplare cu cota de profit (16) si cu cea de dividende istorica (8). Sase
    # constante ar fi intrat in clichet ca datorie fiscala permanenta, nereparabila fiindca nu e
    # fiscala. Cu nume SI valoare: trei fisiere, zero fals-pozitive, ZERO clasa C adaugata — cele
    # patru valori nou-vazute sunt clasa E, adica sursate in proza, nu nesursate.
    #
    # CE NU PRINDE, si se scrie: o valoare fiscala care NU e in registru. Instanta ramasa,
    # `intrastat.PRAG_2026 = 1000000` — pragul Intrastat nu e in `COTE`, deci nicio regula ancorata
    # pe registru n-o poate vedea. E alta clasa (o valoare fara temei, interdictia 57).
    for n in arb.body:
        if not isinstance(n, _ast.Assign):
            continue
        for tg in n.targets:
            nume = getattr(tg, "id", "")
            if nume and nume.isupper() and NUME_FISCAL.search(nume) and _e_valoare(n.value):
                return True
    return False


def inventar(rad=RAD):
    """Toti literalii clasificati din modulele fiscale. Fara efecte in afara de citit."""
    hits = []
    for f in sorted(os.listdir(rad)):
        if not f.endswith(".py") or f.startswith("test_"):
            continue
        with open(os.path.join(rad, f), encoding="utf-8", errors="replace") as fh:
            _src = fh.read()
        if not in_domeniu(f, _src):
            continue
        hits += scan(f, _src)
    vaz, U = set(), []
    for h in hits:
        k = (h["f"], h["l"], h["v"])
        if k in vaz:
            continue
        vaz.add(k)
        if h["cls"] == "C" and _este_precizie(h):
            h["cls"] = "D"
        U.append(h)
    return U


def nesursate(rad=RAD):
    """Doar clasa C - constantele fiscale fara temei atasat, nici macar in proza."""
    return [h for h in inventar(rad) if h["cls"] == "C"]


def in_proza(rad=RAD):
    """Clasa E - citarea exista, dar ca text pentru om. Nu e datorie de acelasi fel cu C, dar nici
    caz inchis: drumul ei e E -> A (temeiul devine obiect, deci verificabil de masina)."""
    return [h for h in inventar(rad) if h["cls"] == "E"]


if __name__ == "__main__":
    from collections import Counter
    U = inventar()
    for c in "ABCDE":
        print("%s %4d" % (c, sum(1 for h in U if h["cls"] == c)))
    print("")
    print("BASELINE = {")
    for f, n in sorted(Counter(h["f"] for h in nesursate()).items()):
        print('    "%s": %d,' % (f, n))
    print("}")
    print("")
    print("E - temei in proza (%d):" % len(in_proza()))
    for h in in_proza():
        print("  %-22s l.%-5d %-10s %s" % (h["f"], h["l"], h["v"], h["cit"]))
