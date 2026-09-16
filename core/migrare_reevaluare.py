# -*- coding: utf-8 -*-
"""core/migrare_reevaluare.py — reevaluarea ca OBIECT, si efectul ei pe registrul mijloacelor fixe.

DE CE (R59, criteriul largit de Costin pe 16.09.2026, INAINTE de reparatie). Ruta
`POST /tenants/{id}/reevaluare-imobilizare` citea valoarea si amortizarea din `mijloace_fixe`,
scria o nota CIORNA (`2813=2131` eliminarea amortizarii, `2131=105` diferenta) si **nu atingea
registrul**. Deci dupa o reevaluare: evidenta contabila spunea o valoare, registrul alta, iar
D406/SAF-T declara `AcquisitionAndProductionCostsEnd` pe cea VECHE. Masurat pe 16.09 (etapa 2,
lotul I, lantul 7): activ 3.000 lei reevaluat la 3.500, ruta a raspuns `200`, registrul a ramas pe
3.000, declaratia a declarat 3.000.

CRITERIUL DE INCHIDERE, verbatim: *inchiderea cere DOUA cifre — (1) coloana din registru urca la
valoarea reevaluata, si (2) `AcquisitionAndProductionCostsEnd` din Assets o declara.*

CE ADAUGA MIGRAREA ASTA, si de ce nu ajunge o coloana:

  - tabelul `reevaluari` — **reevaluarea ca fapt cu atribute**, nu ca sir intr-o descriere:
    ce activ, ce nota, ce valoare bruta avea, ce amortizare s-a eliminat, ce valoare justa s-a
    stabilit, si CAND s-a aplicat pe registru (`aplicata_la`).

DE CE `aplicata_la` E NULLABLE, si e miezul: ruta produce o **CIORNA**. Efectul pe registru se
produce la **validarea notei** — varianta (a) din conditia de deblocare a lui R59 —, nu la scrierea
ciornei. Cele doua stari (consemnata / aplicata) sunt exact deosebirea dintre o propunere si
evidenta, iar o coloana `boolean` ar fi spus mai putin: aici se stie si MOMENTUL.

DE CE NU EXISTA O COLOANA `data_reevaluare` PE `mijloace_fixe`, desi motorul are nevoie de ea:
ar fi a doua definitie a aceluiasi fapt. `mijloace_fixe.valoare` poarta valoarea bruta CURENTA
(cifra 1 din criteriu), iar tot ce trebuie ca sa se reconstituie amortizarea peste reevaluare sta in
`reevaluari`. Interogarile din `core/repo_mijloace_fixe.py` aduc randurile APLICATE odata cu
activul, ca niciun apelant sa nu poata construi un mijloc fix "fara reevaluari" din uitare.

NU SE FACE BACKFILL, si nu e o scapare: pe toate cele 17 scheme exista **zero** note de reevaluare
(masurat la deschiderea lui R59, 26.08.2026). Nu exista istorie de reconstituit, iar un rand fabricat
ar fi o afirmatie despre un act care nu s-a intamplat.

Sursa UNICA a DDL-ului = oglinda in `tenant_template.sql`. Idempotent (IF NOT EXISTS). Se aplica:
tenanti NOI prin template; EXISTENTI prin `python3 -m core.migrare_reevaluare`.
"""
import sys

from core import db

_DDL = [
    # Reevaluarea, ca obiect. `inregistrare_id` e nota (ciorna la nastere); `aplicata_la` e
    # momentul in care efectul a intrat pe registru, la validarea ei.
    'CREATE TABLE IF NOT EXISTS "{s}".reevaluari ('
    ' id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,'
    ' inregistrare_id integer NOT NULL,'
    ' mijloc_fix_id integer NOT NULL,'
    ' data date NOT NULL,'
    ' valoare_bruta_veche numeric NOT NULL,'
    ' amortizare_eliminata numeric NOT NULL,'
    ' valoare_justa numeric NOT NULL,'
    ' aplicata_la timestamptz,'
    ' creat_la timestamptz NOT NULL DEFAULT now()'
    ');',
    # O nota = cel mult o reevaluare. Poarta e in BAZA, nu doar in cod: validarea notei se poate
    # cere de doua ori (retry, doua file deschise), iar a doua aplicare ar urca valoarea inca o data.
    'CREATE UNIQUE INDEX IF NOT EXISTS reevaluari_nota_unic'
    ' ON "{s}".reevaluari (inregistrare_id);',
    'CREATE INDEX IF NOT EXISTS reevaluari_mijloc_idx'
    ' ON "{s}".reevaluari (mijloc_fix_id, data);',
]

_INDECSI = ("reevaluari_nota_unic", "reevaluari_mijloc_idx")


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    """Tabelul EXISTA si poarta AMANDOI indecsii — nu doar primul."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", ('"%s".reevaluari' % schema,))
        tab = cur.fetchone()[0] is not None
        cur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname=%s "
                    "AND indexname = ANY(%s)", (schema, list(_INDECSI)))
        idx = cur.fetchone()[0] == len(_INDECSI)
    return tab and idx


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
                    esec.append((s, "verificarea a picat dupa aplicare"))
        except Exception as e:  # noqa: BLE001
            esec.append((s, "%s: %s" % (type(e).__name__, e)))
    print("scheme: %d · aplicat+verificat: %d · esec: %d" % (len(scheme), ok, len(esec)))
    for s, m in esec:
        print("  ESEC %s — %s" % (s, m))
    return 1 if esec else 0


if __name__ == "__main__":
    sys.exit(_main())
