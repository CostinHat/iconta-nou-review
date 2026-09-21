# -*- coding: utf-8 -*-
"""GARD: contul de venit pe linia de factura se stabileste DETERMINIST (fara AI); cand nu
se poate, emiterea se BLOCHEAZA - nu cade tacut pe default-ul firmei. (22.09.2026, DECIZII 64)

Clasa reparata (`_potriveste_linii`): `linie["cont_venit"] = cont or cv_firma`, unde `cont` venea
NUMAI din AI. Fara cheie AI, o factura de servicii primea tacit 707 (marfa) in loc de 704 (servicii,
OMFP 1802/2014) - cifra valid-dar-falsa in nota si in declaratii.

MUTATIA care il face rosu (confirmata la scriere): repune `or cv_firma` la capatul deducerii ->
`test_nedeterminat_fara_ai_BLOCHEAZA` nu mai ridica (cade pe default), deci PICA. La fel, o clasificare
gresita in `tip_din_denumire` pica `test_tip_din_denumire_determinist`.

Probele nu ating baza: cu `cota_tva` dat pe linie, `_potriveste_linii` sare peste ramura de nomenclator
(singura care foloseste `conn`), deci `conn=None` e suficient si testul e PUR (fara schema efemera)."""
import pytest

from core import facturi as _fc
from core import facturi_api
from core import ai_client


def _linie(descriere, **extra):
    d = {"descriere": descriere, "cota_tva": 21, "cantitate": 1, "pret_unitar": 100}
    d.update(extra)
    return d


def test_tip_din_denumire_determinist():
    assert _fc.tip_din_denumire("Servicii de consultanta") == "servicii"
    assert _fc.tip_din_denumire("prestari catre client") == "servicii"
    assert _fc.tip_din_denumire("marfa") == "marfa"
    assert _fc.tip_din_denumire("Produse finite") == "produse"
    # niciun cuvant-cheie -> nu decide (nu ghiceste)
    assert _fc.tip_din_denumire("Consultanta IT") is None
    # ambiguu (produse + marfa) -> nu decide
    assert _fc.tip_din_denumire("Produs marfa vandut") is None
    # contul corect pentru servicii, verificat prin harta VENIT
    assert _fc.VENIT[_fc.tip_din_denumire("Servicii")] == "704"


def test_servicii_fara_ai_da_704_nu_default(monkeypatch):
    """Fara AI, o denumire de serviciu -> 704 din regula determinista, NU 707 din default."""
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    out = facturi_api._potriveste_linii(None, [_linie("Servicii")], platitor_tva=True)
    assert out[0]["cont_venit"] == "704"


def test_nedeterminat_fara_ai_BLOCHEAZA(monkeypatch):
    """Fara AI si fara cuvant-cheie clar, emiterea se blocheaza (nu cade tacut pe default)."""
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    with pytest.raises(ValueError):
        facturi_api._potriveste_linii(None, [_linie("Consultanta IT")], platitor_tva=True)


def test_cont_explicit_ocoleste_blocarea(monkeypatch):
    """Un cont_venit explicit pe linie (escape, simetric cu cota) trece neatins, fara clasificare."""
    monkeypatch.setattr(ai_client, "disponibil", lambda: False)
    out = facturi_api._potriveste_linii(
        None, [_linie("Consultanta IT", cont_venit="704")], platitor_tva=True)
    assert out[0]["cont_venit"] == "704"
