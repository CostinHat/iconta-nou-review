"""
core/migrare_tva_incasare_perioade.py — perioadele în care firma aplică sistemul TVA la încasare (deficiența 428, comanda Costin 10.1, verbatim în
DECIZII „Comanda 10.1”): „Construiește regimul pe firmă, cu data de la care se aplică și verificarea în registrul ANAF”. Temei: CF art.282
alin.(3) (exigibilitatea la încasare, „persoane care aplică sistemul TVA la încasare”), alin.(3^1) (data de la care se aplică), alin.(5)
(renunțarea / ieșirea, de la prima zi a perioadei fiscale următoare), alin.(7) (facturile emise înainte de ieșire rămân în sistem).
`de_la` = prima zi în care se aplică; `pana_la` = ultima zi (NULL = se aplică în continuare). `verificat_anaf_la` / `stare_anaf` =
ultima verificare în Registrul persoanelor care aplică sistemul TVA la încasare (RTVAI). `firma_profil.tva_la_incasare` rămâne
indicatorul „aplică azi”, sincronizat din perioade.

Coloane / tabele noi, goale: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_tva_incasare_perioade.py`.
"""
from core import db

_DDL = [
    "CREATE TABLE IF NOT EXISTS \"{s}\".tva_incasare_perioade (id serial PRIMARY KEY, de_la date NOT NULL, pana_la date, "
    "sursa text NOT NULL DEFAULT 'manual' CHECK (sursa IN ('manual', 'anaf')), verificat_anaf_la timestamptz, stare_anaf text, "
    "creat_la timestamptz NOT NULL DEFAULT now(), CHECK (pana_la IS NULL OR pana_la >= de_la));",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema=%s AND table_name='tva_incasare_perioade'", (schema,))
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
    print("migrare_tva_incasare_perioade: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
