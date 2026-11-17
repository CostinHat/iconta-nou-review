# -*- coding: utf-8 -*-
"""scripts/verificator_design.py — uneltele VERIFICATORULUI DE DESIGN pe criteriul „migrat” (comanda 15.1-E1, R5 / R6 / R7).

Verificatorul independent (un subagent, promptul fix din `scripts/verificator_design_prompt.txt`) nu rulează niciodată pe producție:
rulează pe serverul de lucru, portul 8019, pe baza de TEST, cu copia firmelor de test (`scripts/dovada_firme_test.py --cloneaza`).
Unealta asta pornește / oprește serverul și măsoară un ecran: PIESELE (clase DS, înălțimi, rânduri), nu pixelii; criteriul rândurilor a–h
e scris o singură dată, în `RANDURI` de mai jos (promptul îl repetă cuvânt cu cuvânt, `core/test_verificator_design_prompt.py` le păzește
identice). Un singur rând PICĂ = ecranul e nemigrat.

  python scripts/verificator_design.py porneste            serverul de lucru pe 8019, din commitul curent (arbore curat), pe baza de TEST
  python scripts/verificator_design.py opreste             oprește serverul din stare.json și orice server al uneltelor care mai ține portul (elibereaza_port); iese cu 1 dacă portul rămâne ocupat
  python scripts/verificator_design.py prompt <director> <ecran>...   promptul fix, cu lista de ecrane și directorul capturilor
  python scripts/verificator_design.py lista               ecranele din registru (core/catalog_ecrane.json)
  python scripts/verificator_design.py ecran "<nume>" <LATxINALT> <director> [<director_png>]
                                                           deschide ecranul ca un contabil, scrie `<director>/<slug>_<LAT>x<INALT>.png` și `.json`
                                                           (măsurătorile și verdictul mecanic pe rândurile a–h) și le tipărește
"""
import contextlib
import fcntl
import json
import os
import re
import select
import shutil
import signal
import stat
import subprocess
import sys
import threading
import time
import unicodedata

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAD, "scripts"))
sys.path.insert(0, RAD)

PORT = 8019
TEMP = "/tmp/verificator_design"
STARE = os.path.join(TEMP, "stare.json")
STARE_COPIE = os.path.expanduser("~/.cache/iconta_dovada")
REGISTRU = os.path.join(RAD, "core", "catalog_ecrane.json")
MASURI = os.path.join(RAD, "scripts", "verificator_design_masuri.js")

#: Criteriul „migrat” (comanda 15.1-E1 pct.2, R7), cuvânt cu cuvânt. Cheia = litera rândului.
RANDURI = {
    "a": "bara de sus: 56 px, fără traseu, firma sau cabinetul în lucru cu CUI, numele ferestrei, căutarea; traseu înseamnă două sau mai multe "
         "ecrane vizitate înșiruite — un singur „›” urmat de numele ferestrei curente NU e traseu; la Panou Admin, unde nu e nicio firmă sau "
         "cabinet în lucru, contextul e „Panou Admin”, fără CUI; „✕” (închidere) de 40 × 40, exact unul, ultimul element din bară, în dreapta sus, "
         "pe FIECARE fereastră de lucru și pe cele mici; „←” nu se judecă: apare numai unde există un pas înapoi real (fereastră deschisă din alta "
         "sau cu pas intern), altfel fereastra are numai „✕”",
    "b": "fereastra de lucru pe tot ecranul la 1920 × 1080 și 1366 × 768, un singur loc de derulare (tabelul lung), bara de jos fixă 72 px "
         "cu un singur buton principal L (cu data-actiune-principala), a cărui etichetă e verbul acțiunii (un buton principal cu textul „Completează …” pică: motivul inactivității stă în bară); bara nu are „Renunță”, în afara ferestrelor din PASTREAZA_RENUNTA (fără „←” activ "
         "în starea formularului sau cu „Renunță” cu efect propriu; revenirea e „←” din antet, „✕” închide); „Închide” și „Renunță” nu sunt "
         "acțiune principală, oricum ar fi colorate; butonul principal inactiv cu motiv cât timp acțiunea nu e posibilă; acțiunea principală a ferestrei "
         "apare o singură dată pe ecran: niciun buton vizibil din conținut (în afara tabelelor, template și details) nu are același text ca butonul "
         "principal din bara de jos; excepție (stare sau meniu "
         "de butoane, pe nume, lista din raport): bara fără buton principal și fără „Renunță”",
    "c": "orice listă de înregistrări e tabelul DS: cap ≥ 40 px, rând ≥ 44 px (cu rândul care se rupe, înălțimea crește), zebra, starea doar în coloana „Stare”, cel mult 2 acțiuni XS pe "
         "rând, subsol 44 px (rândul de totaluri fix, bara-fixa, nu e o listă de înregistrări; nici starea goală, nici meniul sau panoul de cifre marcat `data-fara-piesa`); nicio celulă cu dată sau sumă tăiată",
    "d": "orice avertisment sau explicație secundară e card-rezumat ≥ 44 px (cu textul rupt, înălțimea crește) cu detaliile pliate; orice semnal e un rând de 36 px (cel mult două rânduri, textul întreg, fără „…”) cu „ce e de "
         "făcut” pliat; niciun paragraf explicativ mai lung de un rând nepliat; un card-rezumat gri (neutru, informativ) e valid; cardurile de eroare "
         "rămân la vedere și nu se numără, din celelalte cel mult 2 la vedere (restul sub „Semnale (n)”); un semnal sau card al cărui text spune "
         "„deschide X” sau „mergi la X” are butonul care deschide X",
    "e": "nicio acțiune în casete de text sau în mijlocul conținutului; acțiune = buton, navigare = link",
    "f": "titlurile de secțiune fără majuscule (numele proprii — firme, cabinete — nu sunt titluri); titlurile de grup 14 px majuscule gri; textele din catalog, cu diacritice, pluralul după număr, "
         "același mesaj o singură dată pe ecran",
    "g": "date, sume, perioade, firma prin funcția unică (un cod de cont analitic, ca 4428.01, nu e o sumă)",
    "h": "cota TVA ca grup cu cotele la data documentului plus categoriile fără TVA; nicio listă derulantă sub 7 variante; nimic „— alege —” sau opțiune goală",
}


#: [17.3] Ferestrele care păstrează „Renunță” în bara de jos, pe titlul din `.fir-acum`: aceleași ca `static/js/cadru.js::PASTREAZA_RENUNTA` și ca rândurile «fără ←» / «efect propriu: da»
#: din docs/dovezi/17_3/inapoi.txt. Intersecția cu EXCEPTII_B e goală; dacă nu, EXCEPTII_B are prioritate.
PASTREAZA_RENUNTA = ["Încasări/plăți", "Invitații cabinete", "Notificări", "Pachete lunare"]


#: Ecranele fără acțiune principală (stare sau meniu de butoane), pe nume — comanda 15.1-E5 pct.1; lista intră în raport. Aceleași ferestre ca
#: `static/js/cadru.js::FARA_ACTIUNE_PRINCIPALA`.
EXCEPTII_B = {"Sinteza zilei": "stare", "Supervizor": "stare", "Declarații lucrate": "stare",
              "Firme": "meniu", "Import date F1": "meniu", "Facturi F1": "meniu", "Operațiuni speciale F1": "meniu", "Activitate": "meniu", "Setări cont": "meniu",
              "Migrare cabinet": "meniu", "Ghiduri": "meniu", "Panou Admin — Anunțuri": "meniu",
              "Mișcări și fișe de magazie F1": "stare", "Mișcări, fișe de magazie, coduri, nivel minim": "stare"}


# ── serverul de lucru ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
#: [17.5-Z] Lacătul serverului de lucru: UN singur fișier pentru toate worktree-urile, ținut (flock) pe toată durata `porneste` / `opreste` / `elibereaza_port`; reentrant în același proces.
LACAT_VD = os.path.expanduser("~/.iconta/lacat_verificator_design")
LACAT_ASTEAPTA = 60                      # secunde de așteptare a lacătului ținut de altă operație, apoi refuz
MARCAJ_TEMP = ".proprietar_verificator_design"
_LACAT_FIR = threading.RLock()
_LACAT_STARE = {"adancime": 0, "fd": None}


class Refuz(Exception):
    """Un refuz al uneltei: rc nenul, ZERO semnale și ZERO ștergeri dincolo de ce s-a făcut deja."""


@contextlib.contextmanager
def _lacat():
    with _LACAT_FIR:
        if _LACAT_STARE["adancime"] == 0:
            os.makedirs(os.path.dirname(LACAT_VD), exist_ok=True)
            fd = os.open(LACAT_VD, os.O_RDWR | os.O_CREAT, 0o600)
            for incercare in range(int(LACAT_ASTEAPTA * 2) + 1):
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if incercare >= int(LACAT_ASTEAPTA * 2):
                        os.close(fd)
                        raise Refuz("lacătul serverului de lucru e ținut de altă operație (%s)" % LACAT_VD)
                    time.sleep(0.5)
            _LACAT_STARE["fd"] = fd
        _LACAT_STARE["adancime"] += 1
        try:
            yield
        finally:
            _LACAT_STARE["adancime"] -= 1
            if _LACAT_STARE["adancime"] == 0:
                fd, _LACAT_STARE["fd"] = _LACAT_STARE["fd"], None
                os.close(fd)                 # închiderea eliberează flock


def _raspunde(port=None):
    import urllib.request
    try:
        return urllib.request.urlopen("http://127.0.0.1:%d/" % (port or PORT), timeout=3).status == 200
    except Exception:  # noqa: BLE001
        return False


# [17.5-Z, §2.2] Sonda portului e FAIL-CLOSED: „liber” numai dintr-un `ss` reușit, cu ieșire întreagă și interpretabilă; orice altceva e „necunoscut”.
def _rul_ss(port, cu_procese):
    """-> (rc, stdout, stderr) al lui `ss`; (None, "", motiv) dacă nu se poate rula."""
    try:
        r = subprocess.run(["ss", "-ltnp" if cu_procese else "-ltn", "( sport = :%d )" % port], capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.SubprocessError) as e:
        return None, "", "%s: %s" % (type(e).__name__, e)
    return r.returncode, r.stdout, r.stderr


def _parseaza_ss(port, rc, out, err):
    """-> (stare, pids, motiv): stare «liber» | «ocupat» | «necunoscut»; `pids` = lista pid-urilor vizibile (None pentru un proprietar invizibil)."""
    if rc is None:
        return "necunoscut", [], "ss n-a putut rula (%s)" % err.strip()[:150]
    if rc != 0:
        return "necunoscut", [], "ss a ieșit cu codul %s (%s)" % (rc, err.strip()[:150])
    if err.strip():
        return "necunoscut", [], "ss a scris pe stderr: %s" % err.strip()[:150]
    linii = [ln for ln in out.splitlines() if ln.strip()]
    if not linii or linii[0].split()[:1] != ["State"] or "Local" not in linii[0] or "Peer" not in linii[0]:
        return "necunoscut", [], "ieșirea lui ss e invalidă sau trunchiată"
    pids = []
    for ln in linii[1:]:
        c = ln.split()
        if len(c) < 5 or c[0] != "LISTEN" or not c[3].endswith(":%d" % port):
            return "necunoscut", [], "rând ss neinterpretabil: %s" % ln[:120]
        if "users:(" in ln and ln.count("(") != ln.count(")"):
            return "necunoscut", [], "rând ss trunchiat: %s" % ln[:120]
        gasite = re.findall(r"pid=(\d+)", ln)
        pids.extend(int(x) for x in gasite) if gasite else pids.append(None)
    return ("ocupat" if pids else "liber"), pids, ""


def stare_port(port=None, cu_procese=False):
    """-> (stare, pids, motiv) pentru portul `port` (implicit 8019). Singura sondă de port a uneltei."""
    port = port or PORT
    return _parseaza_ss(port, *_rul_ss(port, cu_procese))


# [17.5-U, U.1] „Ocupat” = portul apare în LISTEN în `ss` (nu răspunsul HTTP). [17.5-Z] O sondă eșuată NU e „liber”: întoarce True (nu putem afirma că e liber).
def port_ocupat(port=None):
    return stare_port(port)[0] != "liber"


def _pornit(pid):
    """Ora pornirii procesului (ISO, din /proc: câmpul 22 din stat + btime) sau „?”."""
    import datetime
    import lacat_test
    tacte = lacat_test.ora_start(pid)
    if tacte is None:
        return "?"
    btime = next(int(ln.split()[1]) for ln in open("/proc/stat", encoding="utf-8") if ln.startswith("btime "))
    return datetime.datetime.fromtimestamp(btime + int(tacte) / os.sysconf("SC_CLK_TCK")).isoformat(timespec="seconds")


def identitate(pid):
    """Identitatea unui proces din /proc: {pid, start (câmpul 22, brut), pgid, sid, cwd (realpath sau None), cmd (sau None), boot_id (sau None)}; None dacă nu se poate citi stat."""
    try:
        s = open("/proc/%d/stat" % pid, encoding="utf-8", errors="replace").read()
        camp = s[s.rindex(")") + 2:].split()
        start, pgid, sid = camp[19], int(camp[2]), int(camp[3])
    except (OSError, ValueError, IndexError):
        return None
    try:
        cmd = open("/proc/%d/cmdline" % pid, "rb").read().replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except OSError:
        cmd = None
    try:
        cwd = os.path.realpath(os.readlink("/proc/%d/cwd" % pid))
    except OSError:
        cwd = None
    try:
        boot = open("/proc/sys/kernel/random/boot_id", encoding="utf-8").read().strip()
    except OSError:
        boot = None
    return {"pid": pid, "start": start, "pgid": pgid, "sid": sid, "cwd": cwd, "cmd": cmd, "boot_id": boot}


def proprietari_port(port=None):
    """Proprietarii portului după `ss -ltnp`: [{pid, comanda, director (realpath din /proc/<pid>/cwd, None dacă nu se poate citi), pornit, start, pgid, sid}]; un port ocupat al cărui pid nu se
    vede, ca și o sondă `ss` eșuată sau neinterpretabilă, întoarce [{pid: None, …}] (străin / necunoscut)."""
    port = port or PORT
    stare, pids, motiv = stare_port(port, cu_procese=True)
    if stare != "ocupat" or None in pids:
        return [{"pid": None, "comanda": "", "director": None, "pornit": "?", "start": None, "pgid": None, "sid": None, "motiv_ss": motiv or "pid invizibil"}]
    iesire = []
    for pid in sorted(set(pids)):
        i = identitate(pid) or {}
        iesire.append({"pid": pid, "comanda": i.get("cmd") or "", "director": i.get("cwd"), "pornit": _pornit(pid),
                       "start": i.get("start"), "pgid": i.get("pgid"), "sid": i.get("sid")})
    return iesire


def _sub(cale, radacina):
    radacina = os.path.realpath(radacina)
    return cale == radacina or cale.startswith(radacina.rstrip(os.sep) + os.sep)


def radacini_unelte():
    """Arborii în care trăiesc serverele uneltelor: worktree-urile de lot (~/iconta_lot*) și directoarele temporare ale verificatorului și ale plasei (TEMP, E2E_TEMP)."""
    import glob
    return sorted(glob.glob(os.path.expanduser("~/iconta_lot*"))) + [TEMP, os.environ.get("E2E_TEMP", "/tmp/e2e_poarta"), "/tmp/e2e_poarta"]


def radacini_productie():
    return [os.path.expanduser("~/iconta_nou")]


def _descrie(p):
    return "pid %s, comanda %s, directorul %s, pornit %s" % (p["pid"], (p["comanda"] or "?")[:200], p["director"] or "?", p["pornit"])


def _motiv_refuz(p, unelte, productie):
    """Motivul pentru care procesul e „străin” (nu se oprește) sau None când e server al uneltelor, DEMONSTRAT: pid vizibil, cwd citit sub un arbore al uneltelor și nu sub producție, «uvicorn» în linia
    de comandă, starttime citit, PID = PGID = SID (liderul propriei sesiuni), diferit de procesul curent și de părinte și de grupul lor. Producția nu se oprește niciodată; orice martor lipsă = străin."""
    if p["pid"] is None:
        return "pid-ul procesului nu se vede" + (" (%s)" % p["motiv_ss"] if p.get("motiv_ss") and p["motiv_ss"] != "pid invizibil" else "")
    if p["director"] is None:
        return "directorul de lucru nu se poate citi"
    if any(_sub(p["director"], r) for r in productie):
        return "directorul de lucru e sub arborele producției"
    if "uvicorn" not in p["comanda"]:
        return "linia de comandă nu conține «uvicorn»"
    if not any(_sub(p["director"], r) for r in unelte):
        return "directorul de lucru nu e într-un arbore al uneltelor"
    if not p.get("start"):
        return "ora de start din /proc nu se poate citi"
    if p.get("pgid") != p["pid"] or p.get("sid") != p["pid"]:
        return "procesul nu e liderul propriei sesiuni (PID, PGID și SID diferă)"
    if p["pid"] in (os.getpid(), os.getppid()) or p["pgid"] in (os.getpgrp(), os.getpgid(os.getppid())):
        return "procesul sau grupul lui e al procesului curent sau al părintelui"
    return None


def _jurnal(lot, detalii, rezultat):
    try:
        import jurnal_lot as JL
        lot = lot or JL.lot_curent()
        if lot == "?":
            return
        JL.sfarsit(lot, "elibereaza_8019", JL.inceput(lot, "elibereaza_8019", detalii), rezultat)
    except Exception as e:  # noqa: BLE001  — jurnalul nu oprește eliberarea
        print("[verificator design] jurnalul n-a putut scrie faza elibereaza_8019: %s: %s" % (type(e).__name__, e), file=sys.stderr)


# [17.5-Z, §2.7] Semnale numai prin pidfd (referință stabilă a procesului), niciodată `killpg` / `kill` pe un număr de PID.
def _asteapta_iesire(fd, secunde):
    """True dacă procesul din pidfd a ieșit în `secunde` (pidfd devine citibil la ieșire)."""
    return bool(select.select([fd], [], [], secunde)[0])


def _inchide_fd(fd):
    try:
        os.close(fd)
    except OSError:
        pass


def _opreste_prin_pidfd(fd, port, asteapta_term=20, asteapta_kill=30):
    """SIGTERM prin `fd`, apoi SIGKILL prin ACELAȘI `fd` numai dacă procesul trăiește după timeout. -> (ok, motiv): ok = procesul a ieșit și `ss` (rc 0) arată portul liber."""
    for sem, asteapta in ((signal.SIGTERM, asteapta_term), (signal.SIGKILL, asteapta_kill)):
        try:
            signal.pidfd_send_signal(fd, sem, None, 0)
        except ProcessLookupError:
            break
        except OSError as e:
            return False, "semnalul %s prin pidfd a eșuat: %s" % (sem.name, e)
        if _asteapta_iesire(fd, asteapta):
            break
    else:
        return False, "procesul n-a ieșit nici după SIGKILL"
    for _ in range(60):                         # până la 30 s ca portul să fie liber, cu o sondă reușită
        if stare_port(port)[0] == "liber":
            return True, ""
        time.sleep(0.5)
    return False, "portul %d nu e liber (sau starea lui nu se poate afla) după oprire" % port


def _opreste_redescoperit(p, port):
    """Oprește un proces REDESCOPERIT (din `ss` sau din stare): pidfd_open, apoi revalidarea completă a identității și a proprietății portului CU pidfd deschis. -> (ok, motiv)."""
    martor = {k: p.get(k) for k in ("start", "pgid", "sid")}
    try:
        fd = os.pidfd_open(p["pid"])
    except OSError as e:
        return False, "pidfd_open(%s) a eșuat: %s" % (p["pid"], e)
    try:
        i = identitate(p["pid"])
        if i is None or {k: i[k] for k in martor} != martor or (p.get("director") and i["cwd"] != p["director"]) or (p.get("comanda") and i["cmd"] != p["comanda"].strip()):
            return False, "identitatea pid %s s-a schimbat între identificare și pidfd_open" % p["pid"]
        stare, pids, _m = stare_port(port, cu_procese=True)
        if stare != "ocupat" or pids != [p["pid"]]:
            return False, "proprietatea portului %d s-a schimbat sau nu se poate confirma" % port
        return _opreste_prin_pidfd(fd, port)
    finally:
        _inchide_fd(fd)


def elibereaza_port(port=None, sonda=None, opreste_fn=None, lot=None, unelte=None, productie=None, proprietari=None):
    """Singura cale prin care se eliberează portul serverului de lucru (U.1). -> (ok, motiv).
    Port liber (`ss` reușit): nimic de oprit; sondă eșuată = refuz, nu „liber”. Server al uneltelor DEMONSTRAT (linia de comandă conține «uvicorn», directorul de lucru sub un arbore de lot, TEMP sau
    E2E_TEMP, nu sub producție, PID = PGID = SID): tipărește pid-ul, comanda, directorul și ora pornirii, îl oprește numai prin pidfd (SIGTERM, SIGKILL pe același pidfd după 20 s), așteaptă până
    la 30 s ca portul să fie liber și scrie în jurnalul lotului faza «elibereaza_8019», rezultat «ok», cele patru valori în detalii; portul rămas ocupat = refuz. Orice alt proces: nu se oprește
    nimic, refuz cu aceleași patru valori.
    `sonda` / `opreste_fn` date (injectate sau suprascrise în teste): blocul vechi, sonda apoi oprirea chemată o singură dată dacă sonda întoarce True, fără proprietar, așteptare sau jurnal."""
    port = port or PORT
    if sonda is not None or opreste_fn is not None:
        if (sonda or _raspunde)():
            (opreste_fn or opreste)()
        return True, ""
    try:
        with _lacat():
            return _elibereaza_sub_lacat(port, lot, unelte, productie, proprietari)
    except Refuz as e:
        print("[verificator design] REFUZ: %s" % e, file=sys.stderr)
        return False, str(e)


def _elibereaza_sub_lacat(port, lot, unelte, productie, proprietari):
    stare, _pids, motiv = stare_port(port)
    if stare == "liber":
        return True, ""
    if stare == "necunoscut":
        print("[verificator design] REFUZ: starea portului %d nu se poate afla: %s" % (port, motiv), file=sys.stderr)
        return False, "starea portului %d necunoscută: %s" % (port, motiv)
    unelte = radacini_unelte() if unelte is None else unelte
    productie = radacini_productie() if productie is None else productie
    props = (proprietari or proprietari_port)(port)
    for p in props:
        m = _motiv_refuz(p, unelte, productie)
        if m:
            print("[verificator design] REFUZ: portul %d e ocupat de un proces străin (%s): %s" % (port, m, _descrie(p)), file=sys.stderr)
            return False, "%d ocupat de pid %s (%s)" % (port, p["pid"] if p["pid"] is not None else "invizibil", (p["comanda"] or "necunoscută")[:120])
    for p in props:
        print("[verificator design] portul %d e ținut de un server al uneltelor: %s; îl opresc" % (port, _descrie(p)))
        ok, motiv = _opreste_redescoperit(p, port)
        if not ok:
            return False, "%d încă ocupat după încercarea de oprire a lui pid %s (%s): %s" % (port, p["pid"], (p["comanda"] or "?")[:120], motiv)
    if stare_port(port)[0] != "liber":
        return False, "%d încă ocupat (sau starea lui necunoscută) după oprirea lui pid %s" % (port, props[0]["pid"])
    _jurnal(lot, "; ".join(_descrie(x) for x in props), "ok")
    return True, ""


# ── TEMP: proprietate și curățare sigură ─────────────────────────────────────────────────────────────────────────────────────────────────
def _stare_cale():
    return os.path.join(TEMP, "stare.json")


def _temp_proprietar():
    """-> (stare, motiv): «absent» | «propriu» (director real, al executantului, fără drept de scriere pentru alții, cu marcajul uneltei SAU cu stare.json în formatul uneltei) | «nesigur»."""
    for cale in (os.path.dirname(TEMP), TEMP):
        try:
            st = os.lstat(cale)
        except FileNotFoundError:
            if cale == TEMP:
                return "absent", ""
            return "nesigur", "%s lipsește" % cale
        except OSError as e:
            return "nesigur", "lstat %s: %s" % (cale, e)
        if stat.S_ISLNK(st.st_mode) or not stat.S_ISDIR(st.st_mode):
            return "nesigur", "%s nu e un director real (legătură simbolică sau alt tip)" % cale
        if cale == TEMP:
            if st.st_uid != os.getuid():
                return "nesigur", "%s nu aparține executantului" % cale
            if st.st_mode & 0o002:
                return "nesigur", "%s are drept de scriere pentru alții" % cale
    try:
        if os.path.lexists(os.path.join(TEMP, MARCAJ_TEMP)) and not os.path.islink(os.path.join(TEMP, MARCAJ_TEMP)):
            return "propriu", ""
        st_json = json.load(open(_stare_cale(), encoding="utf-8")) if os.path.isfile(_stare_cale()) and not os.path.islink(_stare_cale()) else None
        if isinstance(st_json, dict) and "pid" in st_json and "sha" in st_json:
            return "propriu", ""
    except (OSError, ValueError):
        pass
    return "nesigur", "%s nu poartă marcajul uneltei (dovezi sau date străine; arhivează-l sau decide explicit)" % TEMP


def _citeste_stare():
    """stare.json al uneltei sau Refuz: JSON invalid, câmpuri lipsă."""
    try:
        s = json.load(open(_stare_cale(), encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise Refuz("stare.json invalid sau ilizibil: %s" % e)
    cheie = ("pid", "start", "pgid", "sid", "cwd", "cmd", "sha")
    if not isinstance(s, dict) or any(k not in s for k in cheie) or not isinstance(s["pid"], int) or isinstance(s["pid"], bool) or s["pid"] <= 1:
        raise Refuz("stare.json incompletă: lipsesc câmpuri sau pid-ul e invalid")
    return s


def _scrie_stare(stare):
    """Atomic: fișier temporar în același director, fsync, apoi os.replace."""
    tmp = _stare_cale() + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(stare, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, _stare_cale())


def _sterge_temp():
    """Șterge TEMP numai cu proprietatea dovedită; -> None sau Refuz."""
    st, motiv = _temp_proprietar()
    if st == "absent":
        return
    if st != "propriu":
        raise Refuz("TEMP păstrat: %s" % motiv)
    shutil.rmtree(TEMP)


def _identitate_server_stare(s):
    """Identitatea din stare.json față de /proc: refuz la orice diferență (PID reutilizat, mort, alt grup, alt director, altă comandă, producție, proces propriu)."""
    i = identitate(s["pid"])
    if i is None:
        raise Refuz("pid %s din stare.json nu mai există (stare veche); verifică manual și șterge stare.json" % s["pid"])
    for k in ("start", "pgid", "sid", "cwd", "cmd"):
        if i[k] != s[k]:
            raise Refuz("pid %s: %s diferă față de stare.json (PID reutilizat sau proces străin)" % (s["pid"], k))
    if s.get("boot_id") and i["boot_id"] != s["boot_id"]:
        raise Refuz("boot_id diferă față de stare.json")
    p = {"pid": s["pid"], "comanda": i["cmd"] or "", "director": i["cwd"], "pornit": _pornit(s["pid"]), "start": i["start"], "pgid": i["pgid"], "sid": i["sid"]}
    m = _motiv_refuz(p, radacini_unelte(), radacini_productie())
    if m:
        raise Refuz("pid %s din stare.json e refuzat: %s" % (s["pid"], m))
    return p


def _curata_copil(app, fd, martor, port):
    """[§2.6] Oprește copilul DIRECT al lui `porneste()` prin pidfd-ul capturat în aceeași invocare (fără cerința de prezență în ss). -> (ok, motiv)."""
    if app.poll() is not None:
        app.wait()
        return (stare_port(port)[0] == "liber"), "copilul ieșise; portul " + ("e liber" if stare_port(port)[0] == "liber" else "nu e liber sau starea lui nu se poate afla")
    if fd is None or martor is None:
        return False, "pidfd sau identitatea copilului nu s-au putut stabili: nu trimit niciun semnal; copilul pid %s rămâne pornit" % app.pid
    i = identitate(app.pid)
    if i is None or {k: i[k] for k in ("start", "pgid", "sid", "cwd", "cmd")} != {k: martor[k] for k in ("start", "pgid", "sid", "cwd", "cmd")}:
        return False, "identitatea copilului pid %s s-a schimbat: nu trimit niciun semnal" % app.pid
    try:
        signal.pidfd_send_signal(fd, signal.SIGTERM, None, 0)
    except ProcessLookupError:
        pass
    except OSError as e:
        return False, "SIGTERM prin pidfd a eșuat: %s" % e
    if not _asteapta_iesire(fd, 20):
        try:
            signal.pidfd_send_signal(fd, signal.SIGKILL, None, 0)
        except ProcessLookupError:
            pass
        except OSError as e:
            return False, "SIGKILL prin pidfd a eșuat: %s" % e
        if not _asteapta_iesire(fd, 30):
            return False, "copilul pid %s n-a ieșit nici după SIGKILL" % app.pid
    try:
        app.wait(timeout=10)
    except subprocess.TimeoutExpired:
        return False, "copilul pid %s nu a fost recoltat" % app.pid
    liber = stare_port(port)[0] == "liber"
    return liber, "copilul oprit; portul " + ("e liber" if liber else "nu e liber sau starea lui nu se poate afla")


def porneste():
    try:
        with _lacat():
            return _porneste_sub_lacat()
    except Refuz as e:
        print("[verificator design] REFUZ: %s" % e, file=sys.stderr)
        return 1


def _porneste_sub_lacat():
    stare, _p, motiv = stare_port(PORT)
    if stare == "necunoscut":
        print("[verificator design] REFUZ: starea portului %d nu se poate afla (%s); nu pornesc" % (PORT, motiv), file=sys.stderr)
        return 1
    if stare == "ocupat":
        print("[verificator design] REFUZ: portul %d e ocupat de: %s" % (PORT, "; ".join(_descrie(p) for p in proprietari_port(PORT))), file=sys.stderr)
        return 1
    if not os.path.exists(os.path.join(STARE_COPIE, "stare.json")):
        print("[verificator design] copia firmelor de test nu există: rulează întâi scripts/dovada_firme_test.py --cloneaza", file=sys.stderr)
        return 2
    st_temp, motiv = _temp_proprietar()
    if st_temp == "nesigur":
        print("[verificator design] REFUZ: %s; nu șterg nimic" % motiv, file=sys.stderr)
        return 4
    if st_temp == "propriu" and os.path.isfile(_stare_cale()):
        try:
            s_veche = json.load(open(_stare_cale(), encoding="utf-8"))
            if isinstance(s_veche, dict) and isinstance(s_veche.get("pid"), int) and identitate(s_veche["pid"]) is not None \
                    and identitate(s_veche["pid"])["start"] == s_veche.get("start", identitate(s_veche["pid"])["start"]):
                print("[verificator design] REFUZ: TEMP e folosit de un proces viu (pid %s din stare.json)" % s_veche["pid"], file=sys.stderr)
                return 4
        except (OSError, ValueError):
            pass
    os.environ["E2E_TEMP"] = TEMP           # înaintea importului: `e2e_poarta.TEMP` se citește la import
    import e2e_poarta
    if e2e_poarta.TEMP != TEMP:
        print("[verificator design] REFUZ: e2e_poarta.TEMP (%s) diferă de TEMP (%s): _exporta ar șterge alt director" % (e2e_poarta.TEMP, TEMP), file=sys.stderr)
        return 4
    from dovada_firme_test import tinta_de_test
    env = e2e_poarta._env_test()
    tinta_de_test(env)                      # refuză dacă mediul nu e dovedit de test
    git = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    stare, _p, motiv = stare_port(PORT)     # revalidare sub lacăt, chiar înainte de `_exporta` (care șterge TEMP fără condiții)
    st_temp, motiv_t = _temp_proprietar()
    if stare != "liber" or st_temp == "nesigur":
        print("[verificator design] REFUZ înainte de export: port %s (%s), TEMP %s (%s); nu șterg nimic" % (stare, motiv, st_temp, motiv_t), file=sys.stderr)
        return 4
    try:
        arb = e2e_poarta._exporta(False)    # indexul = ce se comite (arborele de lucru murdar nu se verifică)
        if os.path.islink(TEMP) or not os.path.isdir(TEMP) or not os.path.isdir(arb):
            raise OSError("TEMP după export nu e un director real")
        open(os.path.join(TEMP, MARCAJ_TEMP), "w").write("%d\n" % os.getuid())
        st_temp, motiv_t = _temp_proprietar()
        if st_temp != "propriu":
            raise OSError("TEMP după export nu e un director real propriu: %s" % motiv_t)
    except (OSError, subprocess.SubprocessError) as e:
        print("[verificator design] exportul a eșuat: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 3
    py = os.path.join(RAD, "venv", "bin", "python")
    r = subprocess.run([py, "scripts/publica_static.py", "--din-arbore"], cwd=arb, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print("[verificator design] publicarea staticului a eșuat: " + (r.stdout + r.stderr)[-400:], file=sys.stderr)
        return 3
    for k in ("ICONTA_AI_SIMULAT", "ICONTA_ANAF_SIMULAT", "ICONTA_BON_DIR"):
        os.makedirs(env[k], exist_ok=True)
    log = open(os.path.join(TEMP, "uvicorn.log"), "w")
    app = subprocess.Popen([py, "-m", "uvicorn", "main:app", "--port", str(PORT)], cwd=arb, env=env, stdout=log, stderr=subprocess.STDOUT,
                           start_new_session=True)
    fd, martor, eroare = None, None, None
    try:
        fd = os.pidfd_open(app.pid)
        martor = identitate(app.pid)
        if martor is None and app.poll() is None:
            eroare = "identitatea copilului pid %s nu se poate citi" % app.pid
        elif martor is not None and not (martor["pid"] == martor["pgid"] == martor["sid"]) or martor["pid"] in (os.getpid(), os.getppid()) \
                or martor["pgid"] in (os.getpgrp(), os.getpgid(os.getppid())) or "uvicorn" not in (martor["cmd"] or "") \
                or not martor["cwd"] or any(_sub(martor["cwd"], r) for r in radacini_productie()):
            eroare = "identitatea copilului pid %s nu e a unui server al uneltelor (PID/PGID/SID, cmdline sau cwd)" % app.pid
    except OSError as e:
        if app.poll() is None:
            eroare = "pidfd_open pe copilul pid %s a eșuat: %s" % (app.pid, e)
    if eroare:
        print("[verificator design] REFUZ: %s; STOP, nu trimit semnale; dovezile rămân în %s" % (eroare, TEMP), file=sys.stderr)
        if fd is not None:
            _inchide_fd(fd)
        return 3
    try:
        pornit = False
        for _ in range(120):
            if app.poll() is not None:
                eroare = "serverul a ieșit în timpul pornirii (cod %s; vezi %s/uvicorn.log)" % (app.returncode, TEMP)
                break
            if _raspunde():
                pornit = True
                break
            time.sleep(2)
        else:
            eroare = "aplicația n-a răspuns pe %d (vezi %s/uvicorn.log)" % (PORT, TEMP)
        if pornit:
            stare, pids, _m = stare_port(PORT, cu_procese=True)
            if stare != "ocupat" or pids != [app.pid]:
                eroare = "portul %d nu e ținut exclusiv de serverul pornit (ss: %s %s)" % (PORT, stare, pids)
        if not eroare:
            sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
            _scrie_stare({"pid": app.pid, "start": martor["start"], "pgid": martor["pgid"], "sid": martor["sid"], "cwd": martor["cwd"], "cmd": martor["cmd"],
                          "boot_id": martor["boot_id"], "sha": sha, "arbore_murdar": bool(git)})
            print("[verificator design] serverul de lucru pe %d, commit %s%s" % (PORT, sha[:8], " (arbore murdar: se verifică indexul)" if git else ""))
            return 0
    except OSError as e:
        eroare = "scrierea stării a eșuat: %s: %s" % (type(e).__name__, e)
    finally:
        log.close()
    ok, detaliu = _curata_copil(app, fd, martor, PORT)
    _inchide_fd(fd)
    print("[verificator design] %s; copilul: %s" % (eroare, detaliu), file=sys.stderr)
    return 3


def opreste():
    """Oprește serverul din stare.json (identitate verificată, pidfd) sau, fără stare.json, orice server al uneltelor care ține portul (elibereaza_port, ruta U.1); apoi curăță TEMP numai cu
    proprietatea dovedită. Ieșire 1 la orice ambiguitate (stare invalidă, proces străin, port necunoscut sau ocupat, TEMP nepropriu): zero semnale, zero ștergeri."""
    try:
        with _lacat():
            return _opreste_sub_lacat()
    except Refuz as e:
        print("[verificator design] REFUZ: %s; nu s-a trimis niciun semnal și nu s-a șters nimic nou" % e, file=sys.stderr)
        return 1


def _opreste_sub_lacat():
    if os.path.lexists(_stare_cale()):
        s = _citeste_stare()
        p = _identitate_server_stare(s)
        stare, pids, motiv = stare_port(PORT, cu_procese=True)
        if stare == "necunoscut":
            raise Refuz("starea portului %d nu se poate afla: %s" % (PORT, motiv))
        if stare == "ocupat" and pids != [s["pid"]]:
            raise Refuz("portul %d e ținut de alt proprietar decât pid %s din stare.json" % (PORT, s["pid"]))
        if stare == "liber" and p is not None:
            raise Refuz("pid %s din stare.json trăiește, dar nu ține portul %d; nu îl opresc automat" % (s["pid"], PORT))
        if stare == "ocupat":
            ok, motiv = _opreste_redescoperit(p, PORT)
            if not ok:
                print("[verificator design] oprit; portul %d ocupat: %s" % (PORT, motiv))
                return 1
    else:
        ok, motiv = elibereaza_port(PORT)
        if not ok:
            print("[verificator design] oprit; portul %d ocupat: %s" % (PORT, motiv))
            return 1
    if stare_port(PORT)[0] != "liber":
        print("[verificator design] oprit; starea portului %d nu e «liber» confirmat" % PORT)
        return 1
    _sterge_temp()
    print("[verificator design] oprit; portul %d liber" % PORT)
    return 0


# ── ecranele ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def slug(nume):
    s = unicodedata.normalize("NFKD", nume).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def registru():
    return json.load(open(REGISTRU, encoding="utf-8"))


def _sesiune(utilizator):
    stare = json.load(open(os.path.join(STARE_COPIE, "stare.json"), encoding="utf-8"))
    email = stare["utilizatori"]["superadmin"] if utilizator == "superadmin" else stare["utilizator"]["email"]
    parola = open(os.path.join(STARE_COPIE, "parola"), encoding="utf-8").read().strip()
    import pasi
    return pasi.autentifica("http://127.0.0.1:%d" % PORT, email, parola), stare["firme"]


def ecran(nume, rez, director, interventie=None, masuri_alt=None, director_png=None):
    """Deschide ecranul `nume` din registru la rezoluția `LATxINALT`; scrie captura și măsurătorile. [16.7] `interventie` = JS rulat după pași,
    înaintea măsurării; `masuri_alt` = a doua cale .js evaluată pe aceeași pagină (rezultat în cheia `masuri_alt`); `director_png` = directorul capturilor."""
    from playwright.sync_api import sync_playwright
    intrari = [e for e in registru() if e["nume"] == nume]
    if not intrari:
        print("[verificator design] ecran necunoscut: %r (vezi `lista`)" % nume, file=sys.stderr)
        return 2
    e = intrari[0]
    lat, inalt = (int(x) for x in rez.split("x"))
    os.makedirs(director, exist_ok=True)
    if director_png:
        os.makedirs(director_png, exist_ok=True)
    os.environ["PROBA_BAZA"] = "http://127.0.0.1:%d" % PORT
    os.environ["E2E_CAPTURI"] = director
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "dovada"))
    init, firme = _sesiune(e.get("utilizator", "cabinet"))
    schema = next((k for k, v in firme.items() if v["nume"].startswith(e["firma"] + " ")), None) if e.get("firma") else None
    if e.get("firma") and not schema:
        print("[verificator design] firma %r nu e în copie" % e["firma"], file=sys.stderr)
        return 2
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(viewport={"width": lat, "height": inalt})
        ctx.add_init_script(init)
        pg = ctx.new_page()
        erori = []
        pg.on("pageerror", lambda x: erori.append(str(x)))
        pg.on("response", lambda r: erori.append("HTTP %d %s" % (r.status, r.url)) if r.status >= 500 else None)
        import pasi
        ec = pasi._e2e("http://127.0.0.1:%d" % PORT, director).Ecran(pg, "verificator")
        eroare = None
        try:
            if e.get("firma"):
                ec.firma(firme[schema]["nume"])
            else:
                ec.acasa()
            for pas in e.get("pasi", []):
                _pas(pg, pas)
            pg.wait_for_timeout(800)
            if interventie:
                pg.evaluate(interventie)
                pg.wait_for_timeout(300)
        except Exception as ex:  # noqa: BLE001 — un ecran care nu se deschide e un rezultat, nu o oprire
            eroare = str(ex).splitlines()[0][:300]
        pg.evaluate("(e) => { window.__exceptieB = e; }", EXCEPTII_B.get(nume))
        pg.evaluate("(l) => { window.__pastreazaRenunta = l; }", PASTREAZA_RENUNTA)
        masuri = pg.evaluate(open(MASURI, encoding="utf-8").read())
        if masuri_alt:
            masuri["masuri_alt"] = pg.evaluate(open(masuri_alt, encoding="utf-8").read())
        masuri.update({"ecran": nume, "rezolutie": rez, "firma": e.get("firma"), "nivel": e.get("nivel"), "eroare_deschidere": eroare or None,
                       "erori_js": erori + ec.erori})
        baza = os.path.join(director, "%s_%s" % (slug(nume), rez))
        pg.screenshot(path=os.path.join(director_png or director, os.path.basename(baza) + ".png"))
        b.close()
    masuri["verdict_mecanic"] = verdict_mecanic(masuri)
    json.dump(masuri, open(baza + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(masuri, ensure_ascii=False, indent=1))
    return 0


def _pas(pg, pas):
    """Un pas al registrului: `{"click": CSS, "text": T}` | `{"text": T}` (clic pe butonul cu textul) | `{"pauza": MS}` | `{"scrie": CSS, "valoare": V}`."""
    if "click" in pas:
        loc = pg.locator(pas["click"])
        if pas.get("index_rand"):   # rândul care conține textul (tabelul DS sau rând-buton), apoi elementul din el
            loc = pg.locator("tr, .firme-rand, button.firme-rand").filter(has_text=pas["index_rand"]).locator(pas["click"])
        if pas.get("text"):
            loc = loc.filter(has_text=pas["text"])
        loc.first.click(timeout=20000)
    elif "text" in pas:
        pg.get_by_text(pas["text"], exact=pas.get("exact", False)).first.click(timeout=20000)
    elif "cauta" in pas:   # căutarea de funcții din bara de sus a ferestrei (aceeași cale ca a contabilului)
        pg.click("#cautare-fereastra")
        pg.fill("#cautare-fereastra", pas["cauta"])
        pg.wait_for_timeout(700)
        pg.locator("#cautare-fereastra-rez .cautare-item").first.click(timeout=20000)
    elif "scrie" in pas:
        pg.fill(pas["scrie"], pas["valoare"])
    elif "pauza" in pas:
        pass
    else:
        raise ValueError("pas necunoscut: %r" % (pas,))
    pg.wait_for_timeout(int(pas.get("pauza", 600)))


def verdict_mecanic(m):
    """Verdictul mecanic pe rândurile a–h, din măsurătorile paginii: {rând: {"verdict": "TRECE"|"PICĂ", "motive": [...]}}.
    E piesa „script care refuză” (R5): subagentul confirmă sau contrazice, cu captura, dar nu slăbește un PICĂ mecanic fără motiv scris."""
    out = {}
    for r in RANDURI:
        motive = list(m.get("pica", {}).get(r, []))
        if m.get("eroare_deschidere") and r == "a":
            motive.insert(0, "ecranul nu s-a deschis: %s" % m["eroare_deschidere"])
        out[r] = {"verdict": "PICĂ" if motive else "TRECE", "motive": motive}
    return out


def prompt(ecrane, director):
    """Promptul fix al verificatorului (`verificator_design_prompt.txt`) cu rândurile a–h din `RANDURI` și lista de ecrane; directorul capturilor
    se spune în prompt. Nimic altceva nu intră în el: subagentul nu vede modificările, notele sau testele lui Code."""
    txt = open(os.path.join(RAD, "scripts", "verificator_design_prompt.txt"), encoding="utf-8").read()
    rd = "\n".join("  %s. %s;" % (k, v) for k, v in RANDURI.items())
    ec = "\n".join("- %s" % e for e in ecrane)
    return txt.replace("{RANDURI}", rd).replace("{ECRANE}", ec).replace("<DIRECTORUL_CAPTURILOR>", director)


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "porneste":
        return porneste()
    if argv[0] == "opreste":
        return opreste()
    if argv[0] == "prompt" and len(argv) >= 3:
        print(prompt(argv[2:], argv[1]))
        return 0
    if argv[0] == "lista":
        for e in registru():
            print("%-14s %-34s %s" % (e.get("nivel", "?"), e["nume"], e.get("firma", "")))
        return 0
    if argv[0] == "ecran" and len(argv) in (4, 5):
        return ecran(argv[1], argv[2], argv[3], director_png=argv[4] if len(argv) == 5 else None)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
