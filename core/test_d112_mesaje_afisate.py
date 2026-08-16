# -*- coding: utf-8 -*-
"""GARD d112_mesaje_afisate: mesajele de business ridicate cu `raise ValueError(...)` din d112.py
ajung la utilizator (control_incrucisat le pune in remediu.cauza via str(e)). Sunt TEXT AFISAT ->
diacritice, nu ASCII de log. Garda de diacritice generala (test_diacritice_afisate.py) NU scaneaza
`raise ValueError` inline - unghi mort dovedit la mesajul CAEN (Q2). Aici acoperim acel unghi in d112."""
import io
import re


def test_raise_valueerror_din_d112_are_diacritice():
    src = io.open("core/d112.py", encoding="utf-8").read()
    probleme = []
    for m in re.finditer(r"raise ValueError\((.*?)\)", src, re.S):
        text = "".join(re.findall(r'"([^"]*)"', m.group(1)))
        if len(text) < 30:            # markere/coduri scurte, nu proza afisata
            continue
        if not re.search(r"[ăâîșțĂÂÎȘȚ]", text):
            probleme.append(text[:70])
    assert not probleme, "mesaje ValueError AFISATE (via control_incrucisat cauza) fara diacritice in d112.py: %r" % probleme
