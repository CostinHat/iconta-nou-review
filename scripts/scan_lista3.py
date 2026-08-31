# -*- coding: utf-8 -*-
"""scripts/scan_lista3.py — lista 3, DERIVATA din registru, nu numarata cu mana.

Cerut de Costin, 31.08.2026: *«Cifra "opt artefacte" vine din premisa care a cazut: e un numar
derivat reafirmat in proza, care nu se mai regenereaza din nimic — aceeasi clasa ca antetul T02. Se
aplica regula ei propriei liste: ori se genereaza, ori se sterge.»*

Aici raspunsul e SE GENEREAZA. Titlul listei e util — spune dintr-o privire cat a mai ramas — deci
nu se sterge; se produce din coloana `stare` a tabelelor, care e singurul loc unde starea fiecarui
artefact se scrie o data.

CE CITESTE, exact: tabelele din `CONFORMITATE.md` care au capul
`| artefact | A producator | B ruta | C ecran | stare |`. Coloana a cincea da starea; primul cuvant
al ei (dupa curatarea ingrosarii) e verdictul.

MODURILE DE ESEC, scrise inainte de prima rulare:
  1. **Vede doar tabelele cu cele CINCI coloane.** Tabelul vechi de cauze are doua coloane si NU se
     numara — el pastreaza cauza masurata la descoperire, nu starea de azi. Daca cineva scrie un
     artefact NOU doar acolo, scanul nu-l vede. Deci cifra e plafon INFERIOR pe artefacte.
  2. **Nu deosebeste «DESCHIS» de «DESCHIS pe o firma».** `R3` e reparat ca derivare si deschis ca
     proba — starea lui e o propozitie, nu o eticheta. Se numara dupa primul cuvant, iar restul
     propozitiei ramane de citit de om.
  3. **Nu verifica daca starea scrisa e ADEVARATA.** Un rand care zice REPARAT fara sa fie n-are cum
     sa fie prins de aici; pentru asta sunt gardile fiecarui artefact.
"""
import io
import os
import re

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = os.path.join(RAD, "CONFORMITATE.md")

CAP = "| artefact | A producător | B rută | C ecran | stare |"

#: Nomenclator INCHIS al verdictelor. Un al cincilea cuvant in coloana `stare` pica, in loc sa fie
#: numarat tacut ca «altceva» — o stare noua e o decizie, nu o scapare de tipar.
VERDICTE = ("DESCHIS", "REPARAT", "FALS")


def _curata(s):
    return re.sub(r"[*`_]", "", s).strip()


def randuri(text=None):
    """[{artefact, stare, verdict}] — din toate tabelele cu cele cinci coloane."""
    t = text if text is not None else io.open(CONF, encoding="utf-8").read()
    out = []
    for m in re.finditer(re.escape(CAP), t):
        p = m.start()
        capat = t.index("\n\n", p)
        for ln in t[p:capat].split("\n")[2:]:
            col = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(col) != 5:
                continue
            stare = _curata(col[4])
            cuv = re.split(r"[\s.,·]", stare)[0].upper() if stare else ""
            out.append({"artefact": _curata(col[0]), "stare": stare, "verdict": cuv})
    return out


def capete_de_tabel(text=None):
    """{tuplu de coloane} — capetele TUTUROR tabelelor din registru.

    Exista ca aserttiunile despre tabele sa se poata face pe o MULTIME calculata, nu cautand un sir
    in document: `"| artefact | cauza |" in doc` intreaba «apare undeva», iar un cap citat intr-un
    paragraf ar trece la fel de bine ca unul real (clichet 50 / METODA §23).
    """
    t = text if text is not None else io.open(CONF, encoding="utf-8").read()
    out = set()
    linii = t.split(chr(10))
    for i, ln in enumerate(linii[:-1]):
        s, urm = ln.strip(), linii[i + 1].strip()
        if not (s.startswith("|") and urm.startswith("|")):
            continue
        if not set(urm) <= set("|-: "):      # a doua linie e separatorul de tabel
            continue
        col = tuple(_curata(c) for c in s.strip("|").split("|"))
        if len(col) >= 2:
            out.add(col)
    return out


def numara(text=None):
    """{verdict: n} + `total`. Verdictele sunt un nomenclator INCHIS."""
    rs = randuri(text)
    d = {v: 0 for v in VERDICTE}
    necunoscute = []
    for r in rs:
        if r["verdict"] in d:
            d[r["verdict"]] += 1
        else:
            necunoscute.append((r["artefact"], r["verdict"]))
    d["total"] = len(rs)
    d["necunoscute"] = necunoscute
    return d


def titlu(text=None):
    """Titlul listei 3, GENERAT. Un singur loc care spune cat a mai ramas."""
    d = numara(text)
    if d["necunoscute"]:
        raise ValueError("verdicte în afara nomenclatorului: %r" % d["necunoscute"])
    if d["DESCHIS"] == 0:
        cat = "**niciun artefact deschis**"
    elif d["DESCHIS"] == 1:
        cat = "**un artefact deschis**"
    else:
        cat = "**%d artefacte deschise**" % d["DESCHIS"]
    return ("#### Lista 3 — nu ies, DIN VINA APLICAȚIEI — %s din %d urmărite "
            "*(cifra e generată din coloana `stare`, cu `scripts/scan_lista3.py`)*"
            % (cat, d["total"]))


def _main():
    d = numara()
    print(titlu())
    print()
    for r in randuri():
        print("  %-9s %s" % (r["verdict"], r["artefact"][:66]))
    print("\nDESCHIS %d · REPARAT %d · FALS %d · total %d"
          % (d["DESCHIS"], d["REPARAT"], d["FALS"], d["total"]))
    if d["necunoscute"]:
        print("VERDICTE NECUNOSCUTE:", d["necunoscute"])
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
