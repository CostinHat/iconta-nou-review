# -*- coding: utf-8 -*-
"""Gardul temeiurilor (PASUL 4): impune forma canonica de citare a REGULILOR de validator din
CLAUDE.md §3.1, pe ce e MARCAT ca regula (optiunea A - nu ghiceste din forma tokenului; codurile
bare = randuri de declaratie, NU se cer).

ACOPERA: `regula <cod>` trebuie sa fie `DUK regula <cod>` sau `eFactura regula <cod>` (cod = litera
+ cifra: A91b, R28, F10_68, BR-RO-100). Distinctiv, nu apare in proza -> robust.

NU acopera (raportat, nu fortat):
- forma `ANAF structura <formular>`: NU se poate pazi mecanic. Regresia ar fi revenirea la
  'structura oficiala D300', dar aceeasi fraza apare si in PROZA (ex. un reason de datorie:
  'de verificat in structura oficiala D300') - textual identic cu o citare. Un gard ar da
  fals-pozitiv pe descrieri. Vezi §3.1; canonizarea e facuta (PASUL 3), regresia se prinde la review.
- forma NORMATIVA (`<TIP> <nr>/<an>`): intra dupa normalizarea celor 113 citari (PASUL 3 rest).

Escape hatch: o linie care contine `# TEMEI LIBER: <motiv>` e exceptata."""
import re
import pathlib

_RAD = pathlib.Path(__file__).resolve().parent.parent
# cod real de regula: litera(e) + cifra (A91b, R28, R11b, F10_68) sau EN16931 (BR-RO-100).
_COD = r"(?:[A-Z][A-Za-z0-9]*\d[A-Za-z0-9_]*|BR-[A-Z]{1,3}-\d+)"


def _incalcari_temei(text):
    """[(linie, motiv, continut)] - citari de `regula <cod>` in forma NEcanonica (fara prefixul
    validatorului). Codurile bare fara 'regula' = randuri de declaratie, NU se raporteaza."""
    viol = []
    for i, line in enumerate(text.splitlines(), 1):
        if "TEMEI LIBER" in line:            # escape hatch adnotat
            continue
        for m in re.finditer(r"\bregul[aăi]\s+(%s)\b" % _COD, line, re.IGNORECASE):
            if not re.search(r"(?:DUK|eFactura)\s+$", line[:m.start()]):
                viol.append((i, "regula '%s' fara prefix 'DUK regula'/'eFactura regula'" % m.group(1),
                             line.strip()))
    return viol


def test_temeiuri_reguli_validator_canonice():
    """Nicio citare `regula <cod>` fara prefix DUK/eFactura in core/*.py."""
    rap = []
    for f in sorted(_RAD.glob("core/*.py")):
        if f.name == "test_temeiuri.py":
            continue  # contine mostre cu incalcari intentionate (testul de mutatie)
        for (ln, motiv, cont) in _incalcari_temei(f.read_text(encoding="utf-8", errors="replace")):
            rap.append("%s:%d %s | %s" % (f.name, ln, motiv, cont[:80]))
    assert not rap, "citari de regula necanonice (vezi CLAUDE.md §3.1):\n" + "\n".join(rap)


def test_gard_temeiuri_prinde_si_tace():
    """Mutatie pe gard, ambele sensuri: prinde forma necanonica, tace pe cea canonica + escape hatch."""
    # PRINDE (necanonic):
    assert _incalcari_temei("    # dovedit prin regula A91b pe validator"), "nu prinde 'regula A91b' bare"
    assert _incalcari_temei("    # regula BR-RO-100 (validator ANAF)"), "nu prinde 'regula BR-RO-100' bare"
    # TACE (canonic sau irelevant):
    assert not _incalcari_temei("    # DUK regula A91b pe validator"), "fals-pozitiv pe 'DUK regula'"
    assert not _incalcari_temei("    # eFactura regula BR-RO-100 (RO-CIUS)"), "fals-pozitiv pe 'eFactura regula'"
    assert not _incalcari_temei("    # regula de aur: verifica la sursa"), "fals-pozitiv pe 'regula' + cuvant fara cifra"
    assert not _incalcari_temei("    # R28 = randul TOTAL TAXA DEDUSA (D300)"), "fals-pozitiv pe cod bare (rand)"
    assert not _incalcari_temei("    # de verificat in structura oficiala D300"), "fals-pozitiv pe proza (structura)"
    # ESCAPE HATCH:
    assert not _incalcari_temei("    # regula A91b  # TEMEI LIBER: mostra didactica"), "escape hatch ignorat"
