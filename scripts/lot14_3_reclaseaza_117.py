# -*- coding: utf-8 -*-
"""scripts/lot14_3_reclaseaza_117.py — D1 din comanda 14.3 (Costin, verbatim): „Da, reclasezi soldurile de preluare de pe 117 pe 1171 la firmele de test
(F1, F8 și oricare altă), printr-o notă de reclasificare 117 = 1171 la data preluării, cu document intern; nu rescrii preluarea validată.”

CE FACE. Pe fiecare firmă a cabinetului de test („Cabinet Test Sesiunea B SRL”; orice alt cabinet = refuz): dacă balanța de deschidere are sold pe sinteticul
117 și niciun analitic al lui (117x), scrie o notă validată la data preluării — 117 = 1171 pentru sold creditor (profit nerepartizat), 1171 = 117 pentru
sold debitor (pierdere neacoperită) —, cu documentul intern „Reclasificare 117 → 1171 (comanda 14.3, D1)”. Balanța de deschidere (preluarea validată) NU se
rescrie. Idempotent: o firmă care are deja nota cu acest document, sau n-are sold pe 117 / are analitic, nu se atinge.
DE CE UN SCRIPT: soldurile deja preluate sunt date ale firmelor de test; regula nouă (527.1) acționează numai la preluări noi.
Uz: ./venv/bin/python scripts/lot14_3_reclaseaza_117.py [--productie | --copie] (--proba | --scrie)
  --copie: pe copia de dovadă a firmelor de test din baza de TEST (`dovada_firme_test.py --cloneaza`), nu pe producție
  --proba: totul într-o tranzacție anulată (nimic scris), aceeași tipărire."""
import os
import sys

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAD)

CABINET_TEST = "Cabinet Test Sesiunea B SRL"
DOCUMENT = "Reclasificare 117 → 1171 (comanda 14.3, D1)"


def reclaseaza(conn, schema):
    """-> mesaj. Scrie numai în tranzacția apelantului."""
    from decimal import Decimal
    from core import db, jurnal_api
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute('SET LOCAL search_path TO "%s", public' % schema)
        cur.execute("SELECT cont, sold_debitor, sold_creditor, data_referinta FROM solduri_initiale WHERE cont = '117' OR cont LIKE '117%%'")
        rd = cur.fetchall()
        cur.execute("SELECT count(*) FROM inregistrari WHERE document_ref = %s AND status <> 'anulata'", (DOCUMENT,))
        deja = cur.fetchone()[0]
    if deja:
        return "are deja nota de reclasificare: nimic de făcut"
    sintetic = [r for r in rd if r[0] == "117"]
    if not sintetic:
        return "n-are sold de preluare pe 117: nimic de făcut"
    if any(r[0] != "117" for r in rd):
        return "are deja analitic al lui 117 în balanță: nu se atinge"
    _c, deb, cred, data = sintetic[0]
    if not data:   # balanță preluată fără dată (înainte ca data să fie cerută, C22): ultima zi a lunii dinaintea lunii efective a preluării
        import calendar
        from core import luna_preluare as _lp, repo_firma_profil as _rfp
        with conn.cursor() as cur:
            cur.execute('SET LOCAL search_path TO "%s", public' % schema)
            _f = _rfp.fapte_preluare(cur)
        luna = _lp.efectiva(_f["salvata"], _f["creat_la"], _f["data_solduri"], _f["prima_nota"])
        if not luna:
            return "balanța n-are dată, iar luna preluării nu se poate stabili: nu se atinge"
        a0, m0 = (luna.year, luna.month) if hasattr(luna, "year") else (int(luna[0]), int(luna[1]))   # `luna` = (an, lună) sau dată
        an, l = (a0, m0 - 1) if m0 > 1 else (a0 - 1, 12)
        import datetime
        data = datetime.date(an, l, calendar.monthrange(an, l)[1])
    suma = Decimal(str(cred or 0)) - Decimal(str(deb or 0))
    if suma == 0:
        return "soldul de pe 117 e zero: nimic de făcut"
    linie = {"debit": "117", "credit": "1171", "suma": str(suma)} if suma > 0 else {"debit": "1171", "credit": "117", "suma": str(-suma)}
    r = jurnal_api.creeaza(conn, schema, "Reclasificare rezultat reportat 117 → 1171", str(data)[:10], [linie], DOCUMENT)
    if not r.get("ok"):
        return "nota nu s-a putut crea: %s" % (r.get("eroare") or r)
    v = jurnal_api.valideaza(conn, schema, r["id"])
    if not v or not v.get("ok"):
        return "nota %s creată, dar nu s-a validat: %s" % (r["id"], v)
    return "nota %s validată la %s: %s = %s %s lei" % (r["id"], str(data)[:10], linie["debit"], linie["credit"], linie["suma"])


def main(argv):
    proba, scrie = "--proba" in argv, "--scrie" in argv
    if proba == scrie:
        print(__doc__)
        return 2
    if "--productie" in argv:
        from core import mediu_test
        os.environ["DATABASE_URL"] = mediu_test.dsn_productie()
    if "--copie" in argv:
        from scripts import dovada_firme_test as _dft
        env = _dft._env_test()
        _dft.tinta_de_test(env)   # refuz dacă baza nu e dovedit de test
        os.environ["DATABASE_URL"] = env["DATABASE_URL"]
    from core import db
    db.init_pool()
    with db.get_conn() as c, c.cursor() as cur:
        cur.execute("SELECT t.schema_name, t.nume, a.nume FROM public.tenants t JOIN public.accounting_firms a ON a.id = t.accounting_firm_id "
                    "WHERE a.nume = %s ORDER BY t.schema_name", (CABINET_TEST + (" — copie de dovadă" if "--copie" in argv else ""),))
        firme = cur.fetchall()
    if not firme:
        print("niciun cabinet „%s” aici: nimic de făcut" % CABINET_TEST)
        return 0
    for schema, nume, _cab in firme:
        with db.get_conn(schema) as conn:
            print("%s (%s): %s" % (schema, nume, reclaseaza(conn, schema)))
            conn.rollback() if proba else conn.commit()
    print("(proba: nimic scris)" if proba else "(scris)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
