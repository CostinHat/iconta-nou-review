# -*- coding: utf-8 -*-
"""scripts/calibreaza_16_4.py — calibrarea comenzii 16.4 (pct.1 și pct.2). NU e o rulare a porții. Scrie docs/dovezi/16_4/calibrare.txt: un rând pe caz, „ATINS” sau „RATAT”; ieșire 1 dacă un caz e ratat.
  calibreaza_16_4.py <parte>...   părți: dovada (pct.1: rândurile refuzate de cere_dovada + lipsuri_dovada pe tot DEFICIENTE.md, înainte / după), jurnale (pct.2: faze_stop pe jurnalele reale ale loturilor
  16.2-C, 16.3, 16.3-A), sigterm (pct.2 (v): lansatorul cu un parcurs fals, oprit cu SIGTERM; lacătul de test adevărat, http.server local, jurnal propriu prin --jurnal). Fără argument: toate.
Numără rândurile lot=16.4 din jurnalul comun înainte și după fiecare parte (diferența trebuie să fie zero: în jurnalul comun apar numai fazele adevărate ale lotului)."""
import os
import signal
import subprocess
import sys
import tempfile
import time
import types

AICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AICI)
RAD = os.path.dirname(AICI)
LOT = "16.4"
DOVEZI = os.path.join(RAD, "docs", "dovezi", "16_4")
CALIB = os.path.join(DOVEZI, "calibrare")
BAZA_COMMIT = "8b969d6e"
REZ = []


def caz(nume, ok, detaliu=""):
    REZ.append((nume, ok, detaliu))
    print("%s  %s  %s" % ("ATINS" if ok else "RATAT", nume, str(detaliu).replace("\n", " ")[:220]))


def git(*a):
    return subprocess.run(["git", *a], cwd=RAD, capture_output=True, text=True).stdout


def jurnal_comun():
    import jurnal_lot as JL
    return os.path.join(os.path.dirname(JL.comun()), ".lot_jurnal.log")


def randuri_lot_in_comun():
    """Numărul rândurilor lot=16.4 din jurnalul comun."""
    return sum(1 for ln in open(jurnal_comun(), encoding="utf-8") if ln.split("\t")[0] == LOT)


def modul_td(sursa, nume):
    """core/test_deficiente.py dintr-o sursă dată (commitul de bază), încărcat ca modul cu __file__ în depozit (rădăcina _RAD rămâne a depozitului)."""
    m = types.ModuleType(nume)
    m.__file__ = os.path.join(RAD, "core", "test_deficiente.py")
    exec(compile(sursa, m.__file__, "exec"), m.__dict__)   # noqa: S102 — calibrare: codul commitului de bază
    return m


def refuzate(td, registru_text):
    """[(nr, motiv)] — rândurile `rezolvată` pe care cere_dovada le cere și lipsuri_dovada le refuză — și mulțimea numerelor care cer dovada."""
    vechi = td.randuri_la_pornirea_lotului_11()
    rd = td.randuri(registru_text)
    cer = [r for r in rd if td.cere_dovada(r, vechi)]
    return sorted((r["nr"], x) for r in cer for x in td.lipsuri_dovada(r)), sorted(r["nr"] for r in cer)


def dovada():
    """pct.1: lista rândurilor refuzate înainte (codul și registrul de la BAZA_COMMIT) și după (codul și registrul curente), identică în afara lui 278.1; testele :96, :132, :318–324 verzi."""
    inainte_cod = git("show", "%s:core/test_deficiente.py" % BAZA_COMMIT)
    inainte_reg = git("show", "%s:DEFICIENTE.md" % BAZA_COMMIT)
    dupa_reg = open(os.path.join(RAD, "DEFICIENTE.md"), encoding="utf-8").read()
    ref_i, cer_i = refuzate(modul_td(inainte_cod, "td_inainte"), inainte_reg)
    ref_d, cer_d = refuzate(modul_td(open(os.path.join(RAD, "core", "test_deficiente.py"), encoding="utf-8").read(), "td_dupa"), dupa_reg)
    caz("1 rânduri care cer dovada: înainte %d, după %d; în plus după: %s" % (len(cer_i), len(cer_d), sorted(set(cer_d) - set(cer_i))), sorted(set(cer_d) - set(cer_i)) == ["278.1"] and not set(cer_i) - set(cer_d), "")
    caz("1 rânduri refuzate înainte / după (în afara lui 278.1): %d / %d, identice" % (len(ref_i), len(ref_d)), [x for x in ref_i if x[0] != "278.1"] == [x for x in ref_d if x[0] != "278.1"],
        "înainte %s | după %s" % (ref_i[:3], ref_d[:3]))
    caz("1 278.1 după: cere dovada și nu e refuzat", "278.1" in cer_d and not [x for x in ref_d if x[0] == "278.1"], [x for x in ref_d if x[0] == "278.1"])
    # direcția opusă: codul vechi pe registrul nou refuză 278.1 (rezolvată fără captură) — modificarea e cea care o scoate
    ref_vechi_nou, _ = refuzate(modul_td(inainte_cod, "td_inainte2"), dupa_reg)
    caz("1 codul vechi pe registrul nou refuză 278.1 (fără captură pe firmele de test): %d motive" % len([x for x in ref_vechi_nou if x[0] == "278.1"]), any(x[0] == "278.1" for x in ref_vechi_nou), "")
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "core/test_deficiente.py", "-k",
                        "test_rezolvata_are_commit_si_test_de_capat_la_capat or test_rezolvata_are_testul_e2e_in_harta_portii or test_garda_dovezii_nu_e_vida or test_dovada_prin_test_pilot"],
                       cwd=RAD, capture_output=True, text=True, env=dict(os.environ, LOT_JURNAL=os.path.join(CALIB, "jurnal_lansator.log")))   # pluginul pytest scrie faze: nu în jurnalul comun
    caz("1 testele :96/:132/:318–324 și calibrarea 278.1 verzi", p.returncode == 0, p.stdout.strip().splitlines()[-1] if p.stdout.strip() else p.stderr[-120:])


def jurnale():
    """pct.2: faze_stop(rows, unelte=False) pe rândurile reale ale loturilor, copiate din jurnalul comun în fișiere de probă."""
    import jurnal_lot as JL
    import publica_lot as PL
    asteptat = {"16.2-C": None, "16.3": "scrisă de mână", "16.3-A": "lipsește din jurnal"}
    for lot, text in asteptat.items():
        fisier = os.path.join(CALIB, "jurnal_real_%s.log" % lot.replace(".", "_"))
        with open(fisier, "w", encoding="utf-8") as f:
            f.writelines(ln for ln in open(jurnal_comun(), encoding="utf-8") if ln.split("\t")[0] == lot)
        rows = [r for r in JL._citeste(fisier) if r[0] == lot and len(r) > 8]
        stop = PL.faze_stop(rows, False)
        ok = (stop == []) if text is None else any(text in m for m in stop)
        caz("2 faze_stop(unelte=False) pe jurnalul real al lotului %s (%s, %d rânduri): %s" % (lot, os.path.relpath(fisier, RAD), len(rows), "fără STOP" if text is None else "STOP «%s»" % text), ok, stop)


def sigterm():
    """pct.2 (v): lansatorul pornit cu parcursul fals și oprit cu SIGTERM scrie sfârșitul «intrerupt» marcat; același lansator fără handler (copia de la baza lotului) nu scrie sfârșitul."""
    import jurnal_lot as JL
    import verifica_pas as VP
    import http.server
    import threading
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    baza = "http://127.0.0.1:%d" % srv.server_address[1]
    csv_ = os.path.join(DOVEZI, "jurnal_verificare_calibrare.csv")
    if not os.path.exists(csv_):
        open(csv_, "w", encoding="utf-8").write(",".join(VP.CAMPURI) + "\n")
    jurnal = os.path.join(CALIB, "jurnal_lansator.log")
    vechi_lansator = os.path.join(AICI, "lanseaza_verificator_inainte_164.py")
    try:
        for eticheta, script in (("cu handler (lansatorul lotului)", os.path.join(AICI, "lanseaza_verificator.py")), ("fără handler (copia de la %s)" % BAZA_COMMIT, vechi_lansator)):
            if script == vechi_lansator:
                open(vechi_lansator, "w", encoding="utf-8").write(git("show", "%s:scripts/lanseaza_verificator.py" % BAZA_COMMIT))
            par = "calib_sigterm_" + ("nou" if "cu handler" in eticheta else "vechi")
            marca = os.path.join(tempfile.mkdtemp(prefix="calib_sigterm_"), "marca")
            env = dict(os.environ, CALIB_MARCA=marca)
            env.pop("LACAT_TEST_PID", None)
            cmd = [sys.executable, script, "--lot", LOT, "--parcurs", os.path.join(CALIB, "parcurs_fals.py"), "--parcurgere", par, "--verificator", "code",
                   "--pasi-txt", os.path.join(CALIB, "pasi_fals.txt"), "--pasi-json", os.path.join(CALIB, "pasi_fals.json"), "--csv", csv_, "--baza", baza, "--jurnal", jurnal]
            p = subprocess.Popen(cmd, cwd=RAD, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
            try:
                for _ in range(240):
                    if os.path.exists(marca) or p.poll() is not None:
                        break
                    time.sleep(0.5)
                intrat = os.path.exists(marca)
                if intrat:
                    os.kill(p.pid, signal.SIGTERM)
                try:
                    cod = p.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    cod = None
            finally:
                try:
                    os.killpg(p.pid, signal.SIGKILL)   # Chromium / driverul rămas după un proces mort fără handler
                except ProcessLookupError:
                    pass
            iesire = (p.stdout.read() or "")[-200:]
            inc = [r for r in JL._citeste(jurnal) if r[0] == LOT and r[1] == "parcurs_code" and r[2] == "inceput" and ("parcurgere=" + par) in r[8]]
            sf = [r for r in JL._citeste(jurnal) if r[0] == LOT and r[1] == "parcurs_code" and r[2] == "sfarsit" and inc and r[6] == inc[-1][6]]
            if "cu handler" in eticheta:
                caz("2 (v) %s: parcursul fals oprit cu SIGTERM -> sfârșit «intrerupt» marcat (ieșire %s)" % (eticheta, cod),
                    intrat and bool(inc) and bool(sf) and sf[-1][5] == "intrerupt" and VP.faza_marcata_valida(inc[-1]) and VP.faza_marcata_valida(sf[-1]), iesire)
            else:
                caz("2 (v) %s: fără sfârșit în jurnal (ieșire %s)" % (eticheta, cod), intrat and bool(inc) and not sf, iesire)
    finally:
        srv.shutdown()
        if os.path.exists(vechi_lansator):
            os.remove(vechi_lansator)


PARTI = {"dovada": dovada, "jurnale": jurnale, "sigterm": sigterm}


def main(a):
    os.makedirs(CALIB, exist_ok=True)
    for p in a or list(PARTI):
        inainte = randuri_lot_in_comun()
        print("\n== %s ==" % p)
        PARTI[p]()
        dupa = randuri_lot_in_comun()
        caz("jurnalul comun, rânduri lot=%s înainte / după partea «%s»: %d / %d (diferența zero)" % (LOT, p, inainte, dupa), inainte == dupa, "")
    out = os.path.join(DOVEZI, "calibrare.txt")
    mod = "a" if os.environ.get("CALIB_ADAUGA") and os.path.exists(out) else "w"
    with open(out, mod, encoding="utf-8") as f:
        for nume, ok, det in REZ:
            f.write("%s  %s  %s\n" % ("ATINS" if ok else "RATAT", nume, str(det).replace("\n", " ")[:200]))
    print("\n%d cazuri, %d ratate -> %s" % (len(REZ), sum(not ok for _, ok, _ in REZ), os.path.relpath(out, RAD)))
    return 1 if any(not ok for _, ok, _ in REZ) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
