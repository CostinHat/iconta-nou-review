# -*- coding: utf-8 -*-
"""[lotul 11, E2C — diagnosticul e2e-urilor Casei după deficiența 455] Verdictul pe care se sprijină e2e-urile reparate: refuzurile de
casă din plasa din 22.10.2026 (421, 406, 440) sunt CORECTE — ieșiri reale din casă fără numerarul din care să se facă —, iar verificarea
NU refuză ce nu e o ieșire din casă (încasarea, mutarea între analiticele casei), nici când registrul e negativ din cauza unei ciorne.

Comanda 11.3 pct.2, verbatim: „Registrul de casă, contul 5311 și verificarea de sold negativ folosesc aceeași cifră, din aceeași sursă.”
Temei: OMFP 1802/2014, funcțiunea contului 531: „Contul 531 "Casa" este un cont de activ. [...] Soldul contului reprezintă numerarul
existent în casierie.” (anaf_surse/omfp_1802_2014.html) — numerarul existent nu poate fi sub zero.
Schemă efemeră din template, ștearsă la ieșire (nu tabele partajate)."""
import io

import pytest

from core import casa_api as _ca, db as _db, jurnal_api as _j, tenant_provisioning as _tprov

_SCH = "efemer_e2c_casa"


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


@pytest.fixture()
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
            cur.execute(_tprov.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCH))
            cur.execute("SET LOCAL search_path TO %s, public" % _SCH)
            cur.execute("""INSERT INTO firma_profil (id,nume,cui,adresa,oras,judet,email,telefon,caen,declarant_nume,declarant_prenume,
                           declarant_functie,platitor_tva) VALUES (1,'F1 SRL','RO14399840','s','B','B','e@x.ro','07','4690','P','I','A',true)""")
        c.commit()
    with _db.get_conn(_SCH) as c:
        yield c
    with _db.get_conn() as c:
        with c.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCH)
        c.commit()


def _nota(conn, data, linii, descriere, doc, valideaza=True):
    """Drumul Registrului jurnal (ca `e2e_bloc_e._nota`): `jurnal_api.creeaza`, apoi `jurnal_api.valideaza` la cerere."""
    r = _j.creeaza(conn, _SCH, descriere, data, linii, doc)
    assert r.get("ok"), r
    return r["id"], (_j.valideaza(conn, _SCH, r["id"]) if valideaza else None)


def test_421_platile_din_casa_cer_intai_numerarul(conn):
    """e2e 421 (`e2e_lot11_w4.py`): 30 de plăți 6022 = 5311 (1 … 30 lei) pe o casă goală. Prima se refuză la validare — refuz corect, nu
    o regresie a lui 455; după ridicarea de la bancă (5311 = 581, 500 lei, validată) toate trec, iar registrul arată 500 − 465 = 35 lei."""
    nid, v = _nota(conn, "2026-10-01", [{"debit": "6022", "credit": "5311", "suma": 1}], "Consum 0", "Bon 0")
    # OMFP 1802/2014, contul 531: „Soldul contului reprezintă numerarul existent în casierie.” — 0 lei în casă, plata de 1 leu nu încape
    assert v.get("cod") == "CASA_NEGATIVA" and v["eroare"].startswith(
        "Nota de 1,00 lei nu încape în casă (contul 5311): soldul casei pe 01.10.2026, în evidența validată, e 0,00 lei"), v
    _nid, v = _nota(conn, "2026-10-01", [{"debit": "5311", "credit": "581", "suma": 500}], "Ridicare numerar", "Cec 1")
    assert v.get("ok"), v
    assert _j.valideaza(conn, _SCH, nid).get("ok")
    for i in range(1, 30):
        _x, v = _nota(conn, "2026-10-01", [{"debit": "6022", "credit": "5311", "suma": 1 + i}], "Consum %d" % i, "Bon %d" % i)
        assert v.get("ok"), (i, v)
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert (reg["sold_final"], reg["sold_final_validat"]) == ("35.00", "35.00"), reg   # 500 − (1 + … + 30) = 500 − 465


def _plata(suma, dest):
    op = {"data": "2026-10-19", "categorie": "plata_furnizor", "suma": suma, "document": "DP1", "partener": "X SRL", "cui": "14399840"}
    if dest:
        op["avans_destinatie"] = dest
    return op


def test_406_440_refuzul_dispozitiei_numeste_suma_si_numai_ce_lipseste(conn):
    """e2e 406 (`e2e_lot92.py`) și 440 (`e2e_lot11_w3a.py`): 142 lei în casă, plată de 200 lei către un furnizor fără facturi deschise
    (avans acordat, 407). Cu destinația aleasă: o singură eroare, a sumei; fără destinație: amândouă deodată (440). Nimic scris."""
    assert _ca.adauga(conn, _SCH, {"data": "2026-10-15", "categorie": "ridicare_banca", "suma": 142, "document": "DI1"}).get("eroare") is None
    cu = _ca.adauga(conn, _SCH, _plata(200, "servicii"))
    assert [e["camp"] for e in cu["erori_campuri"]] == ["c-suma"] and cu["cod"] == "CASA_NEGATIVA", cu
    assert "soldul casei pe 19.10.2026, în registru, e 142,00 lei, iar după ea casa ar ajunge la -58,00 lei" in cu["eroare"], cu
    fara = _ca.adauga(conn, _SCH, _plata(200, None))
    assert [e["camp"] for e in fara["erori_campuri"]] == ["c-suma", "c-avans-dest"], fara
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert reg["sold_final"] == "142.00" and [o["suma"] for o in reg["operatiuni"]] == ["142.00"], reg
    assert _ca.adauga(conn, _SCH, _plata(142, "servicii")).get("eroare") is None   # încape exact


def test_455_ce_nu_e_iesire_din_casa_nu_se_refuza_nici_cu_registrul_negativ(conn):
    """Registrul e negativ din cauza unei ieșiri în CIORNĂ (6022 = 5311, 50 lei, pe casa goală — ciorna nu se refuză la scriere în jurnal).
    Încasarea (5311 = 1012, 30 lei) și mutarea între analiticele casei (5311.01 = 5311, variația pe 5311 = 0) NU sunt ieșiri: se validează
    (refuzul lor ar bloca tocmai repararea casei). Ieșirea în ciornă rămâne refuzată la validare: 30 − 50 < 0."""
    iesire, _v = _nota(conn, "2026-10-05", [{"debit": "6022", "credit": "5311", "suma": 50}], "Consum", "Bon 50", valideaza=False)
    _i, v = _nota(conn, "2026-10-05", [{"debit": "5311", "credit": "1012", "suma": 30}], "Aport capital", "DI 30")
    assert v.get("ok"), v   # o intrare în casă nu e o ieșire: nu trece prin refuz (OMFP 1802/2014, contul 531, soldul = numerarul existent)
    with conn.cursor() as cur:   # analiticul casei, dată de pornire (planul firmei)
        cur.execute("INSERT INTO plan_conturi (simbol, denumire, tip) VALUES ('5311.01', 'Casa punct de lucru', 'A')")
    _t, v = _nota(conn, "2026-10-05", [{"debit": "5311.01", "credit": "5311", "suma": 20}], "Mutare analitic", "PV 1")
    assert v.get("ok"), v   # mutarea în casa 5311 (analitic) nu schimbă numerarul din casă
    r = _j.valideaza(conn, _SCH, iesire)
    assert r.get("cod") == "CASA_NEGATIVA" and "nu încape în casă" in r["eroare"], r
    reg = _ca.registru(conn, _SCH, 2026, 10)
    assert (reg["sold_final"], reg["sold_final_validat"]) == ("-20.00", "30.00"), reg   # registrul (cu ciorna) și fișa (validate)
