# -*- coding: utf-8 -*-
"""[lotul 10, deficiența C69] e-Factura: numele, strada și localitatea vânzătorului și ale cumpărătorului — cerute, nu „-”.

Ce era (core/efactura_send.py `genereaza_xml`, înainte): `StreetName` = `adresa or "-"`, `CityName` = `oras or "-"`, `RegistrationName`
= `nume or "-"`, pentru ambele părți. Sursa: validatorul ANAF FACT1 (schematron CIUS-RO), probat 20.10.2026 pe XML sintetic din care
s-a scos câte un element (scratchpad N2/p_fact1.out): „[BR-RO-080]-Adresa Vanzatorului - Linia 1 (BT-35) trebuie furnizata”,
„[BR-RO-080]-Adresa Cumparatorului - Linia 1 (BT-50) trebuie furnizata” (BR-RO-082), „[BR-RO-090]-Localitatea Vanzatorului (BT-37)
trebuie furnizata” (BR-RO-091), „[BR-RO-090]-Localitatea Cumparatorului (BT-52) trebuie furnizata” (BR-RO-092), „[BR-06]-An Invoice
shall contain the Seller name (BT-27)”, „[BR-07]-An Invoice shall contain the Buyer name (BT-44)” — iar cu „-” FACT1 răspunde „ok”.
Fără rețea: generatorul e pur.
"""
import re
import xml.etree.ElementTree as ET

import pytest

from core import efactura_send as ef

_NS = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
       "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


def _adresa(xml, parte):
    """(StreetName, CityName) din PostalAddress-ul părții (`AccountingSupplierParty` / `AccountingCustomerParty`), citite din XML."""
    pa = ET.fromstring(xml.encode("utf-8")).find("cac:%s/cac:Party/cac:PostalAddress" % parte, _NS)
    return pa.findtext("cbc:StreetName", namespaces=_NS), pa.findtext("cbc:CityName", namespaces=_NS)

FACT = {"numar": "FCT77", "serie": "FCT", "data_emitere": "2026-10-19", "data_scadenta": "2026-11-18", "moneda": "RON",
        "directie": "emisa"}
LIN = [{"descriere": "Servicii", "um": "buc", "cantitate": 1, "pret_unitar": 100, "cota_tva": 21}]
FURN = {"nume": "FIRMA C69 SRL", "cui": "14399840", "adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "judet": "CJ",
        "platitor_tva": True, "reg_com": "J12/1/2020", "iban": "RO59BTRLRONCRT0C69TEST01"}
CLI = {"nume": "ALTEX ROMANIA SRL", "cui": "RO2864518", "adresa": "Bd. Biruintei 87", "oras": "Pantelimon", "judet": "IF", "tara": "RO"}


def test_cu_datele_partilor_xml_le_poarta_pe_ale_lor():
    x = ef.genereaza_xml(FACT, LIN, FURN, CLI)
    assert _adresa(x, "AccountingSupplierParty") == ("Str. Probei 9", "Cluj-Napoca")       # BT-35 / BT-37 ale vânzătorului
    assert _adresa(x, "AccountingCustomerParty") == ("Bd. Biruintei 87", "Pantelimon")     # BT-50 / BT-52 ale cumpărătorului
    assert ">-<" not in x


@pytest.mark.parametrize("parte,cheie,regula", [
    ("v", "nume", "BR-06"), ("v", "adresa", "BR-RO-080"), ("v", "oras", "BR-RO-090"),       # BT-27, BT-35, BT-37
    ("c", "nume", "BR-07"), ("c", "adresa", "BR-RO-082"), ("c", "oras", "BR-RO-092"),       # BT-44, BT-50, BT-52
])
def test_lipsa_opreste_trimiterea_cu_campul_numit(parte, cheie, regula):
    f, c = dict(FURN), dict(CLI)
    (f if parte == "v" else c)[cheie] = ""
    with pytest.raises(ef.EDateIncomplete) as ei:
        ef.genereaza_xml(FACT, LIN, f, c)
    assert regula in str(ei.value) and "„-”" in str(ei.value)      # regula ANAF numită; factura nu pleacă cu „-”
    d = ei.value.detaliu()
    if parte == "v":                                                 # datele firmei: butonul spre Date firmă, cu câmpul în vedere
        assert d["ecran"] == "date_firma" and d["camp_ecran"] in ("df-nume-portofoliu", "df-adresa", "df-oras")
    else:
        assert d["ecran"] is None


def test_randul_fara_denumire_nu_pleaca_cu_liniuta():
    """Generalizarea clasei în același fișier: `<cbc:Name>` al articolului (BT-153) era `descriere or "-"`. FACT1 (probat 20.10.2026): „[BR-25]-Each
    Invoice line (BG-25) shall contain the Item name (BT-153).”, iar cu „-” răspunde „ok” — emiterea îl cere deja, deci rămâne numai factura veche / importată."""
    with pytest.raises(ef.EDateIncomplete) as ei:
        ef.genereaza_xml(FACT, [dict(LIN[0], descriere="  ")], FURN, CLI)
    assert re.findall(r"^Factura nu se poate trimite în e-Factura: (.+?) fără denumirea articolului \(rândul (.+?)\) — ANAF o cere "
                      r"\(regula (BR-\d+), (BT-\d+)\)", str(ei.value)) == [("un rând e", "1", "BR-25", "BT-153")], str(ei.value)   # BT-153, rândul numit


def test_bucuresti_localitatea_din_sectorul_adresei_nu_e_inventata():
    c = dict(CLI, oras="", judet="B", adresa="Str. Lunga 3, Sector 2")
    x = ef.genereaza_xml(FACT, LIN, FURN, c)
    assert _adresa(x, "AccountingCustomerParty")[1] == "SECTOR2"     # BR-RO-100: sectorul, citit din adresă (dată a facturii)


def test_clientul_cu_judet_dar_fara_localitate_o_ia_din_anaf(monkeypatch):
    """`efactura_trimitere.completeaza_client_ro`: localitatea lipsă (cu județul scris) — din ANAF, ca județul (C61)."""
    from core import efactura_trimitere as et, uc_comun
    monkeypatch.setattr(uc_comun, "_platitor_tva_tert",
                        lambda cui, tara="RO", adresa=None: (adresa.update({"localitate": "Pantelimon", "judet": "IF"}) or True))
    out = et.completeaza_client_ro(dict(CLI, oras=""))
    assert out["oras"] == "Pantelimon" and out["judet"] == "IF"
