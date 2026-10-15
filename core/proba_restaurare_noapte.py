# -*- coding: utf-8 -*-
"""core/proba_restaurare_noapte.py — PROBA DE RESTAURARE AUTOMATĂ, în fiecare noapte (decizia Costin 15.10.2026, pct.4, verbatim în
DECIZII „Lotul 3 — C35”: „Proba de restaurare automată în fiecare noapte: da, pe o bază separată ștearsă după probă; în jurnal numai
cifre.”).

DE CE. `backup_verificare` (04:30) dovedește că dump-ul de noapte e recent, întreg și citibil; nu dovedește că se poate RESTAURA într-o
bază care funcționează. Proba manuală din lotul 2 (`scripts/proba_restaurare.py`) o dovedea o dată; de acum, în fiecare noapte.

CE FACE (zilnic 05:00, din crontab, prin `cron.ruleaza` — eșec = alertă Brevo + exit 1; reușită = bătaia `proba_restaurare_noapte`, deci și
lipsa rulării alarmează, prin `cron.verifica_batai`): ia ultimul `iconta_v2_*.dump` din /var/backups/iconta (backup-ul de 03:00) și
îl dă probei de restaurare în modul „dump existent”: bază SEPARATĂ (`iconta_proba_restaurare`), restaurare cu `ON_ERROR_STOP`,
amprenta ei față de producția de acum (scheme, tabele, rânduri, sume de control), apoi baza se șterge și se verifică absența ei —
inclusiv la eșec. Pică dacă restaurarea are vreo eroare, dacă lipsește vreun tabel din cuprinsul arhivei sau dacă baza restaurată e
goală. Diferențele față de producția de acum (scrierile și migrările de după 03:00) se numără, nu pică.

ÎN JURNAL NUMAI CIFRE: proba tipărește numai numere și sume sha256 — niciun nume de firmă, de fișier sau valoare din rânduri; erorile
au numai etapa și codul de ieșire (textul unei erori `COPY` ar purta rândul).
LIMITA: aceeași mașină și același server de baze de date ca producția — dovedește arhiva, nu recuperarea după pierderea serverului.
"""
import glob
import os
import sys

DIR = "/var/backups/iconta"
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ultimul_dump(director=DIR):
    dumpuri = sorted(glob.glob(os.path.join(director, "iconta_v2_*.dump")), key=os.path.getmtime)
    if not dumpuri:
        raise RuntimeError("Niciun backup local al bazei (iconta_v2_*.dump) de restaurat.")
    return dumpuri[-1]


def proba(director=DIR):
    sys.path.insert(0, os.path.join(_RAD, "scripts"))
    import proba_restaurare
    cod = proba_restaurare.main(["proba_restaurare", "--dump", ultimul_dump(director)])
    if cod != 0:
        raise RuntimeError("Proba de restaurare a backup-ului de noapte a PICAT (cod %d) — cifrele sunt în proba_restaurare.log." % cod)
    return "restaurat și comparat; baza de probă ștearsă"


if __name__ == "__main__":
    from core import cron
    print("proba de restaurare: %s" % cron.ruleaza("proba_restaurare_noapte", proba), flush=True)
