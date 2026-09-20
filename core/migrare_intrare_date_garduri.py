# -*- coding: utf-8 -*-
"""core/migrare_intrare_date_garduri.py — [GARZI cat.1] NOT NULL pe bani + chei naturale UNIQUE.

Categoria 1 din GARZI.md (Intrare date), LIPSA linia 69-70: „gard care cere NOT NULL pe fiecare
coloana de bani si cheie naturala unica pe fiecare tabel de import. Idempotenta importurilor nu e
verificata mecanic." C5 a acoperit doar `extras_import`; asta e sub-lotul 1 al clasei generale.

Decizia Costin (20.09):
- NOT NULL pe categoriile (A) suma de baza cu 0 NULL-uri reale + (B) coloane cu `default 0` (inchide
  gaura inserarii explicite de NULL). Categoria (C) LEGITIM nullable (curs valutar pe RON,
  venituri_6_luni) NU se atinge — ramane in whitelist-ul gardului-ratchet (core/test_intrare_date_garduri).
- Chei naturale UNIQUE pe tabelele de import CURATE. In PostgreSQL, UNIQUE trateaza NULL ca distinct
  => `UNIQUE(cui)`/`UNIQUE(barcode)` = unic pe non-NULL, NULL-uri nelimitate (PF fara CUI, articol fara
  cod scanat). `solduri_parteneri` = (cont, cui) fiindca un cont de control poarta mai multi parteneri.
- EXCLUSE din sub-lotul 1: `produse` (fara camp de cod — decizie de schema deschisa) si `mijloace_fixe`
  (are un duplicat real in tenant_003 — sub-lotul 2, dupa curatare).

Sursa UNICA a DDL-ului = mirror in tenant_template.sql. Idempotent: SET NOT NULL e no-op pe coloana
deja NOT NULL; constrangerile UNIQUE se adauga doar daca lipsesc (verificat in pg_constraint). Se aplica:
tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_intrare_date_garduri`.
"""
from core import db

# (A) 0 NULL-uri reale (suma de baza a inregistrarii) + (B) default 0 (inchide NULL explicit).
# NB (gasit la poarta): NU se pun aici `miscari_stoc.pret_unitar` (miscarea poarta `valoare`, nu pret
# unitar — iesirile/inventarul insereaza fara pret) si `salariati.salariu_brut` (baza poate fi LEGITIM
# LIPSA — semnalata, nu tacuta; GARZI cat.1). Verificarea „0 NULL in date" nu era destula: codul
# insereaza NULL pe cai neexercitate de seed. Ambele -> whitelist in core/test_intrare_date_garduri.
NOT_NULL = [
    ("bonuri", "total"),
    ("bonuri", "tva_11"), ("bonuri", "tva_21"),
    ("concedii_medicale", "baza"), ("concedii_medicale", "brut_ang"),
    ("concedii_medicale", "brut_fnuass"), ("concedii_medicale", "cas"),
    ("concedii_medicale", "cass"), ("concedii_medicale", "impozit"), ("concedii_medicale", "net"),
    ("d301_operatiuni", "tva"), ("plan_conturi", "sold_creditor"),
    ("plan_conturi", "sold_debitor"),
]

# (tabel, nume_constrangere, coloane) — chei naturale CURATE. NULL distinct in PG => non-NULL unic.
UNIQUE = [
    ("efactura_primite", "efactura_primite_msg_uniq", "id_mesaj_anaf"),
    ("solduri_initiale", "solduri_initiale_cont_uniq", "cont"),
    ("solduri_parteneri", "solduri_parteneri_cont_cui_uniq", "cont, cui"),
    ("asociati", "asociati_cnp_uniq", "cnp"),
    ("clienti", "clienti_cui_uniq", "cui"),
    ("furnizori", "furnizori_cui_uniq", "cui"),
    ("state_plata", "state_plata_sal_luna_ex_uniq", "salariat_id, luna, exemplar"),
    ("articole", "articole_barcode_uniq", "barcode"),
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for tab, col in NOT_NULL:
            cur.execute(f'ALTER TABLE "{schema}".{tab} ALTER COLUMN {col} SET NOT NULL')
        for tab, nume, cols in UNIQUE:
            # idempotent: adauga constrangerea doar daca nu exista deja in schema
            cur.execute("""SELECT 1 FROM pg_constraint con
                           JOIN pg_namespace n ON n.oid=con.connamespace
                           WHERE n.nspname=%s AND con.conname=%s""", (schema, nume))
            if not cur.fetchone():
                cur.execute(f'ALTER TABLE "{schema}".{tab} ADD CONSTRAINT {nume} UNIQUE ({cols})')
    conn.commit()


def toate_schemele(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name LIKE 'tenant_%' ORDER BY 1")
        return [r[0] for r in cur.fetchall()]


def main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = toate_schemele(conn)
        for s in scheme:
            aplica(conn, s)
        print("intrare_date_garduri aplicat pe %d scheme: %s" % (len(scheme), ", ".join(scheme)))


if __name__ == "__main__":
    main()
