"""
core/migrare_um_borderou.py — unitatea de măsură a liniilor borderourilor de achiziție pe cont de stoc (lotul 12, deficiența C115).

DEFECTUL. Borderoul de achiziție (`uc_tenants.borderou_achizitie`, OMFP 2634/2015 cod 14-4-13) scria linia documentului și intrarea în stoc
cu UM-ul trimis de ecran sau „buc”; ecranul trimite UM-ul numai la „Articol nou…”, deci un articol ALES DIN NOMENCLATOR („grau”, în kg)
intra pe borderou cu „buc” (F1: BA-2, BA-3). Reparat în cod: UM-ul liniei e al articolului ales.

DATELE EXISTENTE (comanda Costin 11.2 pct.3: „Orice reparație acoperă și datele existente”): pe borderourile (`facturi.tip = 'borderou'`) a
căror intrare în stoc (`miscari_stoc.factura_id`) e pe un articol cu altă unitate decât „buc”, linia documentului cu denumirea articolului
și încă pe implicitul „buc” primește unitatea articolului. E o CITIRE a documentului: cantitatea, prețul, nota, fișa articolului și
declarațiile nu se ating (cantitatea din fișă e deja în unitatea articolului). O linie cu altă unitate decât „buc” (pusă de om) nu se
rescrie. Idempotentă.
Rulare: `python -m core.migrari_registru ruleaza [--productie] core/migrare_um_borderou.py`.
"""
from core import db

IMPLICIT = "buc"


def aplica(conn, schema):
    """UM-ul articolului din stoc pe liniile borderourilor scrise înainte de reparație. Întoarce {"linii": n, "borderouri": [numar]}."""
    if not db.schema_valida(schema):
        raise ValueError("schema invalidă: %r" % schema)
    with conn.cursor() as cur:
        cur.execute('UPDATE "%s".factura_linii l SET um = a.um FROM "%s".facturi f, "%s".miscari_stoc m, "%s".articole a '
                    "WHERE f.id = l.factura_id AND f.tip = 'borderou' AND m.factura_id = f.id AND a.id = m.articol_id "
                    "AND COALESCE(btrim(a.um), '') NOT IN ('', %%s) AND COALESCE(l.um, %%s) = %%s "
                    "AND lower(btrim(l.descriere)) = lower(btrim(a.denumire)) RETURNING f.numar"
                    % (schema, schema, schema, schema), (IMPLICIT, IMPLICIT, IMPLICIT))
        numere = sorted({r[0] for r in cur.fetchall()})
    return {"linii": len(numere), "borderouri": numere}


def verifica(conn, schema):
    """Nicio linie de borderou rămasă pe „buc” când articolul intrat în stoc din el are altă unitate."""
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
            if r["borderouri"]:
                print("  %s: borderourile %s au acum unitatea articolului pe linie" % (s, ", ".join(r["borderouri"])))
        except Exception as e:  # noqa: BLE001
            esec.append((s, str(e)))
    print("migrare_um_borderou: %d ok, %d esec, %d linii cu unitatea articolului" % (ok, len(esec), total))
    for s, e in esec:
        print("  ESEC %s: %s" % (s, e))
    if esec:
        raise SystemExit(1)


if __name__ == "__main__":
    _main()
