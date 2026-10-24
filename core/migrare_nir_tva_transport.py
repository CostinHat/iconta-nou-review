"""
core/migrare_nir_tva_transport.py — TVA-ul transportului facturat, pe NIR-urile scrise înainte de reparația deficienței 476 (lotul 12).

DEFECTUL (Costin, comanda 12.1, grav): „NIR: TVA transport cu factură pe 4428 în loc de 4426.” TVA-ul transportului lua contul TVA-ului
MĂRFII: la NIR-ul fără factură al mărfii (408, TVA pe 4428.01), transportul facturat de transportator (datoria pe 401) ieșea
4428.01 = 401 — neexigibil deși factura transportului există, iar legarea facturii mărfii mută numai 4428.01 = 408, deci rămânea acolo.
Reparat în `stocuri.cont_tva_transport`. Temei: CF art.299 alin.(1) lit.a (deducerea cere factura, pe care transportul o are); OMFP 1802/2014,
funcțiunea contului 4426 („taxa pe valoarea adăugată deductibilă potrivit legii (401, 404, ...)”) și a contului 408 (4428 numai pentru
aprovizionările pentru care nu s-au primit facturi).

DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): pe notele NIR-urilor, rândul 4428.01 = <cont
diferit de 408> e TVA-ul unui transport cu factură:
  · nota CIORNĂ: rândul trece pe 4426 (aceeași sumă, același cont creditor) — nota nu e încă evidență;
  · nota VALIDATĂ: nu se modifică (OMFP 1802/2014 pct.69); se scrie o notă CIORNĂ de corectură 4426 = 4428.01, cu suma și data NIR-ului și
    NIR-ul ca document — intră în evidență numai după ce o validează un om;
  · luna blocată: nu se scrie nimic, NIR-ul se numește la rulare (redeschiderea lunii e decizia contabilului).
Idempotentă: corectura are în descriere marcajul `MARCAJ`, iar rândul ciornei mutat nu mai e 4428.01. Rulare:
`python -m core.migrari_registru ruleaza [--productie] core/migrare_nir_tva_transport.py`.
"""
from core import db

MARCAJ = "Corectură TVA transport (476)"


def aplica(conn, schema):
    """-> {"ciorne": n, "corecturi": n, "blocate": [(nir_numar, motiv)]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    from core import stocuri_api as _sa
    from core import jurnal_api as _j
    from core import nir_legare as _nl
    from core import eticheta_nota as _et
    rez = {"ciorne": 0, "corecturi": 0, "blocate": []}
    s = '"%s"' % schema
    with conn.cursor() as cur:
        cur.execute("SELECT id, numar, data, inregistrari_ids FROM %s.nir WHERE COALESCE(transport, 0) > 0 ORDER BY id" % s)
        nirs = [{"id": r[0], "numar": r[1], "data": r[2], "inregistrari_ids": r[3]} for r in cur.fetchall()]
        for n in nirs:
            note = _sa.note_nir(n)
            if not note:
                continue
            cur.execute("SELECT l.id, l.inregistrare_id, l.suma, i.status FROM %s.inregistrari_linii l JOIN %s.inregistrari i "
                        "ON i.id = l.inregistrare_id WHERE l.inregistrare_id = ANY(%%s) AND l.cont_debit = %%s "
                        "AND split_part(l.cont_credit, '.', 1) <> %%s ORDER BY l.id" % (s, s),
                        (note, _nl.CONT_TVA_NIR, _nl.CONT_NESOSITE))
            doc = _j.eticheta_document("NIR", n["numar"], n["data"])
            for lid, iid, suma, status in cur.fetchall():
                cur.execute("SAVEPOINT m476")
                try:
                    if status != "validata":
                        cur.execute("UPDATE %s.inregistrari_linii SET cont_debit = '4426' WHERE id = %%s" % s, (lid,))
                        rez["ciorne"] += 1
                    else:
                        # nota cum o vede contabilul în Registrul jurnal („nr. crt. N din ZZ.LL.AAAA”, `eticheta_nota`), nu id-ul ei; numărul
                        # notei validate nu se mai schimbă (`nr_curent_neschimbat`), deci descrierea rămâne cheia idempotenței
                        desc = "%s — NIR %s: TVA-ul transportului facturat e deductibil (4426), nu neexigibil (rândul din nota %s)" % (
                            MARCAJ, n["numar"], _et.nota(cur, schema, iid))
                        cur.execute("SELECT 1 FROM %s.inregistrari WHERE descriere = %%s" % s, (desc[:200],))
                        if cur.fetchone():
                            cur.execute("RELEASE SAVEPOINT m476")
                            continue
                        cur.execute("INSERT INTO %s.inregistrari (data, descriere, sursa, status, document_ref) "
                                    "VALUES (%%s, %%s, 'stocuri', 'ciorna', %%s) RETURNING id" % s, (n["data"], desc[:200], doc))
                        nid = cur.fetchone()[0]
                        cur.execute("INSERT INTO %s.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                                    "VALUES (%%s, '4426', %%s, %%s)" % s, (nid, _nl.CONT_TVA_NIR, suma))
                        rez["corecturi"] += 1
                    cur.execute("RELEASE SAVEPOINT m476")
                except Exception as e:  # noqa: BLE001 — luna blocată (PERIOADA_BLOCATA) sau ciorna altui utilizator: se numește, nu se forțează
                    cur.execute("ROLLBACK TO SAVEPOINT m476")
                    rez["blocate"].append((n["numar"], str(e).split("\n")[0][:160]))
    return rez


def verifica(conn, schema):
    """Niciun rând 4428.01 = <cont diferit de 408> pe o notă CIORNĂ a unui NIR cu transport."""
    from core import stocuri_api as _sa
    s = '"%s"' % schema
    with conn.cursor() as cur:
        cur.execute("SELECT inregistrari_ids FROM %s.nir WHERE COALESCE(transport, 0) > 0" % s)
        note = [i for (ids,) in cur.fetchall() for i in _sa.note_nir({"inregistrari_ids": ids})]
        if not note:
            return True
        cur.execute("SELECT count(*) FROM %s.inregistrari_linii l JOIN %s.inregistrari i ON i.id = l.inregistrare_id "
                    "WHERE l.inregistrare_id = ANY(%%s) AND i.status <> 'validata' AND l.cont_debit = '4428.01' "
                    "AND split_part(l.cont_credit, '.', 1) <> '408'" % (s, s), (note,))
        return cur.fetchone()[0] == 0


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, ciorne, corecturi = 0, [], 0, 0
    for sc in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, sc)
                conn.commit()
            ok += 1
            ciorne += r["ciorne"]
            corecturi += r["corecturi"]
            for numar, motiv in r["blocate"]:
                print("  %s: NIR %s — rândul TVA-ului transportului nu s-a corectat: %s" % (sc, numar, motiv))
        except Exception as e:  # noqa: BLE001
            esec.append((sc, str(e)))
    print("migrare_nir_tva_transport: %d ok, %d esec, %d rânduri de ciornă mutate pe 4426, %d note ciornă de corectură scrise"
          % (ok, len(esec), ciorne, corecturi))
    for sc, e in esec:
        print("  ESEC %s: %s" % (sc, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
