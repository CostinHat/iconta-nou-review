# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `scad` — gărzile STATICE ale claselor reparate (pe tot `static/js` și pe drumul validării facturii primite).

  469 „Scadențar: butonul ales apare gri, ca dezactivat; cel neales pare activ.” Clasa: o alegere de vedere marcată cu `disabled`
      (`${vedere === "x" ? " disabled" : ""}`): butonul ales arată ca unul care nu merge (DS cap.1 v2.87: „butonul dezactivat arată
      dezactivat”). Starea aleasă e `.buton-activ` (DS cap.1: „STARE (nu buton): marchează butonul cu zona toggle deschisă”) + aria-pressed.
  C105 „Validare factură” arăta TVA și Total brute („294.00”). Clasa: câmpurile text readonly cu sume, fără `bani()` (DESIGN_SYSTEM.md cap.4:
      sumele afișate trec prin `bani(v)`).
  477 Un singur drum de validare a facturii primite: `uc_tenants.factura_primita_valideaza` (XML) și `uc_factura_primita.factura_primita_manuala`
      (de mână) trec prin `uc_factura_primita.valideaza`; contarea și intrarea în stoc ale facturii primite nu se mai scriu a doua oară."""
import ast
import glob
import io
import os
import re

from core import arbore_js as _aj

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _js():
    for p in sorted(glob.glob(os.path.join(RAD, "static", "js", "**", "*.js"), recursive=True)):
        if {"vendor"} & set(os.path.relpath(p, RAD).split(os.sep)):
            continue
        yield os.path.relpath(p, RAD), io.open(p, encoding="utf-8").read()


#: alegerea unei vederi marcată prin `disabled`: `${x === "y" ? " disabled" : ""}` (sau `==`, sau `x === v` cu o variabilă)
_ALES_DEZACTIVAT = re.compile(r'\$\{\s*[\w.]+\s*===?\s*(?:["\'][^"\']*["\']|[\w.]+)\s*\?\s*["\']\s*disabled["\']\s*:\s*["\']{2}\s*\}')


def test_def_469_alegerea_unei_vederi_nu_se_marcheaza_dezactivata():
    """469. MUTAȚIE: în `scadentarEcran`, `vb` înapoi pe `${vedere === v ? " disabled" : ""}` -> pică, cu fișierul și linia."""
    surse = list(_js())
    assert len(surse) >= 50, len(surse)   # domeniul chiar se vede (static/js, fără vendor)
    gasite = [(f, s[:m.start()].count("\n") + 1, m.group(0)) for f, s in surse for m in _ALES_DEZACTIVAT.finditer(s)]
    assert not gasite, "vederea aleasă marcată `disabled` (arată ca un buton care nu merge) — folosește `.buton-activ` + aria-pressed: %s" % gasite


def test_def_469_scadentarul_marcheaza_vederea_aleasa_activa():
    # pe NOD (`core/arbore_js.py`): șablonul butonului de vedere, cu fiecare interpolare la locul ei — nu șirul căutat în sursă
    arb, cod = _aj.arbore_js("facturi_ecran.js")
    vb = [d["init"] for d in _aj.noduri(_aj.functia(arb, "scadentarEcran"), "VariableDeclarator") if d["id"].get("name") == "vb"]
    assert len(vb) == 1 and vb[0]["body"]["type"] == "TemplateLiteral", [cod(x) for x in vb]
    t = vb[0]["body"]
    assert [(q["value"]["cooked"], cod(e)) for q, e in zip(t["quasis"], t["expressions"])] == [
        ('<button class="buton-secundar', 'vedere === v ? " buton-activ" : ""'), ('" id="', "id"),
        ('" aria-pressed="', "vedere === v"), ('">', "text")], cod(t)


#: un câmp text readonly a cărui etichetă / id spune că ține o sumă
_SUMA = re.compile(r"(?i)\b(tva|total|sum[aă]|sold|valoare|pre[tț]|baz[aă])\b")


def test_def_c105_campurile_readonly_cu_sume_trec_prin_bani():
    """C105. Orice `<input … readonly>` care ține o sumă (eticheta / id: TVA, total, sumă, sold, valoare, preț, bază) primește valoarea
    formatată (`bani(` / `sumaCuMoneda(`), nu textul brut. MUTAȚIE: `value="${esc(sumaCuMoneda(p.tva, p.moneda))}"` înapoi pe
    `value="${esc(p.tva || "")}"` -> pică."""
    rele = []
    for f, s in _js():
        for m in re.finditer(r"<input\b[^>]*\breadonly\b[^>]*>", s):
            el = m.group(0)
            semn = " ".join(re.findall(r'(?:aria-label|id)="([^"]*)"', el))
            v = re.search(r'value="(\$\{.*?\})"', el)
            if v and _SUMA.search(semn) and not re.search(r"\b(bani|sumaCuMoneda)\(", v.group(1)):
                rele.append((f, s[:m.start()].count("\n") + 1, el[:160]))
    assert not rele, rele


def _functie(cale, nume):
    """Nodul AST al funcției `nume` din `cale`; exact una."""
    f = [n for n in ast.walk(ast.parse(io.open(os.path.join(RAD, cale), encoding="utf-8").read()))
         if isinstance(n, ast.FunctionDef) and n.name == nume]
    assert len(f) == 1, (cale, nume, len(f))
    return f[0]


def _apeluri(fn, chemat):
    """Argumentele (sursa fiecăruia) ale fiecărui apel `chemat(...)` din `fn`."""
    return [[ast.unparse(a) for a in n.args] for n in ast.walk(fn) if isinstance(n, ast.Call) and ast.unparse(n.func) == chemat]


def test_def_477_validarea_facturii_primite_are_un_singur_drum():
    """477. Factura din XML și cea de mână trec prin `uc_factura_primita.valideaza`; corpul validării din XML nu mai scrie el contarea /
    intrarea în stoc / clasificarea (a doua cale ar fi divergent la prima schimbare)."""
    xml = _functie("core/uc_tenants.py", "factura_primita_valideaza")
    man = _functie("core/uc_factura_primita.py", "factura_primita_manuala")
    assert [a[:3] for a in _apeluri(xml, "_ufp.valideaza")] == [["conn", "schema", "f"]], (
        "validarea facturii din XML nu trece prin `uc_factura_primita.valideaza`")
    assert [a[:3] for a in _apeluri(man, "valideaza")] == [["conn", "schema", "f"]]
    # nici chemată, nici numită (dată mai departe ca valoare): a doua cale de validare în uc_tenants
    numite = {n.id for n in ast.walk(xml) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(xml) if isinstance(n, ast.Attribute)}
    assert not numite & {"contabilizeaza", "intrare_din_factura", "actualizeaza_clasificarea", "actualizeaza_conturi_linii"}, (
        "a doua cale de validare în uc_tenants: %s" % sorted(numite & {"contabilizeaza", "intrare_din_factura", "actualizeaza_clasificarea",
                                                                        "actualizeaza_conturi_linii"}))
