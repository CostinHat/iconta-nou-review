# -*- coding: utf-8 -*-
"""Unealta care aduce acte din portal NU are voie să scrie un `.txt` gol.

CE FACE IMPOSIBIL: exact modul de eșec al lui **R20** — opt artefacte de un octet intrate în corpus
pe 13.08.2026 fiindcă extragerea a produs gol și n-a spus-o. Clichetul din `test_provenienta.py` a
coborât pe **0**, deci orice artefact gol pică poarta; dar un clichet pe 0 fără gardă la sursă cade
la prima regenerare, iar atunci nu se poate spune dacă e regresie sau comportament normal. Asta e
gardă la producător, nu la poartă.

CE NU FACE, declarat: nu atinge rețeaua și nu verifică extragerea în sine (`text()`) — verifică doar
că un rezultat gol se OPREȘTE în loc să fie scris. Un `text()` care ar extrage prost, dar nenul, trece.
"""
import importlib.util
import io
import os

import pytest

_CALE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     "scripts", "portal_legislativ.py")


def _modul():
    spec = importlib.util.spec_from_file_location("portal_legislativ", _CALE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.mark.parametrize("gol", ["", "   ", "\n\n", " \t \n "])
def test_extragerea_goala_se_opreste_si_nu_lasa_nimic(tmp_path, gol):
    """Calibrare negativă, pe propriul mod de eșec: gol → excepție, ȘI zero fișiere pe disc.
    Un `.txt.sha256` rămas fără `.txt` ar fi la fel de rău — amprentă pe un act inexistent."""
    p = _modul()
    p.DIR = str(tmp_path)
    with pytest.raises(ValueError) as e:
        p._scrie_text("d999_proba", gol)
    assert "EXTRAGERE GOALA" in str(e.value) and "d999_proba" in str(e.value), \
        "mesajul nu numește nici defectul, nici fișierul: %r" % str(e.value)
    assert os.listdir(str(tmp_path)) == [], \
        "s-au lăsat fișiere în urmă: %r" % os.listdir(str(tmp_path))


def test_textul_real_se_scrie_iar_amprenta_e_pe_TEXT(tmp_path):
    """Calibrare pozitivă: garda nu blochează cazul bun, iar amprenta e pe text, nu pe pagină."""
    import hashlib
    p = _modul()
    p.DIR = str(tmp_path)
    continut = "Art. 1. — Probă de text extras.\n"
    amp = p._scrie_text("d999_proba", continut)

    assert io.open(os.path.join(str(tmp_path), "d999_proba.txt"), encoding="utf-8").read() == continut
    assert amp == hashlib.sha256(continut.encode("utf-8")).hexdigest()
    pe_disc = io.open(os.path.join(str(tmp_path), "d999_proba.txt.sha256"), encoding="utf-8").read()
    assert pe_disc.strip() == amp
    assert sorted(os.listdir(str(tmp_path))) == ["d999_proba.txt", "d999_proba.txt.sha256"]


def test_adu_chiar_trece_prin_garda(tmp_path):
    """Anti-vacuu: garda ar fi decorativă dacă `adu` ar mai scrie `.txt` pe lângă ea.
    Se citește sursa lui `adu`, nu doar existența funcției."""
    import inspect
    p = _modul()
    sursa = inspect.getsource(p.adu)
    assert "_scrie_text(" in sursa, "`adu` nu mai cheamă garda — ocolită"
    assert '".txt"' not in sursa, "`adu` scrie din nou direct `.txt`, pe lângă gardă:\n%s" % sursa
