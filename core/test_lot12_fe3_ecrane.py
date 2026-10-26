# -*- coding: utf-8 -*-
"""[lotul 12, pachetul fe3] Ecranele comenzii 12.3 (pct.1, 4, 9), în Chromium, cu rutele simulate (se măsoară ecranul real, nu baza).

Deciziile, verbatim din comanda Costin 12.3:
  pct.4 (C164): „pe ecranele scunde, antetul detaliului facturii se strânge pe un rând (număr, client, total, stare SPV); acțiunea
                principală rămâne fixă jos (clasa 285).”
  pct.9:        „Da: cota și categoria pe linia șablonului recurent, ca la factură.”
  pct.1 (C109): „refuzul cronului ajunge la contabil prin notificare (clopoțel și email); pe șablon se vede și starea ultimei emiteri.”

Ecranele REALE (`facturi_ecran.js`, `navigator.js`, `stil.css` din arbore), cu harness-ul pachetului ui2 (`core/test_lot12_ui2_ecrane.py`).
Măsurat la 1280×600 (fereastra scundă) și pe telefon (390×844); la 1280×900 antetul rămâne cel de până acum (regresia).
Mutațiile (raportul fe3): `--antet-scund` scos din media query -> antetul nu se strânge -> ROȘU; mutarea butoanelor în bară scoasă -> „Trimite
pe email” nu e în bară -> ROȘU; categoria netrimisă de ecranul șablonului -> corpul cererii fără `categorie_tva` -> ROȘU; rândul refuzului
scos din lista șabloanelor -> ROȘU.

Temei: N/A — reguli de interfață (DS cap.9 „Antetul documentului pe ecranul scund”, cap.6 285, cap.8); cota și categoria TVA nu se
calculează aici (le verifică emiterea, `categorii_tva.verifica_linii`, testată în `core/test_lot12_fe3_recurente.py`).
"""
import json

from core.test_lot12_ui2_ecrane import _pagina, browser  # noqa: F401 — harness-ul comun (serverul static + Chromium)

_CORP = "[...document.querySelectorAll('.fereastra-corp')].pop()"


def _factura(n_linii=30):
    linii = [{"id": i, "descriere": "Serviciu de probă %d" % i, "cantitate": 1, "um": "buc", "pret_unitar": 100, "cota_tva": 21,
              "categorie_tva": None} for i in range(1, n_linii + 1)]
    return {"id": 7, "numar": "15", "serie": "FE3", "tip": "factura", "directie": "emisa", "status": "emisa", "moneda": "RON",
            "data_emitere": "2026-10-20", "data_scadenta": "2026-11-19", "tert_nume": "ALFA PROBA SRL", "tert_cod": "14399840",
            "tert_cod_eticheta": "CUI", "tert_adresa_completa": "Str. Exemplu 1, Cluj-Napoca", "linii": linii,
            "total": 121.0 * n_linii, "tva": 21.0 * n_linii, "contabilizata": False, "nota_contare": None,
            "stare_incasare": {"stare": "neincasata"},
            "stare_spv": {"stare": "netrimisa", "termen": "2026-10-27", "depasit": False, "obligatorie": True}}


def _rute_detaliu(f):
    return {"/facturi/perioada": {}, "/facturi/7": f, "/facturi": {"facturi": [dict(f, linii=None)]},
            "/trimiteri-spv": {}, "/chitante": {"chitante": []}}


def _deschide_detaliul(pg):
    pg.evaluate("""async () => { const m = await import('/static/js/ecrane/facturi_ecran.js');
      window._nav.deschide('Facturi', (c, n) => m.randeazaFacturi(c, n, 1, {})); }""")
    pg.wait_for_selector("#fac-istoric", timeout=15000)
    pg.click("#fac-istoric")
    pg.wait_for_selector(".fac-frand-btn[data-id='7']", timeout=15000)
    pg.click(".fac-frand-btn[data-id='7']")
    pg.wait_for_selector("#fd-pdf", timeout=15000)
    pg.wait_for_timeout(300)


#: unde stă fiecare parte a detaliului: rândul scurt (vizibil, un rând), butoanele (în ce bloc, în vedere), rezumatul lipit
_ASEZARE = """() => { const c = %s, sc = c.querySelector('#fd-antet-scurt'), rc = c.getBoundingClientRect();
  const jos = Math.min(innerHeight, rc.bottom), vazut = (e) => { const r = e.getBoundingClientRect();
    return r.width > 0 && r.top >= rc.top - 1 && r.bottom <= jos + 1; };
  const copii = sc ? [...sc.children].filter((e) => e.getClientRects().length) : [];
  const sus = copii.map((e) => e.getBoundingClientRect().top), inalt = copii.map((e) => e.getBoundingClientRect().height);
  const butoane = [...c.querySelectorAll('button.buton-secundar[id^=fd-]')];
  return {scurt_vizibil: !!sc && !sc.hidden && sc.getClientRects().length > 0,
          scurt_text: sc ? sc.innerText.replace(/\\s+/g, ' ').trim() : '',
          scurt_un_rand: copii.length > 0 && Math.max(...sus) - Math.min(...sus) < Math.max(...inalt) && sc.scrollHeight <= sc.clientHeight + 1,
          scurt_inaltime: sc ? sc.getBoundingClientRect().height : 0,
          butoane: butoane.map((b) => b.id),
          in_bara: butoane.filter((b) => b.closest('.bara-fixa')).map((b) => b.id),
          in_antet: butoane.filter((b) => b.closest('.fd-antet-sus')).map((b) => b.id),
          vizibile: butoane.filter(vazut).map((b) => b.id),
          rezumat: (c.querySelector('.rezumat-fix') || {}).id || (c.querySelector('.rezumat-fix') || {className: ''}).className,
          lateral: c.scrollWidth > c.clientWidth + 1, deruleaza: c.scrollHeight > c.clientHeight + 1}; }""" % _CORP


def _asezare(pg, jos=False):
    pg.evaluate("() => { const c = %s; c.scrollTop = %s; }" % (_CORP, "c.scrollHeight" if jos else "0"))
    pg.wait_for_timeout(150)
    return pg.evaluate(_ASEZARE)


def _pe_ecranul_scund(a):
    """Rândul scurt vizibil, pe un rând, cu numărul, clientul, totalul și starea SPV; toate butoanele în bara de jos, în vedere."""
    assert a["scurt_vizibil"] and a["scurt_un_rand"], a
    for t in ("Factură FE3 nr. 15", "ALFA PROBA SRL", "3.630,00 RON", "netrimisă în SPV"):
        assert t in a["scurt_text"], (t, a)
    assert a["rezumat"] == "fd-antet-scurt", a                     # rezumatul lipit sus e rândul scurt, nu antetul întreg
    assert a["butoane"] and a["in_bara"] == a["butoane"] and not a["in_antet"], a
    assert a["vizibile"] == a["butoane"], a                       # acțiunea principală fixă jos, în vedere fără derulare
    assert not a["lateral"], a


def test_def_c164_pe_fereastra_scunda_antetul_e_un_rand_iar_actiunile_raman_jos(browser):  # noqa: F811
    """1280×600, factura cu 30 de linii (tabelul derulează): antetul lipit e UN rând (număr, client, total, stare SPV), iar „PDF factură”,
    „Trimite pe email”, „Stornează”, „Emite chitanță”, „Export SAGA”, „Trimite în SPV” stau în bara lipită jos — în vedere la începutul și
    la capătul tabelului. Rezultatul unei acțiuni („Introdu o adresă validă.” la „Trimite pe email” cu adresa goală) e în vedere — de la
    lotul 13 (673, DS cap.2a v2.104) în fereastra formularului de email, deschisă peste detaliu."""
    f = _factura()
    pg, erori = _pagina(browser, _rute_detaliu(f), lat=1280, inalt=600)
    _deschide_detaliul(pg)
    sus = _asezare(pg)
    assert sus["deruleaza"], sus                                  # anti-vacuu: tabelul e mai lung decât fereastra
    _pe_ecranul_scund(sus)
    assert sus["scurt_inaltime"] <= 60, sus
    _pe_ecranul_scund(_asezare(pg, jos=True))
    pg.click("#fd-email")
    pg.wait_for_selector("#fd-email-send", timeout=5000)
    pg.fill("#fd-email-input", "")
    pg.click("#fd-email-send")
    pg.wait_for_function("() => (document.querySelector('#fd-email-rez') || {}).innerText", timeout=5000)
    v = pg.evaluate("""() => { const c = %s, z = c.querySelector('#fd-email-rez'), r = z.getBoundingClientRect(), rc = c.getBoundingClientRect();
      return {text: z.innerText.trim(), fereastra_lui: !c.querySelector('#fd-pdf'), ok: r.top >= rc.top && r.bottom <= Math.min(innerHeight, rc.bottom) + 1}; }"""
                    % _CORP)
    assert v["text"] == "Introdu o adresă validă." and v["fereastra_lui"] and v["ok"], v
    assert erori == [], erori


def test_def_c164_pe_telefon_antetul_e_un_rand_iar_actiunile_raman_jos(browser):  # noqa: F811
    """390×844 (telefon): același rând scurt, butoanele în bara de jos, în vedere; nimic nu împinge fereastra lateral."""
    pg, erori = _pagina(browser, _rute_detaliu(_factura()), lat=390, inalt=844)
    _deschide_detaliul(pg)
    _pe_ecranul_scund(_asezare(pg))
    _pe_ecranul_scund(_asezare(pg, jos=True))
    assert erori == [], erori


def test_c164_pe_ecranul_inalt_antetul_ramane_cel_de_pana_acum_si_revine_la_marire(browser):  # noqa: F811
    """1280×900: rândul scurt ascuns, butoanele în antetul lipit sus (DS cap.9 v2.96 pct.5), în ordinea lor. Fereastra micșorată la 600 px
    -> rândul scurt și butoanele jos; mărită la loc -> fiecare buton înapoi în antet, în aceeași ordine, iar zona de rezultat a unei
    acțiuni rămâne cu ce era scris în ea (se mută nodurile, nu se redesenează). [lotul 13, 673] „Trimite pe email” și „Stornează” au acum
    fereastra lor; zona care rămâne în detaliu e rezultatul lui „Export SAGA”."""
    pg, erori = _pagina(browser, _rute_detaliu(_factura()), lat=1280, inalt=900)
    _deschide_detaliul(pg)
    inalt = _asezare(pg)
    assert not inalt["scurt_vizibil"] and inalt["in_antet"] == inalt["butoane"] and not inalt["in_bara"], inalt
    assert {"fd-antet"} <= set(inalt["rezumat"].split()), inalt   # clasa (sau id-ul) rezumatului lipit: antetul întreg
    ordine = pg.eval_on_selector_all(".fd-antet-sus > *", "els => els.map((e) => e.id || e.tagName)")
    pg.click("#fd-saga")
    pg.wait_for_function("() => (document.querySelector('#fd-saga-zona') || {innerText: ''}).innerText.includes('XML SAGA descărcat')", timeout=5000)
    pg.set_viewport_size({"width": 1280, "height": 600})
    pg.wait_for_timeout(300)
    _pe_ecranul_scund(_asezare(pg))
    assert "XML SAGA descărcat" in pg.inner_text("#fd-saga-zona")
    pg.set_viewport_size({"width": 1280, "height": 900})
    pg.wait_for_timeout(300)
    inapoi = _asezare(pg)
    assert not inapoi["scurt_vizibil"] and inapoi["in_antet"] == inalt["butoane"], inapoi
    assert pg.eval_on_selector_all(".fd-antet-sus > *", "els => els.map((e) => e.id || e.tagName)") == ordine
    assert "XML SAGA descărcat" in pg.inner_text("#fd-saga-zona")
    assert erori == [], erori


# ── 12.3 pct.9: cota și categoria pe linia șablonului ──────────────────────────────────────────────────────────────────────────────
_NUMEROTARE = {"cote_permise": [21, 11, 0], "categorii_tva": [{"cod": "scutit_cu_drept", "eticheta": "Scutit cu drept de deducere"},
                                                               {"cod": "taxare_inversa", "eticheta": "Taxare inversă (art.331)"},
                                                               {"cod": "livrare_ic", "eticheta": "Livrare intracomunitară scutită"},
                                                               {"cod": "serviciu_extern", "eticheta": "Prestare cu locul în afara României"}],
               "categorii_331": [{"cod": "deseuri", "eticheta": "Deșeuri feroase și neferoase"}]}


def _deschide_sablonul(pg):
    pg.evaluate("""async () => { const m = await import('/static/js/ecrane/facturi_ecran.js');
      window._nav.deschide('Șablon nou', (c, n) => m.formSablon(c, n, 1, {})); }""")
    pg.wait_for_selector("#fr-l0-descriere", timeout=15000)


def test_9_sablonul_platitorului_alege_cota_si_categoria_pe_linie_ca_la_factura(browser):  # noqa: F811
    """Plătitorul: „Consultanță IT” -> cota propusă din nomenclator (21%) preselectată în lista cotelor în vigoare; aleasă 0% -> lista
    categoriilor apare; „Prestare cu locul în afara României” -> salvarea trimite cota 0 și categoria pe linie; a doua linie cu taxare inversă
    -> „Categoria produsului (art.331)” apare și pleacă pe șablon. Cota schimbată de pe 0% golește categoria (ca la emitere)."""
    trimis = []

    def salveaza(metoda, _c, _q, corp):
        if metoda == "POST":
            trimis.append(json.loads(corp))
        return {"id": 1}
    rute = {"/facturi/numerotare": _NUMEROTARE, "/vector": {"platitor_tva": True},
            "/produse/potriveste": {"ok": True, "cota": 21}, "/facturi-recurente": salveaza}
    pg, erori = _pagina(browser, rute, lat=1280, inalt=720)
    _deschide_sablonul(pg)
    assert pg.eval_on_selector("#fr-l0-cota", "e => [e.tagName, [...e.options].map((o) => o.textContent)]") == ["SELECT", ["—", "21%", "11%", "0%"]]
    assert pg.is_hidden("#fr-l0-categorie") and pg.is_hidden("#fr-c331")
    pg.fill("#fr-cui", "DE811907980")
    pg.dispatch_event("#fr-cui", "change")
    pg.fill("#fr-nume", "KUNDE GMBH")
    pg.fill("#fr-l0-descriere", "Consultanta IT lunara")
    pg.wait_for_function("() => document.querySelector('#fr-l0-cota').value === '21'", timeout=5000)
    pg.select_option("#fr-l0-cota", "0")
    assert pg.is_visible("#fr-l0-categorie")
    pg.select_option("#fr-l0-categorie", "serviciu_extern")
    pg.fill("#fr-l0-cantitate", "1")
    pg.fill("#fr-l0-pret_unitar", "500")
    pg.click("#fr-add-linie")
    pg.fill("#fr-l1-descriere", "Deseuri metalice")
    pg.wait_for_function("() => document.querySelector('#fr-l1-cota').value === '21'", timeout=5000)
    pg.select_option("#fr-l1-cota", "0")
    pg.select_option("#fr-l1-categorie", "taxare_inversa")
    assert pg.is_visible("#fr-c331")
    pg.select_option("#fr-c331", "deseuri")
    pg.fill("#fr-l1-pret_unitar", "100")
    pg.click("#fr-salveaza")
    pg.wait_for_timeout(500)
    assert len(trimis) == 1, trimis
    c = trimis[0]
    assert c["tert_tara"] == "DE" and c["categorie_331"] == "deseuri", c
    assert [(l["cota_tva"], l.get("categorie_tva")) for l in c["linii"]] == [(0, "serviciu_extern"), (0, "taxare_inversa")], c
    assert erori == [], erori


def test_9_cota_scoasa_de_pe_zero_goleste_categoria_iar_neplatitorul_are_cota_zero(browser):  # noqa: F811
    """Plătitorul: 0% + categorie, apoi 21% -> categoria ascunsă și golită, nu pleacă pe linie. Neplătitorul: nicio listă, cota „0%” fixă
    după denumire (CF art.310 alin.(10) lit.b — fără cerere de potrivire), nicio categorie."""
    trimis = []

    def salveaza(metoda, _c, _q, corp):
        if metoda == "POST":
            trimis.append(json.loads(corp))
        return {"id": 1}
    cereri = []
    for platitor in (True, False):
        trimis.clear()
        rute = {"/facturi/numerotare": dict(_NUMEROTARE, categorii_tva=_NUMEROTARE["categorii_tva"] if platitor else []),
                "/vector": {"platitor_tva": platitor}, "/produse/potriveste": {"ok": True, "cota": 21}, "/facturi-recurente": salveaza}
        pg, erori = _pagina(browser, rute, cereri=cereri, lat=1280, inalt=720)
        _deschide_sablonul(pg)
        pg.fill("#fr-nume", "Client SRL")
        pg.fill("#fr-l0-descriere", "Abonament mentenanta")
        if platitor:
            pg.wait_for_function("() => document.querySelector('#fr-l0-cota').value === '21'", timeout=5000)
            pg.select_option("#fr-l0-cota", "0")
            pg.select_option("#fr-l0-categorie", "scutit_cu_drept")
            pg.select_option("#fr-l0-cota", "21")
            assert pg.is_hidden("#fr-l0-categorie")
        else:
            pg.wait_for_timeout(600)
            assert pg.eval_on_selector("#fr-l0-cota", "e => [e.tagName, e.textContent.trim()]") == ["SPAN", "0%"]
            assert pg.query_selector("#fr-l0-categorie") is None
        pg.fill("#fr-l0-pret_unitar", "100")
        pg.click("#fr-salveaza")
        pg.wait_for_timeout(500)
        assert [(l["cota_tva"], l.get("categorie_tva")) for l in trimis[0]["linii"]] == [(21, None) if platitor else (0, None)], trimis
        assert trimis[0]["categorie_331"] is None
        assert erori == [], erori
        if not platitor:
            assert not [c for c in cereri if c[1].endswith("/produse/potriveste")][1:], cereri   # numai plătitorul a cerut potrivirea


# ── C109: starea ultimei emiteri pe șablon ──────────────────────────────────────────────────────────────────────────────────────────
def test_def_c109_lista_sabloanelor_arata_ultima_emitere_si_refuzul_cu_motivul(browser):  # noqa: F811
    """Lista șabloanelor: cel emis arată „ultima factură emisă: 05.10.2026”; cel refuzat de emiterea automată arată, sub el, „Emiterea
    automată refuzată la 06.11.2026:” și motivul întreg; cel nou, „nicio factură emisă încă”."""
    sab = [{"id": 1, "tert_nume": "EMIS SRL", "zi_emitere": 5, "activ": True, "moneda": "RON", "ultima_emitere": "2026-10-05",
            "ultimul_refuz": None, "ultimul_refuz_la": None, "linii": [{"cantitate": 1, "pret_unitar": 100}], "tert_tara": "RO"},
           {"id": 2, "tert_nume": "REFUZAT SRL", "zi_emitere": 5, "activ": True, "moneda": "RON", "ultima_emitere": "2026-10-05",
            "ultimul_refuz": "Firma nu e plătitoare de TVA, deci factura nu poate purta TVA.", "ultimul_refuz_la": "2026-11-06",
            "linii": [{"cantitate": 1, "pret_unitar": 100}], "tert_tara": "RO"},
           {"id": 3, "tert_nume": "NOU SRL", "zi_emitere": 5, "activ": True, "moneda": "RON", "ultima_emitere": None,
            "ultimul_refuz": None, "ultimul_refuz_la": None, "linii": [], "tert_tara": "RO"}]
    pg, erori = _pagina(browser, {"/facturi-recurente": {"sabloane": sab}}, lat=1280, inalt=720)
    pg.evaluate("""async () => { const m = await import('/static/js/ecrane/facturi_ecran.js');
      window._nav.deschide('Facturi', (c, n) => m.randeazaFacturi(c, n, 1, {})); }""")
    pg.wait_for_selector("#fac-recurente", timeout=15000)
    pg.click("#fac-recurente")
    pg.wait_for_selector(".pf-frand[data-id='3']", timeout=15000)
    txt = {i: " ".join(pg.inner_text(".pf-frand[data-id='%d'] .pf-frand-text" % i).split()) for i in (1, 2, 3)}
    # textul întreg al fiecărui rând (numele, ziua, ultima emitere, starea și, la cel refuzat, refuzul cu ziua și motivul), comparat cu `==`
    # [lotul 13, 680] plus rândul modului de emitere (șablonul fără `mod_emitere` = cel de dinainte de 680: „se emite singură”)
    assert txt == {1: "EMIS SRL ziua 5 · ultima factură emisă: 05.10.2026 · activ se emite singură",
                   2: "REFUZAT SRL ziua 5 · ultima factură emisă: 05.10.2026 · activ se emite singură Emiterea automată refuzată la "
                      "06.11.2026: Firma nu e plătitoare de TVA, deci factura nu poate purta TVA.",
                   3: "NOU SRL ziua 5 · nicio factură emisă încă · activ se emite singură"}, txt
    assert pg.eval_on_selector("#fr-refuz-2 span", "e => getComputedStyle(e).color") == pg.evaluate(
        "() => { const d = document.createElement('span'); d.style.color = 'var(--rosu)'; document.body.appendChild(d); "
        "const c = getComputedStyle(d).color; d.remove(); return c; }")
    assert erori == [], erori
