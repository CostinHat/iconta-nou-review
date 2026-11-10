# -*- coding: utf-8 -*-
"""scripts/asteapta_poarta.py — așteptarea porții (17.5-U, U.3), chemat de scripts/asteapta_poarta.sh. Citește numai jurnalul lotului, poarta_verdicte.log și
lot_stare_<lot_fisier>.json (nu pornește și nu caută procese după linia de comandă: fără pgrep, fără ps) și iese când jurnalul arată rezultatul.

Uz:
  asteapta_poarta.sh <lot> [secunde_max] [--dupa=<ISO cu fus orar>]
  secunde_max: întreg între 1 și 540 (implicit 540); pasul buclei e de 10 s. --dupa = ora lansării porții (date --iso-8601=seconds): rândurile mai vechi se ignoră.
  Ieșiri (stdout: o linie «poarta <lot>: <rezultat> <sha>», la 2 și 7 gol): 0 verde, 1 rosu, 2 apel invalid, 3 oprit, 4 infra, 5 intrerupt, 6 nepornita,
  7 eroare de unealtă, 9 in_curs (nu e rezultat: reiei așteptarea)."""
import datetime
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import argumente_script  # noqa: E402
import jurnal_lot as JL  # noqa: E402
import lacat_test  # noqa: E402
import poarta_lib as L  # noqa: E402

PAS_S = 10
PLAFON_S = 540
FAZE = ("poarta_verificator", "poarta_pytest", "poarta_plasa")
NUME = {0: "verde", 1: "rosu", 3: "oprit", 4: "infra", 5: "intrerupt", 6: "nepornita", 9: "in_curs"}


def _marja(nume, implicit):
    try:
        return float(os.environ.get(nume, implicit))
    except ValueError:
        return float(implicit)


def _ora(text):
    """ISO -> datetime cu fus; fără fus orar se citește ca oră locală."""
    d = datetime.datetime.fromisoformat(text)
    return d if d.tzinfo else d.astimezone()


def _start_proces(pid):
    """Momentul de start al procesului (epoch, s) din /proc, sau None."""
    tacte = lacat_test.ora_start(pid)
    if tacte is None:
        return None
    btime = next(int(ln.split()[1]) for ln in open("/proc/stat", encoding="utf-8") if ln.startswith("btime "))
    return btime + int(tacte) / os.sysconf("SC_CLK_TCK")


def _vie(pid, inceput):
    """kill -0 reușește și procesul a pornit cel mult MARJA_PID_S după rândul «inceput» (un pid refolosit mai târziu e mort)."""
    try:
        os.kill(int(pid), 0)
    except PermissionError:
        pass
    except (OSError, ValueError):
        return False
    start = _start_proces(pid)
    return start is not None and start <= inceput.timestamp() + _marja("MARJA_PID_S", 2)


def faze(rows, lot, d):
    """Fazele poarta_* ale lotului cu «inceput» la ora ≥ d: [{faza, inceput (datetime), sha, sfarsit (datetime|None), rezultat, pid}], în ordinea începuturilor."""
    rl = [r for r in rows if len(r) > 6 and r[0] == lot and r[1] in FAZE]
    sf = {r[6]: r for r in rl if r[2] == "sfarsit"}
    iesire = []
    for r in rl:
        if r[2] != "inceput" or _ora(r[3]) < d:
            continue
        s = sf.get(r[6])
        iesire.append({"faza": r[1], "inceput": _ora(r[3]), "sha": r[4], "sfarsit": _ora(s[3]) if s else None, "rezultat": s[5] if s else None,
                       "pid": r[7] if len(r) > 7 else ""})
    return iesire


def verdicte(cale, lot, d):
    """Rândurile VERDE / ROSU / INFRA ale lotului (jeton lot=<lot> întreg, pe orice poziție) cu data (câmpul 4) ≥ d, în ordinea din fișier: [(tip, sha, data)]."""
    try:
        linii = open(cale, encoding="utf-8").read().splitlines()
    except OSError:
        return []
    iesire = []
    for ln in linii:
        p = ln.split()
        if len(p) >= 5 and p[0] in ("VERDE", "ROSU", "INFRA") and ("lot=" + lot) in p[4:]:
            data = _ora(p[3])
            if data >= d:
                iesire.append((p[0], p[1], data))
    return iesire


def decide(rows, lot, ver, stare, d, acum, head):
    """PURĂ (procedura U.3.c, primul caz potrivit câștigă). -> (cod, sha, motiv); cod None = continuă (la expirare: 9 sau 6, după `asteapta`)."""
    marja = _marja("MARJA_RELANSARE_S", 120)
    v = ver[-1] if ver else None
    r = v[2] if v else d
    toate = faze(rows, lot, d)
    n = [f for f in toate if (f["inceput"] > v[2] if v else f["inceput"] >= r)]
    sha_n = n[-1]["sha"] if n else "-"
    sha_v = v[1] if v else sha_n
    infra = stare.get("infra") or []
    if stare.get("oprit") or len(infra) >= 3:
        return 3, sha_v, stare.get("oprit") or "infra ×3"
    if any(f["sfarsit"] is None and f["rezultat"] is None and _vie(f["pid"], f["inceput"]) for f in n):
        return None, head, "in_curs"
    moarta = [f for f in n if f["rezultat"] == "intrerupt" or (f["sfarsit"] is None and not _vie(f["pid"], f["inceput"]))]
    if moarta:
        return 5, head, "faza %s moartă" % moarta[0]["faza"]
    if n:
        vechime = (acum - max(f["sfarsit"] for f in n)).total_seconds()
        if vechime >= marja:
            return 5, head, "poartă încheiată fără verdict"
        return None, head, "in_curs"
    if v:
        if v[0] == "VERDE":
            return 0, sha_v, ""
        if v[0] == "ROSU":
            return 1, sha_v, ""
        if len(infra) < 3 and (acum - v[2]).total_seconds() >= marja:
            return 4, sha_v, "relansarea n-a urmat"
        return None, head, "in_curs"
    return None, head, "nepornita"


def _stare(lot):
    comun = JL.comun()
    cale = os.path.join(comun, "lot_stare_%s.json" % L.lot_fisier(lot))
    return json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}, os.path.join(comun, "poarta_verdicte.log")


def _head():
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "-"


def _argumente(argv):
    a = argumente_script.citeste(argv, __doc__, cu_valoare=("--dupa=",), pozitionale=2, prefix="[asteapta_poarta]")

    def uz(motiv):
        print("[asteapta_poarta] %s — nimic nu pornește.\n%s" % (motiv, __doc__[__doc__.index("Uz:"):].rstrip()), file=sys.stderr)
        sys.exit(2)

    poz = [x for x in a if not x.startswith("-")]
    dupa = [x.split("=", 1)[1] for x in a if x.startswith("--dupa=")]
    if not poz:
        uz("lipsește lotul")
    secunde = PLAFON_S
    if len(poz) > 1:
        if not poz[1].isdigit() or not 1 <= int(poz[1]) <= PLAFON_S:
            uz("secunde_max trebuie să fie un întreg între 1 și %d (primit: %s)" % (PLAFON_S, poz[1]))
        secunde = int(poz[1])
    d = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)
    if dupa:
        try:
            d = datetime.datetime.fromisoformat(dupa[0])
        except ValueError:
            uz("--dupa nu e o oră ISO: %s" % dupa[0])
        if d.tzinfo is None:
            uz("--dupa fără fus orar: %s" % dupa[0])
    return poz[0], secunde, d


def main(argv):
    try:
        lot, secunde, d = _argumente(argv)
        t0 = time.time()
        while True:
            rows = JL.citeste_jurnal()
            stare, jv = _stare(lot)
            cod, sha, motiv = decide(rows, lot, verdicte(jv, lot, d), stare, d, datetime.datetime.now().astimezone(), _head())
            if cod is None and time.time() - t0 >= secunde:
                cod = 6 if motiv == "nepornita" else 9
                sha = sha if cod == 6 else _head()
                if cod == 6:
                    ver = verdicte(jv, lot, d)
                    sha = ver[-1][1] if ver else (faze(rows, lot, d) or [{"sha": "-"}])[-1]["sha"]
            if cod is not None:
                print("poarta %s: %s %s" % (lot, NUME[cod], sha))
                if motiv:
                    print("[asteapta_poarta] %s" % motiv, file=sys.stderr)
                return cod
            time.sleep(max(0, min(PAS_S, secunde - (time.time() - t0))))
    except Exception as e:  # noqa: BLE001  — SystemExit (argumentele, ieșirea 2) trece neprins
        print("[asteapta_poarta] eroare de unealtă: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 7


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
