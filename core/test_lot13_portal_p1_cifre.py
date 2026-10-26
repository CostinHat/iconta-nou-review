# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”) — portalul clientului, cifrele (fork P1 al subagentului PORTAL).

  553  „Cifrele firmei”: „Profit −6.075 lei” la rezultat negativ (clientul citește „Pierdere”; e înainte de impozit); previziunea pe 8
       săptămâni: în prima săptămână 15.423 lei fără explicație; media cheltuielilor „~117 lei” față de 15.074 cheltuiți.
  554  Clientul vede ce are de plătit și până când (TVA, impozit, contribuții), cu sume, în cuvintele lui — nu codurile declarațiilor.
  555  „Declarații depuse”: rândul arăta doar „d406 · depusă” (fără perioadă, dată, recipisă).
  559  „Portalul folosește aceeași bază peste tot”: „De încasat” (balanța) față de Scadențar (și facturi cu note nevalidate).

Temei: 553 — OMFP 1802/2014, grupa 69 „Cheltuieli cu impozitul pe profit și alte impozite” (anaf_surse/omfp_1802_2014.txt): rezultatul
înainte de impozit nu le cuprinde (`motor.GRUPE_IMPOZIT`, aceeași listă ca pachetul lunar); 554 — CF art.326 alin.(1) (TVA), art.80 alin.(1),
art.146 alin.(3), art.168 alin.(3), art.220^6 alin.(1) (salarii), art.56 alin.(1) / art.41 alin.(1) (impozitul firmei), citate în
`uc_portal.PLATI_DIN_DECLARATII`; 555, 559 — N/A, regulă de produs. Schemă efemeră din template, în tranzacție anulată (fixtura lui 417),
perioade sintetice 2099. CUI 14399840 (DANTE INTERNATIONAL SA): cifra de control verificată.
"""
import datetime
from decimal import Decimal as D

import pytest

from core import cashflow, kpi_client, portal_api, repo_portal, uc_portal
from core.test_417_storno_trimitere import _db_ok, conn  # noqa: F401 — fixtura și ajutoarele ei

DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
AZI = datetime.date(2099, 10, 22)


def _r(cont, **k):
    b = {"cont": cont, "denumire": "", "si_d": 0, "si_c": 0, "prec_d": 0, "prec_c": 0,
         "rul_d": 0, "rul_c": 0, "tot_d": 0, "tot_c": 0, "sf_d": 0, "sf_c": 0}
    b.update(k)
    return b


# ── 553 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_553_rezultatul_negativ_e_pierdere_inainte_de_impozit():
    """Venituri 1.000, cheltuieli 1.500 + impozit 698 de 10: pierdere înainte de impozit 500, felul „pierdere”. MUTAȚIE: `GRUPE_IMPOZIT`
    scos din `kpi_din_balanta` -> cheltuieli 1.510, pierdere 510 -> pică."""
    k = kpi_client.kpi_din_balanta([_r("704", rul_c=1000), _r("628", rul_d=1500), _r("698", rul_d=10)])
    # OMFP 1802/2014 grupa 69: impozitul nu e cheltuială a rezultatului „înainte de impozit”
    assert (k["cheltuieli"], k["profit"], k["tip"]) == (1500, -500, "pierdere"), k
    assert kpi_client.kpi_din_balanta([_r("704", rul_c=10)])["tip"] == "profit"
    assert kpi_client.kpi_din_balanta([])["tip"] == "neutru"


def test_def_553_saptamana_isi_spune_componentele():
    """Săptămâna întâi a lui F1 (22.10): furnizori 3.000 (sold preluat fără factură), salarii nete 8.347, impozite și contribuții 5.866 —
    plățile 17.213 se desfac în trei componente numite, a căror sumă e exact plata săptămânii. MUTAȚIE: `componente` goale în `forecast`
    -> pică."""
    azi = datetime.date(2099, 10, 22)
    primite = (cashflow.din_facturi([], 3000, cashflow.CE_FACTURI_FURNIZORI, cashflow.CE_SOLD_PLATIT_FARA_FACTURA, azi)
               + cashflow.plati_estimate({"salarii_nete": 8347.0, "fiscale": 5866.0}, 0, azi=azi))
    s1 = cashflow.forecast(17759, [], primite, azi=azi, saptamani=1)[0]
    comp = {c["ce"]: c["suma"] for c in s1["componente"] if c["sens"] == "-"}
    assert comp == {cashflow.CE_SOLD_PLATIT_FARA_FACTURA: 3000.0, cashflow.CE_SALARII: 8347.0, cashflow.CE_FISCALE: 5866.0}, comp
    assert s1["plati"] == sum(comp.values()) == 17213.0


def test_def_553_media_cuprinde_salariile_si_lunile_cu_evidenta():
    """F1: cheltuieli 15.148,86 (din care 641 13.900, 646 313), evidență din septembrie (fără rulaje preluate) -> pe octombrie media e
    15.148,86 / 2 = 7.574,43 (înainte: fără 641 și împărțit la 10 -> 124,89). Amortizarea (6811) și impozitul (698) nu intră.
    MUTAȚIE: `luni_cu_evidenta` întoarce mereu luna calendaristică (10) -> 1.514,89 -> pică."""
    bal = [_r("607", prec_d=500, rul_d=377.62), _r("627", rul_d=15), _r("635", rul_d=43.24), _r("641", prec_d=13900),
           _r("646", prec_d=313), _r("6811", rul_d=400), _r("698", rul_d=50)]
    de_la, luni = cashflow.luni_cu_evidenta(datetime.date(2026, 10, 22), (2026, 9), False)
    assert (de_la, luni) == (9, 2)
    assert cashflow.cheltuieli_lunare_cash(bal, luni) == 7574.43
    assert cashflow.luni_cu_evidenta(datetime.date(2026, 10, 22), (2026, 9), True) == (1, 10)    # rulajele anului preluate: cumul de la 1 ianuarie
    assert cashflow.luni_cu_evidenta(datetime.date(2026, 10, 22), (2025, 3), False) == (1, 10)   # evidență mai veche decât anul
    assert cashflow.luni_cu_evidenta(datetime.date(2026, 10, 22), None, False) == (1, 10)


def test_def_553_micro_are_impozitul_la_obligatii():
    """CF art.56 alin.(1): impozitul micro „se efectuează trimestrial, până la data de 25 inclusiv a lunii următoare trimestrului” — 4418
    intră la obligațiile fiscale ale previziunii (lipsea)."""
    assert cashflow.obligatii_din_balanta([_r("4418", sf_c=120), _r("4423", sf_c=80)])["fiscale"] == 200.0


# ── 554 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_554_de_platit_in_cuvintele_clientului_cu_sumele_din_balanta():
    """Obligațiile F1 pe 22.10: D300 / D112 / D100 de urmărit (termen 26.10), D394 / D406 (fără plată), o D406 veche depusă. Clientul vede:
    contribuțiile 5.866 (431 + 436 + 444 la 30.09), impozitul micro fără sumă încă („o calculează contabilul”), TVA 1.486 (4423); nimic
    despre D394 / D406. MUTAȚIE: filtrul `PLATI_DIN_DECLARATII` scos -> apar D394 / D406 -> pică."""
    rez = {"urmarit": [{"tip": "d300", "an": 2099, "luna": 9, "termen": "2099-10-26", "perioada": "09/2099"},
                       {"tip": "d394", "an": 2099, "luna": 9, "termen": "2099-10-30", "perioada": "09/2099"},
                       {"tip": "d112", "an": 2099, "luna": 9, "termen": "2099-10-26", "perioada": "09/2099"},
                       {"tip": "d100", "an": 2099, "luna": 9, "termen": "2099-10-26", "perioada": "T3/2099"},
                       {"tip": "d406", "an": 2099, "luna": 9, "termen": "2099-11-02", "perioada": "09/2099"}],
           "confirmate": [{"tip": "d300", "an": 2099, "luna": 1, "termen": "2099-02-25", "perioada": "01/2099"}]}
    bal = [_r("4315", sf_c=3475), _r("4316", sf_c=1390), _r("436", sf_c=313), _r("444", sf_c=688), _r("4423", sf_c=1486), _r("4111", sf_d=9)]
    p = uc_portal.de_platit(rez, lambda an, luna: bal, "micro", AZI)
    assert [(x["ce"], x["perioada"], x["termen"]) for x in p] == [
        ("Contribuții sociale și impozitul pe salarii", "09/2099", "2099-10-26"),
        ("Impozitul pe veniturile microîntreprinderii", "T3/2099", "2099-10-26"),
        ("TVA de plată", "09/2099", "2099-10-26")], p
    sume = {x["ce"]: x["suma"] for x in p}
    assert D(sume["Contribuții sociale și impozitul pe salarii"]) == D("5866")     # CF art.80 / 146 / 168 / 220^6: 25 a lunii următoare
    assert D(sume["TVA de plată"]) == D("1486")                                     # CF art.326 alin.(1)
    assert sume["Impozitul pe veniturile microîntreprinderii"] is None             # 4418 fără sold: încă necalculat
    assert all(not x["ce"].lower().startswith("d") for x in p)


def test_def_554_depusa_fara_sold_nu_mai_e_de_platit_iar_termenul_trecut_iese():
    rez = {"urmarit": [], "confirmate": [{"tip": "d300", "an": 2099, "luna": 9, "termen": "2099-10-26", "perioada": "09/2099"},
                                         {"tip": "d112", "an": 2099, "luna": 8, "termen": "2099-09-25", "perioada": "08/2099"}]}
    assert uc_portal.de_platit(rez, lambda an, luna: [_r("431", sf_c=100)], "profit", AZI) == []


# ── 555 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
class _Cur:
    def __init__(self, randuri):
        self.r = randuri

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, *a):
        pass

    def fetchall(self):
        return self.r


class _Conn:
    def __init__(self, randuri):
        self.r = randuri

    def cursor(self, *a, **k):
        return _Cur(self.r)


def test_def_555_randul_declaratiei_are_perioada_data_si_recipisa():
    """Rândul D406 al F1: „D406 · 01/2026”, denumirea, „depusă pe 02.03.2026” (ora României) și „recipisa TEST-1”. MUTAȚIE: `recipisa`
    scoasă din rând -> pică."""
    import zoneinfo
    t = datetime.datetime(2026, 3, 1, 22, 0, tzinfo=datetime.timezone.utc)      # = 02.03.2026 00:00 la București
    (d,) = portal_api.declaratii_depuse(_Conn([("d406", 2026, 1, t, " TEST-1 ")]), 105779)
    assert (d["cod"], d["perioada"], d["data"], d["recipisa"]) == ("D406", "01/2026", "2026-03-02", "TEST-1"), d
    assert d["denumire"] == "Fișierul Standard de Control Fiscal (SAF-T) pentru România"
    assert zoneinfo.ZoneInfo("Europe/Bucharest")
    assert portal_api.denumire_declaratie("d300") == "Decont de TVA" and portal_api.denumire_declaratie("x; import os") is None


# ── 559 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _factura(conn, numar, total, total_lei, moneda="RON", tip="factura", scadenta="2099-11-16"):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO facturi (numar, data_emitere, data_scadenta, directie, total, tva, total_lei, tva_lei, curs_bnr, moneda, "
                    "tert_nume, tert_cui, status, tip) VALUES (%s, '2099-10-17', %s, 'emisa', %s, 0, %s, 0, 1, %s, "
                    "'DANTE INTERNATIONAL SA', '14399840', 'emisa', %s) RETURNING id", (numar, scadenta, total, total_lei, moneda, tip))
        return cur.fetchone()[0]


def _nota(conn, fid, status):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, descriere, sursa, status, factura_id) VALUES ('2099-10-17', 'Factură', 'facturi', %s, %s) "
                    "RETURNING id", (status, fid))
        iid = cur.fetchone()[0]
        cur.execute("INSERT INTO inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, '4111', '704', 1)", (iid,))


@DB
def test_def_559_de_incasat_si_scadentarul_au_aceeasi_baza(conn):
    """F1A5 (1.000 lei, nota validată), F1A15 (500 lei, nota ciornă), soldul preluat (2.000 lei, fără notă), F1A14 (60,50 EUR = 323,64 lei,
    nota validată): portalul vede 3.000 lei + 60,50 EUR, total 3.323,64 lei — aceleași trei facturi ca Scadențarul clientului; F1A15 (ciornă) lipsește din amândouă. Balanța arată 3.968,24: diferența 644,60 se spune. MUTAȚIE: `conditie_nota_validata`
    întoarce "" -> F1A15 intră -> pică."""
    from core import nomenclator_status_factura as _nsf
    assert "f.tip = '%s'" % _nsf.TIP_SOLD_PRELUAT in repo_portal.CONDITIE_NOTA_VALIDATA   # aceeași valoare ca nomenclatorul
    a = _factura(conn, "F1A5", 1000, 1000)
    b = _factura(conn, "F1A15", 500, 500)
    c = _factura(conn, "Sold la 31.08.2099", 2000, 2000, tip="preluata", scadenta=None)
    e = _factura(conn, "F1A14", D("60.50"), D("323.64"), moneda="EUR")
    _nota(conn, a, "validata")
    _nota(conn, b, "ciorna")
    _nota(conn, e, "validata")
    with conn.cursor() as cur:
        f = repo_portal.facturi_deschise_validate(cur, "emisa")
    assert sorted(x["id"] for x in f) == sorted([a, c, e]), f
    pm = uc_portal._pe_moneda(f, D("3968.24"))
    assert pm["pe_moneda"] == [{"moneda": "RON", "suma": "3000.00"}, {"moneda": "EUR", "suma": "60.50"}], pm
    assert (D(pm["total_lei"]), D(pm["fara_factura"])) == (D("3323.64"), D("644.60")), pm
    # previziunea pornește din aceleași facturi, fiecare la scadența ei, iar diferența față de balanță intră o dată, numită
    inc = cashflow.din_facturi(f, D("3968.24"), cashflow.CE_FACTURI_CLIENTI, cashflow.CE_SOLD_INCASAT_FARA_FACTURA, AZI)
    assert sum(x["suma"] for x in inc) == D("3968.24")
    assert [x["suma"] for x in inc if x["ce"] == cashflow.CE_SOLD_INCASAT_FARA_FACTURA] == [D("644.60")]
