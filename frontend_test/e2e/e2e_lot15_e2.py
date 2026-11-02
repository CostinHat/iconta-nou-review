# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E2 — cadrul ferestrei de lucru (DS ferestre și tabele, secțiunea 1), în browser, pe ecranul real.

  * bara de sus: 56 px, „←” 40 × 40, fără traseu (un singur „›” urmat de numele ferestrei NU e traseu), căutarea 320 × 40; la o fereastră de firmă
    „<nume> · CUI <cod>”, la una de cabinet numele cabinetului;
  * bara de jos: 72 px, fixă, ultimul copil al corpului, un singur buton principal L (52 px) în dreapta și „Renunță” M (44 px) lângă el; fereastra fără
    acțiune proprie are „Închide”; „Renunță” întoarce un pas;
  * butonul principal e inactiv cât un câmp obligatoriu (etichetă cu „*”) vizibil e gol, cu motivul „Completează: …” în bară (729).
Firma e NOUĂ (`firma_noua`)."""
import pytest

from conftest import firma_noua
from e2e_bloc_a import pregateste_firma

REZOLUTII = ((1920, 1080), (1366, 768))


@pytest.fixture()
def firma_cadru(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


def _masuri(pg):
    return pg.evaluate("""() => {
      const F = [...document.querySelectorAll('.fereastra')].pop(), r = (e) => { const b = e.getBoundingClientRect(); return [Math.round(b.width), Math.round(b.height)]; };
      const ant = F.querySelector('.fereastra-antet'), jos = F.querySelector('.fereastra-corp > .fereastra-jos'), corp = F.querySelector('.fereastra-corp');
      const pr = jos && [...jos.querySelectorAll('button.fj-principal')], ren = jos && jos.querySelector('.fj-renunta');
      return { antet: r(ant), sageata: r(ant.querySelector('.nav-sageata')), cautare: r(ant.querySelector('.cautare-in-fereastra .cautare-camp')),
        fir: ant.querySelector('.fereastra-fir').innerText.replace(/\\s+/g, ' ').trim(), separatori: ant.querySelectorAll('.fir-sep').length, verigi: ant.querySelectorAll('.fir-veriga').length,
        jos: jos && r(jos), jos_ultimul: !!jos && corp.lastElementChild === jos,
        jos_jos: jos && Math.round(F.getBoundingClientRect().bottom - jos.getBoundingClientRect().bottom),
        principale: pr && pr.map((b) => [b.innerText.trim(), r(b)[1], b.disabled || !!b.dataset.cadruInactiv]), renunta: ren && [ren.innerText.trim(), r(ren)[1]],
        motiv: jos && jos.querySelector('.fj-motiv').innerText.trim() }; }""")


@pytest.mark.parametrize("lat,inalt", REZOLUTII)
def test_cadrul_ferestrei_de_firma(patron, firma_cadru, lat, inalt):
    pg = patron.pg
    pg.set_viewport_size({"width": lat, "height": inalt})
    patron.firma(firma_cadru["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=25000)
    m = _masuri(pg)
    assert m["antet"][1] == 56 and m["sageata"] == [40, 40] and m["cautare"] == [320, 40], m
    assert m["verigi"] == 0 and m["separatori"] == 1 and "· CUI " in m["fir"] and m["fir"].endswith("Operațiuni speciale"), m
    assert m["jos"][1] == 72 and m["jos_ultimul"] and m["jos_jos"] == 0, m
    assert m["principale"] == [["Închide", 52, False]] and m["renunta"] == ["Renunță", 44], m


def test_cabinetul_in_bara_de_sus(patron):
    pg = patron.pg
    pg.set_viewport_size({"width": 1920, "height": 1080})
    patron.acasa()
    pg.click("button.cab-card:has([data-cheie='termene'])")
    pg.wait_for_selector(".fereastra-jos", timeout=20000)
    m = _masuri(pg)
    assert m["antet"][1] == 56 and m["separatori"] == 1 and m["fir"].endswith("Termene"), m
    assert "Cabinet" in m["fir"].split("›")[0] and "F1" not in m["fir"], m


def test_principalul_inactiv_cu_motiv_din_etichetele_cu_stea(patron, firma_cadru):
    pg = patron.pg
    pg.set_viewport_size({"width": 1920, "height": 1080})
    patron.firma(firma_cadru["nume"])
    pg.click("#fa-operatiuni")
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=25000)
    pg.evaluate("""() => { const b = document.querySelector("button[data-op='chirie']"); const g = b.closest('.op-grup[hidden]');
        if (g) document.querySelector('.rap-tab[data-grup="' + g.dataset.frecventa + '"]').click(); }""")
    pg.click("button[data-op='chirie']")
    pg.wait_for_selector("#op-trimite", timeout=20000)
    pg.wait_for_timeout(1000)
    m = _masuri(pg)
    assert m["principale"][0][2] is True and m["motiv"], m                      # inactiv, cu motiv în bară
    assert pg.eval_on_selector("#op-trimite", "e => !!e.closest('.fereastra-jos')")   # același buton al ecranului, mutat în bară
    pg.locator(".fereastra-jos .fj-renunta").click()                             # „Renunță” întoarce un pas
    pg.wait_for_selector("button[data-op='chirie']", state="attached", timeout=20000)
    assert pg.locator("#op-trimite").count() == 0                                # fereastra formularului s-a închis
