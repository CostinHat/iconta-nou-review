# -*- coding: utf-8 -*-
"""Gard D205: divid_D (dividend DISTRIBUIT) vs. divid_P (dividend PLATIT) - model corect.

NECONFORMITATE reparata la radacina (HEAD 6cd0054): pull() aduna cont DEBIT 457 (= dividende
PLATITE: a debita datoria 457 = stingere) dar build_xml emitea divid_D (distribuit)=suma si
divid_P (platit)=0. Model corect confruntat cu structura ANAF (anaf_surse/d205_struct_anaf.txt,
rand 39.a/39.b):
  - divid_D "7.V. Dividende distribuite" N(15), >=0 pt. tip_venit1=08  <- CREDIT 457 (117/121=457)
  - divid_P "8.V. Dividende platite"    N(15), >=0 pt. tip_venit1=08  <- DEBIT 457 (457=5121/446)
baza1/imp1 pe dividendul PLATIT (impozit retinut la plata). Regula fully-paid: divid_D>=divid_P;
daca fereastra anului nu contine creditul de distribuire, divid_D=platit.

MUTATIE DOVEDITA: caz cu distribuit(credit 457)=10000 si platit(debit 457)=6000 partial.
  HEAD 6cd0054: pull citeste DOAR debit 457=6000, emite divid_D=6000, divid_P=0
     -> assert divid_P==6000 PICA (primeste 0); assert divid_D==10000 PICA (primeste 6000).
  Post-fix: divid_D=10000, divid_P=6000 -> TRECE.
"""
import re
import pytest

from core.common import Perioada
from core import db as _db, tenant_provisioning as _tp, duk as _duk
from core import d205 as _d205

_SCHEMA = "ztest_d205_divid"
_DUK_OK = _duk.poate_valida("d205")


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_partial():
    """Schema temporara: firma + 1 asociat rezident (CNP valid, cota 100) + dividend DISTRIBUIT
    10000 (credit 457) si PLATIT partial 6000 (debit 457) in 2026. ROLLBACK garantat."""
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(
                    open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute(
                    "INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,"
                    "declarant_nume,declarant_prenume,declarant_functie) "
                    "VALUES (1,'PROBA SRL','14399840','Str. Test 1','Bucuresti','B','Pop','Ion','administrator')")
                cur.execute("INSERT INTO asociati (nume,cnp,cota) VALUES ('POPESCU ION','1700510400076',100)")
                # distribuire: 117 = 457 (CREDIT 457) 10000
                cur.execute("INSERT INTO inregistrari (data,status) VALUES ('2026-03-01','validata') RETURNING id")
                i1 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                            "VALUES (%s,'117','457',10000)", (i1,))
                # plata partiala: 457 = 5121 (DEBIT 457) 6000
                cur.execute("INSERT INTO inregistrari (data,status) VALUES ('2026-06-01','validata') RETURNING id")
                i2 = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id,cont_debit,cont_credit,suma) "
                            "VALUES (%s,'457','5121',6000)", (i2,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_divid_distribuit_si_platit_separate(conn_partial):
    xml, res = _d205.genereaza(conn_partial, _SCHEMA, Perioada(2026))
    b = res.beneficiari[0]
    # MUTATIE: pe HEAD divid_P=0 si divid_D=6000 (din debit 457). Post-fix:
    assert b.divid_p == 6000, "divid_P (platit) = Σ debit 457; got %s" % b.divid_p
    assert b.divid_d == 10000, "divid_D (distribuit) = Σ credit 457; got %s" % b.divid_d
    # baza1/imp1 pe dividendul PLATIT (16% Legea 141/2025): 6000 -> 960
    assert b.baza1 == 6000 and b.imp1 == 960, (b.baza1, b.imp1)
    # emis in XML
    linie = re.search(r'<benef[^>]*/>', xml).group(0)
    assert 'divid_D="10000"' in linie and 'divid_P="6000"' in linie, linie


@pytest.mark.skipif(not _db_ok() or not _DUK_OK, reason="DB sau DUK indisponibil")
def test_divid_partial_ramane_duk_valid(conn_partial):
    xml, _ = _d205.genereaza(conn_partial, _SCHEMA, Perioada(2026))
    rez = _duk.valideaza(xml, "d205", an=2026)
    assert rez["stare"] == "valid", "DUK a respins D205 partial: %s" % rez
