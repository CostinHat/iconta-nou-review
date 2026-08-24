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


def _server(linii):
    """Ce face `creeaza_factura`: quantize pe LINIE, apoi sumă."""
    tva = Decimal("0.00")
    for cant, pret, cota in linii:
        baza = Decimal(str(cant)) * Decimal(str(pret))
        tva += (baza * Decimal(str(cota)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return tva


def _ecran(linii):
    """Ce face `recalc()` DUPĂ reparație: rotunjire pe linie, în float, apoi sumă."""
    tva = 0.0
    for cant, pret, cota in linii:
        tva += round((cant * pret) * (cota / 100.0) * 100) / 100
    return Decimal(str(round(tva, 2)))


def _ecran_vechi(linii):
    """Forma de DINAINTE: sumă nerotunjită. Ținută ca să se poată proba divergența."""
    tva = 0.0
    for cant, pret, cota in linii:
        tva += (cant * pret) * (cota / 100.0)
    return Decimal(str(round(tva, 2)))


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


@pytest.mark.parametrize("fisier,tipar", [
    ("emitere_ecran.js", r"tva \+= Math\.round\("),
    ("facturi_ecran.js", r"const tva = Math\.round\("),
])
def test_rotunjirea_pe_linie_e_CHIAR_in_sursa_JS(fisier, tipar):
    """Aritmetica de mai sus e o reproducere; asta verifică originalul. Dacă cineva scoate
    rotunjirea din JS, reproducerea ar rămâne verde și ar minți."""
    src = io.open(os.path.join(_JS, fisier), encoding="utf-8").read()
    assert re.search(tipar, src), (
        "%s nu mai rotunjește TVA-ul pe linie — ecranul poate diverge iar de server" % fisier)


def test_nicio_ALTA_aritmetica_de_cota_fara_rotunjire_in_ecrane():
    """Clichet: o a treia formulă de TVA apărută în prezentare, fără rotunjire pe linie, pică."""
    rele = []
    for f in sorted(os.listdir(_JS)):
        if not f.endswith(".js"):
            continue
        src = io.open(os.path.join(_JS, f), encoding="utf-8").read()
        for i, linie in enumerate(src.split("\n"), 1):
            if not re.search(r"\bcota\w*\s*/\s*100|\*\s*cota\w*\s*/\s*100", linie):
                continue
            if "Math.round" in linie or linie.strip().startswith("//"):
                continue
            rele.append("  %s:%d %s" % (f, i, linie.strip()[:90]))
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

# Cele doua sunt aritmetica pe DATE calendaristice, nu fiscala:
#   api.js            — `slice(0, 10)` peste o potrivire de data
#   facturi_ecran.js  — `Date.now() + 30 * 864e5`
NUME_NEUTRE_CLICHET = 2


def _fara_comentarii_si_siruri(src):
    """Scoate comentariile SI sirurile, PASTRAND newline-urile.

    Prima forma a acestei functii, 24.08.2026, colapsa liniile — deci raporta
    numere de linie ale ALTOR linii. De-aia exista aserttiunea de mai jos.
    """
    out, i, n = [], 0, len(src)
    while i < n:
        c, d = src[i], src[i:i + 2]
        if d == "//":
            j = src.find("\n", i)
            if j < 0:
                out.append(" " * (n - i))
                break
            out.append(" " * (j - i))
            i = j
        elif d == "/*":
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j]))
            i = j
        elif c in "\"'`":
            j, q = i + 1, c
            while j < n:
                if src[j] == "\\":
                    j += 2
                    continue
                if src[j] == q:
                    break
                j += 1
            j = min(j, n - 1)
            out.append("".join(ch if ch == "\n" else " " for ch in src[i:j + 1]))
            i = j + 1
        else:
            out.append(c)
            i += 1
    return "".join(out)


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
