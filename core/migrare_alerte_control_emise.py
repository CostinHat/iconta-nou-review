"""
core/migrare_alerte_control_emise.py — jurnal de idempotenta al alertelor de control fiscal (public).

SCHEMA PUBLIC (nu tenant). Pattern public.alerte_emise / F103: dedup al notificarilor de control
per (tenant, verificator, perioada). SURSA DE ADEVAR a schemei.

Era declarata ca o constanta-string (DDL_JURNAL in alerte_control_fiscal.py) aplicata MANUAL prin
superuser (sudo -u postgres psql + ALTER OWNER TO iconta_user) fiindca iconta_user n-avea CREATE pe
schema public. Golul e inchis (GRANT CREATE ON SCHEMA public, DECIZII 22.07 [INFRA]) -> DDL-ul a
devenit o migrare normala, idempotenta, rulata CA iconta_user. Fara pas manual, fara cod mort.

Idempotent (CREATE TABLE IF NOT EXISTS). Tabelul exista deja in prod -> no-op acolo; un server nou
il primeste de aici.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS public.alerte_control_emise (
    tenant_id   integer     NOT NULL,
    verificator text        NOT NULL,
    perioada    text        NOT NULL,
    emisa_la    timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT alerte_control_emise_pkey PRIMARY KEY (tenant_id, verificator, perioada)
)
"""


def aplica(conn):
    """Aplica DDL-ul idempotent pe public. Comiterea o face apelantul / _main."""
    with conn.cursor() as cur:
        cur.execute(DDL)


def verifica(conn):
    """True daca public.alerte_control_emise exista."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.alerte_control_emise')")
        return cur.fetchone()[0] is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        aplica(conn)
    with db.get_conn() as conn:
        ok = verifica(conn)
    print("Migrare alerte_control_emise (public): %s" % ("OK" if ok else "ESEC"))
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
