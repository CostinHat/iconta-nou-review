# -*- coding: utf-8 -*-
"""Lotul 11, subagentul x: C78 — „Livrare/prestare intracomunitară” (Operațiuni speciale, `uc_tenants.vanzare_ic`) scria DOUĂ note pe
aceeași factură (contarea făcută la emitere, 4111 = 707, și încă o notă proprie 4111 = 707): venitul și creanța ieșeau dublate.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`), pregătită pe drumul ecranelor
(`e2e_bloc_a.pregateste_firma`: Date firmă, vectorul fiscal, seria facturilor). Stocul firmei: global-valoric, pus tot prin ruta „Date
firmă” (`POST firma-profil/date`) — la cantitativ-valoric emiterea cere articolul pe linia de marfă, iar formularul livrării IC nu are
articol (consemnat separat în raportul lotului). VIES e servit de plasă pe server (`<ICONTA_ANAF_SIMULAT>/vies.json`, codul
DE811907980 — cel din proba R187 — „valid”). `sql` numai citește.

Temei: OMFP 2634/2015 anexa 1 pct.58 lit.c — „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui
document”; factura de 1.000 lei justifică 1.000 lei de venit, nu 2.000."""
import datetime as _dt
import json
import os

import pytest

from conftest import firma_noua, sql

AZI = _dt.date.today()
COD_CLIENT = "DE811907980"


@pytest.fixture(scope="module")
def firma_x_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_x(patron, firma_x_noua):
    from e2e_bloc_a import _api, _ok, _profil, pregateste_firma
    pregateste_firma(patron, firma_x_noua)
    p = _profil(firma_x_noua)
    p["metoda_stoc"] = "global_valoric"
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % firma_x_noua["tenant_id"], p), "Date firmă (stoc global-valoric)")
    d = os.environ.get("ICONTA_ANAF_SIMULAT")
    if d:   # VIES pe plasă: răspunsul „valid” al clientului german
        os.makedirs(d, exist_ok=True)
        cale = os.path.join(d, "vies.json")
        vies = json.load(open(cale, encoding="utf-8")) if os.path.exists(cale) else {}
        vies[COD_CLIENT] = {"valid": True, "nume": "KUNDE E2E GMBH", "adresa": "Berlin", "eroare": None}
        with open(cale, "w", encoding="utf-8") as f:
            json.dump(vies, f, ensure_ascii=False)
    return firma_x_noua


def _livrare(patron, firma, tip, valoare, cont):
    """Operațiuni speciale -> „Livrare/prestare intracomunitară (VIES live)” -> completează -> „Generează nota”; id-ul facturii nou emise."""
    s = firma["schema"]
    inainte = {r[0] for r in sql('SELECT id FROM "%s".facturi' % s)}
    patron.firma(firma["nume"])
    pg = patron.pg
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("[data-op]", timeout=20000)
    pg.locator("button[data-op='vanzare_ic']").click()
    pg.wait_for_selector("#op-trimite", timeout=10000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-valoare", valoare)
    pg.fill("#op-cod_tva_client", COD_CLIENT)
    pg.select_option("#op-tip", tip)
    pg.fill("#op-cont_venit", cont)
    if tip == "bunuri":
        pg.select_option("#op-dovada_transport", label="Da")
    pg.fill("#op-descriere", "Marfa IC E2E")
    pg.click("#op-trimite")
    pg.wait_for_selector("#op-mesaj .caseta-ok", timeout=30000)
    patron.captura(tip)
    noi = [r[0] for r in sql('SELECT id FROM "%s".facturi ORDER BY id' % s) if r[0] not in inainte]
    assert len(noi) == 1, noi
    return pg, noi[0]


def _notele_facturii(firma, fid):
    s = firma["schema"]
    return sql('SELECT i.id, l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s AND i.sursa = 'facturi' ORDER BY i.id, l.id" % (s, s), (fid,))


def test_def_c78_vanzarea_intracomunitara_are_o_singura_nota(patron, firma_x):
    """C78. Pașii: Operațiuni speciale -> „Livrare/prestare intracomunitară” -> Bunuri, 1.000 lei, client DE811907980 (VIES valid), cont
    707, dovada transportului: Da -> „Generează nota” -> confirmarea arată nota 4111 = 707 · 1.000,00 lei, iar factura emisă are O SINGURĂ
    notă (înainte: două, 4111 = 707 de două ori — venitul 2.000). Apoi Servicii, 704: tot o notă.
    MUTAȚIA: core/uc_tenants.py, nota proprie pusă la loc în `vanzare_ic` -> factura cu două note -> ROȘU."""
    pg, fid = _livrare(patron, firma_x, "bunuri", "1000", "707")
    t = pg.inner_text("#op-mesaj")
    assert "4111 = 707 · 1.000,00 lei" in t, t
    note = _notele_facturii(firma_x, fid)
    # OMFP 2634/2015 pct.58 lit.c: „fiecare dată înregistrată în contabilitate trebuie să se regăsească în conținutul unui document”
    assert len({n[0] for n in note}) == 1, note
    assert [(d, c, s) for _i, d, c, s in note if s != "0.00"] == [("4111", "707", "1000.00")], note
    _pg2, fid2 = _livrare(patron, firma_x, "servicii", "1000", "704")
    note2 = _notele_facturii(firma_x, fid2)
    assert len({n[0] for n in note2}) == 1 and [(d, c, s) for _i, d, c, s in note2 if s != "0.00"] == [("4111", "704", "1000.00")], note2
