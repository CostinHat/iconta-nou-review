# -*- coding: utf-8 -*-
"""core/test_d101_reconciliere.py — gardul A DOUA CALE D101 (05.08.2026, pas 5/6).
Acopera PROFITUL CONTABIL (P1/P2/P4/P5 din balanta), NU impozabilul (ajustari manuale + golden)."""
import io
import ast
import pytest

from core.common import Perioada
from core import d101 as _d101
from core import d101_reconciliere as _rec
from core.d101_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD101


def test_non_tautologie_calea2_nu_foloseste_generatorul_d101():
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name)
    assert "core.d101" not in mods
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d101", "pull"):
        assert interzis not in folosite, "calea 2 foloseste '%s'" % interzis


from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d101_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _nota(cur, data, cd, cc, suma):
    cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES (%s,'n','validata') RETURNING id", (data,))
    nid = cur.fetchone()[0]
    cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                (nid, cd, cc, suma))


@pytest.fixture
def conn_recon():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,platitor_tva,tip_decont,regim_fiscal,declarant_nume,declarant_prenume,declarant_functie) "
                            "VALUES (1,'TEST SRL','14399840','Str 1','Buc','B','6920',true,'L','real','Popescu','Ion','ADMINISTRATOR')")
                _nota(cur, '2026-03-05', '4111', '707', 1000)   # ven exploatare
                _nota(cur, '2026-04-10', '607', '401', 400)     # chelt exploatare
                _nota(cur, '2026-05-12', '5121', '766', 50)     # ven financiar
                _nota(cur, '2026-06-12', '666', '5121', 20)     # chelt financiar
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_si_genereaza_trece(conn_recon):
    xml, res = _d101.genereaza(conn_recon, _SCHEMA, Perioada(2026))   # poarta wired -> crapa daca fals-pozitiv
    assert (res.P["P1"], res.P["P2"], res.P["P4"], res.P["P5"]) == (1000, 400, 50, 20)
    rap = reconciliaza(conn_recon, _SCHEMA, Perioada(2026), res)
    assert rap["divergente"] == [], rap["divergente"]
    assert "declaratie" in xml.lower()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_venituri_gresite_pica(conn_recon):
    _xml, res = _d101.genereaza(conn_recon, _SCHEMA, Perioada(2026))
    res.P["P1"] = 9999   # <- mutatie: venituri exploatare gresite
    with pytest.raises(ReconciliereD101) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, Perioada(2026), res)
    msg = str(ei.value)
    assert "P1 (venituri exploatare): generator=9999 vs cale2=1000" in msg, msg


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_baza_suprascrisa_manual_e_sarita(conn_recon):
    """Daca contabilul suprascrie P1 prin manual, calea 2 il SARE (nu alarma falsa pe input propriu)."""
    _xml, res = _d101.genereaza(conn_recon, _SCHEMA, Perioada(2026))
    res.P["P1"] = 5000
    rap = reconciliaza(conn_recon, _SCHEMA, Perioada(2026), res, manual={"P1": 5000})
    assert "P1" in rap["sarite"] and all(d["rand"] != "P1" for d in rap["divergente"])
