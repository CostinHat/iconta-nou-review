# -*- coding: utf-8 -*-
"""GARD — un `0` care nu poate fi altceva decât `0` nu susține nicio cauză afirmată.

**Ce s-a găsit** (pragul 3, poziția 2, interdicția 32, 24.08.2026): `inregistrari.document_ref` e
scrisă de **0 din 48** de căi de INSERT și citită de `note_salarii_ciorna()`, care de aceea întoarce
**0 prin construcție** — pentru orice firmă, orice lună. Acel 0 ajungea în `compara_d112`, unde
ramura *„note de salarii în ciornă, așteaptă validare"* devenea **cod mort**, iar în locul ei se lua
mereu ramura care **afirmă o cauză**: *„Statul de plată nu este contabilizat"*, cu remediu
**executabil**: *„Contabilizează statul de plată."*

Pe datele de azi afirmația nimerește adevărul — nicio cale nu creează nota statului de plată
(`salarii_contare` nelegat, R33). Devine **falsă** în ziua în care calea aia se leagă: aplicația i-ar
cere contabilului exact lucrul pe care tocmai l-a făcut, ascunzându-i acțiunea reală. Dar
**independent de asta**, a afirma o cauză pe un necunoscut nedeclarat e **interdicția 10**, azi.

**CE FACE IMPOSIBIL**: ca `note_ciorna` să redevină cu două valori în loc de trei. `None` înseamnă
*nu se poate ști*, și nu are voie să producă nici un remediu **executabil**, nici o cauză afirmată.

**CE NU VERIFICĂ, declarat**: dacă `note_salarii_ciorna` întoarce cifra corectă când coloana **e**
populată — aia cere baza de date, e o probă, nu un gard. Aici se păzește **contractul celor trei
valori** și faptul că interogarea consultă starea coloanei înainte de a o filtra.

**ASERTEAZĂ PE STRUCTURĂ** (METODA §23): verdictele se citesc ca **dicționare**, pe câmp și valoare;
consultarea coloanei se citește din **nodurile `Call`** ale funcției. Niciun `in` pe textul sursei.
"""
import ast
import io
import os

import pytest

from core.control_incrucisat import compara_d112

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# D112 declară, evidența n-are rulaj — situația în care cele trei valori se despart.
DECL = {"602": 100, "412": 250, "432": 100, "480": 22}
RULAJ = {c: {"debit": 0, "credit": 0} for c in ("421", "4315", "4316", "436")}


def _remedii(note_ciorna):
    r = compara_d112(DECL, RULAJ, note_ciorna=note_ciorna)
    assert r, "compara_d112 n-a produs nicio constatare — gardul ar trece pe gol"
    return [c["remediu"] for c in r]


# ── miezul: necunoscutul nu se rotunjește la „știu că nu e" ──────────────────
def test_necunoscutul_nu_produce_remediu_executabil():
    """Un remediu «executabil» e o instrucțiune. Pe un necunoscut, e o ghicitură cu buton."""
    for rem in _remedii(None):
        assert rem["fel"] == "investigatie", (
            "necunoscutul (`note_ciorna=None`) produce remediu «%s» — se comportă ca și cum s-ar "
            "ști că statul nu e contabilizat" % rem["fel"])


def test_necunoscutul_nu_afirma_cauza():
    for rem in _remedii(None):
        assert "nu este contabilizat" not in rem["cauza"], (
            "se afirmă cauza pe un necunoscut — interdicția 10:\n  %s" % rem["cauza"])
        assert "nu se poate ști" in rem["cauza"], (
            "necunoscutul nu e DECLARAT în cauză, doar ocolit:\n  %s" % rem["cauza"])


def test_necunoscutul_numeste_AMANDOUA_actiunile():
    """P11: unde textul nu determină, nu se alege. Contabilul primește ambele ramuri, nu una ghicită."""
    for rem in _remedii(None):
        a = rem["actiune"].lower()
        assert "contabiliz" in a, "acțiunea nu numește contabilizarea:\n  %s" % rem["actiune"]
        assert "valid" in a, "acțiunea nu numește validarea ciornei:\n  %s" % rem["actiune"]


# ── calibrare: cele două valori CUNOSCUTE nu se strică ───────────────────────
def test_CALIBRARE_zero_cunoscut_pastreaza_executabilul():
    """Direcția opusă. Dacă reparația ar transforma orice 0 în necunoscut, ar strica verdictul bun:
    când chiar se știe că nu sunt ciorne, «contabilizează statul» e instrucțiunea corectă."""
    for rem in _remedii(0):
        assert rem["fel"] == "executabil", (
            "un 0 CUNOSCUT nu mai produce instrucțiune — reparația a mers prea departe")
        assert "nu este contabilizat" in rem["cauza"]


def test_CALIBRARE_ciorne_cunoscute_dau_sugerat():
    """Ramura care era cod mort. Aici se dovedește că e vie când primește o cifră adevărată."""
    for rem in _remedii(2):
        assert rem["fel"] == "sugerat", "ramura «ciornă» nu mai e atinsă nici cu o cifră reală"
        assert "ciorn" in rem["cauza"]


def test_CALIBRARE_cele_trei_valori_dau_trei_verdicte_diferite():
    """Anti-vacuu: dacă toate trei ar da același lucru, testele de mai sus ar trece degeaba."""
    feluri = {v: {r["fel"] for r in _remedii(v)} for v in (None, 0, 2)}
    assert len({frozenset(f) for f in feluri.values()}) == 3, (
        "cele trei valori ale lui `note_ciorna` nu produc trei verdicte distincte: %r" % feluri)


# ── interogarea consultă starea coloanei ÎNAINTE de a o filtra ───────────────
def _functia(nume):
    arb = ast.parse(io.open(os.path.join(RAD, "core", "control_incrucisat.py"),
                            encoding="utf-8").read())
    for n in ast.walk(arb):
        if isinstance(n, ast.FunctionDef) and n.name == nume:
            return n
    raise AssertionError("nu mai găsesc `%s` — gardul măsoară ce nu vede" % nume)


def test_numaratoarea_intreaba_intai_daca_are_ce_numara():
    """Fără asta, cineva ar putea scoate verificarea și lăsa `None` să nu mai apară niciodată —
    testele pure de mai sus ar rămâne toate verzi, fiindcă primesc valoarea direct."""
    apeluri = {getattr(n.func, "attr", None) or getattr(n.func, "id", None)
               for n in ast.walk(_functia("note_salarii_ciorna")) if isinstance(n, ast.Call)}
    assert "_document_ref_populat" in apeluri, (
        "`note_salarii_ciorna` nu mai consultă starea coloanei — întoarce iar 0 prin construcție, "
        "iar ramura «ciornă» redevine cod mort")


def test_exista_o_cale_prin_care_se_intoarce_necunoscutul():
    """Apelul ar putea exista și rezultatul lui ignorat. Se cere un `return None` în funcție."""
    fn = _functia("note_salarii_ciorna")
    assert any(isinstance(n, ast.Return) and isinstance(n.value, ast.Constant)
               and n.value.value is None for n in ast.walk(fn)), (
        "funcția nu mai are cale de ieșire cu `None` — necunoscutul nu mai poate fi declarat")


@pytest.mark.parametrize("nume", ["note_salarii_ciorna", "_document_ref_populat"])
def test_anti_vacuu_functiile_exista(nume):
    assert _functia(nume) is not None
