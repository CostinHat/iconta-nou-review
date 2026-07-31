# -*- coding: utf-8 -*-
"""Gard de PARITATE d300 <-> d394 pe TVA pe cota. Ambele se depun la ANAF pe aceeasi luna.

Masurat 31.07.2026: NU diverg - ambele folosesc factura_linii cand exista (forward, per cota)
si deduc cota invers IDENTIC din total/tva stocat cand lipsesc liniile (d300._segmente fallback,
d394.pull fallback, aceeasi formula round(tva/baza*100)). Deci sursa e comuna (liniile). Acest
gard PRINDE daca cineva schimba derivarea intr-un singur generator - atunci ar diverge si ANAF
ar primi doua declaratii inconsistente. (A2 din brief - eliminarea deducerii inverse din d300 -
ar fi gresita: d394 o face la fel; s-ar rupe paritatea, nu s-ar repara.)"""
import pytest
from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, d300, d394, duk as _duk

SCHEMA_T = "ztest_d3d9_par"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_par():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA_T)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), SCHEMA_T))
                cur.execute("SET search_path TO %s, public" % SCHEMA_T)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                            "telefon,platitor_tva,tip_decont) VALUES (1,'PROBA SRL','14399840','Str 1','Buc',"
                            "'B','6202','BCR','RO49RNCB0000000000000001','0700000000',true,'L')")
            yield conn
        finally:
            conn.rollback()


def _seed(conn):
    with conn.cursor() as cur:
        # emisa multi-cota CU linii + stocat gresit -> ambele folosesc liniile
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,"
                    "taxare_inversa) VALUES ('A1','2026-06-10','emisa','RO14399840','CLIENT',9999,8888,false) RETURNING id")
        fid = cur.fetchone()[0]
        for desc, pret, cota in [("x21", 1000, 21), ("x11", 500, 11), ("scutit", 300, 0)]:
            cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                        "VALUES (%s,%s,'buc',1,%s,%s)", (fid, desc, pret, cota))
        # emisa FARA linii (import) -> ambele deduc invers identic
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,"
                    "taxare_inversa) VALUES ('B1','2026-06-11','emisa','RO14399840','CLIENT2',1210,210,false)")


def _seed_clean(conn):
    """Date CONSISTENTE (stocat = suma liniilor) pentru proba DUK: 21%(1000)+11%(500)+scutit(300)
    -> total 2065, tva 265."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,"
                    "taxare_inversa) VALUES ('C1','2026-06-12','emisa','RO14399840','CLIENT',2065,265,false) RETURNING id")
        fid = cur.fetchone()[0]
        for desc, pret, cota in [("x21", 1000, 21), ("x11", 500, 11), ("scutit", 300, 0)]:
            cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                        "VALUES (%s,%s,'buc',1,%s,%s)", (fid, desc, pret, cota))


def _colectata_d300(r3):
    return {21: r3.R.get("R9_2", 0), 11: r3.R.get("R10_2", 0)}


def _colectata_d394(r9):
    return {c: int(round(float(r9.rezumat2[c].get("tvaL", 0)))) for c in r9.rezumat2}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_d394_aceeasi_tva_colectata_pe_cota(conn_par):
    """TVA colectata pe cota trebuie sa coincida intre d300 si d394 (aceeasi sursa = liniile)."""
    _seed(conn_par)
    p3, f3 = d300.pull(conn_par, SCHEMA_T, Perioada(2026, luna=6))
    r3 = d300.calcul_d300(p3, Perioada(2026, luna=6), f3)
    p9, f9 = d394.pull(conn_par, SCHEMA_T, 2026, 6)
    r9 = d394.calcul_d394(p9, 2026, 6, f9)
    c3, c9 = _colectata_d300(r3), _colectata_d394(r9)
    for cota in (21, 11):
        assert c3.get(cota, 0) == c9.get(cota, 0), (
            "DIVERGENTA d300 vs d394 la cota %d%%: d300=%s d394=%s" % (cota, c3.get(cota), c9.get(cota)))


@pytest.mark.skipif(not _db_ok() or not _duk.poate_valida("d300") or not _duk.poate_valida("d394"),
                    reason="DB sau DUK indisponibil")
def test_d300_si_d394_ambele_valide_duk_pe_aceeasi_luna(conn_par):
    """A4: ambele declaratii pe aceeasi luna trec DUK, totalul colectat reconciliat intre ele."""
    _seed_clean(conn_par)
    x3, _ = d300.genereaza(conn_par, SCHEMA_T, Perioada(2026, luna=6))
    x9, _ = d394.genereaza(conn_par, SCHEMA_T, 2026, 6)
    assert _duk.valideaza(x3, "d300", an=2026, luna=6)["stare"] == "valid"
    assert _duk.valideaza(x9, "d394", an=2026, luna=6)["stare"] == "valid"
    p3, f3 = d300.pull(conn_par, SCHEMA_T, Perioada(2026, luna=6))
    r3 = d300.calcul_d300(p3, Perioada(2026, luna=6), f3)
    p9, f9 = d394.pull(conn_par, SCHEMA_T, 2026, 6)
    r9 = d394.calcul_d394(p9, 2026, 6, f9)
    tot3 = sum(_colectata_d300(r3).values())
    tot9 = sum(_colectata_d394(r9).values())
    assert tot3 == tot9, "TVA colectata totala nereconciliata: d300=%s d394=%s" % (tot3, tot9)


# cota taxabila -> randul de TVA colectata din d300
_ROW = {21: "R9_2", 11: "R10_2", 9: "R11_2"}


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_d394_aceeasi_clasificare_cote_taxabile(conn_par):
    """Clasificare, nu doar sume: setul de cote TAXABILE (>0) coincide intre d300 si d394 pe
    facturi COMPLETE (cu linii).

    LIMITA DOCUMENTATA (nu bug, cerinta ANAF): taxarea inversa PRIMITA fara linii (tva=0) diverge
    PRIN SPEC. d300 NU proceseaza reverse charge din facturi - randurile rd.12 se introduc MANUAL
    de contabil (care stie cota bunului); calea auto pune achizitia neclasificabila in "alte".
    d394 o auto-clasifica tip C la cota standard a perioadei (semnalata ca PRESUPUNERE in
    avertismente, d394.pull). Cele doua declaratii au structuri diferite pentru aceeasi operatiune;
    alinierea ar cere ca d300 sa auto-proceseze reverse charge - feature, si ar avea nevoie de cota
    bunului (absenta pe o factura fara linii). Deci gardul acopera clasificarea pe date COMPLETE,
    NU cazul reverse-charge-fara-linii."""
    _seed(conn_par)
    p3, f3 = d300.pull(conn_par, SCHEMA_T, Perioada(2026, luna=6))
    r3 = d300.calcul_d300(p3, Perioada(2026, luna=6), f3)
    p9, f9 = d394.pull(conn_par, SCHEMA_T, 2026, 6)
    r9 = d394.calcul_d394(p9, 2026, 6, f9)
    cote_d300 = {c for c, row in _ROW.items() if r3.R.get(row)}
    cote_d394 = set(r9.rezumat2)
    assert cote_d300 == cote_d394, (
        "CLASIFICARE divergenta d300=%s d394=%s" % (sorted(cote_d300), sorted(cote_d394)))
