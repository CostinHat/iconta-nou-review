# -*- coding: utf-8 -*-
"""429 pe DRUMUL REAL al contabilului (lotul 11, comanda Costin 11.1 pct.11, verbatim în DECIZII „Comanda 11.1”: „429: reevaluarea în
valută e neschimbată pe producție (formular manual, fără propunere, fără curs BNR, nimic la închiderea lunii). Explică de ce a fost
raportată rezolvată și rezolv-o.”).

DE CE A FOST RAPORTATĂ REZOLVATĂ (lotul 10): testul de dinainte INSERA factura EUR direct în bază (moneda, cursul, totalul în lei) și o
valida cu SQL, într-o lună încheiată, cu cursul BNR în cache — adică exact datele pe care drumul real nu le producea pe producție. Pe F1
(19–20.10.2026) facturile EUR emise din ecran aveau nota de contare în CIORNĂ, luna era în curs, iar Costin a ajuns la reevaluare din
Operațiuni (formularul manual): propunerea sărea tăcut facturile, butonul din Închidere lună apărea numai cu blocaj, iar formularul manual
nu avea nici propunere, nici curs. Testul de acum reface pașii pe ecrane și pe API-ul aplicației, fără nicio inserare directă.

Pașii (pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ a fișierului, pregătită pe rutele ecranelor): Emite factură -> data
26.08.2026, clientul DANTE INTERNATIONAL SA (CUI 14399840, cifra de control verificată cu algoritmul din CLAUDE.md), 2 × 150 EUR + 21% ->
„Emite factură” -> Închidere lună 08/2026 -> „Reevaluare valută” (butonul e mereu acolo): factura nu intră, cu motivul „nota ei de
contare e ciornă” -> se validează nota de contare (acțiunea „Validează” din Registrul jurnal, pe ruta ei) -> Închidere lună: „Ce oprește
închiderea” spune că soldurile în valută nu sunt reevaluate -> „Reevaluare valută”: partenerul, 4111, 363,00 EUR, cursul din evidență
5,2534, cursul BNR 5,2586 din 31.08.2026, diferența 1,89 pe 765 -> „Generează nota” -> nota (4111 = 765 1,89 lei), ciornă.

Temei: CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1) — factura din 26.08 ia cursul comunicat în ziua anterioară (25.08.2026: 5,2534);
OMFP 1802/2014 pct.325 alin.(1)–(2) lit.b — reevaluarea la cursul comunicat în ultima zi bancară a lunii (31.08.2026: 5,2586). Ambele
cursuri sunt în cache-ul bazei de test (nicio cerere la BNR)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, PRODUS, _api, _deschide_emiterea, _ok

ZI = _dt.date(2026, 8, 26)


@pytest.fixture(scope="module")
def firma_val_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_val(patron, firma_val_noua):
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_val_noua)
    return firma_val_noua


def _emite_eur_din_ecran(patron, f):
    """Factura EUR emisă din formularul de emitere, ca un contabil: data, clientul, linia, moneda, „Emite factură”."""
    _deschide_emiterea(patron, f["nume"])
    pg = patron.pg
    pg.fill("#em-data", ZI.isoformat())
    pg.dispatch_event("#em-data", "change")
    for sel, v in CLIENT.items():
        pg.fill(sel, v)
    pg.fill("#em-l0-descriere", PRODUS)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value === '21'", timeout=20000)
    pg.fill("#em-l0-pret_unitar", "150")
    pg.fill("#em-l0-cantitate", "2")
    pg.select_option("#em-moneda", "EUR")
    # CF art.290 alin.(2) + HG 1/2016 pct.35 alin.(1): cursul comunicat în ziua ANTERIOARĂ facturii (25.08.2026)
    pg.wait_for_function("() => (document.querySelector('#em-valuta') || {innerText: ''}).innerText.includes('din 25.08.2026')",
                         timeout=20000)
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
    return fid


def _inchidere(patron, f, an, luna, asteapta):
    """Închidere lună, de la luna curentă înapoi până la `luna/an`, până apare `asteapta` în controalele lunii."""
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector(".fereastra:last-of-type #il-prev", timeout=30000)
    for _ in range((AZI.year * 12 + AZI.month) - (an * 12 + luna)):
        pg.click(".fereastra:last-of-type #il-prev")
    pg.wait_for_function("(l) => document.querySelector('.fereastra:last-of-type .pf-intro').innerText.includes(l)",
                         arg="%02d/%d" % (luna, an), timeout=60000)
    pg.wait_for_function("(t) => (document.querySelector('.fereastra:last-of-type #il-controale') || {innerText: ''}).innerText.includes(t)",
                         arg=asteapta, timeout=60000)
    pg.wait_for_selector(".fereastra:last-of-type #il-reevaluare", timeout=60000)
    return pg


def _reevaluare(pg):
    pg.click(".fereastra:last-of-type #il-reevaluare")
    pg.wait_for_selector(".fereastra:last-of-type #rv-genereaza", timeout=60000)


def test_def_429_inchiderea_propune_reevaluarea_si_genereaza_nota(patron, firma_val):
    f = firma_val
    s = f["schema"]
    fid = _emite_eur_din_ecran(patron, f)
    patron.captura("emisa")
    r = sql('SELECT moneda, curs_bnr::text, data_curs::text, total_lei::text FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0]
    assert r == ("EUR", "5.2534", "2026-08-25", "1906.98"), r   # 363 EUR x 5,2534 = 1.906,98 lei (CF art.290 + HG 1/2016 pct.35)
    # contarea, cum o scrie aplicația la emitere: ciornă — exact cazul F1 de pe producție
    (nid, st), = sql('SELECT id, status FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\'' % s, (fid,))
    assert st == "ciorna", st
    pg = _inchidere(patron, f, 2026, 8, "ciorn")
    assert "nu sunt reevaluate" not in pg.inner_text(".fereastra:last-of-type #il-controale")
    _reevaluare(pg)
    caseta = pg.inner_text(".fereastra:last-of-type #rv-neincluse")
    assert "DANTE INTERNATIONAL SA" in caseta and "nota ei de contare e ciornă" in caseta, caseta   # spus, nu sărit tăcut
    patron.captura("neinclusa_ciorna")
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {}), "validarea contării")
    pg = _inchidere(patron, f, 2026, 8, "nu sunt reevaluate")
    assert "buton-primar" in pg.get_attribute(".fereastra:last-of-type #il-reevaluare", "class")
    patron.captura("inchidere")
    _reevaluare(pg)
    rand = pg.inner_text(".fereastra:last-of-type #rv-tabel tr:has-text('DANTE INTERNATIONAL SA')")
    # OMFP 1802/2014 pct.325 alin.(1): 363 EUR x 5,2586 = 1.908,87 lei; 1.908,87 - 1.906,98 = 1,89 -> 765 (creanța crește)
    for x in ("4111", "363,00", "5,2534", "1.906,98", "5,2586", "31.08.2026", "1,89", "765"):
        assert x in rand, (x, rand)
    patron.captura("propunere")
    pg.click(".fereastra:last-of-type #rv-genereaza")
    # [lotul 11, 8c] confirmarea pe drumul unic: caseta verde, cu rândurile notei citite din Registrul jurnal („debit = credit · sumă”)
    pg.wait_for_selector(".fereastra:last-of-type #rv-mesaj .caseta-ok .cok-linii", timeout=60000)
    mesaj = pg.inner_text(".fereastra:last-of-type #rv-mesaj")
    patron.captura("nota")
    assert "Nota de reevaluare" in mesaj and "= 765 · 1,89 lei" in mesaj, mesaj
    assert pg.is_disabled(".fereastra:last-of-type #rv-genereaza")
    note = sql('SELECT i.status, l.cont_debit, l.cont_credit, l.suma::text, l.partener_cui FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.descriere LIKE 'Reevaluare valută la 31.08.2026%%%%'" % (s, s))
    assert [(n[0], n[2], n[3], n[4]) for n in note] == [("ciorna", "765", "1.89", "14399840")], note   # R36: ciornă, partenerul pe rând
    assert sql('SELECT partener, sold_valuta::text FROM "%s".reevaluari_valuta WHERE data = \'2026-08-31\'' % s) == [("14399840", "363.00")]
