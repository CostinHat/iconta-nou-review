from urllib.parse import urlsplit

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
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
def inchidere(pg):
    pg.set_viewport_size({"width": 1366, "height": 768})
    firma(pg, F1, "#fa-inchidere")
    pg.wait_for_function("""sel => {
        const e = document.querySelector(sel);
        const text = id => e?.querySelector(id)?.textContent.trim() || '';
        return text('#il-stare-perioada').startsWith('Luna ') &&
               text('#il-lock') && text('#il-controale') &&
               /Evidența facturilor (?:e (?:deschisă|închisă)|nu se poate închide)/.test(text('#il-facturi')) &&
               !/Nu s-au putut citi/.test(text('#il-controale'));
    }""", arg=TOP.strip())


def balanta(pg):
    pg.set_viewport_size({"width": 603, "height": 590})
    with pg.expect_response(lambda r: urlsplit(r.url).path.endswith("/balanta") and r.request.method == "GET") as resp:
        firma(pg, F1, "#fa-balanta")
    if not resp.value.ok:
        raise RuntimeError("API Balanță indisponibil")
    pg.locator(TOP + "#b-intro").wait_for()
    rows = resp.value.json()["randuri"]
    if not rows or not rows[0].get("cont") or not rows[0].get("denumire"):
        raise RuntimeError("Lipsește un cont cu denumire în balanța perioadei")
    return {"cont": str(rows[0]["cont"]), "denumire": str(rows[0]["denumire"]), "randuri": len(rows)}


def masoara(pg, pas):
    corp = pg.locator(TOP + ".fereastra-corp")
    return corp.evaluate("""(e, pas) => {
        const r = e.getBoundingClientRect();
        const afisat = n => n.checkVisibility({checkOpacity:true, checkVisibilityCSS:true}) &&
                              n.getBoundingClientRect().width > 0 && n.getBoundingClientRect().height > 0;
        const actiuni = Array.from(e.closest('.fereastra-overlay').querySelectorAll('button'))
            .filter(afisat).map(b => ({id:b.id, text:b.innerText.trim()}));
        const depasiri = [];
        for (const n of [e, ...e.querySelectorAll('*')]) {
            if (!afisat(n) || !n.clientWidth || n.scrollWidth <= n.clientWidth + 1) continue;
            if (getComputedStyle(n).overflowX !== 'visible' || n === e)
                depasiri.push({tag:n.tagName,id:n.id,latime:n.clientWidth,continut:n.scrollWidth});
        }
        const text = e.innerText;
        return {viewport:[innerWidth,innerHeight], latime:e.clientWidth, scroll_x:e.scrollWidth,
            inaltime:e.clientHeight, scroll_y:e.scrollHeight, sus:r.top, jos:r.bottom,
            actiuni, depasiri, text};
    }""", pas)


def nume_cont(pg, martor, director):
    """Citește denumirea din rândul contului sau din detaliul deschis din acel rând."""
    import json
    import re
    from playwright.sync_api import TimeoutError as Expirat

    cont = martor["cont"]
    denumire = martor["denumire"]
    corp = pg.locator(TOP + ".fereastra-corp")
    # Un rând poate fi tabelar, card cu data-cont sau element semantic de listă.
    randuri = corp.locator("tr:visible, [role=row]:visible, li:visible, article:visible, details:visible").filter(has=pg.get_by_text(cont, exact=True))
    cu_id = corp.locator('[data-cont=' + json.dumps(cont) + ']:visible')
    if cu_id.count() == 1:
        rand = cu_id
    elif randuri.count():
        rand = randuri.last
    else:
        return {"sursa": "lipsa", "cont": cont, "rand": "", "detaliu": ""}
    initial = rand.inner_text()
    proba = {"sursa": "rand", "cont": cont, "rand": initial, "detaliu": ""}
    if denumire in initial:
        return proba

    nume_actiune = re.compile(r"detali|fi[șs][aă]|deschide|^" + re.escape(cont) + r"$", re.I)
    actiuni = [rand.get_by_role("button", name=nume_actiune), rand.get_by_role("link", name=nume_actiune), rand.locator("summary:visible")]
    buton = next((a for a in actiuni if a.count() == 1 and a.is_visible() and a.is_enabled()), None)
    if buton is None:
        return proba
    controlat = buton.get_attribute("aria-controls")
    rand_vechi = rand.element_handle()
    fereastra_veche = pg.locator(TOP.strip()).element_handle()
    buton.click()
    # Pentru deschidere în aceeași listă se acceptă doar rândul inițial sau
    # zona lui aria-controls. O fereastră nouă trebuie să identifice contul.
    try:
        pg.wait_for_function("""([row, oldWindow, target, name, code, top]) => {
            const shown = e => e && e.isConnected && e.getClientRects().length && e.checkVisibility({checkVisibilityCSS:true,checkOpacity:true});
            const visibleText = e => shown(e) ? e.innerText || '' : '';
            const active = document.querySelector(top);
            if ((active?.contains(row) && visibleText(row).includes(name)) ||
                (target && visibleText(document.getElementById(target)).includes(name))) return true;
            return active && active !== oldWindow && visibleText(active).includes(code) && visibleText(active).includes(name);
        }""", arg=[rand_vechi, fereastra_veche, controlat, denumire, cont, TOP.strip()], timeout=3500)
    except Expirat:
        return proba
    if controlat:
        zona = pg.locator('[id=' + json.dumps(controlat) + ']')
        if zona.count() == 1 and zona.is_visible() and denumire in zona.inner_text():
            proba.update(sursa="controlat", detaliu=zona.inner_text())
    if proba["sursa"] == "rand" and rand_vechi.evaluate("(e,top) => e.isConnected && document.querySelector(top)?.contains(e)", TOP.strip()):
        extins = rand_vechi.inner_text()
        if denumire in extins:
            proba.update(sursa="rand_deschis", detaliu=extins)
    if proba["sursa"] == "rand":
        nou = pg.locator(TOP.strip())
        if not fereastra_veche.evaluate("(e,top) => document.querySelector(top) === e", TOP.strip()):
            proba.update(sursa="fisa", detaliu=nou.inner_text())
    if proba["sursa"] != "rand":
        pg.screenshot(path=str(director / "e.2-detaliu.png"))
    return proba


def rezultat(ident, m):
    if not (m["latime"] > 0 and m["inaltime"] > 0):
        raise ValueError("Fereastră fără dimensiuni")
    if ident == "e.1":
        if m["viewport"] != [1366, 768] or "Evidența facturilor" not in m["text"]:
            raise ValueError("Martorul Închidere lună nu este disponibil")
        return (m["scroll_y"] <= m["inaltime"] + 1 and m["sus"] >= -1 and m["jos"] <= 769
                and any(b["id"] == "il-lock" and b["text"] for b in m["actiuni"]))
    if ident != "e.2" or m["viewport"] != [603, 590] or m["martor"]["randuri"] < 1:
        raise ValueError("Martorul Balanță nu este disponibil")
    import re
    cont = re.escape(m["martor"]["cont"])
    acces = m["acces_denumire"]
    cod = re.compile(r"(?<!\w)" + cont + r"(?!\w)")
    ruta = acces["sursa"]
    den = m["martor"]["denumire"]
    nume_corect = ((ruta == "rand" and den in acces["rand"])
                   or (ruta in ("controlat", "rand_deschis") and den in acces["detaliu"])
                   or (ruta == "fisa" and cod.search(acces["detaliu"]) and den in acces["detaliu"]))
    return bool(not m["depasiri"] and m["scroll_x"] <= m["latime"] + 1
                and acces["cont"] == m["martor"]["cont"] and cod.search(acces["rand"])
                and nume_corect)


def test_ferestre_17_5_Q4(browser, capsys):
    import json
    from pathlib import Path
    from conftest import BAZA, CAPTURI, sesiune
    from core.ceas_proba import MOMENT_REF
    origine = origine_proba(BAZA)
    init = sesiune("dovada.71507@sesiuneab.test")
    dest = Path(CAPTURI) / "17_5_Q4"
    dest.mkdir(parents=True, exist_ok=True)
    masuri, verdicte, erori = {}, {}, {}
    for ident, route in (("e.1", inchidere), ("e.2", balanta)):
        ctx = browser.new_context()
        try:
            ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(init)
            pg = ctx.new_page()
            pg.goto(origine + "/", wait_until="domcontentloaded")
            martor = route(pg)
            pg.evaluate("document.fonts.ready")
            pg.evaluate("() => new Promise(ok => requestAnimationFrame(() => requestAnimationFrame(ok)))")
            m = masoara(pg, ident)
            if martor is not None:
                m["martor"] = martor
            pg.screenshot(path=str(dest / (ident + ".png")))
            if ident == "e.2":
                m["acces_denumire"] = nume_cont(pg, martor, dest)
            masuri[ident] = m
            verdicte[ident] = rezultat(ident, m)
        except Exception as exc:
            erori[ident] = type(exc).__name__ + ": " + str(exc).splitlines()[0]
        finally:
            ctx.close()
    (dest / "masuri.json").write_text(json.dumps(masuri, ensure_ascii=False, indent=2), encoding="utf-8")
    (dest / "erori.json").write_text(json.dumps(erori, ensure_ascii=False), encoding="utf-8")
    with capsys.disabled():
        for ident, trecut in verdicte.items():
            print(f"VERDICT {ident} {'trece' if trecut else 'pica'}", flush=True)
    if erori:
        raise RuntimeError(f"NEEXECUTAT: {erori}")
    assert set(verdicte) == {"e.1", "e.2"} and all(verdicte.values()), verdicte
