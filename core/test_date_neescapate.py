# -*- coding: utf-8 -*-
"""C37 (Lotul 5, 15.10.2026): datele scrise de om (nume, prenume, email, denumiri, mesaje) puse în HTML trec prin `esc()` — DS cap.10.
Instrumentul e `scripts/scan_date_neescapate.py`, același pe care îl rulează verificatorul (DATE_UTILIZATOR_NEESCAPATE): o singură
implementare, două porți. Aici: frontendul întreg are zero, iar instrumentul vede ce trebuie (exemple scrise de mână, în ambele
direcții) — un zero e o veste bună numai dacă instrumentul chiar vede ceva.
Plus [269] salutul: niciun ecran nu mai ia „ultimul cuvânt” din nume (`.split(" ").slice(-1)`); funcția comună e `numeDeSalut`
(salut.js) / `nume_de_salut` (core/common.py), iar comportamentul pe pagina principală îl probează e2e `test_def_269_*`.
MUTAȚII (raportul lotului): `esc(` scos din salutul din salut.js -> pică primul test; `.split(" ").slice(-1)[0]` pus la loc în
navigator.js -> pică testul salutului."""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_date_neescapate as S  # noqa: E402
from core.common import nume_de_salut  # noqa: E402


def test_frontendul_nu_pune_date_scrise_de_om_in_html_fara_esc():
    rele = S.toate(RAD)
    assert rele == [], "date scrise de om puse în HTML fără esc() (DS cap.10):\n" + "\n".join("  %s:%d  %s" % r for r in rele)
    assert len(S.fisiere(RAD)) > 40, "anti-vacuu: frontendul are doar %d fișiere" % len(S.fisiere(RAD))


def test_instrumentul_vede_ce_trebuie():
    rele = [
        'x.innerHTML = `<h1>Salut, ${prenume}</h1>`;',
        '<div class="sol-mesaj">${s.mesaj}</div>',
        '<b>Adresa:</b> ${p.email || "-"}</div>',
        '<span class="subbara-firma">${firmaInLucru}</span>',
        '<div>${c.creat_de_nume || "—"}</div>',
        'el.insertAdjacentHTML("afterend", \'<p class="msg-eroare">\' + (e.mesaj || "Eroare.") + \'</p>\');',
        '_banner("Adresa e <b>" + (d.email || "nouă") + "</b>.");',
        '<input value="${p.email}">',
    ]
    bune = [
        'x.innerHTML = `<h1>Salut, ${esc(prenume)}</h1>`;',
        '<div class="sol-mesaj">${esc(s.mesaj)}</div>',
        '<option value="${esc(p.cui)}">${esc(p.nume)}</option>',
        '<svg>${ICOANE[nume] || ""}</svg>',
        '<label for="m${i}-${sc.nume}">${esc(sc.eticheta)}</label>',
        '<div>${firma.tenant_id}</div>',
        '<p>${e.mesaj ? "A" : "B"}</p>',
        '<p>${opt.tva === false ? "(firma nu e plătitoare de TVA)" : ""}</p>',
        'arataMesaj(zm, "Nu s-a putut citi" + (e && e.mesaj ? " (" + e.mesaj + ")" : ""), "eroare");',
        'const _vn = (x) => esc(String(x));\nconst h = `<td>${_vn(l.denumire)}</td>`;',
        '// <b>${prenume}</b> într-un comentariu',
    ]
    for r in rele:
        assert S.cauta(r), "instrumentul NU vede: %r" % r
    for b in bune:
        assert not S.cauta(b), "fals pozitiv: %r -> %s" % (b, S.cauta(b))


def test_verificatorul_ruleaza_instrumentul():
    """Pe arborele verificatorului (AST): importă instrumentul și îl cheamă; ce găsește intră în `rap[...]`, deci în TOTAL."""
    import ast
    arb = ast.parse(open(os.path.join(RAD, "verificator_conformitate.py"), encoding="utf-8").read())
    importat = {a.asname for n in ast.walk(arb) if isinstance(n, ast.Import) for a in n.names if a.name == "scan_date_neescapate"}
    assert importat == {"_sdn"}
    chemat = [n for n in ast.walk(arb) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "toate"
              and isinstance(n.func.value, ast.Name) and n.func.value.id == "_sdn"]
    assert len(chemat) == 1
    chei = {n.slice.value for n in ast.walk(arb) if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name)
            and n.value.id == "rap" and isinstance(n.slice, ast.Constant)}
    assert {"date_utilizator_neescapate"} <= chei


# ── [269] salutul ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_TAIE_NUMELE = re.compile(r"""nume\b[^;\n]*\.split\(\s*["'] ["']\s*\)\s*\.slice\(\s*-1\s*\)""")


def test_niciun_salut_nu_ia_ultimul_cuvant_din_nume():
    taie = []
    for d in (os.path.join(RAD, "static", "js"), os.path.join(RAD, "static", "js", "ecrane")):
        for f in sorted(os.listdir(d)):
            if f.endswith(".js"):
                for ln, rand in enumerate(open(os.path.join(d, f), encoding="utf-8"), 1):
                    if _TAIE_NUMELE.search(rand):
                        taie.append("%s:%d" % (f, ln))
    assert taie == [], "salut din ultimul cuvânt al numelui (269): %s" % taie
    assert _TAIE_NUMELE.search('const p = u.prenume || (u.nume || "").split(" ").slice(-1)[0] || "";')   # anti-vacuu


def test_nume_de_salut():
    assert nume_de_salut(None, "Test 253") == "Test 253"         # numele întreg, nu „253”
    assert nume_de_salut("  ", " Ionescu Maria ") == "Ionescu Maria"
    assert nume_de_salut("Maria", "Ionescu") == "Maria"         # prenumele scris separat
    assert nume_de_salut(None, None) == ""
