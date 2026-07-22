# -*- coding: utf-8 -*-
"""Teste gardian F183 — audit_preluare (nucleele PURE, date minime construite manual).

Principii aparate (aceeasi anatomie ca control_incrucisat): TREI stari
coerent=verde / divergent=rosu / NEVERIFICAT=gri; gri NU se ascunde ca verde; un sold
fiscal fara declaratia care-l explica -> gri (SEMNAL), NICIODATA rosu automat.
"""
from decimal import Decimal
from core.audit_preluare import (
    constatare_parteneri, constatare_istoric_fiscal, constatare_rip, audit,
)


# ---- parteneri: coincide None/True/False -> gri/verde/rosu ----

def test_parteneri_coincide_da_verde():
    r = constatare_parteneri([{"cont": "4111", "suma_parteneri": 100.0,
                               "sold_balanta": 100.0, "diferenta": 0.0, "coincide": True}])
    assert r[0]["stare"] == "verde"
    assert r[0]["remediu"] is None


def test_parteneri_divergent_da_rosu_fara_ajustare():
    r = constatare_parteneri([{"cont": "401", "suma_parteneri": 50.0,
                               "sold_balanta": 80.0, "diferenta": -30.0, "coincide": False}])
    c = r[0]
    assert c["stare"] == "rosu"
    assert c["remediu"]["fel"] == "investigatie"
    # NICIODATA "ajusteaza contul ca sa dea verde"
    txt = (c["remediu"]["actiune"] + c["remediu"]["cauza"]).lower()
    assert "ajusteaz" not in txt


def test_parteneri_fara_sold_balanta_da_gri():
    r = constatare_parteneri([{"cont": "4111", "suma_parteneri": 100.0,
                               "sold_balanta": None, "diferenta": None, "coincide": None}])
    assert r[0]["stare"] == "gri"


# ---- istoric fiscal: SEMNAL gri, niciodata rosu ----

def test_istoric_lipsa_da_gri():
    r = constatare_istoric_fiscal({"4423": Decimal("100")}, set())
    assert any(c["stare"] == "gri" for c in r)
    assert all(c["stare"] != "rosu" for c in r)  # niciodata rosu pe istoric


def test_sold_fiscal_fara_declaratie_da_semnal_gri():
    # sold pe 4315 (CAS) dar D112 NU e in istoric -> gri, referind D112
    r = constatare_istoric_fiscal({"4315": Decimal("500")}, {"D300"})
    semnal = [c for c in r if "4315" in c["mesaj"]]
    assert semnal and semnal[0]["stare"] == "gri"
    assert "D112" in semnal[0]["mesaj"]


def test_sold_fiscal_cu_declaratie_da_verde():
    r = constatare_istoric_fiscal({"4423": Decimal("100")}, {"D300"})
    assert len(r) == 1 and r[0]["stare"] == "verde"


def test_sold_fiscal_sub_toleranta_ignorat():
    # sold zero pe conturile fiscale, dar exista istoric -> verde (nimic de semnalat)
    r = constatare_istoric_fiscal({"4423": Decimal("0.00")}, {"D300"})
    assert len(r) == 1 and r[0]["stare"] == "verde"


# ---- RIP: sold implicit negativ -> rosu; neclasificat -> gri ----

def test_rip_sold_pozitiv_da_verde():
    r = constatare_rip(Decimal("1000"), Decimal("400"), 10, 0)
    assert r[0]["stare"] == "verde"
    assert len(r) == 1


def test_rip_sold_negativ_da_rosu():
    r = constatare_rip(Decimal("400"), Decimal("1000"), 10, 0)
    assert r[0]["stare"] == "rosu"
    assert r[0]["remediu"]["fel"] == "investigatie"


def test_rip_neclasificat_adauga_gri():
    r = constatare_rip(Decimal("1000"), Decimal("400"), 10, 3)
    stari = [c["stare"] for c in r]
    assert "verde" in stari and "gri" in stari


# ---- orchestrator: grupare pe cele trei categorii + prioritate stare ----

class _FakeCur:
    def __init__(self, rows_map): self.rows_map = rows_map; self._rows = []
    def execute(self, sql, params=None):
        s = sql.lower()
        if "to_regclass" in s:
            self._rows = [(None,)]  # niciun tabel -> forteaza caile gri
        elif "declaratii_depuse" in s:
            self._rows = []
        else:
            self._rows = []
    def fetchone(self): return self._rows[0] if self._rows else None
    def fetchall(self): return self._rows
    def __enter__(self): return self
    def __exit__(self, *a): return False


class _FakeConn:
    def cursor(self, **kw): return _FakeCur({})


def test_audit_fara_documente_da_gri_nu_verde():
    # nicio sursa importata -> totul gri (NEVERIFICAT), stare gri, NU verde tacut
    r = audit(_FakeConn(), "tenant_x", 1, _FakeConn())
    assert r["stare"] == "gri"
    assert r["divergent"] == 0 and r["coerent"] == 0
    assert r["neverificat"] >= 1
    assert r["modul"] == "audit_preluare"
