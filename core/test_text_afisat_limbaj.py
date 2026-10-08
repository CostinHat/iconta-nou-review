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
import re

from core.test_diacritice_afisate import _DIAC, _DISPLAY_KEYS, _TRIGGERE, _candidati, _cuvinte

CHEI = set(_DISPLAY_KEYS) | {"temei_completitudine"}
LISTE_AFISATE = {"avertismente", "blocaje", "erori", "motive", "limite", "atentionari"}
FARA_ECRAN = {"core/registru_interpretari.py", "core/p4_clasificare.py"}
DECLARATII_CACHE = {"Declaratie", "_Dec"}

TRIGGERE = set(_TRIGGERE) | {"atentie", "apartin", "apartine", "apartinand", "incrucisat", "incrucisata", "incrucisate",
                             "verificari"}
AMBIGUE = {"sa", "tine", "lipsa", "afara", "cheltuiala", "exista"}   # „în afara”, „cheltuiala X”, „a exista” — corecte
ACRONIME = {"ANAF", "IBAN", "OMFP", "OPANAF", "SPV", "CUI", "CIF", "CNP", "TVA", "DUK", "XML", "XSD", "PDF", "SAGA", "BNR", "CASS",
            "OUG", "CAEN", "EORI", "EUR", "RON", "USD", "REVISAL", "REGES", "INTRASTAT", "VIES", "HTTP", "JSON", "ONRC", "PFA", "SRL",
            "HORECA", "FIFO", "LIFO", "OSS", "IOSS", "NIR", "SEPA", "COR", "SAFT", "UBL", "CIUS", "BCR", "CEC", "DNF", "UIT", "SSM",
            "IMM", "ITM", "AMEF", "SMTP", "OAUTH", "HTML", "CSV", "UTC", "IBAN", "DIICOT", "WINMENTOR", "UNICEF", "CNAS", "FNUASS",
            "CAM", "CAS", "CMR", "RO", "AAAA", "XLSX", "GDPR", "ANRP", "IFRS", "AFSP", "HEAD", "ZIP", "SWIFT", "NACE",
            "YYYY", "SUPPLY", "CORRECTION", "MSEST"}   # ultimele trei: elemente ale structurii XML D398/D399 (OSS), numite ca în ANAF   # + numerele romane din citări (art.LXVI), vezi `majuscule`

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


def roluri_din(src, fn="<sursa>"):
    out = []
    arb = ast.parse(src)
    for n in ast.walk(arb):
        if isinstance(n, ast.Call) and _nume_apel(n.func) not in DECLARATII_CACHE:
            out += [(fn, ln, s) for kw in n.keywords if kw.arg in CHEI for ln, s in _lit(kw.value)]
            f = n.func
            if isinstance(f, ast.Attribute) and f.attr in ("append", "insert") and _nume_apel(f.value) in LISTE_AFISATE:
                out += [(fn, ln, s) for a in n.args for ln, s in _lit(a)]
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


def fara_diacritice(s):
    if not _e_proza(s) or not any(c.islower() for c in s):
        return []
    cuv = set(_cuvinte(s))
    return sorted(cuv & (TRIGGERE - AMBIGUE if any(c in _DIAC for c in s) else TRIGGERE))


def limbaj_de_cod(s):
    if not _e_proza(s):
        return []
    # `PERIOADA_BLOCATA: ` e eticheta de protocol a excepției, tăiată înainte de afișare (main.py, handlerul 423;
    # control_incrucisat `.replace("PERIOADA_BLOCATA: ", "")`) — nu ajunge la contabil
    s2 = _DOMENIU.sub("", re.sub(r"^PERIOADA_BLOCATA: ", "", s))
    return (_SNAKE.findall(s2) + _PUNCT.findall(s2) + _COD_MARE.findall(s2) + _LITERALE.findall(s2)
            + _BACKTICK.findall(s2))


def majuscule(s):
    if not _e_proza(s):
        return []
    return [m for m in _MAJ.findall(s) if e_accent(m)]


def e_accent(m):
    """Un cuvânt scris cu majuscule ca accent (nu acronim, nu număr roman dintr-o citare)."""
    return m not in ACRONIME and not re.fullmatch(r"[IVXLCDM]+", m) and (len(m) >= 4 or m in SCURTE)


def defecte():
    out = []
    toate = texte_afisate()
    for fn, ln, s in toate:
        for fel, f in (("diacritice", fara_diacritice), ("cod", limbaj_de_cod), ("majuscule", majuscule)):
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
    for s in ("Cota standard (common.COTE tva_standard) e valabilă", "d300 nu expune R3_1_1/R7_1_1 aici",
              "d100_fapt: trimestru fără venituri (False), nu None", "câmpurile partener_id și self_billing"):
        assert limbaj_de_cod(s), s
    assert not limbaj_de_cod("Conform CF art.146 alin.(5) și pct.12, vezi iConta.eu")
    assert majuscule("NEVERIFICAT: dacă D300 depus coincide") == ["NEVERIFICAT"]
    assert majuscule("ATENTIE: conturi EXCLUSE") == ["ATENTIE", "EXCLUSE"]
    assert not majuscule("emis implicit „ADMINISTRATOR” — OPANAF 206/2025, CAEN, ANAF, SAF-T, CF art.LXVI, UE")
    assert majuscule("facturile NU apar ȘI în D394") == ["NU", "ȘI"]


def test_rolurile_noi_vad_limitele_verdictului():
    """Rolurile care lipseau, fiecare probat separat pe un fragment: argument cu nume, atribuire, `+=`, `avertismente.append`,
    cheia `temei_completitudine`; iar metadatele de cache (`Declaratie(motiv=)`) rămân pe dinafară."""
    src = ("_rezultat(x, limita='r1')\nlimita = 'r2'\nlimita += 'r3'\nres.avertismente.append('r4')\n"
           "d = {'temei_completitudine': 'r5'}\nLIMITA = 'r6'\nDeclaratie(motiv='x1')\n")
    assert sorted(s for _fn, _ln, s in roluri_din(src)) == ["r1", "r2", "r3", "r4", "r5", "r6"]


def defecte_js():
    from core import test_diacritice_afisate as D
    crit = lambda s: (majuscule(s) + [x for x in fara_diacritice(s) if any(c in _DIAC for c in s)]) or None   # noqa: E731
    return [(fn, ln, rol, s, h) for fn in D._js_files() for ln, rol, s, h in D.scan_js_text(open(fn, encoding="utf-8").read(), crit)]


def test_ecranele_fara_majuscule_de_accent():
    gasite = defecte_js()
    assert not gasite, "Text de ecran cu majuscule de accent / diacritice lipsă:\n" + "\n".join(
        "  %s:%d [%s] %s <- %r" % (fn, ln, rol, ",".join(h), s[:100]) for fn, ln, rol, s, h in gasite)


def test_textul_afisat_e_limba_romana():
    gasite = defecte()
    raport = "\n".join("  %s:%d  [%s] %s  <- %r" % (fn, ln, fel, ",".join(g), s[:110]) for fn, ln, fel, g, s in gasite)
    assert not gasite, "Text afișat contabilului în limbaj de programator / fără diacritice / cu majuscule:\n" + raport
