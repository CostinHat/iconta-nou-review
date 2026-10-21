"""
core/migrare_borderou_numar_unic.py — numărul borderoului de achiziție e unic în anul lui (lotul 10, deficiența 434, comanda Costin 10.2
pct.4, verbatim: „la F1, borderoul de achiziție nou (Maria Ionescu, 20.10) a primit numărul BA-1, deși BA-1 există deja (Ion Popescu,
19.10). Numerotarea borderourilor e unică și continuă.”).

Aplicația continuă numerotarea după cel mai mare borderou al anului și refuză un număr scris de mână care e deja al altui borderou
(`documente_interne.cel_mai_mare` / `borderou_cu_numarul`, `uc_tenants.achizitie_neinregistrat`). Indexul unic face dublura IMPOSIBILĂ
și pe orice alt drum (alt ecran, un import, o scriere directă): aceeași formă ca verificarea din aplicație — `upper(btrim(numar))` și
anul datei, numai pe `facturi.tip = 'borderou'`.

Datele existente NU se schimbă: dacă o firmă are deja doi borderouri cu același număr în același an, migrarea NU renumerotează (numărul e
al documentului, schimbarea lui e o corectură a contabilului) — se oprește pe firma aceea și le numește; după corectarea numărului, se
rulează din nou. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent (IF NOT EXISTS).
Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_borderou_numar_unic.py`.
"""
from core import db

_INDEX = ("CREATE UNIQUE INDEX IF NOT EXISTS facturi_borderou_numar_an_uniq ON \"{s}\".facturi "
          "(upper(btrim(numar)), (EXTRACT(YEAR FROM data_emitere))) WHERE tip = 'borderou';")


def dubluri(conn, schema):
    """Borderourile care au deja același număr în același an: [(numărul, anul, [(data, vânzătorul)])]."""
    with conn.cursor() as cur:
        cur.execute("SELECT upper(btrim(numar)), EXTRACT(YEAR FROM data_emitere)::int, "
                    "array_agg(to_char(data_emitere, 'DD.MM.YYYY') || ' ' || COALESCE(tert_nume, '') ORDER BY id) "
                    "FROM \"{s}\".facturi WHERE tip = 'borderou' GROUP BY 1, 2 HAVING count(*) > 1 ORDER BY 2, 1".format(s=schema))
        return [(r[0], r[1], list(r[2])) for r in cur.fetchall()]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    d = dubluri(conn, schema)
    if d:
        raise ValueError("borderouri cu același număr în același an (se corectează numărul unuia, apoi se rulează din nou): " + "; ".join(
            "%s / %s: %s" % (nr, an, ", ".join(x)) for nr, an, x in d))
    with conn.cursor() as cur:
        cur.execute(_INDEX.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname = %s AND indexname = 'facturi_borderou_numar_an_uniq'", (schema,))
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
    print("migrare_borderou_numar_unic: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
