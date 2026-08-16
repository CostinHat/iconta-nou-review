# -*- coding: utf-8 -*-
"""GARD profil_blocaje: ecranul Date firma NU pretinde 'toate declaratiile se pot genera' cand un
camp e prezent-dar-invalid (CAEN in afara nomenclatorului D112 - Q1) sau vectorul TVA e necompletat
la platitor (periodicitate/data - Q8). Completitudinea verifica VALABILITATEA, nu doar prezenta."""
import io


def test_caen_nomenclator_d112():
    from core import d112
    assert d112.caen_in_nomenclator("6201") is True, "6201 e in enumerarea D112"
    assert d112.caen_in_nomenclator("6210") is False, "6210 NU e in enumerarea inchisa D112 (Q1)"
    assert d112.caen_in_nomenclator("") is True, "CAEN gol e camp obligatoriu, nu 'invalid pt D112'"


def test_firma_profil_expune_blocaje():
    src = io.open("core/firma_profil_api.py", encoding="utf-8").read()
    assert "def blocaje" in src, "lipseste functia blocaje in firma_profil_api"
    assert '"blocaje"' in src, "citeste_date nu intoarce blocaje"


def test_verdict_nu_mai_pretinde_toate_declaratiile():
    js = io.open("static/js/ecrane/date_firma.js", encoding="utf-8").read()
    assert "Toate declara" not in js, "verdictul inca pretinde 'toate declaratiile se pot genera' (Q1)"
    assert "d.blocaje" in js or "blocaje" in js, "ecranul nu randeaza blocajele de declaratii"
