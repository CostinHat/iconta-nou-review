# -*- coding: utf-8 -*-
"""core/migrare_retest2.py — migrările lotului „Retest 2” (comanda Costin 09.10.2026, verbatim în DECIZII).

  · pct.4  `casa_operatiuni.storno_de` (+ cheia străină și unicitatea): o operațiune de casă cu notă validată nu se șterge, se
           stornează; stornarea poartă legătura spre operațiunea stornată.
  · pct.2  „Notele 121/122 se refac cu descrierea în limbaj de contabil și se retrimit la validare.” Notele de refacere NIR scrise
           de `migrare_retest_0810` purtau în descriere „(decizia Costin 08.10, pct.4)”; descrierea se rescrie cu
           `migrare_retest_0810.descriere_refacere_nir` (sursa unică, aceeași cu care se creează) și nota respinsă se retrimite la
           validare pe drumul aplicației (`coada_api.retrimite_nota`), în numele celui care a pregătit-o, cu notificarea validatorilor.
Sursa UNICĂ (mirror în tenant_template.sql). Idempotentă. `python3 -m core.migrare_retest2`.
"""
from core import db


def _scheme(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        return [r[0] for r in cur.fetchall()]


def casa_storno(conn, schema):
    """True dacă a adăugat coloana; None dacă schema n-are `casa_operatiuni`."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='casa_operatiuni'", (schema,))
        if not cur.fetchone():
            return None
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name='casa_operatiuni' "
                    "AND column_name='storno_de'", (schema,))
        if cur.fetchone():
            return False
        cur.execute('ALTER TABLE "{s}".casa_operatiuni ADD COLUMN storno_de integer'.format(s=schema))
        cur.execute('ALTER TABLE ONLY "{s}".casa_operatiuni ADD CONSTRAINT casa_operatiuni_storno_de_fkey FOREIGN KEY (storno_de) '
                    'REFERENCES "{s}".casa_operatiuni(id)'.format(s=schema))
        cur.execute('CREATE UNIQUE INDEX casa_operatiuni_storno_de_uq ON "{s}".casa_operatiuni (storno_de) WHERE storno_de IS NOT NULL'
                    .format(s=schema))
        return True


def note_refacere_nir(conn, schema, tenant_id, cabinet_id):
    """[(nota_id, descriere_noua, coada_id sau motivul, eticheta elementului)] — notele de refacere NIR cu proveniența internă în descriere (pct.2)."""
    from core import coada_api
    from core.migrare_retest_0810 import descriere_refacere_nir
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='nir'", (schema,))
        if not cur.fetchone():
            return out
        cur.execute('SELECT i.id, n.numar FROM "{s}".inregistrari i JOIN "{s}".nir n '
                    "ON i.numar = 'REFACERE-NIR-' || n.id WHERE i.status = 'ciorna' AND i.descriere LIKE '%%decizia Costin%%' "
                    "ORDER BY i.id".format(s=schema))
        note = cur.fetchall()
        cur.execute('SET LOCAL search_path TO "{s}", public'.format(s=schema))
        for nid, numar in note:
            cur.execute("UPDATE inregistrari SET descriere = %s WHERE id = %s", (descriere_refacere_nir(numar), nid))
            cur.execute("SELECT stare, creat_de_id FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' AND perioada = %s "
                        "ORDER BY id DESC LIMIT 1", (tenant_id, coada_api.perioada_nota(nid)))
            ultim = cur.fetchone()
            if not ultim or ultim[0] != "respinsa":
                out.append((nid, descriere_refacere_nir(numar), "nu se retrimite: %s" % (ultim[0] if ultim else "nu e în coadă"), None))
                continue
            r = coada_api.retrimite_nota(conn, cabinet_id, tenant_id, nid, ultim[1], confirma=True)
            out.append((nid, descriere_refacere_nir(numar), r.get("coada_id") if r.get("ok") else "nereușit: %s" % r.get("mesaj"),
                        r.get("eticheta")))
    return out


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = _scheme(conn)
    n = 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                if casa_storno(conn, s):
                    n += 1
                conn.commit()
        except Exception as e:  # noqa: BLE001
            print("  ESEC", s, e)
    print("pct.4 casa_operatiuni.storno_de: %d / %d scheme" % (n, len(scheme)))
    from core import uc_comun
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, accounting_firm_id FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        firme = cur.fetchall()
    for tid, s, cab in firme:
        with db.get_conn() as conn:
            rez = note_refacere_nir(conn, s, tid, cab)
            conn.commit()
        for nid, desc, coada, eticheta in rez:
            print("pct.2 %s nota %s -> %r; coada: %s" % (s, nid, desc, coada))
            if isinstance(coada, int):
                with db.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT creat_de_id FROM public.declaratii_coada WHERE id = %s", (coada,))
                        uid = cur.fetchone()[0]
                    uc_comun._notif_note_de_validat(conn, cab, [eticheta], uid, tenant_id=tid, coada_id=coada)
                    conn.commit()


if __name__ == "__main__":
    _main()
