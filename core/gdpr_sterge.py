"""GDPR art. 17 — stergere completa cabinet. Doi pasi: previzualizare + executa (confirmare typed-back a numelui).
Sterge: scheme tenant (DROP SCHEMA CASCADE), randuri public (audit_log/user_tenants/tenants/users/accounting_firms), fisiere disc.
Logheaza in public.gdpr_stergeri (FARA date personale) — logul supravietuieste.
NU se sterge: backup Storage Box (dump integral, stergere selectiva imposibila, expira 30 zile)."""
import os
import psycopg2.extras as _E
from core import tenant_stergere  # [R72] o singura cale de stergere a unei firme

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
        # [R72, 27.08.2026] O SINGURA cale de stergere a unei firme, nu doua.
        # Ce era aici pana azi: DROP SCHEMA pe fiecare firma, apoi DELETE din DOUA tabele din
        # `public` (audit_log, user_tenants). Masurat pe 27.08: **13** tabele poarta tenant_id,
        # deci 11 ramaneau in urma. Iar `anunturi_cabinet` si `solicitari_client` au FK cu
        # ON DELETE NO ACTION: la primul cabinet cu un anunt sau o solicitare, DELETE FROM
        # tenants ar fi esuat -- DUPA ce DROP SCHEMA rulase deja. Schema disparuta, cabinetul
        # ramas, stergerea oprita la mijloc.
        # Costin: "daca R72 construieste stergerea corecta pentru o firma, gdpr_sterge trebuie
        # s-o foloseasca pentru fiecare firma a cabinetului, nu sa aiba propria lista."
        for t in tens:
            tenant_stergere.sterge(conn, t["id"], "gdpr_cabinet", sters_de_user_id)
        # Ce ramane specific CABINETULUI: randurile legate de userii lui, nu de firme.
        cur.execute("DELETE FROM public.audit_log WHERE user_id=ANY(%s)", (uid,))
        cur.execute("DELETE FROM public.user_tenants WHERE user_id=ANY(%s)", (uid,))
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
        fisiere += tenant_stergere.sterge_fisiere(sch)   # [R72] aceeasi curatare de disc
    return {"cabinet_id": cabinet_id, "scheme_sterse": scheme, "nr_useri": nr_useri, "nr_tenanti": len(scheme),
            "fisiere_sterse": fisiere, "log_id": log["id"], "sters_la": str(log["sters_la"]), "NU_se_sterge": NU_SE_STERGE}
