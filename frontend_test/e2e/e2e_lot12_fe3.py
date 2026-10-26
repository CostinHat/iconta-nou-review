# -*- coding: utf-8 -*-
"""Lotul 12, pachetul fe3 (comanda Costin 12.3): testele de capăt la capăt pentru C109, C164 și cota / categoria pe linia șablonului recurent.

Deciziile, verbatim din comanda 12.3:
  · pct.1 — „C109: refuzul cronului ajunge la contabil prin notificare (clopoțel și email); pe șablon se vede și starea ultimei emiteri.”
  · pct.4 — „C164: pe ecranele scunde, antetul detaliului facturii se strânge pe un rând (număr, client, total, stare SPV); acțiunea
    principală rămâne fixă jos (clasa 285).”
  · pct.9 — „Da: cota și categoria pe linia șablonului recurent, ca la factură.” (rămânea deschisă la C160: „[DECIZIE] cota și categoria pe
    linia șablonului”)

Pașii pe aplicația din index, pe baza de TEST, pe firme NOI de test (`firma_noua`), pregătite pe drumul ecranelor (`pregateste_firma`:
Date firmă + Vector fiscal + numerotarea). Factura lunară o emite tura cronului (`facturi_recurente.emite_scadente`, ce rulează cronul
zilnic). Emailul notificării îl trimite cutia de ieșire a aplicației (bucla `main._bucla_livrare_notificari`, la 30 s): testul așteaptă
rândul jurnalului livrării (`public.notificari_jurnal`, canalul `email`). Nicio scriere SQL: `sql` doar citește.
Temei: CF art.310 alin.(10) lit.b (neplătitorul „nu are voie să menționeze taxa pe factură”: refuzul real al cronului folosit de C109);
CF art.278 alin.(2) (locul prestării la beneficiarul persoană impozabilă: linia 0% „Prestare cu locul în afara României”)."""
import datetime as _dt

import pytest

from conftest import firma_noua, perioada_incheiata, sql

CUI_DANTE = "14399840"            # DANTE INTERNATIONAL SA — cifra de control verificată (CLAUDE.md)
COD_CLIENT_IC = "DE811907980"     # clientul din DE al probelor C78 / C110 / C154 / C160
LUNA = perioada_incheiata("lunar")
ZI = LUNA.inceput.replace(day=10)
_F = ".fereastra:last-of-type "


@pytest.fixture()
def firma_fe3():
    for f in firma_noua():
        yield f


def _sablon(patron, f, cui, nume, denumire, cota, categorie=None, tara=None):
    """Facturi -> Facturi recurente -> „+ Șablon nou” -> beneficiarul, o linie (denumire, 1 × 500, cota aleasă din listă, categoria la 0%),
    ziua 5 -> „Salvează șablonul”."""
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-recurente")
    pg.click("#fac-recurente")
    pg.wait_for_selector("#fr-add", timeout=20000)
    pg.click("#fr-add")
    pg.wait_for_selector("#fr-l0-descriere", timeout=20000)
    pg.fill("#fr-cui", cui)
    pg.dispatch_event("#fr-cui", "change")
    if tara:
        pg.wait_for_function("(t) => document.querySelector('#fr-tara').value === t", arg=tara, timeout=10000)
    pg.fill("#fr-nume", nume)
    pg.fill("#fr-l0-descriere", denumire)
    pg.dispatch_event("#fr-l0-descriere", "input")
    pg.wait_for_timeout(900)                                   # propunerea din nomenclator (cerută după 400 ms) a sosit
    pg.select_option("#fr-l0-cota", str(cota))                 # 12.3 pct.9: cota se ALEGE pe linie, ca la „Emite factură”
    if categorie:
        pg.wait_for_selector("#fr-l0-categorie", state="visible", timeout=5000)
        pg.select_option("#fr-l0-categorie", categorie)
    pg.fill("#fr-l0-cantitate", "1")
    pg.dispatch_event("#fr-l0-cantitate", "input")
    pg.fill("#fr-l0-pret_unitar", "500")
    pg.dispatch_event("#fr-l0-pret_unitar", "input")
    pg.fill("#fr-zi", "5")
    # [lotul 13, 680] întrebările emiterii de pe șablon, alese explicit (scadența, perioada, modul, SPV)
    pg.fill("#fr-scadenta", "15")
    pg.fill("#fr-inceput", "2026-01-01")
    pg.click("#fr-pana button[data-val='oprire']")
    pg.click("#fr-mod button[data-val='automata']")
    pg.click("#fr-spv button[data-val='false']")
    patron.captura("sablon")
    pg.click("#fr-salveaza")
    pg.wait_for_selector("#fr-add", timeout=30000)               # salvat: înapoi la lista șabloanelor
    rand = pg.locator(".pf-frand", has_text=nume)
    rand.wait_for(timeout=10000)
    return rand


def test_def_c109_refuzul_cronului_ajunge_in_clopotel_pe_email_si_pe_sablon(patron, firma_fe3):
    """C109. Pașii: firmă plătitoare -> Facturi recurente -> „+ Șablon nou” (DANTE, „Servicii de consultanta IT E2E C109”, cota 21%,
    ziua 5) -> salvat -> Vector fiscal: firma devine neplătitoare -> tura cronului: factura lunii refuzată (CF art.310 alin.(10) lit.b) ->
    clopoțelul contabilului-șef: „<firma>: factura recurentă pentru DANTE INTERNATIONAL SA nu s-a emis (…). Motivul: Firma nu e plătitoare
    de TVA…” -> notificarea pleacă pe email (jurnalul livrării, canalul email; bifată din oficiu) -> Facturi recurente: rândul șablonului
    spune „Emiterea automată refuzată la <zi>:” cu motivul. Înainte: refuzul rămânea în jurnalul jobului, nimeni nu afla.
    MUTAȚIILE (`mut_lot12_fe3.json`): consemnarea refuzului scoasă din ramura excepției -> nimic în clopoțel -> ROȘU; tipul fără
    `"implicit": True` -> emailul nu pleacă (jurnalul: „nebifat”) -> ROȘU; rândul refuzului scos din lista șabloanelor -> ROȘU."""
    from conftest import _db
    from core import facturi_recurente, notificari
    from e2e_bloc_a import pregateste_firma
    f = firma_fe3
    s = f["schema"]
    pregateste_firma(patron, f)
    _sablon(patron, f, CUI_DANTE, "DANTE INTERNATIONAL SA", "Servicii de consultanta IT E2E C109", 21)
    assert sql('SELECT ultimul_refuz FROM "%s".facturi_recurente' % s) == [(None,)]
    pregateste_firma(patron, f, platitor=False)                     # Date firmă + Vector fiscal: neplătitor de TVA
    _db()
    emise = facturi_recurente.emite_scadente(s, ZI)                   # tura cronului zilnic, în ziua emiterii
    assert [("Firma nu e plătitoare de TVA" in (e.get("eroare") or "")) for e in emise if "sablon" in e] == [True], emise
    assert sql('SELECT count(*) FROM "%s".facturi' % s)[0][0] == 0
    zi = ZI.strftime("%d.%m.%Y")
    # clopoțelul
    pg = patron.pg
    patron.acasa()
    pg.click("#nav-clopot")
    pg.wait_for_selector(".clopot-item, .clopot-gol", timeout=20000)
    it = pg.locator(".clopot-item", has_text=f["nume"]).filter(has_text="factura recurentă").first
    it.wait_for(timeout=20000)
    txt = " ".join(it.inner_text().split())
    patron.captura("clopot")
    assert ("factura recurentă pentru DANTE INTERNATIONAL SA nu s-a emis (%s)" % zi) in txt and "Firma nu e plătitoare de TVA" in txt, txt
    # emailul: cutia de ieșire a aplicației, pe canalul contabilului (implicit email), bifat din oficiu
    nid = sql("SELECT n.id FROM public.notificari n JOIN public.users u ON u.id = n.user_id WHERE u.email = 'patron@prisma-cont.test' "
              "AND n.tip = %s AND n.text LIKE %s ORDER BY n.id DESC LIMIT 1", (facturi_recurente.TIP_REFUZ, f["nume"] + ":%"))[0][0]
    jurnal = []
    for _ in range(45):
        jurnal = sql("SELECT canal, stare, detaliu FROM public.notificari_jurnal WHERE notificare_id = %s", (nid,))
        if jurnal:
            break
        pg.wait_for_timeout(2000)
    assert jurnal and jurnal[0][0] == "email" and jurnal[0][2] != notificari.DETALIU_NEBIFAT, jurnal
    # pe șablon: starea ultimei emiteri
    from e2e_bloc_a import _card
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-recurente")
    pg.click("#fac-recurente")
    rand = pg.locator(".pf-frand", has_text="DANTE INTERNATIONAL SA")
    rand.wait_for(timeout=20000)
    t = " ".join(rand.inner_text().split())
    patron.captura("sablon_refuzat")
    assert ("Emiterea automată refuzată la %s:" % zi) in t and "Firma nu e plătitoare de TVA" in t and "nicio factură emisă încă" in t, t


def test_def_c160_sablonul_platitorului_alege_cota_si_categoria_pe_linie(patron, firma_fe3):
    """C160 (rămasul: „[DECIZIE] cota și categoria pe linia șablonului” — 12.3 pct.9). Pașii: firmă PLĂTITOARE -> Facturi recurente ->
    „+ Șablon nou” -> CUI DE811907980: „Țara beneficiarului” devine DE -> „Servicii de consultanta IT E2E C160P”, cota 0% din listă ->
    apare „Categoria de TVA a liniei” -> „Prestare de servicii cu locul în afara României” (CF art.278 alin.(2)) -> 1 × 500, ziua 5 ->
    „Salvează șablonul”: salvat (înainte refuzat: „în șablon nu se alege categoria de TVA a liniei”) -> tura cronului emite factura lunară
    -> Istoric facturi -> factura: linia „0%” cu categoria ei; în bază, linia are categoria „serviciu_extern” și factura țara DE.
    MUTAȚIA (`mut_lot12_fe3.json`): categoria netrimisă de ecran -> salvarea refuzată lângă categoria liniei -> ROȘU."""
    from conftest import _db
    from core import facturi_recurente
    from e2e_bloc_a import pregateste_firma
    f = firma_fe3
    s = f["schema"]
    pregateste_firma(patron, f)
    rand = _sablon(patron, f, COD_CLIENT_IC, "KUNDE E2E GMBH", "Servicii de consultanta IT E2E C160P", 0, "serviciu_extern", tara="DE")
    assert "client din DE" in " ".join(rand.inner_text().split())
    patron.captura("lista_sabloane")
    assert sql("""SELECT tert_tara, linii->0->>'cota_tva', linii->0->>'categorie_tva' FROM "%s".facturi_recurente""" % s) == [
        ("DE", "0", "serviciu_extern")]
    _db()
    emise = facturi_recurente.emite_scadente(s, ZI)
    assert [bool(e.get("factura")) for e in emise if "sablon" in e] == [True], emise
    fid, tara = sql('SELECT id, tert_tara FROM "%s".facturi' % s)[0]
    assert tara == "DE"
    assert sql('SELECT cota_tva::int, categorie_tva FROM "%s".factura_linii WHERE factura_id = %%s' % s, (fid,)) == [(0, "serviciu_extern")]
    # Istoric facturi -> factura emisă de cron (luna încheiată: din luna curentă, „← luna”) -> linia cu cota 0% și categoria ei
    from core import categorii_tva
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(f["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    azi = _dt.date.today()
    for _ in range((azi.year - ZI.year) * 12 + azi.month - ZI.month):
        pg.wait_for_selector("#fac-prev", timeout=20000)
        pg.click("#fac-prev")
    pg.wait_for_selector(".fac-frand-btn[data-id='%s']" % fid, timeout=25000)
    pg.click(".fac-frand-btn[data-id='%s']" % fid)
    pg.wait_for_selector("#fd-pdf", timeout=25000)
    cel = " ".join(pg.inner_text(_F + ".fd-tabel tbody tr td:nth-child(5)").split())
    patron.captura("factura_lunara")
    assert cel.startswith("0%") and categorii_tva.CATEGORII["serviciu_extern"]["eticheta"] in cel, cel


def _factura_emisa(patron, f):
    from e2e_bloc_a import emite_api, pregateste_firma
    pregateste_firma(patron, f)
    r = emite_api(patron, f)
    return r.get("id") or r.get("factura_id")


_ASEZARE = """() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), sc = c.querySelector('#fd-antet-scurt');
  const rc = c.getBoundingClientRect(), jos = Math.min(innerHeight, rc.bottom);
  const copii = [...sc.children].filter((e) => e.getClientRects().length), sus = copii.map((e) => e.getBoundingClientRect().top);
  const butoane = [...c.querySelectorAll('button.buton-secundar[id^=fd-]')];
  return {vizibil: !sc.hidden && sc.getClientRects().length > 0, text: sc.innerText.replace(/\\s+/g, ' ').trim(),
          un_rand: copii.length > 0 && Math.max(...sus) - Math.min(...sus) < 8 && sc.scrollHeight <= sc.clientHeight + 1,
          butoane: butoane.map((b) => b.id), in_bara: butoane.filter((b) => b.closest('.bara-fixa')).map((b) => b.id),
          in_vedere: butoane.filter((b) => { const r = b.getBoundingClientRect(); return r.top >= rc.top - 1 && r.bottom <= jos + 1; }).map((b) => b.id)}; }"""


def test_def_c164_pe_ecranul_scund_antetul_facturii_e_un_rand_iar_actiunile_raman_jos(patron, firma_fe3):
    """C164. Pașii: o factură emisă -> fereastra browserului de 1280 × 600 -> Facturi -> „Istoric facturi” -> factura: sus UN rând cu
    numărul, clientul, totalul și starea SPV; „PDF factură”, „Trimite pe email”, „Stornează”, „Emite chitanță”, „Export SAGA”, „Trimite în
    SPV” în bara lipită jos, în vedere (și la capătul paginii) -> „Trimite pe email” cu adresa ștearsă -> „Trimite”: „Introdu o adresă
    validă.” în vedere, lângă buton. La fel pe telefon (390 × 844). Înainte: antetul cu toate acțiunile stătea lipit sus, mai înalt decât
    fereastra, iar rezultatul unei acțiuni scris în el nu mai putea intra în vedere.
    MUTAȚIA (`mut_lot12_fe3.json`): media query-ul ecranului scund scos din stil.css -> antetul întreg rămâne sus -> ROȘU."""
    from e2e_bloc_a import _deschide_factura
    f = firma_fe3
    fid = _factura_emisa(patron, f)
    pg = patron.pg
    try:
        for lat, inalt in ((1280, 600), (390, 844)):
            pg.set_viewport_size({"width": lat, "height": inalt})
            _deschide_factura(patron, f, fid)
            pg.wait_for_timeout(400)
            a = pg.evaluate(_ASEZARE)
            patron.captura("antet_%dx%d" % (lat, inalt))
            assert a["vizibil"] and a["un_rand"], a
            assert "DANTE INTERNATIONAL SA" in a["text"] and " nr. " in a["text"] and "SPV" in a["text"] and "RON" in a["text"], a
            assert a["butoane"] and a["in_bara"] == a["butoane"] and a["in_vedere"] == a["butoane"], a
            pg.evaluate("() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(); c.scrollTop = c.scrollHeight; }")
            pg.wait_for_timeout(300)
            assert pg.evaluate(_ASEZARE)["in_vedere"] == a["butoane"]
            pg.click(_F + "#fd-email")
            pg.wait_for_selector(_F + "#fd-email-send", timeout=20000)
            pg.fill(_F + "#fd-email-input", "")
            pg.click(_F + "#fd-email-send")
            pg.wait_for_function("() => (document.querySelector('.fereastra:last-of-type #fd-email-rez') || {}).innerText", timeout=20000)
            pg.wait_for_timeout(800)
            v = pg.evaluate("""() => { const z = document.querySelector('.fereastra:last-of-type #fd-email-rez'), c = z.closest('.fereastra-corp');
              const r = z.getBoundingClientRect(), rc = c.getBoundingClientRect();
              return {text: z.innerText.trim(), fereastra_lui: !z.closest('.fereastra').querySelector('#fd-pdf'),
                      ok: r.top >= rc.top && r.bottom <= Math.min(innerHeight, rc.bottom) + 1}; }""")
            patron.captura("email_refuz_%dx%d" % (lat, inalt))
            # [lotul 13, 673 — DS cap.2a v2.104] formularul de email e în fereastra lui (nu în bara detaliului); refuzul, în vedere
            assert v["text"] == "Introdu o adresă validă." and v["fereastra_lui"] and v["ok"], v
    finally:
        pg.set_viewport_size({"width": 1700, "height": 1000})
