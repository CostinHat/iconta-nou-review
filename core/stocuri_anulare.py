# -*- coding: utf-8 -*-
"""core/stocuri_anulare.py — respingerea unui document cu mișcare de stoc o stornează în fișa de magazie (retest Costin 07.10, R1).

Decizia Costin (07.10.2026), verbatim: „respingerea anulează mișcarea de stoc printr-o înregistrare inversă în fișa de magazie
(nu prin ștergere), cu CMP recalculat. Documentul respins rămâne în listă, marcat «respins», cu motivul vizibil, și poate fi
refăcut de asistent.”

FORMA: stornare în ROȘU. OMFP 1802/2014 pct.69: „Înregistrarea stornării unei operațiuni contabile aferente exercițiului
financiar curent se efectuează fie prin corectarea cu semnul minus a operațiunii inițiale (stornare în roșu), fie prin
înregistrarea inversă a acesteia (stornare în negru), în funcție de politica contabilă și programele informatice utilizate.”
*INTERPRETARE CU TEMEI:* aleasă stornarea în roșu (aceeași mișcare, cantitatea și valoarea cu minus, `anuleaza_id` = mișcarea
stornată), fiindcă toate citirile care însumează pe tip (stocul pe locații, D406, costul vânzărilor) se anulează singure, fără o
excludere în fiecare interogare; iar valoarea ieșită e exact a mișcării (nu CMP-ul de acum). Alternativa respinsă: stornarea în
negru (o ieșire pentru o intrare) — fiecare agregare ar fi trebuit să excludă perechea. De reconfirmat dacă politica contabilă a
firmei cere negru.

DATA stornării = data respingerii (sau a mișcării, dacă e mai târzie): ieșirile de după intrare își păstrează CMP-ul cu care au
fost contate — o stornare datată în trecut le-ar fi schimbat valoarea în fișă fără să le schimbe nota.

Documentul unei mișcări (aceeași cheie ca în coadă, `coada_api._GRUP_DOC`): `nir-<id>` -> `miscari_stoc.nir_id`; `factura-<id>`
-> `miscari_stoc.factura_id`; altfel nota însăși (`inregistrare_id`: ieșirea manuală, rețeta, inventarul).
"""
from datetime import date as _date
from decimal import Decimal

from psycopg2.extras import RealDictCursor

#: mișcările VII ale unui document: nici stornări, nici stornate deja
_VII = "m.anuleaza_id IS NULL AND NOT EXISTS (SELECT 1 FROM {s}.miscari_stoc r WHERE r.anuleaza_id = m.id)"

MESAJ_IESITA = ("Respingerea nu s-a făcut: %s a intrat în stoc, iar marfa a ieșit deja (%s). Stornarea intrării ar lăsa stocul "
                "negativ. Anulează întâi ieșirile care au folosit-o, apoi respinge documentul.")


def _cheie(grup):
    g = str(grup or "")
    for pref, col in (("nir-", "nir_id"), ("factura-", "factura_id")):
        if g.startswith(pref) and g[len(pref):].isdigit():
            return col, int(g[len(pref):])
    return None, None


def miscari_vii(cur, schema, grup, note_ids):
    """Mișcările vii ale documentului (cheia de grup din coadă + notele lui)."""
    col, val = _cheie(grup)
    if col:
        cond, arg = "m.%s = %%s" % col, val
    else:
        cond, arg = "m.inregistrare_id = ANY(%s)", [int(i) for i in note_ids or []]
    cur.execute(("SELECT m.* FROM {s}.miscari_stoc m WHERE " + cond + " AND " + _VII + " ORDER BY m.id").format(s=schema), (arg,))
    return [dict(r) for r in cur.fetchall()]


def storneaza(conn, schema, grup, note_ids, motiv):
    """Stornează în roșu mișcările vii ale documentului. Întoarce {"stornate": [ids]} sau {"eroare": mesaj} (nimic scris)."""
    from core import repo_stocuri, stocuri_cv as _cv
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        miscari = miscari_vii(cur, schema, grup, note_ids)
        if not miscari:
            return {"stornate": []}
        azi = _date.today()
        noi = []
        cur.execute("SAVEPOINT stornare")   # un refuz nu lasă nimic scris, oricine ar fi apelantul
        for m in miscari:
            d = max(azi, m["data"])
            doc = ("Stornare: %s (respins la validare)" % (m.get("document") or "mișcare #%s" % m["id"]))[:100]
            cur.execute(f"""INSERT INTO {schema}.miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document,
                                inregistrare_id, locatie, factura_id, nir_id, anuleaza_id)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                        (m["articol_id"], d, m["tip"], -Decimal(str(m["cantitate"])), m.get("pret_unitar"),
                         -Decimal(str(m["valoare"])), doc, m.get("inregistrare_id"), m.get("locatie"), m.get("factura_id"),
                         m.get("nir_id"), m["id"]))
            noi.append(cur.fetchone()["id"])
        # fișa fiecărui articol atins se recalculează cu stornările: o intrare a cărei marfă a ieșit deja nu se poate storna
        for aid in sorted({m["articol_id"] for m in miscari}):
            try:
                _cv.fisa_magazie(repo_stocuri.miscari_ale_articolului(cur, schema, aid))
            except ValueError:
                cur.execute(f"SELECT denumire FROM {schema}.articole WHERE id = %s", (aid,))
                den = (cur.fetchone() or {}).get("denumire") or "articolul"
                doc = next((m.get("document") for m in miscari if m["articol_id"] == aid), None) or "documentul"
                cur.execute("ROLLBACK TO SAVEPOINT stornare")
                return {"eroare": MESAJ_IESITA % (doc, den)}
        cur.execute("RELEASE SAVEPOINT stornare")
    return {"stornate": noi}


def document_stornat(cur, schema, nota_id):
    """Nota aparține unui document al cărui stoc a fost stornat la respingere și nerefăcut? Atunci nota nu mai poate intra în
    evidență (validare din jurnal, retrimitere): mișcarea ei nu mai există. Întoarce eticheta documentului sau None.
    `schema` gol = schema din calea conexiunii (`db.get_conn(schema)`)."""
    p = (schema + ".") if schema else ""
    vii = _VII.replace("{s}.", p)
    cur.execute(f"""SELECT r.document FROM {p}miscari_stoc r
                    JOIN {p}inregistrari i ON i.id = %s
                    WHERE r.anuleaza_id IS NOT NULL AND (
                          r.inregistrare_id = i.id
                       OR r.nir_id = (SELECT n.id FROM {p}nir n WHERE n.inregistrari_ids @> to_jsonb(i.id) ORDER BY n.id LIMIT 1)
                       OR (r.factura_id = i.factura_id AND NOT EXISTS (
                              SELECT 1 FROM {p}miscari_stoc m WHERE m.factura_id = i.factura_id AND {vii})))
                    LIMIT 1""", (nota_id,))
    r = cur.fetchone()
    if not r:
        return None
    return (r["document"] if isinstance(r, dict) else r[0]) or "documentul"


COD_DOCUMENT_STORNAT = "DOCUMENT_STORNAT"
MESAJ_NOTA_STORNATA = ("Nota nu mai intră în evidență: documentul ei a fost respins la validare, iar mișcarea lui de stoc a fost "
                       "stornată (%s). Refă documentul — un NIR sau o ieșire nouă; la factură, „Contabilizează” reface și stocul.")


def reface_factura(conn, schema, factura_id):
    """Factura refăcută („Contabilizează” după respingere) își reface și mișcarea de stoc stornată: intrarea (factura primită)
    sau ieșirile (factura emisă, cu nota lor nouă — ciornele respinse ale ieșirilor vechi se scot, elementul lor din coadă rămâne
    ca istoric). No-op dacă factura n-are stornări sau are deja mișcări vii."""
    from core import note_derivate as _nd, stocuri_cv_api as _cvapi
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(f"""SELECT o.tip, o.data, o.inregistrare_id, a.cont_stoc, a.cont_cheltuiala
                        FROM {schema}.miscari_stoc r JOIN {schema}.miscari_stoc o ON o.id = r.anuleaza_id
                        JOIN {schema}.articole a ON a.id = o.articol_id
                        WHERE r.factura_id = %s AND o.tip <> 'ajustare' ORDER BY o.id""", (factura_id,))
        # [08.10 §6 pct.2] ajustarea de preț a unei facturi legate de NIR nu se reface aici: o rescrie contarea (`nir_legare`)
        stornate = [dict(x) for x in cur.fetchall()]
        if not stornate:
            return None
        cur.execute(f"SELECT 1 FROM {schema}.miscari_stoc m WHERE m.factura_id = %s AND {_VII.format(s=schema)} LIMIT 1",
                    (factura_id,))
        if cur.fetchone():
            return None
        for iid in sorted({s["inregistrare_id"] for s in stornate if s["tip"] == "iesire" and s["inregistrare_id"]}):
            if _nd.respinsa(cur, schema, iid):
                _nd.sterge_respinsa(cur, schema, iid)
    s0 = stornate[0]
    if s0["tip"] == "intrare":
        return _cvapi.intrare_din_factura(conn, schema, factura_id, s0["cont_stoc"], s0["data"], s0.get("cont_cheltuiala"))
    return _cvapi.descarca_factura(conn, schema, factura_id, s0["data"])
