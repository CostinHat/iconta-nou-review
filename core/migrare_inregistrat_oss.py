# -*- coding: utf-8 -*-
"""core/migrare_inregistrat_oss.py — `firma_profil.inregistrat_oss` (lotul 13, deficiența 595, decizia Costin 26.10.2026: „6 da” la
propunerea „înregistrarea OSS se întreabă în Date firmă, nu în formularul D398”).

CF art.315 alin.(3): „În cazul în care România este statul membru de înregistrare, persoana impozabilă respectivă trebuie să depună în
format electronic o declarație de începere a activității sale supuse regimului special la organul fiscal competent.” Aplicația nu poate
deduce înregistrarea din codul de TVA (art.317 dă cod, nu și regimul special), deci e un răspuns al firmei: Da / Nu / NULL (nedeclarat —
fără răspuns implicit; D398 nu se generează până nu se răspunde, `d398.refuz_oss`). Sursa UNICĂ a DDL-ului (mirror în
tenant_template.sql). Idempotent. Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_inregistrat_oss` (sau rulatorul
`core.migrari_registru`). Nicio valoare nu se completează din oficiu: firmele existente rămân NULL.
"""
from core import db

DDL = 'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS inregistrat_oss boolean;'


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name='inregistrat_oss'", (schema,))
        return cur.fetchone() is not None


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='firma_profil' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_tabela(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare inregistrat_oss: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
