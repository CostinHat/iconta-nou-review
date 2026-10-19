# -*- coding: utf-8 -*-
"""Gard COMPORTAMENTAL (unit) pentru clasa 'importul accepta orice fisier si declara succes'
(campania certificare-comportament, 11.08.2026, ceruta de Costin).

Clasa: un fisier cu structura CSV valida dar FARA coloanele asteptate era parsat tacit ->
extrage() intorcea [] (0 randuri) -> ruta raspundea HTTP 200 total=0 (ZERO-BASE incalcat:
rezultat gol prezentat ca succes, nu ca eroare). Gasita pe solduri (reparata punctual cu
strict=True) DAR persista pe asociati/istoric/mijloace/salariati/solduri (coloane).

Fix: parserul ridica ValueError cand coloana-CHEIE de identificare lipseste -> ruta 400.
retete_import_api/articole_import_api aveau deja checkul; adus la toata familia.

Proba ca gardul MUSCA pe codul vechi: pe parserul nereparat, un CSV cu coloane-gunoi
intoarce [] fara exceptie -> assertul pytest.raises pica (rosu). Dupa fix ridica -> verde.
"""
import pytest
from core import (asociati_import_api, istoric_declaratii_import_api,
                  mijloace_fixe_import_api, salariati_import_api, solduri_api)

# CSV cu structura VALIDA (antet + o linie), dar coloane care NU sunt cele asteptate.
GUNOI = b"aaa,bbb,ccc\n1,2,3\n"

# (modul, functia de parsare) - solduri foloseste extrage_balanta, restul extrage
PARSERE = [
    (asociati_import_api, "extrage"),
    (istoric_declaratii_import_api, "extrage"),
    (mijloace_fixe_import_api, "extrage"),
    (salariati_import_api, "extrage"),
    (solduri_api, "extrage_balanta"),
]


@pytest.mark.parametrize("modul,fn", PARSERE, ids=lambda x: getattr(x, "__name__", x))
def test_parser_respinge_coloane_nerecunoscute(modul, fn):
    """Un fisier .csv valid ca structura dar cu coloane straine NU se accepta tacit
    (ZERO-BASE): parserul ridica ValueError, nu intoarce [] pe tacere."""
    with pytest.raises(ValueError):
        getattr(modul, fn)(GUNOI, "migrare.csv")


def test_parser_accepta_fisier_bun_asociati():
    """Non-regresie: un fisier CU coloanele corecte NU e respins de noul check."""
    bun = b"nume,cnp,cota\nPopescu Ion,1900101221144,100\n"
    assert asociati_import_api.extrage(bun, "asociati.csv"), "fisier valid respins gresit"


def test_articole_stoc_fara_pret_e_invalid():
    # [articol_pret] articol cu cantitate > 0 dar pret 0/lipsa -> valoarea stocului 0 fabricata tacit. Invalid.
    # [373, comanda Costin 8.2] eticheta rândului vine din aceeași verificare ca salvarea (`eticheteaza` / `verifica_randuri`)
    from core import articole_import_api as ai
    rez = ai.eticheteaza(ai.extrage("denumire,um,cantitate,pret,cont stoc\nCiment,buc,100,50,371\nNisip,buc,200,,371\n".encode(),
                                    "articole.csv"))
    d = {r["denumire"]: r for r in rez}
    assert d["Ciment"]["stare"] != "respins"
    assert d["Nisip"]["stare"] == "respins" and "stoc" in d["Nisip"]["motive"][0].lower()
    # coloana pret lipsa complet -> orice articol cu stoc invalid
    rez2 = ai.eticheteaza(ai.extrage("denumire,um,cantitate,cont stoc\nVar,buc,10,371\n".encode(), "articole.csv"))
    assert rez2[0]["stare"] == "respins"
    # articol fara stoc (cantitate 0) fara pret -> intră (nomenclator pur, fara miscare)
    rez3 = ai.eticheteaza(ai.extrage("denumire,um,cantitate,pret,cont stoc\nServiciu,buc,0,,371\n".encode(), "articole.csv"))
    assert rez3[0]["stare"] != "respins"
