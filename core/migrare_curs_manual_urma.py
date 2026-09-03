# -*- coding: utf-8 -*-
"""core/migrare_curs_manual_urma.py — CINE si CAND a introdus cursul de mana.

Sursa UNICA a DDL-ului. Idempotent (ADD COLUMN IF NOT EXISTS).
Aplica pe existenti: `python3 -m core.migrare_curs_manual_urma`.

DE CE (R130, decizia lui Costin 04.09.2026). Peste pragul de vechime, emiterea automata se
opreste, iar contabilul poate introduce cursul de mana — *„cu data lui, consemnat cine si cand"*.
Doua din cele trei existau deja: `curs_bnr` poarta valoarea, `curs_sursa='manual'` spune ca n-a
venit de la BNR. Lipseau **autorul** si **momentul** — iar fara ele „manual" e o stare, nu un act:
peste sase luni, la un control, nimeni nu poate spune cine a ales cifra cu care s-a calculat TVA-ul.

  - curs_manual_de   text        — cine a introdus cursul. TEXT, nu `integer`, fiindca sunt DOUA
                                   cai si nu se poate preface ca-s una: din ecran e un utilizator
                                   (`utilizator 1968`), prin API e o cheie de cabinet
                                   (`cheie API a cabinetului 1968`). Un `integer` ar fi trebuit sa
                                   aleaga una dintre ele si sa minta pe cealalta.
  - curs_manual_la   timestamptz — cand.

CE NU FACE: nu atinge `data_curs`, care exista si poarta deja DATA cursului — pe calea manuala e
data pe care o da contabilul, nu data facturii. Corectura aia e in `facturi_api`, nu aici.
"""
from core import db

_DDL = [
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS curs_manual_de text;',
    'ALTER TABLE "{s}".facturi ADD COLUMN IF NOT EXISTS curs_manual_la timestamptz;',
]

_COLOANE = ("curs_manual_de", "curs_manual_la")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s "
                    "AND table_name='facturi' AND column_name = ANY(%s)", (schema, list(_COLOANE)))
        return cur.fetchone()[0] == len(_COLOANE)


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec = 0, []
    for s in scheme:
        try:
            with db.get_conn() as conn:
                aplica(conn, s)
                conn.commit()
            with db.get_conn() as conn:
                if verifica(conn, s):
                    ok += 1
                else:
                    esec.append("%s: coloanele nu sunt acolo dupa aplicare" % s)
        except Exception as e:
            esec.append("%s: %r" % (s, e))
    print("migrare_curs_manual_urma: %d/%d scheme OK" % (ok, len(scheme)))
    for e in esec:
        print("   ESEC", e)
    return 0 if not esec else 2


if __name__ == "__main__":
    raise SystemExit(_main())
