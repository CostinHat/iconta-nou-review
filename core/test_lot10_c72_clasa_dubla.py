# -*- coding: utf-8 -*-
"""[lotul 10, C72 — găsită de e2e la 428 (afiliatul)] Ecranul Clienți dădea lui `api.selectDaNu` atributele `class="cl-afiliat" …`, iar
helperul scria deja `class="camp-input"`: browserul păstrează numai PRIMUL atribut `class` al unui element, deci selectul n-avea
`cl-afiliat`, ascultătorul „change” nu se lega și „Salvează” rămânea inactiv pentru totdeauna (bifa „Persoană afiliată” nu se putea
salva din ecran). Reparația e în helper: clasa apelantului se unește cu `camp-input`.
GARDĂ: (1) comportamentul helperului, rulat în Node pe sursa reală; (2) clasa: niciun șablon din `static/js` nu scrie același atribut
(`class` / `id`) de două ori pe un element; (3) niciun helper din `api.js` nu mai pune un `class` fix lângă atributele apelantului.
MUTAȚIE: helperul vechi (`<select class="camp-input" … ${atribute}>`) -> (1) și (3) pică."""
import glob
from html.parser import HTMLParser
import io
import json
import os
import re
import shutil
import subprocess

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_API = os.path.join(_RAD, "static", "js", "api.js")


def _sursa_helper():
    s = io.open(_API, encoding="utf-8").read()
    a = s.index("export function selectDaNu(")
    return s[a:s.index("\n}\n", a) + 3].replace("export ", "")


def _atribute(html):
    """Atributele primului element din `html`, ca listă de perechi, cu tot cu dublurile (exact ce scrie șablonul, înainte ca browserul
    să păstreze numai primul `class`)."""
    class _P(HTMLParser):
        atr = None

        def handle_starttag(self, tag, attrs):
            if self.atr is None:
                self.atr = attrs
    p = _P()
    p.feed(html)
    return p.atr


@pytest.mark.skipif(not shutil.which("node"), reason="node lipsește")
def test_clasa_apelantului_se_uneste_cu_camp_input():
    js = ("const esc = (x) => String(x); const ALEGE = '<option value=\"\">— alege —</option>';\n" + _sursa_helper() +
          "\nconsole.log(JSON.stringify([selectDaNu('class=\"cl-afiliat\" id=\"cl-afiliat-c1\" data-cheie=\"c1\"', false, 'Afiliat'), "
          "selectDaNu('id=\"x\"', true)]));")
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    cu_clasa, fara = json.loads(r.stdout)
    a_cu, a_fara = _atribute(cu_clasa), _atribute(fara)
    assert [v for k, v in a_cu if k == "class"] == ["camp-input cl-afiliat"], cu_clasa   # un singur `class`, cu clasa apelantului
    assert {k: v for k, v in a_cu if k in ("id", "data-cheie")} == {"id": "cl-afiliat-c1", "data-cheie": "c1"}, cu_clasa
    assert [v for k, v in a_fara if k == "class"] == ["camp-input"], fara
    assert [v for k, v in a_fara if k == "id"] == ["x"], fara


_DUBLU = re.compile(r'<[a-z][a-z0-9]*\b[^<>`]*?\s(class|id)="[^"]*"[^<>`]*?\s\1=')


def test_niciun_sablon_nu_scrie_acelasi_atribut_de_doua_ori():
    rele = []
    for f in glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True):
        for i, ln in enumerate(io.open(f, encoding="utf-8"), 1):
            if _DUBLU.search(ln):
                rele.append("%s:%d" % (os.path.relpath(f, _RAD), i))
    assert rele == [], rele


def test_scanul_vede_forma_rea():
    """Anti-vacuu."""
    assert _DUBLU.search('<select class="camp-input" aria-label="x" class="cl-afiliat">')
    assert not _DUBLU.search('<div class="pr-rand" data-id="1" id="pr-1">')


def test_niciun_helper_nu_pune_clasa_fixa_langa_atributele_apelantului():
    s = io.open(_API, encoding="utf-8").read()
    rele = re.findall(r'<[a-z]+ class="[a-z][^"$]*"[^>`]*\$\{atribute\}', s)
    assert rele == [], rele
