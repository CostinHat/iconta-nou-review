# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 435 — comanda Costin 10.2 pct.5, verbatim] „la F1, Produse arată doar Marfa A și Marfa C. Marfa B (din NIR 3),
Carte tehnica (din importul XML) și grâu (din borderou) sunt în stoc, dar lipsesc din nomenclator, iar cota Marfei B nu se poate
completa nicăieri, deși factura trimite la Produse. Orice articol din stoc apare în nomenclator.”

Cauza: nomenclatorul primea articolul numai când documentul de intrare avea cotă (`produse_api.asigura_din_document`, 415) și numai când
documentul CREA articolul. Reparația: lista nomenclatorului (`produse_api.lista`) cuprinde orice articol din stoc fără produs, „cotă
lipsă”, iar cota aleasă pe rând îl scrie în nomenclator; documentul cu cotă o duce și pentru articolul existent; cota 0 de pe o factură
PRIMITĂ nu devine cota vânzării. Temei pentru „cota nu se presupune”: CF art.291 (cotele) se aplică pe livrare — cota achiziției de la un
furnizor neplătitor (0) nu spune cota livrării. Schemă efemeră din template, în tranzacție anulată."""
import contextlib
import io

import pytest

from core import db as _db, tenant_provisioning as _tp

SCH = "tenant_test_435_nomenclator"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


class _P:
    def __init__(s, c): s._c = c
    def commit(s): pass
    def __getattr__(s, n): return getattr(s._c, n)


@pytest.fixture
def conn(monkeypatch):
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
                cur.execute("SET LOCAL search_path TO %s, public" % SCH)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                            "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
            from core import auth_api, uc_comun, uc_tenants
            monkeypatch.setattr(uc_tenants.db, "get_conn", lambda *a, **k: contextlib.nullcontext(_P(c)))
            monkeypatch.setattr(auth_api, "schema_tenant", lambda *a, **k: SCH)
            monkeypatch.setattr(uc_comun, "_cere_luna_deschisa", lambda *a, **k: None)
            yield c
        finally:
            c.rollback()


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _lista(c):
    from core import produse_api
    return {p["denumire"]: p for p in produse_api.lista(c)}


def test_def_435_orice_articol_din_stoc_apare_in_nomenclator(conn):
    from core import uc_tenants, produse_api
    with conn.cursor() as cur:
        # Marfa A: în stoc și în nomenclator (cu cotă); Marfa B: în stoc, creată înaintea lui 415 (fără produs); Carte tehnica: articol
        # scris de orice alt drum (import de articole, migrare) — orice rând din `articole`
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa A', 'buc'), ('Marfa B', 'buc'), ('Carte tehnica', 'buc')")
    produse_api.creeaza(conn, "marfa a", cota_tva=21)
    # grâu din borderou (fără cotă: persoana fizică nu facturează TVA)
    uc_tenants.achizitie_neinregistrat(1, {"data": "2026-10-19", "furnizor_nume": "Ion Popescu", "furnizor_adresa": "Str. Florilor 1",
                                           "furnizor_act": "PH 123456", "valoare": 200, "cont_cheltuiala": "371", "articol": "grâu", "articol_nou": True,
                                           "cantitate": 100, "um": "kg"}, {"uid": 1})
    l = _lista(conn)
    # comanda 10.2 pct.5: „Orice articol din stoc apare în nomenclator” — Marfa A o dată (produsul), restul ca rânduri din stoc
    assert sorted(l) == ["Carte tehnica", "Marfa B", "grâu", "marfa a"], sorted(l)
    for den in ("Carte tehnica", "Marfa B", "grâu"):
        # „cota Marfei B nu se poate completa nicăieri” — rândul vine fără cotă (nu se presupune), de completat pe el
        assert l[den]["din_stoc"] is True and l[den]["cota_tva"] is None and l[den]["id"] is None, l[den]
    assert l["grâu"]["um"] == "kg"
    assert l["marfa a"]["cota_tva"] == 21.0 and not l["marfa a"].get("din_stoc")
    # cota aleasă pe rând îl scrie în nomenclator (același POST ca ecranul): rândul din stoc devine produs, o singură dată
    produse_api.creeaza(conn, "Marfa B", um="buc", cota_tva=21, confirmat=True)
    l = _lista(conn)
    assert l["Marfa B"]["cota_tva"] == 21.0 and l["Marfa B"]["id"] and not l["Marfa B"].get("din_stoc"), l["Marfa B"]
    assert len([d for d in l if d.lower() == "marfa b"]) == 1


def test_def_435_documentul_cu_cota_o_duce_si_pentru_articolul_existent(conn):
    """Marfa B există în stoc fără produs; o intrare nouă cu cotă (NIR / factură primită) o pune în nomenclator, cu cota rândului."""
    from core import stocuri_cv_api as scv
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa B', 'buc') RETURNING id")
        aid = cur.fetchone()[0]
    r = scv.intrare(conn, SCH, {"articol_id": aid, "cantitate": "2", "pret_unitar": "10", "data": "2026-10-20", "cota_tva": 21,
                                "document": "NIR nr 3 din 20.10.2026"})
    assert "eroare" not in r, r
    l = _lista(conn)
    assert l["Marfa B"]["cota_tva"] == 21.0 and l["Marfa B"]["sursa"] == "document", l["Marfa B"]


def test_def_435_cota_zero_de_pe_factura_primita_nu_devine_cota_vanzarii(conn):
    """Factura primită de la un furnizor neplătitor (cota 0 pe linie): articolul intră în stoc și în nomenclator „cotă lipsă”, nu „fără
    TVA”. CF art.291 — cota se aplică livrării; achiziția la 0 nu o stabilește."""
    from core import stocuri_cv_api as scv
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, status, tert_nume) VALUES ('X1', '2026-10-20', 'primita', "
                    "'importata', 'Furnizor neplatitor') RETURNING id")
        fid = cur.fetchone()[0]
        cur.execute("INSERT INTO factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%s, 'Carte tehnica', 3, 40, 0)",
                    (fid,))
    r = scv.intrare_din_factura(conn, SCH, fid, "371", "2026-10-20")
    assert r["stare"] == "intrat" and r["linii"] == 1, r
    l = _lista(conn)
    assert l["Carte tehnica"]["cota_tva"] is None and l["Carte tehnica"]["din_stoc"] is True, l["Carte tehnica"]


def test_def_435_nir_pe_articol_existent_duce_cota_in_nomenclator(conn):
    """Cazul F1: Marfa B era deja în stoc (creată înaintea lui 415), fără produs; NIR-ul nou pe ea, cu cota 21% pe rând, o pune în
    nomenclator (înainte, numai articolul NOU din NIR primea produsul)."""
    from core import stocuri_api as _s
    with conn.cursor() as cur:
        cur.execute("INSERT INTO articole (denumire, um) VALUES ('Marfa B', 'buc') RETURNING id")
        aid = cur.fetchone()[0]
    r = _s.adauga_nir(conn, SCH, {"numar": "4", "data": "2026-10-20", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
                                  "factura_sosita": False, "linii": [{"articol_id": aid, "denumire": "Marfa B", "cantitate": 2,
                                                                      "pret_achizitie": 25, "cota_tva": 21}]}, cere_decizia=True)
    assert "eroare" not in r, r
    l = _lista(conn)
    assert l["Marfa B"]["cota_tva"] == 21.0 and not l["Marfa B"].get("din_stoc"), l["Marfa B"]
