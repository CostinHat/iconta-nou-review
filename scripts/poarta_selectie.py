# -*- coding: utf-8 -*-
"""scripts/poarta_selectie.py — ce rulează poarta implicită (comanda 15.G, 30.10.2026), derivat mecanic; nu primește fișiere în argv.

Tipărește JSON: {"pytest": [fișiere core/test_*.py], "e2e": [fișiere e2e_*.py], "motive": {fișier: de ce}, "incerte": [...]}.
  1. testele fișierelor atinse de la ultima publicare (`main`): `poarta_scurta.selectie`, nivelul `direct`; nesiguranța derivării NU
     extinde la suita întreagă (se listează în `incerte`) — suita întreagă e doar poarta de noapte;
  2. scenariile deficiențelor: core/test_lot*scenariu* și e2e-urile numerotate (e2e_lot*.py) + scenariul lunii pilot (e2e_pilot_luna.py);
  3. nucleul fiscal și de calcul: declarații (d###), TVA, solduri, stocuri, salarii, balanță.
Ce e pe lista de sărit (`poarta_sare`) nu apare. „Testele picate la ultima rulare" sunt `pytest --lf` / fișierul de cazute al plasei (poarta_lot.sh)."""
import glob
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import perimetru as P  # noqa: E402
import poarta_scurta as S  # noqa: E402
import poarta_sare  # noqa: E402

RAD = P.RAD
NUCLEU = re.compile(r"^test_(d\d{3}|.*(tva|sold|stoc|salar|declarat|balanta))")
BAZA_PUBLICAT = "main"


def _rel(cale):
    return os.path.relpath(cale, RAD)


def selecteaza():
    motive = {}

    def pune(f, de_ce):
        motive.setdefault(f, []).append(de_ce)

    baza = subprocess.run(["git", "merge-base", "HEAD", BAZA_PUBLICAT], cwd=RAD, capture_output=True, text=True).stdout.strip()
    incerte = []
    if baza:
        P.BAZA = baza
        atinse = P.atinse_din_git()
        teste, incerte, e2e, _front, _nev = S.selectie(atinse, "direct")
        for t in teste:
            pune(t, "atins de la ultima publicare")
        for e, ms in e2e.items():
            if any(S.PLASA_INTREAGA in m for m in ms):
                continue                      # conftest-ul plasei / e2e_poarta.py atins: nu extinde la toată plasa (doar poarta de noapte)
            pune(e, "atins de la ultima publicare")
    for f in sorted(glob.glob(os.path.join(RAD, "core", "test_lot*scenariu*.py"))):
        pune(_rel(f), "scenariu")
    for f in sorted(glob.glob(os.path.join(RAD, "frontend_test", "e2e", "e2e_lot*.py"))) + [os.path.join(RAD, "frontend_test", "e2e", "e2e_pilot_luna.py")]:
        if os.path.isfile(f):
            pune(_rel(f), "scenariu")
    for f in sorted(glob.glob(os.path.join(RAD, "core", "test_*.py"))):
        if NUCLEU.match(os.path.basename(f)):
            pune(_rel(f), "nucleu fiscal / calcul")
    ramase = {f: m for f, m in motive.items() if os.path.isfile(os.path.join(RAD, f)) and not poarta_sare.sare_fisier(os.path.join(RAD, f))}
    return {"pytest": sorted(f for f in ramase if f.startswith("core/") and os.path.basename(f).startswith("test_")),
            "e2e": sorted(os.path.basename(f) for f in ramase if f.startswith("frontend_test/e2e/")),
            "motive": ramase, "incerte": list(incerte), "baza": baza}


if __name__ == "__main__":
    print(json.dumps(selecteaza(), ensure_ascii=False, indent=1))
