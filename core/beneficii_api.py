# -*- coding: utf-8 -*-
"""core/beneficii_api.py — beneficii extrasalariale ONE-OFF pe luna (F133 Faza 2).

Tichete de vacanta (2a) si cadou (2b) NU sunt config permanent ca tichetele de masa -
sunt sume acordate intr-o luna anume. Se stocheaza per (salariat, an, luna, tip).

Tratament fiscal (verificat la sursa 2026):
- vacanta: CASS 10% + impozit 10%, FARA CAS/CAM; plafon neimpozabil 6 salarii minime/an.
- cadou (2b): sub 300 lei/eveniment = neimpozabil; peste = taxat integral ca salariu.
"""
from decimal import Decimal
from psycopg2.extras import RealDictCursor

TIPURI = ("vacanta", "cadou")


def seteaza(conn, schema, salariat_id, an, luna, tip, valoare):
    """Upsert valoarea unui beneficiu one-off (salariat/an/luna/tip). valoare 0 -> sterge randul."""
    if tip not in TIPURI:
        return {"eroare": "tip beneficiu necunoscut: %r" % tip}
    try:
        v = Decimal(str(valoare or 0))
    except Exception:
        return {"eroare": "valoare invalida"}
    if v < 0:
        return {"eroare": "valoarea nu poate fi negativa"}
    with conn.cursor() as cur:
        cur.execute(f"SELECT 1 FROM {schema}.salariati WHERE id = %s", (salariat_id,))
        if not cur.fetchone():
            return None
        if v == 0:
            cur.execute(f"DELETE FROM {schema}.beneficii_lunare "
                        f"WHERE salariat_id=%s AND an=%s AND luna=%s AND tip=%s",
                        (salariat_id, an, luna, tip))
        else:
            cur.execute(f"""INSERT INTO {schema}.beneficii_lunare (salariat_id, an, luna, tip, valoare)
                            VALUES (%s,%s,%s,%s,%s)
                            ON CONFLICT (salariat_id, an, luna, tip)
                            DO UPDATE SET valoare = EXCLUDED.valoare""",
                        (salariat_id, an, luna, tip, v))
    conn.commit()
    return {"ok": True}


def lista_luna(conn, schema, an, luna, tip):
    """{salariat_id: valoare(float)} pentru o luna si un tip (pt stat de plata)."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT salariat_id, valoare FROM {schema}.beneficii_lunare
                        WHERE an=%s AND luna=%s AND tip=%s""", (an, luna, tip))
        return {sid: float(val) for sid, val in cur.fetchall()}


def total_an(conn, schema, salariat_id, an, tip, pana_luna=12):
    """Suma acordata unui salariat intr-un an (pt plafonul anual - vacanta 6 sal.minime).
    pana_luna: cumulat pana la luna inclusiv (pt verificare la momentul acordarii)."""
    with conn.cursor() as cur:
        cur.execute(f"""SELECT COALESCE(SUM(valoare),0) FROM {schema}.beneficii_lunare
                        WHERE salariat_id=%s AND an=%s AND tip=%s AND luna<=%s""",
                    (salariat_id, an, tip, pana_luna))
        return float(cur.fetchone()[0])
