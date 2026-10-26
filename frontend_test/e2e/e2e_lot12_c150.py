# -*- coding: utf-8 -*-
"""[lotul 12, C150] Confirmarea contării din Bancă numește linia contată.

Găsit la scenariul pilot (pasul 18): două plăți din aceeași zi, contate pe aceeași notă propusă, primeau exact același text („Notă
401=5121 creată (din 28.09.2026, ciornă)…”), deci contabilul nu putea spune din mesaj că a doua s-a scris (comanda Costin 05.10.2026
pct.8: mesajul spune exact ce s-a creat). Acum confirmarea începe cu linia: „Linia din ZZ.LL.AAAA, −12,50 lei (Comision …): notă …”.
MUTAȚIA (`mut_lot12_c150.json`): `ceLinie` întoarce "" -> cele două confirmări sunt identice -> ROȘU.
"""
import time

from e2e_bloc_a import AZI, _card, pregateste_firma


def test_def_c150_doua_contari_din_aceeasi_zi_au_confirmari_diferite(patron, firma_e2e):
    pregateste_firma(patron, firma_e2e)
    zi = AZI.strftime("%d.%m.%Y")
    extras = ("Data;Detalii;Suma\n%s;Comision administrare cont E2E C150;-12,50\n%s;Comision mentenanta card E2E C150;-7,00\n"
              % (zi, zi))
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    pg.set_input_files("#bk-fisier", {"name": "extras_e2e_c150_%d.csv" % time.time(), "mimeType": "text/csv",
                                      "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('importate')", timeout=30000)
    confirmari = []
    for text, suma in (("Comision administrare cont E2E C150", "12,50"), ("Comision mentenanta card E2E C150", "7,00")):
        rand = pg.locator("#bk-lista tbody.tn-nota", has_text=text).first
        rand.locator("[data-cont]").first.click()
        pg.locator("#bk-lista tbody.tn-nota", has_text=text).get_by_text("Contată").first.wait_for(timeout=20000)
        pg.wait_for_function("(t) => document.querySelector('#bk-mesaj').innerText.includes(t)", arg=text, timeout=20000)
        m = " ".join(pg.inner_text("#bk-mesaj").split())
        assert m.startswith("Linia din %s, −%s lei (%s): notă 627=5121 creată" % (zi, suma, text)), m
        confirmari.append(m)
    patron.captura("doua_confirmari")
    assert confirmari[0] != confirmari[1], confirmari
