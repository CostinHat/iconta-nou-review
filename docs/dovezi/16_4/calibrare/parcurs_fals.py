# -*- coding: utf-8 -*-
"""Parcurs fals pentru calibrarea 16.4 pct.2 (v): intră în parcurs, anunță prin fișierul din CALIB_MARCA și așteaptă să fie oprit. Nu scrie rânduri, nu apelează Haiku."""
import os
import time


def ruleaza(pagina, ctx):
    open(os.environ["CALIB_MARCA"], "w").write("in parcurs\n")
    time.sleep(120)
