# -*- coding: utf-8 -*-
"""17.5-C0 — rândurile modificabile ale plasei fixe. `plasa_modificabile` citește linia arhitectului din praguri, iar `manifest_refuzuri(..., modificabile=)`
acceptă un rând modificat numai dacă toate condițiile sunt adevărate (cale numită, în diff, aceeași comandă, număr de teste nescăzut, hash corect).
Pe depozite git temporare: fără 8019, fără Chromium, fără baza de test, fără rețea."""
import importlib.util
import os
import subprocess
import sys
import tempfile

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import poarta_lib as L  # noqa: E402

BAZA_LOT = "594b72a9e69aee9c86e0d72f07ec21da6f13c3e6"   # commitul de bază al lotului 17.5-C0
F = "frontend_test/e2e/e2e_vechi.py"
ANTET = "# manifest de probă\n"


def _g(d, *a):
    return subprocess.run(["git", *a], cwd=d, capture_output=True, text=True)


def _commit(d, nume, text, mesaj="x"):
    os.makedirs(os.path.dirname(os.path.join(d, nume)) or d, exist_ok=True)
    open(os.path.join(d, nume), "w").write(text)
    _g(d, "add", nume)
    _g(d, "-c", "core.hooksPath=/dev/null", "commit", "-q", "-m", mesaj)
    return _g(d, "rev-parse", "HEAD").stdout.strip()


def _rand(f, h, n=3, cmd=None):
    return "%s\t%s\t%d\t%s\n" % (f, h, n, cmd or "python -m pytest -q %s" % f)


@pytest.fixture()
def depozit():
    with tempfile.TemporaryDirectory() as tmp:
        d = os.path.join(tmp, "dep")
        subprocess.run(["git", "init", "-q", "-b", "main", d], check=True)
        _g(d, "config", "user.email", "c@c")
        _g(d, "config", "user.name", "c")
        _commit(d, F, "def test_a():\n    assert 1\n")
        baza = _commit(d, L.MANIFEST, ANTET + _rand(F, "a" * 64), "baza")
        _g(d, "checkout", "-q", "-b", "lot")
        yield d, baza


def _modifica(d, n=3, cmd=None, hash_bun=True, in_diff=True):
    """Fișierul de test se schimbă (în diff dacă `in_diff`), iar manifestul primește rândul nou; -> calea manifestului."""
    if in_diff:
        _commit(d, F, "def test_a():\n    assert 2\n")
    h = L.hash_fisier(os.path.join(d, F)) if hash_bun else "f" * 64
    cale = os.path.join(d, L.MANIFEST)
    open(cale, "w").write(ANTET + _rand(F, h, n, cmd))


def _modul_baza(tmp):
    """poarta_lib.py de pe commitul de bază al lotului, într-un modul temporar (referința pentru testul 7)."""
    text = subprocess.run(["git", "show", "%s:scripts/poarta_lib.py" % BAZA_LOT], cwd=RAD, capture_output=True, text=True, check=True).stdout
    cale = os.path.join(tmp, "poarta_lib_baza.py")
    open(cale, "w", encoding="utf-8").write(text)
    spec = importlib.util.spec_from_file_location("poarta_lib_baza", cale)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_1_rand_modificat_pentru_cale_modificabila_e_acceptat(depozit):
    d, baza = depozit
    _modifica(d)
    assert L.manifest_refuzuri(d, baza, modificabile={F}) == []


def test_2_aceeasi_modificare_fara_cale_in_modificabile_e_refuz(depozit):
    d, baza = depozit
    _modifica(d)
    r = L.manifest_refuzuri(d, baza, modificabile={"frontend_test/e2e/altul.py"})
    assert len(r) == 1 and F in r[0] and "modificat" in r[0]


def test_3_numarul_de_teste_scazut_e_refuz_cu_ambele_numere(depozit):
    d, baza = depozit
    _modifica(d, n=2)
    r = L.manifest_refuzuri(d, baza, modificabile={F})
    assert len(r) == 1 and F in r[0] and "3" in r[0] and "2" in r[0] and "scăzut" in r[0]


def test_3b_numarul_de_teste_crescut_e_acceptat(depozit):
    d, baza = depozit
    _modifica(d, n=5)
    assert L.manifest_refuzuri(d, baza, modificabile={F}) == []


def test_4_comanda_schimbata_e_refuz(depozit):
    d, baza = depozit
    _modifica(d, cmd="python -m pytest -q -x %s" % F)
    r = L.manifest_refuzuri(d, baza, modificabile={F})
    assert len(r) == 1 and F in r[0] and "comanda" in r[0]


def test_5_cale_modificabila_dar_fisierul_nu_e_in_diff_e_refuz(depozit):
    d, baza = depozit
    _modifica(d, in_diff=False, hash_bun=False)
    r = L.manifest_refuzuri(d, baza, modificabile={F})
    assert len(r) == 1 and F in r[0] and "diff" in r[0]


def test_6_sha256_diferit_de_hash_ul_fisierului_e_refuz(depozit):
    d, baza = depozit
    _modifica(d, hash_bun=False)
    r = L.manifest_refuzuri(d, baza, modificabile={F})
    assert len(r) == 1 and F in r[0] and "sha256" in r[0]


def test_7_fara_modificabile_iesirea_e_cea_a_functiei_de_pe_baza(depozit):
    d, baza = depozit
    with tempfile.TemporaryDirectory() as tmp:
        ref = _modul_baza(tmp)
        cazuri = [dict(), dict(n=2), dict(cmd="python -m pytest -q -x %s" % F), dict(hash_bun=False)]
        for k in cazuri:
            _g(d, "reset", "-q", "--hard", baza)
            _modifica(d, **k)
            assert L.manifest_refuzuri(d, baza) == ref.manifest_refuzuri(d, baza), k
        _g(d, "reset", "-q", "--hard", baza)
        _modifica(d, in_diff=False)
        assert L.manifest_refuzuri(d, baza) == ref.manifest_refuzuri(d, baza)
        assert len(L.manifest_refuzuri(d, baza)) == 1   # rândul modificat rămâne refuz și fără `modificabile`


def test_8_plasa_modificabile_citeste_linii_si_cai(depozit):
    d, _ = depozit
    _commit(d, "scripts/praguri_9_9.txt", "unelte\nplasa_modificabile x.py y.py\nalt rând\nplasa_modificabile z.py\n")
    assert L.plasa_modificabile(d, "9_9") == {"x.py", "y.py", "z.py"}
    assert L.plasa_modificabile(d, "8_8") == set()   # fără fișier de praguri
    _commit(d, "scripts/praguri_7_7.txt", "unelte\nfara linia plasei\n")
    assert L.plasa_modificabile(d, "7_7") == set()


def test_9_rand_lipsa_pentru_o_cale_modificabila_ramane_refuz(depozit):
    d, baza = depozit
    _commit(d, F, "def test_a():\n    assert 2\n")
    open(os.path.join(d, L.MANIFEST), "w").write(ANTET)
    r = L.manifest_refuzuri(d, baza, modificabile={F})
    assert len(r) == 1 and F in r[0] and "lipsă" in r[0]
