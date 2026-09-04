# -*- coding: utf-8 -*-
r"""GARD [04.09.2026]: cititorul comun de JS nu poate orbi tacut peste cod real.

DE UNDE VINE. Doua instrumente stateau pe cate o COPIE a aceluiasi cititor, si copiile purtau
acelasi defect: un sir `'` sau `"` neinchis pe randul lui albea tot pana la urmatoarea ghilimea
din FISIER. Declansatorul, o singura linie cu trei ghilimele —
`cd.match(/filename="([^"]+)"/)`. Masurat pe `277e4300`: `ecrane/facturi_ecran.js` orb de la
randul 530 (639 de randuri), `api.js` de la 397 (59 de randuri).

CE FACE ASTA IMPOSIBIL, si e mai tare decat o cifra: pe TOT corpusul `static/js`, textul citit
trebuie sa aiba acoladele si parantezele in echilibru. Un sir care se scurge peste cod inghite
acolade, iar dezechilibrul se vede. **Mutatie dovedita**: cu cititorul de dinainte, `api.js` iese
`{42 }41` — garda cade, numind fisierul.

CE NU FACE, declarat: nu spune ca ce ramane vizibil e citit CORECT, doar ca nu s-a pierdut un
bloc intreg. Si nu e un parser: v. cele trei moduri de esec scrise in `core/cititor_js.py`.

Aserttiunile de mai jos sunt scrise pe NUMARATOARE, nu pe `x in text` (clichetul 50 /
METODA_VERIFICARE §23): o numaratoare spune si cate, deci prinde si dublarea, nu doar disparitia.
"""
import io
import os

import pytest

from core import cititor_js as c

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_JS = os.path.join(_RAD, "static", "js")


def _fisiere_js():
    for rad, _d, nume in os.walk(_JS):
        for f in sorted(nume):
            if f.endswith(".js"):
                yield os.path.join(rad, f)


# ── proprietatea, pe corpusul real ───────────────────────────────────────────
def test_ANTI_VACUU_chiar_sunt_fisiere_de_citit():
    """Fara asta, testele de mai jos ar trece despre nimic."""
    n = len(list(_fisiere_js()))
    assert n >= 40, "doar %d fisiere .js gasite — domeniul s-a rupt, gardul e gol" % n


def test_acoladele_raman_in_echilibru_pe_tot_corpusul():
    rele = []
    for cale in _fisiere_js():
        curat = c.fara_siruri(io.open(cale, encoding="utf-8").read())
        a, b = curat.count("{"), curat.count("}")
        pa, pb = curat.count("("), curat.count(")")
        if a != b or pa != pb:
            rele.append("%s: {%d }%d ( %d ) %d" % (os.path.relpath(cale, _RAD), a, b, pa, pb))
    assert not rele, (
        "cititorul a inghitit cod: un sir sau un regex s-a scurs peste acolade\n  "
        + "\n  ".join(rele))


def test_lungimea_si_numarul_de_randuri_se_pastreaza():
    for cale in _fisiere_js():
        src = io.open(cale, encoding="utf-8").read()
        curat = c.fara_siruri(src)
        assert len(curat) == len(src), cale
        assert curat.count("\n") == src.count("\n"), cale


# ── calibrare pe DEFECTUL propriu (directia «rateaza cod») ───────────────────
def test_DEFECTUL_un_sir_neinchis_nu_inghite_randurile_urmatoare():
    """Linia care a nascut orbirea, cu cod dupa ea. Mutatia care face gardul rosu: scoate
    din `_curata_sir` regula «un sir simplu se opreste la capat de rand»."""
    js = ('const m = cd.match(/filename="([^"]+)"/);\n'
          'try {\n'
          '  await api.post("/x", corp);\n'
          '} catch (e) {\n'
          '  arataMesaj(zona, e.mesaj);\n'
          '}\n')
    curat = c.fara_siruri(js)
    assert curat.count("api.post") == 1, "codul de dupa linia cu trei ghilimele a fost albit: %r" % curat
    assert curat.count("arataMesaj") == 1, curat
    assert curat.count("{") == curat.count("}") == 2, curat


def test_regexul_cu_ghilimele_e_albit_ca_TEXT():
    js = 'const m = cd.match(/filename="([^"]+)"/); const z = 1;'
    curat = c.fara_siruri(js)
    assert curat.count("filename") == 0, "textul expresiei regulate a trecut drept cod: %r" % curat
    assert curat.count("const z = 1;") == 1, curat


def test_acoladele_dintr_un_regex_nu_se_numara():
    js = 'const d = /^\\d{4}-\\d{2}$/; function f() { return 1; }'
    curat = c.fara_siruri(js)
    assert curat.count("{") == curat.count("}") == 1, (
        "acoladele din cuantificatorul expresiei regulate au intrat in numaratoare: %r" % curat)


# ── calibrare in directia OPUSA (directia «acuza pe nedrept») ────────────────
@pytest.mark.parametrize("js", [
    "const x = (a + b) / 2;",
    "const x = lista[i] / 2;",
    "const x = suma * 21 / 100;",
    "const x = f() / 2;",
    "const x = obj.prop / 2;",
])
def test_impartirea_NU_e_luata_drept_expresie_regulata(js):
    """Daca `/` de impartire ar fi albit, aritmetica ar disparea din corpus — iar gardul
    de cote pe nume neutre ar tacea exact acolo unde trebuie sa vorbeasca."""
    curat = c.fara_siruri(js)
    assert curat == js, "s-a albit o impartire: %r" % curat


def test_expresia_regulata_dupa_cuvant_cheie_E_recunoscuta():
    js = 'function f(s) { return /^ab$/.test(s); }'
    curat = c.fara_siruri(js)
    assert curat.count("^ab$") == 0, "expresia regulata de dupa `return` a ramas cod: %r" % curat
    assert curat.count("test(s)") == 1, curat


def test_un_slash_care_nu_se_inchide_pe_rand_ramane_impartire():
    """Partea sigura: daca nu se poate sti, se citeste ca si cod."""
    js = "const a = x /\nconst b = 2;"
    curat = c.fara_siruri(js)
    assert curat.count("const b = 2;") == 1, curat


# ── ce a fost calibrat inainte, si trebuie sa ramana adevarat ────────────────
def test_interpolarea_ramane_COD():
    js = "const h = `TVA: ${suma * 21 / 100}`;"
    curat = c.fara_siruri(js)
    assert curat.count("* 21 / 100") == 1, "aritmetica din interpolare a fost inghitita: %r" % curat
    assert curat.count("TVA:") == 0, curat


def test_template_imbricat_ramane_SIR():
    js = "const h = `<ul>${a.map((u) => `<li>Total 21% (bere)</li>`).join(\"\")}</ul>`;"
    curat = c.fara_siruri(js)
    assert curat.count("21%") == 0, "HTML dintr-un template imbricat a scapat ca fiind cod: %r" % curat
    assert len(curat) == len(js)


def test_cei_doi_cititori_de_sir_NU_se_contrazic():
    """ASIMETRIA care a nascut defectul: `_sfarsit_sir` oprea la capat de rand, `_curata_sir`
    nu — desi amandoi raspund la aceeasi intrebare. Aici nu mai pot diverge."""
    for js in ['const a = "ne\nconst b = 2;', "const a = 'ne\nconst b = 2;"]:
        i = js.index('"') if js.count('"') else js.index("'")
        out = []
        assert c._curata_sir(js, i, len(js), out) == c._sfarsit_sir(js, i, len(js)), js
