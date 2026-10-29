"""[714, comanda 14.2] CF art.297 alin.(3): la o firmă cu TVA la încasare, TVA-ul unei achiziții nu se deduce pe loc (4426 = 401 / 404) printr-o
notă din Operațiuni; factura furnizorului intră pe drumul facturii primite (4428 -> 4426 la plată). Pe Postgres, schemă sintetică, rollback."""
import ast
import datetime as _dt
import io
import os

import pytest

from core import db as _db, erori as _erori, tenant_provisioning as _tp, tva_incasare as _tvi
from core.test_lot11_t import _db_ok

_SCHEMA = "tenant_test_lot14_2_714"
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def cur_t():
    _db.init_pool()
    with _db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO tva_incasare_perioade (de_la, pana_la, sursa) VALUES ('2026-10-01', NULL, 'manual')")
                yield cur
        finally:
            conn.rollback()


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_nota_cu_4426_la_firma_in_sistem_e_refuzata_cu_drumul_corect(cur_t):
    linii = [("605", "401", 1000), ("4426", "401", 210)]
    m = _tvi.refuz_nota_tva_la_primire(cur_t, None, _dt.date(2026, 10, 21), linii)
    assert m == ("Firma aplică sistemul TVA la încasare la 21.10.2026: factura furnizorului se înregistrează în Facturi primite, nu ca notă. Acolo TVA-ul "
                 "merge pe 4428 și se deduce (4426) abia când plătești factura, proporțional cu plata (Cod fiscal art. 297 alin. (3)); nota de "
                 "aici l-ar deduce imediat."), m
    assert _tvi.refuz_nota_tva_la_primire(cur_t, None, _dt.date(2026, 9, 30), linii) is None, "înainte de intrarea în sistem: regulile generale"
    assert _tvi.refuz_nota_tva_la_primire(cur_t, None, _dt.date(2026, 10, 21), [("605", "401", 1000)]) is None, "fără TVA de dedus"
    assert _tvi.refuz_nota_tva_la_primire(cur_t, None, _dt.date(2026, 10, 21), [("4426", "4427", 210)]) is None, "taxarea inversă nu e amânată"
    assert _tvi.refuz_nota_tva_la_primire(cur_t, None, _dt.date(2026, 10, 21), [("167", "404", 100), ("4426", "404", 21)]), "rata de leasing"
    from core import uc_tenants as _ut
    with pytest.raises(_erori.DateInvalide):
        _ut._refuza_deducere_imediata(cur_t, None, _dt.date(2026, 10, 21), linii)


def test_fiecare_ruta_din_operatiuni_cu_tva_pe_achizitie_trece_prin_refuz():
    """Clasa: orice funcție din `uc_tenants` care generează o notă cu TVA deductibil pe achiziție (refacturare, chiria plătită, leasing,
    obiecte de inventar) cheamă `_refuza_deducere_imediata`. MUTAȚIE: apelul scos dintr-o rută -> ROȘU."""
    arb = ast.parse(io.open(os.path.join(RAD, "core", "uc_tenants.py"), encoding="utf-8").read())
    generatoare = {"nota_refacturare", "nota_chirie_platita", "nota_rata_financiar", "nota_rata_operational", "nota_reziduala", "nota_achizitie"}
    apeluri = {f.name: {getattr(c.func, "attr", getattr(c.func, "id", "")) for c in ast.walk(f) if isinstance(c, ast.Call)}
               for f in ast.walk(arb) if isinstance(f, ast.FunctionDef)}
    scriu = {nume: ch for nume, ch in apeluri.items() if ch & generatoare}
    fara_refuz = sorted(nume for nume, ch in scriu.items() if "_refuza_deducere_imediata" not in ch)
    assert fara_refuz == [], "scriu nota unei achiziții fără refuzul TVA la încasare: %s" % fara_refuz
    assert set().union(*(ch & generatoare for ch in scriu.values())) == generatoare
