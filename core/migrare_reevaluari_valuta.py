"""
core/migrare_reevaluari_valuta.py — reevaluarea lunară a soldurilor în valută propusă de aplicație (deficiența 429, comanda Costin 10.1, verbatim
în DECIZII „Comanda 10.1”): „La închiderea lunii, aplicația propune singură creanțele și datoriile în valută neîncasate (pe factură),
disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și diferența pe 665/765”. Temei: OMFP 1802/2014
pct.325 alin.(1)–(2) (reevaluarea lunară a creanțelor, datoriilor și disponibilităților în valută la cursul BNR din ultima zi bancară a lunii). Un rând pe element reevaluat (factura sau contul de disponibilități),
legat de nota generată; cursul nou devine cursul din evidență al lunii următoare. Ștergerea notei (ciornă) șterge rândurile.

Coloane / tabele noi, goale: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_reevaluari_valuta.py`.
"""
from core import db

_DDL = [
    "CREATE TABLE IF NOT EXISTS \"{s}\".reevaluari_valuta (id serial PRIMARY KEY, data date NOT NULL, "
    "inregistrare_id integer NOT NULL REFERENCES \"{s}\".inregistrari(id) ON DELETE CASCADE, "
    "factura_id integer REFERENCES \"{s}\".facturi(id) ON DELETE CASCADE, cont text NOT NULL, moneda text NOT NULL, "
    "sold_valuta numeric(15,2) NOT NULL, curs_vechi numeric(12,4) NOT NULL, curs_nou numeric(12,4) NOT NULL, "
    "diferenta numeric(15,2) NOT NULL, creat_la timestamptz NOT NULL DEFAULT now());",
    "CREATE INDEX IF NOT EXISTS reevaluari_valuta_factura ON \"{s}\".reevaluari_valuta (factura_id, data);",
    # sursa rândului: propunerea din Închidere lună sau formularul manual — generarea înlocuiește numai ciornele PROPUNERII
    "ALTER TABLE \"{s}\".reevaluari_valuta ADD COLUMN IF NOT EXISTS sursa text NOT NULL DEFAULT 'propunere' "
    "CHECK (sursa IN ('propunere', 'manual'));",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='reevaluari_valuta' "
                    "AND column_name='sursa'", (schema,))
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
    print("migrare_reevaluari_valuta: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
