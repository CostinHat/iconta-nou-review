# -*- coding: utf-8 -*-
"""PROBA PE DATE REALE a lanțului facturii — DDD, EEE, FFF, GGG.

DE CE EXISTĂ SEPARAT DE GARDĂ. `core/test_contare_automata.py` rulează pe o schemă efemeră din
`tenant_template.sql`. Aici totul se petrece pe o **firmă reală din portofoliu**, cu planul ei de
conturi, profilul ei fiscal și perioadele ei — adică pe lumea în care actele chiar rulează.

DE CE ÎȘI CONSTRUIEȘTE SINGURĂ FIXTURILE — și e o lecție, nu un detaliu de implementare.
**Prima formă a probei se sprijinea pe INSTANȚE ISTORICE**: cele 3 facturi a căror cheie era ocupată
de o notă de plată (`tenant_004` #9, `tenant_013` #14, `tenant_017` #8) și cele 2 din clasa ambiguă
de TVA la încasare. Erau chiar cazurile măsurate, deci proba era foarte convingătoare — **până când
R89 le-a contabilizat pe toate**. A doua zi, aceeași probă nu mai putea demonstra nimic: nu fiindcă
reparația s-ar fi stricat, ci fiindcă *lumea pe care o citea dispăruse*. **O probă care depinde de o
stare pe care munca ta o va desființa e o probă cu termen de expirare.** Acum fiecare bloc își
construiește cazul, îl exercită și îl întoarce.

NU SCRIE NIMIC. Fiecare probă rulează într-o tranzacție încheiată cu `ROLLBACK`, iar numărările de
rânduri din `facturi`, `inregistrari` și `inregistrari_linii` se citesc înainte și după: trebuie să
fie **identice**. *Contoarele din `pg_stat_user_tables` NU se întorc — o inserare anulată tot se
numără acolo —, deci ele n-ar dovedi nimic aici; numărătoarea de rânduri dovedește.*

    ./venv/bin/python scripts/proba_contare_reala.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import db, contare_facturi as _cf, facturi_api as _fa  # noqa: E402

FIRMA = "tenant_017"          # firmă reală din portofoliu, cu plan de conturi și profil fiscal
CUI_PROBA = "RO14399840"      # trece cifra de control (regula datelor de test)

# Instanțele care au PRODUS clasele, păstrate ca istorie. NU se mai citesc: R89 le-a contabilizat pe
# 29.08.2026, iar o probă care le-ar cere ar cădea pe absența lor, nu pe un defect.
ISTORIC = {
    "cheie ocupată de o notă care nu e contare": ["tenant_004 #9", "tenant_013 #14", "tenant_017 #8"],
    "furnizor la încasare + firmă în regim normal": ["tenant_004 #9", "tenant_017 #8"],
}


def numaratori(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT (SELECT COUNT(*) FROM facturi), (SELECT COUNT(*) FROM inregistrari), "
                    "       (SELECT COUNT(*) FROM inregistrari_linii)")
        return cur.fetchone()


def numaratori_noua():
    """Aceleași numărători, pe o conexiune NOUĂ. Se folosește DUPĂ `rollback`: un `SET search_path`
    e tranzacțional în PostgreSQL, deci rollback-ul îl dă înapoi odată cu datele — iar o numărătoare
    pe conexiunea veche ar cădea pe „relation does not exist" în loc să spună ceva despre rânduri."""
    with db.get_conn(FIRMA) as c:
        return numaratori(c)


def _factura(conn, numar, data, directie="emisa", **kw):
    linii = [{"descriere": "servicii de probă", "cantitate": 1, "pret_unitar": 1000,
              "cota_tva": 21, "cont_venit": "704"}]
    return _fa.creeaza_factura(conn, numar, data, directie, linii,
                               tert_nume="PARTENER PROBA SRL", tert_cui=CUI_PROBA, **kw)


def _nota_de_plata(conn, factura_id, data, linii):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, factura_id, descriere, sursa, status) "
                    "VALUES (%s,%s,'plata de probă','banca','validata') RETURNING id",
                    (data, factura_id))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, "
                        "suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s))
    return nid


def ruleaza():
    db.init_pool()
    rez = {}

    print("FIRMA: %s (reală, din portofoliu) · toate probele se încheie cu ROLLBACK\n" % FIRMA)
    print("Instanțele care au produs clasele, contabilizate de R89 pe 29.08.2026 — păstrate ca")
    print("istorie, nu ca dependență:")
    for clasa, lista in ISTORIC.items():
        print("    %-46s %s" % (clasa, ", ".join(lista)))

    # ══════════════════════════════════════════════════ DDD1
    print("\n═══ DDD1 — o notă care NU e contare nu blochează contarea")
    with db.get_conn(FIRMA) as conn:
        inainte = numaratori(conn)
        f = _factura(conn, "PROBA-DDD1", "2026-08-29", directie="primita")
        fid = f["factura_id"]
        nid = _nota_de_plata(conn, fid, "2026-08-29", [("401", "5121", 1210)])
        with _cf.cursor_dict(conn) as cur:
            existenta = _cf.contare_existenta(cur, "", fid)
            r = _cf.contabilizeaza(cur, "", fid, automat=False, cont_cheltuiala="371")
        print("  factura #%d, cu nota de PLATĂ #%d (`401=5121`) care îi poartă cheia" % (fid, nid))
        print("    contare_existenta -> %s   (COUNT(*) ar fi spus «există»)"
              % ("#%d" % existenta["id"] if existenta else "None"))
        print("    contabilizarea    -> %s : %s"
              % (r["stare"], " · ".join("%s=%s %s" % (x["debit"], x["credit"], x["suma"])
                                        for x in r["linii"])))
        # și direcția inversă: nota de contare BLOCHEAZĂ
        with _cf.cursor_dict(conn) as cur:
            a_doua = _cf.contabilizeaza(cur, "", fid, automat=False, cont_cheltuiala="371")
        print("    a doua contare    -> %s   (idempotență, nu eroare)" % a_doua["stare"])
        rez["ddd1"] = (existenta is None and r["stare"] == "contata"
                       and a_doua["stare"] == "deja_contata")
        conn.rollback()
        dupa = numaratori_noua()
    print("    rânduri facturi/înregistrări/linii: %s -> după ROLLBACK %s" % (inainte, dupa))
    assert inainte == dupa, "PROBA A LĂSAT URMĂ"

    # ══════════════════════════════════════════════════ FFF2/FFF4
    print("\n═══ FFF4 — clasa ambiguă de TVA la încasare: automatul refuză, omul contează pe 4428")
    with db.get_conn(FIRMA) as conn:
        inainte = numaratori(conn)
        f = _factura(conn, "PROBA-FFF4", "2026-08-29", directie="primita",
                     furnizor_tva_incasare=True)
        fid = f["factura_id"]
        with _cf.cursor_dict(conn) as cur:
            try:
                _cf.contabilizeaza(cur, "", fid, automat=True, cont_cheltuiala="371")
                auto = "A SCRIS — GREȘIT"
            except _cf.RefuzContare as e:
                auto = "refuzat: %s (cont %s, temei %s)" % (e.cod, e.detalii.get("cont_tva"),
                                                            e.detalii.get("temei"))
            r = _cf.contabilizeaza(cur, "", fid, automat=False, cont_cheltuiala="371")
        conturi = sorted({x["debit"] for x in r["linii"]} | {x["credit"] for x in r["linii"]})
        print("  factura #%d, furnizor la încasare, firma proprie în regim normal" % fid)
        print("    automat -> %s" % auto)
        print("    manual  -> %s, conturi: %s" % (r["stare"], ", ".join(conturi)))
        rez["fff4"] = auto.startswith("refuzat") and r["stare"] == "contata" and "4428" in conturi
        conn.rollback()
        dupa = numaratori_noua()
    print("    rânduri: %s -> după ROLLBACK %s" % (inainte, dupa))
    assert inainte == dupa, "PROBA A LĂSAT URMĂ"

    # ══════════════════════════════════════════════════ EEE
    print("\n═══ EEE4 — emiterea produce nota AUTOMAT, în ciornă; ștergerea refuză motivat")
    with db.get_conn(FIRMA) as conn:
        inainte = numaratori(conn)
        f = _factura(conn, "PROBA-EEE4", "2026-08-29")
        fid = f["factura_id"]
        with conn.cursor() as cur:
            cur.execute("SELECT id, status, sursa, factura_id, data FROM inregistrari "
                        "WHERE factura_id=%s", (fid,))
            nota = cur.fetchone()
        print("  factura #%d — contare: %s" % (fid, f["contare"]["stare"]))
        print("    nota: id=%s status=%s sursa=%s factura_id=%s data=%s" % nota)
        print("    linii: %s" % " · ".join("%s=%s %s" % (x["debit"], x["credit"], x["suma"])
                                           for x in f["contare"]["linii"]))
        try:
            _fa.sterge_factura(conn, fid)
            st = "A ȘTERS — GREȘIT"
        except _cf.RefuzContare as e:
            st = "refuz %s -> ieșire %s" % (e.cod, e.detalii.get("iesire"))
        print("    ștergerea: %s" % st)
        rez["eee4"] = (f["contare"]["stare"] == "contata" and nota[1] == "ciorna"
                       and nota[2] == "facturi" and st.startswith("refuz ARE_NOTA_DE_CONTARE"))
        conn.rollback()
        dupa = numaratori_noua()
    print("    rânduri: %s -> după ROLLBACK %s" % (inainte, dupa))
    assert inainte == dupa, "PROBA A LĂSAT URMĂ"

    # ══════════════════════════════════════════════════ GGG
    print("\n═══ GGG — dezlegarea: refuz → dezlegare → ștergere; iar contarea NU se dezleagă")
    with db.get_conn(FIRMA) as conn:
        inainte = numaratori(conn)
        f = _factura(conn, "PROBA-GGG", "2026-08-29", directie="primita")
        fid = f["factura_id"]
        nid = _nota_de_plata(conn, fid, "2026-08-29", [("401", "5121", 1210)])
        try:
            _fa.sterge_factura(conn, fid)
            pas1 = "A ȘTERS — GREȘIT"
        except _cf.RefuzContare as e:
            pas1 = "refuz %s -> ieșire %s" % (e.cod, e.detalii.get("iesire"))
        with _cf.cursor_dict(conn) as cur:
            dezlegata = _cf.dezleaga_nota(cur, "", nid)
        pas3 = "ștearsă: %s" % _fa.sterge_factura(conn, fid)["ok"]
        print("  factura #%d cu nota de plată #%d" % (fid, nid))
        print("    1. ștergere ÎNAINTE  -> %s" % pas1)
        print("    2. dezlegare         -> nota #%d ← factura %s" % (nid, dezlegata))
        print("    3. ștergere DUPĂ     -> %s" % pas3)
        # direcția inversă: o notă de CONTARE nu se dezleagă
        g = _factura(conn, "PROBA-GGG2", "2026-08-29")
        with _cf.cursor_dict(conn) as cur:
            nota_c = _cf.contare_existenta(cur, "", g["factura_id"])
            try:
                _cf.dezleaga_nota(cur, "", nota_c["id"])
                dez = "A DEZLEGAT — GREȘIT"
            except _cf.RefuzContare as e:
                dez = "refuz %s -> ieșire %s" % (e.cod, e.detalii.get("iesire"))
        print("    nota de CONTARE (#%s): %s" % (nota_c["id"], dez))
        rez["ggg"] = (pas1.startswith("refuz ARE_NOTA_LEGATA") and dezlegata == fid
                      and pas3 == "ștearsă: True" and dez.startswith("refuz E_NOTA_DE_CONTARE"))
        conn.rollback()
        dupa = numaratori_noua()
    print("    rânduri: %s -> după ROLLBACK %s" % (inainte, dupa))
    assert inainte == dupa, "PROBA A LĂSAT URMĂ"

    # ══════════════════════════════════════════════════ JJJ
    print("\n═══ JJJ2 — nota la ALTĂ dată decât emiterea, când luna emiterii e închisă")
    with db.get_conn(FIRMA) as conn:
        inainte = numaratori(conn)
        f = _factura(conn, "PROBA-JJJ", "2026-04-15")
        fid = f["factura_id"]
        with conn.cursor() as cur:                      # nota automată de la emitere iese din drum
            cur.execute("DELETE FROM inregistrari WHERE factura_id=%s", (fid,))
            cur.execute("INSERT INTO perioade_blocate (an, luna) VALUES (2026, 4) "
                        "ON CONFLICT DO NOTHING")
        with _cf.cursor_dict(conn) as cur:
            try:
                _cf.contabilizeaza(cur, "", fid, automat=False)
                fara = "A SCRIS — GREȘIT"
            except _cf.RefuzContare as e:
                fara = "refuz %s (data notei ar fi fost %s)" % (e.cod, e.detalii.get("data_nota"))
            r = _cf.contabilizeaza(cur, "", fid, automat=False, data_nota="2026-08-29",
                                   motiv_data="luna emiterii era inchisa la data descoperirii (R89)")
            cur.execute("SELECT data, descriere, factura_id FROM inregistrari WHERE id=%s",
                        (r["inregistrare_id"],))
            nota = dict(cur.fetchone())
        print("  factura #%d emisă 2026-04-15, luna 2026-04 BLOCATĂ" % fid)
        print("    fără `data_nota` -> %s" % fara)
        print("    cu `data_nota`   -> nota la %s, factura_id=%s" % (nota["data"], nota["factura_id"]))
        print("    descriere: %s" % nota["descriere"])
        rez["jjj"] = (fara.startswith("refuz LUNA_INCHISA") and str(nota["data"]) == "2026-08-29"
                      and nota["factura_id"] == fid and "2026-04-15" in nota["descriere"])
        conn.rollback()
        dupa = numaratori_noua()
    print("    rânduri: %s -> după ROLLBACK %s" % (inainte, dupa))
    assert inainte == dupa, "PROBA A LĂSAT URMĂ"

    print("\n═══ VERDICT")
    for k, et in (("ddd1", "DDD1 — nota care nu e contare nu blochează; a doua contare e no-op"),
                  ("fff4", "FFF4 — clasa ambiguă: automat refuză, manual scrie pe 4428"),
                  ("eee4", "EEE4 — emiterea produce nota în ciornă; ștergerea refuză"),
                  ("ggg",  "GGG  — refuz → dezlegare → ștergere; contarea nu se dezleagă"),
                  ("jjj",  "JJJ2 — nota la data descoperirii, cu mențiunea care o leagă")):
        print("  %s: %s" % ("DA " if rez[k] else "NU ", et))
    print("  toate probele au făcut ROLLBACK; numărările de rânduri s-au întors identice")
    return all(rez.values())


if __name__ == "__main__":
    sys.exit(0 if ruleaza() else 1)
