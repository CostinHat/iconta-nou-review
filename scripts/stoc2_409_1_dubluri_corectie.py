# -*- coding: utf-8 -*-
"""scripts/stoc2_409_1_dubluri_corectie.py — datele existente ale deficienței 409.1 (lotul 12, comanda Costin 12.2 pct.1, verbatim în
DECIZII „Comanda 12.2”): „F1, 05.10: cinci note 607=371 (8 +100; 30 și 32 stornări ale lui 8; 31 și 33 ieșiri pe Factura 2). Net corect,
dar nota 8 e stornată de două ori, ieșirea e dublată, titlul notei 30 e stricat. Cerut: o stornare, o ieșire, titlu corect.”

DE UNDE VIN. Nu din aplicație: notele 30/31 și 32/33 n-au nicio mișcare de stoc și niciun autor (`creat_de_id` gol) — sunt reparația 409
pe datele F1, rulată de două ori: la publicarea lotului 9 (20.10.2026, 05:07, ISTORIC „Reparația 409 pe datele cabinetului (aprobată):
stornarea notei vechi + nota corectă cu documentul facturii”) și din nou la publicarea lotului 10 (21.10.2026, 16:25, DECIZII „Comanda
10.3” pct.2: „409: nota veche 105 rămâne (R1), stornată de 168 (607=371 −100,00) și înlocuită de 169 (607=371 100,00)”). Scriptul de
atunci nu verifica dacă reparația era deja făcută, iar prima rulare a scris titlul cu textul motivului lipit în eticheta notei
(„Stornare: n (descărcarea facturii, scrisă fără document)ota nr. crt. 8 din 05.10.2026”).

CE FACE. Pentru fiecare notă de stoc validată care are o mișcare de stoc (nota inițială, aici nr. crt. 8), caută notele de CORECȚIE scrise
de o reparație: validate, sursa „stocuri”, fără mișcare de stoc, fără autor, cu data notei inițiale — stornările (rândurile ei cu minus)
și înlocuirile (aceleași rânduri). Dacă sunt câte DOUĂ sau mai multe din fiecare, în același număr (deci o corecție dublată, cu netul
neschimbat), păstrează prima stornare și prima înlocuire și le scoate pe celelalte (perechi), iar stornarea păstrată primește titlul
corect: „Stornare: nota <eticheta notei inițiale> (<descrierea ei>)”, cu motivul scris de reparația dublată („ — …”), dacă îl are.
Rulajul și soldul pe 607 / 371 nu se schimbă (o pereche −100 / +100 scoasă). Numerele din Registrul-jurnal ale perechii scoase (32, 33)
rămân libere: numărul unei note validate nu se mută (deficiența 302), deci notele de după ele își păstrează numărul.

DE CE NU E O MIGRARE ȘI DE CE CERE APROBARE. Scoate note VALIDATE și schimbă titlul uneia — exact ce regulile de fond ale bazei opresc
(OMFP 1802/2014 pct.69: corectura se face prin stornare; `trg_regula_nota`, `trg_regula_linii_nota`), suspendate NUMAI în tranzacția
scriptului, pentru notele numite (`ALTER TABLE … DISABLE TRIGGER` e tranzacțional: la ROLLBACK revine și el). Se rulează NUMAI cu
aprobarea scrisă a lui Costin, după backup, pe schema numită (F1 = `tenant_049` pe producție, `tenant_9049` pe copie).
Uz: ./venv/bin/python scripts/stoc2_409_1_dubluri_corectie.py [--productie] (--proba | --scrie) --schema tenant_049
  --proba: totul într-o tranzacție anulată (nimic scris), aceeași tipărire."""
import os
import sys
from decimal import Decimal

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

#: regulile de fond suspendate în tranzacția reparației (numai ele; perioada închisă și urma sursei rămân active)
REGULI_SUSPENDATE = (("inregistrari", "trg_regula_nota"), ("inregistrari_linii", "trg_regula_linii_nota"))


def _linii(cur, nid):
    cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = %s ORDER BY cont_debit, cont_credit, suma",
                (nid,))
    return [(d, c, Decimal(str(s))) for d, c, s in cur.fetchall()]


def _neg(linii):
    return sorted((d, c, -s) for d, c, s in linii)


def dubluri(cur, schema):
    """[{original, stornari, inlocuiri, de_scos, titlu: (id, vechi, nou) | None}] — corecțiile dublate ale notelor de stoc ale schemei.
    O corecție e a notei inițiale numai dacă o NUMEȘTE (data și sumele nu ajung: două ieșiri din aceeași zi, de aceeași valoare, ar fi
    confundate): stornarea poartă eticheta ei („nota nr. crt. 8 din 05.10.2026”) sau descrierea ei, în document ori în titlu; înlocuirea
    are documentul facturii mișcării notei inițiale („Factură 2 din 05.10.2026”)."""
    from core import eticheta_nota as _et
    cur.execute('SET LOCAL search_path TO "%s", public' % schema)
    cur.execute("SELECT i.id, i.data, i.descriere, (SELECT m.factura_id FROM miscari_stoc m WHERE m.inregistrare_id = i.id "
                "AND m.factura_id IS NOT NULL ORDER BY m.id LIMIT 1) FROM inregistrari i WHERE i.status = 'validata' AND i.sursa = 'stocuri' "
                "AND EXISTS (SELECT 1 FROM miscari_stoc m WHERE m.inregistrare_id = i.id) ORDER BY i.id")
    originale = cur.fetchall()
    cur.execute("SELECT i.id, i.data, COALESCE(i.descriere, ''), COALESCE(i.document_ref, '') FROM inregistrari i WHERE i.status = 'validata' "
                "AND i.sursa = 'stocuri' AND i.creat_de_id IS NULL AND NOT EXISTS (SELECT 1 FROM miscari_stoc m WHERE m.inregistrare_id = i.id) "
                "ORDER BY i.id")
    corectii = [(i, d, ds, doc, _linii(cur, i)) for i, d, ds, doc in cur.fetchall()]
    descr = {i: ds for i, _d, ds, _doc, _li in corectii}
    out = []
    for oid, odata, odescr, ofid in originale:
        lo, et = _linii(cur, oid), _et.nota(cur, schema, oid)
        doc_f = _et.factura(cur, schema, ofid) if ofid else None
        stornari = [i for i, d, ds, doc, li in corectii if d == odata and li == _neg(lo)
                    and (et in doc + " " + ds or (odescr and odescr in ds))]
        inlocuiri = [i for i, d, _ds, doc, li in corectii if d == odata and li == sorted(lo) and doc_f and doc == doc_f]
        if len(stornari) < 2 or len(stornari) != len(inlocuiri):
            continue
        de_scos = stornari[1:] + inlocuiri[1:]
        motiv = next((descr[i].split(" — ", 1)[1] for i in stornari if " — " in descr[i]), None)
        nou = ("Stornare: nota %s (%s)" % (et, odescr or "fără descriere") + (" — %s" % motiv if motiv else ""))[:200]
        titlu = (stornari[0], descr[stornari[0]], nou) if descr[stornari[0]] != nou else None
        out.append({"original": oid, "stornari": stornari, "inlocuiri": inlocuiri, "de_scos": de_scos, "titlu": titlu})
    return out


def repara(conn, schema):
    """Scoate corecțiile dublate și pune titlul stornării păstrate, în tranzacția apelantului. -> lista din `dubluri`, cu ce s-a scos
    tipărit întreg (`scoase`: [(id, nr. crt., data, descriere, document, rânduri)])."""
    from core import db
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        gasite = dubluri(cur, schema)
        if not gasite:
            return []
        for tabel, trg in REGULI_SUSPENDATE:
            cur.execute('ALTER TABLE "%s".%s DISABLE TRIGGER %s' % (schema, tabel, trg))
        for g in gasite:
            cur.execute("SELECT i.id, r.nr_curent, i.data::text, i.descriere, i.document_ref FROM inregistrari i "
                        "LEFT JOIN registru_jurnal_numere r ON r.inregistrare_id = i.id WHERE i.id = ANY(%s) ORDER BY i.id", (g["de_scos"],))
            g["scoase"] = [tuple(x) + (_linii(cur, x[0]),) for x in cur.fetchall()]
            cur.execute("DELETE FROM inregistrari WHERE id = ANY(%s)", (g["de_scos"],))   # rândurile și numărul lor pleacă odată cu ea
            if g["titlu"]:
                cur.execute("UPDATE inregistrari SET descriere = %s WHERE id = %s", (g["titlu"][2], g["titlu"][0]))
        for tabel, trg in REGULI_SUSPENDATE:
            cur.execute('ALTER TABLE "%s".%s ENABLE TRIGGER %s' % (schema, tabel, trg))
    return gasite


def main(argv):
    proba, scrie = "--proba" in argv, "--scrie" in argv
    scheme = [argv[i + 1] for i, a in enumerate(argv) if a == "--schema" and i + 1 < len(argv)]
    if proba == scrie or len(scheme) != 1:
        print(__doc__)
        return 2
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    from core import db
    db.init_pool()
    with db.get_conn(scheme[0]) as conn:
        gasite = repara(conn, scheme[0])
        for g in gasite:
            print("nota inițială %s: stornări %s, înlocuiri %s" % (g["original"], g["stornari"], g["inlocuiri"]))
            for s in g["scoase"]:
                print("  scoasă: id %s, nr. crt. %s, %s, %r, document %r, rânduri %s" % (s[0], s[1], s[2], s[3], s[4],
                                                                                       [(d, c, str(x)) for d, c, x in s[5]]))
            if g["titlu"]:
                print("  titlul notei %s: %r -> %r" % g["titlu"])
        if not gasite:
            print("nicio corecție dublată")
        conn.rollback() if proba else conn.commit()
    print("(proba: nimic scris)" if proba else "(scris)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
