"""Construiește intrari.tar pentru lanseaza_calibrare_P0.py (17.5-P0, B5 pct.11): ruleaza.sh primul, driverul, gărzile r4 (verifica_margini_P0.py,
verifica_parcurs_publicare.py) și cititorul de predecesori din ~/ghid_incoming (verificate după SHA-ul din manifestul pachetului), sursa lotului exportată
din Git (git archive <commit>: core/, scripts/, static/, tenant_template.sql, .gitignore — fără .git, fără venv, fără ~/.iconta).
  python3 construieste_intrari.py <commit> <director-nou> [<cazuri separate prin virgulă>]   -> tipărește SHA-256 al arhivei"""
import hashlib, io, json, os, subprocess, sys, tarfile
from pathlib import Path

AICI = Path(__file__).resolve().parent
RAD = AICI.parents[3]
GHID = Path.home() / 'ghid_incoming'
MANIFEST = json.loads((GHID / 'manifest_17_5_P0.json').read_text())


def din_ghid(nume, sha=None):
    b = (GHID / nume).read_bytes()
    if sha is None:
        sha = MANIFEST['fisiere'][nume]
    if hashlib.sha256(b).hexdigest() != sha:
        raise SystemExit('SHA diferit pentru %s' % nume)
    return b


def main(commit, dest, doar=''):
    dest = Path(dest)
    dest.mkdir(mode=0o700)
    sursa = subprocess.run(['git', '-C', str(RAD), 'archive', '--format=tar', commit, 'core', 'scripts', 'static', 'tenant_template.sql',
                            '.gitignore'], capture_output=True, check=True).stdout
    fisiere = {
        'ruleaza.sh': b'set -eu\nexec /usr/bin/python3 -I -B ./calibrare.py\n',
        'calibrare.py': subprocess.run(['git', '-C', str(RAD), 'show', '%s:docs/dovezi/17_5_P0/calibrare/calibrare.py' % commit],
                                       capture_output=True, check=True).stdout,
        'verifica_margini_P0.py': din_ghid('verifica_margini_P0.py'),
        'verifica_parcurs_publicare.py': din_ghid('verifica_parcurs_publicare.py'),
        'conditii_predecesori.py': (GHID / 'conditii_predecesori.py').read_bytes(),
        'manifest_pachet.py': (GHID / 'manifest_pachet.py').read_bytes(),
        'sursa.tar': sursa,
        'commit.txt': (commit + '\n').encode(),
    }
    if doar:
        fisiere['doar.txt'] = (doar + '\n').encode()
    arh = dest / 'intrari.tar'
    with tarfile.open(arh, 'x') as t:
        for nume in ['ruleaza.sh'] + sorted(k for k in fisiere if k != 'ruleaza.sh'):
            m = tarfile.TarInfo(nume)
            m.mode, m.size, m.mtime = 0o600, len(fisiere[nume]), 0
            t.addfile(m, io.BytesIO(fisiere[nume]))
    os.chmod(arh, 0o600)
    print(hashlib.sha256(arh.read_bytes()).hexdigest())


if __name__ == '__main__':
    main(*sys.argv[1:])
