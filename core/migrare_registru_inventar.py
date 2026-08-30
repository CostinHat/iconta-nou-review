"""
core/migrare_registru_inventar.py — registrul-inventar (cod 14-1-2), partida dubla.

SURSA DE ADEVAR a schemei (mirror in `tenant_template.sql`). Idempotent.

DE UNDE VINE. **Legea 82/1991, art. 20**: registrele obligatorii sunt Registrul-jurnal,
**Registrul-inventar** si Cartea mare. Continutul e la **OMFP 2634/2015, Anexa 2, cod 14-1-2**, si e
specificat integral acolo: sase coloane, cu ce intra in fiecare.

DE CE UN TABEL, si nu o derivare din balanta. Coloana 3 (*valoarea contabila*) SE DERIVA — e soldul
din balanta. **Coloana 4 (*valoarea de inventar*) NU se deriva din nimic**: norma spune ca registrul
se completeaza *„pe baza datelor cuprinse in listele de inventariere si in procesele-verbale de
inventariere"*, adica pe baza NUMARARII FAPTICE. Aplicatia nu poate sti cate bucati sunt in
magazie. Deci substanta lipseste, ca la registrele art. 321 — nu documentul.

Ce EXISTA azi si nu tine locul: `core/inventariere.py` produce NOTELE CONTABILE care rezulta din
inventariere (plus, minus imputabil/neimputabil, casare), iar `stocuri_cv_api.inventar` primeste
cantitatile faptice **in corpul cererii** si le transforma in miscari — dar nu le PASTREAZA, si le
are doar pentru articole de stoc. Registrul cere toate elementele: imobilizari, creante, datorii,
capitaluri proprii, disponibilitati.

DE CE `diferenta` NU e o coloana stocata: coloana 5 e, prin norma, *diferenta intre valoarea
contabila si valoarea de inventar*. Stocata, ar putea sa le contrazica pe amandoua. Se calculeaza.

DE CE `cauza` e nullable in DDL desi norma o cere: e ceruta **conditionat** — numai cand exista o
diferenta. Un `CHECK` conditionat ar ascunde regula intr-un constrangere greu de citit; sta in
producator, `core/registru_inventar.py`, langa citarea care o justifica.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS {s}.registru_inventar (
    id                 BIGSERIAL PRIMARY KEY,
    exercitiu          integer     NOT NULL,
    momentul           text        NOT NULL
                       CHECK (momentul IN ('inceput_activitate', 'sfarsit_exercitiu',
                                           'incetare_activitate')),
    nr_curent          integer     NOT NULL,
    cont               text        NOT NULL,
    element            text        NOT NULL,
    gestiune           text,
    valoare_contabila  numeric(18,2) NOT NULL,
    valoare_inventar   numeric(18,2) NOT NULL,
    cauza              text,
    data_inventariere  date,
    document           text,
    creat_la           timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registru_inventar_ordine_unica UNIQUE (exercitiu, momentul, nr_curent)
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
                    "WHERE table_schema=%s AND table_name='registru_inventar'", (schema,))
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
