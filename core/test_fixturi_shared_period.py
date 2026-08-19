# -*- coding: utf-8 -*-
"""[Verificare funcțională reală] GARD: o fixtură de test care scrie într-un tabel PARTAJAT period-keyed
(`public.declaratii_depuse` / `public.declaratii_coada`) trebuie să poarte marker `# fixtura-sintetica-ok:`
(tenant_id sintetic / rollback) SAU să folosească anul sintetic 2099 — altfel PICĂ.

Lecție 22.07: prima depunere reală D300 tenant_002 2026/06 a coliziat de PK cu un test care insera fabricat
pe aceeași perioadă → „verde azi, roșu mâine" fără schimbare de cod. Marker-ul face alegerea sigură CONȘTIENTĂ.
"""
import os
import re
import glob
import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_TAB = re.compile(r"public\.(declaratii_depuse|declaratii_coada)\b")


def test_fixturi_shared_period_marcate():
    rele = []
    for f in glob.glob(os.path.join(_RAD, "core", "test_*.py")):
        lines = open(f, encoding="utf-8").read().split("\n")
        for i, ln in enumerate(lines):
            if _TAB.search(ln) and "INSERT" in ln:
                fer = "\n".join(lines[max(0, i - 5):i + 5])
                if "fixtura-sintetica-ok:" in fer or re.search(r"\b2099\b", fer):
                    continue
                rele.append("%s:%d" % (os.path.basename(f), i + 1))
    assert not rele, ("fixtură pe tabel PARTAJAT period-keyed fără marker `# fixtura-sintetica-ok:` și fără an "
                      "2099 (risc de coliziune PK cu depunerea reală - bug 22.07): %s" % rele)
