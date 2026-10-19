# -*- coding: utf-8 -*-
"""scripts/denumiri_randuri.py — generează `core/denumiri_randuri.py`: denumirea OFICIALĂ a fiecărui rând din formularele D300 și D101,
citită din textul ordinelor ANAF din `anaf_surse/` (nu scrisă de mână).

[deficiența 379, comanda Costin 8.2, 18.10.2026] „La D300 rândurile apar doar ca număr («rândul 9, coloana Valoare»). Fiecare rând se
afișează cu denumirea lui oficială din formular, la toate declarațiile.” Surse:
- D300: OPANAF 174/2026, anexa 1 (`anaf_surse/opanaf_174_2026_d300.txt`), tabelul „Denumire indicatori”, rd.1–45;
- D101: OPANAF 206/2025 (`anaf_surse/opanaf_206_2025_d101.txt`), secțiunea B „Date privind impozitul pe profit”, rd.1–53.

Extragerea din PDF pierde exponenții: „art. 2781”, „rd. 381”. Corecturile sunt o listă ÎNCHISĂ, fiecare verificată în Codul fiscal local
(`anaf_surse/cod_fiscal_227_2015_consolidat.html`): art.278^1 există (vânzări la distanță) și art.2781 nu; art.22^1 e scutirea de impozit pe
profit a contribuabililor din cercetare-inovare, iar art.221 e despre nerezidenți; art.18^1 e impozitul minim, iar art.181 e abrogat;
art.40^2 e limitarea deductibilității dobânzii, iar art.402 e documentul administrativ electronic (accize). Rândurile
D101 cu exponent (38^1, 39^1, 40^1, 43^1) sunt atributele P38a, P39a, P40a, P43a (`anaf_surse/d101_struct_anaf.txt`: P38a = P35+P36+P37-P38).

Uz: python scripts/denumiri_randuri.py            -> rescrie core/denumiri_randuri.py
    python scripts/denumiri_randuri.py --verifica -> 0 identic / 1 diferă (garda: core/test_denumiri_randuri.py)
"""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURSA_D300 = os.path.join(RAD, "anaf_surse", "opanaf_174_2026_d300.txt")
SURSA_D101 = os.path.join(RAD, "anaf_surse", "opanaf_206_2025_d101.txt")
IESIRE = os.path.join(RAD, "core", "denumiri_randuri.py")

#: exponenții pierduți la extragere, verificați în Codul fiscal local (vezi antetul)
EXPONENTI = (("art. 2781", "art. 278^1"), ("art. 221 ", "art. 22^1 "), ("art. 181 ", "art. 18^1 "),
             ("art. 402 ", "art. 40^2 "), ("rd. 381", "rd. 38^1"), ("rd. 391", "rd. 39^1"), ("rd. 431", "rd. 43^1"))
#: rândurile D101 tipărite cu exponent -> eticheta pe care o dă `d101_randuri.rand_d101` atributului lor
RAND_EXPONENT_D101 = {"381": "38^1", "391": "39^1", "401": "40^1", "431": "43^1"}

_RAND = re.compile(r"^\s{0,2}(\d{1,3}(?:\.\d){0,2})\s+(\S.*?)\s*$")


def _curata(t):
    t = " ".join(t.split())
    for a, b in EXPONENTI:
        t = t.replace(a, b)
    return t.rstrip(" ,")


def _randuri(linii, ultimul):
    out, cur = {}, None
    for ln in linii:
        m = _RAND.match(ln)
        if m and not re.match(r"^\d+(?:\.\d)*,", ln.strip()):
            nr, text = m.group(1), m.group(2)
            text = re.sub(r"\s+%s$" % re.escape(nr), "", text)        # D101 repetă numărul rândului în coloana din dreapta
            cur = nr
            out.setdefault(nr, []).append(text)
            if nr == ultimul:
                ultimul = None
            continue
        if not ln.strip() or not ln[:1].isspace() or "Denumire indicatori" in ln:
            if cur and ultimul is None and not ln.strip():
                break
            cur = None
            continue
        if cur:
            out[cur].append(ln.strip())
    return {k: _curata(" ".join(v)) for k, v in out.items()}


def extrage_d300(text):
    linii = text.splitlines()
    a = next(i for i, ln in enumerate(linii) if ln.startswith("COMERŢ INTRACOMUNITAR"))
    z = next(i for i, ln in enumerate(linii) if "Cod CAEN al activit" in ln)
    return _randuri(linii[a:z], "45")


def extrage_d101(text):
    linii = text.splitlines()
    a = next(i for i, ln in enumerate(linii) if re.match(r"^\s*1\s+Venituri din exploatare", ln))
    z = next(i for i, ln in enumerate(linii) if i > a and "C. Date de identificare a împuternicitului" in ln)
    r = _randuri(linii[a:z], "53")
    return {RAND_EXPONENT_D101.get(k, k): v for k, v in r.items()}


def _cheie(k):
    return [(0, int(x)) if x.isdigit() else (1, x) for x in re.findall(r"\d+|[a-z]", k)]


def randeaza(d300, d101):
    def bloc(nume, d):
        linii = ["%s = {" % nume]
        for k in sorted(d, key=_cheie):
            linii.append("    %r: %r," % (k, d[k]))
        return linii + ["}", ""]
    linii = ['# -*- coding: utf-8 -*-',
             '"""core/denumiri_randuri.py — GENERAT de `scripts/denumiri_randuri.py` din textul formularelor ANAF (nu se editează de mână; garda',
             '`core/test_denumiri_randuri.py` îl compară cu regenerarea). [deficiența 379, comanda Costin 8.2] Denumirea oficială a fiecărui rând,',
             'pe eticheta rândului din formular („9”, „12.1”, „38^1”)."""',
             '',
             '#: D300 — OPANAF 174/2026, anexa 1 (anaf_surse/opanaf_174_2026_d300.txt)']
    linii += bloc("D300", d300)
    linii += ['#: D101 — OPANAF 206/2025, secțiunea B (anaf_surse/opanaf_206_2025_d101.txt)']
    linii += bloc("D101", d101)
    return "\n".join(linii)


def main(argv):
    d300 = extrage_d300(open(SURSA_D300, encoding="utf-8").read())
    d101 = extrage_d101(open(SURSA_D101, encoding="utf-8").read())
    nou = randeaza(d300, d101)
    if "--verifica" in argv:
        vechi = open(IESIRE, encoding="utf-8").read() if os.path.exists(IESIRE) else ""
        print("identic" if vechi == nou else "diferă — regenerează: python scripts/denumiri_randuri.py")
        return 0 if vechi == nou else 1
    open(IESIRE, "w", encoding="utf-8").write(nou)
    print("scris %s: D300 %d rânduri, D101 %d rânduri" % (IESIRE, len(d300), len(d101)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
