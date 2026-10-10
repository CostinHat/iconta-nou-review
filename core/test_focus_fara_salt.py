# -*- coding: utf-8 -*-
"""[deficiența 159, retestul Costin 09.10.2026 — „ecranul tot sare: rândul atins urcă cu ~100 px”] `el.focus()` fără `preventScroll`
derulează elementul în centrul zonei când nu se vede întreg: la „Marchează depusă” lista sărea cu 100–475 px. Focusul trece prin
`api.focusFaraSalt` (fără derulare, apoi `nearest`) sau, unde nu se poate importa `api.js` (`reautentificare.js`, importat de el),
prin `.focus({ preventScroll: true })`. Gardul: niciun `.focus(` în static/js fără `preventScroll: true`."""
import glob
import io
import os
import re

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_FOCUS = re.compile(r"\.focus\((?!\{\s*preventScroll:\s*true\s*\})")


def focus_cu_salt(text):
    """Liniile (fără comentarii `//`) care cheamă `.focus(` fără `preventScroll: true`."""
    return [ln.strip() for ln in text.split("\n") if _FOCUS.search(ln.split("//", 1)[0])]


def test_niciun_focus_care_deruleaza_in_static_js():
    """MUTAȚIE: un `x.focus()` adăugat într-un ecran -> pică (vezi și testul sintetic de mai jos)."""
    rele = {}
    for f in glob.glob(os.path.join(_RAD, "static", "js", "**", "*.js"), recursive=True):
        r = focus_cu_salt(io.open(f, encoding="utf-8").read())
        if r:
            rele[os.path.relpath(f, _RAD)] = r
    assert not rele, "focus care derulează ecranul (folosește focusFaraSalt din api.js): %s" % rele


def test_gardul_vede_formele_focusului():
    """Anti-vacuu: gardul prinde formele întâlnite (simplă, opțională, în setTimeout) și lasă trecerea fără derulare."""
    assert focus_cu_salt("a.focus();\nb?.focus()\nsetTimeout(() => c.focus(), 0)") == [
        "a.focus();", "b?.focus()", "setTimeout(() => c.focus(), 0)"]
    assert focus_cu_salt("el.focus({ preventScroll: true });\n// x.focus() in comentariu") == []
