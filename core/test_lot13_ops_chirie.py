# -*- coding: utf-8 -*-
"""[lotul 13, deficiențele 530 / 531 / 506, comanda Costin 13.1] Chiria încasată și refacturarea utilităților, prin factura emisă.

530, verbatim: „la total 1.000, refacturat 400, cota 21 se generează două note: 605 = 401 600, 4426 = 401 126, 461 = 401 484 și 4111 = 708
400, 4111 = 4427 84. […] Corect (art. 271, livrare în nume propriu): toată factura ca achiziție proprie (605 = 401 1.000, 4426 = 401 210),
apoi factura către chiriaș (4111 = 708 400, 4111 = 4427 84), fără 461.”
531, verbatim: „Închirierea de imobile e scutită (art. 292 alin. 2 lit. e) dacă firma nu a optat pentru taxare (art. 292 alin. 3, cu
notificare). […] fără opțiune chiria e scutită, cu rândul ei în D300 […]. Azi «cota 0» dă 4111 = 706 2.000 fără să se știe că e scutită.”
TEMEI: CF art.271 alin.(2) lit.c) (cel care acționează în nume propriu „se consideră că a achiziționat și livrat ea însăși”); CF art.292
alin.(2) lit.e) („arendarea, concesionarea, închirierea și leasingul de bunuri imobile” — scutite fără drept de deducere) și alin.(3)
(„Orice persoană impozabilă poate opta pentru taxarea operațiunilor prevăzute la alin. (2) lit. e) și f)”); OPANAF 174/2026, D300 rd.15.
Firma de probă: CUI 14399840; chiriaș 18765430; furnizor 31654471 (cifrele de control verificate cu algoritmul oficial)."""
import pytest

from core import erori
from core.test_lot13_ops_schema import CTX, linii, schema_ops

D = "2026-10-15"


def _firma(cur):
    cur.execute("INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,caen,banca,iban,telefon,platitor_tva,tip_decont,inreg_art317,"
                "declarant_nume,declarant_prenume,declarant_functie,forma_juridica,capital_subscris,serie_factura,metoda_stoc) VALUES "
                "(1,'X SRL','14399840','Str 1','Cluj-Napoca','CJ','6820','BCR','RO49RNCB0000000000000001','0700000000',true,'lunar',false,"
                "'Popescu','Ion','ADMINISTRATOR','SRL',200,'CHR','global_valoric')")


@pytest.fixture
def uc_anaf(monkeypatch):
    from core import anaf_api
    monkeypatch.setattr(anaf_api, "valideaza_cui", lambda lista, **k: [{"cui": c, "gasit": True, "platitor_tva": True, "denumire": "X"}
                                                                       for c in lista])


def _linii_facturii(cur, fid):
    cur.execute("SELECT cota_tva::text, categorie_tva FROM factura_linii WHERE factura_id = %s", (fid,))
    return cur.fetchall()


def test_def_530_refacturarea_e_achizitie_proprie_si_factura_catre_chirias(monkeypatch, uc_anaf):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        r = uc.nota_chirie(1, {"data": D, "fel": "refacturare", "total_factura": 1000, "parte_refacturata": 400, "cota": 21,
                               "numar": "UT-77", "furnizor_cui": "31654471", "furnizor_nume": "Utilitati SA",
                               "client_cui": "18765430", "client_nume": "Chirias SRL"}, CTX)
        primire, emitere = r["inregistrari"]
        assert [x[:3] for x in linii(cur, primire)] == [("605", "401", "1000.00"), ("4426", "401", "210.00")]   # fără 461
        assert {x[3] for x in linii(cur, primire)} == {"Utilitati SA"}                                        # 506: furnizorul
        assert sorted(x[:3] for x in linii(cur, emitere)) == [("4111", "4427", "84.00"), ("4111", "708", "400.00")]
        cur.execute("SELECT directie, tert_nume FROM facturi WHERE id = %s", (r["factura_id"],))
        assert cur.fetchone() == ("emisa", "Chirias SRL")


def test_def_530_factura_furnizorului_deja_primita_nu_se_dubleaza(monkeypatch, uc_anaf):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        cur.execute("INSERT INTO facturi (numar, data_emitere, directie, total, tert_cui, tert_nume) VALUES ('UT-77', %s, 'primita', 1210, "
                    "'RO31654471', 'Utilitati SA')", (D,))
        r = uc.nota_chirie(1, {"data": D, "fel": "refacturare", "total_factura": 1000, "parte_refacturata": 400, "cota": 21,
                               "numar": "UT-77", "furnizor_cui": "31654471", "furnizor_nume": "Utilitati SA",
                               "client_cui": "18765430", "client_nume": "Chirias SRL"}, CTX)
        assert len(r["inregistrari"]) == 1 and "deja în Facturi primite" in r["factura_furnizor"]


def test_def_531_chiria_unui_imobil_fara_optiune_e_scutita(monkeypatch, uc_anaf):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        r = uc.nota_chirie(1, {"data": D, "fel": "chirie_incasata", "chirie": 2000, "tip_bun": "imobil", "optiune_taxare": "false",
                               "client_cui": "18765430", "client_nume": "Chirias SRL"}, CTX)
        assert _linii_facturii(cur, r["factura_id"]) == [("0.00", "scutit_fara_drept")]   # D300 rd.15, art.292 alin.(2) lit.e)
        assert [x[:3] for x in linii(cur, r["inregistrari"][0])] == [("4111", "706", "2000.00")]
        assert "scutită fără drept de deducere" in r["regim"]
        r = uc.nota_chirie(1, {"data": D, "fel": "chirie_incasata", "chirie": 2000, "tip_bun": "imobil", "optiune_taxare": "true",
                               "cota": 21, "client_cui": "18765430", "client_nume": "Chirias SRL"}, CTX)
        assert sorted(x[:3] for x in linii(cur, r["inregistrari"][0])) == [("4111", "4427", "420.00"), ("4111", "706", "2000.00")]


def test_def_506_chiriasul_e_cerut(monkeypatch, uc_anaf):
    with schema_ops(monkeypatch) as (c, cur, uc):
        _firma(cur)
        with pytest.raises(erori.DateInvalide) as e:
            uc.nota_chirie(1, {"data": D, "fel": "chirie_incasata", "chirie": 2000, "tip_bun": "imobil", "optiune_taxare": "false"}, CTX)
        assert [x["camp"] for x in e.value.detaliu["erori_campuri"]] == ["op-client_cui", "op-client_nume"]
