# -*- coding: utf-8 -*-
"""GARD D394 (16.08.2026, campanie rețeta D300) — doua neconformitati reparate:

(1) nrFact la FACTURA MULTI-COTA. OPANAF 2194/2025 pct.C.5 (anaf_surse/opanaf_2194_2025_d394.txt:1221-1227):
    "in situatia in care in cuprinsul unei facturi ... exista operatiuni cu cote de TVA diferite, la rubrica
    «numar de facturi» se vor inscrie: valoarea 1 in dreptul operatiunii cu valoarea cea mai mare a TVA si
    valoarea 0 pentru restul; daca valoarea TVA este aceeasi ... la cota de TVA cea mai mare." COD VECHI: fiecare
    split pe_cota primea nrFact=1 -> o factura cu 2 cote raporta nrFact=2 (supra-numarare tacuta). FIX: pull()
    marcheaza nrFact=1 doar pe cota cu TVA max (dep. cota max), 0 pe rest; calcul_d394 respecta f["nrFact"].

(2) IMPLICITE FABRICATE TACUT (regula 4): denR/functie_reprez/calitate_intocmit="ADMINISTRATOR", judP="40"
    (Bucuresti) cand lipsesc din profil. COD VECHI: le emitea TACIT. FIX: implicitul se emite tot (DUK cere
    campul completat) DAR ANUNTAT prin avertisment vizibil.

Aserturi/markere ASCII. Numerele verificabile (21% x baza).
"""
import pytest
from decimal import Decimal

from core.common import Perioada
from core import d394
from core.d394 import calcul_d394, build_xml


def _prof(**kw):
    p = {"cui": "14399840", "nume": "PROBA SRL", "caen": "4711", "tip_decont": "L",
         "adresa": "Str 1", "judet": "B", "reprezentant_nume": "POPESCU ION",
         "reprezentant_functie": "ADMINISTRATOR", "declarant_functie": "CONTABIL"}
    p.update(kw)
    return p


# ============================================================
#  (1) nrFact — calea PURA respecta f["nrFact"] per intrare
# ============================================================
def test_calcul_respecta_nrfact_din_factura_multicota():
    """Doua linii ale ACELEIASI facturi (cota 21 nrFact=1, cota 9 nrFact=0) catre acelasi client RO ->
    op1(21) nr=1, op1(9) nr=0. RED pre-fix: calcul_d394 punea literal 1 -> op1(9) ar fi avut nr=1."""
    date = {"facturi": [
        {"cui": "RO14399840", "nume": "CLIENT", "directie": "emisa", "platitor_tva": True,
         "cota": 21, "baza": Decimal(1000), "tva": Decimal(210), "nrFact": 1},
        {"cui": "RO14399840", "nume": "CLIENT", "directie": "emisa", "platitor_tva": True,
         "cota": 9, "baza": Decimal(500), "tva": Decimal(45), "nrFact": 0},
    ]}
    res = calcul_d394(_prof(), Perioada(2026, luna=6), date)
    nr_pe_cota = {k[2]: v[0] for k, v in res.op1.items()}
    assert nr_pe_cota.get(21) == 1, "cota cu TVA max primeste nrFact=1"
    assert nr_pe_cota.get(9) == 0, "restul cotelor primesc nrFact=0"
    assert sum(v[0] for v in res.op1.values()) == 1, "factura 2-cote = 1 în total, nu 2"


def test_calcul_nrfact_default_1_fara_cheie():
    """CONTROL backward-compat: o intrare fara cheia nrFact -> f.get('nrFact',1)=1 (comportament vechi
    pentru apelanti cu o singura linie pe factura)."""
    date = {"facturi": [
        {"cui": "RO14399840", "nume": "CLIENT", "directie": "emisa", "platitor_tva": True,
         "cota": 21, "baza": Decimal(1000), "tva": Decimal(210)},
    ]}
    res = calcul_d394(_prof(), Perioada(2026, luna=6), date)
    assert sum(v[0] for v in res.op1.values()) == 1


# ============================================================
#  (2) Implicite fabricate -> AVERTISMENT (nu tacut)
# ============================================================
def test_reprezentant_lipsa_avertisment_nu_tacut():
    """Profil fara reprezentant/declarant -> denR/functie emise implicit 'ADMINISTRATOR' DAR cu avertisment.
    RED pre-fix: 'ADMINISTRATOR' emis tacut, fara niciun avertisment."""
    prof = _prof(reprezentant_nume=None, reprezentant_functie=None, declarant_functie=None,
                 declarant_nume=None)
    res = calcul_d394(prof, Perioada(2026, luna=6), {"facturi": []})
    build_xml(res)
    txt = " ".join(res.avertismente)
    assert "reprezentantului (denR) lipsește" in txt, "lipsă denR trebuie ANUNTATA"
    assert "calitatea întocmitorului" in txt, "lipsă calitate_intocmit trebuie ANUNTATA"


def test_reprezentant_prezent_fara_avertisment():
    """CONTROL: profil cu reprezentant complet -> niciun avertisment de implicit fabricat."""
    res = calcul_d394(_prof(), Perioada(2026, luna=6), {"facturi": []})
    build_xml(res)
    txt = " ".join(res.avertismente)
    assert "emis implicit" not in txt and "judP emis implicit" not in txt


def test_judet_lipsa_partener_neinreg_avertisment():
    """Partener NEINREGISTRAT (tip 2) fara cod + profil FARA judet -> judP emis implicit '40' DAR anuntat.
    RED pre-fix: judP='40' (Bucuresti) emis tacit."""
    prof = _prof(judet=None)
    manual = {"operatiuni": [{"tip": "LS", "tip_partener": 2, "cuiP": "", "denP": "PF ANONIM",
                              "cota": 0, "baza": Decimal(100)}]}
    res = calcul_d394(prof, Perioada(2026, luna=6), {"facturi": []}, manual)
    xml = build_xml(res)
    assert 'judP="40"' in xml, "judP implicit încă emis (DUK cere campul)"
    assert any("judP emis implicit" in a for a in res.avertismente), "implicitul judP trebuie ANUNTAT"


# ============================================================
#  DB: proba pe date reale (pull) + zero-base + DUK
# ============================================================
from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d394_nrfact"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _schema(cur, facturi_sql):
    cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
    cur.execute(_tp.parametrizeaza_template(
        open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
    cur.execute("SET search_path TO %s, public" % _SCHEMA)
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,"
                "platitor_tva,tip_decont) VALUES (1,'PROBA SRL','14399840','Str 1','Buc','B','4711','BCR',"
                "'RO49RNCB0000000000000001','0700000000',true,'L')")
    for s in facturi_sql:
        cur.execute(s)


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pull_factura_multicota_nrfact_1_pe_tva_max(conn):
    """O SINGURA factura emisa cu 2 linii (1000@21% + 500@9%) -> pull marcheaza nrFact=1 pe cota 21
    (TVA 210 > 45), 0 pe cota 9. rezumat2 propaga: nrFacturiL[21]=1, nrFacturiL[9]=0.
    RED pre-fix: ambele split-uri nrFact=1 -> total 2."""
    with conn.cursor() as cur:
        _schema(cur, [
            "INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,taxare_inversa) "
            "VALUES ('F1','2026-06-05','emisa','RO14399840','CLIENT',1755,255,false) RETURNING id",
        ])
        f1 = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,'m21','buc',1,1000,21),(%s,'m9','buc',1,500,9)", (f1, f1))
        _prof_db, date = d394.pull(conn, _SCHEMA, Perioada(2026, luna=6))
    nr = {f["cota"]: f["nrFact"] for f in date["facturi"]}
    assert nr == {21: 1, 9: 0}, "nrFact 1 pe cota cu TVA max (21), 0 pe rest; găsit %r" % nr
    res = calcul_d394(_prof(), Perioada(2026, luna=6), date)
    assert res.rezumat2[21]["nrFacturiL"] == 1
    assert res.rezumat2[9]["nrFacturiL"] == 0
    assert sum(v[0] for v in res.op1.values()) == 1, "o factura = un singur nrFact în total"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pull_multicota_tva_egal_alege_cota_mare(conn):
    """La TVA EGAL intre cote (19% x 100 = 19 = 20% x 95), regula cere numerotare la cota CEA MAI MARE (20)."""
    with conn.cursor() as cur:
        _schema(cur, [
            "INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,taxare_inversa) "
            "VALUES ('F2','2026-06-06','emisa','RO14399840','CLIENT',233,38,false) RETURNING id",
        ])
        f1 = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,'a','buc',1,100,19),(%s,'b','buc',1,95,20)", (f1, f1))
        _prof_db, date = d394.pull(conn, _SCHEMA, Perioada(2026, luna=6))
    nr = {f["cota"]: f["nrFact"] for f in date["facturi"]}
    assert nr == {19: 0, 20: 1}, "TVA egal -> nrFact=1 la cota mai mare (20); găsit %r" % nr


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nrfacturi_e_numarul_real_nu_spanul_seriei(conn):
    """3 facturi emise NECONTIGUE (nr 45,46,50) -> nrFacturi=3, NU spanul 1+(50-45)=6.
    RED pre-fix: informatii.nrFacturi = span (6). serieFacturi pastreaza plaja 45-50."""
    with conn.cursor() as cur:
        _schema(cur, [])
        for nr, tot, tva in (("A45", 1210, 210), ("A46", 1210, 210), ("A50", 1210, 210)):
            cur.execute("INSERT INTO facturi (serie,numar,data_emitere,directie,tert_cui,tert_nume,"
                        "total,tva,taxare_inversa) VALUES ('A',%s,'2026-06-05','emisa','RO14399840',"
                        "'CLIENT',%s,%s,false) RETURNING id", (nr, tot, tva))
            fid = cur.fetchone()[0]
            cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                        "VALUES (%s,'m','buc',1,1000,21)", (fid,))
        _prof_db, date = d394.pull(conn, _SCHEMA, Perioada(2026, luna=6))
    assert date["nr_facturi"] == 3, "număr REAL de facturi emise = 3; găsit %r" % date["nr_facturi"]
    res = calcul_d394(_prof(), Perioada(2026, luna=6), date)
    assert res.informatii["nrFacturi"] == 3, "nrFacturi = număr (3), NU spanul seriei (6)"
    # serieFacturi pastreaza plaja completa 45-50 (tip 1 si tip 2)
    plaje = {(s["nrI"], s["nrF"]) for s in res.serii}
    assert (45, 50) in plaje, "serieFacturi pastreaza plaja min-max 45-50: %r" % plaje


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_multicota_ramane_duk_valid(conn):
    """Proba DUK: o D394 cu factura multi-cota (nrFact=0 pe o linie op1) e valida structural la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d394"):
        pytest.skip("DUK d394 indisponibil")
    with conn.cursor() as cur:
        _schema(cur, [
            "INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,total,tva,taxare_inversa) "
            "VALUES ('F1','2026-06-05','emisa','RO14399840','CLIENT',1755,255,false) RETURNING id",
        ])
        f1 = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,'m21','buc',1,1000,21),(%s,'m9','buc',1,500,9)", (f1, f1))
        xml, res = d394.genereaza(conn, _SCHEMA, Perioada(2026, luna=6))
    rez = duk.valideaza(xml, "d394", an=2026, luna=6)
    assert rez["stare"] == "valid", "D394 multi-cota trebuie să fie DUK-valid; rez=%r" % rez
