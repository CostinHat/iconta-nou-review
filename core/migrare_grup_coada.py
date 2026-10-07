# -*- coding: utf-8 -*-
"""core/migrare_grup_coada.py — cheia DOCUMENTULUI pe elementele existente din coadă (lotul 07.10 B, comanda Costin C8).

Comanda: „coada grupează notele aceluiași document și pentru elementele existente (migrare) … Aceeași grupare pentru cele 4
note ale unui NIR.” Măsurat pe producție, 07.10: elementele F1A3 (contarea + ieșirea din stoc, create pe 06.10 la 12:54,
înaintea grupării) n-aveau `payload.grup`, deci apăreau ca două documente; cele 4 note ale NIR-ului 1 aveau fiecare cheia ei.

Recalculează `payload.grup` pentru TOATE elementele `fel='nota'` cu aceeași definiție ca la inserare (`coada_api._GRUP_DOC`,
pe schema firmei) și reface `hash`-ul payload-ului. Nu schimbă nicio stare: un element validat rămâne validat, unul la validare
rămâne la validare — doar se leagă de documentul lui. Idempotentă. `python3 -m core.migrare_grup_coada`.
"""
import psycopg2.extras as _E

from core import coada_api as _c
from core import db


def aplica(conn, tenant_id=None):
    """Întoarce [(coada_id, grup_vechi, grup_nou)] pentru rândurile schimbate. `conn` poate fi pe orice schemă."""
    schimbate = []
    with conn.cursor(cursor_factory=_E.RealDictCursor) as cur:
        cond, val = "c.fel = 'nota'", []
        if tenant_id is not None:
            cond += " AND c.tenant_id = %s"
            val.append(tenant_id)
        cur.execute("SELECT c.id, c.payload, c.perioada, t.schema_name FROM public.declaratii_coada c "
                    "JOIN public.tenants t ON t.id = c.tenant_id WHERE " + cond + " ORDER BY c.id", val)
        randuri = cur.fetchall()
        for r in randuri:
            if not db.schema_valida(r["schema_name"]):
                continue
            nota_id = int(str(r["perioada"]).split("-", 1)[1])
            cur.execute('SET LOCAL search_path TO "%s", public' % r["schema_name"])
            cur.execute("SELECT " + _c._GRUP_DOC + " AS grup_doc FROM inregistrari i WHERE i.id = %s", (nota_id,))
            x = cur.fetchone()
            nou = _c.grup_nota(nota_id, x["grup_doc"] if x else None)
            p = dict(r["payload"] or {})
            if p.get("grup") == nou:
                continue
            vechi, p["grup"] = p.get("grup"), nou
            cur.execute("UPDATE public.declaratii_coada SET payload = %s, hash = %s WHERE id = %s",
                        (_E.Json(p), _c.calcul_hash(p), r["id"]))
            schimbate.append((r["id"], vechi, nou))
        cur.execute("RESET search_path")
    return schimbate


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        s = aplica(conn)
        conn.commit()
    print("migrare grup_coada: %d elemente legate de documentul lor" % len(s))
    for cid, v, n in s:
        print("  #%s  %s -> %s" % (cid, v, n))


if __name__ == "__main__":
    _main()
