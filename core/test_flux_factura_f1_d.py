# -*- coding: utf-8 -*-
"""GARDA pasului D din comanda Costin 05.10.2026 („fluxul de factură pe F1”, pct.10–11), pe schemă efemeră.

Costin, verbatim (DECIZII 05.10.2026): „10. … ecranul se deschide cu situația stocului (articol, UM, cantitate, CMP, valoare),
formularele (NIR, mișcări, coduri, nivel minim) stau sub ea, la cerere; Rețete apare doar la firmele HoReCa. Confirmă în raport
că «Descarcă gestiunea lunii» nu descarcă a doua oară marfa descărcată deja la emiterea facturii.”

Temeiul listei HoReCa: CF art.48 alin.(2^2) (codurile CAEN 5510, 5520, 5530, 5590, 5610, 5621, 5629, 5630) și CF art.54
alin.(4) (de la 1 ianuarie 2025, și 5611, 5612, 5622) — `anaf_surse/cod_fiscal_227_2015_consolidat.txt`.
"""
import datetime
import io
import os
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = "efemer_flux_f1_d"
ZI = datetime.date(2026, 10, 5)


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris) "
                        "VALUES (1, 'ZT Stoc SRL', '14399840', true, 'SRL', 200)")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nota(conn, data, sursa, linii, status="validata", factura_id=None):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id) VALUES (%s,'n',%s,%s,%s) RETURNING id",
                    (data, sursa, status, factura_id))
        nid = cur.fetchone()[0]
        for d, c, s in linii:
            cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s,%s,%s,%s)",
                        (nid, d, c, Decimal(str(s))))
    return nid


def _stoc_global_valoric(conn):
    """Marfă intrată la preț de vânzare (GV): cost 1000, adaos 200, TVA neexigibilă 264 (21% din 1200+…)."""
    _nota(conn, "2026-10-01", "stocuri", [("371", "401", 1000), ("371", "378", 200), ("371", "4428", 252)])


# ── HoReCa ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_horeca_dupa_codul_caen_din_codul_fiscal():
    """MUTAȚIE: un cod scos din listă (5630) -> pică."""
    from core import horeca
    assert horeca.CODURI == frozenset({"5510", "5520", "5530", "5590", "5610", "5621", "5629", "5630",   # CF art.48 alin.(2^2)
                                       "5611", "5612", "5622"})                                        # CF art.54 alin.(4)
    assert horeca.e_horeca("5610") and horeca.e_horeca(" 5630 ") and horeca.e_horeca("5611")
    assert not horeca.e_horeca("4711") and not horeca.e_horeca(None) and not horeca.e_horeca("")


def test_situatia_stocului_spune_daca_retetele_se_arata(conn):
    """Rețetele: la firma HoReCa (CAEN din listă) sau la cea care are deja rețete (datele nu se ascund).
    MUTAȚIE: `retete_vizibile` constant True -> pică pe firma fără CAEN HoReCa."""
    from core import stocuri_cv_api as cv
    assert cv.retete_vizibile(conn, SCH) is False
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET caen = '5610'")
    assert cv.retete_vizibile(conn, SCH) is True
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET caen = '4711'")
        cur.execute("INSERT INTO retete (denumire, pret_fara_tva) VALUES ('Meniu', 30)")
    assert cv.retete_vizibile(conn, SCH) is True


# ── „Descarcă gestiunea lunii” ────────────────────────────────────────────────────────────────────────────────────────────
def test_descarcarea_lunii_nu_include_vanzarea_facturata(conn):
    """Confirmarea cerută de Costin, ca probă: vânzarea din factură (nota de contare are sursa `facturi`; marfa ei s-a
    descărcat la emitere, 607=371 pe articol) NU intră în baza descărcării lunare. Cu numai o factură în lună, descărcarea
    spune „fără vânzări de mărfuri”. MUTAȚIE: `facturi` adăugat în sursele vânzărilor -> descarcă -> pică."""
    from core import stocuri_api as sa
    _stoc_global_valoric(conn)
    _nota(conn, ZI, "facturi", [("4111", "707", 500), ("4111", "4427", 105)])
    r = sa.descarca_luna(conn, SCH, 2026, 10)
    assert r.get("note") == [] and r.get("k") is None, r


def test_a_doua_descarcare_a_aceleiasi_luni_se_refuza(conn):
    """Înainte, a doua apăsare scria al doilea set de ciorne 607/378/4428=371 (nicio gardă). MUTAȚIE: verificarea
    scoasă -> a doua rulare scrie din nou -> pică."""
    from core import stocuri_api as sa
    _stoc_global_valoric(conn)
    _nota(conn, ZI, "horeca_z", [("5311", "707", 500), ("5311", "4427", 105)])
    r1 = sa.descarca_luna(conn, SCH, 2026, 10)
    assert r1.get("inregistrari"), r1
    r2 = sa.descarca_luna(conn, SCH, 2026, 10)
    assert r2.get("cod") == "DEJA_DESCARCATA" and r2["inregistrari_existente"] == r1["inregistrari"], r2
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM inregistrari WHERE numar = 'DESC-GV-2026-10'")
        assert cur.fetchone()[0] == len(r1["inregistrari"])


def test_descarcarea_din_factura_nu_se_face_de_doua_ori(conn):
    """MUTAȚIE: verificarea mișcărilor existente scoasă -> a doua chemare descarcă din nou -> pică."""
    from core import stocuri_cv_api as cv
    art = cv.intrare(conn, SCH, {"denumire": "Pâine", "data": "2026-10-01", "cantitate": 10, "pret_unitar": 2})
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tva) VALUES ('Z1', %s, 'emisa', 10, 0) RETURNING id", (ZI,))
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva, articol_id) "
                    "VALUES (%s, 'Pâine', 2, 5, 11, %s)", (fid, art["articol_id"]))
    assert len(cv.descarca_factura(conn, SCH, fid, ZI)["descarcate"]) == 1
    r = cv.descarca_factura(conn, SCH, fid, ZI)
    assert r["descarcate"] == [] and r.get("deja_descarcata") is True
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM miscari_stoc WHERE factura_id = %s AND tip = 'iesire'", (fid,))
        assert cur.fetchone()[0] == 1
