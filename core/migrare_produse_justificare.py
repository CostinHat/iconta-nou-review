"""
core/migrare_produse_justificare.py — justificările de cotă deja păstrate, fără numele interne ale programului (lotul 12, deficiența 471).

DEFECTUL (comanda Costin 12.1, 471: „justificarea arată «EXCEPTII_21»”). Potrivirea automată a cotei (`cote_tva.potriveste_cota`) trimite
modelului regula din CF art.291, iar la alimente textul trimis spunea „vezi EXCEPTII_21 (…)” — numele unei constante din cod. Modelul îl
copia în justificare („… se încadrează în EXCEPTII_21 …”), iar justificarea se păstrează în `produse.justificare` și se arată pe rândul
produsului. Promptul spune acum excepțiile cu cuvintele legii (CF art.291 alin.(2) lit.b) pct.1-4), iar răspunsul modelului trece prin
`cote_tva.justificare_afisabila` (niciun nume intern nu mai ajunge pe ecran).

DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): justificările păstrate înainte de reparație
trec prin ACEEAȘI funcție (`justificare_afisabila`, sursa unică) — „EXCEPTII_21” -> „excepțiile de la cota redusă”. Cota, sursa și restul
produsului rămân neatinse. Idempotentă (a doua rulare nu mai găsește nimic de schimbat).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_produse_justificare.py`.
"""
from core import db


def aplica(conn, schema):
    """Rescrie justificările care conțin un nume intern; întoarce câte a schimbat."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import cote_tva as _ct
    n = 0
    with conn.cursor() as cur:
        cur.execute('SELECT to_regclass(%s)', ('"%s".produse' % schema,))
        if cur.fetchone()[0] is None:
            return 0
        cur.execute('SELECT id, justificare FROM "%s".produse WHERE justificare IS NOT NULL ORDER BY id' % schema)
        for pid, j in cur.fetchall():
            nou = _ct.justificare_afisabila(j)
            if nou != j:
                cur.execute('UPDATE "%s".produse SET justificare = %%s WHERE id = %%s' % schema, (nou, pid))
                n += 1
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    total, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                n = aplica(conn, s)
                conn.commit()
            total += n
            if n:
                print("  %s: %d justificări rescrise" % (s, n))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_produse_justificare: %d justificări rescrise, %d esec" % (total, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
