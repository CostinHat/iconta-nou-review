# -*- coding: utf-8 -*-
"""Lotul 11 (comanda Costin 11.1 pct.1, decizia din 10.3 verbatim în DECIZII „Comanda 10.3”): „Cursul BNR: aplici textul legal în
vigoare (CF art. 290, HG 1/2016 pct. 35), verificat verbatim.”

Textul, verbatim (formele consolidate din `anaf_surse/`, descărcate de pe legislatie.just.ro):
  CF art.290 alin.(2): „Dacă elementele folosite pentru stabilirea bazei de impozitare a unei operațiuni, alta decât importul de bunuri,
  se exprimă în valută, cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...] valabil
  la data la care intervine exigibilitatea taxei pentru operațiunea în cauză”.
  HG 1/2016 pct.35 alin.(1): „În sensul art. 290 alin. (2) din Codul fiscal, prin ultimul curs de schimb comunicat de Banca Națională a
  României se înțelege cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este valabil pentru operațiunile care se
  vor desfășura în ziua următoare.”
  OMFP 1802/2014 pct.325 alin.(2) lit.b (reevaluarea lunară, altă regulă): „cursul de schimb al pieței valutare comunicat de Banca
  Națională a României, din ultima zi bancară a lunii în cauză, pentru evaluarea creanțelor și datoriilor în valută, a disponibilităților
  în valută [...] existente în sold la sfârșitul lunii.”; lit.a: „pentru contabilizarea tranzacțiilor efectuate în ultima zi a lunii,
  cursul de schimb al pieței valutare, comunicat de Banca Națională a României, din ultima zi bancară anterioară operațiunii”.

Deci: operațiunea din ziua Z ia cursul comunicat ÎNAINTEA zilei Z (data cubului BNR < Z); reevaluarea de la sfârșitul lunii ia cursul
comunicat în ultima zi bancară a lunii (data cubului <= ultima zi). Codul de dinainte dădea operațiunii cursul comunicat chiar în ziua ei
(data cubului <= Z) — pe producție, F1A8 din 19.10.2026 poartă cursul comunicat pe 19.10 (5,3272), nu pe cel de vineri 16.10 (5,3368).
Cursurile de test sunt pe zile SINTETICE 2099 (tabelul `public.curs_bnr_zilnic` e partajat: scrise în tranzacție, anulate la final).
"""
import datetime as _dt
from decimal import Decimal as D

import pytest

from core import curs_bnr as cb

HARTA = {_dt.date(2099, 9, 9): {"EUR": D("4.9000")}, _dt.date(2099, 9, 10): {"EUR": D("4.9500")},
         _dt.date(2099, 9, 30): {"EUR": D("5.0000")}}


def test_operatiunea_ia_cursul_comunicat_in_ziua_anterioara():
    # HG 1/2016 pct.35 alin.(1): „cursul de schimb comunicat de respectiva bancă în ziua anterioară și care este valabil pentru
    # operațiunile care se vor desfășura în ziua următoare” — factura din 10.09 ia cursul comunicat pe 09.09, nu pe cel din 10.09
    assert cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 10)) == (D("4.9000"), _dt.date(2099, 9, 9))
    # o zi fără comunicare (sâmbătă 12.09.2099 nu e în hartă) ia ultimul curs comunicat înaintea ei — al zilei de 10.09
    assert cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 12)) == (D("4.9500"), _dt.date(2099, 9, 10))
    # niciun curs comunicat înaintea zilei: nimic, nu cursul zilei
    assert cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 9)) == (None, None)


def test_reevaluarea_ia_cursul_comunicat_in_ultima_zi_bancara_a_lunii():
    # OMFP 1802/2014 pct.325 alin.(2) lit.b: „comunicat de Banca Națională a României, din ultima zi bancară a lunii în cauză”
    assert cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 30), regula=cb.REGULA_SFARSIT_LUNA) == (D("5.0000"), _dt.date(2099, 9, 30))
    # aceeași zi, ca operațiune (pct.325 alin.(2) lit.a: „din ultima zi bancară anterioară operațiunii”): cursul din 10.09
    assert cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 30)) == (D("4.9500"), _dt.date(2099, 9, 10))


def test_regula_necunoscuta_e_refuzata():
    with pytest.raises(ValueError):
        cb.curs_din_harta(HARTA, "EUR", _dt.date(2099, 9, 30), regula="cursul_zilei")


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_curs_pentru_pe_cache_aplica_aceeasi_regula():
    """`curs_pentru` (emiterea, factura primită, decontarea, previzualizarea din formular) decide pe cache cu aceeași regulă ca harta;
    `curs_sfarsit_luna` (reevaluarea) cu regula pct.325. Tranzacție anulată: cache-ul partajat nu păstrează zilele 2099."""
    from core import db
    with db.get_conn() as conn:
        try:
            with conn.cursor() as cur:
                for zi, m in HARTA.items():
                    cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES (%s, 'EUR', %s) "
                                "ON CONFLICT (data, moneda) DO UPDATE SET curs = EXCLUDED.curs", (zi, m["EUR"]))
            # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): factura din 10.09 -> cursul comunicat pe 09.09
            assert cb.curs_pentru(conn, "EUR", _dt.date(2099, 9, 10)) == (D("4.9000"), _dt.date(2099, 9, 9), "bnr")
            # OMFP 1802/2014 pct.325 alin.(2) lit.b: reevaluarea la 30.09 -> cursul comunicat pe 30.09
            assert cb.curs_sfarsit_luna(conn, "EUR", _dt.date(2099, 9, 30)) == (D("5.0000"), _dt.date(2099, 9, 30), "bnr")
            assert cb.curs_pentru(conn, "RON", _dt.date(2099, 9, 10)) == (D("1"), _dt.date(2099, 9, 10), "ron")
        finally:
            conn.rollback()


def test_garda_un_singur_loc_alege_cursul():
    """Gardă: nicio interogare a cache-ului de cursuri în afara `curs_bnr.py` / `uc_curs_bnr.py` (scrierea) — orice alt drum care și-ar
    alege singur cursul („data <= ziua”) ar ocoli regula. MUTAȚIE: o citire `FROM public.curs_bnr_zilnic` într-un modul din `core/`."""
    import os
    import re
    rad = os.path.dirname(os.path.abspath(__file__))
    voie = {"curs_bnr.py", "uc_curs_bnr.py"}
    gasite = []
    for f in sorted(os.listdir(rad)):
        if not f.endswith(".py") or f.startswith(("test_", "migrare_")) or f in voie:
            continue
        txt = open(os.path.join(rad, f), encoding="utf-8").read()
        if re.search(r"FROM\s+public\.curs_bnr_zilnic", txt):
            gasite.append(f)
    principal = open(os.path.join(os.path.dirname(rad), "main.py"), encoding="utf-8").read()
    if re.search(r"FROM\s+public\.curs_bnr_zilnic", principal):
        gasite.append("main.py")
    assert gasite == [], "cursul BNR ales în afara `curs_bnr`: %s" % gasite
