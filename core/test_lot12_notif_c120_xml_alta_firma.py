# -*- coding: utf-8 -*-
"""[lotul 12, C120 — clasa deficienței 599] „Import manual XML” (Facturi primite, `spv_receive.importa_xml_manual`): o factură e-Factura
între ALTE două firme (firma aleasă nu e nici furnizor, nici cumpărător) nu intră ca factură primită; refuzul numește firmele
(`efactura_import.alta_firma`, aceeași funcție ca la celelalte importuri). Schimbare cerută de pachetul `migr`, aplicată de `notif`.

Temei: N/A — regula de import (comanda Costin 12.1, 599: „compară firma din fișier cu firma aleasă și cere confirmare când diferă, la
toate importurile”); nu o valoare fiscală.
"""
import contextlib
import re

from core import spv_receive as sr

CUI_FIRMA = "14399840"            # DANTE INTERNATIONAL SA — cifra de control verificată (CLAUDE.md, algoritmul CUI)


class _Cur:
    def __init__(self, scrise):
        self.scrise = scrise

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, q, p=None):
        self.scrise.append(q)

    def fetchone(self):
        return (CUI_FIRMA,)


def _ruleaza(monkeypatch, factura):
    scrise = []

    class _Conn:
        def cursor(self, *a, **k):
            return _Cur(scrise)
    monkeypatch.setattr(sr.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_Conn()))
    monkeypatch.setattr(sr.efi, "extrage_fisiere", lambda nume, continut: [("f1.xml", b"<Invoice/>")])
    monkeypatch.setattr(sr.efi, "parseaza_xml", lambda xml, cif: dict(factura))
    rez = sr.importa_xml_manual("tenant_x", b"<Invoice/>", "f1.xml")
    # instrucțiunile care scriu: cuvântul INSERT oriunde în instrucțiune (și într-un `WITH … INSERT`), ca cuvânt al SQL-ului
    return rez, [q for q in scrise if {"INSERT"} & set(re.findall(r"[A-Z_]+", q.upper()))]


def test_def_c120_factura_intre_alte_doua_firme_nu_intra(monkeypatch):
    """MUTAȚIE: blocul `_alta = efi.alta_firma(f, cif)` scos din `importa_xml_manual` -> factura intră în `efactura_primite` -> pică."""
    factura = {"directie": "primita", "numar": "AB 12", "furnizor_nume": "Furnizor Alfa SRL", "furnizor_cui": "RO18547290",
               "cumparator_nume": "Alta Firmă SRL", "cumparator_cui": "RO6859662"}
    rez, inserari = _ruleaza(monkeypatch, factura)
    assert inserari == [], "factura altei firme a intrat în facturile primite"
    assert rez["importate"] == 0 and len(rez["erori"]) == 1, rez
    assert rez["erori"] == ["f1.xml: %s" % sr.efi.alta_firma(factura, CUI_FIRMA)], rez   # refuzul comun al importurilor (clasa 599)
    # refuzul numește factura și cele trei firme: furnizorul, cumpărătorul din fișier și firma aleasă
    assert rez["erori"][0].startswith("f1.xml: Factura AB 12 nu e a firmei") and re.findall(r"CUI (\d+)", rez["erori"][0]) == [
        "18547290", "6859662", CUI_FIRMA], rez


def test_c120_factura_catre_firma_trece_mai_departe(monkeypatch):
    """Factura către firmă trece de verificare și ajunge la scriere (aici oprită: a doua conexiune e a scrierii)."""
    import pytest

    class _LaScriere(Exception):
        pass
    apeluri = []

    class _Conn:
        def cursor(self, *a, **k):
            return _Cur([])

    def _get_conn(*a, **k):
        apeluri.append(1)
        if len(apeluri) > 1:
            raise _LaScriere()
        return contextlib.nullcontext(_Conn())
    monkeypatch.setattr(sr.db, "get_conn", _get_conn)
    monkeypatch.setattr(sr.efi, "extrage_fisiere", lambda nume, continut: [("f1.xml", b"<Invoice/>")])
    monkeypatch.setattr(sr.efi, "parseaza_xml", lambda xml, cif: {"directie": "primita", "numar": "AB 13", "furnizor_cui": "RO18547290",
                                                                   "cumparator_cui": "RO" + CUI_FIRMA})
    with pytest.raises(_LaScriere):
        sr.importa_xml_manual("tenant_x", b"<Invoice/>", "f1.xml")
