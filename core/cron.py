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
    # Bataia e efect secundar: un job nou, inca neadaugat in RITMURI, NU trebuie sa cada
    # din cauza asta. Dar o spune, ca lipsa supravegherii sa nu fie tacuta.
    try:
        bate(nume, durata)
    except ValueError as e:
        print("[heartbeat] %s" % e, flush=True)
    print("%s job OK: %s (%.1fs)" % (inceput, nume, durata), flush=True)
    return rez


# ============================================================
#  HEARTBEAT — jobul care NU porneste deloc
# ============================================================
# Ritmul fiecarui job si pragul in ore peste care lipsa devine alerta.
# Pragul = ritm x2 + marja: o rulare ratata nu alarmeaza, doua consecutive da.
# sinteza_zilnica ruleaza doar luni-vineri -> vineri 19:00 pana luni 19:00 sunt 72h normale.
#
# DOUA SURSE, nu una (R74, 27.08.2026). Lista era "din crontab" si atat - iar cele trei joburi
# SPV ruleaza din TIMERE SYSTEMD, deci n-au fost niciodata in ea. Rezultatul: au rulat un
# interpretor inexistent (/opt/iconta/venv/, sters pe 27.07) si au esuat cu status 203 la
# fiecare declansare timp de ~31 de zile, in tacere. Deadman-ul nu se uita la ele fiindca
# lista lui era o COPIE a crontab-ului, nu o citire a sistemului.
# `core/test_joburi_supravegheate.py` citeste acum ambele surse si compara cu lista asta.
RITMURI = {
    "alerta_acces":        2,     # la 15 minute
    # [P2, 08.09.2026] modelul de citire al portofoliului. La 5 minute: rezumatul e ce vede
    # contabilul pe ecran, iar o firma atinsa la 9:05 n-are de ce sa apara gri pana maine.
    "firma_rezumat":       1,     # la 5 minute
    "audit_retentie":      50,    # zilnic 04:00
    "facturi_recurente":   50,    # zilnic 07:00
    "woocommerce":         50,    # zilnic 07:30
    "notificari_scadenta": 50,    # zilnic 08:00
    "monitor_fiscal":      50,    # zilnic 09:00 + luni 08:00
    "sinteza_zilnica":     96,    # luni-vineri 19:00 (72h peste weekend + marja)
    "expirare_cote":       800,   # LUNAR, ziua 1 06:00 (~730h; 800 prinde o luna ratata)
    # --- procesul care serveste ecranele (R75 (b), 27.08.2026) ---
    # Al 12-lea job supravegheat NU e un job: e `iconta-nou.service`, procesul care le serveste pe
    # toate. Pana azi joburile de fundal aveau deadman si el nu avea nimic. `core/sonda_web` cere
    # pagina (viu SI RASPUNDE, cum a cerut Costin) si compara ora de pornire a unitatii cu cea de
    # la sonda precedenta - o repornire intre doua sonde se vede, chiar daca a durat trei secunde.
    # Ce NU se poate spune de aici: CAT a fost jos. Limita e scrisa in antetul sondei.
    "sonda_web":           2,     # la 15 minute (crontab)
    # --- timere systemd (nu crontab), adaugate 27.08.2026 pe R74 ---
    "spv_poll":            2,     # timer spv-poll, la 30 de minute (*:07,37)
    "spv_receive":         2,     # timer spv-receive, la 30 de minute (*:17,47)
    "spv_refresh":         50,    # timer spv-refresh, zilnic 03:30
}

# Ce NU se supravegheaza aici, si de ce - ca absenta sa fie declarata, nu tacuta:
#   `cron`            = heartbeat-ul insusi. Cine il supravegheaza pe el cere un deadman
#                       EXTERN; limita e scrisa in verifica_batai si nu se rezolva azi.
#   `iconta-backup`   = shell, nu modul Python: nu poate chema `bate()`. Isi alerteaza singur
#                       esecurile consecutive (FAIL_PRAG in iconta-backup.sh), deci nu e tacut.
NESUPRAVEGHEATE = {"cron": "heartbeat-ul insusi - cere deadman EXTERN",
                   "iconta-backup": "shell, nu modul; alerteaza singur (iconta-backup.sh)"}


# ============================================================
#  DE UNDE SE AFLA JOBURILE — din SISTEM, nu dintr-o copie scrisa de mana
# ============================================================
# R74, 27.08.2026. Gardul de pana acum compara `RITMURI` cu un set scris in test - deci se
# compara cu propria copie a raspunsului si n-avea cum sa vada un job pe care nu-l stia deja.
# Functiile de mai jos sunt PURE (primesc text, intorc structura), ca sa poata fi calibrate;
# `citeste_sistemul()` e singura care atinge discul.

def joburi_din_crontab(text):
    """Modulele `core.X` chemate din liniile necomentate ale unui crontab. -> set(nume)."""
    import re
    gasite = set()
    for linie in (text or "").splitlines():
        if linie.strip().startswith("#") or not linie.strip():
            continue
        gasite.update(re.findall(r"-m\s+core\.([A-Za-z_][A-Za-z_0-9]*)", linie))
    return gasite


def _camp_unitate(text, cheie):
    for linie in (text or "").splitlines():
        s = linie.strip()
        if s.startswith(cheie + "="):
            return s[len(cheie) + 1:].strip()
    return None


def unitati_systemd(perechi):
    """perechi = [(nume_timer, text_timer, nume_service, text_service)].

    -> [{timer, service, modul, interpretor, calendar}]. `modul` e None cand serviciul nu
    ruleaza un modul Python (shell) - acela nu poate bate si se declara in NESUPRAVEGHEATE.
    """
    import re
    out = []
    for timer, t_txt, service, s_txt in perechi:
        exec_start = _camp_unitate(s_txt, "ExecStart") or ""
        m = re.search(r"-m\s+core\.([A-Za-z_][A-Za-z_0-9]*)", exec_start)
        out.append({
            "timer": timer,
            "service": service,
            "modul": m.group(1) if m else None,
            "interpretor": exec_start.split()[0] if exec_start.split() else None,
            "calendar": _camp_unitate(t_txt, "OnCalendar"),
        })
    return out


def citeste_sistemul(dir_unitati="/etc/systemd/system"):
    """(joburi_din_crontab, unitati_systemd) citite de pe masina asta. Atinge discul."""
    import glob
    import io as _io
    import os
    import subprocess
    try:
        r = subprocess.run(["crontab", "-l"], capture_output=True, text=True, timeout=20)
        ct = r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        ct = ""
    perechi = []
    for cale_t in sorted(glob.glob(os.path.join(dir_unitati, "*.timer"))):
        try:
            t_txt = _io.open(cale_t, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        nume_t = os.path.basename(cale_t)
        tinta = _camp_unitate(t_txt, "Unit") or (nume_t[:-6] + ".service")
        cale_s = os.path.join(dir_unitati, tinta)
        try:
            s_txt = _io.open(cale_s, encoding="utf-8", errors="ignore").read()
        except OSError:
            s_txt = ""
        perechi.append((nume_t, t_txt, tinta, s_txt))
    return joburi_din_crontab(ct), unitati_systemd(perechi)


DDL_DETALII = """
-- [R75 (b), 27.08.2026] Memoria sondei web: ce a observat la rularea precedenta (ora de pornire
-- a unitatii). Fara ea, sonda ar putea spune doar „raspunde acum", nu „a repornit intre timp".
ALTER TABLE public.cron_batai ADD COLUMN IF NOT EXISTS detalii jsonb;
"""


def asigura_detalii(conn):
    """Idempotent. Se cheama o data, din `python3 -m core.cron --migrare`."""
    with conn.cursor() as cur:
        cur.execute(DDL_DETALII)
    return True


def bate(nume, durata_sec=None):
    """Consemneaza o rulare REUSITA. Esecul consemnarii nu strica jobul, dar o SPUNE.

    Numele TREBUIE sa fie in RITMURI: altfel nimeni nu-l supravegheaza, iar randul doar
    se acumuleaza in tabel. (27.07.2026: o verificare manuala scrisese randul 'proba' in
    productie - exact felul de reziduu care nu trebuie lasat in urma.)
    """
    if nume not in RITMURI:
        raise ValueError(
            "job necunoscut in heartbeat: %r. Adauga-l in cron.RITMURI cu pragul lui, "
            "altfel nimic nu-i supravegheaza lipsa." % nume)
    try:
        from core import db
        db.init_pool()          # nemascat - vezi nota din verifica_batai
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                # upsert-ok: heartbeat cron pe nume - incrementeaza rulari + timestamp, intentionat
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
    # init_pool NU se mascheaza (27.07.2026): daca esueaza, get_conn de mai jos crapa
    # oricum, dar cu mesajul "pool neinitializat" - cauza reala (variabile de mediu
    # lipsa) ramane ascunsa. Dovedit rulind modulul fara .env dupa reboot.
    db.init_pool()
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
    if "--migrare" in sys.argv:          # [R75 (b)] coloana `detalii` pe cron_batai
        from core import db as _db
        _db.init_pool()
        with _db.get_conn() as _c:
            asigura_detalii(_c)
        print("cron_batai.detalii: gata")
        sys.exit(0)
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
