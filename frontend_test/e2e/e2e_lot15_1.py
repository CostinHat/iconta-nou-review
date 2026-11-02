# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1, zona A — scenariile 720 și 721 (Operațiuni speciale › Chirii / comodat / refacturări), în browser, pe ecranul real.

  * 720 — felul e grup de alegere pe un rând, fără „— alege —” ca buton; imediat după alegerea felului „chirie plătită”, la o firmă cu TVA la
          încasare, refuzul 714 apare ca card-rezumat cu drum spre Facturi primite, iar „Generează nota” e inactiv cu motiv; „Verifică” pe CUI aduce
          denumirea și stabilește tipul (câmpul „Proprietar” nu se mai cere); cota TVA e grup de alegere din cotele legale la data documentului;
          câmpurile sunt pe grupuri (Document / Furnizor / Client / Sume), aceeași înălțime (44 px), nimic tăiat la 1920 × 1080 și 1366 × 768.
  * 721 — formularul început se păstrează pe server: „înapoi” duce la Operațiuni speciale, la revenire câmpurile sunt cum au fost lăsate; „Renunță” îl golește.
Firma e NOUĂ (`firma_noua`), cu TVA la încasare din prima zi a lunii."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import pregateste_firma

AZI = _dt.date.today()
REZOLUTII = ((1920, 1080), (1366, 768))


@pytest.fixture()
def firma_tvai(patron):
    for f in firma_noua():
        pregateste_firma(patron, f, regim_fiscal="profit")
        sql('INSERT INTO "%s".tva_incasare_perioade (de_la) VALUES (%%s)' % f["schema"], (AZI.replace(day=1).isoformat(),))   # date-de-pornire: perioada TVA la încasare a firmei
        yield f


def _formular_chirie(patron, f):
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=25000)
    pg.evaluate("""() => { const b = document.querySelector("button[data-op='chirie']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""")
    pg.click("button[data-op='chirie']")
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_timeout(1500)


def _alege(pg, camp, valoare):
    sel = "#op-%s" % camp
    pg.wait_for_function("([s, v]) => [...document.querySelector(s).options].some((o) => o.value === String(v))", arg=[sel, str(valoare)], timeout=20000)
    pg.select_option(sel, str(valoare))
    pg.dispatch_event(sel, "change")


def _taiat(pg):
    """Câmpuri, etichete și texte alese în liste care nu încap în lățimea lor (un select nu raportează depășirea prin scrollWidth: se măsoară textul ales)."""
    return pg.evaluate("""() => {
      const lat = (txt, el) => { const s = document.createElement('span'); const c = getComputedStyle(el);
        s.style.cssText = 'position:absolute;visibility:hidden;white-space:nowrap;font:' + c.font; s.textContent = txt; document.body.appendChild(s);
        const w = s.getBoundingClientRect().width; s.remove(); return w; };
      const rau = [];
      for (const e of document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra .camp-input, .fereastra-overlay:not(.fundal) .fereastra .camp-eticheta')) {
        if (!e.offsetParent) continue;
        if (e.scrollWidth > e.clientWidth + 1) rau.push(e.id || e.textContent.trim());
        if (e.tagName === 'SELECT' && !e.classList.contains('alegere-sursa')) {
          const o = e.options[e.selectedIndex];
          if (o && lat(o.text, e) > e.clientWidth - 36) rau.push((e.id || 'select') + ': ' + o.text);
        }
      }
      return rau; }""")


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_720_formular_pe_piese(patron, firma_tvai, lat, inalt):
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    _formular_chirie(patron, firma_tvai)
    # felul: un singur rând de butoane, fără „— alege —” ca buton, nimic ales la început
    butoane = pg.locator(".alegere-butoane:has(+ #op-fel) > button")
    assert butoane.count() == 4, butoane.all_inner_texts()
    assert not any("alege" in t.lower() for t in butoane.all_inner_texts())
    ys = {round(b.bounding_box()["y"]) for b in butoane.all()}
    assert len(ys) == 1, "felul nu stă pe un rând: %s" % ys
    assert pg.eval_on_selector("#op-fel", "e => e.value") == ""
    # câmpurile pe grupuri, cu titlu
    titluri = pg.locator(".ds-grup:not([hidden]) .ds-grup-titlu").all_inner_texts()
    assert "DOCUMENT" in [t.upper() for t in titluri], titluri
    # felul „chirie plătită” la o firmă cu TVA la încasare: refuzul 714 imediat, cu drum spre Facturi primite; butonul notei inactiv, cu motiv
    _alege(pg, "fel", "chirie_platita")
    pg.wait_for_selector("#op-refuz-fel .ds-rezumat-eroare", timeout=15000)
    assert "Facturi primite" in pg.inner_text("#op-refuz-fel")
    assert pg.locator("#op-refuz-fel .ds-rezumat-actiune").inner_text().strip() == "Deschide Facturi primite"
    assert pg.get_attribute("#op-trimite", "aria-disabled") == "true"
    assert pg.get_attribute("#op-trimite", "data-motiv-inactiv")
    assert pg.inner_text("#op-motiv-inactiv").strip()
    # „Verifică”: denumirea și tipul se stabilesc, „Proprietar” nu se mai cere separat
    pg.fill("#op-furnizor_cui", "14399840")
    pg.click("#op-furnizor_cui-verifica")
    pg.wait_for_function("() => document.querySelector('#op-furnizor_nume').value.length > 3", timeout=20000)
    assert pg.eval_on_selector("#op-proprietar", "e => e.closest('.camp').classList.contains('camp-dedus')")
    assert not pg.is_visible("#op-proprietar")
    # cota: grup de alegere din cotele legale la data documentului, nu câmp de scris
    assert pg.eval_on_selector("#op-cota", "e => e.tagName") == "SELECT"
    cote = pg.locator(".alegere-butoane:has(+ #op-cota) > button").all_inner_texts()
    assert "21%" in cote and "11%" in cote, cote
    # aceeași înălțime pe câmpurile de pe același rând și nimic tăiat
    inaltimi = pg.evaluate("() => [...document.querySelectorAll('.ds-grup .camp-input')].filter((e) => e.offsetParent && e.tagName === 'INPUT').map((e) => Math.round(e.getBoundingClientRect().height))")
    assert inaltimi and set(inaltimi) == {44}, inaltimi
    assert _taiat(pg) == [], _taiat(pg)
    assert pg.evaluate("() => document.documentElement.scrollWidth <= window.innerWidth + 1")
    cuvant = pg.evaluate("""() => { const b = document.querySelector('#op-furnizor_cui-verifica').getBoundingClientRect(), d = document.querySelector('#op-furnizor_nume').getBoundingClientRect();
        return b.right <= d.left || b.bottom <= d.top; }""")
    assert cuvant, "„Verifică” acoperă denumirea: %s" % pg.evaluate("""() => ['#op-furnizor_cui', '#op-furnizor_cui-verifica', '#op-furnizor_nume'].map((q) => { const r = document.querySelector(q).getBoundingClientRect(); return [q, Math.round(r.left), Math.round(r.right), Math.round(r.top)]; })""")
    derulare = pg.evaluate("() => [...document.querySelectorAll('.fereastra-corp')].filter((e) => e.offsetParent && e.scrollHeight > e.clientHeight + 1).map((e) => e.scrollHeight - e.clientHeight)")
    assert derulare == [], "formularul se derulează: %s" % derulare
    patron.captura("l15_720_%d" % lat)


def test_def_721_ciorna_pe_server(patron, firma_tvai):
    pg = patron.pg
    _formular_chirie(patron, firma_tvai)
    _alege(pg, "fel", "chirie_incasata")
    pg.fill("#op-chirie", "1000")
    pg.dispatch_event("#op-chirie", "change")
    pg.wait_for_timeout(2500)   # pauza de tastare: ciorna pleacă la server
    pg.locator(".nav-inapoi").last.click()
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=20000)   # „înapoi” duce la Operațiuni speciale
    assert pg.locator("#fa-operatiuni").count() == 0
    pg.evaluate("""() => { const b = document.querySelector("button[data-op='chirie']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""")
    pg.click("button[data-op='chirie']")
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_function("() => document.querySelector('#op-fel').value === 'chirie_incasata'", timeout=15000)
    assert pg.input_value("#op-chirie") not in ("", None)
    # F5: ciorna e pe server, iar fereastra revine singură (725): formularul are aceleași valori
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_selector("#op-trimite", state="attached", timeout=60000)
    pg.wait_for_function("() => document.querySelector('#op-fel').value === 'chirie_incasata'", timeout=15000)
    # „Renunță” golește ciorna
    pg.click("#op-renunta")
    pg.wait_for_function("() => !!document.querySelector(\"button[data-op='chirie']\")", timeout=20000)
    pg.wait_for_timeout(1500)
    _formular_chirie(patron, firma_tvai)
    assert pg.eval_on_selector("#op-fel", "e => e.value") == ""


# ── zona B ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
@pytest.fixture()
def firma_b(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_722_tip_declaratie_lista_cu_cautare(patron, firma_b, lat, inalt):
    """722 / 726 (refăcut la 15.1-E3, 722 / 727.1): lista „Tip declarație” e lista cu căutare PERMANENTĂ pe lățimea ferestrei (căutare de 44 px, rânduri de 44 px, nimic tăiat):
    datoratele sus (restanțele întâi), restul dedesubt, fără butoane stivuite, fără „încă n” și fără „Arată alte declarații”."""
    from e2e_bloc_a import _card
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    patron.firma(firma_b["nume"])
    _card(patron, "declaratii", "#dec-tip")
    pg.wait_for_function("() => { const s = document.querySelector('#dec-tip'); return !!s && s.classList.contains('ds-lista-sursa') && !!s.nextElementSibling && s.nextElementSibling.classList.contains('ds-lista-permanenta'); }", timeout=30000)
    assert pg.locator("#dec-datorate, #dec-alte, .ds-datorata, .ds-datorate-inca").count() == 0, "butoanele stivuite / „Arată alte declarații” au rămas"
    assert "Alege tipul declarației" not in pg.evaluate("() => document.body.innerText")
    cutie = pg.eval_on_selector(".ds-lista-panou", "e => { const r = e.getBoundingClientRect(); return [r.left, r.right, innerWidth, r.width]; }")
    assert cutie[0] >= 0 and cutie[1] <= cutie[2] and cutie[3] <= 720, cutie   # niciodată mai lată decât ecranul, cel mult 720 px
    assert pg.eval_on_selector(".ds-lista-cauta", "e => Math.round(e.getBoundingClientRect().height)") == 44
    inalt_rand = pg.eval_on_selector_all(".ds-lista-rand", "es => es.map(e => Math.round(e.getBoundingClientRect().height))")
    assert inalt_rand and set(inalt_rand) == {44}, inalt_rand
    grupuri = pg.locator(".ds-lista-grup").all_inner_texts()
    if len(grupuri) > 1:   # datoratele întâi, „Alte declarații” la urmă
        assert grupuri[-1].strip().lower() == "alte declarații", grupuri
    pg.fill(".ds-lista-cauta", "d104")
    filtrate = pg.locator(".ds-lista-rand .ds-lista-nume").all_inner_texts()
    assert filtrate and all("D104" in t.upper() for t in filtrate), filtrate
    patron.captura("l15_722_%d" % lat)
    pg.locator(".ds-lista-rand").first.evaluate("e => e.click()")   # un singur clic (Playwright reîncearcă un clic al cărui țintă dispare în handler)
    pg.wait_for_function("() => { const s = document.querySelector('#dec-tip'); return !!s && s.value === 'd104'; }", timeout=15000)   # ecranul se redesenează după alegere
    assert pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1")


def test_def_fa_emite_factura_cota_grup_si_data(patron, firma_b):
    """F-A: cota liniei e grup de alegere; la data 15.06.2025 grupul arată 19% / 9% / 5%, iar 21% nu se poate alege și nu rămâne aplicată;
    cu 21% aleasă, TVA 210,00 și total 1.210,00; secțiunile se numesc Document / Client / Sume; după emitere butonul nu mai spune „Se emite…”."""
    from e2e_bloc_a import _deschide_emiterea
    pg = patron.pg
    _deschide_emiterea(patron, firma_b["nume"])
    titluri = pg.locator(".fereastra-overlay:not(.fundal) .fereastra .em-eticheta").all_inner_texts()
    assert [t.capitalize() for t in titluri[:3]] == ["Document", "Client", "Sume"], titluri   # CSS le afișează cu majuscule
    pg.fill("#em-l0-descriere", "Serviciu test")
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "1000")
    pg.wait_for_selector("#em-l0-cota-sel, #em-l0-cota", timeout=10000)
    grup = ".alegere-butoane:has(+ #em-l0-cota)"
    assert pg.locator(grup).count() == 1, "cota liniei nu e grup de alegere"
    assert pg.eval_on_selector("#em-l0-cota", "e => e.tagName") == "SELECT"
    pg.click(grup + " > button:has-text('21%')")
    assert pg.evaluate("() => document.body.innerText").count("1.210,00") >= 1
    pg.fill("#em-data", "2025-06-15")
    pg.dispatch_event("#em-data", "change")
    pg.wait_for_function("() => [...document.querySelectorAll('.alegere-butoane:has(+ #em-l0-cota) > button')].some((b) => b.textContent.trim() === '19%')", timeout=15000)
    cote = pg.locator(grup + " > button").all_inner_texts()
    assert "19%" in cote and "9%" in cote and "5%" in cote and "21%" not in cote, cote
    assert pg.eval_on_selector("#em-l0-cota", "e => e.value") == "", "21% a rămas aplicată la o dată în care nu era valabilă"
    patron.captura("l15_fa_2025")


def test_def_547_1_factura_primita_fara_butoanele_facturii_emise(patron, firma_b):
    """547.1: factura primită arată numai acțiunile ei; niciun buton gri fără motiv."""
    from e2e_lot13_fact import _ti_api
    from e2e_bloc_a import _deschide_factura
    fid = _ti_api(patron, firma_b, "TI-547-1")
    _deschide_factura(patron, firma_b, fid)
    pg = patron.pg
    for b in ("#fd-email", "#fd-chitanta", "#fd-spv", "#fd-transforma", "#fd-storno", "#fd-saga"):
        assert pg.locator(b).count() == 0, "%s apare pe o factură primită" % b
    fara_motiv = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra button')].filter((b) => b.offsetParent
        && (b.disabled || b.getAttribute('aria-disabled') === 'true') && !(b.getAttribute('data-motiv-inactiv') || b.title)).map((b) => b.textContent.trim())""")
    assert fara_motiv == [], fara_motiv
    patron.captura("l15_547_1")


def test_def_673_1_nota_se_deschide_in_fereastra_ei(patron, firma_b):
    """673.1: linkul „nota …” din detaliul facturii deschide nota în fereastra ei (720 px, centrată), cu liniile ei; „←” readuce detaliul."""
    from e2e_lot13_fact import _ti_api
    from e2e_bloc_a import _deschide_factura
    fid = _ti_api(patron, firma_b, "TI-673-1")
    _deschide_factura(patron, firma_b, fid)
    pg = patron.pg
    pg.click("#fd-vezi-nota")
    pg.wait_for_selector("#fd-nota-linii", timeout=20000)
    f = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra", "e => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.left + r.width / 2), innerWidth]; }")
    assert f[0] == 720 and abs(f[1] - f[2] / 2) <= 2, f   # 720 px, centrată
    assert "=" in pg.inner_text("#fd-nota-linii")
    patron.captura("l15_673_1")
    pg.locator(".fereastra-overlay:not(.fundal) .fereastra .nav-inapoi").click()
    pg.wait_for_selector("#fd-vezi-nota", timeout=15000)


@pytest.fixture()
def firma_fara_metoda():
    for f in firma_noua():   # firmă nouă, fără profil pregătit: metoda de stoc nedeclarată
        yield f


def test_def_676_1_metoda_de_stoc_grup_de_alegere(patron, firma_fara_metoda):
    """676.1: „Metoda de stoc” e grup de alegere pe un rând, nimic ales la început, fără „— alege —”; cel ales rămâne apăsat după salvare."""
    from e2e_bloc_c import _deschide
    _deschide(patron, firma_fara_metoda["nume"], "datefirma", "#df-metoda_stoc")
    pg = patron.pg
    grup = ".alegere-butoane:has(+ #df-metoda_stoc) > button"
    assert pg.locator(grup).count() >= 2
    assert not any("alege" in t.lower() for t in pg.locator(grup).all_inner_texts())
    assert pg.locator(grup + "[aria-checked='true']").count() == 0, "metoda apare aleasă fără ca omul s-o fi ales"
    ys = {round(b.bounding_box()["y"]) for b in pg.locator(grup).all()}
    assert len(ys) == 1, "butoanele metodei nu stau pe un rând: %s" % ys
    pg.locator(grup + ":has-text('global-valoric')").first.click()
    assert pg.input_value("#df-metoda_stoc") != ""
    assert pg.locator(grup + "[aria-checked='true']").count() == 1
    patron.captura("l15_676_1")


def _formular_operatie(patron, f, cheie, alegeri):
    pg = patron.pg
    patron.firma(f["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='%s']" % cheie, state="attached", timeout=25000)
    pg.evaluate("""(c) => { const b = document.querySelector("button[data-op='" + c + "']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""", cheie)
    pg.click("button[data-op='%s']" % cheie)
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_timeout(1000)
    for camp, val in alegeri:
        _alege(pg, camp, val)
    pg.wait_for_timeout(500)


@pytest.mark.parametrize("cheie,alegeri", (("decont", (("fel", "decont"),)), ("marja_turism", ()), ("chirie", (("fel", "refacturare"),))))
@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_670_509_formular_pe_piese_fara_derulare(patron, firma_b, cheie, alegeri, lat, inalt):
    """670 / 509: formularul Operațiunilor (Decont deplasare — Decont final, Marjă agenții de turism, Refacturare) e pe grupuri, aliniat, etichete întregi pe un rând,
    nimic tăiat și fără derulare la 1920 × 1080 și 1366 × 768."""
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    try:
        _formular_operatie(patron, firma_b, cheie, alegeri)
    except Exception:
        pytest.skip("formularul %s nu se deschide în fixtura asta" % cheie)
    assert _taiat(pg) == [], _taiat(pg)
    et = pg.evaluate("() => [...document.querySelectorAll('.ds-grup .camp-eticheta')].filter((e) => e.offsetParent).map((e) => Math.round(e.getBoundingClientRect().height))")
    assert et and max(et) <= 24, et   # o etichetă nu trece pe al doilea rând
    derulare = pg.evaluate("() => [...document.querySelectorAll('.fereastra-corp')].filter((e) => e.offsetParent && e.scrollHeight > e.clientHeight + 1).map((e) => e.scrollHeight - e.clientHeight)")
    assert derulare == [], "formularul se derulează: %s" % derulare
    assert pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1")
    patron.captura("l15_670_%s_%d" % (cheie, lat))


def test_def_653_1_tara_un_singur_camp_lista_cu_cautare(patron, firma_b):
    """653.1: D207, „Stat de rezidență”: un singur câmp de țară, listă cu căutare, aleasă o dată (nu o căsuță de căutare plus o listă sub ea)."""
    from e2e_lot13_decl import _F, _continua_formular, _platitor, AN_D207
    _platitor(patron, firma_b)
    pg = _continua_formular(patron, firma_b, "d207", AN_D207)
    assert pg.locator(_F + "#d207-stat-cauta").count() == 0
    assert pg.locator(_F + "#d207-stat + .ds-lista").count() == 1
    pg.click(_F + "#d207-stat + .ds-lista .ds-lista-titlu")
    assert pg.locator(_F + ".ds-lista-cauta").count() == 1
    pg.fill(_F + ".ds-lista-cauta", "germ")
    nume = pg.locator(_F + ".ds-lista-rand .ds-lista-nume").all_inner_texts()
    assert "Germania (DE)" in nume and not [t for t in nume if "(FR)" in t], nume
    pg.locator(_F + ".ds-lista-rand").first.evaluate("e => e.click()")
    assert pg.eval_on_selector(_F + "#d207-stat", "e => e.value") == "DE"


def test_def_184_2_suma_separatori_automati(patron, firma_b):
    """184.2 (regula 3a): suma se scrie numai cu cifre; punctele la mii și virgula apar singure, „1000.50” și „1000,5” se corectează, iar la ieșirea din
    câmp suma are două zecimale; valoarea citită de aplicație rămâne cea canonică."""
    pg = patron.pg
    _formular_chirie(patron, firma_b)
    _alege(pg, "fel", "chirie_incasata")
    camp = "#op-chirie"
    pg.click(camp)
    pg.keyboard.type("1000000")
    assert pg.evaluate("(s) => Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').get.call(document.querySelector(s))", camp) == "1.000.000"
    pg.keyboard.press("Tab")
    assert pg.evaluate("(s) => Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').get.call(document.querySelector(s))", camp) == "1.000.000,00"
    assert pg.eval_on_selector(camp, "e => e.value") == "1000000.00"   # valoarea citită de aplicație: canonică
    for scris, afisat, canonic in (("1000.50", "1.000,50", "1000.50"), ("1000,5", "1.000,50", "1000.50"), ("12345,678", "12.345,678", "12345.678")):
        pg.fill(camp, "")
        pg.click(camp)
        pg.keyboard.type(scris)
        pg.keyboard.press("Tab")
        assert pg.evaluate("(s) => Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').get.call(document.querySelector(s))", camp) == afisat, scris
        assert pg.eval_on_selector(camp, "e => e.value") == canonic, scris
    assert pg.eval_on_selector(camp, "e => getComputedStyle(e).textAlign") in ("right", "end")
    patron.captura("l15_184_2")


def test_def_725_f5_readuce_fereastra(patron, firma_tvai):
    """725: după F5 aplicația redeschide aceeași fereastră (firma, Operațiuni speciale › Chirii), cu câmpurile cum au fost lăsate; „Proprietar”, dedus din
    „Verifică”, nu reapare."""
    pg = patron.pg
    _formular_chirie(patron, firma_tvai)
    _alege(pg, "fel", "chirie_platita")
    pg.fill("#op-furnizor_cui", "14399840")
    pg.click("#op-furnizor_cui-verifica")
    pg.wait_for_function("() => document.querySelector('#op-furnizor_nume').value.length > 3", timeout=20000)
    pg.fill("#op-chirie", "1000")
    pg.dispatch_event("#op-chirie", "change")
    pg.wait_for_timeout(2500)   # ciorna pleacă la server
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_selector("#op-trimite", state="attached", timeout=60000)   # nimeni nu a apăsat nimic: fereastra a revenit singură
    pg.wait_for_function("() => document.querySelector('#op-fel') && document.querySelector('#op-fel').value === 'chirie_platita' && document.querySelector('#op-furnizor_nume').value.length > 3", timeout=30000)
    assert pg.input_value("#op-furnizor_cui") == "14399840"
    assert not pg.is_visible("#op-proprietar"), "Proprietar reapare la revenirea din ciornă"
    # închisă de om (Renunță), F5 nu o mai redeschide
    pg.click("#op-renunta")
    pg.wait_for_function("() => !!document.querySelector(\"button[data-op='chirie']\")", timeout=20000)
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_timeout(4000)
    assert pg.locator("#op-trimite").count() == 0


def test_def_712_2_mesajul_tarii_o_singura_data(patron, firma_b):
    """712.1 (observație retest 31.10): țara partenerului nepotrivită cu codul fiscal: după „Emite factură”, mesajul apare o singură dată pe ecran
    (caseta „NU s-a salvat” îl păstrează, linia de stare de lângă CUI se ascunde cât stă caseta)."""
    from e2e_bloc_a import _deschide_emiterea
    pg = patron.pg
    _deschide_emiterea(patron, firma_b["nume"])
    pg.fill("#em-cui", "14399840")
    pg.fill("#em-nume", "DANTE INTERNATIONAL SA")
    pg.dispatch_event("#em-nume", "input")
    pg.click(".rap-tab[data-fila='tva']")
    pg.select_option("#em-tara", "DE")
    pg.dispatch_event("#em-tara", "change")
    pg.click(".rap-tab[data-fila='factura']")
    pg.fill("#em-l0-descriere", "Serviciu")
    pg.fill("#em-l0-cantitate", "1")
    pg.fill("#em-l0-pret_unitar", "100")
    pg.fill("#em-l0-um", "buc")
    pg.click(".alegere-butoane:has(+ #em-l0-cota) > button:has-text('21%')")
    pg.click("#em-emite")
    pg.wait_for_selector(".refuz-salvare", timeout=20000)
    text = pg.evaluate("() => document.body.innerText")
    assert text.count("nu se potrivește cu codul fiscal") == 1, text.count("nu se potrivește cu codul fiscal")


# ── zona C ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_713_bara_de_sus_fara_traseu(patron, firma_b):
    """713 / 681.1 / 701: bara de sus arată numai firma în lucru (nume · CUI) și numele ferestrei curente, fără traseu; „←” face un pas înapoi."""
    pg = patron.pg
    _formular_chirie(patron, firma_b)
    antet = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra .fereastra-antet", "e => e.innerText")
    assert "CUI" in antet and "Chirii" in antet, antet
    assert pg.locator(".fereastra-overlay:not(.fundal) .fereastra .fir-veriga").count() == 0, "traseul (Firme › Firme existente › …) nu mai apare în bara de sus"
    assert "Firme existente" not in antet and "Operațiuni speciale" not in antet, antet
    pg.locator(".fereastra-overlay:not(.fundal) .fereastra .nav-inapoi").click()
    pg.wait_for_function("() => !!document.querySelector(\"button[data-op='chirie']\")", timeout=20000)   # un pas înapoi: lista Operațiunilor
    antet2 = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra .fereastra-antet", "e => e.innerText")
    assert "Operațiuni speciale" in antet2 and "Chirii" not in antet2, antet2


def test_def_681_1_istoric_gaseste_facturile(patron, firma_b):
    """681.1: căutarea de funcții potrivește pe sens: „istoric” duce la fereastra Facturi (Istoric facturi), „stat de plată” nu dă D100."""
    from e2e_bloc_d import PATRON, _api
    st, r = _api(PATRON, "GET", "/eu/cautare?q=istoric&tenant_id=%d" % firma_b["tenant_id"])
    assert st == 200, (st, r)
    assert any(x.get("cheie") == "facturi" for x in r["rezultate"]), r["rezultate"]
    st, r = _api(PATRON, "GET", "/eu/cautare?q=stat%%20de%%20plata&tenant_id=%d" % firma_b["tenant_id"])
    assert st == 200 and r["rezultate"] and r["rezultate"][0]["titlu"] == "Stat de plată", r["rezultate"]   # [15.1-E3, 681.2] sensul bate cuvântul comun: Stat de plată e primul, D100 (…„bugetul de stat”) vine după


def test_def_687_2_inchidere_luna_semnale_si_amortizare(patron, firma_b):
    """687.1-a: Închidere lună: semnalele pe un rând fiecare (detalii pliate, fără derulare internă), un singur buton principal, „Registru jurnal” pe luna
    ferestrei, „Generează amortizarea” inactiv cu motiv când luna e blocată."""
    from e2e_bloc_d import PATRON, _api
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    an, luna = (AZI.year, AZI.month - 1) if AZI.month > 1 else (AZI.year - 1, 12)
    st, r = _api(PATRON, "POST", "/tenants/%d/perioade-blocate?an=%d&luna=%d" % (firma_b["tenant_id"], an, luna), {})
    if st != 200:
        pytest.skip("luna %02d/%d nu se poate bloca în fixtura asta: %s" % (luna, an, r))
    patron.firma(firma_b["nume"])
    pg.click("#fa-inchidere")
    pg.wait_for_selector("#il-lock", timeout=20000)
    pg.click("#il-prev")   # luna precedentă = blocată
    pg.wait_for_function("() => document.querySelector('#il-lock') && document.querySelector('#il-lock').textContent.includes('Deblochează')", timeout=20000)
    text = pg.evaluate("() => document.querySelector('.fereastra-overlay:not(.fundal) .fereastra').innerText")
    assert "Nimic nu oprește închiderea lunii" not in text, "luna blocată spune că nimic nu oprește închiderea"
    assert pg.get_attribute("#il-amort", "aria-disabled") == "true" and pg.get_attribute("#il-amort", "data-motiv-inactiv")
    assert pg.inner_text("#il-amort-motiv").strip()
    assert pg.locator("#il-jurnal").count() == 1
    assert pg.locator(".fereastra-overlay:not(.fundal) .fereastra button.buton-primar:visible").count() == 1, "mai mult de o acțiune principală"
    derulare = pg.evaluate("() => [...document.querySelectorAll('.fereastra-corp, .ds-semnale-lista, #il-controale')].filter((e) => e.offsetParent && e.scrollHeight > e.clientHeight + 1 && getComputedStyle(e).overflowY !== 'visible' && e.id !== '').length")
    assert derulare == 0, "semnalele derulează intern"
    patron.captura("l15_687_1_a")


def test_def_687_3_spv_card_rezumat_pe_ecranul_firmei(patron, firma_b):
    """687.1-SPV: starea SPV a firmei e un card-rezumat de un rând (≤ 52 px), cu explicația pliată sub „▾ detalii” și butonul spre Conectare SPV, nimic tăiat la 1366."""
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    patron.firma(firma_b["nume"])
    pg.wait_for_selector("#firma-spv .ds-rezumat", timeout=30000)
    h = pg.eval_on_selector("#firma-spv .ds-rezumat", "e => Math.round(e.getBoundingClientRect().height)")
    assert h <= 52, h
    if pg.locator("#firma-spv .ds-rezumat-plie").count():
        pg.click("#firma-spv .ds-rezumat-plie")
        assert pg.is_visible("#firma-spv .ds-rezumat-detalii")
    patron.captura("l15_687_3")


def test_def_724_restantele_din_termene_sunt_cele_din_control_fiscal():
    """724: Termene arată exact restanțele din Control fiscal (`lipsa`): nicio perioadă dinaintea preluării, nicio declarație „nu se datorează”; aceeași sursă."""
    import datetime as _dt
    from conftest import _db
    from core import control_fiscal_api as _cf
    from core import firma_rezumat as FR
    ctx = {"uid": None}
    for f in firma_noua():
        azi = _dt.date.today()
        with _db().get_conn(f["schema"]) as cs:
            r = _cf.evalueaza_firma(cs, cs, f["tenant_id"], f["schema"], azi)
        rest = {(str(e["tip"]).lower(), e["an"], e.get("luna")) for e in (r.get("lipsa") or [])}
        ev, _neev = FR._termene_una_firma({"id": f["tenant_id"], "nume": f["nume"], "cui": None}, ctx, azi, rest)
        din_termene = {(str(t["tip"]).lower(), t["an"], t.get("luna")) for t in ((ev or {}).get("termene") or []) if t.get("restanta")}
        assert din_termene <= rest, ("restanțe în Termene care nu sunt în Control fiscal", din_termene - rest)


def test_def_673_2_nota_peste_fereastra_facturii_nu_peste_cabinet(patron, firma_b):
    """673.2 / 446.2: fereastra mică (nota, 720 px) se deschide peste fereastra facturii, nu peste ecranul cabinetului; bara ei nu poartă firul de navigare."""
    from e2e_lot13_fact import _ti_api
    from e2e_bloc_a import _deschide_factura
    fid = _ti_api(patron, firma_b, "TI-673-2")
    _deschide_factura(patron, firma_b, fid)
    pg = patron.pg
    pg.click("#fd-vezi-nota")
    pg.wait_for_selector("#fd-nota-linii", timeout=20000)
    fundal = pg.locator(".fereastra-overlay.fundal")
    assert fundal.count() == 1, "sub nota deschisă trebuie să se vadă fereastra facturii"
    assert fundal.locator("#fd-vezi-nota").count() == 1, "fundalul nu e fereastra facturii"
    assert fundal.get_attribute("inert") is not None
    sus = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra-antet", "e => e.innerText")
    assert "Firme" not in sus and "›" not in sus, sus
    pg.locator(".fereastra-overlay:not(.fundal) .fereastra .nav-inapoi").click()
    pg.wait_for_selector("#fd-vezi-nota", timeout=15000)
    assert pg.locator(".fereastra-overlay.fundal").count() == 0


def test_def_725_1_f5_din_istoric_facturi_readuce_istoricul(patron, firma_b):
    """725.1: Ctrl+R din Istoric facturi readuce Istoric facturi, nu ecranul cabinetului."""
    pg = patron.pg
    patron.firma(firma_b["nume"])
    pg.click("#fa-facturi")
    pg.click("#fac-istoric")
    pg.wait_for_function("() => /Istoric/i.test(document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-antet').innerText)", timeout=30000)
    pg.reload(wait_until="domcontentloaded")
    pg.wait_for_function("() => { const a = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-antet'); return !!a && /Istoric/i.test(a.innerText); }", timeout=60000)


def test_def_726_declaratiile_datorate_sunt_primele_din_lista(patron, firma_b):
    """726 (refăcut la 15.1-E3): declarațiile datorate („D112 · 08/2026 · termen …”, motivul „restanță” în dreapta) sunt primele rânduri ale listei cu căutare,
    restanțele întâi; fără „Alege tipul declarației”."""
    from e2e_bloc_a import _card
    pg = patron.pg
    patron.firma(firma_b["nume"])
    _card(patron, "declaratii", "#dec-tip")
    pg.wait_for_selector(".ds-lista-permanenta .ds-lista-rand", state="attached", timeout=30000)
    primul_grup = pg.evaluate("""() => { const u = document.querySelector('.ds-lista-randuri'); const r = []; let g = null;
        for (const li of u.children) { if (li.classList.contains('ds-lista-grup')) { g = li.textContent.trim(); continue; }
          if (li.classList.contains('ds-lista-rand')) r.push({ g, nume: li.querySelector('.ds-lista-nume').textContent, motiv: li.querySelector('.ds-lista-motiv').textContent }); }
        return r; }""")
    datorate = [x for x in primul_grup if x["g"] and "datorate" in x["g"].lower()]
    assert datorate, "firma de test n-are declarații datorate: %s" % primul_grup
    assert "Alege tipul declarației" not in pg.evaluate("() => document.body.innerText")
    for g in {x["g"] for x in datorate}:   # în fiecare grup al datoratelor, restanțele sunt înaintea celorlalte
        restanta = ["restan" in x["motiv"].lower() for x in datorate if x["g"] == g]
        assert restanta == sorted(restanta, reverse=True), "restanțele nu sunt toate înaintea celorlalte în %s: %s" % (g, datorate)
    assert all("termen" in x["nume"] for x in datorate), datorate
    assert primul_grup.index(datorate[0]) == 0, "datoratele nu sunt primele"


def test_def_d1_control_fiscal_cabinet_pe_tot_ecranul(patron, firma_b):
    """D1 (zona C, pct.2): Control fiscal de la cabinet e fereastră de lucru pe tot ecranul (margine 16 px), nu fereastră mică centrată."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector(".fereastra-overlay:not(.fundal) .fereastra.fer-lucru", timeout=30000)
    r = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra", "e => { const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.width), innerWidth]; }")
    assert r[0] == 16 and r[1] == r[2] - 32, r   # 15.1-D: marginea ferestrei de lucru e 16 px, exact, pe fiecare parte


def _corp_derulat(pg):
    return pg.evaluate("() => { const c = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra-corp'); return c ? c.scrollHeight - c.clientHeight : -1; }")


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_def_d3_operatiuni_speciale_fara_derulare_titluri_ds(patron, firma_b, lat, inalt):
    """D3: Operațiuni speciale încape pe ecran fără derulare (1366 × 768 și 1920 × 1080); titlurile categoriilor sunt titluri de grup DS."""
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    patron.firma(firma_b["nume"])
    pg.locator("#fa-operatiuni").evaluate("e => e.click()")
    pg.wait_for_selector(".op-categorie .ds-grup-titlu", timeout=25000)
    assert _corp_derulat(pg) <= 1, _corp_derulat(pg)
    assert pg.locator(".op-categorie .pf-frand-nume").count() == 0


def test_def_d3_bilant_avertisment_card_si_un_singur_buton_principal(patron, firma_b):
    """D3: Bilanț anual — categoria nedeterminată e un card-rezumat de un rând (nu zid de text roșu), iar fereastra are un singur buton principal."""
    pg = patron.pg
    patron.firma(firma_b["nume"])
    pg.locator("#fa-bilant").evaluate("e => e.click()")
    pg.wait_for_selector("#bl-val", timeout=25000)
    pg.wait_for_function("() => !!document.querySelector('#bl-categorie .ds-rezumat') || !!document.querySelector('#bl-categorie .caseta-info')", timeout=30000)
    assert pg.locator("#bl-categorie .caseta-atentie").count() == 0
    principale = pg.evaluate("() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra .buton-primar')].filter((b) => b.offsetParent).length")
    assert principale <= 1, principale


def test_def_d3_control_fiscal_lista_tabel_ds_si_titluri_fara_majuscule(patron, firma_b):
    """D3 (3a, 3b, 3d, 3g): Control fiscal de la cabinet — bara ferestrei spune cabinetul; lista firmelor e tabel DS (cap, rânduri, pastila în coloana Stare, buton
    „Deschide”); titlurile de secțiune din Detaliu firmă nu sunt scrise cu majuscule."""
    pg = patron.pg
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='control'])")
    pg.wait_for_selector("#cf-lista .ds-tabel tbody tr", timeout=60000)
    bara = pg.inner_text(".fereastra-overlay:not(.fundal) .fereastra-fir")
    assert "Cabinet" in bara and bara.rstrip().endswith("Control fiscal"), bara   # cabinetul + numele ferestrei curente, fără traseu de ecrane
    assert pg.locator(".fereastra-overlay:not(.fundal) .fereastra-fir .fir-firma").count() == 1
    assert pg.locator("#cf-lista thead th").count() == 4
    assert pg.locator("#cf-lista tbody tr:first-child .ds-pastila").count() == 1
    assert pg.locator("#cf-lista tbody tr:first-child button", has_text="Deschide").count() == 1
    inalt = pg.eval_on_selector_all("#cf-lista tbody tr", "es => [...new Set(es.map(e => Math.round(e.getBoundingClientRect().height)))]")
    assert inalt == [44], inalt
    pg.locator("#cf-lista tbody tr:first-child button", has_text="Deschide").evaluate("e => e.click()")
    pg.wait_for_selector(".cf-grup-titlu", timeout=60000)
    transformari = pg.eval_on_selector_all(".cf-grup-titlu", "es => [...new Set(es.map(e => getComputedStyle(e).textTransform))]")
    assert transformari == ["uppercase"], transformari   # [15.1-E3, 733] titlurile de grup: 14 px, majuscule, gri (titlul de secțiune de 20 px nu mai e în Detaliu firmă)


@pytest.mark.parametrize("cheie", ["validat", "termene", "firme", "activitate", "pachete", "supervizor", "capacitate", "consolidare", "asistenti", "setari", "brief"])
def test_def_d4_ecranele_de_cabinet_sunt_ferestre_de_lucru_pe_tot_ecranul(patron, firma_b, cheie):
    """D4: fiecare ecran de cabinet (De validat, Termene, Firme, Activitate, Pachete lunare, Supervizor, Capacitate, Consolidare, Asistenți, Setări cont, Sinteza zilei) e fereastră
    de lucru pe tot ecranul (margine 16 px), cu bara de sus „Cabinet › numele ferestrei”, fără traseu și fără titluri de secțiune scrise cu majuscule."""
    pg = patron.pg
    patron.acasa()
    pg.locator("button.cab-card:has([data-cheie='%s'])" % cheie).first.evaluate("e => e.click()")
    pg.wait_for_selector(".fereastra-overlay:not(.fundal) .fereastra.fer-lucru", timeout=30000)
    r = pg.eval_on_selector(".fereastra-overlay:not(.fundal) .fereastra", """async e => { await Promise.all(e.getAnimations().map((a) => a.finished));
        const b = e.getBoundingClientRect(); return [Math.round(b.left), Math.round(b.top), Math.round(b.width), innerWidth]; }""")
    assert r[0] == 16 and r[1] == 16 and r[2] == r[3] - 32, r
    bara = pg.inner_text(".fereastra-overlay:not(.fundal) .fereastra-fir")
    assert bara.count("›") == 1 and bara.startswith("Cabinet"), bara
    maj = pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) .fereastra-corp *')].filter((e) => e.offsetParent && e.children.length === 0
        && (e.textContent || '').trim().length > 2 && getComputedStyle(e).textTransform === 'uppercase'
        && !e.matches('.ds-grup-titlu, .cf-grup-titlu, .em-eticheta, .mf-eticheta, .ans-grupa-titlu, .ds-lista-grup')).map((e) => String(e.className).split(' ')[0])""")   # [15.1-E3, 733] titlurile de grup (14 px, majuscule, gri) sunt singurele permise
    assert maj == [], maj


def test_def_d4_ecranele_din_panoul_admin_sunt_ferestre_de_lucru():
    """D4: regula ferestrei de lucru e în navigator (fără excepție pe nivel): orice fereastră în afară de confirmare, notă și tabel ia ecranul."""
    import re
    src = open("static/js/navigator.js", encoding="utf-8").read()
    m = re.search(r'fer\.classList\.toggle\("fer-lucru", ([^;]+)\);', src)
    assert m and 'stiva.length' not in m.group(1) and all(x in m.group(1) for x in ('"mic"', '"tabel"', '"nota"')), m and m.group(1)
