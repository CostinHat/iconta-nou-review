# -*- coding: utf-8 -*-
"""GARD — parametrul unei funcții interioare nu acoperă parametrul funcției care o conține (lotul 5, comanda 4; prins de rularea
țintită pe 16.10.2026: 244 și 245 picau și pe commitul comenzii 3).

Cazul care a deschis clasa: comanda 3 (265) i-a dat lui `deseneaza` din `ecranJurnal(corp, nav, t, opt)` parametrul `opt = {}`
(`{ peLoc }`). De atunci `opt.evidentiaza` din `deseneaza` citea obiectul gol, iar Registrul jurnal deschis din Bilanț nu mai
evidenția notele de închidere propuse (244). Nicio eroare: numele exista, doar că era altul. Detectorul
(`scripts/scan_parametri_umbriti.js`) citește arborele sintactic al fiecărui fișier din `static/js` (acorn).

Măsurat pe 16.10.2026: 6 apariții — cea din jurnal (defectul) și 5 benigne (`c`, `t` refolosite într-o funcție interioară care nu
citea numele exterior), redenumite toate, ca regula să fie „zero”, nu „zero care contează”.
Limita, declarată: numai parametrii; o variabilă `let` / `const` din corp care acoperă un parametru exterior nu e în clasă.
"""
import json
import os
import subprocess

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCAN = os.path.join(_RAD, "scripts", "scan_parametri_umbriti.js")


def _scan(*fisiere):
    r = subprocess.run(["node", _SCAN, *fisiere], cwd=_RAD, capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, "detectorul nu a putut citi sursele (fail-closed): %s" % r.stderr[-500:]
    return json.loads(r.stdout)


def test_niciun_parametru_interior_nu_acopera_unul_exterior():
    """MUTAȚIE: `deseneaza = async (opt = {})` pus înapoi în `ecranJurnal` -> pică, cu linia și numele."""
    gasite = _scan()
    assert not gasite, "Parametri care acoperă parametrul funcției exterioare (corpul interior citește alt obiect decât crezi):\n" + \
        "\n".join("  %(fisier)s:%(linie)s %(functie)s(%(nume)s) — acoperă parametrul funcției de la linia %(linie_exterioara)s" % g
                  for g in gasite)


def test_detectorul_are_dinti(tmp_path):
    """Fiecare formă de parametru e prinsă (simplu, cu valoare implicită, destructurat, `...rest`, la orice adâncime); numele nou și
    funcțiile surori (nu imbricate) trec."""
    f = tmp_path / "proba.js"
    f.write_text(
        'export function e1(corp, opt = {}) { const d = async (opt = {}) => opt.peLoc; return d; }\n'
        'export function e2(t) { [1].forEach(([c, t]) => c + t); }\n'
        'export function e3(a) { return function ({ a: x, b }) { return () => (...a) => a; }; }\n'
        'export function ok1(opt) { const d = (mod = {}) => mod.peLoc && opt.an; return d; }\n'
        'export function ok2(c) { return c; }\nexport function ok3(c) { return c; }\n', encoding="utf-8")
    assert sorted((g["functie"], g["nume"]) for g in _scan(str(f))) == [("(anonimă)", "a"), ("(anonimă)", "t"), ("d", "opt")]
