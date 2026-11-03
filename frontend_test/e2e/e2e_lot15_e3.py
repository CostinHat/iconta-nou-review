# -*- coding: utf-8 -*-
"""Lotul 15, comanda 15.1-E3 — reparațiile pe piese, în browser, pe ecranul real (firma e NOUĂ: `firma_noua`).

  * 722 / 727.1: Declarații, pasul 1 = lista cu căutare permanentă (căutare de 44 px, rânduri de 44 px), fără butoane stivuite, fără „încă n”, fără „Arată alte declarații”;
  * F-A.3: Emite factură — categoriile fără TVA sunt grup de butoane, un singur buton principal (în bară), fără derulare la 1366 × 768;
  * 725.3: Ctrl+R din Declarații redeschide aceeași fereastră, nu ecranul cabinetului.
Scenariile de server (căutarea 681.2, luna preluării 724.2, catalogul acțiunilor 728.1) sunt în `core/test_lot15_e3.py`."""
import pytest

from conftest import firma_noua
from e2e_bloc_a import pregateste_firma


@pytest.fixture()
def firma_e3(patron):
    for f in firma_noua():
        pregateste_firma(patron, f)
        yield f


def test_def_722_declaratii_lista_cu_cautare(patron, firma_e3):
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    patron.firma(firma_e3["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector(".ds-lista-permanenta .ds-lista-cauta", timeout=25000)
    m = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra')].pop(), c = F.querySelector('.ds-lista-cauta'), r = F.querySelector('.ds-lista-rand');
      const corp = F.querySelector('.fereastra-corp'), lista = F.querySelector('.ds-lista');
      return { cauta: Math.round(c.getBoundingClientRect().height), rand: r ? Math.round(r.getBoundingClientRect().height) : null, lat: Math.round(lista.getBoundingClientRect().width),
        butoaneStivuite: F.querySelectorAll('.ds-datorata, .ds-datorate-inca, #dec-alte').length, incaN: /\\bîncă \\d+/.test(F.innerText),
        selectVizibil: [...F.querySelectorAll('select')].some((s) => !s.classList.contains('ds-lista-sursa') && s.offsetParent && s.getBoundingClientRect().width > 4 && getComputedStyle(s).opacity !== '0'),
        derularePagina: corp.scrollHeight > corp.clientHeight + 1 && getComputedStyle(corp).overflowY !== 'visible' && !corp.querySelector('.zona-derulare'),
        incape: lista.getBoundingClientRect().right <= innerWidth }; }""")
    assert m["cauta"] == 44 and m["rand"] == 44 and m["lat"] <= 720 and m["incape"], m
    assert m["butoaneStivuite"] == 0 and not m["incaN"] and not m["selectVizibil"], m
    pg.fill(".ds-lista-cauta", "D300")                                          # căutarea filtrează lista, fără să o închidă
    pg.wait_for_timeout(300)
    assert pg.locator(".ds-lista-rand").count() >= 1 and pg.locator(".ds-lista-cauta").is_visible()
    for incercare in range(3):                                                  # alegerea unui rând = tipul ales (lista se redesenează după căutare: un clic pierdut în redesenare se repetă)
        pg.locator(".ds-lista-rand:not(.ds-lista-inactiv)").first.click()
        try:
            pg.wait_for_function("() => document.querySelector('#dec-tip') && document.querySelector('#dec-tip').value !== ''", timeout=4000 if incercare < 2 else 10000)
            break
        except Exception:  # noqa: BLE001 — Playwright TimeoutError
            if incercare == 2:
                raise
    patron.captura("l15_722_declaratii")


def test_def_f_a3_categoriile_fara_tva_grup_de_butoane(patron, firma_e3):
    from e2e_bloc_a import _deschide_emiterea
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    _deschide_emiterea(patron, firma_e3["nume"])
    m = pg.evaluate("""() => { const F = [...document.querySelectorAll('.fereastra')].pop(), corp = F.querySelector('.fereastra-corp'),
      principale = [...F.querySelectorAll('button.buton-primar')].filter((b) => b.offsetParent && b.closest('.fereastra-jos'));
      return { principale: principale.map((b) => b.innerText.trim()), principaleInConinut: [...F.querySelectorAll('.fereastra-corp button.buton-primar')].filter((b) => b.offsetParent && !b.closest('.fereastra-jos')).length,
        derulare: corp.scrollHeight - corp.clientHeight }; }""")
    assert m["principale"] == ["Emite factură"] and m["principaleInConinut"] == 0, m
    assert m["derulare"] <= 1, m                                                # formularul nu derulează la 1366 × 768
    # „Fără TVA” pe linie -> categoriile apar ca grup de butoane, nu listă derulantă
    pg.click(".em-linie .alegere-butoane button:has-text('Fără TVA')")
    pg.wait_for_timeout(500)
    cat = pg.evaluate("""() => { const s = document.querySelector('.em-l-categorie'); const g = s && s.previousElementSibling;
      return { butoane: g && g.classList.contains('alegere-butoane') && !g.hidden ? [...g.querySelectorAll('button')].map((b) => b.innerText.trim()) : null,
               selectVizibil: !!s && !s.hidden && s.offsetParent && s.getBoundingClientRect().width > 4 && getComputedStyle(s).opacity !== '0' }; }""")
    assert cat["butoane"] and len(cat["butoane"]) == 7 and not cat["selectVizibil"], cat
    patron.captura("l15_fa3_emite")


def test_def_725_3_ctrl_r_readuce_declaratiile(patron, firma_e3):
    pg = patron.pg
    patron.firma(firma_e3["nume"])
    pg.click("#fa-declaratii")
    pg.wait_for_selector(".ds-lista-permanenta", timeout=25000)
    pg.reload(wait_until="domcontentloaded")                                    # Ctrl+R
    pg.wait_for_selector(".ds-lista-permanenta", state="attached", timeout=60000)   # nimeni nu a apăsat nimic: Declarațiile au revenit singure
    assert pg.locator(".fereastra .pf-titlu", has_text="Declarații").count() >= 1
    pg.locator(".fereastra-jos .fj-renunta").click()                            # închisă de om: Ctrl+R nu o mai redeschide
    pg.wait_for_function("() => !document.querySelector('.ds-lista-permanenta') || document.querySelectorAll('.fereastra').length <= 1", timeout=20000)
