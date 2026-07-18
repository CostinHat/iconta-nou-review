"""
core/migrare_etransport_trimiteri.py — urmarirea trimiterilor e-Transport UIT (F121).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). PER-TENANT, self-contained (notificarile
e-Transport NU sunt persistate ca facturile - se genereaza din formular; aici stocam trimiterea).
Idempotent (CREATE TABLE/INDEX IF NOT EXISTS). Se aplica: tenanti NOI prin template; EXISTENTI prin
`python3 -m core.migrare_etransport_trimiteri`.

GARDA DE TIMP UIT (specifica e-Transport, NU copiata de la factura): codul UIT + valabilitatea sunt
stocate (data_transport, uit_valabil_pana, intracom). Termen legal (ARHITECTURA_SPV.md): declarare max
3 zile INAINTE de miscare; UIT valabil 5 zile (national) / 15 zile (intracomunitar). Folosire dupa expirare
= blocata (verificata la trimitere de fereastra_uit, nu doar stocata).
DEDUP: index unic partial pe xml_sha256 pe PROD (stari vii) - upload-ul ANAF nu e idempotent (dubla
trimitere a aceleiasi notificari = UIT dublu pt acelasi transport).
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS "{s}".etransport_trimiteri (
  id                BIGSERIAL PRIMARY KEY,
  mediu             TEXT NOT NULL CHECK (mediu IN ('test','prod')),
  stare             TEXT NOT NULL DEFAULT 'pregatit'
                    CHECK (stare IN ('pregatit','eroare_upload','incarcat','ok','nok')),
  index_incarcare   TEXT,
  uit               TEXT,
  data_transport    DATE,
  intracom          BOOLEAN NOT NULL DEFAULT false,
  uit_valabil_pana  DATE,
  execution_status  INTEGER,
  error_message     TEXT,
  ref_declarant     TEXT,
  xml_trimis        TEXT,
  xml_sha256        TEXT NOT NULL,
  trimis_la         TIMESTAMPTZ,
  creat_la          TIMESTAMPTZ NOT NULL DEFAULT now(),
  actualizat_la     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_etransport_trimiteri_viu
  ON "{s}".etransport_trimiteri (xml_sha256)
  WHERE mediu='prod' AND stare IN ('incarcat','ok');
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_name='etransport_trimiteri'", (schema,))
        tabel = cur.fetchone()[0] == 1
        cur.execute("SELECT count(*) FROM pg_indexes "
                    "WHERE schemaname=%s AND indexname='uq_etransport_trimiteri_viu'", (schema,))
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
    print("Migrare etransport_trimiteri: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
