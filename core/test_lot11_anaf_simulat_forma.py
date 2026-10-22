# -*- coding: utf-8 -*-
"""[lotul 11] Răspunsul ANAF simulat al plasei e2e (`anaf_api.CHEIE_SIMULAT`, deficiența 444) are forma ÎNTREAGĂ a răspunsului real
(`anaf_api.rezultat_gol`), cu câmpurile pregătite de test peste ea. Găsit în plasa e2e din 22.10.2026: un răspuns pregătit numai cu
câmpurile testului (fără `tva_la_incasare`) dădea KeyError în `statut_furnizori` -> lista facturilor primite 500, iar toate e2e-urile
care deschideau „Facturi primite” după testul care pregătise fișierul cădeau în lanț. MUTAȚIE: simulatorul întors la `dict(pregatit,
cui=…, gasit=True)` -> pică."""
import json

from core import anaf_api as a


def test_raspunsul_simulat_are_cheile_raspunsului_real(tmp_path, monkeypatch):
    (tmp_path / "anaf.json").write_text(json.dumps({"14399840": {"denumire": "DANTE INTERNATIONAL SA", "platitor_tva": True}}),
                                        encoding="utf-8")
    monkeypatch.setenv(a.CHEIE_SIMULAT, str(tmp_path))
    monkeypatch.setattr("core.mediu_test.motive", lambda: [])
    gasit, negasit = a.valideaza_cui(["14399840", "2864518"])
    assert set(gasit) == set(a.rezultat_gol("x")) and set(negasit) == set(a.rezultat_gol("x"))
    assert (gasit["gasit"], gasit["denumire"], gasit["platitor_tva"], gasit["tva_la_incasare"]) == (
        True, "DANTE INTERNATIONAL SA", True, False)
    assert (negasit["cui"], negasit["gasit"]) == ("2864518", False)


def test_statutul_furnizorului_se_afla_din_raspunsul_simulat(tmp_path, monkeypatch):
    (tmp_path / "anaf.json").write_text(json.dumps({"14399840": {"denumire": "DANTE INTERNATIONAL SA", "platitor_tva": True}}),
                                        encoding="utf-8")
    monkeypatch.setenv(a.CHEIE_SIMULAT, str(tmp_path))
    monkeypatch.setattr("core.mediu_test.motive", lambda: [])
    # conftest leagă `statut_furnizori` de un ANAF „jos” (`functools.partial`, interogare=…); aici se probează interogarea simulată
    st = a.statut_furnizori.func([("14399840", "2026-10-01", None)], interogare=a.valideaza_cui)[("14399840", "2026-10-01")]
    assert (st["platitor_tva"], st["tva_la_incasare"], st["denumire_anaf"]) == (True, False, "DANTE INTERNATIONAL SA")


def test_baza_reala_a_plasei_se_vede_iar_testul_o_poate_suprascrie(tmp_path, monkeypatch):
    """Baza simulatorului (`frontend_test/e2e/anaf_baza.json`, răspunsuri ANAF reale capturate o dată) se vede fără ca testul să
    pregătească ceva — cum vedea plasa ANAF-ul real înainte de 444 —, iar `anaf.json` al testului ÎNLOCUIEȘTE înregistrarea CUI-ului (ce
    nu scrie testul e „gol”, ca înainte de bază — testele 444 / 459 își scriu răspunsul întreg). MUTAȚIE: baza
    necitită -> DANTE „negăsit” -> pică (în plasă: validarea facturii primite de la DANTE cerea statutul de TVA de mână)."""
    import os
    import shutil
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    shutil.copy(os.path.join(rad, "frontend_test", "e2e", "anaf_baza.json"), tmp_path / "anaf_baza.json")
    monkeypatch.setenv(a.CHEIE_SIMULAT, str(tmp_path))
    monkeypatch.setattr("core.mediu_test.motive", lambda: [])
    (dante,) = a.valideaza_cui(["14399840"])
    assert (dante["gasit"], dante["denumire"], dante["platitor_tva"], dante["judet"]) == (True, "DANTE INTERNATIONAL SA", True, "B")
    (tmp_path / "anaf.json").write_text(json.dumps({"14399840": {"denumire": "NUME NOU SA"}}), encoding="utf-8")
    (dante,) = a.valideaza_cui(["14399840"])
    assert (dante["denumire"], dante["platitor_tva"], dante["judet"]) == ("NUME NOU SA", False, "")
