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
      for (const e of document.querySelectorAll('.fereastra:last-of-type .camp-input, .fereastra:last-of-type .camp-eticheta')) {
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
    """722: „Tip declarație” e listă cu căutare pe lățimea ferestrei, rânduri de 44 px, nimic tăiat, la ambele rezoluții."""
    from e2e_bloc_a import _card
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    patron.firma(firma_b["nume"])
    _card(patron, "declaratii", "#dec-tip")
    pg.wait_for_function("() => { const s = document.querySelector('#dec-tip'); return !!s && s.classList.contains('ds-lista-sursa') && !!s.nextElementSibling && s.nextElementSibling.classList.contains('ds-lista'); }", timeout=30000)
    lista = pg.locator(".ds-lista")
    assert lista.count() == 1
    pg.click(".ds-lista-titlu")
    pg.wait_for_selector(".ds-lista-cauta", timeout=5000)
    cutie = pg.eval_on_selector(".ds-lista-panou", "e => { const r = e.getBoundingClientRect(); return [r.left, r.right, innerWidth]; }")
    assert cutie[0] >= 0 and cutie[1] <= cutie[2], cutie   # niciodată mai lată decât ecranul
    inalt_rand = pg.eval_on_selector_all(".ds-lista-rand", "es => es.map(e => Math.round(e.getBoundingClientRect().height))")
    assert inalt_rand and set(inalt_rand) == {44}, inalt_rand
    nume = pg.locator(".ds-lista-rand .ds-lista-nume").all_inner_texts()
    assert any(t.upper().startswith("D300") for t in nume), nume
    # căutarea filtrează după nume
    pg.fill(".ds-lista-cauta", "d394")
    filtrate = pg.locator(".ds-lista-rand .ds-lista-nume").all_inner_texts()
    assert filtrate and all("D394" in t.upper() for t in filtrate), filtrate
    patron.captura("l15_722_%d" % lat)
    pg.locator(".ds-lista-rand").first.evaluate("e => e.click()")   # un singur clic (Playwright reîncearcă un clic al cărui țintă dispare în handler)
    pg.wait_for_function("() => { const s = document.querySelector('#dec-tip'); return !!s && s.value === 'd394'; }", timeout=15000)   # ecranul se redesenează după alegere
    assert pg.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1")


def test_def_fa_emite_factura_cota_grup_si_data(patron, firma_b):
    """F-A: cota liniei e grup de alegere; la data 15.06.2025 grupul arată 19% / 9% / 5%, iar 21% nu se poate alege și nu rămâne aplicată;
    cu 21% aleasă, TVA 210,00 și total 1.210,00; secțiunile se numesc Document / Client / Sume; după emitere butonul nu mai spune „Se emite…”."""
    from e2e_bloc_a import _deschide_emiterea
    pg = patron.pg
    _deschide_emiterea(patron, firma_b["nume"])
    titluri = pg.locator(".fereastra:last-of-type .em-eticheta").all_inner_texts()
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
    fara_motiv = pg.evaluate("""() => [...document.querySelectorAll('.fereastra:last-of-type button')].filter((b) => b.offsetParent
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
    f = pg.eval_on_selector(".fereastra:last-of-type", "e => { const r = e.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.left + r.width / 2), innerWidth]; }")
    assert f[0] == 720 and abs(f[1] - f[2] / 2) <= 2, f   # 720 px, centrată
    assert "=" in pg.inner_text("#fd-nota-linii")
    patron.captura("l15_673_1")
    pg.locator(".fereastra:last-of-type .nav-inapoi").click()
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
