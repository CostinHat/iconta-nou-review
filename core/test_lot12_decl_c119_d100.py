# -*- coding: utf-8 -*-
"""[lotul 12, deficiența C119, găsită de pachetul `pilot`] Baza D100 la microîntreprindere includea TVA-ul din Raportul Z.

Nota Raportului Z trece brutul pe venit și scoate TVA-ul cu o a doua linie: `5311 = 707` 5.826,00 și `707 = 4427` 126,00 (`uc_tenants`).
`repo_d100.select_inregistrari_linii` aduna numai CREDITUL conturilor 70x / 75x / 76x (și scădea numai debitul 709), deci baza ieșea 5.826
-> impozit 58 lei; venitul contului 707 e rulajul lui net, 5.700 -> 57 lei. Aceeași formă de sumă (numai latura funcțiunii) era în calea a
doua a D100 (`d100_reconciliere`), în D101 (`d101.baza_contabila`, deci și D100 pe profit) și în calea a doua a D101 (`d101_reconciliere`),
și în centrele de cost (`centre_cost_api`). Reparația e în calculul bazei — rulajul NET al conturilor de venituri (credit − debit) și de
cheltuieli (debit − credit), fără închiderea în 121 —, nu în nota Z: acoperă și notele Z deja validate, fără migrare.

Temei: CF art.53 alin.(1): „Baza impozabilă a impozitului pe veniturile microîntreprinderilor o constituie veniturile din orice sursă”
(venitul înregistrat al contului 707 = soldul lui creditor, după scoaterea TVA-ului colectat pe 4427); CF art.51 alin.(1): „Cota de impozit pe veniturile microîntreprinderilor este de 1%.”
(registrul `impozit_micro`, citit de generator). Judecătorul formei: validatorul DUK D100 (`core/duk.py`).
Fixtura: schemă efemeră din tenant_template, ROLLBACK; CUI-ul firmei 14399840 cu cifra de control verificată (`test_d100_reconciliere`).
"""
from decimal import Decimal

import pytest

from core import d100 as _d100, d101 as _d101
from core import db as _db, tenant_provisioning as _tp
from core.common import Perioada
from core.test_d100_reconciliere import _db_ok, _profil

_SCHEMA = "efemer_lot12_c119"


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
            yield c
        finally:
            c.rollback()


def _nota_z(cur, data="2026-08-31", brut=5826, tva=126):
    """Nota Raportului Z cum o scrie aplicația: brutul pe 707, TVA-ul scos de pe 707 pe 4427."""
    cur.execute("INSERT INTO inregistrari (data, descriere, status, sursa) VALUES (%s, 'Raport Z', 'validata', 'raport_z') RETURNING id",
                (data,))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'5311','707',%s),"
                "(%s,'707','4427',%s)", (nid, brut, nid, tva))


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c119_baza_micro_e_venitul_net_al_lui_707(conn):
    with conn.cursor() as cur:
        _profil(cur, "micro")
        _nota_z(cur)
    _xml, res = _d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    # CF art.53 alin.(1): veniturile = 5.826 − 126 = 5.700; CF art.51 alin.(1): 1% -> 57 (era 5.826 -> 58)
    assert [(o.cod_oblig, o.suma_dat) for o in res.obligatii] == [("121", 57)]
    # rândurile sintezei (lista afișată sub declarație), fiecare întreg
    assert {"cont 707: 5.700,00 lei", "Baza impozabilă: 5.700,00 lei × cota 1% = cod 121: 57 lei (rotunjit la leu)."} <= set(res.sinteza), \
        res.sinteza


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c119_d100_micro_cu_nota_z_e_valid_pe_duk(conn):
    from core import duk
    with conn.cursor() as cur:
        _profil(cur, "micro")
        _nota_z(cur)
    xml, _res = _d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    v = duk.valideaza(xml, "d100", an=2026, luna=9)
    if v.get("stare") == "gri":
        pytest.skip("validator D100 indisponibil: %s" % v.get("temei"))
    assert v.get("stare") == "valid", v   # DUK D100 — judecătorul final


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c119_d100_profit_pleaca_de_la_venitul_net(conn):
    """Pe profit, rezultatul contabil cumulat (d101.baza_contabila, calea generatorului) și calea a doua (`d100_reconciliere`) pleacă de la
    același venit net: 5.700 -> impozit 16% = 912 (CF art.17); calea a doua nu blochează generarea."""
    with conn.cursor() as cur:
        _profil(cur, "profit")
        _nota_z(cur)
    _xml, res = _d100.genereaza(conn, _SCHEMA, Perioada(2026, trim=3))
    assert res.profit["cumulat"] == 912, res.profit   # CF art.17: 16% din 5.700
    assert {"rezultatul contabil: 5.700,00 lei (venituri 5.700,00 − cheltuieli 0,00)",
            "profitul impozabil cumulat: 5.700,00 lei; impozitul cumulat: 912,00 lei"} <= set(res.sinteza), res.sinteza


def test_def_c119_baza_contabila_d101_pe_rulajul_net():
    """Calea pură a D101: venitul net al lui 707 (credit 5.826, debit 126), 709 debitat se scade, iar cheltuiala stornată (credit pe 6x)
    scade cheltuiala."""
    rl = {"707": (Decimal("126"), Decimal("5826")), "709": (Decimal("50"), Decimal("0")), "607": (Decimal("1000"), Decimal("100")),
          "766": (Decimal("0"), Decimal("10")), "666": (Decimal("5"), Decimal("0"))}
    b = _d101.baza_contabila(rl)
    assert (b["ven_expl"], b["cifra_afaceri"], b["chelt_expl"], b["ven_fin"], b["chelt_fin"]) == (
        Decimal("5650"), Decimal("5650"), Decimal("900"), Decimal("10"), Decimal("5"))
