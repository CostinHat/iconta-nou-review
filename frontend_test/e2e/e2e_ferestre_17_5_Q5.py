"""Probe 17.5-Q5, exclusiv pe copia oficială de test."""
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
F7 = "F7 Preluare Test SRL"
ELIGIBIL = ':enabled:not([aria-disabled="true" i])'

def origine_proba(url):
    adresa = urlsplit(url)
    if adresa.scheme != "http" or adresa.hostname not in ("localhost", "127.0.0.1") or adresa.port != 8019:
        raise RuntimeError("Proba cere instanța de test pe loopback, portul 8019")
    return f"{adresa.scheme}://{adresa.netloc}"


def acasa(pg):
    origine = origine_proba(pg.url)
    pg.evaluate("sessionStorage.removeItem('iconta_fereastra_deschisa')")
    pg.goto(origine + "/", wait_until="domcontentloaded")
    origine_proba(pg.url)
    pg.locator("button.cab-card:has([data-cheie='firme'])").wait_for()


def firma(pg, nume, control):
    acasa(pg)
    pg.locator("button.cab-card:has([data-cheie='firme'])").click()
    pg.locator(TOP + "#opt-existente").click()
    lista = pg.locator(TOP + "#firme-lista button.firme-rand")
    lista.filter(has=pg.get_by_text(nume, exact=True)).click()
    tinta = pg.locator(TOP + control)
    tinta.wait_for(state="attached")
    grup = tinta.locator("xpath=ancestor::*[contains(concat(' ',normalize-space(@class),' '),' firme-optiuni ')][1]")
    if grup.count() and not grup.is_visible():
        pg.locator(TOP + f'button[aria-controls="{grup.get_attribute("id")}"]').click()
    tinta.click()


def import_pas(pg, nume, pas, ancora):
    firma(pg, nume, "#fa-import")
    pg.locator(TOP + "#mig-pasi").get_by_text(pas, exact=True).click()
    pg.locator(TOP + ancora).wait_for(state="attached")


STYLE = """e => {
    const nodes = [e, ...e.querySelectorAll('*')].filter(n => {
        const r = n.getBoundingClientRect();
        return r.width > 1 && r.height > 1 && n.checkVisibility({checkOpacity:true,checkVisibilityCSS:true});
    });
    const styles = nodes.map(n => getComputedStyle(n));
    return {cursor:styles.map(s => s.cursor), aspect:styles.map(s => [s.color,
       s.backgroundColor, s.backgroundImage, s.borderTopColor, s.borderRightColor,
       s.borderBottomColor, s.borderLeftColor, s.outlineStyle, s.outlineColor,
       s.boxShadow, s.filter, s.transform, s.opacity]), hover:e.matches(':hover')};
}"""

ACTIUNI = """(e, eligibil) => {
    const viz = b => b.checkVisibility({checkOpacity:true,checkVisibilityCSS:true})
                     && b.getBoundingClientRect().width > 1 && b.getBoundingClientRect().height > 1;
    const butoane = [...e.querySelectorAll('button')].filter(viz);
    const principal = b => b.matches('.fj-principal,.buton-primar');
    return {butoane: butoane.map(b => ({text:b.innerText.trim(), principal:principal(b),
              bara:!!b.closest('.fereastra-jos'), linie:b.getAttribute('data-cont'),
              id_control:b.id, disabled_nativ:b.matches(':disabled'), aria_disabled:b.getAttribute('aria-disabled'),
              activ:b.matches(eligibil),
              fond:getComputedStyle(b).backgroundColor, culoare:getComputedStyle(b).color,
              contur:getComputedStyle(b).borderTopColor, rand:b.closest('[data-linie-id]')?.dataset.linieId || null})),
            randuri:[...e.querySelectorAll('tbody[data-linie-id]')].filter(viz).map(r=>r.dataset.linieId)};
}"""


def stiluri(pg, director, eticheta):
    zona = pg.locator(TOP + "#mig-drop")
    zona.scroll_into_view_if_needed()
    neutru = zona.evaluate("""el => {
        for (const y of [2, innerHeight-2, innerHeight/2])
          for (const x of [2, innerWidth-2, innerWidth/2])
            if (!el.contains(document.elementFromPoint(x,y))) return [x,y];
        throw Error('Niciun punct neutru în viewport');
    }""")
    pg.mouse.move(*neutru)
    pg.wait_for_timeout(250)
    inainte = zona.evaluate(STYLE)
    pg.screenshot(path=str(director / (eticheta + "-repaus.png")))
    zona.hover()
    pg.wait_for_timeout(250)
    dupa = zona.evaluate(STYLE)
    pg.screenshot(path=str(director / (eticheta + "-hover.png")))
    if inainte["hover"] or not dupa["hover"]:
        raise RuntimeError("Lipsește trecerea fizică repaus→hover")
    return [inainte, dupa]


def css_observat(stil):
    if set(stil) != {"F1-1366", "F1-603", "F7-1366", "F7-603"}:
        raise ValueError("C236: configurație absentă")
    for cheie, (a, b) in stil.items():
        if a["hover"] is not False or b["hover"] is not True:
            raise ValueError(f"{cheie}: lipsește tranziția fizică de hover")
        for stare in (a, b):
            if not stare["cursor"] or not stare["aspect"] or len(stare["cursor"]) != len(stare["aspect"]):
                raise ValueError(f"{cheie}: măsuri CSS incomplete")
    return {"e.1": all(c in ("default", "auto", "text") for pereche in stil.values()
                        for stare in pereche for c in stare["cursor"]),
            "e.2": all(a["aspect"] == b["aspect"] for a, b in stil.values())}


def principal_unic(butoane, nume):
    principale = [b for b in butoane if b["principal"]]
    return len(principale) == 1 and principale[0]["bara"] and principale[0]["text"] == nume


def stoc_corect(m):
    actiuni = m["butoane"]
    des = [b for b in actiuni if b["text"] == "Descarcă gestiunea lunii"]
    return principal_unic(actiuni, "+ NIR nou") and len(des) == 1 and not des[0]["principal"]


def banca_corecta(m):
    api = m["api_id"]
    if not api or len(api) != len(set(api)) or any(x in ("", "None") for x in api):
        raise ValueError("Bancă: lista independentă de ID-uri este goală sau ambiguă")
    butoane = m["butoane"]
    linii = [b for b in butoane if b["rand"] and b["text"].startswith("Contează")]
    return (principal_unic(butoane, "Importă extras") and Counter(api) == Counter(m["randuri"])
            and Counter(b["rand"] for b in linii) == Counter(api)
            and all(b["linie"] == b["rand"] and not b["principal"] for b in linii))


def judeca(m):
    return {**css_observat(m["stil"]),
            "e.4": stoc_corect(m["stoc"]), "e.5": banca_corecta(m["banca"])}


def get_martor(pg, cale):
    # Citește lista martor din sesiunea autentificată a paginii.
    origine_proba(pg.url)
    rezultat = pg.evaluate("""async cale => {
        const token = sessionStorage.getItem('iconta_token');
        if (!token) throw Error('Lipsește sesiunea de test');
        const r = await fetch(cale,{method:'GET',redirect:'error',cache:'no-store',
          signal:AbortSignal.timeout(90000),headers:{Authorization:'Bearer '+token}});
        if (!r.ok) throw Error(cale+' HTTP '+r.status);
        return await r.json();
    }""", cale)
    return rezultat


def stabil(pg):
    pg.evaluate("() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))")


def sectiuni_exclusive(sectiuni_dom):
    # Un selector descendent include și tabelul interior în DOM-ul de pe E.
    deoparte = sectiuni_dom["bk-deoparte"]
    ids_deoparte = set(deoparte)
    return {"bk-lucru": [i for i in sectiuni_dom["bk-lucru"] if i not in ids_deoparte],
            "bk-deoparte": deoparte}


def culege_actiuni(pg, director, nume):
    banca = nume == "banca"
    firma(pg, F1, "#fa-banca" if banca else "#fa-stocuri")
    pg.locator(TOP + ("#bk-lucru" if banca else "#s-actiuni")).wait_for(state="attached")
    pg.locator(TOP + ".fereastra-jos").wait_for()
    stabil(pg)
    masura = pg.locator(TOP.strip()).evaluate(ACTIUNI, ELIGIBIL)
    if banca:
        raspuns = get_martor(pg, "/tenants/105779/banca/reconciliere")
        masura["api_id"] = [str(r["id"]) for r in raspuns["linii"]]
        masura["stare_api"] = {str(r["id"]): r["status"] for r in raspuns["linii"]}
        masura["sectiuni_dom"] = pg.locator(TOP.strip()).evaluate("""e => Object.fromEntries(
          ['bk-lucru','bk-deoparte'].map(id => [id, [...e.querySelectorAll('#'+id+' tbody[data-linie-id]')]
            .filter(r => r.checkVisibility()).map(r => r.dataset.linieId)]))""")
        masura["sectiuni"] = sectiuni_exclusive(masura["sectiuni_dom"])
    pg.screenshot(path=str(director / (nume + ".png")))
    control = "button[data-cont]" if banca else "#s-desc"
    tinta = pg.locator(TOP + control + ELIGIBIL + ":visible")
    masura["martori_activi"] = tinta.count()
    if masura["martori_activi"]:
        ales = tinta.first
        if banca:
            ids = tinta.evaluate_all("es => es.map(e=>e.getAttribute('data-cont'))")
            ales = pg.locator(TOP + 'button[data-cont="' + str(min(int(i) for i in ids)) + '"]' + ELIGIBIL + ":visible")
        ales.scroll_into_view_if_needed()
        masura["martor_vizual"] = ales.evaluate("""(b, eligibil) => ({
          id:b.getAttribute('data-cont') || b.id, text:b.innerText.trim(),
          activ:b.matches(eligibil), fond:getComputedStyle(b).backgroundColor,
          culoare:getComputedStyle(b).color, bordura:getComputedStyle(b).borderTopColor,
          perioada:b.closest('.fereastra-overlay')?.querySelector('p.pf-intro')?.innerText.split('\\n')[0] || ''
        })""", ELIGIBIL)
        if not masura["martor_vizual"]["activ"]:
            raise RuntimeError(f"{nume}: martorul a devenit inactiv înaintea capturii")
        pg.screenshot(path=str(director / (nume + "-eligibil.png")))
    return masura


def salveaza(director, nume, continut):
    (director / nume).write_text(json.dumps(continut, ensure_ascii=False, indent=2), encoding="utf-8")


def diagnostic(pg, director, nume, exc, trafic):
    from playwright.sync_api import Error as EroareBrowser
    info = {"tip": type(exc).__name__, "motiv": str(exc)[:1200], "http": trafic[-16:]}
    try:
        info["dom"] = pg.locator(TOP.strip()).evaluate_all("""es=>es.map(e=>({
          antete:[...e.querySelectorAll('thead')].map(t=>t.innerText.slice(0,180)),
          liniiBanca:e.querySelectorAll('tbody[data-linie-id]').length,
          descarcare:e.querySelectorAll('#s-desc').length,
          gol:e.querySelector('.stare-goala')?.innerText?.slice(0,180),
          mesaj:[...e.querySelectorAll('.ecran-nota')].map(n=>n.innerText.slice(0,180)),
          titlu:e.querySelector('.fir-acum')?.innerText}))""")
        pg.screenshot(path=str(director / (nume + "-eroare.png")), timeout=5000)
    except EroareBrowser as secundara:
        info["diagnostic_incomplet"] = str(secundara)[:240]
    salveaza(director, nume + "-eroare.json", info)


def test_ferestre_17_5_Q5(browser, capsys):
    from playwright.sync_api import Error as EroareBrowser
    from conftest import BAZA, CAPTURI, sesiune
    from core.ceas_proba import MOMENT_REF
    origine = origine_proba(BAZA)
    init = sesiune("dovada.71507@sesiuneab.test")
    director = Path(CAPTURI) / "17_5_Q5"
    director.mkdir(parents=True, exist_ok=True)
    masuri, verdicte, erori = {}, {}, {}
    def solduri(pg):
        stil = {}
        for nume in (F1, F7):
            for w, h in ((1366, 768), (603, 590)):
                pg.set_viewport_size({"width": w, "height": h})
                import_pas(pg, nume, "Solduri inițiale", "#mig-alege")
                cheie = f"{nume[:2]}-{w}"
                stil[cheie] = stiluri(pg, director, cheie)
                masuri["stil"] = stil
                salveaza(director, "masuri.json", masuri)
        return stil

    for nume in ("stil", "stoc", "banca"):
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        try:
            ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(init)
            pg = ctx.new_page()
            trafic = []
            def raspuns(r):
                cale = urlsplit(r.url).path
                if cale == "/tenants/105779/banca/reconciliere":
                    trafic.append([cale, r.status])
            pg.on("response", raspuns)
            try:
                pg.goto(origine + "/", wait_until="load")
                if nume == "stil":
                    masuri[nume] = solduri(pg)
                    verdicte.update(css_observat(masuri[nume]))
                else:
                    masuri[nume] = culege_actiuni(pg, director, nume)
                    if nume == "banca":
                        verdicte["e.5"] = banca_corecta(masuri[nume])
                    else:
                        verdicte["e.4"] = stoc_corect(masuri[nume])
            except (EroareBrowser, ValueError, RuntimeError, KeyError, TypeError) as exc:
                erori[nume] = type(exc).__name__
                diagnostic(pg, director, nume, exc, trafic)
            finally:
                salveaza(director, "masuri.json", masuri)
                salveaza(director, "pas_cu_pas.json", {"judecate": verdicte, "neexecutate": erori})
        finally:
            ctx.close()
    if erori:
        raise RuntimeError(f"NEEXECUTAT: {erori}; măsurările independente sunt în pas_cu_pas.json")
    assert set(verdicte) == {"e.1", "e.2", "e.4", "e.5"}
    with capsys.disabled():
        for ident, trecut in sorted(verdicte.items()):
            print(f"VERDICT {ident} {'trece' if trecut else 'pica'}", flush=True)
    assert all(verdicte.values()), verdicte
