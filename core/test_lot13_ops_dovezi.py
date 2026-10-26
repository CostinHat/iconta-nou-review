# -*- coding: utf-8 -*-
"""[lotul 13, pachetul `ops`] Forma dovezilor pe copia firmelor de test (`frontend_test/dovada/dovezi_lot13_ops.json`) și a mutațiilor de
capăt la capăt (`frontend_test/e2e/mut_lot13_ops.json`): o dovadă cu un pas sau o verificare pe care unealta nu le știe ar cădea abia la
rulare; o mutație a cărei ancoră nu mai e în fișier (sau e de două ori) n-ar mai face testul ei roșu.
Temei: N/A — formă de unealtă (CLAUDE.md §4: „rezolvată” = dovadă pe ecran + test permanent în poartă)."""
import json
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOVEZI = os.path.join(RAD, "frontend_test", "dovada", "dovezi_lot13_ops.json")
MUTATII = os.path.join(RAD, "frontend_test", "e2e", "mut_lot13_ops.json")
FIRME_COPIE = {"tenant_9049", "tenant_9050", "tenant_9051", "tenant_9052", "tenant_9053", "tenant_9054", "tenant_9055", "tenant_9057"}


def _pasi():
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    import pasi
    return pasi


def test_dovezile_folosesc_numai_pasii_si_verificarile_uneltei():
    p = _pasi()
    d = json.load(open(DOVEZI, encoding="utf-8"))
    assert len(d) >= 10
    capturi = [x["captura"] for x in d]
    assert len(capturi) == len(set(capturi)), "captură cu același nume la două dovezi"
    for x in d:
        assert x["firma"] in FIRME_COPIE, x["nr"]
        assert x["descriere"] and x["captura"].endswith(".png"), x["nr"]
        for pas in x["pasi"]:
            assert [k for k in pas if k in p.PASI], (x["nr"], pas)
        for v in x["verifica"]:
            assert [k for k in v if k in p.VERIFICARI], (x["nr"], v)


def test_dovezile_pe_datele_dinainte_de_reparatie_au_vechi_in_nume():
    """CLAUDE.md §4: „inclusiv pe documentele create înainte de reparație” — captura lor poartă `vechi` (regula 3a)."""
    d = json.load(open(DOVEZI, encoding="utf-8"))
    assert {x["nr"] for x in d if "vechi" in x["captura"]} >= {"522", "518", "527", "533", "541", "516", "519", "670"}


def test_mutatiile_au_ancora_unica_si_testul_lor():
    m = json.load(open(MUTATII, encoding="utf-8"))
    teste = open(os.path.join(RAD, "frontend_test", "e2e", "e2e_lot13_ops.py"), encoding="utf-8").read()
    assert len(m) >= 20
    for x in m:
        assert open(os.path.join(RAD, x["fisier"]), encoding="utf-8").read().count(x["ancora"]) == 1, x["test"]
        assert x["inlocuire"] != x["ancora"]
        fis, nume = x["test"].split("::")
        assert fis == "frontend_test/e2e/e2e_lot13_ops.py" and ("def %s(" % nume) in teste, x["test"]


#: [lotul 13, valul 4] numerele pachetului `ops` care cer dovada pe copia firmelor de test (`core/test_deficiente.py`: „rezolvată” = test
#: e2e AL NUMĂRULUI + captură `<nr>_…_f<k>_….png`)
NUMERE_VAL4 = ("505", "506", "507", "508", "511", "512", "513", "514", "516", "517", "519", "520", "521", "522", "528", "529", "533",
               "548", "550", "552", "601", "631", "633", "670", "C116", "C129")
#: numerele al căror test e2e e în alt fișier al plasei (rândul din registru îl numește)
TEST_ALTUNDEVA = {"C116": "e2e_lot12_migr.py", "C129": "e2e_lot12_diverse.py"}


def test_fiecare_numar_are_captura_pe_firma_de_test():
    """Forma capturii din `core/test_deficiente._RE_CAPTURA`: numărul rândului la început, apoi firma copiei (`f1`…`f7`)."""
    import re
    d = json.load(open(DOVEZI, encoding="utf-8"))
    capturi = {}
    for x in d:
        for c in [x["captura"]] + [p["captura"] for p in x["pasi"] if "captura" in p]:
            capturi.setdefault(x["nr"], []).append(c)
    for nr in NUMERE_VAL4:
        forma = re.compile(r"^%s_(?:[a-z0-9]+_)*?f\d+(?:_[a-z0-9]+)*\.png$" % re.escape(nr.lower()))
        bune = [c for c in capturi.get(nr, []) if forma.match(c)]
        assert bune, "%s: nicio captură `%s_…_f<k>_….png` (are: %s)" % (nr, nr.lower(), capturi.get(nr))


def test_fiecare_numar_are_testul_lui_si_fiecare_test_mutatia_lui():
    """`test_def_505_507_508_…` acoperea numai 505 (`core/test_deficiente.plasa_e2e`): fiecare număr are testul lui, iar fiecare test din
    fișier are o mutație care îl face roșu."""
    import re
    src = open(os.path.join(RAD, "frontend_test", "e2e", "e2e_lot13_ops.py"), encoding="utf-8").read()
    teste = re.findall(r"^def (test_def_(\w+?)_[a-z]\w*)\(", src, re.M)
    numere = {re.match(r"(c?\d+)", n).group(1).upper() for _t, n in teste}
    for nr in NUMERE_VAL4:
        if nr in TEST_ALTUNDEVA:
            assert ("def test_def_%s_" % nr.lower()) in open(os.path.join(RAD, "frontend_test", "e2e", TEST_ALTUNDEVA[nr]), encoding="utf-8").read()
            continue
        assert nr in numere, "%s: niciun `test_def_%s_…` în e2e_lot13_ops.py" % (nr, nr.lower())
    cu_mutatie = {x["test"].split("::")[1] for x in json.load(open(MUTATII, encoding="utf-8"))}
    fara = sorted(t for t, _n in teste if t not in cu_mutatie)
    assert not fara, "teste fără mutație în mut_lot13_ops.json: %s" % fara
