# -*- coding: utf-8 -*-
"""scripts/ciorne_depasite.py — ciornele derivate DEPĂȘITE, firmă cu firmă (lotul 11, deficiența 451). NUMAI numără și listează: baza se
deschide numai-citire (`default_transaction_read_only`) și tranzacția se anulează la final, deci nimic nu se scrie.

Comanda Costin 11.1 pct.6: „ciornele generate înainte de o reparație rămân validabile cu regula veche [...] Toate trebuie refăcute din
sursă sau marcate depășite și oprite de la validare, pe toate firmele.” Validarea le oprește singură (`ciorne_depasite`, din
`jurnal_api.valideaza`); scriptul arată câte sunt și care, pe fiecare firmă, cu motivul — exact textul refuzului de la validare.

Pentru fiecare ciornă: `la zi` (regenerarea pe uscat dă aceeași notă) / `depășită` (alta — cu diferențele) / `depășită, sursa n-o mai poate
scrie` / `neverificată` (felul ei e NEREGENERABIL în `ciorne_depasite.SURSE`: limita declarată) / `nederivată` (manuală, din Operațiuni).

Uz: python scripts/ciorne_depasite.py --proba [--productie] [--firme=tenant_049,tenant_053] [--detalii]
    --productie   baza de producție (`~/.iconta/db.env`); fără el, baza de test (`~/.iconta/test.env`)
    --firme=…     numai schemele numite (implicit: toate firmele cu Registru jurnal)
    --detalii     tipărește și motivul fiecărei ciorne depășite (fără el: numai numărătoarea și eticheta notei)
"""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _conexiune(productie):
    import psycopg2
    from core import mediu_test
    dsn = mediu_test.dsn_productie() if productie else mediu_test.dsn_productie(mediu_test.CALE_TEST_ENV)
    if not dsn:
        raise SystemExit("[ciorne] DSN-ul bazei (%s) nu se poate citi — nimic nu pornește"
                         % (mediu_test.CALE_DB_ENV if productie else mediu_test.CALE_TEST_ENV))
    c = psycopg2.connect(dsn, options="-c default_transaction_read_only=on")
    c.set_session(readonly=True)
    return c


def masoara(conn, scheme=None):
    """{schema: {"firma", "stari": {stare: n}, "depasite": [(id, eticheta, felul, mesaj)]}} — numai citire (savepoint pe fiecare notă)."""
    from psycopg2.extras import RealDictCursor
    from core import ciorne_depasite as _cd, eticheta_nota as _et
    out = {}
    with conn.cursor() as cur:
        cur.execute("SELECT t.schema_name, t.nume FROM public.tenants t WHERE t.schema_name ~ '^tenant_[0-9]+$' "
                    "AND to_regclass(t.schema_name || '.inregistrari') IS NOT NULL ORDER BY t.schema_name")
        firme = [(s, n) for s, n in cur.fetchall() if not scheme or s in scheme]
    for schema, nume in firme:
        rez = {"firma": nume, "stari": {}, "depasite": []}
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % schema)
            cur.execute("SELECT id FROM %s.inregistrari WHERE status = 'ciorna' ORDER BY data, id" % schema)
            for nid in [r["id"] for r in cur.fetchall()]:
                cur.execute("SAVEPOINT ciorna")
                try:
                    fel = _cd.felul(cur, schema, nid)
                    if fel is None:
                        stare = "nederivată"
                    elif fel not in _cd.REGENERATOARE:
                        stare = "neverificată (%s)" % fel if _cd.SURSE.get(fel, (None,))[0] == _cd.NEREGENERABIL else "verificată altfel (%s)" % fel
                    else:
                        d = _cd.verifica(conn, cur, schema, nid)
                        if not d:
                            stare = "la zi (%s)" % fel
                        else:
                            stare = ("depășită, sursa n-o mai poate scrie (%s)" if d["neregenerabila"] else "depășită (%s)") % fel
                            rez["depasite"].append((nid, _et.nota(cur, schema, nid), fel, d["mesaj"]))
                except Exception as e:  # noqa: BLE001 — o notă care nu se poate măsura se spune, nu se ascunde
                    stare = "nemăsurată (%s: %s)" % (type(e).__name__, str(e).split("\n")[0][:120])
                cur.execute("ROLLBACK TO SAVEPOINT ciorna")
                rez["stari"][stare] = rez["stari"].get(stare, 0) + 1
        out[schema] = rez
    return out


def main(argv):
    sys.path.insert(0, RAD)
    sys.path.insert(0, os.path.join(RAD, "scripts"))
    import argumente_script
    argv = argumente_script.citeste(argv, __doc__, flaguri=("--proba", "--productie", "--detalii"), cu_valoare=("--firme=",),
                                    prefix="[ciorne]")
    if "--proba" not in argv:
        print("[ciorne] scriptul numai numără și listează: cere `--proba` — nimic nu pornește.\n" + __doc__[__doc__.index("Uz:"):],
              file=sys.stderr)
        return 2
    scheme = next((a.split("=", 1)[1].split(",") for a in argv if a.startswith("--firme=")), None)
    conn = _conexiune("--productie" in argv)
    try:
        rez = masoara(conn, scheme)
    finally:
        conn.rollback()
        conn.close()
    total = {}
    for schema, r in rez.items():
        print("%s — %s" % (schema, r["firma"]))
        for stare, n in sorted(r["stari"].items()):
            print("    %-60s %d" % (stare, n))
            total[stare.split(" (")[0]] = total.get(stare.split(" (")[0], 0) + n
        for nid, et, fel, mesaj in r["depasite"]:   # id-ul intern: scriptul e al celui care publică, nu al contabilului
            print("    DEPĂȘITĂ nota id %d (%s) [%s]%s" % (nid, et, fel, (" — " + mesaj) if "--detalii" in argv else ""))
    print("TOTAL (%d firme): %s" % (len(rez), ", ".join("%s %d" % (k, v) for k, v in sorted(total.items())) or "nicio ciornă"))
    print("[ciorne] ROLLBACK — nimic scris")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
