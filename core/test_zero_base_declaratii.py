# -*- coding: utf-8 -*-
"""GARD ZERO-BASE (10.08.2026): un zero care POATE fi defect nu arata ca un nil legal.
- D100 pe zero = XML STRUCTURAL INVALID la DUK (sectiunea <obligatie> obligatorie) -> se REFUZA
  (ca D390 'nu se depune pe zero'), nu se emite XML invalid. (tura 22->23: avertisment -> refuz, dovedit de DUK.)
- D300 pe zero cu facturi in perioada -> AVERTISMENT non-blocant (nil-ul D300 E legal si obligatoriu, decide
  contabilul); nil legal (fara facturi) -> FARA avertisment.
Mutatie: cod vechi -> D100 nu ridica (avertisment/XML invalid) si D300 nu avertizeaza -> assert-urile pica.
"""
import pytest
from core import db as _db, tenant_provisioning as _tp, d100, d300
from core.common import Perioada

SCH = "ztest_zerobase"
PROFIL = ("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,cod_postal,caen,banca,iban,telefon,email,"
          "declarant_nume,declarant_prenume,declarant_functie,regim_fiscal,platitor_tva,tip_decont,tva_la_incasare) "
          "VALUES (1,'ZTEST ZB SRL','14399840','Str 1','Buc','B','010101','6202','BT',"
          "'RO49AAAA1B31007593840000','0712','z@z.ro','A','A','ADMIN','micro',true,'lunar',true)")
FACT = ("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
        "VALUES ('E-1','2026-08-15','emisa',1210,210,'RO14399840','CLIENT','emisa')")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _avert(res):
    return getattr(res, "avertismente", []) or []


@pytest.fixture
def sch():
    _db.init_pool(); p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute(PROFIL)
        yield conn
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d100_pe_zero_refuza(sch):
    """D100 pe zero (fara obligatie) -> ValueError 'nu se depune pe zero' (XML gol e invalid la DUK).
    Mutatie: cod vechi emitea XML invalid + doar avertiza -> nu ridica -> pica."""
    with sch.cursor() as cur:
        cur.execute(FACT)   # factura emisa necontabilizata (venituri 70x = 0)
    with pytest.raises(ValueError, match="nu se depune pe zero"):
        d100.genereaza(sch, SCH, Perioada(2026, trim=3))
    # si fara facturi (nil) tot se refuza - D100 nil nu e depozitabil
    with sch.cursor() as cur:
        cur.execute("DELETE FROM facturi")
    with pytest.raises(ValueError, match="nu se depune pe zero"):
        d100.genereaza(sch, SCH, Perioada(2026, trim=3))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_pe_zero_cu_facturi_avertizeaza(sch):
    """D300 pe zero (TVA la incasare nedecontata) cu facturi -> AVERTISMENT (non-blocant)."""
    with sch.cursor() as cur:
        cur.execute(FACT)
    _x, rd300 = d300.genereaza(sch, SCH, Perioada(2026, luna=8))
    assert not any(rd300.R.values()), "presupunere gresita: D300 nu e pe zero"
    assert any("zero" in x.lower() and "factur" in x.lower() for x in _avert(rd300)), \
        "D300 pe zero cu factura NU a semnalat zero-suspect: %r" % _avert(rd300)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d300_nil_legal_fara_avertisment(sch):
    """Control negativ: D300 nil (FARA facturi) = nil legal -> FARA avertisment de zero-suspect."""
    _x, rd300 = d300.genereaza(sch, SCH, Perioada(2026, luna=8))
    assert not any("zero" in x.lower() and "factur" in x.lower() for x in _avert(rd300)), \
        "nil legal D300 nu trebuie sa avertizeze zero-suspect: %r" % _avert(rd300)
