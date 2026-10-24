# -*- coding: utf-8 -*-
"""[deficiența 325, comanda Costin 8.1 pct.2, 18.10.2026, verbatim în DECIZII „Comanda 8.1”] „nicio listă, fereastră, formular sau card nu
se deschide fără clicul utilizatorului. Pune-o ca gardă, ca să nu mai revină.”

Garda vie e în plasa e2e (`frontend_test/e2e/conftest.py::GARDA_DESCHIDERI`, în fiecare ecran `_ecran`). Aici partea statică, care o
ține întreagă:
- garda din plasă nu poate dispărea / slăbi tăcut (focusul pe liste, `showPicker`, ferestrele dinaintea primului gest, aserțiunea finală);
- ferestrele pe care aplicația le deschide singură prin DECIZIE sunt exact cele aprobate — o fereastră nouă marcată
  `data-deschidere="aplicatie"` ca să scape de gardă pică aici până intră în listă, cu decizia ei;
- niciun `showPicker(` și niciun `autofocus` pe o listă în static (deschid lista din cod).
"""
import ast
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC = os.path.join(RAD, "static")

#: fișier -> de ce se deschide fără clic (decizia)
DESCHISE_DE_APLICATIE = {
    "static/js/ecrane/ansamblu.js": "bun venit, la prima logare (bun_venit_v1)",
    "static/js/ecrane/inceput.js": "prima intrare, „Înainte de a începe” (telefonul, canalul, notificările): obligatorie înaintea aplicației "
                                   "(decizia 320); fereastră din lotul 12 (deficiențele 561 / 596, DESIGN_SYSTEM cap.12b)",
    "static/js/navigator.js": "anunțul iConta către utilizatori (anunt_modal_v2)",
    "static/js/reautentificare.js": "sesiunea a expirat: reautentificarea, ca să nu se piardă lucrul",
}


def _js():
    for d, _s, fs in os.walk(STATIC):
        for f in fs:
            if f.endswith((".js", ".html")):
                cale = os.path.join(d, f)
                yield os.path.relpath(cale, RAD), open(cale, encoding="utf-8").read()


def _functii(cale):
    arb = ast.parse(open(os.path.join(RAD, cale), encoding="utf-8").read())
    return arb, {n.name: n for n in ast.walk(arb) if isinstance(n, ast.FunctionDef)}


def test_325_garda_din_plasa_e_intreaga():
    """Pe AST, nu pe text: scriptul gărzii există, e pus pe fiecare ecran al plasei (`_ecran`), iar deschiderile notate pică testul.
    Ce notează scriptul (focus pe listă, `showPicker`, fereastra dinaintea primului gest) e dovedit de comportament, în plasă:
    `e2e_lot81.py::test_def_325_garda_noteaza_focusul_showpicker_si_fereastra_din_cod` le provoacă pe toate trei și le cere exact."""
    arb, fn = _functii(os.path.join("frontend_test", "e2e", "conftest.py"))
    scripturi = [n.value.value for n in arb.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
                 and [getattr(x, "id", None) for x in n.targets] == ["GARDA_DESCHIDERI"]]
    assert len(scripturi) == 1 and scripturi[0].strip(), "scriptul GARDA_DESCHIDERI a dispărut din conftest-ul plasei"
    puse = [c for c in ast.walk(fn["_ecran"]) if isinstance(c, ast.Call) and getattr(c.func, "attr", None) == "add_init_script"
            and [getattr(a, "id", None) for a in c.args] == ["GARDA_DESCHIDERI"]]
    assert len(puse) == 1, "garda nu mai e pusă pe ecranele plasei (_ecran)"
    pica = [a for a in ast.walk(fn["_ecran"]) if isinstance(a, ast.Assert) and isinstance(a.test, ast.UnaryOp)
            and isinstance(a.test.op, ast.Not) and getattr(a.test.operand, "id", None) == "singure"]
    assert len(pica) == 1, "deschiderile notate nu mai pică testul (assert not singure în _ecran)"
    _a, teste = _functii(os.path.join("frontend_test", "e2e", "e2e_lot81.py"))
    assert set(teste) >= {"test_def_325_garda_noteaza_focusul_showpicker_si_fereastra_din_cod"}, "proba de comportament a gărzii a dispărut"


def test_325_ferestrele_deschise_de_aplicatie_sunt_cele_aprobate():
    gasite = {cale for cale, t in _js() if re.search(r'data-deschidere="aplicatie"|dataset\.deschidere\s*=\s*"aplicatie"', t)}
    assert gasite == set(DESCHISE_DE_APLICATIE), (
        "fereastră deschisă fără clic, neaprobată (sau una aprobată a dispărut): %s" % sorted(gasite ^ set(DESCHISE_DE_APLICATIE)))


def test_325_nicio_lista_deschisa_din_cod():
    rele = []
    for cale, t in _js():
        for m in re.finditer(r"\.showPicker\s*\(|<select\b[^>]*\bautofocus\b", t):
            rele.append("%s:%d %s" % (cale, t[:m.start()].count("\n") + 1, m.group(0)[:40]))
    assert not rele, "lista se deschide din cod, fără clicul omului: %s" % rele
