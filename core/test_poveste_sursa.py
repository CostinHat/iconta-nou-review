# -*- coding: utf-8 -*-
"""Povestea lunii: ce nu se sprijină pe pachet nu ajunge în editor (deficiențele 32 + 33, retestul Costin 09.10.2026), și AI-ul simulat
al plasei (comanda Costin 09.10.2026 pct.7), refuzat pe un mediu care nu e de test."""
import json
import os

import pytest

from core import ai_client, pachete_api as pa

RZ = {"declaratii_depuse": ["D300 09/2026"], "venituri": 1000, "cheltuieli": 0, "rezultat": 1000, "tip": "profit"}


def test_lauda_si_afirmatia_despre_declaratii_se_scot_faptele_raman():
    """„povestea lunii păstrează laude nesusținute de cifre” (32); „scrie fals «în septembrie nu a fost nicio declarație de depus»” (33).
    [209: „spune doar ce reiese din cifre și nimic despre declarații”] nici o propoziție despre o declarație depusă nu rămâne.
    MUTAȚIE: ramura laudelor scoasă -> lauda rămâne -> pică."""
    t = ("A fost o lună excelentă, cu o creștere remarcabilă. Veniturile au fost de 1.000,00 lei.\n\n"
         "În septembrie nu a fost nicio declarație de depus. Firma a depus D300.\nRezultatul e profit.")
    curat, scoase = pa.scoate_afirmatii_fara_sursa(t, RZ)
    assert curat == "Veniturile au fost de 1.000,00 lei.\n\nRezultatul e profit."
    assert scoase == ["A fost o lună excelentă, cu o creștere remarcabilă.", "În septembrie nu a fost nicio declarație de depus.",
                      "Firma a depus D300."]
    assert pa.scoate_afirmatii_fara_sursa(curat, RZ) == (curat, [])


def test_promptul_nu_primeste_declaratiile():
    """[33 + 209] Promptul nu primește declarațiile (nici depuse, nici „nicio declarație”) și cere să nu se scrie despre ele.
    MUTAȚIE: rândul declarațiilor depuse înapoi în prompt -> pică."""
    fara = pa._prompt_poveste(dict(RZ, declaratii_depuse=[], nume_firma="X"), 2026, 9)
    cu = pa._prompt_poveste(dict(RZ, declaratii_depuse=["D300 09/2026"], nume_firma="X"), 2026, 9)
    assert fara == cu, "declarațiile depuse schimbă promptul"           # deci nu intră în el, oricare ar fi
    assert "nicio declaratie" not in fara.lower() and "D300" not in fara and "Nu scrie nimic despre declaratii" in fara, fara


def test_ai_simulat_consuma_raspunsurile_in_ordine_si_jurnalizeaza(tmp_path, monkeypatch):
    monkeypatch.setenv(ai_client.CHEIE_SIMULAT, str(tmp_path))
    json.dump(["unu", "doi"], open(tmp_path / "raspunsuri.json", "w"))
    assert ai_client.disponibil()
    assert ai_client.genereaza_text("p1") == "unu" and ai_client.citeste_imagini([(b"x", "image/png")], "p2") == "doi"
    with pytest.raises(RuntimeError, match="niciun răspuns pregătit"):
        ai_client.genereaza_text("p3")
    assert [json.loads(x)["prompt"] for x in open(tmp_path / "prompturi.jsonl")] == ["p1", "p2", "p3"]


def test_ai_simulat_e_refuzat_pe_un_mediu_care_nu_e_de_test(tmp_path, monkeypatch):
    """Producția nu poate primi texte pregătite: cu mediul nedeclarat de test, cheia e refuzată. MUTAȚIE: refuzul scos -> pică."""
    monkeypatch.setenv(ai_client.CHEIE_SIMULAT, str(tmp_path))
    monkeypatch.setenv("ICONTA_MEDIU", "productie")
    json.dump(["text pregătit"], open(tmp_path / "raspunsuri.json", "w"))
    with pytest.raises(RuntimeError, match="nu e de test"):
        ai_client.genereaza_text("p")
    assert not os.path.exists(tmp_path / "prompturi.jsonl")
