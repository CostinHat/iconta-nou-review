# -*- coding: utf-8 -*-
"""GARD — un formular nu cere de la om un ID intern (decizia Costin 07.10.2026, C4).

Instanța: „ID mijloc fix” (reevaluare, casare) era un câmp numeric — contabilul trebuia să știe ID-ul din baza de date, iar
refuzul îi cerea „Alege-l din listă” fără ca lista să existe. Acum: listă din registrul activelor firmei (`GET mijloace-fixe`).
CE FACE IMPOSIBIL: un câmp `*_id` tastabil (numar / text) în registrul ecranului „Operațiuni speciale”; `mijloc_fix_id` altfel decât
listă. Măsurat la 07.10: nicio altă apariție a clasei în ecrane. LIMITA: vede registrul `C(...)`; un `<input>` scris de mână
într-un alt ecran, cu alt nume decât `*_id`, nu se vede.
"""
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(RAD, "static/js/ecrane/operatiuni_ecran.js"), encoding="utf-8").read()


def test_niciun_id_intern_tastabil():
    """MUTAȚIE: `C("mijloc_fix_id", "ID mijloc fix", "numar", …)` pus la loc -> pică."""
    assert re.findall(r'C\("([a-z_]*_id)", "[^"]*", "(?:numar|text)"', SRC) == []


def test_mijlocul_fix_se_alege_din_registru():
    campuri = re.findall(r'C\("mijloc_fix_id", "[^"]*", "([a-z_]+)"', SRC)
    assert campuri == ["mijloc_fix", "mijloc_fix"]                        # reevaluare + casare
    assert re.search(r'api\.get\(`/tenants/\$\{t\.id\}/mijloace-fixe`\)', SRC)   # lista vine din registrul firmei
    assert re.search(r'c\.tip === "mijloc_fix" \? parseInt\(v, 10\)', SRC)      # se trimite ID-ul ales, numeric
