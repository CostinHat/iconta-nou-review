"""[17.5-F6] Probele țintite e2e ale lotului, în afara plasei fixe (rulate separat la pct. 6, pe candidat, pe copia 8019):
Cabinet 8 — secțiunea «Consultanță» a paginii cabinetului pe trei roluri (administratorul cu firmele cabinetului, asistentul cu o parte din
firme și fără drept de conducere, utilizatorul fără firme), la 1366×768 și 603×590: pliată la deschidere, desfăcută, revenirea după o
fereastră (starea în memorie) și reîncărcarea (pliată), cele două carduri, firmele distincte din titlu, cifra cardului = lista din fereastra
lui, o firmă fără nimic de făcut absentă, clic pe o firmă -> fereastra firmei direct la funcție; 502 — fereastra firmei pe două perioade cu
rezultate distincte (data transmisă la API și data, starea, valoarea afișate la fiecare schimbare); BB — bara de jos a ferestrei 502
construită de cadru, fără buton principal, și accesul la cele cinci detalii. Ceasul fixat la MOMENT_REF; capturile în CAPTURI/17_5_F6_tinte."""
import json
import re
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

TOP = ".fereastra-overlay:not(.fundal) "
ADMIN, ASISTENT, FARA_FIRME = "dovada.71507@sesiuneab.test", "dovada.71508@sesiuneab.test", "proba_reg_indpaznk@example.test"
F1, F2 = "F1 Comert Stoc SRL", "F2 Profit Amortizare SRL"
REZ = ((1366, 768), (603, 590))
SEC = ".cab-grila > section.firme-grup.cab-consultanta"
BTN = SEC + " > h3 > button.firme-grup-btn[aria-controls='fgc-consultanta']"
CHEI = ["hotarari_aga", "consultanta"]
TITLURI = ["Hotărâri AGA", "Consultanță fiscală"]
SUS = ["validat", "control", "termene", "firme", "brief", "setari"]

JS_PAGINA = """() => {
  const g = document.querySelector('.cab-grila:not([id])'); if (!g) return {grila: false};
  const sec = g.querySelector(':scope > section.cab-consultanta'), sef = g.querySelector(':scope > section.firme-grup[aria-labelledby="fg-sef"]');
  const b = sec ? sec.querySelector('h3 > button.firme-grup-btn') : null, c = document.getElementById('fgc-consultanta');
  const carduri = c ? [...c.querySelectorAll('button.cab-card')].map((x) => ({cheie: (x.querySelector('[data-cheie]') || {dataset: {}}).dataset.cheie,
    titlu: (x.querySelector('.cab-card-titlu') || {}).textContent, sinteza: ((x.querySelector('.cab-card-sinteza') || {}).textContent || '').trim(),
    vizibil: !!(x.getClientRects().length), activ: !x.disabled})) : [];
  return {grila: true, sectiune: !!sec, ascunsa: sec ? sec.hidden : null, ultima: sec ? !sec.nextElementSibling : null, parinte: sec ? sec.parentElement === g : null,
          dupaSef: sef ? sef.nextElementSibling === sec : null, sef: !!sef, titlu: b ? b.textContent.replace(/\\s+/g, ' ').trim() : null,
          expandat: b ? b.getAttribute('aria-expanded') : null, controleaza: !!(b && c && sec.contains(c)), continutAscuns: c ? c.hidden : null,
          inaltimeContinut: c ? Math.round(c.getBoundingClientRect().height) : null, carduri,
          sus: [...g.children].filter((x) => x.matches('button.cab-card')).map((x) => (x.querySelector('[data-cheie]') || {dataset: {}}).dataset.cheie),
          butoaneConsultanta: [...document.querySelectorAll('button.firme-grup-btn')].filter((x) => /^consultanță/i.test(x.textContent.trim())).length,
          cheiPagina: [...document.querySelectorAll('[data-cheie]')].map((e) => e.dataset.cheie)};
}"""
JS_LISTA = """() => {
  const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra'); if (!F) return null;
  const rows = [...F.querySelectorAll('table.ds-tabel tbody tr')].map((tr) => [...tr.querySelectorAll('td')].map((td) => td.textContent.trim()));
  return {titlu: (F.getAttribute('aria-label') || ''), randuri: rows, subsol: ((F.querySelector('.ds-tabel-subsol') || {}).textContent || '').trim(),
          gol: ((F.querySelector('.ds-tabel-gol') || {}).textContent || '').trim()};
}"""
JS_FEREASTRA = """() => { const o = [...document.querySelectorAll('.fereastra-overlay:not(.fundal)')]; const t = o[o.length - 1];
  return t ? {eticheta: (t.querySelector('.fereastra') || {getAttribute: () => ''}).getAttribute('aria-label'), antet: ((t.querySelector('.fereastra-antet') || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
              titlu: ((t.querySelector('h2.pf-titlu') || {}).textContent || '').trim(), operatie: ((t.querySelector('#op-operatie') || {}).value || null)} : null; }"""


def _pagina(browser, cont, w, h):
    from conftest import BAZA, sesiune
    from core.ceas_proba import MOMENT_REF
    from e2e_ferestre_17_5_Q5 import origine_proba
    origine_proba(BAZA)
    ctx = browser.new_context(viewport={"width": w, "height": h}, accept_downloads=True)
    ctx.clock.set_fixed_time(MOMENT_REF)
    ctx.add_init_script(sesiune(cont))
    pg = ctx.new_page()
    pg.goto(BAZA + "/", wait_until="domcontentloaded")
    return ctx, pg


def _poza(pg, nume):
    from conftest import CAPTURI
    d = Path(CAPTURI) / "17_5_F6_tinte"
    d.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(d / ("%s.png" % nume)))


def _martor(nume, date):
    from conftest import CAPTURI
    d = Path(CAPTURI) / "17_5_F6_tinte"
    d.mkdir(parents=True, exist_ok=True)
    (d / ("%s.json" % nume)).write_text(json.dumps(date, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def _acasa(pg):
    """Pagina principală proaspătă; rezumatele paginii, inclusiv ale secțiunii «Consultanță», nu mai sunt «se încarcă»."""
    from e2e_ferestre_17_5_Q5 import acasa
    acasa(pg)
    pg.wait_for_function("() => ![...document.querySelectorAll('.cab-card-sinteza')].some((e) => e.textContent.includes('se încarcă'))", timeout=30000)
    pg.wait_for_timeout(500)


def _ruta(pg):
    """Răspunsul rutei secțiunii, pe sesiunea paginii (cifrele cu care se confruntă ecranul)."""
    return pg.evaluate("""async () => { const t = sessionStorage.getItem('iconta_token') || localStorage.getItem('iconta_token');
      const r = await fetch('/cabinet/consultanta', {headers: t ? {Authorization: 'Bearer ' + t} : {}}); return {status: r.status, corp: r.ok ? await r.json() : null}; }""")


def _asteapta_la_zi(pg, limita=420):
    """Rezumatele pe firmă le calculează lucrătorul aplicației (o tură la pornire, apoi la 5 minute): proba așteaptă ca nicio firmă a
    utilizatorului să nu mai fie «în recalculare», ca să judece cifrele, nu o stare de tranziție."""
    t0 = time.time()
    while True:
        r = _ruta(pg)
        c = (r.get("corp") or {}).get("carduri") or {}
        if r["status"] == 200 and not any((x or {}).get("in_recalculare") for x in c.values()):
            return r["corp"]
        if time.time() - t0 > limita:
            pytest.fail("rezumatele secțiunii «Consultanță» au rămas «în recalculare» peste %d s: %s" % (limita, r))
        time.sleep(10)


def _n_din_sinteza(text):
    m = re.search(r"(\d+)", text or "")
    return int(m.group(1)) if m else 0


@pytest.mark.parametrize("w,h", REZ)
def test_cabinet8_administratorul_sectiunea_cardurile_si_intrarea_directa(browser, w, h):
    ctx, pg = _pagina(browser, ADMIN, w, h)
    z = "%dx%d" % (w, h)
    try:
        ruta = _asteapta_la_zi(pg)
        _acasa(pg)
        p = pg.evaluate(JS_PAGINA)
        _poza(pg, "admin_pliat_%s" % z)
        # pliată la deschidere, ultimul copil al grilei, imediat după secțiunea șefului, un singur buton «Consultanță…»
        assert p["sectiune"] and not p["ascunsa"] and p["parinte"] and p["ultima"] and p["sef"] and p["dupaSef"], p
        assert p["expandat"] == "false" and p["continutAscuns"] and p["inaltimeContinut"] == 0 and p["controleaza"], p
        assert p["butoaneConsultanta"] == 1 and p["sus"] == SUS, p
        n = ruta["firme_distincte"]
        assert n >= 1 and p["titlu"] == ("Consultanță · %d %s" % (n, "firmă" if n == 1 else "firme")), (p["titlu"], ruta)
        assert [c["cheie"] for c in p["carduri"]] == CHEI and [c["titlu"] for c in p["carduri"]] == TITLURI
        assert [p["cheiPagina"].count(k) for k in CHEI] == [1, 1], p["cheiPagina"]
        # desfăcută
        pg.click(BTN)
        pg.wait_for_selector("#fgc-consultanta:not([hidden])", state="visible", timeout=5000)
        p2 = pg.evaluate(JS_PAGINA)
        _poza(pg, "admin_deschis_%s" % z)
        assert p2["expandat"] == "true" and all(c["vizibil"] and c["activ"] and c["sinteza"] and "se încarcă" not in c["sinteza"] for c in p2["carduri"]), p2
        sint = {c["cheie"]: c["sinteza"] for c in p2["carduri"]}
        ha, ko = ruta["carduri"]["hotarari_aga"], ruta["carduri"]["consultanta"]
        assert _n_din_sinteza(sint["hotarari_aga"]) == ha["n"] and _n_din_sinteza(sint["consultanta"]) == ko["n"], (sint, ruta)
        # cardul 501: lista = cifra cardului, firma fără nimic de făcut lipsește, intrarea directă la dividend
        pg.click("#fgc-consultanta button.cab-card:has([data-cheie='hotarari_aga'])")
        pg.wait_for_selector(TOP + "table.ds-tabel, " + TOP + ".ds-tabel-gol", timeout=20000)
        l1 = pg.evaluate(JS_LISTA)
        _poza(pg, "admin_lista_hotarari_%s" % z)
        assert l1["titlu"].startswith("Hotărâri AGA") and len(l1["randuri"]) == ha["n"], (l1, ha)
        nume = [r[0].split(" · CUI")[0] for r in l1["randuri"]]
        assert "F5 SRL Salariati SRL" not in nume and "F4 PFA Sistem Real" not in nume, nume   # fără profit / partidă simplă: nu apar
        assert F1 in nume, nume
        pg.locator(TOP + "table.ds-tabel tbody tr").filter(has_text=F1).first.click()
        pg.wait_for_function("() => { const f = document.querySelector('.fereastra-overlay:not(.fundal) #op-operatie'); return !!f && f.value === 'dividend'; }",
                             timeout=20000)
        f1 = pg.evaluate(JS_FEREASTRA)
        _poza(pg, "admin_intrare_501_%s" % z)
        assert "F1 Comert Stoc" in f1["antet"] and f1["operatie"] == "dividend" and "Decontări asociați" in (f1["titlu"] + f1["eticheta"]), f1
        # revenirea: „✕” acasă -> secțiunea a rămas desfăcută (starea în memorie)
        pg.locator(TOP + "button.nav-x").last.click()
        pg.wait_for_selector(SEC, state="attached", timeout=20000)
        pg.wait_for_timeout(600)
        assert pg.evaluate(JS_PAGINA)["expandat"] == "true"
        _poza(pg, "admin_revenire_%s" % z)
        # cardul 502: lista = cifra cardului, totalul listei = economia cardului, intrarea directă în fereastra 502 a firmei
        pg.click("#fgc-consultanta button.cab-card:has([data-cheie='consultanta'])")
        pg.wait_for_selector(TOP + "table.ds-tabel, " + TOP + ".ds-tabel-gol", timeout=20000)
        l2 = pg.evaluate(JS_LISTA)
        _poza(pg, "admin_lista_consultanta_%s" % z)
        assert len(l2["randuri"]) == ko["n"], (l2, ko)
        total = sum(float(r[3].replace(".", "").replace(",", ".")) for r in l2["randuri"])
        assert abs(total - float(ko["economie"])) < 0.005, (l2, ko)
        assert ("total %s lei/an" % "{:,.2f}".format(float(ko["economie"])).replace(",", "X").replace(".", ",").replace("X", ".")) in l2["subsol"], l2["subsol"]
        assert "· %s" % ("{:,.2f}".format(float(ko["economie"])).replace(",", "X").replace(".", ",").replace("X", ".")) in sint["consultanta"], sint
        tinta = l2["randuri"][0][0].split(" · CUI")[0]
        pg.locator(TOP + "table.ds-tabel tbody tr").filter(has_text=tinta).first.click()
        pg.wait_for_selector(TOP + "[data-masura='M5']", timeout=30000)
        f2 = pg.evaluate(JS_FEREASTRA)
        _poza(pg, "admin_intrare_502_%s" % z)
        assert f2["titlu"] == "Consultanță fiscală" and tinta.split(" SRL")[0] in f2["antet"], f2
        # reîncărcarea: pliată
        _acasa(pg)
        assert pg.evaluate(JS_PAGINA)["expandat"] == "false"
        _poza(pg, "admin_reincarcare_%s" % z)
        _martor("admin_%s" % z, {"ruta": ruta, "pliat": p, "deschis": p2, "lista_501": l1, "intrare_501": f1, "lista_502": l2, "intrare_502": f2})
    finally:
        ctx.close()


@pytest.mark.parametrize("w,h", REZ)
def test_cabinet8_asistentul_vede_numai_firmele_lui_fara_drept_de_conducere(browser, w, h):
    ctx, pg = _pagina(browser, ASISTENT, w, h)
    z = "%dx%d" % (w, h)
    try:
        ruta = _asteapta_la_zi(pg)
        _acasa(pg)
        p = pg.evaluate(JS_PAGINA)
        _poza(pg, "asistent_pliat_%s" % z)
        assert ruta["firme_accesibile"] == 3, ruta
        vazute = {f["nume"] for c in ruta["carduri"].values() for f in c["firme"]}
        assert vazute <= {F1, F2, "F5 SRL Salariati SRL"}, vazute
        assert p["sectiune"] and not p["ascunsa"] and p["ultima"] and not p["sef"] and p["expandat"] == "false", p
        n = ruta["firme_distincte"]
        assert p["titlu"] == ("Consultanță · %d %s" % (n, "firmă" if n == 1 else "firme") if n else "Consultanță"), (p["titlu"], ruta)
        dist = {f["tenant_id"] for c in ruta["carduri"].values() for f in c["firme"]}
        assert n == len(dist), ruta   # aceeași firmă pe ambele carduri se numără o dată
        pg.click(BTN)
        pg.wait_for_selector("#fgc-consultanta:not([hidden])", state="visible", timeout=5000)
        p2 = pg.evaluate(JS_PAGINA)
        _poza(pg, "asistent_deschis_%s" % z)
        assert [c["cheie"] for c in p2["carduri"]] == CHEI and all(c["vizibil"] and c["sinteza"] for c in p2["carduri"]), p2
        pg.click("#fgc-consultanta button.cab-card:has([data-cheie='consultanta'])")
        pg.wait_for_selector(TOP + "table.ds-tabel, " + TOP + ".ds-tabel-gol", timeout=20000)
        l2 = pg.evaluate(JS_LISTA)
        _poza(pg, "asistent_lista_consultanta_%s" % z)
        assert len(l2["randuri"]) == ruta["carduri"]["consultanta"]["n"] and all(r[0].split(" · CUI")[0] in vazute for r in l2["randuri"]), l2
        pg.locator(TOP + "button.nav-x").last.click()
        pg.wait_for_selector(SEC, state="attached", timeout=20000)
        pg.wait_for_timeout(600)
        assert pg.evaluate(JS_PAGINA)["expandat"] == "true"
        _acasa(pg)
        assert pg.evaluate(JS_PAGINA)["expandat"] == "false"
        _martor("asistent_%s" % z, {"ruta": ruta, "pliat": p, "deschis": p2, "lista_502": l2})
    finally:
        ctx.close()


@pytest.mark.parametrize("w,h", REZ)
def test_cabinet8_utilizatorul_fara_firme_nu_vede_sectiunea(browser, w, h):
    ctx, pg = _pagina(browser, FARA_FIRME, w, h)
    z = "%dx%d" % (w, h)
    try:
        ruta = _ruta(pg)
        _acasa(pg)
        pg.wait_for_function("() => !document.querySelector('.cab-grila > section.cab-consultanta')", timeout=20000)
        p = pg.evaluate(JS_PAGINA)
        _poza(pg, "fara_firme_%s" % z)
        assert ruta["status"] == 200 and ruta["corp"]["firme_accesibile"] == 0, ruta
        assert p["grila"] and not p["sectiune"] and p["butoaneConsultanta"] == 0 and not any(k in p["cheiPagina"] for k in CHEI), p
        _acasa(pg)
        assert not pg.evaluate(JS_PAGINA)["sectiune"]
        _martor("fara_firme_%s" % z, {"ruta": ruta, "pagina": p})
    finally:
        ctx.close()


def _consultanta_f1(pg):
    from e2e_ferestre_17_5_Q5 import firma
    firma(pg, F1, "#fa-consultanta")
    pg.wait_for_selector(TOP + "[data-masura='M5']", timeout=30000)


def _masuri(pg):
    return pg.evaluate("""() => [...document.querySelectorAll('.fereastra-overlay:not(.fundal) [data-masura]')].map((m) => ({cod: m.dataset.masura,
      stare: (m.querySelector('[data-masura-stare]') || {}).textContent, suma: ((m.querySelector('.cs-suma-valoare') || {}).textContent || null),
      motiv: ((m.querySelector('[data-masura-motiv]') || {}).textContent || null)}))""")


@pytest.mark.parametrize("w,h", REZ)
def test_502_doua_perioade_data_ceruta_si_rezultatele_afisate(browser, w, h):
    """F1 (micro, salariați): la 03.11.2026 M2 «Se aplică» cu suma ei; la 31.12.2025 M2 «Nu se aplică» (niciun salariat activ la acea dată)
    și M4 «Lipsesc date — temei neverificat» (plafonul micro al anului 2025 nu e în registrul datat). Fiecare schimbare cere API-ul cu data
    aleasă, iar fereastra arată data primită."""
    ctx, pg = _pagina(browser, ADMIN, w, h)
    z = "%dx%d" % (w, h)
    cereri = []
    pg.on("request", lambda r: cereri.append(r.url) if "/consultanta-fiscala" in r.url else None)
    try:
        _consultanta_f1(pg)
        implicit = {"data": pg.input_value(TOP + "#cs-data"), "afisat": pg.inner_text(TOP + "#cs-data-afisata")}
        assert "data" not in parse_qs(urlsplit(cereri[-1]).query), cereri   # la deschidere: ziua serverului, fără dată cerută
        y, m, d = implicit["data"].split("-")
        assert implicit["afisat"] == "%s.%s.%s" % (d, m, y), implicit

        def la(data):
            n0 = len(cereri)
            pg.fill(TOP + "#cs-data", data)
            pg.dispatch_event(TOP + "#cs-data", "change")
            y2, m2, d2 = data.split("-")
            pg.wait_for_function("(t) => (document.querySelector('.fereastra-overlay:not(.fundal) #cs-data-afisata') || {}).textContent === t",
                                 arg="%s.%s.%s" % (d2, m2, y2), timeout=30000)
            pg.wait_for_selector(TOP + "[data-masura='M5']", timeout=30000)
            assert len(cereri) == n0 + 1 and parse_qs(urlsplit(cereri[-1]).query).get("data") == [data], cereri
            return {"data": pg.input_value(TOP + "#cs-data"), "afisat": pg.inner_text(TOP + "#cs-data-afisata"), "masuri": _masuri(pg)}
        a = la("2026-11-03")
        _poza(pg, "502_perioada_a_%s" % z)
        st = {m["cod"]: m for m in a["masuri"]}
        assert [m["cod"] for m in a["masuri"]] == ["M1", "M2", "M3", "M4", "M5"]
        assert st["M2"]["stare"] == "Se aplică" and st["M2"]["suma"] and st["M4"]["stare"] == "Lipsesc date", st
        b = la("2025-12-31")
        _poza(pg, "502_perioada_b_%s" % z)
        sb = {m["cod"]: m for m in b["masuri"]}
        assert sb["M2"]["stare"] == "Nu se aplică" and sb["M4"]["stare"] == "Lipsesc date — temei neverificat", sb
        assert [st[k]["stare"] for k in ("M2", "M4")] != [sb[k]["stare"] for k in ("M2", "M4")]
        c = la("2026-11-03")
        assert c["masuri"] == a["masuri"], c
        _martor("502_perioade_%s" % z, {"implicit": implicit, "a": a, "b": b, "revenire": c, "cereri": cereri})
    finally:
        ctx.close()


@pytest.mark.parametrize("w,h", REZ)
def test_bb_fereastra_502_bara_fara_principal_si_cele_cinci_detalii(browser, w, h):
    """BB (comanda F6 pct.3): fereastra «Consultanță fiscală» e de consultare — bara de jos construită de cadru există și nu are buton
    principal; fiecare dintre cele cinci detalii se deschide și se închide, iar conținutul lui ajunge în vedere."""
    ctx, pg = _pagina(browser, ADMIN, w, h)
    z = "%dx%d" % (w, h)
    try:
        _consultanta_f1(pg)
        bara = pg.evaluate("""() => { const F = document.querySelector('.fereastra-overlay:not(.fundal) .fereastra');
          const j = F && F.querySelector('.fereastra-jos'); return {bara: !!j, principal: j ? j.querySelectorAll('.fj-principal, .buton-primar').length : null}; }""")
        assert bara["bara"] and bara["principal"] == 0, bara
        det = []
        for cod in ("M1", "M2", "M3", "M4", "M5"):
            btn = pg.locator(TOP + "[data-masura='%s'] .cs-det-btn" % cod)
            btn.scroll_into_view_if_needed()
            btn.click()
            corp = pg.locator(TOP + "[data-masura='%s'] .cs-detalii" % cod)
            corp.wait_for(state="visible", timeout=5000)
            corp.scroll_into_view_if_needed()
            vizibil = corp.is_visible() and pg.evaluate("(e) => { const r = e.getBoundingClientRect(); return r.height > 0 && r.top < innerHeight; }",
                                                        corp.element_handle())
            _poza(pg, "502_detalii_%s_%s" % (cod, z))
            btn.scroll_into_view_if_needed()
            btn.click()
            corp.wait_for(state="hidden", timeout=5000)
            det.append({"cod": cod, "deschis_vizibil": vizibil, "inchis": not corp.is_visible()})
        assert all(d["deschis_vizibil"] and d["inchis"] for d in det), det
        _martor("bb_502_%s" % z, {"bara": bara, "detalii": det})
    finally:
        ctx.close()
