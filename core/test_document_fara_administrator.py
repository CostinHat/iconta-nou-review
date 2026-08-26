# -*- coding: utf-8 -*-
"""GARD [R66 (c), 26.08.2026]: un document care tipărește numele administratorului nu se produce
fără el — iar refuzul NUMEȘTE documentul și locul, nu doar refuză.

De ce există. Poarta exista deja în cod (`firma_profil_api.cere_administrator` → 422), dar era
probată doar prin faptul că **a picat un test existent** — adică printr-un accident, nu printr-o
probă. Costin: *„dacă cineva scoate apelul, testul acela ar putea trece din alt motiv, iar refuzul
dispare tăcut."*

Iar calibrarea e cerută pe partea care contează, tot a lui: *„probează că refuzul NUMEȘTE
documentul și locul, nu doar că refuză. Un refuz generic ar trece un test care verifică doar codul
422."*

CE FACE IMPOSIBIL: un producător de document care nu mai cere administratorul · un apel care nu
spune CE document se refuză (`cere_administrator(conn, "")` sau cu o variabilă în loc de un nume) ·
o rută care lasă `ValueError` să iasă ca 500 în loc de 422 · un mesaj care nu mai e compus din
`UNDE_ADMINISTRATOR`, adică nu mai spune unde se completează.

CUM ASERTEAZĂ: pe **noduri de AST** — apeluri, argumente literale, handlere de excepție — și pe
faptul că mesajul e **compus din constanta de loc**, nu că fraza conține un anumit șir. Același
tipar ca `cont_valid.UNDE_SE_CREEAZA` (clichetul 50 / METODA §23).

CE NU FACE, declarat: apără **două** documente, nu clasa. Alte artefacte care tipăresc date de
firmă nu sunt verificate, iar mulțimea lor n-a fost măsurată. Și nu probează pe date că ruta chiar
întoarce 422 — e o gardă pe structură.
"""
import ast
import io
import os

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# producătorii de document care tipăresc administratorul, și ruta care îi cheamă
_PRODUCATORI = {"core/adeverinta.py": "date_auto", "core/contracte_api.py": "genereaza_pdf"}
_RUTE = ("tenant_adeverinta", "contracte_genereaza")


def _arbore(cale):
    return ast.parse(io.open(os.path.join(_RAD, cale), encoding="utf-8").read())


def _apeluri_cere_administrator(arb):
    """[(document, e_literal)] pentru fiecare apel al gărzii găsit în arbore."""
    out = []
    for n in ast.walk(arb):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        nume = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
        if nume != "cere_administrator":
            continue
        doc = n.args[1] if len(n.args) > 1 else None
        e_literal = isinstance(doc, ast.Constant) and isinstance(doc.value, str)
        out.append((doc.value if e_literal else None, e_literal))
    return out


def test_ANTI_VACUU_producatorii_si_rutele_se_gasesc():
    """Fără asta, o redenumire ar face gardul să treacă pe o mulțime goală."""
    for cale, fn in _PRODUCATORI.items():
        nume = {n.name for n in ast.walk(_arbore(cale))
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
        assert nume >= {fn}, "`%s` a dispărut din %s" % (fn, cale)
    nume_main = {n.name for n in ast.walk(_arbore("main.py"))
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    lipsa = set(_RUTE) - nume_main
    assert not lipsa, "rute negăsite în main.py: %s" % sorted(lipsa)


def test_fiecare_document_cere_administratorul():
    rele = [c for c in _PRODUCATORI if not _apeluri_cere_administrator(_arbore(c))]
    assert not rele, (
        "documente care se produc fără să ceară numele administratorului: %s — "
        "ies cu un gol în locul lui" % rele)


def test_refuzul_NUMESTE_documentul():
    """Un refuz generic („nu se poate emite") ar trece un test care verifică doar codul 422.
    Aici se cere ca fiecare apel să spună, ca **literal**, ce document se refuză: dintr-o
    variabilă nu se poate ști, la citirea codului, că omul află numele documentului."""
    fara_nume = []
    for cale in _PRODUCATORI:
        for doc, e_literal in _apeluri_cere_administrator(_arbore(cale)):
            if not e_literal or not (doc or "").strip():
                fara_nume.append(cale)
    assert not fara_nume, (
        "apeluri care nu numesc documentul refuzat: %s — omul primește un refuz care nu spune "
        "ce anume n-a putut fi emis" % fara_nume)


def test_refuzul_SPUNE_UNDE_se_completeaza():
    """Structural: mesajul e COMPUS din `UNDE_ADMINISTRATOR`, nu conține o frază despre loc.
    Un mesaj rescris care ar pierde locul nu mai referă constanta, iar asta se vede în AST."""
    arb = _arbore("core/mesaje.py")
    compus_din = set()
    for n in ast.walk(arb):
        if isinstance(n, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "MESAJ_FARA_ADMINISTRATOR" for t in n.targets):
            compus_din = {x.id for x in ast.walk(n.value) if isinstance(x, ast.Name)}
    assert compus_din >= {"UNDE_ADMINISTRATOR"}, (
        "`MESAJ_FARA_ADMINISTRATOR` nu mai e compus din `UNDE_ADMINISTRATOR` (referă: %s) — "
        "refuzul poate să nu mai spună unde se completează" % sorted(compus_din))


def test_rutele_transforma_refuzul_in_422_nu_in_500():
    """Un `ValueError` scăpat din rută devine 500, adică «s-a stricat ceva», nu «lipsește ceva»."""
    arb = _arbore("main.py")
    fns = {n.name: n for n in ast.walk(arb)
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    rele = []
    for r in _RUTE:
        prinde = False
        for h in ast.walk(fns[r]):
            if not isinstance(h, ast.ExceptHandler):
                continue
            if h.type is None:
                continue
            tipuri = {x.id for x in ast.walk(h.type) if isinstance(x, ast.Name)}
            if "ValueError" not in tipuri:
                continue
            for c in ast.walk(h):
                if (isinstance(c, ast.Call) and getattr(c.func, "id", None) == "HTTPException"
                        and c.args and isinstance(c.args[0], ast.Constant)
                        and c.args[0].value == 422):
                    prinde = True
        if not prinde:
            rele.append(r)
    assert not rele, (
        "rute care nu transformă refuzul în 422: %s — omul primește «s-a stricat ceva» în loc de "
        "«lipsește ceva, uite unde se completează»" % rele)


_REFUZ_GENERIC = chr(10).join([
    "def date_auto(conn, schema, sid, an, luna):",
    "    fel = 'ceva'",
    "    _fpa.cere_administrator(conn, fel)",
    "    return {}",
])


def test_CALIBRARE_un_refuz_care_NU_numeste_documentul_e_prins():
    """Calibrare negativă pe exact forma pe care a cerut-o Costin: apelul **există**, deci un gard
    care ar verifica doar prezența lui — sau doar codul 422 — ar trece verde. Documentul vine
    dintr-o variabilă, deci refuzul nu-l poate numi."""
    apeluri = _apeluri_cere_administrator(ast.parse(_REFUZ_GENERIC))
    assert apeluri, "calibrarea nu mai vede niciun apel — proba și-a pierdut obiectul"
    assert not any(e_literal for _doc, e_literal in apeluri), (
        "un document dat printr-o variabilă e acceptat ca «numit»: %s" % apeluri)
