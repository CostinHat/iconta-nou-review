# -*- coding: utf-8 -*-
"""Lotul 12, comanda Costin 12.1 (verbatim în DECIZII „Comanda 12.1”), pachetul `scad` — pașii contabilului pe aplicația din index, pe baza de
TEST, pe o firmă NOUĂ de test (`firma_noua`), plătitoare de TVA. CUI-ul furnizorului / clientului: DANTE INTERNATIONAL SA 14399840 (cifra de
control verificată cu algoritmul din CLAUDE.md).

  466 Scadențar: facturi încasate apar neîncasate (grav).         468 Scadențar: totalul pe client adună lei cu euro (grav).
  467 Scadențar: „Fișă client” nu deschide fișa sau factura.     469 Scadențar: butonul ales apare gri, ca dezactivat.
  477 Facturi primite: lipsește introducerea manuală (grav).       418 Import e-Factura: după „Altă livrare” confirmarea rămâne.
  C104 importul XML pierde unitatea de măsură.                     C105 „Validare factură”: TVA și Total neformatate.
  Decizia Costin „cursul vechi la validare (a)”: anunțul la validarea facturii primite în valută, ca la emitere.

DATE DE PORNIRE fără ecran (declarate, regula lui 429): încasarea prin bancă legată de factură (nota 5121 = 4111 cu `factura_id`, ce scrie
reconcilierea bancară la „Contează” — `e2e_lot72_contab` probează drumul acela) și factura emisă în EUR (curs 5, 2.500 lei în evidență) se
scriu cu SQL; NIR-ul „fără factură” și factura din XML intră pe rutele ecranelor.

Temei: CF art.290 alin.(2) și HG 1/2016 pct.35 alin.(1) (cursul BNR al facturii în valută — textul în `core/uc_factura_primita.py`);
OMFP 1802/2014 pct.322 alin.(1) (plata stinge creanța la valoarea din evidență — restul în valută). Structură (EN 16931, nu normă): BT-130
unitatea de măsură a liniei (UN/ECE Rec 20: H87, MTR, KGM, C62)."""
import datetime as _dt
import io
import re
import time

import pytest

from conftest import _db, firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, emite_api, pregateste_firma

AZI = _dt.date.today()
PROBA_XML = "/home/costin/ghid_incoming/lot12_fisiere_proba/F1_efactura_DANTE_DNT-RT-1020.xml"


@pytest.fixture(scope="module")
def firma_scad_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_scad(patron, firma_scad_noua):
    pregateste_firma(patron, firma_scad_noua, regim_fiscal="profit")
    return firma_scad_noua


def _lei(x):
    """Suma cum o scrie ecranul (`bani`): 1.234,56."""
    s = "{:,.2f}".format(float(x))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _t(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _emisa(patron, firma, pret):
    """Factura emisă de 1 × `pret` lei, 21% (pe ruta formularului), către DANTE; scadența scrisă în formular: azi + 30 de zile (`emite_api`)."""
    return emite_api(patron, firma, linii=[{"descriere": "Servicii E2E scadentar", "cantitate": 1, "um": "buc", "pret_unitar": pret,
                                            "cota_tva": 21, "cota_propusa": 21, "articol_id": None}])


def _incasare_banca(firma, fid, suma):
    """Date de pornire: nota băncii legată de factură (5121 = 4111), cum o scrie reconcilierea la „Contează”."""
    s = firma["schema"]
    # nota și rândul ei într-o SINGURĂ tranzacție, ca reconcilierea: regula de fond din bază (`regula_linii_nota`) nu lasă rânduri
    # adăugate unei note validate într-o tranzacție anterioară
    with _db().get_conn() as conn, conn.cursor() as cur:
        # date-de-pornire: nota băncii legată de factură, cum o scrie reconcilierea la „Contează” (drumul acela îl probează e2e_lot72_contab)
        cur.execute('INSERT INTO "%s".inregistrari (data, descriere, sursa, status, factura_id) VALUES (%%s, %%s, \'banca\', \'validata\', %%s) '
                    "RETURNING id" % s, (AZI, "Încasare extras E2E", fid))
        iid = cur.fetchone()[0]
        # date-de-pornire: rândul 5121 = 4111 al aceleiași note, în aceeași tranzacție (regula_linii_nota)
        cur.execute('INSERT INTO "%s".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%%s, \'5121\', \'4111\', %%s)'
                    % s, (iid, suma))
        conn.commit()


def _emisa_eur(firma, numar, total, total_lei, scadenta):
    s = firma["schema"]
    # date-de-pornire: factura în EUR cu cursul fix 5 (2.500 lei în evidență), scadentă ieri — formularul ia cursul BNR al zilei, nu cursul probei
    return sql('INSERT INTO "%s".facturi (numar, serie, data_emitere, data_scadenta, directie, total, tva, total_lei, tva_lei, curs_bnr, '
               "moneda, tert_nume, tert_cui, status, tip) VALUES (%%s, NULL, %%s, %%s, 'emisa', %%s, 0, %%s, 0, 5, 'EUR', "
               "'DANTE INTERNATIONAL SA', '14399840', 'emisa', 'factura') RETURNING id" % s,
               (numar, AZI, scadenta, total, total_lei))[0][0]


def _scadentar(patron, firma):
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-scadentar")
    patron.pg.click("#fac-scadentar")
    patron.pg.wait_for_selector("#sc-facturi", timeout=25000)


# ── 466 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_466_factura_incasata_prin_banca_nu_apare_in_scadentar(patron, firma_scad):
    """466. Pașii: două facturi emise de 121,00 lei; prima încasată integral prin bancă, a doua cu 21,00 lei -> Facturi -> Scadențar ->
    „Facturi neîncasate”: prima NU apare, a doua apare cu 100,00 lei („încasată parțial, rest din 121,00 lei”)."""
    a, b = _emisa(patron, firma_scad, 100.0), _emisa(patron, firma_scad, 100.0)
    _incasare_banca(firma_scad, a["factura_id"], 121)
    _incasare_banca(firma_scad, b["factura_id"], 21)
    _scadentar(patron, firma_scad)
    pg = patron.pg
    patron.captura("scadentar_facturi")
    assert pg.locator(".sc-fact-btn[data-id='%s']" % a["factura_id"]).count() == 0, _t(pg, "#sc-lista")   # încasată: nimic de încasat
    rand = _t(pg, ".sc-fact-btn[data-id='%s']" % b["factura_id"])
    assert "100,00 lei" in rand and "încasată parțial, rest din 121,00 lei" in rand, rand          # 121 − 21 = 100 de încasat


# ── 468 / 467 / 469 ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_468_fisa_client_tine_leii_separat_de_euro(patron, firma_scad):
    """468. Pașii: DANTE are o factură în lei (1.210,00 lei, în termen) și una în euro (500,00 EUR, scadentă ieri) -> Scadențar -> „Fișă
    client”: rândul DANTE spune „500,00 EUR restant · 1.210,00 lei + 500,00 EUR” (nu 1.710 „lei”); fișa lui arată „De încasat: 1.210,00
    lei + 500,00 EUR” și „Restant: 500,00 EUR”."""
    s = firma_scad["schema"]
    # fișa clientului pornește de la zero în testul ăsta: facturile de dinainte (466) declarate încasate integral (`platita_la`, ca
    # chitanța integrală — `facturi_api._cu_stare_incasare`). Notele băncii lui 466 rămân: sunt validate, iar nota validată nu se șterge.
    for (fid,) in sql('SELECT id FROM "%s".facturi WHERE directie = \'emisa\'' % s):
        # date-de-pornire: facturile testului 466 închise ca încasate integral, ca fișa să pornească de la zero; o încasare reală ar lăsa note validate în fișă
        sql('UPDATE "%s".facturi SET platita_la = now() WHERE id = %%s' % s, (fid,))
    lei = _emisa(patron, firma_scad, 1000.0)   # scadența din formular: azi + 30 de zile, în termen
    eur = _emisa_eur(firma_scad, "E2E-EUR-%d" % (time.time() % 100000), 500, 2500, AZI - _dt.timedelta(days=1))
    _scadentar(patron, firma_scad)
    pg = patron.pg
    pg.click("#sc-clienti")
    pg.wait_for_selector(".sc-client-btn", timeout=20000)
    rand = _t(pg, ".sc-client-btn[data-cheie='14399840']")
    patron.captura("fisa_client_lista")
    assert "500,00 EUR restant · 1.210,00 lei + 500,00 EUR" in rand, rand
    assert "1.710" not in rand, rand
    pg.click(".sc-client-btn[data-cheie='14399840']")
    pg.wait_for_selector("#sc-fisa-sold", timeout=20000)
    sold = _t(pg, "#sc-fisa-sold")
    patron.captura("fisa_client")
    assert "De încasat: 1.210,00 lei + 500,00 EUR" in sold and "Restant: 500,00 EUR" in sold, sold
    lista = _t(pg, "#sc-fisa-lista")
    assert "1.210,00 lei" in lista and "500,00 EUR" in lista, lista
    assert {int(x) for x in pg.eval_on_selector_all("#sc-fisa-lista .sc-fact-btn", "bs => bs.map(b => b.dataset.id)")} == {lei["factura_id"], eur}


def test_def_467_fisa_client_deschide_fisa_si_factura(patron, firma_scad):
    """467. Pașii: Scadențar -> „Fișă client” -> clic pe DANTE: se deschide „Fișă client · DANTE INTERNATIONAL SA”, cu facturile lui ->
    clic pe factura în lei: se deschide factura (detaliul cu „Descarcă PDF”); din „Facturi neîncasate”, clic pe factură: la fel."""
    f = _emisa(patron, firma_scad, 50.0)
    _scadentar(patron, firma_scad)
    pg = patron.pg
    pg.click("#sc-clienti")
    pg.click(".sc-client-btn[data-cheie='14399840']")
    pg.wait_for_selector("#sc-fisa-lista", timeout=20000)
    # titlul ferestrei e „Fișă client”, iar clientul e numit o dată, în antetul fișei (verificator ENTITATE_IN_TITLU)
    assert pg.inner_text("#sc-fisa-client").strip() == "DANTE INTERNATIONAL SA", patron.fereastra()[:300]
    pg.click("#sc-fisa-lista .sc-fact-btn[data-id='%s']" % f["factura_id"])
    pg.wait_for_selector("#fd-pdf", timeout=25000)
    patron.captura("factura_din_fisa")
    serie, numar = sql('SELECT serie, numar FROM "%s".facturi WHERE id = %%s' % firma_scad["schema"], (f["factura_id"],))[0]
    afis = "%s nr. %s" % (serie, numar[len(serie):]) if serie and numar.startswith(serie) else numar   # [443] seria și numărul separat
    assert afis in patron.fereastra(), patron.fereastra()[:300]
    _scadentar(patron, firma_scad)
    pg.click(".sc-fact-btn[data-id='%s']" % f["factura_id"])
    pg.wait_for_selector("#fd-pdf", timeout=25000)


def test_def_469_vederea_aleasa_e_activa_nu_dezactivata(patron, firma_scad):
    """469. Pașii: Scadențar: „Facturi neîncasate” e marcat ales (albastru închis, apăsat), NU dezactivat; „Fișă client” arată ca un buton
    obișnuit, activ -> clic pe „Fișă client”: marcajul trece pe el. DS cap.1 `.buton-activ`."""
    _scadentar(patron, firma_scad)
    pg = patron.pg

    def stare(sel):
        return pg.eval_on_selector(sel, "b => ({dez: b.disabled, activ: b.classList.contains('buton-activ'), apasat: b.getAttribute('aria-pressed'),"
                                        " fundal: getComputedStyle(b).backgroundColor})")
    patron.captura("vederea_aleasa")
    assert stare("#sc-facturi") == {"dez": False, "activ": True, "apasat": "true", "fundal": "rgb(26, 90, 148)"}, stare("#sc-facturi")
    s2 = stare("#sc-clienti")
    assert s2["dez"] is False and s2["activ"] is False and s2["apasat"] == "false", s2
    pg.click("#sc-clienti")
    pg.wait_for_timeout(300)
    assert stare("#sc-clienti")["activ"] is True and stare("#sc-facturi")["activ"] is False


# ── 477 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _primite(patron, firma):
    patron.firma(firma["nume"])
    _card(patron, "facturi", "#fac-primite")
    patron.pg.click("#fac-primite")
    patron.pg.wait_for_selector("#fp-manual", timeout=25000)


def test_def_477_factura_primita_introdusa_de_mana(patron, firma_scad):
    """477. Pașii: Facturi -> „Facturi primite (SPV)” -> „Introdu factura de mână” -> CUI 14399840 -> „Verifică la ANAF” (numele vine de
    la ANAF) -> seria DNT, numărul, data de azi -> linia „Servicii curierat”, 2 buc × 50,00, 21% (totalul arată 100,00 + TVA 21,00 = 121,00
    lei) -> contul 628 -> „Validează” -> „Validează”: „Validată.”, cu „← Înapoi”; în evidență: factura primită DNT, nota 628 = 401 100,00 și
    4426 = 401 21,00; a doua oară, aceeași factură e refuzată („e deja înregistrată”, refuzul comun al dublurii, lotul 12 C73.1)."""
    s = firma_scad["schema"]
    nr = "M%d" % (time.time() % 1000000)
    _primite(patron, firma_scad)
    pg = patron.pg
    pg.click("#fp-manual")
    pg.wait_for_selector("#pm-cui", timeout=20000)
    pg.fill("#pm-cui", "14399840")
    pg.click("#pm-verifica")
    pg.wait_for_function("() => document.querySelector('#pm-furnizor').value.length > 0", timeout=30000)
    assert "DANTE" in pg.input_value("#pm-furnizor")
    pg.fill("#pm-serie", "DNT")
    pg.fill("#pm-numar", nr)
    pg.fill("#pm-data", AZI.isoformat())
    pg.dispatch_event("#pm-data", "change")
    pg.wait_for_function("() => !document.querySelector('#pm-l1-cota').disabled", timeout=20000)
    pg.fill("#pm-l1-descriere", "Servicii curierat")
    pg.fill("#pm-l1-cantitate", "2")
    pg.fill("#pm-l1-pret", "50")
    pg.select_option("#pm-l1-cota", "21")
    pg.fill("#pr-cont", "628")
    tot = _t(pg, "#pm-total")
    assert "Total fără TVA 100,00 lei · TVA 21,00 lei" in tot and "Total 121,00 lei" in tot, tot
    patron.captura("formular")
    pg.click("#pm-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    patron.captura("validata")
    assert pg.locator("#pr-zona button", has_text="Înapoi").count() == 1 and pg.is_disabled("#pm-valideaza")
    fid, serie, total = sql('SELECT id, serie, total FROM "%s".facturi WHERE numar = %%s AND directie = \'primita\'' % s, (nr,))[0]
    assert (serie, float(total)) == ("DNT", 121.0)
    note = sql('SELECT l.cont_debit, l.cont_credit, l.suma FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               "WHERE i.factura_id = %%s ORDER BY l.cont_debit" % (s, s), (fid,))
    assert [(d, c, float(v)) for d, c, v in note] == [("4426", "401", 21.0), ("628", "401", 100.0)], note
    # a doua oară: refuzul numit, nimic scris
    r = _api(patron, "POST", "/tenants/%d/facturi-primite/manual" % firma_scad["tenant_id"],
             {"tert_tara": "RO", "tert_cui": "14399840", "tert_nume": "DANTE INTERNATIONAL SA", "serie": "DNT", "numar": nr,
              "data_emitere": AZI.isoformat(), "moneda": "RON", "cont": "628",
              "linii": [{"descriere": "Servicii curierat", "cantitate": "2", "um": "buc", "pret_unitar": "50", "cota_tva": "21"}]})
    assert r["status"] == 409 and r["json"]["detail"]["cod"] == "CHEIE_DUBLATA", r   # [lotul 12, C73.1] refuzul comun al dublurii
    assert sql('SELECT count(*) FROM "%s".facturi WHERE numar = %%s' % s, (nr,))[0][0] == 1


# ── C104 / C105 / 418 / cursul vechi — factura din XML ─────────────────────────────────────────────────────────────────────
def _proba_xml(firma, tag, moneda="RON", data=None):
    """Fișierul de probă real (F1, DANTE DNT-RT-1020: 20 H87, 50 MTR, 12,5 KGM, 1 C62), cu firma de test drept cumpărător, numărul `tag`
    și, la cerere, altă monedă / dată."""
    x = io.open(PROBA_XML, encoding="utf-8").read()
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma["schema"])[0][0] if c.isdigit())
    x = x.replace("DNT-RT-1020", tag).replace("RO401002001", "RO" + cifre).replace(">401002001<", ">%s<" % cifre)
    x = x.replace("F1 Comert Stoc SRL", firma["nume"])
    if data:
        x = x.replace("<cbc:IssueDate>2026-10-20</cbc:IssueDate>", "<cbc:IssueDate>%s</cbc:IssueDate>" % data)
    else:
        x = x.replace("2026-10-20", AZI.isoformat())
    if moneda != "RON":
        x = x.replace('currencyID="RON"', 'currencyID="%s"' % moneda).replace(
            "<cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>", "<cbc:DocumentCurrencyCode>%s</cbc:DocumentCurrencyCode>" % moneda)
    return x.encode("utf-8")


def _importa_si_deschide(patron, firma, tag, **k):
    _primite(patron, firma)
    pg = patron.pg
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml", "buffer": _proba_xml(firma, tag, **k)})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=40000)
    pg.locator(".fac-primita-btn", has_text=tag).click()
    pg.wait_for_selector("#pr-cont", timeout=20000)


def test_def_c105_validarea_arata_sumele_formatate(patron, firma_scad):
    """C105. Pașii: „Importă XML UBL” cu factura de probă (TVA 294,00, total 1.694,00) -> deschide-o: câmpurile TVA și Total arată
    „294,00 lei” și „1.694,00 lei” (nu „294.00” / „1694.00”)."""
    tag = "E2EC105-%d" % (time.time() % 100000)
    _importa_si_deschide(patron, firma_scad, tag)
    pg = patron.pg
    patron.captura("validare_sume")
    assert (pg.input_value("#pr-tva"), pg.input_value("#pr-total")) == ("294,00 lei", "1.694,00 lei")


def test_def_c104_importul_xml_pastreaza_unitatea_de_masura(patron, firma_scad):
    """C104. Pașii: factura de probă (marfă 20 buc, cablu 50 m, detergent 12,5 kg, transport 1) -> contul facturii 371, transportul pe 624
    -> „Validează”: liniile poartă buc / m / kg / buc, iar în stoc cablul intră în „m”, detergentul în „kg” (nu „buc”)."""
    s = firma_scad["schema"]
    tag = "E2EC104-%d" % (time.time() % 100000)
    _importa_si_deschide(patron, firma_scad, tag)
    pg = patron.pg
    pg.fill("#pr-cont", "371")
    pg.fill("#pr-cont-l3", "624")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată') || "
                         "!!document.querySelector('#nir-alta')", timeout=40000)
    if pg.query_selector("#nir-alta"):
        pg.click("#nir-alta")
        pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    patron.captura("validata")
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % s, (tag,))[0][0]
    assert sql('SELECT descriere, um FROM "%s".factura_linii WHERE factura_id = %%s ORDER BY id' % s, (fid,)) == [
        ("Marfa A", "buc"), ("Cablu electric cupru 3x1,5 mm", "m"), ("Detergent pudra vrac", "kg"), ("Transport marfa", "buc")]
    stoc = sql('SELECT a.denumire, a.um FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id WHERE m.factura_id = %%s '
               "ORDER BY m.id" % (s, s), (fid,))
    assert ("Cablu electric cupru 3x1,5 mm", "m") in stoc and ("Detergent pudra vrac", "kg") in stoc, stoc


def test_def_418_dupa_alta_livrare_confirmarea_ramane(patron, firma_scad):
    """418c (cazul lui Costin: „După «Altă livrare», aplicația sare în fereastra firmei fără niciun mesaj de confirmare”). Pașii: NIR „fără
    factură” de la DANTE (marfa nesosită cu factură) -> factura de marfă din XML pe 371 -> „Validează” -> caseta NIR -> „Altă livrare — nu e
    niciunul”: „Validată.” rămâne pe ecran, cu „← Înapoi”, după 1,5 s (nu sare singură); NIR-ul rămâne nelegat."""
    s, tid = firma_scad["schema"], firma_scad["tenant_id"]
    n = "N418-%d" % (time.time() % 100000)
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/nir" % tid, {"factura_sosita": False, "numar": n, "data": AZI.isoformat(),
                                                               "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
                                                               "linii": [{"denumire": "Marfa NIR 418", "articol_nou": True, "cantitate": 3,
                                                                          "pret_achizitie": 10, "cota_tva": 21}]}), "NIR")
    tag = "E2E418A-%d" % (time.time() % 100000)
    _importa_si_deschide(patron, firma_scad, tag)
    pg = patron.pg
    pg.fill("#pr-cont", "371")
    pg.fill("#pr-cont-l3", "624")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_selector("#nir-alta", timeout=40000)
    patron.captura("caseta_nir")
    pg.click("#nir-alta")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    pg.wait_for_timeout(1500)
    patron.captura("dupa_alta_livrare")
    assert pg.is_visible("#pr-zona") and "Validată" in pg.inner_text("#pr-zona")
    assert pg.locator("#pr-zona button", has_text="Înapoi").count() == 1
    assert sql('SELECT factura_id FROM "%s".nir WHERE numar = %%s' % s, (n,)) == [(None,)]


def _zi_fara_cursul_zilei():
    """O zi de factură al cărei curs BNR (comunicat în ziua bancară dinainte) nu poate fi încă în aplicație: ziua bancară așteptată e după
    azi (HG 1/2016 pct.35 alin.(1)) — atunci se folosește cursul de azi, mai vechi, iar anunțul trebuie să apară."""
    from core import curs_bnr as cb
    z = AZI + _dt.timedelta(days=2)
    while not (cb.ziua_bancara_asteptata(z) and cb.ziua_bancara_asteptata(z) > AZI):
        z += _dt.timedelta(days=1)
    return z


def test_decizia_curs_vechi_la_validare_anuntul_ca_la_emitere(patron, firma_scad):
    """Decizia Costin „cursul vechi la validare (a)” (lotul 11, §6): factura primită în EUR, datată într-o zi al cărei curs BNR nu e încă
    comunicat -> detaliul ei arată cursul cu care se va valida și anunțul „… lipsește din aplicație … factura validată acum îl păstrează (se
    fixează la validare)” (ca formularul de emitere, `curs_bnr.cursul_zilei_lipsa`) -> „Validează” pe 628: anunțul rămâne lângă „Validată.”"""
    z = _zi_fara_cursul_zilei()
    tag = "E2ECURS-%d" % (time.time() % 100000)
    _importa_si_deschide(patron, firma_scad, tag, moneda="EUR", data=z.isoformat())
    pg = patron.pg
    pg.wait_for_selector("#pr-valuta .pr-curs", timeout=40000)
    t = _t(pg, "#pr-valuta")
    patron.captura("curs_inainte")
    assert "lipsește din aplicație" in t and "factura validată acum îl păstrează (se fixează la validare)" in t, t
    pg.fill("#pr-cont", "628")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    patron.captura("curs_dupa")
    assert "factura validată acum îl păstrează" in _t(pg, "#pr-zona .pr-curs-validat"), _t(pg, "#pr-zona")
    assert re.search(r"din \d\d\.\d\d\.\d{4}", t), t
