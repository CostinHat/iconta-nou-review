# -*- coding: utf-8 -*-
"""core/test_garzi_mesaje_afisabile.py — GARD STRUCTURAL (C-5, pct.5 Costin): niciun test nu asertează
pe EGALITATE EXACTĂ cu textul unui mesaj AFIȘABIL (detail/mesaj/eroare/str(exceptie)).

De ce: un mesaj rescris cap.6 (explicit + diacritice) NU trebuie să spargă un test. Riscul dispare
STRUCTURAL, nu prin disciplină: testele asertează pe COD/TIP/status (contractul stabil) sau pe SUBSTRING
(`in`, un cuvânt-cheie care supraviețuiește rescrierii), niciodată pe șirul afișabil complet.

Suita curentă respectă deja convenția (zero situri fragile). Gardul o păstrează: dacă reapare tiparul
`<canal_mesaj> == "text cu spații"`, PICĂ, cu indicație să rescrii pe cod/substring.
"""
import glob
import io
import re

_TESTE = sorted(glob.glob("core/test_*.py"))
_ACEST = "test_garzi_mesaje_afisabile.py"

# canal de mesaj afișabil (user-facing) urmat de == "text multi-cuvânt" (are cel puțin un spațiu)
_CANAL = (r'(\[\s*["\']detail["\']\s*\]|\[\s*["\']mesaj["\']\s*\]|\[\s*["\']eroare["\']\s*\]'
          r'|str\(\s*ei\.value\s*\)|str\(\s*e\s*\)|\.detail)')
_RE_FRAGIL = re.compile(_CANAL + r'\s*==\s*(["\'])(?P<txt>[^"\']*\s[^"\']*)\2')


def test_niciun_test_aserteaza_pe_sir_de_mesaj_afisabil():
    if not _TESTE:
        import pytest
        pytest.skip("core/test_*.py absent (rulare in afara radacinii)")
    fragile = []
    for f in _TESTE:
        if f.endswith(_ACEST):
            continue
        for i, lin in enumerate(io.open(f, encoding="utf-8").read().split("\n"), 1):
            m = _RE_FRAGIL.search(lin)
            if m:
                fragile.append("%s:%d  == %r" % (f.split("/")[-1], i, m.group("txt")[:44]))
    assert not fragile, (
        "Aserție FRAGILĂ pe șir de mesaj afișabil (o rescriere cap.6 ar sparge testul). "
        "Rescrie pe cod/tip/status SAU pe SUBSTRING (`\"cuvant-cheie\" in ...`), nu pe textul complet:\n"
        + "\n".join(fragile))
