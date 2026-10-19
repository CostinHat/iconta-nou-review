# -*- coding: utf-8 -*-
"""Lotul 9, comanda 9.2 (Costin 19.10.2026, verbatim în DECIZII „Comanda 9.2”): deficiențele 398–417 — pașii contabilului pe aplicația
din index, pe baza de TEST, pe firme NOI de test (`firma_noua`). CUI-urile au cifra de control verificată (algoritmul din CLAUDE.md)."""
import pytest

from conftest import firma_noua, sql


@pytest.fixture(scope="module")
def firma_srl():
    for f in firma_noua():
        yield f


def _refuz(pg):
    """Lista „NU s-a salvat” de lângă buton: [(eticheta trimiterii, restul rândului)]."""
    return pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li",
                                   "lis => lis.map(li => [li.querySelector('button').textContent.trim(), "
                                   "li.textContent.slice(li.querySelector('button').textContent.length).trim()])")


# ── 410 — „NU s-a salvat” lângă buton, cu lista câmpurilor ───────────────────────────────────────────────
def test_def_410_date_firma_refuzul_se_vede_langa_salveaza_cu_campurile(patron, firma_srl):
    """410 (PRIORITAR). Date firmă: „Salvează” refuzat fără mesaj vizibil. Pașii: fereastra firmei -> Date firmă -> golește Telefon și
    Banca, scrie o adresă nouă -> Salvează: lângă buton „NU s-a salvat.” și câmpurile refuzate, fiecare cu trimitere; adresa scrisă
    rămâne; clic pe „Telefon” -> câmpul primește focus; completat -> iese din listă."""
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma_srl["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    pg.fill("#df-telefon", "")
    pg.fill("#df-banca", "")
    pg.fill("#df-adresa", "Str. Refuzului 410")
    pg.click("#df-salveaza")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura()
    box = pg.eval_on_selector(".refuz-salvare", "b => ({ text: b.querySelector('b').textContent, langa: b.previousElementSibling "
                                                "&& b.previousElementSibling.contains(document.querySelector('#df-salveaza')), "
                                                "vizibil: b.getBoundingClientRect().bottom <= innerHeight && b.getBoundingClientRect().top >= 0 })")
    assert box == {"text": "NU s-a salvat.", "langa": True, "vizibil": True}, box
    invalide = pg.eval_on_selector_all(".camp-invalid", "els => els.map(e => e.id)")
    lista = _refuz(pg)
    assert len(lista) == len(invalide) and {"df-telefon", "df-banca"} <= set(invalide), (lista, invalide)
    assert ["Telefon", "— Completează Telefon."] in lista and ["Banca", "— Completează Banca."] in lista, lista
    assert pg.input_value("#df-adresa") == "Str. Refuzului 410"   # ce s-a scris nu se pierde
    pg.locator(".refuz-salvare-lista button", has_text="Telefon").click()
    assert pg.evaluate("() => document.activeElement && document.activeElement.id") == "df-telefon"
    pg.fill("#df-telefon", "0722000410")
    pg.wait_for_function("() => ![...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('Telefon'))",
                         timeout=5000)
    assert ["Telefon", "— Completează Telefon."] not in _refuz(pg)


# ── 406 — casa nu ajunge sub zero ────────────────────────────────────────────────────────────────────
def test_def_406_plata_peste_soldul_casei_e_refuzata_la_salvare(patron, firma_srl):
    """406 (PRIORITAR). Casă: plată 200 cu sold 142 acceptată, registrul −58. Pașii: fereastra firmei -> Casă -> „+ Dispoziție nouă” ->
    ridicare de la bancă 142 lei -> Adaugă; apoi plată furnizor 200 lei: previzualizarea spune refuzul, „Adaugă” -> „NU s-a salvat.”
    lângă buton (motivul e mai jos), nimic scris, soldul final rămâne 142,00 lei."""
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma_srl["nume"])
    _card(patron, "casa", "#c-toggle")

    def _dispozitie(cat, suma, doc):
        if pg.is_hidden("#c-zona"):
            pg.click("#c-toggle")
        pg.select_option("#c-cat", cat)
        pg.fill("#c-suma", str(suma))
        pg.fill("#c-part", "DANTE INTERNATIONAL SA")
        pg.fill("#c-cui", "14399840")
        pg.fill("#c-doc", doc)
        pg.wait_for_timeout(600)   # previzualizarea (250 ms după tastare)
    _dispozitie("ridicare_banca", 142, "DI406")
    pg.click("#c-adauga")
    pg.wait_for_function("() => (document.querySelector('#c-sold-final') || {}).textContent === '142,00 lei'", timeout=20000)
    _dispozitie("plata_furnizor", 200, "DP406")
    pg.wait_for_selector("#c-previz-refuz.msg-eroare", timeout=10000)
    asteptat = ("Plată către furnizor de 200,00 lei nu încape în casă (contul 5311): soldul casei pe %s, în registru, e 142,00 lei, iar "
                "după ea casa ar ajunge la -58,00 lei pe %s. Numerarul din casă nu poate fi negativ. Înregistrează întâi încasarea sau "
                "ridicarea de numerar din care s-a plătit.")
    zi = pg.eval_on_selector("#c-data", "e => e.value.split('-').reverse().join('.')")
    assert pg.inner_text("#c-previz-refuz") == asteptat % (zi, zi)
    pg.click("#c-adauga")
    pg.wait_for_function("() => (document.querySelector('#c-mesaj') || {}).textContent", timeout=10000)
    patron.captura()
    assert pg.inner_text("#c-mesaj") == asteptat % (zi, zi)
    assert _refuz(pg) == [["motivul e mai jos", ""]], _refuz(pg)
    assert pg.inner_text("#c-sold-final") == "142,00 lei"


# ── firma la cost (cantitativ-valoric), plătitoare de TVA ────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_cv_noua():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma_cv(patron, firma_cv_noua):
    """Firma nouă, cu Date firmă, vectorul fiscal, seria și nomenclatorul (pregătirea e idempotentă: o valoare neschimbată nu scrie)."""
    from e2e_bloc_a import pregateste_firma
    pregateste_firma(patron, firma_cv_noua)
    return firma_cv_noua


def _lei(x):
    """Suma cum o scrie ecranul (`bani`): 1.234,56."""
    s = "{:,.2f}".format(float(x))
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _numerar(patron, f, suma=5000):
    from e2e_bloc_a import _api, _ok
    from e2e_bloc_e import _nota
    _nota(f, AZI.isoformat(), [{"debit": "5311", "credit": "581", "suma": suma}], "Ridicare numerar E2E 9.2", valideaza=True,
          document_ref="Cec 9.2")
    del _api, _ok


import datetime as _dt   # noqa: E402

AZI = _dt.date.today()


# ── 411 — netul de plată cu indemnizația CM ─────────────────────────────────────────────────────────────────────────────
def _salariat_cu_cm(firma):
    """Salariatul probelor 411–414 (salariul 4.050 lei, ocupația COR 241107, CM cod 01 pe 3 zile în luna curentă); o singură dată pe
    firmă, ca fiecare test să poată rula și singur (mutațiile rulează câte un test). Întoarce id-ul."""
    s = firma["schema"]
    gasit = sql('SELECT id FROM "%s".salariati WHERE cnp = %%s' % s, ("1900101410011",))
    if gasit:
        return gasit[0][0]
    sid = sql('WITH s AS (INSERT INTO "%s".salariati (cnp, nume, prenume, data_angajare, ore_zi, judet_casa, cor) VALUES '
              "('1900101410011', 'IONESCU', 'VASILE', '2024-01-01', 8, 'B', '241107') RETURNING id, data_angajare), "
              'i AS (INSERT INTO "%s".salariu_istoric (salariat_id, valabil_din, salariu_brut) SELECT id, data_angajare, 4050 FROM s) '
              "SELECT id FROM s" % (s, s))[0][0]
    d0 = AZI.replace(day=13)
    sql('INSERT INTO "%s".concedii_medicale (salariat_id, an, luna, cod, zile, indemnizatie, baza, media_zilnica, procent, diminuare, '
        "zile_platite, zile_ang, zile_fnuass, brut_ang, brut_fnuass, cass, impozit, cas, net, serie, numar, loc_prescriere, data_acordare, "
        "data_inceput, data_sfarsit) VALUES (%%s, %%s, %%s, '01', 3, 262, 24300, 116.45, 75, false, 3, 3, 0, 262, 0, 26, 17, 66, 153, 'AB', "
        "'1234567', 1, %%s, %%s, %%s)" % s, (sid, AZI.year, AZI.month, d0, d0, d0 + _dt.timedelta(days=2)))
    return sid


def test_def_411_stat_cu_cm_arata_netul_de_plata_si_costul_cu_indemnizatia(patron, firma_cv):
    """411 (PRIORITAR). Stat cu CM: netul arăta numai salariul. Pașii: salariat cu salariul 4.050 lei și CM cod 01 pe 3 zile în luna
    curentă -> Salariați: rândul arată „net <salariu + CM> (salariu … + indemnizație CM …)”, costul cuprinde indemnizația angajatorului,
    compoziția netului se termină cu „Net de plată (salariu + indemnizație CM)”, iar deducerea stă sub impozit, nu printre rețineri."""
    from e2e_bloc_a import _api, _card, _ok
    sid = _salariat_cu_cm(firma_cv)
    st = _ok(_api(patron, "GET", "/tenants/%d/stat-plata?an=%d&luna=%d" % (firma_cv["tenant_id"], AZI.year, AZI.month)), "stat")["stat"]
    r = next(x for x in st if x["id"] == sid)
    assert r["cm_net"] > 0 and abs(r["net_de_plata"] - (r["net"] + r["cm_net"])) < 0.005, r
    patron.firma(firma_cv["nume"])
    _card(patron, "salariati", "#sp-contare")
    pg = patron.pg
    rand = pg.locator(".pf-frand", has_text="IONESCU VASILE").first
    t = " ".join(rand.inner_text().split())
    patron.captura()
    assert ("net %s (salariu %s + indemnizație CM %s)" % (_lei(r["net_de_plata"]), _lei(r["net"]), _lei(r["cm_net"]))) in t, t
    assert ("cost %s" % _lei(r["cost_total"])) in t and abs(r["cost_total"] - r["cost"] - 262) < 0.005, (t, r)
    rand.locator("details.dec-xml summary").click()
    t = " ".join(rand.inner_text().split())
    assert ("din ce se face %s lei" % _lei(r["net_de_plata"])) in t and ("Net de plată (salariu + indemnizație CM) %s" % _lei(r["net_de_plata"])) in t, t
    assert "în calculul impozitului, scade baza (nu se reține): deducere personală" in t, t


# ── 416 / 417 / 419 — stornarea ─────────────────────────────────────────────────────────────────────────────────────────
def test_def_419_stornarea_intreaba_de_retur_si_readuce_marfa(patron, firma_cv):
    """419 (PRIORITAR, 9.3). Pașii: factură cu un articol din stoc, emisă cu „Pleacă marfa acum: Da” -> detaliul -> „Stornează”: întrebarea
    „Marfa … se întoarce în stoc?”; fără răspuns: „NU s-a salvat.”; „Da” -> „Confirm stornarea”: confirmarea spune că marfa a revenit în
    stoc, iar stocul articolului e iar cel dinainte. 416: factura stornată apare „stornată” în Istoric facturi."""
    from e2e_bloc_a import ARTICOL, _api, _card, _ok, articol_in_stoc, emite_api
    tid = firma_cv["tenant_id"]
    aid = articol_in_stoc(patron, firma_cv, cantitate=22, pret=10)
    stoc0 = next(a for a in _ok(_api(patron, "GET", "/tenants/%d/stocuri/articole" % tid), "art")["articole"] if a["id"] == aid)["stoc"]
    f = emite_api(patron, firma_cv, linii=[{"descriere": ARTICOL, "cantitate": 1, "um": "buc", "pret_unitar": 20.0, "cota_tva": 21,
                                             "cota_propusa": 21, "articol_id": aid}], pleaca_marfa=True)
    from e2e_bloc_a import _deschide_factura
    _deschide_factura(patron, firma_cv, f["factura_id"])
    pg = patron.pg
    pg.wait_for_selector("#fd-storno", timeout=20000)
    pg.click("#fd-storno")
    pg.wait_for_selector("#fd-storno-retur", timeout=10000)
    assert "se întoarce în stoc?" in pg.inner_text("#fd-storno-zona")
    pg.click("#fd-storno-ok")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    pg.select_option("#fd-storno-retur", "true")
    pg.click("#fd-storno-ok")
    pg.wait_for_function("() => (document.querySelector('#fd-storno-rez') || {}).textContent && "
                         "document.querySelector('#fd-storno-rez').textContent.includes('Storno creat')", timeout=30000)
    t = pg.inner_text("#fd-storno-rez")
    patron.captura()
    assert "Marfa a revenit în stoc: %s × 1 buc" % ARTICOL in t and pg.is_visible("#fd-spre-istoric"), t
    stoc1 = next(a for a in _ok(_api(patron, "GET", "/tenants/%d/stocuri/articole" % tid), "art")["articole"] if a["id"] == aid)["stoc"]
    assert float(stoc1) == float(stoc0), (stoc0, stoc1)
    pg.click("#fd-spre-istoric")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % f["factura_id"], timeout=20000)
    rand = " ".join(pg.inner_text(".fac-frand-btn[data-id='%s']" % f["factura_id"]).split())
    patron.captura("istoric")
    assert "stornată" in rand, rand


def test_def_416_factura_stornata_integral_e_stornata_nu_neincasata(patron, firma_cv):
    """416. Pașii: factură emisă (servicii) -> stornare integrală -> Istoric facturi: factura „stornată”, nu „neîncasată”."""
    from e2e_bloc_a import _api, _card, _ok, emite_api
    f = emite_api(patron, firma_cv)
    _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (firma_cv["tenant_id"], f["factura_id"]), {}), "storno")
    patron.firma(firma_cv["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg = patron.pg
    pg.click("#fac-istoric")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % f["factura_id"], timeout=25000)
    rand = " ".join(pg.inner_text(".fac-frand-btn[data-id='%s']" % f["factura_id"]).split())
    patron.captura()
    assert "stornată" in rand and "neîncasată" not in rand, rand


# ── 398–400 — NIR-ul ────────────────────────────────────────────────────────────────────────────────────────────────────
def _nir_form(patron, firma, numar):
    from e2e_bloc_a import _card
    patron.firma(firma["nume"])
    _card(patron, "stocuri", "#sn-toggle")
    pg = patron.pg
    pg.click("#sn-toggle")
    pg.fill("#sn-numar", numar)
    pg.select_option("#nir-l0-articol", "nou")
    pg.fill("#nir-l0-denumire", "Marfa NIR %s" % numar)
    pg.fill("#nir-l0-cantitate", "2")
    pg.fill("#nir-l0-pret_achizitie", "25")
    pg.select_option("#nir-l0-cota_tva", "21")
    pg.fill("#sn-transport", "5")
    return pg


def _nir_salvat(patron, firma, numar):
    """NIR cu factura nesosită și TVA 21% pe transport, salvat din formular; deschide detaliul lui."""
    pg = _nir_form(patron, firma, numar)
    pg.select_option("#sn-factura-sosita", "false")
    pg.select_option("#sn-transport-cota", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('NIR salvat')", timeout=30000)
    pg.click(".nir-deschide[data-numar='%s']" % numar)
    pg.wait_for_selector("#nir-detaliu-linii", timeout=20000)
    return pg


def test_def_399_nir_cere_factura_sosita_si_tva_transportului(patron, firma_cv):
    """399. Pașii: Stocuri -> „+ NIR nou” -> articol nou, 2 buc × 25 lei, 21%, transport 5 lei -> Salvează: „NU s-a salvat.” cu
    „Factura furnizorului a sosit?” și cota TVA a transportului (nimic presupus); „Nu” + 21% -> NIR salvat."""
    pg = _nir_form(patron, firma_cv, "N399")
    pg.click("#sn-salveaza")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    lista = _refuz(pg)
    patron.captura("refuz")
    assert [x[0] for x in lista] == ["Factura furnizorului a sosit?", "Cota TVA a transportului"], lista
    pg.select_option("#sn-factura-sosita", "false")
    pg.select_option("#sn-transport-cota", "21")
    pg.click("#sn-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('NIR salvat')", timeout=30000)
    patron.captura()


def test_def_398_toate_liniile_nir_pe_aceeasi_regula(patron, firma_cv):
    """398. Pașii: NIR cu factura nesosită și transport -> detaliul: notele marfa ȘI transportul pe 408, cu TVA-ul lor pe 4428.01."""
    pg = _nir_salvat(patron, firma_cv, "N398")
    note = pg.eval_on_selector_all("table.fd-tabel:last-of-type tbody tr", "trs => trs.map(t => [...t.cells].slice(1, 4).map(c => c.innerText.trim()))")
    patron.captura()
    assert sorted(note) == sorted([["371", "408", "50,00"], ["4428.01", "408", "10,50"], ["371", "408", "5,00"], ["4428.01", "408", "1,05"]]), note


def test_def_400_detaliul_nir_arata_transportul_repartizat_si_costul_unitar(patron, firma_cv):
    """400. Pașii: NIR 2 buc × 25 lei + transport 5 -> detaliul: transportul repartizat 5,00, costul final 55,00, costul unitar 27,50."""
    pg = _nir_salvat(patron, firma_cv, "N400")
    cel = pg.eval_on_selector_all("#nir-detaliu-linii tbody tr td", "tds => tds.map(t => t.innerText.trim())")
    patron.captura()
    assert cel[-3:] == ["5,00", "55,00", "27,50"], cel


# ── 401–402 — borderoul de achiziție ─────────────────────────────────────────────────────────────────────────────────────
def test_def_401_borderoul_de_achizitie_cere_vanzatorul_si_arata_nota(patron, firma_cv):
    """401, 402. Pașii: Operațiuni speciale -> „Achiziție de la neînregistrat” -> fără domiciliu și act de identitate: lângă câmpuri
    (și „NU s-a salvat.”); completat, cont 371 cu articolul și cantitatea -> „Notă generată … Nota: 371 = 401 200,00 lei.”; în Registrul
    jurnal documentul e „Borderou de achiziție BA-1 din …”, nu „Factură”."""
    from e2e_bloc_a import _card
    patron.firma(firma_cv["nume"])
    _card(patron, "operatiuni", "[data-op='neinregistrat']")
    pg = patron.pg
    pg.click("[data-op='neinregistrat']")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", "Ion Popescu")
    pg.fill("#op-valoare", "200")
    pg.fill("#op-cont_cheltuiala", "371")
    pg.click("#op-trimite")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    assert {x[0] for x in _refuz(pg)} >= {"Domiciliul vânzătorului", "Actul de identitate (seria și numărul)"}, _refuz(pg)
    pg.fill("#op-furnizor_adresa", "Str. Florilor 1, Ploiești")
    pg.fill("#op-furnizor_act", "PH 123456")
    pg.fill("#op-articol", "Mere E2E")
    pg.fill("#op-cantitate", "100")
    pg.fill("#op-um", "kg")
    pg.select_option("#op-categorie", "alte_bunuri")
    pg.click("#op-trimite")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {}).innerText && "
                         "document.querySelector('#op-mesaj').innerText.includes('Notă generată')", timeout=30000)
    t = pg.inner_text("#op-mesaj")
    patron.captura()
    assert "Nota: 371 = 401 200,00 lei." in t, t
    patron.firma(firma_cv["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg.wait_for_function("() => document.body.innerText.includes('Borderou de achiziție BA-1 din')", timeout=20000)
    patron.captura("jurnal")


def test_def_402_achizitia_pf_pe_stoc_cere_articolul_si_intra_in_gestiune(patron, firma_cv):
    """402. Achiziție de la neînregistrat pe 371, cu vânzătorul identificat, dar fără articol și cantitate -> „NU s-a salvat.” cu cele două
    câmpuri (nu 371 crescut fără stoc); completat (Pere E2E 402, 50 kg) -> articolul intră în gestiune: fișa lui are intrarea de 120,00
    lei, cu borderoul ca document."""
    from e2e_bloc_a import _card
    patron.firma(firma_cv["nume"])
    _card(patron, "operatiuni", "[data-op='neinregistrat']")
    pg = patron.pg
    pg.click("[data-op='neinregistrat']")
    pg.wait_for_selector("#op-furnizor_nume", timeout=20000)
    pg.fill("#op-data", AZI.isoformat())
    pg.fill("#op-furnizor_nume", "Maria Ionescu")
    pg.fill("#op-furnizor_adresa", "Str. Livezii 2, Buzău")
    pg.fill("#op-furnizor_act", "BZ 654321")
    pg.fill("#op-valoare", "120")
    pg.fill("#op-cont_cheltuiala", "371")
    pg.select_option("#op-categorie", "alte_bunuri")
    pg.click("#op-trimite")
    pg.wait_for_selector(".refuz-salvare", timeout=10000)
    patron.captura("refuz")
    assert {x[0] for x in _refuz(pg)} == {"Articolul (la un cont de stoc)", "Cantitatea (la un cont de stoc)",
                                       "motivul e mai jos"}, _refuz(pg)
    s = firma_cv["schema"]
    assert sql('SELECT count(*) FROM "%s".articole WHERE denumire = %%s' % s, ("Pere E2E 402",))[0][0] == 0
    pg.fill("#op-articol", "Pere E2E 402")
    pg.fill("#op-cantitate", "50")
    pg.fill("#op-um", "kg")
    pg.click("#op-trimite")
    pg.wait_for_function("() => (document.querySelector('#op-mesaj') || {}).innerText && "
                         "document.querySelector('#op-mesaj').innerText.includes('Notă generată')", timeout=30000)
    patron.captura()
    m = sql('SELECT m.tip, m.cantitate, m.valoare, m.document FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id '
            "WHERE a.denumire = %%s" % (s, s), ("Pere E2E 402",))
    assert [(r[0], float(r[1]), float(r[2])) for r in m] == [("intrare", 50.0, 120.0)] and m[0][3].startswith("Borderou de achiziție BA-"), m


# ── 404 — inventarul ────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_404_lipsa_la_inventar_se_incadreaza(patron, firma_cv):
    """404. Pașii: Stocuri -> „Mișcări, fișe…” -> Inventar: faptic sub scriptic -> apare „lipsă imputabilă / neimputabilă / justificată”;
    fără alegere: refuzul lângă ea; „neimputabilă” -> nota 607=371 + 635=4427 și „nedeductibile … (CF art.25 alin.(4) lit.c)”."""
    from e2e_bloc_a import ARTICOL, _card, articol_in_stoc
    aid = articol_in_stoc(patron, firma_cv)
    patron.firma(firma_cv["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-inv", timeout=20000)
    pg.click("#cv-inv")
    pg.fill("#cvi-a%d-faptic" % aid, "0")
    pg.wait_for_selector("#cvi-a%d-lipsa" % aid, state="visible", timeout=5000)
    pg.click("#cvi-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="cvi-a%d-lipsa"]' % aid, timeout=20000)
    pg.select_option("#cvi-a%d-lipsa" % aid, "neimputabila")
    pg.click("#cvi-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('nedeductibile la impozitul pe profit')", timeout=20000)
    t = " ".join(pg.inner_text("body").split())
    patron.captura()
    assert ("%s: minus" % ARTICOL) in t and "607=371 + 635=4427" in t and "(CF art.25 alin.(4) lit.c)" in t, t[-1500:]


# ── 407 — avansul acordat furnizorului ─────────────────────────────────────────────────────────────────────────────────
def test_def_407_avansul_platit_furnizorului_cere_destinatia_si_e_409x(patron, firma_cv):
    """407. Pașii: numerar în casă -> Casă -> plată furnizor 300 lei fără facturi deschise: previzualizarea spune avansul acordat
    (nota 409x = 5311, factura o emite furnizorul) și cere „Avansul e pentru”; „bunuri (4091)” -> Adaugă -> nota 4091=5311."""
    from e2e_bloc_a import _card
    _numerar(patron, firma_cv)
    patron.firma(firma_cv["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.click("#c-toggle")
    pg.select_option("#c-cat", "plata_furnizor")
    pg.fill("#c-suma", "300")
    pg.fill("#c-part", "DANTE INTERNATIONAL SA")
    pg.fill("#c-cui", "14399840")
    pg.fill("#c-doc", "DP407")
    pg.wait_for_selector("#c-avans-dest", timeout=10000)
    t = pg.inner_text("#c-previz")
    assert "avans acordat furnizorului, cu nota 409x = 5311" in t and "Emite factura" not in t, t
    pg.select_option("#c-avans-dest", "stocuri")
    pg.click("#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=20000)
    patron.captura()
    assert "4091=5311" in pg.inner_text("body")


# ── 412 / 413 / 414 — salarii (salariatul lui 411) ─────────────────────────────────────────────────────────────────────
def _stat(patron, firma):
    from e2e_bloc_a import _card
    _salariat_cu_cm(firma)
    patron.firma(firma["nume"])
    _card(patron, "salariati", "#sp-contare")
    return patron.pg


def test_def_412_adeverinta_precompleteaza_functia_din_fisa(patron, firma_cv):
    """412. Pașii: Salariați -> „Adeverință” la salariatul cu ocupația COR 241107: „Funcția” = „auditor financiar”, modificabilă."""
    pg = _stat(patron, firma_cv)
    pg.locator(".pf-frand", has_text="IONESCU VASILE").first.locator("[data-adev]").click()
    pg.wait_for_function("() => (document.querySelector('#ad-functie') || {}).value === 'auditor financiar'", timeout=20000)
    patron.captura()


def test_def_413_orele_suplimentare_propun_suma_si_semnaleaza_sporul_sub_75(patron, firma_cv):
    """413. Pașii: Salariați -> „Prime, sporuri, ore supl.” -> ore suplimentare 10 ore, spor 50%: suma propusă = tarif × ore × 1,5 și
    semnalul „sub 75% … art.123 alin.(2)”."""
    pg = _stat(patron, firma_cv)
    pg.locator(".pf-frand", has_text="IONESCU VASILE").first.locator("[data-elem]").click()
    pg.select_option("#el-tip", "ore_suplimentare")
    pg.fill("#el-ore", "10")
    pg.fill("#el-spor", "50")
    pg.wait_for_function("() => (document.querySelector('#el-propunere') || {}).innerText", timeout=5000)
    t = pg.inner_text("#el-propunere")
    suma = pg.input_value("#el-suma")
    patron.captura()
    assert t.startswith("Propus: ") and "× 10 ore × (1 + 50%)" in t and "art.123 alin.(2)" in t and float(suma) > 0, (t, suma)


def test_def_414_luna_in_curs_nu_ofera_butonul_care_scrie_nota(patron, firma_cv):
    """414. Pașii: Salariați -> „Contabilizează statul” în luna în curs: „Nota salariilor se scrie după ce luna se încheie”, niciun buton
    care scrie nota (nici înlocuirea ciornei, nici recontabilizarea)."""
    pg = _stat(patron, firma_cv)
    pg.click("#sp-contare")
    pg.wait_for_selector("#sp-contare-neincheiata", timeout=30000)
    patron.captura()
    assert pg.query_selector("#sp-contare-scrie") is None


# ── 418 — importul e-Factura (9.3) ──────────────────────────────────────────────────────────────────────────────────────
UBL_418 = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>{numar}</cbc:ID><cbc:IssueDate>{data}</cbc:IssueDate><cbc:DocumentCurrencyCode>RON</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party><cac:PartyTaxScheme><cbc:CompanyID>RO14399840</cbc:CompanyID><cac:TaxScheme><cbc:ID>VAT</cbc:ID>
    </cac:TaxScheme></cac:PartyTaxScheme><cac:PartyLegalEntity><cbc:RegistrationName>DANTE INTERNATIONAL SA</cbc:RegistrationName>
    </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity><cbc:RegistrationName>{client}</cbc:RegistrationName></cac:PartyLegalEntity>
    <cac:PartyTaxScheme><cbc:CompanyID>RO{cui}</cbc:CompanyID></cac:PartyTaxScheme></cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount>143.54</cbc:TaxAmount></cac:TaxTotal>
  <cac:LegalMonetaryTotal><cbc:TaxInclusiveAmount>827.04</cbc:TaxInclusiveAmount></cac:LegalMonetaryTotal>
  <cac:InvoiceLine><cbc:InvoicedQuantity>10</cbc:InvoicedQuantity><cbc:LineExtensionAmount>483.50</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>48.35</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Marfa A 418</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
  <cac:InvoiceLine><cbc:InvoicedQuantity>5</cbc:InvoicedQuantity><cbc:LineExtensionAmount>200.00</cbc:LineExtensionAmount>
    <cac:Price><cbc:PriceAmount>40.00</cbc:PriceAmount></cac:Price>
    <cac:Item><cbc:Name>Carte tehnica 418</cbc:Name><cac:ClassifiedTaxCategory><cbc:ID>S</cbc:ID><cbc:Percent>21</cbc:Percent></cac:ClassifiedTaxCategory></cac:Item>
  </cac:InvoiceLine>
</Invoice>"""


def test_def_418_statutul_furnizorului_aflat_contul_pe_linie_si_confirmarea_ramane(patron, firma_cv):
    """418 a, b, c (9.3). Pașii: Facturi primite -> importă XML-ul (furnizorul cu cod de TVA RO în PartyTaxScheme/VAT) -> detaliul:
    „Furnizorul e înregistrat în scopuri de TVA” și „TVA la încasare” AFLATE (ANAF / XML), fără alegere; marfa pe contul facturii (371),
    cartea pe contul ei (6028) -> Validează: confirmarea rămâne, cu „← Înapoi” (nu sare singură); în bază: 371 și 6028 pe linii, în stoc
    numai marfa."""
    import time as _t
    from e2e_bloc_a import _card
    tag = "E2E418-%d" % _t.time()
    s = firma_cv["schema"]
    patron.firma(firma_cv["nume"])
    pg = patron.pg
    _card(patron, "facturi", "#fac-primite")
    pg.click("#fac-primite")
    cifre = "".join(c for c in sql('SELECT cui FROM "%s".firma_profil WHERE id = 1' % s)[0][0] if c.isdigit())
    pg.set_input_files("#fp-xml", {"name": "%s.xml" % tag, "mimeType": "text/xml", "buffer": UBL_418.format(
        numar=tag, data=AZI.isoformat(), client=firma_cv["nume"], cui=cifre).encode("utf-8")})
    pg.wait_for_function("() => (document.querySelector('#fp-mesaj') || {innerText: ''}).innerText.includes('importat')", timeout=40000)
    pg.locator(".fac-primita-btn", has_text=tag).click()
    pg.wait_for_selector("#pr-cont", timeout=20000)
    patron.captura("detaliu")
    assert pg.query_selector("#pr-platitor") is None and pg.query_selector("#pr-furnizor-incasare") is None, "statutul se cere de mână"
    t = " ".join(pg.inner_text(".fereastra:last-of-type").split())
    assert "Aflat din ANAF, registrul contribuabililor" in t or "Aflat din XML-ul facturii: codul de TVA RO14399840" in t, t[:1500]
    pg.fill("#pr-cont", "371")
    pg.fill("#pr-cont-l1", "6028")
    pg.click("#pr-valideaza")
    pg.click("#ca-ok")
    pg.wait_for_function("() => document.querySelector('#pr-zona').innerText.includes('Validată')", timeout=40000)
    pg.wait_for_timeout(1500)   # înainte, ecranul pleca singur după 0,9 s
    patron.captura("validata")
    assert pg.is_visible("#pr-zona") and pg.locator("#pr-zona button", has_text="Înapoi").count() == 1
    fid = sql('SELECT id FROM "%s".facturi WHERE numar = %%s' % s, (tag,))[0][0]
    linii = sql('SELECT l.cont_debit, l.suma FROM "%s".inregistrari_linii l JOIN "%s".inregistrari i ON i.id = l.inregistrare_id '
                "WHERE i.factura_id = %%s AND l.cont_credit = '401' AND l.cont_debit IN ('371', '6028') ORDER BY l.cont_debit" % (s, s), (fid,))
    assert [(d, float(v)) for d, v in linii] == [("371", 483.5), ("6028", 200.0)], linii
    stoc = sql('SELECT a.denumire FROM "%s".miscari_stoc m JOIN "%s".articole a ON a.id = m.articol_id WHERE m.factura_id = %%s' % (s, s), (fid,))
    assert stoc == [("Marfa A 418",)], stoc


# ── 415 — articolul creat din NIR își are cota la emitere ─────────────────────────────────────────────────────────────────
def test_def_415_articolul_nou_din_nir_are_cota_la_emitere(patron, firma_cv):
    """415. Pașii: NIR cu „+ articol nou” Marfa NIR 415, cota 21% (factură nesosită) -> Emite factură, linia cu articolul din stoc:
    cota 21% vine din articol, fără mesajul „articolul … n-are cotă în nomenclator”."""
    from e2e_bloc_a import _api, _ok
    tid = firma_cv["tenant_id"]
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/nir" % tid, {"factura_sosita": False, "numar": "N415", "data": AZI.isoformat(),
                                                               "furnizor": "DANTE INTERNATIONAL SA", "cui": "14399840",
                                                               "linii": [{"denumire": "Marfa NIR 415", "articol_nou": True, "cantitate": 3,
                                                                          "pret_achizitie": 10, "cota_tva": 21}]}), "NIR")
    r = _ok(_api(patron, "POST", "/tenants/%d/produse/potriveste" % tid, {"denumire": "Marfa NIR 415", "articol": True}), "potrivire")
    assert r.get("ok") is True and float(r["cota"]) == 21.0, r


# ── 403 / 408 / 417 ─────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_403_fisa_de_magazie_numeste_documentul_nu_id_ul(patron, firma_cv):
    """403. O mișcare scrisă de o versiune veche („Factura #1”, id-ul intern), legată de factura F… -> Stocuri -> „Vezi fișa”: documentul
    e „Factură <serie+număr> din <dată>”, nu „Factura #1”."""
    from e2e_bloc_a import _card, articol_in_stoc, emite_api
    s = firma_cv["schema"]
    aid = articol_in_stoc(patron, firma_cv)
    f = emite_api(patron, firma_cv)
    sql('INSERT INTO "%s".miscari_stoc (articol_id, data, tip, cantitate, pret_unitar, valoare, document, factura_id) VALUES (%%s, %%s, %%s, 1, 12.5, 12.5, '
        "'Factura #1', %%s)" % s, (aid, AZI, "intrare", f["factura_id"]))   # intrare: stocul articolului e comun testelor firmei
    patron.firma(firma_cv["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-fisa", timeout=20000)
    pg.select_option("#cv-art", str(aid))
    pg.click("#cv-fisa")
    pg.wait_for_selector("#cv-fisa-zona .pf-frand", timeout=20000)
    t = pg.inner_text("#cv-fisa-zona")
    patron.captura()
    assert "Factura #1" not in t and ("Factură %s din %s" % (f["numar"], AZI.strftime("%d.%m.%Y"))) in t, t   # AZI-dat-de-test (emite_api)


def test_def_408_cardul_nir_din_coada_arata_rulajul_tuturor_notelor(patron, firma_cv):
    """408. Asistentul salvează un NIR cu transport (patru note) -> coada contabilului-șef: cardul NIR-ului arată „rulaj <suma tuturor
    notelor>”, nu rulajul primei note."""
    from e2e_bloc_d import ASISTENT, _api as _api_ca, _atribuie_asistentului, _card_coada, _coada, _in_coada
    _atribuie_asistentului(firma_cv)
    st, r = _api_ca(ASISTENT, "POST", "/tenants/%d/stocuri/nir" % firma_cv["tenant_id"],
                    {"factura_sosita": False, "cota_tva_transport": 21, "numar": "N408", "data": AZI.isoformat(), "transport": 10,
                     "furnizor": "DANTE INTERNATIONAL SA", "linii": [{"denumire": "Marfa N408", "articol_nou": True, "cantitate": 10,
                                                                      "pret_achizitie": 100, "cota_tva": 21}]})
    assert st == 200 and len(r["inregistrari"]) == 4, (st, r)
    _in_coada(firma_cv)
    _coada(patron)
    card = _card_coada(patron, firma_cv, "NIR nr N408 ")
    t = " ".join(card.inner_text().split())
    patron.captura()
    # 1.000 + 210 (TVA) + 10 (transport) + 2,10 (TVA transport) = 1.222,10
    assert "rulaj 1.222,10 lei" in t, t


def test_def_417_pdf_ul_stornarii_numeste_factura_stornata(patron, firma_cv):
    """417. Factură emisă -> stornare -> PDF-ul stornării (butonul „PDF” din detaliu): „Stornare factura <serie> nr. <n> din <dată>”."""
    import base64
    import io as _io
    from pypdf import PdfReader
    from e2e_bloc_a import _api, _deschide_factura, _ok, emite_api
    tid = firma_cv["tenant_id"]
    f = emite_api(patron, firma_cv)
    st = _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, f["factura_id"]), {}), "storno")
    _deschide_factura(patron, firma_cv, st["factura_id"])
    b64 = patron.pg.evaluate("""async (u) => { const t = sessionStorage.getItem('iconta_token');
        const r = await fetch(u, {headers: {Authorization: 'Bearer ' + t}}); const b = new Uint8Array(await r.arrayBuffer());
        let s = ''; b.forEach((x) => { s += String.fromCharCode(x); }); return btoa(s); }""", "/tenants/%d/facturi/%d/pdf" % (tid, st["factura_id"]))
    text = " ".join(" ".join(p.extract_text().split()) for p in PdfReader(_io.BytesIO(base64.b64decode(b64))).pages)
    patron.captura()
    serie = sql('SELECT serie FROM "%s".facturi WHERE id = %%s' % firma_cv["schema"], (f["factura_id"],))[0][0]
    nr = f["numar"][len(serie):] if serie and f["numar"].startswith(serie) else f["numar"]
    assert ("Stornare factura %s nr. %s din %s" % (serie, nr, AZI.strftime("%d.%m.%Y"))) in text, text[:1500]   # AZI-dat-de-test


# ── găsite de Code în lot (C58, C60) ────────────────────────────────────────────────────────────────────────────────────
def test_def_c58_primul_clic_pe_adauga_dupa_tastare_pleaca(patron, firma_cv):
    """C58 (găsită de e2e la 406). Cu un refuz afișat deasupra butonului (previzualizarea casei), primul clic pe „Adaugă” după ce omul a
    tastat în ultimul câmp se pierdea: la părăsirea câmpului (`change`) eroarea dispărea, rândurile urcau între apăsare și eliberare, iar
    clicul cădea pe alt element. Pașii: Casă -> plată peste sold (previzualizarea spune refuzul) -> se scrie documentul -> UN clic pe
    „Adaugă”: cererea pleacă (refuzul serverului e lângă buton)."""
    from e2e_bloc_a import _card
    patron.firma(firma_cv["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.click("#c-toggle")
    pg.select_option("#c-cat", "depunere_banca")
    pg.fill("#c-suma", "999999")
    pg.wait_for_selector("#c-previz-refuz.msg-eroare", timeout=10000)
    cereri = []
    pg.on("request", lambda r: cereri.append(r.url) if r.method == "POST" and r.url.endswith("/casa/operatiuni") else None)
    pg.fill("#c-doc", "DD-C58")
    # tastarea a șters refuzul (`input`), previzualizarea (250 ms după tastare) îl scrie la loc: abia acum `change`-ul de la părăsirea
    # câmpului (la apăsarea pe „Adaugă”) l-ar mai putea șterge sub cursor — cazul găsit la 406
    pg.wait_for_timeout(600)
    pg.wait_for_function("() => (document.querySelector('#c-previz-refuz') || {}).textContent", timeout=10000)
    pg.click("#c-adauga")
    pg.wait_for_function("() => (document.querySelector('#c-mesaj') || {}).textContent", timeout=10000)
    patron.captura()
    assert len(cereri) == 1, cereri


def test_def_c60_registrul_de_casa_porneste_de_la_soldul_casei(patron, firma_cv):
    """C60 (găsită de Code la 406). Registrul de casă pornea de la zero în fiecare lună: o ridicare de numerar din luna trecută nu era în
    soldul lunii. Pașii: notă 5311 = 581 de 1.000 lei în luna trecută, validată -> Casă, luna curentă: „sold la început 1.000,00 lei”
    (și soldurile de pe rânduri pornesc de acolo)."""
    from e2e_bloc_a import _card
    from e2e_bloc_e import _nota
    luna_trecuta = (AZI.replace(day=1) - _dt.timedelta(days=1)).replace(day=10)
    _nota(firma_cv, luna_trecuta.isoformat(), [{"debit": "5311", "credit": "581", "suma": 1000}], "Ridicare C60", valideaza=True,
          document_ref="Cec C60")
    patron.firma(firma_cv["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    pg.wait_for_selector("#c-sold-inceput", timeout=20000)
    patron.captura()
    assert pg.inner_text("#c-sold-inceput") == "1.000,00 lei"


# ── C59 — stornarea poartă orașul și județul clientului (e-Factura BT-52 / BT-54) ─────────────────────────────────────────
_NS_UBL = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
           "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}


def test_def_c59_stornarea_pastreaza_orasul_si_judetul_clientului_in_xml(patron, firma_cv):
    """C59 (găsită de validatorul ANAF FACT1 la 417, lotul 9.2). Stornarea nu copia orașul și județul clientului: XML-ul e-Factura al
    stornării ieșea fără ele (BR-RO-110, BT-54). Pașii: factură emisă către DANTE INTERNATIONAL SA, cu localitatea „Sector 6” și județul
    „B” -> Istoric facturi -> detaliul: „Către: … București, Sector 6” -> „Stornează” (la întrebarea de retur, dacă apare: „Nu”) -> „Confirm
    stornarea” -> „Înapoi la Istoric facturi” -> stornarea: „Către: … București, Sector 6” -> XML-ul e-Factura al stornării: la cumpărător
    CityName SECTOR6 și CountrySubentity RO-B, iar BillingReference trimite la factura stornată (numărul și data ei).

    De la C62, pe stornare „Trimite în SPV” (#fd-spv) apare (testul C62 de mai jos), dar în proba SPV nu e conectat: trimiterea se oprește
    la poarta tokenului (`efactura_trimitere.trimite`, `MESAJ_FARA_TOKEN`) ÎNAINTE de a genera XML-ul, iar „Export SAGA” e XML-ul SAGA, nu
    UBL. De aceea XML-ul se generează cu funcția pe care o cheamă „Trimite în SPV” după poarta tokenului
    (`efactura_trimitere.genereaza_din_factura`), pe stornarea creată din ecran. Formularul de emitere trimite localitatea și județul
    numai la clientul străin (emitere_ecran.js, `tert_oras` / `tert_judet`), deci factura de pornire se emite pe ruta formularului, cu
    ele în corp."""
    import xml.etree.ElementTree as ET
    from conftest import _db
    from core import efactura_trimitere as _eft
    from e2e_bloc_a import CLIENT, PRODUS, _api, _deschide_factura, _ok, _profil
    tid, s = firma_cv["tenant_id"], firma_cv["schema"]
    # adresa, localitatea, județul — cum le pune detaliul (`factura_pdf.adresa_tert`): de la C61 județul român apare cu numele lui
    # („București”), iar adresa clientului îl cuprinde deja, deci nu se repetă
    assert "București" in CLIENT["#em-adresa"], CLIENT["#em-adresa"]
    adresa_vazuta = "%s, Sector 6" % CLIENT["#em-adresa"]
    # vânzătorul din București cere sectorul în adresă (`efactura_send._localitate`, BR-RO-100), altfel XML-ul se oprește la vânzător
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, dict(_profil(firma_cv), adresa="Str. Proba 1, Sector 1")),
        "Date firmă cu sectorul")
    try:
        corp = {"linii": [{"descriere": PRODUS, "cantitate": 2, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                           "articol_id": None}],
                "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"],
                "tert_oras": "Sector 6", "tert_judet": "B",   # ce n-ajunge din formular la un client din România
                "moneda": "RON", "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
                "data_emitere": AZI.isoformat(), "data_scadenta": (AZI + _dt.timedelta(days=30)).isoformat(), "tip": "factura"}
        f = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % tid, corp), "emitere")
        _deschide_factura(patron, firma_cv, f["factura_id"])
        pg = patron.pg
        t = pg.locator(".fd-antet .tip-micut").last.inner_text()
        assert t == adresa_vazuta, t   # factura de pornire chiar poartă localitatea și județul
        pg.click("#fd-storno")
        pg.wait_for_selector("#fd-storno-ok", timeout=10000)
        if pg.query_selector("#fd-storno-retur"):   # numai la factura care a descărcat stocul (419)
            pg.select_option("#fd-storno-retur", "false")
        with pg.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/facturi/%d/storno" % f["factura_id"]),
                                timeout=30000) as rr:
            pg.click("#fd-storno-ok")
        st = rr.value.json()
        assert rr.value.status == 200 and st.get("factura_id"), (rr.value.status, st)
        pg.wait_for_function("() => (document.querySelector('#fd-storno-rez') || {}).textContent && "
                             "document.querySelector('#fd-storno-rez').textContent.includes('Storno creat')", timeout=30000)
        pg.click("#fd-spre-istoric")
        pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % st["factura_id"], timeout=20000)
        pg.click(".fac-frand-btn[data-id='%s']" % st["factura_id"])
        pg.wait_for_function("(x) => [...document.querySelectorAll('.fd-antet h2')].some((h) => h.textContent.trim() === x)",
                             arg="Factură %s" % st["numar"], timeout=25000)
        t = pg.locator(".fd-antet .tip-micut").last.inner_text()
        patron.captura()
        assert t == adresa_vazuta, t   # stornarea, pe ecran: aceeași adresă cu localitatea și județul
        # XML-ul e-Factura al stornării (aceeași funcție ca „Trimite în SPV”), numai citire; numai argumentele poziționale
        with _db().get_conn(s) as c:
            xml, _f = _eft.genereaza_din_factura(c, s, st["factura_id"])
            c.rollback()
        rad = ET.fromstring(xml.encode("utf-8"))
        adr = rad.find("cac:AccountingCustomerParty/cac:Party/cac:PostalAddress", _NS_UBL)
        assert adr is not None, xml[:2000]
        # BT-52 (în București sectorul, BR-RO-100) și BT-54 (codul ISO 3166-2:RO, BR-RO-110)
        assert (adr.findtext("cbc:CityName", namespaces=_NS_UBL), adr.findtext("cbc:CountrySubentity", namespaces=_NS_UBL)) == (
            "SECTOR6", "RO-B"), ET.tostring(adr, encoding="unicode")
        # BG-3: BT-25 numărul facturii stornate (cu seria, ca în BT-1 al ei) și BT-26 data ei
        ref = [(x.findtext("cbc:ID", namespaces=_NS_UBL), x.findtext("cbc:IssueDate", namespaces=_NS_UBL))
               for x in rad.findall("cac:BillingReference/cac:InvoiceDocumentReference", _NS_UBL)]
        assert ref == [(f["numar"], AZI.isoformat())], (ref, f["numar"])   # AZI-dat-de-test
    finally:
        _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % tid, _profil(firma_cv)), "Date firmă la loc")


# ── C62 — stornarea se trimite în SPV din ecran ───────────────────────────────────────────────────────────────────────────
def test_def_c62_stornarea_se_trimite_in_spv_din_ecran(patron, firma_cv):
    """C62 (găsită de Code 19.10.2026). Pe stornarea unei facturi emise „Trimite în SPV” lipsea (condiția `!f.storno_din_id`, pusă pe
    18.07.2026 când generatorul UBL nu trata stornarea); de la 417 XML-ul stornării trimite la factura stornată și trece FACT1. Temei:
    OUG 120/2021 art.4 alin.(10) — „Factura electronică corectată se transmite în cadrul aceluiași sistem național privind factura
    electronică RO e-Factura.” Pașii: factură emisă -> stornare -> Istoric facturi -> stornarea: starea „netrimisă în SPV · termen …” și
    butonul „Trimite în SPV” -> „Trimite în SPV” în caseta de confirmare: cererea pleacă pe `facturi/<stornare>/trimite-spv`, iar
    răspunsul serverului e lângă buton (în probă cabinetul nu e conectat la SPV: „Cabinetul nu e conectat la SPV, …”, cu butonul spre
    Conectare SPV)."""
    from core import efactura_trimitere as _eft
    from core.uc_tenants import COD_SPV_NECONECTAT
    from e2e_bloc_a import _api, _deschide_factura, _ok, emite_api
    tid = firma_cv["tenant_id"]
    cab = sql("SELECT accounting_firm_id FROM public.tenants WHERE id = %s", (tid,))[0][0]
    assert sql("SELECT count(*) FROM public.spv_token WHERE accounting_firm_id = %s AND activ", (cab,)) == [(0,)], "premisa: neconectat"
    f = emite_api(patron, firma_cv)
    st = _ok(_api(patron, "POST", "/tenants/%d/facturi/%d/storno" % (tid, f["factura_id"]), {}), "storno")
    _deschide_factura(patron, firma_cv, st["factura_id"])
    pg = patron.pg
    assert pg.inner_text(".fd-antet .fd-stare") == "storno"   # chiar stornarea e deschisă
    assert pg.inner_text("#fd-stare-spv").startswith("netrimisă în SPV · termen "), pg.inner_text("#fd-stare-spv")
    assert pg.inner_text("#fd-spv") == "Trimite în SPV"
    pg.click("#fd-spv")
    with pg.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/facturi/%d/trimite-spv" % st["factura_id"]),
                            timeout=30000) as rr:
        pg.click("#ca-ok")
    corp = rr.value.json()
    assert rr.value.status == 409 and (corp.get("detail") or {}).get("cod") == COD_SPV_NECONECTAT, (rr.value.status, corp)
    pg.wait_for_selector("#fd-spv-zona [data-ecran-destinatie='conectare_spv']", timeout=20000)
    zona = " ".join(pg.inner_text("#fd-spv-zona").split())
    patron.captura()
    assert " ".join(_eft.MESAJ_FARA_TOKEN.split()) in zona, zona
    assert sql('SELECT count(*) FROM "%s".efactura_trimiteri WHERE factura_id = %%s' % firma_cv["schema"], (st["factura_id"],)) == [(0,)], \
        "nimic încărcat"


# ── C63 / C64 — factura născută din proformă ────────────────────────────────────────────────────────────────────────────
def _proforma_transformata(patron, firma):
    """O proformă către DANTE, cu adresa clientului și linia „3 ora” -> detaliul ei -> „Transformă în factură”. Întoarce (pagina, adresa
    proformei de pe ecran, răspunsul transformării)."""
    from e2e_bloc_a import CLIENT, PRODUS, _api, _deschide_factura, _ok
    corp = {"linii": [{"descriere": PRODUS, "cantitate": 3, "um": "ora", "pret_unitar": 150.0, "cota_tva": 21, "cota_propusa": 21,
                       "articol_id": None}],
            "tert_nume": CLIENT["#em-nume"], "tert_cui": CLIENT["#em-cui"], "tert_adresa": CLIENT["#em-adresa"], "moneda": "RON",
            "tert_tara": "RO", "tip_operatiune": "normal", "bon_fiscal_nr": None, "bon_fiscal_data": None,
            "data_emitere": AZI.isoformat(), "data_scadenta": None, "tip": "proforma"}
    p = _ok(_api(patron, "POST", "/tenants/%d/facturi/emite" % firma["tenant_id"], corp), "proforma")
    _deschide_factura(patron, firma, p["factura_id"])
    pg = patron.pg
    pg.wait_for_selector("#fd-transforma", timeout=20000)
    adresa = " ".join(pg.inner_text(".fd-antet .tip-micut").split())
    assert adresa == CLIENT["#em-adresa"], adresa
    with pg.expect_response(lambda r: r.url.endswith("/transforma") and r.request.method == "POST", timeout=30000) as rr:
        pg.click("#fd-transforma")
    return pg, adresa, rr.value.json()


def test_def_c63_factura_din_proforma_pastreaza_adresa_si_unitatea(patron, firma_cv):
    """C63 (găsită de Code, 19.10.2026). Pașii: proforma -> „Transformă în factură” -> „transformată în …”: factura are aceeași adresă
    a clientului și aceeași unitate de măsură („ora”, nu „buc”). Înainte, transformarea le pierdea (adresa: CF art.319 alin.(20) lit.f).
    MUTAȚIE: `tert_adresa` scos din `uc_tenants.antet_din_proforma` -> adresa lipsește de pe factură -> ROȘU."""
    pg, adresa, _r = _proforma_transformata(patron, firma_cv)
    pg.wait_for_selector("#fd-vezi-transformata", timeout=30000)
    pg.click("#fd-vezi-transformata")
    pg.wait_for_function("() => /^Factur/.test((document.querySelector('h2.pf-titlu') || {}).textContent || '') && "
                         "!document.querySelector('#fd-transforma')", timeout=20000)
    patron.captura()
    assert " ".join(pg.inner_text(".fd-antet .tip-micut").split()) == adresa, pg.inner_text(".fd-antet")
    assert [x.strip() for x in pg.locator(".fd-td-um").all_inner_texts()] == ["ora"], pg.locator(".fd-td-um").all_inner_texts()


def test_def_c64_confirmarea_transformarii_ramane_peste_detaliu(patron, firma_cv):
    """C64 (găsită de Code la C63, 19.10.2026). „Transformă în factură” -> pe ecran rămânea numai „Factura … a fost emisă.”: mesajul
    se scria în locul detaliului abia redesenat, fără drum spre factura nouă. Acum: detaliul proformei rămâne, cu „Factura <nr> a fost
    emisă.” în zona lui și „transformată în <nr>” ca drum spre ea (DS cap.27 v2.94).
    MUTAȚIE: mesajul repus pe `corp` (`arataMesaj(corp, …)`) -> detaliul dispare -> ROȘU."""
    pg, _adresa, r = _proforma_transformata(patron, firma_cv)
    pg.wait_for_function("(t) => ((document.querySelector('#fd-act-rez') || {}).textContent || '') === t",
                         arg="Factura %s a fost emisă." % r["numar"], timeout=20000)
    patron.captura()
    assert " ".join(pg.inner_text("#fd-vezi-transformata").split()) == "transformată în %s" % r["numar"], pg.inner_text(".fd-antet")
