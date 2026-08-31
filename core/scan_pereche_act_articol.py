# -*- coding: utf-8 -*-
"""DOCUMENTUL PE CARE ÎL CITEAZĂ UN TEMEI CONȚINE ARTICOLUL PE CARE ÎL NUMEȘTE?

**Instanța care a deschis clasa** (31.08.2026, în timpul măsurării interdicției 55):
`OG 16/2022 art. 97`. Articolul 97 **nu e al ordonanței** — OG 16/2022 spune *„articolul 97
alineatul (7) … se modifică"*, deci art. 97 e al **Codului fiscal**. Temeiul numește actul
**MODIFICATOR** cu articolul actului **MODIFICAT**. Confirmat la sursă și pe `OUG 8/2026`, care
spune *„articolul 282, alineatul (3) se modifică"*.

**De ce contează, concret:** orice verificare de vigoare pe perechea asta întreabă **documentul
greșit**. Iar `COTE.impozit_dividend` are **patru** temeiuri și **niciunul** nu se poate confrunta
cu documentul lui — trei negăsite, unul ciot. Valoarea e corectă; ce nu se poate reface e drumul de
la ea la lege.

**Nu e același lucru cu interdicția 59.** Aceea compară verificarea *pe act* cu cea *pe articol*.
Aici perechea (act, articol) e **inconsistentă în sine**: articolul nu există în actul citat, deci
nici măcar nu se pune problema pe ce nivel verifici.

**Nu e același lucru cu interdicția 53.** Aceea întreabă dacă **citatul** conține valoarea — și
răspunde da pe 34 din 34. Un temei poate avea citatul potrivit și actul greșit: citatul e copiat de
noi, actul e o trimitere. Două întrebări, două răspunsuri, iar al doilea n-avea instrument.

CELE TREI FELURI DE „NU POT SPUNE", deosebite — un singur „nu" le-ar topi într-unul:
  - **NEGASIT**  — actul e adus și are articole, dar nu pe ăsta. *Ăsta e defectul.*
  - **CIOT**     — documentul citat are sub două titluri de articol (extras de PDF, formă parțială).
                   Nu se poate afirma nimic; e o problemă de **corpus**, nu de temei.
  - **FISIER_LIPSA** — `url`-ul temeiului nu duce nicăieri.

MODURILE DE EȘEC ALE INSTRUMENTULUI, scrise înainte de prima rulare:
  1. **Plafon INFERIOR.** Un temei fără `art` nu se poate verifica deloc — se numără separat, nu se
     trece la „bine".
  2. **Nu vede potrivirea GREȘITĂ.** Dacă actul citat conține din întâmplare un articol cu același
     număr, perechea trece — chiar dacă articolul acela e despre altceva. Ar cere o citire.
  3. **Depinde de corpus.** Un `CIOT` nu spune că temeiul e greșit; spune că nu s-a putut întreba.
"""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import articol_in_act as A  # noqa: E402

#: Stările în care perechea NU se poate confirma. Nomenclator ÎNCHIS.
NECONFIRMATE = ("NEGASIT", "CIOT", "FISIER_LIPSA", "FARA_ART")


def _cale(url):
    return url if os.path.isabs(str(url)) else os.path.join(RAD, str(url))


def inventar():
    """[{cale, temei, act, art, url, stare}] — o intrare per temei unic din registrul de cote."""
    from core import scan_citate
    out = []
    for cale, t, _v in scan_citate.inventar():
        art = getattr(t, "art", None)
        url = getattr(t, "url", None)
        rand = {"cale": cale, "temei": str(t), "art": art, "url": url,
                "act": "%s %s/%s" % (getattr(t, "tip", "?"), getattr(t, "nr", "?"),
                                     getattr(t, "an", "?"))}
        if not art:
            rand["stare"] = "FARA_ART"
        elif not url:
            rand["stare"] = "FISIER_LIPSA"
        else:
            rand["stare"] = A.cauta(_cale(url), art)["stare"]
        out.append(rand)
    return out


def neconfirmate(inv=None):
    """Perechile care NU se pot confirma, fără cele fără articol — clasa propriu-zisă plus ciotul."""
    return [x for x in (inv if inv is not None else inventar())
            if x["stare"] in ("NEGASIT", "CIOT", "FISIER_LIPSA")]


def pe_stare(inv=None):
    d = {}
    for x in (inv if inv is not None else inventar()):
        d[x["stare"]] = d.get(x["stare"], 0) + 1
    return d


def _main():
    inv = inventar()
    for x in sorted(inv, key=lambda y: (y["stare"], y["act"], str(y["art"]))):
        print("  %-13s %-26s art.%-8s %-34s  <- %s"
              % (x["stare"], x["act"][:26], str(x["art"])[:8],
                 os.path.basename(str(x["url"]))[:34], x["cale"][:34]))
    print()
    print("PE STARE: %s" % pe_stare(inv))
    ver = [x for x in inv if x["stare"] != "FARA_ART"]
    print("verificabile: %d · confirmate: %d · NECONFIRMATE: %d"
          % (len(ver), sum(1 for x in ver if x["stare"] in ("GASIT", "ABROGAT")),
             len(neconfirmate(inv))))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
