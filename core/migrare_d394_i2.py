# -*- coding: utf-8 -*-
"""core/migrare_d394_i2.py — D394 Î2: încasările din activități exceptate de la AMEF (decizia Costin, 03.10.2026).

  · `firma_profil.activitate_exceptata_amef` (boolean, implicit false) + `firma_profil.activitate_amef` (litera din
    OUG 28/1999 art.2, v. core/activitati_amef.py) — „bifa pe profilul firmei (cu activitatea)”;
  · `chitante.cota_tva` (NULL = neclasificată) — „cotă pe chitanță”: D394 Î2 cere baza și TVA pe cote (OPANAF 2194/2025,
    lit.G pct.16–17), iar chitanța purta doar totalul.
Sursa UNICA a DDL-ului (mirror în tenant_template.sql). Idempotent. Se aplică pe ORICE schemă care are tabelele.
`python3 -m core.migrare_d394_i2`.
"""
from core import db

DDL = {
    "firma_profil": [
        'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS activitate_exceptata_amef boolean NOT NULL DEFAULT false;',
        'ALTER TABLE "{s}".firma_profil ADD COLUMN IF NOT EXISTS activitate_amef character varying(2);',
    ],
    "chitante": [
        'ALTER TABLE "{s}".chitante ADD COLUMN IF NOT EXISTS cota_tva numeric(5,2);',
    ],
}


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for tabel, ddl in DDL.items():
            cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name=%s",
                        (schema, tabel))
            if cur.fetchone():
                for d in ddl:
                    cur.execute(d.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND (table_name, column_name) "
                    "IN (('firma_profil','activitate_exceptata_amef'), ('firma_profil','activitate_amef'), "
                    "('chitante','cota_tva'))", (schema,))
        return cur.fetchone()[0]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                        "WHERE table_name IN ('firma_profil','chitante') ORDER BY 1")
            scheme = [r[0] for r in cur.fetchall()]
        ok, esec = 0, []
        for s in scheme:
            try:
                aplica(conn, s)
                conn.commit()
                ok += 1
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare d394_i2: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
