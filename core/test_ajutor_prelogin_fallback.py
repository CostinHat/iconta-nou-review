# -*- coding: utf-8 -*-
"""GARD ajutor_prelogin: handlerul global al semnului "?" nu depinde DOAR de _navGlobal (shell
autentificat, montat abia dupa login). Pe ecranele pre-login trebuie sa randeze ajutorul intr-un
overlay propriu, nu sa taca. Tiparul: orice "?" pus pre-autentificare."""
import io


def test_semn_ajutor_are_fallback_prelogin():
    src = io.open("static/js/api.js", encoding="utf-8").read()
    assert "_ajutorOverlayLiber" in src, "lipseste helperul de fallback pre-login in api.js"
    assert "if (window._navGlobal)" in src, "handlerul ? nu mai testeaza _navGlobal"
    # ramura de fallback: dupa branch-ul _navGlobal se cheama overlay-ul liber
    poz_if = src.find("if (window._navGlobal)")
    poz_fb = src.find("_ajutorOverlayLiber(titlu, _randeazaAjutor(a))")
    assert poz_fb > poz_if > 0, "nu exista ramura de fallback dupa testul _navGlobal"
