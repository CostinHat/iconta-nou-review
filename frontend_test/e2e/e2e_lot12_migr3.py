# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `migr3` — deficiența 252, decizia Costin 12.3 pct.5, verbatim: „252: coloana TVA la încasare e opțională în fișierul
de preluare; dacă lipsește, se ia regimul firmei la data facturii.”

Pașii contabilului, pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`) care aplică sistemul TVA la încasare de la
01.01.2026, preluată la sfârșitul lunii trecute: balanța de deschidere (4111 D 4.235, 401 C 1.210, 4428 C 105, 5121 D 10.000, 1012 C 12.920)
pe rutele Migrării, apoi PE ECRAN: Import date -> „Solduri parteneri” -> situația pe facturi cu coloana „TVA la încasare” (FA-101 «da»,
FA-102 «nu», FB-7 și G-55 goale) -> previzualizarea arată coloana -> „Salvează partenerii”: „Cu TVA la încasare: 3 facturi — TVA
neexigibil 315,00 lei pe cele emise, nededus 210,00 lei pe cele primite” -> Bancă: încasarea FA-101 -> „Contează” -> nota are și
4428 = 4427 210,00. O valoare necunoscută în coloană e refuzată cu rândul ei.
CUI-urile: sintetice, cu cifra de control verificată (`conftest.cui_cu_control`). Temei: CF art.282 alin.(3), (8); art.297 alin.(3); art.291
alin.(5) (citate în `core/test_lot12_migr3_tva_incasare.py`). Mutațiile: `frontend_test/e2e/mut_lot12_migr3.json`. Dovada pe firmele de
test: `frontend_test/dovada/dovezi_lot12_migr3.json`."""
import datetime as _dt

import pytest

from conftest import cui_cu_control, firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, pregateste_firma
from e2e_import_saga import _incarca, _pas

AZI = _dt.date.today()
DATA_REF = AZI.replace(day=1) - _dt.timedelta(days=1)          # soldurile de preluare: ziua dinaintea lunii preluării
ALFA = (str(cui_cu_control(25200111)), "ALFA DISTRIBUTIE MIGR3 SRL")
BETA = (str(cui_cu_control(25200112)), "BETA CONSTRUCT MIGR3 SRL")
GAMMA = (str(cui_cu_control(25200113)), "GAMMA LOGISTIC MIGR3 SRL")


def _ro(d):
    return d.strftime("%d.%m.%Y")


def fisier_tvai(valoare_fb7=""):
    """Situația pe facturi cu coloana „TVA la încasare” (cota standard 21% la datele facturilor: FA-101 1.210 -> TVA 210)."""
    f1, f2, f3, f4 = (DATA_REF - _dt.timedelta(days=n) for n in (20, 10, 5, 15))
    return ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA la încasare\n"
            "4111;RO%s;%s;FA-101;%s;%s;1210,00;da\n" % (ALFA + (_ro(f1), _ro(AZI + _dt.timedelta(days=20)))) +
            "4111;RO%s;%s;FA-102;%s;%s;2420,00;nu\n" % (ALFA + (_ro(f2), _ro(AZI + _dt.timedelta(days=30)))) +
            "4111;%s;%s;FB-7;%s;;605,00;%s\n" % (BETA + (_ro(f3), valoare_fb7)) +
            "401;%s;%s;G-55;%s;%s;1210,00;\n" % (GAMMA + (_ro(f4), _ro(AZI + _dt.timedelta(days=10))))).encode("utf-8")


def fisier_f6_tvai():
    """[dovada pe F6] Situația partenerilor lui F6 (soldurile la 30.09.2026), pe facturi, cu coloana „TVA la încasare”: F6 aplică sistemul
    de la 01.10.2026, deci F6-A1 «da» (05.09.2026) contrazice Date firmă — previzualizarea o spune și nu lasă salvarea."""
    return ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată;TVA la încasare\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A1;05.09.2026;05.10.2026;5000,00;da\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A2;20.09.2026;20.10.2026;2140,00;nu\n"
            "4111;401006208;Beta Construct SRL;F6-B1;15.09.2026;15.10.2026;4760,00;\n"
            "401;401006305;Gamma Logistic SRL;G-901;10.09.2026;10.10.2026;5950,00;\n"
            "401;401006402;Delta Ambalaje SRL;D-77;25.09.2026;;3570,00;\n").encode("utf-8")


@pytest.fixture(scope="module")
def firma_migr3():
    for f in firma_noua():
        yield f


@pytest.fixture()
def in_sistem(patron, firma_migr3):
    """Firma în sistemul TVA la încasare de la 01.01.2026, cu balanța de deschidere la DATA_REF (pe rutele Migrării)."""
    f, tid = firma_migr3, firma_migr3["tenant_id"]
    if not sql('SELECT count(*) FROM "%s".solduri_initiale' % f["schema"])[0][0]:
        pregateste_firma(patron, f)
        # CF art.282 alin.(3^1): „de la” = prima zi a unei perioade fiscale
        # date-de-pornire: perioada TVA la încasare a firmei (ruta din Date firmă cheamă registrul ANAF; ecranul e probat în e2e_lot10_date_firma)
        sql('INSERT INTO "%s".tva_incasare_perioade (de_la, sursa) VALUES (%%s, %%s)' % f["schema"], ("2026-01-01", "manual"))
        # date-de-pornire: indicatorul „aplică azi”, sincronizat din perioade de salvarea din Date firmă (`regim_tva_incasare.sincronizeaza`)
        sql('UPDATE "%s".firma_profil SET tva_la_incasare = true WHERE id = 1' % f["schema"])
        _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"luna_preluare": AZI.strftime("%Y-%m")}), "luna preluării")
        _ok(_api(patron, "POST", "/tenants/%d/solduri" % tid, {"data_referinta": DATA_REF.isoformat(), "randuri": [
            {"cont": "4111", "debit": 4235}, {"cont": "401", "credit": 1210}, {"cont": "4428", "credit": 105},
            {"cont": "5121", "debit": 10000}, {"cont": "1012", "credit": 12920}]}), "balanța de deschidere")
    return f


def _r(pg, rand):
    return " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="%d"]' % rand).all_inner_texts()).split())


def test_def_252_tva_la_incasare_din_fisier_si_din_regimul_firmei(patron, in_sistem):
    """252 (12.3 pct.5). Pașii: Import date -> „Solduri parteneri” -> situația pe facturi cu coloana „TVA la încasare” -> previzualizarea:
    coloana „TVA la încasare” — ALFA „da: FA-101; nu: FA-102”, BETA și GAMMA „după Date firmă” -> „Salvează partenerii”: „Cu TVA la
    încasare: 3 facturi — TVA neexigibil 315,00 lei pe cele emise, nededus 210,00 lei pe cele primite” -> Bancă: extrasul cu +1.210 de la
    ALFA: „Potrivire exactă” -> „Contează”: nota 5121 = 4111 1.210,00 și 4428 = 4427 210,00 (CF art.282 alin.(3), (8)).
    ROȘU înainte: coloana nu se citea; facturile preluate fără TVA; nota băncii numai 5121 = 4111."""
    f, pg = in_sistem, patron.pg
    _pas(patron, f, "Solduri parteneri")
    _incarca(patron, "situatie_tvai.csv", fisier_tvai(), "#mig-salveaza-part")
    patron.captura("previzualizare")
    assert "TVA la încasare" in pg.inner_text(".mig-prev thead"), pg.inner_text(".mig-prev thead")
    assert _r(pg, 2).endswith("FA-101, FA-102 da: FA-101; nu: FA-102"), _r(pg, 2)
    assert _r(pg, 4).endswith("FB-7 după Date firmă") and _r(pg, 5).endswith("G-55 după Date firmă"), (_r(pg, 4), _r(pg, 5))
    assert "Coloana opțională „TVA la încasare” (da / nu)" in patron.fereastra()
    assert pg.locator("#mig-refuz-tvai").count() == 0
    pg.click("#mig-salveaza-part")
    pg.wait_for_function("() => document.body.innerText.includes('Cu TVA la încasare: 3 facturi — TVA neexigibil 315,00 lei pe cele emise, "
                         "nededus 210,00 lei pe cele primite')", timeout=30000)
    patron.captura("salvat")
    t = " ".join(pg.inner_text("body").split())
    assert "4 facturi deschise preluate (de încasat 4.235,00 lei, de plătit 1.210,00 lei)" in t, t[:1200]
    assert "4428 din balanța de deschidere" not in t, t[:1200]   # 210 + 105 − 210 = 105: se potrivește, nicio atenție
    fa101 = sql('SELECT id, tva::text FROM "%s".facturi WHERE tip = \'preluata\' AND numar = \'FA-101\'' % f["schema"])[0]
    assert fa101[1] == "210.00", fa101
    # Bancă: extrasul, încasarea ALFA pentru FA-101
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    extras = "Data;Detalii;Suma\n%s;Incasare FA-101 CUI RO%s;1210,00\n" % (_ro(AZI), ALFA[0])
    pg.set_input_files("#bk-fisier", {"name": "extras_migr3.csv", "mimeType": "text/csv", "buffer": extras.encode("utf-8")})
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('linie importată')", timeout=30000)
    linie = pg.locator("#bk-lista tbody.tn-nota", has_text="Incasare FA-101").first
    linie.wait_for(timeout=20000)
    assert "Potrivire exactă" in " ".join(linie.inner_text().split()), linie.inner_text()
    inainte = pg.inner_text("#bk-mesaj")
    linie.locator("[data-cont]").first.click()
    pg.wait_for_function("(p) => { const m = document.querySelector('#bk-mesaj').innerText; return m !== p && m.includes('creat'); }",
                         arg=inainte, timeout=30000)
    patron.captura("banca_contata")
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s ORDER BY l.id" % (f["schema"], f["schema"]), (fa101[0],))
    assert note == [("5121", "4111", "1210.00"), ("4428", "4427", "210.00")], note


def test_def_252_valoarea_necunoscuta_in_tva_la_incasare_e_refuzata(patron, in_sistem):
    """252 (12.3 pct.5). Pașii: Import date -> „Solduri parteneri” -> fișierul cu „poate” în coloana „TVA la încasare” pe FB-7 -> sub
    fișier: „Rândul 4 (BETA …, factura FB-7): în coloana „TVA la încasare” scrie „poate”. Se acceptă «da» sau «nu»”; nicio previzualizare.
    ROȘU înainte: coloana nu se citea (valoarea trecea tăcut)."""
    f, pg = in_sistem, patron.pg
    _pas(patron, f, "Solduri parteneri")
    pg.set_input_files("#mig-file", files=[{"name": "situatie_tvai_gresit.csv", "mimeType": "text/csv", "buffer": fisier_tvai("poate")}])
    pg.wait_for_function("() => document.querySelector('#mig-eroare').innerText.includes('poate')", timeout=20000)
    patron.captura("refuz")
    t = " ".join(pg.inner_text("#mig-eroare").split())
    assert "Rândul 4 (%s, factura FB-7): în coloana „TVA la încasare” scrie „poate”. Se acceptă «da» sau «nu»" % BETA[1] in t, t
    assert pg.locator("#mig-salveaza-part").count() == 0
