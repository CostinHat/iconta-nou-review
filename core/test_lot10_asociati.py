# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 431, comanda Costin 10.1] Asociații și cotele, cu istoricul cesiunilor, în Date firmă. Verbatim: „Fluxul e unul
singur: asociații și cotele (cu istoricul cesiunilor) în datele firmei; nota de dividende împarte automat pe asociați; D205 preia din
notele validate; mesajul de refuz trimite la ce lipsește.”

Ce garantează, pentru nota de dividende și D205: suma cotelor = 100% (refuz numit altfel), CNP / CUI cu cifra de control, istoricul
fără goluri (fiecare structură are intervalul ei, una după alta), structura la o dată. Pe bază: schemă efemeră, în ROLLBACK; use-case-ul
(cu tranzacția lui) pe o schemă creată și ștearsă la final.
"""
import datetime as dt
import io
import os
import uuid
from decimal import Decimal

import pytest

from core import asociati_api as A
from core import asociati_import_api as I

RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = dt.date


def _cnp(baza12):
    """CNP valid din primele 12 cifre (algoritmul din CLAUDE.md, cheia 279146358279)."""
    ch = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
    c = sum(int(baza12[i]) * ch[i] for i in range(12)) % 11
    return baza12 + str(1 if c == 10 else c)


CNP_A = _cnp("180010141001")   # 1 800101 41 001x — București sector 1 (41), 01.01.1980
CNP_B = _cnp("285020241002")   # 2 850202 41 002x
CNP_C = _cnp("190030341003")


def test_cnp_urile_de_test_trec_cifra_de_control():
    from core.identitate import valideaza_cnp
    for c in (CNP_A, CNP_B, CNP_C):
        assert valideaza_cnp(c) == (True, "ok"), c


# ── pure ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_randurile_ecranului_cota_goala_nu_devine_zero():
    r = A.randuri_din_corp([{"nume": " Ion ", "cnp": "ro 14399840", "cota": "33,5"}, {"nume": "Ana", "cnp": CNP_B, "cota": ""},
                            {"nume": "X", "cnp": CNP_C, "cota": "abc"}])
    assert r[0] == {"nume": "Ion", "cnp": "14399840", "cota": 33.5, "rand_fisier": 1}
    assert r[1]["cota"] is None and r[2]["cota"] == "abc"
    assert A.erori_cota_lipsa(r) == [{"camp": "as-2-cota", "mesaj": "Ana: scrie cota de participare (procent din capitalul social)."}]


def test_suma_cotelor_100_refuz_numit_pe_campul_totalului():
    r = A.randuri_din_corp([{"nume": "Ion", "cnp": CNP_A, "cota": "60"}, {"nume": "Ana", "cnp": CNP_B, "cota": "30"}])
    er = A.erori_pe_campuri(I.verifica_randuri(r))
    # INTERPRETARE CU TEMEI: Legea 31/1990 art.11 alin.(1) „Capitalul social al unei societăți cu răspundere limitată se divide în părți
    # sociale egale”, iar art.7 lit.d) cere „numărul părților sociale atribuite fiecărui asociat” — tot capitalul e atribuit: suma = 100%
    assert er == [{"camp": "as-total", "mesaj": "cotele asociaților care intră însumează 90%, nu 100%"}], er


def test_cnp_invalid_si_dublura_pe_campul_randului():
    rau = CNP_A[:-1] + str((int(CNP_A[-1]) + 1) % 10)
    r = A.randuri_din_corp([{"nume": "Ion", "cnp": rau, "cota": "50"}, {"nume": "Ana", "cnp": CNP_B, "cota": "25"},
                            {"nume": "Ana 2", "cnp": CNP_B, "cota": "25"}])
    er = A.erori_pe_campuri(I.verifica_randuri(r))
    campuri = [e["camp"] for e in er]
    # cifra de control (CLAUDE.md, cheia 279146358279) pe rândul 1; un asociat o dată (rândul 3); fără ei, intră numai 25% (as-total)
    assert campuri == ["as-1-cnp", "as-3-cnp", "as-total"], er


# ── pe bază ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


SCH = "ztest_lot10_asoc"


def _template(c, sch):
    from core import tenant_provisioning as _tp
    c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
    c.execute(_tp.parametrizeaza_template(io.open(os.path.join(RAD, "tenant_template.sql"), encoding="utf-8").read(), sch))


@pytest.fixture
def cur():
    from core import db
    db.init_pool()
    with db.get_conn() as conn:
        try:
            with conn.cursor() as c:
                _template(c, SCH)
                c.execute("SET LOCAL search_path TO %s, public" % SCH)
                yield c
        finally:
            conn.rollback()


def _r(*x):
    return A.randuri_din_corp([{"nume": n, "cnp": c, "cota": q} for n, c, q in x])


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cesiunea_pastreaza_structura_veche_si_istoricul_n_are_goluri(cur):
    conn = cur.connection
    I.importa(conn, _r(("Ion", CNP_A, "60"), ("Ana", CNP_B, "40")))
    I.importa(conn, _r(("Ion", CNP_A, "50"), ("Ana", CNP_B, "50")), data_cesiune="2025-07-01")
    I.importa(conn, _r(("Ion", CNP_A, "50"), ("Vlad", CNP_C, "50")), data_cesiune="2026-02-01")
    c = A.citeste(cur)
    assert [(x["nume"], x["cota"]) for x in c["asociati"]] == [("Ion", "50"), ("Vlad", "50")] and c["total_cota"] == "100"
    assert c["valabila_de_la"] == "2026-02-01"
    # „fără goluri”: fiecare structură începe a doua zi după precedenta (Legea 31/1990 art.67 alin.(6): „Dividendele care se cuvin
    # după data transmiterii acțiunilor aparțin cesionarului”)
    assert [(s["de_la"], s["pana_la"]) for s in c["istoric"]] == [("2025-07-01", "2026-01-31"), (None, "2025-06-30")]
    # structura la o dată (pentru nota de dividende / D205; Legea 31/1990 art.67 alin.(2): „proporțional cu cota de participare”)
    la = lambda d: sorted((n, q) for _c, n, q in A.structura_la(cur, d))
    assert la("2025-06-30") == [("Ana", Decimal("40")), ("Ion", Decimal("60"))]
    assert la(D(2025, 7, 1)) == [("Ana", Decimal("50")), ("Ion", Decimal("50"))]
    assert la("2026-02-01") == [("Ion", Decimal("50")), ("Vlad", Decimal("50"))]


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_cesiunea_fara_structura_de_dinainte_e_refuzata(cur):
    with pytest.raises(ValueError) as e:
        I.importa(cur.connection, _r(("Ion", CNP_A, "100")), data_cesiune="2026-01-01")
    # garanția „fără goluri”: perioada de dinaintea cesiunii n-ar avea asociați
    assert str(e.value).startswith("firma n-are înregistrată structura asociaților de dinaintea cesiunii"), str(e.value)
    cur.execute("SELECT count(*) FROM asociati_istoric")
    assert cur.fetchone()[0] == 0


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_use_case_refuza_pe_campuri_nu_scrie_nimic_si_jurnalizeaza_ce_scrie(monkeypatch):
    """Use-case-ul (tranzacția lui): refuzul 100% / cota lipsă nu scrie; corectura și cesiunea intră, cu jurnalul Date firmă."""
    from core import db, erori, uc_asociati as U, uc_comun
    sch = "ztest_lot10_asoc_uc_%s" % uuid.uuid4().hex[:8]
    db.init_pool()
    with db.get_conn() as conn, conn.cursor() as c:
        _template(c, sch)
    try:
        monkeypatch.setattr(uc_comun, "_schema_sau_404", lambda ctx, tid: sch)
        monkeypatch.setattr(I, "verificare_anaf", lambda randuri: {})
        ctx = {"uid": 77}
        with pytest.raises(erori.DateInvalide) as e:
            U.asociati_salveaza(1, {"randuri": [{"nume": "Ion", "cnp": CNP_A, "cota": "60"}, {"nume": "Ana", "cnp": CNP_B, "cota": ""}]}, ctx)
        assert e.value.args[0]["erori_campuri"] == [{"camp": "as-2-cota",
                                                     "mesaj": "Ana: scrie cota de participare (procent din capitalul social)."}]
        with pytest.raises(erori.DateInvalide) as e:
            U.asociati_salveaza(1, {"randuri": [{"nume": "Ion", "cnp": CNP_A, "cota": "60"}, {"nume": "Ana", "cnp": CNP_B, "cota": "30"}]}, ctx)
        assert e.value.args[0]["erori_campuri"][0]["camp"] == "as-total"
        r = U.asociati_salveaza(1, {"randuri": [{"nume": "Ion", "cnp": CNP_A, "cota": "60"}, {"nume": "Ana", "cnp": CNP_B, "cota": "40"}]}, ctx)
        assert r["ok"] and r["total_cota"] == "100" and r["istoric"] == [], r
        with pytest.raises(erori.DateInvalide) as e:
            U.asociati_cesiune(1, {"randuri": [{"nume": "Ion", "cnp": CNP_A, "cota": "100"}]}, ctx)
        assert e.value.args[0]["erori_campuri"][0]["camp"] == "as-data-cesiune"     # cesiunea are o dată (Legea 31/1990 art.67 alin.(6))
        r = U.asociati_cesiune(1, {"data_cesiune": "2026-03-01", "randuri": [{"nume": "Ion", "cnp": CNP_A, "cota": "100"}]}, ctx)
        assert r["ok"] and r["arhivati"] == 2 and r["istoric"][0]["pana_la"] == "2026-02-28", r
        with db.get_conn(sch) as conn, conn.cursor() as c:
            c.execute("SELECT camp, valoare_veche, valoare_noua, user_id FROM firma_profil_jurnal ORDER BY id")
            j = c.fetchall()
        # comanda Costin 06.10.2026 §6.4: „Orice modificare se jurnalizează (cine, când, valoare veche → nouă)”
        assert j == [("asociati", None, "Ion 60%; Ana 40%", 77),
                     ("asociati", "Ion 60%; Ana 40%", "Ion 100% (cesiune de la 01.03.2026)", 77)], j
    finally:
        with db.get_conn() as conn, conn.cursor() as c:
            c.execute("DROP SCHEMA IF EXISTS %s CASCADE" % sch)
