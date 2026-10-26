# -*- coding: utf-8 -*-
"""[lotul 10, deficiența 425 — partea de EFECT] Balanța de deschidere cu soldurile inițiale ale anului și rulajele lui ajunge în balanță,
D101 (+ capital / rezerve), D100 pe profit, F20 / categoria de mărime, KPI / cash-flow, coeficientul K și controlul D101 ↔ 691.

Comanda Costin 10.1 (verbatim în DECIZII): „O balanță completă la 30.09.2026 (format SAGA: solduri inițiale an, rulaje precedente, rulaje
lună, total sume, solduri finale, antet pe două rânduri) e citită doar din «Solduri finale». Soldurile de la 1 ianuarie și rulajele
ianuarie–septembrie se pierd, iar conturile cu sold final 0 (707, 607, 641, 646, 6811, 4426, 4427) nu intră deloc. Cifra de afaceri a anului
(707 = 180.000 lei) și cheltuielile dispar, deci D101, bilanțul anual, plafonul de micro și controalele cumulate de TVA ies greșite pentru o
firmă preluată în cursul anului. Când fișierul are soldurile inițiale ale anului și rulajele, ele intră ca sold inițial și sume precedente,
cu toate conturile care au rulaj. Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului
lipsesc și ce afectează.”

Fixtura = balanța SAGA a unei firme care închide lunar 6 / 7 în 121 (soldul final 0 pe 707, 607, 641, 646, 6811, 4426, 4427), la 30.09.2026,
cu o notă validată în octombrie. Toate cifrele de mai jos se leagă: balanța de deschidere e echilibrată pe toate cele trei perechi.
"""
import datetime
import io
import os
import sys
from decimal import Decimal

import pytest
from psycopg2.extras import RealDictCursor

_RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _RAD not in sys.path:
    sys.path.insert(0, _RAD)

from core import db as _db  # noqa: E402
from core import tenant_provisioning as _tp  # noqa: E402

SCH = "ztest_lot10_rulaje"
REF = datetime.date(2026, 9, 30)

#: (cont, denumire, si_an D, si_an C, rulaj an D, rulaj an C) — soldul final se calculează (si + rulaje), ca în fișierul SAGA
BALANTA_SAGA = (
    ("1012", "Capital subscris vărsat", 0, 10000, 0, 0),
    ("117", "Rezultatul reportat", 0, 78000, 0, 0),
    ("121", "Profit sau pierdere", 0, 0, 136675, 180000),
    ("2131", "Echipamente tehnologice", 60000, 0, 0, 0),
    ("2813", "Amortizarea instalațiilor", 0, 12000, 0, 6000),
    ("371", "Mărfuri", 30000, 0, 100000, 100000),
    ("401", "Furnizori", 0, 0, 121000, 121000),
    ("4111", "Clienți", 0, 0, 217800, 217800),
    ("421", "Personal - salarii datorate", 0, 0, 30000, 30000),
    ("436", "Contribuția asiguratorie pentru muncă", 0, 0, 675, 675),
    ("4423", "TVA de plată", 0, 0, 16800, 16800),
    ("4426", "TVA deductibilă", 0, 0, 21000, 21000),
    ("4427", "TVA colectată", 0, 0, 37800, 37800),
    ("5121", "Conturi la bănci în lei", 10000, 0, 217800, 168475),
    ("607", "Cheltuieli privind mărfurile", 0, 0, 100000, 100000),
    ("641", "Cheltuieli cu salariile personalului", 0, 0, 30000, 30000),
    ("646", "Cheltuieli privind contribuția asiguratorie pentru muncă", 0, 0, 675, 675),
    ("6811", "Cheltuieli de exploatare privind amortizarea imobilizărilor", 0, 0, 6000, 6000),
    ("707", "Venituri din vânzarea mărfurilor", 0, 0, 180000, 180000),
)

#: notele validate din octombrie 2026 (după preluare)
NOTE_OCTOMBRIE = (("2026-10-15", "4111", "707", 10000), ("2026-10-15", "4111", "4427", 2100), ("2026-10-20", "607", "371", 6000),
                  ("2026-10-31", "641", "421", 3000))


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


def _creeaza(cu_rulaje=True, note=NOTE_OCTOMBRIE):
    sablon = io.open(os.path.join(_RAD, "tenant_template.sql"), encoding="utf-8").read()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(sablon, SCH))
            cur.execute(f"INSERT INTO {SCH}.firma_profil (id, nume, cui, adresa, oras, judet, caen, reg_com, platitor_tva, tip_decont, "
                        "regim_fiscal, declarant_nume, declarant_prenume, declarant_functie) VALUES (1, 'PROBA PRELUARE SRL', '14399840', "
                        "'Str. Exemplu 1', 'București', 'București', '4719', 'J40/1/2020', true, 'L', 'profit', 'Popescu', 'Ion', "
                        "'ADMINISTRATOR') ON CONFLICT (id) DO NOTHING")
            for cont, den, sid, sic, rd, rc in BALANTA_SAGA:
                net = Decimal(sid) - Decimal(sic) + Decimal(rd) - Decimal(rc)
                sfd, sfc = (net, 0) if net > 0 else (0, -net)
                cur.execute(f"INSERT INTO {SCH}.solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta, si_an_debit, "
                            "si_an_credit, rulaj_an_debit, rulaj_an_credit) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                            (cont, den, sfd, sfc, REF, *((sid, sic, rd, rc) if cu_rulaje else (None, None, None, None))))
            if not cu_rulaje:   # „Când are doar solduri finale”: conturile cu sold final 0 nu au rând (ca înainte de 425)
                cur.execute(f"DELETE FROM {SCH}.solduri_initiale WHERE sold_debitor = 0 AND sold_creditor = 0")
            for data, deb, cre, suma in note:
                cur.execute(f"INSERT INTO {SCH}.inregistrari (data, numar, descriere, status, sursa, document_ref) VALUES "
                            "(%s, 'L10', 'proba 425', 'validata', 'manual', 'NC L10') RETURNING id", (data,))
                cur.execute(f"INSERT INTO {SCH}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%s, %s, %s, %s)",
                            (cur.fetchone()[0], deb, cre, suma))
        conn.commit()


def _sterge():
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()


@pytest.fixture
def cu_rulaje():
    _creeaza(True)
    try:
        yield SCH
    finally:
        _sterge()


@pytest.fixture
def fara_rulaje():
    _creeaza(False)
    try:
        yield SCH
    finally:
        _sterge()


def test_fixtura_e_o_balanta_echilibrata():
    """Datele de probă se leagă: soldurile de la 1 ianuarie, rulajele și soldurile finale se închid (debit = credit)."""
    tot = [sum(Decimal(r[i]) for r in BALANTA_SAGA) for i in (2, 3, 4, 5)]
    assert tot[0] == tot[1] == Decimal(100000) and tot[2] == tot[3], tot


def _rand(randuri, cont):
    return next(r for r in randuri if r["cont"] == cont)


def test_balanta_10_2026_sold_initial_an_si_sume_precedente(cu_rulaje):
    """Balanța pe 10/2026: „ele intră ca sold inițial și sume precedente, cu toate conturile care au rulaj” (comanda 10.1). 707: sold
    inițial 0, sume precedente 180.000 / 180.000 (vânzarea și închiderea lunară), rulaj octombrie C 10.000, sold final C 10.000; 371: sold
    inițial D 30.000 (1 ianuarie, nu 30.09), sold final D 24.000 = 30.000 + 100.000 − 100.000 − 6.000. Cele cinci egalități (OMFP
    2634/2015 anexa 2: „soldurile inițiale debitoare și creditoare; totalul sumelor debitoare și creditoare ale lunii precedente [...];
    rulajele curente [...]; totalul sumelor [...]; soldurile finale”) se închid. MUTAȚIE: ramura `if p:` din `documente_api.balanta` scoasă
    -> sold inițial 371 = 30.000 (soldul final de la 30.09), 707 fără sume precedente -> pică."""
    from core import documente_api as da
    with _db.get_conn() as conn:
        rr = da.balanta(conn, SCH, 2026, 10)
        inch = da.inchidere_balanta(rr)
    r707, r371, r121 = _rand(rr, "707"), _rand(rr, "371"), _rand(rr, "121")
    assert (r707["si_d"], r707["si_c"], r707["prec_d"], r707["prec_c"], r707["rul_c"], r707["sf_c"]) == (0, 0, 180000, 180000, 10000, 10000)
    assert (r371["si_d"], r371["prec_d"], r371["prec_c"], r371["rul_c"], r371["sf_d"]) == (30000, 100000, 100000, 6000, 24000)
    assert (r121["prec_d"], r121["prec_c"], r121["sf_c"]) == (136675, 180000, 43325)
    for cont in ("607", "641", "646", "6811", "4426", "4427"):   # soldul final 0 la 30.09: au rând, cu rulajele lor
        assert _rand(rr, cont)["prec_d"] > 0, cont
    assert inch["stare"] == "se_inchide", inch                       # OMFP 2634/2015 anexa 2: cele cinci egalități
    tot = da.totaluri_balanta(rr)
    assert (tot["si_d"], tot["prec_d"], tot["sf_d"]) == (100000, 1216225, 164425), tot   # Σ rulajele preluate; SF + octombrie


def test_balanta_soldul_final_identic_cu_cel_fara_rulaje(cu_rulaje):
    """Soldurile finale nu se schimbă: sold de la 1 ianuarie + rulajele preluate = soldul final preluat (comanda: „comportamentul de acum”
    pe soldurile finale) — 5121: 10.000 + 217.800 − 168.475 = 59.325."""
    from core import documente_api as da
    with _db.get_conn() as conn:
        rr = da.balanta(conn, SCH, 2026, 10)
    assert _rand(rr, "5121")["sf_d"] == 59325 and _rand(rr, "2813")["sf_c"] == 18000


def test_balanta_anul_urmator_porneste_din_soldul_la_1_ianuarie(cu_rulaje):
    """Anul 2027: soldul inițial = soldul preluat + notele de după preluare (ca până acum), fără rulajele preluate în sume precedente."""
    from core import documente_api as da
    with _db.get_conn() as conn:
        rr = da.balanta(conn, SCH, 2027, 1)
    r371 = _rand(rr, "371")
    assert (r371["si_d"], r371["prec_d"], r371["prel_d"]) == (24000, 0, 0)
    assert _rand(rr, "707")["si_c"] == 10000


def test_kpi_venituri_cumulate_fara_inchiderea_in_121(cu_rulaje):
    """KPI pe 10/2026: venituri = 180.000 + 10.000 = 190.000, cheltuieli = 106.000 + 33.000 + 675 + 6.000 = 145.675. Închiderea lunară
    preluată (707 debit 180.000) nu e venit negativ — OMFP 1802/2014, contul 121: „În creditul contului 121 [...] se înregistrează: – la
    sfârșitul perioadei, soldul creditor al conturilor din clasa 7”. MUTAȚIE: `rulaje_cumulate` fără scăderea închiderii -> venituri 10.000
    -> pică."""
    from core import documente_api as da, kpi_client, cashflow
    with _db.get_conn() as conn:
        rr = da.balanta(conn, SCH, 2026, 10)
    k = kpi_client.kpi_din_balanta(rr)
    assert (k["venituri"], k["cheltuieli"], k["profit"]) == (190000, 145675, 44325), k
    # media lunară a cheltuielilor cash (cl.6 fără 68x și fără grupa 69), pe 10 luni: (106.000 + 33.000 + 675) / 10 — [lotul 13, 553]
    # salariile (641) intră: 421 / 431 din balanță acoperă numai luna trecută (înainte: fără 641, 10.667,5)
    assert cashflow.cheltuieli_lunare_cash(rr, 10) == 13967.5


def test_d101_2026_cuprinde_cifra_de_afaceri_preluata_si_e_valid_pe_duk(cu_rulaje):
    """D101 pe 2026: cifra de afaceri 180.000 (preluată) + 10.000 (octombrie) = 190.000 la rd.1, cheltuieli 145.675 la rd.2; capitalul
    1012 preluat (10.000) intră în baza rezervei legale (CF art.26 alin.(1) lit.a); reconcilierea a doua cale trece; XML valid pe DUK.
    MUTAȚIE: `_rp.rulaje` scos din `bilant_api.rulaje_67` -> P1 = 10.000 -> pică."""
    from core import d101, duk
    from core.common import Perioada
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        prof, r = d101.pull(conn, SCH, Perioada(2026))
        xml, res = d101.genereaza(conn, SCH, Perioada(2026))
        conn.rollback()
    assert (r["ven_expl"], r["cifra_afaceri"], r["chelt_expl"], r["capital"]) == (190000, 190000, 145675, 10000), r
    assert (res.P["P1"], res.P["P2"]) == (190000, 145675), res.P
    assert res.avertismente == [], res.avertismente     # cu rulajele anului preluate, nimic nu lipsește (nicio afirmație 425)
    v = duk.valideaza(xml, "d101", an=2026)
    assert v["stare"] in ("valid", "gri"), v
    if v["stare"] == "gri":
        pytest.skip("validatorul DUK D101 nu e instalat: %s" % v.get("limita"))


def test_d100_profit_fereastra_cumulata_cuprinde_rulajele_preluate(cu_rulaje):
    """D100 pe profit (cumulul 01.01 – sfârșitul trimestrului, CF art.41 alin.(1)): T3/2026 (până la 30.09) cuprinde rulajele preluate;
    T2 (până la 30.06) nu le poate folosi — un singur cumul, nu se împarte pe luni (regula ferestrei)."""
    from core import d101
    from core.d100 import _DeLaInceputulAnului
    with _db.get_conn(SCH) as conn:
        _p, r3 = d101.pull(conn, SCH, _DeLaInceputulAnului(2026, 3))
        _p, r2 = d101.pull(conn, SCH, _DeLaInceputulAnului(2026, 2))
    assert (r3["ven_expl"], r3["chelt_expl"]) == (180000, 136675), r3
    assert (r2["ven_expl"], r2["chelt_expl"]) == (0, 0), r2


def test_f20_si_categoria_de_marime_cuprind_rulajele_preluate(cu_rulaje):
    """Bilanțul F20 S1005 pe 2026: rd.01 cifra de afaceri netă = 190.000; rd.04 personal = 33.675; rd.05 amortizare = 6.000; rd.06 alte
    cheltuieli (607) = 106.000. Categoria de mărime citește aceeași cifră. MUTAȚIE: `fara_inchidere_121=False` în `rulaje_67` -> F20 rd.01
    tot 190.000 (latura C), dar rd.02 / rezultatul nu se schimbă — mutația care pică e scoaterea rulajelor preluate (rd.01 = 10.000)."""
    from core import bilant as b, bilant_api as ba, categorie_marime as cm
    with _db.get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            rl = ba._rulaje_67(cur, SCH, 2026)
        ind = cm.indicatori(conn, SCH, 2026)
    assert rl["707"] == (Decimal(0), Decimal(190000)), rl["707"]       # fără închiderea preluată pe debit
    f20 = b.f20_din_rulaje(rl)
    assert (f20[1], f20[4], f20[5], f20[6]) == (190000, 33675, 6000, 106000), f20
    assert ind["cifra_afaceri_neta"] == Decimal(190000), ind


def test_f20_an_precedent_din_rulajele_preluate():
    """Preluarea la 31.12.2025 cu rulajele lui 2025: coloana „An precedent” a bilanțului pe 2026 se ia din evidență (rulajele preluate),
    nu se mai cere completată manual — `bilant_api.rulaje_an_cunoscute`."""
    from core import bilant_api as ba
    _creeaza(True, note=())
    try:
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {SCH}.solduri_initiale SET data_referinta = '2025-12-31'")
            conn.commit()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                assert ba.rulaje_an_cunoscute(cur, SCH, datetime.date(2025, 12, 31), 2025)
                assert not ba.rulaje_an_cunoscute(cur, SCH, datetime.date(2025, 12, 31), 2024)
                assert ba._rulaje_67(cur, SCH, 2025)["707"] == (Decimal(0), Decimal(180000))
    finally:
        _sterge()


def test_control_d101_rd48_vs_691_cuprinde_691_preluat():
    """Controlul D101 rd.48 ↔ contul 691 pe an: impozitul înregistrat înainte de preluare (691 preluat, debit 5.000) intră în dreapta
    perechii — altfel un D101 corect apare „roșu” la o firmă preluată. MUTAȚIE: adunarea preluatului scoasă -> diferență 5.000 -> pică."""
    from core import control_incrucisat as ci
    rand = ("691", "Cheltuieli cu impozitul pe profit", 0, 0, 5000, 5000)
    global BALANTA_SAGA
    vechi = BALANTA_SAGA
    BALANTA_SAGA = vechi + (rand, ("4411", "Impozitul pe profit", 0, 0, 5000, 5000))
    try:
        _creeaza(True, note=())
        with _db.get_conn() as conn:
            r = ci._pereche_691(conn, SCH, 2026, Decimal(5000), 0)
        assert r and r[0]["stare"] == "verde" and r[0]["inregistrat_691"] == 5000, r
    finally:
        BALANTA_SAGA = vechi
        _sterge()


def test_fara_rulaje_comportamentul_ramane_si_avertismentul_spune_ce_lipseste(fara_rulaje):
    """„Când are doar solduri finale, comportamentul de acum rămâne, dar aplicația spune clar că rulajele anului lipsesc și ce afectează.”
    Balanța: sold inițial = soldul final de la 30.09 (371 D 30.000 −> rămâne cum era), D101 = numai octombrie; avertismentul (afirmație
    `necunoastere`, domeniul 01–09/2026) apare pe balanță, D101 și F20 și numește data. Pe 2027 nu mai apare. MUTAȚIE: `are_rulaje`
    întoarce mereu True -> fără avertisment -> pică."""
    from core import documente_api as da, d101, rulaje_preluate as rp, bilant_api as ba
    from core.common import Perioada
    with _db.get_conn(SCH) as conn:
        rr = da.balanta(conn, SCH, 2026, 10)
        av = da.avertisment_balanta(conn, SCH, 2026)
        _p, r = d101.pull(conn, SCH, Perioada(2026))
        with conn.cursor() as cur:
            cur.execute("SET LOCAL search_path TO %s, public" % SCH)
        _xml, res = d101.genereaza(conn, SCH, Perioada(2026))
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            av_f20 = ba.avertismente_rulaje(cur, SCH, 2026)
        with conn.cursor() as cur:
            av_2027 = rp.avertisment(cur, SCH, 2027, "balanta")
        conn.rollback()
    assert _rand(rr, "371")["si_d"] == 30000 and _rand(rr, "371")["prel_d"] == 0
    assert not any(x["cont"] == "707" and x["prec_c"] for x in rr)
    assert (r["ven_expl"], r["chelt_expl"]) == (10000, 9000), r
    assert av is not None, "balanța fără rulajele anului nu spune ce lipsește"
    assert av["fel"] == "necunoastere" and (av["domeniu_de"], av["domeniu_pana"]) == ("2026-01", "2026-09"), av
    # afirmația, pe locurile ei: intervalul lipsă (de la 1 ianuarie la data preluării) și efectul pe balanță (`EFECTE["balanta"]`)
    assert av["motiv"].partition(": ")[0] == "Rulajele de la 01.01.2026 până la 30.09.2026 lipsesc", av["motiv"]
    assert av["motiv"].partition("Pe 2026, ")[2].partition(". Importă")[0] == rp.EFECTE["balanta"], av["motiv"]
    # aceeași afirmație ajunge la D101 și la F20, fiecare cu efectul ei (o singură sursă a textului: `rulaje_preluate.avertisment`)
    assert av["motiv"].replace(rp.EFECTE["balanta"], rp.EFECTE["d101"]) in res.avertismente, res.avertismente
    assert av_f20 == [av["motiv"].replace(rp.EFECTE["balanta"], rp.EFECTE["bilant"])], av_f20
    assert av_2027 is None


def test_cu_rulaje_niciun_avertisment(cu_rulaje):
    from core import documente_api as da
    with _db.get_conn() as conn:
        assert da.avertisment_balanta(conn, SCH, 2026) is None


def test_fara_inchidere_pastreaza_latura_functiunii():
    """OMFP 1802/2014 pct.594 (funcțiunea contului, `plan_functiune`): 707 (P) -> creditul, 607 (A) -> debitul, 609 (P) -> creditul,
    709 (A) -> debitul; în afara claselor 6 / 7, nimic nu se taie."""
    from core.rulaje_preluate import fara_inchidere
    D = Decimal
    assert fara_inchidere("707", D(180000), D(180000)) == (0, D(180000))
    assert fara_inchidere("607", D(5), D(5)) == (D(5), 0)
    assert fara_inchidere("609", D(1), D(2)) == (0, D(2))
    assert fara_inchidere("709", D(1), D(2)) == (D(1), 0)
    assert fara_inchidere("4111", D(1), D(2)) == (D(1), D(2))


def test_fereastra_rulajelor_preluate(cu_rulaje):
    """Regula ferestrei: rulajele preluate [01.01, 30.09] intră numai într-o fereastră care le cuprinde întregi."""
    from core import rulaje_preluate as rp
    d = datetime.date
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            assert rp.rulaje(cur, SCH, d(2026, 1, 1), d(2027, 1, 1))["707"] == (Decimal(180000), Decimal(180000))
            assert rp.rulaje(cur, SCH, d(2026, 1, 1), d(2026, 10, 1))["707"] == (Decimal(180000), Decimal(180000))
            assert rp.rulaje(cur, SCH, d(2026, 1, 1), d(2026, 9, 30)) == {}            # se termină înainte de data preluării
            assert rp.rulaje(cur, SCH, d(2026, 2, 1), d(2027, 1, 1)) == {}            # începe după 1 ianuarie
            assert rp.sold_preluat(cur, SCH, "1012", d(2026, 1, 1)) == (0, Decimal(10000))
            assert rp.sold_preluat(cur, SCH, "371", d(2026, 1, 1)) == (Decimal(30000), 0)   # soldul de la 1 ianuarie
            assert rp.sold_preluat(cur, SCH, "5121", d(2027, 1, 1)) == (Decimal(59325), 0)  # soldul final de la 30.09


def test_k_global_valoric_din_soldul_de_la_1_ianuarie_si_intrarile_preluate():
    """Descărcarea global-valorică pe 10/2026: K = (sold inițial 378 + adaosul intrărilor cumulat de la începutul exercițiului) / (sold
    inițial 371 + intrările cumulate, fără TVA neexigibilă) — OMFP 1802/2014 pct.286 alin.(4) și nota *2). Cu balanța de la 30.09 cu rulaje:
    (10.000 + 45.000) / (50.000 + 200.000 − 8.000 − 32.000) = 55.000 / 210.000 = 0,261905; adaosul pe vânzarea din octombrie (20.000) =
    5.238,10. Înainte (soldul de la 30.09 + numai octombrie): 25.000 / 84.000 = 0,297619 -> 5.952,38. MUTAȚIE: ramura `if prel is not None`
    scoasă -> K 0,297619 -> pică."""
    from core import stocuri_api
    global BALANTA_SAGA
    vechi = BALANTA_SAGA
    BALANTA_SAGA = (("371", "Mărfuri", 50000, 0, 200000, 150000), ("378", "Diferențe de preț la mărfuri", 0, 10000, 30000, 45000),
                    ("4428.02", "TVA neexigibilă în stoc", 0, 8000, 24000, 32000))
    try:
        _creeaza(True, note=())
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {SCH}.firma_profil SET metoda_stoc = 'global_valoric'")
                cur.execute(f"INSERT INTO {SCH}.inregistrari (data, numar, descriere, status, sursa) VALUES ('2026-10-10', 'F1', 'vanzare', "
                            "'validata', 'facturi') RETURNING id")
                cur.execute(f"INSERT INTO {SCH}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s, '4111', '707', 20000)", (cur.fetchone()[0],))
            rez = stocuri_api.descarca_luna(conn, SCH, 2026, 10)
            conn.rollback()
        assert (rez.get("k"), rez.get("adaos")) == ("0.261905", "5238.10"), rez
    finally:
        BALANTA_SAGA = vechi
        _sterge()


def test_amortizarea_cumulata_cuprinde_soldul_preluat_al_contului_28x(schema):
    """Generalizarea pe clasă (cititor cumulat care ignora balanța de deschidere): perechea „amortizarea declarată de registru ↔ soldul
    creditor al contului 28xx la 31.12” (OMFP 1802/2014, grupa 28) adună și soldul PRELUAT. Activul R191 (6.000 lei, 60 de luni, PIF
    15.12.2025) are la 31.12.2026 amortizarea cumulată 1.200; preluarea la 30.09.2026 aduce 2813 C 900 (ianuarie–septembrie), iar notele
    din iConta.eu octombrie–decembrie 3 × 100 = 300 -> 1.200 = 1.200 -> verde. Înainte: 300 față de 1.200 -> „roșu, divergență certă”.
    MUTAȚIE: adunarea soldului preluat scoasă din `_amortizare_inregistrata` -> roșu -> pică."""
    from core import control_incrucisat as ci
    from core.test_r191_amortizare_confruntata import SCH as S191
    with schema.get_conn() as conn:
        with conn.cursor() as c:
            c.execute('INSERT INTO "%s".solduri_initiale (cont, sold_debitor, sold_creditor, data_referinta) VALUES '
                      "('2813', 0, 900, '2026-09-30'), ('2131', 6000, 0, '2026-09-30')" % S191)
            for luna in (10, 11, 12):
                c.execute('INSERT INTO "%s".inregistrari (data, descriere, status) VALUES (%%s, %%s, %%s) RETURNING id' % S191,
                          (datetime.date(2026, luna, 28), "amortizare", "validata"))
                c.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, 100)'
                          % S191, (c.fetchone()[0], "6811", "2813"))
        r = ci._pereche_amortizare(conn, S191, 2026)
        conn.rollback()
    assert [(x["stare"], x["declarat_registru"], x["inregistrat_contabil"]) for x in r] == [("verde", 1200, 1200)], r


from core.test_r191_amortizare_confruntata import schema  # noqa: E402,F401 — fixtura schemei R191 (registrul de imobilizări)


def test_k_in_anul_urmator_soldul_initial_cuprinde_notele_anilor_anteriori():
    """Aceeași normă (OMFP 1802/2014 pct.286 alin.(4): „Soldul inițial al stocurilor” = la începutul exercițiului), al doilea drum găsit la
    generalizare: firma fără balanță de deschidere, cu marfa intrată în 12/2025 (371 D 1.000, 378 C 200, 4428.02 C 160), vinde 500 în
    01/2026. Înainte: soldul inițial se lua numai din `solduri_initiale` (gol), deci K = 0 / 0 -> refuz „Nu se poate calcula
    coeficientul de adaos”. Acum: soldul inițial = notele anilor anteriori (ca balanța) -> K = 200 / (1.000 − 160) = 0,238095, adaos
    119,05. MUTAȚIE: termenii `_rulaj(..., inceput_an)` scoși din `si[cont]` -> refuz -> pică."""
    from core import stocuri_api
    global BALANTA_SAGA
    vechi = BALANTA_SAGA
    BALANTA_SAGA = ()
    try:
        _creeaza(True, note=(("2025-12-10", "371", "401", 1000), ("2025-12-10", "401", "378", 200), ("2025-12-10", "401", "4428.02", 160)))
        with _db.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(f"UPDATE {SCH}.firma_profil SET metoda_stoc = 'global_valoric'")
                cur.execute(f"INSERT INTO {SCH}.inregistrari (data, numar, descriere, status, sursa) VALUES ('2026-01-15', 'F1', 'vanzare', "
                            "'validata', 'facturi') RETURNING id")
                cur.execute(f"INSERT INTO {SCH}.inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) "
                            "VALUES (%s, '4111', '707', 500)", (cur.fetchone()[0],))
            rez = stocuri_api.descarca_luna(conn, SCH, 2026, 1)
            conn.rollback()
        assert (rez.get("k"), rez.get("adaos")) == ("0.238095", "119.05"), rez
    finally:
        BALANTA_SAGA = vechi
        _sterge()


def test_avertismentul_porneste_de_la_infiintare(fara_rulaje):
    """Firma înființată în anul preluării nu are rulaje dinainte de înființare — Legea 82/1991 art.27 alin.(8): „Exercițiul financiar al
    unităților nou-înființate începe la data înființării, potrivit legii.” Înființată 15.03.2026: lipsesc 15.03.2026 – 30.09.2026;
    înființată după data soldurilor de preluare: nimic nu lipsește, fără avertisment. MUTAȚIE: `max(..., infiintare)` scos -> textul
    pornește de la 01.01.2026 -> pică."""
    from core import documente_api as da
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {SCH}.firma_profil SET data_infiintare = '2026-03-15'")
        av = da.avertisment_balanta(conn, SCH, 2026)
        with conn.cursor() as cur:
            cur.execute(f"UPDATE {SCH}.firma_profil SET data_infiintare = '2026-10-01'")
        av_dupa = da.avertisment_balanta(conn, SCH, 2026)
        conn.rollback()
    assert av and av["motiv"].startswith("Rulajele de la 15.03.2026 până la 30.09.2026 lipsesc"), av
    assert av_dupa is None
