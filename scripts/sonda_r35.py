# -*- coding: utf-8 -*-
"""SONDA R35 — verdicte TVA care ies VERZI peste un necunoscut pe care il au in mana.

DE CE EXISTA CA FISIER: cifra din 24.08 („3 din 9 perechi verzi cu facturi necontabilizate") a fost
masurata ad-hoc. O cifra care nu se poate recalcula nu e o masuratoare, e o amintire.

    ./venv/bin/python scripts/sonda_r35.py

ESANTIONUL, ca REGULA nu ca lista: toate schemele ACTIVE, ori lunile lui 2026 in care firma are cel
putin o factura. O luna fara facturi n-are cum sa produca clasa asta, iar a o include ar umfla
numitorul cu perechi pe care masuratoarea nu le poate atinge.

DOUA CLASE, numarate SEPARAT, fiindca se repara in locuri diferite:
  * VERDE-PESTE-NECUNOSCUT — verdictul e verde, iar `facturi_necontabilizate` din propriul lui
    payload NU e gol. Asta e R35 ca atare.
  * VERDE-PESTE-GRI — verdictul de sus e verde, desi printre constatarile lui exista una GRI.
    Agregarea `rosu if any(rosu) else verde` nu are ramura de gri, deci o inghite. E o a doua
    instanta, in aceeasi functie, si nu se vede din prima.

NU SCRIE NIMIC: `pg_stat_user_tables` inainte si dupa, iar diferenta se tipareste.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, control_incrucisat as _ci  # noqa: E402


def scrieri(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT coalesce(sum(n_tup_ins), 0), coalesce(sum(n_tup_upd), 0), "
                    "coalesce(sum(n_tup_del), 0) FROM pg_stat_user_tables")
        return cur.fetchone()


def perechi(conn):
    """(schema, an, luna) — schemele active, pe lunile cu cel putin o factura."""
    out = []
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY schema_name")
        scheme = [r[0] for r in cur.fetchall()]
    for s in scheme:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM data_emitere)::int, "
                            "EXTRACT(MONTH FROM data_emitere)::int FROM %s.facturi "
                            "WHERE data_emitere IS NOT NULL ORDER BY 1, 2" % s)
                for an, luna in cur.fetchall():
                    out.append((s, an, luna))
        except Exception:
            conn.rollback()
    # ANTI-VACUU. Prima forma a sondei intreba de coloana `data`, care nu exista pe `facturi`
    # (e `data_emitere`); exceptia era inghitita de `rollback`, iar sonda a raportat linistit
    # "0 perechi · 0 verzi peste necunoscut" - adica un rezultat FAVORABIL pe o lume pe care
    # n-o vedea. De-aia domeniul gol e o EROARE, nu un raspuns.
    assert out, ("sonda n-a gasit nicio pereche (schema x luna cu facturi) - domeniul e gol, "
                 "deci orice raspuns al ei ar fi despre nimic")
    return out


def ruleaza():
    db.init_pool()
    with db.get_conn() as conn:
        p = perechi(conn)
        inainte = scrieri(conn)
        print("PERECHI: %d (scheme active x lunile cu facturi)" % len(p))
        print("pg_stat_user_tables INAINTE: ins=%d upd=%d del=%d\n" % inainte)
        verde_peste_necunoscut, verde_peste_gri, sarite = [], [], []
        for schema, an, luna in p:
            try:
                with conn.cursor() as cur:
                    cur.execute("SET search_path TO %s, public" % schema)
                v = _ci.verifica_tva(conn, schema, an, luna)
            except Exception as e:
                conn.rollback()
                sarite.append((schema, an, luna, "%s: %s" % (type(e).__name__, str(e)[:70])))
                continue
            finally:
                try:
                    with conn.cursor() as cur:
                        cur.execute("SET search_path TO public")
                except Exception:
                    conn.rollback()
            nec = v.get("facturi_necontabilizate") or []
            gri = [c for c in (v.get("constatari") or []) if c.get("stare") == "gri"]
            if v.get("stare") == "verde" and nec:
                verde_peste_necunoscut.append((schema, an, luna, len(nec),
                                               sum(float(f.get("tva") or 0) for f in nec)))
            if v.get("stare") == "verde" and gri:
                verde_peste_gri.append((schema, an, luna, [c.get("eticheta") for c in gri]))
        dupa = scrieri(conn)

    print("VERDE PESTE NECUNOSCUT (R35): %d perechi" % len(verde_peste_necunoscut))
    for schema, an, luna, n, tva in verde_peste_necunoscut:
        print("    %s %d-%02d — verdict VERDE, iar payload-ul poarta %d facturi necontabilizate "
              "(TVA %.2f)" % (schema, an, luna, n, tva))
    print("VERDE PESTE GRI (agregare fara ramura de gri): %d perechi" % len(verde_peste_gri))
    for schema, an, luna, et in verde_peste_gri:
        print("    %s %d-%02d — verdict VERDE, cu constatari GRI: %s" % (schema, an, luna, et))
    print("perechi nemasurabile: %d" % len(sarite))
    for schema, an, luna, motiv in sarite[:12]:
        print("    SARIT %s %d-%02d — %s" % (schema, an, luna, motiv))
    delta = tuple(b - a for a, b in zip(inainte, dupa))
    print("\npg_stat_user_tables DUPA: ins=%d upd=%d del=%d" % dupa)
    print("DELTA scrieri: ins=%+d upd=%+d del=%+d  →  %s"
          % (delta + ("SONDA N-A SCRIS" if delta == (0, 0, 0) else "*** A SCRIS ***",)))
    return verde_peste_necunoscut, verde_peste_gri, sarite, delta


if __name__ == "__main__":
    vn, vg, sar, delta = ruleaza()
    print("\nVERDICT R35")
    print("  verzi peste necunoscut: %d" % len(vn))
    print("  verzi peste gri:        %d" % len(vg))
    print("  scrieri: %s" % ("ZERO" if delta == (0, 0, 0) else str(delta)))
