# -*- coding: utf-8 -*-
"""PROBA PE DATE REALE a contării automate — DDD1, EEE4, FFF4.

DE CE EXISTĂ SEPARAT DE GARDĂ. `core/test_contare_automata.py` rulează pe o schemă efemeră din
`tenant_template.sql`: acolo se pot construi toate cazurile, dar niciunul nu e cel MĂSURAT. Cele trei
facturi care ar fi fost refuzate fals și cele două din clasa ambiguă de TVA la încasare trăiesc în
portofoliul real, iar întrebarea *„după reparație, chiar trec?"* se poate pune numai despre ele.

NU SCRIE NIMIC. Fiecare probă rulează într-o tranzacție care se încheie cu `ROLLBACK`, iar
`pg_stat_user_tables` se citește înainte și după: delta se tipărește. *Un ROLLBACK lasă totuși urmă
în contoarele lui `pg_stat` — inserările se numără chiar dacă se anulează —, deci delta NU e zero aici
și n-are cum să fie. Ce se dovedește cu ea e altceva: se compară numărul de rânduri din `inregistrari`
și `facturi` înainte și după, care trebuie să fie IDENTIC. Contorul spune că s-a lucrat; numărătoarea
de rânduri spune că nu s-a rămas cu nimic.*

    ./venv/bin/python scripts/proba_contare_reala.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, contare_facturi as _cf, facturi_api as _fa  # noqa: E402

# Cele trei măsurate la BLOC BBB: cheia le e ocupată de o notă de plată sau de încasare.
FALS_REFUZATE = [("tenant_004", 9), ("tenant_013", 14), ("tenant_017", 8)]
# Cele două din clasa ambiguă (furnizor la încasare + firmă în regim normal), FFF2.
AMBIGUE = [("tenant_004", 9), ("tenant_017", 8)]


def numaratori(conn, schema):
    with conn.cursor() as cur:
        cur.execute("SELECT (SELECT COUNT(*) FROM %s.facturi), "
                    "       (SELECT COUNT(*) FROM %s.inregistrari), "
                    "       (SELECT COUNT(*) FROM %s.inregistrari_linii)" % (schema, schema, schema))
        return cur.fetchone()


def ruleaza():
    db.init_pool()
    rezultat = {"ddd1": [], "fff4": [], "eee4": None, "urme": []}

    print("═══ DDD1 — cele 3 facturi pe care COUNT(*) le refuza FALS")
    for schema, fid in FALS_REFUZATE:
        with db.get_conn() as conn:
            inainte = numaratori(conn, schema)
            with _cf.cursor_dict(conn) as cur:
                legate = _cf.note_cu_cheia(cur, schema, fid)
                contare = _cf.contare_existenta(cur, schema, fid)
                try:
                    rez = _cf.contabilizeaza(cur, schema, fid, automat=False, cont_cheltuiala="371")
                    stare, cod = rez["stare"], None
                    linii = rez["linii"]
                except _cf.RefuzContare as e:
                    stare, cod, linii = "refuzata", e.cod, []
            dupa = numaratori(conn, schema)
            conn.rollback()
            dupa_rollback = numaratori(conn, schema)
        print("  %s #%d — note cu cheia: %s"
              % (schema, fid, ", ".join("#%d %s(%s)"
                                        % (n["id"], n["sursa"],
                                           "contare" if n["e_contare"] else "NU e contare")
                                        for n in legate) or "niciuna"))
        print("      contare_existenta -> %s   |   contabilizeaza -> %s%s"
              % ("#%d" % contare["id"] if contare else "None", stare,
                 " (%s)" % cod if cod else ""))
        if linii:
            print("      nota care S-AR fi scris: %s"
                  % " · ".join("%s=%s %s" % (l["debit"], l["credit"], l["suma"]) for l in linii))
        print("      randuri facturi/inregistrari/linii: %s -> %s -> dupa ROLLBACK %s"
              % (inainte, dupa, dupa_rollback))
        assert inainte == dupa_rollback, "PROBA A LASAT URMA in %s" % schema
        rezultat["ddd1"].append((schema, fid, contare is None, stare))

    print()
    print("═══ FFF4 — clasa ambigua: automatul REFUZA, ruta manuala TRECE (pe 4428)")
    for schema, fid in AMBIGUE:
        with db.get_conn() as conn:
            inainte = numaratori(conn, schema)
            with _cf.cursor_dict(conn) as cur:
                cur.execute("SELECT COALESCE(tva_la_incasare,false) AS t FROM %s.firma_profil "
                            "WHERE id=1" % schema)
                proprie = bool(cur.fetchone()["t"])
                cur.execute("SELECT COALESCE(furnizor_tva_incasare,false) AS f FROM %s.facturi "
                            "WHERE id=%%s" % schema, (fid,))
                furnizor = bool(cur.fetchone()["f"])
                try:
                    _cf.contabilizeaza(cur, schema, fid, automat=True, cont_cheltuiala="371")
                    auto = "A SCRIS — GRESIT"
                except _cf.RefuzContare as e:
                    auto = "refuzat: %s" % e.cod
                try:
                    rez = _cf.contabilizeaza(cur, schema, fid, automat=False, cont_cheltuiala="371")
                    man, linii = rez["stare"], rez["linii"]
                except _cf.RefuzContare as e:
                    man, linii = "refuzat: %s" % e.cod, []
            conn.rollback()
            dupa_rollback = numaratori(conn, schema)
        conturi = sorted({l["debit"] for l in linii} | {l["credit"] for l in linii})
        print("  %s #%d — furnizor la incasare=%s, firma proprie la incasare=%s"
              % (schema, fid, furnizor, proprie))
        print("      automat -> %s" % auto)
        print("      manual  -> %s   conturi: %s" % (man, ", ".join(conturi)))
        assert inainte == dupa_rollback, "PROBA A LASAT URMA in %s" % schema
        rezultat["fff4"].append((schema, fid, auto, man, conturi))

    print()
    print("═══ EEE4 — o factura EMISA noua produce nota AUTOMAT, in ciorna (pe o firma reala)")
    schema = "tenant_017"
    with db.get_conn(schema) as conn:
        inainte = numaratori(conn, schema)
        linii = [{"descriere": "servicii de probă", "cantitate": 1, "pret_unitar": 1000,
                  "cota_tva": 21, "cont_venit": "704"}]
        r = _fa.creeaza_factura(conn, "PROBA-EEE4", "2026-08-29", "emisa", linii,
                                tert_nume="PARTENER PROBA SRL", tert_cui="RO14399840")
        fid = r["factura_id"]
        print("  factura #%d creata — contare: %s" % (fid, r["contare"]["stare"]))
        with conn.cursor() as cur:
            cur.execute("SELECT id, status, sursa, factura_id FROM inregistrari WHERE factura_id=%s",
                        (fid,))
            nota = cur.fetchone()
        print("  nota: id=%s status=%s sursa=%s factura_id=%s" % nota)
        print("  linii: %s" % " · ".join("%s=%s %s" % (l["debit"], l["credit"], l["suma"])
                                         for l in r["contare"]["linii"]))
        # plasa o protejeaza de dublare: a doua chemare e no-op
        with _cf.cursor_dict(conn) as cur:
            # prefix gol: conexiunea e deschisă cu `db.get_conn(schema)`, deci search_path e fixat.
            a_doua = _cf.contabilizeaza(cur, "", fid, automat=False)
        print("  a doua contare (idempotenta): %s" % a_doua["stare"])
        # si stergerea o refuza motivat
        try:
            _fa.sterge_factura(conn, fid)
            sterge = "A STERS — GRESIT"
        except _cf.RefuzContare as e:
            sterge = "refuzata: %s -> iesire %s" % (e.cod, e.detalii.get("iesire"))
        print("  stergerea: %s" % sterge)
        rezultat["eee4"] = {"stare": r["contare"]["stare"], "status_nota": nota[1],
                            "sursa": nota[2], "a_doua": a_doua["stare"], "stergere": sterge}
        conn.rollback()
    with db.get_conn() as conn:
        dupa_rollback = numaratori(conn, schema)
    print("  randuri facturi/inregistrari/linii: %s -> dupa ROLLBACK %s" % (inainte, dupa_rollback))
    assert inainte == dupa_rollback, "PROBA A LASAT URMA in %s" % schema

    print()
    print("═══ VERDICT")
    ok_ddd1 = all(fara_contare and stare == "contata" for _s, _f, fara_contare, stare
                  in rezultat["ddd1"])
    print("  DDD1 — cele 3 nu mai sunt refuzate fals: %s" % ("DA" if ok_ddd1 else "NU"))
    ok_fff4 = all(a.startswith("refuzat") and m == "contata" and "4428" in c
                  for _s, _f, a, m, c in rezultat["fff4"])
    print("  FFF4 — clasa ambigua: automat refuza, manual scrie pe 4428: %s"
          % ("DA" if ok_fff4 else "NU"))
    e = rezultat["eee4"]
    ok_eee4 = (e["stare"] == "contata" and e["status_nota"] == "ciorna" and e["sursa"] == "facturi"
               and e["a_doua"] == "deja_contata")
    print("  EEE4 — emiterea produce nota in ciorna, idempotent, stergerea refuza: %s"
          % ("DA" if ok_eee4 else "NU"))
    print("  toate probele au facut ROLLBACK; numararile de randuri s-au intors identice")
    return ok_ddd1 and ok_fff4 and ok_eee4


if __name__ == "__main__":
    sys.exit(0 if ruleaza() else 1)
