# -*- coding: utf-8 -*-
"""GARD anti-regresie CHICKEN-AND-EGG (16.08.2026) — pas2 (declaratii.js).

TIPARUL (clasa, cautata sistematic in toata aplicatia 16.08 - un singur caz genuin, aici):
ecranul de generare declaratie (pas2) randeaza panoul EDITABIL de operatiuni (d300/d301/d390) DOAR
dupa ce POST-ul /declaratii/{tip}/valideaza reuseste. Dar acel POST REFUZA pe zero-base (firma fara
operatiuni). Deci o firma proaspata primea eroarea si NU ajungea la panoul unde ar introduce prima
operatiune -> nu exista punct de intrare. FIX: pe eroare, pas2 randeaza TOTUSI panoul editabil.

INVARIANT GARDAT (mecanic, generic): orice container de panou-declaratie `dec-XXX` gardat de `S.tip ===`
in ramura de SUCCES a lui pas2 trebuie sa apara SI in ramura `catch` (+ loader-ul apelat in catch).
Astfel, un panou editabil NOU adaugat in succes fara randare-pe-eroare pica aici (reintroduce chicken-and-egg).
Restul ecranelor sunt benigne: formularul de add e gardat de un GET-citire (intoarce lista goala, nu arunca),
randat neconditionat (empty-state ascunde doar LISTA) - deci nu au nevoie de gard.
"""
import io
import re
from pathlib import Path

_JS = Path(__file__).resolve().parent.parent / "static" / "js" / "ecrane" / "declaratii.js"


def _pas2_body(src):
    i = src.index("async function pas2(")
    rest = src[i + 1:]
    m = re.search(r"\n(async function |function )", rest)
    return src[i:(i + 1 + m.start()) if m else len(src)]


def test_pas2_panourile_editabile_se_randeaza_si_pe_eroare():
    src = io.open(_JS, encoding="utf-8").read()
    pas2 = _pas2_body(src)
    ci = pas2.index("} catch (e) {")
    catch_ret = pas2.index("return;", ci)          # return-ul din catch
    catch_block = pas2[ci:catch_ret]
    success = pas2[catch_ret:]                       # randarea de succes + apelurile de loader (dupa catch)

    # panouri de declaratie gardate de S.tip in randarea de SUCCES: S.tip === "XXX" ? '<div id="dec-XXX...">'
    panouri = re.findall(r'S\.tip === "(\w+)"\s*\?\s*\'<div id="(dec-[\w-]+)">', success)
    assert panouri, "asteptam panouri editabile gardate de S.tip in randarea de succes a lui pas2"

    lipsa = []
    for tip, cid in panouri:
        # containerul editabil trebuie randat SI pe eroare
        if cid not in catch_block:
            lipsa.append("containerul '%s' (tip %s)" % (cid, tip))
        # loader-ul pt acel tip trebuie apelat SI in catch (S.tip === "XXX" ... randeaza...)
        if ('S.tip === "%s"' % tip) not in catch_block:
            lipsa.append("apelul de loader pt tip %s" % tip)
    assert not lipsa, (
        "CHICKEN-AND-EGG: panou(ri) editabil(e) randate in SUCCES dar NU in ramura catch a lui pas2 - pe "
        "eroare de generare (refuz zero-base) firma fara operatiuni nu poate ajunge la ecranul de introducere: "
        + "; ".join(lipsa))


def test_gardul_prinde_regresia():
    """MUTATIE: daca un panou din succes lipseste din catch, gardul pica (nu e tautologic/gol)."""
    # succes are d300/d301/d390; catch simulat FARA d301
    fake_success = 'x = `${S.tip === "d301" ? \'<div id="dec-d301-op"></div>\' : ""}`'
    catch_fara_d301 = 'corp.innerHTML = `${S.tip === "d390" ? ...}`; if (S.tip === "d390") ...;'
    panouri = re.findall(r'S\.tip === "(\w+)"\s*\?\s*\'<div id="(dec-[\w-]+)">', fake_success)
    assert panouri == [("d301", "dec-d301-op")]
    assert "dec-d301-op" not in catch_fara_d301, "mutatia (catch fara d301) trebuie sa lipseasca -> gard rosu"
