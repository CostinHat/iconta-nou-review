"""
core/migrare_registre_art321.py — cele DOUĂ registre cerute de art. 321 alin. (4) din Codul fiscal.

SURSA DE ADEVĂR a schemei (mirror în `tenant_template.sql`). Idempotent.

DE UNDE VINE. Art. 321 alin. (1)-(3) cere „evidențe corecte și complete", iar **alin. (4) trimite
conținutul la normele metodologice** și numește acolo, expres, două registre. HG 1/2016, normele la
art. 321:

  - **lit. e) — registrul nontransferurilor**: bunuri transportate de persoana impozabilă (sau de
    altcineva în contul ei) în afara României, dar în interiorul Comunității, pentru operațiunile de
    la art. 270 alin. (12) lit. f)-h) CF;
  - **lit. f) — registrul bunurilor primite**: bunuri mobile corporale primite din alt stat membru
    (sau importate/achiziționate în RO de o persoană nestabilită) **în scopul evaluării sau pentru
    lucrări** efectuate asupra lor în România.

DE CE UN SINGUR TABEL, cu discriminator. Cele două liste de câmpuri din normă sunt **oglinzi**:
una pornește de la *primitor*, cealaltă de la *expeditor*; amândouă au număr de ordine, dată de
transport, descriere, cantitate, un picior de **retur după lucrări**, și mențiunea documentelor.
Două tabele identice ar fi cerut două seturi de gărzi pentru aceeași formă.

DE CE `valoare` E NULLABLE, și nu e o scăpare: lit. e) cere expres *„valoarea bunurilor
transportate"*; **lit. f) NU cere o valoare**. Constrângerea nu se pune în DDL (ar fi un `CHECK`
condiționat, greu de citit), ci în producător — `core/registre_art321.py`, `CAMPURI_CERUTE` — ca să
poată purta citarea alături de regulă.
"""
from core import db

DDL = """
CREATE TABLE IF NOT EXISTS {s}.registre_art321 (
    id                     BIGSERIAL PRIMARY KEY,
    fel                    text        NOT NULL
                           CHECK (fel IN ('nontransfer', 'bunuri_primite')),
    nr_ordine              integer     NOT NULL,
    partener_denumire      text        NOT NULL,
    partener_adresa        text        NOT NULL,
    data_transport         date        NOT NULL,
    descriere              text        NOT NULL,
    cantitate              numeric(18,3) NOT NULL,
    valoare                numeric(18,2),
    data_retur             date,
    descriere_returnate    text,
    cantitate_returnate    numeric(18,3),
    descriere_nereturnate  text,
    cantitate_nereturnate  numeric(18,3),
    documente              text,
    data_documente         date,
    creat_la               timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT registre_art321_ordine_unica UNIQUE (fel, nr_ordine)
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
                    "WHERE table_schema=%s AND table_name='registre_art321'", (schema,))
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
