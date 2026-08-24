# -*- coding: utf-8 -*-
"""GARD (R29): o cotă de TVA absentă nu se completează singură, în niciun limbaj și în nicio formă.

  core/test_cota_fara_default_fallback.py

CLASA ARE TREI FORME, iar R29 a supraviețuit fiindcă gardul existent acoperea doar una:

  1. default în SEMNĂTURĂ — `def f(cota=21)`      → `core/test_cota_fara_default.py`, doar `core/*.py`
  2. fallback la CITIRE   — `x or 21`, `x || 21`, `else 21.0`   → aici
  3. literal în INIȚIALIZARE — `{ cota_tva: 21 }`               → aici

R26 a măsurat prin AST pe Python și a declarat clasa golită. Măsurătoarea era corectă **înăuntrul
domeniului ei** și falsă despre aplicație: formele 2 și 3 trăiau în `firme.js` (ecranul de NIR, de
trei ori, una plecând în corpul cererii) ȘI în `core/produse_api.py` (`else 21.0`, pe o cale vie,
`main.py:2513`). Deci nu era „clasa golită în Python, vie în JS" — era clasa golită PE O FORMĂ.

Forma 3 a fost adăugată **după ce RED-proof-ul a arătat că lipsea**: mutația care repunea
`cota_tva: 21` pe linia nouă de NIR lăsa gardul VERDE, fiindcă acolo nu există `or`/`||`/`else`.

CE FACE IMPOSIBIL: ca o cotă lipsă să devină o cotă concretă fără ca omul s-o fi ales.

CE NU PRINDE, declarat:
  · defaultul pe ZERO (`cota or 0`) — altă clasă, legitimă în aritmetică, 18 instanțe reale;
  · `cota` fără sufix la forma 3 — e un nume suprasolicitat: `cota=1` e **flagul micro** cerut de
    validatorul DUK (`d100`, `d114`), iar `cota="21"` apare în XML-uri de exemplu din `amef_import`.
    Măsurat: 6 potriviri, toate legitime. Restrângerea la `cota_tva` le scoate pe toate fără nicio
    listă de tolerat — iar o listă de tolerat din prima zi ar fi fost chiar mirosul pe care îl vânăm;
  · cota adusă prin dicționar (`corp["cota"]`) — apărată de `common.cota_ceruta`, altă poartă.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Forma 2 — fallback la citire. Literalul trebuie să poată FI o cotă: 1..99, zecimale opționale.
# Limita de două cifre a fost adăugată după un fals-pozitiv real: `core/d406.py:1465` are
# `tcod_l = "300101" if (r["ti"] or cota == 0) else "300501"` — cod SAF-T, nu cotă.
FALLBACK = re.compile(
    r"""\b(cota_tva|cota)\b[^\n]{0,80}?(\bor\b|\|\||\belse\b)\s*["']?([1-9]\d?(?:\.\d+)?)["']?(?!\d)""")

# Forma 3 — literal în inițializare. DOAR `cota_tva`: vezi „ce nu prinde" din antet.
INIT = re.compile(r"""\bcota_tva\s*[:=]\s*["']?([1-9]\d?(?:\.\d+)?)["']?(?!\d)""")

ZONE = [("static/js", ".js"), ("static/js/ecrane", ".js"), ("core", ".py"), (".", ".py")]
SARITE = ("test_", "scan_", "conftest")


def _fisiere():
    vazut = []
    for zona, ext in ZONE:
        d = os.path.join(RAD, zona)
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            if not f.endswith(ext) or f.startswith(SARITE):
                continue
            cale = os.path.join(d, f)
            if os.path.isfile(cale) and cale not in vazut:
                vazut.append(cale)
    return vazut


def _hituri():
    out = []
    for cale in _fisiere():
        try:
            t = io.open(cale, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for i, ln in enumerate(t.split("\n"), 1):
            s = ln.strip()
            if s.startswith(("//", "#", "*")):
                continue
            for rx, forma in ((FALLBACK, "fallback"), (INIT, "initializare")):
                m = rx.search(ln)
                if m:
                    out.append((os.path.relpath(cale, RAD), i, forma, m.groups()[-1], s[:110]))
                    break
    return out


def test_ANTIVACUU_domeniul_chiar_exista():
    """O gardă care scanează zero fișiere raportează verde despre nimic (interdicția 19)."""
    fis = _fisiere()
    assert len(fis) > 40, "domeniu suspect de mic: %d fisiere" % len(fis)
    assert any(f.endswith("firme.js") for f in fis), "nu vad static/js/ecrane/firme.js"
    assert any(f.endswith("produse_api.py") for f in fis), "nu vad core/produse_api.py"


def test_nicio_cota_absenta_nu_se_completeaza_singura():
    h = _hituri()
    assert not h, (
        "cota de TVA completata tacit, in %d loc(uri):\n%s\n\n"
        "O cota lipsa trebuie sa plece LIPSA - serverul stie s-o refuze (main.py:798). "
        "Daca ecranul sau API-ul o completeaza, refuzul nu se poate declansa niciodata."
        % (len(h), "\n".join("  %s:%d [%s] -> %s | %s" % x for x in h)))


def test_CALIBRARE_pozitiva_toate_TREI_formele_se_prind():
    """Cazuri CONSTRUITE: exact formele care au existat in R29, plus cea gasita de RED-proof."""
    assert FALLBACK.search('cota_tva: l.cota_tva || 21,'), "forma 2 (||) nu se prinde"
    assert FALLBACK.search('d["cota_tva"] = float(x) if x is not None else 21.0'), "forma 2 (else)"
    assert FALLBACK.search('cota = corp.get("cota") or 19'), "forma 2 (or)"
    assert INIT.search('const l = { denumire: "", cota_tva: 21 };'), "forma 3 (initializare)"
    assert INIT.search('cota_tva = 11'), "forma 3 (atribuire)"


def test_CALIBRARE_negativa_ce_NU_trebuie_prins():
    """Trei clase pe care gardul nu are voie sa le gaseasca, toate cu instanta reala in cod.

    (1) defaultul pe ZERO — „nimic de adaugat", nu o cota fabricata;
    (2) un cod lung dintr-o linie care doar POMENESTE cota (d406.py:1465);
    (3) `cota` fara sufix — flagul micro cerut de validator (d100/d114) si XML de exemplu (amef)."""
    for linie in ('const cota = Number(l.cota_tva) || 0;',
                  'cota = int(f.get("cota") or 0)',
                  'tva += val * ((l.cota_tva || 0) / 100);',
                  'tcod_l = "300101" if (r["ti"] or cota == 0) else "300501"',
                  'cota: str = ""          # doar pt. cod_oblig 121 (micro): validator cere cota="1"',
                  '<coteZ cota="21" valOp="2100.00" tva="364.46"/>'):
        assert not FALLBACK.search(linie) and not INIT.search(linie), "prinde gresit: %s" % linie
