# -*- coding: utf-8 -*-
"""Lotul 11, subagentul D3 (unealta de dovadă pe copia firmelor de test, comanda Costin 11.2 pct.3). Dovada pe F6 (copia lui tenant_055)
a găsit un drum al lui 428 rămas nereparat: „Configurare emitere” deschisă din formularul facturii („Schimbă seria”, firmă cu numerotarea
deja configurată — F6 după factura F6 nr. 1) arăta numai „Regim TVA: plătitoare de TVA (din profilul firmei).”, fără sistemul TVA la
încasare de la 01.11.2026. Cauza: `emitere_ecran.js` cheamă `configureazaNumerotare` de două ori; prima dată (numerotarea neconfigurată) cu
regimul TVA la încasare, a doua oară (butonul „Schimbă seria”) fără el.

Pașii: Date firmă (rutele ecranului) + numerotarea configurată (ruta ecranului „Configurare emitere”, `PUT facturi/numerotare`) -> Date firmă
-> „Aplică sistemul TVA la încasare”: Da, de la prima zi a lunii viitoare (CF art.282 alin.(3^1) lit.a) -> Salvează -> Facturi -> „Emite
factură” (formularul, numerotarea configurată) -> „Schimbă seria” -> „Configurare emitere” spune „TVA la încasare de la 01.LL.AAAA … — azi
nu se aplică”. Datele de pornire pe rutele ecranelor; nimic inserat direct în bază."""
import datetime as _dt

from e2e_bloc_a import AZI, PRODUS, _api, _card, _ok, _profil
from e2e_lot11_t import _regimul_din_date_firma


def test_def_428_schimba_seria_arata_sistemul_tva_la_incasare(patron, firma_e2e):
    """428, drumul „Schimbă seria” (găsit de dovada pe F6). ROȘU înainte: „Regim TVA: plătitoare de TVA (din profilul firmei).”, fără
    TVA la încasare. VERDE: „TVA la încasare de la <luna viitoare> … — azi nu se aplică” (CF art.282 alin.(3^1) lit.a: opțiunea
    exercitată luna asta se aplică de la prima zi a perioadei fiscale următoare)."""
    tid = firma_e2e["tenant_id"]
    luna_viitoare = (AZI.replace(day=28) + _dt.timedelta(days=4)).replace(day=1)
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, _profil(firma_e2e)), "Date firmă")
    _ok(_api(patron, "POST", "/tenants/%d/vector" % tid, {"regim_fiscal": "profit", "platitor_tva": True, "tip_decont": "lunar",
                                                         "operatiuni_ic": False, "inreg_art317": False, "tva_data_inceput": "2026-01-01"}),
        "vector fiscal")
    _ok(_api(patron, "POST", "/tenants/%d/produse" % tid, {"denumire": PRODUS, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21,
                                                          "confirmat": True}), "produs")
    _ok(_api(patron, "PUT", "/tenants/%d/facturi/numerotare" % tid, {"serie": "D3S", "numar_start": 1}), "numerotarea")
    _regimul_din_date_firma(patron, firma_e2e, luna_viitoare)
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    _card(patron, "facturi", "#fac-emite")
    pg.click("#fac-emite")
    pg.wait_for_selector("#em-cui", timeout=25000)
    assert not pg.locator("#em-config-regim").count(), "numerotarea configurată: se deschide formularul, nu Configurare emitere"
    pg.click("#em-schimba-serie")
    pg.wait_for_selector(".fereastra:last-of-type #em-config-regim", timeout=25000)
    regim = " ".join(pg.inner_text(".fereastra:last-of-type #em-config-regim").split())
    patron.captura("configurare_din_schimba_seria")
    # CF art.282 alin.(3^1) lit.a: sistemul ales luna asta se aplică de la prima zi a lunii viitoare, deci azi nu
    assert "TVA la încasare de la %s" % luna_viitoare.strftime("%d.%m.%Y") in regim and "azi nu se aplică" in regim, regim
