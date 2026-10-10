# -*- coding: utf-8 -*-
"""scripts/amprente_declaratii.py — amprentele declarațiilor pe portofoliu, înainte și după mutarea valorilor în registru (comanda Costin
08.10.2026, verbatim în DECIZII; pașii R2 și R8 din TESTE.md: „Amprentele «înainte»: toate declarațiile generabile pe portofoliu (baza
de test; producția în tranzacție anulată), XML normalizat + SHA” și „Amprentele «după» = «înainte»”).

Ce se amprentează: fiecare tip din `declaratii_api.DECLARATII` + situațiile financiare, pe fiecare perioadă a firmei în care există date
(lunile cu note sau facturi — `cifre_referinta._luni_cu_date`), la periodicitatea tipului (setul TVA-decont după `tip_decont`-ul firmei,
ca selectorul). Generarea trece pe DRUMUL APLICAȚIEI (`declaratii_api.genereaza`), în sesiune READ-ONLY, iar fiecare generare se
anulează. Un refuz e și el o amprentă: aceeași cerere trebuie refuzată la fel și după.

Ce se păstrează: NUMAI amprenta (SHA-256 al XML-ului fără părțile care se schimbă la fiecare generare — `cifre_referinta._VOLATIL`),
niciodată conținutul. Pe firmele din afara cabinetului de test, nici textul refuzului, nici numele firmei: doar SHA-uri și schema.

Amprenta DATELOR firmei (SHA pe conținutul tabelelor schemei + rândul ei din `public.tenants`) stă lângă amprentele declarațiilor: baza
de test se schimbă între R2 și R8 (plasa e2e scrie în ea la fiecare poartă), deci la R8 „înainte” și „după” se iau pe ACELEAȘI date —
codul „înainte” rulat dintr-un worktree al commitului R2 (`--cod-din`), cel „după” din arbore —, iar amprenta datelor arată că datele
sunt aceleași.

Uz: python scripts/amprente_declaratii.py --test <iesire.json>        baza de test (~/.iconta/test.env)
    python scripts/amprente_declaratii.py --productie <iesire.json>   producția, read-only
    python scripts/amprente_declaratii.py --compara <a.json> <b.json> -> 0 identice / 1 diferă (lista tipărită)
"""
import datetime as _dt
import hashlib
import json
import os
import subprocess
import sys
import time

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
sys.path.insert(0, os.path.join(RAD, "scripts"))

from cifre_referinta import CABINET, _amprenta, _luni_cu_date  # noqa: E402

READ_ONLY = "-c default_transaction_read_only=on"


def perioade(per, luni):
    """Cererile (corpul `genereaza`) pentru periodicitatea `per`, din lunile cu date [(an, luna)], fără repetiții, în ordine."""
    out = []
    for a, m in luni:
        if per == "lunar":
            b = {"an": a, "luna": m}
        elif per == "trimestrial":
            b = {"an": a, "trim": (m - 1) // 3 + 1}
        elif per == "semestrial":
            b = {"an": a, "luna": 6 if m <= 6 else 12}
        else:
            b = {"an": a}
        if b not in out:
            out.append(b)
    return out


def eticheta(body):
    a = body["an"]
    if "trim" in body:
        return "T%d/%04d" % (body["trim"], a)
    if "luna" in body:
        return "%02d/%04d" % (body["luna"], a)
    return "%04d" % a


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def rezultat(xml=None, refuz=None, de_test=True):
    """Ce se păstrează dintr-o generare: amprenta XML-ului normalizat, sau refuzul — textul lui numai pe firmele de test."""
    if refuz is None:
        return {"amprenta": _amprenta(xml if isinstance(xml, str) else xml.decode("utf-8"))}
    return {"refuz": refuz} if de_test else {"refuz_sha": _sha(refuz)}


def amprenta_date(cur, schema):
    """SHA pe conținutul tuturor tabelelor schemei firmei (rândurile ordonate după propriul lor SHA) + rândul ei din `public.tenants`."""
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = %s ORDER BY 1", (schema,))
    h = hashlib.sha256()
    for (t,) in cur.fetchall():
        cur.execute('SELECT coalesce(string_agg(md5(x::text), \'\' ORDER BY md5(x::text)), \'\') FROM "%s"."%s" x' % (schema, t))
        h.update(("%s:%s;" % (t, cur.fetchone()[0])).encode())
    cur.execute("SELECT md5(t::text) FROM public.tenants t WHERE schema_name = %s", (schema,))
    h.update(str(cur.fetchone()).encode())
    return h.hexdigest()


def firma(conn, schema, de_test):
    from core import declaratii_api as da
    from cifre_referinta import _anuleaza
    with conn.cursor() as cur:
        luni = _luni_cu_date(cur, schema)
        cur.execute("SELECT tip_decont, platitor_tva FROM firma_profil WHERE id = 1")
        r = cur.fetchone()
        date_sha = amprenta_date(cur, schema)
    _anuleaza(conn, schema)
    prof = {"tip_decont": r[0], "platitor_tva": r[1]} if r else None
    out = {"date": date_sha, "luni": ["%02d/%04d" % (m, a) for a, m in luni], "declaratii": {}}
    tipuri = dict(da.DECLARATII, **da.SITUATII_FINANCIARE)
    for tip in sorted(tipuri):
        per = da.periodicitate_firma(tip, prof)
        out["declaratii"][tip] = {}
        for body in perioade(per, luni):
            try:
                xml = da.genereaza(conn, schema, tip, dict(body))[0]
                rez = rezultat(xml=xml)
            except Exception as e:  # noqa: BLE001 — refuzul generatorului e și el o amprentă
                rez = rezultat(refuz="%s: %s" % (type(e).__name__, str(e).split("\n")[0][:600]), de_test=de_test)
            _anuleaza(conn, schema)
            out["declaratii"][tip][eticheta(body)] = rez
    return out


def culege(baza):
    """{schema: amprente} pe baza dată — fiecare conexiune confirmă că e read-only înainte de citire."""
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW default_transaction_read_only")
            assert cur.fetchone()[0] == "on", "sesiunea nu e read-only — refuz"
            cur.execute("SELECT t.nume, t.schema_name, coalesce(a.nume, '') FROM public.tenants t "
                        "LEFT JOIN public.accounting_firms a ON a.id = t.accounting_firm_id "
                        "JOIN pg_namespace n ON n.nspname = t.schema_name ORDER BY t.schema_name")
            firme = cur.fetchall()
        conn.rollback()
    rez = {}
    for nume, schema, cabinet in firme:
        de_test = baza == "test" or cabinet == CABINET     # baza de test n-are date reale; pe producție, numai cabinetul de test
        t0 = time.time()
        with db.get_conn(schema) as conn:
            with conn.cursor() as cur:
                cur.execute("SHOW default_transaction_read_only")
                assert cur.fetchone()[0] == "on", "sesiunea nu e read-only — refuz"
            f = firma(conn, schema, de_test)
            conn.rollback()
        f["nume"] = nume if de_test else None
        f["secunde"] = round(time.time() - t0, 1)
        rez[schema] = f
        print("  %s: %d cereri, %.1fs" % (schema, sum(len(v) for v in f["declaratii"].values()), f["secunde"]), flush=True)
    return rez


def compara(a, b):
    """[(schema, tip, perioadă, înainte, după)] — fiecare amprentă care diferă, lipsește sau e nouă; plus datele firmei, dacă diferă."""
    out = []
    for s in sorted(set(a) | set(b)):
        fa, fb = a.get(s) or {}, b.get(s) or {}
        if fa.get("date") != fb.get("date"):
            out.append((s, "(datele firmei)", "", fa.get("date"), fb.get("date")))
        da_, db_ = fa.get("declaratii") or {}, fb.get("declaratii") or {}
        for t in sorted(set(da_) | set(db_)):
            pa, pb = da_.get(t) or {}, db_.get(t) or {}
            for p in sorted(set(pa) | set(pb)):
                if pa.get(p) != pb.get(p):
                    out.append((s, t, p, pa.get(p), pb.get(p)))
    return out


def _mediu(baza):
    env = {}
    if baza == "test":
        for linie in open(os.path.expanduser("~/.iconta/test.env"), encoding="utf-8"):
            linie = linie.strip()
            if "=" in linie and not linie.startswith("#"):
                k, v = linie.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    else:
        from core import mediu_test
        dsn = mediu_test.dsn_productie()
        if not dsn:
            raise SystemExit("DSN-ul de producție nu se poate citi (%s) — refuz" % mediu_test.CALE_DB_ENV)
        env["DATABASE_URL"] = dsn
    for k in ("ANTHROPIC_API_KEY", "BREVO_API_KEY"):      # nimic trimis în afară dintr-o amprentă
        os.environ.pop(k, None)
    os.environ.update(env)
    os.environ["PGOPTIONS"] = READ_ONLY


def main(argv):
    if argv[:1] == ["--compara"]:
        dif = compara(json.load(open(argv[1], encoding="utf-8"))["firme"], json.load(open(argv[2], encoding="utf-8"))["firme"])
        for d in dif[:60]:
            print("  %s %s %s: %s -> %s" % d)
        print("[amprente] %s" % ("identice" if not dif else "%d diferențe" % len(dif)))
        return 1 if dif else 0
    baza = "productie" if "--productie" in argv else "test" if "--test" in argv else None
    if baza is None:
        print(__doc__)
        return 2
    iesire = [x for x in argv if not x.startswith("--")][0]
    _mediu(baza)
    t0 = time.time()
    firme = culege(baza)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=RAD, capture_output=True, text=True).stdout.strip()
    json.dump({"baza": baza, "commit": commit, "generat": _dt.datetime.now().isoformat(timespec="seconds"),
               "secunde": round(time.time() - t0, 1), "firme": firme},
              open(iesire, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    n = sum(len(p) for f in firme.values() for p in f["declaratii"].values())
    gen = sum(1 for f in firme.values() for p in f["declaratii"].values() for r in p.values() if "amprenta" in r)
    print("[amprente] %s: %d firme, %d cereri (%d XML, %d refuzuri), %.0fs -> %s"
          % (baza, len(firme), n, gen, n - gen, time.time() - t0, iesire))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
