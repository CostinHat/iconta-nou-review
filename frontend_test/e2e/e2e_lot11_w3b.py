# -*- coding: utf-8 -*-
"""Lotul 11, comanda 11.1 (Costin 21.10.2026, verbatim în DECIZII „Comanda 11.1”) — subagentul w3b: deficiența 440 pe server, pct.16
(verbatim): „toate erorile apar deodată, fiecare cu textul ei, în casetă și lângă câmp. Fără «motivul e mai sus». Pe toată aplicația.”

Pașii contabilului pe aplicația din index, pe baza de TEST, pe o firmă NOUĂ (`firma_noua`). Produse (B30): serverul refuza la prima
greșeală, iar un UM de peste 10 caractere sau un preț de peste 10 cifre cădea în bază (500). Clienți (B35): numele golit se refuza singur,
iar o localitate de peste 100 de caractere cădea în bază (500). Ambele ecrane arată acum toate erorile serverului, fiecare lângă câmpul
ei și în caseta „NU s-a salvat.”.

DATE DE PORNIRE scrise direct (declarate): factura către partenerul fără fișă (`e2e_lot10_c69._factura_pf`, ca în `e2e_lot11_p`) —
documentul e pornirea, testul e fișa. Fișa însăși se creează din ecran (rândul „fără fișă” -> Salvează).
Mutațiile: frontend_test/e2e/mut_lot11_w3b.json."""
import pytest

from conftest import firma_noua, sql


@pytest.fixture(scope="module")
def firma_w3b():
    for f in firma_noua():
        yield f


def _caseta(pg):
    """Caseta „NU s-a salvat.”: textele vizibile, rând cu rând."""
    return [t for t, viz in pg.eval_on_selector_all(".refuz-salvare .refuz-salvare-lista > li",
                                                    "lis => lis.map(li => [li.textContent.trim(), !li.hidden])") if viz]


def _langa_camp(pg, ids):
    """[(id, aria-invalid, textele spre care trimite aria-describedby)] — eroarea stă lângă câmp (DS cap.6 v2.99 pct.2)."""
    return pg.evaluate("""(ids) => ids.map((id) => {
        const el = document.getElementById(id);
        const d = (el.getAttribute('aria-describedby') || '').split(' ').map((x) => document.getElementById(x)).filter(Boolean);
        return [id, el.getAttribute('aria-invalid'), d.map((x) => x.textContent.trim()).filter((t) => t)];
      })""", ids)


# ── 440 · Produse ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_440_produse_toate_erorile_serverului_langa_campuri(patron, firma_w3b):
    """440 (pct.16). Pașii: Produse -> „+ Adaugă produs”: „Produs E2E 440”, preț 99999999999, UM „kilogramexx” (11 caractere), cota 11%
    -> Salvează: lângă preț și lângă UM textul fiecăruia (aria-invalid, aria-describedby), în caseta de lângă buton AMBELE; nimic în
    nomenclator (înainte: 500, „eroare internă”) -> UM „kg”, preț 12,50 -> Salvează -> produsul e în listă și în nomenclator."""
    from e2e_bloc_a import _card
    patron.firma(firma_w3b["nume"])
    _card(patron, "produse", "#pr-add")
    pg = patron.pg
    pg.click("#pr-add")
    pg.fill("#pr-den", "Produs E2E 440")
    pg.fill("#pr-pret", "99999999999")
    pg.fill("#pr-um", "kilogramexx")
    pg.select_option("#pr-cota", "11")
    pg.click("#pr-salveaza")
    pg.wait_for_selector('.msg-eroare[data-camp="pr-um"]', timeout=20000)
    pg.wait_for_selector('.msg-eroare[data-camp="pr-pret"]', timeout=20000)
    patron.captura("refuz")
    langa = dict((i, (inv, t)) for i, inv, t in _langa_camp(pg, ["pr-um", "pr-pret"]))
    assert langa["pr-um"][0] == "true" and any("cel mult 10 caractere" in t for t in langa["pr-um"][1]), langa       # 440: lângă câmp
    assert langa["pr-pret"][0] == "true" and any("10 cifre" in t for t in langa["pr-pret"][1]), langa
    caseta = " | ".join(_caseta(pg))
    assert "cel mult 10 caractere" in caseta and "10 cifre" in caseta, caseta                                         # 440: în casetă
    assert "motivul e" not in pg.inner_text("#pr-form-zona"), caseta                                                   # „Fără «motivul e mai sus»”
    assert sql('SELECT count(*) FROM "%s".produse WHERE denumire = %%s' % firma_w3b["schema"], ("Produs E2E 440",)) == [(0,)]
    pg.fill("#pr-um", "kg")
    pg.fill("#pr-pret", "12.50")
    pg.click("#pr-salveaza")
    pg.wait_for_selector('.pr-rand:has-text("Produs E2E 440")', timeout=20000)
    patron.captura("salvat")
    assert sql('SELECT um, pret_unitar FROM "%s".produse WHERE denumire = %%s' % firma_w3b["schema"], ("Produs E2E 440",)) == [
        ("kg", 12.5)]


# ── 440 · Clienți ───────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_440_clienti_numele_golit_si_localitatea_lunga_deodata(patron, firma_w3b):
    """440 (pct.16). Pașii: (pornire: o vânzare către CLIENT E2E W3B SRL, fără fișă) -> Clienți -> rândul lui: Localitatea „Sibiu”,
    Salvează (fișa nouă) -> pe rândul fișei: numele golit și localitatea de 101 caractere -> Salvează: lângă nume și lângă localitate
    textul fiecăruia, în caseta „NU s-a salvat.” AMBELE; fișa neschimbată (înainte: numai numele, apoi 500 pe localitate) -> numele
    înapoi, localitatea „Mediaș” -> Salvează -> „localitatea și județul sunt în fișă”."""
    from e2e_bloc_a import _card
    from e2e_lot10_c69 import _factura_pf
    s = firma_w3b["schema"]
    _factura_pf(firma_w3b, "W3B-1", "emisa", "CLIENT E2E W3B SRL", data="2026-09-10")
    patron.firma(firma_w3b["nume"])
    _card(patron, "clienti", "#cl-tabel")
    pg = patron.pg
    rand = "tr[data-partener='nume-CLIENT_E2E_W3B_SRL']"
    pg.fill(rand + " input[id^='cl-oras-']", "Sibiu")
    pg.click(rand + " button.cl-salveaza")
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('sunt în fișă')", timeout=30000)
    cid = sql('SELECT id FROM "%s".clienti WHERE nume = %%s' % s, ("CLIENT E2E W3B SRL",))[0][0]
    cheie = "c%d" % cid
    pg.fill("#cl-nume-" + cheie, "")
    pg.fill("#cl-oras-" + cheie, "L" * 101)
    pg.click("#cl-salveaza-" + cheie)
    pg.wait_for_function("(k) => ['cl-nume-' + k, 'cl-oras-' + k].every((id) => document.getElementById(id).getAttribute('aria-invalid') "
                         "=== 'true')", arg=cheie, timeout=20000)
    patron.captura("refuz")
    langa = dict((i, t) for i, _inv, t in _langa_camp(pg, ["cl-nume-" + cheie, "cl-oras-" + cheie]))
    assert any("nu poate rămâne gol" in t for t in langa["cl-nume-" + cheie]), langa                                  # 440: lângă câmp
    assert any("Localitatea are cel mult 100 de caractere" in t for t in langa["cl-oras-" + cheie]), langa
    mesaj = pg.inner_text("#cl-mesaj")
    assert "nu poate rămâne gol" in mesaj and "cel mult 100 de caractere" in mesaj, mesaj                              # 440: toate deodată
    assert "motivul e" not in mesaj, mesaj
    assert sql('SELECT nume, oras FROM "%s".clienti WHERE id = %%s' % s, (cid,)) == [("CLIENT E2E W3B SRL", "Sibiu")]
    pg.fill("#cl-nume-" + cheie, "CLIENT E2E W3B SRL")
    pg.fill("#cl-oras-" + cheie, "Mediaș")
    pg.click("#cl-salveaza-" + cheie)
    pg.wait_for_function("() => (document.querySelector('#cl-mesaj') || {innerText: ''}).innerText.includes('sunt în fișă')", timeout=30000)
    patron.captura("salvat")
    assert sql('SELECT nume, oras FROM "%s".clienti WHERE id = %%s' % s, (cid,)) == [("CLIENT E2E W3B SRL", "Mediaș")]
