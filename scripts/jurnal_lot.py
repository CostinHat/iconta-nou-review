# -*- coding: utf-8 -*-
"""scripts/jurnal_lot.py — jurnalul lotului, scris de scripturi (comanda 16.1, pct.2). Fișier: <rădăcina depozitului principal>/.lot_jurnal.log (ignorat de git;
LOT_JURNAL îl mută în teste). Un rând = un eveniment, câmpuri separate prin TAB:
    lot, faza, eveniment (inceput|sfarsit), ora ISO, sha, rezultat, id-ul rulării, pid, detalii
O fază cu început fără sfârșit, al cărei proces nu mai trăiește, e marcată „intrerupt” de următorul script care scrie în jurnal (niciodată absentă sau verde).
Fazele obligatorii (aceeași listă la publica_lot.sh): pornire, hook, verificator, verificator_poarta, pytest, plasa_e2e, publicare.
  inceput <lot> <faza> [detalii]            scrie începutul, tipărește id-ul rulării
  sfarsit <lot> <faza> <id> <rezultat> [detalii]
  pornire <lot> [fișier-praguri]            scrie începutul și sfârșitul fazei „pornire”, cu hash-ul pragurilor și al scripturilor porții; fixează lotul curent
  rezumat <lot>                             duratele pe fază (copia din raport)
  lot-curent                                tipărește lotul (LOT, ramura lucru/lotNN-M, fișierul lot_curent din depozit)"""
import datetime
import fcntl
import os
import re
import subprocess
import sys
import time

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
import poarta_lib as L  # noqa: E402

FAZE_OBLIGATORII = ("pornire", "hook", "verificator", "poarta_verificator", "poarta_pytest", "poarta_plasa", "publicare")
#: scripturile porții a căror schimbare e vizibilă arhitectului prin hash în jurnal (pct.1a)
SCRIPTURI_POARTA = ("scripts/poarta_lot.sh", "scripts/publica_lot.sh", "scripts/baza_test.sh", "scripts/poarta_nucleu.txt", "scripts/plasa_16_2.manifest",
                    "scripts/poarta_clasifica.py", "scripts/poarta_lib.py", "conftest.py")


def _git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=cwd or os.getcwd(), capture_output=True, text=True).stdout.strip()


def comun(cwd=None):
    return _git("rev-parse", "--path-format=absolute", "--git-common-dir", cwd=cwd)


def cale_jurnal():
    if os.environ.get("LOT_JURNAL"):
        return os.environ["LOT_JURNAL"]
    return os.path.join(os.path.dirname(comun()), ".lot_jurnal.log")


def lot_curent():
    if os.environ.get("LOT"):
        return os.environ["LOT"]
    m = re.search(r"lot(\d+)-(\d+)", _git("symbolic-ref", "--short", "HEAD"))
    if m:
        return "%s.%s" % m.groups()
    try:
        return open(os.path.join(comun(), "lot_curent.txt"), encoding="utf-8").read().strip()
    except OSError:
        return "?"


def _sha():
    return _git("rev-parse", "HEAD")[:12] or "-"


def _viu(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ValueError):
        return False


def _citeste(cale):
    try:
        return [ln.rstrip("\n").split("\t") for ln in open(cale, encoding="utf-8") if ln.strip()]
    except OSError:
        return []


def _scrie(cale, campuri):
    os.makedirs(os.path.dirname(cale) or ".", exist_ok=True)
    with open(cale, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write("\t".join(str(c).replace("\t", " ").replace("\n", " ") for c in campuri) + "\n")


def _acum():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def marcheaza_intrerupte(cale=None):
    """Orice început fără sfârșit al cărui proces a murit primește un sfârșit „intrerupt” (la ora la care l-am constatat)."""
    cale = cale or cale_jurnal()
    rows = _citeste(cale)
    inchise = {r[6] for r in rows if len(r) > 6 and r[2] == "sfarsit"}
    for r in rows:
        if len(r) > 7 and r[2] == "inceput" and r[6] not in inchise and not _viu(r[7]):
            _scrie(cale, [r[0], r[1], "sfarsit", _acum(), r[4], "intrerupt", r[6], r[7], "constatat de următorul script"])
            inchise.add(r[6])


def inceput(lot, faza, detalii="", pid=None):
    """`pid` = procesul a cărui moarte înseamnă „întrerupt”: din linia de comandă, shell-ul care a chemat scriptul (nu python-ul de o clipă)."""
    cale = cale_jurnal()
    marcheaza_intrerupte(cale)
    id_ = "%d-%d" % (os.getpid(), time.time() * 1000)
    _scrie(cale, [lot, faza, "inceput", _acum(), _sha(), "-", id_, pid or os.getpid(), detalii])
    return id_


def sfarsit(lot, faza, id_, rezultat, detalii=""):
    cale = cale_jurnal()
    marcheaza_intrerupte(cale)
    pid = next((r[7] for r in _citeste(cale) if len(r) > 7 and r[6] == id_ and r[2] == "inceput"), os.getpid())
    _scrie(cale, [lot, faza, "sfarsit", _acum(), _sha(), rezultat, id_, pid, detalii])


def hash_scripturi(rad=None):
    rad = rad or _git("rev-parse", "--show-toplevel")
    return " ".join("%s=%s" % (os.path.basename(s), L.hash_fisier(os.path.join(rad, s))[:16]) for s in SCRIPTURI_POARTA)


def pornire(lot, praguri=None):
    rad = _git("rev-parse", "--show-toplevel")
    praguri = praguri or os.path.join(rad, "scripts", "praguri_%s.txt" % lot.replace(".", "_"))
    id_ = inceput(lot, "pornire", "praguri=%s praguri_sha256=%s" % (os.path.basename(praguri), L.hash_fisier(praguri)), pid=os.getpid())
    open(os.path.join(comun(), "lot_curent.txt"), "w", encoding="utf-8").write(lot + "\n")
    sfarsit(lot, "pornire", id_, "ok" if os.path.exists(praguri) else "lipsa_praguri", "scripturi_poarta: " + hash_scripturi(rad))
    return 0 if os.path.exists(praguri) else 1


def durate(lot, cale=None):
    """-> [(faza, id, început, sfârșit, rezultat, secunde)] în ordinea începuturilor."""
    cale = cale or cale_jurnal()
    marcheaza_intrerupte(cale)
    rows = [r for r in _citeste(cale) if r[0] == lot and len(r) > 6]
    sfarsituri = {r[6]: r for r in rows if r[2] == "sfarsit"}
    iesire = []
    for r in rows:
        if r[2] != "inceput":
            continue
        s = sfarsituri.get(r[6])
        sec = ""
        if s:
            sec = round((datetime.datetime.fromisoformat(s[3]) - datetime.datetime.fromisoformat(r[3])).total_seconds())
        iesire.append((r[1], r[6], r[3], s[3] if s else "-", s[5] if s else "intrerupt", sec))
    return iesire


def main(a):
    if not a:
        print(__doc__)
        return 2
    if a[0] == "lot-curent":
        print(lot_curent())
    elif a[0] == "inceput":
        print(inceput(a[1], a[2], " ".join(a[3:]), pid=os.getppid()))
    elif a[0] == "sfarsit":
        sfarsit(a[1], a[2], a[3], a[4], " ".join(a[5:]))
    elif a[0] == "pornire":
        return pornire(a[1], a[2] if len(a) > 2 else None)
    elif a[0] == "rezumat":
        for f, i, b, s, r, sec in durate(a[1]):
            print("%-20s %-10s %s -> %s  %ss" % (f, r, b, s, sec))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
