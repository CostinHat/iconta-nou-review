# -*- coding: utf-8 -*-
"""[lotul 13, deficiența 670, comanda Costin 13.1] Decontul de deplasare / diurna (Operațiuni → Personal și deconturi).

Proba lui Costin, pe care s-a văzut defectul: decont final, Casa, avans 1.000, diurnă 300, transport 200, cazare 400, cota 21 ->
625 = 542 900; 4426 = 542 126; 542 = 5311 26. Cinci lipsuri: (a) fără salariat (542 neurmărit pe persoană); (b) diurna fără zile și fără
deplasare internă/externă, deci plafonul neimpozabil nu se verifică; (c) o singură cotă pentru tot (cazarea are cota redusă: 86 lei în loc
de 126); (d) cota precompletată, transportul și cazarea obligatorii; (e) confirmarea de trei ori.

TEMEI (anaf_surse/cod_fiscal_227_2015_consolidat.txt):
  CF art.76 alin.(2) lit.k: „… pentru partea care depășește plafonul neimpozabil stabilit astfel: (i) în țară, 2,5 ori nivelul legal stabilit
  pentru indemnizație, prin hotărâre a Guvernului, pentru personalul autorităților și instituțiilor publice, în limita a 3 salarii de bază
  corespunzătoare locului de muncă ocupat; (ii) în străinătate, 2,5 ori nivelul legal stabilit pentru diurnă […]”.
  Ordinul MF 1235/2023 (MO 261/29.03.2023) art.1: „Începând cu data de 1 aprilie 2023: […] se majorează la 23 lei” (indemnizația de
  delegare din HG 714/2018) -> plafonul în țară 57,50 lei/zi.
  CF art.291 alin.(2) lit.m: cota redusă de 11% se aplică „cazarea în cadrul sectorului hotelier sau al sectoarelor cu funcție similară”.
"""
import sys
import types
from decimal import Decimal

import pytest

from core import deconturi
from core.test_lot13_ops_schema import CTX, linii, nota, salariat, schema_ops


@pytest.fixture
def excedente(monkeypatch):
    """`core.diurna_salariat` e modulul salarizării (subagentul SAL): aici se înregistrează ce i se trimite."""
    trimise = []
    mod = types.ModuleType("core.diurna_salariat")
    mod.adauga_excedent = lambda cur, schema, sid, an, luna, suma, referinta, descriere: trimise.append(
        (sid, an, luna, Decimal(str(suma)), referinta, descriere)) or 1
    mod.sterge_excedent = lambda cur, schema, referinta: None
    monkeypatch.setitem(sys.modules, "core.diurna_salariat", mod)
    import core
    monkeypatch.setattr(core, "diurna_salariat", mod, raising=False)
    return trimise


def test_def_670_c_fiecare_cheltuiala_cu_cota_ei():
    # CF art.291 alin.(1) 21% transportul, alin.(2) lit.m 11% cazarea: 200 x 21% = 42 + 400 x 11% = 44 -> 86 (nu 126)
    r = deconturi.nota_decont(1000, diurna=300, transport=200, cazare=400, cota_transport=21, cota_cazare=11)
    assert r["linii"] == [("625", "542", Decimal("900.00")), ("4426", "542", Decimal("86.00")), ("5311", "542", Decimal("14.00"))]
    assert (r["tva_transport"], r["tva_cazare"]) == (Decimal("42.00"), Decimal("44.00"))


def test_def_670_d_transportul_si_cazarea_pot_lipsi_fara_cota():
    r = deconturi.nota_decont(0, diurna=300, sursa="banca")
    assert r["linii"] == [("625", "542", Decimal("300.00")), ("542", "5121", Decimal("300.00"))]
    with pytest.raises(ValueError, match="cota de TVA a cazării"):
        deconturi.nota_decont(0, diurna=0, cazare=400, cota_transport=21)


def _decont(uc, sid, **extra):
    corp = {"data": "2026-10-15", "fel": "decont", "salariat_id": sid, "sursa": "casa", "avans": 1000, "diurna": 300,
            "deplasare": "interna", "zile": 3, "transport": 200, "cota_transport": 21, "cazare": 400, "cota_cazare": 11}
    corp.update(extra)
    return uc.nota_decont_deplasare(1, corp, CTX)


def test_def_670_proba_lui_costin_pe_persoana_cu_plafon_si_cote(monkeypatch, excedente):
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur, salariu=6000)
        cur.execute("SELECT cnp FROM salariati WHERE id = %s", (sid,))
        cnp = cur.fetchone()[0]
        nota(cur, "2026-10-10", [("542", "5311", 1000)], partener=(cnp, "Ionescu Vasile"))   # avansul, validat
        r = _decont(uc, sid)
        assert linii(cur, r["inregistrare_id"]) == [("625", "542", "900.00", "Ionescu Vasile"), ("4426", "542", "86.00", "Ionescu Vasile"),
                                                    ("5311", "542", "14.00", "Ionescu Vasile")]
        cur.execute("SELECT partener_cui FROM inregistrari_linii WHERE inregistrare_id = %s", (r["inregistrare_id"],))
        assert {x[0] for x in cur.fetchall()} == {cnp}                     # 542 urmărit pe persoană (CNP-ul salariatului)
        # plafonul în țară: 2,5 x 23 = 57,50 lei/zi (3 x 6.000 / 22 zile lucrătoare în 10/2026 = 818,18 nu limitează) -> 172,50 neimpozabil
        assert (r["diurna"]["plafon_zi"], r["diurna"]["neimpozabil"], r["diurna"]["impozabil"]) == ("57.50", "172.50", "127.50")
        # excedentul (CF art.76 alin.(2) lit.k) pleacă spre statul de plată al lunii decontului, legat de notă
        assert excedente == [(sid, 2026, 10, Decimal("127.50"), "decont-deplasare:%d" % r["inregistrare_id"],
                              "Diurnă peste plafonul neimpozabil, Ionescu Vasile (în țară, 3 zile)")]


def test_def_670_b_sub_plafon_nimic_in_stat(monkeypatch, excedente):
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur)
        r = _decont(uc, sid, avans=0, diurna=150, transport=0, cazare=0)
        assert r["diurna"]["impozabil"] == "0.00" and excedente == []


def test_def_670_a_salariatul_e_cerut(monkeypatch, excedente):
    from core import erori
    with schema_ops(monkeypatch) as (c, cur, uc):
        with pytest.raises(erori.DateInvalide) as e:
            _decont(uc, None)
        assert e.value.detaliu["erori_campuri"][0]["camp"] == "op-salariat_id"


def test_def_670_d_cota_ceruta_numai_pentru_cheltuiala_care_exista(monkeypatch, excedente):
    from core import erori
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur)
        with pytest.raises(erori.DateInvalide) as e:
            _decont(uc, sid, avans=0, cota_transport=None, cota_cazare="")
        assert [x["camp"] for x in e.value.detaliu["erori_campuri"]] == ["op-cota_transport", "op-cota_cazare"]
        r = _decont(uc, sid, avans=0, transport=0, cazare=0, cota_transport=None, cota_cazare=None)   # fără ele, nicio cotă cerută
        assert linii(cur, r["inregistrare_id"])[0][:3] == ("625", "542", "300.00")


def test_def_524_avansul_nu_poate_depasi_soldul_542(monkeypatch, excedente):
    """Avansul în ciornă nu e încă sold: refuzul o numește (deficiența 524, regula soldului stins)."""
    from core import erori
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur)
        nota(cur, "2026-10-10", [("542", "5311", 1000)], status="ciorna")
        with pytest.raises(erori.DateInvalide) as e:
            _decont(uc, sid)
        m = e.value.detaliu["mesaj"]
        assert "contul 542" in m and "sold debitor 0,00 lei" in m and "valideaz-o întâi" in m, m
        assert e.value.detaliu["erori_campuri"][0]["camp"] == "op-avans"


def test_def_670_b_strainatate_la_cursul_bnr(monkeypatch, excedente):
    """În străinătate: 2,5 x diurna țării (HG 518/1995) x cursul BNR (CF art.290 alin.(2)): 35 EUR x 2,5 x 5 = 437,50 lei/zi."""
    from core import curs_bnr, uc_comun
    monkeypatch.setattr(curs_bnr, "curs_pentru", lambda conn, moneda, data, **k: (Decimal("5"), data, "bnr"))
    monkeypatch.setattr(uc_comun, "_preincalzeste_cursul", lambda *a, **k: None)
    with schema_ops(monkeypatch) as (c, cur, uc):
        sid = salariat(cur, salariu=20000)
        r = _decont(uc, sid, avans=0, diurna=1500, zile=3, deplasare="externa", diurna_bugetara=35, moneda="EUR", transport=0, cazare=0)
        assert (r["diurna"]["plafon_zi"], r["diurna"]["neimpozabil"], r["diurna"]["impozabil"]) == ("437.50", "1312.50", "187.50")
        assert excedente[0][3] == Decimal("187.50")
