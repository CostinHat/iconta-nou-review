# -*- coding: utf-8 -*-
"""[deficiențele 398, 399, 400, 415, 408 — retestul Costin 19.10.2026] NIR-ul:
  398 „liniile aceluiași NIR contate diferit (marfa 371=408/4428.01=408, transportul 371=401) — toate liniile aceeași regulă”;
  399 „cost accesoriu (transport 100 lei, furnizor plătitor TVA) fără TVA; pe NIR nu se alege cu factură/fără → 408 fără decizia
      utilizatorului”;
  400 „Detaliul NIR arată doar prețul de achiziție, nu transportul repartizat și costul unitar final (55 / 27,50)”;
  415 „Articol creat din NIR («+ articol nou», Marfa B, cotă 21%) rămâne fără cotă; preia cota de pe rândul NIR”;
  408 „Coada: NIR 3 «rulaj 1.000,00» deși notele însumează 1.310”.
Temei: OMFP 1802/2014, funcțiunea contului 408 („valoarea bunurilor aprovizionate [...] pentru care nu s-au primit facturile”); costul de
achiziție cuprinde prețul, taxele nerecuperabile și transportul direct atribuibil (OMFP 1802/2014, cum îl aplică `stocuri._repartizeaza`); CF art.297 alin.(4) lit.a (TVA-ul
transportului, deductibil). Schemă efemeră din template, ștearsă la ieșire."""
import io
from decimal import Decimal

import pytest

from core import coada_api, db as _db, stocuri_api as _s, tenant_provisioning as _tprov

SCH = "efemer_398_nir"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute("SET search_path TO %s, public" % SCH)
            cur.execute("INSERT INTO firma_profil (id, nume, cui, platitor_tva, forma_juridica, capital_subscris, metoda_stoc) "
                        "VALUES (1, 'F1 SRL', '14399840', true, 'SRL', 200, 'cantitativ_valoric')")
        c.commit()
    with _db.get_conn(SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        c.commit()


def _nir(**extra):
    return {"numar": "3", "data": "2026-10-19", "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
            "linii": [{"denumire": "Marfa B", "articol_nou": True, "cantitate": 2, "pret_achizitie": 25, "cota_tva": 21}], **extra}


def _note(conn, ids):
    with conn.cursor() as cur:
        cur.execute("SELECT cont_debit, cont_credit, suma FROM inregistrari_linii WHERE inregistrare_id = ANY(%s) ORDER BY id", (ids,))
        return [(d, c, str(s)) for d, c, s in cur.fetchall()]


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def test_399_decizia_facturii_si_cota_transportului_se_cer(conn):
    assert _s.adauga_nir(conn, SCH, _nir(transport=5), cere_decizia=True)["cod"] == _s.COD_FACTURA_NEDECLARATA
    r = _s.adauga_nir(conn, SCH, _nir(transport=5, factura_sosita=True), cere_decizia=True)
    assert r["cod"] == _s.COD_FACTURA_NEDECLARATA and r["eroare"].startswith("Factura a sosit: la stocul la cost, factura primită aduce"), r
    r = _s.adauga_nir(conn, SCH, _nir(transport=5, factura_sosita=False), cere_decizia=True)
    assert r["cod"] == _s.COD_COTA_TRANSPORT and r["erori_campuri"][0]["camp"] == "sn-transport-cota", r


def test_398_399_toate_liniile_pe_aceeasi_regula_si_tva_pe_transport(conn):
    """Factura nesosită: marfa 371 = 408 și 4428.01 = 408, transportul 371 = 408 (nu 401) și TVA-ul lui 4428.01 = 408."""
    r = _s.adauga_nir(conn, SCH, _nir(transport=5, factura_sosita=False, cota_tva_transport=21), cere_decizia=True)
    assert "eroare" not in r, r
    assert _note(conn, r["inregistrari"]) == [("371", "408", "50.00"), ("4428.01", "408", "10.50"), ("371", "408", "5.00"),
                                              ("4428.01", "408", "1.05")]


def test_400_detaliul_arata_accesoriul_si_costul_unitar_final(conn):
    r = _s.adauga_nir(conn, SCH, _nir(transport=5, factura_sosita=False, cota_tva_transport=0), cere_decizia=True)
    d = _s.nir_detaliu(conn, SCH, r["id"])
    l = d["linii"][0]
    assert (l["pret_achizitie"], l["accesoriu"], l["cost_final"], l["cost_unitar_final"]) == ("25.0000", "5.00", "55.00", "27.5000"), l


def test_415_articolul_nou_din_nir_isi_ia_cota_in_nomenclator(conn):
    _s.adauga_nir(conn, SCH, _nir(factura_sosita=False), cere_decizia=True)
    with conn.cursor() as cur:
        cur.execute("SELECT denumire, cota_tva, confirmat FROM produse")
        assert cur.fetchall() == [("Marfa B", Decimal("21.00"), True)]


def test_408_rulajul_documentului_e_al_tuturor_notelor():
    p = coada_api._payload_grup([(1, {"total": "1000", "rulaj": "1000.00", "rulaj_storno": "0"}),
                                 (2, {"total": "310", "rulaj": "310.00", "rulaj_storno": "0"})])
    assert (p["rulaj"], p["rulaj_storno"], p["total"]) == ("1310.00", "0", "1310")
