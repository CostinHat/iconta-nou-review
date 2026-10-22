# -*- coding: utf-8 -*-
"""Lotul 11, comanda Costin 11.3 (verbatim, DECIZII „Comanda 11.3”):
  pct.2 — 455 (prioritar): „casa F1 are două solduri în același moment: 294 la refuzul plății, 42 în registrul de casă. Registrul de casă,
          contul 5311 și verificarea de sold negativ folosesc aceeași cifră, din aceeași sursă.”
  pct.3 — 456: „încasarea în numerar de la o firmă se salvează fără chitanță. Emite automat chitanța, cu seria firmei și PDF.”

Temei: OMFP 2634/2015 anexa 2 (anaf_surse/omfp_2634_2015_anexa2_norme_specifice.txt) — Registrul de casă (14-4-7A): „document de
stabilire, la sfârșitul fiecărei zile, a soldului de casă [...] Registrul de casă se întocmește zilnic, pe baza documentelor justificative
de încasări și plăți.”; Chitanța (14-4-1): „documente justificative de înregistrare în registrul de casă [...] a încasărilor și plăților
efectuate în numerar [...] Se întocmește pentru fiecare sumă încasată”; „În condițiile utilizării aparatelor de marcat electronice fiscale
[...] documentul în baza căruia se înregistrează în contabilitate veniturile aferente încasărilor zilnice este Raportul fiscal de închidere
zilnică”.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_e2e`, `firma_noua` + `pregateste_firma`).
DATELE DE PORNIRE scrise direct (declarate): la 456, seria chitanțelor scoasă din Date firmă — aplicația nu lasă seria ștearsă după ce a fost
stabilită, iar firma nouă o primește din `pregateste_firma`; e singura cale spre starea „firmă fără serie”. Raportul Z intră pe ruta pe care
o cheamă ecranul HoReCa („Generează notă”, `POST /horeca/raport-z`). Clientul DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control
verificată cu algoritmul din CLAUDE.md."""
import base64
import datetime as _dt
import io
import os
import sys

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import AZI, CLIENT, _api, _ok, emite_api, pregateste_firma

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def _bani(v):
    """1234.5 -> „1.234,50” (formatul ecranului, `bani` din api.js)."""
    s = "%.2f" % float(v)
    i, z = s.split(".")
    return "{:,}".format(int(i)).replace(",", ".") + "," + z


def _casa(e, firma):
    e.firma(firma["nume"])
    e.pg.click("#fa-casa")
    e.pg.wait_for_selector("#c-toggle", timeout=20000)


def _dispozitie(pg, cat, suma, doc=None, cui=None, factura_id=None):
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", cat)
    pg.fill("#c-suma", str(suma))
    if doc:
        pg.fill("#c-doc", doc)
    if cui:
        pg.fill("#c-cui", cui)
        pg.dispatch_event("#c-campuri", "change")
    if factura_id:
        pg.wait_for_selector("#c-facturi [data-cf='%d']" % factura_id, timeout=20000)
        pg.check("#c-facturi [data-cf='%d']" % factura_id)
    pg.click("#c-adauga")


def _pdf(e, cale):
    b64 = e.pg.evaluate("""async (c) => { const t = sessionStorage.getItem('iconta_token');
        const x = await fetch(c, {headers: {Authorization: 'Bearer ' + t}}); const b = new Uint8Array(await x.arrayBuffer());
        let s = ''; b.forEach((v) => { s += String.fromCharCode(v); }); return btoa(s); }""", cale)
    return base64.b64decode(b64)


def test_def_455_registrul_si_refuzul_platii_arata_aceeasi_cifra(patron, firma_e2e):
    """455. Pașii: Casă -> „+ Dispoziție nouă”: ridicare de la bancă 242 lei -> „Adaugă” -> HoReCa: raportul Z de azi, 131 lei numerar
    -> Casă: rândul raportului Z e în registru, soldul final 373,00 -> dispoziție: depunere la bancă 400 lei -> „Adaugă” -> refuzul spune
    „în registru, e 373,00 lei” — aceeași cifră cu registrul (înainte: refuzul spunea soldul din note, registrul pe cel din dispoziții, fără
    raportul Z), iar soldul casei din `casa_sold` (sursa unică) e tot 373,00."""
    s, tid = firma_e2e["schema"], firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e)
    pg = patron.pg
    _casa(patron, firma_e2e)
    _dispozitie(pg, "ridicare_banca", "242", doc="CEC 455")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Dispoziția a fost salvată')",
                         timeout=20000)
    # raportul Z de azi, 131 lei numerar — ruta butonului „Generează notă” din HoReCa
    _ok(_api(patron, "POST", "/tenants/%d/horeca/raport-z" % tid, {"data": AZI.isoformat(), "nui": "8000000455", "nr_raport": "0455",
                                                                   "nr_bonuri": 3, "total_11": 0, "total_21": 131, "numerar": 131,
                                                                   "card": 0}), "raport Z")
    _casa(patron, firma_e2e)
    pg.wait_for_selector("#c-sold-final", timeout=20000)
    text = patron.fereastra()
    # OMFP 2634/2015 14-4-1: raportul Z e documentul încasărilor zilnice în numerar -> rând în registrul de casă (14-4-7A)
    assert "notă din raportul Z" in text and "131,00" in text, text
    sold_registru = pg.inner_text("#c-sold-final")
    assert sold_registru.startswith(_bani(373)), sold_registru
    patron.captura("registrul")
    _dispozitie(pg, "depunere_banca", "400", doc="DEP 455")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('nu încape în casă')", timeout=20000)
    refuz = patron.fereastra()
    patron.captura("refuzul")
    # 14-4-7A: un singur sold de casă la sfârșitul zilei — refuzul și registrul spun aceeași cifră
    assert "soldul casei pe %s, în registru, e %s lei" % (AZI.strftime("%d.%m.%Y"), _bani(373)) in refuz, refuz   # AZI-dat-de-test (data dispoziției, #c-data)
    from core import casa_sold as _cs, db
    with db.get_conn(s) as c, c.cursor() as cur:
        assert str(_cs.sold_inainte(cur, s, "5311", AZI + _dt.timedelta(days=1))) == "373.00"   # AZI-dat-de-test (soldul de după ziua dispozițiilor)
    assert sql('SELECT count(*) FROM "%s".casa_operatiuni WHERE categorie = %%s' % s, ("depunere_banca",)) == [(0,)]


@pytest.fixture(scope="module")
def firma_a455_ch():
    for f in firma_noua():
        yield f


def test_def_456_incasarea_facturii_din_casa_emite_chitanta_cu_seria_firmei(patron, firma_a455_ch):
    """456. Pașii: firma fără serie de chitanțe -> „Emite factură” -> Casă -> „+ Dispoziție nouă”: încasare de la client, factura bifată
    -> „Adaugă” -> refuz numit, cu „Deschide Date firmă”, nimic scris -> seria scrisă în Date firmă -> aceeași încasare -> „Chitanța E2ECH
    nr. 1 a fost emisă”; rândul are „PDF chitanță”, iar PDF-ul e chitanța E2ECH nr. 1, cu clientul și suma -> încasarea fără factură
    (avansul de la client) rămâne „fără chitanță”, numită pe rând (decizie cerută pentru partea fără factură)."""
    f = firma_a455_ch
    s, tid = f["schema"], f["tenant_id"]
    pregateste_firma(patron, f)
    sql('UPDATE "%s".firma_profil SET serie_chitanta = NULL' % s)   # date-de-pornire: firma fără serie de chitanțe (`pregateste_firma` o completează)
    fac = emite_api(patron, f)
    fid = fac["factura_id"]
    (total,) = sql('SELECT total::text FROM "%s".facturi WHERE id = %%s' % s, (fid,))[0]
    pg = patron.pg
    _casa(patron, f)
    _dispozitie(pg, "incasare_client", total, cui=CLIENT["#em-cui"], factura_id=fid)
    pg.wait_for_selector(".fereastra:last-of-type [data-ecran-destinatie='date_firma']", timeout=20000)
    assert "n-are serie pentru chitanțe" in patron.fereastra(), patron.fereastra()
    patron.captura("fara_serie")
    assert sql('SELECT (SELECT count(*) FROM "%s".casa_operatiuni), (SELECT count(*) FROM "%s".chitante)' % (s, s)) == [(0, 0)]
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"serie_chitanta": "E2ECH"}), "seria chitanțelor")
    _casa(patron, f)
    _dispozitie(pg, "incasare_client", total, cui=CLIENT["#em-cui"], factura_id=fid)
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Chitanța E2ECH nr. 1 a fost emisă')",
                         timeout=20000)
    pg.wait_for_selector(".fereastra:last-of-type [data-chpdf]", timeout=20000)
    patron.captura("chitanta_emisa")
    ((cid, serie, nr, f_id, op_id, anulata),) = sql('SELECT id, serie, numar, factura_id, casa_operatiune_id, anulata FROM "%s".chitante' % s)
    assert (serie, nr, f_id, anulata) == ("E2ECH", 1, fid, False)
    assert sql('SELECT document FROM "%s".casa_operatiuni WHERE id = %%s' % s, (op_id,)) == [("E2ECH-1",)]
    import pypdf
    text = "".join(p.extract_text() for p in pypdf.PdfReader(io.BytesIO(_pdf(patron, "/tenants/%d/chitante/%d/pdf" % (tid, cid)))).pages)
    assert "CHITANȚĂ seria E2ECH nr. 1" in text and _bani(total) in text and "DANTE INTERNATIONAL SA" in text, text
    # încasarea fără factură: fără chitanță automată, numită pe rând
    _dispozitie(pg, "incasare_client", "50", cui=CLIENT["#em-cui"])
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('fără chitanță')", timeout=20000)
    patron.captura("avans_fara_chitanta")
