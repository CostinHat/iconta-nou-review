# -*- coding: utf-8 -*-
"""Teste F136 adeverinta — formatarea datei (partea pura). PDF-ul e testat functional."""
from datetime import date
from core.adeverinta import _d_ro


def test_d_ro_din_date():
    assert _d_ro(date(2026, 1, 5)) == "05.01.2026"

def test_d_ro_din_iso():
    assert _d_ro("2024-01-15") == "15.01.2024"

def test_d_ro_gol():
    assert _d_ro(None) == "" and _d_ro("") == ""
