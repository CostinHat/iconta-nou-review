# -*- coding: utf-8 -*-
"""CLASIFICAREA rutelor fără apelant — R70, blocul SSS (29.08.2026).

R70 spune că o rută scrisă, gardată și verde, dar nechemată, e cod care nu se execută — și că un
instrument are nevoie de o cale de **declarare**, altfel ar cere ștergerea a ce e păstrat intenționat.
Calea aia există: marcajul `[api_intern_v1]` pe linia decoratorului. Ce lipsea era **clasificarea**:
fiecare rută fără apelant e ori **API intenționată**, cu motivul scris, ori **candidat la ștergere**.

**NU ȘTERGE NIMIC, și nici nu propune ștergerea ca decizie luată.** Un candidat rămâne candidat până
la o confirmare separată — cerut explicit la SSS3.

DE UNDE CITEȘTE: `core/test_ruta_fara_apelant.py`. Detectorul, lista de artefacte și cititorul de
marcaje trăiesc acolo, cu calibrările lor; a le rescrie aici ar fi însemnat două definiții ale lui
„fără apelant" (P1). *Un script care importă un modul de test e neobișnuit — dar alternativa era o a
doua copie a discriminatorului, iar aia se desincronizează.*

LIMITA, moștenită și declarată: detectorul caută ultimul segment al căii în textul din `static/`. O
rută chemată printr-o cale **compusă la rulare** nu e găsită — deci lista e un **plafon superior**,
nu un număr exact. E chiar orbirea măsurată la R80.

    ./venv/bin/python scripts/scan_rute_clasificate.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import test_ruta_fara_apelant as _t  # noqa: E402


def clasifica():
    st = _t._scan()
    rute = st.citeste_rute()
    fara = _t._fara_apelant(rute, _t._static())
    declarate = _t.declarate()
    artefacte = set(_t._ARTEFACTE)
    api, candidate, artef = [], [], []
    for metoda, cale in sorted(fara):
        if (metoda, cale) in declarate or cale in declarate:
            api.append((metoda, cale))
        elif (metoda, cale) in artefacte or cale in artefacte:
            artef.append((metoda, cale))
        else:
            candidate.append((metoda, cale))
    return rute, fara, api, artef, candidate


def main():
    rute, fara, api, artef, candidate = clasifica()
    vizibile, total, procent = _t._acoperire()
    print("RUTE în inventar: %d · fără apelant în `static/`: %d" % (len(rute), len(fara)))
    print("acoperirea detectorului: %d din %d (%d%%) — restul au căi compuse la rulare, pe care "
          "căutarea pe text nu le vede (R80)\n" % (vizibile, total, procent))

    print("A. API INTENȚIONATĂ — declarată în cod cu `[api_intern_v1]`: %d" % len(api))
    for m, c in api:
        print("   %-6s %s" % (m, c))
    print("\nB. ARTEFACTE CUNOSCUTE ale detectorului (nu sunt rute reale fără apelant): %d" % len(artef))
    for m, c in artef:
        print("   %-6s %s" % (m, c))
    print("\nC. CANDIDAȚI — fără apelant și FĂRĂ declarație: %d" % len(candidate))
    if not candidate:
        print("   (niciunul)")
    for m, c in candidate:
        print("   %-6s %s" % (m, c))
    print("\n*Un candidat NU e cod mort dovedit: poate fi chemat printr-o cale compusă la rulare.*")
    print("*Nu se șterge nimic din script — clasificarea e o listă, nu o acțiune.*")
    return api, artef, candidate


if __name__ == "__main__":
    main()
