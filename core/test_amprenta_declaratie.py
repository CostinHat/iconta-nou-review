# -*- coding: utf-8 -*-
"""core/test_amprenta_declaratie.py — GARD C3 (snapshot+hash): regenerare-diff prinde editarea retroactiva."""
import pytest
from core.amprenta_declaratie import amprenta, verifica_regenerare, DeclaratieModificataDupaDepunere
from core.test_pull_declaratii import schema, SCHEMA_T, _db_ok   # reutilizeaza fixtura DB efemera


def test_amprenta_determinista():
    """Aceeasi declaratie (normalizata) -> aceeasi amprenta; reformatarea (spatii intre taguri) NU schimba amprenta."""
    x1 = '<d><a v="1"/><b v="2"/></d>'
    x2 = '<d>\n  <a v="1"/>\n  <b v="2"/>\n</d>'   # reformatat
    assert amprenta(x1) == amprenta(x2)
    assert amprenta(x1) != amprenta('<d><a v="9"/><b v="2"/></d>')   # continut diferit -> amprenta diferita


def test_verifica_regenerare_amprenta_lipsa_semnaleaza():
    """Regula bazei nule: amprenta depusa LIPSA nu se ia drept 'coincide' - se ridica."""
    with pytest.raises(DeclaratieModificataDupaDepunere):
        verifica_regenerare("<d/>", None)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_regenerare_prinde_editarea_retroactiva_MUTATIE(schema):
    """[C3 snapshot+hash] La depunere se ingheata amprenta D112. Regenerarea pe ACELEASI date -> aceeasi amprenta
    (deterministic). MUTATIE: editare retroactiva (schimb salariul in luna deja 'depusa') -> amprenta DIFERA ->
    verifica_regenerare ridica. Non-tautologie: prezent (regenerare) vs sinele trecut (amprenta), axa TIMP -
    schema NU previne editarea retroactiva, DUK nu vede istoria."""
    from core import d112
    with schema.cursor() as cur:
        cur.execute("INSERT INTO salariati (id,nume,prenume,cnp,data_angajare,salariu_brut,ore_zi,part_time) "
                    "OVERRIDING SYSTEM VALUE VALUES (1,'S','A','1900101410011','2025-01-01',6000,8,false)")
        cur.execute("INSERT INTO salariu_istoric (salariat_id,valabil_din,salariu_brut) VALUES (1,'2025-01-01',6000)")
    xml1, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    a_depusa = amprenta(xml1)
    # DETERMINISM: regenerare pe aceleasi date -> aceeasi amprenta
    xml2, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    assert amprenta(xml2) == a_depusa, "regenerarea pe aceleasi date trebuie deterministica (aceeasi amprenta)"
    assert verifica_regenerare(xml2, a_depusa) is True
    # MUTATIE: editare retroactiva a salariului in luna deja depusa
    with schema.cursor() as cur:
        cur.execute("UPDATE salariu_istoric SET salariu_brut=8000 WHERE salariat_id=1")
    xml3, _ = d112.genereaza(schema, SCHEMA_T, 2026, 6)
    assert amprenta(xml3) != a_depusa, "dupa editare retroactiva amprenta trebuie sa DIFERE"
    with pytest.raises(DeclaratieModificataDupaDepunere):
        verifica_regenerare(xml3, a_depusa)
