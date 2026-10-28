# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul P: 442, 444 și deciziile din 10.3 pct.4
(fișa partenerului, întocmitorul bilanțului, CUI-ul fără „RO”).

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI (`firma_noua`). Nimic nu se scrie direct în bază (garda
`core/test_e2e_fara_date_fabricate.py`; afară de restaurarea întocmitorului cabinetului de test partajat, marcată): Date firmă și vectorul
fiscal pe rutele formularului (`POST firma-profil/date`, `POST vector`); facturile emise ale firmei către POPESCU ION (persoană fizică fără
cod), ALTEX și DANTE intră prin importul e-Factura al aplicației (`POST import-efactura`, XML-ul UBL al facturii emise — numărul, data,
CUI-ul și numele cum le scrie documentul; emiterea din formular nu primește un client fără cod fiscal, `facturi_api.cere_cod_partener`);
întocmitorul golit pe ruta „Date cabinet” (`POST /cabinet/intocmitor`). Răspunsul ANAF e servit de plasă pe server
(`anaf_api.CHEIE_SIMULAT`, `<dir>/anaf.json`), deci comparația fișă–ANAF rulează în aplicație. CUI-urile 14399840 / 2864518 au cifra de
control verificată (algoritmul din CLAUDE.md). Mutațiile: frontend_test/e2e/mut_lot11_p.json."""
import json
import os
import re
import urllib.error
import urllib.request
import uuid

import pytest

from conftest import BAZA, firma_noua, sql
from e2e_bloc_d import PATRON, _api as _api_cont, _token


def _ruta(cale, corp, ce):
    """O cerere pe ruta ecranului, cu sesiunea contabilului-șef (aceleași gărzi, același autor în jurnal ca pe ecran)."""
    st, r = _api_cont(PATRON, "POST", cale, corp)
    assert st == 200 and (not isinstance(r, dict) or r.get("ok") is not False), (ce, st, r)
    return r


@pytest.fixture(scope="module")
def firma_p():
    """Firmă NOUĂ: Date firmă (identitatea, banca, declarantul, „Mare contribuabil: Nu”, forma de proprietate 35; forma juridică, capitalul
    și „Entitate de interes public” rămân necompletate — le completează testele) și vectorul fiscal (micro, plătitoare de TVA, lunar,
    fără operațiuni intracomunitare), pe rutele formularului."""
    for f in firma_noua():
        tid = f["tenant_id"]
        _ruta("/tenants/%d/firma-profil/date" % tid,
              {"adresa": "Str. Probei 9", "oras": "Cluj-Napoca", "judet": "CJ", "caen": "6920", "banca": "BT",
               "iban": "RO59BTRLRONCRT0C69TEST01", "telefon": "0264111222", "declarant_nume": "POPESCU", "declarant_prenume": "ION",
               "declarant_functie": "ADMINISTRATOR", "reg_com": "J12/11/2020", "mare_contribuabil": False, "forma_proprietate": "35"},
              "Date firmă")
        _ruta("/tenants/%d/vector" % tid, {"regim_fiscal": "micro", "platitor_tva": True, "tip_decont": "lunar", "operatiuni_ic": False},
              "vectorul fiscal")
        assert sql('SELECT interes_public FROM "%s".firma_profil' % f["schema"]) == [(None,)]   # nedeclarat: îl cere bilanțul
        yield f


def _date_firma(patron, firma):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    return patron.pg


def _salveaza(pg):
    pg.evaluate("() => { const m = document.querySelector('#df-msg'); if (m) m.innerHTML = ''; }")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('alvat')", timeout=30000)


def _anaf(raspunsuri):
    """Răspunsurile ANAF ale plasei (`anaf_api._raspuns_simulat`): {cui: rezultat}."""
    d = os.environ["ICONTA_ANAF_SIMULAT"]
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "anaf.json"), "w", encoding="utf-8") as f:
        json.dump(raspunsuri, f, ensure_ascii=False)


#: factura EMISĂ de firmă (furnizorul = firma), în forma e-Factura (UBL 2.1, EN 16931): o linie de 100 lei + TVA 21%, fără adresa clientului
UBL_EMISA = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>{numar}</cbc:ID><cbc:IssueDate>{data}</cbc:IssueDate><cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO{cui_firma}</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
    </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>{nume_firma}</cbc:RegistrationName></cac:PartyLegalEntity>
  </cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party>{cod_client}<cac:PartyLegalEntity><cbc:RegistrationName>{client}</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount currencyID="RON">21.00</cbc:TaxAmount>
    <cac:TaxSubtotal><cbc:TaxableAmount currencyID="RON">100.00</cbc:TaxableAmount><cbc:TaxAmount currencyID="RON">21.00</cbc:TaxAmount>
      <cac:TaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:TaxCategory>
    </cac:TaxSubtotal></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:LineExtensionAmount currencyID="RON">100.00</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="RON">100.00</cbc:TaxExclusiveAmount><cbc:TaxInclusiveAmount currencyID="RON">121.00</cbc:TaxInclusiveAmount>
    <cbc:PayableAmount currencyID="RON">121.00</cbc:PayableAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine><cbc:ID>1</cbc:ID><cbc:InvoicedQuantity unitCode="H87">1</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="RON">100.00</cbc:LineExtensionAmount>
    <cac:Item><cbc:Name>Marfa</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent>
      <cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:ClassifiedTaxCategory></cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="RON">100.00</cbc:PriceAmount></cac:Price></cac:InvoiceLine>
</Invoice>"""


def _factura(firma, numar, cui, nume, data="2026-09-10"):
    """Factura emisă a firmei, adusă prin importul e-Factura al aplicației (`POST /tenants/{id}/import-efactura`, cu sesiunea
    contabilului-șef): XML-ul UBL al facturii, cu numărul, data, codul clientului (gol = persoană fizică fără cod) și numele cum le scrie
    documentul. Direcția (emisă) o decide aplicația, din CUI-ul furnizorului = CUI-ul firmei. -> id-ul facturii."""
    from xml.sax.saxutils import escape
    cui_firma = sql("SELECT cui FROM public.tenants WHERE id = %s", (firma["tenant_id"],))[0][0]
    cod = ("<cac:PartyTaxScheme><cbc:CompanyID>%s</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme>"
           % escape(cui)) if cui else ""
    xml = UBL_EMISA.format(numar=escape(numar), data=data, cui_firma=escape(str(cui_firma).upper().replace("RO", "").strip()),
                           nume_firma=escape(firma["nume"]), cod_client=cod, client=escape(nume))
    b = uuid.uuid4().hex
    corp = (("--%s\r\nContent-Disposition: form-data; name=\"fisiere\"; filename=\"%s.xml\"\r\nContent-Type: text/xml\r\n\r\n" % (b, numar))
            .encode("utf-8") + xml.encode("utf-8") + ("\r\n--%s--\r\n" % b).encode("utf-8"))
    req = urllib.request.Request(BAZA + "/tenants/%d/import-efactura" % firma["tenant_id"], method="POST", data=corp,
                                 headers={"Authorization": "Bearer " + _token(PATRON), "Content-Type": "multipart/form-data; boundary=" + b})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            st, rez = r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        st, rez = e.code, e.read().decode("utf-8", "replace")
    assert st == 200 and rez.get("importate") == 1 and not rez.get("erori"), (numar, st, rez)
    (fid,) = [x[0] for x in sql('SELECT id FROM "%s".facturi WHERE numar = %%s AND directie = \'emisa\'' % firma["schema"], (numar,))]
    return fid


# ── 442 — capitalul social lipsă în „Profil incomplet”, cu „blochează emiterea facturilor” ────────────────────────────────────────────
def test_def_442_capitalul_lipsa_apare_in_profil_incomplet(patron, firma_p):
    """442. Pașii: Date firmă (SRL fără formă juridică și fără capital) -> „Profil incomplet”: „Forma juridică — blochează emiterea
    facturilor” -> Forma juridică: SRL -> Salvează -> „Capital social subscris — blochează emiterea facturilor” (și în mesajul de după
    salvare) -> capitalul 200 -> Salvează -> panoul nu mai spune nimic despre emiterea facturilor. (Legea 31/1990 art.74 alin.(3))"""
    from e2e_lot10_date_firma import _panou_profil
    s = firma_p["schema"]
    # Date firmă -> forma juridică și capitalul goale -> Salvează (ruta formularului; pe firma nouă nu sunt completate încă)
    _ruta("/tenants/%d/firma-profil/date" % firma_p["tenant_id"], {"forma_juridica": None, "capital_subscris": None, "capital_varsat": None},
          "forma și capitalul goale")
    assert sql('SELECT forma_juridica, capital_subscris, capital_varsat FROM "%s".firma_profil' % s) == [(None, None, None)]
    pg = _date_firma(patron, firma_p)
    panou = _panou_profil(pg)
    assert "Forma juridică — blochează emiterea facturilor" in panou, panou
    patron.captura("forma_lipsa")
    pg.select_option("#df-forma_juridica", "SRL")
    _salveaza(pg)
    mesaj = pg.inner_text("#df-msg")   # mesajul de după salvare, citit înainte de a deschide cardul (la întoarcere formularul se redesenează)
    panou = _panou_profil(pg)
    assert "Capital social subscris — blochează emiterea facturilor" in panou, panou
    assert "emiterea facturilor" in mesaj, mesaj
    patron.captura("capital_lipsa")
    pg.fill("#df-capital_subscris", "200")
    _salveaza(pg)
    assert "emiterea facturilor" not in _panou_profil(pg, poate_lipsi=True)
    assert sql('SELECT forma_juridica, capital_subscris FROM "%s".firma_profil' % s)[0][0] == "SRL"


# ── decizia 10.3 — localitatea / județul în fișa partenerului; refuzul D406 trimite acolo ─────────────────────────────────────────────
def test_def_c69_d406_refuzul_trimite_la_fisa_partenerului(patron, firma_p):
    """Decizia 10.3 („refuzul declarației trimite direct acolo”). Pașii: o vânzare din 09.2026 către POPESCU ION (persoană fizică, fără
    localitate pe factură) -> Declarații, D406 pe 09.2026 -> refuz „lipsește localitatea … POPESCU ION (facturile L11P-1)”, cu butonul
    „Deschide Clienți” -> butonul deschide Clienți, cu rândul lui POPESCU ION evidențiat și localitatea în vedere -> Localitatea: Sibiu,
    Județul: Sibiu -> Salvează -> „localitatea și județul sunt în fișă” -> D406 pe 09.2026: <City>Sibiu</City>, din fișă."""
    from e2e_lot10_c69 import _declaratie, _xml
    s = firma_p["schema"]
    # facturile celorlalte teste ale modulului (ALTEX, DANTE) sunt din 08.2026, deci nu intră în D406 pe 09.2026
    _factura(firma_p, "L11P-1", "", "POPESCU ION")
    pg = _declaratie(patron, firma_p, "d406", 2026, 9)
    err = pg.inner_text(".dec-eroare")
    assert "lipsește localitatea" in err and "POPESCU ION (facturile L11P-1)" in err and "fișa partenerului" in err, err
    patron.captura("refuz")
    pg.click(".dec-eroare [data-ecran-destinatie='clienti']")
    pg.wait_for_selector("tr.val-evidentiat[data-partener='nume-POPESCU_ION']", timeout=30000)
    patron.captura("fisa")
    rand = "tr[data-partener='nume-POPESCU_ION']"
    pg.fill(rand + " input[id^='cl-oras-']", "Sibiu")
    pg.select_option(rand + " select[id^='cl-judet-']", "SB")
    pg.click(rand + " button.cl-salveaza")
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('sunt în fișă')", timeout=30000)
    assert sql('SELECT nume, oras, judet FROM "%s".clienti WHERE cui IS NULL' % s) == [("POPESCU ION", "Sibiu", "SB")]
    pg = _declaratie(patron, firma_p, "d406", 2026, 9)
    assert not pg.query_selector(".dec-eroare"), pg.inner_text(".dec-eroare")
    xml = _xml(pg)
    assert "<City>Sibiu</City>" in xml[xml.index("<Customers>"):xml.index("</Customers>")]   # S.AD.5 City — din fișa partenerului
    patron.captura("generat")


# ── 444 — numele de la ANAF diferit de fișă: se spune și se propune actualizarea ───────────────────────────────────────────────────────
def test_def_444_numele_anaf_diferit_de_fisa_se_propune_actualizarea(patron, firma_p):
    """444. Pașii: o vânzare către „ALTEX SRL” (CUI 2864518) -> Clienți: rândul ALTEX (fără fișă) -> „Verifică la ANAF” -> „Numele de la
    ANAF diferă: «ALTEX ROMANIA SRL» (în fișă: «ALTEX SRL»)” cu „Actualizează fișa cu numele de la ANAF” -> clic -> fișa are numele de la
    ANAF -> „Verifică la ANAF” din nou: „numele din fișă e același”."""
    from e2e_bloc_a import _card
    s = firma_p["schema"]
    _anaf({"2864518": {"denumire": "ALTEX ROMANIA SRL", "platitor_tva": True, "localitate": "Pantelimon", "judet": "IF",
                       "adresa": "Sos. Vergului 1"}})
    _factura(firma_p, "L11P-2", "RO2864518", "ALTEX SRL", data="2026-08-10")
    patron.firma(firma_p["nume"])
    _card(patron, "clienti", "#cl-tabel")
    pg = patron.pg
    rand = "tr[data-partener='cui-2864518']"
    if not pg.eval_on_selector(rand + " details.cl-actiuni", "d => d.open"):   # [lotul 13, DS cap.9 v2.83] acțiunile rândului, în meniul „Acțiuni”
        pg.click(rand + " details.cl-actiuni > summary")
    pg.click(rand + " button.cl-anaf")
    pg.wait_for_selector(rand + " button[id^='cl-anaf-aplica-']", timeout=30000)
    st = pg.inner_text(rand + " div[id^='cl-anaf-stare-']")
    assert "Numele de la ANAF diferă" in st and "ALTEX ROMANIA SRL" in st and "ALTEX SRL" in st, st
    patron.captura("diferit")
    pg.click(rand + " button[id^='cl-anaf-aplica-']")
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('numele din fișă e acum')",
                         timeout=30000)
    assert sql('SELECT nume, cui, oras, judet FROM "%s".clienti WHERE cui = %%s' % s, ("2864518",)) == [
        ("ALTEX ROMANIA SRL", "2864518", "Pantelimon", "IF")]   # CUI-ul fără „RO” (decizia 10.3); localitatea / județul de la ANAF
    if not pg.eval_on_selector(rand + " details.cl-actiuni", "d => d.open"):   # [lotul 13, DS cap.9 v2.83] acțiunile rândului, în meniul „Acțiuni”
        pg.click(rand + " details.cl-actiuni > summary")
    pg.click(rand + " button.cl-anaf")
    pg.wait_for_function("r => (document.querySelector(r + \" div[id^='cl-anaf-stare-']\") || {innerText: ''}).innerText.includes('e același')",
                         arg=rand, timeout=30000)
    patron.captura("acelasi")


# ── decizia 10.3 — întocmitorul (profilul cabinetului) și interesul public (Date firmă) blochează bilanțul ─────────────────────────────
def test_def_c69_bilant_cere_interesul_public_si_intocmitorul(patron, firma_p):
    """Decizia 10.3. Pașii: Bilanț 2025, S1005, „Descarcă XML” -> refuz „Nu e declarat dacă firma e entitate de interes public … Calitatea
    întocmitorului bilanțului lipsește …”, cu „Deschide Date firmă” -> Entitate de interes public: Nu -> Salvează -> Bilanț: refuz cu
    „Deschide Date cabinet” -> Calitatea: Contabil șef, Numele: IONESCU MARIA -> Salvează întocmitorul -> Bilanț: interes_public="0",
    calit_intocmit="12", nume_intocmit="IONESCU MARIA" (generatorul scria 0 / 12 / administratorul oricărei firme)."""
    from e2e_bloc_e import _bilant
    s, cab = firma_p["schema"], firma_p["cabinet_id"]
    inainte = sql("SELECT calit_intocmit, nume_intocmit, cif_intocmit, nri_intocmit FROM public.accounting_firms WHERE id = %s", (cab,))[0]
    # Setări cont -> Date cabinet -> calitatea, numele și CIF-ul întocmitorului goale -> Salvează (ruta butonului, administratorul cabinetului)
    _ruta("/cabinet/intocmitor", {"calit_intocmit": "", "nume_intocmit": "", "cif_intocmit": "", "nri_intocmit": inainte[3] or ""},
          "întocmitorul golit")
    assert sql("SELECT calit_intocmit, nume_intocmit, cif_intocmit FROM public.accounting_firms WHERE id = %s", (cab,)) == [(None, None, None)]
    try:
        _bilant(patron, firma_p, 2025, "s1005")
        pg = patron.pg
        pg.click("#bl-xml")
        pg.wait_for_selector("#bl-rez [data-ecran-destinatie='date_firma']", timeout=60000)
        rez = pg.inner_text("#bl-rez")
        assert "entitate de interes public" in rez and "Calitatea întocmitorului" in rez, rez
        patron.captura("refuz_firma")
        pg.click("#bl-rez [data-ecran-destinatie='date_firma']")
        pg.wait_for_selector("#df-interes_public", timeout=30000)
        pg.select_option("#df-interes_public", "0")
        _salveaza(pg)
        assert sql('SELECT interes_public FROM "%s".firma_profil' % s) == [(False,)]
        _bilant(patron, firma_p, 2025, "s1005")
        pg.click("#bl-xml")
        pg.wait_for_selector("#bl-rez [data-ecran-destinatie='date_cabinet']", timeout=60000)
        patron.captura("refuz_cabinet")
        pg.click("#bl-rez [data-ecran-destinatie='date_cabinet']")
        pg.wait_for_selector("#cab-calit_intocmit", timeout=30000)
        pg.select_option("#cab-calit_intocmit", "12")
        pg.fill("#cab-nume_intocmit", "IONESCU MARIA")
        pg.click("#cab-salveaza-intocmitor")
        pg.wait_for_function("() => (document.querySelector('#cab-msg-intocmitor') || {innerText: ''}).innerText.includes('a fost salvat')",
                             timeout=30000)
        assert sql("SELECT calit_intocmit, nume_intocmit FROM public.accounting_firms WHERE id = %s", (cab,)) == [(12, "IONESCU MARIA")]
        _bilant(patron, firma_p, 2025, "s1005")
        with pg.expect_response(lambda r: "/s1005-xml" in r.url, timeout=90000) as rsp:
            with pg.expect_download(timeout=90000):
                pg.click("#bl-xml")
        xml = rsp.value.json()["xml"]
        at = dict(re.findall(r'\b(interes_public|calit_intocmit|nume_intocmit)="([^"]*)"', xml))
        assert at == {"interes_public": "0", "calit_intocmit": "12", "nume_intocmit": "IONESCU MARIA"}, at
        patron.captura("generat")
    finally:
        # date-de-pornire: restaurează întocmitorul cabinetului de test partajat la valorile citite înainte (curățenie, nu date ale probei)
        sql("UPDATE public.accounting_firms SET calit_intocmit = %s, nume_intocmit = %s, cif_intocmit = %s, nri_intocmit = %s WHERE id = %s",
            tuple(inainte) + (cab,))


# ── decizia 10.3 — CUI-ul fără „RO”, „RO” la afișare după starea de plătitor ─────────────────────────────────────────────────────────
def test_decizia_103_cui_fara_ro_si_ro_la_afisare(patron, firma_p):
    """Decizia 10.3. Pașii: Clienți -> rândul unei vânzări către „RO 14399840” (scris cu „RO” și spațiu) -> Salvează (fișa nouă) -> fișa are
    CUI-ul 14399840, fără „RO” -> Date firmă (firma e plătitoare de TVA): CUI-ul arătat cu „RO” în față (CF art.318 alin.(1)), iar în bază
    fără."""
    from e2e_bloc_a import _card
    s = firma_p["schema"]
    _factura(firma_p, "L11P-3", "RO 14399840", "DANTE INTERNATIONAL SA", data="2026-08-11")
    assert sql('SELECT tert_cui, tert_platitor_tva FROM "%s".facturi WHERE numar = %%s' % s, ("L11P-3",)) == [("14399840", True)]
    patron.firma(firma_p["nume"])
    _card(patron, "clienti", "#cl-tabel")
    pg = patron.pg
    rand = "tr[data-partener='cui-14399840']"
    pg.fill(rand + " input[id^='cl-oras-']", "București")
    pg.click(rand + " button.cl-salveaza")
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('sunt în fișă')", timeout=30000)
    assert sql('SELECT cui FROM "%s".clienti WHERE nume = %%s' % s, ("DANTE INTERNATIONAL SA",)) == [("14399840",)]
    cui_firma = sql('SELECT cui FROM "%s".firma_profil' % s)[0][0]
    pg = _date_firma(patron, firma_p)
    assert pg.input_value("#df-cui") == "RO" + cui_firma and not cui_firma.startswith("RO"), (pg.input_value("#df-cui"), cui_firma)
    patron.captura("cui_afisat")
