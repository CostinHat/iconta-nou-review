# -*- coding: utf-8 -*-
"""scripts/cifre_referinta.py — cifrele de referință ale firmelor de test F1–F5 (comanda Costin 09.10.2026, pct.10, verbatim în
DECIZII: „Cifre de referință pe firmele de test F1–F5, pe lunile cu date: balanța, D300, D394, D406, D112 (rândurile și totalurile).
Exportă-le într-un fișier în ~/ghid_incoming/, ca să le verific eu înainte să devină referință. După aprobare, orice diferență față de
ele oprește publicarea.”).

Cifrele ies pe DRUMUL APLICAȚIEI (`documente_api.balanta`, `d300/d394/d112.genereaza(Perioada)`, `d406.genereaza(an, luna)`), pe
perioada fiecărei declarații (D300 / D394 pe perioada fiscală TVA a firmei, D406 pe fereastra SAF-T — `common.fereastra_tva`,
`common.fereastra_d406`; D112 lunar, pe lunile cu stat de plată). Un REFUZ al generatorului e și el o cifră de referință: textul lui.
SESIUNE READ-ONLY: pe producție, fiecare conexiune pornește cu `default_transaction_read_only=on` — un generator care ar încerca să
scrie cade, nu scrie (se vede în export). Firmele de test sunt ale cabinetului „Cabinet Test Sesiunea B SRL” (confirmat de Costin,
09.10.2026: „cu date inventate, fără clienți reali”).

Uz: python scripts/cifre_referinta.py --productie <iesire_fara_extensie>   -> <iesire>.md (de citit) + <iesire>.json (complet)
"""
import datetime as _dt
import hashlib
import json
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)
CABINET = "Cabinet Test Sesiunea B SRL"
_ATRIB = re.compile(r'([A-Za-z_][A-Za-z0-9_]*)="([^"]*)"')
#: părți care se schimbă la fiecare generare și nu sunt cifre (data generării); se scot înaintea amprentei
_VOLATIL = [re.compile(p) for p in (r'<DateCreated>[^<]*</DateCreated>', r'data_generare="[^"]*"')]


def _amprenta(xml):
    x = xml
    for p in _VOLATIL:
        x = p.sub("", x)
    return hashlib.sha256(x.encode("utf-8")).hexdigest()


def _atribute(xml, tag=None):
    """Atributele elementului rădăcină (sau ale primului `<tag …>`)."""
    if tag:
        m = re.search(r"<%s\b([^>]*)>" % re.escape(tag), xml)
        return dict(_ATRIB.findall(m.group(1))) if m else {}
    m = re.search(r"<(?!\?)[A-Za-z][^>]*>", xml)
    return dict(_ATRIB.findall(m.group(0))) if m else {}


def _numara(xml, sectiune, element):
    m = re.search(r"<%s>.*?</%s>" % (sectiune, sectiune), xml, re.S)
    return len(re.findall(r"<%s>" % element, m.group(0))) if m else 0


def _luni_cu_date(cur, schema):
    s = '"%s"' % schema
    cur.execute("SELECT DISTINCT to_char(d, 'YYYY-MM') FROM (SELECT data AS d FROM {s}.inregistrari UNION ALL "
                "SELECT data_emitere FROM {s}.facturi) x WHERE d IS NOT NULL ORDER BY 1".format(s=s))
    return [tuple(int(p) for p in r[0].split("-")) for r in cur.fetchall()]


def _luni_cu_stat(cur, schema):
    """Lunile cu salarii: un stat emis (`state_plata.luna`, o dată) SAU o notă de salarii (`inregistrari.sursa = 'salarii'`) — F5 are
    salariile contate fără stat emis, iar D112 se generează din salariați pe lună, nu din statul emis."""
    s = '"%s"' % schema
    cur.execute("SELECT DISTINCT d FROM (SELECT date_trunc('month', luna)::date AS d FROM {s}.state_plata UNION "
                "SELECT date_trunc('month', data)::date FROM {s}.inregistrari WHERE sursa = 'salarii') x ORDER BY 1".format(s=s))
    return [(d.year, d.month) for (d,) in cur.fetchall()]


def _eticheta(fereastra):
    """Luna-etichetă a perioadei (ultima lună a ferestrei): așa se depune trimestrialul (3/6/9/12)."""
    _inc, sf = fereastra
    ultima = sf - _dt.timedelta(days=1)
    return ultima.year, ultima.month


def _incearca(f):
    try:
        return f(), None
    except Exception as e:  # noqa: BLE001 — refuzul generatorului e o cifră de referință
        return None, "%s: %s" % (type(e).__name__, str(e).split("\n")[0][:600])


def _anuleaza(conn, schema):
    """Anulează (read-only, nimic de păstrat) și repune `search_path` — un SET din tranzacția anulată se anulează și el
    (`db.get_conn` îl pune o dată, la deschidere)."""
    conn.rollback()
    with conn.cursor() as cur:
        cur.execute('SET search_path TO "%s", public' % schema)


def firma(conn, schema):
    from core import common, d112, d300, d394, d406, documente_api
    from core.common import Perioada
    from core.d300_randuri import rand_formular
    with conn.cursor() as cur:
        luni = _luni_cu_date(cur, schema)
        luni_stat = _luni_cu_stat(cur, schema)
    _anuleaza(conn, schema)
    out = {"luni": ["%02d/%04d" % (m, a) for a, m in luni], "balanta": {}, "D300": {}, "D394": {}, "D406": {}, "D112": {}}
    for a, m in luni:
        rows, err = _incearca(lambda: documente_api.balanta(conn, schema, a, m))
        _anuleaza(conn, schema)
        out["balanta"]["%02d/%04d" % (m, a)] = err or [
            {k: (float(v) if isinstance(v, (int, float)) or hasattr(v, "quantize") else v) for k, v in r.items()}
            for r in rows if any(float(r.get(c) or 0) for c in ("si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c"))]
    with conn.cursor() as cur:            # numai ce decide perioadele (vectorul fiscal), citit ca atare
        cur.execute("SELECT platitor_tva, tip_decont FROM firma_profil LIMIT 1")
        r = cur.fetchone()
    prof = {"platitor_tva": r[0], "tip_decont": r[1]} if r else {}
    per_tva, err = _incearca(lambda: sorted({_eticheta(common.fereastra_tva(Perioada(a, luna=m), common.perioada_tva_tip(prof)))
                                             for a, m in luni}) if prof.get("platitor_tva") else [])
    if err:
        out["D300"] = out["D394"] = "refuz: " + err
        per_tva = []
    for a, m in per_tva:
        r, err = _incearca(lambda: d300.genereaza(conn, schema, Perioada(a, luna=m)))
        _anuleaza(conn, schema)
        out["D300"]["%02d/%04d" % (m, a)] = {"refuz": err} if err else {
            "randuri": {"%s (%s)" % (k, rand_formular(k)): v for k, v in sorted(_atribute(r[0]).items()) if re.match(r"^R\d", k)},
            "amprenta": _amprenta(r[0])}
        r, err = _incearca(lambda: d394.genereaza(conn, schema, Perioada(a, luna=m)))
        _anuleaza(conn, schema)
        out["D394"]["%02d/%04d" % (m, a)] = {"refuz": err} if err else {
            "antet": {k: v for k, v in _atribute(r[0]).items() if k.startswith(("tot", "nr", "op_", "tip_D394", "sistemTVA"))},
            "rezumat1": re.findall(r"<rezumat1\b([^>]*)>", r[0]), "rezumat2": re.findall(r"<rezumat2\b([^>]*)>", r[0]),
            "amprenta": _amprenta(r[0])}
    if prof and not prof.get("platitor_tva"):
        out["D300"] = out["D394"] = "nu se aplică: neplătitor de TVA"
    per_saft, err = _incearca(lambda: sorted({_eticheta(common.fereastra_d406(prof, a, m)) for a, m in luni}))
    if err:
        out["D406"] = "refuz: " + err
        per_saft = []
    for a, m in per_saft:
        r, err = _incearca(lambda: d406.genereaza(conn, schema, a, m))
        _anuleaza(conn, schema)
        if err:
            out["D406"]["%02d/%04d" % (m, a)] = {"refuz": err}
            continue
        x = r[0]
        out["D406"]["%02d/%04d" % (m, a)] = {
            "GeneralLedgerEntries": {t: (re.search(r"<GeneralLedgerEntries>.*?<%s>([^<]*)</%s>" % (t, t), x, re.S) or [None, None])[1]
                                     for t in ("NumberOfEntries", "TotalDebit", "TotalCredit")},
            "jurnale": re.findall(r"<Journal>\s*<JournalID>([^<]*)</JournalID>", x),
            "facturi_emise": _numara(x, "SalesInvoices", "Invoice"), "facturi_primite": _numara(x, "PurchaseInvoices", "Invoice"),
            "amprenta": _amprenta(x)}
    for a, m in luni_stat:
        r, err = _incearca(lambda: d112.genereaza(conn, schema, Perioada(an=a, luna=m)))
        _anuleaza(conn, schema)
        out["D112"]["%02d/%04d" % (m, a)] = {"refuz": err} if err else {
            "obligatii (angajatorA)": [dict(_ATRIB.findall(g)) for g in re.findall(r"<angajatorA\b([^>]*)>", r[0])],
            "angajatorB": [dict(_ATRIB.findall(g)) for g in re.findall(r"<angajatorB\b([^>]*)>", r[0])],
            "asigurati": len(re.findall(r"<asigurat\b", r[0])), "amprenta": _amprenta(r[0])}
    return out


def _md(rez):
    L = ["# Cifre de referință F1–F5 — de verificat de Costin înainte să devină referință (comanda 09.10.2026, pct.10)", "",
         "Generat %s, pe producție, în sesiune read-only, pe drumul aplicației. „refuz” = textul cu care generatorul refuză perioada."
         % _dt.datetime.now().strftime("%d.%m.%Y %H:%M"), ""]
    for nume, f in rez.items():
        L += ["## %s" % nume, "", "Lunile cu date: %s" % ", ".join(f["luni"]), ""]
        for luna, rows in f["balanta"].items():
            L += ["### Balanța %s (note validate)" % luna, ""]
            if isinstance(rows, str):
                L += ["refuz: " + rows, ""]
                continue
            L += ["| cont | denumire | SI D | SI C | rulaj D | rulaj C | SF D | SF C |", "|---|---|--:|--:|--:|--:|--:|--:|"]
            tot = dict.fromkeys(("si_d", "si_c", "rul_d", "rul_c", "sf_d", "sf_c"), 0.0)
            for r in rows:
                L.append("| %s | %s | %s |" % (r["cont"], (r.get("denumire") or "")[:40], " | ".join(
                    "%.2f" % float(r.get(c) or 0) for c in tot)))
                for c in tot:
                    tot[c] += float(r.get(c) or 0)
            L += ["| **total** | | %s |" % " | ".join("**%.2f**" % tot[c] for c in tot), ""]
        for d in ("D300", "D394", "D406", "D112"):
            v = f[d]
            L += ["### %s" % d, ""]
            if isinstance(v, str) or not v:
                L += [v or "nicio perioadă cu date", ""]
                continue
            for per, x in v.items():
                L += ["**%s %s** — %s" % (d, per, ("refuz: " + x["refuz"]) if "refuz" in x else "amprenta %s" % x["amprenta"][:12])]
                for k, val in x.items():
                    if k in ("refuz", "amprenta"):
                        continue
                    if isinstance(val, dict):
                        L += ["- %s: %s" % (k, ", ".join("%s=%s" % kv for kv in val.items()) or "—")]
                    else:
                        L += ["- %s: %s" % (k, val)]
                L.append("")
    return "\n".join(L) + "\n"


def main(argv):
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    os.environ["PGOPTIONS"] = "-c default_transaction_read_only=on"
    iesire = [a for a in argv if not a.startswith("--")][0]
    from core import db
    db.init_pool()
    rez = {}
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SHOW default_transaction_read_only")
            assert cur.fetchone()[0] == "on", "sesiunea nu e read-only — refuz"
            cur.execute("SELECT t.nume, t.schema_name FROM public.tenants t JOIN public.accounting_firms a ON a.id = t.accounting_firm_id "
                        "WHERE a.nume = %s ORDER BY t.nume", (CABINET,))
            firme = cur.fetchall()
        conn.rollback()
    for nume, schema in firme:
        with db.get_conn(schema) as conn:          # ca aplicația: conexiunea pe schema firmei
            with conn.cursor() as cur:
                cur.execute("SHOW default_transaction_read_only")
                assert cur.fetchone()[0] == "on", "sesiunea nu e read-only — refuz"
            rez["%s (%s)" % (nume, schema)] = firma(conn, schema)
            conn.rollback()
    json.dump(rez, open(iesire + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
    open(iesire + ".md", "w", encoding="utf-8").write(_md(rez))
    print("scris: %s.md, %s.json (%d firme)" % (iesire, iesire, len(rez)))


if __name__ == "__main__":
    main(sys.argv[1:])
