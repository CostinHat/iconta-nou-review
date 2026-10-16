# -*- coding: utf-8 -*-
"""core/rulari_teste.py — rulează acum pe server o probă sau o suită de teste? (comanda Costin 15.10.2026 noaptea, „Lotul 5 — comanda 3”
pct.6b: alerta de load „nu pleacă în timpul rulărilor tale de teste”).

Rulările de probă împart procesoarele cu producția: pytest (`-n 3` în poartă), plasa e2e și uneltele vizuale (aplicația de probă pe
portul 8019, Chromium). Procesul aplicației rulează ca același utilizator, deci citește `/proc/<pid>/cmdline` al lor. Un proces e o
rulare de teste dacă linia lui de comandă are unul din `SEMNE` — numite aici, într-un singur loc. Limită declarată: o rulare pornită de
alt utilizator (fără acces la `/proc/<pid>/cmdline`) nu se vede; pe server toate rulările sunt ale utilizatorului `costin`.
Gard: core/test_rulari_teste.py."""
import os

#: semnele unei rulări de teste în linia de comandă (cuvinte întregi, după despărțirea pe NUL și spații)
SEMNE = ("pytest", "e2e_poarta.py", "poarta_lot.sh", "poarta_scurta.py", "axe_scan.py", "mobil_scan.py",
         "interactiune_scan.py", "text_ecran_scan.py")
#: aplicația de probă (`scripts/e2e_poarta.PORT`) — pornită cu `--port 8019`
PORT_PROBA = "8019"


def _e_rulare(argv):
    cuvinte = [os.path.basename(a) for a in argv]
    if any(c in SEMNE for c in cuvinte):
        return True
    return "uvicorn" in cuvinte and any(argv[i] == "--port" and argv[i + 1] == PORT_PROBA for i in range(len(argv) - 1))


def in_curs(proc="/proc"):
    """[(pid, linia de comandă scurtă)] ale rulărilor de teste care merg acum."""
    out = []
    try:
        pids = [p for p in os.listdir(proc) if p.isdigit()]
    except OSError:
        return out
    for pid in pids:
        try:
            with open(os.path.join(proc, pid, "cmdline"), "rb") as f:
                argv = [a.decode("utf-8", "replace") for a in f.read().split(b"\0") if a]
        except OSError:          # procesul s-a terminat între listare și citire, sau nu e al nostru
            continue
        argv = [w for a in argv for w in a.split()] if len(argv) == 1 else argv
        if argv and _e_rulare(argv):
            out.append((int(pid), " ".join(argv)[:120]))
    return out
