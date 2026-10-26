# -*- coding: utf-8 -*-
"""[lotul 13, comanda Costin 13.1 — deficiențele 662, 663, 664, 665, 666, 668, 580, 584] STAREA PAȘILOR DE PRELUARE, PE FIRMĂ
(`audit_preluare.stare_pasi`, citită de `GET /migrare/firma/{tenant_id}`, meniul Migrare cabinet cu firma în lucru, meniul „Import date”
și fereastra firmei).

Verbatim (anexa comenzii 13.1): 663 „Stările pașilor sunt pe cabinet, nu pe firma în lucru: după salvarea soldurilor F7, «Solduri inițiale»
rămâne «obligatoriu»; «Vector fiscal» arată «gata», deși pentru F7 nu s-a citit nimic. Pașii pe care soldurile salvate îi fac necesari (4
pentru 401/4111, 11 pentru 371 la cantitativ-valoric) nu devin obligatorii.” 665 „Un cont cu sold în balanță și fără parteneri trebuie să
țină pasul deschis.” 666 „Firma fără solduri (FISCALOS) apare «de încărcat» în loc de «nu e cazul»”. 662 „Firma nouă trebuie să deschidă cu
«Începe preluarea».” 668 „Fișele (3 articole, 4.100 lei) față de 371 din balanță (4.200) […] contul care nu se potrivește nu intră.”

CIFRELE sunt ale firmei F7 Preluare Test SRL din retestul lui Costin (balanța la 30.09.2026: 371 D 4.200, 401 C 3.000, 4111 D 2.500, 5121 D
10.000, 5311 D 500, 1012 C 200, 117 C 14.000; partenerii 4111: 1.500 + 1.000, 401 refuzat; articolele 1.500 + 1.600 + 1.000 = 4.100), pe o
schemă efemeră din șablon, în tranzacție anulată. CUI-urile partenerilor: cifra de control verificată (CLAUDE.md §10).
TEMEI: N/A — reguli de produs (comanda 13.1); confruntările sunt cele ale auditului de preluare (OMFP 1802/2014 pct.130: soldurile de
deschidere).
"""
import os

import pytest

from core import db as _db, audit_preluare as ap, migrare_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot13_migr_stare"
DATA = "2026-09-30"
BALANTA_F7 = (("1012", 0, 200), ("117", 0, 14000), ("371", 4200, 0), ("401", 0, 3000), ("4111", 2500, 0), ("5121", 10000, 0), ("5311", 500, 0))


def _cui_valid(c):
    ch = [7, 5, 3, 2, 1, 7, 5, 3, 2]
    corp, ctrl = c[:-1].rjust(9, "0"), int(c[-1])
    r = sum(int(corp[i]) * ch[i] for i in range(9)) * 10 % 11
    return (0 if r == 10 else r) == ctrl


ALFA, BETA, FURNIZOR = "401007106", "401007203", "401007300"
assert all(_cui_valid(c) for c in (ALFA, BETA, FURNIZOR))   # CLAUDE.md §10: CUI de test numai cu cifra de control verificată


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
    from core import tenant_provisioning as _tp
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCHEMA)
                cur.execute(_tp.parametrizeaza_template(open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, tip_firma) VALUES (1, 'PROBA 663 SRL', '14399840', 'srl')")
            yield c
        finally:
            c.rollback()


def _balanta(c, randuri=BALANTA_F7):
    with c.cursor() as cur:
        for cont, d, cr in randuri:
            cur.execute("INSERT INTO solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES (%s,%s,%s,%s)",
                        (cont, d, cr, DATA))


def _parteneri(c, randuri):
    with c.cursor() as cur:
        for cont, cui, den, d, cr in randuri:
            cur.execute("INSERT INTO solduri_parteneri (cont, cui, denumire, sold_debitor, sold_creditor, data_referinta) "
                        "VALUES (%s,%s,%s,%s,%s,%s)", (cont, cui, den, d, cr, DATA))


def _articole(c, randuri):
    with c.cursor() as cur:
        for den, cant, pret in randuri:
            cur.execute("INSERT INTO articole (denumire, um, cont_stoc, cont_cheltuiala) VALUES (%s, 'buc', '371', '607') RETURNING id", (den,))
            aid = cur.fetchone()[0]
            cur.execute("INSERT INTO miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document) "
                        "VALUES (%s, %s, 'intrare', %s, %s, %s, 'sold initial (import)')", (aid, DATA, cant, pret, cant * pret))


def _metoda(c, metoda):
    with c.cursor() as cur:
        cur.execute("UPDATE firma_profil SET metoda_stoc = %s WHERE id = 1", (metoda,))


def _stare(c):
    return ap.stare_pasi(c, SCHEMA, 999999, migrare_api.straturi_pentru("srl"))


def test_662_firma_noua_fara_nimic_incepe_preluarea_iar_partenerii_nu_sunt_cazul(conn):
    """662 + 666: firma fără balanță, fără note și fără nimic adus -> „Începe preluarea”; soldurile inițiale sunt obligatorii, iar
    soldurile pe parteneri „nu e cazul” (fără balanță n-are ce defalca — FISCALOS)."""
    s = _stare(conn)
    assert s["incepe_preluarea"] is True and s["in_preluare"] is False
    assert s["pasi"]["solduri"]["stare"] == "obligatoriu"
    assert s["pasi"]["solduri_parteneri"]["stare"] == "nu_e_cazul", s["pasi"]["solduri_parteneri"]
    assert s["pasi"]["solduri_parteneri"]["eticheta"] == "nu e cazul"
    assert s["pasi"]["vector_fiscal"]["stare"] == "obligatoriu"   # 663: nimic citit pentru firmă -> nu „gata”


def test_663_664_665_668_f7_dupa_balanta_pasii_necesari_devin_obligatorii(conn):
    """F7 după balanță (371 la cantitativ-valoric, 401 și 4111), cu partenerii numai pe 4111 și articolele de 4.100: soldurile inițiale
    „gata”; Solduri parteneri obligatoriu, cu 401 numit (creditor 3.000,00 lei); Articole obligatoriu, cu 371 numit (4.100 față de 4.200);
    pașii următori = vectorul, partenerii, articolele."""
    _balanta(conn)
    _metoda(conn, "cantitativ_valoric")
    _parteneri(conn, (("4111", ALFA, "Client Alfa Test SRL", 1500, 0), ("4111", BETA, "Client Beta Test SRL", 1000, 0)))
    _articole(conn, (("Marfa X Test", 10, 150), ("Marfa Y Test", 20, 80), ("Marfa Z Test", 5, 200)))
    s = _stare(conn)
    p = s["pasi"]
    assert p["solduri"]["stare"] == "gata" and p["solduri"]["exista"] == "balanța la 30.09.2026: 7 conturi"
    assert p["solduri_parteneri"]["stare"] == "obligatoriu", p["solduri_parteneri"]
    assert "401 (creditor 3.000,00 lei în balanță) — partenerii dau 0,00 lei" in p["solduri_parteneri"]["detaliu"]
    assert p["solduri_parteneri"]["exista"] == "2 parteneri"
    assert p["articole"]["stare"] == "obligatoriu", p["articole"]
    assert "371: stocul inițial 4.100,00 lei, balanța debitor 4.200,00 lei" in p["articole"]["detaliu"]
    assert s["urmatori"] == ["vector_fiscal", "solduri_parteneri", "articole"], s["urmatori"]
    assert s["incepe_preluarea"] is False and s["in_preluare"] is True
    assert p["mijloace_fixe"]["stare"] == "nu_e_cazul"   # balanța n-are 20x / 21x / 28x


def test_665_partenerii_care_dau_fiecare_cont_inchid_pasul_iar_stocul_potrivit_inchide_articolele(conn):
    """Când partenerii dau și 401 (3.000) și articolele dau 371 (4.200), cei doi pași sunt „gata”."""
    _balanta(conn)
    _metoda(conn, "cantitativ_valoric")
    _parteneri(conn, (("4111", ALFA, "Client Alfa Test SRL", 1500, 0), ("4111", BETA, "Client Beta Test SRL", 1000, 0),
                      ("401", FURNIZOR, "Furnizor Test SRL", 0, 3000)))
    _articole(conn, (("Marfa X Test", 10, 150), ("Marfa Y Test", 20, 80), ("Marfa Z Test", 5, 220)))   # 1.500 + 1.600 + 1.100 = 4.200
    p = _stare(conn)["pasi"]
    assert p["solduri_parteneri"]["stare"] == "gata", p["solduri_parteneri"]
    assert p["articole"]["stare"] == "gata", p["articole"]
    assert ap.nepotrivite_terti(conn, SCHEMA, ap.randuri_balanta(conn, SCHEMA)) == []


def test_668_global_valoric_articolele_nu_sunt_cazul(conn):
    """La metoda global-valorică stocul se ține pe conturi, fără fișe pe articole: pasul Articole „nu e cazul”."""
    _balanta(conn)
    _metoda(conn, "global_valoric")
    assert _stare(conn)["pasi"]["articole"]["stare"] == "nu_e_cazul"


def test_584_comportamentul_importului_e_spus_pe_fiecare_pas(conn):
    """584: fiecare pas spune ce face importul cu ce există (adaugă / actualizează / înlocuiește)."""
    p = _stare(conn)["pasi"]
    assert p["salariati"]["comportament"].startswith("Importul adaugă salariații noi și actualizează fișele celor cu același CNP")
    assert p["istoric_declaratii"]["comportament"].startswith("Un fișier nou înlocuiește istoricul preluat")
    assert set(ap.STARI_PAS) == {"gata", "obligatoriu", "nu_e_cazul", "optional"}
    assert all(v["stare"] in ap.STARI_PAS for v in p.values())
