# -*- coding: utf-8 -*-
"""Inventarul gărzilor, DERIVAT din cod — blocul generat din `GARZI.md`.

DE CE EXISTĂ. `GARZI.md` e „registrul gardurilor", scris ca narațiune, o intrare per decizie. Între
**22.08 și 28.08.2026** n-a primit nicio intrare, deși în fereastra aia au intrat **zeci** de gărzi.
Un registru cu șase zile în urmă nu se citește ca incomplet: se citește ca **complet**. Costin,
28.08: *„rămâne viu, nu se îngheață."*

Partea narativă rămâne scrisă de om — de ce s-a construit garda, ce instanță a produs-o, ce nu face.
Partea care se poate **deriva** nu mai are voie să îmbătrânească: ce gărzi există, când au intrat, și
ce spune fiecare despre sine. Asta o generează instrumentul ăsta, iar `core/test_garzi_inventar.py`
compară blocul din document caracter cu caracter cu ce iese de aici — același tipar ca Partea XII din
`TRASEE.md`.

CE CITEȘTE: fiecare `core/test_*.py`, `core/scan_*.py` și `scripts/scan_*.py`, cu **prima linie a
docstringului de modul** (afirmația gărzii despre ea însăși) și data primului commit care l-a adus.

CE NU FACE, declarat: **nu judecă dacă garda e bună**, nu numără aserțiunile și nu spune dacă păzește
ceva viu. Un fișier fără docstring apare cu `—`, ca lipsa să se vadă. Iar data e a **commitului**, nu
a scrierii: un fișier mutat între directoare arată ca nou.

  ./venv/bin/python scripts/scan_garzi_inventar.py --md
"""
import ast
import io
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARCA_START = "<!-- INVENTAR-GARZI:START (generat de scripts/scan_garzi_inventar.py --md) -->"
MARCA_STOP = "<!-- INVENTAR-GARZI:STOP -->"

DIRECTOARE = (("core", "test_"), ("core", "scan_"), ("scripts", "scan_"))


def fisiere():
    out = []
    for director, prefix in DIRECTOARE:
        baza = os.path.join(RAD, director)
        for f in sorted(os.listdir(baza)):
            if f.startswith(prefix) and f.endswith(".py"):
                out.append("%s/%s" % (director, f))
    return sorted(set(out))


def _prima_linie(rel):
    """Prima frază a docstringului de modul — afirmația gărzii despre ea însăși."""
    try:
        arb = ast.parse(io.open(os.path.join(RAD, rel), encoding="utf-8").read())
    except SyntaxError:      # pragma: no cover
        return "—"
    d = ast.get_docstring(arb)
    if not d:
        return "—"
    linie = " ".join(d.strip().split("\n")[0].split())
    return linie or "—"


def _data_intrarii():
    """{cale: YYYY-MM-DD} — data primului commit care a adus fișierul. O singură trecere prin git."""
    r = subprocess.run(["git", "-C", RAD, "log", "--reverse", "--diff-filter=A",
                        "--name-only", "--format=@%ad", "--date=short", "--",
                        "core", "scripts"], capture_output=True, text=True)
    out, data = {}, None
    for linie in (r.stdout or "").splitlines():
        if linie.startswith("@"):
            data = linie[1:].strip()
        elif linie.strip() and linie.strip() not in out:
            out.setdefault(linie.strip(), data)
    return out


def inventar():
    """[(cale, data, afirmatia)] — sortat pe dată, apoi pe cale."""
    datele = _data_intrarii()
    out = [(f, datele.get(f) or "—", _prima_linie(f)) for f in fisiere()]
    return sorted(out, key=lambda x: (x[1], x[0]))


def redare_md():
    """Blocul generat. **Fără date**, și ăsta e un lucru învățat pe loc: prima formă grupa gărzile
    pe ziua primului commit, iar fișierele din commitul CURENT n-au încă una. Blocul ar fi intrat cu
    `—` și s-ar fi schimbat singur imediat după commit, făcând garda doc↔cod roșie la următoarea
    rulare — un registru care se strică prin propria actualizare. Datele trăiesc în intrările
    narative, unde sunt scrise o dată și verificate contra `git log`."""
    inv = sorted(inventar(), key=lambda x: x[0])
    pe_dir = {}
    for cale, _data, afirm in inv:
        pe_dir.setdefault(cale.split("/")[0], []).append((cale, afirm))
    linii = [MARCA_START, ""]
    linii.append("**%d gărzi și instrumente.** Afirmația e prima frază a docstringului fiecăruia — "
                 "ce spune garda despre ea însăși, nu ce cred eu despre ea. Un `—` înseamnă că "
                 "fișierul n-are docstring de modul, iar lipsa se vede în loc să se piardă."
                 % len(inv))
    linii.append("")
    for director in sorted(pe_dir):
        linii.append("### `%s/` — %d" % (director, len(pe_dir[director])))
        linii.append("")
        for cale, afirm in pe_dir[director]:
            if len(afirm) > 150:
                afirm = afirm[:147] + "…"
            linii.append("- `%s` — %s" % (cale, afirm))
        linii.append("")
    linii.append(MARCA_STOP)
    return chr(10).join(linii)


def pe_zile(de_la=None):
    """[(data, [(cale, afirmatie)])] — pentru intrarile narative. NU intra in blocul generat."""
    pe_zi = {}
    for cale, data, afirm in inventar():
        if de_la and (data == "—" or data < de_la):
            continue
        pe_zi.setdefault(data, []).append((cale, afirm))
    return sorted(pe_zi.items())


def main():
    if "--md" in sys.argv:
        print(redare_md())
        return 0
    if "--zile" in sys.argv:
        de_la = sys.argv[sys.argv.index("--zile") + 1]
        for data, lista in pe_zile(de_la):
            print("### %s — %d" % (data, len(lista)))
            for cale, afirm in lista:
                print("- `%s` — %s" % (cale, afirm))
            print()
        return 0
    inv = inventar()
    print("gărzi și instrumente: %d" % len(inv))
    fara = [c for c, _d, a in inv if a == "—"]
    print("fără docstring de modul: %d %s" % (len(fara), fara[:6]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
