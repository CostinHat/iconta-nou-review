# -*- coding: utf-8 -*-
"""SESIUNEA B — F2 ETAPA 8 (Declaratii) + validare DUK. Profit 16%/TVA trimestrial.
Ruleaza cu env: set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; ./venv/bin/python frontend_test/proba_f2_etapa8.py
"""
import os, sys
_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,_RAD)
import core.db as _db  # noqa: E402
from core import d300, d394, d100, d406, duk  # noqa: E402
from core.common import Perioada  # noqa: E402
SCH="tenant_050"
def _val(x,tip,an=2026,luna=9):
    r=duk.valideaza(x,tip,an=an,luna=luna); return (r.get("stare"),(r.get("erori") or "")[:200]) if isinstance(r,dict) else (r,"")
def main():
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur: cur.execute('SET search_path TO %s, public'%SCH)
        x,_=d300.genereaza(conn,SCH,Perioada(2026,luna=9)); print("D300(T3):",_val(x,"d300"))
        r=d394.genereaza(conn,SCH,Perioada(2026,luna=9)); print("D394:",_val(r[0] if isinstance(r,tuple) else r,"d394"))
        r=d100.genereaza(conn,SCH,Perioada(2026,trim=3)); print("D100(T3):",_val(r[0] if isinstance(r,tuple) else r,"d100",luna=None))
        r=d406.genereaza(conn,SCH,2026,9); print("D406:",_val(r[0] if isinstance(r,tuple) else r,"d406"))
    print("D101 (profit ANUAL) = la inchiderea anului, nu mid-year.")
if __name__=="__main__": main()
