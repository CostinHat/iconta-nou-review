# -*- coding: utf-8 -*-
"""scripts/masoara_concurenta.py — ce se întâmplă când mai mulți contabili apasă deodată.

**DE CE EXISTĂ.** Curba P3 măsoară o cerere singură: cât costă ea în interogări, conexiuni și
timp. Dar pool-ul are un plafon (`ICONTA_POOL_MAX`, azi 10), iar plafonul nu se vede niciodată
într-o măsurătoare secvențială — o rută care ia 3 conexiuni pe rând nu atinge niciodată 10, oricât
de multe cereri ai face **una după alta**.

**DE-AIA TOTALUL NU E CRITERIUL.** „Achiziții totale < maxconn" nu spune nimic despre capacitate:
totalul se acumulează în timp, plafonul se atinge în același moment. Ce se măsoară aici e
**numărul de conexiuni SIMULTANE**, prin eșantionarea lui `pg_stat_activity` în timpul rafalei, pe
backendurile pornite de chiar serverul ăsta (pid-urile de dinainte se exclud).

**PE UN SERVER PROPRIU, NU PE PRODUCȚIE.** Se pornește un `uvicorn` pe un port liber, din arborele
de lucru. A trage 10 cereri × 1000 de firme în procesul viu ar fi un test de încărcare pe clienți
adevărați, nu o măsurătoare.

**CE NU MĂSOARĂ, declarat:** rețeaua reală (totul e pe `127.0.0.1`), mai multe procese de
aplicație (aici e unul singur, cu pool-ul lui), și încărcarea concurentă a lucrătorului de fundal
(oprit pe durata măsurătorii n-ar fi realist, pornit ar adăuga zgomot neatribuibil — rulează, și
conexiunile lui intră în numărătoare, fiindcă și în producție intră).
"""
from __future__ import annotations

import io
import json
import os
import socket
import statistics
import subprocess
import sys
import threading
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import masoara_rute_portofoliu as MR  # noqa: E402

#: Ruta cea mai grea a fiecărui val — cea cu cel mai mare răspuns, deci cel mai mult de serializat.
RUTE = {
    "val A": "/supervizor",
    "val B": "/migrare/parteneri",
    "P2 (martor)": "/control-fiscal",
}
NIVELE = (1, 2, 5, 10)
CERERI_PER_NIVEL = 20
N_FIRME = 1000


def _port_liber():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def _pids(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT pid FROM pg_stat_activity WHERE datname = current_database()")
        return {r[0] for r in cur.fetchall()}


def _conexiune_proprie():
    """O conexiune DIRECTĂ, în afara pool-ului aplicației.

    **De ce nu una din pool.** Prima formă a eșantionatorului cerea pool-ului o conexiune la
    fiecare probă și scădea `1` din rezultat, „ca să nu se numere pe sine". Fudge-ul ăla a picat
    calibrarea: pool-ul REFOLOSEȘTE conexiuni, iar pid-ul refolosit era deja în linia de bază —
    deci se scădea unul care nu trebuia scăzut, și 6 conexiuni ținute deodată se raportau ca 5.
    *O corecție cu o constantă e semnul că nu știi ce numeri.*

    Cu o conexiune proprie, deschisă ÎNAINTEA liniei de bază, ea intră în linia de bază ca oricare
    alta și nu se mai scade nimic. Rămâne deschisă toată măsurătoarea, deci nu adaugă și nu scoate
    backenduri în timpul ei."""
    import psycopg2
    from core import db as _db
    return psycopg2.connect(_db.dsn_din_config(_db.config_din_env()))


class Esantionator(threading.Thread):
    """Numără, des, câte backenduri NOI sunt deschise deodată. Maximul lui e răspunsul.

    NOI = absente din linia de bază. Nu cumulat: un pid care apare și dispare nu rămâne numărat,
    fiindcă fiecare probă recitește mulțimea curentă. Probat de `calibreaza()`, direcția (b)."""

    def __init__(self, dinainte, conn):
        super().__init__(daemon=True)
        self.dinainte = dinainte
        self.conn = conn
        self.maxim = 0
        self.probe = 0
        self.opreste = threading.Event()

    def run(self):
        while not self.opreste.is_set():
            try:
                self.conn.rollback()          # instantaneu proaspăt, nu vederea tranzacției vechi
                noi = _pids(self.conn) - self.dinainte
                self.maxim = max(self.maxim, len(noi))
                self.probe += 1
            except Exception:
                pass
            time.sleep(0.004)


def _cere(url, tok, rezultate, idx):
    import httpx
    t0 = time.perf_counter()
    try:
        r = httpx.get(url, headers={"Authorization": "Bearer " + tok}, timeout=60.0)
        rezultate[idx] = (r.status_code, time.perf_counter() - t0, None)
    except Exception as e:
        rezultate[idx] = (None, time.perf_counter() - t0, type(e).__name__ + ": " + str(e)[:120])


def rafala(baza, ruta, tok, k, cereri, dinainte, obs):
    """`k` cereri deodată, repetat până la `cereri`. Întoarce percentile + erori + simultane."""
    es = Esantionator(dinainte, obs)
    es.start()
    latente, erori, statusuri = [], [], {}
    facute = 0
    try:
        while facute < cereri:
            lot = min(k, cereri - facute)
            rez = [None] * lot
            fire = [threading.Thread(target=_cere, args=(baza + ruta, tok, rez, i))
                    for i in range(lot)]
            for f in fire:
                f.start()
            for f in fire:
                f.join()
            for st, dt, er in rez:
                latente.append(dt)
                statusuri[st] = statusuri.get(st, 0) + 1
                if er:
                    erori.append(er)
            facute += lot
    finally:
        es.opreste.set()
        es.join(timeout=2)
    latente.sort()

    def pct(p):
        if not latente:
            return None
        i = min(len(latente) - 1, int(round(p / 100.0 * (len(latente) - 1))))
        return round(latente[i] * 1000, 1)

    return {
        "simultane_cerute": k, "cereri": facute,
        "p50_ms": pct(50), "p95_ms": pct(95), "p99_ms": pct(99),
        "min_ms": round(latente[0] * 1000, 1), "max_ms": round(latente[-1] * 1000, 1),
        "medie_ms": round(statistics.mean(latente) * 1000, 1),
        "statusuri": {str(k2): v for k2, v in statusuri.items()},
        "erori": erori[:5], "nr_erori": len(erori),
        "conexiuni_simultane_maxim": es.maxim, "probe_esantionator": es.probe,
    }


def calibreaza(verbose=True):
    """**Instrumentul măsoară SIMULTANEITATE? Se probează, în ambele direcții.**

    Afirmația lui e „atâtea conexiuni au fost deschise ÎN ACELAȘI MOMENT". Un eșantionator care ar
    număra, din greșeală, backendurile *cumulat* ar da exact aceeași cifră mare — și n-am avea cum
    să știm. De aceea i se dau două lumi construite anume:

      (a) **K conexiuni ținute deodată** -> TREBUIE să raporteze cel puțin K. Dacă ratează, cifra
          din raport ar fi o subestimare tăcută, iar „pool-ul n-a fost atins" ar fi o minciună
          liniștitoare.
      (b) **K conexiuni una după alta**, fiecare închisă înainte de următoarea -> TREBUIE să
          raporteze mult sub K. *Asta e mutația pe propriul mod de eșec:* un instrument care
          numără cumulat trece (a) fără să clipească și pică (b). Fără (b), (a) singură n-ar
          dovedi nimic despre simultaneitate.

    Întoarce `(ok, detaliu)`. Nu se măsoară nimic dacă asta nu trece."""
    from core import db as _db
    _db.init_pool()
    K = 6
    obs = _conexiune_proprie()
    dinainte = _pids(obs)
    obs.rollback()

    # ── (a) deodată: K backenduri NOI, ținute în același timp ──────────────
    porneste, gata = threading.Event(), threading.Barrier(K + 1)

    def _tine():
        c2 = _conexiune_proprie()
        try:
            with c2.cursor() as cur:
                cur.execute("SELECT 1")
            gata.wait()
            porneste.wait(timeout=5)
        finally:
            c2.close()

    fire = [threading.Thread(target=_tine, daemon=True) for _ in range(K)]
    for f in fire:
        f.start()
    gata.wait(timeout=10)
    es_a = Esantionator(dinainte, obs)
    es_a.start()
    time.sleep(0.35)
    es_a.opreste.set(); es_a.join(timeout=2)
    porneste.set()
    for f in fire:
        f.join(timeout=5)

    # ── (b) una după alta: aceleași K, dar niciodată două deodată ──────────
    es_b = Esantionator(dinainte, obs)
    es_b.start()
    for _ in range(K):
        c2 = _conexiune_proprie()
        with c2.cursor() as cur:
            cur.execute("SELECT 1")
        c2.close()
        time.sleep(0.05)
    es_b.opreste.set(); es_b.join(timeout=2)
    obs.close()

    vede_simultan = es_a.maxim >= K
    nu_numara_cumulat = es_b.maxim < K
    ok = vede_simultan and nu_numara_cumulat and es_a.probe > 0 and es_b.probe > 0
    det = {"K": K, "a_deodata_maxim": es_a.maxim, "b_pe_rand_maxim": es_b.maxim,
           "probe_a": es_a.probe, "probe_b": es_b.probe,
           "vede_simultaneitatea": vede_simultan, "NU_numara_cumulat": nu_numara_cumulat}
    if verbose:
        print("CALIBRARE masoara_concurenta — simultan vs cumulat:")
        print("  (a) %d conexiuni TINUTE deodata -> maxim vazut %d  (trebuie >= %d): %s"
              % (K, es_a.maxim, K, vede_simultan))
        print("  (b) %d conexiuni UNA DUPA ALTA  -> maxim vazut %d  (trebuie <  %d): %s"
              % (K, es_b.maxim, K, nu_numara_cumulat))
        print("      (b) e mutatia: un contor cumulat ar trece (a) si ar pica (b)")
        print("  probe: %d / %d" % (es_a.probe, es_b.probe))
        print("  VERDICT: %s" % ("OK" if ok else "PICAT"))
    return ok, det


def main():
    from core import db as _db
    _db.init_pool()
    cfg = _db.config_din_env() if hasattr(_db, "config_din_env") else None
    maxconn = int(os.environ.get("ICONTA_POOL_MAX", "10"))

    # ORDINEA CONTEAZĂ, și a costat o rulare: portofoliul se construiește DUPĂ ce serverul e sus.
    #
    # Pornirea e fail-closed — `lifespan()` face DDL + `migreaza_triggerele` pe TOȚI tenanții
    # înainte de a accepta cereri. Cu 1000 de firme sintetice deja în bază, asta înseamnă ~30.000
    # de triggere puse la pornire, iar `uvicorn` n-a apucat să răspundă în 120 s. Cu ordinea
    # inversată, pornirea vede doar firmele reale, iar firmele sintetice își primesc triggerele de
    # la `construieste`, ca la orice altă măsurătoare.
    with _db.get_conn() as conn:
        MR.curata(conn)
        conn.commit()

    port = _port_liber()
    baza = "http://127.0.0.1:%d" % port
    print("── uvicorn pe %s ──" % baza, flush=True)
    # Observatorul se deschide ÎNAINTE de linia de bază, deci intră în ea; uvicorn pornește DUPĂ,
    # deci toate backendurile lui sunt noi prin construcție.
    obs = _conexiune_proprie()
    dinainte = _pids(obs)
    obs.rollback()
    # Ieșirea serverului se PĂSTREAZĂ. Cu `DEVNULL`, un eșec de pornire n-a lăsat nimic în urmă
    # și a trebuit ghicit — iar ghicitul e exact ce n-are voie să facă un instrument de măsură.
    cale_log = os.path.join(RAD, "masuratori", "p3", "concurenta_uvicorn.log")
    os.makedirs(os.path.dirname(cale_log), exist_ok=True)
    jurnal_srv = io.open(cale_log, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [os.path.join(RAD, "venv/bin/python"), "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "info"],
        cwd=RAD, stdout=jurnal_srv, stderr=subprocess.STDOUT)
    out = {"commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                                    cwd=RAD).stdout.strip(),
           "N_FIRME": N_FIRME, "POOL_MAX": maxconn, "cfg": str(cfg)[:80], "rute": {}}
    try:
        import httpx
        gata = False
        for _ in range(180):
            try:
                httpx.get(baza + "/", timeout=2.0)
                gata = True
                break
            except Exception:
                time.sleep(1)
        if not gata:
            jurnal = ""
            try:
                jurnal = io.open(cale_log, encoding="utf-8", errors="replace").read()[-2000:]
            except Exception:
                pass
            raise RuntimeError("uvicorn n-a pornit in 180s. Jurnalul lui:\n" + jurnal)
        print("   pornit.", flush=True)

        print("── se construiește portofoliul sintetic (N=%d) ──" % N_FIRME, flush=True)
        with _db.get_conn() as conn:
            uid, _ids = MR.construieste(conn, N_FIRME, procent_invalidat=10, rece=False)
            tok = MR._token(conn, uid)
        print("   %d firme." % N_FIRME, flush=True)

        for eticheta, ruta in RUTE.items():
            print("── %s · %s ──" % (eticheta, ruta), flush=True)
            out["rute"][ruta] = {"val": eticheta, "nivele": []}
            for k in NIVELE:
                r = rafala(baza, ruta, tok, k, CERERI_PER_NIVEL, dinainte, obs)
                out["rute"][ruta]["nivele"].append(r)
                print("   k=%-3d p50=%-7s p95=%-7s p99=%-7s max_simultane=%-3s erori=%d %s"
                      % (k, r["p50_ms"], r["p95_ms"], r["p99_ms"],
                         r["conexiuni_simultane_maxim"], r["nr_erori"], r["statusuri"]),
                      flush=True)
    finally:
        obs.close()
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
        try:
            jurnal_srv.close()
        except Exception:
            pass
        with _db.get_conn() as conn:
            MR.curata(conn)
            conn.commit()

    cale = os.path.join(RAD, "masuratori", "p3", "concurenta.json")
    os.makedirs(os.path.dirname(cale), exist_ok=True)
    with open(cale, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\nscris: %s" % cale)
    return out


if __name__ == "__main__":
    ok, det = calibreaza()
    print()
    if not ok:
        print("NU SE MASOARA NIMIC: instrumentul n-a trecut calibrarea. %s" % det)
        sys.exit(2)
    main()
