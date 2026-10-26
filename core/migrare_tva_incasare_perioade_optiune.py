"""
core/migrare_tva_incasare_perioade_optiune.py — data notificării (opțiunii) pe perioadele sistemului TVA la încasare (deficiența 541, lotul 13,
comanda 13.1, verbatim: „Pe 22.10.2026 s-a salvat «Aplică de la 01.10.2026» fără avertisment: opțiunea nu se aplică retroactiv în perioada în
curs, ci din prima zi a perioadei fiscale următoare (art. 282; F2 trimestrială → 01.01.2027). Aplicația refuză sau propune data corectă.”).
Temei: CF art.282 alin.(3^1) lit.a) — „aplică sistemul TVA la încasare începând cu prima zi a perioadei fiscale următoare celei în care
persoana impozabilă și-a exercitat opțiunea” (anaf_surse/cod_fiscal_227_2015_consolidat.txt; regula: `core/regim_tva_incasare.erori_optiune`).

`data_optiune` = data la care s-a depus notificarea la ANAF (NULL = nescrisă). Coloană nouă, goală: datele existente nu se ating — perioadele
scrise înainte rămân fără dată, iar ecranul avertizează pe cele scrise retroactiv în perioada în curs (`regim_tva_incasare.avertisment_optiune`,
derivat din `creat_la`). Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (IF NOT EXISTS). Firmele existente:
`python -m core.migrari_registru ruleaza [--productie] core/migrare_tva_incasare_perioade_optiune.py` (după `migrare_tva_incasare_perioade.py`,
care creează tabela — `migrari_registru.DUPA`).
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".tva_incasare_perioade ADD COLUMN IF NOT EXISTS data_optiune date;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='tva_incasare_perioade' "
                    "AND column_name='data_optiune'", (schema,))
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
    print("migrare_tva_incasare_perioade_optiune: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
