# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 524, comanda Costin 13.1] „Orice plată, restituire sau regularizare verifică soldul contului pe care îl stinge,
ca la dividende.” Probele lui Costin, refăcute: plata ratei cu creditul și dobânda numai în ciornă (1621 și 1682 zero) -> nota cu sold
invers; restituirea împrumutului fără datorie către asociați (4551 = 5121 20.000); regularizarea 409 cu 4091 zero (401 = 4091 5.000);
decontarea în valută fără creanță în valută (5124 = 4111 24.750 + 765 1.935 inventat).

TEMEI: OMFP 1802/2014, funcțiunea conturilor (1621/1682: în debit „sumele rambursate”; 4551: restituirile; 409: „valoarea avansurilor
acordate furnizorilor, cu ocazia regularizării plăților”) — un cont de datorie nu se debitează peste soldul lui; refuz de FORMĂ (sold
invers). Decontarea în valută: OMFP 1802/2014 pct.322 alin.(1) (diferența față de cursul la care creanța a fost înregistrată).
"""
from decimal import Decimal

import pytest

from core import erori
from core.test_lot13_ops_schema import CTX, linii, nota, schema_ops

D = "2026-10-15"


def _refuz(fn, *a):
    with pytest.raises(erori.DateInvalide) as e:
        fn(*a)
    d = e.value.detaliu
    return (d["mesaj"], [x["camp"] for x in d.get("erori_campuri") or []]) if isinstance(d, dict) else (d, [])


def test_def_524_plata_ratei_fara_credit_validat_se_refuza(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        nota(cur, "2026-10-01", [("5121", "1621", 5000)], status="ciorna")   # primirea creditului, încă ciornă
        m, campuri = _refuz(uc.nota_credit, 1, {"data": D, "operatie": "plata", "tip": "lung", "rata": 5000, "dobanda": 0}, CTX)
        assert "contul 1621" in m and "sold creditor 0,00 lei" in m and "e încă în ciorna" in m and campuri == ["op-rata"], m


def test_def_524_dobanda_din_sold_sau_din_666_stabilita_de_aplicatie(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        nota(cur, "2026-09-01", [("5121", "1621", 5000)])
        # fără dobândă angajată și fără ciornă: cheltuiala lunii, 666 = 5121
        r = uc.nota_credit(1, {"data": D, "operatie": "plata", "tip": "lung", "rata": 1000, "dobanda": 500}, CTX)
        assert linii(cur, r["inregistrare_id"]) == [("1621", "5121", "1000.00", None), ("666", "5121", "500.00", None)]
        assert r["dobanda_din"].startswith("666")
        # dobânda angajată (validată) pe 1682: se plătește din 1682
        nota(cur, "2026-09-30", [("666", "1682", 500)])
        r = uc.nota_credit(1, {"data": D, "operatie": "plata", "tip": "lung", "rata": 0, "dobanda": 500}, CTX)
        assert linii(cur, r["inregistrare_id"]) == [("1682", "5121", "500.00", None)]


def test_def_524_dobanda_ramasa_in_ciorna_se_refuza(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        nota(cur, "2026-09-01", [("5121", "1621", 5000)])
        nota(cur, "2026-09-30", [("666", "1682", 500)], status="ciorna")
        m, campuri = _refuz(uc.nota_credit, 1, {"data": D, "operatie": "plata", "tip": "lung", "rata": 0, "dobanda": 500}, CTX)
        assert "contul 1682" in m and "valideaz-o întâi" in m and campuri == ["op-dobanda"], m


def test_def_524_restituirea_imprumutului_fara_datorie_se_refuza(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        m, campuri = _refuz(uc.nota_asociati, 1, {"data": D, "operatie": "imprumut", "fel": "restituire", "suma": 20000}, CTX)
        assert "contul 4551" in m and "sold creditor 0,00 lei" in m and campuri == ["op-suma"], m
        nota(cur, "2026-09-01", [("5121", "4551", 20000)])
        r = uc.nota_asociati(1, {"data": D, "operatie": "imprumut", "fel": "restituire", "suma": 20000, "dobanda": 0}, CTX)
        assert linii(cur, r["inregistrare_id"]) == [("4551", "5121", "20000.00", None)]


def test_def_524_regularizarea_409_fara_avans_se_refuza(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        corp = {"data": D, "operatie": "regularizare_platit", "suma": 5000, "cota": 21, "data_livrare": D, "destinatie": "stocuri"}
        m, campuri = _refuz(uc.nota_avans, 1, corp, CTX)
        assert "contul 4091" in m and "sold debitor 0,00 lei" in m and campuri == ["op-suma"], m
        nota(cur, "2026-09-01", [("4091", "401", 5000), ("4426", "401", 1050)])
        r = uc.nota_avans(1, corp, CTX)
        assert linii(cur, r["inregistrare_id"]) == [("401", "4091", "5000.00", None), ("401", "4426", "1050.00", None)]


def test_def_524_doua_restituiri_nevalidate_nu_trec_amandoua(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        nota(cur, "2026-09-01", [("5121", "4551", 20000)])
        uc.nota_asociati(1, {"data": D, "operatie": "imprumut", "fel": "restituire", "suma": 15000, "dobanda": 0}, CTX)
        m, _c = _refuz(uc.nota_asociati, 1, {"data": D, "operatie": "imprumut", "fel": "restituire", "suma": 15000}, CTX)
        assert "din care 15.000,00 lei sunt deja stinși de" in m, m


def _factura_valuta(cur, total_eur=5000, curs="4.95"):
    """Factura emisă F3V nr. 1 în EUR, contată prin notă validată: 4111 = 707 la cursul facturii."""
    lei = (Decimal(total_eur) * Decimal(curs)).quantize(Decimal("0.01"))
    cur.execute("INSERT INTO facturi (serie, numar, data_emitere, directie, moneda, total, total_lei, curs_bnr, tert_nume, tert_cui, tert_tara) "
                "VALUES ('F3V', '1', '2026-09-10', 'emisa', 'EUR', %s, %s, %s, 'Client IE', 'IE6388047V', 'IE') RETURNING id",
                (total_eur, lei, curs))
    fid = cur.fetchone()[0]
    nid = nota(cur, "2026-09-10", [("4111", "707", lei)])
    cur.execute("UPDATE inregistrari SET factura_id = %s, sursa = 'facturi' WHERE id = %s", (fid, nid))
    return fid


def test_def_524_decontarea_in_valuta_pe_factura_de_origine(monkeypatch):
    from core import curs_bnr, uc_comun
    monkeypatch.setattr(curs_bnr, "curs_pentru", lambda conn, moneda, data, **k: (Decimal("5.3370"), data, "bnr"))
    monkeypatch.setattr(uc_comun, "_preincalzeste_cursul", lambda *a, **k: None)
    with schema_ops(monkeypatch) as (c, cur, uc):
        # fără creanță în valută: nicio factură deschisă -> refuz (înainte: 5124 = 4111 24.750 + 765 1.935 inventat)
        m, campuri = _refuz(uc.decontare_valuta, 1, {"data": D, "tip": "creanta", "factura_id": 999, "valoare_valuta": 5000,
                                                       "cont_banca": "5124"}, CTX)
        assert campuri == ["op-factura_id"], m
        fid = _factura_valuta(cur)
        lista = uc.operatiuni_date(1, "facturi_valuta", {"tip": "creanta", "data": D}, CTX)["facturi"]
        assert [(f["id"], f["rest_valuta"], f["curs_evidenta"], f["curs_din"]) for f in lista] == [(fid, "5000.00", "4.95", "cursul facturii")]
        m, campuri = _refuz(uc.decontare_valuta, 1, {"data": D, "tip": "creanta", "factura_id": fid, "valoare_valuta": 6000,
                                                       "cont_banca": "5124"}, CTX)
        assert "depășește soldul rămas" in m and campuri == ["op-valoare_valuta"], m
        r = uc.decontare_valuta(1, {"data": D, "tip": "creanta", "factura_id": fid, "valoare_valuta": 2000, "cont_banca": "5124"}, CTX)
        # 2.000 EUR x 4,95 = 9.900 la cursul de evidență; x 5,3370 = 10.674 -> 765 774 (pct.322 alin.(1))
        assert linii(cur, r["inregistrare_id"]) == [("5124", "4111", "9900.00", "Client IE"), ("5124", "765", "774.00", None)]
        assert r["rest_valuta"] == "3000.00"
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (r["inregistrare_id"],))
        lista = uc.operatiuni_date(1, "facturi_valuta", {"tip": "creanta", "data": D}, CTX)["facturi"]
        assert [f["rest_valuta"] for f in lista] == ["3000.00"]   # soldul facturii scade cu decontarea legată de ea


def test_def_541_nota_tva_la_incasare_nu_exigibilizeaza_peste_4428(monkeypatch):
    """CF art.282 alin.(3): TVA-ul colectat devine exigibil la încasare — numai cel neexigibil de pe 4428 (4111 = 4428 la emitere)."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        corp = {"data": D, "sens": "incasare", "suma_incasata": 1210, "cota": 21, "data_fapt_generator": D,
                "ramura_291_5": "fapt_generator"}
        m, campuri = _refuz(uc.nota_tva_incasare, 1, corp, CTX)
        assert "TVA colectat neexigibil" in m and "4428" in m and campuri == ["op-suma_incasata"], m
        nota(cur, "2026-09-10", [("4111", "704", 1000), ("4111", "4428", 210)])   # factura emisă la TVA la încasare, validată
        nota(cur, "2026-09-12", [("4428", "401", 300)])                           # TVA deductibil neexigibil: nu se amestecă
        r = uc.nota_tva_incasare(1, corp, CTX)
        assert linii(cur, r["inregistrare_id"]) == [("4428", "4427", "210.00", None)]
        m, _c = _refuz(uc.nota_tva_incasare, 1, corp, CTX)   # a doua oară: 210 deja exigibilizați de ciorna de mai sus
        assert "deja exigibilizați de note nevalidate" in m, m


def test_def_524_contul_de_trezorerie_e_lista_inchisa_din_planul_firmei(monkeypatch):
    """[lotul 13, decizia Costin după 524 / 504] Contul prin care s-a decontat se alege dintr-o listă ÎNCHISĂ din planul firmei: 5124, 5121,
    5314 (casa în valută) și analiticele lor (aici 5124.01 „Stripe EUR”, procesatorul ținut ca analitic); 5125 / 5311 nu sunt în ea, iar
    serverul refuză lângă câmp un cont din afara ei. Decontarea prin casa în valută: 5314 = 4111 la cursul facturii + 765 diferența.
    MUTAȚIE: verificarea listei scoasă din `decontare_valuta` -> 5125 trece -> pică."""
    from core import curs_bnr, uc_comun
    monkeypatch.setattr(curs_bnr, "curs_pentru", lambda conn, moneda, data, **k: (Decimal("5.3370"), data, "bnr"))
    monkeypatch.setattr(uc_comun, "_preincalzeste_cursul", lambda *a, **k: None)
    with schema_ops(monkeypatch) as (c, cur, uc):
        cur.execute("INSERT INTO plan_conturi (simbol, denumire, tip) VALUES ('5124.01', 'Stripe EUR', 'Bifunctional') ON CONFLICT DO NOTHING")
        conturi = [x["cont"] for x in uc.operatiuni_date(1, "conturi_trezorerie", {}, CTX)["conturi"]]
        assert {"5121", "5124", "5124.01", "5314"} <= set(conturi) and not [x for x in conturi if x.startswith(("5125", "5311"))], conturi
        fid = _factura_valuta(cur)
        m, campuri = _refuz(uc.decontare_valuta, 1, {"data": D, "tip": "creanta", "factura_id": fid, "valoare_valuta": 1000,
                                                       "cont_banca": "5125"}, CTX)
        assert campuri == ["op-cont_banca"] and "5314" in m, m
        r = uc.decontare_valuta(1, {"data": D, "tip": "creanta", "factura_id": fid, "valoare_valuta": 1000, "cont_banca": "5314"}, CTX)
        # 1.000 EUR x 4,95 = 4.950 la cursul de evidență; x 5,3370 = 5.337 -> 765 387 (OMFP 1802/2014 pct.322 alin.(1))
        assert linii(cur, r["inregistrare_id"]) == [("5314", "4111", "4950.00", "Client IE"), ("5314", "765", "387.00", None)]
        r = uc.decontare_valuta(1, {"data": D, "tip": "creanta", "factura_id": fid, "valoare_valuta": 500, "cont_banca": "5124.01"}, CTX)
        assert linii(cur, r["inregistrare_id"])[0][:2] == ("5124.01", "4111")
