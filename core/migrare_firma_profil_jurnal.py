# -*- coding: utf-8 -*-
"""core/migrare_firma_profil_jurnal.py — jurnalul schimbărilor regimului de TVA al firmei (decizia Costin 04.10.2026).

Decizia: „Regimul de TVA la «Poate pregăti»: confirmat, cu jurnalizarea fiecărei schimbări (utilizator, dată, vechi → nou),
ca la bifa C&D.” Câmpurile: `platitor_tva`, `tip_decont`, `inreg_art317` — cele care schimbă ce declarații de TVA
datorează firma și cum (DECIZII 04.10.2026, PIVOT pe drepturi, consecința 1). Tabelul stă în schema FIRMEI, nu în
`public.audit_log` (acela se șterge după 12 luni, `core/audit_retentie.py`), ca `mijloace_fixe_jurnal`. `user_id` e
obligatoriu: o schimbare fără autor nu e jurnalizată. Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql).
Idempotent. Pe ORICE schemă care are `firma_profil`.
Tenanți NOI prin template; EXISTENȚI prin `python3 -m core.migrare_firma_profil_jurnal`.
"""
from core import db

DDL = ('CREATE TABLE IF NOT EXISTS "{s}".firma_profil_jurnal ('
       ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
       ' camp character varying(40) NOT NULL,'
       ' valoare_veche text,'
       ' valoare_noua text,'
       ' user_id integer NOT NULL,'
       ' la timestamp with time zone NOT NULL DEFAULT now());')


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".firma_profil_jurnal' % schema,))
        return cur.fetchone()[0] is not None


def scheme_cu_tabela(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables "
                    "WHERE table_name='firma_profil' ORDER BY 1")
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
        print("migrare firma_profil_jurnal: %d/%d ok" % (ok, len(scheme)))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
