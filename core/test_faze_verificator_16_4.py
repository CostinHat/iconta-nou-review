# -*- coding: utf-8 -*-
"""GARD (comanda 16.4 pct.2, C221) — faza „verificator” din jurnal la publicarea unui lot «produs»: `publica_lot.faze_stop(rows, unelte=False)` dă STOP
când ultima rulare a verificatorului n-are sfârșit, e „intrerupt”, nu poartă marcajul scris de lansator sau are alt id decât începutul. Jurnalul de probă
e propriu (LOT_JURNAL în tmp_path, cheie temporară), cu toate fazele obligatorii; rândurile „verificator” se scriu cu `verifica_pas.scrie_faza` (marcate)
sau cu `jurnal_lot.inceput` / `sfarsit` (nemarcate), nu de mână. Cazul (v) — lansatorul oprit cu SIGTERM — rulează în scripts/calibreaza_16_4.py (cere Chromium și lacătul).
"""
import os
import sys

import pytest

_SCRIPTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
LOT = "PROBA-164"
SHA = "c" * 12


def _rand(faza, ev, rez, id_):
    return "\t".join([LOT, faza, ev, "2026-11-05T06:00:00+02:00", SHA, rez, id_, "4242", ""]) + "\n"


@pytest.fixture
def mediu(tmp_path, monkeypatch):
    """-> (VP, JL, PL, jurnal) cu cheia oracolului și jurnalul în tmp_path; jurnalul are toate fazele obligatorii în afară de „verificator”."""
    monkeypatch.syspath_prepend(_SCRIPTS)
    import jurnal_lot as JL
    import publica_lot as PL
    import verifica_pas as VP
    monkeypatch.setattr(VP, "CHEIE_ORACOL", str(tmp_path / "cheie_oracol"))
    jurnal = tmp_path / "jurnal.log"
    monkeypatch.setenv("LOT_JURNAL", str(jurnal))
    text = ""
    for i, f in enumerate(("pornire", "hook", "poarta_verificator", "poarta_pytest", "poarta_plasa")):
        text += _rand(f, "inceput", "-", "id%d" % i) + _rand(f, "sfarsit", "verde", "id%d" % i)
    jurnal.write_text(text + _rand("publicare", "inceput", "-", "idp"), encoding="utf-8")
    return VP, JL, PL, str(jurnal)


def _stop(mediu, unelte=False):
    _, JL, PL, jurnal = mediu
    return PL.faze_stop([r for r in JL._citeste(jurnal) if r[0] == LOT and len(r) > 8], unelte)


def _complet(VP, rezultat="parcurs"):
    a = VP.scrie_faza(LOT, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=SHA)
    VP.scrie_faza(LOT, "verificator", "sfarsit", rezultat, a, "corespunde/nu corespunde/nejudecabil=5/0/2 parcurgere=haiku_1", sha=SHA)
    return a


def test_faza_completa_marcata_nu_da_stop(mediu):
    """Anti-vacuu: jurnalul cu faza completă, marcată, nu dă STOP; fără faza „verificator” dă STOP (produs) și nu dă (unelte)."""
    assert _stop(mediu, unelte=True) == []
    assert any("lipsește" in m and "verificator" in m for m in _stop(mediu))
    _complet(mediu[0])
    assert _stop(mediu) == []


def test_inceput_fara_sfarsit_e_stop(mediu):
    """(i) lansator ucis cu SIGKILL: ultimul «inceput» fără «sfarsit»."""
    mediu[0].scrie_faza(LOT, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=SHA)
    assert any("fără sfârșit" in m for m in _stop(mediu))


def test_inceput_orfan_vechi_urmat_de_o_faza_completa_nu_da_stop(mediu):
    """(ii) un început orfan mai vechi, apoi o fază cu început și sfârșit marcate = fără STOP (contează ultima rulare)."""
    mediu[0].scrie_faza(LOT, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=SHA)
    _complet(mediu[0])
    assert _stop(mediu) == []


def test_sfarsit_intrerupt_e_stop(mediu):
    """(iii) sfârșit cu rezultat «intrerupt» (marcat): lansator oprit."""
    _complet(mediu[0], "intrerupt")
    assert any("întreruptă" in m for m in _stop(mediu))


def test_sfarsit_fara_marcaj_valid_e_stop_scris_de_mana(mediu):
    """(iv) început marcat și sfârșit scris cu `jurnal_lot.sfarsit` (fără marcaj)."""
    VP, JL, _, _ = mediu
    a = VP.scrie_faza(LOT, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=SHA)
    JL.sfarsit(LOT, "verificator", a, "parcurs")
    assert any("scrisă de mână" in m for m in _stop(mediu))


def test_sfarsit_cu_alt_id_decat_inceputul_e_stop(mediu):
    """(vi) sfârșitul marcat al altei rulări nu închide începutul."""
    VP = mediu[0]
    VP.scrie_faza(LOT, "verificator", "inceput", detalii="parcurgere=haiku_1", sha=SHA)
    VP.scrie_faza(LOT, "verificator", "sfarsit", "parcurs", "alt-id", "parcurgere=haiku_1", sha=SHA)
    assert any("fără sfârșit" in m for m in _stop(mediu))


def test_inceput_fara_marcaj_cu_sfarsit_marcat_e_stop(mediu):
    """(vii) început scris cu `jurnal_lot.inceput` (fără marcaj), sfârșit marcat cu același id."""
    VP, JL, _, _ = mediu
    a = JL.inceput(LOT, "verificator", pid=os.getpid())
    VP.scrie_faza(LOT, "verificator", "sfarsit", "parcurs", a, "parcurgere=haiku_1", sha=SHA)
    assert any("scrisă de mână" in m for m in _stop(mediu))
