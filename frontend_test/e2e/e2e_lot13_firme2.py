# -*- coding: utf-8 -*-
"""Lotul 13, comanda Costin 13.1 (verbatim în DECIZII „Comanda 13.1”), pachetul `firme2` — Casă, Bancă, Registru jurnal, Stocuri, Raport Z,
Inventar, Plan de conturi și cardurile firmei PFA, în `firme.js`.

  669 — soldurile pe parteneri preluate se sting din Bancă („Alege facturile” oferă documentul „Sold la …”); Casa: `e2e_lot13_migr.py`.
  624 — Casă și Bancă la forma 617/622: tabel, observațiile la clic, explicația o dată, cele puse deoparte grupate.
  607 — pe comisionul băncii „Alege facturile” nu e activ (stă inactiv, cu motivul — 675).
  602 / 563 — nota nouă din Registru jurnal: data de azi; după salvare rămâi pe nota salvată, cu confirmarea; nimic „nederivat”.
  610 — „Validează” pe nota fără document: inactiv, cu motivul; clicul nu dă niciun refuz (nici unul, nici două).
  605 — Raport Z: rândul numit „Raport Z nr … · casa …”, confirmarea sub buton; 618 — explicația notei cu data românească.
  612 / 606 — inventarul în fereastra lui: rândul lipsei sub articol, încadrarea cu diacritice.
  589 — Plan de conturi: sinteticul refuzat înainte de salvare; contul nelegal fără rulaj se șterge; „Șterge” inactiv spune de ce.
  577 — firma PFA: cardurile Declarații, Verificări, Registrul de evidență fiscală descriu ce are PFA-ul.
  628 — două deschideri consecutive ale Stocurilor arată aceeași listă.
  C177 — două ferestre Stocuri deschise deodată (Stocuri + „Mișcări, fișe…”) își desenează fiecare situația (răspunsurile ținute pe loc).
  673 / 675 / 676 — dispoziția nouă în fereastra ei, tipul din butoane alăturate, aceleași butoane pe fiecare operațiune.

Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI (`conftest.firma_noua`). Datele de pornire puse pe rutele
aplicației (aceeași sesiune — `e2e_bloc_a._api`) sunt numite pe linia lor. CUI-urile: sintetice, cu cifra de control verificată
(`conftest.cui_cu_control`) sau DANTE INTERNATIONAL SA, 14399840 (verificat în `e2e_lot12_firme1.py`).
TEMEI: N/A — reguli de interfață (DS cap.1 / cap.2a / cap.9 v2.102–v2.104; CLAUDE.md §9), cu excepțiile citate pe linie: 669 (OMFP 1802/2014
funcțiunea contului 411: „În creditul contului 411 "Clienți" se înregistrează: – sumele încasate de la clienți (512, 531)”), 589 (planul legal = nomenclatorul validatorului ANAF pe norma firmei).
Mutațiile: `frontend_test/e2e/mut_lot13_firme2.json`. Dovezile pe firmele de test: `frontend_test/dovada/dovezi_lot13_firme2.json`."""
import datetime as _dt
import re
import time

import pytest

from conftest import cui_cu_control, firma_noua, linie_nota, sql, zile_de_acum
from e2e_bloc_a import _api, _card, _ok, pregateste_firma

AZI = _dt.date.today()
_F = ".fereastra:last-of-type "
ALFA = (cui_cu_control(40130011), "CLIENT ALFA E2E FIRME2 SRL")


def _txt(pg, sel):
    return " ".join(pg.inner_text(sel).split())


def _butoane(pg, sel):
    return pg.eval_on_selector_all(sel, "bs => bs.map((b) => [b.textContent.trim(), b.getAttribute('aria-disabled') === 'true', b.title])")


def _tag():
    return int(time.time() * 1000) % 1000000


@pytest.fixture(scope="module")
def firma_mod():
    for f in firma_noua():
        yield f


@pytest.fixture()
def firma(patron, firma_mod):
    """Firma nouă a modulului, cu Date firmă, vectorul fiscal, seria și nomenclatorul (idempotent)."""
    pregateste_firma(patron, firma_mod)
    return firma_mod


@pytest.fixture()
def firma_noua_test():
    """O firmă NOUĂ numai pentru testul care își pune balanța (preluarea nu se suprapune cu datele altor teste)."""
    for f in firma_noua():
        yield f


def _incarca_extras(pg, csv_text, eticheta):
    with pg.expect_response(lambda r: "/banca/reconciliere/import" in r.url and r.request.method == "POST", timeout=60000):
        pg.set_input_files("#bk-fisier", {"name": "extras_firme2_%s_%d.csv" % (eticheta, time.time()), "mimeType": "text/csv",
                                          "buffer": csv_text.encode("utf-8")})
    pg.wait_for_function("() => { const t = document.querySelector('#bk-mesaj').innerText; return t && !t.includes('Se cite'); }", timeout=30000)


# ── 669 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _text_din_card(pg, card, sel):
    """[lotul 14, 687] Ce stă într-un card-rezumat al ferestrei (fereastra lui): deschide cardul, citește elementul, se întoarce la fereastra de dedesubt."""
    pg.click("[data-card='%s']" % card)
    pg.wait_for_selector(".fereastra:last-of-type " + sel, timeout=20000)
    text = pg.inner_text(".fereastra:last-of-type " + sel)
    pg.click(".fereastra:last-of-type .nav-sageata.nav-inapoi")
    pg.wait_for_selector("#bk-fisier", timeout=20000)
    return text


def test_def_669_banca_alege_facturile_ofera_si_stinge_soldul_preluat(patron, firma_noua_test):
    """669: „Soldurile preluate pe parteneri trebuie să apară ca sume de încasat/plătit, ca să poată fi stinse în prima lună. Aceeași
    verificare la plata către furnizor și la potrivirea extrasului bancar.” Pașii: balanța la 30.09.2026 cu 4111 = 1.500 pe Alfa (date de
    pornire, rutele „Solduri inițiale” și „Solduri parteneri”) -> Bancă -> extrasul cu încasarea de 1.500 lei fără CUI în descriere ->
    rândul liniei „Fără potrivire” -> „Alege facturile”: fereastra ei oferă „Sold la 30.09.2026 (sold preluat la migrare)”, Alfa, 1.500,00
    -> bifat -> „Contează selectate”: fereastra se închide, Banca spune nota creată; nota 5121 = 4111 1.500,00 stă pe documentul preluat.
    MUTAȚIA: soldul preluat scos din facturile deschise ale Băncii -> lista fără „Sold la” -> ROȘU."""
    f = firma_noua_test
    pregateste_firma(patron, f)
    from e2e_lot13_migr import _balanta_api, _parteneri_api
    _balanta_api(patron, f, (("4111", 1500, 0), ("1012", 0, 1500)))   # date de pornire: balanța de deschidere (ecranul ei: e2e_lot13_migr)
    _parteneri_api(patron, f, (("4111",) + ALFA + (1500, 0),))        # date de pornire: soldul lui Alfa (ecranul ei: e2e_lot13_migr)
    (doc,) = [r[0] for r in sql('SELECT id FROM "%s".facturi WHERE tip = \'preluata\'' % f["schema"])]
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    pg = patron.pg
    desc = "Incasare sold vechi E2E 669 %d" % _tag()
    _incarca_extras(pg, "Data;Detalii;Suma\n%s;%s;1500,00\n" % (AZI.strftime("%d.%m.%Y"), desc), "669")
    rand = pg.locator("#bk-lista tbody.tn-nota", has_text=desc).first
    rand.wait_for(timeout=20000)
    rand.locator("[data-alege]").click()
    pg.wait_for_selector(_F + "#bk-pk-tabel", timeout=20000)
    oferta = _txt(pg, _F + "#bk-pk-tabel")
    patron.captura("alege_facturile_sold_preluat")
    assert "Sold la 30.09.2026 (sold preluat la migrare)" in oferta and ALFA[1] in oferta and "1.500,00" in oferta, oferta
    pg.check(_F + "input[data-fid='%d']" % doc)
    pg.click(_F + "#bk-pk-ok")
    pg.wait_for_function("() => !document.querySelector('#bk-pk-ok') && (document.querySelector('#bk-mesaj') || {innerText: ''}).innerText.includes('creat')",
                         timeout=30000)
    patron.captura("contata")
    linii = sql('SELECT l.cont_debit, l.cont_credit, l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
                "WHERE i.factura_id = %%s" % (f["schema"], f["schema"]), (doc,))
    # OMFP 1802/2014, funcțiunea contului 411: „În creditul contului 411 "Clienți" se înregistrează: – sumele încasate de la clienți (512,
    # 531)” — creanța preluată în balanța de deschidere se stinge la încasare (5121 = 4111), nu se mai contează venitul
    assert [(d.split(".")[0], c.split(".")[0], v) for d, c, v in linii] == [("5121", "4111", "1500.00")], linii


# ── 607 + 624 (Bancă) ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_607_624_comisionul_bancii_si_liniile_puse_deoparte(patron, firma):
    """607: „La comisionul bancar apare și «Alege facturile».” 624: „bancă la forma din 617/622; observații la clic; respinsele grupate”.
    Pașii: Bancă -> extrasul cu un comision (−12,50) și o plată de chirie (−300,00) -> rândul comisionului: „Contează 627=5121” activ,
    „Alege facturile” inactiv, cu motivul „operațiune a băncii” la trecerea cu mouse-ul -> explicația „Operațiune a băncii (1)” o dată,
    deasupra tabelului -> clic pe rândul chiriei: detaliul (descrierea, „Ignoră”) -> „Ignoră”: linia trece în „Linii puse deoparte (1)”.
    MUTAȚIA: motivul 607 scos din butoanele liniei -> „Alege facturile” activ pe comision -> ROȘU."""
    f = firma
    patron.firma(f["nume"])
    _card(patron, "banca", "#bk-fisier")
    pg = patron.pg
    t = _tag()
    com, chirie = "Comision administrare cont E2E 607 %d" % t, "Plata chirie E2E 624 %d" % t
    zi = AZI.strftime("%d.%m.%Y")
    _incarca_extras(pg, "Data;Detalii;Suma\n%s;%s;-12,50\n%s;%s;-300,00\n" % (zi, com, zi, chirie), "607")
    rc = pg.locator("#bk-lista tbody.tn-nota", has_text=com).first
    rc.wait_for(timeout=20000)
    b = _butoane(pg, "#bk-lista tbody.tn-nota[data-linie-id='%s'] .tn-actiuni button" % rc.get_attribute("data-linie-id"))
    patron.captura("comisionul")
    assert b[0][:2] == ["Contează 627=5121", False], b
    assert b[1][:2] == ["Alege facturile", True] and "operațiune a băncii" in b[1][2], b
    expl = _text_din_card(pg, "explicatii", "#bk-explicatii")   # [lotul 14, 687] explicațiile semnelor stau în cardul lor
    assert expl.count("Operațiune a băncii (") == 1, expl
    rch = pg.locator("#bk-lista tbody.tn-nota", has_text=chirie).first
    rch.locator(".tn-deschide").click()
    assert "Descrierea din extras: %s" % chirie in _txt(pg, "#bk-lista tbody.tn-nota[data-linie-id='%s'] .tn-detaliu" % rch.get_attribute("data-linie-id"))
    rch.locator("[data-ign]").click()
    pg.wait_for_selector("#bk-deoparte tbody.tn-nota:has-text('%s')" % chirie, timeout=20000)
    patron.captura("pusa_deoparte")
    assert re.search(r"Linii puse deoparte \(\d+\)", _txt(pg, "#bk-deoparte")), _txt(pg, "#bk-deoparte")


# ── 624 + 673 + 675 + 676 (Casă) ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_624_673_675_676_casa_tabel_fereastra_si_butoanele(patron, firma):
    """624 (Casă la forma 617/622), 673 (dispoziția nouă în fereastra ei), 675 (aceleași butoane, inactive cu motivul), 676 (tipul =
    butoane alăturate). Pașii: Casă -> „+ Dispoziție nouă”: fereastră nouă, „Tip” cu cinci butoane, nimic ales -> „Ridicare de la bancă”,
    300 lei, DR-<tag> -> „Adaugă”: fereastra se închide, Casa spune „Dispoziția a fost salvată” -> rândul operațiunii în tabel: „Stornează”
    inactiv („Nota operațiunii nu e validată …”), „Șterge” activ -> clic pe rând: detaliul cu documentul, „PDF chitanță” inactiv („Operațiunea n-are
    chitanță emisă.”) și „Leagă de factură” inactiv („Numai încasarea de la client și plata furnizorului …”).
    MUTAȚIA: dispoziția nouă desenată în pagina Casei (fără fereastră) -> ROȘU."""
    f = firma
    patron.firma(f["nume"])
    _card(patron, "casa", "#c-toggle")
    pg = patron.pg
    doc = "DR-%d" % _tag()
    pg.click("#c-toggle")
    pg.wait_for_selector(_F + "#c-campuri", timeout=20000)
    assert pg.locator(_F + "#c-tabel, " + _F + "#c-gol").count() == 0, "dispoziția nouă e în pagina Casei, nu în fereastra ei"
    grup = _butoane(pg, _F + ".alegere-butoane:has(+ #c-cat) button")
    patron.captura("dispozitie_noua")
    assert [x[0] for x in grup] == ["Încasare client (5311=4111)", "Plată furnizor (401=5311)", "Ridicare de la bancă (5311=581)",
                                    "Depunere la bancă (581=5311)", "Avans spre decontare (542=5311)"], grup
    assert pg.locator(_F + ".alegere-butoane:has(+ #c-cat) .buton-activ").count() == 0                     # nimic ales în locul omului
    pg.click(_F + ".alegere-butoane:has(+ #c-cat) button[data-valoare='ridicare_banca']")
    pg.fill(_F + "#c-suma", "300")
    pg.fill(_F + "#c-doc", doc)
    pg.click(_F + "#c-adauga")
    pg.wait_for_function("() => document.body.innerText.includes('Dispoziția a fost salvată')", timeout=30000)
    pg.wait_for_selector("#c-tabel", timeout=20000)
    rand = pg.locator("#c-tabel tbody.tn-nota", has_text=doc).first
    oid = rand.get_attribute("data-op-id")
    b = _butoane(pg, "#c-tabel tbody[data-op-id='%s'] .tn-actiuni button" % oid)
    assert [x[:2] for x in b] == [["Stornează", True], ["Șterge", False]] and b[0][2].startswith("Nota operațiunii nu e validată"), b
    rand.locator(".tn-deschide").click()
    det = _butoane(pg, "#c-tabel tbody[data-op-id='%s'] .tn-detaliu button" % oid)
    patron.captura("randul_si_detaliul")
    assert [x[:2] for x in det] == [["PDF chitanță", True], ["Leagă de factură", True]], det
    assert det[0][2] == "Operațiunea n-are chitanță emisă." and det[1][2].startswith("Numai încasarea de la client"), det
    assert ("Document: %s" % doc) in _txt(pg, "#c-tabel tbody[data-op-id='%s'] .tn-detaliu" % oid)


# ── 602 + 563 + 610 (Registru jurnal) ────────────────────────────────────────────────────────────────────────────────────────────
def test_def_602_563_nota_noua_cu_data_de_azi_si_ramai_pe_ea_dupa_salvare(patron, firma):
    """602: „data notei noi vine 01.10, nu data zilei”; 563: „după salvare niciun mesaj, lista sare la început”. Pașii: Registru jurnal
    (luna curentă) -> „+ Notă nouă”: fereastra notei, „Data notei” = azi -> descrierea, documentul, 612 = 401 · 50 lei, partenerul ->
    „Salvează”: fereastra se închide; registrul arată confirmarea „Ai salvat nota din <azi> („…”)” sus și rândul notei evidențiat; nicăieri
    „nederivat”.
    MUTAȚIA: data notei noi înapoi pe 1 ale lunii -> ROȘU."""
    f = firma
    patron.firma(f["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg = patron.pg
    desc = "E2E 602 consumabile %d" % _tag()
    pg.click("#j-nota-noua")
    pg.wait_for_selector(_F + "#je-data", timeout=20000)
    # data notei noi o pune aplicația ACUM (ziua în care scrie contabilul), deci se compară cu ziua de la import SAU cea de acum
    assert pg.input_value(_F + "#je-data") in [d.isoformat() for d in zile_de_acum(AZI)], pg.input_value(_F + "#je-data")
    patron.captura("nota_noua")
    pg.fill(_F + "#je-desc", desc)
    pg.fill(_F + "#je-doc", "PV E2E 602")
    pg.fill(_F + ".je-deb", "612")
    pg.fill(_F + ".je-cre", "401")
    pg.fill(_F + ".je-sum", "50")
    pg.fill(_F + ".je-pnume", "PARTENER PROBA SRL")
    pg.click(_F + "#je-salveaza")
    pg.wait_for_function("() => ((document.querySelector('#j-mesaj') || {}).innerText || '').startsWith('Ai salvat')", timeout=30000)
    (nid,) = [r[0] for r in sql('SELECT id FROM "%s".inregistrari WHERE descriere = %%s' % f["schema"], (desc,))]
    pg.wait_for_selector("tbody.tn-nota.val-evidentiat[data-nota-id='%d']" % nid, timeout=20000)
    patron.captura("dupa_salvare")
    assert any(_txt(pg, "#j-mesaj").startswith("Ai salvat nota din %s („%s”)" % (d.strftime("%d.%m.%Y"), desc))
               for d in zile_de_acum(AZI)), _txt(pg, "#j-mesaj")
    assert "nederivat" not in patron.fereastra()


def test_def_610_valideaza_pe_nota_fara_document_inactiv_cu_motivul(patron, firma):
    """610: „La «Validează» pe o notă fără document, refuzul cu motiv apare de două ori”. Pașii: o notă fără document (date de pornire:
    ruta „Notă nouă”, fără referință) -> Registru jurnal: „Validează” e inactiv, cu pasul notei la trecerea cu mouse-ul -> clic pe el:
    niciun refuz pe ecran (nici unul, nici două) și nota rămâne ciornă; regula stă o dată, deasupra tabelului.
    MUTAȚIA: „Validează” activ pe nota fără document -> refuzul serverului apare -> ROȘU."""
    f = firma
    desc = "E2E 610 fără document %d" % _tag()
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % f["tenant_id"], {"descriere": desc, "data": AZI.isoformat(), "document_ref": "",
                                                                           "linii": [linie_nota("612", "401", "40.00")]}), "nota")["id"]
    patron.firma(f["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg = patron.pg
    b = _butoane(pg, "[data-val='%d']" % nid)[0]
    assert b[1] and b[2].startswith("Notă fără document justificativ. Scrie referința"), b
    pg.click("[data-val='%d']" % nid, force=True)
    pg.wait_for_timeout(800)
    patron.captura("clic_pe_validare")
    assert pg.locator(".msg-eroare, .caseta-eroare").count() == 0, patron.fereastra()[:1500]
    assert patron.fereastra().count("o notă nu se validează fără documentul din care provine") == 1
    assert sql('SELECT status FROM "%s".inregistrari WHERE id = %%s' % f["schema"], (nid,)) == [("ciorna",)]


# ── 605 + 618 (Raport Z) ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def _z_generat(patron, f, casa):
    """Raport Z -> data de azi, casa dată, Z nr. unic, total 21% 121,00, numerar 121,00, card 0, 3 bonuri -> „Generează notă”; așteaptă
    confirmarea notei (conturile ei). Întoarce numărul Z-ului."""
    patron.firma(f["nume"])
    _card(patron, "raportz", "#z-salveaza")
    pg = patron.pg
    nr = "%04d" % (_tag() % 10000)
    for sel, v in (("#z-data", AZI.isoformat()), ("#z-nui", casa), ("#z-nr", nr), ("#z-21", "121"), ("#z-num", "121"),
                   ("#z-card", "0"), ("#z-bonuri", "3")):
        pg.fill(sel, v)
    pg.click("#z-salveaza")
    pg.wait_for_function("() => (document.querySelector('#z-rezultat') || {innerText: ''}).innerText.includes('5311')", timeout=30000)
    return nr


def test_def_605_raport_z_numele_documentului_si_confirmarea_sub_buton(patron, firma):
    """605: „Textul «raportul Z Raport Z nr»; [...] mesajul de confirmare sus, departe de buton (clasa 45).” Pașii: un raport Z nou ->
    „Generează notă”: confirmarea stă SUB buton (`#z-rezultat`); lista Z-urilor lunii numește rândul „Raport Z nr <nr> · casa 8000000605”, nu
    cheia „Z-8000000605-<nr>”, și nicăieri „raportul Z Raport Z”.
    MUTAȚIA: numele rândului înapoi pe cheia notei (`numeZ`) -> ROȘU."""
    f = firma
    nr = _z_generat(patron, f, "8000000605")
    pg = patron.pg
    patron.captura("nota_generata")
    assert pg.evaluate("() => !!(document.querySelector('#z-salveaza').compareDocumentPosition(document.querySelector('#z-rezultat'))"
                       " & Node.DOCUMENT_POSITION_FOLLOWING)"), "confirmarea notei nu stă sub buton"
    pg.wait_for_selector("#z-descarcare .pf-frand", timeout=20000)
    lista = _txt(pg, "#z-descarcare")
    assert "Raport Z nr %s · casa 8000000605" % nr in lista and "Z-8000000605" not in lista, lista
    assert "raportul Z Raport Z" not in _txt(pg, ".fereastra:last-of-type")


def test_def_618_explicatia_notei_z_are_data_romaneasca(patron, firma):
    """618: „Raport Z | Titlul notei cu data ISO («Raport Z 2026-10-20»)”. Pașii: un raport Z nou -> „Generează notă” -> Registru jurnal,
    căutarea „raportul Z nr <nr>”: explicația notei e „Vânzări din raportul Z nr <nr> din <azi>, casa 8000000618” (data românească), iar
    în baza de date nota n-are nicio dată ISO în explicație. (Datele existente: `core/migrare_explicatie_raport_z.py`, dovada `618_f1_vechi_…`.)
    MUTAȚIA: explicația notei înapoi cu data ISO (`jurnal_api.explicatie_raport_z`) -> ROȘU."""
    f = firma
    nr = _z_generat(patron, f, "8000000618")
    pg = patron.pg
    (desc,) = [r[0] for r in sql('SELECT descriere FROM "%s".inregistrari WHERE numar = %%s' % f["schema"], ("Z-8000000618-%s" % nr,))]
    asteptat = "Vânzări din raportul Z nr %s din %s, casa 8000000618" % (nr, AZI.strftime("%d.%m.%Y"))
    assert desc == asteptat, desc
    assert not re.search(r"\d{4}-\d{2}-\d{2}", desc), desc
    patron.firma(f["nume"])
    _card(patron, "jurnal", "#j-nota-noua")
    pg.fill("#jn-cauta", "raportul Z nr %s" % nr)
    pg.wait_for_timeout(500)
    patron.captura("explicatia_notei_z")
    assert asteptat in _txt(pg, ".fereastra:last-of-type"), _txt(pg, ".fereastra:last-of-type")[:600]
    assert "Raport Z %s" % AZI.isoformat() not in _txt(pg, ".fereastra:last-of-type")   # AZI-dat-de-test: data Z-ului o scrie testul (`_z_generat`)

# ── 612 + 606 (Inventar) ─────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_612_606_inventarul_in_fereastra_lui_cu_randul_lipsei_sub_articol(patron, firma):
    """612: „Rândul cu lipsă e înghesuit”; 606: „«neimputabila» fără diacritice”. Pașii: un articol cu denumire lungă în stoc (5 buc,
    date de pornire: ruta „Intrare”) -> Stocuri -> „Mișcări, fișe…” -> „Inventar (stoc faptic)”: fereastra inventarului, tabel -> faptic 3:
    rândul lipsei apare SUB articol, cu încadrarea din trei butoane („lipsă imputabilă”, „lipsă neimputabilă”, „lipsă justificată …”), iar
    denumirea stă pe cel mult două rânduri -> „lipsă neimputabilă”, cota 21 -> „Salvează inventarul”: fereastra se închide, Stocuri arată notele
    diferențelor și „Lipsa neimputabilă …” (cu diacritice).
    MUTAȚIA: rândul lipsei pus pe rândul articolului -> ROȘU."""
    f = firma
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"metoda_stoc": "cantitativ_valoric"}), "metoda de stoc")
    den = "Marfa cu denumire lungă pentru inventarul E2E 612, ambalaj de carton %d" % _tag()
    aid = _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % f["tenant_id"], {"denumire": den, "um": "buc", "data": AZI.isoformat(),
                                                                                "cantitate": 5, "pret_unitar": 10, "document": "NIR E2E 612"}),
              "intrare")["articol_id"]   # date de pornire: articolul în stoc
    patron.firma(f["nume"])
    _card(patron, "stocuri", "#cv-toggle")
    pg = patron.pg
    pg.click("#cv-toggle")
    pg.wait_for_selector("#cv-inv", timeout=20000)
    pg.click("#cv-inv")
    pg.wait_for_selector(_F + "#cvi-tabel", timeout=20000)
    pg.fill(_F + "#cvi-a%d-faptic" % aid, "3")
    pg.wait_for_selector(_F + "#cvi-a%d-lipsa-zona" % aid, state="visible", timeout=5000)
    g = pg.evaluate("""(id) => { const n = document.querySelector('#cvi-a' + id + '-rand .cvi-denumire'), z = document.querySelector('#cvi-a' + id + '-lipsa-zona');
      const lh = parseFloat(getComputedStyle(n).lineHeight) || parseFloat(getComputedStyle(n).fontSize) * 1.3;
      return {randuri: Math.round(n.getBoundingClientRect().height / lh), sub: z.getBoundingClientRect().top >= n.getBoundingClientRect().bottom - 1,
              butoane: [...z.querySelectorAll('.alegere-butoane button')].map((b) => b.textContent.trim())}; }""", aid)
    patron.captura("randul_lipsei")
    assert g["sub"] and g["randuri"] <= 2, g
    assert g["butoane"] == ["lipsă imputabilă", "lipsă neimputabilă", "lipsă justificată (distrusă, pierdută, furată — dovedit)"], g
    pg.click(_F + "#cvi-a%d-lipsa-zona .alegere-butoane button[data-valoare='neimputabila']" % aid)
    # articolul intrat pe ruta „Intrare” n-are cota în nomenclator: contabilul scrie cota cu care s-a dedus TVA-ul (ajustarea 635 = 4427;
    # fără ea, refuzul stă lângă câmp — `stocuri_cv_api`, HG 1/2016 titlul VII pct.78 alin.(6) lit.a)
    pg.fill(_F + "#cvi-a%d-cota" % aid, "21")
    pg.click(_F + "#cvi-salveaza")
    pg.wait_for_function("() => document.body.innerText.includes('Inventarul din')", timeout=30000)
    patron.captura("dupa_inventar")
    t = patron.fereastra()
    assert "Lipsa neimputabilă" in t and "neimputabila" not in t, t[-1500:]


# ── 589 (Plan de conturi) ────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_589_sinteticul_refuzat_inainte_de_salvare_si_contul_nelegal_se_sterge(patron, firma):
    """589: „Contul sintetic 731 (în afara planului legal) a fost adăugat manual; avertismentul apare după salvare; contul nu se poate
    șterge. Adăugarea manuală doar pentru analitice sub sintetic legal.” Pașii: Plan de conturi -> simbolul „731”: avertismentul apare cât
    scrii, înainte de „Adaugă” („Contul 731 e sintetic …”) -> „Adaugă”: refuzat lângă câmp, nimic scris -> serverul refuză și el (cererea
    directă) -> un 731 „Test cont nelegal” rămas din înainte (date de pornire: scris direct, cum l-a lăsat retestul pe F6) -> rândul lui are
    „Șterge” activ -> „Șterge” -> contul dispare din plan; 4111 (folosit) are „Șterge” inactiv, cu motivul.
    MUTAȚIA: refuzul sinteticului scos din ecran -> avertismentul nu apare înainte de salvare -> ROȘU."""
    f = firma
    s = f["schema"]
    sql('DELETE FROM "%s".plan_conturi WHERE simbol = \'731\'' % s)
    patron.firma(f["nume"])
    _card(patron, "planconturi", "#pcf-adauga")
    pg = patron.pg
    pg.fill(_F + "#pcf-simbol", "731")
    pg.wait_for_selector(_F + "#pcf-avert", timeout=5000)
    assert _txt(pg, _F + "#pcf-avert").startswith("Contul 731 e sintetic"), _txt(pg, _F + "#pcf-avert")
    pg.fill(_F + "#pcf-denumire", "Test cont nelegal")
    pg.click(_F + "#pcf-adauga")
    pg.wait_for_selector('.msg-eroare[data-camp="pcf-simbol"]', timeout=10000)
    patron.captura("refuzat_inainte")
    assert sql('SELECT count(*) FROM "%s".plan_conturi WHERE simbol = \'731\'' % s) == [(0,)]
    r = _api(patron, "POST", "/tenants/%d/plan-conturi" % f["tenant_id"], {"simbol": "731", "denumire": "Test cont nelegal"})
    assert r["status"] >= 400 and "e sintetic" in str(r["json"]), r
    sql('INSERT INTO "%s".plan_conturi (simbol, denumire, tip) VALUES (\'731\', \'Test cont nelegal\', \'Nedeterminat\')' % s)   # date-de-pornire: contul sintetic 731 nelegal, pe care aplicația îl refuză acum — trebuie să existe deja ca să probăm ștergerea lui
    patron.firma(f["nume"])
    _card(patron, "planconturi", "#pcf-adauga")
    pg.fill(_F + "#pcf-cauta", "731")
    pg.wait_for_selector(_F + "#pcf-lista [data-simbol='731'] [data-sterge]", timeout=10000)
    assert _butoane(pg, _F + "#pcf-lista [data-simbol='731'] [data-sterge]")[0][:2] == ["Șterge", False]
    pg.click(_F + "#pcf-lista [data-simbol='731'] [data-sterge]")
    pg.click("#ca-ok")
    pg.wait_for_selector(_F + "#pcf-lista [data-simbol='731']", state="detached", timeout=20000)
    assert sql('SELECT count(*) FROM "%s".plan_conturi WHERE simbol = \'731\'' % s) == [(0,)]
    pg.fill(_F + "#pcf-cauta", "4111")
    pg.wait_for_selector(_F + "#pcf-lista [data-simbol='4111'] [data-sterge]", timeout=10000)
    b = _butoane(pg, _F + "#pcf-lista [data-simbol='4111'] [data-sterge]")[0]
    patron.captura("sters")
    assert b[1] and b[2].startswith("Contul nu se șterge:"), b


# ── 577 (PFA) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture(scope="module")
def firma_pfa():
    for f in firma_noua("pfa"):
        yield f


def test_def_577_cardurile_firmei_pfa_descriu_ce_are_pfa(patron, firma_pfa):
    """577: „F4 PFA: cardurile au descrieri de SRL — Declarații «D101», Verificări «Echilibru», Registrul de evidență fiscală «Profit · art.
    19».” Pașii: firma PFA -> fereastra ei: „Declarații — D212 (declarația unică), D300, D112 și restul”, „Verificări — Trezorerie, TVA,
    documente pozate”, „Registrul de evidență fiscală — Venituri și cheltuieli · persoane fizice · art. 68”; în registru, varianta aleasă e
    „Persoane fizice · art. 68”.
    MUTAȚIA: descrierile PFA scoase -> cardurile spun din nou „D101”, „Echilibru”, „Profit · art. 19” -> ROȘU."""
    patron.firma(firma_pfa["nume"])
    pg = patron.pg
    pg.wait_for_selector("#fa-declaratii", timeout=20000)
    d = {k: _txt(pg, "#fa-%s .firme-optiune-desc" % k) for k in ("declaratii", "verificari", "regfiscal")}
    patron.captura("cardurile_pfa")
    assert d == {"declaratii": "D212 (declarația unică), D300, D112 și restul", "verificari": "Trezorerie, TVA, documente pozate",
                 "regfiscal": "Venituri și cheltuieli · persoane fizice · art. 68"}, d
    pg.click("#fa-regfiscal")
    pg.wait_for_selector(_F + "#rf-var", state="attached", timeout=20000)
    assert pg.eval_on_selector(_F + "#rf-var", "s => s.value") == "venituri_pf"


# ── 628 (Stocuri) ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_628_doua_deschideri_consecutive_ale_stocurilor_arata_aceeasi_lista(patron, firma):
    """628: „Stocuri F1: două deschideri consecutive arată liste diferite (4, apoi 6 rânduri)”. Pașii: șase articole în stoc (date de
    pornire: ruta „Intrare”) -> Stocuri: situația stocului -> „←” -> Stocuri din nou, imediat -> aceeași listă, cu toate articolele firmei.
    MUTAȚIA: contorul cererilor situației stocului comun tuturor ferestrelor -> a doua deschidere rămâne pe „Se încarcă” -> ROȘU (cu
    răspunsul primei cereri întârziat)."""
    f = firma
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"metoda_stoc": "cantitativ_valoric"}), "metoda de stoc")
    t = _tag()
    for i in range(6):
        _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % f["tenant_id"], {"denumire": "Articol E2E 628 %d-%d" % (t, i), "um": "buc",
                                                                              "data": AZI.isoformat(), "cantitate": 1 + i, "pret_unitar": 5,
                                                                              "document": "NIR E2E 628"}), "intrare")   # date de pornire
    total = len(_ok(_api(patron, "GET", "/tenants/%d/stocuri/articole" % f["tenant_id"]), "articole")["articole"])
    patron.firma(f["nume"])
    pg = patron.pg

    def _lista():
        _card(patron, "stocuri", "#s-situatie-tabel")
        return pg.eval_on_selector_all(_F + "#s-situatie-tabel tbody tr", "rr => rr.map((r) => r.cells[0].innerText.trim())")
    prima = _lista()
    pg.click(".nav-sageata.nav-inapoi")
    a_doua = _lista()
    patron.captura("a_doua_deschidere")
    assert prima == a_doua and len(a_doua) == total, (prima, a_doua, total)
    assert len([x for x in a_doua if x.startswith("Articol E2E 628 %d-" % t)]) == 6



def test_def_c177_doua_ferestre_stocuri_nu_isi_anuleaza_situatia(patron, firma):
    """C177: „Stocuri: contorul cererilor situației stocului era comun tuturor ferestrelor — o fereastră o lăsa pe alta pe «Se încarcă
    situația stocului…».” Din clicuri: Stocuri (cererea situației ținută pe loc, `page.route`) -> „Mișcări, fișe de magazie, coduri, nivel
    minim” (fereastra ei, peste Stocuri, cere și ea articolele) -> răspunsurile eliberate, întâi al ferestrei de sus, apoi al Stocurilor ->
    AMBELE ferestre își desenează lista: mișcările au formularele, iar Stocuri (dedesubt) situația, nu „Se încarcă situația stocului…”.
    Cursa se probează numai cu răspunsurile ținute pe loc (ca C102 în `e2e_lot11_s9.py`); fără ele, cererea Stocurilor se termină înaintea
    clicului. Date de pornire: metoda cantitativ-valorică și un articol în stoc (ruta „Intrare”).
    MUTAȚIA: contorul situației comun tuturor ferestrelor (`ultimaCerere(document.body)`) -> Stocuri rămâne pe „Se încarcă” -> ROȘU."""
    f = firma
    _ok(_api(patron, "POST", "/tenants/%d/firma-profil/date" % f["tenant_id"], {"metoda_stoc": "cantitativ_valoric"}), "metoda de stoc")
    t = _tag()
    _ok(_api(patron, "POST", "/tenants/%d/stocuri/intrare" % f["tenant_id"], {"denumire": "Articol E2E C177 %d" % t, "um": "buc",
                                                                          "data": AZI.isoformat(), "cantitate": 3, "pret_unitar": 5,
                                                                          "document": "NIR E2E C177"}), "intrare")   # date de pornire
    patron.firma(f["nume"])
    pg = patron.pg
    vazute, tinute = [0], []

    def _tine(route):
        # prima cerere a articolelor e a formularului NIR (ecranul o așteaptă ca să se deseneze): trece; situațiile se țin pe loc
        vazute[0] += 1
        if vazute[0] == 1:
            route.continue_()
        else:
            tinute.append(route)
    pg.route("**/stocuri/articole*", _tine)

    def asteapta_cereri(n):
        for _ in range(150):
            if len(tinute) >= n:
                return
            pg.wait_for_timeout(100)
        raise AssertionError("ecranul n-a cerut situația stocului (%d cereri din %d)" % (len(tinute), n))
    try:
        _card(patron, "stocuri", "#cv-toggle")
        asteapta_cereri(1)
        assert "Se încarcă situația stocului" in _txt(pg, _F + "#s-situatie")
        pg.click(_F + "#cv-toggle")                                   # fereastra mișcărilor, peste Stocuri
        asteapta_cereri(2)
        for i in (1, 0):                                              # întâi răspunsul ferestrei de sus, apoi al Stocurilor
            with pg.expect_response(lambda r: "/stocuri/articole" in r.url):
                tinute[i].continue_()
            pg.wait_for_timeout(300)
    finally:
        pg.unroute("**/stocuri/articole*")
    pg.wait_for_selector(_F + "#cv-zona #cv-art", state="attached", timeout=15000)
    patron.captura("doua_ferestre_stocuri")
    # [lotul 13, 673] o singură fereastră e în pagină: Stocurile (dedesubt) se văd prin „înapoi”, cu corpul păstrat — aici se probează că răspunsul
    # lor, sosit cât stăteau sub fereastra mișcărilor, a ajuns în corpul păstrat
    pg.click(_F + ".fereastra-antet .nav-inapoi")
    pg.wait_for_selector(_F + "#s-situatie", timeout=15000)
    jos = _F + "#s-situatie"
    # [lotul 14, 687] Stocurile revenite se redesenează cu un pas după „înapoi” (fereastra păstrată își citește situația): se așteaptă tabelul,
    # iar dacă răspunsul ținut n-a ajuns niciodată în corp, așteptarea expiră și testul pică pe „Se încarcă situația stocului…”
    try:
        pg.wait_for_selector(jos + " #s-situatie-tabel", state="attached", timeout=15000)
    except Exception:  # noqa: BLE001 — mesajul de mai jos spune ce vede contabilul
        pass
    assert pg.locator(jos + " #s-situatie-tabel").count() == 1, _txt(pg, jos)
    assert "Se încarcă situația stocului" not in _txt(pg, jos)
    assert "Articol E2E C177 %d" % t in _txt(pg, jos)

# ── generatorul extrasului dovezii 669 / 607 pe F7 (copia firmelor de test, `frontend_test/dovada/dovezi_lot13_firme2.json`) ─────────
def extras_dovada_f7(zi):
    """O încasare de 1.500 lei fără CUI în descriere (o stinge soldul preluat al lui Client Alfa Test SRL, „Alege facturile”) și un comision
    al băncii de 5 lei — extrasul de probă al dovezii, încărcat pe ecranul Bancă al copiei F7."""
    d = _dt.date.fromisoformat(zi).strftime("%d.%m.%Y")
    return ("Data;Detalii;Suma\n%s;Proba 669 Incasare sold vechi Client Alfa;1500,00\n%s;Proba 607 Comision administrare cont;-5,00\n"
            % (d, d)).encode("utf-8")
