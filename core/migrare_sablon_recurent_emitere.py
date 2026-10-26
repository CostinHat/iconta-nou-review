"""
core/migrare_sablon_recurent_emitere.py — șablonul facturii recurente cu aceleași întrebări ca „Emite factură” (lotul 13, deficiența 680).

DEFICIENȚA (comanda Costin 13.1, verbatim): „680: Facturi recurente, Șablon nou (nesalvat în probă) | [...] lipsesc seria, scadența,
perioada de valabilitate și, mai ales, dacă factura se emite singură sau ca ciornă și dacă pleacă singură în SPV.” Briefing: „nimic implicit”.

CE FACE: pe `facturi_recurente`, cinci coloane:
  * `scadenta_zile int` — termenul de plată, în zile de la emitere (data scadenței facturii lunii = data emiterii + zilele);
  * `data_inceput date`, `data_sfarsit date` — perioada de valabilitate (sfârșitul gol = „până îl opresc”, ales explicit pe ecran);
  * `mod_emitere text` — „automata” (cronul emite factura) sau „ciorna” (cronul o pregătește și anunță; contabilul o emite din listă);
  * `trimite_spv boolean` — factura emisă automat pleacă singură în SPV (RO e-Factura) sau o trimite contabilul.
DATELE EXISTENTE: șabloanele salvate înainte au fost create cu promisiunea de pe ecran „Șabloane emise automat în fiecare lună” și n-au fost
trimise niciodată în SPV de cron: primesc exact asta, scris (`mod_emitere = 'automata'`, `trimite_spv = false`), nu presupus la fiecare
rulare. Scadența și perioada rămân goale pe ele: factura lunii iese fără scadență (cum ieșea), iar șablonul e valabil până la oprire (cum
era). Facturile emise deja nu se ating. Idempotentă (ADD COLUMN IF NOT EXISTS; UPDATE numai pe rândurile fără mod).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()`.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_sablon_recurent_emitere.py`.
"""
from core import db

MARCAJ_INCEPUT = ("-- [sablon_recurent_emitere_v1, lotul 13, 680] scadența, perioada, modul emiterii și trimiterea în SPV pe șablonul facturii "
                  "recurente — SURSA: core/migrare_sablon_recurent_emitere.py")
MARCAJ_SFARSIT = "-- [sablon_recurent_emitere_v1] sfârșit"
COLOANE = ("scadenta_zile", "data_inceput", "data_sfarsit", "mod_emitere", "trimite_spv", "ultima_pregatire")
MODURI = ("automata", "ciorna")


def sql(s):
    return ("ALTER TABLE %(s)s.facturi_recurente ADD COLUMN IF NOT EXISTS scadenta_zile integer, "
            "ADD COLUMN IF NOT EXISTS data_inceput date, ADD COLUMN IF NOT EXISTS data_sfarsit date, "
            "ADD COLUMN IF NOT EXISTS mod_emitere text, ADD COLUMN IF NOT EXISTS trimite_spv boolean, "
            "ADD COLUMN IF NOT EXISTS ultima_pregatire date;" % {"s": s})


def sql_date(s):
    return ("UPDATE %(s)s.facturi_recurente SET mod_emitere = 'automata', trimite_spv = false WHERE mod_emitere IS NULL;" % {"s": s})


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))
        cur.execute(sql_date('"%s"' % schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = 'facturi_recurente' "
                    "AND column_name = ANY(%s)", (schema, list(COLOANE)))
        if cur.fetchone()[0] != len(COLOANE):
            return False
        cur.execute('SELECT count(*) FROM "%s".facturi_recurente WHERE mod_emitere IS NULL' % schema)
        return cur.fetchone()[0] == 0


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
    print("migrare_sablon_recurent_emitere: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
