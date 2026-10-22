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
    # [lotul 10, C69] + mare_contribuabil / forma_proprietate: bilanțul le cere (bifaMC / codJJ, codPP), altfel se oprește
    cur.execute("""INSERT INTO firma_profil
        (id,nume,cui,reg_com,adresa,oras,judet,caen,banca,iban,tip_decont,platitor_tva,
         declarant_nume,declarant_prenume,declarant_functie,mare_contribuabil,forma_proprietate,interes_public)
        VALUES (1,'ZTEST BILANT SRL','14399840',%s,'Str 1','Buc','B','6202','Banca Test',
         'RO49AAAA1B31007593840000','T',false,'Ada','Ada','ADMINISTRATOR',false,'35',false)""" % rc)


def _cu_schema(reg_com, fn):
    _db.init_pool()
    p = _db.pool()
    conn = p.getconn()
    schema = "ztest_bilant_rc"
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
            cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), schema))
            # [lotul 11, decizia 10.3] cabinetul sintetic care ține firma, cu întocmitorul bilanțului completat (antetul îl cere)
            cur.execute("INSERT INTO public.accounting_firms (nume, calit_intocmit, nume_intocmit) VALUES ('Cabinet sintetic', 12, 'IONESCU MARIA') RETURNING id")
            cur.execute("INSERT INTO public.tenants (schema_name, nume, accounting_firm_id, creat_la) VALUES (%s, 'ZTEST BILANT SRL', "
                        "%s, '2020-01-01')", (schema, cur.fetchone()[0]))
            cur.execute('SET search_path TO "%s", public' % schema)
            _profil(cur, reg_com)
        return fn(conn, schema)
    finally:
        conn.rollback()
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % schema)
        conn.commit()
        p.putconn(conn)


#: refuzul întreg, pe care îl dau ambele formulare (poarta e partajată) — valoarea, nu „fragmentul apare” (core/test_garzi_pe_text.py)
_REFUZ_REG_COM = ("Bilanț nu se poate genera: Nr. registrul comerțului lipsește — obligatoriu în bilanț; fără el declarația e respinsă "
                  "de validatorul ANAF. Se completează la Date firmă.")


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1005_refuza_fara_reg_com():
    """Fara reg_com -> genereaza (S1005) RIDICA ValueError cu 'registrul comertului', NU emite XML."""
    def _run(conn, schema):
        with pytest.raises(ValueError) as ei:
            bilant_api.genereaza(conn, schema, 2025)
        return str(ei.value)
    msg = _cu_schema(None, _run)
    assert msg == _REFUZ_REG_COM, ("refuzul S1005 nu numeste campul lipsa (Nr. registrul comertului): %r" % msg)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1003_refuza_fara_reg_com():
    """Aceeasi poarta partajata acopera si S1003 (generalizare)."""
    def _run(conn, schema):
        with pytest.raises(ValueError) as ei:
            bilant_api.genereaza_s1003(conn, schema, 2025)
        return str(ei.value)
    msg = _cu_schema(None, _run)
    assert msg == _REFUZ_REG_COM, ("refuzul S1003 nu numeste campul lipsa (Nr. registrul comertului): %r" % msg)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_s1005_cu_reg_com_nu_blocheaza_pe_reg_com():
    """Control pozitiv: cu reg_com completat, genereaza nu mai ridica pe motiv de reg_com (emite XML)."""
    def _run(conn, schema):
        xml, av = bilant_api.genereaza(conn, schema, 2025)
        return xml
    xml = _cu_schema("J40/1234/2020", _run)
    import re
    import xml.etree.ElementTree as _ET
    rad = _ET.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", xml))   # elementul rădăcină, nu „șirul apare” (core/test_garzi_pe_text.py)
    assert rad.tag.rsplit("}", 1)[-1] == "Bilant1005", "S1005 cu reg_com completat nu s-a generat: %r" % xml[:120]
