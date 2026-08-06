# -*- coding: utf-8 -*-
"""core/test_d300_d394_trimestrial.py — gard PERIOADA FISCALA TVA (06.08.2026, C-4 transa 2).

Apara fix-ul trimestrial (optiunea B): decontul TVA (D300/D394) al unui platitor
TRIMESTRIAL agrega TOT trimestrul (nu luna-ancora), eticheta XML (luna 3/6/9/12) ramane
separata de fereastra de date. Temei CF art.322. Vectorul fiscal (firma_profil.tip_decont)
= sursa; lipsa -> eroare (fara default tacit 'L').

MUTATIE care prinde (ambele sensuri):
  - daca pull() revine la fereastra pe luna -> D300 trimestrial pierde aprilie (test trim PICA).
  - daca fereastra devine mereu trimestru -> D300 lunar vede alta luna (test lunar PICA).
"""
import pytest
from datetime import date

from core.common import Perioada, perioada_tva_tip, fereastra_tva
from core import d300 as _d300, d394 as _d394
from core import db as _db, tenant_provisioning as _tp, duk as _duk

_SCHEMA = "test_trim_tva"
_SCHEMA_TI = "test_ti_furnizor"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


# ---- unit: vectorul fiscal (fara DB) ----

def test_perioada_tva_tip_lipsa_ridica_fara_default_L():
    with pytest.raises(ValueError):
        perioada_tva_tip({})
    with pytest.raises(ValueError):
        perioada_tva_tip({"tip_decont": ""})
    with pytest.raises(ValueError):
        perioada_tva_tip({"tip_decont": None})
    assert perioada_tva_tip({"tip_decont": "trimestrial"}) == "T"
    assert perioada_tva_tip({"tip_decont": "T"}) == "T"
    assert perioada_tva_tip({"tip_decont": "lunar"}) == "L"
    assert perioada_tva_tip({"tip_decont": "L"}) == "L"


def test_fereastra_tva_decupleaza_trimestru_de_luna():
    # Q2 (luna-eticheta 6) -> fereastra [apr, iul); lunar -> doar iunie
    assert fereastra_tva(Perioada(2026, luna=6), "T") == (date(2026, 4, 1), date(2026, 7, 1))
    assert fereastra_tva(Perioada(2026, luna=6), "L") == (date(2026, 6, 1), date(2026, 7, 1))
    assert fereastra_tva(Perioada(2026, luna=3), "T") == (date(2026, 1, 1), date(2026, 4, 1))
    assert fereastra_tva(Perioada(2026, luna=12), "T") == (date(2026, 10, 1), date(2027, 1, 1))
    assert fereastra_tva(Perioada(2026, luna=12), "A") == (date(2026, 1, 1), date(2027, 1, 1))


# ---- integrare: schema efemera, achizitie in APRILIE (prima luna Q2) ----

@pytest.fixture
def conn_trim():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                # platitor TVA TRIMESTRIAL
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                            "telefon,platitor_tva,tip_decont) VALUES (1,'TRIM SRL','14399840','Str 1','Buc',"
                            "'B','4669','BCR','RO49RNCB0000000000000001','0700000000',true,'trimestrial')")
                # achizitie in APRILIE (Q2, prima luna): 1000 net + 210 TVA @ 21% -> R22 deductibil
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,tert_platitor_tva,"
                            "total,tva,taxare_inversa) VALUES ('A1','2026-04-10','primita','RO14399840','FURNIZOR',"
                            "true,1210,210,false) RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'marfa','buc',1,1000,21)", (fid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_trimestrial_agrega_tot_trimestrul(conn_trim):
    """GARD PRINCIPAL: decont trimestrial luna=6 (Q2) include achizitia din APRILIE.
    Daca fereastra revine pe luna (iunie), R22 -> 0 si testul PICA."""
    _, res = _d300.genereaza(conn_trim, _SCHEMA, Perioada(2026, luna=6))
    assert res.R.get("R22_2", 0) == 210, "Q2 trebuie sa includa TVA deductibil din aprilie; got %r" % res.R
    assert res.R.get("R22_1", 0) == 1000


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_lunar_NU_vede_alta_luna(conn_trim):
    """MUTATIE inversa: aceeasi firma comutata pe LUNAR -> luna=6 (iunie) NU vede aprilie.
    Daca fereastra devine mereu trimestru, R22 ramane 210 si testul PICA."""
    with conn_trim.cursor() as cur:
        cur.execute("UPDATE firma_profil SET tip_decont='lunar' WHERE id=1")
    _, res = _d300.genereaza(conn_trim, _SCHEMA, Perioada(2026, luna=6))
    assert res.R.get("R22_2", 0) == 0, "lunar iunie NU trebuie sa vada aprilie; got %r" % res.R.get("R22_2")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_lipsa_tip_decont_ridica(conn_trim):
    """Fara vector (tip_decont gol) -> eroare la generare, NU default tacit 'L'."""
    with conn_trim.cursor() as cur:
        cur.execute("UPDATE firma_profil SET tip_decont=NULL WHERE id=1")
    with pytest.raises(ValueError):
        _d300.genereaza(conn_trim, _SCHEMA, Perioada(2026, luna=6))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d394_tip_D394_urmeaza_vectorul(conn_trim):
    """D394 al firmei trimestriale: tip_D394='T' (nu hardcodat 'L')."""
    xml, _ = _d394.genereaza(conn_trim, _SCHEMA, Perioada(2026, luna=6))
    assert 'tip_D394="T"' in xml, "tip_D394 trebuie 'T' pt platitor trimestrial"


# ---- integrare: taxare inversa FURNIZOR -> rd.13 auto -> DUK valid ----

@pytest.fixture
def conn_ti_furnizor():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA_TI)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA_TI))
                cur.execute("SET search_path TO %s, public" % _SCHEMA_TI)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                            "telefon,platitor_tva,tip_decont) VALUES (1,'FURNIZOR TI SRL','14399840','Str 1','Buc',"
                            "'B','4120','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar')")
                # livrare cu taxare inversa (art.331 lit.g cladiri): emisa, cota 0, taxare_inversa
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,"
                            "total,tva,taxare_inversa,categorie_331) VALUES ('TI1','2026-06-10','emisa',"
                            "'RO14399840','CUMPARATOR',40000,0,true,'cladiri_terenuri') RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'cladire','buc',1,40000,0)", (fid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_furnizor_taxare_inversa_rd13_DUK_valid(conn_ti_furnizor):
    """Furnizorul cu livrare taxare inversa: rd.13 auto (40000, fara TVA) -> DUK valid."""
    xml, res = _d300.genereaza(conn_ti_furnizor, _SCHEMA_TI, Perioada(2026, luna=6))
    assert res.R.get("R13_1") == 40000
    r = _duk.valideaza(xml, "d300", an=2026, luna=6)
    assert r["stare"] == "valid", "DUK a respins rd.13 furnizor: %s" % r.get("erori")
