# -*- coding: utf-8 -*-
"""GARD (interdicția 4): aritmetica fiscală din ecran nu diverge de cea din server.

CE FACE IMPOSIBIL: ca ecranul să arate un TVA pe care factura salvată nu-l are. Măsurat 23.08.2026,
pe date obișnuite: o factură de **50 de rânduri × 3 × 19,99 la 21%** → serverul salvează **629,50**,
ecranul arăta **629,69**. Cauza: serverul rotunjește **pe linie** (`Decimal.quantize`, ROUND_HALF_UP),
iar ecranul aduna în `float` și rotunjea o singură dată, la afișare.

CE NU FACE, declarat — și e partea care contează: **nu scoate regula fiscală din stratul de
prezentare.** Calculul rămâne duplicat în JS, deci rămâne netestat pe cale reală, negardat și
neversionat pe dată — chiar interdicția 4. Gardul oprește **cifra greșită**, nu **duplicarea**;
pentru a doua e nevoie de o cale prin server, iar aia e restanță.

DE CE E UN TEST PYTHON PENTRU COD JS: reproduce **cele două aritmetici** pe aceleași date și cere să
dea la fel, plus verifică pe SURSA JS că rotunjirea pe linie e chiar acolo. Un test care ar rula JS
ar cere un motor de browser în poartă; unul care doar citește sursa n-ar prinde divergența numerică.
Amândouă, împreună, o prind.
"""
import io
import os
import re
from decimal import ROUND_HALF_UP, Decimal

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(_RAD, "static", "js", "ecrane")


# [lotul 11, decizia Costin 10.3: „Rotunjirea TVA: o singură regulă pe toată aplicația, cea cerută de validatorul e-Factura.”] Regula
# de pe 23.08.2026 (rotunjire pe LINIE) nu mai e a aplicației: TVA-ul se calculează pe COTĂ, din suma valorilor nete ale liniilor, rotunjit o
# dată (EN 16931 BR-DEC-23 / BR-S-08 / BR-CO-17, `core/tva_calcul.py`). Prinsă la trecerea pe regula unică: `_server` de aici reproducea
# „quantize pe linie” ca fiind `creeaza_factura`, dar `facturi_api.totaluri_din_linii` (cel care scrie TVA-ul pe factură) rotunjea o singură
# dată, la total — gardul compara ecranul cu o REPRODUCERE, nu cu serverul, și era verde peste divergența 629,50 (ecran) / 629,69 (factura).
# Acum `_server` e funcția reală a regulii, iar `_ecran` e chiar JS-ul ecranului (`tvaDocument`), rulat în Node.
def _server(linii):
    """TVA-ul documentului pe regula unică (`core/tva_calcul.py`) — sursa pe care o folosesc factura, PDF-ul, XML-ul și nota."""
    from core import tva_calcul as _tc
    return _tc.totaluri([{"cantitate": c, "pret_unitar": p, "cota_tva": k} for c, p, k in linii])["tva"]


def _ecran(linii):
    """Ce afișează ecranul: `tvaDocument` din `emitere_ecran.js` (folosit și de `facturi_ecran.js`), executat în Node."""
    import json
    import shutil
    import subprocess
    if not shutil.which("node"):
        pytest.skip("node lipsește")
    src = io.open(os.path.join(_JS, "emitere_ecran.js"), encoding="utf-8").read()
    m = re.search(r"const _BI = BigInt[^\n]*\nfunction _zec\(.*?\nexport function tvaDocument\(linii\) \{.*?\n\}\n", src, re.S)
    assert m, "tvaDocument a dispărut din emitere_ecran.js"
    js = m.group(0).replace("export function", "function") + "\nconsole.log(JSON.stringify(tvaDocument(%s)));" % json.dumps(
        [{"cantitate": str(c), "pret_unitar": str(p), "cota_tva": str(k)} for c, p, k in linii])
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    return Decimal(str(json.loads(r.stdout)["tva"])).quantize(Decimal("0.01"))


def _ecran_vechi(linii):
    """Forma de DINAINTE (23.08.2026 – lotul 11): rotunjire pe linie, apoi sumă. Ținută ca să se poată proba divergența."""
    tva = Decimal(0)
    for cant, pret, cota in linii:
        tva += (Decimal(str(cant)) * Decimal(str(pret)) * Decimal(str(cota)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return tva


CAZURI = [
    ("o linie obișnuită", [(1, 333.33, 21)]),
    ("două cote diferite", [(1, 100.00, 21), (1, 100.00, 11)]),
    ("douăzeci de rânduri mici", [(1, 0.07, 21)] * 20),
    ("factură de 50 de rânduri", [(3, 19.99, 21)] * 50),
    ("sută de rânduri", [(1, 12.34, 11)] * 100),
    ("cote amestecate", [(2, 9.99, 21), (1, 5.55, 11), (7, 1.11, 21), (1, 0.03, 11)] * 12),
]


@pytest.mark.parametrize("nume,linii", CAZURI)
def test_ecranul_da_ACEEASI_cifra_ca_serverul(nume, linii):
    assert _ecran(linii) == _server(linii), (
        "%s: ecranul %s, serverul %s — contabilul ar vedea un total pe care factura nu-l are"
        % (nume, _ecran(linii), _server(linii)))


def test_ANTIVACUU_forma_veche_CHIAR_diverge():
    """Fără asta, testul de mai sus ar putea trece fiindcă niciun caz nu discriminează. Se probează
    că datele alese chiar prind defectul reparat."""
    divergente = [(n, _ecran_vechi(l) - _server(l)) for n, l in CAZURI if _ecran_vechi(l) != _server(l)]
    assert len(divergente) >= 2, (
        "niciun caz nu mai discriminează — cazurile de probă s-au tocit: %r" % divergente)
    assert any(abs(d) >= Decimal("0.09") for _n, d in divergente), \
        "divergențele rămase sunt sub un ban; alege cazuri care chiar despart cele două aritmetici"


@pytest.mark.parametrize("fisier", ["emitere_ecran.js", "facturi_ecran.js"])
def test_ecranele_calculeaza_tva_cu_regula_unica(fisier):
    """[lotul 11] Ambele ecrane cu totaluri de factură trec prin `tvaDocument` (oglinda regulii unice) și nu mai rotunjesc TVA-ul pe linie."""
    src = io.open(os.path.join(_JS, fisier), encoding="utf-8").read()
    from core.arbore_js import apeluri, arbore_js
    arb, cod = arbore_js(fisier)   # apelul ca nod acorn, nu șirul în sursă (core/test_garzi_pe_text.py)
    assert apeluri(arb, cod, "tvaDocument"), "%s nu mai calculează TVA-ul cu tvaDocument (regula unică, decizia 10.3)" % fisier
    assert not re.search(r"tva \+?= Math\.round\(|const tva = Math\.round\(", src), (
        "%s rotunjește iar TVA-ul pe linie — altă regulă decât factura, PDF-ul și e-Factura" % fisier)


def test_nicio_ALTA_aritmetica_de_cota_fara_rotunjire_in_ecrane():
    """Clichet: o a treia formulă de TVA apărută în prezentare, fără rotunjire pe linie, pică."""
    rele, rotunjite = [], 0
    for f in sorted(os.listdir(_JS)):
        if not f.endswith(".js"):
            continue
        src = io.open(os.path.join(_JS, f), encoding="utf-8").read()
        for i, linie in enumerate(src.split("\n"), 1):
            if not re.search(r"\bcota\w*\s*/\s*100|\*\s*cota\w*\s*/\s*100", linie):
                continue
            if linie.strip().startswith("//"):
                continue
            if re.search(r"\bMath\.round\s*\(", linie):   # apelul de rotunjire pe același rând (nu „șirul apare”, garzi_pe_text)
                rotunjite += 1
                continue
            rele.append("  %s:%d %s" % (f, i, linie.strip()[:90]))
    # anti-vacuu: scanul chiar vede aritmetica de cotă rotunjită (formulele de azi); zero ar însemna că regexul nu mai prinde nimic
    assert rotunjite > 0, "scanul nu vede nicio aritmetică de cotă în %s — regexul s-a rupt" % _JS
    assert not rele, ("aritmetică de cotă fără rotunjire pe linie, în stratul de prezentare:\n"
                      + "\n".join(rele) + "\n\nVezi interdicția 4: regula fiscală n-are ce căuta în "
                      "ecran; până se scoate, măcar să nu dea altă cifră decât serverul.")


# ─────────────────────────────────────────────────────────────────────────────
# CALIBRAREA PE NUME NEUTRE, ca CIFRA PAZITA (24.08.2026).
#
# NOTA, dintr-o greseala proprie de acum cinci minute: constanta de mai jos se
# numeste `_JS_TOT`, nu `_JS`, fiindca `_JS` EXISTA deja in acest fisier si
# arata spre `static/js/ecrane`. Redefinirea a schimbat tacit ce masurau doua
# garzi vechi, iar ele au picat cu «fisier inexistent». Un nume reciclat intr-un
# fisier de garzi nu e o scapare de stil: muta domeniul altui gard.
#
# Costin, de doua ori: «cifra "N formule" e plafon inferior pana la calibrarea pe
# nume neutre, iar noi am tratat-o ca lista completa». Masuratoarea s-a facut si a
# dat ZERO — dar o masuratoare care traieste intr-un raport se uita. Aici devine
# test: daca cineva scrie o formula fiscala pe `a`, `val`, `x`, cifra creste si
# gardul o numeste.
#
# CE NU VEDE, declarat: o formula fara nicio cifra literala; una intinsa pe mai
# multe randuri; una construita din siruri.
import os as _os
import re as _re

_JS_TOT = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                    "static", "js")
_COTA = _re.compile(r"(?<![\w.])(0\.(19|21|10|25|16|09|05|08)|19|21|10|25|16|121|119|110|105)(?![\w.])")
_ARIT = _re.compile(r"[*/]|\bMath\.round\b")
_FISCAL = _re.compile(r"(?i)\b\w*(tva|cota|baza|impozit|cas|cass|net|brut|deduc|plafon|"
                      r"acciz|contrib|taxa|scutit)\w*")

# Ramane UNA, aritmetica pe DATE calendaristice, nu fiscala:
#   facturi_ecran.js  — `Date.now() + 30 * 864e5`
#
# COBORAT 2→1 pe 04.09.2026, si nu fiindca s-a reparat ceva in ecrane: a doua instanta
# (`api.js`, `slice(0, 10)` peste o potrivire de data) era o ACUZATIE FALSA a cititorului
# vechi — „aritmetica" erau barele expresiei regulate din `.match(/…/)`, iar „cota" era
# 10-le din `slice`. Cititorul reparat albeste expresiile regulate, deci instanta dispare.
# Masurat in amandoua felurile pe acelasi commit `277e4300`: cititor vechi 2, reparat 1.
#
# COBORAT 1→0 pe 05.10.2026, tot fără reparație fiscală: instanța rămasă (`facturi_ecran.js`, `Date.now() + 30 * 864e5`)
# avea drept „cotă” același `10` din `.toISOString().slice(0, 10)` de pe rând. Clasa DATA_UTC (DS cap.4 v2.68) a înlocuit
# forma cu `dataIso(...)`, deci rândul nu mai poartă niciun literal de cotă.
NUME_NEUTRE_CLICHET = 0


# Cititorul e COMUN din 04.09.2026 (`core/cititor_js.py`). Copia care traia aici purta
# acelasi defect ca sora ei din `scan_refuz_tacut.py`: un sir `'` sau `"` neinchis pe
# randul lui albea tot pana la urmatoarea ghilimea din fisier. Din cauza lui, clichetul
# de mai sus a numarat pe `api.js:366` o „aritmetica" care erau chiar barele unei
# EXPRESII REGULATE: `full.slice(0, 10).match(/^(\\d{4})-(\\d{2})-(\\d{2})$/)`.
from core.cititor_js import fara_siruri as _fara_comentarii_si_siruri


def _aritmetica_pe_nume_neutre():
    """(fisier, linie, text) — aritmetica cu cota literala, FARA nume fiscal pe linie."""
    gasite = []
    for rad, _, nume in _os.walk(_JS_TOT):
        for f in sorted(nume):
            if not f.endswith(".js"):
                continue
            cale = _os.path.join(rad, f)
            src = io.open(cale, encoding="utf-8").read()
            orig = src.split("\n")
            curat = _fara_comentarii_si_siruri(src)
            assert len(curat.split("\n")) == len(orig), cale   # anti-derapaj
            for nr, linie in enumerate(curat.split("\n"), 1):
                if _COTA.search(linie) and _ARIT.search(linie) and not _FISCAL.search(linie):
                    gasite.append((_os.path.relpath(cale, _JS_TOT), nr, orig[nr - 1].strip()))
    return gasite


def test_curatarea_pastreaza_numerotarea():
    """CALIBRARE pe modul propriu de esec: daca taierea colapseaza liniile, tot ce
    raporteaza gardul trimite omul la locul gresit."""
    s = 'const a = 1;\n// comentariu\n/* pe\ndoua */\nconst b = "sir\ncu newline";\nconst c = 2;\n'
    assert len(_fara_comentarii_si_siruri(s).split("\n")) == len(s.split("\n"))


def test_tiparul_prinde_o_formula_scrisa_pe_nume_neutre():
    """CALIBRARE POZITIVA — chiar cazul de care se temea Costin."""
    linie = "  const x = a * 21 / 100;"
    assert _COTA.search(linie) and _ARIT.search(linie) and not _FISCAL.search(linie)


def test_CALIBRARE_template_imbricat_ramane_SIR():
    """Direcția «acuză pe nedrept». Forma care a doborât cititorul vechi: un template literal cu
    interpolare care conține alt template literal. Tot ce e text trebuie să rămână text."""
    js = "const h = `<ul>${a.map((u) => `<li>Total 21% (bere)</li>`).join(\"\")}</ul>`;"
    curat = _fara_comentarii_si_siruri(js)
    assert curat.count("21%") == 0, (
        "HTML dintr-un template imbricat a scapat ca fiind cod: %r" % curat)
    assert len(curat) == len(js), "cititorul a schimbat lungimea — numerele de linie ar sari"


def test_CALIBRARE_aritmetica_din_interpolare_RAMANE_VIZIBILA():
    """Direcția care contează mai mult: ce e între `${` și `}` **e cod**. Dacă cititorul l-ar
    înghiți ca șir, o cotă scrisă acolo ar trece nevăzută — iar gardul ar fi liniștit degeaba."""
    js = "const h = `TVA: ${suma * 21 / 100}`;"
    curat = _fara_comentarii_si_siruri(js)
    assert curat.count("* 21 / 100") == 1, (
        "aritmetica din interpolare a fost înghițită ca șir: %r" % curat)
    assert curat.count("TVA:") == 0, "textul din jurul interpolării trebuia albit: %r" % curat


def test_CALIBRARE_apostroful_dintr_un_sir_nu_deschide_alt_sir():
    """Un `'` scăpat într-un șir cu ghilimele duble nu trebuie să defazeze cititorul."""
    js = 'const a = "n-ar trebui"; const b = x * 21 / 100;'
    curat = _fara_comentarii_si_siruri(js)
    assert curat.count("* 21 / 100") == 1, curat


def test_nicio_formula_noua_pe_nume_neutre():
    """CLICHET. Masurat 24.08.2026: 2, ambele calendaristice. Zero fiscale."""
    g = _aritmetica_pe_nume_neutre()
    assert len(g) <= NUME_NEUTRE_CLICHET, (
        "aritmetica noua cu cota literala pe nume neutre — daca e fiscala, scanul de "
        "formule NU o vede:\n" + "\n".join("  %s:%d  %s" % x for x in g))


def test_clichetul_de_nume_neutre_nu_ramane_peste_realitate():
    g = _aritmetica_pe_nume_neutre()
    if len(g) < NUME_NEUTRE_CLICHET:
        raise AssertionError("sunt doar %d — coboara NUME_NEUTRE_CLICHET la %d" % (len(g), len(g)))
