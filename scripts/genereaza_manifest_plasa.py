# -*- coding: utf-8 -*-
"""scripts/genereaza_manifest_plasa.py — scrie scripts/plasa_16_2.manifest (comanda 16.0, completarea 2, pct.H) și îl verifică; scrie numai la --scrie (17.5-U, U.4).
Sursa manifestului e LISTA aprobată: frontend_test/e2e/e2e_pilot_luna.py întreg plus fișierele de test care citează ID-ul unei poziții „ok” din
~/ghid_incoming/scenarii_pilot.txt. Rezultatele testelor nu intră în alegere: un test roșu rămâne în manifest.
Format (un rând pe fișier, câmpuri separate prin TAB): cale, sha256, teste descoperite (pytest --collect-only), comanda de rulare. Fără globuri.

Uz:
  genereaza_manifest_plasa.py --scrie [<cale manifest>]     scrie manifestul; refuză (ieșire 1, rândurile numite, nimic scris) dacă ar scoate rânduri aflate azi în manifest
  genereaza_manifest_plasa.py --verifica [<cale manifest>]  refuză (ieșire 1, numește fișierul) dacă un fișier lipsește, hash-ul diferă sau numărul de teste diferă; nu scrie niciodată
  genereaza_manifest_plasa.py --help | -h                   tipărește acest text, fără nicio scriere
Fără nicio opțiune, cu o opțiune necunoscută sau cu --scrie împreună cu --verifica: ieșire 2, nimic nu se scrie."""
import hashlib
import io
import os
import re
import subprocess
import sys

import argumente_script

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
MANIFEST = os.path.join(RAD, "scripts", "plasa_16_2.manifest")
SCENARII = os.path.join(RAD, "docs", "scenarii_pilot.txt")   # copia din repo (16.0 pct.4), nu fișierul din afara git-ului
PILOT = "frontend_test/e2e/e2e_pilot_luna.py"
PY = os.path.join(RAD, "venv", "bin", "python")
if not os.path.exists(PY):
    PY = sys.executable


def sha(cale):
    return hashlib.sha256(io.open(os.path.join(RAD, cale), "rb").read()).hexdigest()


def descoperite(cale):
    r = subprocess.run([PY, "-m", "pytest", "--collect-only", "-q", cale], cwd=RAD, capture_output=True, text=True)
    return sum(1 for ln in r.stdout.splitlines() if "::" in ln)


def comanda(cale):
    return "python -m pytest -q %s" % cale


def lista_aprobata():
    import verifica_plasa_pilot as V
    text = io.open(SCENARII, encoding="utf-8").read()
    ok = V.pozitii_ok(text)
    dir_ = os.path.join(RAD, "frontend_test", "e2e")
    fis = {PILOT}
    for f in sorted(os.listdir(dir_)):
        if f.startswith("e2e_") and f.endswith(".py"):
            t = io.open(os.path.join(dir_, f), encoding="utf-8").read()
            if any(re.search(r"\b%s\b" % re.escape(i), t) for i in ok):
                fis.add("frontend_test/e2e/" + f)
    return sorted(fis)


def scoase(lista):
    """Căile aflate azi în manifest pe care lista aprobată nu le mai are (rândurile pe care --scrie le-ar scoate)."""
    if not os.path.exists(MANIFEST):
        return []
    azi = [ln.split("\t")[0] for ln in io.open(MANIFEST, encoding="utf-8") if ln.strip() and not ln.startswith("#")]
    return [c for c in azi if c not in lista]


def scrie():
    lista = lista_aprobata()
    rele = scoase(lista)
    if rele:
        for c in rele:
            print("[plasa fixa] REFUZ --scrie: manifestul ar scoate rândul %s (nu e în lista aprobată); nimic nu s-a scris" % c)
        return 1
    randuri = ["\t".join([c, sha(c), str(descoperite(c)), comanda(c)]) + "\n" for c in lista]
    with io.open(MANIFEST, "w", encoding="utf-8") as o:
        o.write("# plasa_16_2.manifest — plasa fixă a măsurătorii 16.0 (completarea 2, pct.H). Câmpuri separate prin TAB: cale, sha256, teste descoperite, comanda.\n")
        o.writelines(randuri)
    print(open(MANIFEST, encoding="utf-8").read())
    return 0


def verifica():
    rele = []
    for ln in io.open(MANIFEST, encoding="utf-8"):
        if not ln.strip() or ln.startswith("#"):
            continue
        c, h, n, _ = ln.rstrip("\n").split("\t")
        if not os.path.isfile(os.path.join(RAD, c)):
            rele.append("%s: lipsește" % c)
        elif sha(c) != h:
            rele.append("%s: hash diferit" % c)
        elif descoperite(c) != int(n):
            rele.append("%s: %d teste descoperite, manifestul spune %s" % (c, descoperite(c), n))
    for m in rele:
        print("[plasa fixa] REFUZ " + m)
    return 1 if rele else 0


def main(argv):
    global MANIFEST
    a = argumente_script.citeste(argv, __doc__, flaguri=("--scrie", "--verifica"), pozitionale=1, prefix="[plasa fixa]")
    uz = __doc__[__doc__.index("Uz:"):].rstrip()
    scrie_, verifica_ = "--scrie" in a, "--verifica" in a
    if scrie_ == verifica_:
        print("[plasa fixa] %s — nimic nu se scrie.\n%s" % ("--scrie și --verifica împreună" if scrie_ else "fără --scrie sau --verifica", uz), file=sys.stderr)
        return 2
    cale = [x for x in a if not x.startswith("--")]
    if cale:
        MANIFEST = os.path.abspath(cale[0])
    return scrie() if scrie_ else verifica()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
