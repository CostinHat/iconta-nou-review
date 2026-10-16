# -*- coding: utf-8 -*-
"""Date scrise de om (nume, prenume, email, denumiri, mesaje) puse în HTML fără `esc()` — DS cap.10: „Orice dată user/import-controlled
afișată în innerHTML se trece prin `esc()`.” Citește depozitul, nu-l atinge. Folosit de `verificator_conformitate.py`
(DATE_UTILIZATOR_NEESCAPATE) și de `core/test_date_neescapate.py`.

DE UNDE VINE (C37, Lotul 5, 15.10.2026). Regula din DS exista fără gard; singurul gard pe `esc` era MESAJ_SERVER_NEESCAPAT, care vede
numai mesajele de eroare de la server (`e.mesaj`, `err.message`, `r.detail`) și numai într-un șablon `${…}` — nu un nume, un email sau
un mesaj scris de client, și nici un mesaj lipit cu `+`. Așa au trecut: salutul (`salut.js`, `admin.js`: prenumele), bara de sus
(`navigator.js`: numele firmei și al omului, firma în lucru), portalul (numele firmei, emailurile), mesajele dintre client și cabinet
(`firme.js`, `portal.js`: textul scris de client ajungea ca HTML în ecranul cabinetului), termenele (numele firmelor), validarea (firma
și autorul), confirmarea adresei noi (`app.js`) și șapte mesaje de eroare lipite cu `+`.

CE PRINDE. Pe un rând cu marcaj (`<` înaintea locului, sau `innerHTML` / `insertAdjacentHTML` pe rând):
  - `${expr}` în care `expr` AFIȘEAZĂ un câmp de identitate — `[obiect.]prenume|nume|email|denumire|mesaj|firma…` (și `x.ceva_nume`,
    `x.ceva_email`, `x.ceva_denumire`) — fără `esc(` înaintea lui;
  - aceeași valoare lipită cu `+` (`'<b>' + x.email + '</b>'`, `'<p>' + (e.mesaj || "…") + '</p>'`).
NU numără: câmpul folosit numai ca test (`x.email ? … : …`, `===`, `&&`, `.length`), o cheie (`ICOANE[nume]`, `x.nume[0]`), un apel
(`x.nume(`), un membru mai departe (`firma.tenant_id`), un identificator de câmp într-un `id=` / `for=` / `name=` (`id="op-${c.nume}"`:
cheia câmpului din configurație, nu text scris de om).
LIMITE, declarate: vede un rând odată — o valoare singură pe rândul ei, în mijlocul unui șablon început mai sus, nu se vede; o variabilă
cu alt nume (`const titlu = u.nume`, apoi `${titlu}`) nu se vede; un text pus întâi într-o variabilă (`mesajSucces = "… " + email`) și
apoi în HTML nu se vede. Plasa pentru ele rămâne regula din DS și `esc` la sursa valorii.
"""
from __future__ import annotations

import os
import re
import sys

_ID = r"(?:[\w$]+\.)*(?:prenume|nume|email|denumire|mesaj|firma|firmaInLucru)(?:_\w+)?|(?:[\w$]+\.)+\w+_(?:nume|email|denumire)"
#: după valoare: nu e o cheie, un apel, un membru mai departe sau un test
_NU_AFISARE = r"(?![\w$.(\[\]])(?!\s*(?:\?(?![?.])|===?|!==?|&&|>=?|<=?))"
_IN_SABLON = re.compile(r"(?:^|(?<=[^\w.$]))(" + _ID + r")" + _NU_AFISARE)
_LIPIT = re.compile(r"\+\s*\(?\s*(" + _ID + r")" + _NU_AFISARE)
_INTERPOLARE = re.compile(r"\$\{([^{}]*)\}")
_ATRIBUT_CHEIE = re.compile(r"""\b(?:id|for|name)\s*=\s*["'](?:[\w-]|\$\{[^{}]*\})*$""")
#: un șir literal (textul lui nu e o valoare: „(firma nu e plătitoare…)”)
_LITERAL = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')
#: un tag scris în literal, pe rând (`'<p class=…>' + …`, `… + '</b>'`): rândul face HTML
_TAG_LITERAL = re.compile(r"""["'`]\s*</?[a-zA-Z]|>\s*["'`]""")
#: o funcție locală care escapează (`const _vn = (x) => … esc(String(x))`): trecerea prin ea e trecere prin `esc`
_ENVELOPA = re.compile(r"(?:const|let|var)\s+([\w$]+)\s*=\s*(?:\([^)]*\)|[\w$]+)\s*=>[^\n]*\besc\(|function\s+([\w$]+)\s*\([^)]*\)\s*\{[^\n]*\besc\(")


def _e_html(rand, poz):
    return "<" in rand[:poz] or "innerHTML" in rand or "insertAdjacentHTML" in rand


def cauta(text):
    """PURĂ. [(linie, fragment)] pentru fiecare valoare de identitate pusă în HTML fără `esc()`."""
    out = []
    escapeaza = ["esc(", "encodeURIComponent("] + ["%s(" % (a or b) for a, b in _ENVELOPA.findall(text)]
    for ln, rand in enumerate(text.split("\n"), 1):
        if rand.lstrip().startswith("//"):
            continue
        for m in _INTERPOLARE.finditer(rand):
            if not _e_html(rand, m.start()) or _ATRIBUT_CHEIE.search(rand[:m.start()]):
                continue
            expr = _LITERAL.sub('""', m.group(1))
            for v in _IN_SABLON.finditer(expr):
                inainte = expr[:v.start()]
                if any(e in inainte for e in escapeaza):
                    continue
                out.append((ln, m.group(0)[:80]))
                break
        if not _TAG_LITERAL.search(rand):
            continue
        for v in _LIPIT.finditer(rand):
            if re.search(r"\besc\(\s*\(?\s*$", rand[:v.start(1)]):
                continue
            out.append((ln, rand[v.start():v.end() + 20].strip()[:80]))
    return out


def fisiere(rad):
    """Frontendul întreg, ca verificatorul: `static/js/*.js` și `static/js/ecrane/*.js`."""
    out = {}
    for d in (os.path.join(rad, "static", "js", "ecrane"), os.path.join(rad, "static", "js")):
        for f in sorted(os.listdir(d)):
            if f.endswith(".js") and ".bak" not in f and f not in out:
                out[f] = os.path.join(d, f)
    return out


def toate(rad):
    rez = []
    for nume, cale in fisiere(rad).items():
        for ln, frag in cauta(open(cale, encoding="utf-8").read()):
            rez.append((nume, ln, frag))
    return rez


if __name__ == "__main__":
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    r = toate(rad)
    for x in r:
        print("%s:%d  %s" % x)
    print("TOTAL", len(r))
    sys.exit(1 if r else 0)
