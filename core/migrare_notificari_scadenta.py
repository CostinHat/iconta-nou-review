"""
core/migrare_notificari_scadenta.py — schema F131 comp.5 (notificari scadenta).

Sursa UNICA a DDL-ului (folosit si de tenant_template.sql, mirror). Idempotent:
CREATE TABLE IF NOT EXISTS + ALTER ... ADD COLUMN IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: prin `python3 -m core.migrare_notificari_scadenta` (comanda
    separata, ruleaza pe TOATE schemele tenant_% si verifica fiecare).

Ce adauga:
  - tabel notificari_scadenta (factura_id, prag, trimis_la, stare) - jurnalul de
    idempotenta per (factura, prag), ca public.alerte_emise la F103. `stare`
    inregistreaza si esecurile (fara_reply_to / fara_email_client) - la fel ca
    limitarea client_id=NULL: se raporteaza in jurnal, nu se reincearca pragul.
  - firma_profil.notificari_scadenta_activ boolean DEFAULT false (opt-in, OPRIT).
  - facturi.notificare_stop boolean DEFAULT false (supapa: nu notifica factura).
  - facturi.notificare_amanata_pana date (supapa: amana pana la data X).
"""
from core import db

# DDL parametrizat pe schema. {s} = numele schemei (validat inainte).
DDL = """
CREATE TABLE IF NOT EXISTS "{s}".notificari_scadenta (
    factura_id integer NOT NULL,
    prag integer NOT NULL,
    trimis_la timestamptz NOT NULL DEFAULT now(),
    stare text NOT NULL DEFAULT 'trimis',
    CONSTRAINT notificari_scadenta_pkey PRIMARY KEY (factura_id, prag)
);
ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS notificari_scadenta_activ boolean NOT NULL DEFAULT false;
ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS notificare_stop boolean NOT NULL DEFAULT false;
ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS notificare_amanata_pana date;
"""


def aplica(conn, schema):
    """Aplica DDL-ul idempotent pe o schema. Ridica daca numele e invalid."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    """True daca schema are TOATE obiectele F131 (tabel + 3 coloane)."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (schema + ".notificari_scadenta",))
        are_tabel = cur.fetchone()[0] is not None
        cur.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND "
            "((table_name='firma_profil' AND column_name='notificari_scadenta_activ') OR "
            " (table_name='facturi' AND column_name IN ('notificare_stop','notificare_amanata_pana')))",
            (schema,))
        nr_coloane = cur.fetchone()[0]
    return are_tabel and nr_coloane == 3


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
    print("Migrare notificari_scadenta: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
