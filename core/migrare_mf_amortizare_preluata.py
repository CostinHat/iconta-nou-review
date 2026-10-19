"""
core/migrare_mf_amortizare_preluata.py — `mijloace_fixe.amortizare_preluata` / `data_preluare` pe fiecare firmă (deficiența 359, comanda
Costin 8.2, 18.10.2026, verbatim în DECIZII „Comanda 8.2”: „amortizarea cumulată (și valoarea rămasă) la data preluării se preia din
registrul vechi; iConta o compară cu ce rezultă din PIF + durată + metodă și semnalează diferențele [...]”).

Coloane noi, goale: mijloacele fixe existente rămân cum sunt (fără cifră preluată, auditul le arată ca atare).
Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS). Se aplică: firmele NOI prin template;
cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie] core/migrare_mf_amortizare_preluata.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".mijloace_fixe ADD COLUMN IF NOT EXISTS amortizare_preluata numeric;",
    "ALTER TABLE \"{s}\".mijloace_fixe ADD COLUMN IF NOT EXISTS data_preluare date;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='mijloace_fixe' "
                    "AND column_name IN ('amortizare_preluata', 'data_preluare')", (schema,))
        return cur.fetchone()[0] == 2


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_mf_amortizare_preluata: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
