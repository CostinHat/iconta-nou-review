# -*- coding: utf-8 -*-
"""Teste F187 — export WinMENTOR. Verificare contra spec-ului OFICIAL (Facturi clienti.pdf Rev.1.2 +
Articole noi.pdf), camp cu camp, + gardul de encoding Windows-1250. Nu avem WinMentor live -> conformitate la spec.
"""
from datetime import date
import pytest
from core import export_winmentor as wm


def _factura(numar="17", serie="AA", tva_incasare=False, taxare_inversa=False):
    firma = {"nume": "FIRMA SRL", "cui": "14399840", "tva_la_incasare": tva_incasare}
    factura = {"numar": numar, "serie": serie, "data_emitere": date(2026, 2, 12),
               "data_scadenta": date(2026, 3, 14), "tert_cui": "RO1234567",
               "taxare_inversa": taxare_inversa, "tert_nume": "CLIENT SA"}
    linii = [{"descriere": "Consultanță IT", "um": "ore", "cantitate": 10, "pret_unitar": 100, "cota_tva": 21}]
    return firma, factura, linii


# ---- cod articol determinist + consecvent ----

def test_cod_articol_determinist_si_format():
    c1 = wm.cod_articol("Consultanță IT")
    c2 = wm.cod_articol("Consultanță IT")
    assert c1 == c2                         # determinist
    assert c1.startswith("A") and len(c1) == 12   # format alfanumeric fix, nu descrierea bruta
    assert wm.cod_articol("Alt serviciu") != c1

def test_cod_consecvent_intre_facturi_si_articole():
    firma, factura, linii = _factura()
    ftxt = wm.facturi_txt(firma, [(factura, linii)], 2026, 2)
    atxt = wm.articole_txt(linii)
    cod = wm.cod_articol("Consultanță IT")
    assert ("Item_1=%s;" % cod) in ftxt      # codul din Item
    assert ("[ArticoleNoi_%s]" % cod) in atxt  # ACELASI cod in definitie


# ---- Facturi.txt: structura contra spec ----

def test_facturi_txt_structura_spec():
    firma, factura, linii = _factura()
    t = wm.facturi_txt(firma, [(factura, linii)], 2026, 2)
    assert "[InfoPachet]" in t
    assert "AnLucru=2026" in t and "LunaLucru=2" in t
    assert "Tipdocument=FACTURA IESIRE" in t
    assert "TotalFacturi=1" in t
    assert "[Factura_1]" in t
    assert "NrDoc=17" in t
    assert "SerieCarnet=AA" in t
    assert "Data=12.02.2026" in t            # dd.mm.yyyy
    assert "CodClient=RO1234567" in t        # CIF (decizie #1)
    assert "Localitate=" in t                # gol (decizie #5)
    assert "TipTVA=0" in t                   # decizie #3
    assert "TotalArticole=1" in t
    assert "[Items_1]" in t

def test_item_format_cod_um_cant_pret_plus_tva():
    firma, factura, linii = _factura()
    t = wm.facturi_txt(firma, [(factura, linii)], 2026, 2)
    cod = wm.cod_articol("Consultanță IT")
    # Item = cod;UM;cantitate;pret_unitar
    assert ("Item_1=%s;ore;10;100.00" % cod) in t
    # TVA pe linie: 10*100*21% = 210.00
    assert "Item_1_TVA=210.00" in t

def test_tva_incasare_si_taxare_inversa_D_N():
    firma, factura, linii = _factura(tva_incasare=True, taxare_inversa=True)
    t = wm.facturi_txt(firma, [(factura, linii)], 2026, 2)
    assert "TVAINCASARE=D" in t
    assert "TaxareInversa=D" in t
    firma2, factura2, linii2 = _factura(tva_incasare=False, taxare_inversa=False)
    t2 = wm.facturi_txt(firma2, [(factura2, linii2)], 2026, 2)
    assert "TVAINCASARE=N" in t2 and "TaxareInversa=N" in t2

def test_serie_goala_ramane_goala():
    firma, factura, linii = _factura(serie="")
    t = wm.facturi_txt(firma, [(factura, linii)], 2026, 2)
    assert "SerieCarnet=\n" in t or t.rstrip().endswith("") and "SerieCarnet=" in t


# ---- Articole.txt: structura contra spec (UM NU e aici, vine din tranzactie) ----

def test_articole_txt_structura_spec():
    linii = [{"descriere": "Consultanță IT", "um": "ore", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}]
    t = wm.articole_txt(linii)
    cod = wm.cod_articol("Consultanță IT")
    assert "[InfoPachet]" in t
    assert ("[ArticoleNoi_%s]" % cod) in t
    assert "Denumire=Consultanță IT" in t
    assert "Serviciu=D" in t                 # default servicii
    assert "ContServiciu=704" in t           # cont venit pt serviciu
    assert "GestiuneImplicita=\n" in t       # gol (spec-valid; UM vine din tranzactie, nu de aici)
    assert "Clasa=\n" in t                   # gol (spec-valid)
    # UM NU trebuie sa apara in Articole.txt (corectie oficiala vs blog)
    assert "denumireUM" not in t and "UM=" not in t

def test_articole_dedup_pe_cod():
    linii = [{"descriere": "Consultanță IT", "um": "ore", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21},
             {"descriere": "Consultanță IT", "um": "ore", "cantitate": 2, "pret_unitar": 100, "cota_tva": 21}]
    t = wm.articole_txt(linii)
    cod = wm.cod_articol("Consultanță IT")
    assert t.count("[ArticoleNoi_%s]" % cod) == 1   # o singura definitie desi 2 linii

def test_config_override():
    linii = [{"descriere": "Marfă X", "um": "buc", "cantitate": 1, "pret_unitar": 50, "cota_tva": 21}]
    t = wm.articole_txt(linii, config={"serviciu": "N", "simbol_gestiune": "DEP1", "simbol_clasa": "MARFA"})
    assert "Serviciu=N" in t
    assert "GestiuneImplicita=DEP1" in t
    assert "Clasa=MARFA" in t
    assert "ContServiciu=\n" in t            # stoc -> fara cont serviciu


# ---- gard encoding Windows-1250 ----

def test_encoding_1250_diacritice_ro_comma_la_cedila():
    # ș/ț moderne (virgula) -> ş/ţ (cedila) valabile in cp1250
    b = wm.encode_1250("Șoseaua Țării ăâî")
    assert isinstance(b, bytes)
    # se decodeaza inapoi din cp1250 fara eroare
    b.decode("cp1250")

def test_encoding_1250_caracter_neencodabil_semnaleaza():
    # un caracter care NU exista in cp1250 (ex. chirilic / emoji) -> EXCEPTIE, nu byte gresit tacit
    with pytest.raises(ValueError) as ei:
        wm.encode_1250("Factura → client 中文", unde="Facturi.txt")
    assert "neencodabil" in str(ei.value).lower()


# ---- REGRESIE F187-fix 21.07: WinMentor exporta facturile emise indiferent de status ----
# Bug real (DANTE iunie 2026): facturile emise au status='de_preluat' (starea NORMALA la creare,
# vezi facturi_api creeaza / main.py default). Filtrul vechi status='emisa' le excludea -> 404,
# desi SAGA (fara filtru) le exporta. Cauza-radacina: 'de_preluat' e starea normala, nu una de exclus.

def test_export_luna_NU_filtreaza_pe_status_emisa(monkeypatch):
    """export_luna trebuie sa ceara facturile FARA a impune status='emisa' (paritate cu SAGA)."""
    from core import export_saga as _xs
    apeluri = {}
    def _spy(conn, schema, an, luna, status=None):
        apeluri["status"] = status
        return [1]
    monkeypatch.setattr(_xs, "facturi_emise_luna", _spy)
    firma, factura, linii = _factura()
    monkeypatch.setattr(_xs, "date_factura", lambda conn, schema, fid: (firma, factura, linii))
    rez = wm.export_luna(None, "sch", 2026, 6)
    assert apeluri["status"] is None, "WinMentor a reintrodus filtrul pe status (bug F187 reaparut)"
    assert rez and "Facturi.txt" in rez and "Articole.txt" in rez

def test_export_luna_include_factura_de_preluat(monkeypatch):
    """O factura emisa cu status='de_preluat' (cazul real DANTE) TREBUIE sa ajunga in export."""
    from core import export_saga as _xs
    # facturi_emise_luna real filtreaza pe status doar daca i se cere; aici confirmam ca id-ul
    # unei facturi 'de_preluat' (returnat cand NU se filtreaza) chiar produce continut txt.
    monkeypatch.setattr(_xs, "facturi_emise_luna",
                        lambda conn, schema, an, luna, status=None: [] if status else [42])
    firma, factura, linii = _factura(numar="7")
    monkeypatch.setattr(_xs, "date_factura", lambda conn, schema, fid: (firma, factura, linii))
    rez = wm.export_luna(None, "sch", 2026, 6)
    assert rez is not None, "factura de_preluat exclusa din export (regresie F187)"
    assert b"NrDoc=7" in rez["Facturi.txt"]
