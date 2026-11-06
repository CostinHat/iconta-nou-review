# -*- coding: utf-8 -*-
"""scripts/matrice_16_7.py — matricea pe tot registrul (comanda 16.7, pct.5): fiecare intrare din core/catalog_ecrane.json, deschisă la 1920 × 1080 și la 1366 × 768 prin
scripts/verificator_design.py `ecran`, cu rândurile a și b judecate de măsurătorile noi. Scrie docs/dovezi/16_7/matrice_inainte.csv (antet `ecran,rand a,rand b,motiv`, un rând pe
intrare, în ordinea registrului), măsurătorile JSON în docs/dovezi/16_7/matrice_inainte/ și capturile PNG în ~/matrice_16_7_capturi/ (în afara depozitului).
Rând: NEDESCHIS (oricare rezoluție nu s-a deschis) > ROSU (PICĂ la cel puțin una) > VERDE. Lista ROȘIE a matricei = lista lotului de produs 16.8.
Regulile comune cu calibrarea (lacătul, 8019, restaurările) sunt în scripts/calibreaza_16_7.py (`ruleaza_pe_server`)."""
import csv
import json
import os
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_7")
JSON_DIR = os.path.join(DOVEZI, "matrice_inainte")
CSV = os.path.join(DOVEZI, "matrice_inainte.csv")
PNG_DIR = os.path.expanduser("~/matrice_16_7_capturi")
REZOLUTII = ("1920x1080", "1366x768")
TIMEOUT = 240
FEREASTRA_MICA = "Fereastră mică — confirmare storno F1"
MOTIVE_X = ("lipsește „✕”", "butoane „✕”", "„✕” nu e de 40 × 40", "„✕” nu e în dreapta sus")
STARE_TIMEOUT = "timeout"
NEDESCHIS_FARA_FEREASTRA = "nicio fereastră de lucru deschisă"


def e_motiv_x(m):
    """Un motiv „✕” al rândului a: începe cu «lipsește „✕”», «<n> butoane „✕”», «„✕” nu e de 40 × 40» sau «„✕” nu e în dreapta sus»."""
    cuvinte = m.split(" ", 1)
    return m.startswith(("lipsește „✕”", "„✕” nu e de 40 × 40", "„✕” nu e în dreapta sus")) or (len(cuvinte) == 2 and cuvinte[0].isdigit() and cuvinte[1].startswith("butoane „✕”"))


def evalueaza(js, litera, nume=""):
    """-> (stare, motive) pentru rândul `litera` la o rezoluție. `js` = dicționarul măsurătorilor | None (JSON lipsă) | STARE_TIMEOUT.
    Stări: NEDESCHIS (cu motivul cauzei), ROSU (motivele rândului), VERDE."""
    if js is None:
        return "NEDESCHIS", ["JSON lipsă"]
    if js == STARE_TIMEOUT:
        return "NEDESCHIS", ["timeout"]
    if js.get("eroare_deschidere"):
        return "NEDESCHIS", [js["eroare_deschidere"]]
    pica = js.get("pica", {})
    if any(NEDESCHIS_FARA_FEREASTRA in m for r in pica.values() for m in r):
        return "NEDESCHIS", [NEDESCHIS_FARA_FEREASTRA]
    motive = list(pica.get(litera, []))
    if nume == FEREASTRA_MICA:   # fereastra mică are numai „✕”: celelalte motive ale rândului a (căutare, CUI, nume) nu o privesc
        motive = [m for m in motive if e_motiv_x(m)] if litera == "a" else []
    return ("ROSU" if motive else "VERDE"), motive


def agrega(stari):
    """Precedența la nivel de rând: NEDESCHIS > ROSU > VERDE (oricare rezoluție NEDESCHISĂ = rând NEDESCHIS)."""
    for s in ("NEDESCHIS", "ROSU"):
        if s in stari:
            return s
    return "VERDE"


def _motiv_rand(litera, pe_rez):
    """Motivele rândului pe rezoluții: o dată dacă sunt la fel la ambele, altfel cu rezoluția."""
    liste = [m for _, m in pe_rez]
    if not any(liste):
        return ""
    if all(m == liste[0] for m in liste):
        return "%s: %s" % (litera, "; ".join(liste[0]))
    return "; ".join("%s (%s): %s" % (litera, rez, "; ".join(m)) for rez, m in pe_rez if m)


def rand_intrare(nume, js_pe_rez):
    """-> (rand a, rand b, motiv) pentru o intrare; `js_pe_rez` = {rezoluție: js | None | STARE_TIMEOUT}."""
    ev = {l: [(rez, evalueaza(js, l, nume)) for rez, js in js_pe_rez.items()] for l in ("a", "b")}
    randuri = {l: agrega([e[0] for _, e in ev[l]]) for l in ev}
    if nume == FEREASTRA_MICA:
        randuri["b"] = "-"
    motive = []
    for l in ("a", "b"):
        if randuri[l] == "-":
            continue
        t = _motiv_rand(l, [(rez, e[1]) for rez, e in ev[l]])
        if t:
            motive.append(t)
    return randuri["a"], randuri["b"], " | ".join(motive)


def deschide(nume, rez):
    """Deschide o intrare la o rezoluție într-un subproces cu timeout; -> js | None | STARE_TIMEOUT."""
    import verificator_design as VD
    cale = os.path.join(JSON_DIR, "%s_%s.json" % (VD.slug(nume), rez))
    if os.path.exists(cale):
        os.remove(cale)
    cmd = [sys.executable, os.path.join(RAD, "scripts", "verificator_design.py"), "ecran", nume, rez, JSON_DIR, PNG_DIR]
    p = subprocess.Popen(cmd, cwd=RAD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        p.wait(timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        import signal
        os.killpg(p.pid, signal.SIGKILL)
        p.wait()
        return STARE_TIMEOUT
    if not os.path.exists(cale):
        return None
    try:
        return json.load(open(cale, encoding="utf-8"))
    except ValueError:
        return None


def matrice():
    import verificator_design as VD
    intrari = VD.registru()
    os.makedirs(JSON_DIR, exist_ok=True)
    os.makedirs(PNG_DIR, exist_ok=True)
    t0 = time.time()
    randuri = []
    for e in intrari:
        randuri.append([e["nume"], *rand_intrare(e["nume"], {rez: deschide(e["nume"], rez) for rez in REZOLUTII})])
        print("[matrice] %d/%d %s: a=%s b=%s" % (len(randuri), len(intrari), e["nume"], randuri[-1][1], randuri[-1][2]), flush=True)
    with open(CSV, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ecran", "rand a", "rand b", "motiv"])
        w.writerows(randuri)
    if len(randuri) != len(intrari):
        print("[matrice] REFUZ: %d rânduri față de %d intrări" % (len(randuri), len(intrari)), file=sys.stderr)
        return 1
    open(os.path.join(JSON_DIR, "durata.txt"), "w", encoding="utf-8").write("%d s\n" % round(time.time() - t0))
    return 0


def main():
    import calibreaza_16_7 as C
    return C.ruleaza_pe_server("matrice_16_7.py", matrice, scrie_sha=os.path.join(JSON_DIR, "sha.txt"))


if __name__ == "__main__":
    sys.exit(main())
