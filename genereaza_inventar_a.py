#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator PARTIAL al Inventarului A — partea STRUCTURATA (derivabila din cod).

SURSA structurata: common.COTE (Temei structurat) -> cluster / valoare / temei / data_in /
data_out / estimat. Se regenereaza din cod (ca ISTORIC, genereaza_grupe_functii).

OVERLAY (judecati umane, PERSISTENTE, NEDERIVABILE din cod): INVENTAR_A_OVERLAY.tsv -> Risc
(FISCAL/STRUCTURA), Verificat la sursa (√ DD.MM / PARTIAL), nota. Regenerarea NU pierde overlay-ul
(proposal point 3, 31.07.2026): fara asta, auto-generarea ar sterge tocmai informatia care nu e
in cod.

Rulare:  python3 genereaza_inventar_a.py            (dry-run: afiseaza)
         python3 genereaza_inventar_a.py --scrie    (scrie INVENTAR_A.md)"""
import os, sys

_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)
from core.common import COTE, Temei  # noqa: E402

OVERLAY = os.path.join(_DIR, "INVENTAR_A_OVERLAY.tsv")
OUT = os.path.join(_DIR, "INVENTAR_A.md")


def structura():
    """Randurile derivabile din common.COTE (partea GENERATA)."""
    rows = []
    for nume, intrari in COTE.items():
        din, val, t = sorted(intrari, key=lambda r: r[0], reverse=True)[0]
        data_out = t.data_out.isoformat() if getattr(t, "data_out", None) else "—"
        if getattr(t, "estimat", False):
            data_out += " (ESTIMAT)"
        rows.append({"cluster": nume, "valoare": str(val), "temei": str(t),
                     "data_in": din.isoformat(), "data_out": data_out})
    return rows


def overlay():
    """Judecatile umane keyed pe cluster. TSV: cluster<TAB>risc<TAB>verificat<TAB>nota."""
    o = {}
    if os.path.exists(OVERLAY):
        for ln in open(OVERLAY, encoding="utf-8"):
            ln = ln.rstrip("\n")
            if not ln or ln.startswith("#"):
                continue
            p = ln.split("\t")
            o[p[0]] = {"risc": p[1] if len(p) > 1 else "",
                       "verificat": p[2] if len(p) > 2 else "",
                       "nota": p[3] if len(p) > 3 else ""}
    return o


def genereaza():
    rows = structura()
    ov = overlay()
    L = ["# INVENTAR A — structura GENERATA din common.COTE + overlay judecati umane",
         "",
         "GENERAT de `genereaza_inventar_a.py` (nu edita direct partea de tabel). Structura",
         "(cluster/valoare/temei/data_in/data_out) se regenereaza din cod; judecatile umane",
         "(Risc/Verificat/nota) traiesc in `INVENTAR_A_OVERLAY.tsv` si NU se pierd la regenerare.",
         "",
         "| Cluster | Valoare | Temei (structurat) | data_in | data_out | Risc | Verificat la sursă | Notă |",
         "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        j = ov.get(r["cluster"], {})
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["cluster"], r["valoare"], r["temei"], r["data_in"], r["data_out"],
            j.get("risc") or "—", j.get("verificat") or "—", j.get("nota") or ""))
    orfane = [k for k in ov if k not in {r["cluster"] for r in rows}]
    if orfane:
        L += ["", "**Overlay ORFAN** (judecata umana fara cota in cod, de reconciliat): " + ", ".join(orfane)]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    txt = genereaza()
    if "--scrie" in sys.argv:
        open(OUT, "w", encoding="utf-8").write(txt)
        print("scris:", OUT)
    else:
        print(txt)
        print("--- dry-run; --scrie pentru INVENTAR_A.md ---")
