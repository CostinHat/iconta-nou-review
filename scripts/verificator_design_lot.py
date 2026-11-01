# -*- coding: utf-8 -*-
"""Rulează verificatorul mecanic pe o listă de ecrane, la ambele rezoluții, și tipărește matricea a–h.
Uz: python scripts/verificator_design_lot.py <director> <nume ecran>... | --grup=cabinet|admin|firma | --toate"""
import json
import os
import subprocess
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
import verificator_design as v  # noqa: E402

REZ = ("1920x1080", "1366x768")


def main(argv):
    director, rest = argv[0], argv[1:]
    reg = v.registru()
    if rest and rest[0].startswith("--grup="):
        nume = [e["nume"] for e in reg if e.get("grup") == rest[0].split("=")[1]]
    elif rest and rest[0] == "--toate":
        nume = [e["nume"] for e in reg]
    else:
        nume = rest
    py = os.path.join(RAD, "venv", "bin", "python")
    print("%-52s %s" % ("ecran", "  ".join("%-9s" % r for r in REZ)))
    for n in nume:
        linie = []
        for rez in REZ:
            r = subprocess.run([py, os.path.join(RAD, "scripts", "verificator_design.py"), "ecran", n, rez, director], capture_output=True, text=True)
            try:
                m = json.load(open(os.path.join(director, "%s_%s.json" % (v.slug(n), rez)), encoding="utf-8"))
                linie.append("".join(k if m["verdict_mecanic"][k]["verdict"] == "PICĂ" else "." for k in "abcdefgh"))
            except Exception:  # noqa: BLE001
                linie.append("NEDESCHIS (%s)" % (r.stderr or r.stdout)[-60:].strip())
        print("%-52s %s" % (n[:52], "  ".join("%-9s" % x for x in linie)), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
