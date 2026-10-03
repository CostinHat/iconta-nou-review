# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, defectul 12: capitalul social pe factură (Legea 31/1990 art.74 alin.(3)).

    python frontend_test/proba_lot19_d12_capital_social.py <radacina_cod>
F1 (tenant_049, SRL) din baza de producție, calea aplicației: `uc_tenants.facturi_emite` (ecranul de emitere, cererea ca
EmitereIn) -> `firma_profil_date_salveaza` (Date firmă) -> din nou `facturi_emite` -> `factura_pdf_ruta` (PDF-ul, citit
cu pdftotext). `commit` neutralizat, ROLLBACK la final.
  · cod VECHI: factura se emite, iar PDF-ul nu are capitalul social;
  · cod NOU: emiterea e refuzată structurat (ce lipsește + Date firmă + temeiul); după completarea formei și a
    capitalului, aceeași cerere se emite, iar PDF-ul tipărește „Capital social: 200,00 lei”.
"""
import contextlib
import os
import subprocess
import sys
import tempfile
import types

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, observare, uc_tenants  # noqa: E402

observare.alerteaza = lambda *a, **k: None
try:
    from core import capital_social  # noqa: F401
    NOU = True
except ImportError:
    NOU = False
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
db.init_pool()
real = db.get_conn


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import EmitereIn  # noqa: E402  modelul cererii, exact ca ruta


def cerere():
    return EmitereIn(tip="factura", linii=[{"descriere": "Consultanta contabila", "cantitate": 1, "pret_unitar": 1000,
                                            "um": "buc", "cota_tva": 21, "cont_venit": "704"}],
                     tert_nume="DANTE INTERNATIONAL SA", tert_cui="14399840", data_emitere="2026-09-30",
                     pleaca_marfa=False)


with real() as conn:
    px = _Fara(conn)

    def _gc(schema=None, *a, **k):
        if schema:
            conn.cursor().execute("SET search_path TO %s, public" % schema)
        yield px
    db.get_conn = contextlib.contextmanager(_gc)
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name='tenant_049'")
        tid, cab = cur.fetchone()
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}

        def emite(et):
            try:
                r = uc_tenants.facturi_emite(tid, cerere(), ctx)
                print("  %s: EMISĂ %s, total %s" % (et, r.get("numar"), r.get("total")))
                return r
            except Exception as e:
                d = getattr(e, "detaliu", e)
                print("  %s: REFUZ %s" % (et, d if isinstance(d, dict) else str(d)[:200]))
                return None

        r = emite("emitere (profil fără capital)")
        if r is None and NOU:
            uc_tenants.firma_profil_date_salveaza(tid, {"forma_juridica": "SRL", "capital_subscris": "200"}, ctx)
            print("  Date firmă: forma SRL, capital social 200 lei salvate")
            r = emite("aceeași cerere, din nou")
        if r and r.get("factura_id"):
            pdf, _nume = uc_tenants.factura_pdf_ruta(tid, r["factura_id"], ctx)
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(pdf)
            txt = subprocess.run(["pdftotext", f.name, "-"], capture_output=True, text=True).stdout
            rand = [l for l in txt.splitlines() if "Capital" in l]
            print("  PDF: %s" % (rand or "fără capital social"))
    finally:
        db.get_conn = real
        conn.rollback()
        print("  ROLLBACK — nimic scris")
