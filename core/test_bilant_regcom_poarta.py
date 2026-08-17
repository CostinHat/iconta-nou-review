# -*- coding: utf-8 -*-
"""core/test_bilant_regcom_poarta.py - GARD: bilant_api.erori_generare blocheaza generarea cand
lipseste Nr. registrul comertului (regCom), pentru ca regCom e OBLIGATORIU in S1005/S1003.

Sursa (Regula 5, temeiul la sursa): DUKIntegrator -v S1005 pe un bilant fara regCom intoarce
"eroare atribut: regCom: atributul trebuie sa existe" (pachet oficial ANAF, reguli 2026.1). Inainte
de acest gard, erori_generare verifica doar cui+nume, iar genereaza emitea un S1005 FARA regCom -
exact "XML respins de ANAF" pe care docstring-ul portii spune ca il previne. Ecranul Date firma promitea
deja "Nr. registrul comertului - blocheaza Bilant S1005", dar codul NU bloca: promisiune falsa.

Gardul cere ca genereaza (S1005) SI genereaza_s1003 sa RIDICE ValueError cand reg_com lipseste, si sa
NU ridice pe motiv de reg_com cand e completat. Efemer: schema stearsa + rollback la final."""
import pytest

from core import db as _db, tenant_provisioning as _tp, bilant_api


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _profil(cur, reg_com):
    rc = "NULL" if reg_com is None else "'%s'" % reg_com
    cur.execute("""INSERT INTO firma_profil
        (id,nume,cui,reg_com,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,
         declarant_nume,declarant_prenume,declarant_functie)
        VALUES (1,'ZTEST BILANT SRL','14399840',%s,'Str 1','Buc','B','6202','Banca Test',
         'RO49AAAA1B31007593840000','T',false,'Ada','Ada','ADMINISTRATOR')""" % rc)


def _cu_schema(reg_com, fn):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    schema = "ztest_bilant_rc"
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
            cur.execute('SET search_path TO "%s", public' % schema)
            _profil(cur, reg_com)
        return fn(conn, schema)
    finally:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        conn.commit()
        p.putconn(conn)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1005_refuza_fara_reg_com():
    """Fara reg_com -> genereaza (S1005) RIDICA ValueError cu 'registrul comertului', NU emite XML."""
    def _run(conn, schema):
        with pytest.raises(ValueError) as ei:
            bilant_api.genereaza(conn, schema, 2025)
        return str(ei.value)
    msg = _cu_schema(None, _run)
    assert "registrul comer" in msg.lower(), (
        "refuzul S1005 nu numeste campul lipsa (Nr. registrul comertului): %r" % msg)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1003_refuza_fara_reg_com():
    """Aceeasi poarta partajata acopera si S1003 (generalizare)."""
    def _run(conn, schema):
        with pytest.raises(ValueError) as ei:
            bilant_api.genereaza_s1003(conn, schema, 2025)
        return str(ei.value)
    msg = _cu_schema(None, _run)
    assert "registrul comer" in msg.lower(), (
        "refuzul S1003 nu numeste campul lipsa (Nr. registrul comertului): %r" % msg)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1005_cu_reg_com_nu_blocheaza_pe_reg_com():
    """Control pozitiv: cu reg_com completat, genereaza nu mai ridica pe motiv de reg_com (emite XML)."""
    def _run(conn, schema):
        xml, av = bilant_api.genereaza(conn, schema, 2025)
        return xml
    xml = _cu_schema("J40/1234/2020", _run)
    assert "Bilant1005" in xml, "S1005 cu reg_com completat nu s-a generat: %r" % xml[:120]
