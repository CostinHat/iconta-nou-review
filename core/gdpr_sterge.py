"""GDPR art. 17 — stergere completa cabinet. Doi pasi: previzualizare + executa (confirmare typed-back a numelui).
Sterge: scheme tenant (DROP SCHEMA CASCADE), randuri public (audit_log/user_tenants/tenants/users/accounting_firms), fisiere disc.
Logheaza in public.gdpr_stergeri (FARA date personale) — logul supravietuieste.
NU se sterge: backup Storage Box (dump integral, stergere selectiva imposibila, expira 30 zile)."""
import os, glob, shutil
import psycopg2.extras as _E
from core import db

BON_DIR_BAZA = os.path.expanduser("~/iconta_date/bonuri")
EFACTURA_ZIP_DIR = os.environ.get("EFACTURA_ZIP_DIR", os.path.expanduser("~/iconta_nou/efactura_zip"))
NU_SE_STERGE = ("backup Storage Box: dump integral, stergere selectiva imposibila tehnic, expira in 30 zile (retentie off-site)")

def previzualizare(conn, cabinet_id):
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, nume FROM public.accounting_firms WHERE id=%s", (cabinet_id,))
        cab = cur.fetchone()
        if not cab: raise ValueError("cabinet inexistent")
        cur.execute("SELECT schema_name FROM public.tenants WHERE accounting_firm_id=%s", (cabinet_id,))
        tens = cur.fetchall()
        cur.execute("SELECT count(*) AS n FROM public.users WHERE accounting_firm_id=%s", (cabinet_id,))
        nu = cur.fetchone()["n"]
    return {"cabinet_id": cabinet_id, "nume": cab["nume"], "nr_tenanti": len(tens), "nr_useri": nu,
            "scheme": [t["schema_name"] for t in tens], "confirmare_ceruta": cab["nume"],
            "avertisment": "Ireversibil. NU se șterge: " + NU_SE_STERGE}

def executa(conn, cabinet_id, confirmare, sters_de_user_id):
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cur.execute("SELECT id, nume FROM public.accounting_firms WHERE id=%s FOR UPDATE", (cabinet_id,))
        cab = cur.fetchone()
        if not cab: raise ValueError("cabinet inexistent")
        if (confirmare or "").strip() != (cab["nume"] or "").strip():
            raise ValueError("confirmare gresita: numele cabinetului nu se potriveste")
        cur.execute("SELECT id, schema_name FROM public.tenants WHERE accounting_firm_id=%s", (cabinet_id,))
        tens = cur.fetchall()
        scheme = [t["schema_name"] for t in tens if t["schema_name"]]
        tid = [t["id"] for t in tens] or [-1]
        cur.execute("SELECT id FROM public.users WHERE accounting_firm_id=%s", (cabinet_id,))
        us = cur.fetchall(); uid = [r["id"] for r in us] or [-1]; nr_useri = len(us)
        for sch in scheme:
            if not db.schema_valida(sch): raise ValueError("schema invalida: %r" % sch)
            cur.execute('DROP SCHEMA IF EXISTS "%s" CASCADE' % sch)
        cur.execute("DELETE FROM public.audit_log WHERE user_id=ANY(%s) OR tenant_id=ANY(%s)", (uid, tid))
        cur.execute("DELETE FROM public.user_tenants WHERE user_id=ANY(%s) OR tenant_id=ANY(%s)", (uid, tid))
        cur.execute("DELETE FROM public.tenants WHERE accounting_firm_id=%s", (cabinet_id,))
        cur.execute("DELETE FROM public.users WHERE accounting_firm_id=%s", (cabinet_id,))
        cur.execute("DELETE FROM public.accounting_firms WHERE id=%s", (cabinet_id,))
        cur.execute("INSERT INTO public.gdpr_stergeri (cabinet_id, nr_tenanti, nr_useri, scheme_sterse, sters_de_user_id, detalii) "
                    "VALUES (%s,%s,%s,%s,%s,%s) RETURNING id, sters_la",
                    (cabinet_id, len(scheme), nr_useri, scheme, sters_de_user_id, _E.Json({"nu_se_sterge": NU_SE_STERGE})))
        log = cur.fetchone()
    conn.commit()
    fisiere = 0
    for sch in scheme:
        d = os.path.join(BON_DIR_BAZA, sch)
        if os.path.isdir(d):
            shutil.rmtree(d, ignore_errors=True); fisiere += 1
        for f in glob.glob(os.path.join(EFACTURA_ZIP_DIR, "%s_*.zip" % sch)):
            try: os.remove(f); fisiere += 1
            except OSError: pass
    return {"cabinet_id": cabinet_id, "scheme_sterse": scheme, "nr_useri": nr_useri, "nr_tenanti": len(scheme),
            "fisiere_sterse": fisiere, "log_id": log["id"], "sters_la": str(log["sters_la"]), "NU_se_sterge": NU_SE_STERGE}
