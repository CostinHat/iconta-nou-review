"""17.5-Q. Probe de produs. Toate interacțiunile au loc pe copia de test."""
import re
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeout

from conftest import BAZA, CAPTURI, sesiune
import e2e_lot13_migr
import e2e_lot91
from core.ceas_proba import DATA_REF, MOMENT_REF

TOP = ".fereastra-overlay:not(.fundal) "
F1 = "F1 Comert Stoc SRL"
F7 = "F7 Preluare Test SRL"
F1_ID = 105779
F7_ID = 105787
CARD = "#mig-carduri button.card-rezumat[data-card='cum-balanta']"
GRUP = "Datorate înainte de preluarea în iConta.eu"


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


# Ansamblul vizibil este intersecția ferestrei cu viewportul și cu toți
# strămoșii care decupează. Hit-testul exclude o bară fixă peste primul rând.
JS_GEOMETRIE = """el => {
  const r = el.getBoundingClientRect();
  let sus = 0, jos = innerHeight, stanga = 0, dreapta = innerWidth;
  for (let p = el.parentElement; p; p = p.parentElement) {
    const b = p.getBoundingClientRect(), s = getComputedStyle(p);
    if (p.matches('.fereastra') || /auto|scroll|hidden|clip/.test(s.overflowY)) {
      sus = Math.max(sus, b.top + p.clientTop);
      jos = Math.min(jos, b.top + p.clientTop + p.clientHeight);
    }
    if (p.matches('.fereastra') || /auto|scroll|hidden|clip/.test(s.overflowX)) {
      stanga = Math.max(stanga, b.left + p.clientLeft);
      dreapta = Math.min(dreapta, b.left + p.clientLeft + p.clientWidth);
    }
  }
  const left = Math.max(stanga, r.left), right = Math.min(dreapta, r.right);
  const linie = Math.min(16, r.height);
  const atins = document.elementFromPoint((left + right) / 2, r.top + linie / 2);
  const vizibil = right > left && linie > 0 && r.top >= sus - 1 &&
    r.top + linie <= jos + 1 && !!atins && el.contains(atins);
  return {sus, jos, top: r.top, inaltime: r.height, vizibil};
}"""


def audit(pg):
    import_pas(pg, F7, "Audit de preluare", "#cf-audit-run")
    origine = origine_proba(pg.url)
    cale = f"{origine}/control-fiscal/{F7_ID}/audit-preluare"
    buton = pg.locator(TOP + "#cf-audit-run")
    # Istoricul de după POST este cel care randează raportul. Înregistrarea
    # așteptării după răspunsul POST ar putea rata un răspuns local rapid.
    pg.wait_for_function("""() => {
      const b = document.querySelector('.fereastra-overlay:not(.fundal) #cf-audit-run');
      return b && !b.disabled;
    }""")
    cereri = []

    def retine(req):
        if req.url == cale and req.method == "POST":
            cereri.append(req)
        elif cereri and req.url == cale + "/istoric" and req.method == "GET":
            cereri.append(req)

    pg.on("request", retine)
    try:
        with pg.expect_response(lambda r: r.request in cereri[1:], timeout=90000) as istoric:
            with pg.expect_response(lambda r: r.url == cale and r.request.method == "POST", timeout=90000) as raspuns:
                buton.click()
            if not raspuns.value.ok:
                raise RuntimeError(f"POST audit F7 HTTP {raspuns.value.status}")
        if not istoric.value.ok or not (istoric.value.json().get("primul") or {}).get("audit"):
            raise RuntimeError(f"Istoric fără raport de audit F7, HTTP {istoric.value.status}")
    finally:
        pg.remove_listener("request", retine)
    pg.wait_for_function("""() => {
      const s = '.fereastra-overlay:not(.fundal) ';
      return document.querySelector(s + '#cf-audit-run')?.textContent.trim() === 'Rerulează auditul'
        && !!document.querySelector(s + '#cf-audit-istoric')?.textContent.trim();
    }""", timeout=60000)
    raport = pg.locator(TOP + "#cf-audit-istoric")
    # După randare, urmărește poziția până la stabilizare, inclusiv scroll lin.
    raport.evaluate("""async el => {
      let anterior, stabil = 0;
      for (let i=0; i<120; ++i) {
        await new Promise(requestAnimationFrame);
        const t = el.getBoundingClientRect().top;
        stabil = anterior !== undefined && Math.abs(t-anterior)<0.25 ? stabil+1 : 0;
        if (stabil >= 6) return;
        anterior = t;
      }
      throw Error('poziția raportului nu s-a stabilizat');
    }""")
    return raport, raport.evaluate(JS_GEOMETRIE)


def declaratii(pg):
    firma(pg, F1, "#fa-declaratii")
    pg.locator(TOP + "#dec-tip option[data-an]").first.wait_for(state="attached")


def deschide_d110(pg):
    pg.locator(TOP + "li.ds-lista-rand").filter(has_text=re.compile(r"\bD110\b", re.I)).first.click()
    pg.locator(TOP + "#dec-continua").click()
    pg.locator(TOP + "#d110-cod").wait_for(state="attached")

CODURI = ['602', '604', '605', '606', '607', '608', '611', '619', '621', '622', '623', '625', '626', '627', '628', '629', '631', '632', '633', '634', '635', '636', '637', '638', '639', '640', '641', '642', '690']
TEXT_EXPLICATIE = 'Din ea se iau soldurile finale și, dacă le are, soldurile de la 1 ianuarie și rulajele anului (sold inițial și sume precedente, cu toate conturile care au rulaj); fără ele, ecranul spune ce lipsește. Debitul total trebuie să fie egal cu creditul total. Analiticele din balanță (de exemplu 4111.01, 401.00012) se adaugă în planul de conturi, sub sinteticul lor; un cont care nu există în planul de conturi al normei firmei e respins, cu motivul. Un sold pe partea opusă funcțiunii contului (de exemplu 5121 creditor) se semnalează pe rând.'
MARTORI_D110 = {'621': '621 — Impozit pe veniturile din jocuri de noroc', '638': '638 — Impozit pe veniturile obținute la jocuri de noroc practicate în România de persoane fizice nerezidente', '602': '602 — Impozit pe veniturile din salarii'}


def get(pg, cale):
    origine_proba(pg.url)
    status, body = pg.evaluate("""async cale => {
      const r = await fetch(cale, {redirect: "error", headers: {
        Authorization: "Bearer " + sessionStorage.getItem("iconta_token")}});
      return [r.status, await r.json()];
    }""", cale)
    if status != 200 or not isinstance(body, dict):
        raise RuntimeError(f"GET {cale}: HTTP {status} / format")
    return body


def principal(pg, text):
    controale = pg.locator(TOP + ".fj-butoane .fj-principal:visible")
    assert controale.all_inner_texts() == [text], controale.all_inner_texts()


def balanta(pg):
    cazuri = [(F1, F1_ID, None), (F7, F7_ID, "2026-09-30")]
    for nume, tid, data in cazuri:
        sursa = get(pg, f"/tenants/{tid}/solduri")
        if not sursa.get("are_solduri") or "data_referinta" not in sursa or sursa["data_referinta"] != data:
            raise RuntimeError(f"Martor {nume} absent sau dată de referință schimbată")
    for nume, tid, data in cazuri:
        import_pas(pg, nume, "Solduri inițiale", "#mig-exista")
        if data:
            luna = date.fromisoformat(data) + timedelta(days=1)
        else:
            luna = DATA_REF.replace(day=1) - timedelta(days=1)
            perioade = get(pg, f"/tenants/{tid}/perioade-blocate")["blocate"]
            if any((p["an"], p["luna"]) == (luna.year, luna.month) for p in perioade):
                luna = DATA_REF
        principal(pg, "Încarcă balanța")
        rand = pg.locator(TOP + "#mig-exista")
        assert rand.inner_text().startswith("Există deja:"), nume
        buton = rand.get_by_role("button", name="Deschide Balanța de verificare", exact=True)
        assert buton.count() == 1 and buton.is_visible(), f"{nume}: buton în rând"
        cale = f"/tenants/{tid}/balanta"
        with pg.expect_response(lambda r: urlsplit(r.url).path == cale and r.request.method == "GET") as raspuns:
            buton.click()
        if not raspuns.value.ok:
            raise RuntimeError(f"Balanța {nume}, HTTP {raspuns.value.status}")
        q = parse_qs(urlsplit(raspuns.value.url).query)
        assert q.get("an") == [str(luna.year)] and q.get("luna") == [str(luna.month)], (nume, q)
        intro = pg.locator(TOP + "#b-intro")
        intro.wait_for()
        assert f"{luna.month:02}/{luna.year}" in intro.inner_text(), (nume, intro.inner_text())
        pg.locator(TOP + ".nav-inapoi:visible").click()
        pg.locator(TOP + "#mig-alege").wait_for()
        print(f"MASURA AC088 {nume}: {luna.year}-{luna.month:02}")


def explicatie(pg):
    import_pas(pg, F1, "Solduri inițiale", "#mig-exista")
    assert pg.locator(TOP + "details#mig-cum-balanta").count() == 0, "explicație în details"
    card = pg.locator(TOP + CARD)
    assert card.count() == 1 and card.is_visible(), "cardul explicației"
    assert "Ce se citește din balanță" in card.inner_text()
    card.click()
    continut = pg.locator(TOP + "#mig-cum-balanta")
    continut.wait_for()
    assert " ".join(continut.inner_text().split()) == TEXT_EXPLICATIE, "textul explicației"
    pg.locator(TOP + ".nav-inapoi:visible").click()
    pg.locator(TOP + "#mig-alege").wait_for()


def raport(pg):
    cale = f"{origine_proba(pg.url)}/control-fiscal/{F7_ID}/audit-preluare"
    defasaje = []
    def intarzie_post(route):
        if route.request.method != "POST":
            route.continue_()
            return
        if defasaje:
            defasaje.append(None)
            route.abort()
            return
        t0 = pg.evaluate("Date.now()")
        sleep(3.2)
        defasaje.append(pg.evaluate("Date.now()") - t0)
        route.continue_()
    pg.route(cale, intarzie_post)
    try:
        _, masura = audit(pg)
    finally:
        pg.unroute(cale, intarzie_post)
    if len(defasaje) != 1 or defasaje[0] <= 3000:
        raise RuntimeError(f"Martor temporal AC093 nevalid: {defasaje}")
    print("MASURA AC093", masura, "întârziere POST (ms)", defasaje[0])
    assert masura["vizibil"], masura
    principal(pg, "Rerulează auditul")


def etichete(pg):
    declaratii(pg)
    date_api = get(pg, f"/declaratii/tipuri?tenant_id={F1_ID}")
    randuri = [d for d in date_api["datorate"]
               if d["tip"] in date_api["tipuri"] and not date_api.get("neaplicabile", {}).get(d["tip"])]
    if not any(d.get("inainte_de_preluare") for d in randuri):
        raise RuntimeError("Lipsește martorul anterior preluării din sursă")
    randuri_dom = pg.locator(TOP + "#dec-tip option[data-an]").evaluate_all("""opts => opts.map(o =>
      [o.value,+o.dataset.an,+o.dataset.luna,o.dataset.motiv,o.textContent.trim(),o.parentElement.dataset.titlu])""")
    def cheie(d):
        return (d["tip"], int(d["an"]), int(d.get("luna") or 0))
    observate = {tuple(r[:3]): r[3:] for r in randuri_dom}
    assert len(randuri_dom) == len(observate) == len(randuri) and set(observate) == {cheie(d) for d in randuri}
    # Piesa DS ascunde selectul nativ. Verificăm și motivul desenat în lista vizibilă.
    surse = pg.locator(TOP + "#dec-tip option[data-an]").evaluate_all(
        "opts => opts.map(o => [o.dataset.nume, o.dataset.motiv || ''])")
    vizibile = pg.locator(TOP + "#dec-tip + .ds-lista li.ds-lista-rand:visible").evaluate_all("""randuri => randuri.map(r =>
      [r.querySelector('.ds-lista-nume').innerText.trim(), r.querySelector('.ds-lista-motiv').innerText.trim()])""")
    necesare = Counter(tuple(r) for r in surse)
    afisate = Counter(tuple(r) for r in vizibile)
    assert not (necesare - afisate), f"lipsesc din lista vizibilă: {necesare - afisate}"
    for d in randuri:
        motiv, text, grup = observate[cheie(d)]
        if d.get("inainte_de_preluare"):
            assert grup == GRUP and motiv == "înainte de preluare", (cheie(d), motiv, grup)
            assert "restanță" not in text.casefold() and "termen de depunere" in text and text.endswith("· înainte de preluare"), text
        elif d.get("restanta"):
            assert grup == "Datorate acum" and motiv == "restanță" and "restanță — termenul a fost" in text, text
        else:
            assert grup == "Datorate acum" and not motiv and "termen de depunere" in text and "restanță" not in text.casefold(), text


def optiuni(pg):
    return pg.locator(TOP + "#d110-cod option").evaluate_all(
        "opts => opts.filter(o => o.value).map(o => [o.value,o.textContent.trim()])")


def d110(pg):
    declaratii(pg)
    d = get(pg, f"/declaratii/tipuri?tenant_id={F1_ID}")
    deschide_d110(pg)
    assert "obligatii_d110" in d, "cheia din răspunsul HTTP"
    sursa = d["obligatii_d110"]
    assert [r["cod"] for r in sursa] == CODURI, "29 coduri în ordine"
    asteptate = [[r["cod"], f'{r["cod"]} — {r["denumire"]}'] for r in sursa]
    assert optiuni(pg) == asteptate, "ordinea, valorile sau denumirile din listă"
    for cod, eticheta in MARTORI_D110.items():
        assert dict(asteptate)[cod] == eticheta
    camp = pg.locator(TOP + "#d110-cod")
    latime = camp.evaluate("e => e.closest('label').getBoundingClientRect().width")
    assert abs(latime - 340) <= 1, latime
    camp.select_option("621")
    pg.locator(TOP + "#d110-dat").fill("10")
    pg.locator(TOP + "#d110-rest").fill("5")
    pg.locator(TOP + "#d110-add").click()
    descriere = pg.locator(TOP + ".dec-man-rand .dec-recl-desc").inner_text()
    assert descriere.startswith(MARTORI_D110["621"] + " · datorat") and "reținut" in descriere, descriere
    # Simulează exclusiv absența cheii noi în citirea GET; identic în rest.
    pattern = re.compile(r"/declaratii/tipuri\?tenant_id=105779$")
    count = []
    def raspuns_vechi(route):
        real = route.fetch()
        if not real.ok:
            raise RuntimeError(f"GET pentru compatibilitate: {real.status}")
        vechi = real.json()
        del vechi["obligatii_d110"]
        count.append(1)
        route.fulfill(response=real, json=vechi)
    pg.route(pattern, raspuns_vechi)
    try:
        declaratii(pg)
        deschide_d110(pg)
        assert count and optiuni(pg) == [[c, c] for c in CODURI], "compatibilitatea cu răspunsul vechi"
    finally:
        pg.unroute(pattern, raspuns_vechi)


def captura_ecran(pg, nume):
    director = Path(CAPTURI)
    director.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(director / f"17_5_Q_{nume}.png"))


def solduri_alegere(pg, nume, dimensiune):
    pg.set_viewport_size(dimensiune)
    import_pas(pg, nume, "Solduri inițiale", "#mig-file")
    if pg.evaluate("document.visibilityState") != "visible":
        raise RuntimeError("Fereastra Solduri inițiale nu este în prim-plan")
    captura_ecran(pg, f"F084_{nume.split()[0]}_{dimensiune['width']}x{dimensiune['height']}")
    top = pg.locator(TOP.strip())
    principal(pg, "Încarcă balanța")
    nume_actiune = top.get_by_text("Încarcă balanța", exact=True).all()
    assert sum(el.is_visible() for el in nume_actiune) == 1, "titlul de încărcare se repetă în fereastră"
    camp = top.locator('#mig-file[type="file"]')
    assert camp.count() == 1, "câmpul pentru balanță lipsește sau este dublat"
    buton = top.locator(".fereastra-jos #mig-alege")
    assert buton.count() == 1 and buton.is_visible() and buton.is_enabled(), "acțiunea din bară"
    try:
        with pg.expect_file_chooser(timeout=3000) as alegere:
            if dimensiune["width"] == 603:
                buton.focus()
                buton.press("Enter")
            else:
                buton.click()
    except PlaywrightTimeout as exc:
        raise AssertionError("acțiunea vizibilă din bară nu a deschis selectorul de fișiere") from exc
    assert alegere.value.element.get_attribute("id") == "mig-file", "butonul deschide alt câmp"
    # Niciun fișier ales. Verificăm și activarea unui label redenumit sau a unei zone cu handler.
    zona = top.locator("#mig-drop")
    labeluri = top.locator('label[for="mig-file"], label:has(#mig-file)')
    assert not any(el.is_visible() for el in labeluri.all()), "eticheta din corp activează același input"
    if zona.count() and zona.is_visible():
        deschideri = []
        def retine(alegere):
            deschideri.append(alegere)
        pg.on("filechooser", retine)
        try:
            zona.click()
            pg.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
            assert not deschideri, "zona din corp deschide încă un selector de fișiere"
        finally:
            pg.remove_listener("filechooser", retine)


def d301_control_f2(pg):
    nume = "F2 Profit Amortizare SRL"
    motiv = "firma e plătitoare de TVA (D301 e pentru neînregistrați în scopuri de TVA)"
    firme = [t for t in get(pg, "/tenants")["tenants"]
             if t.get("nume") == nume and str(t.get("cui")) == "403000015"]
    if len(firme) != 1:
        raise RuntimeError("Lipsește martorul F2 cu CUI 403000015")
    cale = f"/control-fiscal/{firme[0]['id']}"
    surse = [x for x in get(pg, cale)["neaplicabile"] if str(x.get("tip")).upper() == "D301"]
    if len(surse) != 1 or motiv not in (surse[0].get("motiv") or ""):
        raise RuntimeError("Martorul D301 cu motivul fiscal așteptat lipsește din sursă")
    with pg.expect_response(lambda r: urlsplit(r.url).path == cale and r.request.method == "GET") as raspuns:
        firma(pg, nume, "#fa-control")
    if not raspuns.value.ok:
        raise RuntimeError(f"Control fiscal F2 HTTP {raspuns.value.status}")
    pg.locator(TOP + ".cf-stare-mare").wait_for()
    if pg.evaluate("document.visibilityState") != "visible":
        raise RuntimeError("Fereastra Control fiscal F2 nu este în prim-plan")
    sectiune = pg.locator(TOP + "section.cf-grup").filter(
        has=pg.get_by_role("heading", name=re.compile(r"^Nu se datorează\s*\(")))
    assert sectiune.count() == 1, "grupul «Nu se datorează» lipsește sau este dublat"
    rand = sectiune.locator(".cf-decl .ds-semnal-text").filter(has_text=re.compile(r"\bD301\b"))
    assert rand.count() == 1 and rand.is_visible(), "rândul D301 lipsește sau este dublat"
    rand.scroll_into_view_if_needed()
    captura_ecran(pg, "749_1_Control_fiscal_F2")
    asteptat = "D301 — nu se datorează — " + motiv
    assert " ".join(rand.inner_text().split()) == asteptat, rand.inner_text()
    titlu = rand.get_attribute("title")
    assert titlu is None or " ".join(titlu.split()) == asteptat, titlu


def observa(pg, masurari):
    defecte = []
    for nume, proba in masurari:
        try:
            proba(pg)
        except AssertionError as eroare:
            defecte.append(f"{nume}: {eroare}")
            print(f"MASURA {nume} pica: {eroare}")
        else:
            print(f"MASURA {nume} trece")
    assert not defecte, " | ".join(defecte)


def solduri_complete(pg):
    dimensiuni = [(1366, 768), (603, 590)]
    masurari = []
    for nume in (F1, F7):
        for w, h in dimensiuni:
            def proba(pagina, firma_test=nume, latime=w, inaltime=h):
                solduri_alegere(pagina, firma_test, {"width": latime, "height": inaltime})
            masurari.append((f"F084 {nume} {w}x{h}", proba))
    def navigare(pagina):
        pagina.set_viewport_size({"width": 1366, "height": 768})
        balanta(pagina)
    masurari.append(("AC088", navigare))
    try:
        observa(pg, masurari)
    finally:
        pg.set_viewport_size({"width": 1366, "height": 768})


def etichete_complete(pg):
    observa(pg, [("749.1", d301_control_f2), ("AC104", etichete)])


def test_ferestre_17_5_Q(browser, capsys):
    origine = origine_proba(BAZA)
    # Pregătirea contului este precondiție; o autentificare eșuată nu este verdict de produs.
    initializare = sesiune("dovada.71507@sesiuneab.test")
    verdicte, tehnice = {}, []
    for ident, proba in [("e.1", solduri_complete), ("e.2", explicatie), ("e.3", raport), ("e.4", etichete_complete), ("e.5", d110)]:
        ctx = browser.new_context(viewport={"width": 1366, "height": 768})
        try:
            if ident == "e.3":
                ctx.clock.install(time=MOMENT_REF)
            else:
                ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(initializare)
            pg = ctx.new_page()
            pg.goto(origine + "/")
            with capsys.disabled():
                proba(pg)
        except AssertionError as exc:
            verdicte[ident] = ("pica", str(exc).splitlines()[0] if str(exc) else "aserțiune")
        except (PlaywrightError, RuntimeError, KeyError, TypeError, ValueError) as exc:
            tehnice.append((ident, type(exc).__name__, str(exc).splitlines()[:1]))
        else:
            verdicte[ident] = ("trece", "observat")
        finally:
            ctx.close()
    assert not tehnice, f"NEJUDECABIL — mediu/navigare/date: {tehnice}"
    with capsys.disabled():
        for ident, (stare, motiv) in verdicte.items():
            print(f"MASURA {ident} {motiv}", flush=True)
            print(f"VERDICT {ident} {stare}", flush=True)
    assert len(verdicte) == 5 and all(v[0] == "trece" for v in verdicte.values()), verdicte

# Pytest înregistrează sub aceste nume fixture-urile suitelor originale.
firma_667 = e2e_lot13_migr.firma
firma_srl = e2e_lot91.firma_srl

# Pytest raportează separat fiecare delegare și execută întregul corp istoric.
def test_q_poarta_667(patron, firma_667):
    assert firma_667["tenant_id"] > 0, "fixture-ul 667 nu a creat firma de test"
    e2e_lot13_migr.test_def_667_rezumatul_lipit_al_balantei_e_mic_si_nu_acopera_tabelul(patron, firma_667)


def test_q_poarta_392(patron, firma_srl):
    assert firma_srl["tenant_id"] > 0, "fixture-ul 392 nu a creat firma de test"
    e2e_lot91.test_def_392_textul_spune_respingerea_si_5121_creditor_e_semnalat(patron, firma_srl)
