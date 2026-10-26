# -*- coding: utf-8 -*-
"""[lotul 13, deficiențele 510 / 548 / 551, comanda Costin 13.1] Producția, vânzarea în regim de marjă și aurul de investiții — din stoc.

510, verbatim: „Obținerea nu cere produs, cantitate, gestiune; la vânzare costul standard ieșit și coeficientul 348 se introduc de mână.
Aplicația ține stocul de produse și calculează coeficientul din soldurile 348 și 345.”
548, verbatim: „Vânzarea nu descarcă bunul din gestiune (607 = 371 / costul aurului) și nu cere clientul; profitul iese mai mare cu tot
costul bunului, stocul rămâne umflat. Prețul de cumpărare se scrie de mână în loc să vină din bunul aflat în stoc (511). […] Corecte: TVA
pe marjă prin sută mărită (36,45 la marja 210), marjă negativă → TVA 0 fără report (norme pct. 86)”.
551 (partea a doua): „Inconsecvent: vânzarea în regim de marjă și cea de aur au trecut fără metoda de stoc (548).”

TEMEI: OMFP 1802/2014 pct.286 alin.(4) (coeficientul de repartizare: „Soldul inițial al diferențelor de preț + Diferențe de preț aferente
intrărilor în cursul perioadei […] / Soldul inițial al stocurilor la preț de înregistrare + Valoarea intrărilor în cursul perioadei la preț
de înregistrare […]. Acest coeficient se înmulțește cu valoarea bunurilor ieșite din gestiune la preț de înregistrare”); OMFP 2634/2015
anexa 2, cod 14-3-3A (Bonul de predare, transfer, restituire — „document justificativ pentru încărcare/descărcare în/din gestiune”);
CF art.312 alin.(1) lit.g) („marja profitului este diferența dintre prețul de vânzare aplicat de persoana impozabilă revânzătoare și prețul de cumpărare”); CF art.313 alin.(10) (identificarea clientului la aur).
Firma de probă: CUI 14399840; clientul 18765430 (cifrele de control verificate cu algoritmul oficial)."""
from decimal import Decimal

import psycopg2
import pytest

from core import erori
from core.test_lot13_ops_schema import CTX, SCH, cnp_valid, linii, schema_ops

D = "2026-10-15"
CNP = cnp_valid("185010140001")   # cifra de control calculată cu algoritmul oficial (CLAUDE.md)


def _firma(cur, metoda="cantitativ_valoric"):
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,inreg_art317,"
                "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES "
                "(1,'X SRL','14399840','Str 1','Cluj-Napoca','CJ','1610','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar',false,"
                "'Popescu','Ion','ADMINISTRATOR','SRL',200,'PRD',%s)", (metoda,))


@pytest.fixture
def uc_anaf(monkeypatch):
    from core import anaf_api
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda lista, **k: [{"cui": c, "gasit": True, "platitor_tva": True, "denumire": "X"}
                                                                       for c in lista])


def _marfa(c, denumire, cant, pret):
    """Bunul în stoc (marfă, 371): intrarea în fișa de magazie, ca după un NIR."""
    from core import stocuri_cv_api as _cva
    return _cva.intrare(c, SCH, {"denumire": denumire, "um": "buc", "cont_stoc": "371", "cont_cheltuiala": "607", "data": "2026-10-01",
                                 "cantitate": cant, "pret_unitar": pret, "document": "NIR 1"})["articol_id"]


def _obtinere(uc):
    return uc.nota_productie(1, {"data": D, "operatie": "obtinere", "produs": "Masa lemn", "um": "buc", "cantitate": 10, "cost_standard": 100,
                                 "cost_efectiv": 1100, "gestiune": "Magazia produse"}, CTX)


def test_def_510_obtinerea_intra_in_stoc_cu_bonul_de_predare(monkeypatch):
    """MUTAȚIE: legarea intrării de notă scoasă (`UPDATE … miscari_stoc SET inregistrare_id`) -> mișcarea fără notă -> pică."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        r = _obtinere(uc)
        assert [x[:3] for x in linii(cur, r["inregistrare_id"])] == [("345", "711", "1000.00"), ("348", "711", "100.00")]
        cur.execute("SELECT document_ref FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert cur.fetchone()[0].startswith("Bon de predare, transfer, restituire nr ")          # OMFP 2634/2015, cod 14-3-3A
        cur.execute("SELECT a.denumire, a.cont_stoc, a.cont_cheltuiala, m.tip, m.cantitate::text, m.valoare::text, m.locatie, m.inregistrare_id "
                    "FROM miscari_stoc m JOIN articole a ON a.id = m.articol_id")
        assert cur.fetchall() == [("Masa lemn", "345", "711", "intrare", "10.000", "1000.00", "Magazia produse", r["inregistrare_id"])]


def test_def_510_obtinerea_cere_produsul_cantitatea_si_gestiunea(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        with pytest.raises(erori.DateInvalide) as e:
            uc.nota_productie(1, {"data": D, "operatie": "obtinere", "cost_standard": 100}, CTX)
        assert {x["camp"] for x in e.value.args[0]["erori_campuri"]} >= {"op-produs", "op-cantitate", "op-gestiune"}
        with pytest.raises(erori.DateInvalide) as e:   # produs nou fără unitatea de măsură: nu se presupune „buc”
            uc.nota_productie(1, {"data": D, "operatie": "obtinere", "produs": "Scaun", "cantitate": 2, "cost_standard": 50,
                                  "gestiune": "M1"}, CTX)
        assert e.value.args[0]["erori_campuri"][0]["camp"] == "op-um"


def test_def_510_vanzarea_e_factura_descarca_produsul_si_repartizeaza_348(monkeypatch, uc_anaf):
    """K = (0 + 100) / (0 + 1.000) = 0,1 (pct.286 alin.(4)); 4 buc ieșite la 100 = 400 -> 711 = 348 40. MUTAȚIE: nota diferențelor scoasă ->
    pică."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        o = _obtinere(uc)
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (o["inregistrare_id"],))   # evidența: obținerea validată
        r = uc.nota_productie(1, {"data": D, "operatie": "vanzare", "produs": "Masa lemn", "cantitate": 4, "pret_vanzare": 150, "cota": 21,
                                  "client_cui": "18765430", "client_nume": "Mobila Client SRL"}, CTX)
        cur.execute("SELECT directie, tert_nume FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == ("emisa", "Mobila Client SRL")                                  # 506: documentul e factura emisă
        assert sorted(x[:3] for x in linii(cur, r["inregistrare_id"])) == [("4111", "4427", "126.00"), ("4111", "701", "600.00")]
        cur.execute("SELECT l.cont_debit, l.cont_credit, l.suma::text FROM miscari_stoc m JOIN inregistrari_linii l "
                    "ON l.inregistrare_id = m.inregistrare_id WHERE m.tip = 'iesire'")
        assert cur.fetchall() == [("711", "345", "400.00")]                                      # descărcarea la ieșire
        assert r["coeficient_348"] == "0.100000"
        assert [x[:3] for x in linii(cur, r["nota_diferente_id"])] == [("711", "348", "40.00")]


def test_def_510_551_fara_stoc_pe_articol_refuzul_trimite_in_date_firma(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur, "global_valoric")
        for fn, corp in ((uc.nota_productie, {"data": D, "operatie": "obtinere", "produs": "Masa", "um": "buc", "cantitate": 1,
                                              "cost_standard": 10, "gestiune": "M"}),
                         (uc.vanzare_marja, {"data": D, "articol": "Ceas", "cantitate": 1, "pret_vanzare": 10, "cota": 21,
                                             "client_nume": "Ion", "document": "BF 1"}),
                         (uc.vanzare_aur_investitii, {"data": D, "articol": "Lingou", "cantitate": 1, "tip": "lingou", "puritate": 999,
                                                      "calitate_client": "PF", "client_identificare": CNP, "client_nume": "Ion",
                                                      "suma": 1000, "document": "F 1"})):
            with pytest.raises(erori.CerereGresita) as e:
                fn(1, corp, CTX)
            assert e.value.args[0]["ecran"] == "date_firma", fn.__name__


def test_def_548_marja_descarca_bunul_iar_pretul_de_cumparare_e_cmp(monkeypatch):
    """Marja 510 − 300 = 210 -> TVA 210 × 21 / 121 = 36,45 (sută mărită, Costin: „36,45 la marja 210”); 4111 = 707 473,55 + 4111 = 4427
    36,45 cu clientul; 607 = 371 300 la CMP. MUTAȚIE: prețul de cumpărare luat din cerere (`corp.get("pret_cumparare")`) -> pică."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        _marfa(c, "Ceas vechi", 1, 300)
        r = uc.vanzare_marja(1, {"data": D, "articol": "Ceas vechi", "cantitate": 1, "pret_vanzare": 510, "cota": 21,
                                 "client_nume": "Ion Pop", "document": "Factura nr 5 din 15.10.2026"}, CTX)
        assert r["pret_cumparare"] == "300.00" and r["tva"] == "36.45"
        assert sorted(linii(cur, r["inregistrare_id"])) == [("4111", "4427", "36.45", "Ion Pop"), ("4111", "707", "473.55", "Ion Pop")]
        assert [x[:3] for x in linii(cur, r["nota_iesire_id"])] == [("607", "371", "300.00")]
        monkeypatch.setattr(uc.auth_api, "schema_tenant_citire", lambda conn, uid, tid: SCH)
        j = uc.jurnal_marja(1, "secondhand", "2026-10", CTX)
        assert [(n["pret_vanzare"], n["cost"], n["marja_neta"], n["tva"], n["client"]) for n in j["note"]] == [
            ("510.00", "300.00", "173.55", "36.45", "Ion Pop")]


def test_def_548_marja_peste_stoc_refuzata_langa_cantitate(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        _marfa(c, "Ceas vechi", 1, 300)
        with pytest.raises(erori.DateInvalide) as e:
            uc.vanzare_marja(1, {"data": D, "articol": "Ceas vechi", "cantitate": 2, "pret_vanzare": 510, "cota": 21,
                                 "client_nume": "Ion Pop", "document": "BF 2"}, CTX)
        assert e.value.args[0]["erori_campuri"][0]["camp"] == "op-cantitate"


def test_def_548_aurul_iese_din_stoc_cu_clientul_pe_4111(monkeypatch):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        _marfa(c, "Lingou 100 g", 1, 30000)
        r = uc.vanzare_aur_investitii(1, {"data": D, "articol": "Lingou 100 g", "cantitate": 1, "tip": "lingou", "puritate": 999,
                                          "calitate_client": "PF", "client_identificare": CNP, "client_nume": "Ion Pop",
                                          "suma": 33000, "document": "Factura nr 6 din 15.10.2026"}, CTX)
        assert r["regim"] == "scutit" and r["cost"] == "30000.00"
        assert linii(cur, r["inregistrare_id"]) == [("4111", "707", "33000.00", "Ion Pop")]   # scutit, fără TVA (art.313 alin.(3))
        assert [x[:3] for x in linii(cur, r["nota_iesire_id"])] == [("607", "371", "30000.00")]


def test_def_548_vanzarea_cu_iesirea_vie_nu_se_sterge(monkeypatch):
    """Triggerul bazei (`trg_vanzare_stoc_sterge`): nota vânzării ștearsă ar lăsa bunul ieșit din gestiune fără vânzare."""
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        _marfa(c, "Ceas vechi", 1, 300)
        r = uc.vanzare_marja(1, {"data": D, "articol": "Ceas vechi", "cantitate": 1, "pret_vanzare": 510, "cota": 21,
                                 "client_nume": "Ion Pop", "document": "BF 3"}, CTX)
        cur.execute("SAVEPOINT s")
        with pytest.raises(psycopg2.Error) as e:
            cur.execute("DELETE FROM inregistrari WHERE id = %s", (r["inregistrare_id"],))
        assert "REGULA_CONTABILA: Vânzarea a scos bunul din stoc" in str(e.value)
        cur.execute("ROLLBACK TO SAVEPOINT s")
        monkeypatch.setattr(uc._uc_comun, "_schema_sau_404", lambda ctx, tid: SCH)
        assert Decimal("0") == Decimal(str(uc.operatiuni_date(1, "articole", {"tip": "marfa"}, CTX)["articole"][0]["stoc"]))
