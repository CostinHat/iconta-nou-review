# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.1 pct.8 (Costin 20.10.2026, verbatim în DECIZII „Comanda 10.1”): 429 — „reevaluarea lunară a soldurilor în valută
cere de mână soldul, moneda și cursul pe fiecare cont. La închiderea lunii, aplicația propune singură creanțele și datoriile în valută
neîncasate (pe factură), disponibilitățile în valută, cursul din evidență, cursul BNR din ultima zi bancară și diferența pe 665/765;
contabilul verifică și generează nota. Reevaluarea apare în «Ce oprește închiderea» când există solduri în valută.”

Temei: OMFP 1802/2014 pct.325 alin.(1) „La finele fiecărei luni, creanțele și datoriile în valută se evaluează la cursul de schimb al
pieței valutare, comunicat de Banca Națională a României din ultima zi bancară a lunii în cauză.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`), luna 08/2026: cursul BNR din
31.08.2026 (luni, ultima zi bancară a lunii) e în cache-ul bazei de test (EUR 5,2586) — ecranul nu cere BNR-ului nimic.
Legătura din „Închidere lună” (butonul `#il-reevaluare`, lângă „Ce oprește închiderea”) o pune sesiunea principală în `firme.js`."""
from conftest import sql
from e2e_bloc_a import AZI  # noqa: F401 — aceeași zi de referință ca restul plasei
from e2e_bloc_e import _card, _nota

LUNA = "2026-08"


def _factura_eur(f):
    """Factura emisă EX-429 / 10.08.2026: 1.000 EUR la cursul 4,9700 (4.970,00 lei), neîncasată; nota de contare 4111 = 707, validată."""
    s = f["schema"]
    gasit = sql('SELECT id FROM "%s".facturi WHERE serie = \'EX\' AND numar = \'429\'' % s)
    if gasit:
        return gasit[0][0]
    fid = sql('INSERT INTO "%s".facturi (numar, serie, data_emitere, total, tva, moneda, directie, status, tert_nume, curs_bnr, total_lei, '
              "tva_lei, data_curs) VALUES ('429', 'EX', '2026-08-10', 1000, 0, 'EUR', 'emisa', 'emisa', 'Client GmbH', 4.97, 4970, 0, "
              "'2026-08-07') RETURNING id" % s)[0][0]
    nid = sql('INSERT INTO "%s".inregistrari (data, factura_id, descriere, sursa, status, document_ref) VALUES (\'2026-08-10\', %%s, '
              "'Factura EX 429', 'facturi', 'ciorna', 'Factura EX 429') RETURNING id" % s, (fid,))[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'4111\', \'707\', 4970)' % s,
        (nid,))
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # [lotul 10] ciornă -> linii -> validată
    return fid


def _cont_eur(f):
    """Contul 5124.EUR („Cont BT EUR”) cu 4.950,00 lei din 05.08.2026 (o depunere de 1.000 EUR la 4,95), notă validată."""
    s = f["schema"]
    if not sql('SELECT 1 FROM "%s".plan_conturi WHERE simbol = \'5124.EUR\'' % s):
        sql('INSERT INTO "%s".plan_conturi (simbol, denumire) VALUES (\'5124.EUR\', \'Cont BT EUR\')' % s)
    if not sql('SELECT 1 FROM "%s".inregistrari_linii WHERE cont_debit = \'5124.EUR\'' % s):
        _nota(f, "2026-08-05", [{"debit": "5124.EUR", "credit": "456", "suma": 4950}], "Aport în valută E2E 429", valideaza=True,
              document_ref="Extras BT 429")


def _inchidere_august(patron, f):
    pg = patron.pg
    _card(patron, f, "inchidere", "#il-prev")
    for _ in range((AZI.year * 12 + AZI.month) - (2026 * 12 + 8)):
        pg.click(".fereastra:last-of-type #il-prev")
    pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type .pf-intro').innerText.includes('08/2026')", timeout=60000)
    pg.wait_for_function("() => document.querySelector('.fereastra:last-of-type #il-controale').innerText.includes('nu sunt reevaluate')",
                         timeout=60000)
    return pg


def test_def_429_inchiderea_propune_reevaluarea_si_genereaza_nota(patron, firma_e2e):
    """429. Pașii: factura de 1.000 EUR neîncasată și contul 5124.EUR -> Închidere lună, 08/2026: „Ce oprește închiderea” spune că soldurile
    în valută nu sunt reevaluate -> „Reevaluare valută”: factura cu 4111, 1.000,00 EUR, cursul din evidență 4,9700, cursul BNR 5,2586 din
    31.08.2026, diferența 288,60 pe 765; contul 5124.EUR cere soldul în valută -> scriu 1000 -> diferența 308,60 pe 765 -> „Generează
    nota” -> confirmarea numește nota (4111 = 765 288,60 lei; 5124.EUR = 765 308,60 lei), ciornă."""
    f = firma_e2e
    s = f["schema"]
    _factura_eur(f)
    _cont_eur(f)
    pg = _inchidere_august(patron, f)
    assert "nu sunt reevaluate" in pg.inner_text(".fereastra:last-of-type #il-controale")
    patron.captura("inchidere")
    pg.click(".fereastra:last-of-type #il-reevaluare")
    pg.wait_for_selector(".fereastra:last-of-type #rv-tabel", timeout=60000)
    fact = pg.inner_text(".fereastra:last-of-type #rv-tabel tr:has-text('Client GmbH')")
    # OMFP 1802/2014 pct.325 alin.(1): 1.000 EUR x 5,2586 = 5.258,60 lei; 5.258,60 - 4.970,00 = 288,60 -> 765 (creanța crește)
    for x in ("4111", "1.000,00", "4,9700", "5,2586", "31.08.2026", "288,60", "765"):
        assert x in fact, (x, fact)
    camp = ".fereastra:last-of-type [data-cheie='c5124.EUR'][data-camp='sold_valuta']"
    assert pg.input_value(camp) == ""
    pg.fill(camp, "1000")
    pg.dispatch_event(camp, "change")
    pg.wait_for_function("() => (document.querySelector(\".fereastra:last-of-type tr[data-cheie='c5124.EUR']\") || {innerText: ''})"
                         ".innerText.includes('308,60')", timeout=60000)
    assert "Net:" in pg.inner_text(".fereastra:last-of-type #rv-totaluri")
    patron.captura("propunere")
    pg.click(".fereastra:last-of-type #rv-genereaza")
    pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #rv-mesaj') || {innerText: ''}).innerText"
                         ".includes('a fost generată (ciornă)')", timeout=60000)
    mesaj = pg.inner_text(".fereastra:last-of-type #rv-mesaj")
    patron.captura("nota")
    assert "4111 = 765 288,60 lei" in mesaj and "5124.EUR = 765 308,60 lei" in mesaj, mesaj
    note = sql('SELECT i.status, count(l.id) FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               "WHERE i.descriere LIKE 'Reevaluare valută la 31.08.2026%%%%' GROUP BY i.id, i.status" % (s, s))
    assert note == [("ciorna", 2)], note   # R36: ciornă, o singură notă pe lună
    assert sql('SELECT count(*) FROM "%s".reevaluari_valuta WHERE data = \'2026-08-31\'' % s) == [(2,)]
