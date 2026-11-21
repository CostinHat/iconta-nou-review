"""Contract de referință. Adaptorii oficiali produc dovezile, exclusiv sub lacăt."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
import subprocess


class Refuz(ValueError):
    pass


@dataclass(frozen=True)
class Plan:
    lot: str
    c: str
    e: str
    fisier: str
    digest: str
    tabel: str
    coloana: str

    def __post_init__(self):
        for value, pattern in [(self.c, r"[a-f0-9]{40}"), (self.e, r"[a-f0-9]{40}"),
                               (self.digest, r"[a-f0-9]{64}"), (self.lot, r"[0-9]+(?:\.[0-9]+)*-[A-Z0-9]+"),
                               (self.fisier, r"core/migrare_[a-z0-9_]+\.py"),
                               (self.tabel, r"[a-z_][a-z0-9_]*"), (self.coloana, r"[a-z_][a-z0-9_]*")]:
            if not re.fullmatch(pattern, value):
                raise Refuz("Identificator invalid")


def verifica_git(root, plan, baza):
    """Verificări locale de identitate în directorul principal fixat de apelant."""
    root = Path(root).resolve(strict=True)
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])
    def line(*args):
        return git(*args).decode().strip()
    common = Path(line("rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()
    if common != root / ".git" or line("symbolic-ref", "--short", "HEAD") != "main":
        raise Refuz("Directorul principal si ramura main sunt obligatorii")
    if any(line("rev-parse", ref) != plan.e for ref in ("HEAD", "refs/heads/main", "refs/remotes/origin/main")):
        raise Refuz("Identitatea E difera")
    if not re.fullmatch(r"[a-f0-9]{40}", baza) or baza == plan.e:
        raise Refuz("Baza publicata lipseste")
    git("merge-base", "--is-ancestor", baza, plan.c)
    git("merge-base", "--is-ancestor", plan.c, plan.e)
    # Fișiere runtime legitime, de ex. lot_curent.txt, pot exista în directorul principal.
    # Verificăm toate fișierele urmărite și căile care pot încărca cod din proiect.
    if git("diff", "--name-only", "HEAD", "--") or git("ls-files", "--others", "--exclude-standard",
        "--", "core", "scripts", "*.py", ":(exclude)lot_curent.txt"):
        raise Refuz("Cod local diferit")
    if git("ls-files", "--others", "--ignored", "--exclude-standard", "--", ":(top,glob)*.py",
           ":(top,glob)core/**/*.py", ":(top,glob)scripts/**/*.py"):
        raise Refuz("Sursa Python locala ignorata poate schimba migrarea")
    cale = root / plan.fisier
    blob = git("show", plan.e + ":" + plan.fisier)
    if (not line("ls-tree", plan.e, "--", plan.fisier).startswith(("100644 blob ", "100755 blob "))
        or cale.resolve() != cale or not cale.is_file() or cale.read_bytes() != blob
        or sha256(blob).hexdigest() != plan.digest):
        raise Refuz("Identitatea fisierului difera")
    if plan.fisier.encode() not in git("diff", "--name-only", baza, plan.c, "--", plan.fisier).splitlines():
        raise Refuz("Migrarea nu apartine lotului")
    if git("show", plan.c + ":" + plan.fisier) != blob:
        raise Refuz("Migrarea s-a schimbat dupa poarta")
    with (common / "publica_verdicte.log").open(encoding="utf-8") as f:
        for row in f:
            cols = row.split()
            if (len(cols) == 6 and cols[:3] == ["PASS", plan.e, plan.lot]
                and cols[4] == "C=" + plan.c and cols[5].startswith("fisiere=")):
                return
    raise Refuz("Lipseste PASS pentru lot, E si C")


def situatie(plan, lipsa, drift):
    """Intrări citite în aceeași verificare din registru și audit_schema, sub ROLLBACK."""
    if lipsa is None or drift is None:
        raise Refuz("Stare necunoscuta")
    if not lipsa and not drift:
        return "pregatit"
    if plan is None or list(lipsa) != [(plan.fisier, plan.digest)]:
        raise Refuz("Set migrari diferit")
    for schema, raport in drift.items():
        if not re.fullmatch(r"tenant_[0-9]+", schema):
            raise Refuz("Schema neasteptata")
        if any(raport[k] for k in ("tabele_lipsa", "tip_dif", "nullable_dif", "triggere_lipsa")):
            raise Refuz("Deriva independenta")
        if raport["coloane_lipsa"] != {plan.tabel: [plan.coloana]}:
            raise Refuz("Alta coloana")
    return "asteapta_migrare"


@dataclass(frozen=True)
class Backup:
    e: str
    baza: str
    serviciu: str
    invocatie: str
    reusit: bool
    incheiat_ns: int
    digest: str


def permite_ddl(plan, aprobare, backup, inceput_ns, acum_ns):
    if aprobare != (plan.lot, plan.e, plan.fisier, plan.digest):
        raise Refuz("Acordul operatorului nu acopera operatia")
    if (not isinstance(backup, Backup) or backup.e != plan.e or backup.baza != "iconta_v2"
        or backup.serviciu != "iconta-backup.service" or not backup.invocatie or not backup.reusit
        or not inceput_ns <= backup.incheiat_ns <= acum_ns or not re.fullmatch(r"[0-9a-f]{64}", backup.digest)):
        raise Refuz("Backup neconfirmat pentru aceasta predare")


def confirma(plan, rand_registru, verificare, restart_rc, brate, toate_procesele, sentinela):
    if rand_registru != (plan.fisier, plan.digest, "rulata", plan.e) or verificare != "pregatit":
        raise Refuz("Registrul sau schema difera")
    if restart_rc != 0 or sentinela or not toate_procesele or tuple(brate) != (plan.e,) * 4:
        raise Refuz("Restartul sau four-way nu este confirmat")
    return "publicat"


def inchide_sub_lacat(plan, operatie, ultima_publicare, semnal, scrie_publicare, scrie_semnal):
    """Apelat sub lacătul unic al publicării după verificarea reală. Callback-urile citesc
    jurnalul/OPRIT din sistemul oficial. Operația adaugă numai părțile încă lipsă.
    Un rând al altei încercări sau un semnal contradictoriu necesită reconciliere."""
    identitate = (plan.lot, plan.e, operatie)
    publicare = ultima_publicare()
    terminal = semnal()
    if publicare not in (None, identitate) or terminal not in (None, (plan.lot,plan.e)):
        raise Refuz("Alta incheiere in jurnal sau in semnal")
    if terminal is not None and publicare is None:
        raise Refuz("Semnal fara publicare oficiala")
    if publicare is None:
        scrie_publicare()
    if ultima_publicare() != identitate:
        raise Refuz("Jurnalul nu confirma E")
    if terminal is None:
        scrie_semnal()
    if semnal() != (plan.lot, plan.e):
        raise Refuz("Semnal terminal neconfirmat")


# ======================================================================================================================
# [17.5-P0] ADAPTORII OFICIALI ai contractului de mai sus (care rămâne octet cu octet cel livrat, sha256 ec8998a4…).
# Numai biblioteca standard: scripts/publica_lot.sh îi cheamă și fără venv. Proprietarii:
#   deschide   — publica_lot.sh, după PASS și înaintea fast-forward: declarația din Git la C și E, rezervarea cheii lot+E+operație,
#                operația durabilă și recipisa <git-common-dir>/migrare_asteptata.json (specificația A.1–A.2);
#   asteapta   — publica_lot.sh, la 75 demonstrat de publica_prod.sh (B.4, B1 pct.1);
#   confirma   — `sh scripts/publica_lot.sh --confirma-migrare <lot> <E>`, singura continuare și singurul restart al unei operații
#                cu plan (D.8–D.9); recitește starea sub lacăt, încheie o singură dată prin jurnal_lot.sfarsit și incheie_lot.sh;
#   sub-lacat  — lacătul exclusiv al publicării, în directorul Git comun, pentru toate intrările care schimbă starea.
# Starea durabilă: <git-common-dir>/operatii-migrare/<E>/{rezervare.json, <operație>/{operatie.json, stadii.json, …}}, scrisă cu
# os.replace / link exclusiv, fsync pe fișier și director, permisiuni 0600 / 0700.
# ======================================================================================================================
import datetime as _dt
import fcntl as _fcntl
import json as _json
import os as _os
import signal as _signal
import sys as _sys
import time as _time
from contextlib import contextmanager as _contextmanager

DECLARATIE = "docs/dovezi/{lotf}/migrare_asteptata.json"
CHEI_DECLARATIE = {"lot", "fisier", "digest", "tabel", "coloana"}
CHEI_RECIPISA = ("lot", "fisier", "digest", "tabel", "coloana", "c", "e", "baza")
RECIPISA = "migrare_asteptata.json"
OPERATII = "operatii-migrare"
LACAT = "publica_migrare.lock"
TERMINALE = ("publicat", "nepublicat")
SENTINELE = ("FOUR_WAY_NEINCHIS", "RESTART_ESUAT", "PUBLICARE_STATIC_ESUATA", "RESTART_OPRIT_MIGRARE", "PUSH_MAIN_ESUAT",
             "PUSH_BACKUP_ESUAT")
#: rezultatele fazei „publicare” care încheie lotul (orice altceva decât „asteapta_migrare” e terminal)
INTERMEDIAR = "asteapta_migrare"


def lot_fisier(lot):
    return re.sub(r"[.\-]", "_", lot)


def _git(repo, *args, check=True):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if check and r.returncode:
        raise Refuz("git %s: %s" % (args[0], r.stderr.decode(errors="replace").strip()[:300]))
    return r


def _linie(repo, *args):
    return _git(repo, *args).stdout.decode().strip()


def comun(repo="."):
    return Path(_linie(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")).resolve()


def _fsync_dir(d):
    fd = _os.open(str(d), _os.O_RDONLY | _os.O_DIRECTORY)
    try:
        _os.fsync(fd)
    finally:
        _os.close(fd)


def _tmp(cale, date):
    cale.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    tmp = cale.with_name(".%s.%d.%d.tmp" % (cale.name, _os.getpid(), _time.time_ns()))
    fd = _os.open(str(tmp), _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL, 0o600)
    try:
        _os.write(fd, date)
        _os.fsync(fd)
    finally:
        _os.close(fd)
    return tmp


def scrie_atomic(cale, date):
    """Înlocuire atomică (os.replace), fsync pe fișier și pe director, 0600."""
    cale = Path(cale)
    _os.replace(_tmp(cale, date), cale)
    _fsync_dir(cale.parent)


def scrie_exclusiv(cale, date):
    """Creează fișierul numai dacă lipsește (link exclusiv); True = creat acum, False = exista deja (nu se suprascrie)."""
    cale = Path(cale)
    tmp = _tmp(cale, date)
    try:
        _os.link(tmp, cale)
        creat = True
    except FileExistsError:
        creat = False
    finally:
        _os.unlink(tmp)
    _fsync_dir(cale.parent)
    return creat


def canon(obj):
    return (_json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode()


def json_strict(raw):
    def perechi(p):
        if len(dict(p)) != len(p):
            raise Refuz("Cheie duplicata")
        return dict(p)
    try:
        obj = _json.loads(raw, object_pairs_hook=perechi)
    except ValueError as ex:
        raise Refuz("Document corupt: %s" % str(ex)[:120])
    if not isinstance(obj, dict):
        raise Refuz("Document corupt")
    return obj


def _acum_iso():
    return _dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _iso_utc(ns):
    return _dt.datetime.fromtimestamp(ns // 10**9, _dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def punct_proba(nume):
    """Numai calibrarea izolată (ICONTA_PROBA_INTRERUPE=<punct>): oprirea forțată a procesului în punctul numit (I10, I11)."""
    if _os.environ.get("ICONTA_PROBA_INTRERUPE") == nume:
        print("[proba] intrerupere %s pid=%d" % (nume, _os.getpid()), flush=True)
        _os.kill(_os.getpid(), _signal.SIGKILL)


# ---------- lacătul publicării (D.9) ----------
@_contextmanager
def lacat(common, cine):
    """Lacăt exclusiv în directorul Git comun. Un proces copil al deținătorului (PUBLICA_LACAT=<cale>) nu-l mai reașteaptă."""
    cale = Path(common) / LACAT
    if _os.environ.get("PUBLICA_LACAT") == str(cale):
        yield None
        return
    fd = _os.open(str(cale), _os.O_RDWR | _os.O_CREAT, 0o600)
    try:
        try:
            _fcntl.flock(fd, _fcntl.LOCK_EX | _fcntl.LOCK_NB)
        except BlockingIOError:
            _os.lseek(fd, 0, 0)
            detinator = _os.read(fd, 400).decode(errors="replace").strip()
            print(_json.dumps(dict(eveniment="concurenta", pid=_os.getpid(), cine=cine, detinator=detinator),
                              ensure_ascii=False), flush=True)
            _fcntl.flock(fd, _fcntl.LOCK_EX)
        _os.ftruncate(fd, 0)
        _os.lseek(fd, 0, 0)
        _os.write(fd, ("pid=%d %s la=%s\n" % (_os.getpid(), cine, _acum_iso())).encode())
        _os.environ["PUBLICA_LACAT"] = str(cale)
        yield cale
    finally:
        if _os.environ.get("PUBLICA_LACAT") == str(cale):
            del _os.environ["PUBLICA_LACAT"]
        _os.close(fd)


# ---------- declarația lotului și PASS (A.1–A.2) ----------
def citeste_pass(common, e, lot):
    """C din ultimul `PASS <E> <lot> <ora> C=<C> fisiere=…` scris de scripts/publica_lot.py (tripleta exactă lot/C/E)."""
    try:
        randuri = (Path(common) / "publica_verdicte.log").read_text(encoding="utf-8").splitlines()
    except OSError:
        raise Refuz("Lipseste jurnalul PASS")
    c = None
    for rand in randuri:
        cols = rand.split()
        if len(cols) == 6 and cols[:3] == ["PASS", e, lot] and cols[4].startswith("C=") and cols[5].startswith("fisiere="):
            c = cols[4][2:]
    if not c or not re.fullmatch(r"[a-f0-9]{40}", c):
        raise Refuz("Lipseste PASS pentru lot si E")
    return c


def declaratie(repo, sha, lot):
    """Documentul docs/dovezi/<lot>/migrare_asteptata.json din obiectele Git ale lui `sha`; None = lot fără migrare declarată."""
    cale = DECLARATIE.format(lotf=lot_fisier(lot))
    ls = _git(repo, "ls-tree", sha, "--", cale).stdout
    if not ls:
        return None
    if not ls.startswith((b"100644 blob ", b"100755 blob ")):
        raise Refuz("Declaratia nu e fisier regulat")
    obj = json_strict(_git(repo, "show", "%s:%s" % (sha, cale)).stdout)
    if set(obj) != CHEI_DECLARATIE or not all(isinstance(v, str) for v in obj.values()):
        raise Refuz("Declaratia are alte campuri")
    if obj["lot"] != lot:
        raise Refuz("Declaratia altui lot")
    return obj


def plan_din_git(repo, lot, c, e, baza):
    """Planul migrării declarate, verificat pe obiectele Git (baza ≺ C ≼ E, același blob regulat pe C și E, digest, apartenența
    la lot); None = nicio declarație la C și la E (traseul obișnuit). Un plan corupt sau discordant e Refuz."""
    dc, de = declaratie(repo, c, lot), declaratie(repo, e, lot)
    if dc is None and de is None:
        return None
    if dc != de:
        raise Refuz("Declaratia difera intre C si E")
    plan = Plan(lot, c, e, dc["fisier"], dc["digest"], dc["tabel"], dc["coloana"])
    if not re.fullmatch(r"[a-f0-9]{40}", baza) or baza in (c, e):
        raise Refuz("Baza publicata lipseste")
    for a, b in ((baza, c), (c, e)):
        if _git(repo, "merge-base", "--is-ancestor", a, b, check=False).returncode:
            raise Refuz("Ordinea baza, C, E nu e respectata")
    blobs = []
    for sha in (c, e):
        if not _git(repo, "ls-tree", sha, "--", plan.fisier).stdout.startswith((b"100644 blob ", b"100755 blob ")):
            raise Refuz("Migrarea declarata lipseste din Git")
        blobs.append(_git(repo, "show", "%s:%s" % (sha, plan.fisier)).stdout)
    if blobs[0] != blobs[1]:
        raise Refuz("Migrarea s-a schimbat dupa poarta")
    if sha256(blobs[0]).hexdigest() != plan.digest:
        raise Refuz("Digestul declarat difera de fisier")
    if plan.fisier.encode() not in _git(repo, "diff", "--name-only", baza, c, "--", plan.fisier).stdout.splitlines():
        raise Refuz("Migrarea nu apartine lotului")
    return plan


# ---------- operația durabilă ----------
def dir_operatie(common, e, operatie):
    if not (re.fullmatch(r"[a-f0-9]{40}", e) and re.fullmatch(r"[0-9]+-[0-9]+", operatie)):
        raise Refuz("Cheie de operatie invalida")
    return Path(common) / OPERATII / e / operatie


def stadii(d):
    try:
        return json_strict((Path(d) / "stadii.json").read_bytes())["stadii"]
    except FileNotFoundError:
        return []


def are_stadiu(d, nume):
    return any(s.get("stadiu") == nume for s in stadii(d))


def adauga_stadiu(d, nume, **detalii):
    lista = stadii(d)
    lista.append(dict(stadiu=nume, la=_acum_iso(), pid=_os.getpid(), **detalii))
    scrie_atomic(Path(d) / "stadii.json", canon(dict(stadii=lista)))
    print("[operatie] stadiu %s %s" % (nume, Path(d).name), file=_sys.stderr, flush=True)


def _deschisa(common, e):
    """Operația rezervată pentru E e încă deschisă (fără stadiu terminal)?"""
    try:
        rez = json_strict((Path(common) / OPERATII / e / "rezervare.json").read_bytes())
        d = dir_operatie(common, e, rez["operatie"])
    except (OSError, KeyError, Refuz):
        return False
    return not any(are_stadiu(d, t) for t in TERMINALE)


def deschide(repo_lot, lot, e, operatie):
    """publica_lot.sh, sub lacăt, după PASS și înaintea fast-forward. None = lot fără plan; altfel Plan, cu operația și recipisa scrise."""
    common = comun(repo_lot)
    if _linie(repo_lot, "rev-parse", "HEAD") != e:
        raise Refuz("HEAD-ul lotului difera de E")
    baza = _linie(common.parent, "rev-parse", "refs/heads/main")
    c = citeste_pass(common, e, lot)
    plan = plan_din_git(repo_lot, lot, c, e, baza)
    if plan is None:
        return None
    d = dir_operatie(common, e, operatie)
    rezervare = Path(common) / OPERATII / e / "rezervare.json"
    date_rez = canon(dict(versiune=1, lot=lot, e=e, operatie=operatie))
    if not scrie_exclusiv(rezervare, date_rez):
        veche = json_strict(rezervare.read_bytes())
        vd = dir_operatie(common, e, veche.get("operatie", ""))
        if are_stadiu(vd, "nepublicat") and not are_stadiu(vd, "publicat"):
            scrie_atomic(rezervare, date_rez)   # o încercare anterioară încheiată nepublicat; noua operație o înlocuiește
        else:
            raise Refuz("E are deja operatia %s a lotului %s" % (veche.get("operatie"), veche.get("lot")))
    ns = _time.time_ns()
    if not scrie_exclusiv(d / "operatie.json", canon(dict(versiune=1, lot=lot, c=c, e=e, baza=baza, fisier=plan.fisier,
                                                        digest=plan.digest, tabel=plan.tabel, coloana=plan.coloana,
                                                        operatie=operatie, deschisa_la=_iso_utc(ns), deschisa_ns=ns))):
        raise Refuz("Operatia exista deja")
    adauga_stadiu(d, "deschisa")
    recipisa = dict(lot=lot, fisier=plan.fisier, digest=plan.digest, tabel=plan.tabel, coloana=plan.coloana, c=c, e=e, baza=baza)
    cale = Path(common) / RECIPISA
    try:
        veche = _json.loads(cale.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        veche = None
    if veche != recipisa:
        if isinstance(veche, dict) and isinstance(veche.get("e"), str) and veche["e"] != e and _deschisa(common, veche["e"]):
            adauga_stadiu(d, "nepublicat", motiv="alta operatie in asteptare")
            raise Refuz("Alta operatie de migrare in asteptare: lotul %s pe %s" % (veche.get("lot"), veche.get("e")))
        scrie_atomic(cale, canon(recipisa))
    return plan


def operatie_curenta(repo, e, lot=None):
    """(plan, operație, director) pentru E, recitite din starea durabilă și comparate cu recipisa și cu obiectele Git."""
    common = comun(repo)
    try:
        rez = json_strict((common / OPERATII / e / "rezervare.json").read_bytes())
    except FileNotFoundError:
        raise Refuz("Nicio operatie de migrare pentru E")
    if rez.get("e") != e or (lot is not None and rez.get("lot") != lot):
        raise Refuz("Operatia rezervata pentru E e a altui lot")
    d = dir_operatie(common, e, rez.get("operatie", ""))
    raw = (d / "operatie.json").read_bytes()
    o = json_strict(raw)
    if raw != canon(o) or (o.get("lot"), o.get("e"), o.get("operatie")) != (rez["lot"], e, rez["operatie"]):
        raise Refuz("Operatia durabila difera")
    try:
        rec = json_strict((common / RECIPISA).read_bytes())
    except FileNotFoundError:
        raise Refuz("Recipisa lipseste")
    if rec != {k: o[k] for k in CHEI_RECIPISA}:
        raise Refuz("Recipisa difera de operatie")
    plan = plan_din_git(repo, o["lot"], o["c"], e, o["baza"])
    if plan is None or (plan.fisier, plan.digest, plan.tabel, plan.coloana) != (o["fisier"], o["digest"], o["tabel"], o["coloana"]):
        raise Refuz("Planul din Git difera de operatie")
    return plan, o, d


def plan_pentru_head(repo):
    """Planul operației deschise pentru HEAD (rulatorul și publica_prod.sh); None = HEAD fără recipisă de migrare."""
    e = _linie(repo, "rev-parse", "HEAD")
    try:
        rec = json_strict((comun(repo) / RECIPISA).read_bytes())
    except FileNotFoundError:
        return None
    if rec.get("e") != e:
        return None
    return operatie_curenta(repo, e)


# ---------- jurnalul oficial și semnalul OPRIT, citite din sursă ----------
def _jurnal(repo):
    if _os.environ.get("LOT_JURNAL"):
        return Path(_os.environ["LOT_JURNAL"])
    return comun(repo).parent / ".lot_jurnal.log"


def randuri_publicare(repo, lot):
    try:
        rows = [ln.rstrip("\n").split("\t") for ln in _jurnal(repo).read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return []
    return [r for r in rows if len(r) > 6 and r[0] == lot and r[1] == "publicare" and r[2] == "sfarsit"]


def _detalii(r):
    return dict(x.split("=", 1) for x in (r[8] if len(r) > 8 else "").split() if "=" in x)


def ultima_publicare(repo, lot, e):
    """Identitatea (lot, E, operație) a rândului «publicare sfarsit publicat» al lotului; None = niciunul. Două rânduri publicat,
    sau unul care nu numește E complet (detalii) cu SHA-ul prescurtat al jurnalului egal cu E[:12], sunt Refuz."""
    pub = [r for r in randuri_publicare(repo, lot) if r[5] == "publicat"]
    if not pub:
        return None
    if len(pub) > 1:
        raise Refuz("Doua randuri publicat pentru lot")
    det = _detalii(pub[0])
    if det.get("e") != e or pub[0][4] != e[:12]:
        return (lot, pub[0][4], det.get("operatie"))
    return (lot, det["e"], det.get("operatie"))


def _dir_oprit():
    return Path(_os.environ.get("OPRIT_DIR") or _os.path.expanduser("~/ghid_incoming"))


def semnal(lot):
    """(lot, sha) din OPRIT_<lot>.txt (și din oprite/), None = absent; un semnal nepublicat sau două contradictorii = Refuz."""
    gasite = set()
    for f in (_dir_oprit() / ("OPRIT_%s.txt" % lot), _dir_oprit() / "oprite" / ("OPRIT_%s.txt" % lot)):
        try:
            parti = f.read_text(encoding="utf-8").split()
        except OSError:
            continue
        # «OPRIT — gata: <nr> <stare> <sha> <ora>»
        if len(parti) < 6 or parti[3] != lot:
            raise Refuz("Semnal OPRIT ilizibil")
        gasite.add((parti[4], parti[5]))
    if not gasite:
        return None
    if len(gasite) > 1 or next(iter(gasite))[0] != "publicat":
        raise Refuz("Semnal OPRIT contradictoriu sau nepublicat")
    return (lot, next(iter(gasite))[1])


def _py(repo):
    p = Path(repo) / "venv/bin/python"
    return str(p) if p.exists() else _sys.executable


def jurnal_inceput(repo, lot, faza, detalii=""):
    r = subprocess.run([_py(repo), "scripts/jurnal_lot.py", "inceput", lot, faza, detalii], cwd=repo, capture_output=True, text=True)
    if r.returncode:
        raise Refuz("Jurnalul nu a inregistrat inceputul: %s" % r.stderr.strip()[:200])
    return r.stdout.strip()


def jurnal_sfarsit(repo, lot, faza, id_, rezultat, detalii=""):
    r = subprocess.run([_py(repo), "scripts/jurnal_lot.py", "sfarsit", lot, faza, id_, rezultat, detalii], cwd=repo,
                       capture_output=True, text=True)
    if r.returncode:
        raise Refuz("Jurnalul nu a inregistrat sfarsitul: %s" % r.stderr.strip()[:200])


# ---------- brațele publicării, citite acum (D.8) ----------
def brate_publicare(repo, e, operatie):
    """((HEAD, origin/main la remote, ref-ul inițial al backupului Git, toți workerii), toți_workerii_la_E, sentinelă, static la E)."""
    import canal_migrare as _canal
    head = _linie(repo, "rev-parse", "HEAD")
    r = _git(repo, "ls-remote", "--exit-code", "--refs", "origin", "refs/heads/main", check=False)
    remote = r.stdout.decode().split("\t")[0].strip() if r.returncode == 0 else "-"
    try:
        ref = _canal.ref_confirmat(repo, e, operatie)
        bk = e
        print("[confirmare] ref_backup %s = %s (ref-ul inițial al operației %s, verificat la remote)" % (ref, e, operatie), flush=True)
    except (OSError, ValueError, subprocess.CalledProcessError) as ex:
        bk = "-"
        print("[confirmare] ref_backup neconfirmat: %s" % str(ex).splitlines()[0][:200] if str(ex) else "[confirmare] ref_backup neconfirmat",
              flush=True)
    w = subprocess.run([_py(repo), "scripts/toate_poarta_head.py", e], cwd=repo, capture_output=True, text=True)
    print((w.stdout + w.stderr).strip(), flush=True)
    toate = w.returncode == 0
    git_dir = comun(repo)
    sentinela = [s for s in SENTINELE if (git_dir / s).exists()]
    try:
        static = _json.loads((Path(repo).resolve().parent / "iconta_publicat/static/.publicat.json").read_text())["commit"]
    except (OSError, ValueError, KeyError, TypeError):
        static = None
    return (head, remote, bk, e if toate else "-"), toate, sentinela, static


def _stare_registru(repo, e, operatie):
    """Ieșirea lui `core.migrari_registru verifica <E> --confirmare <operație>`: (cod, dicționar JSON de pe ultima linie)."""
    r = subprocess.run([_py(repo), "-m", "core.migrari_registru", "verifica", e, "--confirmare", operatie], cwd=repo,
                       capture_output=True, text=True)
    print((r.stdout + r.stderr).strip(), flush=True)
    try:
        date = _json.loads(r.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        date = {}
    return r.returncode, date


def confirma_operatie(repo, argv, lot, e):
    """`sh scripts/publica_lot.sh --confirma-migrare <lot> <E>` din depozitul principal (D.8–D.9). Coduri: 0 publicat (sau deja
    publicat), 75 încă în așteptare (migrarea nerulată), 3 reconciliere (rezultat ambiguu), alt nenul = refuz / eșec real."""
    repo = Path(repo).resolve()
    common = comun(repo)
    if common != repo / ".git" or _linie(repo, "symbolic-ref", "--short", "HEAD") != "main":
        raise Refuz("Continuarea se face din depozitul principal, pe main")
    if _linie(repo, "rev-parse", "HEAD") != e:
        raise Refuz("HEAD-ul depozitului principal difera de E")
    print(_json.dumps(dict(eveniment="revenire", argv=argv, pid=_os.getpid(), lot=lot, e=e, la=_acum_iso())), flush=True)
    with lacat(common, "confirma-migrare lot=%s e=%s" % (lot, e)):
        plan, o, d = operatie_curenta(repo, e, lot)
        op = o["operatie"]
        intrare = dict(argv=argv, pid=_os.getpid(), operatie=op, lot=lot, e=e, la=_acum_iso())
        cale_intrari = d / "confirmari.jsonl"
        with open(cale_intrari, "a", encoding="utf-8") as f:
            f.write(_json.dumps(intrare, ensure_ascii=True) + "\n")
            f.flush()
            _os.fsync(f.fileno())
        print("[confirmare] intrarea operatorului: %s" % cale_intrari, flush=True)
        print(_json.dumps(intrare, ensure_ascii=True), flush=True)

        def scrie_publicare():
            jurnal_sfarsit(repo, lot, "publicare", id_conf, "publicat", "e=%s operatie=%s" % (e, op))
            print("[confirmare] jurnal: publicare sfarsit publicat e=%s operatie=%s" % (e, op), flush=True)
            punct_proba("dupa_jurnal")

        def scrie_semnal():
            subprocess.run(["sh", "scripts/incheie_lot.sh", lot, "publicat", e], cwd=repo, check=False)
            punct_proba("dupa_oprit")

        identitate = (lot, e, op)
        publicare, terminal = ultima_publicare(repo, lot, e), semnal(lot)
        if publicare == identitate and terminal == (lot, e):
            print("[confirmare] rezultat existent: publicat %s pe %s (operatia %s); nimic de refacut" % (lot, e, op), flush=True)
            return 0
        rez = randuri_publicare(repo, lot)
        if publicare is None and rez and rez[-1][5] not in (INTERMEDIAR, "intrerupt"):
            raise Refuz("Operatia s-a incheiat %s; nu se reia" % rez[-1][5])
        if any(are_stadiu(d, t) for t in ("nepublicat", "restart_esuat")) and publicare is None:
            raise Refuz("Operatia s-a incheiat nepublicat")
        if publicare is not None:   # jurnalul are deja «publicat» (căderea dintre jurnal și semnal): numai efectul lipsă, fără rând nou
            id_conf = None
            reguli_inchide(plan, op, repo, lot, e, scrie_publicare, scrie_semnal)
            adauga_stadiu(d, "publicat", reluare="semnal")
            print("publicat %s pe %s" % (lot, e), flush=True)
            return 0
        id_conf = jurnal_inceput(repo, lot, "publicare", "confirmare e=%s operatie=%s" % (e, op))
        cod, st = _stare_registru(repo, e, op)
        rand = tuple(st.get("rand") or ()) or None
        if st.get("stare") == "asteapta_migrare":
            jurnal_sfarsit(repo, lot, "publicare", id_conf, INTERMEDIAR, "e=%s operatie=%s motiv=migrare_nerulata" % (e, op))
            print("AȘTEAPTĂ MIGRAREA %s pe %s — operația %s (migrarea %s nu e rulată)" % (lot, e, op, plan.fisier), flush=True)
            return 75
        if cod != 0:
            jurnal_sfarsit(repo, lot, "publicare", id_conf, INTERMEDIAR, "e=%s operatie=%s motiv=registru" % (e, op))
            raise Refuz("Registrul sau schema nu confirma migrarea: %s" % st.get("motiv", "cod %d" % cod))
        if are_stadiu(d, "restart_cerut") and not are_stadiu(d, "restart_ok"):
            # căderea după cererea restartului: se adoptă numai un restart atestat de serviciu și de toți workerii la E
            brate, toate, sentinela, static = brate_publicare(repo, e, op)
            try:
                confirma(plan, rand, "pregatit", 0, brate, toate, False)
            except Refuz:
                jurnal_sfarsit(repo, lot, "publicare", id_conf, INTERMEDIAR, "e=%s operatie=%s motiv=reconciliere" % (e, op))
                adauga_stadiu(d, "reconciliere", motiv="restart cerut fara dovada rezultatului")
                print("[confirmare] RECONCILIERE: restartul a fost cerut, dar serviciul și workerii nu atestă E; "
                      "nu se repornește în orb (brate=%s)" % (brate,), flush=True)
                return 3
            adauga_stadiu(d, "restart_ok", adoptat=True)
        if not are_stadiu(d, "restart_ok"):
            adauga_stadiu(d, "restart_cerut")
            id_r = jurnal_inceput(repo, lot, "restart", "confirmare e=%s operatie=%s" % (e, op))
            rs = subprocess.run(["sh", "scripts/publica_prod.sh", "--ref-migrare", e, op], cwd=repo).returncode
            jurnal_sfarsit(repo, lot, "restart", id_r, "ok" if rs == 0 else "esec")
            if rs != 0 and (common / "RESTART_ESUAT").exists():
                # avaria restartului: eșec real, terminal nepublicat (I08); nu se reia automat
                adauga_stadiu(d, "restart_esuat", rc=rs)
                adauga_stadiu(d, "nepublicat", motiv="restartul productiei nu s-a facut")
                jurnal_sfarsit(repo, lot, "publicare", id_conf, "esec_restart", "e=%s operatie=%s" % (e, op))
                subprocess.run(["sh", "scripts/incheie_lot.sh", lot, "nepublicat", "-",
                                "restartul productiei nu s-a facut dupa migrare"], cwd=repo, check=False)
                print("[confirmare] restartul productiei NU s-a facut (rc=%d); nepublicat" % rs, flush=True)
                return rs
            if rs != 0:
                # restartul a fost cerut, dar statica, four-way-ul sau workerii nu confirmă E: confirmare refuzată; o continuare ulterioară
                # adoptă restartul numai dacă serviciul și toți workerii atestă E (fără al doilea restart)
                adauga_stadiu(d, "confirmare_refuzata", rc=rs)
                jurnal_sfarsit(repo, lot, "publicare", id_conf, INTERMEDIAR, "e=%s operatie=%s motiv=confirmare_refuzata" % (e, op))
                print("[confirmare] confirmare refuzată: statica, four-way-ul sau workerii nu confirmă E (rc=%d); nepublicat" % rs, flush=True)
                return rs
            adauga_stadiu(d, "restart_ok")
            punct_proba("dupa_restart")
        brate, toate, sentinela, static = brate_publicare(repo, e, op)
        if static != e:
            sentinela = sentinela + ["static=%s" % static]
        try:
            confirma(plan, rand, "pregatit", 0, brate, toate, bool(sentinela))
        except Refuz as ex:
            jurnal_sfarsit(repo, lot, "publicare", id_conf, INTERMEDIAR, "e=%s operatie=%s motiv=confirmare" % (e, op))
            raise Refuz("%s: brate=%s workeri=%s sentinele=%s" % (ex, brate, toate, sentinela))
        adauga_stadiu(d, "confirmat")
        reguli_inchide(plan, op, repo, lot, e, scrie_publicare, scrie_semnal)
        adauga_stadiu(d, "publicat")
        print("publicat %s pe %s" % (lot, e), flush=True)
        return 0


def reguli_inchide(plan, op, repo, lot, e, scrie_publicare, scrie_semnal):
    """inchide_sub_lacat pe jurnalul oficial și pe fișierul OPRIT, citite din sursă la fiecare pas."""
    inchide_sub_lacat(plan, op, lambda: ultima_publicare(repo, lot, e), lambda: semnal(lot), scrie_publicare, scrie_semnal)


def _main_adaptor(args):
    if args[:1] == ["sub-lacat"] and len(args) > 1:
        with lacat(comun("."), "publica_lot pid=%d" % _os.getppid()):
            return subprocess.call(args[1:])
    if args[:1] == ["deschide"] and len(args) == 4:
        plan = deschide(Path.cwd(), *args[1:])
        print("plan" if plan else "fara_plan")
        return 0
    if args[:1] == ["asteapta"] and len(args) == 3:
        _plan, _o, d = operatie_curenta(comun(".").parent, args[1])
        if _o["operatie"] != args[2]:
            raise Refuz("Alta operatie")
        adauga_stadiu(d, INTERMEDIAR)
        return 0
    if args[:1] == ["incheie"] and len(args) == 4:
        _plan, _o, d = operatie_curenta(comun(".").parent, args[1])
        if _o["operatie"] == args[2]:
            adauga_stadiu(d, "nepublicat", motiv=args[3])
        return 0
    if args[:1] == ["confirma"] and len(args) == 5 and args[2] == "--confirma-migrare":
        # argv-ul operatorului, așa cum l-a primit scripts/publica_lot.sh: <script> --confirma-migrare <lot> <E>
        return confirma_operatie(Path.cwd(), args[1:], args[3], args[4])
    print("utilizare: reguli_publicare_migrare.py sub-lacat <comanda…> | deschide <lot> <E> <operatie> | asteapta <E> <operatie> | "
          "incheie <E> <operatie> <motiv> | confirma <script> --confirma-migrare <lot> <E>", file=_sys.stderr)
    return 2


if __name__ == "__main__":
    try:
        _sys.exit(_main_adaptor(_sys.argv[1:]))
    except Refuz as _ex:
        print("[publicare] REFUZ: %s" % _ex, file=_sys.stderr, flush=True)
        _sys.exit(1)
