"""
core/migrare_bon_cui_cumparator.py — codul fiscal al cumpărătorului, citit de pe bonul pozat (lotul 17.5-P, AC153; decizii_17_5_P.txt M1).

DE CE. Un bon fiscal ține loc de factură simplificată, deci justifică deducerea TVA, numai dacă poartă codul de înregistrare în scopuri
de TVA al beneficiarului (HG 1/2016 pct. 69 alin. (6); Cod fiscal art. 319 alin. (12) și (21) lit. f). Până acum extragerea AI cerea
numai codul comerciantului, iar bonul se salva fără codul cumpărătorului: aprobarea nu avea ce verifica.

CE FACE. Numai STRUCTURA: coloana `bonuri.cui_cumparator text` — nulabilă, fără valoare implicită, fiindcă NULL înseamnă «necitit» (bon
încărcat înainte de acest lot): bonurile existente rămân NULL, nu devin «fără cod» (șirul gol = citit și absent de pe bon, scris de
`core.uc_portal.portal_bon`). Nicio scriere în datele existente, nicio notă contabilă. Idempotentă (ADD COLUMN IF NOT EXISTS).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (firmele noi; păzit de core/test_bon_cui_cumparator_17_5_P.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_bon_cui_cumparator.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [bon_cui_cumparator_v1, lotul 17.5-P, AC153] codul fiscal al cumpărătorului de pe bon — SURSA: core/migrare_bon_cui_cumparator.py"
MARCAJ_SFARSIT = "-- [bon_cui_cumparator_v1] sfârșit"


def sql(s):
    return "ALTER TABLE %(s)s.bonuri ADD COLUMN IF NOT EXISTS cui_cumparator text;" % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    """Adaugă coloana pe schema dată (fără nicio scriere în date)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))


def verifica(conn, schema):
    """Coloana există, e text, nulabilă și fără valoare implicită."""
    with conn.cursor() as cur:
        cur.execute("SELECT data_type, is_nullable, column_default FROM information_schema.columns WHERE table_schema = %s "
                    "AND table_name = 'bonuri' AND column_name = 'cui_cumparator'", (schema,))
        return cur.fetchone() == ("text", "YES", None)


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
    print("migrare_bon_cui_cumparator: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
