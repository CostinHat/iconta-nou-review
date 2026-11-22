"""17.5-Q. Parcurs oficial al celor 12 aserțiuni. API de intrare: ruleaza(pagina, ctx)."""
import verifica_pas as VP
import re
from urllib.parse import urlsplit


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


def in_cadru(element):
    element.scroll_into_view_if_needed()
    # Verifică decuparea și acoperirea, inclusiv la ambele capete ale unui text lung.
    bun = element.evaluate("""el => {
      const r = el.getBoundingClientRect();
      if (r.width < 4 || r.height < 4) return false;
      const cx = (r.left + r.right) / 2, cy = (r.top + r.bottom) / 2;
      return [[cx, r.top + 2], [cx, r.bottom - 2], [r.left + 2, cy], [r.right - 2, cy]]
        .every(([x, y]) => el.contains(document.elementFromPoint(x, y)));
    }""")
    if not bun:
        raise RuntimeError("Martorul vizual este decupat sau acoperit")


def martor_declaratie(pg):
    select = pg.locator(TOP + "#dec-tip")
    sursa = select.locator(f"optgroup[data-titlu='{GRUP}'] option[value='d100'][data-an='2025'][data-luna='12']")
    nume = sursa.get_attribute("data-nume")
    if not nume:
        raise RuntimeError("Lipsește martorul D100 decembrie 2025")
    lista = pg.locator(TOP + "#dec-tip + .ds-lista")
    lista.get_by_role("searchbox").fill(nume)
    # Lista DS desenează titlul și rândurile ca frați.
    titlu = lista.locator("li.ds-lista-grup").filter(has_text=re.compile("^" + re.escape(GRUP) + "$"))
    rand = titlu.locator("xpath=following-sibling::li[1]")
    if rand.locator(".ds-lista-nume").inner_text().strip() != nume:
        raise RuntimeError("Rândul vizibil nu aparține martorului D100")
    in_cadru(rand)
    in_cadru(titlu)
    if not rand.evaluate("e => e.contains(document.elementFromPoint(e.getBoundingClientRect().x + 4, e.getBoundingClientRect().bottom - 3))"):
        raise RuntimeError("Rândul D100 a ieșit din cadru după poziționarea titlului")
    return lista


def martor_cod(pg, cod):
    lista = pg.locator(TOP + "#d110-cod + .ds-lista")
    buton = lista.locator("button.ds-lista-titlu")
    if buton.get_attribute("aria-expanded") == "false":
        buton.click()
    lista.get_by_role("searchbox").fill(cod)
    nume = lista.locator("li.ds-lista-rand .ds-lista-nume").filter(
        has_text=re.compile(r"^" + re.escape(cod) + r"(?:\s|$)"))
    nume.wait_for()
    in_cadru(nume)


def ruleaza(pagina, ctx):
    def verifica(pas):
        rezultate, verdict = VP.verifica_pagina(pagina, ctx.lot, pas, ctx.parcurgere,
                                                 ctx.verificator, ctx.pasi_json, ctx.csv)
        print(f"[parcurs] {pas} {verdict} {rezultate}")
        if verdict == "neexecutat":
            raise RuntimeError(f"Oracol neexecutat la {pas}: {rezultate}")

    acasa(pagina)
    verifica("implicit")
    import_pas(pagina, F1, "Solduri inițiale", "#mig-exista")
    verifica("solduri")
    card = pagina.locator(TOP + CARD)
    deschis = card.is_visible()
    if deschis:
        card.click()
        pagina.locator(TOP + "p#mig-cum-balanta").wait_for()
    verifica("card_balanta")
    if deschis:
        pagina.locator(TOP + ".nav-inapoi:visible").click()
        pagina.locator(TOP + "#mig-alege").wait_for()
    verifica("solduri_actiune")

    bloc, masura = audit(pagina)
    bloc.evaluate("(e,v) => e.dataset.vizibilDupaRulare = v", "da" if masura["vizibil"] else "nu")
    print("MASURA AC093", masura)
    # Captura raportului precedă orice schimbare de viewport sau derulare manuală.
    verifica("audit_raport")
    marime = pagina.viewport_size
    try:
        pagina.set_viewport_size({"width": 640, "height": 480})
        in_cadru(pagina.locator(TOP + "#cf-audit-run"))
        verifica("audit_buton")
    finally:
        pagina.set_viewport_size(marime)

    declaratii(pagina)
    lista = martor_declaratie(pagina)
    verifica("declaratii")
    lista.get_by_role("searchbox").fill("")
    deschide_d110(pagina)
    verifica("d110")
    for cod in ("621", "638"):
        martor_cod(pagina, cod)
        verifica("d110_" + cod)
