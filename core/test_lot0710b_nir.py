# -*- coding: utf-8 -*-
"""GARD — NIR-ul urmează evaluarea stocului firmei (lotul 07.10 B, comanda Costin C10/C11).

Constatarea (retest 07.10, F1 cantitativ-valoric, CMP): NIR 1, Marfa A 10×55, raft 80 a scris 371=401 550 · 4426=401 115,50 ·
371=378 111,16 · 371=4428 138,84 — 371 încărcat la preț de vânzare, iar ieșirile scot la CMP (607=371): soldul 371 nu mai poate
corespunde stocului. Decizia: „evaluarea stocului … e setare a firmei și se aplică identic la intrări și ieșiri. La cost: NIR la
cost, fără 378/4428, prețul de raft nu se cere și nu se verifică.” Setarea e `metoda_stoc` (cantitativ-valoric = cost CMP,
global-valoric = preț cu amănuntul). Temei: OMFP 1802/2014 pct.287 alin.(1)-(2) — „Metoda aleasă trebuie aplicată cu consecvență”.
"""
import io
from decimal import Decimal

import pytest

from core import db as _db
from core import tenant_provisioning as _tprov

_SCH = "efemer_lot0710b_nir"
_L = {"cantitate": 10, "pret_achizitie": 55, "cota_tva": 21}


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("INSERT INTO %s.firma_profil (id, nume, cui) VALUES (1, 'NIR SRL', '14399840')" % _SCH)
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _metoda(conn, m):
    with conn.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = %s", (m,))


def _note(conn, ids):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma::text FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id", (ids,))
        return [tuple(x) for x in cur.fetchall()]


def test_la_cost_nir_intra_la_cost_fara_378_4428_si_in_fisa(conn):
    """Cazul F1: același NIR, la firma cantitativ-valorică. MUTAȚIE: `motor = _m.nir_gv` mereu -> apar 378 și 4428 -> pică."""
    from core import stocuri_api as s
    _metoda(conn, "cantitativ_valoric")
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", articol_nou=True)]})
    assert "eroare" not in r, r
    assert _note(conn, r["inregistrari"]) == [("371", "401", "550.00"), ("4426", "401", "115.50")]   # OMFP 1802 pct.287
    with conn.cursor() as cur:
        cur.execute("SELECT a.denumire, m.tip, m.cantitate::text, m.valoare::text FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id")
        assert [tuple(x) for x in cur.fetchall()] == [("Marfa A", "intrare", "10.000", "550.00")]          # C11e: stocul o arată


def test_la_cost_articolul_nu_se_creeaza_tacit(conn):
    """C11c: „Marfa  A” (două spații) ca articol NOU lângă „Marfa A” se refuză lângă câmp; fără alegere se refuză; ales -> intră."""
    from core import stocuri_api as s
    _metoda(conn, "cantitativ_valoric")
    s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", articol_nou=True)]})
    r = s.adauga_nir(conn, _SCH, {"numar": "2", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa  A", articol_nou=True)]})
    assert [x["camp"] for x in r["erori_campuri"]] == ["nir-l0-denumire"]
    r = s.adauga_nir(conn, _SCH, {"numar": "2", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A")]})
    assert [x["camp"] for x in r["erori_campuri"]] == ["nir-l0-articol"]
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM articole")
        (aid,), = cur.fetchall()
    assert "eroare" not in s.adauga_nir(conn, _SCH, {"numar": "2", "data": "2099-10-07", "linii": [dict(_L, articol_id=aid)]})
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), sum(cantitate)::text FROM miscari_stoc WHERE articol_id = %s", (aid,))
        assert cur.fetchone() == (2, "20.000")


def test_la_pret_de_vanzare_raftul_gol_nu_e_zero(conn):
    """C11a: la global-valoric prețul de raft gol se cere lângă câmp — nu mai devine 0 și nu mai iese „sub costul de achiziție”."""
    from core import stocuri_api as s
    _metoda(conn, "global_valoric")
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", pret_vanzare=None)]})
    assert [x["camp"] for x in r["erori_campuri"]] == ["nir-l0-pret_vanzare"]
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", pret_vanzare=60)]})
    assert [x["camp"] for x in r["erori_campuri"]] == ["nir-l0-pret_vanzare"]          # sub cost: tot lângă câmp
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", pret_vanzare=80)]})
    assert {d for d, _c, _s in _note(conn, r["inregistrari"])} == {"371", "4426"} and \
        {c for _d, c, _s in _note(conn, r["inregistrari"])} == {"401", "378", "4428"}                    # metoda prețului cu amănuntul


def test_metoda_nedeclarata_se_cere_in_date_firma(conn):
    from core import stocuri_api as s
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A")]})
    assert (r["cod"], r["ecran"]) == ("METODA_STOC_NEDECLARATA", "date_firma")


def test_nir_salvat_se_deschide_cu_articolele_si_notele(conn):
    """C11d: detaliul NIR-ului întoarce articolele și notele lui."""
    from core import stocuri_api as s
    _metoda(conn, "cantitativ_valoric")
    r = s.adauga_nir(conn, _SCH, {"numar": "1", "data": "2099-10-07", "linii": [dict(_L, denumire="Marfa A", articol_nou=True)]})
    d = s.nir_detaliu(conn, _SCH, r["id"])
    assert (d["nir"]["metoda_stoc"], [x["denumire"] for x in d["linii"]], sorted({x["id"] for x in d["note"]})) == \
        ("cantitativ_valoric", ["Marfa A"], sorted(r["inregistrari"]))
    assert d["linii"][0]["pret_vanzare"] is None and Decimal(d["linii"][0]["cantitate"]) == 10
