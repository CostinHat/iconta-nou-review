# -*- coding: utf-8 -*-
"""GARD DE CLASA (04.08.2026, campania "reimprospatarea surselor invechite"): fiecare nomenclator care
ajunge la ANAF e ANCORAT PE VALIDATORUL INSTALAT, nu pe un document.

DE CE ancorare-pe-validator si NU un prag de vechime (N ani):
Vechimea NU e riscul. Un nomenclator din 2013 poate fi perfect CURENT (ex. D301 tipuri operatiune 1-5, inca
valide). Un document din 2025 poate fi depasit luna urmatoare. Riscul real e DIVERGENTA fata de validatorul
INSTALAT - exact ce au ascuns:
  - ASI (pdf D394 2020 avea 9 tipuri incl. ASI; validatorul J8 il respinsese demult - cod dupa document mort);
  - HRK (pdf D301 2013 avea 19 valute; validatorul D301_9 accepta 20 - cod mai strict decat validatorul).
Un prag de N ani ar rata AMBELE: nu erau despre varsta, ci despre ce ACCEPTA validatorul azi. De aceea gardul
nu se uita la date, ci cere ca fiecare pin de nomenclator sa fie PROBAT pe validator.

Gardul DESCOPERA (AST) constantele de forma nomenclator (set/tuple/frozenset de coduri scurte alfanumerice
majuscule) la nivel de modul in generatoarele care emit catre ANAF, si CERE ca fiecare sa aiba un test de
ancorare care atinge validatorul (proba DUK / snapshot validator-confirmat). O constanta noua fara ancora ->
gardul pica: te forteaza sa probezi validatorul instalat, NU sa copiezi un pdf.
"""
import ast
import importlib
import pathlib
import re

RAD = pathlib.Path(__file__).resolve().parent.parent
CORE = RAD / "core"
GENERATOARE = ["d100", "d101", "d112", "d205", "d300", "d301", "d390", "d394", "d406", "d710", "common"]

# Registru: (modul, CONSTANTA) -> test de ancorare pe VALIDATOR. Fiecare nomenclator care ajunge la ANAF
# trebuie sa fie aici, cu un test care il probeaza pe validatorul INSTALAT (nu doar pe un pdf/document).
# Constantele derivate (subseturi ale unui set deja ancorat) pot pointa pe testul parintelui.
ANCORE = {
    ("d301", "VALUTE"): "test_valute_ancorate_pe_validator_nu_pe_pdf_2013",
    ("d390", "TARI_UE"): "test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020",
    ("d390", "TIPURI"): "test_nomenclatoare_d390_ancorate_pe_validator_nu_pe_pdf_2020",
    ("d394", "TIPURI"): "test_TIPURI_e_setul_validatorului_curent",
    ("d394", "TIP_COTA_ZERO"): "test_TIPURI_e_setul_validatorului_curent",   # subset derivat din TIPURI
    ("d394", "REZ1_FARA_TVA"): "test_TIPURI_e_setul_validatorului_curent",   # subset derivat din TIPURI
    ("d394", "OP1_CU_TVA"): "test_TIPURI_e_setul_validatorului_curent",      # subset derivat din TIPURI
    ("d394", "_TARI_UE"): "test_tip_partener_clasificare_pct216",
    ("d406", "_UE_NON_RO"): "test_registration_number_partener_si_firma_proprie",
}


def _coduri_scurte(node):
    """Elementele daca node e un set/tuple/list/frozenset de string-uri scurte (1-4) alfanumerice majuscule
    (forma unui nomenclator de coduri). Altfel None."""
    elts = None
    if isinstance(node, (ast.Set, ast.Tuple, ast.List)):
        elts = node.elts
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "frozenset" and node.args:
        a = node.args[0]
        if isinstance(a, (ast.Set, ast.Tuple, ast.List)):
            elts = a.elts
    if not elts:
        return None
    vals = [e.value for e in elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
    if len(vals) < 3 or len(vals) != len(elts):
        return None
    if all(1 <= len(v) <= 4 and v.isupper() and v.isalnum() for v in vals):
        return vals
    return None


def _nomenclatoare_descoperite():
    """{(modul, NUME): [coduri]} - constantele de forma nomenclator din generatoare."""
    gasite = {}
    for mod in GENERATOARE:
        p = CORE / (mod + ".py")
        if not p.exists():
            continue
        tree = ast.parse(p.read_text(encoding="utf-8"))
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                vals = _coduri_scurte(node.value)
                if vals is not None:
                    gasite[(mod, node.targets[0].id)] = vals
    return gasite


_CACHE_TESTE = {}
def _corp_test(nume_test):
    """Sursa functiei de test `nume_test` din core/test_*.py (prima aparitie), sau None."""
    if not _CACHE_TESTE:
        for p in CORE.glob("test_*.py"):
            src = p.read_text(encoding="utf-8", errors="replace")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name not in _CACHE_TESTE:
                    _CACHE_TESTE[node.name] = ast.get_source_segment(src, node) or ""
    return _CACHE_TESTE.get(nume_test)


def test_fiecare_nomenclator_e_ancorat_pe_validator():
    """Fiecare constanta de forma nomenclator din generatoare are o intrare in ANCORE (test de ancorare pe
    validator). O constanta noua fara ancora pica aici - forteaza proba pe validator, nu copierea unui document."""
    descoperite = _nomenclatoare_descoperite()
    neancorate = sorted(k for k in descoperite if k not in ANCORE)
    assert not neancorate, (
        "nomenclatoare FARA ancora pe validator (adauga un test cu proba DUK pe validatorul instalat si "
        "inregistreaza-l in ANCORE - NU copia dintr-un pdf/document): %s" % neancorate)
    # (informativ) nu lasam intrari de registru pentru constante care au disparut din cod
    disparute = sorted(k for k in ANCORE if k not in descoperite)
    assert not disparute, "intrari ANCORE pentru constante care nu mai exista in cod (curata registrul): %s" % disparute


def test_ancorele_exista_si_ating_validatorul():
    """Fiecare test de ancorare din registru EXISTA, atinge VALIDATORUL/DUK in corp (nu doar un document), si
    constanta ancorata exista in modul."""
    for (mod, const), test in sorted(ANCORE.items()):
        corp = _corp_test(test)
        assert corp is not None, "testul de ancora %s (pt %s.%s) nu exista in core/test_*.py" % (test, mod, const)
        # Ancora trebuie sa atinga VALIDATORUL: fie jar-ul instalat (duk/validator/DUKIntegrator), fie
        # SPECIFICATIA oficiala masinala a validatorului (schema_anaf + validare sintactica) - cazul d406,
        # unde DUK e xfail preexistent, deci ancora e schema oficiala ANAF (curenta), nu un pdf derivat vechi.
        # NU accepta ancorarea pe un simplu document de structura invechit.
        assert re.search(r"\bduk\b|validator|DUKIntegrator|schema_anaf|validare sintactic", corp, re.IGNORECASE), (
            "ancora %s (pt %s.%s) nu atinge validatorul/DUK/schema oficiala in corp - ancorata pe document invechit?" % (test, mod, const))
        m = importlib.import_module("core." + mod)
        assert hasattr(m, const), "constanta ancorata %s.%s nu exista in modul" % (mod, const)
