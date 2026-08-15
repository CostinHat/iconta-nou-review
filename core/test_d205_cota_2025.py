# -*- coding: utf-8 -*-
"""GARD D205 (16.08.2026, campanie rețeta D300, pas 7/8) — cota impozitului pe dividende 2025 = 10%.

BUG FISCAL (activ, campania curenta pt anul 2025): registrul common.COTE['impozit_dividend'] avea 2023->8%,
2026->16%, DAR LIPSEA 2025->10% -> pentru an=2025 cota() returna 8% -> impozit SUB-DECLARAT cu 20% pentru
orice D205 aferent anului 2025. Nota/comentariul care ziceau "10% e GRESIT" au confundat DATA (peticul 10%
era pe 2024-01-01, gresit fiindca 2024=8%) si au aruncat cota in loc s-o mute la 2025.

Sursa (bate memoria, regula 2): OUG 156/2024 art.LXIV+LXV (oug_156_2024.txt:3-4,50): dividende 10% "impozitul
fiind final", in vigoare de la 1 ianuarie 2025; confirmat INDEPENDENT de d205_struct_anaf.txt:6 "8%/2024,
10%/2025, 16%/2026". FIX: adaugat (2025,1,1)->10% in registru.

Aserturi ASCII.
"""
import pytest
from datetime import date
from core.common import cota, Perioada


def test_registru_cota_dividend_2025_e_10pct():
    """Registrul: 2024->8% (OG 16/2022), 2025->10% (OUG 156/2024), 2026->16% (Legea 141/2025).
    RED pre-fix: 2025 returna 8% (lipsea intrarea 2025)."""
    assert cota("impozit_dividend", date(2024, 12, 31))[0] == __import__("decimal").Decimal("0.08")
    assert cota("impozit_dividend", date(2025, 12, 31))[0] == __import__("decimal").Decimal("0.10"), \
        "2025 trebuie 10%% (OUG 156/2024), nu 8%%"
    assert cota("impozit_dividend", date(2026, 12, 31))[0] == __import__("decimal").Decimal("0.16")


from core import d205 as _d205, db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d205_cota_2025"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_div_2025():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,regim_fiscal,"
                            "platitor_tva,tip_decont,declarant_nume,declarant_prenume,declarant_functie) VALUES "
                            "(1,'PROBA SRL','14399840','Str 1','Buc','B','6202','real',true,'L','Pop','Ion','administrator')")
                cur.execute("INSERT INTO asociati (nume,cnp,cota) VALUES ('ASOCIAT UNU','1900101410011',100)")
                cur.execute("INSERT INTO inregistrari (data,status,sursa) VALUES ('2025-04-10','validata','test') RETURNING id")
                iid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                            "VALUES (%s,'457','5121',50000)", (iid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d205_2025_impozit_10pct(conn_div_2025):
    """50000 dividende platite in 2025, asociat 100% -> impozit 10% = 5000 (OUG 156/2024).
    RED pre-fix: 8% = 4000."""
    xml, res = _d205.genereaza(conn_div_2025, _SCHEMA, Perioada(2025))
    b = res.beneficiari[0]
    assert b.baza1 == 50000 and b.imp1 == 5000, (
        "50000 dividende 2025, impozit 10%% = 5000; got baza=%s imp=%s (pre-fix 8%%=4000)" % (b.baza1, b.imp1))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_d205_2025_duk_valid(conn_div_2025):
    """Proba DUK: D205 pt 2025 cu impozit 10% e valid la DUKIntegrator."""
    from core import duk
    if not duk.poate_valida("d205"):
        pytest.skip("DUK d205 indisponibil")
    xml, _res = _d205.genereaza(conn_div_2025, _SCHEMA, Perioada(2025))
    rez = duk.valideaza(xml, "d205", an=2025)
    assert rez["stare"] == "valid", "D205 2025 (10%%) trebuie DUK-valid; rez=%r" % rez
