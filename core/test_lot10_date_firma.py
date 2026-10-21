# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 427, comanda Costin 10.1] Date firmă: „completarea vectorului fiscal nu se poate salva cât timp lipsesc Nr.
registrul comerțului, CAEN și adresa. Ce s-a completat se salvează; lipsurile rămân în «Profil incomplet» și blochează doar
declarațiile afectate, cum spune deja ecranul.”

Ce păzește: (1) `salveaza_date` nu mai refuză un câmp obligatoriu gol — salvează restul și întoarce lipsurile; o valoare INVALIDĂ se
refuză în continuare; (2) lipsa blochează declarația, nu salvarea: D112 nu mai pune CAEN-ul inventat „0000”, ci se oprește
(structura ANAF D112 îl cere), iar harta OBLIGATORII o spune. Pe bază: schemă efemeră, în ROLLBACK.
"""
import io
import os

import pytest

from core import firma_profil_api as fp
from core import d112

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _prof(**k):
    p = {"cui": "14399840", "nume": "FIRMA TEST SRL", "caen": "6202", "declarant_nume": "POPESCU", "declarant_prenume": "ION",
         "declarant_functie": "ADMINISTRATOR"}
    p.update(k)
    return p


def test_d112_se_opreste_fara_caen_nu_inventeaza_0000():
    # structura ANAF D112 (anaf_surse/d112_struct_anaf.txt): „6 caen Cod CAEN N(4) DA  Nomenclator 1 – coduri CAEN si tarife de risc
    # […] ERR caen ‘Cod caen inexistent in nomenclator’” — câmpul e cerut; lipsa oprește declarația, nu se completează cu „0000”
    er = d112.erori_generare(_prof(caen=""))
    assert len(er) == 1 and "Lipsă cod CAEN" in er[0], er                 # o singură eroare, refuzul numit al câmpului lipsă
    assert d112.erori_generare(_prof()) == []
    assert set(fp.OBLIGATORII["caen"]) >= {"D112"}, fp.OBLIGATORII["caen"]   # harta spune ce blochează lipsa (panoul „Profil incomplet”)
    assert d112.caen_in_nomenclator("0000") is False                     # „0000” scris de om e în afara nomenclatorului, nu „lipsă”
    assert d112.caen_in_nomenclator("") is True                          # lipsa e a OBLIGATORII, nu „prezent-dar-invalid”


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_lot10_df"


@pytest.fixture
def conn():
    from core import db, tenant_provisioning as _tp
    db.init_pool()
    with db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui) VALUES (1, 'ZT', '14399840')")
            yield c
        finally:
            c.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_427_campul_obligatoriu_gol_nu_opreste_salvarea_restului(conn):
    date = {"reg_com": "", "caen": "", "adresa": "", "telefon": "0722000427", "banca": "ING"}
    r = fp.salveaza_date(conn, date, tenant_id=None, user_id=7)
    # comanda Costin 10.1 (427): „Ce s-a completat se salvează; lipsurile rămân în «Profil incomplet» și blochează doar declarațiile
    # afectate”
    assert r["ok"] is True, r
    with conn.cursor() as cur:
        cur.execute("SELECT telefon, banca FROM firma_profil")
        assert cur.fetchone() == ("0722000427", "ING")
    lip = {l["camp"]: l["declaratii"] for l in r["lipsuri"]}
    assert {"reg_com", "caen", "adresa"} <= set(lip), lip
    assert lip["caen"] == ["D101", "D112", "D300", "D394"] and lip["reg_com"] == ["Bilanț S1005"], lip


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_427_valoarea_invalida_se_refuza_in_continuare_fara_scriere(conn):
    r = fp.salveaza_date(conn, {"telefon": "0722000427", "serie_chitanta": "CH-427!"}, tenant_id=None, user_id=7)
    assert r["ok"] is False and r["camp"] == "serie_chitanta", r          # valoare invalidă (regula seriei din `salveaza_date`): refuz numit, nimic scris
    with conn.cursor() as cur:
        cur.execute("SELECT telefon FROM firma_profil")
        assert cur.fetchone() == (None,)
