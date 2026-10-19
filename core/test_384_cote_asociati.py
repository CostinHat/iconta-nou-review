# -*- coding: utf-8 -*-
"""[deficiența 384, retestul Costin 19.10.2026, verbatim în DECIZII „Comanda 9.1”] „Import Asociați: «total cote ✓ 100%» adună și rândurile
respinse; intră un singur asociat, cu 30%.” Cotele se adună numai pe rândurile care INTRĂ; cu un rând respins, setul nu mai dă 100% și
salvarea se refuză numit (`cote_nu_dau_suta`) — niciun asociat nu intră cu o structură incompletă. Fișierele sunt inventate; CNP-ul are
cifra de control verificată (CLAUDE.md), al doilea are cifra de control greșită intenționat."""
from core import asociati_import_api as a

CNP = "1800101221144"          # cifra de control verificată
CNP_GRESIT = "1800101221145"   # aceeași bază, cifra de control greșită


def _citeste(text):
    return a.extrage(text.encode(), "asociati.csv")


def test_randul_respins_nu_se_aduna_la_cote():
    r = _citeste("Nume;CNP;Cota\nPop Ion;%s;30\nIon Pop;%s;70\n" % (CNP, CNP_GRESIT))
    er = a.verifica_randuri(r)
    # Legea 31/1990: structura asociaților = 100% din capital; rândul cu CNP invalid nu intră, deci cotele care intră însumează 30%
    assert a.coerenta_cote(r, {e.get("rand") for e in er}) == {"total": 30.0, "coincide": False}
    assert [e["regula"] for e in er] == ["cnp_invalid", "cote_nu_dau_suta"], er
    assert er[-1]["mesaj"].endswith("cotele asociaților care intră însumează 30%, nu 100%"), er[-1]


def test_dublura_nu_se_aduna_la_cote():
    r = _citeste("Nume;CNP;Cota\nPop Ion;%s;30\nPop Ion;%s;70\n" % (CNP, CNP))
    assert [e["regula"] for e in a.verifica_randuri(r)] == ["identificator_dublat", "cote_nu_dau_suta"]


def test_CALIBRARE_setul_complet_trece():
    r = _citeste("Nume;CNP;Cota\nPop Ion;%s;100\n" % CNP)
    assert a.verifica_randuri(r) == [] and a.coerenta_cote(r) == {"total": 100.0, "coincide": True}


def test_salvarea_refuza_structura_incompleta():
    """Poarta unică: `importa` refuză înainte de a scrie (fără conexiune folosită)."""
    import pytest
    r = _citeste("Nume;CNP;Cota\nPop Ion;%s;30\nIon Pop;%s;70\n" % (CNP, CNP_GRESIT))
    with pytest.raises(ValueError, match="însumează 30%"):
        a.importa(None, r)
