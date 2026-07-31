# -*- coding: utf-8 -*-
"""Export/PDF: linie fara cota TVA = intrare INCOMPLETA -> eroare, NU cota 0 (scutit) ghicita.

Aceeasi clasa cu bug-ul produse_api:46 (or 21), alta masca: `Decimal(str(l.get("cota_tva") or 0))`
transforma cota NULL in 0 = scutit. Exportul catre contabil (SAGA/WinMentor) sau PDF-ul declara
"scutit" unde factura are "lipsa". Distinge None (incomplet -> eroare) de 0 (scutit -> pastreaza)."""
import pytest
from decimal import Decimal


def _linie(cota):
    return {"descriere": "Serviciu", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": cota}


# --- WinMentor ---
def test_winmentor_linie_fara_cota_ridica():
    from core import export_winmentor
    with pytest.raises(ValueError):
        export_winmentor._linii_valorizate([_linie(None)])


def test_winmentor_cota_0_scutit_pastrata_tva_zero():
    from core import export_winmentor
    out = export_winmentor._linii_valorizate([_linie(0)])
    assert out[0]["tva"] == 0   # scutit -> TVA 0, NU eroare


# --- SAGA ---
def test_saga_linie_fara_cota_ridica():
    from core import export_saga
    firma = {"nume": "F", "cui": "14399840", "reg_com": "", "adresa": "A", "iban": "", "banca": ""}
    factura = {"numar": "1", "data_emitere": "2026-06-10", "tert_nume": "C", "tert_cui": "RO1"}
    with pytest.raises(ValueError):
        export_saga.xml_factura(firma, factura, [_linie(None)])


# --- PDF ---
def test_pdf_linie_fara_cota_ridica():
    from core import factura_pdf
    profil = {"nume": "F", "cui": "14399840", "adresa": "A"}
    factura = {"numar": "1", "data_emitere": "2026-06-10", "directie": "emisa",
               "linii": [_linie(None)]}
    with pytest.raises(ValueError):
        factura_pdf.genereaza_pdf(profil, factura)
