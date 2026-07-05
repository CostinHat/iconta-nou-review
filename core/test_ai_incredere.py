# -*- coding: utf-8 -*-
from core.ai_incredere import normalizeaza, evalueaza


def test_normalizare():
    assert normalizeaza("Plata OMV 1234 - motorina!!") == "plata omv motorina"
    assert normalizeaza("") == ""


def test_sigur():
    ist = [{"cont_final": "6022", "corectat": False}] * 4
    e = evalueaza(ist)
    assert e["incredere"] == "sigur" and e["cont"] == "6022"


def test_de_verificat():
    ist = [{"cont_final": "628", "corectat": True},
           {"cont_final": "6022", "corectat": True},
           {"cont_final": "628", "corectat": False}]
    e = evalueaza(ist)
    assert e["incredere"] == "de_verificat"


def test_probabil_istoric_scurt():
    ist = [{"cont_final": "6022", "corectat": False}]
    e = evalueaza(ist)
    assert e["incredere"] == "probabil"


def test_invatare_cont_recent():
    ist = [{"cont_final": "628", "corectat": True},
           {"cont_final": "6022", "corectat": False},
           {"cont_final": "6022", "corectat": False}]
    assert evalueaza(ist)["cont"] == "628"
