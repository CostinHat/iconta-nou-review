# -*- coding: utf-8 -*-
"""Lotul 11 — deficiența C88 (găsită de Code la 460): cursul monedelor cotate de BNR la 100 de unități se păstra cu 4 zecimale.

`public.curs_bnr_zilnic.curs numeric(12,4)`: HUF 1,4719 / 100 = 0,014719 devenea 0,0147 (IDR 0,0256 / 100 = 0,000256 devenea 0,0003);
aceeași precizie în `facturi.curs_bnr numeric(12,4)`, `rip_operatiuni.curs_valutar numeric(10,4)`, `reevaluari_valuta.curs_vechi /
curs_nou numeric(12,4)`, iar cursul din evidență calculat la reevaluare se rotunjea la 4 zecimale. Cursul se păstrează, se aplică și se
afișează cum îl dă BNR: valoarea / multiplicatorul (`curs_bnr.parse_xml`).

Temei: CF art.290 alin.(2) — „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României”
(`anaf_surse/cod_fiscal_227_2015_consolidat.txt`): cursul comunicat, nu o rotunjire a lui. HG 1/2016 pct.35 alin.(2) — „cursul de schimb
valutar utilizat [...] la data emiterii acestor facturi va rămâne neschimbat la data definitivării operațiunii”
(`anaf_surse/hg_1_2016_norme_cod_fiscal.txt`): migrarea NU recalculează facturile existente.

XML-ul de mai jos e o zi REALĂ din arhiva BNR (`https://curs.bnr.ro/files/xml/years/nbrfxrates2026.xml`, Cube 2026-07-01, descărcată
22.10.2026). Rândurile de cache scrise aici sunt pe zile SINTETICE (2099) și se anulează (ROLLBACK).
"""
import io
import re
from decimal import Decimal as D

import pytest

from core import curs_bnr as cb

#: Cube 2026-07-01, verbatim din arhiva BNR 2026 (numai antetul DataSet scurtat la ce cere `parse_xml`).
CUBE_2026_07_01 = (
    '<Cube date="2026-07-01"><Rate currency="AED">1.2531</Rate><Rate currency="AUD">3.1716</Rate><Rate currency="BRL">0.8919</Rate>'
    '<Rate currency="CAD">3.2359</Rate><Rate currency="CHF">5.6790</Rate><Rate currency="CNY">0.6774</Rate><Rate currency="CZK">0.2161</Rate>'
    '<Rate currency="DKK">0.7012</Rate><Rate currency="EGP">0.0937</Rate><Rate currency="EUR">5.2409</Rate><Rate currency="GBP">6.0966</Rate>'
    '<Rate currency="HKD">0.5867</Rate><Rate currency="HUF" multiplier="100">1.4719</Rate><Rate currency="IDR" multiplier="100">0.0256</Rate>'
    '<Rate currency="ILS">1.5456</Rate><Rate currency="INR">0.0484</Rate><Rate currency="ISK" multiplier="100">3.6446</Rate>'
    '<Rate currency="JPY" multiplier="100">2.8284</Rate><Rate currency="KRW" multiplier="100">0.2955</Rate><Rate currency="MDL">0.2602</Rate>'
    '<Rate currency="MXN">0.2625</Rate><Rate currency="MYR">1.1242</Rate><Rate currency="NOK">0.4631</Rate><Rate currency="NZD">2.6111</Rate>'
    '<Rate currency="PHP">0.0747</Rate><Rate currency="PLN">1.2204</Rate><Rate currency="RSD">0.0447</Rate><Rate currency="RUB">0.0591</Rate>'
    '<Rate currency="SEK">0.4721</Rate><Rate currency="SGD">3.5494</Rate><Rate currency="THB">0.1379</Rate><Rate currency="TRY">0.0985</Rate>'
    '<Rate currency="UAH">0.1027</Rate><Rate currency="USD">4.6023</Rate><Rate currency="XAU">589.5791</Rate><Rate currency="XDR">6.2379</Rate>'
    '<Rate currency="ZAR">0.2803</Rate></Cube>')


def _xml(cube=CUBE_2026_07_01):
    return ('<?xml version="1.0" encoding="utf-8"?><DataSet xmlns="https://www.bnr.ro/xsd" xmlns:xsi="https://www.w3.org/2001/'
            'XMLSchema-instance" xsi:schemaLocation="https://curs.bnr.ro/xsd/nbrfxrates.xsd"><Header><Publisher>National Bank of Romania'
            '</Publisher><PublishingDate>2026-10-22</PublishingDate><MessageType>DR</MessageType></Header><Body><Subject>Reference rates'
            '</Subject><OrigCurrency>RON</OrigCurrency>%s</Body></DataSet>' % cube)


def _db_ok():
    try:
        from core import db
        db.init_pool()
        with db.get_conn():
            return True
    except Exception:
        return False


DB = pytest.mark.skipif(not _db_ok(), reason="DB indisponibil")


# ── pur ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_parse_xml_pastreaza_cursul_pe_unitate_exact_din_arhiva_reala():
    h = cb.parse_xml(_xml())[cb.date(2026, 7, 1)]
    # CF art.290 alin.(2): „ultimul curs de schimb comunicat de Banca Națională a României” — HUF 1,4719 la 100 de unități
    assert h["HUF"] == D("0.014719") and str(h["HUF"]) == "0.014719", h["HUF"]
    assert h["IDR"] == D("0.000256") and h["KRW"] == D("0.002955") and h["JPY"] == D("0.028284") and h["ISK"] == D("0.036446")
    assert str(h["EUR"]) == "5.2409" and str(h["XAU"]) == "589.5791"      # cotate la unitate: neschimbate
    # monedele cu multiplicator din XML-ul real = lista măsurată (garda listei folosite la cursurile calculate)
    cotate_la_100 = set(re.findall(r'currency="([A-Z]{3})" multiplier="100"', CUBE_2026_07_01))
    assert cotate_la_100 == set(cb.MONEDE_COTATE_LA_100), cotate_la_100
    # nicio zecimală peste precizia declarată
    assert max(-v.as_tuple().exponent for v in h.values()) == cb.ZECIMALE_CURS


def test_cursul_calculat_are_precizia_bnr_a_monedei():
    """Cursul din evidență la reevaluare (sold în lei / sold în valută). MUTAȚIE: în `curs_derivat`, `CURS_Q if …` -> `CQ_MIN if …`
    (4 zecimale pentru toate) -> HUF 0,0147 -> pică."""
    assert cb.curs_derivat(D("14719") / D("1000000"), "HUF") == D("0.014719")
    assert cb.curs_derivat(D("256") / D("1000000"), "idr") == D("0.000256")
    assert cb.curs_derivat(D("1906.98") / D("363"), "EUR") == D("5.2534")             # EUR: 4 zecimale, ca BNR (neschimbat)
    assert str(cb.curs_derivat(D("1782.5") / D("121000"), "HUF")) == "0.014731"        # ROUND_HALF_UP: 0,0147314… -> 0,014731
    assert cb.curs_derivat(D("0.0147245"), "HUF") == D("0.014725")                     # ,5 -> în sus (aritmetic, nu bancar)


def test_cursul_scris_pentru_om_are_precizia_bnr():
    assert cb.curs_text(D("0.014719")) == "0,014719"
    assert cb.curs_text(D("5.2409")) == "5,2409"
    assert cb.curs_text(D("5.240900")) == "5,2409"
    assert cb.curs_text(D("0.01472")) == "0,01472"
    assert cb.curs_text(D("4.97")) == "4,9700"


def _coloane_curs(text):
    """[(coloana, scala)] — coloanele `curs*` numerice din DDL-ul `text` (scala None = `numeric` fără scală fixă)."""
    return [(m.group(1), int(m.group(3)) if m.group(3) else None)
            for m in re.finditer(r"\b(curs\w*)\s+numeric(\(\s*(?:\d+)\s*,\s*(\d+)\s*\))?", text, re.I)]


def test_garda_nicio_coloana_de_curs_sub_precizia_bnr():
    """GARDĂ: nicio coloană de curs (`curs*` numeric) din șablonul firmelor, din bootstrap-ul public sau dintr-un DDL din `core/*.py` cu
    scală fixă sub `curs_bnr.ZECIMALE_CURS`. Excepția unică: `core/migrare_reevaluari_valuta.py` (lotul 10, deja rulată pe producție;
    lărgită de `migrare_curs_precizie`, care rulează DUPĂ ea — `migrari_registru.DUPA`). MUTAȚIE: `curs_bnr numeric(12,4)` înapoi în
    `tenant_template.sql` -> pică."""
    import glob
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    surse = [os.path.join(rad, "tenant_template.sql"), os.path.join(rad, "infra", "bootstrap_public.sql")]
    surse += [p for p in glob.glob(os.path.join(rad, "core", "*.py"))
              if not os.path.basename(p).startswith("test_") and os.path.basename(p) != "migrare_reevaluari_valuta.py"]
    gasite, sub = 0, []
    for p in surse:
        for col, scala in _coloane_curs(io.open(p, encoding="utf-8").read()):
            gasite += 1
            if scala is not None and scala < cb.ZECIMALE_CURS:
                sub.append("%s: %s numeric(…,%d)" % (os.path.relpath(p, rad), col, scala))
    assert gasite >= 6, gasite          # curs_bnr, curs_valutar, curs_vechi, curs_nou, curs (d301), curs (cache public)
    assert not sub, "coloane de curs cu mai puține zecimale decât dă BNR (HUF 0,014719 -> 0,0147): %s" % sub


def test_garda_migrarea_acopera_toate_coloanele_de_curs_ale_sabloanelor():
    """Coloanele lărgite de migrare = coloanele de curs cu scală fixă din forma de DINAINTE (`numeric(12,4)` / `numeric(10,4)`) ale
    șabloanelor; o coloană de curs nouă intră deja cu precizia (garda de mai sus), deci lista nu poate rămâne în urmă tăcut."""
    from core import migrare_curs_precizie as mig
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sablon = {c for c, _s in _coloane_curs(io.open(os.path.join(rad, "tenant_template.sql"), encoding="utf-8").read())}
    assert {c for _t, c in mig.COLOANE_FIRMA} | {"curs"} == sablon, sablon       # „curs” = d301_operatiuni.curs (deja `numeric`)
    assert mig.COLOANE_PUBLIC == (("curs_bnr_zilnic", "curs"),)


# ── cu baza de test (ROLLBACK) ─────────────────────────────────────────────────────────────────────────────────────────────────
_SCHEMA = "tenant_test_c88_curs"
_LINIE_HUF = {"descriere": "Servicii consultanță", "cantitate": 1, "pret_unitar": 100000, "cota_tva": 21, "um": "buc",
              "cont_venit": "704"}


@pytest.fixture
def conn():
    from core import db as _db, tenant_provisioning as _tp
    _db.init_pool()
    with _db.get_conn() as c:
        try:
            with c.cursor() as cur:
                cur.execute("DROP SCHEMA IF EXISTS %s CASCADE" % _SCHEMA)
                cur.execute(_tp.parametrizeaza_template(io.open("tenant_template.sql", encoding="utf-8").read(), _SCHEMA))
                cur.execute("SET LOCAL search_path TO %s, public" % _SCHEMA)
                cur.execute("INSERT INTO firma_profil (id, nume, cui, adresa, oras, judet, caen, telefon, banca, iban, regim_fiscal, "
                            "platitor_tva, tip_decont, declarant_nume, declarant_prenume, declarant_functie, reg_com) VALUES (1,'F1 SRL',"
                            "'14399840','Str Test 1','Sector 1','B','4690','0722000000','BCR','RO49AAAA1B31007593840000','real',true,"
                            "'L','Popescu','Ion','ADMINISTRATOR','J40/1/2020')")
                cur.execute("UPDATE firma_profil SET forma_juridica = 'SRL', capital_subscris = 200, serie_factura = 'F1A', "
                            "metoda_stoc = 'global_valoric' WHERE id = 1")
            yield c
        finally:
            c.rollback()


def _cache_2099(conn, rand):
    """Scrie în cache (în tranzacția testului, anulată) cursurile Cube-ului real, mutate pe 01.07.2099 (zi sintetică)."""
    h = cb.parse_xml(_xml())[cb.date(2026, 7, 1)]
    with conn.cursor() as cur:
        for mon, v in rand(h).items():
            cur.execute("INSERT INTO public.curs_bnr_zilnic (data, moneda, curs) VALUES ('2099-07-01', %s, %s) "
                        "ON CONFLICT (data, moneda) DO UPDATE SET curs = EXCLUDED.curs", (mon, v))


@DB
def test_def_c88_cache_ul_public_pastreaza_cursul_bnr_exact(conn):
    """MUTAȚIE: `curs numeric(12,4)` în cache (forma de dinainte) -> HUF se citește 0,0147 -> pică."""
    _cache_2099(conn, lambda h: {"HUF": h["HUF"], "EUR": h["EUR"], "IDR": h["IDR"]})
    # CF art.290 alin.(2): cursul comunicat de BNR, nu o rotunjire a lui (factura din 02.07.2099 ia cursul comunicat pe 01.07.2099)
    assert cb._din_cache(conn, "HUF", cb.date(2099, 7, 2)) == (D("0.014719"), cb.date(2099, 7, 1))
    assert cb._din_cache(conn, "IDR", cb.date(2099, 7, 2))[0] == D("0.000256")
    c, _d = cb._din_cache(conn, "EUR", cb.date(2099, 7, 2))
    assert str(c) == "5.2409", c          # forma cursurilor la unitate rămâne cea a BNR (nu „5.240900”)


@DB
def test_def_c88_factura_in_huf_se_calculeaza_cu_cursul_exact(conn):
    """Factură 1 × 100.000 HUF + 21% din 02.07.2099, cursul automat din cache (comunicat pe 01.07.2099, HUF 1,4719 / 100).
    MUTAȚIE: `curs_bnr numeric(12,4)` în `tenant_template.sql` -> cursul facturii 0,0147 -> pică."""
    from core import facturi_api
    _cache_2099(conn, lambda h: {"HUF": h["HUF"]})
    r = facturi_api.creeaza_factura(conn, "F1A1", "2099-07-02", "emisa", [dict(_LINIE_HUF)], data_scadenta="2099-08-01",
                                    tert_nume="DANTE INTERNATIONAL SA", tert_cui="RO14399840", tert_adresa="Str. Test 2",
                                    tert_oras="Sector 2", tert_judet="B", status="emisa", moneda="HUF")
    with conn.cursor() as cur:
        cur.execute("SELECT curs_bnr, data_curs, tva_lei, total_lei, curs_sursa FROM facturi WHERE id = %s", (r["factura_id"],))
        curs, data_curs, tva_lei, total_lei, sursa = cur.fetchone()
    # HG 1/2016 pct.35 alin.(1): cursul comunicat în ziua anterioară; CF art.290 alin.(2): ultimul curs comunicat de BNR (exact)
    assert (curs, data_curs, sursa) == (D("0.014719"), cb.date(2099, 7, 1), "bnr"), (curs, data_curs, sursa)
    # CF art.319 alin.(20) lit.j): TVA în lei; ROUND_HALF_UP: 21.000 × 0,014719 = 309,099 -> 309,10 (cu 0,0147: 308,70)
    assert tva_lei == D("309.10"), tva_lei
    # 121.000 × 0,014719 = 1.780,999 -> 1.781,00 (cu 0,0147: 1.778,70)
    assert total_lei == D("1781.00"), total_lei


# ── migrarea ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
_VECHI = "tenant_test_c88_vechi"


@DB
def test_migrarea_largeste_coloanele_vechi_fara_sa_schimbe_datele(conn):
    """O firmă cu forma de DINAINTE (numeric(12,4) / numeric(10,4)): migrarea lărgește coloanele; cursul facturii existente rămâne exact
    cel scris (HG 1/2016 pct.35 alin.(2): „va rămâne neschimbat”); a doua rulare nu mai face nimic."""
    from core import migrare_curs_precizie as mig
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS %s CASCADE; CREATE SCHEMA %s" % (_VECHI, _VECHI))
        cur.execute("CREATE TABLE %s.facturi (id serial PRIMARY KEY, curs_bnr numeric(12,4)); "
                    "CREATE TABLE %s.rip_operatiuni (id serial PRIMARY KEY, curs_valutar numeric(10,4)); "
                    "CREATE TABLE %s.reevaluari_valuta (id serial PRIMARY KEY, curs_vechi numeric(12,4) NOT NULL, curs_nou numeric(12,4) "
                    "NOT NULL)" % (_VECHI, _VECHI, _VECHI))
        cur.execute("INSERT INTO %s.facturi (curs_bnr) VALUES (5.2534), (0.0147)" % _VECHI)
    assert mig.verifica(conn, _VECHI) is False
    assert mig.aplica(conn, _VECHI) == ["facturi.curs_bnr", "rip_operatiuni.curs_valutar", "reevaluari_valuta.curs_vechi",
                                        "reevaluari_valuta.curs_nou"]
    with conn.cursor() as cur:
        cur.execute("SELECT column_name, numeric_scale FROM information_schema.columns WHERE table_schema = %s AND column_name LIKE "
                    "'curs%%' ORDER BY 1", (_VECHI,))
        assert cur.fetchall() == [("curs_bnr", None), ("curs_nou", None), ("curs_valutar", None), ("curs_vechi", None)]
        cur.execute("SELECT curs_bnr::text FROM %s.facturi ORDER BY id" % _VECHI)
        # HG 1/2016 pct.35 alin.(2): cursul facturii emise „va rămâne neschimbat” — nimic recalculat
        assert [x[0] for x in cur.fetchall()] == ["5.2534", "0.0147"]
        cur.execute("INSERT INTO %s.facturi (curs_bnr) VALUES (0.014719) RETURNING curs_bnr" % _VECHI)
        assert cur.fetchone()[0] == D("0.014719")
    assert mig.verifica(conn, _VECHI) is True
    assert mig.aplica(conn, _VECHI) == []                      # idempotent


@DB
def test_migrarea_reface_cache_ul_rotunjit_din_arhiva_bnr(conn):
    """Cache-ul cu valorile rotunjite la 4 zecimale (cum le lăsa `numeric(12,4)`) se reface din arhiva BNR; valorile exacte nu se ating;
    a doua rulare nu mai reface nimic. MUTAȚIE: comparația cu rotunjirea scoasă (orice diferență refăcută) -> valoarea străină se
    suprascrie -> pică."""
    from core import migrare_curs_precizie as mig
    harta = {2099: cb.parse_xml(_xml(CUBE_2026_07_01.replace("2026-07-01", "2099-07-01")))}
    _cache_2099(conn, lambda h: {"HUF": D("0.0147"), "IDR": D("0.0003"), "EUR": h["EUR"], "JPY": D("0.0283")})
    r = mig.refa_cache(conn, harta, ani=[2099])
    assert r == {"refacute": 3, "pe_moneda": {"HUF": 1, "IDR": 1, "JPY": 1}, "ani": [2099]}, r
    with conn.cursor() as cur:
        cur.execute("SELECT moneda, curs::text FROM public.curs_bnr_zilnic WHERE data = '2099-07-01' ORDER BY 1")
        assert cur.fetchall() == [("EUR", "5.2409"), ("HUF", "0.014719"), ("IDR", "0.000256"), ("JPY", "0.028284")]
    assert mig.refa_cache(conn, harta, ani=[2099])["refacute"] == 0
    # o valoare care nu e nici a BNR, nici rotunjirea ei: oprire, nimic schimbat
    with conn.cursor() as cur:
        cur.execute("UPDATE public.curs_bnr_zilnic SET curs = 0.0150 WHERE data = '2099-07-01' AND moneda = 'HUF'")
    with pytest.raises(ValueError, match="HUF: în cache 0.0150"):
        mig.refa_cache(conn, harta, ani=[2099])
    with pytest.raises(ValueError, match="fără arhivă"):
        mig.refa_cache(conn, {}, ani=[2099])


def _curs_format_local(rad):
    """-> (formatările locale cu `minimumFractionDigits: 4`, definiția din api.js scutită). Definiția = linia din `static/js/api.js` care
    are și `maximumFractionDigits: 6` (precizia BNR); se întoarce separat, ca testul să-și verifice premisa (o listă goală de încălcări
    nu spune nimic dacă scanul nu vede nici definiția)."""
    import glob
    import os
    out, definitie = [], []
    for p in glob.glob(os.path.join(rad, "static", "js", "**", "*.js"), recursive=True):
        e_api = os.path.relpath(p, rad) == os.path.join("static", "js", "api.js")
        for i, l in enumerate(io.open(p, encoding="utf-8").read().splitlines(), 1):
            if not re.search(r"minimumFractionDigits\s*:\s*4\b", l):
                continue
            unde = "%s:%d" % (os.path.relpath(p, rad), i)
            (definitie if e_api and re.search(r"maximumFractionDigits\s*:\s*6\b", l) else out).append(unde)
    return out, definitie


def test_garda_cursul_se_afiseaza_numai_prin_cursvalutar():
    """DS cap.4 v2.101 (C88): cursul valutar pe ecran trece prin `cursValutar(v)` (precizia BNR, 4–6 zecimale); nicio formatare locală
    cu `minimumFractionDigits: 4` în afara definiției din api.js. MUTAȚIE: `Number(r.curs).toLocaleString("ro-RO", {
    minimumFractionDigits: 4 })` repus în emitere_ecran.js -> pică."""
    import os
    rad = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out, definitie = _curs_format_local(rad)
    assert len(definitie) == 1, definitie   # premisa: scanul vede exact definiția `cursValutar` din api.js
    assert out == [], out
