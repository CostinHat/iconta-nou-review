# -*- coding: utf-8 -*-
"""[lotul 12, C151] Încasarea de la client salvată fără factură, legată apoi din Casă de factura pe care o stinge: chitanța emisă automat
pe ea (456 a) se leagă de aceeași factură, iar nota o numește.

Găsit la repararea suitei (R3): după „Leagă de factură”, chitanța rămânea fără factură, iar nota scria „document E2ECH-N” în loc de
„chitanța E2ECH-N — factura …” (168). La o firmă exceptată de la casa de marcat, chitanța rămasă fără factură și fără cotă ar fi oprit D394
ca „de clasificat”, deși stinge o factură.
MUTAȚIA (`mut_lot12_c151.json`): fără blocul C151 din `casa_api.leaga` -> chitanța rămâne fără factură -> ROȘU.
"""
import os
import sys

from conftest import sql
from e2e_bloc_a import AZI, _card, emite_api, pregateste_firma

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def test_def_c151_chitanta_incasarii_legate_de_factura_numeste_factura(patron, firma_e2e):
    pregateste_firma(patron, firma_e2e)
    s = firma_e2e["schema"]
    f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E C151", "cantitate": 1, "um": "buc", "pret_unitar": 200.0,
                                             "cota_tva": 21, "cota_propusa": 21, "articol_id": None}])
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", "151")
    pg.fill("#c-cui", "14399840")
    pg.dispatch_event("#c-campuri", "change")
    pg.wait_for_timeout(800)
    pg.click("#c-adauga")   # factura nebifată: încasarea se salvează fără factură, cu chitanța ei (456 a)
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('a fost emisă')", timeout=30000)
    ((cid, serie, nr, op_id),) = sql('SELECT id, serie, numar, casa_operatiune_id FROM "%s".chitante WHERE suma = 151 AND factura_id IS NULL' % s)
    rand = pg.locator(".pf-frand", has_text="%s-%s" % (serie, nr)).first
    rand.locator("[data-leaga]").click()
    rand.locator("[data-leaga-f='%s']" % f["factura_id"]).click()
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Operațiunea e legată de factura')",
                         timeout=20000)
    patron.captura("legata")
    assert sql('SELECT factura_id FROM "%s".chitante WHERE id = %%s' % s, (cid,)) == [(f["factura_id"],)]
    ((descriere, fid_nota, partener),) = sql('SELECT i.descriere, i.factura_id, o.partener FROM "%s".casa_operatiuni o JOIN "%s".inregistrari i '
                                             "ON i.id = o.inregistrare_id WHERE o.id = %%s" % (s, s), (op_id,))
    assert fid_nota == f["factura_id"], fid_nota
    # descrierea cuvenită, din aceeași formulă ca nota chitanței la încasarea facturii (168): chitanța, factura stinsă, clientul
    from core import casa_api
    from core.pdf_util import data_ro, serie_nr
    ((serie_f, numar_f, data_f),) = sql('SELECT serie, numar, data_emitere FROM "%s".facturi WHERE id = %%s' % s, (f["factura_id"],))
    cuvenita = casa_api.descriere_nota({"categorie": "incasare_client", "document": "%s-%s" % (serie, nr), "fel_document": "chitanța",
                                        "stinge": "factura %s din %s" % (serie_nr(serie_f, numar_f), data_ro(data_f)), "partener": partener})
    assert descriere == cuvenita, (descriere, cuvenita)
