# -*- coding: utf-8 -*-
"""PROBĂ PE PORTOFOLIU — lot 19, top-5 defecte (02.10.2026). INVALID pe codul vechi, VALID pe cel nou.

Rulare (aceleași date, două rădăcini de cod):
    python frontend_test/proba_lot19_top5.py <radacina_cod>      # ex. un worktree pe HEAD-ul vechi, apoi arborele
Firmele de test ale portofoliului (F1 tenant_049 plătitor lunar, F2 tenant_050 profit, F3 tenant_051 NEplătitor) din
baza de producție. TOTUL într-o singură tranzacție ANULATĂ la final; `observare.alerteaza` neutralizat (fără alerte reale).
Datele introduse (rapoarte Z, angajare/CFP, cesiune, dividende) sunt ale probei, construite pe firmă.
"""
import os
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal

RAD = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, RAD)
os.chdir(RAD)

from core import db, observare  # noqa: E402
from core.common import Perioada  # noqa: E402

observare.alerteaza = lambda *a, **k: None
NOU = os.path.exists(os.path.join(RAD, "core", "corpus_continut.py"))
print("=== COD: %s (%s)" % (RAD, "NOU" if NOU else "VECHI"))


def duk(xml, tip, an, luna=None):
    from core import duk as _d
    r = _d.valideaza(xml, tip, an=an, luna=luna)
    return "%s%s" % (r["stare"], (" — " + " | ".join(l.strip() for l in (r.get("erori") or "").splitlines() if l.strip())[:300]) if r.get("erori") else "")


def sp(cur, s):
    cur.execute("SET search_path TO %s, public" % s)


db.init_pool()
with db.get_conn() as conn:
    cur = conn.cursor()
    try:
        # ---- 4a D216 pe 2026 -------------------------------------------------------------------------------------
        from core import d216
        m = {"nume": "POPESCU ION", "cif": "1960101410019", "domiciliuFiscal": "JUD BOTOSANI", "nume_intocmit": "IONESCU",
             "functia_intocmit": "CONTABIL", "d_rec": 0,
             "imobile": [{"judet_imobil": "BOTOSANI", "cod_judet_imobil": "7", "localitate_imobil": "BOTOSANI",
                          "cod_localitate_imobil": "1", "strada_imobil": "STR PRIMAVERII", "cod_strada_imobil": "1",
                          "nr_cadastral": "12345", "valoare_impozabila_imobil": 3000000, "cota": 100, "plafon_imobil": 2500000}],
             "mobile": [{"an_detinere": 2025, "niv": 5, "valoare_impozabila_mobil": 400000, "plafon_mobil": 375000}]}
        x, r = d216.genereaza(None, None, Perioada(2026, luna=12), m)
        print("[4a D216 2026] impozit_imobile=%s impozit_mobile=%s -> DUK %s" % (r.impozit_imobile, r.impozit_mobile, duk(x, "d216", 2026, 12)))

        # ---- 4b D300 F1 sept 2026 cu un raport Z validat -----------------------------------------------------------
        S = "tenant_049"
        sp(cur, S)
        cur.execute("INSERT INTO inregistrari (data, numar, descriere, sursa, status) VALUES "
                    "('2026-09-25','Z-PROBA19-0001','Raport Z proba lot 19','horeca_z','validata') RETURNING id")
        iz = cur.fetchone()[0]
        for d, c, s_ in (("5311", "707", 1321), ("707", "4427", 221)):
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (iz, d, c, s_))
        cur.execute("SELECT to_regclass('rapoarte_z_cote')")
        if cur.fetchone()[0]:
            cur.execute("INSERT INTO rapoarte_z_cote (inregistrare_id, cota, baza, tva) VALUES (%s,21,1000,210),(%s,11,100,11)", (iz, iz))
        from core import d300
        try:
            x, r = d300.genereaza(conn, S, Perioada(2026, luna=9))
            cur.execute("SELECT COALESCE(SUM(l.suma),0) FROM inregistrari_linii l JOIN inregistrari i ON i.id=l.inregistrare_id "
                        "WHERE i.status='validata' AND l.cont_credit='4427' AND i.data >= '2026-09-01' AND i.data < '2026-10-01'")
            c4427 = Decimal(cur.fetchone()[0])
            dec = r.R.get("R9_2", 0) + r.R.get("R10_2", 0) + r.R.get("R11_2", 0)
            print("[4b D300 F1 09.2026] R9=%s/%s R10=%s/%s | TVA colectată în decont %s vs credit 4427 în evidență %s -> %s | DUK %s"
                  % (r.R.get("R9_1"), r.R.get("R9_2"), r.R.get("R10_1"), r.R.get("R10_2"), dec, c4427,
                     "COINCID" if abs(Decimal(dec) - c4427) <= 1 else "LIPSĂ %s lei" % (c4427 - Decimal(dec)), duk(x, "d300", 2026, 9)))
        except Exception as e:
            print("[4b D300 F1 09.2026] REFUZ: %s" % e)
        cur.execute("SAVEPOINT dupa_d300")

        # ---- 4c D112 F1 sept 2026: Popescu angajat pe 16.09, Georgescu în CFP 8-12.09 -----------------------------
        cur.execute("UPDATE salariati SET data_angajare='2026-09-16' WHERE id=2")
        cur.execute("SELECT to_regclass('suspendari_contract')")
        if cur.fetchone()[0]:
            cur.execute("INSERT INTO suspendari_contract (salariat_id, data_inceput, data_sfarsit, tip) VALUES (3,'2026-09-08','2026-09-12','cfp')")
        from core import d112
        x, _av = d112.genereaza(conn, S, 2026, 9)
        for a in ET.fromstring(x).iter():
            if a.tag.split("}")[-1] == "asigurat":
                b1 = next(s for s in a if s.tag.split("}")[-1] == "asiguratB1")
                print("[4c D112 F1 09.2026] %-10s B1_sal1=%s B1_sal2=%s B1_15=%s B1_7=%s" % (
                    a.get("numeAsig"), b1.get("B1_sal1"), b1.get("B1_sal2"), b1.get("B1_15"), b1.get("B1_7", "-")))
        print("[4c D112 F1 09.2026] DUK %s" % duk(x, "d112", 2026, 9))

        # ---- 4d F3 neplătitor: propunerea cotei, emiterea cu 21%, PDF-ul -----------------------------------------
        S = "tenant_051"
        sp(cur, S)
        import main  # noqa
        print("[4d F3] ProdusPotrivesteIn fără câmp -> platitor_tva=%r (vechiul implicit trimitea 21%% unui neplătitor)"
              % getattr(main.ProdusPotrivesteIn(denumire="Consultanta"), "platitor_tva", "citit din profil"))
        from core import facturi_api, factura_pdf, firma_profil_api
        cur.execute("SAVEPOINT f3")
        try:
            rr = facturi_api.creeaza_factura(conn, "PROBA19-1", "2026-07-10", "emisa",
                                             [{"descriere": "Consultanta", "cantitate": 1, "pret_unitar": 1000, "cota_tva": 21,
                                               "cont_venit": "704", "um": "buc"}], tert_nume="Client PF", tert_pf=True)
            print("[4d F3] factură emisă cu TVA 21%% la neplătitor: ACCEPTATĂ (tva=%s)" % rr.get("tva"))
        except ValueError as e:
            print("[4d F3] factură emisă cu TVA 21%% la neplătitor: REFUZATĂ — %s" % e)
        cur.execute("ROLLBACK TO SAVEPOINT f3")
        import io
        from pypdf import PdfReader
        prof = firma_profil_api.citeste_profil(conn)
        pdf = factura_pdf.genereaza_pdf(prof, {"numar": "PROBA19-2", "directie": "emisa", "data_emitere": "2026-07-10",
                                               "moneda": "RON", "tert_nume": "Client PF", "total": 1000, "tva": 0,
                                               "linii": [{"descriere": "Consultanta", "cantitate": 1, "um": "buc",
                                                          "pret_unitar": 1000, "cota_tva": 0}]})
        t = " ".join(" ".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(pdf)).pages).split())
        print("[4d F3] PDF factură 0%%: mențiunea taxei %s; trimiterea la art. 310 %s" % (
            "PREZENTĂ ('TVA 0%')" if "TVA 0" in t else "absentă", "PREZENTĂ" if "art. 310" in t else "ABSENTĂ"))

        # ---- 4e F2 dividende 2026 cu o cesiune la 01.04 ----------------------------------------------------------
        S = "tenant_050"
        sp(cur, S)
        cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('ASOCIAT B','2900202410026',100)")
        cur.execute("INSERT INTO asociati_istoric (cnp, nume, cota, valabil_pana_la) VALUES ('1900101410011','ASOCIAT A',100,'2026-03-31')")
        for data, d, c, s_ in (("2026-02-15", "117", "457", 10000), ("2026-05-10", "457", "5121", 10000),
                               ("2026-06-20", "117", "457", 5000), ("2026-07-01", "457", "5121", 5000)):
            cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES (%s,'dividende proba','validata') RETURNING id", (data,))
            nid = cur.fetchone()[0]
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)", (nid, d, c, s_))
        from core import d205
        x, r = d205.genereaza(conn, S, Perioada(2026))
        for b in r.beneficiari:
            print("[4e D205 F2 2026] %-10s baza1=%s imp1=%s divid_D=%s" % (b.nume1, b.baza1, b.imp1, b.divid_d))
        print("[4e D205 F2 2026] DUK %s" % duk(x, "d205", 2026))
    finally:
        conn.rollback()
        print("=== ROLLBACK (nimic scris)")
