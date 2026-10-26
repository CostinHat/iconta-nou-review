# -*- coding: utf-8 -*-
"""Lotul 6, comanda 1 (Costin 16.10.2026, verbatim în DECIZII „Lotul 6, comanda 1”): 272–282, pe aplicația din index, pe baza de TEST.

277: un extras MT940 nou, încărcat o singură dată, era respins cu „Extras deja importat: 2 linii. Nu s-a adăugat nimic.” — duplicatul se
hotăra pe hash-ul fișierului întreg. Acum o linie e duplicat numai dacă aceeași mișcare (dată, sumă, sens, referință / descriere, cont)
există deja, iar mesajul spune ce s-a găsit deja și ce e nou.

278, 279: dispoziția de casă legată de factură, avansul și plafonul în formular; starea reală a notei la salvare și pe rând."""
import time

from conftest import alege_tipul, sql, zile_de_acum
from e2e_bloc_a import AZI, CLIENT, _card, emite_api, pregateste_firma

MT940 = """:20:EXTRAS20261016
:25:RO49AAAA1B31007593840000
:28C:00010/001
:60F:C261015RON10000,00
:61:2610161016C242,00NTRFNONREF
:86:Incasare FISCALOS ICONTA SRL CUI 55229657 contravaloare factura F1A4 din 16.10.2026 {tag}
:61:2610161016D12,50NCHGNONREF
:86:Comision administrare cont octombrie {tag}
:62F:C261016RON10229,50
"""


def _incarca(patron, nume, text, asteapta):
    pg = patron.pg
    pg.evaluate("() => { document.querySelector('#bk-mesaj').textContent = ''; }")
    pg.set_input_files("#bk-fisier", {"name": nume, "mimeType": "text/plain", "buffer": text.encode("utf-8")})
    pg.wait_for_function("(t) => document.querySelector('#bk-mesaj').innerText.includes(t)", arg=asteapta, timeout=30000)
    return pg.inner_text("#bk-mesaj")


def test_def_277_extrasul_nou_se_importa_iar_duplicatul_e_miscarea(patron, firma_e2e):
    """277. Bancă: extrasul MT940 nou respins ca „deja importat”.
    Pașii contabilului: încarcă extrasul MT940 din comandă — 2 linii importate, cu soldurile comparate; îl încarcă din nou — nicio linie
    nouă, cele 2 „găsite deja”, numite; încarcă extrasul zilei următoare, care le repetă și aduce o plată nouă — 1 importată, 2 găsite."""
    tag = "E2E277-%d" % time.time()
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    _card(patron, "banca", "#bk-fisier")
    text = MT940.format(tag=tag)
    m1 = _incarca(patron, "extras_%s.sta" % tag, text, "importate")
    patron.captura("primul_import")
    assert "2 linii importate" in m1 and "găsite deja" not in m1, m1
    assert "Sold inițial la 15.10.2026: 10.000,00 RON în extras" in m1 and "Sold final la 16.10.2026: 10.229,50 RON în extras" in m1, m1
    assert patron.pg.locator("#bk-lista tbody.tn-nota", has_text="Comision administrare cont octombrie " + tag).count() == 1

    m2 = _incarca(patron, "extras_%s_iar.sta" % tag, text, "găsite deja")
    patron.captura("acelasi_extras")
    assert "Nicio linie nouă: nu s-a adăugat nimic." in m2, m2
    assert "2 linii găsite deja" in m2, m2
    assert "16.10.2026 · 242,00 lei · încasare · Incasare FISCALOS ICONTA SRL" in m2, m2
    assert "16.10.2026 · 12,50 lei · plată · Comision administrare cont octombrie " + tag in m2, m2

    urmator = text.replace(":62F:", ":61:2610171017D50,00NTRFREF77\n:86:Plata furnizor Z %s\n:62F:" % tag)
    m3 = _incarca(patron, "extras_%s_17.sta" % tag, urmator, "găsite deja")
    patron.captura("extras_suprapus")
    assert "1 linie importată" in m3 and "2 linii găsite deja" in m3, m3
    s = firma_e2e["schema"]
    assert sql('SELECT count(*) FROM "%s".extras_linii WHERE descriere LIKE %%s' % s, ("%" + tag,)) == [(3,)]


def test_def_276_banca_spune_formatele_si_compara_soldurile(patron, firma_e2e):
    """276. Bancă: formatele pe bănci, soldurile extrasului față de 5121, ajutorul fără termeni de programator.
    Pașii contabilului: deschide Bancă — vede formatele (MT940, ING, altă bancă), iar fereastra de alegere primește și .sta; deschide
    ajutorul „?” — fără „magic bytes” / „motor”; încarcă un extras MT940 — soldul inițial și final, cu 5121 și diferența; linia fără
    factură e „Fără potrivire”, nu „Fără match”."""
    tag = "E2E276-%d" % time.time()
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "banca", "#bk-fisier")
    formate = pg.inner_text("#bk-formate")
    assert "MT940" in formate and "ING" in formate and "Altă bancă" in formate, formate
    assert ".sta" in pg.get_attribute("#bk-fisier", "accept")
    pg.click("h2.pf-titlu [data-ajutor]")
    pg.wait_for_selector(".fereastra:last-of-type .aj-continut", timeout=20000)
    ajutor = pg.inner_text(".fereastra:last-of-type .aj-continut")
    patron.captura("ajutor")
    assert "recunoaște singură formatul" in ajutor and "magic bytes" not in ajutor and "motor" not in ajutor.lower(), ajutor
    pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
    pg.wait_for_selector("#bk-fisier", timeout=20000)
    m = _incarca(patron, "extras_%s.sta" % tag, MT940.format(tag=tag), "importate")
    patron.captura("solduri")
    assert "Sold inițial la 15.10.2026: 10.000,00 RON în extras, 0,00 în 5121 (din notele validate) — diferență 10.000,00." in m, m
    assert "Sold final la 16.10.2026: 10.229,50 RON în extras, 0,00 în 5121 (din notele validate) — diferență 10.229,50." in m, m
    rand = pg.locator("#bk-lista tbody.tn-nota", has_text="Comision administrare cont octombrie " + tag)
    # [309, 17.10.2026] comisionul e recunoscut din descriere: n-are factură de potrivit, are nota propusă (nu „Fără potrivire”, roșu)
    assert "Notă propusă 627 = 5121" in rand.inner_text() and "Fără potrivire" not in rand.inner_text() \
        and "match" not in rand.inner_text().lower(), rand.inner_text()


def _dispozitie(e, suma, cui):
    pg = e.pg
    pg.click("#c-toggle")
    pg.fill("#c-data", AZI.isoformat())
    pg.select_option("#c-cat", "incasare_client")
    pg.fill("#c-suma", str(suma))
    pg.fill("#c-cui", cui)


def test_def_278_dispozitia_leaga_factura_si_semnaleaza_avansul_si_plafonul(patron, firma_e2e):
    """278. Casă: încasare de 6.000 lei pe o factură de 242,00 — factura rămânea neîncasată, avansul și plafonul nesemnalate.
    Pașii contabilului: dispoziție nouă, încasare de la client, 6.000 lei, CUI-ul clientului -> formularul arată factura deschisă; o
    bifează -> ÎNAINTE de „Adaugă”: 5.758,00 lei avans (termenul facturii de avans) și plafonul de 5.000 lei/zi; salvează -> două
    operațiuni (242,00 pe factură, 5.758,00 avans), factura încasată."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E 278", "cantitate": 1, "um": "buc", "pret_unitar": 200.0,
                                             "cota_tva": 21, "cota_propusa": 21, "articol_id": None}])
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "casa", "#c-toggle")
    _dispozitie(patron, 6000, CLIENT["#em-cui"])
    pg.wait_for_selector("[data-cf='%s']" % f["factura_id"], timeout=20000)
    pg.check("[data-cf='%s']" % f["factura_id"])
    pg.wait_for_function("() => (document.querySelector('#c-previz-avert') || {innerText: ''}).innerText.includes('facturile alese')",
                         timeout=20000)
    avert = pg.inner_text("#c-previz-avert")
    patron.captura("formular")
    assert "5.758,00 lei depășesc facturile alese ale clientului: sunt avans de la client" in avert and "art.319 alin.(16)" in avert, avert
    assert "nu e legată" not in avert, "factura e aleasă: semnalul de factură nelegată dispare"
    assert "> 5.000,00 lei/zi" in avert and "Legea 70/2015" in avert, avert
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=20000)
    patron.captura("salvata")
    mesaj = pg.locator("p.pf-intro", has_text="Dispoziția a fost salvată").inner_text()
    assert "242,00 lei pe factură, 5.758,00 lei avans" in mesaj and "sunt ciorne" in mesaj, mesaj
    s = firma_e2e["schema"]
    assert sql('SELECT COALESCE(SUM(l.suma), 0)::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               "WHERE i.factura_id = %%s AND l.cont_credit = '4111' AND i.sursa = 'casa'" % (s, s), (f["factura_id"],)) == [("242.00",)]
    assert sql('SELECT suma::text, avans FROM "%s".casa_operatiuni ORDER BY id DESC LIMIT 2' % s) == [("5758.00", True), ("242.00", False)]
    # [lotul 11, 443, comanda 11.1 pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”] rândul registrului numește
    # factura „E2EA nr. 1”, nu „E2EA1”; numărul se potrivește întreg (nu și „nr. 12”)
    import re as _re
    from e2e_bloc_a import SERIE
    assert f["numar"].startswith(SERIE), f
    nr = "%s nr. %s" % (SERIE, f["numar"][len(SERIE):])
    assert pg.locator(".fereastra:last-of-type tbody.tn-nota", has_text=_re.compile(r"factura %s(?!\d)" % _re.escape(nr))).count() == 1


def test_def_279_starea_reala_a_notei_la_salvare_si_pe_rand(asistent, firma_e2e):
    """279. Casă / validare: „creată ca ciornă”, dar nota plecase la validare; apoi „Șterge” oferit și refuzat.
    Pașii asistentului (fără „Poate valida”): dispoziție de 150 lei, avans -> mesajul spune „trimisă la validare în cabinet”; rândul
    spune „notă la validare în cabinet” și nu oferă „Șterge”."""
    uid = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    era = sql("SELECT poate_valida FROM public.users WHERE id = %s", (uid,))[0][0]
    sql("UPDATE public.users SET poate_valida = false WHERE id = %s", (uid,))
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, firma_e2e["tenant_id"]))
    try:
        asistent.firma(firma_e2e["nume"])
        pg = asistent.pg
        _card(asistent, "casa", "#c-toggle")
        _dispozitie(asistent, 150, "")
        pg.fill("#c-doc", "DI-E2E-279")
        pg.wait_for_selector("#c-avans", timeout=20000)
        pg.check("#c-avans")
        pg.click("#c-adauga")
        pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=20000)
        mesaj = pg.locator("p.pf-intro", has_text="Dispoziția a fost salvată").inner_text()
        asistent.captura("salvata")
        assert "e trimisă la validare în cabinet" in mesaj and "Cabinetul o validează" in mesaj and "ciornă" not in mesaj, mesaj
        rand = pg.locator(".fereastra:last-of-type tbody.tn-nota", has_text="DI-E2E-279")
        assert "notă la validare în cabinet" in rand.inner_text(), rand.inner_text()
        assert rand.locator("[data-del]:not([aria-disabled='true'])").count() == 0, "nota la validare nu oferă ștergerea"   # [lotul 13, 675] inactiv cu motiv
    finally:
        sql("UPDATE public.users SET poate_valida = %s WHERE id = %s", (era, uid))


# ── SPV (273, 275, 289): pe baza de test cabinetul NU e conectat la SPV — exact starea pe care o raportase Costin ──────────────────
from e2e_bloc_a import _deschide_factura  # noqa: E402

UBL_PRIMITA = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>{numar}</cbc:ID><cbc:IssueDate>2026-10-10</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>FURNIZOR E2E SRL</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO40372003</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID></cac:TaxScheme></cac:PartyTaxScheme></cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>{client}</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO{cui}</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>21.00</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>121.00</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine><cbc:InvoicedQuantity>1</cbc:InvoicedQuantity><cbc:LineExtensionAmount>100</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>100</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Servicii E2E 273</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


def test_def_273_facturi_primite_spun_starea_spv_si_primesc_xml(patron, firma_e2e):
    """273. Facturi primite din SPV: „apar aici automat” fără conexiune; fără import UBL; câmpurile nepreluate nesemnalate.
    Pașii contabilului: deschide „Facturi primite” — starea SPV (necontectat, cu butonul spre Conectare SPV), fără „apar aici automat”;
    importă un XML UBL — factura apare; statutul de TVA al furnizorului e numit ca în D394 și AFLAT (ANAF sau codul de TVA RO din XML,
    BT-31 — deficiența 418a, comanda 9.3: „Contabilul nu trebuie să-l introducă manual”), nu cerut; validată, factura poartă statutul.
    Ramura „nu se poate afla -> se cere” e în `core/test_418_import_efactura.py` (ANAF simulat): aici aplicația de probă întreabă ANAF
    real, deci un furnizor „necunoscut” n-ar fi determinist.
    [16.10.2026, răspunsul Costin pct.4] „Terț plătitor” = un terț care plătește factura: nu e element UBL / RO_CIUS (numai beneficiarul
    plății, BT-59) și nu se declară în D394 (partenerul e furnizorul) — deci nu se cere pe factură; câmpul cerut e statutul TVA al
    furnizorului, numit ca în D394."""
    tag = "E2E273-%d" % time.time()
    pregateste_firma(patron, firma_e2e)
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    pg.wait_for_selector("#fp-spv .spv-stare-text", timeout=20000)
    stare = pg.inner_text("#fp-spv")
    assert "SPV: cabinetul nu e conectat" in stare and "Deschide Conectare SPV" in stare, stare
    assert "apar aici automat" not in pg.inner_text("#fp-lista")
    cui = sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"])[0][0]
    cifre = "".join(c for c in cui if c.isdigit())
    # [lotul 11] răspunsul ANAF pentru furnizorul facturii (plasa nu întreabă ANAF real: `anaf_api.CHEIE_SIMULAT`, 444): înregistrat în
    # scopuri de TVA, fără TVA la încasare — statutul se AFLĂ, nu se cere de mână (418a)
    import json as _json
    import os as _os
    with open(_os.path.join(_os.environ["ICONTA_ANAF_SIMULAT"], "anaf.json"), "w", encoding="utf-8") as _f:
        _json.dump({"40372003": {"denumire": "FURNIZOR E2E SRL", "platitor_tva": True, "tva_la_incasare": False}}, _f, ensure_ascii=False)
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml",
                                   "buffer": UBL_PRIMITA.format(numar=tag, client=firma_e2e["nume"], cui=cifre).encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=20000)
    patron.captura("importata")
    rand = pg.locator(".fac-primita-btn", has_text=tag)
    assert "de completat: dacă furnizorul e înregistrat în scopuri de TVA" not in rand.inner_text(), rand.inner_text()
    rand.click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    assert pg.query_selector("#pr-platitor") is None, "statutul furnizorului se cere de mână deși e aflat"
    t = " ".join(pg.inner_text(".fereastra:last-of-type").split())
    assert "înregistrat în scopuri de TVA" in t and "terț plătitor" not in t.lower(), t[:1500]
    assert "Aflat din ANAF, registrul contribuabililor" in t or "Aflat din XML-ul facturii: codul de TVA RO40372003" in t, t[:1500]
    pg.fill("#pr-cont", "628")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=20000)
    patron.captura("validata")
    # statutul e cel aflat (ANAF la data facturii, altfel XML-ul): scris pe factură, nu lăsat necunoscut
    assert sql('SELECT tert_platitor_tva IS NOT NULL FROM "%s".facturi WHERE numar = %%s' % firma_e2e["schema"], (tag,)) == [(True,)]


def test_def_275_factura_emisa_arata_starea_spv_si_drumul_spre_conectare(patron, firma_e2e):
    """275. Factura emisă: starea SPV lipsea; „Conectează ANAF (SPV)…” fără buton.
    Pașii contabilului: emite o factură; Istoric facturi — „netrimisă în SPV · termen ZZ.LL.AAAA”; detaliul — la fel; „Trimite în SPV” ->
    refuzul spune că cabinetul nu e conectat și are butonul „Deschide Conectare SPV”, care deschide panoul de conectare."""
    pregateste_firma(patron, firma_e2e)
    f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E 275", "cantitate": 1, "um": "buc", "pret_unitar": 200.0,
                                             "cota_tva": 21, "cota_propusa": 21, "articol_id": None}])
    _deschide_factura(patron, firma_e2e, f["factura_id"])
    pg = patron.pg
    st = pg.inner_text("#fd-stare-spv")
    assert st.startswith("netrimisă în SPV · termen "), st
    pg.click("#fd-spv")
    pg.click("#ca-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-spv-zona') || {innerText: ''}).innerText.includes('nu e conectat la SPV')",
                         timeout=20000)
    pg.wait_for_selector("#fd-spv-zona [data-ecran-destinatie='conectare_spv']", timeout=20000)
    patron.captura("refuz_spv")
    pg.click("#fd-spv-zona [data-ecran-destinatie='conectare_spv']")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].some((f) => f.innerText.includes('Conectare SPV') "
                         "&& f.innerText.includes('Neconectat'))", timeout=20000)
    patron.captura("panou_spv")


def test_def_289_starea_spv_in_fereastra_firmei_setari_si_ghid(patron, firma_e2e):
    """289. Conexiunea SPV: fereastra firmei fără stare; ghidul de bun venit fără pasul SPV.
    Pașii contabilului: deschide firma — linia „SPV: cabinetul nu e conectat…” cu butonul spre Conectare SPV; Setări cont → Conectare SPV —
    „Neconectat: facturile nu pleacă…”; „?” general — pasul cabinetului, cu textul cerut."""
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    pg.wait_for_selector("#firma-spv .spv-stare-text", timeout=20000)
    linie = pg.inner_text("#firma-spv")
    patron.captura("fereastra_firmei")
    assert "SPV: cabinetul nu e conectat" in linie and "Deschide Conectare SPV" in linie, linie
    patron.acasa()   # fereastra firmei se închide; „?” general e în bara de sus
    pg.click("#nav-ghid")
    pg.wait_for_selector("#ans-spv", timeout=20000)
    ghid = pg.inner_text("#ans-spv")
    patron.captura("ghid")
    assert ("Conectează cabinetul la SPV: Setări cont → Conectare SPV. Te autentifici o singură dată cu certificatul digital; conexiunea "
            "acoperă toate firmele pentru care ai împuternicire la ANAF. Fără acest pas facturile nu pleacă în SPV și nici cele de la "
            "furnizori nu vin automat.") in ghid, ghid


def test_def_289_certificatul_fara_drept_pe_cui_e_spus_exact_peste_tot(patron, firma_e2e):
    """289, completarea Costin 17.10.2026 pct.2: „Fereastra firmei (starea SPV de la 289) și refuzul de la «Trimite în SPV» trebuie să spună
    contabilului exact asta: certificatul conectat nu are drept SPV pentru CUI-ul acestei firme, cu ce are de făcut. Conexiunea activă fără
    drept pe CUI nu se arată ca «conectat».” Pașii: cabinetul conectat (token activ), iar citirea automată a primit pe CUI-ul firmei „Nu aveti
    drept in SPV” -> fereastra firmei: „fără drept pentru această firmă”, cu ce faci, fără „conectat”; Setări cont -> Conectare SPV: firma
    în lista celor verificate, fără drept; „Trimite în SPV” pe o factură: același refuz, fără încărcare, cu butonul spre Conectare SPV."""
    from core import spv_conector as sc
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tid,))[0][0]
    cui = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"])[0][0] if c.isdigit())
    assert sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = %s AND activ", (cab,)) == [(0,)], "premisa: neconectat"
    tok = sql("INSERT INTO public.spv_token (accounting_firm_id, serial_certificat, access_token, refresh_token, access_expira, "
              "refresh_expira, activ) VALUES (%s, 'E2E-289', %s, %s, now() + interval '30 days', now() + interval '300 days', true) "
              "RETURNING id", (cab, sc.cripteaza("x.e30.y"), sc.cripteaza("r")))[0][0]
    raspuns = "Nu aveti drept in SPV pentru CIF=%s" % cui
    sql("INSERT INTO public.spv_cui_acoperit (token_id, cui, verificat_la, are_drept, eroare, mesaje) VALUES (%s, %s, now(), false, %s, 0)",
        (tok, cui, raspuns))
    try:
        f = emite_api(patron, firma_e2e, linii=[{"descriere": "Servicii E2E 289", "cantitate": 1, "um": "buc", "pret_unitar": 200.0,
                                                 "cota_tva": 21, "cota_propusa": 21, "articol_id": None}])
        asteptat = sc.mesaj_fara_drept(cui, raspuns)
        patron.firma(firma_e2e["nume"])
        pg = patron.pg
        pg.wait_for_selector("#firma-spv .spv-stare-text", timeout=20000)
        linie = pg.inner_text("#firma-spv")
        patron.captura("fereastra_firmei")
        assert linie.startswith("SPV: fără drept pentru această firmă. " + asteptat) and "conectat" not in linie.replace(
            "Certificatul conectat", "").replace("conectezi cabinetul", "").replace("Conectare SPV", ""), linie
        _deschide_factura(patron, firma_e2e, f["factura_id"])
        pg.click("#fd-spv")
        pg.click("#ca-ok")
        pg.wait_for_function("(t) => (document.querySelector('#fd-spv-zona') || {innerText: ''}).innerText.includes(t)",
                             arg=asteptat[:60], timeout=20000)
        pg.wait_for_selector("#fd-spv-zona [data-ecran-destinatie='conectare_spv']", timeout=20000)
        patron.captura("refuz_trimite")
        assert sql('SELECT count(*) FROM "%s".efactura_trimiteri WHERE factura_id = %%s' % firma_e2e["schema"], (f["factura_id"],)) == [(0,)], \
            "nimic încărcat"
        pg.click("#fd-spv-zona [data-ecran-destinatie='conectare_spv']")
        pg.wait_for_selector("#spv-cuiuri .spv-cui[data-cui='%s']" % cui, timeout=20000)
        patron.captura("conectare_spv")
        # [315, 17.10.2026] Conectare SPV: explicația o dată, sus; pe firmă numai rândul „<firmă> · fără drept în SPV · verificat …”
        rand = pg.inner_text("#spv-cuiuri .spv-cui[data-cui='%s']" % cui)
        assert "fără drept în SPV · verificat " in rand and "OMFP" not in rand, rand
        assert pg.inner_text("#spv-cuiuri").count("OMFP 660/2017") == 1 and raspuns in pg.inner_text("#spv-explicatie")
    finally:
        sql("DELETE FROM public.spv_cui_acoperit WHERE token_id = %s", (tok,))
        sql("DELETE FROM public.spv_token WHERE id = %s", (tok,))


def test_def_287_fara_validare_in_doi_pasul_urmator_e_depunerea(patron):
    """287. Declarații / roluri: D300 trimisă de administrator apărea „trimisă seniorului pentru validare”, deși validarea în doi e oprită.
    Pașii administratorului (cabinetul de test: validarea în doi oprită, are dreptul de depunere): D710 -> obligația -> „Trimite în coadă →”:
    „Trimisă în coadă … gata de depunere … o depui tu, din «De depus»”, nu „seniorului”."""
    from e2e_bloc_c import _curata_coada, _declaratie_pas1, _trimite_si_asteapta
    tid = 4838
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    pg = patron.pg
    try:
        _declaratie_pas1(patron, "Comert Micro TVA", "d710", 2026, luna=9, trim=3)
        pg.wait_for_selector("#d710-cod", timeout=60000)
        pg.select_option("#d710-cod", "121")
        pg.fill("#d710-i", "100")
        pg.fill("#d710-c", "150")
        pg.fill("#d710-cota", "1")
        pg.click("#d710-add")
        pg.click("#d710-regen")
        _trimite_si_asteapta(patron)
        patron.captura("trimisa")
        t = patron.fereastra()
    finally:
        _curata_coada(tid, peste)
    assert "Trimisă în coadă" in t and "gata de depunere" in t and "o depui tu" in t, t[:1500]
    assert "seniorului" not in t and "Trimisă în coada de validare" not in t, t[:1500]


def _ciorne_pe_card(pg):
    import re as _re
    t = pg.inner_text(".cab-card-sinteza[data-cheie='validat']")
    m = _re.search(r"(\d+) (?:notă a ta|note ale tale) în ciornă", t)
    return int(m.group(1)) if m else 0


def test_def_286_contoarele_paginii_principale_urmeaza_scrierile(patron, firma_e2e):
    """286. Pagina principală: contoarele cardurilor nu se schimbau după validare / respingere, ci la reîncărcarea forțată.
    Pașii: pagina principală deschisă; o notă nouă (ciornă) scrisă prin aplicație -> „note ale tale în ciornă” crește, fără
    reîncărcare; ștearsă -> scade la loc. Scrierea trece prin `api.js`, ca orice acțiune din ecrane."""
    patron.acasa()
    pg = patron.pg
    pg.wait_for_function("() => (document.querySelector('.cab-card-sinteza[data-cheie=validat]') || {innerText: ''}).innerText.length > 0",
                         timeout=20000)
    pg.wait_for_timeout(1500)
    inainte = _ciorne_pe_card(pg)
    nid = pg.evaluate("""async (tid) => {
        const m = await import('/static/js/api.js');
        const r = await m.api.post(`/tenants/${tid}/jurnal`, {descriere: 'Notă E2E 286', data: new Date().toISOString().slice(0, 10),
            linii: [{debit: '6022', credit: '5311', suma: '11.00'}]});
        return (r.nota || r).id;
    }""", firma_e2e["tenant_id"])
    pg.wait_for_function("(n) => { const t = document.querySelector('.cab-card-sinteza[data-cheie=validat]').innerText;"
                         " const m = t.match(/(\\d+) (?:notă a ta|note ale tale) în ciornă/); return (m ? +m[1] : 0) === n; }",
                         arg=inainte + 1, timeout=15000)
    patron.captura("dupa_nota")
    pg.evaluate("async ([tid, nid]) => { const m = await import('/static/js/api.js'); await m.api.del(`/tenants/${tid}/jurnal/${nid}`); }",
                [firma_e2e["tenant_id"], nid])
    pg.wait_for_function("(n) => { const t = document.querySelector('.cab-card-sinteza[data-cheie=validat]').innerText;"
                         " const m = t.match(/(\\d+) (?:notă a ta|note ale tale) în ciornă/); return (m ? +m[1] : 0) === n; }",
                         arg=inainte, timeout=15000)


def test_def_283_declaratii_intai_ce_datoreaza_firma_cu_termenul(patron):
    """283. Declarații: lista oferea toate cele ~30 de tipuri (și ale persoanelor fizice) și „Pasul 1 din 3 — alege firma” cu firma aleasă.
    Pașii: „Comert Micro TVA” -> Declarații: textul pasului nu mai cere firma; grupa „Datorate de firmă” vine întâi, cu perioada și termenul
    („D300 · T3/2026 · termen …”); alegerea ei fixează și perioada; restul, separat („Alte declarații”)."""
    from e2e_bloc_c import _deschide
    pg = patron.pg
    _deschide(patron, "Comert Micro TVA", "declaratii", "#dec-tip")
    intro = pg.inner_text(".mig-intro")
    assert intro == "Pasul 1 din 3 — alege tipul declarației și perioada.", intro
    grupe = pg.eval_on_selector_all("#dec-tip optgroup", "(gs) => gs.map((g) => g.label)")
    assert grupe == ["Datorate de firmă (din vectorul fiscal și din operațiile înregistrate)"], grupe   # [301] „Alte declarații” pliată, la cerere
    pg.click("#dec-alte")
    grupe = pg.eval_on_selector_all("#dec-tip optgroup", "(gs) => gs.map((g) => g.label)")
    assert grupe == ["Datorate de firmă (din vectorul fiscal și din operațiile înregistrate)", "Alte declarații"], grupe
    datorate = pg.eval_on_selector_all("#dec-tip optgroup:first-of-type option", "(os) => os.map((o) => o.textContent)")
    d300 = [t for t in datorate if t.startswith("D300 · T3/2026 · termen ")]
    assert d300, datorate
    pg.select_option("#dec-tip", label=d300[0])
    pg.wait_for_selector("#dec-trim", timeout=10000)
    patron.captura("datorate")
    assert (pg.input_value("#dec-trim"), pg.input_value("#dec-an")) == ("3", "2026")


def test_def_284_refuzul_d300_numeste_nota_iar_dupa_validare_declaratia_intra_singura(patron, firma_e2e):
    """284. D300 / control: refuzul de la „Trimite în coadă” spunea „4 note nevalidate”, fără să le numească.
    Pașii administratorului: o factură emisă (nota ei e ciornă) -> Declarații -> D300 pe luna ei, încheiată -> „Trimite în coadă →”: refuzul
    numără nota („Diferența pe contul 4427 o explică 1 notă nevalidată”), iar butonul o numește, cu butonul spre ea; butonul deschide Registrul jurnal cu nota
    evidențiată. Notele numite se validează -> declarația se generează din nou și intră singură în coadă, iar cine a trimis-o primește
    notificarea. Depunerea rămâne clicul contabilului (elementul e în coadă, nu depus)."""
    from e2e_bloc_a import _api
    from e2e_bloc_c import _curata_coada, _declaratie_pas1, _trimite_si_asteapta
    from e2e_lot72_declaratii import LUNA, ZI   # [lotul 10, 383] luna în curs nu se generează: factura și D300 pe luna încheiată
    pregateste_firma(patron, firma_e2e)
    emite_api(patron, firma_e2e, data_emitere=ZI)
    tid = firma_e2e["tenant_id"]
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    pg = patron.pg
    try:
        _declaratie_pas1(patron, firma_e2e["nume"], "d300", LUNA.an, luna=LUNA.luna)
        _trimite_si_asteapta(patron)
        pg.wait_for_selector(".coada-note-refuz button", timeout=30000)
        patron.captura("refuz")
        mesaj = pg.inner_text("#dec-coada-mesaj")
        assert "Diferența pe contul 4427 o explică 1 notă nevalidată." in mesaj and " — Factură " in mesaj, mesaj   # [lotul 11, 436] lângă buton, fraza numără nota; butonul o numește   # [302] ciorna n-are nr.
        assert "se generează din nou și intră singură în coadă" in mesaj and "notă(e) nevalidată(e)" not in mesaj, mesaj
        asteptare = sql("SELECT id, note_ids FROM public.declaratii_in_asteptare WHERE tenant_id = %s AND rezolvata_la IS NULL", (tid,))
        assert len(asteptare) == 1, asteptare
        note = asteptare[0][1]
        pg.click(".coada-note-refuz button")
        pg.wait_for_selector(".val-evidentiat[data-nota-id='%d']" % note[0], timeout=30000)
        patron.captura("nota_evidentiata")
        for nid in note:
            assert _api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, nid), {})["status"] == 200
        intrata = []
        for _ in range(90):
            intrata = sql("SELECT id, stare FROM public.declaratii_coada WHERE tenant_id = %s AND tip = 'd300' AND id > %s", (tid, peste))
            if intrata:
                break
            time.sleep(1)
        rez = sql("SELECT rezultat FROM public.declaratii_in_asteptare WHERE id = %s", (asteptare[0][0],))[0][0]
        assert intrata and intrata[0][1] != "depusa", (intrata, rez)
        notif = sql("SELECT text FROM public.notificari WHERE tip = 'declaratie_reluata' AND link = %s", ("validat:%d" % intrata[0][0],))
        assert notif and "notele au fost validate, declarația s-a generat din nou" in notif[0][0], notif
    finally:
        sql("DELETE FROM public.notificari WHERE tip = 'declaratie_reluata' AND text LIKE %s", ("%" + firma_e2e["nume"] + "%",))
        sql("DELETE FROM public.declaratii_in_asteptare WHERE tenant_id = %s", (tid,))
        _curata_coada(tid, peste)


def test_def_272_cui_nu_se_modifica_din_date_firma_ci_prin_corectura_administratorului(asistent, patron, firma_e2e):
    """272. Date firmă: un asistent junior modifica CUI-ul unei firme existente, cu documente.
    Pașii: asistentul (numai „Poate pregăti”) -> fereastra firmei -> Date firmă: CUI-ul se citește, nu se scrie, iar „Corectează CUI-ul”
    nu i se arată; cererea cu alt CUI e refuzată de server. Administratorul: „Corectează CUI-ul” -> CUI-ul corect -> avertismentul ->
    „Corectez CUI-ul” -> CUI-ul nou, cu rândul în jurnal.
    [lotul 11, decizia Costin 10.3 pct.4] Firma e plătitoare de TVA (`pregateste_firma`, pe rutele Date firmă + vector fiscal — și când
    testul rulează singur): Date firmă arată CUI-ul nou cu „RO” în față, iar în bază (ambele locuri) el stă fără „RO”."""
    from conftest import cui_cu_control
    from e2e_bloc_a import _api
    tid = firma_e2e["tenant_id"]
    pregateste_firma(patron, firma_e2e)   # plătitoare de TVA, lunar
    uid = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    era = sql("SELECT poate_valida, poate_depune FROM public.users WHERE id = %s", (uid,))[0]
    sql("UPDATE public.users SET poate_valida = false, poate_depune = false WHERE id = %s", (uid,))
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, tid))
    vechi = sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"])[0][0]
    nou = cui_cu_control(27272727)
    try:
        asistent.firma(firma_e2e["nume"])
        pg = asistent.pg
        pg.click("#fa-datefirma")
        pg.wait_for_selector("#df-salveaza", timeout=20000)
        assert pg.get_attribute("#df-cui", "readonly") is not None
        assert not pg.locator("#df-cui-corecteaza").is_visible(), "corectura e a administratorului"
        asistent.captura("asistent")
        r = _api(asistent, "POST", "/tenants/%d/firma-profil/date" % tid, {"cui": nou})
        assert r["status"] == 422 and "CUI-ul nu se modifică din Date firmă" in str(r["json"]), r
        patron.firma(firma_e2e["nume"])
        pg = patron.pg
        pg.click("#fa-datefirma")
        pg.wait_for_selector("#df-cui-corecteaza", timeout=20000)
        pg.click("#df-cui-corecteaza")
        pg.fill("#df-cui-nou", nou)
        pg.click("#df-cui-continua")
        pg.wait_for_selector("#df-cui-confirma", timeout=20000)   # avertismentul serverului, sub câmp, cu butonul de confirmare
        aviz = pg.inner_text("#df-cui-aviz")
        assert "Corectezi CUI-ul firmei din %s în %s" % (vechi, nou) in aviz, aviz
        patron.captura("avertisment")
        pg.click("#df-cui-confirma")
        pg.wait_for_function("() => (document.querySelector('#df-msg') || {innerText: ''}).innerText.includes('CUI-ul a fost corectat')",
                             timeout=20000)
        patron.captura("corectat")
        # [lotul 11, decizia Costin 10.3 pct.4: „CUI-ul se păstrează fără «RO» și fără spații; «RO» apare doar la afișare, după starea de
        # plătitor de TVA.”] firma e plătitoare: ecranul arată CUI-ul nou cu „RO”; în bază, în ambele locuri, fără „RO”
        assert sql('SELECT platitor_tva FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"]) == [(True,)]
        assert pg.input_value("#df-cui") == "RO" + nou, pg.input_value("#df-cui")
        assert sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % firma_e2e["schema"])[0][0] == nou, "Date firmă"
        assert sql("SELECT cui FROM public.tenants WHERE id = %s", (tid,))[0][0] == nou, "ambele locuri"
    finally:
        _api(patron, "POST", "/tenants/%d/cui/corectura" % tid, {"cui": vechi, "confirmat": True})
        sql("UPDATE public.users SET poate_valida = %s, poate_depune = %s WHERE id = %s", (era[0], era[1], uid))


def test_def_281_amortizarea_restanta_dintr_o_actiune_si_inchiderea_cu_confirmare(patron, firma_e2e):
    """281. Mijloace fixe / închidere: lunile de amortizare restante se generau lună cu lună, iar închiderea lunii nu se oprea.
    Pașii: un mijloc fix pus în funcțiune acum patru luni (100 lei pe lună), fără amortizare înregistrată; amortizarea lunii trecute
    generată și validată -> Închidere lună -> luna trecută: „Ce oprește închiderea” numește lunile anterioare (schimbă profitul), iar
    „Închide luna fără amortizarea lunilor anterioare” -> confirmarea -> luna se închide, cu confirmarea în istoric. Apoi luna se
    redeschide și „Generează amortizarea restantă” face câte o notă pe fiecare lună rămasă, dintr-o singură apăsare."""
    import datetime as _dt
    from e2e_bloc_a import _api
    from e2e_bloc_e import _card, _la_luna, _mf
    f = firma_e2e
    tid, sch = f["tenant_id"], f["schema"]
    trecuta = AZI.replace(day=1) - _dt.timedelta(days=1)
    m = AZI.year * 12 + AZI.month - 1 - 4
    pif = _dt.date(m // 12, m % 12 + 1, 10)
    mid = _mf(f, "MF281", "3000", 30, pif.isoformat())
    pg = patron.pg
    try:
        r = _api(patron, "POST", "/tenants/%d/amortizare?an=%d&luna=%d" % (tid, trecuta.year, trecuta.month), {})
        assert r["status"] == 200 and r["json"].get("nota_id"), r
        assert _api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (tid, r["json"]["nota_id"]), {})["status"] == 200
        _card(patron, f, "inchidere", "#il-prev")
        _la_luna(patron, "#il-prev", trecuta.year, trecuta.month)
        pg.wait_for_selector(".fereastra:last-of-type #il-lock-confirma", timeout=60000)
        zona = pg.inner_text(".fereastra:last-of-type #il-controale")
        assert "Ce oprește închiderea (1)" in zona and "amortizarea lunilor anterioare nu e înregistrată pe contul 2813" in zona, zona
        assert "schimbă profitul (D100/D101)" in zona, zona
        patron.captura("blocaj_confirmabil")
        pg.click(".fereastra:last-of-type #il-lock-confirma")
        pg.click("#ca-ok")
        pg.wait_for_function("() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-stare-perioada') || {})"
                             ".textContent.startsWith('Luna e blocată')", timeout=30000)
        patron.captura("inchisa_cu_confirmare")
        motiv = sql('SELECT motiv FROM "%s".perioade_inchideri WHERE an = %%s AND luna = %%s AND actiune = \'inchisa\' ORDER BY cand DESC '
                    "LIMIT 1" % sch, (trecuta.year, trecuta.month))[0][0]
        assert motiv and motiv.startswith("închisă cu confirmare explicită"), motiv
        assert _api(patron, "DELETE", "/tenants/%d/perioade-blocate?an=%d&luna=%d&motiv=proba%%20281" % (tid, trecuta.year, trecuta.month),
                    None)["status"] == 200
        _card(patron, f, "inchidere", "#il-prev")
        _la_luna(patron, "#il-prev", trecuta.year, trecuta.month)
        pg.wait_for_selector(".fereastra:last-of-type #il-amort-restanta", timeout=60000)
        pg.click(".fereastra:last-of-type #il-amort-restanta")
        pg.wait_for_function("() => ([...document.querySelectorAll('.fereastra')].pop().querySelector('#il-mesaj') || {innerText: ''})"
                             ".innerText.includes('generat')", timeout=60000)
        mesaj = pg.inner_text(".fereastra:last-of-type #il-mesaj")
        patron.captura("restanta")
        note = sql('SELECT numar FROM "%s".inregistrari WHERE sursa = \'amortizare\' ORDER BY data' % sch)
        luni = [n[0] for n in note]
        assert len(luni) == len(set(luni)) and len(luni) >= 3, luni
        assert ("%d note de amortizare generate" % (len(luni) - 1)) in mesaj, (mesaj, luni)
    finally:   # notele (una validată) rămân: firma probei se scoate la sfârșitul fișierului, iar nota validată nu se șterge
        sql('DELETE FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % sch, (trecuta.year, trecuta.month))
        sql('DELETE FROM "%s".mijloace_fixe WHERE id = %%s' % sch, (mid,))


_DEPASIRE_JS = """() => { const f = [...document.querySelectorAll('.fereastra')].pop(); const c = f && f.querySelector('.fereastra-corp');
    if (!c) return null; const late = [...c.querySelectorAll('*')].filter((e) => e.getBoundingClientRect().right > c.getBoundingClientRect().right + 2)
      .slice(0, 3).map((e) => e.tagName + (e.id ? '#' + e.id : '') + '.' + String(e.className).slice(0, 30));
    return {lat: c.scrollWidth, vizibil: c.clientWidth, late}; }"""


def _fara_derulare_laterala(pg, unde):
    d = pg.evaluate(_DEPASIRE_JS)
    assert d is not None, unde
    return [] if d["lat"] <= d["vizibil"] + 1 else ["%s: %d > %d %s" % (unde, d["lat"], d["vizibil"], d["late"])]


def test_def_285_nicio_fereastra_cu_derulare_laterala_iar_actiunea_se_vede(patron, firma_e2e):
    """285 (clasă, toate ferestrele). „nicio fereastră nu are derulare; acțiunea principală și mesajele de refuz/eroare se văd mereu
    (exemple: D300, mesajul de refuz și «Trimite în coadă» jos, tăiate; detaliul facturii, derulare orizontală)”.
    Pașii: fereastra firmei -> FIECARE card activ, deschis pe rând: conținutul ferestrei nu e mai lat decât ea (fereastra se lățește
    singură, `navigator._lateste`); detaliul unei facturi emise la fel; D300 cu „Din ce e făcută declarația” deschis: „Trimite în
    coadă →” și zona de mesaj rămân în fereastră (zona fixă de jos, `.bara-fixa`)."""
    from e2e_bloc_c import _declaratie_pas1
    from e2e_lot72_declaratii import LUNA, ZI
    pregateste_firma(patron, firma_e2e)
    fid = emite_api(patron, firma_e2e)["factura_id"]   # azi: Istoric facturi se deschide pe luna curentă
    pg = patron.pg
    patron.firma(firma_e2e["nume"])
    carduri = pg.eval_on_selector_all(".firme-optiune:not([disabled])", "(bs) => bs.map((b) => b.id)")
    assert len(carduri) >= 20, carduri
    rele = []
    for c in carduri:
        patron.firma(firma_e2e["nume"])
        pg.click("#" + c)
        pg.wait_for_timeout(2500)
        rele += _fara_derulare_laterala(pg, c)
    patron.firma(firma_e2e["nume"])
    pg.click("#fa-facturi")
    pg.wait_for_selector("#fac-istoric", timeout=20000)
    pg.click("#fac-istoric")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.wait_for_selector("#fd-pdf", timeout=25000)
    vp = pg.viewport_size
    pg.set_viewport_size({"width": 1100, "height": vp["height"]})   # ecran îngust: lățirea ferestrei nu mai ajunge, contează ruperea rândului
    pg.wait_for_timeout(1500)
    rele += _fara_derulare_laterala(pg, "detaliul facturii, 1100px")
    pg.set_viewport_size(vp)
    patron.captura("detaliu_factura")
    assert rele == [], rele
    # plasa pentru ecranele care vor veni: un conținut mai lat decât fereastra o lățește singură (navigator `_lateste`), fără să-l ceară ecranul
    pg.evaluate("() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); const d = document.createElement('div');"
                " d.style.width = '1300px'; d.style.height = '4px'; d.id = 'proba-lata'; c.appendChild(d); }")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().classList.contains('fer-tabel')", timeout=5000)
    pg.wait_for_timeout(500)   # `.fereastra { transition: max-width 0.18s }`
    assert _fara_derulare_laterala(pg, "conținut lat sintetic") == []
    # [lotul 10, 383] D300 pe luna încheiată (luna în curs nu se mai generează), cu o factură în ea
    emite_api(patron, firma_e2e, data_emitere=ZI)
    _declaratie_pas1(patron, firma_e2e["nume"], "d300", LUNA.an, luna=LUNA.luna)
    pg.wait_for_selector("#dec-trimite", timeout=90000)
    pg.evaluate("() => document.querySelectorAll('.fereastra details').forEach((d) => { d.open = true; })")
    pg.wait_for_timeout(500)
    vede = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop().querySelector('.fereastra-corp');
        const c = f.getBoundingClientRect(), b = document.querySelector('#dec-trimite').getBoundingClientRect();
        const z = document.querySelector('.bara-fixa').getBoundingClientRect();
        return {derulabil: f.scrollHeight > f.clientHeight, inauntru: b.top >= c.top && b.bottom <= c.bottom + 1,
                lipita_jos: Math.abs(z.bottom - c.bottom) <= 1}; }""")
    patron.captura("d300_lung")
    assert vede == {"derulabil": True, "inauntru": True, "lipita_jos": True}, vede   # nimic din conținut nu se vede sub zona fixă


def test_def_c41_registrul_fiscal_pe_profit_nu_cade(patron, firma_e2e):
    """C41 (găsit de garda 285, care deschide toate cardurile firmei). Registrul de evidență fiscală, varianta profit: „Nu s-a putut
    întocmi registrul” cu 500 de la server („relation firma_profil does not exist”) — la ORICE firmă, fiindcă use-case-ul îi dădea
    generatorului D101 conexiunea publică. Pașii: fereastra firmei -> „Registrul de evidență fiscală” (varianta profit, anul trecut):
    ecranul arată registrul sau refuzul datelor (422, cu motivul), niciodată o cădere; plasa refuză orice răspuns 5xx."""
    patron.firma(firma_e2e["nume"])
    pg = patron.pg
    with pg.expect_response(lambda r: "/registru-evidenta-fiscala?" in r.url, timeout=60000) as raspuns:
        pg.click("#fa-regfiscal")
    patron.captura("registru")
    assert raspuns.value.status < 500, raspuns.value.status


def test_def_290_eroarea_dispare_cand_campul_e_corectat(patron, browser, request):
    """290 (clasă, toate formularele). „Completează emailul mai întâi.” rămânea în fereastra de autentificare după completarea emailului;
    „Adaugă cel puțin o captură sau un fișier de export.” rămânea în Suport → Cerere import după atașarea fișierului.
    Pașii: (1) autentificare client: „Trimite-mi linkul” fără email -> eroarea; se scrie emailul -> eroarea dispare. (2) Suport ->
    „Cerere import din altă aplicație” -> „Trimite cererea” fără aplicație și fără fișier -> două erori (lângă câmp și a formularului);
    se scrie aplicația -> eroarea ei dispare; se atașează fișierul -> eroarea formularului dispare. Mecanismul e unul, în `api.js`
    (`stergeEroriDupaCorectare`), pentru toate formularele."""
    from conftest import BAZA, LAT, INALT
    ctx = browser.new_context(viewport={"width": LAT, "height": INALT})
    vp = ctx.new_page()
    try:
        vp.goto(BAZA + "/", wait_until="domcontentloaded")
        vp.wait_for_selector("#pagina-acces-btn", timeout=20000)
        vp.click("#pagina-acces-btn")
        vp.click("#acces-intra")
        vp.click("#lg-client")
        vp.click("#lgc-trimite")
        vp.wait_for_function("() => document.querySelector('#lgc-msg').innerText.includes('Completează emailul mai întâi.')", timeout=10000)
        vp.type("#lgc-email", "a@b.ro")
        assert vp.inner_text("#lgc-msg").strip() == "", vp.inner_text("#lgc-msg")
        # alt dialect al zonei de eroare (`login-eroare`, caseta cu fundal): autentificarea cabinetului fără parolă
        vp.click("#lgc-inapoi")
        vp.click("#lg-cabinet")
        vp.fill("#login-email", "a@b.ro")
        vp.click("#login-buton")
        vp.wait_for_selector("#login-eroare:not([hidden])", timeout=10000)
        vp.type("#login-parola", "x")
        assert vp.locator("#login-eroare").is_hidden(), vp.inner_text("#login-eroare")
    finally:
        ctx.close()
    pg = patron.pg
    patron.acasa()
    pg.click("[data-banda='raport']")
    pg.wait_for_selector(".rap-tab[data-tab='import']", timeout=20000)
    pg.click(".rap-tab[data-tab='import']")
    pg.click("#imp-trimite")
    pg.wait_for_function("() => document.querySelector('#imp-msg').innerText.includes('Adaugă cel puțin o captură')", timeout=10000)
    assert pg.locator(".msg-eroare[data-camp='imp-aplicatie']").count() == 1
    patron.captura("erori")
    pg.type("#imp-aplicatie", "WinMentor")
    assert pg.locator(".msg-eroare[data-camp='imp-aplicatie']").count() == 0, "eroarea câmpului corectat"
    pg.set_input_files("#imp-file", files=[{"name": "export.csv", "mimeType": "text/csv", "buffer": b"cont;sold\n5121;10\n"}])
    pg.wait_for_function("() => !document.querySelector('#imp-msg').innerText.includes('Adaugă cel puțin o captură')", timeout=10000)
    patron.captura("corectat")


def test_def_291_bulina_suport_numai_pentru_vestile_de_la_iconta(patron):
    """291. Bulina roșie de pe „Suport” apărea pentru cererea trimisă chiar de utilizator.
    Pașii: pagina principală, fără vești -> „Trimite sesizarea” -> pe „Suport” nu apare bulina (cererea mea); iConta răspunde -> bulina
    apare (1); firul se deschide -> bulina se stinge; iConta închide firul -> bulina apare (starea schimbată); firul se deschide -> se stinge."""
    from core import db, raportari_api as rap
    uid = sql("SELECT id FROM public.users WHERE email = 'patron@prisma-cont.test'")[0][0]
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.raportari")[0][0]
    # vești vechi ale contului comun (alte probe): se marchează citite, ca bulina să pornească de la zero
    for (r0,) in sql("SELECT id FROM public.raportari WHERE autor_id = %s", (uid,)):
        with db.get_conn() as c:
            rap.marcheaza_citit(c, r0, "utilizator")
    pg = patron.pg
    bulina = "[data-banda='raport'] .cab-card-badge"

    def asteapta_bulina(n):
        pg.wait_for_function("([s, n]) => { const e = document.querySelector(s); return (e ? +e.textContent : 0) === n; }", arg=[bulina, n],
                             timeout=20000)
    try:
        patron.acasa()
        pg.click("[data-banda='raport']")
        pg.wait_for_selector("#rap-text", timeout=20000)
        pg.fill("#rap-text", "Proba 291: nu se vede bulina pentru cererea mea.")
        pg.click("#rap-trimite")
        # confirmarea, nu primul text: „Se trimite...” apare înaintea cererii, iar rândul nu e încă în bază (cursa văzută 17.10.2026)
        pg.wait_for_function("() => document.querySelector('#rap-msg').innerText.includes('Sesizare trimisă')", timeout=20000)
        rid = sql("SELECT id FROM public.raportari WHERE autor_id = %s AND id > %s ORDER BY id DESC LIMIT 1", (uid, peste))[0][0]
        patron.acasa()
        pg.wait_for_selector("[data-banda='raport']", timeout=20000)
        pg.wait_for_timeout(1500)
        asteapta_bulina(0)
        patron.captura("dupa_cerere")
        with db.get_conn() as c:
            rap.adauga_mesaj(c, rid, None, "admin", "Ne uităm și revenim.")
        patron.acasa()
        asteapta_bulina(1)
        patron.captura("raspuns")
        pg.click("[data-banda='raport']")
        pg.click(".rap-fir[data-id='%d'] .rap-fir-cap" % rid)
        pg.wait_for_function("(id) => !document.querySelector(`.rap-fir[data-id='${id}'] .rap-badge-pct`)", arg=rid, timeout=10000)
        patron.acasa()
        asteapta_bulina(0)
        with db.get_conn() as c:
            rap.seteaza_stare(c, rid, "inchisa")
        patron.acasa()
        asteapta_bulina(1)
    finally:
        sql("DELETE FROM public.raportari_mesaje WHERE raportare_id IN (SELECT id FROM public.raportari WHERE autor_id = %s AND id > %s)",
            (uid, peste))
        sql("DELETE FROM public.raportari WHERE autor_id = %s AND id > %s", (uid, peste))


def test_def_292_fereastra_cozii_poarta_titlul_cardului(asistent, patron):
    """292. Cardul „De validat” deschidea fereastra intitulată „Declarații de depus”, cu secțiunea „DE DEPUS” (rest din 266, clasa 127).
    Pașii: Ana (asistentă, „Poate valida”) -> cardul „De validat” -> titlul ferestrei e „De validat”, oricare ar fi conținutul (o
    declarație gata de depus pusă în coadă de administrator, cu validarea în doi oprită); la fel după o redesenare a ferestrei. Pe
    pagina cabinetului, fereastra poartă titlul cardului de acolo."""
    from e2e_bloc_c import _curata_coada, _declaratie_pas1, _trimite_si_asteapta
    tid = 4838
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    try:
        _declaratie_pas1(patron, "Comert Micro TVA", "d710", 2026, luna=9, trim=3)
        patron.pg.wait_for_selector("#d710-cod", timeout=60000)
        patron.pg.select_option("#d710-cod", "121")
        patron.pg.fill("#d710-i", "100")
        patron.pg.fill("#d710-c", "150")
        patron.pg.fill("#d710-cota", "1")
        patron.pg.click("#d710-add")
        patron.pg.click("#d710-regen")
        _trimite_si_asteapta(patron)
        asistent.acasa()
        pg = asistent.pg
        pg.click("button.cab-card:has([data-cheie='validat'])")
        pg.wait_for_selector(".fereastra:last-of-type #val-titlu", timeout=30000)
        assert pg.inner_text(".fereastra:last-of-type #val-titlu").strip() == "De validat"
        asistent.captura("asistent")
        pg.evaluate("() => window.dispatchEvent(new Event('iconta:drepturi'))")   # redesenarea la drepturi păstrează titlul
        pg.wait_for_timeout(1500)
        assert pg.inner_text(".fereastra:last-of-type #val-titlu").strip() == "De validat"
        patron.acasa()
        card = patron.pg.inner_text("button.cab-card:has([data-cheie='validat']) .cab-card-titlu").strip()
        patron.pg.click("button.cab-card:has([data-cheie='validat'])")
        patron.pg.wait_for_selector(".fereastra:last-of-type #val-titlu", timeout=30000)
        assert patron.pg.inner_text(".fereastra:last-of-type #val-titlu").strip() == card, card
    finally:
        _curata_coada(tid, peste)


def test_def_293_pe_declaratia_altcuiva_fara_depunere_numai_vizualizare(asistent, patron):
    """293. Ana (asistentă cu „Poate valida”, fără „Poate depune”) vedea „Renunță” pe D300 pregătită de administrator.
    Pașii: administratorul pune o declarație în coadă (validarea în doi oprită) -> Ana deschide „De validat”: pe rândul declarației nu e
    „Renunță” (nicio acțiune, numai „Vezi declarația…”); cererea de renunțare trimisă direct e refuzată (403)."""
    from e2e_bloc_a import _api
    from e2e_bloc_c import _curata_coada, _declaratie_pas1, _trimite_si_asteapta
    tid = 4838
    uid = sql("SELECT id FROM public.users WHERE email = 'asistent@prisma-cont.test'")[0][0]
    era = sql("SELECT poate_valida, poate_depune FROM public.users WHERE id = %s", (uid,))[0]
    sql("UPDATE public.users SET poate_valida = true, poate_depune = false WHERE id = %s", (uid,))
    sql("INSERT INTO public.user_tenants (user_id, tenant_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (uid, tid))
    peste = sql("SELECT COALESCE(max(id), 0) FROM public.declaratii_coada")[0][0]
    try:
        _declaratie_pas1(patron, "Comert Micro TVA", "d710", 2026, luna=9, trim=3)
        patron.pg.wait_for_selector("#d710-cod", timeout=60000)
        patron.pg.select_option("#d710-cod", "121")
        patron.pg.fill("#d710-i", "100")
        patron.pg.fill("#d710-c", "150")
        patron.pg.fill("#d710-cota", "1")
        patron.pg.click("#d710-add")
        patron.pg.click("#d710-regen")
        _trimite_si_asteapta(patron)
        cid = sql("SELECT id FROM public.declaratii_coada WHERE tenant_id = %s AND id > %s AND fel <> 'nota' ORDER BY id DESC LIMIT 1",
                  (tid, peste))[0][0]
        asistent.acasa()
        pg = asistent.pg
        pg.click("button.cab-card:has([data-cheie='validat'])")
        rand = ".fereastra:last-of-type .val-rand:has(.val-vezi)"
        pg.wait_for_selector(".fereastra:last-of-type .val-titlu:has-text('D710')", timeout=30000)
        asistent.captura("coada_ana")
        actiuni = pg.eval_on_selector_all(".fereastra:last-of-type .val-titlu:has-text('D710')",
                                          "(ts) => ts.map((t) => t.closest('.val-info').parentElement.querySelector('.val-actiuni').innerText)")
        assert actiuni and all("Renunță" not in a for a in actiuni), actiuni
        r = _api(asistent, "POST", "/coada/%d/respinge" % cid, {"motiv": "proba 293"})
        assert r["status"] == 403 and "Tu o poți vedea" in str(r["json"]), r
    finally:
        _curata_coada(tid, peste)
        sql("UPDATE public.users SET poate_valida = %s, poate_depune = %s WHERE id = %s", (era[0], era[1], uid))


def test_def_294_perioada_implicita_e_cea_scadenta_si_nedepusa(patron):
    """294. La D100, trimestrul propus implicit era T4 (în curs, termen 25.01.2027) în loc de T3 (scadent pe 25.10.2026); legat de 283.
    Pașii: „Comert Micro TVA” -> Declarații -> D100 (oricare din grupe): perioada propusă e cea scadentă și nedepusă din vectorul fiscal
    (sau, fără ea, trimestrul încheiat), nu trimestrul în curs; o declarație anuală din „Alte declarații” propune anul încheiat."""
    from e2e_bloc_c import _deschide
    pg = patron.pg
    _deschide(patron, "Comert Micro TVA", "declaratii", "#dec-tip")
    t_curent = (AZI.month - 1) // 3 + 1
    datorata = pg.eval_on_selector_all("#dec-tip option[value='d100'][data-an]", "(os) => os.map((o) => [o.dataset.an, o.dataset.luna])")
    asteptat = (int(datorata[0][0]), (int(datorata[0][1]) - 1) // 3 + 1) if datorata else \
        ((AZI.year, t_curent - 1) if t_curent > 1 else (AZI.year - 1, 4))
    # [301, 17.10.2026] „Alte declarații” e pliată: se deschide ca omul, apoi se caută acolo D100 (opțiunea fără perioadă datorată)
    if pg.locator("#dec-alte").count() and pg.get_attribute("#dec-alte", "aria-expanded") != "true":
        pg.click("#dec-alte")
    alte = pg.eval_on_selector_all("#dec-tip option[value='d100']:not([data-an])", "(os) => os.length")
    if alte:   # D100 și în „Alte declarații” (nu e datorată): alegerea de acolo propune tot perioada scadentă
        pg.select_option("#dec-tip", index=pg.eval_on_selector("#dec-tip", "(s) => [...s.options].findIndex((o) => o.value === 'd100' && !o.dataset.an)"))
    else:
        alege_tipul(pg, "d100")
    pg.wait_for_selector("#dec-trim", timeout=10000)
    patron.captura("d100")
    assert (int(pg.input_value("#dec-an")), int(pg.input_value("#dec-trim"))) == asteptat, (pg.input_value("#dec-an"), pg.input_value("#dec-trim"))
    # trimestrul în curs = al zilei în care aplicația a propus perioada (ACUM: importul testului sau, după miezul nopții, azi)
    curente = {(z.year, (z.month - 1) // 3 + 1) for z in zile_de_acum(AZI)}
    assert (int(pg.input_value("#dec-an")), int(pg.input_value("#dec-trim"))) not in curente, "nu trimestrul în curs"
    anuale = pg.eval_on_selector_all("#dec-tip optgroup:last-of-type option", "(os) => os.map((o) => o.value)")
    for tip in ("d205", "d101", "d100"):
        if tip in anuale and tip != "d100":
            pg.select_option("#dec-tip", index=pg.eval_on_selector("#dec-tip", "(s, t) => [...s.options].findIndex((o) => o.value === t && !o.dataset.an)", tip))
            pg.wait_for_selector("#dec-an", timeout=10000)
            if not pg.locator("#dec-trim, #dec-luna").count():
                assert int(pg.input_value("#dec-an")) in {z.year - 1 for z in zile_de_acum(AZI)}, (tip, pg.input_value("#dec-an"))
                break


def test_def_295_d100_pasul_2_are_rezumatul_cu_baza(patron):
    """295. D100 pasul 2 arăta doar obligația (cod 121, 10 lei, cota 1), fără baza de calcul.
    Pașii: „Comert Micro TVA” -> Declarații -> D100, T3/2026 -> Continuă: caseta „Rezumat” arată baza (veniturile trimestrului pe
    conturi, deducerile) și calculul impozitului, ca la D112."""
    from e2e_bloc_c import _declaratie_pas1
    pg = patron.pg
    _declaratie_pas1(patron, "Comert Micro TVA", "d100", 2026, trim=3)
    pg.wait_for_selector("#dec-trimite, #dec-gol-da, .dec-eroare", timeout=90000)
    patron.captura("pas2")
    t = patron.fereastra()
    assert "Rezumat" in t and "Baza de calcul T3/2026" in t, t[:2000]
    assert "Deduceri din bază:" in t and "Baza impozabilă:" in t and "cod 121:" in t, t[:2000]


def test_def_274_articolul_fara_cota_in_nomenclator_spune_si_trimite_la_produse(patron, firma_e2e):
    """274a. Emite factură: pentru un articol din stoc („Marfa A”) cota TVA rămânea „—” și nu se propunea nimic.
    Pașii: un articol cu stoc care nu e în nomenclatorul de produse -> Emite factură -> linia: alege articolul -> cota „—”, iar sub
    linie mesajul „Articolul „…” n-are cota TVA în nomenclator…” cu „Deschide Produse”; butonul deschide Produse peste factură."""
    from e2e_bloc_a import _api, _deschide_emiterea, _ok
    pregateste_firma(patron, firma_e2e)
    tid = firma_e2e["tenant_id"]
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % tid, {"denumire": "Marfa A 274", "um": "buc", "data": AZI.isoformat(),
                                                                   "cantitate": 5, "pret_unitar": 10, "document": "NIR 274"}), "intrare")
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    pg.wait_for_selector("#em-l0-articol", timeout=20000)
    pg.select_option("#em-l0-articol", label=pg.eval_on_selector("#em-l0-articol",
                     "(s) => [...s.options].find((o) => o.textContent.startsWith('Marfa A 274')).textContent"))
    pg.wait_for_selector("#em-l0-cota-mesaj .caseta-atentie", timeout=15000)
    patron.captura("fara_cota")
    t = pg.inner_text("#em-l0-cota-mesaj")
    assert "Articolul „Marfa A 274” n-are cota TVA în nomenclator" in t and "Deschide Produse" in t, t
    assert pg.input_value("#em-l0-cota") == ""
    pg.click("#em-l0-cota-mesaj [data-ecran-destinatie='produse']")
    pg.wait_for_function("() => [...document.querySelectorAll('.fereastra')].pop().innerText.includes('Produse')", timeout=15000)


def test_def_274_linia_cu_0_cere_categoria_de_tva(patron, firma_e2e):
    """274b (decizia Costin 16.10.2026): „Categoria e obligatorie pe orice linie cu 0%” — taxare inversă, scutit cu / fără drept de
    deducere, livrare intracomunitară, export, în afara sferei; „O” automat la neplătitor.
    Pașii: Emite factură -> linia cu cota 0% -> sub ea apare „categoria de TVA”; emisă fără categorie -> refuzul stă la câmpul ei;
    „taxare inversă” -> se cere și categoria produsului (art.331); „scutit fără drept de deducere” -> factura se emite, cu categoria pe
    linie (D300 rd.15)."""
    from e2e_bloc_a import _deschide_emiterea, _completeaza_factura
    pregateste_firma(patron, firma_e2e)
    _deschide_emiterea(patron, firma_e2e["nume"])
    pg = patron.pg
    _completeaza_factura(pg)
    pg.wait_for_function("() => document.querySelector('#em-l0-cota').value !== ''", timeout=20000)
    assert pg.locator("#em-l0-categorie").is_hidden(), "pe o linie cu cotă pozitivă nu se cere categoria"
    pg.select_option("#em-l0-cota", "0")
    pg.wait_for_selector("#em-l0-categorie", state="visible", timeout=10000)
    optiuni = pg.eval_on_selector_all("#em-l0-categorie option", "els => els.map(e => e.value).filter(Boolean)")
    assert optiuni == ["taxare_inversa", "scutit_cu_drept", "scutit_fara_drept", "livrare_ic", "serviciu_extern", "export",
                       "in_afara_sferei"], optiuni   # [17.10.2026] + prestarea de servicii cu locul în afara României (art.278 alin.(2))
    pg.click("#em-emite")
    pg.wait_for_function("() => [...document.querySelectorAll('.em-linie .msg-eroare')].some((m) => m.innerText.includes('alege categoria'))",
                         timeout=20000)
    patron.captura("fara_categorie")
    pg.select_option("#em-l0-categorie", "taxare_inversa")
    pg.wait_for_selector("#em-c331", state="visible", timeout=10000)
    patron.captura("taxare_inversa_cere_categoria_produsului")
    pg.select_option("#em-l0-categorie", "scutit_fara_drept")
    assert pg.locator("#em-c331").is_hidden()
    with pg.expect_response(lambda r: r.url.endswith("/facturi/emite"), timeout=60000) as rr:
        pg.click("#em-emite")
    assert rr.value.status == 200, rr.value.text()[:300]
    fid = rr.value.json()["factura_id"]
    pg.wait_for_selector("#em-rezultat.em-bun", timeout=20000)
    patron.captura("emisa")
    assert sql('SELECT cota_tva::int, categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % firma_e2e["schema"], (fid,)) == \
        [(0, "scutit_fara_drept")]


def test_def_288_povestea_se_verifica_la_aprobare_si_spune_perioada(patron, firma_e2e):
    """288. Povestea lunii: (a) „încasări” în loc de „venituri” trecea la aprobare; (b) nu spunea dacă cifrele sunt ale lunii sau cumulate;
    (c) pomenea restanțele cabinetului fără decizia contabilului.
    Pașii: Pachet lunar -> firma, luna curentă: „Cifrele lunii — luna … (numai luna, nu cumulat de la 1 ianuarie)”; povestea cu
    „încasări” -> „Aprobă”: refuz numit (termen: încasări); povestea care pomenește declarațiile nedepuse -> „Aprobă”: refuz cu pasul de
    decizie -> „Aprob cu restanțele (decizia mea)” -> aprobată."""
    from e2e_bloc_a import _pachet, _deschide_povestea
    from core.pachete_api import LUNI
    luna = LUNI[AZI.month]
    pregateste_firma(patron, firma_e2e)
    _pachet(patron, firma_e2e, AZI.year, AZI.month)
    pg = patron.pg
    per = pg.inner_text("#pac-perioada")
    assert "numai luna, nu cumulat de la 1 ianuarie" in per and luna in per, per
    _deschide_povestea(patron)
    pg.fill("#pacm-text", "În %s firma a avut încasări mici." % luna)
    pg.click("#pacm-aproba")
    pg.wait_for_function("() => document.querySelector('#pacm-stare').innerText.includes('Povestea nu se aprobă')", timeout=15000)
    assert "termen: încasări" in pg.inner_text("#pacm-stare")
    patron.captura("refuz_termeni")
    pg.fill("#pacm-text", "În %s firma n-a avut operațiuni. Firma are declarații nedepuse, cu termenele depășite." % luna)
    pg.click("#pacm-aproba")
    pg.wait_for_selector("#ca-ok", timeout=15000)
    patron.captura("decizie_restante")
    assert "Aprob cu restanțele (decizia mea)" in pg.inner_text("#ca-ok")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pacm-stare').innerText.includes('Aprobată')", timeout=15000)
