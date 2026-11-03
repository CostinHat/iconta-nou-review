# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E4 — piesele de afișare aplicate tuturor ferestrelor, în browser, pe ecranul real (firma e NOUĂ: `firma_noua`).

  * tabelul DS: lista de înregistrări (Plan de conturi, 579 de rânduri) e tabel DS cu cap de 40 px, rânduri de 44 px, subsol cu contorul, căutare de 44 px sus,
    derulare numai în interiorul tabelului (capul și subsolul rămân vizibile); căutarea filtrează, contorul urmează, clicul pe butonul rândului merge;
  * card-rezumat: explicația și nota devin card de 44 px cu „▾ detalii”; textul întreg (cu temeiul) e sub „detalii”, nu tăiat; cel mult 2 la vedere;
  * Audit de preluare se deschide din Import date (intrarea lipsea: catalogul căutării îl punea acolo, ecranul nu avea butonul).
Scenariile de server și registrele sunt în `core/test_lot15_e4.py`, `core/test_semnale_cu_buton.py`, `core/test_poarta_lista.py`."""
import pytest

from conftest import firma_noua
from e2e_bloc_a import pregateste_firma


@pytest.fixture()
def firma_e4(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


def test_tabel_ds_plan_de_conturi_cautare_derulare_interna_si_clic(patron, firma_e4):
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    patron.firma(firma_e4["nume"])
    pg.click("#fa-planconturi")
    pg.wait_for_selector(".fereastra .ds-tabel-lista-tabel tbody tr", timeout=30000)
    m = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra')].pop(), t = F.querySelector('table.ds-tabel'), sub = F.querySelector('.ds-tabel-subsol'),
      corp = F.querySelector('.fereastra-corp'), zona = F.querySelector('.zona-derulare'), cauta = F.querySelector('.fereastra-corp input[type=search], .fereastra-corp input[placeholder*="Caut"]');
      const rect = (e) => e.getBoundingClientRect();
      return { cap: Math.round(rect(t.querySelector('thead th')).height), rand: Math.round(rect(t.querySelector('tbody td')).height), subsol: Math.round(rect(sub).height),
        subsolVizibil: rect(sub).bottom <= innerHeight, randuri: t.querySelectorAll('tbody tr').length, contor: sub.textContent.trim(), cautare: cautare = cauta ? Math.round(rect(cauta).height) : null,
        fereastraDeruleaza: corp.scrollHeight > corp.clientHeight + 1, zonaDeruleaza: !!zona && zona.scrollHeight > zona.clientHeight + 1, zebra: getComputedStyle(t.querySelectorAll('tbody tr')[0]).backgroundColor !== getComputedStyle(t.querySelectorAll('tbody tr')[1]).backgroundColor }; }""".replace("cautare: cautare =", "cautare:"))
    assert abs(m["cap"] - 40) <= 1 and abs(m["rand"] - 44) <= 1 and abs(m["subsol"] - 44) <= 1 and m["zebra"], m   # aceeași toleranță de 1 px (chenarul) ca în verificator
    assert m["randuri"] > 20 and m["subsolVizibil"] and not m["fereastraDeruleaza"] and m["zonaDeruleaza"], m   # capul și subsolul la vedere, derulează doar tabelul
    assert str(m["randuri"]) in m["contor"].replace(".", ""), m                   # contorul din subsol = rândurile tabelului
    assert m["cautare"] == 44, m
    # căutarea filtrează, contorul urmează
    cauta = pg.locator(".fereastra-corp input[type=search]:visible, .fereastra-corp input[placeholder*='Caut']:visible").first
    cauta.fill("Capital")
    pg.wait_for_timeout(500)
    vizibile = pg.locator(".fereastra .ds-tabel tbody tr:visible").count()
    assert 1 <= vizibile < m["randuri"], vizibile
    # clicul pe butonul rândului merge ca înainte („Adaugă analitic” deschide formularul pe contul rândului)
    pg.locator(".fereastra .ds-tabel tbody tr:visible button:has-text('Adaugă analitic')").first.click()
    pg.wait_for_timeout(500)
    patron.captura("l15e4_plan_de_conturi")


def test_card_rezumat_explicatia_lunga_intreaga_sub_detalii(patron, firma_e4):
    pg = patron.pg
    pg.set_viewport_size({"width": 900, "height": 768})                         # explicația de 140 de caractere se rupe pe două rânduri: devine card
    patron.firma(firma_e4["nume"])
    pg.click("#fa-planconturi")
    pg.wait_for_selector(".fereastra .ds-rezumat", timeout=30000)
    m = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra')].pop(), carduri = [...F.querySelectorAll('.ds-rezumat')].filter((c) => c.offsetParent),
      corp = F.querySelector('.fereastra-corp');
      return { n: carduri.length, h: carduri.map((c) => Math.round(c.getBoundingClientRect().height)), neerori: carduri.filter((c) => !c.classList.contains('ds-rezumat-eroare')).length,
        deruleaza: corp.scrollHeight > corp.clientHeight + 1 }; }""")
    assert m["n"] >= 1 and all(abs(h - 44) <= 1 for h in m["h"]) and m["neerori"] <= 2 and not m["deruleaza"], m
    pg.locator(".fereastra .ds-rezumat-plie:visible").first.click()                     # „▾ detalii” arată textul întreg, sub card
    det = pg.locator(".fereastra .ds-rezumat-detalii:visible").first
    assert len(det.inner_text().strip()) > 90
    patron.captura("l15e4_card_rezumat")


def test_audit_de_preluare_se_deschide_din_import_date(patron, firma_e4):
    pg = patron.pg
    patron.firma(firma_e4["nume"])
    pg.click("#fa-import")
    pg.wait_for_selector(".fereastra .mig-frand", timeout=30000)
    pg.locator(".fereastra .mig-frand", has_text="Audit de preluare").click()
    pg.wait_for_selector("#cf-audit-zona, #cf-audit-run", timeout=30000)
    assert pg.locator("#cf-audit-run").count() == 1
