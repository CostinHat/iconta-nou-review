# -*- coding: utf-8 -*-
import uuid
import xml.etree.ElementTree as ET
import pytest
from core import reges_client as m

AID = str(uuid.uuid4())

def _valid_xml(x):
    root = ET.fromstring(x)
    assert root.tag.endswith("}Message")

def test_inregistrare_salariat():
    x = m.mesaj_inregistrare_salariat(
        {"cnp": "1800612015459", "nume": "Popescu", "prenume": "Ion",
         "adresa": "Str. X & Y <1>"}, AID, "costin")
    _valid_xml(x)
    assert 'xsi:type="Salariat"' in x
    assert "<Operation>InregistrareSalariat</Operation>" in x
    assert "<Nume>POPESCU</Nume>" in x
    assert "&amp;" in x and "&lt;1&gt;" in x

def test_salariat_fara_cnp():
    with pytest.raises(ValueError):
        m.mesaj_inregistrare_salariat({"nume": "X"}, AID, "c")

def test_adaugare_contract():
    ref = str(uuid.uuid4())
    x = m.mesaj_adaugare_contract(
        {"numar": "12", "data_contract": "2026-07-01", "data_inceput": "2026-07-06",
         "salariu": 4500, "cor": "251204"}, ref, AID, "costin")
    _valid_xml(x)
    assert f"<Id>{ref}</Id>" in x
    assert "<Salariu>4500</Salariu>" in x

def test_contract_camp_lipsa():
    with pytest.raises(ValueError, match="salariu"):
        m.mesaj_adaugare_contract({"numar": "1", "data_contract": "2026-01-01",
                                   "data_inceput": "2026-01-01", "cor": "1"},
                                  str(uuid.uuid4()), AID, "c")

def test_incetare():
    x = m.mesaj_incetare_contract(str(uuid.uuid4()), "2026-08-01", "Art55LitB",
                                  "Acord parti", AID, "c")
    _valid_xml(x)
    assert 'xsi:type="ActiuneIncetare"' in x

def test_medii():
    assert "dev.inspectiamuncii.org" in m.RegesClient("u", "p", "test").api
    assert m.RegesClient("u", "p", "prod").api == "https://api.inspectiamuncii.ro"
