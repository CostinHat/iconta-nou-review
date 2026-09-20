# -*- coding: utf-8 -*-
"""SESIUNEA B — F1 ETAPA 8 (Declaratii - generare) + validare DUK.
Genereaza D300/D394/D112/D100 pe fluxul F1 (sept 2026; D100 trim Q3) si valideaza pe validatorul
oficial DUK. D406 = STOP (finding SPV<->stoc, decizie Costin). Vezi asteptari_f1_etapa8.md.
Rulare (cu env): set -a; . ~/.iconta/db.env; . ~/.iconta/api_keys.env; set +a; ./venv/bin/python frontend_test/proba_f1_etapa8.py
"""
import os
import sys

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _RAD)
import core.db as _db  # noqa: E402
from core import d300, d394, d112, d100, d406, duk  # noqa: E402
from core.common import Perioada  # noqa: E402

SCH = "tenant_049"


def _val(xml, tip, an=2026, luna=9):
    r = duk.valideaza(xml, tip, an=an, luna=luna)
    return (r.get("stare"), (r.get("erori") or "")[:200]) if isinstance(r, dict) else (r, "")


def main():
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SET search_path TO %s, public' % SCH)
        x, _ = d300.genereaza(conn, SCH, Perioada(2026, luna=9)); print("D300:", _val(x, "d300"))
        r = d394.genereaza(conn, SCH, Perioada(2026, luna=9)); print("D394:", _val(r[0] if isinstance(r, tuple) else r, "d394"))
        r = d112.genereaza(conn, SCH, 2026, 9); print("D112:", _val(r[0] if isinstance(r, tuple) else r, "d112"))
        r = d100.genereaza(conn, SCH, Perioada(2026, trim=3)); print("D100:", _val(r[0] if isinstance(r, tuple) else r, "d100", luna=None))
        # D406 (SAF-T): deblocat dupa reparatia reconcilierii SPV<->stoc (finding inchis) + curatarea F1 (cont 371, cantitate D2).
        r = d406.genereaza(conn, SCH, 2026, 9); print("D406:", _val(r[0] if isinstance(r, tuple) else r, "d406"))


if __name__ == "__main__":
    main()
