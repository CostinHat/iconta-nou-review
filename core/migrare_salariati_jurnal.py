"""
core/migrare_salariati_jurnal.py — jurnalul corecturii scutirii de contribuția minimă pe fișa salariatului (lotul 12, C133).

DECIZIA (comanda Costin 12.3, pct.8, verbatim în DECIZII): „C133: «Scutit» și «Motiv» se pot corecta, cu jurnal (cine, când, vechi →
nou); motivul e obligatoriu când e bifat «Scutit».” Până acum „Corectează datele” n-avea cele două câmpuri, iar o schimbare a lor (din
„De verificat” sau la reimport) nu lăsa nicio urmă. Acum fiecare schimbare a lui `scutit_contrib_minim` sau `motiv_exceptare` pe o fișă
existentă lasă un rând: câmpul, valoarea de dinainte, cea nouă, cine, când (`salariati_api.jurnalizeaza_scutirea`, singurul loc care scrie).

DE CE UN TABEL AL FIȘEI SALARIATULUI, nu `public.audit_log`: acela se șterge după 12 luni (`core/audit_retentie.py`), iar scutirea intră
în D112 — aceeași alegere ca la `firma_profil_jurnal` (regimul de TVA) și `mijloace_fixe_jurnal` (bifa C&D), aceeași formă (câmp, valoare
veche, valoare nouă, `user_id` obligatoriu, `la`). Nu exista un jurnal al fișei salariatului (căutat: `grep -n "_jurnal" tenant_template.sql`
-> factura_cota_jurnal, firma_profil_jurnal, mijloace_fixe_jurnal, produse_cota_jurnal, registru_jurnal_numere), deci nu e unul paralel.
`ON DELETE CASCADE`: ștergerea unui salariat e permisă numai pentru greșeala de introducere, fără nicio lună declarată
(`salariati_api.sterge_salariat`), iar atunci fișa dispare întreagă.

Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de core/test_lot12_sal3_c133_scutire.py).
Idempotent (CREATE TABLE IF NOT EXISTS).
DATELE EXISTENTE: neafectate — până acum scutirea nu se putea corecta din „Corectează datele”, iar schimbările de dinainte nu au autor
cunoscut; nu se inventează rânduri.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_salariati_jurnal.py`.
"""
from core import db

MARCAJ_INCEPUT = ("-- [salariati_jurnal_v1, lotul 12, C133] corectura scutirii de contribuția minimă pe fișa salariatului, consemnată — "
                  "SURSA: core/migrare_salariati_jurnal.py")
MARCAJ_SFARSIT = "-- [salariati_jurnal_v1] sfârșit"


def sql(s):
    return ("CREATE TABLE IF NOT EXISTS %(s)s.salariati_jurnal (\n"
            "    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,\n"
            "    salariat_id integer NOT NULL REFERENCES %(s)s.salariati(id) ON DELETE CASCADE,\n"
            "    camp character varying(40) NOT NULL,\n"
            "    valoare_veche text,\n"
            "    valoare_noua text,\n"
            "    user_id integer NOT NULL,\n"
            "    la timestamp with time zone NOT NULL DEFAULT now()\n"
            ");") % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schemă invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".salariati_jurnal' % schema,))
        return cur.fetchone()[0] is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                        "WHERE table_name = 'salariati' AND table_schema ~ '^tenant_[0-9]+$' ORDER BY 1")
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
    print("migrare_salariati_jurnal: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
