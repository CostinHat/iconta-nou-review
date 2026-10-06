# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — punctul 4 (decizia Costin 03.10.2026): retragerea coloanei `salariati.salariu_brut`.

    python frontend_test/proba_2b_coloana.py <radacina_cod>
F1 (tenant_049, 3 salariați) din baza de producție, septembrie 2026, într-o tranzacție ANULATĂ:
  1) statul de plată + D112 (cifrele + DUK) cu coloana încă prezentă;
  2) migrarea `core.migrare_2b_coloana.aplica` (backfill + DROP COLUMN), în aceeași tranzacție;
  3) aceleași calcule după.
  · cod VECHI: după DROP, statul de plată crapă (`SELECT … salariu_brut` din stat_plata_api) — coloana era încă citită;
  · cod NOU: aceleași cifre înainte și după (salariul vine numai din salariu_istoric), D112 DUK valid.
"""
from core.common import Perioada  # [D1, lotul 07.10] d112.pull/genereaza(conn, schema, perioada)
import os
import sys

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare, stat_plata_api, d112, duk  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = os.path.exists(os.path.join(RAD, "core", "migrare_2b_coloana.py"))
S, AN, LUNA = "tenant_049", 2026, 9
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))


def _cifre(conn, et):
    try:
        st = stat_plata_api.stat_plata(conn, S, AN, LUNA)
        rand = [(r["nume"], r["brut"], r["cas"], r["cass"], r["impozit"], r["net"]) for r in st]
        print("  %s — stat de plată: %s" % (et, rand))
    except Exception as e:
        print("  %s — stat de plată CRAPĂ: %s" % (et, str(e).split("\n")[0][:200]))
        conn.rollback()
        return None
    try:
        xml, res = d112.genereaza(conn, S, Perioada(an=AN, luna=LUNA))
        v = duk.valideaza(xml, "d112", an=AN, luna=LUNA, timeout=240)
        print("  %s — D112: %d caractere, DUK %s%s" % (et, len(xml), v["stare"],
                                                     (" — " + (v.get("erori") or "")[:160]) if v.get("erori") else ""))
        return rand, len(xml)
    except Exception as e:
        print("  %s — D112 REFUZ: %s" % (et, str(e)[:200]))
        return rand, None


db.init_pool()
with db.get_conn() as conn:
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % S)
            cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='salariati' "
                        "AND column_name='salariu_brut'", (S,))
            print("  coloana salariati.salariu_brut prezentă: %s" % bool(cur.fetchone()[0]))
        inainte = _cifre(conn, "ÎNAINTE")
        if NOU:
            from core import migrare_2b_coloana as m
            print("  migrare (în tranzacție): %s" % m.aplica(conn, S))
        else:
            with conn.cursor() as cur:
                cur.execute('ALTER TABLE "%s".salariati DROP COLUMN IF EXISTS salariu_brut' % S)
            print("  DROP COLUMN (în tranzacție), cod vechi")
        dupa = _cifre(conn, "DUPĂ")
        print("  VERDICT: %s" % ("IDENTIC înainte/după" if (inainte and dupa and inainte == dupa)
                                 else "DIFERIT / CRAPĂ"))
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
