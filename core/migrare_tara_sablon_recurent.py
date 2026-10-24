"""
core/migrare_tara_sablon_recurent.py — țara clientului pe șablonul facturii recurente (lotul 12, deficiența C160).

DEFECTUL. Șablonul facturii recurente (`facturi_recurente`) nu ținea țara clientului, iar emiterea lui (`facturi_recurente._proba_emiterii`
la salvare, `emite_scadente` la cron) chema `facturi_api.emite_factura` cu implicitul `tert_tara="RO"`: o factură lunară către un client
din alt stat membru ieșea ca o vânzare în România — la neplătitorul înregistrat art.317 fără axa „servicii” (`categorii_tva.axa_neplatitor`
cere țara), deci în D390 ca livrare de bunuri (L), nu ca prestare (P); la plătitor, categoriile intracomunitare ale liniilor (livrare
intracomunitară, prestare cu locul în afara României) se refuzau față de țara „RO”. Reparat în cod: șablonul poartă țara clientului, aleasă
pe ecran (dedusă din codul fiscal, ca la „Emite factură”), de la salvare până la emitere.
TEMEI: CF art.325 alin.(1) lit.a și c (D390: livrările intracomunitare de bunuri și prestările art.278 alin.(2) către persoane impozabile
stabilite în alt stat membru); CF art.278 alin.(2) (locul prestării, la beneficiarul persoană impozabilă).

CE FACE: coloana `facturi_recurente.tert_tara text NOT NULL DEFAULT 'RO'` (același tip și același implicit ca `facturi.tert_tara`).
DATELE EXISTENTE: un șablon salvat înainte primește „RO” — țara pe care o lua deja la emitere, deci nimic nu se schimbă pentru el: de la
462 un cod fiscal cu prefixul altui stat nu se putea salva, iar unul vechi cu un asemenea cod e refuzat și acum la cron, până se alege țara
(`facturi_recurente.verificari_drum`). Facturile emise deja din șabloane nu se ating. Idempotentă (ADD COLUMN IF NOT EXISTS).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de core/test_lot12_c160_c162_tara_axa.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_tara_sablon_recurent.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [tara_sablon_recurent_v1, lotul 12, C160] țara clientului pe șablonul facturii recurente — SURSA: core/migrare_tara_sablon_recurent.py"
MARCAJ_SFARSIT = "-- [tara_sablon_recurent_v1] sfârșit"


def sql(s):
    return "ALTER TABLE %(s)s.facturi_recurente ADD COLUMN IF NOT EXISTS tert_tara text DEFAULT 'RO'::text NOT NULL;" % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = 'facturi_recurente' "
                    "AND column_name = 'tert_tara'", (schema,))
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
    print("migrare_tara_sablon_recurent: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
