# -*- coding: utf-8 -*-
"""Comanda Costin 14.10.2026, pct.2 (verbatim în DECIZII): deficiențele 243, 244, 245 din retestul 13.10 — nota de închidere a anului pe
ecranele Bilanț și Registru jurnal. Pașii contabilului, pe aplicația din index, pe baza de TEST."""
import datetime
import re

import pytest

from conftest import firma_noua, nr_crt, sql
from e2e_bloc_d import PATRON, _api, _date_firma, _deschide, _nota_validata
from e2e_comanda_1010 import _alege_bilant, _solduri

_F = ".fereastra:last-of-type"


def _bilant(patron, f, an):
    """Bilanț pe `an`, S1005: zona „An precedent” după ULTIMA ei recitire (la deschidere se citește cu tipul reținut, apoi la alegerea
    anului și a tipului — `_alege_bilant` se mulțumește cu prima)."""
    patron.firma(f["nume"])
    _deschide(patron, "#fa-bilant", "Bilanț anual")
    _alege_bilant(patron, an)
    _zona_linistita(patron.pg)
    return patron.pg.inner_text("%s #bl-precedent" % _F)


def _zona_linistita(pg, liniste_ms=800):
    """Așteaptă până când zona „An precedent” nu se mai schimbă `liniste_ms` (citirile pornite la deschidere și la alegerea anului / a
    tipului se întorc pe rând și o redesenează fiecare)."""
    pg.evaluate("""(ms) => new Promise(r => { const z = document.querySelector('.fereastra:last-of-type #bl-precedent');
      let t = setTimeout(() => { o.disconnect(); r(); }, ms);
      const o = new MutationObserver(() => { clearTimeout(t); t = setTimeout(() => { o.disconnect(); r(); }, ms); });
      o.observe(z, {childList: true, subtree: true, characterData: true}); })""", liniste_ms)


def _operatiunile(f, an):
    """Vânzare 1.000 + TVA 210, servicii 200 + TVA 42, încasarea și plata — validate, neînchise."""
    for zi, d, c, s, ce in (("%d-03-10", "4111", "704", 1000, "Vanzare"), ("%d-03-10", "4111", "4427", 210, "TVA vanzare"),
                            ("%d-03-11", "628", "401", 200, "Servicii"), ("%d-03-11", "4426", "401", 42, "TVA servicii"),
                            ("%d-03-20", "5121", "4111", 1210, "Incasare"), ("%d-03-21", "401", "5121", 242, "Plata")):
        _nota_validata(f, zi % an, d, c, s, "%s %d" % (ce, an))


@pytest.fixture()
def firma_2025():
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "2024-12-31")
        _operatiunile(f, 2025)
        yield f


@pytest.fixture()
def firma_an_curent():
    an = datetime.date.today().year
    for f in firma_noua():
        _date_firma(f)
        _solduri(f, "%d-12-31" % (an - 1))
        _operatiunile(f, an)
        yield f


def _propune(patron, an):
    """Apasă „Propune … nota de închidere la 31.12.an” și întoarce zona recitită după propunere (244) — textul îl verifică testul."""
    pg = patron.pg
    pg.eval_on_selector("%s #bl-precedent .bl-inchidere" % _F, "d => { d.dataset.vechi = '1'; }")     # zona de dinainte de propunere
    pg.click("%s .bl-inchidere-propune[data-an='%d']" % (_F, an))
    pg.wait_for_function("() => { const z = document.querySelector('.fereastra:last-of-type #bl-precedent'); return z && "
                         "!z.querySelector('[data-vechi]') && z.innerText.trim(); }", timeout=60000)
    _zona_linistita(pg)
    return pg.inner_text("%s #bl-precedent" % _F)


def _note_inchidere(f):
    return sql("SELECT id, status FROM \"%s\".inregistrari WHERE sursa = 'inchidere_an' ORDER BY id" % f["schema"])


# ── 243 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_243_anul_neincheiat_nu_se_propune(patron, firma_an_curent):
    """243 (retestul Costin 13.10.2026): „nota de închidere se poate propune pentru un an neîncheiat; operațiunile ulterioare o fac
    greșită, iar după validare nu se mai corectează. Fie permiți propunerea numai după 31.12, fie avertizezi și recalculezi înainte de
    validare. Alege varianta mai sigură și spune de ce.” Aleasă: numai după 31.12.
    Pașii: firma cu operațiuni în anul curent, neînchise -> Bilanț pe anul curent: refuzul spune că anul nu s-a încheiat și când se
    propune nota; niciun buton de propunere; cererea directă (ruta) e refuzată cu același motiv; o ciornă de închidere deja scrisă pe
    31.12 a anului curent (cazul F2 din producție) nu se validează.
    MUTAȚIA din plasă: `an_incheiat` întors mereu True -> ROȘU."""
    pg = patron.pg
    f, an = firma_an_curent, datetime.date.today().year
    zona = _bilant(patron, f, an)
    patron.captura()
    assert ("anul %d nu s-a încheiat — clasele 6/7 se închid în 121 la 31.12.%d, iar nota de închidere se propune după această dată"
            % (an, an)) in zona and "închide clasele 6/7" not in zona, zona
    assert pg.locator("%s .bl-inchidere-propune" % _F).count() == 0
    st, r = _api(PATRON, "POST", "/tenants/%d/bilant-inchidere-propunere?an=%d" % (f["tenant_id"], an), {})
    assert st >= 400 and ("Nota de închidere pe %d se propune după 31.12.%d" % (an, an)) in str(r), (st, r)
    assert _note_inchidere(f) == []
    nid = sql("INSERT INTO \"%s\".inregistrari (data, descriere, sursa, status, document_ref) VALUES ('%d-12-31', 'Închidere F2', "
              "'inchidere_an', 'ciorna', 'Notă de calcul nr 1') RETURNING id" % (f["schema"], an))[0][0]
    sql("INSERT INTO \"%s\".inregistrari_linii (inregistrare_id, cont_debit, cont_credit, suma) VALUES (%d, '704', '121', 1000), "
        "(%d, '121', '628', 200)" % (f["schema"], nid, nid))
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {})
    assert st >= 400 and ("Nota de închidere %s nu se validează înainte de 31.12.%d" % (nr_crt(f["schema"], nid), an)) in str(r), (st, r)   # [258]
    assert _note_inchidere(f) == [(nid, "ciorna")]


def test_def_243_nota_care_nu_mai_corespunde_soldurilor_nu_se_valideaza(patron, firma_2025):
    """243, același drum după 31.12: nota propusă pe 2025, apoi o vânzare din noiembrie 2025 validată (500). Bilanțul spune că notele
    propuse nu mai corespund soldurilor și oferă „Propune din nou”; nota veche nu se validează; propusă din nou, se validează.
    MUTAȚIA din plasă: `corespunde` întors mereu True -> ROȘU."""
    pg = patron.pg
    f = firma_2025
    _bilant(patron, f, 2025)
    _propune(patron, 2025)
    vechi = [i for i, _s in _note_inchidere(f)]
    _nota_validata(f, "2025-11-30", "4111", "704", 500, "Vanzare tarzie 2025")
    zona = _bilant(patron, f, 2025)
    assert "dar nu mai corespund soldurilor de la 31.12.2025 din notele validate" in zona, zona
    pg.locator("%s .bl-inchidere-propune" % _F).scroll_into_view_if_needed()
    patron.captura()
    assert pg.inner_text("%s .bl-inchidere-propune[data-an='2025']" % _F) == "Propune din nou nota de închidere la 31.12.2025"
    st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], vechi[-1]), {})
    assert st >= 400 and "nu mai corespunde soldurilor de la 31.12.2025" in str(r), (st, r)
    _propune(patron, 2025)
    noi = [i for i, _s in _note_inchidere(f)]
    assert set(noi).isdisjoint(vechi) and len(noi) == 2, (vechi, noi)
    for nid in noi:
        st, r = _api(PATRON, "POST", "/tenants/%d/jurnal/%d/valideaza" % (f["tenant_id"], nid), {})
        assert st == 200 and r.get("ok"), (st, r)


# ── 244 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_244_dupa_propunere_legatura_spre_notele_de_validat(patron, firma_2025):
    """244 (retestul Costin 13.10.2026): „după propunere, mesajul roșu din Bilanț spune în continuare «închide clasele 6/7 în 121». Trebuie
    «Notele de închidere propuse așteaptă validarea», cu link direct spre ele, deschis pe luna lor (textul «Jurnal — notele de validat»
    m-a dus la Jurnalul regim marjă).”
    Pașii: Bilanț 2025 -> „Propune nota de închidere la 31.12.2025” -> refuzul se recitește: „Notele de închidere propuse așteaptă
    validarea: #… Regularizarea TVA …; #… Închiderea …”, fără „închide clasele 6/7”, mesajul propunerii fără „Jurnal — notele de validat”
    -> „Deschide notele de închidere în Registrul jurnal — decembrie 2025” -> Registrul jurnal pe 12/2025, cu cele două note evidențiate.
    MUTAȚIA din plasă: `propuse` nepasat din `bilant_api` -> ROȘU."""
    pg = patron.pg
    f = firma_2025
    zona = _bilant(patron, f, 2025)
    assert "închide clasele 6/7 în 121 la 31.12.2025" in zona, zona
    zona = _propune(patron, 2025)
    patron.captura("propunerea")
    note = [i for i, _s in _note_inchidere(f)]
    # [258] notele numite cum le arată Registrul jurnal („nr. crt. N din 31.12.2025”), nu prin id-ul intern
    assert re.findall(r"Notele de închidere propuse așteaptă validarea: Regularizarea TVA la 31\.12\.2025 \(nota (nr\. crt\. \d+ din [\d.]+)\); "
                      r"Închiderea conturilor de venituri și cheltuieli în 121 la 31\.12\.2025 \(nota (nr\. crt\. \d+ din [\d.]+)\)", zona) \
        == [tuple(nr_crt(f["schema"], i) for i in note)], zona
    assert "închide clasele 6/7" not in zona and "notele de validat" not in zona, zona
    mesaj = pg.inner_text("%s .bl-inchidere-mesaj" % _F)
    assert mesaj.startswith("Am propus la 31.12.2025") and "în Registrul jurnal, luna decembrie 2025" in mesaj, mesaj
    leg = pg.locator("%s .bl-inchidere-jurnal" % _F)
    assert leg.inner_text() == "Deschide notele de închidere în Registrul jurnal — decembrie 2025"
    leg.click()
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                         "return f && f.querySelectorAll('.val-evidentiat').length === 2 && !document.getAnimations().length; }",
                         timeout=30000)
    patron.captura("registrul_jurnal")
    assert pg.inner_text("%s .pf-intro" % _F).startswith("Luna 12/2025"), pg.inner_text("%s .pf-intro" % _F)
    assert sorted(int(x) for x in pg.eval_on_selector_all("%s .val-evidentiat" % _F, "rr => rr.map(r => r.dataset.notaId)")) == note


# ── 245 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
def test_def_245_sursa_notei_se_scrie_in_cuvinte(patron, firma_2025):
    """245 (retestul Costin 13.10.2026): „pe note apare «sursa: inchidere_an». Scrie «sursa: închiderea anului» și verifică toate sursele
    de note afișate.”
    Pașii: nota de închidere propusă -> Registrul jurnal, decembrie 2025: „sursa: închiderea anului” pe ambele note; martie 2025 (notele
    introduse de contabil): „sursa: introducere manuală”; nicăieri codul („inchidere_an”, „manual”).
    MUTAȚIA din plasă: ecranul afișează iar `n.sursa` -> ROȘU."""
    pg = patron.pg
    f = firma_2025
    _bilant(patron, f, 2025)
    _propune(patron, 2025)
    pg.click("%s .bl-inchidere-jurnal" % _F)
    pg.wait_for_function("() => { const f = [...document.querySelectorAll('.fereastra')].pop(); "
                         "return f && f.querySelectorAll('.val-evidentiat').length === 2 && !document.getAnimations().length; }",
                         timeout=30000)
    patron.captura("decembrie")
    surse = lambda: re.findall(r"sursa: ([^\n·]+?)(?:\n|$| ·)", pg.inner_text(_F))   # noqa: E731
    assert surse() == ["închiderea anului", "închiderea anului"], surse()
    for _ in range(9):                                                         # decembrie -> martie
        pg.click("%s #j-prev" % _F)
        pg.wait_for_function("(l) => { const p = document.querySelector('.fereastra:last-of-type .pf-intro'); "
                             "return p && p.innerText.startsWith(l); }", arg="Luna %02d/2025" % (11 - _), timeout=30000)
    patron.captura("martie")
    assert set(surse()) == {"introducere manuală"} and len(surse()) == 6, surse()
    assert "inchidere_an" not in pg.inner_text(_F) and "sursa: manual" not in pg.inner_text(_F)
