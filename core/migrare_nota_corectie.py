# -*- coding: utf-8 -*-
"""core/migrare_nota_corectie.py — reparația pe date a neconformității din 09.10.2026 (DECIZII: „Neconformitate: nota de corecție
respinsă stornează stocul documentului contat”; aprobarea, verbatim, în „Comanda Costin … registrul deficiențelor”, pct.1:
„aprob ștergerea rândurilor 8 și 9 din miscari_stoc (mișcări de sistem fără notă contabilă), cu backup înainte și rândurile tipărite
integral în jurnal. Apoi retrimite notele 121 și 122 la validare, cu descrierea în limbaj de contabil.”).

  · `stornari_gresite` — stornările scrise la respingere peste o mișcare ÎN EVIDENȚĂ (`stocuri_anulare.IN_EVIDENTA`, aceeași
    definiție care oprește acum stornarea) se scot; fiecare rând se întoarce întreg, ca să fie tipărit în jurnalul rulării.
  · `retrimite_refaceri` — notele de refacere NIR (`REFACERE-NIR-<id>`) încă în ciornă, a căror ultimă respingere a fost pentru
    descriere (proveniența internă „decizia Costin” — în descriere sau în motivul respingerii), primesc descrierea în limbaj de
    contabil (`migrare_retest_0810.descriere_refacere_nir`, sursa unică) și se retrimit pe drumul butonului (`coada_api.retrimite_nota`).
    O notă respinsă pentru alt motiv NU se atinge: acolo cel care a pregătit-o are de corectat ceva.
Idempotentă (a doua rulare nu mai găsește nici stornări greșite, nici note respinse). Fiecare schemă se comite separat; rularea se
scrie în registrul migrărilor rulând-o prin `python -m core.migrari_registru ruleaza --productie core/migrare_nota_corectie.py`.
"""
from psycopg2.extras import RealDictCursor

from core import db


def stornari_gresite(conn, schema):
    """[rând întreg de stornare scos (dict)] — stornările de la respingere peste o mișcare în evidență. Scrie în tranzacția `conn`."""
    from core.stocuri_anulare import IN_EVIDENTA
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    s = '"%s"' % schema
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='miscari_stoc'", (schema,))
        if not cur.fetchone():
            return []
        cur.execute(("SELECT r.* FROM {s}.miscari_stoc r JOIN {s}.miscari_stoc m ON m.id = r.anuleaza_id WHERE " + IN_EVIDENTA
                     + " ORDER BY r.id").format(s=s))
        gresite = [dict(r) for r in cur.fetchall()]
        if gresite:
            cur.execute("DELETE FROM {s}.miscari_stoc WHERE id = ANY(%s)".format(s=s), ([r["id"] for r in gresite],))
    return gresite


def retrimite_refaceri(conn, schema, tenant_id, cabinet_id):
    """[(nota_id, descriere, coada_id sau motivul, eticheta)] — notele de refacere NIR respinse pentru descriere, retrimise."""
    from core import coada_api
    from core.migrare_retest_0810 import descriere_refacere_nir
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    s = '"%s"' % schema
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM information_schema.tables WHERE table_schema=%s AND table_name='nir'", (schema,))
        if not cur.fetchone():
            return out
        cur.execute("SELECT i.id, n.numar, i.descriere FROM {s}.inregistrari i JOIN {s}.nir n ON i.numar = 'REFACERE-NIR-' || n.id "
                    "WHERE i.status = 'ciorna' ORDER BY i.id".format(s=s))
        note = cur.fetchall()
        cur.execute('SET LOCAL search_path TO {s}, public'.format(s=s))
        for nid, numar, descriere in note:
            cur.execute("SELECT stare, creat_de_id, motiv_respingere FROM public.declaratii_coada WHERE tenant_id = %s AND fel = 'nota' "
                        "AND perioada = %s ORDER BY id DESC LIMIT 1", (tenant_id, coada_api.perioada_nota(nid)))
            ultim = cur.fetchone()
            if not ultim or ultim[0] != "respinsa":
                continue
            if "decizia Costin" not in (descriere or "") and "decizia Costin" not in (ultim[2] or ""):
                continue                     # respinsă pentru altceva: o corectează cine a pregătit-o, nu migrarea
            noua = descriere_refacere_nir(numar)
            cur.execute("UPDATE inregistrari SET descriere = %s WHERE id = %s", (noua, nid))
            r = coada_api.retrimite_nota(conn, cabinet_id, tenant_id, nid, ultim[1], confirma=True)
            out.append((nid, noua, r.get("coada_id") if r.get("ok") else "nereușit: %s" % r.get("mesaj"), r.get("eticheta")))
    return out


def _main():
    from core import uc_comun
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, schema_name, accounting_firm_id FROM public.tenants WHERE schema_name IS NOT NULL ORDER BY id")
        firme = cur.fetchall()
    for tid, s, cab in firme:
        with db.get_conn() as conn:
            scoase = stornari_gresite(conn, s)
            conn.commit()
        for r in scoase:
            print("stornare scoasă %s: %s" % (s, {k: (str(v) if v is not None else None) for k, v in r.items()}))
    for tid, s, cab in firme:
        with db.get_conn() as conn:
            rez = retrimite_refaceri(conn, s, tid, cab)
            conn.commit()
        for nid, desc, coada, eticheta in rez:
            print("%s nota %s -> %r; coada: %s" % (s, nid, desc, coada))
            if isinstance(coada, int):
                with db.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT creat_de_id FROM public.declaratii_coada WHERE id = %s", (coada,))
                        uid = cur.fetchone()[0]
                    uc_comun._notif_note_de_validat(conn, cab, [eticheta], uid, tenant_id=tid, coada_id=coada)
                    conn.commit()


if __name__ == "__main__":
    _main()
