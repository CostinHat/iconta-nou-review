"""
core/migrare_efactura_primite.py — facturi PRIMITE de la furnizori din SPV (F126 receive, F179).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). PER-TENANT (FK spre facturi(id)). Idempotent.
Se aplica: tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_efactura_primite`.

Schema stabilita de Costin (18.07). DEDUP: id_mesaj_anaf UNIC - cronul ruleaza la 30 min pe fereastra
de 2-3 zile suprapuse, aceeasi factura apare la mai multe rulari; INSERT ... ON CONFLICT DO NOTHING.
GARD anti-scurgere: cif_beneficiar TREBUIE = CIF-ul tenantului (validat la insert de cron, nu doar stocat).
MASINA DE STARI: descarcata (auto) -> ciorna (parsata, prezentata contabilului) -> validata (om confirma,
ABIA atunci se creeaza cheltuiala si se leaga factura_id) sau respinsa. factura_id NULL pana la four-eyes.
Vezi DECIZII.md 18.07 + ARHITECTURA_SPV.md (listaMesajeFactura).
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".efactura_primite (
  id                BIGSERIAL PRIMARY KEY,
  id_mesaj_anaf     TEXT NOT NULL,
  id_solicitare     TEXT,
  cif_emitent       TEXT NOT NULL,
  cif_beneficiar    TEXT NOT NULL,
  data_creare       TIMESTAMPTZ,
  tip               TEXT,
  xml_brut          TEXT,
  xml_sha256        TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'descarcata'
                    CHECK (status IN ('descarcata','ciorna','validata','respinsa')),
  factura_id        BIGINT REFERENCES "{s}".facturi(id),
  importat_la       TIMESTAMPTZ NOT NULL DEFAULT now(),
  validat_la        TIMESTAMPTZ
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_efactura_primite_mesaj
  ON "{s}".efactura_primite (id_mesaj_anaf);
-- four-eyes (pasul 5): motivul respingerii + contul de cheltuiala confirmat de om
ALTER TABLE "{s}".efactura_primite ADD COLUMN IF NOT EXISTS motiv_respins  TEXT;
ALTER TABLE "{s}".efactura_primite ADD COLUMN IF NOT EXISTS cont_cheltuiala TEXT;
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_name='efactura_primite'", (schema,))
        tabel = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM pg_indexes "
                    "WHERE schemaname=%s AND indexname='uq_efactura_primite_mesaj'", (schema,))
        idx = cur.fetchone()[0] == 1
    return tabel and idx


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
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                    print("  OK  %s" % s)
                else:
                    esec.append(s)
                    print("  ESEC (verificare)  %s" % s)
        except Exception as e:
            esec.append(s)
            print("  ESEC %s: %s" % (s, e))
    print("Migrare efactura_primite: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
