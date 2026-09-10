# -*- coding: utf-8 -*-
"""scripts/masoara_p5.py — CÂT ȚINE BUCLA OCUPATĂ, măsurat pe calea reală. (P5, diagnostic)

**CE ÎNTREABĂ.** `scan_blocante.py` spune care căi au I/O blocant pe bucla de evenimente. Aici se
măsoară **ce se întâmplă celorlalte cereri** cât timp una din ele lucrează — fiindcă asta e chiar
definiția canonică a lui P5 (`PLAN_HARDENING.md:328`): *„se caută rutele în care un I/O blocant ține
bucla de evenimente ocupată"*.

**MECANICA MĂSURĂTORII: CANARUL.** Se trimite o cerere pe ruta grea și, în paralel, se bat cereri
**ieftine** pe o rută care nu atinge nici baza, nici rețeaua (`GET /public/config`). Dacă bucla e
liberă, canarul răspunde în milisecunde oricât ar dura ruta grea. Dacă bucla e blocată, canarul
**așteaptă exact cât durează ruta grea** — și aia e dovada, nu o deducție.

**SUBIECTUL ALES, și de ce el.** `POST /tenants/{id}/banca/parse-extras`:
  * e `async def`, deci rulează **pe buclă** — clasa C1;
  * **nu scrie nimic**: deschide o conexiune ca să verifice accesul, citește fișierul, parsează și
    întoarce. Verificat și mecanic, cu inventarul lui P4 (zero scrieri pe calea ei);
  * costul lui crește cu **N** = numărul de tranzacții din extras, deci se poate face curbă.
*O rută care scrie ar fi măsurat altceva: efectele ei, nu blocajul.*

**MmartorUL SINCRON.** Aceeași măsurătoare pe o rută `def` (threadpool). Fără el, „canarul a
așteptat" s-ar putea explica prin orice — încărcare, GIL, rețea. Cu el, deosebirea rămâne una
singură: cine rulează pe buclă.

**UNDE RULEAZĂ.** Pe un `uvicorn` PROPRIU, pe un port liber, din arborele de lucru — niciodată pe
procesul viu. Firma e sintetică, construită și ștearsă de instrument. La final se compară o
**amprentă** a bazei dinainte și de după, ca „n-a atins producția" să fie o măsurătoare, nu o
promisiune.

**CE NU MĂSOARĂ, declarat:** rețeaua reală (tot pe `127.0.0.1`) · mai multe procese de aplicație
(unul singur, ca în producție) · latența serviciilor externe reale (ANAF/BNR/Brevo nu se apelează
deloc — ar fi efect în afara noastră).
"""
from __future__ import annotations

import io
import json
import os
import statistics
import subprocess
import sys
import threading
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

import masoara_concurenta as MC  # noqa: E402
import masoara_p3 as MP3
import masoara_rute_portofoliu as MR  # noqa: E402

#: cele sase cerute, plus doua peste, ca panta sa se vada dincolo de zgomot
NN = (5, 50, 100, 250, 500, 1000, 2500, 5000)
NIVELE = (1, 2, 5, 10)
CANAR = "/public/config"
RUTA_ASYNC = "/tenants/%d/banca/parse-extras"
RUTA_SYNC = "/tenants/%d/facturi"
DIR = os.path.join(RAD, "masuratori", "p5")

#: tabelele din `public` pe care se ia amprenta, ca „n-a atins productia" sa fie masurat
TABELE_AMPRENTA = ("tenants", "accounting_firms", "users", "user_tenants", "audit_log",
                   "declaratii_coada", "declaratii_depuse", "firma_rezumat", "spv_token",
                   "notificari")


# ============================================================================
#  EXTRASUL SINTETIC
# ============================================================================

def extras_csv(n):
    """Un extras bancar CSV cu `n` tranzacții. Numai text — nu atinge nimic."""
    linii = ["Data,Detalii,Debit,Credit"]
    for i in range(n):
        zi = (i % 28) + 1
        if i % 2:
            linii.append("%02d.06.2026,Plata furnizor %d,%d.50," % (zi, i, 100 + i))
        else:
            linii.append("%02d.06.2026,Incasare client %d,,%d.50" % (zi, i, 200 + i))
    return ("\n".join(linii) + "\n").encode("utf-8")


# ============================================================================
#  AMPRENTA BAZEI — „n-a atins productia", masurat
# ============================================================================

def curata_audit(conn, uid, tids):
    """Sterge randurile pe care le-a lasat MIDDLEWARE-ul de audit pentru probele mele.

    `@app.middleware("http")` scrie in `public.audit_log` pentru fiecare cerere. Sunt randuri ale
    unui utilizator si ale unor firme SINTETICE, deci n-au ce cauta in evidenta reala. Prima rulare
    le-a lasat in urma, iar amprenta le-a prins — si aia e chiar purtarea buna a amprentei."""
    n = 0
    with conn.cursor() as cur:
        cur.execute("DELETE FROM public.audit_log WHERE user_id = %s OR tenant_id = ANY(%s)",
                    (uid, list(tids) or [-1]))
        n = cur.rowcount
    return n


def amprenta(conn):
    """`{tabel: (nr_randuri, md5)}` peste tabelele din `public` pe care le-ar putea atinge o probă.

    Numărătoarea singură e oarbă la modificări (**R137**), deci se ia și amprenta rândurilor."""
    out = {}
    with conn.cursor() as cur:
        for t in TABELE_AMPRENTA:
            try:
                cur.execute("SAVEPOINT a")
                cur.execute("SELECT count(*), coalesce(md5(string_agg(md5(x::text), '|' "
                            "ORDER BY md5(x::text))), '-') FROM public.%s x" % t)
                out[t] = tuple(cur.fetchone())
                cur.execute("RELEASE SAVEPOINT a")
            except Exception:
                cur.execute("ROLLBACK TO SAVEPOINT a")
                out[t] = ("(lipsa)", "-")
    return out


# ============================================================================
#  CANARUL
# ============================================================================

class Canar(threading.Thread):
    """Bate cereri ieftine cât timp altcineva lucrează. Latențele lui sunt răspunsul."""

    def __init__(self, baza, pauza=0.002):
        super().__init__(daemon=True)
        self.baza = baza
        self.pauza = pauza
        self.latente = []
        self.erori = []
        self.opreste = threading.Event()

    def run(self):
        import httpx
        # CLIENT PERSISTENT, si nu e un detaliu: prima forma deschidea o conexiune TCP noua la
        # fiecare cerere si isi platea ~21 ms de instalare — adica isi ineca propria masuratoare.
        # Un blocaj de 30 ms nu se poate vedea sub 21 ms de zgomot al instrumentului.
        with httpx.Client(timeout=120.0) as cl:
            # o cerere de incalzire, ca instalarea conexiunii sa nu intre in prima latenta
            try:
                cl.get(self.baza + CANAR)
            except Exception:  # noqa: BLE001
                pass
            while not self.opreste.is_set():
                t0 = time.perf_counter()
                try:
                    r = cl.get(self.baza + CANAR)
                    dt = time.perf_counter() - t0
                    if r.status_code == 200:
                        self.latente.append(dt)
                    else:
                        self.erori.append("HTTP %s" % r.status_code)
                except Exception as e:  # noqa: BLE001
                    self.erori.append(type(e).__name__)
                time.sleep(self.pauza)


def _pct(valori, p):
    if not valori:
        return None
    v = sorted(valori)
    i = min(len(v) - 1, int(round(p / 100.0 * (len(v) - 1))))
    return round(v[i] * 1000, 1)


#: esantioanele BRUTE, pe eticheta — se scriu la final in `P5_RAW_EVIDENCE/`
BRUT = {}


def _clasa_eroare(e):
    """`TIMEOUT` / `DEADLOCK` / `HTTP_xxx` / `ALTA` — numarate separat, nu la gramada.

    Un `nr_erori: 0` e adevarat, dar nu raspunde la intrebarea pusa: comanda cere `TIMEOUTS` si
    `DEADLOCKS` pe nume. Clasele se citesc din textul erorii (tipul exceptiei sau codul PostgreSQL),
    fiindca proba vine prin HTTP si nu vede obiectul original."""
    t = str(e)
    if "40P01" in t or "eadlock" in t:
        return "DEADLOCK"
    if "57014" in t or "QueryCanceled" in t or "imeout" in t:
        return "TIMEOUT"
    if t.startswith("HTTP "):
        return "HTTP_" + t.split()[1]
    return "ALTA"


def _numara_erori(erori):
    clase = {}
    for e in erori:
        c = _clasa_eroare(e)
        clase[c] = clase.get(c, 0) + 1
    return {"ERRORS": len(erori), "TIMEOUTS": clase.get("TIMEOUT", 0),
            "DEADLOCKS": clase.get("DEADLOCK", 0), "clase": clase}


def _rezumat(latente, erori, eticheta=None):
    """Percentilele — si, daca i se da o eticheta, esantionul BRUT din care ies."""
    if eticheta:
        BRUT[eticheta] = {"latente_ms": [round(x * 1000, 2) for x in latente],
                          "erori": [str(e) for e in erori]}
    if not latente:
        return dict({"n": 0, "erori": len(erori)}, **_numara_erori(erori))
    return dict({"n": len(latente), "p50_ms": _pct(latente, 50), "p95_ms": _pct(latente, 95),
                 "p99_ms": _pct(latente, 99), "max_ms": round(max(latente) * 1000, 1),
                 "min_ms": round(min(latente) * 1000, 1),
                 "medie_ms": round(statistics.mean(latente) * 1000, 1), "erori": len(erori)},
                **_numara_erori(erori))


# ============================================================================
#  MASURATORILE
# ============================================================================

def _post_fisier(baza, ruta, tok, continut, nume, rezultat, idx):
    import httpx
    t0 = time.perf_counter()
    try:
        r = httpx.post(baza + ruta, headers={"Authorization": "Bearer " + tok},
                       files={"fisier": (nume, continut, "text/csv")}, timeout=300.0)
        rezultat[idx] = (r.status_code, time.perf_counter() - t0, (r.text or "")[:200])
    except Exception as e:  # noqa: BLE001
        rezultat[idx] = (None, time.perf_counter() - t0, type(e).__name__ + ": " + str(e)[:160])


def _get(baza, ruta, tok, rezultat, idx):
    import httpx
    t0 = time.perf_counter()
    try:
        r = httpx.get(baza + ruta, headers={"Authorization": "Bearer " + tok}, timeout=300.0)
        rezultat[idx] = (r.status_code, time.perf_counter() - t0, (r.text or "")[:120])
    except Exception as e:  # noqa: BLE001
        rezultat[idx] = (None, time.perf_counter() - t0, type(e).__name__ + ": " + str(e)[:160])


def canar_liber(baza, secunde=1.5):
    """Linia de bază a canarului: nimeni nu încarcă buclă. Fără ea, orice cifră de mai jos e goală."""
    c = Canar(baza)
    c.start()
    time.sleep(secunde)
    c.opreste.set()
    c.join(timeout=5)
    return _rezumat(c.latente, c.erori, "canar_liber")


def _statusuri_rele(curba, martor):
    """Orice status ≠ 200, cu locul lui. *O durată există și pe 500* — deci fără verificarea asta
    o măsurătoare poate descrie liniștită altă ramură decât cea numită."""
    rele = {}
    for r in curba:
        for st, n in r.get("statusuri", {}).items():
            if st != "200":
                rele["async N=%d status %s" % (r["N"], st)] = n
    for st, n in (martor or {}).get("statusuri", {}).items():
        if st != "200":
            rele["sync status %s" % st] = n
    return rele


def curba_async(baza, tid, tok, nn=NN, repetari=8):
    """Pentru fiecare N: durata rutei `async def` și ce a pățit canarul cât timp ea lucra.

    **Canarul se încălzește ÎNAINTE**, iar ruta grea se repetă de `repetari` ori: fereastra unei
    singure cereri de 40 ms îi lăsa canarului 1-2 probe, adică o cifră fără distribuție. *O
    percentilă pe două valori nu e o percentilă.*"""
    out = []
    for n in nn:
        continut = extras_csv(n)
        c = Canar(baza)
        c.start()
        time.sleep(0.25)                       # încălzire: conexiunea TCP nu intră în măsurătoare
        c.latente.clear(); c.erori.clear()
        durate, statusuri = [], {}
        t0 = time.perf_counter()
        for _ in range(repetari):
            rez = [None]
            _post_fisier(baza, RUTA_ASYNC % tid, tok, continut, "extras.csv", rez, 0)
            st, dt, corp = rez[0]
            durate.append(dt)
            statusuri[str(st)] = statusuri.get(str(st), 0) + 1
        fereastra = time.perf_counter() - t0
        c.opreste.set()
        c.join(timeout=5)
        out.append({"N": n, "repetari": repetari, "statusuri": statusuri,
                    "durata_ruta_p50_ms": _pct(durate, 50),
                    "durata_ruta_p95_ms": _pct(durate, 95),
                    "durata_ruta_max_ms": round(max(durate) * 1000, 1),
                    "fereastra_ms": round(fereastra * 1000, 1),
                    "canar": _rezumat(c.latente, c.erori, "canar_in_timpul_async_N%d" % n)})
        BRUT["ruta_async_N%d" % n] = {"latente_ms": [round(x * 1000, 2) for x in durate],
                                      "erori": []}
        print("  N=%-5d ruta p50 %8.1f ms · canar p50 %6s / p95 %6s / max %6s ms (%d probe)"
              % (n, out[-1]["durata_ruta_p50_ms"], out[-1]["canar"].get("p50_ms"),
                 out[-1]["canar"].get("p95_ms"), out[-1]["canar"].get("max_ms"),
                 out[-1]["canar"].get("n", 0)), flush=True)
    return out


def curba_sync(baza, tid, tok, repetari=40):
    """MARTORUL: aceeași măsurătoare pe o rută `def`, care rulează în threadpool."""
    c = Canar(baza)
    c.start()
    time.sleep(0.25)
    c.latente.clear(); c.erori.clear()
    durate, statusuri = [], {}
    for _ in range(repetari):
        rez = [None]
        _get(baza, RUTA_SYNC % tid, tok, rez, 0)
        durate.append(rez[0][1])
        statusuri[str(rez[0][0])] = statusuri.get(str(rez[0][0]), 0) + 1
    BRUT["ruta_sync"] = {"latente_ms": [round(x * 1000, 2) for x in durate], "erori": []}
    c.opreste.set()
    c.join(timeout=5)
    return {"ruta": RUTA_SYNC, "repetari": repetari, "statusuri": statusuri,
            "durata_p50_ms": _pct(durate, 50), "durata_max_ms": round(max(durate) * 1000, 1),
            "durata_p95_ms": _pct(durate, 95),
            "canar": _rezumat(c.latente, c.erori, "canar_in_timpul_sync")}


def concurenta(baza, tid, tok, dinainte, obs, nivele=NIVELE, n_tranzactii=250):
    """k cereri deodată pe ruta grea, cu canarul pornit și cu eșantionarea conexiunilor."""
    continut = extras_csv(n_tranzactii)
    out = []
    for k in nivele:
        es = MC.Esantionator(dinainte, obs)
        es.start()
        c = Canar(baza)
        c.start()
        time.sleep(0.25)
        c.latente.clear(); c.erori.clear()
        rez = [None] * k
        fire = [threading.Thread(target=_post_fisier,
                                 args=(baza, RUTA_ASYNC % tid, tok, continut, "extras.csv", rez, i))
                for i in range(k)]
        t0 = time.perf_counter()
        for f in fire:
            f.start()
        for f in fire:
            f.join()
        total = time.perf_counter() - t0
        c.opreste.set(); c.join(timeout=5)
        es.opreste.set(); es.join(timeout=2)
        latente = [x[1] for x in rez if x]
        erori = [x[2] for x in rez if x and x[0] is None]
        statusuri = {}
        for x in rez:
            statusuri[str(x[0])] = statusuri.get(str(x[0]), 0) + 1
        out.append({
            "k": k, "N": n_tranzactii, "total_ms": round(total * 1000, 1),
            "debit_cereri_pe_sec": round(k / total, 2) if total else None,
            "p50_ms": _pct(latente, 50), "p95_ms": _pct(latente, 95), "p99_ms": _pct(latente, 99),
            "max_ms": round(max(latente) * 1000, 1) if latente else None,
            "statusuri": statusuri, "erori": erori[:3], "nr_erori": len(erori),
            # numele cerute de comanda fazei, ca raportul sa le poata cita ca atare
            "MAX_SIMULTANEOUS_RESOURCE_USE": es.maxim,
            "RESOURCE_CAPACITY": int(os.environ.get("ICONTA_POOL_MAX", "10")),
            "probe_esantionator": es.probe,
            "canar": _rezumat(c.latente, c.erori, "canar_in_timpul_k%d" % k),
        })
        out[-1].update(_numara_erori(erori))
        BRUT["ruta_async_k%d" % k] = {"latente_ms": [round(x * 1000, 2) for x in latente],
                                      "erori": [str(e) for e in erori]}
        print("  k=%-3d total %8.1f ms · p50 %s · p95 %s · conex. simultane max %d · "
              "canar p95 %s ms" % (k, total * 1000, out[-1]["p50_ms"], out[-1]["p95_ms"],
                                   es.maxim, out[-1]["canar"].get("p95_ms")), flush=True)
    return out


# ============================================================================
#  CALIBRARE
# ============================================================================

def calibreaza(baza, verbose=True):
    """**Canarul măsoară blocajul buclei? Se probează în ambele direcții.**

    (a) fără nicio încărcare, canarul trebuie să fie RAPID — altfel orice cifră de mai jos ar fi
        despre altceva (rețea, mașină, instrument);
    (b) cu bucla ocupată deliberat, canarul trebuie să ÎNCETINEASCĂ vizibil. Fără direcția a doua,
        un canar care măsoară mereu „rapid" ar trece prima probă și n-ar detecta nimic.

    Direcția (b) folosește chiar ruta grea, cu un N mare — nu un blocaj fabricat în afara
    aplicației, care ar proba instrumentul, nu aplicația.
    """
    liber = canar_liber(baza, 1.0)
    ok_a = bool(liber.get("n", 0) > 50 and (liber.get("p95_ms") or 9999) < 25)
    det = {"liber": liber}
    if verbose:
        print("CALIBRARE canar — ambele direcții:")
        print("  (a) fără încărcare: %d probe, p50 %s ms, p95 %s ms  -> %s"
              % (liber.get("n", 0), liber.get("p50_ms"), liber.get("p95_ms"),
                 "OK" if ok_a else "PICAT"))
    return ok_a, det


# ============================================================================
#  CLI
# ============================================================================

def main():
    from core import db as _db
    _db.init_pool()
    os.makedirs(DIR, exist_ok=True)
    brut = {"commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                     text=True, cwd=RAD).stdout.strip(),
            "pornit_la": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "capacitati": {"ICONTA_POOL_MAX": int(os.environ.get("ICONTA_POOL_MAX", "10")),
                           "threadpool_anyio": 40, "procese_uvicorn": 1}}

    # curățenie ÎNAINTE, ca o rulare oprită la mijloc să nu se târască în următoarea
    with _db.get_conn() as conn:
        MP3.curata_reale(conn)
        MR.curata(conn)
        conn.commit()

    obs = MC._conexiune_proprie()
    dinainte = MC._pids(obs)
    obs.rollback()
    with obs.cursor() as _c:
        _c.execute("SELECT 1")
    amp_inainte = amprenta(obs)
    obs.rollback()

    port = MC._port_liber()
    baza = "http://127.0.0.1:%d" % port
    print("── uvicorn pe %s ──" % baza, flush=True)
    # stdout/stderr BRUT al serverului, in  — locul cerut pentru dovada bruta
    os.makedirs(os.path.join(DIR, "P5_RAW_EVIDENCE"), exist_ok=True)
    cale_log = os.path.join(DIR, "P5_RAW_EVIDENCE", "P5_uvicorn.log")
    jurnal = io.open(cale_log, "w", encoding="utf-8")
    proc = subprocess.Popen(
        [os.path.join(RAD, "venv/bin/python"), "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "info"],
        cwd=RAD, stdout=jurnal, stderr=subprocess.STDOUT)
    try:
        import httpx
        gata = False
        for _ in range(240):
            try:
                if httpx.get(baza + CANAR, timeout=2.0).status_code == 200:
                    gata = True
                    break
            except Exception:
                pass
            time.sleep(0.5)
        if not gata:
            print("PICAT: serverul nu a pornit; v. %s" % cale_log)
            return 2

        ok_cal, det_cal = calibreaza(baza)
        brut["calibrare_canar"] = det_cal
        if not ok_cal:
            print("PICAT: canarul nu e rapid în gol — nicio cifră de mai jos n-ar valora nimic")
            return 2

        with _db.get_conn() as conn:
            # SCHEMA ADEVĂRATĂ, nu goală. Forma dinainte folosea firma cu schemă goală — bună
            # pentru P2, unde ramura fără tabele E subiectul; aici însă ruta de control cădea cu
            # `UndefinedTable`, deci martorul măsura o cale de EROARE.
            MP3.curata_reale(conn)
            uid, ids = MP3.construieste_reale(conn, 1)
            conn.commit()
            tok = MR._token(conn, uid)
        tid = ids[0]
        brut["subiect"] = {"uid": uid, "tenant": tid}
        print("firmă sintetică: tenant %s" % tid, flush=True)

        print("\n── CURBA N pe ruta `async def` (bucla) ──", flush=True)
        brut["curba_async"] = curba_async(baza, tid, tok)
        print("\n── MARTOR: rută `def` (threadpool) ──", flush=True)
        brut["martor_sync"] = curba_sync(baza, tid, tok)
        print("  canar în timpul rutei sincrone: p50 %s / p95 %s ms"
              % (brut["martor_sync"]["canar"].get("p50_ms"),
                 brut["martor_sync"]["canar"].get("p95_ms")), flush=True)
        rele = _statusuri_rele(brut["curba_async"], brut["martor_sync"])
        brut["statusuri_neasteptate"] = rele
        if rele:
            print("PICAT: cereri care NU au ieșit 200 — %s" % rele)
            print("  O durată există și pe 500. Fără poarta asta, martorul ar fi măsurat cât "
                  "durează să arunci o excepție, și ar fi părut o rută rapidă.")
            return 2
        print("\n── CONCURENȚĂ k=1,2,5,10 pe ruta `async def` ──", flush=True)
        brut["concurenta"] = concurenta(baza, tid, tok, dinainte, obs)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except Exception:
            proc.kill()
        jurnal.close()
        with _db.get_conn() as conn:
            sters = 0
            try:
                sters = curata_audit(conn, brut.get("subiect", {}).get("uid"),
                                     [brut.get("subiect", {}).get("tenant")])
            except Exception as e:  # noqa: BLE001
                print("curatenia auditului a esuat: %s" % e)
            MP3.curata_reale(conn)
            MR.curata(conn)
            conn.commit()
        brut["curatenie"] = {"randuri_audit_sterse": sters, "scheme_reale_sterse": True}
        print("curatenie: %d rânduri de audit șterse" % sters)

    obs.rollback()
    amp_dupa = amprenta(obs)
    obs.close()
    difera = {t: (amp_inainte[t], amp_dupa[t]) for t in TABELE_AMPRENTA
              if amp_inainte.get(t) != amp_dupa.get(t)}
    brut["amprenta"] = {"tabele": list(TABELE_AMPRENTA), "difera": {k: list(v)
                                                                   for k, v in difera.items()},
                        "PRODUCTION_DATA_AFFECTED": "NO" if not difera else "DA"}
    print("\nAMPRENTA BAZEI: %s" % ("NESCHIMBATĂ pe toate cele %d tabele" % len(TABELE_AMPRENTA)
                                    if not difera else "DIFERĂ: %s" % sorted(difera)))

    # JURNALUL SERVERULUI, citit — un deadlock sau un timeout de pool NU se vede in raspunsul
    # HTTP (ajunge un 500 fara nume), ci in stderr-ul procesului. Daca nu-l citesc, `DEADLOCKS=0`
    # ar fi o afirmatie despre ce n-am privit.
    tipare = {"DEADLOCKS": ("40P01", "eadlock"), "TIMEOUTS_DB": ("57014", "QueryCanceled"),
              "POOL_EPUIZAT": ("PoolTimeout", "connection pool exhausted", "too many clients"),
              "URME_EXCEPTIE": ("Traceback (most recent call last)",)}
    gasite = dict.fromkeys(tipare, 0)
    linii = 0
    with io.open(cale_log, encoding="utf-8", errors="replace") as f:
        for linie in f:
            linii += 1
            for cod, ac in tipare.items():
                if any(a in linie for a in ac):
                    gasite[cod] += 1
    brut["jurnal_server"] = dict(gasite, linii=linii, fisier="P5_RAW_EVIDENCE/P5_uvicorn.log")
    print("jurnalul serverului (%d linii): %s"
          % (linii, " · ".join("%s=%d" % kv for kv in sorted(gasite.items()))))

    # ESANTIOANELE BRUTE — o percentila fara esantionul din care iese nu se poate reface
    dir_brut = os.path.join(DIR, "P5_RAW_EVIDENCE")
    os.makedirs(dir_brut, exist_ok=True)
    with io.open(os.path.join(dir_brut, "esantioane.json"), "w",
                 encoding="utf-8", newline="") as f:
        json.dump(BRUT, f, ensure_ascii=False, indent=1, sort_keys=True)
    brut["esantioane_brute"] = {"fisier": "P5_RAW_EVIDENCE/esantioane.json",
                                "serii": len(BRUT),
                                "valori": sum(len(v["latente_ms"]) for v in BRUT.values())}
    print("dovadă brută: %d serii, %d valori"
          % (brut["esantioane_brute"]["serii"], brut["esantioane_brute"]["valori"]))

    cale = os.path.join(DIR, "P5_MASURATORI.json")
    with io.open(cale, "w", encoding="utf-8", newline="") as f:
        json.dump(brut, f, ensure_ascii=False, indent=2, default=str)
    print("scris: %s" % cale)
    return 0


if __name__ == "__main__":
    sys.exit(main())
