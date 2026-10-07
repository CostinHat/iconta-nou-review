# -*- coding: utf-8 -*-
"""core/migrare_fapte_date_firma.py — două fapte DA/NU din Date firmă fără implicit în schemă (lotul 07.10 B, comanda Costin A.3).

Comanda: „cont_venit_implicit 707 rămâne. Cele două fapte Da/Nu, pe firmele unde nu le-a ales nimeni, se cer o dată la prima
folosire relevantă, ca seria și metoda de stoc; mecanismul îl alegi tu.”

  · `firma_profil.activitate_exceptata_amef` (OUG 28/1999 art.2) — era `NOT NULL DEFAULT false` (core/migrare_d394_i2.py);
  · `firma_profil.inreg_art317` (CF art.317) — era `DEFAULT false NOT NULL` (core/migrare_art317.py).

DDL: implicitul și NOT NULL se scot (NULL = „neales”, ca `metoda_stoc`). DATE: un `false` stocat nu se poate deosebi de
implicitul schemei — ecranul Date firmă venea cu „Nu” ales și îl salva fără ca omul să fi ales — deci devine NULL și se cere
la prima folosire (chitanța fără factură / D394 pentru AMEF; D301 pentru art.317). Rămân: orice `true` (ales explicit — nu
era implicitul) și `inreg_art317 = false` cu o intrare în `firma_profil_jurnal` (o schimbare consemnată = o alegere).
Sursa UNICĂ a DDL-ului (mirror în tenant_template.sql). Idempotent. `python3 -m core.migrare_fapte_date_firma`.
"""
from core import db

DDL = [
    'ALTER TABLE "{s}".firma_profil ALTER COLUMN activitate_exceptata_amef DROP NOT NULL;',
    'ALTER TABLE "{s}".firma_profil ALTER COLUMN activitate_exceptata_amef DROP DEFAULT;',
    'ALTER TABLE "{s}".firma_profil ALTER COLUMN inreg_art317 DROP NOT NULL;',
    'ALTER TABLE "{s}".firma_profil ALTER COLUMN inreg_art317 DROP DEFAULT;',
]

DATE = [
    'UPDATE "{s}".firma_profil SET activitate_exceptata_amef = NULL WHERE activitate_exceptata_amef = false;',
    'UPDATE "{s}".firma_profil SET inreg_art317 = NULL WHERE inreg_art317 = false '
    'AND NOT EXISTS (SELECT 1 FROM "{s}".firma_profil_jurnal j WHERE j.camp = \'inreg_art317\');',
]


def _are(cur, schema, tabel, coloana=None):
    if coloana is None:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name=%s", (schema, tabel))
    else:
        cur.execute("SELECT 1 FROM information_schema.columns WHERE table_schema=%s AND table_name=%s AND column_name=%s",
                    (schema, tabel, coloana))
    return cur.fetchone() is not None


def aplica(conn, schema):
    """Întoarce (nule_amef, nule_art317) — câte rânduri au devenit „neales” (pentru raportul migrării)."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    with conn.cursor() as cur:
        if not (_are(cur, schema, "firma_profil", "activitate_exceptata_amef") and _are(cur, schema, "firma_profil", "inreg_art317")):
            return (0, 0)
        for d in DDL:
            cur.execute(d.format(s=schema))
        cur.execute(DATE[0].format(s=schema))
        n_amef = cur.rowcount
        if _are(cur, schema, "firma_profil_jurnal"):
            cur.execute(DATE[1].format(s=schema))
        else:
            cur.execute('UPDATE "{s}".firma_profil SET inreg_art317 = NULL WHERE inreg_art317 = false;'.format(s=schema))
        return (n_amef, cur.rowcount)


def verifica(conn, schema):
    """True dacă ambele coloane acceptă NULL și n-au implicit."""
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema=%s AND table_name='firma_profil' "
                    "AND column_name IN ('activitate_exceptata_amef', 'inreg_art317') AND is_nullable='YES' "
                    "AND column_default IS NULL", (schema,))
        return cur.fetchone()[0] == 2


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT table_schema FROM information_schema.tables WHERE table_name='firma_profil' ORDER BY 1")
            scheme = [r[0] for r in cur.fetchall()]
        ok, esec, nule = 0, [], [0, 0]
        for s in scheme:
            try:
                a, b = aplica(conn, s)
                conn.commit()
                nule[0] += a
                nule[1] += b
                ok += 1 if verifica(conn, s) else 0
            except Exception as e:  # noqa: BLE001
                conn.rollback()
                esec.append((s, str(e)))
        print("migrare fapte_date_firma: %d/%d ok; neales: amef %d, art317 %d" % (ok, len(scheme), nule[0], nule[1]))
        for s, e in esec:
            print("  ESEC", s, e)


if __name__ == "__main__":
    _main()
