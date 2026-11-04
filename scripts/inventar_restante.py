# -*- coding: utf-8 -*-
"""scripts/inventar_restante.py — inventarul canonic al restanței e2e (comanda 16.0, pct.3 și 5).
  valideaza            refuză (ieșire 1) un rând fără ID, clasă validă sau (la clasa c) număr de deficiență
  scade <log>...       citește liniile `FAILED <fișier>::<test>` din loguri; picăturile cu rând a/b/c în inventar sunt „restanță <ID>” (nu fac ROȘU);
                       ieșire 1 dacă rămâne cel puțin o picătură fără rând (baza s-a mișcat) — le numește."""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INV = os.path.join(RAD, "scripts", "poarta_e2e_restante.txt")
CLASE = set("abcdef")


def citeste():
    rows = []
    for n, ln in enumerate(open(INV, encoding="utf-8"), 1):
        if not ln.strip() or ln.startswith("#"):
            continue
        p = [x.strip() for x in ln.rstrip("\n").split(" | ")]
        rows.append((n, p))
    return rows


def valideaza():
    rele = []
    for n, p in citeste():
        if len(p) < 6 or not re.fullmatch(r"R\d{3,}", p[0]):
            rele.append("rândul %d: fără ID (R001…) sau câmpuri lipsă" % n)
        elif p[2] not in CLASE:
            rele.append("rândul %d (%s): clasă invalidă %r" % (n, p[0], p[2]))
        elif p[2] == "c" and not re.fullmatch(r"\d+(\.\d+)?", p[3]):
            rele.append("rândul %d (%s): clasa c cere numărul din DEFICIENTE" % (n, p[0]))
    ids = [p[0] for _, p in citeste()]
    rele += ["ID dublat: %s" % i for i in sorted({i for i in ids if ids.count(i) > 1})]
    return rele


def scade(loguri):
    inv = {p[1].split("::")[-1].split("[")[0]: p for _, p in citeste() if p[2] in ("a", "b", "c")}
    cazute = set()
    for l in loguri:
        for ln in open(l, encoding="utf-8", errors="replace"):
            m = re.match(r"(?:FAILED|ERROR) (?:\S*/)?(\S+?\.py)::(\S+?)(?:\[.*\])?(?: - .*)?\s*$", ln)
            if m:
                cazute.add((m.group(1), m.group(2)))
    scazute, ramase = [], []
    for f, t in sorted(cazute):
        (scazute if t in inv and inv[t][1].startswith(f) else ramase).append((f, t))
    for f, t in scazute:
        print("restanță %s (%s) %s::%s" % (inv[t][0], inv[t][2] + (" " + inv[t][3] if inv[t][3] != "-" else ""), f, t))
    for f, t in ramase:
        print("PICĂ FĂRĂ RÂND ÎN INVENTAR: %s::%s" % (f, t))
    print("[inventar] %d picături scăzute ca restanță, %d rămase" % (len(scazute), len(ramase)))
    return 1 if ramase else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "valideaza":
        r = valideaza()
        for x in r:
            print("[inventar] REFUZ " + x)
        sys.exit(1 if r else 0)
    if len(sys.argv) > 2 and sys.argv[1] == "scade":
        sys.exit(scade(sys.argv[2:]))
    print(__doc__)
    sys.exit(2)
