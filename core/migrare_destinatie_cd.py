# -*- coding: utf-8 -*-
"""core/migrare_destinatie_cd.py — coloana `destinatie_cd` pe mijloace_fixe (lot 19, defectul 11, 03.10.2026).

CF art.20 alin.(1) lit.b): „aplicarea metodei de amortizare accelerată și în cazul aparaturii și echipamentelor
destinate activităților de cercetare-dezvoltare”; art.20^1 alin.(8): „Prevederile art. 20 alin. (1) lit. b) se aplică
și în situația în care contribuabilul optează pentru aplicarea creditului fiscal”. Registrul nu stia ca un activ e
destinat C&D, deci accelerata se refuza pe orice cont altul decat 2131. Decizia lui Costin (03.10.2026): coloana +
bifa. Default FALSE = cazul obisnuit. Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent.
Se aplica pe ORICE schema care are tabela (nu doar `tenant_N`: si schemele de test ramase), ca niciun cititor sa nu
cada pe o coloana lipsa. Tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_destinatie_cd`.
"""
from core import db

DDL = 'ALTER TABLE "{s}".mijloace_fixe ADD COLUMN IF NOT EXISTS destinatie_cd boolean NOT NULL DEFAULT false;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='mijloace_fixe' AND column_name='destinatie_cd'", (schema,))
        return cur.fetchone()[0] == 1


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                    "WHERE table_name='mijloace_fixe' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_tabela(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare destinatie_cd: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
