# -*- coding: utf-8 -*-
"""SONDA R34 — nota de salarii vs D112 declarat, pe cele 40 de perechi (firma x luna).

DE CE EXISTA CA FISIER, nu ca script ad-hoc: cifra „29 de divergente pe 10 perechi" a fost
masurata pe 24.08.2026 fara sa lase un instrument. O cifra care nu se poate recalcula nu e o
masuratoare, e o amintire. Acum se poate rula oricand:

    ./venv/bin/python scripts/sonda_r34.py

ESANTIONUL, scris ca sa fie reproductibil: cele 8 scheme active cu cel putin un salariat, ori
lunile 2026-04 … 2026-08 = **40 de perechi**. Nu „firmele care ies azi" — regula, nu lista.

DOUA FORME, masurate pe aceleasi perechi:
  * VECHE — agregare din `calcul_salariu` per salariat, adica forma de dinainte de R34. E
    pastrata AICI, dublata deliberat fata de modul: o linie de baza care se schimba odata cu
    codul reparat nu mai e o linie de baza. Fara ea, un „0 divergente" n-ar dovedi nimic — ar
    putea insemna la fel de bine ca sonda nu vede nimic (interdictia 19).
  * NOUA — `salarii_contare.note_lunare`, care citeste cele patru pozitii din D112.

NU SCRIE NIMIC: `pg_stat_user_tables` se citeste inainte si dupa, iar diferenta se tipareste.
"""
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, salarii_contare as _sc  # noqa: E402

LUNI = ((2026, 4), (2026, 5), (2026, 6), (2026, 7), (2026, 8))


def scheme_cu_salariati(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT schema_name FROM public.tenants WHERE activ ORDER BY schema_name")
        out = []
        for (s,) in cur.fetchall():
            try:
                cur.execute("SELECT count(*) FROM %s.salariati" % s)
                if cur.fetchone()[0]:
                    out.append(s)
            except Exception:
                conn.rollback()
    return out


def scrieri(conn):
    """Totalul de inserari/actualizari/stergeri, pe toate schemele. Instantaneu, nu delta."""
    with conn.cursor() as cur:
        cur.execute("SELECT coalesce(sum(n_tup_ins), 0), coalesce(sum(n_tup_upd), 0), "
                    "coalesce(sum(n_tup_del), 0) FROM pg_stat_user_tables")
        return cur.fetchone()


def nota_forma_veche(conn, schema, an, luna):
    """Forma de dinainte de R34: cele patru pozitii RECALCULATE prin calcul_salariu.

    Copie deliberata a codului scos din `note_lunare` — vezi antetul pentru de ce."""
    from core import d112 as _d112, salarizare as _sz, beneficii_api as _ben
    from datetime import date as _dt
    _prof, salariati = _d112.pull(conn, schema, an, luna)
    ref = _dt(an, luna, 1)
    agg = {}
    cadou_total = sum(_ben.lista_luna(conn, schema, an, luna, "cadou").values())
    if cadou_total > 0:
        agg[("642", "5328")] = agg.get(("642", "5328"), Decimal("0")) + _sc._d(cadou_total)
    for s in salariati:
        calc = _sz.calcul_salariu(
            (s.get("brut_lucrat") if s.get("brut_lucrat") is not None else s.get("brut")) or 0,
            persoane=s.get("persoane_intretinere") or 0, la_data=ref,
            norma_intreaga=not s.get("part_time"),
            venit_brut_total=float(s.get("brut") or 0),
            sub_26=_sz.sub_26_la(s.get("data_nastere"), ref),
            copii_scoala=(int(s.get("copii_scolarizati") or 0) if s.get("declaratie_copii") else 0),
            declaratie_copii=bool(s.get("declaratie_copii")),
            data_angajare=s.get("data_angajare"),
            data_incetare=s.get("data_incetare"))
        for n in _sz.monografie_salariu(calc):
            k = (n["debit"], n["credit"])
            agg[k] = agg.get(k, Decimal("0")) + _sc._d(n["suma"])
    return [(d, c, s) for (d, c), s in sorted(agg.items()) if s > 0], len(salariati)


def masoara(conn, schema, an, luna, forma):
    """(divergente, nr_salariati) sau (None, motiv). Fiecare pereche isi poarta esecul.

    `search_path` se pune pe schema fiindca o parte din lantul de calcul interogheaza tabele
    NECALIFICATE (`core/pontaj.py`: „SELECT data_angajare FROM salariati"). In aplicatie il pun
    rutele; o sonda care nu-l pune masoara doar firmele fara tichete de masa — si tocmai
    `tenant_001`, cea cu cea mai mare divergenta, are tichete. Prima forma a sondei asta a sarit
    5 perechi din 40 exact asa, si ar fi raportat un rezultat mai bun decat realitatea."""
    try:
        with conn.cursor() as cur:
            cur.execute("SET search_path TO %s, public" % schema)
        note, nr = (nota_forma_veche(conn, schema, an, luna) if forma == "veche"
                    else _sc.note_lunare(conn, schema, an, luna))
        return _sc.control_coerenta(note, conn, schema, an, luna), nr
    except Exception as e:
        conn.rollback()
        return None, "%s: %s" % (type(e).__name__, str(e)[:90])
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute("SET search_path TO public")
        except Exception:
            conn.rollback()


def ruleaza():
    db.init_pool()
    with db.get_conn() as conn:
        scheme = scheme_cu_salariati(conn)
        perechi = [(s, a, l) for s in scheme for a, l in LUNI]
        inainte = scrieri(conn)
        print("PEREGHI: %d scheme x %d luni = %d perechi" % (len(scheme), len(LUNI), len(perechi)))
        print("pg_stat_user_tables INAINTE: ins=%d upd=%d del=%d\n" % inainte)

        rezultat = {}
        for forma in ("veche", "noua"):
            div_total, perechi_cu_div, sarite = 0, [], []
            for schema, an, luna in perechi:
                div, nr = masoara(conn, schema, an, luna, forma)
                if div is None:
                    sarite.append((schema, an, luna, nr))
                    continue
                if div:
                    div_total += len(div)
                    perechi_cu_div.append((schema, an, luna, div))
            rezultat[forma] = (div_total, perechi_cu_div, sarite)
            print("FORMA %-6s: %d divergente pe %d perechi · %d perechi n-au putut fi masurate"
                  % (forma.upper(), div_total, len(perechi_cu_div), len(sarite)))
            for schema, an, luna, div in perechi_cu_div:
                for d in div:
                    print("    %s %d-%02d  %-16s cont %-5s nota %12.2f  declarat %12.2f  dif %10.2f (tol %.2f)"
                          % (schema, an, luna, d["eticheta"], d["cont"], d["nota"],
                             d["declaratie"], d["diferenta"], d["toleranta"]))
            for schema, an, luna, motiv in sarite:
                print("    SARIT %s %d-%02d — %s" % (schema, an, luna, motiv))
            print()

        dupa = scrieri(conn)
        print("pg_stat_user_tables DUPA:    ins=%d upd=%d del=%d" % dupa)
        delta = tuple(b - a for a, b in zip(inainte, dupa))
        print("DELTA scrieri: ins=%+d upd=%+d del=%+d  →  %s"
              % (delta + ("SONDA N-A SCRIS" if delta == (0, 0, 0) else "*** A SCRIS ***",)))
        return rezultat, delta


if __name__ == "__main__":
    rez, delta = ruleaza()
    v, n = rez["veche"][0], rez["noua"][0]
    print("\nVERDICT R34")
    print("  forma VECHE (dinainte de reparatie): %d divergente pe %d perechi" % (v, len(rez["veche"][1])))
    print("  forma NOUA  (cele patru din D112):   %d divergente pe %d perechi" % (n, len(rez["noua"][1])))
    if v == 0:
        print("  *** SONDA NU DISCRIMINEAZA: nici forma veche nu diverge. Masuratoarea nu spune nimic.")
    print("  scrieri in timpul masuratorii: %s" % ("ZERO" if delta == (0, 0, 0) else str(delta)))
