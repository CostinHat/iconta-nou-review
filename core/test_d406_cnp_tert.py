# -*- coding: utf-8 -*-
"""GARD D406 CNP in tert_cui -> tipul 03 (E3/E4, CATALOG_INVALIDITATE.md; 10.08.2026).

Sursa oficiala: d406_schema_anaf.xlsx, foaia "5. Structures", codificarea tip 00-11 (S.I.26/S.I.23):
  "4. 03 urmat de CNP pentru persoane fizice cetateni romani ..." iar validarea sintactica pct.1.4:
  "03 atunci se verifica ca lungimea ... fara prefixul 03 sa fie 13 caractere numerice, prima cifra
  diferita de 0". Un partener persoana fizica care ISI declara CNP-ul se raporteaza 03+CNP.

DEFECT (HEAD 8b74ccb): _partener_id_saft / _partener_registration_number nu emiteau NICIODATA tipul
  03 - un CNP in tert_cui iesea 00+CNP (tratat ca CUI) -> DUK il respinge INDIFERENT de validitate
  (tipul gresit, calea 03 inexistenta). Reparat: CNP VALID -> 03+CNP (referit identic pe factura si
  in <Suppliers>/<Customers>); CNP invalid -> ValueError care numeste partenerul.

MUTATIE: pe HEAD SupplierID iese "001900101410011" -> assert "03..." PICA (si DUK ar respinge).
"""
import re
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_cnp_tert"
CNP_VALID = "1900101410011"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _duk_ok():
    try:
        from core import duk
        return duk.instalat("D406") if hasattr(duk, "instalat") else True
    except Exception:
        return False


def _seed(conn, tert_cui=CNP_VALID, tert_nume="IONESCU MARIA", directie="primita"):
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
        cur.execute("SET search_path TO \"%s\", public" % SCH)
        cur.execute("INSERT INTO firma_profil (id,nume,cui,platitor_tva,tva_la_incasare) VALUES (1,%s,%s,true,false)",
                    ("ZTEST SRL", "14399840"))
        cur.execute("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id",
                    ("CNP-1", "2026-08-10", directie, 119, 19, tert_cui, tert_nume, directie))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id,descriere,um,cantitate,pret_unitar,cota_tva) "
                    "VALUES (%s,%s,%s,%s,%s,%s)", (fid, "Serviciu", "buc", 1, 100, 19))


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
def test_cnp_valid_emis_ca_03_in_supplier_si_master(conn):
    _seed(conn, tert_cui=CNP_VALID, directie="primita")
    xml, res = d406.genereaza(conn, SCH, 2026, 8)
    sids = re.findall(r"<SupplierID>(.*?)</SupplierID>", xml)
    assert ("03" + CNP_VALID) in sids, "CNP valid trebuie emis 03+CNP, gasit: %s" % set(sids)
    assert ("00" + CNP_VALID) not in sids, "CNP nu trebuie emis 00+CNP (tipul gresit)"
    # Consistenta master: acelasi cod in <Suppliers> (RegistrationNumber/SupplierID)
    supp = re.search(r"<Suppliers>.*?</Suppliers>", xml, re.S)
    assert supp and ("03" + CNP_VALID) in supp.group(0), "03+CNP trebuie sa apara si in <Suppliers>"


@pytest.mark.skipif(not (_db_ok() and _duk_ok()), reason="DB/DUK indisponibil")
def test_cnp_valid_03_e_duk_valid(conn):
    from core import duk
    _seed(conn, tert_cui=CNP_VALID, directie="primita")
    xml, res = d406.genereaza(conn, SCH, 2026, 8)
    r = duk.valideaza(xml, "d406", an=2026, luna=8, timeout=110)
    if r["stare"] == "gri":
        pytest.skip("validator SAF-T indisponibil: %s" % r.get("erori"))
    assert r["stare"] == "valid", "03+CNP trebuie acceptat de DUK; erori: %s" % r["erori"]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cnp_invalid_ridica_numind_partenerul(conn):
    _seed(conn, tert_cui="1900101410010", tert_nume="POPESCU ION")  # checksum CNP gresit
    with pytest.raises(ValueError) as ei:
        d406.genereaza(conn, SCH, 2026, 8)
    assert "POPESCU ION" in str(ei.value), str(ei.value)
