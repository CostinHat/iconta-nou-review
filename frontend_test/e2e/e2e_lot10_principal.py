# -*- coding: utf-8 -*-
"""Lotul 10 (comanda Costin 10.1, 20.10.2026, verbatim în DECIZII „Comanda 10.1”) — ce a lucrat sesiunea principală: 432 („Datorate de
firmă” marcate „înainte de preluare”) și C68 (eroarea 500 din `/eu/ciorne`). Pașii contabilului pe aplicația din index, pe baza de TEST."""
import datetime

import pytest

from conftest import firma_noua, sql


def _luna_dinainte(azi):
    return (azi.year - 1, 12) if azi.month == 1 else (azi.year, azi.month - 1)


@pytest.fixture()
def firma_preluata():
    """O firmă NOUĂ, plătitoare de TVA lunar, preluată în iConta.eu din luna CURENTĂ (Date firmă -> luna preluării)."""
    yield from firma_noua()


def test_def_432_datorate_dinaintea_preluarii_raman_marcate_separat(patron, firma_preluata):
    """432. F6 (preluată din 10/2026): „Datorate de firmă” arăta D112, D300, D394, D406 pe 09/2026 fără mențiunea „înainte de preluare”.
    Pașii: firma plătitoare de TVA lunar, luna preluării = luna curentă -> Declarații -> lista tipurilor: D394 pe luna dinainte (termenul ei
    cade în luna curentă, deci e în fereastra de 60 de zile oricare ar fi ziua) apare în grupul „Datorate de firmă — înainte de preluare în
    iConta.eu”, cu „· înainte de preluare” pe rând; nicio opțiune a lunii curente nu e în grupul acela.
    MUTAȚIA: în core/firma_rezumat.py `                _t["inainte_de_preluare"] = _lp.inainte(_t["an"], _t.get("luna"), preluare)` ->
    `                _t["inainte_de_preluare"] = False` -> ROȘU (D394 pe luna dinainte în grupul obișnuit, nemarcată)."""
    from e2e_bloc_a import _card, pregateste_firma
    f = firma_preluata
    pregateste_firma(patron, f)
    azi = datetime.date.today()
    sql('UPDATE "%s".firma_profil SET luna_preluare = %%s WHERE id = 1' % f["schema"], (azi.replace(day=1),))
    an_p, luna_p = _luna_dinainte(azi)
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "declaratii", "#dec-tip")
    grupuri = pg.evaluate("""() => [...document.querySelectorAll('#dec-tip optgroup')].map(g => ({eticheta: g.label,
        optiuni: [...g.querySelectorAll('option')].map(o => ({tip: o.value, an: +o.dataset.an, luna: +o.dataset.luna, text: o.textContent}))}))""")
    print("432 grupuri:", grupuri)
    patron.captura()
    inainte = [g for g in grupuri if g["eticheta"] == "Datorate de firmă — înainte de preluare în iConta.eu"]
    assert inainte, grupuri
    # D394 (termen 30 al lunii următoare) și D406 (ultima zi a lunii următoare) pe luna dinainte: cel puțin una e în fereastră oricare zi
    luna_dinainte = [o for o in inainte[0]["optiuni"] if o["tip"] in ("d394", "d406") and (o["an"], o["luna"]) == (an_p, luna_p)]
    assert luna_dinainte and all(o["text"].endswith("· înainte de preluare") for o in luna_dinainte), inainte
    assert all((o["an"], o["luna"] or 12) < (azi.year, azi.month) for o in inainte[0]["optiuni"]), inainte
    obisnuite = [g for g in grupuri if g["eticheta"] == "Datorate de firmă (din vectorul fiscal)"]
    assert all("înainte de preluare" not in o["text"] for g in obisnuite for o in g["optiuni"]), obisnuite


@pytest.fixture()
def doua_firme():
    """Două firme NOI ale cabinetului de test: pe prima contabilul-șef are o notă ciornă, a doua se șterge sub cerere."""
    g1, g2 = firma_noua(), firma_noua()
    a, b = next(g1), next(g2)
    try:
        yield a, b
    finally:
        for g in (g2, g1):
            try:
                next(g)
            except StopIteration:
                pass


def test_def_c68_ciornele_tale_nu_cad_cand_o_firma_dispare(patron, doua_firme):
    """C68 (găsită de Code la curățenia e2e a lotului 9, comanda 10.1 pct.3: „eroarea 500 intermitentă din /eu/ciorne se repară în acest
    lot”). `GET /eu/ciorne` cădea cu 500 (`relation "inregistrari" does not exist`) când o firmă din lista utilizatorului era ștearsă
    între citirea listei și interogarea ei. Pașii: o notă ciornă a contabilului-șef pe firma A; schema firmei B dispare (firma încă în
    listă — exact fereastra cursei) -> ecranul principal: cardul „De validat” numără „1 notă a ta în ciornă”, fără nicio cerere 5xx (garda
    fixturii) -> fereastra „De validat”: „Notele tale în ciornă (1)” cu firma A.
    MUTAȚIA: în core/uc_eu.py `        exista, note = db.pe_firma_existenta(t["schema_name"], lambda c, _t=t: coada_api.ciorne_proprii(c, _t["id"], uid))`
    -> `        exista, note = True, coada_api.ciorne_proprii(db.get_conn(t["schema_name"]).__enter__(), t["id"], uid)` -> ROȘU (500 pe
    `/eu/ciorne`)."""
    from e2e_bloc_a import _api, _ok
    a, b = doua_firme
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % a["tenant_id"],
                   {"data": datetime.date.today().isoformat(), "descriere": "Ciorna C68", "document_ref": "C68",
                    "linii": [{"debit": "6022", "credit": "5311", "suma": 68}]}), "nota ciornă")["id"]
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % a["schema"], (nid,)) == [("ciorna",)]
    sql('DROP SCHEMA "%s" CASCADE' % b["schema"])     # firma B: rândul ei e încă în listă, schema nu mai e
    pg = patron.pg
    patron.acasa()
    pg.wait_for_function("() => /notă a ta în ciornă/.test((document.querySelector('[data-cheie=\"validat\"]') || {}).innerText || '')",
                         timeout=20000)
    card = pg.inner_text("[data-cheie='validat']")
    print("C68 card:", card)
    assert "1 notă a ta în ciornă" in " ".join(card.split()), card
    pg.click("button.cab-card:has([data-cheie='validat'])")
    # [lotul 12, comanda 12.2 pct.12, deficiența 622] „Notele tale în ciornă” e tabelul de note: un rând pe ciornă, cu firma și explicația pe rând
    pg.wait_for_selector("#val-ciorne tbody.tn-nota[data-ciorna]", timeout=20000)
    lista = pg.inner_text(".fereastra:last-of-type")
    patron.captura()
    # titlul grupului e afișat cu majuscule de CSS (`inner_text` dă textul afișat): comparația nu ține seama de majuscule
    assert "notele tale în ciornă (1)" in lista.lower() and a["nume"] in lista and "Ciorna C68" in lista, lista
    assert b["nume"] not in lista
