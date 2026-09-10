# -*- coding: utf-8 -*-
"""scripts/artefacte_p5.py — scrie artefactele fazei de diagnostic, toate din aceeași scanare.

**De ce un singur generator.** Dacă inventarul, clasificarea și lanțurile de apel s-ar produce prin
rulări separate, ele ar putea descrie stări diferite ale codului fără ca nimic să prindă asta.
Aici se scanează O DATĂ și se scriu toate, deci contabilitatea dintre ele e adevărată prin
construcție, nu prin noroc.

Scrie în `masuratori/p5/`:
  * `P5_INVENTAR_BRUT.{txt,json}`        — cei %d candidați bruți, cu primitive și lanțuri
  * `P5_CLASIFICARE.{txt,json}`          — verdict, regulă, motiv, dovadă, val, per candidat
  * `P5_CALLCHAINS.{txt,json}`           — lanțul de apel până la fiecare primitivă blocantă
  * `P5_DETECTOR_CALIBRATION.{txt,json}` — proba cu proba, pozitiv și negativ
"""
import io
import json
import os
import sys
import textwrap

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import scan_blocante as SB  # noqa: E402
from core import p5_clasificare as P  # noqa: E402

IES = os.path.join(RAD, "masuratori", "p5")
_RAD_G = RAD


def _scrie(nume, text=None, date=None):
    if not os.path.isdir(IES):
        os.makedirs(IES)
    if text is not None:
        with io.open(os.path.join(IES, nume + ".txt"), "w", encoding="utf-8", newline="") as f:
            f.write(text)
    if date is not None:
        with io.open(os.path.join(IES, nume + ".json"), "w", encoding="utf-8", newline="") as f:
            json.dump(date, f, ensure_ascii=False, indent=1, sort_keys=True)
    print("  scris: %s" % nume)


def clasificare(cand):
    randuri, date = [], []
    for x in cand:
        v = P.verdict(x)
        date.append({"id": x["id"], "intrare": x["intrare"], "fisier": x["fisier"],
                     "fel": x["fel"], "async": x["async"], "detectori": sorted(x["detectori"]),
                     "clasa": v["clasa"], "regula": v["regula"], "dovada": v["dovada"],
                     "val": v.get("val"), "de_ce": v["de_ce"]})
    date.sort(key=lambda d: ({P.ACTIUNE: 0, P.ACCEPTABIL: 1, P.FALS: 2}[d["clasa"]],
                             d.get("val") or 9, d["intrare"]))
    n = P.numaratori(cand)
    randuri.append("P5 — CLASIFICAREA CANDIDAȚILOR BRUȚI")
    randuri.append("=" * 100)
    randuri.append("")
    randuri.append("RAW_CANDIDATES ........... %d" % n["RAW_CANDIDATES"])
    randuri.append("CLASSIFIED_CANDIDATES .... %d" % n["CLASSIFIED_CANDIDATES"])
    randuri.append("UNCLASSIFIED_RAW ......... %d" % n["UNCLASSIFIED_RAW_CANDIDATES"])
    randuri.append("ACTION_REQUIRED .......... %d" % n["ACTION_REQUIRED"])
    randuri.append("ACCEPTABLE_BY_DESIGN ..... %d" % n["ACCEPTABLE_BY_DESIGN"])
    randuri.append("FALSE_POSITIVE ........... %d" % n["FALSE_POSITIVES"])
    randuri.append("RAW_CLASS_ACCOUNTING ..... %s (%d+%d+%d = %d = %d)" % (
        n["RAW_CLASS_ACCOUNTING"], n["ACTION_REQUIRED"], n["ACCEPTABLE_BY_DESIGN"],
        n["FALSE_POSITIVES"], n["RAW_CLASS_SUM"], n["RAW_CANDIDATES"]))
    randuri.append("EXCLUSIONS_TOTAL ......... %d" % n["EXCLUSIONS_TOTAL"])
    randuri.append("UNEXPLAINED_EXCLUSIONS ... %d" % n["UNEXPLAINED_EXCLUSIONS"])
    randuri.append("")
    randuri.append("pe regulă:  " + " · ".join("%s=%d" % kv for kv in sorted(n["pe_regula"].items())))
    randuri.append("pe dovadă:  " + " · ".join("%s=%d" % kv for kv in sorted(n["pe_dovada"].items())))
    randuri.append("pe val:     " + " · ".join("val %s=%d" % kv for kv in sorted(n["valuri"].items())))
    randuri.append("")
    clasa_curenta = None
    for d in date:
        if d["clasa"] != clasa_curenta:
            clasa_curenta = d["clasa"]
            randuri.append("")
            randuri.append("=" * 100)
            randuri.append(clasa_curenta)
            randuri.append("=" * 100)
        randuri.append("")
        randuri.append("%s  %s" % (d["id"], d["intrare"]))
        randuri.append("    fișier ..... %s   (%s%s)" % (
            d["fisier"], d["fel"], ", async" if d["async"] else ""))
        randuri.append("    detectori .. %s" % ", ".join(d["detectori"]))
        randuri.append("    regula ..... %s" % d["regula"])
        randuri.append("    dovada ..... %s%s" % (
            d["dovada"], "   val %s" % d["val"] if d.get("val") else ""))
        for i, linie in enumerate(textwrap.wrap(d["de_ce"], 92)):
            randuri.append("    %s %s" % ("de ce ......" if i == 0 else "            ", linie))
    return "\n".join(randuri) + "\n", {"numaratori": n, "randuri": date}


def callchains(cand):
    randuri, date = [], []
    for x in cand:
        v = P.verdict(x)
        lant = [{"fel": p["fel"], "detaliu": p["detaliu"], "loc": p["loc"], "via": p["via"],
                 "pe_bucla": p["pe_bucla"], "in_domeniu_db": p["in_domeniu_db"],
                 "omonim": p["omonim"]} for p in x["primitive"]]
        date.append({"id": x["id"], "intrare": x["intrare"], "clasa": v["clasa"], "lant": lant})
        randuri.append("")
        randuri.append("%s  %s   [%s]" % (x["id"], x["intrare"], v["clasa"]))
        randuri.append("-" * 100)
        for p in lant:
            steaguri = "".join(["B" if p["pe_bucla"] else ".",
                                "D" if p["in_domeniu_db"] else ".",
                                "O" if p["omonim"] else "."])
            randuri.append("  [%s] %-28s %s" % (steaguri, p["detaliu"], p["loc"]))
            randuri.append("        %s" % p["via"])
    antet = [
        "P5 — LANȚURILE DE APEL până la fiecare primitivă blocantă",
        "=" * 100,
        "",
        "Steaguri:  B = se execută PE BUCLA de evenimente",
        "           D = se execută cât timp e ținută o conexiune din pool",
        "           O = numele a fost rezolvat pe treapta a treia (toate omonimele) — oarbire",
        "",
        "Sub fiecare primitivă e scris DRUMUL, de la punctul de intrare până la ea. O primitivă",
        "fără drum n-ar fi o dovadă, ar fi o afirmație.",
    ]
    return "\n".join(antet + randuri) + "\n", {"lanturi": date}


def calibrare():
    probe = SB.probe_calibrare()
    picate = [n for n, ok in probe if not ok]
    randuri = ["P5 — CALIBRAREA DETECTORILOR",
               "=" * 100, "",
               "DETECTOR_CALIBRATION_GAPS = %d" % len(picate),
               "probe totale ............. %d" % len(probe),
               "detectori ................ %d" % len(SB.DETECTORI),
               "controale negative ....... %d" % len(SB.CONTROALE_NEGATIVE), "",
               "Fiecare detector are un caz sintetic care aprinde NUMAI pe el (sau, unde asta e",
               "matematic imposibil, mulțimea minimă — pinată, cu implicația scrisă). Controalele",
               "negative sunt căi curate: dacă vreunul se aprinde, detectorul minte.", "",
               "DETECTORI:"]
    for cod in sorted(SB.DETECTORI):
        ruta, astept = SB.CALIBRARE[cod]
        implicatie = "" if astept == {cod} else "   (mulțime minimă: %s aprinde și %s)" % (
            cod, ", ".join(sorted(astept - {cod})))
        randuri.append("  %-4s %s" % (cod, SB.DETECTORI[cod]))
        randuri.append("       caz: %-26s aștept %s%s" % (ruta, sorted(astept), implicatie))
    randuri += ["", "PROBE:"]
    for nume, ok in probe:
        randuri.append("  %-70s %s" % (nume[:70], "OK" if ok else "PICAT"))
    return "\n".join(randuri) + "\n", {
        "DETECTOR_CALIBRATION_GAPS": len(picate), "probe_total": len(probe),
        "picate": picate, "detectori": SB.DETECTORI,
        "calibrare": {k: {"caz": v[0], "astept": sorted(v[1])} for k, v in SB.CALIBRARE.items()},
        "controale_negative": list(SB.CONTROALE_NEGATIVE),
        "probe": [{"nume": n, "ok": ok} for n, ok in probe]}


def acceptare(cand, stat):
    """Blocul de cifre cerut de comanda fazei — DERIVAT, ca raportul să-l poată cita, nu rescrie."""
    n = P.numaratori(cand)
    cal = calibrare()[1]
    m = P.masuratori(reincarca=True)
    import json as _json
    cale_m = os.path.join(IES, "P5_MASURATORI.json")
    d = _json.load(io.open(cale_m, encoding="utf-8")) if os.path.exists(cale_m) else {}
    conc = {r["k"]: r for r in d.get("concurenta", [])}
    L = ["BLOCUL DE ACCEPTARE P5 — DIAGNOSTIC", "=" * 78, "",
         "--- INVENTAR ---",
         "ENTRY_POINTS_SCANNED=%d" % stat["intrari"],
         "  (rute async %d · rute sync %d · middleware %d · restul: lucrători și pornire)"
         % (stat["rute_async"], stat["rute_sync"], stat["middleware"]),
         "DETECTORS=%d" % len(SB.DETECTORI),
         "RAW_CANDIDATES=%d" % n["RAW_CANDIDATES"],
         "TRUNCATED_EXPANSIONS=%d   (adâncime %d)" % (stat["trunchiate"], stat["adancime"]),
         "",
         "--- CALIBRARE ---",
         "DETECTOR_CALIBRATION_PROBES=%d" % cal["probe_total"],
         "DETECTOR_CALIBRATION_GAPS=%d" % cal["DETECTOR_CALIBRATION_GAPS"],
         "NEGATIVE_CONTROLS=%d" % len(SB.CONTROALE_NEGATIVE),
         "",
         "--- CLASIFICARE ---",
         "CLASSIFIED_CANDIDATES=%d" % n["CLASSIFIED_CANDIDATES"],
         "UNCLASSIFIED_RAW_CANDIDATES=%d" % n["UNCLASSIFIED_RAW_CANDIDATES"],
         "ACTION_REQUIRED=%d" % n["ACTION_REQUIRED"],
         "ACCEPTABLE_BY_DESIGN=%d" % n["ACCEPTABLE_BY_DESIGN"],
         "FALSE_POSITIVES=%d" % n["FALSE_POSITIVES"],
         "RAW_CLASS_SUM=%d" % n["RAW_CLASS_SUM"],
         "RAW_CLASS_ACCOUNTING=%s" % n["RAW_CLASS_ACCOUNTING"],
         "EXCLUSIONS_TOTAL=%d   (populația: toți candidații care NU cer acțiune)"
         % n["EXCLUSIONS_TOTAL"],
         "UNEXPLAINED_EXCLUSIONS=%d" % n["UNEXPLAINED_EXCLUSIONS"],
         "",
         "  valuri de remediere (propuse, NEEXECUTATE): " +
         " · ".join("val %s = %d căi" % kv for kv in sorted(n["valuri"].items())),
         "",
         "--- MASURATORI ---",
         "MEASUREMENT_COMMIT=%s" % (d.get("commit") or "?"),
         "BASELINE_CANARY_P95_MS=%s" % m.get("canar_baza_p95"),
         "N_SERIES=%s" % ",".join(str(r["N"]) for r in d.get("curba_async", [])),
         "PEAK_N=%s" % m.get("N_varf"),
         "PEAK_ROUTE_P50_MS=%s" % m.get("ruta_varf_p50"),
         "PEAK_CANARY_P95_MS=%s" % m.get("canar_varf_p95"),
         "PEAK_CANARY_MAX_MS=%s" % m.get("canar_varf_max"),
         "SYNC_CONTROL_CANARY_P95_MS=%s   (rută sincronă de cost comparabil, toate 200)"
         % m.get("canar_sync_p95"),
         "UNEXPECTED_STATUSES=%s" % ("0" if d.get("statusuri_neasteptate") == {} else "DA"),
         "SERVER_LOG_TRACEBACKS=%s" % d.get("jurnal_server", {}).get("URME_EXCEPTIE"),
         "RAW_EVIDENCE_SERIES=%s   (%s valori)" % (
             d.get("esantioane_brute", {}).get("serii"),
             d.get("esantioane_brute", {}).get("valori")),
         ""]
    L.append("--- CONCURENTA ---")
    for k in sorted(conc):
        r = conc[k]
        L.append("k=%-3d THROUGHPUT=%s req/s · P50=%s ms · P95=%s ms · P99=%s ms · "
                 "MAX_SIMULTANEOUS_RESOURCE_USE=%s · RESOURCE_CAPACITY=%s · ERRORS=%s · "
                 "TIMEOUTS=%s · DEADLOCKS=%s"
                 % (k, r["debit_cereri_pe_sec"], r["p50_ms"], r["p95_ms"], r["p99_ms"],
                    r["MAX_SIMULTANEOUS_RESOURCE_USE"], r["RESOURCE_CAPACITY"],
                    r["ERRORS"], r["TIMEOUTS"], r["DEADLOCKS"]))
    L += ["",
          "--- SIGURANTA SONDEI ---",
          "PRODUCTION_DATA_AFFECTED=%s" % d.get("amprenta", {}).get("PRODUCTION_DATA_AFFECTED"),
          "FINGERPRINTED_TABLES=%d" % len(d.get("amprenta", {}).get("tabele", [])),
          "FINGERPRINT_DIFFS=%d" % len(d.get("amprenta", {}).get("difera", {})),
          "AUDIT_ROWS_CLEANED=%s" % d.get("curatenie", {}).get("randuri_audit_sterse"),
          "",
          "--- CONTRACTUL FAZEI ---"]
    L += contractul_fazei()
    L.append("")
    return "\n".join(L) + "\n"


#: commitul de la care pleacă faza — pinat, ca diferența să aibă un capăt fix
BASELINE_COMMIT = "8ce4cd84b07f411f458a35cc9b9ff9e9990fbcd1"

#: ce e „cod de producție": ce ajunge în procesul care servește cereri
NU_E_PRODUCTIE = ("core/test_", "core/p5_", "scripts/", "masuratori/", "core/conftest",
                  "RAPORT_", "PLAN_", "METODA_", "TESTE.md", "AGENDA")


def _e_productie(cale):
    if any(cale.startswith(p) or ("/" + p) in cale for p in NU_E_PRODUCTIE):
        return False
    return cale.endswith((".py", ".js", ".html", ".css", ".sql"))


def contractul_fazei(baza=None):
    """`PRODUCTION_CODE_CHANGED` etc. — DERIVATE din git, nu declarate.

    Forma dinainte le scria de mână. Un câmp care spune «n-am schimbat nimic» și pe care îl scriu
    tot eu nu e o măsurătoare, e o promisiune — exact felul de rând pe care runda de acceptare îl
    cere derivat. Acum se citește diferența față de commitul de bază și se numesc fișierele.
    """
    import subprocess
    baza = baza or BASELINE_COMMIT
    r = subprocess.run(["git", "-C", _RAD_G, "diff", "--name-status", "%s..HEAD" % baza],
                       capture_output=True, text=True)
    r2 = subprocess.run(["git", "-C", _RAD_G, "status", "--porcelain"],
                        capture_output=True, text=True)
    atinse = []
    for linie in (r.stdout or "").splitlines():
        parti = linie.split("\t")
        if len(parti) >= 2:
            atinse.append((parti[0], parti[-1]))
    for linie in (r2.stdout or "").splitlines():
        st, _, cale = linie.partition(" ")
        cale = cale.strip().strip('"')
        if cale:
            atinse.append((st.strip() or "??", cale))
    prod = sorted({c for st, c in atinse if _e_productie(c) and not st.startswith("??")})
    noi = sorted({c for st, c in atinse if st.startswith("??")})
    out = ["BASELINE_COMMIT=%s" % baza,
           "PRODUCTION_CODE_CHANGED=%s" % ("NO" if not prod else "DA"),
           "REQUEST_PATH_CHANGED=%s" % ("NO" if not prod else "DA"),
           "RUNTIME_BEHAVIOR_CHANGED=%s" % ("NO" if not prod else "DA"),
           "P5_IMPLEMENTATION_STARTED=NO",
           "  fișiere de producție atinse față de baseline: %s"
           % (", ".join(prod) if prod else "niciunul")]
    if noi:
        out.append("  fișiere noi, netracked: %s" % ", ".join(noi[:12]))
    return out


def main():
    print("scanez...")
    cand, stat = SB.inventar(rad=RAD)
    print("  %d puncte de intrare, %d candidați" % (stat["intrari"], stat["candidati"]))
    t, d = SB.raport_text(cand, stat), {"stat": stat, "candidati": cand}
    _scrie("P5_INVENTAR_BRUT", t, d)
    _scrie("P5_CLASIFICARE", *clasificare(cand))
    _scrie("P5_CALLCHAINS", *callchains(cand))
    _scrie("P5_DETECTOR_CALIBRATION", *calibrare())
    _scrie("acceptare", acceptare(cand, stat))
    n = P.numaratori(cand)
    print("\nCONTABILITATE: %d + %d + %d = %d   (brut %d)   %s" % (
        n["ACTION_REQUIRED"], n["ACCEPTABLE_BY_DESIGN"], n["FALSE_POSITIVES"],
        n["RAW_CLASS_SUM"], n["RAW_CANDIDATES"], n["RAW_CLASS_ACCOUNTING"]))
    return 0 if n["RAW_CLASS_ACCOUNTING"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
