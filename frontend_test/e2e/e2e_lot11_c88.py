# -*- coding: utf-8 -*-
"""Lotul 11 — deficiența C88 (găsită de Code la 460): cursul monedelor cotate de BNR la 100 de unități se păstra și se afișa cu 4
zecimale — HUF 1,4719 / 100 = 0,014719 devenea 0,0147 (cache-ul `public.curs_bnr_zilnic`, `facturi.curs_bnr`, ecranele, PDF-ul).

Temei: CF art.290 alin.(2) — „cursul de schimb care se aplică este ultimul curs de schimb comunicat de Banca Națională a României [...]”
(`anaf_surse/cod_fiscal_227_2015_consolidat.txt`) — cursul comunicat, nu o rotunjire a lui; HG 1/2016 pct.35 alin.(1) — „cursul de
schimb comunicat de respectiva bancă în ziua anterioară” (factura din 02.07.2026 ia cursul comunicat pe 01.07.2026); CF art.319 alin.(20)
lit.j) — TVA-ul în lei pe factură, rotunjit aritmetic.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua` + `pregateste_firma`, pe rutele ecranelor):
Facturi -> Emite factură -> data 02.07.2026, clientul DANTE INTERNATIONAL SA (CUI 14399840, cifra de control verificată cu algoritmul
din CLAUDE.md), 1 × 100.000 HUF + 21% -> Monedă HUF -> sub totaluri: cursul BNR 0,014719 din 01.07.2026, TVA în lei 309,10, total
1.781,00 -> „Emite factură” -> factura scrisă cu cursul exact -> detaliul facturii: „curs BNR 0,014719”.

DATELE DE PORNIRE: niciuna scrisă de test. Cursul HUF din 01.07.2026 e în cache-ul bazei de test (date BNR publice, refăcute exact din
arhiva BNR de `core/migrare_curs_precizie.py`: `<Rate currency="HUF" multiplier="100">1.4719</Rate>` în Cube 2026-07-01 din
`https://curs.bnr.ro/files/xml/years/nbrfxrates2026.xml`); testul îl citește întâi și se oprește cu motivul dacă nu e cel al BNR."""
from decimal import Decimal

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import CLIENT, PRODUS, _card, _deschide_emiterea, pregateste_firma

ZI = "2026-07-02"
ZI_CURS = "2026-07-01"
CURS_HUF = Decimal("0.014719")       # BNR, 01.07.2026: 1,4719 la 100 HUF


@pytest.fixture(scope="module")
def firma_c88_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_c88(patron, firma_c88_noua):
    pregateste_firma(patron, firma_c88_noua)
    return firma_c88_noua


def test_def_c88_factura_in_huf_are_cursul_cu_precizia_bnr(patron, firma_c88):
    """Pașii: Emite factură în HUF din 02.07.2026 -> cursul arătat înainte de emitere, cel scris pe factură și cel din detaliul facturii
    sunt 0,014719 (BNR: 1,4719 / 100), iar TVA-ul și totalul în lei se calculează cu el. Pe codul vechi: 0,0147, TVA 308,70, total
    1.778,70. MUTAȚII: formatorul cursului cu 4 zecimale (JS) -> ecranul arată 0,0147 -> pică; `curs_bnr numeric(12,4)` în șablonul
    firmei -> factura păstrează 0,0147 -> pică."""
    f = firma_c88
    rand = sql("SELECT curs FROM public.curs_bnr_zilnic WHERE moneda = 'HUF' AND data = %s", (ZI_CURS,))
    assert rand and Decimal(str(rand[0][0])) == CURS_HUF, (
        "pornirea: cache-ul bazei de test nu are cursul BNR HUF din %s (%r) — rulează migrare_curs_precizie pe baza de test" % (ZI_CURS, rand))
    _deschide_emiterea(patron, f["nume"])
    pg = patron.pg
    pg.fill("#em-data", ZI)
    pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.fill("#em-l0-pret_unitar", "100000")
    pg.fill("#em-l0-cantitate", "1")
    pg.select_option("#em-moneda", "HUF")
    # CF art.319 alin.(20) lit.j) + ROUND_HALF_UP: 21.000 HUF × 0,014719 = 309,099 -> 309,10 lei (cu 0,0147: 308,70)
    pg.wait_for_function("() => (document.querySelector('#em-valuta-tva') || {innerText: ''}).innerText.includes('309,10')", timeout=60000)
    t = " ".join(pg.inner_text("#em-valuta").split())
    patron.captura("inainte_de_emitere")
    # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): ultimul curs comunicat de BNR, în ziua anterioară — exact, pe unitate
    assert "Curs BNR HUF 0,014719 din 01.07.2026" in t, t
    # 121.000 HUF × 0,014719 = 1.780,999 -> 1.781,00 lei (cu 0,0147: 1.778,70)
    assert "TVA în lei 309,10 lei" in t and "Total în lei 1.781,00 lei" in t, t
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
    patron.captura("emisa")
    r = sql('SELECT moneda, curs_bnr::text, data_curs::text, tva_lei::text, total_lei::text FROM "%s".facturi WHERE id = %%s'
            % f["schema"], (fid,))[0]
    # ce s-a arătat înainte de emitere = ce s-a scris pe factură (HG 1/2016 pct.35 alin.(2): cursul se fixează la emitere)
    assert r == ("HUF", "0.014719", ZI_CURS, "309.10", "1781.00"), r
    # Istoric facturi arată luna curentă (`istoricFacturi`: `facturi?an=&luna=`), iar factura e din 07/2026: contabilul merge înapoi cu
    # „← luna” până la luna facturii (`_la_luna` așteaptă antetul „Luna LL/AAAA” al fiecărei luni), apoi deschide rândul
    from e2e_bloc_e import _la_luna
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    an_f, luna_f = int(ZI[:4]), int(ZI[5:7])
    _la_luna(patron, "#fac-prev", an_f, luna_f)
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.wait_for_selector("#fd-pdf", timeout=25000)
    sub = " ".join(pg.inner_text(".fd-valuta-sub").split())
    patron.captura("detaliu")
    assert "curs BNR 0,014719" in sub and "01.07.2026" in sub, sub
