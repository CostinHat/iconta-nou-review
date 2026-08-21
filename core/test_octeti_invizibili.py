# -*- coding: utf-8 -*-
"""GARD (21.08.2026): niciun octet de CONTROL invizibil în codul sursă.

DE CE. Gardul R4 (`test_temei_termene`) avea în regex un octet 0x08 (backspace) în loc de `\\b` —
probabil un `\\b` interpretat de shell la scrierea fișierului. Efectul: regexul nu potrivea NIMIC,
deci `xfail(strict=True)` raporta „încă nerezolvat" oricâtă muncă s-ar fi făcut. **Un gard care nu
poate deveni verde arată exact ca o datorie reală** — și dezactivase tăcut singura verificare a
temeiurilor de termene.

Clasa e mai largă decât regexurile: un octet invizibil într-un șir poate schimba o comparație, o
cheie de dicționar sau un mesaj, fără nicio urmă la citire. Scanul de la naștere: 0 în tot repo-ul
(după reparație) — deci gardul pornește de la o lume curată, nu de la un clichet.

CE NU ACOPERĂ: caracterele invizibile care NU sunt de control — spații non-breaking (U+00A0),
zero-width (U+200B), semne de direcție. Alea au uneori rost în text afișat, iar o interdicție largă
ar da fals-pozitive pe conținut legitim. Aici se păzește doar ce nu poate fi niciodată intenționat
într-un fișier sursă.
"""
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BEL, BS, VT, FF, ESC — niciunul n-are ce căuta în cod sursă scris de om.
_CONTROL = {"\x07": "BEL", "\x08": "BS", "\x0b": "VT", "\x0c": "FF", "\x1b": "ESC"}
_SARI = ("venv", "_arhiva", ".git", "node_modules", "__pycache__", ".lant_tmp")


def _fisiere():
    for rad, dirs, fis in os.walk(_RAD):
        dirs[:] = [d for d in dirs if d not in _SARI]
        if any(x in rad for x in _SARI):
            continue
        for f in fis:
            if f.endswith((".py", ".js")):
                yield os.path.join(rad, f)


def _gaseste():
    rele = []
    for p in _fisiere():
        try:
            s = io.open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for i, ch in enumerate(s):
            if ch in _CONTROL:
                rele.append((os.path.relpath(p, _RAD), s[:i].count("\n") + 1, _CONTROL[ch]))
    return rele


def test_niciun_octet_de_control_in_sursa():
    """Miezul. Un `\\b` scris greșit devine un backspace real, iar regexul care-l conține nu mai
    potrivește nimic — tăcut."""
    rele = _gaseste()
    assert not rele, (
        "octeți de control în cod sursă:\n"
        + "\n".join("  %s:%d  %s" % r for r in rele[:20])
        + "\n\nCel mai probabil un `\\b`/`\\f`/`\\v` interpretat la scrierea fișierului. "
        "Scrie-l ca escape într-un raw string, nu ca octet.")


def test_gardul_chiar_citeste_repo_ul():
    """Anti-vacuu pe domeniu: dacă lista de fișiere se golește, testul de mai sus trece pe gol."""
    n = sum(1 for _ in _fisiere())
    assert n >= 300, "prea puține fișiere scanate (%d) — verifică domeniul" % n


@pytest.mark.parametrize("ch,nume", sorted(_CONTROL.items()))
def test_detectorul_chiar_vede_fiecare_octet(ch, nume, tmp_path):
    """Fiecare octet din listă e chiar detectabil — altfel lista e o intenție, nu o verificare."""
    p = tmp_path / "proba.py"
    p.write_text("x = 1  # aici%svine" % ch, encoding="utf-8")
    s = p.read_text(encoding="utf-8")
    assert any(c in _CONTROL for c in s), "octetul %s n-ar fi fost văzut" % nume
