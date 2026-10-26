# -*- coding: utf-8 -*-
"""scripts/lot13_migr_c120_facturi_altei_firme.py — DATELE EXISTENTE ale deficienței C120 (lotul 13, comanda Costin 13.1 pct.4 + regula 3a:
„Orice reparație acoperă și datele existente”), NUMAI CITIRE.

C120 (găsită de Code la 599, lotul 12): „Importul manual al unui XML e-Factura în care firma nu e nici furnizor, nici cumpărător intra ca
factură primită, cu TVA de dedus”. Reparația (lotul 12) refuză importul și validarea; facturile intrate ÎNAINTE rămân de găsit. Scriptul
le caută pe fiecare firmă: rândurile din `efactura_primite` (XML-urile primite / importate) al căror emitent ȘI beneficiar diferă de codul
fiscal al firmei (Date firmă), cu starea lor (descărcată / ciornă / validată / respinsă) și factura legată. Nu scrie nimic.

Rulare: `./venv/bin/python scripts/lot13_migr_c120_facturi_altei_firme.py` — pe baza din mediul procesului (`core.db`). Pe PRODUCȚIE numai
cu aprobarea lui Costin (CLAUDE.md §7: datele cabinetului real nu se citesc fără aprobarea lui), iar rezultatul nu intră în rapoarte
decât ca număr.
"""
import os
import re
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)


def _cifre(v):
    return re.sub(r"\D", "", str(v or ""))


def cauta(conn):
    """[(schema, id, emitent, beneficiar, stare, factura_id)] — XML-urile primite ale altei firme, pe toate firmele."""
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
        scheme = [r[0] for r in cur.fetchall()]
        for s in scheme:
            cur.execute("SELECT to_regclass(%s), to_regclass(%s)", ('"%s".efactura_primite' % s, '"%s".firma_profil' % s))
            a, b = cur.fetchone()
            if a is None or b is None:
                continue
            cur.execute('SELECT cui FROM "%s".firma_profil WHERE id = 1' % s)
            r = cur.fetchone()
            cui = _cifre(r[0]) if r else ""
            if not cui:
                continue
            cur.execute('SELECT id, cif_emitent, cif_beneficiar, status, factura_id FROM "%s".efactura_primite ORDER BY id' % s)
            for i, em, ben, st, fid in cur.fetchall():
                if _cifre(em) != cui and _cifre(ben) != cui:
                    out.append((s, i, em, ben, st, fid))
    return out


def main(argv):
    if argv:   # argumentele, înainte de orice efect (core/test_argumente_script.py): scriptul n-are niciunul
        print("Uz: ./venv/bin/python scripts/lot13_migr_c120_facturi_altei_firme.py   (numai citire, pe baza din mediu)")
        return 0 if set(argv) <= {"-h", "--help"} else 2
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        gasite = cauta(conn)
        conn.rollback()
    for x in gasite:
        print("%s: XML %s — emitent %s, beneficiar %s, stare %s, factura %s" % x)
    print("C120: %d XML-uri primite ale altei firme" % len(gasite))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
