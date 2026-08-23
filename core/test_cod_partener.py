# -*- coding: utf-8 -*-
"""GARD (prag 2, 23.08.2026): codul fiscal al partenerului se CERE la introducere.

CE FACE IMPOSIBIL: o factură salvată fără codul partenerului, tăcut. Până azi `tert_cui` era default
de parametru (`None`) în amândouă funcțiile de creare, iar **nimic** nu-l verifica — nici prezența,
nici cifra de control. Măsurat pe date reale: **2 din 42** de facturi fără cod, una către un **SRL**,
intrată **prin aplicație** (status `de_preluat`, produs de `emite_factura`).

DE CE SE CERE, NU SE SEMNALEAZĂ (decizia lui Costin): o factură fără CUI de partener **nu intră în
D394** și **nu se poate corela în VIES** — nu e o coloană goală, e o declarație incompletă la prima
firmă reală. Iar codul nu se poate completa retroactiv de nimeni altcineva decât cel care a emis
factura, deci momentul e introducerea.

CE NU FACE, declarat: nu verifică cifra de control a CUI-ului (aia e `identitate.valideaza_cui`, altă
poartă) și nu decide dacă partenerul CHIAR e persoană fizică — `tert_pf` e o declarație a celui care
introduce, nu o deducere. A ghici din nume ar readuce exact tăcerea pe care o înlocuiește.
"""
import pytest

from core import facturi_api


def test_lipsa_codului_opreste_salvarea():
    with pytest.raises(ValueError) as e:
        facturi_api.cere_cod_partener(None, tert_nume="Agentie Turism Marja SRL")
    m = str(e.value)
    assert "cod" in m.lower(), m
    assert "Agentie Turism Marja SRL" in m, "mesajul nu spune DESPRE CINE e vorba"


@pytest.mark.parametrize("gol", [None, "", "   "])
def test_codul_gol_nu_trece_ca_prezent(gol):
    with pytest.raises(ValueError):
        facturi_api.cere_cod_partener(gol)


def test_mesajul_spune_CONSECINTA_si_TEMEIUL_nu_doar_ca_lipseste():
    """Un refuz care spune doar «câmp obligatoriu» nu-l ajută pe contabil să decidă. Ăsta spune ce se
    strică (D394, VIES), ce are de făcut, și de unde vine cerința."""
    with pytest.raises(ValueError) as e:
        facturi_api.cere_cod_partener(None)
    m = str(e.value)
    assert "D394" in m and "VIES" in m, m
    assert "319" in m, "mesajul nu poartă temeiul"
    assert "persoană fizică" in m, "mesajul nu spune care e ieșirea legitimă"


def test_mesajul_e_in_limba_contabilului_fara_nume_interne():
    """Regula 14.4: un refuz nu expune nume interne de câmp."""
    with pytest.raises(ValueError) as e:
        facturi_api.cere_cod_partener(None)
    m = str(e.value)
    for intern in ("tert_cui", "tert_pf", "tert_nume", "ValueError"):
        assert intern not in m, "mesajul scurge numele intern %r" % intern


def test_persoana_fizica_DECLARATA_trece():
    """Ieșirea legitimă există și e explicită — altfel garda ar bloca vânzarea către populație."""
    assert facturi_api.cere_cod_partener(None, tert_pf=True) is None
    assert facturi_api.cere_cod_partener("", tert_pf=True) is None


def test_codul_prezent_trece_si_se_intoarce_curatat():
    assert facturi_api.cere_cod_partener("  RO1234567897 ") == "RO1234567897"


def test_ANTIVACUU_amandoua_caile_de_creare_chiar_cheama_garda():
    """Garda ar fi decorativă dacă funcțiile de creare n-ar trece prin ea. Se citește sursa, nu se
    presupune — aceeași formă ca la R22."""
    import inspect
    for fn in (facturi_api.creeaza_factura, facturi_api.emite_factura):
        s = inspect.getsource(fn)
        assert "cere_cod_partener(" in s, "`%s` nu mai cere codul de partener" % fn.__name__
        assert "tert_pf" in s, "`%s` n-are ieșirea declarată pentru persoană fizică" % fn.__name__
