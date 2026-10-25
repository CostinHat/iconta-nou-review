# -*- coding: utf-8 -*-
"""[lotul 12, C102.1] Certificatul de concediu medical: zilele lucrătoare CM peste zilele lucrătoare ale intervalului nu se salvează tăcut.

Costin, comanda 12.2 pct.8: „10 zile pe un interval cu 5 zile lucrătoare trec fără avertisment.” Serverul (`salariati_api.salveaza_concediu`)
răspunde cu `cod` = CONFIRMA_ZILE_PESTE_INTERVAL și întrebarea, fără să scrie certificatul; cu `confirma_zile_peste_interval` îl salvează.
Intervalul se numără pe calendarul unic al aplicației (`scadente.zile_lucratoare_interval`: L–V, fără sărbătorile legale). Indemnizația se
înmulțește cu „numărul de zile lucrătoare din concediul medical” (normele OUG 158/2005, Ordinul 506/1030/2026, art.78^4 alin.(4),
`anaf_surse/ordin_506_1030_2026_norme_oug158.txt`); sărbătorile: Legea 53/2003 art.139 alin.(1). Nu se refuză: Legea 53/2003 art.141 —
„Prevederile art. 139 nu se aplică în locurile de muncă în care activitatea nu poate fi întreruptă” —, deci cifra poate fi corectă.

CNP-ul de test are cifra de control verificată (algoritmul din CLAUDE.md): 1800101410013.
"""
import datetime

import pytest

from core import db as _db, salariati_api, scadente
from core.test_lot11_s9_deducere_plafon import _setup

_SCHEMA = "test_lot12_sal2_c102"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                _setup(cur, [{"cnp": "1800101410013", "nume": "IONESCU", "dn": "1980-06-01", "brut": 5000}], schema=_SCHEMA)
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _certificat(conn, de, pana, zile, **extra):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM salariati")
        sid = cur.fetchone()[0]
    return salariati_api.salveaza_concediu(conn, sid, {
        "serie": "AB", "numar": "102", "cod": "01", "data_acordare": de, "data_inceput": de, "data_sfarsit": pana,
        "zile_cm": zile, "venituri_6_luni": 30000, "zile_6_luni": 125, "an": int(de[:4]), "luna": int(de[5:7]), **extra})


def _certificate(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT zile FROM concedii_medicale ORDER BY id")
        return [r[0] for r in cur.fetchall()]


def test_c102_1_calendarul_intervalului_scade_sarbatorile():
    """30.11–04.12.2026: luni–vineri, dar 30 noiembrie și 1 decembrie sunt sărbători legale (Legea 53/2003 art.139 alin.(1)) -> 3 zile
    lucrătoare; 05–11.10.2026 (luni–duminică) -> 5."""
    assert scadente.zile_lucratoare_interval(datetime.date(2026, 11, 30), datetime.date(2026, 12, 4)) == 3
    assert scadente.zile_lucratoare_interval(datetime.date(2026, 10, 5), datetime.date(2026, 10, 11)) == 5


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c102_1_zile_peste_interval_cer_confirmarea(conn):
    """10 zile pe 05–11.10.2026 (5 zile lucrătoare): nu se scrie nimic, răspunsul întreabă și numește cele două cifre. ROȘU înainte:
    certificatul se salva cu 10 zile, fără niciun cuvânt."""
    r = _certificat(conn, "2026-10-05", "2026-10-11", 10)
    assert r["cod"] == "CONFIRMA_ZILE_PESTE_INTERVAL" and r["ok"] is False, r
    assert (r["zile_cm"], r["zile_interval"]) == (10, 5), r
    assert r["mesaj"] == ("Ai scris 10 zile lucrătoare de concediu medical, dar între 05.10.2026 și 11.10.2026 sunt 5 zile lucrătoare "
                          "(fără weekend și sărbători legale). Verifică cifra de pe certificat. Salvezi certificatul cu 10 zile?"), r
    assert _certificate(conn) == [], "certificatul s-a salvat fără confirmare"


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c102_1_confirmat_se_salveaza_cu_cifra_omului(conn):
    """Contabilul confirmă („Salvează cu 10 zile”): certificatul se salvează cu cifra lui, neschimbată."""
    r = _certificat(conn, "2026-10-05", "2026-10-11", 10, confirma_zile_peste_interval=True)
    assert r["ok"] is True and r.get("cod") is None, r
    assert _certificate(conn) == [10]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_def_c102_1_sarbatorile_numara_in_avertisment(conn):
    """5 zile pe 30.11–04.12.2026 (3 zile lucrătoare, cu două sărbători legale): întrebarea vine; 3 zile se salvează direct."""
    r = _certificat(conn, "2026-11-30", "2026-12-04", 5)
    assert (r.get("cod"), r.get("zile_interval")) == ("CONFIRMA_ZILE_PESTE_INTERVAL", 3), r
    r = _certificat(conn, "2026-11-30", "2026-12-04", 3)
    assert r["ok"] is True and r.get("cod") is None, r
    assert _certificate(conn) == [3]
