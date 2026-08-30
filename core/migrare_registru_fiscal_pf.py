"""
core/migrare_registru_fiscal_pf.py — Registrul de evidenta fiscala pentru PERSOANE FIZICE.

SURSA DE ADEVAR a schemei (mirror in `tenant_template.sql`). Idempotent.

DE UNDE VINE. CF art. 68 alin. (8)-(9) + **OMFP 3254/2017**. Registrul se tine **anual**, **pe
fiecare sursa din cadrul fiecarei categorii de venit**, si cuprinde venitul brut si cheltuielile
deductibile din care iese venitul net anual / pierderea neta anuala.

DE CE UN TABEL, si nu o derivare. Constatarea nu e a mea, e scrisa in cod: `core/d212.py`, in
`pull()` — *„D212 e MANUALA pe persoana fizica; firma nu are registru PF."* Adica venitul brut si
cheltuielile deductibile se introduc direct in declaratie si **nu se pastreaza nicaieri**. Ori
tocmai asta e rostul registrului, dupa art. 2 din ordin: sa tina informatiile *care stau la baza*
declaratiei. Fara el, declaratia nu are in spate niciun document care s-o justifice la control.

CE NU FACE MIGRAREA ASTA, declarat: nu rescrie D212 sa citeasca de aici. Registrul exista si tine
datele; alimentarea declaratiei din el e un pas separat, pe un motor de declaratie — nu se face in
aceeasi tura cu nasterea tabelului.

DE CE `rectificare` e o coloana: art. 6 spune ca registrul *„se modifica ori de cate ori se constata
diferente"*, iar modelul din Anexa 1 are un camp „Rectificare". O rectificare care ar suprascrie
randul ar sterge exact istoricul pe care articolul il cere.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS {s}.registru_fiscal_pf (
    id                      BIGSERIAL PRIMARY KEY,
    an                      integer     NOT NULL,
    categorie_venit         text        NOT NULL,
    sursa_venit             text        NOT NULL,
    nr_crt                  integer     NOT NULL,
    venit_brut              numeric(18,2) NOT NULL,
    cheltuieli_deductibile  numeric(18,2) NOT NULL,
    rectificare             boolean     NOT NULL DEFAULT false,
    motiv_rectificare       text,
    creat_la                timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registru_fiscal_pf_ordine_unica UNIQUE (an, categorie_venit, sursa_venit, nr_crt)
)
"""


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        cur.execute(DDL.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.tables "
                    "WHERE table_schema=%s AND table_name='registru_fiscal_pf'", (schema,))
        return cur.fetchone()[0] == 1


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM public.tenants ORDER BY id")
            scheme = [r[0] for r in cur.fetchall()]
    for s in scheme:
        with db.get_conn() as conn:
            aplica(conn, s)
            conn.commit()
            print("%-14s %s" % (s, "OK" if verifica(conn, s) else "LIPSA"))


if __name__ == "__main__":
    _main()
