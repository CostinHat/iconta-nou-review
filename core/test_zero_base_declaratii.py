# -*- coding: utf-8 -*-
"""GARD ZERO-BASE (10.08.2026, decizie Costin): D100/D300 pe zero care POATE fi defect SEMNALEAZA
(avertisment), nu tace ca un nil legal. Un zero cu facturi in perioada (necontabilizate) != nil legal
(fara activitate). NU blocheaza generarea/depunerea - nil-ul e legal, decide contabilul. Vezi DECIZII 10.08.
Mutatie: pe cod vechi (fara avertisment) assert-urile de zero-suspect pica; controlul negativ (nil legal)
trece pe ambele.
"""
import pytest
from core import db as _db, tenant_provisioning as _tp, d100, d300
from core.common import Perioada

SCH = "ztest_zerobase"
PROFIL = ("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,cod_postal,caen,banca,iban,telefon,email,"
          "declarant_nume,declarant_prenume,declarant_functie,regim_fiscal,platitor_tva,tip_decont,tva_la_incasare) "
          "VALUES (1,'ZTEST ZB SRL','14399840','Str 1','Buc','B','010101','6202','BT',"
          "'RO49AAAA1B31007593840000','0712','z@z.ro','A','A','ADMIN','micro',true,'lunar',true)")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _avert(res):
    return getattr(res, "avertismente", []) or []


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_zero_base_d100_d300():
    _db.init_pool(); p = _db.pool(); conn = p.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute(PROFIL)
            # o factura emisa in perioada, DAR fara nota 70x si fara decontare (necontabilizata)
            cur.execute("INSERT INTO facturi (numar,data_emitere,directie,total,tva,tert_cui,tert_nume,status) "
                        "VALUES ('E-1','2026-08-15','emisa',1210,210,'RO14399840','CLIENT','emisa')")

        # (A) D100 pe zero cu factura emisa necontabilizata -> avertisment
        _x, rd100 = d100.genereaza(conn, SCH, Perioada(2026, trim=3))
        a100 = _avert(rd100)
        assert any("factur" in x.lower() for x in a100), \
            "D100 pe zero cu factura emisa NU a semnalat zero-suspect: %r" % a100

        # (B) D300 pe zero (TVA la incasare, factura nedecontata) cu facturi -> avertisment
        _x, rd300 = d300.genereaza(conn, SCH, Perioada(2026, luna=8))
        assert not any(rd300.R.values()), "presupunere gresita: D300 nu e pe zero"
        a300 = _avert(rd300)
        assert any("zero" in x.lower() and "factur" in x.lower() for x in a300), \
            "D300 pe zero cu factura NU a semnalat zero-suspect: %r" % a300

        # (C) control negativ: FARA facturi -> nil legal -> FARA avertisment de zero-suspect
        with conn.cursor() as cur:
            cur.execute("DELETE FROM facturi")
        _x, rd100n = d100.genereaza(conn, SCH, Perioada(2026, trim=3))
        _x, rd300n = d300.genereaza(conn, SCH, Perioada(2026, luna=8))
        assert not any("factur" in x.lower() for x in _avert(rd100n)), \
            "nil legal D100 nu trebuie sa avertizeze zero-suspect: %r" % _avert(rd100n)
        assert not any("zero" in x.lower() and "factur" in x.lower() for x in _avert(rd300n)), \
            "nil legal D300 nu trebuie sa avertizeze zero-suspect: %r" % _avert(rd300n)
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback()
        p.putconn(conn)
