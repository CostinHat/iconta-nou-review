# -*- coding: utf-8 -*-
"""[lotul 12, C144 / C145] Proforma și avizul nu sunt documente de stins în Bancă / Casă și nu intră în pragul Intrastat.

C144: `reconciliere_api.facturi_deschise` lua orice rând din `facturi` cu sold > 0 — proformele și avizele nestinse apăreau printre
documentele de potrivit pe extras / casă. C145: `repo_facturi.emise_pe_luni_pentru_intrastat` număra și proformele (nu sunt documente
fiscale; avizul e urmat de factură, deci s-ar număra de două ori). Fixtura: schema efemeră a testului 443, ROLLBACK.
"""
from core.test_lot11_n_443_existente import SCH, conn  # noqa: F401  (fixtura `conn`)


def _document(conn, tip, numar, total=1210, directie="emisa"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, total_lei, tva_lei, moneda, directie, status, tip, tert_nume, "
                    "tert_cui) VALUES (%s, '2099-10-10', %s, 210, %s, 210, 'RON', %s, 'emisa', %s, 'Client P SRL', '18547290') "
                    "RETURNING id", (numar, total, total, directie, tip))
        return cur.fetchone()[0]


def test_def_c144_proforma_si_avizul_nu_sunt_de_stins_in_banca(conn):
    """MUTAȚIE: filtrul `clauza_tip_cu_incasare` scos din `facturi_deschise` -> pică (proforma și avizul apar)."""
    from core import reconciliere_api
    fid = _document(conn, "factura", "P-1")
    _document(conn, "proforma", "PF-1")
    _document(conn, "aviz", "AV-1")
    deschise = {r["id"] if isinstance(r, dict) else r[0] for r in reconciliere_api.facturi_deschise(conn, SCH)}
    assert fid in deschise, deschise
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM facturi WHERE tip IN ('proforma', 'aviz')")
        altele = {r[0] for r in cur.fetchall()}
    assert not (altele & deschise), (altele, deschise)


def test_def_c145_pragul_intrastat_numara_numai_facturile(conn):
    """MUTAȚIE: `clauza_tip_document` înlocuit cu `TRUE` în `emise_pe_luni_pentru_intrastat` -> pică (baza proformei se adună)."""
    from core import repo_facturi
    _document(conn, "factura", "P-2")
    _document(conn, "proforma", "PF-2")
    with conn.cursor() as cur:
        randuri = repo_facturi.emise_pe_luni_pentru_intrastat(cur, SCH, 2099)
    baze = [float(r[3] if not isinstance(r, dict) else r["baza"]) for r in randuri]
    assert baze == [1000.0], randuri
