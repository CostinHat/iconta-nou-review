# -*- coding: utf-8 -*-
"""[15.1-E5, R10] Niciun test de browser din core/ nu ia „azi” de la ceasul calendarului: ziua vine din `core.ceas_proba.DATA_REF`, iar pagina are același ceas fix."""
import glob
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_testele_de_browser_nu_iau_data_de_la_ceas():
    """MUTAȚIE: `AZI = datetime.date.today()` pus înapoi în core/test_lot13_firme2_ecrane.py -> pică."""
    rele = []
    for f in sorted(glob.glob(os.path.join(_RAD, "core", "test_*.py"))):
        t = open(f, encoding="utf-8").read()
        if re.search(r"\(browser[,)]|def _pagina\(browser", t) and re.search(r"\bdate\.today\(\)|datetime\.now\(\)", t.replace("datetime.date.today()", "date.today()")):
            rele.append(os.path.basename(f))
    assert rele == [], rele
