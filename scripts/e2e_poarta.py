# -*- coding: utf-8 -*-
"""scripts/e2e_poarta.py — testele de CAPĂT LA CAPĂT ale deficiențelor rezolvate, în browser, ca pas al porții (comanda Costin
09.10.2026, pct.8, verbatim în DECIZII: „Proba unei deficiențe «rezolvate» e un test de capăt la capăt în browser care reface pașii
contabilului din deficiență și verifică ce apare pe ecran și cifrele, cu captură. Testul rămâne permanent în poartă.”; regula de
direcție: „orice publicare la care pică o verificare a plasei nu se face”).

CE SE PROBEAZĂ e exact ce se COMITE: indexul git se exportă (`git checkout-index`) într-un director temporar, staticul lui se publică
LÂNGĂ el (`publica_static.py --din-arbore` scrie în `<export>/../iconta_publicat`, niciodată în directorul servit de producție),
aplicația pornește din export pe portul 8019, pe baza de TEST (`~/.iconta/test.env`), iar testele din `frontend_test/e2e/e2e_*.py` ale
exportului rulează contra ei. Capturile rămân în `<iesire>` (implicit /tmp/e2e_poarta/capturi), pentru raport și ZIP.
Exit: codul lui pytest (0 = verde); 3 = aplicația n-a pornit. Uz: python scripts/e2e_poarta.py [--arbore] [--doar=e2e_x.py] [<iesire>]
  --arbore       probează arborele de lucru în locul indexului (lucrul la teste, nu poarta)
  --doar=FIȘIER  numai acel fișier de teste (lucrul la un bloc; poarta rulează mereu tot)
  --mutatie=M.json  MUTAȚIA unui test: {"fisier": "...", "ancora": "...", "inlocuire": "..."} (sau o listă) se aplică pe COPIA
                    exportată, niciodată pe arborele de lucru — testul trebuie să pice (CLAUDE.md, verificarea prin mutație)
  E2E_PORT / E2E_TEMP  port și director de lucru (implicit 8019, /tmp/e2e_poarta) — rulări în paralel nu se calcă
"""
import fcntl
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("E2E_PORT", "8019"))
#: [09.10.2026, prins la prima rulare în paralel] Pornirea aplicației face DDL pe toate firmele (`migreaza_triggerele`, sub un lacăt
#: consultativ); o pornire peste o altă instanță care servește cereri pe aceeași bază de test a dus la un blocaj între procese pe care
#: Postgres nu-l vede. Deci O SINGURĂ aplicație de probă pe baza de test la un moment dat: lacăt exclusiv pe tot rulajul.
LACAT = "/tmp/e2e_poarta.lacat"
TEMP = os.environ.get("E2E_TEMP", "/tmp/e2e_poarta")


def _env_test():
    env = dict(os.environ)
    for cale in (os.path.expanduser("~/.iconta/test.env"), os.path.expanduser("~/.iconta/api_keys.env")):
        for linie in open(cale, encoding="utf-8"):
            linie = linie.strip()
            if linie.startswith("export "):
                linie = linie[7:]
            if "=" in linie and not linie.startswith("#"):
                k, v = linie.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    env.pop("BREVO_API_KEY", None)               # nimic trimis în afară din probă
    # [comanda Costin 09.10.2026 pct.7] AI simulat: nicio cerere spre model; testele pregătesc răspunsurile (`core.ai_client`)
    env.pop("ANTHROPIC_API_KEY", None)
    env["ICONTA_AI_SIMULAT"] = os.path.join(TEMP, "ai_simulat")
    env["ICONTA_BON_DIR"] = os.path.join(TEMP, "bonuri")   # [pct.7, deficiența 9] pozele bonurilor de probă nu stau lângă cele reale
    return env


def _exporta(din_arbore):
    arb = os.path.join(TEMP, "iconta_nou")
    shutil.rmtree(TEMP, ignore_errors=True)
    os.makedirs(arb)
    if din_arbore:
        fis = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], cwd=RAD, capture_output=True, text=True,
                             check=True).stdout.split("\n")
        for f in filter(None, fis):
            if os.path.isfile(os.path.join(RAD, f)) and not f.startswith("import_fiscalos/"):
                os.makedirs(os.path.dirname(os.path.join(arb, f)) or arb, exist_ok=True)
                shutil.copy2(os.path.join(RAD, f), os.path.join(arb, f))
    else:
        subprocess.run(["git", "checkout-index", "-a", "--prefix=%s/" % arb], cwd=RAD, check=True)
    os.symlink(os.path.join(RAD, "venv"), os.path.join(arb, "venv"))
    return arb


def _contor_schema(env, pune=None):
    """`(last_value, is_called)` al lui `tenant_schema_seq` pe baza de TEST; cu `pune`, îl readuce acolo. [09.10.2026, prins de poartă]
    Fiecare firmă sintetică a plasei consumă un număr de schemă: fără readucere, contorul (o cifră pe care PREDARE_LANT.md o arată,
    păzită de `core/test_predare_cifre.py`) creștea la fiecare poartă, iar următoarea poartă pica pe o cifră schimbată de plasă."""
    import psycopg2
    from core.tenant_provisioning import SECVENTA_SCHEMA
    with psycopg2.connect(env["DATABASE_URL"]) as c, c.cursor() as cur:
        if pune is None:
            cur.execute("SELECT last_value, is_called FROM %s" % SECVENTA_SCHEMA)
            return cur.fetchone()
        cur.execute("SELECT setval(%s, %s, %s)", (SECVENTA_SCHEMA, pune[0], pune[1]))
    return pune


def _scoate_firmele(env, contor=None):
    """Firmele probei, scoase încă o dată DUPĂ oprirea aplicației (ce a scris ea în fundal după ștergerea din fixtură); apoi contorul
    de scheme readus la valoarea de dinainte de rulare."""
    cale = os.path.join(TEMP, "firme_create.txt")
    if not os.path.exists(cale):
        if contor:
            _contor_schema(env, contor)
        return
    firme = [tuple(int(x) if i == 0 else x for i, x in enumerate(ln.split())) for ln in open(cale) if ln.strip()]
    vechi = {k: os.environ.get(k) for k in ("DATABASE_URL",)}
    os.environ["DATABASE_URL"] = env["DATABASE_URL"]           # baza de TEST a rulării
    sys.path.insert(0, os.path.join(RAD, "frontend_test", "e2e"))
    sys.path.insert(0, RAD)
    try:
        import curatenie
        from core import db
        db.init_pool()
        curatenie.scoate(db, firme)
        if contor:
            _contor_schema(env, contor)
    finally:
        for k, v in vechi.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _raspunde(port):
    try:
        return urllib.request.urlopen("http://127.0.0.1:%d/" % port, timeout=3).status == 200
    except Exception:  # noqa: BLE001
        return False


def _opreste(app):
    """SIGTERM pe grupul procesului, apoi SIGKILL dacă nu s-a oprit în 20 s (o pornire blocată în lifespan nu răspunde la TERM)."""
    for sem, asteapta in ((signal.SIGTERM, 20), (signal.SIGKILL, 10)):
        try:
            os.killpg(app.pid, sem)
        except ProcessLookupError:
            return
        try:
            app.wait(timeout=asteapta)
            return
        except subprocess.TimeoutExpired:
            continue


def main(argv):
    with open(LACAT, "w") as lac:
        fcntl.flock(lac, fcntl.LOCK_EX)          # așteaptă rândul: rulările se serializează, nu se calcă
        return _main(argv)


def _main(argv):
    din_arbore = "--arbore" in argv
    doar = [a.split("=", 1)[1] for a in argv if a.startswith("--doar=")]
    rest = [a for a in argv if not a.startswith("--")]
    iesire = rest[0] if rest else os.path.join(TEMP + "_capturi")
    shutil.rmtree(iesire, ignore_errors=True)
    os.makedirs(iesire)
    t0 = time.time()
    arb = _exporta(din_arbore)
    for m in [a.split("=", 1)[1] for a in argv if a.startswith("--mutatie=")]:
        import json
        muts = json.load(open(m, encoding="utf-8"))
        for mu in (muts if isinstance(muts, list) else [muts]):
            cale = os.path.join(arb, mu["fisier"])
            text = open(cale, encoding="utf-8").read()
            if mu["ancora"] not in text:
                print("[e2e] mutația nu se aplică: ancora lipsește din %s" % mu["fisier"])
                return 4
            open(cale, "w", encoding="utf-8").write(text.replace(mu["ancora"], mu["inlocuire"], 1))
            print("[e2e] MUTAȚIE aplicată pe copie: %s" % mu["fisier"])
    env = _env_test()
    os.makedirs(env["ICONTA_AI_SIMULAT"], exist_ok=True)
    os.makedirs(env["ICONTA_BON_DIR"], exist_ok=True)
    sys.path.insert(0, RAD)
    contor = _contor_schema(env)
    py = os.path.join(RAD, "venv", "bin", "python")
    r = subprocess.run([py, "scripts/publica_static.py", "--din-arbore"], cwd=arb, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        print("[e2e] publicarea staticului exportului a eșuat: %s" % (r.stdout + r.stderr).strip()[-400:])
        return 3
    if _raspunde(PORT):
        print("[e2e] portul %d răspunde deja (alt proces): refuz — un rezultat de la el n-ar fi al codului probat" % PORT)
        return 3
    log = open(os.path.join(iesire, "uvicorn.log"), "w")
    app = subprocess.Popen([py, "-m", "uvicorn", "main:app", "--port", str(PORT)], cwd=arb, env=env, stdout=log,
                           stderr=subprocess.STDOUT, start_new_session=True)
    try:
        for _ in range(90):
            if _raspunde(PORT):
                break
            time.sleep(2)
        else:
            print("[e2e] aplicația exportului n-a răspuns pe %d (vezi %s/uvicorn.log)" % (PORT, iesire))
            return 3
        print("[e2e] aplicația din %s pornită pe %d în %ds" % ("arbore" if din_arbore else "index", PORT, time.time() - t0))
        env.update({"PROBA_BAZA": "http://127.0.0.1:%d" % PORT, "E2E_CAPTURI": iesire, "E2E_TEMP": TEMP,
                    "PYTHONPATH": "%s:%s/frontend_test" % (arb, arb), "PYTHONDONTWRITEBYTECODE": "1"})
        dir_e2e = os.path.join(arb, "frontend_test", "e2e")
        tinte = [os.path.join(dir_e2e, d) for d in doar] or [dir_e2e]
        r = subprocess.run([py, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-o", "python_files=e2e_*.py",
                            "--rootdir", dir_e2e] + tinte,
                           cwd=arb, env=env, capture_output=True, text=True)
        out = r.stdout + r.stderr
        open(os.path.join(iesire, "pytest.log"), "w").write(out)
        print("\n".join(ln for ln in out.splitlines() if ln.startswith(("FAILED", "ERROR")))[-3000:])
        print("[e2e] %s (%ds; capturi în %s)" % (out.strip().splitlines()[-1] if out.strip() else "fără ieșire", time.time() - t0,
                                                 iesire))
        return r.returncode
    finally:
        _opreste(app)
        _scoate_firmele(env, contor)
        shutil.rmtree(TEMP, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
