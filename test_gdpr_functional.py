# -*- coding: utf-8 -*-
"""Test functional GDPR pe cont FABRICAT — F199 (export) + F200b (cerere stergere).

Ruleaza: /opt/iconta/venv/bin/python3 test_gdpr_functional.py
Creeaza un cabinet fabricat, exercita ambele fluxuri REAL (DB + email mock),
apoi curata TOT dupa el (finally). Nu atinge date reale."""
import glob, os, io, json, zipfile

for _f in glob.glob(os.path.expanduser("~/.iconta/*.env")):
    for _ln in open(_f):
        _ln = _ln.strip()
        if _ln and not _ln.startswith("#") and "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k, _v.strip().strip('"'))

from core import db, gdpr_export, gdpr_cerere, observare

NUME = "ZZ TEST GDPR CABINET"


def main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO public.accounting_firms "
                "(nume, activ, creat_la, educatie_4ochi_la_nr, patru_ochi_activ) "
                "VALUES (%s, true, now(), 0, false) RETURNING id", (NUME,))
            cab = cur.fetchone()[0]
        conn.commit()
    print("cabinet fabricat #%s" % cab)
    try:
        # ---- A. EXPORT: ZIP valid + logare audit (nume de coloane reale) ----
        with db.get_conn() as conn:
            zbytes = gdpr_export.export_cabinet(conn, cab)
        assert zipfile.is_zipfile(io.BytesIO(zbytes)), "export: nu e ZIP valid"
        names = zipfile.ZipFile(io.BytesIO(zbytes)).namelist()
        assert "public/accounting_firms.json" in names, "export: lipseste accounting_firms.json"
        print("  [A] export ZIP valid, %d intrari" % len(names))
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO public.audit_log (user_id, actiune, entitate, entitate_id, detalii) "
                    "VALUES (%s,'gdpr_export',%s,%s,%s)",
                    (None, "cabinet", cab, json.dumps({"octeti": len(zbytes)})))
            conn.commit()
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM public.audit_log "
                            "WHERE actiune='gdpr_export' AND entitate_id=%s", (cab,))
                n = cur.fetchone()[0]
        assert n == 1, "export: log audit lipsa (%s)" % n
        print("  [A] audit_log gdpr_export scris OK (cine/cand, fara continut)")

        # ---- B. CERERE STERGERE: typed-back + email + jurnal ----
        capt = []
        orig = observare._trimite_brevo
        observare._trimite_brevo = lambda s, m: capt.append((s, m)) or True
        try:
            with db.get_conn() as conn:
                try:
                    gdpr_cerere.depune_cerere(conn, cab, 111, "ALT NUME", "x")
                    assert False, "cerere: typed-back gresit a trecut!"
                except ValueError:
                    print("  [B] typed-back gresit respins OK")
                conn.rollback()
            with db.get_conn() as conn:
                r = gdpr_cerere.depune_cerere(conn, cab, 111, NUME, "inchidem activitatea")
                conn.commit()
            assert r["ok"] and r["cerere_id"], "cerere: raspuns invalid"
            assert r["termen_zile_lucratoare"] == 5, "cerere: termen gresit"
            assert capt and "stergere" in capt[0][0].lower(), "cerere: email neanuntat"
            print("  [B] cerere #%s inregistrata, email->contact@iconta.eu anuntat, termen %s zile"
                  % (r["cerere_id"], r["termen_zile_lucratoare"]))
            with db.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT stare, nume_cabinet, motiv FROM public.gdpr_cereri_stergere "
                                "WHERE id=%s", (r["cerere_id"],))
                    row = cur.fetchone()
            assert row and row[0] == "primita" and row[1] == NUME and row[2] == "inchidem activitatea", \
                "cerere: jurnal incomplet %r" % (row,)
            print("  [B] jurnal gdpr_cereri_stergere: stare=%s, dovada de primire OK" % row[0])
        finally:
            observare._trimite_brevo = orig
        print("\nTOATE TESTELE: PASS")
    finally:
        with db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM public.gdpr_cereri_stergere WHERE cabinet_id=%s", (cab,))
                cur.execute("DELETE FROM public.audit_log WHERE actiune='gdpr_export' AND entitate_id=%s", (cab,))
                cur.execute("DELETE FROM public.accounting_firms WHERE id=%s", (cab,))
            conn.commit()
        print("curatat cabinet fabricat #%s" % cab)


if __name__ == "__main__":
    main()
