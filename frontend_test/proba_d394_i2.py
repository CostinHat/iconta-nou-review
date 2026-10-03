# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — D394 Î2: încasările din activități exceptate de la AMEF (decizia Costin 03.10.2026, „cotă pe
chitanță”). INVALID pe codul vechi, VALID pe nou.

    python frontend_test/proba_d394_i2.py <radacina_cod>
F1 (tenant_049, plătitor lunar) din baza de producție, septembrie 2026, pe calea aplicației (`uc_tenants`: emiterea
chitanței, dispoziția de casă, clasificarea, cu cererile ca modelele rutelor). TOTUL într-o tranzacție ANULATĂ la final
(`commit` neutralizat); `observare.alerteaza` neutralizat.
  · cod VECHI: chitanța fără factură se emite doar ca încasare de creanță (5311=4111); D394 iese fără Î2, iar TVA-ul
    vânzării lipsește din D300 — vânzarea fără factură a firmei exceptate nu ajunge în nicio declarație.
  · cod NOU: (1) firmă neexceptată + cotă -> refuz numit; (2) chitanță fără cotă emisă înainte de marcare -> D394 refuză
    NUMIT; (3) după clasificare: op2 Î2 (fără nrAMEF/nrBF), rezumat2 *_incasari_i2, incasari_i2, avertismentul pentru
    încasarea din casă fără chitanță, DUK valid; D300 rd.9/10 cu baza și TVA-ul chitanțelor.
"""
import contextlib
import os
import sys
import xml.etree.ElementTree as ET

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, uc_tenants  # noqa: E402
from core.common import Perioada  # noqa: E402

observare.alerteaza = lambda *a, **k: None
from core import d300, d394, duk  # noqa: E402
from main import ChitantaEmite  # noqa: E402
try:
    from main import ChitantaCota  # noqa: E402
    NOU = True
except ImportError:
    NOU = False
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))
S = "tenant_049"
P = Perioada(2026, luna=9)


class _Fara:
    def __init__(self, c):
        self._c = c

    def commit(self):
        pass

    def __getattr__(self, n):
        return getattr(self._c, n)


def _detaliu(e):
    d = getattr(e, "detaliu", e)
    return ("%s — %s" % (d.get("cod"), d.get("mesaj"))) if isinstance(d, dict) else str(d)


def _arata394(xml):
    rad = ET.fromstring(xml.split("?>", 1)[1])
    ns = rad.tag.split("}")[0] + "}"
    inf = rad.find(ns + "informatii")
    print("  D394 informatii incasari_i1=%s incasari_i2=%s · op_efectuate=%s" % (
        inf.get("incasari_i1"), inf.get("incasari_i2"), rad.get("op_efectuate")))
    for o in rad.iter(ns + "op2"):
        print("   op2:", dict(o.attrib))
    for r in rad.iter(ns + "rezumat2"):
        if r.get("baza_incasari_i2") not in (None, "0") or r.get("tva_incasari_i2") not in (None, "0"):
            print("   rezumat2 cota %s: baza_incasari_i2=%s tva_incasari_i2=%s" % (
                r.get("cota"), r.get("baza_incasari_i2"), r.get("tva_incasari_i2")))
    v = duk.valideaza(xml, "d394", an=2026, luna=9, timeout=180)
    print("  DUK D394: %s, severitate %s%s" % (v["stare"], v.get("severitate"),
                                             (" — " + (v.get("erori") or "").replace("\n", " ")[:300]) if v.get("erori") else ""))


def _arata300(conn):
    try:
        xml, res = d300.genereaza(conn, S, P)
        print("  D300 R9 (21%%): baza %s TVA %s · R10 (11%%): baza %s TVA %s" % (
            res.R.get("R9_1"), res.R.get("R9_2"), res.R.get("R10_1"), res.R.get("R10_2")))
    except Exception as e:
        print("  D300 REFUZ: %s" % str(e)[:300])


db.init_pool()
real = db.get_conn
with real() as conn:
    px = _Fara(conn)

    def _gc(schema=None, *a, **k):
        if schema:
            conn.cursor().execute("SET search_path TO %s, public" % schema)
        yield px
    db.get_conn = contextlib.contextmanager(_gc)
    try:
        cur = conn.cursor()
        cur.execute("SET search_path TO %s, public" % S)
        cur.execute("SELECT id, accounting_firm_id FROM public.tenants WHERE schema_name=%s", (S,))
        tid, cab = cur.fetchone()
        cur.execute("SELECT id FROM public.users WHERE rol='admin_firma' AND accounting_firm_id=%s LIMIT 1", (cab,))
        ctx = {"uid": cur.fetchone()[0], "rol": "admin_firma"}

        def chit(et, **k):
            try:
                r = uc_tenants.chitanta_emite(tid, ChitantaEmite(**k), ctx)
                cur.execute("SET search_path TO %s, public" % S)
                cur.execute("SELECT l.cont_debit||'='||l.cont_credit||' '||l.suma FROM inregistrari_linii l "
                            "JOIN chitante c ON c.inregistrare_id = l.inregistrare_id WHERE c.id = %s ORDER BY l.id",
                            (r["chitanta_id"],))
                print("  %s: EMISĂ %s-%s, nota %s" % (et, r["serie"], r["numar"], [x[0] for x in cur.fetchall()]))
                return r
            except Exception as e:
                print("  %s: REFUZ %s" % (et, _detaliu(e)[:240]))

        print("[1] firma NEexceptată:")
        vechi = chit("chitanță fără factură, fără cotă (emisă înainte de marcare)", data="2026-09-05", suma=242,
                     **({"client_nume": "Maria Ionescu", "reprezentand": "reparatie instalatie"} if NOU else {}))
        if NOU:
            chit("chitanță fără factură CU cotă", data="2026-09-05", suma=121, cota_tva=21)
            cur.execute("UPDATE firma_profil SET activitate_exceptata_amef = true, activitate_amef = 'i'")
            print("[2] Date firmă: exceptată de la AMEF, OUG 28/1999 art.2 lit.i (instalații la domiciliul clientului)")
            chit("vânzare 21%", data="2026-09-12", suma=1210, cota_tva=21, client_nume="Ion Popescu",
                 reprezentand="reparatie centrala termica")
            chit("vânzare 11%", data="2026-09-18", suma=333, cota_tva=11, client_nume="Ana Dumitru")
            chit("vânzare 0% (scutit)", data="2026-09-20", suma=100, cota_tva=0)
            chit("fără cotă", data="2026-09-21", suma=50)
            uc_tenants.casa_adauga(tid, {"data": "2026-09-22", "categorie": "incasare_client", "suma": 400,
                                         "partener": "Client fara chitanta", "document": "DI-7"}, ctx)
            uc_tenants.casa_adauga(tid, {"data": "2026-09-23", "categorie": "ridicare_banca", "suma": 1000}, ctx)
            print("  casa: încasare client 400 lei fără chitanță (DI-7) + ridicare de la bancă 1000 lei")
            try:
                d394.genereaza(conn, S, P)
                print("  D394: GENERAT (greșit — chitanța fără cotă trebuia numită)")
            except ValueError as e:
                print("  D394: REFUZ cod=%s chitanțe=%s" % (getattr(e, "cod", None), getattr(e, "chitante", None)))
                print("    mesaj: %s" % str(e)[:330])
            cur.execute("SET search_path TO %s, public" % S)
            cur.execute("SELECT id FROM chitante WHERE factura_id IS NULL AND cota_tva IS NULL ORDER BY id")
            for (cid,) in cur.fetchall():
                r = uc_tenants.chitanta_cota(tid, cid, ChitantaCota(cota_tva=21), ctx)
                print("[3] Casă «Stabilește cota» chitanța %s -> 21%%, nota %s" % (cid, r["nota"]))
        try:
            xml, res = d394.genereaza(conn, S, P)
            _arata394(xml)
            for a in res.avertismente:
                if "registrul de casă" in a:
                    print("  AVERTISMENT: %s" % a[:300])
        except Exception as e:
            print("  D394 REFUZ: %s" % str(e)[:400])
        _arata300(conn)
        if vechi and not NOU:
            print("  VERDICT: INCOMPLET — vânzarea încasată pe chitanță lipsește din D394 Î2 și din D300")
    finally:
        db.get_conn = real
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
