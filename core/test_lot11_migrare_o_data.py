# -*- coding: utf-8 -*-
"""[lotul 11, comanda Costin 11.2 pct.2 — 409: „ce oprește repetarea”] Reparația pe datele F1 (stornarea notei 105 + nota nouă) s-a aplicat
de două ori — lotul 9 (notele 146 / 147) și lotul 10 (168 / 169) —, fiindcă nimic nu refuza o rulare repetată. Pe PRODUCȚIE,
`core.migrari_registru ruleaza --productie` refuză acum o migrare cu aceeași amprentă deja în registru. MUTAȚIE: refuzul scos din `main`
-> `test_a_doua_rulare_pe_productie_e_refuzata` pică (migrarea rulează din nou)."""
import pytest

from core import migrari_registru as mr

CALE = "core/migrare_borderou_tip_vechi.py"


def _text_migrare():
    import io
    import os
    return io.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CALE), encoding="utf-8").read()


def _pregateste(monkeypatch, deja_rulata, rulari):
    monkeypatch.setattr(mr, "_env_productie", lambda: None)
    monkeypatch.setattr(mr, "_reporneste_daca_e_cazul", lambda productie: None)
    monkeypatch.setattr(mr, "_cu_registrul", lambda f: f(object()))
    monkeypatch.setattr(mr, "nerulate", lambda cur, m: [] if deja_rulata else list(m.items()))
    monkeypatch.setattr(mr, "inainte_nerulate", lambda cur, cale: [])
    monkeypatch.setattr(mr, "inregistreaza", lambda *a, **k: None)
    import runpy
    monkeypatch.setattr(runpy, "run_path", lambda *a, **k: rulari.append(a[0]))


def test_a_doua_rulare_pe_productie_e_refuzata(monkeypatch):
    rulari = []
    _pregateste(monkeypatch, True, rulari)
    with pytest.raises(SystemExit) as e:
        mr.main(["ruleaza", "--productie", CALE])
    # mesajul EXACT al refuzului (cu amprenta migrării), nu un sub-șir oriunde; și nicio rulare
    assert (str(e.value), rulari) == ("%s (amprenta %s) e deja rulată pe producție — o a doua rulare a aceleiași migrări nu se face "
                                      "(reparația 409 aplicată de două ori, lotul 11)." % (CALE, mr.amprenta(_text_migrare())[:12]), []), \
        (str(e.value), rulari)


def test_prima_rulare_pe_productie_merge(monkeypatch):
    rulari = []
    _pregateste(monkeypatch, False, rulari)
    assert mr.main(["ruleaza", "--productie", CALE]) == 0 and len(rulari) == 1


def test_pe_baza_de_test_rularea_repetata_ramane_admisa(monkeypatch):
    rulari = []
    _pregateste(monkeypatch, True, rulari)
    assert mr.main(["ruleaza", CALE]) == 0 and len(rulari) == 1
