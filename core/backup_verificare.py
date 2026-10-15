# -*- coding: utf-8 -*-
"""core/backup_verificare.py — supravegherea backup-ului LOCAL al bazei (comanda Costin 14.10.2026, pct.5: „repară alerta la eșecul
dump-ului local”; verbatim în DECIZII „Lotul 2”).

DE CE. `iconta-backup.sh` (timer systemd, 03:00, rulat ca `postgres`) alerta NUMAI la eșecul copiei off-site: cu `set -euo pipefail`,
un `pg_dump` local căzut oprea scriptul înaintea contorului și a emailului, unitatea n-are `OnFailure=`, iar deadman-ul aplicației
(`cron.NESUPRAVEGHEATE`) îl scutea pe motiv că „alertează singur”. Un backup local mort era TĂCUT (GARZI cat.7, corectat 14.10.2026).

CE FACE (zilnic 04:30, din crontab, prin `cron.ruleaza` — eșec = alertă Brevo + exit 1; reușită = bătaie `backup_verificare`, deci și
lipsa rulării alarmează, prin `cron.verifica_batai`): ultimul `iconta_v2_*.dump` din /var/backups/iconta trebuie să fie
  - RECENT (mai nou de VARSTA_MAX_ORE),
  - NE-TRUNCHIAT (cel puțin MIN_FRACTIE din mărimea dump-ului anterior și peste MIN_OCTETI),
  - CITIBIL (`pg_restore -l` iese 0 și cuprinsul are date de tabel) și CITIBIL INTEGRAL (`pg_restore -f /dev/null` — decomprimă
    fiecare bloc de date). `-l` citește NUMAI cuprinsul din capul arhivei: un dump tăiat la 70% iese cu cod 0 la `-l` și cu cod 1
    („could not read from input file: end of file”) la citirea integrală — măsurat pe 15.10.2026 pe o copie trunchiată.
Prinde și timerul care n-a pornit deloc (nimic nou), nu doar scriptul care a căzut. Nu citește date: numai cuprinsul arhivei.
LIMITA: aceeași mașină — serverul jos nu-și poate semnala singur lipsa (limita din `cron.verifica_batai`).
"""
import datetime
import glob
import os
import subprocess

DIR = "/var/backups/iconta"
VARSTA_MAX_ORE = 26          # backup-ul rulează la 03:00; o zi ratată + marjă
MIN_FRACTIE = 0.5            # un dump sub jumătatea celui de dinainte e suspect de trunchiere
MIN_OCTETI = 100 * 1024


def verifica(director=DIR, acum=None, pg_restore="pg_restore"):
    """`{fisier, ore, octeti, tabele_cu_date}` pentru ultimul dump; `RuntimeError` cu motivul, altfel."""
    dumpuri = sorted(glob.glob(os.path.join(director, "iconta_v2_*.dump")), key=os.path.getmtime)
    if not dumpuri:
        raise RuntimeError("Niciun backup local al bazei (iconta_v2_*.dump) în %s." % director)
    ultimul = dumpuri[-1]
    acum = acum or datetime.datetime.now().timestamp()
    ore = (acum - os.path.getmtime(ultimul)) / 3600.0
    if ore > VARSTA_MAX_ORE:
        raise RuntimeError("Ultimul backup local al bazei (%s) e vechi de %.1f ore (prag %d): backup-ul de noapte n-a mai "
                           "produs un dump." % (os.path.basename(ultimul), ore, VARSTA_MAX_ORE))
    octeti = os.path.getsize(ultimul)
    if octeti < MIN_OCTETI:
        raise RuntimeError("Ultimul backup local al bazei (%s) are numai %d octeți." % (os.path.basename(ultimul), octeti))
    if len(dumpuri) > 1:
        anterior = os.path.getsize(dumpuri[-2])
        if octeti < MIN_FRACTIE * anterior:
            raise RuntimeError("Ultimul backup local al bazei (%s, %d octeți) e sub jumătate din cel de dinainte (%d octeți): "
                               "probabil trunchiat." % (os.path.basename(ultimul), octeti, anterior))
    r = subprocess.run([pg_restore, "-l", ultimul], capture_output=True, text=True)
    tabele = sum(1 for l in r.stdout.splitlines() if " TABLE DATA " in l)
    if r.returncode != 0 or tabele == 0:
        raise RuntimeError("Ultimul backup local al bazei (%s) nu se poate citi cu pg_restore (cod %d, %d tabele cu date): %s"
                           % (os.path.basename(ultimul), r.returncode, tabele, (r.stderr or "").strip()[:300]))
    r = subprocess.run([pg_restore, "-f", os.devnull, ultimul], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("Ultimul backup local al bazei (%s) nu se poate citi integral cu pg_restore (cod %d): %s"
                           % (os.path.basename(ultimul), r.returncode, (r.stderr or "").strip()[:300]))
    return {"fisier": os.path.basename(ultimul), "ore": round(ore, 1), "octeti": octeti, "tabele_cu_date": tabele}


if __name__ == "__main__":
    from core import cron
    rez = cron.ruleaza("backup_verificare", verifica)
    print("backup local verificat: %s" % rez, flush=True)
