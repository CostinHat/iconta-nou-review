# -*- coding: utf-8 -*-
"""C2 (audit tenant_003): dupa salvarea unui strat de import (salariati, solduri, parteneri, asociati,
mijloace, istoric) navigarea NU mai deschide wizardul de CABINET (o fereastra noua, in afara firmei);
revine pe traseu (nav.inapoiPas) la meniul firmei, cu mesaj de succes (arataMesaj "ok", DS cap.6).
Gard de continut pe migrare.js."""
import io, os
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = io.open(os.path.join(_ROOT, "static/js/ecrane/migrare.js"), encoding="utf-8").read()

TITLURI = [
    ("Solduri inițiale", "wizardSolduri"),
    ("Solduri parteneri", "wizardParteneri"),
    ("Salariați", "wizardSalariati"),
    ("Asociați", "wizardAsociati"),
    ("Mijloace fixe", "wizardMijloace"),
    ("Istoric declarații", "wizardIstoric"),
    ("Vector fiscal", "wizardVector"),  # aceeasi clasa (generalizare Regula 13)
]


def test_handlerele_de_salvare_nu_mai_deschid_wizardul_de_cabinet():
    # nav.deschide("<Titlu>", ...wizard...) e legitim O SINGURA data - la dispecerul de straturi (108-116).
    # A doua aparitie era in handlerul de salvare (bounce la cabinet, in afara firmei) - eliminata (inapoiPas).
    for titlu, wiz in TITLURI:
        pat = 'nav.deschide("%s", (cc, nn) => %s(cc, nn));' % (titlu, wiz)
        assert MIG.count(pat) == 1, (
            "nav.deschide('%s') trebuie sa apara O SINGURA data (dispecerul de straturi); a doua "
            "(handlerul de salvare) trebuie sa revina cu nav.inapoiPas() la firma - C2" % titlu)


def test_mesaj_de_succes_supravietuieste_revenirea():
    assert "let _migMesaj" in MIG, "mecanismul de mesaj de succes (_migMesaj) lipseste - C2"
    assert "function _consumaMigMesaj" in MIG, "consumatorul de mesaj (_consumaMigMesaj) lipseste - C2"
    assert MIG.count("_consumaMigMesaj(corp)") >= 2, (
        "_consumaMigMesaj trebuie DEFINIT si APELAT la revenirea in meniul firmei - C2")
    assert MIG.count("nav.inapoiPas();") >= 7, (
        "cele 7 handlere de salvare trebuie sa revina cu nav.inapoiPas() - C2")
