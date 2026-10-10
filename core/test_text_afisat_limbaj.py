"""core/test_text_afisat_limbaj.py — GARD: textul afișat contabilului e limbă română, nu limbaj de programator.

Comanda Costin, lotul „Retest 08.10” pct.14 (verbatim în DECIZII): „Limbaj de programator în ecrane: common.COTE tva_standard,
R3_1_1/R7_1_1, NEVERIFICAT, d100_fapt / False / None, partener_id, partener_nume, self_billing. Plus texte fără diacritice / cu
majuscule («ATENTIE», «apartin», «incrucisat»).”

DE CE AU SCĂPAT gărzile existente (`test_diacritice_afisate`, `test_mesaje_fara_camp_intern`, `test_control_fiscal_diacritice`) —
trei goluri de CLASĂ, nu de instanță:
  1. ROLUL. Ele citesc textul numai din chei de dicționar (`{"limita": "..."}`), din `HTTPException(detail=)` și din corpul
     excepțiilor. Limitele verdictului Control fiscal se scriu prin ARGUMENT CU NUME (`_rezultat(..., limita="...")`), prin
     ATRIBUIRE (`limita = "..."; limita += "..."`) și prin `res.avertismente.append("...")` — invizibile pentru ele.
  2. ȘIRUL MIXT. `flag()` sare peste orice șir care are măcar o diacritică — „ATENTIE (D406): unitate(i) de masura necunoscută(e)”
     are „ă”, deci trecea întreg.
  3. DICȚIONARUL. „atentie”, „apartin”, „incrucisat” nu erau declanșatori; majusculele de accent și identificatorii de cod
     (`common.COTE`, `R3_1_1`, `False`) nu erau căutați deloc.

Rolurile citite aici = cele ale gărzii vechi (`_candidati`) + cele trei de mai sus. Cele trei detectoare:
  · DIACRITICE — declanșatorii vechi + cei noi; într-un șir mixt (care are deja diacritice) numai formele neambigue („sa” = „a sa”,
    „tine” = „pe tine”, „lipsa” = „lipsa X” articulat sunt corecte și fără diacritică).
  · COD — `nume_cu_underscore`, `modul.atribut`, `COD_CU_UNDERSCORE`, `False` / `None` / `True`, `între backtick-uri`.
  · MAJUSCULE — un cuvânt de 4+ litere scris integral cu majuscule, care nu e acronim (lista `ACRONIME`) și nu e între ghilimele
    (o valoare emisă, ex. „ADMINISTRATOR”). Accentul se pune prin formulare, nu prin strigăt.

NU se citesc: metadatele de cache (`Declaratie(rol=, sursa=, motiv=)` — documentație pentru dezvoltator), registrul de interpretări
(`registru_interpretari.py`, nu are ecran) și unealta de clasificare P4 (`p4_clasificare.py`, iese în terminal).
ECRANELE (JS): aceeași extracție de text afișat ca gardul de diacritice JS (`scan_js_text`), cu criteriul majusculelor și al
diacriticelor din șirurile mixte. Identificatorii de cod nu se caută în JS: extracția lasă bucăți de interpolare (`${s.aratate`).
LIMITĂ declarată: textul construit din bucăți în afara acestor roluri (un `"%s" % x` întors de o funcție și pus apoi în `limita`)
nu se vede.
"""
import ast
import glob
import io
import json
import os
import re

from core.test_diacritice_afisate import _DIAC, _DISPLAY_KEYS, _TRIGGERE, _candidati, _cuvinte

CHEI = set(_DISPLAY_KEYS) | {"temei_completitudine"}
LISTE_AFISATE = {"avertismente", "blocaje", "erori", "motive", "limite", "atentionari", "av"}   # `av`: d112 / bilanț (172)
FARA_ECRAN = {"core/registru_interpretari.py", "core/p4_clasificare.py"}
DECLARATII_CACHE = {"Declaratie", "_Dec"}
#: [Retest 2, pct.2] rolul `raise X("…")`: mesajul unei excepții de domeniu ajunge pe ecran (refuzul, `DateInvalide(str(e))`).
#: Excepțiile de PROGRAMATOR (invarianți interni) nu sunt text pentru contabil și nu se citesc.
EXCEPTII_DEV = {"RuntimeError", "TypeError", "KeyError", "AssertionError", "AfirmatieIncompleta", "NotImplementedError",
                "SystemExit", "ImportError", "AttributeError", "IndexError", "SchemaInvalida", "_SchemaInvalida"}

TRIGGERE = set(_TRIGGERE) | {"atentie", "apartin", "apartine", "apartinand", "incrucisat", "incrucisata", "incrucisate",
                             "verificari", "buna"}   # „Buna, Dobrescu!” (deficiența 198)
AMBIGUE = {"sa", "tine", "lipsa", "afara", "cheltuiala", "exista"}   # „în afara”, „cheltuiala X”, „a exista” — corecte
ACRONIME = {"ANAF", "IBAN", "OMFP", "OPANAF", "SPV", "CUI", "CIF", "CNP", "TVA", "DUK", "XML", "XSD", "PDF", "SAGA", "BNR", "CASS",
            "OUG", "CAEN", "EORI", "EUR", "RON", "USD", "REVISAL", "REGES", "INTRASTAT", "VIES", "HTTP", "JSON", "ONRC", "PFA", "SRL",
            "HORECA", "FIFO", "LIFO", "OSS", "IOSS", "NIR", "SEPA", "COR", "SAFT", "UBL", "CIUS", "BCR", "CEC", "DNF", "UIT", "SSM",
            "IMM", "ITM", "AMEF", "SMTP", "OAUTH", "HTML", "CSV", "UTC", "IBAN", "DIICOT", "WINMENTOR", "UNICEF", "CNAS", "FNUASS",
            "CAM", "CAS", "CMR", "RO", "AAAA", "XLSX", "GDPR", "ANRP", "IFRS", "AFSP", "HEAD", "ZIP", "SWIFT", "NACE",
            "YYYY", "SUPPLY", "CORRECTION", "MSEST", "IMCA", "DGRFP", "JPEG", "JPG", "PNG", "GIF", "WEBP"}   # ultimele trei: elemente ale structurii XML D398/D399 (OSS), numite ca în ANAF   # + numerele romane din citări (art.LXVI), vezi `majuscule`

_SNAKE = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
_PUNCT = re.compile(r"\b(?!(?:art|alin|lit|pct|nr|ex|etc|resp|max|min|instr|rd|cf|cca|str|bl|sc|ap|et|jud|tel|cod|pag)\.)"
                    r"[a-z_][a-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]{2,}\b")
_COD_MARE = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")
_LITERALE = re.compile(r"\b(?:False|None|True)\b")
_BACKTICK = re.compile(r"`[^`]+`")
_MAJ = re.compile(r"(?<![\w\"'«„“])([A-ZĂÂÎȘȚŞŢ]{2,})(?![\w\"'»”])")
#: cuvinte scurte de accent („NU”, „ȘI”) — sub 4 litere numai acestea; restul de 2-3 litere sunt acronime (CF, UE, PF, IC)
SCURTE = {"NU", "ȘI", "CU", "LA", "CEA", "MAI", "DIN", "PE", "ÎN", "SAU", "DAR", "TOT"}   # nu „DE”/„UN”: cod de țară, UN/ECE
_DOMENIU = re.compile(r"\b[\w.-]+\.(?:eu|ro|com|gov\.ro)\b|\bhttps?://\S+")


def _lit(node):
    return [(x.lineno, x.value) for x in ast.walk(node) if isinstance(x, ast.Constant) and isinstance(x.value, str)]


def _nume_apel(f):
    return f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")


def _roluri_noi():
    out = []
    for fn in sorted(glob.glob("core/*.py")) + ["main.py"]:
        if fn.split("/")[-1].startswith("test_") or fn in FARA_ECRAN:
            continue
        out += roluri_din(open(fn, encoding="utf-8").read(), fn)
    return out


#: [Retest 2 pct.2] un `raise` de domeniu al cărui mesaj NU ajunge la contabil (argumentul greșit al unui apelant, un registru
#: din cod, pornirea serviciului) poartă pe linia lui `# invariant-intern-ok: <motiv>` — ca `# upsert-ok:`. Motivul e obligatoriu,
#: iar numărul lor are plafon: un marcaj nou se adaugă conștient, cu plafonul ridicat aici, nu se strecoară.
MARCAJ_INTERN = re.compile(r"#\s*invariant-intern-ok:\s*(\S.*)?$")
PLAFON_INVARIANTE = 27


def _intern(linii, n):
    m = MARCAJ_INTERN.search(linii[n.lineno - 1]) if 0 < n.lineno <= len(linii) else None
    return bool(m and m.group(1))


def _sabloane(arb):
    """[Retest 2] Numele legate de un text (`_MESAJ = ("Lipsă %s …")`, la nivel de modul sau de funcție): un mesaj construit
    `_MESAJ % x` n-are literalul în apel, iar gardul nu-l vedea (instanța: „LIPSĂ numele declarantului”, firma_profil_api)."""
    out = {}
    for n in ast.walk(arb):
        if (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)):
            out.setdefault(n.targets[0].id, []).append((n.value.lineno, n.value.value))
    return out


def _lit_cu_sabloane(node, sabloane):
    return _lit(node) + [x for nm in ast.walk(node) if isinstance(nm, ast.Name) for x in sabloane.get(nm.id, [])]


def roluri_din(src, fn="<sursa>"):
    out = []
    arb = ast.parse(src)
    linii = src.splitlines()
    sabloane = _sabloane(arb)
    for n in ast.walk(arb):
        if (isinstance(n, ast.Raise) and isinstance(n.exc, ast.Call) and n.exc.args
                and _nume_apel(n.exc.func) not in EXCEPTII_DEV and not _intern(linii, n)):
            out += [(fn, ln, s) for ln, s in _lit_cu_sabloane(n.exc.args[0], sabloane)]
        if isinstance(n, ast.Call) and _nume_apel(n.func) not in DECLARATII_CACHE:
            out += [(fn, ln, s) for kw in n.keywords if kw.arg in CHEI for ln, s in _lit(kw.value)]
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in ("append", "insert") and _nume_apel(f.value) in LISTE_AFISATE:
                out += [(fn, ln, s) for a in n.args for ln, s in _lit_cu_sabloane(a, sabloane)]
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            tinte = n.targets if isinstance(n, ast.Assign) else [n.target]
            if any(isinstance(t, ast.Name) and t.id.lower() in CHEI for t in tinte):   # `limita = …`, `LIMITA = …`
                out += [(fn, ln, s) for ln, s in _lit(n.value)]
        if isinstance(n, ast.Dict):
            out += [(fn, ln, s) for k, v in zip(n.keys, n.values)
                    if isinstance(k, ast.Constant) and k.value == "temei_completitudine" for ln, s in _lit(v)]
    return out


def texte_generatoare():
    """Textele din funcțiile de validare ale generatoarelor (`valideaza` / `erori*` din `core/d*.py`, `*engine*`, `bilant.py`) — același
    scop ca `test_mesaje_generare_fara_camp_intern` (care păzește, pe clichet, numele interne de câmp de acolo). Aici: numai diacriticele
    și majusculele (retest 08.10: „LIPSĂ CUI”, scris în `er.append`, nu în `erori.append`)."""
    from core import test_mesaje_generare_fara_camp_intern as M
    out = []
    for cale in M._fisiere():
        rel = "core/" + cale.replace("\\", "/").rsplit("/core/", 1)[-1]
        arb = ast.parse(open(cale, encoding="utf-8").read())
        doc = {id(n.value) for n in ast.walk(arb) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
        for fn in ast.walk(arb):
            if isinstance(fn, ast.FunctionDef) and M._fn_erori(fn.name):
                out += [(rel, x.lineno, x.value) for x in ast.walk(fn)
                        if isinstance(x, ast.Constant) and isinstance(x.value, str) and id(x) not in doc]
    return sorted(set(out))


def texte_afisate():
    return sorted({c for c in _candidati() if c[0] not in FARA_ECRAN} | set(_roluri_noi()))


def _e_proza(s):
    return " " in s.strip() and not re.search(r"\b(SELECT|INSERT|UPDATE|DELETE|CREATE|FROM|WHERE)\b", s) \
        and not re.search(r"<[A-Za-z/!?]", s)


#: [Retest 2, pct.2] lexiconul derivat din corpusul legislativ (`scripts/genereaza_lexicon_diacritice.py`): o formă ASCII care în
#: legislație apare (practic) numai cu diacritice. Lista scrisă de mână (`TRIGGERE`) prindea câteva zeci de cuvinte; un text pe
#: jumătate corectat („Ocupația … lucratoare”) trecea.
LEXICON = json.load(io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lexicon_diacritice.json"), encoding="utf-8"))


def fara_diacritice(s):
    if not _e_proza(s) or not any(c.islower() for c in s):
        return []
    cuv = set(_cuvinte(s))
    return sorted((cuv & (TRIGGERE - AMBIGUE if any(c in _DIAC for c in s) else TRIGGERE)) | set(cuvinte_lexicon(s))
                  | set(AFARA.findall(s)))


#: [Retest 2 pct.2] „în afară” urmat de un substantiv e „în afara” („în afara României”, „în afara intervalului”); „în afară” stă
#: numai înaintea lui „de” („în afară de”) sau la capăt de propoziție. Prinsă după corectarea în masă a diacriticelor din 09.10.
AFARA = re.compile(r"\b[îÎ]n afară(?=\s+(?!de\b)[\wăâîșțĂÂÎȘȚ])")


_CUV_INTREG = re.compile(r"[A-Za-zĂÂÎȘȚăâîșțŞŢşţ]+")


def cuvinte_lexicon(s):
    """Cuvintele ÎNTREGI, numai ASCII, pe care lexiconul le știe cu diacritice („străinătate” nu se taie în „str/in/tate”); nu și
    cele lipite de cod (`_`, `.`, `=`, backtick)."""
    out = []
    for m in _CUV_INTREG.finditer(s):
        w, a, b = m.group(0), m.start(), m.end()
        if not w.isascii() or (a and s[a - 1] in "_.=`") or (b < len(s) and s[b] in "_.=`("):
            continue
        if w.lower() in LEXICON and (w.islower() or w == w.capitalize()):
            out.append(w.lower())
    return out


def limbaj_de_cod(s):
    if not _e_proza(s):
        return []
    # `PERIOADA_BLOCATA: ` e eticheta de protocol a excepției, tăiată înainte de afișare (main.py, handlerul 423;
    # control_incrucisat `.replace("PERIOADA_BLOCATA: ", "")`) — nu ajunge la contabil
    s2 = _DOMENIU.sub("", re.sub(r"^PERIOADA_BLOCATA: ", "", s))
    return (_SNAKE.findall(s2) + _PUNCT.findall(s2) + _COD_MARE.findall(s2) + _LITERALE.findall(s2)
            + _BACKTICK.findall(s2))


#: [Retest 2] o majusculă cu diacritică ÎN cuvânt („LipsĂ”, scris „Lips\\u0102” — d300, prins la proba de ecran din 09.10)
MAJ_IN_CUVANT = re.compile(r"\b[A-Za-zăâîșțĂÂÎȘȚ]*[a-zăâîșț][ĂÂÎȘȚŞŢ][A-Za-zăâîșțĂÂÎȘȚ]*\b")


def majuscule(s):
    if not _e_proza(s):
        return []
    return [m for m in _MAJ.findall(s) if e_accent(m)] + MAJ_IN_CUVANT.findall(s)


def e_accent(m):
    """Un cuvânt scris cu majuscule ca accent (nu acronim, nu număr roman dintr-o citare)."""
    return m not in ACRONIME and not re.fullmatch(r"[IVXLCDM]+", m) and (len(m) >= 4 or m in SCURTE)


def jargon(s):
    """[deficiența 172, retestul Costin 09.10.2026: „limbajul de programator a rămas … «rânduri persistate», «-> nimic de comparat.
    GRI, nu roșu»”] Aceleași forme pe care le judecă ecranul (`core/limba_ecran.py`: jargonul de dezvoltator, săgeata `->`, stările
    interne „GRI”/„NEVERIFICAT”, trimiterile la proveniența internă) — o singură listă, citită de amândouă. Gardul de sursă nu le
    căuta, deci textele care apar pe ecran numai pe o ramură rară (o depunere fără rânduri salvate) treceau de el."""
    if not _e_proza(s):
        return []
    from core import limba_ecran as _le   # import târziu: limba_ecran citește constantele de aici
    return _le._JARGON.findall(s) + _le._SAGEATA.findall(s) + _le._INTERN.findall(s)


#: [deficiența 172] migrările rulează din terminal (operatorul, `python -m core.migrari_registru ruleaza`), nu pe ecranul contabilului;
#: textele lor nu se judecă la jargon („schema invalidă” e pentru operator). Și: o migrare deja rulată NU se rescrie — registrul o
#: cheiază pe amprenta conținutului (`core.migrari_registru`), deci o corectură de text ar cere rularea ei din nou pe producție.
def _e_migrare(fn):
    return os.path.basename(fn).startswith("migrare_")


def defecte():
    out = []
    toate = texte_afisate()
    for fn, ln, s in toate:
        for fel, f in (("diacritice", fara_diacritice), ("cod", limbaj_de_cod), ("majuscule", majuscule), ("jargon", jargon)):
            if fel == "jargon" and _e_migrare(fn):
                continue
            gasit = f(s)
            if gasit:
                out.append((fn, ln, fel, gasit, s))
    for fn, ln, s in sorted(set(texte_generatoare()) - set(toate)):
        for fel, f in (("diacritice", fara_diacritice), ("majuscule", majuscule)):
            gasit = f(s)
            if gasit:
                out.append((fn, ln, fel, gasit, s))
    return out


def test_detectoarele_au_dinti():
    """Fiecare exemplu din comanda lui Costin e prins; proza corectă trece."""
    assert fara_diacritice("ATENTIE (D406): conturi care nu apartin normei")
    assert fara_diacritice("Unitate de măsură necunoscută; controlul incrucisat nu o vede")        # șir mixt
    assert not fara_diacritice("Factura sa nu are CUI, lipsa lui oprește declarația")              # „sa”/„lipsa” corecte
    assert fara_diacritice("locul prestării în afară României") == ["în afară"]                    # Retest 2: „în afara”
    assert not fara_diacritice("nimeni în afară de sondă și nimic în afară.")
    for s in ("Cota standard (common.COTE tva_standard) e valabilă", "d300 nu expune R3_1_1/R7_1_1 aici",
              "d100_fapt: trimestru fără venituri (False), nu None", "câmpurile partener_id și self_billing"):
        assert limbaj_de_cod(s), s
    assert not limbaj_de_cod("Conform CF art.146 alin.(5) și pct.12, vezi iConta.eu")
    assert majuscule("NEVERIFICAT: dacă D300 depus coincide") == ["NEVERIFICAT"]
    assert majuscule("ATENTIE: conturi EXCLUSE") == ["ATENTIE", "EXCLUSE"]
    assert not majuscule("emis implicit „ADMINISTRATOR” — OPANAF 206/2025, CAEN, ANAF, SAF-T, CF art.LXVI, UE")
    assert majuscule("facturile NU apar ȘI în D394") == ["NU", "ȘI"]
    assert majuscule("LipsĂ bancă — obligatorie la D300.") == ["LipsĂ"]                             # Retest 2
    assert not majuscule("iConta.eu și eFactura")
    assert crit_js("Se incarca…") and crit_js("Selecteaza firme"), "textul JS scris integral fără diacritice se vede"
    src = "_M = ('LIPSĂ %s (x).')\ndef f():\n    erori.append(_M % 'a')\n"
    assert {s for _fn, _ln, s in roluri_din(src)} >= {"LIPSĂ %s (x)."}, "mesajul din șablon se vede"


def test_rolurile_noi_vad_limitele_verdictului():
    """Rolurile care lipseau, fiecare probat separat pe un fragment: argument cu nume, atribuire, `+=`, `avertismente.append`,
    cheia `temei_completitudine`; iar metadatele de cache (`Declaratie(motiv=)`) rămân pe dinafară."""
    src = ("_rezultat(x, limita='r1')\nlimita = 'r2'\nlimita += 'r3'\nres.avertismente.append('r4')\n"
           "d = {'temei_completitudine': 'r5'}\nLIMITA = 'r6'\nDeclaratie(motiv='x1')\nraise ValueError('r7')\n"
           "raise RuntimeError('x2')\n")
    assert sorted(s for _fn, _ln, s in roluri_din(src)) == ["r1", "r2", "r3", "r4", "r5", "r6", "r7"]


def test_marcajul_intern_are_motiv_si_plafon():
    """Marcajul care scoate un `raise` din judecată are motiv scris și nu se înmulțește pe tăcute."""
    src = "raise ValueError('r1')  # invariant-intern-ok: argumentul apelantului\nraise ValueError('r2')  # invariant-intern-ok:\n"
    assert [s for _fn, _ln, s in roluri_din(src)] == ["r2"], "fără motiv, marcajul nu scoate mesajul din judecată"
    marcaje = []
    for fn in sorted(glob.glob("core/*.py")) + ["main.py"]:
        if not fn.split("/")[-1].startswith("test_"):
            marcaje += ["%s:%d" % (fn, i) for i, ln in enumerate(open(fn, encoding="utf-8"), 1) if MARCAJ_INTERN.search(ln)]
    goale = [m for m in marcaje if not MARCAJ_INTERN.search(open(m.split(":")[0], encoding="utf-8").read().splitlines()[int(m.split(":")[1]) - 1]).group(1)]
    assert not goale, "marcaj fără motiv: %s" % goale
    assert len(marcaje) <= PLAFON_INVARIANTE, "%d marcaje `invariant-intern-ok` (plafon %d):\n  %s" % (
        len(marcaje), PLAFON_INVARIANTE, "\n  ".join(marcaje))


def defecte_js():
    from core import test_diacritice_afisate as D
    # [Retest 2, 09.10.2026] diacriticele se cer și în textele scrise integral fără ele („Selecteaza firme”, „Se incarca…”) — până
    # azi se judecau numai șirurile care aveau deja o diacritică. Antetele de import (`cheie:antet`) sunt chei de format, nu text.
    return [(fn, ln, rol, s, h) for fn in D._js_files() for ln, rol, s, h in D.scan_js_text(open(fn, encoding="utf-8").read(), crit_js)
            if not rol.startswith("cheie:")]


def crit_js(s):
    return (majuscule(s) + fara_diacritice(s)) or None


def test_ecranele_fara_majuscule_de_accent():
    gasite = defecte_js()
    assert not gasite, "Text de ecran cu majuscule de accent / diacritice lipsă:\n" + "\n".join(
        "  %s:%d [%s] %s <- %r" % (fn, ln, rol, ",".join(h), s[:100]) for fn, ln, rol, s, h in gasite)


def test_textul_afisat_e_limba_romana():
    gasite = defecte()
    raport = "\n".join("  %s:%d  [%s] %s  <- %r" % (fn, ln, fel, ",".join(g), s[:110]) for fn, ln, fel, g, s in gasite)
    assert not gasite, "Text afișat contabilului în limbaj de programator / fără diacritice / cu majuscule:\n" + raport


#: [deficiența 204, retestul Costin 09.10.2026: „Fluturașul: titlul «Fluturas» fără diacritice”] textul pus în documentele PDF
#: (`Paragraph`, `drawString`) — fluturașul, chitanța, factura — nu trecea prin niciun rol de mai sus.
PDF_APELURI = {"Paragraph", "drawString", "drawCentredString", "drawRightString"}
#: titlul formularului tipizat se scrie cu majuscule, ca pe model (chitanța: OMFP 2634/2015, formularul 14-4-1 „CHITANȚĂ”) — nu e accent
TITLURI_FORMULAR = {"CHITANȚĂ"}


def texte_pdf():
    out = []
    for fn in sorted(glob.glob("core/*.py")):
        if fn.split("/")[-1].startswith("test_"):
            continue
        arb = ast.parse(open(fn, encoding="utf-8").read())
        chei = ({id(n.slice) for n in ast.walk(arb) if isinstance(n, ast.Subscript)}   # `c["mentiuni"]` e o cheie, nu text
                | {id(a) for n in ast.walk(arb) if isinstance(n, ast.Call) and _nume_apel(n.func) == "get" for a in n.args})
        for n in ast.walk(arb):
            if isinstance(n, ast.Call) and _nume_apel(n.func) in PDF_APELURI:
                out += [(fn, x.lineno, x.value) for a in n.args for x in ast.walk(a)
                        if isinstance(x, ast.Constant) and isinstance(x.value, str) and id(x) not in chei and len(x.value) > 3]
    return out


def test_textul_din_pdf_e_limba_romana():
    """MUTAȚIE: „Fluturaș” -> „Fluturas” în titlul fluturașului -> pică."""
    texte = texte_pdf()
    assert [s for _f, _l, s in texte if s.startswith("Fluturaș de salariu")], "anti-vacuu: titlul fluturașului nu e printre textele PDF"
    rele = [(fn, ln, g, s[:90]) for fn, ln, s in texte
            for g in [fara_diacritice(s) + cuvinte_lexicon(s) + [m for m in majuscule(s) if m not in TITLURI_FORMULAR] + jargon(s)] if g]
    assert not rele, "Text din PDF fără diacritice / cu majuscule de accent / jargon:\n" + "\n".join("  %s:%d %s <- %r" % r for r in rele)


#: [deficiența 198, retestul Costin 09.10.2026: „«Buna, Dobrescu!» e fără diacritice”] gardul JS de mai sus citește textul din șabloanele
#: de ecran; un literal pus într-o variabilă sau într-un obiect („Buna, ” + nume; `depusa: "1 declaratie depusa"`) nu trecea prin el.
#: Aici: orice literal JS care arată a proză (începe cu majusculă sau cifră, are spații, fără marcaj de cod).
_LIT_JS = re.compile(r'"((?:[^"\\\n]|\\.){4,})"|\'((?:[^\'\\\n]|\\.){4,})\'|`([^`$\n]{4,})`')
_PROZA_JS = re.compile(r"[A-ZĂÂÎȘȚ0-9][^{}<>#_=\\$|]*")
#: literale care nu sunt proză românească: un nume de font, rânduri de exemplu dintr-un fișier CSV de import, „pentru tine” (corect)
PROZA_JS_NU = {"Georgia, \"Times New Roman\", serif", "Multi-client, multi-utilizator, drepturi pe rol.", "Ce s-a depus la ANAF pentru tine"}


def proza_js_fara_diacritice():
    out = []
    for fn in sorted(glob.glob("static/js/**/*.js", recursive=True)):
        for i, ln in enumerate(io.open(fn, encoding="utf-8"), 1):
            for m in _LIT_JS.finditer(ln.split("// ", 1)[0]):
                s = (m.group(1) or m.group(2) or m.group(3)).strip()
                if (not re.search(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}", s) or not _PROZA_JS.fullmatch(s) or re.match(r"^(GET|POST|PUT|DELETE|PATCH) ", s)
                        or s in PROZA_JS_NU or re.match(r"^[\w .\-]+,[\w .\-]+,", s)):   # ultima: rând CSV de exemplu
                    continue
                g = fara_diacritice(s) + cuvinte_lexicon(s)
                if not g and len(s.split()) <= 3:   # un fragment scurt („Buna, ”) nu e „proză” pentru `fara_diacritice`: cuvânt cu cuvânt
                    g = [w.lower() for w in _CUV_INTREG.findall(s) if w.isascii() and w.lower() in (TRIGGERE - AMBIGUE)]
                if g:
                    out.append((fn, i, sorted(set(g)), s[:90]))
    return out


def test_literalele_js_in_proza_au_diacritice():
    """MUTAȚIE: „Bună, ” -> „Buna, ” în salutul de la logare -> pică."""
    rele = proza_js_fara_diacritice()
    assert not rele, "Text JS fără diacritice:\n" + "\n".join("  %s:%d %s <- %r" % r for r in rele)

