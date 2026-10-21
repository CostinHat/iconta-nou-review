"""
core/migrare_compensari_afiliat.py — compensările de creanțe și datorii și beneficiarul afiliat (lotul 10, deficiența 428, deciziile
Costin 20.10.2026, verbatim în DECIZII „Lotul 10: deciziile lui Costin la întrebările din lot”): „Construiesc acum” — tabelă de compensări
(factura emisă ↔ factura primită, suma, data) și ecran; fiecare compensare stinge cele două facturi și mută TVA-ul prin același punct ca
banca și casa; „Bifă pe client” — câmpul „persoană afiliată (art.7 pct.26)” pe client.

Temei: CF art.282 alin.(3) și (8) (încasarea, inclusiv prin compensare, face exigibilă partea încasată); CF art.282 alin.(6) lit.d
(beneficiarul afiliat furnizorului — art.7 pct.26 — rămâne pe regulile generale). `compensari`: un rând pe compensare (o creanță pe o
factură emisă stinsă cu o datorie pe o factură primită, același partener), legat de nota ei (ON DELETE CASCADE). `clienti.afiliat`:
bifa clientului; `facturi.beneficiar_afiliat`: faptul înghețat pe factură la emitere (citit de motorul TVA la încasare).

Coloane / tabele noi, goale: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_compensari_afiliat.py`.
"""
from core import db

_DDL = [
    "CREATE TABLE IF NOT EXISTS \"{s}\".compensari (id serial PRIMARY KEY, data date NOT NULL, "
    "factura_emisa_id integer NOT NULL REFERENCES \"{s}\".facturi(id), factura_primita_id integer NOT NULL REFERENCES \"{s}\".facturi(id), "
    "suma numeric(15,2) NOT NULL CHECK (suma > 0), inregistrare_id integer REFERENCES \"{s}\".inregistrari(id) ON DELETE CASCADE, "
    "document_ref text, creat_la timestamptz NOT NULL DEFAULT now());",
    "CREATE INDEX IF NOT EXISTS compensari_emisa ON \"{s}\".compensari (factura_emisa_id);",
    "CREATE INDEX IF NOT EXISTS compensari_primita ON \"{s}\".compensari (factura_primita_id);",
    "ALTER TABLE \"{s}\".clienti ADD COLUMN IF NOT EXISTS afiliat boolean NOT NULL DEFAULT false;",
    "ALTER TABLE \"{s}\".facturi ADD COLUMN IF NOT EXISTS beneficiar_afiliat boolean NOT NULL DEFAULT false;",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT (SELECT count(*) FROM information_schema.tables WHERE table_schema=%s AND table_name='compensari') + "
                    "(SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND ((table_name='clienti' AND "
                    "column_name='afiliat') OR (table_name='facturi' AND column_name='beneficiar_afiliat')))", (schema, schema))
        return cur.fetchone()[0] == 3


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
    print("migrare_compensari_afiliat: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
