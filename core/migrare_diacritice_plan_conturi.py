# -*- coding: utf-8 -*-
"""core/migrare_diacritice_plan_conturi.py — diacritice pe numele de cont din plan_conturi (tenanti EXISTENTI).

Balanta PDF (core/documente_api.py) ia numele de cont din plan_conturi (DB); tenantii existenti au numele
seedate ASCII din tenant_template.sql -> PDF fara diacritice ("TVA colectata", "Venituri din vanzarea
marfurilor"). Fontul REDA diacritice (titlul balantei le are). Aceasta migrare aduce numele la forma cu
diacritice din core.plan_omfp.PLAN_OMFP, DOAR unde forma curenta e EXACT ASCII-ul numelui diacritic
(invariant strict: strip_diacritice(nou)==curent) - nu atinge nume personalizate de utilizator.
Idempotent. Tenanti NOI: deja acoperiti de tenant_template.sql. Plimbarea M2 14.08.2026, constatarea 17."""
from core import db
from core.plan_omfp import PLAN_OMFP

_STRIP = str.maketrans("ăâîșțĂÂÎȘȚşţ", "aaistAAISTst")


def _strip(s):
    return (s or "").translate(_STRIP)


def aplica(conn, schema):
    if not db.schema_valida(schema):
        raise ValueError("schema invalida: %r" % schema)
    n = 0
    with conn.cursor() as cur:
        cur.execute("SET search_path TO %s, public" % schema)
        cur.execute("SELECT simbol, denumire FROM plan_conturi")
        for cont, den in cur.fetchall():  # cont = simbol
            nou = PLAN_OMFP.get(str(cont))
            if not nou or nou == den:
                continue
            # doar diacritice: forma curenta trebuie sa fie EXACT ASCII-ul numelui diacritic
            if _strip(nou) == den:
                cur.execute("UPDATE plan_conturi SET denumire=%s WHERE simbol=%s", (nou, cont))
                n += 1
    return n


def _main():
    db.init_pool()
    with db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT schema_name FROM information_schema.schemata "
                        "WHERE schema_name ~ '^tenant_[0-9]+$' ORDER BY schema_name")
            scheme = [r[0] for r in cur.fetchall()]
    tot = 0
    for s in scheme:
        try:
            with db.get_conn() as conn:
                k = aplica(conn, s)
            tot += k
            print("  OK  %s (%d nume diacriticizate)" % (s, k))
        except Exception as e:
            print("  ESEC %s: %s" % (s, e))
            raise SystemExit(1)
    print("plan_conturi diacritice: %d actualizari pe %d scheme" % (tot, len(scheme)))


if __name__ == "__main__":
    _main()
