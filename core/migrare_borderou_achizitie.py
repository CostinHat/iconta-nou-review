"""
core/migrare_borderou_achizitie.py — `facturi.tert_act_identitate`: actul de identitate (seria și numărul) al persoanei fizice de la care
se cumpără pe borderou de achiziție (deficiențele 401–402, retestul Costin 19.10.2026: „furnizorul doar nume, fără datele de
identificare cerute pe borderou”). Temei: OMFP 2634/2015 anexa 1 pct.2 — documentul justificativ cuprinde „menționarea părților
care participă la efectuarea operațiunii economico-financiare”.

Coloană nouă, goală: documentele existente rămân cum sunt. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent.
Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_borderou_achizitie.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".facturi ADD COLUMN IF NOT EXISTS tert_act_identitate text;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='facturi' "
                    "AND column_name = 'tert_act_identitate'", (schema,))
        return cur.fetchone()[0] == 1


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
    print("migrare_borderou_achizitie: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
