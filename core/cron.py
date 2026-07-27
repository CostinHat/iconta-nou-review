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
    durata = time.time() - t0
    bate(nume, durata)
    print("%s job OK: %s (%.1fs)" % (inceput, nume, durata), flush=True)
    return rez


# ============================================================
#  HEARTBEAT — jobul care NU porneste deloc
# ============================================================
# Ritmul fiecarui job (din crontab, 27.07.2026) si pragul in ore peste care lipsa devine
# alerta. Pragul = ritm x2 + marja: o rulare ratata nu alarmeaza, doua consecutive da.
# sinteza_zilnica ruleaza doar luni-vineri -> vineri 19:00 pana luni 19:00 sunt 72h normale.
RITMURI = {
    "alerta_acces":        2,     # la 15 minute
    "audit_retentie":      50,    # zilnic 04:00
    "facturi_recurente":   50,    # zilnic 07:00
    "woocommerce":         50,    # zilnic 07:30
    "notificari_scadenta": 50,    # zilnic 08:00
    "monitor_fiscal":      50,    # zilnic 09:00 + luni 08:00
    "sinteza_zilnica":     96,    # luni-vineri 19:00 (72h peste weekend + marja)
}


def bate(nume, durata_sec=None):
    """Consemneaza o rulare REUSITA. Esecul consemnarii nu strica jobul, dar o SPUNE."""
    try:
        from core import db
        try:
            db.init_pool()
        except Exception:
            pass
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.cron_batai (nume, ultima_reusita, durata_sec, rulari) "
                    "VALUES (%s, now(), %s, 1) "
                    "ON CONFLICT (nume) DO UPDATE SET ultima_reusita = now(), "
                    "durata_sec = EXCLUDED.durata_sec, rulari = public.cron_batai.rulari + 1",
                    (nume, round(durata_sec, 2) if durata_sec is not None else None))
            conn.commit()
    except Exception as e:
        print("[bataie neconsemnata: %s] %s: %s" % (nume, type(e).__name__, e), flush=True)


def verifica_batai(acum=None, ritmuri=None):
    """Joburile care au depasit pragul (sau n-au batut niciodata). [(nume, ore, motiv)].

    DE CE (27.07.2026): `ruleaza()` prinde jobul care CRAPA. NU prinde jobul care nu porneste
    DELOC - cron oprit, reboot fara restaurarea crontab-ului, linie stearsa din greseala,
    server jos la ora rularii. Un job disparut arata exact ca unul care n-a avut de lucru -
    dovedit chiar azi cu woocommerce (tacut 12 zile; a fost nevoie de investigatie ca sa se
    stabileasca daca e defect - nu era).

    LIMITA DECLARATA: verificatorul ruleaza pe ACELASI server. Server jos = nici el nu ruleaza,
    nimeni nu afla. Un deadman EXTERN (ping catre un serviciu tert care alerteaza la lipsa
    semnalului) ar acoperi si asta; nu se construieste azi.
    """
    import datetime
    from core import db
    ritmuri = ritmuri or RITMURI
    acum = acum or datetime.datetime.now(datetime.timezone.utc)
    try:
        db.init_pool()
    except Exception:
        pass
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT nume, ultima_reusita FROM public.cron_batai")
            vazute = {r[0]: r[1] for r in cur.fetchall()}
        conn.rollback()
    intarziate = []
    for nume, prag_ore in sorted(ritmuri.items()):
        ultima = vazute.get(nume)
        if ultima is None:
            intarziate.append((nume, None, "nicio rulare reusita consemnata vreodata"))
            continue
        ore = (acum - ultima).total_seconds() / 3600.0
        if ore > prag_ore:
            intarziate.append((nume, round(ore, 1),
                               "ultima reusita acum %.1f ore (prag %d)" % (ore, prag_ore)))
    return intarziate


def bootstrap():
    """Pune o bataie initiala pentru joburile care n-au niciuna, la instalarea heartbeat-ului.

    Fara asta, un job cu ritm lung (sinteza_zilnica ruleaza luni-vineri la 19:00) apare
    "intarziat" din prima secunda, desi doar nu i-a venit inca randul. Un fals-pozitiv la
    instalare invata omul sa ignore alerta - exact ce nu vrem. Dupa bootstrap, pragurile
    pornesc de ACUM: daca jobul chiar nu ruleaza in intervalul lui, se detecteaza.
    """
    noi = []
    for nume in RITMURI:
        if not verifica_batai(ritmuri={nume: RITMURI[nume]}):
            continue
        bate(nume, None)
        noi.append(nume)
    return noi


def _main_verificare():
    """Rulat de systemd timer (NU de cron: trebuie sa supravietuiasca unui crontab pierdut)."""
    import datetime
    intarziate = verifica_batai()
    marca = datetime.datetime.now().isoformat(timespec="seconds")
    if not intarziate:
        print("%s heartbeat: toate joburile la zi" % marca, flush=True)
        return 0
    corp = "\n".join("  - %s: %s" % (n, m) for n, _o, m in intarziate)
    print("%s heartbeat: %d joburi intarziate\n%s" % (marca, len(intarziate), corp), flush=True)
    try:
        from core import observare
        observare.alerteaza("cron_heartbeat",
                            "Joburi de fundal care nu au mai rulat",
                            "Urmatoarele joburi n-au mai raportat o rulare reusita:\n\n%s\n\n"
                            "Verifica: crontab -l, systemctl status cron, "
                            "si logurile din ~/iconta_nou/*.log" % corp)
    except Exception as e:
        print("%s ALERTA NETRIMISA: %s" % (marca, e), flush=True)
    return len(intarziate)


if __name__ == "__main__":
    # Exit 0 chiar cand exista joburi intarziate: verificarea SI-A FACUT treaba, iar semnalul
    # e ALERTA, nu codul de iesire. Cu exit 1, systemd marcheaza serviciul "failed" la fiecare
    # rulare cu constatari - si atunci un esec REAL al heartbeat-ului (DB jos, cod stricat) ar
    # arata identic cu functionarea normala. Acelasi principiu ca peste tot azi: un semnal care
    # se aprinde mereu nu mai e semnal.
    try:
        _main_verificare()
    except BaseException:
        import traceback
        print("HEARTBEAT ESUAT:\n%s" % traceback.format_exc(), flush=True)
        sys.exit(1)          # AICI exit 1 e corect: verificarea insasi n-a putut rula
    sys.exit(0)
