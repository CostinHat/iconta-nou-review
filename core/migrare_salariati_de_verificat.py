"""
core/migrare_salariati_de_verificat.py — `salariati.de_verificat` (text[]): câmpurile salariatului care au intrat la import FĂRĂ
valoare din fișier și așteaptă confirmarea contabilului.

Decizia Costin 14.10.2026 (verbatim în DECIZII „Importul din SAGA — răspunsul la §6 al lotului 1”), pct.3–4: „Persoanele în
întreținere lipsă din fișier: rândul se importă, iar salariatul e marcat vizibil «persoane în întreținere de completat»; calculul
salariului afișează avertismentul până la confirmare.” și „Coloana «Scutit contribuție minimă», absentă din exportul SAGA: rândul nu se
mai refuză. Se importă cu «nescutit» și e marcat «de verificat», la fel ca la 3.”
Valorile: 'persoane_intretinere', 'scutit_contrib_minim'. Se golesc când câmpul se salvează pe salariat
(`salariati_api.actualizeaza_salariat`). Sursa UNICĂ = mirror în tenant_template.sql. Idempotent (ADD COLUMN IF NOT EXISTS).
Se aplică: firmele NOI prin template; cele EXISTENTE prin `python -m core.migrari_registru ruleaza [--productie]
core/migrare_salariati_de_verificat.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".salariati ADD COLUMN IF NOT EXISTS de_verificat text[] NOT NULL DEFAULT '{{}}'::text[];",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='salariati' "
                    "AND column_name='de_verificat'", (schema,))
        return cur.fetchone() is not None


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
    print("migrare_salariati_de_verificat: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
