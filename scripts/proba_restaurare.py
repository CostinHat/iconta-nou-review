# -*- coding: utf-8 -*-
"""scripts/proba_restaurare.py — PROBA DE RESTAURARE a backup-ului bazei, pe o bază SEPARATĂ de pe același server, ștearsă după probă.

Comanda Costin 14.10.2026, pct.5 (verbatim în DECIZII „Lotul 2”): „fă o probă de restaurare pe o bază separată pe același server,
ștearsă după probă. În raport numai cifre (număr de scheme, de rânduri, sume de control), fără date.”

DOUĂ MODURI:
  snapshot (implicit) — dump NOU al producției, făcut cu `pg_dump --snapshot` din ACEEAȘI tranzacție (REPEATABLE READ, read-only) în
      care se calculează amprenta producției; restaurat; amprenta bazei restaurate trebuie să fie IDENTICĂ, tabel cu tabel (rânduri +
      md5 pe conținut). Exact, chiar dacă producția se mișcă între timp: ambele părți văd același snapshot.
  --dump <fișier> — restaurează un dump EXISTENT (ex. cel de noapte din /var/backups/iconta) și arată câte tabele au rămas identice cu
      producția de ACUM (diferențele sunt scrierile de după dump, nu defecte ale arhivei; criteriul aici e restaurarea fără eroare).

Amprenta e cea din `scripts/amprenta_productie.py` (sursă unică: `amprenta`, `globala`, `compara`). Ieșirea are NUMAI cifre: scheme,
tabele, rânduri, numărul tabelelor identice, sume de control sha256 — niciun nume de firmă, nicio valoare din rânduri. Dump-ul de
snapshot se scrie în ~/backups_db (mod 600) și se șterge după probă; baza de probă se șterge (`DROP DATABASE ... WITH (FORCE)`) și se
verifică absența ei, inclusiv la eșec.

Folosire (acreditările producției în mediu: DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD):
  (set -a; . ~/.iconta/db.env; set +a; ./venv/bin/python scripts/proba_restaurare.py [--dump /var/backups/iconta/iconta_v2_X.dump])
Necesită `sudo -n -u postgres psql` (crearea și ștergerea bazei, restaurarea ca superuser — rolurile și extensiile din dump).
"""
from __future__ import annotations

import datetime
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import amprenta_productie as ap  # noqa: E402

BAZA_PROBA = "iconta_proba_restaurare"
DIR_DUMP = os.path.expanduser("~/backups_db")
_NUME = re.compile(r"^[a-z_][a-z0-9_]*$")


def _psql_postgres(sql, baza="postgres"):
    r = subprocess.run(["sudo", "-n", "-u", "postgres", "psql", "-X", "-At", "-v", "ON_ERROR_STOP=1", "-d", baza, "-c", sql],
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("psql (postgres) a eșuat, cod %d: %s" % (r.returncode, r.stderr.strip()[:300]))
    return r.stdout.strip()


def _pg_dump(env, argumente):
    """`pg_dump` pe baza din mediu; parola îi ajunge printr-un fișier `.pgpass` temporar (mod 600, șters după), nu prin mediu."""
    import tempfile
    port = env.get("DB_PORT", "5432")
    with tempfile.NamedTemporaryFile("w", prefix="pgpass_", delete=False) as f:
        f.write(":".join([env["DB_HOST"], port, env["DB_NAME"], env["DB_USER"], env["DB_PASSWORD"]]) + "\n")
    try:
        os.chmod(f.name, 0o600)
        return subprocess.run(["pg_dump", "-h", env["DB_HOST"], "-p", port, "-U", env["DB_USER"], "-d", env["DB_NAME"]] + argumente,
                              capture_output=True, text=True, env=dict(env, PGPASSFILE=f.name))
    finally:
        os.remove(f.name)


def _conn(env, baza):
    import psycopg2
    return psycopg2.connect(host=env["DB_HOST"], port=int(env.get("DB_PORT", "5432")), dbname=baza, user=env["DB_USER"],
                            password=env["DB_PASSWORD"], connect_timeout=10)


def _rezumat(a):
    """Numai cifre: scheme, tabele, rânduri, suma de control globală."""
    scheme = {k.split(".", 1)[0] for k in a}
    return {"scheme": len(scheme), "scheme_firma": sum(1 for s in scheme if s.startswith("tenant_")), "tabele": len(a),
            "randuri": sum(v["randuri"] for v in a.values()), "md5_omise": sum(1 for v in a.values() if v["md5_omis"]),
            "sha256": ap.globala(a)}


def _restaureaza(dump, env):
    if _psql_postgres("SELECT count(*) FROM pg_database WHERE datname = '%s'" % BAZA_PROBA) != "0":
        raise RuntimeError("baza %s există deja — nu o suprascriu; se șterge de mână după ce se vede de unde vine" % BAZA_PROBA)
    coll = _psql_postgres("SELECT datcollate || '|' || datctype FROM pg_database WHERE datname = '%s'" % env["DB_NAME"]).split("|")
    _psql_postgres("CREATE DATABASE %s OWNER %s TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE '%s' LC_CTYPE '%s'"
                   % (BAZA_PROBA, env["DB_USER"], coll[0], coll[1]))
    p1 = subprocess.Popen(["pg_restore", "-f", "-", dump], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.run(["sudo", "-n", "-u", "postgres", "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-d", BAZA_PROBA],
                        stdin=p1.stdout, capture_output=True, text=True)
    p1.stdout.close()
    err1 = p1.stderr.read().decode("utf-8", "replace")
    p1.wait()
    if p1.returncode != 0 or p2.returncode != 0:
        raise RuntimeError("restaurarea a eșuat: pg_restore cod %d, psql cod %d: %s" %
                           (p1.returncode, p2.returncode, (err1 + p2.stderr).strip()[:400]))


def _amprenta_restaurata(env):
    conn = _conn(env, BAZA_PROBA)
    conn.set_session(readonly=True, autocommit=True)
    try:
        with conn.cursor() as cur:
            return ap.amprenta(cur)
    finally:
        conn.close()


def _sterge():
    _psql_postgres("DROP DATABASE IF EXISTS %s WITH (FORCE)" % BAZA_PROBA)
    return _psql_postgres("SELECT count(*) FROM pg_database WHERE datname = '%s'" % BAZA_PROBA)


def main(argv):
    env = os.environ
    lipsa = [k for k in ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD") if not env.get(k)]
    if lipsa:
        print("PICAT: lipsesc din mediu %s — nu ghicesc baza" % ", ".join(lipsa))
        return 2
    if not (_NUME.match(env["DB_NAME"]) and _NUME.match(env["DB_USER"])):
        print("PICAT: nume de bază / rol neașteptat")
        return 2
    dump_dat = argv[2] if len(argv) >= 3 and argv[1] == "--dump" else None
    dump_snapshot = None
    cod = 1
    try:
        prod = _conn(env, env["DB_NAME"])
        prod.set_session(isolation_level="REPEATABLE READ", readonly=True)
        try:
            with prod.cursor() as cur:
                cur.execute("SELECT pg_export_snapshot()")
                snap = cur.fetchone()[0]
                if dump_dat is None:
                    os.makedirs(DIR_DUMP, exist_ok=True)
                    dump_snapshot = os.path.join(DIR_DUMP, "proba_restaurare_%s.dump" % datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
                    r = _pg_dump(env, ["-Fc", "--snapshot=%s" % snap, "-f", dump_snapshot])
                    if r.returncode != 0:
                        raise RuntimeError("pg_dump a eșuat, cod %d: %s" % (r.returncode, r.stderr.strip()[:300]))
                    os.chmod(dump_snapshot, 0o600)
                a_prod = ap.amprenta(cur)
            prod.rollback()
        finally:
            prod.close()
        dump = dump_dat or dump_snapshot
        print("mod: %s" % ("dump existent" if dump_dat else "snapshot (dump nou + amprenta producției din aceeași tranzacție)"))
        print("dump: %d octeți" % os.path.getsize(dump))
        _restaureaza(dump, env)
        print("restaurare: fără eroare (pg_restore 0, psql ON_ERROR_STOP 0)")
        a_rest = _amprenta_restaurata(env)
        rp, rr = _rezumat(a_prod), _rezumat(a_rest)
        schimbate, aparute, disparute = ap.compara(a_prod, a_rest)
        for k in ("scheme", "scheme_firma", "tabele", "randuri", "md5_omise"):
            print("%-13s productie %9d | restaurat %9d" % (k, rp[k], rr[k]))
        print("tabele identice (rânduri + md5): %d din %d" % (len(set(a_prod) & set(a_rest)) - len(schimbate), len(a_prod)))
        print("tabele diferite %d | doar în producție %d | doar în restaurare %d" % (len(schimbate), len(disparute), len(aparute)))
        print("sha256 productie: %s" % rp["sha256"])
        print("sha256 restaurat: %s" % rr["sha256"])
        identic = not (schimbate or aparute or disparute)
        if dump_dat:
            cod = 0
            print("VERDICT: dump-ul existent se restaurează fără eroare; %s" %
                  ("identic cu producția de acum" if identic else "diferențele = scrierile de după dump"))
        else:
            cod = 0 if identic else 1
            print("VERDICT: %s" % ("RESTAURARE IDENTICĂ cu producția (același snapshot)" if identic else "RESTAURARE DIFERITĂ — PICAT"))
    except Exception as e:  # noqa: BLE001 — proba raportează orice eșec și trece totuși prin ștergere
        print("PICAT: %s" % e)
    finally:
        try:
            print("baza de probă după DROP: %s (0 = ștearsă)" % _sterge())
        except Exception as e:  # noqa: BLE001
            print("PICAT la ștergerea bazei de probă: %s" % e)
            cod = 1
        if dump_snapshot and os.path.exists(dump_snapshot):
            os.remove(dump_snapshot)
            print("dump-ul de probă șters: %s" % ("da" if not os.path.exists(dump_snapshot) else "NU"))
    return cod


if __name__ == "__main__":
    sys.exit(main(sys.argv))
