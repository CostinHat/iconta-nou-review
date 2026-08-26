"""
core/migrare_patron_email.py — R65: `patron_email` iese din `coalesce` ȘI din schemă.

Rulare: `python3 -m core.migrare_patron_email`. Idempotent (`DROP COLUMN IF EXISTS`).

DE CE, cu măsurătoarea. `core/pachete_api.py` trimitea pachetul lunar la
`coalesce(patron_email, email)` din `firma_profil` — deci `patron_email` avea **precedență**. Dar
**niciun ecran nu o scria**: `grep` pe tot `static/` întorcea zero, iar ecranul de date ale firmei
are un singur câmp de email, care scrie `email`. Era a doua coloană **cu drum de citire și fără
drum de scriere** găsită pe 26.08.2026, după `tenants.principal_client_id`.

CE O FĂCEA DIFERITĂ, și de-aia a primit restanță proprie (R65, nu R63): la `principal_client_id`,
coloana goală producea un **refuz** — vizibil. Aici, coloana goală produce **comportamentul
corect**, iar completarea ei — dintr-un import, dintr-un seed, dintr-un `UPDATE` manual — ar fi
mutat pachetele **fără ca vreun ecran s-o arate**. Aceeași formă, semne opuse: una se plânge,
cealaltă tace până în ziua în care cineva o completează.

DECIZIA lui Costin: iese din `coalesce`, iar coloana se scoate — nu doar `coalesce`-ul. Motivul,
al lui: *„un al doilea câmp de email pe firmă cere explicat când îl folosești — iar dacă nu se
poate explica în două cuvinte pe ecran, întrebarea nu e a produsului, e a noastră."* Și: R63
tocmai stabilise că există **două** adrese care înseamnă lucruri diferite — cine intră (portal) și
cine primește (firma). `patron_email` ar fi fost a treia, *„și nu știu ce ar însemna"*.

Dacă apare nevoia reală — un patron care vrea pachetul la altă adresă decât cea a firmei — se
construiește **atunci**, cu ecran și cu explicație. Nu se lasă o coloană care așteaptă o nevoie
ipotetică.

MĂSURAT ÎNAINTE, cum a cerut el: **0 din 17** firme o aveau completată. Ștergerea nu pierde nicio
valoare, iar pachetele plecau deja la `email`.

CE NU ATINGE, declarat: `patron_nume`, care stă alături și e la fel de citită de `pachete_api`.
Ea rămâne — apare în corpul pachetului ca nume, nu ca destinație, iar întrebarea dacă ARE cale de
scriere se măsoară separat.
"""
import sys

DDL = "ALTER TABLE %s.firma_profil DROP COLUMN IF EXISTS patron_email;"


def scheme_tenant(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata "
                    "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
        return [r[0] for r in cur.fetchall()]


def aplica(conn, schema):
    with conn.cursor() as cur:
        cur.execute(DDL % schema)


def main():
    sys.path.insert(0, "/home/costin/iconta_nou")
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_tenant(conn)
    facute = 0
    for s in scheme:
        with db.get_conn() as conn:
            aplica(conn, s)
            conn.commit()
        facute += 1
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("""SELECT count(*) FROM information_schema.columns
                       WHERE table_name='firma_profil' AND column_name='patron_email'""")
        ramase = cur.fetchone()[0]
    print("scheme atinse: %d · coloane `patron_email` ramase: %d" % (facute, ramase))
    return 0


if __name__ == "__main__":
    sys.exit(main())
