# -*- coding: utf-8 -*-
"""[lotul 12, comanda Costin 12.2, C181 — clasa 443.1 „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”] Două răspunsuri
de server pe care ecranul le afișează numeau factura cu seria lipită de număr:

  * `uc_tenants.bon_facturi_candidate` (ruta `/bonuri/{id}/facturi-candidate`, ecranul „Leagă bonul de factură” din firme.js: `Factura
    ${f.numar}`) lipea `serie + numar` -> „Factura F1A3”; acum `pdf_util.serie_nr` -> „Factura F1A nr. 3”;
  * `rapoarte_comerciale_api.fisa_partener` (ecranul „Fișa partenerului” din Rapoarte comerciale: `numarCuSerie(r.serie, r.numar)`) nu
    întorcea `serie`, deci ecranul afișa numai numărul; acum `serie` e în SELECT și în răspuns.

Temei: CF art.319 alin.(20) lit.a — „numărul de ordine, în baza uneia sau a mai multor serii” (seria și numărul sunt două elemente ale
facturii). MUTAȚII: lipirea veche pusă la loc în `bon_facturi_candidate` -> pică primul test; `"serie": r["serie"]` scos din
`fisa_partener` -> pică al doilea."""
import contextlib
import io
import os

import pytest

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot12_int1_serie"


def _db_ok():
    from core import db
    try:
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


def test_c181_facturile_candidate_ale_bonului_poarta_seria_separat(monkeypatch):
    """Factura primită cu seria „F1A” și numărul „3” (și una emisă în stil vechi, cu seria deja în număr: „F1A14”) -> „F1A nr. 3” și
    „F1A nr. 14”, nu „F1A3” / „F1AF1A14”; fără serie, numărul rămâne cum e."""
    from core import uc_tenants as ut
    monkeypatch.setattr(ut.db, "get_conn", lambda *a, **k: contextlib.nullcontext(type("C", (), {
        "cursor": lambda self, *a, **k: contextlib.nullcontext(None)})()))
    monkeypatch.setattr(ut.auth_api, "schema_tenant", lambda conn, uid, tid: "tenant_x")
    monkeypatch.setattr(ut.repo_casa, "cui_si_total_bon", lambda cur, s, bid: ("14399840", 119))
    monkeypatch.setattr(ut.repo_facturi, "candidate_pentru_bon", lambda cur, s, cui, suma: [
        (1, "3", "F1A", None, 119, "Furnizor", "14399840"),
        (2, "F1A14", "F1A", None, 119, "Furnizor", "14399840"),
        (3, "12", None, None, 119, "Altul", "14399840")])
    rez = ut.bon_facturi_candidate(1, 5, {"uid": 1})
    assert [f["numar"] for f in rez["facturi"]] == ["F1A nr. 3", "F1A nr. 14", "12"], rez


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c181_fisa_partenerului_intoarce_seria_pe_care_o_afiseaza_ecranul():
    """Schemă efemeră din template, an 2099, în tranzacție anulată: fișa întoarce `serie` lângă `numar`, iar ecranul o citește
    (`numarCuSerie(r.serie, r.numar)` în firme.js)."""
    from core import db, rapoarte_comerciale_api as rc, tenant_provisioning as _tp
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("INSERT INTO %s.facturi (serie, numar, data_emitere, directie, tip, tert_nume, tert_cui, total) VALUES "
                            "('F1A', '3', '2099-03-01', 'emisa', 'factura', 'DANTE INTERNATIONAL SA', '14399840', 100)" % SCHEMA)
            fisa = rc.fisa_partener(conn, '"%s"' % SCHEMA, "14399840", "2099-01-01", "2099-12-31")
            assert [(f["serie"], f["numar"]) for f in fisa["facturi"]] == [("F1A", "3")], fisa
        finally:
            conn.rollback()
