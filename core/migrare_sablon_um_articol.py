"""
core/migrare_sablon_um_articol.py — unitatea de măsură pe liniile șabloanelor de facturi recurente (lotul 13, regula UM).

DECIZIA (sesiunea principală, 26.10.2026, pe întrebarea zonei fact, verbatim): „Șablonul recurent — DA: linia șablonului poartă UM, cu
aceeași regulă (`um_linie`: scris de om / al articolului / refuz lângă câmp la salvarea șablonului); șabloanele vechi fără UM: la emiterea
lunii, linia fără UM și fără articol nu se emite pe ascuns cu «buc» — șablonul se oprește cu refuzul în clopoțel (mecanismul C109
existent), ca să fie completat o dată. Datele existente: migrare care pune UM-ul articolului unde linia are articol; restul rămân de
completat (le numește refuzul).”

CE FACE: pe `facturi_recurente.linii` (jsonb, lista liniilor), o linie cu `articol_id` și fără UM (cheia lipsă sau goală) primește UM-ul
articolului din nomenclator (`articole.um`) — regula `facturi.um_linie`. Liniile fără articol rămân cum sunt: refuzul cronului le numește
(`facturi_recurente.verificari_drum`, câmpul `fr-l{i}-um`). Facturile emise deja nu se ating. Idempotentă (atinge numai liniile fără UM).
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_sablon_um_articol.py`.
"""
import json

from core import db
from core import facturi as _fc


def linii_cu_um(linii, um_articole):
    """PURĂ. (liniile noi, câte au primit UM) — UM-ul articolului pe liniile cu articol și fără UM (`facturi.um_linie`); restul neatinse."""
    out, n = [], 0
    for l in linii or []:
        if isinstance(l, dict) and l.get("articol_id") and not str(l.get("um") or "").strip():
            um = _fc.um_linie(l, um_articole.get(int(l["articol_id"])))
            if um:
                l = dict(l, um=um)
                n += 1
        out.append(l)
    return out, n


def aplica(conn, schema):
    """Întoarce {"linii": n, "sabloane": [id]} — liniile care au primit UM-ul articolului."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute('SELECT id, um FROM "%s".articole' % schema)
        um_articole = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute('SELECT id, linii FROM "%s".facturi_recurente ORDER BY id' % schema)
        sabloane = cur.fetchall()
        total, atinse = 0, []
        for sid, linii in sabloane:
            if isinstance(linii, str):
                linii = json.loads(linii)
            noi, n = linii_cu_um(linii, um_articole)
            if n:
                cur.execute('UPDATE "%s".facturi_recurente SET linii = %%s WHERE id = %%s' % schema, (json.dumps(noi), sid))
                total += n
                atinse.append(sid)
    return {"linii": total, "sabloane": atinse}


def verifica(conn, schema):
    """Nicio linie de șablon cu articol rămasă fără UM, când articolul are unul."""
    r = aplica(conn, schema)
    conn.rollback()
    return r["linii"] == 0


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    ok, esec, total = 0, [], 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                r = aplica(conn, s)
                conn.commit()
            ok += 1
            total += r["linii"]
            if r["sabloane"]:
                print("  %s: șabloanele %s au acum UM-ul articolului pe linie" % (s, ", ".join(str(x) for x in r["sabloane"])))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_sablon_um_articol: %d ok, %d esec, %d linii cu UM-ul articolului" % (ok, len(esec), total))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
