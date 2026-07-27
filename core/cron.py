# -*- coding: utf-8 -*-
"""core/cron.py — ambalaj pentru joburile de fundal (cron).

PROBLEMA (dovedita 27.07.2026): crontab-ul NU are MAILTO si serverul n-are MTA local.
Un job care crapa scrie un traceback in fisierul lui de log si atat - nimeni nu afla.
Joburile ruleaza NESUPRAVEGHEAT: facturi recurente emise, notificari de scadenta,
alerte fiscale, alerta de acces anormal (securitate), audit de retentie (GDPR).
Un job mort arata exact ca unul care n-a avut nimic de facut.

Doctrina exista deja scrisa in iconta-backup.sh: "Off-site care esueaza TACIT e mai rau
decat lipsa lui -> se logheaza + alerteaza." Joburile cron nu o respectau.

CE FACE: ruleaza functia, si daca arunca:
  1. tipareste traceback-ul complet in log (pentru diagnostic);
  2. ALERTEAZA prin canalul unic observare.alerteaza (Brevo, cu throttling pe cheie);
  3. iese cu cod 1, ca esecul sa fie vizibil si pentru cron/systemd.
Pe succes tipareste marca de timp + durata: logul spune ca jobul A RULAT, nu doar ca
n-a avut de lucru (tacerea nu se mai confunda cu moartea).

NU acopera: jobul care nu porneste DELOC (cron oprit, reboot, linie stricata in crontab).
Pentru asta e nevoie de heartbeat/deadman - subiect separat, in DE_FACUT.

ALERTA NU TREBUIE SA MASCHEZE ESECUL: daca trimiterea alertei crapa la randul ei, se
tipareste si se iese TOT cu cod 1. Un canal de alertare care inghite eroarea pe care
trebuia s-o semnaleze ar fi aceeasi clasa de bug ca `except: pass`.
"""
import datetime
import sys
import time
import traceback

MODUL = "cron"


def ruleaza(nume, fn):
    """Ruleaza fn() ca job de fundal. Esec -> log + alerta + exit(1)."""
    t0 = time.time()
    inceput = datetime.datetime.now().isoformat(timespec="seconds")
    try:
        rez = fn()
    except BaseException:
        tb = traceback.format_exc()
        durata = time.time() - t0
        print("%s JOB ESUAT: %s (dupa %.1fs)\n%s" % (inceput, nume, durata, tb), flush=True)
        try:
            from core import observare
            observare.alerteaza(
                "cron_esec_%s" % nume,
                "Job de fundal esuat: %s" % nume,
                "Jobul '%s' a esuat la %s, dupa %.1f secunde.\n\n%s" % (nume, inceput, durata, tb))
        except BaseException:
            print("%s ALERTA NETRIMISA pentru %s:\n%s"
                  % (inceput, nume, traceback.format_exc()), flush=True)
        sys.exit(1)
    print("%s job OK: %s (%.1fs)" % (inceput, nume, time.time() - t0), flush=True)
    return rez
