from contextlib import contextmanager
from pathlib import Path
from urllib.parse import urlsplit
import json

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

MESURE = """list => {
  const rows = [...list.querySelectorAll('[role=option]')];
  const owners = [];
  let clip = {top:0,bottom:innerHeight,left:0,right:innerWidth};
  for(let n=list; n; n=n.parentElement){
    const s=getComputedStyle(n),r=n.getBoundingClientRect();
    if(/auto|scroll/.test(s.overflowY) && n.scrollHeight>n.clientHeight+1) owners.push(n.id||n.className||n.tagName);
    if(/hidden|clip|scroll|auto/.test(s.overflowY)) {
      const top=r.top+n.clientTop;clip.top=Math.max(clip.top,top);clip.bottom=Math.min(clip.bottom,top+n.clientHeight);
    }
    if(/hidden|clip|scroll|auto/.test(s.overflowX)) {
      const left=r.left+n.clientLeft;clip.left=Math.max(clip.left,left);clip.right=Math.min(clip.right,left+n.clientWidth);
    }
  }
  const fully=rows.filter(n=>{const r=n.getBoundingClientRect();return r.width>0 && r.height>0 && r.top>=clip.top-0.5 && r.bottom<=clip.bottom+0.5 && r.left>=clip.left-0.5 && r.right<=clip.right+0.5});
  return {viewport:[innerWidth,innerHeight], total:rows.length,owners,visible:fully.length,
          labels:rows.map(n=>n.querySelector('.ds-lista-nume')?.innerText.trim()||n.innerText.trim())};
}"""

def declaratii(pg, width):
    pg.set_viewport_size({"width":width,"height":590 if width==603 else 768})
    firma(pg, F1, "#fa-declaratii")
    panel = pg.locator(TOP+"#dec-tip + .ds-lista")
    panel.locator('[role=option]').filter(has_text="D300 · 10/2026").first.wait_for(state="attached")
    pg.evaluate("document.fonts.ready")
    return panel

@contextmanager
def pas(nume):
    try:
        yield
    except Exception as exc:
        mesaj = str(exc).splitlines()
        raise RuntimeError(f"{nume} — {type(exc).__name__}: {mesaj[0] if mesaj else ''}") from exc


def observa_din_panou(pg, ident, panel, m):
    lista = panel.locator('[role=listbox]')
    tip = pg.locator(TOP + "#dec-tip")
    with pas("geometria inițială"):
        m.update(lista.evaluate(MESURE))

    with pas("citirea opțiunilor sursă pentru filtrare"):
        m["asteptate_filtru"] = tip.locator("option").evaluate_all("""options => options
            .filter(o => o.value && !o.hasAttribute('data-alege'))
            .filter(o => ((o.dataset.nume || o.textContent) + ' ' + (o.dataset.motiv || ''))
                .toLowerCase().includes('d300'))
            .map(o => (o.dataset.nume || o.textContent).trim())""")
    field = panel.locator("input[type=search]")
    rand = lista.locator('[role=option]').filter(has_text="D300 · 10/2026").first
    with pas("aplicarea filtrului D300"):
        field.fill("D300")
        rand.wait_for(state="attached")
        m["filtrate"] = lista.locator(".ds-lista-nume").all_inner_texts()
    with pas("anularea filtrului D300"):
        field.fill("")
        m["restabilite"] = lista.locator(".ds-lista-nume").all_inner_texts()
    with pas("selectarea și citirea perioadei D300"):
        rand.scroll_into_view_if_needed()
        rand.click()
        m["selectie"] = [pg.locator(TOP + selector).input_value()
                         for selector in ("#dec-tip", "#dec-an", "#dec-luna")]
    if ident == "e.1":
        # A doua alegere pornește din vederea inițială a aceleiași firme.
        with pas("redeschiderea listei F1 pentru ultima opțiune"):
            nou = declaratii(pg, 603).locator('[role=listbox]')
            if nou.locator(".ds-lista-nume").all_inner_texts() != m["labels"]:
                raise ValueError("lista redeschisă diferă de lista inițială")
        with pas("selectarea ultimei opțiuni active și citirea din select"):
            last = tip.evaluate("""s => {
                const o = [...s.options].filter(o => o.value && !o.matches(':disabled')
                    && !o.hasAttribute('data-alege')).at(-1);
                if (!o) throw new Error('nicio opțiune activă');
                return {label:(o.dataset.nume || o.textContent).trim(), value:o.value, index:o.index};
            }""")
            m["ultim_sursa"] = last["value"]
            m["index_ultim_sursa"] = last["index"]
            rand = nou.locator('[role=option]:not(.ds-lista-inactiv)').filter(
                has=pg.get_by_text(last["label"], exact=True)).last
            rand.scroll_into_view_if_needed()
            rand.click()
            ales = tip.evaluate("s => ({value:s.value, index:s.selectedIndex})")
            m["ultim_selectat"] = ales["value"]
            m["index_ultim_selectat"] = ales["index"]
    return m

def rezultat(ident,m):
    dim=[603,590] if ident=="e.1" else [1366,768]
    if ident not in ("e.1","e.2") or m["viewport"]!=dim or m["total"]<8 or not any("D300 · 10/2026" in label for label in m["labels"]):
        raise ValueError("Lipsesc lista lungă din F1 sau declarația martor")
    select=m["selectie"]
    selectie=(select[0].lower()=="d300" and select[1]=="2026" and int(select[2])==10)
    if ident == "e.1":
        return (len(m["owners"]) == 1 and bool(m["ultim_sursa"])
                and m["ultim_selectat"] == m["ultim_sursa"]
                and m["index_ultim_selectat"] == m["index_ultim_sursa"] and selectie)
    expected=[x for x in m["labels"] if "d300" in x.lower()]
    return m["visible"]>=8 and m["restabilite"]==m["labels"] and m["filtrate"]==m["asteptate_filtru"] and all(x in m["filtrate"] for x in expected) and bool(expected) and selectie

def test_ferestre_17_5_Q6(browser,capsys):
    from conftest import BAZA, CAPTURI, sesiune
    from core.ceas_proba import MOMENT_REF
    origine=origine_proba(BAZA)
    init=sesiune("dovada.71507@sesiuneab.test")
    dest=Path(CAPTURI)/"17_5_Q6"
    dest.mkdir(parents=True,exist_ok=True)
    masuri, verdicte, erori, partiale = {}, {}, {}, {}
    for ident in ("e.1","e.2"):
        m = {}
        ctx=browser.new_context()
        try:
            ctx.clock.set_fixed_time(MOMENT_REF)
            ctx.add_init_script(init)
            pg=ctx.new_page()
            pg.goto(origine+"/",wait_until="domcontentloaded")
            # Capture initial geometry before search/selection can scroll the pane.
            panel=declaratii(pg,603 if ident=="e.1" else 1366)
            pg.screenshot(path=str(dest/(ident+".png")))
            observa_din_panou(pg, ident, panel, m)
            verdicte[ident]=rezultat(ident,m)
            masuri[ident]=m
        except Exception as exc:
            partiale[ident] = m
            erori[ident]=type(exc).__name__+": "+str(exc).splitlines()[0]
        finally:
            ctx.close()
    for nume,obj in [("erori",erori),("masuri",masuri),("partiale",partiale)]:
        (dest/(nume+".json")).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")
    with capsys.disabled():
        for ident,ok in verdicte.items():print(f"VERDICT {ident} {'trece' if ok else 'pica'}",flush=True)
    if erori:raise RuntimeError(f"NEEXECUTAT: {erori}")
    assert set(verdicte)=={"e.1","e.2"} and all(verdicte.values()),verdicte
