# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.2 (verbatim în `~/ghid_incoming/comanda_12_2.txt`), pachetul `reev2` — pașii contabilului pe aplicația din
index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`), plătitoare de TVA.

  630 Reevaluare valută, luna neîncheiată: cursul ultimei zile bancare nu e publicat încă -> diferența provizorie la ultimul curs, marcată;
      cursul cu virgulă; stornarea numită; soldul în lei din 4111 (nota), la ban.
  639 Termenul D390 al lui noiembrie nu se mută pe 21 decembrie (excepția CPF art.155 alin.(2) e a creanțelor); D300 rămâne pe 21.
  268.1 Emailul „TEST Alertă iConta.eu — sănătate server” n-are „Dezabonează-te” de la noi (antetul Brevo: vezi raportul).

DATE DE PORNIRE fără ecran (declarate, regula lui 429): factura EUR pe ruta formularului de emitere (`POST facturi/emite`), validarea contării
pe ruta „Validează” din Registrul jurnal, stornarea pe ruta butonului „Stornează” (`POST facturi/{id}/storno`), vectorul fiscal pe ruta
ecranului Date firmă (`POST vector`). Clientul: DANTE INTERNATIONAL SA, CUI 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md).

Temei: OMFP 1802/2014 pct.325 alin.(1) și alin.(2) lit.b (cursul BNR „din ultima zi bancară a lunii în cauză”); CPF art.155 alin.(2)
(„Creanțele fiscale […] scadența și/sau termenul de declarare se împlinesc la 25 decembrie, sunt scadente și/sau se declară până la data de
21 decembrie”); CPF art.75 -> Legea 134/2010 art.181 alin.(2) („Când ultima zi a unui termen cade într-o zi nelucrătoare, termenul se
prelungește până în prima zi lucrătoare care urmează.”); OPANAF 705/2020 (D390: „până la data de 25 inclusiv a lunii următoare”)."""
import calendar
import datetime as _dt
import re
from decimal import Decimal

import pytest

from conftest import BAZA, _ecran, firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, PRODUS, _api, _card, _ok, pregateste_firma


@pytest.fixture()
def firma_r():
    for f in firma_noua():
        yield f


@pytest.fixture()
def superadmin(browser, request):
    yield from _ecran(browser, request, "admin@prisma-cont.test")


def _bani(x):
    """Forma românească a sumei (DS cap.4): 1.906,98."""
    s = "{:,.2f}".format(Decimal(str(x)))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _factura_eur_azi(patron, f):
    """Factura EUR de azi (2 × 150 EUR + 21% = 363,00 EUR), pe ruta formularului de emitere, cu contarea validată. Întoarce id-ul."""
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                       "articol_id": None}], "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"],
            "tert_adresa": CLIENT["#em-adresa"], "moneda": "EUR", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None,
            "bon_fiscal_data": None, "data_emitere": AZI.isoformat(), "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat(),
            "tip": "factura"}
    fid = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % f["tenant_id"], corp), "emitere")["factura_id"]
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND status = \'ciorna\'' % f["schema"], (fid,)):
        _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {}), "validarea contării")
    return fid


def test_def_630_reevaluarea_lunii_in_curs_arata_diferenta_provizorie_stornarea_si_soldul_din_4111(patron, firma_r):
    """630. Pașii: factura EUR de azi, contată și validată; a doua factură EUR, contată, validată și stornată (stornarea rămâne cu nota în
    ciornă) -> Închidere lună (luna în curs) -> „Reevaluare valută”: rândul DANTE are cursul BNR cu virgulă, „din <ziua cursului> —
    provizoriu” și diferența „provizorie”; caseta spune simplu că cursul ultimei zile bancare nu e publicat încă (fără „flux întrerupt”);
    „Sold în lei” = suma de pe 4111 a notelor validate; stornarea apare numită la „Facturi în valută care nu intră”; „Generează nota”
    inactiv. MUTAȚIE (JS): marcajul „provizoriu” scos -> pică."""
    from core import curs_bnr as _cb
    f = firma_r
    pregateste_firma(patron, f, platitor=True, regim_fiscal="profit")
    f1 = _factura_eur_azi(patron, f)
    f2 = _factura_eur_azi(patron, f)
    _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (f["tenant_id"], f2), {}), "stornarea")
    from core.pdf_util import serie_nr
    ((st_serie, st_numar),) = sql('SELECT serie, numar FROM "%s".facturi WHERE storno_din_id = %%s' % f["schema"], (f2,))
    ((o_serie, o_numar),) = sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % f["schema"], (f2,))
    eticheta_storno = "Factură %s din %s (stornarea %s)" % (serie_nr(st_serie, st_numar), AZI.strftime("%d.%m.%Y"), serie_nr(o_serie, o_numar))
    (lei_4111,) = sql('SELECT COALESCE(SUM(l.suma), 0) FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
                      'WHERE i.factura_id = ANY(%%s) AND i.status = \'validata\' AND l.cont_debit LIKE \'411%%%%\'' % (f["schema"], f["schema"]),
                      ([f1, f2],))[0]
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector(".fereastra:last-of-type #il-reevaluare", timeout=60000)
    pg.click(".fereastra:last-of-type #il-reevaluare")
    pg.wait_for_selector(".fereastra:last-of-type #rv-tabel", timeout=60000)
    z = ".fereastra:last-of-type "
    patron.captura("luna_in_curs")
    rand = pg.locator(z + "#rv-tabel tbody tr:has-text('DANTE INTERNATIONAL SA')")
    celule = [" ".join(c.split()) for c in rand.locator("td").all_inner_texts()]
    fereastra = " ".join(patron.fereastra().split())
    # OMFP 1802/2014 pct.325 alin.(1): creanța din evidență — soldul 4111 al partenerului, din notele validate, la ban
    assert celule[6] == _bani(lei_4111), (celule, lei_4111)
    # cursul cu virgulă, urmat de ziua lui: „5,3495 din 23.10.2026 — provizoriu” (punctele datei nu sunt ale cursului)
    assert "flux întrerupt" not in fereastra and re.match(r"\d+,\d{4} din \d{2}\.\d{2}\.\d{4}\b", celule[7]), (celule, fereastra)
    m = re.match(r"(\d+,\d{4,6}) din (\d\d)\.(\d\d)\.(\d{4})", celule[7])
    assert m, celule
    data_curs = _dt.date(int(m.group(4)), int(m.group(3)), int(m.group(2)))
    sfarsit = AZI.replace(day=calendar.monthrange(AZI.year, AZI.month)[1])
    asteptata = _cb.ziua_bancara_asteptata(sfarsit, _cb.REGULA_SFARSIT_LUNA)
    if data_curs < asteptata:
        # pct.325 alin.(2) lit.b: până la cursul ultimei zile bancare, diferența e provizorie și se spune
        assert celule[7].endswith("— provizoriu") and celule[8].endswith("provizorie"), celule
        caseta = " ".join(pg.inner_text(z + "#rv-curs-provizoriu").split())
        assert caseta.startswith("Cursul BNR din ultima zi bancară a lunii (%s)" % asteptata.strftime("%d.%m.%Y")), caseta
        assert "Diferența e provizorie, la ultimul curs publicat: %s din %s" % (m.group(1), data_curs.strftime("%d.%m.%Y")) in caseta, caseta
    else:   # rularea chiar în ultima zi bancară, după publicare: cursul e cel final, fără marcaj
        assert "provizori" not in " ".join(celule) and pg.locator(z + "#rv-curs-provizoriu").count() == 0, celule
    neincluse = " ".join(pg.inner_text(z + "#rv-neincluse").split())
    # stornarea numită lângă factura ei; nota ei de contare e în ciornă, deci nu intră încă în sold (se spune, nu se sare tăcut)
    assert "%s — %s: nota ei de contare e ciornă" % (eticheta_storno, CLIENT["#em-nume"]) in neincluse, (eticheta_storno, neincluse)
    assert pg.is_disabled(z + "#rv-genereaza")   # nota se generează după sfârșitul lunii, cu cursul ultimei zile bancare
    assert not patron.erori, patron.erori


def test_def_639_termenul_d390_din_noiembrie_nu_trece_pe_21_decembrie(patron, firma_r):
    """639. Pașii: firmă plătitoare de TVA cu operațiuni intracomunitare (Date firmă -> vector) -> Declarații -> lista „Datorate de firmă”:
    fiecare D390 are termenul pe 25 sau pe prima zi lucrătoare de după (25–29 ale lunii), niciodată pe 21 decembrie; D300 al lui noiembrie,
    dacă e în listă, rămâne pe 21.12 (creanță). MUTAȚIE (Python): excepția de 21 decembrie aplicată oricărui tip -> D390 11/2026 apare cu
    21.12.2026 (cât timp 21.12 e în fereastra de 60 de zile) -> pică."""
    f = firma_r
    pregateste_firma(patron, f, platitor=True, regim_fiscal="profit")
    _ok(_api(patron, "POST", "/tenants/%d/vector" % f["tenant_id"], {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
                                                                     "operatiuni_ic": True, "inreg_art317": False,
                                                                     "tva_data_inceput": "2026-01-01"}), "vectorul cu operațiuni IC")
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", "#dec-tip")
    pg.wait_for_timeout(800)
    optiuni = [" ".join(t.split()) for t in pg.locator("#dec-tip option").all_inner_texts()]
    patron.captura("datorate")
    termene = {}
    for o in optiuni:
        m = re.match(r"(D\d+) · (.+?) · termen de depunere (\d\d)\.(\d\d)\.(\d{4})", o)
        if m:
            termene.setdefault(m.group(1), []).append((m.group(2), _dt.date(int(m.group(5)), int(m.group(4)), int(m.group(3)))))
    assert termene.get("D390"), optiuni
    for per, t in termene["D390"]:
        # OPANAF 705/2020: „până la data de 25 inclusiv a lunii următoare”; Legea 134/2010 art.181 alin.(2): zi nelucrătoare -> DUPĂ
        assert 25 <= t.day <= 29 and t.weekday() < 5, (per, t, optiuni)
    for per, t in termene.get("D300", []):
        if t.month == 12 and t.day < 25:
            # CPF art.155 alin.(2): creanța de 25 decembrie „se declară până la data de 21 decembrie” (ultima zi lucrătoare dinainte)
            assert t <= _dt.date(t.year, 12, 21), (per, t)
    assert not patron.erori, patron.erori


def test_def_268_1_alerta_de_test_n_are_dezabonare(superadmin):
    """268.1. Pașii administratorului: Panou Admin -> Sănătate server -> „Trimite alertă de test” -> emailul „TEST Alertă iConta.eu —
    sănătate server” (cutia de test a instanței de probă) n-are „Dezabonează-te” și nici antetele List-Unsubscribe — dezabonarea e numai
    pe recomandări și pe sinteza zilnică (268). MUTAȚIE (Python): subsolul de dezabonare pus pe orice email -> pică."""
    from e2e_inregistrare_libera import _scrisori
    pg = superadmin.pg
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    pg.wait_for_selector(".cab-grila", timeout=30000)
    pg.click("button.cab-card:has([data-cheie='sanatate'])")
    pg.wait_for_selector("#san-test-alerta", timeout=30000)
    pg.click("#san-test-alerta")
    pg.wait_for_function("() => /trimisă la/.test((document.querySelector('#san-test-msg') || {}).innerText || '')", timeout=30000)
    msg = " ".join(pg.inner_text("#san-test-msg").split())
    catre = re.search(r"trimisă la (\S+)\.", msg).group(1)
    superadmin.captura("alerta_trimisa")
    alerte = [s for s in _scrisori(catre) if s["subiect"] == "TEST Alertă iConta.eu — sănătate server"]
    assert alerte, msg
    ultima = alerte[-1]
    assert ultima["antete"] == {} and ultima["html"].count("Dezabonează-te") == 0, ultima
    assert not superadmin.erori, superadmin.erori
