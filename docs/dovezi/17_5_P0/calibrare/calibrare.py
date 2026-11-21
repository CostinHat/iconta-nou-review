"""Driverul calibrării 17.5-P0 (I01–I12). Rulează numai sub lanseaza_calibrare_P0.py (spațiu Linux privat, /lab), pe date sintetice.

Intrările OFICIALE (din sursa exportată a lotului, neschimbate): sh scripts/publica_lot.sh (prima publicare), python -m core.migrari_registru
backup-inainte / ruleaza --productie (rulatorul), sh scripts/publica_lot.sh --confirma-migrare <lot> <E> (continuarea), hook-urile post-commit,
four-way, pre-push, reference-transaction, scripts/publica_prod.sh, scripts/jurnal_lot.py, scripts/incheie_lot.sh, scripts/publica_static.py,
scripts/toate_poarta_head.py, cititorul de predecesori conditii_predecesori.py --pornire. Baza: un cluster PostgreSQL 16 privat (initdb), DB iconta_v2.

MARGINILE SIMULATE (dubluri în /lab/work/dubluri, fiecare apel jurnalizat cu ns): systemctl (show), journalctl, restartul (PUBLICA_PROD_RESTART:
oprește workerii vechi și pornește doi workeri reali care se înregistrează prin core.instante), alerta (ALERTA_CMD), tmux, sudo, node (--check),
date (+%Y-%m-%d, numai pentru I12 peste miezul nopții). Backupul manual al lui Costin = pg_dump real al clusterului privat + rândurile backup.log +
jurnalul PID 1 simulat. Acordul lui Costin = semnătură OpenSSH reală cu o cheie EFEMERĂ (ancora din baza de calibrare o numește).
LIMITE: scripts/publica_lot.py (verificatorul lotului: ZIP, faze, dovezi) e înlocuit în baza de calibrare cu o dublură care scrie PASS pentru tripleta
lot/C/E; poarta pe C nu rulează în VM: «dovada unică a porții pe C» e rândul VERDE scris o dată în starea inițială (șablon), copiat în fiecare caz.
Urmele: /lab/out/<Ixx-varianta>.jsonl + /lab/out/<Ixx-varianta>/ (fișierele brute citate); judecătorul: verifica_parcurs_publicare.py /lab/out.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import time

LAB = Path('/lab'); W = LAB / 'work'; HOME = LAB / 'home'; OUT = LAB / 'out'
REPO = HOME / 'iconta_nou'; WT = HOME / 'iconta_lot17_5p'; GHID = HOME / 'ghid_incoming'; PUBL = HOME / 'iconta_publicat'
GITD = LAB / 'git'; ORIGIN = GITD / 'origin.git'
DUB = W / 'dubluri'; ST = W / 'stare'; SABLON = W / 'sablon'; CHEI = W / 'chei'; SOCK = W / 'socket'; CLUSTER = W / 'cluster'
PGB = Path('/usr/lib/postgresql/16/bin'); PORT = 15432; DB = 'iconta_v2'
BK = Path('/var/backups/iconta')
LOT = '17.5-P'; LOTF = '17_5_P'; SUCC = '17_5_Q'
MIGR = 'core/migrare_cal_bon_cui.py'; DECL = 'docs/dovezi/17_5_P/migrare_asteptata.json'
URL = 'postgresql://calibrare@127.0.0.1:%d/%s' % (PORT, DB)
PG_LOG = W / 'postgres.log'

ENV = dict(HOME=str(HOME), PATH=str(DUB) + ':/usr/bin:/bin', GIT_ALLOW_PROTOCOL='file', GIT_CONFIG_NOSYSTEM='1',
           GIT_CONFIG_GLOBAL='/dev/null', LC_ALL='C.UTF-8', TZ='Europe/Bucharest', LOT_JURNAL=str(REPO / '.lot_jurnal.log'),
           JURNAL_PROBA=str(REPO / '.lot_jurnal.log'), OPRIT_DIR=str(GHID), GHID_PROBA=str(GHID),
           PUBLICA_PROD_PASS_LOG=str(REPO / '.git/publica_verdicte.log'), PUBLICA_PROD_RESTART=str(DUB / 'restart'),
           ALERTA_CMD=str(DUB / 'alerta'), ICONTA_PROBA_BACKUP_PROPRIETAR='calibrare', PYTHONDONTWRITEBYTECODE='1',
           GIT_AUTHOR_NAME='Calibrare', GIT_AUTHOR_EMAIL='calibrare@example.invalid', GIT_COMMITTER_NAME='Calibrare',
           GIT_COMMITTER_EMAIL='calibrare@example.invalid')
for k in ('CAL_NET_HOST', 'CAL_PID_HOST', 'CAL_MNT_HOST'):
    ENV[k] = os.environ[k]


def cere(ok, mesaj):
    if not ok:
        raise RuntimeError(mesaj)


def sh(*args, cwd=None, env=None, check=True, inp=None):
    r = subprocess.run([str(a) for a in args], cwd=cwd, env=env or ENV, capture_output=True, text=True, input=inp)
    if check and r.returncode:
        raise RuntimeError('%s: rc=%d\n%s%s' % (args[:3], r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
    return r.stdout


def git(*args, cwd=REPO, check=True):
    return sh('git', '-C', cwd, *args, check=check).strip()


def psql(sql, db=DB):
    return sh(PGB / 'psql', '-X', '-q', '-A', '-t', '-v', 'ON_ERROR_STOP=1', '-h', SOCK, '-p', PORT, '-U', 'calibrare', '-d', db, '-c', sql)


def ns():
    return time.time_ns()


# ---------------------------------------------------------------- dublurile marginilor
DUBLURI_PY = {
    'systemctl': r'''
import json, os, sys, time
ST = "/lab/work/stare"
a = sys.argv[1:]
with open("/lab/work/obs/systemctl.log", "a") as f:
    f.write("%d %s\n" % (time.time_ns(), json.dumps(dict(argv=a, pid=os.getpid()))))
if not a or a[0] != "show":
    sys.exit(1)
unit = next(x for x in a[1:] if not x.startswith("-") and a[a.index(x) - 1] != "-p")
props = [a[i + 1] for i, x in enumerate(a) if x == "-p"]
p = os.path.join(ST, unit + ".json")
try:
    st = json.load(open(p))
except OSError:
    sys.exit(1)
if unit == "iconta-backup.service" and st.get("inlocuire"):
    n = st.get("arataturi", 0) + 1
    st["arataturi"] = n
    if n > st["inlocuire"]["dupa"]:
        st["InvocationID"] = st["inlocuire"]["id"]
    json.dump(st, open(p + ".tmp", "w")); os.replace(p + ".tmp", p)
for k in props:
    v = st.get(k, "")
    print(v if "--value" in a else "%s=%s" % (k, v))
''',
    'journalctl': r'''
import json, os, sys, time
a = sys.argv[1:]
with open("/lab/work/obs/journalctl.log", "a") as f:
    f.write("%d %s\n" % (time.time_ns(), json.dumps(dict(argv=a, pid=os.getpid()))))
filtre = dict(x.split("=", 1) for x in a if "=" in x and not x.startswith("-"))
try:
    rows = [json.loads(l) for l in open("/lab/work/stare/journal.jsonl")]
except OSError:
    rows = []
for r in rows:
    if all(str(r.get(k)) == v for k, v in filtre.items()):
        print(json.dumps(r))
''',
    'restart': r'''
import json, os, signal, subprocess, sys, time
ST = "/lab/work/stare"
op = os.environ.get("PUBLICA_OPERATIE_MIGRARE", "")
with open("/lab/work/obs/restart.log", "a") as f:
    f.write("%d %s\n" % (time.time_ns(), json.dumps(dict(argv=sys.argv, pid=os.getpid(), ppid=os.getppid(), cwd=os.getcwd(),
                                                          operatie=op or None, eticheta=("restart" if op else "restart_legacy")))))
mod = json.load(open(os.path.join(ST, "restart.json"))).get("mod", "ok")
if mod == "esec":
    print("Job for iconta-nou.service failed (simulat)", file=sys.stderr); sys.exit(1)
try:
    for pid in json.load(open(os.path.join(ST, "workers.json"))):
        try: os.kill(pid, signal.SIGTERM)
        except ProcessLookupError: pass
except OSError:
    pass
time.sleep(0.5)
sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
shas = {"ok": [sha, sha], "worker_lipsa": [sha], "worker_alt": [sha, "0" * 40]}[mod]
pids = []
for s in shas:
    p = subprocess.Popen(["/usr/bin/python3", "-I", "-B", "/lab/work/worker.py", s], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=open("/lab/work/obs/worker.err", "a"))
    pids.append(p.pid)
json.dump(pids, open(os.path.join(ST, "workers.json"), "w"))
u = json.load(open(os.path.join(ST, "iconta-nou.json")))
time.sleep(1.5)
u["ActiveEnterTimestamp"] = time.strftime("%a %Y-%m-%d %H:%M:%S %Z")
json.dump(u, open(os.path.join(ST, "iconta-nou.json"), "w"))
''',
    'alerta': r'''
import json, os, sys, time
with open("/lab/work/obs/alerta.log", "a") as f:
    f.write("%d %s\n" % (time.time_ns(), json.dumps(dict(argv=sys.argv[1:], pid=os.getpid()), ensure_ascii=False)))
''',
    'node': r'''
import json, os, sys, time
with open("/lab/work/obs/node.log", "a") as f:
    f.write("%d %s\n" % (time.time_ns(), json.dumps(dict(argv=sys.argv[1:]))))
sys.exit(int(open("/lab/work/stare/node").read().strip() or 0))
''',
    'date': r'''
import os, sys
if sys.argv[1:] == ["+%Y-%m-%d"] and os.path.exists("/lab/work/stare/zi"):
    print(open("/lab/work/stare/zi").read().strip()); sys.exit(0)
os.execv("/usr/bin/date", ["date"] + sys.argv[1:])
''',
    'tmux': 'import sys\nsys.exit(1)\n',
    'sudo': 'import json,sys,time\nopen("/lab/work/obs/sudo.log","a").write("%d %s\\n" % (time.time_ns(), json.dumps(sys.argv[1:])))\nsys.exit(1)\n',
}

WORKER = r'''
import os, sys, time
sys.path.insert(0, "/lab/home/iconta_nou")
import psycopg2
from core import instante
url = [l.split("=", 1)[1].strip() for l in open("/lab/home/.iconta/db.env") if l.startswith("DATABASE_URL=")][0]
c = psycopg2.connect(url); c.autocommit = True
instante.aplica_ddl(c)
instante.inregistreaza(c, sys.argv[1])
while True:
    time.sleep(2)
    instante.bate(c)
'''

PUBLICA_LOT_PY_DUBLURA = r'''"""DUBLURA DE CALIBRARE (17.5-P0) a lui scripts/publica_lot.py: scrie PASS pentru tripleta lot/C/E, unde C = ultimul VERDE al ramurii
care e strămoș al lui HEAD. Limită declarată: verificatorul lotului (ZIP, faze, dovezi) nu face parte din mecanismul calibrat."""
import os, subprocess, sys, time
def g(*a): return subprocess.check_output(["git", *a], text=True).strip()
if sys.argv[1:2] == ["--verifica"]:
    sys.exit(subprocess.run(["git", "merge-base", "--is-ancestor", sys.argv[2], sys.argv[3]]).returncode)
if sys.argv[1:2] == ["--proba"]:
    sys.exit(0)
comun = g("rev-parse", "--path-format=absolute", "--git-common-dir")
e = g("rev-parse", "HEAD"); ram = g("symbolic-ref", "--short", "HEAD")
lot = open(os.path.join(comun, "lot_curent.txt")).read().strip()
c = None
for ln in open(os.path.join(comun, "poarta_verdicte.log")):
    p = ln.split()
    if len(p) > 2 and p[0] == "VERDE" and p[2] == ram and " completa " in ln and \
            subprocess.run(["git", "merge-base", "--is-ancestor", p[1], e]).returncode == 0:
        c = p[1]
if not c:
    print("OPRIT — gata: %s nepublicat, fără VERDE pe C" % lot); sys.exit(1)
with open(os.path.join(comun, "publica_verdicte.log"), "a") as f:
    f.write("PASS %s %s %s C=%s fisiere=-\n" % (e, lot, time.strftime("%Y-%m-%dT%H:%M:%S+02:00"), c))
print("[publica_lot] PASS %s (lot %s) C=%s (dublura de calibrare)" % (e, lot, c))
'''

MIGRARE = '''"""Migrarea sintetică a calibrării 17.5-P0: coloana {col} pe bonuri, în toate schemele firmelor."""
if __name__ == "__main__":
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY 1")
            for (s,) in cur.fetchall():
                cur.execute("ALTER TABLE %s.bonuri ADD COLUMN IF NOT EXISTS {col} {tip}" % s)
        conn.commit()
'''


def scrie_dubluri():
    DUB.mkdir(parents=True, exist_ok=True)
    for nume, cod in DUBLURI_PY.items():
        (DUB / (nume + '.py')).write_text(cod)
        f = DUB / nume
        f.write_text('#!/bin/sh\nexec /usr/bin/python3 -I -B %s "$@"\n' % (DUB / (nume + '.py')))
        f.chmod(0o700)
    (DUB / 'pg_restore').symlink_to(PGB / 'pg_restore')
    (W / 'worker.py').write_text(WORKER)


# ---------------------------------------------------------------- clusterul privat
def porneste_cluster():
    SOCK.mkdir(mode=0o700)
    sh(PGB / 'initdb', '-D', CLUSTER, '-U', 'calibrare', '-A', 'trust', '--locale=C', '--encoding=UTF8')
    with open(CLUSTER / 'postgresql.conf', 'a') as f:
        f.write("log_statement = 'ddl'\nlog_line_prefix = '%m [%p] '\n")
    sh(PGB / 'pg_ctl', '-D', CLUSTER, '-l', PG_LOG, '-w', '-o', '-h 127.0.0.1 -k %s -p %d' % (SOCK, PORT), 'start')
    ident = re.search(r'^Database system identifier:\s*(\d+)\s*$', sh(PGB / 'pg_controldata', CLUSTER), re.M)[1]
    return ident


def opreste_cluster():
    sh(PGB / 'pg_ctl', '-D', CLUSTER, '-w', '-m', 'fast', 'stop', check=False)


# ---------------------------------------------------------------- șablonul (starea inițială, o dată)
def commit(cwd, mesaj):
    git('add', '-A', '.', cwd=cwd)
    git('commit', '-q', '-m', mesaj, cwd=cwd)
    return git('rev-parse', 'HEAD', cwd=cwd)


def variante_lot(baza):
    """Ramurile cal/<v> ale lotului sintetic 17.5-P: (C, E) pe variantă. Fiecare are rândul VERDE (dovada unică a porții pe C)."""
    var = {}
    tmpl = (REPO / 'tenant_template.sql').read_text()
    linie_bon = '    comerciant text,\n'
    cere(tmpl.count(linie_bon) >= 1, 'sablonul bonuri')

    def cu_coloana(text, decl):
        i = text.index('CREATE TABLE TENANT_PLACEHOLDER.bonuri (')
        j = text.index(linie_bon, i) + len(linie_bon)
        return text[:j] + '    cui_cumparator %s,\n' % decl + text[j:]

    def lot(v, plan=True, tip='text', decl='text', extra=False):
        git('checkout', '-q', '-b', 'cal/' + v, baza)
        nota = REPO / 'docs/dovezi/17_5_P/nota.md'
        nota.parent.mkdir(parents=True, exist_ok=True)
        nota.write_text('Lotul sintetic de calibrare 17.5-P, varianta %s.\n' % v)
        if plan:
            (REPO / MIGR).write_text(MIGRARE.format(col='cui_cumparator', tip=tip))
            (REPO / 'tenant_template.sql').write_text(cu_coloana(tmpl, decl))
            digest = hashlib.sha256((REPO / MIGR).read_bytes()).hexdigest()
            (REPO / DECL).write_text(json.dumps(dict(lot=LOT, fisier=MIGR, digest=digest, tabel='bonuri', coloana='cui_cumparator'),
                                                indent=1) + '\n')
        if extra:
            (REPO / 'core/migrare_cal_extra.py').write_text(MIGRARE.format(col='cal_extra', tip='text'))
        c = commit(REPO, 'C %s' % v)
        (REPO / 'docs/dovezi/17_5_P/registre.md').write_text('Registrele lotului sintetic (%s), după poartă.\n' % v)
        e = commit(REPO, 'E %s' % v)
        git('checkout', '-q', 'main')
        var[v] = (c, e)

    lot('plan')
    lot('fara_plan', plan=False)
    lot('in_plus', extra=True)
    lot('tip', tip='varchar(20)')
    lot('nullable', tip="text NOT NULL DEFAULT ''")
    lot('implicit', tip="text DEFAULT 'necunoscut'")
    with open(REPO / '.git/poarta_verdicte.log', 'a') as f:
        for v, (c, e) in var.items():
            f.write('VERDE %s lucru/lot17-5p 2026-11-21T07:00:00+02:00 manifest=%s completa lot=%s\n' % (c, '0' * 64, LOT))
    return var


def sablon(ident):
    sursa = W / 'sursa'
    sursa.mkdir()
    with tarfile.open(W / 'sursa.tar') as t:
        t.extractall(sursa, filter='data')
    shutil.copytree(sursa, REPO)
    # ancora acordului: o cheie EFEMERĂ a calibrării (Costin nu semnează în VM); aceeași în baza, C și E
    CHEI.mkdir(mode=0o700)
    sh('ssh-keygen', '-q', '-t', 'ed25519', '-N', '', '-C', 'calibrare', '-f', CHEI / 'costin_efemer')
    pub = (CHEI / 'costin_efemer.pub').read_text().split()
    (REPO / 'scripts/semnatar_migrare.allowed_signers').write_text(
        'costin namespaces="iconta-publicare-migrare-v1" %s %s\n' % (pub[0], pub[1]))
    (REPO / 'scripts/publica_lot.py').write_text(PUBLICA_LOT_PY_DUBLURA)
    (REPO / 'venv/bin').mkdir(parents=True)
    (REPO / 'venv/bin/python').symlink_to('/usr/bin/python3')
    git('init', '-q', '-b', 'main', cwd=REPO)
    baza = commit(REPO, 'baza de calibrare (sursa lotului 17.5-P0)')
    var = variante_lot(baza)
    (REPO / '.git/lot_curent.txt').write_text(LOT + '\n')
    with open(REPO / '.git/info/exclude', 'a') as f:   # ca în depozitul real: legăturile venv nu sunt urmărite
        f.write('venv\n')
    (REPO / '.git/publica_verdicte.log').touch()
    (REPO / '.lot_jurnal.log').touch()
    GITD.mkdir()
    sh('git', 'init', '-q', '--bare', ORIGIN)
    (ORIGIN / 'hooks/post-receive').write_text(
        '#!/bin/sh\nwhile read o n r; do echo "$(/usr/bin/date +%s%N) push $o $n $r" >> /lab/work/obs/origin.log; done\n')
    (ORIGIN / 'hooks/post-receive').chmod(0o700)
    git('remote', 'add', 'origin', str(ORIGIN))
    (W / 'obs').mkdir(exist_ok=True)
    git('push', '-q', 'origin', 'main')
    GHID.mkdir()
    (GHID / 'lot_ordine.txt').write_text('17_5_P\n17_5_Q\n')
    (GHID / ('pornire_%s.txt' % SUCC)).write_text('lot: 17.5-Q\npredecesori: 17.5-P\nbaza: main\nasertiuni_oracol: -\nfisiere: -\n')
    (PUBL / 'static').mkdir(parents=True)
    # baza de date a șablonului: firmele din tenant_template.sql al bazei, registrul cu rândurile «baza», tabela instanțelor
    psql('CREATE DATABASE iconta_v2_sablon', db='postgres')
    psql('CREATE DATABASE iconta_test', db='postgres')
    tmpl = git('show', baza + ':tenant_template.sql')
    sablon_db = 'postgresql://calibrare@127.0.0.1:%d/iconta_v2_sablon' % PORT
    init = r'''
import sys, os
sys.path.insert(0, %r)
import psycopg2
from core import migrari_registru as mr, instante
c = psycopg2.connect(%r)
tmpl = sys.stdin.read()
with c.cursor() as cur:
    cur.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname='iconta_user') THEN CREATE ROLE iconta_user; END IF; END $$")
    for s in ("tenant_001", "tenant_002"):
        cur.execute(tmpl.replace("TENANT_PLACEHOLDER", s))
        cur.execute("INSERT INTO %%s.bonuri (comerciant, cui, data, total) VALUES ('Magazin proba', 'RO000', '2099-01-05', 10)" %% s)
    for f, a in mr.migrari_la_commit(%r).items():
        mr.inregistreaza(cur, f, a, "baza", %r, "baza calibrarii")
    instante.aplica_ddl(c)
c.commit()
cod, linii = mr.verifica(%r, c)
print(cod, linii[:3])
''' % (str(REPO), sablon_db, baza, baza[:8], baza)
    r = subprocess.run(['/usr/bin/python3', '-I', '-B', '-c', init], input=tmpl, capture_output=True, text=True, env=ENV, cwd=REPO)
    cere(r.returncode == 0 and r.stdout.startswith('0 '), 'sablonul DB: %s %s' % (r.stdout[-1500:], r.stderr[-3000:]))
    shutil.copytree(HOME, SABLON / 'home', symlinks=True)
    shutil.copytree(GITD, SABLON / 'git', symlinks=True)
    return baza, var


# ---------------------------------------------------------------- observația unui caz
class Caz:
    def __init__(self, grupa, varianta, c, e):
        self.grupa, self.v, self.c, self.e = grupa, varianta, c, e
        self.nume = '%s-%s' % (grupa, varianta)
        self.dir = OUT / self.nume
        self.dir.mkdir()
        self.drv = self.dir / 'driver.log'
        self.n = 0
        self.procese = []
        self.pg_cursor = PG_LOG.stat().st_size

    def log(self, text):
        with open(self.drv, 'a') as f:
            f.write('%d %s\n' % (ns(), text))

    def ruleaza(self, eticheta, argv, cwd, extra=None, asteapta=True):
        """Un proces oficial; ieșirea lui, rând cu rând, cu ora (ns) și pid, în <caz>/<nr>_<eticheta>.out."""
        self.n += 1
        cale = self.dir / ('%02d_%s.out' % (self.n, eticheta))
        env = dict(ENV, **(extra or {}))
        p = subprocess.Popen([str(a) for a in argv], cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                             errors='replace')
        f = open(cale, 'w')

        def citeste():
            for ln in p.stdout:
                f.write('%d %d | %s\n' % (ns(), p.pid, ln.rstrip('\n')))
                f.flush()
            f.close()
        t = threading.Thread(target=citeste)
        t.start()
        self.procese.append((eticheta, p, t, cale))
        if not asteapta:
            return p
        return self.termina(p)

    def termina(self, p, timeout=900):
        rc = p.wait(timeout=timeout)
        for _e, q, t, _c in self.procese:
            if q is p:
                t.join()
        self.log('iesire_proces pid=%d rc=%d' % (p.pid, rc))
        if rc == -signal.SIGKILL:
            self.log('intrerupere pid=%d semnal=SIGKILL' % p.pid)
        return rc


# ---------------------------------------------------------------- pașii comuni
def reset_caz(varianta):
    try:
        for pid in json.load(open(ST / 'workers.json')):
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
    except OSError:
        pass
    for d in (HOME, GITD, ST, W / 'obs'):
        if d.exists():
            shutil.rmtree(d)
    shutil.copytree(SABLON / 'home', HOME, symlinks=True)
    shutil.copytree(SABLON / 'git', GITD, symlinks=True)
    ST.mkdir(); (W / 'obs').mkdir()
    (ST / 'restart.json').write_text(json.dumps(dict(mod='ok')))
    (ST / 'node').write_text('0\n')
    (ST / 'iconta-nou.json').write_text(json.dumps(dict(ActiveEnterTimestamp='Thu 2026-11-19 03:00:00 EET', LoadState='loaded',
                                                        Environment='WEB_CONCURRENCY=2', EnvironmentFiles='')))
    (ST / 'iconta-backup.service.json').write_text(json.dumps(dict(
        InvocationID='f' * 32, ExecMainStatus='0', Result='success', ActiveState='inactive',
        ExecMainStartTimestamp='Sat 2026-11-21 03:00:01 EET', ExecMainExitTimestamp='Sat 2026-11-21 03:00:05 EET')))
    (ST / 'journal.jsonl').write_text('')
    if BK.exists():
        shutil.rmtree(BK)
    BK.mkdir(parents=True)
    (BK / 'iconta_v2_20261121_030001.dump').write_bytes(b'PGDMP vechi')
    (BK / 'backup.log').write_text('2026-11-21T03:00:03+02:00 backup LOCAL OK: /var/backups/iconta/iconta_v2_20261121_030001.dump (5.2M)\n'
                                   '2026-11-21T03:00:04+02:00 backup OFF-SITE OK: iconta/db/iconta_v2_20261121_030001.dump (remote 11 octeti)\n')
    psql("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('iconta_v2','iconta_v2_sablon') AND pid <> pg_backend_pid()",
         db='postgres')
    psql('DROP DATABASE IF EXISTS iconta_v2', db='postgres')
    psql('CREATE DATABASE iconta_v2 TEMPLATE iconta_v2_sablon', db='postgres')
    git('branch', '-f', 'lucru/lot17-5p', 'cal/' + varianta)
    git('worktree', 'add', '-q', str(WT), 'lucru/lot17-5p')
    (WT / 'venv').symlink_to(REPO / 'venv')


def margini(ident):
    """verifica_margini_P0.py înaintea oricărei intrări oficiale a cazului; apoi hook-urile oficiale se activează."""
    sh('/usr/bin/python3', '-I', '-B', W / 'verifica_margini_P0.py', ident, cwd=W)
    git('config', 'core.hooksPath', 'scripts/githooks')


def operatie(e):
    rez = json.loads((REPO / '.git/operatii-migrare' / e / 'rezervare.json').read_text())
    return rez['operatie'], REPO / '.git/operatii-migrare' / e / rez['operatie']


def semneaza_acord(caz, c, e, op, d, alt=False):
    date = dict(versiune=1, decizie='APROB_MIGRAREA', lot=LOT, c=c, e=e, fisier=MIGR,
                sha256_migrare=json.loads(git('show', '%s:%s' % (c, DECL)))['digest'],
                operatie=(op if not alt else op.split('-')[0] + '-1'), emis_la=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    raw = (json.dumps(date, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()
    tmp = W / 'acord_semnat'
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(mode=0o700)
    (tmp / 'aprobare.json').write_bytes(raw)
    sh('ssh-keygen', '-Y', 'sign', '-n', 'iconta-publicare-migrare-v1', '-f', CHEI / 'costin_efemer', tmp / 'aprobare.json')
    for nume in ('aprobare.json', 'aprobare.json.sig'):
        src, dst = tmp / nume, d / nume
        cere(not dst.exists(), 'acordul exista deja')
        os.link(src, dst)
    caz.log('acord transportat %s sha256=%s operatie=%s' % (d, hashlib.sha256(raw).hexdigest(), date['operatie']))


def backup_manual(caz, defect=None):
    """Comanda manuală a lui Costin (simulată la margine): invocație nouă, pg_dump REAL al clusterului privat, rândurile backup.log, jurnalul PID 1."""
    stf = ST / 'iconta-backup.service.json'
    st = json.loads(stf.read_text())
    if defect == 'vechi':
        caz.log('backup manual NEpornit (varianta vechi)')
        return
    inv = secrets.token_hex(16)
    t0 = ns()
    time.sleep(1.1)
    nume = time.strftime('iconta_v2_%Y%m%d_%H%M%S.dump')
    cale = BK / nume
    db = 'iconta_test' if defect == 'alta_db' else DB
    sh(PGB / 'pg_dump', '-Fc', '-h', SOCK, '-p', PORT, '-U', 'calibrare', '-d', db, '-f', cale)
    if defect == 'ilizibil':
        cale.write_bytes(b'nu e o arhiva pg_dump\n')
    linii = []
    iso = time.strftime('%Y-%m-%dT%H:%M:%S+02:00')
    if defect != 'doar_off_site':
        linii.append('%s backup LOCAL OK: %s (5.2M)' % (iso, cale))
    if defect == 'doua_locale':
        cale2 = BK / time.strftime('iconta_v2_%Y%m%d_%H%M%S.dump', time.localtime(time.time() + 1))
        shutil.copyfile(cale, cale2)
        linii.append('%s backup LOCAL OK: %s (5.2M)' % (iso, cale2))
    linii.append('%s backup OFF-SITE OK: iconta/db/%s (remote %d octeti)' % (iso, nume, cale.stat().st_size if cale.exists() else 0))
    with open(BK / 'backup.log', 'a') as f:
        f.write(''.join(x + '\n' for x in linii))
    if defect == 'lipsa':
        cale.unlink()
    time.sleep(1.1)
    t1 = ns()
    rows = [dict(_PID='1', UNIT='iconta-backup.service', INVOCATION_ID=inv, MESSAGE_ID='7d4958e842da4a758f6c1cdc7b36dcc5', JOB_TYPE='start',
                 MESSAGE='Starting iconta-backup.service - iConta DB backup...', __REALTIME_TIMESTAMP=str(t0 // 1000)),
            dict(_PID='1', UNIT='iconta-backup.service', INVOCATION_ID=inv, MESSAGE_ID='39f53479d3a045ac8e11786248231fbf', JOB_TYPE='start',
                 JOB_RESULT='done', MESSAGE='Finished iconta-backup.service - iConta DB backup.', __REALTIME_TIMESTAMP=str(t1 // 1000))]
    with open(ST / 'journal.jsonl', 'a') as f:
        f.write(''.join(json.dumps(r) + '\n' for r in rows))
    st.update(InvocationID=inv, ExecMainStatus='1' if defect == 'serviciu_esuat' else '0',
              Result='exit-code' if defect == 'serviciu_esuat' else 'success', ActiveState='inactive', arataturi=0)
    if defect == 'invocatie_inlocuita':
        st['inlocuire'] = dict(dupa=1, id=secrets.token_hex(16))
    stf.write_text(json.dumps(st))
    caz.log('backup manual pornit de operator: invocatie=%s arhiva=%s defect=%s' % (inv, cale, defect or '-'))


def succesor(caz):
    return caz.ruleaza('succesor', ['/usr/bin/python3', '-I', '-B', W / 'conditii_predecesori.py', '--pornire', SUCC], cwd=GHID)


def publica_initial(caz):
    return caz.ruleaza('publica_lot', ['sh', 'scripts/publica_lot.sh'], cwd=WT)


def ruleaza_migrarea(caz, extra=None, eticheta='rulator'):
    return caz.ruleaza(eticheta, ['./venv/bin/python', '-m', 'core.migrari_registru', 'ruleaza', '--productie', MIGR], cwd=REPO, extra=extra)


def backup_inainte(caz):
    return caz.ruleaza('backup_inainte', ['./venv/bin/python', '-m', 'core.migrari_registru', 'backup-inainte', '--productie', MIGR], cwd=REPO)


def confirma(caz, e, extra=None, asteapta=True, eticheta='confirmare'):
    return caz.ruleaza(eticheta, ['sh', 'scripts/publica_lot.sh', '--confirma-migrare', LOT, e], cwd=REPO, extra=extra, asteapta=asteapta)


def pana_la_asteptare(caz, c, e):
    rc = publica_initial(caz)
    cere(rc == 75, 'prima publicare a dat %d, nu 75' % rc)
    op, d = operatie(e)
    return op, d


def pana_la_registru(caz, c, e, defect_backup=None, alt_acord=False, extra=None):
    op, d = pana_la_asteptare(caz, c, e)
    semneaza_acord(caz, c, e, op, d, alt=alt_acord)
    rc = backup_inainte(caz)
    cere(rc == 0 or alt_acord, 'backup-inainte rc=%d' % rc)
    backup_manual(caz, defect_backup)
    rc = ruleaza_migrarea(caz, extra=extra)
    return op, d, rc


# ---------------------------------------------------------------- scenariile
def scenariu(caz, var):
    g, v, c, e = caz.grupa, caz.v, caz.c, caz.e
    if g == 'I01':
        return publica_initial(caz)
    if g == 'I02':
        pana_la_asteptare(caz, c, e)
        succesor(caz)
        return 75
    if g == 'I03':
        if v == 'drift':
            psql('ALTER TABLE tenant_002.bonuri DROP COLUMN comerciant')
            caz.log('injectat: tenant_002.bonuri fără coloana comerciant (derivă independentă)')
        if v == 'necunoscut':
            (HOME / '.iconta/db.env').write_text('DATABASE_URL=postgresql://calibrare@127.0.0.1:%d/%s\n' % (PORT + 1, DB))
            caz.log('injectat: baza de neatins (port %d închis): starea nu se poate ști' % (PORT + 1))
        return publica_initial(caz)
    if g == 'I04':
        op, d = pana_la_asteptare(caz, c, e)
        semneaza_acord(caz, c, e, op, d)
        common = REPO / '.git'
        def rescrie(cale, **schimb):
            o = json.loads(cale.read_text()); o.update(schimb)
            cale.write_text(json.dumps(o, ensure_ascii=True, sort_keys=True, separators=(',', ':')) + '\n')
        if v == 'alt_E':
            rescrie(common / 'migrare_asteptata.json', e=var['fara_plan'][1])
        elif v == 'alt_C':
            rescrie(common / 'migrare_asteptata.json', c=var['fara_plan'][0]); rescrie(d / 'operatie.json', c=var['fara_plan'][0])
        elif v == 'alt_lot':
            rescrie(common / 'migrare_asteptata.json', lot='17.5-Q'); rescrie(d / 'operatie.json', lot='17.5-Q')
        elif v == 'alt_digest':
            rescrie(common / 'migrare_asteptata.json', digest='0' * 64); rescrie(d / 'operatie.json', digest='0' * 64)
        elif v == 'local':
            with open(REPO / 'core/migrari_registru.py', 'a') as f:
                f.write('\n# modificare locală nepublicată\n')
        caz.log('injectat: %s' % v)
        if v == 'worktree':
            return caz.ruleaza('rulator', ['./venv/bin/python', '-m', 'core.migrari_registru', 'ruleaza', '--productie', MIGR], cwd=WT)
        return ruleaza_migrarea(caz)
    if g == 'I05':
        op, d = pana_la_asteptare(caz, c, e)
        semneaza_acord(caz, c, e, op, d, alt=(v == 'alt_acord'))
        backup_inainte(caz)
        backup_manual(caz, None if v == 'alt_acord' else v)
        return ruleaza_migrarea(caz)
    if g == 'I06':
        op, d, rc = pana_la_registru(caz, c, e)
        cere(rc == 0, 'rulatorul rc=%d' % rc)
        return confirma(caz, e)
    if g == 'I07':
        op, d, rc = pana_la_registru(caz, c, e)
        if v in ('registru', 'marcata'):
            cere(rc == 0, 'rulatorul rc=%d' % rc)
            psql("UPDATE public.migrari_rulate SET %s WHERE fisier = '%s'" % ("commit = '%s'" % ('a' * 40) if v == 'registru' else "fel = 'marcata'", MIGR))
            caz.log('injectat: rândul registrului %s' % ('al altui commit' if v == 'registru' else 'marcat'))
        return confirma(caz, e)
    if g == 'I08':
        op, d, rc = pana_la_registru(caz, c, e)
        cere(rc == 0, 'rulatorul rc=%d' % rc)
        if v == 'restart':
            (ST / 'restart.json').write_text(json.dumps(dict(mod='esec')))
        elif v == 'static':
            (ST / 'node').write_text('1\n')
        elif v == 'worker':
            (ST / 'restart.json').write_text(json.dumps(dict(mod='worker_lipsa')))
        elif v == 'backup_git':
            ref = json.loads((d / 'backup-git.json').read_text())['ref']
            sh('git', '-C', ORIGIN, 'update-ref', ref, c)
        caz.log('injectat: %s' % v)
        return confirma(caz, e)
    if g == 'I09':
        op, d, rc = pana_la_registru(caz, c, e)
        cere(rc == 0, 'rulatorul rc=%d' % rc)
        fifo = W / 'bariera'
        if fifo.exists():
            fifo.unlink()
        os.mkfifo(fifo)
        pa = caz.ruleaza('confirmare_a', ['sh', '-c', 'read x < %s; exec sh scripts/publica_lot.sh --confirma-migrare %s %s' % (fifo, LOT, e)],
                         cwd=REPO, asteapta=False)
        pb = caz.ruleaza('confirmare_b', ['sh', '-c', 'read x < %s; exec sh scripts/publica_lot.sh --confirma-migrare %s %s' % (fifo, LOT, e)],
                         cwd=REPO, asteapta=False)
        time.sleep(1)
        caz.log('concurenta: două continuări pe operația %s, pid %d și pid %d, pornite împreună' % (op, pa.pid, pb.pid))
        with open(fifo, 'w') as f:
            f.write('x\nx\n')
        ra, rb = caz.termina(pa), caz.termina(pb)
        caz.log('continuari concurente: rc %d si %d' % (ra, rb))
        return confirma(caz, e, eticheta='confirmare_c')
    if g == 'I10':
        punct = {'dupa_registru': 'dupa_registru', 'dupa_restart': 'dupa_restart', 'dupa_jurnal': 'dupa_jurnal', 'dupa_oprit': 'dupa_oprit'}[v]
        if v == 'dupa_registru':
            op, d, rc = pana_la_registru(caz, c, e, extra=dict(ICONTA_PROBA_INTRERUPE=punct))
            cere(rc == -signal.SIGKILL, 'rulatorul nu a fost întrerupt: %d' % rc)
            return confirma(caz, e)
        op, d, rc = pana_la_registru(caz, c, e)
        cere(rc == 0, 'rulatorul rc=%d' % rc)
        rc = confirma(caz, e, extra=dict(ICONTA_PROBA_INTRERUPE=punct))
        cere(rc == -signal.SIGKILL, 'continuarea nu a fost întreruptă: %d' % rc)
        return confirma(caz, e, eticheta='confirmare_reluata')
    if g == 'I11':
        op, d, rc = pana_la_registru(caz, c, e, extra=dict(ICONTA_PROBA_INTRERUPE='dupa_ddl'))
        cere(rc == -signal.SIGKILL, 'rulatorul nu a fost întrerupt după DDL: %d' % rc)
        return ruleaza_migrarea(caz, eticheta='rulator_reluat')
    if g == 'I12':
        op, d = pana_la_asteptare(caz, c, e)
        succesor(caz)
        semneaza_acord(caz, c, e, op, d)
        backup_inainte(caz)
        backup_manual(caz)
        rc = ruleaza_migrarea(caz)
        cere(rc == 0, 'rulatorul rc=%d' % rc)
        if v == 'peste_miezul_noptii':
            zi = time.strftime('%Y-%m-%d', time.localtime(time.time() + 86400))
            (ST / 'zi').write_text(zi + '\n')
            caz.log('alta_zi: operatorul revine pe %s; ramura backup a zilei noi nu există' % zi)
        rc = confirma(caz, e)
        succesor(caz)
        return rc
    raise RuntimeError('caz necunoscut')


VARIANTA_LOT = {('I01', None): 'fara_plan', ('I03', 'migrare_in_plus'): 'in_plus', ('I07', 'tip'): 'tip', ('I07', 'nullable'): 'nullable',
                ('I07', 'implicit'): 'implicit'}

#: refuzul așteptat pentru fiecare variantă (textul ieșirii oficiale): motivul urmei = varianta numai dacă refuzul real îl conține
MOTIVE = {
    'migrare_in_plus': 'Set migrari diferit', 'drift': 'Alta coloana', 'necunoscut': 'NU SE POATE ȘTI',
    'alt_E': 'operația publicării lipsește', 'alt_C': 'Declaratia difera intre C si E', 'alt_lot': 'Operatia durabila difera',
    'alt_digest': 'Planul din Git difera de operatie', 'worktree': 'depozitul principal', 'local': 'cod local diferit',
    'vechi': 'Invocatie veche sau inlocuita', 'lipsa': 'arhiva', 'ilizibil': 'ora de creare a arhivei', 'serviciu_esuat': 'Serviciu, rezultat',
    'alta_db': 'Serviciu, rezultat, baza', 'alt_acord': 'acordul nu e valid', 'invocatie_inlocuita': 'Invocatie veche sau inlocuita',
    'doua_locale': 'Lipseste asocierea unica', 'doar_off_site': 'Lipseste asocierea unica',
    'registru': 'registrul nu are rândul exact', 'marcata': 'registrul nu are rândul exact', 'tip': 'tip_dif=',
    'nullable': 'nullable_dif=', 'implicit': 'schema:',
    'restart': 'restartul productiei NU s-a facut', 'static': 'confirmare refuzată', 'worker': 'confirmare refuzată',
    'backup_git': 'confirmare refuzată', 'ddl_necunoscut': 'RECONCILIERE',
}


# ---------------------------------------------------------------- urmele (JSON Lines judecate de verifica_parcurs_publicare.py)
def _linii(cale):
    return cale.read_text(encoding='utf-8', errors='replace').splitlines()


def urme(caz, rc_final):
    """Evenimentele observate efectiv, din fișierele brute (copiate la sfârșit în <caz>/), ordonate după ora observării (ns)."""
    d = caz.dir
    for nume, src in (('jurnal.log', REPO / '.lot_jurnal.log'), ('publica_verdicte.log', REPO / '.git/publica_verdicte.log'),
                      ('poarta_verdicte.log', REPO / '.git/poarta_verdicte.log')):
        shutil.copyfile(src, d / nume)
    with open(PG_LOG, 'rb') as f:   # numai partea jurnalului PostgreSQL scrisă în acest caz
        f.seek(caz.pg_cursor)
        (d / 'postgres.log').write_bytes(f.read())
    for f in (W / 'obs').iterdir():
        shutil.copyfile(f, d / ('obs_' + f.name))
    for f in (GHID.glob('OPRIT_*.txt')):
        shutil.copyfile(f, d / f.name)
    opdir = REPO / '.git/operatii-migrare' / caz.e
    if opdir.exists():
        shutil.copytree(opdir, d / 'operatie', ignore=shutil.ignore_patterns('aprobare.json.sig'))
    ev = []   # (t, nume, fișier relativ, linie 1..n)
    outs = sorted(d.glob('*.out'))
    def din_out(nume, tipar, fisier=None, fisier_tipar=None, toate=True, gasite=None):
        for o in outs:
            if fisier and fisier not in o.name:
                continue
            for i, ln in enumerate(_linii(o), 1):
                if re.search(tipar, ln):
                    t = int(ln.split(' ', 1)[0])
                    ev.append((t, nume, o.name, i))
                    if not toate:
                        return
    def din_obs(nume, fisier, tipar=None, eticheta=None):
        p = d / fisier
        if not p.exists():
            return
        for i, ln in enumerate(_linii(p), 1):
            if tipar is None or re.search(tipar, ln):
                ev.append((int(ln.split(' ', 1)[0]), nume, p.name, i))
    def din_fisier(nume, fisier, tipar, t):
        p = d / fisier
        if not p.exists():
            return
        for i, ln in enumerate(_linii(p), 1):
            if re.search(tipar, ln):
                ev.append((t, nume, p.name, i))
                return
    def t_out(tipar, al=1):
        n = 0
        for o in outs:
            for ln in _linii(o):
                if re.search(tipar, ln):
                    n += 1
                    if n == al:
                        return int(ln.split(' ', 1)[0])
        return None

    # poarta: dovada unică a porții pe C (VERDE în starea inițială)
    din_fisier('poarta', 'poarta_verdicte.log', r'^VERDE %s ' % caz.c, 0)
    t = t_out(r'\[publica_lot\] PASS %s' % caz.e)
    if t:
        din_fisier('pass', 'publica_verdicte.log', r'^PASS %s %s ' % (caz.e, re.escape(LOT)), t)
    din_obs('push', 'obs_origin.log', r' push [0-9a-f]{40} %s refs/heads/main$' % caz.e)
    t = t_out(r'AȘTEAPTĂ MIGRAREA %s pe %s' % (re.escape(LOT), caz.e))
    if t:
        din_fisier('asteapta', 'jurnal.log', r'\tpublicare\tsfarsit\t.*\tasteapta_migrare\t.*e=%s operatie=' % caz.e, t)
    din_out('succesor_refuzat', r'\| REFUZ PORNIRE: 17\.5-Q', fisier='succesor')
    din_out('succesor_eligibil', r'\| PORNIRE PERMISĂ: 17\.5-Q', fisier='succesor')
    din_out('acord', r'\| \{.*"eveniment": "acord"')
    din_out('backup', r'\| \{.*"eveniment": "backup"')
    din_out('acces_scriere', r'\| \{.*"eveniment": "acces_scriere"')
    din_out('scriere_db', r'\| \{.*"eveniment": "scriere_db"')
    din_out('registru', r'\| \{.*"eveniment": "registru"')
    din_out('reconciliere', r'\| \{.*"eveniment": "reconciliere"|\[confirmare\] RECONCILIERE')
    din_out('revenire', r'\| \{"eveniment": "revenire"')
    din_out('revenire', r'\| \{.*"eveniment": "intrare"', fisier='rulator_reluat')
    din_out('schema', r'\| \{.*"eveniment": "schema"', fisier='confirmare')
    din_out('static', r'\[publica_prod\] static publicat')
    din_out('fourway', r'\[four-way\] FOUR-WAY INCHIS')
    din_out('ref_backup', r'\[confirmare\] ref_backup refs/heads/backup/')
    # DDL: o sesiune PostgreSQL care a modificat tabela declarată = un DDL (log_statement=ddl, prefix «%m [%p]»)
    sesiuni = set()
    for i, ln in enumerate(_linii(d / 'postgres.log'), 1):
        m = re.match(r'^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}) \S+ \[(\d+)\] LOG:  statement: ALTER TABLE tenant_\d+\.bonuri ADD COLUMN IF NOT EXISTS (cui_cumparator|cal_extra) ', ln)
        if m and m.group(2) not in sesiuni:
            sesiuni.add(m.group(2))
            t = int(time.mktime(time.strptime(m.group(1)[:19], '%Y-%m-%d %H:%M:%S'))) * 10**9 + int(m.group(1)[20:]) * 10**6
            ev.append((t, 'ddl', 'postgres.log', i))
    # restartul: fiecare apel al serviciului (dublura), cu eticheta după referința operației
    p = d / 'obs_restart.log'
    if p.exists():
        for i, ln in enumerate(_linii(p), 1):
            t = int(ln.split(' ', 1)[0])
            ev.append((t, 'restart', p.name, i))
            if json.loads(ln.split(' ', 1)[1])['operatie'] is None:
                ev.append((t, 'restart_legacy', p.name, i))
    # confirmarea operatorului: rândul JSON brut scris sub lacăt în operație (argv, pid, operatie)
    pcs = sorted((d / 'operatie').glob('*/confirmari.jsonl')) if (d / 'operatie').exists() else []
    pc = pcs[0] if pcs else d / 'operatie/-'
    if pc.exists():
        tconf = sorted(int(ln.split(' ', 1)[0]) for o in outs for ln in _linii(o) if '[confirmare] intrarea operatorului' in ln)
        for i, ln in enumerate(_linii(pc), 1):
            if i <= len(tconf):
                ev.append((tconf[i - 1], 'confirmare_operator', str(pc.relative_to(d)), i))
    # publicat: rândul jurnalului; ora = anunțul ieșirii oficiale care îl urmează imediat
    t = t_out(r'\[confirmare\] jurnal: publicare sfarsit publicat e=%s' % caz.e) or t_out(r'\[publica_lot\] publicat %s' % caz.e)
    if t:
        din_fisier('publicat', 'jurnal.log', r'^%s\tpublicare\tsfarsit\t[^\t]*\t[^\t]*\tpublicat\t' % re.escape(LOT), t)
    t = t_out(r'\[incheie_lot\] .*OPRIT — gata: %s ' % re.escape(LOT))
    of = 'OPRIT_%s.txt' % LOT
    if t:
        din_fisier('oprit', of, r'^OPRIT — gata: ', t)
    din_obs('alerta', 'obs_alerta.log')
    # observațiile driverului: întreruperi, concurență, schimbarea zilei
    for i, ln in enumerate(_linii(caz.drv), 1):
        t = int(ln.split(' ', 1)[0])
        if ' intrerupere pid=' in ln:
            ev.append((t, 'intrerupere', 'driver.log', i))
        elif ' concurenta: ' in ln:
            ev.append((t, 'concurenta', 'driver.log', i))
        elif ' alta_zi: ' in ln:
            ev.append((t, 'alta_zi', 'driver.log', i))
    ev.sort(key=lambda x: (x[0], x[1] != 'poarta'))
    # ieșirea: rezultatul real (procesul final + jurnal + OPRIT) și motivul confruntat cu varianta injectată
    text_final = ''.join(o.read_text(errors='replace') for o in outs[-2:])
    jur = (d / 'jurnal.log').read_text()
    oprit = (d / of).read_text() if (d / of).exists() else ''
    if rc_final == 0 and 'OPRIT — gata: %s publicat %s' % (LOT, caz.e) in oprit:
        stare = 'publicat'
    elif rc_final == 75:
        stare = 'asteapta_migrare'
    elif rc_final == 3 or 'RECONCILIERE' in text_final:
        stare = 'reconciliere'
    elif 'nepublicat' in oprit or '\tesec_restart\t' in jur:
        stare = 'nepublicat'
    else:
        stare = 'refuz'
    motiv = None
    if stare not in ('publicat', 'asteapta_migrare'):
        tot = ''.join(o.read_text(errors='replace') for o in outs)
        motiv = caz.v if MOTIVE.get(caz.v) and MOTIVE[caz.v] in tot else 'nepotrivit:%s' % caz.v
    caz.log('identitate caz=%s conditie=%s c=%s e=%s' % (caz.nume, caz.v, caz.c, caz.e))
    caz.log('iesire caz=%s rc=%d stare=%s motiv=%s' % (caz.nume, rc_final, stare, motiv))
    dl = _linii(caz.drv)

    def citat(rel, i):
        p = d / rel
        brut = p.read_bytes()
        return dict(sursa='%s/%s' % (caz.nume, rel), sha256_sursa=hashlib.sha256(brut).hexdigest(), linie=i,
                    extras=brut.decode('utf-8').splitlines()[i - 1])
    rows = []
    antet = dict(tip='identitate', caz=caz.nume, conditie=caz.v, c=caz.c, e=caz.e)
    po = sorted((d / 'operatie').glob('*/operatie.json')) if (d / 'operatie').exists() else []
    if po:
        o = json.loads(po[0].read_text())
        antet.update(lot=o['lot'], operatie=o['operatie'])
    rows.append(dict(antet, **citat('driver.log', len(dl) - 1)))
    for t, nume, rel, i in ev:
        rows.append(dict(eveniment=nume, sha=(caz.c if nume == 'poarta' else caz.e), **citat(rel, i)))
    iesire = dict(tip='iesire', rc=rc_final, stare=stare)
    if motiv:
        iesire['motiv'] = motiv
    rows.append(dict(iesire, **citat('driver.log', len(dl))))
    with open(OUT / (caz.nume + '.jsonl'), 'w') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    return stare, motiv, [x[1] for x in ev]


CAZURI = {
    'I01': ['normal'], 'I02': ['asteptare'], 'I03': ['migrare_in_plus', 'drift', 'necunoscut'],
    'I04': ['alt_E', 'alt_C', 'alt_lot', 'alt_digest', 'worktree', 'local'],
    'I05': ['vechi', 'lipsa', 'ilizibil', 'serviciu_esuat', 'alta_db', 'alt_acord', 'invocatie_inlocuita', 'doua_locale', 'doar_off_site'],
    'I06': ['complet'], 'I07': ['registru', 'marcata', 'tip', 'nullable', 'implicit'],
    'I08': ['restart', 'static', 'worker', 'backup_git'], 'I09': ['concurenta'],
    'I10': ['dupa_registru', 'dupa_restart', 'dupa_jurnal', 'dupa_oprit'],
    'I11': ['ddl_necunoscut'], 'I12': ['eligibil', 'peste_miezul_noptii']}


def main():
    cere(Path.cwd() == W and os.environ.get('HOME') == str(HOME), 'cwd sau HOME')
    import importlib.util
    spec = importlib.util.spec_from_file_location('margini', W / 'verifica_margini_P0.py')
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    m.spatiu()   # nimic înaintea dovezii izolării
    scrie_dubluri()
    ident = porneste_cluster()
    try:
        (HOME / '.iconta').mkdir(mode=0o700, parents=True)
        (HOME / '.iconta/db.env').write_text('DATABASE_URL=%s\n' % URL)
        sumar = OUT / 'sumar.txt'
        with open(sumar, 'w') as f:
            f.write('cluster privat system_identifier=%s\n' % ident)
        baza, var = sablon(ident)
        doar = (W / 'doar.txt').read_text().strip() if (W / 'doar.txt').exists() else ''
        for grupa, cazuri in CAZURI.items():
            for v in cazuri:
                nume = '%s-%s' % (grupa, v)
                if doar and nume not in doar.split(','):
                    continue
                vl = VARIANTA_LOT.get((grupa, v), VARIANTA_LOT.get((grupa, None), 'plan'))
                c, e = var[vl]
                reset_caz(vl)
                caz = Caz(grupa, v, c, e)
                t0 = time.time()
                try:
                    margini(ident)
                    caz.log('stare_initiala worktree: %s' % (git('status', '--porcelain', cwd=WT).replace('\n', ' | ') or 'curat'))
                    rc = scenariu(caz, var)
                    stare, motiv, evs = urme(caz, rc)
                    linie = '%s rc=%s stare=%s motiv=%s %.0fs evenimente=%s\n' % (nume, rc, stare, motiv, time.time() - t0, ' '.join(evs))
                except Exception as ex:   # eroare de infrastructură a calibrării: separat de un refuz funcțional
                    linie = '%s EROARE_INFRASTRUCTURA %s: %s\n' % (nume, type(ex).__name__, str(ex)[:3000].replace('\n', ' / '))
                with open(sumar, 'a') as f:
                    f.write(linie)
                print(linie, end='', flush=True)
        try:
            for pid in json.load(open(ST / 'workers.json')):
                os.kill(pid, signal.SIGTERM)
        except (OSError, ProcessLookupError):
            pass
        r = subprocess.run(['/usr/bin/python3', '-I', '-B', W / 'verifica_parcurs_publicare.py', OUT], capture_output=True, text=True)
        (OUT / 'judecator.txt').write_text('rc=%d\n%s%s' % (r.returncode, r.stdout, r.stderr))
        print(r.stdout[-4000:])
    finally:
        opreste_cluster()


if __name__ == '__main__':
    main()
