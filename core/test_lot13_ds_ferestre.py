# -*- coding: utf-8 -*-
"""Lotul 13 (comanda 13.1), clasele Design System 673 / 509 (fereastra de lucru), 575 (drumul din antet), 676 (listele scurte), 675
(butonul inactiv cu motivul), 581 (bara de jos nu mănâncă tabelul) — mecanismele REALE (`navigator.js`, `api.js`, `stil.css`), în
Chromium, pe pagina-ham a lotului 12 (`core/test_lot12_ui2_ecrane.PAGINA`: navigatorul real, rutele simulate).

Comanda 13.1, verbatim: 673 „Se extinde la orice acțiune din orice fereastră: deschide o fereastră nouă, centrată; fereastra de lucru
(formular, detalii) ocupă ecranul ca fereastra cu tabel, fără derulare”; 676 „opțiunile apar ca butoane alăturate, toate vizibile, cea
aleasă marcată […] Nimic nu se deschide singur.”; 675 „ce nu se aplică stă inactiv, cu motivul la trecerea cu mouse-ul”; 575 „titlul
«Firme › Firme existente» la Adaugă firmă”; 581 „casetele roșii fixe strâng tabelul rândurilor într-o bară albă”.

Temei: N/A — reguli de interfață (DS cap.1, cap.2a, cap.9, v2.104).
"""
import pytest

from core.test_lot12_ui2_derulare import _pagina
from core.test_lot12_ui2_ecrane import INALT, LAT, browser  # noqa: F401 — fixture


@pytest.fixture()
def pg(browser):  # noqa: F811
    p, erori = _pagina(browser, {})
    yield p
    p.close()
    assert not erori, erori


def test_def_673_fereastra_deschisa_peste_alta_e_fereastra_de_lucru_cat_ecranul(pg):
    """673 / 509. MUTAȚIE: `fer.classList.toggle("fer-lucru", …)` scos din navigator -> a doua fereastră rămâne de 680 px -> pică."""
    r = pg.evaluate("""() => new Promise((rez) => {
      window._nav.deschide('Fereastra firmei', (c) => { c.innerHTML = '<p class="ecran-nota">Carduri</p>'; });
      window._nav.deschide('Salariu', (c) => { c.innerHTML = '<label class="camp"><span class="camp-eticheta">Salariu</span><input id="s" class="camp-input"></label>'; });
      // [14.2] se măsoară DUPĂ animația de apariție (`aparitie-fereastra`, 140 ms, translateY 8 -> 0): la 120 ms fereastra era încă în mișcare și,
      // sub încărcarea porții, ieșea cu 2-3 px mai jos; geometria cerută (cât ecranul, centrată, ±2 px) rămâne aceeași
      setTimeout(async () => {
        const f = [...document.querySelectorAll('.fereastra')].pop();
        await Promise.all(f.getAnimations().map((a) => a.finished));
        const b = f.getBoundingClientRect();
        rez({ clase: f.className, lat: b.width, inalt: b.height, stanga: b.left, sus: b.top,
              fir: (f.querySelector('.fereastra-fir') || {}).innerText || '', acum: (f.querySelector('.fir-acum') || {}).innerText || '' });
      }, 120);
    })""")
    assert set(r["clase"].split()) >= {"fer-lucru"}, r
    assert abs(r["lat"] - (LAT - 24)) <= 2 and abs(r["inalt"] - (INALT - 24)) <= 2, r          # cât ecranul, minus marginea (12 px pe parte; [lotul 14, 687] era 24)
    assert abs(r["stanga"] - 12) <= 2 and abs(r["sus"] - 12) <= 2, r                           # centrată
    # 575 — drumul se încheie cu fereastra de acum (nu cu părintele, citit ca titlu). MUTAȚIE: `fir-acum` scos -> pică.
    assert r["acum"] == "Salariu" and r["fir"].replace("\n", " ").strip().endswith("Salariu"), r


def test_def_673_confirmarea_ramane_fereastra_mica_si_prima_fereastra_nu_se_schimba(pg):
    r = pg.evaluate("""() => new Promise((rez) => {
      window._nav.deschide('Prima', (c) => { c.innerHTML = '<p class="ecran-nota">x</p>'; });
      const prima = [...document.querySelectorAll('.fereastra')].pop().className;
      window._nav.deschide('Confirmare', (c) => { c.innerHTML = '<p class="ecran-nota">Sigur?</p>'; }, { lat: 'mic' });
      setTimeout(() => rez({ prima, mica: [...document.querySelectorAll('.fereastra')].pop().className,
                             acum: !!document.querySelector('.fereastra .fir-acum') }), 80);
    })""")
    assert "fer-lucru" not in r["prima"] and "fer-lucru" not in r["mica"], r


_LISTE = """() => new Promise((rez) => {
  window._nav.deschide('Decont', (c) => {
    c.innerHTML = `<label class="camp"><span class="camp-eticheta">Fel</span><select id="fel" class="camp-input" data-butoane>
        <option value="" data-alege selected disabled hidden>— alege —</option><option value="avans">Avans deplasare</option>
        <option value="decont">Decont final</option></select></label>
      <label class="camp"><span class="camp-eticheta">Lungă</span><select id="lung" class="camp-input" data-butoane>
        ${[1,2,3,4,5,6,7].map((i) => `<option value="${i}">O${i}</option>`).join('')}</select></label>
      <p><button class="buton-primar" id="salv">Salvează</button></p><div id="m"></div>`;
    window._schimbari = [];
    c.querySelector('#fel').addEventListener('change', (e) => window._schimbari.push(e.target.value));
  });
  setTimeout(rez, 120);
})"""


def test_def_676_lista_scurta_e_butoane_alaturate_fara_nimic_ales(pg):
    """676. MUTAȚIE: observatorul listelor scurte (`_listeScurte`) scos din api.js -> lista rămâne derulantă -> pică. MUTAȚIE:
    `marcheaza()` scos din setterul `value` -> valoarea pusă din cod nu se vede pe buton -> pică."""
    pg.evaluate(_LISTE)
    r = pg.evaluate("""() => { const g = document.querySelector('#fel').previousElementSibling;
      return { grup: g && g.className, butoane: g ? [...g.querySelectorAll('button')].map((b) => [b.textContent, b.getAttribute('aria-checked')]) : [],
               lunga: !!(document.querySelector('#lung').previousElementSibling || {}).classList?.contains('alegere-butoane')
                      && !document.querySelector('#lung').previousElementSibling.hidden,
               sursaVizibila: document.querySelector('#fel').getBoundingClientRect().width }; }""")
    assert r["grup"] == "alegere-butoane", r
    assert r["butoane"] == [["Avans deplasare", "false"], ["Decont final", "false"]], r          # „— alege —” nu e buton; nimic ales
    assert r["lunga"] is False, r                                                                # 7 opțiuni: rămâne listă
    assert r["sursaVizibila"] <= 1, r
    # clicul pe eticheta de lângă butoane nu alege nimic (o etichetă ar apăsa primul buton)
    pg.click(".fereastra:last-of-type label.camp .camp-eticheta >> text=Fel")
    assert pg.evaluate("() => document.querySelector('#fel').selectedOptions[0].hasAttribute('data-alege')")
    pg.click(".fereastra:last-of-type .alegere-butoane button >> text=Decont final")
    r2 = pg.evaluate("""() => ({ v: document.querySelector('#fel').value, sch: window._schimbari,
      ales: [...document.querySelectorAll('.alegere-butoane button')].filter((b) => b.classList.contains('buton-activ')).map((b) => b.textContent) })""")
    assert r2 == {"v": "decont", "sch": ["decont"], "ales": ["Decont final"]}, r2
    r3 = pg.evaluate("""() => { document.querySelector('#fel').value = 'avans';
      return [...document.querySelectorAll('.alegere-butoane button')].filter((b) => b.getAttribute('aria-checked') === 'true').map((b) => b.textContent); }""")
    assert r3 == ["Avans deplasare"], r3


def test_def_676_alegerea_lipsa_se_cere_langa_butoane(pg):
    """676 + cap.17: lista nevăzută rămâne cea cerută de `cereAlegerile` (nu `display:none`) -> refuzul vine lângă butoane."""
    pg.evaluate(_LISTE)
    r = pg.evaluate("""async () => { const A = await import('/static/js/api.js');
      const lipsa = A.cereAlegerile(document.querySelector('.fereastra-corp'), ['#fel']);
      const sp = document.querySelector('.msg-eroare[data-camp="fel"]');
      return { lipsa, eroare: sp && sp.textContent }; }""")
    assert r["lipsa"] is True and r["eroare"], r


def test_def_675_butonul_care_nu_se_aplica_sta_inactiv_cu_motivul(pg):
    """675. MUTAȚIE: ascultătorul de clic din captură (`[aria-disabled="true"]`) scos din api.js -> handlerul ecranului rulează -> pică."""
    r = pg.evaluate("""async () => { const A = await import('/static/js/api.js');
      window._nav.deschide('Salariați', (c) => {
        c.innerHTML = `<p><button class="buton-secundar" id="b1"${A.atributeInactiv('Nota e validată — se stornează, nu se șterge.')}>Șterge</button>
          <button class="buton-secundar" id="b2">+ masă</button></p>`;
      });
      await new Promise((r) => setTimeout(r, 80));
      let apasat = 0; const b1 = document.getElementById('b1'), b2 = document.getElementById('b2');
      b1.addEventListener('click', () => apasat++);
      b1.click();
      A.inactiv(b2, 'Salariatul are tichetul pus pe luna aceasta.');
      return { apasat, titlu: b1.title, op: getComputedStyle(b1).opacity, b2: b2.getAttribute('aria-disabled'), t2: b2.title,
               focusabil: b1.tabIndex >= 0 && !b1.disabled }; }""")
    assert r["apasat"] == 0 and r["titlu"].startswith("Nota e validată") and float(r["op"]) < 0.6, r
    assert r["b2"] == "true" and r["t2"].startswith("Salariatul") and r["focusabil"], r


def test_def_581_caseta_din_bara_de_jos_nu_mananca_tabelul(pg):
    """581. Fereastra cu tabel la 1280×720, cu lista rândurilor respinse ale unui import (40 de rânduri) în bara de jos: zona refuzului are
    cel mult 35vh, iar tabelul păstrează loc. MUTAȚIE: regula `.bara-fixa .mig-eroare { max-height: 35vh }` scoasă din stil.css -> pică."""
    r = pg.evaluate("""() => new Promise((rez) => {
      window._nav.deschide('Balanță încărcată', (c) => {
        c.innerHTML = `<div class="rezumat-fix"><p class="mig-intro">40 de conturi</p></div>
          <table class="fd-tabel"><tbody>${[...Array(40).keys()].map((i) => `<tr><td>Rândul ${i}</td><td>1.000,00</td></tr>`).join('')}</tbody></table>
          <div class="bara-fixa"><div class="mig-eroare" id="mig-eroare">${[...Array(40).keys()].map((i) => `Rândul ${i}: contul nu există în plan.`).join('<br>')}</div>
          <button class="buton-primar mig-buton">Salvează soldurile</button></div>`;
      }, { lat: 'tabel' });
      setTimeout(() => { const e = document.getElementById('mig-eroare').getBoundingClientRect();
        const corp = document.querySelector('.fereastra-corp').getBoundingClientRect();
        const bara = document.querySelector('.bara-fixa').getBoundingClientRect();
        rez({ eroare: e.height, bara: bara.height, corp: corp.height }); }, 150);
    })""")
    assert r["eroare"] <= 0.35 * INALT + 2, r
    assert r["corp"] - r["bara"] >= 0.3 * r["corp"], r            # tabelul are loc deasupra barei
