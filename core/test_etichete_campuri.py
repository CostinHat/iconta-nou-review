# -*- coding: utf-8 -*-
"""GARD — niciun câmp de formular fără etichetă accesibilă (clasa găsită 04.10.2026).

La proba UI a schimbării salariului, axe a semnalat „Form elements must have labels” pe câmpurile zonei (eticheta vizibilă
era un `<span>`). Generalizarea pe toată aplicația a găsit 54 de câmpuri în 17 fișiere (etichetă în `<span>` sau `<label>`
vecin nelegat) — toate reparate (`for` pe eticheta vecină, altfel `aria-label` cu textul etichetei). axe vede doar ecranele
pe care le deschide; zonele inline și dialogurile nu — de aceea gardul e static, pe șabloane (`scripts/scan_etichete_campuri.py`).
WCAG 2.1 — 1.3.1 / 4.1.2 (nume accesibil pentru controalele de formular).
"""
from scripts import scan_etichete_campuri as _s


def test_niciun_camp_fara_eticheta():
    # MUTAȚIE: aria-label scos de pe #salariu-data -> listat aici -> pică
    assert _s.neetichetate() == []


def test_scanerul_vede_formele_clasei(tmp_path):
    # ANTI-VACUU: span-etichetă și label vecin nelegat sunt prinse; label cu for, label care învelește, aria-label și
    # input-ul de fișier ascuns nu
    d = tmp_path / "static" / "js"
    d.mkdir(parents=True)
    (d / "x.js").write_text(
        '<span class="camp-eticheta">Salariu</span><input id="a" class="camp-input">\n'
        '<label class="camp-eticheta">CUI</label>\n<input id="b">\n'
        '<label for="c">C</label><input id="c">\n'
        '<label class="camp"><span>D</span><input id="d"></label>\n'
        '<input id="e" aria-label="E">\n'
        '<input type="file" id="f" hidden>\n', encoding="utf-8")
    assert _s.neetichetate(str(tmp_path)) == [("static/js/x.js", 1, "a"), ("static/js/x.js", 3, "b")]
