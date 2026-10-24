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
from core import scan_sql_efectiv as _efectiv

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Cele două căi de PRODUCȚIE, numite. Un al treilea nume aici cere o decizie, nu o completare.
ASTEPTATE = {
    ("core/facturi_api.py", "creeaza_factura"),
    # [P7 · valul use-case, 13.09.2026] `_factura_din_parsat` a plecat din `main.py` in stratul
    # use-case, cu corpul neatins. Calea e ACEEASI — se schimba numai fisierul in care locuieste.
    ("core/uc_comun.py", "_factura_din_parsat"),
    # [lotul 12, deficiența 252] A treia ușă, DECISĂ: facturile deschise preluate din programul vechi (situația clienților /
    # furnizorilor). Nu e o emitere și nu e un import de document: rândul e `tip = 'preluata'`, fără linii și fără TVA, iar soldul
    # lui e deja în balanța de deschidere — o notă l-ar înregistra a doua oară, deci contarea îl refuză (`contare_facturi`,
    # `SOLD_PRELUAT`). Prin `_factura_din_parsat` n-ar putea trece: acolo o emisă devine `de_recunoscut`, iar recunoașterea scrie
    # notă. Că rândul chiar e `preluata` o verifică `test_calea_preluarii_scrie_numai_facturi_preluate`.
    ("core/solduri_parteneri_api.py", "_scrie_documente"),
}
#: [252] calea care scrie numai facturi deschise preluate (nu documente fiscale) — nu ocolește actul de emitere, n-are ce emite
CALEA_PRELUARII = ("core/solduri_parteneri_api.py", "_scrie_documente")
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


def test_o_factura_se_naste_din_EXACT_trei_locuri_in_productie(productie):
    """Miezul, și răspunsul la HHH1. `creeaza_factura` e actul care produce nota automat (R87);
    `_factura_din_parsat` e calea de import, declarată ca excepție lângă cod; `_scrie_documente` scrie numai facturi deschise
    preluate (252, decizie — vezi `ASTEPTATE`). **A patra ușă cere o decizie, nu o completare** — vezi R91."""
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
               if (f, fn) not in {("core/facturi_api.py", "creeaza_factura"), CALEA_PRELUARII}}
    assert ocolesc == {("core/uc_comun.py", "_factura_din_parsat")}, ocolesc


def test_calea_preluarii_scrie_numai_facturi_preluate():
    """[lotul 12, 252] Calea preluării iese din întrebarea HHH1 numai fiindcă nu naște un document fiscal. Se verifică pe AST, nu pe
    proză: singurul INSERT în `facturi` din `_scrie_documente` pune coloana `tip` pe `_TIP_PRELUAT`, iar constanta e chiar
    `TIP_SOLD_PRELUAT` din nomenclator — pe care contarea, stornarea, trimiterea o refuză. Altă valoare pe `tip` (o factură obișnuită
    scrisă pe aici) pică."""
    import ast
    from core import nomenclator_status_factura as _nsf, solduri_parteneri_api as _sp
    arb = ast.parse(open(os.path.join(_RAD, CALEA_PRELUARII[0]), encoding="utf-8").read())
    fn = next(n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef) and n.name == CALEA_PRELUARII[1])
    inserturi = [c for c in ast.walk(fn) if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                 and c.func.attr == "execute" and c.args and _s.e_insert_in_facturi(_s._literal(c.args[0]))]
    assert len(inserturi) == 1, "calea preluării are %d INSERT-uri în `facturi`, nu unul" % len(inserturi)
    sql, valori = _s._literal(inserturi[0].args[0]), inserturi[0].args[1]
    coloane = [c.strip().lower() for c in sql.split("(", 1)[1].split(")", 1)[0].split(",")]
    expresii = sql.split("VALUES", 1)[1].split("(", 1)[1].rsplit(")", 1)[0].split(",")
    poz = [i for i, e in enumerate(expresii) if e.strip() == "%s"]   # al câtelea parametru e fiecare coloană cu %s
    assert isinstance(valori, ast.Tuple)
    param_tip = valori.elts[poz.index(coloane.index("tip"))]
    assert isinstance(param_tip, ast.Name) and param_tip.id == "_TIP_PRELUAT", ast.dump(param_tip)
    assert _sp._TIP_PRELUAT == _nsf.TIP_SOLD_PRELUAT == "preluata"


def test_calea_de_import_are_ACUM_actul_ei_de_recunoastere():
    """[KKK3] Inventarul nu se mai citește la fel. Când s-a construit, `_factura_din_parsat` era o
    **scăpare declarată**: o cale prin care o factură emisă intra fără notă, iar absența era scrisă
    lângă cod. De la R91 e o cale **acoperită**, cu act propriu — `POST /facturi/{id}/recunoaste`.

    Gardul rămâne pinat pentru orice a PATRA cale: aia ar fi iar o scăpare, nu o cale.

    Se verifică pe AST, nu pe proză: actul există, cheamă generatorul de notă, iar calea de import
    scrie o stare care îl așteaptă."""
    import ast
    # [P7 · valul use-case] Corpul rutei traieste in `core/uc_*.py`; intrebarea e neatinsa.
    sursa = _efectiv.sursa_aplicatie()
    arb = ast.parse(sursa)
    functii = {n.name: n for n in ast.walk(arb)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    # Forma de mulțime, nu `in`: `>=` crapă dacă `functii` încetează să fie un dicționar, iar `in`
    # ar trece ca sub-șir (clichetul 50 / `scan_garzi_pe_text`).
    assert functii.keys() >= {"factura_recunoaste"}, "actul de recunoaștere nu mai există"
    apeluri = {c.func.attr for c in ast.walk(functii["factura_recunoaste"])
               if isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)}
    assert apeluri >= {"contabilizeaza"}, "actul nu mai scrie nota"
    stari = {c.value for c in ast.walk(functii["_factura_din_parsat"])
             if isinstance(c, ast.Constant) and isinstance(c.value, str)}
    assert stari >= {"de_recunoscut", "importata"}, (
        "calea de import nu mai distinge ciorna de recunoaștere de o factură primită importată")


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
