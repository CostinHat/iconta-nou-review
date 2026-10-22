# -*- coding: utf-8 -*-
"""[lotul 11, C99] Contribuția minimă (suprataxa) în luna cu concediu medical: aceeași cifră pe stat / fluturaș și în D112, dintr-un
singur loc de calcul (`salarizare.baza_minima_contributii` pe `salarizare.zile_contract_activ`).

SURSE (locale):
- CF art.146 alin.(5^6) (`anaf_surse/cod_fiscal_227_2015_consolidat.txt`): „… asupra salariului de bază minim brut pe țară în vigoare în
  luna pentru care se datorează contribuția de asigurări sociale, corespunzător numărului zilelor lucrătoare din lună în care contractul a
  fost activ.”
- Legea 53/2003 (Codul muncii) art.50 (`anaf_surse/legea_53_2003_codul_muncii.txt`): „Contractul individual de muncă se suspendă de drept
  în următoarele situații: […] b) concediu pentru incapacitate temporară de muncă”; art.49 alin.(2): „Suspendarea contractului individual
  de muncă are ca efect suspendarea prestării muncii de către salariat și a plății drepturilor de natură salarială de către angajator.”
- Structura D112: „part_time= ROUND(sm*zile_PT /NZL)”, „Daca baza>0 si baza<part_time atunci B4_7P =part_time”; arbitrul DUK (regula
  SP1B4_1) calculează suma limită pe zilele lucrate declarate (B4_1), fără zilele de CM.

Până la 22.10.2026: statul socotea podeaua pe zilele active CU zilele de CM (suprataxă 349 + 140 lei la 5.000 lei cu 10 zile de CM), D112
pe zilele fără CM (0); salariatul scutit de contribuția minimă primea suprataxă pe stat (statul nu transmitea scutirea), dar nu și în D112.

CNP-urile de test sunt verificate cu algoritmul cifrei de control (CLAUDE.md): 1800101410013.
"""
import datetime
from decimal import Decimal

import pytest

from core import d112, db as _db, salariati_api, salarizare, stat_plata_api
from core.common import Perioada
from core.test_lot11_s9_deducere_plafon import _setup, structura, unic

_SCHEMA = "test_lot11_s9_supra"
_LUNA = datetime.date(2026, 9, 1)     # 22 de zile lucrătoare; salariul minim 4.325, suma netaxabilă 200 -> nivelul 4.125


def _db_ok():
    try:
        _db.init_pool()
        with _db.get_conn():
            return True
    except Exception:
        return False


@pytest.fixture
def conn():
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            yield c
        finally:
            c.rollback()
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
            c.commit()


def _firma(conn, salariat, cm_zile=0, scutit=False):
    """Salariatul + (opțional) un certificat cod 01 salvat pe drumul aplicației (`salariati_api.salveaza_concediu`), 1–10.09.2026 (8 zile
    lucrătoare, sub cele 10 zile calendaristice ale medicului de familie). Întoarce (rândul statului, secțiunile D112 ale salariatului)."""
    with conn.cursor() as cur:
        _setup(cur, [salariat], schema=_SCHEMA)
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
        if scutit:   # date de pornire: scutirea de contribuția minimă (motivul 1, elev/student sub 26 de ani) — câmpul fișei
            cur.execute("UPDATE salariati SET scutit_contrib_minim = true, motiv_exceptare = 1")
        cur.execute("SELECT id FROM salariati")
        sid = cur.fetchone()[0]
    if cm_zile:
        salariati_api.salveaza_concediu(conn, sid, {
            "serie": "AB", "numar": "1", "cod": "01", "data_acordare": "2026-09-01", "data_inceput": "2026-09-01",
            "data_sfarsit": "2026-09-10", "loc_prescriere": 1, "zile_cm": cm_zile, "venituri_6_luni": 30000, "zile_6_luni": 125,
            "an": 2026, "luna": 9})
    conn.commit()
    with conn.cursor() as cur:
        cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
    st = stat_plata_api.stat_final(conn, _SCHEMA, 2026, 9)
    assert len(st) == 1, st
    xml = d112.genereaza(conn, _SCHEMA, Perioada(an=2026, luna=9))[0]
    return st[0], structura(xml)[salariat["cnp"]], xml


def _duk_valid(xml):
    from core import duk
    if not duk.poate_valida("d112"):
        pytest.skip("DUK d112 indisponibil")
    rez = duk.valideaza(xml, "d112", an=2026, luna=9)
    assert rez["stare"] == "valid", rez


def test_c99_baza_minima_pe_zilele_active_fara_cm():
    """Unicul loc de calcul: 09/2026, nivelul 4.325 − 200 = 4.125; pe 22 de zile = 4.125, pe 14 = ROUND(4.125 × 14 / 22) = 2.625 (cifra pe
    care o calculează DUK, SP1B4_1); zilele active scad cu zilele de CM (Codul muncii art.50 lit.b: suspendare de drept)."""
    assert salarizare.baza_minima_contributii(_LUNA, 22) == Decimal("4125")   # CF art.146 alin.(5^6), luna întreagă
    assert salarizare.baza_minima_contributii(_LUNA, 14) == Decimal("2625")   # „corespunzător numărului zilelor … în care … activ”
    assert salarizare.zile_contract_activ(_LUNA, "2024-01-01", None, (), 8) == 14
    assert salarizare.zile_contract_activ(_LUNA, "2024-01-01", None, (), 0) == 22


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c99_norma_intreaga_cu_cm_fara_suprataxa_nici_pe_stat_nici_in_d112(conn):
    """5.000 lei, 8 zile de CM: baza 5.000 × 14 / 22 = 3.182 > 2.625 -> nicio suprataxă pe stat, nicio sumă limită în D112. ROȘU pe codul
    vechi: statul 4.025 (zilele active cu CM) -> suprataxă CAS + CASS > 0, D112 0. DUK valid."""
    r, a, xml = _firma(conn, {"cnp": "1800101410013", "nume": "CM", "dn": "1980-06-01", "brut": 5000}, cm_zile=8)
    b4 = unic(a, "asiguratB4")
    assert (r["cas_suprataxa"], r["cass_suprataxa"]) == (0.0, 0.0), r
    assert (b4["B4_7P"], b4["B4_8D"], b4["B4_6D"]) == ("0", "0", "0"), b4
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c99_norma_partiala_cu_cm_aceeasi_suprataxa_pe_stat_si_in_d112(conn):
    """Normă parțială de 4 ore, 2.000 lei, 8 zile de CM: baza = 2.000 × 14 / 22 = 1.273 < 2.625 -> suma limită 2.625 (B4_7P), CAS minim
    ROUND(2.625 × 25%) = 656 (B4_8P), CASS minim 263 (B4_6P); suprataxa pe stat = diferența față de reținut, aceeași cu B4_8D / B4_6D. DUK
    valid."""
    r, a, xml = _firma(conn, {"cnp": "1800101410013", "nume": "PARTIAL", "dn": "1980-06-01", "brut": 2000, "pt": True, "ore": 4},
                       cm_zile=8)
    b4 = unic(a, "asiguratB4")
    # structura D112: „part_time= ROUND(sm*zile_PT /NZL)”; „B4_8P = ROUND (B4_7P * 25%)”
    assert (b4["B4_7P"], b4["B4_8P"], b4["B4_6P"]) == ("2625", "656", "263"), b4
    assert (r["cas_suprataxa"], r["cass_suprataxa"]) == (float(b4["B4_8D"]), float(b4["B4_6D"])), (r, b4)
    assert r["cas_suprataxa"] > 0 and r["cass_suprataxa"] > 0, r
    _duk_valid(xml)


@pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")
def test_c99_salariatul_scutit_fara_suprataxa_pe_stat(conn):
    """Normă parțială de 4 ore, 2.000 lei, scutit de contribuția minimă (CF art.146 alin.(5^7), motivul 1): nicio suprataxă pe stat, ca în
    D112 (asigExc = 1, fără sume limită). ROȘU pe codul vechi: statul nu transmitea scutirea -> suprataxă > 0."""
    r, a, xml = _firma(conn, {"cnp": "1800101410013", "nume": "SCUTIT", "dn": "2004-06-01", "brut": 2000, "pt": True, "ore": 4},
                       scutit=True)
    b4 = unic(a, "asiguratB4")
    assert (r["cas_suprataxa"], r["cass_suprataxa"]) == (0.0, 0.0), r
    assert (b4["B4_7P"], b4["B4_8D"]) == ("0", "0"), b4
    _duk_valid(xml)
