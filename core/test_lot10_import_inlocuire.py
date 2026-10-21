# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 426, comanda Costin 10.1, verbatim în DECIZII „Comanda 10.1”] „al doilea import de balanță pentru aceeași firmă
o înlocuiește pe prima fără avertisment. Înainte de înlocuire: spune că există deja o balanță, arată totalurile vechi și noi, cere
confirmare; dacă există note pe lunile de după preluare, spune că soldurile lor se recalculează.”

TEMEI: N/A — regulă de produs (nimic nu se înlocuiește pe tăcute, comanda 8.2 pct.4). „Se recalculează” e faptul din cod: soldurile la o
zi sunt „soldurile de preluare + mișcările validate de după data lor” (`bilant_api.sold_la`), deci o balanță nouă le schimbă.
Schemă efemeră din template, tranzacție anulată."""
import contextlib
import os

import pytest

from core import db as _db, solduri_api

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA = "ztest_lot10_inlocuire"
VECHE = [{"cont": "1012", "denumire": "Capital", "debit": 0, "credit": 1000}, {"cont": "5121", "denumire": "Bancă", "debit": 1000, "credit": 0}]
NOUA = [{"cont": "1012", "denumire": "Capital", "debit": 0, "credit": 2500}, {"cont": "5311", "denumire": "Casa", "debit": 500, "credit": 0},
        {"cont": "5121", "denumire": "Bancă", "debit": 2000, "credit": 0}]


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
            yield c
        finally:
            c.rollback()


def _nota(c, data):
    with c.cursor() as cur:
        cur.execute("INSERT INTO inregistrari (data, numar, descriere) VALUES (%s, 'N1', 'probă') RETURNING id", (data,))


def test_def_426_a_doua_balanta_nu_inlocuieste_fara_confirmare(conn):
    """ROȘU înainte: `importa` făcea DELETE + INSERT fără nicio întrebare. MUTAȚIA: condiția `vechi["are_solduri"] and not inlocuieste`
    scoasă -> a doua balanță trece fără confirmare -> pică."""
    solduri_api.importa(conn, VECHE, "2026-06-30")
    _nota(conn, "2026-08-14")
    _nota(conn, "2026-07-02")
    _nota(conn, "2026-06-30")                                # în ziua balanței: nu e „după”
    with pytest.raises(solduri_api.BalantaExistenta) as e:
        solduri_api.importa(conn, NOUA, "2026-06-30")
    m = str(e.value)
    assert m == ("Firma are deja o balanță de deschidere la 30.06.2026: 2 conturi, debit 1.000,00 lei, credit 1.000,00 lei. Balanța nouă "
                 "la 30.06.2026: 3 conturi, debit 2.500,00 lei, credit 2.500,00 lei. Salvarea o înlocuiește pe cea veche. Firma are 2 note "
                 "contabile după data balanței (prima la 02.07.2026): soldurile lor se recalculează pe balanța nouă. Confirmă înlocuirea "
                 "și salvează din nou."), m
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), sum(sold_debitor) FROM solduri_initiale")
        assert cur.fetchone() == (2, 1000)                   # balanța veche e neatinsă
    rez = solduri_api.importa(conn, NOUA, "2026-06-30", inlocuieste=True)
    assert rez["inlocuita"]["randuri"] == 2 and rez["note_dupa"] == {"numar": 2, "prima": "2026-07-02"}
    with conn.cursor() as cur:
        cur.execute("SELECT count(*), sum(sold_debitor) FROM solduri_initiale")
        assert cur.fetchone() == (3, 2500)


def test_426_prima_balanta_nu_cere_confirmare(conn):
    rez = solduri_api.importa(conn, VECHE, "2026-06-30")
    assert rez["inlocuita"] is None and rez["note_dupa"] == {"numar": 0, "prima": None}


def test_426_ruta_raspunde_409_fara_confirmare(conn, monkeypatch):
    """Use-case-ul: `BalantaExistenta` -> `Conflict` (409), cu textul totalurilor; cu `inlocuieste` -> scris."""
    import main
    from core import erori, uc_tenants, uc_comun

    @contextlib.contextmanager
    def _gc(schema=None):
        yield conn
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCHEMA)
    solduri_api.importa(conn, VECHE, "2026-06-30")
    corp = main.SolduriIn(randuri=[main.SoldRand(**r) for r in NOUA], data_referinta="2026-06-30")
    with pytest.raises(erori.Conflict) as e:
        uc_tenants.solduri_salveaza(1, corp, {"uid": 7})
    assert str(e.value).startswith("Firma are deja o balanță de deschidere la 30.06.2026: 2 conturi")
    corp.inlocuieste = True
    assert uc_tenants.solduri_salveaza(1, corp, {"uid": 7})["randuri"] == 3


def test_426_previzualizarea_arata_balanta_existenta_si_notele(conn, monkeypatch):
    from core import uc_tenants, uc_comun

    @contextlib.contextmanager
    def _gc(schema=None):
        yield conn
    monkeypatch.setattr(uc_tenants.db, "get_conn", _gc)
    monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: SCHEMA)
    monkeypatch.setattr(uc_tenants, "_data_soldurilor", lambda c, s: "2026-06-30")
    solduri_api.importa(conn, VECHE, "2026-06-30")
    _nota(conn, "2026-09-01")
    csv = "cont;denumire;sold debitor;sold creditor\n1012;Capital;0;2500\n5311;Casa;500;0\n5121;Bancă;2000;0\n".encode()
    import json
    r = json.loads(uc_tenants.solduri_incarca(1, csv, "b.csv", {"uid": 7}).body)
    assert r["existenta"]["randuri"] == 2 and r["existenta"]["data_referinta"] == "2026-06-30"
    assert r["note_dupa"] == {"numar": 1, "prima": "2026-09-01"}
    # avertismentul previzualizării e EXACT textul comun cu refuzul de la salvare (`text_inlocuire`, al cărui conținut îl păzește
    # test_def_426 mai sus), pe balanța veche, pe totalurile fișierului nou (3 conturi, 2.500 / 2.500) și pe nota de după preluare
    assert r["avertisment_inlocuire"] == solduri_api.text_inlocuire(
        r["existenta"], {"randuri": 3, "total_debit": 2500, "total_credit": 2500}, {"numar": 1, "prima": "2026-09-01"}, "2026-06-30")
