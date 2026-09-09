# -*- coding: utf-8 -*-
"""scripts/p4_artefacte.py — artefactele lui P4, scrise din INSTRUMENT, nu din raport.

Trei fișiere în `masuratori/p4/`, toate derivate la rulare:

  * `inventar_brut.txt` / `.json` — inventarul brut (îl scrie `scan_tranzactii --inventar`);
  * `clasificare.txt` — fiecare candidat cu clasa lui și motivul, confruntat cu inventarul;
  * `efecte_ireversibile.txt` — locurile pe care `rollback` nu le desface, cu verdictul fiecăruia.

Rulare: `./venv/bin/python -m scripts.p4_artefacte`
"""
from __future__ import annotations

import io
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAD not in sys.path:
    sys.path.insert(0, RAD)

from core import p4_clasificare as CL      # noqa: E402
from scripts import scan_tranzactii as ST  # noqa: E402

DIR = os.path.join(RAD, "masuratori", "p4")


def _scrie(nume, text):
    os.makedirs(DIR, exist_ok=True)
    cale = os.path.join(DIR, nume)
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    print("scris: %s" % cale)


def _peste_prag(inv):
    out = {}
    for x in inv:
        a = x["analiza"]
        if a["domenii_care_scriu"] > 1 or a["partial_commit"] or a["extern_in_tranzactie"]:
            out[x["intrare"]] = a
    return out


def clasificare_text(inv):
    peste = _peste_prag(inv)
    L = []
    L.append("CLASIFICAREA OPERATIILOR COMPUSE — pasul B si C din comanda P4")
    L.append("Generat cu: ./venv/bin/python -m scripts.p4_artefacte")
    L.append("Sursa listei: scripts/scan_tranzactii.py (mecanic) · sursa judecatii: "
             "core/p4_clasificare.py")
    L.append("=" * 78)
    nr = {}
    for v in CL.CLASIFICARE.values():
        nr[v["clasa"]] = nr.get(v["clasa"], 0) + 1
    L.append("candidati peste prag, la rularea asta: %d" % len(peste))
    L.append("clasificari scrise: %d  (%s)"
             % (len(CL.CLASIFICARE), " · ".join("%s %d" % (k, nr[k]) for k in sorted(nr))))
    L.append("cai critice fara proba de injectie: %d"
             % len([1 for c, p in CL.probe_cerute().items() if not p]))
    L.append("excluderi fara justificare scrisa: %d"
             % len([1 for _c, m in CL.excluderi().items() if len((m or '').strip()) < 80]))
    L.append("")
    for clasa in (CL.CRITIC, CL.NECRITIC, CL.FALS):
        L.append("=" * 78)
        L.append("### %s" % clasa)
        L.append("")
        for cale, v in CL.CLASIFICARE.items():
            if v["clasa"] != clasa:
                continue
            a = peste.get(cale)
            L.append("%s" % cale)
            if a:
                L.append("    in inventar : %d domenii care scriu · %d commituri partiale · "
                         "%d efecte ireversibile in tranzactie"
                         % (a["domenii_care_scriu"], len(a["partial_commit"]),
                            len(a["extern_in_tranzactie"])))
            elif v.get("reparat"):
                L.append("    in inventar : IESITA dupa reparatie (randul ramane ca urma)")
            elif v.get("cale_interna"):
                L.append("    in inventar : cale INTERNA, nu punct de intrare")
            L.append("    efecte      : %s" % v["efecte"])
            L.append("    de ce       : %s" % v["de_ce"])
            if v.get("reparatie"):
                L.append("    reparatie   : %s" % v["reparatie"])
            if v.get("proba"):
                L.append("    proba       : core/test_p4_fault_injection.py::%s" % v["proba"])
            L.append("")
    return "\n".join(L)


def efecte_text(inv):
    situri = {}
    for x in inv:
        for e in x["analiza"]["extern_in_tranzactie"]:
            situri.setdefault(e["unde"], set()).add(x["intrare"])
    L = []
    L.append("EFECTELE PE CARE `ROLLBACK` NU LE DESFACE — analiza separata ceruta de P4")
    L.append("Generat cu: ./venv/bin/python -m scripts.p4_artefacte")
    L.append("Lista locurilor e DERIVATA (scan_tranzactii.analiza -> extern_in_tranzactie);")
    L.append("verdictul fiecaruia e scris in core/p4_clasificare.EFECTE_EXTERNE si pazit de")
    L.append("core/test_tranzactii_clasificate.py — un loc nou, nejudecat, cade poarta.")
    L.append("=" * 78)
    n_int = len([1 for v in CL.EFECTE_EXTERNE.values() if v["fel"] == CL.INTEROGARE])
    n_ef = len([1 for v in CL.EFECTE_EXTERNE.values() if v["fel"] == CL.EFECT])
    L.append("locuri gasite la rularea asta: %d · judecate: %d (%d interogari, %d efecte)"
             % (len(situri), len(CL.EFECTE_EXTERNE), n_int, n_ef))
    L.append("")
    for loc in sorted(set(situri) | set(CL.EFECTE_EXTERNE)):
        v = CL.EFECTE_EXTERNE.get(loc)
        L.append("%s" % loc)
        L.append("    cai atinse : %d%s" % (len(situri.get(loc, ())),
                                            "" if loc in situri else "  (NU mai apare in cod)"))
        for c in sorted(situri.get(loc, ()))[:6]:
            L.append("        %s" % c)
        if v is None:
            L.append("    VERDICT    : LIPSA — nejudecat")
        else:
            L.append("    fel        : %s" % v["fel"])
            L.append("    ce e       : %s" % v["ce_e"])
            L.append("    verdict    : %s" % v["verdict"])
        L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    if not ST.calibreaza(verbose=True):
        sys.exit(2)
    print()
    inv, stat = ST.inventar()
    _scrie("inventar_brut.txt", ST.raport_text(inv, stat))
    import json
    _scrie("inventar_brut.json",
           json.dumps({"stat": stat, "candidati": inv}, ensure_ascii=False, indent=2))
    _scrie("clasificare.txt", clasificare_text(inv))
    _scrie("efecte_ireversibile.txt", efecte_text(inv))
    print()
    print("CIFRELE LUI P4, la rularea asta:")
    print("  puncte de intrare parcurse            : %d" % stat["intrari"])
    print("  candidati (cel putin un semn C1..C6)  : %d" % stat["candidati"])
    print("  cai peste prag (cer clasificare)      : %d" % len(_peste_prag(inv)))
    print("  CRITICAL_COMPOSITES                   : %d" % len(CL.cai_critice()))
    print("  ...cu proba de injectie               : %d"
          % len([p for p in CL.probe_cerute().values() if p]))
    print("  UNEXPLAINED_EXCLUSIONS                : %d"
          % len([1 for _c, m in CL.excluderi().items() if len((m or '').strip()) < 80]))
    print("  efecte ireversibile in tranzactie     : %d locuri, toate judecate: %s"
          % (len(CL.EFECTE_EXTERNE),
             set(CL.EFECTE_EXTERNE) >= {e["unde"] for x in inv
                                        for e in x["analiza"]["extern_in_tranzactie"]}))
