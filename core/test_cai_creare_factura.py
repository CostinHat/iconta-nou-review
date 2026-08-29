# -*- coding: utf-8 -*-
"""GARDA inventarului de căi prin care se naște o factură (HHH1). Instrumentul:
`core/scan_cai_factura.py`.

CE FACE IMPOSIBIL: ca o a TREIA cale de creare a unei facturi să apară TĂCUT în producție. R87 a
legat nota contabilă de `facturi_api.creeaza_factura` — punctul unic prin care trec toate emiterile
aplicației. Afirmația *„unic"* e adevărată doar cât timp nimeni nu mai deschide o ușă.

DE CE INSTRUMENTUL E SEPARAT: calibrarea lui are nevoie de mostre de SQL, iar mostrele într-un fișier
`test_*` se aprind în două gărzi care n-au nicio treabă cu subiectul — `test_schema_coloane` (o
coloană inventată într-un SQL de probă) și `test_garzi_pe_text` (căutare de șiruri). *Măsurat: prima
formă a fișierului ăstuia le-a aprins pe amândouă.*

CE NU FACE, DECLARAT: nu verifică dacă o cale nouă **ar trebui** să contabilizeze automat — asta e o
decizie, și e chiar R91. Verifică doar că nu apare una fără să se vadă.
"""
import os

import pytest

from core import scan_cai_factura as _s

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cele două căi de PRODUCȚIE, numite. Un al treilea nume aici cere o decizie, nu o completare.
ASTEPTATE = {
    ("core/facturi_api.py", "creeaza_factura"),
    ("main.py", "_factura_din_parsat"),
}
# Clichetul l-a dat INSTRUMENTUL, nu numărătoarea mea de dinainte: numărasem 4 (fișiere), el numără
# 5 (funcții) — `firma_grea_audit.py` are trei locuri care inserează facturi.
CLICHET_SEED = 5


@pytest.fixture(scope="module")
def productie():
    return _s.cai(_RAD, doar=lambda r: (r == "main.py" or r.startswith("core/"))
                  and not os.path.basename(r).startswith("test_")
                  and os.path.basename(r) != "scan_cai_factura.py")


def test_cititorul_chiar_distinge_tabelele():
    """ANTI-VACUU și calibrare în ambele direcții. Fără el, un `e_insert_in_facturi` care ar întoarce
    mereu False ar face inventarul gol, iar gardul ar trece raportând despre o lume pe care n-o vede.
    Iar unul care ar întoarce mereu True ar înghiți `factura_linii` și `facturi_recurente` — două
    tabele care încep chiar cu numele căutat."""
    da, nu = _s.calibrare()
    assert da == len(_s.MOSTRE_DA), "instrumentul nu recunoaște toate formele de INSERT în `facturi`"
    assert nu == len(_s.MOSTRE_NU), "instrumentul confundă `facturi` cu tabelele vecine"


def test_o_factura_se_naste_din_EXACT_doua_locuri_in_productie(productie):
    """Miezul, și răspunsul la HHH1. `creeaza_factura` e actul care produce nota automat (R87);
    `_factura_din_parsat` e calea de import, declarată ca excepție lângă cod. **A treia ușă cere o
    decizie, nu o completare** — vezi R91."""
    gasite = set(productie)
    assert gasite == ASTEPTATE, (
        "căile prin care se naște o factură în PRODUCȚIE s-au schimbat."
        "  așteptate: %s ·  găsite: %s. "
        "Dacă e o cale nouă legitimă, ea trebuie să spună ce face cu nota contabilă (ZZ4: automat, "
        "sau excepție DECLARATĂ lângă cod) — și abia apoi să intre aici."
        % (sorted(ASTEPTATE), sorted(gasite)))


def test_calea_de_import_e_singura_care_ocoleste_actul_de_emitere(productie):
    """Formularea exactă a întrebării HHH1, citită din inventar, nu din memorie."""
    ocolesc = {(f, fn) for (f, fn) in productie
               if (f, fn) != ("core/facturi_api.py", "creeaza_factura")}
    assert ocolesc == {("main.py", "_factura_din_parsat")}, ocolesc


def test_seedurile_nu_cresc():
    """Fixturile scriu direct în tabele — ele sunt chiar motivul pentru care 19 note din 34 n-au
    `sursa` (măsurat la R36). Nu e un defect, dar nici nu poate crește tăcut: un seed nou care
    ocolește actul de emitere face baza de test tot mai puțin asemănătoare cu aplicația."""
    seed = _s.cai(os.path.join(_RAD, "date_test"))
    assert len(seed) <= CLICHET_SEED, (
        "seeduri care inserează direct în `facturi`: %d > %d — %s"
        % (len(seed), CLICHET_SEED, "; ".join("%s :: %s" % x for x in seed)))
    assert len(seed) == CLICHET_SEED, (
        "clichetul e mai larg decât realitatea — coboară-l la %d" % len(seed))
