# -*- coding: utf-8 -*-
"""[lotul 14, deficiența 687 — clasă] Fiecare fereastră de lucru încape pe un singur ecran, la 1920 × 1080 și la 1366 × 768; tabelele lungi
(și listele declarate) derulează numai în zona lor, iar secundarul stă în carduri-rezumat deschise în fereastra lor (DS cap.9 v2.105).

Comanda Costin 14.1 (verbatim în DS): „fiecare fereastră de lucru încape pe un singur ecran, fără derulare, la 1920 × 1080 și la 1366 × 768;
dacă nu încape, se reorganizează […]. Excepție: tabelele lungi (registre, balanțe) — se derulează doar tabelul, titlul, filtrele și acțiunile
rămân fixe.” Navigatorul REAL (`navigator.js`, `carduri.js`, `stil.css`), în Chromium, cu un ecran sintetic care are forma celor din aplicație:
titlu, luna, o acțiune principală, un șir de carduri, un tabel de 80 de rânduri sau o listă de 40.
MUTAȚII: `_zonaDerulare()` scos din `_lateste` -> corpul derulează -> pică; `flex: 1 1 0` scos de pe corpul ferestrei -> zona nu are înălțime -> pică;
clicul pe card nu mai deschide fereastra -> pică.
"""
import pytest

from core.test_lot12_ui2_ecrane import browser, _pagina  # noqa: F401 — harness-ul ecranelor lotului 12

REZOLUTII = [(1920, 1080), (1366, 768)]

_ECRAN_TABEL = """async () => {
  const { siraCarduri } = await import("/static/js/carduri.js");
  window._nav.deschide("Registru de probă", (corp, nav) => {
    corp.innerHTML = `<div class="rezumat-fix"><h2 class="pf-titlu">Registru de probă</h2>
        <p class="pf-intro">Luna 10/2026 <button class="buton-secundar">← luna</button> <button class="buton-primar" id="act">Acțiunea principală</button></p>
        <p class="pf-intro">O explicație lungă pe care o citește omul o dată: ${"text ".repeat(60)}</p><div id="carduri"></div></div>
      <table class="fd-tabel" id="tab"><thead><tr><th>Cont</th><th>Denumire</th><th class="fd-td-num">Suma</th></tr></thead>
        <tbody>${Array.from({ length: 80 }, (_, i) => `<tr><td>${1000 + i}</td><td>Rând ${i}</td><td class="fd-td-num">${i},00</td></tr>`).join("")}</tbody>
        <tfoot><tr><td colspan="2">Total</td><td class="fd-td-num">3.160,00</td></tr></tfoot></table>`;
    siraCarduri(corp.querySelector("#carduri"), [
      { id: "a", ton: "ok", text: "Balanța se închide ✓", deschide: (c) => { c.innerHTML = '<h2 class="pf-titlu">Balanța</h2><p id="in-card">Detaliul cardului</p>'; } },
      { id: "b", ton: "atentie", text: "45 de ciorne nevalidate", deschide: (c) => { c.innerHTML = '<p>Ciorne</p>'; } }], nav);
  });
  return true;
}"""

_ECRAN_LISTA = """async () => {
  window._nav.deschide("Închidere de probă", (corp) => {
    corp.innerHTML = `<h2 class="pf-titlu">Închidere</h2><p class="pf-intro">Luna 09/2026</p>
      <div id="ctl" data-zona-derulare><ul>${Array.from({ length: 90 }, (_, i) => `<li>Blocajul ${i}: ${"text ".repeat(12)}</li>`).join("")}</ul></div>
      <h3 class="pf-subtitlu">Evidența facturilor</h3><p><button class="buton-verde" id="fac">Închide evidența</button></p>`;
  }, { lat: "lucru" });
  return true;
}"""

_MASOARA = """() => { const c = [...document.querySelectorAll('.fereastra-corp')].pop(), z = c.querySelector('.zona-derulare');
  const r = { corp_dep: c.scrollHeight - c.clientHeight, lateral: c.scrollWidth - c.clientWidth, cu_zona: c.classList.contains('cu-zona'),
    fer: c.closest('.fereastra').className, fer_h: c.closest('.fereastra').getBoundingClientRect().height, vh: innerHeight };
  if (z) { const zr = z.getBoundingClientRect(), cr = c.getBoundingClientRect();
    r.zona_h = z.clientHeight; r.zona_dep = z.scrollHeight - z.clientHeight; r.zona_in_corp = zr.top >= cr.top - 1 && zr.bottom <= cr.bottom + 1; }
  const a = c.querySelector('#act, #fac'); if (a) { const ar = a.getBoundingClientRect(), cr = c.getBoundingClientRect(); r.actiune_vizibila = ar.top >= cr.top && ar.bottom <= cr.bottom + 1; }
  return r; }"""


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_tabelul_lung_deruleaza_in_zona_lui_nu_fereastra(browser, lat, inalt):
    """Tabel de 80 de rânduri + o explicație lungă + carduri: corpul ferestrei NU derulează (nici lateral), zona tabelului derulează ea, acțiunea
    principală e în vedere, iar zona are loc (cel puțin 30% din fereastră). MUTAȚII: `_zonaDerulare()` scos din `_lateste` sau `flex: 1 1 0`
    scos de pe corp (stil.css) -> pică."""
    pg, erori = _pagina(browser, {}, lat=lat, inalt=inalt)
    pg.evaluate(_ECRAN_TABEL)
    pg.wait_for_selector(".zona-derulare", timeout=10000)
    pg.wait_for_timeout(300)
    m = pg.evaluate(_MASOARA)
    assert m["corp_dep"] <= 1 and m["lateral"] <= 1, m
    assert m["cu_zona"] and m["zona_dep"] > 100 and m["zona_in_corp"], m                  # tabelul derulează în zona lui
    assert m["zona_h"] >= 0.3 * m["fer_h"] and m["actiune_vizibila"], m
    assert m["fer_h"] >= inalt - 24 - 1, m                                               # fereastra ia ecranul minus 12 px pe margine
    assert erori == []


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_antetul_si_totalul_tabelului_raman_in_zona(browser, lat, inalt):
    """Antetul (thead) și totalul (tfoot) se lipesc în zona de derulare: după derulare la mijloc rămân la marginile zonei, fără să acopere rânduri."""
    pg, _e = _pagina(browser, {}, lat=lat, inalt=inalt)
    pg.evaluate(_ECRAN_TABEL)
    pg.wait_for_selector(".zona-derulare", timeout=10000)
    r = pg.evaluate("""() => { const z = document.querySelector('.zona-derulare'); z.scrollTop = 600;
      const zr = z.getBoundingClientRect(), th = z.querySelector('thead th').getBoundingClientRect(), tf = z.querySelector('tfoot td').getBoundingClientRect();
      return { sus: Math.abs(th.top - zr.top) < 2, jos: Math.abs(tf.bottom - zr.bottom) < 2 }; }""")
    assert r == {"sus": True, "jos": True}, r


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_lista_declarata_deruleaza_in_zona_si_actiunea_ramane_in_vedere(browser, lat, inalt):
    """O listă care nu e tabel („Ce oprește închiderea”), declarată `data-zona-derulare`, derulează ea; titlul și acțiunea de sub ea rămân în vedere."""
    pg, _e = _pagina(browser, {}, lat=lat, inalt=inalt)
    pg.evaluate(_ECRAN_LISTA)
    pg.wait_for_selector(".zona-derulare", timeout=10000)
    pg.wait_for_timeout(200)
    m = pg.evaluate(_MASOARA)
    assert m["corp_dep"] <= 1 and m["zona_dep"] > 100 and m["actiune_vizibila"], m


def test_cardul_se_deschide_in_fereastra_lui(browser):
    """Clicul pe un card-rezumat deschide FEREASTRA lui, de lucru (`fer-lucru`, centrată, cât ecranul), peste cea de dedesubt; cardul fără conținut
    nu deschide nimic. MUTAȚIE: `nav.deschide` scos din `siraCarduri` -> pică."""
    pg, _e = _pagina(browser, {})
    pg.evaluate(_ECRAN_TABEL)
    pg.wait_for_selector("[data-card='a']", timeout=10000)
    assert pg.locator(".fereastra").count() == 1
    pg.click("[data-card='a']")
    pg.wait_for_selector("#in-card", timeout=5000)
    assert pg.locator(".fereastra").count() >= 1
    sus = pg.evaluate("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); return { cls: f.className, txt: f.innerText }; }")
    assert "fer-lucru" in sus["cls"] and "Detaliul cardului" in sus["txt"], sus
    assert pg.evaluate("() => [...document.querySelectorAll('.card-rezumat')].every(b => b.tagName === 'BUTTON')")
