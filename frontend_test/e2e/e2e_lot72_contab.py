# -*- coding: utf-8 -*-
"""Lotul 7, comanda 7.2 (Costin 17.10.2026, verbatim în DECIZII „Comanda 7.2”): contabilitatea — 302, 309, 310, 311, 312, 314 — pe
aplicația din index, pe baza de TEST, pe firma nouă a fișierului (`firma_e2e`)."""
import datetime as _dt
import json
import time

from conftest import sql
from e2e_bloc_a import AZI, CLIENT, _api, _card, _ok, emite_api, pregateste_firma


def _nota(e, firma, data, descriere, doc, deb, cre, suma):
    return _ok(_api(e, "POST", "/tenants/%d/jurnal" % firma["tenant_id"], {"data": data, "descriere": descriere, "document_ref": doc,
                                                                        "linii": [{"debit": deb, "credit": cre, "suma": suma}]}), "nota")["id"]


def _valideaza(e, firma, nid):
    _ok(_api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid), {}), "validarea notei")


def _nr(firma, nid):
    r = sql('SELECT nr_curent FROM "%s".registru_jurnal_numere WHERE inregistrare_id = %%s' % firma["schema"], (nid,))
    return r[0][0] if r else None


def test_def_302_numarul_notei_validate_nu_se_schimba(patron, firma_e2e):
    """302. „Nr. crt.” se dădea pe an, în ordinea datelor, la fiecare citire: o notă nouă cu o dată mai veche muta numărul notelor validate
    („nr. crt. 25” a apărut la două note).
    Pașii: o notă de azi, validată -> are numărul N în Registrul jurnal; o notă cu data de ieri, ciornă -> în Registrul jurnal n-are
    număr, iar nota de azi păstrează N; nota de ieri se validează -> primește N+1; nota de azi rămâne N."""
    pregateste_firma(patron, firma_e2e)
    ieri = (AZI - _dt.timedelta(days=1)) if AZI.day > 1 else AZI
    a = _nota(patron, firma_e2e, AZI.isoformat(), "Încasare A 302", "CH-A302", "5311", "4111", 10)
    _valideaza(patron, firma_e2e, a)
    n = _nr(firma_e2e, a)
    assert n, "nota validată are număr în Registrul jurnal"
    b = _nota(patron, firma_e2e, ieri.isoformat(), "Încasare B 302", "CH-B302", "5311", "4111", 20)
    assert _nr(firma_e2e, b) is None and _nr(firma_e2e, a) == n, "ciorna n-are număr; nota validată nu se mută"
    patron.firma(firma_e2e["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg = patron.pg
    pg.wait_for_selector("[data-nota-id='%d']" % b, timeout=20000)
    assert ("Nr. crt. %d" % n) in pg.inner_text("[data-nota-id='%d'] .pf-frand-nume" % a)
    assert "Nr. crt." not in pg.inner_text("[data-nota-id='%d'] .pf-frand-nume" % b), "ciorna n-are număr"
    patron.captura("ciorna_fara_numar")
    _valideaza(patron, firma_e2e, b)
    assert (_nr(firma_e2e, a), _nr(firma_e2e, b)) == (n, n + 1)
    patron.firma(firma_e2e["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg.wait_for_selector("[data-nota-id='%d']" % b, timeout=20000)
    assert ("Nr. crt. %d" % (n + 1)) in pg.inner_text("[data-nota-id='%d'] .pf-frand-nume" % b)
    assert ("Nr. crt. %d" % n) in pg.inner_text("[data-nota-id='%d'] .pf-frand-nume" % a)
    patron.captura("numerele_pastrate")


def test_def_c48_avansul_pentru_servicii_se_inregistreaza_pe_4092(patron, firma_e2e):
    """C48. Planul firmelor noi n-avea 4092 / 4093 / 4094, deși aplicația le propune singură (avansul pentru servicii, 312): nota pe 4092
    era refuzată „cont inexistent”.
    Pașii: firmă nouă -> notă „avans furnizor servicii” 4092 = 5311, validată -> Registrul jurnal: nota, cu 4092 pe linie."""
    pregateste_firma(patron, firma_e2e)
    nid = _nota(patron, firma_e2e, AZI.isoformat(), "Avans furnizor servicii C48", "DP-C48", "4092", "5311", 50)
    _valideaza(patron, firma_e2e, nid)
    patron.firma(firma_e2e["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg = patron.pg
    pg.wait_for_selector("[data-nota-id='%d']" % nid, timeout=20000)
    rand = pg.inner_text("[data-nota-id='%d']" % nid)
    patron.captura("nota_pe_4092")
    assert "4092" in rand and "5311" in rand, rand


MT940 = """:20:EXTRAS{tag}
:25:RO49AAAA1B31007593840000
:28C:00010/001
:60F:C{ziua}RON10000,00
:61:{ziua}{zz}C242,00NTRFNONREF
:86:Incasare DANTE INTERNATIONAL SA CUI 14399840 factura {tag}
:61:{ziua}{zz}D12,50NCHGNONREF
:86:Comision administrare cont {tag}
:62F:C{ziua}RON10229,50
"""


def test_def_309_banca_contata_la_validare_comisionul_si_motivul_pe_romaneste(patron, firma_e2e):
    """309. Bancă: „Contat ✓” cât nota e încă la validare; „match exact pe o factura”; comisionul roșu „Fără potrivire”.
    Pașii: extrasul cu o încasare de la client (factura lui de 242,00) și un comision -> comisionul arată „Notă propusă 627 = 5121”, nu
    „Fără potrivire”; încasarea „Contează” -> rândul spune „Contată, nota e la validare”; un rând importat înainte de reparație, cu motivul
    vechi în engleză, se citește „potrivire exactă pe o factură”."""
    from e2e_lot6 import _incarca
    pregateste_firma(patron, firma_e2e)
    emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E 309", "cantitate": 1, "um": "buc", "pret_unitar": 200.0, "cota_tva": 21,
                                         "cota_propusa": 21, "articol_id": None}])
    tag = "E2E309%d" % (time.time() % 100000)
    s = firma_e2e["schema"]
    patron.firma(firma_e2e["nume"])
    _card(patron, "banca", "#bk-fisier")
    _incarca(patron, "extras_%s.sta" % tag, MT940.format(tag=tag, ziua=AZI.strftime("%y%m%d"), zz=AZI.strftime("%m%d")), "importate")
    pg = patron.pg
    comision = pg.locator(".pf-frand", has_text="Comision administrare cont " + tag)
    assert "Notă propusă 627 = 5121" in comision.inner_text() and "Fără potrivire" not in comision.inner_text(), comision.inner_text()
    lid = sql('SELECT id FROM "%s".extras_linii WHERE descriere LIKE %%s AND tip = \'incasare\'' % s, ("%" + tag,))[0][0]
    r = _api(patron, "POST", "/tenants/%d/banca/reconciliere/%d/conteaza" % (firma_e2e["tenant_id"], lid), {})
    assert r["status"] == 200, r
    sql('UPDATE "%s".extras_linii SET alocari = jsonb_set(alocari, \'{motiv}\', \'"match exact pe o factura"\') WHERE id = %%s' % s, (lid,))
    patron.firma(firma_e2e["nume"])
    _card(patron, "banca", "#bk-fisier")
    incasare = pg.locator(".pf-frand", has_text="Incasare DANTE INTERNATIONAL SA CUI 14399840 factura " + tag)
    t = incasare.inner_text()
    patron.captura("banca")
    assert "Contată, nota e la validare" in t and "Contat ✓" not in t, t
    assert sql('SELECT alocari->>\'motiv\' FROM "%s".extras_linii WHERE id = %%s' % s, (lid,)) == [("match exact pe o factura",)]
    linii = _api(patron, "GET", "/tenants/%d/banca/reconciliere" % firma_e2e["tenant_id"], None)["json"]["linii"]
    assert [x["alocari"]["motiv"] for x in linii if x["id"] == lid] == ["potrivire exactă pe o factură"]


def test_def_310_casa_spune_de_ce_lipseste_factura_si_are_renunta(patron, firma_e2e):
    """310. Casă: factura nu apărea la facturile deschise din cauza încasării bancare aflate la validare, fără explicație; „Dispoziție
    nouă” n-avea Renunță.
    Pașii: o factură încasată printr-o notă bancară ciornă (5121 = 4111, legată de factură) -> Casă -> Dispoziție nouă, încasare de la
    client, CUI-ul clientului: factura nu e în listă și rândul spune de ce („… nu e în listă: e încasată printr-o notă care așteaptă
    validarea (din …) …”); „Renunță” închide formularul."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E 310", "cantitate": 1, "um": "buc", "pret_unitar": 200.0, "cota_tva": 21,
                                             "cota_propusa": 21, "articol_id": None}])
    s = firma_e2e["schema"]
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, status, factura_id, document_ref) VALUES (%%s, \'Incasare banca E2E 310\', '
              '\'ciorna\', %%s, \'EXTRAS E2E 310\') RETURNING id' % s, (AZI.isoformat(), f["factura_id"]))[0][0]
    sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'5121\', \'4111\', 242)' % s, (nid,))
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "242")
    pg.fill("#c-cui", CLIENT["#em-cui"])
    rand = pg.locator(".c-fact-asteptare", has_text=f["numar"] + " din ")
    rand.first.wait_for(timeout=20000)
    t = rand.first.inner_text()
    patron.captura("factura_in_asteptare")
    assert t.startswith(f["numar"]) and "e încasată printr-o notă care așteaptă validarea" in t and "(din " in t, t
    assert pg.locator("[data-cf='%s']" % f["factura_id"]).count() == 0
    pg.click("#c-renunta")
    assert pg.locator("#c-zona").is_hidden()
    patron.captura("renunta")


def test_def_311_asistentul_cu_poate_pregati_genereaza_amortizarea(browser, request, patron, firma_e2e):
    """311. Generarea amortizării (lunară și restantă) cerea „Poate valida”; decizia: „Poate pregăti”, validarea rămâne la „Poate valida”.
    Pașii: Ana cu „Poate pregăti” (fără „Poate valida”), pe firma ei: Închidere lună -> luna trecută -> „Generează amortizarea restantă”
    -> notele se generează (ciorne); validarea uneia îi e refuzată (403)."""
    from e2e_bloc_a import cont_asistent, ecran_cont
    from e2e_bloc_e import _la_luna, _mf
    f = firma_e2e
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    m = AZI.year * 12 + AZI.month - 1 - 3
    mid = _mf(f, "MF311", "3000", 30, _dt.date(m // 12, m % 12 + 1, 10).isoformat())
    try:
        with cont_asistent(firme=(f["tenant_id"],)) as a, ecran_cont(browser, request, a["email"]) as e:
            e.firma(f["nume"])
            e.pg.click("#fa-inchidere")
            e.pg.wait_for_selector("#il-prev", timeout=30000)
            _la_luna(e, "#il-prev", trecuta.year, trecuta.month)
            e.pg.wait_for_selector(".fereastra:last-of-type #il-amort-restanta", timeout=60000)
            e.pg.click(".fereastra:last-of-type #il-amort-restanta")
            e.pg.wait_for_function("() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-mesaj') || {innerText: ''})"
                                   ".innerText.includes('de validat')", timeout=60000)
            e.captura("generata_de_asistent")
            note = sql('SELECT id, status FROM "%s".inregistrari WHERE sursa = \'amortizare\'' % f["schema"])
            assert note and all(st == "ciorna" for _i, st in note), note
            r = _api(e, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], note[0][0]), {})
            assert r["status"] == 403, r
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE sursa = \'amortizare\' AND status = \'ciorna\'' % f["schema"])
        sql('DELETE FROM "%s".mijloace_fixe WHERE id = %%s' % f["schema"], (mid,))


def test_def_312_dupa_generare_de_validat_iar_401_debitor_spre_4091_4092(patron, firma_e2e):
    """312. După „Generează amortizarea restantă” motivul rămânea „neînregistrată”, butonul activ, iar a doua apăsare spunea iar „8 note
    generate”; la 401 debitor se propunea 409.
    Pașii: Închidere lună -> luna trecută (mijloc fix fără amortizare) -> „Generează amortizarea restantă” -> „N note de amortizare
    generate, de validat”; după redesenare motivele spun „generată …, de validat”, iar butonul nu mai e; o plată către furnizor fără
    factură (401 debitor) -> semnalul propune 4091 / 4092, nu 409."""
    from e2e_bloc_e import _card as _card_e, _la_luna, _mf
    f = firma_e2e
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    m = AZI.year * 12 + AZI.month - 1 - 3
    mid = _mf(f, "MF312", "3000", 30, _dt.date(m // 12, m % 12 + 1, 10).isoformat())
    plata = _nota(patron, f, trecuta.isoformat(), "Plata furnizor fara factura E2E 312", "OP-312", "401", "5121", 500)
    _valideaza(patron, f, plata)
    pg = patron.pg
    try:
        _card_e(patron, f, "inchidere", "#il-prev")
        _la_luna(patron, "#il-prev", trecuta.year, trecuta.month)
        pg.wait_for_selector(".fereastra:last-of-type #il-amort-restanta", timeout=60000)
        zona = pg.inner_text(".fereastra:last-of-type #il-controale")
        assert "4091 pentru bunuri de natura stocurilor, 4092 pentru servicii" in zona and "(409)" not in zona, zona
        pg.click(".fereastra:last-of-type #il-amort-restanta")
        pg.wait_for_function("() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-mesaj') || {innerText: ''})"
                             ".innerText.includes('de validat')", timeout=60000)
        mesaj = pg.inner_text(".fereastra:last-of-type #il-mesaj")
        assert "note de amortizare generate, de validat" in mesaj, mesaj
        pg.wait_for_function("() => !document.querySelector('.fereastra:last-of-type #il-amort-restanta')", timeout=30000)
        zona = pg.inner_text(".fereastra:last-of-type #il-controale")
        patron.captura("de_validat")
        assert "e generată pe contul 2813" in zona and "de validat" in zona and "nu e înregistrată" not in zona, zona
        a2 = _api(patron, "POST", "/tenants/%d/amortizare/restanta?an=%d&luna=%d" % (f["tenant_id"], trecuta.year, trecuta.month), {})
        assert a2["json"]["generate"] == 0 and a2["json"]["deja_generate"] >= 1, a2
    finally:
        sql('DELETE FROM "%s".inregistrari WHERE sursa = \'amortizare\' AND status = \'ciorna\'' % f["schema"])
        sql('DELETE FROM "%s".mijloace_fixe WHERE id = %%s' % f["schema"], (mid,))


def test_def_314_povestea_aprobata_pe_alte_cifre_e_depasita_si_nu_pleaca(patron, firma_e2e):
    """314. Povestea aprobată rămânea „gata de trimis” după ce cifrele lunii s-au schimbat.
    Pașii: Pachet lunar -> luna curentă: povestea aprobată (cifrele de acum) -> „aprobată ✓ — gata de trimis”; o factură nouă, cu nota
    validată, în lună -> la redeschidere: „aprobată, dar depășită”, „Trimite” inactiv cu motivul; trimiterea cerută direct e refuzată."""
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    f1 = emite_api(patron, firma_e2e)
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s' % firma_e2e["schema"], (f1["factura_id"],)):
        _valideaza(patron, firma_e2e, nid)
    rz = _ok(_api(patron, "GET", "/pachete/%d/rezumat?an=%d&luna=%d" % (tid, AZI.year, AZI.month), None), "rezumat")
    text = "În %s firma a avut venituri de %s lei și cheltuieli de %s lei." % (
        rz["luna_nume"], ("%.2f" % rz["venituri"]).replace(".", ","), ("%.2f" % rz["cheltuieli"]).replace(".", ","))
    r = _api(patron, "POST", "/pachete/%d/poveste/aproba?an=%d&luna=%d" % (tid, AZI.year, AZI.month), {"text": text})
    assert r["status"] == 200, r
    assert _api(patron, "GET", "/pachete/%d/poveste?an=%d&luna=%d" % (tid, AZI.year, AZI.month), None)["json"]["depasita"] is False  # AZI-dat-de-test: luna cerută
    f2 = emite_api(patron, firma_e2e)
    for (nid,) in sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s' % firma_e2e["schema"], (f2["factura_id"],)):
        _valideaza(patron, firma_e2e, nid)
    p = _api(patron, "GET", "/pachete/%d/poveste?an=%d&luna=%d" % (tid, AZI.year, AZI.month), None)["json"]
    assert p["depasita"] is True and "depășită" in p["motiv_depasita"], p
    s = firma_e2e["schema"]
    era = sql('SELECT email FROM "%s".firma_profil LIMIT 1' % s)
    sql('UPDATE "%s".firma_profil SET email = \'client-314@prisma-cont.test\'' % s)   # altfel refuzul „fără email” vine înainte
    try:
        t = _api(patron, "POST", "/pachete/%d/trimite?an=%d&luna=%d" % (tid, AZI.year, AZI.month), {})
    finally:
        sql('UPDATE "%s".firma_profil SET email = %%s' % s, (era[0][0] if era else None,))
    assert t["status"] == 400 and "depășită" in json.dumps(t["json"], ensure_ascii=False), t
    from e2e_bloc_a import _deschide_povestea, _pachet
    _pachet(patron, firma_e2e, AZI.year, AZI.month)
    _deschide_povestea(patron)
    pg = patron.pg
    pg.wait_for_function("() => (document.querySelector('#pacm-motiv-trimite') || {textContent: ''}).textContent.includes('depășită')",
                         timeout=30000)
    patron.captura("depasita")
    assert pg.locator("#pacm-trimite").is_disabled()
