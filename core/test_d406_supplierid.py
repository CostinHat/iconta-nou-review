# -*- coding: utf-8 -*-
"""GARD D406 SupplierID (10.08.2026): SupplierID/CustomerID pe factura NU poate fi "0".
Sursa oficiala: d406_schema_anaf.xlsx, regula sintactica SD.P.23 (si S.I.26/MF.S.3):
  "2. Altfel daca SupplierID este egal cu 0 (zero) se semnaleaza eroare sintactica
   (SupplierID nu poate fi 0)". Furnizorul de pe o factura are mereu identitate; PF fara
  cod fiscal -> tipul 04 (cod client alocat unic de operator, doar alfanumeric).
Defect DUK dovedit (ALFA tenant_013, factura PF-01, furnizor persoana fizica fara CUI):
  "PurchaseInvoices Invoice SupplierInfo SupplierID: SupplierID nu poate fi 0 (zero)".
MUTATIE: cod vechi emitea `_partener_registration_number(cui) or "0"` -> SupplierID="0"
  pe achizitia de la PF -> assert-ul de mai jos (sid != "0") PICA pe cod vechi.
"""
import re
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_supplierid"
PROFIL = ("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,cod_postal,caen,banca,iban,telefon,email,"
          "declarant_nume,declarant_prenume,declarant_functie,regim_fiscal,platitor_tva,tip_decont,tva_la_incasare) "
          "VALUES (1,'ZTEST D406 SRL','14399840','Str 1','Buc','B','010101','6202','BT',"
          "'RO49AAAA1B31007593840000','0712','z@z.ro','A','A','ADMIN','micro',true,'lunar',true)")
# Factura PRIMITA de la o persoana fizica FARA cod fiscal (tert_cui gol) - cazul defect.
FACT_PF = ("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
           "VALUES ('PF-T','2026-08-10','primita',119,19,'','IONESCU MARIA PFA','primita')")


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
            cur.execute(FACT_PF)
        yield conn
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


def _supplier_ids(xml):
    bloc = re.search(r"<PurchaseInvoices>.*?</PurchaseInvoices>", xml, re.S)
    assert bloc, "lipseste sectiunea PurchaseInvoices in XML"
    return re.findall(r"<SupplierInfo>\s*<SupplierID>(.*?)</SupplierID>", bloc.group(0))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_supplierid_pf_fara_cui_nu_e_zero(sch):
    """Furnizor PF fara cod fiscal -> SupplierID = tipul 04 + cod intern, NICIODATA "0".
    Cod vechi: `... or "0"` -> SupplierID="0" -> pica aici (DUK: SupplierID nu poate fi 0)."""
    xml, _res = d406.genereaza(sch, SCH, 2026, 8)
    sids = _supplier_ids(xml)
    assert sids, "nicio factura de cumparare in PurchaseInvoices"
    for sid in sids:
        assert sid != "0", "SupplierID=0 interzis de SAF-T (regula SD.P.23) - cod vechi"
    # cazul PF fara cod fiscal: tipul 04 + nume normalizat (alfanumeric, fara spatii)
    assert "04IONESCUMARIAPFA" in sids, \
        "furnizor PF fara CUI trebuie sa poarte tipul 04 + cod intern, dar am: %r" % sids
