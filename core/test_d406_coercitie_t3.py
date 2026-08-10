# -*- coding: utf-8 -*-
"""GARD D406 coercitie TACITA enum-necunoscut (T3, CATALOG_INVALIDITATE.md; 10.08.2026).

Clasa (d): o valoare in afara nomenclatorului era inlocuita TACIT cu un default -> XML DUK-valid dar
date GRESITE la ANAF. Reparat: avertisment CLAR, PER-ITEM, care numeste valoarea sursa coercita:
  - UOM necunoscut -> H87 (bucata): avertismentul numeste FACTURA + unitatea.
  - cota fara cod TaxCode de livrare -> 310312 (taxare inversa): numeste FACTURA + cota.
  - PaymentMethod necunoscut -> 03 (fara numerar): numeste plata + metoda.

MUTATIE (HEAD 8b74ccb): UOM avertiza global fara sa numeasca factura; cota si PaymentMethod se
  inlocuiau COMPLET tacit (niciun avertisment). Assert-urile de mai jos PICA pe HEAD.
"""
import re
from datetime import date
from decimal import Decimal
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_coercitie"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _seed(conn, um="parseci", cota=Decimal("7"), pret=Decimal("100")):
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute("SET search_path TO \"%s\", public" % SCH)
        cur.execute("INSERT INTO firma_profil (id,nume,cui,platitor_tva,tva_la_incasare) VALUES (1,%s,%s,true,false)",
                    ("ZTEST SRL", "14399840"))
        tva = (pret * cota / 100)
        total = pret + tva
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    ("FX-9", "2026-08-10", "emisa", total, tva, "14399840", "ALFA SRL", "emisa"))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", (fid, "Serviciu", um, 1, pret, cota))


@pytest.fixture
def conn():
    _db.init_pool(); p = _db.pool(); c = p.getconn()
    try:
        yield c
    finally:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.rollback(); p.putconn(c)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_uom_necunoscut_avertisment_numeste_factura_si_unitatea(conn):
    _seed(conn, um="parseci", cota=Decimal("21"))   # cota valida ca sa izolam UOM
    xml, res = d406.genereaza(conn, SCH, 2026, 8)
    av = " ".join(res.avertismente)
    assert "parseci" in av, "avertismentul trebuie sa NUMEASCA unitatea coercita: %s" % av
    assert "FX-9" in av, "avertismentul UOM trebuie sa NUMEASCA factura: %s" % av


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cota_necunoscuta_avertisment_numeste_factura_si_cota(conn):
    _seed(conn, um="buc", cota=Decimal("7"))   # 7% nu are cod TaxCode livrari -> 310312
    xml, res = d406.genereaza(conn, SCH, 2026, 8)
    av = " ".join(res.avertismente)
    assert "310312" in av, "avertismentul trebuie sa spuna ca s-a folosit 310312: %s" % av
    assert "FX-9" in av and "7" in av, "avertismentul cota trebuie sa NUMEASCA factura + cota: %s" % av


def test_payment_method_necunoscut_avertisment_numeste_plata():
    # construieste (fara DB): o plata cu metoda necunoscuta trebuie sa produca avertisment numind-o.
    prof = {"cui": "14399840", "nume": "TEST SRL", "platitor_tva": True}
    p = d406.Plata(ref="PL-7", data=date(2026, 8, 10), metoda="bitcoin", partener_id="0014399840")
    p.linii.append(d406.LiniePlata(nr=1, cont="5121", descriere="x", suma=Decimal("100.00"), sens="D"))
    p.linii.append(d406.LiniePlata(nr=2, cont="4111", descriere="y", suma=Decimal("100.00"), sens="C"))
    res = d406.construieste(prof, 2026, 8, [], [], [], plati=[p])
    av = " ".join(res.avertismente)
    assert "bitcoin" in av and "PL-7" in av, "avertismentul PaymentMethod trebuie sa numeasca metoda + plata: %s" % av
    # emisia ramane un cod ANAF valid (03)
    xml = d406.build_xml(res)
    assert re.search(r"<PaymentMethod>03</PaymentMethod>", xml)


def test_payment_method_cunoscut_nu_avertizeaza():
    prof = {"cui": "14399840", "nume": "TEST SRL", "platitor_tva": True}
    p = d406.Plata(ref="PL-8", data=date(2026, 8, 10), metoda="numerar", partener_id="0014399840")
    p.linii.append(d406.LiniePlata(nr=1, cont="5311", descriere="x", suma=Decimal("50.00"), sens="D"))
    p.linii.append(d406.LiniePlata(nr=2, cont="4111", descriere="y", suma=Decimal("50.00"), sens="C"))
    res = d406.construieste(prof, 2026, 8, [], [], [], plati=[p])
    assert not any("metoda de plata necunoscuta" in a for a in res.avertismente)
