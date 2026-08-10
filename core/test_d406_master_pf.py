# -*- coding: utf-8 -*-
"""GARD D406 partener PF fara cod fiscal in MASTER (10.08.2026): un partener persoana
fizica fara cod fiscal declarat (tert_cui gol), referit pe factura cu tipul 04, trebuie
sa apara SI in <Customers>/<Suppliers> (MasterFiles) - consistent cu felul in care il
refera factura (SupplierID/CustomerID=04...).

Sursa oficiala: d406_schema_anaf.xlsx, foaia "5. Structures", codificarea tip 00-11:
  tip 04 = "cod client asociat in mod unic de catre operatorul economic ... pentru pers.
  fizice care nu isi declara CNP-ul". Referinta de pe factura si intrarea din master
  trebuie sa fie IDENTICE (acelasi cod alocat). Un CustomerID/SupplierID referit dar
  absent din master este o neconformitate (partener nedeclarat).

RADACINA: derivarea master-din-facturi (core/d406.py, pull()) folosea
  _partener_registration_number (doar 00/01/02) + filtra tert_cui != '' -> partenerul PF
  (tip 04) era EXCLUS din master, desi factura il referea. Reparat sa foloseasca
  _partener_id_saft (aceeasi identitate ca referinta de pe factura).

MUTATIE: pe HEAD (6cd0054) "04IONESCUMARIAPFA" / "04POPESCUIONPF" NU apar in blocurile
  <Suppliers>/<Customers> -> assert-urile de mai jos PICA; dupa reparatie TREC.
"""
import re
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_master_pf"
PROFIL = ("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,cod_postal,caen,banca,iban,telefon,email,"
          "declarant_nume,declarant_prenume,declarant_functie,regim_fiscal,platitor_tva,tip_decont,tva_la_incasare) "
          "VALUES (1,'ZTEST D406 SRL','14399840','Str 1','Buc','B','010101','6202','BT',"
          "'RO49AAAA1B31007593840000','0712','z@z.ro','A','A','ADMIN','micro',true,'lunar',true)")
# Furnizor PF fara cod fiscal (achizitie de la persoana fizica) - tip 04 in referinta.
FACT_FURN_PF = ("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
                "VALUES ('PF-F','2026-08-10','primita',119,19,'','IONESCU MARIA PFA','primita')")
# Client PF fara cod fiscal (vanzare catre persoana fizica) - tip 04 in referinta.
FACT_CLI_PF = ("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
               "VALUES ('PF-C','2026-08-11','emisa',119,19,'','POPESCU ION PF','emisa')")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def sch():
    _db.init_pool(); p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute(PROFIL)
            cur.execute(FACT_FURN_PF)
            cur.execute(FACT_CLI_PF)
        yield conn
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


def _block(xml, tag):
    m = re.search(r"<%s>.*?</%s>" % (tag, tag), xml, re.S)
    assert m, "lipseste sectiunea <%s> in XML" % tag
    return m.group(0)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pf_furnizor_apare_in_suppliers(sch):
    """Furnizor PF fara CUI, referit ca SupplierID=04..., trebuie sa apara in <Suppliers>."""
    xml, _res = d406.genereaza(sch, SCH, 2026, 8)
    pid = "04IONESCUMARIAPFA"
    assert ("<SupplierID>%s</SupplierID>" % pid) in xml, "factura nu refera furnizorul PF ca 04..."
    supp = _block(xml, "Suppliers")
    # MUTATIE: pe HEAD partenerul PF lipsea din master -> pica aici
    assert pid in supp, "furnizorul PF (tip 04) referit de factura lipseste din <Suppliers> (master)"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_pf_client_apare_in_customers(sch):
    """Client PF fara CUI, referit ca CustomerID=04..., trebuie sa apara in <Customers>."""
    xml, _res = d406.genereaza(sch, SCH, 2026, 8)
    pid = "04POPESCUIONPF"
    assert ("<CustomerID>%s</CustomerID>" % pid) in xml, "factura nu refera clientul PF ca 04..."
    cust = _block(xml, "Customers")
    # MUTATIE: pe HEAD partenerul PF lipsea din master -> pica aici
    assert pid in cust, "clientul PF (tip 04) referit de factura lipseste din <Customers> (master)"
