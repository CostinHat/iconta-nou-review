# -*- coding: utf-8 -*-
"""GARD amortizare pe METODA (Q6+Q15, tura import 16.08.2026).

DEFECT reparat: ecranul /mijloace-fixe (main.tenant_mijloace_fixe) + notele de amortizare
lunara / casare / reevaluare calculau MEREU liniar, ignorand `metoda` din activ, si afisau
cifra ca "amortizat la zi". Motorul cu cele patru metode (core/d406_active.py, CF art.28)
exista dar NU era chemat. Acum toate patru consuma motorul unic prin doua functii noi:
  - amortizat_la_data(mf, la_data): cumulat 'la zi' pe metoda (ecran/casare/reevaluare);
  - amortizare_luna(mf, an, luna): rata unei luni pe metoda (nota lunara).

Probele:
(a) PUR: amortizat_la_data e coerent cu calc_asset la granita de an, si DIFERA de liniar
    la mijloc de an pe un activ degresiv/accelerat (metoda chiar conteaza);
(b) PUR: amortizare_luna insumat pe toata durata = valoarea amortizabila EXACT (nu se
    amortizeaza mai mult/putin decat costul), pe fiecare metoda si durata;
(c) DB/ENDPOINT: ecranul real, pe un activ degresiv, intoarce amortizatul DEGRESIV (== motor),
    NU liniarul. Pe codul vechi (liniar hardcodat) aserta (c) PICA -> gardul e RED-provabil.
(d) DB/ENDPOINT: un activ cu metoda nepermisa pe categorie (constructii + degresiva) NU se
    calculeaza liniar tacit -> randul poarta eroare, amortizat/ramas None (DS cap.17)."""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import pytest

import core.d406_active as _d406
from core import db as _db, tenant_provisioning as _tp
import main

SCH = "ztest_amort_ecran"


def _mf(metoda, cont="2131", val=100000, rez=0, dnf=60, pif=date(2025, 12, 20)):
    return {"cod": "MF-%s" % metoda[:3].upper(), "denumire": "Test %s" % metoda,
            "cont_imobilizare": cont, "cont_amortizare": "2813", "valoare": val,
            "rezidual": rez, "dnf_luni": dnf, "data_pif": pif, "metoda": metoda, "activ": True}


def _liniar_la_data(val, rez, dnf, pif, la_data):
    luni = max(0, min(dnf, (la_data.year - pif.year) * 12 + (la_data.month - pif.month)))
    rata = (Decimal(val) - Decimal(rez)) / dnf
    return (rata * luni).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------- (a) PUR: coerenta la granita + metoda conteaza ----------
@pytest.mark.parametrize("metoda", ["liniara", "degresiva", "accelerata"])
def test_amortizat_la_data_coerent_cu_calc_asset(metoda):
    mf = _mf(metoda)
    for an in (2026, 2027, 2028):
        ca = _d406.calc_asset(mf, an)
        ld = _d406.amortizat_la_data(mf, date(an, 12, 31))
        assert ld["amortizat"] == ca["accum_depr"], "%s %d amortizat" % (metoda, an)
        assert ld["ramas"] == ca["book_end"], "%s %d ramas" % (metoda, an)


def test_amortizat_la_data_difera_de_liniar_pe_neliniar():
    azi = date(2026, 8, 16)
    lin = _d406.amortizat_la_data(_mf("liniara"), azi)["amortizat"]
    deg = _d406.amortizat_la_data(_mf("degresiva"), azi)["amortizat"]
    acc = _d406.amortizat_la_data(_mf("accelerata"), azi)["amortizat"]
    assert deg != lin and acc != lin, (lin, deg, acc)   # daca ecranul ar fi liniar, ar fi egale
    assert deg > lin and acc > lin                       # metode accelerate -> mai mult in fata


# ---------- (b) PUR: suma lunilor = amortizabil exact ----------
@pytest.mark.parametrize("metoda", ["liniara", "degresiva", "accelerata"])
@pytest.mark.parametrize("dnf", [24, 60, 120])
def test_amortizare_luna_insumata_egal_amortizabil(metoda, dnf):
    mf = _mf(metoda, dnf=dnf)
    total = Decimal("0")
    for k in range(1, dnf + 1):
        mo = 12 + k
        y = 2025 + (mo - 1) // 12
        mo = (mo - 1) % 12 + 1
        total += _d406.amortizare_luna(mf, y, mo)
    assert total == Decimal("100000.00"), "%s dnf=%d -> %s" % (metoda, dnf, total)


# ---------- DB fixtures ----------
def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


def _seed(metoda, cont):
    _db.init_pool()
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
            cur.execute(_tp.parametrizeaza_template(
                open("tenant_template.sql", encoding="utf-8").read(), SCH))
            cur.execute('SET search_path TO "%s", public' % SCH)
            cur.execute("""INSERT INTO mijloace_fixe
                (cod,denumire,cont_imobilizare,cont_amortizare,valoare,rezidual,dnf_luni,
                 data_pif,metoda,activ)
                VALUES ('MF-1','Strung CNC',%s,'2813',100000,0,60,'2025-12-20',%s,true)""",
                        (cont, metoda))
        conn.commit()


def _drop():
    with _db.get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % SCH)
        conn.commit()


# ---------- (c) ENDPOINT: ecranul aplica metoda reala ----------
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ecran_mf_intoarce_amortizat_degresiv_nu_liniar(monkeypatch):
    _seed("degresiva", "2131")   # echipament -> degresiva legala
    try:
        monkeypatch.setattr(main, "_schema_sau_404", lambda ctx, tid: SCH)
        res = main.tenant_mijloace_fixe(1, ctx={"uid": 1})
        row = res["mijloace"][0]
        azi = date.today()
        deg = _d406.amortizat_la_data(_mf("degresiva"), azi)["amortizat"]
        lin = _liniar_la_data(100000, 0, 60, date(2025, 12, 20), azi)
        assert row["eroare"] is None, row
        assert row["amortizat"] == str(deg)          # == motor degresiv
        assert row["amortizat"] != str(lin)          # RED pe codul vechi (liniar hardcodat)
        assert row["ramas"] == str((Decimal("100000") - deg).quantize(Decimal("0.01")))
    finally:
        _drop()


# ---------- (d) ENDPOINT: metoda nepermisa -> eroare pe rand, nu liniar tacit ----------
@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_ecran_mf_metoda_nepermisa_da_eroare_nu_liniar(monkeypatch):
    _seed("degresiva", "212")   # constructii -> doar liniara permisa (alin.5 lit.a)
    try:
        monkeypatch.setattr(main, "_schema_sau_404", lambda ctx, tid: SCH)
        res = main.tenant_mijloace_fixe(1, ctx={"uid": 1})
        row = res["mijloace"][0]
        assert row["amortizat"] is None and row["ramas"] is None   # nu fabrica liniar
        assert row["eroare"] and "nu e permisa" in row["eroare"]    # spune care e problema
    finally:
        _drop()
