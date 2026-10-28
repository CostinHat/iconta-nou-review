# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII), pachetul `ctrl` — Control fiscal: 484 (grav) și 463.

  * 484 „Control încrucișat: confruntarea declarații–contabilitate nu rulează”: confruntarea rula pe luna ÎN CURS (fără decont încă:
    „coincid” pe 0 cu 0), iar reconcilierea fiecărei declarații datorate cu documentele perioadei nu se arăta deloc. Acum «Declarație vs
    contabilitate» confruntă luna încheiată (`control_fiscal_api.luna_confruntata`), o spune, și arată «Declarațiile recalculate din
    documente», fiecare cu numele declarației.
  * 463 „Termene SPV absente din Control fiscal; lipsa dreptului aflată târziu”: secțiunea «e-Factura — transmiterea în SPV» arată
    facturile emise de la luna preluării care trebuie transmise și nu sunt, cu termenul fiecăreia, și starea dreptului SPV al firmei.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): factura din luna trecută și nota ei VALIDATĂ se scriu direct în schema firmei noi —
testul e despre ce arată Control fiscal peste o lună încheiată, nu despre emitere (acoperită de blocurile A/B) — iar luna preluării se pune
pe ruta Date firmă. Clientul: DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: CF art.323 alin.(1) — decontul se depune „până la data de 25 inclusiv a lunii următoare celei în care se încheie perioada fiscală”
(luna confruntată e luna încheiată); OUG 120/2021 art.10 alin.(7) — „Termenul-limită pentru transmiterea facturilor în sistemul național
privind factura electronică RO e-Factura este de 5 zile lucrătoare de la data emiterii facturii”."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _ok, pregateste_firma
from e2e_bloc_d import _control_firma

AZI = _dt.date.today()
LUNA_TRECUTA = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)
CUI_CLIENT = "14399840"


@pytest.fixture()
def firma_ctrl():
    for f in firma_noua():
        yield f


def _factura_validata(firma, numar, zi):
    """Factura emisă către DANTE (1.000 + TVA 21% = 210, 1.210) și nota ei VALIDATĂ (4111 = 707 1.000, 4111 = 4427 210)."""
    s = firma["schema"]
    # date-de-pornire: factura din luna trecută (luna încheiată pe care o confruntă Control fiscal), netransmisă în SPV; emiterea pe ecran e probată în blocurile A/B
    fid = sql('INSERT INTO "%s".facturi (numar, data_emitere, directie, total, tva, tert_cui, tert_nume, tert_tara, status) '
              "VALUES (%%s, %%s, 'emisa', 1210, 210, %%s, 'DANTE INTERNATIONAL SA', 'RO', 'emisa') RETURNING id" % s,
              (numar, zi.isoformat(), CUI_CLIENT))[0][0]
    # date-de-pornire: linia facturii de pornire de mai sus
    sql('INSERT INTO "%s".factura_linii (factura_id, descriere, cantitate, pret_unitar, cota_tva) VALUES (%%s, %%s, 1, 1000, 21)' % s,
        (fid, "Servicii de consultanță"))
    # date-de-pornire: nota contării facturii de pornire (4111 = 707, 4111 = 4427), ciornă întâi (regula_linii_nota)
    nid = sql('INSERT INTO "%s".inregistrari (data, descriere, status, factura_id, document_ref) VALUES (%%s, %%s, %%s, %%s, %%s) '
              "RETURNING id" % s, (zi.isoformat(), "Factura " + numar, "ciorna", fid, "Factura " + numar))[0][0]
    for deb, cre, suma in (("4111", "707", 1000), ("4111", "4427", 210)):
        # date-de-pornire: rândurile notei de pornire de mai sus
        sql('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, %%s, %%s, %%s)' % s,
            (nid, deb, cre, suma))
    # date-de-pornire: nota facturii de pornire validată (ciornă -> rânduri -> validată); validarea pe ecran e probată în blocul D
    sql('UPDATE "%s".inregistrari SET status = \'validata\' WHERE id = %%s' % s, (nid,))   # ciornă -> rânduri -> validată (regula_linii_nota)
    return fid


def test_def_484_confruntarea_ruleaza_pe_luna_incheiata_si_arata_reconcilierea(patron, firma_ctrl):
    """484. Pașii contabilului: firmă plătitoare de TVA lunar, cu o factură emisă în luna trecută (1.000 + 210 TVA) contabilizată și
    validată -> Control fiscal -> firma -> «Declarație vs contabilitate»: „Luna confruntată: <luna trecută>”, „TVA colectată: D300 și
    contul 4427 coincid.” (210 cu 210, nu 0 cu 0 pe luna în curs) și «Declarațiile recalculate din documente» cu „D300 (decont TVA):
    Recalculul din documentele perioadei confirmă cifrele declarației generate.”"""
    pregateste_firma(patron, firma_ctrl, platitor=True, regim_fiscal="micro")
    _factura_validata(firma_ctrl, "E2E484-1", LUNA_TRECUTA.replace(day=10))
    _control_firma(patron, firma_ctrl)
    pg = patron.pg
    pg.wait_for_selector(".fereastra:last-of-type #cf-incrucisat", timeout=60000)
    pg.locator(".fereastra:last-of-type #cf-incrucisat").scroll_into_view_if_needed()
    patron.captura("declaratie_vs_contabilitate")
    text = " ".join(pg.inner_text(".fereastra:last-of-type #cf-incrucisat").split())
    # CF art.323 alin.(1): azi se depune decontul lunii trecute — aceea se confruntă
    # [lotul 14, 694] fiecare comparație își arată perioada: firma lunară -> D300 pe luna trecută (nu „luna confruntată” generică)
    assert "Perioada comparată: D300 %s" % LUNA_TRECUTA.strftime("%m/%Y") in text, text
    assert "TVA colectată: D300 și contul 4427 coincid." in text, text
    assert "Declarațiile recalculate din documente" in text, text
    assert "D300 (decont TVA): Recalculul din documentele perioadei confirmă cifrele declarației generate." in text, text
    assert "VERIFICARE INTRERUPTA" not in text and "reconciliaza" not in text, text


def test_def_463_control_fiscal_arata_termenele_spv_si_dreptul(patron, firma_ctrl):
    """463. Pașii contabilului: firmă preluată în luna trecută (Date firmă -> „Luna preluării”), cu o factură emisă pe 10 ale lunii trecute
    către un client român, netransmisă în SPV; cabinetul de probă nu e conectat la SPV -> Control fiscal -> firma -> «e-Factura —
    transmiterea în SPV»: factura, cu „termen ZZ.LL.AAAA (depășit)” (5 zile lucrătoare de la emitere), și starea SPV „cabinetul nu e
    conectat”, cu butonul spre Conectare SPV; în «Verificări contabile» nu se repetă (stă în secțiunea ei)."""
    from core.facturi_api import termen_spv
    from core.pdf_util import data_ro
    tid = firma_ctrl["tenant_id"]
    pregateste_firma(patron, firma_ctrl, platitor=True, regim_fiscal="micro")
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"luna_preluare": LUNA_TRECUTA.strftime("%Y-%m")}), "luna preluării")
    zi = LUNA_TRECUTA.replace(day=10)
    _factura_validata(firma_ctrl, "E2E463-1", zi)
    termen = termen_spv(zi)   # OUG 120/2021 art.10 alin.(7): 5 zile lucrătoare de la emitere
    _control_firma(patron, firma_ctrl)
    pg = patron.pg
    pg.wait_for_selector(".fereastra:last-of-type #cf-efactura", timeout=60000)
    pg.wait_for_selector(".fereastra:last-of-type #cf-spv-stare .spv-stare-text", timeout=30000)
    pg.locator(".fereastra:last-of-type #cf-efactura").scroll_into_view_if_needed()
    patron.captura("efactura_spv")
    text = " ".join(pg.inner_text(".fereastra:last-of-type #cf-efactura").split())
    assert "E2E463-1" in text and "din %s" % data_ro(zi) in text, text
    assert "termen %s (depășit)" % data_ro(termen) in text, text
    assert "SPV: cabinetul nu e conectat" in text, text
    titlu = pg.locator(".fereastra:last-of-type .cf-grup-titlu", has_text="e-Factura — transmiterea în SPV").inner_text()
    assert "(1)" in titlu, titlu
    tot = patron.fereastra()
    assert "Facturi netransmise în SPV după termen" not in tot, tot   # nu se repetă în «Verificări contabile»
