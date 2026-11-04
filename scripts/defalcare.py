# -*- coding: utf-8 -*-
"""scripts/defalcare.py — duratele lotului, citite din jurnalul .lot_jurnal.log (comanda 16.1, pct.2). `python scripts/defalcare.py <lot>`: fiecare fază cu început, sfârșit,
rezultat și secunde; totalul pe fază; de la prima la ultima înregistrare. Raportul copiază această ieșire (git rămâne pentru control, nu pentru durate)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import jurnal_lot as JL  # noqa: E402


def main(a):
    if not a:
        print(__doc__)
        return 2
    rows = JL.durate(a[0])
    if not rows:
        print("[defalcare] niciun rând pentru lotul %s în %s" % (a[0], JL.cale_jurnal()))
        return 1
    tot = {}
    for faza, _, b, s, r, sec in rows:
        print("%-20s %-12s %s -> %s  %s s" % (faza, r, b, s, sec))
        if sec != "":
            tot[faza] = tot.get(faza, 0) + sec
    print("--- total pe fază (s): " + ", ".join("%s %d" % kv for kv in sorted(tot.items())))
    import datetime
    t0, t1 = min(r[2] for r in rows), max(r[3] for r in rows if r[3] != "-")
    print("--- de la prima la ultima înregistrare: %d s" % (datetime.datetime.fromisoformat(t1) - datetime.datetime.fromisoformat(t0)).total_seconds())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
