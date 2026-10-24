# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `scad` — scadențarul și starea de încasare.

  466 (grav) „Scadențar: facturi încasate apar neîncasate.” Cauza: scadențarul (și notificările de scadență, și potrivirea bonului cu factura
      primită) socoteau „neîncasată” orice factură fără `platita_la` — pusă numai de chitanța integrală / bonul stins; factura încasată prin
      bancă rămânea „restantă”, iar notificarea de plată pleca la client. Acum: starea UNICĂ (`repo_facturi.de_incasat` ->
      `facturi_api._cu_stare_incasare`), cu restul facturii încasate parțial.
  468 (grav) „Scadențar: totalul pe client adună lei cu euro.” Acum soldul și restanța clientului PE MONEDĂ (`scadentar.scadentar`,
      `solduri`); aceeași clasă: cashflow-ul (totalul în lei, `pentru_cashflow`) și starea de încasare din „Istoric facturi” (totalul în lei
      comparat cu încasările în lei — lista nu citea `tva_lei`, iar o factură de 1.000 EUR cu 2.000 lei încasați ieșea „încasată”).

Temei: OMFP 1802/2014 pct.322 alin.(1) — „Diferențele de curs valutar care apar cu ocazia decontării creanțelor și datoriilor în valută la
cursuri diferite față de cele la care au fost înregistrate inițial [...] trebuie recunoscute în luna în care apar, ca venituri sau cheltuieli
din diferențe de curs valutar” (anaf_surse/omfp_1802_2014_reglementari_consolidat.txt): plata stinge creanța la valoarea ei din evidență,
deci restul în valută = totalul în valută × restul în lei / totalul în lei (INTERPRETARE CU TEMEI, aceeași ca `reevaluare_valuta`).
Schemă efemeră din template, în tranzacție anulată (fixtura lui 417). CUI 14399840 (DANTE INTERNATIONAL SA): cifra de control verificată."""
import datetime
from decimal import Decimal as D

import pytest

from core import facturi_api, repo_facturi, repo_notificari_scadenta, repo_scadentar, scadentar
from core.test_417_storno_trimitere import _LINIE, _db_ok, conn  # noqa: F401 — fixtura și ajutoarele ei

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
_AZI = datetime.date(2099, 12, 31)


def _rd(conn):
    import psycopg2.extras as _E
    return conn.cursor(cursor_factory=_E.RealDictCursor)


def _emisa(conn, numar, scadenta="2099-05-01"):
    r = facturi_api.creeaza_factura(conn, numar, "2099-04-01", "emisa", [dict(_LINIE)], data_scadenta=scadenta,
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840", status="emisa")
    return r["factura_id"]


def _incasare(conn, fid, suma, cont_credit="4111", status="validata"):
    """Încasarea prin bancă legată de factură (nota 5121 = 4111, `inregistrari.factura_id`) — ca reconcilierea bancară."""
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id) VALUES ('2099-04-10', 'Încasare extras', "
                    "'banca', %s, %s) RETURNING id", (status, fid))
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '5121', %s, %s)",
                    (iid, cont_credit, suma))


def _valuta(conn, numar, total, total_lei, directie="emisa"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, data_scadenta, directie, total, tva, total_lei, tva_lei, curs_bnr, moneda, "
                    "tert_nume, tert_cui, status, tip) VALUES (%s, '2099-04-01', '2099-05-01', %s, %s, 0, %s, 0, 5, 'EUR', "
                    "'DANTE INTERNATIONAL SA', '14399840', 'emisa', 'factura') RETURNING id", (numar, directie, total, total_lei))
        return cur.fetchone()[0]


@DB
def test_def_466_factura_incasata_prin_banca_nu_mai_e_de_incasat(conn):
    """466. O factură de 121 lei încasată integral prin bancă (nota 5121 = 4111 legată de ea) iese din scadențar și din notificările de
    scadență; una încasată parțial (21 din 121) rămâne cu restul de 100. MUTAȚIE: `repo_scadentar.select_facturi` înapoi pe
    `platita_la IS NULL` -> pică (factura încasată rămâne)."""
    a, b = _emisa(conn, "F1A501"), _emisa(conn, "F1A502")
    _incasare(conn, a, 121)
    _incasare(conn, b, 21)
    with _rd(conn) as cur:
        sc = {r["id"]: r["suma"] for r in repo_scadentar.select_facturi(cur)}
        nt = {r["id"]: r["suma"] for r in repo_notificari_scadenta.select_facturi(cur, _AZI)}
    assert a not in sc and a not in nt, (sc, nt)                 # încasată integral: nimic de încasat, nicio notificare
    assert sc[b] == D("100.00") and nt[b] == D("100.00"), (sc, nt)   # 121 − 21 = 100 de încasat
    # aceeași stare ca pe factură („Istoric facturi”), nu una paralelă
    assert facturi_api.detalii_factura(conn, a)["stare_incasare"]["stare"] == "incasata"
    assert facturi_api.detalii_factura(conn, b)["stare_incasare"]["stare"] == "partial"


@DB
def test_def_466_notificarile_pe_cursor_simplu_au_forma_de_tuplu(conn):
    """`notificari_scadenta._plan_notificari` citește rândurile pe poziție: (id, numar, data_scadenta, suma, moneda, client_email)."""
    a = _emisa(conn, "F1A503")
    with conn.cursor() as cur:
        rows = [r for r in repo_notificari_scadenta.select_facturi(cur, _AZI) if r[0] == a]
    assert rows == [(a, "F1A503", datetime.date(2099, 5, 1), D("121.00"), "RON", None)], rows


@DB
def test_def_466_bonul_nu_mai_e_potrivit_cu_o_factura_primita_platita(conn):
    """Aceeași clasă: candidatele bonului fiscal sunt facturile primite care MAI AU de plătit (o plată prin bancă le scoate)."""
    with conn.cursor() as cur:
        cur.execute("SELECT current_schema()")
        schema = cur.fetchone()[0]
    p = _valuta(conn, "FP-1", 100, 500, directie="primita")
    q = _valuta(conn, "FP-2", 100, 500, directie="primita")
    _incasare(conn, p, 500, cont_credit="5121")   # nota 401 = 5121 de mai jos
    with conn.cursor() as cur:
        cur.execute("UPDATE inregistrari_linii SET cont_debit = '401', cont_credit = '5121' WHERE inregistrare_id IN "
                    "(SELECT id FROM inregistrari WHERE factura_id = %s)", (p,))
        ids = [x[0] for x in repo_facturi.candidate_pentru_bon(cur, schema, "14399840", 500)]
    assert p not in ids and q in ids, ids


def test_def_468_soldul_clientului_se_tine_pe_moneda():
    """468. Clientul cu o factură în lei (1.210) și una în euro (500): soldul NU e 1.710 „lei”, ci 1.210,00 lei + 500,00 EUR; restanța la
    fel, pe moneda ei. MUTAȚIE: `m = c["pe_moneda"].setdefault(_moneda(f) …` cu o singură cheie -> pică."""
    z = datetime.date(2099, 6, 1)
    f = [{"id": 1, "numar": "F1", "data_scadenta": datetime.date(2099, 5, 1), "suma": D("1210.00"), "rest_lei": D("1210.00"), "moneda": "RON",
          "tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "14399840"},
         {"id": 2, "numar": "F2", "data_scadenta": datetime.date(2099, 7, 1), "suma": D("500.00"), "rest_lei": D("2500.00"), "moneda": "EUR",
          "tert_nume": "DANTE INTERNATIONAL SA", "tert_cui": "14399840"}]
    r = scadentar.scadentar(f, z)
    assert len(r["clienti"]) == 1
    c = r["clienti"][0]
    assert c["solduri"] == [{"moneda": "RON", "sold": D("1210.00"), "restant": D("1210.00")},
                            {"moneda": "EUR", "sold": D("500.00"), "restant": D("0")}], c
    assert {l["client_cheie"] for l in r["linii"]} == {c["cheie"]} == {"14399840"}


@DB
def test_def_468_restul_facturii_in_valuta_e_in_valuta(conn):
    """468. Factura de 100 EUR (500 lei în evidență) încasată cu 250 lei: rămân 50,00 EUR de încasat (nu 250, nici 100 − 250)."""
    fid = _valuta(conn, "FE-1", 100, 500)
    _incasare(conn, fid, 250)
    with _rd(conn) as cur:
        r = [x for x in repo_facturi.de_incasat(cur, "emisa") if x["id"] == fid]
    assert [(x["moneda"], x["rest"], x["rest_lei"]) for x in r] == [("EUR", D("50.00"), D("250.00"))], r


@DB
def test_def_468_istoricul_compara_lei_cu_lei(conn):
    """Aceeași clasă, în „Istoric facturi”: factura de 1.000 EUR (5.000 lei) cu 2.000 lei încasați e „încasată parțial: 2.000 din 5.000
    lei”, nu „încasată” (lista nu citește `tva_lei`, iar totalul cădea pe valuta). MUTAȚIE: `_cu_stare_incasare` înapoi pe `antet_lei`
    singur -> pică."""
    fid = _valuta(conn, "FE-2", 1000, 5000)
    _incasare(conn, fid, 2000)
    st = [f["stare_incasare"] for f in facturi_api.lista_facturi(conn, an=2099, luna=4) if f["id"] == fid]
    assert st == [{"stare": "partial", "incasat": "2000.00", "total": "5000.00"}], st


@DB
def test_def_468_cashflow_aloca_in_lei(conn):
    """Aceeași clasă: cashflow-ul împarte soldul balanței (lei) pe facturi cu totalul în LEI (500), nu în valută (100)."""
    fid = _valuta(conn, "FE-3", 100, 500)
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM facturi WHERE id = %s", (fid,))
        tot = [float(r[3]) for r in repo_facturi.pentru_cashflow(cur)]
    assert tot == [500.0], tot
