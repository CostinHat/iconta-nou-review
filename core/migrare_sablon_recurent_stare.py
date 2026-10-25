"""
core/migrare_sablon_recurent_stare.py — starea ultimei emiteri și categoria produsului pe șablonul facturii recurente (lotul 12, comanda
Costin 12.3 pct.1 și pct.9).

DECIZIA (comanda 12.3, verbatim): pct.1 „C109: refuzul cronului ajunge la contabil prin notificare (clopoțel și email); pe șablon se vede și
starea ultimei emiteri.”; pct.9 „Da: cota și categoria pe linia șablonului recurent, ca la factură.”

DEFECTUL (C109). Un șablon refuzat la emiterea automată nu emitea nimic, iar refuzul rămânea numai în jurnalul jobului: pe șablon se vedea
doar data ultimei facturi emise, deci nimic nu spunea că factura lunii n-a plecat. Starea refuzului nu se poate deduce din ce există
(`ultima_emitere` e data ultimei facturi; notificările sunt ale fiecărui om și nu există la o firmă fără destinatari), deci se ține pe șablon.
pct.9: cota și categoria liniei stau în `linii` (jsonb, ca până acum cota); categoria PRODUSULUI la taxarea inversă (art.331, codul din D394)
e a documentului, ca la „Emite factură” (`facturi.categorie_331`), deci are coloana ei.

CE FACE: pe `facturi_recurente`, trei coloane fără valoare implicită:
  * `ultimul_refuz text` — motivul ultimului refuz al emiterii automate (golit la emiterea reușită);
  * `ultimul_refuz_la date` — ziua lui (aceeași unitate ca `ultima_emitere`);
  * `categorie_331 text` — categoria produsului cu taxare inversă (codul D394), aceeași ca `facturi.categorie_331`.
DATELE EXISTENTE: un șablon salvat înainte rămâne cu cele trei NULL — „niciun refuz consemnat”, adevărat: refuzurile de dinainte n-au fost
păstrate nicăieri în afara jurnalului jobului, iar următoarea rulare a cronului le consemnează (și le anunță) dacă se repetă. Liniile vechi
fără categorie: la plătitor, linia cu 0% fără categorie e refuzată la emitere ca la „Emite factură” (`categorii_tva.verifica_linii`) — acum
refuzul ajunge la contabil; clientul din alt stat cu o linie fără cotă rămâne refuzat (`facturi_recurente.verificari_drum`). Nimic nu se
ghicește pe datele vechi. Facturile emise deja din șabloane nu se ating. Idempotentă (ADD COLUMN IF NOT EXISTS).
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de core/test_lot12_fe3_recurente.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_sablon_recurent_stare.py`.
"""
from core import db

MARCAJ_INCEPUT = ("-- [sablon_recurent_stare_v1, lotul 12, C109 + 12.3 pct.9] starea ultimei emiteri și categoria produsului pe șablonul "
                  "facturii recurente — SURSA: core/migrare_sablon_recurent_stare.py")
MARCAJ_SFARSIT = "-- [sablon_recurent_stare_v1] sfârșit"
COLOANE = ("ultimul_refuz", "ultimul_refuz_la", "categorie_331")


def sql(s):
    return ("ALTER TABLE %(s)s.facturi_recurente ADD COLUMN IF NOT EXISTS ultimul_refuz text, "
            "ADD COLUMN IF NOT EXISTS ultimul_refuz_la date, ADD COLUMN IF NOT EXISTS categorie_331 text;" % {"s": s})


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = 'facturi_recurente' "
                    "AND column_name = ANY(%s)", (schema, list(COLOANE)))
        return cur.fetchone()[0] == len(COLOANE)


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
    print("migrare_sablon_recurent_stare: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
