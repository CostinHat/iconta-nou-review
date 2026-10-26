# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — facturile primite: 545 (dublura), 546 (totalul de plată la taxarea inversă), 547 (ștergerea
facturii primite cu nota încă ciornă).

Temei:
  * 546 — CF art.331 alin.(3): „Pe facturile emise pentru livrările de bunuri/prestările de servicii prevăzute la alin. (2)
    furnizorii/prestatorii nu vor înscrie taxa colectată aferentă. Beneficiarii vor determina taxa aferentă, care se va evidenția în
    decontul prevăzut la art. 323, atât ca taxă colectată, cât și ca taxă deductibilă.” -> datoria către furnizor e baza.
  * 545 / 547 — OMFP 2634/2015 anexa 1 pct.58 lit.c: „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul
    unui document”.
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417); zilele sunt SINTETICE (2099). CUI 14399840 (DANTE INTERNATIONAL
SA): cifra de control verificată cu algoritmul oficial (`test_lot12_fact2_c73_dublura.test_cuiurile_de_proba_au_cifra_de_control_buna`)."""
from decimal import Decimal as D

import pytest

from core import chei_unice, contare_facturi, facturi, facturi_api, repo_contabilitate, repo_facturi
from core.test_417_storno_trimitere import _SCHEMA, _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _ti(conn, numar="TI-1", baza="30000", data="2099-03-10"):
    """Achiziția cu taxare inversă internă, ca Operațiunile (`uc_tenants.achizitie_taxare_inversa`): factura primită cu cota 21 pe linie
    și `taxare_inversa`, apoi nota ei ciornă 371 = 401 baza, 4426 = 4427 TVA."""
    r = facturi_api.creeaza_factura(conn, numar, data, "primita", [{"descriere": "Deșeuri feroase", "cantitate": 1, "pret_unitar": baza,
                                                                    "cota_tva": 21}],
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="14399840", categorie_331="deseuri",
                                    taxare_inversa=True, status="importata", tert_platitor_tva=True)
    with conn.cursor() as cur:
        iid = repo_contabilitate.nota_facturi_cu_factura(cur, _SCHEMA, data, r["factura_id"], "Achiziție - taxare inversă")[0]
        repo_contabilitate.adauga_linie(cur, _SCHEMA, iid, "371", "401", D(baza))
        repo_contabilitate.adauga_linie(cur, _SCHEMA, iid, "4426", "4427", (D(baza) * D("0.21")).quantize(D("0.01")))
    return r["factura_id"], iid


def test_def_546_definitia_totalului_de_plata_e_pura():
    """Pur: la factura primită cu taxare inversă totalul de plată e totalul fără TVA; la emisă / primită obișnuită, totalul.
    MUTAȚIE: `fara_tva_de_plata` -> False -> 36300 -> pică."""
    assert facturi.total_de_plata({"directie": "primita", "taxare_inversa": True}, "36300.00", "6300.00") == D("30000.00")
    assert facturi.total_de_plata({"directie": "primita", "taxare_inversa": False}, "1210", "210") == D("1210")
    assert facturi.total_de_plata({"directie": "emisa", "taxare_inversa": True}, "1000", "0") == D("1000")


@DB
def test_def_546_factura_primita_cu_taxare_inversa_se_datoreaza_fara_tva(conn):
    """TI-1, baza 30.000, cota 21 -> antetul păstrează TVA-ul determinat de firmă (6.300, citit de D300 / D394 / D406), dar: detaliul arată
    totalul de plată 30.000 și TVA-ul de taxare inversă separat; starea de plată, lista „Istoric facturi”, restul de plată (scadențar,
    bon, potrivire) și forma SQL a definiției spun 30.000, nu 36.300."""
    fid, _iid = _ti(conn)
    f = facturi_api.detalii_factura(conn, fid)
    assert (D(f["total"]), D(f["tva"])) == (D("36300.00"), D("6300.00"))                     # antetul neschimbat (declarațiile)
    assert (D(f["total_de_plata"]), D(f["tva_taxare_inversa"])) == (D("30000.00"), D("6300.00"))
    assert f["stare_incasare"]["stare"] == "neincasata" and D(f["stare_incasare"]["total"]) == D("30000.00"), f["stare_incasare"]
    lista = [x for x in facturi_api.lista_facturi(conn, directie="primita") if x["id"] == fid]
    assert D(lista[0]["total_de_plata"]) == D("30000.00") and D(lista[0]["stare_incasare"]["total"]) == D("30000.00")
    with conn.cursor() as cur:
        rest = [x for x in repo_facturi.de_incasat(cur, "primita") if x["id"] == fid][0]
        assert (rest["rest"], rest["rest_lei"]) == (D("30000.00"), D("30000.00")), rest
        cur.execute("SELECT " + facturi.SQL_TOTAL_DE_PLATA_LEI.format(a="f") + " FROM facturi f WHERE f.id = %s", (fid,))
        assert D(cur.fetchone()[0]) == D("30000.00")


@DB
def test_def_545_a_doua_factura_ti_1_de_la_acelasi_furnizor_se_refuza(conn):
    """545: aceeași factură (TI-1, același furnizor) introdusă a doua oară pe drumul taxării inverse (`creeaza_factura`, chemat de
    Operațiuni) -> refuzul numit, care o arată pe prima; nimic scris. MUTAȚIE: verificarea C73.1 scoasă din `creeaza_factura` -> pică."""
    fid, _iid = _ti(conn)
    with pytest.raises(chei_unice.CheieDublata) as e:
        _ti(conn)
    assert (e.value.valoare, e.value.existent) == ("TI1", {"facturi": [fid]}), (e.value.valoare, e.value.existent)
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE numar = 'TI-1'")
        assert cur.fetchone()[0] == 1


@DB
def test_def_547_factura_primita_cu_nota_ciorna_se_sterge_cu_notele_ei(conn):
    """547: factura primită introdusă greșit, cu nota încă ciornă -> „Șterge factura” o șterge împreună cu nota ei (liniile cad); nicio
    notă cu cheia ei nu rămâne. MUTAȚIE: fără ramura `primita_ciorna` din `sterge_factura` -> refuzul „are notă contabilă” -> pică."""
    fid, iid = _ti(conn)
    r = facturi_api.sterge_factura(conn, fid)
    assert r == {"ok": True, "note_sterse": 1}, r
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM inregistrari WHERE id = %s", (iid,))
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM inregistrari_linii WHERE inregistrare_id = %s", (iid,))
        assert cur.fetchone()[0] == 0


@DB
def test_def_547_factura_primita_cu_nota_validata_nu_se_sterge(conn):
    """547, ce rămâne refuzat: nota facturii VALIDATĂ (factura e în evidență) -> refuzul cu ieșirea „storno”; factura și nota rămân."""
    fid, iid = _ti(conn)
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari SET status = 'validata' WHERE id = %s", (iid,))
    with pytest.raises(contare_facturi.RefuzContare) as e:
        facturi_api.sterge_factura(conn, fid)
    assert e.value.cod == "ARE_NOTA_DE_CONTARE", e.value.cod
    with conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM facturi WHERE id = %s", (fid,))
        assert cur.fetchone()[0] == 1


@DB
def test_def_547_factura_emisa_nu_se_sterge_pe_drumul_primitei(conn):
    """Ramura nouă e numai a facturii PRIMITE: o factură emisă cu nota ciornă rămâne refuzată (CF art.330 alin.(1): se stornează)."""
    r = facturi_api.creeaza_factura(conn, "F1A1", "2099-03-11", "emisa", [{"descriere": "Servicii", "cantitate": 1, "pret_unitar": "100",
                                                                          "cota_tva": 21}],
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="14399840", status="de_preluat", serie="F1A")
    with pytest.raises(contare_facturi.RefuzContare):
        facturi_api.sterge_factura(conn, r["factura_id"])
