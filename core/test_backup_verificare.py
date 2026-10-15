# -*- coding: utf-8 -*-
"""Alerta la eșecul backup-ului LOCAL (comanda Costin 14.10.2026, pct.5, verbatim în DECIZII „Lotul 2”) — cele două plase:
  1. `config/iconta-backup.sh`: un `pg_dump` căzut trimite email (curl Brevo) ÎNAINTE ca scriptul să cadă — până azi `set -e` îl
     oprea fără nicio alertă;
  2. `core/backup_verificare.py`: ultimul dump vechi / trunchiat / necitibil / lipsă -> `RuntimeError` (jobul cron alertează).
Totul pe fișiere și programe FALSE, într-un director temporar (fără bază, fără /var/backups).
MUTAȚII: `trap ... ERR` scos din script -> ROȘU; pragul de vârstă ocolit -> ROȘU; citirea integrală scoasă -> ROȘU."""
import json
import os
import subprocess
import time

import pytest

from core import backup_verificare as bv

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _exe(cale, corp):
    cale.write_text("#!/bin/sh\n" + corp)
    os.chmod(cale, 0o755)
    return str(cale)


def test_scriptul_alerteaza_cand_dumpul_local_cade(tmp_path):
    src = open(os.path.join(RAD, "config", "iconta-backup.sh"), encoding="utf-8").read()
    src = src.replace("DIR=/var/backups/iconta", "DIR=%s" % tmp_path)
    script = tmp_path / "backup.sh"
    script.write_text(src)
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    _exe(bin_ / "pg_dump", "exit 1\n")
    marca = tmp_path / "corp_trimis.json"
    _exe(bin_ / "curl", 'while [ $# -gt 0 ]; do [ "$1" = "-d" ] && printf "%%s" "$2" > %s; shift; done\n' % marca)
    r = subprocess.run(["bash", str(script)], capture_output=True, text=True,
                       env=dict({k: v for k, v in os.environ.items() if k != "ICONTA_ALERTA_EMAIL"},   # destinatarul implicit
                                PATH="%s:%s" % (bin_, os.environ["PATH"]), BREVO_API_KEY="x"))
    assert r.returncode != 0                                         # scriptul cade vizibil, ca înainte
    corp = json.loads(marca.read_text())                             # și a trimis alerta înainte (corpul cererii către Brevo)
    assert (corp["subject"], corp["to"]) == ("[iConta] Backup LOCAL esuat", [{"email": "contact@iconta.eu"}])


def _dump(d, nume, octeti, ore_in_urma):
    p = d / nume
    p.write_bytes(b"x" * octeti)
    t = time.time() - ore_in_urma * 3600
    os.utime(p, (t, t))
    return p


@pytest.fixture()
def pg_restore_bun(tmp_path):
    return _exe(tmp_path / "pg_restore_bun", 'echo "1; 0 0 TABLE DATA public t costin"\necho "2; 0 0 TABLE DATA public u costin"\n')


def test_dumpul_recent_si_citibil_trece(tmp_path, pg_restore_bun):
    _dump(tmp_path, "iconta_v2_1.dump", 200_000, 30)
    _dump(tmp_path, "iconta_v2_2.dump", 210_000, 2)
    r = bv.verifica(str(tmp_path), pg_restore=pg_restore_bun)
    assert (r["fisier"], r["octeti"], r["tabele_cu_date"]) == ("iconta_v2_2.dump", 210_000, 2)


def test_lipsa_vechimea_trunchierea_si_arhiva_necitibila_alarmeaza(tmp_path, pg_restore_bun):
    cazuri = {
        "lipsa": ([], "^Niciun backup local"),
        "vechi": ([("a", 200_000, 40)], "e vechi de 40.0 ore"),                                   # prag 26 h
        "mic": ([("a", 50_000, 1)], "are numai 50000 octeți"),                                    # prag 102.400
        "trunchiat": ([("a", 400_000, 2), ("b", 150_000, 1)], "probabil trunchiat"),              # 150.000 < 0,5 x 400.000
    }
    for nume, (dumpuri, motiv) in cazuri.items():
        d = tmp_path / nume
        d.mkdir()
        for n, octeti, ore in dumpuri:
            _dump(d, "iconta_v2_%s.dump" % n, octeti, ore)
        with pytest.raises(RuntimeError, match=motiv):
            bv.verifica(str(d), pg_restore=pg_restore_bun)
    d = tmp_path / "necitibil"
    d.mkdir()
    _dump(d, "iconta_v2_a.dump", 400_000, 1)
    rau = _exe(tmp_path / "pg_restore_rau", "echo 'pg_restore: error: corrupted' >&2\nexit 1\n")
    with pytest.raises(RuntimeError, match="nu se poate citi cu pg_restore"):
        bv.verifica(str(d), pg_restore=rau)
    # trunchiat la coadă: cuprinsul (-l) se citește, datele (-f) nu — cazul măsurat pe 15.10.2026 pe o copie reală tăiată la 70%
    coada = _exe(tmp_path / "pg_restore_coada", 'case "$1" in -l) echo "1; 0 0 TABLE DATA public t costin";; '
                 '*) echo "pg_restore: error: could not read from input file: end of file" >&2; exit 1;; esac\n')
    with pytest.raises(RuntimeError, match="nu se poate citi integral cu pg_restore"):
        bv.verifica(str(d), pg_restore=coada)


def test_jobul_e_supravegheat_si_backupul_nu_mai_e_scutit():
    from core import cron
    assert cron.RITMURI["backup_verificare"] == 50
    assert cron.NESUPRAVEGHEATE["iconta-backup"].endswith("verificat zilnic de backup_verificare")
