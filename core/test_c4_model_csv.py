# -*- coding: utf-8 -*-
"""C4 (audit tenant_003): fiecare strat de import cu fisier ofera 'Descarca model (CSV)' cu formatul REAL
citit din parser (nu din textul de pe ecran). Intro-ul mijloacelor fixe mentioneaza contul de imobilizare
si de amortizare (le citeste parserul). Gard de continut pe migrare.js."""
import io, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = io.open(os.path.join(_ROOT, "static/js/ecrane/migrare.js"), encoding="utf-8").read()

STRATURI = ["parteneri", "salariati", "asociati", "mijloace", "istoric", "articole", "retete", "rip"]


def test_toate_straturile_de_import_au_model_csv():
    for cheie in STRATURI:
        assert "_descarcaModelCSV(MODELE.%s)" % cheie in MIG, (
            "stratul '%s' nu are butonul 'Descarca model (CSV)' cablat - C4" % cheie)
    # 8 straturi noi + solduri (descarcaModelSolduri) = 9 straturi cu buton model
    assert MIG.count('id="mig-model"') >= 9, "asteptam cel putin 9 butoane de model (8 noi + solduri) - C4"


def test_modelele_au_toate_cheile():
    for cheie in STRATURI:
        assert 'fisier: "model_' in MIG and (cheie + ":") in MIG, "MODELE.%s lipseste - C4" % cheie


def test_intro_mijloace_mentioneaza_contul_de_imobilizare():
    # Bugul numit: textul de pe ecran la mijloace fixe omitea contul de imobilizare, desi parserul il citeste.
    assert "PIF · metodă · cont imobilizare · cont amortizare" in MIG, (
        "intro-ul mijloacelor fixe trebuie sa mentioneze cont imobilizare + cont amortizare (citite la import) - C4")
