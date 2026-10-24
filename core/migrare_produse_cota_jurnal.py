"""
core/migrare_produse_cota_jurnal.py — jurnalul corecturii cotei TVA a unui produs din nomenclator (lotul 12, deficiența 472).

DEFECTUL (comanda Costin 12.1, 472: „Cota TVA salvată nu se mai poate corecta”). Ecranul Produse spunea „O poți corecta oricând”, dar pe
rândul unui produs salvat stătea numai „Șterge”: cota greșită rămânea, iar factura o lua de acolo. Corectura se face acum pe rând
(`PUT /produse/{id}`, `produse_api.actualizeaza`) și, ca la cota de pe linia facturii (deficiența 21, decizia Costin 05.10.2026:
„contabilul poate corecta cota; schimbarea rămâne consemnată (propus → ales, cine, când)”), rămâne CONSEMNATĂ: un rând pe fiecare
schimbare a cotei (sau a categoriei cotei 0%) — cota și categoria de dinainte, cele noi, cine, când.

Tabelul stă în schema FIRMEI (ca `factura_cota_jurnal`), fără legătură cu `produse`: un produs șters nu-și șterge istoria cotei (de aceea
și denumirea se păstrează în rând). Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de
core/test_lot12_prod_produse.py). Idempotent (CREATE TABLE IF NOT EXISTS).
DATELE EXISTENTE: neafectate — nicio cotă nu s-a putut corecta până acum, deci n-are ce consemna.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_produse_cota_jurnal.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [produse_cota_jurnal_v1, lotul 12, 472] corectura cotei TVA a produsului, consemnată — SURSA: core/migrare_produse_cota_jurnal.py"
MARCAJ_SFARSIT = "-- [produse_cota_jurnal_v1] sfârșit"


def sql(s):
    return ("CREATE TABLE IF NOT EXISTS %(s)s.produse_cota_jurnal (\n"
            "    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n"
            "    produs_id integer NOT NULL,\n"
            "    denumire text NOT NULL,\n"
            "    cota_veche numeric(5,2),\n"
            "    categorie_veche text,\n"
            "    cota_noua numeric(5,2) NOT NULL,\n"
            "    categorie_noua text,\n"
            "    user_id integer NOT NULL,\n"
            "    la timestamp with time zone NOT NULL DEFAULT now()\n"
            ");") % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".produse_cota_jurnal' % schema,))
        return cur.fetchone()[0] is not None


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
    print("migrare_produse_cota_jurnal: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
