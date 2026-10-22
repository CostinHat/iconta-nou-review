# -*- coding: utf-8 -*-
"""core/eticheta_nota.py — cum se numește o înregistrare în textele pe care le citește omul (deficiența 258, comanda Costin 15.10.2026:
„mesajul pentru asistent spune «Nota #24», iar pe card nota e «Nr. crt. 5»; numărul intern nu se afișează nicăieri.”).

Nota se numește cum o vede contabilul în Registrul jurnal: „nr. crt. 5 din 12.03.2026”. Definiția e UNA, în bază:
`<schema>.eticheta_nota(nid)` (core/migrare_ciorne_proprii.py), folosită și de triggerele care refuză (ciorna altuia, regulile de
fond); aici doar se cheamă, ca refuzul din bază și mesajul din aplicație să spună același lucru. Numerotarea e a
`repo_contabilitate.jurnal_pe_an` (paritatea: core/test_eticheta_nota.py). Operațiunea din registrul de încasări și plăți:
`<schema>.eticheta_rip(oid)` („plata din 12.03.2026 de 150,00 RON”). Factura: felul, numărul cu seria și data
(`jurnal_api.eticheta_factura`, „Factură FCT nr. 12 din 05.10.2026”) — niciodată id-ul.

`schema` gol = schema curentă a conexiunii (cursorul cu `search_path` pus). Cursor dict sau tuplu.
"""

#: o notă care nu (mai) există n-are număr curent; mesajul o spune, nu inventează unul
NOTA_INEXISTENTA = "care nu mai există"


def _q(schema):
    return '"%s".' % str(schema).strip('"') if schema else ""


def _unu(cur):
    r = cur.fetchone()
    if r is None:
        return None
    return list(r.values())[0] if isinstance(r, dict) else r[0]


def nota(cur, schema, nid):
    """„nr. crt. 5 din 12.03.2026” — nota `nid` cum o arată Registrul jurnal."""
    cur.execute("SELECT %seticheta_nota(%%s)" % _q(schema), (int(nid),))
    return _unu(cur) or NOTA_INEXISTENTA


def note(cur, schema, ids):
    """[(id, eticheta)] pentru mai multe note, într-o singură interogare, în ordinea din Registrul jurnal (data, apoi id-ul)."""
    ids = sorted({int(i) for i in ids or [] if i})
    if not ids:
        return []
    s = _q(schema)
    cur.execute("SELECT n.id, %seticheta_nota(n.id) FROM %sinregistrari n WHERE n.id = ANY(%%s) ORDER BY n.data, n.id" % (s, s), (ids,))
    return [tuple(list(r.values()) if isinstance(r, dict) else r) for r in cur.fetchall()]


def lista(cur, schema, ids):
    """„nr. crt. 5 din 12.03.2026, nr. crt. 6 din 12.03.2026” — mai multe note, în ordinea din Registrul jurnal."""
    return ", ".join(e for _, e in note(cur, schema, ids)) or NOTA_INEXISTENTA


def rip(cur, schema, oid):
    """„plata din 12.03.2026 de 150,00 RON” — operațiunea din registrul de încasări și plăți cum o arată rândul ei."""
    cur.execute("SELECT %seticheta_rip(%%s)" % _q(schema), (int(oid),))
    return _unu(cur) or "operațiunea care nu mai există"


def factura(cur, schema, fid):
    """„Factură FCT nr. 12 din 05.10.2026” — felul, numărul cu seria și data, ca în Registrul jurnal (`jurnal_api.eticheta_factura`)."""
    cur.execute("SELECT tip, serie, numar, data_emitere FROM %sfacturi WHERE id = %%s" % _q(schema), (int(fid),))
    r = cur.fetchone()
    if r is None:
        return "factura care nu mai există"
    tip, serie, numar, data = list(r.values()) if isinstance(r, dict) else r
    return factura_din_rand({"tip": tip, "serie": serie, "numar": numar, "data_emitere": data})


def factura_din_rand(f):
    """Aceeași etichetă din rândul facturii deja citit (dict cu `tip`, `serie`, `numar`, `data_emitere`); None dacă n-are număr."""
    if f.get("numar") is None:
        return None
    from core import jurnal_api as _j
    return _j.eticheta_factura(f.get("tip"), f.get("serie"), f["numar"], f.get("data_emitere"))


def conturi(cur, schema, nid):
    """[401, lotul 9] Ce a scris nota, în conturi: „371 = 401 200,00 lei” (rândurile cu aceleași conturi, însumate, în ordinea lor) — ca
    ecranul să arate nota după generare, nu numai numărul ei. None fără rânduri."""
    from core.pdf_util import bani
    cur.execute("SELECT cont_debit, cont_credit, sum(suma) FROM %sinregistrari_linii WHERE inregistrare_id = %%s "
                "GROUP BY cont_debit, cont_credit ORDER BY min(id)" % _q(schema), (int(nid),))
    rows = [tuple(r.values()) if isinstance(r, dict) else tuple(r) for r in cur.fetchall()]
    return "; ".join("%s = %s %s lei" % (d, c, bani(s)) for d, c, s in rows) or None


def in_raspuns(cur, schema, rez):
    """Pune lângă id-urile de note dintr-un răspuns etichetele lor, ca ecranul să numească nota cum o arată Registrul jurnal:
    `nota_eticheta` (și `nota`, conturile ei) lângă `inregistrare_id` / `nota_id`, `note_etichete` (în ordinea din jurnal) lângă `inregistrari`. Întoarce `rez`."""
    nid = rez.get("inregistrare_id") or rez.get("nota_id")
    if nid:
        rez["nota_eticheta"] = nota(cur, schema, nid)
        _c = conturi(cur, schema, nid)   # [401] conturile notei, arătate după generare (o `nota` pusă de operațiune rămâne a ei)
        if _c and "nota" not in rez:
            rez["nota"] = _c
    if rez.get("inregistrari"):
        rez["note_etichete"] = [e for _, e in note(cur, schema, rez["inregistrari"])]
    return rez
