# -*- coding: utf-8 -*-
"""scripts/stoc2_619_documente_pe_jumatate.py — datele existente ale deficienței 619 (lotul 12, comanda Costin 12.2 pct.10, verbatim în
DECIZII „Comanda 12.2”): „la F1A nr. 8 și F1A nr. 14 validarea contării lasă ieșirea de stoc în ciornă”; „stornarea/returul (−27,50) s-a
validat înaintea documentului stornat, aflat în ciornă, deci 607 e negativ în evidența validată”.

Ce rămâne după reparația din cod (`coada_api.valideaza_documentul`: un document se validează cu toate notele lui, iar stornarea numai după
documentul stornat): documentele validate PE JUMĂTATE înainte de ea — o notă validată (pe drumul vechi, o singură notă), alta ciornă.
Regula de acum spune că documentul se validează o dată, cu toate notele lui; documentul pe jumătate se COMPLETEAZĂ, pe drumul validării
(`valideaza_documentul`, cu toate regulile ei: documentul justificativ, ciorna depășită, casa sub zero, perioada închisă). Documentul
stornat înaintea stornării lui. O notă refuzată rămâne ciornă și se numără pe felul refuzului. Nimic nu se șterge, nimic nu se rescrie.

Nu e o migrare: o migrare schimbă schema, iar notele se ating numai pe drumul validării
(`core/test_migrari_registru.py::test_nicio_migrare_noua_nu_scrie_in_notele_contabile`) — ca `scripts/valideaza_note_interne_pfa.py`.
Scrie în notele contabile: se rulează NUMAI cu aprobarea lui Costin (regimul pilot), după backup, pe schemele numite.
Ieșirea: numărători (documente, note validate, refuzuri pe cod) — fără nume de firmă, fără date, sume sau etichete de note.
Uz: ./venv/bin/python scripts/stoc2_619_documente_pe_jumatate.py [--productie] (--proba | --scrie) --schema tenant_049 [--schema …]
  --proba: totul într-o tranzacție anulată (nimic scris), aceleași numărători."""
import collections
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)


def documente_pe_jumatate(cur, schema):
    """[(cheia documentului, id-ul primei ciorne)] — documentele (cheia `coada_api._GRUP_DOC`: factura, NIR) cu cel puțin o notă validată
    și una ciornă, documentul stornat înaintea stornării lui (factura / borderoul de stornare au `storno_din_id`), apoi după cheie."""
    from core import coada_api as c
    cur.execute('SET LOCAL search_path TO "%s", public' % schema)
    cur.execute("SELECT g, min(id) FILTER (WHERE status = 'ciorna') FROM (SELECT (" + c._GRUP_DOC + ") AS g, i.id, i.status "
                "FROM inregistrari i) x WHERE g IS NOT NULL GROUP BY g HAVING bool_or(status = 'validata') AND bool_or(status = 'ciorna')")
    docs = cur.fetchall()

    def e_stornare(g):
        if not g.startswith("factura-"):
            return False
        cur.execute("SELECT storno_din_id IS NOT NULL FROM facturi WHERE id = %s", (int(g.split("-", 1)[1]),))
        r = cur.fetchone()
        return bool(r and r[0])
    return sorted(((g, n) for g, n in docs), key=lambda x: (e_stornare(x[0]), x[0]))


def completeaza(conn, schema):
    """Completează, pe drumul validării, documentele validate pe jumătate ale schemei. Tranzacția e a apelantului.
    -> {"documente": n, "validate": n note, "refuzate": [codul refuzului]}"""
    import psycopg2
    from core import coada_api as c
    with conn.cursor() as cur:
        docs = documente_pe_jumatate(cur, schema)
    validate, refuzate = 0, []
    for _g, nota in docs:
        try:
            r = c.valideaza_documentul(conn, schema, nota)
        except psycopg2.Error as e:   # refuzul unei reguli din bază (perioada închisă, documentul lipsă): `valideaza_documentul` a anulat
            from core import jurnal_api as j
            refuzate.append(j._cod_din_baza(e) or "EROARE")
            continue
        if r and r.get("ok"):
            validate += len(r["validate"])   # nota cerută și celelalte ciorne ale documentului (`notele_documentului`): toate erau ciorne
        else:
            refuzate.append(str((r or {}).get("cod") or "REFUZ"))
    return {"documente": len(docs), "validate": validate, "refuzate": refuzate}


def main(argv):
    proba, scrie = "--proba" in argv, "--scrie" in argv
    scheme = [argv[i + 1] for i, a in enumerate(argv) if a == "--schema" and i + 1 < len(argv)]
    if proba == scrie or not scheme:
        print(__doc__)
        return 2
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    from core import db
    db.init_pool()
    total, refuzuri = collections.Counter(), collections.Counter()
    for s in scheme:
        if not db.schema_valida(s):
            print("schemă invalidă: %r" % s)
            return 2
        with db.get_conn(s) as conn:
            r = completeaza(conn, s)
            conn.rollback() if proba else conn.commit()
        total.update({"documente": r["documente"], "validate": r["validate"]})
        refuzuri.update(r["refuzate"])
    print("documente validate pe jumătate: %d" % total["documente"])
    print("note validate acum (pe drumul validării): %d" % total["validate"])
    print("documente refuzate (rămân cu ciorne): %d" % sum(refuzuri.values()))
    for cod, n in sorted(refuzuri.items()):
        print("  %s: %d" % (cod, n))
    print("(proba: nimic scris)" if proba else "(scris)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
