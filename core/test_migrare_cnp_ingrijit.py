# -*- coding: utf-8 -*-
"""core/test_migrare_cnp_ingrijit.py — gard: fiecare schema de TENANT are coloana cnp_ingrijit (D_8/D_8a).

Coloana e ceruta de D112 pentru concediile de ingrijire copil (09/91/92) / pacient oncologic (17). Daca un tenant
n-o are, generarea D112 crapa pe SELECT sau emite gresit. Tiparul REAL al schemelor de tenant e `^tenant_[0-9]+$`
(verificat: singurul tenant real e tenant_001; restul schemelor non-sistem sunt ztest_* = reziduuri de test, NU
tenanti). Gardul reutilizeaza verifica() din modulul de migrare (sursa unica a definitiei coloanei).
"""
import pytest
from core import db
from core.migrare_cnp_ingrijit import verifica


def _db_ok():
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


_SCHEME_TENANT_SQL = "SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_toti_tenantii_au_cnp_ingrijit():
    """Fiecare schema de tenant (^tenant_[0-9]+$) are concedii_medicale.cnp_ingrijit. Pica daca migrarea n-a rulat
    pe un tenant (ruleaza `python3 -m core.migrare_cnp_ingrijit`)."""
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(_SCHEME_TENANT_SQL)
            scheme = [r[0] for r in cur.fetchall()]
        assert scheme, "niciun tenant ^tenant_[0-9]+$ - mediul de test n-are tenanti reali"
        lipsa = [s for s in scheme if not verifica(conn, s)]
    assert not lipsa, ("scheme de tenant FARA cnp_ingrijit (ruleaza migrarea): %s" % lipsa)
