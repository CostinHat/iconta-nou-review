# -*- coding: utf-8 -*-
"""core/test_d300_forfait_agricol.py — gard TVA ORFAN din antet la achizitii primite
(C-4 transa 2, item (e): T-5 forfetar agricol, deductibilitate la cumparator P1).

SCENARIU (T-5 din seed transa2): S3 (agricultor forfetar art.315^1) -> P1.
Factura primita: baza 25.000, cota linie 0 (agricultorul NU colecteaza TVA), dar in
ANTET tva=2.000 = compensatia forfetara 8% (art.315^1 al.1-2). Cumparatorul P1 are drept
de deducere pe compensatie (al.17) DAR doar daca agricultorul e in Registrul agricultorilor
la data livrarii - flag INEXISTENT in date (decizie de produs, "nu se forteaza" per C4_date.md).

DIVERGENTA reparata: calcul_d300 deriva TVA din COTA (0) si ignora antetul -> cele 2.000
cadeau tacit in 'alte_a' cu un avertisment GENERIC ("cota in afara 21/11/9 - neincluse")
care NU numea suma. Cumparatorul putea citi "cota 0 = scutit" si pierdea deducerea ->
TVA de plata supraevaluata. FIX: se masoara TVA-ul orfan (antet - randuri pe cota) si se
semnaleaza CANTITATIV (ca precedentul 9% deductibil), fara sa se auto-deduca (nu se forteaza)
si fara sa se schimbe XML-ul (ramane DUK-valid).

Metoda: RED pe codul vechi (avertisment nenumit) -> GREEN. Bidirectional:
  - directia 1 (sub-raportare): fara masurare -> avertismentul nu numeste 2.000 -> PICA.
  - directia 2 (supra-corectie): daca cineva auto-deduce orfanul -> TVA de plata scade -> PICA.
"""
import pytest
from core.common import Perioada
from core import d300 as _d300, db as _db, tenant_provisioning as _tp, duk as _duk

_SCHEMA = "test_forfait_agricol"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_forfait():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                # cumparator P1: platitor TVA, lunar
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,"
                            "telefon,platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES (1,'P1 PROFIT SRL','95275466','Str 1','Buc',"
                            "'B','4669','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar','Popescu','Ion','ADMINISTRATOR')")
                # achizitie de la agricultor forfetar: baza 25000, cota linie 0, ANTET tva 2000 (forfait 8%)
                cur.execute("INSERT INTO facturi (numar,data_emitere,directie,tert_cui,tert_nume,tert_platitor_tva,"
                            "total,tva,taxare_inversa) VALUES ('AGR1','2026-06-12','primita','95873249','S3 AGRICULTOR',"
                            "false,27000,2000,false) RETURNING id")
                fid = cur.fetchone()[0]
                cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                            "VALUES (%s,'produse agricole','buc',1,25000,0)", (fid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_forfait_orfan_semnalat_cantitativ(conn_forfait):
    """GARD (RED pe codul vechi): avertismentul TREBUIE sa numeasca cele 2.000 lei de TVA
    forfetar din antet, altfel cumparatorul pierde deducerea tacit."""
    _, res = _d300.genereaza(conn_forfait, _SCHEMA, Perioada(2026, luna=6))
    orfan = [a for a in res.avertismente if "2.000" in a and "forfetar" in a.lower()]
    assert orfan, "avertisment cantitativ pt TVA forfetar orfan lipsa; avertismente=%r" % res.avertismente


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_forfait_NU_se_auto_deduce(conn_forfait):
    """MUTATIE inversa (supra-corectie): compensatia forfetara NU se auto-deduce (nu se forteaza -
    lipsa flag Registrul agricultorilor). Deci nu apare TVA deductibil auto (R22/R23) si nu exista
    TVA de recuperat din aceasta factura. Daca cineva o auto-deduce, aceste asertii PICA."""
    _, res = _d300.genereaza(conn_forfait, _SCHEMA, Perioada(2026, luna=6))
    assert res.R.get("R22_2", 0) == 0, "forfait NU trebuie auto-dedus la R22; got %r" % res.R.get("R22_2")
    assert res.R.get("R23_2", 0) == 0, "forfait NU trebuie auto-dedus la R23; got %r" % res.R.get("R23_2")
    assert res.tva_de_recuperat == 0, "forfait nedeductibil auto -> fara TVA de recuperat; got %r" % res.tva_de_recuperat


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_forfait_d300_ramane_DUK_valid(conn_forfait):
    """Avertismentul e in res, NU in XML -> declaratia ramane DUK-valida."""
    xml, _ = _d300.genereaza(conn_forfait, _SCHEMA, Perioada(2026, luna=6))
    r = _duk.valideaza(xml, "d300", an=2026, luna=6)
    assert r["stare"] == "valid", "DUK a respins D300 cu achizitie forfetara: %s" % r.get("erori")
