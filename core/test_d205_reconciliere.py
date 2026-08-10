# -*- coding: utf-8 -*-
"""core/test_d205_reconciliere.py — gardul A DOUA CALE D205 (05.08.2026, pas 6/6).
Recalcul propriu al bazei/impozitului pe dividende (NU cross-check cu D100 = same-source trap)."""
import io
import ast
import pytest

from core.common import Perioada
from core import d205 as _d205
from core import d205_reconciliere as _rec
from core.d205_reconciliere import reconciliaza, verifica_reconciliere, ReconciliereD205


def test_non_tautologie_calea2_nu_foloseste_generatorul_d205():
    tree = ast.parse(io.open(_rec.__file__, encoding="utf-8").read())
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and n.module:
            mods.add(n.module)
        elif isinstance(n, ast.Import):
            for a in n.names:
                mods.add(a.name)
    assert "core.d205" not in mods
    folosite = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} \
             | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
    for interzis in ("calcul_d205", "pull"):
        assert interzis not in folosite, "calea 2 foloseste '%s'" % interzis


from core import db as _db, tenant_provisioning as _tp
_SCHEMA = "test_d205_recon"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn_recon():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,"
                            "declarant_nume,declarant_prenume,declarant_functie) "
                            "VALUES (1,'TEST SRL','14399840','Str 1','Buc','B','POP','ION','ADMINISTRATOR')")
                cur.execute("INSERT INTO asociati (nume, cnp, cota) VALUES ('POPESCU','1900101410011',60),('IONESCU','2900101410011',40)")
                # total dividende distribuite (cont 457) = 10000, in an
                cur.execute("INSERT INTO inregistrari (data, descriere, status) VALUES ('2026-04-01','div','validata') RETURNING id")
                nid = cur.fetchone()[0]
                cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,'457','5121',10000)", (nid,))
            yield conn
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_reconciliere_curata_si_genereaza_trece(conn_recon):
    xml, res = _d205.genereaza(conn_recon, _SCHEMA, Perioada(2026))   # poarta wired
    # 2026: cota dividende 16%. POPESCU 60% -> baza 6000, imp 960 ; IONESCU 40% -> 4000, 640.
    porc = {b.cif: (int(b.baza1), int(b.imp1)) for b in res.beneficiari}
    assert porc.get("1900101410011") == (6000, 960), porc
    assert porc.get("2900101410011") == (4000, 640), porc
    rap = reconciliaza(conn_recon, _SCHEMA, Perioada(2026), res)
    assert rap["acoperit"] is True and rap["divergente"] == [], rap["divergente"]
    assert "declaratie205" in xml


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_impozit_gresit_pica(conn_recon):
    _xml, res = _d205.genereaza(conn_recon, _SCHEMA, Perioada(2026))
    res.beneficiari[0].imp1 = 1   # <- mutatie: impozit gresit pe primul beneficiar
    with pytest.raises(ReconciliereD205) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, Perioada(2026), res)
    assert "impozit: generator=1 vs cale2=" in str(ei.value), str(ei.value)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_mutatie_beneficiar_pierdut_pica(conn_recon):
    """Generatorul pierde un beneficiar cu dividende -> calea 2 il gaseste in 457+asociati."""
    _xml, res = _d205.genereaza(conn_recon, _SCHEMA, Perioada(2026))
    res.beneficiari = res.beneficiari[:1]   # <- mutatie: al doilea beneficiar dispare
    with pytest.raises(ReconciliereD205) as ei:
        verifica_reconciliere(conn_recon, _SCHEMA, Perioada(2026), res)
    assert "beneficiar LIPSA" in str(ei.value), str(ei.value)
