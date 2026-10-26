"""
core/migrare_coloana_tva_preluat.py — marcajul „TVA de verificat” pe facturile deschise preluate (lotul 13, deficiența 252).

DECIZIA. Comanda Costin 13.1, verbatim: „252: la facturile preluate, dacă fișierul are suma TVA, se ia suma din fișier; doar unde lipsește se
calculează la cota standard, iar factura e marcată «de verificat».” Până acum importul soldurilor pe parteneri calcula TVA-ul neexigibil al
unei facturi preluate cu TVA la încasare MEREU la cota standard (`solduri_parteneri_api.cu_regimul_tva`): o factură cu cotă redusă sau scutită
ieșea cu TVA greșit la încasare (4428 -> 4427, D300, D394), fără ca ceva să o spună.

CE FACE:
1. STRUCTURA: coloana `facturi.tva_de_verificat boolean NOT NULL DEFAULT false` — adevărat pe factura deschisă preluată al cărei TVA
   neexigibil s-a CALCULAT la cota standard (fișierul n-avea suma TVA). Auditul de preluare le numește (`audit_preluare`).
2. DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): facturile deschise preluate înainte de
   reparație cu TVA neexigibil (`tip = 'preluata'`, `tva > 0`) au TVA-ul calculat la cota standard — fișierul de atunci nu putea aduce suma
   (coloana nu exista) —, deci primesc marcajul. Facturile fără TVA neexigibil (regulile generale) rămân nemarcate. Notele, balanța și
   declarațiile depuse nu se ating. Idempotentă (ADD COLUMN IF NOT EXISTS; marcajul numai pe cele nemarcate).
Rulează înaintea lui `migrare_documente_preluate` (ordinea alfabetică a rulatorului, `migrari_registru.in_ordine`): aceea scrie facturile
preluate cu marcajul.
Sursa UNICĂ a structurii: blocul din tenant_template.sql = `bloc_template()` (păzit de core/test_lot13_migr_tva_preluat.py).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_coloana_tva_preluat.py`.
"""
from core import db

MARCAJ_INCEPUT = "-- [tva_preluat_de_verificat_v1, lotul 13, 252] TVA-ul facturii deschise preluate, calculat la cota standard — SURSA: core/migrare_coloana_tva_preluat.py"
MARCAJ_SFARSIT = "-- [tva_preluat_de_verificat_v1] sfârșit"


def sql(s):
    return "ALTER TABLE %(s)s.facturi ADD COLUMN IF NOT EXISTS tva_de_verificat boolean DEFAULT false NOT NULL;" % {"s": s}


def bloc_template():
    return "%s\n%s\n%s" % (MARCAJ_INCEPUT, sql("TENANT_PLACEHOLDER"), MARCAJ_SFARSIT)


def aplica(conn, schema):
    """-> câte facturi preluate existente au primit marcajul."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(sql('"%s"' % schema))
        cur.execute('UPDATE "%s".facturi SET tva_de_verificat = true WHERE tip = %%s AND COALESCE(tva, 0) > 0 AND NOT tva_de_verificat'
                    % schema, ("preluata",))
        return cur.rowcount


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema = %s AND table_name = 'facturi' "
                    "AND column_name = 'tva_de_verificat'", (schema,))
        return cur.fetchone() is not None


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, marcate = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                n = aplica(conn, s)
                conn.commit()
            ok += 1
            marcate += n
            if n:
                print("  %s: %d facturi preluate marcate „TVA de verificat”" % (s, n))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_coloana_tva_preluat: %d ok, %d esec, %d facturi preluate marcate" % (ok, len(esec), marcate))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
