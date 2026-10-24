# -*- coding: utf-8 -*-
"""Lotul 12, pachetul cx5: testele de capăt la capăt pentru C154 și C155 — prestarea intracomunitară de servicii a firmei NEPLĂTITOARE de
TVA înregistrate în scopuri de TVA după CF art.317 (forma firmei de test F3), emisă din „Emite factură”.

  · C154 — serviciul emis către clientul din DE intra în D390 ca livrare intracomunitară de bunuri (L), nu ca prestare (P): liniile
    neplătitorului poartă categoria regimului special (O), fără axă, iar factura rămânea fără axa bunuri / servicii. Acum axa vine din
    felul liniei (contul de venit 704, `categorii_tva.axa_neplatitor`) — CF art.325 alin.(1) lit.c.
  · C155 — Control fiscal nu arăta D390 datorat pe luna cu prestarea: calendarul neplătitorului art.317 lua faptul D301 (numai achizițiile
    de bunuri primite). Acum faptul e al D390-ului lunii (`control_incrucisat.d390_luni_neplatitor`) — CF art.325 alin.(1) și alin.(2).

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`), pregătite pe drumul ecranelor (`pregateste_firma` +
Date firmă + Vector fiscal, `e2e_lot12_cx3._neplatitor_art317`). Factura se datează în luna încheiată (`conftest.perioada_incheiata`):
D390 se generează numai pe o lună încheiată (383), iar termenul ei (25 ale lunii de azi) e în fereastra Control fiscal. VIES e servit de
plasă (`<ICONTA_ANAF_SIMULAT>/vies.json`, codul DE811907980 al probei R187 / C78 / C110). Nicio scriere SQL: `sql` doar citește."""
import pytest

from conftest import alege_perioada, alege_tipul, firma_noua, perioada_incheiata, sql

COD_CLIENT_IC = "DE811907980"
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=10)
SERVICIU = "Servicii de consultanta IT E2E C154"   # felul din denumire („servici” -> contul 704), cum îl scrie contabilul
_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_cx5():
    for f in firma_noua():
        yield f


def _emite_prestarea_ic(patron, f):
    """Emite factură, pe ecran: clientul german (cod de TVA verificat în VIES), o linie de servicii de 500 lei — cota 0% fără listă de
    categorii (neplătitorul, CF art.310 alin.(10) lit.b) —, data în luna încheiată -> „Emite factură”. Întoarce id-ul facturii noi."""
    from e2e_bloc_a import _deschide_emiterea
    s = f["schema"]
    inainte = {r[0] for r in sql('SELECT id FROM "%s".facturi' % s)}
    _deschide_emiterea(patron, f["nume"])
    pg = patron.pg
    pg.fill("#em-cui", COD_CLIENT_IC)
    pg.click("#em-verifica")
    pg.wait_for_function("() => document.querySelector('#em-tara').value === 'DE'", timeout=20000)
    pg.fill("#em-nume", "KUNDE E2E GMBH")
    pg.fill("#em-adresa", "Unter den Linden 1")
    pg.fill("#em-oras", "Berlin")
    pg.fill("#em-data", ZI.isoformat())
    pg.fill("#em-l0-descriere", SERVICIU)
    # la neplătitor cota nu e o listă: e textul „0%” (`emitere_ecran.randLinie`, `<span id="em-l0-cota">`), pus fără potrivire (CF art.310)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').textContent.trim() === '0%'", timeout=20000)
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "500")
    assert pg.locator("#em-l0-categorie").count() == 0, "neplătitorul nu alege categoria de TVA (vine din regimul firmei)"
    patron.captura("emitere")
    pg.wait_for_function("() => !document.querySelector('#em-emite').disabled", timeout=20000)
    pg.click("#em-emite")
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=60000)
    noi = [r[0] for r in sql('SELECT id FROM "%s".facturi ORDER BY id' % s) if r[0] not in inainte]
    assert len(noi) == 1, noi
    return noi[0]


def test_def_c154_serviciul_ic_al_neplatitorului_art317_intra_in_d390_ca_prestare(patron, firma_cx5):
    """C154. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Facturi -> Emite factură -> client DE811907980 (VIES valid), linia
    „Servicii de consultanta IT …”, 500 lei, 0% -> „Emite factură” -> Declarații -> D390, luna facturii -> „Continuă”: în „Clasificare
    intracomunitară” operațiunea din factură e „Servicii prestate (P)”, 500 lei; în bază factura are axa „servicii”, linia contul 704.
    Înainte: „Livrare bunuri (L)” (factura fără axă, D390 lua implicitul bunuri).
    MUTAȚIA (`mut_lot12_cx5.json`): axa derivată din felul liniilor scoasă din `facturi_api.creeaza_factura` -> operațiunea iese L -> ROȘU."""
    from e2e_bloc_c import _deschide
    from e2e_lot12_cx3 import _neplatitor_art317
    f = firma_cx5
    s = f["schema"]
    _neplatitor_art317(patron, f)
    fid = _emite_prestarea_ic(patron, f)
    assert sql('SELECT cont_venit FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [("704",)]
    # CF art.325 alin.(1) lit.c: prestarea art.278 alin.(2) a înregistratului art.317 intră în D390 — axa „servicii” de pe document (P)
    assert sql('SELECT axa_ic, tert_tara FROM "%s".facturi WHERE id = %%s' % s, (fid,)) == [("servicii", "DE")]
    pg = patron.pg
    _deschide(patron, f["nume"], "declaratii", "#dec-tip")
    alege_tipul(pg, "d390")
    pg.wait_for_selector("#dec-an", timeout=10000)
    alege_perioada(pg, LUNA.an, LUNA.luna)
    pg.click("#dec-continua")
    pg.wait_for_selector("#dec-d390-clasif .dec-recl-rand", timeout=90000)
    patron.captura("d390_clasificare")
    randuri = pg.locator("#dec-d390-clasif .dec-recl-rand")
    assert randuri.count() == 1, randuri.count()
    assert pg.input_value("#dec-d390-clasif select.dec-recl") == "P"
    assert pg.get_attribute("#dec-d390-clasif select.dec-recl", "data-cod") == COD_CLIENT_IC[2:]
    assert " ".join(pg.inner_text("#dec-d390-clasif .dec-recl-suma").split()) == "500,00 lei"


def test_def_c155_luna_cu_prestarea_ic_e_d390_datorat_in_control_fiscal(patron, firma_cx5):
    """C155. Pașii: firmă neplătitoare de TVA, înregistrată art.317 -> Emite factură: prestarea de servicii către clientul din DE în luna
    încheiată -> Control fiscal -> detaliul firmei: D390 pe luna facturii apare (rândul `d390-<an>-<luna>`), cu faptul pe care se
    sprijină: „operațiuni intracomunitare înregistrate în LL/AAAA” (CF art.325 alin.(1) lit.c, alin.(2)). Înainte: niciun rând D390 —
    calendarul lua numai achizițiile de bunuri primite (faptul D301).
    MUTAȚIA (`mut_lot12_cx5.json`): calendarul D390 al neplătitorului înapoi pe faptul D301 (`d301_luni_operatiuni | d301_luni_facturi_ic`)
    -> rândul lipsește -> ROȘU."""
    from e2e_bloc_f import _detaliu_fiscal
    from e2e_lot12_cx3 import _neplatitor_art317
    f = firma_cx5
    _neplatitor_art317(patron, f)
    _emite_prestarea_ic(patron, f)
    pg = patron.pg
    _detaliu_fiscal(patron, f["nume"])
    patron.captura(intreaga=True)
    rand = _F + ".cf-decl-item[data-cheie='d390-%d-%d']" % (LUNA.an, LUNA.luna)
    assert pg.locator(rand).count() == 1, "D390 %02d/%d lipsește din Control fiscal" % (LUNA.luna, LUNA.an)
    temei = [" ".join(t.split()) for t in pg.locator(rand + " .cf-incr-temei").all_inner_texts()]
    fapt = "operațiuni intracomunitare înregistrate în %02d/%d" % (LUNA.luna, LUNA.an)
    # rândul datorat poartă ca motiv faptul pe care se sprijină (`control_fiscal_api._clasifica`; dinaintea preluării, lângă motivul ei)
    assert any(fapt in t for t in temei), temei
