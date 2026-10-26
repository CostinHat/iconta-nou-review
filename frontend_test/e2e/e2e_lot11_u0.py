# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — punctele transversale, subagentul U0:
440 (pct.16), 441 (pct.17), 443 (pct.19), 445 (pct.21). Pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test
(`firma_noua` / `_firma_noua`); CUI-urile au cifra de control verificată (`cui_cu_control`, algoritmul din CLAUDE.md).

Date de pornire scrise direct: niciuna. Firma, numerotarea, factura și profilul se fac pe rutele pe care le cheamă ecranele
(`pregateste_firma`, `emite_api`, `_factura_emisa`); ce se probează se face pe ecran."""
import pytest

from conftest import firma_noua, sql
from e2e_bloc_a import _api, _card, _ok, emite_api, pregateste_firma
from e2e_bloc_d import _detaliu_factura, _factura_emisa, firma_gv  # noqa: F401 — fixtura modulului


@pytest.fixture(scope="module")
def firma_u0():
    for f in firma_noua():
        yield f


def _caseta(pg):
    """Caseta „NU s-a salvat.”: [(text, vizibil)] pe rând."""
    return pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li", "lis => lis.map(li => [li.textContent.trim(), !li.hidden])")


# ── 440 — toate erorile deodată, fiecare cu textul ei, în casetă și lângă câmp ─────────────────────────────────────────────
def test_def_440_date_firma_toate_erorile_cu_textul_lor_in_caseta_si_langa_camp(patron, firma_u0):
    """440 (comanda 11.1 pct.16: „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp. Fără «motivul e mai sus».”).
    Pașii: fereastra firmei -> Date firmă -> golește denumirea, scrie seria de chitanțe „CH-440!” (invalidă) -> Salvează: lângă fiecare
    câmp textul lui (aria-invalid, aria-describedby spre el), iar în caseta de lângă buton AMBELE, fiecare cu textul ei; nicio trimitere
    „motivul e mai sus / mai jos”."""
    pg = patron.pg
    patron.firma(firma_u0["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    pg.fill("#df-nume-portofoliu", "")
    pg.fill("#df-serie_chitanta", "CH-440!")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => [...document.querySelectorAll('.refuz-salvare-lista > li')].some(li => li.textContent.includes('Seria'))",
                         timeout=20000)
    patron.captura()
    campuri = pg.evaluate("""() => ['df-nume-portofoliu', 'df-serie_chitanta'].map((id) => {
        const el = document.getElementById(id);
        const d = (el.getAttribute('aria-describedby') || '').split(' ').map((x) => document.getElementById(x)).filter(Boolean);
        return [id, el.getAttribute('aria-invalid'), d.map((x) => x.textContent.trim()).filter((t) => t)];
      })""")
    assert campuri[0][1] == "true" and "Completează denumirea din portofoliu." in campuri[0][2], campuri
    assert campuri[1][1] == "true" and any("Seria chitanțelor" in t for t in campuri[1][2]), campuri
    caseta = [t for t, viz in _caseta(pg) if viz]
    assert any(t.startswith("Denumirea firmei — Completează denumirea") for t in caseta), caseta
    assert any(t.startswith("Seria chitanțelor — Seria chitanțelor:") for t in caseta), caseta
    assert "motivul e" not in pg.inner_text(".fereastra:last-of-type"), caseta   # 440: „Fără «motivul e mai sus»”


# ── 441 — orice câmp de dată opțional se poate goli ───────────────────────────────────────────────────────────────────────
def test_def_441_data_infiintarii_se_goleste_din_x_si_ramane_goala(patron, firma_u0):
    """441 (pct.17: „orice câmp de dată opțional se poate goli.”). Pașii: Date firmă -> „Data înființării” 01.05.2020 -> Salvează ->
    redeschis: data e acolo, cu „×” lângă ea -> „×” -> câmpul gol -> Salvează -> redeschis: câmpul gol; în bază NULL."""
    pg = patron.pg
    patron.firma(firma_u0["nume"])
    _card(patron, "datefirma", "#df-salveaza")
    pg.fill("#df-nume-portofoliu", firma_u0["nume"])
    pg.fill("#df-data_infiintare", "2020-05-01")
    pg.click("#df-salveaza")
    pg.wait_for_function("() => /salvat/i.test((document.querySelector('#df-msg') || {}).textContent || '')", timeout=20000)
    assert str(sql('SELECT data_infiintare FROM "%s".firma_profil WHERE id = 1' % firma_u0["schema"])[0][0]) == "2020-05-01"
    x = pg.locator("#df-data_infiintare + .data-goleste")
    assert x.is_visible() and x.get_attribute("aria-label") == "Golește data"
    patron.captura("cu_data")
    x.click()
    assert pg.input_value("#df-data_infiintare") == "" and not x.is_visible()
    pg.click("#df-salveaza")
    pg.wait_for_function("() => /salvat/i.test((document.querySelector('#df-msg') || {}).textContent || '')", timeout=20000)
    patron.captura("golita")
    assert sql('SELECT data_infiintare FROM "%s".firma_profil WHERE id = 1' % firma_u0["schema"])[0][0] is None   # 441: „se poate goli”
    assert pg.input_value("#df-data_infiintare") == ""
    # câmpul obligatoriu al aceluiași ecran nu primește „×”
    assert pg.locator(".fereastra:last-of-type label:has(.oblig) .data-goleste").count() == 0


# ── 443 — seria și numărul separat ────────────────────────────────────────────────────────────────────────────────────────
def test_def_443_factura_seriei_f6_se_afiseaza_f6_nr_1(patron, firma_u0):
    """443 (pct.19: „seria și numărul se afișează separat peste tot (F6 nr. 1, nu F61)”). Pașii: Configurare emitere cu seria „F6”, de
    la 1 (ruta ecranului) -> factura emisă (ruta formularului) -> Facturi -> Istoric: rândul și detaliul spun „F6 nr. 1”, nicăieri „F61”."""
    tid = firma_u0["tenant_id"]
    _ok(_api(patron, "PUT", "/tenants/%d/facturi/numerotare" % tid, {"serie": "F6", "numar_start": 1}), "seria F6")
    pregateste_firma(patron, firma_u0)
    emite_api(patron, firma_u0)
    assert sql('SELECT serie, numar FROM "%s".facturi ORDER BY id DESC LIMIT 1' % firma_u0["schema"])[0] == ("F6", "F61")
    pg = patron.pg
    patron.firma(firma_u0["nume"])
    _card(patron, "facturi", "#fac-istoric")
    pg.click("#fac-istoric")
    pg.wait_for_selector(".fereastra:last-of-type .fac-frand-btn", timeout=20000)
    rand = pg.inner_text(".fereastra:last-of-type .fac-frand-btn")
    patron.captura("istoric")
    assert "F6 nr. 1" in rand and "F61" not in rand, rand
    pg.click(".fereastra:last-of-type .fac-frand-btn")
    # titlul DETALIULUI (`.fd-antet`), nu cel pus de navigator cât se încarcă ecranul (`h2[data-titlu-pus]` = „Factură”, fără număr)
    pg.wait_for_selector(".fereastra:last-of-type .fd-antet .pf-titlu", timeout=20000)
    titlu = pg.inner_text(".fereastra:last-of-type .fd-antet .pf-titlu")
    assert "F6 nr. 1" in titlu and "F61" not in pg.inner_text(".fereastra:last-of-type"), titlu


# ── 445 — „Deschide X” dintr-un refuz întoarce în formular, cu datele intacte ─────────────────────────────────────────────
def test_def_445_deschide_date_firma_din_refuzul_chitantei_intoarce_la_chitanta(patron, firma_gv):
    """445 (pct.21: „orice buton «Deschide X» dintr-un refuz întoarce în formularul de plecare, cu datele intacte.”), pe chitanța facturii.
    [lotul 13, 543 — comanda Costin 13.1: „La lipsa seriei de chitanțe, aplicația trimite în Date firmă, iar la factură seria se cere pe loc
    […] Seria se cere pe loc, ca la factură.”] Refuzul seriei nu mai trimite în Date firmă: seria se cere chiar sub formular, deci nici nu
    se mai pleacă din el. Pașii: firma fără serie de chitanțe -> factura emisă -> detaliul ei -> „Emite chitanță” (fereastra chitanței, cu
    data și suma propuse, nimic tastat) -> „Emite”: refuzul spune că lipsește seria și o cere pe loc, fără „Deschide Date firmă”, iar data și
    suma rămân cele din formular -> seria „G445” -> „Stabilește seria și emite chitanța”: chitanța se emite cu ACEEAȘI dată și sumă."""
    assert not sql('SELECT serie_chitanta FROM "%s".firma_profil WHERE serie_chitanta IS NOT NULL' % firma_gv["schema"])
    numar, fid = _factura_emisa(firma_gv)
    pg = patron.pg
    _detaliu_factura(patron, firma_gv, numar)
    pg.click(".fereastra:last-of-type #fd-chitanta")
    pg.wait_for_selector(".fereastra:last-of-type #fd-chit-ok", timeout=20000)
    inainte = {"data": pg.input_value("#fd-chit-data"), "suma": pg.input_value("#fd-chit-suma")}
    pg.click(".fereastra:last-of-type #fd-chit-ok")
    pg.wait_for_selector(".fereastra:last-of-type #ser-chit-serie", timeout=20000)
    refuz = pg.inner_text(".fereastra:last-of-type #ser-chit-box")
    patron.captura("seria_pe_loc")
    assert "serie" in refuz, refuz
    assert not pg.query_selector(".fereastra:last-of-type [data-ecran-destinatie='date_firma']:not([hidden])"), "refuzul nu mai trimite în Date firmă (543)"
    dupa = {"data": pg.input_value("#fd-chit-data"), "suma": pg.input_value("#fd-chit-suma")}
    assert dupa == inainte, (inainte, dupa)                                                 # 445: „cu datele intacte”
    pg.fill(".fereastra:last-of-type #ser-chit-serie", "G445")
    pg.click(".fereastra:last-of-type #ser-chit-ok")
    pg.wait_for_function("() => document.body.innerText.includes('a fost emisă')", timeout=30000)
    patron.captura("emisa")
    rand = sql('SELECT serie, data::text, suma FROM "%s".chitante WHERE factura_id = %%s' % firma_gv["schema"], (fid,))
    assert [(r[0], r[1], float(r[2])) for r in rand] == [("G445", inainte["data"], float(inainte["suma"]))], (rand, inainte)
