"""
core/migrare_efactura_trimiteri.py — tabelul de urmarire a trimiterilor e-Factura (F126/F160, pasul 2).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). PER-TENANT: referinta e facturi(id),
care traieste in fiecare schema tenant. Idempotent (CREATE TABLE/INDEX IF NOT EXISTS). Se aplica:
  - tenanti NOI: prin tenant_template.sql;
  - tenanti EXISTENTI: `python3 -m core.migrare_efactura_trimiteri`.

Schema stabilita de Costin (18.07). Coloane-cheie:
  - mediu ('test'/'prod'): separa validarile pe TEST de trimiterile reale.
  - stare: pregatit -> eroare_upload | incarcat -> in_prelucrare -> ok | nok (masina de stari SPV).
  - index_incarcare / id_descarcare: id-urile ANAF (upload, apoi recipisa de descarcat).
  - xml_sha256 / xml_semnat_sha256: amprenta XML trimis + a XML-ului semnat intors de ANAF.
INDEX UNIC PARTIAL uq_efactura_trimiteri_viu: un singur send VIU per factura pe PROD - upload-ul
ANAF NU e idempotent, o dubla trimitere = dubla factura la ANAF. Pe 'test' nu blocheaza (validari
repetate permise). Vezi DECIZII.md 18.07 "Tabel urmarire trimiteri e-Factura".
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".efactura_trimiteri (
  id                BIGSERIAL PRIMARY KEY,
  factura_id        BIGINT NOT NULL REFERENCES "{s}".facturi(id),
  mediu             TEXT NOT NULL CHECK (mediu IN ('test','prod')),
  stare             TEXT NOT NULL DEFAULT 'pregatit'
                    CHECK (stare IN ('pregatit','eroare_upload','incarcat','in_prelucrare','ok','nok')),
  index_incarcare   TEXT,
  execution_status  INTEGER,
  id_descarcare     TEXT,
  error_message     TEXT,
  xml_trimis        TEXT,
  xml_sha256        TEXT NOT NULL,
  zip_raspuns_path  TEXT,
  xml_semnat_sha256 TEXT,
  trimis_la         TIMESTAMPTZ,
  finalizat_la      TIMESTAMPTZ,
  creat_la          TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizat_la     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_efactura_trimiteri_viu
  ON "{s}".efactura_trimiteri (factura_id)
  WHERE mediu='prod' AND stare IN ('incarcat','in_prelucrare','ok');
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_name='efactura_trimiteri'", (schema,))
        tabel = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM pg_indexes "
                    "WHERE schemaname=%s AND indexname='uq_efactura_trimiteri_viu'", (schema,))
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
    print("Migrare efactura_trimiteri: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
