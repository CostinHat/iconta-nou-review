# -*- coding: utf-8 -*-
"""core/arbore_js.py — ARBORELE SINTACTIC al unui fișier din `static/js` (acorn), pentru gărzile care asertează pe NOD, nu pe text.

DE UNDE VINE (21.10.2026, lotul 10): `core/test_garzi_pe_text.py` (clichetul aserțiunilor `"șir" in sursă`) a cerut ca gărzile ecranelor
din lot să citească structura — apelul cu argumentele lui, declarația cu inițializarea ei, condiția cu ramurile ei, elementul HTML cu
atributele lui —, fiindcă un șir căutat în sursă trece și dintr-un comentariu. Uneltele s-au scris întâi în `core/test_lot10b_facturi.py`
și erau importate de alte patru fișiere de test; locul lor e un modul comun, ca un fișier de test să nu depindă de altul.

Sora lui: `core/cititor_js.py` (albește textul, păstrează codul — pentru scanere pe regex). Aici se parsează de-a binelea: `node` cu acorn
din `/usr/share/nodejs` (aceeași sursă ca `scripts/scan_parametri_umbriti.js`). Fail-closed: un fișier pe care acorn nu-l citește oprește
garda, nu o trece.
"""
import html.parser
import io
import json
import os
import subprocess

from core.common import cate

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ── unealta ──────────────────────────────────────────────
# Gărzile de mai jos asertează pe NOD (apelul cu argumentele lui, declarația cu inițializarea ei, condiția cu ramurile ei, elementul HTML
# cu atributele lui), cu valoarea exactă — nu „șirul apare undeva în fișier”, care trece și dintr-un comentariu (`core/test_garzi_pe_text.py`).
_ACORN = ("const a = require('/usr/share/nodejs/acorn'); const s = require('fs').readFileSync(process.argv[1], 'utf8');"
          "process.stdout.write(JSON.stringify(a.parse(s, {ecmaVersion: 'latest', sourceType: 'module'})));")


def arbore_js(cale):
    """(arborele acorn al fișierului JS, `cod(nod)` = sursa nodului cu spațiile normalizate). Pozițiile acorn sunt în unități UTF-16."""
    cale = cale if os.path.isabs(cale) else os.path.join(RAD, "static", "js", "ecrane", cale)
    r = subprocess.run(["node", "-e", _ACORN, cale], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        raise RuntimeError("acorn nu a putut citi %s (fail-closed): %s" % (cale, r.stderr[-500:]))
    u16 = io.open(cale, encoding="utf-8").read().encode("utf-16-le")

    def cod(n):
        return " ".join(u16[2 * n["start"]:2 * n["end"]].decode("utf-16-le").split())
    return json.loads(r.stdout), cod


def noduri(n, tip):
    """Nodurile de tipul `tip` de sub `n` (inclusiv), în ordinea din sursă."""
    out, stiva = [], [n]
    while stiva:
        x = stiva.pop()
        if isinstance(x, dict):
            if x.get("type") == tip:
                out.append(x)
            stiva.extend(x.values())
        elif isinstance(x, list):
            stiva.extend(x)
    return sorted(out, key=lambda x: x["start"])


def functia(arb, nume):
    """Declarația funcției `nume` (oriunde în fișier, și imbricată); exact una."""
    f = [n for n in noduri(arb, "FunctionDeclaration") if n["id"]["name"] == nume]
    if len(f) != 1:
        raise LookupError("funcția %s: %s, se aștepta exact una" % (nume, cate(len(f), "declarație", "declarații")))
    return f[0]


def apeluri(n, cod, chemat):
    """Argumentele (sursa fiecăruia) ale fiecărui apel `chemat(...)` de sub `n`, în ordinea din sursă."""
    return [tuple(cod(a) for a in c["arguments"]) for c in noduri(n, "CallExpression") if cod(c["callee"]) == chemat]


def declaratii(n, cod):
    """{numele variabilei: [sursa inițializării, …]} pentru declarațiile de sub `n`."""
    out = {}
    for d in noduri(n, "VariableDeclarator"):
        if d["id"].get("type") == "Identifier" and d.get("init"):
            out.setdefault(d["id"]["name"], []).append(cod(d["init"]))
    return out


class _Elemente(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.gasite = []

    def handle_starttag(self, tag, attrs):
        self.gasite.append((tag, dict(attrs)))


def elemente_html(n):
    """[(eticheta, {atribut: valoare})] — elementele HTML scrise în șabloanele și șirurile de sub `n`; o interpolare `${…}` e „\x00”."""
    p = _Elemente()
    for s in noduri(n, "TemplateLiteral"):
        p.feed("\x00".join(q["value"]["cooked"] or "" for q in s["quasis"]))
        p.feed("\n")
    for s in noduri(n, "Literal"):
        if isinstance(s.get("value"), str):
            p.feed(s["value"])
            p.feed("\n")
    p.close()
    return p.gasite


def conditii_cu_element(n, cod):
    """{id-ul elementului din ramura „da” a unei condiții `c ? <html> : …`: mulțimea termenilor lui `c` legați cu &&}."""
    out = {}
    for c in noduri(n, "ConditionalExpression"):
        termeni, stiva = set(), [c["test"]]
        while stiva:
            x = stiva.pop()
            if x.get("type") == "LogicalExpression" and x["operator"] == "&&":
                stiva += [x["left"], x["right"]]
            else:
                termeni.add(cod(x))
        for _tag, at in elemente_html(c["consequent"]):
            if at.get("id"):
                out.setdefault(at["id"], set()).update(termeni)
    return out
