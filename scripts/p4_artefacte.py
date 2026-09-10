# -*- coding: utf-8 -*-
"""scripts/p4_artefacte.py — artefactele lui P4, scrise din INSTRUMENT, nu din raport.

Patru fișiere în `masuratori/p4/`, toate derivate la rulare:

  * `inventar_brut.txt` / `.json` — inventarul brut (callchain, `file:line`, frontiere, efecte);
  * `clasificare.txt` — **fiecare** candidat brut cu verdictul lui, regula care l-a produs și
    motivul concret. Nu doar cei de peste un prag: **toți**;
  * `efecte_ireversibile.txt` — locurile pe care `rollback` nu le desface, cu verdictul fiecăruia;
  * `acceptare.txt` — blocul de cifre al acceptării, derivat.

Rulare: `./venv/bin/python -m scripts.p4_artefacte`
"""
from __future__ import annotations

import io
import json
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


def clasificare_text(inv):
    """FIECARE candidat brut, cu verdict, regulă și motiv. Fără prag, fără selecție."""
    n = CL.numaratori(inv)
    L = []
    L.append("CLASIFICAREA COMPLETA A CANDIDATILOR BRUTI — pasii B si C din comanda P4")
    L.append("Generat cu: ./venv/bin/python -m scripts.p4_artefacte")
    L.append("Sursa listei: scripts/scan_tranzactii.py (mecanic)")
    L.append("Sursa judecatii: core/p4_clasificare.py — randuri INDIVIDUALE + REGULI pe clasa")
    L.append("Pazit de: core/test_tranzactii_clasificate.py")
    L.append("=" * 78)
    L.append("")
    L.append("REGULA LUI P4: orice cale care aprinde CEL PUTIN UNUL din C1..C6 e candidat.")
    L.append("NU exista prag suplimentar inaintea clasificarii. Toti candidatii de mai jos au")
    L.append("verdict; niciunul n-a fost declarat neimportant inainte de a fi clasificat.")
    L.append("")
    L.append("RAW_CANDIDATES              = %d" % n["RAW_CANDIDATES"])
    L.append("CLASSIFIED_CANDIDATES       = %d" % n["CLASSIFIED_CANDIDATES"])
    L.append("UNCLASSIFIED_RAW_CANDIDATES = %d" % n["UNCLASSIFIED_RAW_CANDIDATES"])
    L.append("  RAW_CRITICAL_COMPOSITES     = %d" % n["RAW_CRITICAL_COMPOSITES"])
    L.append("  RAW_NON_CRITICAL_COMPOSITES = %d" % n["RAW_NON_CRITICAL_COMPOSITES"])
    L.append("  RAW_FALSE_POSITIVES         = %d" % n["RAW_FALSE_POSITIVES"])
    L.append("  RAW_CLASS_SUM               = %d   (%s)"
             % (n["RAW_CLASS_SUM"], n["RAW_CLASS_ACCOUNTING"]))
    L.append("")
    L.append("Caile INTERNE (nu sunt puncte de intrare, deci NU sunt in cei de mai sus):")
    L.append("  INTERNAL_CRITICAL_COMPOSITES = %d" % n["INTERNAL_CRITICAL_COMPOSITES"])
    L.append("  TOTAL_CRITICAL_OPERATIONS    = %d" % n["TOTAL_CRITICAL_OPERATIONS"])
    L.append("")
    L.append("PE REGULA:")
    for cod in sorted(n["pe_regula"]):
        titlu = CL.INDIVIDUAL if cod == CL.INDIVIDUAL else next(
            (r["titlu"] for r in CL.REGULI if r["cod"] == cod), "?")
        L.append("  %-22s %4d   %s" % (cod, n["pe_regula"][cod],
                                       "rand scris, per cale" if cod == CL.INDIVIDUAL else titlu))
    L.append("")
    L.append("REGULILE, in ordinea aplicarii (prima care se potriveste da verdictul):")
    L.append("  %-22s %-22s %s" % ("cod", "clasa", "cand se aplica"))
    L.append("  %-22s %-22s %s" % (CL.INDIVIDUAL, "(a randului scris)",
                                   "calea are un rand in CLASIFICARE"))
    L.append("  %-22s %-22s %s" % ("(niciuna)", "-> cere judecata",
                                   "scrieri in >1 tranzactie, commit partial, "
                                   "sau efect ireversibil in tranzactie"))
    for r in CL.REGULI:
        L.append("  %-22s %-22s %s" % (r["cod"], r["clasa"], r["titlu"]))
    L.append("")
    L.append("=" * 78)

    pe_clasa = {}
    for x in inv:
        v = CL.verdict(x)
        pe_clasa.setdefault(v["clasa"] if v else "NECLASIFICAT", []).append((x, v))
    for clasa in (CL.CRITIC, CL.NECRITIC, CL.FALS, "NECLASIFICAT"):
        randuri = pe_clasa.get(clasa, [])
        if not randuri:
            continue
        L.append("")
        L.append("### %s — %d" % (clasa, len(randuri)))
        L.append("")
        for x, v in sorted(randuri, key=lambda p: p[0]["intrare"]):
            f = x["fapte"]
            a = x["analiza"]
            L.append("%s" % x["intrare"])
            L.append("    semne      : %s" % ", ".join(sorted(x["semne"])))
            L.append("    fapte      : %d domenii (%d scriu) · %d scrieri in %d tabele · "
                     "%d efecte externe%s%s"
                     % (f["domenii_total"], f["domenii_care_scriu"], f["scrieri_total"],
                        len(f["tabele"]), f["externe_total"],
                        " · COMMIT PARTIAL" if a["partial_commit"] else "",
                        " · EFECT IREVERSIBIL IN TRANZACTIE"
                        if a["extern_in_tranzactie"] else ""))
            L.append("    verdict    : %s" % (v["clasa"] if v else "LIPSA"))
            L.append("    regula     : %s" % (v["regula"] if v else "-"))
            L.append("    de ce      : %s" % (v["de_ce"] if v else "-"))
            if v and v["regula"] == CL.INDIVIDUAL:
                rand = CL.CLASIFICARE[x["intrare"]]
                if rand.get("reparatie"):
                    L.append("    reparatie  : %s" % rand["reparatie"])
                if rand.get("proba"):
                    L.append("    proba      : core/test_p4_fault_injection.py::%s"
                             % rand["proba"])
            L.append("")
    # randurile individuale care NU sunt puncte de intrare (cai interne)
    interne = {k: v for k, v in CL.CLASIFICARE.items() if v.get("cale_interna")}
    if interne:
        L.append("=" * 78)
        L.append("### CAI INTERNE — nu sunt puncte de intrare, deci nu apar in inventarul brut")
        L.append("")
        for k, v in interne.items():
            L.append("%s" % k)
            L.append("    verdict    : %s" % v["clasa"])
            L.append("    efecte     : %s" % v["efecte"])
            L.append("    de ce      : %s" % v["de_ce"])
            L.append("    reparatie  : %s" % v.get("reparatie", "-"))
            L.append("    proba      : core/test_p4_fault_injection.py::%s" % v.get("proba", "-"))
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


def acceptare(inv, stat):
    """Blocul de cifre al acceptarii, DERIVAT — pe DOUA universuri, numite separat.

    `RAW_*` inchide inventarul brut; `INTERNAL_*` / `TOTAL_*` privesc operatiile critice, unde
    intra si caile interne, care nu sunt puncte de intrare. Cele doua nu se aduna intre ele —
    prima forma a blocului le punea sub acelasi nume si dadea 333 pe o populatie de 332.
    """
    n = CL.numaratori(inv)
    gaps = [x["intrare"] for x in inv
            if x["analiza"]["domenii_care_scriu"] > 1 and CL.verdict(x) is None]
    partiale = [x["intrare"] for x in inv
                if x["analiza"]["partial_commit"] and CL.verdict(x) is None]
    L = []
    L.append("BLOCUL DE ACCEPTARE P4 — derivat, nu scris")
    L.append("Generat cu: ./venv/bin/python -m scripts.p4_artefacte")
    L.append("=" * 78)
    L.append("")
    L.append("--- UNIVERSUL 1: INVENTARUL BRUT (puncte de intrare) ------------------------")
    L.append("RAW_CANDIDATES=%d" % n["RAW_CANDIDATES"])
    L.append("CLASSIFIED_CANDIDATES=%d" % n["CLASSIFIED_CANDIDATES"])
    L.append("")
    L.append("RAW_CRITICAL_COMPOSITES=%d" % n["RAW_CRITICAL_COMPOSITES"])
    L.append("RAW_NON_CRITICAL_COMPOSITES=%d" % n["RAW_NON_CRITICAL_COMPOSITES"])
    L.append("RAW_FALSE_POSITIVES=%d" % n["RAW_FALSE_POSITIVES"])
    L.append("")
    L.append("RAW_CLASS_SUM=%d   (= %d + %d + %d)"
             % (n["RAW_CLASS_SUM"], n["RAW_CRITICAL_COMPOSITES"],
                n["RAW_NON_CRITICAL_COMPOSITES"], n["RAW_FALSE_POSITIVES"]))
    L.append("RAW_CLASS_ACCOUNTING=%s   (RAW_CLASS_SUM == CLASSIFIED_CANDIDATES == "
             "RAW_CANDIDATES)" % n["RAW_CLASS_ACCOUNTING"])
    L.append("UNCLASSIFIED_RAW_CANDIDATES=%d" % n["UNCLASSIFIED_RAW_CANDIDATES"])
    L.append("")
    L.append("--- UNIVERSUL 2: OPERATIILE CRITICE (inclusiv caile interne) ----------------")
    L.append("INTERNAL_CRITICAL_COMPOSITES=%d   (%s)"
             % (n["INTERNAL_CRITICAL_COMPOSITES"], ", ".join(CL.cai_interne()) or "-"))
    L.append("TOTAL_CRITICAL_OPERATIONS=%d   (= RAW_CRITICAL_COMPOSITES %d + "
             "INTERNAL_CRITICAL_COMPOSITES %d)"
             % (n["TOTAL_CRITICAL_OPERATIONS"], n["RAW_CRITICAL_COMPOSITES"],
                n["INTERNAL_CRITICAL_COMPOSITES"]))
    L.append("")
    L.append("CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS=%d"
             % n["CRITICAL_OPERATIONS_REQUIRING_FAULT_TESTS"])
    L.append("CRITICAL_OPERATIONS_WITH_FAULT_TESTS=%d"
             % n["CRITICAL_OPERATIONS_WITH_FAULT_TESTS"])
    L.append("UNTESTED_CRITICAL_OPERATIONS=%d%s"
             % (n["UNTESTED_CRITICAL_OPERATIONS"],
                ("   " + ", ".join(n["netestate"])) if n["netestate"] else ""))
    L.append("")
    L.append("--- EXCLUDERI, peste TOTI candidatii exclusi din critic ---------------------")
    L.append("EXCLUSIONS_TOTAL=%d   (= RAW_NON_CRITICAL_COMPOSITES + RAW_FALSE_POSITIVES)"
             % n["EXCLUSIONS_TOTAL"])
    L.append("UNEXPLAINED_EXCLUSIONS=%d" % n["UNEXPLAINED_EXCLUSIONS"])
    L.append("  (derivat peste TOATE cele %d, nu doar peste cele %d randuri individuale)"
             % (n["EXCLUSIONS_TOTAL"], len(CL.CLASIFICARE)))
    L.append("")
    L.append("--- PROPRIETATEA TRANZACTIEI -----------------------------------------------")
    L.append("TRANSACTION_OWNERSHIP_GAPS=%d   (cai cu scrieri in >1 tranzactie, ramase fara "
             "verdict scris)" % len(gaps))
    L.append("PARTIAL_COMMIT_PATHS=%d   (cai cu commit partial, ramase fara verdict scris)"
             % len(partiale))
    L.append("")
    L.append("P4_CRITICAL_OPERATION_INVENTORY=%s"
             % ("MECHANICALLY_DERIVED · COMPLETE"
                if n["UNCLASSIFIED_RAW_CANDIDATES"] == 0
                and n["RAW_CLASS_ACCOUNTING"] == "PASS" else "INCOMPLETE"))
    L.append("P4_FAULT_INJECTION_COVERAGE=%s"
             % ("COMPLETE" if n["UNTESTED_CRITICAL_OPERATIONS"] == 0 else "INCOMPLETE"))
    L.append("")
    L.append("puncte de intrare parcurse=%d" % stat["intrari"])
    L.append("cai trunchiate de adancime=%d" % stat["trunchiate"])
    return "\n".join(L)

if __name__ == "__main__":
    if not ST.calibreaza(verbose=True):
        sys.exit(2)
    print()
    inv, stat = ST.inventar()
    _scrie("inventar_brut.txt", ST.raport_text(inv, stat))
    _scrie("inventar_brut.json",
           json.dumps({"stat": stat, "candidati": inv}, ensure_ascii=False, indent=2))
    _scrie("clasificare.txt", clasificare_text(inv))
    _scrie("efecte_ireversibile.txt", efecte_text(inv))
    _scrie("acceptare.txt", acceptare(inv, stat))
    print()
    print(acceptare(inv, stat))
