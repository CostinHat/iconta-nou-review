"""Comanda 16.8-B, pct.3: `sectiune` și `text_scenariu` din scripts/lanseaza_verificator.py (C225). Fără Chromium, fără 8019, fără baza de test, fără jurnal de loturi.

Modulul se încarcă din rădăcina VERIFICATOR_RAD_16_8_B (implicit worktree-ul); fixturile sunt copii înghețate ale scenariilor din docs/dovezi/16_8_B/scenarii/."""
import importlib.util
import os
import re
import sys
import types

import pytest

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(RAD, "docs", "dovezi", "16_8_B", "scenarii")
X05, X06, PILOT = (os.path.join(FIX, n) for n in ("scenariu_X05_16_8_C1.txt", "scenariu_X06_17_1.txt", "scenarii_pilot.txt"))
ANTET = re.compile(r"([A-Z]\d{2,3}) · ")


def _incarca(cale, nume, rad):
    """Încarcă un modul din rădăcina `rad`, cu nume unic și cu scripts/ al ei primul în sys.path."""
    scripts = os.path.join(rad, "scripts")
    sys.path.insert(0, scripts)
    try:
        spec = importlib.util.spec_from_file_location("%s_%s" % (nume, abs(hash(rad))), os.path.join(scripts, cale))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    finally:
        sys.path.remove(scripts)


LV = _incarca("lanseaza_verificator.py", "lanseaza_verificator_16_8_B", os.environ.get("VERIFICATOR_RAD_16_8_B", RAD))


def _sectiune_veche(text, cod):
    """Algoritmul de la ada64bef (scripts/lanseaza_verificator.py:85–93), referința care deosebește defectul de reparație."""
    rez, in_ = [], False
    for ln in text.splitlines():
        if re.match(r"F\d{3} · ", ln):
            in_ = ln.startswith(cod)
        if in_:
            rez.append(ln)
    return "\n".join(rez)


def _citeste(cale):
    return open(cale, encoding="utf-8").read()


def _coduri(text):
    return [m.group(1) for m in (ANTET.match(ln) for ln in text.splitlines()) if m]


def test_sectiune_x05_si_x06_din_fixturile_lor():
    t05, t06 = _citeste(X05), _citeste(X06)
    s05, s06 = LV.sectiune(t05, "X05"), LV.sectiune(t06, "X06")
    assert s05.startswith("X05 · Navigare ferestre (16.8-C1)")
    assert len(s05) == 1812
    assert s05 == t05.rstrip("\n")
    assert s06.startswith("X06 · Meniul firmei")
    assert len(s06) == 3125


def test_sectiune_cod_din_alt_scenariu_sau_prefix_da_gol():
    assert LV.sectiune(_citeste(X05), "X06") == ""
    assert LV.sectiune(_citeste(PILOT), "F999") == ""
    assert LV.sectiune(_citeste(PILOT), "F01") == ""


def test_sectiune_pilot_toate_cele_44_de_coduri():
    t = _citeste(PILOT)
    coduri = _coduri(t)
    assert len(coduri) == 44
    for cod in coduri:
        s = LV.sectiune(t, cod)
        assert s.startswith(cod + " · ")
        assert _coduri(s) == [cod], cod
    assert LV.sectiune(t, "X02").startswith("X02 · Fereastra de bun venit")


def test_sectiune_pilot_f017_ca_algoritmul_vechi_iar_vechiul_da_gol_pe_x():
    t05, t06, tp = _citeste(X05), _citeste(X06), _citeste(PILOT)
    assert LV.sectiune(tp, "F017") == _sectiune_veche(tp, "F017") != ""
    assert _sectiune_veche(t05, "X05") == "" and _sectiune_veche(t06, "X06") == "" and _sectiune_veche(tp, "X02") == ""


def test_sectiune_sintetica_fiecare_ia_numai_randurile_ei():
    t = "preambul\nA01 · unu\nrând 1\ng02 — intrare\nB22 · doi\nrând 2\nC333 · trei\nrând 3"
    assert LV.sectiune(t, "A01") == "A01 · unu\nrând 1\ng02 — intrare"
    assert LV.sectiune(t, "B22") == "B22 · doi\nrând 2"
    assert LV.sectiune(t, "C333") == "C333 · trei\nrând 3"
    assert LV.sectiune(t, "preambul") == ""


def test_text_scenariu_cazurile_regulii():
    assert LV.text_scenariu(None, None) == ("", None)
    assert LV.text_scenariu(X05, None) == (_citeste(X05), None)
    assert LV.text_scenariu(None, "X05") == ("", "--sectiune cere --scenariu")
    text, motiv = LV.text_scenariu(PILOT, "ZZ99")
    assert text == ""
    assert motiv == "secțiunea ZZ99 nu e în %s (coduri găsite: %s)" % (PILOT, ", ".join(_coduri(_citeste(PILOT))))
    assert LV.text_scenariu(X05, "X05") == (LV.sectiune(_citeste(X05), "X05"), None)


def _args(sectiune, scenariu=X05):
    return types.SimpleNamespace(parcurs=__file__, pasi_txt=__file__, pasi_json=__file__, scenariu=scenariu, sectiune=sectiune, formate=[],
                                 verificator="code", sha="0" * 40, lot="16.8-B", csv=None)


def test_text_scenariu_lanseaza_refuza_sectiunea_negasita_inainte_de_orice(capsys):
    assert LV._lanseaza(_args("ZZ99"), "0" * 40, None) == (1, False, (0, 0, 0, 0))
    assert "[lanseaza_verificator] REFUZ: secțiunea ZZ99 nu e în " in capsys.readouterr().out


def test_text_scenariu_lanseaza_trece_de_sectiune_si_ajunge_la_importuri(capsys):
    assert LV._lanseaza(_args("X05"), "0" * 40, None) == (1, False, (0, 0, 0, 0))
    assert "parcursul importă module nepermise" in capsys.readouterr().out
    assert LV._lanseaza(_args(None, None), "0" * 40, None) == (1, False, (0, 0, 0, 0))
    assert "parcursul importă module nepermise" in capsys.readouterr().out
