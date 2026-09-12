# -*- coding: utf-8 -*-
"""P7 — clasificarea, cu REGULA lângă fiecare item. Diagnostic; nu repară nimic.

`scripts/scan_p7_straturi.py` produce itemii; aici fiecare primește exact o clasă, printr-o regulă
scrisă. 265 de itemi nu se pot clasifica unul câte unul din memorie — dar nici nu se pot lăsa
neclasificați, fiindcă atunci cifra ar fi o impresie. Deci clasificarea e pe REGULI, iar regulile
citează textul canonic.

TEXTUL CANONIC: `PLAN_HARDENING.md:733-755`. Cele trei verificări mecanice, verbatim (l. 749-751):
*„un motor fiscal nu importă `db`; un use-case nu construiește `HTTPException`; ruta nu conține
SQL."*

CE NU FACE FIȘIERUL ĂSTA: nu propune reparații, nu mută nimic, nu atinge producția. P7 e DESCHIS ca
diagnostic, nu ca implementare.
"""
import collections
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_p7_straturi as S  # noqa: E402

AR = "ACTION_REQUIRED"
ABD = "ACCEPTABLE_BY_DESIGN"
FP = "FALSE_POSITIVE"
EL = "EVIDENCE_LIMITATION"

Regula = collections.namedtuple("Regula", "clasa temei de_ce")

#: ─────────────────────────────────────────────────────────────────────────────
#: REGULILE. Fiecare are temeiul în textul canonic, cu linia.
REGULI = {
    "D1_SQL_IN_RUTA": Regula(
        AR, "PLAN_HARDENING.md:751 — «ruta nu conține SQL»",
        "Textul canonic nu lasă nicio excepție, iar eu nu inventez una: fiecare instrucțiune SQL "
        "executată în corpul unei rute e o poziție de mutat sub stratul repository. Nu e un defect "
        "de comportament — aplicația funcționează —, e chiar datoria pe care o numește P7."),

    "D1_NECUNOSCUT": Regula(
        FP, "definiția detectorului: item = `.execute` pe un CURSOR",
        "`.execute` există și pe alte obiecte. Un apel pe un nume care NU e legat de `.cursor()` în "
        "corpul rutei nu e SQL, deci nu intră în măsurătoare. Se numără separat ca să se vadă că "
        "discriminatorul a fost folosit, nu sărit."),

    "D2_MOTOR_FISCAL_CU_DB": Regula(
        AR, "PLAN_HARDENING.md:749 — «un motor fiscal nu importă `db`»",
        "Un motor care își deschide singur conexiunea nu mai poate fi chemat din afara unei "
        "tranzacții deținute de use-case (P4) și nu mai e pur."),

    "D3_HTTP_SUB_HTTP_IN_MODUL_DE_RUTE": Regula(
        ABD, "PLAN_HARDENING.md:743 — «HTTP — validare de formă, AUTENTIFICARE, traducerea "
             "erorilor în coduri»",
        "Itemul stă într-un modul care CONȚINE rute, deci e chiar stratul HTTP, iar ce face e "
        "autentificare/autorizare tradusă în cod HTTP — exact sarcina stratului. Că funcția e "
        "lexical în afara corpului rutei nu-i schimbă stratul. *Regula nu se extinde la module "
        "fără rute: acolo același apel ar fi ACTION_REQUIRED.*"),

    "D4_STRAT_MIXT": Regula(
        AR, "PLAN_HARDENING.md:742-746 — cele patru straturi, fiecare cu sarcina lui",
        "Modulul face azi două lucruri deodată (are un al doilea strat declarat în `mixt_cu`). "
        "Comanda V3 o cere limpede: nu se inventează o clasificare, se numește amestecul și se "
        "trece ca poziție de lucru pentru valul care separă. Nu se repară aici."),
}


def _excluse():
    """{regulă: [fișiere]} — ce NU intră în niciun univers, cu motivul. Fără excluderi tăcute."""
    out = collections.defaultdict(list)
    baza = os.path.join(RAD, "core")
    for f in sorted(os.listdir(baza)):
        if not f.endswith(".py"):
            continue
        if f.startswith("test_"):
            out["probe, nu cod care serveste cereri"].append("core/" + f)
        elif f.startswith("scan_"):
            out["instrumente de masura, nu strat de aplicatie"].append("core/" + f)
    scripts = os.path.join(RAD, "scripts")
    for f in sorted(os.listdir(scripts)):
        if f.endswith(".py"):
            out["unelte de lucru; nu sunt pe calea unei cereri"].append("scripts/" + f)
    return out


def itemi():
    """[(item, cheie_regula)] — fiecare item al fiecărui detector, cu regula lui."""
    inv = S.inventar()
    out = []
    for it in inv["D1"]:
        out.append((it, "D1_SQL_IN_RUTA"))
    for it in inv["D1_necunoscute"]:
        out.append((it, "D1_NECUNOSCUT"))
    for it in inv["D2"]:
        out.append((it, "D2_MOTOR_FISCAL_CU_DB"))
    for it in inv["D3"]:
        # modulul conține rute? atunci e stratul HTTP, oriunde ar sta fișierul
        are_rute = bool(S.rute([it.fisier]))
        out.append((it, "D3_HTTP_SUB_HTTP_IN_MODUL_DE_RUTE" if are_rute
                    else "D3_HTTP_SUB_HTTP"))
    for it in inv["D4"]:
        out.append((it, "D4_STRAT_MIXT"))
    return out


def numaratori():
    lista = itemi()
    pe_clasa = collections.Counter(REGULI[cheie].clasa for _it, cheie in lista)
    excluse = _excluse()
    inv = S.inventar()
    return {
        "P7_SCANNED_ITEMS": len(S.fisiere_de_aplicatie()),
        "P7_EXCLUDED_ITEMS": sum(len(v) for v in excluse.values()),
        "P7_RAW_ITEMS": len(lista),
        "P7_CLASSIFIED_ITEMS": sum(pe_clasa.values()),
        "P7_ACTION_REQUIRED": pe_clasa.get(AR, 0),
        "P7_ACCEPTABLE_BY_DESIGN": pe_clasa.get(ABD, 0),
        "P7_FALSE_POSITIVES": pe_clasa.get(FP, 0),
        "P7_EVIDENCE_LIMITATIONS": pe_clasa.get(EL, 0),
        "P7_UNCLASSIFIED_ITEMS": len([1 for _it, cheie in lista if cheie not in REGULI]),
        "P7_UNEXPLAINED_EXCLUSIONS": len([1 for regula in excluse if not regula]),
        "universuri": {"rute": inv["rute"], "module_core": inv["module_core"],
                       "module_fiscale": len(S.module_fiscale()[0]),
                       "registru": len(S.univers_registru())},
        "pe_detector": {
            "D1": len(inv["D1"]) + len(inv["D1_necunoscute"]),
            "D2": len(inv["D2"]),
            "D3": len(inv["D3"]),
            "D4": len(inv["D4"]),
        },
    }


def main():
    n = numaratori()
    lista = itemi()
    print("CONTABILITATE P7 — DIAGNOSTIC")
    for k in ("P7_SCANNED_ITEMS", "P7_EXCLUDED_ITEMS", "P7_RAW_ITEMS", "P7_CLASSIFIED_ITEMS",
              "P7_ACTION_REQUIRED", "P7_ACCEPTABLE_BY_DESIGN", "P7_FALSE_POSITIVES",
              "P7_EVIDENCE_LIMITATIONS", "P7_UNCLASSIFIED_ITEMS", "P7_UNEXPLAINED_EXCLUSIONS"):
        print("  %-28s %d" % (k, n[k]))
    print()
    print("  universuri : %s" % n["universuri"])
    print("  pe detector: %s" % n["pe_detector"])
    assert n["P7_CLASSIFIED_ITEMS"] == n["P7_RAW_ITEMS"], "contabilitatea nu se inchide"
    assert n["P7_UNCLASSIFIED_ITEMS"] == 0
    print()
    pe_regula = collections.Counter(cheie for _it, cheie in lista)
    for cheie, cate in pe_regula.most_common():
        print("  [%s] %-36s %d" % (REGULI[cheie].clasa, cheie, cate))
    if "--itemi" in sys.argv:
        print()
        for it, cheie in lista:
            print("  %-14s %-22s %s:%s  %s  <- %s"
                  % (REGULI[cheie].clasa, it.detector, it.fisier, it.linie, it.simbol, it.cale))
    return 0


if __name__ == "__main__":
    sys.exit(main())
