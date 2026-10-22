# -*- coding: utf-8 -*-
"""[lotul 11, subagentul w3b, deficiența 440 pe server — comanda Costin 11.1 pct.16, verbatim] „toate erorile apar deodată, fiecare cu
textul ei, în casetă și lângă câmp.” Produse (B30 din lista U0): `produse_api.creeaza` refuza la denumirea lipsă („denumire lipsă”) și
nimic altceva; un UM mai lung de 10 caractere sau un preț cu peste 10 cifre întregi cădea în INSERT / UPDATE (DataError -> 500), iar la
editare denumirea golită se scria goală. Acum: denumirea, UM-ul, prețul și categoria cotei, toate deodată, lângă `pr-den`, `pr-um`,
`pr-pret`, `pr-cota` / `pr-c331`.

Temei: N/A — contractul refuzului (G10) și limitele coloanelor (`tenant_template.sql`: `um character varying(10)`,
`pret_unitar numeric(12,2)`), confruntate mai jos cu schema bazei, ca limita din cod să nu poată deriva.
"""
import io
import os
import re

import pytest

from core import db as _db, produse_api as pa, tenant_provisioning as _tp

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCH = "efemer_lot11_w3b_prod"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    if not _db_ok():
        pytest.skip("DB indisponibil")
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), _SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            yield c
        finally:
            c.rollback()


def _campuri(r):
    return [c["camp"] for c in r["erori_campuri"]]


def test_b30_produsul_nou_refuza_toate_greselile_deodata(conn):
    """Fără denumire + UM de 13 caractere + preț de 11 cifre + categorie la cota nenulă: patru erori, nimic scris.
    MUTAȚIE: `return` pe denumirea lipsă (forma veche) -> pică."""
    r = pa.creeaza(conn, " ", um="bucăți-pachet", pret_unitar=1e11, cota_tva=21, categorie_tva="scutit_cu_drept")
    assert r["ok"] is False and r["cod"] == "GOL" and _campuri(r) == ["pr-den", "pr-um", "pr-pret", "pr-cota"], r   # 440
    assert r["mesaj"].split("\n— ") == [                                                                         # textul fiecăreia
        "Produsul nu s-a salvat:", "Scrie denumirea produsului sau a serviciului.",
        "Unitatea de măsură are cel mult 10 caractere (ex. buc, kg, ore, mp); „bucăți-pachet” are 13.",
        "Prețul are cel mult 10 cifre înaintea virgulei (sub 10.000.000.000 lei).",
        "Categoria (Scutit cu drept de deducere (art.294 alin.(1), 295, 296)) se alege numai la cota 0%: o cotă de 21% e o livrare taxabilă."], \
        r["mesaj"]
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM produse")
        assert cur.fetchone()[0] == 0


def test_b30_editarea_refuza_denumirea_golita_si_um_ul_lung(conn):
    """Denumirea golită (înainte se scria goală) + UM peste coloană (înainte 500): două erori, produsul neschimbat.
    MUTAȚIE: `_erori_produs(...)` scos din `actualizeaza` -> pică."""
    p = pa.creeaza(conn, "Pâine albă", um="buc", pret_unitar=3, cota_tva=0, confirmat=True)
    assert p["ok"], p
    r = pa.actualizeaza(conn, p["id"], denumire="  ", um="x" * 11)
    assert r["ok"] is False and r["cod"] == "DATE_INVALIDE" and _campuri(r) == ["pr-den", "pr-um"], r
    with conn.cursor() as cur:
        cur.execute("SELECT denumire, um FROM produse WHERE id = %s", (p["id"],))
        assert cur.fetchone() == ("Pâine albă", "buc")


def test_b30_use_case_trimite_toate_erorile_ecranului(conn, monkeypatch):
    """Ruta POST /produse: refuzul are `erori_campuri` (ecranul le pune lângă câmpuri, `api._campuriAutomat`), nu numai fraza."""
    import contextlib
    from types import SimpleNamespace
    from core import erori, uc_comun, uc_tenants

    @contextlib.contextmanager
    def _gc(schema=None):
        yield conn
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: _SCH)
    monkeypatch.setattr(uc_tenants.cote_tva, "intreaba", lambda d: {})
    date = SimpleNamespace(denumire="Produs W3B", um="kilogramexx", pret_unitar=99999999999.0, cota_tva=21, categorie=None,
                           confirmat=True, categorie_tva=None, categorie_331=None)
    with pytest.raises(erori.CerereGresita) as e:
        uc_tenants.produse_creeaza(1, date, {"uid": 1})
    assert [c["camp"] for c in e.value.detaliu["erori_campuri"]] == ["pr-um", "pr-pret"], e.value.detaliu


def test_limitele_din_cod_sunt_ale_coloanelor(conn):
    """Garda: `LIMITE_UM` și `LIMITE_PRET` sunt cele din `tenant_template.sql` ȘI din schema creată (information_schema). MUTAȚIE:
    `LIMITE_UM = 12` -> pică."""
    sablon = io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read()
    bloc = re.search(r"CREATE TABLE TENANT_PLACEHOLDER\.produse \((.*?)\);", sablon, re.S).group(1)
    assert re.search(r"\bum character varying\((\d+)\)", bloc).group(1) == str(pa.LIMITE_UM)
    prec, scala = re.search(r"\bpret_unitar numeric\((\d+),(\d+)\)", bloc).groups()
    assert pa.LIMITE_PRET == 10 ** (int(prec) - int(scala))
    with conn.cursor() as cur:
        cur.execute("SELECT column_name, character_maximum_length, numeric_precision, numeric_scale FROM information_schema.columns "
                    "WHERE table_schema = %s AND table_name = 'produse' AND column_name IN ('um', 'pret_unitar') ORDER BY 1", (_SCH,))
        assert cur.fetchall() == [("pret_unitar", None, int(prec), int(scala)), ("um", pa.LIMITE_UM, None, None)]
