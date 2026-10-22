"""
core/migrare_reevaluare_partener.py — reevaluarea lunară în valută pe PARTENER și ajustarea manuală în același formular (lotul 11,
deficiența 429; decizia Costin din 10.3, verbatim în DECIZII „Comanda 10.3”: „Reevaluarea valutei se face pe soldul în valută al
partenerului, inclusiv plățile nelegate; avansurile intră doar dacă OMFP 1802 pct. 325 le cuprinde, verificat verbatim.”).

Trei coloane noi pe `reevaluari_valuta` (un rând pe element reevaluat, legat de nota generată):
  - `partener` — cheia partenerului (codul fiscal fără RO și spații, altfel „~NUME”) pe creanțele / datoriile reevaluate pe partener;
    NULL pe disponibilități și pe conturile ajustate manual. Rândurile dinainte (pe factură, `factura_id`) rămân cum sunt: propunerea
    le citește în continuare, pe partenerul facturii.
  - `manual` — contul adăugat de contabil la ajustarea manuală (luna următoare revine singur în propunere).
  - `clauza` — creanță / datorie în lei cu clauză valutară: diferența pe 768 / 668 (OMFP 1802/2014 pct.325 alin.(3)).
Temei: OMFP 1802/2014 pct.325 alin.(1)–(3) (reevaluarea lunară la cursul BNR din ultima zi bancară a lunii).

Coloane noi, cu valori implicite: datele existente nu se ating. Sursa UNICĂ a structurii = mirror în tenant_template.sql. Idempotent
(IF NOT EXISTS). Firmele existente: `python -m core.migrari_registru ruleaza [--productie] core/migrare_reevaluare_partener.py`.
"""
from core import db

_DDL = [
    "ALTER TABLE \"{s}\".reevaluari_valuta ADD COLUMN IF NOT EXISTS partener text;",
    "ALTER TABLE \"{s}\".reevaluari_valuta ADD COLUMN IF NOT EXISTS manual boolean NOT NULL DEFAULT false;",
    "ALTER TABLE \"{s}\".reevaluari_valuta ADD COLUMN IF NOT EXISTS clauza boolean NOT NULL DEFAULT false;",
    "CREATE INDEX IF NOT EXISTS reevaluari_valuta_partener ON \"{s}\".reevaluari_valuta (partener, cont, moneda, data);",
]


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        for ddl in _DDL:
            cur.execute(ddl.format(s=schema))


def verifica(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='reevaluari_valuta' "
                    "AND column_name IN ('partener', 'manual', 'clauza')", (schema,))
        return cur.fetchone()[0] == 3


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
            ok += 1
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_reevaluare_partener: %d ok, %d esec" % (ok, len(esec)))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
