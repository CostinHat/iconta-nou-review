# -*- coding: utf-8 -*-
"""Detector "running == HEAD": commitul cu care a PORNIT procesul (stampilat in memorie la startup) vs HEAD de
pe disc. Nu reporneste, nu repara - doar semnaleaza (decizia iulie: detector vizibil, NU auto-restart; vezi
GARZI/DECIZII "running == HEAD"). Commitul rulat NU se deduce din mtime-uri: se citeste git HEAD in momentul
pornirii procesului si se tine in memorie (= codul incarcat de procesul viu)."""
import os
import subprocess

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # radacina repo (parintele lui core/)

RUNNING_COMMIT = None   # stampilat O DATA la startup (lifespan); commitul cu care ruleaza procesul viu


def git_head(rad=RAD):
    """HEAD citit ACUM de pe disc (subprocess git rev-parse). None daca nu se poate citi fidel (repo lipsa,
    git indisponibil) - NU se cade pe deducere din mtime-uri."""
    try:
        r = subprocess.run(["git", "-C", rad, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=5)
        h = r.stdout.strip()
        return h if r.returncode == 0 and len(h) == 40 else None
    except Exception:
        return None


def stampileaza(rad=RAD):
    """Se apeleaza O DATA la startup (lifespan): fixeaza in memorie commitul cu care a pornit procesul = codul
    pe care il ruleaza. Ulterior HEAD de pe disc poate avansa fara restart -> divergenta."""
    global RUNNING_COMMIT
    RUNNING_COMMIT = git_head(rad)
    return RUNNING_COMMIT


def stare_versiune(running, head):
    """PURA: {running, head, divergent, necunoscut}. divergent = ambele cunoscute SI diferite. Pe necunoscut
    (None de o parte) NU semnalam divergenta (nu alarmam pe nesigur), dar marcam necunoscut=True."""
    divergent = bool(running and head and running != head)
    return {"running": running, "head": head,
            "divergent": divergent, "necunoscut": not (running and head)}


def stare(rad=RAD):
    """Starea LIVE: commitul din memorie (startup) vs HEAD de pe disc acum."""
    return stare_versiune(RUNNING_COMMIT, git_head(rad))
