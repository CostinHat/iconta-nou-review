# -*- coding: utf-8 -*-
"""core/migrare_2b_coloana.py — retragerea coloanei `salariati.salariu_brut` (punctul 4, decizia Costin 03.10.2026).

Decizia: „Ștergi salariati.salariu_brut după ce dovedești că nimic nu o mai citește, cu migrare pe toți tenanții (toate
datele sunt de test) și backup înainte.” Sursa UNICĂ a salariului contractual e `salariu_istoric` (PASUL 2, 29.07.2026);
scrierile au trecut pe istoric în 2b-scrieri, deci coloana rămăsese o copie ÎNVECHITĂ, citită doar de puntea din
`salariu_istoric.salariu_la` pentru salariații fără istoric.

Pe fiecare schemă care încă are coloana, într-o singură tranzacție:
  1. BACKFILL: salariații FĂRĂ niciun rând în `salariu_istoric` primesc unul — `valabil_din` = data angajării, salariul =
     valoarea coloanei (exact ce le dădea puntea). Fără pasul ăsta, scoaterea punții le-ar lăsa salariul gol. Un salariat
     fără data angajării sau fără valoare nu se completează (se raportează, nu se inventează).
  2. `ALTER TABLE salariati DROP COLUMN salariu_brut`.
Idempotent: o schemă fără coloană e sărită. Tenanți NOI: `tenant_template.sql` nu mai are coloana.
"""
from core import db


def are_coloana(cur, schema):
    cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='salariati' "
                "AND column_name='salariu_brut'", (schema,))
    return cur.fetchone() is not None


def aplica(conn, schema):
    """Întoarce {completati, necompletati: [id], scoasa: bool}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        if not are_coloana(cur, schema):
            return {"completati": 0, "necompletati": [], "scoasa": False}
        cur.execute('SELECT to_regclass(%s)', ('"%s".salariu_istoric' % schema,))
        if cur.fetchone()[0] is None:
            raise ValueError("%s: tabela salariu_istoric lipsește — rulează întâi core.migrare_salariu_istoric" % schema)
        cur.execute(f'''SELECT id FROM "{schema}".salariati sa
                        WHERE NOT EXISTS (SELECT 1 FROM "{schema}".salariu_istoric i WHERE i.salariat_id = sa.id)
                          AND (sa.data_angajare IS NULL OR sa.salariu_brut IS NULL)''')
        necompletati = [r[0] for r in cur.fetchall()]
        cur.execute(f'''INSERT INTO "{schema}".salariu_istoric (salariat_id, valabil_din, salariu_brut)
                        SELECT sa.id, sa.data_angajare, sa.salariu_brut FROM "{schema}".salariati sa
                        WHERE NOT EXISTS (SELECT 1 FROM "{schema}".salariu_istoric i WHERE i.salariat_id = sa.id)
                          AND sa.data_angajare IS NOT NULL AND sa.salariu_brut IS NOT NULL''')
        completati = cur.rowcount
        cur.execute(f'ALTER TABLE "{schema}".salariati DROP COLUMN salariu_brut')
    return {"completati": completati, "necompletati": necompletati, "scoasa": True}


def scheme_cu_coloana(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.columns WHERE table_name='salariati' "
                    "AND column_name='salariu_brut' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_coloana(conn)
        ok, esec = 0, []
        for s in scheme:
            try:
                rez = aplica(conn, s)
                conn.commit()
                with conn.cursor() as cur:
                    ramasa = are_coloana(cur, s)
                ok += 0 if ramasa else 1
                print("  %s: istoric completat pentru %d salariați%s; coloana %s" % (
                    s, rez["completati"], (", NECOMPLETAȚI (fără dată/valoare): %s" % rez["necompletati"])
                    if rez["necompletati"] else "", "RĂMASĂ" if ramasa else "scoasă"))
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare 2b-coloana: %d/%d scheme fără coloană" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
