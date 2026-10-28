# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 696] Stocuri arăta 8.983,74 față de 371 = 6.272,38 (diferență 2.711,36, nesemnalată): fereastra număra mișcările
din ciorne. Acum arată stocul VALIDAT (cel care se potrivește cu balanța), ciornele separat și reconcilierea cu 371 (comanda Costin 14.1,
verbatim: „Fereastra arată stocul validat (egal cu 371, cu 378/4428 la global-valoric) și separat ce e în ciornă, cu reconcilierea față
de balanță (aceeași regulă ca 176/R36).”) + gestiunea articolului, ca două rânduri cu aceeași denumire să se deosebească.
Regula: o mișcare e VALIDATĂ dacă nota ei (sau o notă a documentului ei) e validată (`stocuri_anulare.IN_EVIDENTA`), ciornă dacă are note,
dar niciuna validată, fără notă dacă n-are nicio notă (soldul preluat la migrare) — aceasta din urmă face parte din stocul validat
(e în soldul de deschidere al lui 371). Schemă efemeră din template, ștearsă la ieșire.
MUTAȚII (în fiecare test): `clasa_miscarilor` care numără ciornele ca validate; reconcilierea fără soldul de preluare.
"""
import datetime
import io
from decimal import Decimal as D

import pytest

from core import db as _db, stocuri_cv_api as cv, tenant_provisioning as _tprov

SCH = "efemer_lot14_stoc"
ZI = datetime.date(2026, 10, 5)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _document(conn, numar, status, suma):
    """Factură primită cu nota ei de recepție 371 = 401 (`suma` lei), în starea dată (`validata` | `ciorna`)."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, serie, data_emitere, directie, total, tva, tert_nume, tert_cui, status, tip) "
                    "VALUES (%s, 'F', %s, 'primita', %s, 0, 'FURNIZOR SRL', 'RO14399840', 'primita', 'factura') RETURNING id",
                    (numar, ZI, suma))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari (data, status, sursa, descriere, document_ref, factura_id) VALUES (%s, %s, 'facturi', 'Recepție', "
                    "%s, %s) RETURNING id", (ZI, status, "Factură F nr. " + numar, fid))
        nid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '371', '401', %s)", (nid, suma))
    return fid, nid


def _intrare(conn, den, cant, pret, factura_id=None, locatie=None, um="kg"):
    return cv.intrare(conn, SCH, {"denumire": den, "um": um, "data": ZI.isoformat(), "cantitate": cant, "pret_unitar": pret,
                                  "locatie": locatie}, factura_id=factura_id)


def _date(conn):
    """Grâu: 200 kg validat (400 lei, gestiunea „Depozit 1”), 10 kg în ciornă (20 lei, „Depozit 2”); soldul preluat: Orz 5 kg × 2 = 10 lei, fără notă,
    cu soldul lui 371 = 10 din balanța de deschidere."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES ('371', 'Mărfuri', 10, 0, %s)",
                    (datetime.date(2026, 9, 30),))
    f1, _n1 = _document(conn, "1", "validata", 400)
    f2, n2 = _document(conn, "2", "ciorna", 20)
    g1 = _intrare(conn, "Grâu", 200, 2, f1, "Depozit 1")
    _intrare(conn, "Grâu", 10, 2, f2, "Depozit 2")
    _intrare(conn, "Orz", 5, 2)
    return n2, g1["articol_id"]


def _art(lista, den):
    return next(a for a in lista if a["denumire"] == den)


def test_stocul_validat_separa_ciorna_si_se_potriveste_cu_371(conn):
    """696: Grâu = 200 kg validat (400,00 lei) + 10 kg în ciornă (20,00 lei); Orz = 5 kg preluat, fără notă, intră în validat. Reconcilierea 371: soldul
    contabil = 10 (preluat) + 400 (nota validată) = 410,00 = Σ valoare validată 410,00 — diferență 0; ciornele (20,00) sunt separat. Fără
    regula, stocul arătat era 430,00 (cu ciorna) față de 410,00 în balanță. MUTAȚIE: ciorna numărată ca validată -> pică."""
    _date(conn)
    lista = cv.articole(conn, SCH)
    g, o = _art(lista, "Grâu"), _art(lista, "Orz")
    assert (g["stoc"], g["valoare"]) == ("210.000", "420.00"), g                                   # fișa întreagă, cu ciorna
    assert (g["stoc_validat"], g["valoare_validata"], g["valoare_ciorna"], g["miscari_ciorna"]) == ("200.000", "400.00", "20.00", 1), g
    assert (o["stoc_validat"], o["valoare_validata"], o["valoare_ciorna"], o["miscari_ciorna"]) == ("5.000", "10.00", "0.00", 0), o
    assert g["locatii"] == ["Depozit 1", "Depozit 2"] and o["locatii"] == []
    rec = cv.reconciliere(conn, SCH, lista)
    assert rec == [{"cont": "371", "sold_contabil": "410.00", "valoare_validata": "410.00", "valoare_ciorna": "20.00", "diferenta": "0.00",
                    "ok": True, "necalculat": 0}], rec


def test_validarea_notei_muta_ciorna_in_validat(conn):
    """Validarea notei din ciornă: stocul validat urcă cu mișcarea ei (210 kg, 420,00), ciorna dispare; reconcilierea rămâne la zero."""
    n2, _aid = _date(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (n2,))
    g = _art(cv.articole(conn, SCH), "Grâu")
    assert (g["stoc_validat"], g["valoare_validata"], g["valoare_ciorna"], g["miscari_ciorna"]) == ("210.000", "420.00", "0.00", 0), g
    assert cv.reconciliere(conn, SCH)[0]["diferenta"] == "0.00"


def test_diferenta_fata_de_balanta_se_vede_cand_nu_e_ciorna(conn):
    """O mișcare de stoc fără notă (intrare manuală de 3 kg × 2) sau o notă 371 fără mișcare nu sunt ciorne: reconcilierea o arată ca diferență
    (nota validată fără mișcare: +50,00 în balanță față de fișe). MUTAȚIE: soldul de preluare scos din `reconciliere` -> diferența ar fi 10,00 -> pică."""
    _date(conn)
    _document(conn, "3", "validata", 50)          # 371 = 401 50 lei, fără mișcare în fișă
    rec = cv.reconciliere(conn, SCH)[0]
    assert (rec["sold_contabil"], rec["valoare_validata"], rec["diferenta"], rec["ok"]) == ("460.00", "410.00", "50.00", False), rec


def test_observatii_dubluri_fractii_si_denumiri(conn):
    """696, restul: două articole cu aceeași denumire (cheie fără majuscule / diacritice) se numesc dubluri; „Cafea boabe” 2,5 buc e o cantitate
    cu zecimale la o unitate care nu se fracționează; „grau” (literă mică, fără diacritice) are forma propusă „Grâu”. Aplicația nu rescrie
    denumirea. MUTAȚII: lista UM întregi goală -> fracția nu se vede -> pică; lexiconul ignorat -> forma propusă lipsește -> pică."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES ('Grâu', 'kg', '371', '607'), ('grau', 'kg', '371', '607'), "
                    "('Cafea boabe', 'buc', '371', '607'), ('Hârtie A4', 'top', '371', '607')")
    _intrare(conn, "Cafea boabe", 2.5, 10, um="buc")
    lista = cv.articole(conn, SCH)
    cafea, grau = _art(lista, "Cafea boabe"), _art(lista, "grau")
    assert [o["fel"] for o in cafea["observatii"]] == ["fractie_um"] and "2,5" in cafea["observatii"][0]["text"], cafea["observatii"]
    assert [o["fel"] for o in grau["observatii"]] == ["litera_mica", "fara_diacritice"] and "grau → grâu" in grau["observatii"][1]["text"], grau["observatii"]
    assert _art(lista, "Grâu")["observatii"] == [] and _art(lista, "Hârtie A4")["observatii"] == []
    d = cv.dubluri(lista)
    assert [(x["denumire"].lower() in ("grâu", "grau"), len(x["articole"])) for x in d] == [(True, 2)], d
