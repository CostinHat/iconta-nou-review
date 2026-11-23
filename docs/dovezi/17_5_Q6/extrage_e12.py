# -*- coding: utf-8 -*-
"""17.5-Q6 — martorii e.1 / e.2 pentru index_matrice.tsv, din rularea DEDICATĂ a testului înghețat și din originalul independent al colectorului.
    python extrage_e12.py RAD_DOVEZI DIR_RULARE DIR_COLECTOR COMMIT DIR_IESIRE
DIR_RULARE: directorul rulării (junit.xml / q6.xml, capturi/17_5_Q6/{masuri.json,e.1.png,e.2.png}); DIR_COLECTOR, DIR_IESIRE: relative la RAD_DOVEZI.
Scrie în DIR_IESIRE: masuri_<id>_F1_<rez>.json (obiectul ID-ului din masuri.json, neschimbat), captura_<id>_F1_<rez>.png (prima vedere a testului),
sursa_<id>_F1_<rez>.json (commit, scenariu, caz, rezoluție, originalul colectorului, localizarea, valorile și extragerile) și o copie a masuri.json integral."""
import hashlib
import json
import shutil
import sys
from pathlib import Path


def main(rad, rulare, dir_col, commit, dir_ies):
    rad, rulare = Path(rad), Path(rulare)
    ies = rad / dir_ies
    ies.mkdir(parents=True, exist_ok=True)
    cap = rulare / "capturi" / "17_5_Q6"
    integral = cap / "masuri.json"
    masuri = json.loads(integral.read_text(encoding="utf-8"))
    shutil.copy(integral, ies / "masuri_integral.json")
    for ident, rez in (("e.1", "603x590"), ("e.2", "1366x768")):
        k = f"{ident}_F1_{rez}"
        if ident not in masuri:
            print(f"{ident}: lipsește din masuri.json (rularea nu a ajuns la verdict)")
            continue
        (ies / f"masuri_{k}.json").write_text(json.dumps(masuri[ident], ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        shutil.copy(cap / f"{ident}.png", ies / f"captura_{k}.png")
        meta = json.loads((rad / dir_col / f"original_meta_{k}.json").read_text(encoding="utf-8"))
        if meta["commit"] != commit:
            raise SystemExit(f"{ident}: originalul colectorului e de pe {meta['commit']}, nu de pe {commit}")
        orig = rad / meta["original"]
        if hashlib.sha256(orig.read_bytes()).hexdigest() != meta["sha256_original"]:
            raise SystemExit(f"{ident}: SHA-ul originalului diferă")
        sursa = {"commit": commit, "scenariu": ident, "caz": "F1", "rezolutie": rez, "original": meta["original"], "sha256_original": meta["sha256_original"],
                 "localizare": "Declarații pasul 1, F1 Comert Stoc SRL, select #dec-tip (opțiunile native, înainte de interacțiune); măsurile: masuri.json al rulării dedicate a e2e_ferestre_17_5_Q6.py",
                 "valori": meta["valori"], "extrageri": meta["extrageri"]}
        (ies / f"sursa_{k}.json").write_text(json.dumps(sursa, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
        print(f"{ident}: scris {k}")


if __name__ == "__main__":
    if len(sys.argv) != 6:
        raise SystemExit(__doc__)
    main(*sys.argv[1:])
