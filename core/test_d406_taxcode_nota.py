# -*- coding: utf-8 -*-
"""GARD D406 TaxCode nota contabila (10.08.2026): pe liniile din GeneralLedgerEntries
(TransactionLine) si Payments (PaymentLine) fara TVA, TaxCode trebuie sa fie un cod VALID
din nomenclatorul oficial, NU "300".

Sursa oficiala: d406_schema_anaf.xlsx, foaia "TVA_NoteContabile", antet integral:
  "NOMENCLATOR CODURI DE TAXA PENTRU RAPORTAREA NOTELOR CONTABILE CARE NU AU CORESPONDENT
   IN DOCUMENTE SURSA". Nomenclatorul contine DOAR familia 380xxx (confirmat si de foaia
  "Legenda coduri taxa TVA": "380nnn - 389nnn - pentru raportarea notelor contabile care
  nu au corespondent in Documente Sursa"). "300" NU exista in nomenclator - era un prefix
  inventat. Singurul cod cu cota 0 / scutit din familie = 380304 (cota 0, "Livrari/prestari
  pentru care nu exista obligatia emiterii facturii si nu sunt supuse TVA, art. 319 alin.
  10 Cod Fiscal") -> valoarea corecta pentru liniile de nota fara TVA (banca/casa/creante).

MUTATIE: codul vechi emitea <TaxCode>300</TaxCode> pe fiecare TransactionLine/PaymentLine
  -> assert-urile de mai jos (fara "300"; 380304 prezent in GL) PICA pe HEAD (6cd0054).
"""
import re
import pytest
from core import db as _db, tenant_provisioning as _tp, d406

SCH = "ztest_d406_taxcode_nota"
PROFIL = ("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,cod_postal,caen,banca,iban,telefon,email,"
          "declarant_nume,declarant_prenume,declarant_functie,regim_fiscal,platitor_tva,tip_decont,tva_la_incasare) "
          "VALUES (1,'ZTEST D406 SRL','14399840','Str 1','Buc','B','010101','6202','BT',"
          "'RO49AAAA1B31007593840000','0712','z@z.ro','A','A','ADMIN','micro',true,'lunar',true)")
# Nota contabila VALIDATA, fara corespondent in documente sursa (incasare client prin banca):
# 5121 = Conturi la banci, 4111 = Clienti. Linie pur contabila, fara TVA.
NOTA = ("INSERT INTO inregistrari (data,descriere,status) "
        "VALUES ('2026-08-12','Incasare client prin banca','validata') RETURNING id")
LINIE = ("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
         "VALUES (%s,'5121','4111',1000.00)")


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
            cur.execute(NOTA)
            nid = cur.fetchone()[0]
            cur.execute(LINIE, (nid,))
        yield conn
    finally:
        with conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.rollback(); p.putconn(conn)


def _gl_block(xml):
    m = re.search(r"<GeneralLedgerEntries>.*?</GeneralLedgerEntries>", xml, re.S)
    assert m, "lipseste sectiunea GeneralLedgerEntries in XML"
    return m.group(0)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_gl_taxcode_nu_e_300_ci_nomenclator_380304(sch):
    """TaxCode "300" (inexistent in nomenclator) interzis; liniile de nota fara TVA
    poarta 380304 (singurul cod cota-0 din familia 380xxx TVA_NoteContabile)."""
    xml, _res = d406.genereaza(sch, SCH, 2026, 8)
    gl = _gl_block(xml)
    # sectiunea GL trebuie sa aiba efectiv linii de nota
    assert "<TransactionLine>" in gl, "nicio TransactionLine in GeneralLedgerEntries"
    # MUTATIE: cod vechi emitea <TaxCode>300</TaxCode> -> pica aici
    assert "<TaxCode>300</TaxCode>" not in xml, \
        "TaxCode '300' nu exista in nomenclatorul TVA_NoteContabile (cod vechi inventat)"
    # fiecare TaxCode din GL trebuie sa fie din familia 380xxx
    coduri = re.findall(r"<TaxCode>(\d+)</TaxCode>", gl)
    assert coduri, "nicio linie cu TaxCode in GeneralLedgerEntries"
    for c in coduri:
        assert c.startswith("380"), \
            "TaxCode GL '%s' nu e din familia 380xxx (note contabile fara document sursa)" % c
    # liniile non-TVA -> 380304 (cota 0 / scutit)
    assert "<TaxCode>380304</TaxCode>" in gl, "linia de nota fara TVA trebuie sa poarte 380304"
    # 380304 declarat si in TaxTable (regasibil la lookup)
    assert re.search(r"<TaxTable>.*<TaxCode>380304</TaxCode>.*</TaxTable>", xml, re.S), \
        "380304 (referit pe liniile GL) trebuie declarat in TaxTable"
