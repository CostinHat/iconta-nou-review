# -*- coding: utf-8 -*-
"""core/test_migrare_program_national_cm.py — gard: fiecare schema de tenant are concedii_medicale.program_national (D_9a)."""
import pytest
from core import db
from core.migrare_program_national_cm import verifica


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SQL = "SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_toti_tenantii_au_program_national():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_SQL)
            scheme = [r[0] for r in cur.fetchall()]
        if not scheme:
            pytest.skip("niciun tenant in mediu")
        lipsa = [s for s in scheme if not verifica(conn, s)]
    assert not lipsa, ("scheme FARA program_national (ruleaza python3 -m core.migrare_program_national_cm): %s" % lipsa)
