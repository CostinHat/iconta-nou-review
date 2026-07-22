"""
core/migrare_platitor_tva_anaf.py — schema F180 (snapshot ANAF pentru platitor_tva).

Sursa UNICA a DDL-ului (mirror in tenant_template.sql). Idempotent:
ALTER ... ADD COLUMN IF NOT EXISTS. Se aplica pe:
  - tenanti NOI: prin tenant_template.sql (la provisionare);
  - tenanti EXISTENTI: prin `python3 -m core.migrare_platitor_tva_anaf` (comanda
    separata, ruleaza pe TOATE schemele tenant_% si verifica fiecare).

Ce adauga (vezi DECIZII.md 22.07 F180):
  - firma_profil.platitor_tva_anaf boolean  — snapshot al scpTVA de la ANAF v9,
    SEPARAT de coloana editabila manual platitor_tva. NULL = fara snapshot (ANAF
    n-a fost interogat / a fost jos) -> Control fiscal arata GRI, nu rosu.
  - firma_profil.platitor_tva_anaf_data date — data interogarii ANAF (cand a fost
    luat snapshot-ul). Face `limita` onesta ("ANAF poate fi in urma la data X").
Comparatia platitor_tva(local, bool) vs platitor_tva_anaf(scpTVA, bool) e apples-to-
apples: scpTVA e "platitor la data interogarii" (verificat la sursa, apel v9 raw 22.07);
TVA la incasare (tva_la_incasare) si SplitTVA sunt fatete separate, nu se amesteca aici.
"""
from core import db

# DDL parametrizat pe schema. {s} = numele schemei (validat inainte).
DDL = """
ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS platitor_tva_anaf boolean;
ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS platitor_tva_anaf_data date;
"""


def aplica(conn, schema):
    """Aplica DDL-ul idempotent pe o schema. Ridica daca numele e invalid."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    """True daca schema are AMBELE coloane F180 pe firma_profil."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND "
            "table_name='firma_profil' AND column_name IN "
            "('platitor_tva_anaf','platitor_tva_anaf_data')",
            (schema,))
        nr_coloane = cur.fetchone()[0]
    return nr_coloane == 2


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
    print("Migrare platitor_tva_anaf: %d/%d scheme OK%s"
          % (ok, len(scheme), ("; ESUATE: " + ", ".join(esec)) if esec else ""))
    return not esec


if __name__ == "__main__":
    import sys
    sys.exit(0 if _main() else 1)
