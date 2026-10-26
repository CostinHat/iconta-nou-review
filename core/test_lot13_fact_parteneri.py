# -*- coding: utf-8 -*-
"""Lotul 13, comanda 13.1, zona `fact` — 632 și 640, fișele partenerilor (Clienți / Furnizori).

  * 632 (a) „După ce clientul primește fișă (salvare), coloana «Facturi emise» se golește (DANTE: 9 → gol); la fel «Facturi primite» la
    Furnizori.”
  * 640 „Același partener (DANTE) are două fișe separate, client și furnizor, cu localitatea de completat de două ori (la furnizor era
    goală, deși aplicația o știa).” + adăugare / ștergere.
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417); zilele SINTETICE (2099). CUI 14399840: cifra de control verificată
(`test_lot12_fact2_c73_dublura.test_cuiurile_de_proba_au_cifra_de_control_buna`). N/A temei fiscal: OMFP 2634/2015 nu cere fișe separate;
D394 / D406 citesc localitatea din fișă (`clienti_api.sql_camp_fisa`)."""
import pytest

from core import clienti_api
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _factura(conn, directie, cui="14399840", nume="DANTE INTERNATIONAL SA", numar="X1"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, total, tva, directie, status, tip, tert_cui, tert_nume) "
                    "VALUES (%s, '2099-01-05', 121, 21, %s, 'importata', 'factura', %s, %s) RETURNING id", (numar, directie, cui, nume))
        return cur.fetchone()[0]


@DB
def test_def_632_fisa_clientului_pastreaza_numarul_de_facturi(conn):
    """Două facturi emise către DANTE, apoi fișa lui salvată -> lista Clienți îl arată cu 2 facturi (nu gol); la furnizori, la fel.
    MUTAȚIE: fără coloana `facturi` din `_sql_lista` -> None -> pică."""
    _factura(conn, "emisa", numar="E1"); _factura(conn, "emisa", numar="E2"); _factura(conn, "primita", numar="P1")
    clienti_api.creeaza_client(conn, "DANTE INTERNATIONAL SA", cui="14399840")
    clienti_api.creeaza_furnizor(conn, "DANTE INTERNATIONAL SA", cui="RO14399840")
    c = [x for x in clienti_api.lista_clienti(conn) if x["cui"] == "14399840"][0]
    f = [x for x in clienti_api.lista_furnizori(conn) if x["cui"] == "14399840"][0]
    assert (c["facturi"], f["facturi"]) == (2, 1), (c, f)


@DB
def test_def_640_localitatea_scrisa_la_client_trece_si_la_furnizor(conn):
    """Același CUI, fișă de client și de furnizor: localitatea și județul scrise pe client ajung și pe furnizor (o singură completare);
    furnizorul fără fișă (numai facturi) primește propunerea din fișa clientului. MUTAȚIE: fără `_sincronizeaza_dupa` -> pică."""
    r = clienti_api.creeaza_client(conn, "DANTE INTERNATIONAL SA", cui="14399840")
    _factura(conn, "primita", numar="P1")
    fara = [x for x in clienti_api.parteneri_fara_fisa(conn, "furnizori") if x["cui"] == "14399840"][0]
    assert (fara["oras"], fara["judet"]) == (None, None)
    clienti_api.actualizeaza_client(conn, r["client_id"], oras="Sector 2", judet="B")
    fara = [x for x in clienti_api.parteneri_fara_fisa(conn, "furnizori") if x["cui"] == "14399840"][0]
    assert (fara["oras"], fara["judet"]) == ("Sector 2", "B"), fara
    clienti_api.creeaza_furnizor(conn, "DANTE INTERNATIONAL SA", cui="14399840")
    clienti_api.actualizeaza_client(conn, r["client_id"], oras="Sector 3")
    f = [x for x in clienti_api.lista_furnizori(conn) if x["cui"] == "14399840"][0]
    assert f["oras"] == "Sector 3" and f["oras_pereche"] == "Sector 3", f


@DB
def test_def_640_declaratiile_citesc_si_fisa_pereche(conn):
    """D394 / D406 (`sql_camp_fisa`): factura primită de la DANTE, fără localitate pe ea și fără fișă de furnizor, ia județul din fișa
    clientului cu același CUI."""
    clienti_api.creeaza_client(conn, "DANTE INTERNATIONAL SA", cui="14399840", oras="Sector 2", judet="B")
    fid = _factura(conn, "primita", numar="P9")
    with conn.cursor() as cur:
        cur.execute("SELECT " + clienti_api.sql_camp_fisa("judet") + " FROM facturi f WHERE f.id = %s", (fid,))
        assert cur.fetchone()[0] == "B"


@DB
def test_def_640_fisa_cu_facturi_nu_se_sterge_cea_fara_da(conn):
    """Fișa furnizorului cu o factură primită -> refuzul numit (localitatea ei intră în declarații); fișa fără documente -> se șterge."""
    _factura(conn, "primita", numar="P1")
    a = clienti_api.creeaza_furnizor(conn, "DANTE INTERNATIONAL SA", cui="14399840")["furnizor_id"]
    b = clienti_api.creeaza_furnizor(conn, "Furnizor fara facturi SRL")["furnizor_id"]
    r = clienti_api.sterge_furnizor(conn, a)
    assert r == {"ok": False, "cod": "ARE_FACTURI", "mesaj": "Furnizorul are 1 factură — fișa nu se șterge: localitatea și județul din ea "
                                                           "intră în D394 / D406."}, r
    assert clienti_api.sterge_furnizor(conn, b) == {"ok": True}
