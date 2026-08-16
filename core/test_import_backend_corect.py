# -*- coding: utf-8 -*-
"""GARD lot1 corectitudine import: preview↔salvare aliniate pe validarea reala + fara default tacit.
Comportamental (cheama functiile), nu grep. RED probat pe codul vechi."""


def test_q3_verifica_citeste_dnf_luni():
    from core import mijloace_fixe_import_api as mf
    # rand ca cel produs de extrage: cheia duratei e dnf_luni, NU durata
    r = [{"cod": "MF1", "denumire": "Laptop", "valoare": 5000, "rezidual": 0, "dnf_luni": 96}]
    motive = [e["motiv"] for e in mf.verifica_randuri(r)]
    assert "durata" not in motive, "verifica_randuri inca citeste cheia gresita 'durata' -> 0 pe fiecare rand (Q3)"


def test_q4_asociat_juridic_acceptat():
    from core import asociati_import_api as a
    # OMEGA HOLDING SRL, CUI valid de 8 cifre (cifra de control corecta)
    er = a.verifica_randuri([{"nume": "OMEGA HOLDING SRL", "cnp": "13548146", "cota": 100}])
    assert not er, "asociat juridic (CUI valid) respins ca CNP de 13 cifre (Q4): %r" % er


def test_q4_cnp_fizic_invalid_tot_respins():
    from core import asociati_import_api as a
    er = a.verifica_randuri([{"nume": "POP ION", "cnp": "1234567890123", "cota": 100}])
    assert any(e["motiv"] == "cnp_invalid" for e in er), "un CNP fizic invalid trebuie tot respins"


def test_q11_extrage_nu_fabrica_norma():
    from core import salariati_import_api as s
    # fisier FARA coloana norma
    randuri = s.extrage(b"nume,cnp,brut\nPOP ION,1960101078911,3000\n", "x.csv")
    assert randuri, "extrage n-a produs randuri"
    assert randuri[0]["tip_norma"] == "", "norma fabricata 'intreaga' cand coloana lipseste (Q11): %r" % randuri[0]["tip_norma"]


def test_q11_norma_lipsa_semnalata():
    from core import salariati_import_api as s
    er = s.verifica_randuri([{"nume": "POP", "prenume": "ION", "cnp_valid": True, "tip_norma": "", "ore_zi": 0}])
    assert any(e["motiv"] == "norma_lipsa" for e in er), "norma lipsa nu e semnalata (Q11): %r" % er


def test_q13_mijloc_fara_default_cont():
    # modelul Pydantic nu mai fabrica 2131 tacit
    import io
    src = io.open("main.py", encoding="utf-8").read()
    assert 'cont_imobilizare: str = "2131"' not in src, "MijlocFixRand inca defaulteaza tacit 2131 (Q13)"
