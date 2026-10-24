# -*- coding: utf-8 -*-
"""Lotul 12, pachetul `p252` — deficiența 252 (grupa 2, poziția pilot F085 „Import solduri parteneri”): „Import parteneri: facturi deschise
neimportate; scadențarul nealimentat.”

Pașii contabilului, pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`), preluată la sfârșitul lunii trecute:
balanța de deschidere (4111 D 5.000, 401 C 1.500, 5121 D 10.000, 1012 C 13.500) pe rutele Migrării, apoi PE ECRAN: Import date ->
„Solduri parteneri” -> situația clienților și furnizorilor din programul vechi, PE FACTURI (Nr. factură, Data, Scadență, Sumă neachitată)
-> previzualizarea arată facturile fiecărui partener -> „Salvează partenerii” -> scadențarul are facturile, cu restul lor -> Bancă: extrasul
cu încasarea de la ALFA potrivește factura preluată -> „Contează” -> scadențarul n-o mai are. Detaliul facturii preluate n-are acțiuni de
document fiscal (PDF, stornare, SPV). CUI-urile: sintetice, cu cifra de control verificată (`conftest.cui_cu_control`). Temei: N/A — regulă
de produs; soldul preluat nu se mai înregistrează (OMFP 1802/2014 pct.130), de aceea facturile preluate n-au notă.
Mutațiile: `frontend_test/e2e/mut_lot12_p252.json`. Dovada pe firmele de test: `frontend_test/dovada/dovezi_lot12_p252.json`."""
import datetime as _dt

import pytest

from conftest import cui_cu_control, firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, pregateste_firma
from e2e_import_saga import _incarca, _pas

AZI = _dt.date.today()
DATA_REF = AZI.replace(day=1) - _dt.timedelta(days=1)          # soldurile de preluare: ziua dinaintea lunii preluării
ALFA = (str(cui_cu_control(25200001)), "ALFA DISTRIBUTIE P252 SRL")
BETA = (str(cui_cu_control(25200002)), "BETA CONSTRUCT P252 SRL")
GAMMA = (str(cui_cu_control(25200003)), "GAMMA LOGISTIC P252 SRL")


def _ro(d):
    return d.strftime("%d.%m.%Y")


def fisier_pe_facturi():
    """Situația clienților / furnizorilor din programul vechi, pe facturi (și pentru dovezi): FA-101 scadentă de 5 zile, FA-102 în termen
    (peste 30 de zile), FB-7 fără scadență, G-55 (furnizorul)."""
    f1, f2, f3, f4 = (DATA_REF - _dt.timedelta(days=n) for n in (20, 10, 5, 15))
    return ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată\n"
            "4111;RO%s;%s;FA-101;%s;%s;1000,00\n" % (ALFA + (_ro(f1), _ro(AZI - _dt.timedelta(days=5)))) +
            "4111;RO%s;%s;FA-102;%s;%s;2000,00\n" % (ALFA + (_ro(f2), _ro(AZI + _dt.timedelta(days=30)))) +
            "4111;%s;%s;FB-7;%s;;2000,00\n" % (BETA + (_ro(f3),)) +
            "401;%s;%s;G-55;%s;%s;1500,00\n" % (GAMMA + (_ro(f4), _ro(AZI + _dt.timedelta(days=10))))).encode("utf-8")


def fisier_f6_pe_facturi():
    """[dovada pe F6, `frontend_test/dovada/dovezi_lot12_p252.json`] Situația partenerilor lui F6 (soldurile lui la 30.09.2026: Alfa 7.140,
    Beta 4.760 pe 4111; Gamma 5.950, Delta 3.570 pe 401), pe facturi: Alfa are două (5.000,00 + 2.140,00)."""
    return ("Cont;Cod fiscal;Denumire;Nr. factură;Data;Scadență;Sumă neachitată\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A1;05.09.2026;05.10.2026;5000,00\n"
            "4111;401006100;Alfa Distribuție SRL;F6-A2;20.09.2026;20.10.2026;2140,00\n"
            "4111;401006208;Beta Construct SRL;F6-B1;15.09.2026;15.10.2026;4760,00\n"
            "401;401006305;Gamma Logistic SRL;G-901;10.09.2026;10.10.2026;5950,00\n"
            "401;401006402;Delta Ambalaje SRL;D-77;25.09.2026;;3570,00\n").encode("utf-8")


@pytest.fixture(scope="module")
def firma_p252():
    for f in firma_noua():
        yield f


@pytest.fixture()
def preluata(patron, firma_p252):
    """Firma cu balanța de deschidere la DATA_REF (pe rutele Migrării, ca la F183)."""
    f, tid = firma_p252, firma_p252["tenant_id"]
    if not sql('SELECT count(*) FROM "%s".solduri_initiale' % f["schema"])[0][0]:
        pregateste_firma(patron, f)
        _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, {"luna_preluare": AZI.strftime("%Y-%m")}), "luna preluării")
        _ok(_api(patron, "POST", "/tenants/%d/solduri" % tid, {"data_referinta": DATA_REF.isoformat(), "randuri": [
            {"cont": "4111", "debit": 5000}, {"cont": "401", "credit": 1500}, {"cont": "5121", "debit": 10000},
            {"cont": "1012", "credit": 13500}]}), "balanța de deschidere")
    return f


def _scadentar(patron, firma):
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-scadentar")
    patron.pg.click("#fac-scadentar")
    patron.pg.wait_for_selector("#sc-facturi", timeout=25000)


def _t(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _id(firma, numar):
    return sql('SELECT id FROM "%s".facturi WHERE tip = \'preluata\' AND numar = %%s' % firma["schema"], (numar,))[0][0]


def _importa_pe_ecran(patron, f):
    """Import date -> „Solduri parteneri” -> situația pe facturi -> previzualizarea (rândul ALFA cu facturile lui) -> „Salvează partenerii”."""
    pg = patron.pg
    _pas(patron, f, "Solduri parteneri")
    _incarca(patron, "situatie_clienti_furnizori.csv", fisier_pe_facturi(), "#mig-salveaza-part")
    rand = " ".join(" ".join(pg.locator('.mig-prev tbody tr[data-rand="2"]').all_inner_texts()).split())
    patron.captura("previzualizare")
    assert rand == "2 intră 4111 %s %s 3.000,00 0,00 FA-101, FA-102" % ALFA, rand
    assert "intră în scadențar și se sting din Bancă, Casă sau Compensări" in patron.fereastra()
    pg.click("#mig-salveaza-part")
    pg.wait_for_function("() => document.body.innerText.includes('3 parteneri salvați. 4 facturi deschise preluate (de încasat 5.000,00 "
                         "lei, de plătit 1.500,00 lei): le sting încasările și plățile din Bancă, Casă sau Compensări.')", timeout=30000)
    patron.captura("salvat")


def test_def_252_facturile_preluate_intra_in_scadentar_si_le_stinge_banca(patron, preluata):
    """252. Pașii: Import date -> „Solduri parteneri” -> situația pe facturi -> previzualizarea: rândul ALFA are „FA-101, FA-102” în
    coloana „Facturi deschise” și 3.000,00 la debit -> „Salvează partenerii”: „3 parteneri salvați. 4 facturi deschise preluate (de încasat
    5.000,00 lei, de plătit 1.500,00 lei)” -> Facturi -> Scadențar: FA-101 restantă (5 zile de întârziere) 1.000,00, FA-102 2.000,00, FB-7
    „fără scadență în sistem” 2.000,00, fiecare „preluată din programul vechi” -> Bancă: extrasul cu +1.000 de la ALFA: „Potrivire exactă”
    -> „Contează”: nota 5121 = 4111 1.000,00 legată de FA-101 -> Scadențar: FA-101 nu mai e, FA-102 și FB-7 rămân.
    ROȘU înainte: „Același partener apare de două ori pe același cont” (forma pe facturi refuzată); cu forma pe solduri, scadențarul gol și
    linia băncii „niciun document deschis”."""
    f, pg = preluata, patron.pg
    _importa_pe_ecran(patron, f)
    _scadentar(patron, f)
    a, b, c = _id(f, "FA-101"), _id(f, "FA-102"), _id(f, "FB-7")
    ra, rb, rc = (_t(pg, ".sc-fact-btn[data-id='%s']" % x) for x in (a, b, c))
    patron.captura("scadentar")
    assert "FA-101 · %s" % ALFA[1] in ra and "5 zile de întârziere · preluată din programul vechi" in ra and "1.000,00 lei" in ra, ra
    assert "FA-102" in rb and "2.000,00 lei" in rb and "preluată din programul vechi" in rb, rb
    assert "FB-7 · %s" % BETA[1] in rc and "fără scadență în sistem · preluată din programul vechi" in rc and "2.000,00 lei" in rc, rc
    # Bancă: extrasul lunii, încasarea ALFA pentru FA-101
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    extras = "Data;Detalii;Suma\n%s;Incasare FA-101 CUI RO%s;1000,00\n" % (_ro(AZI), ALFA[0])
    pg.set_input_files("#bk-fisier", {"name": "extras_p252.csv", "mimeType": "text/csv", "buffer": extras.encode("utf-8")})
    # o singură linie: „1 linie importată” (singularul, `cate` din firme.js), nu „importate”
    pg.wait_for_function("() => document.querySelector('#bk-mesaj').innerText.includes('linie importată')", timeout=30000)
    assert "1 linie importată: 1 potrivită pe facturi, 0 fără potrivire" in " ".join(pg.inner_text("#bk-mesaj").split()), \
        pg.inner_text("#bk-mesaj")
    linie = pg.locator("#bk-lista .pf-frand", has_text="Incasare FA-101").first
    linie.wait_for(timeout=20000)
    patron.captura("banca_potrivire")
    assert "Potrivire exactă" in " ".join(linie.inner_text().split()), linie.inner_text()
    inainte = pg.inner_text("#bk-mesaj")
    linie.locator("[data-cont]").first.click()
    pg.wait_for_function("(p) => { const m = document.querySelector('#bk-mesaj').innerText; return m !== p && m.includes('creat'); }",
                         arg=inainte, timeout=30000)
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l '
               "ON l.inregistrare_id = i.id WHERE i.factura_id = %%s" % (f["schema"], f["schema"]), (a,))
    assert note == [("5121", "4111", "1000.00")], note
    _scadentar(patron, f)
    patron.captura("scadentar_dupa_incasare")
    assert pg.locator(".sc-fact-btn[data-id='%s']" % a).count() == 0, _t(pg, "#sc-lista")
    assert pg.locator(".sc-fact-btn[data-id='%s']" % b).count() == 1 and pg.locator(".sc-fact-btn[data-id='%s']" % c).count() == 1


def test_def_252_factura_preluata_n_are_actiuni_de_document_fiscal(patron, preluata):
    """252. Pașii: Scadențar -> rândul FA-102 -> detaliul: „preluată din programul vechi”, „neîncasată”, data, scadența, clientul, textul
    „Soldul ei e în balanța de deschidere: nu se contează și nu intră în declarații.” și „Rest la preluare 2.000,00 RON”; fără „PDF
    factură”, „Stornează”, „Trimite în SPV”. ROȘU înainte: factura preluată nu exista (nimic de deschis)."""
    f, pg = preluata, patron.pg
    if not sql('SELECT count(*) FROM "%s".facturi WHERE tip = \'preluata\'' % f["schema"])[0][0]:
        _importa_pe_ecran(patron, f)          # rulat singur (mutația lui): facturile preluate, pe ecran, ca în testul de mai sus
    _scadentar(patron, f)
    pg.click(".sc-fact-btn[data-id='%s']" % _id(f, "FA-102"))
    pg.wait_for_selector("#fd-preluata", timeout=25000)
    t = patron.fereastra()
    patron.captura("detaliu")
    assert "preluată din programul vechi" in t and "neîncasată" in t.lower(), t[:600]
    assert "Soldul ei e în balanța de deschidere: nu se contează și nu intră în declarații." in t, t[:600]
    assert "Rest la preluare" in t and "2.000,00 RON" in t, t[:600]
    for sel in ("#fd-pdf", "#fd-storno", "#fd-spv", "#fd-email", "#fd-transforma", "#fd-chitanta"):
        assert pg.locator(sel).count() == 0, sel
