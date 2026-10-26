# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”) — portalul clientului (fork P1 al subagentului PORTAL):

  553  Cifrele firmei: „Profit −6.075 lei” la rezultat negativ; previziunea fără explicație a săptămânii; media cheltuielilor greșită.
  554  Clientul vede ce are de plătit și până când, în cuvintele lui — nu codurile declarațiilor („d300”, „d394”).
  555  „Declarații depuse” fără perioadă, dată, recipisă; cardul Documente promitea „Recipise, balanțe, bilanț”; „Previzualizează
       portalul” inactiv fără să spună de ce.
  556  Balanța lunii deschise arăta definitivă.
  557  PDF-ul balanței pentru client avea paragraful tehnic pentru contabil.
  558  Povestea aprobată cu termeni greșiți („încasări”) ajungea la client; prima lună se compara cu o lună care nu există în iConta.eu.
  559  „De încasat” (balanța) diferea de Scadențar (facturi cu note nevalidate).
  560  Linkul „Intră în portal” din invitație ducea la formularul de autentificare; linkul de activare deja folosit spunea „invalid sau
       expirat”; emailul asistentului spunea „în cabinetul tău”.

Pașii contabilului și ai clientului pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua` + `pregateste_firma`).
DATELE DE PORNIRE scrise pe drumul aplicației (declarate): facturile prin ruta formularului de emitere (`_emite`), notele prin funcția
Registrului jurnal (`_nota`), contul clientului prin ruta „Acces client” (`client-acces`). Scrise direct în bază, pentru că aplicația nu
are drum pentru ele (declarate, curățate la final): închiderea unei luni (`perioade_blocate`, 556), soldul de preluare (`solduri_initiale`,
557), o depunere (`declaratii_depuse`, 555, perioadă sintetică 2099) și o poveste aprobată înainte de reparația 288 (`pachet_povestea`,
558, perioadă sintetică 2099). Clientul DANTE INTERNATIONAL SA, CUI 14399840 — cifra de control verificată cu algoritmul din CLAUDE.md.

Temei: 553 — OMFP 1802/2014 grupa 69 („Cheltuieli cu impozitul pe profit și alte impozite”): rezultatul „înainte de impozit” nu le
cuprinde; 554 — CF art.326 alin.(1) („Orice persoană trebuie să achite taxa de plată organelor fiscale până la data la care are obligația
depunerii unuia dintre deconturile [...]”), citat cu celelalte în `core/uc_portal.PLATI_DIN_DECLARATII`; 555–560 — N/A, reguli de produs
(comanda 13.1; decizia din 05.10.2026: restanțele declarațiilor rămân la cabinet).
"""
import contextlib
import datetime as _dt
import io
import re
import time
from decimal import Decimal

import pytest

from conftest import BAZA, GARDA_DESCHIDERI, Ecran, _ecran, firma_noua, sql
from e2e_bloc_a import _api, _ok, pregateste_firma
from e2e_bloc_e import _nota
from e2e_inregistrare_libera import _scrisori
from e2e_lot12_cx1 import _emite
from e2e_lot12_start import _scoate_contul

ecran_cont = contextlib.contextmanager(_ecran)
AZI = _dt.date.today()
LUNA_TRECUTA = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=1)


@pytest.fixture(scope="module")
def firma_553():
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_554():
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_doc():
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_558():
    """[558] O firmă NOUĂ, fără nicio notă: luna preluării aleasă (09/2099) e luna efectivă numai fără o notă mai veche — altfel se
    socotește luna primei note (`luna_preluare.efectiva`, „niciodată după luna primei note”), iar 08/2099 ar fi o lună din evidență
    (goală), cu comparația corectă. Pe `firma_doc`, notele probelor anterioare (2026) mutau începutul evidenței în 2026."""
    for f in firma_noua():
        yield f


@pytest.fixture(scope="module")
def firma_559():
    for f in firma_noua():
        yield f


def _email(nr):
    return "e2e.l13.p1.%s.%d@exemplu.ro" % (nr, int(time.time() * 1000) % 100000000)


def _client(patron, firma, nr):
    """Contul de client al firmei, pe ruta „Acces client” (`POST /tenants/{id}/client-acces`), trecut de „Bun venit” (ca C113: fereastra de
    primire, deschisă de aplicație la prima intrare, ar acoperi cardurile — proba e portalul, nu primirea)."""
    email = _email(nr)
    _scoate_contul(email)
    _ok(_api(patron, "POST", "/tenants/%d/client-acces" % firma["tenant_id"], {"email": email, "nume": "Client Probă %s" % nr}), "acces client")
    sql("UPDATE public.users SET bun_venit_vazut_la = now() WHERE email = %s", (email,))
    return email


def _card(cp, titlu):
    card = cp.locator("button.cab-card", has_text=titlu).first
    card.wait_for(timeout=30000)
    card.click()


def _valideaza_nota_facturii(patron, firma, fid):
    ((nid,),) = sql('SELECT id FROM "%s".inregistrari WHERE factura_id = %%s AND sursa = \'facturi\'' % firma["schema"], (fid,))
    _ok(_api(patron, "POST", "/tenants/%d/jurnal/%d/valideaza" % (firma["tenant_id"], nid), {}), "validarea notei facturii")


def _bani(text):
    return [Decimal(m.replace(".", "").replace(",", ".")) for m in re.findall(r"(\d{1,3}(?:\.\d{3})*(?:,\d+)?) lei", text)]


# ── 553 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_553_cifrele_spun_pierderea_si_previziunea_isi_explica_saptamana(patron, firma_553, browser, request):
    """553. Pașii: contabilul emite o factură de 100 lei + TVA și îi validează nota (venituri 100), scrie și validează nota salariilor
    641 = 421 de 500 lei (cheltuieli 500) -> clientul: „Cifrele firmei”: rândul rezultatului spune „Pierdere înainte de impozit” și 400 lei,
    fără minus (înainte: „Profit −400 lei”); previziunea: rândul săptămânii întâi își spune componentele („Plăți: salarii nete 500”), iar
    media cheltuielilor e 500 lei, „media pe luna …”, cu salariile (înainte: fără 641, împărțit la luna calendaristică).
    MUTAȚIA: eticheta rezultatului scrisă mereu „Profit” -> ROȘU."""
    f = firma_553
    pregateste_firma(patron, f)
    fac = _emite(patron, f, 100, descriere="Servicii E2E 553")
    _valideaza_nota_facturii(patron, f, fac["factura_id"])
    _nota(f, AZI.isoformat(), [{"debit": "641", "credit": "421", "suma": "500.00"}], descriere="Salarii E2E 553", valideaza=True)
    email = _client(patron, f, "553")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Cifrele firmei")
            cp.wait_for_selector("#cf-rezultat", timeout=30000)
            cp.wait_for_selector("#cf-zona .pf-frand", timeout=30000)
            rez = " ".join(cp.inner_text("#cf-rezultat").split())
            assert "Pierdere înainte de impozit" in rez, rez
            assert _bani(rez) == [Decimal("400")] and "−" not in rez and "-400" not in rez, rez
            intro = cp.inner_text("#cf-intro")
            assert "inclusiv salariile" in intro and "~500 lei" in intro and "media pe luna" in intro, intro
            prima = " ".join(cp.locator("#cf-zona .pf-frand").first.inner_text().split())
            assert "Plăți: salarii nete 500" in prima, prima
            c.captura("cifre_pierdere_si_previziune")
    finally:
        _scoate_contul(email)


# ── 554 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_554_clientul_vede_ce_are_de_platit_fara_codurile_declaratiilor(patron, firma_554, browser, request):
    """554. Pașii: firma plătitoare de TVA lunar, cu evidența din luna trecută și TVA de plată 300 lei la sfârșitul ei (nota 4427 = 4423
    validată) -> clientul, pagina principală: panoul „De plătit la stat” (sau „Nimic de plătit…”), fără niciun cod de declarație („d300”,
    „d394”, „D406”). Cât termenul TVA pe luna trecută nu a trecut, rândul „TVA de plată · LL/AAAA · 300,00 lei · până pe …” (din balanță).
    MUTAȚIA: titlul panoului înapoi pe „termene” -> ROȘU."""
    f = firma_554
    pregateste_firma(patron, f)
    _nota(f, LUNA_TRECUTA.replace(day=15).isoformat(), [{"debit": "4427", "credit": "4423", "suma": "300.00"}],
          descriere="Regularizare TVA E2E 554", valideaza=True)
    # date-de-pornire: evidența firmei din luna trecută (luna preluării, Date firmă) — altfel obligațiile ei sunt „înainte de preluare”
    sql('UPDATE "%s".firma_profil SET luna_preluare = %%s WHERE id = 1' % f["schema"], (LUNA_TRECUTA,))
    email = _client(patron, f, "554")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            with cp.expect_response(lambda r: "/portal/acasa" in r.url, timeout=60000) as rr:
                cp.goto(BAZA + "/", wait_until="domcontentloaded")
            plati = rr.value.json()["de_platit"]
            cp.wait_for_selector("#pa-status .pa-titlu", timeout=60000)
            panou = " ".join(cp.inner_text("#pa-status").split())
            assert cp.inner_text("#pa-status .pa-titlu").strip() in ("De plătit la stat", "Nimic de plătit la stat în perioada următoare"), panou
            assert not re.search(r"(?i)\bd\s?\d{3}\b", panou), panou            # decizia 05.10: declarațiile rămân la cabinet
            for x in plati:
                assert x["ce"] in panou and "până pe" in panou, (x, panou)
            tva = [x for x in plati if x["ce"] == "TVA de plată"]
            if tva:   # termenul D300 pe luna trecută (25, mutat pe zi lucrătoare) încă neîmplinit
                assert Decimal(tva[0]["suma"]) == Decimal("300") and "300,00 lei" in panou, (tva, panou)
            c.captura("de_platit")
    finally:
        _scoate_contul(email)


# ── 555 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_555_declaratia_depusa_are_perioada_data_si_recipisa(patron, firma_doc, browser, request):
    """555. Pașii: o D406 depusă pe 01/2099 (02.03.2099, recipisa E2E-555) -> clientul: „Declarații depuse”: rândul „D406 · 01/2099”, cu
    denumirea formularului, „depusă pe 02.03.2099” și „recipisa E2E-555” (înainte: „d406 · ” și „depusă ” gol); cardul „Documente” spune
    „Balanțele lunare, în PDF” și deschide direct balanțele (nu și a doua oară declarațiile).
    MUTAȚIA: recipisa scoasă din rândul declarației -> ROȘU."""
    f = firma_doc
    pregateste_firma(patron, f)
    # date-de-pornire: depunerea (aplicația o scrie numai la depunerea prin SPV), perioadă sintetică 2099 — tabel partajat
    sql("INSERT INTO public.declaratii_depuse (tenant_id, an, luna, tip, data_depunere, sursa, recipisa) VALUES (%s, 2099, 1, 'd406', "
        "'2099-03-02 10:00+02', 'extern', 'E2E-555')", (f["tenant_id"],))
    email = _client(patron, f, "555")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            doc = " ".join(cp.locator("button.cab-card", has_text="Documente").first.inner_text().split())
            assert "Balanțele lunare, în PDF" in doc and "Recipise" not in doc and "bilanț" not in doc, doc
            _card(cp, "Declarații depuse")
            cp.wait_for_selector(".fereastra .pf-frand", timeout=30000)
            rand = " ".join(cp.locator(".fereastra .pf-frand", has_text="D406").first.inner_text().split())
            assert "D406 · 01/2099" in rand and "depusă pe 02.03.2099" in rand and "recipisa E2E-555" in rand, rand
            assert "Fișierul Standard de Control Fiscal" in rand, rand
            c.captura("declaratie_depusa")
    finally:
        _scoate_contul(email)
        sql("DELETE FROM public.declaratii_depuse WHERE tenant_id = %s AND an = 2099", (f["tenant_id"],))


def test_def_555_previzualizarea_inactiva_isi_spune_motivul(patron, firma_559):
    """555 (515). Pașii: contabilul -> firma fără cont de client -> „Acces client”: „Previzualizează portalul” e inactiv, iar lângă el scrie
    de ce („Previzualizarea cere un cont de client: invită unul cu «Invită client nou».”) — înainte numai în `title`, pe care Chromium nu-l
    arată pe un buton dezactivat. MUTAȚIA: motivul înapoi în `title` -> ROȘU."""
    f = firma_559
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-acces")
    pg.wait_for_selector(".fereastra:last-of-type #ac-btn-preview:disabled", timeout=20000)
    motiv = pg.locator(".fereastra:last-of-type #ac-btn-preview + .motiv-generat")
    assert motiv.count() == 1 and motiv.is_visible(), "motivul nu stă lângă buton"
    assert "Previzualizarea cere un cont de client" in motiv.inner_text(), motiv.inner_text()
    assert pg.get_attribute(".fereastra:last-of-type #ac-btn-preview", "aria-describedby") == motiv.get_attribute("id")
    patron.captura("previzualizare_inactiva_cu_motiv")


# ── 556 + 557 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_556_luna_deschisa_e_provizorie_iar_cea_inchisa_definitiva(patron, firma_doc, browser, request):
    """556. Pașii: o notă validată în luna trecută, apoi luna trecută închisă de contabil; o notă ciornă în luna curentă -> clientul:
    „Documente”: luna curentă „provizorie — contabilul încă lucrează la ea (1 înregistrare neverificată)”, luna trecută „definitivă — luna
    e închisă de contabil” (înainte: orice lună, fără stare). MUTAȚIA: orice lună socotită definitivă -> ROȘU."""
    f, s = firma_doc, firma_doc["schema"]
    pregateste_firma(patron, f)
    vechi = _nota(f, LUNA_TRECUTA.replace(day=10).isoformat(), [{"debit": "5311", "credit": "1012", "suma": "100.00"}], valideaza=True)
    noua = _nota(f, AZI.isoformat(), [{"debit": "5311", "credit": "1012", "suma": "50.00"}])
    # date-de-pornire: închiderea lunii trecute (blocarea perioadei, ca din „Închide luna”) — după nota ei
    sql('INSERT INTO "%s".perioade_blocate (an, luna) VALUES (%%s, %%s)' % s, (LUNA_TRECUTA.year, LUNA_TRECUTA.month))
    email = _client(patron, f, "556")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Documente")
            cp.wait_for_selector(".fereastra .pf-frand[data-luna]", timeout=30000)
            curenta = cp.locator('.fereastra .pf-frand[data-luna="%s"]' % AZI.strftime("%Y-%m"))
            trecuta = cp.locator('.fereastra .pf-frand[data-luna="%s"]' % LUNA_TRECUTA.strftime("%Y-%m"))
            assert curenta.get_attribute("data-definitiva") == "nu" and trecuta.get_attribute("data-definitiva") == "da"
            tc = " ".join(curenta.inner_text().split())
            assert "provizorie — contabilul încă lucrează la ea (1 înregistrare neverificată)" in tc, tc
            assert "definitivă — luna e închisă de contabil" in " ".join(trecuta.inner_text().split())
            c.captura("balante_provizorie_si_definitiva")
    finally:
        _scoate_contul(email)
        sql('DELETE FROM "%s".perioade_blocate WHERE an = %%s AND luna = %%s' % s, (LUNA_TRECUTA.year, LUNA_TRECUTA.month))
        from e2e_bloc_e import _sterge_note
        _sterge_note(f, [noua, vechi])


def test_def_557_pdf_balantei_clientului_fara_paragraful_pentru_contabil(patron, firma_doc, browser, request):
    """557. Pașii: firma cu soldurile de preluare la sfârșitul lunii trecute (fără rulajele anului) și o notă ciornă în luna curentă ->
    clientul: „Documente” -> balanța lunii curente -> „Descarcă PDF”: sub antet „Provizorie: luna … nu e încă închisă de contabil…” și
    „Evidența în iConta.eu începe cu <luna> <an>.”, fără paragraful pentru contabil („Rulajele de la … lipsesc …”, „Import date › Solduri
    inițiale”, „ciorne nevalidate”). MUTAȚIA: PDF-ul clientului fără notele lui (cel al contabilului) -> ROȘU."""
    if AZI.month == 1:
        pytest.skip("în ianuarie soldurile de preluare la 31.12 sunt ale anului trecut: balanța anului curent nu are ce avertiza")
    f, s = firma_doc, firma_doc["schema"]
    pregateste_firma(patron, f)
    ref = AZI.replace(day=1) - _dt.timedelta(days=1)
    # date-de-pornire: balanța de deschidere fără rulaje (ca o preluare doar cu solduri finale), la sfârșitul lunii trecute
    sql('INSERT INTO "%s".solduri_initiale (cont, denumire, sold_debitor, sold_creditor, data_referinta) VALUES '
        "('5311', 'Casa în lei', 100, 0, %%s), ('1012', 'Capital subscris vărsat', 0, 100, %%s)" % s, (ref, ref))
    noua = _nota(f, AZI.isoformat(), [{"debit": "5311", "credit": "1012", "suma": "50.00"}])
    email = _client(patron, f, "557")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Documente")
            buton = '.fereastra .pf-frand[data-luna="%s"] [data-bal]' % AZI.strftime("%Y-%m")
            cp.wait_for_selector(buton, timeout=30000)
            with cp.expect_download(timeout=60000) as dl:
                cp.click(buton)
            from pypdf import PdfReader
            text = " ".join(PdfReader(io.BytesIO(open(dl.value.path(), "rb").read())).pages[0].extract_text().split())
            c.captura("pdf_balanta_client")
        assert "Provizorie: luna %02d/%d nu e încă închisă de contabil" % (AZI.month, AZI.year) in text, text[:600]
        assert "Evidența în iConta.eu începe cu" in text, text[:600]
        for tehnic in ("Import date", "Rulajele de la", "ciorne nevalidate", "Cuprinde numai notele validate"):
            assert tehnic not in text, (tehnic, text[:600])
    finally:
        _scoate_contul(email)
        sql('DELETE FROM "%s".solduri_initiale WHERE data_referinta = %%s' % s, (ref,))
        from e2e_bloc_e import _sterge_note
        _sterge_note(f, [noua])


# ── 558 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_558_povestea_cu_termeni_gresiti_e_retrasa_si_prima_luna_fara_comparatie(patron, firma_558, browser, request):
    """558. Pașii: evidența firmei începe cu 09/2099 (luna preluării); povestea lunii 09/2099, aprobată înainte de reparația 288 („încasări de
    1.000 de lei”) -> clientul: „Povestea lunii”: rândul spune „Textul acestei luni a fost retras: folosea alți termeni decât cifrele lunii.
    Contabilul îl reface.”, cu cifrele lunii, fără „încasări”; și fără „față de luna anterioară” (08/2099 nu există în iConta.eu).
    MUTAȚIILE: povestea niciodată retrasă -> ROȘU; comparația și la prima lună -> ROȘU."""
    f, s = firma_558, firma_558["schema"]
    assert sql('SELECT count(*) FROM "%s".inregistrari' % s) == [(0,)]   # calibrarea: nicio notă, deci evidența începe cu luna aleasă
    # date-de-pornire: luna preluării (Date firmă) și povestea aprobată înainte de 288 (fără amprenta cifrelor), perioadă sintetică 2099
    sql('UPDATE "%s".firma_profil SET luna_preluare = %%s WHERE id = 1' % s, (_dt.date(2099, 9, 1),))
    # date-de-pornire: povestea lunii aprobată înainte de reparația 288, scrisă cum o scria codul de atunci (documentul vechi)
    sql("INSERT INTO public.pachet_povestea (tenant_id, an, luna, text, status, updated_at) VALUES (%s, 2099, 9, "
        "'În septembrie firma a avut încasări de 1.000 de lei.', 'aprobat', now())", (f["tenant_id"],))
    email = _client(patron, f, "558")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Povestea lunii")
            cp.wait_for_selector("#pov-lista .pf-frand", timeout=30000)
            rand = " ".join(cp.locator("#pov-lista .pf-frand").first.inner_text().split())
            assert "Textul acestei luni a fost retras: folosea alți termeni decât cifrele lunii. Contabilul îl reface." in rand, rand
            assert "încasări" not in rand, rand
            assert "față de luna anterioară" not in rand, rand
            c.captura("poveste_retrasa_fara_comparatie")
    finally:
        _scoate_contul(email)
        sql("DELETE FROM public.pachet_povestea WHERE tenant_id = %s AND an = 2099", (f["tenant_id"],))
        # date-de-pornire: curățenie după probă — luna preluării a firmei de probă înapoi la nealeasă (nu e o dată a probei)
        sql('UPDATE "%s".firma_profil SET luna_preluare = NULL WHERE id = 1' % s)


# ── 559 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_559_de_incasat_si_scadentarul_au_aceeasi_baza(patron, firma_559, browser, request):
    """559 (grav). Pașii: contabilul emite factura A (100 lei + TVA = 121,00) și îi validează nota, apoi factura B (200 lei + TVA = 242,00)
    rămasă cu nota ciornă -> clientul: „Cifrele firmei”: „De încasat de la clienți” 121,00 lei, „1 factură deschisă, aceleași ca în
    Scadențar”; „Facturi” -> „Scadențar”: factura A, nu și B (înainte: Scadențarul număra și facturile cu nota nevalidată).
    MUTAȚIA: condiția „nota validată” scoasă -> B intră -> ROȘU."""
    f = firma_559
    pregateste_firma(patron, f)
    a = _emite(patron, f, 100, descriere="Servicii E2E 559 A")["factura_id"]
    _valideaza_nota_facturii(patron, f, a)
    b = _emite(patron, f, 200, descriere="Servicii E2E 559 B")["factura_id"]
    email = _client(patron, f, "559")
    try:
        with ecran_cont(browser, request, email) as c:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Cifrele firmei")
            cp.wait_for_selector("#cf-de-incasat", timeout=30000)
            r = " ".join(cp.inner_text("#cf-de-incasat").split())
            assert "121,00 lei" in r and "242" not in r and "363" not in r, r
            assert "1 factură deschisă, aceleași ca în Scadențar" in r, r
            c.captura("de_incasat")
            cp.keyboard.press("Escape")
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            _card(cp, "Facturi")
            cp.wait_for_selector("#fac-scadentar", timeout=30000)
            with cp.expect_response(lambda x: "/scadentar" in x.url, timeout=30000) as rr:
                cp.click("#fac-scadentar")
            cp.wait_for_selector(".sc-fact-btn, .stare-goala", timeout=30000)
            ids = {x["id"] for x in rr.value.json()["linii"]}
            assert a in ids and b not in ids, ids
            assert cp.locator('.sc-fact-btn[data-id="%s"]' % a).count() == 1 and cp.locator('.sc-fact-btn[data-id="%s"]' % b).count() == 0
            c.captura("scadentar")
    finally:
        _scoate_contul(email)


# ── 560 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_560_linkul_invitatiei_intra_in_cont_si_in_fila_deja_deschisa(patron, firma_559, browser, request):
    """560 (grav). Pașii: contabilul -> firma -> „Acces client” -> „Invită client nou” -> „Trimite invitația” (o invitație NOUĂ) -> emailul
    n-are „Dezabonează-te” și nici antetul List-Unsubscribe; clientul are deja deschisă pagina iConta.eu (formularul de intrare) și deschide
    linkul „Intră în portal” în aceeași filă, o singură dată -> intră în cont („Înainte de a începe”, prima intrare a clientului), nu rămâne
    pe formularul de autentificare (înainte: aplicația citea `#magic=` numai la pornire; un link cu același început de adresă nu reîncarcă
    pagina). MUTAȚIA: ascultarea schimbării fragmentului scoasă -> rămâne pe pagina de intrare -> ROȘU."""
    f = firma_559
    email = _email("560")
    _scoate_contul(email)
    pg = patron.pg
    try:
        patron.firma(f["nume"])
        pg.click("#fa-acces")
        pg.wait_for_selector(".fereastra:last-of-type #ac-btn-invita", timeout=20000)
        pg.click(".fereastra:last-of-type #ac-btn-invita")
        pg.wait_for_selector("#ac-email", timeout=10000)
        pg.fill("#ac-email", email)
        pg.click("#ac-btn")
        pg.wait_for_function("(m) => document.body.innerText.includes(m)", arg=email, timeout=20000)
        (m,) = [x for x in _scrisori(email) if "portal" in x["subiect"].lower()][-1:]
        assert "Dezabonează" not in m["html"] and not any("unsubscribe" in k.lower() for k in (m.get("antete") or {})), m.get("antete")
        tok = re.search(r"#magic=([\w-]+)", m["html"]).group(1)
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        ctx.add_init_script(GARDA_DESCHIDERI)
        c = Ecran(ctx.new_page(), request.node.name + "_client")
        try:
            cp = c.pg
            cp.goto(BAZA + "/", wait_until="domcontentloaded")
            cp.wait_for_selector("#pagina-acces-btn", timeout=30000)        # fila e deschisă pe pagina de intrare
            cp.goto(BAZA + "/#magic=" + tok, wait_until="domcontentloaded")    # același document: numai fragmentul se schimbă
            cp.wait_for_selector("#prima-intrare", timeout=30000)              # a intrat în cont
            assert cp.locator("#pagina-acces-btn").count() == 0
            c.captura("intrat_din_fila_deschisa")
            assert sql("SELECT folosit FROM public.tokene_activare t JOIN public.users u ON u.id = t.user_id WHERE u.email = %s", (email,)) == [(True,)]
            assert not c.erori and not c.cereri_rele, (c.erori, c.cereri_rele)
        finally:
            ctx.close()
    finally:
        _scoate_contul(email)


def test_def_560_linkul_de_activare_folosit_spune_contul_e_deja_activat(patron, firma_559, browser, request):
    """560. Pașii: contabilul-șef invită un asistent (`POST /asistenti`, ruta ecranului Asistenți) -> emailul spune numele cabinetului
    („în cabinetul <b>…</b>”, nu „în cabinetul tău”) și n-are „Dezabonează-te” -> asistentul deschide linkul, își pune parola -> deschide
    din nou ACELAȘI link și încearcă iar: „Contul e deja activat — intră cu emailul și parola.” (înainte: „link de activare invalid sau
    expirat”). MUTAȚIA: mesajul înapoi pe „invalid sau expirat” -> ROȘU."""
    email = _email("560a")
    _scoate_contul(email)
    try:
        _ok(_api(patron, "POST", "/asistenti", {"email": email, "nume": "Asistent Probă 560", "firme": [firma_559["tenant_id"]]}), "asistent")
        (m,) = [x for x in _scrisori(email) if "asistent" in x["subiect"].lower()][-1:]
        ((cabinet,),) = sql("SELECT a.nume FROM public.accounting_firms a JOIN public.users u ON u.accounting_firm_id = a.id "
                            "WHERE u.email = 'patron@prisma-cont.test'")
        assert "în cabinetul tău" not in m["html"] and ("în cabinetul <b>%s</b>" % cabinet.strip()) in m["html"], m["html"][:300]
        assert "Dezabonează" not in m["html"]
        tok = re.search(r"#activare=([\w-]+)", m["html"]).group(1)
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        ctx.add_init_script(GARDA_DESCHIDERI)
        c = Ecran(ctx.new_page(), request.node.name + "_asistent")
        try:
            cp = c.pg
            for runda in (1, 2):
                cp.goto(BAZA + "/?r=%d#activare=%s" % (runda, tok), wait_until="domcontentloaded")
                cp.wait_for_selector("#act-p1", timeout=30000)
                cp.fill("#act-p1", "ParolaProba560!")
                cp.fill("#act-p2", "ParolaProba560!")
                if runda == 1:
                    with cp.expect_response(lambda r: "/public/activare" in r.url, timeout=30000) as rr:
                        cp.click("#act-btn")
                    assert rr.value.status == 200
                else:
                    cp.click("#act-btn")
                    cp.wait_for_function("() => (document.querySelector('#act-msg') || {}).innerText", timeout=30000)
            msg = cp.inner_text("#act-msg")
            assert "Contul e deja activat — intră cu emailul și parola." in msg, msg
            c.captura("activare_link_folosit")
        finally:
            ctx.close()
    finally:
        _scoate_contul(email)
