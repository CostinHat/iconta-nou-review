# -*- coding: utf-8 -*-
"""Lotul 10, comanda 10.2 (Costin 21.10.2026, verbatim în DECIZII „Comanda 10.2”): pct.3 (433), pct.7h (suma goală), pct.7i (394),
pct.7k (386) — pașii contabilului pe aplicația din index, pe baza de TEST, pe firme NOI de test. Salariatul e al probelor 411–414
(`e2e_lot92._salariat_cu_cm`: IONESCU VASILE, CNP 1900101410011 — cifra de control verificată; ocupația COR 241107, auditor financiar)."""
import datetime as _dt

import pytest

from conftest import firma_noua, sql
from e2e_lot92 import _stat, firma_cv, firma_cv_noua  # noqa: F401 — fixturile modulului

AZI = _dt.date.today()
_RAND = "IONESCU VASILE"


@pytest.fixture(scope="module")
def firma_jurnal():
    for f in firma_noua():
        yield f


# ── 433 — statul de plată: nimic nu se deschide fără să fie ales ─────────────────────────────────────────────────────────────────
def test_def_433_dupa_contabilizarea_statului_nu_se_deschide_formularul_cor(patron, firma_cv):
    """433. „la F5, după «Contabilizează statul», formularul «Ocupație COR · Ionescu Vasile» se deschide singur, gol, deși Ionescu are
    COR. Nimic nu se deschide fără să fie ales.” Cauza: butonul „Adeverință” purta și atributul care deschide formularul COR, deci un clic
    pe „Adeverință” îl deschidea și pe acela, gol; statul în care s-a scris ceva se păstrează la întoarcere, cu formularul deschis.
    Pașii: Salariați -> „+ vacanță” la IONESCU VASILE -> 100 -> „Renunță” -> „Adeverință” -> „←” -> „Contabilizează statul”: sub stat
    apare propunerea notei, iar formularul „Ocupație COR” NU e deschis -> „COR ✓”: formularul se deschide cu ocupația lui (241107)."""
    pg = _stat(patron, firma_cv)
    rand = pg.locator(".pf-frand", has_text=_RAND).first
    rand.locator("[data-vac]").click()
    pg.fill("#vac-input", "100")          # statul a primit o tastare: la întoarcere se păstrează (nu se redesenează)
    pg.click("#vac-cancel")
    pg.locator(".pf-frand", has_text=_RAND).first.locator("[data-adev]").click()
    pg.wait_for_selector("#ad-functie", timeout=20000)
    pg.click(".nav-sageata.nav-inapoi")
    pg.wait_for_selector("#sp-contare", timeout=20000)
    pg.click("#sp-contare")
    pg.wait_for_function("() => { const z = document.querySelector('#sp-contare-zona'); return z && !z.innerText.includes('Se calculează'); }",
                         timeout=30000)
    patron.captura("dupa_contabilizare")
    assert pg.inner_html("#sp-cor-zona").strip() == "", pg.inner_text("#sp-cor-zona")   # „Nimic nu se deschide fără să fie ales.”
    assert pg.locator("text=Ocupație COR ·").count() == 0
    pg.locator(".pf-frand", has_text=_RAND).first.locator("[data-cor]").click()
    pg.wait_for_selector("#cor-edit-cor-cauta", timeout=10000)
    patron.captura("cor_ales")
    assert pg.input_value("#cor-edit-cor") == "241107" and pg.input_value("#cor-edit-cor-cauta").startswith("241107")   # „deși Ionescu are COR”


# ── 10.2 pct.7h — „Notă nouă”: câmpurile de sumă sunt goale ──────────────────────────────────────────────────────────────────────
def test_def_sumagoala_nota_noua_are_suma_goala_si_o_cere(patron, firma_jurnal):
    """10.2 pct.7h. „Notă nouă în Registru jurnal: câmpul Sumă vine precompletat cu «0,00»; câmpurile de sumă sunt goale.” Pașii:
    Registru jurnal -> „+ Notă nouă”: Sumă goală -> „+ linie”: și a doua sumă goală -> „−” pe a doua linie -> documentul „Chitanță nr. 7
    din <azi>”, 6022 = 5311, suma lăsată goală -> „Salvează”: lângă câmp „Scrie suma liniei.”, nota nu se scrie -> suma 45 -> „Salvează”
    -> nota de 45,00 e în registru."""
    from e2e_bloc_a import _card
    s = firma_jurnal["schema"]
    patron.firma(firma_jurnal["nume"])
    pg = patron.pg
    _card(patron, "jurnal", "#j-nota-noua")
    pg.click("#j-nota-noua")
    pg.wait_for_selector("#je-salveaza", timeout=10000)
    assert pg.input_value("#je-linii .je-sum") == ""
    pg.click("#je-plus")
    assert pg.eval_on_selector_all("#je-linii .je-sum", "e => e.map((x) => x.value)") == ["", ""]
    patron.captura("goala")
    pg.locator("#je-linii > div").nth(1).locator(".je-scoate").click()
    pg.fill("#je-doc", "Chitanță nr. 7 din %s" % AZI.strftime("%d.%m.%Y"))   # AZI-dat-de-test
    pg.fill("#je-desc", "Rechizite E2E 10.2 7h")
    pg.fill("#je-linii .je-deb", "6022")
    pg.fill("#je-linii .je-cre", "5311")
    n0 = sql('SELECT count(*) FROM "%s".inregistrari' % s)[0][0]
    pg.click("#je-salveaza")
    pg.wait_for_selector("#je-linii .msg-eroare", timeout=10000)
    assert "Scrie suma liniei." in pg.inner_text("#je-linii")
    patron.captura("ceruta")
    assert sql('SELECT count(*) FROM "%s".inregistrari' % s)[0][0] == n0   # nu s-a scris o notă cu suma 0
    pg.fill("#je-linii .je-sum", "45")
    pg.click("#je-salveaza")
    pg.wait_for_selector("#j-nota-noua", timeout=20000)
    pg.wait_for_function("() => document.body.innerText.includes('Rechizite E2E 10.2 7h')", timeout=20000)
    assert sql('SELECT l.suma::text FROM "%s".inregistrari i JOIN "%s".inregistrari_linii l ON l.inregistrare_id = i.id '
               "WHERE i.descriere = 'Rechizite E2E 10.2 7h'" % (s, s)) == [("45.00",)]


# ── 394 (10.2 pct.7i) — fereastra „Notă nouă” nu derulează ───────────────────────────────────────────────────────────────────────
def test_def_394_nota_noua_nu_deruleaza_cu_note_in_luna(patron, firma_jurnal):
    """394. „fereastra «Notă nouă» din Registru jurnal încă se derulează vertical.” (proba lotului 9 era pe o firmă FĂRĂ note). Pașii, pe
    un ecran de laptop (1366×768): 8 note în luna curentă -> Registru jurnal -> „+ Notă nouă”: fereastra nu derulează, „Salvează” se vede,
    linia notei (debit = credit · sumă · centru · partener) stă pe un rând -> „Renunță”: notele lunii revin."""
    from e2e_bloc_a import _card
    from e2e_bloc_e import _nota
    for i in range(8):
        _nota(firma_jurnal, AZI.replace(day=1).isoformat(), [{"debit": "627", "credit": "5121", "suma": 10 + i}], "Comision E2E 394 %d" % i,
              document_ref="Extras bancar E2E 394 nr. %d" % i)
    pg = patron.pg
    pg.set_viewport_size({"width": 1366, "height": 768})
    try:
        patron.firma(firma_jurnal["nume"])
        _card(patron, "jurnal", "#j-nota-noua")
        pg.click("#j-nota-noua")
        pg.wait_for_selector("#je-salveaza", timeout=10000)
        pg.wait_for_timeout(400)
        m = pg.evaluate("""() => { const f = [...document.querySelectorAll('.fereastra')].pop(), c = f.querySelector('.fereastra-corp');
          const s = document.querySelector('#je-salveaza');
          return {sh: c.scrollHeight, ch: c.clientHeight, jos_s: s.getBoundingClientRect().bottom, jos_c: c.getBoundingClientRect().bottom,
                  randuri: new Set([...document.querySelectorAll('#je-linii > div > *')].map((x) => {
                    const r = x.getBoundingClientRect(); return Math.round(r.top + r.height / 2); })).size}; }""")
        patron.captura()
        assert m["sh"] <= m["ch"] + 1 and m["jos_s"] <= m["jos_c"] and m["randuri"] == 1, m
        pg.click("#je-renunta")
        pg.wait_for_function("() => document.body.innerText.includes('Comision E2E 394 7')", timeout=20000)
    finally:
        from conftest import INALT, LAT
        pg.set_viewport_size({"width": LAT, "height": INALT})


# ── 386 (10.2 pct.7k) — nota fără document: un singur mesaj ─────────────────────────────────────────────────────────────────────
def test_def_386_nota_fara_document_are_un_singur_mesaj(patron, firma_jurnal):
    """386. „în Registru jurnal, la nota fără document, același mesaj apare de două ori (stânga și dreapta).” Pașii: o notă 6581 = 5311 de
    100 lei, fără document -> Registru jurnal: pe rândul ei, o singură dată, „… nu se validează fără documentul din care provine … Scrie
    referința cu «Editează», apoi validează.”; „Validează” e inactiv; un clic pe el nu deschide a doua casetă (în dreapta)."""
    from e2e_bloc_a import _api, _ok, _card
    from e2e_bloc_e import _nota
    tid = firma_jurnal["tenant_id"]
    _nota(firma_jurnal, AZI.isoformat(), [{"debit": "5311", "credit": "581", "suma": 1000}], "Ridicare numerar E2E 386b", valideaza=True,
          document_ref="Cec 386b")
    nid = _ok(_api(patron, "POST", "/tenants/%d/jurnal" % tid, {"descriere": "Amendă fără document E2E 386b", "data": AZI.isoformat(),
                                                              "linii": [{"debit": "6581", "credit": "5311", "suma": "100.00"}]}), "nota")["id"]
    patron.firma(firma_jurnal["nume"])
    pg = patron.pg
    _card(patron, "jurnal", "#j-nota-noua")
    sel = "[data-nota-id='%s']" % nid
    pg.wait_for_selector(sel + " [data-val]", timeout=30000)
    assert pg.is_disabled(sel + " [data-val]")
    pg.eval_on_selector(sel + " [data-val]", "b => b.click()")
    pg.wait_for_timeout(500)
    # [lotul 12, comanda 12.2 pct.9, deficiența 617] „explicațiile o singură dată”: fraza generală stă o dată, deasupra tabelului
    # (`#jn-expl-fara_doc`), iar pasul notei („Scrie referința cu «Editează»”) în detaliul rândului ei — deschis întâi, ca omul
    from e2e_bloc_b import _deschide_rand, _nota_jn   # e2e_bloc_b nu importă din acest fișier
    rand = " ".join(_deschide_rand(patron, _nota_jn(patron, nid)).inner_text().split())
    fer = " ".join(pg.evaluate("() => [...document.querySelectorAll('.fereastra')].pop().innerText").split())
    patron.captura()
    assert fer.count("nu se validează fără documentul din care provine") == 1 and "Scrie referința cu „Editează”" in rand, (fer, rand)
    assert "nu se validează fără documentul din care provine" in pg.inner_text("#jn-expl-fara_doc"), fer
    assert pg.locator("#caseta-atentie-activa").count() == 0
