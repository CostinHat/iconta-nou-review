# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), zona portal — emailurile către clienții firmei:

  · C158 — emailul de amintire a scadenței scria suma în „RON” („363,00 RON”), iar aplicația scrie „lei”. Pașii contabilului: clientul cu
    email -> factura emisă în lei, scadentă peste 3 zile -> Facturi -> Scadențar: rândul facturii arată suma „… lei” -> bifa „Trimite automat
    notificări de plată clienților” -> jobul zilnic al amintirilor, pe firmă (`notificari_scadenta.emite_pentru_firma`, ce rulează cronul de
    la 08:00) -> emailul din cutia poștală de test spune suma EXACT ca rândul din Scadențar („363,00 lei”), fără „RON”.
    Emailul nu are ecran în aplicație: se citește din cutia poștală de test a aplicației de probă (`ICONTA_EMAIL_CUTIE`,
    `observare._in_cutia_de_test`), ca la C122 (`e2e_lot12_cx3.py`). Ecranul comparat e Scadențarul (aceeași factură, aceeași sumă).

Pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ de test (`firma_noua`), pregătită pe drumul ecranelor (`pregateste_firma`). Clientul
DANTE INTERNATIONAL SA, CUI 14399840 (cifra de control verificată cu algoritmul din CLAUDE.md, `e2e_bloc_a.CLIENT`).

Temei: N/A — regulă de produs (DS cap.4: sumele „1.234,56 lei”; textele în limba contabilului).
"""
import datetime as _dt
import os
import time

import pytest

from conftest import firma_noua
from e2e_lot12_cx3 import _emailurile


def _captura_email(ecran, email, sufix):
    """Captura emailului din cutia de test, randat ca în clientul de email (pagină separată, același browser): dovada vizuală a textului
    care pleacă la client, lângă captura ecranului cu care se compară."""
    from conftest import CAPTURI
    pg = ecran.pg.context.new_page()
    try:
        pg.set_content("<div style='font-family:sans-serif;max-width:640px;margin:16px'><p><b>Către:</b> %s<br><b>Subiect:</b> %s</p><hr>%s</div>"
                       % (email["catre"], email["subiect"], email["html"]))
        os.makedirs(CAPTURI, exist_ok=True)
        pg.screenshot(path=os.path.join(CAPTURI, "%s_%s.png" % (ecran.nume, sufix)), full_page=True)
    finally:
        pg.close()


@pytest.fixture()
def firma_l13p():
    for f in firma_noua():
        yield f


def test_def_c158_amintirea_scadentei_scrie_suma_in_lei_ca_scadentarul(patron, firma_l13p):
    """C158. MUTAȚIA (`mut_lot13_portal.json`): `pdf_util.moneda_scrisa` întoarce codul („RON”) -> emailul spune „363,00 RON”, Scadențarul
    „363,00 lei” -> ROȘU."""
    import glob

    from conftest import _db
    from core import notificari_scadenta
    from e2e_bloc_a import CLIENT, PRODUS, _api, _card, _ok, _profil, pregateste_firma
    f = firma_l13p
    tid = f["tenant_id"]
    pregateste_firma(patron, f)
    p = _profil(f)
    p["email"] = "firma.c158.%d@prisma-cont.test" % tid
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, p), "Date firmă (emailul firmei)")
    email_client = "client.c158.%d@prisma-cont.test" % tid
    cid = _ok(_api(patron, "POST", "/tenants/%d/clienti" % tid, {"nume": CLIENT["#em-nume"], "cui": CLIENT["#em-cui"],
                                                                "adresa": CLIENT["#em-adresa"], "email": email_client}), "client")["client_id"]
    azi = _dt.date.today()
    scadenta = azi + _dt.timedelta(days=3)
    fac = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % tid, {
        "linii": [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                   "articol_id": None}],
        "client_id": cid, "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"],
        "moneda": "RON", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
        "data_emitere": azi.isoformat(), "data_scadenta": scadenta.isoformat(), "tip": "factura"}), "emitere")
    patron.firma(f["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-scadentar")
    pg.click("#fac-scadentar")
    pg.wait_for_selector("#sc-optin", timeout=25000)
    pg.check("#sc-optin")
    pg.wait_for_selector("#sc-lista [data-stop='%s']" % fac["factura_id"], timeout=20000)
    suma_pe_ecran = " ".join(pg.locator("#sc-lista .sc-fact-btn[data-id='%s'] .pf-frand-suma" % fac["factura_id"]).inner_text().split())
    patron.captura("scadentar_suma_in_lei")
    assert suma_pe_ecran == "363,00 lei", suma_pe_ecran          # 2 × 150,00 + TVA 21% = 363,00 (cifra probei)
    cutie = os.environ["ICONTA_EMAIL_CUTIE"]
    inainte = set(glob.glob(os.path.join(cutie, "*.json")))
    _db()
    rez = notificari_scadenta.emite_pentru_firma(f["schema"])
    assert rez["trimise"] == 1, rez
    gasite = []
    for _ in range(20):
        gasite = _emailurile(cutie, email_client, inainte)
        if gasite:
            break
        time.sleep(0.5)
    assert len(gasite) == 1, gasite
    corp = " ".join(gasite[0]["html"].split())
    _captura_email(patron, gasite[0], "email_amintire")      # emailul, așa cum îl citește clientul (n-are ecran în aplicație)
    assert "<b>%s</b>" % suma_pe_ecran in corp, corp               # aceeași sumă, aceeași monedă ca Scadențarul
    assert "RON" not in corp, corp
