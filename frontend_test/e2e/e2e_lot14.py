# -*- coding: utf-8 -*-
"""Lotul 14, comanda Costin 14.1 (verbatim în DECIZII „Comanda 14.1”) — probe de capăt la capăt, în browser, pe ecranele reale:

  * 688 — Închidere lună / TVA: „La plătitorii de TVA, închiderea trebuie să propună nota 4427 = 4426 + 4423/4424 pe perioada fiscală a firmei și
    să refuze blocarea cât 4426/4427 au sold.” (firma cu 4426 D 210 și 4427 C 210 la sfârșitul lunii trecute).
  * 683 — Bilanț: fereastra spune că lipsesc rulajele dinainte de preluare, cu trimitere la Import date › Solduri inițiale; după import, bilanțul
    folosește rulajele importate (nu mai refuză).
  * 695 — D100: perioada care începe înainte de preluare se refuză (nu se validează cu veniturile din septembrie singure).
  * 696 — Stocuri: stocul validat, ciorna separat, reconcilierea cu 371 în carduri-rezumat.
  * 687 — ferestrele de lucru încap pe un singur ecran la 1920×1080 și 1366×768 (Stocuri, Închidere lună, Balanță).

DATE DE PORNIRE fără ecran (declarate): notele validate se scriu pe ruta Registrului jurnal (`_nota_validata`); soldurile de preluare și rulajele lor
direct în schema firmei noi (SQL) — importul pe ecran e probat de `e2e_import_saga.py`; aici ecranul probat e cel care CITEȘTE ce a adus importul.
Firmele sunt NOI (`firma_noua`)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_c import _declaratie_pas1
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata

AZI = _dt.date.today()
LUNA_TRECUTA = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
_F = ".fereastra:last-of-type"
REZOLUTII = [(1920, 1080), (1366, 768)]


@pytest.fixture()
def firma_tva():
    """Plătitoare de TVA, decont lunar, regim micro; luna trecută: factură furnizor (4426 = 401, 210) și vânzare (4111 = 4427, 210), validate."""
    for f in firma_noua():
        _date_firma(f)
        st, r = _api(PATRON, "POST", "/tenants/%d/vector" % f["tenant_id"],
                     {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "inreg_art317": False,
                      "tva_data_inceput": "2026-01-01"})
        assert st == 200, (st, r)
        zi = LUNA_TRECUTA.replace(day=10).isoformat()
        _nota_validata(f, zi, "4426", "401", 210, "Factura furnizor T14")
        _nota_validata(f, LUNA_TRECUTA.replace(day=20).isoformat(), "4111", "4427", 210, "Vanzare T14")
        yield f


def _incape(pg):
    return pg.evaluate("() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); return {dep: c.scrollHeight - c.clientHeight, lat: c.scrollWidth - c.clientWidth}; }")


def test_def_c206_inchiderea_lunii_cere_regularizarea_tva_si_o_propune(patron, firma_tva):
    """688. Pașii: firma cu 4426 D 210 și 4427 C 210 la sfârșitul lunii trecute -> Închidere lună, luna trecută: „Ce oprește închiderea” spune că TVA-ul
    nu e regularizat (cu 210,00 lei), „Blochează luna” e inactiv -> „Propune regularizarea TVA”: nota 4427 = 4426 (ciornă) -> o validez în Registrul
    jurnal -> blocajul dispare și luna se poate bloca. MUTAȚIA: blocajul `TVA_NEREGULARIZAT` scos din `uc_comun.controale_inchidere` -> ROȘU."""
    f = firma_tva
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-inchidere", "Închidere lună")
    pg.click(_F + " #il-prev")
    pg.wait_for_function("(t) => (document.querySelector('.fereastra:last-of-type #il-controale') || {innerText: ''}).innerText.includes(t)",
                         arg="TVA-ul perioadei nu e regularizat", timeout=30000)
    txt = " ".join(pg.inner_text(_F + " #il-controale").split())
    patron.captura("tva_neregularizat")
    assert "210,00 lei" in txt, txt
    assert pg.is_disabled(_F + " #il-lock"), "luna se poate bloca cu TVA-ul neregularizat"
    pg.click(_F + " #il-tva-regularizare")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #il-mesaj') || {innerText: ''}).innerText.includes('Am propus')", timeout=30000)
    patron.captura("regularizare_propusa")
    r = sql('SELECT id, status, sursa FROM "%s".inregistrari WHERE sursa = \'regularizare_tva\'' % f["schema"])
    assert len(r) == 1 and r[0][1] == "ciorna", r
    st, rez = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], r[0][0]), {})
    assert st == 200, (st, rez)
    pg.click(_F + " #il-next")
    pg.click(_F + " #il-prev")
    pg.wait_for_function("() => !(document.querySelector('.fereastra:last-of-type #il-controale') || {innerText: ''}).innerText.includes('nu e regularizat')", timeout=30000)
    patron.captura("dupa_validare")
    assert "TVA-ul perioadei nu e regularizat" not in pg.inner_text(_F + " #il-controale")


@pytest.fixture()
def firma_preluata():
    """Înființată în 2025, preluată cu balanța de la 31.08 a anului curent, FĂRĂ rulajele anului (numai solduri finale): capital 1.000 / bancă 1.000."""
    for f in firma_noua():
        _date_firma(f)
        st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"data_infiintare": "2025-01-10"})
        assert st == 200, (st, r)
        ref = "%d-08-31" % AZI.year
        # date-de-pornire: balanța de deschidere numai cu soldurile finale (importul pe ecran e probat de e2e_import_saga.py)
        sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES '
            "('5121', 'Banca', 1000, 0, %%s), ('1012', 'Capital', 0, 1000, %%s)" % f["schema"], (ref, ref))
        yield f


def test_def_c204_bilantul_refuza_fara_rulajele_preluate_si_le_foloseste_dupa_import(patron, firma_preluata):
    """683. Pașii: firma preluată pe 31.08 cu numai soldurile finale -> Bilanț anual, anul curent, S1005: refuz cu „Rulajele anului până la preluare” /
    „începe înainte de preluarea firmei”, cu trimitere la Import date › Solduri inițiale (buton). Apoi balanța de deschidere primește rulajele anului
    (date de pornire: coloanele de an ale soldurilor) -> același ecran: refuzul rulajelor nu mai apare. MUTAȚIA: motivul scos din
    `bilant_api.coloana_curenta_f10` -> bilanțul nu mai refuză -> ROȘU."""
    f = firma_preluata
    pg = patron.pg
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    pg.fill(_F + " #bl-an", str(AZI.year))
    pg.dispatch_event(_F + " #bl-an", "change")
    pg.select_option(_F + " #bl-tip", "s1005")
    pg.wait_for_selector(_F + " .bl-prec-refuz", timeout=30000)
    msg = " ".join(pg.inner_text(_F + " .bl-prec-refuz").split())
    patron.captura("bilant_refuz_rulaje")
    assert "începe înainte de preluarea firmei" in msg and "Import date › Solduri inițiale" in msg, msg
    assert pg.locator(_F + " #bl-import-solduri").count() == 1
    # import: rulajele anului ale balanței de deschidere (date de pornire; formatul SAGA complet e probat de e2e_import_saga.py)
    sql('UPDATE "%s".solduri_initiale SET si_an_debit = 0, si_an_credit = 0, rulaj_an_debit = sold_debitor, rulaj_an_credit = sold_creditor' % f["schema"])
    pg.select_option(_F + " #bl-tip", "")
    pg.select_option(_F + " #bl-tip", "s1005")
    pg.wait_for_timeout(2500)
    after = " ".join(pg.inner_text(_F).split())
    assert "începe înainte de preluarea firmei" not in after, after[:1500]


def test_def_c205_d100_pe_trimestrul_dinainte_de_preluare_se_refuza(patron, firma_preluata):
    """695. Pașii: firma preluată pe 31.08, fără rulajele anului -> Declarații -> D100, T3 (iulie–septembrie) -> Continuă: refuz cu trimitere la Import date ›
    Solduri inițiale, fără „Trimite în coadă” (înainte: D100 pe T3 cu numai septembrie, validat). MUTAȚIA: refuzul scos din `d100.genereaza` -> ROȘU."""
    f = firma_preluata
    pg = patron.pg
    st, r = _api(PATRON, "POST", "/tenants/%d/vector" % f["tenant_id"],
                 {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False, "inreg_art317": False, "tva_data_inceput": "2026-01-01"})
    assert st == 200, (st, r)
    _declaratie_pas1(patron, f["nume"], "d100", AZI.year, trim=3)
    pg.wait_for_selector("#dec-trimite, #dec-gol-da, .dec-eroare", timeout=90000)
    patron.captura("d100_refuz")
    t = " ".join(patron.fereastra().split())
    assert "D100 pe T3/%d nu se poate genera" % AZI.year in t and "Import date › Solduri inițiale" in t, t[:1500]
    assert pg.locator("#dec-trimite").count() == 0


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_c203_ferestrele_incap_pe_un_ecran_stocuri_inchidere_balanta(patron, firma_tva, lat, inalt):
    """687. Pașii: pe firma cu date, la 1920×1080 și 1366×768, Stocuri, Închidere lună (cu blocaj) și Balanță nu derulează în corp (derulează cel mult zona
    tabelului / a listei). MUTAȚIA: `_zonaDerulare()` scos din navigator -> ROȘU."""
    f = firma_tva
    pg = patron.pg
    # date-de-pornire: 60 de articole (rânduri în situația stocului), ca tabelul să fie lung și fereastra să deruleze fără zona lui
    sql('INSERT INTO "%s".articole (denumire, um, cont_stoc, cont_cheltuiala) SELECT \'Articol \' || g, \'buc\', \'371\', \'607\' FROM generate_series(1, 60) g' % f["schema"])
    vechi = pg.viewport_size
    pg.set_viewport_size({"width": lat, "height": inalt})
    try:
        for card, text in (("#fa-stocuri", "Stocuri"), ("#fa-inchidere", "Închidere lună"), ("#fa-balanta", "Balanță de verificare")):
            patron.firma(f["nume"])
            _deschide(patron, card, text)
            pg.wait_for_timeout(1500)
            m = _incape(pg)
            patron.captura("incape_%s_%dx%d" % (card[4:], lat, inalt))
            assert m["dep"] <= 1 and m["lat"] <= 1, (card, m)
    finally:
        pg.set_viewport_size(vechi)


def test_def_c208_stocuri_arata_stocul_validat_si_reconcilierea_in_carduri(patron, firma_tva):
    """696. Pașii: firma cu un articol cu intrare în stoc (mișcare fără notă = stoc preluat) -> Stocuri: tabelul cu coloana „Gestiune” și „În ciornă (lei)”, iar sub
    titlu cardurile-rezumat (butoane): reconcilierea cu balanța. MUTAȚIE: `carduriStocuri` scos din `ecranStocuri` -> nu există carduri -> ROȘU."""
    f = firma_tva
    pg = patron.pg
    st, r = _api(PATRON, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"metoda_stoc": "cantitativ_valoric"})
    assert st == 200, (st, r)
    st, r = _api(PATRON, "POST", "/tenants/%d/stocuri/intrare" % f["tenant_id"],
                 {"denumire": "Grâu T14", "um": "kg", "data": (AZI - _dt.timedelta(days=3)).isoformat(), "cantitate": 200, "pret_unitar": 2, "locatie": "Depozit 1"})
    assert st == 200 and not (r or {}).get("eroare"), (st, r)
    patron.firma(f["nume"])
    _deschide(patron, "#fa-stocuri", "Stocuri")
    pg.wait_for_selector(_F + " #s-carduri .card-rezumat", timeout=30000)
    patron.captura("stocuri_carduri")
    cap = [c.strip() for c in pg.locator(_F + " #s-situatie-tabel thead th").all_inner_texts()]
    assert "Gestiune" in cap and "În ciornă (lei)" in cap, cap
    assert pg.locator(_F + " #s-carduri .card-rezumat[data-card='reconciliere']").count() == 1
    assert pg.eval_on_selector_all(_F + " #s-carduri .card-rezumat", "e => e.every(b => b.tagName === 'BUTTON')")
