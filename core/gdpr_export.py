"""GDPR art. 20 — export complet al datelor unui cabinet (portabilitate).
Colecteaza din public (accounting_firms/users/tenants/audit_log ale cabinetului)
+ fiecare schema tenant (TOATE tabelele) + fisierele de pe disc (imagini bonuri,
zip-uri e-Factura). Intoarce bytes ZIP.
Citeste cu nume CALIFICAT schema.tabela (NU depinde de search_path)."""
import io, os, json, glob, zipfile, base64, datetime, decimal

BON_DIR_BAZA = os.path.expanduser("~/iconta_date/bonuri")
EFACTURA_ZIP_DIR = os.environ.get("EFACTURA_ZIP_DIR", os.path.expanduser("~/iconta_nou/efactura_zip"))

def _default(o):
    if isinstance(o, (datetime.datetime, datetime.date)): return o.isoformat()
    if isinstance(o, decimal.Decimal): return str(o)
    if isinstance(o, (bytes, memoryview)): return base64.b64encode(bytes(o)).decode()
    return str(o)

def _dump(cur, sql, params=None):
    cur.execute(sql, params or ())
    cols = [c.name for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def _j(rows):
    return json.dumps(rows, ensure_ascii=False, default=_default, indent=1).encode("utf-8")

def export_cabinet(conn, cabinet_id):
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        with conn.cursor() as cur:
            zf.writestr("public/accounting_firms.json", _j(_dump(cur,
                "SELECT * FROM public.accounting_firms WHERE id=%s", (cabinet_id,))))
            zf.writestr("public/users.json", _j(_dump(cur,
                "SELECT * FROM public.users WHERE accounting_firm_id=%s", (cabinet_id,))))
            tenants = _dump(cur, "SELECT * FROM public.tenants WHERE accounting_firm_id=%s", (cabinet_id,))
            zf.writestr("public/tenants.json", _j(tenants))
            uid_list = [u["id"] for u in _dump(cur,
                "SELECT id FROM public.users WHERE accounting_firm_id=%s", (cabinet_id,))] or [-1]
            tid_list = [t["id"] for t in tenants] or [-1]
            zf.writestr("public/audit_log.json", _j(_dump(cur,
                "SELECT * FROM public.audit_log WHERE user_id = ANY(%s) OR tenant_id = ANY(%s)",
                (uid_list, tid_list))))
            manifest = {"cabinet_id": cabinet_id, "generat_la": datetime.datetime.now().isoformat(),
                        "tenants": [], "fisiere": 0}
            for t in tenants:
                schema = t.get("schema_name")
                if not schema:
                    continue
                tbls = _dump(cur, "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_type='BASE TABLE' ORDER BY table_name", (schema,))
                for tb in tbls:
                    rows = _dump(cur, 'SELECT * FROM "%s"."%s"' % (schema, tb["table_name"]))
                    zf.writestr("%s/tabele/%s.json" % (schema, tb["table_name"]), _j(rows))
                manifest["tenants"].append({"tenant_id": t["id"], "schema": schema,
                                            "nume": t.get("nume"), "tabele": len(tbls)})
                bon_root = os.path.join(BON_DIR_BAZA, schema)
                for f in glob.glob(os.path.join(bon_root, "**", "*"), recursive=True):
                    if os.path.isfile(f):
                        zf.write(f, "%s/fisiere/bonuri/%s" % (schema, os.path.relpath(f, bon_root)))
                        manifest["fisiere"] += 1
                for f in glob.glob(os.path.join(EFACTURA_ZIP_DIR, "%s_*.zip" % schema)):
                    if os.path.isfile(f):
                        zf.write(f, "%s/fisiere/efactura/%s" % (schema, os.path.basename(f)))
                        manifest["fisiere"] += 1
            zf.writestr("MANIFEST.json", _j(manifest))
    return z.getvalue()
